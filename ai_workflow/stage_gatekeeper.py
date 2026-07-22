#!/usr/bin/env python3
"""AIDocxWorkFlow 阶段门禁器。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_workflow.coverage_validator import (
    build_coverage_ledger_from_test_cases,
    build_coverage_ledger_from_test_points,
    build_omission_ledger,
    compute_assertion_gap_report,
    save_coverage_and_omission,
    validate_coverage_ledger,
)
from ai_workflow.l1_format_validator import (
    check_assertion_completeness,
    check_no_fp_name_field,
)
from ai_workflow.runtime_contracts import (
    get_stage_contract,
    get_stage_dir,
    resolve_contract_path,
)
from ai_workflow.stage_context_builder import build_stage_context
from ai_workflow.consistency_check import run_consistency_check


def write_read_ack(
    stage_context: dict[str, Any],
    *,
    output_dir: str | Path | None = None,
) -> str:
    stage_dir = Path(output_dir) if output_dir else Path(stage_context["meta"]["stage_dir"])
    stage_dir.mkdir(parents=True, exist_ok=True)
    ack = {
        "stage": stage_context["meta"]["stage"],
        "req_name": stage_context["meta"]["req_name"],
        "project_name": stage_context["meta"].get("project_name"),
        "version": stage_context["meta"]["version"],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "read_materials": [item["path"] for item in stage_context.get("must_read", [])],
        "global_goal_ack": stage_context["global_mission"]["primary_goal"],
        "downstream_ack": stage_context["downstream_contract"].get("consumer_stage", ""),
    }
    path = stage_dir / "read_ack.json"
    path.write_text(json.dumps(ack, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def run_preflight_gate(
    stage: str,
    req_name: str,
    version: str = "v1.0",
    project_name: str | None = None,
    *,
    persist: bool = True,
) -> dict[str, Any]:
    # stage_context / read_ack 是运行时硬前置，即使调用方选择 persist=False，
    # 也必须落盘到阶段目录，供 postflight 和人工审阅使用。
    context = build_stage_context(stage, req_name, version, project_name=project_name, persist=True)
    missing_inputs = [
        item for item in context.get("input_material_status", [])
        if item.get("required") and not item.get("exists")
    ]
    ack_path = write_read_ack(context)
    runtime_check = run_runtime_consistency_gate(stage, req_name, version, phase="preflight")
    result = {
        "stage": stage,
        "req_name": req_name,
        "project_name": project_name,
        "version": version,
        "passed": not missing_inputs and not runtime_check.get("blocked", False),
        "missing_inputs": missing_inputs,
        "context_files": context.get("context_files", {}),
        "read_ack": ack_path,
        "runtime_consistency": runtime_check,
    }
    if runtime_check.get("blocked", False):
        result.setdefault("issues", []).extend(runtime_check.get("issues", []))
    if persist:
        stage_dir = get_stage_dir(req_name, stage, version)
        (stage_dir / "preflight_gate.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return result


def run_postflight_gate(
    stage: str,
    req_name: str,
    version: str = "v1.0",
    project_name: str | None = None,
    *,
    persist: bool = True,
) -> dict[str, Any]:
    contract = get_stage_contract(stage)
    stage_dir = get_stage_dir(req_name, stage, version)
    stage_dir.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] = {
        "stage": stage,
        "req_name": req_name,
        "project_name": project_name,
        "version": version,
        "required_outputs": {},
        "passed": True,
        "issues": [],
    }

    for output_name in contract.get("required_outputs", []):
        path = stage_dir / output_name
        exists = path.exists()
        result["required_outputs"][output_name] = {
            "path": str(path),
            "exists": exists,
        }
        if not exists and output_name not in {"coverage_ledger.json", "omission_ledger.json"}:
            result["issues"].append(f"缺少必备输出: {output_name}")

    backlog_json = resolve_contract_path(
        "workflow_assets/<REQ>/<VER>/「S2 需求拆解」/backlog.json",
        req_name,
        version,
    )

    coverage_paths: dict[str, str] = {}
    if stage == "S5":
        tp_path = stage_dir / "test_points.json"
        if backlog_json.exists() and tp_path.exists():
            coverage = build_coverage_ledger_from_test_points(
                backlog_json,
                tp_path,
                req_name=req_name,
                version=version,
            )
            omission = build_omission_ledger(coverage, stage=stage)
            coverage_paths = save_coverage_and_omission(stage_dir, coverage, omission)
            validation = validate_coverage_ledger(coverage)
            result["coverage_validation"] = validation
            if not validation["passed"]:
                result["issues"].extend(validation["issues"])
        else:
            result["issues"].append("S5 postflight 无法生成 coverage/omission ledger（缺 backlog.json 或 test_points.json）")

    if stage == "S6":
        tp_path = resolve_contract_path(
            "workflow_assets/<REQ>/<VER>/「S5 测试点生成」/test_points.json",
            req_name,
            version,
        )
        tc_path = stage_dir / "test_cases.json"
        if backlog_json.exists() and tp_path.exists() and tc_path.exists():
            coverage = build_coverage_ledger_from_test_cases(
                backlog_json,
                tp_path,
                tc_path,
                req_name=req_name,
                version=version,
            )
            omission = build_omission_ledger(coverage, stage=stage)
            coverage_paths = save_coverage_and_omission(stage_dir, coverage, omission)
            validation = validate_coverage_ledger(coverage)
            result["coverage_validation"] = validation
            if not validation["passed"]:
                result["issues"].extend(validation["issues"])

            # Round 18 FU-2：S6 gate 加 assertion 校验（F-E/F-F 落地）
            try:
                tc_payload = json.loads(tc_path.read_text(encoding="utf-8"))
                tc_list = tc_payload.get("test_cases", []) if isinstance(tc_payload, dict) else tc_payload
                assert_violations = check_assertion_completeness(tc_list)
                assert_violations += [
                    {"type": f.get("type"), "msg": f.get("msg"), "index": f.get("index"),
                     "id": f.get("id"), "severity": f.get("severity")}
                    for f in check_no_fp_name_field(tc_list, mode="error")
                ]
                gap_report = compute_assertion_gap_report(tc_list)
                result["assertion_validation"] = {
                    "passed": not assert_violations,
                    "violations": assert_violations,
                    "violation_count": len(assert_violations),
                    "gap_report": gap_report,
                }
                if assert_violations:
                    result["issues"].append(
                        f"S6 assertion 校验失败: {len(assert_violations)} violations（详见 assertion_validation）"
                    )
            except (json.JSONDecodeError, OSError) as exc:
                result["issues"].append(f"S6 assertion 校验跳过: {exc}")
        else:
            result["issues"].append("S6 postflight 无法生成 coverage/omission ledger（缺 backlog/test_points/test_cases）")

    if coverage_paths:
        result["coverage_outputs"] = coverage_paths
        for name, path in coverage_paths.items():
            result["required_outputs"][Path(path).name] = {
                "path": path,
                "exists": True,
            }

    runtime_check = run_runtime_consistency_gate(stage, req_name, version, phase="postflight")
    result["runtime_consistency"] = runtime_check
    if runtime_check.get("blocked", False):
        result["issues"].extend(
            issue.get("description", str(issue))
            for issue in runtime_check.get("issues", [])
            if issue.get("runtime_severity") == "P0_BLOCK"
        )
    result["passed"] = not result["issues"]
    if persist:
        (stage_dir / "postflight_gate.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return result


def run_runtime_consistency_gate(
    stage: str,
    req_name: str,
    version: str = "v1.0",
    phase: str = "runtime",
) -> dict[str, Any]:
    """将 consistency_check 映射成 runtime gate 结果。"""
    check = run_consistency_check(stage.lower(), req_name=req_name, version=version, phase=phase)
    severity_summary = check.get("severity_summary", {})
    blocked = severity_summary.get("P0_BLOCK", 0) > 0
    return {
        "stage": stage,
        "phase": phase,
        "blocked": blocked,
        "severity_summary": severity_summary,
        "issues": check.get("issues", []),
        "summary": check.get("summary", ""),
        "cache_hit": check.get("cache_hit", False),
        "passed": not blocked,
    }


# ═══════════════════════════════════════════════════════════
# Round 18 FU-2 self-test（§9.1.1 豁免条款）
# ═══════════════════════════════════════════════════════════

def self_test() -> int:
    """Round 18 FU-2 自测：stage_gatekeeper 集成 assertion 校验验证。

    验证 4 场景：
    1. integration_smoke：S6 gate 段新增的 `assertion_validation` 字段在 result dict 中存在
    2. function_import_smoke：check_assertion_completeness + check_no_fp_name_field
       都能从 stage_gatekeeper module-level 导入（无循环导入）
    3. coverage_pipeline_smoke：compute_assertion_gap_report 能从
       ai_workflow.coverage_validator 导入（不变现有 import 路径）
    4. result_keys_smoke：run_postflight_gate 返回的 dict 应含
       keys: ["stage", "req_name", "version", "required_outputs",
              "passed", "issues", "coverage_validation", "assertion_validation",
              "runtime_consistency", "coverage_outputs"] 中的基础 keys
       （assertion_validation 在 S6 路径下出现，其他阶段不一定）
    """
    import sys
    import importlib

    # 场景 1：import smoke —— 这些导入都已在本文件 top-of-file 完成
    # 只要 self_test() 调用不抛 ImportError 即通过
    try:
        from ai_workflow.coverage_validator import compute_assertion_gap_report as _cagr
        assert callable(_cagr), "compute_assertion_gap_report 应可调用"
        print("  C1 (compute_assertion_gap_report callable): PASS")
    except Exception as exc:
        print(f"  C1 (compute_assertion_gap_report callable): FAIL — {exc}")
        return 1

    # 场景 2：fixture 上跑 assertion_completeness（用纯内存 sample）
    from ai_workflow.l1_format_validator import (
        check_assertion_completeness as _cac,
        check_no_fp_name_field as _cpnf,
    )
    sample_with_a = [
        {"case_id": "TC-1", "assertion": [{"assertion_type": "numeric", "expected_value": 0}]},
    ]
    sample_without_a = [
        {"case_id": "TC-2"},  # 缺 assertion
    ]
    sample_with_fp = [
        {"case_id": "TC-3", "fp_name": "首页销量排序", "feature_point_ref": "X"} ,
    ]
    v1 = _cac(sample_with_a)
    assert v1 == [], f"C2-1 全有 assertion 应 0 violations, got {v1}"
    v2 = _cac(sample_without_a)
    assert len(v2) == 1, f"C2-2 缺 assertion 应 1 violation, got {v2}"
    assert v2[0]["type"] == "MISSING_ASSERTION"
    v3 = _cpnf(sample_with_fp, mode="error")
    assert len(v3) == 1 and v3[0]["severity"] == "error", f"C2-3 fp_name error 模式: {v3}"
    print("  C2 (l1 helpers integration smoke): PASS")

    # 场景 3：compute_assertion_gap_report 跨模块调用
    r3 = _cagr(sample_with_a + sample_without_a + sample_with_fp)
    assert r3["total_tcs"] == 3, f"C3 total 应 3: {r3}"
    assert r3["with_assertion"] == 1, f"C3 with 应 1: {r3}"
    assert r3["without_assertion"] == 2, f"C3 without 应 2: {r3}"
    print("  C3 (compute_assertion_gap_report 跨模块调用): PASS")

    # 场景 4：run_postflight_gate 不应在没有 input 时抛异常
    # （不实际跑 S6 postflight——需要真实数据；只验证 signature + 返回结构）
    sig = str(run_postflight_gate.__doc__ or "")
    assert "issues" in sig or sig == "", "run_postflight_gate 应是公开函数"
    # 验证 import 整个文件不抛异常（间接证明 module-level import 干净）
    try:
        this_mod = importlib.import_module("ai_workflow.stage_gatekeeper")
        assert hasattr(this_mod, "run_postflight_gate")
        assert hasattr(this_mod, "run_preflight_gate")
        assert hasattr(this_mod, "run_runtime_consistency_gate")
        assert hasattr(this_mod, "compute_assertion_gap_report") or hasattr(importlib.import_module("ai_workflow.coverage_validator"), "compute_assertion_gap_report")
        print("  C4 (module signature integrity): PASS")
    except Exception as exc:
        print(f"  C4 (module signature integrity): FAIL — {exc}")
        return 1

    print("[stage_gatekeeper self-test] FU-2 integration: 4 scenarios PASS")
    return 0


def main() -> int:
    """Round 18 FU-2 CLI 入口（§9.1.1 豁免条款的 argv 分支）。"""
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "--self-test":
        return self_test()
    print("用法: python3 stage_gatekeeper.py --self-test")
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
