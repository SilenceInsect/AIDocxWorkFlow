#!/usr/bin/env python3
"""S7 用例体检器（thin wrapper）— 脚本不审查质量，只做机械统计 + 摘要输出。

⚠️ 设计原则（v2.0 重构 — 2026-06-15）：
- **脚本不判 PASS/FAIL**：硬指标审查 = 强行套结构，真实需求多种多样。
- **脚本只做轻量体检**：
  1. TC 字段是否填写（机械检查，S6 10列）
  2. S5 TP 字段是否填写（S5 v3 schema）
  3. 模块字段是否归一为 8 模块（机械检查）
  4. Story/Epic 覆盖统计（仅事实统计，不评判）
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
    s5_structure: StructureSnapshot | None = None
    coverage: dict = field(default_factory=dict)
    module_counter: dict = field(default_factory=dict)
    type_counter: dict = field(default_factory=dict)
    ai_input_summary: str = ""
    date: str = ""


# ── S6 TC 字段检查（10列）────────────────────────────────────────────────

def _check_structure(cases: list) -> StructureSnapshot:
    """检查 S6 TC 必填字段（10列：用例描述/功能描述/前置/步骤/预期/优先级/状态）。

    v2.0 修复（2026-06-15）：
    - 旧 4 字段（用例描述/前置/步骤/预期）→ S6 10 列
    - 字段名支持中英双语（用例描述=title / 功能描述=功能描述 等）
    """
    REQUIRED_TC_FIELDS = [
        ("用例描述",  "title"),
        ("功能描述",  "功能描述"),
        ("前置条件", "precondition"),
        ("操作步骤", "steps"),
        ("预期结果", "expected"),
        ("优先级",   "优先级"),
        ("用例状态", "用例状态"),
    ]
    total_fields = len(cases) * len(REQUIRED_TC_FIELDS)
    filled = 0
    missing = []

    for case in cases:
        for zh, en in REQUIRED_TC_FIELDS:
            val = case.get(zh) or case.get(en)
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
        if "id" in tp and "tp_id" not in tp:
            tp["tp_id"] = tp.pop("id")
        if "type" in tp and "test_point_type" not in tp:
            tp["test_point_type"] = tp.pop("type")
        if "title" in tp and "description" not in tp:
            tp["description"] = tp.pop("title")

    total_fields = len(test_points) * len(S5_REQUIRED_FIELDS)
    filled = 0
    missing = []

    for tp in test_points:
        tp_id = tp.get("tp_id", "?")
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
) -> ReviewSnapshot:
    """生成审查事实快照（**不**给 PASS/FAIL 判决）。

    v2.0 新增（2026-06-15）：
    - test_points_path 参数：传入 S5 test_points.json 路径时，额外检查 S5 v3 schema 字段
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
    cases = tc_data.get("test_cases", [])

    structure = _check_structure(cases)
    module_counter = _module_stats(cases)
    type_counter = _type_stats(cases)

    # v2.0 新增：S5 TP schema 检查
    s5_structure = None
    if test_points_path and Path(test_points_path).exists():
        tp_path = Path(test_points_path)
        with tp_path.open(encoding="utf-8") as f:
            tp_data = json.load(f)
        # 兼容 3 种 JSON 结构
        if isinstance(tp_data, list):
            tp_list = tp_data
        elif isinstance(tp_data, dict):
            tp_list = []
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

    ai_summary = _build_ai_summary(
        cases, structure, s5_structure, coverage, module_counter, type_counter
    )

    return ReviewSnapshot(
        total_cases=len(cases),
        structure=structure,
        s5_structure=s5_structure,
        coverage=coverage,
        module_counter=module_counter,
        type_counter=type_counter,
        ai_input_summary=ai_summary,
        date=datetime.now().strftime("%Y-%m-%d"),
    )


# ── 兼容旧调用方（auto_review） ─────────────────────────────────────────────

def auto_review(
    test_cases_path: str | Path,
    backlog_path: str | Path | None = None,
    test_points_path: str | Path | None = None,
) -> ReviewSnapshot:
    """兼容旧 API。**v2.0 不再返回 PASS/FAIL 判决**——改返回事实快照。"""
    return snapshot(test_cases_path, backlog_path, test_points_path)


# ── 报告保存 ────────────────────────────────────────────────────────────────

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
        f"\n- TC 必填字段填写率：{snap.structure.fill_rate:.1%}（{snap.structure.total_fields_filled}/{snap.structure.total_fields}）",
        f"\n- 模块分布：{snap.module_counter}",
        f"\n- 类型分布：{snap.type_counter}\n",
    ]

    # v2.0 新增：S5 TP 字段检查
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

    if snap.structure.missing_field_cases:
        lines.append(f"\n## 3. TC 缺失字段用例（前 {len(snap.structure.missing_field_cases)} 条）\n")
        for item in snap.structure.missing_field_cases:
            lines.append(f"- {item['case_id']}: 缺失「{item['field']}」\n")

    lines.append(f"\n## 4. AI 审核输入（事实摘要）\n\n```\n{snap.ai_input_summary}\n```\n")
    lines.append("\n## 5. LLM 审查建议（待 LLM 在对话中填写）\n\n")
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
