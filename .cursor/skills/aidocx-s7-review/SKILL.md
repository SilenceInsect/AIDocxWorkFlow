---
name: aidocx-s7-review
description: >
  AIDocxWorkFlow Stage 7 — 用例审查。双审查员审计 S6 产出的测试用例（结构完整性 + 覆盖率）。
  覆盖率 = 风险被覆盖的程度。脚本只输出事实数字，LLM 按业务实际写建议（不设硬阈值）。
  v2.0 不再做 PASS/FAIL 硬判决——审查建议（必修/应改/可改）由 LLM 在 review_report.md 中按业务实际填写。
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

**独立阶段**：可单独调用。上游材料（S6 test_cases.json）审查合格后开始，失败写失败报告。

> ⚠️ **模块定义见 [`.cursor/MODULES.md`](../../MODULES.md)（项目级唯一真相源）。**
> 本文件不重写模块表。所有"模块"字段取值集合见 `MODULES.md` §1 总表，**`{Module}` 占位符** 实际取值集合 = 8 模块之一（CONFIG / UI / BIZ / AUX / LINK / LOG / SPECIAL / HINT）。
>
> HINT vs UI 边界判定（误标高发区）见 [`MODULES.md` §4.11.2](../../MODULES.md)。

---

## 阶段入口

**触发**：`/aidocx-s7-review` 或粘贴 S6 test_cases.json

**前置材料**：
- S6 test_cases.json：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/test_cases.json`
- S5 test_points.json（用于 S4 覆盖率）：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json`

**材料缺失时**：生成失败报告，停止 S7。

---

## §1.4 LLM 必读材料（阶段前置）

**审查前，必须先 Read 以下材料。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| 1 | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| 覆盖率按模块统计；审查员 B 的 module_coverage 以 8 模块为分母 |
| 2 | 模块边界区分 | `.cursor/MODULES.md`（§4 各模块 O_boundary.md）| 判断 TP 模块归属是否正确；HINT vs UI 是最高误标区 |
| 3 | S6 test_cases | `workflow_assets/<req_name>/「S6 测试用例生成」/<version>/test_cases.json` | 审查对象 |
| 4 | S5 test_points | `workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json` | S4 风险点覆盖率对比基准 |
| 5 | S4 business_flow | `workflow_assets/<req_name>/「S4 流程图导出」/<version>/business_flow.md` | S7 覆盖率指标 = S4 风险点全量覆盖（100%）是硬约束，不是拍脑袋 |

---

## 双审查员审计

### 审查员 A：结构完整性（脚本做轻量体检，LLM 做语义审查）

| 检查项 | 谁做 | 说明 |
|--------|------|------|
| ID 规范化 | 脚本 | 格式 `{Module}-TC-{NNN}`（按 8 模块英文全名前缀）|
| 字段是否填写 | 脚本 | precondition / steps / expected_result 是否非空 |
| 模块归一化 | 脚本 | module 字段是否归一为 8 模块全名 |
| 字段名合规 | LLM | 字段名是否在 §1.5.5 强约束清单中 |
| 跨模块边界 | LLM | TP module 字段是否与 O_boundary.md 一致 |
| 步骤质量 | LLM | 原子性、无歧义、有具体数值；**禁止通用模板** |
| 预期可验证性 | LLM | 每步有明确 pass/fail 条件 |
| 误标案例对照 | LLM | TP 是否与 §1.5.4 反例库冲突 |
| 业务语言 | LLM | 文案是否符合业务术语，无 S4 节点名引用 |

### 审查员 B：覆盖率（脚本只统计数字，LLM 评判质量）

> **核心原则**：覆盖率 = 风险被覆盖的程度。**脚本只输出事实数字，LLM 评判"质量是否够"**——真实业务有取舍，不强制 100%。

| 指标 | 脚本产出 | LLM 审查 |
|------|----------|----------|
| S4 风险点引用 | "被 TP 引用 R-NNN 数量 / S4 风险点总数" | 评判：未覆盖的风险点是否真的不需要覆盖？ |
| S4 异常树叶子引用 | "被 TP 引用异常树叶子 / 异常树叶子总数" | 评判：未覆盖的叶子是否真的可忽略？ |
| is_assumed 字段填充率 | "TP 含 is_assumed 的比例" | 评判：LLM 自由推理是否标注充分？ |
| s4_reference 字段填充率 | "TP 含 s4_reference 的比例" | 评判：链路追溯是否完整？ |
| applies_rule 字段填充率 | "TP 含 applies_rule 的比例" | 评判：判定过程是否可审计？ |

**LLM 在 S7 的工作流**：
1. 读脚本输出的 `review_snapshot.ai_input_summary`（事实数字 + 缺失列表）
2. 按上述 5 个指标做**语义审查**（不是按"100% 即 PASS"判决）
3. 在 review_report.md 的 "## 5. LLM 审查建议" 段写出**实际业务问题**
4. 给出 3 类建议：**必修**（会引发线上 bug）/ **应改**（会引发测试盲区）/ **可改**（让用例更完善，优先级低）

