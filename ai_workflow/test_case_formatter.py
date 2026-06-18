#!/usr/bin/env python3
"""S5/S6 自动化格式化模块。

- S5: compose_test_points_from_structure() — 从 backlog 自动生成测试点骨架
- S6: format_test_cases() — 自动分配用例ID、规范化字段、生成 .md/.json/.xlsx
"""

from __future__ import annotations
import copy, json, re
from datetime import datetime
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).parent.parent.resolve()
WF    = _ROOT / "workflow_assets"


# ─────────────────────────────────────────────────────────────────────────────
# S5: 测试点骨架生成
# ─────────────────────────────────────────────────────────────────────────────

def compose_test_points_from_structure(
    backlog_json: dict,
    req_name: str = "游戏道具商城系统",
    version: str = "v1.0",
) -> dict:
    """
    从 backlog.json 生成测试点结构骨架。

    骨架仅保留 Story 原始信息，不预填任何推导字段。
    `scenario_test_points[]` 完全由 LLM 按 SKILL.md §1.4 推理填入：
    - 4 类型枚举（POSITIVE/BOUNDARY/NEGATIVE/EXCEPTION）
    - 8 模块（UI/BIZ/CONFIG/AUX/LINK/LOG/SPECIAL/HINT）
    - s4_reference、applies_rule、is_assumed 等必填字段

    返回:
        dict: {
            "version": str,
            "stage": "S5",
            "req_name": str,
            "stories": [
                {
                    "story_id": "BIZ-PURCHASE-001",
                    "title": "购买确认流程",
                    "module": "BIZ",
                    "precondition": "...",
                    "input_data": "...",
                    "expected_output": "...",
                    "acceptance_criteria": [...],
                    "scenario_test_points": [],   # LLM 推理填入
                }
            ]
        }
    """
    epics = backlog_json.get("epics", [])
    result = {
        "version": version,
        "stage": "S5",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "req_name": req_name,
        "stories": [],
    }

    for epic in epics:
        epic_id   = epic["id"]
        epic_mod  = epic.get("module", epic_id.split("-")[0])
        for story in epic.get("stories", []):
            sid    = story["id"]
            title  = story["title"]
            acs    = story.get("acceptance_criteria", [])
            pre    = story.get("precondition", "")
            inp    = story.get("input_data", "")
            out    = story.get("expected_output", "")

            result["stories"].append({
                "story_id": sid,
                "epic_id": epic_id,
                "module": epic_mod,
                "title": title,
                "precondition": pre,
                "input_data": inp,
                "expected_output": out,
                "acceptance_criteria": acs,
                "scenario_test_points": [],   # LLM 按 SKILL.md §1.4 推理填入
            })

    return result




# ─────────────────────────────────────────────────────────────────────────────
# S6: 测试用例格式化
# ─────────────────────────────────────────────────────────────────────────────

def format_test_cases(
    ai_raw_output: str | list,
    breakdown: dict,
    test_points: dict,
    req_name: str = "游戏道具商城系统",
    version: str = "v1.0",
    output_dir: Path | str | None = None,
) -> dict:
    """
    将 AI 输出的用例内容规范化为完整格式。

    自动化处理：
    - 分配用例 ID（按模块序号：UI-TC-001, BIZ-TC-001...）
    - 规范化字段
    - 步骤编号
    - 去重
    - 生成 .md + .json + .xlsx

    参数:
        ai_raw_output: AI 生成的用例内容（字符串或列表）
        breakdown: backlog.json 数据
        test_points: S5 输出的测试点 JSON
        output_dir: 输出目录（默认 <req_name>/「S6 测试用例生成」/v1.0/）
    """
    if output_dir is None:
        output_dir = WF / req_name / "「S6 测试用例生成」" / version
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 解析 AI 输出
    if isinstance(ai_raw_output, str):
        parsed = _parse_ai_output(ai_raw_output)
    else:
        parsed = ai_raw_output

    # 自动分配 ID
    cases = _assign_ids(parsed, test_points)

    # 构建最终 JSON
    result_json = {
        "version": version,
        "stage": "S6",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "req_name": req_name,
        "summary": _build_summary(cases),
        "test_cases": cases,
    }

    # 保存 JSON
    json_path = output_dir / "test_cases.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    print(f"[S6] JSON → {json_path}")

    # 保存 Markdown
    md_path = _save_md(cases, output_dir)
    print(f"[S6] Markdown → {md_path}")

    # 保存 Excel
    xlsx_path = _save_xlsx(cases, output_dir)
    print(f"[S6] XLSX → {xlsx_path}")

    return {
        "json": str(json_path),
        "md": str(md_path),
        "xlsx": str(xlsx_path),
        "case_count": len(cases),
        "summary": result_json["summary"],
    }


