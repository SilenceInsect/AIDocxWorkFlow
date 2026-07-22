# 改造方案：用 goal-loop 能力改造 aidocx-workflow-conversation SKILL.md

> **任务来源**：Round 17 自迭代
> **落档路径**：`governance/design_iter/current/goal_workflow_conversation_transform.md`
> **执行日期**：2026-07-20

## 1. 改造目标

将 `aidocx-workflow-conversation/SKILL.md` 从"纯编排契约"升级为"自治循环可驱动"的编排技能。
核心：在保留向后兼容的前提下，使 `run_pipeline()` 支持 goal-loop 五段式自治闭环。

## 2. 源能力分析（goal-loop/SKILL.md）

### 2.1 五段式自治闭环（§3）

```
Plan (仅首轮 / 目标变更触发)
  ↓
Act (执行产出交付物)
  ↓
Audit (逐条证据化自检)
  ↓
Review (缺陷汇总 + 根因 + 修复方案)
  ↓
Iterate (PASS → achieved；FAIL → 轮次 +1；上限 → budget-limited)
  ↓ (FAIL)
回到 Act
```

### 2.2 Goal 快照 20 字段（§2，v1.2.1）

| 字段 | 类型 | 说明 |
|---|---|---|
| `goal_id` | string | UUIDv4 |
| `raw_user_goal` | string | 用户原始目标 |
| `value_criteria` | string[] | 外部价值类验收（v1.1） |
| `process_criteria` | string[] | 内部过程类验收（v1.1） |
| `value_ratio` | float | value_criteria 占比（0~1） |
| `severity_label` | enum | BLOCKER/MAJOR/MINOR |
| `follow_up_items` | object[] | 遗留项列表 |
| `goal_signature` | string | 目标语义哈希 |
| `goal_signature_changelog` | object[] | 签名变更历史 |
| `out_of_scope_md` | string | 禁区清单路径 |
| `audit_stability` | dict | 增量审计追踪 |
| `efficiency_stats` | dict | 效能统计 |
| `task_queue` | object[] | 子任务队列（含 parallelizable/depends_on） |
| `parallel_executor_hints` | dict | 并行化建议 |
| `loop_round` | int | 当前轮次（从 1 起） |
| `last_audit` | object/null | 上一轮审计 |
| `last_review` | object/null | 上一轮复盘 |
| `latest_artifact` | string/null | 最新交付物路径 |
| `status` | enum | active/achieved/converged_with_followup/paused/budget-limited |
| `token_budget` | object | {used, limit, updated_at} |

**持久化路径**：`.goal-log-db/active/<goal_id>/snapshot.json`

### 2.3 三层熔断（§4）

| 熔断层 | 默认阈值 | 触发动作 |
|---|---|---|
| 最大迭代轮次 | `loop_round >= 5` | `status = budget-limited`，暂停循环 |
| Token 预算 | `token_budget.used >= token_budget.limit` | 同上 |
| 用户输入阻断 | 检测到未读用户消息 | `status = paused`，等待人工指令 |

### 2.4 事件驱动自动续跑（§8）

| 事件 | 触发器 | 动作 |
|---|---|---|
| `sessionStart` | Cursor 窗口重载 / 会话刷新 | 读快照 → 注入 system_reminder 提示继续 Act |
| `afterFileEdit` | Agent 写文件完成 | 触发 Audit（对比 snapshot.latest_artifact vs accept_criteria） |
| `afterShellExecution` | Shell 命令完成 | 触发 Review（如命令返回非 0 或时间超阈值） |
| `beforeSubmitPrompt` | 用户提交 prompt | 检测未读消息 → 触发暂停熔断 |

### 2.5 破环机制（§10）

新增 `afterAgentResponse` 事件 + 双门判定：
- **门 A（字面）**：`response_text` 含 `CONVERGED` / `BLOCKED` / `REPAIRING→BLOCKED`
- **门 B（数据）**：`last_audit.verdicts` 中每个 `PASS` 都有非空 `reverse_challenge`

