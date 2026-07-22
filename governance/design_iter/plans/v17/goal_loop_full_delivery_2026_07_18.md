# Goal Loop Skill 全量交付记录

## 目标契约

- **目标**：在 AIDocxWorkFlow 项目内实现对标 Codex Native Goal /goal 的自治循环能力，包括：会话级 Goal 快照持久化、事件驱动自动续跑、五段式自治闭环、三层熔断、业务审计规则、管控指令 (`/pause-goal` / `/clear-goal`)。
- **任务范围**：
  1. 改造 `.cursor/skills/goal-loop/SKILL.md` 为完整五段式规范（含命令契约 + 状态机 + 五段流程 + 熔断规则 + 业务审计）。
  2. 新增 `ai_workflow/goal_snapshot.py`：会话级 Goal 快照持久化（含 `goal_id` / `raw_user_goal` / `accept_criteria` / `task_queue` / `loop_round` / `last_audit` / `last_review` / `latest_artifact` / `status` / `token_budget` 字段）。
  3. 新增 `ai_workflow/goal_loop_runner.py`：五段式闭环 (Plan → Act → Audit → Review → Iterate) + 三层熔断（最大轮次 / Token / 用户输入阻断）。
  4. 在 `.cursor/hooks.json` 中接入事件驱动：afterShellExecution / afterFileEdit 触发快照读写；sessionStart 触发挂起任务恢复。
  5. 业务审计规则落到 `.cursor/rules/GOAL_BUSINESS_AUDIT.mdc`：FP 中性命名、文本锚点禁止、TP/TC 结构化映射、正反场景冲突检测、L1 轻量化。
  6. 标准化模板：`workflow_assets/goals/<goal_id>/audit_<round>.md` + `review_<round>.md`。
  7. 全量交付文档 `PRODUCT_DOCUMENTATION.md` 增补。
- **非目标**：不修改 AIDocxWorkFlow 9 阶段契约；不创建 Codex 服务端调用；不在文档中虚构「真实 Codex 内部实现」。
- **约束**：遵守项目 DNA / 决策密度上限（每响应 ≤ 3 文件改动）；分 5 轮迭代；每轮必须有自检证据；产物路径遵守项目 Git 分类铁律。
- **验收标准**（可量化）：
  1. SKILL.md 含五段式 + 熔断 + 管控指令 + 业务审计约束的完整规范，验证器扫描通过。
  2. `goal_snapshot.py` 含 10 字段完整 schema，含 `self_test()` 函数，含 atomic write 防丢失。
  3. `goal_loop_runner.py` 实现 Plan→Act→Audit→Review→Iterate 状态机，最大 5 轮、Token 预算、用户输入阻断三项熔断。
  4. `hooks.json` 接入 afterShellExecution / afterFileEdit / sessionStart 三事件，含 goal-loop 调度 handler。
  5. `GOAL_BUSINESS_AUDIT.mdc` 列出 5 条业务审计规则，结构化描述 + 触发方式。
  6. 所有 `.py` 模块通过 `python3 -m py_compile` 语法验证 + `self_test` 运行通过。
  7. `validate_skills.py` 全量扫描 13+ Skill，`0 errors, 0 warnings`。
  8. PROJECT_DOCUMENTATION.md 增补「Goal Loop 自治循环」章节。
- **正确范例**：用 `/goal-loop 创建完整自治循环能力` 作为首个目标任务，锁定本契约 → 5 轮迭代 → 自检收敛。
- **反例**：只重写 SKILL.md 而不落地代码、只写代码不验证语法、虚构 Codex 行为而不标注「本项目设计」。
- **收敛条件**：8 条验收全部 PASS + 每轮决策表落档 + 反模式决策任务关闭。

## 决策表

| 改动 | 文件 | 影响范围 | 替代方案 |
|---|---|---|---|
| 1 | `.cursor/skills/goal-loop/SKILL.md` | Agent 指令层 | A. 整体重写 5 段规范；B. 拼接式追加 |
| 2 | `ai_workflow/goal_snapshot.py` | Agent 运行时 | A. SQLite；B. JSON 文件 + atomic write |
| 3 | `ai_workflow/goal_loop_runner.py` | Agent 运行时 | A. 独立子进程；B. 同步函数链 |
| 4 | `.cursor/hooks.json` | Agent + 平台 | A. 新增事件；B. 复用 afterFileEdit |
| 5 | `.cursor/rules/GOAL_BUSINESS_AUDIT.mdc` | Agent 约束层 | A. 写入现有 .mdc；B. 新建独立规则 |
| 6 | `PRODUCT_DOCUMENTATION.md` | 人 | A. 新增章节；B. 独立 README |

## 状态机

固定 5 段式循环：Plan → Act → Audit → Review → Iterate。

## Round 决策日志

### Round 1 (2026-07-18) — SKILL.md 完整化
- 目标：把当前指令型 SKILL.md 升级为带 5 段式 + 熔断 + 业务审计规范的完整规格
- 操作：扩展 §3 §4 §5 §6 内容，引入 snapshot schema、状态机、模板路径
- 验收：验证器扫描 13 Skill 通过 + 内容自检

### Round 2 (2026-07-18) — 快照持久化
- 目标：实现 goal_snapshot.py 含 10 字段 schema + atomic write
- 操作：JSON 文件 + `.lock` 防并发 + `self_test()`
- 验收：py_compile + self_test 通过

### Round 3 (2026-07-18) — 闭环 runner
- 目标：实现五段状态机 + 三层熔断
- 操作：函数式状态机 + 预算计数 + 用户输入标志
- 验收：py_compile + 状态转移用例通过

### Round 4 (2026-07-18) — Hook 接入
- 目标：让 hook 系统自动驱动循环
- 操作：afterShellExecution/afterFileEdit → 触发 Audit/Iterate；sessionStart → 恢复挂起
- 验收：hooks.json JSON 合法 + handler 自检

### Round 5 (2026-07-18) — 业务审计 + 文档
- 目标：业务审计规则落 .mdc，交付文档补齐
- 操作：5 条规则 + 触发方式 + PRODUCT_DOCUMENTATION.md 新增章节
- 验收：.mdc 结构化 + 文档章节存在

## 落档协议执行记录

- 计划文件：`governance/design_iter/plans/v17/goal_loop_full_delivery_2026_07_18.md`（本文件）
- 实际产物：本记录 + 5 轮改动文件
