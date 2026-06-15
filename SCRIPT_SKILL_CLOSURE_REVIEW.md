# 脚本-SKILL 逻辑闭环审查报告

**审查日期**：2026-06-15
**审查范围**：ai_workflow/ 下的 11 个 Python 脚本 + 13 个 SKILL.md
**设计哲学**：`LLM 负责推理 + 语义审查，脚本只做格式整理`——禁止脚本做硬指标审查

---

## 总览

| 指标 | 结果 |
|------|------|
| 脚本总数 | 11 |
| SKILL.md 总数 | 13 |
| 与阶段对应 | 9 个脚本对应 9 个阶段 ✓；2 个孤儿 |
| 违反 LLM 推理原则的脚本 | **2 个（P0 问题）** |
| 脚本-SKILL 引用断裂 | **5 处（P0 问题）** |
| 脚本缺失 CLI | **2 个** |
| 闭环断裂点 | **7 个** |

### 脚本-SKILL 引用断裂一览

| 断裂点 | 来源 SKILL 引用 | 目标函数/文件 | 实际存在 |
|--------|---------------|--------------|---------|
| 1 | aidocx-s5-test-points SKILL.md §自动化支持 | `_build_fallback_scenarios` | **不存在** |
| 2 | aidocx-s5-test-points SKILL.md §自动化支持 | `save_stage5_output` | **不存在** |
| 3 | aidocx-s7-review SKILL.md §自动化支持 | `auto_review()` 有 `overall_pass` | **v2.0 已废弃** |
| 4 | aidocx-s7-review SKILL.md §自动化支持 | `ai_workflow/auto_reviewer` 的 `overall_pass` 字段 | **不存在** |
| 5 | aidocx-s7-review SKILL.md §自动化支持 | `reviewer_b['s4_risk_coverage']` 字段 | **不存在** |
| 6 | aidocx-s7-review SKILL.md §自动化支持 | `reviewer_b['uncovered_risks']` 字段 | **不存在** |
| 7 | aidocx-workflow-conversation SKILL.md §S7执行 | `make_stage6_skill()` | **不存在** |
| 8 | aidocx-workflow-conversation SKILL.md §S7执行 | `make_stage7_skill()` | **不存在** |
| 9 | aidocx-s8-self-iteration SKILL.md §自动化支持 | `self_iteration.py` | **不存在** |
| 10 | aidocx-s4-flowchart SKILL.md §自动化支持 | `ai_workflow/s4_validator.py` | **不存在** |
| 11 | aidocx-s4-flowchart SKILL.md §自动化支持 | `validate_s4_output` | **不存在** |
| 12 | aidocx-s4-flowchart SKILL.md §自动化支持 | `report['risk_id_duplicates']` | **不存在** |
| 13 | aidocx-workflow-conversation SKILL.md §S5执行 | `_build_fallback_scenarios` | **不存在** |

---

## 脚本与阶段映射表

| 脚本 | 对应阶段 | 状态 | 评分 |
|------|---------|------|------|
| `requirement_reviewer_auto.py` | S1 | ✓ 合理 | 7/10 |
| `test_case_formatter.py` | S5/S6 | ✓ 合理（v3.0 修复后） | 9/10 |
| `s6_generate.py` | S6 | ✓ 合理 | 9/10 |
| `s6_xlsx_enhance.py` | S6 | ✓ 合理 | 9/10 |
| `auto_reviewer.py` | S7 | ✗ 越界（S7 SKILL.md 引用不存在的 API） | 6/10 |
| `iteration_aggregator.py` | S8 | ✗ SKILL.md 引用不存在的 `self_iteration.py` | 5/10 |
| `validate_skills.py` | 工具 | ✓ 合理 | 8/10 |
| `conversation_skills.py` | S2/S2.5/S3/S4 | ✓ 合理 | 9/10 |
| `feedback_logger.py` | 工具 | ✓ 合理 | 9/10 |
| `upgrade_skills.py` | 工具 | ✓ 合理 | 8/10 |
| `__init__.py` | - | 空文件 | N/A |

---

## 逐脚本审查

### 1. ai_workflow/requirement_reviewer_auto.py

**对应阶段**：S1

**是否违反 LLM 推理原则**：✗ **部分违反（行 1-176）**

该脚本是一个**规则引擎**（regex 关键词匹配），而非 AI 推理引擎。其逻辑存在以下问题：

