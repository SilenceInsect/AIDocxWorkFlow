# Goal: Round 15 遗留 follow_up + Round 16 用例描述/功能描述格式治理立项

> **本档是 q_decision_table 占位骨架（DNA §9.5 落档协议）**。
> **新 goal_id**：`6d3edb03-352d-4a3f-921c-b880db0625f5`
> **触发源**：Round 15 §11.5 遗留 follow_up 4 项 + Round 16 用户新诉求「用例描述/功能描述格式治理」。
> **状态**：⏸️ **GOAL PAUSED**——等待用户审核本 Plan 后启动 goal-loop 推进。

---

## 1. 立项范围（合并 5 个待办）

### 1.1 来源 A：Round 15 §11.5 遗留 follow_up（4 项）

| # | 遗留项 | 等级 | 修复方向 |
|---|---|---|---|
| FU-A1 | normalizer `mirror_bilingual_aliases` 把 list 错误 join 成字符串 bug | MAJOR | 修 normalizer + 加 self_test |
| FU-A2 | SSOT §11 拆约束对象（LLM 生成约束 vs 数据存储约束）| MAJOR | v3.02 治理 |
| FU-A3 | 合并 TC 加 `source_case_ids` 追溯字段 | MINOR | merger 加字段 |
| FU-A4 | v3.01 数据 step/expected 错位 | MINOR | v3.02 prompt 治理 |

### 1.2 来源 B：Round 16 用户新诉求（格式治理）

| # | 诉求 | 等级 | 修复方向 |
|---|---|---|---|
| FU-B1 | **用例描述 / 功能描述 字段格式治理** | MAJOR | xlsx 排序（按 OBJ→FP）+ Sheet 2「用例描述索引」+ 同 OBJ 同色背景 + 空行隔离 |
| FU-B2 | **测试设计原则落档**：1 OBJ 下多 FP / 1 FP 下多前置条件 / 1 前置下多步骤 → 多 TC | MAJOR | SSOT §11 加测试设计层级原则段 |

### 1.3 来源 C：本 Goal 自带过程合规（3 项）

| # | 项 | 等级 |
|---|---|---|
| FU-C1 | 全部 follow_up 落地后维护 snapshot status + V/P 重算 | MAJOR |
| FU-C2 | Round 17 audit + review + CONVERGED.md 落档 | MAJOR |
| FU-C3 | 不修改 v3.01 test_cases.json（继承 Round 12 out_of_scope §10）| MAJOR |

---

## 2. 现状证据（关键行号 + 1 行现状）

| 文件 | 行号 | 现状 |
|---|---|---|
| `ai_workflow/case_id_and_field_normalizer.py` | L156-176 | `mirror_bilingual_aliases` 把 list 字段 join 成字符串 → 丢多元素语义（Round 15 §3 根因 C）|
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | L569-570 + L1108-1109 | 单步原则 + Round 15 例外条款已落 |
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | L109 | 单预期原则 + Round 15 例外条款已落 |
| `ai_workflow/test_case_formatter.py` | L761-776 | field_mapping 已扩展 `expected_results` / `preconditions` plural |
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` | 主表 88 行 | 87 条合并 TC × 全部 Ready，但未按 OBJ→FP 分组排序 |
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` | 11311 行 | v3.01 数据 331 条单步 TC + step/expected 错位 + 多个 obj 含多个 fp（2~5 个）|

---

## 3. 决策表（DNA §9.5 占位 · 待用户审核后启动 Act）

