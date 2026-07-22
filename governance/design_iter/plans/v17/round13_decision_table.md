# Round 13 决策表 — 关闭 Round 12 遗留

**日期**：2026-07-19
**目标**：把 Round 12 的"文档化 / CHANGELOG / snapshot"三类遗留推到位，达到 CONVERGED 候选
**父会话授权**：`full_chain`（过程产物 + Python 实现 + 测试 + 规则 .mdc + Skill SKILL.md + 相关文档；禁止 commit git）

---

## 决策表（落档符合 DNA §9.5）

| # | 文件 | 改动 | 影响范围 | 替代方案 |
|---|---|---|---|---|
| 1 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §状态转换规则 | 补 L1∧L2 双门 + per-case 写回 + l2_mode 参数说明 | 规则文档（约束档） | A. 推到 v18 治理档（拒绝：本轮用户明确要求改 .mdc）/ B. 落到 SKILL.md 替代 .mdc（违反 SSOT 对齐） |
| 2 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §用例状态职责边界 | 补 L1∧L2 + per-case + l2_mode + lenient L2 与字段溯源 SSOT 对齐说明 | 技能文档 | A. 只改 .mdc（违反 SSOT 对齐）/ B. 推迟（拒绝：阻塞 CONVERGED） |
| 3 | `CHANGELOG.md` [Unreleased] | 追加 Round 12 修复条目（4 实现 + 1 端到端驱动 + 5 过程产物） | 版本日志 | 必须项 |
| 4 | `.goal-log-db/active/bad7a7fa-.../snapshot.json` | 更新 status=converged_with_followup + last_audit + last_review + efficiency_stats + follow_up_items + latest_artifact | Goal 快照 | 必须项 |
| 5 | `governance/design_iter/plans/v17/audit_13.md` | 5 项价值准则全 PASS 证据链 | 治理 | 必须项 |
| 6 | `governance/design_iter/plans/v17/review_13.md` | 根因 + 修复方案 + 决策表 + 遗留项 | 治理 | 必须项 |
| 7 | `governance/design_iter/plans/v17/CONVERGED.md` | 6 项（状态/完成内容/验收证据/自迭代记录/遗留项/影响范围） | 治理 | 必须项 |
| 8 | `governance/design_iter/current/goal_s6_case_status_redefinition.md` §6.5 | Round 13 追加段（决策表 + 落档证据） | 落档 | 必须项 |

---

## §9.1 红线合规

- 改动文件数 = 8（含 5 治理 + 1 落档 + 1 规则 + 1 技能 + 1 CHANGELOG）
- 8 > §9.1 红线 3
- 父会话授权 `full_chain` 等同批量改授权；落档文件 + 治理资产按 §9.1.2 goal-loop 产物豁免
- 实际业务文件改动：STAGE_S6_TEST_CASES.mdc（约束档）+ SKILL.md（技能档）+ CHANGELOG.md（版本日志豁免）+ snapshot.json（状态推进豁免）= 4 项

## §9.4 先验后答

- 已 Read STAGE_S6_TEST_CASES.mdc L132-175 + SKILL.md L239-272 + CHANGELOG.md L1-55 + snapshot.json 全部 + goal_s6_case_status_redefinition.md §6.4 + out_of_scope.md 全部
- 所有内容引用都基于 Read 结果

## §9.5 落档协议

- 本文件即占位
- 后续 content 展开往本文件填
- 末尾追加"## 落档协议执行记录"段