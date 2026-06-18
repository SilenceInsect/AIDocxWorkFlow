#!/usr/bin/env python3
"""S4 流程图质量门禁 — 机械事实检查，不做语义推理。

设计原则：
- 脚本只做机械事实判断：ID 重复、语法错误、章节缺失
- LLM 负责内容优化：判断风险点归类是否合理、异常路径是否完整
- 脚本输出 issue 列表供 LLM 写 fail_report，不自行判决

验收标准（来自 STAGE_S4.mdc §质量门禁）：
  1. 每个 Epic 有 4 类产出（flowchart / sequence / 异常树 / 风险点）
  2. 风险点全局 ID 唯一（无重复 R-NNN）
  3. 异常树叶子节点 ID 唯一（无重复 S4-{EpicID}-X.Y.Z）
  4. Mermaid 流程图语法合法
  5. Mermaid 时序图语法合法
  6. 风险点 ↔ 异常树叶子交叉引用（每条风险点指向 ≥1 叶子）

用法：
    from ai_workflow.s4_validator import validate_s4_output
    report = validate_s4_output(
        flow_md_path="path/to/business_flow.md",
        backlog_json_path="path/to/backlog.json",
    )
    # report["passed"]: bool
    # report["issues"]: list[dict]  — 每个 issue 含 type / epic_id / detail
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ValidationIssue:
    """质量门禁问题（纯事实陈述，不含判决）。"""
    type: str           # e.g. "risk_id_duplicate", "mermaid_syntax_error"
    epic_id: str        # 关联的 Epic，空字符串表示全局问题
    detail: str         # 人类可读的事实描述
    raw_value: str = ""  # 触发问题的原始值（供 LLM 定位）


@dataclass
class ValidationReport:
    """质量门禁报告（事实清单，不含 PASS/FAIL 硬判决）。"""
    passed: bool        # 是否通过门禁（issues 为空时为 True）
    issues: list[ValidationIssue] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)  # 统计数字，供 LLM 写报告用


# ─────────────────────────────────────────────────────────────────────────────
# 核心函数
# ─────────────────────────────────────────────────────────────────────────────

def validate_s4_output(
    flow_md_path: str | Path,
    backlog_json_path: Optional[str | Path] = None,
) -> ValidationReport:
    """对 S4 business_flow.md 做质量门禁。

    Args:
        flow_md_path: business_flow.md 文件路径
        backlog_json_path: backlog.json 路径（可选，用于检查 Epic 章节完整性）

    Returns:
        ValidationReport（不含 PASS/FAIL 硬判决，issues 列表供 LLM 写 fail_report）
    """
    flow_path = Path(flow_md_path)
    if not flow_path.exists():
        raise FileNotFoundError(f"business_flow.md 不存在: {flow_path}")

    flow_text = flow_path.read_text(encoding="utf-8")

    issues: list[ValidationIssue] = []
    metadata: dict = {
        "flow_md_size": len(flow_text),
        "epics_checked": 0,
        "total_risks": 0,
        "total_leaves": 0,
        "total_flowchart_errors": 0,
        "total_sequence_errors": 0,
    }

    # ── 1. Mermaid 语法检查（整文件级别）───────────────────────────────
    flowchart_errors = _check_mermaid_flowchart(flow_text)
    for err in flowchart_errors:
        issues.append(ValidationIssue(
            type="mermaid_flowchart_syntax_error",
            epic_id="",
            detail=err,
        ))
        metadata["total_flowchart_errors"] += 1

    sequence_errors = _check_mermaid_sequence(flow_text)
    for err in sequence_errors:
        issues.append(ValidationIssue(
            type="mermaid_sequence_syntax_error",
            epic_id="",
            detail=err,
        ))
        metadata["total_sequence_errors"] += 1

    # ── 2. 风险点 ID 唯一性 ────────────────────────────────────────────
    risk_ids = _extract_all_risk_ids(flow_text)
    dupes = _find_duplicates(risk_ids)
    for dupe_group in dupes:
        ids_str = ", ".join(dupe_group)
        issues.append(ValidationIssue(
            type="risk_id_duplicate",
            epic_id="",
            detail=f"风险点 ID 出现重复：{ids_str}",
            raw_value=ids_str,
        ))
    metadata["total_risks"] = len(risk_ids)

    # ── 3. 异常树叶子 ID 唯一性 ──────────────────────────────────────
    leaf_ids = _extract_all_leaf_ids(flow_text)
    leaf_dupes = _find_duplicates(leaf_ids)
    for dupe_group in leaf_dupes:
        ids_str = ", ".join(dupe_group)
        issues.append(ValidationIssue(
            type="exception_tree_leaf_duplicate",
            epic_id="",
            detail=f"异常树叶子 ID 出现重复：{ids_str}",
            raw_value=ids_str,
        ))
    metadata["total_leaves"] = len(leaf_ids)

    # ── 4. Epic 章节完整性（需要 backlog.json）─────────────────────────
    if backlog_json_path and Path(backlog_json_path).exists():
        bd_data = json.loads(Path(backlog_json_path).read_text(encoding="utf-8"))
        epic_issues = _check_epic_sections(flow_text, bd_data)
        issues.extend(epic_issues)
        metadata["epics_checked"] = len(bd_data.get("epics", []))

    # ── 5. 风险点 ↔ 异常树叶子交叉引用 ───────────────────────────────
    # 每条风险点至少指向一个异常树叶子（S4-{EpicID}-X.Y.Z 格式引用）
    cross_ref_issues = _check_cross_references(flow_text)
    issues.extend(cross_ref_issues)
    metadata["cross_ref_missing"] = len(cross_ref_issues)

    return ValidationReport(
        passed=len(issues) == 0,
        issues=issues,
        metadata=metadata,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 子检查函数（每个只做一件事）
# ─────────────────────────────────────────────────────────────────────────────

def _check_mermaid_flowchart(text: str) -> list[str]:
    """检查 Mermaid flowchart 语法错误。

    检查规则：
    - flowchart 块内不允许空节点（[""] 或 ["  "]）
    - flowchart 块内不允许孤立箭头（--> 前后无节点）
    - 每个 ```mermaid 块必须以 flowchart TD/TB/BT/LR/RL 开头
    - 闭合 ``` 数量与开头 ```mermaid 数量一致
    """
    errors: list[str] = []

    # 找所有 ```mermaid 块
    block_pattern = re.compile(r'```mermaid\s*\n(.*?)```', re.DOTALL | re.IGNORECASE)
    blocks = block_pattern.findall(text)

    for idx, block in enumerate(blocks, 1):
        block_stripped = block.strip()
        if not block_stripped.startswith(("flowchart", "graph")):
            continue  # 非 flowchart 块，跳过

        # 检查空节点
        for line_num, line in enumerate(block.splitlines(), 1):
            if re.search(r'\[\s*\]', line) or re.search(r'\(\s*\)', line):
                errors.append(
                    f"第 {idx} 个 flowchart 块第 {line_num} 行：空节点 {line.strip()!r}"
                )

        # 检查孤立箭头（箭头前后无节点名）
        for line_num, line in enumerate(block.splitlines(), 1):
            line = line.strip()
            # 匹配 --> |label| --> 或 --> -->
            arrows = re.findall(r'(-{2,}>+)', line)
            if arrows:
                parts = re.split(r'(-{2,}>+)', line)
                parts = [p.strip() for p in parts if p.strip() and not re.match(r'^[-=>]+$', p)]
                if len(parts) < 2 and arrows:
                    errors.append(
                        f"第 {idx} 个 flowchart 块第 {line_num} 行：孤立箭头 {line!r}"
                    )

    return errors


