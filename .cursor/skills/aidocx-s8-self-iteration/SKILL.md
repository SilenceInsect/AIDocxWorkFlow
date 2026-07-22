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

**独立阶段**：可单独调用。上游材料（S7 review_report.json / review_snapshot.json）审查合格后开始，失败写失败报告。

> ⚠️ **模块定义见 [`.cursor/MODULES.md`](../../MODULES.md)（项目级唯一真相源）。**
> 本文件不重写模块表。涉及"模块归属错误"分析时，按 `MODULES.md` §1 总表 + §3.5 交叉场景判定规则 + §4.5-§4.12 各模块边界 + §9 兼容映射综合判定。
>
> **HINT vs UI 边界误标**是历史 S5 误标高发区（`SYS_MSG` / `RED_DOT` 旧枚举出现），自迭代时需重点关注。

---

## 阶段入口

**触发**：`/aidocx-s8-self-iteration` 或粘贴 S7 审查报告

**前置材料**：
- S7 审查报告：`workflow_assets/<req_name>/<version>/「S6 测试用例生成」/review_report.json`
- S5 test_points.json（用于 S4 覆盖率分析）：`workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json`
- S6 test_cases.json：`workflow_assets/<req_name>/<version>/「S6 测试用例生成」/test_cases.json`
- S4 business_flow.md（用于风险点提取）：`workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md`
- 执行反馈日志（可选）：`workflow_assets/feedback_logs/`

**材料缺失时**：生成失败报告，停止 S8。

---

## §1.4 LLM 必读材料（阶段前置）

**开始根因分析前，必须先 Read 以下材料。禁止凭印象直接生成。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| 1 | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| 缺陷根因最终落到模块 × 类型的组合；缺陷模式按模块统计 |
| 2 | 模块边界区分 | `.cursor/MODULES.md`（§4 各模块 O_boundary.md）| 判断 S5 TP 模块归属是否正确；根因分析的起点 |
| 3 | S7 review_report | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/review_report.json` | 所有审查结论的来源；按 reviewer_a / reviewer_b / recommendations 结构追溯 |
| 4 | S5 test_points | `workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json` | S5 层缺陷追溯的起点 |
| 5 | S4 business_flow | `workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md` | 异常决策树和风险点清单是 S5 缺 TP 的根因来源 |
| 6 | S6 test_cases | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/test_cases.json` | S6 层缺陷追溯的参考 |

---

## §5 一致性检查（SKILL ↔ Rule 自动对齐）

> **触发时机**：本节读取后、正式执行前。**仅执行一次**（同一次对话中多次触发本阶段，不重复检查）。

**检查类型**：A = 必读材料对齐 / B = 输出路径对齐 / C = 字段名对齐 / D = 模块枚举对齐

```python
from ai_workflow.consistency_check import run_consistency_check

result = run_consistency_check(stage="s8")
if not result["passed"]:
    print(f"[一致性检查] 发现 {len(result['issues'])} 个问题（见日志）")
```

检查结果不阻断阶段执行，仅输出到日志供人工参考。

---

## 核心任务

分析 S7 审查报告，推理不达标的根因，产出可执行的改进建议，并归档经验。

### 分析流程（4 步）

**第 1 步：读取 S7 审查报告**

```python
import json
with open("workflow_assets/<req_name>/<version>/「S6 测试用例生成」/review_report.json") as f:
    report = json.load(f)

reviewer_a = report["reviewer_a"]
reviewer_b = report["reviewer_b"]
recommendations = report["recommendations"]
```

**第 2 步：缺陷根因追溯（改版 — 取消 PASS/FAIL 硬判决）**

> **变更（2026-07-09 闭环 Q-539/Q-540）**：
> - S7 已废弃 `overall_pass` 字段，S8 不再做 PASS/FAIL 硬判决
> - 取消"S4 风险点覆盖率=100% + 结构完整性≥90% = PASS / 否则 FAIL"硬条件
> - 改为：**LLM 按业务实际判断是否需要根因追溯**——高风险缺陷（必修项）触发追溯；低风险（可改项）记录经验即可

**LLM 根因追溯触发判断**：

