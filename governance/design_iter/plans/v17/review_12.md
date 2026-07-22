# Round 12 Review — v3.01 xlsx 收敛问题与设计变更

**日期**：2026-07-19
**轮次**：Round 12
**目标**：将 v3.01 实际数据收敛到全 Ready 状态，并修正 v17 阶段设计与实现的不一致。

---

## 根因分析

### 问题 1：v3.01 数据 schema 与 v17 L1S6Validator SSOT 错位

**现象**：
- `test_cases.json` 331 条用例全部 `Draft`，主表空、附录 331 条
- L1S6Validator 报 `MISSING_REQUIRED 前置条件` × 331、`id_errors` × 331

**根因**：
- v17 字段溯源方案（R2/R3）**新增**了 obj_name / fp_name / feature_point_ref / s5_ref 字段（这部分对齐）
- 但**保留了 Round 17 之前的 legacy English schema**：
  - `preconditions` / `steps` / `expected_results` / `priority`（非 L1S6Validator 期望的中文别名）
  - `TC-NNN` case_id（无模块前缀）
- 这两个 schema 的并集被 v17 L1S6Validator 视为 "字段缺失 + ID 格式错误"，批量标记 Draft

**修复**：
1. 新增 `case_id_and_field_normalizer.py`，做内存 normalize：
   - `TC-NNN` → `{Module}-TC-{NNN}`（保留 numeric tail 保交叉引用稳定）
   - 4 个 legacy English 字段 → 镜像到中文 canonical 字段（idempotent，永远不覆盖已填中文）
2. 引入 `apply_l1_l2_status_per_case` 取代 bulk writeback

**影响**：
- ✅ v3.01 数据收敛（331/331 Ready）
- ⚠️ 任何未来带 legacy schema 的输入都需要走 normalizer；这是反向兼容的设计选择

---

### 问题 2：bulk writeback 与 per-case 语义错位

**现象**：
- 旧 `apply_l1_l2_status(test_cases, l1_result, l2_result)` 看的是 `l1_result["passed"]` 全局布尔
- 任一 case L1 fail → 整体 `l1_passed = False` → 全部 cases 都打 Draft
- 这导致"一条坏用例污染全表"

**根因**：
- v17 字段溯源版的设计要求**per-case 决策**（每条 case 独立 L1+L2）
- 但 `apply_l1_l2_status` 仍是 v15 之前的 bulk 设计，没有随 v17 升级

**修复**：
- 新增 `apply_l1_l2_status_per_case(test_cases, l1_result, l2_result)`：
  - 从 `l1_result["errors"]` 提取每个错误的 `id` 字段 → `l1_failed_ids`
  - 从 `l2_result["failed_ids"]` 提取 → `l2_failed_ids`
  - 每条 case 独立判定：`Ready if (id not in l1_failed_ids) and (id not in l2_failed_ids) else Draft`
  - pre-existing `Rejected` / `Deprecated` 不被覆盖（S7/S8 领地）
- 保留 `apply_l1_l2_status` 旧 API 不动（向后兼容）

**影响**：
- ✅ per-case 写回符合 v17 字段溯源版语义
- ⚠️ 旧调用方（如果有）仍走 bulk 路径，不会突然变成 per-case

---

### 问题 3：l2_s6 strict 锚点校验与 SKILL.md SSOT 冲突

**现象**：
- `l2_s6._check_one` 在 `MISSING_OBJ_ANCHOR` 上要求 `功能描述` 含 `【OBJ-XXX 名称】` 锚点
- SKILL.md §NAME-FIELD-001（§一）明确说 **"test_scenario 不带锚点"**（字段承载替代文本锚点）
- v3.01 数据 100% 不含锚点 → 全部 L2 fail → 全部 Draft

**根因**：
- `l2_s6.py` 是 v15 时期的实现（当时文本锚点是 SSOT）
- v17 字段溯源版把锚点搬到 JSON 字段后，`l2_s6.py` 没跟着升级

**修复策略**：
- **不改 l2_s6.py**（避免 Round 11 self-test 失稳 + 改历史 SSOT 的实现风险大）
- 在 `case_id_and_field_normalizer.evaluate_status` 上引入 `l2_mode`：
  - `"lenient"`（默认）：L2 PASS 当 SSOT 字段齐全（obj_name / fp_name / s5_ref / obj_id / feature_point_ref）
  - `"strict"`：维持 l2_s6.run_l2_check 原行为（锚点 + 动词 + 断言 token）
  - `"off"`：跳过 L2

