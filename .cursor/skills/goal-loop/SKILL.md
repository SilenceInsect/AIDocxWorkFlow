---
name: goal-loop
description: >
  对标 Codex Native Goal (/goal) 的项目级自治循环技能。提供会话级 Goal 快照持久化、事件驱动自动续跑、五段式 (Plan→Act→Audit→Review→Iterate) 强制闭环、三层熔断 (最大轮次 / Token 预算 / 用户输入阻断) 与内置业务审计规则。仅通过 /goal-loop 显式调用，禁止 Agent 自动触发。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: goal-execution
  spec_version: agentskills.io/1.0
  cursor_compat: true
  hermes_compat: true
---

# Goal Loop 自治循环

## 1. 命令契约

```
/goal-loop <任务目标>   # 启动自治循环（含或不含 plan）
/pause-goal              # 暂停当前自治循环（写入 pause 标志）
/clear-goal              # 清空当前 goal 快照，重置状态为 idle
```

调用 `/goal-loop` 时必须携带 `任务内容 + 任务 plan（验收标准 + 正确范例）`；缺少时按 §6 推理补全并标注 `[推理补全]`。

每轮固定输出三件套：

1. 最新完整交付物
2. 本轮审计论证单 (`audit_<round>.md`)
3. 本轮复盘报告 (`review_<round>.md`)

## 2. Goal 快照 Schema（必填 10 字段）

会话级持久化字段（文件路径：`.goal-log-db/active/<goal_id>/snapshot.json`）：

| 字段 | 类型 | 含义 |
|---|---|---|
| `goal_id` | string | 唯一任务 ID，UUIDv4 |
| `raw_user_goal` | string | 用户原始目标文本 |
| `accept_criteria` | string[] | 可量化验收断言清单（≥ 1 条） |
| `task_queue` | object[] | 子任务队列（每项含 `id` / `title` / `status` / `artifact`） |
| `loop_round` | int | 当前迭代轮次（从 1 起） |
| `last_audit` | object/null | 上一轮审计论证记录 |
| `last_review` | object/null | 上一轮复盘根因与修复方案 |
| `latest_artifact` | string/null | 最新交付物路径 |
| `status` | enum | `active` / `achieved` / `paused` / `budget-limited` |
| `token_budget` | object | `{used, limit, updated_at}` 资源消耗记录 |

**持久化规则**：

- 窗口重载、工具执行结束、中途闲聊、刷新输入框 → 不丢失进度
- 仅 `/clear-goal` 手动清空指令可销毁任务
- 普通对话无法篡改 Goal 快照（读写隔离：仅 `goal_snapshot.py` 写入）
- atomic write：先写 `<file>.tmp` 再 `os.replace()`，防止崩溃半写

**Round 无新交付物时处理规范**（F1 修复）：

当某轮 Act 阶段无新 artifact 产出时：
1. `audit_<round>.md` 仍必须产出（总结当前状态，不可跳过）
2. `latest_artifact` 字段沿用上一轮的值
3. audit 内容聚焦于"本轮是否仍保持 achieved 状态"
4. review 内容说明"本轮无新交付物原因 + 是否可继续收敛"

## 2.1 value_ratio 软指导（v30 D1 新增）

> **来源**：v26 草案 D1 + v28 DT-V28-001 决策（选 B：启动软指导值 0.5 + 收敛硬约束 0.6）
>
> **运行时行为**（`ai_workflow/goal_snapshot.py`）：
> - `create_snapshot` 阶段：`value_ratio >= MIN_VALUE_RATIO_HARD (0.6)` 才可启动，低于 0.5 则 WARN 并允许继续
> - 收敛判定阶段：必须 `value_ratio >= MIN_VALUE_RATIO_HARD (0.6)`
> - 0.5 ~ 0.6 之间：WARN 并记录到 `follow_up_items`，不阻断启动
>
> **常量**：`MIN_VALUE_RATIO_SOFT = 0.5`（启动软指导），`MIN_VALUE_RATIO_HARD = 0.6`（收敛硬约束）

