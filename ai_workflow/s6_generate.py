#!/usr/bin/env python3
"""S6 测试用例整理器（thin wrapper）— 脚本不推理，只整理。

⚠️ 设计原则（v2.0 重构 — 2026-06-15）：
- **LLM 负责推理**：从 S5 test_points.json 派生出 N 个 TC、按什么测试方法拓宽、
  每个 TC 的步骤/预期怎么写——全是 LLM 在对话/SKILL.md 引导下做。
- **脚本只负责整理**：把 LLM 输出的 case 列表做 ID 分配 / 字段归一化 / 写成
  JSON+MD+XLSX 三种格式。脚本不做"1:6.87 / 18 种方法 / 模块风险加权"等硬推导。
- 真实需求多种多样，硬指标脚本只服务一种结构。LLM 推理 + 脚本整理能适配任意结构。

用法：
    1) LLM 在对话中读取 S5 test_points.json + 8 模块模板 + S4 业务流
    2) LLM 生成 case 列表（JSON 数组）—— 不限数量、不限方法、不限结构
    3) 把 LLM 生成的 cases 粘到 test_points.json 的 `llm_generated_cases` 字段
       （或直接用环境变量/LLM tool call 传入）
    4) 本脚本读取后做 ID 分配 / 字段归一化 / 写文件

兼容旧用法：
- 如果 test_points.json 还没有 `llm_generated_cases` 字段，
  本脚本会从 S5 的 scenario_test_points 直接 1:1 转成 case（**保留 LLM 改写步骤的
  入口**：步骤/预期保留 LLM 后续在对话中改写）。
"""

from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from case_status_writer import apply_l1_l2_status, write_transition_log
from test_case_formatter import (
    _assign_ids,
    _build_summary,
    _save_md,
    _save_xlsx,
    normalize_module_name,
)
from validators.l1_s6 import L1S6Validator


REQ_NAME = "游戏道具商城系统"
S5_PATH = Path(
    "/Users/gleon/Documents/TestDev/AIDocxWorkFlow-SH/workflow_assets/游戏道具商城系统/"
    "「S5 测试点生成」/v1.0/test_points.json"
)
OUT_DIR = Path(
    "/Users/gleon/Documents/TestDev/AIDocxWorkFlow-SH/workflow_assets/游戏道具商城系统/"
    "「S6 测试用例生成」/v1.0"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _tp_to_seed_case(tp: dict, story: dict) -> dict:
    """把单个 S5 test_point 转成一个"种子 case"——结构和字段都不动。

    LLM 在后续对话中改写步骤/预期——本脚本只搬运，不推导。
    """
    return {
        # ── ID 字段（脚本最终统一分配；此处先留空字符串）──
        "case_id": "",
        # ── 8 模块字段（脚本做归一化）──
        "module": tp.get("module", ""),
        "模块": tp.get("module", ""),
        # ── 用例语义字段（保留 LLM 改写入口，原样搬运 S5）──
        "用例描述": tp.get("scenario", ""),
        "title": tp.get("scenario", ""),
        "功能描述": "",
        "前置条件": tp.get("precondition", ""),
        "precondition": tp.get("precondition", ""),
        "操作步骤": "",
        "steps": "",
        "预期结果": tp.get("expected", ""),
        "expected": tp.get("expected", ""),
        # ── 分类字段（脚本保留但不做推导）──
        "test_type": tp.get("test_type", "POSITIVE"),
        "优先级": "",  # LLM 按业务风险自由决定
        "备注": "",
        # ── 溯源字段（脚本搬运）──
        "scenario": tp.get("scenario", ""),
        "story_id": story.get("story_id", ""),
        "story_name": story.get("story_name", ""),
        "tp_id": tp.get("tp_id", ""),
        # ── S5 → S6 必传字段（Q-525：S7 覆盖率审查依赖）──
        "s4_reference": tp.get("s4_reference", ""),
        "test_type_subclass": tp.get("test_type_subclass", ""),
        "applies_rule": tp.get("applies_rule", ""),
        "is_assumed": tp.get("is_assumed", False),
    }


def collect_cases(test_points: dict) -> list:
    """从 S5 test_points.json 收集 cases。

    优先读取 `llm_generated_cases` 字段（LLM 推理后写入的）;
    兜底从 `scenario_test_points` 1:1 转种子（保留 LLM 后续改写空间）。
    """
    llm_cases = test_points.get("llm_generated_cases")
    if isinstance(llm_cases, list) and llm_cases:
        return llm_cases

    # 兜底：1:1 转种子 case，**不做任何"1:N 拓宽"或"18 种方法加权"**。
    # 这些都是 LLM 在对话中基于 S5 内容 + S4 风险点 + 模块边界推理决定的。
    cases = []
    for story in test_points.get("stories", []):
        for tp in story.get("scenario_test_points", []):
            cases.append(_tp_to_seed_case(tp, story))
    return cases


def main() -> dict:
    with S5_PATH.open(encoding="utf-8") as f:
        test_points = json.load(f)

    cases = collect_cases(test_points)
    tp_total = sum(
        len(s.get("scenario_test_points", []))
        for s in test_points.get("stories", [])
    )
    print(f"[S6] S5 测试点: {tp_total}")
    print(f"[S6] 收集到 cases: {len(cases)}（LLM 自由决定 / 兜底 1:1 转种子）")

    # ID 分配 + 模块归一化（脚本机械工作）
    cases = _assign_ids(cases, test_points)
    summary = _build_summary(cases)
    print(f"[S6] 汇总: {summary}")

    out_json = OUT_DIR / "test_cases.json"
    result_json = {
        "version": "v2.0-thin",
        "stage": "S6",
        "date": "2026-06-15",
        "req_name": REQ_NAME,
        "design_principle": "LLM 推理 + 脚本整理（thin wrapper）",
        "tp_count": tp_total,
        "tc_count": len(cases),
        "summary": summary,
        "test_cases": cases,
    }
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)

    l1_result = L1S6Validator().run_l1_check(out_json)
    status_report = apply_l1_l2_status(cases, l1_result)  # l2_result=None 退回 L1-only
    result_json["status_writeback"] = status_report
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    write_transition_log(status_report, OUT_DIR / "case_status_transitions.json")
    print(f"[S6] L1 {'PASS' if l1_result['passed'] else 'FAIL'} → {status_report['target_status']}")
    print(f"[S6] → {out_json}")

    md_path = _save_md(cases, OUT_DIR)
    print(f"[S6] → {md_path}")

    try:
        xlsx_path = _save_xlsx(cases, OUT_DIR)
        print(f"[S6] → {xlsx_path}")
    except Exception as e:
        print(f"[S6] xlsx 写入失败（可忽略）: {e}")

    return summary