# ── 子函数 ──────────────────────────────────────────────────────────────────

# 模块定义见 .cursor/MODULES.md（项目级唯一真相源）
# 本文件不重写模块表，仅引用；如模块调整，只改 MODULES.md
#
# 重要规则（与 MODULES.md §1 严格一致）：
# 1. HINT **不**作为 Epic ID 前缀——HINT 仅作为 TP module 字段的取值
# 2. 测试用例 case_id 的"模块"前缀必须从 8 模块中取全名（UI/BIZ/CONFIG/AUX/LINK/LOG/SPECIAL/HINT）
# 3. 模块字段支持中英双语（"界面" = "UI"），但 case_id 前缀统一用英文全名
_MODULE_SEQ = ["UI", "BIZ", "CONFIG", "AUX", "LINK", "LOG", "SPECIAL", "HINT"]
_MODULE_COUNTER = {m: 0 for m in _MODULE_SEQ}

# 中英模块名归一化映射（"界面" / "UI" / "ui" → "UI"）
# 用于 summary 分组时合并中英键
# 重要：同时支持 **v1.1 旧 4 字母缩写**（CFG/LNK/SPC/HNT）和 **8 模块全名**
_MODULE_NAME_NORMALIZE = {
    # ── 中文 → 英文全名 ──
    "界面":   "UI",
    "业务":   "BIZ",
    "配置":   "CONFIG",
    "辅助":   "AUX",
    "关联":   "LINK",
    "日志":   "LOG",
    "特殊":   "SPECIAL",
    "提示":   "HINT",
    # ── 英文全名（pass-through，大小写不敏感）──
    "ui":   "UI",
    "biz":  "BIZ",
    "config": "CONFIG",
    "aux":  "AUX",
    "link": "LINK",
    "log":  "LOG",
    "special": "SPECIAL",
    "hint": "HINT",
    "UI":   "UI",
    "BIZ":  "BIZ",
    "CONFIG": "CONFIG",
    "AUX":  "AUX",
    "LINK": "LINK",
    "LOG":  "LOG",
    "SPECIAL": "SPECIAL",
    "HINT": "HINT",
    # ── v1.1 旧 4 字母缩写 → 现行全名（v1.1 时 _module_prefix() 错误返回的缩写）──
    "cfg":  "CONFIG",   # 旧 "CFG" → CONFIG
    "lnk":  "LINK",     # 旧 "LNK" → LINK
    "spc":  "SPECIAL",  # 旧 "SPC" → SPECIAL
    "hnt":  "HINT",     # 旧 "HNT" → HINT
    "CFG":  "CONFIG",
    "LNK":  "LINK",
    "SPC":  "SPECIAL",
    "HNT":  "HINT",
}

