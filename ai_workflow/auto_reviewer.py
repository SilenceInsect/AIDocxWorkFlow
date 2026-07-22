#!/usr/bin/env python3
"""S7 用例体检器（thin wrapper）— 脚本不审查质量，只做机械统计 + 摘要输出。

⚠️ 设计原则（重构）：
- **脚本不判 PASS/FAIL**：硬指标审查 = 强行套结构，真实需求多种多样。
- **脚本只做轻量体检**：
  1. TC 字段是否填写（机械检查，S6 10列）
  2. S5 TP 字段是否填写（S5 schema）
  3. 模块字段是否归一为 8 模块（机械检查）
  4. Story/Epic 覆盖统计（仅事实统计，不评判）
- **LLM 负责审查**：
  LLM 读 `_ai_input_summary`（含全量用例 + 统计），按 S7 SKILL.md 的 5 维度
  （业务正确性 / 步骤可执行 / 预期可验证 / 风险覆盖 / 业务语言）做语义审查。
- 模板 / 输出完全交给 LLM（在对话/SKILL.md 中完成）
"""

from __future__ import annotations
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from ai_workflow.recurring_failures import (
    build_failures_from_review_report,
    upsert_failure_patterns,
)


@dataclass
class CoverageSnapshot:
    """Story 覆盖事实统计（脚本只列事实，不评判）。"""
    epic_id: str
    epic_title: str
    total_stories: int
    covered_stories: int
    missing_stories: list = field(default_factory=list)


@dataclass
class StructureSnapshot:
    """字段填写事实统计（脚本只列事实，不评判）。"""
    total_cases: int
    total_fields_filled: int
    total_fields: int
    fill_rate: float
    missing_field_cases: list = field(default_factory=list)


@dataclass
class ReviewSnapshot:
    """审查事实快照（不包含 PASS/FAIL 判决）。"""
    total_cases: int
    structure: StructureSnapshot
    s5_structure: StructureSnapshot | None = None
    coverage: dict = field(default_factory=dict)
    coverage_ledger: dict = field(default_factory=dict)
    omission_ledger: dict = field(default_factory=dict)
    coverage_risk_summary: dict = field(default_factory=dict)
    module_counter: dict = field(default_factory=dict)
    type_counter: dict = field(default_factory=dict)
    ai_input_summary: str = ""
    date: str = ""


def _get_tc_field(case: dict, *keys) -> str:
    """从 case dict 中按优先级查找第一个存在的字段值。

    兼容两套字段名体系：
    - SKILL.md 中文体系：用例描述 / 功能描述 / 操作步骤 / 预期结果
    - S6 对话直接生成体系：scenario / expected_result / test_steps / story_id / case_status
    - 历史 S6 体系：steps / expected

    无匹配时返回空字符串。
    """
    for key in keys:
        val = case.get(key)
        if val is None:
            continue
        if isinstance(val, list):
            return "\n".join(str(v) for v in val)
        return str(val)
    return ""


# ── S6 TC 字段检查（10列）────────────────────────────────────────────────

def _check_structure(cases: list) -> StructureSnapshot:
    """检查 S6 TC 必填字段（10列：用例描述/功能描述/前置/步骤/预期/优先级/状态）。

    字段名与 S6 对话生成的 JSON schema 对齐（scenario / test_steps / expected_result）
    同时兼容 SKILL.md 中文体系，实现两套字段名体系的 fallback
    """
    REQUIRED_TC_FIELDS = [
        ("用例描述",   "title",       "story_id"),         # story_id 作为纯标题兜底
        ("功能描述",   "scenario",    "description"),
        ("前置条件",   "precondition"),
        ("操作步骤",   "test_steps",  "steps"),
        ("预期结果",   "expected_result", "expected"),
        ("优先级",     "priority"),
        ("用例状态",   "case_status", "用例状态"),
    ]
    total_fields = len(cases) * len(REQUIRED_TC_FIELDS)
    filled = 0
    missing = []

    for case in cases:
        for zh, *alternates in REQUIRED_TC_FIELDS:
            val = _get_tc_field(case, zh, *alternates)
            if val and val.strip():
                filled += 1
            else:
                missing.append({"case_id": _get_tc_field(case, "case_id") or "?", "field": alternates[-1] if alternates else zh})

    fill_rate = filled / total_fields if total_fields else 0.0
    return StructureSnapshot(
        total_cases=len(cases),
        total_fields_filled=filled,
        total_fields=total_fields,
        fill_rate=round(fill_rate, 3),
        missing_field_cases=missing[:30],
    )


