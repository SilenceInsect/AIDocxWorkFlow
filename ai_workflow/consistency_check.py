"""
AIDocxWorkFlow — SKILL ↔ Rule 一致性检查器

检查阶段 SKILL.md 与阶段 Rule 文件（STAGE_S*.mdc）之间的声明式约束是否对齐。
仅检查声明式约束（文件路径、字段名、枚举值、输出路径），不检查内容质量。

调用方式：
    from ai_workflow.consistency_check import run_consistency_check
    result = run_consistency_check(stage="s5")

    # CLI
    python -m ai_workflow.consistency_check s5
    python -m ai_workflow.consistency_check --all
    python -m ai_workflow.consistency_check --fix
"""

from __future__ import annotations

import json
import re
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ai_workflow.runtime_contracts import get_stage_contract, get_stage_dir

# 工作区根目录（ai_workflow 的父目录）
_WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
_RULES_DIR = _WORKSPACE_ROOT / ".cursor" / "rules"
_SKILLS_DIR = _WORKSPACE_ROOT / ".cursor" / "skills"
_MODULES_FILE = _WORKSPACE_ROOT / ".cursor" / "MODULES.md"

# 阶段 → (skill_dir_name, rule_file_name, skill_section_hint)
_STAGE_MAP: dict[str, dict[str, str]] = {
    "s1": {
        "skill_dir": "aidocx-s1-review",
        "rule_file": "STAGE_S1_REVIEW.mdc",
        "section_hint": "S1",
    },
    "s1_5": {
        "skill_dir": "aidocx-s1-5-clarification",
        "rule_file": "STAGE_S1.5 Clarification.mdc",
        "section_hint": "S1.5",
    },
    "s2": {
        "skill_dir": "aidocx-s2-breakdown",
        "rule_file": "STAGE_S2_BREAKDOWN.mdc",
        "section_hint": "S2",
    },
    "s2_5": {
        "skill_dir": "aidocx-s2-5-iteration",
        "rule_file": "STAGE_S2_5_ITERATION.mdc",
        "section_hint": "S2.5",
    },
    "s3": {
        "skill_dir": "aidocx-s3-prototype",
        "rule_file": "STAGE_S3_PROTOTYPE.mdc",
        "section_hint": "S3",
    },
    "s4": {
        "skill_dir": "aidocx-s4-flowchart",
        "rule_file": "STAGE_S4_FLOWCHART.mdc",
        "section_hint": "S4",
    },
    "s5": {
        "skill_dir": "aidocx-s5-test-points",
        "rule_file": "STAGE_S5_TEST_POINTS.mdc",
        "section_hint": "S5",
    },
    "s6": {
        "skill_dir": "aidocx-s6-test-cases",
        "rule_file": "STAGE_S6_TEST_CASES.mdc",
        "section_hint": "S6",
    },
    "s7": {
        "skill_dir": "aidocx-s7-review",
        "rule_file": "STAGE_S7_REVIEW.mdc",
        "section_hint": "S7",
    },
    "s8": {
        "skill_dir": "aidocx-s8-self-iteration",
        "rule_file": "STAGE_S8_SELF_ITERATION.mdc",
        "section_hint": "S8",
    },
}

# 全局缓存：每阶段只检查一次
_CHECK_CACHE: dict[str, dict[str, Any]] = {}

# 8 模块枚举（从 MODULES.md §1 总表）
_MODULE_ENUMS = {
    "CONFIG", "UI", "BIZ", "AUX", "LINK",
    "SPECIAL", "LOG", "HINT",
}

# TP JSON 必填字段（S5/S6/S7 核心）
_TP_JSON_REQUIRED_FIELDS = {
    "tp_id", "module", "test_point_type", "test_type_subclass",
    "description", "s4_reference", "boundary", "is_assumed", "applies_rule",
}

# OBJ 必填字段（S2）
_OBJ_REQUIRED_FIELDS = {
    "obj_id", "obj_name", "belong_module", "scene",
    "input", "normal_flow", "exception_flow",
    "data_change", "output_display", "verify_method",
}

# TC 字段（S6）
_TC_REQUIRED_FIELDS = {
    "case_id", "模块", "用例描述", "功能描述",
    "前置条件", "操作步骤", "预期结果", "优先级", "用例状态",
}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _read_file(path: Path) -> str:
    """读取文件内容，文件不存在返回空字符串。"""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _extract_yaml_frontmatter(text: str) -> str:
    """提取 --- ... --- 之间的 YAML frontmatter 块。"""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return ""
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return ""


