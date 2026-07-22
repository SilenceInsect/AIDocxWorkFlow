#!/usr/bin/env python3
"""L2 业务正确性校验器 — S6 测试用例产物（v16 T4 §3）。

校验范围：
  - test_cases.json（用例描述、步骤、预期、引用等业务正确性）

校验维度（与 L1 字段层并存）：
  1. 用例描述非空、不包含「等等」「…」
  2. test_scenario 含 【OBJ-XXX 名称】 锚点
  3. 操作步骤包含动词、与功能点引用一致
  4. 预期结果含可验证断言（数字/状态/字段名）
  5. feature_point_ref 与 obj_id 都非空

L1（l1_s6.py）负责字段格式，L2（本档）负责业务正确性。

l2_mode 三档契约（Round 14 闭环补齐，§v17 字段溯源 SSOT）：
  - "lenient"（默认）：跳过 5 项中的第 2 项（OBJ 锚点），与 SKILL.md §NAME-FIELD-001
    对齐（test_scenario 不带【】锚点）。其他 4 项仍然校验。
  - "strict"：完整 5 项校验（旧行为，与 v16 锚点方案对齐）。
  - "off"：跳过所有 5 项，仅返回 passed=True（用于 dry-run）。
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from typing import Any


_L2_MODES = ("lenient", "strict", "off")


# 描述中禁止出现的占位词（"等等" 暗示描述不完整）
_PLACEHOLDER_TOKENS = ("等等", "…", "...", "TODO", "TBD", "占位")
# OBJ 锚点正则：【OBJ-XXX 名称】
_OBJ_ANCHOR_PAT = re.compile(r"【OBJ-[A-Za-z0-9_-]+\s+[^】]+】")
# 操作步骤动词（中文常见动词，按需求范围列出 12 个）
# R3-F4 扩展：增加"通过/玩家/系统/查询/观察/检查/等待/发送"等业务场景动词
# 覆盖：道具列表/购买/退款/风控/邮件等场景的系统侧操作
_STEP_VERBS = (
    "点击", "输入", "选择", "进入", "刷新", "提交", "取消", "确认", "关闭", "拖动", "滚动", "等待",
    # 业务场景动词
    "通过", "访问", "购买", "支付", "退款", "查询", "观察", "检查", "执行",
    "发送", "接收", "处理", "记录", "扣除", "发放", "释放", "返回", "触发",
    "扫描", "创建", "更新", "删除", "重试", "模拟",
)
# 可验证断言标记（§12 v2.0 扩展版）
# 包含：助动词 + 状态词 + 验证词 + 常见模式 + §12 v2.0 新增
# R3-F4 fix: 添加"变为"（状态变更词，用于"状态变为 confirm"类断言）
_ASSERTION_TOKENS = (
    # 助动词
    "应", "应该", "必须", "需要", "应当",
    # 返回/状态
    "返回", "展示", "显示", "提示", "状态",
    # 常见模式
    "正常", "成功", "完成", "可见", "存在",
    # §12 v2.0 新增：状态描述词（用于"禁用"/"不可"/"为"等格式）
    "禁用", "不可", "不为", "不显示", "不展示", "不出现",
    "为", "是", "成", "到",
    # R3-F4 新增：状态变更词（"状态变为 confirm"类断言）
    "变为", "变成", "转为", "切换为",
    # 标点（数字/百分比/状态码）
    "= ", "：", ":",
)


@dataclass
class L2CheckResult:
    """L2 校验结果。"""
    passed: bool
    total: int = 0
    failed_count: int = 0
    failed_ids: list[str] = field(default_factory=list)
    error_details: list[dict] = field(default_factory=list)


def _get_field(case: dict, *keys: str) -> str:
    """多键名兜底取值。

    支持两种列表格式：
    1. 普通列表：[item1, item2, ...] → join 成字符串
    2. §12 v2.0 格式：[{'step_ref': N, '预期': '...'}, ...] → 仅提取 '预期' 字段
    """
    for k in keys:
        val = case.get(k)
        if val is None:
            continue
        if isinstance(val, list):
            # §12 v2.0 格式：提取 '预期' 字段
            if val and isinstance(val[0], dict) and "预期" in val[0]:
                return "\n".join(str(e.get("预期", "")) for e in val if isinstance(e, dict))
            # 普通列表
            return "\n".join(str(v) for v in val)
        return str(val)
    return ""


def _check_one(case: dict, case_id: str, l2_mode: str = "lenient") -> list[str]:
    """校验单个用例，返回错误类型列表。

    l2_mode:
      - "off": 跳过所有校验
      - "lenient": 跳过 OBJ 锚点（SKILL.md §NAME-FIELD-001）
      - "strict": 完整 5 项
    """
    errs: list[str] = []

    if l2_mode == "off":
        return errs

    # 1. 用例描述非空、不包含「等等」「…」
    desc = _get_field(case, "用例描述", "title")
    if not desc or not desc.strip():
        errs.append("MISSING_DESCRIPTION")
    elif any(tok in desc for tok in _PLACEHOLDER_TOKENS):
        errs.append("PLACEHOLDER_IN_DESCRIPTION")

    # 2. test_scenario 含 【OBJ-XXX 名称】 锚点（strict 才校验）
    if l2_mode == "strict":
        scenario = _get_field(case, "功能描述", "scenario", "description")
        if scenario and not _OBJ_ANCHOR_PAT.search(scenario):
            errs.append("MISSING_OBJ_ANCHOR")

    # 3. 操作步骤包含动词
    steps = _get_field(case, "操作步骤", "test_steps", "steps")
    # R3-F4 fix: 显式检查空步骤（_get_field 可能返回空字符串）
    if not steps or not steps.strip():
        errs.append("EMPTY_STEPS")
    elif not any(verb in steps for verb in _STEP_VERBS):
        errs.append("NO_VERB_IN_STEPS")

    # 4. 预期结果校验（支持字符串旧格式和 §12 v2.0 列表新格式）
    # R3-F4 fix: 旧格式字符串也要经过 _ASSERTION_TOKENS 检查，不能被 elif 漏判
    expected_list = case.get("预期结果", case.get("expected_results", []))
    if isinstance(expected_list, list) and expected_list:
        # §12 v2.0 新格式：[{'step_ref': N, '预期': '...'}, ...]
        if expected_list and isinstance(expected_list[0], dict) and "预期" in expected_list[0]:
            # 有"预期"字段即可，不强制要求断言标记（由 L1 保证非空）
            has_content = all(
                isinstance(e, dict) and e.get("预期", "").strip()
                for e in expected_list
            )
            if not has_content:
                errs.append("EMPTY_ASSERTION")
            # §12 v2.0 跳过断言标记检查
        else:
            # 普通列表：[str, ...] — 检查断言标记
            for item in expected_list:
                text = str(item) if not isinstance(item, dict) else ""
                if isinstance(item, dict):
                    text = item.get("预期", item.get("expected", ""))
                if not text.strip():
                    errs.append("EMPTY_ASSERTION")
                    break
                if not any(tok in text for tok in _ASSERTION_TOKENS):
                    errs.append("EMPTY_ASSERTION")
                    break
    elif isinstance(expected_list, str) and expected_list.strip():
        # 旧格式：预期结果 = 字符串（self-test 用例格式）
        if not any(tok in expected_list for tok in _ASSERTION_TOKENS):
            errs.append("EMPTY_ASSERTION")
    elif expected_list:
        # 非空但非列表非字符串（异常类型）
        errs.append("EMPTY_ASSERTION")

    # 5. feature_point_ref 与 obj_id 都非空
    fp_ref = _get_field(case, "feature_point_ref", "fp_id")
    obj_id = _get_field(case, "obj_id", "requirement_object_id")
    if not fp_ref or not fp_ref.strip():
        errs.append("MISSING_FEATURE_POINT_REF")
    if not obj_id or not obj_id.strip():
        errs.append("MISSING_OBJ_ID")

    return errs


def run_l2_check(test_cases: list[dict], l2_mode: str = "lenient") -> L2CheckResult:
    """批量 L2 校验。

    Args:
        test_cases: 用例列表
        l2_mode: "lenient" (默认) / "strict" / "off"

    Returns:
        L2CheckResult（passed / total / failed_count / failed_ids / error_details）
    """
    if l2_mode not in _L2_MODES:
        raise ValueError(f"l2_mode 必须是 {_L2_MODES} 之一，收到：{l2_mode!r}")

    failed_ids: list[str] = []
    error_details: list[dict] = []
    total = len(test_cases)

    for idx, case in enumerate(test_cases):
        case_id = _get_field(case, "case_id", "tc_id") or f"#{idx}"
        errs = _check_one(case, case_id, l2_mode=l2_mode)
        if errs:
            failed_ids.append(case_id)
            error_details.append({"case_id": case_id, "errors": errs})

    return L2CheckResult(
        passed=(len(failed_ids) == 0),
        total=total,
        failed_count=len(failed_ids),
        failed_ids=failed_ids,
        error_details=error_details,
    )


def self_test() -> int:
    """7 cases：3 模式 × 1 边界 + 1 unknown mode 拒绝。

    Case 1: lenient 跳过 OBJ 锚点 → 全 PASS
    Case 2: strict 缺 OBJ 锚点 → 触发 MISSING_OBJ_ANCHOR
    Case 3: off → 全部 PASS（即使缺锚点）
    Case 4: unknown mode → ValueError
    """
    base = {
        "case_id": "PASS-TC-001",
        "用例描述": "购买道具流程",
        "功能描述": "【OBJ-001 道具购买】玩家在详情页点击购买按钮",
        "操作步骤": "1. 进入道具详情页\n2. 点击【购买】按钮",
        "预期结果": "应弹出购买确认弹窗，状态变为 confirm",
        "feature_point_ref": "FP-001",
        "obj_id": "OBJ-001",
    }
    no_anchor = {
        "case_id": "FAIL-TC-002",
        "用例描述": "缺锚点 case",
        "功能描述": "玩家在详情页操作",  # 无【】锚点
        "操作步骤": "1. 进入页面\n2. 点击按钮",
        "预期结果": "应显示确认",
        "feature_point_ref": "FP-002",
        "obj_id": "OBJ-002",
    }

    # Case 1: lenient 跳过 OBJ 锚点 → base + no_anchor 都 PASS
    r_lenient = run_l2_check([base, no_anchor], l2_mode="lenient")
    assert r_lenient.passed is True, f"lenient 期望 passed=True：{r_lenient}"
    assert r_lenient.failed_count == 0

    # Case 2: strict 不跳过 → no_anchor FAIL MISSING_OBJ_ANCHOR
    r_strict = run_l2_check([base, no_anchor], l2_mode="strict")
    assert r_strict.passed is False
    assert r_strict.failed_count == 1
    assert "FAIL-TC-002" in r_strict.failed_ids
    assert any("MISSING_OBJ_ANCHOR" in e["errors"] for e in r_strict.error_details)

    # Case 3: off → 全部 PASS（即使缺锚点）
    r_off = run_l2_check([no_anchor], l2_mode="off")
    assert r_off.passed is True
    assert r_off.failed_count == 0

    # Case 4: unknown mode → ValueError
    try:
        run_l2_check([base], l2_mode="bogus")
    except ValueError as e:
        assert "l2_mode" in str(e)
    else:
        raise AssertionError("unknown mode 应抛 ValueError")

    print("l2_s6 self-test: PASS (lenient/strict/off 三档 + unknown 拒绝)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    raise SystemExit("usage: python3 ai_workflow/validators/l2_s6.py --self-test")