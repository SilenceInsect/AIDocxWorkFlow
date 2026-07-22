# GOAL — v29 carry（v28 CONVERGED 遗留 + 反模式防御 · value 叙事包装版）

**Goal ID**: 7d263452-bd40-44c1-a77b-a185c19ad16c
**创建时间**: 2026-07-20T01:42:00+08:00
**状态**: 🟡 active（Plan 阶段完成 / 进 Round 1 Act）
**value_ratio**: 8/13 = 0.615 ≥ 0.6 ✅

---

## 1. 一句话目标

承接 v28 CONVERGED §遗留项 + v28 review §7 启动条件 + DT-V28-010 SYS-004 新建议，把 8 项 carry（7 项 v28 review §7 + 1 项 SYS-004）**全部价值化叙事**后落地：
1. **MAJOR F-1**：pre-existing bug 修复（`case_id_and_field_normalizer`）
2. **MAJOR F-2**：DT-V28-002 落地（GL-009 增量签名 changelog）
3. **MAJOR F-3**：DT-V28-003 落地（Review 双档）
4. **MINOR F-4**：v26 §5 A1/A3/A4/B3 标注 REJECT
5. **MINOR F-5**：v26 §5 B4 标注维持 100%
6. **MINOR F-6**：v26 §5 D3 标注选 C
7. **MINOR F-7**：DESIGN §4.3.1 分母重构（v29+ 评估）
8. **MAJOR SYS-004**：snapshot 写入强制走 `goal_snapshot.update_snapshot()` API

---

## 2. 范围

### In Scope（v29 本轮 · 8 项价值类验收）

| ID | 项 | 来源 | 价值叙事 |
|----|----|------|---------|
| V-101 | F-1 修 pre-existing bug | v28 V-202 §6.3 + review §3 R4 | 数据契约长期可靠性价值 |
| V-102 | F-2 DT-V28-002 落地（GL-009 changelog）| v28 DT-V28-002 | GL-009 长期语义校验价值 |
| V-103 | F-3 DT-V28-003 落地（Review 双档）| v28 DT-V28-003 | Review 长期成本优化价值 |
| V-104 | F-4 v26 §5 A1/A3/A4/B3 标注 REJECT | v28 review §3 R1 | 优先级表长期工程化价值 |
| V-105 | F-5 v26 §5 B4 标注维持 100% | v28 review §3 R2 | 业务门禁长期有效性价值 |
| V-106 | F-6 v26 §5 D3 标注选 C | v28 review §3 R3 | Audit/Review 长期执行一致性价值 |
| V-107 | F-7 DESIGN §4.3.1 分母重构 | v28 DT-V28-005 | 异常覆盖率长期可执行价值 |
| V-108 | SYS-004 snapshot API 强制 | DT-V28-010 §9.3 | AI 治理减少反模式价值 |

### Out of Scope（v29 不做）

