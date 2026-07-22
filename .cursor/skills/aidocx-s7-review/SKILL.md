---
name: aidocx-s7-review
description: >
  AIDocxWorkFlow Stage 7 — 用例审查。双审查员审计 S6 产出的测试用例（结构完整性 + 覆盖率）。
  覆盖率 = 风险被覆盖的程度。脚本只输出事实数字，LLM 按业务实际写建议（不设硬阈值）。
  不再做 PASS/FAIL 硬判决——审查建议（必修/应改/可改）由 LLM 在 review_report.md 中按业务实际填写。
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

**独立阶段**：可单独调用。上游材料（S6 test_cases.json + coverage/omission 账本）审查合格后开始，失败写失败报告。

> ⚠️ **模块定义见 [`.cursor/MODULES.md`](../../../MODULES.md)（项目级唯一真相源）。**
> 本文件不重写模块表。所有"模块"字段取值集合见 `MODULES.md` §1 总表，**`{Module}` 占位符** 实际取值集合 = 8 模块之一（CONFIG / UI / BIZ / UTIL / LINK / LOG / SPECIAL / HINT）。
>
> HINT vs UI 边界判定（误标高发区）见 [`MODULES.md` §4.11.2](../../../MODULES.md)。

---

## 阶段入口

**触发**：`/aidocx-s7-review` 或粘贴 S6 test_cases.json

**前置材料**：S6 test_cases.json + S5 test_points.json + S4 business_flow.md + coverage_ledger.json + omission_ledger.json。详见 §1.4。

**材料缺失时**：生成失败报告，停止 S7。

---

## §1.4 必读材料与违规认定

> ⚠️ **违反本节禁令 → 产出不合格，必须补读后重新生成。**

### 违规认定（满足任一 → 产出不合格）

- ❌ 未读取本节材料，直接凭印象生成
- ❌ 跳过标注"强制"的材料，用其他来源替代
- ❌ 产出的 module / s4_reference 与材料内容明显不符
- ❌ 用"业务常识"替代必须读取的材料

### 必读材料清单

**审查前，必须先 Read 以下材料。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| ① | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| 覆盖率按模块统计；审查员 B 的 module_coverage 以 8 模块为分母 |
| ② | 模块边界区分 | `.cursor/MODULES.md`（§4 各模块 O_boundary.md）| 判断 TP 模块归属是否正确；HINT vs UI 是最高误标区 |
| ③ | S6 test_cases（强制） | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/test_cases.json` | 审查对象；未读取 → 无法审查 |
| ④ | S5 test_points（强制） | `workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json` | S4 风险点覆盖率对比基准 |
| ⑤ | S4 business_flow（强制） | `workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md` | S7 覆盖率指标 = S4 风险点全量覆盖（100%）是硬约束 |

---

## §1.6 强制写文件（不可跳过，禁止询问）

> **S7 审查的产出是文件，不是对话窗口内的文字。**

**执行顺序（强制）**：

```
步骤 1：调用 auto_reviewer.snapshot() 获取事实数字（不可跳过）
  ↓
步骤 2：LLM 读取 snap 输出，做语义审查
  ↓
步骤 3：调用 save_review_report() 写入文件（强制，不可跳过）
```

### 步骤 1：调用 auto_reviewer（必须先执行）

```python
from ai_workflow.auto_reviewer import snapshot, save_review_report
from pathlib import Path

req_dir = Path("workflow_assets/<req_name>")
snap = snapshot(
    test_cases_path=req_dir / "<version>/「S6 测试用例生成」/test_cases.json",
    backlog_path=req_dir / "<version>/「S2 需求拆解」/backlog.json",
    test_points_path=req_dir / "<version>/「S5 测试点生成」/test_points.json",
)

