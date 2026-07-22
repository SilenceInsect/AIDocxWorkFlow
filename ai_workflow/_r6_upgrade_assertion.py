#!/usr/bin/env python3
"""T12 — Upgrade S6 TC assertion fields to domain-specific assertions.

Round 6 Act phase: S-002 fix — upgrade all assertion fields from
generic placeholder (string_contains + "成功"/"EXCEPTION") to module-aware
domain-specific assertions.

Assertion templates by module:
  UI:  element_visible | text_equals | button_enabled | element_hidden
  BIZ: order_status_equals | balance_decreased_by | vip_discount_applied
       promotion_applied | item_delivered | refund_completed
  LOG: log_level_equals | log_format_valid | log_entry_count
  SPECIAL: risk_action_equals | limit_check_equals | captcha_triggered
"""

from __future__ import annotations
import json, re, sys
from pathlib import Path
from typing import Any

TC_FILE = "workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json"

# ── Domain-specific assertion templates ──────────────────────────────────────

UI_KEYWORDS_ORDER_STATUS = ["待支付", "已支付", "已完成", "已取消", "已退款"]
UI_KEYWORDS_BUTTON = ["购买", "支付", "确认", "取消", "退款", "下单", "提交"]
UI_KEYWORDS_ELEMENT = ["展示", "显示", "可见", "隐藏", "空态", "标签", "图标", "数量"]

BIZ_KEYWORDS_ORDER = ["订单", "状态"]
BIZ_KEYWORDS_BALANCE = ["余额", "游戏币", "扣减", "扣除", "扣款", "余额不足"]
BIZ_KEYWORDS_VIP = ["VIP", "折扣", "vip", "会员"]
BIZ_KEYWORDS_PROMO = ["促销", "优惠", "折扣", "满减", "最优"]
BIZ_KEYWORDS_ITEM = ["道具", "到账", "发货", "发放", "库存"]
BIZ_KEYWORDS_REFUND = ["退款", "退换"]

LOG_KEYWORDS = ["日志", "记录", "操作日志", "audit", "log"]
SPECIAL_KEYWORDS_RISK = ["风控", "拦截", "拒绝", "封禁", "验证码", "限额", "超限"]
SPECIAL_KEYWORDS_LIMIT = ["单笔", "日累计", "日限额", "频率", "封禁"]


def _keyword_match(text: str, keywords: list[str]) -> bool:
    text_l = text.lower()
    return any(kw.lower() in text_l for kw in keywords)


def _extract_expected_value(text: str, module: str, test_type: str) -> str | None:
    """Derive expected_value from test_scenario free text."""
    if module == "UI":
        # Try to extract status from text
        for status in ["待支付", "已支付", "已完成", "已取消", "已退款"]:
            if status in text:
                return status
    elif module == "BIZ":
        for status in ["待支付", "已支付", "已完成", "已取消", "已退款"]:
            if status in text:
                return status
    elif module == "SPECIAL":
        if _keyword_match(text, ["拒绝", "拦截", "BLOCK"]):
            return "BLOCK"
        if _keyword_match(text, ["放行", "通过", "PASS", "允许"]):
            return "PASS"
        if _keyword_match(text, ["告警", "ALERT", "验证码"]):
            return "ALERT"
    return None


