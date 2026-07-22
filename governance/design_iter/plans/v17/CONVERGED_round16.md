# CONVERGED — Goal 6d3edb03（GL-017 · Round 15 §11.5 遗留 + Round 16 格式治理 · Round 1 Act）

**日期**：2026-07-19
**Goal ID**：`6d3edb03-352d-4a3f-921c-b880db0625f5`
**Goal-loop 编号**：GL-017（GL-009 R14-R18 完整收敛后的新一轮 Goal-loop）
**状态**：`achieved`（GL-017 Round 1 终态，单轮收敛）

> **本档是 GL-017 Round 1 收敛档**——覆盖 5 项 Round 15 §11.5 遗留 follow_up 中的 3 项 + Round 16 用户新诉求 1 项 + 过程合规 2 项 = 12 项 task_queue 全 done，6 V + 4 P 全 PASS。
> 沿用 GL-009 完整轨迹（R14-R18，CONVERGED.md §1-9），本 Goal-loop 是 GL-009 的后续轮次（GL-017）。
> 与 GL-009 CONVERGED.md 不冲突——本档独立存在，记录 GL-017 Round 1 增量收敛。

---

## 1. 状态

✅ **Goal 单轮完全收敛成功（achieved · value_ratio = 0.6 达标）**

- V-001 ~ V-006（4 BLOCKER + 2 MAJOR）全部 PASS
- P-001 ~ P-004（4 MAJOR）全部 PASS
- 12 项 task_queue 全部 done（T-001 ~ T-012）
- loop_round = 1（单轮收敛，无 follow_up 阻塞）
- status = achieved
- value_ratio = 6 / (6 + 4) = **0.6**（恰好达标 ≥ 0.6 硬约束）
- follow_up_items 显式记录 4 项遗留（推 Round 17 / v3.02）

---

## 2. 完成内容（12 项 task_queue · 全 ✅）

| ID | 任务 | 状态 | 关键证据 |
|---|---|---|---|
| T-001 | 修 normalizer mirror_bilingual_aliases（list 字段保持 list）| ✅ | `_resolve_field` 返回 `(Any, bool)`；`_LIST_CANONICAL_KEYS` 白名单；list → list 镜像 |
| T-002 | normalizer self_test +3 case（list→list / string→string / mix 字段）| ✅ | self_test 9 case 全 PASS |
| T-003 | scenario_group_merger 加 source_case_ids 字段 | ✅ | `_flush` 写 source_case_ids；singleton 强制 1 元素 list |
| T-004 | merger self_test +1 case（source_case_ids 字段验证）| ✅ | self_test 6 case 全 PASS |
| T-005 | test_case_formatter 加 Sheet 2「用例描述索引」+ OBJ→FP 排序 + 同色背景 + 空行 | ✅ | 4 helper 函数：`_sort_cases_by_obj_fp` / `_populate_worksheet_with_obj_grouping` / `_build_case_description_index_rows` / `_populate_description_index_sheet` |
| T-006 | run_round15_merge_export.py 升级调用新 formatter 入口 | ✅ | `sort_options` + `description_index_sheet=True` |
| T-007 | SKILL.md §11 加测试设计层级原则段 | ✅ | 新增 `#### 测试设计层级原则（Round 16 新增 · 永久强制）` 段 |
| T-008 | STAGE_S6_TEST_CASES.mdc §11 同步 | ✅ | 新增 `### §11 测试设计层级原则（Round 16 新增 · 同步 SKILL.md §11.1）` 段 |
| T-009 | 跑完整 pytest 套件 + 4 个 self-test + 主调脚本 | ✅ | pytest 25/26 PASS（1 pre-existing FAIL 与 Round 16 无关）+ 4 self-test 全 PASS + 主调 0 errors |
| T-010 | 重导 v3.01 xlsx + 物理验证（双 Sheet + 索引 + 排序 + 背景）| ✅ | 87 TC + 15 spacer = 102 行 / 附录 0 / Sheet 2 索引 16 OBJ / 5 色 OBJ 分组 |
| T-011 | audit_16.md + review_16.md 落档（6 VC 全 PASS 证据）| ✅ | `governance/design_iter/plans/v17/audit_16.md` + `review_16.md` |
| T-012 | snapshot 推进 + CONVERGED.md 6 项必含 | ✅ | snapshot.json status=achieved + loop_round=1 + 12 task done + 4 follow_up 记录 |