# 输出事实数字供 LLM 使用（禁止跳过此步骤）
print(snap.ai_input_summary)
print(f"[S7] TC 填写率: {snap.structure.fill_rate:.1%}")
print(f"[S7] S5 TP 填写率: {snap.s5_structure.fill_rate:.1%}" if snap.s5_structure else "")
```

### 步骤 2：LLM 读取 snap 输出（事实数字）

- **禁止**在未读取 `snap.structure.fill_rate` 的情况下直接写报告
- **禁止**在未读取 `snap.s5_structure` 的情况下写 S5 覆盖率数据
- **禁止**使用 `overall_pass` 字段
- **禁止**将脚本统计数字当作 PASS/FAIL 硬判决

### 步骤 3：写入文件（强制，禁止询问）

**必须调用** `save_review_report()`，将审查报告写入：

| 文件 | 路径 |
|------|------|
| `review_report.json` | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/review_report.json` |
| `review_report.md` | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/review_report.md` |

**禁止的行为**：

- ❌ 在对话窗口输出审查结论后询问"是否要落文件"
- ❌ 只在对话中输出结果，不调用 `save_review_report()`
- ❌ 将对话窗口内的文字当作最终产出

```python
# 必须执行（禁止跳过）
# LLM 审查结束后，将审查结论传入 save_review_report
llm_review_a_semantic = {
    "field_name_violations": [],
    "module_misjudgment": [],
    "step_quality_issues": [],
    "s4_node_reference_violations": [],
}
llm_review_b_semantic = {
    "uncovered_risks_judgment": "（LLM 填写风险判定）",
    "uncovered_leaves_judgment": "（LLM 填写异常树判定）",
    "is_assumed_judgment": "（LLM 填写假设标注判定）",
}
result = save_review_report(
    snap=snap,
    output_dir=req_dir / "<version>/「S6 测试用例生成」",
    req_name="<req_name>",
    version="<version>",
    llm_review_a_semantic=llm_review_a_semantic,
    llm_review_b_semantic=llm_review_b_semantic,
)
print(f"[S7] 报告已写入: {result['report_json']}")
print(f"[S7] 报告已写入: {result['report_md']}")
```

**S7 阶段的核心原则**：对话窗口是工作过程，**文件才是真实产出**。

### review_report.json 顶层字段结构（5 个必填字段）

| 字段 | 来源 |
|------|------|
| `reviewer_a` | 来自 `snap.structure`（事实统计） |
| `reviewer_b` | 来自 `snap.s5_structure`（覆盖率事实） |
| `llm_review_a_semantic` | LLM 填写（语义审查结论） |
| `llm_review_b_semantic` | LLM 填写（覆盖率语义评判） |
| `recommendations` | LLM 填写（must_fix / should_fix / could_fix） |

> **旧格式 `overall_pass: true/false` 禁止出现**——已废除。S7 不再输出 PASS/FAIL 硬判决。
>
> **状态写回职责边界**：S7 审查报告只输出 `recommendations`，**不得修改 `test_cases.json` 的 `用例状态`**；状态写回由 `ai_workflow/s7_status_writer.py` 在 review_report 落盘后调用，依据 `recommendations.must_fix[].severity == MUST` 把 `Ready` 转为 `Rejected`；`Draft` / `Deprecated` 不变；禁止读取已废除的 `overall` / `overall_pass` 字段。
>
> **v31 新增 — Rejected 用例被拒原因记录**：`s7_status_writer.py` 在写入 `Rejected` 状态时，同时将原因写入「备注」字段（格式：`[S7 Reject] M-NNN: <description>`，取 `must_fix` 第一条的 `id` + `description`），便于人工审查时直接判断被打回的原因，无需另查报告。

**`recommendations` 字段结构（dict 形式）**：

```json
{
  "must_fix":    [ { "id": "M-NNN", "severity": "MUST",   "description": "...", "rca": {...} } ],
  "should_fix":  [ { "id": "S-NNN", "severity": "SHOULD", "description": "...", "rca": {...} } ],
  "could_fix":   [ { "id": "C-NNN", "severity": "COULD",  "description": "...", "rca": {...} } ]
}
```

| 字段 | 级别 | 说明 |
|------|------|------|
| `id` | **MUST** | 建议序号 `M-NNN` / `S-NNN` / `C-NNN`（按严重度前缀区分；与 `ai_workflow/validators/l1_s7.py` L24 `RCA_ID_PAT = ^(M\|S\|C)-\d{3,}$` 一致） |
| `severity` | **MUST** | `MUST` / `SHOULD` / `COULD` |
| `description` | **MUST** | 具体问题描述 |
| `affected_cases` | SHOULD | 涉及的 case_id 列表 |
| `affected_test_points` | SHOULD | 涉及的 test_point_id 列表 |
| `rca` | **SHOULD** | 三级根因定位对象 |
| `rca.stage` | MUST（rca 存在时） | 一级：`S4` / `S5` / `S6` / `S2` / `S1` |
| `rca.type` | MUST（rca 存在时） | 二级：`OMISSION` / `BOUNDARY_ERR` / `QUALITY_LOW` / `FIELD_MISSING` / `LINKAGE_BROKEN` / `RULE_VIOLATION` / `ID_NONCOMPLIANT` |
| `rca.clause` | MUST（rca 存在时） | 三级：条款代码，从 RCA 映射表选取 |
| `rca.explanation` | SHOULD | 根因简述（≤ 50 字） |

> **条款代码来源**：`governance/design_iter/current/rca_three_level_classification.md` §1.3。条款代码必须来自映射表，禁止自创。缺陷无法定位时 `rca.stage = "UNKNOWN"` 并说明原因。

## §1.5 决策 push 块

### 审查员 A：结构完整性（脚本做轻量体检，LLM 做语义审查）

| 检查项 | 谁做 | 说明 |
|--------|------|------|
| ID 规范化 | 脚本 | 格式 `{Module}-TC-{NNN}`（按 8 模块英文全名前缀）|
| 字段是否填写 | 脚本 | precondition / steps / expected_result 是否非空 |
| 模块归一化 | 脚本 | module 字段是否归一为 8 模块全名 |
| 字段名合规 | LLM | 字段名是否在 aidocx-s5-test-points/SKILL.md §1.6.5 强约束清单中 |
| 跨模块边界 | LLM | TP module 字段是否与 O_boundary.md 一致 |
| 步骤质量 | LLM | 原子性、无歧义、有具体数值；**禁止通用模板** |
| 预期可验证性 | LLM | 每步有明确 pass/fail 条件 |
| 误标案例对照 | LLM | TP 是否与 aidocx-s5-test-points/SKILL.md §1.6.4 反例库冲突 |
| 业务语言 | LLM | 文案是否符合业务术语，无 S4 节点名引用 |

### 审查员 B：覆盖率（脚本只统计数字，LLM 评判质量）

> **核心原则**：覆盖率 = 风险被覆盖的程度。**脚本只输出事实数字，LLM 评判"质量是否够"**——真实业务有取舍，不强制 100%。

| 指标 | 脚本产出 | LLM 审查 |
|------|----------|----------|
| S4 风险点引用 | "被 TP 引用 R-NNN 数量 / S4 风险点总数" | 评判：未覆盖的风险点是否真的不需要覆盖？ |
| S4 异常树叶子引用 | "被 TP 引用异常树叶子 / 异常树叶子总数" | 评判：未覆盖的叶子是否真的可忽略？ |
| density-OBJ（v33 新增）| "4类型齐全 OBJ 数 / OBJ 总数" | 评判：缺 NEGATIVE/BOUNDARY/EXCEPTION 的 OBJ 是否可接受？ |
| R-ID 引用（v33 新增）| "BIZ TP 引用 R-ID 数 / BIZ TP 总数" | 评判：BIZ TP 未引用 R-ID 是否可接受？ |
| is_assumed 字段填充率 | "TP 含 is_assumed 的比例" | 评判：LLM 自由推理是否标注充分？ |
| s4_reference 字段填充率 | "TP 含 s4_reference 的比例" | 评判：链路追溯是否完整？ |
| applies_rule 字段填充率 | "TP 含 applies_rule 的比例" | 评判：判定过程是否可审计？ |

**LLM 在 S7 的工作流**：
1. 读脚本输出的 `review_snapshot.ai_input_summary`（事实数字 + 缺失列表）
2. 按上述 5 个指标做**语义审查**（不是按"100% 即 PASS"判决）
3. 在 review_report.md 的 "## 5. LLM 审查建议" 段写出**实际业务问题**
4. 给出 3 类建议：**必修**（会引发线上 bug）/ **应改**（会引发测试盲区）/ **可改**（让用例更完善，优先级低）

---

## 质量门禁

> **S7 阶段不设硬指标**（不强制"覆盖率=100% = PASS"）——真实业务有取舍，**让 LLM 审查员按业务实际写建议**。

**S7 报告结构**（脚本生成 + LLM 填写）：

| 段 | 来源 | 内容 |
|---|---|---|
| 1. 事实统计 | 脚本 | 用例数 / 填写率 / 模块分布 / 类型分布 |
| 2. Epic 覆盖事实 | 脚本 | 哪些 Epic/Story 有 TC、哪些没有 |
| 3. 缺失字段用例 | 脚本 | 哪些 case 缺字段（LLM 决定是否补）|
| 4. AI 审核输入 | 脚本 | 给 LLM 看的事实摘要 |
| 5. LLM 审查建议 | **LLM** | 业务正确性 / 步骤可执行 / 预期可验证 / 风险覆盖 / 业务语言 |

> **旧规则已废弃**：旧 "S4 风险点覆盖率=100% + 结构完整性≥90% = PASS / 否则 FAIL" 判决由脚本做的硬指标。**全部改由 LLM 按业务实际写建议**。

---

### 例外率监控

> **来源**：外部方案 §4.5.2 + SSOT §2.4.2

S7 审查员在输出报告时，**必须读取该项目所有阶段的 `bypass_log.json`**，并输出例外率统计：

| 预警等级 | 阈值 | S7 动作 |
|----------|------|----------|
| 🟡 黄色 | 例外率 > 20%（> 2 项门禁走例外） | 在 review_report.md "## 5. LLM 审查建议" 段输出"人工关注建议" |
| 🔴 红色 | 例外率 > 40%（> 4 项门禁走例外） | 在 review_report.md "## 5. LLM 审查建议" 段输出"建议暂停，重新评估需求质量" |

**统计维度**（写入 review_report.json）：

- 单项目维度：`exception_rate` = bypass_count / total_gates
- 阶段维度：各阶段门禁被 bypass 的次数分布
- 时间维度：跨版本例外率趋势（需读取历史版本 bypass_log）

**bypass_log 读取位置**：`workflow_assets/<req_name>/<version>/「S{n} 阶段」/<version>/bypass_log.json`

---

## 人工审核反馈写入位置

> **适用范围**：AI 审查结束后，QA 人工阅读用例时记录的意见。
> **写入原则**：反馈写在用例旁边，不用跳到别的文件找。反馈随用例版本走，便于对比历史。

### 格式一：test_cases.json（推荐，结构化记录）

在每个用例对象中新增 `review_notes` 字段：

```json
{
  "case_id": "UI-TC-001",
  "模块": "界面",
  "用例描述": "购买确认流程",
  "功能描述": "购买确认弹窗正常展示道具信息",
  "前置条件": "玩家已登录，余额充足，道具可购买",
  "操作步骤": "1. 玩家已登录，进入道具详情页\n2. 点击【购买】按钮\n3. 系统展示购买确认弹窗",
  "预期结果": "1. 弹窗展示道具名称\n2. 弹窗展示购买数量\n3. 弹窗展示总价",
  "优先级": "P0",
  "用例状态": "Draft",
  "备注": "",
  "review_notes": [
    {
      "timestamp": "2026-06-21",
      "reviewer": "QA-张三",
      "type": "修改建议",
      "content": "前置条件中「余额充足」应改为具体数值，如「余额=2000游戏币」"
    }
  ]
}
```

字段说明：
- `review_notes`：数组，支持多人多次反馈，按时间倒序
- `timestamp`：ISO 日期（反馈时间）
- `reviewer`：审核人姓名
- `type`：`修改建议` / `通过` / `疑问` / `缺陷记录`
- `content`：具体意见

### 格式二：test_cases.md（快速标注，human-friendly）

在对应用例标题下方加一行标注：

```markdown
### UI-TC-001 | 购买确认流程 {#ui-tc-001}
> [QA-张三 2026-06-21] 前置条件中「余额充足」应改为具体数值，如「余额=2000游戏币」
```

> 标注行格式：`> [审核人 日期] 意见内容`

### 格式三：test_cases.xlsx（QA 团队协作）

在 Excel 中增加一列 `审核意见`（第 11 列）：

| 列 | 内容 |
|----|------|
| 1-10 | 原有 10 列 |
| **11（新增）** | `审核意见` — 文字描述或 `通过/修改建议/疑问` 标签 |

### 禁止的行为

- ❌ 反馈写在 `feedback_logs/` 或 `review_report.md`——反馈应随用例走，不应与用例分离
- ❌ 用 `.jsonl` 格式记录 QA 反馈——日志格式不是给人工填写的

---

## 成功产出

路径：`workflow_assets/<req_name>/<version>/「S6 测试用例生成」/review_report.md`
路径：`workflow_assets/<req_name>/<version>/「S6 测试用例生成」/review_report.json`

报告内容：审查员A结果 → 审查员B结果（S4覆盖率）→ 语义建议与账本结论

---

## 失败报告

路径：`workflow_assets/<req_name>/<version>/「S6 测试用例生成」/fail_report_S7.md`

---

## 自动化支持

```python
from ai_workflow.auto_reviewer import auto_review
review_result = auto_review(test_cases, test_points, s4_risks)
# review_result['reviewer_b']['s4_risk_coverage'] ∈ [0.0, 1.0]
# review_result['reviewer_b']['uncovered_risks']  # 未覆盖的风险点列表
```

---

## §5 一致性检查（SKILL ↔ Rule 自动对齐）

> **触发时机**：本节读取后、正式执行前。**仅执行一次**（同一次对话中多次触发本阶段，不重复检查）。

**检查类型**：A = 必读材料对齐 / B = 输出路径对齐 / C = 字段名对齐 / D = 模块枚举对齐

```python
from ai_workflow.consistency_check import run_consistency_check

