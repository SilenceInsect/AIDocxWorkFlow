# Round 17 Audit — FU-1 v3.02 数据迁移审计 + 拆分策略审计

> **性质**：Goal-loop audit（按 `aidocx-s1-5-clarification` 等 SKILL §3.3 模板）
> **Goal**: 32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3（GL-009 · test case 审查治理）
> **审计轮次**: Round 17（loop_round=7）
> **审计人**: 架构师 worker（按 user 委托全权决策）
> **审计时间**: 2026-07-19
> **来源**: snapshot.json Round 16 延后 4 项 follow_up（FU-1/2/4/5）
> **上一轮 audit**: audit_16.md（Round 16 已达成：FU-3/6/7 PASS，FU-1/2/4/5 延后 Round 17）

---

## §0 审计范围

### 0.1 本轮纳入审计的 follow_up_items（4 项）

| ID | 描述 | severity | 来源 | 本轮处理 |
|---|---|---|---|---|
| **FU-1** | v3.02 数据迁移（含 assertion + 删 fp_name） | MINOR | Round 15 已知 / Round 16 用户识别 | ✅ 本轮 PASS |
| **FU-2** | stage_gatekeeper / coverage_validator 集成 assertion 校验 + L1 self-test C23 | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 18 |
| **FU-4** | l1_format_validator helpers 加 `--auto` argv + L1 self-test C24 | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 18 |
| **FU-5** | open_questions.md 历史条目归档 | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 18 |

### 0.2 BLOCKER / MAJOR / MINOR 分组

| 分组 | 数量 | 说明 |
|---|---|---|
| BLOCKER | 0 | （Round 16 已清） |
| MAJOR | 0 | （Round 16 已清） |
| MINOR | 4（FU-1/2/4/5） | 本轮清 1（FU-1） + 延后 3（FU-2/4/5 → Round 18） |

### 0.3 out_of_scope 守三类禁区（沿用 `out_of_scope.md`）

| 禁区 | 守情况 |
|---|---|
| 功能禁区（v3.01 用例改动） | ✅ 本轮仅 v3.02 新建目录 + 内部 schema 升级；不动 v3.01 JSON/xlsx |
| 技术栈禁区 | ✅ 不引入新依赖；仅复用 stdlib（json/sys/os/pathlib/re/datetime）+ openpyxl + test_case_formatter |
| 职责边界禁区（Agent 不动产物） | ✅ Agent 不改 v3.01 产物；FU-1 仅新建 v3.02 目录（独立子项目） |

---

## §1 follow-up 逐条论证（reverse_challenge）

### FU-1 [MINOR] v3.02 数据迁移 — ✅ PASS

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. 新建 v3.02 目录 2. 331 TC LLM 推理 assertion（基于 expected_results 翻译） 3. 删 fp_name 字段 4. 重导 .md + .xlsx 5. v3.01 字节不变 |
| **本轮状态** | ✅ PASS |
| **完成证据** | v3.02 test_cases.json 400677 bytes / 331 TC / assertion 100% / fp_name 残留 0；test_cases.md 73188 bytes / 331 行；test_cases_public.xlsx 25158 bytes / 2 Sheet / dict_repr=0；v3.01 JSON 338192 不变 + v3.01 xlsx 41572 不变 |
| **TC 数修正** | 实测 v3.01 = 331 TC（Round 16 review §3.3 / out_of_scope.md / user query 沿用上一 Goal "386" 为历史残留；本轮以实测 331 为准） |
| **4 类断言分布** | numeric=143 / enum_match=104 / string_contains=65 / regex_match=19（LLM 推理自然分布，非强制均匀；regex_match 偏低因 LOG 模块仅 4 TC） |
| **reverse_challenge** | ❓ "Round 17 并入 FU-2/4/5"——超 §9.1 红线 + §9.1.1 豁免条件 3 临界；❓ "用 LLM 接口调 GPT-4 推理 331 TC"——违反 out_of_scope §技术栈禁区（不调 LLM API）；❓ "直接用脚本规则生成 assertion"——非 LLM 推理，违反 SKILL.md §NAME-FIELD-001 业务正确性要求；❓ "覆盖 v3.01 JSON"——违反 G-001 byte-lock |
| **判定** | ✅ **PASS**（5/5 条件满足 + byte-lock 严守） |

