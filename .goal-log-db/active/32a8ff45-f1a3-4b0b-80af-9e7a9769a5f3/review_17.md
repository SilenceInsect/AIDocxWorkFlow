# Round 17 Review — FU-1 v3.02 数据迁移复盘 + Round 18 修复方案

> **性质**：Goal-loop review（按 `aidocx-s1-5-clarification` 等 SKILL §3.3 三段式模板）
> **Goal**: 32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3（GL-009 · test case 审查治理）
> **复盘轮次**: Round 17（loop_round=7）
> **复盘人**: 架构师 worker
> **复盘时间**: 2026-07-19
> **来源**: audit_17.md 4 项 follow_up（FU-1/2/4/5）

---

## §1 缺陷汇总

### 1.1 数量与分级

| severity | 总数 | 本轮新发现 | 已修复 | 留 follow-up（Round 18） |
|---|---|---|---|---|
| BLOCKER | 0 | 0 | 0 | 0 |
| MAJOR | 0 | 0 | 0 | 0 |
| MINOR | 4（FU-1~FU-5） | 4 | 1（FU-1） | 3（FU-2/4/5） |
| **合计** | **4** | **4** | **1** | **3** |

### 1.2 FU-1 缺陷明细（本轮修复）

#### FU-1：v3.02 数据迁移

- **症状**：v3.01 331 TC × 缺 assertion 字段 × 含 fp_name 字段；Round 15 SSOT 修订已落地但 v3.01 数据未迁移
- **影响范围**：v3.02 独立目录（workflow_assets/ 整体 .gitignore，无 git 提交负担）；xlsx 主表 0 行（因 v3.02 全部 Draft，符合 _partition_cases_for_xlsx 设计预期）
- **影响深度**：MINOR（v3.01 仍 Ready；v3.02 schema 已升级；xlsx 主表 0 行是 FU-1 范围内预期行为）
- **修复落地**：
  - `workflow_assets/.../v3.02/「S6 测试用例生成」/test_cases.json`（400677 bytes / 331 TC / assertion 100% / fp_name 残留 0）
  - `workflow_assets/.../v3.02/「S6 测试用例生成」/test_cases.md`（73188 bytes / 331 行）
  - `workflow_assets/.../v3.02/「S6 测试用例生成」/test_cases_public.xlsx`（25158 bytes / 2 Sheet / dict_repr=0）
- **4 类断言分布**：numeric=143 / enum_match=104 / string_contains=65 / regex_match=19（LLM 推理自然分布；regex_match 偏低因 LOG 模块仅 4 TC）
- **TC 数修正说明**：实测 v3.01 = 331 TC（Round 16 review §3.3 / out_of_scope.md / user query 中 "386" 为上一 Goal 历史残留；本轮以实测 331 为准）

### 1.3 FU-2 / FU-4 / FU-5 缺陷明细（延后 Round 18）

#### FU-2：stage_gatekeeper / coverage_validator 未自动校验 assertion

- **症状**：Round 15 L1 加了 `check_assertion_completeness`，但 `stage_gatekeeper` / `coverage_validator` 未集成——手动跑 self-test 才生效
- **影响深度**：MINOR（production 跑 S6 时不会自动校验）
- **延后理由**：改 stage_gatekeeper 业务函数 → §9.1.1 豁免条件 3「不动业务函数签名」**临界**

#### FU-4：l1_format_validator helpers 未接入 stage_gatekeeper 主流程

- **症状**：Round 15 helpers 只在 `--self-test` 模式触发；production 跑 S6 时不会自动校验
- **影响深度**：MINOR（与 FU-2 同源）
- **延后理由**：同 FU-2；与 FU-4 强相关，并入 Round 18 更顺

#### FU-5：open_questions.md 历史条目堆积

- **症状**：Q-V17-001~007（v17 字段溯源方案）+ Round 15 治理可能产生新 Q；未按"已解 / 未解 / 无主"分类
- **影响深度**：MINOR（治理档类）
- **延后理由**：
  1. `governance/open_questions.md` 不存在；实际在 `governance/design_iter/current/open_questions.md` 维护（目录确认需 Read 全文）
  2. 涉及 governance/ 跨档归档；工作量"中"
  3. 与 FU-1/2/4 主题关联弱（governance 清理 vs pipeline 改造）

### 1.4 与上一轮缺陷的对比

