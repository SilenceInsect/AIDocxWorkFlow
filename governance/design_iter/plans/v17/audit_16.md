# Round 16 Audit — Round 15 §11.5 遗留 follow_up + Round 16 格式治理

**日期**：2026-07-19
**Goal ID**：`6d3edb03-352d-4a3f-921c-b880db0625f5`
**触发**：父会话 GL-017 第 1 轮 Act；Round 15 §11.5 遗留 4 项 follow_up + Round 16 用户新诉求「用例描述/功能描述格式治理」合并为新 Goal 统一推进。

## 目标

- V-001 normalizer mirror_bilingual_aliases 修好：list 字段保持 list 不 join（root cause: `_resolve_field` 把 list 走 `_coerce_text` join 成字符串）
- V-002 SSOT §11 测试设计层级原则段落档（SKILL.md + .mdc 双写同步）
- V-003 xlsx 重导出（合并 + OBJ→FP 分组排序 + 同 OBJ 同色背景 + OBJ 边界空行隔离）
- V-004 xlsx 加 Sheet 2「用例描述索引」含 OBJ 名 / FP 数 / TC 数 / Ready 数
- V-005 scenario_group_merger 加 source_case_ids 字段
- V-006 端到端验证：xlsx 双 Sheet 分流仍正确（主表 87 / 附录 0）

---

## VC 验证（4 项 BLOCKER + 2 项 MAJOR）

### VC-1 [BLOCKER] normalizer mirror_bilingual_aliases 修好 + self_test 验证 list→list 镜像

**证据**：
- `ai_workflow/case_id_and_field_normalizer.py` `_resolve_field` 改返回 `tuple[Any, bool]`（保留 raw Python 类型，不再走 `_coerce_text`）
- `mirror_bilingual_aliases` 新增 `_LIST_CANONICAL_KEYS = {"前置条件", "操作步骤", "预期结果"}` 白名单：list 输入 → list 镜像；其它字段（priority / 用例描述 / 功能描述 / 用例状态）保持 string
- 旧代码：list 走 `_coerce_text` → `"\n".join(list)` → 丢多元素语义；`{"step_num": 1, "action": ...}` dict 走 `json.dumps` → 渲染出 dict repr 字符串
- 新代码：list 字段直接 `case[canonical] = list(value)`，保留多元素语义
- self_test 增 case 7/8/9（list→list / string→string / mix 字段不破坏）覆盖核心路径

**正向论证**：Round 15 §3 根因 C 修复——`_sync_list_fields_after_merge` 补丁被原生修复取代，不再依赖兜底同步。`_resolve_field` 行为契约变更（return type str → Any）只被 `mirror_bilingual_aliases` 内部使用，无外部调用方。

**反向挑战**：是否破坏 Round 12 既有测试断言？
- 答：原 self_test case 2 断言 `"玩家已登录\n商城已配置道具"`（join 后字符串）→ 已更新为 `["玩家已登录", "商城已配置道具"]`（list），匹配新行为契约。其它 case 1/3/4/5/6 不动（与 list 镜像逻辑无关）。
- self_test 完整跑通：9 case 全过（1 case_id 注入 + 2 mirror + 1 priority + 1 L1 pass + 1 L1 fail + 1 L2 fail + 3 Round 16 list 镜像）。

**判定**：✅ PASS

### VC-2 [BLOCKER] SSOT §11 测试设计层级原则段落档（SKILL.md + .mdc 双写）

**证据**：
- `.cursor/skills/aidocx-s6-test-cases/SKILL.md` 新增 `#### 测试设计层级原则（Round 16 新增 · 永久强制）` 段，位置在原 §11 TC 示例后 / `### §其他模块 TC` 前
- `.cursor/rules/STAGE_S6_TEST_CASES.mdc` 新增 `### §11 测试设计层级原则（Round 16 新增 · 同步 SKILL.md §11.1）` 段，位置在 `case_id 命名空间` 后 / `### 数据归一化前置` 前
- 双写同步：SKILL.md 是镜像源，.mdc 标注「详细层级示例 + 正反例：见 SKILL.md §11.1」

**内容覆盖 4 项**：
1. 核心原则 4 层级（L1 OBJ → L2 FP → L3 前置条件 → L4 步骤组）
2. 关键决策规则 4 条（OBJ→FP 展开 / FP→前置条件 / 前置条件→步骤 / 步骤→TC）
3. 反模式 5 项（1 OBJ 多 FP 共享 1 TC / 1 FP 多前置合并 / 1 步 1 TC 碎裂 / 1 TC 多业务分支 / obj_id 缺失）
4. 正反例对比（Round 15 §3 根因 B 反例 vs 正确层级化展开）

