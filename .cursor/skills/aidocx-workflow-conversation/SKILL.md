---
name: aidocx-workflow-conversation
description: >
  在纯对话模式下执行 AI 测试用例生成流水线（S1-S7），通过 Python 自动化引擎 + AI 协作节省 token
  Use when the user wants to run the full S1-S7 pipeline in conversation mode, save tokens via Python automation engine + AI collaboration.
  使用当用户希望在纯对话模式下执行 AI 测试用例生成流水线（S1-S7）、通过 Python 自动化引擎 + AI 协作节省 token 时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: workflow-conversation
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow — 对话模式使用指南

在纯对话模式下，通过 Python 自动化引擎 + AI 协作执行流水线，无需任何 MCP 工具。

---

## 工作原理

```
用户输入需求
    ↓
┌─────────────────────────────────────────────────────┐
│  自动化引擎（Python）                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ S1 规则引擎 │  │ S5 骨架生成  │  │ S7 审查  │  │
│  │ S8 结构验证 │  │ S6 ID分配   │  │ S8 聚合  │  │
│  └─────────────┘  └──────────────┘  └──────────┘  │
│        ↓                ↓              ↓             │
│  AI 只做创意工作（评分验证 / 填内容 / 定性分析）      │
└─────────────────────────────────────────────────────┘
    ↓
文件输出（.md / .json / .xlsx）
```

---

## 流水线阶段（S1-S7）

| Stage | Name | Auto? | 默认 | Key Outputs |
|-------|------|-------|------|-------------|
| S1 | 需求评审 | 部分 | ✅ 执行 | review_report.md, review_report.json |
| S2 | 需求拆解 | 否 | ✅ 执行 | backlog.md, backlog.json |
| **S2.5** | **迭代规划** | 否 | ⏭️ **全流程默认跳过** | iteration_plan.md, iteration_plan.json |
| S3 | 原型导出 | 否 | ✅ 执行 | prototype.md |
| S4 | 流程图导出 | 否 | ✅ 执行 | business_flow.md |
| S5 | 测试点生成 | 部分 | ✅ 执行 | test_points.json |
| S6 | 测试用例生成 | 部分 | ✅ 执行 | test_cases.md/json/xlsx |
| S7 | 用例审查 | 部分 | ✅ 执行 | review_report.md, review_report.json |
| S8 | 自迭代 | 是 | ✅ 执行 | iteration.md, iteration.json |

> **S2.5 默认跳过原则**：S2.5（迭代规划）只解决"开发节奏/资源/排期"问题，**对 S5 测试点、S6 用例的产出数量/质量无强关系**。在「全流程模式」下默认跳过该阶段。需要做迭代排期时：
> - **方式 1（编排层）**：在执行 S2 之前声明环境变量 `AIDOCX_INCLUDE_S2_5=true`（或 `1`），本 SKILL 的「第四步」才会被执行；其他值 / 未设置 = 跳过。
> - **方式 2（独立调用）**：直接 `/aidocx-s2-5-iteration` 单独跑 S2.5，**不受 `AIDOCX_INCLUDE_S2_5` 控制**。
> - **判定时机**：编排层（顶层 LLM）在准备进入「第四步」时，先检查环境变量；不通过则直接进入「第五步：执行 S3」，并在流程报告里写 `S2.5: SKIPPED (AIDOCX_INCLUDE_S2_5 unset)`。

---

## 完整流水线（S1→S2→[S2.5 opt-in]→S3→S4→S5→S6→S7→S8）

### 第一步：执行 Stage 1（自动评分 + AI 验证）

```
python
from ai_workflow.requirement_reviewer_auto import auto_review_requirement

auto_result = auto_review_requirement(req_text)
print(f"自动评分: {auto_result['score_total']}/10 → {auto_result['verdict']}")
```

### 第二步：Gate Check

```
if verdict == "REJECT":
    输出审查结果 → 停止
else:
    进入 S2
```