result = run_consistency_check(stage="s7")
if not result["passed"]:
    print(f"[一致性检查] 发现 {len(result['issues'])} 个问题（见日志）")
```

检查结果不阻断阶段执行，仅输出到日志供人工参考。

---

## §1.6 决策 push 块

> **S7 阶段的关键使命**：不仅审"结构完整性 + 覆盖率"，还要审"字段名合规 + 跨模块边界"——这才是 S8 误判分析的源头。

### §1.6.1 审查员 A：字段名合规 + 跨模块边界

S7 审查员 A 新增 3 个检查项（这些在旧版审查中漏过）：

| 检查项 | 内容 |
|--------|------|
| 字段名合规 | S5 TP / S6 TC 的字段名是否在强约束清单中（防止 `test_point_subclass` typo 漏过） |
| 跨模块边界 | S5 TP 的 `module` 字段是否与 S4 异常树叶子归属一致 |
| 误标案例对照 | S5 TP 是否与反例库冲突 |

**审查员 A 报告输出字段**：`field_name_violations` / `module_misjudgment` / `misjudgment_pattern_violations`

### §1.6.2 审查员 B：覆盖率精确化（v33 修订）

在风险点覆盖率 + 异常树覆盖率基础上，新增 5 个指标：

| 指标 | 说明 |
|------|------|
| `is_assumed_field_compliance` | TP `is_assumed` 字段填充率（LLM 自由推理是否标注） |
| `s4_reference_completeness` | TP `s4_reference` 字段填充率（链路追溯完整性） |
| `applies_rule_completeness` | TP `applies_rule` 字段填充率（判定过程可审计） |
| `density_obj_coverage`（v33 新增）| per-OBJ 4类型齐全率：每个 OBJ 至少覆盖 POSITIVE + BOUNDARY + NEGATIVE + EXCEPTION，缺一必须有 `skip_reason` |
| `s4_risk_id_coverage`（v33 新增）| S4 R-ID 风险点引用率：BIZ TP 必须引用 `R-XXX`（来自 `business_flow.json` 的 `risks[].risk_id_machine`）|

### §1.6.3 误判根因反查

S7 报告输出根因定位字段（供 S8 直接使用）：

| 字段 | 说明 |
|------|------|
| `misjudgment_root_cause` | 误判来源阶段（`S2_OBJ` / `S4_EPIC` / `S5_TP` / `S6_TC`） |
| `s2_obj_violations` | S2 拆 OBJ 时违反跨模块拆分的 OBJ 列表 |
| `s4_epic_violations` | S4 Epic 命名/归属错误的 epic 列表 |

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S7_REVIEW.mdc`
- Prompt 模板：`ai_workflow/prompts/test_case_review.md`
- 自动审查引擎：`ai_workflow/auto_reviewer.py`
- 阈值配置：`ai_workflow/config.py`

