---
name: aidocx-s7-review
description: AIDocxWorkFlow Stage 7 — 用例审查。双审查员审计 S6 产出的测试用例（结构完整性 + 覆盖率），输出 PASS/FAIL 判决。质量门禁：覆盖率 ≥ 85% 且结构完整性 ≥ 90% 则 PASS。使用当用户执行 /aidocx-s7-review、粘贴 S6 test_cases.json、或进行 S7 用例审查任务。
disable-model-invocation: true
---

# AIDocxWorkFlow S7 — 用例审查

**独立阶段**：可单独调用。上游材料（S6 test_cases.json）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s7-review` 或粘贴 S6 test_cases.json

**前置材料**：
- S6 test_cases.json：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/test_cases.json`
- S5 test_points.json（参考）：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json`

**材料缺失时**：生成失败报告，停止 S7。

---

## 双审查员审计

### 审查员 A：结构完整性

| 检查项 | 权重 |
|--------|------|
| ID 规范化 | 固定 | 格式 `{Module}-TC-{NNN}` |
| 字段完整性 | 固定 | precondition、steps、expected_result 全有值 |
| 步骤质量 | 固定 | 原子性、无歧义、有具体数值 |
| 预期结果可验证性 | 固定 | 每步有明确 pass/fail 条件 |
| 无冗余 | 固定 | 无重复覆盖同一场景的用例 |

### 审查员 B：覆盖率

| 指标 | 阈值 | 说明 |
|------|------|------|
| 需求覆盖率 | ≥ 85% | 每个 Story/AC 至少 1 个正向用例 |
| 边界覆盖率 | ≥ 85% | 所有边界值测试点被覆盖 |
| 异常覆盖率 | ≥ 85% | 关键异常场景被覆盖 |
| 负向覆盖率 | ≥ 30% | 无效输入、权限违规场景被覆盖 |

---

## 质量门禁

| 条件 | 判决 |
|------|------|
| 覆盖率 ≥ 85% **且** 结构完整性 ≥ 90% | **PASS** |
| 否则 | **FAIL**（需修改后重审）|

---

## 成功产出

路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/review_report.md`
路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/review_report.json`

报告内容：审查员A结果（通过率+问题列表）→ 审查员B结果（覆盖率+缺口）→ 整体判决

---

## 失败报告

路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/fail_report_S7.md`

---

## 自动化支持

```python
from ai_workflow.auto_reviewer import auto_review
review_result = auto_review(test_cases, test_points, config)
# review_result['overall_pass'] ∈ {True, False}
# review_result['reviewer_a']['pass_rate'] ∈ [0.0, 1.0]
# review_result['reviewer_b']['requirement_coverage'] ∈ [0.0, 1.0]
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S7_REVIEW.mdc`
- Prompt 模板：`ai_workflow/prompts/test_case_review.md`
- 自动审查引擎：`ai_workflow/auto_reviewer.py`
- 阈值配置：`ai_workflow/config.py`