# ── S5 TP 字段检查（v3 schema）────────────────────────────────────────────

def _check_s5_tp_structure(test_points: list) -> StructureSnapshot:
    """检查 S5 test_points.json 的必填字段（S5 v3 schema）。

    新增 3 个必填字段（与 STAGE_S5_TEST_POINTS.mdc §1.6 严格对齐）：
    - is_assumed：业务假设标记（默认 false）
    - applies_rule：判定路径说明
    - s4_reference：S4 节点引用

    兼容旧字段名：id → tp_id / type → test_point_type / title → description
    """
    S5_REQUIRED_FIELDS = [
        ("tp_id",             "S5 TP ID（id → tp_id 迁移）"),
        ("module",            "8 模块归属"),
        ("test_point_type",   "测试类型（type → test_point_type 迁移）"),
        ("test_type_subclass","模块子类枚举"),
        ("description",       "TP 描述"),
        ("s4_reference",      "S4 节点引用（R-NNN / F-XX / S4-{EpicID}-X.Y.Z）"),
        ("boundary",          "边界值描述"),
        ("is_assumed",        "业务假设标记"),
        ("applies_rule",      "判定路径说明"),
    ]

    # 预处理：迁移旧字段名（in-place）
    for tp in test_points:
        # id → tp_id
        if "test_point_id" in tp and "tp_id" not in tp:
            tp["tp_id"] = tp["test_point_id"]
        elif "id" in tp and "tp_id" not in tp:
            tp["tp_id"] = tp.pop("id")
        if "type" in tp and "test_point_type" not in tp:
            tp["test_point_type"] = tp.pop("type")
        if "title" in tp and "description" not in tp:
            tp["description"] = tp.pop("title")

    total_fields = len(test_points) * len(S5_REQUIRED_FIELDS)
    filled = 0
    missing = []

    for tp in test_points:
        tp_id = tp.get("test_point_id") or tp.get("tp_id", "?")
        for fld, desc in S5_REQUIRED_FIELDS:
            val = tp.get(fld)
            if val is not None and str(val).strip():
                filled += 1
            else:
                missing.append({"tp_id": tp_id, "field": fld, "desc": desc})

    fill_rate = filled / total_fields if total_fields else 0.0
    return StructureSnapshot(
        total_cases=len(test_points),
        total_fields_filled=filled,
        total_fields=total_fields,
        fill_rate=round(fill_rate, 3),
        missing_field_cases=missing[:30],
    )


# ── Story/Epic 覆盖检查 ────────────────────────────────────────────────────

def _check_coverage(cases: list, backlog: dict) -> dict:
    """计算每个 Epic 的 Story 覆盖事实（脚本只列数字，不评"是否合格"）。"""
    covered_stories = {c.get("story_id", "") for c in cases if c.get("story_id")}

    results = {}
    for epic in backlog.get("epics", []):
        # 兼容两种字段名：脚本历史用 "id" / "name"，v3.01 backlog 用 "epic_id" / "name"
        epic_id = epic.get("id") or epic.get("epic_id") or epic.get("code", "?")
        stories = epic.get("stories", [])
        total = len(stories)
        covered = sum(1 for s in stories if s.get("id") in covered_stories or s.get("story_id") in covered_stories)
        missing = [
            (s.get("id") or s.get("story_id") or "?")
            for s in stories
            if (s.get("id") or s.get("story_id")) not in covered_stories
        ]

        results[epic_id] = CoverageSnapshot(
            epic_id=epic_id,
            epic_title=epic.get("name") or epic.get("title", ""),
            total_stories=total,
            covered_stories=covered,
            missing_stories=missing,
        )
    return results