### 第三步：执行 S2（AI 纯创意）

```
python
from ai_workflow.conversation_skills import make_stage2_skill, save_stage2_output

s2 = make_stage2_skill()
# AI 读取 s2['system_prompt'] + s2['user_template']
# AI 输出 Epic/Story JSON 后调用 save_stage2_output()
```

### 第四步：执行 S2.5（**全流程默认跳过**，按需开启）

> **跳过条件**（满足任一即跳过）：
> 1. 环境变量 `AIDOCX_INCLUDE_S2_5` 未设置 / 值为 `false` / `0` / 空 → 跳过
> 2. S2 backlog 缺失（前置材料不满足） → 跳过（按 STAGE_S2_5 rule 走失败报告）
> 3. 项目明确不需要做迭代排期（如小需求、单次性小改）→ 跳过
>
> **跳过时**直接在流程报告里写 `S2.5: SKIPPED (reason: <上面条件之一>)`，**不**创建空 `「S2.5 迭代规划」/` 目录，进入「第五步：执行 S3」。

```python
import os
if os.environ.get("AIDOCX_INCLUDE_S2_5", "").lower() in ("true", "1", "yes"):
    from ai_workflow.conversation_skills import make_stage2_5_skill, save_iteration_plan

    s2_5 = make_stage2_5_skill()
    # AI 生成迭代计划 Markdown + JSON
    # AI 调用 save_iteration_plan()
else:
    print("[S2.5] SKIPPED — AIDOCX_INCLUDE_S2_5 not set; S2.5 not required for test case generation")
```

### 第五步：执行 S3（AI 纯创意）

```
python
from ai_workflow.conversation_skills import make_stage3_skill, save_stage3_output

s3 = make_stage3_skill()
# AI 生成 Markdown 原型 + Mermaid 页面流
# AI 调用 save_stage3_output()
```

### 第六步：执行 S4（AI 纯创意）

```
python
from ai_workflow.conversation_skills import make_stage4_skill, save_stage4_output

s4 = make_stage4_skill()
# AI 生成业务流程图 + 时序图 + 异常决策树
# AI 调用 save_stage4_output()
```

### 第七步：执行 S5（骨架自动化 + AI 填内容）

```
python
# 1. Python 自动生成测试点骨架
from ai_workflow.test_case_formatter import compose_test_points_from_structure

skeleton = compose_test_points_from_structure(breakdown)
# 骨架包含：story_id, module, equivalence_classes, boundary_values
# 字段：scenario_test_points（AI 填充）

# 2. AI 读取 S5 SKILL.md（.cursor/skills/aidocx-s5-test-points/SKILL.md §1.4 LLM 必读指令）
# AI 必须先 Read：MODULES.md §1 总表 + 8 模块 .md + 8 边界 O_boundary.md
# AI 然后生成 scenario_test_points（简化输出），按每个 Story 命中模块 × 命中类型组合

# 3. AI 自行保存 test_points.json 到 workflow_assets/<req_name>/「S5 测试点生成」/<version>/
# ⚠️ 当前代码无 save_stage5_output 自动化函数，需 AI 手工 write_file / IDE 保存
```

### 第八步：执行 S6（自动化 ID 分配 + AI 填内容）

```
python
from ai_workflow.test_case_formatter import format_test_cases

# 1. AI 生成用例内容（简化版）—— 读取 S6 SKILL.md
# AI 必须先 Read：S5 test_points.json + 8 模块子模板（按 TP 的 module 字段）

# 2. Python 自动处理
formatted = format_test_cases(ai_raw_output, breakdown, test_points)
# 自动分配用例ID（按模块序号）、规范化字段、步骤编号、去重
# 自动生成 .md + .json + .xlsx
```

### 第九步：执行 S7（自动审查 + AI 定性分析）