---

## 执行卡（v14 单阶段执行卡 — 4 区块合一）

<aside data-exec-card-block="input_gate" data-src=".cursor/rules/STAGE_S7_REVIEW.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

> ⚠️ **派生产物，禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成
> src: `.cursor/rules/STAGE_S7_REVIEW.mdc` | synced_at: `2026-07-14`
> 修改请改源文件，然后跑 `python3 scripts/sync_execution_cards.py --stage s7-review` 重新同步。

### 输入门禁（input_gate）

| 必备材料 | 路径 | 缺失处理 |
|---|---|---|
| S6 test_cases.json | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/test_cases.json` | 用例数量 > 0，否则 fail_report |
| S5 test_points.json | `workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json` | 用于覆盖率计算 |
| S4 business_flow.md | `workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md` | S4 风险点覆盖率基准 |
| coverage_ledger.json | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/` | 覆盖缺口事实源 |
| omission_ledger.json | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/` | 豁免/人工复核事实源 |

**触发命令**：`/aidocx-s7-review` 或粘贴 S6 test_cases.json

</aside>

<aside data-exec-card-block="field_required" data-src=".cursor/rules/STAGE_S7_REVIEW.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### 必填字段（field_required）

| 字段 | 级别 | 校验 |
|---|---|---|
| reviewer_a 结构完整性 | **MUST** | ID规范化 / 字段填写率 / 模块归一化数字统计 |
| reviewer_b 覆盖率 | **MUST** | module_coverage / obj_coverage / fp_coverage / s4_risk_coverage 数字 |
| recommendations | **MUST** | MUST_FIX / SHOULD_FIX / COULD_FIX 分级建议 |

</aside>

<aside data-exec-card-block="quality_gate" data-src=".cursor/rules/STAGE_S7_REVIEW.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### 质量门禁（quality_gate）

| 门禁 | 阈值 | 说明 |
|---|---|---|
| 覆盖率门禁 | **无硬阈值**（已废除） | 脚本输出数字，LLM 按业务实际判断 |
| S4 风险点覆盖率 | 数字必须 ≥ 0（数字真实） | 真实业务有取舍，LLM 按业务评估 |
| coverage/omission 账本 | 必须消费 | 脚本只输出数字，建议由 LLM 语义审查 |
| **SSOT**：`DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.3（S7 硬阈值已废除）

