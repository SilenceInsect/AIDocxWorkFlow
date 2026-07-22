# Round 16 Audit — 7 项 follow_up 审计 + 拆分策略审计

> **性质**：Goal-loop audit（按 `aidocx-s1-5-clarification` 等 SKILL §3.3 模板）
> **Goal**: 32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3（GL-009 · test case 审查治理）
> **审计轮次**: Round 16（loop_round=6 · Round 4 Act 第 3 轮）
> **审计人**: 架构师 worker（按 user 委托全权决策）
> **审计时间**: 2026-07-19
> **来源**: 用户识别 7 项边界问题 follow_up（FU-1~FU-7，全部 MINOR）
> **上一轮 audit**: audit_15.md（Round 15 已达成，F-E/F-F PASS）

---

## §0 审计范围

### 0.1 本轮纳入审计的 follow_up_items（7 项）

| ID | 描述 | severity | 来源 | 本轮处理 |
|---|---|---|---|---|
| **FU-1** | v3.02 数据迁移（含 assertion + 删 fp_name） | MINOR | Round 15 已知 / Round 16 用户识别 | ⏸️ 延后 Round 17 |
| **FU-2** | stage_gatekeeper / coverage_validator 集成 assertion 校验 | MINOR | Round 15 已知 / Round 16 用户识别 | ⏸️ 延后 Round 17 |
| **FU-3** | out_of_scope.md 整理（v3.01 守卫规则集中归档） | MINOR | Round 16 用户识别 | ✅ 本轮 PASS |
| **FU-4** | L1 校验器接入 stage_gatekeeper 主流程（--auto argv） | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 17 |
| **FU-5** | Open Questions 清理（Q-V17-001~007 + Round 15 治理 Q） | MINOR | Round 16 用户识别 | ⏸️ 延后 Round 17 |
| **FU-6** | .bak 文件清理（v3.01 目录 5 个备份） | MINOR | Round 16 用户识别 | ✅ 本轮 PASS |
| **FU-7** | CONVERGED.md 收尾（Round 16 收敛版） | MINOR | Round 16 用户识别 | ✅ 本轮 PASS |

### 0.2 BLOCKER / MAJOR / MINOR 分组

| 分组 | 数量 | 说明 |
|---|---|---|
| BLOCKER | 0 | （用户识别 7 项全 MINOR） |
| MAJOR | 0 | （用户识别 7 项全 MINOR） |
| MINOR | 7 | FU-1~FU-7（本轮清 3 + 延后 4） |

### 0.3 out_of_scope 守三类禁区（沿用 `out_of_scope.md`）

| 禁区 | 守情况 |
|---|---|
| 功能禁区（v3.01 用例改动） | ✅ 本轮仅治理档 + workflow_assets 内部 .bak 清理；不动 v3.01 JSON/xlsx |
| 技术栈禁区 | ✅ 不引入新依赖 |
| 职责边界禁区（Agent 不动产物） | ✅ Agent 不改 v3.01 产物；FU-6 仅删 .bak 备份（非产物本身） |

---

## §1 follow-up 逐条论证（reverse_challenge）

### FU-1 [MINOR] v3.02 数据迁移 — ⏸️ 延后 Round 17

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. 新建 v3.02 目录 2. LLM 推理 386 TC assertion 3. 删除 fp_name 4. 重导出 .md + .xlsx 5. v3.01 字节不变 |
| **本轮状态** | 未开始（架构师判断延后） |
| **延后理由** | 1. 工作量"大"（386 TC LLM 重推理 + 全套导出）；2. 属"独立 v3.02 子项目"，单独轮做更稳；3. 7 项硬塞违反 Goal-loop 节奏（Round 14/15 模式：每轮 2-4 follow-up） |
| **Round 17 启动条件** | 1. Read v3.01 test_cases.json（必先 Read §9.4）；2. 用 `ai_workflow/test_case_formatter.py` 重导出；3. 验证 v3.02 行数 / 字段覆盖 / dict repr=0；4. 验证 v3.01 字节不变 |
| **reverse_challenge** | ❓ "Round 16 并入"——超 §9.1 红线（业务文件 ≥ 4），需 §9.1.1 豁免（条件 3 临界）；❓ "用 §NAME-FIELD-001 规则直接删 fp_name"——v3.01 实际数据保留 fp_name 兼容 legacy；新数据可走 v3.02 |
| **判定** | ⏸️ **延后 Round 17**（架构师自主决策；用户允许） |