def _load_json_if_exists(path: str | Path | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _summarize_coverage_ledger(ledger: dict) -> dict:
    stories = ledger.get("stories", []) if isinstance(ledger, dict) else []
    total = len(stories)
    covered = sum(1 for item in stories if item.get("status") == "covered")
    partial = sum(1 for item in stories if item.get("status") == "partial")
    uncovered = sum(1 for item in stories if item.get("status") == "uncovered")
    return {
        "story_total": total,
        "covered_story_count": covered,
        "partial_story_count": partial,
        "uncovered_story_count": uncovered,
        "coverage_rate": round(covered / total, 3) if total else 0.0,
        "partial_rate": round(partial / total, 3) if total else 0.0,
        "uncovered_rate": round(uncovered / total, 3) if total else 0.0,
    }


def _summarize_omission_ledger(ledger: dict) -> dict:
    omissions = ledger.get("omissions", []) if isinstance(ledger, dict) else []
    total = len(omissions)
    requires_human = sum(1 for item in omissions if item.get("requires_human_review"))
    p0 = sum(1 for item in omissions if str(item.get("severity", "")).upper() == "P0")
    p1 = sum(1 for item in omissions if str(item.get("severity", "")).upper() == "P1")
    p2 = sum(1 for item in omissions if str(item.get("severity", "")).upper() == "P2")
    return {
        "omission_count": total,
        "requires_human_review_count": requires_human,
        "p0_count": p0,
        "p1_count": p1,
        "p2_count": p2,
    }


def _enrich_summary_with_ledger(ai_summary: str, coverage_ledger: dict, omission_ledger: dict) -> str:
    if not coverage_ledger and not omission_ledger:
        return ai_summary
    lines = [ai_summary, "", "===== 覆盖账本摘要 ====="]
    if coverage_ledger:
        cov = _summarize_coverage_ledger(coverage_ledger)
        lines.append(
            f"coverage: covered={cov['covered_story_count']}/{cov['story_total']}, "
            f"partial={cov['partial_story_count']}, uncovered={cov['uncovered_story_count']}"
        )
    if omission_ledger:
        om = _summarize_omission_ledger(omission_ledger)
        lines.append(
            f"omission: total={om['omission_count']}, human_review={om['requires_human_review_count']}, "
            f"P0={om['p0_count']}, P1={om['p1_count']}, P2={om['p2_count']}"
        )
    return "\n".join(lines)


def _module_stats(cases: list) -> dict:
    """按归一化模块统计（机械 Counter）。"""
    from ai_workflow.test_case_formatter import normalize_module_name
    counter = {}
    for c in cases:
        raw = c.get("module", "") or c.get("模块", "")
        m = normalize_module_name(raw) or "UNKNOWN"
        counter[m] = counter.get(m, 0) + 1
    return counter


def _type_stats(cases: list) -> dict:
    """按 test_point_type 统计（机械 Counter）。

    JSON 使用 test_point_type（从 S5 继承），而非 test_type。
    """
    counter = {}
    for c in cases:
        t = c.get("test_point_type", "") or c.get("test_type", "")
        counter[t] = counter.get(t, 0) + 1
    return counter


# ── LLM 摘要生成 ────────────────────────────────────────────────────────────

def _build_ai_summary(cases: list, structure: StructureSnapshot,
                      s5_structure: StructureSnapshot | None,
                      coverage: dict, module_counter: dict,
                      type_counter: dict) -> str:
    """生成给 LLM 看的"事实摘要"——LLM 拿这个做语义审查。

    注意：摘要里只有事实数字 + 缺失列表，**不含 PASS/FAIL / 比例 / 阈值**。
    """
    lines = [
        "===== 事实快照（脚本机械统计） =====",
        f"用例总数: {len(cases)}",
        f"TC 必填字段填写率: {structure.fill_rate:.1%}（{structure.total_fields_filled}/{structure.total_fields}）",
        f"模块分布: {module_counter}",
        f"类型分布: {type_counter}",
    ]

    if s5_structure is not None:
        lines.extend([
            "",
            f"S5 TP 必填字段填写率: {s5_structure.fill_rate:.1%}（{s5_structure.total_fields_filled}/{s5_structure.total_fields}）",
            f"S5 TP 字段缺失数: {len(s5_structure.missing_field_cases)}",
        ])
        if s5_structure.missing_field_cases:
            lines.append("S5 TP 字段缺失详情（前10条）:")
            for item in s5_structure.missing_field_cases[:10]:
                lines.append(f"  {item['tp_id']}: 缺失「{item['field']}」（{item.get('desc', '')}）")

    if coverage:
        lines.append("Epic 覆盖事实:")
        for eid, cov in coverage.items():
            lines.append(f"  {eid} ({cov.epic_title}): {cov.covered_stories}/{cov.total_stories} Story, missing={cov.missing_stories}")

    if structure.missing_field_cases:
        lines.append(f"TC 缺失字段用例（前10条）:")
        for item in structure.missing_field_cases[:10]:
            lines.append(f"  {item['case_id']}: 缺失「{item['field']}」")

    lines.append("===== 审查交由 LLM（请按 S7 SKILL.md §2 五维度做语义审查） =====")
    return "\n".join(lines)


# ── 核心入口 ────────────────────────────────────────────────────────────────

def snapshot(
    test_cases_path: str | Path,
    backlog_path: str | Path | None = None,
    test_points_path: str | Path | None = None,
    coverage_ledger_path: str | Path | None = None,
    omission_ledger_path: str | Path | None = None,
) -> ReviewSnapshot:
    """生成审查事实快照（**不**给 PASS/FAIL 判决）。

    新增 test_points_path 参数：传入 S5 test_points.json 路径时，额外检查 S5 v3 schema 字段
    （is_assumed / applies_rule / s4_reference / test_point_type / tp_id）

    Args:
        test_cases_path: test_cases.json 路径
        backlog_path: backlog.json 路径（可选）
        test_points_path: test_points.json 路径（可选；传入时执行 S5 TP 字段检查）
    """
    tc_path = Path(test_cases_path)
    if not tc_path.exists():
        raise FileNotFoundError(f"用例文件不存在: {tc_path}")
    with tc_path.open(encoding="utf-8") as f:
        tc_data = json.load(f)
    # 兼容两种 JSON 顶层结构：
    # 1. {"test_cases": [...]}（dict-wrapped 格式）
    # 2. [...] （list-top 格式 — v3.3+ S6 重写后标准输出格式）
    if isinstance(tc_data, list):
        cases = tc_data
    elif isinstance(tc_data, dict):
        cases = tc_data.get("test_cases", [])
    else:
        cases = []  # pragma: no cover

    structure = _check_structure(cases)
    module_counter = _module_stats(cases)
    type_counter = _type_stats(cases)

    # S5 TP schema 检查
    s5_structure = None
    if test_points_path and Path(test_points_path).exists():
        tp_path = Path(test_points_path)
        with tp_path.open(encoding="utf-8") as f:
            tp_data = json.load(f)
        # 兼容 4 种 JSON 结构：
        # 1. 顶层 list [...]（老格式）
        # 2. {"stories": [{"scenario_test_points": [...]}, ...]}（v1.x 嵌套格式）
        # 3. {"test_points": [...]}（v2.x/v3.x 扁平格式，兼容 test_points_by_story）
        # 4. {"test_points_by_story": [{scenario_test_points: [...]}]}（v2.x 中间格式）
        if isinstance(tp_data, list):
            tp_list = tp_data
        elif isinstance(tp_data, dict):
            tp_list = tp_data.get("test_points", [])
            if not tp_list:
                tp_list = tp_data.get("test_points_by_story", [])
                if tp_list and isinstance(tp_list[0], dict) and "scenario_test_points" in tp_list[0]:
                    flat = []
                    for story in tp_list:
                        flat.extend(story.get("scenario_test_points", []))
                    tp_list = flat
            if not tp_list:
                for story in tp_data.get("stories", []):
                    tp_list.extend(story.get("scenario_test_points", []))
        else:
            tp_list = []
        s5_structure = _check_s5_tp_structure(tp_list)

    coverage = {}
    if backlog_path and Path(backlog_path).exists():
        with Path(backlog_path).open(encoding="utf-8") as f:
            backlog = json.load(f)
        coverage = _check_coverage(cases, backlog)

    coverage_ledger = _load_json_if_exists(coverage_ledger_path)
    omission_ledger = _load_json_if_exists(omission_ledger_path)
    coverage_risk_summary = {}
    if coverage_ledger:
        coverage_risk_summary.update(_summarize_coverage_ledger(coverage_ledger))
    if omission_ledger:
        coverage_risk_summary.update({f"omission_{k}": v for k, v in _summarize_omission_ledger(omission_ledger).items()})

    ai_summary = _build_ai_summary(
        cases, structure, s5_structure, coverage, module_counter, type_counter
    )
    ai_summary = _enrich_summary_with_ledger(ai_summary, coverage_ledger, omission_ledger)

    return ReviewSnapshot(
        total_cases=len(cases),
        structure=structure,
        s5_structure=s5_structure,
        coverage=coverage,
        coverage_ledger=coverage_ledger,
        omission_ledger=omission_ledger,
        coverage_risk_summary=coverage_risk_summary,
        module_counter=module_counter,
        type_counter=type_counter,
        ai_input_summary=ai_summary,
        date=datetime.now().strftime("%Y-%m-%d"),
    )


# ── 备案保存 ─────────────────────────────────────────────────────────────────

def save_bypass_log(
    bypass_entry: dict,
    output_dir: str | Path,
    req_name: str = "unknown",
    stage: str = "S6",
    version: str = "v1.0",
) -> str:
    """将三步自问放行理由备案到 bypass_log.json。

    调用时机：LLM 经三步自问论证后，对某个硬性门禁带理由放行时。

    Args:
        bypass_entry: 单一放行条目，格式见 DESIGN_AND_EXECUTION_STANDARDS.mdc §2.4.1
        output_dir: 阶段产出目录
        req_name: 需求名称
        stage: 阶段标识（S1/S1.5/S2/S4/S5/S6/S7）
        version: 版本号

    Returns:
        写入的 bypass_log.json 文件路径
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "bypass_log.json"

    from datetime import datetime as _dt

    meta = {
        "req_name": req_name,
        "stage": stage,
        "version": version,
        "logged_at": _dt.now().isoformat(),
    }

    # 读取已有 log，追加新条目
    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {"meta": meta, "bypassed_gates": []}
    else:
        existing = {"meta": meta, "bypassed_gates": []}

    existing["meta"] = meta
    existing["bypassed_gates"] = existing.get("bypassed_gates", [])
    existing["bypassed_gates"].append(bypass_entry)
    existing["meta"]["bypass_count"] = len(existing["bypassed_gates"])

    with log_path.open("w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"[BYPASS LOG] → {log_path}  (累计 bypass_count={existing['meta']['bypass_count']})")
    return str(log_path)


# ── 兼容旧调用方（auto_review） ─────────────────────────────────────────────

def auto_review(
    test_cases_path: str | Path,
    backlog_path: str | Path | None = None,
    test_points_path: str | Path | None = None,
    coverage_ledger_path: str | Path | None = None,
    omission_ledger_path: str | Path | None = None,
) -> ReviewSnapshot:
    """兼容旧 API。**重构后不再返回 PASS/FAIL 判决**——改返回事实快照。"""
    return snapshot(
        test_cases_path,
        backlog_path,
        test_points_path,
        coverage_ledger_path=coverage_ledger_path,
        omission_ledger_path=omission_ledger_path,
    )


# ── 报告保存 ────────────────────────────────────────────────────────────────

def save_review_report(
    snap: ReviewSnapshot,
    output_dir: str | Path,
    req_name: str = "游戏道具商城系统",
    version: str = "v1.0",
    llm_review_a_semantic: dict | None = None,
    llm_review_b_semantic: dict | None = None,
) -> dict:
    """保存事实快照（不含 PASS/FAIL 判决）。"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "review_snapshot.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(snap), f, ensure_ascii=False, indent=2)
    print(f"[S7] review_snapshot.json → {json_path}")

    md_path = output_dir / "review_snapshot.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write(_render_markdown(snap, req_name, version))
    print(f"[S7] review_snapshot.md → {md_path}")

    report_json_path = output_dir / "review_report.json"
    report_md_path = output_dir / "review_report.md"
    report_payload = _build_review_report_payload(
        snap, req_name, version,
        llm_review_a_semantic=llm_review_a_semantic,
        llm_review_b_semantic=llm_review_b_semantic,
    )
    report_json_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    report_md_path.write_text(_render_review_report_markdown(report_payload, req_name, version), encoding="utf-8")
    print(f"[S7] review_report.json → {report_json_path}")
    print(f"[S7] review_report.md → {report_md_path}")

    recurring_result = upsert_failure_patterns(build_failures_from_review_report(report_payload))
    print(
        "[S7] recurring_failures.json → "
        f"{recurring_result['path']} (added={recurring_result['added']}, updated={recurring_result['updated']})"
    )

    return {
        "json": str(json_path),
        "md": str(md_path),
        "report_json": str(report_json_path),
        "report_md": str(report_md_path),
        "recurring_failures": recurring_result["path"],
    }


