---
name: aidocx-feedback-logger
description: >
  从 Excel/CSV/JSON 文件导入测试用例执行反馈和审查结果，自动标准化并保存到 feedback_logs/
  Use when importing test case execution feedback from Excel/CSV/JSON files.
  使用当需要从 Excel/CSV/JSON 文件导入测试用例执行反馈时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: feedback-logger
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow — 反馈收集与导入 Skill

## 功能概述

`feedback_logger` 模块支持从多种来源导入反馈，自动识别 Excel sheet 列名，标准化后保存。

## 核心函数

### `import_feedback()` — 通用导入

```python
from ai_workflow.feedback_logger import import_feedback

result = import_feedback(
    feedback_file="/path/to/feedback.xlsx",
    review_file="/path/to/review.xlsx",   # 可选
    output_dir="/path/to/feedback_logs/",
    version="v1.0",
    req_name="游戏道具商城系统",
    merge_duplicates="latest",            # "latest" | "first" | "all"
)
```

### `import_from_test_cases_xlsx()` — 从 test_cases.xlsx 导入

```python
from ai_workflow.feedback_logger import import_from_test_cases_xlsx

# 自动读「反馈结果」或「执行追踪」sheet
result = import_from_test_cases_xlsx(
    xlsx_path="/path/to/test_cases.xlsx",
    version="v1.0",
)
```

### CLI 用法

```bash
# 从 Excel 导入（自动探测反馈结果 sheet）
python3 -m ai_workflow.feedback_logger --file feedback.xlsx

# 从 test_cases.xlsx 读执行追踪 sheet
python3 -m ai_workflow.feedback_logger --file test_cases.xlsx

# 同时提供反馈和审查结果
python3 -m ai_workflow.feedback_logger \
    --file feedback.xlsx \
    --review review.xlsx \
    --version v1.0
```

---

## 支持的文件格式

### Excel 文件

自动探测以下 sheet，按优先级依次查找：

**反馈 sheet（`import_feedback`）：**
1. `反馈结果`
2. `执行追踪`
3. `执行记录`
4. `用例详情`

**审查 sheet（`import_feedback --review`）：**
1. `审核结果`
2. `审查结果`
3. `review`

**test_cases.xlsx 专属 sheet（`import_from_test_cases_xlsx`）：**
1. `反馈结果`
2. `执行追踪` ← `test_cases.xlsx` 的这个 sheet 就是反馈数据
3. `执行记录`

### CSV 文件

自动识别 GBK/UTF-8 编码，首行作为列头。

### JSON 文件

支持三种格式：
```json
// 格式 1: 顶层数组
[{"case_id": "UI-TC-001", "result": "PASS", ...}]

// 格式 2: 对象含 entries 字段
{"entries": [{"case_id": "...", ...}]}

// 格式 3: 单条记录
{"case_id": "UI-TC-001", "result": "PASS", ...}
```

---

## 自动列名映射

模块自动将各种中文/英文列名映射到标准字段：

| 标准字段 | 支持的中文列名 | 支持的英文列名 |
|----------|---------------|---------------|
| `case_id` | 用例ID, 用例编号, 测试用例ID | case_id, test_case_id |
| `result` | 执行结果, 测试结果, 执行状态 | result, test_result, status |
| `actual_result` | 实际结果, 实际输出, 观测结果 | actual_result, actual_output |
| `defect_desc` | 缺陷描述, 问题描述, 缺陷说明 | defect_desc, bug_description, issue |
| `severity` | 严重程度, 缺陷等级 | severity, bug_severity, priority |
| `reviewer` | 审核人, 审核者 | reviewer, auditor |
| `review_result` | 审核结果, 审查结果 | review_result, audit_result |
| `module` | 模块, 所属模块 | module |
| `title` | 用例描述, 用例名称 | title, test_title |
| `execution_time` | 执行时间, 测试时间 | execution_time, test_time |

**结果值自动标准化：**

`result` 字段 → `PASS` / `FAIL` / `BLOCKED` / `DRAFT`
- ✅ 通过/成功/PASS/pass → `PASS`
- ❌ 失败/不通过/FAIL/fail → `FAIL`
- 阻塞/阻断/BLOCKED → `BLOCKED`
- 待执行/未执行/DRAFT → `DRAFT`

`severity` 字段 → `CRITICAL` / `MAJOR` / `MINOR` / `LOW`
- P0/阻断级/致命 → `CRITICAL`
- P1/严重 → `MAJOR`
- P2/一般 → `MINOR`
- P3/轻微/提示 → `LOW`

---

## 输出格式

导入后生成 `feedback_<req_name>_<version>_<timestamp>.json`：

```json
{
  "version": "v1.0",
  "entries": [
    {
      "case_id": "界面-TC-001",
      "result": "PASS",
      "actual_result": "弹窗正常展示道具名称和总价",
      "defect_desc": "",
      "severity": "",
      "module": "界面",
      "title": "购买确认流程",
      "execution_time": "2026-06-13",
      "notes": "",
      "import_time": "2026-06-13 12:00:00"
    },
    {
      "case_id": "业务-TC-002",
      "result": "FAIL",
      "actual_result": "余额计算错误，实际扣款比预期多",
      "defect_desc": "购买50个道具时，余额扣款 = 50 * 单价，但总价显示 = 49 * 单价",
      "severity": "CRITICAL",
      "module": "业务",
      "title": "购买确认弹窗余额对比",
      "notes": "复现步骤：道具单价=100，余额=10000，购买数量=50"
    }
  ],
  "count": 2
}
```

---

## 用法示例

### 场景 1：从测试工程师提交的 Excel 导入

```bash
python3 -m ai_workflow.feedback_logger \
    --file ~/Desktop/用例执行结果_20260613.xlsx \
    --version v1.0
```

### 场景 2：从 test_cases.xlsx 的执行追踪 sheet 导入

```bash
python3 -m ai_workflow.feedback_logger \
    --file workflow_assets/游戏道具商城系统/v1.0/「S6 测试用例生成」/test_cases.xlsx \
    --version v1.0
```

### 场景 3：同时导入执行反馈 + 审查结果

```bash
python3 -m ai_workflow.feedback_logger \
    --file 反馈结果_20260613.xlsx \
    --review 审核结果_20260613.xlsx \
    --version v1.0 \
    --output workflow_assets/feedback_logs/
```

### 场景 4：在对话中用 Python 调用

```
请帮我将 ~/Desktop/测试反馈.xlsx 导入到反馈日志中。
```

```python
import sys
sys.path.insert(0, "/Users/gleon/Documents/TestDev/AIDocxWorkFlow")
from ai_workflow.feedback_logger import import_feedback

result = import_feedback(
    feedback_file="/Users/gleon/Desktop/测试反馈.xlsx",
    version="v1.0",
)
print(f"导入成功: PASS={result.pass_count}, FAIL={result.fail_count}")
```

---

## 导入结果摘要示例

```
=====================================================
  反馈导入结果
=====================================================
  来源文件：/path/to/feedback.xlsx
  用例总数：195
  ✅ PASS:      87
  ❌ FAIL:      12
  ⏸ BLOCKED:    3
  📝 DRAFT:     93
  保存至：
    - workflow_assets/feedback_logs/feedback_游戏道具商城系统_v1.0_20260613_120000.json
=====================================================
```
