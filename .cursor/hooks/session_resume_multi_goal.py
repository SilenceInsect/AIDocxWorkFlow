#!/usr/bin/env python3
"""Session Resume Multi-Goal hook（v1.2 新增）

sessionStart hook：读取所有 active goal，按 goal_id 分组注入续跑 system_reminder。

支持多 goal 并存（跨 Round 并行），每个 goal 独立注入，互不阻塞。

触发点：`sessionStart`
目标：支持多个 /goal-loop 实例同时运行，各自有独立快照

行为：
  - 读取 .goal-log-db/active/ 下所有 active goal
  - 逐个注入续跑 reminder（按 goal_id 分组）
  - 支持同时续跑多个 goal
  - 无 active goal → exit 0（无噪声）

设计约束：
  - 不阻断主 sessionStart 流程
  - 失败绝不让 IDE 崩溃（任何异常返回 exit 0）
  - 与 goal_snapshot.py 共享路径常量
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "ai_workflow"))

try:
    from goal_snapshot import load_all_active_snapshots, SnapshotError  # noqa: E402
except Exception:  # pragma: no cover
    load_all_active_snapshots = None  # type: ignore
    SnapshotError = Exception  # type: ignore


def _inject(reminder: str) -> int:
    """通过 stdout 写 system_reminder（Cursor hook 约定）。"""
    out = {"system_reminder": reminder}
    try:
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    except Exception:
        return 0
    return 0


def _build_goal_reminder(snap: dict[str, Any]) -> str:
    """为单个 goal 构建续跑 reminder 文本。"""
    goal_id = snap.get("goal_id", "?")
    raw_goal = snap.get("raw_user_goal", "?")
    loop_round = snap.get("loop_round", 0)
    status = snap.get("status", "?")
    artifact = snap.get("latest_artifact") or "(无)"
    task_queue = snap.get("task_queue", [])
    parallel_hints = snap.get("parallel_executor_hints") or {}

    # 构建 pending tasks 列表
    pending = [t for t in task_queue if t.get("status") in ("pending", "running")]
    pending_titles = [t.get("title", t.get("id", "?")) for t in pending[:3]]
    pending_str = ", ".join(pending_titles) if pending_titles else "（无）"
    if len(pending) > 3:
        pending_str += f" ...（共 {len(pending)} 项）"

    # 并行化信息
    parallel_info = ""
    if parallel_hints:
        groups = parallel_hints.get("groups", [])
        if groups:
            parallel_info = f" | 并行分组：{len(groups)} 组"

    return (
        f"[Goal Loop — 续跑 Goal #{goal_id[:8]}]\n"
        f"  目标：{raw_goal[:80]}{'...' if len(raw_goal) > 80 else ''}\n"
        f"  状态：{status} | 轮次：{loop_round}{parallel_info}\n"
        f"  最新交付物：{artifact}\n"
        f"  待处理子任务：{pending_str}\n"
        f"  → 请继续 Act 阶段，或在响应中明确宣告 CONVERGED"
    )


def handle_session_start_multi_goal(payload: dict[str, Any]) -> int:
    """sessionStart handler（多 goal 续跑版，v1.2）。

    读取所有 active goal，逐个注入续跑 reminder。
    支持跨 Round 并行（多个 goal 同时存在）。
    """
    if load_all_active_snapshots is None:
        return 0

    try:
        active_goals = load_all_active_snapshots()
    except SnapshotError:
        return 0
    except Exception:
        return 0

    if not active_goals:
        return 0  # 无 active goal → 不注入

    # 按 loop_round 降序排列（轮次高的优先）
    active_goals.sort(key=lambda s: s.get("loop_round", 0), reverse=True)

    if len(active_goals) == 1:
        # 单 goal：直接注入
        return _inject(_build_goal_reminder(active_goals[0]))

    # 多 goal：逐个注入（用分隔符隔开）
    reminders = []
    for i, snap in enumerate(active_goals, 1):
        reminder = _build_goal_reminder(snap)
        reminders.append(f"--- Goal {i}/{len(active_goals)} ---\n{reminder}")

    full_reminder = (
        f"[Goal Loop — 多 Goal 续跑（{len(active_goals)} 个 active goals）]\n"
        + "\n\n".join(reminders)
    )
    return _inject(full_reminder)


HANDLERS = {
    "sessionStart": handle_session_start_multi_goal,
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
    """python3 .cursor/hooks/session_resume_multi_goal.py --self-test

    验证 5 项：
      1. 空 stdin → exit 0
      2. 无 active goal → exit 0 + 无 stdout
      3. 单 active goal → 注入 reminder（含 goal_id + round + artifact）
      4. 多 active goal → 注入多 goal reminder（含数量标注）
      5. 未知事件 → exit 0
    """
    import io
    import subprocess as sp
    import tempfile
    from contextlib import redirect_stdout

    import goal_snapshot as gs_mod
    from goal_snapshot import create_snapshot, GOALS_DIR as ORIG_GD

    # Case 1: 空 stdin → exit 0
    p1 = sp.run(
        [sys.executable, __file__], input="", capture_output=True, text=True, timeout=10
    )
    assert p1.returncode == 0, f"Case 1: 应 exit 0, got {p1.returncode}"
    print("  [OK] Case 1: 空 stdin → exit 0")

    # Case 2: 无 active goal → exit 0 + 无 stdout
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_empty"
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_session_start_multi_goal({})
        assert rc == 0, f"Case 2: 应 exit 0, got {rc}"
        assert buf.getvalue() == "", f"Case 2: 应无 stdout, got {buf.getvalue()!r}"
        print("  [OK] Case 2: 无 active goal → exit 0 + 无 stdout")
    finally:
        gs_mod.GOALS_DIR = ORIG_GD

    # Case 3: 单 active goal → 注入 reminder
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_single"
    try:
        snap = create_snapshot(
            "实现并行化扩展目标",
            ["标准1", "标准2"],
            token_limit=1000,
        )
        from goal_snapshot import update_snapshot
        update_snapshot(snap["goal_id"], loop_round=3, latest_artifact="/tmp/output.md")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_session_start_multi_goal({})
        assert rc == 0, f"Case 3: 应 exit 0, got {rc}"
        captured = buf.getvalue().strip()
        assert captured, "Case 3: 应注入 reminder"
        out = json.loads(captured)
        reminder = out["system_reminder"]
        assert snap["goal_id"][:8] in reminder, f"Case 3: 应含 goal_id 前缀, got {reminder}"
        assert "loop_round=3" in reminder or "轮次：3" in reminder, f"Case 3: 应含轮次, got {reminder}"
        assert "/tmp/output.md" in reminder, f"Case 3: 应含 artifact, got {reminder}"
        print(f"  [OK] Case 3: 单 goal → 注入 reminder ({len(reminder)} chars)")
    finally:
        gs_mod.GOALS_DIR = ORIG_GD

    # Case 4: 多 active goal → 注入多 goal reminder
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_multi"
    try:
        snap1 = create_snapshot("Goal 1 目标", ["标准1"], token_limit=1000)
        snap2 = create_snapshot("Goal 2 目标", ["标准1"], token_limit=1000)
        from goal_snapshot import update_snapshot
        update_snapshot(snap1["goal_id"], loop_round=5)
        update_snapshot(snap2["goal_id"], loop_round=2)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_session_start_multi_goal({})
        assert rc == 0, f"Case 4: 应 exit 0, got {rc}"
        captured = buf.getvalue().strip()
        assert captured, "Case 4: 应注入 reminder"
        out = json.loads(captured)
        reminder = out["system_reminder"]
        assert "2 个 active goals" in reminder or "2/" in reminder, f"Case 4: 应含 goal 数量, got {reminder}"
        assert snap1["goal_id"][:8] in reminder or "Goal 1" in reminder, f"Case 4: 应含 Goal 1, got {reminder}"
        assert snap2["goal_id"][:8] in reminder or "Goal 2" in reminder, f"Case 4: 应含 Goal 2, got {reminder}"
        print(f"  [OK] Case 4: 多 goal → 注入多 goal reminder ({len(reminder)} chars)")
    finally:
        gs_mod.GOALS_DIR = ORIG_GD

    # Case 5: 未知事件 → exit 0
    p5 = sp.run(
        [sys.executable, __file__],
        input=json.dumps({"event": "unknownEvent"}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert p5.returncode == 0, f"Case 5: 应 exit 0, got {p5.returncode}"
    print("  [OK] Case 5: 未知事件 → exit 0")

    print("  [OK] self_test passed (5 cases, v1.2)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())