- **加权公式硬编码**（行 16-21）：`_DIMENSIONS` 权重固定为 completeness=0.25 / clarity=0.25 / consistency=0.20 / testability=0.20 / feasibility=0.10。这些权重是项目经验的结晶，**LLM 应该自己决定各维度重要性**。
- **判决阈值硬编码**（行 23）：`_GATE_THRESHOLD = 7.0` 固定值。SKILL.md 的判决规则（≥7.0 PASS / 4.0-6.9 NEEDS_REVISION / <4.0 REJECT）与此对齐，但 SKILL.md 本身也是硬编码阈值。
- **正则匹配打分**（行 28-95）：`_score_completeness` / `_score_clarity` 等函数用 regex 关键词匹配打分——这是**机械规则**，非语义推理。真实需求"清晰度"需要理解上下文，不是"可能|也许"出现几次扣几分。

**与 SKILL.md 一致性**：⚠️ **行 329 注释已标记不一致**

```python:329:329
# ai_workflow/requirement_reviewer_auto.py
# ⚠️ 仍按"4 项内容门禁"实现，待对齐本次重构
```

SKILL.md（aidocx-s1-review v2.0 重构）已将"内容门禁"改为"5 维度评分 + 角色定义 + 需求对象 + 问题需求"4 段审查产物，但脚本仍按旧版"4 项内容门禁"逻辑运行（代码中没有角色定义提取、需求对象拆解）。

**调用关系**：
- 被 `conversation_skills.py::execute_simple_flow()` 调用（行 737）
- 被 `aidocx-workflow-conversation SKILL.md` 引用（§第一步）

**评分**：7/10

**问题**：
- 脚本是规则引擎，符合"非 AI"设计意图——但 SKILL.md 已更新为 5 维度评审（包含角色定义等），脚本未同步更新。

---

### 2. ai_workflow/test_case_formatter.py

**对应阶段**：S5/S6

**是否违反 LLM 推理原则**：✓ **不违反**

- `_derive_equivalence_classes()`（行 109-145）：从 story 推导等价类，但仅做关键词匹配（数值/余额/价格/支付/VIP），**不涉及语义推理**，属于格式整理。
- `_derive_boundary_values()`（行 148-159）：从输入参数推导边界值，仅做数值化处理，属于格式整理。
- `_assign_ids()`（行 384-418）：ID 分配 + 模块归一化，机械操作。
- `_build_summary()`（行 456-474）：按模块汇总统计，机械操作。
- `compose_test_points_from_structure()`（行 22-106）：从 backlog 生成测试点骨架，**自动生成等价类和边界值**，AI 只需填充 `scenario_test_points`。这是**合理的自动化分工**。

**与 SKILL.md 一致性**：✓ **v3.0 修复后完全一致**

- SKILL.md 要求 10 列（用例ID/模块/用例描述/功能描述/前置条件/操作步骤/预期结果/优先级/用例状态/备注），`_save_md()` 和 `_save_xlsx()` 均已对齐。
- 模块归一化支持中英双语 + 旧 v1.1 缩写，与 SKILL.md §用例格式严格一致。
- `_MODULE_NAME_NORMALIZE` 覆盖全部 8 模块，与 MODULES.md §1 一致。

**调用关系**：
- 被 `s6_generate.py` 导入（`_assign_ids`, `_build_summary`, `_save_md`, `_save_xlsx`, `normalize_module_name`）
- 被 `auto_reviewer.py` 导入（`normalize_module_name`）
- `migrate_test_points_file()` 提供 CLI `--migrate-modules`

**CLI 文档**：✓ `--migrate-modules` CLI，文档清晰（行 593-616）

**评分**：9/10

---

### 3. ai_workflow/s6_generate.py

**对应阶段**：S6

**是否违反 LLM 推理原则**：✓ **不违反**

设计哲学与 SKILL.md §自动化支持（thin wrapper）严格一致：
- 优先读取 `llm_generated_cases`（LLM 推理结果）
- 兜底 1:1 转种子 case（不做"1:N 拓宽"或"18种方法加权"）
- 只做 ID 分配 / 字段归一化 / 写文件

**与 SKILL.md 一致性**：✓ **一致**

SKILL.md aidocx-s6-test-cases 明确："脚本只做整理：ID 分配 / 字段归一化 / 输出 JSON+MD+XLSX"，本脚本完全遵守。

**调用关系**：
- 导入 `test_case_formatter` 的 `_assign_ids`, `_build_summary`, `_save_md`, `_save_xlsx`, `normalize_module_name`
- 硬编码路径 `S5_PATH` 和 `OUT_DIR`（行 39-46）

