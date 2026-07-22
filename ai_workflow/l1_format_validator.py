#!/usr/bin/env python3
"""AIDocxWorkFlow L1 格式校验通用基类（v16 T2 §2）。

职责（L1 脚本级校验——不做语义审查）：
  1. JSON 格式合法性
  2. 必填字段完整性（MUST 级别）
  3. ID 命名规范（正则匹配 + 重复检测）
  4. 引用 ID 存在性（跨文件/跨节点头）

调用方式：
  from ai_workflow.l1_format_validator import L1BaseValidator
  validator = MyStageValidator()
  result = validator.run_l1_check(Path("artifact.json"))

  python3 ai_workflow/l1_format_validator.py --self-test

退出码：
  0 = 通过
  1 = 失败（errors 存在）
"""

from __future__ import annotations

import json
import re
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

# ── 8 模块枚举（与 .cursor/MODULES.md §1 一致）───────────────
VALID_MODULES = frozenset({
    "CONFIG", "UI", "BIZ", "AUX", "LINK",
    "SPECIAL", "LOG", "HINT",
})

# ── 通用 ID 正则模式库 ───────────────────────────────────────
ID_PATTERNS: dict[str, re.Pattern] = {
    # S5 兼容简化格式（历史产物）
    "TP_SIMPLE": re.compile(r"^TP-\d{3,}$"),
    # S5 规范格式：{Module}-TP-{NNN}
    "TP_MODULE": re.compile(r"^(CONFIG|UI|BIZ|AUX|LINK|SPECIAL|LOG|HINT)-TP-\d{3,}$"),
    # S6 TC 格式：{Module}-TC-{NNN}
    "TC_MODULE": re.compile(r"^(CONFIG|UI|BIZ|AUX|LINK|SPECIAL|LOG|HINT)-TC-\d{3,}$"),
    # S2 Epic 格式：{Module}-{NNN}  如 CONFIG-001
    "EPIC": re.compile(r"^(CONFIG|UI|BIZ|AUX|LINK|SPECIAL|LOG|HINT)-\d{3,}$"),
    # S2 Story 格式：{EpicID}-{NN}  如 CONFIG-001-001
    "STORY": re.compile(r"^[A-Z]+-\d{3,}-\d{1,3}$"),
    # S2 OBJ 格式：{StoryID}-OBJ-{NN}  如 CONFIG-001-001-OBJ-01
    "OBJ": re.compile(r"^[A-Z]+-\d{3,}-\d{1,3}-OBJ-\d{1,3}$"),
    # S2 FP 格式：FP-{OBJ_seq}-{FP_seq}  如 FP-001-01
    "FP": re.compile(r"^FP-\d{1,3}-\d{1,3}$"),
    # S4 风险点（全局）：R-NNN
    "R_GLOBAL": re.compile(r"^R-\d{3,}$"),
    # S4 风险点（按 Epic）：R-{EpicID}-NN
    "R_EPIC": re.compile(r"^R-[A-Z]+-\d{3,}-\d{1,3}$"),
    # S4 异常树叶子：S4-{EpicID}-X.Y.Z
    "S4_LEAF": re.compile(r"^S4-[A-Z]+-\d{3,}-\d+\.\d+(\.\d+)*$"),
    # S4 流程节点：S4-{EpicID}-F{NN}
    "S4_FLOW": re.compile(r"^S4-[A-Z]+-\d{3,}-F\d{1,3}$"),
    # S3 页面节点：PAGE-{EpicID}-{NN}
    "PAGE": re.compile(r"^PAGE-[A-Z]+-\d{3,}-\d{2}$"),
    # S7 RCA 建议 ID
    "RCA": re.compile(r"^(M|S|C)-\d{3}$"),
}


# ═══════════════════════════════════════════════════════════
# 通用异常
# ═══════════════════════════════════════════════════════════

class L1ValidationError(Exception):
    """L1 校验失败"""
    pass


# ═══════════════════════════════════════════════════════════
# 基类
# ═══════════════════════════════════════════════════════════

