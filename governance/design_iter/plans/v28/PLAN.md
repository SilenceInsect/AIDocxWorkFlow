# PLAN — v28 v27 carry 落地轮（7 项价值化 + SYS-001/002 防御）

**版本**: v28
**状态**: 🟡 active → Round 1 收敛后转 🟢 current
**Goal ID**: （沿用 v27 9b1ca386... 终态后新开，本轮独立 goal 或作为 v28 闭环 Goal 由 .goal-log-db 路径登记）
**创建时间**: 2026-07-20
**承接**: v27 CONVERGED.md + v27 §3 遗留清单（F-1 / F-2 / F-3 / F-4 / F-5）+ v26 草案 5 项放宽 + v28 GOAL.md

---

## 解决（5 项 action + 9 个 DT 决策 + 7 项价值化）

### 价值化总览（本轮 F-1 ~ F-5 全部价值化）

|| ID | 来源 | 实际产出 | 状态 |
||---|---|---|---|---|
|| F-1 | v27 follow_up §2.4.2/§5.1 残留数字 | T-201 V-201：DESIGN §2.4.2/§5.1 数字 → 「如 §4.3 配置所示」索引格式 | ✅ |
|| F-2 | v27 §3 carry: v17 5 项约束放宽 | T-202 V-202：SKILL.md §3/§11 + STAGE_S6.mdc §1.7/§11 同步 4 项放宽（preconditions[] 维持）| ✅ |
|| F-3 | v27 §3 carry: D1-D3 精审 | T-203 V-203：DT-V28-001/002/003 落档 | ✅ |
|| F-4 | v27 §3 carry: B2/B4 精审 | T-204 V-204：DT-V28-004/005 落档 | ✅ |
|| F-5 | v27 §3 carry: A1/A3/A4/B3 精审 | T-205 V-205：DT-V28-006/007/008/009 落档（4 项 REJECT）| ✅ |

### 9 个 DT 决策清单

|| DT ID | 主题 | 方案 | 状态 |
||---|---|---|---|
|| DT-V28-001 | D1 value_ratio 阈值 | B：降到 0.5 + 软记录（§9 维持 0.6）| ✅ |
|| DT-V28-002 | D2 相似度阻断 | D：增量更新签名 + `goal_signature_changelog[]` | ✅ |
|| DT-V28-003 | D3 Audit/Review 频率 | C：Audit 每轮必跑（§3.5 F2 不动）+ Review 双档 | ✅ |
|| DT-V28-004 | B2 例外率阈值 | **维持（先校正口径，不调整 20% / 40%）** | ✅ |
|| DT-V28-005 | B4 异常覆盖率 | **维持业务门槛 + 重构口径（不接受 95%）** | ✅ |
|| DT-V28-006 | A1 §1 Q5 vs §10 Q5 | REJECT 维持现状 | ✅ |
|| DT-V28-007 | A3 §9.4/§9.5 | REJECT 维持现状 | ✅ |
|| DT-V28-008 | A4 §9.6 vs §11 | REJECT 维持现状 | ✅ |
|| DT-V28-009 | B3 §3.7 vs §9.1 | REJECT 维持现状 | ✅ |

### SYS 类防御

|| ID | 描述 | 处置 | 状态 |
||---|---|---|---|
|| SYS-001 | v28 GOAL 必须避免与 out_of_scope.md 产生内在矛盾 | GOAL.md §1 标注「本轮只精审不改 SKILL.md」+ out_of_scope.md v1.2 同步 | ✅ |
|| SYS-002 | 父任务描述路径必须先 Read 验证 | 子任务 prompt 注入「先 Read 路径再写入」前置段 | ✅ |

---

## 新增

