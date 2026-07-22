# S7 审查链路字段审计（Q2 元指令落地前置）

## 扫描时间
2026-07-19

## 1. 扫描输入

| 输入 | 路径 | 状态 |
|---|---|---|
| SKILL.md | `.cursor/skills/aidocx-s7-review/SKILL.md`（654 行） | ✅ 已 Read 全文 |
| STAGE_S7_REVIEW.mdc | `.cursor/rules/STAGE_S7_REVIEW.mdc`（512 行） | ✅ 已 Read 全文 |
| auto_reviewer.py | `ai_workflow/auto_reviewer.py`（755 行） | ✅ 已 Read 全文 |
| l1_s7.py | `ai_workflow/validators/l1_s7.py`（119 行） | ✅ 已 Read 全文 |
| 最近 S7 review_report.json | **未找到**（项目 S7 阶段从未真实产出过 review_report.json） | ⚠️ 唯一 review_report.json 实为 S1 评审报告（游戏道具商城系统 v3.01） |

## 2. 字段矩阵（10 字段 · 实测填表）

| # | 字段路径 | SSOT 文档层（SKILL.md + .mdc） | 代码层（auto_reviewer.py + l1_s7.py） | 实际产物层 | 判定 |
|---|---|---|---|---|---|
| 1 | `overall_pass` | SKILL.md L160「禁止」+ .mdc L305-308「禁止」+ 执行卡 L455「禁止 PASS/FAIL」 | **不写**（auto_reviewer.py L584-621 完全不输出此字段） | 0/N | ✅ **已废除**——保留 SSOT「禁止」声明即可，无需操作 |
| 2 | `reviewer_a.overall_assessment` | SKILL.md L129「允许 LLM 填」+ .mdc 执行卡 L442-458「**MUST 字段**」+ .mdc L455「不能含 PASS/FAIL」 | **不写**（auto_reviewer.py L592-601 输出 reviewer_a 仅含 7 字段：id_normalization_rate / field_completion_rate / module_normalization_rate / field_name_violations / module_misjudgment / misjudgment_pattern_violations / step_quality_issues / s4_node_reference_violations——**无 overall_assessment**） | 0/N | ⚠️ **SSOT-代码不一致（噪音候选）**：.mdc 列 MUST 但代码不写；**Q2 元指令应清理对象** |
| 3 | `reviewer_b.overall_assessment` | .mdc 执行卡 L442-458「**MUST**」+ §1.6.1「**审查员 A**」限定（不涉及 B） | **不写**（auto_reviewer.py L602-612 输出 reviewer_b 9 字段，无 overall_assessment） | 0/N | ⚠️ **SSOT-代码不一致**——.mdc 列 MUST 但 SKILL.md §1.6.1 限定 reviewer_a；**Q2 元指令应清理对象** |
| 4 | `reviewer_a.summary` | **未找到引用**（SKILL.md / .mdc 全文 grep 0 命中） | **不写** | 0/N | ❌ **未找到引用**——字段不存在 |
| 5 | `recommendations`（顶层 dict vs array） | SKILL.md L162-177「**数组形式** `[]`」+ .mdc L339-343「**dict 形式** `{"must_fix":[],"should_fix":[],"could_fix":[]}`」 | **dict 形式**（auto_reviewer.py L615-619：dict not array） | 0/N | ⚠️ **SSOT 内部不一致**——SKILL.md L162 vs .mdc L339；**Q2 元指令应统一为 dict**（代码已用 dict，删除 SKILL.md 数组形式声明） |
| 6 | `recommendations.must_fix[].id` | SKILL.md L166「**MUST 字段 `REC-NNN`**」+ .mdc L437「`MUST_FIX/SHOULD_FIX/COULD_FIX` 分级建议」 | **写**（auto_reviewer.py L616：`"must_fix": uncovered[:10]`——uncovered 是 dict 列表，不是 REC-NNN 格式字符串！）+ **校验**（l1_s7.py L24：`RCA_ID_PAT = re.compile(r"^(M\|S\|C)-\d{3,}$")` 校验 M/S/C-NNN 格式） | 0/N | ⚠️ **SSOT 文档-代码不一致**：SKILL.md 写 `REC-NNN`，l1_s7 校验 `M/S/C-NNN`；**auto_reviewer.py 实际产出的是 dict 项而非字符串 id**——**实际写盘数据不符合 l1_s7 校验规则**（潜在阻断风险） |
| 7 | `recommendations.must_fix[].severity` | SKILL.md L167「MUST `MUST_FIX/SHOULD_FIX/COULD_FIX`」 | **不写**（auto_reviewer.py L616 直接放 uncovered list 项——无 severity 字段） | 0/N | ⚠️ **SSOT-代码不一致**：SKILL.md 列 MUST 但代码不写 |
| 8 | `recommendations.must_fix[].resolved` | **未找到引用**（SKILL.md / .mdc 全文 grep 0 命中） | **不写** | 0/N | ❌ **未找到引用**——字段不存在 |
| 9 | `coverage_gaps[]` | **未找到引用** | **不写**（最接近的是 reviewer_b.uncovered_risks） | 0/N | ❌ **未找到引用**——可能与 uncovered_risks 混淆 |
| 10 | `unresolved_critical_count` | **未找到引用** | **不写** | 0/N | ❌ **未找到引用**——字段不存在 |

