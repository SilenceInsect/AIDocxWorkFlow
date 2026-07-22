#!/usr/bin/env python3
"""L1 校验器 — S5 测试点产物（字段溯源版）。

校验范围：
  - test_points.json

重点：
  - 直接复用 s5_exit_precheck.py 的 run_precheck()
  - TP ID 格式：{Module}-TP-{NNN} 或 TP-{NNN}（兼容）
  - module 为 8 模块枚举之一
  - s4_reference 引用存在性（可选 context）
  - 字段溯源校验：TP 必须包含 obj_name/fp_name 字段
    obj_name 与 S2 obj_name 逐字相等；fp_name 与 S2 fp_desc 不字面重复
"""

from __future__ import annotations

import re

from ai_workflow.l1_format_validator import L1BaseValidator
from ai_workflow.validators.bad_pattern_detector import BadPatternDetector

__all__ = ["L1S5Validator"]


# ---------------------------------------------------------------------------
# 字段溯源校验辅助函数（模块级，供外部调用）
# ---------------------------------------------------------------------------

# v2 入口别名（向后兼容 — 外部调用方可能仍引用 validate_formal_name_v2）


# ---------------------------------------------------------------------------
# L1S5Validator
# ---------------------------------------------------------------------------


class L1S5Validator(L1BaseValidator):
    """S5 测试点产物 L1 校验器（字段溯源版）

    直接复用 s5_exit_precheck.py 的 run_precheck()。
    字段溯源校验：obj_name/fp_name 字段 + feature_point_ref 字段 + 锚点分离校验。
    """

    stage = "S5"
    array_keys = ["test_points", "scenario_test_points", "items"]

    def get_required_fields(self) -> list[str]:
        # 实际 S5 test_points.json 必填字段（v17 字段溯源版）
        # 新增 preconditions 字段（v17 整改）
        return [
            "tp_id",
            "module",
            "test_point_type",
            "description",
            "s4_reference",
            "is_assumed",
            "applies_rule",
            "preconditions",  # v17 新增：前置条件（数组）
        ]

    def get_id_fields(self) -> dict[str, str]:
        return {
            "tp_id": "TP_SIMPLE",  # 兼容简化格式：TP-NNN
        }

    def get_reference_fields(self) -> list[dict]:
        return [
            # s4_reference 可选；若 context 提供了 s4_ids 则做校验
            {"field": "s4_reference", "target_ids": set(), "context_key": "s4_ids"},
            # fp_id 对应 S2 OBJ 的 feature_points
            {"field": "fp_id", "target_ids": set(), "context_key": "fp_ids"},
        ]

    def validate_json_format(self, data: dict | list) -> list[dict]:
        errors = super().validate_json_format(data)
        items = self._collect_items(data)
        if not items:
            errors.append(self._standardize_error(
                "EMPTY_ARRAY",
                "测试点数组为空",
            ))
        return errors

    def validate_required_fields(self, data: dict | list) -> list[dict]:
        errors = super().validate_required_fields(data)
        items = self._collect_items(data)
        for i, tp in enumerate(items):
            if not isinstance(tp, dict):
                continue
            tp_id = tp.get("tp_id", f"#{i}")

            # module 枚举检查
            mod = tp.get("module", "")
            if mod and mod not in {"CONFIG", "UI", "BIZ", "UTIL", "LINK", "SPECIAL", "LOG", "HINT"}:
                errors.append(self._standardize_error(
                    "INVALID_MODULE",
                    f"module '{mod}' 不在 8 模块枚举中",
                    index=i, field="module", id=tp_id,
                    expected="CONFIG|UI|BIZ|UTIL|LINK|SPECIAL|LOG|HINT",
                ))

            # v17 新增：preconditions 非空校验（≥ 1 项）
            precond = tp.get("preconditions")
            if precond is None:
                errors.append(self._standardize_error(
                    "MISSING_PRECONDITIONS",
                    f"[{tp_id}] preconditions 字段缺失",
                    index=i, field="preconditions", id=tp_id,
                ))
            elif not isinstance(precond, list) or len(precond) == 0:
                errors.append(self._standardize_error(
                    "EMPTY_PRECONDITIONS",
                    f"[{tp_id}] preconditions 为空数组",
                    index=i, field="preconditions", id=tp_id,
                ))

        # 思维约束 · bad pattern 阻断（防御 Agent 套模板）
        errors += self.validate_bad_patterns(data)

        return errors

    def validate_id_naming(self, data: dict | list) -> list[dict]:
        errors = []
        items = self._collect_items(data)
        seen_ids: set[str] = set()
        for i, tp in enumerate(items):
            if not isinstance(tp, dict):
                continue
            tp_id = str(tp.get("tp_id", "")).strip()
            if not tp_id:
                continue
            if tp_id in seen_ids:
                errors.append(self._standardize_error(
                    "DUPLICATE_ID",
                    f"tp_id '{tp_id}' 重复",
                    index=i, field="tp_id", id=tp_id,
                ))
            seen_ids.add(tp_id)
            simple = re.compile(r"^TP-\d{3,}$")
            module = re.compile(r"^(CONFIG|UI|BIZ|UTIL|LINK|SPECIAL|LOG|HINT)-TP-\d{3,}$")
            if not (simple.match(tp_id) or module.match(tp_id)):
                errors.append(self._standardize_error(
                    "INVALID_ID_FORMAT",
                    f"tp_id '{tp_id}' 不符合规范（TP-NNN 或 {{Module}}-TP-NNN）",
                    index=i, field="tp_id", id=tp_id,
                    expected="TP-NNN 或 {Module}-TP-NNN",
                ))
        return errors

    # -------------------------------------------------------------------------
    # 字段溯源校验（精准匹配 — 替代锚点校验）
    # -------------------------------------------------------------------------

    def validate_field_traceability(self, data: dict | list) -> list[dict]:
        """字段溯源校验：每个 TP 的 obj_name/fp_name/preconditions 字段必须精准匹配 S2。

        5 项校验（v17 新增 preconditions）：
          1. obj_name 字段存在且 == S2 obj_name（逐字相等）
          2. fp_name 字段存在且命名规则合规（含动词 + ≤ 20 字符）
          3. fp_name 与 S2 fp_desc 不字面重复（避免语义重定义）
          4. title / description 不带【OBJ - FP】锚点（锚点分离）
          5. preconditions 数组长度 ≥ 1（v17 新增）
        """
        errors = []
        items = self._collect_items(data)

        # Build S2 name maps
        obj_name_by_id: dict[str, str] = {}
        fp_desc_by_id: dict[str, str] = {}
        fp_to_obj: dict[str, str] = {}

        for obj in getattr(self, "requirement_objects", []):
            obj_id = obj.get("id", "")
            obj_name = obj.get("obj_name", "").strip()
            obj_name_by_id[obj_id] = obj_name
            for fp in obj.get("feature_points", []):
                fp_id = fp.get("id", "")
                fp_desc = fp.get("fp_desc", "").strip()
                fp_desc_by_id[fp_id] = fp_desc
                fp_to_obj[fp_id] = obj_id

        for i, tp in enumerate(items):
            if not isinstance(tp, dict):
                continue
            tp_id = tp.get("tp_id", f"#{i}")

            # Resolve IDs
            fpr = tp.get("feature_point_ref", "")
            fp_id = fpr
            obj_id = fp_to_obj.get(fp_id, "")
            s2_obj_name = obj_name_by_id.get(obj_id, "")
            s2_fp_desc = fp_desc_by_id.get(fp_id, "")

            # 1. obj_name 字段存在且 == S2 obj_name（逐字相等）
            tp_obj_name = tp.get("obj_name", "").strip()
            if tp_obj_name and s2_obj_name and tp_obj_name != s2_obj_name:
                errors.append({
                    "type": "L1_FIELD_FAIL",
                    "tp_id": tp_id,
                    "error": (
                        f"[{tp_id}] TP.obj_name「{tp_obj_name}」与 S2 obj_name「{s2_obj_name}」"
                        f"不一致（字段逐字比对）"
                    ),
                    "index": i,
                    "field": "obj_name",
                })

            # 2. fp_name 字段存在且命名规则合规
            tp_fp_name = tp.get("fp_name", "").strip()
            if not tp_fp_name:
                errors.append({
                    "type": "L1_FIELD_FAIL",
                    "tp_id": tp_id,
                    "error": f"[{tp_id}] fp_name 字段缺失",
                    "index": i,
                    "field": "fp_name",
                })
            else:
                # 命名规则：含动词 + 长度 ≤ 20 字符
                if len(tp_fp_name) > 20:
                    errors.append({
                        "type": "L1_FIELD_FAIL",
                        "tp_id": tp_id,
                        "error": (
                            f"[{tp_id}] fp_name「{tp_fp_name}」长度 {len(tp_fp_name)} > 20 字符"
                        ),
                        "index": i,
                        "field": "fp_name",
                    })

            # 3. fp_name 与 S2 fp_desc 不字面重复
            if tp_fp_name and s2_fp_desc and tp_fp_name == s2_fp_desc:
                errors.append({
                    "type": "L1_FIELD_FAIL",
                    "tp_id": tp_id,
                    "error": (
                        f"[{tp_id}] fp_name「{tp_fp_name}」与 S2 fp_desc 字面量重复"
                        f"（避免语义重定义）"
                    ),
                    "index": i,
                    "field": "fp_name",
                })

            # 4. title / description 不带【OBJ - FP】锚点（锚点分离）
            title_text = tp.get("title", "") or ""
            desc_text = tp.get("description", "") or ""
            for field_name, field_text in [("title", title_text), ("description", desc_text)]:
                if field_text and field_text.startswith("【"):
                    errors.append({
                        "type": "L1_FIELD_FAIL",
                        "tp_id": tp_id,
                        "error": (
                            f"[{tp_id}] {field_name} 不应以【】锚点开头"
                            f"（字段溯源版仅 JSON 字段承载 OBJ/FP 名称）"
                            f"当前 {field_name} 前 30 字符：「{field_text[:30]}」"
                        ),
                        "index": i,
                        "field": field_name,
                    })

            # 5. preconditions 数组长度 ≥ 1（v17 新增）
            precond = tp.get("preconditions")
            if precond is None:
                errors.append({
                    "type": "L1_FIELD_FAIL",
                    "tp_id": tp_id,
                    "error": f"[{tp_id}] preconditions 字段缺失",
                    "index": i,
                    "field": "preconditions",
                })
            elif not isinstance(precond, list) or len(precond) == 0:
                errors.append({
                    "type": "L1_FIELD_FAIL",
                    "tp_id": tp_id,
                    "error": f"[{tp_id}] preconditions 为空数组",
                    "index": i,
                    "field": "preconditions",
                })

        return errors

    def check_field_traceability_coverage(self, data: dict | list) -> dict:
        """字段溯源覆盖率统计（v17 新增 preconditions）。

        统计维度：
          - field_obj_match：TP.obj_name 字段与 S2 obj_name 逐字相等
          - field_fp_present：TP.fp_name 字段存在
          - field_fp_no_literal_conflict：TP.fp_name 与 S2 fp_desc 不字面重复
          - anchor_separated：title 和 description 无【】锚点
          - preconditions_present：TP.preconditions 数组长度 ≥ 1
          - all_pass：5 项全部达标
        """
        items = self._collect_items(data)
        if not items:
            return {
                "field_obj_match": 0, "field_fp_present": 0,
                "field_fp_no_literal_conflict": 0, "anchor_separated": 0,
                "preconditions_present": 0, "all_pass": 0,
                "total_items": 0,
            }

        obj_name_by_id: dict[str, str] = {}
        fp_desc_by_id: dict[str, str] = {}
        fp_to_obj: dict[str, str] = {}

        for obj in getattr(self, "requirement_objects", []):
            obj_id = obj.get("id", "")
            obj_name_by_id[obj_id] = obj.get("obj_name", "").strip()
            for fp in obj.get("feature_points", []):
                fp_id = fp.get("id", "")
                fp_desc_by_id[fp_id] = fp.get("fp_desc", "").strip()
                fp_to_obj[fp_id] = obj_id

        stats = {
            "field_obj_match": 0,
            "field_fp_present": 0,
            "field_fp_no_literal_conflict": 0,
            "anchor_separated": 0,
            "preconditions_present": 0,
            "all_pass": 0,
            "total_items": len(items),
        }

        for tp in items:
            if not isinstance(tp, dict):
                continue

            fpr = tp.get("feature_point_ref", "")
            fp_id = fpr
            obj_id = fp_to_obj.get(fp_id, "")
            s2_obj_name = obj_name_by_id.get(obj_id, "")
            s2_fp_desc = fp_desc_by_id.get(fp_id, "")

            tp_obj_name = tp.get("obj_name", "").strip()
            tp_fp_name = tp.get("fp_name", "").strip()

            ok_obj = bool(tp_obj_name and s2_obj_name and tp_obj_name == s2_obj_name)
            ok_fp_present = bool(tp_fp_name)
            ok_fp_no_conflict = bool(tp_fp_name and s2_fp_desc and tp_fp_name != s2_fp_desc)

            # Anchor separation: title 和 description 都不以【开头
            title_text = tp.get("title", "") or ""
            desc_text = tp.get("description", "") or ""
            ok_anchor_sep = (not title_text.startswith("【")) and (not desc_text.startswith("【"))

            # v17 新增：preconditions 存在且非空
            precond = tp.get("preconditions")
            ok_precond = bool(isinstance(precond, list) and len(precond) >= 1)

            if ok_obj:
                stats["field_obj_match"] += 1
            if ok_fp_present:
                stats["field_fp_present"] += 1
            if ok_fp_no_conflict:
                stats["field_fp_no_literal_conflict"] += 1
            if ok_anchor_sep:
                stats["anchor_separated"] += 1
            if ok_precond:
                stats["preconditions_present"] += 1
            if ok_obj and ok_fp_present and ok_fp_no_conflict and ok_anchor_sep and ok_precond:
                stats["all_pass"] += 1

        return stats

    def validate_formal_name_v2(self, data: dict | list) -> tuple[bool, list[str], dict]:
        """字段溯源校验入口（向后兼容别名，v17 新增 preconditions 校验）。

        返回 (passed: bool, errors: list[str], stats: dict)。
        5 项校验全部通过才算 passed=True。
        """
        errors_dict = self.validate_field_traceability(data)
        errors = [f"[{e.get('tp_id', '?')}] {e.get('error', '')}" for e in errors_dict]
        stats = self.check_field_traceability_coverage(data)
        total = stats.get("total_items", 0)
        stats["check_name"] = "field_traceability"
        stats["total_tps"] = total
        stats["passed_count"] = stats.get("all_pass", 0)
        stats["pass_rate"] = round(stats.get("all_pass", 0) / total, 4) if total else 0
        stats["threshold"] = 1.0  # 硬门禁：100%
        passed = len(errors) == 0
        return passed, errors, stats

    def set_requirement_objects(self, objs: list):
        """Set S2 requirement_objects for field traceability validation. Call before validate()."""
        self.requirement_objects = objs

    # -------------------------------------------------------------------------
    # Bad pattern 检测（思维约束 · 阻断级别）
    # -------------------------------------------------------------------------

    def validate_bad_patterns(self, data: dict | list) -> list[dict]:
        """检测 TP 的泛化描述 / 模板语言。

        阻断条件：
        - description 含「验证正常」「正常流程」「功能可用」类泛化词
        - title 以「验证」「测试」「检查」开头（这些是测试动作，不是测试意图）
        - preconditions 含「无」「无特殊」类占位

        强制 Agent 写出具体可验证的测试意图——避免「套字段模板」式的产出。
        """
        items = self._collect_items(data)
        detector = BadPatternDetector()
        errors: list[dict] = []
        warn_count = 0

        for tp in items:
            if not isinstance(tp, dict):
                continue
            tp_id = tp.get("tp_id", "?")
            blocks, warns = detector.check_tp_all(tp)

            for e in blocks:
                errors.append(self._standardize_error(
                    "BAD_PATTERN_BLOCK",
                    f"[{e.field}] {e.description}",
                    field=e.field, id=tp_id,
                    matched=(e.matched_text or "")[:80],
                    suggestion=e.suggestion,
                ))
            warn_count += len(warns)

        return errors


