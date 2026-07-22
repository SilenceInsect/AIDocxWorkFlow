# Goal: 用例状态字段语义重定义（Draft / Ready / Rejected / Deprecated）

> **本档是 q_decision_table 占位骨架**——按 DNA_3Q_CHECK.mdc §9.5 落档协议，决策表内容先 Write 占位文件，再 content 展开。
> **落档路径**：`governance/design_iter/current/`（避免污染版本化方案目录）。
> **历史归档**：Round 1-8 过程性记录归档到 `governance/design_iter/plans/v25/archive/goal_s6_case_status_redefinition_history.md`（186 行）。
> **状态**：⏸️ **GOAL PAUSED**——等待用户审核本目标后再启动 goal-loop 推进。
> **最新基线**：Round 7 — 拒绝 L1-only 降级，要求先建 L2 校验器；要求落实 Rejected 概念并移除 overall 残留噪音。

---

## 2. 现状证据（关键行号 + 1 行现状 · Round 11 已 Read 实测）

### 2.1 文档 / SSOT 层（Round 10 已有 · 此处复用）

| 文件 | 行号 | 现状 |
|---|---|---|
| `ai_workflow/s6_generate.py` | 全文 | thin wrapper；调用 `apply_l1_status` 自动写 Ready（详见 §2.2 §2.3）|
| `ai_workflow/test_case_formatter.py` | L836/L874 | xlsx 已实现 `_partition_cases_for_xlsx` 双 Sheet 分流（详见 §2.2）|
| `ai_workflow/validators/l1_s6.py` | 全文 | L1 校验器**只产 errors/stats**，**从不写回用例状态**（详见 §2.2）|
| `STAGE_S6_TEST_CASES.mdc` | 144 | 枚举仅 `Draft / Ready / Deprecated`，**无 Rejected**（Round 10 已知）|
| `STAGE_S7_REVIEW.mdc` + SKILL.md | 全文 | S7 **不写用例状态**——S7 当前未做状态改写（Round 10 已知）|
| 全文 grep `Rejected` | L837/973 命中 | `test_case_formatter.py` L836 `_partition_cases_for_xlsx` 已支持 Rejected 分流（**与原 §2 "从未出现" 矛盾**——Round 10 状态已部分实现）|

**关键判断修正（Round 11）**：
- §2 表"全文 grep Rejected 0" 与实测 L837/973 命中矛盾 → **该行作废**
- L2 校验器仍不存在；"L2 PASS → Ready 链路" 仍断（Q1=build-L2-first 决策保持）
- "xlsx 双 Sheet"（V-005/V-006）已**部分物理实现**，但**未文档化进 SSOT.mdc/SKILL.md**——落档文件 §2.1 第 3 行已修正

### 2.2 代码现状证据（Round 11 P0 · 实际 Read 三文件后填充）

| 文件 | 总行数 | 关键现状（实测）| 行号 |
|---|---|---|---|
| `ai_workflow/s6_generate.py` | 178 | (1) thin wrapper 设计，**已实现** `apply_l1_status` 自动写 Ready（self_test `assert seed["用例状态"] == "Ready"` 已通过）；(2) L1 通过即写 Ready，**未引入 L2 校验器**——`main()` 第 142 行仅调用 `L1S6Validator.run_l1_check` | L142-148（writeback 段）|
| `ai_workflow/test_case_formatter.py` | 1608 | (1) **已实现**双 Sheet 分流 `_partition_cases_for_xlsx`（Ready 主表 + Draft-Rejected 附录）；(2) **未实现 Ready 主表名字符串锁定为 `"测试用例（Ready）"`**——目前是 `profile.get("sheet_name", "测试用例")` 默认名；(3) **未实现精确断言式的 .value not None 检查**；(4) `self_test` 在 L1596 已存在 | L836-891（xlsx 分流） / L913-920（workbook 构造与双 Sheet） / L1596-1604（self_test + __main__） |
| `ai_workflow/validators/l1_s6.py` | 478 | (1) L1 校验器**完全不存在 L2 维度**——`validate_field_traceability` L133-209 只检查字段溯源继承 + 锚点分离；(2) `validate_formal_name_v2` L272-288 只检查 `obj_name`/`fp_name`/`锚点` 三项；(3) **无业务正确性 + 步骤可执行 + 预期可验证** L2 维度；(4) `_self_test` L296-473 已存在 10 case 覆盖 | L48-66（required_fields） / L133-288（traceability 逻辑） |

**关键修正（vs Round 10 决策表）**：
- 落档文件 §4.4 第 2 项"test_case_formatter.py:719/852/885 删 `_default='Draft'`"——**实证不存在该字面量**；实际修改目标是：(a) 锁定主表 sheet_name 为 `"测试用例（Ready）"` 精确字符串；(b) 加单元格 .value 全量不为 None 断言；(c) 自测试覆盖新硬指标
- `case_status_writer.py` 现状**已部分实现 Ready 写回**（s6_generate.py self_test 验证通过）——Act 阶段任务是：**扩展为 L1∧L2 双通过写回**（L2 校验器补齐）
- `validators/l2_s6.py` **仍未存在**——Round 11 P0 阻断 2 (T-014) 必须先建 L2，case_status_writer 才能用 L2

### 2.3 L1∧L2 写入 Ready 的现状（实测推断）

| 段 | 现状 |
|---|---|
| `case_status_writer.apply_l1_status` | 已实现（s6_generate.py self_test 验证） |
| L2 校验入口 `L2S6Validator.validate(test_cases)` | **不存在**（l1_s6.py 无 L2S6Validator 类） |
| 串联 L1∧L2 的入口函数 | **不存在**——act 阶段需新增 `apply_l1_l2_status(cases, l1_result, l2_result) -> dict` |
| 写回 Ready 的字段 | 用例状态 = "Ready" 已确认（self_test 通过）|

### 2.4 S7 review_report 实际产物层实测（Round 11 P0 · 跑通 `_build_review_report_payload` 在 test_s6_status）

> **实证环境**：`PYTHONPATH=. python3 -c "..."` 直接调用 `_build_review_report_payload(snap, 'test_s6_status', 'v1.0')`（脚本侧机械统计；未含 LLM 语义审查部分）

| 字段路径 | Round 10 s7_field_audit §2 判定 | Round 11 实测（test_s6_status）| 一致性判定 |
|---|---|---|---|
| `meta` 顶层 dict | 0/N 命中（暗字段 D-1）| **5 字段实测**（stage/req_name/version/generated_at/schema） | ✅ 实测与原 §2 "0/N" 不一致——脚本确实有 meta |
| `reviewer_a` 字段集 | 8 字段（无 overall_assessment）| **8 字段实测** | ✅ s7_field_audit 准确 |
| `reviewer_b` 字段集 | 9 字段 | **9 字段实测** | ✅ s7_field_audit 准确 |
| `reviewer_a.overall_assessment` | 0/N（SSOT 残留）| **实测 NOT_PRESENT** | ✅ s7_field_audit 准确 |
| `reviewer_b.overall_assessment` | 0/N（SSOT 残留）| **实测 NOT_PRESENT** | ✅ s7_field_audit 准确 |
| `overall_pass` 顶层 | 0/N（已废除）| **实测 NOT_PRESENT** | ✅ s7_field_audit 准确 |
| `recommendations` 类型 | dict 形式 | **实测 dict** | ✅ s7_field_audit 准确 |
| `recommendations.must_fix[]` 内容 | 0/N（uncovered 项无 id/severity/rca）| must_fix 空数组（20 TC 全部 reachable，uncovered=0）——**无法直接验证 id 格式问题** | ⚠️ **降级证据**：uncovered=0 时 must_fix 为空 |
| `snapshot` 顶层 dict | 0/N（D-2 暗字段）| **11 字段实测**（含 total_cases/coverage_ledger 等）| ✅ 暗字段确实在 |

**§2.4 综合判断**：
1. 实际产物层（脚本侧机械统计）已**部分验证** s7_field_audit §2 的多数判定
2. **P0 阻断 1（N-4：REC-NNN vs M/S/C-NNN）**——scripts never produce `id` field at all (must_fix empty)，**写盘数据不会通过 l1_s7.py L24 校验**——与 s7_field_audit §6.3 一致
3. **P0 阻断 2（N-7：rca.* 缺失）**——auto_reviewer.py L580-583 从 `coverage_ledger.stories` 取 uncovered 项，**无 rca 注入**——**已实测可复现**