| # | 文件 | 改动 | 替代方案 |
|---|---|---|---|
| 1 | `ai_workflow/case_id_and_field_normalizer.py` L156-176 | 修 `mirror_bilingual_aliases`：list 字段保持 list 不 join | A. 改 merger sync（已 Round 15 实现，但绕过 normalizer 不彻底）/ B. 推迟 v3.02 |
| 2 | `ai_workflow/case_id_and_field_normalizer.py` self_test | 加 case：list 字段不 join | 必须项 |
| 3 | `ai_workflow/scenario_group_merger.py` | 加 `source_case_ids` 字段（合并 TC 标注 source TC id list）| A. 不加（用户未明确要求）/ B. 加字段 + formatter 渲染 |
| 4 | `ai_workflow/test_case_formatter.py` | 加 Sheet 2「用例描述索引」：列 OBJ / FP 数 / TC 数 / Ready 数；按 OBJ 聚合计数 | A. 不加 Sheet 2（仅靠排序）/ B. 加 Sheet 2 + 加 Sheet 3 同 OBJ 分组 |
| 5 | `ai_workflow/test_case_formatter.py` | 主表行按 `obj_id` → `feature_point_ref` → `case_id` 排序 + 同 OBJ 同色背景 + OBJ 边界插空行 | A. 仅排序不加背景/B. 排序 + 背景 + 空行（推荐）|
| 6 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §11 | 加测试设计层级原则段：1 OBJ 多 FP / 1 FP 多前置 / 1 前置多步骤 → 多 TC | 必须项 |
| 7 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §11 | 同步 SKILL.md §11 测试设计层级原则 | 必须项 |
| 8 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` | **本 Goal 核心审查对象** — 重导出（合并 + OBJ→FP 分组 + Sheet 2 索引）| 唯一目标 |
| 9 | `governance/design_iter/current/goal_round16_followup_and_format.md` | 本档追加 Act 执行记录 | 必须项 |
| 10 | `governance/design_iter/plans/v17/audit_16.md` + `review_16.md` + `CONVERGED.md` | 本轮 audit + review + 收敛报告 | 必须项 |
| 11 | `.goal-log-db/active/6d3edb03-352d-4a3f-921c-b880db0625f5/snapshot.json` | 新 Goal 快照（status=active；loop_round=1；plan 已落档）| 必须项 |
| 12 | `.goal-log-db/active/6d3edb03-352d-4a3f-921c-b880db0625f5/out_of_scope.md` | 新 Goal 禁区清单 | 必须项 |

**§9.1 红线**：12 项改动 > 红线 3。业务文件 5 项（normalizer 修 + merger 加字段 + formatter 加 Sheet/排序/背景 + SKILL.md + .mdc），其余为落档/产物豁免。**本轮父会话 full_chain 授权等同批量改**。

---

## 4. out_of_scope.md（GL-003 强制）

### 4.1 功能禁区

- 不重生成 v3.01 test_cases.json（继承 Round 12 out_of_scope §10）
- 不重跑 S5/S6 prompt 治理（推 v3.02 单独治理）
- 不修改 S7 review_report schema（与本 Goal 无关）
- 不改 stage_gatekeeper / coverage_validator（与本 Goal 无关）

### 4.2 技术栈禁区

- 不引入新依赖（如 pandas / xlsxwriter）—— 沿用 openpyxl
- 不改 `apply_l1_l2_status` / `apply_l1_l2_status_per_case` 行为契约
- 不动 L1S6Validator / L2S6Validator 校验规则
- 不动 v17 单步原则的 LLM 生成约束语义（仅加同源合并例外 + 测试设计层级原则）

### 4.3 职责边界禁区

- 不修复 v3.01 数据 step/expected 错位（推 v3.02 prompt 治理；属 FU-A4）
- 不动 auto_reviewer / S7 审查链路
- 不动 S5 test_points.json / S2 requirement_objects.json / S3 prototype.json
- 不 commit（用户明确禁止）

---

## 5. 启动条件

1. 用户审核本 Plan 通过
2. 用户对「Sheet 2 用例描述索引 + 主表 OBJ→FP 分组排序 + 同 OBJ 同色背景」三个格式细节确认（如不确认则退回 default 排序 + 不加 Sheet 2）
3. 用户对 value_ratio 是否放宽（V=6 / P=4 → ratio=0.6 恰好达标；无放宽需要）

---

## 6. 落档协议执行记录

### 6.1 Round 16 Plan 阶段（2026-07-19 · 当前轮）

- 文件改动：1（current/ 全文新建）+ 1（`.goal-log-db/active/6d3edb03.../snapshot.json`）+ 1（`out_of_scope.md`）
- 核心动作：合并 Round 15 §11.5 遗留 follow_up 4 项 + Round 16 新诉求 2 项 → 12 项决策表
- **value_ratio 预估**：V=6 / P=4 / ratio=6/10=0.6 恰好达标
- **goal_signature**：（待 snapshot.json 落档时生成）
- **下一步等待**：用户审核本 Plan + Sheet 2 格式细节确认 → 启动 Act 阶段