def build_assertion(tc: dict, module: str, test_type: str) -> list[dict]:
    """Build domain-specific assertion list for one TC."""

    scenario = tc.get("test_scenario", "")
    func_desc = tc.get("功能描述", "")
    combined = f"{scenario} {func_desc}"

    assertions: list[dict] = []

    if module == "UI":
        if _keyword_match(combined, UI_KEYWORDS_BUTTON):
            # Detect which button and expected state
            if _keyword_match(combined, ["禁用", "不可点", "灰态"]):
                assertions.append({"assertion_type": "button_disabled", "assertion_target": "ui", "expected_value": "购买按钮"})
            elif _keyword_match(combined, ["可用", "可点", "正常"]):
                assertions.append({"assertion_type": "button_enabled", "assertion_target": "ui", "expected_value": "购买按钮"})
        if _keyword_match(combined, ["空态", "无结果", "空列表"]):
            assertions.append({"assertion_type": "element_visible", "assertion_target": "ui", "expected_value": "空态提示"})
        if _keyword_match(combined, ["折扣", "促销", "优惠"]):
            assertions.append({"assertion_type": "text_equals", "assertion_target": "ui", "expected_value": "促销标签"})
        if _keyword_match(combined, ["隐藏", "不可见", "不可操作"]):
            assertions.append({"assertion_type": "element_hidden", "assertion_target": "ui", "expected_value": "VIP专区入口"})
        if _keyword_match(combined, ["道具", "列表", "展示"]):
            assertions.append({"assertion_type": "element_visible", "assertion_target": "ui", "expected_value": "道具卡片"})
        if _keyword_match(combined, ["数量", "边界", "超限"]):
            assertions.append({"assertion_type": "text_equals", "assertion_target": "ui", "expected_value": "数量选择器"})

        # Fallback
        if not assertions:
            assertions.append({"assertion_type": "element_visible", "assertion_target": "ui", "expected_value": "页面主元素"})

    elif module == "BIZ":
        if _keyword_match(combined, BIZ_KEYWORDS_ORDER):
            expected_status = _extract_expected_value(combined, module, test_type)
            if not expected_status:
                if _keyword_match(combined, ["创建", "下单", "确认"]):
                    expected_status = "待支付"
                elif _keyword_match(combined, ["完成", "成功"]):
                    expected_status = "已完成"
                elif _keyword_match(combined, ["超时"]):
                    expected_status = "已超时"
                elif _keyword_match(combined, ["退款"]):
                    expected_status = "已退款"
            assertions.append({
                "assertion_type": "order_status_equals",
                "assertion_target": "database",
                "expected_value": expected_status or "待支付"
            })
        if _keyword_match(combined, BIZ_KEYWORDS_BALANCE):
            assertions.append({"assertion_type": "balance_decreased_by", "assertion_target": "database", "expected_value": ">=0"})
        if _keyword_match(combined, BIZ_KEYWORDS_VIP):
            vip_match = re.search(r'(\d+)%?折扣?', combined)
            pct = vip_match.group(1) + "%" if vip_match else "VIP折扣"
            assertions.append({"assertion_type": "vip_discount_applied", "assertion_target": "response", "expected_value": pct})
        if _keyword_match(combined, BIZ_KEYWORDS_PROMO):
            assertions.append({"assertion_type": "promotion_applied", "assertion_target": "response", "expected_value": "最优价格"})
        if _keyword_match(combined, BIZ_KEYWORDS_ITEM):
            assertions.append({"assertion_type": "item_delivered", "assertion_target": "database", "expected_value": "1秒内到账"})
        if _keyword_match(combined, BIZ_KEYWORDS_REFUND):
            assertions.append({"assertion_type": "refund_completed", "assertion_target": "database", "expected_value": "已退款"})

        # Fallback for BIZ
        if not assertions:
            if "EXCEPTION" in combined or "异常" in combined:
                assertions.append({"assertion_type": "error_handled", "assertion_target": "system", "expected_value": "容错正确"})
            else:
                assertions.append({"assertion_type": "order_status_equals", "assertion_target": "database", "expected_value": "已完成"})

    elif module == "LOG":
        if _keyword_match(combined, ["失败", "异常", "error", "错误"]):
            assertions.append({"assertion_type": "log_level_equals", "assertion_target": "log", "expected_value": "ERROR"})
        elif _keyword_match(combined, ["警告", "warn", "告警"]):
            assertions.append({"assertion_type": "log_level_equals", "assertion_target": "log", "expected_value": "WARN"})
        else:
            assertions.append({"assertion_type": "log_level_equals", "assertion_target": "log", "expected_value": "INFO"})
        assertions.append({"assertion_type": "log_format_valid", "assertion_target": "log", "expected_value": "true"})

    elif module == "SPECIAL":
        if _keyword_match(combined, ["拒绝", "拦截", "封禁", "BLOCK"]):
            assertions.append({"assertion_type": "risk_action_equals", "assertion_target": "risk_system", "expected_value": "BLOCK"})
        elif _keyword_match(combined, ["验证码", "captcha", "ALERT"]):
            assertions.append({"assertion_type": "risk_action_equals", "assertion_target": "risk_system", "expected_value": "ALERT"})
        else:
            assertions.append({"assertion_type": "risk_action_equals", "assertion_target": "risk_system", "expected_value": "PASS"})
        if _keyword_match(combined, ["单笔", "日累计", "限额", "上限"]):
            limit_match = re.search(r'(\d+)', combined)
            assertions.append({
                "assertion_type": "limit_check_equals",
                "assertion_target": "risk_system",
                "expected_value": f"limit_{limit_match.group(1)}" if limit_match else "limit_checked"
            })

        # Fallback
        if not assertions:
            assertions.append({"assertion_type": "risk_action_equals", "assertion_target": "risk_system", "expected_value": "PASS"})

    else:
        # Unknown module — keep generic but upgrade target
        assertions.append({"assertion_type": "response_valid", "assertion_target": "system", "expected_value": "success"})

    return assertions