**CLI**：仅 `if __name__ == "__main__": main()`，无 argparse，无 `--help`，CLI 不友好。

**评分**：9/10（扣 1 分：无 CLI 文档）

---

### 4. ai_workflow/s6_xlsx_enhance.py

**对应阶段**：S6

**是否违反 LLM 推理原则**：✓ **不违反**

纯字段搬运 + 机械 Counter 统计，不涉及任何推理。

**与 SKILL.md 一致性**：⚠️ **部分不一致**

SKILL.md aidocx-s6-test-cases 要求 10 列：
```
用例ID / 模块 / 用例描述 / 功能描述 / 前置条件 / 操作步骤 / 预期结果 / 优先级 / 用例状态 / 备注
```

但 `s6_xlsx_enhance.py` 的 Sheet 1 表头（行 31-32）：
```python
["用例ID", "Story", "TP", "标题", "模块", "前置条件",
 "操作步骤", "预期结果", "优先级", "用例类型", "用例状态"]
```

差异：
1. 多出 "Story" / "TP" 列（不在 SKILL.md 10 列中）
2. "标题" ≠ SKILL.md 的"用例描述"
3. "用例类型" 不在 SKILL.md 10 列中（SKILL.md 用"用例状态"但这里是第11列）
4. **缺少** "功能描述" 列（第3列要求有，Sheet 1 没有）
5. **缺少** "备注" 列（SKILL.md 第10列，Sheet 1 没有）

`s6_xlsx_enhance.py` 与 `test_case_formatter._save_xlsx()` 存在**表头不一致**，会导致同一 test_cases.json 被两个脚本生成出不同格式的 xlsx。

**调用关系**：无导入，独立运行。

**CLI**：仅 `if __name__ == "__main__": main()`，无 argparse。

**评分**：7/10（扣 2 分：表头与 SKILL.md 不一致 + 与 test_case_formatter._save_xlsx() 不一致）

---

### 5. ai_workflow/auto_reviewer.py

**对应阶段**：S7

**是否违反 LLM 推理原则**：✓ **不违反**

v2.0 重构后设计哲学正确：
- 脚本只做机械统计（字段填写检查、模块归一化、Epic/Story 覆盖统计）
- **不做 PASS/FAIL 判决**
- 判决交给 LLM（`ai_input_summary` 作为 LLM 输入）

**与 SKILL.md 一致性**：✗ **多处引用不存在的 API**

SKILL.md aidocx-s7-review §自动化支持（行 126-134）写：

```python
from ai_workflow.auto_reviewer import auto_review
review_result = auto_review(test_cases, test_points, s4_risks)
# review_result['overall_pass'] ∈ {True, False}
# review_result['reviewer_b']['s4_risk_coverage'] ∈ [0.0, 1.0]
# review_result['reviewer_b']['uncovered_risks']  # 未覆盖的风险点列表
```

实际情况：
1. `auto_review()` **已废弃**（v2.0），返回 `ReviewSnapshot` 而非含 `overall_pass` 的 dict
2. `ReviewSnapshot` **没有** `reviewer_b['s4_risk_coverage']` 字段（SKILL.md 说有，实际没有）
3. `ReviewSnapshot` **没有** `reviewer_b['uncovered_risks']` 字段（SKILL.md 说有，实际没有）
4. `save_review_report()` 输出 `review_snapshot.json`（行 217），但 SKILL.md §成功产出行 113-114 要求输出 `review_report.md` + `review_report.json`——**文件名不一致**

另外，`aidocx-workflow-conversation SKILL.md` 行 162-174 引用：
- `make_stage6_skill()` 和 `make_stage7_skill()`——这两个函数**在 conversation_skills.py 中不存在**（grep 结果确认只有 S2/S2.5/S3/S4，没有 S6/S7）

**调用关系**：
- 导入 `test_case_formatter.normalize_module_name`
- `__main__` 有 demo 入口

**评分**：6/10

---

### 6. ai_workflow/iteration_aggregator.py

**对应阶段**：S8

**是否违反 LLM 推理原则**：✓ **不违反**

`_analyze_defects()` 仅做 FAIL 记录的筛选 + 模块分组 + Counter 统计，不做语义推理。

**与 SKILL.md 一致性**：✗ **多处断裂**

SKILL.md aidocx-s8-self-iteration §自动化支持（行 175-185）写：

```python
from ai_workflow.self_iteration import analyze_and_iterate
result = analyze_and_iterate(version, review_report, test_points, test_cases, s4_risks)
# result['verdict']        # "PASS" / "FAIL"
# result['root_causes']    # 根因列表

from ai_workflow.self_iteration import archive_experience
archive_experience(result, version)
```

