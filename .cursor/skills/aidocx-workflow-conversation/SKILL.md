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

| Stage | Name | Auto? | Key Outputs |
|-------|------|-------|-------------|
| S1 | 需求评审 | 部分 | review_report.md, review_report.json |
| S2 | 需求拆解 | 否 | backlog.md, backlog.json |
| S2.5 | 迭代规划 | 否 | iteration_plan.md, iteration_plan.json |
| S3 | 原型导出 | 否 | prototype.md |
| S4 | 流程图导出 | 否 | business_flow.md |
| S5 | 测试点生成 | 部分 | test_points.json |
| S6 | 测试用例生成 | 部分 | test_cases.md/json/xlsx |
| S7 | 用例审查 | 部分 | review_report.md, review_report.json |
| S8 | 自迭代 | 是 | iteration.md, iteration.json |

---

## 完整流水线（S1→S2→S2.5→S3→S4→S5→S6→S7→S8）

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

### 第四步：执行 S2.5（AI 纯创意）

```
python
from ai_workflow.conversation_skills import make_stage2_5_skill, save_iteration_plan

s2_5 = make_stage2_5_skill()
# AI 生成迭代计划 Markdown + JSON
# AI 调用 save_iteration_plan()
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
from ai_workflow.conversation_skills import make_stage4_skill
from ai_workflow.test_case_formatter import compose_test_points_from_structure

# 1. Python 自动生成测试点骨架
skeleton = compose_test_points_from_structure(breakdown)
# 骨架包含：story_id, module_coverage, equivalence_classes, boundary_values

# 2. AI 读取优化后的 prompt
s4 = make_stage4_skill()
# AI 只生成 scenario_test_points（简化输出）
```

### 第八步：执行 S6（ID自动化 + AI 填内容）

```
python
from ai_workflow.conversation_skills import make_stage5_skill
from ai_workflow.test_case_formatter import format_test_cases

# 1. AI 生成用例内容（简化版）
s5 = make_stage5_skill()
# AI 只输出：功能点、标题、前置条件内容、步骤内容、预期结果内容

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

## 自动化模块速查

| Module | Function | Purpose |
|--------|----------|---------|
| `requirement_reviewer_auto` | `auto_review_requirement()` | S1 规则引擎：自动评分（5维度加权） |
| `test_case_formatter` | `compose_test_points_from_structure()` | S5 骨架生成：从 breakdown 生成测试点结构 |
| `test_case_formatter` | `format_test_cases()` | S6 格式化：自动ID分配、字段规范化、去重 |
| `auto_reviewer` | `auto_review()` | S7 审查：结构验证+覆盖率计算+通过判定 |
| `iteration_aggregator` | `aggregate_iteration_data()` | S8 聚合：反馈日志+审核报告统计 |
| `feedback_logger` | `import_feedback()` | 反馈收集：从 Excel/CSV/JSON 导入执行反馈 |
| `feedback_logger` | `import_from_test_cases_xlsx()` | 反馈收集：从 test_cases.xlsx 导入执行追踪数据 |

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
