---
name: aidocx-s4-flowchart
description: >
  AIDocxWorkFlow Stage 4 — 流程图导出。为每个 Epic 生成业务流程图（Flowchart）、时序图（Sequence）、异常/错误决策树、风险点清单。使用当用户执行 /aidocx-s4-flowchart、粘贴 S2 backlog + S3 prototype、或进行 S4 流程图导出任务。
  Use when the user runs /aidocx-s4-flowchart, pastes S2 backlog + S3 prototype, or starts flowchart export.
  使用当用户执行 /aidocx-s4-flowchart、粘贴 S2 backlog + S3 prototype、或进行 S4 流程图导出任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s4-flowchart
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S4 — 流程图导出

**独立阶段**：可单独调用。上游材料（S2 backlog + S3 prototype）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s4-flowchart` 或粘贴 S2 backlog + S3 prototype

**前置材料**：
- S2 backlog.md：`workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.md`
- S3 prototype.md（可选）：`workflow_assets/<req_name>/「S3 原型导出」/<version>/prototype.md`

**材料缺失时**：生成失败报告，停止 S4。

---

## 核心任务

为每个 Epic 生成：

1. **Mermaid 业务流程图**（Flowchart）
2. **Mermaid 时序图**（Sequence Diagram）
3. **异常/错误决策树**
4. **风险点清单**

风险点关注：竞态条件、时间依赖、状态损坏场景、支付幂等性。

---

## 成功产出

路径：`workflow_assets/<req_name>/「S4 流程图导出」/<version>/business_flow.md`

---

## 失败报告

路径：`workflow_assets/<req_name>/「S4 流程图导出」/<version>/fail_report_S4.md`

---

## 自动化支持

```python
from ai_workflow.conversation_skills import save_stage4_output
save_stage4_output(version, breakdown, prototype_text, raw_output, req_name)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S4_FLOWCHART.mdc`
- Prompt 模板：`ai_workflow/prompts/flowchart_export.md`
- 流程图模板库：`workflow_assets/flowchart_library/`