## 3. 集成点分析

### 3.1 run_pipeline 签名扩展

```python
# 现有签名（conversation_skills.py §134-185）
def run_pipeline(
    stages: list[str],
    req_name: str = "游戏道具商城系统",
    version: str = "v1.0",
    project_name: str | None = None,
    *,
    stage_callables: dict[str, Any] | None = None,
    stop_on_failure: bool = True,
) -> dict

# 扩展后签名（goal-loop 模式）
def run_pipeline(
    stages: list[str],
    req_name: str = "游戏道具商城系统",
    version: str = "v1.0",
    project_name: str | None = None,
    *,
    stage_callables: dict[str, Any] | None = None,
    stop_on_failure: bool = True,
    # ── goal-loop 新增参数 ──
    goal: str | None = None,           # 有值时进入自治循环
    accept_criteria: list[str] | None = None,  # 可量化验收断言
    token_limit: int = 200_000,        # Token 预算上限
    max_rounds: int = 5,               # 最大迭代轮次
    severity_label: str = "MAJOR",     # BLOCKER/MAJOR/MINOR
) -> dict
```

### 3.2 行为分支

| 参数组合 | 行为 |
|---|---|
| `goal=None` | **向后兼容**：原有顺序编排，调用现有 `run_pipeline()` 实现 |
| `goal="..."` | **goal-loop 模式**：五段式自治循环 |

### 3.3 五段式集成映射

| goal-loop 阶段 | aidocx-workflow-conversation 映射 |
|---|---|
| **Plan** | 解析 goal → 拆分 task_queue → 映射到 stages 列表 |
| **Act** | 调用 `run_pipeline(stages, ...)` 执行阶段流水线 |
| **Audit** | 每阶段完成后：读产物 + 对照 accept_criteria 逐条判定 PASS/FAIL/UNKNOWN |
| **Review** | 汇总本轮所有 FAIL → 缺陷分类 + 根因定位 + 修复方案 |
| **Iterate** | 全部 PASS → status=achieved；存在 FAIL → loop_round+=1，继续 Act；达到上限 → budget-limited |

### 3.4 快照持久化集成

| goal-loop 需求 | aidocx-workflow-conversation 实现 |
|---|---|
| 快照路径 | `.goal-log-db/active/<goal_id>/snapshot.json` |
| 快照写入 | `goal_snapshot.create_snapshot()` → `goal_snapshot.update_snapshot()` |
| 快照读取 | `goal_snapshot.load_snapshot()` |
| atomic write | 由 `goal_snapshot.py` 保证（flock + os.replace） |

### 3.5 事件驱动集成

| 事件 | aidocx-workflow-conversation 接入方式 |
|---|---|
| `sessionStart` | Cursor hooks 读 `.goal-log-db/index/session-index.jsonl` → 注入 system_reminder |
| `afterFileEdit` | 触发 audit，对比 `snapshot.latest_artifact` vs `accept_criteria` |
| `afterAgentResponse` | 破环机制（双门判定，见 goal-loop/SKILL.md §10） |

## 4. SKILL.md 新增章节设计

### 4.1 新增 §10 goal-loop 驱动模式

**章节结构**：

```
§10 goal-loop 驱动模式
  §10.1 触发条件
  §10.2 参数契约
  §10.3 五段式集成映射
  §10.4 快照持久化
  §10.5 三层熔断
  §10.6 事件驱动续跑
  §10.7 向后兼容保证
  §10.8 与 goal-loop/SKILL.md 的关系
```

**核心声明**：

当 `run_pipeline(..., goal="<目标描述>")` 时，进入 goal-loop 五段式自治循环：

