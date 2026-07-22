# out_of_scope.md（v29 Round 2 — 4 项 MINOR 弱证据补强）

> **依据**：goal-loop SKILL v1.2 §3.1 强制产出
> **Goal ID**：`97ab325d-a505-466b-8778-62c4706c9ff8`
> **承接**：v29 Round 1 follow_up_items 4 项 MINOR + SYS-005 候选复核
> **创建日期**：2026-07-20

---

## 功能禁区

- ❌ **不动 v29 已落档档位**（audit_round1/review_round1/CONVERGED/INDEX.md/CHANGELOG.md/snapshot.json 原 v29 已 achieved）
- ❌ **不动 v17-v28 历史治理档**
- ❌ **不动 test_cases.json 字节**（v3.01 SSOT 守住 hash `7d6359f8...`）
- ❌ **不动 v3.02/v3.03/v28 active goals**
- ❌ **不动 hooks.json**（C2 决策保留）
- ❌ **不动 knowledge/public/**（v29 Round 2 仅做 SYS-005 累计次数核对，不写入候选清单）

## Round 2 范围合规

### 必做（Group 1 并行）
- T-201 V-101R self-test verbose + 写入产物文件
- T-202 V-102R SNAPSHOT_FIELDS 同步实测
- T-203 V-103R SKILL.md §3 + §3.4 双档实测
- T-204 V-107R 评估报告全文深度实测
- T-205 RR-2-004 SYS-005 累计次数核对（仅核对，不写入 knowledge/public/）

### 必做（Group 2 串行）
- T-206 Round 2 治理档（audit_round2.md + review_round2.md + CONVERGED_round2.md）

### 不做（硬约束）
- ❌ 不引入新依赖
- ❌ 不修改 v29 Round 1 已落档任何文件
- ❌ 不修改 SKILL.md / v29_f7_*.md 业务内容（仅 Read 实测）
- ❌ 不 commit

### SYS 守住
- SYS-001 守住（In/Out 边界显式）
- SYS-002 守住（路径先 Read）
- SYS-004 守住（snapshot 走 API）
- SYS-005 守住（不预先 mkdir snapshot goal_id 目录）

## 触发熔断

| 条件 | 触发动作 |
|---|---|
| 修改 v29 Round 1 已落档 | BLOCKER：撤销 + 写 DT |
| 写入 knowledge/public/ | BLOCKER：撤回 + 写 DT |
| 直接 Edit snapshot.json | BLOCKER：触发 SYS-004 |
| 字符串拼接 JSON | BLOCKER：触发 SYS-004 |
| commit | BLOCKER：撤销 commit |
