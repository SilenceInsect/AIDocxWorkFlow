#!/usr/bin/env python3
"""Cursor hook: aidocx-feedback-logger auto-collector.

Triggers:
  - beforeSubmitPrompt : before the user hits Enter, scan the in-flight
                         chat for a freshly-finished workflow stage and
                         auto-append a "stage_finished" event to
                         workflow_assets/feedback_logs/<session>.jsonl
  - sessionEnd         : on conversation end, emit a "session_summary"
                         event aggregating stage events

Input via stdin (JSON).  Schema varies by event — see handlers below.

Design: we do NOT scan every AI response (too noisy). We only react to
two narrow signals:
  1. The previous turn produced a workflow artifact (review_report.md,
     test_cases.json, fail_report_S*.md, iteration.json, etc.) under
     workflow_assets/ — that means a stage just finished.
  2. The user is about to submit a prompt that mentions a stage keyword
     (e.g. "/aidocx-s7-review", "stage 3", "再跑一次 S6") — that means
     a stage is about to start, so we record a "stage_started" event
     to pair with the eventual "stage_finished" event.

All events are append-only JSONL. Downstream S8 self-iteration
(ai_workflow/iteration_aggregator.py) reads them.

Stage resolution rules (sh-only fix vs main):
  - The same artifact name (e.g. review_report.{md,json}) may be owned
    by multiple stages (S1 + S7).  The LAST stage in STAGE_ARTIFACTS
    that claims it wins.  So S7's review_report.md overrides S1's.
  - Some stages intentionally drop artifacts into a sibling stage's
    directory (S7 writes review_report.{md,json} into
    "「S6 测试用例生成」/").  When the stage directory name does NOT
    contain the artifact's natural owner, we fall back to the
    artifact → owner lookup.  This is the case the fix targets.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── paths ───────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FEEDBACK_LOGS_DIR = REPO_ROOT / "workflow_assets" / "feedback_logs"
WORKFLOW_ASSETS = REPO_ROOT / "workflow_assets"

# Stages we recognize, in order. The order matters: when two stages
# claim the same artifact name (e.g. review_report.md for S1 and S7),
# the LATER entry wins.
#
# Each tuple: (stage_code, dir_substring, pass_artifact, fail_artifact).
# We list BOTH .md and .json variants where the stage produces them,
# so the auto-scanner picks up whichever the AI wrote.
STAGE_ARTIFACTS = [
    ("S1",   "S1",  "review_report.md",    "fail_report_S1.md"),
    ("S1",   "S1",  "review_report.json",  "fail_report_S1.md"),
    ("S1.5", "S1.5", "exit_permission.json", "fail_report_S1_5.md"),
    ("S2",   "S2",  "backlog.md",          "fail_report_S2.md"),
    ("S2",   "S2",  "backlog.json",        "fail_report_S2.md"),
    ("S2.5", "S2.5", "iteration_plan.md",   "fail_report_S2_5.md"),
    ("S2.5", "S2.5", "iteration_plan.json", "fail_report_S2_5.md"),
    ("S3",   "S3",  "prototype.md",         "fail_report_S3.md"),
    ("S3",   "S3",  "prototype.json",      "fail_report_S3.md"),
    ("S4",   "S4",  "business_flow.md",     "fail_report_S4.md"),
    ("S5",   "S5",  "test_points.json",     "fail_report_S5.md"),
    ("S5",   "S5",  "test_points.md",       "fail_report_S5.md"),
    ("S6",   "S6",  "test_cases.json",      "fail_report_S6.md"),
    ("S6",   "S6",  "test_cases.md",        "fail_report_S6.md"),
    # S7 must come AFTER S1 so ARTIFACT_OWNER resolves review_report.*
    # to S7 (last-wins).  S7 writes into "「S6 测试用例生成」/" so the
    # CROSS_DIRECTORY_DROPS table below also routes it correctly.
    ("S7",   "S7",  "review_report.md",     "fail_report_S7.md"),
    ("S7",   "S7",  "review_report.json",   "fail_report_S7.md"),
    ("S8",   "S8",  "iteration.json",       "fail_report_S8.md"),
    ("S8",   "S8",  "iteration.md",         "fail_report_S8.md"),
]

# Flatten for last-wins directory-name matching.
STAGE_ARTIFACTS_ORDER: list[str] = [c for c, _, _, _ in STAGE_ARTIFACTS]

# Build (artifact_name → owning_stage_code) lookup. Later entries
# overwrite earlier ones, so S7 wins over S1 for review_report.md.
ARTIFACT_OWNER: dict[str, str] = {}
for _code, _, _ok, _fail in STAGE_ARTIFACTS:
    ARTIFACT_OWNER[_ok] = _code
    ARTIFACT_OWNER[_fail] = _code

# User-side keywords that signal "I'm starting stage X"
STAGE_KEYWORDS = {
    "S1":   ["/aidocx-s1-review", "S1 review", "需求评审"],
    "S1.5": ["/aidocx-s1-5", "S1.5", "业务澄清"],
    "S2":   ["/aidocx-s2-breakdown", "S2", "需求拆解"],
    "S2.5": ["/aidocx-s2-5-iteration", "S2.5", "迭代规划"],
    "S3":   ["/aidocx-s3-prototype", "S3", "原型导出"],
    "S4":   ["/aidocx-s4-flowchart", "S4", "流程图"],
    "S5":   ["/aidocx-s5-test-points", "S5", "测试点"],
    "S6":   ["/aidocx-s6-test-cases", "S6", "测试用例"],
    "S7":   ["/aidocx-s7-review", "S7", "用例审查"],
    "S8":   ["/aidocx-s8-self-iteration", "S8", "自迭代"],
}

# ── small helpers ───────────────────────────────────────────────────────────

def _session_id() -> str:
    """Stable session id for the lifetime of this Cursor conversation."""
    sid = os.environ.get("AIDOCX_SESSION_ID")
    if sid:
        return sid
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _log_path(session_id: str) -> Path:
    FEEDBACK_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return FEEDBACK_LOGS_DIR / f"session_{session_id}.jsonl"


def _append_event(session_id: str, event: dict) -> None:
    p = _log_path(session_id)
    event.setdefault("ts", datetime.now(timezone.utc).isoformat())
    event.setdefault("session_id", session_id)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _safe_read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# ── detection: was a stage just finished in the previous turn? ──────────────

# Special cross-directory drops: a stage that writes into a SIBLING
# stage's directory.  Maps (sibling_dir_substring, artifact_name) →
# true owner.  Last-wins on artifact_name.
CROSS_DIRECTORY_DROPS: list[tuple[str, str, str]] = [
    # S7 writes review_report.{md,json} into "「S6 测试用例生成」/".
    # When we see review_report.md/json inside a S6 directory, the
    # owner is S7, not S6.
    ("S6", "review_report.md", "S7"),
    ("S6", "review_report.json", "S7"),
    # (S6 itself writes test_cases.{md,json,xlsx} into its own dir — no
    # cross-directory drop needed.)
]


def _detect_finished_stage() -> tuple[str | None, str | None, str | None]:
    """Return (stage, req_name, verdict) for the most recent stage artifact.

    verdict ∈ {"pass", "fail", None}. None = no fresh artifact.

    Resolution rules (see module docstring):
      1. Directory name match (last-wins) is the primary signal.
      2. Fallback to ARTIFACT_OWNER lookup when the directory name
         doesn't contain any stage code (cross-directory drops like
         S7 → 「S6」).
    """
    if not WORKFLOW_ASSETS.exists():
        return None, None, None

    # Each candidate is (mtime, stage_code, req_name, verdict, artifact_relpath).
    candidates: list[tuple[float, str, str, str, str]] = []
    for req_dir in WORKFLOW_ASSETS.iterdir():
        if not req_dir.is_dir():
            continue
        for stage_dir in req_dir.iterdir():
            if not stage_dir.is_dir():
                continue
            for version_dir in stage_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                for fname, owner in ARTIFACT_OWNER.items():
                    p = version_dir / fname
                    if not p.exists():
                        continue
                    # Stage resolution priority:
                    #   1. CROSS_DIRECTORY_DROPS — overrides everything
                    #      (handles S7 writing review_report.{md,json}
                    #      into "「S6 测试用例生成」/").
                    #   2. Directory name match (last-wins when multiple
                    #      stages appear in the name; e.g. S2.5 wins
                    #      over S2 in "「S2.5 迭代规划」").
                    #   3. ARTIFACT_OWNER lookup (last-wins across the
                    #      STAGE_ARTIFACTS list).
                    resolved: str | None = None
                    for cd_dir, cd_fname, cd_owner in CROSS_DIRECTORY_DROPS:
                        if cd_fname == fname and cd_dir in stage_dir.name:
                            resolved = cd_owner
                            break
                    if resolved is None:
                        for code in STAGE_ARTIFACTS_ORDER:
                            if code in stage_dir.name or code.replace(".", "") in stage_dir.name:
                                dir_match = code
                        resolved = dir_match if dir_match is not None else owner
                    verdict = "fail" if fname.startswith("fail_") else "pass"
                    mtime = p.stat().st_mtime
                    candidates.append((
                        mtime, resolved, req_dir.name, verdict,
                        str(p.relative_to(REPO_ROOT)),
                    ))
    if not candidates:
        return None, None, None
    candidates.sort(reverse=True)
    _, code, req, verdict, artifact = candidates[0]
    return code, req, f"{verdict}:{artifact}"


def _detect_started_stage(prompt_text: str) -> str | None:
    """Return stage code if the user is about to start one, else None."""
    if not prompt_text:
        return None
    # Pick the LAST match in the prompt (most recent intent).
    last: tuple[int, str] | None = None
    for code, keywords in STAGE_KEYWORDS.items():
        for kw in keywords:
            idx = prompt_text.rfind(kw)
            if idx >= 0 and (last is None or idx > last[0]):
                last = (idx, code)
    return last[1] if last else None


# ── handlers ────────────────────────────────────────────────────────────────

def handle_before_submit_prompt(payload: dict) -> int:
    """Called before the user submits a prompt. We use this to:
      1. Detect a finished stage in the previous turn → record it.
      2. Detect a stage about to start in this prompt → record it.
    Never blocks the prompt (always exit 0).
    """
    sid = payload.get("session_id") or _session_id()
    prompt_text = (payload.get("prompt") or "").strip()

    finished_code, req_name, finished_info = _detect_finished_stage()
    if finished_code and req_name:
        # De-dup: don't write the same (req, stage) finish twice in a row.
        events = _safe_read_jsonl(_log_path(sid))
        last_two = events[-2:]
        if not any(
            e.get("kind") == "stage_finished"
            and e.get("req") == req_name
            and e.get("stage") == finished_code
            for e in last_two
        ):
            _append_event(sid, {
                "kind": "stage_finished",
                "stage": finished_code,
                "req": req_name,
                "info": finished_info,
                "source": "auto_artifact_scan",
            })

    started_code = _detect_started_stage(prompt_text)
    if started_code:
        _append_event(sid, {
            "kind": "stage_started",
            "stage": started_code,
            "req": "<inferred-from-prompt>",
            "source": "auto_keyword_detect",
        })

    return 0


def handle_session_end(payload: dict) -> int:
    sid = payload.get("session_id") or _session_id()
    events = _safe_read_jsonl(_log_path(sid))
    started = [e for e in events if e.get("kind") == "stage_started"]
    finished = [e for e in events if e.get("kind") == "stage_finished"]
    _append_event(sid, {
        "kind": "session_summary",
        "stages_started": len(started),
        "stages_finished": len(finished),
        "stages_failed": sum(1 for e in finished if str(e.get("info", "")).startswith("fail:")),
    })
    return 0


# ── dispatcher ──────────────────────────────────────────────────────────────

HANDLERS = {
    "beforeSubmitPrompt": handle_before_submit_prompt,
    "sessionEnd": handle_session_end,
}


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return 0
    event = payload.get("event") or payload.get("hook") or ""
    handler = HANDLERS.get(event)
    if handler is None:
        return 0
    try:
        return handler(payload)
    except Exception as exc:  # never let a hook crash the IDE
        sys.stderr.write(f"aidocx_feedback_logger_hook: {exc!r}\n")
        return 0


# ── self-test ───────────────────────────────────────────────────────────────
def self_test() -> int:
    """python3 .cursor/hooks/aidocx_feedback_logger_hook.py --self-test

    验证 4 项（用临时 session_id 隔离，不污染真实日志）：
      1. _detect_started_stage：纯字符串匹配
      2. handle_before_submit_prompt：stage 关键词 → 写 stage_started 事件
      3. handle_session_end：聚合 events → 写 session_summary
      4. main() dispatcher：JSON in → JSON 解析 + handler 调用
    """
    import os as _os
    import tempfile as _tf

    test_sid = "selftest_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    _os.environ["AIDOCX_SESSION_ID"] = test_sid

    # Case 1: _detect_started_stage 关键词匹配
    assert _detect_started_stage("/aidocx-s7-review 跑一次") == "S7", "Case 1a: S7 keyword"
    assert _detect_started_stage("S6 测试用例生成") == "S6", "Case 1b: S6 keyword"
    assert _detect_started_stage("S2.5 迭代规划") == "S2.5", "Case 1c: S2.5 keyword"
    assert _detect_started_stage("普通对话无 stage 关键词") is None, "Case 1d: no match"
    # 取最后（最右）匹配
    assert _detect_started_stage("先 S5 再 S6") == "S6", "Case 1e: last match wins"
    print("  [OK] Case 1: _detect_started_stage 5 sub-cases pass")

    # Case 2: handle_before_submit_prompt 写 stage_started 事件
    payload2 = {
        "session_id": test_sid,
        "event": "beforeSubmitPrompt",
        "prompt": "/aidocx-s7-review 跑一次",
    }
    rc2 = handle_before_submit_prompt(payload2)
    assert rc2 == 0, f"Case 2: expected exit 0, got {rc2}"
    log_p = _log_path(test_sid)
    assert log_p.exists(), f"Case 2: log file not created at {log_p}"
    events_after = _safe_read_jsonl(log_p)
    started_events = [e for e in events_after if e.get("kind") == "stage_started"]
    assert len(started_events) == 1, f"Case 2: expected 1 stage_started, got {len(started_events)}"
    assert started_events[0]["stage"] == "S7", f"Case 2: expected S7, got {started_events[0]['stage']}"
    print(f"  [OK] Case 2: handle_before_submit_prompt → 1 stage_started event written ({log_p.name})")

    # Case 3: handle_session_end 聚合 + 写 session_summary
    payload3 = {"session_id": test_sid, "event": "sessionEnd"}
    rc3 = handle_session_end(payload3)
    assert rc3 == 0, f"Case 3: expected exit 0, got {rc3}"
    events_after_end = _safe_read_jsonl(log_p)
    summaries = [e for e in events_after_end if e.get("kind") == "session_summary"]
    assert len(summaries) == 1, f"Case 3: expected 1 session_summary, got {len(summaries)}"
    summary = summaries[0]
    assert summary["stages_started"] == 1, f"Case 3: expected 1 stage_started, got {summary['stages_started']}"
    assert summary["stages_finished"] == 0, f"Case 3: expected 0 stage_finished (no artifact written in self-test), got {summary['stages_finished']}"
    print(f"  [OK] Case 3: handle_session_end → session_summary (started={summary['stages_started']}, finished={summary['stages_finished']})")

    # Case 4: main() dispatcher 集成（用 stdin，独立 payload 避免污染 Case 2/3 文件）
    main_sid = test_sid + "_main"
    payload4 = {"session_id": main_sid, "event": "sessionEnd"}
    proc = __import__("subprocess").run(
        [sys.executable, __file__],
        input=json.dumps(payload4),
        capture_output=True,
        text=True,
        env={**_os.environ, "AIDOCX_SESSION_ID": main_sid},
        timeout=10,
    )
    assert proc.returncode == 0, f"Case 4: expected exit 0, got {proc.returncode} stderr={proc.stderr}"
    main_log = _log_path(main_sid)
    assert main_log.exists(), f"Case 4: main() log not created at {main_log}"
    main_events = _safe_read_jsonl(main_log)
    main_summaries = [e for e in main_events if e.get("kind") == "session_summary"]
    assert len(main_summaries) == 1, f"Case 4: expected 1 session_summary from main(), got {len(main_summaries)}"
    print(f"  [OK] Case 4: main() dispatcher → stdin JSON → session_summary event")

    # 清理 self-test 临时文件
    for p in [log_p, main_log]:
        if p.exists():
            p.unlink()
    print("  [OK] self-test passed (4 cases + cleanup)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())
