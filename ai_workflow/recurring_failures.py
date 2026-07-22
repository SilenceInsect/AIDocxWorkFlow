#!/usr/bin/env python3
"""AIDocxWorkFlow 重复失败模式记录。

用于在阶段启动时回灌最相关的历史错误模式，
避免同类问题只能靠人工反复提醒。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_workflow.runtime_contracts import WORKFLOW_ROOT

GOVERNANCE_DIR = WORKFLOW_ROOT / "_governance"
FAILURES_PATH = GOVERNANCE_DIR / "recurring_failures.json"

DEFAULT_FAILURES = [
    {
        "id": "RF-001",
        "stage": "S5",
        "pattern": "coding_mindset_shrink",
        "symptom": "只覆盖主路径，异常/边界/状态切换场景静默消失",
        "prevent_by": [
            "stage_context.global_mission",
            "coverage_ledger",
            "omission_ledger",
        ],
        "severity": "high",
    },
    {
        "id": "RF-002",
        "stage": "S6",
        "pattern": "silent_omission",
        "symptom": "未覆盖的 Story/需求对象没有出现在任何用例或遗漏账本中",
        "prevent_by": [
            "coverage_ledger",
            "omission_ledger",
            "postflight_gate",
        ],
        "severity": "high",
    },
    {
        "id": "RF-003",
        "stage": "S6",
        "pattern": "stage_local_optimization",
        "symptom": "只满足当前阶段书写规范，没有考虑 S7/S8 的审查与迭代消费",
        "prevent_by": [
            "downstream_contract",
            "read_ack",
            "stage_context",
        ],
        "severity": "medium",
    },
]

SEVERITY_ORDER = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


def ensure_failures_file() -> Path:
    GOVERNANCE_DIR.mkdir(parents=True, exist_ok=True)
    if not FAILURES_PATH.exists():
        FAILURES_PATH.write_text(
            json.dumps(DEFAULT_FAILURES, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return FAILURES_PATH


def load_failures() -> list[dict[str, Any]]:
    path = ensure_failures_file()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = list(DEFAULT_FAILURES)
    normalized = [_normalize_failure(item) for item in data if isinstance(item, dict)]
    return _sort_failures(normalized)


def load_relevant_failures(stage: str, limit: int = 3) -> list[dict[str, Any]]:
    failures = load_failures()
    relevant = [item for item in failures if item.get("stage") == stage]
    if len(relevant) < limit:
        remaining = [item for item in failures if item.get("stage") != stage]
        relevant.extend(remaining[: max(0, limit - len(relevant))])
    return relevant[:limit]


def append_failure_pattern(entry: dict[str, Any]) -> str:
    return upsert_failure_patterns([entry])["path"]


def upsert_failure_patterns(entries: list[dict[str, Any]]) -> dict[str, Any]:
    path = ensure_failures_file()
    data = load_failures()
    index_by_key = {
        _failure_key(item): idx
        for idx, item in enumerate(data)
    }

    added = 0
    updated = 0
    next_id = _next_failure_id(data)
    written_entries: list[dict[str, Any]] = []
    for raw_entry in entries:
        if not raw_entry:
            continue
        entry = _normalize_failure(raw_entry)
        key = _failure_key(entry)
        written_entries.append(entry)
        if key in index_by_key:
            data[index_by_key[key]] = _merge_failure_entry(data[index_by_key[key]], entry)
            updated += 1
            continue
        entry["id"] = entry.get("id") or f"RF-{next_id:03d}"
        next_id += 1
        data.append(entry)
        index_by_key[key] = len(data) - 1
        added += 1

    data = _sort_failures(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "path": str(path),
        "added": added,
        "updated": updated,
        "total": len(data),
        "entries": written_entries,
    }


def build_failures_from_review_report(review_report: dict[str, Any]) -> list[dict[str, Any]]:
    reviewer_a = review_report.get("reviewer_a", {})
    reviewer_b = review_report.get("reviewer_b", {})
    snapshot = review_report.get("snapshot", {})
    s5_structure = snapshot.get("s5_structure") or {}
    entries: list[dict[str, Any]] = []

    missing_case_fields = reviewer_a.get("field_name_violations", [])
    if missing_case_fields:
        fields = sorted({str(item.get("field", "")).strip() for item in missing_case_fields if item.get("field")})
        entries.append({
            "stage": "S6",
            "pattern": "field_completion_gap",
            "symptom": f"S7 审查发现 S6 用例必填字段缺失（{', '.join(fields[:3]) or 'unknown'}）",
            "prevent_by": ["read_ack", "postflight_gate", "test_cases.json"],
            "severity": "medium",
            "source_stage": "S7",
            "source_artifact": "review_report.json",
            "evidence": {
                "missing_field_count": len(missing_case_fields),
                "sample_case_ids": [
                    item.get("case_id")
                    for item in missing_case_fields[:5]
                    if item.get("case_id")
                ],
            },
        })

    uncovered_risks = reviewer_b.get("uncovered_risks", [])
    if uncovered_risks:
        entries.append({
            "stage": "S6",
            "pattern": "coverage_gap",
            "symptom": "S7 审查发现 S6 coverage ledger 仍有 partial/uncovered Story",
            "prevent_by": ["coverage_ledger", "omission_ledger", "postflight_gate"],
            "severity": "high",
            "source_stage": "S7",
            "source_artifact": "review_report.json",
            "evidence": {
                "story_ids": [item.get("story_id") for item in uncovered_risks[:5] if item.get("story_id")],
                "count": len(uncovered_risks),
            },
        })

    missing_tp_fields = s5_structure.get("missing_field_cases", [])
    if missing_tp_fields:
        fields = sorted({str(item.get("field", "")).strip() for item in missing_tp_fields if item.get("field")})
        entries.append({
            "stage": "S5",
            "pattern": "test_point_schema_gap",
            "symptom": f"S7 审查发现 S5 TP 关键字段缺失（{', '.join(fields[:3]) or 'unknown'}）",
            "prevent_by": ["stage_context", "coverage_ledger", "omission_ledger"],
            "severity": "high",
            "source_stage": "S7",
            "source_artifact": "review_report.json",
            "evidence": {
                "missing_field_count": len(missing_tp_fields),
                "sample_tp_ids": [
                    item.get("tp_id")
                    for item in missing_tp_fields[:5]
                    if item.get("tp_id")
                ],
            },
        })

    return entries


def build_failures_from_iteration_result(iteration_result: dict[str, Any]) -> list[dict[str, Any]]:
    fact_summary = iteration_result.get("fact_summary", {})
    defect_frequencies = iteration_result.get("defect_frequencies", {})
    by_root_cause = defect_frequencies.get("by_root_cause", {})
    entries: list[dict[str, Any]] = []

    if fact_summary.get("s4_reference_fill_rate", 1.0) < 1.0:
        entries.append({
            "stage": "S5",
            "pattern": "s4_reference_gap",
            "symptom": "S8 聚合发现 S5 的 s4_reference 填充率未闭合",
            "prevent_by": ["stage_context", "coverage_ledger", "review_report.json"],
            "severity": "high",
            "source_stage": "S8",
            "source_artifact": "iteration.json",
            "evidence": {
                "s4_reference_fill_rate": fact_summary.get("s4_reference_fill_rate", 0.0),
            },
        })

    if fact_summary.get("applies_rule_fill_rate", 1.0) < 1.0:
        entries.append({
            "stage": "S5",
            "pattern": "rule_trace_gap",
            "symptom": "S8 聚合发现 S5 的 applies_rule 填充率未闭合",
            "prevent_by": ["stage_context", "read_ack", "review_report.json"],
            "severity": "medium",
            "source_stage": "S8",
            "source_artifact": "iteration.json",
            "evidence": {
                "applies_rule_fill_rate": fact_summary.get("applies_rule_fill_rate", 0.0),
            },
        })

    for root_cause, count in by_root_cause.items():
        stage = _stage_from_root_cause(root_cause)
        if not stage or not count:
            continue
        entries.append({
            "stage": stage,
            "pattern": "root_cause_recurrence",
            "symptom": f"S8 聚合发现 {root_cause} 相关缺陷重复出现 {count} 次",
            "prevent_by": _default_prevent_by(stage),
            "severity": "high" if int(count) >= 3 else "medium",
            "source_stage": "S8",
            "source_artifact": "iteration.json",
            "evidence": {
                "root_cause": root_cause,
                "count": int(count),
            },
        })

    return entries


def _normalize_failure(entry: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now().isoformat(timespec="seconds")
    normalized = dict(entry)
    normalized["stage"] = str(normalized.get("stage", "")).upper()
    normalized["pattern"] = str(normalized.get("pattern", "")).strip()
    normalized["symptom"] = str(normalized.get("symptom", "")).strip()
    normalized["severity"] = str(normalized.get("severity", "medium")).lower()
    normalized["prevent_by"] = sorted({
        str(item).strip()
        for item in normalized.get("prevent_by", [])
        if str(item).strip()
    })
    normalized["occurrence_count"] = int(normalized.get("occurrence_count", 1) or 1)
    normalized["first_seen_at"] = normalized.get("first_seen_at") or now
    normalized["last_seen_at"] = normalized.get("last_seen_at") or now
    normalized["status"] = normalized.get("status") or "open"
    return normalized


def _failure_key(entry: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(entry.get("stage", "")).upper(),
        str(entry.get("pattern", "")).strip().lower(),
        str(entry.get("symptom", "")).strip(),
    )


def _merge_failure_entry(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    merged["severity"] = _max_severity(existing.get("severity"), incoming.get("severity"))
    merged["prevent_by"] = sorted({
        *existing.get("prevent_by", []),
        *incoming.get("prevent_by", []),
    })
    merged["occurrence_count"] = int(existing.get("occurrence_count", 1) or 1) + int(incoming.get("occurrence_count", 1) or 1)
    merged["last_seen_at"] = incoming.get("last_seen_at") or existing.get("last_seen_at")
    merged["first_seen_at"] = existing.get("first_seen_at") or incoming.get("first_seen_at")
    merged["source_stage"] = incoming.get("source_stage") or existing.get("source_stage")
    merged["source_artifact"] = incoming.get("source_artifact") or existing.get("source_artifact")
    if incoming.get("evidence"):
        merged["evidence"] = incoming["evidence"]
    return merged


def _sort_failures(failures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        failures,
        key=lambda item: (
            -SEVERITY_ORDER.get(str(item.get("severity", "medium")).lower(), 1),
            -int(item.get("occurrence_count", 1) or 1),
            str(item.get("last_seen_at", "")),
            str(item.get("id", "")),
        ),
        reverse=False,
    )


def _max_severity(left: str | None, right: str | None) -> str:
    left_norm = str(left or "medium").lower()
    right_norm = str(right or "medium").lower()
    return left_norm if SEVERITY_ORDER.get(left_norm, 1) >= SEVERITY_ORDER.get(right_norm, 1) else right_norm


def _next_failure_id(entries: list[dict[str, Any]]) -> int:
    max_id = 0
    for entry in entries:
        raw = str(entry.get("id", ""))
        if raw.startswith("RF-"):
            try:
                max_id = max(max_id, int(raw.split("-")[1]))
            except Exception:
                continue
    return max_id + 1


def _stage_from_root_cause(root_cause: str) -> str | None:
    upper = str(root_cause).upper()
    for stage in ("S5", "S6", "S7", "S8"):
        if upper.startswith(stage):
            return stage
    return None


def _default_prevent_by(stage: str) -> list[str]:
    if stage == "S5":
        return ["stage_context", "coverage_ledger", "omission_ledger"]
    if stage == "S6":
        return ["coverage_ledger", "omission_ledger", "postflight_gate"]
    if stage == "S7":
        return ["review_report.json", "coverage_ledger", "omission_ledger"]
    if stage == "S8":
        return ["review_report.json", "feedback_logs", "iteration.json"]
    return ["stage_context"]