```
python
from ai_workflow.conversation_skills import make_stage6_skill
from ai_workflow.auto_reviewer import auto_review

# 1. Python 自动审查
result = auto_review(test_cases, breakdown, req_text)
print(f"自动审查: overall_pass={result.overall_pass}")
print(f"  coverage={result.coverage.requirement_coverage:.0%}")
print(f"  structure={result.structure_pass_rate:.0%}")

# 2. AI 只做定性审核
s6 = make_stage6_skill()
# AI 审核 result.ai_input_summary（~500 chars）
```

### 第十步：执行 S8（自动聚合 + AI 定性建议）

```
python
from ai_workflow.conversation_skills import make_stage7_skill
from ai_workflow.iteration_aggregator import aggregate_iteration_data

# 1. Python 自动聚合
stats = aggregate_iteration_data(feedback_dir, reports_dir)
print(f"聚合: {stats.total_feedback_entries}条反馈, {stats.total_reviews}个审核")

# 2. AI 生成定性建议
s7 = make_stage7_skill()
# AI 读取 stats.ai_summary（~400 chars）
```

---

## 简化流水线（S1→S2→S5→S6）

只执行 4 阶段（S1→S2→S5→S6），无原型/流程图/审核/迭代。

```
python
from ai_workflow.simple_flow_executor import execute_wf_simple_flow

result = execute_wf_simple_flow(req_text, version='v1.0', filename='test_cases')
```

---

## 自动化模块速查（**仅列代码中实际存在的函数**）

| Module | Function | 阶段 | 状态 |
|--------|----------|------|------|
| `requirement_reviewer_auto` | `auto_review_requirement()` | S1 | ✅ 存在 |
| `conversation_skills` | `make_stage2_skill()` | S2 | ✅ 存在 |
| `conversation_skills` | `save_stage2_output()` | S2 | ✅ 存在 |
| `conversation_skills` | `make_stage2_5_skill()` | S2.5 | ✅ 存在 |
| `conversation_skills` | `save_iteration_plan()` | S2.5 | ✅ 存在 |
| `conversation_skills` | `make_stage3_skill()` | S3 | ✅ 存在 |
| `conversation_skills` | `save_stage3_output()` | S3 | ✅ 存在 |
| `conversation_skills` | `make_stage4_skill()` | S4（注意：不是 S5）| ✅ 存在 |
| `conversation_skills` | `save_stage4_output()` | S4 | ✅ 存在 |
| `conversation_skills` | `execute_simple_flow()` | S1→S2 入口 | ✅ 存在 |
| `conversation_skills` | `execute_full_flow()` | 全流程状态查询 | ✅ 存在 |
| `test_case_formatter` | `compose_test_points_from_structure()` | S5 骨架 | ✅ 存在 |
| `test_case_formatter` | `format_test_cases()` | S6 格式化 | ✅ 存在 |
| `auto_reviewer` | `auto_review()` | S7 自动审查 | ✅ 存在 |
| `iteration_aggregator` | `aggregate_iteration_data()` | S8 聚合 | ✅ 存在 |
| `feedback_logger` | `import_feedback()` | 反馈收集 | ✅ 存在 |
| `feedback_logger` | `import_from_test_cases_xlsx()` | 反馈收集 | ✅ 存在 |

**⚠️ 代码中不存在的 S5 自动化函数**（SKILL.md 必须基于真实 API）：
- ~~`make_stage5_skill()`~~ — 不存在；S5 完全靠 LLM 读 SKILL.md §1.4 + 手工调 `compose_test_points_from_structure()` + 自行保存
- ~~`save_stage5_output()`~~ — 不存在；S5 输出由 LLM 手工 `write_file` 保存
- ~~`make_stage6_skill()` / `save_stage6_output()`~~ — 不存在；S6 同样靠 SKILL.md + LLM

---

## 文件输出路径