def _check_mermaid_sequence(text: str) -> list[str]:
    """检查 Mermaid sequence diagram 语法错误。

    检查规则：
    - 每个 sequenceDiagram 块必须闭合
    - 箭头两侧必须有 participant 或 actor
    - 不允许空 participant 声明
    """
    errors: list[str] = []

    block_pattern = re.compile(r'```mermaid\s*\n(.*?)```', re.DOTALL | re.IGNORECASE)
    blocks = block_pattern.findall(text)

    for idx, block in enumerate(blocks, 1):
        block_stripped = block.strip()
        if not block_stripped.startswith("sequenceDiagram"):
            continue

        lines = block.splitlines()
        # 检查空 participant
        for line_num, line in enumerate(lines, 1):
            if re.match(r'\s*participant\s+\|?\s*\|?\s*$', line):
                errors.append(
                    f"第 {idx} 个 sequence 块第 {line_num} 行：空 participant 声明 {line.strip()!r}"
                )
            # 检查无 participant 的箭头
            if re.search(r'(-{2,}>+|-->)', line):
                if not re.search(r'participant|actor|\w+->>', line.split('-->')[0]):
                    errors.append(
                        f"第 {idx} 个 sequence 块第 {line_num} 行：箭头前无 participant {line.strip()!r}"
                    )

    return errors