实际情况：
- **`self_iteration.py` 文件不存在**（grep 搜索确认整个 ai_workflow 目录下无此文件）
- `iteration_aggregator.py` 的函数名是 `aggregate_iteration_data()`，与 SKILL.md 引用的 `analyze_and_iterate()` 不一致
- SKILL.md 要求输出 `iteration.json`（含 `verdict` / `root_causes`），但 `iteration_aggregator.py` 输出的是 `iteration_stats.json`（含 `defect_patterns` / `top_epic_defects` / `ai_summary`），**字段结构完全不同**
- `save_iteration_report()` 只保存 `iteration_stats.json`，SKILL.md 要求的 `iteration.md` 和 `iteration.json` 均未生成

**调用关系**：可独立运行，无其他脚本导入。

**CLI**：无 argparse，无文档。

**评分**：5/10（多个 P0 断裂）

---

### 7. ai_workflow/validate_skills.py

**对应阶段**：工具

**是否违反 LLM 推理原则**：✓ **不违反**

纯 YAML 解析 + 正则校验，无推理。

**与 SKILL.md 一致性**：N/A（无对应 SKILL）

**调用关系**：CLI 入口，可独立运行。

**CLI**：✓ 完整 argparse，文档清楚（行 248-253）。

**评分**：8/10

---

### 8. ai_workflow/conversation_skills.py

**对应阶段**：S2 / S2.5 / S3 / S4

**是否违反 LLM 推理原则**：✓ **不违反**

- `make_stage*_skill()` 函数生成 system_prompt + user_template，是 prompt 工厂
- `save_stage*_output()` 函数保存文件，无推理逻辑
- `execute_simple_flow()` / `execute_full_flow()` 是状态查询/流水线编排

**与 SKILL.md 一致性**：⚠️ **缺少 S5/S6/S7/S8 的 make/save 函数**

SKILL.md aidocx-s5-test-points §自动化支持引用 `save_stage5_output`（行 255），不存在。

SKILL.md aidocx-workflow-conversation §S7 执行引用 `make_stage6_skill()` 和 `make_stage7_skill()`（行 162/180），不存在。

**调用关系**：
- 导入 `requirement_reviewer_auto.auto_review_requirement`
- 被 workflow-conversation SKILL.md 引用（多处）

**CLI**：无（`if __name__ == "__main__": execute_full_flow()` 仅 demo）。

**评分**：9/10

---

### 9. ai_workflow/feedback_logger.py

**对应阶段**：工具

**是否违反 LLM 推理原则**：✓ **不违反**

纯文件读取 + 字段映射 + 标准化，无推理。

**与 SKILL.md 一致性**：✓ **与 aidocx-feedback-logger SKILL.md 完全一致**

`import_feedback()` / `import_from_test_cases_xlsx()` 与 SKILL.md §核心函数一一对应。

**调用关系**：可独立运行，被 workflow-conversation SKILL.md 引用。

**CLI**：✓ 完整 argparse，文档清楚（行 592-629）。

**评分**：9/10

---

### 10. ai_workflow/upgrade_skills.py

**对应阶段**：工具

**是否违反 LLM 推理原则**：✓ **不违反**

纯文件操作 + YAML frontmatter 修改，无推理。

**与 SKILL.md 一致性**：N/A（无对应 SKILL）

**调用关系**：CLI 入口，可独立运行。

**CLI**：✓ 完整 argparse，文档清楚（行 180-204，含 dry-run）。

**评分**：8/10

---

### 11. ai_workflow/__init__.py

**对应阶段**：-

仅两行注释，无任何函数定义。这是一个**空文件**。

---

## 数据流闭环分析

### S2 → S5 数据流

| 维度 | 状态 |
|------|------|
| backlog.json 的 story 字段 | ✓ 被 `test_case_formatter.compose_test_points_from_structure()` 消费 |
| story.acceptance_criteria | ✓ 被 `_derive_equivalence_classes()` 提取关键词（行 76-80） |
| story.precondition / input_data / expected_output | ✓ 被搬运到测试点骨架（行 71-74） |
| S5 缺少 save 函数 | ✗ `save_stage5_output` 不存在 |

**断裂点**：`test_case_formatter` 有 `compose_test_points_from_structure()`，但 SKILL.md 引用的 `save_stage5_output()` 不存在——**S5 输出需要 LLM 手工 write_file**。

---

### S5 → S6 数据流

