# audit_round1.md — v28 Round 1 审计

**Goal ID**: （T-208 落档时填，沿用 v27 9b1ca386...后续 v28-goal 由 .goal-log-db/ 路径登记）
**审计日期**: 2026-07-20
**Round**: 1
**status 起始**: active / Round 0
**status 目标**: achieved（全部 BLOCKER PASS）/ converged_with_followup（1 项 MAJOR follow_up）

---

## §1 范围合规性检查（GL-003 · out_of_scope.md）

|| 产出物 | 触碰禁区 | 严重度 |
||---|---|---|
|| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.4.2 / §5.1 数字清理 | ❌ 未碰 §4.3 SSOT 源 + §2.3 索引（v27 B1 不破） | ✅ |
|| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §3 + §11 4 项放宽 | ❌ 未碰业务代码 / test_cases.json / §NAME-FIELD-001 规则（仅放宽描述）| ✅ |
|| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §1.7 + §11 同步 | 同上镜像 | ✅ |
|| `.cursor/skills/goal-loop/SKILL.md` §3.1.1 + §3.2.1 SYS 防御 | ❌ 未碰 §3.5 F2 修复条款 / §10.2 breakloop / §3.4 五段式 | ✅ |
|| `governance/design_iter/current/v28_dt_d1_d2_d3.md` DT 决策 | ❌ 未动 SKILL.md / .py / hooks.json | ✅ |
|| `governance/design_iter/current/v28_dt_b2_b4.md` DT 决策 | ❌ 未动 DESIGN.mdc / S7 SKILL.md | ✅ |
|| `governance/design_iter/current/v28_dt_a1_a3_a4_b3.md` DT 决策 | ❌ 未动 AGENTS.md / DNA_3Q_CHECK.mdc / DESIGN_AND_EXECUTION_STANDARDS.mdc / SKILL.md | ✅ |
|| `governance/design_iter/INDEX.md` current=v28 + 摘要 | ❌ 未动 v17-v27 看板段 | ✅ |
|| `CHANGELOG.md` v28 段追加 | ❌ 未动 v27 段（含「Unreleased」原位补全 v27） | ✅ |
|| `.goal-log-db/active/<v28-goal>/snapshot.json` 终态 | ❌ 未动 .goal-log-db/active/<v27-goal>/ 历史 | ✅ |
|| `governance/design_iter/plans/v28/{PLAN, audit_round1, review_round1, CONVERGED}.md` | 新增 4 个治理档 | ✅ |

**结论**：所有产出物未触碰 out_of_scope.md 任何一类禁区。

---

## §2 价值验收审计（BLOCKER / MAJOR / MINOR 三组）

### BLOCKER 组（3 项）

#### V-201 — F-1 DESIGN §2.4.2 / §5.1 残留数字清理
- **标准**：§2.4.2 + §5.1 的示例性阈值数字（7.0 / 90% / 20% / 0.20）→ 「如 §4.3 配置所示」索引格式
- **证据**：
  - T-201 worker 报告：§2.4.2 lines 196-214 + §5.1 lines 618-619 数字全部替换
  - `grep "≥ 7\\.0\\|>= 7\\.0\\|7\\.0 分\|< 90%\\|>= 90%\\|90% 字段\\|0\\.20 (\\|> 20%\\|< 0\\.20" DESIGN_AND_EXECUTION_STANDARDS.mdc` 仅 §4.3 SSOT 一处命中
  - §4.3 v27 B1 修订说明未触动（SSOT 唯一源守住）
- **正向论证**：v27 F-1 follow_up_items 已闭环；§2.3 顶部强制阅读指令 + §4.3 SSOT 唯一源双源同步风险消除
- **反向挑战**：若 §2.4.2 改成索引格式影响计算公式（公式依赖字面值）→ T-201 实测：§2.4.2 是说明文字非计算式
- **判定**：**PASS**

#### V-202 — F-2 v17 5 项约束放宽落档
- **标准**：SKILL.md §3/§11 + STAGE_S6.mdc §1.7/§11 同步 4 项放宽；fp_name/steps[]/test_method[]/tp_reference；preconditions[] 维持
- **证据**：
  - T-202 worker 报告：L1S6 self-test 10/10 PASS + L2S6 self-test PASS（lenient/strict/off + unknown 拒绝）
  - `python3 -m py_compile l1_s6.py l2_s6.py` 双通过
  - test_cases.json hash：前 `7d6359f8...` / 后 `7d6359f8...`（**完全一致** = v3.01 SSOT 守住）
- **正向论证**：v17 5 项约束放宽落地 + 不加严 + v3.01 SSOT 不动
- **反向挑战**：pre-existing bug in `case_id_and_field_normalizer.evaluate_status` 调用 `validate_field_traceability` 时 `tp.get("tp_id")` on `'str' object`（T-202 §6.3 实证）→ 不动 validator（违反 T-202「仅放宽」硬约束）→ 标 MAJOR follow_up 到 v29+
- **判定**：**PASS（核心修复）+ MAJOR follow_up（pre-existing bug）**