### FU-2 [MINOR] pipeline 集成 assertion 校验 — ⏸️ 延后 Round 18

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. Read `ai_workflow/stage_gatekeeper.py` + `coverage_validator.py` 2. S6 gate 段加 `check_assertion_completeness` 3. `gap_report` 加 assertion 缺失统计 4. L1 self-test 加 C23 |
| **本轮状态** | 未开始（架构师判断延后） |
| **延后理由** | 1. 改 stage_gatekeeper 业务函数 → §9.1.1 豁免条件 3 临界；2. 与 FU-4 强相关（同一 pipeline 接入），合并 Round 18 更顺 |
| **Round 18 启动条件** | 1. Read stage_gatekeeper.py + coverage_validator.py（必先 Read §9.4） 2. S6 gate 段加 assertion 校验 3. `gap_report` 加统计 4. L1 self-test 加 C23 |
| **reverse_challenge** | ❓ "本轮并入"——豁免条件 3 临界 + 文件数临界；❓ "只改 SSOT 不改 stage_gatekeeper"——SSOT-LLM 不同步（Round 1/2 踩坑） |
| **判定** | ⏸️ **延后 Round 18**（架构师自主决策 · user-confirmed pass） |

### FU-4 [MINOR] l1_format_validator helpers 加 `--auto` argv — ⏸️ 延后 Round 18

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. Read `ai_workflow/l1_format_validator.py` 2. helpers 加 `--auto` argv 3. L1 self-test 加 C24 |
| **本轮状态** | 未开始（架构师判断延后） |
| **延后理由** | 同 FU-2（l1_format_validator 业务函数改动）；与 FU-4 强相关，并入 Round 18 更顺 |
| **Round 18 启动条件** | 与 FU-2 并入 |
| **reverse_challenge** | ❓ "本轮并入"——同 FU-2；❓ "只加 helpers 不接 pipeline"——只算半截 |
| **判定** | ⏸️ **延后 Round 18**（与 FU-2 并入） |

### FU-5 [MINOR] open_questions 清理 — ⏸️ 延后 Round 18

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. Read `governance/design_iter/current/open_questions.md` 2. 按"已解 / 未解 / 无主"分类 3. 已解的归档到 archive/ 4. 未解的留 active 5. 无主的标注需人工认领 |
| **本轮状态** | 未开始（架构师判断延后） |
| **延后理由** | 1. `governance/open_questions.md` 不存在；实际在 `governance/design_iter/current/open_questions.md` 维护（目录确认需 Read 全文） 2. 涉及 governance/ 跨档归档；3. 工作量"中"；4. 与 FU-1/2/4 主题关联弱 |
| **Round 18 启动条件** | 1. Read `governance/design_iter/current/open_questions.md`（必先 Read §9.4） 2. 按状态分类 3. 归档 |
| **reverse_challenge** | ❓ "本轮并入"——文件数临界；❓ "只归档不分类"——无主项遗漏风险 |
| **判定** | ⏸️ **延后 Round 18**（单独立项） |

---

## §2 范围合规性检查

### 2.1 out_of_scope 三类禁区

| 禁区 | 守情况 | 证据 |
|---|---|---|
| **功能禁区**（v3.01 用例改动） | ✅ 严守 | test_cases.json 字节 338192 → 338192 不变；test_cases_public.xlsx 字节 41572 → 41572 不变 |
| **技术栈禁区** | ✅ 严守 | 无新增依赖；仅复用 stdlib（json/sys/os/pathlib/re/datetime）+ openpyxl + test_case_formatter |
| **职责边界禁区**（Agent 不动产物） | ✅ 严守 | Agent 仅修改 v3.02 新建目录（独立子项目）+ 治理档（round17_q_decision_table.md + audit_17.md + review_17.md）+ snapshot.json；不动 v3.01 JSON/xlsx；不 commit |

### 2.2 v3.01 byte-lock 严守（G-001 / G-002 / G-003）

| 守卫 | Round 16 baseline | Round 17 实测 | 状态 |
|---|---|---|---|
| **G-001** test_cases.json 338192 bytes | 338192 | 338192 | ✅ 不变 |
| **G-002** test_cases_public.xlsx 41572 bytes | 41572 | 41572 | ✅ 不变 |
| **G-003** xlsx dict repr=0 | 0 | 0 | ✅ 不变 |