|| LLM 判断 | 触发动作 |
||---------|---------|
|| `recommendations.must_fix` 非空 | **触发根因追溯**——对应必修项回溯 S4→S5→S6 链路 |
|| `recommendations.should_fix` 非空 | **触发根因追溯**——对应应改项回溯 S4→S5→S6 链路 |
|| `recommendations.could_fix` 非空 | **不触发追溯**——记录经验，输出迭代报告即可 |
|| `recommendations` 全空 | **不触发追溯**——S7 报告无缺陷标记，S8 仅归档经验 |

> **核心原则**：S8 不再用"覆盖率数字"做硬判决——LLM 按业务实际决定哪些必修/应改项需要根因追溯。

**LLM 触发后，按以下规则执行根因追溯**：

|| LLM 识别的缺陷类型 | 触发动作 |
||-------------------|---------|
|| 必修项（must_fix）非空 | **必须追溯**——S7 报告中的每条必修项回溯 S4→S5→S6 链路 |
|| 应改项（should_fix）非空 | **应追溯**——S7 报告中的每条应改项回溯 S4→S5→S6 链路 |
|| 可改项（could_fix）非空 | **不追溯**——记录经验即可 |

**根因链路图（改版 — 适应 LLM 触发判断）**：

```
症状 ──── S7 审查报告中的必修项 / 应改项
            ↓
根因层 1 ── 具体缺口：哪些 R-XX / 异常树叶子未被覆盖？哪些字段名违规？哪些模块归属错误？
            ↓
根因层 2 ── S5/S6 层缺失：这些缺口是否在 test_points.json / test_cases.json 中？
            ↓
根因层 3 ── 根本原因：
              - S4→S5 衔接断裂（风险点清单未传递）？
              - S5 规则未明确要求引用 S4？
              - S5 执行者遗漏了某些风险点？
              - S2 OBJ 拆分错误导致模块归属错误？
              - S4 Epic 命名误导导致模块归属错误？
              - S6 字段命名未对齐 SKILL.md 强约束？
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

> **v14 RCA 扩展**：iteration_items 每条必须填写 RCA 根因字段（MUST）。`rca.stage` 必须与根因链路图"根本原因"层对应，`clause` 从 RCA 映射表选取，禁止自创。

#### iteration_items[] 字段结构（v14 RCA 扩展）

|| 字段 | 级别 | 说明 |
||------|------|------|
|| `id` | **MUST** | 迭代项序号 `ITER-{NNN}` |
|| `problem` | **MUST** | 具体问题描述（S7 报告中的具体缺口） |
|| `evidence` | **MUST** | 数据支撑（S7 报告中的数值） |
|| `root_cause` | **MUST** | 根因定位（哪个阶段、哪个环节断裂） |
|| `fix` | **MUST** | 具体修复动作 |
|| `affected_stage` | **MUST** | 需要修改的阶段数组（如 `["S5", "SKILL.S5"]`） |
|| `expected_impact` | SHOULD | 预期改善效果 |
|| `rca` | **MUST** | 三级根因定位对象 |
|| `rca.stage` | **MUST** | 一级：`S4` / `S5` / `S6` / `S2` / `S1` |
|| `rca.type` | **MUST** | 二级：`OMISSION` / `BOUNDARY_ERR` / `QUALITY_LOW` / `FIELD_MISSING` / `LINKAGE_BROKEN` / `RULE_VIOLATION` / `ID_NONCOMPLIANT` |
|| `rca.clause` | **MUST** | 三级：条款代码，从 RCA 映射表选取 |
|| `rca.explanation` | SHOULD | 根因简述（≤ 50 字） |
|| `archive_target` | SHOULD | 归档目标（如 `knowledge/project_local/.review_queue/`） |

> **条款代码来源**：`governance/design_iter/current/rca_three_level_classification.md` §1.3。条款代码必须来自映射表，禁止自创。`affected_stage` 数组必须包含 `rca.stage`。


## 归档机制

将可复用经验沉淀到知识库：

| 归档位置 | 内容 |
|----------|------|
| `knowledge/project_local/.review_queue/` | 写入待人工审核的知识候选（含模块、子类、目标段落、建议内容） |
| `knowledge/public/test_point_library/` | 公共测试点知识库，**只读参考，不自动写入** |
| `knowledge/public/test_case_library/` | 公共用例知识库，**只读参考，不自动写入** |

**归档触发条件**：S7 账本无 uncovered/partial 时触发归档；否则仅记录根因，暂不归档（待问题解决后归档）。

---

## 成功产出

路径：`workflow_assets/<req_name>/<version>/「S8 自迭代」/iteration.md`
路径：`workflow_assets/<req_name>/<version>/「S8 自迭代」/iteration.json`

**iteration.json 内容结构**：

```json
{
  "iteration_number": 2,
  "verdict": "PASS / FAIL（由 root_causes 与账本状态推导，不依赖 overall_pass）",
  "s4_risk_coverage": 0.95,
  "s4_exception_coverage": 1.0,
  "root_causes": [
    {
      "problem": "R-12 缓存击穿风险点未覆盖",
      "evidence": "S4风险点覆盖率 95% (19/20)",
      "root_cause": "S5 执行时遗漏了 UTIL-CACHE Epic 的 R-12 风险点",
      "fix": "为 UTIL-CACHE-001 补充缓存击穿 EXCEPTION 测试点",
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

路径：`workflow_assets/<req_name>/<version>/「S8 自迭代」/fail_report_S8.md`

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
- 归档目录：写入 `knowledge/project_local/.review_queue/`，由人工审核后决定是否回写公共知识库

---

## 执行卡（v14 单阶段执行卡 — 4 区块合一）

<aside data-exec-card-block="input_gate" data-src=".cursor/rules/STAGE_S8_SELF_ITERATION.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

> ⚠️ **派生产物，禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成
> src: `.cursor/rules/STAGE_S8_SELF_ITERATION.mdc` | synced_at: `2026-07-14`
> 修改请改源文件，然后跑 `python3 scripts/sync_execution_cards.py --stage s8-self-iteration` 重新同步。

### 输入门禁（input_gate）

| 必备材料 | 路径 | 缺失处理 |
|---|---|---|
| S7 审查报告 | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/review_report.json` | 必须存在，否则 fail_report_S8.md |
| S5 test_points.json | `workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json` | S5 层缺陷追溯起点 |
| S6 test_cases.json | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/test_cases.json` | S6 层缺陷追溯参考 |
| S4 business_flow.md | `workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md` | 风险点清单来源 |

**触发命令**：`/aidocx-s8-self-iteration` 或粘贴 S7 审查报告

</aside>

<aside data-exec-card-block="field_required" data-src=".cursor/rules/STAGE_S8_SELF_ITERATION.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### 必填字段（field_required）

| 字段 | 级别 | 校验 |
|---|---|---|
| 缺陷模式分析 | **MUST** | 按 module × type × stage 三维分类 |
| Prompt 改进建议 | **MUST** | 针对 S4→S5→S6 链路的具体改进 |
| 经验归档 | **MUST** | 写入 `knowledge/project_local/.review_queue/` |
| iteration.md / iteration.json | **MUST** | 最终迭代报告 |

</aside>

<aside data-exec-card-block="quality_gate" data-src=".cursor/rules/STAGE_S8_SELF_ITERATION.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### 质量门禁（quality_gate）

| 门禁 | 阈值 | 说明 |
|---|---|---|
| 可执行建议数 | ≥ 3 | 审查报告中有明确执行路径的建议条数 |
| 根因追溯深度 | 需追溯到 S4 层 | 缺陷模式须落 module × type × stage |
| 归档维度 | 必须含 module 维度 | 缺陷模式按模块统计 |

**SSOT**：`DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 `S8_MIN_SUGGESTIONS`

</aside>

<aside data-exec-card-block="naming" data-src=".cursor/rules/STAGE_S8_SELF_ITERATION.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### ID 命名规范（naming）

| 产物 | 格式 |
|---|---|
| 迭代报告 | `iteration.md` / `iteration.json` |
| 归档队列 | `knowledge/project_local/.review_queue/` |
| 反馈日志 | `workflow_assets/feedback_logs/` |
| 输出目录 | `workflow_assets/<req_name>/<version>/「S8 自迭代」/` |

</aside>