---

## 3. 验收证据（6 V + 4 P）

### 3.1 V 项验证（6 项）

| ID | 等级 | 标题 | 判定 | 关键证据 |
|---|---|---|---|---|
| V-001 | BLOCKER | normalizer mirror_bilingual_aliases list→list 镜像 | ✅ PASS | `_resolve_field` 行为契约变更 + 9 self_test case |
| V-002 | BLOCKER | SSOT §11 测试设计层级原则段档 | ✅ PASS | SKILL.md + .mdc 双写 §11.1 |
| V-003 | BLOCKER | xlsx 重导出（OBJ→FP 排序 + 同色 + 空行）| ✅ PASS | 87 TC + 15 spacer + 5 色轮转物理验证 |
| V-004 | BLOCKER | xlsx 加 Sheet 2「用例描述索引」 | ✅ PASS | 16 OBJ × {OBJ ID / 用例描述 / FP 数 / TC 数 / Ready 数} |
| V-005 | MAJOR | merger 加 source_case_ids 字段 | ✅ PASS | Group A (2→1) / Group B (3→1) / singleton self_test |
| V-006 | MAJOR | 端到端验证：双 Sheet 分流仍正确 | ✅ PASS | 主表 87 / 附录 0 / Sheet 2 16 OBJ |

### 3.2 P 项验证（4 项）

| ID | 等级 | 标题 | 判定 | 关键证据 |
|---|---|---|---|---|
| P-001 | MAJOR | 治理记录同步：snapshot / 落档 / CONVERGED.md 三处一致 | ✅ PASS | snapshot.json 6 V + 4 P + 4 follow_up 与 audit_16.md / review_16.md / 本档 §3 一致 |
| P-002 | MAJOR | 所有 .py 含 def self_test() + --self-test argv | ✅ PASS | case_id_and_field_normalizer / scenario_group_merger / test_case_formatter / run_round15_merge_export 全 PASS |
| P-003 | MAJOR | 不修改 v3.01 test_cases.json；不 commit | ✅ PASS | test_cases.json 字节级 338192 不变（stash pop 验证）；未 commit |
| P-004 | MAJOR | 严格执行 12 项 task_queue；不扩展目标范围 | ✅ PASS | 12 task 全部 done；未扩展 FU-A2 / FU-A4（推 Round 17 / v3.02）|

### 3.3 客观回归指标

| 指标 | 期望 | Round 16 实测 | 状态 |
|---|---|---|---|
| v3.01 test_cases.json 字节 | 338192 | 338192 | ✅ 严守（out_of_scope）|
| v3.01 test_cases_public.xlsx 字节 | 不锁 | 20265 → 重新生成（含 Sheet 2 索引）| ✅ 过程产物 |
| v3.01 xlsx sheetnames | 3 | ['测试用例', 'Draft-Rejected附录', '用例描述索引'] | ✅ |
| 主表 TC 数 | 87 | 87 | ✅ |
| 主表 spacer 数 | 15 | 15 | ✅ |
| 主表 OBJ 填充色 | 5 种轮转 | 5 种（gray/blue/yellow/green/purple）| ✅ |
| 附录 row 数 | 1 (header only) | 1 | ✅ |
| Sheet 2 索引 OBJ 数 | 16 | 16 | ✅ |
| Sheet 2 FP 数合计 | 50 | 50 | ✅ |
| Sheet 2 TC 数合计 | 87 | 87 | ✅ |
| Sheet 2 Ready 数合计 | 87 | 87 | ✅ |
| pytest | 25/26 PASS | 25 PASS + 1 pre-existing FAIL（test_s5_s6_s7_closure）| ✅ |
| self-test | 4/4 PASS | case_id_and_field_normalizer / scenario_group_merger / test_case_formatter / run_round15_merge_export 全 PASS | ✅ |
| py_compile | 0 errors | 0 | ✅ |
| value_ratio | ≥ 0.6 | 0.6（恰好达标）| ✅ |
| follow_up_items | 显式记录 | 4 项（v3.02 prompt / FU-A2 拆约束 / 补丁清理 / source_case_ids 渲染）| ✅ |
| status | achieved | achieved | ✅ |
| loop_round | 1 | 1（单轮收敛）| ✅ |

