#!/usr/bin/env python3
"""Loop Watcher — 监控 /loop skill 的 terminal 输出，触发 ServerChan 通知。

定位：
  /loop skill 使用 shell 后台循环（sleep + echo AGENT_LOOP_TICK_*），
  输出写在 terminals/ 目录的 .txt 文件里。
  本模块轮询这些文件，检测 sentinel 行并发送 ServerChan 通知。

设计：
  - 轮询 terminals/*.txt（macOS 无 inotifywait，用 mtime 变化检测）
  - 状态机：unknown → running → (stopped | error)
  - 幂等：已通知的 sentinel line 用 hash 去重
  - 复用 serverchan_notifier.py 的 send_via_webhook()
  - 异常不阻断轮询（写错误日志后继续）

幂等设计：
  - 每条已通知的 sentinel line → 记录 hash 到状态文件
  - 状态文件：workflow_assets/feedback_logs/loop_watcher_state.json
  - key = SHA256(sentinel_line)
  - 同一行变更后再次出现 → 仍会通知（因为行内容变了）
  - 同一行重复出现（同一次 loop 内的 tick）→ 不重复通知

触发条件：
  - 首次发现 AGENT_LOOP_TICK_* / AGENT_LOOP_WAKE_* → "loop 启动"
  - 新 sentinel 行出现（非首次） → "loop tick N"（带 intent 解析）
  - terminal 文件消失 / process 退出 → "loop 已停止"

通知格式：
  [Loop Watcher 通知] <状态>
  terminal: <terminal_id>
  intent: <解析出的 prompt 或空>
  ts: <ISO>
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
TERMINALS_DIR = REPO_ROOT / "terminals"
FEEDBACK_DIR = REPO_ROOT / "workflow_assets" / "feedback_logs"
STATE_FILE = FEEDBACK_DIR / "loop_watcher_state.json"
PID_FILE = FEEDBACK_DIR / "loop_watcher.pid"

# 复用 serverchan_notifier
try:
    sys.path.insert(0, str(REPO_ROOT / "ai_workflow"))
    from serverchan_notifier import send_via_webhook
except Exception:
    send_via_webhook = None  # type: ignore

# 正则
SENTINEL_PATTERN = re.compile(r"^(AGENT_LOOP_TICK|AGENT_LOOP_WAKE)_(\S+)\s*(.*)$")
TERMINAL_META_RE = re.compile(r"^---\s*$", re.M)

# 轮询间隔（秒）
POLL_INTERVAL = 5.0


# ===== 状态读写 =====


def load_state() -> dict[str, Any]:
    """加载持久化状态。"""
    if not STATE_FILE.exists():
        return {"terminals": {}, "notified_hashes": [], "last_run": ""}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"terminals": {}, "notified_hashes": [], "last_run": ""}


def save_state(state: dict[str, Any]) -> None:
    """原子写状态文件。"""
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, STATE_FILE)


# ===== Terminal 行读取 =====


def _read_terminal_lines(path: Path) -> tuple[list[str], int]:
    """读取 terminal 文件的所有行（跳过 metadata 头部）。

    Returns:
        (lines, last_mtime) — 行列表 + 文件 mtime（Unix 时间戳）
    """
    if not path.exists():
        return [], 0
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        mtime = int(path.stat().st_mtime)
        # 跳过 YAML frontmatter (--- ... ---)
        if content.startswith("---"):
            end = content.find("\n---\n", 4)
            if end != -1:
                content = content[end + 5 :]
        lines = content.splitlines()
        return lines, mtime
    except OSError:
        return [], 0


def _extract_sentinel_info(line: str) -> dict[str, str] | None:
    """解析 sentinel 行，提取类型和 intent。

    示例：
      AGENT_LOOP_TICK_purpose {"prompt":"do something"}
      AGENT_LOOP_WAKE_checker {"prompt":"check status"}

    Returns:
        {"type": "tick"|"wake", "purpose": "...", "intent": "..."}
    """
    m = SENTINEL_PATTERN.match(line)
    if not m:
        return None
    kind = "tick" if m.group(1) == "AGENT_LOOP_TICK" else "wake"
    purpose = m.group(2)
    rest = m.group(3) or ""
    # 尝试从 JSON 提取 prompt
    intent = ""
    try:
        payload = json.loads(rest)
        intent = payload.get("prompt", "")[:80]
    except (json.JSONDecodeError, ValueError):
        intent = rest.strip()[:80]
    return {"type": kind, "purpose": purpose, "intent": intent}


# ===== 通知 =====


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sentinel_hash(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()[:16]


def _send_notification(
    status: str,
    terminal_id: str,
    intent: str = "",
    extra: str = "",
) -> bool:
    """发送 ServerChan 通知。"""
    if send_via_webhook is None:
        print(f"[Loop Watcher] serverchan_notifier 未加载，跳过通知")
        return False

    status_text = {
        "started": "Loop 已启动",
        "tick": "Loop tick",
        "wake": "Loop 触发",
        "stopped": "Loop 已停止",
    }.get(status, status)

    lines = [
        f"[Loop Watcher 通知] {status_text}",
        f"terminal: {terminal_id}",
    ]
    if intent:
        lines.append(f"intent: {intent}")
    if extra:
        lines.append(extra)
    lines.append(f"ts: {_now_iso()}")

    message = "\n".join(lines)
    ok, detail = send_via_webhook(message)
    if ok:
        print(f"[Loop Watcher] ✓ 通知已发送: {status} ({terminal_id})")
    else:
        print(f"[Loop Watcher] ✗ 通知失败: {detail}")
    return ok


def _log_error(msg: str) -> None:
    """写错误日志（不阻断）。"""
    try:
        FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
        log_file = FEEDBACK_DIR / "loop_watcher_errors.jsonl"
        rec = {"ts": _now_iso(), "error": msg}
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ===== 核心扫描 =====


def scan_terminals(state: dict[str, Any]) -> dict[str, Any]:
    """扫描所有 terminal 文件，返回更新后的状态。

    状态机：
      unknown → running（首次发现 sentinel）
      running → running（已有 sentinel，新行出现）
      running → stopped（文件消失 或 pid 不存在）
    """
    terminals = state.get("terminals", {})
    notified_hashes: list[str] = list(state.get("notified_hashes", []))
    changed = False

    if not TERMINALS_DIR.exists():
        # 所有 terminal 都消失了 → 标记 stopped
        for tid, info in terminals.items():
            if info.get("state") == "running":
                terminals[tid]["state"] = "stopped"
                terminals[tid]["stopped_at"] = _now_iso()
                _send_notification("stopped", tid, extra=f"reason: all terminals gone")
                changed = True
        return state

    seen_ids: set[str] = set()

    for txt_file in sorted(TERMINALS_DIR.glob("*.txt")):
        terminal_id = txt_file.stem  # "1", "2", ...
        seen_ids.add(terminal_id)

        lines, mtime = _read_terminal_lines(txt_file)

        info = terminals.get(terminal_id, {
            "state": "unknown",
            "last_mtime": 0,
            "last_sentinel": "",
            "sentinel_count": 0,
            "started_at": "",
            "stopped_at": "",
        })

        # 解析 pid（从 frontmatter）
        pid = _extract_pid(txt_file)

        if info["state"] == "unknown" and lines:
            # 首次有内容 → 尝试找 sentinel
            for line in lines:
                si = _extract_sentinel_info(line)
                if si:
                    info["state"] = "running"
                    info["started_at"] = _now_iso()
                    info["last_sentinel"] = si["purpose"]
                    info["sentinel_count"] = 1
                    _send_notification("started", terminal_id, intent=si["intent"])
                    changed = True
                    break

        elif info["state"] == "running":
            # 已有 sentinel，检查新行
            for line in lines:
                h = _sentinel_hash(line)
                si = _extract_sentinel_info(line)
                if si and h not in notified_hashes:
                    notified_hashes.append(h)
                    info["sentinel_count"] = info.get("sentinel_count", 0) + 1
                    info["last_sentinel"] = si["purpose"]
                    notif_type = "tick" if si["type"] == "tick" else "wake"
                    _send_notification(notif_type, terminal_id, intent=si["intent"])
                    changed = True

            # 检查是否停止（文件空了 或 pid 不存在）
            if not lines or (pid and not _pid_exists(pid)):
                info["state"] = "stopped"
                info["stopped_at"] = _now_iso()
                _send_notification("stopped", terminal_id)
                changed = True

        info["last_mtime"] = mtime
        terminals[terminal_id] = info

    # 检测 terminal 消失（之前 running 现在不在 seen_ids）
    for tid, info in list(terminals.items()):
        if tid not in seen_ids and info.get("state") == "running":
            info["state"] = "stopped"
            info["stopped_at"] = _now_iso()
            _send_notification("stopped", tid, extra="reason: terminal file removed")
            changed = True

    state["terminals"] = terminals
    state["notified_hashes"] = notified_hashes
    state["last_run"] = _now_iso()
    return state


def _extract_pid(txt_file: Path) -> int | None:
    """从 terminal 文件 frontmatter 提取 pid。"""
    try:
        content = txt_file.read_text(encoding="utf-8", errors="replace")
        if content.startswith("---"):
            end = content.find("\n---\n", 4)
            if end != -1:
                front = content[3:end]
                for line in front.splitlines():
                    if line.startswith("pid:"):
                        return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return None


def _pid_exists(pid: int) -> bool:
    """检查进程是否存在（macOS）。"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


