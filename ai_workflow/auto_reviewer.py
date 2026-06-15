#!/usr/bin/env python3
"""S7 用例体检器（thin wrapper）— 脚本不审查质量，只做机械统计 + 摘要输出。

⚠️ 设计原则（v2.0 重构 — 2026-06-15）：
- **脚本不判 PASS/FAIL**：硬指标审查 = 强行套结构，真实需求多种多样。
- **脚本只做轻量体检**：
  1. 字段是否填写（机械检查）
  2. 模块字段是否归一为 8 模块（机械检查）
  3. Story/Epic 覆盖统计（仅事实统计，不评判）
- **LLM 负责审查**：
  LLM 读 `_ai_input_summary`（含全量用例 + 统计），按 S7 SKILL.md 的 5 维度
  （业务正确性 / 步骤可执行 / 预期可验证 / 风险覆盖 / 业务语言）做语义审查。
- 模板 / 输出完全交给 LLM（在对话/SKILL.md 中完成）
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


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
    coverage: dict
    module_counter: dict
    type_counter: dict
    ai_input_summary: str
    date: str


def _check_structure(cases: list) -> StructureSnapshot:
    """检查必填字段是否填写。脚本只检查"是否填了"，不评判"填得好不好"。"""
    REQUIRED_FIELDS = [
        ("title", "用例描述"),
        ("precondition", "前置条件"),
        ("steps", "操作步骤"),
        ("expected", "预期结果"),
    ]
    total_fields = len(cases) * len(REQUIRED_FIELDS)
    filled = 0
    missing = []

    for case in cases:
        for en, zh in REQUIRED_FIELDS:
            val = case.get(en) or case.get(zh)
            if val and str(val).strip():
                filled += 1
            else:
                missing.append({"case_id": case.get("case_id", "?"), "field": en})

    fill_rate = filled / total_fields if total_fields else 0.0
    return StructureSnapshot(
        total_cases=len(cases),
        total_fields_filled=filled,
        total_fields=total_fields,
        fill_rate=round(fill_rate, 3),
        missing_field_cases=missing[:30],
    )


def _check_coverage(cases: list, backlog: dict) -> dict:
    """计算每个 Epic 的 Story 覆盖事实（脚本只列数字，不评"是否合格"）。"""
    covered_stories = {c.get("story_id", "") for c in cases if c.get("story_id")}

    results = {}
    for epic in backlog.get("epics", []):
        epic_id = epic["id"]
        stories = epic.get("stories", [])
        total = len(stories)
        covered = sum(1 for s in stories if s.get("id") in covered_stories)
        missing = [s.get("id", "?") for s in stories if s.get("id") not in covered_stories]

        results[epic_id] = CoverageSnapshot(
            epic_id=epic_id,
            epic_title=epic.get("name", epic.get("title", "")),
            total_stories=total,
            covered_stories=covered,
            missing_stories=missing,
        )
    return results


def _module_stats(cases: list) -> dict:
    """按归一化模块统计（机械 Counter）。"""
    from test_case_formatter import normalize_module_name
    counter = {}
    for c in cases:
        raw = c.get("module", "") or c.get("模块", "")
        m = normalize_module_name(raw) or "UNKNOWN"
        counter[m] = counter.get(m, 0) + 1
    return counter


def _type_stats(cases: list) -> dict:
    """按 test_type 统计（机械 Counter）。"""
    counter = {}
    for c in cases:
        t = c.get("test_type", "")
        counter[t] = counter.get(t, 0) + 1
    return counter


def _build_ai_summary(cases: list, structure: StructureSnapshot,
                      coverage: dict, module_counter: dict,
                      type_counter: dict) -> str:
    """生成给 LLM 看的"事实摘要"——LLM 拿这个做语义审查。

    注意：摘要里只有事实数字 + 缺失列表，**不含 PASS/FAIL / 比例 / 阈值**。
    """
    lines = [
        "===== 事实快照（脚本机械统计） =====",
        f"用例总数: {len(cases)}",
        f"必填字段填写率: {structure.fill_rate:.1%}",
        f"模块分布: {module_counter}",
        f"类型分布: {type_counter}",
    ]
    if coverage:
        lines.append("Epic 覆盖事实:")
        for eid, cov in coverage.items():
            lines.append(f"  {eid} ({cov.epic_title}): {cov.covered_stories}/{cov.total_stories} Story, missing={cov.missing_stories}")
    if structure.missing_field_cases:
        lines.append(f"缺失字段用例（前10条）:")
        for item in structure.missing_field_cases[:10]:
            lines.append(f"  {item['case_id']}: 缺失「{item['field']}」")
    lines.append("===== 审查交由 LLM（请按 S7 SKILL.md §2 五维度做语义审查） =====")
    return "\n".join(lines)


def snapshot(
    test_cases_path: str | Path,
    backlog_path: str | Path | None = None,
) -> ReviewSnapshot:
    """生成审查事实快照（**不**给 PASS/FAIL 判决）。"""
    tc_path = Path(test_cases_path)
    if not tc_path.exists():
        raise FileNotFoundError(f"用例文件不存在: {tc_path}")
    with tc_path.open(encoding="utf-8") as f:
        tc_data = json.load(f)
    cases = tc_data.get("test_cases", [])

    structure = _check_structure(cases)
    module_counter = _module_stats(cases)
    type_counter = _type_stats(cases)

    coverage = {}
    if backlog_path and Path(backlog_path).exists():
        with Path(backlog_path).open(encoding="utf-8") as f:
            backlog = json.load(f)
        coverage = _check_coverage(cases, backlog)

    ai_summary = _build_ai_summary(
        cases, structure, coverage, module_counter, type_counter
    )

    return ReviewSnapshot(
        total_cases=len(cases),
        structure=structure,
        coverage=coverage,
        module_counter=module_counter,
        type_counter=type_counter,
        ai_input_summary=ai_summary,
        date=datetime.now().strftime("%Y-%m-%d"),
    )


# ── 兼容旧调用方（auto_review）—— 保留入口但返回事实快照 + 警告 ───────────
def auto_review(
    test_cases_path: str | Path,
    backlog_path: str | Path | None = None,
    req_text: str = "",
) -> ReviewSnapshot:
    """兼容旧 API。**v2.0 不再返回 PASS/FAIL 判决**——改返回事实快照。
    旧代码可能用 `.overall_pass` —— 此处加一个**永远为 None** 的属性提示。
    """
    snap = snapshot(test_cases_path, backlog_path)
    # 不在 dataclass 里加 overall_pass 字段（避免误导调用方"按硬指标通过"）
    # 调用方应改用 snapshot() 并由 LLM 自行做语义审查
    print("[S7] 警告: auto_review() 已废弃，请改用 snapshot() + LLM 语义审查")
    return snap


def save_review_report(
    snap: ReviewSnapshot,
    output_dir: str | Path,
    req_name: str = "游戏道具商城系统",
    version: str = "v1.0",
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

    return {"json": str(json_path), "md": str(md_path)}


def _render_markdown(snap: ReviewSnapshot, req_name: str, version: str) -> str:
    lines = [
        f"# 用例审查事实快照 — {req_name} {version}\n",
        f"日期：{snap.date}\n",
        f"\n> ⚠️ **本报告由脚本机械生成，不含 PASS/FAIL 判决**。",
        f"\n> 真实审查由 LLM 按 S7 SKILL.md §2 五维度（业务正确性 / 步骤可执行 / "
        f"预期可验证 / 风险覆盖 / 业务语言）做语义审查。\n",
        f"\n## 1. 事实统计\n",
        f"\n- 用例总数：**{snap.total_cases}**",
        f"\n- 必填字段填写率：{snap.structure.fill_rate:.1%}（{snap.structure.total_fields_filled}/{snap.structure.total_fields}）",
        f"\n- 模块分布：{snap.module_counter}",
        f"\n- 类型分布：{snap.type_counter}\n",
    ]

    if snap.coverage:
        lines.append("\n## 2. Epic 覆盖事实\n")
        lines.append("| Epic | 标题 | Story 覆盖 | 缺失 |\n|---|---|---|---|\n")
        for cov in snap.coverage.values():
            lines.append(f"| {cov.epic_id} | {cov.epic_title} | "
                         f"{cov.covered_stories}/{cov.total_stories} | "
                         f"{', '.join(cov.missing_stories) or '—'} |\n")

    if snap.structure.missing_field_cases:
        lines.append(f"\n## 3. 缺失字段用例（前 {len(snap.structure.missing_field_cases)} 条）\n")
        for item in snap.structure.missing_field_cases:
            lines.append(f"- {item['case_id']}: 缺失「{item['field']}」\n")

    lines.append(f"\n## 4. AI 审核输入（事实摘要）\n\n```\n{snap.ai_input_summary}\n```\n")
    lines.append("\n## 5. LLM 审查建议（待 LLM 在对话中填写）\n\n")
    lines.append("按 S7 SKILL.md §2 五维度填写：\n")
    lines.append("- 业务正确性：\n- 步骤可执行：\n- 预期可验证：\n- 风险覆盖：\n- 业务语言：\n")

    return "".join(lines)


if __name__ == "__main__":
    req_dir = Path(__file__).parent.parent / "workflow_assets" / "游戏道具商城系统"
    tc_path = req_dir / "「S6 测试用例生成」" / "v1.0" / "test_cases.json"
    bd_path = req_dir / "「S2 需求拆解」" / "v1.0" / "backlog.json"

    if tc_path.exists():
        snap = snapshot(tc_path, bd_path if bd_path.exists() else None)
        print(f"用例数: {snap.total_cases}")
        print(f"填写率: {snap.structure.fill_rate:.1%}")
        print(f"模块分布: {snap.module_counter}")
        print(f"类型分布: {snap.type_counter}")
    else:
        print("用例文件不存在")
