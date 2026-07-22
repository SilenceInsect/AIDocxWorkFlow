# Goal Loop 产品功能说明

> **文档版本**：v1.1
> **归档日期**：2026-07-18
> **归属**：AIDocxWorkFlow 项目级自治循环 Skill
> **状态**：已审查 → v1.1 实施完成
> **相关文件**：
> - 规则定义：`.cursor/skills/goal-loop/SKILL.md`（v1.1）
> - 快照持久化：`ai_workflow/goal_snapshot.py`（v3，18字段）
> - 破环 Hook：`.cursor/hooks/goal_loop_breakloop_hook.py`（v2）
> - 反模式库：`knowledge/public/goal_loop/antipattern_cases.jsonl`
> - 效能Schema：`knowledge/public/goal_loop/session-index-schema.md`

---

## 1. 产品概述

### 1.1 定位

Goal Loop 是 AIDocxWorkFlow 项目级自治循环 Skill，对标 Codex Native `/goal` 的会话级目标管理能力。

**解决的问题**：
- Agent 单次响应完成 ≠ 目标实际完成（循环静默死亡）
- 多轮迭代中进度丢失（窗口重载、闲聊、刷新后无法续跑）
- Agent 自我宣布 CONVERGED 但数据层不支持（虚假收敛）
- 遗留问题无法跨 goal 传递（本轮结束 = 问题消失）

### 1.2 核心能力

| 能力 | 说明 |
|---|---|
| 会话级快照持久化 | Goal 状态（轮次、审计记录、剩余任务）写入文件，跨会话不丢失 |
| 五段式强制闭环 | Plan → Act → Audit → Review → Iterate，每轮必跑，不可跳过 |
| 三层熔断防死 | 最大轮次 / Token 预算 / 用户输入阻断 |
| 事件驱动自动续跑 | sessionStart 自动读取快照并续跑 Act |
| 破环双门判定 | 字面 CONVERGED + 数据层 audit 双重验证，防止虚假收敛 |
| 内置业务审计 | AIDocxWorkFlow 场景的 5 条 FP 命名 / 字段溯源规则 |
| 原子化写后验证 | snapshot.json.tmp + os.replace() + read-back 断言 |

### 1.3 v1.1 优化项 vs 已知缺口

| 缺口编号 | 描述 | v1.1 解决方案 | 状态 |
|---|---|---|---|
| GQ-01 | CONVERGED 后遗留问题无法自动生成 follow-up goal | `converged_with_followup` 状态 + `follow_up_items` 结构 | ✅ 已解决（GL-002） |
| GQ-02 | `task_queue` 残留项不跨轮传递 | `follow_up_items` 结构化遗留项（根因相同） | ✅ 已解决（GL-002） |
| GQ-03 | `coverage_validator` 无 `story_id` fallback | 与 Goal Loop 无直接关联，属于 coverage_validator 模块 | ⏳ 待独立修复 |

**v1.1 新增 8 项 GL-001~GL-008**（详见 §12b）

---

## 2. 命令契约

### 2.1 三条命令

```
/goal-loop <任务目标>   # 启动自治循环（含或不含 plan）
/pause-goal              # 暂停当前自治循环（写入 pause 标志）
/clear-goal              # 清空当前 goal 快照，重置状态为 idle
```

**调用约定**：
- `/goal-loop` 时必须携带 `任务内容 + 任务 plan（验收标准 + 正确范例）`
- 缺少 plan 时，Agent 按 §6 推理补全并标注 `[推理补全]`
- 每轮固定输出三件套：最新交付物 + `audit_<round>.md` + `review_<round>.md`

### 2.2 Goal 快照 Schema（v1.1 — 18 字段）

快照路径：`.goal-log-db/active/<goal_id>/snapshot.json`

