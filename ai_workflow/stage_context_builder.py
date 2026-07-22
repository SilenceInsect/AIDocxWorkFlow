#!/usr/bin/env python3
"""AIDocxWorkFlow 阶段上下文构建器。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_workflow.recurring_failures import load_relevant_failures
from ai_workflow.runtime_contracts import (
    GLOBAL_RULES,
    ROOT,
    STAGE_RULE_FILES,
    STAGE_SKILL_DIRS,
    get_stage_contract,
    get_stage_dir,
    resolve_contract_path,
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _short_preview(text: str, limit: int = 220) -> str:
    cleaned = " ".join(text.split())
    return cleaned[:limit]


def _build_material_entry(path_str: str) -> dict[str, Any]:
    path = ROOT / path_str
    text = _read_text(path)
    return {
        "path": path_str,
        "exists": path.exists(),
        "preview": _short_preview(text),
    }


def _resolve_input_status(
    stage: str,
    req_name: str,
    version: str,
    project_name: str | None = None,
) -> list[dict[str, Any]]:
    contract = get_stage_contract(stage)
    statuses = []
    for item in contract.get("upstream_inputs", []):
        resolved = resolve_contract_path(item["path"], req_name, version, project_name=project_name)
        exists = resolved.is_dir() if item.get("kind") == "dir" else resolved.exists()
        statuses.append({
            **item,
            "resolved_path": str(resolved),
            "exists": exists,
        })
    return statuses


def _render_stage_context_md(context: dict[str, Any]) -> str:
    lines = [
        f"# {context['meta']['stage']} 阶段上下文包\n\n",
        f"- 需求：`{context['meta']['req_name']}`\n",
        f"- 项目：`{context['meta'].get('project_name') or '-'}`\n",
        f"- 版本：`{context['meta']['version']}`\n",
        f"- 生成时间：`{context['meta']['generated_at']}`\n\n",
        "## 全局任务\n\n",
        f"- 主目标：{context['global_mission']['primary_goal']}\n",
        f"- 反模式：{', '.join(context['global_mission']['anti_patterns'])}\n\n",
        "## 必读材料\n\n",
        "| 路径 | 存在 | 说明 |\n|---|---|---|\n",
    ]
    for item in context["must_read"]:
        lines.append(f"| {item['path']} | {'Y' if item['exists'] else 'N'} | {item['preview']} |\n")

    lines.extend([
        "\n## 上游输入状态\n\n",
        "| 键 | 路径 | 必需 | 存在 |\n|---|---|---|---|\n",
    ])
    for item in context["input_material_status"]:
        lines.append(
            f"| {item['key']} | {item['resolved_path']} | "
            f"{'Y' if item['required'] else 'N'} | {'Y' if item['exists'] else 'N'} |\n"
        )

    lines.extend([
        "\n## 下游契约\n\n",
        f"- 下游阶段：`{context['downstream_contract'].get('consumer_stage', '-')}`\n",
        f"- 必备产物：{', '.join(context['required_outputs'])}\n",
        f"- Gate：{', '.join(context['gates'])}\n\n",
        "## 近期重复失败模式\n\n",
    ])
    for item in context["historical_failures"]:
        lines.append(
            f"- `{item.get('id')}` {item.get('pattern')}: "
            f"{item.get('symptom')} | prevent_by={item.get('prevent_by', [])}\n"
        )

    return "".join(lines)


def build_stage_context(
    stage: str,
    req_name: str,
    version: str = "v1.0",
    project_name: str | None = None,
    *,
    persist: bool = True,
) -> dict[str, Any]:
    contract = get_stage_contract(stage)
    stage_dir = get_stage_dir(req_name, stage, version)
    stage_dir.mkdir(parents=True, exist_ok=True)

    must_read = [_build_material_entry(path) for path in GLOBAL_RULES]
    if stage in STAGE_RULE_FILES:
        must_read.append(_build_material_entry(STAGE_RULE_FILES[stage]))
    if stage in STAGE_SKILL_DIRS:
        must_read.append(_build_material_entry(STAGE_SKILL_DIRS[stage]))

    context = {
        "meta": {
            "stage": stage,
            "req_name": req_name,
            "project_name": project_name,
            "version": version,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "stage_dir": str(stage_dir),
        },
        "global_mission": {
            "primary_goal": contract.get(
                "primary_goal",
                "需求覆盖最大化，显式报告未覆盖点，避免局部最优。",
            ),
            "anti_patterns": contract.get(
                "anti_patterns",
                ["coding_mindset_shrink", "silent_omission"],
            ),
        },
        "must_read": must_read,
        "input_material_status": _resolve_input_status(stage, req_name, version, project_name),
        "upstream_contract": contract.get("upstream_inputs", []),
        "current_stage_contract": {
            "stage": stage,
            "primary_goal": contract.get("primary_goal", ""),
            "must_read": contract.get("must_read", []),
        },
        "downstream_contract": contract.get("downstream_contract", {}),
        "historical_failures": load_relevant_failures(stage, limit=3),
        "required_outputs": contract.get("required_outputs", []),
        "gates": contract.get("gates", []),
    }

    if persist:
        json_path = stage_dir / "stage_context.json"
        md_path = stage_dir / "stage_context.md"
        json_path.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(_render_stage_context_md(context), encoding="utf-8")
        context["context_files"] = {
            "json": str(json_path),
            "md": str(md_path),
        }

    return context