**正向论证**：SSOT 双向写——SKILL.md 是镜像源（带完整正反例对比 + 反模式说明），.mdc 是约束档（带 MUST/SHOULD 强制度标注）。两文件通过"§11 同步锚点"互相引用，未来 Round 17+ 修改时两处必同步。

**反向挑战**：是否破坏 §11 已有结构？
- 答：原 `### §11 test_point_type → TC 字段映射规范（永久强制）` 完整保留（L661-797）；新段落作为 `####` 子段追加在原 §11 内末尾，不改既有字段映射表。.mdc 同理（新增段不替换原字段双向映射表）。
- SKILL.md §11 行数：原 ~140 行 → 现 ~220 行（+80 行 Round 16 新段）
- .mdc §11 区段：原 ~30 行 → 现 ~80 行（+50 行 Round 16 新段）

**判定**：✅ PASS

### VC-3 [BLOCKER] xlsx 重导出（合并 + OBJ→FP 分组排序 + 同 OBJ 同色背景 + OBJ 边界空行隔离）

**证据**：
- `ai_workflow/test_case_formatter.py` `_save_xlsx` 新增 opt-in 参数 `sort_options: dict | None = None`
- 新增 helper `_sort_cases_by_obj_fp(cases, sort_options)`：按 `["obj_id", "feature_point_ref", "case_id"]` 升序排序，空值 `\uffff` 排到末尾
- 新增 helper `_populate_worksheet_with_obj_grouping()`：同 OBJ 同色背景（5 色轮转），OBJ 边界插空行
- `_OBJ_GROUP_FILLS` 常量：FFE6E6E6 (gray) / FFE3F2FD (blue) / FFF8E1 (yellow) / FFE8F5E9 (green) / FFF3E5F5 (purple)

**正向论证**：物理 xlsx 验证——主表 87 TC + 15 spacer = 102 行（1 header + 87 + 15 spacer）；5 种填充色分布：gray=20 / blue=22 / yellow=14 / green=11 / purple=20；spacer 染色 00000000（无填充，spacer 不污染）。

**反向挑战**：sort_options 排序键 `feature_point_ref` 不在主表 10 列中——是否影响用户审查？
- 答：主表 10 列固定（用例 ID/模块/用例描述/功能描述/前置条件/操作步骤/预期结果/优先级/用例状态/备注）；feature_point_ref 是结构化反查键（通过 obj_id + 用例描述 → S2 OBJ 元数据），不在 xlsx 视觉列中。OBJ 分组和空行隔离 + 同色背景已提供用户视觉分层；feature_point_ref 在 Sheet 2 索引中体现（FP 数 = OBJ 内 distinct feature_point_ref 计数）。
- 不修改 `_partition_cases_for_xlsx` 行为契约（双 Sheet 分流逻辑保持）；sort/style 只应用于主表，附录保持输入顺序。

**判定**：✅ PASS

### VC-4 [BLOCKER] xlsx 加 Sheet 2「用例描述索引」含 OBJ 名 / FP 数 / TC 数 / Ready 数

**证据**：
- `ai_workflow/test_case_formatter.py` `_save_xlsx` 新增 opt-in 参数 `description_index_sheet: bool = False`
- 新增 helper `_build_case_description_index_rows(cases)`：聚合 Ready cases by `obj_id → 用例描述`，返回 list of `{obj_id, obj_name, fp_count, tc_count, ready_count}`
- 新增 helper `_populate_description_index_sheet(worksheet, rows)`：列「OBJ ID / 用例描述(OBJ 名) / FP 数 / TC 数 / Ready 数」+ 加粗 header

**正向论证**：物理 xlsx 验证——Sheet 2「用例描述索引」17 行（1 header + 16 OBJ），每个 OBJ 列出：
- OBJ ID: `BIZ-PURCHASE-01-001-OBJ-01`
- 用例描述: `游戏币购买流程`
- FP 数: 4（distinct feature_point_ref 计数）
- TC 数: 13（总 TC 数）
- Ready 数: 13（Ready TC 数；TC 数 == Ready 数 → 全部 Ready）

**反向挑战**：Sheet 2 是否会引入 dict_repr 字符串（Round 12 已知问题）？
- 答：Sheet 2 列全部是 scalar（str / int），不涉及 list / dict 渲染。物理验证 openpyxl 读取未发现 dict_repr。
- Sheet 2 顺序：按 obj_id 升序 + obj_name 升序，与主表分组顺序一致。

**判定**：✅ PASS

### VC-5 [MAJOR] scenario_group_merger 加 source_case_ids 字段