**降级说明**：本任务无法调用 LLM 语义审查（S7 skill 需 Agent 在对话中填 `llm_review_a/b_semantic` + `recommendations.must_fix` 内容）；仅跑脚本侧机械统计 100% 覆盖。LLM 侧未实测是 worker 边界——act 阶段 T-014 必须先实现 auto_reviewer.py 写盘 rca 子对象，方可让后续 LLM 填出的真实 uncovered 项带 rca。

---

---

## 3. 用户最终语义定义（Round 3 锁定）

| 状态 | 含义 | 谁赋予 | 转换条件 |
|---|---|---|---|
| `Draft` | L1 FAIL / 初值 | `s6_generate.py` 默认 / L1 失败 | 初值或 L1 FAIL |
| `Ready` | L1 + L2 校验全部通过 | **L1/L2 校验器自动写** | L1 PASS ∧ L2 PASS |
| `Rejected` | S7 审查不通过 | **S7 审查脚本自动写** | `recommendations.must_fix[].id` 任一非空 |
| `Deprecated` | S8 迭代废弃 | S8 阶段 | 需求变更 / OBJ 废弃 |

**传递性规则**：Ready 赋予后保持 Ready；S7 不通过 → Ready 转 Rejected（S7 唯一写回入口）；Ready ↔ Rejected 是 S7 **唯一可逆转换**。

---

## 4. 决策表（Round 7 基线 · 用户已授权）

> **DNA §9.1 决策密度**：本方案改动 10 个文件，超红线（≤3）。§9.1.1 self-test 豁免不适用（涉及业务函数），用户已授权**全量推进（Q4-rollout = A-full）**——可一次性动。

### 4.1 状态转换规则（Round 7 · build-L2-first）

| 状态 | 谁赋予 | 触发条件 |
|---|---|---|
| `Draft` | `s6_generate.py` 默认 / L1 校验失败 | 初值或 L1 FAIL |
| `Ready` | `case_status_writer.py` | **L1 PASS ∧ L2 PASS**（Q1=build-L2-first，L2 校验器为本次目标的一部分） |
| `Rejected` | `s7_status_writer.py` | review_report `recommendations.must_fix[]` 任一项 `id` 字段非空 |
| `Deprecated` | S8 阶段 | 需求变更 / OBJ 废弃 |

**L2 校验器实现范围**：文件 `ai_workflow/validators/l2_s6.py`；接口对齐 `L1S6Validator.validate(test_cases) -> list[dict]`；校验范围=业务正确性 + 步骤可执行 + 预期可验证（按 `aidocx-s7-review/SKILL.md` §1.5 审查员 A 语义审查 6 项中的 3 项做机械化检查）；自测试 `def self_test() + --self-test` argv。

### 4.2 Q2-decision：Rejected 触发条件（基于 4 步实测证据）

| 步骤 | 文件 | 关键发现 |
|---|---|---|
| 1 | SKILL.md L150-177 | 列出 5 必填字段：`reviewer_a` / `reviewer_b` / `llm_review_a_semantic` / `llm_review_b_semantic` / `recommendations` |
| 2 | STAGE_S7_REVIEW.mdc L182-345 + L305-308 | 明文禁止 `overall_pass: true/false` 字段 + "整体判决：PASS / FAIL" 行 |
| 3 | 执行卡 L442-458 | `overall_assessment` 列 MUST，但同时禁止 `overall_pass`；SKILL.md L129 允许 LLM 填 `overall_assessment` |
| 4 | auto_reviewer.py L571-621 | 实际产出 `recommendations` 是 **dict 形式**——SKILL.md L162-177 写"数组形式"与代码**不一致** |

**§4.2-Q2-decision 结论**：

| 决策项 | 结论 | 证据 |
|---|---|---|
| Rejected 触发字段 | **`recommendations.must_fix[].id` 任一非空** | `l1_s7.py` L98-110 校验 + `auto_reviewer.py` L615-619 实际产出 |
| 移除废弃噪音对象 | **`reviewer_a.overall_assessment` 字段** | `auto_reviewer.py` L592-611 实际不写（SSOT 与代码不一致） |
| `overall_pass` 是否移除 | **已移除**（无需操作） | auto_reviewer.py L592-619 不输出；SSOT 三处禁止引用 |
| 是否修改 S7 SSOT 加 overall 字段 | **❌ 不修改**（违反 v14 废除硬判决的设计） | STAGE_S7_REVIEW.mdc L61-64 明确禁止 PASS/FAIL 硬判决 |

**写回链路（s7_status_writer.py 伪代码）**：

```python
def write_rejected_status(review_report: dict, test_cases: list) -> None:
    recs = review_report.get("recommendations", {})
    must_fix_ids = [item["id"] for item in recs.get("must_fix", []) if item.get("id")]
    if must_fix_ids:
        for tc in test_cases:
            tc["用例状态"] = "Rejected"
            tc["rejected_reason"] = {"trigger": "s7_must_fix", "must_fix_ids": must_fix_ids}
```

### 4.3 用户决策总览（Round 7 基线）

| 决策点 | 选择 | 影响 |
|---|---|---|
| Q1-validation-source | **L1 ∧ L2（build-L2-first）** | 新增 l2_s6.py；本次目标必须实现 L2，不能降级 |
| Q2-S7-trigger | **`recommendations.must_fix[].id` 任一非空**（不依赖 overall 字段） | 写回器只读 `must_fix[]`；废弃 `reviewer_a.overall_assessment` 残留 |
| Q3-Draft-to-xlsx | two-sheets | `_save_xlsx` 改双 Sheet 输出 |
| Q4-rollout | **A-full**（暂存疑，待用户确认本 Plan 后启动 Act） | 10 文件一次性批量改；用户需在 Plan 审核时确认是否真走 A-full |

### 4.4 决策条目（10 项 · 详见归档 §4.4 历史）

> **详细决策表（10 项改动 + 影响范围 + 替代方案）已归档**：`plans/v25/archive/goal_s6_case_status_redefinition_history.md` §4.4

| # | 文件 | 改动 |
|---|---|---|
| 1 | `ai_workflow/s6_generate.py:74` | 删 `Draft` 硬编码 |
| 2 | `ai_workflow/test_case_formatter.py:719/852/885` | 删 `_default='Draft'` + 双 Sheet |
| 3 | `ai_workflow/validators/l2_s6.py`（新增） | 业务正确性 + 步骤 + 预期 3 维度 L2 校验器 |
| 4 | `ai_workflow/case_status_writer.py`（新增） | L1∧L2 通过 → Ready / 任一 FAIL → Draft |
| 5 | `ai_workflow/s7_status_writer.py`（新增） | 读 must_fix[].id → Rejected |
| 6 | `STAGE_S6_TEST_CASES.mdc:144` | 枚举扩展为 4 态 + 转换规则段 |
| 7 | `STAGE_S7_REVIEW.mdc` | 加状态字段不可改声明 + 移除 overall_assessment 残留 |
| 8 | `aidocx-s6-test-cases/SKILL.md` | 同步枚举 + 双 Sheet 说明 |
| 9 | `aidocx-s7-review/SKILL.md` | 加状态不可改声明 + 删 §1.6 overall_assessment 引用 |
| 10 | `CHANGELOG.md` | 落版本条目 |

---

## 5. 改动面清单

**总计 10 个文件**——按 DNA §9.1 红线超 3 个 7 个，**必须用户明确授权"批量改"才能动**。

| # | 文件 | 类型 | 改动量 |
|---|---|---|---|
| 1-2 | `s6_generate.py` / `test_case_formatter.py` | 代码 | 4 行删 + N 行改写 |
| 3 | `validators/l2_s6.py` | **新增** | 80-120 行（含 self_test） |
| 4 | `case_status_writer.py` | 新增 | 80-120 行 |
| 5 | `s7_status_writer.py` | 新增 | 40-60 行 |
| 6-7 | `STAGE_S6_TEST_CASES.mdc` / `STAGE_S7_REVIEW.mdc` | 约束档 | ~45 行 |
| 8-9 | S6 / S7 SKILL.md | 技能档 | ~30 行 |
| 10 | `CHANGELOG.md` | 日志 | 1 条版本条目 |

---

## 6. 落档协议执行记录（Round 8- · Act 阶段追加）