class L1BaseValidator(ABC):
    """L1 格式校验基类（v16 T2 §2）。

    子类必须实现：
      get_required_fields()    — 必填字段列表
      get_id_patterns()       — ID 正则模式 {field: pattern_name}
      get_reference_fields()   — 引用字段列表

    继承即可用的 4 类校验：
      validate_json_format()   — JSON 合法性
      validate_required_fields() — 必填字段完整性
      validate_id_naming()    — ID 命名规范
      validate_references()    — 引用存在性

    统一入口：
      run_l1_check(artifact_path, context) → {passed, errors, warnings, summary}
    """

    # 子类覆盖的阶段名
    stage: str = "UNKNOWN"

    # 子类覆盖的数组键名（支持多种 schema 格式）
    array_keys: list[str] = []

    # ── 3 个抽象方法（子类必须实现）────────────────────────

    @abstractmethod
    def get_required_fields(self) -> list[str]:
        """返回该阶段每个条目的必填字段（MUST 级别），如 ["tp_id", "module", "description"]"""

    @abstractmethod
    def get_id_fields(self) -> dict[str, str]:
        """返回 ID 字段映射 {field_name: pattern_name}，如 {"tp_id": "TP_MODULE", "module": None}"""

    @abstractmethod
    def get_reference_fields(self) -> list[dict]:
        """返回引用字段列表，每个元素包含：
        {
            "field": str,          # 字段名
            "target_ids": list[str],  # 从 context 中提取的目标 ID 集合
            "context_key": str | None,  # context dict 中持有目标 ID 的键
        }
        若无引用关系，返回空列表。
        """

    # ── 4 类通用校验（基类实现，子类可覆盖）────────────────

    def _collect_items(self, data: dict | list) -> list[dict]:
        """从 data 中提取条目列表（支持多种 schema 格式）。"""
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            for key in self.array_keys:
                if key in data and isinstance(data[key], list):
                    return [item for item in data[key] if isinstance(item, dict)]
            return [data]  # 单对象也算一个条目
        return []

    def _standardize_error(
        self,
        err_type: str,
        msg: str,
        index: int | None = None,
        field: str | None = None,
        id_val: str | None = None,
        expected: str | None = None,
        **extra: Any,
    ) -> dict:
        """构造标准错误对象。"""
        obj: dict = {
            "type": err_type,
            "msg": msg,
        }
        if index is not None:
            obj["index"] = index
        if field is not None:
            obj["field"] = field
        if id_val is not None:
            obj["id"] = id_val
        if expected is not None:
            obj["expected"] = expected
        obj.update(extra)
        return obj

    def _standardize_warning(
        self,
        warn_type: str,
        msg: str,
        field: str | None = None,
        **extra: Any,
    ) -> dict:
        """构造标准警告对象。"""
        obj: dict = {"type": warn_type, "msg": msg}
        if field is not None:
            obj["field"] = field
        obj.update(extra)
        return obj

    def validate_json_format(self, data: dict | list) -> list[dict]:
        """JSON 格式合法性校验（递归容错）。"""
        errors: list[dict] = []
        if isinstance(data, list):
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    errors.append(self._standardize_error(
                        "NOT_DICT", f"第 {i} 项不是 dict 类型", index=i,
                    ))
        elif not isinstance(data, dict):
            errors.append(self._standardize_error(
                "NOT_DICT", "JSON 根对象不是 dict",
            ))
        return errors

    def validate_required_fields(self, data: dict | list) -> list[dict]:
        """必填字段完整性校验（MUST 级别）。"""
        errors: list[dict] = []
        required = self.get_required_fields()
        items = self._collect_items(data)
        if not items:
            errors.append(self._standardize_error(
                "EMPTY_ARRAY", "条目数组为空",
            ))
            return errors

        for i, item in enumerate(items):
            for field in required:
                val = item.get(field)
                if val is None or val == "" or val == []:
                    errors.append(self._standardize_error(
                        "MISSING_REQUIRED",
                        f"缺少必填字段 '{field}'",
                        index=i, field=field,
                        id=item.get(self._get_id_field(), f"#{i}"),
                    ))
        return errors

    def validate_id_naming(self, data: dict | list) -> list[dict]:
        """ID 命名规范校验（正则匹配 + 重复检测）。"""
        errors: list[dict] = []
        warnings: list[dict] = []
        id_fields = self.get_id_fields()
        items = self._collect_items(data)
        if not items:
            return errors

        # 收集每个 ID 字段的已见 ID
        seen_ids: dict[str, set[str]] = {
            field: set() for field in id_fields
        }

        for i, item in enumerate(items):
            for field, pattern_name in id_fields.items():
                if pattern_name is None:
                    continue
                raw_val = item.get(field)
                if raw_val is None:
                    continue
                id_val = str(raw_val).strip()
                pattern = ID_PATTERNS.get(pattern_name)

                # 格式检查
                if pattern and not pattern.match(id_val):
                    errors.append(self._standardize_error(
                        "INVALID_ID_FORMAT",
                        f"ID '{id_val}' 不符合规范格式（期望: {pattern_name}）",
                        index=i, field=field, id=id_val,
                        expected=pattern_name,
                    ))

                # 重复检查
                if id_val and id_val in seen_ids[field]:
                    errors.append(self._standardize_error(
                        "DUPLICATE_ID",
                        f"ID '{id_val}' 重复出现",
                        index=i, field=field, id=id_val,
                    ))
                seen_ids[field].add(id_val)

        return errors + warnings

    def validate_references(self, data: dict | list, context: dict | None) -> list[dict]:
        """引用 ID 存在性校验。

        Args:
            data: 产物 JSON 数据
            context: 上下文 dict，可包含 {target_ids: set[str]} 或其他元数据
        """
        errors: list[dict] = []
        ref_fields = self.get_reference_fields()
        if not ref_fields:
            return errors

        items = self._collect_items(data)
        for i, item in enumerate(items):
            for ref in ref_fields:
                field = ref["field"]
                raw_val = item.get(field)
                if raw_val is None or raw_val == "":
                    continue
                ref_val = str(raw_val).strip()
                target_ids = ref.get("target_ids", set())
                if target_ids and ref_val not in target_ids:
                    errors.append(self._standardize_error(
                        "REFERENCE_NOT_FOUND",
                        f"引用 ID '{ref_val}' 在目标集合中不存在",
                        index=i, field=field,
                        id=item.get(self._get_id_field(), f"#{i}"),
                        referenced=ref_val,
                    ))
        return errors

    def _get_id_field(self) -> str | None:
        """获取该阶段的 ID 字段名（第一个）"""
        id_fields = self.get_id_fields()
        return next(iter(id_fields.keys())) if id_fields else None

    # ── 统一入口 ────────────────────────────────────────────

    def run_l1_check(
        self,
        artifact_path: Path | str,
        context: dict | None = None,
    ) -> dict:
        """执行全量 L1 校验，返回统一结果结构。

        Args:
            artifact_path: 产物文件路径（.json）
            context: 可选上下文 {target_ids: set[str], ...}

        Returns:
            {
                "passed": bool,
                "errors": [...],
                "warnings": [...],
                "summary": {...}
            }
        """
        errors: list[dict] = []
        warnings: list[dict] = []
        path = Path(artifact_path)

        # 1. JSON 格式
        if not path.exists():
            return {
                "passed": False,
                "errors": [self._standardize_error(
                    "FILE_NOT_FOUND", f"文件不存在: {path}",
                )],
                "warnings": [],
                "summary": {
                    "stage": self.stage,
                    "artifact_path": str(path),
                    "item_count": 0,
                    "errors_count": 1,
                    "warnings_count": 0,
                    "fields_validated": [],
                    "ids_validated": [],
                    "references_validated": [],
                },
            }
        try:
            raw_text = path.read_text(encoding="utf-8")
            data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            return {
                "passed": False,
                "errors": [self._standardize_error(
                    "JSON_PARSE_ERROR", f"JSON 解析失败: {e}",
                )],
                "warnings": [],
                "summary": {
                    "stage": self.stage,
                    "artifact_path": str(path),
                    "item_count": 0,
                    "errors_count": 1,
                    "warnings_count": 0,
                    "fields_validated": [],
                    "ids_validated": [],
                    "references_validated": [],
                },
            }

        # 2-5. 4 类校验
        errors += self.validate_json_format(data)
        errors += self.validate_required_fields(data)
        errors += self.validate_id_naming(data)
        errors += self.validate_references(data, context)

        items = self._collect_items(data)
        item_count = len(items)

        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "stage": self.stage,
                "artifact_path": str(path),
                "item_count": item_count,
                "errors_count": len(errors),
                "warnings_count": len(warnings),
                "fields_validated": self.get_required_fields(),
                "ids_validated": list(self.get_id_fields().keys()),
                "references_validated": [
                    r["field"] for r in self.get_reference_fields()
                ],
            },
        }


