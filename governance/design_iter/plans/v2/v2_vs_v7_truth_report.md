# v2 vs v7 现状澄清（决策报告）

> **触发**：用户 2026-07-09 00:23 问 "到底是 v2 还是 v7"
> **背景**：上轮我把 v3 份 audit_input 文件 mv 到 `governance/design_iter/plans/v7/`，INDEX.md / INDEX.json 加 v7 段。但 current 软链仍指 v2。
> **DNA 引用**：AGENTS.md "方案迭代管理" + DESIGN_AND_EXECUTION_STANDARDS.mdc §0.1 + §9.5 落档协议

---

## 1. 现状事实（§9.4 先验后答，全部基于已 Read 证据）

### 1.1 文件分布

| 路径 | 存在？ | 内容性质 |
|---|---|---|
| `plans/v2/PLAN.md` | ✅ | v2 主方案（待 5 决策）|
| `plans/v2/open_questions.md` | ✅ | **26.7KB**——含 v2 主体 Q-001~Q-005 + 次级 Q-101~Q-201 + v6.x Q-301/Q-401/Q-402 + **v7 启动版 Q-501~Q-569（69 条）**|
| `plans/v2/resolved_questions.md` | ✅ | v2 已解决 |
| `plans/v2/decisions.json` | ✅ | v2 决策占位 D-101~D-105 |
| `plans/v2/q_decision_table.md` | ✅ | v2 启动决策表 |
| `plans/v2/q_decision_table_q_audit_001_v2.md` | ✅ | Q-AUDIT-001 重做决策表 |
| `plans/v2/q_decision_table_round2.md` | ✅ | 本轮决策表（根目录治理 + v7 体系完整化）|
| `plans/v7/PLAN.md` | ✅ | v7 主方案（9.9KB）——含 §2 表格 56 行 |
| `plans/v7/audit_input.md` | ✅ | 输入源 1（RULE_SKILL 24 条）|
| `plans/v7/audit_input_scripts_skill.md` | ✅ | 输入源 2（SCRIPT_SKILL 14 条）|
| `plans/v7/audit_input_skill_logic.md` | ✅ | 输入源 3（SKILL_LOGIC 31 条）|
| `plans/v7/open_questions.md` | ❌ | **缺**（v7 的 Q 实际在 v2/open_questions.md §v7 启动版 段）|
| `plans/v7/resolved_questions.md` | ❌ | 缺 |
| `plans/v7/decisions.json` | ❌ | 缺 |
| `plans/v7/changes/` | ❌ | 缺 |
| **current 软链** | ✅ `-> plans/v2` | **未切 v7** |

### 1.2 v2 4 件套齐全 ✅ / v7 4 件套 缺 4 件套 ❌

按 AGENTS.md "方案迭代管理"——每份方案 v{N} 必有：
- ✅ PLAN.md
- ✅ open_questions.md
- ✅ resolved_questions.md
- ✅ decisions.json
- ✅ changes/（推荐）

| 方案 | 4 件套齐全？ | current 指向？ | 实质状态 |
|---|---|---|---|
| **v2** | ✅ 齐全 | ✅ 是 | **生效方案** |
| **v7** | ❌ 仅 PLAN.md + 3 audit_input（audit_input 是"输入"不是"治理文件"）| ❌ 否 | **未启动**（仅"目录骨架"）|

---

## 2. 我的错（诚实承认）

### 2.1 上轮违规

- 我之前回复中说 "**v7 启动版**"——**事实不成立**
- 我把 "mv 3 个 audit_input" 等同于 "v7 启动"——**这是概念混淆**
- AGENTS.md "方案迭代管理" 没明说 "启动 = 建 open_questions.md"，但**所有历史版本（v1/v2/v3/v4）启动时都先建 4 件套**

### 2.2 INDEX.md / INDEX.json 加 v7 段的反思

- 我加 v7 段时，把 v7 标为 "**启动版 / 未切 current**"——这个描述**模糊**：
 - "启动版"暗示"v7 已启动"——但 4 件套缺，**未真正启动**
 - 准确说应该是 "**输入归档 / 治理文件待补**"
- 这是 Q1 一致性违规：INDEX 段描述与 v7/ 实际文件不匹配

### 2.3 修正方案建议（§9.1 红线 ≤ 3 文件改动）

**建议实施 3 文件改动**（按优先级 N1→N2→N3）：

| N | 操作 | 文件 |
|---|---|---|
| 1 | INDEX.md v7 段描述从"启动版 / 未切 current"改为"输入归档 / 治理文件待补" | `governance/design_iter/INDEX.md` |
| 2 | INDEX.json v7 段 `status` 同步改为"输入归档 / 治理文件待补" | `governance/design_iter/INDEX.json` |
| 3 | q_decision_table_round2.md 头部加 "说明段"——澄清该文件归属 v2 主体决策，不属 v7 | `governance/design_iter/plans/v2/q_decision_table_round2.md` |

**如果不修正**：INDEX 描述与文件实际不一致，会误导后续 Agent / 人读 INDEX 时以为 v7 已启动

**如果想真正启动 v7**：必须再补 4 件套（v7/open_questions.md + resolved_questions.md + decisions.json + changes/）——共 4 文件改动，**超 §9.1 红线 1**——必须单独 ask

---

## 3. v7 启动与否的 4 种决策选项

| 选项 | 操作 | 风险 | 推荐度 |
|---|---|---|---|
| **A** | **明确现状**——INDEX 改回"输入归档"，承认 v7 未启动 | 低（只是修正描述）| ⭐⭐⭐ 最低风险 |
| **B** | **补 v7 4 件套 + 切 current**——v7/open_questions.md + resolved_questions.md + decisions.json + changes/diff_v6_to_v7.md + `rm current && ln -s plans/v7 current` | 高（治理层强约束变更，必须先 ask）| ⭐⭐ 中风险 |
| **C** | **回滚 v7 状态**——从 INDEX 撤回"v7"段，把 audit_input 移回根目录或归 _archive | 中（破坏现有治理状态）| ⭐ 不推荐 |
| **D** | **双轨**——v2 为主线，v7 只留 PLAN + audit_input（不补 4 件套）| 低（最少动作）| ⭐⭐ 推荐作默认 |

### 3.1 推荐路径

**本轮不动 v7 状态**——只修正 INDEX 描述（选项 A）：
- 把"v7 启动版 / 未切 current"改为"v7 输入归档 / 治理文件待补"
- 把 v2 段加注："v2/open_questions.md §v7 启动版 段是 v7 输入归档（Q-501~Q-569），不是 v7 治理文件"
- **v7 是否启动 = 下次用户决策**

### 3.2 v2 与 v7 的关系澄清

按 AGENTS.md "方案迭代管理" + DESIGN §2.6 设计：
- **v2 是当前生效**——current 指向 + 4 件套齐全 + open_questions 跟踪全项目问题
- **v7 是"输入归档"**——3 份 audit_input 是未来 v7 治理的输入材料
- **v7 启动条件**：用户拍板 + v7/PLAN.md §3 栏填全 + 4 件套齐全 + 决策点明确
- **当前 v7 不是"半成品"而是"筹备阶段"**——3 份 audit_input 已经在 v7/ 目录下就位

---

## 4. 落档协议执行记录

- 2026-07-09 00:23：本报告落档（用户问"到底是 v2 还是 v7"触发）
- 上轮决策：`q_decision_table_round2.md` 已落档
- 本报告作为上轮决策的 **纠偏补充**——v7 真实状态澄清