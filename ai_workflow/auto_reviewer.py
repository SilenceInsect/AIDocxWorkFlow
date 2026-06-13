#!/usr/bin/env python3
"""S7 — 用例自动审查引擎（规则引擎，非 AI）。

输入：test_cases.json + backlog.json + 终版需求.md
输出：覆盖率 + 结构完整性 + 通过判定
"""

from __future__ import annotations
import json, re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class CoverageResult:
    epic_id: str
    epic_title: str
    total_stories: int
    covered_stories: int
    coverage: float   # 0.0 - 1.0
    missing_stories: list = field(default_factory=list)


@dataclass
class StructureResult:
    total_fields_filled: int = 0
    total_fields: int = 0
    pass_rate: float = 0.0
    missing_field_cases: list = field(default_factory=list)


@dataclass
class ReviewResult:
    overall_pass: bool
    coverage: dict       # {epic_id: CoverageResult}
    structure: StructureResult
    total_cases: int
    module_stats: dict
    ai_input_summary: str   # AI 审核用的 ~500字符摘要
    date: str


def auto_review(
    test_cases_path: str | Path,
    backlog_path: str | Path | None = None,
    req_text: str = "",
) -> ReviewResult:
    """
    自动审查测试用例的结构完整性和覆盖率。

    参数:
        test_cases_path: test_cases.json 路径
        backlog_path: backlog.json 路径（可选，用于覆盖率计算）
        req_text: 终版需求文本（可选）
    """
    tc_path = Path(test_cases_path)
    if not tc_path.exists():
        raise FileNotFoundError(f"用例文件不存在: {tc_path}")

    with tc_path.open(encoding="utf-8") as f:
        tc_data = json.load(f)

    cases = tc_data.get("test_cases", [])
    total = len(cases)

    # ── 结构完整性审查 ────────────────────────────────────────────────────
    structure = _check_structure(cases)

    # ── 覆盖率审查（如果提供了 backlog）──────────────────────────────────
    coverage_map = {}
    module_stats = {}

    if backlog_path and Path(backlog_path).exists():
        with Path(backlog_path).open(encoding="utf-8") as f:
            backlog = json.load(f)
        coverage_map = _check_coverage(cases, backlog)
    else:
        # 按模块统计
        for case in cases:
            m = case.get("module", "OTHER")
            module_stats.setdefault(m, {"total": 0, "filled": 0})
            module_stats[m]["total"] += 1
            if case.get("title") and case.get("steps"):
                module_stats[m]["filled"] += 1

    # ── 通过判定 ─────────────────────────────────────────────────────────
    coverage_pass = (
        len(coverage_map) == 0 or
        all(cov.coverage >= 0.6 for cov in coverage_map.values())
    )
    structure_pass = structure.pass_rate >= 0.90
    overall_pass = coverage_pass and structure_pass

    # ── AI 审核摘要 ───────────────────────────────────────────────────────
    ai_summary = _build_ai_summary(
        cases, total, structure, coverage_map, module_stats
    )

    return ReviewResult(
        overall_pass=overall_pass,
        coverage=coverage_map,
        structure=structure,
        total_cases=total,
        module_stats=module_stats,
        ai_input_summary=ai_summary,
        date=datetime.now().strftime("%Y-%m-%d"),
    )


# ── 内部审查函数 ────────────────────────────────────────────────────────────

_REQUIRED_FIELDS = ["title", "precondition", "steps", "expected"]


def _check_structure(cases: list) -> StructureResult:
    total_fields = len(cases) * len(_REQUIRED_FIELDS)
    filled = 0
    missing = []

    for case in cases:
        for field_name in _REQUIRED_FIELDS:
            val = case.get(field_name, "")
            if val and str(val).strip():
                filled += 1
            else:
                missing.append({"case_id": case.get("case_id", "?"), "field": field_name})

    pass_rate = filled / total_fields if total_fields else 0.0
    return StructureResult(
        total_fields_filled=filled,
        total_fields=total_fields,
        pass_rate=round(pass_rate, 3),
        missing_field_cases=missing[:20],  # 只保留前20条
    )


def _check_coverage(cases: list, backlog: dict) -> dict:
    """计算每个 Epic 的 Story 覆盖率。"""
    # 建立 case_id → story_id 映射
    covered_stories = set()
    for case in cases:
        sid = case.get("story_id", "")
        if sid:
            covered_stories.add(sid)

    results = {}
    for epic in backlog.get("epics", []):
        epic_id = epic["id"]
        stories  = epic.get("stories", [])
        total    = len(stories)
        covered  = sum(1 for s in stories if s["id"] in covered_stories)
        missing  = [s["id"] for s in stories if s["id"] not in covered_stories]
        coverage = covered / total if total else 0.0

        results[epic_id] = CoverageResult(
            epic_id=epic_id,
            epic_title=epic.get("title", ""),
            total_stories=total,
            covered_stories=covered,
            coverage=round(coverage, 3),
            missing_stories=missing,
        )
    return results


