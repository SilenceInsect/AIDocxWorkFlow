#!/usr/bin/env python3
"""T-106 regression baseline runner (canonical v18-aligned path).

Uses run_normalize_and_export main() pipeline which:
- reads v3.01 test_cases.json (raw, on disk)
- normalizes in-memory (case_id + bilingual alias mirroring)
- evaluates L1 via L1S6Validator (required/id/trace) + L2 lenient (SSOT field presence)
- does NOT write the JSON back (write_artifact=False default)
- writes the xlsx as a side-effect (in-place, idempotent)

v18 baseline (round18_audit_round18.md §2):
  input_cases=331, merged_cases=87
  l1_passed=true, required_errors=0, id_errors=0, trace_errors=0
  l2_passed=true, l2_failed_count=0
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/gleon/Documents/TestDev/AIDocxWorkFlow")
TC_JSON = REPO / "workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json"
XLSX = REPO / "workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx"
OBJS = REPO / "workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」/requirement_objects.json"
TPS = REPO / "workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json"


def main():
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "ai_workflow"))

    print(f"=== T-106 v3.01 L1∧L2 regression baseline (canonical path) ===")
    print(f"src: {TC_JSON}")
    print(f"xlsx: {XLSX}")
    print()

    # Snapshot pre-state
    tc_pre = json.loads(TC_JSON.read_text(encoding="utf-8"))
    if isinstance(tc_pre, dict):
        pre_cases = tc_pre.get("test_cases", [])
    else:
        pre_cases = tc_pre
    print(f"raw JSON case count: {len(pre_cases)}")

    xlsx_sha_pre = ""
    if XLSX.exists():
        import hashlib
        xlsx_sha_pre = hashlib.sha256(XLSX.read_bytes()).hexdigest()
        print(f"xlsx sha256 (pre): {xlsx_sha_pre}")

    # Run canonical baseline
    from ai_workflow.run_normalize_and_export import normalize_and_export, _summary_for_stdout

    summary = normalize_and_export(
        src_json=TC_JSON,
        xlsx_out=XLSX,
        objs_json=OBJS if OBJS.exists() else None,
        tps_json=TPS if TPS.exists() else None,
        xlsx_backup=True,
        write_artifact=False,
        l2_mode="lenient",
    )

    # Strip writeback_disabled before printing for clarity
    out = _summary_for_stdout(summary)
    print()
    print("--- canonical pipeline output (summary) ---")
    print(json.dumps(out, ensure_ascii=False, indent=2))

    # Extract L1 stats
    l1 = summary["evaluation"]["l1_result"]
    l2 = summary["evaluation"]["l2_result"]
    print()
    print(f"--- L1 detailed ---")
    print(f"l1.passed: {l1['passed']}")
    print(f"l1.stats: {l1.get('stats', {})}")
    if l1.get("errors"):
        from collections import Counter
        cnt = Counter(e.get("type", "?") for e in l1["errors"])
        print(f"l1 error type breakdown: {dict(cnt)}")

    print(f"--- L2 detailed ---")
    print(f"l2.passed: {l2.get('passed')}")
    print(f"l2.mode: {l2.get('mode')}")
    print(f"l2.total: {l2.get('total')}")
    print(f"l2.failed_count: {l2.get('failed_count')}")
    if l2.get("failed_ids"):
        print(f"l2.failed_ids (first 5): {l2['failed_ids'][:5]}")

    # Verify JSON untouched
    tc_post = json.loads(TC_JSON.read_text(encoding="utf-8"))
    if isinstance(tc_post, dict):
        post_cases = tc_post.get("test_cases", [])
    else:
        post_cases = tc_post
    print()
    print(f"raw JSON case count (post): {len(post_cases)}  (pre={len(pre_cases)})  delta={len(post_cases)-len(pre_cases)}")
    if len(pre_cases) != len(post_cases):
        print("⚠️  WARNING: JSON case count changed (should NOT happen — write_artifact=False)")

    xlsx_sha_post = ""
    if XLSX.exists():
        import hashlib
        xlsx_sha_post = hashlib.sha256(XLSX.read_bytes()).hexdigest()
        print(f"xlsx sha256 (post): {xlsx_sha_post}  (changed: {xlsx_sha_pre != xlsx_sha_post})")

    # Verdict vs v18
    v18_l1_passed = True
    v18_l2_failed = 0
    cur_l1 = l1["passed"]
    cur_l2_fail = l2.get("failed_count", 0) or 0
    print()
    print(f"--- Verdict vs v18 baseline ---")
    print(f"v18 baseline: l1_passed={v18_l1_passed}, l2_failed_count={v18_l2_failed}")
    print(f"current:      l1_passed={cur_l1}, l2_failed_count={cur_l2_fail}")
    if cur_l1 is True and cur_l2_fail <= v18_l2_failed:
        print("RESULT: PASS (no regression vs v18)")
        return 0
    else:
        print("RESULT: FAIL (regression detected)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
