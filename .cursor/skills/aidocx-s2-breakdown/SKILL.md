---
name: aidocx-s2-breakdown
description: AIDocxWorkFlow Stage 2 — 需求拆解。将需求拆解为 Epic → Story → 需求对象 → 功能点四层，包含对象状态、交互形态、业务逻辑、异常边界、异常交互、关联模块、日志埋点、关联协议。使用当用户执行 /aidocx-s2-breakdown、粘贴 S1.5 准出许可路径、或进行 S2 需求拆解任务。
disable-model-invocation: true
---

# AIDocxWorkFlow S2 — 需求拆解

**独立阶段**：可单独调用。上游材料（S1.5 准出许可）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发方式**：`/aidocx-s2-breakdown` 或粘贴 S1.5 准出许可路径

**前置材料**：
- 终版需求.md：`workflow_assets/<req_name>/「S1 需求评审」/<version>/终版需求.md`
- S1.5 准出许可：`workflow_assets/<req_name>/「S1 需求评审」/<version>/exit_permission.json`
- clarification_checklist.md：`workflow_assets/<req_name>/「S1 需求评审」/<version>/clarification_checklist.md`

**材料缺失或 `can_proceed_to_s2 == false` 时**：生成失败报告，停止 S2。

---

## 核心升级：四层拆解

S2 的拆解深度为 **Epic → Story → 需求对象 → 功能点** 四层，为 S3 迭代规划和 S5/S6 测试用例设计提供充足物料：

```
Epic
 └─ Story × N
     └─ 需求对象 × M（每个 Story 1-5 个）
         ├─ 对象状态拆解（正常态 / 异常态 / 边界态）
         ├─ 交互形态（界面操作 / API 调用 / 系统事件 / 定时任务）
         ├─ 业务逻辑（输入→处理规则→输出）
         ├─ 异常业务边界（超限 / 空值 / 冲突 / 幂等）
         ├─ 异常交互（超时 / 重试 / 降级 / 兜底 UI）
         ├─ 关联模块推理（主模块 + 辅助模块，CONFIG/UI/BIZ/AUX/LINK/SPECIAL/LOG）
         ├─ 日志与埋点（事件名→触发时机→字段列表）
         ├─ 关联协议（协议名→调用方→接收方→关键字段）
         └─ 功能点 × K（每个需求对象 3-8 个）
             ├─ 功能名称
             ├─ 分类维度（业务分类标签）
             ├─ 分类边界（边界值 / 等价类 / 异常触发条件）
             ├─ 测试类型（正向 / 逆向 / 边界 / 异常）
             ├─ 前置条件 / 输入 / 预期输出
             └─ 优先级 P0 / P1 / P2
```

---

## 8 模块系统

| 模块 | 前缀 | 描述 |
|------|------|------|
| 配置 | CONFIG | 游戏数据配置表重载/字段校验/一致性 |
| 界面 | UI | UI控件、纯前端交互、布局/兼容性 |
| 业务 | BIZ | 核心业务逻辑、数据流、协议交互 |
| 辅助 | AUX | 公共工具、网络层、资源管理 |
| 关联 | LINK | 外部API、数据同步、多端一致性 |
| 特殊情境 | SPECIAL | 边界情况、异常处理、反作弊安全 |
| 日志 | LOG | 行为日志、审计追踪 |
| 基础 | BASE | 未分类 Epics（尽量避免） |

---

## 拆解规则

### Epic
- 粒度：1-4 周，格式 `{Module}-{Number}`，如 `CONFIG-001`

### Story
- 粒度：1-3 人天，格式 `{EpicID}-{StoryNumber}`，如 `CONFIG-001-001`
- 必填字段：`id`、`title`、`acceptance_criteria`（至少2条）、`precondition`、`input_data`、`expected_output`

### 需求对象
- 粒度：每个 Story 拆 1-5 个
- 格式：`{StoryID}-OBJ-{N}`，如 `CONFIG-001-001-OBJ-1`
- 必填字段：9 个字段（见上方核心升级）

### 功能点
- 粒度：每个需求对象 3-8 个
- 格式：`{需求对象ID}-FP-{N}`，如 `CONFIG-001-001-OBJ-1-FP-1`

### 分类边界找不到时
- 标注 `[待确认]` 并列出候选边界及不确定原因，**不要跳过**

---

## 成功产出

| 文件 | 路径 |
|------|------|
| backlog.md | `workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.md` |
| backlog.json | `workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.json` |
| requirement_objects.md（新增） | `workflow_assets/<req_name>/「S2 需求拆解」/<version>/requirement_objects.md` |
| requirement_objects.json（新增） | `workflow_assets/<req_name>/「S2 需求拆解」/<version>/requirement_objects.json` |

---

## 失败报告

路径：`workflow_assets/<req_name>/「S2 需求拆解」/<version>/fail_report_S2.md`

---

## 自动化支持

```python
from ai_workflow.conversation_skills import save_stage2_output
save_stage2_output(version, req_text, raw_output, parsed, req_name)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S2_BREAKDOWN.mdc`
- Prompt 模板：`ai_workflow/prompts/requirement_breakdown.md`