### FU-2 [MINOR] pipeline 同步支持 assertion 校验 — ⏸️ 延后 Round 17

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. Read `ai_workflow/stage_gatekeeper.py`（必先 Read §9.4）2. S6 gate 段加 `check_assertion_completeness` 自动调用 3. `gap_report` 输出段加 assertion 缺失统计 4. L1 self-test 加 C23 |
| **本轮状态** | 未开始（架构师判断延后） |
| **延后理由** | 1. 改 stage_gatekeeper 业务函数 → §9.1.1 豁免条件 3「不动业务函数签名」**临界**；2. 工作量"中"；3. 与 FU-4 强相关（同一 pipeline 接入），并入 Round 17 更顺 |
| **Round 17 启动条件** | 1. Read stage_gatekeeper.py + coverage_validator.py；2. 在 S6 gate 段加 `check_assertion_completeness`；3. `gap_report` 加 assertion 缺失统计；4. L1 self-test 加 C23 |
| **reverse_challenge** | ❓ "Round 16 并入"——豁免条件 3 临界 + 文件数临界（8 > 6）；❓ "只改 SSOT 不改 stage_gatekeeper"——SSOT-LLM 不同步（Round 1/2 已踩坑） |
| **判定** | ⏸️ **延后 Round 17**（与 FU-4 并入） |

### FU-3 [MINOR] out_of_scope.md 整理 — ✅ PASS

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. 新建 `governance/design_iter/current/out_of_scope.md` 2. 集中 3 条 v3.01 守卫规则（G-001/002/003） 3. 预留 G-004~G-012 给 Round 17 4. 引用 RD16 §3 |
| **本轮状态** | ✅ PASS |
| **完成证据** | `governance/design_iter/current/out_of_scope.md` 新建（≤ 200 行）· 含 12 条守卫编号 G-001~G-012 · §3 引用 RD16 §3 |
| **reverse_challenge** | ❓ "只改 round16_q_decision_table.md 不单独建档"——散落问题未根治；❓ "合并到 GL-002 的 out_of_scope"——双 Goal 引用易混淆；❓ "覆盖现有 out_of_scope"——`.goal-log-db/.../out_of_scope.md` 是 Goal 级，本档是 governance/ 治理级，**双轨合理** |
| **判定** | ✅ **PASS**（4/4 条件满足） |

### FU-4 [MINOR] L1 校验器接入 stage_gatekeeper — ⏸️ 延后 Round 17

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. Read `ai_workflow/stage_gatekeeper.py`（必先 Read §9.4） 2. S6 gate 段加 `run_all_l1_checks()` 调用 3. helpers 加 `--auto` argv 4. L1 self-test 加 C24 |
| **本轮状态** | 未开始（架构师判断延后） |
| **延后理由** | 同 FU-2（stage_gatekeeper 业务函数改动临界） |
| **Round 17 启动条件** | 与 FU-2 并入（同一 pipeline 接入） |
| **reverse_challenge** | ❓ "Round 16 并入"——同 FU-2；❓ "只加 helpers 不接 pipeline"——只算半截；❓ "只接 production 不加 --auto"——argv 分支缺失 |
| **判定** | ⏸️ **延后 Round 17**（与 FU-2 并入） |

### FU-5 [MINOR] Open Question 清理 — ⏸️ 延后 Round 17

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. Read `governance/open_questions.md` 2. 按"已解 / 未解 / 无主"分类 3. 已解的归档到 archive/ 4. 未解的留 active 5. 无主的标注需人工认领 |
| **本轮状态** | 未开始（架构师判断延后） |
| **延后理由** | 1. 涉及 governance/ 跨文件归档；2. 工作量"中"；3. 与 FU-1/2/4 主题关联弱（governance 清理 vs pipeline 改造） |
| **Round 17 启动条件** | 1. Read `governance/open_questions.md` + `governance/design_iter/current/open_questions.md`；2. 按状态分类；3. 归档 |
| **reverse_challenge** | ❓ "Round 16 并入"——文件数临界；❓ "只归档不分类"——无主项遗漏风险 |
| **判定** | ⏸️ **延后 Round 17**（单独立项） |