| 字段 | 类型 | 含义 |
|---|---|---|
| `goal_id` | string | 唯一任务 ID，UUIDv4 |
| `raw_user_goal` | string | 用户原始目标文本 |
| `value_criteria` | string[] | 外部价值类验收（v1.1） |
| `process_criteria` | string[] | 内部过程类验收（v1.1） |
| `value_ratio` | float | value_criteria 占比（v1.1） |
| `severity_label` | enum | BLOCKER / MAJOR / MINOR（v1.1） |
| `follow_up_items` | object[] | 遗留项列表（v1.1） |
| `goal_signature` | string | 目标语义哈希（v1.1，GL-008） |
| `out_of_scope_md` | string | 禁区清单路径（v1.1，GL-003） |
| `audit_stability` | object | 增量审计追踪（v1.1，GL-005） |
| `efficiency_stats` | object | 效能统计（v1.1，GL-007） |
| `task_queue` | object[] | 子任务队列 |
| `loop_round` | int | 当前迭代轮次 |
| `last_audit` | object/null | 上一轮审计论证记录 |
| `last_review` | object/null | 上一轮复盘根因与修复方案 |
| `latest_artifact` | string/null | 最新交付物路径 |
| `status` | enum | active / achieved / converged_with_followup / paused / budget-limited |
| `token_budget` | object | `{used, limit, updated_at}` |

**持久化规则**：
- 窗口重载、工具执行结束、中途闲聊、刷新输入框 → 不丢失进度
- 仅 `/clear-goal` 手动清空指令可销毁任务
- 普通对话无法篡改 Goal 快照（读写隔离：仅 `goal_snapshot.py` 写入）
- atomic write：先写 `<file>.tmp` 再 `os.replace()`，防止崩溃半写
- 写后 read-back 验证（goal_id 一致性断言）

---

## 3. 五段式自治闭环

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

### 3.5 Iterate 收敛判定
- 全部 `PASS` → `status = achieved`，归档全量日志，终止循环
- 存在 `FAIL` 且未超限 → 自动修复，`loop_round += 1`，继续 Act
- 达到上限 → `status = budget-limited`，输出阻塞清单，进入 `BLOCKED`

**禁止跳轮条款**：
- 禁止跳过中间 Round（每轮必须产出 `audit_<round>.md` + `review_<round>.md`）
- 禁止引用"任务描述 / GOAL.md / SKILL.md 中不存在的条款"作为决策依据
- 若需提前收敛，必须满足 §6 收敛判定全部条件，不得以"无新交付物"为由跳过 audit
- 违反本条款 → 触发 §5 反模式熔断 → 创建 DT 决策任务

**Round 无新交付物时处理规范**：
1. `audit_<round>.md` 仍必须产出（总结当前状态，不可跳过）
2. `latest_artifact` 字段沿用上一轮的值
3. audit 内容聚焦于"本轮是否仍保持 achieved 状态"
4. review 内容说明"本轮无新交付物原因 + 是否可继续收敛"

---

## 4. 三层熔断防死循环

| 熔断层 | 默认阈值 | 触发动作 |
|---|---|---|
| 最大迭代轮次 | `loop_round >= 5` | `status = budget-limited`，暂停循环 |
| Token 预算 | `token_budget.used >= token_budget.limit` | 同上 |
| 用户输入阻断 | 检测到未读用户消息 | `status = paused`，等待人工指令 |

优先级：Token > 用户输入 > 轮次。

---

## 5. 反模式打断与决策任务

在每轮 Audit / Review 节点扫描以下 10 种反模式：

| # | 反模式 | 描述 |
|---|---|---|
| 1 | 只产出不验证 | 只调用工具不读产物 |
| 2 | 测试通过 = 目标完成 | 不验证实际业务价值 |
| 3 | 局部问题优先 | 只修局部不检查全局一致性 |
| 4 | 无证据给通过 | 没有客观证据却给 PASS |
| 5 | 验收标准漂移 | 执行中静默删除、弱化或替换验收标准 |
| 6 | 同根因重复修复 | 连续同一种修复处理同根因无新增证据 |
| 7 | 隐藏问题 | 隐藏未解决问题 / 跳过失败验证 |
| 8 | 伪造测试 | 为通过检查而修改测试 / 校验器 / 正确范例 |
| 9 | 循环静默死亡 | 达到收敛条件但不宣布 / 不归档 |
| 10 | 越权操作 | 即将执行不可逆 / 高风险 / 超授权操作 |

命中反模式 → 立即暂停主任务，创建并执行 `DT-<seq>` 决策任务，记录：触发反模式 / 证据 / 断点 / 根因假设 / 候选行动 / 选择与依据 / 执行结果 / 验证证据 / 恢复点。

---

## 6. 优先级与边界

