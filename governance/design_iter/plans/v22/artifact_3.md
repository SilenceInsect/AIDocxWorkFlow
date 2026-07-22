# Round 3 Artifact — goal_parallel_executor.py v1.2

## 产物路径

`ai_workflow/goal_parallel_executor.py` → 新增

## 变更摘要

### 新增模块结构

| 类/函数 | 行数 | 用途 |
|---|---|---|
| `TaskNode` dataclass | ~15 | DAG 节点（对应 task_queue 单任务） |
| `ParallelGroup` dataclass | ~10 | 并行批次 |
| `SubagentResult` dataclass | ~10 | subagent 执行结果 |
| `CyclicDependencyError` | ~5 | 循环依赖异常 |
| `_build_dag()` | ~20 | DAG 构建 |
| `_compute_in_degree()` | ~15 | 入度计算 |
| `_detect_cycle()` | ~25 | DFS 环检测 |
| `detect_parallelizable()` | ~40 | 核心：分组检测 |
| `GoalParallelExecutor` | ~60 | 主类 |
| `self_test()` | ~70 | 8 个案例 |
| CLI `_cli()` | ~20 | detect 子命令 |

### 核心算法

1. **DAG 构建**：扫描 task_queue，构建 task_id→节点 + 依赖边
2. **环检测**：DFS 三色标记（White/Gray/Black）
3. **拓扑排序**：BFS 入度归零批次调度
4. **并行分组**：入度=0 + parallelizable=true → 真正并行分组

### 并行约束（§11.4）

- `MAX_CONCURRENT_SUBAGENTS = 5`（常量）
- `DEFAULT_SUBAGENT_BUDGET = 50_000`（token 预算）

## 产物位置

```
ai_workflow/goal_parallel_executor.py  (v1.2 新增)
```

## 验收证据

- [x] py_compile 通过
- [x] self-test 8/8 通过
- [x] Case 1: 空任务 → 空分组
- [x] Case 2: 单任务 → 串行分组
- [x] Case 3: 两独立并行 → 单并行分组
- [x] Case 4: 串行依赖链 A→B→C → 3 串行分组
- [x] Case 5: 并行+串行混合 → 3 分组
- [x] Case 6: 循环依赖 → CyclicDependencyError
- [x] Case 7: summarize_results 正确更新
- [x] Case 8: can_launch_more 正确判断