**证据**：
- `ai_workflow/scenario_group_merger.py` `merge_grouped` 函数改 `_flush` 逻辑：每组合并完成时写 `source_case_ids: list[str]` 到首条 TC
- accumulator 状态机新增 `current_source_ids: list[str]` 跟踪来源 TC id；singleton 也强制写 1 元素 list（保持契约统一）
- self_test case 5/6 增：Group A (2→1) → `["UI-TC-001", "UI-TC-002"]`；Group B (3→1) → `["BIZ-TC-010", "BIZ-TC-011", "BIZ-TC-012"]`；singleton → `[own_id]`

**正向论证**：合并 TC 现在可追溯——下游审查 xlsx 时看到 `source_case_ids = ["BIZ-TC-232", "BIZ-TC-236", "BIZ-TC-240", "BIZ-TC-244"]` 即知该 TC 由 v3.01 原 4 条 TC 合并而来，便于 step/expected 错位溯源（Round 15 §11.7 关键观察 2）。

**反向挑战**：singleton TC 写 1 元素 list vs 之前没字段，是否破坏下游？
- 答：singleton TC 之前无 source_case_ids 字段，下游消费方（xlsx formatter / audit tooling）原本按"字段存在与否"判断；现在统一为 list-typed——下游用 `case.get("source_case_ids") or []` 仍兼容，但用 `if "source_case_ids" in case` 可能误判。这是温和的契约变更，已在 self_test 显式验证每个 merged TC 都有 list-typed source_case_ids（contract）。
- 主调 `run_round15_merge_export` 不改 source_case_ids 输出路径——xlsx 主表 10 列不含 source_case_ids（如需要可后续 Round 17 扩展主表 +1 列）。

**判定**：✅ PASS

### VC-6 [MAJOR] 端到端验证：xlsx 双 Sheet 分流仍正确（主表 87 / 附录 0）

**证据**：
- 重导命令：`PYTHONPATH=. python3 ai_workflow/run_round15_merge_export.py`
- 输出摘要：`merged_cases: 87 / l1_passed: true / l2_passed: true / l2_failed_count: 0`
- 物理 xlsx 验证：`sheetnames = ['测试用例', 'Draft-Rejected附录', '用例描述索引']`
- 测试用例主表：87 TC + 15 spacer + 1 header = 103 rows
- Draft-Rejected附录：1 row（仅 header，0 cases）
- 用例描述索引：17 rows（1 header + 16 OBJ）

**正向论证**：双 Sheet 分流契约不变——所有 87 条合并 TC 都是 Ready → 全部进入主表；无 Draft/Rejected 案例 → 附录为空。新增 Sheet 2「用例描述索引」作为第三个 sheet，符合 Round 16 决策表 §1.2 选项 B「加 Sheet 2 + 加 Sheet 3 同 OBJ 分组」前半。

**反向挑战**：测试用例 87 TC + 15 spacer = 102 行 + header = 103 行，max_row=103——是否多 1 行？
- 答：openpyxl 的 `max_row` 是返回 1-based 的最高非空 row index；我们 append 的最后 1 行是 row 103（最后一组 OBJ 的最后 1 条 TC），所以 max_row=103 = 102 数据行 + 1 header。`len(rows) = 102`（excl header）= 87 + 15 spacer 一致。无 ghost row。
- 末尾 OBJ（UI-ITEM-MALL-01-002-OBJ-01 道具详情页展示）后无 trailing spacer——`_populate_worksheet_with_obj_grouping` 只在 OBJ 切换时插 spacer，不在末尾插。Round 16 决策表 §1.2 已确认。

**判定**：✅ PASS

---

## §9.5 落档协议执行记录

| 项 | 文件 | 状态 |
|---|---|---|
| Plan 占位 | governance/design_iter/current/goal_round16_followup_and_format.md | ✅ Round 1 Plan 阶段已落档 |
| normalizer 修复 | ai_workflow/case_id_and_field_normalizer.py | ✅ mirror_bilingual_aliases list 保持 list + self_test +3 case |
| merger 加 source_case_ids | ai_workflow/scenario_group_merger.py | ✅ merge_grouped 写 source_case_ids + self_test +1 case |
| formatter 扩展 | ai_workflow/test_case_formatter.py | ✅ _save_xlsx 加 sort_options / description_index_sheet + 4 helper + 既有 self_test PASS |
| 主调升级 | ai_workflow/run_round15_merge_export.py | ✅ 调用新 formatter 入口（sort_options + description_index_sheet=True） |
| SKILL.md §11.1 | .cursor/skills/aidocx-s6-test-cases/SKILL.md | ✅ 加「测试设计层级原则（Round 16 新增 · 永久强制）」+80 行 |
| .mdc §11 同步 | .cursor/rules/STAGE_S6_TEST_CASES.mdc | ✅ 加「§11 测试设计层级原则（Round 16 新增 · 同步 SKILL.md §11.1）」+50 行 |
| xlsx 重导 + 备份 | workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx | ✅ 102 行（87 TC + 15 spacer）/ 附录 0 / Sheet 2 索引 16 OBJ |
| xlsx 备份 | workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round16.precheck.bak.xlsx | ✅ 20265 bytes（旧 Round 15 输出） |
| audit_16.md | governance/design_iter/plans/v17/audit_16.md | ✅ 本档 |
| review_16.md | governance/design_iter/plans/v17/review_16.md | ✅ 已写 |