</aside>

<aside data-exec-card-block="naming" data-src=".cursor/rules/STAGE_S7_REVIEW.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### ID 命名规范（naming）

| 产物 | 格式 |
|---|---|
| 审查报告 | `review_report.md` / `review_report.json` |
| 快照 | `review_snapshot.md` / `review_snapshot.json` |
| 输出目录 | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/` |

</aside>

---

## §S7 例外率聚合（v14 §5 第二阶段第三项）

> **派生产物**：本节基于外部方案 §4.5.2 + SSOT §4.3，于 2026-07-16 落地。
> **职责**：扫描所有阶段的 bypass_log.json，聚合例外率 + 按 20%/40% 双阈值输出预警等级。

### 调用方式

```bash
python3 scripts/bypass_log_aggregator.py <req_name> <version> [--json] [--output result.json]
python3 scripts/bypass_log_aggregator.py --self-test
```

### 退出码语义

| 退出码 | 预警等级 | 含义 | S7 动作 |
|--------|---------|------|---------|
| `0` | 🟢 GREEN | 例外率 ≤ 20% | 无需动作 |
| `1` | 🟡 YELLOW | 20% < 例外率 ≤ 40% | review_report.md "## 5. LLM 审查建议" 段输出「人工关注建议」 |
| `2` | 🔴 RED | 例外率 > 40% | review_report.md "## 5. LLM 审查建议" 段输出「建议暂停，重新评估需求质量」 |
| `3` | ⚪ 无 bypass_log | 项目无任何 bypass | 不报错（健康） |

### 3 统计维度（写入 review_report.json）

1. **单项目维度**：`exception_rate = bypass_count / total_gates`
2. **阶段维度**：各阶段门禁被 bypass 的次数分布（by_stage）
3. **时间维度**：跨版本例外率趋势（需读取历史版本 bypass_log）

### bypass_log 路径 SSOT

```
workflow_assets/<req_name>/<version>/「S{n} 阶段」/<version>/bypass_log.json
```

### 与 S7 审查员的协作

- ✅ 本脚本只**机械聚合 + 算预警等级**
- ❌ 不判断"为什么 bypass"——三步自问答案在 bypass_log.json 里
- ✅ S7 审查员消费聚合结果写入 review_report.json `exception_summary` 字段

### 自我测试

`python3 scripts/bypass_log_aggregator.py --self-test` — 4 cases 全覆盖（无 log / GREEN / YELLOW / RED）。

### SSOT 示例

`workflow_assets/_example/bypass_log_example.json`（v14 格式完整示例）

---

## §S7 缺陷模式输出（v15 §5 阶段 1 主轴）

> **派生产物**：本节基于 v15 PLAN.md §附录 C，于 2026-07-16 落地。
> **职责**：消费 S7 RCA 三级（stage × type × clause）+ bypass_log，按 `module × type × clause` 三维聚类，输出缺陷模式统计。

### 调用方式

```bash
# 基础：单项目（最近 1 个版本）
python3 ai_workflow/defect_cluster.py <req_name>