# ═══════════════════════════════════════════════════════════
# Cross-stage consistency helpers（Round 14 F-C / F-D 物化）
# ═══════════════════════════════════════════════════════════

def check_tp_id_s5_ref_consistency(
    data: dict | list,
    *,
    tp_id_field: str = "tp_id",
    s5_ref_field: str = "s5_ref",
) -> list[dict]:
    """Round 14 F-C [MAJOR]：S5 双标识一致性检查。

    约束：每条 TP 的 `tp_id` 必须 == `s5_ref`（决策档 `s5_id_dedupe_decision.md` 方案 C）。

    Returns:
        violations list — [{"type": "INCONSISTENT_TP_ID", "msg": ..., "index": i, "id": ..., "tp_id": ..., "s5_ref": ...}]
    """
    errors: list[dict] = []
    items = _collect_items_safely(data)
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        tp_id = item.get(tp_id_field)
        s5_ref = item.get(s5_ref_field)
        if tp_id is None and s5_ref is None:
            continue
        if str(tp_id or "") != str(s5_ref or ""):
            errors.append({
                "type": "INCONSISTENT_TP_ID",
                "msg": f"tp_id ({tp_id}) != s5_ref ({s5_ref})",
                "index": i,
                "id": str(tp_id or s5_ref or f"#{i}"),
                "tp_id": tp_id,
                "s5_ref": s5_ref,
            })
    return errors


def check_tc_id_field_absence(
    data: dict | list,
    *,
    tc_id_field: str = "tc_id",
    new_only: bool = False,
) -> list[dict]:
    """Round 14 F-D [MAJOR]：S6 tc_id 死字段检查。

    约束：S6 TC 不应含 `tc_id` 字段（决策档 `s6_id_dedupe_decision.md` 方案 A）。
    - `new_only=False`（默认）：仅 WARN（不 FAIL）——兼容 v3.01 out_of_scope 数据
    - `new_only=True`：FAIL——强制新数据不含 `tc_id` 字段

    Returns:
        warnings/errors list — [{"type": "DEPRECATED_TC_ID", "msg": ..., "index": i, "id": ..., "severity": "warn"|"error"}]
    """
    items = _collect_items_safely(data)
    findings: list[dict] = []
    severity = "error" if new_only else "warn"
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        if tc_id_field in item:
            findings.append({
                "type": "DEPRECATED_TC_ID",
                "msg": f"TC 含历史冗余字段 '{tc_id_field}'（决策档方案 A：新数据应忽略）",
                "index": i,
                "id": str(item.get("case_id", f"#{i}")),
                "field": tc_id_field,
                "value": item.get(tc_id_field),
                "severity": severity,
            })
    return findings