def _extract_all_risk_ids(text: str) -> list[str]:
    """提取所有 R-NNN 格式的风险点 ID（NNN 为 3 位数字）。"""
    # 注意：不使用 \b——因为 R-002 中 - 是 \w 的一部分，
    # \b 在 R 前不成立（在字母和 - 之间），用 negative lookahead/lookbehind 代替
    pattern = re.compile(r'(?<![a-zA-Z\d])(R-\d{3})(?![a-zA-Z\d])')
    return pattern.findall(text)


def _extract_all_leaf_ids(text: str) -> list[str]:
    """提取所有 S4-{EpicID}-X.Y.Z 格式的异常树叶子 ID。"""
    pattern = re.compile(r'\b(S4-[A-Z]+(?:-[A-Z]+)*-\d+\.\d+\.\d+)\b')
    return pattern.findall(text)


def _find_duplicates(items: list[str]) -> list[list[str]]:
    """找出重复项，返回分组列表。"""
    from collections import Counter
    counter = Counter(items)
    # counter.items() → (item_string, count)
    # 当 count > 1 时，整条 item 是重复的 → 返回 [item]（单元素 list）
    return [[k] for k, v in counter.items() if v > 1]


def _check_epic_sections(text: str, backlog_data: dict) -> list[ValidationIssue]:
    """检查每个 Epic 是否有 4 类产出章节。

    章节判定（按 STAGE_S4.mdc 规范顺序）：
    1. 主业务流程（mermaid flowchart）
    2. 时序图（mermaid sequenceDiagram）
    3. 异常/错误决策树（树形结构文本）
    4. 风险点（风险 ID 表）
    """
    issues: list[ValidationIssue] = []

    epics = backlog_data.get("epics", [])
    if not epics:
        return issues

    for epic in epics:
        epic_id = epic.get("id", "")
        epic_title = epic.get("title", "")

        # 找该 Epic 对应的章节（在 business_flow.md 中搜索）
        # 章节以 "## N. {EpicID}" 或 "## {EpicID}" 或 "### {EpicID}" 开头
        epic_section_pattern = re.compile(
            rf"(?:^|\n)(?:#+\s*)({re.escape(epic_id)}[^\n]*|{re.escape(epic_title)}[^\n]*)(?=\n|$)",
            re.MULTILINE,
        )
        epic_match = epic_section_pattern.search(text)
        if not epic_match:
            issues.append(ValidationIssue(
                type="epic_section_missing",
                epic_id=epic_id,
                detail=f"Epic [{epic_id}] {epic_title!r} 在 business_flow.md 中未找到对应章节",
            ))
            continue

        # 取该 Epic 章节到下一个 ## 章节之间的文本
        section_start = epic_match.start()
        next_section = re.search(r"\n## ", text[section_start + 1:])
        if next_section:
            section_text = text[section_start:section_start + 1 + next_section.start()]
        else:
            section_text = text[section_start:]

        # 检查 4 类产出
        has_flowchart = bool(re.search(r"flowchart\s+(TD|TB|BT|LR|RL)", section_text, re.IGNORECASE))
        has_sequence = bool(re.search(r"sequenceDiagram", section_text, re.IGNORECASE))
        has_tree = bool(re.search(r"异常.*决策树|S4-[A-Z]+-\d+\.\d+\.\d+", section_text))
        has_risks = bool(re.search(r"\bR-\d{3}\b", section_text))

        missing = []
        if not has_flowchart:
            missing.append("主业务流程（flowchart）")
        if not has_sequence:
            missing.append("时序图（sequenceDiagram）")
        if not has_tree:
            missing.append("异常/错误决策树")
        if not has_risks:
            missing.append("风险点清单")

        for m in missing:
            issues.append(ValidationIssue(
                type="epic_missing_section",
                epic_id=epic_id,
                detail=f"Epic [{epic_id}] {epic_title!r} 缺少章节：{m}",
            ))

    return issues