1. 先遵守当前仓库规则、用户显式约束和安全边界，再执行本 Skill。
2. 只在需要用户专属判断时询问：不可逆或破坏性操作、权限/认证、秘密信息、产品范围冲突、多个方案存在不可推断的业务取舍。
3. 可逆且低风险的工程决策由 Agent 根据验收标准自主选择，并记录依据。
4. 不以「写完代码」「测试通过」或「完成一轮」代替目标完成。
5. 不弱化测试、删除验收标准或缩小任务范围来制造收敛。
6. 缺少 plan / 验收标准 / 正确范例时，按工程通用标准推理补全并标注 `[推理补全]`，继续执行；不得仅因缺失而停下来询问。

---

## 7. 业务审计规则（内置）

适配 AIDocxWorkFlow 测试标准化治理场景，详见 `.cursor/rules/GOAL_BUSINESS_AUDIT.mdc`：

| # | 规则 | 禁止 | 正确示例 |
|---|---|---|---|
| 1 | FP 中性功能命名 | `FP-001 用户登录` | `FP-001 身份验证` |
| 2 | 禁止【】文本锚点冗余 | 依赖"见上文【】"追溯 | 依赖 `obj_id` / `story_id` / `feature_point_id` 结构化字段溯源 |
| 3 | TP/TC/Excel 结构化映射 | 文本截取解析 | 统一 ID 字段解析 |
| 4 | 正反场景无语义冲突 | `EP_VALID` 与 `EP_INVALID` 边界重叠 | 边界一致且互斥 |
| 5 | L1 校验轻量化 | 校验文本格式（格式绑架） | 仅校验必填字段和枚举 |

---

## 8. 事件驱动自动续跑

| 事件 | 触发器 | 动作 |
|---|---|---|
| `sessionStart` | Cursor 窗口重载 / 会话刷新 | 读快照 → 注入 system_reminder 提示继续 Act |
| `afterFileEdit` | Agent 写文件完成 | 触发 Audit（对比 snapshot.latest_artifact vs accept_criteria） |
| `afterShellExecution` | Shell 命令完成 | 触发 Review（如命令返回非 0 或时间超阈值） |
| `beforeSubmitPrompt` | 用户提交 prompt | 检测未读消息 → 触发暂停熔断 |

---

## 9. 收敛判定

只有同时满足以下 6 条，status 才可设为 `achieved`：

| # | 条件 | 说明 |
|---|---|---|
| 1 | 每条 `accept_criteria` 均为 `PASS` | 且有可复核证据 |
| 2 | 正确范例已实现或等价实例验证 | 不能只靠逻辑推演 |
| 3 | 至少一次反向挑战 | 能识别反例 |
| 4 | 所有反模式决策任务均已关闭 | DT-* 任务无 open |
| 5 | 无未处理 `FAIL` / `UNKNOWN` / 回归 / 真实阻塞 | 0 残留 |
| 6 | 最终差异与目标范围一致，无意外修改 | diff 可控 |

满足 → 输出 `status = achieved` + `CONVERGED` 结束报告（含 6 项：状态 / 完成内容 / 验收证据 / 自迭代记录 / 剩余问题 / 影响范围）。

不满足 → `REPAIRING` 或 `BLOCKED`（列阻塞证据 + 解除所需最小输入）。

---

## 10. 破环机制（Break Loop Mechanism）

### 10.1 触发点

事件 **`afterAgentResponse`**（Cursor Agent 每次响应结束后），对应 hook：`.cursor/hooks/goal_loop_breakloop_hook.py`。

### 10.2 双门判定

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

---

## 11. 产物结构

### 11.1 Snapshot 目录

```
.goal-log-db/
  active/
    <goal_id>/
      snapshot.json          ← Goal 快照（10 字段）
      .lock                  ← 文件锁（防并发）
  session-index.jsonl        ← 全量历史索引
  thread_goals.json          ← 全局状态库
```

### 11.2 Goal 产出目录

```
workflow_assets/goals/<goal_id>/
  snapshot.json              ← 首轮由 Agent 创建，后续由 goal_snapshot.py 写入
  audit_1.md ~ audit_N.md    ← 每轮审计论证单
  review_1.md ~ review_N.md  ← 每轮复盘报告
  CONVERGED.md               ← 收敛结束报告（含 6 项）
```

### 11.3 产出报告格式

**CONVERGED.md 固定 6 项**：
1. 状态
2. 完成内容
3. 验收证据
4. 自迭代记录
5. 剩余问题
6. 影响范围

**audit_<round>.md 固定 5 项**：
1. 标准（对应哪条 accept_criteria）
2. 证据（文件路径 / 命令输出 / diff）
3. 正向论证
4. 反向挑战
5. 判定（PASS / FAIL / UNKNOWN）