def _extract_skill_required_materials(text: str) -> list[dict[str, str]]:
    """从 SKILL.md §1.4 中提取必读材料清单。
    返回列表，每个元素含 {id, material, path, reason, mandatory}
    """
    materials = []
    # 定位 §1.4 节
    section_match = re.search(r"## §1\.4[^\n]*\n(.*?)(?=\n## |\n# |\Z)", text, re.DOTALL)
    if not section_match:
        return materials

    section = section_match.group(1)

    # 解析 markdown 表格（# | 材料 | 路径 | 必读原因）
    table_pattern = re.compile(
        r"^\|\s*#\s*\|([^|]+)\|([^|]+)\|([^|]+)\|",
        re.MULTILINE,
    )
    for m in table_pattern.finditer(section):
        num = m.group(1).strip()
        material = m.group(2).strip()
        path_raw = m.group(3).strip()
        if num and material and path_raw and num not in ("#", ""):
            materials.append({
                "id": num,
                "material": material,
                "path": path_raw,
                "mandatory": "强制" in material or "必须" in material,
            })

    return materials


def _extract_rule_required_materials(text: str, stage: str) -> list[dict[str, str]]:
    """从 Rule 文件（STAGE_S*.mdc）中提取必读材料清单。
    支持：§1.4 LLM 必读材料 / §必读材料 两种节名。
    """
    materials = []
    # 匹配两种节名模式
    section_pattern = re.compile(
        r"(?:## §1\.4|## §必读材料)[^\n]*\n(.*?)(?=\n## |\n# |\Z)",
        re.DOTALL,
    )
    section_match = section_pattern.search(text)
    if not section_match:
        return materials

    section = section_match.group(1)

    table_pattern = re.compile(
        r"^\|\s*[^|]*\|\s*([^|]+)\|([^|]+)\|([^|]*)\|",
        re.MULTILINE,
    )
    for m in table_pattern.finditer(section):
        label = m.group(1).strip()
        material = m.group(2).strip()
        reason = m.group(3).strip()
        if label and label not in ("#", "材料", "Material", "项目"):
            materials.append({
                "label": label,
                "material": material,
                "reason": reason,
            })

    return materials


def _extract_output_paths(text: str, direction: str = "success") -> list[str]:
    """从文件内容中提取输出路径（Markdown 代码块中的路径）。"""
    paths = []
    # 匹配路径格式：workflow_assets/... 或 `path/to/file`
    path_pattern = re.compile(
        r"`(workflow_assets/[^`\n]+)`"
    )
    # 也匹配 "路径：`xxx`" 格式
    labeled_pattern = re.compile(
        r"(?:路径|路径：|路径:|Output path|输出路径)[：`\s]*(workflow_assets/[^\s`\n]+)",
        re.IGNORECASE,
    )

    for m in path_pattern.finditer(text):
        path = m.group(1).strip()
        if path:
            paths.append(path)

    for m in labeled_pattern.finditer(text):
        path = m.group(1).strip()
        if path and path not in paths:
            paths.append(path)

    return paths


