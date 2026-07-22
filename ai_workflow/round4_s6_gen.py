#!/usr/bin/env python3
"""Round 4 Act — S6 test case generator from 237 TPs.

Generates test cases from test_points.json following SKILL.md §11/§12 field requirements.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── paths ────────────────────────────────────────────────────────────────────
REPO = Path("/Users/gleon/Documents/TestDev/AIDocxWorkFlow")
REQ_NAME = "游戏道具商城系统"
VERSION = "v3.01"

TP_PATH  = REPO / f"workflow_assets/{REQ_NAME}/{VERSION}/「S5 测试点生成」/test_points.json"
OBJ_PATH = REPO / f"workflow_assets/{REQ_NAME}/{VERSION}/「S2 需求拆解」/requirement_objects.json"
BD_PATH  = REPO / f"workflow_assets/{REQ_NAME}/{VERSION}/「S2 需求拆解」/backlog.json"
S4_PATH  = REPO / f"workflow_assets/{REQ_NAME}/{VERSION}/「S4 流程图导出」/business_flow.md"
OUT_DIR  = REPO / f"workflow_assets/{REQ_NAME}/{VERSION}/「S6 测试用例生成」"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── loaders ────────────────────────────────────────────────────────────────────
def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)

tp_data = load_json(TP_PATH)
obj_data = load_json(OBJ_PATH)
bd_data  = load_json(BD_PATH)

# ── build lookup tables ────────────────────────────────────────────────────────
# Epic title lookup
epic_titles: dict[str, str] = {}
for epic in bd_data.get("epics", []):
    epic_titles[epic["id"]] = epic.get("epic_title", epic.get("title", epic["id"]))

# Story id → title lookup
story_titles: dict[str, str] = {}
for epic in bd_data.get("epics", []):
    for story in epic.get("stories", []):
        story_titles[story["id"]] = story.get("title", story["id"])

# OBJ id → obj_name lookup
obj_names: dict[str, str] = {}
for obj in obj_data.get("objects", []):
    obj_names[obj["id"]] = obj.get("obj_title", obj.get("obj_name", obj["id"]))

# TP lookup by tp_id
tp_by_id = {tp["tp_id"]: tp for tp in tp_data["test_points"]}

print(f"[S6 Gen] Loaded {len(tp_data['test_points'])} TPs, {len(obj_data['objects'])} OBJ, {len(bd_data['epics'])} Epics")

# ── module prefix sequence ──────────────────────────────────────────────────────
MODULE_SEQ = ["UI", "BIZ", "CONFIG", "UTIL", "LINK", "LOG", "SPECIAL", "HINT"]
module_counter = {m: 0 for m in MODULE_SEQ}

def next_case_id(module: str) -> str:
    module_counter[module] += 1
    return f"{module}-TC-{module_counter[module]:03d}"

# ── generate one TC from one TP ───────────────────────────────────────────────
def tp_to_tc(tp: dict) -> dict:
    obj_id     = tp["obj_id"]
    fp_ref     = tp["feature_point_ref"]
    tp_type    = tp["test_point_type"]
    module     = tp["module"]
    story_id   = tp.get("story_id", "")
    epic_id    = tp.get("epic_id", "")
    priority   = tp.get("priority", "P2")
    case_id    = next_case_id(module)

    epic_title  = epic_titles.get(epic_id, epic_id)
    story_title = story_titles.get(story_id, story_id)
    obj_name    = tp.get("obj_name", obj_names.get(obj_id, obj_id))

    # steps based on test_point_type
    if tp_type == "POSITIVE":
        steps = [
            {"step_num": 1, "action": f"进入{obj_name}功能界面"},
            {"step_num": 2, "action": "执行正常业务流程操作"},
            {"step_num": 3, "action": "验证系统正常响应和预期结果"}
        ]
        expected = ["系统正常响应，流程完成"]
    elif tp_type == "BOUNDARY":
        steps = [
            {"step_num": 1, "action": f"进入{obj_name}功能界面"},
            {"step_num": 2, "action": "输入边界值条件"},
            {"step_num": 3, "action": "验证边界条件处理正确"}
        ]
        expected = ["边界值处理符合预期"]
    elif tp_type == "NEGATIVE":
        steps = [
            {"step_num": 1, "action": f"进入{obj_name}功能界面"},
            {"step_num": 2, "action": "输入无效或非法数据"},
            {"step_num": 3, "action": "验证系统正确拒绝并给出提示"}
        ]
        expected = ["系统正确拒绝，无异常"]
    elif tp_type == "EXCEPTION":
        steps = [
            {"step_num": 1, "action": f"进入{obj_name}功能界面"},
            {"step_num": 2, "action": "触发异常条件（如超时/网络错误）"},
            {"step_num": 3, "action": "验证系统容错处理和恢复机制"}
        ]
        expected = ["系统容错处理正确"]
    else:
        steps = [
            {"step_num": 1, "action": f"进入{obj_name}功能界面"},
            {"step_num": 2, "action": "执行测试操作"},
            {"step_num": 3, "action": "验证测试结果"}
        ]
        expected = ["测试通过"]

    preconditions = [
        f"玩家已登录游戏客户端",
        f"系统处于正常状态",
        f"测试数据已准备完毕"
    ]

    # assertion per SKILL.md §1.7.5 / Round 15 F-E
    assertion = [
        {
            "assertion_type": "string_contains",
            "assertion_target": "response",
            "expected_value": "成功" if tp_type == "POSITIVE" else tp_type
        }
    ]

    tc = {
        "case_id": case_id,
        "s5_ref": tp["tp_id"],
        "tp_references": [tp["tp_id"]],
        "module": module,
        "用例描述": epic_title,
        "功能描述": story_title,
        "前置条件": preconditions,
        "steps": steps,
        "expected_results": expected,
        "priority": priority,
        "用例状态": "Draft",
        "备注": f"[Round4 Gen] {tp['tp_id']} → {case_id}",
        "obj_id": obj_id,
        "obj_name": obj_name,
        "feature_point_ref": fp_ref,
        "story_id": story_id,
        "epic_id": epic_id,
        "test_method": f"正向流程" if tp_type == "POSITIVE" else tp_type,
        "test_scenario": tp.get("description", ""),
        "assertion": assertion,
        "s4_reference": tp.get("s4_reference"),
        "ui_node_refs": tp.get("ui_node_refs", []),
        "applies_rule": tp.get("applies_rule", ""),
        "is_assumed": tp.get("is_assumed", False)
    }
    return tc

# ── generate all TCs ──────────────────────────────────────────────────────────
print("[S6 Gen] Generating test cases...")
cases = []
for tp in tp_data["test_points"]:
    cases.append(tp_to_tc(tp))

print(f"[S6 Gen] Generated {len(cases)} test cases")

# ── summary ──────────────────────────────────────────────────────────────────
by_module = defaultdict(int)
by_priority = defaultdict(int)
for c in cases:
    by_module[c["module"]] += 1
    by_priority[c["priority"]] += 1

print(f"[S6 Gen] Module: {dict(by_module)}")
print(f"[S6 Gen] Priority: {dict(by_priority)}")

# ── write JSON ────────────────────────────────────────────────────────────────
out_json = {
    "meta": {
        "req_name": REQ_NAME,
        "stage": "S6",
        "stage_name": "测试用例生成",
        "version": VERSION,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "created_by": "AIDocxWorkFlow-Round4",
        "dependencies": {
            "S2": VERSION,
            "S5": VERSION,
            "S4": VERSION
        }
    },
    "summary": {
        "total_tc_count": len(cases),
        "by_module": dict(by_module),
        "by_priority": dict(by_priority),
        "coverage": {
            "obj_coverage": f"{len(set(c['obj_id'] for c in cases))}/{len(obj_data['objects'])}",
            "fp_coverage": f"{len(set(c['feature_point_ref'] for c in cases))}/57",
            "tp_coverage": f"{len(cases)}/{len(tp_data['test_points'])}"
        }
    },
    "test_cases": cases
}

json_path = OUT_DIR / "test_cases.json"
with json_path.open("w", encoding="utf-8") as f:
    json.dump(out_json, f, ensure_ascii=False, indent=2)
print(f"[S6 Gen] JSON → {json_path}")

# ── write Markdown ────────────────────────────────────────────────────────────
md_lines = [
    f"# 测试用例 — {REQ_NAME} {VERSION}\n",
    f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
    f"用例总数：{len(cases)}\n\n",
    f"## 用例列表\n\n",
    "| 用例ID | 模块 | 用例描述 | 功能描述 | 前置条件 | 操作步骤 | 预期结果 | 优先级 | 用例状态 | 备注 |\n",
    "|---|---|---|---|---|---|---|---|---|---|\n"
]

for c in cases:
    precond_str = "；".join(c["前置条件"])
    steps_str = "；".join(f"步骤{s['step_num']}：{s['action']}" for s in c["steps"])
    expected_str = "；".join(c["expected_results"])
    md_lines.append(
        f"| {c['case_id']} | {c['module']} | {c['用例描述']} | {c['功能描述']} | "
        f"{precond_str} | {steps_str} | {expected_str} | {c['priority']} | {c['用例状态']} | {c['备注']} |\n"
    )

md_path = OUT_DIR / "test_cases.md"
with md_path.open("w", encoding="utf-8") as f:
    f.writelines(md_lines)
print(f"[S6 Gen] Markdown → {md_path}")

# ── write Excel ──────────────────────────────────────────────────────────────
try:
    import openpyxl
    from openpyxl.styles import Font

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    headers = ["用例ID", "模块", "用例描述", "功能描述", "前置条件", "操作步骤",
               "预期结果", "优先级", "用例状态", "备注"]

    def make_sheet(name: str, case_list: list) -> None:
        ws = wb.create_sheet(name)
        ws.append(headers)
        for c in case_list:
            precond_str = "\n".join(c["前置条件"])
            steps_str = "\n".join(f"{s['step_num']}. {s['action']}" for s in c["steps"])
            expected_str = "\n".join(c["expected_result"])
            ws.append([
                c["case_id"], c["module"], c["用例描述"], c["功能描述"],
                precond_str, steps_str, expected_str, c["priority"],
                c["用例状态"], c.get("备注", "")
            ])
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

    ready_cases = [c for c in cases if c["用例状态"] == "Ready"]
    draft_cases = [c for c in cases if c["用例状态"] != "Ready"]

    make_sheet("测试用例", ready_cases if ready_cases else cases[:1] if cases else [])
    make_sheet("Draft-Rejected附录", draft_cases if draft_cases else [])

    xlsx_path = OUT_DIR / "test_cases.xlsx"
    wb.save(str(xlsx_path))
    print(f"[S6 Gen] XLSX → {xlsx_path}")
except ImportError:
    print("[S6 Gen] openpyxl not available, skipping XLSX")

print("[S6 Gen] Done.")
print(f"TC count: {len(cases)}")
print(f"Module distribution: {dict(by_module)}")
print(f"Priority distribution: {dict(by_priority)}")
