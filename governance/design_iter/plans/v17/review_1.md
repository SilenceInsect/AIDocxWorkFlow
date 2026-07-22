# Round 1 Review — S1.5 现状审计复盘

> **Goal**: 根据 S1，推翻旧的 S1.5 阶段的一切，重新规定需求澄清阶段
> **Round**: 1
> **Date**: 2026-07-20

---

## 缺陷汇总

### 严重缺陷

| # | 缺陷 | 来源 |
|---|------|------|
| D1 | S1 产出 6 份 vs S1.5 要求 10 份——根本性数字对不上 | P1（BLOCKER） |
| D2 | 三阶段定位被写了 3 次且措辞略有差异——无统一 SSOT | P2（BLOCKER） |
| D3 | SKILL.md 产出 clarification_report.md，STAGE 文件无此产出——文档打架 | P3（BLOCKER） |

### 一般缺陷

| # | 缺陷 | 来源 |
|---|------|------|
| D4 | 10 份物料中 testability_assessment.md/edge_cases.md/review_issues.md 在 S1 规范中不存在 | P4 |
| D5 | 两套分级体系（P0/P1/P2 vs PURCHASE_STRONG 3 段）职责不清 | P5 |
| D6 | S1.5 定位模糊——说是"澄清怎么做算对"，实际只是读 checklist | P6 |

### 根因定位

1. **机制问题**：S1.5 Clarification.mdc 是旧版规范，与 S1 REVIEW.mdc v18 不同步
2. **规范问题**：三阶段边界无 SSOT，各自为战
3. **文档问题**：SKILL.md 由 AI 生成，STAGE 文件由人工维护，两者未同步

---

## 修复方案

### R1：统一三阶段定位（写入 AGENTS.md SSOT）

**决策**：三阶段定位只在 AGENTS.md 写一次，STAGE_S*.mdc 只引用不重复。

**执行**：STAGE_S1_REVIEW.mdc、STAGE_S1.5 Clarification.mdc、STAGE_S2_BREAKDOWN.mdc 删除"三阶段核心边界"节，统一引用 AGENTS.md。

### R2：精简 S1.5 前置物料清单（3 份，强制）

**决策**：S1.5 只验收 3 份 S1 产出：
1. `clarification_checklist.md`（P0/P1/P2 人工填写）
2. `终版需求.md`（S1 草稿，S1.5 完善）
3. `review_report.md`（S1 质量评价，S1.5 读取参考）

其余 S1 产出（gm_commands.md/test_coverage.md/planning_acceptance.md/quality_loop_report.md/role_definitions.md）直接进入 S2，不经过 S1.5。

**理由**：S1.5 是人工决策阶段，不是文档整理阶段。AI 产出不需要 S1.5 验收。

### R3：统一 S1.5 SKILL.md 与 STAGE_S1.5 Clarification.mdc

**决策**：删除 clarification_report.md 产出，统一为：
1. 完善 `终版需求.md`
2. 生成 `exit_permission.json`

**执行**：重写两个文件。

---

## 执行动作

| # | 动作 | 影响文件 | 优先级 |
|---|------|---------|--------|
| A1 | 删除 STAGE_S1_REVIEW.mdc §三阶段核心边界 | STAGE_S1_REVIEW.mdc | P1 |
| A2 | 删除 STAGE_S2_BREAKDOWN.mdc §三阶段核心边界 | STAGE_S2_BREAKDOWN.mdc | P1 |
| A3 | 重写 STAGE_S1.5 Clarification.mdc（精简物料+统一产出） | STAGE_S1.5 Clarification.mdc | P1 |
| A4 | 重写 aidocx-s1-5-clarification/SKILL.md | aidocx-s1-5-clarification/SKILL.md | P1 |
| A5 | 更新 AGENTS.md §三阶段定位 | AGENTS.md | P2 |