def _build_ai_summary(
    cases: list,
    total: int,
    structure: StructureResult,
    coverage: dict,
    module_stats: dict,
) -> str:
    """生成 AI 审核用的 ~500字符摘要。"""
    lines = [
        f"用例总数: {total} | 结构完整率: {structure.pass_rate:.0%}",
    ]

    if coverage:
        low_cov = [(eid, cov.coverage) for eid, cov in coverage.items() if cov.coverage < 0.8]
        if low_cov:
            lines.append(f"低覆盖率Epic: {', '.join(f'{eid}({c:.0%})' for eid,c in low_cov)}")
        lines.append(f"已覆盖Epic: {len(coverage)}个")
    elif module_stats:
        lines.append(f"按模块统计: {module_stats}")

    if structure.missing_field_cases:
        lines.append(f"缺失字段用例: {len(structure.missing_field_cases)}个")

    return " | ".join(lines)[:500]


# ── 保存审查结果 ───────────────────────────────────────────────────────────

def save_review_report(
    result: ReviewResult,
    output_dir: str | Path,
    req_name: str = "游戏道具商城系统",
    version: str = "v1.0",
) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = output_dir / "review_report.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(result), f, ensure_ascii=False, indent=2)
    print(f"[S7] review_report.json → {json_path}")

    # Markdown
    md_path = output_dir / "review_report.md"
    md = _render_markdown(result, req_name, version)
    with md_path.open("w", encoding="utf-8") as f:
        f.write(md)
    print(f"[S7] review_report.md → {md_path}")

    return {"json": str(json_path), "md": str(md_path)}


def _render_markdown(r: ReviewResult, req_name: str, version: str) -> str:
    lines = [
        f"# 用例审查报告 — {req_name} {version}\n",
        f"审查日期：{r.date}\n",
        f"## 审查结论\n\n",
        f"**{'✅ PASS' if r.overall_pass else '❌ FAIL'}**\n\n",
        f"## 统计概览\n\n",
        f"- 用例总数：{r.total_cases}\n",
        f"- 结构完整率：{r.structure.pass_rate:.1%}\n",
        f"- 覆盖率 Epic 数：{len(r.coverage)}\n\n",
    ]

    if r.coverage:
        lines.append("## Epic 覆盖率\n\n")
        lines.append("| Epic ID | 标题 | 覆盖Story | 覆盖率 |\n")
        lines.append("|---------|------|-----------|--------|\n")
        for cov in r.coverage.values():
            pct = f"{cov.coverage:.0%}"
            flag = "🟢" if cov.coverage >= 0.8 else "🟡" if cov.coverage >= 0.6 else "🔴"
            lines.append(f"| {cov.epic_id} | {cov.epic_title} | "
                         f"{cov.covered_stories}/{cov.total_stories} | {flag} {pct} |\n")

    lines.append("\n## 结构完整性\n\n")
    lines.append(f"- 已填字段：{r.structure.total_fields_filled}/{r.structure.total_fields} "
                f"({r.structure.pass_rate:.1%})\n")

    if r.structure.missing_field_cases:
        lines.append(f"- 缺失字段用例（前10条）：\n")
        for item in r.structure.missing_field_cases[:10]:
            lines.append(f"  - {item['case_id']}: 缺失「{item['field']}」\n")

    lines.append("\n## AI 审核摘要\n\n")
    lines.append(f"```\n{r.ai_input_summary}\n```\n")

    return "".join(lines)


if __name__ == "__main__":
    # 快速测试
    req_dir = Path(__file__).parent.parent / "workflow_assets" / "游戏道具商城系统"
    tc_path = req_dir / "「S6 测试用例生成」" / "v1.0" / "test_cases.json"
    bd_path = req_dir / "「S2 需求拆解」" / "v1.0" / "backlog.json"

    if tc_path.exists():
        result = auto_review(tc_path, bd_path if bd_path.exists() else None)
        print(f"审查结果: {'PASS' if result.overall_pass else 'FAIL'}")
        print(f"用例数: {result.total_cases}")
        print(f"结构完整率: {result.structure.pass_rate:.1%}")
        for cid, cov in result.coverage.items():
            print(f"  {cid}: {cov.coverage:.0%}")
    else:
        print("用例文件不存在")