def _check_cross_references(text: str) -> list[ValidationIssue]:
    """检查风险点是否指向异常树叶子。

    每条风险点应在同一行/附近文本中包含 S4-{EpicID}-X.Y.Z 引用。
    交叉引用率 < 50% 时给出警告（不是 fail）。
    """
    issues: list[ValidationIssue] = []

    # 提取每条风险点所在行
    risk_line_pattern = re.compile(r'^\s*\|\s*(R-\d{3})\s*\|.*?\|(.*?)\|.*$', re.MULTILINE)
    risk_lines = list(risk_line_pattern.finditer(text))

    if not risk_lines:
        return issues  # 无风险点，跳过

    unreferenced = []
    for m in risk_lines:
        risk_id = m.group(1)
        rest = m.group(2)
        # 在该行及周围文本中查找 S4-{EpicID}-X.Y.Z
        line_start = m.start()
        line_end = m.end()
        window = text[max(0, line_start - 50):min(len(text), line_end + 200)]
        if not re.search(r'S4-[A-Z]+(?:-[A-Z]+)*-\d+\.\d+\.\d+', window):
            unreferenced.append(risk_id)

    # 交叉引用率 < 50% 时报告（警告，非 fail）
    coverage = (len(risk_lines) - len(unreferenced)) / len(risk_lines) if risk_lines else 1.0
    if coverage < 0.5 and unreferenced:
        seen = set()
        for rid in unreferenced:
            if rid not in seen:
                seen.add(rid)
                issues.append(ValidationIssue(
                    type="risk_no_exception_tree_reference",
                    epic_id="",
                    detail=f"风险点 [{rid}] 未找到异常树叶子引用（交叉引用率 {coverage:.0%}）",
                    raw_value=rid,
                ))

    return issues


# ─────────────────────────────────────────────────────────────────────────────
# 输出函数
# ─────────────────────────────────────────────────────────────────────────────

def report_to_dict(report: ValidationReport) -> dict:
    """将 ValidationReport 转为 dict（供 JSON 序列化）。"""
    return {
        "passed": report.passed,
        "issues": [
            {
                "type": i.type,
                "epic_id": i.epic_id,
                "detail": i.detail,
                "raw_value": i.raw_value,
            }
            for i in report.issues
        ],
        "metadata": report.metadata,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, sys

    ap = argparse.ArgumentParser(description="S4 流程图质量门禁")
    ap.add_argument("flow_md", help="business_flow.md 路径")
    ap.add_argument("--backlog", default=None, help="backlog.json 路径（可选）")
    ap.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = ap.parse_args()

    try:
        report = validate_s4_output(args.flow_md, args.backlog)
    except FileNotFoundError as e:
        print(f"[s4_validator] 错误: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import json
        print(json.dumps(report_to_dict(report), ensure_ascii=False, indent=2))
    else:
        print(f"[s4_validator] 检查完毕")
        print(f"  问题数: {len(report.issues)}")
        print(f"  通过门禁: {report.passed}")
        for k, v in report.metadata.items():
            print(f"  {k}: {v}")
        if report.issues:
            print("\n详细问题：")
            for i, issue in enumerate(report.issues, 1):
                print(f"  [{i}] [{issue.type}] Epic={issue.epic_id or '全局'} {issue.detail}")
