---
name: aidocx-s5-test-points
description: >
  AIDocxWorkFlow Stage 5 — 测试点生成。为每个 Story 生成测试点，覆盖7模块系统（CONFIG/UI/BIZ/HINT/LINK/SPECIAL/LOG），每个 Story ≥ 6 个测试点（2正向+2边界+1负向+1异常）。使用当用户执行 /aidocx-s5-test-points、粘贴 S2 backlog、或进行 S5 测试点生成任务。
  Use when the user runs /aidocx-s5-test-points, pastes S2 backlog, or starts test point generation.
  使用当用户执行 /aidocx-s5-test-points、粘贴 S2 backlog、或进行 S5 测试点生成任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s5-test-points
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S5 — 测试点生成

**独立阶段**：可单独调用。上游材料（S2 backlog）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s5-test-points` 或粘贴 S2 backlog

**前置材料**：
- S2 backlog.md：`workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.md`
- S4 business_flow.md（**强烈推荐参考**）：`workflow_assets/<req_name>/「S4 流程图导出」/<version>/business_flow.md`
  - 包含异常/错误决策树和风险点清单，用于补充 EXCEPTION 类型测试点
  - 若 S4 未执行，EXCEPTION 测试点需自行推导异常路径，可能遗漏风险场景

**材料缺失时**：生成失败报告，停止 S5。

---

## 7模块测试类型

| 模块 | 前缀 | 必须覆盖的测试类型 |
|------|------|------------------|
| CONFIG | 配置 | RELOAD_4_MODE、FIELD_LEGALITY、FIELD_INTRA_DEP、FIELD_CROSS_DEP |
| UI | 界面 | CONTROL_EXISTENCE、LAYOUT、RESOLUTION_COMPAT、INTERACTION |
| BIZ | 业务 | ACTIVITY_OPEN/CLOSE、PROTOCOL、ENTITY_CACHE、DB_PERSIST |
| HINT | 提示 | RED_DOT、ITEM_FLOAT、CURRENCY_FLOAT、SYS_MSG |
| LINK | 关联 | CORRELATION_TEST、REGRESSION_TEST |
| SPECIAL | 特殊情境 | DUPLICATE_PACKET、HIGH_FREQ_PACKET、WEAK_NETWORK、SWITCH_TO_BACKGROUND |
| LOG | 日志 | ASSET_CHANGE、PROGRESS_TRIGGER、ANOMALY |

---

## 每个 Story 必须生成

| 类型 | 数量 | 说明 |
|------|------|------|
| POSITIVE（正向） | ≥ 2 | 正常流程测试 |
| BOUNDARY（边界值） | ≥ 2 | 边界条件测试 |
| NEGATIVE（负向） | ≥ 1 | 异常输入测试 |
| EXCEPTION（异常） | ≥ 1 | 系统异常处理测试 |

**ID 格式**：`{StoryID}-TP-{3位序号}`，如 `UI-001-001-TP-001`

---

## 成功产出

路径：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json`

---

## 失败报告

路径：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/fail_report_S5.md`

---

## 自动化支持

```python
from ai_workflow.test_case_formatter import compose_test_points_from_structure, _build_fallback_scenarios
breakdown = {'epics': [...], '_version': 'v1.0'}
skeleton = compose_test_points_from_structure(breakdown)
# skeleton 中每个 Story 有 module + 真实测试点内容

from ai_workflow.conversation_skills import save_stage5_output
save_stage5_output(version, breakdown, flowchart_text, raw_output, parsed, req_name)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S5_TEST_POINTS.mdc`
- Prompt 模板：`ai_workflow/prompts/test_point_gen.md`
- 测试点库：`workflow_assets/test_point_library/`
- 示例参考：`workflow_assets/example_test_points/`
