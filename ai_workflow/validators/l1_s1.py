#!/usr/bin/env python3
"""L1 校验器 — S1 需求评审产物（v16 T2 §3.1）。

校验范围：
  - review_report.json（5维度评分）
  - requirement_objects.json（需求对象）

不校验：
  - 终版需求.md（Markdown，无需格式校验）
  - clarification_checklist.md（Markdown）
"""

from __future__ import annotations

from typing import Any

from ai_workflow.l1_format_validator import L1BaseValidator

__all__ = ["L1S1Validator"]


class L1S1Validator(L1BaseValidator):
    """S1 需求评审产物 L1 校验器（v16 T2 §3.1）"""

    stage = "S1"

    # 支持的数组键名（requirement_objects.json 用 requirement_objects[]）
    array_keys = ["requirement_objects"]

    def get_required_fields(self) -> list[str]:
        return [
            "meta",
        ]

    def get_id_fields(self) -> dict[str, str]:
        # S1 无固定 ID 字段，用 meta 代替
        return {}

    def get_reference_fields(self) -> list[dict]:
        # S1 产物无跨文件引用需求
        return []

    def validate_json_format(self, data: dict | list) -> list[dict]:
        errors = super().validate_json_format(data)
        if isinstance(data, dict):
            meta = data.get("meta", {})
            if not isinstance(meta, dict):
                errors.append(self._standardize_error(
                    "INVALID_META",
                    "meta 字段必须是 dict",
                    field="meta",
                ))
            # meta.stage 必须为 S1
            stage_val = meta.get("stage", "")
            if stage_val and stage_val != "S1":
                errors.append(self._standardize_error(
                    "INVALID_STAGE_TAG",
                    f"meta.stage 应为 'S1'，实际为 '{stage_val}'",
                    field="meta.stage",
                    expected="S1",
                ))
        return errors

    def validate_required_fields(self, data: dict | list) -> list[dict]:
        errors = super().validate_required_fields(data)
        if isinstance(data, dict):
            # requirement_objects 数组非空
            objs = data.get("requirement_objects", [])
            if not isinstance(objs, list) or len(objs) == 0:
                errors.append(self._standardize_error(
                    "MISSING_REQUIRED",
                    "requirement_objects 数组不能为空",
                    field="requirement_objects",
                ))
        return errors