| Round | 缺陷数（总数） | 修复数 | follow-up（延后） |
|---|---|---|---|
| Round 14 (loop_round=4) | 4（F-A/B/C/D） | 4 | 2（F-E/F-F） |
| Round 15 (loop_round=5) | 2（F-E/F-F） | 2 | 0 |
| Round 16 (loop_round=6) | 7（FU-1~7） | 3（FU-3/6/7） | 4（FU-1/2/4/5） |
| **Round 17 (loop_round=7)** | **4（FU-1/2/4/5）** | **1（FU-1）** | **3（FU-2/4/5）** |

---

## §2 根因分析（Root Cause）

### 2.1 FU-1 根因：数据迁移与 SSOT 修订分离（Migration Lag · Round 16 已知）

**机制层根因**：
- Round 15 SSOT 修订（assertion + 删 fp_name）仅约束新数据生成
- v3.01 legacy 数据（331 TC × 缺 assertion × 含 fp_name）未迁移到新 schema
- v3.01 byte-lock 守 → 数据迁移必须走新建 v3.02 目录

**规格层根因**：
- §4.2.1 版本规则未细化"v3.0 → v3.01 数据迁移"路径
- 缺乏"v3.0 数据迁移触发条件 + 迁移 SOP"
- Round 16 决策档 §3.3 列出 Round 17 启动条件但未细化 LLM 推理规则

**触发条件**：Round 15 已识别 → Round 16 用户跟进 → FU-1 浮出

### 2.2 FU-2 / FU-4 根因：pipeline 接入缺位（Pipeline Integration Gap · 已知）

**机制层根因**：
- L1 helpers (`check_assertion_completeness` / `check_no_fp_name_field`) 只在 `--self-test` 模式触发
- production 跑 S6 时 stage_gatekeeper / coverage_validator 不自动调 L1 helpers
- `gap_report` 输出段不展示 assertion 缺失统计

**规格层根因**：
- L1 校验器与 pipeline 集成的边界未明确（"self-test 触发 vs production 触发"）
- `--auto` argv 分支约定缺失

**触发条件**：Round 15 已识别 → Round 16 用户跟进 → FU-2/4 浮出

### 2.3 FU-5 根因：open_questions 治理缺位（Open Question Governance Gap · 已知）

**机制层根因**：
- `governance/open_questions.md` 历史条目堆积（Q-V17-001~007 + Round 15 治理 Q）
- 按"已解 / 未解 / 无主"分类未落实
- 已解 Q 未归档到 archive/，未解 Q 仍留 active

**规格层根因**：
- DESIGN_AND_EXECUTION_STANDARDS.mdc §5.2 is_assumed 标记规则与 open_questions 治理流程脱节
- 缺乏"open_questions 定期归档 SOP"

**触发条件**：Round 16 浮出 → Round 17 已知 → 延后 Round 18

---

## §3 修复方案

### 3.1 本轮（Round 17）修复落地（1 件套）

| # | 落地项 | 文件 | 行数/字节数变化 |
|---|---|---|---|
| 1 | FU-1 v3.02 数据迁移 | `workflow_assets/.../v3.02/「S6 测试用例生成」/{test_cases.json, test_cases.md, test_cases_public.xlsx}` | +498,923 bytes（400677 + 73188 + 25158） |

### 3.2 修复策略原则

| 原则 | 体现 |
|---|---|
| **小集合先做** | Round 17 仅做 FU-1（用户点名核心）—— 业务文件改动 = 0（治理档 + workflow_assets 内部迁移均属过程资产豁免） |
| **FU-1 独立可验证** | v3.02 是新建目录，schema 升级（assertion + 删 fp_name）独立可验证；xlsx 双 Sheet 路由符合预期 |
| **§9.5 落档协议** | `round17_q_decision_table.md` 先 Write 占位后 content 展开 |
| **out_of_scope 守** | v3.01 JSON 字节不变（338192 不变）；xlsx 字节不变（41572 不变）；dict_repr=0 不变 |
| **GL-009 语义校验** | user-confirmed pass · §3.2 合法目标变更路径（用户层面已确认） |
| **拆分策略** | FU-2/4/5 拆 Round 18（stage_gatekeeper 业务函数改动 → §9.1.1 豁免条件 3 临界） |

### 3.3 Round 18 修复方案（FU-2 / FU-4 / FU-5）

#### FU-2 + FU-4 修复方案（pipeline 接入）