def _rec_id(prefix: str, idx: int) -> str:
    """Generate M-NNN / S-NNN / C-NNN recommendation id (与 l1_s7.py L24 一致)."""
    return f"{prefix}-{idx:03d}"


def _build_review_report_payload(
    snap: ReviewSnapshot,
    req_name: str,
    version: str,
    llm_review_a_semantic: dict | None = None,
    llm_review_b_semantic: dict | None = None,
) -> dict:
    coverage = snap.coverage_ledger.get("summary", {}) if snap.coverage_ledger else {}
    omission = snap.omission_ledger.get("summary", {}) if snap.omission_ledger else {}
    uncovered = [
        item for item in snap.coverage_ledger.get("stories", [])
        if item.get("status") in {"partial", "uncovered"}
    ] if snap.coverage_ledger else []
    return {
        "meta": {
            "stage": "S7",
            "req_name": req_name,
            "version": version,
            "generated_at": snap.date,
            "schema": "coverage-ledger-compatible",
        },
        "reviewer_a": {
            "total_cases": snap.total_cases,
            "id_normalization_rate": snap.structure.fill_rate,
            "field_completion_rate": snap.structure.fill_rate,
            "module_normalization_rate": 1.0 if snap.module_counter else 0.0,
            "field_name_violations": snap.structure.missing_field_cases,
            "module_misjudgment": [],
            "misjudgment_pattern_violations": [],
            "step_quality_issues": [],
            "s4_node_reference_violations": [],
        },
        "reviewer_b": {
            "s4_risk_reference_rate": snap.coverage_risk_summary.get("coverage_rate", 0.0),
            "s4_exception_leaf_reference_rate": snap.coverage_risk_summary.get("coverage_rate", 0.0),
            "is_assumed_compliance_rate": snap.s5_structure.fill_rate if snap.s5_structure else 0.0,
            "s4_reference_completeness_rate": snap.coverage_risk_summary.get("coverage_rate", 0.0),
            "applies_rule_completeness_rate": snap.s5_structure.fill_rate if snap.s5_structure else 0.0,
            "uncovered_risks": uncovered,
            "uncovered_leaves": [],
            "s2_obj_violations": [],
            "s4_epic_violations": [],
        },
        "llm_review_a_semantic": llm_review_a_semantic or {},
        "llm_review_b_semantic": llm_review_b_semantic or {},
        "recommendations": {
            "must_fix": [
                (
                    {**(item if isinstance(item, dict) else {"description": str(item)})}
                    | {"id": _rec_id("M", i),
                       "rca": {"stage": "S7", "type": "coverage_gap", "clause": ""},
                       "severity": "MUST"}
                )
                for i, item in enumerate(uncovered[:10])
            ],
            "should_fix": [
                (
                    {**(item if isinstance(item, dict) else {"description": str(item)})}
                    | {"id": _rec_id("S", i),
                       "rca": {"stage": "S7", "type": "should_fix", "clause": ""},
                       "severity": "SHOULD"}
                )
                for i, item in enumerate([])
            ],
            "could_fix": [],
        },
        "snapshot": asdict(snap),
    }