## 3. 废弃残留清单（SSOT 有 + 代码无 / SSOT 内部不一致）

| 编号 | 字段 | SSOT 来源 | 代码层 | 严重度 |
|---|---|---|---|---|
| N-1 | `reviewer_a.overall_assessment` | SKILL.md L129 + .mdc 执行卡 L442 MUST | 不写（auto_reviewer.py L592-601） | MEDIUM |
| N-2 | `reviewer_b.overall_assessment` | .mdc 执行卡 L442 MUST（但 SKILL.md §1.6.1 不涉及 B） | 不写（auto_reviewer.py L602-612） | MEDIUM |
| N-3 | `recommendations` 数组形式 | SKILL.md L162-177「数组 `[]`」 | dict 形式（auto_reviewer.py L615-619） | HIGH（SSOT 内部不一致） |
| N-4 | `recommendations.must_fix[].id` 格式 `REC-NNN` | SKILL.md L166「`REC-NNN`」 | 校验 `M/S/C-NNN`（l1_s7.py L24） | HIGH（写盘数据不会通过校验） |
| N-5 | `recommendations.must_fix[].severity` MUST | SKILL.md L167「`MUST`」 | 不写（auto_reviewer.py L616 直接放 uncovered 项） | LOW |
| N-6 | `overall_pass` 字段 | SKILL.md L160 + .mdc L305-308「禁止」 | 已不输出（auto_reviewer.py L584-621） | LOW（仅保留禁止声明即可） |
| N-7 | `recommendations[].rca.{stage,type,clause}` MUST | SKILL.md L172-174 + .mdc L70-74 | 不写（auto_reviewer.py L616 uncovered 项不带 rca 子对象） | HIGH |

## 4. 暗字段清单（实际产物有 + SSOT 无）

| 编号 | 字段 | 来源 | 说明 |
|---|---|---|---|
| D-1 | `meta.{stage,req_name,version,generated_at,schema}` | auto_reviewer.py L585-591 | SSOT 仅在 .mdc L66-68 提"文件名"，不提 meta 内部字段 |
| D-2 | `snapshot`（顶层 dict） | auto_reviewer.py L620 | SSOT 完全未提及——SSOT 仅规定 5 必填顶层字段，snapshot 是第 6 段 |
| D-3 | `reviewer_a.id_normalization_rate` / `field_completion_rate` / `module_normalization_rate` | auto_reviewer.py L593-595 | SKILL.md §1.6.1 + .mdc L107-124 仅作为示例 JSON 展示，未列为 MUST 必填顶层字段 |
| D-4 | `reviewer_b.{s4_risk_reference_rate, s4_exception_leaf_reference_rate, is_assumed_compliance_rate, s4_reference_completeness_rate, applies_rule_completeness_rate, uncovered_risks, uncovered_leaves, s2_obj_violations, s4_epic_violations}` | auto_reviewer.py L603-611 | 同 D-3 |
| D-5 | `reviewer_b.uncovered_risks` 字段名为 `list[dict]`（uncovered 项）| auto_reviewer.py L580-583 + L608 | SSOT .mdc L332 仅说 `uncovered_risks: []`（未明确是 list[dict] 还是 list[str]） |

## 5. 给 Q2 元指令的建议清理对象

> **目标**：让 SSOT（SKILL.md + .mdc）与代码层（auto_reviewer.py + l1_s7.py）一致，**移除废弃噪音**，**解决 SSOT 内部矛盾**。

