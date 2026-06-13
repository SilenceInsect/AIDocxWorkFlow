---
name: aidocx-s7-review
description: >
  AIDocxWorkFlow Stage 7 — 用例审查。双审查员审计 S6 产出的测试用例（结构完整性 + 覆盖率）。
  覆盖率以 S4 风险点全量覆盖为核心指标（100%），不再使用「NEGATIVE ≥ 30%」等拍脑袋指标。
  支持 PASS / FAIL 两种判决（风险全覆盖即 PASS）。
  使用当用户执行 /aidocx-s7-review、粘贴 S6 test_cases.json、或进行 S7 用例审查任务。
disable-model-invocation: true
  Use when the user runs /aidocx-s7-review, pastes S6 test_cases.json, or starts test case review.
  使用当用户执行 /aidocx-s7-review、粘贴 S6 test_cases.json、或进行 S7 用例审查任务时。
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s7-review
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S7 — 用例审查

**独立阶段**：可单独调用。上游材料（S6 test_cases.json）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s7-review` 或粘贴 S6 test_cases.json

**前置材料**：
- S6 test_cases.json：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/test_cases.json`
- S5 test_points.json（用于 S4 覆盖率）：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json`

**材料缺失时**：生成失败报告，停止 S7。

---

## 双审查员审计

### 审查员 A：结构完整性

| 检查项 | 说明 |
|--------|------|
| ID 规范化 | 格式 `{Module}-TC-{NNN}`，如 `界面-TC-001` |
| 字段完整性 | precondition、steps、expected_result 全有值 |
| 步骤质量 | 原子性、无歧义、有具体数值；**禁止通用模板** |
| 预期结果可验证性 | 每步有明确 pass/fail 条件 |
| 无冗余 | 无重复覆盖同一场景的用例 |

### 审查员 B：覆盖率

> **核心原则：覆盖率 = 风险被覆盖的程度，而非比例。**

| 优先级 | 指标 | 阈值 | 说明 |
|--------|------|------|------|
| **P0** | **S4 风险点覆盖率** | **= 100%** | S4 每个风险点有对应测试点 |
| **P0** | **S4 异常树覆盖率** | **= 100%** | S4 异常决策树每个叶子节点有对应测试点 |
| P1 | 等价类覆盖率 | ≥ 80% | 每个等价类至少 1 个测试点 |
| P1 | 边界值覆盖率 | ≥ 80% | 每个边界值至少 1 个测试点 |
| P2 | 状态转换覆盖率 | ≥ 80% | 多状态 Story 的每个状态至少 1 个测试点 |

**覆盖率计算**：
- 从 test_points.json 的 `s4_reference` 字段提取（如 `R-01`、`S4-1.3异常树`）
- `S4风险点覆盖率 = 测试点引用了 S4-RXX 的数量 / S4 风险点总数`

---

## 质量门禁

| 条件 | 判决 |
|------|------|
| S4风险点覆盖率=100% **且** S4异常树覆盖率=100% **且** 结构完整性≥90% | **PASS** |
| S4风险点覆盖率<100% **或** S4异常树覆盖率<100% | **FAIL**（风险缺口） |
| 结构完整性 < 90% | **FAIL**（结构问题） |

> **PASS 解读**：只要 S4 的每个风险点和异常树节点都被覆盖，即为 PASS。测试点数量多少不重要。

---

## 成功产出

路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/review_report.md`
路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/review_report.json`

报告内容：审查员A结果 → 审查员B结果（S4覆盖率）→ 整体判决

---

## 失败报告

路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/fail_report_S7.md`

---

## 自动化支持

```python
from ai_workflow.auto_reviewer import auto_review
review_result = auto_review(test_cases, test_points, s4_risks)
# review_result['overall_pass'] ∈ {True, False}
# review_result['reviewer_b']['s4_risk_coverage'] ∈ [0.0, 1.0]
# review_result['reviewer_b']['uncovered_risks']  # 未覆盖的风险点列表
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S7_REVIEW.mdc`
- Prompt 模板：`ai_workflow/prompts/test_case_review.md`
- 自动审查引擎：`ai_workflow/auto_reviewer.py`
- 阈值配置：`ai_workflow/config.py`
