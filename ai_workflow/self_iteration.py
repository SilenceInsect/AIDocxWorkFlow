#!/usr/bin/env python3
"""S8 自迭代 — 数据聚合与归档脚本。

设计原则：
- 脚本只做：读文件 → 统计 → 写归档
- LLM 的活：缺陷根因归因、Prompt 语义改进建议
- 脚本输出结构化事实，供 LLM 做语义推理

用法：
    from ai_workflow.self_iteration import analyze_and_iterate, archive_experience

    result = analyze_and_iterate(
        version="v1.0",
        review_report_path="path/to/review_report.json",
        feedback_logs_dir="path/to/feedback_logs/",
    )
    # result["fact_summary"]     — 统计事实（脚本产出）
    # result["defect_frequencies"] — 缺陷频率（脚本计数）
    # result["prompt_stats"]     — prompt 引用统计（脚本计数）
    # result["llm_input"]        — 给 LLM 看的汇总 prompt

    archive_experience(result, version="v1.0")
    # 写 feedback_archive/rules/<Module>/通用补充点.md
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FactSummary:
    """S7 审查报告的事实统计。"""
    total_cases: int
    total_epics: int
    total_modules_covered: list[str]
    s4_risk_coverage: float           # S4 风险点覆盖率（数字）
    s4_leaf_coverage: float           # 异常树叶子覆盖率（数字）
    s4_risks_total: int
    s4_leaves_total: int
    is_assumed_fill_rate: float       # is_assumed 字段填充率
    s4_reference_fill_rate: float     # s4_reference 字段填充率
    applies_rule_fill_rate: float     # applies_rule 字段填充率


@dataclass
class DefectFrequency:
    """按阶段/模块统计的缺陷频率（脚本计数，LLM 做语义归因）。"""
    by_root_cause: dict[str, int]    # {"S5_TP": 5, "S2_OBJ": 2, ...}
    by_module: dict[str, int]         # {"BIZ": 7, "HINT": 3, ...}
    by_epic: dict[str, int]           # {"BIZ-PURCHASE": 4, ...}
    by_field: dict[str, int]          # {"module": 3, "boundary": 2, ...}


@dataclass
class IterationInput:
    """LLM 执行 S8 分析所需的完整输入。"""
    fact_summary: FactSummary
    defect_frequencies: DefectFrequency
    module_violations: list[dict]     # 跨模块误判列表
    s2_obj_violations: list[dict]     # S2 拆解违规列表
    s4_epic_violations: list[dict]    # S4 Epic 归属错误列表
    recent_feedback: list[dict]        # feedback_logs 中最近的条目


# ─────────────────────────────────────────────────────────────────────────────
# 核心函数
# ─────────────────────────────────────────────────────────────────────────────

def analyze_and_iterate(
    version: str = "v1.0",
    review_report_path: Optional[str | Path] = None,
    feedback_logs_dir: Optional[str | Path] = None,
    workflow_assets_root: Optional[str | Path] = None,
) -> dict:
    """聚合 S7 审查数据 + 反馈日志，产出 LLM 分析所需的输入。

    脚本只做数据聚合与统计，不做语义推理。

    Args:
        version: 版本标识
        review_report_path: S7 review_report.json 路径
        feedback_logs_dir: feedback_logs/ 目录路径
        workflow_assets_root: workflow_assets 根目录（用于自动推断路径）

    Returns:
        dict 含 fact_summary / defect_frequencies / llm_input
    """
    # 自动推断路径
    if workflow_assets_root is None:
        wf_root = Path(__file__).parent.parent / "workflow_assets"
    else:
        wf_root = Path(workflow_assets_root)

    if review_report_path is None:
        # 尝试在 workflow_assets 下查找最新的 review_report.json
        candidates = list(wf_root.glob("*/「S6 测试用例生成」/*/review_report.json"))
        if candidates:
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            review_report_path = candidates[0]
        elif candidates:
            review_report_path = candidates[0]

    if feedback_logs_dir is None:
        feedback_logs_dir = wf_root / "feedback_logs"

    # ── 1. 读取 S7 审查报告 ───────────────────────────────────────────
    s7_data: dict = {}
    if review_report_path and Path(review_report_path).exists():
        s7_data = json.loads(Path(review_report_path).read_text(encoding="utf-8"))

    # ── 2. 读取 feedback_logs ─────────────────────────────────────────
    feedback_entries: list[dict] = []
    fl_dir = Path(feedback_logs_dir) if feedback_logs_dir else None
    if fl_dir and fl_dir.exists():
        for log_file in sorted(fl_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:20]:
            try:
                entries = json.loads(log_file.read_text(encoding="utf-8"))
                if isinstance(entries, list):
                    feedback_entries.extend(entries)
                else:
                    feedback_entries.append(entries)
            except Exception:
                pass

    # ── 3. 统计 ────────────────────────────────────────────────────────
    fact_summary = _extract_fact_summary(s7_data)
    defect_frequencies = _extract_defect_frequencies(s7_data, feedback_entries)

    # ── 4. 提取违规列表（供 LLM 归因）────────────────────────────────
    module_violations = _extract_module_violations(s7_data)
    s2_obj_violations = _extract_s2_obj_violations(s7_data)
    s4_epic_violations = _extract_s4_epic_violations(s7_data)

    # ── 5. 生成 LLM 输入 ─────────────────────────────────────────────
    llm_input = _build_llm_input(
        fact_summary, defect_frequencies,
        module_violations, s2_obj_violations, s4_epic_violations,
        feedback_entries,
    )

    return {
        "version": version,
        "date": date.today().isoformat(),
        "fact_summary": _fact_summary_to_dict(fact_summary),
        "defect_frequencies": _defect_freq_to_dict(defect_frequencies),
        "module_violations": module_violations,
        "s2_obj_violations": s2_obj_violations,
        "s4_epic_violations": s4_epic_violations,
        "recent_feedback_count": len(feedback_entries),
        "llm_input": llm_input,
    }


def archive_experience(
    iteration_result: dict,
    version: str = "v1.0",
    archive_root: Optional[str | Path] = None,
) -> dict:
    """将可复用的经验归档到知识库。

    脚本只写文件，不判断"哪些经验值得归档"（由 LLM 决定，在 iteration_result["archival_items"] 中指定）。

    Args:
        iteration_result: analyze_and_iterate() 返回的 dict
        version: 版本标识
        archive_root: 归档根目录（默认 workflow_assets/feedback_archive/rules/）

    Returns:
        dict: {"archived": [归档文件路径列表]}
    """
    if archive_root is None:
        archive_root = Path(__file__).parent.parent / "workflow_assets" / "feedback_archive" / "rules"
    else:
        archive_root = Path(archive_root)

    archived_files: list[str] = []
    archival_items: list[dict] = iteration_result.get("archival_items", [])

    for item in archival_items:
        module = item.get("module", "UNKNOWN")
        content = item.get("content", "")
        filename = item.get("filename", "")

        if not content:
            continue

        module_dir = archive_root / module
        module_dir.mkdir(parents=True, exist_ok=True)

        filepath = module_dir / filename if filename else module_dir / "通用补充点.md"
        filepath.write_text(content, encoding="utf-8")
        archived_files.append(str(filepath))

    return {"archived": archived_files}


# ─────────────────────────────────────────────────────────────────────────────
# 内部统计函数
# ─────────────────────────────────────────────────────────────────────────────

def _extract_fact_summary(s7_data: dict) -> FactSummary:
    """从 S7 review_report.json 提取事实统计。"""
    if not s7_data:
        return FactSummary(
            total_cases=0, total_epics=0, total_modules_covered=[],
            s4_risk_coverage=0.0, s4_leaf_coverage=0.0,
            s4_risks_total=0, s4_leaves_total=0,
            is_assumed_fill_rate=0.0, s4_reference_fill_rate=0.0, applies_rule_fill_rate=0.0,
        )

    reviewer_b = s7_data.get("reviewer_b", {})
    snapshot = s7_data.get("snapshot", {})

    # 覆盖率
    s4_cov = reviewer_b.get("s4_risk_coverage", 0.0)
    leaf_cov = reviewer_b.get("s4_leaf_coverage", 0.0)
    risks_total = reviewer_b.get("s4_risks_total", 0)
    leaves_total = reviewer_b.get("s4_leaves_total", 0)

    # 字段填充率
    cases = snapshot.get("test_cases", [])
    total = len(cases) if cases else 1
    is_assumed_filled = sum(1 for c in cases if "is_assumed" in c and c["is_assumed"] is not None)
    s4_ref_filled = sum(1 for c in cases if c.get("s4_reference"))
    applies_rule_filled = sum(1 for c in cases if c.get("applies_rule"))

    return FactSummary(
        total_cases=total,
        total_epics=len(s7_data.get("epic_coverage", {})),
        total_modules_covered=list(snapshot.get("module_counter", {}).keys()),
        s4_risk_coverage=s4_cov,
        s4_leaf_coverage=leaf_cov,
        s4_risks_total=risks_total,
        s4_leaves_total=leaves_total,
        is_assumed_fill_rate=is_assumed_filled / total,
        s4_reference_fill_rate=s4_ref_filled / total,
        applies_rule_fill_rate=applies_rule_filled / total,
    )


def _extract_defect_frequencies(s7_data: dict, feedback_entries: list[dict]) -> DefectFrequency:
    """统计缺陷频率（脚本计数）。"""
    by_root_cause: Counter[str] = Counter()
    by_module: Counter[str] = Counter()
    by_epic: Counter[str] = Counter()
    by_field: Counter[str] = Counter()

    # 从 reviewer_b.misjudgment_root_cause 计数
    reviewer_b = s7_data.get("reviewer_b", {})
    root_causes = reviewer_b.get("misjudgment_root_cause", {})
    for cause, count in root_causes.items():
        if isinstance(count, int):
            by_root_cause[cause] += count
        elif isinstance(count, list):
            by_root_cause[cause] += len(count)

    # 从 uncovered_cases / missing_field_cases 计数
    snapshot = s7_data.get("snapshot", {})
    for c in snapshot.get("test_cases", []):
        mod = c.get("module", "")
        if mod:
            by_module[mod] += 1
        epic = c.get("epic_id", "") or c.get("story_id", "").split("-")[0] if c.get("story_id") else ""
        if epic:
            by_epic[epic] += 1

    # 从 feedback_entries 计数
    for entry in feedback_entries:
        cause = entry.get("root_cause_stage", entry.get("stage", "UNKNOWN"))
        by_root_cause[cause] += 1
        mod = entry.get("module", "")
        if mod:
            by_module[mod] += 1

    # 从字段缺失统计
    missing = snapshot.get("missing_field_cases", [])
    for m in missing:
        field = m.get("field", "UNKNOWN")
        by_field[field] += 1

    return DefectFrequency(
        by_root_cause=dict(by_root_cause),
        by_module=dict(by_module),
        by_epic=dict(by_epic),
        by_field=dict(by_field),
    )


def _extract_module_violations(s7_data: dict) -> list[dict]:
    """提取 S5 TP 跨模块误判列表（供 LLM 归因）。"""
    reviewer_a = s7_data.get("reviewer_a", {})
    return reviewer_a.get("module_misjudgment", [])


def _extract_s2_obj_violations(s7_data: dict) -> list[dict]:
    """提取 S2 拆解违规列表（供 LLM 归因）。"""
    reviewer_b = s7_data.get("reviewer_b", {})
    return reviewer_b.get("s2_obj_violations", [])


def _extract_s4_epic_violations(s7_data: dict) -> list[dict]:
    """提取 S4 Epic 归属错误列表（供 LLM 归因）。"""
    reviewer_b = s7_data.get("reviewer_b", {})
    return reviewer_b.get("s4_epic_violations", [])


# ─────────────────────────────────────────────────────────────────────────────
# LLM 输入生成
# ─────────────────────────────────────────────────────────────────────────────

def _build_llm_input(
    fact_summary: FactSummary,
    defect_frequencies: DefectFrequency,
    module_violations: list[dict],
    s2_obj_violations: list[dict],
    s4_epic_violations: list[dict],
    feedback_entries: list[dict],
) -> str:
    """生成给 LLM 看的汇总 prompt（纯事实，无判决）。"""
    lines = [
        "===== S8 自迭代 — LLM 分析输入（脚本统计事实）=====",
        "",
        "## 1. S7 审查事实统计",
        f"- 测试用例总数：{fact_summary.total_cases}",
        f"- 覆盖 Epic 数：{fact_summary.total_epics}",
        f"- 覆盖模块：{', '.join(fact_summary.total_modules_covered) or '—'}",
        f"- S4 风险点覆盖率：{fact_summary.s4_risk_coverage:.1%}（{int(fact_summary.s4_risk_coverage * fact_summary.s4_risks_total)}/{fact_summary.s4_risks_total}）",
        f"- S4 异常树叶子覆盖率：{fact_summary.s4_leaf_coverage:.1%}（{int(fact_summary.s4_leaf_coverage * fact_summary.s4_leaves_total)}/{fact_summary.s4_leaves_total}）",
        f"- is_assumed 字段填充率：{fact_summary.is_assumed_fill_rate:.1%}",
        f"- s4_reference 字段填充率：{fact_summary.s4_reference_fill_rate:.1%}",
        f"- applies_rule 字段填充率：{fact_summary.applies_rule_fill_rate:.1%}",
        "",
        "## 2. 缺陷频率统计（按根因阶段）",
    ]

    for cause, cnt in sorted(defect_frequencies.by_root_cause.items(), key=lambda x: -x[1]):
        lines.append(f"- {cause}：{cnt} 次")

    lines.extend(["", "## 3. 缺陷频率统计（按模块）"])
    for mod, cnt in sorted(defect_frequencies.by_module.items(), key=lambda x: -x[1]):
        lines.append(f"- {mod}：{cnt} 次")

    lines.extend(["", "## 4. 缺失字段统计"])
    for fld, cnt in sorted(defect_frequencies.by_field.items(), key=lambda x: -x[1]):
        lines.append(f"- {fld}：{cnt} 个用例缺失")

    if module_violations:
        lines.extend(["", "## 5. S5 TP 跨模块误判（供根因分析）"])
        for v in module_violations[:10]:
            lines.append(f"- {v.get('tp_id', '?')}: {v.get('issue', '')}")

    if s2_obj_violations:
        lines.extend(["", "## 6. S2 拆解违规（供根因分析）"])
        for v in s2_obj_violations[:10]:
            lines.append(f"- {v.get('obj_id', '?')}: {v.get('issue', '')}")

    if s4_epic_violations:
        lines.extend(["", "## 7. S4 Epic 归属错误（供根因分析）"])
        for v in s4_epic_violations[:10]:
            lines.append(f"- {v.get('epic_id', '?')}: {v.get('issue', '')}")

    if feedback_entries:
        lines.extend(["", f"## 8. 反馈日志（共 {len(feedback_entries)} 条，最新 5 条）"])
        for entry in feedback_entries[-5:]:
            lines.append(f"- [{entry.get('date', '?')}] {entry.get('summary', str(entry)[:80])}")

    lines.extend([
        "",
        "===== 请按以下维度做语义分析（LLM 的活）=====",
        "1. 根因归因：根据缺陷频率分布，判断哪些阶段/模块是系统性薄弱点",
        "2. Prompt 改进：哪些 prompt 的指令不够清晰导致了这些缺陷？",
        "3. 覆盖率缺口：哪些异常路径/风险场景反复被遗漏？",
        "4. 归档建议：哪些经验值得沉淀到知识库？（返回 archival_items 列表）",
    ])

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 序列化工具
# ─────────────────────────────────────────────────────────────────────────────

def _fact_summary_to_dict(fs: FactSummary) -> dict:
    return {
        "total_cases": fs.total_cases,
        "total_epics": fs.total_epics,
        "total_modules_covered": fs.total_modules_covered,
        "s4_risk_coverage": round(fs.s4_risk_coverage, 4),
        "s4_leaf_coverage": round(fs.s4_leaf_coverage, 4),
        "s4_risks_total": fs.s4_risks_total,
        "s4_leaves_total": fs.s4_leaves_total,
        "is_assumed_fill_rate": round(fs.is_assumed_fill_rate, 4),
        "s4_reference_fill_rate": round(fs.s4_reference_fill_rate, 4),
        "applies_rule_fill_rate": round(fs.applies_rule_fill_rate, 4),
    }


def _defect_freq_to_dict(df: DefectFrequency) -> dict:
    return {
        "by_root_cause": df.by_root_cause,
        "by_module": df.by_module,
        "by_epic": df.by_epic,
        "by_field": df.by_field,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, sys

    ap = argparse.ArgumentParser(description="S8 自迭代 — 数据聚合")
    ap.add_argument("--version", default="v1.0", help="版本标识")
    ap.add_argument("--review-report", dest="review_report", help="S7 review_report.json 路径")
    ap.add_argument("--feedback-logs", dest="feedback_logs", help="feedback_logs/ 目录路径")
    ap.add_argument("--archive-root", dest="archive_root", help="归档根目录")
    ap.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = ap.parse_args()

    result = analyze_and_iterate(
        version=args.version,
        review_report_path=args.review_report,
        feedback_logs_dir=args.feedback_logs,
    )

    # 如果调用方传了 archival_items，从 stdin 读（方便 shell 管道）
    archival_items_raw = sys.stdin.read().strip()
    if archival_items_raw:
        try:
            archival_items = json.loads(archival_items_raw)
            result["archival_items"] = archival_items
            archive_result = archive_experience(result, version=args.version, archive_root=args.archive_root)
            print(f"[S8] 归档完成：{len(archive_result['archived'])} 个文件", file=sys.stderr)
        except json.JSONDecodeError:
            pass

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["llm_input"])