|| ID | 内容 | 位置 |
||---|---|---|
| N1 | v28 治理档（PLAN / audit_round1 / review_round1 / CONVERGED） | governance/design_iter/plans/v28/ |
| N2 | 3 个 DT 决策档（9 DT） | governance/design_iter/current/v28_dt_*.md |
| N3 | INDEX.md current=v28 + 摘要行 + §2 看板行 | governance/design_iter/INDEX.md |
| N4 | CHANGELOG.md v28 段（11 文件清单 + 9 DT） | CHANGELOG.md |
| N5 | snapshot.json 终态写入 | .goal-log-db/active/<v28-goal>/snapshot.json |

## 遗留（转下轮 v29+/v30+）

|| ID | 项 | 来源 | 承接 |
||---|---|---|---|---|
|| L1 | `case_id_and_field_normalizer.evaluate_status` 调用 `validate_field_traceability` 时 tp.get("tp_id") on 'str' object | T-202 §6.3 实证（pre-existing，非本轮引入）| v29 评估修复（**follow_up · MAJOR**）|
|| L2 | D2 DT-V28-002 落地 SKILL.md §2 schema + §3.2 + goal_signature_changelog[] | 本轮未实装 | v29 |
|| L3 | D3 DT-V28-003 落地 SKILL.md §3.4 Review 两档 | 本轮未实装 | v29 |
|| L4 | F-1 残留（v27 follow_up_items）已本轮 T-201 处理 | T-201 已 PASS | — |

---

## 决策表（每个 T 子任务）

### T-201 [BLOCKER] V-201 F-1 §2.4.2/§5.1 残留数字清理
- 文件：`.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`
- 改：§2.4.2（lines 196-214）+ §5.1（lines 618-619）的示例性阈值数字（7.0 / 90% / 20% / 0.20）→ 「如 §4.3 配置所示」索引格式
- 影响：DESIGN §2.4.2/§5.1 文字版（仅文档清理，不影响 §4.3 SSOT 唯一源）
- 替代方案：B 不清理 = 留 v27 follow_up_items（v26 草案 B 组已拍）
- 反模式：❌ 改 §4.3 SSOT 数值 = BLOCKER（违反 v27 B1 决策）

### T-202 [BLOCKER] V-202 F-2 v17 5 项约束放宽
- 文件 1：`.cursor/skills/aidocx-s6-test-cases/SKILL.md` §3 + §11
- 文件 2：`.cursor/rules/STAGE_S6_TEST_CASES.mdc` §1.7 + §11
- 改：4 项放宽（fp_name 已删除注 + steps[] 字符串数组 + test_method[] 单/数 + tp_references[] 数组）；preconditions[] 维持
- 验证：test_cases.json hash 不变（v3.01 SSOT 守住） + L1S6 self-test 10/10 + L2S6 self-test PASS + py_compile OK
- 反模式：❌ 改 test_cases.json = BLOCKER（v3.01 SSOT）；❌ 加严校验 = BLOCKER（仅放宽）

### T-203 [MAJOR] V-203 F-3 D1-D3 精审
- 文件：新建 `governance/design_iter/current/v28_dt_d1_d2_d3.md`
- 改：仅落档 DT-V28-001/002/003（含触发反模式/证据/断点/根因/候选/选择/验证 7 字段）
- 不动：SKILL.md / .py / hooks.json / v17-v27 历史治理档
- 反模式：❌ 单独改 SKILL.md §3.5 F2 修复条款 = BLOCKER（必触发 v17.1 Round 4 同款事故）

### T-204 [MAJOR] V-204 F-4 B2/B4 精审
- 文件：新建 `governance/design_iter/current/v28_dt_b2_b4.md`
- 改：DT-V28-004（B2 维持 20%/40% + 校正口径，不接受 30%/50% 草案）+ DT-V28-005（B4 维持业务门槛 + 重构口径，不接受 95% 草案）
- 反模式：❌ 接受 v26 草案 B4 95% = BLOCKER（草案样例 88% < 95%，自身矛盾）

