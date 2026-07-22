# v27 GOAL — AI 自治规则放宽 v1（强目标导向）

> **本档定位**：v26 草案的用户拍板落地轮 — **4 个高优动作**精准执行
> **基线**：`governance/design_iter/plans/v26/PLAN_dialectic_ai_constraints_relaxation.md`（已落档 + C 组已精审）
> **承接**：v17 阶段 5 项卡 AI 自治约束（v27 carry 第 2 阶段再开子任务）

---

## 1. 一句话目标

把 `v26/PLAN` 拍板的 **4 个高优动作**精准落地：

1. **B1** 阈值 SSOT 合并：`DESIGN_AND_EXECUTION_STANDARDS.mdc §2.3` 速查表改"读 §4.3"索引（§2.3 仅保留门禁类型/判定文字，不列阈值）；§4.3 唯一阈值常量源
   - **精修**（2026-07-19 grep 实测）：子任务原称"§2.3 + §4.3 + §11.3 三处重复"——**DESIGN 文件只有 §2.3 + §4.3 两处**，§11.3 不存在。**改动面从 3 处变 2 处**
2. **C1/A2** 决策密度阈值 docstring 改 5（`dna_decision_density_check.py` 源码支持环境变量，不改源码）
3. **C2** `session_resume_multi_goal.py` **保留不注册**（精审发现 `goal_loop_hook.py:62-83` 已实现 sessionStart v1 单 goal；双注册会双注入；本轮决策 = 不动 hooks.json，v28+ 合并）
4. **C4** `before_prompt_dna_check.py` 注入文本 3 问 → 5 问对齐 `DNA_3Q_CHECK.mdc §1`（**已完成**）

> **德鲁克目标导向**：**少即是好**——4 个动作，对应 4 个目标；不是 25 条全做。

---

## 2. 范围

### In Scope（v27 本轮）

- `DESIGN_AND_EXECUTION_STANDARDS.mdc`：阈值 SSOT 三处合并
- `.cursor/hooks/dna_decision_density_check.py`：改 docstring 默认值 + 补 README
- `README.md`（hooks 目录）：新增阈值覆盖说明
- `.cursor/hooks.json`：补注册 `session_resume_multi_goal.py` 到 sessionStart
- `.cursor/hooks/before_prompt_dna_check.py`：注入文本 3 问 → 5 问
- `INDEX.md` + `CHANGELOG.md`：v27 = current + 4 个动作摘要

### Out of Scope（v27 不做，等下轮）

- v17 阶段 5 项约束（fp_name / steps[] / test_method[] / tp_reference / preconditions[]）→ v28 carry
- D1-D3 goal-loop 早期约束放宽 → v29 carry
- B2 / B4 业务门禁放宽（A 组中优 / E 组）→ v30 carry
- 中优 A1/A3/A4/B3 内部冗余合并 → v30 carry

---

## 3. 完成判定（验收标准）

- [ ] `DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3` 仍是**唯一**阈值定义处；§2.3 与 §11.3 改"读 §4.3"索引
- [ ] `dna_decision_density_check.py` docstring 默认值改 5；`python3 -m py_compile` 通过；`--self-test` 通过
- [ ] `hooks.json#sessionStart` 含 `session_resume_multi_goal.py` 4 条
- [ ] `before_prompt_dna_check.py` DNA_3Q_CHECK 文本与 `DNA_3Q_CHECK.mdc §1` 5 问一一对应；`--self-test` 4/4 通过
- [ ] `INDEX.md` current = v27 + 1 行进度摘要
- [ ] `CHANGELOG.md` 新增 v27 段
- [ ] 跑 v3.01 验证：L1∧L2 校验脚本不报新 fail

---

## 4. 反模式（DNA 执行版硬约束）

- ❌ 单 turn 改 ≥ 3 个文件（v26 §9.1 红线，**本轮豁免到 ≤ 4** 因 4 个动作必须在同闭环验证）
- ❌ 跳过 Read 目标文件
- ❌ 阈值变更不留 CHANGELOG 记录
- ❌ 把"v26 草案未拍板项"当"已发布硬约束"
- ❌ 把"精审后的修订判断"当"原文未改"——必须 StrReplace + Read 验证

---

## 5. 落档协议

- 本档已落档（governance/design_iter/plans/v27/GOAL.md）
- v27 PLAN.md（任务分解 + 反模式）后置生成
- 4 个动作每完成一个必 run self-test（hook）/ py_compile（py）

---

## 6. 反模式熔断（DNA §5）

触发下述任一 → 立即暂停 + 创建 DT-v27.x 决策任务：

- 阈值在 §2.3 / §4.3 / §11.3 任一处出现 **非索引指向 SSOT** 的硬编码
- hook 改动未跑 self-test 提交
- 补注册到 hooks.json 后未验证 IDE 会话启动不报错
- v17 5 项约束在本轮被私自处理（明确 Out of Scope）

---

## 7. v27 与 v17 / v18 / v19 / v26 关系

| 版本 | 关系 |
|---|---|
| v17 | 已 CONVERGED；本轮**不动** v17 阶段产物（v17 5 项约束由 v28 接办）|
| v18-v22 | 已归档；本轮**不动**其索引 |
| v25 | 已归档；本轮**不动** |
| v26 | 草案状态（plan-only）；v27 是其落地轮 |
| v27 | **本轮 current**（完成后 v27 = current）|