**实践意义**：
- 简单工程类目标（如"修复 bug"）process_criteria 可能占多数，ratio 落在 0.5~0.6 区间——WARN 不阻断
- 业务类目标（如"落地新规范"）value_criteria 自然占多数——ratio 通常 ≥ 0.6
- 真正体现"价值导向优先"的把关在**收敛判定**（必须 0.6），不在启动前检

## 3. 五段式自治闭环（每轮必跑，不可跳过）

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

### 3.1 Plan 规划
- 解析顶层目标 → 拆解结构化 `task_queue`
- 生成可量化 `accept_criteria`（无模糊描述）
- 锁定全局约束、历史坑点、禁止行为（写入 `governance/design_iter/plans/v{N}/`）

### 3.2 Act 执行
- 完整产出交付物（文档/JSON/代码/规范）
- 调用工具落地，不省略、不缩写
- 每次写操作前必须 Read 目标文件（先验后答）

### 3.3 Audit 客观论证
逐条对照 `accept_criteria`，凭客观证据判定 `PASS` / `FAIL` / `UNKNOWN`：

- **标准**：验证哪条验收
- **证据**：文件路径、命令输出、diff
- **正向论证**：证据如何支持通过
- **反向挑战**：什么情况会推翻通过
- **判定**：`PASS` / `FAIL` / `UNKNOWN`（`UNKNOWN` 不得按通过处理）

### 3.4 Review 深度复盘
固定三段式：

1. 缺陷汇总（去重、排序：严重 / 一般 / 优化）
2. 根因定位（机制 / 规范 / 习惯问题）
3. 可落地修复方案（明确下一步动作 + 影响范围）

> **v30 D3 新增：Review 双档（轻量 + 深度）**
> - `review_<round>_light.md`：**每轮必产**，≤ 30 行 PASS/FAIL 摘要（用于触发 breakloop 门 B 数据更新）
> - `review_<round>.md`：**每 2 轮产 1 次**或最终轮，含完整三段式复盘
> - Audit 不得跳轮（§3.5 F2 修复条款）；Review 可按双档节奏产

### 3.5 Iterate 收敛判定
- 全部 `PASS` → `status = achieved`，归档全量日志，终止循环
- 存在 `FAIL` 且未超限 → 自动修复，`loop_round += 1`，继续 Act
- 达到上限 → `status = budget-limited`，输出阻塞清单，进入 `BLOCKED`

**禁止跳轮条款**（F2 修复）：

> Round 4 audit_4.md 缺失是 v17.1 goal-loop 的核心结构性问题（DT-v17.1-001 §DT-2 问题 1）。本条款明确禁止：
- 禁止跳过中间 Round（每轮必须产出 `audit_<round>.md` + `review_<round>.md`）
- 禁止引用"任务描述 / GOAL.md / SKILL.md 中不存在的条款"作为决策依据
- 若需提前收敛，必须满足 §9 收敛判定全部条件，不得以"无新交付物"为由跳过 audit
- 违反本条款 → 触发 §5 反模式熔断 → 创建 DT 决策任务

## 3.6 goal_signature 漂移校验（v30 D2 新增）

> **来源**：v26 草案 D2 + v28 DT-V28-002 决策（选 D：增量更新签名 + `goal_signature_changelog[]`）
>
> **签名漂移判定**（`ai_workflow/goal_snapshot.py`）：
> - `compute_similarity(raw_user_goal, snapshot["goal_signature"])` 计算相似度
> - `>= MIN_SIGNATURE_SOFT (0.5)`：**PASS**，无警告
> - `< MIN_SIGNATURE_SOFT (0.5)`：触发 WARN + 记录到 `snapshot["goal_signature_changelog"]`
>
> **changelog 记录格式**：
> ```json
> {
>   "timestamp": "<ISO>",
>   "previous_signature": "<hex>",
>   "new_signature": "<hex>",
>   "similarity": 0.XX,
>   "reason": "<变更说明>",
>   "round": <N>
> }
> ```
>
> **不阻断**：签名更新不等于目标漂移——目标变更本身是自治循环的正常行为，changelog 是审计链，不是阻断器
>
> **常量**：`MIN_SIGNATURE_SOFT = 0.5`（软指导阈值）
>
> **schema 字段**：`snapshot["goal_signature_changelog"]`（`goal_snapshot.py` v1.2+，向后兼容旧快照默认 `[]`）