def _extract_json_field_names(text: str, section_hint: str = "") -> dict[str, list[str]]:
    """从文件内容中提取 JSON 字段名。
    返回 {section_name: [field_name, ...]}
    """
    result: dict[str, list[str]] = {}
    # 匹配 JSON 代码块
    json_blocks = re.findall(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    for block in json_blocks:
        # 提取顶层字段名（简单方法：匹配 "key": 或 "key": {）
        # 用正则匹配 "key":
        field_matches = re.findall(r'"(\w+)":\s*(?:\{|[^"\n])', block)
        if field_matches:
            section_key = f"json_{len(result)}"
            result[section_key] = list(set(field_matches))
    return result


def _extract_field_names_from_tables(text: str) -> list[str]:
    """从 Markdown 表格中提取字段名（第三列）。"""
    fields = []
    # 匹配 "字段" 表（| 字段 | 含义 | ...）
    field_table_pattern = re.compile(
        r"^\|\s*([^|]+?)\s*\|",
        re.MULTILINE,
    )
    for m in field_table_pattern.finditer(text):
        field = m.group(1).strip()
        if field and field not in ("字段", "字段名", "字段名称", "Field", "Key", "#", "---"):
            fields.append(field)
    return fields


def _extract_module_enums(text: str) -> set[str]:
    """从文件内容中提取模块枚举值（CONFIG/UI/BIZ 等）。"""
    found = set()
    for mod in _MODULE_ENUMS:
        # 匹配完整词（前后有边界）
        pattern = re.compile(rf"\b{mod}\b")
        if pattern.search(text):
            found.add(mod)
    return found


def _extract_tp_type_enums(text: str) -> set[str]:
    """从文件内容中提取 test_point_type 枚举值。"""
    enums = set()
    # 匹配 `POSITIVE` / `BOUNDARY` / `NEGATIVE` / `EXCEPTION`
    enum_pattern = re.compile(r"`(POSITIVE|BOUNDARY|NEGATIVE|EXCEPTION)`")
    for m in enum_pattern.finditer(text):
        enums.add(m.group(1))
    return enums


def _normalize_path(path_str: str) -> str:
    """标准化路径：去除 <req_name> / <version> 等变量，保留结构。"""
    normalized = path_str.strip()
    # 替换 <req_name> / <version> 等变量为占位符
    normalized = re.sub(r"<req_name>", "<REQ>", normalized)
    normalized = re.sub(r"<requirement_name>", "<REQ>", normalized)
    normalized = re.sub(r"<version>", "<VER>", normalized)
    normalized = re.sub(r"<Module>", "<MOD>", normalized)
    normalized = re.sub(r"<MOD>", "<MODULE>", normalized)
    # 去除多余空格
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _paths_equivalent(path1: str, path2: str) -> bool:
    """判断两条路径是否语义等价（忽略变量名差异）。"""
    n1 = _normalize_path(path1)
    n2 = _normalize_path(path2)
    return n1 == n2


def _section_contains(text: str, keyword: str) -> bool:
    """判断文件中是否包含某关键词（用于快速判断必读材料是否存在）。"""
    return keyword.lower() in text.lower()


# ---------------------------------------------------------------------------
# 一致性检查核心
# ---------------------------------------------------------------------------

def _check_type_a_materials(
    stage: str,
    skill_text: str,
    rule_text: str,
    stage_map: dict[str, str],
) -> list[dict[str, Any]]:
    """类型 A：必读材料清单对齐（SKILL §1.4 ↔ Rule 必读材料节）。"""
    issues: list[dict[str, Any]] = []

    skill_materials = _extract_skill_required_materials(skill_text)
    rule_materials = _extract_rule_required_materials(rule_text, stage)

    # 构建 Rule 材料集合（用于快速查询）
    rule_material_set = set()
    for rm in rule_materials:
        rule_material_set.add(rm["material"].strip())

    # A1: SKILL §1.4 列出的材料，Rule 是否有对应
    for sm in skill_materials:
        material_name = sm["material"].strip()
        # 在 Rule 材料中查找匹配（模糊匹配，忽略序号）
        found = False
        for rm in rule_materials:
            if material_name in rm["material"] or rm["material"] in material_name:
                found = True
                break
        if not found:
            # 检查 Rule 中是否包含该材料的关键词（如文件名）
            # 提取材料名中的关键标识（如 "knowledge/public/module_templates/"）
            has_keyword = False
            for rm in rule_materials:
                reason = rm.get("reason", "")
                # 如果 SKILL 材料路径中的关键部分出现在 Rule 的材料名或原因中
                key_parts = [p for p in material_name.split("/") if len(p) > 3]
                for part in key_parts:
                    if part in rm["material"] or part in reason:
                        has_keyword = True
                        break

            if not has_keyword:
                issues.append({
                    "type": "A1_missing_in_rule",
                    "severity": "warn",
                    "location": f"{stage_map['skill_dir']}/SKILL.md §1.4 {sm.get('id', '')}",
                    "rule_location": f"{stage_map['rule_file']} 必读材料节",
                    "description": (
                        f"SKILL §1.4 列出了 '{material_name}'，"
                        f"但 Rule 必读材料节中未找到对应项"
                    ),
                    "skill_item": material_name,
                })

    # A2: Rule 中标注"必须读取"的材料，SKILL §1.4 是否列出
    # 构建 SKILL 材料名集合
    skill_material_set = {sm["material"].strip() for sm in skill_materials}
    for rm in rule_materials:
        rule_mat = rm["material"].strip()
        # 检查是否在 SKILL 中出现（模糊匹配）
        found_in_skill = any(
            rule_mat in sm or sm in rule_mat
            for sm in skill_material_set
        )
        if not found_in_skill:
            # 提取关键路径部分
            key_parts = [p for p in rule_mat.split("/") if len(p) > 3]
            found_keyword = any(
                part in sm for sm in skill_material_set for part in key_parts
            )
            if not found_keyword and key_parts:
                issues.append({
                    "type": "A2_missing_in_skill",
                    "severity": "warn",
                    "location": f"{stage_map['rule_file']} 必读材料节",
                    "rule_location": f"{stage_map['skill_dir']}/SKILL.md §1.4",
                    "description": (
                        f"Rule 列出了 '{rule_mat}'，"
                        f"但 SKILL §1.4 中未找到对应项"
                    ),
                    "rule_item": rule_mat,
                })

    return issues


def _check_type_b_outputs(
    stage: str,
    skill_text: str,
    rule_text: str,
    stage_map: dict[str, str],
) -> list[dict[str, Any]]:
    """类型 B：输出路径对齐（SKILL ↔ Rule）。"""
    issues: list[dict[str, Any]] = []

    skill_paths = _extract_output_paths(skill_text)
    rule_paths = _extract_output_paths(rule_text)

    # 检查 SKILL 路径是否在 Rule 中有对应
    for sp in skill_paths:
        sp_normalized = _normalize_path(sp)
        found = any(_normalize_path(rp) == sp_normalized for rp in rule_paths)
        if not found:
            issues.append({
                "type": "B1_output_path_skill_only",
                "severity": "warn",
                "location": f"{stage_map['skill_dir']}/SKILL.md",
                "rule_location": f"{stage_map['rule_file']}",
                "description": (
                    f"SKILL 中声明了输出路径 '{sp}'，"
                    f"但 Rule 中未找到语义相同的路径声明"
                ),
                "skill_path": sp,
            })

    # 检查 Rule 路径是否在 SKILL 中有对应
    for rp in rule_paths:
        rp_normalized = _normalize_path(rp)
        found = any(_normalize_path(sp) == rp_normalized for sp in skill_paths)
        if not found:
            issues.append({
                "type": "B2_output_path_rule_only",
                "severity": "warn",
                "location": f"{stage_map['rule_file']}",
                "rule_location": f"{stage_map['skill_dir']}/SKILL.md",
                "description": (
                    f"Rule 中声明了输出路径 '{rp}'，"
                    f"但 SKILL 中未找到语义相同的路径声明"
                ),
                "rule_path": rp,
            })

    return issues


def _check_type_c_fields(
    stage: str,
    skill_text: str,
    rule_text: str,
    stage_map: dict[str, str],
) -> list[dict[str, Any]]:
    """类型 C：字段名规范对齐（SKILL §push/字段规范 ↔ Rule 字段规范）。"""
    issues: list[dict[str, Any]] = []

    # 从 SKILL 提取 JSON 字段（S5/S6/S7 重点检查 TP 字段）
    skill_fields = _extract_json_field_names(skill_text)

    # 从 Rule 提取字段名
    rule_fields = _extract_field_names_from_tables(rule_text)

    # S5 特殊：检查 TP 必填字段
    if stage in ("s5",):
        skill_all_fields: set[str] = set()
        for fields in skill_fields.values():
            skill_all_fields.update(fields)

        # 检查 SKILL 中声明的 TP 字段与 Rule 字段规范
        # 提取 SKILL §1.6.5 中的必填字段列表
        field_enum_match = re.search(
            r"## §1\.6\.5.*?(?=\n## |\n# |\Z)",
            skill_text,
            re.DOTALL,
        )
        if field_enum_match:
            field_list_text = field_enum_match.group(0)
            # 提取 `- field_name` 或 `field_name` 格式
            declared_fields = re.findall(r"`(\w+)`", field_list_text)
            for df in declared_fields:
                if df not in rule_fields and df not in skill_all_fields:
                    issues.append({
                        "type": "C1_field_declaration_mismatch",
                        "severity": "warn",
                        "location": f"{stage_map['skill_dir']}/SKILL.md §1.6.5",
                        "rule_location": f"{stage_map['rule_file']} 字段规范",
                        "description": (
                            f"SKILL §1.6.5 中声明的字段 '{df}' "
                            f"在 Rule 字段规范中未找到对应"
                        ),
                        "field": df,
                    })

    # S2 特殊：检查 OBJ 字段
    if stage in ("s2",):
        # 提取 OBJ 字段（从 SKILL §1.5.5）
        obj_field_match = re.search(
            r"## §1\.5\.5[^\n]*\n(.*?)(?=\n## |\n# |\Z)",
            skill_text,
            re.DOTALL,
        )
        if obj_field_match:
            field_list_text = obj_field_match.group(0)
            declared_fields = re.findall(r"`(\w+)`", field_list_text)
            for df in declared_fields:
                if df not in rule_fields:
                    issues.append({
                        "type": "C2_obj_field_mismatch",
                        "severity": "warn",
                        "location": f"{stage_map['skill_dir']}/SKILL.md §1.5.5",
                        "rule_location": f"{stage_map['rule_file']} 字段规范",
                        "description": (
                            f"SKILL §1.5.5 OBJ 字段 '{df}' "
                            f"在 Rule 字段规范中未找到"
                        ),
                        "field": df,
                    })

    # 通用：检查字段名拼写一致性
    for sf_list in skill_fields.values():
        for sf in sf_list:
            # 查找 Rule 中是否有相近字段名（用于检测拼写差异）
            for rf in rule_fields:
                if rf != sf and (
                    (sf.lower() in rf.lower() and len(sf) > 3)
                    or (rf.lower() in sf.lower() and len(rf) > 3)
                ):
                    issues.append({
                        "type": "C3_field_spelling_variants",
                        "severity": "warn",
                        "location": f"{stage_map['skill_dir']}/SKILL.md",
                        "rule_location": f"{stage_map['rule_file']} 字段规范",
                        "description": (
                            f"SKILL 与 Rule 中存在相近字段名："
                            f"'{sf}' vs '{rf}'（可能是拼写不一致）"
                        ),
                        "skill_field": sf,
                        "rule_field": rf,
                    })

    return issues


def _check_type_d_modules(
    stage: str,
    skill_text: str,
    rule_text: str,
    stage_map: dict[str, str],
) -> list[dict[str, Any]]:
    """类型 D：模块枚举对齐（SKILL ↔ Rule ↔ MODULES.md）。"""
    issues: list[dict[str, Any]] = []

    skill_modules = _extract_module_enums(skill_text)
    rule_modules = _extract_module_enums(rule_text)

    # D1: SKILL 模块是否在 Rule 中出现
    for mod in skill_modules:
        if mod not in rule_modules:
            issues.append({
                "type": "D1_module_skill_only",
                "severity": "warn",
                "location": f"{stage_map['skill_dir']}/SKILL.md",
                "rule_location": f"{stage_map['rule_file']}",
                "description": (
                    f"SKILL 中引用了模块 '{mod}'，"
                    f"但 Rule 中未找到该模块枚举"
                ),
                "module": mod,
            })

    # D2: Rule 模块是否在 SKILL 中出现
    for mod in rule_modules:
        if mod not in skill_modules:
            issues.append({
                "type": "D2_module_rule_only",
                "severity": "warn",
                "location": f"{stage_map['rule_file']}",
                "rule_location": f"{stage_map['skill_dir']}/SKILL.md",
                "description": (
                    f"Rule 中引用了模块 '{mod}'，"
                    f"但 SKILL 中未找到该模块枚举"
                ),
                "module": mod,
            })

    return issues


def _load_modules_enums() -> set[str]:
    """加载 MODULES.md §1 总表中的模块枚举。"""
    text = _read_file(_MODULES_FILE)
    return _extract_module_enums(text)


def _check_runtime_assets(stage: str, req_name: str, version: str, phase: str = "runtime") -> list[dict[str, Any]]:
    """检查运行时资产是否齐备。"""
    issues: list[dict[str, Any]] = []
    stage_upper = stage.upper().replace("_", ".")
    contract = get_stage_contract(stage_upper)
    if not contract:
        return issues

    stage_dir = get_stage_dir(req_name, stage_upper, version)

    runtime_required = ["stage_context.json", "read_ack.json"]
    if phase == "postflight":
        runtime_required.append("preflight_gate.json")
        if stage_upper in {"S5", "S6"}:
            runtime_required.extend(["coverage_ledger.json", "omission_ledger.json"])
        if stage_upper == "S7":
            runtime_required.extend([
                "review_snapshot.json",
                "review_snapshot.md",
                "review_report.json",
                "review_report.md",
            ])

    for name in runtime_required:
        path = stage_dir / name
        if not path.exists():
            issues.append({
                "type": "runtime_asset_missing",
                "severity": "error",
                "runtime_severity": "P0_BLOCK",
                "location": str(path),
                "description": f"缺少运行时资产：{name}",
                "repair_hint": f"先执行对应阶段 gate/产出逻辑，补齐 {name}",
            })

    return issues


# ---------------------------------------------------------------------------
# 主检查函数
# ---------------------------------------------------------------------------

def run_consistency_check(
    stage: str,
    req_name: str | None = None,
    version: str = "v1.0",
    phase: str = "runtime",
) -> dict[str, Any]:
    """
    对指定阶段执行一致性检查。

    参数：
        stage: 阶段标识符（s1 / s1_5 / s2 / s2_5 / s3 / s4 / s5 / s6 / s7 / s8）

    返回：
        dict，包含：
            - stage: str
            - checked_at: str (ISO 8601)
            - passed: bool
            - cache_hit: bool
            - issues: list[dict]
            - summary: str
    """
    # 检查缓存
    cache_key = f"{stage}:{req_name or ''}:{version}:{phase}"
    if cache_key in _CHECK_CACHE:
        result = _CHECK_CACHE[cache_key].copy()
        result["cache_hit"] = True
        return result

    if stage not in _STAGE_MAP:
        return {
            "stage": stage,
            "error": f"未知阶段：{stage}。可用阶段：{list(_STAGE_MAP.keys())}",
            "passed": False,
            "cache_hit": False,
        }

    stage_map = _STAGE_MAP[stage]

    skill_path = _SKILLS_DIR / stage_map["skill_dir"] / "SKILL.md"
    rule_path = _RULES_DIR / stage_map["rule_file"]

    skill_text = _read_file(skill_path)
    rule_text = _read_file(rule_path)

    if not skill_text:
        result = {
            "stage": stage,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "passed": False,
            "cache_hit": False,
            "issues": [{
                "type": "skill_file_missing",
                "severity": "error",
                "location": str(skill_path),
                "description": f"SKILL.md 文件不存在：{skill_path}",
            }],
            "summary": f"一致性检查失败：SKILL.md 不存在（{stage_map['skill_dir']}/SKILL.md）",
        }
        _CHECK_CACHE[cache_key] = result.copy()
        return result

    if not rule_text:
        result = {
            "stage": stage,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "passed": False,
            "cache_hit": False,
            "issues": [{
                "type": "rule_file_missing",
                "severity": "error",
                "location": str(rule_path),
                "description": f"Rule 文件不存在：{rule_path}",
            }],
            "summary": f"一致性检查失败：Rule 文件不存在（{stage_map['rule_file']}）",
        }
        _CHECK_CACHE[cache_key] = result.copy()
        return result

    # 执行 4 类检查
    all_issues: list[dict[str, Any]] = []

    issues_a = _check_type_a_materials(stage, skill_text, rule_text, stage_map)
    issues_b = _check_type_b_outputs(stage, skill_text, rule_text, stage_map)
    issues_c = _check_type_c_fields(stage, skill_text, rule_text, stage_map)
    issues_d = _check_type_d_modules(stage, skill_text, rule_text, stage_map)

    all_issues.extend(issues_a)
    all_issues.extend(issues_b)
    all_issues.extend(issues_c)
    all_issues.extend(issues_d)
    if req_name:
        all_issues.extend(_check_runtime_assets(stage, req_name, version, phase=phase))

    error_count = sum(1 for i in all_issues if i.get("severity") == "error")
    warn_count = sum(1 for i in all_issues if i.get("severity") == "warn")

    # runtime severity：将检查问题映射为门禁级别
    for issue in all_issues:
        issue_type = issue.get("type", "")
        if issue.get("severity") == "error":
            issue["runtime_severity"] = "P0_BLOCK"
        elif issue_type.startswith(("A1_", "A2_", "B1_", "B2_", "C1_", "D1_", "D2_", "skill_file_missing", "rule_file_missing")):
            issue["runtime_severity"] = "P1_WARN"
        else:
            issue["runtime_severity"] = "P2_INFO"

    if error_count > 0:
        summary = (
            f"一致性检查失败：发现 {error_count} 个 error + {warn_count} 个 warn。"
            f"建议运行 'python -m ai_workflow.consistency_check --fix {stage}' 查看修复建议"
        )
    elif warn_count > 0:
        summary = (
            f"一致性检查通过（类型 A/B/C/D 均匹配），"
            f"发现 {warn_count} 个非阻断性 warn"
        )
    else:
        summary = f"一致性检查通过（4/4 类型全部匹配），发现 0 个问题"

    result = {
        "stage": stage,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "passed": error_count == 0,
        "cache_hit": False,
        "issues": all_issues,
        "severity_summary": {
            "P0_BLOCK": sum(1 for i in all_issues if i.get("runtime_severity") == "P0_BLOCK"),
            "P1_WARN": sum(1 for i in all_issues if i.get("runtime_severity") == "P1_WARN"),
            "P2_INFO": sum(1 for i in all_issues if i.get("runtime_severity") == "P2_INFO"),
        },
        "summary": summary,
        "stats": {
            "type_a_issues": len(issues_a),
            "type_b_issues": len(issues_b),
            "type_c_issues": len(issues_c),
            "type_d_issues": len(issues_d),
            "errors": error_count,
            "warnings": warn_count,
        },
    }

    _CHECK_CACHE[cache_key] = result.copy()
    return result


def run_all_checks() -> dict[str, Any]:
    """对所有阶段执行一致性检查。"""
    results: dict[str, Any] = {}
    for stage in _STAGE_MAP:
        results[stage] = run_consistency_check(stage)

    total_issues = sum(len(r.get("issues", [])) for r in results.values())
    total_errors = sum(
        sum(1 for i in r.get("issues", []) if i.get("severity") == "error")
        for r in results.values()
    )
    total_warns = sum(
        sum(1 for i in r.get("issues", []) if i.get("severity") == "warn")
        for r in results.values()
    )

    return {
        "all_stages_checked": len(results),
        "total_issues": total_issues,
        "total_errors": total_errors,
        "total_warnings": total_warns,
        "results": results,
        "summary": (
            f"全阶段一致性检查完成：{len(results)} 个阶段，"
            f"{total_errors} errors, {total_warns} warnings"
        ),
    }


# ---------------------------------------------------------------------------
# 输出格式化
# ---------------------------------------------------------------------------

def _print_result(result: dict[str, Any], verbose: bool = False) -> None:
    """打印单个阶段检查结果。"""
    stage = result.get("stage", "?")
    cache_hit = result.get("cache_hit", False)

    if cache_hit:
        print(f"[CACHE] {stage.upper()} （命中缓存，跳过检查）")
        return

    if "error" in result:
        print(f"[ERROR] {stage.upper()}：{result['error']}")
        return

    passed = result.get("passed", False)
    status_icon = "✓" if passed else "✗"
    issues = result.get("issues", [])
    error_count = sum(1 for i in issues if i.get("severity") == "error")
    warn_count = sum(1 for i in issues if i.get("severity") == "warn")

    print(f"\n[{status_icon}] {stage.upper()} — {result.get('summary', '')}")
    print(f"    issues: {len(issues)} ({error_count} errors, {warn_count} warnings)")

    if verbose or not passed:
        for issue in issues:
            sev = issue.get("severity", "?").upper()
            loc = issue.get("location", "?")
            desc = issue.get("description", "")
            print(f"    [{sev}] {loc}")
            print(f"         {desc}")


def _generate_fix_suggestions(result: dict[str, Any]) -> list[str]:
    """根据检查结果生成修复建议。"""
    suggestions: list[str] = []
    issues = result.get("issues", [])

    for issue in issues:
        issue_type = issue.get("type", "")
        location = issue.get("location", "")
        rule_loc = issue.get("rule_location", "")

        if issue_type == "A1_missing_in_rule":
            item = issue.get("skill_item", "")
            suggestions.append(
                f"[{location}]\n"
                f"  → 在 Rule 文件 '{rule_loc}' 中补充必读材料：{item}\n"
            )
        elif issue_type == "A2_missing_in_skill":
            item = issue.get("rule_item", "")
            suggestions.append(
                f"[{location}]\n"
                f"  → 在 SKILL.md §1.4 中补充必读材料：{item}\n"
            )
        elif issue_type == "B1_output_path_skill_only":
            path = issue.get("skill_path", "")
            suggestions.append(
                f"[{location}]\n"
                f"  → 确认输出路径 '{path}' 是否需要在 Rule 中声明"
            )
        elif issue_type == "B2_output_path_rule_only":
            path = issue.get("rule_path", "")
            suggestions.append(
                f"[{location}]\n"
                f"  → 确认输出路径 '{path}' 是否需要在 SKILL 中声明"
            )
        elif issue_type == "C1_field_declaration_mismatch":
            field = issue.get("field", "")
            suggestions.append(
                f"[{location}]\n"
                f"  → 检查字段 '{field}' 是否在 Rule 字段规范中"
            )
        elif issue_type == "C3_field_spelling_variants":
            sf = issue.get("skill_field", "")
            rf = issue.get("rule_field", "")
            suggestions.append(
                f"[{location}]\n"
                f"  → 字段名可能存在拼写不一致：'{sf}' vs '{rf}'，建议统一"
            )
        elif issue_type == "D1_module_skill_only":
            mod = issue.get("module", "")
            suggestions.append(
                f"[{location}]\n"
                f"  → SKILL 引用了模块 '{mod}'，请确认 Rule 中是否需要同步"
            )
        elif issue_type == "D2_module_rule_only":
            mod = issue.get("module", "")
            suggestions.append(
                f"[{location}]\n"
                f"  → Rule 引用了模块 '{mod}'，请确认 SKILL 中是否需要同步"
            )
        elif issue_type == "skill_file_missing":
            suggestions.append(
                f"[{location}]\n"
                f"  → 创建缺失的 SKILL.md 文件：{issue.get('description', '')}"
            )
        elif issue_type == "rule_file_missing":
            suggestions.append(
                f"[{location}]\n"
                f"  → 创建缺失的 Rule 文件：{issue.get('description', '')}"
            )

    return suggestions


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> int:
    """命令行入口。"""
    args = sys.argv[1:]

    if not args:
        print("用法:")
        print("  python -m ai_workflow.consistency_check <stage>   # 检查指定阶段")
        print("  python -m ai_workflow.consistency_check --all      # 检查所有阶段")
        print("  python -m ai_workflow.consistency_check --fix [stage]  # 显示修复建议")
        print()
        print("可用阶段:", ", ".join(_STAGE_MAP.keys()))
        return 0

    command = args[0]

    if command == "--all":
        print("=" * 70)
        print(" AIDocxWorkFlow — SKILL ↔ Rule 一致性检查（全阶段）")
        print("=" * 70)
        result = run_all_checks()
        for stage in _STAGE_MAP:
            if stage in result["results"]:
                _print_result(result["results"][stage], verbose=False)
        print("\n" + "=" * 70)
        print(f"  {result['summary']}")
        print("=" * 70)
        return 1 if result["total_errors"] > 0 else 0

    if command == "--fix":
        target = args[1] if len(args) > 1 else None
        if target:
            result = run_consistency_check(target)
            suggestions = _generate_fix_suggestions(result)
            print(f"=== 修复建议：{target.upper()} ===")
            if suggestions:
                for s in suggestions:
                    print(s)
            else:
                print("  无需修复建议")
        else:
            # 全阶段修复建议
            result = run_all_checks()
            print("=== 全阶段修复建议 ===")
            has_suggestions = False
            for stage, res in result.get("results", {}).items():
                suggestions = _generate_fix_suggestions(res)
                if suggestions:
                    has_suggestions = True
                    print(f"\n[{stage.upper()}]")
                    for s in suggestions:
                        print(f"  {s}")
            if not has_suggestions:
                print("  所有阶段均无发现需要修复的问题")
        return 0

    # 单阶段检查
    result = run_consistency_check(command)
    print("=" * 70)
    print(f" AIDocxWorkFlow — 一致性检查：{command.upper()}")
    print("=" * 70)
    _print_result(result, verbose=True)
    print("=" * 70)
    print(f"  {result.get('summary', '')}")
    print("=" * 70)
    return 1 if not result.get("passed", False) else 0


if __name__ == "__main__":
    sys.exit(main())
