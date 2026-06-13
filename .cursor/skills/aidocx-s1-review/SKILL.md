---
name: aidocx-s1-review
description: >
  AIDocxWorkFlow Stage 1 — 需求评审。执行需求文档的5维度评审（完整性/清晰度/一致性/可测试性/可行性），输出评分与判决（PASS/NEEDS_REVISION/REJECT）。使用当用户执行 /aidocx-s1-review、粘贴原始需求、或进行 S1 需求评审任务。
  Use when the user runs /aidocx-s1-review, pastes raw requirements, or starts a Stage 1 review task.
  使用当用户执行 /aidocx-s1-review、粘贴原始需求文档、或进行 S1 需求评审任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s1-review
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S1 — 需求评审

**独立阶段**：可单独调用。丢入材料 → 审查材料 → [合格] 开始评审产出 / [不合格] 生成失败报告。

---

## 阶段入口

**触发**：`/aidocx-s1-review` 或直接粘贴需求文本

**前置检查**：用户在丢入材料后，AI 先审查材料完整性，再决定是否开始评审。

---

## 输入审查（门禁前置）

| 检查项 | 要求 | 缺失时 |
|--------|------|--------|
| 用户角色定义 | 至少1类角色 | 标记缺失，提示补充 |
| 功能描述 | 有具体功能点描述 | 标记缺失 |
| 量化指标 | 性能/数量有具体数值 | 允许为空但标注 |
| 验收标准 | 有可验证的通过条件 | 标记缺失 |

---

## 5维度评审

| 维度 | 权重 | 评审要点 |
|------|------|----------|
| 完整性 | 25% | 用户角色、功能描述、非功能约束、验收标准是否齐全 |
| 清晰度 | 25% | 无模糊术语、有量化指标、术语定义一致 |
| 一致性 | 20% | 内部无矛盾、无重叠/冲突的功能描述 |
| 可测试性 | 20% | 每个验收标准有明确通过/失败条件 |
| 可行性 | 10% | 技术约束已识别，无未定义的外部依赖 |

---

## 判决规则

| 总分 | 判决 | 后续动作 |
|------|------|----------|
| ≥ 7.0 | **PASS** | 进入 S2 |
| 4.0 – 6.9 | **NEEDS_REVISION** | 输出修改建议，等待修订后重审 |
| < 4.0 | **REJECT** | 输出失败报告，停止流水线 |

---

## 成功产出

路径：`workflow_assets/<req_name>/「S1 需求评审」/<version>/review_report.md`

报告内容：评分表 → 缺失信息 → 冲突项 → 待确认问题 → 优先级建议 → 总结

---

## 失败报告

路径：`workflow_assets/<req_name>/「S1 需求评审」/<version>/fail_report_S1.md`

报告内容：失败原因（缺失材料/冲突项/不可行要求）→ 修改建议（阻断/可选）→ 后续动作

---

## 自动化支持

```python
from ai_workflow.requirement_reviewer_auto import auto_review_requirement
result = auto_review_requirement(requirement_text)
# result['verdict'] ∈ {'PASS', 'NEEDS_REVISION', 'REJECT'}
# result['score_total'] ∈ [0.0, 10.0]
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S1_REVIEW.mdc`
- Prompt 模板：`ai_workflow/prompts/requirement_review.md`