## 4. 三层熔断防死循环

| 熔断层 | 默认阈值 | 触发动作 |
|---|---|---|
| 最大迭代轮次 | `loop_round >= 5`（可环境变量覆盖） | `status = budget-limited`，暂停循环 |
| Token 预算 | **默认无上限**（`token_budget.limit = null`）；显式声明才限制 | 同上 |
| 用户输入阻断 | 检测到未读用户消息 | `status = paused`，等待人工指令 |

> **Token 默认无上限**：除非显式声明 `GOAL_LOOP_TOKEN_LIMIT` 环境变量或 `create_snapshot(token_limit=N)`，否则 token 熔断永不触发。设置示例：`GOAL_LOOP_TOKEN_LIMIT=200000` 或 `python3 goal_loop_runner.py new --goal "..." --token-limit 200000`。

阈值由 `goal_loop_runner.py` 配置常量管理；优先级 Token > 用户输入 > 轮次。

## 5. 反模式打断与决策任务

在每轮 Audit / Review 节点扫描：

- 只产出不验证（只调用工具不读产物）
- 只因测试通过就宣布目标完成
- 只修局部问题不检查规则 / 文档 / 调用方一致性
- 没有证据却给通过结论
- 验收标准在执行中被静默删除、弱化或替换
- 连续同一种修复处理同根因无新增证据
- 隐藏未解决问题 / 跳过失败验证
- 为通过检查而修改测试 / 校验器 / 正确范例
- 即将执行不可逆 / 高风险 / 超授权操作

命中反模式 → 立即暂停主任务，创建并执行 `DT-<seq>` 决策任务，记录：触发反模式 / 证据 / 断点 / 根因假设 / 候选行动 / 选择与依据 / 执行结果 / 验证证据 / 恢复点。

## 6. 优先级与边界

1. 先遵守当前仓库规则、用户显式约束和安全边界，再执行本 Skill。
2. 只在需要用户专属判断时询问：不可逆或破坏性操作、权限/认证、秘密信息、产品范围冲突、多个方案存在不可推断的业务取舍。
3. 可逆且低风险的工程决策由 Agent 根据验收标准自主选择，并记录依据。
4. 不以「写完代码」「测试通过」或「完成一轮」代替目标完成。
5. 不弱化测试、删除验收标准或缩小任务范围来制造收敛。
6. 缺少 plan / 验收标准 / 正确范例时，按工程通用标准推理补全并标注 `[推理补全]`，继续执行；不得仅因缺失而停下来询问。

## 7. 业务审计规则（内置）

适配 AIDocxWorkFlow 测试标准化治理场景，详见 `.cursor/rules/GOAL_BUSINESS_AUDIT.mdc`：

1. FP 必须中性功能命名，禁止场景化命名（如 `FP-001 用户登录` → `FP-001 身份验证`）
2. 禁止文本【】锚点冗余，依赖结构化字段溯源（`obj_id` / `story_id` / `feature_point_id`）
3. TP/TC/Excel 结构化映射，禁止文本截取解析（统一 ID 字段）
4. 正反场景无语义冲突（EP_VALID 与 EP_INVALID 边界一致）
5. L1 校验轻量化、无格式绑架（仅校验必填字段和枚举，不校验文本格式）

## 8. 事件驱动自动续跑

事件 → handler 映射（`.cursor/hooks.json`）：

| 事件 | 触发器 | 动作 |
|---|---|---|
| `sessionStart` | Cursor 窗口重载 / 会话刷新 | 读快照 → 注入 system_reminder 提示继续 Act |
| `afterFileEdit` | Agent 写文件完成 | 触发 Audit（对比 snapshot.latest_artifact vs accept_criteria） |
| `afterShellExecution` | Shell 命令完成 | 触发 Review（如命令返回非 0 或时间超阈值） |
| `beforeSubmitPrompt` | 用户提交 prompt | 检测未读消息 → 触发暂停熔断 |

## 9. 收敛判定

只有同时满足：

