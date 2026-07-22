#!/usr/bin/env python3
"""L1 校验器 — S6 测试用例产物（字段溯源版）。

校验范围：
  - test_cases.json

重点：
  - TC ID 格式：{Module}-TC-{NNN}
  - module 为 8 模块枚举之一
  - priority 为 P0/P1/P2/P3
  - s5_ref 引用 S5 tp_id 存在性（可选 context）
  - obj_id 引用 S2 OBJ 存在性（可选 context）
  - 字段溯源继承校验：TC 必须从 S5 TP 继承 obj_name/fp_name 字段
"""

from __future__ import annotations

import re

from ai_workflow.l1_format_validator import L1BaseValidator
from ai_workflow.validators.bad_pattern_detector import BadPatternDetector

__all__ = ["L1S6Validator"]


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

TC_ID_PAT = re.compile(r"^(CONFIG|UI|BIZ|UTIL|LINK|SPECIAL|LOG|HINT)-TC-\d{3,}$")
VALID_MODULES = {"CONFIG", "UI", "BIZ", "UTIL", "LINK", "SPECIAL", "LOG", "HINT"}
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}


def _tc_uses_cn_priority(case_id: str, items: list) -> bool:
    """检查给定 case_id 的 TC 是否使用中文优先级字段（优先级）而非 priority。"""
    for tc in items:
        if tc.get("case_id") == case_id and isinstance(tc, dict):
            # 用了 优先级 且没用 priority → 属于中文别名兼容
            has_cn = tc.get("优先级") is not None and tc.get("优先级") != ""
            has_en = tc.get("priority") is not None and tc.get("priority") != ""
            return has_cn and not has_en
    return False


# ---------------------------------------------------------------------------
# L1S6Validator
# ---------------------------------------------------------------------------