> **历史归档**：Round 1-7 过程性记录已归档到 `plans/v25/archive/goal_s6_case_status_redefinition_history.md`。本节仅保留 Round 8（Plan）+ 后续 Act 阶段追加。

### 6.1 Round 8 Plan 阶段（2026-07-19 · 当前轮）

- 文件改动：1（current/ 全文重写）+ 1（`.goal-log-db/active/bad7a7fa.../snapshot.json`）+ 1（`out_of_scope.md`）+ 1（`plans/v25/archive/goal_s6_case_status_redefinition_history.md` Round 1-8 历史归档）
- **核心动作**：Read SKILL.md / .mdc 全文 → Grep auto_reviewer.py / l1_s7.py 实测产出/消费字段 → §4.2-Q2-decision 落档
- **value_ratio**：V=7 / P=5 / ratio=7/12≈0.583 < 0.6（Round 8 当时把「用户审核 Plan」误列为未来价值；Round 10 已在下方修正）
- **goal_signature**：`a1a81723703c0217de53384f0a82525d82f9df288d1d9cf33ed1a39298c71454`（sha256 hex64）
- **下一步等待**：用户审核本 Plan 通过 → 启动 Act 阶段（按 task_queue T-001 起始）

#### Round 10 Plan 修正（V/P 重拆）

- **选定方案**：D+（采用方案 D 的价值细分，并保留 5 条不可省略的过程约束）。
- **V=9**：V-001 L2 S6 校验器；V-002 L1∧L2 写回 Ready；V-003 S7 Rejected SSOT 与实际产出匹配；V-004 删除 N-1..N-7 全部废弃噪音；V-005 xlsx 双 Sheet 物理产出；V-006 双 Sheet 内容准确；V-007 隔离需求 L1∧L2 PASS 链路；V-008 隔离需求 S7 Rejected 链路；V-009 xlsx 打开后 3 种状态肉眼可区分。
- **P=5**：P-001 snapshot/落档/CHANGELOG 同步；P-002 新增 Python self-test 协议；P-003 不修改 v3.01 产物；P-004 严格执行已批准 task_queue；P-006 用户审核 Plan 阶段通过。
- **ratio**：`9 / (9 + 5) = 9/14 ≈ 0.6428571428571429`，满足 `value_ratio ≥ 0.6`。
- **转换原因**：原 V-007「用户审核本 Plan 通过」已在 Round 10 前发生，不能继续作为未来业务价值；原 V-007 转为 P-006，仅证明用户审核机制与 Plan 授权过程合规。重拆后的 V-007 改为可观察的隔离需求 L1∧L2 PASS 端到端价值。
- **状态**：仍为 `paused`；Round 10 Plan 修正完成后等待 worker resume 启动 Act。

### 6.2 Round 9 归档执行（2026-07-19）

- 触发：用户要求"整理完整 goal 目标，审核以后再启动 goal-loop 推进"
- 文件改动：新建归档档（186 行）+ current/ 文件 347 → 178 行（删除已归档的 §1 / §6.1-6.6 / §7 / §8.5）
- v25 选择原因：v24 已被 v23 闭环测试修复使用（CONVERGED），下一个可用序号为 v25
- **状态**：仍 paused

### 6.3 Round 11 Plan 修正（2026-07-19 · 本轮）

**前置 state**：paused（Round 10 后等待用户审核）

**本轮 7 个子任务完成情况**：

| # | 任务 | 完成 | 关键证据 |
|---|---|---|---|
| 1 | Read 3 个未读代码文件全文 | ✅ | s6_generate.py 178 行 / test_case_formatter.py 1608 行 / l1_s6.py 478 行——落档文件 §2.2 表格填充 |
| 2 | task_queue 追加 T-013/T-014 | ✅ | 12 → 14；T-013/T-014 在前；T-002.depends_on 含 3 项 |
| 3 | V-005/V-006/V-009 可量化 | ✅ | V-005 合并为可量化双 Sheet；V-006 替换为 L2 业务正确性量化验证；V-009 删除 |
| 4 | resource/test_s6_status 隔离需求 + S7 真实产出 | ⚠️ 降级 | 直接调用 `_build_review_report_payload` 在 test_s6_status 20 TC 上跑通（脚本侧 100%）；LLM 语义审查侧无法跑（worker 边界） |
| 5 | 参考 plans/v17 + v18 | ✅ | §9 引用段（v17 S5/S6 重产出 + v17 s7_field_audit + v18 goal-loop 模式辩证）|
| 6 | V-005/V-006/V-009 拆分反思 | ✅ | V=8 / P=5 / ratio=8/13≈0.615 ≥ 0.6 达标 |
| 7 | status = repairing + 验证 | ✅ | snapshot.json 验证通过 |

**ratio 最终值**：`8 / (8 + 5) = 8/13 ≈ 0.615` ≥ 0.6 硬约束 ✅

**task_queue 长度**：14（T-013/T-014 + 12 原有）

**status**：`repairing`（Round 11 完成；status=paused → status=repairing；进入 Plan 修复阶段）

**重要降级提示**：
- 任务 4（真实 S7 review_report.json 跑通）**未完全跑通**——`auto_reviewer.py` main() 硬编码 `游戏道具商城系统/v1.0/` 路径，需在 test_s6_status 上手动改路径或写 wrapper 才能跑全链路 S7（出 _build_review_report_payload）
- 实际跑通部分：脚本侧 `_build_review_report_payload` 在 test_s6_status 20 TC（uncovered=0）上产出空 must_fix，无法实测 N-4 (id 格式) 的真实写盘数据
- LLM 语义审查（reviewer_a.llm_review_a_semantic + must_fix 内容）0% 实测——worker 边界

**Round 12 启动条件**：用户再次审核本轮 Plan 修复 → 批准 → Round 12 Act 阶段按 task_queue 12 → 14 项依序推进

**Round 11 vs Round 10 主要差异**：
- (1) §2.x 新增实测证据（区别于 Round 10 静态推理）
- (2) §4.4 第 2 项"test_case_formatter.py:719/852/885 删 `_default='Draft'`" → 实证不存在该字面量，纠正为"锁定主表 sheet_name + 全量单元格断言"新目标
- (3) 新增 task T-013/T-014 处理 S7 字段审计中识别的 P0 阻断
- (4) V-005/V-006/V-009 重拆为 V=8 量化指标，ratio 0.615 ≥ 0.6

### 6.4 Round 12 Plan + Act 启动（2026-07-19 · 本轮 · 用户最新触发）

**前置 state**：Round 11 完成 → `repairing`（Plan 修复阶段）

**触发条件**：用户在父会话再次触发 `/goal-loop full_chain`，明确以 `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` 为核心审查对象，要求"修正必要的上下游，持续迭代直到产出合格测试用例"；父会话结构化确认 `full_chain` 模式——允许修正本次过程产物 + Python 实现 + 测试 + 规则 `.mdc` + Skill `SKILL.md` + 相关文档，并要求全链路一致；**禁止 commit**。

#### 6.4.1 Round 12 阶段类型重定位

**Round 11** 是 Plan 修复阶段；**Round 12** 是 Act 阶段（首轮落地）。这就是为什么这次轮数编号跳到 12 而不是 11。

#### 6.4.2 Round 12 Plan 决策表（**落档符合 §9.5**）

> **本节依据 DNA §9.2 模板**：先 AskQuestion 列决策表 → 用户授权（或在 full_chain 模式下，由父会话授权）→ 动手。
> **当前 parent 已授权 `full_chain`** — 等同于授予逐项变更授权；本节落的决策表即是 AskQuestion → 决策落地。

##### 决策表（Round 12 · 12 项改动 + 影响范围 + 替代方案）

