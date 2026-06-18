---
name: aidocx-s5-test-points
description: >
  AIDocxWorkFlow Stage 5 — 测试点生成。模块定义完整见 `.cursor/MODULES.md`（项目级唯一真相源），不重写压缩版。完整类型数量约束见 §1.1 + §1.4 + 各模块 .md 子模板（无硬数字）。
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

**前置材料**：S2 backlog.md + S4 business_flow.md。详见 §1.4 必读材料清单。

**材料缺失时**：生成失败报告，停止 S5。

---

## 8 模块测试类型（**模块 × 类型双维度必填**）

> ⚠️ 模块定义见 [`.cursor/MODULES.md`](../../../MODULES.md)（项目级唯一真相源）。
> 本文件不重写模块表。如模块定义调整，只改 MODULES.md。

### 测试类型枚举

> 完整定义见 [`.cursor/MODULES.md` §4 测试类型矩阵](../../../MODULES.md)。

### 1.2 模块 × 类型 双维度强制判定（S5 误标高发区）

> **每个测试点必须同时回答 2 问**：
> 1. **属于哪个模块？**（8 模块之一）
> 2. **属于哪种类型？**（4 类型之一）
>
> 同一个功能点常跨多模块 → **每个模块都要单独生成 TP**（不是"取主"）

| 场景 | 模块 | 类型 | 备注 |
|------|------|------|------|
| 购买按钮按下响应 | UI | POSITIVE | UI 测样式 |
| 购买按钮调支付接口 | BIZ | POSITIVE | BIZ 测业务 |
| 购买按钮按下报错 Toast | HINT | EXCEPTION | HINT 测提示内容 |
| 购买按钮按下上报日志 | LOG | EXCEPTION | LOG 测埋点 |
| 购买按钮切弱网容错 | SPECIAL | EXCEPTION | SPECIAL 测降级 |
| 红包系统反作弊 | SPECIAL | NEGATIVE | 反作弊校验 |

### 1.3 HINT vs UI 二次判定（**S5 误标高发区**）

> **完整边界规则 + 决策树**见 [`.cursor/MODULES.md` §4.11.2 HINT vs UI 边界](../../../MODULES.md) + [`workflow_assets/module_templates/HINT/O_boundary.md`](../../../workflow_assets/module_templates/HINT/O_boundary.md)。

## §1.4 必读材料与违规认定

> ⚠️ **违反本节禁令 → 产出不合格，必须补读后重新生成。**

### 违规认定（满足任一 → 产出不合格）

- ❌ 未读取本节材料，直接凭印象生成
- ❌ 跳过标注"强制"的材料，用其他来源替代
- ❌ 产出的 module / s4_reference 与材料内容明显不符
- ❌ 用"业务常识"替代必须读取的材料

### 必读材料清单

**生成任何 TP 前，必须先 Read 以下材料。禁止凭印象/常识/历史产物直接生成。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| ① | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| 所有 Epic/Story 必须有模块前缀；模块分类决定后续所有判断 |
| ② | 模块边界区分 | `.cursor/MODULES.md`（§3.5 快速归类表）| 8 模块边界容易混淆（尤其 HINT vs UI、BIZ vs CONFIG），判定前必须读取 |
| ③ | 命中模块概览 | `workflow_assets/module_templates/<Module>/<Module>.md` | 该模块的子类枚举和测试方法决定 TP 类型 |
| ④ | 命中模块边界文件 | `workflow_assets/module_templates/<Module>/O_boundary.md` | 反例库对照，防止模块归属错误 |
| ⑤ | S4 业务流（强制） | `workflow_assets/<req_name>/「S4 流程图导出」/<version>/business_flow.md` | 异常决策树和风险点清单是 EXCEPTION 类型 TP 的核心来源；未读取 → s4_reference 无法填写 |

**判定规则完整见** [MODULES.md §3.5](.cursor/MODULES.md) + [§4.11.2 HINT vs UI 边界](.cursor/MODULES.md)。

### 反例库强制对照

写 TP 前，必须先扫反例库（HINT 误判 1-8 / BIZ 误判 1-10 / UI 误判 1-5 / AUX vs BIZ 误判 5 / LOG 误判 8）：

- 与某反例同 pattern → 改 module 或删除
- 与反例无冲突 → 记录"与反例 N 无冲突"
- LLM 必须在 TP JSON 的 `applies_rule` 字段里声明反例对照结果

---

## 决策 push 块

> **哲学**：不告诉 LLM 多少算合格，告诉 LLM 怎么思考产出质量。
>
> ⚠️ **未走 Push 即写 TP → 该 TP 不合格。**

### 跨模块拆分 push

写 TP 前先问自己 3 问：

- Q1. 这个 Story 的"业务流"是单系统还是涉及上下游/第三方？（如购买涉及支付/订单/邮件）
- Q2. "业务流"的数据/状态变化会触发哪些 UI/HINT/LOG 反馈？
- Q3. 这个 Story 是否会暴露配置/缓存/异常/合规风险？

**3 问任一为"是"→ 必须为该模块单独生成 TP，不偷懒合并。**

### 4 步判定 push

每个 TP 写之前必走 4 步（任一空答 → 暂停，先补 Read）：

| # | 操作 | 目的 |
|---|------|------|
| Push 1 | 读 MODULES.md §3.5，找命中模块（8 选 1） | 确认模块归属 |
| Push 2 | 读命中模块的 `<MODULE>.md`，找命中子类 | 确认类型枚举 |
| Push 3 | 读命中模块的 `O_boundary.md`，确认不与相邻模块冲突 | 边界 guard |
| Push 4 | 读 S4 业务流，找对应 F-XX 节点/异常树叶子/R-XX 风险点 | 填写 s4_reference |

**4 步全部回答后，再开始写 TP。** LLM 必须在 TP JSON 的 `applies_rule` 字段里说明走了哪 4 步。

### is_assumed 强制要求

> 定义见 [`.cursor/MODULES.md`](../../../MODULES.md)（全局强制）。

### 反例库强制对照

> 定义见 [`.cursor/MODULES.md`](../../../MODULES.md) 各模块 O_boundary.md。

### JSON Schema 字段名强约束

> 定义见各阶段 SKILL.md。

### 5 问质量 push

> ⚠️ **5 问任一空答 → TP 不合格，删除或重写。**

| # | 问题 |
|---|------|
| Q1 | 测什么（明确场景）？ |
| Q2 | 命中哪个模块 + 哪个子类（精确不模糊）？ |
| Q3 | 边界值/异常输入是什么（具体不抽象）？ |
| Q4 | 预期结果可验证吗（pass/fail 明确）？ |
| Q5 | 对应 S4 哪个节点（链路可追溯）？ |

---

## 成功产出

路径：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json`

---

## 失败报告

路径：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/fail_report_S5.md`

---

## 自动化支持

```python
from ai_workflow.test_case_formatter import compose_test_points_from_structure
breakdown = {'epics': [...], '_version': 'v1.0'}
skeleton = compose_test_points_from_structure(breakdown)
# skeleton 中每个 Story 仅含原始字段
# scenario_test_points: [] — LLM 按 §1.4 推理填入，4 类型必填 + s4_reference 必填

# 保存（LLM 手工 write_file）
# 输出: workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S5_TEST_POINTS.mdc`
- Prompt 模板：`ai_workflow/prompts/test_point_gen.md`
- 测试点库：`workflow_assets/test_point_library/`
- 示例参考：`workflow_assets/example_test_points/`

