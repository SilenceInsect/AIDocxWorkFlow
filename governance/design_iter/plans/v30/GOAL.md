# v30 GOAL — v26 真实缺口闭环 + 一致性修复

> **本档定位**：v26 AI 自治规则整治草案的最终落地轮 — 修复规则 / Hook / 代码三方不一致
> **基线**：
> - v26 草案（`governance/design_iter/plans/v26/PLAN_dialectic_ai_constraints_relaxation.md`）
> - v27 CONVERGED（4 高优动作）
> - v28 CONVERGED（9 DT 决策）
> - v29 CONVERGED（8 follow_up 落地）
> - **当前 SKILL.md 实测**：255 行，§2 无 value_ratio / goal_signature_changelog，§3.4 无 Review 双档
> - **v28/v29 CONVERGED 错误引用**：声称 SKILL.md 有 498 行、§2.1/§3.2/§3.4 及相应字段，但实测文件只有 255 行且无这些章节

---

## 1. 一句话目标

修复 v26 草案落地过程中的 5 个真实缺口，同时纠正 v28/v29 DT 决策中关于 SKILL.md 行号和内容的错误引用：

1. **A2/C1**：DNA §9.1 决策密度 ≤ 3 → ≤ 5，与 hook 默认阈值 5 对齐
2. **D1**：goal_snapshot `MIN_VALUE_RATIO` 0.6 → 0.5（启动软指导），收敛判定维持 0.6
3. **D2**：goal_snapshot `MIN_SIGNATURE_SIMILARITY` 0.7 → 0.5 + 新增 `goal_signature_changelog[]` 字段
4. **D3**：SKILL.md 新增 §2.1（value_ratio 软指导）+ §3.2（goal_signature 校验）+ §3.4（Review 双档）
5. **B2/B4 口径**：DESIGN §4.3 例外率统计口径注明"实际触发分母"

---

## 2. 当前状态快照（实测 vs 声称）

| 项 | v28/v29 声称 | 实测文件内容 | 来源 |
|---|---|---|---|
| SKILL.md 行数 | 498 行 | **255 行** | Read 实测 |
| SKILL.md §2.1 | 有 value_ratio 约束 | **不存在** | Read 实测 |
| SKILL.md §3.2 | 有签名校验段 | **不存在** | Read 实测 |
| SKILL.md §3.4 | 有 Review 双档 | **不存在** | Read 实测 |
| SKILL.md schema | 18 / 20 字段 | **10 字段** | Read 实测 |
| goal_snapshot.py | `goal_signature_changelog[]` 已加 | ✅ 已有 | Read 实测 |
| goal_snapshot.py | `MIN_VALUE_RATIO = 0.6` | ✅ 确认 | Read 实测 |
| goal_snapshot.py | `MIN_SIGNATURE_SIMILARITY = 0.7` | ✅ 确认 | Read 实测 |
| DNA §9.1 | 决策密度 ≤ 5 | **≤ 3** | Read 实测 |
| Hook 阈值 | 默认 = 5 | ✅ 确认 | Read 实测 |

**根因**：v28/v29 DT 决策引用了不存在的 SKILL.md 行号（声称 498 行，实测 255 行），导致所有涉及"修改 SKILL.md §2.1/§3.2/§3.4"的 DT 决策实际上从未执行。本轮直接修复 SKILL.md，绕过错误引用。

---

## 3. 范围

### In Scope（本轮 v30）

- `DNA_3Q_CHECK.mdc` §9.1 — A2/C1 一致性修复
- `ai_workflow/goal_snapshot.py` — D1/D2 常量修复 + schema 字段新增
- `.cursor/skills/goal-loop/SKILL.md` — 新增 §2.1/§3.2/§3.4 章节
- `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 — B2/B4 口径注明
- `governance/design_iter/INDEX.md` + `CHANGELOG.md` — v30 段更新

### Out of Scope

- Hook 源码逻辑本身（`dna_decision_density_check.py` 等）—— 不改
- S6 Skill / Rule / 验证器（v17 5 项放宽已完成）
- B2/B4 统计口径重构（B2 驳回维持 20%/40%；B4 驳回维持 100%）—— 仅注明，不重构
- v28/v29 CONVERGED.md 原文—— 不修改历史归档
- knowledge/public/ — Agent 不得直接入库

---

## 4. 完成判定（验收标准）

- [ ] DNA §9.1 阈值改为 ≤ 5（与 hook 5 对齐）
- [ ] goal_snapshot `MIN_VALUE_RATIO = 0.5`（启动软指导）；`MIN_VALUE_RATIO_HARD = 0.6`（收敛判定硬约束）
- [ ] goal_snapshot `MIN_SIGNATURE_SIMILARITY = 0.5`（软指导）
- [ ] goal_snapshot schema 含 `goal_signature_changelog[]`（已存在，验证存在性）
- [ ] SKILL.md 新增 §2.1 value_ratio 软指导说明
- [ ] SKILL.md 新增 §3.2 goal_signature 校验说明
- [ ] SKILL.md §3.4 Review 注明双档（轻量 + 深度）
- [ ] DESIGN §4.3 例外率注明"实际触发分母"
- [ ] `python3 -m py_compile` goal_snapshot.py 通过
- [ ] `python3 ai_workflow/goal_snapshot.py --self-test` 通过
- [ ] INDEX.md + CHANGELOG.md v30 段更新
- [ ] 不 commit / 不改 hooks.json / 不动 v17-v29 历史归档

---

## 5. 反模式（DNA 执行版硬约束）

- ❌ 单 turn 改 ≥ 5 个文件（本轮涉及 4 个规则/代码文件 + 2 个索引文件，合计 6 个，需用户明确豁免或分两 turn）
- ❌ 跳过 Read 目标文件（DNA §9.4）
- ❌ 在 SKILL.md 中引用不存在的行号
- ❌ 修改 v17-v29 历史 CONVERGED.md 归档
- ❌ 修改 Hook 源码逻辑

---

## 6. 落档协议

- 本档占位（`governance/design_iter/plans/v30/GOAL.md`）
- PLAN.md 由 T-001 产出（决策表 + 子任务分配）
- audit_1.md / review_1.md / CONVERGED.md 由 goal-loop 三件套机制产出