**S5 输出 test_points.json 的关键字段**（来自 aidocx-s5-test-points SKILL.md §1.6 强制输出字段）：

| 字段 | SKILL.md 要求 | test_case_formatter/s6_generate.py 是否消费 |
|------|-------------|-------------------------------------|
| `tp_id` | 必填 | ✗ `_tp_to_seed_case()` 只取 `tp.get("scenario")` → 丢失 `tp_id` |
| `module` | 必填（8模块） | ✓ `tp.get("module")` → case["module"] |
| `test_point_type` | 必填 | ✓ `tp.get("test_type", "POSITIVE")` → case["test_type"] |
| `test_type_subclass` | 必填 | ✗ 未被提取 |
| `description` | 必填 | ✗ 未被提取（只有 `scenario` → `用例描述`）|
| **`s4_reference`** | 必填 | ✗ **未被提取** |
| `boundary` | 必填 | ✗ 未被提取 |
| `is_assumed` | 必填 | ✗ 未被提取 |
| `applies_rule` | 必填 | ✗ 未被提取 |
| `precondition` | 来自 story | ✓ 被搬运 |
| `expected` | 来自 story | ✓ 被搬运 |
| `story_id` | 溯源 | ✓ 被搬运 |
| `scenario` | → 用例描述 | ✓ 被搬运 |

**断裂点（P0）**：
1. **`s4_reference` 字段丢失**：S5 最重要的字段（EXCEPTION TP 与 S4 风险点的关联）在 S6 完全丢失——`s6_generate._tp_to_seed_case()` 没有提取 `s4_reference`，导致 S7 无法做 S4 风险点覆盖率审查。
2. **`test_type_subclass` 字段丢失**：S5 TP 的子类枚举在 S6 丢失。
3. **`applies_rule` 字段丢失**：S5 TP 的判定过程记录在 S6 丢失。
4. **`is_assumed` 字段丢失**：S5 TP 的业务假设标记在 S6 丢失。
5. **`tp_id` 字段未保留**：S5 生成的 `tp_id` 未传递到 case 的 `备注` 字段（S6 的 `备注` 只填了 `tp_id` 字符串，未填完整 ID）。

**s6_generate.py 的 `_tp_to_seed_case()` 当前实现**（行 50-81）：

```python
def _tp_to_seed_case(tp: dict, story: dict) -> dict:
    return {
        "case_id": "",
        "module": tp.get("module", ""),
        "模块": tp.get("module", ""),
        "用例描述": tp.get("scenario", ""),
        "title": tp.get("scenario", ""),
        "功能描述": "",     # ← S5 有 description，这里没填
        "前置条件": tp.get("precondition", ""),
        "操作步骤": "",
        "预期结果": tp.get("expected", ""),
        # 缺少：s4_reference / test_type_subclass / applies_rule / is_assumed / tp_id
    }
```

---

### S6 → S7 数据流

**S6 输出 test_cases.json 的关键字段**（来自 aidocx-s6-test-cases SKILL.md）：

| 字段 | SKILL.md 要求 | auto_reviewer.py 是否消费 |
|------|-------------|----------------------|
| `case_id` | 必填 | ✓ `case_id` 检查 |
| `title` / `用例描述` | 必填 | ✓ `("title", "用例描述")` |
| `precondition` / `前置条件` | 必填 | ✓ |
| `steps` / `操作步骤` | 必填 | ✓ |
| `expected` / `预期结果` | 必填 | ✓ |
| `module` | 必填（8模块） | ✓ `normalize_module_name` |
| `test_type` | 可选 | ✓ `_type_stats()` |
| `story_id` | 溯源 | ✓ `_check_coverage()` |
| `s4_reference` | SKILL.md 无强制 | ✗ 未被检查（但 s6_generate 未传递）|
| `is_assumed` | SKILL.md 无强制 | ✗ 未被检查 |
| `applies_rule` | SKILL.md 无强制 | ✗ 未被检查 |

**S7 输出字段 vs SKILL.md 要求**：

| SKILL.md §成功产出要求的字段 | auto_reviewer.py 实际输出 |
|--------------------------|----------------------|
| `review_report.md` | ✗ 输出的是 `review_snapshot.md` |
| `review_report.json` | ✗ 输出的是 `review_snapshot.json` |
| `reviewer_b.s4_risk_coverage` | ✗ 不存在 |
| `reviewer_b.uncovered_risks` | ✗ 不存在 |
| `overall_pass` | ✗ v2.0 已废弃（但 SKILL.md 仍在引用）|

