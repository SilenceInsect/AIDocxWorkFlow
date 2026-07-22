# Round 4 Artifact — goal_snapshot.py v3.1 + session_resume_multi_goal.py

## 产物路径

- `ai_workflow/goal_snapshot.py` → v3.1
- `.cursor/hooks/session_resume_multi_goal.py` → 新增

## 变更摘要

### goal_snapshot.py v3.1

| 变更点 | 详情 |
|---|---|
| Schema 版本 | v1.1 → v1.2（19 字段） |
| SNAPSHOT_FIELDS | 新增 `parallel_executor_hints` 字段 |
| `create_snapshot()` | 初始化 `parallel_executor_hints = {}` |
| `_migrate_legacy_snapshot()` | 追加 `parallel_executor_hints` 和 `task_queue` 向前兼容填充 |
| `_validate_snapshot()` | 新增 `parallel_executor_hints` dict 类型校验 |
| `load_all_active_snapshots()` | 新增函数（v1.2 跨 Round 并行支持）|
| docstring | 更新为 v3.1 + 19 字段列表 |
| self_test | 追加 Case 21 + 22（v1.2 新增） |

### session_resume_multi_goal.py（新增）

| 功能 | 详情 |
|---|---|
| `handle_session_start_multi_goal()` | 主 handler：读取所有 active goal，按 goal_id 分组注入 reminder |
| `_build_goal_reminder()` | 为单个 goal 构建续跑文本（含 pending tasks + 并行分组信息）|
| 多 goal 支持 | ≥2 goals 时注入多 goal reminder（含数量标注 + 分隔符）|
| 轮次排序 | 按 loop_round 降序排列（轮次高的优先）|
| self_test | 5 个案例（空 stdin / 无 active / 单 goal / 多 goal / 未知事件）|

## 产物位置

```
ai_workflow/goal_snapshot.py  (v3.1, 19 字段)
.cursor/hooks/session_resume_multi_goal.py  (v1.2 新增)
```

## 验收证据

- [x] goal_snapshot.py --self-test 22/22 通过
- [x] session_resume_multi_goal.py --self-test 5/5 通过
- [x] load_all_active_snapshots() 返回完整 snapshot（含 task_queue + parallel_executor_hints）
- [x] SNAPSHOT_FIELDS = 19
- [x] _migrate_legacy_snapshot 向前兼容填充 parallel_executor_hints
