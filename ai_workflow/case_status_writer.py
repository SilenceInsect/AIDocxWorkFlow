#!/usr/bin/env python3
"""Write S6 case statuses from an L1S6Validator result."""

from __future__ import annotations

import json
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any


STATUS_FIELD = "用例状态"
VALID_CASE_STATUSES = {"Draft", "Ready", "Rejected", "Deprecated"}


def apply_l1_l2_status(
    test_cases: list[dict[str, Any]],
    l1_result: Mapping[str, Any],
    l2_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Set every case to Ready on L1 ∧ L2 pass, otherwise Draft.

    向后兼容：l2_result 为 None 时退回旧 L1-only 行为（L1 pass → Ready）。
    """
    l1_passed = l1_result.get("passed") is True
    if l2_result is None:
        # 向后兼容：旧 L1-only 行为
        l2_passed = True  # 不阻断
        target_status = "Ready" if l1_passed else "Draft"
    else:
        l2_passed = l2_result.get("passed") is True
        target_status = "Ready" if (l1_passed and l2_passed) else "Draft"
    transitions: list[dict[str, str]] = []

    for index, test_case in enumerate(test_cases):
        previous_status = str(test_case.get(STATUS_FIELD, ""))
        test_case[STATUS_FIELD] = target_status
        if previous_status != target_status:
            transitions.append({
                "case_id": str(test_case.get("case_id") or test_case.get("tc_id") or f"#{index}"),
                "from": previous_status,
                "to": target_status,
            })

    return {
        "source": "L1S6Validator+L2S6Validator",
        "l1_passed": l1_passed,
        "l2_passed": l2_passed,
        "target_status": target_status,
        "total_cases": len(test_cases),
        "changed_cases": len(transitions),
        "transitions": transitions,
    }


# ---------------------------------------------------------------------------
# Per-case writeback (Round 12 / v17 field-traceability redefinition)
# ---------------------------------------------------------------------------

def _case_ids_with_errors(l1_result: Mapping[str, Any]) -> set[str]:
    """Extract the set of case_ids that have at least one L1 error.

    Falls back to empty set if the result does not carry per-case error
    attribution — that means "we cannot decide per-case, assume all failed".
    """
    raw_errors = l1_result.get("errors") or []
    ids: set[str] = set()
    for err in raw_errors:
        if not isinstance(err, Mapping):
            continue
        case_id = err.get("id")
        if isinstance(case_id, str) and case_id:
            ids.add(case_id)
    return ids


def _case_ids_with_l2_failures(l2_result: Mapping[str, Any]) -> set[str]:
    """Extract the set of case_ids that L2 marked as failed.

    Mirrors the lenient mode contract used by case_id_and_field_normalizer:
    ``l2_result["failed_ids"]`` carries the case_ids the validator pinned
    against.
    """
    raw = l2_result.get("failed_ids") or []
    return {str(cid) for cid in raw if isinstance(cid, (str, int))}


def apply_l1_l2_status_per_case(
    test_cases: list[dict[str, Any]],
    l1_result: Mapping[str, Any],
    l2_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Per-case writeback — each case is independently classified.

    Rules:
    - Case passes L1 AND (L2 skipped OR L2 pass) → ``Ready``
    - Otherwise → ``Draft``
    - Pre-existing ``Rejected`` / ``Deprecated`` are NOT overwritten (S7 /
      S8 territory); caller must run the corresponding writer first.
    - Empty ``l1_result["errors"]`` is treated as "no per-case attribution"
      and the function falls back to bulk behavior to remain safe.

    Returns a report dict mirroring ``apply_l1_l2_status`` shape but with
    per-case transitions.
    """
    frozen_statuses = {"Rejected", "Deprecated"}
    l2_skipped = l2_result is None
    l2_global_pass = l2_skipped or l2_result.get("passed") is True

    l1_failed_ids = _case_ids_with_errors(l1_result)
    l2_failed_ids = set() if l2_skipped else _case_ids_with_l2_failures(l2_result)

    transitions: list[dict[str, str]] = []
    ready_count = 0
    draft_count = 0
    frozen_count = 0

    for index, test_case in enumerate(test_cases):
        if not isinstance(test_case, dict):
            continue
        case_id = str(
            test_case.get("case_id") or test_case.get("tc_id") or f"#{index}"
        )
        previous_status = str(test_case.get(STATUS_FIELD, ""))
        if previous_status in frozen_statuses:
            frozen_count += 1
            continue  # leave Rejected/Deprecated untouched

        # If l1_result lacks per-case attribution (e.g., legacy callers), use
        # bulk behavior to stay safe.
        if not l1_result.get("errors"):
            target = "Ready" if (l2_skipped or l2_global_pass) else "Draft"
        else:
            l1_ok = case_id not in l1_failed_ids
            l2_ok = l2_skipped or l2_global_pass or (case_id not in l2_failed_ids)
            target = "Ready" if (l1_ok and l2_ok) else "Draft"

        test_case[STATUS_FIELD] = target
        if previous_status != target:
            transitions.append({
                "case_id": case_id,
                "from": previous_status,
                "to": target,
            })
        if target == "Ready":
            ready_count += 1
        else:
            draft_count += 1

    return {
        "source": "L1S6Validator+L2S6Validator[per-case]",
        "l1_passed": l1_result.get("passed") is True,
        "l2_passed": l2_global_pass,
        "target_status": None,  # per-case, no global target
        "total_cases": len(test_cases),
        "ready_count": ready_count,
        "draft_count": draft_count,
        "frozen_count": frozen_count,
        "transitions": transitions,
    }


# 向后兼容别名：保留旧函数名（l2_result=None 走 L1-only）
def apply_l1_status(
    test_cases: list[dict[str, Any]],
    l1_result: Mapping[str, Any],
) -> dict[str, Any]:
    """旧 API 别名：仅 L1 校验，无 L2."""
    return apply_l1_l2_status(test_cases, l1_result, l2_result=None)


def write_transition_log(report: Mapping[str, Any], output_path: Path | str) -> Path:
    """Persist a status transition report for auditability."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def apply_l1_l2_status_to_artifact(
    artifact_path: Path | str,
    l1_result: Mapping[str, Any],
    l2_result: Mapping[str, Any] | None = None,
    transition_log_path: Path | str | None = None,
) -> dict[str, Any]:
    """Update a list or object-form test_cases JSON artifact in place.

    向后兼容：l2_result 为 None 时退回旧 L1-only 行为。
    """
    path = Path(artifact_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        test_cases = payload
    elif isinstance(payload, dict) and isinstance(payload.get("test_cases"), list):
        test_cases = payload["test_cases"]
    else:
        raise ValueError("test case artifact must be a list or contain test_cases[]")

    report = apply_l1_l2_status(test_cases, l1_result, l2_result=l2_result)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if transition_log_path is not None:
        write_transition_log(report, transition_log_path)
    return report


# 向后兼容别名
def apply_l1_status_to_artifact(
    artifact_path: Path | str,
    l1_result: Mapping[str, Any],
    transition_log_path: Path | str | None = None,
) -> dict[str, Any]:
    """旧 API 别名：仅 L1 校验。"""
    return apply_l1_l2_status_to_artifact(
        artifact_path, l1_result, l2_result=None, transition_log_path=transition_log_path
    )


def self_test() -> int:
    """Verify L1 / L1∧L2 status assignment and artifact writeback."""
    # 旧 L1-only 路径（向后兼容）
    ready_cases = [{"case_id": "UI-TC-001"}, {"case_id": "BIZ-TC-001", STATUS_FIELD: "Draft"}]
    ready_report = apply_l1_status(ready_cases, {"passed": True, "errors": []})
    assert [case[STATUS_FIELD] for case in ready_cases] == ["Ready", "Ready"]
    assert ready_report["target_status"] == "Ready"
    assert ready_report["changed_cases"] == 2

    draft_cases = [{"case_id": "UI-TC-002", STATUS_FIELD: "Ready"}]
    draft_report = apply_l1_status(draft_cases, {"passed": False, "errors": [{"type": "TEST"}]})
    assert draft_cases[0][STATUS_FIELD] == "Draft"
    assert draft_report["target_status"] == "Draft"

    # 新 L1∧L2 路径：L1 pass + L2 pass → Ready
    both_pass_cases = [{"case_id": "UI-TC-010"}, {"case_id": "UI-TC-011"}]
    both_report = apply_l1_l2_status(both_pass_cases, {"passed": True}, {"passed": True, "failed_ids": []})
    assert [case[STATUS_FIELD] for case in both_pass_cases] == ["Ready", "Ready"]
    assert both_report["target_status"] == "Ready"
    assert both_report["l1_passed"] is True
    assert both_report["l2_passed"] is True

    # 新 L1∧L2 路径：L1 pass + L2 fail → Draft
    l2_fail_cases = [{"case_id": "UI-TC-020", STATUS_FIELD: "Ready"}]
    l2_fail_report = apply_l1_l2_status(l2_fail_cases, {"passed": True}, {"passed": False, "failed_ids": ["UI-TC-020"]})
    assert l2_fail_cases[0][STATUS_FIELD] == "Draft"
    assert l2_fail_report["target_status"] == "Draft"
    assert l2_fail_report["l2_passed"] is False

    # 新 L1∧L2 路径：l2_result=None 退回 L1-only 行为
    none_l2_cases = [{"case_id": "UI-TC-030"}]
    none_l2_report = apply_l1_l2_status(none_l2_cases, {"passed": True}, l2_result=None)
    assert none_l2_cases[0][STATUS_FIELD] == "Ready"
    assert none_l2_report["l2_passed"] is True  # None 时视为通过（向后兼容）

    with tempfile.TemporaryDirectory() as tmpdir:
        artifact = Path(tmpdir) / "test_cases.json"
        log_path = Path(tmpdir) / "case_status_transitions.json"
        artifact.write_text(json.dumps({"test_cases": [{"case_id": "UI-TC-003"}]}), encoding="utf-8")
        report = apply_l1_l2_status_to_artifact(artifact, {"passed": True}, {"passed": True}, log_path)
        saved = json.loads(artifact.read_text(encoding="utf-8"))
        assert saved["test_cases"][0][STATUS_FIELD] == "Ready"
        assert json.loads(log_path.read_text(encoding="utf-8"))["changed_cases"] == 1
        assert report["l1_passed"] is True
        assert report["l2_passed"] is True

    print("case_status_writer self-test: PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    raise SystemExit("usage: python3 ai_workflow/case_status_writer.py --self-test")