def main() -> int:
    with open(TC_FILE, encoding="utf-8") as f:
        data = json.load(f)

    cases: list[dict] = data.get("test_cases", [])
    by_module: dict[str, list[dict]] = {}

    for tc in cases:
        module = tc.get("module", "BIZ")
        by_module.setdefault(module, []).append(tc)

    stats: dict[str, dict] = {}
    generic_count = 0
    upgraded_count = 0

    for tc in cases:
        module = tc.get("module", "BIZ")
        test_type = tc.get("test_method", tc.get("test_point_type", ""))
        old_assertion = tc.get("assertion", [])

        # Check if currently generic
        is_generic = (
            len(old_assertion) == 1
            and old_assertion[0].get("assertion_type") == "string_contains"
            and old_assertion[0].get("expected_value") in ("成功", "EXCEPTION", "失败", "容错正确")
        )

        new_assertion = build_assertion(tc, module, test_type)
        tc["assertion"] = new_assertion

        # Track
        stats.setdefault(module, {"generic": 0, "upgraded": 0, "unchanged": 0})
        if is_generic:
            stats[module]["generic"] += 1
            upgraded_count += 1
        else:
            stats[module]["upgraded"] += 1

    # Report
    print("=" * 70)
    print("T12 — S6 Domain Assertion Upgrade Report")
    print("=" * 70)
    print(f"Total TCs processed: {len(cases)}")
    print()

    print("By module:")
    total_generic = 0
    total_upgraded = 0
    for mod in sorted(stats):
        s = stats[mod]
        cnt = len(by_module.get(mod, []))
        print(f"  {mod:10s}  total={cnt:3d}  generic_upgraded={s['generic']:3d}  non_generic={s['upgraded']:3d}")
        total_generic += s['generic']
        total_upgraded += s['upgraded']
    print()
    print(f"  {'TOTAL':10s}  total={len(cases):3d}  generic_upgraded={total_generic:3d}  non_generic={total_upgraded:3d}")

    # Show sample per module
    print()
    print("Sample upgraded assertions by module:")
    for mod in ["UI", "BIZ", "LOG", "SPECIAL"]:
        sample_tcs = by_module.get(mod, [])
        if sample_tcs:
            # Pick one with assertion upgraded from generic
            sample = next((tc for tc in sample_tcs if tc["assertion"][0]["assertion_type"] != "string_contains"), sample_tcs[0])
            print(f"  [{mod}] {sample['case_id']}: {sample['assertion'][:2]}")

    # Save
    out_path = TC_FILE
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print()
    print(f"Saved: {TC_FILE}")

    # Detail report
    report_path = TC_FILE.replace(".json", "_r6_assertion_upgrade.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total": len(cases),
                "generic_upgraded": total_generic,
                "non_generic": total_upgraded,
                "by_module": {mod: stats[mod] for mod in stats}
            }
        }, f, ensure_ascii=False, indent=2)
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
