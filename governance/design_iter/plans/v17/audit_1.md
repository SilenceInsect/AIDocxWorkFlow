# S1.5 现状审计报告

> **Goal**: 根据 S1，推翻旧的 S1.5 阶段的一切，重新规定需求澄清阶段
> **Round**: 1
> **Date**: 2026-07-20

---

## T1 审计结论

### 问题清单

| # | 问题 | 严重度 | 来源证据 |
|---|------|--------|----------|
| P1 | **S1 产出与 S1.5 输入不匹配** | 🔴 BLOCKER | S1.REVIEW.mdc §S1产出清单=6份；S1.5 Clarification.mdc §前置物料=10份（含 testability_assessment.md/edge_cases.md/review_issues.md）——这两个列表对不上 |
| P2 | **三阶段定位重复且各自表述** | 🔴 BLOCKER | S1.REVIEW.mdc §三阶段核心边界 / S1.5 Clarification.mdc §三阶段核心边界 / S2.BREAKDOWN.mdc §三阶段核心边界——三个文件都写了同一段话，且措辞略有不同 |
| P3 | **S1.5 SKILL.md 与 STAGE_S1.5 Clarification.mdc 产出矛盾** | 🔴 BLOCKER | SKILL.md §产出3 提到 clarification_report.md；STAGE 文件无此产出 |
| P4 | **10 份物料清单过重** | 🟡 MAJOR | S1.5 Clarification.mdc 前置物料要求 10 份，但 S1 实际最多产出 6-7 份，其余（testability_assessment.md/edge_cases.md/review_issues.md）在 S1 规范中不存在 |
| P5 | **P0/P1/P2 分级与强付费项 3 段重叠** | 🟡 MAJOR | S1 Clarification checklist 有 P0/P1/P2 分级；S1 同时有强付费项 PURCHASE_STRONG 3 段（程序自测点/测试覆盖/策划验收）——两套体系是否合并不清 |
| P6 | **S1.5 的价值说不清** | 🟡 MAJOR | 三阶段定位写"澄清解决'怎么做算对'"，但实际只是"读取人工填写的 checklist + 完善需求文档"——没说清楚相比 S1/S2 的增量价值 |
| P7 | **exit_permission.json 字段膨胀** | 🟡 MAJOR | 含遗留项/s2_guidance/fallback_rules 等 7 个顶层字段；但 S2 实际只用 can_proceed_to_s2 + quality_level |

### 根因分析

1. **规范漂移**：S1.5 Clarification.mdc 是早期版本，S1 REVIEW.mdc 是 v18 改写，两者不同步
2. **文档冗余**：三阶段边界被写了 3 次，无统一 SSOT
3. **AI 产出混入人工决策**：testability_assessment.md/edge_cases.md 是 AI 产出，S1.5 不应该验收它们（那是 S1 的活）

---

## 验收标准审计

| # | 验收标准 | 对应问题 | 审计结论 |
|---|---------|----------|---------|
| AC-1 | 新 S1.5 阶段规范文档完成 | P1-P7 | ✅ 相关，需执行 |
| AC-2 | 新 S1.5 SKILL.md 完成 | P3 | ✅ 相关，需执行 |
| AC-3 | 与 S1/S2 的衔接契约清晰 | P2 | ✅ 相关，需执行 |
| AC-4 | 旧 10 份物料清单重新评估 | P1/P4 | ✅ 相关，需执行 |
| AC-5 | 新 S1.5 流程有实际需求场景验证 | P6 | ✅ 相关，需执行 |

---

## 审计结论

**PASS（含遗留问题）**

T1 完成现状审计，发现 7 个问题（含 3 个 BLOCKER）。进入 Act 阶段执行 T2-T5。

### 遗留问题（带入下一轮）

- R1：S1 的强付费项 3 段体系与 S1.5 P0/P1/P2 分级是否合并（待 T2 决策）
- R2：旧 S1.5 产物（workflow_assets/ 下的 clarification_checklist/exit_permission）是否需要迁移（待 T4 决策）