**断裂点**：
1. 输出文件名不一致：`review_snapshot.*` vs `review_report.*`
2. S7 的 `review_snapshot` 不含 S4 风险点覆盖率数据（`s4_risk_coverage` / `uncovered_risks`）——因为 S6 的 case 没有传递 `s4_reference`，auto_reviewer 无法做 S4 覆盖率检查。

---

### S7 → S8 数据流

**S7 输出字段 vs S8 消费期望**：

| S7 输出字段 | S8 期望字段 | 状态 |
|-----------|-----------|------|
| `ReviewSnapshot` | `iteration_stats.defect_patterns` | ⚠️ 字段名不同 |
| `CoverageSnapshot` | `top_epic_defects` | ⚠️ 结构不同 |
| 无 | `verdict` | ✗ 不存在 |
| 无 | `root_causes` | ✗ 不存在 |
| `ai_summary` (~400 chars) | ✓ 存在 |

**断裂点**：
1. S8 SKILL.md 要求读取 `review_report.json` 的 `overall_pass` / `reviewer_b` 字段，但 S7 输出的 `review_snapshot.json` 没有这些字段。
2. `iteration_stats.json`（iteration_aggregator 产出）没有 `verdict` / `root_causes` / `archive_summary` / `next_iteration_focus`——这些都是 S8 SKILL.md 要求的字段，但 aggregator.py 没有生成。
3. **`self_iteration.py` 不存在**——S8 应该有一个主脚本负责根因分析和迭代建议，但目前只有 `iteration_aggregator.py` 负责数据聚合（而非分析）。

---

## P0 级问题（必须修）

### P0-1：s6_generate.py 丢失 S5 核心字段

**位置**：`s6_generate.py` 行 50-81 `_tp_to_seed_case()`

**问题**：S5 test_points.json 的 `s4_reference` / `test_type_subclass` / `applies_rule` / `is_assumed` 等字段被完全丢弃，导致 S7 无法做 S4 风险点覆盖率审查（S7 的核心价值之一）。

**修复建议**：`_tp_to_seed_case()` 应保留所有 S5 TP 字段到 case 的 `备注` 或新增字段：

```python
def _tp_to_seed_case(tp: dict, story: dict) -> dict:
    return {
        # ... 现有字段 ...
        "备注": f"tp_id={tp.get('tp_id','')} s4_ref={tp.get('s4_reference','')} "
                f"is_assumed={tp.get('is_assumed', False)}",
        # 或直接加到 case 顶层
        "s4_reference": tp.get("s4_reference", ""),
        "test_type_subclass": tp.get("test_type_subclass", ""),
        "is_assumed": tp.get("is_assumed", False),
        "applies_rule": tp.get("applies_rule", ""),
    }
```

---

### P0-2：iteration_aggregator.py 的 SKILL.md 引用完全断裂

**位置**：
- `aidocx-s8-self-iteration SKILL.md` 行 175-185 引用不存在的 `self_iteration.py`
- `iteration_aggregator.py` 的 API 与 SKILL.md 不一致

**问题**：
1. SKILL.md 说用 `from ai_workflow.self_iteration import analyze_and_iterate`，但文件不存在
2. SKILL.md 说输出 `verdict` / `root_causes` / `archive_summary`，但 aggregator 输出的是 `defect_patterns` / `top_epic_defects` / `ai_summary`
3. SKILL.md 说 S8 读取 `review_report.json` 的 `overall_pass` / `reviewer_b`，但 S7 输出的是 `review_snapshot.json`（无这些字段）

**修复建议**：
- 选项 A（推荐）：重命名 `iteration_aggregator.py` → `self_iteration.py`，实现 `analyze_and_iterate()` 和 `archive_experience()`，使其与 SKILL.md §自动化支持对齐
- 选项 B：更新 SKILL.md §自动化支持，引用实际的 `iteration_aggregator.aggregate_iteration_data()`

---

### P0-3：auto_reviewer.py 与 SKILL.md 的 API 引用断裂

**位置**：
- `aidocx-s7-review SKILL.md` 行 126-134 引用不存在的 `overall_pass` / `reviewer_b` 字段
- `aidocx-workflow-conversation SKILL.md` 行 162/180 引用不存在的 `make_stage6_skill()` / `make_stage7_skill()`

**问题**：多个 SKILL.md 引用了代码中不存在的 API。

**修复建议**：
1. 更新 aidocx-s7-review SKILL.md §自动化支持，引用实际的 `auto_reviewer.snapshot()` API（v2.0），删除对 `overall_pass` / `reviewer_b` 的引用
2. 更新 aidocx-workflow-conversation SKILL.md，删除对 `make_stage6_skill()` / `make_stage7_skill()` 的引用（S6/S7 完全靠 SKILL.md 引导 LLM）

