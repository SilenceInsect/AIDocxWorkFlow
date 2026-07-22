# Round 16 Review — 7 项 follow_up 根因复盘 + Round 17 修复方案

> **性质**：Goal-loop review（按 `aidocx-s1-5-clarification` 等 SKILL §3.3 三段式模板）
> **Goal**: 32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3（GL-009 · test case 审查治理）
> **复盘轮次**: Round 16（loop_round=6 · Round 4 Act 第 3 轮）
> **复盘人**: 架构师 worker
> **复盘时间**: 2026-07-19
> **来源**: audit_16.md 7 项 MINOR follow_up（FU-1~FU-7）

---

## §1 缺陷汇总

### 1.1 数量与分级

| severity | 总数 | 本轮新发现 | 已修复 | 留 follow-up（Round 17） |
|---|---|---|---|---|
| BLOCKER | 0 | 0 | 0 | 0 |
| MAJOR | 0 | 0 | 0 | 0 |
| MINOR | 7（FU-1~FU-7） | 7 | 3（FU-3/6/7） | 4（FU-1/2/4/5） |
| **合计** | **7** | **7** | **3** | **4** |

### 1.2 FU-3 / FU-6 / FU-7 缺陷明细（本轮修复）

#### FU-3：out_of_scope 守卫规则散落

- **症状**：v3.01 byte-lock + v3.01 xlsx 字节不变 + v3.01 dict repr=0 不得回潮 3 条规则散落在 Round 11~15 各决策档（`audit_*.md` / `review_*.md` / `round1*_q_decision_table.md` / `goal_s6_case_status_redefinition.md §6.4.9`）
- **影响范围**：未来 Round 审查引用 SSOT 缺失；守卫检查命令散落无统一入口
- **影响深度**：MINOR（不影响 v3.01 byte-lock 实质守门；仅治理档 SSOT 缺失）
- **修复落地**：`governance/design_iter/current/out_of_scope.md` 新建 + 12 条守卫编号 G-001~G-012

#### FU-6：v3.01 目录 .bak 备份未清理

- **症状**：v3.01 S6 目录有 5 个 .bak / 临时文件（`test_cases.json.bak` 99167 / `test_cases_public.xlsx.round1.before.bak` 39818 / `test_cases_public.xlsx.round12.bak` 32516 / `test_cases_public.round12.precheck.bak.xlsx` 25250 / `.~test_cases_public.xlsx` 165）
- **影响范围**：v3.01 S6 目录臃肿（19 项 → 14 项）；未来 Round 找有效文件成本上升
- **影响深度**：MINOR（workflow_assets/ 整体 .gitignore，无 git 提交负担）
- **修复落地**：删除 5 个无用 .bak；保留 audit / transitions JSON（追溯价值）

#### FU-7：CONVERGED.md 主题不一致

- **症状**：原 CONVERGED.md 是 GL-002（`bad7a7fa-...`）Round 11~13 收敛档，与 GL-009（`32a8ff45-...`）Round 14+15+16 轨迹脱节
- **影响范围**：未来 Goal 收敛阅读混乱；Round 14/15/16 实际产物未在 CONVERGED.md 体现
- **影响深度**：MINOR（治理档类；不影响业务产物）
- **修复落地**：覆盖为 GL-009 Round 14 + 15 + 16 三轮轨迹完整版

### 1.3 FU-1 / FU-2 / FU-4 / FU-5 缺陷明细（延后 Round 17）

#### FU-1：v3.01 数据未迁移到 v3.02 schema

- **症状**：v3.01 386 TC × 缺 assertion 字段 × 含 fp_name 字段；Round 15 SSOT 修订已落地但 v3.01 数据未迁移
- **影响深度**：MINOR（v3.01 仍 Ready；QA 跑用例需人工翻译 expected_results）
- **延后理由**：工作量"大"（386 TC LLM 重推理 + 全套导出）；属"独立 v3.02 子项目"

#### FU-2：stage_gatekeeper / coverage_validator 未自动校验 assertion