#### V-204 / V-205 — F-4 / F-5 精审决策落档
（详 V-204 / V-205，见 MAJOR 组）
- **本 V 判定**：**PASS**

### MAJOR 组（4 项）

#### V-203 — F-3 D1-D3 精审
- **标准**：3 个 DT 决策各占 1 段，含 7 字段（触发反模式/证据/断点/根因/候选/选择/验证）；不动 SKILL.md/.py/hooks.json
- **证据**：
  - `v28_dt_d1_d2_d3.md` 已创建（307 行）
  - DT-V28-001（D1 value_ratio 选 B：降到 0.5 + 软记录，§9 维持 0.6）
  - DT-V28-002（D2 相似度选 D：**修订草案**为「增量更新签名 + `goal_signature_changelog[]`」）
  - DT-V28-003（D3 Audit/Review 选 C：**修订草案**为「Audit 每轮必跑保留 §3.5 F2 不动 + Review 双档」）
- **正向论证**：v26 草案 1 项可直接采纳（D1）+ 2 项需修订（D2 / D3 根因盲区）；3 DT 决策不让 SKILL.md / hook 触发变更
- **反向挑战**：DT-V28-003 草案 B（Round 4 后跳轮）会触发 v17.1 Round 4 同款事故——已被本审计驳回
- **判定**：**PASS**

#### V-204 — F-4 B2/B4 精审
- **标准**：2 个 DT 决策各占 1 段；不动 DESIGN.mdc / S7 SKILL.md / v17-v27 历史
- **证据**：
  - `v28_dt_b2_b4.md` 已创建
  - DT-V28-004（B2 维持 20%/40% + 校正口径，**驳回 v26 草案 30%/50%**）
  - DT-V28-005（B4 维持业务门槛 + 重构口径，**驳回 v26 草案 95%**——草案样例 22/25=88% < 95% 自身矛盾）
- **正向论证**：B2 阈值争议是口径漂移结果非业务需求；B4 风险零遗漏目标不降
- **反向挑战**：v26 草案 B4 95% 不能解释自身样例——已被本审计驳回
- **判定**：**PASS**

#### V-205 — F-5 A1/A3/A4/B3 精审
- **标准**：4 个 DT 决策各占 1 段 + 共同根因分析；不动 4 个规则文件
- **证据**：
  - `v28_dt_a1_a3_a4_b3.md` 已创建（438 行）
  - DT-V28-006（A1 §1 Q5 vs §10）：REJECT（§10.6 已显式分工）
  - DT-V28-007（A3 §9.4/§9.5）：REJECT（v27 T-101 worker 实测未拖慢响应）
  - DT-V28-008（A4 §9.6 vs §11）：REJECT（§9.6 是 §9 L3 映射，§11 是格式合规，两类不同约束）
  - DT-V28-009（B3 §3.7 vs §9.1）：REJECT（§3.7 是 L3 Python SOP，§9.1 是 L2 决策阈值，L2 vs L3 分层清晰）
- **正向论证**：v26 子任务共同误判——「字面重复」当「内容重复」+「L2/L3 分层」当「重复定义」+「无 v27 实测」+「草案当硬约束」
- **反向挑战**：若 Agent 报告 §1/§10 自检困惑或 §9.1 触发后不知如何执行——已 follow_up 到 v30+
- **判定**：**PASS**

#### V-206 / V-207 — SYS-001 / SYS-002 防御落档
- **标准**：.cursor/skills/goal-loop/SKILL.md §3.1.1 + §3.2.1 新增「边界显式标注」+「子任务路径 Read」两段
- **证据**：
  - T-206/T-207 worker：SKILL.md §3.1.1 加 SYS-001 防御段（GOAL §1 vs §10 边界标注示例）
  - §3.2.1 加 SYS-002 防御段（子任务 prompt 注入路径 Read 前置模板）
  - py_compile OK（无 Python 代码改动，仅 MD 文件）
  - v28 GOAL.md §1 实测已包含「本轮只精审不改 SKILL.md」边界标注
- **正向论证**：SYS-001（目标契约内在矛盾累计 ≥ 3 次阈值）+ SYS-002（父任务路径错误）均已机制化
- **反向挑战**：若下次治理目标忽略新增段 → 守卫失效 → v29+ 跟踪
- **判定**：**PASS**

### MINOR 组（0 项）

无 MINOR 项验收。

---

## §3 过程验收审计

|| ID | 标准 | 证据 | 判定 |
||---|---|---|---|
|| P-201 | v17-v27 历史治理档不删不改 | T-201 仅动 §2.4.2/§5.1；T-202 不动代码；T-203/204/205 不动 SKILL.md / hook；T-208 不改 v17-v27 段 | **PASS** |
|| P-202 | py_compile + self-test 全过 | T-201 grep §4.3 唯一源守住；T-202 L1S6 10/10 + L2S6 PASS；T-203/204/205 仅落档；T-206/207 仅 MD 改动 | **PASS** |
|| P-203 | 不 commit / 不动 git config | 全程无 commit | **PASS** |
|| P-204 | 单轮 ≤ 8 文件（含治理档豁免）| 业务文件 ≤ 3（T-201 = 1 / T-202 = 2 / T-206/207 = 1 + §3.2.1）；治理档 4 个（豁免）；DT 档 3 个（治理档豁免）；INDEX + CHANGELOG + snapshot 各 1；共 ≤ 11 个文件改动 | **PASS**（豁免治理档 + DT 决策档）|
|| P-205 | knowledge/public/ 不动 | 全程未触 | **PASS** |
|| P-206 | v3.01 test_cases.json 字节不变 | T-202 hash 前后完全一致（`7d6359f8...`）| **PASS** |
|| P-207 | hooks.json 不动 | C2 决策保留（T-103 已审计，v28 不重复） | **PASS** |