---

### P0-4：s6_xlsx_enhance.py 表头与 SKILL.md 不一致

**位置**：`s6_xlsx_enhance.py` 行 31-32

**问题**：Sheet 1 表头与 SKILL.md aidocx-s6-test-cases 要求的 10 列不一致，且与 `test_case_formatter._save_xlsx()` 的 `_XLSX_HEADERS_V3` 不一致。

| 列 | SKILL.md | s6_xlsx_enhance | test_case_formatter._save_xlsx |
|----|---------|-----------------|-------------------------------|
| 1 | 用例ID | 用例ID ✓ | 用例ID ✓ |
| 2 | 模块 | Story ✗ | 模块 ✓ |
| 3 | 用例描述 | TP ✗ | 用例描述 ✓ |
| 4 | 功能描述 | 标题 ✗ | 功能描述 ✓ |
| 5 | 前置条件 | 前置条件 ✓ | 前置条件 ✓ |
| 6 | 操作步骤 | 操作步骤 ✓ | 操作步骤 ✓ |
| 7 | 预期结果 | 预期结果 ✓ | 预期结果 ✓ |
| 8 | 优先级 | 优先级 ✓ | 优先级 ✓ |
| 9 | 用例状态 | 用例类型 ✗ | 用例状态 ✓ |
| 10 | 备注 | 用例状态 ✗ | 备注 ✓ |

**修复建议**：删除 `s6_xlsx_enhance.py`（功能已被 `test_case_formatter._save_xlsx()` 覆盖且格式正确），或在 `s6_xlsx_enhance.py` 中导入 `_XLSX_HEADERS_V3` 保持一致。

---

## P1 级问题（建议修）

### P1-1：s6_xlsx_enhance.py 与 test_case_formatter._save_xlsx() 重复

两个脚本都能生成 test_cases.xlsx，功能高度重叠，但表头不一致。建议：
- 保留 `test_case_formatter._save_xlsx()`（v3.0 正确表头）
- 删除 `s6_xlsx_enhance.py`，或将其改造为"增强工具"（加额外分析 sheet，不覆盖主 sheet）

### P1-2：requirement_reviewer_auto.py 与 SKILL.md 的角色定义/需求对象不对齐

SKILL.md aidocx-s1-review v2.0 要求产出 4 段审查产物（角色定义/需求对象/问题需求/5维度评分），但脚本只有评分逻辑。建议：
- 选项 A：更新 SKILL.md §自动化支持，注明脚本只做评分，其他产物由 LLM 手工生成
- 选项 B：扩展脚本支持角色定义提取（基于 regex 关键词）

### P1-3：conversation_skills.py 缺少 S5/S6/S7/S8 的 make/save 函数

SKILL.md 多处引用 `save_stage5_output()` / `make_stage6_skill()` 等函数，但实际不存在。建议：
- 在 conversation_skills.py 中添加这些函数的桩（存根），避免 SKILL.md 引用报错
- 或更新 SKILL.md，注明这些阶段需要 LLM 手工 write_file

### P1-4：iteration_aggregator.py 无 CLI

`iteration_aggregator.py` 没有 argparse CLI，调用方需要写 Python 代码。建议添加 argparse CLI：

```python
# 在 __main__ 中
# python -m ai_workflow.iteration_aggregator --feedback-dir workflow_assets/feedback_logs/ --output workflow_assets/游戏道具商城系统/「S8 自迭代」/v1.0/
```

### P1-5：S7 输出文件名不一致

`auto_reviewer.py` 输出 `review_snapshot.*`，但 SKILL.md 要求 `review_report.*`。建议：
- 将 `review_snapshot.*` 重命名为 `review_report.*`
- 或在输出目录同时生成两个文件（snapshot 供脚本用，report 供人工审阅）

---

## P2 级问题（小修小补）

### P2-1：s6_generate.py 无 CLI

仅 `if __name__ == "__main__": main()`，无 argparse。建议添加 argparse CLI。

### P2-2：SKILL.md aidocx-s5-test-points 引用的 `_build_fallback_scenarios` 不存在

SKILL.md 行 250：
```python
from ai_workflow.test_case_formatter import compose_test_points_from_structure, _build_fallback_scenarios
```
`_build_fallback_scenarios` 不存在（grep 搜索确认）。删除该引用即可。