def self_test() -> int:
    """Verify seed cases omit status and L1∧L2 writeback owns assignment."""
    seed = _tp_to_seed_case({"module": "UI", "scenario": "场景", "tp_id": "TP-001"}, {})
    assert "用例状态" not in seed

    # 主测试：L1 pass + L2 pass → Ready（双通过语义）
    seed_pass = _tp_to_seed_case({"module": "UI", "scenario": "场景", "tp_id": "TP-002"}, {})
    report_pass = apply_l1_l2_status([seed_pass], {"passed": True}, {"passed": True, "failed_ids": []})
    assert seed_pass["用例状态"] == "Ready", f"L1+L2 PASS 应写 Ready，实际: {seed_pass['用例状态']}"
    assert report_pass["l1_passed"] is True
    assert report_pass["l2_passed"] is True
    assert report_pass["target_status"] == "Ready"

    # 边界 1：L1 FAIL → Draft
    seed_l1_fail = _tp_to_seed_case({"module": "UI", "scenario": "场景", "tp_id": "TP-003"}, {})
    report_l1_fail = apply_l1_l2_status([seed_l1_fail], {"passed": False, "errors": []})
    assert seed_l1_fail["用例状态"] == "Draft", f"L1 FAIL 应写 Draft，实际: {seed_l1_fail['用例状态']}"
    assert report_l1_fail["target_status"] == "Draft"

    # 边界 2：L1 pass + L2 FAIL → Draft（阻断语义）
    seed_l2_fail = _tp_to_seed_case({"module": "UI", "scenario": "场景", "tp_id": "TP-004"}, {})
    report_l2_fail = apply_l1_l2_status([seed_l2_fail], {"passed": True}, {"passed": False, "failed_ids": ["TP-004"]})
    assert seed_l2_fail["用例状态"] == "Draft", f"L2 FAIL 应写 Draft（即使 L1 PASS），实际: {seed_l2_fail['用例状态']}"
    assert report_l2_fail["l1_passed"] is True
    assert report_l2_fail["l2_passed"] is False
    assert report_l2_fail["target_status"] == "Draft"

    # 边界 3：l2_result=None → 退回 L1-only（向后兼容）
    seed_compat = _tp_to_seed_case({"module": "UI", "scenario": "场景", "tp_id": "TP-005"}, {})
    report_compat = apply_l1_l2_status([seed_compat], {"passed": True}, l2_result=None)
    assert seed_compat["用例状态"] == "Ready"
    assert report_compat["l2_passed"] is True  # None 时视为通过

    print("s6_generate self-test: PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    main()