- 每条 `accept_criteria` 均为 `PASS`，且有可复核证据
- 正确范例已实现或由等价实例验证
- 至少一次反向挑战，能识别反例
- 所有反模式决策任务均已关闭
- 无未处理 `FAIL` / `UNKNOWN` / 回归 / 真实阻塞
- 最终差异与目标范围一致，没有意外修改

→ 输出 `status = achieved` + `CONVERGED` 结束报告（含 6 项：状态 / 完成内容 / 验收证据 / 自迭代记录 / 剩余问题 / 影响范围）。

无法满足 → `REPAIRING` 或 `BLOCKED`（列阻塞证据 + 解除所需最小输入）。

## 10. 破环机制（Break Loop Mechanism）

> **本节是对 §1-§9 的运行时补强——解决"单次响应完成 ≠ 目标完成"导致的循环静默死亡。**

### 10.1 触发点

新增事件 **`afterAgentResponse`**（Cursor Agent 每次响应结束后触发一次）。对应 hook：
`.cursor/hooks/goal_loop_breakloop_hook.py`，注册见 `.cursor/hooks.json#afterAgentResponse`。

### 10.2 双门判定

防止 Agent "自我宣布 CONVERGED" 但数据层未支持：

| 门 | 检查项 | 不通过 → |
|---|---|---|
| 门 A（字面） | `response_text` 含 `CONVERGED` / `BLOCKED` / `REPAIRING→BLOCKED` | 不注入完成阻断 |
| 门 B（数据） | `last_audit.verdicts` 中每个 `PASS` 都有非空 `reverse_challenge` | 注入【阻断警告】 |

| 输入情形 | 行为 |
|---|---|
| 无 active goal | exit 0，不注入（避免噪声） |
| 含 CONVERGED + 数据未支持 | 注入【破环阻断】system_reminder |
| 含 CONVERGED + 数据支持 | exit 0（真通过，不注入） |
| 未含 CONVERGED/BLOCKED | 注入【破环续跑】system_reminder |

### 10.3 反模式防御

| 反模式 | 防御策略 |
|---|---|
| 测试通过 = 目标完成 | 门 B 强制 `reverse_challenge` 字段非空 |
| 自我宣布 CONVERGED | 门 A 要求关键字命中 + 门 B 要求数据支持 |
| 循环静默死亡 | 门 A 不命中时主动注入续跑 reminder |
| Agent 伪造 last_audit | `last_audit` 仅由 `GoalLoop.audit()` API 写入，普通对话无法篡改 |

### 10.4 跨平台兼容性

| Agent | 事件支持 | 兼容方案 |
|---|---|---|
| Cursor Agent | `afterAgentResponse`（本设计） | 直接接入 |
| Claude Code | 等价事件 `PostResponse` / `Stop` | 需 IDE 适配（v18+） |
| Codex CLI | `stop` 事件 | 需 IDE 适配（v18+） |
| Hermes Agent | 等价 `agentEnd` | 需 IDE 适配（v18+） |

### 10.5 self-test 豁免

本 hook 含 `def self_test()` + `--self-test` argv 分支，未引入新依赖，不修改既有业务函数。作为豁免单元对待（单文件改动）。

---

## 正确范例

输入：

```text
/goal-loop 创建项目级 goal-loop Skill 全量自治循环能力。
计划：五段式 + 快照持久化 + 三层熔断 + 业务审计 + 事件驱动；验收标准为 SKILL.md 完整规范、快照 10 字段、runner 五段状态机、hooks 接入 4 事件、业务审计 5 条规则；正确范例为用本任务自身作为目标运行一次完整 5 轮迭代。
```

合格执行应：锁定目标契约（落档）→ 5 轮迭代（每轮产 audit_*.md + review_*.md）→ 每轮自检论证 → 命中反模式时暂停并决策 → 全部 `PASS` 后 `achieved` 收敛。

## 错误范例

只重写 SKILL.md 而不落地代码；虚构 Codex 内部实现并声称"对标成功"；把"测试通过"当作"目标完成"；删除验收标准或缩小范围以制造收敛；快照写入不 atomic 导致半写丢失。