| 优先级 | 字段 | 操作 | 影响范围 | 依据 |
|---|---|---|---|---|
| 🔴 P0 | `recommendations[].rca.*` MUST（SKILL.md L172-174 + .mdc L70-74） | **代码补写**——auto_reviewer.py L616 写盘时给 uncovered 项附加 rca 子对象 | auto_reviewer.py + l1_s7.py | SSOT 三处 MUST 但代码 0 命中 → 现有产物无法通过 L1S7Validator 校验 |
| 🔴 P0 | `recommendations[].id` 格式 `REC-NNN` vs `M/S/C-NNN` | **统一为 `M/S/C-NNN`**——修改 SKILL.md L166 或修改 l1_s7.py L24 | SKILL.md 或 l1_s7.py | 格式不一致会导致现有产物被 L1S7Validator 拒绝 |
| 🟡 P1 | `recommendations` 数组 vs dict | **统一为 dict**——SKILL.md L162-177 改为 dict 形式声明 | SKILL.md L162-177 | 代码已用 dict 形式；SKILL.md 描述与实际产出不符 |
| 🟡 P1 | `reviewer_a.overall_assessment`（SKILL.md L129 + .mdc 执行卡 L442 MUST）| **删除 SSOT 引用**——SKILL.md L129 + .mdc 执行卡 MUST 列表删除此字段 | SKILL.md L129 + .mdc L437-458 | SSOT 列 MUST 但代码不写，属废弃残留 |
| 🟡 P1 | `reviewer_b.overall_assessment`（.mdc 执行卡 L442 MUST）| **删除 SSOT 引用**——.mdc 执行卡 MUST 列表删除此字段 | .mdc L437-458 | SKILL.md §1.6.1 限定 reviewer_a；.mdc 误列 B |
| 🟢 P2 | `recommendations.must_fix[].severity` MUST（SKILL.md L167）| **代码补写**——auto_reviewer.py 写盘时给每项加 severity 字段 | auto_reviewer.py | SSOT 列 MUST 但代码不写 |
| 🟢 P2 | `meta.{stage,req_name,version,generated_at,schema}` | **SKILL.md / .mdc 增补**——明确 meta 是标准顶层字段 | SKILL.md + .mdc | 代码已写但 SSOT 未提——建议补 SSOT 而非删代码（meta 是合理字段） |
| 🟢 P2 | `snapshot` 顶层 dict（auto_reviewer.py L620）| **SKILL.md / .mdc 增补**——明确 snapshot 是第 6 个顶层字段 | SKILL.md + .mdc | 同 D-2——代码合理字段，SSOT 应补 |
| 🟢 P2 | reviewer_a / reviewer_b 内 12 个细粒度 rate / violation 字段（D-3 + D-4）| **SKILL.md / .mdc 增补**——SSOT 列出全部 12 字段 | SKILL.md §1.6.1 + §1.6.2 + .mdc L107-167 | 同 D-3/D-4——代码已用，SSOT 示例不全 |
| 🟢 P2 | `unresolved_critical_count` / `coverage_gaps[]` / `recommendations.must_fix[].resolved` / `reviewer_a.summary` | **未找到引用**——任务用户假设存在但 SSOT 与代码皆无 | N/A | 字段不存在，无需清理 |

## 6. 核心发现（SSOT vs 代码 vs 产物 三层一致性评估）

### 6.1 SSOT 内部矛盾（最高优先级）

**SKILL.md 与 .mdc 自相矛盾**：
- `recommendations` 数组 vs dict（SKILL.md L162-177 数组 vs .mdc L339-343 dict）
- `recommendations[].id` 格式（SKILL.md L166 `REC-NNN` vs .mdc L70-74 `M/S/C-NNN` 经 l1_s7.py L24 强化）

**结论**：SSOT 内部 2 处矛盾——SKILL.md 是**过时版本**（v13 早期），.mdc + 代码 + l1_s7.py 是**现行版本**（v14+）。**Q2 元指令应优先删除 SKILL.md 中的过时声明**。

### 6.2 SSOT-代码不一致（中高优先级）

**5 个 SSOT 列 MUST 但代码不写**：
- `reviewer_a.overall_assessment`（N-1）
- `reviewer_b.overall_assessment`（N-2）
- `recommendations.must_fix[].severity`（N-5）
- `recommendations[].rca.*`（N-7）
- `recommendations[].id` 格式（SKILL.md `REC-NNN` vs 代码 `M/S/C-NNN`，N-4）

**结论**：SSOT 列出但代码 0 写入 = **SSOT 文档与实际产物不一致**——会误导后续 S7 审查员按 SSOT 期望填写但实际写入时被代码忽略。

### 6.3 实际产物缺失（最高风险）

**项目 S7 阶段从未真实产出过 review_report.json**：
- `find workflow_assets/ -name "review_report.json"` 仅命中 S1 评审报告（v3.01）
- `find workflow_assets/ -name "review_snapshot.json"` 0 命中
- `find workflow_assets/ -name "postflight_gate.json"` 命中 1 个 test_req S7 失败的 gate

**结论**：本审计基于 SKILL.md / .mdc / auto_reviewer.py 静态分析；**实测产物层缺失**——本扫描结果未经真实 S7 产出验证，**Q2 元指令落地时必须先在隔离需求版本（如 `resource/test_s6_status`）跑一次 S7 拿到真实 review_report.json 后再做精确矩阵填充**。

### 6.4 大规模不一致判定

**SSOT-代码不一致字段数** = **7 项**（N-1..N-7）—— 超过任务指令中"≥3 个文档说 vs 代码不一致"的阈值。

**结论**：⚠️ **满足"大规模不一致"条件**——这是潜在的更高级阻断。

## 7. 任务自检（DNA §9.4）

- ✅ Read SKILL.md L1-654
- ✅ Read STAGE_S7_REVIEW.mdc L1-512
- ✅ Read auto_reviewer.py L1-755（含 _build_review_report_payload L571-621 关键方法）
- ✅ Read l1_s7.py L1-119（含 RCA_ID_PAT L24 + validate_id_naming L92-115）
- ✅ Glob workflow_assets/ 找 review_report.json — 命中仅 S1
- ✅ Read 唯一 review_report.json（实为 S1）前 100 行——确认非 S7 产物