---

## 4. 自迭代记录（GL-017 Round 1 · 5 项 follow_up 清 3 项）

| 类别 | 改进点 | 状态 |
|---|---|---|
| FU-A1 normalizer list mirror bug | `_resolve_field` 行为契约变更 + `_LIST_CANONICAL_KEYS` 白名单 | ✅ 清 |
| FU-A3 merger source_case_ids 字段 | `_flush` 写 source_case_ids + singleton 1 元素 list 契约 | ✅ 清 |
| FU-B1 用例描述 / 功能描述格式治理 | xlsx sort + 同色 + 空行 + Sheet 2 索引 + SSOT §11.1 测试设计层级原则 | ✅ 清 |
| FU-A2 SSOT 拆约束对象（LLM vs 数据存储）| 推 v3.02 治理 | ❌ 延后 |
| FU-A4 v3.01 数据 step/expected 错位 | 推 v3.02 prompt 治理 | ❌ 延后 |

**GL-017 Round 1 拆分策略**：父会话 `full_chain` 授权一次性 12 项 task_queue 推进；3 项 follow_up（FU-A1 / FU-A3 / FU-B1）一次清完，2 项 follow_up（FU-A2 / FU-A4）推 v3.02 治理（out_of_scope §10 继承）。

---

## 5. 遗留项（follow_up_items · 4 项）

| 遗留项 | 等级 | 修复方向 |
|---|---|---|
| v3.01 数据 step/expected 错位（Round 15 §11.5 FU-A4）| MINOR | v3.02 prompt 治理（重生成 v3.02 数据时确保 step 与 expected 对齐）|
| SSOT 拆约束对象（Round 15 §11.5 FU-A2 LLM 生成 vs 数据存储）| MAJOR | v3.02 治理（SKILL.md §11 拆分为 §11.LLM-generation-rules + §11.Data-storage-rules）|
| `_sync_list_fields_after_merge` 补丁清理 | LOW | Round 17 验证 normalizer 修复后可移除（防御性兜底）|
| source_case_ids 在 xlsx 主表渲染 | LOW | Round 17 可扩展主表 +1 列展示 source TC id 列表（用户可视化追溯）|

---

## 6. 影响范围

### 6.1 修改文件清单（按 Git 分类 · GL-017 Round 1）

**业务文档（应提交 git · 但本 Goal 用户禁止 commit）**

| 类别 | 文件 | 改动 |
|---|---|---|
| 技能 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | +80 行 §11.1「测试设计层级原则（Round 16 新增 · 永久强制）」|
| 规则 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | +50 行 §11 测试设计层级原则（同步 SKILL.md §11.1）|

**实现代码（应提交 git · 但本 Goal 用户禁止 commit）**

| 类别 | 文件 | 改动 |
|---|---|---|
| 实现（修改） | `ai_workflow/case_id_and_field_normalizer.py` | `_resolve_field` 返回 `(Any, bool)`；`_LIST_CANONICAL_KEYS` 白名单；self_test +3 case |
| 实现（修改） | `ai_workflow/scenario_group_merger.py` | `_flush` 加 `source_case_ids` 写入；`_source_ids` accumulator；self_test +1 case |
| 实现（修改） | `ai_workflow/test_case_formatter.py` | `_save_xlsx` 加 `sort_options` / `description_index_sheet` 参数；4 helper 函数（`_sort_cases_by_obj_fp` / `_populate_worksheet_with_obj_grouping` / `_build_case_description_index_rows` / `_populate_description_index_sheet`）|
| 实现（修改） | `ai_workflow/run_round15_merge_export.py` | 调新 formatter 入口（`sort_options` + `description_index_sheet=True`）|

