---
name: aidocx-s8-self-iteration
description: >
  AIDocxWorkFlow Stage 8 — 自迭代。分析 S7 审查报告，从 S4→S5→S6→S7 链路推理根因，
  以「风险点覆盖」为核心指标，产出缺陷模式分析、Prompt 改进建议，并将经验归档到知识库。
  使用当用户执行 /aidocx-s8-self-iteration、粘贴 S7 审查报告、或进行 S8 自迭代/根因分析任务。
disable-model-invocation: true
  Use when the user runs /aidocx-s8-self-iteration, pastes S7 review report, or starts self-iteration/root-cause analysis.
  使用当用户执行 /aidocx-s8-self-iteration、粘贴 S7 审查报告、或进行 S8 自迭代/根因分析任务时。
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s8-self-iteration
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S8 — 自迭代

**独立阶段**：可单独调用。上游材料（S7 review_report.json）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s8-self-iteration` 或粘贴 S7 审查报告

**前置材料**：
- S7 审查报告：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/review_report.json`
- S5 test_points.json（用于 S4 覆盖率分析）：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json`
- S6 test_cases.json：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/test_cases.json`
- S4 business_flow.md（用于风险点提取）：`workflow_assets/<req_name>/「S4 流程图导出」/<version>/business_flow.md`
- 执行反馈日志（可选）：`workflow_assets/feedback_logs/`

**材料缺失时**：生成失败报告，停止 S8。

---

## 核心任务

分析 S7 审查报告，推理不达标的根因，产出可执行的改进建议，并归档经验。

### 分析流程（4 步）

**第 1 步：读取 S7 审查报告**

```python
import json
with open("workflow_assets/<req_name>/「S6 测试用例生成」/<version>/review_report.json") as f:
    report = json.load(f)

verdict = report["overall_pass"]           # True / False
reviewer_b = report["reviewer_b"]           # s4_risk_coverage, s4_exception_coverage, ...
```

**第 2 步：判断判决类型**

| 条件 | 判决 | 含义 |
|------|------|------|
| S4风险点覆盖率=100% 且 S4异常树覆盖率=100% 且 结构完整性≥90% | PASS | 所有风险已覆盖 |
| S4风险点覆盖率<100% 或 S4异常树覆盖率<100% | FAIL | 存在未被覆盖的风险点 |

**第 3 步：根因链路推理**

**PASS → 无需根因分析**：记录经验，输出 iteration 报告即可。

**FAIL → 根因链路推理**：

| 症状 | 最可能根因 | 回溯方向 |
|------|-----------|---------|
| S4 风险点覆盖率 < 100% | S5 未引用 S4 风险点 | 回溯 S5，检查每个 R-XX 是否映射了测试点 |
| S4 异常树覆盖率 < 100% | S5 未引用 S4 异常决策树 | 回溯 S5，检查每个异常树叶子节点是否映射了测试点 |
| 结构完整性 < 90% | S6 步骤质量差（通用模板） | 重点修改 S6 步骤写作规则 |

**根因链路图**：

```
症状 ──── S7 FAIL（S4 风险点/异常树未全覆盖）
            ↓
根因层 1 ── 具体缺口：哪些 R-XX 或异常树节点未被覆盖？
            ↓
根因层 2 ── S5 层缺失：这些风险点/异常节点是否在 test_points.json 中？
            ↓
根因层 3 ── 根本原因：
              - S4→S5 衔接断裂（风险点清单未传递）？
              - S5 规则未明确要求引用 S4？
              - S5 执行者遗漏了某些风险点？
```

**第 4 步：产出改进建议**

| 字段 | 内容 |
|------|------|
| **Problem** | 具体问题描述（S7 报告中的具体缺口） |
| **Evidence** | 数据支撑（S7 报告中的数值） |
| **Root Cause** | 根因定位（哪个阶段、哪个环节断裂） |
| **Fix** | 具体修复动作 |
| **Affected Stage** | 需要修改的阶段（S4/S5/S6 规则文件） |
| **Expected Impact** | 预期改善效果 |

---

## 归档机制

将可复用经验沉淀到知识库：

| 归档位置 | 内容 |
|----------|------|
| `workflow_assets/feedback_archive/rules/<Module>/通用补充点.md` | 按模块分类的通用测试点 |
| `workflow_assets/test_point_library/` | 新增测试点类型（如新增的风险驱动测试点） |
| `workflow_assets/test_case_library/` | 新增用例模板（如 S4 风险点映射模板） |

**归档触发条件**：S7 PASS 时触发归档；S7 FAIL 时，仅记录根因，暂不归档（待问题解决后归档）。

---

## 成功产出

路径：`workflow_assets/<req_name>/「S8 自迭代」/<version>/iteration.md`
路径：`workflow_assets/<req_name>/「S8 自迭代」/<version>/iteration.json`

**iteration.json 内容结构**：

```json
{
  "iteration_number": 2,
  "verdict": "PASS / FAIL",
  "s4_risk_coverage": 0.95,
  "s4_exception_coverage": 1.0,
  "root_causes": [
    {
      "problem": "R-12 缓存击穿风险点未覆盖",
      "evidence": "S4风险点覆盖率 95% (19/20)",
      "root_cause": "S5 执行时遗漏了 AUX-CACHE Epic 的 R-12 风险点",
      "fix": "为 AUX-CACHE-001 补充缓存击穿 EXCEPTION 测试点",
      "affected_stage": "S5 规则"
    }
  ],
  "prompt_refinements": [],
  "archive_summary": {},
  "next_iteration_focus": []
}
```

---

## 失败报告

路径：`workflow_assets/<req_name>/「S8 自迭代」/<version>/fail_report_S8.md`

---

## 自动化支持

```python
from ai_workflow.self_iteration import analyze_and_iterate
result = analyze_and_iterate(version, review_report, test_points, test_cases, s4_risks)
# result['verdict']        # "PASS" / "FAIL"
# result['root_causes']    # 根因列表
# result['archive_summary'] # 归档摘要

from ai_workflow.self_iteration import archive_experience
archive_experience(result, version)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S8_SELF_ITERATION.mdc`
- S7 审查规范：`.cursor/rules/STAGE_S7_REVIEW.mdc`
- S5 测试点规范：`.cursor/rules/STAGE_S5_TEST_POINTS.mdc`
- Prompt 模板：`ai_workflow/prompts/self_iteration.md`
- 迭代引擎：`ai_workflow/self_iteration.py`
- 反馈日志：`workflow_assets/feedback_logs/`
- 归档目录：`workflow_assets/feedback_archive/rules/`
