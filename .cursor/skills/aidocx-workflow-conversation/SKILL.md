---
name: aidocx-workflow-conversation
description: >
  AIDocxWorkFlow 对话编排入口。使用 run_stage() / run_pipeline() 串联阶段 gate、阶段执行与产物校验。
  Use when the user wants the conversation layer to orchestrate the workflow through the runtime contract instead of manual per-stage narration.
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: workflow-conversation
  spec_version: agentskills.io/1.0
  cursor_compat: true
  cursor_mode_hint: multi_task
---

# AIDocxWorkFlow 编排契约

本 skill 不再承担"完整手工操作指南"职责。
它只定义一件事：对话层如何通过 `run_stage()` / `run_pipeline()` 驱动运行时编排。

## 1. 目标

- 统一单阶段与多阶段入口，避免脚本绕过 gate / ledger / review 资产。
- 让“人看到的入口说明”和“代码实际编排路径”保持一致。
- 把旧式“分阶段手工说明”降级为历史兼容背景，而不是当前推荐入口。

## 2. 唯一推荐入口

```python
from ai_workflow.conversation_skills import run_stage, run_pipeline
```

### 单阶段

```python
result = run_stage("S6", req_name="游戏道具商城系统", project_name="<project_name>", version="v3.01")
print(result["status"])
```

### 多阶段

```python
pipeline = run_pipeline(
    ["S5", "S6", "S7"],
    req_name="游戏道具商城系统",
    project_name="<project_name>",
    version="v3.01",
)
for item in pipeline["stages"]:
    print(item["stage"], item["status"])
```

### 阶段开始前：旧产物清理询问（v8 实战决策）

`run_stage()` / `run_pipeline()` / `run_s1_pipeline()` 在执行每个阶段前会自动检测
**该阶段目录是否存在且非空**——若命中，会在 `preflight` 之前询问：

```
┌─ [AIDocxWorkFlow] 阶段开始前询问 ─────────────────────────────┐
│ 检测到阶段目录已存在且非空，是否删除旧产物后重新执行？       │
└──────────────────────────────────────────────────────────────┘
  阶段        ：S6
  需求        ：游戏道具商城系统
  版本        ：v3.01
  阶段目录    ：workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」
  现有文件数  ：7
  现有总大小  ：28.4 KB
  最近修改    ：2026-07-09T23:54:17
  文件清单    ：
    - test_cases.json
    - test_cases.md
    - ...

请选择：
  [Y] 删除旧产物，重新跑该阶段（推荐）
  [N] 保留旧产物，跳过该阶段（status=SKIPPED）
  [A] 中止整个流水线（abort）
```

**决策语义**：

| 用户输入 | 行为 | 返回 status |
|---|---|---|
| `Y` | `shutil.rmtree(stage_dir)` 删除整个阶段目录（含 raw + ledger），重新执行 | 阶段正常推进 |
| `N` / 空回车 | 保留旧产物，**跳过该阶段** | `SKIPPED` + `skip_reason=user_chose_keep_existing` |
| `A` | 中止整个流水线 | `SystemExit`（run_pipeline 抛出后停） |
| 非交互环境（无 TTY） | 默认 `auto_keep`（不阻塞 CI） | `SKIPPED` + `skip_reason=non_interactive_env_default_keep` |

**作用域**：

- `run_stage("S6", ...)` → 仅 S6 询问
- `run_pipeline(["S5","S6","S7"], ...)` → 每个阶段独立询问（不会批量问）
- `run_s1_pipeline(...)` → S1 子模块入口同样询问（覆盖直接调用场景）

**删除范围**：

- `shutil.rmtree` 整个阶段目录（含 `raw/`、`*.json`、`*.md`、`*.xlsx`、`coverage_ledger.json`、`omission_ledger.json`、`preflight_gate.json`、`postflight_gate.json` 等所有产物）
- **不删** `resource/<req_name>/<version>_raw.docx`（gitignore 区，原始输入材料）

**为什么是固定行为（不再每次口头约定）**：

- v8 实战（2026-07-10）用户明确要求固化——避免每次跑 v3.01 都口头"先问一下"
- 防止 stage_callable 覆盖写入时与旧 `coverage_ledger.json` / `omission_ledger.json` 串味
- 人本可审查准则：删除前必须让用户看见具体文件清单

## 3. 编排顺序

`run_stage()` 的固定顺序是：

1. `run_stage_preflight(stage, req_name, version, project_name)`
2. 执行 `stage_callable`（如有）
3. `run_stage_postflight(stage, req_name, version, project_name)`

