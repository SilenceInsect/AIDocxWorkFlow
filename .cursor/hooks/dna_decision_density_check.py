#!/usr/bin/env python3
"""AIDocxWorkFlow 决策密度检测 hook（sessionEnd 事件）

作用：
  - 会话结束时，扫描本次会话 Agent 的 Write/Edit 调用次数
  - 单次响应 > 3 文件改动 = 决策密度违规
  - < 3 次：软记录
  - ≥ 3 次：临界点 block（exit 1 + stderr 警告）

为什么是 sessionEnd（不是 beforeSubmitPrompt）：
  - beforeSubmitPrompt 拿不到完整响应文件改动记录
  - sessionEnd 拿 session_id，可以反查 transcript 文件
  - 跟 dna_violation_check.py 同款协议

为什么是 v3.1 新增（不是 v3.0）：
  - v3.0 §0.4 教训：hook 防不住"误读"型违规
  - v3.1 翻案：决策密度是"可数"型违规（> 3 = 违规）——hook 能防
  - v3.1 D-304 决策 + D-304 用户点头

触发：
  .cursor/hooks.json -> sessionEnd array -> {command: dna_decision_density_check.py}

协议：
  stdin: JSON {"session_id": "...", "event": "sessionEnd"}
  stdout: 无
  exit 0: 软记录 / exit 1: 临界点 block
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── 配置（可由环境变量覆盖，参考 v3.1 open_questions.md Q-311）─────────
DENSITY_THRESHOLD = int(os.environ.get("DNA_DECISION_DENSITY_THRESHOLD", "3"))
TRANSCRIPT_DIR = Path.home() / ".cursor" / "projects" / "AIDocxWorkFlow" / "agent-transcripts"
LOG_FILE = Path("workflow_assets/feedback_logs/dna_decision_density.jsonl")


def find_transcript(session_id: str) -> Path | None:
    """根据 session_id 找 transcript jsonl 文件（同 dna_violation_check.py 协议）"""
    if not session_id:
        return None
    candidates = list(TRANSCRIPT_DIR.glob(f"{session_id}/{session_id}.jsonl"))
    if candidates:
        return candidates[0]
    for p in TRANSCRIPT_DIR.rglob("*.jsonl"):
        try:
            if session_id in p.stem or session_id in p.read_text(errors="ignore")[:1000]:
                return p
        except OSError:
            continue
    return None


def count_file_edits(transcript: Path) -> tuple[int, list[str]]:
    """扫描 transcript 里的 Agent Write/Edit 调用

    返回: (单次最大连续改动文件数, 触发该最大值的工具调用文件列表)

    判定规则：
      - 每次"工具调用块"中 Write/Edit 的 unique 路径数 = 该次的文件改动数
      - 取整个会话的最大值（不是累加）
      - "最大"是因为：决策密度问的是"单次响应"——单次 = 一次 Assistant message
    """
    max_edits_in_turn = 0
    max_turn_files: list[str] = []

    try:
        for line in transcript.read_text(errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            role = obj.get("role") or obj.get("type") or ""
            if role != "assistant":
                continue

            # 提取该 turn 的工具调用里的文件路径
            tool_calls = obj.get("tool_calls") or []
            files_in_turn: set[str] = set()
            for tc in tool_calls:
                if not isinstance(tc, dict):
                    continue
                fn = tc.get("function") or tc.get("name") or ""
                if fn not in ("Write", "Edit", "MultiEdit", "write", "edit"):
                    continue
                args = tc.get("arguments") or tc.get("args") or tc.get("input") or {}
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        continue
                if not isinstance(args, dict):
                    continue
                path = args.get("file_path") or args.get("path") or args.get("filePath") or ""
                if path:
                    files_in_turn.add(path)

            n = len(files_in_turn)
            if n > max_edits_in_turn:
                max_edits_in_turn = n
                max_turn_files = sorted(files_in_turn)

    except OSError:
        pass

    return max_edits_in_turn, max_turn_files


def log_density(session_id: str, max_edits: int, files: list[str]) -> None:
    """追加一条密度记录到 dna_decision_density.jsonl"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "max_edits_in_turn": max_edits,
        "threshold": DENSITY_THRESHOLD,
        "files_in_max_turn": files,
        "action": "blocked" if max_edits >= DENSITY_THRESHOLD else "soft_logged",
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return 0

    session_id = (
        payload.get("session_id")
        or payload.get("conversation_id")
        or ""
    )

    if not session_id:
        sys.stderr.write("[DNA-DENSITY] no session_id in payload; skipped\n")
        return 0

    transcript = find_transcript(session_id)
    if transcript is None:
        sys.stderr.write(
            f"[DNA-DENSITY] transcript not found for session {session_id[:8]}; skipped\n"
        )
        return 0

    max_edits, files = count_file_edits(transcript)
    log_density(session_id, max_edits, files)

    if max_edits >= DENSITY_THRESHOLD:
        sys.stderr.write(
            f"[DNA-DENSITY-BLOCK] session {session_id[:8]} single turn has "
            f"{max_edits} file edits (>= {DENSITY_THRESHOLD}). Files: {files}. "
            f"Next session: re-read DNA_3Q_CHECK.mdc §7 (decision density) "
            f"and use AskQuestion to collect user approval before batch edits.\n"
        )
        return 1  # 临界点 block

    if max_edits > 0:
        sys.stderr.write(
            f"[DNA-DENSITY-WARN] session {session_id[:8]} max turn edits = "
            f"{max_edits} (< {DENSITY_THRESHOLD}). Logged to {LOG_FILE}.\n"
        )
        return 0

    return 0


# ── self-test ───────────────────────────────────────────────────────
def self_test() -> int:
    """python3 .cursor/hooks/dna_decision_density_check.py --self-test

    验证：tool_call 解析、threshold 判定、log 写入
    """
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        # 模拟单次 turn 改 4 文件（应 block）
        f.write(json.dumps({
            "role": "assistant",
            "tool_calls": [
                {"function": "Write", "arguments": {"file_path": "/a/b.py"}},
                {"function": "Edit", "arguments": {"file_path": "/a/c.md"}},
                {"function": "Edit", "arguments": {"file_path": "/a/d.json"}},
                {"function": "Write", "arguments": {"file_path": "/a/e.mdc"}},
            ],
        }, ensure_ascii=False) + "\n")
        # 模拟另一次 turn 改 2 文件（应软记录）
        f.write(json.dumps({
            "role": "assistant",
            "tool_calls": [
                {"function": "Write", "arguments": {"file_path": "/a/x.md"}},
                {"function": "Edit", "arguments": {"file_path": "/a/y.md"}},
            ],
        }, ensure_ascii=False) + "\n")
        # 模拟 user turn（应跳过）
        f.write(json.dumps({"role": "user", "content": "继续"}, ensure_ascii=False) + "\n")
        transcript_path = Path(f.name)

    max_n, files = count_file_edits(transcript_path)
    assert max_n == 4, f"expected max 4 edits, got {max_n}"
    assert len(files) == 4, f"expected 4 files, got {len(files)}"
    print(f"  [OK] count_file_edits: max={max_n}, files={files}")

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log_density("self-test-session", max_n, files)
    assert LOG_FILE.exists(), "log file not created"
    print(f"  [OK] log_density: wrote to {LOG_FILE}")

    transcript_path.unlink()
    print("  [OK] self-test passed")
    return 0


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
            sys.exit(self_test())
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[DNA-DENSITY-CRASH] {type(exc).__name__}: {exc}\n")
        sys.stderr.flush()
        sys.exit(0)
