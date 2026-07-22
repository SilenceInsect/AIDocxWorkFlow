#!/usr/bin/env python3
"""L1 校验器 — S2 需求拆解产物（v16 T2 §3.2）。

校验范围：
  - backlog.json（Epic/Story 层）
  - requirement_objects.json（OBJ/FP 层）

重点：
  - Epic/Story/OBJ/FP ID 命名规范
  - feature_points[] 非空（禁止 fp_count）
  - meta.stage == "S2"
"""

from __future__ import annotations

from ai_workflow.l1_format_validator import L1BaseValidator

__all__ = ["L1S2Validator"]


class L1S2Validator(L1BaseValidator):
    """S2 需求拆解产物 L1 校验器（v16 T2 §3.2）"""

    stage = "S2"
    array_keys = ["requirement_objects"]

    def get_required_fields(self) -> list[str]:
        # OBJ 级别必填字段（9 字段新范式）
        return [
            "obj_id",
            "obj_name",
            "belong_module",
            "feature_points",   # 必须是非空数组（禁止 fp_count）
        ]

    def get_id_fields(self) -> dict[str, str]:
        return {
            "obj_id": "OBJ",
            "fp_id": "FP",
        }

    def get_reference_fields(self) -> list[dict]:
        # 无跨文件引用（S2 是生产者）
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
            stage_val = meta.get("stage", "")
            if stage_val and stage_val != "S2":
                errors.append(self._standardize_error(
                    "INVALID_STAGE_TAG",
                    f"meta.stage 应为 'S2'，实际为 '{stage_val}'",
                    field="meta.stage",
                    expected="S2",
                ))
            # summary.epic_count >= 1
            summary = data.get("summary", {})
            if isinstance(summary, dict):
                epic_count = summary.get("epic_count", 0)
                if epic_count < 1:
                    errors.append(self._standardize_error(
                        "INVALID_EPIC_COUNT",
                        f"summary.epic_count 应 >= 1，实际为 {epic_count}",
                        field="summary.epic_count",
                    ))
        return errors

    def validate_required_fields(self, data: dict | list) -> list[dict]:
        errors = super().validate_required_fields(data)
        if isinstance(data, dict):
            # 额外检查 feature_points 非空（禁止 fp_count）
            objs = data.get("requirement_objects", [])
            for i, obj in enumerate(objs):
                if not isinstance(obj, dict):
                    continue
                fps = obj.get("feature_points")
                if fps is None:
                    errors.append(self._standardize_error(
                        "MISSING_REQUIRED",
                        "feature_points 字段缺失（禁止使用 fp_count）",
                        index=i, field="feature_points",
                        id=obj.get("obj_id", f"#{i}"),
                    ))
                elif not isinstance(fps, list) or len(fps) == 0:
                    errors.append(self._standardize_error(
                        "MISSING_REQUIRED",
                        "feature_points 数组不能为空",
                        index=i, field="feature_points",
                        id=obj.get("obj_id", f"#{i}"),
                    ))
        return errors