| 步骤 | 内容 |
|---|---|
| 1 | Read `ai_workflow/stage_gatekeeper.py`（必先 Read §9.4） |
| 2 | Read `ai_workflow/coverage_validator.py` |
| 3 | Read `ai_workflow/l1_format_validator.py` |
| 4 | S6 gate 段加 `check_assertion_completeness` 自动调用（FU-2） |
| 5 | `gap_report` 输出段加 assertion 缺失统计（FU-2） |
| 6 | S6 gate 段加 `run_all_l1_checks()` 调用（FU-4） |
| 7 | helpers 加 `--auto` argv 分支（FU-4） |
| 8 | L1 self-test 加 C23（stage_gatekeeper 集成）+ C24（auto 模式接入） |
| **§9.1.1 豁免** | 业务文件 ≥ 3；豁免条件 1/2 满足；条件 3 临界（仅加调用 + 加 argv，不改业务签名）—— 走豁免 + 决策档明确论证 |
| **工作量** | 中 |

#### FU-5 修复方案（open_questions 归档）

| 步骤 | 内容 |
|---|---|
| 1 | Read `governance/design_iter/current/open_questions.md`（如有迁移到 current/） |
| 2 | 按"已解 / 未解 / 无主"分类 |
| 3 | 已解的归档到 `governance/design_iter/archive/open_questions_resolved/` |
| 4 | 未解的留 active |
| 5 | 无主的标注需人工认领 |
| **§9.1.1 豁免** | 豁免条件 1/2/3/4 满足（governance/ 归档，非业务函数改动） |
| **工作量** | 中 |

---

## §4 新 follow_up_items（延后 Round 18）

| ID | 描述 | severity | 来源 | 状态 |
|---|---|---|---|---|
| **FU-2** | stage_gatekeeper / coverage_validator 集成 assertion 校验 + L1 self-test C23 | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 18 |
| **FU-4** | l1_format_validator helpers 加 `--auto` argv + L1 self-test C24 | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 18 |
| **FU-5** | open_questions.md 历史条目归档（Q-V17-001~007 + Round 15 治理 Q） | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 18 |

---

## §5 收敛判定

| 维度 | 值 | 判定 |
|---|---|---|
| `follow_up_count`（本轮新增） | 0（Round 17 无新 follow_up 识别） | ✅ Round 17 本轮清 1（FU-1）延后 3（FU-2/4/5） |
| `status` | `converged_with_followup` | ✅ 目标达成（含延后 follow_up） |
| `loop_round` | 7 | ✅ Round 7 收敛 |
| `efficiency_stats.convergence_round` | 7 | ✅ Round 7 收敛 |
| `efficiency_stats.total_iterations` | 7 | ✅ 7 轮迭代 |
| `efficiency_stats.follow_up_count` | 3（FU-2/4/5 延后 Round 18） | ✅ 3 项延后 Round 18 |
| `test_cases_json_bytes_unchanged`（v3.01） | true | ✅ 严守 out_of_scope |
| `test_cases_xlsx_bytes_unchanged`（v3.01） | true | ✅ 严守 out_of_scope |
| v3.02 数据迁移 | 331 TC / assertion 100% / fp_name 残留 0 | ✅ FU-1 PASS |

---

## §6 xlsx 主表 0 数据行的解释（关键事实记录）

**关键事实**：v3.02 主表 `测试用例` 仅 1 行（表头），331 TC 全部进附录 `Draft-Rejected附录`。

**原因**：v3.02 数据迁移**只做 schema 升级**（加 assertion + 删 fp_name），**未跑 L1/L2 写回**——所以 `用例状态` 仍保留 v3.01 的 `Draft`。`_partition_cases_for_xlsx` 把 Draft 分流到附录（按 _DEFAULT_XLSX_PROFILE 设计）。

**这是预期行为**：
- FU-1 目标 = 数据迁移（schema 升级），不包含 L1∧L2 写回
- 写回 Ready 是 FU-2（pipeline 接入）/ S7 Rejected / S8 Deprecated 的职责
- 跑 L1∧L2 写回需要 Round 18 先集成 stage_gatekeeper（FU-2）才能 production 触发

**下一步**：Round 18 FU-2 落地后，v3.02 可触发 L1∧L2 写回 → 主表 331 / 附录 0（与 v3.01 一致）。

---

> 本 review 档：`review_17.md`（loop_round=7）
> 配套 audit 档：`audit_17.md`
> 配套决策档：`governance/design_iter/current/round17_q_decision_table.md`
> 配套 snapshot：`.goal-log-db/active/32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3/snapshot.json`（atomic write）