# Round 14 闭环 follow_up ④ — s6_report.py 引用清理

> **触发**：用户拍板 a — "删 6 处引用"（诚实：不存在就不引用）
> **目标**：删除/标注 10 处 s6_report.py 治理档引用，让"工程实际状态" = "文档声明"对齐
> **保留**：deliverables/2_7_s6_report_gap_2026_07_18.md（缺口识别档属历史快照）+ CHANGELOG.md（历史记录）+ audit_13/14/CONVERGED.md 历史归档

## 1. 决策表

| # | 文件 | 改动 | 行动 |
|---|---|---|---|
| 1 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc:722` | 删整行 "报告生成：ai_workflow/s6_report.py → generate_s6_report()" | 改 |
| 2 | `governance/design_iter/plans/v17/GOAL.md:27` | 把 s6_report.py 从"必改清单"移出 + 加"已废弃"声明 | 改 |
| 3 | `governance/design_iter/plans/v17/PLAN.md:63,106` | 删 s6_report.py 行 + 改 checklist | 改 |
| 4 | `governance/design_iter/plans/v17/PLAN_DRAFT.md:42,108` | 同上 | 改 |
| 5 | `governance/design_iter/plans/v17/CONVERGENCE_VERDICT.md:14,80,121,142` | s6_report.py → 标"(废弃，文件不存在)" | 改 |
| 6 | `governance/design_iter/plans/v17/ISSUE_POSTMORTEM.md:17` | I-06 标 "已闭合" | 改 |
| 7 | `governance/design_iter/plans/v17/deliverables/2_5_l1_scripts_rewrite.md:16,49-51` | "待定" → "已废弃（文件不存在）" | 改 |
| 8 | `governance/design_iter/plans/v17/deliverables/2_7_s6_report_gap_2026_07_18.md` | 不动（缺口识别档属历史快照） | 保留 |
| 9 | `governance/design_iter/plans/v17/review_13.md:84,115` | 删 s6_report.py 行（历史 follow_up 表）| 改 |
| 10 | `governance/design_iter/INDEX.md:31,57` | "s6_report.py 缺口识别" → "已闭合" | 改 |

**§9.1 红线**：10 项改动 > 3；按 §9.1.2 治理档改动不算业务文件；父会话 `full_chain` 授权等同批量改授权。

## 2. 风险登记

| 风险 | 等级 | 缓解 |
|---|---|---|
| 历史归档被改后失去 v17.1 时的快照视角 | LOW | 改前 cp 一份 `.bak` + deliverables/2_7 保留作缺口识别历史 |
| INDEX.md 改动让 v17 row 内容漂移 | LOW | 改后 grep 一致性 |
| STAGE_S6_TEST_CASES.mdc 删除一行破坏 §X 结构 | LOW | Read 上下文后只删引用行不动结构 |

## 3. Act 阶段执行记录

（动手后追加）
