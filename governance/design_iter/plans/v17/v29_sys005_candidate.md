# v29 SYS-005 候选（待人工审核）

> **漏洞 ID**：SYS-005
> **状态**：CANDIDATE（候选，未入正式表）
> **相关 Skill**：goal-loop
> **来源**：`governance/design_iter/plans/v29/review_round1.md` §2 根因 C、§6 SYS-005；`governance/design_iter/plans/v29/audit_round1.md` §4 SYS-005
> **正式入册目标**：`knowledge/public/goal_loop/systemic_issues.md`
> **审核人**：待人工

## 1. 漏洞描述

`goal_snapshot.create_snapshot()` 不接收 `goal_id` 入参，而是在调用内部自动生成 UUID v4，并按自动生成的 `goal_id` 写入 `.goal-log-db/active/<goal_id>/snapshot.json`。

父任务如果在调用 `create_snapshot()` 前，先为自定义 `goal_id` 执行 `mkdir .goal-log-db/active/<custom_goal_id>/`，会产生两个不同目录：

1. 父任务预建的自定义目录；
2. `create_snapshot()` 按返回 UUID 创建的真实快照目录。

父任务继续使用自定义 `goal_id` 调用 `update_snapshot()` 时，目录与快照身份错位，可能出现“目录存在但快照不存在”、更新目标错误或孤儿目录。

## 2. 触发记录

| 触发场景 | 是否形成错位 | 计数 | 证据 |
|---|---|---:|---|
| v29 Round 0 启动 | 是 | 1 | `audit_round1.md` §4 与 `review_round1.md` §2 根因 C 均记录父任务预先创建自定义 Goal 目录后与 `create_snapshot()` 返回 UUID 错位 |
| v29 Round 2 启动 | 否 | 0 | Goal ID `97ab325d-a505-466b-8778-62c4706c9ff8` 的目录、`snapshot.json#goal_id` 与 `session-index.jsonl` 的 `create` 记录一致 |

- **累计出现次数**：1
- **首次时间**：2026-07-20 01:42（UTC+8）
- **末次时间**：2026-07-20 01:42（UTC+8）
- **当前状态**：候选跟踪；未达到 Skill 实装阈值

本次只核对现有 Round 2 启动证据，没有另行调用 `create_snapshot()` 制造测试快照，也没有预建错误目录。静态源码验证或阅读历史记录不计为新触发；只有真实发生“预建自定义目录与返回 UUID 错位”才增加出现次数。

## 3. 当前方案与修复方案

### 当前 API 行为

- `create_snapshot(raw_user_goal, value_criteria, ...)` 无 `goal_id` 参数。
- `create_snapshot()` 内部执行 `str(uuid.uuid4())` 生成身份。
- `create_snapshot()` 自动按返回身份落盘，不需要父任务预建目录。

### 正确调用方案

1. 父任务先调用 `create_snapshot(...)`。
2. 父任务从返回对象读取 `snapshot["goal_id"]`。
3. 父任务将返回的 `goal_id` 用于后续 `update_snapshot(goal_id, ...)`、子任务描述和审计引用。
4. 父任务禁止在 `create_snapshot()` 前预建自定义 Goal ID 目录。

### 达到阈值后的候选修复

当同类错位累计达到 3 次时，再生成 Skill 迭代建议草案，候选内容为：

- 在 goal-loop Plan 持久化流程中明确“先 `create_snapshot()`，后使用返回 `goal_id`”；
- 明确禁止父任务预先 `mkdir` 自定义 Goal ID 目录；
- 为父任务启动流程增加“目录名、`snapshot.json#goal_id`、create 索引三者一致”检查。

当前累计 1 次，小于 3 次，不修改 `SKILL.md`，也不生成正式实装草案。

## 4. 入册流程

`knowledge/public/goal_loop/systemic_issues.md` 当前正式表只有 SYS-008，没有 SYS-005。根据公共知识库人工审核边界：

1. Agent 只维护本候选档；
2. 人工核对触发证据、计数和修复建议；
3. 人工确认后，再由人工将 SYS-005 复制到正式问题表；
4. Agent 不直接写入 `knowledge/public/goal_loop/systemic_issues.md`。

## 5. 反向挑战

1. **若正式表已含 SYS-005 但出现次数仍为 0**：说明候选入册或计数流程漏跑，当前“正式表无 SYS-005”的实测结论将被推翻。
2. **若候选档缺少 API 行为、触发证据、时间和修复路径**：人工无法复核，候选流程不合格；本档已提供对应信息。
3. **若累计次数达到 3 次仍宣称不实施**：违反 GL-004 的 Skill 迭代建议阈值；当前实证累计仅 1 次，因此不实施成立。

## 6. 审计元数据

- **Goal ID**：`97ab325d-a505-466b-8778-62c4706c9ff8`
- **Worker**：T-205
- **验收项**：RR-2-004
- **subagent_budget_used**：34000（估算）
- **修改范围**：仅创建本候选档；未修改正式问题表、`snapshot.json` 或 `SKILL.md`