# v1.1 → v1.2/v1.7 旧枚举升级映射（v1.1 旧数据加载时执行）
# 仅保留仍可识别的旧枚举；新枚举不在此表中
_V11_TO_CURRENT = {
    # UI v1.1 4 枚举 → v1.2 11 枚举
    "CONTROL_EXISTENCE":  "CONTROL_RENDER",   # 默认归 RENDER；人工判定时可拆出 STATE
    "INTERACTION":        "PURE_INTERACTION", # 默认归 PURE；UI 基础功能可拆出 CONTROL_BASE_FUNC
    "LAYOUT":             "LAYOUT_ADAPT",
    "RESOLUTION_COMPAT":  "LAYOUT_ADAPT",
    # AUX v1.1 4 枚举 → v1.2 14 枚举
    "TOOL_UTIL":          "COMMON_UTIL",
    "NETWORK_LAYER":      "NETWORK_LAYER",
    "CACHE_HIT_RATE":     "CACHE_HIT_RATE",
    "RESOURCE_MGMT":      "RESOURCE_MGMT",
    # BIZ v1.1 4 枚举 → v1.2 9 枚举（ACTIVITY_OPEN_CLOSE 拆分）
    "ACTIVITY_OPEN_CLOSE": "BIZ_STATE_MACHINE",  # 状态流转类；业务结果→BIZ_LOGIC
    "PROTOCOL":            "BIZ_PROTOCOL",
    "DB_PERSIST":          "BIZ_DB_PERSIST",
    "ENTITY_CACHE":        "CACHE_HIT_RATE",     # v1.1 旧 BIZ 枚举 → v1.2 移交 AUX
    # LINK v1.1 3 枚举 → v1.2 6 枚举
    "CORRELATION_TEST":    "INTERNAL_BIZ_LINKAGE",
    "REGRESSION_TEST":     "CROSS_SERVER_SYNC",  # 跨服部分；第三方部分→EXTERNAL_THIRD_PARTY
    "MULTI_TENANT_SYNC":   "MULTI_CLIENT_SYNC",  # 多端一致性
    # LOG v1.1 4 枚举 → v1.9 13 枚举
    "ASSET_CHANGE":        "LOG_ASSET_AUDIT",
    "PROGRESS_TRIGGER":    "LOG_MONITOR",
    "ANOMALY":             "LOG_CRASH_REPORT",
    "AUDIT_TRAIL":         "LOG_INTEGRITY",
    # SPECIAL v1.1 5 枚举 → v1.2 9 枚举
    "DUPLICATE_PACKET":    "BOUNDARY_EXTREME",   # 业务层去重；流量层→WEAK_NET_RATE_LIMIT
    "HIGH_FREQ_PACKET":    "BOUNDARY_EXTREME",   # 业务层高频；服务端 HA→SERVER_HA_RISK
    "WEAK_NETWORK":        "WEAK_NET_RATE_LIMIT",
    "SWITCH_TO_BACKGROUND": "BG_FG_SWITCH",
    "ANTI_CHEAT":          "ANTI_CHEAT",
    # HINT v1.6.1 6 枚举 → v1.7 13 枚举
    "RED_DOT":             "RED_DOT_BADGE",      # 语义升级：扩展为「红点+角标+数字」
    "ITEM_FLOAT":          "ITEM_FLOAT",
    "CURRENCY_FLOAT":      "CURRENCY_FLOAT",
    "MODAL_DIALOG":        "MODAL_DIALOG",
    "TOAST":               "TOAST",
    "FLOAT_NOTIFY":        "FLOAT_NOTIFY",
    # 旧/已废/凭空出现的枚举（v1.6.1 S6 test_cases.json 发现的）
    "SYS_MSG":             "MODAL_DIALOG",       # v1.6.1 凭空出现 → 迁移至 MODAL_DIALOG 或 TOAST
    "ENTITY_REL":          "BIZ_DATA_FLOW",      # 旧枚举（v1.1）→ BIZ 端服数据流
    "GAME_LOG":            "LOG_OPERATION",      # 旧枚举 → LOG 通用
}