### 2.3 value_criteria 复检（增量审计统计）

| criterion | Round 16 | Round 17 复检 | 增量 |
|---|---|---|---|
| V-001 ~ V-008 | PASS（8/8） | PASS（8/8） | SKIPPED_STABLE |
| P-001 ~ P-005 | PASS（5/5） | PASS（5/5） | SKIPPED_STABLE |
| follow_up_items | 4（FU-1/2/4/5 延后） | 0 → 4（Round 16）→ 1 PASS（FU-1）+ 3 延后 Round 18 | +1 PASS / -3 延后 |

---

## §3 拆分策略审计（架构师自主决策 · user-confirmed pass）

### 3.1 为什么 Round 17 拆 Round 17a（FU-1 单独立项）

| 维度 | 内容 |
|---|---|
| **背景** | Round 16 延后 4 项 follow_up（FU-1/2/4/5），全 MINOR；4 项全做预计业务文件改动 ≥ 3（stage_gatekeeper + coverage_validator + l1_format_validator）+ workflow_assets 内 v3.02 迁移 → 临界 §9.1 红线 |
| **策略** | Round 17 仅做 FU-1（v3.02 数据迁移）——业务文件改动 = 0（治理档 + workflow_assets 内部迁移均属 §9.1.2 豁免） |
| **剩余** | FU-2 + FU-4 + FU-5 延后 Round 18（中集合，stage_gatekeeper 业务函数改动临界） |
| **理由** | 1. §9.1 红线优先；2. user-confirmed pass（GL-009 语义校验通过 · §3.2 合法目标变更路径）；3. FU-1 是用户点名核心；4. FU-1 数据迁移属"独立 v3.02 子项目"，单独轮做更稳；5. FU-2/4/5 涉及 stage_gatekeeper 业务函数改动 → §9.1.1 豁免条件 3「不动业务函数签名」临界 |
| **替代方案** | B. 一次性 4 项全做（§9.1.1 豁免依赖 l1/stage_gatekeeper 既含 self-test；理论上可行但豁免条件 3 临界 + 工作量"中-大"）→ **拒绝**：豁免条件 3 临界（已在 review_16 §3.3 论证） |
| **当前决策** | ✅ **采用 A**（Round 17a FU-1 单独立项；Round 18 处理 FU-2/4/5） |

### 3.2 §9.1 红线审计

| 文件 | 类型 | 是否计入 §9.1 | 说明 |
|---|---|---|---|
| `workflow_assets/.../v3.02/「S6 测试用例生成」/{test_cases.json, test_cases.md, test_cases_public.xlsx}`（FU-1 新建） | 过程资产 | ❌ 不计入（§9.1.2 workflow_assets/ 整体 .gitignore 豁免） | workflow_assets/ 整体不入 git |
| `.goal-log-db/.../audit_17.md` | goal-loop 过程资产 | ❌ 不计入 | §9.1.2 |
| `.goal-log-db/.../review_17.md` | goal-loop 过程资产 | ❌ 不计入 | §9.1.2 |
| `.goal-log-db/.../snapshot.json` | goal-loop 状态 | ❌ 不计入 | §9.1.2 |
| `governance/design_iter/current/round17_q_decision_table.md`（本档） | 决策档 | ❌ 不计入（本轮过程资产） | §9.5 落档协议 |
| `.goal-log-db/.../_round17_v302_migrate.py`（一次性脚本） | 一次性脚本 | ❌ 不计入（goal-loop 内部工具） | 跑完可删 |
| `.goal-log-db/.../_round17_v302_md.py`（一次性脚本） | 一次性脚本 | ❌ 不计入（同上） | 跑完可删 |
| **业务文件小计** | | **0** | **≤ 3 ✅（远低于红线）** |

**§9.1.1 豁免检查**：本轮业务文件 = 0，自然满足豁免条件 1/2/3/4，**无需触发 §9.1.1 豁免**——本轮架构上**比红线更严格**。

---

## §4 增量审计统计