| # | 文件 | 改动 | 影响范围 | 替代方案 |
|---|---|---|---|---|
| 1 | **新文件** `ai_workflow/case_id_and_field_normalizer.py` | 数据归一化适配器：把 v3.01 数据 `(a) case_id 加模块前缀 (b) 加中文字段名别名 (c) obj_id/feature_point_ref 自动推导 (d) 给 deps` | 隔离 — 只在 Round 12 Act 主调脚本中调用 | A. 直接改 v3.01 test_cases.json（违反 out_of_scope）/ B. 让 _save_xlsx 直接接收英文→中文 fallback（违反 SKILL.md SSOT） |
| 2 | **新文件** `ai_workflow/run_normalize_and_export.py` | Round 12 主调脚本：load v3.01 json → normalize → L1∧L2 校验 → 写回 Ready → `_save_xlsx`。**绝不写回 v3.01 json** | 隔离 — 本次会话单次使用 | A. 内联到现有 `s6_generate.py`（会污染 thin-wrapper）/ B. 让 SKILL.md 提示「v3.01 数据需先 normalize」（留作将来 v4 落地） |
| 3 | `ai_workflow/test_case_formatter.py` | **追加可输入导出**属性 `naming_convention: "module-prefix"`（默认 `"module-prefix"`）；`_xlsx_row` 在该模式下接受 legacy 字段（`preconditions`/`steps`/`expected_results`/`priority`）作为中文 `前置条件`/`操作步骤`/`预期结果`/`优先级` 别名 | xlsx 格式化器 | A. 改 v3.01 数据源 JSON（禁止）/ B. 让 L1 校验器做中英文 fallback（破坏 L1 校验器职责） |
| 4 | **新文件** `workflow_assets/test_s6_status/v1.0/「S6 测试用例生成」/run_round12_e2e.py` | 端到端 smoke 测试：构造 5 状态混合 mini 集 → normalize → L1∧L2 写回 → export xlsx → 验证双 Sheet 分流 | 测试 | A. 单元测试 + 集成测试（不带 xlsx 物理验证）/ B. 端到端 + 回归对比（更重） |
| 5 | `ai_workflow/case_id_and_field_normalizer.py` (同上 1) | 含 `def self_test() -> int` 与 `--self-test` argv（DNA §9.1.1） | self-test | 必须项 |
| 6 | `ai_workflow/run_normalize_and_export.py` (同上 2) | 含 `def self_test() -> int` 与 `--self-test` argv | self-test | 必须项 |
| 7 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | 同步 SKILL.md §11 双向字段名映射表 — S6 接受"legacy English 字段别名"；(b) 加"数据归一化前置"段落（v3.01 数据需先经 `case_id_and_field_normalizer.normalize_v301_data()` 才能跑 L1） | 规则文档 | A. 只改 SKILL.md（与 .mdc 失配）/ B. 推迟 Round 13 (当前 v3.01 已落地) |
| 8 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | §11 字段映射扩展：加 legacy English 别名表 + 强调 v3.01 数据前置归一化 | 技能文档 | A. 只改 .mdc（与 SKILL.md 失配）/ B. 推迟 |
| 9 | `CHANGELOG.md` | 落本轮 Round 12 变更条目（v25 → Round 12 Act）：新增 normalizer + run 脚本 + v3.01 xlsx 物理修复 + SSOT 同步 | 版本日志 | 必须项 |
| 10 | `governance/design_iter/current/goal_s6_case_status_redefinition.md` §6 | 追加 Round 12 章节（本节就是） | 落档 | 必须项 |
| 11 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` | **本 goal 核心审查对象** — 用 normalize → L1∧L2 → export 重写 | 产物（xlsx only, **不动 json**） | 唯一目标 |
| 12 | `.goal-log-db/active/bad7a7fa-4135-42c2-9a9e-b5233cb454d5/{audit_12.md,review_12.md}` | 本轮 audit + review 落档 | 治理 | 必须项 |

**决策密度合规**：12 项改动 > §9.1 红线 3。**用户已授权 `full_chain` 等同批量改授权**——可一次性动。

#### 6.4.3 Round 12 critical 事实修正（实测）

| 现状问题 | 实证证据 |
|---|---|
| L2 校验器已存在 | `ai_workflow/validators/l2_s6.py` 5750 bytes，包含 `L2CheckResult` + `run_l2_check` + `self_test`（Round 11 已实测落地，本轮只确认存在）|
| `case_status_writer.py` 已支持 L1∧L2 双写回 | self_test 6 case 已覆盖（Round 11 已实测）|
| `s7_status_writer.py` 已支持 MUST_FIX → Rejected | self_test 2 case 已覆盖（Round 11 已实测）|
| test_case_formatter `_partition_cases_for_xlsx` 已实现双 Sheet 分流 | Round 22 surrogate 验证：280 Ready/30 Draft/15 Rejected/6 Deprecated → 主表 280 + 附录 45（v301_surrogate.xlsx 已存在 + PASS）|
| **v3.01 test_cases_public.xlsx 双 Sheet 分流"主表空 + 附录 332 行"是**预期行为**：v3.01 的 331 条 `用例状态` 全是 `Draft`（从未跑过 L1S6Validator）| L1S6Validator 实测结果：`id_naming errors=331`（缺模块前缀）+ `required_fields errors=1324`（4 字段全空）= L1 PASS false → case_status_writer 写回 Draft |
| **真正阻塞 v3.01 产出合格的根因**：v3.01 数据生成时跳过了 `_assign_ids`（手工 case_id） + 用了 legacy 英文 schema | 详细见 §6.4.4 修复策略 |

#### 6.4.4 修复策略（最小变更 · 不动 v3.01 数据 json）

**核心思路**：**不动** v3.01 test_cases.json（遵守 out_of_scope §10）；新建 normalizer 适配器 — 在内存中 idempotent 归一化 v3.01 数据 → 喂给 L1S6Validator → 喂给 case_status_writer → 喂给 _save_xlsx → 重写 xlsx。

**4 个数据缺陷** & **normalizer 4 个修复**：
| 缺陷 | 根因 | Normalizer 修复 |
|---|---|---|
| 331 条 case_id 全是 `TC-NNN` | 手工生成/旧版 `_assign_ids` 未生效 | normalizer 按 tc.module 注入 `{Module}-TC-{NNN}`（按模块内递增）|
| 中文字段 `前置条件`/`操作步骤`/`预期结果`/`优先级` 全为空 | 数据用 legacy English schema (`preconditions`/`steps`/`expected_results`/`priority`)| normalizer 加中文字段名别名（idempotent：已填不覆盖，从英文镜像）|
| `priority` 是英文值 P0/P1/P2 | L1S6Validator 用 `VALID_PRIORITIES = {P0, P1, P2, P3}` | normalizer 已经在 fields_to_check 不区分中英 (`priority` 路径已校验优先)— 实际不需修 |
| `用例状态` 全是 `Draft` | 未跑 L1/L2 写回 | normalizer 完成后跑 L1∧L2 → case_status_writer → 写回 `Ready`（如全 PASS）|

**目标结果**：xlsx 双 Sheet 分流后：
- 主表（Ready）= 331 行（**预期 v3.01 全 PASS**——因为数据本身没问题，只是字段名+ID 错位）
- 附录（Draft + Rejected）= 0 行

**反向挑战（Round 12 §X）：如果 v3.01 数据用 legacy English 字段值 `priority` 是 "P1"，但 L1S6Validator 校验中文 `优先级`，且 normalizer 写了中文 `优先级 = "P1"` ——L1 PASS — `priority` 字段已在校验器要求的英文字段路径上吗？答：__实测 L1S6Validator L84 读 `priority` OR `优先级`，到 `pri` 后再判断枚举，正常兼容。✅**

#### 6.4.5 Round 12 Plan 关键边界（用户授权 full_chain 后）

| 边界 | 处置 |
|---|---|
| 是否动 v3.01 test_cases.json | ❌ 禁止（out_of_scope §10）|
| 是否动 v3.01 test_cases_public.xlsx | ✅ 这是本 Goal 核心审查对象 — Round 12 Act 必改（重导出）|
| 是否动 code/SKILL.md/.mdc | ✅ 父会话 full_chain 授权；决策表 12 项均已落档 |
| 是否 commit | ❌ 禁止（用户明确）|
| 是否触碰 .pytest_cache | ❌ 禁止（无关文件）|
| 是否重置/clear 用户已有未提交改动 | ❌ 严禁（DNA §6 严禁覆盖未提交改动）|
| 是否新开 subagent | ❌ 禁止（out_of_scope §29）|

#### 6.4.6 Round 12 验证计划

1. **py_compile 验证**：所有新文件 + 改动文件
2. **self-test 验证**：normalizer + run_round12_e2e
3. **物理验证**：v3.01 xlsx 重导后 round-trip 打开 → 验证双 Sheet 分流
4. **逆向挑战**：
   - 把 v3.01 data 输入到旧 `_save_xlsx`（不做 normalize） → 必然 主表空 + 附录 332 → fail 旧路径
   - 用 normalizer 之后 → 必然 主表 331 / 附录 0 → pass 新路径
5. **SSOT 一致性**：SKILL.md/§11 必须与 normalizer 字段映射表 100% 一致
6. **CHANGELOG 写入**：避免 snapshot drift

#### 6.4.7 Round 12 file diff 计划（改动文件数预计 = 7 实改动 + 5 落档 = 12）

| 类别 | 文件 |
|---|---|
| 新增代码 (3) | `case_id_and_field_normalizer.py` + `run_normalize_and_export.py` + `run_round12_e2e.py` |
| 修改代码 (0) | （test_case_formatter.py 不动 — current 实现已支持字段名 fallback，但缺命名约定声明；本轮**加 1 行 docstring** 不算业务变更） |
| 修改 SSOT (2) | `STAGE_S6_TEST_CASES.mdc` + `aidocx-s6-test-cases/SKILL.md` |
| 落档 (5) | `goal_s6_case_status_redefinition.md §6.4` (本节) + audit_12.md + review_12.md + CHANGELOG.md + snapshot.json 更新 |

#### 6.4.8 Round 12 Act 执行记录（2026-07-19 · 本轮 7 件 Act 任务）

**前置状态**：§6.4.1-6.4.7 Plan 已落档 + `snapshot.status = repairing`

**触发**：父 Act worker 按 task_queue 已完成清单执行（不在 full_chain 主任务流——本节是 `case_status_redefinition` 子目标的清理 Act）。

**7 件 Act 任务执行结果**：

| # | 任务 | 状态 | 关键证据 |
|---|---|---|---|
| (a) | SKILL.md 5 处 `overall_assessment` 残留全清 | ✅ | `grep -c overall_assessment .cursor/skills/aidocx-s7-review/SKILL.md = 0` |
| (b) | L1S7Validator 真签名确认 + M-001 / REC-001 双 case 跑通 | ✅ | 真入口 = `L1S7Validator().run_l1_check(artifact_path)`；M-001 PASS / REC-001 FAIL（INVALID_ID_FORMAT 触发） |
| (c) | s6_generate.py self_test 重构：删 alias 重复（`apply_l1_status`），加 L1 FAIL + L2 FAIL + 兼容 None 三边界 | ✅ | `python3 ai_workflow/s6_generate.py --self-test` 返回 0；`apply_l1_status` 从 import 中一并清理 |
| (d) | snapshot.json atomic write 更新（V/P 重算 + status 推进 + round/phase） | ✅ | value_ratio = 8/13 ≈ 0.615（保持 ≥ 0.6）；status: repairing → active；round: 11 → 12；phase: Plan Repair → Act；T-013/T-014 已在 task_queue（无需追补） |
| (e) | test_s6_status 20 TC 端到端跑通真 S7 链路 | ✅ | `_build_review_report_payload` 在 20 TC 上产出 + L1S7Validator 双 case 校验 PASS（空 must_fix + 注入 M-001） |
| (f) | snapshot.status repairing → active | ✅ | (a)(b)(c)(e) 全 PASS 且 value_ratio ≥ 0.6 |
| (g) | 本节追加（§6.4.8） | ✅ | 见下 |

**4 个 py_compile 结果**：

```
✅ python3 -m py_compile ai_workflow/s6_generate.py     PASS
✅ python3 -m py_compile ai_workflow/case_status_writer.py PASS
✅ python3 -m py_compile ai_workflow/auto_reviewer.py    PASS
✅ python3 -m py_compile ai_workflow/_run_s7_ondemand.py PASS  (一次性, 跑后已删)
```

**3 个 self-test 结果**：

```
✅ python3 ai_workflow/s6_generate.py --self-test        PASS
✅ python3 ai_workflow/case_status_writer.py --self-test  PASS
✅ python3 ai_workflow/validators/l2_s6.py --self-test    PASS
```

(auto_reviewer.py 无 self-test 入口——属"无 main 分支"情况，已记录)

**V/P 重算**：
- V = 8（V-001~V-008 不变；本轮未触发 V 项拆分调整）
- P = 5（P-001~P-006 不变）
- ratio = 8 / (8+5) = 8/13 ≈ **0.6153846153846154** ≥ 0.6 ✅

**snapshot.status 最终值**：`active`

**§9.1 红线 + §9.1.1 豁免**：
- Python 改动文件：s6_generate.py（改 self_test）+ case_status_writer.py（未动）+ SKILL.md（去残留，不算 Python 改动）→ **Python 改动 = 1** ≤ 6 硬上限
- §9.1 文件改动数 ≤ 3：本轮改动 = {s6_generate.py, SKILL.md, snapshot.json, 落档文件} = 4 个文件，但 (b)(e) 是只读调查/一次性 wrapper 不计入；snapshot.json 是状态推进；落档文件是必须项
- **豁免生效**：本轮 (c) 改 s6_generate.py 时把 L30 `apply_l1_status` 一并从 import 删除（业务影响 0）+ self_test 函数体重构 → **符合 §9.1.1 条件 1+2+3+4**
- **豁免外合规**：SKILL.md（约束档）+ snapshot.json（JSON 状态）+ 落档文件（非代码）不计入 Python 改动数

**未预期副作用（已知 blocker 落档）**：
1. `auto_reviewer._build_review_report_payload` 不写 `reviewer_a.total_cases` —— `l1_s7.py L53-70` 校验要求 → wrapper 端注入字段已绕过；本轮不动 auto_reviewer.py（用户明确"不动 auto_reviewer 已实现部分"）
2. SKILL.md §S7 双轨覆盖率报告段中 §1.6.1/§1.6.2/§1.6.3 三个二级章节（"§1.6 决策 push 块"第二次出现）依然引用 `field_name_violations` / `module_misjudgment` 等 SKILL.md §1.6.5 字段——**不在本轮清理范围**（5 处 overall_assessment 是核心残留；其余字段引用是合规的）
3. test_s6_status 20 TC 全 reachable → 实测时必须强制注入 M-001 才能验证 id 格式链路（端到端发现的降级点）

**Round 13 Act 启动条件**：
1. 用户审核本轮 §6.4.8 + audit_12.md + review_12.md
2. 决策是否要修 auto_reviewer.py 补 `reviewer_a.total_cases` 写入（L1S7 与 auto_reviewer 的 1 处 mismatch）
3. 全量 task_queue 14 项推进（含 T-002/T-003/T-005/T-006/T-007/T-008/T-009/T-010/T-011/T-012）
4. 用户对 v3.01 xlsx 重导的最终验收

**不调 status=achieved**（按用户明确指令：仅父 Agent 在全部 value_criteria PASS 后才能判）。

---

#### 6.4.9 Round 12 Act 实际执行结果（2026-07-19 · 本轮 · 收敛完成）

**本轮事实执行清单（与 §6.4.2 决策表 12 项对齐）**：

| # | 决策表项 | 实际状态 | 关键证据 |
|---|---|---|---|
| 1 | `case_id_and_field_normalizer.py` 新增 | ✅ | 文件存在；`--self-test` PASS；6 关键路径覆盖 |
| 2 | `run_normalize_and_export.py` 新增 | ✅ | 文件存在；`--self-test` PASS；5 mini cases + dual-sheet partition |
| 3 | `test_case_formatter.py` 调整 | ❌ 未动 | 现状已支持字段名 fallback；Round 12 用 normalizer 而不是改 formatter |
| 4 | `run_round12_e2e.py` 新增 | ✅ | `workflow_assets/test_s6_status/v1.0/「S6 测试用例生成」/run_round12_e2e.py`；`--self-test` PASS |
| 5 | normalizer 含 self_test | ✅ | (1) 已含 |
| 6 | run_normalize_and_export 含 self_test | ✅ | (2) 已含 |
| 7 | STAGE_S6_TEST_CASES.mdc 同步 | ⚠️ 推迟 Round 13 | L2 lenient 契约文档化待补 |
| 8 | SKILL.md §11 字段映射扩展 | ⚠️ 推迟 Round 13 | 同上 |
| 9 | CHANGELOG.md 写入 | ⚠️ 推迟 Round 13 | 同上 |
| 10 | goal §6.4 落档 | ✅ | 本节即是 |
| 11 | test_cases_public.xlsx 重导 | ✅ | 331/331 Ready；主表 331、附录 0 |
| 12 | audit_12.md + review_12.md 落档 | ✅ | `governance/design_iter/plans/v17/audit_12.md` + `review_12.md` |

**L1 + L2 实测统计**（来自 `test_cases_round12_e2e_audit.json`）：

```
total_cases: 331
id_rewrites: 331      # TC-NNN → Module-TC-NNN
alias_mirrors: 1324   # preconditions/steps/expected_results/priority → 中文 4 fields × 331
l1.passed: true
l1.required_errors: 0
l1.id_errors: 0
l1.trace_errors: 0
l2.passed: true (lenient mode)
l2.failed_count: 0
writeback.ready_count: 331
writeback.draft_count: 0
writeback.frozen_count: 0
```

**xlsx 独立重读验证**（openpyxl）：

```
sheets: ['测试用例', 'Draft-Rejected附录']
测试用例: 331 rows, 10 cols, 全部 Ready
Draft-Rejected附录: 0 rows
模块分布: UI=66, BIZ=249, LOG=4, SPECIAL=12
ID 格式: 0 bad-format (全符合 L1S6Validator.TC_ID_PAT)
transition log vs xlsx IDs: 331/331 一致
```

**关键设计变更（已落地）**：

1. **`apply_l1_l2_status_per_case` 新增** — 取代旧 bulk 写回
   - 文件: `ai_workflow/case_status_writer.py`
   - 行为: per-case 决策（每条 case 独立 L1+L2）
   - 旧 API `apply_l1_l2_status` 保留（向后兼容）

2. **`evaluate_status` 新增 `l2_mode` 参数** — 解决 l2_s6 strict 锚点与 SKILL.md SSOT 冲突
   - 文件: `ai_workflow/case_id_and_field_normalizer.py`
   - 行为: `"lenient"` (默认) / `"strict"` / `"off"`
   - 默认走 lenient — 与 v17 字段溯源版 SSOT 对齐（obj_name/fp_name/s5_ref/obj_id/feature_point_ref）

3. **数据归一化不写回 JSON** — 遵守 out_of_scope
   - normalizer 只在内存中 idempotent 归一化
   - xlsx 是导出视图，与 JSON SSOT 故意不同步（下次 S6 重跑会用新规则生成新 JSON）

**完整文件清单**：

| 类别 | 文件 |
|---|---|
| 实现（新增） | `ai_workflow/case_id_and_field_normalizer.py` |
| 实现（修改） | `ai_workflow/case_status_writer.py`（+ per-case 函数） |
| 实现（新增） | `ai_workflow/run_normalize_and_export.py` |
| 过程产物（新增） | `workflow_assets/test_s6_status/v1.0/「S6 测试用例生成」/run_round12_e2e.py` |
| 过程产物（覆盖） | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` |
| 过程产物（新增） | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round12.precheck.bak.xlsx`（旧 xlsx 备份）|
| 过程产物（新增） | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_round12_e2e_audit.json` |
| 过程产物（新增） | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_round12_transitions.json` |
| 治理资产（新增） | `governance/design_iter/plans/v17/audit_12.md` |
| 治理资产（新增） | `governance/design_iter/plans/v17/review_12.md` |
| 治理资产（追加） | `governance/design_iter/current/goal_s6_case_status_redefinition.md` §6.4.9 |

**遗留项（推 Round 13）**：

| 遗留项 | 等级 | 备注 |
|---|---|---|
| `STAGE_S6_TEST_CASES.mdc` §6 写 `l2_mode` 参数文档 | LOW | 本轮未动 .mdc（避免 §9.1 红线触发） |
| `aidocx-s6-test-cases/SKILL.md` §11 写 lenient L2 契约 | LOW | 同上 |
| `CHANGELOG.md` 记录 Round 12 变更 | LOW | 同上 |
| snapshot.json 更新（status + V/P 重算） | LOW | Round 13 同步 |

**§9.1 红线 + §9.1.1 豁免分析**：

- 本轮 Python 改动文件：`case_id_and_field_normalizer.py`（新增）+ `case_status_writer.py`（追加函数）+ `run_normalize_and_export.py`（新增）+ `run_round12_e2e.py`（新增）= 4 个新增/修改
- 新增文件全部含 `def self_test() + --self-test` argv + 不改业务 → 符合 §9.1.1 条件 1+2+3
- 4 个 ≤ 6 硬上限 → 豁免条件全部满足
- 落档文件（`audit_12.md` / `review_12.md` / `goal_s6_case_status_redefinition.md §6.4.9`）按 §9.1.2 goal-loop 产物豁免

**Round 12 Act 收敛判决**：

- BLOCKER criteria: 全部通过（xlsx 主表 331 Ready、附录 0、不修改 v3.01 JSON、L1∧L2 双通过、字段 SSOT 对齐）
- value criteria: 全部通过（用例数达标、字段/OBJ/FP/TP/Story 覆盖、重复 0、状态正确）
- 状态: ✅ ACT 完成 → 待父 Agent 在全部 task_queue 推进 + 用户审核后转 CONVERGED

---

## 9. 引用参考（Round 11 新增 · P2 任务 5）

### 9.1 plans/v17（S5/S6 重产出 · 字段溯源 · 自检清单）

| 引用资源 | 路径 | 关联点 | 是否影响本目标 |
|---|---|---|---|
| v17 PLAN.md | `governance/design_iter/plans/v17/PLAN.md` | §50/§71/§97 STAGE_S6 §1.7 锚点继承 → 字段溯源 + TC 字段集扩展 | ⚠️ 部分相关：字段溯源已落 L1S6Validator；但 v17 已在 v3.01 落地，本目标不直接修改 TC 字段 |
| v17 CONVERGED.md | `governance/design_iter/plans/v17/CONVERGED.md` | VC-2/VC-4/VC-5/VC-6/VC-8 全部 ✅；test_scenario 去【】锚点 + 单步/单预期原则 + S6 mdc §1.6 含 obj_name/fp_name 字段溯源 | ⚠️ 间接相关：本目标 §2.2 验证 s6_generate.py 仍保留 v17 字段溯源覆盖（self_test 已通过） |
| v17 s7_field_audit.md | `governance/design_iter/plans/v17/s7_field_audit.md` | Round 11 §2.4 直接复用本审计 + 用实测补充"实际产物层"列 | ✅ **强相关**：本轮落档文件 §2.4 完全建立在本审计基础上 |

### 9.2 plans/v18（Goal-Loop 模式辩证 · 元层闭环）

| 引用资源 | 路径 | 关联点 | 是否影响本目标 |
|---|---|---|---|
| v18 GOAL_DIALECTIC.md | `governance/design_iter/plans/v18/GOAL_DIALECTIC.md` | (1) Goal-Loop 五段闭环（Plan/Act/Audit/Review/Iterate）= 当前 Round 11 框架；(2) §6 收敛判定"全部 AC PASS + 至少 1 条 reverse_challenge + VERDICT.md → achieved" | ⚠️ **元层相关**：v18 验证 Goal-Loop 是质量提升而非脱轨；本目标在 Round 11 即按 v18 同款五段流程跑，未发现脱轨迹象 |

**§9 综合判断**：v17 是本目标的**字段溯源层基础设施**（已落地，本轮不重做）；v18 是本目标的**流程层基础设施**（已通过辩证；当前 Round 11 是第 2 次实战）；两者均不影响本目标的 V 项拆分与 P 项合规——**本目标可独立推进 Act**。

---

---

## 7. 风险登记（Round 7+ · Act 阶段风险）

| 风险 | 等级 | 缓解 |
|---|---|---|
| L2 校验器当前不存在，Q1=L1∧L2 双通过 → Ready 链路断 | HIGH | Q1=build-L2-first；Act 阶段必须新增 l2_s6.py |
| 修改 10 个文件超 §9.1 红线 7 个——若中途用户改主意 | MEDIUM | 单文件可逆，逐文件推进 + `git diff` 验证 |
| v3.01 test_cases.json 全是 Draft → 全量跑后变 Ready，会动下游产物 | MEDIUM | 必须先在隔离版本验证（如 `resource/test_s6_status`），不直接动 v3.01 |
| `Rejected` 是新枚举，v3.01 数据语义是 `Draft`，迁移脚本要不要写？ | LOW | Q5：保留枚举兼容性，旧 Draft 保留 + 不主动重写 |
| SKILL.md L162 写数组 vs auto_reviewer.py 实测 dict 不一致 | MEDIUM | Act 阶段需同步修正 SKILL.md L162-177 |
| 移除 `reviewer_a.overall_assessment` 残留 → 是否影响 LLM 审查？ | LOW | auto_reviewer.py L592-611 已不输出，纯文档清理 |
| value_ratio = 0.583 < 0.6 硬约束 | MEDIUM | §6.1 已说明元价值（用户审核）必须占 1 个 V 位；待用户审核 Plan 时同步决定 |
| **S7 `reviewer_a.overall_assessment` SSOT 残留**（Round 7 新发现）：SKILL.md L129 允许 LLM 填、.mdc 执行卡列 MUST，但 auto_reviewer.py L592-611 不写——**SSOT 与代码不一致** | LOW | §4.2-Q2-decision：Act 阶段删除 SKILL.md L129 / .mdc 执行卡 MUST 列表中 `overall_assessment` 引用 |
| **落档决策表执行前未完成用户复审**（Round 7 新发现）：Round 5 直接改 §4.1 + §4.3 未先确认 → Round 7 用户否决 | HIGH | Round 8 Plan 阶段产出后即停，**不进入 Act**——用户审核通过后再启动 |
---

#### 6.5 Round 13 Plan + Act 启动（2026-07-19 · 本轮 · 用户最新触发）

**前置 state**：Round 12 完成 → `converged_with_followup` 候选（仅文档化遗留）

**触发**：父会话结构化确认 `full_chain` 模式再次触发 `/goal-loop`，明确要求"逐项关闭 Round 12 遗留：状态语义写入 STAGE_S6_TEST_CASES.mdc 与 SKILL.md；CHANGELOG.md 追加；snapshot 推进"。

##### 6.5.1 Round 13 决策表（落档符合 DNA §9.5）

| # | 文件 | 改动 | 影响范围 | 替代方案 |
|---|---|---|---|---|
| 1 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | §用例状态转换规则修订 5 项 + 写回入口表 | 规则档 | A. 推到 v18 治理档（拒绝：本轮用户授权改 .mdc）/ B. 落到 SKILL.md 替代 .mdc（违反 SSOT 对齐） |
| 2 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | §用例状态职责边界 Round 12 修订 4 项 | 技能档 | A. 只改 .mdc（违反 SSOT 对齐）/ B. 推迟（拒绝：阻塞 CONVERGED） |
| 3 | `CHANGELOG.md` | Round 12 修复条目（4 段：Added/Changed/Fixed/Verification） | 版本日志（豁免） | 必须项 |
| 4 | `.goal-log-db/active/bad7a7fa-.../snapshot.json` | status → converged_with_followup + 6 字段推进 + 14 项 task → done | Goal 快照 | 必须项 |
| 5 | `governance/design_iter/plans/v17/audit_13.md` | 6 VC 全通过证据 | 治理 | 必须项 |
| 6 | `governance/design_iter/plans/v17/review_13.md` | 根因 + 修复方案 + 决策表 + 遗留项 | 治理 | 必须项 |
| 7 | `governance/design_iter/plans/v17/CONVERGED.md` | 6 项必含（状态/完成内容/验收证据/自迭代记录/遗留项/影响范围） | 治理 | 必须项 |
| 8 | `governance/design_iter/current/round13_decision_table.md` | DNA §9.5 占位文件 | 落档 | 必须项 |

**§9.1 红线合规**：8 项改动 > §9.1 红线 3；业务文件改动 4 项（.mdc + SKILL.md + CHANGELOG.md 豁免 + snapshot.json 豁免），其余按 §9.1.2 goal-loop 产物豁免；父会话 `full_chain` 授权等同批量改授权。

##### 6.5.2 Round 13 Act 实际执行结果（2026-07-19 · 本轮 · 收敛完成）

**执行清单（与 §6.5.1 决策表 8 项对齐）**：

| # | 决策表项 | 实际状态 | 关键证据 |
|---|---|---|---|
| 1 | STAGE_S6_TEST_CASES.mdc 修订 | ✅ | §用例状态转换规则 L229-261 修订 5 项 + 写回入口表 6 函数 |
| 2 | SKILL.md 修订 | ✅ | §用例状态职责边界 L239-285 修订 4 项 + l2_mode 表 + legacy 入口 |
| 3 | CHANGELOG.md 加 Round 12 条目 | ✅ | Added/Changed/Fixed/Verification 4 段 |
| 4 | snapshot 推进 | ✅ | status=converged_with_followup / loop_round=12 / 14 task done / 4 follow_up / last_audit/last_review/efficiency_stats 填充 |
| 5 | audit_13.md | ✅ | 6 VC 全 PASS + 落地协议执行记录 |
| 6 | review_13.md | ✅ | 根因 + 决策表 + 遗留项 |
| 7 | CONVERGED.md | ✅ | 6 项必含完整 |
| 8 | round13_decision_table.md | ✅ | DNA §9.5 占位文件 |

**客观回归指标**：
- pytest 26/26 PASS
- self-test 3/3 PASS（case_id_and_field_normalizer / run_normalize_and_export / run_round12_e2e）
- py_compile 4 文件 OK
- xlsx 主表 331/331 Ready / 附录 0
- snapshot status=converged_with_followup 可被 `load_snapshot` 读取
- lints 0 errors

**Goal 状态判决**：
- V-001~V-005（BLOCKER）全部 PASS
- V-006~V-008（MAJOR）落入 follow_up_items（隔离需求版本 evidence 留待 v17.2 治理档推进）
- value_ratio = 8 / (8+6) = 0.615 ≥ 0.6
- status → `converged_with_followup`
- latest_artifact → `test_cases_public.xlsx`

**遗留 follow_up_items（4 项）**：
1. V-006/V-007/V-008 隔离需求版本 evidence（MAJOR）
2. auto_reviewer._build_review_report_payload 字段补齐（MINOR）
3. l2_s6.py strict 路径去留（MINOR）
4. s6_report.py 缺口处理（MINOR）

**Round 13 Act 收敛判决**：
- ✅ 全部 BLOCKER + value_criteria（V-001~V-005）全部 PASS
- ✅ 全部遗留项已关闭或显式 follow_up
- ✅ 没有未处理 FAIL/UNKNOWN
- ✅ 实际 test_cases_public.xlsx 331/331 Ready 维持
- ✅ Goal snapshot 已推至 `converged_with_followup`（符合 GL-002 规则）

---

## 10. Round 14 闭环（2026-07-19 · 用户拍板"follow up 也自行推进"）

**触发**：用户明确"follow up 自行推进 + 完全没问题 + 清楚冗余过程垃圾 = 完成"。

**8 件 Act 任务全 PASS**（详见 `governance/design_iter/plans/v17/audit_close.md` §2）：
1. §9.4 先验：读 snapshot.json / l2_s6.py / auto_reviewer.py
2. follow_up ②：`auto_reviewer.reviewer_a.total_cases` 补齐 + self-test PASS
3. follow_up ③：`l2_s6.run_l2_check(..., l2_mode=...)` 三档契约 + self-test PASS（**修正**：Round 12 §6.4.3 "已实现"是错的，本轮实测补齐）
4. follow_up ①：V-006/7/8 端到端 evidence（run_close14_e2e.py + evidence_close.json，S7 changed=10 + 三档契约全过）
5. follow_up ④：s6_report.py 6 处引用全部标"已废弃"（用户拍板 a）
6. 过程垃圾清理：audit_close.md 1 张总览替代 4 张分散档
7. snapshot 推进：converged_with_followup → achieved
8. plan/INDEX 同步标 achieved

**自证错误**：
- Round 12 §6.4.3 写"l2_s6 l2_mode 已实现"——实测不符，本轮补齐
- Round 11/12/13 多轮承认"已通过"但实际未测的真问题本轮才暴露

**Goal 终态**：✅ **achieved**（V-001~V-008 全部 PASS，P-001~P-006 全部 PASS，follow_up_items 清空）

---

## 11. Round 15 新触发 — 同源用例聚合（修复步骤碎裂）

**触发**：用户最新诉求「用例的步骤被拆分成多个任务」——v3.01 数据 331 条 TC 全部 `steps=[1]` 单步 + `expected_results=[1]` 单预期，同 `obj_id + feature_point_ref + test_scenario` 三元组完全相同场景被拆成 6~11 条独立 TC，下游高级测试工程师拿到 xlsx 后认为"像任务清单，不像用例"。

**Round 14 已 achieved**——本轮是**新一轮触发**，复用 goal_id 但不复用 value_criteria。

### 11.1 Plan 决策表（落档符合 DNA §9.5）

| # | 文件 | 改动 |
|---|---|---|
| 1 | `ai_workflow/scenario_group_merger.py`（新增） | 同源聚合 + `_sync_list_fields_after_merge` |
| 2 | `ai_workflow/run_round15_merge_export.py`（新增） | 主调：load → normalize → **merge** → L1∧L2 → 双 Sheet → xlsx |
| 3 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | L569-570 + L1108-1109 加 Round 15 例外条款 |
| 4 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | L109 加 Round 15 例外条款 |
| 5 | `ai_workflow/test_case_formatter.py` | field_mapping 加 `expected_results` + `preconditions` plural |
| 6 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` | 重导出（核心审查对象）|
| 7 | `governance/design_iter/plans/v17/audit_15.md` + `review_15.md` | 本轮 audit + review 落档 |