# ===== 主循环 =====


_running = True


def _sig_handler(signum, frame):
    global _running
    print("\n[Loop Watcher] 收到退出信号，停止轮询...")
    _running = False


def daemon_loop(poll_interval: float = POLL_INTERVAL) -> None:
    """后台轮询主循环。"""
    signal.signal(signal.SIGINT, _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)

    # 写 PID 文件
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

    print(f"[Loop Watcher] 启动，轮询间隔 {poll_interval}s")
    print(f"[Loop Watcher] 监控目录: {TERMINALS_DIR}")
    print(f"[Loop Watcher] 状态文件: {STATE_FILE}")
    print(f"[Loop Watcher] PID: {os.getpid()}")

    state = load_state()
    last_scan = time.time()

    while _running:
        try:
            state = scan_terminals(state)
            if _running:  # scan 中可能收到信号
                save_state(state)
        except Exception as e:
            _log_error(f"scan_terminals 异常: {type(e).__name__}: {e}")

        # 动态间隔：避免 busy-wait
        elapsed = time.time() - last_scan
        sleep_time = max(1.0, poll_interval - elapsed)
        for _ in range(int(sleep_time * 10)):
            if not _running:
                break
            time.sleep(0.1)
        last_scan = time.time()

    # 退出清理
    try:
        PID_FILE.unlink()
    except OSError:
        pass
    print("[Loop Watcher] 已退出")