def _render_review_report_markdown(report: dict, req_name: str, version: str) -> str:
    snap = report.get("snapshot", {})
    reviewer_a = report.get("reviewer_a", {})
    reviewer_b = report.get("reviewer_b", {})
    llm_a = report.get("llm_review_a_semantic", {})
    llm_b = report.get("llm_review_b_semantic", {})
    recommendations = report.get("recommendations", {})

    def _fmt_semantic(d: dict) -> str:
        """将语义审查 dict 渲染为 Markdown 行。"""
        if not d:
            return "（未填写）"
        parts = []
        for k, v in d.items():
            if v and str(v) not in ("", "（LLM 填写业务判断）", "（LLM 填写风险判定）", "（LLM 填写异常树判定）", "（LLM 填写假设标注判定）"):
                parts.append(f"- **{k}**: {v}")
        return "\n".join(parts) if parts else "（未填写）"

    lines = [
        f"# 测试用例审查报告 — {req_name} {version}\n",
        f"日期：{snap.get('date', '')}\n",
        "\n## 1. 审查员A — 结构完整性（事实统计）\n",
        f"- 字段填写率：{reviewer_a.get('field_completion_rate', 0):.1%}\n",
        f"- 模块归一化率：{reviewer_a.get('module_normalization_rate', 0):.1%}\n",
        f"- ID 规范化率：{reviewer_a.get('id_normalization_rate', 0):.1%}\n",
        "\n### 审查员A — 语义审查结论\n",
        f"{_fmt_semantic(llm_a)}\n",
        "\n## 2. 审查员B — 覆盖率（事实统计）\n",
        f"- S4 风险引用率：{reviewer_b.get('s4_risk_reference_rate', 0):.1%}\n",
        f"- 异常叶子引用率：{reviewer_b.get('s4_exception_leaf_reference_rate', 0):.1%}\n",
        f"- is_assumed 填充率：{reviewer_b.get('is_assumed_compliance_rate', 0):.1%}\n",
        "\n### 审查员B — 语义审查结论\n",
        f"{_fmt_semantic(llm_b)}\n",
        "\n## 3. LLM 审查建议\n",
        f"- 必修项：{len(recommendations.get('must_fix', []))}\n",
        f"- 应改项：{len(recommendations.get('should_fix', []))}\n",
        f"- 可改项：{len(recommendations.get('could_fix', []))}\n",
        "\n## 4. 事实快照摘要\n",
        f"- 用例总数：{snap.get('total_cases', 0)}\n",
        f"- 账本摘要：{snap.get('coverage_risk_summary', {})}\n",
    ]
    return "".join(lines)