def check_assertion_completeness(
    data: dict | list,
    *,
    assertion_field: str = "assertion",
    min_count: int = 1,
) -> list[dict]:
    """Round 15 F-E [MINOR]：S6 TC 机器可读断言完整性检查。

    约束：每条 TC 必须含 ≥ `min_count` 个 `assertion`，每项必须含 `assertion_type` 必填子字段。
    - v3.01 JSON 暂未含 assertion（属 Round 16+ 数据迁移范围）；本轮 SKILL.md 新增，本校验默认 ERROR 模式强约束新数据
    - 决策档 `governance/design_iter/current/round15_q_decision_table.md` §1 决策 1

    Args:
        data: 产物 JSON 数据（list 或 dict）
        assertion_field: assertion 字段名（默认 "assertion"）
        min_count: 每 TC 最少 assertion 数（默认 1）

    Returns:
        errors list — [{"type": "MISSING_ASSERTION" | "INCOMPLETE_ASSERTION" | "MISSING_ASSERTION_TYPE",
                       "msg": ..., "index": i, "id": ..., "field": ...}]
    """
    errors: list[dict] = []
    items = _collect_items_safely(data)
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        tc_id = str(item.get("case_id", f"#{i}"))
        raw = item.get(assertion_field)
        if raw is None or raw == []:
            errors.append({
                "type": "MISSING_ASSERTION",
                "msg": f"TC 缺机器可读断言字段 '{assertion_field}'（Round 15 F-E 必填 ≥ {min_count} 项）",
                "index": i,
                "id": tc_id,
                "field": assertion_field,
                "expected_min_count": min_count,
            })
            continue
        if not isinstance(raw, list):
            errors.append({
                "type": "INCOMPLETE_ASSERTION",
                "msg": f"TC '{assertion_field}' 应为数组类型，实际为 {type(raw).__name__}",
                "index": i,
                "id": tc_id,
                "field": assertion_field,
            })
            continue
        if len(raw) < min_count:
            errors.append({
                "type": "INCOMPLETE_ASSERTION",
                "msg": f"TC '{assertion_field}' 长度 {len(raw)} < {min_count}",
                "index": i,
                "id": tc_id,
                "field": assertion_field,
                "actual_count": len(raw),
                "expected_min_count": min_count,
            })
            continue
        for j, assertion in enumerate(raw):
            if not isinstance(assertion, dict):
                errors.append({
                    "type": "INCOMPLETE_ASSERTION",
                    "msg": f"TC.assertion[{j}] 应为 dict，实际为 {type(assertion).__name__}",
                    "index": i,
                    "id": tc_id,
                    "field": f"{assertion_field}[{j}]",
                })
                continue
            if "assertion_type" not in assertion or not assertion.get("assertion_type"):
                errors.append({
                    "type": "MISSING_ASSERTION_TYPE",
                    "msg": f"TC.assertion[{j}] 缺必填子字段 'assertion_type'",
                    "index": i,
                    "id": tc_id,
                    "field": f"{assertion_field}[{j}].assertion_type",
                })
    return errors


def check_no_fp_name_field(
    data: dict | list,
    *,
    fp_name_field: str = "fp_name",
    mode: str = "warn",
) -> list[dict]:
    """Round 15 F-F [MINOR]：S6 TC fp_name 死字段检查。

    约束：S6 TC 不应再含 `fp_name` 字段（决策档 `s6_id_dedupe_decision.md` 后续 F-F 修订）。
    `feature_point_ref` 已结构化足以反查 FP 元数据，fp_name 双字段冗余已治理。
    - `mode="warn"`（默认）：仅 WARN（不 FAIL）——兼容 v3.01 out_of_scope 数据
    - `mode="error"`：FAIL——强制新数据不含 `fp_name` 字段（与 F-D tc_id `--new-only` 策略一致）

    Args:
        data: 产物 JSON 数据（list 或 dict）
        fp_name_field: 死字段名（默认 "fp_name"）
        mode: 严重度模式（默认 "warn"）

    Returns:
        findings list — [{"type": "DEPRECATED_FP_NAME", "msg": ..., "index": i, "id": ..., "severity": "warn"|"error"}]
    """
    items = _collect_items_safely(data)
    findings: list[dict] = []
    severity = "error" if mode == "error" else "warn"
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        if fp_name_field in item:
            findings.append({
                "type": "DEPRECATED_FP_NAME",
                "msg": f"TC 含历史冗余字段 '{fp_name_field}'（Round 15 F-F 已删除，用 'feature_point_ref' 反查）",
                "index": i,
                "id": str(item.get("case_id", f"#{i}")),
                "field": fp_name_field,
                "value": item.get(fp_name_field),
                "severity": severity,
            })
    return findings


def _collect_items_safely(data: dict | list) -> list[dict]:
    """从 data 中提取条目列表（复用基类约定但不强制 array_keys）。"""
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        # 尝试常见 array_keys
        for key in ("test_points", "stories", "test_cases", "items"):
            if key in data and isinstance(data[key], list):
                nested: list[dict] = []
                for item in data[key]:
                    if isinstance(item, dict):
                        # stories 可能嵌套 scenario_test_points
                        if key == "stories" and "scenario_test_points" in item:
                            for tp in item["scenario_test_points"]:
                                if isinstance(tp, dict):
                                    nested.append(tp)
                        else:
                            nested.append(item)
                if nested:
                    return nested
        return [data]  # 单对象
    return []