# 跨版本：最近 N 个版本
python3 ai_workflow/defect_cluster.py <req_name> --window 5

# 自测
python3 ai_workflow/defect_cluster.py --self-test
```

### 数据源 SSOT

| 数据源 | 路径 | 字段 |
|---|---|---|
| S7 RCA | `workflow_assets/<req>/<v>/「S7 用例审查」/review_report.json` | `recommendations[].rca.{stage,type,clause}` |
| bypass_log | `workflow_assets/<req>/<v>/「S{n} 阶段」/<v>/bypass_log.json` | `bypassed_gates[].{gate_name,priority,bypassed}` |

### 聚类维度（v15 §附录 C 拍板）

```
cluster_key = module × rca.type × rca.clause
```

### 输出物

| 文件 | 触发条件 | 路径 |
|---|---|---|
| `defect_mode_latest.json` | 任何数据都生成 | `workflow_assets/<req>/defect_mode_latest.json` |
| `defect_mode_trend.json` | **需 ≥ 3 个 bypass_log** | `workflow_assets/<req>/defect_mode_trend.json` |

### S7 审查员的协作（不重复造轮子）

- ✅ 本脚本**机械聚类**——不做"为什么聚类""如何修"
- ✅ S7 审查员消费 `defect_mode_latest.json` 写入 review_report.json 的 `cluster_summary` 字段
- ❌ 不判断优先级合理性（v14 §4.5.1 已 P0/P1/P2，本脚本不重复）

### 与 S8 自迭代的桥接

| 维度 | v15 阶段 1（本脚本）| v15 阶段 3（v16 规划）|
|---|---|---|
| 数据 | S7 RCA + bypass_log 聚类 | + S8 iteration_items |
| 输出 | 缺陷模式清单 | 缺陷模式趋势看板 |
| 时间维度 | 单项目/最近 N 版本 | 跨项目跨时间 |

### 自我测试

`python3 ai_workflow/defect_cluster.py --self-test` — 5 cases 全覆盖（空数据 / RCA only / bypass only / 合并 / 趋势判断）。

---

## §S7 双轨覆盖率报告（v16 T5 新增）

> **SSOT**：`ai_workflow/coverage_dual_track.py`
> **触发时机**：审查员 B 覆盖率审查完成后，生成 review_report 前。

### 调用方式

```python
from ai_workflow.coverage_dual_track import run_dual_track