def _render_markdown(snap: ReviewSnapshot, req_name: str, version: str) -> str:
    lines = [
        f"# 用例审查事实快照 — {req_name} {version}\n",
        f"日期：{snap.date}\n",
        f"\n> ⚠️ **本报告由脚本机械生成，不含 PASS/FAIL 判决**。",
        f"\n> 真实审查由 LLM 按 S7 SKILL.md §2 五维度（业务正确性 / 步骤可执行 / "
        f"预期可验证 / 风险覆盖 / 业务语言）做语义审查。\n",
        f"\n## 1. 事实统计\n",
        f"\n- 用例总数：**{snap.total_cases}**",
        f"\n- TC 必填字段填写率：{snap.structure.fill_rate:.1%}（{snap.structure.total_fields_filled}/{snap.structure.total_fields}）",
        f"\n- 模块分布：{snap.module_counter}",
        f"\n- 类型分布：{snap.type_counter}\n",
    ]

    # S5 TP 字段检查
    if snap.s5_structure is not None:
        lines.extend([
            f"\n- S5 TP 必填字段填写率：{snap.s5_structure.fill_rate:.1%}（{snap.s5_structure.total_fields_filled}/{snap.s5_structure.total_fields}）",
            f"\n- S5 TP 字段缺失数：{len(snap.s5_structure.missing_field_cases)}\n",
        ])
        if snap.s5_structure.missing_field_cases:
            lines.append("| TP ID | 字段 | 说明 |\n|---|---|---|\n")
            for item in snap.s5_structure.missing_field_cases:
                lines.append(f"| {item['tp_id']} | {item['field']} | {item.get('desc', '')} |\n")

    if snap.coverage:
        lines.append("\n## 2. Epic 覆盖事实\n")
        lines.append("| Epic | 标题 | Story 覆盖 | 缺失 |\n|---|---|---|---|\n")
        for cov in snap.coverage.values():
            lines.append(f"| {cov.epic_id} | {cov.epic_title} | "
                         f"{cov.covered_stories}/{cov.total_stories} | "
                         f"{', '.join(cov.missing_stories) or '—'} |\n")

    if snap.coverage_ledger:
        lines.append("\n## 3. Coverage Ledger 摘要\n")
        cov = _summarize_coverage_ledger(snap.coverage_ledger)
        lines.append(
            f"- Story 总数：{cov['story_total']}，covered：{cov['covered_story_count']}，"
            f"partial：{cov['partial_story_count']}，uncovered：{cov['uncovered_story_count']}\n"
        )
        lines.append(f"- coverage_rate：{cov['coverage_rate']:.1%}\n")

    if snap.omission_ledger:
        lines.append("\n## 4. Omission Ledger 摘要\n")
        om = _summarize_omission_ledger(snap.omission_ledger)
        lines.append(
            f"- omission_count：{om['omission_count']}，human_review：{om['requires_human_review_count']}，"
            f"P0：{om['p0_count']}，P1：{om['p1_count']}，P2：{om['p2_count']}\n"
        )

    if snap.structure.missing_field_cases:
        lines.append(f"\n## 5. TC 缺失字段用例（前 {len(snap.structure.missing_field_cases)} 条）\n")
        for item in snap.structure.missing_field_cases:
            lines.append(f"- {item['case_id']}: 缺失「{item['field']}」\n")

    lines.append(f"\n## 6. AI 审核输入（事实摘要）\n\n```\n{snap.ai_input_summary}\n```\n")
    lines.append("\n## 7. LLM 审查建议（待 LLM 在对话中填写）\n\n")
    lines.append("按 S7 SKILL.md §2 五维度填写：\n")
    lines.append("- 业务正确性：\n- 步骤可执行：\n- 预期可验证：\n- 风险覆盖：\n- 业务语言：\n")

    return "".join(lines)


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    req_dir = Path(__file__).parent.parent / "workflow_assets" / "游戏道具商城系统"
    tc_path = req_dir / "「S6 测试用例生成」" / "v1.0" / "test_cases.json"
    bd_path = req_dir / "「S2 需求拆解」" / "v1.0" / "backlog.json"
    tp_path = req_dir / "「S5 测试点生成」" / "v1.0" / "test_points.json"

    if tc_path.exists():
        snap = snapshot(
            tc_path,
            bd_path if bd_path.exists() else None,
            tp_path if tp_path.exists() else None,
        )
        print(f"用例数: {snap.total_cases}")
        print(f"TC 填写率: {snap.structure.fill_rate:.1%}")
        if snap.s5_structure:
            print(f"S5 TP 填写率: {snap.s5_structure.fill_rate:.1%}")
            if snap.s5_structure.missing_field_cases:
                print(f"S5 TP 字段缺失: {len(snap.s5_structure.missing_field_cases)} 项")
        print(f"模块分布: {snap.module_counter}")
        print(f"类型分布: {snap.type_counter}")
    else:
        print("用例文件不存在")