**过程产物（不入 git · workflow_assets）**

| 文件 | 处理 |
|---|---|
| `workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases.json` | ✅ R16 严守 338192 bytes（out_of_scope）|
| `workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases_public.xlsx` | ✅ R16 重导出（102 行主表 + 1 行附录 + 17 行 Sheet 2 索引）|
| `workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases_public.round16.precheck.bak.xlsx` | ✅ R16 新建 20265 bytes（旧 Round 15 输出备份）|

**Goal 快照（不入 git · .goal-log-db）**

| 文件 | 改动 |
|---|---|
| `.goal-log-db/active/6d3edb03-.../snapshot.json` | R1 status=paused → active → achieved；loop_round=1；12 task_queue 全部 done |

**治理资产（v17/plans/ + current/ · R16 新增）**

| 文件 | 改动 |
|---|---|
| `governance/design_iter/plans/v17/audit_16.md` | R16 审计档（6 V 全 PASS 证据 + 反向挑战）|
| `governance/design_iter/plans/v17/review_16.md` | R16 复盘档（缺陷 / 根因 / 修复方案 / 决策表 / 遗留项 / 影响范围 / 反模式自检）|
| `governance/design_iter/plans/v17/CONVERGED_round16.md` | R16 收敛档（本档）|
| `governance/design_iter/current/goal_round16_followup_and_format.md` | R16 Plan 占位档（已存在）+ §6.1 落档协议执行记录（计划追加）|

### 6.2 用户决策影响

无 — 所有改动在父会话 `full_chain` 授权范围内；用户明确禁止 commit git（所有改动保留在工作区）。

### 6.3 下游影响

- **S6 后续生成**：未来 S6 调用可使用 normalizer 修复后的 list→list 镜像（无需 `_sync_list_fields_after_merge` 兜底）；新生成 TC 的 `obj_id` / `feature_point_ref` 必填（SSOT §11.1 测试设计层级原则）。
- **S7 Rejected 链路**：v3.01 仍可继续按现有链路审查（byte-lock 守）；`source_case_ids` 字段供 S7 审查员 B 追溯合并 TC 源。
- **xlsx 用户体验**：打开 v3.01 xlsx 即见 3 个 Sheet——测试用例（87 TC 按 OBJ 分组 + 5 色背景 + 空行）/ Draft-Rejected附录（空）/ 用例描述索引（16 OBJ × {OBJ ID / 用例描述 / FP 数 / TC 数 / Ready 数}）。
- **LLM 生成 TC**：未来 S6 prompt 按 §11.1 测试设计层级原则展开（OBJ→FP→前置条件→TC）——避免 1 OBJ 多 FP 共享 1 TC 或 1 步 1 TC 碎裂两个极端。

### 6.4 风险登记

| 风险 | 等级 | 缓解 |
|---|---|---|
| normalizer 行为契约变更可能影响外部调用方 | LOW | `_resolve_field` 是内部函数（无外部调用）；self_test 9 case 覆盖核心路径 |
| xlsx 同 OBJ 同色背景 5 色轮转可能导致部分用户视觉疲劳 | INFO | 颜色经 WCAG AA 对比度验证；可后续 Round 17 用户反馈调整 |
| `_sync_list_fields_after_merge` 兜底补丁未移除 | LOW | 保留不影响正确性；Round 17 验证 normalizer 修复后可清理 |
| value_ratio = 0.6 恰好达标 | INFO | 4 项 BLOCKER + 2 项 MAJOR 全 PASS；按 SKILL.md §2.1 强制占比已满足 |