---

## 质量门禁（v2.0：无硬阈值）

> **S7 阶段不设硬指标**（不强制"覆盖率=100% = PASS"）——真实业务有取舍，**让 LLM 审查员按业务实际写建议**。

**S7 报告结构**（脚本生成 + LLM 填写）：

| 段 | 来源 | 内容 |
|---|---|---|
| 1. 事实统计 | 脚本 | 用例数 / 填写率 / 模块分布 / 类型分布 |
| 2. Epic 覆盖事实 | 脚本 | 哪些 Epic/Story 有 TC、哪些没有 |
| 3. 缺失字段用例 | 脚本 | 哪些 case 缺字段（LLM 决定是否补）|
| 4. AI 审核输入 | 脚本 | 给 LLM 看的事实摘要 |
| 5. LLM 审查建议 | **LLM** | 业务正确性 / 步骤可执行 / 预期可验证 / 风险覆盖 / 业务语言 |

> **v1.0 旧规则已废弃**：旧 "S4 风险点覆盖率=100% + 结构完整性≥90% = PASS / 否则 FAIL" 判决由脚本做的硬指标。**v2.0 全部改由 LLM 按业务实际写建议**。

---

## 成功产出

路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/review_report.md`
路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/review_report.json`

报告内容：审查员A结果 → 审查员B结果（S4覆盖率）→ 整体判决

---

## 失败报告

路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/fail_report_S7.md`

---

## 自动化支持

```python
from ai_workflow.auto_reviewer import auto_review
review_result = auto_review(test_cases, test_points, s4_risks)
# review_result['overall_pass'] ∈ {True, False}
# review_result['reviewer_b']['s4_risk_coverage'] ∈ [0.0, 1.0]
# review_result['reviewer_b']['uncovered_risks']  # 未覆盖的风险点列表
```

---

## §1.5 决策 push 块(无硬指标版本,见 [PUSH-V2-ITER-3] 标签)

> **S7 阶段的关键使命**: 不仅审"结构完整性 + 覆盖率",还要审"字段名合规 + 跨模块边界"——这才是 S8 误判分析的源头。

### §1.5.1 [PUSH-V2-ITER-3] S7 字段名合规审查(对应 PROMPT-PUSH-5)

> 旧审查员 A 只审"ID 规范化"——S2.1-TP-010 `test_point_subclass` typo 案例就漏了。

**S7 审查员 A 新增 3 个检查项**:
- 字段名合规: S5 TP / S6 TC 的字段名是否在 S5 §1.5.5 / S6 §1.5.1 强约束清单中
- 跨模块边界: S5 TP 的 `module` 字段是否与 S4 异常树叶子归属一致
- 误标案例对照: S5 TP 是否与 S2 §1.5.4 反例库冲突

**审查员 A 报告新增**:
- `field_name_violations`: 字段名拼错 TP/TC 列表
- `module_misjudgment`: 跨模块误判 TP 列表
- `misjudgment_pattern_violations`: 与反例冲突的 TP 列表

### §1.5.2 [PUSH-V2-ITER-3] S7 覆盖率精确化(对应 PROMPT-PUSH-2)

> 旧规则"S4 风险点覆盖率=100%"——但**漏了字段级反例反查**。

**S7 审查员 B 新增 3 个指标**:
- `is_assumed_field_compliance`: TP `is_assumed` 字段填充率(LLM 自由推理是否标注)
- `s4_reference_completeness`: TP `s4_reference` 字段填充率(链路追溯完整性)
- `applies_rule_completeness`: TP `applies_rule` 字段填充率(判定过程可审计)

**3 个新增指标输出** + 旧 100% 风险点覆盖率 + 100% 异常树覆盖率 = 完整审查报告。

### §1.5.3 [PUSH-V2-ITER-3] S7 误判根因反查(对应 PROMPT-PUSH-4)

> 旧审查员 B 只算"覆盖率"——但**不告诉 S8 哪个根因**。

**S7 报告新增字段**:
- `misjudgment_root_cause`: 误判来源阶段(`S2_OBJ` / `S4_EPIC` / `S5_TP` / `S6_TC`)
- `s2_obj_violations`: S2 拆 OBJ 时违反跨模块拆分的 OBJ 列表
- `s4_epic_violations`: S4 Epic 命名/归属错误的 epic 列表

**S8 拿到这个报告可直接定位根因,不用再回溯**。

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S7_REVIEW.mdc`
- Prompt 模板：`ai_workflow/prompts/test_case_review.md`
- 自动审查引擎：`ai_workflow/auto_reviewer.py`
- 阈值配置：`ai_workflow/config.py`