def normalize_module_name(name: str) -> str | None:
    """归一化模块名（中文/英文缩写/全名/小写 → 8 模块全名）。

    规则：
    - 8 模块之一（大小写不敏感）→ 返回全名
    - 中文名（界面/业务/...）→ 返回对应全名
    - 旧 v1.1 缩写（CFG/LNK/SPC/HNT）→ 返回 CONFIG/LINK/SPECIAL/HINT
    - 不识别 → 返回 None（调用方应处理）

    Args:
        name: 任意形式的模块名

    Returns:
        8 模块之一（CONFIG/UI/BIZ/AUX/LINK/LOG/SPECIAL/HINT），不识别返回 None
    """
    if not name:
        return None
    key = str(name).strip()
    return _MODULE_NAME_NORMALIZE.get(key) or _MODULE_NAME_NORMALIZE.get(key.upper())


def migrate_old_enum(old_value: str, fallback_module: str = "BIZ") -> tuple[str, str | None]:
    """将 v1.1 旧枚举值升级为 v1.2/v1.7 现行枚举。

    Args:
        old_value: 旧枚举字符串
        fallback_module: 当无法识别时，回退到该模块的默认枚举

    Returns:
        (new_enum, migration_note) - new_enum 是 v1.2+ 现行枚举；
        migration_note 是 None（无迁移）或迁移说明字符串
    """
    if not old_value:
        return (fallback_module, None)

    v = str(old_value).strip().upper()
    if v in _V11_TO_CURRENT:
        new = _V11_TO_CURRENT[v]
        if new != v:
            return (new, f"v1.1→v1.2: {v} → {new}")
        return (new, None)

    # 不在迁移表里——可能是 v1.2+ 现行枚举或非法值
    return (v, None)


def _assign_ids(cases: list, test_points: dict) -> list:
    """为每个用例分配唯一 ID，按模块分组递增。

    模块定义见 .cursor/MODULES.md（项目级唯一真相源）
    重要：HINT 不作为 Epic ID 前缀，但作为 case_id 前缀允许使用（"HINT-TC-NNN"）
    """
    global _MODULE_COUNTER
    _MODULE_COUNTER = {m: 0 for m in _MODULE_SEQ}

    for case in cases:
        # 中英归一化（"界面" / "UI" / "ui" → "UI"）
        raw_module = case.get("module", "BIZ")
        module = normalize_module_name(raw_module) or "BIZ"

        # 旧枚举迁移（如有）
        if "test_type" in case:
            new_enum, note = migrate_old_enum(case["test_type"], fallback_module=module)
            if note:
                case["_migration_note"] = note
            case["test_type"] = new_enum

        # 旧枚举迁移（"module" 字段本身可能是 v1.1 旧枚举值，常见于 test_points.json）
        if module in _V11_TO_CURRENT and _V11_TO_CURRENT[module] != module:
            new_module = _V11_TO_CURRENT[module]
            case["_migration_note"] = f"v1.1→v1.2: {module} → {new_module}"
            module = new_module

        case["module"] = module  # 写回归一化后的模块名

        seq = _MODULE_COUNTER.get(module, 0) + 1
        _MODULE_COUNTER[module] = seq
        # case_id 前缀 = 归一化后的模块全名
        case["case_id"] = f"{module}-TC-{seq:03d}"

    return cases


def _module_prefix(module: str) -> str:
    """模块 → ID 前缀映射（与 .cursor/MODULES.md §1 严格一致）。

    返回 8 模块英文全名（CONFIG/UI/BIZ/AUX/LINK/LOG/SPECIAL/HINT）。
    不识别时返回 None（禁止 fallback 到 "MISC"——必须 raise 由 S6 fail_report 处理）。
    """
    return normalize_module_name(module)


def _parse_ai_output(raw: str) -> list:
    """从 AI 输出字符串中解析出用例列表。"""
    cases = []
    # 尝试从 JSON 数组中解析
    json_match = re.search(r'\[[\s\S]+]\]', raw)
    if json_match:
        try:
            cases = json.loads(json_match.group())
            return cases
        except json.JSONDecodeError:
            pass

    # 从 Markdown 表格中解析
    rows = re.findall(r'\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|', raw)
    for row in rows[1:]:  # 跳过表头
        if len(row) >= 5:
            cases.append({
                "title":        row[0].strip(),
                "module":       row[1].strip(),
                "precondition": row[2].strip(),
                "steps":        row[3].strip(),
                "expected":     row[4].strip(),
            })
    return cases