阶段若未生成以下运行时资产，不算完成：

- `stage_context.json`
- `stage_context.md`
- `read_ack.json`
- 对应阶段的 `postflight_gate.json`

S5 / S6 还必须补齐：

- `coverage_ledger.json`
- `omission_ledger.json`

S7 还必须补齐：

- `review_snapshot.json`
- `review_snapshot.md`
- `review_report.json`
- `review_report.md`

## 4. run_pipeline 契约

`run_pipeline()` 是顺序编排器，不是并发执行器。

默认行为：

- 按传入顺序依次执行阶段
- 默认 `stop_on_failure=True`
- 任一阶段状态不是 `PASS`，后续阶段标记为 `SKIPPED`
- 返回 `halted=true` 和 `halt_reason`

返回结构的关键字段：

```json
{
  "req_name": "xxx",
  "project_name": "<project_name>",
  "version": "v1.0",
  "stop_on_failure": true,
  "halted": false,
  "halt_reason": null,
  "stages": [
    {
      "stage": "S5",
      "status": "PASS",
      "preflight": {},
      "stage_result": {},
      "postflight": {},
      "runtime_gate": {}
    }
  ]
}
```

## 5. 阶段状态枚举

- `PASS`：preflight / runtime gate / postflight 全部通过
- `FAIL_PRECHECK`：输入或前置资产不满足
- `FAIL_RUNTIME_GATE`：runtime consistency gate 阻断
- `FAIL_POSTCHECK`：阶段产物未闭合
- `NEED_LLM_OUTPUT`：preflight 已过，但未提供 `stage_callable`
- `SKIPPED`：由于上游阶段失败被跳过

## 6. 推荐阶段 callable

当前实现层已经可直接复用的 callable：

- S5：`save_stage5_output(...)`
- S6：`format_test_cases(...)`
- S7：`save_stage7_output(...)`

示例：

```python
from ai_workflow.conversation_skills import run_pipeline, save_stage5_output, save_stage7_output
from ai_workflow.test_case_formatter import format_test_cases

pipeline = run_pipeline(
    ["S5", "S6", "S7"],
    req_name="游戏道具商城系统",
    project_name="<project_name>",
    version="v3.01",
    stage_callables={
        "S5": lambda: save_stage5_output("游戏道具商城系统", test_points_payload, version="v3.01", project_name="<project_name>"),
        "S6": lambda: format_test_cases(test_cases_payload, backlog_payload, test_points_payload, req_name="游戏道具商城系统", version="v3.01", project_name="<project_name>"),
        "S7": lambda: save_stage7_output("游戏道具商城系统", version="v3.01", project_name="<project_name>"),
    },
)
```

## 7. 旧入口地位

以下函数仍保留，但不代表当前编排主入口：

- `execute_simple_flow()`
- `execute_full_flow()`

它们可用于兼容旧调用方或状态查询，但不应替代 `run_stage()` / `run_pipeline()`。

## 8. 约束边界

本 skill 只描述编排契约，不重复各阶段内容规范。

阶段内容生成、字段要求、必读材料、质量门禁，仍以以下文件为准：

- `AGENTS.md`
- `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`
- `.cursor/rules/STAGE_S*.mdc`
- `.cursor/skills/aidocx-s*/SKILL.md`

## 9. 何时使用

在以下场景应优先使用本 skill：

- 需要把多个阶段按运行时 gate 串起来执行
- 需要把端到端回归绑定到真实运行时资产
- 需要判断某一阶段失败后，下游是否应停止
- 需要让对话层入口与实现层编排保持同一套语义

---

## 10. goal-loop 驱动模式

> **来源**：goal-loop/SKILL.md 五段式自治闭环能力集成
> **目的**：使 `run_pipeline()` 支持 goal-loop 自治循环，在保留向后兼容的前提下实现 Plan→Act→Audit→Review→Iterate 五段式闭环

### 10.1 触发条件

当 `run_pipeline()` 接收到 `goal` 参数时，进入自治循环模式：

```python
pipeline = run_pipeline(
    ["S5", "S6", "S7"],
    req_name="游戏道具商城系统",
    project_name="<project_name>",
    version="v3.01",
    goal="完整生成游戏道具商城系统的测试用例，验收标准：S5 产出 test_points.json、S6 产出 test_cases.json、S7 审查通过",
    accept_criteria=[
        "S5 目录存在且含 test_points.json",
        "S6 目录存在且含 test_cases.json",
        "S7 审查覆盖率 ≥ 90%",
    ],
    token_limit=200_000,
    max_rounds=5,
)
```