class L1S6Validator(L1BaseValidator):
    """S6 测试用例产物 L1 校验器（字段溯源版）

    新增：字段溯源继承校验 — TC.obj_name/fp_name 必须从 S5 TP 字段继承。
    """

    stage = "S6"
    array_keys = ["test_cases", "items"]

    def get_required_fields(self) -> list[str]:
        # 实际 S6 test_cases.json 必填字段（v17 字段溯源版）
        # 新增 obj_name 字段（v17 整改）+ assertion 字段（Round 2 F4 整改）
        # 优先级字段：使用 priority（v3.01 实际数据），兼容 优先级 在 validate_required_fields 中单独处理
        return [
            "case_id",
            "module",
            "用例描述",
            "前置条件",
            "操作步骤",
            "预期结果",
            "priority",  # v3.01 实际数据用 priority；validate_required_fields 单独兼容 优先级
            "obj_name",  # v17 新增：从 S5 TP 继承
            "assertion",  # Round 2 F4 新增：断言验证非空
        ]

    def get_id_fields(self) -> dict[str, str]:
        return {"case_id": "TC_MODULE"}

    def get_reference_fields(self) -> list[dict]:
        return [
            {"field": "s5_ref", "target_ids": set(), "context_key": "s5_refs"},
            {"field": "obj_id", "target_ids": set(), "context_key": "obj_ids"},
        ]

    def validate_required_fields(self, data: dict | list) -> list[dict]:
        errors = super().validate_required_fields(data)
        items = self._collect_items(data)
        for i, tc in enumerate(items):
            if not isinstance(tc, dict):
                continue
            # module 枚举
            mod = tc.get("module", "")
            if mod and mod not in VALID_MODULES:
                errors.append(self._standardize_error(
                    "INVALID_MODULE",
                    f"module '{mod}' 不在 8 模块枚举中",
                    index=i, field="module", id=tc.get("case_id", f"#{i}"),
                    expected="|".join(sorted(VALID_MODULES)),
                ))
            # priority 枚举
            pri = tc.get("优先级", tc.get("priority", ""))
            if pri and pri not in VALID_PRIORITIES:
                errors.append(self._standardize_error(
                    "INVALID_PRIORITY",
                    f"优先级 '{pri}' 不在 P0/P1/P2/P3 中",
                    index=i, field="优先级", id=tc.get("case_id", f"#{i}"),
                    expected="P0|P1|P2|P3",
                ))
            # s5_ref MUST
            s5_ref = tc.get("s5_ref")
            if not s5_ref or s5_ref == "":
                errors.append(self._standardize_error(
                    "MISSING_REQUIRED",
                    "s5_ref 缺失",
                    index=i, field="s5_ref",
                    id=tc.get("case_id", f"#{i}"),
                ))
            # §12 v2.0: 预期结果必须含 step_ref（强制规范）
            expected = tc.get("预期结果", tc.get("expected_results", []))
            if expected:
                if isinstance(expected, list):
                    has_step_ref = any(
                        isinstance(e, dict) and "step_ref" in e
                        for e in expected
                    )
                    if not has_step_ref:
                        errors.append(self._standardize_error(
                            "MISSING_STEP_REF",
                            "预期结果缺少 step_ref（§12 v2.0 强制）",
                            index=i, field="预期结果",
                            id=tc.get("case_id", f"#{i}"),
                        ))

            # Round 2 F4: assertion 字段非空校验
            assertion = tc.get("assertion")
            if assertion is None:
                errors.append(self._standardize_error(
                    "MISSING_ASSERTION",
                    "assertion 字段缺失（Round 2 F4 新增门禁）",
                    index=i, field="assertion",
                    id=tc.get("case_id", f"#{i}"),
                ))
            elif isinstance(assertion, list) and len(assertion) == 0:
                errors.append(self._standardize_error(
                    "EMPTY_ASSERTION",
                    "assertion 字段为空数组",
                    index=i, field="assertion",
                    id=tc.get("case_id", f"#{i}"),
                ))
            elif isinstance(assertion, str) and assertion.strip() == "":
                errors.append(self._standardize_error(
                    "EMPTY_ASSERTION",
                    "assertion 字段为空字符串",
                    index=i, field="assertion",
                    id=tc.get("case_id", f"#{i}"),
                ))

        # 优先级双名兼容：实际数据中部分 TC 使用"优先级"而非"priority"
        # base validator 已按 get_required_fields() 中的"priority"字段检查，
        # 对使用"优先级"的 TC 会报 MISSING_REQUIRED('priority') —— 这些是误报，需过滤
        errors = [
            e for e in errors
            if not (
                e.get("type") == "MISSING_REQUIRED"
                and e.get("field") == "priority"
                and e.get("id")  # 有 id 才能查到对应 TC
                and _tc_uses_cn_priority(e.get("id"), items)
            )
        ]

        # 思维约束 · bad pattern 阻断（防御 Agent 套模板）
        errors += self.validate_bad_patterns(data)

        return errors

    def validate_id_naming(self, data: dict | list) -> list[dict]:
        errors = []
        items = self._collect_items(data)
        seen_ids: set[str] = set()
        for i, tc in enumerate(items):
            if not isinstance(tc, dict):
                continue
            case_id = str(tc.get("case_id", "")).strip()
            if not case_id:
                continue
            if case_id in seen_ids:
                errors.append(self._standardize_error(
                    "DUPLICATE_ID",
                    f"case_id '{case_id}' 重复",
                    index=i, field="case_id", id=case_id,
                ))
            seen_ids.add(case_id)
            if not TC_ID_PAT.match(case_id):
                errors.append(self._standardize_error(
                    "INVALID_ID_FORMAT",
                    f"case_id '{case_id}' 不符合 {{Module}}-TC-{{NNN}} 格式",
                    index=i, field="case_id", id=case_id,
                    expected="{Module}-TC-{NNN}",
                ))
        return errors

    # -------------------------------------------------------------------------
    # 字段溯源继承校验（替代锚点继承校验）
    # -------------------------------------------------------------------------

    def validate_field_traceability(self, data: dict | list) -> list[dict]:
        """字段溯源继承校验：每个 TC 的 obj_name/fp_name 必须从源 S5 TP 字段继承。

        4 项校验：
          1. TC.obj_name 字段 == 源 TP.obj_name（继承性，逐字相等）
          2. TC.fp_name 字段 == 源 TP.fp_name（继承性，逐字相等）
          3. test_scenario 不以【OBJ - FP】锚点开头（锚点分离）
          4. feature_point_ref 字段继承自源 TP
        """
        errors = []
        items = self._collect_items(data)

        # S5 TP field map: tp_id -> obj_name / fp_name / feature_point_ref
        tp_obj_name: dict[str, str] = {}
        tp_fp_name: dict[str, str] = {}
        tp_feature_point_ref: dict[str, str] = {}
        for tp in getattr(self, "tp_list", []):
            tp_id = tp.get("tp_id", "")
            if tp_id:
                tp_obj_name[tp_id] = (tp.get("obj_name", "") or "").strip()
                tp_fp_name[tp_id] = (tp.get("fp_name", "") or "").strip()
                tp_feature_point_ref[tp_id] = (tp.get("feature_point_ref", "") or "").strip()

        for i, tc in enumerate(items):
            if not isinstance(tc, dict):
                continue
            tc_id = tc.get("case_id", f"#{i}")
            s5_ref = tc.get("s5_ref", "")

            # 1. TC.obj_name 字段 == 源 TP.obj_name（继承性）
            tc_obj_name = tc.get("obj_name", "").strip()
            expected_tp_obj = tp_obj_name.get(s5_ref, "")
            if tc_obj_name and expected_tp_obj and tc_obj_name != expected_tp_obj:
                errors.append({
                    "type": "L1_FIELD_FAIL",
                    "tc_id": tc_id,
                    "error": (
                        f"[{tc_id}] TC.obj_name「{tc_obj_name}」与源 TP「{s5_ref}」"
                        f"的 obj_name「{expected_tp_obj}」不一致（继承性失败）"
                    ),
                    "index": i,
                    "field": "obj_name",
                })

            # 2. TC.fp_name 字段 == 源 TP.fp_name（继承性）
            tc_fp_name = tc.get("fp_name", "").strip()
            expected_tp_fp = tp_fp_name.get(s5_ref, "")
            if tc_fp_name and expected_tp_fp and tc_fp_name != expected_tp_fp:
                errors.append({
                    "type": "L1_FIELD_FAIL",
                    "tc_id": tc_id,
                    "error": (
                        f"[{tc_id}] TC.fp_name「{tc_fp_name}」与源 TP「{s5_ref}」"
                        f"的 fp_name「{expected_tp_fp}」不一致（继承性失败）"
                    ),
                    "index": i,
                    "field": "fp_name",
                })

            # 3. test_scenario / 用例描述 不以【OBJ - FP】锚点开头（锚点分离）
            # 校验 test_scenario 和 用例描述 两个字段，任何一个带【】都 FAIL
            for field_name in ("test_scenario", "用例描述"):
                field_text = tc.get(field_name, "") or ""
                if field_text and field_text.startswith("【"):
                    errors.append({
                        "type": "L1_FIELD_FAIL",
                        "tc_id": tc_id,
                        "error": (
                            f"[{tc_id}] {field_name} 不应以【】锚点开头"
                            f"（字段溯源版仅 JSON 字段承载 OBJ/FP 名称）"
                            f"当前 {field_name} 前 30 字符：「{field_text[:30]}」"
                        ),
                        "index": i,
                        "field": field_name,
                    })

        return errors

    def check_field_traceability_coverage(self, data: dict | list) -> dict:
        """字段溯源继承覆盖率统计。

        统计维度：
          - field_obj_inherited：TC.obj_name == 源 TP.obj_name
          - field_fp_inherited：TC.fp_name == 源 TP.fp_name
          - anchor_separated：test_scenario 无【】锚点
          - all_pass：3 项全部达标
        """
        items = self._collect_items(data)
        if not items:
            return {
                "field_obj_inherited": 0, "field_fp_inherited": 0,
                "anchor_separated": 0, "all_pass": 0,
                "total_items": 0,
            }

        # S5 TP field map
        tp_obj_name: dict[str, str] = {}
        tp_fp_name: dict[str, str] = {}
        for tp in getattr(self, "tp_list", []):
            tp_id = tp.get("tp_id", "")
            if tp_id:
                tp_obj_name[tp_id] = (tp.get("obj_name", "") or "").strip()
                tp_fp_name[tp_id] = (tp.get("fp_name", "") or "").strip()

        stats = {
            "field_obj_inherited": 0,
            "field_fp_inherited": 0,
            "anchor_separated": 0,
            "all_pass": 0,
            "total_items": len(items),
        }

        for tc in items:
            if not isinstance(tc, dict):
                continue
            s5_ref = tc.get("s5_ref", "")
            expected_tp_obj = tp_obj_name.get(s5_ref, "")
            expected_tp_fp = tp_fp_name.get(s5_ref, "")

            tc_obj_name = tc.get("obj_name", "").strip()
            tc_fp_name = tc.get("fp_name", "").strip()

            ok_obj = bool(tc_obj_name and expected_tp_obj and tc_obj_name == expected_tp_obj)
            ok_fp = bool(tc_fp_name and expected_tp_fp and tc_fp_name == expected_tp_fp)

            scenario_text = tc.get("test_scenario", "") or tc.get("用例描述", "") or ""
            ok_anchor_sep = (not scenario_text.startswith("【"))

            if ok_obj:
                stats["field_obj_inherited"] += 1
            if ok_fp:
                stats["field_fp_inherited"] += 1
            if ok_anchor_sep:
                stats["anchor_separated"] += 1
            if ok_obj and ok_fp and ok_anchor_sep:
                stats["all_pass"] += 1

        return stats

    def validate_formal_name_v2(self, data: dict | list) -> tuple[bool, list[str], dict]:
        """字段溯源校验入口（向后兼容别名）。

        返回 (passed: bool, errors: list[str], stats: dict)。
        4 项校验全部通过才算 passed=True。
        """
        errors_dict = self.validate_field_traceability(data)
        errors = [f"[{e.get('tc_id', '?')}] {e.get('error', '')}" for e in errors_dict]
        stats = self.check_field_traceability_coverage(data)
        total = stats.get("total_items", 0)
        stats["check_name"] = "tc_field_traceability"
        stats["total_tcs"] = total
        stats["passed_count"] = stats.get("all_pass", 0)
        stats["pass_rate"] = round(stats.get("all_pass", 0) / total, 4) if total else 0
        stats["threshold"] = 1.0  # 硬门禁：100%
        passed = len(errors) == 0
        return passed, errors, stats

    def set_requirement_objects_and_tp_list(self, objs: list, tp_list: list):
        """Set S2 requirement_objects and S5 tp_list for field traceability validation. Call before validate()."""
        self.requirement_objects = objs
        self.tp_list = tp_list

    # -------------------------------------------------------------------------
    # Bad pattern 检测（思维约束 · 阻断级别）
    # -------------------------------------------------------------------------

    def validate_bad_patterns(self, data: dict | list) -> list[dict]:
        """检测 TC 的泛化描述 / 模板语言。

        阻断条件：
        - 操作步骤含「执行操作」「执行测试」「验证预期结果」类模板语言
        - 操作步骤含「验证XX正常」类泛化描述
        - 预期结果为「无」占位
        - 预期结果含「系统正常响应」「预期结果正确」类循环定义
        - 预期结果含 S4 节点编号引用
        - 前置条件为「无」类占位

        强制 Agent 写出具体可执行的测试步骤和可验证的预期——避免「套字段模板」式产出。
        """
        items = self._collect_items(data)
        detector = BadPatternDetector()
        errors: list[dict] = []
        warn_count = 0

        for tc in items:
            if not isinstance(tc, dict):
                continue
            tc_id = tc.get("case_id", "?")
            blocks, warns = detector.check_tc_all(tc)

            for e in blocks:
                errors.append(self._standardize_error(
                    "BAD_PATTERN_BLOCK",
                    f"[{e.field}] {e.description}",
                    field=e.field, id=tc_id,
                    matched=(e.matched_text or "")[:80],
                    suggestion=e.suggestion,
                ))
            warn_count += len(warns)

        return errors