### FU-6 [MINOR] .bak 文件清理 — ✅ PASS

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. Read v3.01 目录（必先 Read §9.4） 2. 评估每个 .bak 归属 3. 删无用 .bak 4. 移有价值的到 archive/ |
| **本轮状态** | ✅ PASS |
| **完成证据** | 5 个 .bak 删除（`test_cases_public.round12.precheck.bak.xlsx` + `test_cases_public.xlsx.round1.before.bak` + `test_cases_public.xlsx.round12.bak` + `test_cases.json.bak` + `.~test_cases_public.xlsx`）· 保留 `test_cases_round12_e2e_audit.json`（1168 bytes）+ `test_cases_round12_transitions.json`（29009 bytes）· v3.01 byte-lock 严守（338192 / 41572） |
| **评估规则** | 1. workflow_assets/ 整体 .gitignore → 过程资产可删（默认）；2. 有历史归档价值的（Round 12 e2e_audit / transitions）→ 保留；3. Excel/JSON 临时备份 → 删 |
| **reverse_challenge** | ❓ "全部移到 archive/"——过度保护；过程资产无须如此归档；❓ "全部保留"——目录臃肿，未来 Round 找有效文件成本上升；❓ "只删 .bak.xlsx 不删 .bak JSON"——`.bak` JSON 是 Round 1 备份（v3.01 JSON 未变更，无保留价值） |
| **判定** | ✅ **PASS**（5/5 评估规则满足） |

### FU-7 [MINOR] CONVERGED.md 收尾 — ✅ PASS

| 维度 | 内容 |
|---|---|
| **Pass 条件** | 1. Read 现有 CONVERGED.md（如存在） 2. 改写为 Round 16 收敛版（含 Round 14 + 15 + 16 三轮轨迹） 3. 标记当前 goal 真正 converged |
| **本轮状态** | ✅ PASS |
| **完成证据** | `governance/design_iter/current/CONVERGED.md` 覆盖（≤ 280 行）· 含 Round 14 + 15 + 16 三轮轨迹 · 标记 GL-009 converged_with_followup · 含 FU-1/2/4/5 Round 17 延后清单 · 含守卫检查清单（G-001~G-012） |
| **reverse_challenge** | ❓ "另建 CONVERGED_GL-009.md"——双 CONVERGED.md 易混淆；❓ "只追加 Round 16 段不动原文"——GL-002 旧 CONVERGED.md 内容与 GL-009 主题不一致；❓ "Round 17 完成后再写"——FU-7 是 Round 16 边界收尾，必须本轮完成 |
| **判定** | ✅ **PASS**（3/3 条件满足） |

---

## §2 范围合规性检查

### 2.1 out_of_scope 三类禁区

| 禁区 | 守情况 | 证据 |
|---|---|---|
| **功能禁区**（v3.01 用例改动） | ✅ 严守 | test_cases.json 字节 338192 → 338192 不变；test_cases_public.xlsx 字节 41572 → 41572 不变 |
| **技术栈禁区** | ✅ 严守 | 无新增依赖；仅复用 stdlib（json/sys/os/pathlib/shutil）+ 删除文件用 shell `rm` |
| **职责边界禁区**（Agent 不动产物） | ✅ 严守 | Agent 仅修改 3 个治理档（round16_q_decision_table.md + out_of_scope.md + CONVERGED.md）+ 删除 5 个 .bak 备份 + 1 个 Excel 临时 lock 文件；不动 v3.01 JSON/xlsx；不 commit |

### 2.2 Round 14 / Round 15 已达成项的稳定性（SKIPPED_STABLE）

| Round | follow-up | status 上一轮 | Round 16 复检 | 处理 |
|---|---|---|---|---|
| Round 14 | F-A | PASS | SKIPPED_STABLE（tc_tp_gap_report 仍能跑） | 跳过审计（不再变） |
| Round 14 | F-B | PASS | SKIPPED_STABLE（qa_fixer_v301 self-test 仍 PASS） | 跳过审计 |
| Round 14 | F-C | PASS | SKIPPED_STABLE（tp_id == s5_ref 一致性仍 100%） | 跳过审计 |
| Round 14 | F-D | PASS | SKIPPED_STABLE（check_tc_id_field_absence 已含） | 跳过审计 |
| Round 15 | F-E | PASS | SKIPPED_STABLE（check_assertion_completeness 22/22 PASS） | 跳过审计 |
| Round 15 | F-F | PASS | SKIPPED_STABLE（check_no_fp_name_field 22/22 PASS） | 跳过审计 |