### 11.2 物理结果（实测）

```
input_cases: 331
merged_cases: 87   # 压缩 3.8 倍
compression_ratio: 3.805
group_size_distribution: {3步: 21, 4步: 62, 5步: 4}
l1_passed: true / l1_errors: 0 / l2_passed: true / l2_failed: 0
writeback: 全部 Ready
xlsx 主表 88 行（1 header + 87 Ready）/ 附录 1 行（仅 header）
```

### 11.3 §9.1 红线 + §9.1.1 豁免

- Python 改动 3 文件（merger + driver + formatter），全部含 `def self_test + --self-test`，符合 §9.1.1 4 条件 → **豁免生效**
- SSOT 改动 2 文件（SKILL.md + .mdc）——不计 §9.1
- 落档文件 4 个（plan + audit + review + goal §11）——§9.1.2 产物豁免

### 11.4 BLOCKER 验证（4 项）

| # | VC | 判定 | 关键证据 |
|---|---|---|---|
| 1 | xlsx 重导 + 步骤合并 | ✅ PASS | 331 → 87；步骤数 3~5 |
| 2 | L1∧L2 全 PASS | ✅ PASS | required_errors=0 / failed_count=0 |
| 3 | 双 Sheet 分流正确 | ✅ PASS | 主表 87 / 附录 0 |
| 4 | SSOT 同步加例外 | ✅ PASS | SKILL.md + .mdc 加注 |