def _build_summary(cases: list) -> dict:
    """按归一化后的模块名汇总。

    关键修复：原版本用 `case.get("module", "OTHER")`，导致 "界面" / "UI" / "ui"
    三个值在 by_module 中成为 3 个 key。本函数先归一化再分组，确保 8 模块只有 8 个 key。
    """
    by_module = {}
    for c in cases:
        # 归一化：中文/英文缩写/全名 → 8 模块全名
        raw = c.get("module", "BIZ")
        m = normalize_module_name(raw) or "BIZ"
        c["module"] = m  # 反向写回
        by_module.setdefault(m, []).append(c.get("case_id", ""))

    return {
        "total_cases": len(cases),
        "by_module": {m: len(ids) for m, ids in by_module.items()},
        "module_list": sorted(by_module.keys()),  # 排序输出便于对比
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI: --migrate-modules 框架（v1.1 → v1.2/v1.7 旧数据平滑过渡）
# ─────────────────────────────────────────────────────────────────────────────

def migrate_test_points_file(json_path: str | Path, *, in_place: bool = False) -> dict:
    """将 v1.1 旧 test_points.json / test_cases.json 文件升级到 v1.2/v1.7。

    升级项：
    1. module 字段：中英归一化（"界面" / "UI" / "ui" → "UI"）
    2. test_point_type 字段：v1.1 旧枚举 → v1.2/v1.7 现行枚举
    3. 凭空出现的旧枚举（RED_DOT → RED_DOT_BADGE；SYS_MSG → MODAL_DIALOG）

    Args:
        json_path: 待升级的 JSON 文件路径
        in_place: 是否原地写入（默认 False，写到 <原名>.migrated.json）

    Returns:
        dict: {"input": 原文件, "output": 输出文件, "migrations": [...]}
    """
    p = Path(json_path)
    with p.open(encoding="utf-8") as f:
        data = json.load(f)

    migrations = []

    def _migrate_node(node: dict, path: str) -> None:
        # module 归一化
        raw_mod = node.get("module", "")
        if raw_mod:
            new_mod = normalize_module_name(raw_mod)
            if new_mod and new_mod != raw_mod:
                migrations.append({
                    "path": f"{path}.module",
                    "from": raw_mod,
                    "to": new_mod,
                    "reason": "中英归一化",
                })
                node["module"] = new_mod

        # test_point_type / test_type 升级
        for enum_field in ("test_point_type", "test_type", "module_type"):
            raw_enum = node.get(enum_field, "")
            if raw_enum and raw_enum in _V11_TO_CURRENT:
                new_enum = _V11_TO_CURRENT[raw_enum]
                if new_enum != raw_enum:
                    migrations.append({
                        "path": f"{path}.{enum_field}",
                        "from": raw_enum,
                        "to": new_enum,
                        "reason": "v1.1→v1.2/v1.7",
                    })
                    node[enum_field] = new_enum

        # S5 v3 schema 迁移（v1.0 → v3）
        # id → tp_id
        if "id" in node and "tp_id" not in node:
            migrations.append({
                "path": f"{path}.id",
                "from": node["id"],
                "to": node["id"],
                "reason": "v3-schema: id → tp_id（字段重命名）",
            })
            node["tp_id"] = node.pop("id")
        # type → test_point_type
        if "type" in node and "test_point_type" not in node:
            migrations.append({
                "path": f"{path}.type",
                "from": node["type"],
                "to": node["type"],
                "reason": "v3-schema: type → test_point_type（字段重命名）",
            })
            node["test_point_type"] = node.pop("type")
        # title → description（仅对 scenario_test_points 条目生效）
        if "title" in node and "description" not in node:
            migrations.append({
                "path": f"{path}.title",
                "from": node["title"],
                "to": node["title"],
                "reason": "v3-schema: title → description（字段重命名）",
            })
            node["description"] = node.pop("title")

    # 兼容三种结构：
    # 1. test_points.json 顶层 {"stories": [...]}（compose_test_points_from_structure 输出）
    # 2. test_points.json 顶层 [...]（直接列表）
    # 3. test_cases.json 顶层 {"test_cases": [...]}（format_test_cases 输出）

    def _walk_story(story: dict, spath: str) -> None:
        _migrate_node(story, spath)
        for tp_idx, tp in enumerate(story.get("scenario_test_points", [])):
            _migrate_node(tp, f"{spath}.scenario_test_points[{tp_idx}]")
        # module_coverage 内部 points[] 也要迁移
        mc = story.get("module_coverage", {})
        if isinstance(mc, dict):
            for mod_key, mc_val in mc.items():
                if not isinstance(mc_val, dict):
                    continue
                new_mod = normalize_module_name(mod_key)
                if new_mod and new_mod != mod_key:
                    migrations.append({
                        "path": f"{spath}.module_coverage.{mod_key}",
                        "from": mod_key,
                        "to": new_mod,
                        "reason": "中英归一化",
                    })
                    mc[new_mod] = mc_val
                    if new_mod != mod_key:
                        del mc[mod_key]
                for p_idx, p in enumerate(mc_val.get("points", [])):
                    if p in _V11_TO_CURRENT:
                        new_p = _V11_TO_CURRENT[p]
                        if new_p != p:
                            migrations.append({
                                "path": f"{spath}.module_coverage.{new_mod or mod_key}.points[{p_idx}]",
                                "from": p,
                                "to": new_p,
                                "reason": "v1.1→v1.2/v1.7",
                            })
                            mc_val["points"][p_idx] = new_p

    if isinstance(data, list):
        # 顶层列表
        for s_idx, story in enumerate(data):
            _walk_story(story, f"[{s_idx}]")
    elif isinstance(data, dict):
        if "stories" in data:
            for s_idx, story in enumerate(data["stories"]):
                _walk_story(story, f"stories[{s_idx}]")
        if "test_cases" in data:
            for tc_idx, tc in enumerate(data["test_cases"]):
                _migrate_node(tc, f"test_cases[{tc_idx}]")

    # 写出
    out_path = p if in_place else p.with_suffix(".migrated.json")
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        "input":  str(p),
        "output": str(out_path),
        "migrations_count": len(migrations),
        "migrations": migrations,
    }


