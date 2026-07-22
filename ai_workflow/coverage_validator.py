#!/usr/bin/env python3
"""AIDocxWorkFlow 覆盖账本与遗漏账本生成器。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCENARIO_FAMILIES = [
    "positive",
    "boundary",
    "negative",
    "exception",
    "config_change",
    "permission_role",
    "state_transition",
    "concurrency_timing",
    "recovery_rollback",
    "observability_hint_log",
]

MODULE_NORMALIZE = {
    "界面": "UI",
    "业务": "BIZ",
    "配置": "CONFIG",
    "辅助": "UTIL",
    "关联": "LINK",
    "日志": "LOG",
    "特殊": "SPECIAL",
    "提示": "HINT",
    "UI": "UI",
    "BIZ": "BIZ",
    "CONFIG": "CONFIG",
    "UTIL": "UTIL",
    "LINK": "LINK",
    "LOG": "LOG",
    "SPECIAL": "SPECIAL",
    "HINT": "HINT",
    "ui": "UI",
    "biz": "BIZ",
    "config": "CONFIG",
    "UTIL": "UTIL",
    "link": "LINK",
    "log": "LOG",
    "special": "SPECIAL",
    "hint": "HINT",
}

TP_TYPE_TO_FAMILY = {
    "POSITIVE": "positive",
    "BOUNDARY": "boundary",
    "NEGATIVE": "negative",
    "EXCEPTION": "exception",
}


def _load_json(source: dict | list | str | Path) -> dict | list:
    if isinstance(source, (dict, list)):
        return source
    path = Path(source)
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_module(value: str | None) -> str:
    if not value:
        return "BIZ"
    return MODULE_NORMALIZE.get(str(value).strip(), str(value).strip().upper())


def _text_blob(*parts: Any) -> str:
    items: list[str] = []
    for part in parts:
        if part is None:
            continue
        if isinstance(part, list):
            items.extend(str(x) for x in part)
        else:
            items.append(str(part))
    return " ".join(items).lower()


def _infer_expected_families(story: dict[str, Any]) -> list[str]:
    blob = _text_blob(
        story.get("title"),
        story.get("module"),
        story.get("acceptance_criteria", []),
        story.get("precondition"),
        story.get("expected_output"),
    )
    families = {"positive", "boundary", "negative", "exception"}
    module = _normalize_module(story.get("module"))

    if module == "CONFIG" or any(word in blob for word in ("配置", "热更", "生效", "失效", "折扣", "vip")):
        families.add("config_change")
    if any(word in blob for word in ("权限", "角色", "管理员", "vip", "等级")):
        families.add("permission_role")
    if any(word in blob for word in ("状态", "切换", "开启", "关闭", "上下架", "到账", "锁定")):
        families.add("state_transition")
    if any(word in blob for word in ("并发", "同时", "重复", "竞态", "库存", "支付", "订单", "同步")):
        families.add("concurrency_timing")
    if any(word in blob for word in ("回滚", "恢复", "补偿", "重试", "失败恢复", "容错")):
        families.add("recovery_rollback")
    if module in {"LOG", "HINT"} or any(word in blob for word in ("提示", "toast", "弹窗", "红点", "日志", "邮件")):
        families.add("observability_hint_log")

    return [family for family in SCENARIO_FAMILIES if family in families]


def _infer_observed_families(entry: dict[str, Any]) -> set[str]:
    families: set[str] = set()
    tp_type = str(entry.get("test_point_type", "")).upper()
    if tp_type in TP_TYPE_TO_FAMILY:
        families.add(TP_TYPE_TO_FAMILY[tp_type])

    blob = _text_blob(
        entry.get("description"),
        entry.get("scenario"),
        entry.get("用例描述"),
        entry.get("功能描述"),
        entry.get("precondition"),
        entry.get("test_steps"),
        entry.get("expected_result"),
        entry.get("module"),
    )
    module = _normalize_module(entry.get("module"))

    if module == "CONFIG" or any(word in blob for word in ("配置", "热更", "生效", "失效", "折扣", "vip")):
        families.add("config_change")
    if any(word in blob for word in ("权限", "角色", "管理员", "vip", "等级")):
        families.add("permission_role")
    if any(word in blob for word in ("状态", "切换", "开启", "关闭", "上下架", "到账", "锁定")):
        families.add("state_transition")
    if any(word in blob for word in ("并发", "同时", "重复", "竞态", "库存", "支付", "订单", "同步")):
        families.add("concurrency_timing")
    if any(word in blob for word in ("回滚", "恢复", "补偿", "重试", "失败恢复", "容错")):
        families.add("recovery_rollback")
    if module in {"LOG", "HINT"} or any(word in blob for word in ("提示", "toast", "弹窗", "红点", "日志", "埋点", "邮件")):
        families.add("observability_hint_log")
    return families


def _extract_backlog_stories(backlog_json: dict[str, Any]) -> list[dict[str, Any]]:
    stories = []
    for epic in backlog_json.get("epics", []):
        epic_id = epic.get("id", "")
        epic_module = _normalize_module(epic.get("module", epic_id.split("-")[0] if epic_id else "BIZ"))
        for story in epic.get("stories", []):
            stories.append({
                "epic_id": epic_id,
                "story_id": story.get("id", ""),
                "title": story.get("title", ""),
                "module": epic_module,
                "acceptance_criteria": story.get("acceptance_criteria", []),
                "precondition": story.get("precondition", ""),
                "expected_output": story.get("expected_output", ""),
                "requirement_objects": story.get("requirement_objects", [story.get("title", "")]),
                "function_points": story.get("acceptance_criteria", []) or [story.get("expected_output", "")],
            })
    return stories


def _extract_story_test_points(test_points_json: dict | list) -> dict[str, list[dict[str, Any]]]:
    data = _load_json(test_points_json)
    grouped: dict[str, list[dict[str, Any]]] = {}
    if isinstance(data, dict) and "stories" in data:
        for story in data["stories"]:
            grouped[story.get("story_id", "")] = list(story.get("scenario_test_points", []))
    elif isinstance(data, dict) and "test_points" in data:
        for tp in data["test_points"]:
            grouped.setdefault(tp.get("story_id", ""), []).append(tp)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "scenario_test_points" in item:
                grouped[item.get("story_id", "")] = list(item.get("scenario_test_points", []))
            elif isinstance(item, dict):
                grouped.setdefault(item.get("story_id", ""), []).append(item)
    return grouped


def _extract_story_test_cases(test_cases_json: dict | list) -> dict[str, list[dict[str, Any]]]:
    data = _load_json(test_cases_json)
    cases = data.get("test_cases", []) if isinstance(data, dict) else data
    grouped: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        story_id = (
            case.get("story_id")
            or case.get("备注")
            or case.get("remark")
            or ""
        )
        grouped.setdefault(str(story_id), []).append(case)
    return grouped


def _story_status(expected_families: list[str], observed_families: set[str], covered_by: list[str]) -> tuple[str, list[str]]:
    missing = [family for family in expected_families if family not in observed_families]
    if not covered_by:
        return "uncovered", expected_families
    if missing:
        return "partial", missing
    return "covered", []


def build_coverage_ledger_from_test_points(
    backlog_json: dict | str | Path,
    test_points_json: dict | list | str | Path,
    *,
    req_name: str,
    version: str,
) -> dict[str, Any]:
    backlog = _load_json(backlog_json)
    test_points = _extract_story_test_points(test_points_json)
    stories = _extract_backlog_stories(backlog)

    rows = []
    for story in stories:
        points = test_points.get(story["story_id"], [])
        observed_families: set[str] = set()
        covered_by: list[str] = []
        modules = {story["module"]}
        for tp in points:
            observed_families |= _infer_observed_families(tp)
            tp_id = tp.get("tp_id") or tp.get("test_point_id") or tp.get("id")
            if tp_id:
                covered_by.append(str(tp_id))
            modules.add(_normalize_module(tp.get("module")))
        expected = _infer_expected_families(story)
        status, missing = _story_status(expected, observed_families, covered_by)
        rows.append({
            "story_id": story["story_id"],
            "epic_id": story["epic_id"],
            "title": story["title"],
            "module": story["module"],
            "requirement_objects": story["requirement_objects"],
            "function_points": story["function_points"],
            "expected_scenario_families": expected,
            "covered_scenario_families": sorted(observed_families),
            "covered_by": covered_by,
            "module_coverage": sorted(modules - {""}),
            "status": status,
            "reason": "missing scenario families" if missing else "fully covered by test points",
            "missing_items": missing,
        })

    return _finalize_ledger(rows, req_name=req_name, version=version, stage="S5")


def build_coverage_ledger_from_test_cases(
    backlog_json: dict | str | Path,
    test_points_json: dict | list | str | Path,
    test_cases_json: dict | list | str | Path,
    *,
    req_name: str,
    version: str,
) -> dict[str, Any]:
    backlog = _load_json(backlog_json)
    cases = _extract_story_test_cases(test_cases_json)
    stories = _extract_backlog_stories(backlog)
    test_points = _extract_story_test_points(test_points_json)

    rows = []
    for story in stories:
        story_cases = cases.get(story["story_id"], [])
        observed_families: set[str] = set()
        covered_by: list[str] = []
        modules = {story["module"]}
        for case in story_cases:
            observed_families |= _infer_observed_families(case)
            case_id = case.get("case_id")
            if case_id:
                covered_by.append(str(case_id))
            modules.add(_normalize_module(case.get("module") or case.get("模块")))
        if not story_cases:
            for tp in test_points.get(story["story_id"], []):
                observed_families |= _infer_observed_families(tp)
        expected = _infer_expected_families(story)
        status, missing = _story_status(expected, observed_families, covered_by)
        rows.append({
            "story_id": story["story_id"],
            "epic_id": story["epic_id"],
            "title": story["title"],
            "module": story["module"],
            "requirement_objects": story["requirement_objects"],
            "function_points": story["function_points"],
            "expected_scenario_families": expected,
            "covered_scenario_families": sorted(observed_families),
            "covered_by": covered_by,
            "module_coverage": sorted(modules - {""}),
            "status": status,
            "reason": "missing scenario families or no test cases linked" if missing else "fully covered by test cases",
            "missing_items": missing,
        })

    return _finalize_ledger(rows, req_name=req_name, version=version, stage="S6")


def compute_assertion_gap_report(test_cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Round 18 FU-2 [MINOR]：S6 TC assertion 缺失统计 + 类型分布（pipeline 集成用）。

    用途：被 stage_gatekeeper.run_postflight_gate 调入，输出 gap_report 一节，
    与现有 coverage ledger / obj_fp linkage 并列写入 postflight_gate.json。
    不动现有 9 个公开函数签名（符合 §9.1.1 豁免条件 3）。

    Args:
        test_cases: S6 test_cases.json["test_cases"] 列表

    Returns:
        dict:
            {
                "total_tcs": int,
                "with_assertion": int,
                "without_assertion": int,
                "types_distribution": {
                    "numeric": int, "enum_match": int,
                    "string_contains": int, "regex_match": int,
                },
                "tc_without_assertion": list[str],  # 前 50 个 case_id 摘要
            }
    """
    total = len(test_cases)
    types_dist: dict[str, int] = {
        "numeric": 0, "enum_match": 0, "string_contains": 0, "regex_match": 0,
    }
    with_a = 0
    without_a: list[str] = []
    for tc in test_cases:
        if not isinstance(tc, dict):
            continue
        tc_id = str(tc.get("case_id", "<unknown>"))
        raw = tc.get("assertion")
        if raw is None or raw == []:
            without_a.append(tc_id)
            continue
        with_a += 1
        if isinstance(raw, list):
            for a in raw:
                if isinstance(a, dict):
                    t = str(a.get("assertion_type", "")).strip()
                    if t in types_dist:
                        types_dist[t] += 1
    return {
        "total_tcs": total,
        "with_assertion": with_a,
        "without_assertion": total - with_a,
        "types_distribution": types_dist,
        "tc_without_assertion": without_a[:50],
    }


