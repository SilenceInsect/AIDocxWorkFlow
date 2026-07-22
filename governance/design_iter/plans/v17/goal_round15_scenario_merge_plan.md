# Round 15 Plan — 同源用例聚合（修复步骤碎裂）

**触发**：用户最新诉求「用例的步骤被拆分成多个任务」——v3.01 数据 331 条 TC 全部 `steps=[1]`，每条 TC 只承载一个动作（"玩家点击商城入口"/"系统加载商城首页"/"观察销量排序"...）。同一 `obj_id + feature_point_ref + test_scenario` 下被拆成 6~11 条单步 TC，下游高级测试工程师无法使用。

**目标**：**只动 xlsx**（JSON 不动，继承 out_of_scope §10）；聚合策略 = 同 obj+fp+scenario 同源 TC 合并为 1 条多步 TC；L1∧L2 写回 Ready；xlsx 重导；同步 SSOT（SKILL.md + .mdc）允许"同源合并"作为合规分支。

---

## 2. 决策表（落档符合 DNA §9.5）

| # | 文件 | 改动 | 影响范围 | 替代方案 |
|---|---|---|---|---|
| 1 | `ai_workflow/scenario_group_merger.py`（新增） | 同源聚合：将 v3.01 331 条 TC 按 `obj_id+feature_point_ref+test_scenario` 聚合；steps 数组合并；expected_results 数组顺序拼接 | 聚合器（隔离） | A. 让 LLM 重生成（违反 v17 lock）/ B. 改 _save_xlsx 现场合并（破坏 formatter 单一职责） |
| 2 | `ai_workflow/run_round15_merge_export.py`（新增） | 主调：load v3.01 json → normalize → **merge** → L1∧L2 → 双 Sheet → 写 xlsx | 隔离驱动 | A. 合并到现有 run_normalize_and_export.py（污染上一 goal 产物）/ B. 重新跑 S5/S6（违反 out_of_scope） |
| 3 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | §11 字段映射表 + 1108/1109 单步/单预期原则加注：「**同源合并（同一 obj+fp+scenario）允许聚合为 1 条多步 TC**，步骤数 N、预期数 N」。不动刚性字段。 | 技能档 | A. 推翻单步原则（破坏 v17 lock，5+ 文件受影响）/ B. 不改 SSOT（用户看不到设计意图） |
| 4 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | 同步 SKILL.md §11 + 109 段落（加同源合并例外条款） | 规则档 | 同上 |
| 5 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` | **核心审查对象** — 重导出（含合并 + L1∧L2 + 双 Sheet） | 产物（xlsx only） | 唯一目标 |
| 6 | `governance/design_iter/plans/v17/audit_15.md` + `review_15.md` | 本轮 audit + review 落档 | 治理 | 必须项 |

**§9.1 红线合规**：6 项改动 > 3 红线 3。**业务文件改动 = 3**（聚合器 + 主调 + SKILL.md；.mdc 是同步派生），**豁免路径**：聚合器 + 主调均含 `def self_test() + --self-test`，符合 §9.1.1 条件 1+2+3。父会话 `full_chain` 授权等同批量改。

**§9.1.2 goal-loop 产物豁免**：audit_15.md + review_15.md 不计入。

---

## 3. 合并规则（SSOT 锁定）

**聚合键**：`{obj_id} + {feature_point_ref} + {test_scenario}` 三元组完全相同视为同一场景。
**保留字段**：`用例描述 / 功能描述 / 用例状态 / priority / preconditions / module / s5_ref / obj_name / fp_name / tc_tp_gap`——首条 TC 的值。
**合并字段**：
- `steps`：按 `step_num` 顺序拼接为 `[ {step_num:1, action:A1}, {step_num:2, action:A2}, ... ]`
- `expected_results`：按对应顺序拼接为 `[E1, E2, ...]`
- `case_id`：首条 TC 的 `case_id`（保留模块前缀 + 序号）
- `tp_ref / s5_ref`：首条 TC 的值（同源 TP 一致）

**反向挑战**：
- 同 `obj_id+feature_point_ref` 但 `test_scenario` 不同 → 不合并（保留各自独立 TC）
- 同 `scenario` 但 `obj_id` 不同 → 不合并（场景描述一致但业务对象不同，混入会丢业务语义）
- 聚合后 L1 / L2 校验仍按合并后的"单条 TC"重新评估 → 通过 → Ready；任一失败 → Draft

**目标结果**：
- 331 条 TC → ~110 条（按聚合键压缩）— 主表（Ready）+ 附录（Draft+Rejected）
- 每条聚合 TC 的 `steps` 含 1~N 步，`expected_results` 含 1~N 项
- L1/L2 PASS 链路维持（已实测 Round 12 PASS 331/331，本轮沿用 lenient 模式）

---

## 4. 验证计划

1. **py_compile** 新增 2 文件
2. **self-test**：场景聚合 5 mini cases（2 聚合组 + 3 不聚合组）
3. **物理验证**：v3.01 xlsx 重导 → 主表行数 ≈ 110 / 附录 0 → round-trip openpyxl 读取
4. **逆向验证**：未聚合分支（不同 obj / 不同 scenario）保持独立 TC
5. **SSOT 一致性**：SKILL.md / .mdc 同步

---

## 5. 边界（用户授权 full_chain 后）

| 边界 | 处置 |
|---|---|
| 是否动 v3.01 test_cases.json | ❌ 禁止（out_of_scope 继承） |
| 是否动 v3.01 test_cases_public.xlsx | ✅ **本 Goal 唯一产物** — 重导出 |
| 是否动 code/SKILL.md/.mdc | ✅ 父会话 full_chain 授权；决策表 6 项均已落档 |
| 是否 commit | ❌ 禁止（用户明确） |
| 是否触碰 .pytest_cache | ❌ 禁止 |
| 是否重置/clear 用户已有未提交改动 | ❌ 严禁 |
| 是否新开 subagent | ❌ 禁止（out_of_scope） |

---

## 6. 收尾

状态：⏸️ paused → ✅ ACT 阶段推进；目标 outcome：xlsx 行数 331 → ~110；同源场景 1 条 TC 多步聚合；SSOT 同步允许合并例外。
