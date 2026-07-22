# Round 5 Artifact — tests/test_goal_parallel.py

## 产物路径

`tests/test_goal_parallel.py` → 新增

## 测试覆盖

| 测试类 | 案例 | 覆盖内容 |
|---|---|---|
| TestParallelDependencyResolution | T1-1~T1-6 | 空任务 / 单任务串行 / 两并行 / 串行链 / 混合 / 循环依赖 |
| TestSubagentBudgetLimit | T2-1~T2-3 | can_launch_more / at-limit / MAX_CONCURRENT=5 |
| TestGoalSnapshotIsolation | T3-1~T3-3 | 两 goal 独立 / parallel_executor_hints 初始化 / task_queue 存在 |
| TestAsyncHookTrigger | T4-1~T4-2 | hook queue 文件写 / sessionStart reminder 注入 |
| TestDAGEdgeCases | T5-1~T5-4 | 缺失依赖忽略 / 全并行 / execute_parallel / summarize_results |
| TestCLI | T6-1 | detect CLI --json-output |

## 运行结果

```
Ran 19 tests in 0.097s — OK
```

## 产物位置

```
tests/test_goal_parallel.py  (v1.2 新增，19 个测试案例)
```

## 验收证据

- [x] python3 tests/test_goal_parallel.py → 19/19 OK
- [x] T1~T6 全覆盖（并行解析 / subagent 上限 / goal 隔离 / 异步 hook / DAG 边界 / CLI）
