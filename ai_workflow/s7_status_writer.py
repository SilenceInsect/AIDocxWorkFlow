#!/usr/bin/env python3
"""Write S7 rejection status without changing the review engine."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


STATUS_FIELD = "用例状态"
NOTE_FIELD = "备注"  # v31 新增：Rejected 时写入被拒原因


def _must_fix_items(review_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    recommendations = review_report.get("recommendations", {})
    if not isinstance(recommendations, Mapping):
        return []
    items = recommendations.get("must_fix", [])
    if not isinstance(items, list):
        return []
    # v31 修复：支持 SKILL.md §1.6 的 MUST / SHOULD / COULD 三级枚举，
    # 兼容旧版 LLM 输出的 MUST_FIX / SHOULD_FIX / COULD_FIX 别名。
    return [
        item for item in items
        if isinstance(item, dict) and str(item.get("severity", "")).upper() in {"MUST_FIX", "MUST"}
    ]


def apply_s7_rejection_status(
    test_cases: list[dict[str, Any]],
    review_report: Mapping[str, Any],
) -> dict[str, Any]:
    """Change Ready cases to Rejected when S7 reports a MUST_FIX item.

    v31 新增：Rejected 状态的用例同时写入被拒原因到「备注」字段，
    格式为 [S7 Reject] <M-NNN>: <description>（取 must_fix 列表第一条），
    便于人工审查时直接看到被打回的原因。备注字段不存在时跳过（向后兼容）。
    """
    must_fix_items = _must_fix_items(review_report)
    transitions: list[dict[str, str]] = []
    if must_fix_items:
        first = must_fix_items[0]
        reason = f"[S7 Reject] {first.get('id', 'M-???')}: {first.get('description', '')}"
        for index, test_case in enumerate(test_cases):
            if test_case.get(STATUS_FIELD) != "Ready":
                continue
            test_case[STATUS_FIELD] = "Rejected"
            # v31 新增：写入被拒原因到备注字段（向后兼容：字段不存在则跳过）
            if "备注" in test_case or "notes" in test_case:
                note_key = "备注" if "备注" in test_case else "notes"
                existing = str(test_case.get(note_key, "")).strip()
                test_case[note_key] = (existing + (" | " if existing else "") + reason) if reason else existing
            transitions.append({
                "case_id": str(test_case.get("case_id") or test_case.get("tc_id") or f"#{index}"),
                "from": "Ready",
                "to": "Rejected",
                "reason": reason,
            })

    return {
        "source": "review_report.recommendations.must_fix",
        "must_fix_detected": bool(must_fix_items),
        "must_fix_ids": [str(item.get("id", "")) for item in must_fix_items if item.get("id")],
        "changed_cases": len(transitions),
        "transitions": transitions,
    }


def apply_s7_rejection_to_artifact(
    artifact_path: Path | str,
    review_report: Mapping[str, Any],
    transition_log_path: Path | str | None = None,
) -> dict[str, Any]:
    """Update Ready statuses in a list or object-form JSON artifact."""
    path = Path(artifact_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        test_cases = payload
    elif isinstance(payload, dict) and isinstance(payload.get("test_cases"), list):
        test_cases = payload["test_cases"]
    else:
        raise ValueError("test case artifact must be a list or contain test_cases[]")

    report = apply_s7_rejection_status(test_cases, review_report)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if transition_log_path is not None:
        log_path = Path(transition_log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def self_test() -> int:
    """Verify MUST_FIX rejection with notes write, no-op behavior, and overall-field independence."""
    # Case 1: MUST_FIX → Rejected + 备注写入
    cases = [
        {"case_id": "UI-TC-001", STATUS_FIELD: "Ready", "备注": ""},
        {"case_id": "UI-TC-002", STATUS_FIELD: "Draft", "备注": "已有注释"},
        {"case_id": "UI-TC-003", STATUS_FIELD: "Deprecated", "备注": ""},
    ]
    report = apply_s7_rejection_status(cases, {
        "overall_pass": True,
        "recommendations": {"must_fix": [{"id": "M-001", "severity": "MUST_FIX", "description": "前置条件缺少具体数值"}]},
    })
    assert [case[STATUS_FIELD] for case in cases] == ["Rejected", "Draft", "Deprecated"], f"Case 1 status: {[case[STATUS_FIELD] for case in cases]}"
    assert "备注" in cases[0], "Case 1 missing 备注 field"
    assert "[S7 Reject] M-001: 前置条件缺少具体数值" in cases[0]["备注"], f"Case 1 notes: {cases[0]['备注']}"
    assert cases[1]["备注"] == "已有注释", f"Case 2 notes should be unchanged: {cases[1]['备注']}"
    assert cases[2]["备注"] == "", f"Case 3 notes should be empty: {cases[2]['备注']}"
    assert report["must_fix_detected"] is True
    assert report["changed_cases"] == 1

    # Case 2: SHOULD_FIX is NOT a rejection trigger
    unchanged = [{"case_id": "BIZ-TC-001", STATUS_FIELD: "Ready", "备注": ""}]
    report = apply_s7_rejection_status(unchanged, {
        "overall": "FAIL",
        "recommendations": {"must_fix": [{"id": "S-001", "severity": "SHOULD_FIX"}]},
    })
    assert unchanged[0][STATUS_FIELD] == "Ready", f"Case 2 should stay Ready: {unchanged[0][STATUS_FIELD]}"
    assert report["changed_cases"] == 0

    # Case 3: MUST severity (new alias) also triggers rejection
    cases3 = [{"case_id": "UI-TC-010", STATUS_FIELD: "Ready", "备注": ""}]
    report3 = apply_s7_rejection_status(cases3, {
        "recommendations": {"must_fix": [{"id": "M-002", "severity": "MUST", "description": "步骤描述过于笼统"}]},
    })
    assert cases3[0][STATUS_FIELD] == "Rejected"
    assert "[S7 Reject] M-002: 步骤描述过于笼统" in cases3[0]["备注"]

    print("s7_status_writer self-test: PASS (3 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    raise SystemExit("usage: python3 ai_workflow/s7_status_writer.py --self-test")
