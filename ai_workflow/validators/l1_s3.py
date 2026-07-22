#!/usr/bin/env python3
"""L1 校验器 — S3 原型导出产物（v16 T2 §3.3）。

校验范围：
  - prototype.md（Mermaid 页面流图 + PAGE-XXX 节点）

重点：
  - Mermaid 流程图语法合法（检查 ```mermaid 块）
  - PAGE-{EpicID}-{NN} 格式节点存在于原型中
  - 页面数 >= 1
"""

from __future__ import annotations

import re

from ai_workflow.l1_format_validator import L1BaseValidator

__all__ = ["L1S3Validator"]


# Mermaid 代码块正则
MERMAID_BLOCK = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)


class L1S3Validator(L1BaseValidator):
    """S3 原型导出产物 L1 校验器（v16 T2 §3.3）

    注意：S3 主产物是 Markdown (prototype.md)，不是 JSON。
    此校验器接受 JSON 格式的 prototype.json（若存在）。
    对于 .md 文件，请使用独立脚本或在 Markdown 审查阶段处理。
    """

    stage = "S3"

    def get_required_fields(self) -> list[str]:
        return []

    def get_id_fields(self) -> dict[str, str]:
        return {}

    def get_reference_fields(self) -> list[dict]:
        return []

    def validate_json_format(self, data: dict | list) -> list[dict]:
        errors = super().validate_json_format(data)
        if isinstance(data, dict):
            # 检查 pages 数组
            pages = data.get("pages", [])
            if not isinstance(pages, list):
                errors.append(self._standardize_error(
                    "INVALID_PAGES",
                    "pages 字段必须是数组",
                    field="pages",
                ))
            elif len(pages) == 0:
                errors.append(self._standardize_error(
                    "EMPTY_PAGES",
                    "pages 数组不能为空",
                    field="pages",
                ))
        return errors

    def validate_required_fields(self, data: dict | list) -> list[dict]:
        return []

    def validate_id_naming(self, data: dict | list) -> list[dict]:
        errors = []
        if isinstance(data, dict):
            pages = data.get("pages", [])
            seen_pages: set[str] = set()
            for i, page in enumerate(pages):
                if not isinstance(page, dict):
                    continue
                page_id = str(page.get("page_id", "")).strip()
                if not page_id:
                    continue
                if page_id in seen_pages:
                    errors.append(self._standardize_error(
                        "DUPLICATE_ID",
                        f"PAGE ID '{page_id}' 重复",
                        index=i, field="page_id", id=page_id,
                    ))
                seen_pages.add(page_id)
                pattern = re.compile(r"^PAGE-[A-Z]+-\d{3,}-\d{2}$")
                if not pattern.match(page_id):
                    errors.append(self._standardize_error(
                        "INVALID_ID_FORMAT",
                        f"page_id '{page_id}' 不符合 PAGE-{{EpicID}}-{{NN}} 格式",
                        index=i, field="page_id", id=page_id,
                        expected="PAGE-{EpicID}-{NN}",
                    ))
        return errors

    def validate_references(self, data: dict | list, context: dict | None) -> list[dict]:
        return []
