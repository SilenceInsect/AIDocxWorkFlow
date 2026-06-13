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
    从 backlog.json 自动生成测试点结构骨架。

    每个 Story 生成 6 个测试点：
      2×正向路径（主要功能）
      2×异常路径（边界/错误）
      1×等价类
      1×边界值

    AI 只需要填充 scenario_test_points（简化版字段）。
    Python 自动填充其他结构化字段。

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
                    "equivalence_classes": [...],   # 自动生成
                    "boundary_values": [...],        # 自动生成
                    "scenario_test_points": [],        # AI 填充
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
            sid  = story["id"]
            title = story["title"]
            acs  = story.get("acceptance_criteria", [])
            pre  = story.get("precondition", "")
            inp  = story.get("input_data", "")
            out  = story.get("expected_output", "")

            # 从 acceptance_criteria 提取等价类关键词
            keywords = set()
            for ac in acs:
                keywords.update(re.findall(r"[\w]{2,}", ac))
            kw_list = list(keywords)[:10]

            # 从输入数据提取参数
            params = [p.strip() for p in re.split(r"[，,、/]", inp) if p.strip()] if inp else []

            # 自动生成等价类
            eq_classes = _derive_equivalence_classes(story)
            # 自动生成边界值
            bv = _derive_boundary_values(params)

            result["stories"].append({
                "story_id": sid,
                "epic_id": epic_id,
                "module": epic_mod,
                "title": title,
                "precondition": pre,
                "input_data": inp,
                "expected_output": out,
                "acceptance_criteria": acs,
                "equivalence_classes": eq_classes,
                "boundary_values": bv,
                "module_coverage": epic_mod,
                "keywords": kw_list,
                "scenario_test_points": [],   # AI 填
            })

    return result


def _derive_equivalence_classes(story: dict) -> list:
    """从 Story 自动推导等价类。"""
    title = story.get("title", "")
    inp   = story.get("input_data", "")
    classes = []

    # 数值型参数
    if re.search(r"\d", inp):
        classes.extend([
            {"id": "EC1", "type": "normal", "description": "正常有效值", "example": "有效范围内数值"},
            {"id": "EC2", "type": "boundary", "description": "边界值（下限）", "example": "最小值"},
            {"id": "EC3", "type": "boundary", "description": "边界值（上限）", "example": "最大值"},
            {"id": "EC4", "type": "invalid", "description": "无效值", "example": "负数/0/超出范围"},
        ])

    # 余额/价格相关
    if any(kw in title + inp for kw in ["余额", "价格", "金额", "支付"]):
        classes.extend([
            {"id": "EC5", "type": "normal", "description": "余额充足", "example": "余额 >= 所需金额"},
            {"id": "EC6", "type": "invalid", "description": "余额不足", "example": "余额 < 所需金额"},
        ])

    # VIP/折扣相关
    if any(kw in title for kw in ["VIP", "折扣", "促销"]):
        classes.extend([
            {"id": "EC7", "type": "normal", "description": "VIP有效等级", "example": "VIP1/2/3"},
            {"id": "EC8", "type": "invalid", "description": "非VIP用户", "example": "普通用户"},
        ])

    # 如果没有提取到，返回通用类
    if not classes:
        classes = [
            {"id": "EC1", "type": "normal", "description": "正常路径", "example": "满足前置条件"},
            {"id": "EC2", "type": "error", "description": "异常路径", "example": "不满足前置条件"},
        ]

    return classes[:6]


def _derive_boundary_values(params: list) -> list:
    """从输入参数推导边界值。"""
    bv = []
    for i, p in enumerate(params[:4]):
        p_clean = re.sub(r"[^\w]", "", p)
        bv.extend([
            {"param": p, "param_clean": p_clean, "boundary": "min", "value": 1,  "desc": f"{p}最小值"},
            {"param": p, "param_clean": p_clean, "boundary": "max", "value": 99,  "desc": f"{p}最大值"},
            {"param": p, "param_clean": p_clean, "boundary": "zero", "value": 0,  "desc": f"{p}为零"},
            {"param": p, "param_clean": p_clean, "boundary": "negative", "value": -1, "desc": f"{p}为负数"},
        ])
    return bv


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

_MODULE_SEQ = ["UI", "BIZ", "CONFIG", "AUX", "LINK", "LOG", "SPECIAL"]
_MODULE_COUNTER = {m: 0 for m in _MODULE_SEQ}


def _assign_ids(cases: list, test_points: dict) -> list:
    """为每个用例分配唯一 ID，按模块分组递增。"""
    global _MODULE_COUNTER
    _MODULE_COUNTER = {m: 0 for m in _MODULE_SEQ}

    for case in cases:
        module = case.get("module", "BIZ")
        seq = _MODULE_COUNTER.get(module, 0) + 1
        _MODULE_COUNTER[module] = seq
        prefix = _module_prefix(module)
        case["case_id"] = f"{prefix}-TC-{seq:03d}"
    return cases


def _module_prefix(module: str) -> str:
    m = module.upper()
    if "UI" in m:   return "UI"
    if "BIZ" in m:  return "BIZ"
    if "CONFIG" in m: return "CFG"
    if "AUX" in m:   return "AUX"
    if "LINK" in m:  return "LNK"
    if "LOG" in m:   return "LOG"
    return "SPC"


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
    by_module = {}
    for c in cases:
        m = c.get("module", "OTHER")
        by_module.setdefault(m, []).append(c["case_id"])

    return {
        "total_cases": len(cases),
        "by_module": {m: len(ids) for m, ids in by_module.items()},
        "module_list": list(by_module.keys()),
    }


def _save_md(cases: list, output_dir: Path) -> Path:
    lines = [
        "# 测试用例 — 游戏道具商城系统 v1.0\n",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"用例总数：{len(cases)}\n\n",
        "## 用例列表\n\n",
        "| ID | 标题 | 模块 | 前置条件 | 操作步骤 | 预期结果 |\n",
        "|---|---|---|---|---|---|\n",
    ]
    for c in cases:
        lines.append(
            f"| {c.get('case_id','')} | {c.get('title','')} | "
            f"{c.get('module','')} | {c.get('precondition','')} | "
            f"{c.get('steps','')} | {c.get('expected','')} |\n"
        )

    md_path = output_dir / "test_cases.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)
    return md_path


def _save_xlsx(cases: list, output_dir: Path) -> Path:
    xlsx_path = output_dir / "test_cases.xlsx"
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "测试用例"

        headers = ["用例ID", "标题", "模块", "前置条件", "操作步骤",
                   "预期结果", "优先级", "用例类型"]
        ws.append(headers)

        for c in cases:
            ws.append([
                c.get("case_id", ""),
                c.get("title", ""),
                c.get("module", ""),
                c.get("precondition", ""),
                c.get("steps", ""),
                c.get("expected", ""),
                c.get("priority", "P1"),
                c.get("case_type", "功能测试"),
            ])

        # 调整列宽
        for col in ws.columns:
            max_len = 0
            for cell in col:
                try:
                    max_len = max(max_len, len(str(cell.value)))
                except Exception:
                    pass
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

        wb.save(str(xlsx_path))
    except ImportError:
        print(f"[S6] openpyxl 未安装，跳过 XLSX 生成: pip install openpyxl")
        # 写一个占位文件
        xlsx_path = output_dir / "test_cases.xlsx"
        xlsx_path.write_text("openpyxl required: pip install openpyxl", encoding="utf-8")
    return xlsx_path