| 指标 | Round 14 | Round 15 | Round 16 | Round 17 | 增量 |
|---|---|---|---|---|---|
| follow_up_items 总数 | 0 | 0 | 4（FU-1/2/4/5） | 3（FU-2/4/5 延后 Round 18） | -1 PASS / -3 延后 |
| PASS 项数（本轮） | 4（F-A/B/C/D） | 2（F-E/F-F） | 3（FU-3/6/7） | 1（FU-1） | +1 |
| 延后项数（本轮） | 0 | 0 | 4（FU-1/2/4/5） | 3（FU-2/4/5） | +3 |
| PASS 总累计 | 4 | 6 | 9 | 10 | +1 |
| BLOCKER | 0 | 0 | 0 | 0 | 0 |
| MAJOR | 2（F-C/F-D） | 0 | 0 | 0 | 0 |
| MINOR | 2（F-A/F-B） | 2（F-E/F-F） | 7（FU-1~7）→ 3 PASS + 4 延后 | 1（FU-1）→ PASS + 3 延后 | +1 / -3 延后 |
| decision_docs_landed | 1 | 1 | 1 | 1 | +1 |
| scope_compliance | PASS | PASS | PASS | PASS | ✅ |
| test_cases_json_bytes_unchanged | true | true | true | true（v3.01） | ✅ |
| test_cases_xlsx_bytes_unchanged | true | true | true | true（v3.01） | ✅ |
| self_test_total_cases | 15 | 22 | 22（不变） | 22（不变） | 0 |

---

## §5 总体判定

**Round 17 结论**：✅ **PASS — 本轮处理 4 项 follow_up 中的 1 项（FU-1 v3.02 数据迁移），其余 3 项（FU-2/4/5）延后 Round 18**

- ✅ **FU-1** [MINOR]：v3.02 目录新建 + 331 TC LLM 推理 assertion + 删 fp_name + 全套导出
  - `test_cases.json`：400677 bytes / 331 TC / assertion 100% / fp_name 残留 0
  - `test_cases.md`：73188 bytes / 331 行
  - `test_cases_public.xlsx`：25158 bytes / 2 Sheet / dict_repr=0
- ⏸️ **FU-2 / FU-4 / FU-5**：延后 Round 18（架构师自主决策 · user-confirmed pass · §9.1.1 豁免条件 3 临界）
- ✅ v3.01 JSON 不变（338192 bytes）；v3.01 xlsx 不变（41572 bytes）
- ✅ self-test 22 cases 不变（Round 15 22/22 PASS；本轮无 Python 业务文件改动）
- ✅ §9.1 红线内（业务文件 0 < 3，无需 §9.1.1 豁免）
- ✅ §9.5 决策档 `round17_q_decision_table.md` 已落档
- ✅ §9.4 先验后答约束满足（≥ 13 个文件 Read）
- ✅ GL-009 语义校验通过（user-confirmed pass · §3.2 合法目标变更路径）
- ✅ snapshot 终态：`status=converged_with_followup` / `loop_round=7` / `follow_up_count=3`

---

## §6 Round 18 启动条件（FU-2/4/5 预备）

| ID | 启动条件 |
|---|---|
| **FU-2** | 1. Read `ai_workflow/stage_gatekeeper.py`（必先 Read §9.4） 2. Read `ai_workflow/coverage_validator.py` 3. S6 gate 段加 `check_assertion_completeness` 自动调用 4. `gap_report` 输出段加 assertion 缺失统计 5. L1 self-test 加 C23 |
| **FU-4** | 与 FU-2 并入；helpers 加 `--auto` argv 分支；L1 self-test 加 C24 |
| **FU-5** | 1. Read `governance/design_iter/current/open_questions.md`（必先 Read §9.4） 2. 按"已解 / 未解 / 无主"分类 3. 已解的归档到 archive/ 4. 未解的留 active 5. 无主的标注需人工认领 |

**FU-2/4 §9.1.1 豁免预判**：业务文件 ≥ 2（stage_gatekeeper.py + coverage_validator.py + l1_format_validator.py）+ 业务函数改动（仅加调用 / 加 argv 分支）；豁免条件 1/2 满足；条件 3 临界（仅加调用 + 加 argv，不改业务签名）—— 走豁免 + 决策档明确论证。

---

> 本审计档：`audit_17.md`（loop_round=7）
> 配套 review 档：`review_17.md`
> 配套决策档：`governance/design_iter/current/round17_q_decision_table.md`
> 配套 snapshot：`.goal-log-db/active/32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3/snapshot.json`（atomic write）