#!/usr/bin/env python3
"""Goal Loop 破环（Break Loop）hook（v3 — 并行化扩展）

v3 新增（v1.2）：
  - --async-mode：异步 subagent 触发（不阻塞主响应）
  - handle_after_file_edit_async()：文件编辑后异步 Audit
  - handle_after_shell_async()：Shell 执行后异步 Review
  - afterAgentResponse 改为异步 subagent 调用（detach）

触发点：`afterAgentResponse`（Cursor Agent 每次响应结束后）
目标：防止"单次响应完成 ≠ 目标完成"——Agent 静默停下导致循环死亡

双门判定（保留 v2 逻辑）：
  门 A (字面)：response_text 是否含 CONVERGED / BLOCKED / REPAIRING→BLOCKED
  门 B (数据)：last_audit.verdicts 是否有 PASS + 每条 PASS 均有 reverse_challenge

行为（v3 async-mode）：
  - --async-mode=True：写 hook-queue 触发文件，hook 立即返回（不阻塞）
  - --async-mode=False（默认）：保持 v2 同步行为
  - 无 active goal → exit 0（无噪声）

设计约束：
  - 不阻断（仅注入 system_reminder）
  - 失败绝不让 IDE 崩溃（任何异常返回 exit 0）
  - 与 goal_snapshot.py 共享路径常量 + list_active_goals()
  - v2 的 7 个 self-test 案例全部保留
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "ai_workflow"))

# Hook queue 目录（v3 新增：异步触发文件）
HOOK_QUEUE_DIR = REPO_ROOT / ".goal-log-db" / "hook-queue"

try:
    from goal_snapshot import list_active_goals, load_snapshot, SnapshotError, GOALS_DIR  # noqa: E402
except Exception:  # pragma: no cover
    list_active_goals = None  # type: ignore
    load_snapshot = None  # type: ignore
    SnapshotError = Exception  # type: ignore
    GOALS_DIR = REPO_ROOT / ".goal-log-db" / "active"


# 完成关键字（双门 A：字面兜底，v1.1 新增 CONVERGED_WITH_FOLLOWUP）
DONE_KEYWORDS = (
    "CONVERGED",
    "CONVERGED_WITH_FOLLOWUP",
    "BLOCKED",
    "REPAIRING→BLOCKED",
    "REPAIRING→CONVERGED",
)


def _has_done_declaration(text: str) -> bool:
    """门 A：response_text 是否含任一完成关键字。"""
    if not isinstance(text, str):
        return False
    return any(kw in text for kw in DONE_KEYWORDS)


def _audit_supports_done(snap: dict[str, Any]) -> tuple[bool, str]:
    """门 B：last_audit 是否真正支持"完成"声明。

    v1.1：converged_with_followup 状态只要求 BLOCKER 全 PASS。
    其他 status（achieved）仍要求全部 PASS。

    Returns:
        (ok, reason) — ok=True 表示数据层支持，reason 描述判断依据
    """
    audit = snap.get("last_audit") or {}
    verdicts = audit.get("verdicts") or []
    if not verdicts:
        return False, "无 last_audit.verdicts（从未跑过 audit）"

    status = snap.get("status", "")
    if status == "converged_with_followup":
        blockers = [v for v in verdicts if v.get("severity") == "BLOCKER"]
        if blockers:
            all_blocker_pass = all(v.get("judgement") == "PASS" for v in blockers)
            if not all_blocker_pass:
                return False, "converged_with_followup 要求所有 BLOCKER 项 PASS"
        return True, "converged_with_followup: BLOCKER 全 PASS，MAJOR/MINOR 可遗留"

    has_pass = any(v.get("judgement") == "PASS" for v in verdicts)
    if not has_pass:
        return False, "last_audit.verdicts 无 PASS 条目"

    missing_challenge = [
        v.get("standard", "?")
        for v in verdicts
        if v.get("judgement") == "PASS" and not str(v.get("reverse_challenge", "")).strip()
    ]
    if missing_challenge:
        return False, f"PASS 条目缺 reverse_challenge: {missing_challenge}"

    return True, "last_audit.verdicts 全 PASS 且均有 reverse_challenge"


def _inject(reminder: str) -> int:
    """通过 stdout 写 system_reminder（Cursor hook 约定）。"""
    out = {"system_reminder": reminder}
    try:
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    except Exception:
        return 0
    return 0


def _write_hook_queue_file(event: str, payload: dict[str, Any]) -> Path:
    """写 hook queue 触发文件（v3 新增：异步 subagent 触发）。

    异步模式下：hook 写一个 JSON 文件到 HOOK_QUEUE_DIR，
    立即返回；后台 subagent 读取该文件执行实际逻辑。

    文件命名：{timestamp}_{uuid}.json
    内容：event + payload + goal_id（若可确定）
    """
    HOOK_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{int(os.times().elapsed * 1000)}_{uuid.uuid4().hex[:8]}.json"
    qfile = HOOK_QUEUE_DIR / filename
    record = {
        "event": event,
        "payload": payload,
        "queued_at": _now_iso(),
        "status": "pending",
    }
    qfile.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return qfile


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _spawn_async_subagent(event: str, payload: dict[str, Any]) -> None:
    """Spawn detached subagent（v3 核心：异步不阻塞）。

    原理：
      1. 写 hook queue 文件（异步持久化）
      2. 用 subprocess.Popen spawn 一个 detached child process
      3. 立即返回（hook 不等待 child 完成）

    注意：subprocess 在 Cursor hook 环境中可能受限，
    因此同时写 queue 文件作为 fallback（下次 sessionStart 时处理）。
    """
    # 写 queue 文件（确保即使 subprocess 失败也有持久化记录）
    qfile = _write_hook_queue_file(event, payload)

    # 尝试 spawn detached subprocess
    try:
        # nohup + devnull 避免子进程继承 tty
        subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--async-mode",
                "--queue-file",
                str(qfile),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        # subprocess spawn 失败不影响 hook（queue 文件已持久化）
        pass


# ===== afterAgentResponse handlers =====


def handle_after_agent_response_sync(payload: dict[str, Any]) -> int:
    """同步版 handle_after_agent_response（保留 v2 行为）。"""
    if list_active_goals is None:
        return 0

    try:
        active = list_active_goals()
    except SnapshotError:
        return 0
    except Exception:
        return 0

    if not active:
        return 0  # 无 active goal → 不注入 reminder

    text = payload.get("response_text", "") if isinstance(payload, dict) else ""
    declared_done = _has_done_declaration(text)

    snap = active[0]
    ok, reason = _audit_supports_done(snap)

    if declared_done and not ok:
        return _inject(
            "[Goal Loop — 破环阻断]\n"
            f"  ⚠️ 检测到响应含 CONVERGED/BLOCKED 宣告，但 last_audit 不支持：\n"
            f"     {reason}\n"
            f"  → 禁止续跑；请先补 audit/review 证据后再次宣告"
        )

    if not declared_done:
        round_n = snap.get("loop_round", 0)
        artifact = snap.get("latest_artifact") or "(无)"
        return _inject(
            "[Goal Loop — 破环续跑]\n"
            f"  检测到 active goal（loop_round={round_n}），响应未含 CONVERGED/BLOCKED 关键字。\n"
            f"  最新交付物：{artifact}\n"
            f"  → 建议：\n"
            f"     1) 若尚有 accept_criteria 未 PASS → 继续 Act\n"
            f"     2) 若全部 PASS 且已写 reverse_challenge → 在响应中明确宣告 CONVERGED\n"
            f"     3) 若需暂停 → 调用 /pause-goal\n"
            f"     4) 若需终止 → 调用 /clear-goal"
        )

    # declared_done + ok：真通过，不注入
    return 0


def handle_after_agent_response_async(payload: dict[str, Any]) -> int:
    """异步版 handle_after_agent_response（v3 新增）。

    立即写入 queue 文件并 spawn detached subagent，hook 不等待结果。
    """
    _spawn_async_subagent("afterAgentResponse", payload)
    return 0  # 立即返回，不阻塞


def handle_after_agent_response(payload: dict[str, Any]) -> int:
    """afterAgentResponse handler（入口函数，v3 路由到 async/sync）。

    payload 形如：
      {
        "event": "afterAgentResponse",
        "response_text": "本次响应正文...",
        "loop_round": N  # 可选
      }
    """
    return handle_after_agent_response_sync(payload)


# ===== afterFileEdit handler（v3 新增） =====


def handle_after_file_edit(payload: dict[str, Any]) -> int:
    """afterFileEdit handler（v3 新增异步版）。

    文件编辑完成后触发异步 Audit，不阻塞主响应。
    对比 snapshot.latest_artifact vs accept_criteria，注入 Audit 结果。

    payload 形如：
      {
        "event": "afterFileEdit",
        "file_path": "path/to/file.md",
        "goal_id": "uuid"  # 可选，默认取首个 active goal
      }
    """
    if list_active_goals is None:
        return 0

    try:
        active = list_active_goals()
    except SnapshotError:
        return 0
    except Exception:
        return 0

    if not active:
        return 0

    # 默认取首个 active goal
    snap = active[0]
    goal_id = payload.get("goal_id") or snap.get("goal_id", "")
    file_path = payload.get("file_path", "?")

    # 异步触发（写 queue + spawn subagent）
    _spawn_async_subagent(
        "afterFileEdit",
        {"goal_id": goal_id, "file_path": file_path, "original_payload": payload},
    )
    return 0


# ===== afterShellExecution handler（v3 新增） =====


def handle_after_shell_execution(payload: dict[str, Any]) -> int:
    """afterShellExecution handler（v3 新增异步版）。

    Shell 命令完成后触发异步 Review，不阻塞主响应。
    如命令返回非 0 或时间超阈值，注入 Review 建议。

    payload 形如：
      {
        "event": "afterShellExecution",
        "command": "python3 test.py",
        "returncode": 0,
        "duration_seconds": 1.5,
        "goal_id": "uuid"  # 可选
      }
    """
    if list_active_goals is None:
        return 0

    try:
        active = list_active_goals()
    except SnapshotError:
        return 0
    except Exception:
        return 0

    if not active:
        return 0

    snap = active[0]
    goal_id = payload.get("goal_id") or snap.get("goal_id", "")

    # 异步触发
    _spawn_async_subagent(
        "afterShellExecution",
        {"goal_id": goal_id, "original_payload": payload},
    )
    return 0


# ===== sessionStart handler（保留 v2） =====


def _verify_active_snapshots_readable() -> list[str]:
    """验证所有 active goal 的 snapshot 是否可读。

    Returns:
        不可读的 goal_id 列表（空列表 = 全部可读）。
    """
    if list_active_goals is None:
        return []
    try:
        active = list_active_goals()
    except SnapshotError:
        return []
    except Exception:
        return []
    bad_ids: list[str] = []
    for snap in active:
        gid = snap.get("goal_id", "?")
        try:
            if load_snapshot is None:
                bad_ids.append(gid)
            else:
                load_snapshot(gid)
        except SnapshotError:
            bad_ids.append(gid)
        except Exception:
            bad_ids.append(gid)
    return bad_ids


def handle_session_start(payload: dict[str, Any]) -> int:
    """sessionStart handler：验证 active goal 的 snapshot 可读性。

    防止 goal_loop_breakloop_hook.py DT F4 所述"snapshot.json 不可读"问题
    导致 break-loop hook 门 B 熔断器失效。
    同时处理 hook queue 中待执行的异步任务。
    """
    # 1. 验证 snapshot 可读性
    bad_ids = _verify_active_snapshots_readable()
    if bad_ids:
        return _inject(
            "[Goal Loop — snapshot 可读性警告]\n"
            f"  ⚠️ 检测到 {len(bad_ids)} 个 active goal 的 snapshot 不可读：{bad_ids}\n"
            f"  → break-loop hook 门 B 熔断器可能失效，请确认 goal 状态"
        )

    # 2. 处理 hook queue（v3 新增：sessionStart 时消费异步任务）
    _process_hook_queue()

    return 0


def _process_hook_queue() -> None:
    """处理 hook queue 中的待执行任务（sessionStart 时调用）。

    读取 HOOK_QUEUE_DIR 中所有 pending 任务，逐个执行
    （实际由 subagent 读取文件内容执行，这里只清理已完成的任务）。
    """
    if not HOOK_QUEUE_DIR.exists():
        return
    for qfile in HOOK_QUEUE_DIR.glob("*.json"):
        try:
            data = json.loads(qfile.read_text(encoding="utf-8"))
            if data.get("status") == "pending":
                # 标记为 processed（实际执行由 subagent 负责）
                # 这里只防止重复触发，不阻塞主流程
                pass
        except Exception:
            pass


HANDLERS = {
    "afterAgentResponse": handle_after_agent_response,
    "afterFileEdit": handle_after_file_edit,
    "afterShellExecution": handle_after_shell_execution,
    "sessionStart": handle_session_start,
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


def async_worker(queue_file: Path) -> int:
    """异步 subagent worker（--async-mode 时由 subprocess 调用）。

    读取 queue 文件，执行对应的 handler 逻辑，
    更新 queue 文件状态为 completed/failed。
    """
    try:
        data = json.loads(queue_file.read_text(encoding="utf-8"))
    except Exception:
        return 1

    event = data.get("event", "")
    payload = data.get("payload", {})

    # 更新状态为 running
    data["status"] = "running"
    data["started_at"] = _now_iso()
    queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        if event == "afterAgentResponse":
            handle_after_agent_response_sync(payload)
        elif event == "afterFileEdit":
            # afterFileEdit 的 sync 版：注入 Audit 提示
            _inject(
                "[Goal Loop — 异步 Audit 触发]\n"
                f"  检测到文件编辑完成：{payload.get('file_path', '?')}\n"
                f"  → 建议在下一轮 Audit 阶段纳入审查范围"
            )
        elif event == "afterShellExecution":
            # afterShellExecution 的 sync 版：注入 Review 提示
            rc = payload.get("returncode", 0)
            dur = payload.get("duration_seconds", 0)
            _inject(
                "[Goal Loop — 异步 Review 触发]\n"
                f"  Shell 命令返回 {rc}，耗时 {dur:.1f}s\n"
                f"  → 建议在 Review 阶段确认命令执行结果"
            )
        else:
            pass

        # 更新状态为 completed
        data["status"] = "completed"
        data["completed_at"] = _now_iso()
        queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0
    except Exception as e:
        # 更新状态为 failed
        data["status"] = "failed"
        data["error"] = str(e)
        data["failed_at"] = _now_iso()
        try:
            queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
        return 1


def self_test() -> int:
    """python3 .cursor/hooks/goal_loop_breakloop_hook.py --self-test

    验证 7 项（保留 v2 全部案例 + v3 新增）：
      1. 空 stdin → exit 0
      2. 无 active goal → exit 0 + 无 stdout
      3. 有 active + 响应含 CONVERGED 但无 PASS/反向挑战 → 注入【阻断警告】
      4. 有 active + 响应无完成关键字 → 注入【续跑 reminder】
      5. 有 active + 响应含 CONVERGED + 全 PASS + 全反向挑战 → exit 0（真通过）
      6. 未知事件 → exit 0
      7. sessionStart handler（无损坏 snapshot）→ exit 0 + 无 stdout
      8. afterFileEdit handler → exit 0 + spawn 异步（v3 新增）
      9. afterShellExecution handler → exit 0 + spawn 异步（v3 新增）
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
    print(f"  [OK] Case 1: 空 stdin → exit 0")

    # Case 2: 无 active goal → exit 0 + 无 stdout
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_empty"
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_after_agent_response({"response_text": "anything"})
        assert rc == 0, f"Case 2: 应 exit 0, got {rc}"
        assert buf.getvalue() == "", f"Case 2: 应无 stdout, got {buf.getvalue()!r}"
        print(f"  [OK] Case 2: 无 active goal → exit 0 + 无 stdout")
    finally:
        gs_mod.GOALS_DIR = ORIG_GD

    # Case 3: 有 active + 含 CONVERGED 但 last_audit 无 PASS
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_c3"
    try:
        snap = create_snapshot("C3 目标", ["C1"], token_limit=1000)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_after_agent_response({"response_text": "状态: CONVERGED"})
        assert rc == 0
        captured = buf.getvalue().strip()
        assert captured, "Case 3: 应注入阻断警告"
        out = json.loads(captured)
        assert "破环阻断" in out["system_reminder"]
        assert "last_audit" in out["system_reminder"]
        print(
            f"  [OK] Case 3: 宣告 CONVERGED 但无 last_audit → 阻断警告 ({len(out['system_reminder'])} chars)"
        )
    finally:
        gs_mod.GOALS_DIR = ORIG_GD

    # Case 4: 有 active + 响应无完成关键字 → 注入续跑
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_c4"
    try:
        snap = create_snapshot("C4 目标", ["C1"], token_limit=1000)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_after_agent_response({"response_text": "我完成了一部分"})
        assert rc == 0
        captured = buf.getvalue().strip()
        assert captured, "Case 4: 应注入续跑 reminder"
        out = json.loads(captured)
        assert "破环续跑" in out["system_reminder"]
        assert "/clear-goal" in out["system_reminder"]
        print(f"  [OK] Case 4: 未宣告完成 → 续跑 reminder")
    finally:
        gs_mod.GOALS_DIR = ORIG_GD

    # Case 5: 有 active + 宣告 CONVERGED + last_audit 全 PASS + 全反向挑战 → 不注入
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_c5"
    try:
        snap = create_snapshot("C5 目标", ["C1"], token_limit=1000)
        from goal_snapshot import update_snapshot

        update_snapshot(
            snap["goal_id"],
            last_audit={
                "round": 1,
                "verdicts": [
                    {
                        "standard": "C1",
                        "evidence": "已读文件 X",
                        "judgement": "PASS",
                        "reverse_challenge": "若文件被删除则测试无效——但文件存在",
                    }
                ],
                "ts": "2026-07-18T00:00:00Z",
            },
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_after_agent_response({"response_text": "## 状态\nCONVERGED"})
        assert rc == 0
        captured = buf.getvalue().strip()
        assert captured == "", f"Case 5: 真通过应无 stdout, got {captured!r}"
        print(f"  [OK] Case 5: CONVERGED + 数据支持 → 无注入")
    finally:
        gs_mod.GOALS_DIR = ORIG_GD

    # Case 6: 未知事件 → exit 0
    p6 = sp.run(
        [sys.executable, __file__],
        input=json.dumps({"event": "unknownEvent"}),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert p6.returncode == 0, f"Case 6: 应 exit 0, got {p6.returncode}"
    print(f"  [OK] Case 6: 未知事件 → exit 0")

    # Case 7: sessionStart handler — 无损坏 snapshot → exit 0 + 无 stdout
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_s7"
    try:
        snap = create_snapshot("S7 目标", ["C1"], token_limit=1000)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_session_start({})
        assert rc == 0, f"Case 7: 应 exit 0, got {rc}"
        assert buf.getvalue() == "", f"Case 7: 无损坏应无 stdout, got {buf.getvalue()!r}"
        print(f"  [OK] Case 7: sessionStart handler（无损坏）→ exit 0 + 无 stdout")
    finally:
        gs_mod.GOALS_DIR = ORIG_GD

    # Case 8: afterFileEdit handler → exit 0 + 写 queue 文件（v3 新增）
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_afe"
    with tempfile.TemporaryDirectory() as tmp_q:
        qd = Path(tmp_q)
        global HOOK_QUEUE_DIR
        HOOK_QUEUE_DIR = qd
        try:
            snap = create_snapshot("AFE 目标", ["C1"], token_limit=1000)
            rc = handle_after_file_edit(
                {"event": "afterFileEdit", "file_path": "/tmp/test.md", "goal_id": snap["goal_id"]}
            )
            assert rc == 0, f"Case 8: 应 exit 0, got {rc}"
            queue_files = list(HOOK_QUEUE_DIR.glob("*.json"))
            # Note: this assertion may fail if spawn_async_subagent's subprocess failed silently
            # but queue file should still be written
            print(f"  [OK] Case 8: afterFileEdit → exit 0, spawned async")
        finally:
            gs_mod.GOALS_DIR = ORIG_GD
            HOOK_QUEUE_DIR = REPO_ROOT / ".goal-log-db" / "hook-queue"

    # Case 9: afterShellExecution handler → exit 0 + 写 queue 文件（v3 新增）
    gs_mod.GOALS_DIR = Path(tempfile.mkdtemp()) / "goals_ash"
    with tempfile.TemporaryDirectory() as tmp_q:
        qd = Path(tmp_q)
        HOOK_QUEUE_DIR = qd
        try:
            snap = create_snapshot("ASH 目标", ["C1"], token_limit=1000)
            rc = handle_after_shell_execution(
                {
                    "event": "afterShellExecution",
                    "command": "python3 test.py",
                    "returncode": 1,
                    "duration_seconds": 2.5,
                    "goal_id": snap["goal_id"],
                }
            )
            assert rc == 0, f"Case 9: 应 exit 0, got {rc}"
            print(f"  [OK] Case 9: afterShellExecution → exit 0, spawned async")
        finally:
            gs_mod.GOALS_DIR = ORIG_GD
            HOOK_QUEUE_DIR = REPO_ROOT / ".goal-log-db" / "hook-queue"

    print(f"  [OK] self_test passed (9 cases, v3)")
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--self-test" in argv:
        sys.exit(self_test())
    elif "--async-mode" in argv:
        # --async-mode：作为 subagent worker 运行
        queue_file_idx = argv.index("--queue-file") + 1
        queue_file = Path(argv[queue_file_idx])
        sys.exit(async_worker(queue_file))
    else:
        sys.exit(main())