---

## 7. 跨 Goal 衔接

### 7.1 上游 Goal

**GL-009 · test case 审查治理**（Goal ID: `32a8ff45-...` · R14-R18 完整轨迹，见 `governance/design_iter/plans/v17/CONVERGED.md`）：
- 本 Goal 沿用 GL-009 建立的 case_id 命名空间（`{Module}-TC-{NNN}`）
- 本 Goal 沿用 GL-009 建立的字段双向映射表（canonical 中文 ↔ legacy English）
- 本 Goal 沿用 GL-009 建立的 xlsx 双 Sheet 分流契约（_partition_cases_for_xlsx）

### 7.2 Round 15 §11.5 遗留 follow_up 5 项 → Round 16 清 3 项

| Round 15 遗留 | GL-017 Round 1 处置 |
|---|---|
| FU-A1 normalizer list mirror bug | ✅ Round 16 直接修复 |
| FU-A3 merger source_case_ids 字段 | ✅ Round 16 merger 加字段 |
| FU-A2 SSOT 拆约束对象 | ❌ 推 v3.02 治理 |
| FU-A4 v3.01 step/expected 错位 | ❌ 推 v3.02 prompt 治理 |
| FU-B1 Round 16 用户新诉求（格式治理）| ✅ Round 16 formatter 扩展 + SSOT §11.1 |

### 7.3 下游 Goal（潜在）

- **GL-018 候选**：基于 GL-017 Round 1 修复后的 normalizer + source_case_ids 字段，跑 v3.02 数据迁移（FU-A2 + FU-A4 治理）
- **GL-019 候选**：基于 GL-017 Round 1 Sheet 2 索引 + SSOT §11.1 层级原则，跑 S7 正式审查 → S8 自迭代

---

## 8. 收敛完成声明

✅ **本 Goal (6d3edb03-...) 完整收敛**：

- 原始需求"Round 15 §11.5 遗留 follow_up + Round 16 格式治理合并推进" — **完全达成**
- 5 项 follow_up（FU-A1 / FU-A2 / FU-A3 / FU-A4 / FU-B1）— **3 项已清**（FU-A1 / FU-A3 / FU-B1），2 项显式延后（FU-A2 / FU-A4 推 v3.02）
- 12 项 task_queue（T-001 ~ T-012）— **全部 done**
- 6 V + 4 P — **全 PASS**
- snapshot.status = **achieved** / loop_round = **1** / value_ratio = **0.6**

**GL-017 Round 1 全部需求闭环** — 单轮收敛、3 项 follow_up 已清、2 项延后项已显式 follow_up_items 记录。

---

## 9. 关键引用

| 内容 | 路径 |
|---|---|
| Round 16 Plan 档 | `governance/design_iter/current/goal_round16_followup_and_format.md` |
| Round 16 审计档 | `governance/design_iter/plans/v17/audit_16.md` |
| Round 16 复盘档 | `governance/design_iter/plans/v17/review_16.md` |
| Round 16 收敛档（本档）| `governance/design_iter/plans/v17/CONVERGED_round16.md` |
| GL-017 Goal 快照 | `.goal-log-db/active/6d3edb03-352d-4a3f-921c-b880db0625f5/snapshot.json` |
| GL-017 禁区清单 | `.goal-log-db/active/6d3edb03-352d-4a3f-921c-b880db0625f5/out_of_scope.md` |
| 业务快照（v3.01）| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` |
| v3.01 重导 xlsx | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` |
| v3.01 xlsx 备份 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round16.precheck.bak.xlsx` |
| GL-009 CONVERGED（上轮完整轨迹）| `governance/design_iter/plans/v17/CONVERGED.md` |
| GL-017 SKILL 入口 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §11.1 |
| GL-017 阶段规则 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §11 |
| 全局 DNA | `AGENTS.md` + `.cursor/rules/DNA_3Q_CHECK.mdc` |
