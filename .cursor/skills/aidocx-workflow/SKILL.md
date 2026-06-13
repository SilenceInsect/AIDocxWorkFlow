---
name: aidocx-workflow
description: >
  AI Test Case Generation Pipeline. Use when generating test cases from requirements, breaking down requirements, creating prototypes/flowcharts, or any test case generation task.
  Use when generating test cases from requirements, breaking down requirements, creating prototypes/flowcharts, or any test case generation task.
  使用当从需求生成测试用例、拆解需求、创建原型/流程图、或任何测试用例生成任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: workflow
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow - AI Test Case Generation Pipeline

A 7-stage AI-driven pipeline that transforms raw requirements into review-ready test cases. Powered by Python automation engine in pure conversation mode.

## The 7 Stages

| Stage | Description | Key Outputs |
|-------|-------------|-------------|
| S1 | Requirement Review: 5-dimension scoring (PASS / NEEDS_REVISION / REJECT) | review_report.md, review_report.json |
| S2 | Breakdown: Epic → Story → Task hierarchy | backlog.md, backlog.json |
| S2.5 | Iteration Planning: 7-step load balancing → kickoff → resource locks → parallel work → tracking | iteration_plan.md, iteration_plan.json |
| S3 | Prototype: Text prototypes + Mermaid page flow per Story | prototype.md |
| S4 | Flowchart: Business flow + sequence diagram + exception decision tree + risk list | business_flow.md |
| S5 | Test Points: 7-module coverage, ≥ 6 points/story (2 POSITIVE + 2 BOUNDARY + 1 NEGATIVE + 1 EXCEPTION) | test_points.json |
| S6 | Test Cases: Detailed executable cases (Markdown + JSON + Excel 3 Sheet) | test_cases.md, test_cases.json, test_cases.xlsx |
| S7 | Review: Dual-reviewer audit — structure completeness + coverage ≥ 85% + structure ≥ 90% | review_report.md, review_report.json |
| S8 | Self-iteration: Defect pattern analysis → Prompt improvement → knowledge archive | iteration.md, iteration.json |

---

## Stage Gate Rules

- **S1 REJECT** → Stop pipeline immediately.
- **S5 FAIL** → Iterate on S5, then retry.
- **S7 FAIL** → Return to S6 for fixes, then retry S7.
- Gate thresholds: coverage ≥ 85%, structure completeness ≥ 90%.

---

## Output Directory Structure

```
workflow_assets/
  review_reports/                                ← S1 报告 + 失败报告（根级公共）
  <req_name>/
    「S1 需求评审」/    <version>/ review_report.md
    「S2 需求拆解」/    <version>/ backlog.md, backlog.json
    「S2.5 迭代规划」/  <version>/ iteration_plan.md, iteration_plan.json
    「S3 原型导出」/    <version>/ prototype.md
    「S4 流程图导出」/  <version>/ business_flow.md
    「S5 测试点生成」/  <version>/ test_points.json
    「S6 测试用例生成」/<version>/ test_cases.md, test_cases.json, test_cases.xlsx
                                 review_report.md, review_report.json
    「S8 自迭代」/     <version>/ iteration.md, iteration.json
  feedback_logs/
  flowchart_library/
  test_point_library/
  test_case_library/
  feedback_archive/
```

---

## S1 Input Processing Pipeline (DOCX → Markdown + OCR)

A modular pipeline that converts DOCX files to Markdown with semantic image references and OCR text extraction.

**Location**: `ai_workflow/stage_s1_input/`

| Module | File | Purpose |
|--------|------|---------|
| `DocxExtractor` | `docx_extractor.py` | Parse .docx/.doc, extract text + images as raw bytes |
| `ImageRenamer` | `image_renamer.py` | Classify images via OCR preview → semantic tag (e.g. `ui_prototype`, `flow_chart`) |
| `OCREngine` | `ocr_engine.py` | Tesseract OCR → structured JSON with confidence + extracted elements |
| `MarkdownConverter` | `md_converter.py` | Build .md with semantic image references (`img_001_flow_chart.png`) |
| `S1Pipeline` | `pipeline.py` | Orchestrate all modules end-to-end |

**Usage**:

```python
from ai_workflow.stage_s1_input import run_s1_pipeline

result = run_s1_pipeline(
    docx_path="/path/to/requirements.docx",
    req_name="游戏道具商城系统",
    version="v1.0",
)
# Output: workflow_assets/游戏道具商城系统/「S1 需求评审」/v1.0/raw/
```

**Output structure**:
```
workflow_assets/<req_name>/「S1 需求评审」/v1.0/
  raw/
    extracted_text.md              ← Markdown with semantic image refs
    image_index.json               ← Central index: ref ↔ metadata
    extracted_images/
      img_001_ui_prototype.png     ← Renamed by semantic analysis
      img_002_flow_chart.png
    ocr_results/
      img_001_ui_prototype.json    ← OCR structured result
      img_002_flow_chart.json
  review_report.md
  review_report.json
```

**Image reference naming**: `img_<index>_<semantic_tag>.<ext>`
- Semantic tags: `ui_prototype`, `flow_chart`, `data_schema`, `sequence_diagram`, `architecture`, `table`, `diagram`, `screenshot`
- OCR JSON fields: `image_ref`, `image_path`, `ocr_text`, `extracted_elements`, `confidence`, `page`

**Requirements**: `python-docx`, `pytesseract`, `Pillow`, Tesseract binary

---

## Automation Modules

| Module | Function | Purpose |
|--------|----------|---------|
| `requirement_reviewer_auto` | `auto_review_requirement()` | S1 规则引擎：自动评分（5维度加权） |
| `test_case_formatter` | `compose_test_points_from_structure()` | S5 骨架生成：从 breakdown 生成测试点结构 |
| `test_case_formatter` | `format_test_cases()` | S6 格式化：自动ID分配、字段规范化、去重 |
| `auto_reviewer` | `auto_review()` | S7 审查：结构验证+覆盖率计算+通过判定 |
| `iteration_aggregator` | `aggregate_iteration_data()` | S8 聚合：反馈日志+审核报告统计 |
| `run_s1_pipeline` | `run_s1_pipeline()` | S1 输入处理：DOCX → Markdown + OCR 自动化 |
