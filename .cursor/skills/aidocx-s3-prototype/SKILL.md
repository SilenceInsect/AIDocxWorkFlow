---
name: aidocx-s3-prototype
description: >
  AIDocxWorkFlow Stage 3 — 原型导出。根据 S2 Epic/Story 列表生成页面原型（文本描述 + Mermaid 页面流图）。使用当用户执行 /aidocx-s3-prototype、粘贴 S2 backlog、或进行 S3 原型导出任务。
  Use when the user runs /aidocx-s3-prototype, pastes S2 backlog, or starts prototype export.
  使用当用户执行 /aidocx-s3-prototype、粘贴 S2 backlog、或进行 S3 原型导出任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s3-prototype
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S3 — 原型导出

**独立阶段**：可单独调用。上游材料（S2 backlog）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s3-prototype` 或粘贴 S2 backlog

**前置材料**：S2 backlog.md：`workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.md`

**材料缺失时**：生成失败报告，停止 S3。

---

## §1.4 LLM 必读材料（阶段前置）

**生成原型前，必须先 Read 以下材料。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| 1 | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| UI 模块 Story 对应页面原型；其他模块 Story 生成文本描述 |
| 2 | S2 backlog | `workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.md` | 每个 Story 的功能点是原型生成的核心输入 |

---

## 核心任务

为每个 Story 生成：
1. **文本原型**：页面原型（含关键 UI 元素、状态变化）
2. **Mermaid 页面流图**：页面之间的导航关系

### 原型内容要求

| 要素 | 内容 |
|------|------|
| 页面名称 | 明确的页面/面板名称 |
| 关键UI元素 | 按钮、输入框、显示区、指示器 |
| 布局描述 | 从上到下或从左到右 |
| 状态变化 | 默认、加载中、错误、成功、禁用 |
| 测试隔离点 | 需要特殊状态（如登录态、冷却时间） |

每个 Epic 至少 1 个完整页面流。

---

## 成功产出

路径：`workflow_assets/<req_name>/「S3 原型导出」/<version>/prototype.md`

---

## 失败报告

路径：`workflow_assets/<req_name>/「S3 原型导出」/<version>/fail_report_S3.md`

---

## 自动化支持

```python
from ai_workflow.conversation_skills import save_stage3_output
save_stage3_output(version, breakdown, raw_output, req_name)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S3_PROTOTYPE.mdc`
- Prompt 模板：`ai_workflow/prompts/prototype_export.md`