### 2.3 value_criteria 复检（增量审计统计）

| criterion | Round 15 | Round 16 复检 | 增量 |
|---|---|---|---|
| V-001 ~ V-008 | PASS（8/8） | PASS（8/8） | SKIPPED_STABLE |
| P-001 ~ P-005 | PASS（5/5） | PASS（5/5） | SKIPPED_STABLE |
| follow_up_items | 0（Round 15 全清） | 0 → 7（用户识别）→ 3 PASS + 4 延后 Round 17 | +7 识别 / -3 PASS / -4 延后 |

---

## §3 拆分策略审计（架构师自主决策 · 用户允许）

### 3.1 为什么 Round 16 拆 Round 16a + 16b（小集合先做）

| 维度 | 内容 |
|---|---|
| **背景** | 用户识别 7 项 follow_up（FU-1~FU-7），全部 MINOR；7 项全做预计业务文件改动 ≥ 5 个 → 超 §9.1 红线（3 文件） |
| **策略** | Round 16 仅做"小集合"（FU-3 + FU-6 + FU-7）—— 业务文件改动 = 0（治理档 + workflow_assets 内部清理均属过程资产 / 治理档豁免） |
| **剩余** | FU-1 + FU-2 + FU-4 + FU-5 延后 Round 17（中集合，预计业务文件改动 ≥ 4 个；走 §9.1.1 豁免或拆 Round 17a/17b） |
| **理由** | 1. §9.1 红线优先；2. 用户允许"架构师自主判断——按'可一次说清不绕弯'原则"；3. 7 项硬塞 1 轮违反 Goal-loop 节奏（Round 14 → 15 模式：每轮 2-4 follow-up）；4. FU-1 数据迁移属"独立 v3.02 子项目"（新建目录 + 386 TC LLM 重推理 + 全套导出），单独轮做更稳 |
| **替代方案** | B. 一次性 7 项全做（§9.1.1 豁免依赖 l1/stage_gatekeeper 既含 self-test；理论上可行但豁免条件 3 临界）→ **拒绝**：豁免条件 3「不动业务函数签名」对 stage_gatekeeper 改动临界 |
| **当前决策** | ✅ **采用 A**（Round 16 小集合；Round 17 中集合） |

### 3.2 §9.1 红线审计

| 文件 | 类型 | 是否计入 §9.1 | 说明 |
|---|---|---|---|
| `governance/design_iter/current/out_of_scope.md`（FU-3 新建） | 治理档 | ❌ 不计入（§9.1.2 治理档不计入） | 决策档类 |
| `workflow_assets/.../v3.01/「S6 测试用例生成」/*.bak` 删除（FU-6） | 过程资产清理 | ❌ 不计入（§9.1.2 goal-loop 产物 / workflow_assets 过程资产豁免） | workflow_assets/ 整体 .gitignore |
| `governance/design_iter/current/CONVERGED.md`（FU-7 覆盖） | 治理档 | ❌ 不计入（§9.1.2 治理档不计入） | 决策档类 |
| `governance/design_iter/current/round16_q_decision_table.md` | 决策档 | ❌ 不计入（本轮过程资产） | §9.5 落档协议 |
| `.goal-log-db/.../audit_16.md` | goal-loop 过程资产 | ❌ 不计入 | §9.1.2 |
| `.goal-log-db/.../review_16.md` | goal-loop 过程资产 | ❌ 不计入 | §9.1.2 |
| `.goal-log-db/.../snapshot.json` | goal-loop 状态 | ❌ 不计入 | §9.1.2 |
| **业务文件小计** | | **0** | **≤ 3 ✅（远低于红线）** |

**§9.1.1 豁免检查**：本轮业务文件 = 0，自然满足豁免条件 1/2/3/4，**无需触发 §9.1.1 豁免**——本轮架构上**比红线更严格**。

---

## §4 增量审计统计