### 10.2 参数契约

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `goal` | `str \| None` | `None` | 用户目标描述；有值时进入 goal-loop 模式 |
| `accept_criteria` | `list[str] \| None` | `None` | 可量化验收断言清单（≥ 1 条） |
| `token_limit` | `int` | `200_000` | Token 预算上限 |
| `max_rounds` | `int` | `5` | 最大迭代轮次 |
| `severity_label` | `str` | `"MAJOR"` | BLOCKER / MAJOR / MINOR |
| `process_criteria` | `list[str] \| None` | `None` | 内部过程类验收（可选） |

### 10.3 五段式集成映射

| goal-loop 阶段 | aidocx-workflow-conversation 映射 |
|---|---|
| **Plan** | 解析 `goal` → 拆分 `task_queue`（每 task 含 `id`/`title`/`status`/`artifact`）→ 映射到 `stages` 列表 |
| **Act** | 调用 `run_pipeline(stages, ...)` 执行阶段流水线；每次 Act 写入 `latest_artifact` |
| **Audit** | 每阶段完成后：读产物 + 对照 `accept_criteria` 逐条判定 `PASS` / `FAIL` / `UNKNOWN` |
| **Review** | 汇总本轮所有 `FAIL` → 缺陷分类（严重/一般/优化）+ 根因定位 + 修复方案 |
| **Iterate** | 全部 `PASS` → `status=achieved`；存在 `FAIL` 且未超限 → `loop_round+=1`，继续 Act；达到上限 → `status=budget-limited` |

**禁止跳轮条款**：每轮必须产出 `audit_<round>.md` + `review_<round>.md`，不得以"无新交付物"为由跳过 audit。

### 10.4 快照持久化

快照 20 字段定义见 `goal-loop/SKILL.md` §2，持久化路径：`.goal-log-db/active/<goal_id>/snapshot.json`。

| 操作 | 函数 |
|---|---|
| 创建快照 | `goal_snapshot.create_snapshot()` |
| 更新快照 | `goal_snapshot.update_snapshot()` |
| 读取快照 | `goal_snapshot.load_snapshot()` |
| 列出活跃目标 | `goal_snapshot.list_active_goals()` |
| 追加遗留项 | `goal_snapshot.add_follow_up_item()` |
| 更新效能统计 | `goal_snapshot.update_efficiency_stats()` |
| 签名漂移检测 | `goal_snapshot.compute_similarity()` |

### 10.5 三层熔断

| 熔断层 | 默认阈值 | 触发动作 |
|---|---|---|
| 最大迭代轮次 | `max_rounds=5`（`loop_round >= 5`） | `status=budget-limited`，暂停循环 |
| Token 预算 | `token_limit=200_000`（`token_budget.used >= limit`） | 同上 |
| 用户输入阻断 | 检测到未读用户消息 | `status=paused`，等待人工指令 |

### 10.6 事件驱动续跑

| 事件 | 触发器 | 动作 |
|---|---|---|
| `sessionStart` | Cursor 窗口重载 / 会话刷新 | 读快照 → 注入 system_reminder 提示继续 Act |
| `afterFileEdit` | Agent 写文件完成 | 触发 Audit（对比 `snapshot.latest_artifact` vs `accept_criteria`） |
| `afterAgentResponse` | Agent 每次响应结束 | 破环机制双门判定（见 `goal-loop/SKILL.md` §10） |

### 10.7 向后兼容保证

- `goal=None`（默认）时：完全走原有顺序编排逻辑，不创建快照，不进入五段式循环
- `run_stage()` 不受影响
- `execute_simple_flow()` / `execute_full_flow()` 不受影响
- 已有的 `stage_callables` 参数继续有效

### 10.8 与 goal-loop/SKILL.md 的关系

本 skill 是 goal-loop 能力在 AIDocxWorkFlow 流水线场景的**应用层集成**：

- **上游能力源**：`goal-loop/SKILL.md` 定义五段式闭环 + 快照 20 字段 + 三层熔断 + 事件驱动
- **本 skill 职责**：将 goal-loop 能力映射到 `run_pipeline()` 的 stages 流水线
- **不修改上游**：goal-loop/SKILL.md 独立维护，作为通用自治循环规范

**引用约束**：本 skill 引用 goal-loop/SKILL.md 的内容时，以 goal-loop/SKILL.md 最新版本为准，不在本 skill 中重复定义。