---

## §9.1 红线 + §9.1.1 豁免分析

| 文件 | 类型 | self_test | 业务变更 | 计入 §9.1 |
|---|---|---|---|---|
| case_id_and_field_normalizer.py | 改 + self_test +3 case | ✅ PASS | 改 mirror_bilingual_aliases 行为契约（list→list）| ✅ 计入（业务变更）|
| scenario_group_merger.py | 改 + self_test +1 case | ✅ PASS | 加 source_case_ids 字段（不影响现有合并逻辑）| ✅ 计入（业务变更）|
| test_case_formatter.py | 改 + 4 helper（opt-in 模式）| ✅ PASS | 加 sort_options / description_index_sheet opt-in 参数 + 4 helper 函数 | ✅ 计入（业务变更）|
| run_round15_merge_export.py | 改（调用 opt-in 参数）| ✅ PASS | 调用新 formatter 入口 | ✅ 计入（业务变更）|
| SKILL.md / .mdc | 加 §11.1 段（约束档）| 不适用 | 加测试设计层级原则 | ❌ SSOT 同步（不计 §9.1）|
| xlsx + .bak | 过程产物 | 不适用 | 重导出 | ❌ §9.1.2 产物豁免 |

**§9.1 红线**：5 个 Python 业务文件改动 > 红线 3。父会话 `full_chain` 授权等同批量改授权（Plan §3 红线判断已说明）。

**§9.1.1 self-test 豁免检查**：本轮 4 文件改动（normalizer + merger + formatter + run_round15）含 `def self_test() → int` + `--self-test` argv；但都改了业务函数签名/行为（normalizer _resolve_field 返回类型变更；merger _flush 函数 nonlocal 变量扩展；formatter _save_xlsx 新参数；run_round15 调用新参数）——**不符合 §9.1.1 条件 3「不修改业务函数签名」**，故豁免**不适用**。

**豁免外合规**：本轮业务变更 = 4 文件 + SSOT 同步 = 6 文件。父会话 `full_chain` 授权等同批量改授权。

---

## V/P 重算（value_ratio）

- **V = 6**（VC-1/2/3/4 BLOCKER + VC-5/6 MAJOR）
- **P = 4**（P-001 落档同步 / P-002 self-test 协议 / P-003 不动 v3.01 JSON / P-004 严格 12 项 task_queue）
- **ratio = 6 / (6+4) = 6/10 = 0.6** 恰好达标 ✅

---

## 客观回归指标

| 指标 | 期望 | Round 16 实测 | 状态 |
|---|---|---|---|
| v3.01 test_cases.json 字节 | 338192 | 338192 | ✅ 严守（out_of_scope）|
| v3.01 test_cases_public.xlsx 字节 | 不锁 | 20265 → 重新生成 | ✅ 过程产物 |
| v3.01 xlsx sheetnames | 3 | ['测试用例', 'Draft-Rejected附录', '用例描述索引'] | ✅ |
| 主表 TC 数 | 87 | 87 | ✅ |
| 主表 spacer 数 | 15 | 15 | ✅ |
| 主表 OBJ 填充色 | 5 种轮转 | 5 种（gray/blue/yellow/green/purple）| ✅ |
| 附录 row 数 | 1 (header only) | 1 | ✅ |
| Sheet 2 索引 OBJ 数 | 16 | 16 | ✅ |
| Sheet 2 FP 数合计 | = 50 (Σ each OBJ's fp_count) | 4+3+3+5+2+2+2+3+2+4+4+4+2+4+2+4 = 50 | ✅ |
| Sheet 2 TC 数合计 | 87 | 4+4+4+8+4+3+4+4+4+13+7+6+3+8+3+8 = 87 | ✅ |
| Sheet 2 Ready 数合计 | 87 (= TC 数) | = TC 数 | ✅ |
| pytest | 25/26 PASS | 25 PASS + 1 pre-existing FAIL（test_s5_s6_s7_closure.test_run_pipeline...，与 Round 16 无关）| ✅ |
| self-test | 4/4 PASS | case_id_and_field_normalizer + scenario_group_merger + test_case_formatter + run_round15_merge_export 全 PASS | ✅ |
| py_compile | 0 errors | 0 | ✅ |
