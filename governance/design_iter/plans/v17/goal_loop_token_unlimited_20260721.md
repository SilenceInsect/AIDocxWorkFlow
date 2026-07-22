# 决策表：goal-loop token 默认无上限

**日期**：2026-07-21
**触发**：用户输入 `/goal-loop 默认token无上限，除非跑任务的时候特别声明`

---

## 决策

| # | 改动 | 影响范围 | 替代方案 |
|---|---|---|---|
| 1 | `goal_snapshot.py`：`DEFAULT_TOKEN_LIMIT = 200_000` → `UNLIMITED_TOKEN = None`，`create_snapshot` 的 `token_limit` 默认值改为 `None` | 所有新建 goal 的 token 熔断默认失效 | 保持 200K 但改熔断阈值环境变量 |
| 2 | `goal_snapshot.py`：Schema 校验 `token_budget.limit > 0` → `limit is None or limit > 0` | 快照 JSON 可存 `null` | 用 `-1` 代表无上限（不够直观） |
| 3 | `goal_loop_runner.py`：`TOKEN_LIMIT` 环境变量默认值 → `None`（与 `DEFAULT_TOKEN_LIMIT` 对齐） | `iterate()` token 熔断 | 维持 200K 但 skip 检查 |
| 4 | `goal_loop_runner.py`：`iterate()` token 熔断条件改为 `limit is not None and used >= limit` | token 熔断逻辑 | 无 |
| 5 | `goal_loop_breakloop_hook.py`：display 时 `limit is None` 显示"无上限" | breakloop 注入的 reminder 文本 | 无 |
| 6 | `SKILL.md`：更新 token_budget 默认行为说明 | Agent 理解默认行为 | 无 |

## 语义

- `token_limit=None`：不设上限，token 熔断永不触发
- `token_limit=100000`：显式限制 100K，超限触发熔断

## 影响范围

- 现有 snapshot 不受影响（已写死的 limit 值不变）
- 所有新建 goal 默认无 token 上限
- `GOAL_LOOP_TOKEN_LIMIT` 环境变量仍然可用（设为具体数值时生效）

## 执行记录

| 日期 | 改动 | 验证 |
|---|---|---|
| 2026-07-21 | `goal_snapshot.py`：`DEFAULT_TOKEN_LIMIT` → `None` | `py_compile` + self-test 22 cases ✓ |
| 2026-07-21 | `goal_snapshot.py`：Schema `limit` 校验改为 `None or > 0` | 同上 |
| 2026-07-21 | `goal_loop_runner.py`：`TOKEN_LIMIT` 默认 `None` | `py_compile` + self-test 10 cases ✓ |
| 2026-07-21 | `goal_loop_runner.py`：`iterate()` token 熔断加 `limit is not None` 条件 | 同上 |
| 2026-07-21 | `SKILL.md` §4：更新 Token 默认无上限说明 | — |

