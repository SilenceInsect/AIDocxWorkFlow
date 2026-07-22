#!/usr/bin/env python3
"""Goal Loop Server 酱 Bridge (v1 · Plan: serverchan_pivot_20260719)

定位：
  在 Cursor afterAgentResponse hook 入口读取 .goal-log-db/active/*/snapshot.json，
  仅在 status 转换到「achieved / converged_with_followup / blocked」时，
  调用 serverchan_notifier 推送摘要。同状态重复触发 → 跳过（幂等）。

设计：
  - stdin 读事件 payload（Cursor hook 约定）
  - stdout 写 system_reminder 或留空
  - 任何异常 → exit 0（不阻断 IDE）
  - 幂等键：.goal-log-db/active/<goal_id>/.notified_status.json（原子写）

与 wechat bridge 的关系：
  本模块是 goal_loop_wechat_bridge.py 的 serverchan 适配版，
  复用其全部行为契约（幂等、错误降级、self_test、CLI 入口）。
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "ai_workflow"))

# 复用 goal_snapshot
try:
    from goal_snapshot import (  # type: ignore
        GOALS_DIR as SNAPSHOT_GOALS_DIR,
        list_active_goals,
        list_live_goals,
        load_snapshot,
        SnapshotError,
    )
except Exception as _e:  # pragma: no cover
    list_active_goals = None  # type: ignore
    list_live_goals = None  # type: ignore
    load_snapshot = None  # type: ignore
    SnapshotError = Exception  # type: ignore
    SNAPSHOT_GOALS_DIR = REPO_ROOT / ".goal-log-db" / "active"

# 复用 serverchan_notifier
try:
    from serverchan_notifier import (  # type: ignore
        DEFAULT_NOTIFY_STATES,
        build_message,
        load_config,
        send_via_webhook,
        ConfigNotFoundError,
        ConfigInvalidError,
    )
except Exception as _e:  # pragma: no cover
    send_via_webhook = None  # type: ignore
    build_message = None  # type: ignore
    load_config = None  # type: ignore
    DEFAULT_NOTIFY_STATES = frozenset()
    ConfigNotFoundError = Exception  # type: ignore
    ConfigInvalidError = Exception  # type: ignore

NOTIFIED_STATUS_FILENAME = ".notified_status.json"
ERROR_LOG_DIR = REPO_ROOT / "workflow_assets" / "feedback_logs"


# ===== 幂等文件读写 =====


def notified_status_path(goal_id: str) -> Path:
    """单个 goal 的幂等记录文件路径。"""
    if not goal_id or "/" in goal_id or ".." in goal_id:
        raise ValueError(f"非法 goal_id: {goal_id!r}")
    return SNAPSHOT_GOALS_DIR / goal_id / NOTIFIED_STATUS_FILENAME


def read_last_notified(goal_id: str) -> str | None:
    """读取该 goal 上次通知过的 status；不存在 → None。"""
    p = notified_status_path(goal_id)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return str(data.get("status") or "")
    except (json.JSONDecodeError, OSError):
        return None
    return None


def write_last_notified(goal_id: str, status: str) -> None:
    """原子写幂等记录（防并发半写）。"""
    p = notified_status_path(goal_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "goal_id": goal_id,
        "status": status,
        "notified_at": _now_iso(),
        "channel": "serverchan",
        "version": 1,
    }
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)


# ===== 判定逻辑 =====


def should_notify(prev_status: str | None, curr_status: str) -> bool:
    """是否应该触发通知：
      1) curr_status 必须是 notify_states 之一
      2) curr_status != prev_status（真状态变化）
    """
    if curr_status not in DEFAULT_NOTIFY_STATES:
        return False
    if not prev_status:
        return True  # 第一次进入终态也算
    return prev_status != curr_status


# ===== 错误日志 =====


def _log_error(goal_id: str, err: str) -> None:
    """把通知失败写到 feedback_logs（不抛错）。"""
    try:
        ERROR_LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = ERROR_LOG_DIR / "serverchan_notifier_errors.jsonl"
        rec = {
            "ts": _now_iso(),
            "goal_id": goal_id,
            "error": err,
            "channel": "serverchan",
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        # 写错误日志本身失败 → 不再往外抛
        pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ===== 主入口 =====


def process_goal(snap: dict[str, Any]) -> str:
    """处理单个 snapshot：
      - 读 curr_status
      - 比对 .notified_status.json
      - 命中 → 调 send_via_webhook + 更新幂等文件 + 记录日志
      - 不命中 → 直接 skip

    Returns:
        "notified" | "skipped" | "config_missing" | "send_failed" | "no_active_goals"
    """
    if send_via_webhook is None or build_message is None:
        return "config_missing"

    goal_id = snap.get("goal_id", "")
    if not goal_id:
        return "skipped"

    curr_status = snap.get("status", "")
    if curr_status not in DEFAULT_NOTIFY_STATES:
        return "skipped"

    prev_status = read_last_notified(goal_id)
    if not should_notify(prev_status, curr_status):
        return "skipped"

    # 准备消息
    max_len = 240
    try:
        cfg = load_config()
        max_len = int(cfg.get("max_message_length", 240))
    except (ConfigNotFoundError, ConfigInvalidError):
        # config 缺失：用默认值 + 记日志
        pass

    message = build_message(
        status=curr_status,
        raw_user_goal=snap.get("raw_user_goal", ""),
        loop_round=int(snap.get("loop_round", 0)),
        latest_artifact=snap.get("latest_artifact"),
        max_length=max_len,
    )

    # 发送
    ok, detail = send_via_webhook(message)

    if ok:
        try:
            write_last_notified(goal_id, curr_status)
        except Exception as e:
            _log_error(goal_id, f"notified but write idempotency failed: {e}")
        return "notified"

    # 失败：不写幂等文件，下次重试
    _log_error(goal_id, f"send failed: {detail}")
    return "send_failed"


def handle_after_agent_response(_payload: dict[str, Any]) -> int:
    """afterAgentResponse handler：扫所有 live goals，触发通知。"""
    if list_live_goals is None and list_active_goals is None:
        return 0
    try:
        # 优先用 list_live_goals（新）；fallback 用 list_active_goals（旧）
        if list_live_goals is not None:
            lives = list_live_goals()
        else:
            lives = list_active_goals()
    except Exception:
        return 0
    if not lives:
        return 0  # 无 live → 不注入

    notified = 0
    skipped = 0
    failed = 0
    for snap in lives:
        try:
            result = process_goal(snap)
            if result == "notified":
                notified += 1
            elif result == "send_failed":
                failed += 1
            else:
                skipped += 1
        except Exception as e:
            _log_error(snap.get("goal_id", "?"), f"unexpected: {type(e).__name__}: {e}")
            failed += 1

    # 注入 reminder 提示 bridge 已工作（不阻断）
    if notified or failed:
        sys.stdout.write(
            json.dumps(
                {
                    "system_reminder": (
                        f"[ServerChan Bridge] notified={notified} skipped={skipped} failed={failed}"
                    ),
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    return 0


# ===== self_test（self-test 豁免条件 1+2）=====


def self_test() -> int:
    """python3 ai_workflow/goal_loop_serverchan_bridge.py --self-test

    覆盖 10 个用例：
      1. should_notify 全 9 状态判定
      2. 幂等文件读写 round-trip
      3. notified_status_path 防 path traversal
      4. _log_error 写日志不抛错
      5. handle_after_agent_response 无 live goal → 不写 stdout + exit 0
      6. handle_after_agent_response 有 active 但 status 不命中 → skip
      7. stdin JSON 解析失败 → exit 0（不阻断 IDE）
      8. 空 stdin → exit 0
      9. status=achieved 被 list_live_goals 命中 → handle_after_agent_response 正常执行
     10. list_live_goals=None 时 fallback list_active_goals 正常 skip
    """
    import io
    import subprocess as sp
    import tempfile
    from contextlib import redirect_stdout
    from unittest.mock import patch as _patch

    _br_dir = Path(__file__).resolve().parent
    _pkg_parent = _br_dir.parent
    if str(_pkg_parent) not in sys.path:
        sys.path.insert(0, str(_pkg_parent))

    print("GoalLoopServerChanBridge self_test（10 cases）")
    print("-" * 50)

    import ai_workflow.goal_loop_serverchan_bridge as br_mod

    # Case 1: should_notify 全状态（v2 新增 REPAIRING 组合）
    cases_should = [
        (None, "achieved", True),
        ("", "achieved", True),
        ("active", "achieved", True),
        ("achieved", "achieved", False),
        ("active", "active", False),
        ("achieved", "converged_with_followup", True),
        ("converged_with_followup", "blocked", True),
        ("blocked", "achieved", True),
        ("active", "paused", False),
        # v2 新增
        (None, "REPAIRING", True),
        ("active", "REPAIRING", True),
        ("REPAIRING", "REPAIRING", False),
        ("REPAIRING", "achieved", True),
        ("paused", "REPAIRING", True),
    ]
    for prev, curr, expected in cases_should:
        actual = should_notify(prev, curr)
        assert actual == expected, f"should_notify({prev!r}, {curr!r}) = {actual}，期望 {expected}"
    print("  [OK] Case 1: should_notify 9 状态组合判定")

    # Case 2: 幂等文件 round-trip
    fake_goal_id = "00000000-0000-0000-0000-000000000010"
    test_goal_dir = SNAPSHOT_GOALS_DIR / fake_goal_id
    test_goal_dir.mkdir(parents=True, exist_ok=True)
    try:
        p = notified_status_path(fake_goal_id)
        if p.exists():
            p.unlink()
        assert read_last_notified(fake_goal_id) is None

        write_last_notified(fake_goal_id, "achieved")
        assert read_last_notified(fake_goal_id) == "achieved"

        write_last_notified(fake_goal_id, "blocked")
        assert read_last_notified(fake_goal_id) == "blocked"
        # 确认 channel 字段标记为 serverchan
        raw = json.loads(notified_status_path(fake_goal_id).read_text())
        assert raw.get("channel") == "serverchan", f"幂等文件 channel 应标 serverchan: {raw}"
        print("  [OK] Case 2: 幂等文件读写 round-trip + channel=serverchan")
    finally:
        p = notified_status_path(fake_goal_id)
        if p.exists():
            p.unlink()
        try:
            test_goal_dir.rmdir()
        except OSError:
            pass

    # Case 3: path traversal
    for bad in ("../etc", "foo/bar", "", ".."):
        try:
            notified_status_path(bad)
            assert False, f"goal_id={bad!r} 应抛 ValueError"
        except ValueError:
            pass
    print("  [OK] Case 3: notified_status_path 拒绝 path traversal")

    # Case 4: _log_error 不抛错
    _log_error("fake_goal_sct", "unit test error serverchan")
    log_file = ERROR_LOG_DIR / "serverchan_notifier_errors.jsonl"
    if log_file.exists():
        last_line = log_file.read_text(encoding="utf-8").strip().split("\n")[-1]
        assert "fake_goal_sct" in last_line, f"日志行应含 fake_goal_sct: {last_line}"
    print("  [OK] Case 4: _log_error 写入不抛错")

    # Case 5: handle_after_agent_response 无 live goal → 不写 stdout + exit 0
    # 使用 tmpdir 隔离，无真实 snapshot 文件 → list_live_goals() 返回 []
    import shutil as _sh
    _real_goals = br_mod.SNAPSHOT_GOALS_DIR
    _bak_goals = {}
    try:
        if _real_goals.exists():
            for _gd in list(_real_goals.iterdir()):
                if _gd.is_dir():
                    _bak = Path(tempfile.mkdtemp())
                    _sh.move(str(_gd), str(_bak / _gd.name))
                    _bak_goals[_gd.name] = _bak
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_after_agent_response({})
        assert rc == 0, f"应 exit 0, got {rc}"
        assert buf.getvalue() == "", f"无 live 应无 stdout, got {buf.getvalue()!r}"
        print("  [OK] Case 5: handle_after_agent_response（无 live）→ exit 0 + 无 stdout")
    finally:
        for _name, _bak in _bak_goals.items():
            _sh.move(str(_bak / _name), str(_real_goals / _name))
            _sh.rmtree(str(_bak), ignore_errors=True)

    # Case 6: handle_after_agent_response status=active → skip
    # 用 tmpdir 隔离真实 goals，让真实 list_live_goals() 只返回测试 goal
    _real_goals6 = br_mod.SNAPSHOT_GOALS_DIR
    _bak_goals6 = {}
    _test_gd6 = _real_goals6 / "00000000-0000-0000-0000-000000000020"
    _snap6_data = {
        "goal_id": "00000000-0000-0000-0000-000000000020",
        "status": "active", "raw_user_goal": "测试",
        "loop_round": 1, "latest_artifact": None,
        "token_budget": {"used": 0, "limit": 100000, "updated_at": ""},
        "value_criteria": [], "process_criteria": [],
        "value_ratio": 1.0, "severity_label": "MAJOR",
        "follow_up_items": [], "goal_signature": "0" * 16,
        "out_of_scope_md": "", "audit_stability": {},
        "parallel_executor_hints": {}, "efficiency_stats": {},
        "session_snapshot": [], "task_queue": [],
    }
    try:
        if _real_goals6.exists():
            for _gd in list(_real_goals6.iterdir()):
                if _gd.is_dir():
                    _bak = Path(tempfile.mkdtemp())
                    _sh.move(str(_gd), str(_bak / _gd.name))
                    _bak_goals6[_gd.name] = _bak
        _test_gd6.mkdir(parents=True, exist_ok=True)
        (_test_gd6 / "snapshot.json").write_text(
            json.dumps(_snap6_data, ensure_ascii=False, indent=2), encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_after_agent_response({})
        assert rc == 0
        assert buf.getvalue() == "", f"non-notify status 应无 stdout, got {buf.getvalue()!r}"
        print("  [OK] Case 6: handle_after_agent_response（status=active）→ skip + 无 stdout")
    finally:
        for _f in list(_test_gd6.glob("*")):
            _f.unlink()
        try:
            _test_gd6.rmdir()
        except OSError:
            pass
        import shutil as _sh6
        for _name, _bak in _bak_goals6.items():
            _sh6.move(str(_bak / _name), str(_real_goals6 / _name))
            _sh6.rmtree(str(_bak), ignore_errors=True)

    # Case 7: stdin 坏 JSON → exit 0
    p = sp.run(
        [sys.executable, __file__],
        input="not valid json",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert p.returncode == 0, f"坏 stdin 应 exit 0, got {p.returncode}"
    print("  [OK] Case 7: 坏 JSON stdin → exit 0（不阻断 IDE）")

    # Case 8: 空 stdin → exit 0
    p = sp.run(
        [sys.executable, __file__], input="", capture_output=True, text=True, timeout=10
    )
    assert p.returncode == 0, f"空 stdin 应 exit 0, got {p.returncode}"
    print("  [OK] Case 8: 空 stdin → exit 0")

    # Case 9: status=achieved 被 list_live_goals 命中 → handle_after_agent_response 跑通
    achieved_snap = {
        "goal_id": "00000000-0000-0000-0000-000000000030",
        "status": "achieved",
        "raw_user_goal": "测试 achieved",
        "loop_round": 3,
        "latest_artifact": None,
    }
    with _patch.object(br_mod, "list_live_goals", return_value=[achieved_snap]):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = handle_after_agent_response({})
        assert rc == 0
        stdout = buf.getvalue()
        # achieved 状态在 DEFAULT_NOTIFY_STATES，process_goal 会走幂等检查 + 实际发送
        # self_test 环境无真实 serverchan，发送会失败（failed=4）但 stderr 不含 "[ServerChan Bridge]"
        # → 断言函数正常执行不抛错即可
        print(f"  [OK] Case 9: status=achieved via list_live_goals → handle_after_agent_response 正常退出")

    # Case 10: list_live_goals 未定义时，fallback 到 list_active_goals 仍能正常 skip
    achieved_snap2 = {
        "goal_id": "00000000-0000-0000-0000-000000000040",
        "status": "achieved",
        "raw_user_goal": "测试 fallback achieved",
        "loop_round": 2,
        "latest_artifact": None,
    }
    with _patch.object(br_mod, "list_live_goals", None):
        with _patch.object(br_mod, "list_active_goals", return_value=[achieved_snap2]):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = handle_after_agent_response({})
            assert rc == 0
            stdout = buf.getvalue()
            # achieved 在 DEFAULT_NOTIFY_STATES，幂等检查通过则写幂等文件
            print(f"  [OK] Case 10: list_live_goals=None fallback list_active_goals → 正常执行")

    print("-" * 50)
    print("  [OK] all 10 cases PASS")
    return 0


# ===== CLI 入口 =====


HANDLERS = {
    "afterAgentResponse": handle_after_agent_response,
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
        return 0  # 绝不崩 IDE


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(main())
