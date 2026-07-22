# Round 2 Artifact — goal_loop_breakloop_hook.py v3

## 产物路径

`.cursor/hooks/goal_loop_breakloop_hook.py` → v3

## 变更摘要

### v3 新增功能

1. **`--async-mode` argv 支持**：作为 subagent worker 独立运行，读取 queue 文件执行
2. **`--queue-file` argv**：指定要处理的 queue 文件路径
3. **`HOOK_QUEUE_DIR`**：`.goal-log-db/hook-queue/` 异步任务持久化目录
4. **`_spawn_async_subagent()`**：写 queue 文件 + spawn detached subprocess
5. **`_write_hook_queue_file()`**：写异步触发 JSON 到 hook queue
6. **`handle_after_file_edit()`**：afterFileEdit handler（v3 新增，异步）
7. **`handle_after_shell_execution()`**：afterShellExecution handler（v3 新增，异步）
8. **`handle_after_agent_response_async()`**：异步版 afterAgentResponse
9. **`async_worker()`**：--async-mode subagent worker 函数
10. **`_process_hook_queue()`**：sessionStart 时处理 hook queue

### v3 保留功能（v2 兼容）

- `handle_after_agent_response_sync()`：同步版（默认），保留 7 个 self-test 案例
- 双门判定逻辑：门 A（字面）+ 门 B（数据）
- `_has_done_declaration()` / `_audit_supports_done()`
- `handle_session_start()`：snapshot 可读性验证

### 向后兼容

- `--self-test` 行为不变（9 个案例）
- 无 `--async-mode` 时默认走同步路径（v2 兼容）
- 无 active goal → exit 0（无噪声）

## 产物位置

```
.cursor/hooks/goal_loop_breakloop_hook.py  (v3)
```

## 验收证据

- [x] py_compile 通过
- [x] v2 全部 7 个 self-test 案例保留
- [x] v3 新增 2 个 handler（afterFileEdit / afterShellExecution）
- [x] --async-mode + --queue-file argv 支持
- [x] hook queue 持久化（JSON 文件）
- [x] _spawn_async_subagent 立即返回（不阻塞）
