# goal-loop model 切换可行性分析与修复决策

**创建时间**：2026-07-18 23:47  
**关联 Goal**：v17 goal-loop自治循环收敛  
**问题**：用户启动 /goal-loop 后，agent model 没有自动切换

---

## 1. 根因分析

### 1.1 误解来源

SKILL.md 第7行存在误导性元数据：

```yaml
disable-model-invocation: true
```

这个字段的含义是「禁止此 Skill 调用其他模型」，但用户期望的是「启动 goal-loop 后自动切换 agent model」。两者是完全不同的概念。

### 1.2 正确理解

**Skill 机制真相**：
- Skill 本质是「指令集」——用户调用 `/goal-loop` → Agent 读取 SKILL.md → 按五段式执行指令
- Cursor Agent **没有公开的 Skill → model 切换 API**
- `disable-model-invocation: true` 是 Skill 元数据字段，告诉 Cursor「不要用其他模型执行这个 Skill 的指令」

**当前 breakloop hook 实际功能**：
- `afterAgentResponse` → 检测响应是否含 CONVERGED/BLOCKED → 注入续跑 reminder
- `sessionStart` → 读取 active snapshot → 注入「请继续 Act」提示
- **不负责 model 切换**

### 1.3 当前 snapshot 状态

| 字段 | 值 |
|---|---|
| goal_id | 09cdc9e7-fc91-4a88-a391-51af56767806 |
| status | achieved（第4轮已收敛） |
| loop_round | 4 |
| latest_artifact | governance/design_iter/plans/v17/CONVERGED.md |
| last_audit | audit_4.md |
| last_review | review_4.md |

---

## 2. 可行性分析

### 2.1 Cursor SDK 分析

根据 `sdk/SKILL.md`：

```python
from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

result = Agent.prompt(
    "执行 goal-loop",
    AgentOptions(
        api_key=os.environ["CURSOR_API_KEY"],
        model="composer-2.5",  # 可指定模型
        local=LocalAgentOptions(cwd=os.getcwd()),
    ),
)
```

**可行性**：✅ Cursor SDK 支持在创建 agent 时指定 model

**限制**：
1. SDK 是在 **Cursor IDE 外部** 创建 agent，需要 `CURSOR_API_KEY`
2. SDK agent 与 **当前 IDE 会话内的 agent** 是两个独立实例
3. **没有公开 API 可以控制 IDE 内已运行的 agent 的 model**

### 2.2 结论

| 方案 | 可行性 | 说明 |
|---|---|---|
| A. 规范文档修复 | ✅ 可行 | 移除误导性字段，澄清 goal-loop 机制 |
| B. 实现 model 切换 | ❌ 不可行 | Cursor Agent 无公开 API 控制 IDE 内 agent 的 model |
| C. SDK 外部 agent | ✅ 但不可行 | SDK agent 是独立实例，无法影响当前 IDE 会话 |

**最终判定**：只执行方案 A（规范文档修复），方案 B 标注为「Cursor 平台限制，待 SDK/API 支持后实现」

---

## 3. 修复决策

### 3.1 修改清单

| 文件 | 修改内容 | 严重度 |
|---|---|---|
| `.cursor/skills/goal-loop/SKILL.md` | 移除 `disable-model-invocation: true`；在 §1 澄清 goal-loop 是指令集不是模型切换器 | 规范修复 |
| 本文件 | 落档决策结果 | 记录 |

### 3.2 SKILL.md 修改点

**删除**：
```yaml
disable-model-invocation: true
```

**新增**（§1 命令契约末尾）：

```markdown
> **机制说明**：`/goal-loop` 是 Agent 指令集触发器，不是模型切换器。
> - 用户调用 `/goal-loop` → Agent 读取 SKILL.md → 按五段式执行
> - breakloop hook 负责「检测目标完成状态并注入续跑 reminder」
> - Cursor Agent 无公开 API 可在运行时切换已运行 agent 的 model
> - 若需在独立进程中用指定 model 执行 goal-loop，使用 Cursor SDK
```

---

## 4. 遗留问题

| ID | 描述 | 状态 | 备注 |
|---|---|---|---|
| Q-LOOP-001 | agent model 运行时切换 | 待实现 | 依赖 Cursor 平台支持 |


---

## 5. 修复执行记录

| 时间 | 操作 | 结果 |
|---|---|---|
| 2026-07-18 23:47 | 创建本决策表 | 完成 |
| 2026-07-18 23:48 | 修复 SKILL.md | ✅ 完成 |
| 2026-07-18 23:48 | 修复 SKILL.md §1 添加机制说明 | ✅ 完成 |
| 2026-07-18 23:49 | hook self-test | ✅ 9 cases passed |
| 2026-07-18 23:50 | 更新决策表 | ✅ 完成 |