```
workflow_assets/<req_name>/
  「S1 需求评审」/<version>/
    review_report.md                              ← S1 评审报告
  「S2 需求拆解」/<version>/
    backlog.md, backlog.json                      ← S2 Epic/Story分解
  「S2.5 迭代规划」/<version>/
    iteration_plan.md, iteration_plan.json       ← S2.5 迭代规划
  「S3 原型导出」/<version>/
    prototype.md                                 ← S3 页面原型
  「S4 流程图导出」/<version>/
    business_flow.md                             ← S4 业务流程图
  「S5 测试点生成」/<version>/
    test_points.json                             ← S5 测试点
  「S6 测试用例生成」/<version>/
    test_cases.md, test_cases.json, test_cases.xlsx  ← S6 用例
    review_report.md, review_report.json             ← S7 审查报告
    full_pipeline_report.md                          ← S6 全流程报告
    quality_gate_report.md                            ← S7 质量门禁报告
  「S8 自迭代」/<version>/
    iteration.md, iteration.json                 ← S8 自迭代
workflow_assets/
  feedback_logs/
  feedback_archive/
```

---

## 关键规则

1. **S1 REJECT 立即停止**：不再执行后续阶段
2. **S7 FAIL 迭代**：修复问题后重跑 S6→S7
3. **纯 JSON 输出**：S1/S2/S5/S6/S7 输出 JSON 不带 markdown 代码块
4. **Markdown 输出**：S2/S3/S4 输出 Markdown + Mermaid
5. **Excel 自动生成**：S6 执行后自动生成 `.xlsx`
6. **流程结束时自动出报告**：流程完成后会自动打印 Markdown 格式的「流程执行报告」

---

## 流程结束后：产出报告 & 反馈收集

### 反馈收集（feedback_logger）

```
python
from ai_workflow.feedback_logger import import_feedback, import_from_test_cases_xlsx

# 方式 1：从 Excel/CSV 导入（自动识别「反馈结果」/「执行追踪」sheet）
result = import_feedback(
    feedback_file="/path/to/feedback.xlsx",
    review_file="/path/to/review.xlsx",   # 可选
    version="v1.0",
    req_name="游戏道具商城系统",
)

# 方式 2：从 test_cases.xlsx 的执行追踪 sheet 直接导入
result = import_from_test_cases_xlsx(
    xlsx_path="/path/to/test_cases.xlsx",
    version="v1.0",
)

# 方式 3：CLI
python3 -m ai_workflow.feedback_logger --file feedback.xlsx --version v1.0
```

支持的文件/sheet：
- Excel: 自动探测 `反馈结果` > `执行追踪` > `执行记录` sheet
- CSV / JSON
- test_cases.xlsx 的 `执行追踪` sheet（含执行结果列）

### 反馈文件存放目录

```
workflow_assets/feedback_logs/
  feedback_<req_name>_<version>_<timestamp>.json  ← 本次导入
  feedback_<req_name>_<version>_<timestamp>.json  ← 历史导入
```

### 反馈数据自动标准化

| Excel/CSV 列名 | → 标准字段 | 示例 |
|---|---|---|
| 用例ID / case_id | case_id | `界面-TC-001` |
| 执行结果 / result | result | `PASS` / `FAIL` |
| 实际结果 / actual_result | actual_result | `按钮无响应` |
| 缺陷描述 / defect_desc | defect_desc | `按钮事件未注册` |
| 严重程度 / severity | severity | `CRITICAL` / `MAJOR` / `MINOR` / `LOW` |
| 审核人 / reviewer | reviewer | `张三` |
| 审核结果 / review_result | review_result | `PASS` / `FAIL` |

值映射示例：`通过`/`✅`/`PASS` → `PASS`；`失败`/`❌`/`FAIL` → `FAIL`；`P0`/`阻断级` → `CRITICAL`

提交反馈后，系统将自动统计缺陷模式，下次生成用例时优先复用知识库中已有的测试点。
