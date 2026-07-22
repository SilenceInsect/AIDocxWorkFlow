# DT-v302-001 — v3.02 Goal 与 v3.01 现状错位决策

## 触发反模式（GL-007）

- ❌ **"没有证据却给通过结论"**（执行前的 V-001/V-003/V-004 描述基于用户记忆草稿，未 Read 现状）
- ❌ **"验收标准在执行中被静默删除、弱化或替换"**——若继续按原 task_queue 执行 = 修不存在的 bug（伪造工作量）

## 断点

`4c1eedec` Goal 的 R=0 阶段进入 Act 前实测：

| V 项 | 描述 | 实测现状 | 判定 |
|---|---|---|---|
| V-001 | 87 TC ID 在模块内连续无跳号 | test_cases.json 331 TC 1-331 全连续；xlsx 87 TC BIZ 1-64 + LOG 1 + SPECIAL 1-3 + UI 1-19 全连续，**gap=0** | **PASS**（v3.01 Round 18 已修复）|
| V-002 | 16/16 OBJ 每 OBJ ≥ 1 P0 | 12/16 OBJ 0 P0（75% OBJ 缺）| **FAIL**（仍存在）|
| V-003 | expected_results 去重保序 | 111/331 TC 字面重复（33.5%），但远低于 v3.02 草稿"72/87"数字 | **PARTIAL**（程度低于预期，且 V-003 描述数字错误）|
| V-004 | OBJ-02 块 row 27/28 B 列有值 | Row 26 B='BIZ'（首行），row 27/28 是 merged cell None——**正确 merge 行为** | **PASS**（非 bug）|

**结论**：8 项问题（用户草稿）中实际仍成立仅 1 项（V-002）。其余 3 项 BLOCKER 已 PASS，4 项 MAJOR 待复测。

## 根因假设

1. **用户草稿记忆偏差**：v3.02 Goal 文本基于更早的 Round N 审计，Round 17/18 修复后未及时同步。
2. **任务队列未做现场 Read 即固化**：Plan 阶段 task_queue 5 项基于描述写入，未 Read v3.01 Round 18 报告做事实校验。
3. **DNA §9.4 "先验后答"**违反——Act 起步才 Read 文件，Plan 阶段未先 Read v18 报告 + 实测基线。

## 候选行动

| 选项 | 描述 | 影响 |
|---|---|---|
| A. 立即收敛 converged_with_followup | 仅 V-002 一项 BLOCKER 待修；其余降级为 follow_up_items；重新启动 v3.03 仅修 V-002 | 工作量最准；闭环快 |
| B. 重写 task_queue 仅修 V-002 | 把 T-001/T-002/T-003 移除；保留 T-004（OBJ 风险矩阵）+ T-005（重导验证）| 中等改动 |
| C. 强修 V-001/V-003/V-004（即使已 PASS）| 按原 plan 跑完全部 5 子任务 | **❌ 违反 SKILL §5 反模式**："为通过检查而修改正确事实" |

## 选择与依据

**推荐：A（立即 converged_with_followup）**——
- **核心论据**：3/4 项 BLOCKER 已 PASS，**继续修不存在的 bug = 伪造工作量**
- **闭环质量**：V-002 仍 FAIL → 必须收敛；写明 V-002 转 v3.03 follow_up
- **避免反模式**：方案 B/C 都触发 SKILL §5 反模式扫描（伪造工作量 / 改正确事实）
- **follow_up_items 机制（GL-002）**：v1.1 SKILL.md §9 明确"带遗留收敛"合法

## 执行结果（待用户确认后填）

- [ ] 用户拍板 A/B/C
- [ ] 根据选择更新 snapshot.task_queue + value_criteria
- [ ] 写 CONVERGED（或 REPAIRING）
- [ ] 反模式案例写 antipattern_cases.jsonl

## 验证证据

- Read `governance/design_iter/plans/v18/round18_audit_round18.md` 全文
- 实测 `test_cases.json` 331 TC ID 1-331 全连续
- 实测 xlsx 87 TC 4 模块内全连续，gap=0
- 实测 16 OBJ P0 数：12 OBJ = 0 P0（BIZ-BACKEND/PROMO/ORDER/VIP 大部分 + UI 全）

## 恢复点

如用户选 C，撤回本 DT，回到 Round 1 Act 强修（不推荐）。
如用户选 B，重写 task_queue，进入 Round 2。
如用户选 A（推荐），写 audit_1 + review_1 + CONVERGED。
