#!/usr/bin/env python3
"""S8 — 迭代数据聚合引擎（规则引擎，非 AI）。

输入：feedback_logs/ + 各阶段审查报告
输出：聚合统计 + AI 建议摘要
"""

from __future__ import annotations
import csv, json, re
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class DefectPattern:
    raw_group_key: str                    # 仅保留分组依据，语义命名交给 LLM
    count: int
    severity_counter: dict   # {"CRITICAL": N, "MAJOR": N, ...}
    epic_ids: list
    case_ids: list


@dataclass
class IterationStats:
    total_feedback_entries: int
    total_reviews: int
    defect_patterns: list[DefectPattern]
    top_epic_defects: dict
    ai_summary: str  # ~400 chars for AI


def aggregate_iteration_data(
    feedback_dir: str | Path,
    reports_dir: str | Path | None = None,
) -> IterationStats:
    """
    聚合反馈日志和审查报告，输出统计摘要。

    参数:
        feedback_dir: workflow_assets/feedback_logs/ 路径
        reports_dir: 各阶段审查报告目录（可选）
    """
    feedback_dir = Path(feedback_dir)
    reports_dir  = Path(reports_dir) if reports_dir else None

    entries = []
    # 读取所有反馈文件
    if feedback_dir.exists():
        for fpath in feedback_dir.glob("*"):
            if fpath.suffix.lower() in (".csv", ".xlsx", ".xls", ".json"):
                entries.extend(_read_feedback_file(fpath))

    # 读取审查报告
    review_entries = []
    if reports_dir and reports_dir.exists():
        for rpath in reports_dir.glob("**/review_report.json"):
            try:
                with rpath.open(encoding="utf-8") as f:
                    review_entries.append(json.load(f))
            except Exception:
                pass

    # 统计缺陷模式
    patterns = _analyze_defects(entries)

    # Epic 缺陷统计
    epic_defects = _epic_defect_counts(entries)

    # AI 摘要
    ai_summary = _build_ai_summary(entries, patterns, epic_defects, len(review_entries))

    return IterationStats(
        total_feedback_entries=len(entries),
        total_reviews=len(review_entries),
        defect_patterns=patterns,
        top_epic_defects=epic_defects,
        ai_summary=ai_summary,
    )


# ── 内部函数 ────────────────────────────────────────────────────────────────

def _read_feedback_file(fpath: Path) -> list:
    entries = []
    suffix = fpath.suffix.lower()

    if suffix == ".json":
        with fpath.open(encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                entries.extend(data)
            else:
                entries.append(data)

    elif suffix in (".csv", ".xlsx", ".xls"):
        try:
            import openpyxl
            if suffix in (".xlsx", ".xls"):
                wb = openpyxl.load_workbook(str(fpath))
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                if not rows:
                    return []
                headers = [str(h).strip() if h else "" for h in rows[0]]
                # 找 case_id / result 列
                for row in rows[1:]:
                    entry = {headers[i]: str(v).strip() if v else "" for i, v in enumerate(row)}
                    entries.append(entry)
            else:
                with fpath.open(encoding="utf-8", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        entries.append(row)
        except ImportError:
            pass

    return entries


def _analyze_defects(entries: list) -> list[DefectPattern]:
    """从反馈中分析缺陷模式。"""
    # 找出所有 FAIL 的记录
    failed = [
        e for e in entries
        if str(e.get("result", e.get("执行结果", ""))).upper() == "FAIL"
    ]

    # 按 epic_id / module 分组
    by_module = defaultdict(list)
    for e in failed:
        cid = e.get("case_id", e.get("用例ID", ""))
        module = cid.split("-")[0] if cid else "OTHER"
        by_module[module].append(e)

    patterns = []
    for module, cases in by_module.items():
        severities = Counter(
            str(e.get("severity", e.get("严重程度", "MAJOR"))).upper()
            for e in cases
        )
        cids = [e.get("case_id", e.get("用例ID", "")) for e in cases[:5]]
        patterns.append(DefectPattern(
            raw_group_key=module,                 # 分组键透明暴露，不附语义
            count=len(cases),
            severity_counter=dict(severities),
            epic_ids=[module],
            case_ids=cids,
        ))

    # 按数量排序
    patterns.sort(key=lambda p: p.count, reverse=True)
    return patterns[:10]


def _epic_defect_counts(entries: list) -> dict:
    """各 Epic/模块的缺陷数量统计。"""
    counter = Counter()
    for e in entries:
        if str(e.get("result", e.get("执行结果", ""))).upper() == "FAIL":
            cid = e.get("case_id", e.get("用例ID", ""))
            module = cid.split("-")[0] if cid else "OTHER"
            counter[module] += 1
    return dict(counter)


def _build_ai_summary(entries: list, patterns: list[DefectPattern],
                      epic_defects: dict, review_count: int) -> str:
    total = len(entries)
    failed = sum(
        1 for e in entries
        if str(e.get("result", e.get("执行结果", ""))).upper() == "FAIL"
    )
    pass_rate = f"{(total - failed) / total * 100:.0f}%" if total else "N/A"

    top_defects = ", ".join(
        f"模块{p.raw_group_key}({p.count}例)" for p in patterns[:3]
    ) or "无"

    return (
        f"反馈{total}条，失败{failed}条，通过率{pass_rate}。"
        f"主要缺陷：{top_defects}。"
        f"审查报告{review_count}份。"
    )[:400]


# ── 保存 ───────────────────────────────────────────────────────────────────

def save_iteration_report(
    stats: IterationStats,
    output_dir: str | Path,
    req_name: str = "游戏道具商城系统",
    version: str = "v1.0",
) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "iteration_stats.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(stats), f, ensure_ascii=False, indent=2)
    print(f"[S8] iteration_stats.json → {json_path}")

    return {"json": str(json_path)}
