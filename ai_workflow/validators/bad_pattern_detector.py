#!/usr/bin/env python3
"""Bad pattern detector — 检测 S5/S6 产出中的泛化描述和模板语言。

Bad pattern 分两类：
- GENERIC_DESC: 泛化描述——让人看了不知道在测什么
- TEMPLATE_LANG: 模板语言——Agent 套路化的标志

每个 pattern 含：
  - pattern: 正则或字符串匹配规则
  - severity: BLOCK（阻断）或 WARN（警告）
  - description: 人可读的错误描述
  - suggestion: 修复建议

用法：
  from ai_workflow.validators.bad_pattern_detector import BadPatternDetector
  detector = BadPatternDetector()
  # S5 TP 检测
  for tp in tps:
      errors = detector.check_tp_description(tp.get("description", ""), tp_id=tp.get("tp_id"))
      errors += detector.check_tp_title(tp.get("title", ""), tp_id=tp.get("tp_id"))
  # S6 TC 检测
  for tc in tcs:
      errors += detector.check_tc_steps(tc.get("操作步骤", ""), tc_id=tc.get("case_id"))
      errors += detector.check_tc_expected(tc.get("预期结果", ""), tc_id=tc.get("case_id"))
      errors += detector.check_tc_precondition(tc.get("前置条件", ""), tc_id=tc.get("case_id"))
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

__all__ = ["BadPatternDetector", "BPError"]


# ---------------------------------------------------------------------------
# Pattern 定义
# ---------------------------------------------------------------------------

@dataclass
class BPPattern:
    pattern: str | re.Pattern
    severity: str  # "BLOCK" 或 "WARN"
    description: str
    suggestion: str


# S5 TP bad patterns: description / title / preconditions
TP_DESCRIPTION_PATTERNS: list[BPPattern] = [
    BPPattern(
        pattern=r"验证.*正常",
        severity="BLOCK",
        description="泛化描述「验证XX正常」——无法让人知道在测什么",
        suggestion="改为具体场景：如「余额=500时购买成功，道具到账，余额扣减」",
    ),
    BPPattern(
        pattern=r"系统正常响应",
        severity="BLOCK",
        description="泛化描述「系统正常响应」——没有说清楚预期",
        suggestion="改为具体结果：如「页面展示道具名称+价格+购买按钮」",
    ),
    BPPattern(
        pattern=r"测试.*功能",
        severity="BLOCK",
        description="泛化描述「测试XX功能」——以测试动作开头，不是测试意图",
        suggestion="改为被测对象+预期：如「道具列表按销量降序展示，前10个可见」",
    ),
    BPPattern(
        pattern=r"流程正常",
        severity="BLOCK",
        description="泛化描述「流程正常」——未指明具体流程和验证点",
        suggestion="指明流程+验证点：如「购买流程：选择道具→确认订单→支付成功→道具到账」",
    ),
    BPPattern(
        pattern=r"正常流程",
        severity="BLOCK",
        description="泛化描述「正常流程」——缺少具体步骤描述",
        suggestion="列出具体步骤：如「登录→进入商城→点击道具→确认购买→支付」",
    ),
    BPPattern(
        pattern=r"业务功能正常",
        severity="BLOCK",
        description="泛化描述「业务功能正常」——笼统无具体内容",
        suggestion="拆解为具体验证点：如「道具价格=100金币，可购买，数量正确」",
    ),
    BPPattern(
        pattern=r"功能可用",
        severity="BLOCK",
        description="泛化描述「功能可用」——无具体验证内容",
        suggestion="指明可用性标准：如「点击购买按钮后，3秒内弹出确认弹窗」",
    ),
    BPPattern(
        pattern=r"正常工作",
        severity="BLOCK",
        description="泛化描述「正常工作」——缺少具体场景和预期",
        suggestion="加上具体场景：如「网络正常时，购买成功后道具立即到账」",
    ),
    BPPattern(
        pattern=r"^\s*$",
        severity="BLOCK",
        description="description 为空",
        suggestion="必须填写具体测试描述",
    ),
]

TP_TITLE_PATTERNS: list[BPPattern] = [
    BPPattern(
        pattern=r"^验证",
        severity="BLOCK",
        description="title 以「验证」开头——以测试动作开头，不是场景",
        suggestion="改为场景式：如「余额充足时购买成功」而非「验证购买功能」",
    ),
    BPPattern(
        pattern=r"^测试",
        severity="BLOCK",
        description="title 以「测试」开头——以测试动作开头",
        suggestion="改为被测对象：如「道具列表按销量排序展示」",
    ),
    BPPattern(
        pattern=r"^检查",
        severity="BLOCK",
        description="title 以「检查」开头——以测试动作开头",
        suggestion="改为场景：如「网络断线时购买按钮禁用」",
    ),
]

TP_PRECONDITION_PATTERNS: list[BPPattern] = [
    BPPattern(
        pattern=r"^(无|无特殊|无前置|无要求|无限制)\s*$",
        severity="BLOCK",
        description="前置条件为「无」类占位——业务场景必有前置",
        suggestion="填写具体初始状态：如「玩家已登录，余额=500，道具A可购买」",
    ),
]


# S6 TC bad patterns: 操作步骤 / 预期结果 / 前置条件
TC_STEPS_PATTERNS: list[BPPattern] = [
    BPPattern(
        pattern=r"执行操作",
        severity="BLOCK",
        description="步骤含「执行操作」——模板语言，无具体动作",
        suggestion="改为具体动作：如「点击【购买】按钮」而非「执行操作」",
    ),
    BPPattern(
        pattern=r"执行测试",
        severity="BLOCK",
        description="步骤含「执行测试」——模板语言",
        suggestion="改为具体动作",
    ),
    BPPattern(
        pattern=r"验证预期结果",
        severity="BLOCK",
        description="步骤含「验证预期结果」——模板语言",
        suggestion="改为具体验证：如「观察页面显示，道具A数量=1」",
    ),
    BPPattern(
        pattern=r"验证.*正常",
        severity="BLOCK",
        description="步骤含「验证XX正常」——泛化描述",
        suggestion="改为具体预期：如「弹窗显示购买成功，道具A数量+1」",
    ),
    BPPattern(
        pattern=r"准备符合.*环境",
        severity="BLOCK",
        description="步骤含「准备符合XX的环境」——模板语言",
        suggestion="改为具体状态：如「玩家登录，余额=500，道具A可购买」",
    ),
    BPPattern(
        pattern=r"^\s*$",
        severity="BLOCK",
        description="步骤为空",
        suggestion="必须填写具体操作步骤",
    ),
    BPPattern(
        pattern=r"^1\.\s*输入",
        severity="WARN",
        description="步骤以「1. 输入」开头但无具体字段——可能泛化",
        suggestion="加上具体字段名和值：如「1. 输入购买数量=99」",
    ),
]

TC_EXPECTED_PATTERNS: list[BPPattern] = [
    BPPattern(
        pattern=r"^无$",
        severity="BLOCK",
        description="预期结果为「无」——业务必有具体预期",
        suggestion="填写具体预期：如「弹窗关闭，道具A数量=1，余额=100」",
    ),
    BPPattern(
        pattern=r"^\s*$",
        severity="BLOCK",
        description="预期结果为空",
        suggestion="必须填写具体预期结果",
    ),
    BPPattern(
        pattern=r"系统正常响应",
        severity="BLOCK",
        description="预期含「系统正常响应」——泛化描述",
        suggestion="改为具体结果：如「购买成功弹窗出现，道具到账通知」",
    ),
    BPPattern(
        pattern=r"预期结果正确",
        severity="BLOCK",
        description="预期含「预期结果正确」——循环定义，无实质内容",
        suggestion="改为具体验证点：如「余额扣减正确，道具数量增加」",
    ),
    BPPattern(
        pattern=r"S4[-\w\.]+",
        severity="BLOCK",
        description="预期含 S4 节点编号引用——禁止直接引用 S4",
        suggestion="改为纯业务描述，不含节点编号",
    ),
]

TC_PRECONDITION_PATTERNS: list[BPPattern] = [
    BPPattern(
        pattern=r"^(无|无特殊|无前置|无要求)\s*$",
        severity="BLOCK",
        description="前置条件为「无」类占位——业务场景必有具体前置",
        suggestion="填写具体初始状态：如「玩家已登录，余额=500，游戏币=1000」",
    ),
    BPPattern(
        pattern=r"^\s*$",
        severity="BLOCK",
        description="前置条件为空",
        suggestion="必须填写具体前置条件",
    ),
]


# ---------------------------------------------------------------------------
# 检测结果
# ---------------------------------------------------------------------------

@dataclass
class BPError:
    pattern_type: str       # "GENERIC_DESC" | "TEMPLATE_LANG" | "EMPTY"
    severity: str          # "BLOCK" | "WARN"
    field: str             # "description" | "title" | "操作步骤" | ...
    matched_text: str       # 命中的文本片段
    matched_pattern: str    # 命中的 pattern 描述
    description: str
    suggestion: str
    tp_id: Optional[str] = None
    tc_id: Optional[str] = None


# ---------------------------------------------------------------------------
# 检测器
# ---------------------------------------------------------------------------

class BadPatternDetector:
    """Bad pattern 检测器。

    提供针对 S5 TP 和 S6 TC 各字段的 bad pattern 检测。
    BLOCK 级别直接加入 errors 列表（阻断产出）；
    WARN 级别加入 warnings 列表（不阻断但不鼓励）。
    """

    def __init__(self):
        self._tp_desc_patterns = TP_DESCRIPTION_PATTERNS
        self._tp_title_patterns = TP_TITLE_PATTERNS
        self._tp_precond_patterns = TP_PRECONDITION_PATTERNS
        self._tc_steps_patterns = TC_STEPS_PATTERNS
        self._tc_expected_patterns = TC_EXPECTED_PATTERNS
        self._tc_precond_patterns = TC_PRECONDITION_PATTERNS

    # ------------------------------------------------------------------
    # 私有工具
    # ------------------------------------------------------------------

    def _match(self, text: str, patterns: list[BPPattern]) -> list[BPError]:
        errors = []
        if not text:
            return errors
        for bp in patterns:
            compiled = re.compile(bp.pattern) if isinstance(bp.pattern, str) else bp.pattern
            if compiled.search(text):
                errors.append(BPError(
                    pattern_type="GENERIC_DESC" if "正常" in bp.description or "泛化" in bp.description else "TEMPLATE_LANG",
                    severity=bp.severity,
                    field="",
                    matched_text=text[:100],
                    matched_pattern=bp.description,
                    description=bp.description,
                    suggestion=bp.suggestion,
                ))
        return errors

    # ------------------------------------------------------------------
    # S5 TP 检测入口
    # ------------------------------------------------------------------

    def check_tp_description(self, text: str, tp_id: str = "") -> list[BPError]:
        """检测 TP description 字段的 bad patterns。

        返回 BLOCK 级别错误 + WARN 级别警告。
        """
        errors = []
        for bp in self._tp_desc_patterns:
            compiled = re.compile(bp.pattern) if isinstance(bp.pattern, str) else bp.pattern
            if compiled.search(text or ""):
                errors.append(BPError(
                    pattern_type="GENERIC_DESC",
                    severity=bp.severity,
                    field="description",
                    matched_text=(text or "")[:100],
                    matched_pattern=bp.description,
                    description=bp.description,
                    suggestion=bp.suggestion,
                    tp_id=tp_id,
                ))
        return errors

    def check_tp_title(self, text: str, tp_id: str = "") -> list[BPError]:
        """检测 TP title 字段的 bad patterns。"""
        errors = []
        for bp in self._tp_title_patterns:
            compiled = re.compile(bp.pattern) if isinstance(bp.pattern, str) else bp.pattern
            if compiled.search(text or ""):
                errors.append(BPError(
                    pattern_type="TEMPLATE_LANG",
                    severity=bp.severity,
                    field="title",
                    matched_text=(text or "")[:100],
                    matched_pattern=bp.description,
                    description=bp.description,
                    suggestion=bp.suggestion,
                    tp_id=tp_id,
                ))
        return errors

    def check_tp_preconditions(self, text: str, tp_id: str = "") -> list[BPError]:
        """检测 TP preconditions 数组的 bad patterns。

        text 为 preconditions join 后的字符串。
        """
        errors = []
        precond_list = text.split("\n") if text else []
        for item in precond_list:
            for bp in self._tp_precond_patterns:
                compiled = re.compile(bp.pattern) if isinstance(bp.pattern, str) else bp.pattern
                if compiled.search(item.strip()):
                    errors.append(BPError(
                        pattern_type="GENERIC_DESC",
                        severity=bp.severity,
                        field="preconditions",
                        matched_text=item.strip()[:100],
                        matched_pattern=bp.description,
                        description=bp.description,
                        suggestion=bp.suggestion,
                        tp_id=tp_id,
                    ))
        return errors

    def check_tp_all(self, tp: dict) -> tuple[list[BPError], list[BPError]]:
        """检测一条 TP 的所有文本字段。

        返回 (blocks, warnings) — BLOCK 列表和 WARN 列表。
        """
        tp_id = tp.get("tp_id", "")
        blocks, warnings = [], []

        for err in self.check_tp_description(tp.get("description", "") or "", tp_id):
            (blocks if err.severity == "BLOCK" else warnings).append(err)
        for err in self.check_tp_title(tp.get("title", "") or "", tp_id):
            (blocks if err.severity == "BLOCK" else warnings).append(err)

        # preconditions 可能是数组或字符串
        precond = tp.get("preconditions")
        if isinstance(precond, list):
            precond_text = "\n".join(str(p) for p in precond)
        else:
            precond_text = str(precond or "")
        for err in self.check_tp_preconditions(precond_text, tp_id):
            (blocks if err.severity == "BLOCK" else warnings).append(err)

        return blocks, warnings

    # ------------------------------------------------------------------
    # S6 TC 检测入口
    # ------------------------------------------------------------------

    def check_tc_steps(self, text: str, tc_id: str = "") -> list[BPError]:
        """检测 TC 操作步骤字段的 bad patterns。"""
        errors = []
        for bp in self._tc_steps_patterns:
            compiled = re.compile(bp.pattern) if isinstance(bp.pattern, str) else bp.pattern
            if compiled.search(text or ""):
                errors.append(BPError(
                    pattern_type="TEMPLATE_LANG",
                    severity=bp.severity,
                    field="操作步骤",
                    matched_text=(text or "")[:100],
                    matched_pattern=bp.description,
                    description=bp.description,
                    suggestion=bp.suggestion,
                    tc_id=tc_id,
                ))
        return errors

    def check_tc_expected(self, text: str, tc_id: str = "") -> list[BPError]:
        """检测 TC 预期结果字段的 bad patterns。"""
        errors = []
        for bp in self._tc_expected_patterns:
            compiled = re.compile(bp.pattern) if isinstance(bp.pattern, str) else bp.pattern
            if compiled.search(text or ""):
                errors.append(BPError(
                    pattern_type="GENERIC_DESC",
                    severity=bp.severity,
                    field="预期结果",
                    matched_text=(text or "")[:100],
                    matched_pattern=bp.description,
                    description=bp.description,
                    suggestion=bp.suggestion,
                    tc_id=tc_id,
                ))
        return errors

    def check_tc_precondition(self, text: str, tc_id: str = "") -> list[BPError]:
        """检测 TC 前置条件字段的 bad patterns。"""
        errors = []
        for bp in self._tc_precond_patterns:
            compiled = re.compile(bp.pattern) if isinstance(bp.pattern, str) else bp.pattern
            if compiled.search(text or ""):
                errors.append(BPError(
                    pattern_type="GENERIC_DESC",
                    severity=bp.severity,
                    field="前置条件",
                    matched_text=(text or "")[:100],
                    matched_pattern=bp.description,
                    description=bp.description,
                    suggestion=bp.suggestion,
                    tc_id=tc_id,
                ))
        return errors

    def check_tc_all(self, tc: dict) -> tuple[list[BPError], list[BPError]]:
        """检测一条 TC 的所有文本字段。

        返回 (blocks, warnings) — BLOCK 列表和 WARN 列表。
        """
        tc_id = tc.get("case_id", "")
        blocks, warnings = [], []

        # 操作步骤（可能是字符串或结构化数组）
        steps = tc.get("操作步骤", tc.get("steps", ""))
        if isinstance(steps, list):
            steps_text = "\n".join(
                s.get("action", str(s)) if isinstance(s, dict) else str(s)
                for s in steps
            )
        else:
            steps_text = str(steps or "")
        for err in self.check_tc_steps(steps_text, tc_id):
            (blocks if err.severity == "BLOCK" else warnings).append(err)

        # 预期结果（可能是字符串或数组）
        expected = tc.get("预期结果", tc.get("expected_results", ""))
        if isinstance(expected, list):
            expected_text = "\n".join(
                e.get("预期", str(e)) if isinstance(e, dict) else str(e)
                for e in expected
            )
        else:
            expected_text = str(expected or "")
        for err in self.check_tc_expected(expected_text, tc_id):
            (blocks if err.severity == "BLOCK" else warnings).append(err)

        # 前置条件
        precond = tc.get("前置条件", tc.get("preconditions", ""))
        if isinstance(precond, list):
            precond_text = "\n".join(str(p) for p in precond)
        else:
            precond_text = str(precond or "")
        for err in self.check_tc_precondition(precond_text, tc_id):
            (blocks if err.severity == "BLOCK" else warnings).append(err)

        return blocks, warnings

    # ------------------------------------------------------------------
    # 汇总报告
    # ------------------------------------------------------------------

    @staticmethod
    def format_errors(errors: list[BPError]) -> list[dict]:
        """把 BPError 列表格式化为 dict 列表（供 validator 使用）。"""
        return [
            {
                "type": f"BAD_PATTERN_{e.severity}",
                "id": e.tp_id or e.tc_id or "?",
                "field": e.field,
                "error": f"[{e.field}] {e.description}",
                "matched": e.matched_text,
                "suggestion": e.suggestion,
            }
            for e in errors
        ]


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------

def _self_test() -> int:
    detector = BadPatternDetector()
    passed = 0
    total = 0

    def check(name: str, text: str, expect_block: bool, check_fn, item_id="TP-001"):
        nonlocal passed, total
        total += 1
        errs = check_fn(text, item_id)
        blocks = [e for e in errs if e.severity == "BLOCK"]
        has_block = len(blocks) > 0
        if has_block == expect_block:
            passed += 1
            print(f"  ✓ {name}: expect_block={expect_block}, got_block={has_block}")
        else:
            print(f"  ✗ {name}: expect_block={expect_block}, got_block={has_block}")
            for e in errs:
                print(f"    -> {e.description}")

    # TP description tests
    check("TP desc: 泛化「验证正常」",
          "验证系统正常", True,
          detector.check_tp_description)
    check("TP desc: 泛化「业务功能正常」",
          "业务功能正常运作", True,
          detector.check_tp_description)
    check("TP desc: 合规描述",
          "玩家进入商城首页，余额=500，尝试购买道具A（单价=200），验证购买成功，道具A数量+1，余额=300",
          False,
          detector.check_tp_description)

    # TP title tests
    check("TP title: 以「验证」开头",
          "验证道具列表展示", True,
          detector.check_tp_title)
    check("TP title: 以「测试」开头",
          "测试购买功能", True,
          detector.check_tp_title)
    check("TP title: 合规",
          "余额充足时购买成功", False,
          detector.check_tp_title)

    # TP preconditions tests
    check("TP precond: 「无」占位",
          "无", True,
          detector.check_tp_preconditions)
    check("TP precond: 合规",
          "玩家已登录\n余额=500\n道具可购买", False,
          detector.check_tp_preconditions)

    # TC steps tests
    check("TC steps: 「执行操作」模板",
          "1. 执行操作\n2. 验证预期结果", True,
          detector.check_tc_steps)
    check("TC steps: 「验证XX正常」泛化",
          "1. 点击购买\n2. 验证系统正常响应", True,
          detector.check_tc_steps)
    check("TC steps: 合规",
          "1. 点击【购买】按钮\n2. 弹窗显示购买成功\n3. 余额=300，道具A数量+1", False,
          detector.check_tc_steps)

    # TC expected tests
    check("TC expected: 「无」占位",
          "无", True,
          detector.check_tc_expected)
    check("TC expected: 「系统正常响应」泛化",
          "系统正常响应", True,
          detector.check_tc_expected)
    check("TC expected: 含 S4 引用",
          "[S4-1.3.2] 异常分支", True,
          detector.check_tc_expected)
    check("TC expected: 合规",
          "1. 弹窗关闭\n2. 余额=300\n3. 道具A数量=1", False,
          detector.check_tc_expected)

    # TC preconditions tests
    check("TC precond: 「无」占位",
          "无", True,
          detector.check_tc_precondition)
    check("TC precond: 合规",
          "玩家已登录，余额=500，道具可购买", False,
          detector.check_tc_precondition)

    # 全字段检测
    total += 1
    blocks, warns = detector.check_tp_all({
        "tp_id": "TP-001",
        "title": "验证道具列表展示",
        "description": "验证功能正常",
        "preconditions": ["无"],
    })
    if len(blocks) >= 3:
        passed += 1
        print(f"  ✓ TP all-fields: got {len(blocks)} blocks (expect ≥3)")
    else:
        print(f"  ✗ TP all-fields: got {len(blocks)} blocks, expect ≥3")

    total += 1
    blocks, warns = detector.check_tc_all({
        "case_id": "UI-TC-001",
        "操作步骤": "1. 执行操作\n2. 验证预期结果",
        "预期结果": "无",
        "前置条件": "无",
    })
    if len(blocks) >= 3:
        passed += 1
        print(f"  ✓ TC all-fields: got {len(blocks)} blocks (expect ≥3)")
    else:
        print(f"  ✗ TC all-fields: got {len(blocks)} blocks, expect ≥3")

    print(f"\n[bad_pattern_detector self-test] {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(_self_test())
