# Q-AUDIT-001 — 根目录 3 个 md 文件归档决策（v2 重做）

> **触发**：用户 @3 个根目录 md 文件 + 用户提醒"工程化优先、设计优先"
> **重做原因**：v1 决策表（`q_decision_table_q_audit_001.md` v1）忽略了 governance 系统本身的"方案迭代管理"约定——RULE_SKILL_CONSISTENCY_REVIEW 的 7 P0 是"规则变更"，必须走 design_iter；不能擅自新建 `governance/audits/` 顶层子目录
> **DNA 引用**：AGENTS.md"方案迭代管理" + DESIGN_AND_EXECUTION_STANDARDS.mdc §0.1 + DNA_3Q_CHECK §1 5 问 + §9.4 先验后答 + §9.5 落档协议
> **落档时间**：2026-07-08（v2 重做）

---

## 1. 事实核对（§9.4 先验后答 — Read 验证）

| 事实 | 出处 | 关键发现 |
|---|---|---|
| `governance/design_iter/README.md` | 已 Read | "所有规则 / 结构 / 流程的设计方案都在这里管理"——**设计方案的治理目录**，但**没禁止**加 audits 子目录 |
| `design_iter/plans/v2/open_questions.md` §v6.2 闭环 | 已 Read | Q-301（产出门禁）/ Q-401（AGENTS 引用）/ Q-402（Edit 残段）——**审查发现 → Q-XXX 跟踪** 是成熟模式；7 P0 报告**应当**走这个模式 |
| AGENTS.md "方案迭代管理" | 必读 | "所有规则 / 结构 / 流程方案变更走 `governance/design_iter/`：每份方案 v{N} 必有 解决 / 新增 / 遗留 三栏" |
| DESIGN_AND_EXECUTION_STANDARDS.mdc §0.1 | 必读 | "新增文件/目录铁律：创建前必须先判定 Git 归属；若用途横跨两类以上、…**必须先询问再创建**" |
| workflow_assets/游戏道具商城系统/ | 不存在 | .gitignore 范围内；v1.0 release notes 对应目录**未在 git 里落盘**——意味着这份报告本身是孤立快照 |

---

## 2. 决策重审（按工程化优先 + 设计优先）

### 决策点 1：`sample_requirements.md`（不变）

- **原建议**：mv 到 `resource/游戏道具商城系统/sample_requirements.md`
- **工程化审视**：input 类，目录已存在，.gitignore 已规整
- **结论**：**保持 v1 决策**

### 决策点 2：`RELEASE_NOTES_v1.0_rerun.md`（变）

- **v1 决策**：mv 到 `workflow_assets/游戏道具商城系统/「S8 自迭代」/v1.0/`（需新建目录）
- **工程化审视**：
 - workflow_assets 整体 .gitignore
 - 但**v1 备份约定**沿用：`workflow_assets/_refactor_backup/PLAN_v1_2026-06-17_021.bak`（governance/design_iter/README §关键设计）
 - 这条 release notes 性质 = "v1.0 静态正畸 + 全流程端到端跑通的快照报告"——属于**项目治理类交付记录**，不是具体的 workflow_assets 阶段产物
- **重审方案**（3 候选）：
 - **A. 推荐**：mv 到 `workflow_assets/_refactor_backup/RELEASE_NOTES_v1.0_rerun_2026-06-15.md`（沿用 backup 目录约定，无需新建"游戏道具商城系统"这种业务目录）
 - **B. 备选**：删除（v1.0 已被 v2.0 修复取代，价值低）
 - **C. 备选**：保留 v1 决策（移到「S8 自迭代」/v1.0/）——**需要新建**业务目录，违反"最小新建目录"原则

### 决策点 3：`RULE_SKILL_CONSISTENCY_REVIEW.md`（重大变更）