| 指标 | Round 14 | Round 15 | Round 16 | 增量 |
|---|---|---|---|---|
| follow_up_items 总数 | 0 | 0 | 4（FU-1/2/4/5 延后 Round 17） | +4（净） |
| PASS 项数（本轮） | 4（F-A/B/C/D） | 2（F-E/F-F） | 3（FU-3/6/7） | +3 |
| 延后项数（本轮） | 0 | 0 | 4（FU-1/2/4/5） | +4 |
| PASS 总累计 | 4 | 6 | 9 | +3 |
| BLOCKER | 0 | 0 | 0 | 0 |
| MAJOR | 2（F-C/F-D） | 0 | 0 | 0 |
| MINOR | 2（F-A/F-B） | 2（F-E/F-F） | 7（FU-1~FU-7）→ 3 PASS + 4 延后 | +5 |
| decision_docs_landed | 1 | 1 | 1 | +1 |
| scope_compliance | PASS | PASS | PASS | ✅ |
| test_cases_json_bytes_unchanged | true | true | true | ✅ |
| test_cases_xlsx_bytes_unchanged | true | true | true | ✅ |
| self_test_total_cases | 15 | 22 | 22（不变） | 0 |

---

## §5 总体判定

**Round 16 结论**：✅ **PASS — 本轮处理 7 项 follow_up 中的 3 项（FU-3 + FU-6 + FU-7），其余 4 项（FU-1/2/4/5）延后 Round 17**

- ✅ **FU-3** [MINOR]：governance/design_iter/current/out_of_scope.md 新建 + 12 条守卫编号 G-001~G-012
- ✅ **FU-6** [MINOR]：v3.01 目录 5 个 .bak 删除 + 保留 audit/transitions JSON
- ✅ **FU-7** [MINOR]：governance/design_iter/current/CONVERGED.md 覆盖为 Round 16 收敛版（含 Round 14+15+16 三轮轨迹）
- ⏸️ **FU-1 / FU-2 / FU-4 / FU-5**：延后 Round 17（架构师自主决策 · 用户允许）
- ✅ v3.01 JSON 不变（338192 bytes）；v3.01 xlsx 不变（41572 bytes）
- ✅ self-test 22 cases 不变（Round 15 22/22 PASS；本轮无 Python 业务文件改动）
- ✅ §9.1 红线内（业务文件 0 < 3，无需 §9.1.1 豁免）
- ✅ §9.5 决策档 `round16_q_decision_table.md` 已落档
- ✅ §9.4 先验后答约束满足（≥ 12 个文件 Read）

---

## §6 Round 17 启动条件（FU-1/2/4/5 预备）

| ID | 启动条件 |
|---|---|
| **FU-1** | 1. Read v3.01 test_cases.json（338192 bytes）；2. 新建 v3.02 目录；3. LLM 推理 386 TC assertion（基于 expected_results 翻译）；4. 删除 fp_name 字段；5. 用 `ai_workflow/test_case_formatter.py` 重导出 .md + .xlsx；6. 验证 v3.02 行数 / 字段覆盖 / dict repr=0；7. 验证 v3.01 字节不变 |
| **FU-2** | 1. Read `ai_workflow/stage_gatekeeper.py`（必先 Read §9.4）；2. Read `ai_workflow/coverage_validator.py`；3. S6 gate 段加 `check_assertion_completeness` 自动调用；4. `gap_report` 输出段加 assertion 缺失统计；5. L1 self-test 加 C23 |
| **FU-4** | 与 FU-2 并入；helpers 加 `--auto` argv 分支；L1 self-test 加 C24 |
| **FU-5** | 1. Read `governance/open_questions.md` + `governance/design_iter/current/open_questions.md`；2. 按"已解 / 未解 / 无主"分类；3. 已解的归档到 `governance/design_iter/archive/open_questions_resolved/`；4. 未解的留 active；5. 无主的标注需人工认领 |

---

> 本审计档：`audit_16.md`（loop_round=6）
> 配套 review 档：`review_16.md`
> 配套决策档：`governance/design_iter/current/round16_q_decision_table.md`
> 配套守卫 SSOT：`governance/design_iter/current/out_of_scope.md`
> 配套 CONVERGED：`governance/design_iter/current/CONVERGED.md`
> 配套 snapshot：`.goal-log-db/active/32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3/snapshot.json`（atomic write）