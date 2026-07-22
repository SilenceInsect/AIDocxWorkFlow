# v33 CONVERGED — aidocx-workflow-conversation 加速方案审查报告

> **目标**：审查 aidocx-workflow-conversation SKILL.md §10 的实现状态，给出加速方案
> **执行时间**：2026-07-21
> **loop_round**：1

---

## 1. 状态

**snapshot 实际 status**: `active`（有 FAIL verdicts，iterate 判为继续，非 achieved）
**snapshot loop_round**: 1
**snapshot token_used**: 5000

> **注意**：本轮 audit 发现 3 个 FAIL verdicts（AC2/AC3/AC4），goal-loop 判为 `active` 继续下一轮，而非 `achieved`。
> CONVERGED.md 标题不改（保持可搜索性），但 §1 内容反映真实状态。

---

## 2. 完成内容

### 2.1 §10 描述层审查

`aidocx-workflow-conversation/SKILL.md` §10 完整定义了 goal-loop 驱动模式的：
- 触发条件（`goal` 参数传入 `run_pipeline()`）
- 参数契约（`goal` / `accept_criteria` / `token_limit` / `max_rounds`）
- 五段式映射（Plan→Act→Audit→Review→Iterate）
- 快照持久化规范（10 字段 Schema）
- 三层熔断（轮次 / Token / 用户输入）
- 事件驱动续跑（4 事件映射）

### 2.2 实现层审查（证据化）

| 模块 | §10 引用 | 实际代码 | 断点 |
|---|---|---|---|
| `conversation_skills.py` | §10.1 `run_pipeline(goal=...)` | 无 `goal` 参数；无 `value_criteria`；无 `GoalLoop` 调用 | **MAJOR 断点** |
| `goal_snapshot.py` | §10.4 | 20 字段 Schema；atomic write；fcntl 锁 | ✅ 完全实现 |
| `goal_loop_runner.py` | §10.3 五段式 | 五段状态机；熔断；AuditVerdict；ReviewReport | ✅ 完全实现 |
| `goal_parallel_executor.py` | §10 Act 并行 | DAG 解析；并行分组；并行执行 stub | ⚠️ 已实现但未被调用 |
| `hooks.json` | §8 `sessionStart` | 5 个 sessionStart hooks（含 goal_loop_skill_md_integrity） | ✅ 已注册 |
| `hooks.json` | §8 `afterShellExecution` | 只注册旧版 `goal_loop_hook.py` | ⚠️ 旧版非 breakloop |
| `hooks.json` | §8 `afterAgentResponse` | 注册 `goal_loop_breakloop_hook.py` | ✅ 正确 |
| `hooks.json` | §8 `afterFileEdit` | 未注册 breakloop 的 afterFileEdit | ❌ 断点 |
| `goal_loop_breakloop_hook.py` | §10.2 双门判定 | 门 A + 门 B 完整实现；7 self-test cases | ✅ 完整实现 |
| `GOAL_BUSINESS_AUDIT.mdc` | §7 业务审计 | 5 条规则 + 审计触发时机 | ✅ 完整 |

### 2.3 加速方案（核心交付物）

**方案 A：轻量化方案（推荐，收敛最快）**
> 目标：在不修改 `conversation_skills.py` 架构的前提下，补充 §10 缺失的集成链路

| 行动 | 涉及文件 | 影响范围 |
|---|---|---|
| 补充 `conversation_skills.py` 的 `run_pipeline()` 添加 `goal` 参数（调用 GoalLoop 状态机） | `conversation_skills.py` | 中 |
| 在 hooks.json 中为 `afterShellExecution` 补充注册 `goal_loop_breakloop_hook.py`（替换旧版 `goal_loop_hook.py`） | `hooks.json` | 小 |
| 在 Act 阶段注释说明 `GoalParallelExecutor` 可被调用（预留接口） | `conversation_skills.py` | 小 |

**方案 B：全量方案（工程最稳，但工作量更大）**
> 在方案 A 基础上：
- `run_pipeline(goal=...)` 完整实现五段式驱动
- `GoalLoop.plan()` 在首轮自动读取 backlog 并生成 task_queue
- `GoalLoop.act()` 由 Agent 通过 Task 工具调用 subagent 实现并行
- `GoalLoop.audit()` 集成 GOAL_BUSINESS_AUDIT.mdc 规则
- `GoalLoop.review()` + `GoalLoop.iterate()` 自动收敛判定
- `hooks.json` 统一为 breakloop hook 处理所有事件
- `goal_parallel_executor.py` 在 Act 阶段真正被调用

---

## 3. 验收证据

| 验收项 | 证据 | 判定 |
|---|---|---|
| AC1 §10 描述层完整 | `aidocx-workflow-conversation/SKILL.md` §10 行 236-329 | ✅ |
| AC2 §10.1 run_pipeline(goal=...) 实际未实现 | `conversation_skills.py` 行 135-186（run_pipeline 无 goal 参数） | ⚠️ 断点 |
| AC3 GoalLoop runner 未在 conversation_skills 中调用 | `conversation_skills.py` 全文件 grep goal/GoalLoop = 2 处（仅字符串字面量） | ⚠️ 断点 |
| AC4 hooks.json 事件映射 | `hooks.json` 行 109-127 | ⚠️ 2 处问题 |
| AC5 parallel_executor 存在但未调用 | `goal_parallel_executor.py` 568 行实现；conversation_skills.py 未 import | ⚠️ 悬空 |
| AC6 加速方案已落档 | 本文件 + governance/design_iter/plans/v33/ | ✅ |

---

## 4. 自迭代记录

| 轮次 | 变更 | 理由 |
|---|---|---|
| Round 1 | 审查 §10 描述层与实际实现的断点；产出加速方案 A/B | 目标本质是"给出方案"，不等同"实现方案" |

---

## 5. 剩余问题

| 问题 | 严重度 | 解除条件 |
|---|---|---|
| §10.1 run_pipeline(goal=...) 未实现 | MAJOR | 补充 goal 参数 + 集成 GoalLoop |
| §10.3 五段式未集成 | MAJOR | 在 run_pipeline 中调用 GoalLoop.plan/act/audit/review/iterate |
| hooks.json afterShellExecution 重复注册 | MINOR | 替换旧版 hook 为 breakloop 版本 |
| parallel_executor 悬空 | MINOR | 在 Act 阶段调用或显式标注为"预留接口" |

---

## 6. 影响范围

- **影响 `conversation_skills.py`**：需补充 `goal` 参数处理逻辑（方案 A 轻量 / 方案 B 全量）
- **影响 `hooks.json`**：替换旧版 `goal_loop_hook.py` 为 `goal_loop_breakloop_hook.py`
- **不影响**：`goal_snapshot.py`（Schema 稳定）、`goal_loop_runner.py`（状态机完整）、`GOAL_BUSINESS_AUDIT.mdc`（规则完整）
- **预期收益**：实现 §10 承诺的"goal 参数驱动五段式自治循环"，减少人工干预
