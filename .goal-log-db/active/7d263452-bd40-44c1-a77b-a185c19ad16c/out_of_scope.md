# out_of_scope.md（v29 carry — v28 CONVERGED 遗留 + 反模式防御）

> **依据**：goal-loop SKILL v1.2 §3.1 强制产出
> **Goal ID**：`8823dca8-aee4-4810-83bd-efa3e4d53a86`
> **承接**：v28 CONVERGED §遗留项 + v28 review §7 v29 启动条件
> **创建日期**：2026-07-20

---

## 功能禁区

- ❌ **不动 v17 已 CONVERGED 产物**（fp_name 已 Round 15 F-F 删除；v17 §2 已闭环）
- ❌ **不动 v18-v19 / v22-v28**（保留审计锚点）
- ❌ **不动 test_cases.json 字节**（v3.01 SSOT 守住 hash `7d6359f8...`）
- ❌ **不动 v3.02 Goal**（`4c1eedec` active 与 v29 独立，v28 CONVERGED line 189 显式说明）
- ❌ **不动 v3.03 Goal**（`4c1eedec-v303` 与 v29 独立）
- ❌ **不动 v28 active goal `a6068831...`**（保留 v28 闭环产物）
- ❌ **不动 .gitignore / git config / git history**
- ❌ **不动 hooks.json**（C2 决策保留，v28 T-103 已审计，v29 不重开）
- ❌ **不动 knowledge/public/**（Agent 不得直接入库）

## 技术栈禁区

- ❌ **不引入新依赖**（DNA §9.1 红线）
- ❌ **不修改 v1.2 schema 19 字段之外的字段**（`closed_at` 不在 schema 中 — 见 DT-V28-010）
- ❌ **不动 validator 源码**（l1_s6.py / l2_s6.py 已闭环，v29 仅放宽不修 bug）
- ❌ **不修改 .mdc / SKILL.md 既有章节**（仅追加 F-2/F-3/SYS-004 新段）

## 职责边界禁区

- ❌ **不 commit**（用户硬约束）
- ❌ **不跨 goal 引用快照**（v3.02 Goal `4c1eedec` / v3.03 Goal `4c1eedec-v303` 与 v29 独立）
- ❌ **不修改 test_cases.json 字节**（v3.01 SSOT 守住）

## 反向边界（特别标注 · SYS-001 落地）

> 这些边界**必须守住**，否则触发反模式熔断：

1. **F-1 bug 修复范围**：仅修 `case_id_and_field_normalizer.evaluate_status` 入参契约 + 加 self-test 覆盖，不动 validator 源码（违反 v28 T-202「仅放宽」硬约束）
2. **F-2 SKILL.md §2 schema 新增** `goal_signature_changelog[]` 字段必须向前兼容（旧 snapshot 缺字段时自动填充空数组 — DT-V28-002 已记录）
3. **F-3 Review 双档**（轻量 / 深度）§3.5 F2 修复条款不动；§10.2 breakloop 门 B 不动
4. **F-4/F-5/F-6 v26 §5 优先级表修订**：仅在对应行追加标注，不动其他段落
5. **SYS-003/SYS-004 反模式防御**：写 systemic_issues.md（v29+ 启动条件）+ SKILL.md §3.2.2（SYS-004）

## 触发熔断条件

| 条件 | 触发动作 |
|---|---|
| 修改 test_cases.json 字节 | BLOCKER：撤销 + 写 DT |
| 修改 v17-v28 历史治理档 | BLOCKER：撤销 + 写 DT |
| 修改 hooks.json | BLOCKER：撤销 + 写 DT |
| 引入新依赖 | BLOCKER：回退 + 写 DT |
| commit | BLOCKER：撤销 commit + 写 DT |
| v29 改动触动 v3.01 / v3.02 / v3.03 / v28 active Goal 快照 | MAJOR：人工确认 |
| 直接 Edit snapshot.json（不走 update_snapshot API）| BLOCKER：触发 SYS-004 反模式 |
| 字符串拼接构造 JSON（不走 json.dump）| BLOCKER：触发 SYS-004 反模式 |