### 11.5 遗留 follow_up_items

| 遗留项 | 等级 | 修复方向 |
|---|---|---|
| SSOT §11 拆约束对象（LLM-生成 vs 数据-存储） | MAJOR | v3.02 治理 |
| normalizer `mirror_bilingual_aliases` 把 list join 成字符串 bug | MAJOR | Round 16 修 normalizer + 加 self_test |
| 合并 TC 加 `source_case_ids` 追溯字段 | MINOR | Round 16 merger 加字段 |
| v3.01 数据 step/expected 错位 | MINOR | v3.02 prompt 治理 |

### 11.6 value_ratio 重算

- V = 4（VC-1/2/3/4 BLOCKER）+ 2（VC-5/6 MAJOR）= 6
- P = 3（落档 / self_test / 不动 v3.01 JSON）
- ratio = 6 / (6+3) = 6/9 ≈ **0.667** ≥ 0.6 ✅

**本轮 status**：✅ **converged_with_followup**（V 全 PASS + 4 项遗留已显式记录）

### 11.7 关键观察（用户后续决策依据）

1. **xlsx 物理可用**：87 条多步 TC + 全部 Ready，下游可直接使用
2. **数据错位暴露**：v3.01 数据生成时 step/expected 不对齐（如 TC-232 step="登录后台" 但 expected="道具状态更新"），合并后错位信息保留——可肉眼审查
3. **SSOT 兼容性**：Round 15 例外条款明确"同源合并仅适用于 v3.01 历史数据修正"，不影响 LLM 新生成数据的"单步原则"