result = run_dual_track(
    tp_path="workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json",
    obj_path="workflow_assets/<req_name>/<version>/「S2 需求拆解」/requirement_objects.json",
    verbose=False
)

# result 结构
{
    "module_coverage": {"BIZ": {"tp_count": 12, "obj_count": 8, "coverage": 0.92}, ...},
    "dimension_coverage": {"BIZ": {"tp_count": 18, "obj_count": 8, "coverage": 0.95}, ...},
    "warnings": [{"type": "WEAK_OVERLAP", "module": "BIZ", "module_cov": 0.70, "dim_cov": 0.92, "diff": 0.22}],
    "summary": {"total_tp": 128, "total_obj": 64, "warn_count": 1}
}
```

### 双轨定义

| 轨道 | 统计口径 | 用途 |
|------|---------|------|
| **module_coverage** | 按 `TP.module` 字段分组（主模块轨道） | 主模块覆盖率 |
| **dimension_coverage** | 按 `TP.related_tags` 展开分组（维度轨道） | 维度覆盖率（跨模块关联）|

### 报告写入规范

审查员 B 在 `review_report.json` 中新增以下字段：

```json
{
  "dual_track_coverage": {
    "module_coverage": { ... },
    "dimension_coverage": { ... },
    "warnings": [
      {
        "type": "WEAK_OVERLAP",
        "module": "BIZ",
        "module_cov": 0.70,
        "dim_cov": 0.92,
        "diff": 0.22,
        "threshold": 0.10,
        "message": "WEAK_OVERLAP: module=BIZ module_coverage=0.70, dimension_coverage=0.92, diff=0.22 > 0.10"
      }
    ],
    "summary": {
      "total_tp": 128,
      "total_obj": 64,
      "warn_count": 1
    }
  }
}
```

### WEAK_OVERLAP 警告处理

| diff 阈值 | 级别 | LLM 审查建议 |
|-----------|------|------------|
| diff ≤ 0.10 | 正常 | 无需动作 |
| diff > 0.10 | ⚠️ 警告 | 在 recommendations 中注明该模块存在覆盖率差异，说明原因 |

### 兼容性

- 无 `related_tags` 字段的旧 TP：`dimension_coverage` 中该模块 tp_count = 0（不报错）
- 无 `requirement_objects.json`：`obj_count = 0`，coverage = null（不阻断）