### P2-3：SKILL.md aidocx-s5-test-points 引用的 `save_stage5_output` 不存在

SKILL.md 行 254-255：
```python
from ai_workflow.conversation_skills import save_stage5_output
save_stage5_output(version, breakdown, flowchart_text, raw_output, parsed, req_name)
```
删除该引用即可（S5 输出由 LLM 手工 write_file）。

### P2-4：SKILL.md aidocx-s4-flowchart 引用的 `s4_validator.py` 不存在

SKILL.md 行 301：
```python
from ai_workflow.s4_validator import validate_s4_output
```
文件不存在。删除该引用即可（S4 验证由 LLM 在 SKILL.md 引导下自检）。

### P2-5：SKILL.md aidocx-workflow 引用的文件不存在

`.cursor/skills/aidocx-workflow/SKILL.md` 文件不存在（Glob 搜索确认无此路径）。这是 git status 中的 untracked 文件引用了一个不存在的 SKILL.md。

---

## 脚本缺失 CLI 一览

| 脚本 | CLI | 状态 |
|------|-----|------|
| `s6_generate.py` | 无 argparse | P2-1 |
| `iteration_aggregator.py` | 无 argparse | P1-4 |
| `requirement_reviewer_auto.py` | `if __name__` demo | 可接受 |
| `test_case_formatter.py` | `--migrate-modules` | ✓ |
| `validate_skills.py` | 完整 argparse | ✓ |
| `feedback_logger.py` | 完整 argparse | ✓ |
| `upgrade_skills.py` | 完整 argparse | ✓ |
| `s6_xlsx_enhance.py` | `if __name__` | 可接受 |
| `auto_reviewer.py` | `if __name__` demo | 可接受 |
| `conversation_skills.py` | `if __name__` demo | 可接受 |

---

## SKILL.md 引用不存在 API 汇总

| SKILL.md | 引用内容 | 状态 |
|---------|---------|------|
| aidocx-s5-test-points | `_build_fallback_scenarios` | 不存在（删引用即可）|
| aidocx-s5-test-points | `save_stage5_output` | 不存在（删引用即可）|
| aidocx-s7-review | `overall_pass` | v2.0 已废弃（更新 SKILL.md）|
| aidocx-s7-review | `reviewer_b['s4_risk_coverage']` | 不存在（更新 SKILL.md）|
| aidocx-s7-review | `reviewer_b['uncovered_risks']` | 不存在（更新 SKILL.md）|
| aidocx-workflow-conversation | `make_stage6_skill()` | 不存在（删引用即可）|
| aidocx-workflow-conversation | `make_stage7_skill()` | 不存在（删引用即可）|
| aidocx-s8-self-iteration | `self_iteration.py` 文件 | 不存在（P0-2）|
| aidocx-s8-self-iteration | `analyze_and_iterate()` | 不存在（P0-2）|
| aidocx-s8-self-iteration | `archive_experience()` | 不存在（P0-2）|
| aidocx-s4-flowchart | `s4_validator.py` | 不存在（删引用即可）|
| aidocx-workflow | 整个 SKILL.md | 文件不存在 |
| aidocx-workflow-conversation | `_build_fallback_scenarios` | 不存在 |

---

## 总结

### 违反 LLM 推理原则的脚本：2 个

1. **`requirement_reviewer_auto.py`**（部分）：加权公式 + 阈值硬编码，但这是规则引擎而非 AI，且 SKILL.md 注释已标记不同步。
2. **无脚本做 PASS/FAIL 硬判决**：S7 auto_reviewer v2.0 正确不做判决，✓。

### 最严重的断裂点

1. **S5 → S6 → S7 数据流断裂**：`s4_reference` 字段从 S5 丢失到 S6，导致 S7 无法做 S4 风险点覆盖率审查——这是整个流水线（S4→S5→S6→S7）的核心价值链。
2. **S7 → S8 数据流断裂**：`review_snapshot.*` 与 `review_report.*` 文件名不一致 + 字段不对齐 + `self_iteration.py` 不存在。
3. **SKILL.md 大量引用不存在的 API**：13 个断裂引用中，6 个需要修复代码，7 个只需更新 SKILL.md。

### 建议修复优先级

1. **立即修复 P0**：S5→S6 字段传递（s6_generate.py）、S7 输出文件名（auto_reviewer.py）、self_iteration.py 创建
2. **次优先 P1**：删除重复脚本（s6_xlsx_enhance.py）、补充 CLI、conversation_skills.py 补桩
3. **收尾 P2**：清理 SKILL.md 中的不存在引用
