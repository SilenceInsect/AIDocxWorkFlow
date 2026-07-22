# Round 1 Review — v3.02 跟进清单前置复盘

## 1. 缺陷汇总（去重 / 按严重度排序）

### BLOCKER（必须修复）
- **DT-v302-001** — v3.02 Goal 与 v3.01 现状错位（task_queue 5 项中 T-001/T-002/T-003 修不存在的 bug）

### MAJOR
- **SYS-008**（新增）— 任务队列固化前未做现状 Read（DNA §9.4 在 Plan 阶段被绕过）

---

## 2. 根因定位

### 机制问题
- **Plan 阶段缺乏强制现场校验**——SKILL.md §3.1 Plan 阶段只要求"解析顶层目标 → 拆解 task_queue"，**未要求 Read 现状数据 + 验证 v 项描述与现状匹配**。这是 v1.1 SKILL 的规范漏洞。
- **task_queue 5 项基于描述草稿固化**——用户提供的 v3.02 Goal 文本 = 8 项问题清单，LLM 在 Plan 阶段未 Read v3.01 数据即拆解为 5 子任务，导致 3 子任务基于"未存在的事实"

### 规范问题
- **GL-009 语义校验未在 Plan 阶段触发**——SKILL.md §3.2 说"每轮执行前校验语义相似度"，但 R=0 Plan 阶段跳过此校验
- **audit_1 应在 Plan 之后 / Act 之前写**——本轮 audit_1 实际是"Plan 校验"角色（不是标准五段式的 Audit）

### 习惯问题
- **依赖用户描述作为事实来源**——v3.02 草稿是"用户记忆"，不是"现场数据"；应做事实校验

---

## 3. 可落地修复方案

### 立即修复（Round 2 / 等用户决策）
1. **A 方案（推荐）**：v3.02 立即 `converged_with_followup`
   - V-002 唯一 FAIL → 转 follow_up_items + 启动 v3.03
   - 撤销 T-001/T-002/T-003（修不存在 bug = 浪费）
   - 保留 T-004（OBJ 风险矩阵）+ T-005（验证重导）
2. **B 方案**：重写 task_queue 仅修 V-002，保留本 Goal ID，3-4 轮收敛
3. **C 方案（不推荐）**：强修 V-001/V-003/V-004，伪造工作量

### 规范沉淀（SKILL 漏洞修复建议）
- **SYS-008 → v22+ SKILL 迭代**：Plan 阶段新增强制步骤"现场 Read 状态校验"——v N 项描述与 v N 数据交叉验证后才允许进入 Act
- **新增 audit_0.md**（Plan 验证报告）作为 R=0 阶段产物，独立于五段式 audit_<round>.md

---

## 4. 修复优先级

| # | 动作 | 优先级 |
|---|---|---|
| 1 | 用户拍板 DT-v302-001 候选 A/B/C | BLOCKER |
| 2 | 按选择更新 snapshot.task_queue + value_criteria | BLOCKER |
| 3 | 写 CONVERGED 或 REPAIRING | BLOCKER |
| 4 | 记录反模式案例到 antipattern_cases.jsonl | MAJOR |
| 5 | SYS-008 提案入 systemic_issues.md | MAJOR |

---

## 5. 影响范围

- **直接影响**：v3.02 Goal 闭环时间（建议 A 方案 1 轮 / B 方案 3-4 轮 / C 方案 5+ 轮）
- **间接影响**：v3.03 跟进（修 V-002 唯一 BLOCKER）
- **规范影响**：v22+ SKILL 迭代建议（Plan 阶段强制 Read-before-Plan）