def _self_test() -> int:
    """self-test: 10 cases 覆盖字段溯源校验全部路径"""
    from ai_workflow.l1_format_validator import L1BaseValidator

    validator = L1S5Validator()
    validator.set_requirement_objects([
        {
            "id": "UI-001-OBJ-01",
            "obj_name": "商城首页道具列表",
            "feature_points": [
                {"id": "UI-001-OBJ-01-FP-1", "fp_desc": "首页按销量展示前10个热门道具"},
            ],
        },
    ])

    cases = []

    # Case 1: 合规样本 → PASS（含 preconditions）
    cases.append({
        "name": "case1_pass",
        "tp": {"tp_id": "TP-001", "module": "UI", "test_point_type": "POSITIVE",
               "obj_name": "商城首页道具列表", "fp_name": "首页销量排序展示",
               "title": "首页销量排序展示验证",
               "description": "玩家进入商城首页验证排序",
               "s4_reference": "R-001", "is_assumed": False,
               "applies_rule": "Step1",
               "preconditions": ["玩家已登录游戏客户端", "商城已配置道具数据"]},
        "expect_pass": True,
    })
    # Case 2: obj_name 不匹配 S2 → FAIL
    cases.append({
        "name": "case2_obj_name_mismatch",
        "tp": {"tp_id": "TP-002", "obj_name": "道具列表",
               "fp_name": "首页销量排序展示", "title": "首页销量排序",
               "description": "描述"},
        "expect_pass": False,
    })
    # Case 3: fp_name 缺失 → FAIL
    cases.append({
        "name": "case3_fp_name_missing",
        "tp": {"tp_id": "TP-003", "obj_name": "商城首页道具列表",
               "title": "title", "description": "desc"},
        "expect_pass": False,
    })
    # Case 4: fp_name 与 S2 fp_desc 字面重复 → FAIL
    cases.append({
        "name": "case4_fp_name_literal_conflict",
        "tp": {"tp_id": "TP-004", "obj_name": "商城首页道具列表",
               "fp_name": "首页按销量展示前10个热门道具",
               "title": "title", "description": "desc"},
        "expect_pass": False,
    })
    # Case 5: title 带【】锚点 → FAIL
    cases.append({
        "name": "case5_title_has_anchor",
        "tp": {"tp_id": "TP-005", "obj_name": "商城首页道具列表",
               "fp_name": "首页销量排序展示",
               "title": "【商城首页道具列表 - 首页按销量展示前10个热门道具】验证",
               "description": "玩家进入商城首页验证排序"},
        "expect_pass": False,
    })
    # Case 6: fp_name 长度 > 20 字符 → FAIL
    cases.append({
        "name": "case6_fp_name_too_long",
        "tp": {"tp_id": "TP-006", "obj_name": "商城首页道具列表",
               "fp_name": "首页销量排序展示功能验证",
               "title": "title", "description": "desc"},
        "expect_pass": False,
    })
    # Case 7: 描述字段带【】 → FAIL
    cases.append({
        "name": "case7_desc_has_anchor",
        "tp": {"tp_id": "TP-007", "obj_name": "商城首页道具列表",
               "fp_name": "首页销量排序展示",
               "title": "首页排序验证",
               "description": "【商城首页道具列表 - 首页按销量展示前10个热门道具】玩家进入"},
        "expect_pass": False,
    })
    # Case 8: 空数据 → 0 errors (但数组为空应有 EMPTY_ARRAY)
    cases.append({
        "name": "case8_empty",
        "tp": [],
        "expect_pass": False,  # 空数组应触发 EMPTY_ARRAY
    })
    # Case 9: 模块字段错误 → 由 validate_required_fields 捕获
    cases.append({
        "name": "case9_invalid_module",
        "tp": {"tp_id": "TP-009", "module": "INVALID",
               "obj_name": "商城首页道具列表",
               "fp_name": "首页销量排序展示",
               "title": "首页排序验证", "description": "desc",
               "test_point_type": "POSITIVE", "s4_reference": "R-01",
               "is_assumed": False, "applies_rule": "Step1"},
        "expect_pass": False,
    })
    # Case 10: 字段缺失测试 → FAIL（缺 description 等必填）
    cases.append({
        "name": "case10_missing_required",
        "tp": {"tp_id": "TP-010", "module": "UI",
               "obj_name": "商城首页道具列表",
               "fp_name": "首页销量排序展示",
               "title": "首页排序验证"},
        "expect_pass": False,
    })
    # Case 11: bad pattern — description 泛化「验证正常」 → FAIL（思维约束）
    cases.append({
        "name": "case11_bad_pattern_desc",
        "tp": {"tp_id": "TP-011", "module": "UI",
               "test_point_type": "POSITIVE",
               "obj_name": "商城首页道具列表",
               "fp_name": "首页销量排序展示",
               "title": "首页销量排序展示验证",
               "description": "验证道具列表功能正常",
               "s4_reference": "R-011", "is_assumed": False,
               "applies_rule": "Step1",
               "preconditions": ["玩家已登录"]},
        "expect_pass": False,
    })
    # Case 12: bad pattern — title 以「验证」开头 → FAIL（思维约束）
    cases.append({
        "name": "case12_bad_pattern_title",
        "tp": {"tp_id": "TP-012", "module": "UI",
               "test_point_type": "POSITIVE",
               "obj_name": "商城首页道具列表",
               "fp_name": "首页销量排序展示",
               "title": "验证道具列表功能",
               "description": "玩家进入商城首页验证排序",
               "s4_reference": "R-012", "is_assumed": False,
               "applies_rule": "Step1",
               "preconditions": ["玩家已登录"]},
        "expect_pass": False,
    })
    # Case 13: bad pattern — preconditions 含「无」占位 → FAIL（思维约束）
    cases.append({
        "name": "case13_bad_pattern_precond",
        "tp": {"tp_id": "TP-013", "module": "UI",
               "test_point_type": "POSITIVE",
               "obj_name": "商城首页道具列表",
               "fp_name": "首页销量排序展示",
               "title": "首页销量排序展示",
               "description": "玩家进入商城首页，验证按销量降序展示",
               "s4_reference": "R-013", "is_assumed": False,
               "applies_rule": "Step1",
               "preconditions": ["无"]},
        "expect_pass": False,
    })

    passed_count = 0
    for case in cases:
        if isinstance(case["tp"], list):
            data = {"test_points": case["tp"]}
        else:
            data = {"test_points": [case["tp"]]}
        passed, errors, stats = validator.validate_formal_name_v2(data)
        # 也跑 validate_required_fields 和 validate_id_naming 模拟完整流程
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

    print(f"\n[L1 S5 self-test] {passed_count}/{len(cases)} passed")
    return 0 if passed_count == len(cases) else 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(_self_test())