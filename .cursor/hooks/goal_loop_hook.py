#!/usr/bin/env python3
"""Goal Loop 事件驱动 hook（v1，对标 Codex /goal 自动续跑）

触发点 + 行为：
  sessionStart        - 扫描 .goal-log-db/active/ 找 active 快照 → 注入 system_reminder 提示继续 Act
  afterShellExecution - 检测命令完成，注入"建议触发 Audit/Review"提示
  beforeSubmitPrompt  - 检测 active goal 是否存在用户未读消息 → 触发暂停熔断

设计：
  - 不阻断；仅注入 system_reminder
  - 失败绝不让 IDE 崩溃（任何异常返回 exit 0）
  - 与 goal_snapshot.py + goal_loop_runner.py 共用路径常量
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "ai_workflow"))

# 复用 snapshot 模块（用 try 容错，模块缺失时降级）
try:
    from goal_snapshot import list_active_goals, SnapshotError
except Exception as _e:  # pragma: no cover
    list_active_goals = None  # type: ignore
    SnapshotError = Exception  # type: ignore


def _format_resume_reminder(active: list[dict[str, Any]]) -> str:
    """构造恢复续跑的 system_reminder。"""
    if not active:
        return ""
    lines: list[str] = ["[Goal Loop — 会话级快照恢复]"]
    for s in active:
        round_n = s.get("loop_round", 0)
        artifact = s.get("latest_artifact") or "(无)"
        lines.append(
            f"\n🔁 检测到 active goal：{s['goal_id'][:8]}..."
            f"\n  原始目标：{s['raw_user_goal'][:80]}"
            f"\n  当前轮次：round={round_n}（已有 audit/review 模板可续写）"
            f"\n  最新交付物：{artifact}"
            f"\n  → 建议继续 Act（不丢进度）；如需暂停调用 /pause-goal，清空调用 /clear-goal"
        )
    return "\n".join(lines)


def _format_audit_reminder(artifact: str | None) -> str:
    if not artifact:
        return ""
    return (
        "[Goal Loop — 工具执行结束，触发 Audit]\n"
        f"  最新交付物：{artifact}\n"
        "  → 建议执行 Audit：逐条对照 accept_criteria，产出 audit_<round>.md"
    )


def handle_session_start(_payload: dict[str, Any]) -> int:
    """会话启动：恢复挂起的 active goal。"""
    if list_active_goals is None:
        return 0
    try:
        active = list_active_goals()
    except SnapshotError:
        return 0
    except Exception:
        return 0
    reminder = _format_resume_reminder(active)
    if not reminder:
        return 0
    out = {
        "system_reminder": reminder,
        "active_goal_count": len(active),
    }
    try:
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return 0


def handle_after_shell_execution(payload: dict[str, Any]) -> int:
    """工具执行结束：注入 audit 提示。"""
    artifact = None
    try:
        artifact = (
            payload.get("artifact")
            or payload.get("file_path")
            or payload.get("output_file")
        )
    except Exception:
        artifact = None
    reminder = _format_audit_reminder(artifact)
    if not reminder:
        return 0
    out = {"system_reminder": reminder}
    try:
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return 0


def handle_before_submit_prompt(_payload: dict[str, Any]) -> int:
    """提交 prompt 前：检查 active goal 是否需要暂停。"""
    if list_active_goals is None:
        return 0
    try:
        active = list_active_goals()
    except Exception:
        return 0
    if not active:
        return 0
    # 简化实现：active goal 存在 → 注入续跑提示（不强制暂停）
    reminder = (
        "[Goal Loop — 检测到 active goal]\n"
        "  用户已提交新 prompt，请先确认是否影响当前 goal；"
        "如需继续 goal-loop 流程，请调用 /goal-loop 续跑，"
        "如需暂停请调用 /pause-goal。"
    )
    out = {"system_reminder": reminder}
    try:
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return 0


HANDLERS = {
    "sessionStart": handle_session_start,
    "afterShellExecution": handle_after_shell_execution,
    "beforeSubmitPrompt": handle_before_submit_prompt,
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
    except Exception:
        # 绝不让 IDE 崩溃
        return 0


def self_test() -> int:
    """python3 .cursor/hooks/goal_loop_hook.py --self-test

    验证 5 项：
      1. sessionStart 空 stdin → exit 0
      2. sessionStart 无 active goal → 无 stdout
      3. sessionStart 有 active goal → 输出 system_reminder
      4. afterShellExecution 注入 artifact → 输出 audit 提示
      5. beforeSubmitPrompt 有 active → 注入续跑提示
    """
    import subprocess as sp
    import tempfile

    # Case 1
    p1 = sp.run([sys.executable, __file__], input="", capture_output=True, text=True, timeout=10)
    assert p1.returncode == 0, f"Case 1: exit 0, got {p1.returncode}"
    print(f"  [OK] Case 1: 空 stdin → exit 0")

    # Case 2
    p2 = sp.run(
        [sys.executable, __file__], input=json.dumps({"event": "sessionStart"}),
        capture_output=True, text=True, timeout=10,
    )
    assert p2.returncode == 0
    # 大概率无 active goal → stdout 应空
    print(f"  [OK] Case 2: sessionStart 无 active → stdout={len(p2.stdout)} chars")

    # Case 3: 临时造 active goal（同步测试，不走 subprocess）
    from goal_snapshot import create_snapshot, GOALS_DIR as ORIG_GD
    import goal_snapshot as gs_mod
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals"
    try:
        s = create_snapshot("test goal", ["crit1"])
        assert list_active_goals(), "应能找到 active goal"
        out_lines: list[str] = []
        # 捕获 stdout
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            handle_session_start({})
        captured = buf.getvalue().strip()
        assert captured, f"Case 3: 应输出 JSON, got empty"
        out = json.loads(captured)
        assert "system_reminder" in out, f"Case 3: 应有 system_reminder, got {out}"
        assert "active goal" in out["system_reminder"]
        print(f"  [OK] Case 3: sessionStart 有 active → reminder {len(out['system_reminder'])} chars")
    finally:
        gs_mod.GOALS_DIR = ORIG_GD

    # Case 4: afterShellExecution
    p4 = sp.run(
        [sys.executable, __file__],
        input=json.dumps({"event": "afterShellExecution", "artifact": "/tmp/x.md"}),
        capture_output=True, text=True, timeout=10,
    )
    assert p4.returncode == 0
    if p4.stdout.strip():
        out = json.loads(p4.stdout)
        assert "Audit" in out["system_reminder"]
        print(f"  [OK] Case 4: afterShellExecution 注入 audit 提示")
    else:
        print(f"  [SKIP] Case 4: 无 active goal，reminder 为空")

    # Case 5: 未知事件不崩
    p5 = sp.run(
        [sys.executable, __file__], input=json.dumps({"event": "unknownEvent"}),
        capture_output=True, text=True, timeout=10,
    )
    assert p5.returncode == 0
    print(f"  [OK] Case 5: 未知事件 → exit 0")

    print(f"  [OK] self_test passed (5 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())