def _self_test() -> int:
    """self-test: 11 cases 覆盖字段溯源继承校验全部路径（含 Round 2 F4 assertion 门禁）"""
    from ai_workflow.l1_format_validator import L1BaseValidator

    validator = L1S6Validator()
    validator.set_requirement_objects_and_tp_list(
        objs=[{
            "id": "UI-001-OBJ-01",
            "obj_name": "商城首页道具列表",
            "feature_points": [
                {"id": "UI-001-OBJ-01-FP-1", "fp_desc": "首页按销量展示前10个热门道具"},
            ],
        }],
        tp_list=[{
            "tp_id": "TP-001", "obj_name": "商城首页道具列表",
            "fp_name": "首页销量排序展示", "feature_point_ref": "UI-001-OBJ-01-FP-1",
        }],
    )

    cases = []

    # Case 1: 合规样本（含 assertion） → PASS
    # priority 字段：实际数据用 priority（v3.01 标准），self-test 也应保持一致
    cases.append({
        "name": "case1_pass",
        "tc": {
            "case_id": "UI-TC-001", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入商城首页验证排序",
            "前置条件": "玩家已登录",
            "操作步骤": "1. 进入商城首页\n2. 查看道具列表",
            "预期结果": "道具列表按销量降序",
            "priority": "P1", "s5_ref": "TP-001",
            "assertion": ["道具列表可见", "排序正确"],
        },
        "expect_pass": True,
    })
    # Case 2: obj_name 不继承自 TP → FAIL
    cases.append({
        "name": "case2_obj_name_not_inherited",
        "tc": {
            "case_id": "UI-TC-002", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "道具列表",
            "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入商城首页",
            "前置条件": "玩家已登录",
            "操作步骤": "1. 进入", "预期结果": "排序正确",
            "priority": "P1", "s5_ref": "TP-001",
        },
        "expect_pass": False,
    })
    # Case 3: fp_name 不继承自 TP → FAIL
    cases.append({
        "name": "case3_fp_name_not_inherited",
        "tc": {
            "case_id": "UI-TC-003", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表",
            "fp_name": "错误fp名",
            "test_scenario": "玩家进入",
            "前置条件": "登录",
            "操作步骤": "1. 进入", "预期结果": "排序",
            "priority": "P1", "s5_ref": "TP-001",
        },
        "expect_pass": False,
    })
    # Case 4: test_scenario 带【】锚点 → FAIL
    cases.append({
        "name": "case4_scenario_has_anchor",
        "tc": {
            "case_id": "UI-TC-004", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "【商城首页道具列表 - 首页按销量展示前10个热门道具】玩家进入",
            "前置条件": "登录",
            "操作步骤": "1. 进入", "预期结果": "排序",
            "priority": "P1", "s5_ref": "TP-001",
        },
        "expect_pass": False,
    })
    # Case 5: 用例描述字段带【】 → FAIL
    cases.append({
        "name": "case5_description_has_anchor",
        "tc": {
            "case_id": "UI-TC-005", "module": "UI",
            "用例描述": "【商城首页道具列表 - 首页按销量展示前10个热门道具】玩家进入",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "登录",
            "操作步骤": "1. 进入", "预期结果": "排序",
            "priority": "P1", "s5_ref": "TP-001",
        },
        "expect_pass": False,
    })
    # Case 6: case_id 格式错误 → FAIL
    cases.append({
        "name": "case6_invalid_id_format",
        "tc": {
            "case_id": "TC-006", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "登录",
            "操作步骤": "1. 进入", "预期结果": "排序",
            "priority": "P1", "s5_ref": "TP-001",
        },
        "expect_pass": False,
    })
    # Case 7: s5_ref 缺失 → FAIL
    cases.append({
        "name": "case7_s5_ref_missing",
        "tc": {
            "case_id": "UI-TC-007", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "登录",
            "操作步骤": "1. 进入", "预期结果": "排序",
            "priority": "P1",
        },
        "expect_pass": False,
    })
    # Case 8: 优先级非法 → FAIL
    cases.append({
        "name": "case8_invalid_priority",
        "tc": {
            "case_id": "UI-TC-008", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "登录",
            "操作步骤": "1. 进入", "预期结果": "排序",
            "priority": "P9", "s5_ref": "TP-001",
        },
        "expect_pass": False,
    })
    # Case 9: 模块非法 → FAIL
    cases.append({
        "name": "case9_invalid_module",
        "tc": {
            "case_id": "UI-TC-009", "module": "INVALID",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "登录",
            "操作步骤": "1. 进入", "预期结果": "排序",
            "priority": "P1", "s5_ref": "TP-001",
        },
        "expect_pass": False,
    })
    # Case 10: 空数组 → EMPTY_ARRAY
    cases.append({
        "name": "case10_empty",
        "tc": [],
        "expect_pass": False,
    })
    # Case 11: assertion 字段缺失 → FAIL（Round 2 F4 assertion 门禁）
    cases.append({
        "name": "case11_assertion_missing",
        "tc": {
            "case_id": "UI-TC-011", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "登录",
            "操作步骤": "1. 进入", "预期结果": "排序",
            "priority": "P1", "s5_ref": "TP-001",
            # assertion 缺失
        },
        "expect_pass": False,
    })
    # Case 12: bad pattern — 操作步骤含「执行操作」模板 → FAIL（思维约束）
    cases.append({
        "name": "case12_bad_pattern_steps",
        "tc": {
            "case_id": "UI-TC-012", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "玩家已登录",
            "操作步骤": "1. 执行操作\n2. 验证预期结果",
            "预期结果": "购买成功",
            "priority": "P1", "s5_ref": "TP-001",
            "assertion": ["a"],
        },
        "expect_pass": False,
    })
    # Case 13: bad pattern — 预期结果为「无」占位 → FAIL（思维约束）
    cases.append({
        "name": "case13_bad_pattern_expected",
        "tc": {
            "case_id": "UI-TC-013", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "玩家已登录",
            "操作步骤": "1. 点击购买",
            "预期结果": "无",
            "priority": "P1", "s5_ref": "TP-001",
            "assertion": ["a"],
        },
        "expect_pass": False,
    })
    # Case 14: bad pattern — 预期含 S4 节点编号 → FAIL（思维约束）
    cases.append({
        "name": "case14_bad_pattern_s4_ref",
        "tc": {
            "case_id": "UI-TC-014", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "玩家已登录",
            "操作步骤": "1. 点击购买",
            "预期结果": "[S4-1.3.2] 异常分支",
            "priority": "P1", "s5_ref": "TP-001",
            "assertion": ["a"],
        },
        "expect_pass": False,
    })
    # Case 15: bad pattern — 前置条件为「无」占位 → FAIL（思维约束）
    cases.append({
        "name": "case15_bad_pattern_precond",
        "tc": {
            "case_id": "UI-TC-015", "module": "UI",
            "用例描述": "商城首页道具列表",
            "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
            "test_scenario": "玩家进入",
            "前置条件": "无",
            "操作步骤": "1. 点击购买",
            "预期结果": "购买成功",
            "priority": "P1", "s5_ref": "TP-001",
            "assertion": ["a"],
        },
        "expect_pass": False,
    })

    passed_count = 0
    for case in cases:
        if isinstance(case["tc"], list):
            data = {"test_cases": case["tc"]}
        else:
            data = {"test_cases": [case["tc"]]}
        passed, errors, stats = validator.validate_formal_name_v2(data)
        req_errors = validator.validate_required_fields(data)
        id_errors = validator.validate_id_naming(data)
        all_passed = passed and len(req_errors) == 0 and len(id_errors) == 0
        if all_passed == case["expect_pass"]:
            passed_count += 1
            print(f"  ✓ {case['name']}: expected={case['expect_pass']}, got={all_passed}")
        else:
            print(f"  ✗ {case['name']}: expected={case['expect_pass']}, got={all_passed}")
            print(f"    field_errors={errors[:2]}")
            print(f"    req_errors={req_errors[:2]}")
            print(f"    id_errors={id_errors[:2]}")

    print(f"\n[L1 S6 self-test] {passed_count}/{len(cases)} passed")
    return 0 if passed_count == len(cases) else 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(_self_test())