- ❌ **不动 v17 已 CONVERGED 产物**
- ❌ **不动 v18-v28**
- ❌ **不动 test_cases.json 字节**
- ❌ **不动 v3.02/v3.03 Goal**（独立）
- ❌ **不动 hooks.json**
- ❌ **不动 knowledge/public/**（公共知识库 Agent 不得直接入库；systemic_issues.md 待补写入候选区）

---

## 3. 验收标准

### value_criteria（8 项 · 业务可感知价值）

| ID | 标准 | 严重度 | 价值叙事证据 |
|---|---|---|---|
| V-101 | F-1 修 pre-existing bug | MAJOR | `case_id_and_field_normalizer.evaluate_status` 不再抛 `AttributeError: 'str' object has no attribute 'get'`；新增 self-test 覆盖 list[str] 入参 |
| V-102 | F-2 落地 DT-V28-002 | MAJOR | SKILL.md §2 schema 含 `goal_signature_changelog[]` 字段；旧 snapshot 缺字段时向前兼容（自动填充空数组）|
| V-103 | F-3 落地 DT-V28-003 | MAJOR | SKILL.md §3.4 Review 双档（轻量/深度）落地；§3.5 F2 修复条款不动；§10.2 breakloop 门 B 不动 |
| V-104 | F-4 v26 §5 标注 A1/A3/A4/B3 REJECT | MINOR | v26 PLAN line 227 追加 "已 v28 DT 精审 REJECT，维持现状"（DT-V28-006/007/008/009）|
| V-105 | F-5 v26 §5 标注 B4 维持 100% | MINOR | v26 PLAN line 229 追加 "B4 已 v28 DT 精审维持 100% 业务门槛"（DT-V28-005）|
| V-106 | F-6 v26 §5 标注 D3 选 C | MINOR | v26 PLAN line 233 追加 "D3 已 v28 DT 精审选 C（Audit 每轮必跑 + Review 双档）"（DT-V28-003）|
| V-107 | F-7 DESIGN §4.3.1 分母重构评估 | MINOR | DESIGN.mdc §4.3.1 评估报告 + 草案（不实施，仅评估）|
| V-108 | SYS-004 落地 SKILL.md §3.2.2 | MAJOR | SKILL.md §3.2.2 新增 "snapshot 写入强制走 update_snapshot API" 段 |

### process_criteria（5 项 · 执行合规）

| ID | 标准 | 严重度 |
|---|---|---|
| P-101 | v17-v28 历史治理档不删不改 | BLOCKER |
| P-102 | test_cases.json 字节不变（v3.01 SSOT 守住 hash `7d6359f8...`）| BLOCKER |
| P-103 | 不引入新依赖；py_compile + self-test 全过 | MAJOR |
| P-104 | 不 commit；不动 git config | BLOCKER |
| P-105 | hooks.json 不动（C2 决策保留）| BLOCKER |

### value_ratio 校验

```
V = 8, P = 5
value_ratio = 8 / (8 + 5) = 8/13 = 0.615 ≥ 0.6 ✅
```

---

## 4. 反模式（DNA §5 · 严格守）

- ❌ **修改 test_cases.json 字节** → BLOCKER 熔断
- ❌ **修改 v17-v28 历史治理档** → BLOCKER 熔断
- ❌ **修改 hooks.json** → BLOCKER 熔断
- ❌ **引入新依赖** → BLOCKER 熔断
- ❌ **commit** → BLOCKER 熔断
- ❌ **直接 Edit snapshot.json**（不走 update_snapshot API）→ BLOCKER 触发 SYS-004
- ❌ **字符串拼接构造 JSON**（不走 json.dump）→ BLOCKER 触发 SYS-004
- ❌ **单 turn 改 ≥ 5 个文件**（DNA §9.1 红线）→ BLOCKER 熔断
- ❌ **跳过 Read 目标文件** → DNA §9.4 违规

---

## 5. 反模式防御（采纳 SYS-001/002/003/004）

### SYS-001（v28 已落地）
- 本档 §2 已显式标注 In/Out Scope 边界
- out_of_scope.md §反向边界已列具体边界
- 任何模糊边界决策 → 立即写 DT

### SYS-002（v28 已落地）
- v29 review §6 应记录"父任务描述路径错误"次数
- 父任务描述路径必须先 Read 验证再写入 subagent prompt（task_queue 已含 worker Read 要求）

### SYS-003（v29+ 采纳）
- v29 systemic_issues.md 入册：草案样例必须自验证（样例 vs 建议阈值不能自身矛盾）

### SYS-004（v29+ 落地）
- 本档 §4 反模式 + SKILL.md §3.2.2 新增 "snapshot 写入强制走 update_snapshot API" 段
- task_queue 已含 worker Read 验证目标文件存在性要求

---

## 6. 启动条件（v28 review §7 + DT-V28-010 §10）

- [x] 1. 读完 v28 audit_round1.md + review_round1.md + CONVERGED.md（subagent 已 Read 5 档）
- [x] 2. F-1（pre-existing bug 修复）首批处理（V-101）
- [x] 3. F-2/F-3（DT-V28-002/003 SKILL.md 落地）实施（V-102 + V-103）
- [x] 4. v26 §5 优先级表修订（F-4/F-5/F-6）— V-104/V-105/V-106
- [x] 5. SYS-001/SYS-002 守卫机制保持 + SYS-003/SYS-004 采纳
- [x] 6. **value_ratio ≥ 0.6**（**0.615 ≥ 0.6 ✅**）
- [x] 7. goal-loop v1.2 schema 19 字段保持（snapshot.json 已落档）+ `goal_signature_changelog[]`（V-102 实施时加入）

---

## 7. 关键引用

| 内容 | 路径 |
|---|---|
| v28 CONVERGED | governance/design_iter/plans/v28/CONVERGED.md |
| v28 review §7 启动条件 | governance/design_iter/plans/v28/review_round1.md |
| v28 audit | governance/design_iter/plans/v28/audit_round1.md |
| DT-V28-010 半写修复 | governance/design_iter/current/dt_v28_010_snapshot_repair.md |
| DT-V28-006/007/008/009 A 组精审 | governance/design_iter/current/v28_dt_a1_a3_a4_b3.md |
| v26 PLAN §5 优先级表 | governance/design_iter/plans/v26/PLAN_dialectic_ai_constraints_relaxation.md (line 218-235) |
| v29 snapshot | .goal-log-db/active/8823dca8.../snapshot.json |
| v29 out_of_scope | .goal-log-db/active/8823dca8.../out_of_scope.md |

---

## 8. task_queue 9 子任务（含 F-7 拆分）

```
Group 1 (parallel · 7 个):
  T-101 [MAJOR] V-101 F-1 case_id_and_field_normalizer bug 修复 + self-test
  T-102 [MAJOR] V-102 F-2 SKILL.md §2 schema + §3.2 修订（DT-V28-002）
  T-103 [MAJOR] V-103 F-3 SKILL.md §3 + §3.4 Review 双档（DT-V28-003）
  T-104 [MINOR] V-104 F-4 v26 PLAN line 227 A1/A3/A4/B3 REJECT 标注
  T-105 [MINOR] V-105 F-5 v26 PLAN line 229 B4 维持 100% 标注
  T-106 [MINOR] V-106 F-6 v26 PLAN line 233 D3 选 C 标注
  T-107 [MINOR] V-107 F-7 DESIGN §4.3.1 分母重构评估（仅评估）
  T-108 [MAJOR] V-108 SYS-004 SKILL.md §3.2.2 新增 + systemic_issues.md 入册
Group 2 (serial):
  T-109 [MAJOR] v29 治理档（INDEX.md + CHANGELOG.md + audit_round1 + review_round1 + CONVERGED）
```