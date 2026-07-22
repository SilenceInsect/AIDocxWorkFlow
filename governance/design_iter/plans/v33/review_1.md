# Review Round 1 — aidocx-workflow-conversation §10 审查

_时间_: 2026-07-21T10:05:00+08:00

## 缺陷汇总

### 严重缺陷

1. **§10.1 run_pipeline(goal=...) 描述与实现脱节**
   `aidocx-workflow-conversation/SKILL.md` §10.1 声称"`run_pipeline()` 接收 goal 参数时进入自治循环模式"，但 `conversation_skills.py` 的 `run_pipeline()` 函数签名（行 135）无 `goal` 参数，无 `value_criteria`，无 `GoalLoop` 集成。

### 一般缺陷

2. **hooks.json afterShellExecution 事件重复注册**
   `goal_loop_hook.py`（旧版，v1，141 行）和 `goal_loop_breakloop_hook.py`（新版，v3，682 行）同时在 `afterShellExecution` 事件中有功能，但 `hooks.json` 只注册了旧版，未注册新版的双门判定逻辑。

3. **goal_loop_breakloop_hook.py afterFileEdit 未在 hooks.json 注册**
   `goal_loop_breakloop_hook.py` 的 `handle_after_file_edit()` 在 `HANDLERS` 字典中（行 411），但 `hooks.json` 的 `afterFileEdit` 数组（行 39-59）未注册它。

4. **parallel_executor 悬空**
   `goal_parallel_executor.py` 有完整实现（568 行，8 self-test cases），但 `conversation_skills.py` 从未 import 也从未调用。

## 根因定位

### 机制问题

| 根因 | 证据 |
|---|---|
| **SKILL.md 先行，实现滞后** | §10 在 skill 中写了参数契约和五段式映射，但实现层（conversation_skills.py）从未跟进补充 | 
| **hook 版本迭代未同步到 hooks.json** | `goal_loop_hook.py`（v1）和 `goal_loop_breakloop_hook.py`（v3）共存于 codebase，但 hooks.json 只注册了 v1，未更新为 v3 |
| **并行执行能力未接入编排层** | parallel_executor 做了 DAG 解析但 Act 阶段从未调用，Act 阶段仍是串行执行 | 

### 规范问题

| 根因 | 证据 |
|---|---|
| **skill 描述与实现未对齐** | §10 说"当 run_pipeline() 接收到 goal 参数时进入自治循环"，实际代码无此参数 | 
| **hook 事件处理分散** | sessionStart、afterFileEdit、afterShellExecution、afterAgentResponse 四个事件分散在 5 个 hook 文件中，没有统一的 goal-loop 事件总线 | 

### 习惯问题

| 根因 | 证据 |
|---|---|
| **skill 写了实现方案，但没有人将它转化为代码任务** | §10 的五段式映射写得很详细，但没有转化为具体的代码实现 ticket | 

## 修复方案

### 方案 A：轻量化修复（推荐，立即可执行）

> **目标**：在不影响现有 stage_callable 接口的前提下，补充 §10 缺失的集成链路

| 行动 | 文件 | 下一步 |
|---|---|---|
| 在 `run_pipeline()` 添加 `goal` 参数（向后兼容：无 goal 时走原逻辑；有 goal 时调用 GoalLoop 状态机） | `conversation_skills.py` | 需用户确认是否实现 |
| 将 `hooks.json` afterShellExecution 中的 `goal_loop_hook.py` 替换为 `goal_loop_breakloop_hook.py` | `hooks.json` | 需用户确认 |
| 在 hooks.json afterFileEdit 数组中补充注册 `goal_loop_breakloop_hook.py` | `hooks.json` | 需用户确认 |

### 方案 B：全量修复（工程最稳）

> 在方案 A 基础上：
1. 完整实现 `run_pipeline(goal=...)` 的五段式驱动（调用 GoalLoop.plan/act/audit/review/iterate）
2. Act 阶段集成 `GoalParallelExecutor`，实现 DAG 并行执行
3. 统一所有事件到 `goal_loop_breakloop_hook.py`，废弃 `goal_loop_hook.py`
4. 集成 `GOAL_BUSINESS_AUDIT.mdc` 5 条规则到 audit 阶段

---

## 轻量修复具体代码

### 修复 1：`conversation_skills.py` 添加 goal 参数

```python
def run_pipeline(
    stages: list[str],
    req_name: str = "游戏道具商城系统",
    version: str = "v1.0",
    project_name: str | None = None,
    *,
    stage_callables: dict[str, Any] | None = None,
    stop_on_failure: bool = True,
    # ── §10.1 goal-loop 驱动模式新增参数 ──
    goal: str | None = None,
    accept_criteria: list[str] | None = None,
    token_limit: int = 200_000,
    max_rounds: int = 5,
) -> dict:
    # 如果传了 goal，进入自治循环
    if goal is not None:
        return _run_goal_loop_pipeline(
            stages, req_name, version, project_name,
            stage_callables, stop_on_failure,
            goal, accept_criteria, token_limit, max_rounds,
        )
    # 否则走原逻辑（向后兼容）
    return _run_pipeline_original(...)


def _run_goal_loop_pipeline(...) -> dict:
    """§10 goal-loop 驱动模式实现。"""
    # 1. Plan：创建快照 + 生成 task_queue（映射到 stages）
    # 2. Act：调用 run_stage() 执行各阶段
    # 3. Audit：逐条对照 accept_criteria 判定
    # 4. Review：汇总缺陷 + 根因 + 修复方案
    # 5. Iterate：收敛判定
    ...
```

### 修复 2：`hooks.json` 更新 afterShellExecution

```json
"afterShellExecution": [
  {
    "command": ".cursor/hooks/goal_loop_breakloop_hook.py",
    "type": "command",
    "timeout": 10
  }
]
```

### 修复 3：hooks.json afterFileEdit 补充 breakloop

```json
"afterFileEdit": [
  ...
  {
    "command": ".cursor/hooks/goal_loop_breakloop_hook.py",
    "type": "command",
    "timeout": 10
  }
]
```