- **症状**：Round 15 L1 加了 `check_assertion_completeness`，但 `stage_gatekeeper` / `coverage_validator` 未集成——手动跑 self-test 才生效
- **影响深度**：MINOR（production 跑 S6 时不会自动校验）
- **延后理由**：改 stage_gatekeeper 业务函数 → §9.1.1 豁免条件 3 临界

#### FU-4：l1_format_validator helpers 未接入 stage_gatekeeper 主流程

- **症状**：Round 15 helpers 只在 `--self-test` 模式触发；production 跑 S6 时不会自动校验
- **影响深度**：MINOR（与 FU-2 同源）
- **延后理由**：同 FU-2；与 FU-4 强相关，并入 Round 17 更顺

#### FU-5：open_questions.md 历史条目堆积

- **症状**：Q-V17-001~007（v17 字段溯源方案）+ Round 15 治理可能产生新 Q；未按"已解 / 未解 / 无主"分类
- **影响深度**：MINOR（治理档类）
- **延后理由**：涉及 governance/ 跨文件归档；工作量"中"；与 FU-1/2/4 主题关联弱

### 1.4 与上一轮缺陷的对比

| Round | 缺陷数（总数） | 修复数 | follow-up（延后） |
|---|---|---|---|
| Round 14 (loop_round=4) | 4（F-A/B/C/D） | 4 | 2（F-E/F-F） |
| Round 15 (loop_round=5) | 2（F-E/F-F） | 2 | 0 |
| Round 16 (loop_round=6) | 7（FU-1~7） | 3（FU-3/6/7） | 4（FU-1/2/4/5） |

---

## §2 根因分析（Root Cause）

### 2.1 FU-3 根因：治理档 SSOT 缺位（Governance SSOT Gap）

**机制层根因**：
- v3.01 byte-lock / xlsx 字节不变 / dict repr=0 规则属"反复重申的硬约束"，散落 Round 11~15 各审计档
- 缺乏独立治理档 SSOT（`governance/design_iter/current/out_of_scope.md`）做集中归档
- 未来 Round 审查引用规则时需跨多档搜索

**规格层根因**：
- `.goal-log-db/active/32a8ff45-.../out_of_scope.md` 是 Goal 级（3 类禁区），不重复 v3.01 byte-lock 规则细节
- governance/ 治理档与 Goal 级 out_of_scope 是**双轨关系**（前者管项目级守卫规则，后者管 Goal 级禁区）

**触发条件**：Round 15 终态 snapshot 写完 → 用户识别出 7 项 follow_up → FU-3 浮出

### 2.2 FU-6 根因：过程资产清理节奏缺位（Asset Cleanup Cadence Gap）

**机制层根因**：
- workflow_assets/ 整体 .gitignore → 过程资产无 git 提交负担 → 清理节奏无强制
- Round 1/2/12 多次备份生成 .bak，未定期清理
- 目录臃肿（19 项文件含 5 个备份）影响人工审查效率

**规格层根因**：
- DESIGN_AND_EXECUTION_STANDARDS.mdc §0.1 Git 分类规定 "workflow_assets/ = 单次需求过程资产区，整体不入 Git" → 清理规则未细化
- 缺乏"定期评估 .bak / 临时文件 → 归档 / 删除" SOP

**触发条件**：用户 7 项 follow_up 识别 → FU-6 浮出

### 2.3 FU-7 根因：CONVERGED.md 主题脱节（Documentation Drift）

**机制层根因**：
- CONVERGED.md 是"Goal 收敛档"，与 Goal 一一对应
- 当前 Goal (32a8ff45-...) 与上一 Goal (bad7a7fa-...) 共用 CONVERGED.md → 主题混淆
- GL-009 Round 14+15+16 轨迹未在 CONVERGED.md 体现

**规格层根因**：
- goal-loop SKILL.md 未明确规定"CONVERGED.md 与 Goal 一一对应"（默认上一 Goal 残留）
- 缺乏"Goal 切换时新建 CONVERGED.md_<goal_id>.md"约定

**触发条件**：用户 7 项 follow_up 识别 → FU-7 浮出

### 2.4 FU-1 根因：数据迁移与 SSOT 修订分离（Migration Lag）