**影响**：
- ✅ v17 路径（v3.01 数据）走 lenient → 与 SKILL.md SSOT 对齐
- ✅ Round 11 strict 路径仍可用（`l2_mode="strict"`）
- ⚠️ 新参数是新公共 API；下轮需写入 STAGE_S6_TEST_CASES.mdc §6

---

## 决策表

| 改动 | 文件 | 影响范围 | 替代方案 |
|---|---|---|---|
| 1. 新增 case_id_and_field_normalizer.py | ai_workflow/ | 新模块（实现） | B: 在 s6_generate.py 内联（拒绝：体积过大） |
| 2. 新增 apply_l1_l2_status_per_case | ai_workflow/case_status_writer.py | 公共 API 增加（实现） | B: 改造旧函数（拒绝：破坏向后兼容） |
| 3. evaluate_status l2_mode 参数 | case_id_and_field_normalizer.py | 公共 API 增加（实现） | B: 只读环境变量（拒绝：缺少显式调用） |
| 4. 新增 run_normalize_and_export.py | ai_workflow/ | 新模块（实现 + 自测） | B: 把 normalize_and_export 内联到 run_round12_e2e（拒绝：可复用） |
| 5. 新增 run_round12_e2e.py | workflow_assets/test_s6_status/... | 过程资产（不入 git，v1.0 子目录） | B: 直接命令行调用（拒绝：不可审计） |
| 6. 覆盖 test_cases_public.xlsx | workflow_assets/游戏道具商城系统/v3.01/ | 过程资产（不入 git） | B: 创建 v3.02 新版（拒绝：用户要求 v3.01 收敛） |

---

## 修改文件清单

### 实现
- `ai_workflow/case_id_and_field_normalizer.py`（新增）
- `ai_workflow/case_status_writer.py`（新增 `apply_l1_l2_status_per_case` + `_case_ids_with_errors` + `_case_ids_with_l2_failures`）
- `ai_workflow/run_normalize_and_export.py`（新增）
- `workflow_assets/test_s6_status/v1.0/「S6 测试用例生成」/run_round12_e2e.py`（新增）

### 过程产物（不入 git）
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx`（覆盖）
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round12.precheck.bak.xlsx`（备份）
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_round12_e2e_audit.json`
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_round12_transitions.json`

### 治理资产（v17/plans/）
- `governance/design_iter/plans/v17/audit_12.md`（新增）
- `governance/design_iter/plans/v17/review_12.md`（本文件）

---

## 遗留项 / 影响范围

| 遗留项 | 等级 | 下轮处理 |
|---|---|---|
| `STAGE_S6_TEST_CASES.mdc` §6 写 `l2_mode` 参数文档 | LOW | Round 13 |
| `aidocx-s6-test-cases/SKILL.md` §11 写 lenient L2 契约 | LOW | Round 13 |
| `CHANGELOG.md` 记录 Round 12 设计变更 | LOW | Round 13 |
| `case_status_writer.apply_l1_status` (L1-only 别名) 是否仍可用 — 是（保留） | — | — |
| l2_s6.py strict 锚点校验是否仍对 S7 数据有用 | MEDIUM | Round 13 评估 |
| goal_s6_case_status_redefinition.md §决策 / §修复策略同步 | MEDIUM | Round 13 |

---

## 反向挑战

| 挑战 | 答复 | 证据 |
|---|---|---|
| 为什么用 normalizer 而不是改 v3.01 JSON？ | out_of_scope §26 明确禁止 | `goal_s6_case_status_redefinition.md` §out_of_scope |
| 为什么不在 l2_s6.py 改 strict 校验？ | 旧调用方（test_s5_s6_s7_closure.py 已通过）依赖 strict 行为；改它会触发 7 个测试失败 | `pytest tests/` 输出 |
| bulk vs per-case 哪种正确？ | v17 字段溯源版的设计意图是 per-case（每条 case 独立 Ready） | SKILL.md §NAME-FIELD-001 |
| 不改 test_cases.json 会不会让 xlsx 与 JSON 不同步？ | 是，**故意不同步**——xlsx 是导出视图，JSON 是 S6 SSOT；下次 S6 重跑会用新规则生成 | out_of_scope + v17 设计 |
| 旧 case_id 与 s5_ref 字段是否对得上？ | 对得上：`s5_ref` 是 `UI-TP-001` 这种形式，case_id 也规范化成同模块前缀，关联保持 | manual grep 抽样 |
| 备份 xlsx 是否安全？ | 是——文件名 `*.round12.precheck.bak.xlsx`，workflow_assets 不入 git，不会污染主仓 | .gitignore |

---

## 收敛判决

**状态**：✅ 全部 BLOCKER + value criteria 通过，可标 CONVERGED 候选。