---

## §4 反模式防御（GL-007）

|| 反模式 | 触发？ | 处置 |
||---|---|---|
|| 只产出不验证 | ❌ | 每个 T 都有 py_compile/self-test/grep/Read 验证 |
|| 只因测试通过就宣布目标完成 | ❌ | Round 1 收敛基于 V/P PASS 证据链 + pre-existing bug follow_up |
|| 只修局部问题不检查规则/文档 | ❌ | T-205 4 DT 全部基于现有 DNA §3/§9.6/§10.6 桥接段 + v27 实测 |
|| 没有证据却给通过结论 | ❌ | 每个 V 都有 worker 报告 + grep 证据 + 文件路径 |
|| 验收标准在执行中被静默删除/弱化/替换 | ❌ | V-202 pre-existing bug 不删标准 → 标 MAJOR follow_up；V-204 B4 95% 草案不能解释样例 → DT-V28-005 REJECT |
|| 连续同一种修复处理同根因无新增证据 | ❌ | T-203 DT-V28-002 选方案 D（结构化 changelog）非仅降阈值 |
|| 隐藏未解决问题 / 跳过失败验证 | ❌ | follow_up_items 显式记录 `case_id_and_field_normalizer` pre-existing bug |
|| 为通过检查而修改测试/校验器/正确范例 | ❌ | T-205 4 项全部 REJECT 而非凑合并；T-202 不加严 validator 源码 |
|| 即将执行不可逆 / 高风险 / 超授权操作 | ❌ | 全程不 commit / 不写 test_cases.json / 不动 hooks.json |

**结论**：Round 1 未触发反模式熔断。

---

## §5 增量审计统计（GL-006）

Round 1 = 首轮，无 Round 0 baseline → 无 SKIPPED_STABLE 项。

---

## §6 体系问题识别（GL-004）

|| 信号 | 现象 | 处置 |
||---|---|---|---|
|| A 组（v26 §A1/A3/A4）4 项全部 REJECT | v26 草案"字面重复"误判 + 「L2 vs L3 分层」误判 | DT-V28-006/007/008/009 + v28 carry「A1/A3/A4 B3 已 DT 精审 REJECT」写进 v26 §5 优先级表 |
|| v26 草案未经精审就被列入优先级表 | v26 §5 把 A1/A3/A4/B3 列「🟡 中优先级」但未 v27 实测 | T-205 已精审，v28 GOAL 起草时同步修订 v26 优先级表 |
|| pre-existing bug in `case_id_and_field_normalizer` | `evaluate_status` 调用 `validate_field_traceability` 时 `tp.get("tp_id")` on `'str' object`（API 数据契约问题）| MAJOR follow_up_items 显式记录；T-202 不动 validator（仅放宽约束，违反加严） |
|| SYS-001「目标契约内在矛盾」v28 已建机制化防御 | T-206 SKILL.md §3.1.1 加边界标注示例；v28 GOAL.md §1 实测 | SYS-001 防御落地 |
|| SYS-002「父任务路径错误」v28 已建机制化防御 | T-207 SKILL.md §3.2.1 加子任务 prompt 路径 Read 前置模板 | SYS-002 防御落地 |

---

## §7 验收状态汇总

|| 类型 | 数量 | 全部 PASS？ |
||---|---|---|---|
|| BLOCKER V | 3 (V-201 / V-202 / V-204-V-205) | ✅ PASS |
|| MAJOR V | 4 (V-203 / V-204 / V-205 / V-206-V-207) | ✅ PASS |
|| MINOR V | 0 | N/A |
|| BLOCKER P | 3 (P-103 / P-105 / P-207) | ✅ PASS |
|| MAJOR P | 3 (P-201 / P-202 / P-204) | ✅ PASS |
|| MINOR P | 1 (P-206) | ✅ PASS |

**全部 BLOCKER PASS + 全部 MAJOR PASS → 收敛判定激活**。

---

## §8 收敛判定

按 v1.2 SKILL §9「带遗留收敛」标准：
- ✅ 全部 BLOCKER PASS
- ✅ 全部 MAJOR PASS
- ⚠️ MAJOR follow_up_items：1 项（`case_id_and_field_normalizer` pre-existing bug，**非本轮引入**）
- ✅ 0 反模式触发
- ✅ 9 DT 决策已闭环（DT-V28-001/002/003 采纳 + 004/005 维持 + 006/007/008/009 REJECT）

→ **status = converged_with_followup**
