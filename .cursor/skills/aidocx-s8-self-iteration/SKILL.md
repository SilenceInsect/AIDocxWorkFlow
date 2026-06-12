---
name: aidocx-s8-self-iteration
description: AIDocxWorkFlow Stage 8 — 自迭代。分析 S7 审查报告 + 执行反馈日志，产出缺陷模式分析、Prompt 改进建议、覆盖率缺口报告，并将经验归档到知识库。使用当用户执行 /aidocx-s8-self-iteration、粘贴 S7 审查报告、或进行 S8 自迭代任务。
disable-model-invocation: true
---

# AIDocxWorkFlow S8 — 自迭代

**独立阶段**：可单独调用。上游材料（S7 review_report + feedback_logs）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s8-self-iteration` 或粘贴 S7 审查报告

**前置材料**：
- S7 审查报告：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/review_report.json`
- 执行反馈日志（可选）：`workflow_assets/feedback_logs/`

**材料缺失时**：生成失败报告，停止 S8。

---

## 分析维度

| 维度 | 内容 |
|------|------|
| 缺陷模式分析 | 哪些测试用例持续漏检 bug？哪些用例频繁误报？ |
| Prompt 有效性 | 哪些 prompt 产出高质量？哪些需要细化？ |
| 覆盖率缺口 | 哪些类型的缺陷反复出现？是否缺少某类测试？ |
| 改进建议 | 每个发现给出 Problem / Evidence / Fix / Expected Impact |

---

## 归档机制

将可复用经验沉淀到知识库：

| 归档位置 | 内容 |
|----------|------|
| `feedback_archive/rules/<Module>/通用补充点.md` | 按模块分类的通用测试点 |
| `test_point_library/` | 新增测试点类型 |
| `test_case_library/` | 新增用例模板 |

S8 归档的经验自动注入下一版本的 S5/S6 prompt，提升用例质量。

---

## 成功产出

路径：`workflow_assets/<req_name>/「S8 自迭代」/<version>/iteration.md`
路径：`workflow_assets/<req_name>/「S8 自迭代」/<version>/iteration.json`

报告内容：缺陷模式分析 → Prompt改进建议 → 覆盖率缺口 → 归档摘要 → 下一轮迭代重点

---

## 失败报告

路径：`workflow_assets/<req_name>/「S8 自迭代」/<version>/fail_report_S8.md`

---

## 自动化支持

```python
from ai_workflow.self_iteration import analyze_and_iterate
result = analyze_and_iterate(version, review_report, feedback_logs)
# result['defect_patterns'], result['prompt_refinements'], result['archive_summary']

from ai_workflow.self_iteration import archive_experience
archive_experience(result, version)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S8_SELF_ITERATION.mdc`
- Prompt 模板：`ai_workflow/prompts/self_iteration.md`
- 迭代引擎：`ai_workflow/self_iteration.py`
- 反馈日志：`workflow_assets/feedback_logs/`
- 归档目录：`workflow_assets/feedback_archive/rules/`
