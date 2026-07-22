# Round 1 Artifact — SKILL.md v1.2 扩展

## 产物路径

`.cursor/skills/goal-loop/SKILL.md` → v1.2

## 变更摘要

### §1 元数据变更
- `spec_version`: `agentskills.io/1.1` → `agentskills.io/1.2`
- description 新增：`v1.2 新增：三层并行化规范...`

### §2 Schema 扩展
- `task_queue` 新增字段：`parallelizable` / `depends_on` / `parallel_group` / `subagent_budget_used`
- 新增字段：`parallel_executor_hints`（并行化建议）
- 新增 §2.5：`task_queue` 并行化字段详解（含依赖解析算法）
- 新增 §2.6：`parallel_executor_hints` 结构定义

### §3.2 Act 执行
- 新增"子任务并行化"子节（v1.2 新增）
- 说明分组调度 / 并行执行 / 结果汇总 / 审计前置流程
- 并行约束：subagent ≤ 5、独立 token 追踪、跨 goal 依赖显式声明

### §8 事件驱动
- 更新 `afterFileEdit` / `afterShellExecution` 描述：标注"异步 subagent 执行"
- 新增 `afterAgentResponse` 行：触发异步 subagent 跑反模式检测 + breakloop 判定
- 新增 v1.2 Hook 层异步规范段落

### §10.4 跨平台兼容性
- 新增"并行能力"列
- Codex CLI 标注"降级为串行"
- Cursor Agent / Claude Code / Hermes Agent 标注 Task 工具并行

### §11 并行化规范（新增章节）
- §11.1 Round 内并行（Act 层）：DAG 依赖解析 + 并行分组执行
- §11.2 跨 Round 并行（Goal 级）：多 goal 共存 + sessionStart 恢复
- §11.3 Hook 层异步：3 类事件异步 subagent 触发
- §11.4 并行约束：5 大约束（subagent 上限 / token 追踪 / 跨 goal 依赖 / 循环依赖检测 / 向后兼容）
- §11.5 向后兼容性：v1.1 快照兼容 / 无并行字段降级串行 / hook 无噪声

## 产物位置

```
.cursor/skills/goal-loop/SKILL.md  (v1.2)
```

## 验收证据

- [x] `spec_version: agentskills.io/1.2`
- [x] §2 新增 2 个并行化字段 + 2 个新子节
- [x] §3.2 新增"子任务并行化"子节
- [x] §8 3 类事件标注异步
- [x] §10.4 新增并行能力列
- [x] §11 新增 5 个子节（§11.1~§11.5）