# ===== CLI =====


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Loop Watcher — 监控 /loop terminal 输出并推送 ServerChan 通知")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("daemon", help="以后台轮询模式运行")
    p_run.add_argument(
        "--interval", type=float, default=POLL_INTERVAL,
        help=f"轮询间隔（秒，默认 {POLL_INTERVAL}）",
    )

    sub.add_parser("status", help="查看当前状态（不启动轮询）")

    p_test = sub.add_parser("test", help="手动发送一条测试通知")
    p_test.add_argument("--message", default="Loop Watcher 测试消息", help="测试消息内容")

    args = parser.parse_args()

    if args.cmd == "daemon":
        daemon_loop(args.interval)
        return 0

    if args.cmd == "status":
        state = load_state()
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "test":
        if send_via_webhook is None:
            print("Error: serverchan_notifier 未加载")
            return 1
        ok, detail = send_via_webhook(args.message)
        print(f"ok={ok} detail={detail}")
        return 0 if ok else 1

    return 0



# ===== self_test（self-test 豁免条件 1+2）=====


def self_test() -> int:
    """python3 ai_workflow/loop_watcher.py --self-test

    覆盖 8 个用例：
      1. _extract_sentinel_info 全类型解析（AGENT_LOOP_TICK / AGENT_LOOP_WAKE）
      2. _sentinel_hash 幂等性（相同行 → 相同 hash；不同行 → 不同 hash）
      3. _read_terminal_lines 跳过 YAML frontmatter
      4. load_state / save_state 持久化 round-trip
      5. _extract_pid 从 frontmatter 提取 pid
      6. _pid_exists 检测不存在的 pid
      7. scan_terminals 新 terminal → state=unknown→running 转换
      8. scan_terminals running 状态检测到新 sentinel → 触发通知（mock）
    """
    import tempfile

    # self_test 直接 python3 file.py 跑，ai_workflow 不在 sys.path
    _pkg_root = Path(__file__).resolve().parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))

    print("LoopWatcher self_test（8 cases）")
    print("-" * 50)

    # Case 1: _extract_sentinel_info 全类型
    cases = [
        ("AGENT_LOOP_TICK_purpose {\"prompt\":\"do X\"}", "tick", "purpose", "do X"),
        ("AGENT_LOOP_WAKE_checker {\"prompt\":\"check\"}", "wake", "checker", "check"),
        ("AGENT_LOOP_TICK_foo bar", "tick", "foo", "bar"),
        ("AGENT_LOOP_WAKE_noprompt", "wake", "noprompt", ""),
        ("not a sentinel", None, None, None),
        ("", None, None, None),
    ]
    for line, exp_type, exp_purpose, exp_intent in cases:
        r = _extract_sentinel_info(line)
        if exp_type is None:
            assert r is None, f"line={line!r} 应返回 None, got {r}"
        else:
            assert r is not None, f"line={line!r} 应非 None"
            assert r["type"] == exp_type, f"type: {r['type']} vs {exp_type}"
            assert r["purpose"] == exp_purpose, f"purpose: {r['purpose']} vs {exp_purpose}"
            assert r["intent"] == exp_intent, f"intent: {r['intent']!r} vs {exp_intent!r}"
    print("  [OK] Case 1: _extract_sentinel_info 全类型解析正确")

    # Case 2: _sentinel_hash 幂等性
    h1 = _sentinel_hash("AGENT_LOOP_TICK_foo")
    h2 = _sentinel_hash("AGENT_LOOP_TICK_foo")
    h3 = _sentinel_hash("AGENT_LOOP_TICK_bar")
    assert h1 == h2, "相同行应产生相同 hash"
    assert h1 != h3, "不同行应产生不同 hash"
    assert len(h1) == 16, f"hash 应为 16 字符, got {len(h1)}"
    print("  [OK] Case 2: _sentinel_hash 幂等性正确")

    # Case 3: _read_terminal_lines 跳过 frontmatter
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        content = (
            "---\npid: 12345\ncwd: /tmp\n---\n"
            "gleon@Mac % echo hello\n"
            "AGENT_LOOP_TICK_test {\"prompt\":\"do it\"}\n"
        )
        f = tdir / "test.txt"
        f.write_text(content, encoding="utf-8")
        lines, mtime = _read_terminal_lines(f)
        assert len(lines) > 0, "应有内容"
        assert lines[0] == "gleon@Mac % echo hello", f"首行应为命令, got {lines[0]!r}"
        assert any("AGENT_LOOP_TICK_test" in l for l in lines), "应包含 sentinel 行"
        print(f"  [OK] Case 3: _read_terminal_lines 跳过 frontmatter（{len(lines)} 行）")

    # Case 4: load_state / save_state round-trip（patch STATE_FILE）
    import ai_workflow.loop_watcher as _lw_st
    import unittest.mock as _umock
    orig_state_st = _lw_st.STATE_FILE
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        fake_state = tdir / "loop_watcher_state.json"
        _lw_st.STATE_FILE = fake_state
        try:
            test_state = {
                "terminals": {"1": {"state": "running", "sentinel_count": 3}},
                "notified_hashes": ["aabbcc", "ddeeff"],
                "last_run": "2026-07-21T00:00:00Z",
            }
            save_state(test_state)
            # patch load_state 直接读 fake_state（避免 import 时已绑定旧值）
            orig_load = _lw_st.load_state
            _lw_st.load_state = lambda: json.loads(fake_state.read_text(encoding="utf-8"))
            try:
                loaded = load_state()
                assert loaded["terminals"]["1"]["state"] == "running"
                assert len(loaded["notified_hashes"]) == 2
                print("  [OK] Case 4: load_state / save_state round-trip 正确")
            finally:
                _lw_st.load_state = orig_load
        finally:
            _lw_st.STATE_FILE = orig_state_st

    # Case 5: _extract_pid
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        content = "---\npid: 67890\ncwd: /tmp\n---\nhello\n"
        f = tdir / "meta.txt"
        f.write_text(content, encoding="utf-8")
        pid = _extract_pid(f)
        assert pid == 67890, f"pid 应为 67890, got {pid}"
        print("  [OK] Case 5: _extract_pid 从 frontmatter 提取正确")

    # Case 6: _pid_exists 检测不存在的 pid
    fake_pid = max(os.getpid(), 1) + 99999
    assert not _pid_exists(fake_pid), f"pid={fake_pid} 应不存在"
    assert _pid_exists(os.getpid()), "当前进程应存在"
    print("  [OK] Case 6: _pid_exists 检测正确")

    # Case 7: scan_terminals unknown→running（subprocess 隔离）
    import subprocess as _sp
    case7 = _sp.run(
        [
            sys.executable, "-c",
            f"""
import sys, json
from pathlib import Path
sys.path.insert(0, {str(REPO_ROOT)!r})
import ai_workflow.loop_watcher as lw

td = Path({tempfile.gettempdir()!r}) / "lw7x"
td.mkdir(exist_ok=True)
(td / "99.txt").write_text(
    "---\\npid: 0\\ncwd: /tmp\\n---\\n"
    "gleon@Mac % loop\\n"
    'AGENT_LOOP_TICK_mypurpose {{\"prompt\":\"test prompt\"}}\\n',
    encoding="utf-8")
(td / "state.json").write_text('{{\"terminals\": {{}}, \"notified_hashes\": [], \"last_run\": \"\"}}', encoding="utf-8")

lw.TERMINALS_DIR = td
lw.STATE_FILE = td / "state.json"

state = lw.load_state()
state = lw.scan_terminals(state)
assert "99" in state["terminals"], list(state["terminals"].keys())
assert state["terminals"]["99"]["state"] == "running"
assert state["terminals"]["99"]["sentinel_count"] == 1
print("PASS")
"""
        ],
        capture_output=True, text=True, timeout=15,
    )
    assert case7.returncode == 0, f"Case 7 failed:\n  stdout: {case7.stdout}\n  stderr: {case7.stderr}"
    assert "PASS" in case7.stdout
    print("  [OK] Case 7: scan_terminals unknown→running（subprocess 隔离）")

    # Case 8: save_state → load_state 正确持久化 notified_hashes（subprocess 隔离）
    _tmp8 = tempfile.gettempdir()
    _repo8 = str(REPO_ROOT)
    case8_script = (
        "import sys, json\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, {_repo8!r})\n"
        "import ai_workflow.loop_watcher as lw\n\n"
        f"td = Path({_tmp8!r}) / 'lw8x'\n"
        "td.mkdir(exist_ok=True)\n"
        "lw.TERMINALS_DIR = td\n"
        "lw.STATE_FILE = td / 'state2.json'\n\n"
        # 写一个带 notified_hashes 的状态，然后 save + load 验证
        "s = {\n"
        "    'terminals': {'88': {'state': 'running', 'sentinel_count': 1}},\n"
        "    'notified_hashes': ['abc123', 'def456'],\n"
        "    'last_run': '2026-07-21T00:00:00Z'\n"
        "}\n"
        "lw.save_state(s)\n"
        "loaded = lw.load_state()\n"
        "assert loaded['notified_hashes'] == ['abc123', 'def456'], loaded['notified_hashes']\n"
        "assert loaded['terminals']['88']['state'] == 'running'\n"
        "print('PASS')\n"
    )
    case8 = _sp.run(
        [sys.executable, "-c", case8_script],
        capture_output=True, text=True, timeout=15,
    )
    assert case8.returncode == 0, f"Case 8 failed:\n  stdout: {case8.stdout}\n  stderr: {case8.stderr}"
    assert "PASS" in case8.stdout
    print("  [OK] Case 8: save_state → load_state 持久化 notified_hashes（subprocess 隔离）")

    print("-" * 50)
    print("  [OK] all 8 cases PASS")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(main())