def _cli_migrate_modules(argv: list[str]) -> int:
    """CLI 入口：
    `python test_case_formatter.py --migrate-modules <json> [--in-place]`
    迁移内容：
    1. v1.1→v1.2/v1.7 旧枚举升级（module / test_point_type）
    2. S5 v3 schema（v1.0→v3）：id→tp_id, type→test_point_type, title→description
    """
    import argparse
    ap = argparse.ArgumentParser(
        prog="test_case_formatter.py",
        description="AIDocxWorkFlow test_case_formatter CLI — v1.1 → v1.2/v1.7 迁移",
    )
    ap.add_argument("--migrate-modules", metavar="JSON", help="升级 v1.1 旧 JSON 文件")
    ap.add_argument("--in-place", action="store_true", help="原地写入（默认输出 <原名>.migrated.json）")
    args = ap.parse_args(argv)

    if args.migrate_modules:
        result = migrate_test_points_file(args.migrate_modules, in_place=args.in_place)
        print(f"[migrate-modules] input  : {result['input']}")
        print(f"[migrate-modules] output : {result['output']}")
        print(f"[migrate-modules] migrations: {result['migrations_count']} 项")
        for m in result["migrations"][:20]:
            print(f"  - {m['path']}: {m['from']} → {m['to']} ({m['reason']})")
        if len(result["migrations"]) > 20:
            print(f"  ... 还有 {len(result['migrations']) - 20} 项")
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(_cli_migrate_modules(sys.argv[1:]))