def _finalize_ledger(rows: list[dict[str, Any]], *, req_name: str, version: str, stage: str) -> dict[str, Any]:
    covered = sum(1 for row in rows if row["status"] == "covered")
    partial = sum(1 for row in rows if row["status"] == "partial")
    uncovered = sum(1 for row in rows if row["status"] == "uncovered")
    return {
        "meta": {
            "req_name": req_name,
            "version": version,
            "stage": stage,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "scenario_family_catalog": SCENARIO_FAMILIES,
        "stories": rows,
        "summary": {
            "story_total": len(rows),
            "covered_story_count": covered,
            "partial_story_count": partial,
            "uncovered_story_count": uncovered,
        },
    }


def build_omission_ledger(coverage_ledger: dict[str, Any], *, stage: str) -> dict[str, Any]:
    omissions = []
    for row in coverage_ledger.get("stories", []):
        if row.get("status") == "covered":
            continue
        severity = "P0" if row.get("status") == "uncovered" else "P1"
        omissions.append({
            "story_id": row.get("story_id"),
            "title": row.get("title"),
            "stage": stage,
            "status": row.get("status"),
            "missing_items": row.get("missing_items", []),
            "severity": severity,
            "reason": row.get("reason"),
            "requires_human_review": row.get("status") == "uncovered",
        })
    return {
        "meta": dict(coverage_ledger.get("meta", {})),
        "omissions": omissions,
        "summary": {
            "omission_count": len(omissions),
            "requires_human_review_count": sum(1 for item in omissions if item["requires_human_review"]),
        },
    }


def validate_coverage_ledger(coverage_ledger: dict[str, Any]) -> dict[str, Any]:
    issues = []
    stories = coverage_ledger.get("stories", [])
    if not stories:
        issues.append("stories 为空")
    for row in stories:
        for field in ("story_id", "status", "expected_scenario_families", "covered_by"):
            if field not in row:
                issues.append(f"{row.get('story_id', '?')} 缺失字段 {field}")
    summary = coverage_ledger.get("summary", {})
    if summary.get("story_total") != len(stories):
        issues.append("summary.story_total 与 stories 数量不一致")
    return {
        "passed": not issues,
        "issues": issues,
        "summary": summary,
    }


def save_coverage_and_omission(
    output_dir: str | Path,
    coverage_ledger: dict[str, Any],
    omission_ledger: dict[str, Any],
) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    coverage_path = output_path / "coverage_ledger.json"
    omission_path = output_path / "omission_ledger.json"
    coverage_path.write_text(json.dumps(coverage_ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    omission_path.write_text(json.dumps(omission_ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "coverage": str(coverage_path),
        "omission": str(omission_path),
    }


# ═══════════════════════════════════════════════════════════
# Round 18 FU-2 self-test（§9.1.1 豁免条款）
# ═══════════════════════════════════════════════════════════

def self_test() -> int:
    """Round 18 FU-2 self-test：compute_assertion_gap_report 行为验证。

    验证 4 场景：
    1. 全有 assertion → with=3 / without=0 / 各类型分布正确
    2. 全无 assertion → with=0 / without=3 / tc_without_assertion 列表正确
    3. 部分缺 → with=2 / without=1 / 类型分布仅统计有的那部分
    4. 空 list → total=0 / with=0 / without=0 / 空分布
    """
    # 场景 1：全有 assertion
    r1 = compute_assertion_gap_report([
        {"case_id": "TC-A", "assertion": [
            {"assertion_type": "numeric", "assertion_target": "balance", "operator": "==", "expected_value": 0}]},
        {"case_id": "TC-B", "assertion": [
            {"assertion_type": "enum_match", "assertion_target": "status", "expected_value": "PAID"},
            {"assertion_type": "string_contains", "assertion_target": "msg", "expected_value": "成功"}]},
        {"case_id": "TC-C", "assertion": [
            {"assertion_type": "regex_match", "assertion_target": "log", "expected_value": "^\\[ERROR\\]"}]},
    ])
    assert r1["total_tcs"] == 3, f"C1 total 应 3: {r1}"
    assert r1["with_assertion"] == 3, f"C1 with 应 3: {r1}"
    assert r1["without_assertion"] == 0, f"C1 without 应 0: {r1}"
    assert r1["types_distribution"]["numeric"] == 1
    assert r1["types_distribution"]["enum_match"] == 1
    assert r1["types_distribution"]["string_contains"] == 1
    assert r1["types_distribution"]["regex_match"] == 1
    assert r1["tc_without_assertion"] == []

    # 场景 2：全无 assertion
    r2 = compute_assertion_gap_report([
        {"case_id": "TC-X"}, {"case_id": "TC-Y"}, {"case_id": "TC-Z", "assertion": []},
    ])
    assert r2["total_tcs"] == 3
    assert r2["with_assertion"] == 0
    assert r2["without_assertion"] == 3
    assert r2["tc_without_assertion"] == ["TC-X", "TC-Y", "TC-Z"]

    # 场景 3：部分缺
    r3 = compute_assertion_gap_report([
        {"case_id": "TC-1", "assertion": [{"assertion_type": "numeric", "expected_value": 1}]},
        {"case_id": "TC-2", "assertion": [{"assertion_type": "enum_match", "expected_value": "OK"}]},
        {"case_id": "TC-3"},  # 缺
    ])
    assert r3["total_tcs"] == 3
    assert r3["with_assertion"] == 2
    assert r3["without_assertion"] == 1
    assert r3["tc_without_assertion"] == ["TC-3"]
    assert r3["types_distribution"]["numeric"] == 1
    assert r3["types_distribution"]["enum_match"] == 1

    # 场景 4：空 list
    r4 = compute_assertion_gap_report([])
    assert r4["total_tcs"] == 0
    assert r4["with_assertion"] == 0
    assert r4["without_assertion"] == 0
    assert r4["types_distribution"] == {
        "numeric": 0, "enum_match": 0, "string_contains": 0, "regex_match": 0,
    }
    assert r4["tc_without_assertion"] == []

    print("[coverage_validator self-test] compute_assertion_gap_report: 4 scenarios PASS")
    return 0


def main() -> int:
    """Round 18 FU-2 CLI 入口（§9.1.1 豁免条款的 argv 分支）。"""
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "--self-test":
        return self_test()
    print("用法: python3 coverage_validator.py --self-test")
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
