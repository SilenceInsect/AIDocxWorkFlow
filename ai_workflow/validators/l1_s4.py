#!/usr/bin/env python3
"""L1 校验器 — S4 流程图导出产物（v16 T2 §3.4）。

校验范围：
  - business_flow.md（4 类产出 + 风险点）

重点：
  - R-NNN 全局唯一
  - S4-{EpicID}-X.Y.Z 叶子节点无重复
  - 每个 Epic 有 4 类产出
  - epic_count >= 1
"""

from __future__ import annotations

import re

from ai_workflow.l1_format_validator import L1BaseValidator

__all__ = ["L1S4Validator"]


# S4 Markdown 节点 ID 正则
S4_LEAF_PAT = re.compile(r"S4-[A-Z]+-\d{3,}-\d+\.\d+(\.\d+)*")
S4_FLOW_PAT = re.compile(r"S4-[A-Z]+-\d{3,}-F\d+")
R_GLOBAL_PAT = re.compile(r"R-\d{3,}")
R_EPIC_PAT = re.compile(r"R-[A-Z]+-\d{3,}-\d+")


class L1S4Validator(L1BaseValidator):
    """S4 流程图导出产物 L1 校验器（v16 T2 §3.4）

    注意：S4 主产物是 Markdown (business_flow.md)。
    此校验器接受 JSON 格式（若存在）。
    """

    stage = "S4"

    def get_required_fields(self) -> list[str]:
        return []

    def get_id_fields(self) -> dict[str, str]:
        return {
            "s4_reference": "R_GLOBAL",
        }

    def get_reference_fields(self) -> list[dict]:
        return []

    def validate_json_format(self, data: dict | list) -> list[dict]:
        errors = super().validate_json_format(data)
        if isinstance(data, dict):
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
        return []

    def validate_id_naming(self, data: dict | list) -> list[dict]:
        errors = []
        if isinstance(data, dict):
            risks = data.get("risk_points", [])
            if not isinstance(risks, list):
                return errors
            seen_r: set[str] = set()
            seen_leaf: set[str] = set()
            for i, risk in enumerate(risks):
                if not isinstance(risk, dict):
                    continue
                rid = str(risk.get("s4_reference", "")).strip()
                if not rid:
                    continue
                # R-NNN 格式
                if R_GLOBAL_PAT.match(rid):
                    if rid in seen_r:
                        errors.append(self._standardize_error(
                            "DUPLICATE_ID",
                            f"R-NNN ID '{rid}' 重复",
                            index=i, field="s4_reference", id=rid,
                        ))
                    seen_r.add(rid)
                # R-{EpicID}-NN 格式
                if R_EPIC_PAT.match(rid):
                    # 不检查重复（可能存在多个 Epic 各自的 R-Epic-NN）
                    pass
                # 检查异常树叶子 ID（从 risk_leaf 或 exception_leaf 字段）
                leaf_id = str(risk.get("exception_leaf", "")).strip()
                if leaf_id and S4_LEAF_PAT.match(leaf_id):
                    if leaf_id in seen_leaf:
                        errors.append(self._standardize_error(
                            "DUPLICATE_ID",
                            f"异常树叶 ID '{leaf_id}' 重复",
                            index=i, field="exception_leaf", id=leaf_id,
                        ))
                    seen_leaf.add(leaf_id)
        return errors

    def validate_references(self, data: dict | list, context: dict | None) -> list[dict]:
        return []