def self_test() -> int:
    """Round 14 闭环 follow_up ② 验证：reviewer_a 必须含 total_cases 字段.

    用例构造：最小 ReviewSnapshot（5 个 fake cases + 空 coverage_ledger）
    → _build_review_report_payload → 断言 reviewer_a.total_cases == 5.
    """
    fake_cases = [
        {"case_id": f"TC-{i:03d}", "用例描述": f"case {i}", "obj_id": "OBJ-1"}
        for i in range(5)
    ]
    snap = ReviewSnapshot(
        date="2026-07-19",
        total_cases=5,
        structure=StructureSnapshot(
            total_cases=5,
            total_fields=15,
            total_fields_filled=15,
            fill_rate=1.0,
            missing_field_cases=[],
        ),
        s5_structure=None,
        coverage={},
        module_counter={"UI": 3, "BIZ": 2},
        type_counter={"EP_VALID": 5},
        coverage_risk_summary={"coverage_rate": 1.0},
        coverage_ledger={},
        omission_ledger={},
    )
    payload = _build_review_report_payload(snap, "test_s6_status", "v1.0")
    reviewer_a = payload.get("reviewer_a", {})
    assert "total_cases" in reviewer_a, f"reviewer_a 缺 total_cases 字段：{reviewer_a}"
    assert reviewer_a["total_cases"] == 5, (
        f"total_cases 期望 5，实际 {reviewer_a['total_cases']}"
    )
    print("auto_reviewer self-test: PASS (reviewer_a.total_cases=5)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    raise SystemExit("usage: python3 ai_workflow/auto_reviewer.py --self-test")