def self_test() -> int:
    """自测：基类 4 类校验 + 统一返回结构 + 错误格式。"""
    import tempfile

    print("[self-test] l1_format_validator.py")

    # ── 测试用 Validator（用 S5-like 字段做测试）────────────
    class _TestValidator(L1BaseValidator):
        stage = "TEST"
        array_keys = ["test_points", "items"]

        def get_required_fields(self):
            return ["tp_id", "module", "description"]

        def get_id_fields(self):
            return {"tp_id": "TP_SIMPLE", "module": None}

        def get_reference_fields(self):
            return []

    validator = _TestValidator()

    print("=== Round 18 FU-2 self_test C23: stage_gatekeeper 集成 assertion 校验 smoke ===")
    # 跨模块导入验证：stage_gatekeeper / coverage_validator 协同可调用
    try:
        from ai_workflow.stage_gatekeeper import self_test as _gk_st  # type: ignore[attr-defined]
        assert callable(_gk_st), "stage_gatekeeper.self_test 应可调用"
        print("  C23 (stage_gatekeeper.self_test 可调用): PASS")
    except (ImportError, AttributeError) as exc:
        print(f"  C23 (stage_gatekeeper 集成 smoke): FAIL — {exc}")
        return 1

    # === Round 18 FU-4 self_test C24: --auto argv 在 fixture 上跑 ===
    print("=== Round 18 FU-4 self_test C24: --auto argv 在 fixture 上跑 ===")
    # 在 self_test 内构造本地 fixture（不依赖外部 tmpdir），便于隔离 argv
    fu4_fix = Path(tempfile.mkdtemp(prefix="l1_fu4_")) / "fixture_fu4.json"
    fu4_fix.write_text(
        json.dumps({
            "test_cases": [
                {"case_id": "TC-OK-1", "assertion": [
                    {"assertion_type": "numeric", "assertion_target": "balance", "operator": "==", "expected_value": 0},
                ], "module": "BIZ"},
                {"case_id": "TC-OK-2", "assertion": [
                    {"assertion_type": "enum_match", "assertion_target": "status", "expected_value": "PAID"},
                ], "module": "BIZ"},
                {"case_id": "TC-MISS-ASSERTION", "module": "BIZ"},
                {"case_id": "TC-HAS-FP-NAME", "fp_name": "首页销量排序",
                 "feature_point_ref": "X", "assertion": [
                     {"assertion_type": "numeric", "expected_value": 1},
                 ], "module": "UI"},
            ],
        }, ensure_ascii=False),
        encoding="utf-8",
    )

    # 用 subprocess 调 --auto argv（隔离 argv 解析）
    # 关键：必须传 PYTHONPATH=. 否则子进程因 cwd != repo root 找不到 ai_workflow module
    import subprocess as _sp_c24  # noqa: PLC0415
    import os as _os_c24  # noqa: PLC0415
    _child_env = dict(_os_c24.environ)
    _child_env["PYTHONPATH"] = _os_c24.pathsep.join(
        [_os_c24.getcwd()] + _child_env.get("PYTHONPATH", "").split(_os_c24.pathsep)
    )
    proc_c24 = _sp_c24.run(
        [sys.executable, str(Path(__file__).resolve()), "--auto", str(fu4_fix)],
        capture_output=True, text=True, timeout=15,
        env=_child_env,
    )
    out_c24 = proc_c24.stdout + proc_c24.stderr
    # --auto 在有 violations 时返回 1（这是预期行为），不是 bug
    assert proc_c24.returncode == 1, f"C24 --auto 应返回 1（检测到 violations），实测 {proc_c24.returncode}: {out_c24}"
    assert f"{fu4_fix}: 2 violations" in out_c24, \
        f"C24 应输出 '2 violations' 行，实测:\n{out_c24}"
    assert "DEPRECATED_FP_NAME" in out_c24, f"C24 应含 DEPRECATED_FP_NAME: {out_c24}"
    assert "MISSING_ASSERTION" in out_c24, f"C24 应含 MISSING_ASSERTION: {out_c24}"
    print(f"  C24 (--auto argv fixture): PASS — {out_c24.splitlines()[0]}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Case 1: 合法样本 → 应通过
        good = tmp / "good.json"
        good.write_text(json.dumps([
            {"tp_id": "TP-001", "module": "UI", "description": "登录"},
            {"tp_id": "TP-002", "module": "BIZ", "description": "购买"},
        ], ensure_ascii=False), encoding="utf-8")
        r = validator.run_l1_check(good)
        assert r["passed"], f"C1 应通过: {r}"
        assert r["summary"]["item_count"] == 2
        assert r["summary"]["errors_count"] == 0
        print("  C1 (good sample): PASS")

        # Case 2: 缺必填字段 → 应失败
        bad_req = tmp / "bad_req.json"
        bad_req.write_text(json.dumps([
            {"tp_id": "TP-001", "module": "UI"},  # 缺 description
            {"tp_id": "TP-002"},                    # 缺 module + description
        ], ensure_ascii=False), encoding="utf-8")
        r = validator.run_l1_check(bad_req)
        assert not r["passed"], f"C2 应失败: {r}"
        assert any(e["type"] == "MISSING_REQUIRED" for e in r["errors"])
        print("  C2 (missing required): PASS")

        # Case 3: ID 格式错误 → 应失败
        bad_id = tmp / "bad_id.json"
        bad_id.write_text(json.dumps([
            {"tp_id": "BAD-ID-1", "module": "UI", "description": "x"},
        ], ensure_ascii=False), encoding="utf-8")
        r = validator.run_l1_check(bad_id)
        assert not r["passed"], f"C3 应失败: {r}"
        assert any(e["type"] == "INVALID_ID_FORMAT" for e in r["errors"])
        print("  C3 (invalid ID format): PASS")

        # Case 4: ID 重复 → 应失败
        dup_id = tmp / "dup_id.json"
        dup_id.write_text(json.dumps([
            {"tp_id": "TP-001", "module": "UI", "description": "a"},
            {"tp_id": "TP-001", "module": "BIZ", "description": "b"},
        ], ensure_ascii=False), encoding="utf-8")
        r = validator.run_l1_check(dup_id)
        assert not r["passed"], f"C4 应失败: {r}"
        assert any(e["type"] == "DUPLICATE_ID" for e in r["errors"])
        print("  C4 (duplicate ID): PASS")

        # Case 5: 文件不存在 → 应失败
        r = validator.run_l1_check(tmp / "nonexistent.json")
        assert not r["passed"], f"C5 应失败: {r}"
        assert any(e["type"] == "FILE_NOT_FOUND" for e in r["errors"])
        print("  C5 (file not found): PASS")

        # Case 6: 统一返回结构完整
        r = validator.run_l1_check(good)
        assert all(k in r for k in ("passed", "errors", "warnings", "summary"))
        assert all(k in r["summary"] for k in (
            "stage", "artifact_path", "item_count", "errors_count",
            "warnings_count", "fields_validated", "ids_validated",
        ))
        print("  C6 (return structure): PASS")

        # Case 7: 空数组 → 应报错
        empty = tmp / "empty.json"
        empty.write_text("[]", encoding="utf-8")
        r = validator.run_l1_check(empty)
        assert not r["passed"]
        assert any(e["type"] == "EMPTY_ARRAY" for e in r["errors"])
        print("  C7 (empty array): PASS")

        # Case 8: JSON 格式错误
        corrupt = tmp / "corrupt.json"
        corrupt.write_text("{bad json", encoding="utf-8")
        r = validator.run_l1_check(corrupt)
        assert not r["passed"]
        assert any(e["type"] == "JSON_PARSE_ERROR" for e in r["errors"])
        print("  C8 (JSON parse error): PASS")

        # Case 9: dict 顶层格式（单对象，非数组）
        single = tmp / "single.json"
        single.write_text(json.dumps({
            "tp_id": "TP-001", "module": "UI", "description": "test",
        }, ensure_ascii=False), encoding="utf-8")
        r = validator.run_l1_check(single)
        assert r["passed"], f"C9 应通过（单对象）: {r}"
        print("  C9 (single-object schema): PASS")

        # Case 10: dict 格式（带 array key）
        with_items = tmp / "with_items.json"
        with_items.write_text(json.dumps({
            "test_points": [
                {"tp_id": "TP-001", "module": "UI", "description": "test"},
            ]
        }, ensure_ascii=False), encoding="utf-8")
        r = validator.run_l1_check(with_items)
        assert r["passed"], f"C10 应通过（dict with array key）: {r}"
        print("  C10 (dict with array key): PASS")

    # === Round 14 F-C: tp_id == s5_ref 一致性检查 2 case ===
    print("=== self_test 11 (F-C): 全一致 tp_id == s5_ref → PASS ===")
    consistent_data = {"test_points": [
        {"tp_id": "UI-TP-001", "s5_ref": "UI-TP-001", "module": "UI"},
        {"tp_id": "BIZ-TP-001", "s5_ref": "BIZ-TP-001", "module": "BIZ"},
    ]}
    c_violations = check_tp_id_s5_ref_consistency(consistent_data)
    assert len(c_violations) == 0, f"F-C C1 全一致应无 violation: {c_violations}"
    print("  PASS — 一致性 PASS")

    print("=== self_test 12 (F-C): 不一致 tp_id != s5_ref → FAIL ===")
    inconsistent_data = {"test_points": [
        {"tp_id": "UI-TP-001", "s5_ref": "TP-001", "module": "UI"},
        {"tp_id": "BIZ-TP-001", "s5_ref": "BIZ-TP-001", "module": "BIZ"},
    ]}
    c_violations2 = check_tp_id_s5_ref_consistency(inconsistent_data)
    assert len(c_violations2) == 1, f"F-C C2 不一致应有 1 violation: {c_violations2}"
    assert c_violations2[0]["type"] == "INCONSISTENT_TP_ID"
    assert c_violations2[0]["tp_id"] == "UI-TP-001"
    assert c_violations2[0]["s5_ref"] == "TP-001"
    print(f"  PASS — 不一致返回 {len(c_violations2)} violation")

    # === Round 14 F-D: tc_id 死字段检查 3 case ===
    print("=== self_test 13 (F-D): 全无 tc_id → PASS ===")
    no_tc_id_data = {"test_cases": [
        {"case_id": "TC-1", "module": "UI", "s5_ref": "UI-TP-001"},
        {"case_id": "TC-2", "module": "BIZ", "s5_ref": "BIZ-TP-001"},
    ]}
    f_violations = check_tc_id_field_absence(no_tc_id_data)
    assert len(f_violations) == 0, f"F-D C1 全无 tc_id 应无 finding: {f_violations}"
    print("  PASS — 无 tc_id, 0 findings")

    print("=== self_test 14 (F-D): 含 tc_id + default 模式 → WARN ===")
    has_tc_id_data = {"test_cases": [
        {"case_id": "TC-1", "tc_id": "TC-1", "module": "UI", "s5_ref": "UI-TP-001"},
    ]}
    f_violations2 = check_tc_id_field_absence(has_tc_id_data, new_only=False)
    assert len(f_violations2) == 1
    assert f_violations2[0]["type"] == "DEPRECATED_TC_ID"
    assert f_violations2[0]["severity"] == "warn", f"F-D C2 default 模式应为 warn: {f_violations2[0]}"
    print(f"  PASS — 含 tc_id default 模式 WARN")

    print("=== self_test 15 (F-D): 含 tc_id + --new-only 模式 → FAIL ===")
    f_violations3 = check_tc_id_field_absence(has_tc_id_data, new_only=True)
    assert len(f_violations3) == 1
    assert f_violations3[0]["severity"] == "error", f"F-D C3 --new-only 模式应为 error: {f_violations3[0]}"
    print(f"  PASS — 含 tc_id --new-only 模式 ERROR")

    # === Round 15 F-E: assertion 完整性检查 4 case ===
    print("=== self_test 16 (F-E): 全部 TC 含 1 assertion → PASS ===")
    e_pass_data = {"test_cases": [
        {"case_id": "TC-1", "module": "UI", "s5_ref": "UI-TP-001",
         "assertion": [{"assertion_type": "numeric", "assertion_target": "balance", "operator": "==", "expected_value": 0}]},
        {"case_id": "TC-2", "module": "BIZ", "s5_ref": "BIZ-TP-001",
         "assertion": [{"assertion_type": "string_contains", "assertion_target": "error_msg", "expected_value": "余额不足"}]},
    ]}
    e_violations = check_assertion_completeness(e_pass_data)
    assert len(e_violations) == 0, f"F-E C1 全 1 assertion 应无 violation: {e_violations}"
    print("  PASS — 全 1 assertion, 0 violations")

    print("=== self_test 17 (F-E): 全部 TC 含 ≥ 2 assertion → PASS ===")
    e_pass_data2 = {"test_cases": [
        {"case_id": "TC-1", "module": "UI", "s5_ref": "UI-TP-001",
         "assertion": [
             {"assertion_type": "numeric", "assertion_target": "balance", "operator": "==", "expected_value": 0},
             {"assertion_type": "string_contains", "assertion_target": "error_msg", "expected_value": "扣款失败"},
         ]},
        {"case_id": "TC-2", "module": "BIZ", "s5_ref": "BIZ-TP-001",
         "assertion": [
             {"assertion_type": "enum_match", "assertion_target": "order_status", "expected_value": "PAID"},
             {"assertion_type": "regex_match", "assertion_target": "log_line", "expected_value": "^\\[ERROR\\].*"},
         ]},
    ]}
    e_violations2 = check_assertion_completeness(e_pass_data2, min_count=2)
    assert len(e_violations2) == 0, f"F-E C2 全 ≥ 2 assertion 应无 violation: {e_violations2}"
    print(f"  PASS — 全 ≥ 2 assertion min_count=2, 0 violations")

    print("=== self_test 18 (F-E): 部分 TC 缺 assertion → FAIL ===")
    e_fail_data = {"test_cases": [
        {"case_id": "TC-1", "module": "UI", "s5_ref": "UI-TP-001",
         "assertion": [{"assertion_type": "numeric", "assertion_target": "balance", "operator": "==", "expected_value": 0}]},
        {"case_id": "TC-2", "module": "BIZ", "s5_ref": "BIZ-TP-001"},  # 缺 assertion
        {"case_id": "TC-3", "module": "AUX", "s5_ref": "AUX-TP-001", "assertion": []},  # 空数组
    ]}
    e_violations3 = check_assertion_completeness(e_fail_data)
    assert len(e_violations3) == 2, f"F-E C3 应 2 violation（缺 assertion + 空数组）: {e_violations3}"
    types_seen = {v["type"] for v in e_violations3}
    assert "MISSING_ASSERTION" in types_seen, f"F-E C3 应含 MISSING_ASSERTION: {types_seen}"
    print(f"  PASS — 部分缺 assertion 返回 {len(e_violations3)} violations ({types_seen})")

    print("=== self_test 19 (F-E): assertion 缺 assertion_type → FAIL ===")
    e_fail_data2 = {"test_cases": [
        {"case_id": "TC-1", "module": "UI", "s5_ref": "UI-TP-001",
         "assertion": [
             {"assertion_target": "balance", "operator": "==", "expected_value": 0},  # 缺 assertion_type
             {"assertion_type": "string_contains", "assertion_target": "error_msg", "expected_value": "失败"},  # OK
         ]},
    ]}
    e_violations4 = check_assertion_completeness(e_fail_data2)
    assert len(e_violations4) == 1, f"F-E C4 应 1 violation（缺 assertion_type）: {e_violations4}"
    assert e_violations4[0]["type"] == "MISSING_ASSERTION_TYPE"
    print(f"  PASS — 缺 assertion_type 返回 {len(e_violations4)} violation ({e_violations4[0]['type']})")

    # === Round 15 F-F: fp_name 死字段检查 3 case ===
    print("=== self_test 20 (F-F): 全无 fp_name → PASS ===")
    f_pass_data = {"test_cases": [
        {"case_id": "TC-1", "module": "UI", "s5_ref": "UI-TP-001",
         "feature_point_ref": "BIZ-PURCHASE-01-001-OBJ-01-FP-1"},
        {"case_id": "TC-2", "module": "BIZ", "s5_ref": "BIZ-TP-001",
         "feature_point_ref": "BIZ-PURCHASE-01-001-OBJ-01-FP-2"},
    ]}
    f_violations4 = check_no_fp_name_field(f_pass_data)
    assert len(f_violations4) == 0, f"F-F C1 全无 fp_name 应无 finding: {f_violations4}"
    print("  PASS — 无 fp_name, 0 findings")

    print("=== self_test 21 (F-F): 含 fp_name + default warn 模式 → WARN ===")
    f_warn_data = {"test_cases": [
        {"case_id": "TC-1", "module": "UI", "s5_ref": "UI-TP-001",
         "fp_name": "首页销量排序展示",  # 历史冗余字段
         "feature_point_ref": "BIZ-PURCHASE-01-001-OBJ-01-FP-1"},
    ]}
    f_violations5 = check_no_fp_name_field(f_warn_data, mode="warn")
    assert len(f_violations5) == 1
    assert f_violations5[0]["type"] == "DEPRECATED_FP_NAME"
    assert f_violations5[0]["severity"] == "warn", f"F-F C2 default 模式应为 warn: {f_violations5[0]}"
    print(f"  PASS — 含 fp_name default 模式 WARN")

    print("=== self_test 22 (F-F): 含 fp_name + error 模式 → FAIL ===")
    f_violations6 = check_no_fp_name_field(f_warn_data, mode="error")
    assert len(f_violations6) == 1
    assert f_violations6[0]["severity"] == "error", f"F-F C3 error 模式应为 error: {f_violations6[0]}"
    print(f"  PASS — 含 fp_name error 模式 ERROR")

    print("[self-test OK] 24 cases passed")
    return 0


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

def main() -> int:
    """Round 18 FU-4 CLI 入口（--auto argv + --self-test argv）。"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="l1_format_validator",
        description="AIDocxWorkFlow L1 格式校验基类（v16 T2 §2）",
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="运行 self-test（不需参数）",
    )
    parser.add_argument(
        "--auto", metavar="JSON_PATH", nargs="+",
        help="Round 18 FU-4：对每个 JSON 路径跑 assertion 完整性 + fp_name 死字段校验（mode=error）",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if args.auto:
        return _run_auto(args.auto)

    print("用法:")
    print("  python3 l1_format_validator.py --self-test")
    print("  python3 l1_format_validator.py --auto <test_cases.json> [<test_cases.json>...]")
    print("  L1 校验基类，请通过子类 validators/l1_s*.py 使用")
    return 0


def _run_auto(json_paths: list[str]) -> int:
    """Round 18 FU-4 --auto argv 实现。

    对每个 JSON 路径：
    - 读 JSON（支持 {test_cases:[...]} / [...] / {meta,test_cases} 3 种 schema）
    - 跑 check_assertion_completeness（默认 min_count=1，error 模式）
    - 跑 check_no_fp_name_field（mode=error）—— Round 15 F-F
    - 打印 `path: N violations` + 每条 violation 的简述
    - 退出码：1 字节 = N total violations > 0；0 = 全通过

    Returns:
        0 = 全通过 / 1 = 存在 violations
    """
    from typing import Any as _Any
    total_violations = 0
    any_fail = False
    for raw_path in json_paths:
        path = Path(raw_path)
        if not path.exists():
            print(f"{path}: FILE_NOT_FOUND")
            any_fail = True
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"{path}: JSON_PARSE_ERROR — {exc}")
            any_fail = True
            continue

        # 取 test_cases（多 schema 兼容）
        if isinstance(data, dict):
            tcs: list = data.get("test_cases", [])
        elif isinstance(data, list):
            tcs = data
        else:
            tcs = []
        if not isinstance(tcs, list):
            tcs = []

        # Round 15 F-E
        assertion_v = check_assertion_completeness(tcs)
        # Round 15 F-F（mode=error）
        fp_name_v = check_no_fp_name_field(tcs, mode="error")
        total = len(assertion_v) + len(fp_name_v)
        print(f"{path}: {total} violations")
        for v in assertion_v:
            print(f"  - [{v.get('type')}] id={v.get('id')} idx={v.get('index')}: {v.get('msg')}")
        for v in fp_name_v:
            print(f"  - [{v.get('type')}] id={v.get('id')} idx={v.get('index')}: {v.get('msg')}")
        total_violations += total
        if total:
            any_fail = True

    print(f"[--auto] total: {total_violations} violations across {len(json_paths)} file(s)")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
