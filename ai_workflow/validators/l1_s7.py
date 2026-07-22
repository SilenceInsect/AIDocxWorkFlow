#!/usr/bin/env python3
"""L1 校验器 — S7 审查报告产物（v16 T2 §3.7）。

校验范围：
  - review_report.json

重点：
  - reviewer_a / reviewer_b 顶层字段存在
  - recommendations 顶层字段存在
  - reviewer_a.total_cases >= 1
  - RCA 建议 ID 格式（M/S/C-NNN）
"""

from __future__ import annotations

import re

from ai_workflow.l1_format_validator import L1BaseValidator

__all__ = ["L1S7Validator"]


# S7 RCA 建议 ID 格式
RCA_ID_PAT = re.compile(r"^(M|S|C)-\d{3,}$")


class L1S7Validator(L1BaseValidator):
    """S7 审查报告产物 L1 校验器（v16 T2 §3.7）"""

    stage = "S7"

    def get_required_fields(self) -> list[str]:
        return []

    def get_id_fields(self) -> dict[str, str]:
        return {}

    def get_reference_fields(self) -> list[dict]:
        return []

    def validate_json_format(self, data: dict | list) -> list[dict]:
        errors = super().validate_json_format(data)
        if isinstance(data, dict):
            # reviewer_a 顶层字段
            rev_a = data.get("reviewer_a", {})
            if not isinstance(rev_a, dict):
                errors.append(self._standardize_error(
                    "MISSING_REQUIRED_STRUCT",
                    "reviewer_a 必须是 dict",
                    field="reviewer_a",
                ))
            else:
                if "total_cases" not in rev_a:
                    errors.append(self._standardize_error(
                        "MISSING_REQUIRED",
                        "reviewer_a.total_cases 缺失",
                        field="reviewer_a.total_cases",
                    ))
                elif not isinstance(rev_a.get("total_cases"), int):
                    errors.append(self._standardize_error(
                        "INVALID_FIELD_TYPE",
                        "reviewer_a.total_cases 必须是 int",
                        field="reviewer_a.total_cases",
                    ))
                elif rev_a["total_cases"] < 1:
                    errors.append(self._standardize_error(
                        "INVALID_CASE_COUNT",
                        f"reviewer_a.total_cases 应 >= 1，实际为 {rev_a['total_cases']}",
                        field="reviewer_a.total_cases",
                    ))
            # reviewer_b 顶层字段
            rev_b = data.get("reviewer_b", {})
            if not isinstance(rev_b, dict):
                errors.append(self._standardize_error(
                    "MISSING_REQUIRED_STRUCT",
                    "reviewer_b 必须是 dict",
                    field="reviewer_b",
                ))
            # recommendations 顶层字段
            recs = data.get("recommendations", {})
            if not isinstance(recs, dict):
                errors.append(self._standardize_error(
                    "MISSING_REQUIRED_STRUCT",
                    "recommendations 必须是 dict",
                    field="recommendations",
                ))
        return errors

    def validate_required_fields(self, data: dict | list) -> list[dict]:
        return []

    def validate_id_naming(self, data: dict | list) -> list[dict]:
        errors = []
        if isinstance(data, dict):
            # RCA 建议 ID 校验
            recs = data.get("recommendations", {})
            if isinstance(recs, dict):
                for category in ("must_fix", "should_fix", "could_fix"):
                    items = recs.get(category, [])
                    if not isinstance(items, list):
                        continue
                    for i, item in enumerate(items):
                        if not isinstance(item, dict):
                            continue
                        rca_id = str(item.get("id", "")).strip()
                        if rca_id and not RCA_ID_PAT.match(rca_id):
                            errors.append(self._standardize_error(
                                "INVALID_ID_FORMAT",
                                f"recommendations.{category}[{i}].id '{rca_id}' "
                                "不符合 M/S/C-NNN 格式",
                                field=f"recommendations.{category}[{i}].id",
                                id=rca_id,
                                expected="M/S/C-NNN",
                            ))
        return errors

    def validate_references(self, data: dict | list, context: dict | None) -> list[dict]:
        return []