1. **Plan**：解析 goal → 拆分 task_queue → 映射到 stages
2. **Act**：执行 `run_pipeline(stages, ...)` 阶段流水线
3. **Audit**：每阶段完成后触发 audit（读产物 + 逐条对照 accept_criteria）
4. **Review**：汇总本轮缺陷 + 根因 + 修复方案
5. **Iterate**：收敛判定 → 继续 / 终止 / 熔断

### 4.2 快照持久化

- 快照路径：`.goal-log-db/active/<goal_id>/snapshot.json`
- 快照 20 字段：见 goal-loop/SKILL.md §2
- 写入函数：`goal_snapshot.create_snapshot()` / `goal_snapshot.update_snapshot()`
- 读取函数：`goal_snapshot.load_snapshot()` / `goal_snapshot.list_active_goals()`

### 4.3 三层熔断

| 熔断层 | 默认阈值 | 触发动作 |
|---|---|---|
| 最大迭代轮次 | `max_rounds=5` | `status=budget-limited` |
| Token 预算 | `token_limit=200_000` | `status=budget-limited` |
| 用户输入阻断 | 检测未读消息 | `status=paused` |

### 4.4 向后兼容保证

- `goal=None` 时：完全走原有顺序编排逻辑
- `run_stage()` 不受影响
- `execute_simple_flow()` / `execute_full_flow()` 不受影响

## 5. 约束边界

| 约束 | 说明 |
|---|---|
| **不修改 goal-loop/SKILL.md** | 独立维护，作为上游能力源 |
| **不修改 conversation_skills.py** | 实现层改动由后续 act 阶段处理 |
| **只改 aidocx-workflow-conversation/SKILL.md** | 加新章节 §10 |
| **向后兼容** | 无 goal 参数时行为完全不变 |
| **文档自洽** | 不与 goal-loop/SKILL.md 冲突 |

## 6. 验收标准

- [ ] `aidocx-workflow-conversation/SKILL.md` 含新增 §10 goal-loop 驱动章节
- [ ] 向后兼容（无 goal 参数时行为不变）
- [ ] 落档文件存在：`governance/design_iter/current/goal_workflow_conversation_transform.md`
- [ ] 文档自洽（不与 goal-loop/SKILL.md 冲突）
- [ ] self-test 验证通过

## 7. 实现层待办（后续 act 阶段）

> 以下为实现层改动，不在本 SKILL.md 改造范围内，但记录于此以便后续跟进。

| 待办 | 说明 |
|---|---|
| P1 | `run_pipeline()` 增加 `goal` / `accept_criteria` / `token_limit` / `max_rounds` / `severity_label` 参数 |
| P1 | `run_pipeline()` 内部增加 goal-loop 五段式状态机 |
| P1 | `run_pipeline()` 调用 `goal_snapshot.create_snapshot()` 初始化快照 |
| P1 | `run_pipeline()` Act 阶段调用原有 `run_pipeline()` 实现（递归调用需防死循环） |
| P1 | `run_pipeline()` Audit 阶段实现逐条对照 accept_criteria |
| P1 | `run_pipeline()` Review 阶段汇总缺陷 + 根因 + 修复方案 |
| P1 | `run_pipeline()` Iterate 阶段实现收敛判定 |
| P2 | 三层熔断检查逻辑 |
| P2 | 事件驱动 hook 接入 |
| P3 | 破环机制双门判定 |

## 8. 落档协议执行记录

| 字段 | 值 |
|---|---|
| 执行日期 | 2026-07-20 |
| 执行人 | AI Agent |
| 落档文件 | `governance/design_iter/current/goal_workflow_conversation_transform.md` |
| 改造范围 | `aidocx-workflow-conversation/SKILL.md` 新增 §10 |
| 约束文件未改 | `goal-loop/SKILL.md`、`conversation_skills.py` |
| 状态 | 已落档，待实施 |

---

## 附录：§10 章节草稿

以下为待写入 `aidocx-workflow-conversation/SKILL.md` 的 §10 章节内容。