def _save_md(cases: list, output_dir: Path) -> Path:
    """保存 10 列 Markdown：与 SKILL.md 当前 10 列严格一致。

    重要：v3.0 修复（2026-06-15）
    - 旧 6 列（ID/标题/模块/前置/步骤/预期）→ 10 列
    - 缺「功能描述」「用例状态」「备注」会导致 S7 审查丢分
    """
    lines = [
        "# 测试用例 — 游戏道具商城系统 v1.0\n",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"用例总数：{len(cases)}\n\n",
        "## 用例列表\n\n",
        "| 用例ID | 模块 | 用例描述 | 功能描述 | 前置条件 | 操作步骤 | 预期结果 | 优先级 | 用例状态 | 备注 |\n",
        "|---|---|---|---|---|---|---|---|---|---|\n",
    ]
    for c in cases:
        lines.append(
            f"| {c.get('case_id','')} | {c.get('模块', c.get('module',''))} | "
            f"{c.get('用例描述','')} | {c.get('功能描述','')} | "
            f"{c.get('前置条件', c.get('precondition',''))} | "
            f"{c.get('操作步骤', c.get('steps',''))} | "
            f"{c.get('预期结果', c.get('expected',''))} | "
            f"{c.get('优先级', c.get('priority','P1'))} | "
            f"{c.get('用例状态','Draft')} | "
            f"{c.get('备注','')} |\n"
        )

    md_path = output_dir / "test_cases.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)
    return md_path


# v3.0 修复：xlsx 表头统一为 10 列（与 SKILL.md 严格一致）
# - 旧 8 列（缺「功能描述」「用例状态」「备注」，多出「用例类型」）→ 10 列
_XLSX_HEADERS_V3 = [
    "用例ID",     # case_id
    "模块",       # 模块 / module
    "用例描述",   # 用例描述（纯 Story 标题）
    "功能描述",   # 功能描述（验证 X 在 Y 条件下表现 Z）
    "前置条件",   # 前置条件 / precondition
    "操作步骤",   # 操作步骤（具体 UI 元素/数值）
    "预期结果",   # 预期结果（纯业务结果）
    "优先级",     # 优先级 P0/P1/P2
    "用例状态",   # 用例状态 Draft/Review/Approved
    "备注",       # 备注 story/tp_id/method 元数据
]


def _save_xlsx(cases: list, output_dir: Path) -> Path:
    """保存 10 列 xlsx：与 SKILL.md 当前 10 列严格一致。

    v3.0 修复（2026-06-15）：旧 8 列错位被 s6_xlsx_enhance 二次覆盖。
    本函数作为 s6_generate.py 主路径兜底使用——表头已对齐 s6_xlsx_enhance。
    """
    xlsx_path = output_dir / "test_cases.xlsx"
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "测试用例"
        ws.append(_XLSX_HEADERS_V3)
        for c in cases:
            ws.append([
                c.get("case_id", ""),
                c.get("模块", c.get("module", "")),
                c.get("用例描述", ""),
                c.get("功能描述", ""),
                c.get("前置条件", c.get("precondition", "")),
                c.get("操作步骤", c.get("steps", "")),
                c.get("预期结果", c.get("expected", "")),
                c.get("优先级", c.get("priority", "P1")),
                c.get("用例状态", "Draft"),
                c.get("备注", ""),
            ])
        for col in ws.columns:
            max_len = 0
            for cell in col:
                try:
                    max_len = max(max_len, len(str(cell.value or "")))
                except Exception:
                    pass
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)
        wb.save(str(xlsx_path))
    except ImportError:
        print(f"[S6] openpyxl 未安装，跳过 XLSX 生成: pip install openpyxl")
        xlsx_path = output_dir / "test_cases.xlsx"
        xlsx_path.write_text("openpyxl required: pip install openpyxl", encoding="utf-8")
    return xlsx_path