- **v1 决策**：mv 到 `governance/audits/rule_skill_consistency_review_2026-06-15.md`（需新建顶层 audits 子目录）
- **设计审视（致命问题）**：
 - ❌ v1 违反 AGENTS.md "方案迭代管理"——"所有规则 / 结构 / 流程方案变更走 `governance/design_iter/`"
 - ❌ v1 违反 open_questions.md v6.2 成熟模式——"审查发现 → Q-XXX 跟踪"
 - ❌ v1 私自新建 governance/audits/ 顶层子目录——违反 §0.1 铁律
- **重审方案**（3 候选）：
 - **A. 推荐**：走 design_iter 系统——
 1. 报告本身存到 `governance/design_iter/plans/v6/audit_input_RULE_SKILL_CONSISTENCY_REVIEW.md`（v6 = 待创建的新方案版本）
 2. 把 7 P0 提炼为 Q-501 ~ Q-507 加到 `governance/design_iter/plans/v2/open_questions.md`（**Q-501+ 起编号**，接 v2 现有 Q-301 / Q-401 / Q-402）
 3. 创建 v6 PLAN.md 头部 3 栏：
 - **解决**：v2.08 实战中已隐含发现的同类问题（Q-301 产出门禁缺 xlsx）
 - **新增**：7 P0（来自本报告）+ 12 P1 + 5 P2 分类跟踪
 - **遗留**：9 阶段 .mdc / SKILL.md 同步更新工作
 4. v6 切 current？（可选——v2/Q-301 等还待答）
 - **B. 备选**：仅把 7 P0 入 open_questions.md（Q-501~Q-507），**报告本身归档到** `governance/design_iter/archive/audit_2026-06-15_RULE_SKILL.md`（**不开新版本号**——避免 governance 设计迭代被无谓打断）
 - **C. 备选**：保留 v1 决策（governance/audits/）——**违反 AGENTS.md + §0.1 铁律，强烈不推荐**

---

## 3. 为什么 v1 决策被否决

1. **没核对 governance README**——只查了"目录是否存在"，没读"README 声明的治理约定"
2. **没读 open_questions.md §v6.2 闭环**——错过了"审查发现 → Q-XXX 跟踪"成熟模式
3. **误把 governance 当成"无限层级"**——违反 §0.1 铁律"必须先询问再创建"
4. **导致的影响**（如果 v1 决策执行了）：
 - governance 出现 2 个并列子目录（design_iter + audits）——**未来再出现 S1-S8 冲突时**，是开"governance/audits/s1-2026-xx.md"还是"governance/design_iter/plans/v6/"？两个目录都能装，必然分裂
 - 7 P0 没进 open_questions.md——其他 Agent 看不到，无法跟踪
 - 报告没版本化——下次"再做一次审查"找不回去

---

## 4. AskQuestion 决策（用户拍板）

### 决策点 1：`sample_requirements.md`
（v1 不变）

### 决策点 2：`RELEASE_NOTES_v1.0_rerun.md`
- A. 推荐：mv 到 `workflow_assets/_refactor_backup/RELEASE_NOTES_v1.0_rerun_2026-06-15.md`（沿用 backup 约定，不新建业务目录）
- B. 删除（v1.0 已废）
- C. 保留 v1（移到「S8 自迭代」/v1.0/，新建业务目录）

### 决策点 3：`RULE_SKILL_CONSISTENCY_REVIEW.md`
- A. 推荐：走 design_iter 系统（v6 方案 + Q-501~Q-507 + open_questions.md 更新）
- B. 备选：不开新版本，Q-501~Q-507 进 open_questions.md，报告归档到 `governance/design_iter/archive/audit_2026-06-15_RULE_SKILL.md`
- C. 保留 v1（governance/audits/，违反 AGENTS.md + §0.1）

---

## 5. 落档协议执行记录

- 2026-07-08 v1 决策表（已 Write，但内容违背 AGENTS.md）
- 2026-07-08 v2 重做（本文件）— 取代 v1
- 后续：本文件 v1 决策表需删除？留作"决策修订示范"？等用户拍板
