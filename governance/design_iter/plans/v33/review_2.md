# Review Round 2 — v33 Plan B 实施复盘

_时间_: 2026-07-21T10:12:00+08:00

## 缺陷汇总

### 一般缺陷

1. **parallel_executor 仍未接入 Act 阶段**
   `_run_goal_loop_pipeline` 的 Act 阶段是串行 for 循环（行 57-80），`GoalParallelExecutor` 从未被 import 或调用。Plan B 承诺的"DAG 并行执行"仍悬空。

## 根因定位

| 根因类型 | 描述 | 证据 |
|---|---|---|
| **实现时机约束** | Act 阶段并行执行需要 task_queue 中 task 含有 `parallelizable` + `depends_on` 字段；但 `_run_goal_loop_pipeline` 当前生成的 task_queue 每个 task 相互独立（`depends_on: []`），即使调用 parallel_executor 也无法产生并行分组 | `_run_goal_loop_pipeline` 行 60-68，task_queue 每个 stage 独立 |
| **并行化边界不清晰** | 阶段级并行（多 stage 并行）与阶段内并行（单个 stage 内的多 task 并行）是两个不同层次；当前 conversation_skills 设计的"阶段串行"是有意约束，不应在 run_pipeline 层引入跨 stage 并行 | aidocx-workflow-conversation SKILL.md §4：run_pipeline 是顺序编排器，不是并发执行器 |

## 修复方案

### 方案 C：阶段内并行（推荐）

> Act 阶段内部支持 parallel_executor，前提是 stage_callables 含有可并行的子任务。

当前 `_run_goal_loop_pipeline` 的 task_queue 是 stages 维度（每个 stage 一个 task），不满足 DAG 并行条件。

真正的并行机会在于：**单个 stage 内部**（例如 S5 多个 Story 可并行生成 TP）。但这需要 `stage_callable` 的设计支持（不是 run_pipeline 的职责）。

**建议**：在 `_run_goal_loop_pipeline` 的 Act 阶段中增加 parallel_executor 调用点（当 stage_callable 含 `parallelizable_tasks` 时），同时在 `run_pipeline` docstring 中明确标注"阶段内并行的前提条件"。

### 不修复声明（决策）

> parallel_executor 未在 Act 阶段调用不是 bug，是设计边界问题。

理由：
1. `aidocx-workflow-conversation SKILL.md §4` 明确：`run_pipeline` 是**顺序编排器**，不是并发执行器
2. Act 阶段的真正并行应在单个 stage_callable 内部实现，不在 run_pipeline 层
3. `goal_parallel_executor.py` 是**预留能力**，当有具体多子任务场景时可被 stage_callable 调用

**决策**：本轮不强制接入 parallel_executor；在 `_run_goal_loop_pipeline` 的 Act 阶段增加一行注释说明调用前提。

---

## 本轮变更记录

| 改动 | 文件 | 验证 |
|---|---|---|
| `_run_goal_loop_pipeline` 函数新增 | `conversation_skills.py` 行 17-165 | smoke test T4 PASS |
| `run_pipeline` 新增 goal/accept_criteria/token_limit/max_rounds 参数 | `conversation_skills.py` 行 296-309 | smoke test T1 PASS |
| `hooks.json` afterShellExecution 替换为 breakloop hook | `hooks.json` | JSON 验证 OK |
| `hooks.json` afterFileEdit 补充 breakloop hook 注册 | `hooks.json` | JSON 验证 OK |