### T-205 [MAJOR] V-205 F-5 A1/A3/A4/B3 精审
- 文件：新建 `governance/design_iter/current/v28_dt_a1_a3_a4_b3.md`
- 改：DT-V28-006/007/008/009（4 项全部 REJECT 维持现状 + MINOR follow_up）
- 依据：v27 worker 实测 + DNA §3/§9.6/§10.6 桥接段均显式分工
- 反模式：❌ 跨层合并 = BLOCKER（DNA §3 L2 vs L3 约束分层原则）

### T-206 [MAJOR] V-206 SYS-001 SKILL.md 防御
- 文件：`.cursor/skills/goal-loop/SKILL.md`
- 改：§3.1.1 新增「GOAL §1 vs §10 边界显式标注」段（防 SYS-001 复发）
- 验证：v28 GOAL.md §1 实测引用该段；py_compile OK

### T-207 [MAJOR] V-207 SYS-002 子任务路径 Read 防御
- 文件：`.cursor/skills/goal-loop/SKILL.md` §3.2.1
- 改：新增「子任务 prompt 注入路径 Read」段（防 SYS-002 复发）
- 验证：v28 T-203/204/205 worker 实测 prompt 包含「先 Read 路径再写入」

### T-208 [MAJOR] V-208 治理档闭环（本任务）
- 文件：
  - `governance/design_iter/plans/v28/{PLAN, audit_round1, review_round1, CONVERGED}.md`（新建）
  - `governance/design_iter/INDEX.md` current=v28 + 摘要行 + 看板行（编辑）
  - `CHANGELOG.md` v28 段追加（编辑）
  - `.goal-log-db/active/<v28-goal>/snapshot.json` 终态写入（更新）
- 改：本响应内完成 11 文件 + 9 DT + 1 follow_up 落档
- 反模式：❌ commit = BLOCKER（按 v27 V-106 + 本任务硬约束）；❌ 改 v17-v27 历史段 = BLOCKER

---

## 反模式熔断（DNA §5）

|| 反模式 | 触发动作 |
||---|---|
| §4.3 SSOT 被改数值 / §2.3 残留硬编码 | BLOCKER：撤销 + DT-v28.101 |
| 加严 L1∧L2 validator | BLOCKER：撤销 + DT-v28.102（违反 T-202「仅放宽」） |
| T-205 任一 DT 跨层合并 DNA §9 + §10 | BLOCKER：撤销 + DT-v28.103 |
| §3.5 F2 修复条款被改动 | BLOCKER：撤销 + DT-v28.104（必触发 v17.1 Round 4 事故）|
| 单轮文件改动 ≥ 3 业务文件 | BLOCKER：列决策表 + ask（豁免见 §9.1.2 goal-loop 产物）|
| commit / 改 git config / 改 v17-v27 历史治理档 | BLOCKER：撤销 + DT-v28.105 |
| test_cases.json 字节变化 | BLOCKER：撤销 + DT-v28.106（v3.01 SSOT） |

---

## v28 ↔ v17/v18/v19/v26/v27 关系

|| 版本 | 关系 |
||---|---|
|| v17 | 已 CONVERGED；本轮**不动** v17 阶段产物（v17 5 项约束放宽由本轮 T-202 接办，**仅放宽文档不动代码**）|
|| v18-v22 | 已归档；本轮**不动**其索引 |
|| v25 | 已归档；本轮**不动** |
|| v26 | 草案状态（plan-only）；v28 是其落地轮（但 T-203/204/205 已对照草案精审）|
|| v27 | **本轮 current 起点**（T-201 处理 v27 follow_up_items F-1） |
|| v28 | **本轮 current 终点**（治理档闭环 + 11 文件 + 9 DT + 1 pre-existing bug follow_up）|

---

## 落档协议

- 本档：`governance/design_iter/plans/v28/PLAN.md`（已落档）
- snapshot：`.goal-log-db/active/<v28-goal>/snapshot.json`（T-208 终态写入）
- audit_round1.md：T-208 完成后产出
- review_round1.md：Audit 后产出
- CONVERGED.md：Round 1 收敛后产出（converged_with_followup）
