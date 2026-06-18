#!/usr/bin/env python3
"""AIDocxWorkFlow 3 问自检违规检测 hook（sessionEnd 事件）

作用：
  - 会话结束时，扫描本次会话 transcript 里的 Agent 响应
  - 检测"⚠️ DNA 自检未通过" marker 出现次数
  - < 3 次：软记录到 workflow_assets/feedback_logs/dna_violations.jsonl
  - ≥ 3 次：exit 1，stderr 输出"建议下次会话先重读 DNA_3Q_CHECK.mdc"

为什么是 sessionEnd（不是 beforeSubmitPrompt）：
  - beforeSubmitPrompt 拿不到完整响应文本（只有 prompt）
  - sessionEnd 拿 session_id，可以反查 transcript 文件

为什么"软记录 + 临界点 block"（不是纯硬阻断）：
  - 纯硬阻断 → Agent 写不出东西（误判）
  - 纯软记录 → 无强制力
  - 临界点 3 次 → 既不误判，又能在连续违规时强制自省

触发：
  .cursor/hooks.json -> sessionEnd array -> {command: dna_violation_check.py}

协议：
  stdin: JSON {"session_id": "...", "event": "sessionEnd"}
  stdout: 无（或 status JSON）
  exit 0: 软记录 / exit 1: 临界点 block
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── 配置（可由环境变量覆盖，参考 v3 open_questions.md Q-305）─────────────
VIOLATION_THRESHOLD = int(os.environ.get("DNA_VIOLATION_BLOCK_THRESHOLD", "3"))
MARKER_PREFIX = "⚠️ DNA 自检未通过"
TRANSCRIPT_DIR = Path.home() / ".cursor" / "projects" / "AIDocxWorkFlow" / "agent-transcripts"
LOG_FILE = Path("workflow_assets/feedback_logs/dna_violations.jsonl")


def find_transcript(session_id: str) -> Path | None:
    """根据 session_id 找 transcript jsonl 文件

    路径约定: ~/.cursor/projects/<project>/agent-transcripts/<sid>/<sid>.jsonl
    实际可能嵌套多层，glob 兜底。
    """
    if not session_id:
        return None
    candidates = list(TRANSCRIPT_DIR.glob(f"{session_id}/{session_id}.jsonl"))
    if candidates:
        return candidates[0]
    # 兜底：glob 全 transcript 找含 session_id 的
    for p in TRANSCRIPT_DIR.rglob("*.jsonl"):
        try:
            if session_id in p.stem or session_id in p.read_text(errors="ignore")[:1000]:
                return p
        except OSError:
            continue
    return None


def count_violations(transcript: Path) -> int:
    """扫描 transcript 里的 Agent 响应，统计 marker 出现次数

    Cursor transcript 每行是 JSON，结构大致：
      {"role": "assistant", "content": "..."}  ← 目标
      {"role": "user", ...}                     ← 跳过
    """
    count = 0
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
            content = obj.get("content") or obj.get("message") or ""
            if isinstance(content, list):
                # 多段 content 拼接
                content = "".join(
                    p.get("text", "") if isinstance(p, dict) else str(p)
                    for p in content
                )
            if MARKER_PREFIX in str(content):
                count += 1
    except OSError:
        pass
    return count


def log_violation(session_id: str, count: int) -> None:
    """追加一条违规记录到 dna_violations.jsonl"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "violation_count": count,
        "threshold": VIOLATION_THRESHOLD,
        "action": "blocked" if count >= VIOLATION_THRESHOLD else "soft_logged",
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
        sys.stderr.write("[DNA-CHECK] no session_id in payload; skipped\n")
        return 0

    transcript = find_transcript(session_id)
    if transcript is None:
        sys.stderr.write(
            f"[DNA-CHECK] transcript not found for session {session_id[:8]}; skipped\n"
        )
        return 0

    count = count_violations(transcript)
    log_violation(session_id, count)

    if count >= VIOLATION_THRESHOLD:
        sys.stderr.write(
            f"[DNA-BLOCK] session {session_id[:8]} has {count} violations "
            f"(>= {VIOLATION_THRESHOLD}). Next session: re-read "
            f".cursor/rules/DNA_3Q_CHECK.mdc + AGENTS.md before starting work.\n"
        )
        return 1  # 临界点 block

    if count > 0:
        sys.stderr.write(
            f"[DNA-WARN] session {session_id[:8]} has {count} violations "
            f"(< {VIOLATION_THRESHOLD}). Logged to {LOG_FILE}.\n"
        )
        return 0

    return 0


# ── self-test（v3 PLAN §4 完成判定用）──────────────────────────────────
def self_test() -> int:
    """python3 .cursor/hooks/dna_violation_check.py --self-test

    验证：marker 检测、threshold 判定、log 写入都能工作
    """
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        # 模拟 1 次违规的 transcript
        f.write(json.dumps({
            "role": "assistant",
            "content": "⚠️ DNA 自检未通过：先动手再问 → 改了 install.sh step 3",
        }, ensure_ascii=False) + "\n")
        f.write(json.dumps({
            "role": "user",
            "content": "继续",
        }, ensure_ascii=False) + "\n")
        f.write(json.dumps({
            "role": "assistant",
            "content": "好的，已修正",
        }, ensure_ascii=False) + "\n")
        transcript_path = Path(f.name)

    # 测试 count_violations
    n = count_violations(transcript_path)
    assert n == 1, f"expected 1 violation, got {n}"
    print(f"  [OK] count_violations: {n} (expected 1)")

    # 测试 log_violation
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log_violation("self-test-session", n)
    assert LOG_FILE.exists(), "log file not created"
    print(f"  [OK] log_violation: wrote to {LOG_FILE}")

    # 清理
    transcript_path.unlink()
    print("  [OK] self-test passed")
    return 0


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
            sys.exit(self_test())
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        # hook 崩了——降级，不阻断会话
        sys.stderr.write(f"[DNA-CHECK-CRASH] {type(exc).__name__}: {exc}\n")
        sys.stderr.flush()
        sys.exit(0)
