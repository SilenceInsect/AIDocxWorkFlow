# v33 Plan — aidocx-workflow-conversation 加速方案

> **目标**：审查 `aidocx-workflow-conversation` 全流程实现，给出加速方案
> **版本**：v33
> **日期**：2026-07-21
> **目标闭环**：goal-loop 自治循环
> **迭代上限**：5 轮

---

## 1. 原始目标

```
/goal-loop /aidocx-workflow-conversation 审查全流程实现，给出加速的方案
```

---

## 2. 验收标准（Accept Criteria）

| # | 标准 | 验证方式 |
|---|---|---|
| AC1 | 识别 `aidocx-workflow-conversation` SKILL.md §10 的所有实现断点 | Read conversation_skills.py 验证 |
| AC2 | §10.1 已在 `run_pipeline()` 中实现（goal/accept_criteria 参数 + 五段式驱动） | Read conversation_skills.py 验证 |
| AC3 | goal-loop runner 已在 conversation_skills 中正确调用 | grep goal_loop_runner 验证 |
| AC4 | hooks.json 中无重复注册，已注册的 handlers 与 skill §8 事件映射一致 | Read hooks.json 验证 |
| AC5 | 并行执行器（goal_parallel_executor）已在 Act 阶段可调用 | Read goal_parallel_executor.py 验证 |
| AC6 | 加速方案已落档（governance/design_iter/plans/v33/ 方案 MD） | ls governance/design_iter/plans/v33/ |

---

## 3. task_queue

| ID | 任务 | 依赖 | 状态 |
|---|---|---|---|
| T-001 | 读取并审查全流程实现 | — | pending |
| T-002 | 识别 §10 描述与实际实现的断点 | T-001 | pending |
| T-003 | 制定加速方案（补实现断点） | T-002 | pending |
| T-004 | 落档加速方案到 governance/design_iter/plans/v33/ | T-003 | pending |

---

## 4. 全局约束（锁定）

### 4.1 历史坑点

- **v17.1 DT F2**：goal-loop 禁止跳轮，每轮必须产出 `audit_<round>.md` + `review_<round>.md`
- **v26 D1**：value_ratio < 0.6 在 `create_snapshot` 时触发 `ValueRatioError`（启动硬约束）
- **v18 Fix-2**：PARTIAL 等价 UNKNOWN 处理，不能算通过
- **v20 Fix-1**：achieved 时必须将 `last_audit` 显式回写快照

### 4.2 禁止行为

- 不修改 `goal_snapshot.py` 的核心 Schema（20 字段已稳定）
- 不在 `hooks.json` 中引入未测试的 handler
- 不在 `conversation_skills.py` 中引入未处理的 `goal=None` 分支以外的代码路径

---

## 5. 正确范例

本 goal-loop 执行自身作为验证：用 goal-loop 审查 goal-loop 实现，产出 audit + review，识别 §10 描述与实际代码的断点，给出加速方案。

---

## 6. 加速方案（待 Act 阶段填充）

> **§6 由 Act 阶段填充——基于 T-002 的审查结论**

---

## 7. 遗留问题

| # | 问题 | 严重度 | 备注 |
|---|---|---|---|
| Q-001 | §10.1 `run_pipeline(goal=...)` 实际未在 conversation_skills.py 中实现 | MAJOR | skill 说"进入 goal-loop 模式"，但代码没有该参数 |
| Q-002 | goal-loop runner（GoalLoop）未在 conversation_skills.py 中被调用 | MAJOR | 五段式只存在于 SKILL.md 描述，不存在于代码 |
| Q-003 | hooks.json 中 `afterShellExecution` 只注册了 `goal_loop_hook.py`（旧版），未注册 `goal_loop_breakloop_hook.py` | MINOR | breakloop hook 注册在 `afterAgentResponse`，不是 `afterShellExecution` |
| Q-004 | `afterFileEdit` 和 `afterShellExecution` handlers 在 breakloop hook 中只写 queue，不真正触发 Audit | MAJOR | async_worker 注入的是"建议 Audit"文本，不是真正跑 audit 逻辑 |
| Q-005 | parallel_executor 存在于代码但从未在 conversation_skills 中被调用 | MINOR | Act 阶段没有 DAG 并行执行能力 |