**机制层根因**：
- Round 15 SSOT 修订（assertion + 删 fp_name）仅约束新数据生成
- v3.01 legacy 数据（386 TC × 缺 assertion × 含 fp_name）未迁移到新 schema
- v3.01 byte-lock 守 → 数据迁移必须走新建 v3.02 目录

**规格层根因**：
- §4.2.1 版本规则未细化"v3.0 → v3.01 数据迁移"路径
- 缺乏"v3.0 数据迁移触发条件 + 迁移 SOP"

**触发条件**：Round 15 已识别 → Round 16 用户跟进 → FU-1 浮出

### 2.5 FU-2 / FU-4 根因：pipeline 接入缺位（Pipeline Integration Gap）

**机制层根因**：
- L1 helpers (`check_assertion_completeness` / `check_no_fp_name_field`) 只在 `--self-test` 模式触发
- production 跑 S6 时 stage_gatekeeper / coverage_validator 不自动调 L1 helpers
- `gap_report` 输出段不展示 assertion 缺失统计

**规格层根因**：
- L1 校验器与 pipeline 集成的边界未明确（"self-test 触发 vs production 触发"）
- `--auto` argv 分支约定缺失

**触发条件**：Round 15 已识别 → Round 16 用户跟进 → FU-2/4 浮出

### 2.6 FU-5 根因：open_questions 治理缺位（Open Question Governance Gap）

**机制层根因**：
- `governance/open_questions.md` 历史条目堆积（Q-V17-001~007 + Round 15 治理 Q）
- 按"已解 / 未解 / 无主"分类未落实
- 已解 Q 未归档到 archive/，未解 Q 仍留 active

**规格层根因**：
- DESIGN_AND_EXECUTION_STANDARDS.mdc §5.2 is_assumed 标记规则与 open_questions 治理流程脱节
- 缺乏"open_questions 定期归档 SOP"

**触发条件**：用户 7 项 follow_up 识别 → FU-5 浮出

---

## §3 修复方案

### 3.1 本轮（Round 16）修复落地（3 件套）

| # | 落地项 | 文件 | 行数变化 |
|---|---|---|---|
| 1 | FU-3 守卫 SSOT 新建（12 条守卫编号 G-001~G-012） | `governance/design_iter/current/out_of_scope.md` | +200 行 |
| 2 | FU-6 v3.01 目录 5 个 .bak 删除 | `workflow_assets/.../v3.01/「S6 测试用例生成」/*.bak` × 5 | -196916 bytes |
| 3 | FU-7 CONVERGED.md 覆盖为 Round 16 收敛版 | `governance/design_iter/current/CONVERGED.md` | +280 行（覆盖） |

### 3.2 修复策略原则

| 原则 | 体现 |
|---|---|
| **小集合先做** | Round 16 仅做 FU-3 + FU-6 + FU-7（业务文件 0 < §9.1 红线 3） |
| **治理档双轨** | Goal 级 out_of_scope.md（禁区） + governance 级 out_of_scope.md（守卫规则）—— 不冲突 |
| **过程资产清理** | workflow_assets/ 整体 .gitignore → .bak 删除无 git 负担；保留 audit/transitions JSON（追溯价值） |
| **CONVERGED 一一对应** | 覆盖为本 Goal 完整轨迹；不另建 CONVERGED_GL-009.md（避免双档混淆） |
| **§9.5 落档协议** | `round16_q_decision_table.md` 先 Write 占位后 content 展开 |
| **out_of_scope 守** | v3.01 JSON 字节不变（338192 不变）；xlsx 字节不变（41572 不变） |

### 3.3 Round 17 修复方案（FU-1 / FU-2 / FU-4 / FU-5）

#### FU-1 修复方案（v3.02 数据迁移）

