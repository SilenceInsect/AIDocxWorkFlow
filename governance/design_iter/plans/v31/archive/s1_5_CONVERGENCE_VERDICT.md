<!--
# v31 archive — Round 4 归档说明（2026-07-21）

此文件原本位于 `v31/<原名>.md`，是 **v31 期其他 goal-loop**（s1-regen / s1-clarification-redesign）的残留产物。
归档原因：
- 当前 v31 goal-loop 的主题是 **S5/S6 方法论重写**（v31-s5-s6-methodology-rewrite-001）
- 原 v31/GOAL.md / v31/PLAN.md / v31/CONVERGENCE_VERDICT.md 是 **S1 阶段工作流重新生成** 和 **S1.5 阶段重新规定** 主题的产物
- 与当前主题不匹配，目录语义被污染
- 归档依据：DT-4 方案 C（Round 2 review 决议，Round 3 推迟，Round 4 act 执行）

归档动作：
- 文件名改为 s1_5_<原名>.md（按其原 goal-loop 主题：S1 / S1.5 期产物）
- 文件头加本注释
- 原位置删除，由 v31/PLAN.md（v31 S5/S6 重写正式 SSOT）取代

参考：
- 当前 v31 PLAN.md（正式 SSOT）：v31/PLAN.md
- 归档决策档：v31/review_2.md §DT-4 + v31/review_3.md §D1 + v31/review_4.md
-->

# CONVERGENCE_VERDICT.md

> **Goal**: 根据 S1，推翻旧的 S1.5 阶段的一切，重新规定需求澄清阶段
> **Goal ID**: s1-clarification-redesign-001
> **收敛时间**: 2026-07-20
> **收敛轮次**: 1 轮

---

## 收敛状态

**✅ CONVERGED**

---

## 完成内容

| # | 内容 |
|---|------|
| 1 | S1.5 前置物料从 10 份精简为 3 份（clarification_checklist + 终版需求 + review_report） |
| 2 | 建立三阶段边界 SSOT（AGENTS.md §三阶段核心边界） |
| 3 | 删除 clarification_report.md 产出（SKILL.md 与 STAGE 文件一致） |
| 4 | 精简 exit_permission.json（删除 fallback_rules / strong_purchase_p0_resolved） |
| 5 | 删除 S2 中废弃的 fallback_rules 体系 |
| 6 | S1.5 本质重新定义：人工决策阶段，不生产新知识 |

---

## 验收证据

| 验收标准 | 证据 | 判定 |
|---------|------|------|
| AC-1 新 STAGE_S1.5 Clarification.mdc 完成 | `.cursor/rules/STAGE_S1.5 Clarification.mdc`（248 行） | ✅ PASS |
| AC-2 新 aidocx-s1-5-clarification/SKILL.md 完成 | `.cursor/skills/aidocx-s1-5-clarification/SKILL.md` | ✅ PASS |
| AC-3 S1/S1.5/S2 衔接契约清晰 | S1.S2.STAGE 文件§三阶段边界均引用 AGENTS.md SSOT | ✅ PASS |
| AC-4 旧 10 份物料清单重新评估 | STAGE_S1.5 Clarification.mdc §前置物料 = 3 份 | ✅ PASS |
| AC-5 新 S1.5 流程有实际需求场景引用 | governance/design_iter/current/s1-5-clarification-redesign-v1.md §3 流程图 | ✅ PASS |

---

## 自迭代记录

| # | 改进点 | 来源 |
|---|--------|------|
| R-1 | 发现旧 S1.5 与 S1 REVIEW.mdc v18 不同步，建立 SSOT 防止再次漂移 | T1 审计 |
| R-2 | 发现 fallback_rules 体系在 exit_permission.json 中无实际消费路径，彻底删除 | T4 重写 |
| R-3 | 发现三阶段边界被写了 3 次，建立 AGENTS.md SSOT 统一引用 | T2 定位重定义 |

---

## 剩余问题

| # | 问题 | 影响 | 处理 |
|---|------|------|------|
| L1 | 旧 S1.5 产物（workflow_assets/ 下的历史产物）是否需要归档 | LOW | 人工决策 |
| L2 | 旧 S1.5 10 份物料中 testability_assessment.md/edge_cases.md/review_issues.md 在 S1 规范中不存在——这些文件从哪来 | MEDIUM | 需人工核实（可能是早期版本的遗留） |

---

## 影响范围

| 文件 | 动作 |
|------|------|
| `AGENTS.md` | 新增 §三阶段核心边界（SSOT） |
| `.cursor/rules/STAGE_S1.5 Clarification.mdc` | 重写（248 行） |
| `.cursor/skills/aidocx-s1-5-clarification/SKILL.md` | 重写 |
| `.cursor/rules/STAGE_S1_REVIEW.mdc` | 修改（删除§三阶段边界 + 更新物料表格） |
| `.cursor/rules/STAGE_S2_BREAKDOWN.mdc` | 修改（删除§三阶段边界 + 删除 fallback_rules 章节） |
| `governance/design_iter/INDEX.md` | 新增 v31 条目 |
| `governance/design_iter/plans/v31/` | 新建（PLAN.md + audit_1.md + review_1.md） |