### §10 goal-loop 驱动模式

#### §10.1 触发条件

当用户提供 `goal` 参数时，`run_pipeline()` 进入自治循环模式：

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

#### §10.2 参数契约

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `goal` | `str \| None` | `None` | 用户目标描述；有值时进入 goal-loop 模式 |
| `accept_criteria` | `list[str] \| None` | `None` | 可量化验收断言清单（≥ 1 条） |
| `token_limit` | `int` | `200_000` | Token 预算上限 |
| `max_rounds` | `int` | `5` | 最大迭代轮次 |
| `severity_label` | `str` | `"MAJOR"` | BLOCKER / MAJOR / MINOR |
| `process_criteria` | `list[str] \| None` | `None` | 内部过程类验收（可选） |

#### §10.3 五段式集成映射

| goal-loop 阶段 | aidocx-workflow-conversation 映射 |
|---|---|
| **Plan** | 解析 `goal` → 拆分 `task_queue`（每 task 含 `id`/`title`/`status`/`artifact`）→ 映射到 `stages` 列表 |
| **Act** | 调用 `run_pipeline(stages, ...)` 执行阶段流水线；每次 Act 写入 `latest_artifact` |
| **Audit** | 每阶段完成后：读产物 + 对照 `accept_criteria` 逐条判定 `PASS` / `FAIL` / `UNKNOWN` |
| **Review** | 汇总本轮所有 `FAIL` → 缺陷分类（严重/一般/优化）+ 根因定位 + 修复方案 |
| **Iterate** | 全部 `PASS` → `status=achieved`；存在 `FAIL` 且未超限 → `loop_round+=1`，继续 Act；达到上限 → `status=budget-limited` |

**禁止跳轮条款**：每轮必须产出 `audit_<round>.md` + `review_<round>.md`，不得以"无新交付物"为由跳过 audit。

#### §10.4 快照持久化

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

#### §10.5 三层熔断

| 熔断层 | 默认阈值 | 触发动作 |
|---|---|---|
| 最大迭代轮次 | `max_rounds=5`（`loop_round >= 5`） | `status=budget-limited`，暂停循环 |
| Token 预算 | `token_limit=200_000`（`token_budget.used >= limit`） | 同上 |
| 用户输入阻断 | 检测到未读用户消息 | `status=paused`，等待人工指令 |

#### §10.6 事件驱动续跑

| 事件 | 触发器 | 动作 |
|---|---|---|
| `sessionStart` | Cursor 窗口重载 / 会话刷新 | 读快照 → 注入 system_reminder 提示继续 Act |
| `afterFileEdit` | Agent 写文件完成 | 触发 Audit（对比 `snapshot.latest_artifact` vs `accept_criteria`） |
| `afterAgentResponse` | Agent 每次响应结束 | 破环机制双门判定（见 `goal-loop/SKILL.md` §10） |

#### §10.7 向后兼容保证

- `goal=None`（默认）时：完全走原有顺序编排逻辑，不创建快照，不进入五段式循环
- `run_stage()` 不受影响
- `execute_simple_flow()` / `execute_full_flow()` 不受影响
- 已有的 `stage_callables` 参数继续有效

#### §10.8 与 goal-loop/SKILL.md 的关系

本 skill 是 goal-loop 能力在 AIDocxWorkFlow 流水线场景的**应用层集成**：

- **上游能力源**：`goal-loop/SKILL.md` 定义五段式闭环 + 快照 20 字段 + 三层熔断 + 事件驱动
- **本 skill 职责**：将 goal-loop 能力映射到 `run_pipeline()` 的 stages 流水线
- **不修改上游**：goal-loop/SKILL.md 独立维护，作为通用自治循环规范

**引用约束**：本 skill 引用 goal-loop/SKILL.md 的内容时，以 goal-loop/SKILL.md 最新版本为准，不在本 skill 中重复定义。