| 步骤 | 内容 |
|---|---|
| 1 | 新建 `workflow_assets/游戏道具商城系统/v3.02/「S6 测试用例生成」/` 目录 |
| 2 | Read v3.01 test_cases.json（338192 bytes） |
| 3 | LLM 推理 386 TC 的 assertion 字段（基于 expected_results 翻译） |
| 4 | 删除 fp_name 字段 |
| 5 | 写 v3.02 test_cases.json |
| 6 | 用 `ai_workflow/test_case_formatter.py` 重导出 .md + .xlsx |
| 7 | 验证 v3.02 行数 / 字段覆盖 / dict repr=0 |
| 8 | 验证 v3.01 字节级不变（G-001 / G-002 / G-003） |
| **§9.1.1 豁免** | 豁免条件 1/2/4 满足；条件 3 业务函数改动临界（重推理 helper）—— 走豁免 + 决策档明确论证 |
| **工作量** | 大（386 TC LLM 重推理 + 全套导出） |

#### FU-2 + FU-4 修复方案（pipeline 接入）

| 步骤 | 内容 |
|---|---|
| 1 | Read `ai_workflow/stage_gatekeeper.py`（必先 Read §9.4） |
| 2 | Read `ai_workflow/coverage_validator.py`（必先 Read §9.4） |
| 3 | S6 gate 段加 `check_assertion_completeness` 自动调用（FU-2） |
| 4 | `gap_report` 输出段加 assertion 缺失统计（FU-2） |
| 5 | S6 gate 段加 `run_all_l1_checks()` 调用（FU-4） |
| 6 | helpers 加 `--auto` argv 分支（FU-4） |
| 7 | L1 self-test 加 C23（stage_gatekeeper 集成） + C24（auto 模式接入） |
| **§9.1.1 豁免** | 豁免条件 1/2/4 满足；条件 3 stage_gatekeeper 业务函数改动临界 —— 走豁免 + 决策档明确论证 |
| **工作量** | 中 |

#### FU-5 修复方案（open_questions 归档）

| 步骤 | 内容 |
|---|---|
| 1 | Read `governance/open_questions.md`（如有迁移到 current/） |
| 2 | 按"已解 / 未解 / 无主"分类 |
| 3 | 已解的归档到 `governance/design_iter/archive/open_questions_resolved/` |
| 4 | 未解的留 active |
| 5 | 无主的标注需人工认领 |
| **§9.1.1 豁免** | 豁免条件 1/2/3/4 满足（governance/ 归档，非业务函数改动） |
| **工作量** | 中 |

---

## §4 新 follow_up_items（延后 Round 17）

| ID | 描述 | severity | 来源 | 状态 |
|---|---|---|---|---|
| **FU-1** | v3.02 数据迁移（新建目录 + 386 TC LLM 重推理 + 全套导出） | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 17 |
| **FU-2** | stage_gatekeeper / coverage_validator 集成 assertion 校验 + L1 self-test C23 | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 17 |
| **FU-4** | l1_format_validator helpers 加 `--auto` argv + L1 self-test C24 | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 17 |
| **FU-5** | open_questions.md 历史条目归档（Q-V17-001~007 + Round 15 治理 Q） | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 17 |

---

## §5 收敛判定

| 维度 | 值 | 判定 |
|---|---|---|
| `follow_up_count`（本轮新增） | 4（FU-1/2/4/5 延后 Round 17） | ✅ Round 16 本轮清 3 延后 4 |
| `status` | `converged_with_followup` | ✅ 目标达成（含延后 follow_up） |
| `loop_round` | 6 | ✅ Round 6 收敛 |
| `efficiency_stats.convergence_round` | 6 | ✅ Round 6 收敛 |
| `efficiency_stats.total_iterations` | 6 | ✅ 6 轮迭代 |
| `efficiency_stats.follow_up_count` | 4 | ✅ 4 项延后 Round 17 |
| `test_cases_json_bytes_unchanged` | true | ✅ 严守 out_of_scope |
| `test_cases_xlsx_bytes_unchanged` | true | ✅ 严守 out_of_scope |

---

> 本 review 档：`review_16.md`（loop_round=6）
> 配套 audit 档：`audit_16.md`
> 配套决策档：`governance/design_iter/current/round16_q_decision_table.md`
> 配套守卫 SSOT：`governance/design_iter/current/out_of_scope.md`
> 配套 CONVERGED：`governance/design_iter/current/CONVERGED.md`
> 配套 snapshot：`.goal-log-db/active/32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3/snapshot.json`（atomic write）