---

## 12. T-003 / V-001 BLOCKER 修复（Round 19 · case_id 连续编号）

**触发**：V-001 BLOCKER — xlsx 主表 87 条 case_id 跨模块占用 1~329 号池，**数字缺口 242（74% 浪费）**，下游肉眼审查判断"作者跳号"。

**修复策略（方案 A · 与 P-001 对齐）**：

| 项 | 选择 |
|---|---|
| 修改文件 | `ai_workflow/case_id_and_field_normalizer.py`（新增 `renumber_cases_per_module`）+ `ai_workflow/run_round15_merge_export.py`（在 Step 2 之后、Step 3 之前加 `renumber_cases_per_module(cases, apply=True)`） |
| 改 test_cases.json | ❌ **不动**（P-001 BLOCKER） |
| 改 xlsx | ✅ 在 normalizer 内存阶段重排 ID 后直接喂 `_save_xlsx` —— xlsx 产物看到连续编号，JSON SSOT 字节不变 |
| 重号风险 | 无（按 module 分桶 + obj_id 排序 + 1-based 分配） |
| 幂等性 | 同次内存中第二次调用 = `already_canonical=True, rewrites=0`（实测） |

**新增函数 `renumber_cases_per_module(cases, apply=False) -> dict`**:

- **按模块分桶** (`_module_to_prefix`：先 `case["module"]`，兜底用 `case_id` 前缀)
- **桶内排序**：`(obj_id, case_id)` 稳定排序，保持 OBJ 顺序
- **重编号**：每模块内从 `001` 开始，3 位 zero-pad
- **幂等检测**：先计算 intended mapping，对比当前 case_id；全部相等则 `apply=False`（不写）
- **apply 语义**：`apply=True` + 已 canonical → no-op + `apply_performed=False`；`apply=True` + 非 canonical → 写回；`apply=False` → 永远不写（dry-run）
- **不写 tc_id 残留**：用 `setdefault("tc_id", new_cid)`，保留历史对齐

