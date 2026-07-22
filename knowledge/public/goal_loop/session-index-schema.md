# Goal Loop session-index Schema 说明

> **文件版本**：v1.0
> **路径**：`knowledge/public/goal_loop/session-index-schema.md`
> **用途**：session-index.jsonl 索引记录的结构说明与效能统计字段规范
> **关联**：goal_snapshot.py `_append_session_index()`

---

## 索引记录结构

每条记录（JSONL 单行）：

```json
{
  "goal_id": "uuid-v4",
  "action": "create | update",
  "timestamp": "ISO8601",
  "round": 0,
  "status": "active | achieved | converged_with_followup | paused | budget-limited",
  "rounds_to_convergence": 3,       // v1.1 GL-008，收敛时填入
  "first_pass_rate": 0.67,          // v1.1 GL-008，首轮通过率
  "blocker_residual_rate": 0.0,     // v1.1 GL-008，BLOCKER 遗留率
  "avg_round_duration_seconds": 120  // v1.1 GL-008，平均单轮耗时
}
```

## 字段说明

| 字段 | 类型 | 含义 | 填充时机 |
|---|---|---|---|
| `goal_id` | string | Goal 唯一 ID | 每次操作 |
| `action` | enum | 操作类型 | 每次操作 |
| `timestamp` | string | ISO 8601 时间戳 | 每次操作 |
| `round` | int | 当前轮次 | 每次操作 |
| `status` | enum | Goal 状态 | 每次操作 |
| `rounds_to_convergence` | int | 收敛总轮次 | 收敛时（achieved / converged_with_followup） |
| `first_pass_rate` | float | 首轮通过率 | 收敛时 |
| `blocker_residual_rate` | float | BLOCKER 遗留率 | 收敛时 |
| `avg_round_duration_seconds` | float | 平均单轮耗时（秒） | 收敛时 |

## 效能统计字段（v1.1 GL-008）

收敛时由 `update_efficiency_stats()` API 写入 session-index.jsonl，供后续聚合分析。

每月自动生成体系效能报告：
- 收敛轮次趋势（平均值/中位数/最大值）
- 首轮通过率趋势
- BLOCKER 遗留率趋势
- 高频 BLOCKER 类型 Top-N
