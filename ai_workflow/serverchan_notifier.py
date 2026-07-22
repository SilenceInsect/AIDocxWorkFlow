#!/usr/bin/env python3
"""Server 酱 Notifier (v1 · Plan: serverchan_pivot_20260719)

A 通道：通过 Server 酱 v3 Webhook 向指定 SendKey 推送 markdown 格式通知。
定位：goal-loop 状态收敛/阻塞通知。取代 v1 的 C 通道（macOS AppleScript）。

接口设计：
  - 与 wechat_notifier.py 同构：load_config / build_message / send_to_wechat
  - 业务函数签名改为 send_via_webhook 以反映实际通道
  - 任何异常 → (False, str) 不抛错（hook 不能崩）
  - 含 def self_test() + --self-test argv（self-test 豁免条件 1+2）

dry_run 语义：
  - config.default_dry_run 字段（默认 false，按你确认）
  - 环境变量 SERVERCHAN_DRY_RUN=true 强制覆盖（兜底防呆）
  - send_via_webhook 的 dry_run 参数最优先

隐私：
  - send_key 落在 .cursor/private/serverchan_config.json
  - 该目录已被 .cursor/private/.gitignore（含 *.json）强制隔离
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PRIVATE_DIR = REPO_ROOT / ".cursor" / "private"
DEFAULT_CONFIG_PATH = PRIVATE_DIR / "serverchan_config.json"

# 通知触发的状态集合（与 config.notify_states 字段同步）
# v1 Plan: serverchan_pivot_20260719
# v2 修订：REPAIRING 加入通知（goal-loop 轮次迭代完成时的状态）
DEFAULT_NOTIFY_STATES = frozenset({
    "achieved",
    "converged_with_followup",
    "blocked",
    "REPAIRING",
})

# 状态映射为中文显示
STATUS_ZH = {
    "achieved": "已完成（achieved）",
    "converged_with_followup": "基本收敛（converged_with_followup）",
    "blocked": "已阻塞（blocked）",
    "active": "运行中（active）",
    "paused": "已暂停（paused）",
    "REPAIRING": "轮次迭代中（REPAIRING）",
    "budget-limited": "预算受限（budget-limited）",
}

# 环境变量：true/1 强制走 dry_run（兜底防误发）
_DRY_RUN_ENV = "SERVERCHAN_DRY_RUN"


# ===== 异常类型 =====


class ServerChanNotifierError(Exception):
    """通知器通用错误。"""


class ConfigNotFoundError(ServerChanNotifierError):
    """配置文件不存在。"""


class ConfigInvalidError(ServerChanNotifierError):
    """配置文件格式不合法。"""


class SendKeyMissingError(ServerChanNotifierError):
    """SendKey 缺失。"""


class WebhookFailedError(ServerChanNotifierError):
    """webhook 调用失败。"""


class MessageTooLongError(ServerChanNotifierError):
    """消息超过配置上限。"""


# ===== 配置加载 =====


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """加载 serverchan_config.json。

    Raises:
        ConfigNotFoundError: 文件不存在。
        ConfigInvalidError: JSON 解析失败或必填字段缺失。
    """
    cp = config_path or DEFAULT_CONFIG_PATH
    if not cp.exists():
        raise ConfigNotFoundError(f"配置文件不存在: {cp}")
    try:
        data = json.loads(cp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigInvalidError(f"JSON 解析失败: {e}") from e
    if not isinstance(data, dict):
        raise ConfigInvalidError("config root must be dict")
    for required in ("send_key",):
        if not data.get(required):
            raise ConfigInvalidError(f"必填字段缺失或为空: {required}")
    return data


def _env_dry_run() -> bool:
    """环境变量强制 dry_run（兜底防误发）。"""
    val = os.environ.get(_DRY_RUN_ENV, "").strip().lower()
    return val in ("true", "1", "yes", "on")


def resolve_dry_run(config: dict[str, Any], explicit: bool | None = None) -> bool:
    """三层 dry_run 决策：explicit > env > config.default_dry_run。

    Args:
        config: 已加载的 config 字典
        explicit: 调用方传入的 explicit 参数；None 表示不显式指定

    Returns:
        最终 dry_run 取值
    """
    if explicit is not None:
        return explicit
    if _env_dry_run():
        return True
    return bool(config.get("default_dry_run", False))


# ===== 消息构造 =====


def build_message(
    status: str,
    raw_user_goal: str,
    loop_round: int,
    latest_artifact: str | None,
    max_length: int = 240,
) -> str:
    """构造标准通知消息（仅摘要，与 wechat_notifier 同格式便于迁移）。

    格式：
      [Goal-Loop 通知] {status_zh}
      目标: {goal[:60]}...
      轮次: round={N}
      产物: {artifact or (无)}
      ts: {ISO}
    """
    status_zh = STATUS_ZH.get(status, status)
    goal_short = (raw_user_goal or "(空)").strip()
    if len(goal_short) > 60:
        goal_short = goal_short[:57] + "..."
    artifact = latest_artifact or "(无)"
    ts = datetime.now(timezone.utc).isoformat()
    lines = [
        f"[Goal-Loop 通知] {status_zh}",
        f"目标: {goal_short}",
        f"轮次: round={loop_round}",
        f"产物: {artifact}",
        f"ts: {ts}",
    ]
    msg = "\n".join(lines)
    if len(msg) > max_length:
        msg = msg[: max_length - 3] + "..."
    return msg


def build_markdown_desp(message: str) -> str:
    """把单行消息包装成 SCT markdown 代码块（显示美观）。"""
    return f"```\n{message}\n```"


# ===== Webhook 发送 =====


def _resolve_endpoint(cfg: dict[str, Any]) -> str:
    """解析 SCT endpoint（支持占位符替换）。"""
    send_key = cfg.get("send_key", "")
    endpoint_template = cfg.get(
        "endpoint", "https://sctapi.ftqq.com/{send_key}.send"
    )
    return endpoint_template.replace("{send_key}", send_key)


def send_via_webhook(
    message: str,
    config_path: Path | None = None,
    dry_run: bool | None = None,
    title: str = "Goal-Loop 通知",
) -> tuple[bool, str]:
    """通过 Server 酱 v3 webhook 推送一条通知。

    Args:
        message: 完整消息文本（已构造好的摘要）
        config_path: 自定义配置路径（默认 .cursor/private/serverchan_config.json）
        dry_run: True=只构造 POST 体不发；False=真发；None=按 env+config 决策
        title: SCT 的 title 字段（短标题，列表显示用）

    Returns:
        (ok, detail) — ok=True 表示 SCT HTTP 200 且返回码成功；detail 是 SCT 响应或错误
    """
    try:
        cfg = load_config(config_path)
    except (ConfigNotFoundError, ConfigInvalidError) as e:
        return False, f"config_error: {e}"

    send_key = cfg.get("send_key", "")
    if not send_key:
        return False, "send_key_missing: config 缺 send_key"

    endpoint = _resolve_endpoint(cfg)
    timeout_s = float(cfg.get("http_timeout_seconds", 8))
    is_dry = resolve_dry_run(cfg, dry_run)

    # POST body (form-urlencoded)
    body_dict = {
        "title": title,
        "desp": build_markdown_desp(message),
    }
    body = urllib.parse.urlencode(body_dict).encode("utf-8")

    # dry_run 分支
    if is_dry:
        return (
            True,
            f"dry_run_ok endpoint={endpoint} title={title!r} body_len={len(body)}",
        )

    # HTTP POST
    try:
        req = urllib.request.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status_code = resp.status

        # SCT v3 返回 JSON: {"code": 0, "message": "..."} 表示成功
        try:
            payload = json.loads(raw)
            code = payload.get("code")
            msg_text = payload.get("message", "")
        except json.JSONDecodeError:
            payload = None
            code = None
            msg_text = raw[:200]

        if status_code == 200 and code in (0, 200):
            return True, f"ok http={status_code} code={code} msg={msg_text!r}"

        return False, (
            f"sct_rejected http={status_code} code={code} body={msg_text!r}"
        )

    except urllib.error.HTTPError as e:
        return False, f"http_error: {e.code} {e.reason}"
    except urllib.error.URLError as e:
        return False, f"url_error: {e.reason}"
    except TimeoutError:
        return False, f"timeout({timeout_s}s)"
    except Exception as e:
        return False, f"unexpected: {type(e).__name__}: {e}"


def notify_with_message(message: str, config_path: Path | None = None) -> tuple[bool, str]:
    """便捷封装：send_via_webhook 的语义化别名（保持与 wechat_notifier 同名 API）。"""
    return send_via_webhook(message, config_path=config_path)


# ===== self_test（豁免条款 1+2）=====


def self_test() -> int:
    """python3 ai_workflow/serverchan_notifier.py --self-test

    覆盖 12 个用例（不依赖网络，全部本地）：
      1.  ConfigNotFoundError（不存在的路径）
      2.  ConfigInvalidError（坏 JSON）
      3.  ConfigInvalidError（缺 send_key）
      4.  resolve_dry_run 三层决策（explicit / env / config）
      5.  build_markdown_desp 包裹格式正确
      6.  build_message 超长截断（240 chars）
      7.  build_message 3 个 notify_states 中文全部命中
      8.  _resolve_endpoint 占位符替换正确
      9.  send_via_webhook dry_run 不发网络（pure dry_run）
     10.  send_via_webhook 缺 send_key → (False, send_key_missing...)
     11.  STATUS_ZH 覆盖主通知状态枚举
     12.  send_via_webhook dry_run_ok 输出含 endpoint/title/body_len
    """
    import sys as _sys
    import tempfile

    # self_test 直接 python3 file.py 跑，ai_workflow 不在 sys.path
    _pkg_root = Path(__file__).resolve().parent.parent
    if str(_pkg_root) not in _sys.path:
        _sys.path.insert(0, str(_pkg_root))

    print("ServerChanNotifier self_test（12 cases）")
    print("-" * 50)

    # 用 sys.modules[__name__] 拿自己（而不是 import ai_workflow.xxx）
    mod = _sys.modules[__name__] 

    # Case 1: 不存在路径
    try:
        load_config(Path("/tmp/__no_such_file__.json"))
        assert False, "应抛 ConfigNotFoundError"
    except ConfigNotFoundError as e:
        assert "不存在" in str(e), f"msg 应含『不存在』: {e}"
        print("  [OK] Case 1: 不存在路径 → ConfigNotFoundError")

    # Case 2: 坏 JSON
    with tempfile.NamedTemporaryFile(
        suffix=".json", mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write("{ not valid json")
        bad_path = Path(f.name)
    try:
        try:
            load_config(bad_path)
            assert False, "应抛 ConfigInvalidError"
        except ConfigInvalidError as e:
            assert "JSON" in str(e), f"msg 应含『JSON』: {e}"
            print("  [OK] Case 2: 坏 JSON → ConfigInvalidError（JSON 解析失败）")
    finally:
        bad_path.unlink(missing_ok=True)

    # Case 3: 缺 send_key
    with tempfile.NamedTemporaryFile(
        suffix=".json", mode="w", delete=False, encoding="utf-8"
    ) as f:
        json.dump({"endpoint": "https://example.com"}, f, ensure_ascii=False)
        no_key = Path(f.name)
    try:
        try:
            load_config(no_key)
            assert False, "应抛 ConfigInvalidError"
        except ConfigInvalidError as e:
            assert "send_key" in str(e), f"msg 应含『send_key』: {e}"
            print("  [OK] Case 3: 缺 send_key → ConfigInvalidError（必填字段缺失）")
    finally:
        no_key.unlink(missing_ok=True)

    # Case 4: resolve_dry_run 三层决策
    # 显式 explicit
    assert resolve_dry_run({"default_dry_run": False}, explicit=True) is True
    assert resolve_dry_run({"default_dry_run": True}, explicit=False) is False
    # env 兜底
    os.environ[_DRY_RUN_ENV] = "true"
    try:
        assert resolve_dry_run({"default_dry_run": False}, explicit=None) is True
        assert resolve_dry_run({"default_dry_run": True}, explicit=None) is True
    finally:
        os.environ.pop(_DRY_RUN_ENV, None)
    # config fallback
    assert resolve_dry_run({"default_dry_run": False}, explicit=None) is False
    assert resolve_dry_run({"default_dry_run": True}, explicit=None) is True
    print("  [OK] Case 4: resolve_dry_run 三层决策（explicit > env > config）")

    # Case 5: markdown 包裹
    body = build_markdown_desp("hello world")
    assert body == "```\nhello world\n```", f"格式错: {body!r}"
    print("  [OK] Case 5: build_markdown_desp 包裹格式正确")

    # Case 6: 消息截断
    long_goal = "测试" * 200
    msg = build_message(
        "achieved",
        long_goal,
        5,
        "/some/very/long/artifact/path/" + "x" * 200,
        max_length=240,
    )
    assert len(msg) <= 240, f"msg 长 {len(msg)} 应 ≤ 240"
    assert msg.endswith("..."), "截断后应含 ..."
    print(f"  [OK] Case 6: build_message 超长截断（{len(msg)} chars）")

    # Case 7: status 中文显示
    for s in ("achieved", "converged_with_followup", "blocked"):
        m = build_message(s, "目标X", 1, "/art.md", max_length=400)
        zh_phrase = {"achieved": "已完成", "converged_with_followup": "基本收敛", "blocked": "已阻塞"}[s]
        assert zh_phrase in m, f"status={s} 中文『{zh_phrase}』应在消息内: {m}"
    print("  [OK] Case 7: 3 个 notify_states 中文短语全部命中")

    # Case 8: endpoint 替换
    cfg_template = {
        "send_key": "ABC123",
        "endpoint": "https://sctapi.ftqq.com/{send_key}.send",
    }
    assert _resolve_endpoint(cfg_template) == "https://sctapi.ftqq.com/ABC123.send"
    cfg_default = {"send_key": "XYZ"}
    assert (
        _resolve_endpoint(cfg_default)
        == "https://sctapi.ftqq.com/XYZ.send"
    )
    print("  [OK] Case 8: _resolve_endpoint 占位符替换正确")

    # Case 9: dry_run 不发网络
    with tempfile.NamedTemporaryFile(
        suffix=".json", mode="w", delete=False, encoding="utf-8"
    ) as f:
        json.dump(
            {"send_key": "FAKE_KEY_FOR_TEST", "default_dry_run": False},
            f,
            ensure_ascii=False,
        )
        good_cfg = Path(f.name)
    try:
        # dry_run=True 显式
        ok, detail = send_via_webhook(
            "hello", config_path=good_cfg, dry_run=True
        )
        assert ok, f"dry_run 应成功: {detail}"
        assert "dry_run_ok" in detail, f"detail 应含 dry_run_ok: {detail}"
        assert "FAKE_KEY_FOR_TEST" in detail, "dry_run detail 应含 send_key（脱敏前）"
        assert "endpoint=https" in detail, "detail 应含 endpoint"
        print(f"  [OK] Case 9: dry_run=True 显式 → 不发网络（{detail}）")
    finally:
        good_cfg.unlink(missing_ok=True)

    # Case 10: 缺 send_key → send_key_missing（容错）
    with tempfile.NamedTemporaryFile(
        suffix=".json", mode="w", delete=False, encoding="utf-8"
    ) as f:
        # 绕过 load_config 的必填校验，让 send_key 为空但能 load
        json.dump({"send_key": "", "endpoint": "https://x"}, f, ensure_ascii=False)
        # 注意 load_config 会对空 send_key 抛 ConfigInvalidError；这里直接测 send_via_webhook
        # 的 send_key 分支需要绕过 load_config，改为测分支逻辑
        # 改用 monkeypatch load_config
        pass
    # 用 monkeypatch：临时让 load_config 返回一个空 send_key 的 cfg
    orig_load = load_config
    mod.load_config = lambda path=None: {"send_key": "", "endpoint": "https://x"}  # type: ignore
    try:
        ok, detail = send_via_webhook("hi")
        assert ok is False, f"缺 send_key 应 ok=False: {ok}"
        assert "send_key_missing" in detail, f"detail 应含 send_key_missing: {detail}"
        print(f"  [OK] Case 10: 缺 send_key → (False, send_key_missing…)")
    finally:
        mod.load_config = orig_load  # type: ignore

    # Case 11: STATUS_ZH 一致性
    for s in DEFAULT_NOTIFY_STATES:
        assert s in STATUS_ZH, f"STATUS_ZH 缺 {s}"
    print(f"  [OK] Case 11: STATUS_ZH 覆盖所有 notify_states (={sorted(DEFAULT_NOTIFY_STATES)})")

    # Case 12: dry_run body_len 一致
    with tempfile.NamedTemporaryFile(
        suffix=".json", mode="w", delete=False, encoding="utf-8"
    ) as f:
        json.dump({"send_key": "SCT_TEST", "default_dry_run": True}, f, ensure_ascii=False)
        cfg_dry = Path(f.name)
    try:
        ok, detail = send_via_webhook(
            "test message body", config_path=cfg_dry, dry_run=None
        )
        assert ok and "dry_run_ok" in detail
        assert "body_len=" in detail
        print(f"  [OK] Case 12: dry_run body_len 字段正确（{detail}）")
    finally:
        cfg_dry.unlink(missing_ok=True)

    print("-" * 50)
    print("  [OK] all 12 cases PASS")
    return 0


# ===== CLI 入口 =====


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return self_test()
    if "--dry-run" in argv:
        message = " ".join(a for a in argv if a != "--dry-run") or "(empty message)"
        ok, detail = send_via_webhook(message, dry_run=True)
        print(f"dry_run ok={ok} detail={detail}")
        return 0 if ok else 1
    print("用法:")
    print("  python3 ai_workflow/serverchan_notifier.py --self-test")
    print('  python3 ai_workflow/serverchan_notifier.py --dry-run "测试消息"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
