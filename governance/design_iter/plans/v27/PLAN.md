# PLAN — v27 AI 自治规则放宽 v1（AI 自治规则放宽 v1）

**版本**: v27
**状态**: 🟡 active
**Goal ID**: 9b1ca386-de47-4d0a-bd60-0206781429be
**创建时间**: 2026-07-20
**承接**: v27 GOAL.md（用户拍板版） + v26 PLAN（草案，已精审）

---

## 解决（4 个高优动作）

| ID | 动作 | 来源 | 当前状态 |
|----|------|------|----------|
| B1 | DESIGN_AND_EXECUTION_STANDARDS.mdc §2.3 改索引指向 §4.3（§4.3 唯一阈值 SSOT） | v26 草案 C 组 | ⏸ 待 T-101 跑 |
| C1/A2 | dna_decision_density_check.py docstring 默认值改 5 + README env 覆盖说明 | v26 草案 C 组 | ✅ **已落地**（line 45 = 5）—— T-102 验证 + 补 README |
| C2 | session_resume_multi_goal.py 保留不注册（goal_loop_hook.py:62-83 已实现单 goal） | v26 草案 C 组精审 | ✅ **决策已定**（v27 GOAL §1 第 3 行）—— T-103 守卫 |
| C4 | before_prompt_dna_check.py 注入文本 3 问 → 5 问对齐 DNA_3Q_CHECK.mdc §1 | v26 草案 C 组 | ✅ **GOAL 标已完成**—— T-104 验证 |

## 新增

| ID | 内容 | 位置 |
|----|------|------|
| N1 | v27 治理档（GOAL.md + PLAN.md + audit/review/CONVERGED） | governance/design_iter/plans/v27/ |
| N2 | snapshot.json 18 字段 v1.1 schema | .goal-log-db/active/9b1ca386.../ |
| N3 | out_of_scope.md v1.1 强制 | .goal-log-db/active/9b1ca386.../out_of_scope.md |

## 遗留（转下轮）

| ID | 项 | 承接 |
|----|----|------|
| L1 | v17 5 项约束放宽（fp_name / steps[] / test_method[] / tp_reference / preconditions[]） | v28 |
| L2 | D1-D3 goal-loop 早期约束放宽 | v29 |
| L3 | B2/B4 业务门禁放宽（A 组中优 / E 组）+ A1/A3/A4/B3 内部冗余合并 | v30 |

---

## 决策表（每个 T 子任务）

### T-101 [BLOCKER] V-101 + V-102 B1
- 文件：`.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`
- 改：§2.3「Quality Gate Thresholds」段开头加"🚨 强制阅读指令"引用 §4.3 唯一阈值源；删除 §2.3 表中所有具体阈值数字（保留类型枚举名 P0/P1/P2/.../P3）；§11.3 若有阈值表则同步改索引
- 影响：阅读 SSOT 路径变更（从 §2.3 移到 §4.3）
- 替代方案：B 不动 §2.3（违反 v27 §1 第 1 行决策，**禁止**）
- 反模式：❌ §2.3 仍列数字 = BLOCKER；§11.3 重复出现数字 = BLOCKER

### T-102 [MAJOR] V-103 C1/A2
- 文件 1：`dna_decision_density_check.py` line 45 已 = 5（**先验已确认**）—— T-102 仅补 docstring 显式标注 + 注释中说明 v27 来源
- 文件 2：`README.md`（hooks 目录）新增段"## 阈值覆盖"，示例 `DNA_DECISION_DENSITY_THRESHOLD=5`
- 验证：`python3 -m py_compile .cursor/hooks/dna_decision_density_check.py` + `--self-test`

### T-103 [BLOCKER] V-104 C2 守卫
- 文件：`.cursor/hooks.json`
- 决策：**不动 hooks.json**（C2 决策保留不注册，避免与 goal_loop_hook.py:62-83 双注入）
- 任务实质：grep `session_resume_multi_goal.py` → 不出现 → 写守卫审计记录（v27/C2.md）
- 反模式：❌ 私自注册 = BLOCKER（违反 v27 §1 第 3 行精审决策）

### T-104 [BLOCKER] V-105 C4
- 文件：`.cursor/hooks/before_prompt_dna_check.py`
- 验证：grep 5 个关键词 (一致性 / 设计 / 全局 / 约束 vs 知识 / 人本可审查) vs `DNA_3Q_CHECK.mdc §1` 5 问
- 跑：`python3 .cursor/hooks/before_prompt_dna_check.py --self-test` 必须 4/4 PASS
- 反模式：❌ 3 问残留 = BLOCKER；未跑 self-test 提交 = BLOCKER

### T-105 [MAJOR] V-106
- 文件 1：`governance/design_iter/INDEX.md` — current = v27 + 1 行摘要
- 文件 2：`CHANGELOG.md` — 新增 v27 段（4 动作 / 3 文件 / 0 commit）

### T-106 [MAJOR] V-107
- 回归基线：跑 v3.01 L1 + L2 校验脚本（`l1_s6.py` / `l2_s6.py`）
- 断言：与 v3.01 baseline 比对 fail 数不增
- 反模式：❌ 阈值调整引入新 fail 不识别 = BLOCKER

---

## 反模式熔断（DNA §5）

| 反模式 | 触发动作 |
|--------|----------|
| §2.3 / §4.3 / §11.3 任一处出现非索引指向 SSOT 的硬编码 | BLOCKER：撤销 + DT-v27.1 |
| hook 改动未跑 self-test 提交 | BLOCKER：撤销 + DT-v27.2 |
| C2 被偷改为已注册 | BLOCKER：撤销 + DT-v27.4（违反 v27 §1 精审决策） |
| v17 5 项约束在本轮被私自处理 | BLOCKER：撤销 + DT-v27.3 |
| 单轮改动 ≥ 5 文件（v27 §4 豁免到 ≤ 4） | BLOCKER：列决策表 + ask |
| 缺 Read 目标文件就改 | MAJOR：DNA §9.4 违规 |
| 阈值变更不留 CHANGELOG 记录 | BLOCKER：补档 |
| 把"v26 草案未拍板项"当"已发布硬约束" | BLOCKER：写 DT 决策 |

---

## v27 ↔ v17/v18/v19/v26 关系

| 版本 | 关系 |
|------|------|
| v17 | 已 CONVERGED；本轮**不动** v17 阶段产物（v17 5 项约束由 v28 接办）|
| v18-v22 | 已归档；本轮**不动**其索引 |
| v25 | 已归档；本轮**不动** |
| v26 | 草案状态（plan-only）；v27 是其落地轮 |
| v27 | **本轮 current**（完成后 v27 = current）|

---

## 落档协议

- 本档：governance/design_iter/plans/v27/PLAN.md（已落档）
- snapshot：.goal-log-db/active/9b1ca386.../snapshot.json（已落档）
- out_of_scope.md：同 dir（已落档）
- audit_round1.md：T-105/T-106 完成后产出
- review_round1.md：Audit 后产出
- CONVERGED.md：Round 1 收敛后产出（achieved 或 converged_with_followup）