**review_<round>.md 固定 3 段**：
1. 缺陷汇总（去重、排序）
2. 根因定位
3. 可落地修复方案

---

## 12. 版本历史

| 版本 | 日期 | 变更说明 |
|---|---|---|
| v1.0 | 2026-07-18 | 初版归档，含完整规范 + 3 个已知缺口 |
| v1.1 | 2026-07-18 | GL-001~GL-009 全部落地：外部价值校验、验收分级、禁区清单、体系复盘、增量审计、目标签名、反模式积累、效能度量；Schema 扩展至 18 字段（注：2026-07-21 撤销 GL-005 质量基线兜底并删除对应文件，后续 GL 编号 -1） |

---

## 12b. v1.1 新增功能详情

### GL-001 外部价值校验

- `accept_criteria` 拆分为 `value_criteria`（外部价值类）和 `process_criteria`（内部过程类）
- `value_ratio >= 0.6` 强制约束，Plan 阶段预检
- `create_snapshot()` 不满足 ratio 时抛出 `ValueRatioError`

### GL-002 验收标准分级

- 三级严重度：`BLOCKER` / `MAJOR` / `MINOR`
- `converged_with_followup` 新状态：BLOCKER 全 PASS + MAJOR/MINOR 可遗留
- `follow_up_items` 结构化遗留项记录
- 破环 hook 支持 `CONVERGED_WITH_FOLLOWUP` 关键字

### GL-003 out_of_scope 禁区清单

- Plan 阶段强制产出 `out_of_scope.md`（三类禁区）
- Audit 阶段新增范围合规性检查
- `snapshot.out_of_scope_md` 存储禁区清单路径

### GL-004 体系级复盘沉淀

- `systemic_issues.md` 全局问题沉淀机制
- Review 阶段自动识别 Skill 规范漏洞
- 同类问题累计 ≥ 3 次触发 Skill 迭代建议草案

### GL-005 增量审计去冗余

- `audit_stability` 字段追踪稳定项
- 连续 2 轮 PASS + 产出物无变更 → 标记 `SKIPPED_STABLE`
- Audit 报告中含"稳定跳过项"统计

### GL-006 反模式案例沉淀

- `antipattern_cases.jsonl` 结构化案例积累
- 同类反模式累计 ≥ 2 条 → 自动生成规则建议

### GL-007 体系效能度量

- `efficiency_stats` 字段（收敛轮次、首轮通过率、BLOCKER 遗留率）
- `session-index-schema.md` 效能字段规范
- `update_efficiency_stats()` API

### GL-008 目标签名防漂移

- `goal_signature` 字段（SHA-256 哈希）
- `generate_goal_signature()` / `compute_similarity()` 辅助函数
- 相似度 < 0.7 触发 WARN

---

## 13. 审查清单（人工审查用）

审查者检查以下功能点，标注优化优先级：

| # | 功能点 | 描述 | 审查意见 |
|---|---|---|---|
| F-01 | 命令契约 | `/goal-loop` / `/pause-goal` / `/clear-goal` 三命令 | |
| F-02 | 快照持久化 | 10 字段 Schema + atomic write + read-back 验证 | |
| F-03 | 五段闭环 | Plan → Act → Audit → Review → Iterate 强制每轮必跑 | |
| F-04 | 禁止跳轮条款 | audit_*/review_* 不可跳过 | |
| F-05 | 无新交付物规范 | Round 无 artifact 时 audit 仍必须产出 | |
| F-06 | 三层熔断 | 轮次 / Token / 用户输入阻断 | |
| F-07 | 反模式打断 | 10 种反模式 + DT 决策任务 | |
| F-08 | 优先级边界 | §6 六条边界条件 | |
| F-09 | 业务审计内置 | 5 条 AIDocxWorkFlow 场景规则 | |
| F-10 | 事件驱动续跑 | 4 事件 → handler 映射 | |
| F-11 | 收敛判定 6 条 | 全部满足才 achieved | |
| F-12 | 破环双门 | 门 A 字面 + 门 B 数据双重验证 | |
| F-13 | 遗留问题传递 | **当前缺失**（GQ-01）| |
| F-14 | task_queue 跨轮 | **当前缺失**（GQ-02）| |

---

*本文件为产品功能说明初稿，待人工审查后制定优化方案。*