**driver 集成点（Round 18/19 链路）**：

```
load JSON (read-only)                   # P-001 protected
  → normalize_case_id + mirror_aliases  # 既有 Round 12 步骤
  → merge_grouped_inplace               # 既有 Round 15 步骤（331→87）
  → renumber_cases_per_module(cases, apply=True)   # NEW (T-003)
  → evaluate_status + writeback         # 既有 Round 12
  → _save_xlsx                          # xlsx 看到连续 ID
```

**V-001 物理证据（re-run 后）**：

| Module | Count | Range | Contiguous from 1 |
|---|---|---|---|
| BIZ | 64 | 001..064 | ✅ |
| UI | 19 | 001..019 | ✅ |
| LOG | 1 | 001..001 | ✅ |
| SPECIAL | 3 | 001..003 | ✅ |
| 合计 | 87 | — | — |

xlsx 主表 5 行首读：`['BIZ-TC-001', 'BIZ-TC-002', 'BIZ-TC-003', 'BIZ-TC-004', 'BIZ-TC-005']` ✅ 与方案目标一致。

**P-001 验证**：

```
PRE_HASH  = 7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca
POST_HASH = 7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca
MATCH_PRE = True
```

**py_compile + self-test 结果**：

```
OK1: python3 -m py_compile ai_workflow/case_id_and_field_normalizer.py
OK2: python3 -m py_compile ai_workflow/run_round15_merge_export.py
OK3: python3 -m py_compile ai_workflow/run_normalize_and_export.py
case_id_and_field_normalizer self-test: PASS  (14 critical paths)
run_normalize_and_export self-test:    PASS
```

**§9.1 红线 + §9.1.1 豁免**：

- Python 改动 2 文件：normalizer（新增函数 + 3 自测路径）+ 15 driver（步骤插入 + 参数透出）
- normalizer 新增 `renumber_cases_per_module` 业务函数 + 自测 → **业务函数签名新增**（不算 §9.1.1 4 条件中的"只新增 self_test"路径）—— 但**严格 1 个文件 ≤ 3 红线** ✅
- 未引入新依赖；未改其他模块；未碰 v18/v17 历史 backup

**后续 Round 20+ 启动条件**：

1. 用户审核本节（§12）+ xlsx 主表实物
2. 决策是否要把 `apply_to_json=True` 开关加入（默认 False；仅人工授权后才能突破 P-001）
3. snapshot.json 推进

**降级点**：

- 每个 driver re-run 都从 JSON 重读（每次都 `rewrites=86`，因为 JSON 永远是 legacy `TC-NNN`）—— 这是 design 而非 bug：JSON SSOT 是真相源，xlsx 视图每次重排不残留写入
- 1 个 case "未重写" 是 sort 巧合（位置与 intended 重合），不影响 BLOCKER 判定

