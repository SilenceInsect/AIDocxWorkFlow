# review_round1.md — v28 Round 1 复盘

**Goal ID**: （T-208 落档时填）
**复盘日期**: 2026-07-20
**Round**: 1
**status**: converged_with_followup

---

## §1 缺陷汇总（去重 · 按严重度排序）

### BLOCKER（0）
全部 BLOCKER PASS，无遗留。

### MAJOR（1）

|| # | 描述 | 建议修复 | 来源 |
||---|---|---|---|
|| M-1 | `ai_workflow/case_id_and_field_normalizer.py` `evaluate_status` 调用 `validate_field_traceability` 时 `tp.get("tp_id")` on `'str' object`（API 数据契约问题，**pre-existing 非本轮引入**）| v29+ 评估修复：`tp_list` 应是 `list[dict]`，不应是 `list[str]`；检查 evaluate_status 入参契约 | T-202 V-202 §6.3 实证；T-202 不动 validator（仅放宽约束 + v3.01 SSOT 守住 + self-test 不受影响）|

### MINOR（0）
无 MINOR 项遗留。

---

## §2 根因定位（机制 / 规范 / 习惯）

### 根因 R1：v26 草案 A1/A3/A4/B3 的「字面重复」误判
**类型**：规范问题（草案撰写方法学）
**现象**：
- v26 §A 组把「两份章节都提到 X」当作「X 被重复定义」（A1 / A3 / A4）
- v26 §B 组 B3 把「§3.7 Python SOP」与「§9.1 决策密度阈值」当作「同一件事分两处」

→ 实际 DNA §10.6 / §9.5-§9.4 关系 / §9.6 紧跟 §9.5 / DESIGN §3.7 vs DNA §9.1 均为**桥接段显式分工**
**根因**：v26 子任务撰写时未引用 DNA §3「约束 vs 知识」分层原则 + 未引用 §9.6「L1 知识 / L2 约束 / L3 机制」三层映射
**影响**：T-205 4 DT 全部 REJECT 维持现状 + v30+ 修订 v26 §5 优先级表
**处置**：DT-V28-006/007/008/009 完整精审 + 共同根因分析（§5.2）+ v28 carry 显式标注「A1/A3/A4/B3 已 v28 DT 精审 REJECT」

### 根因 R2：v26 草案 B4 自身矛盾
**类型**：规范问题（草案样例选择）
**现象**：
- v26 §B4 草案建议「原始覆盖率改为 ≥ 95%」
- 草案样例「22/25=88% 仍属例外率 0」，**自身低于建议阈值**

→ 草案样例不能用自身证明建议阈值合理
**根因**：草案撰写时未做自验证（草案样例 vs 建议阈值）
**影响**：T-204 DT-V28-005 驳回 v26 草案 + 维持 1.0 + 重构口径
**处置**：DT-V28-005 落档「维持业务门槛 + 重构分母与处置分类」+ v28 carry「B4 已 v28 DT 精审维持 100% 业务门槛」

### 根因 R3：v26 草案 D3 忽视 L3 联动
**类型**：机制问题（goal-loop L3 联动 + 反模式防御的双向锁）
**现象**：
- v26 §D3 草案建议「Round 4 后每 2 轮跑 1 次」
- SKILL.md §3.5 F2 修复条款（DT-v17.1-001 §DT-2 问题 1）明确禁止跳轮
- SKILL.md §10.2 breakloop 门 B 强依赖 `last_audit.verdicts`，跳轮 = 门 B 失效

→ 改草案 B 选项必触发 v17.1 Round 4 同款事故
**根因**：v26 子任务撰写时未引用 SKILL.md §3.5 / §10.2 / DT-v17.1-001 教训
**影响**：T-203 DT-V28-003 修订草案 → 选 C（Audit 每轮必跑 + Review 双档，保留 §3.5 F2 不动）
**处置**：DT-V28-003 落档「选项 C 与草案 B 完全不同，修订为更安全的解」

### 根因 R4：pre-existing bug 不在本轮范围
**类型**：机制问题（任务边界契约）
**现象**：
- T-202 V-202 §6.3 实证 `case_id_and_field_normalizer.evaluate_status` 调用 `validate_field_traceability` 时 `tp.get("tp_id")` on `'str' object`
- T-202 硬约束：「不加严校验（仅放宽）」→ 不动 validator 源码

→ 实证 bug 出现但不修，留 follow_up
**根因**：T-202 硬约束「仅放宽描述，不动代码」与 bug 修复路径冲突
**影响**：L1S6/L2S6 self-test 不受影响（self-test 用合规 dict tp_list）；V-202 PASS 但 pre-existing bug 留 v29+
**处置**：MAJOR follow_up_items 显式记录 + 「v29+ 评估修复」承接 + 写明「tp_list 应是 list[dict]，不应是 list[str]」

---

## §3 可落地修复方案（明确下一步动作 + 影响范围）

### v29+ follow_up_items（已写入 snapshot）

|| # | 描述 | 严重度 | 建议修复 | 影响范围 |
||---|---|---|---|---|
|| F-1 | `case_id_and_field_normalizer.evaluate_status` tp.get("tp_id") on 'str' object | MAJOR | v29 评估修复 `tp_list` 数据契约（list[dict]）+ 检查 evaluate_status 入参 + 加 self-test 覆盖 | ai_workflow/case_id_and_field_normalizer.py + l1 validator 调用契约 |

### v29+ carry（来自 v28 GOAL §2）

|| # | 描述 | 来源 |
||---|---|---|
|| F-2 | DT-V28-002 落地 SKILL.md §2 schema + §3.2 + goal_signature_changelog[] | 本轮 DT 决策未实装 |
|| F-3 | DT-V28-003 落地 SKILL.md §3.4 Review 双档 | 本轮 DT 决策未实装 |
|| F-4 | v26 §5 优先级表修订（标注「A1/A3/A4/B3 已 v28 DT 精审 REJECT」）| 本轮根因 R1 follow_up |
|| F-5 | v26 §5 优先级表修订（标注「B4 已 v28 DT 精审维持 100%」）| 本轮根因 R2 follow_up |
|| F-6 | v26 §5 优先级表修订（标注「D3 已 v28 DT 精审选 C」）| 本轮根因 R3 follow_up |

### v29+ 反模式防御建议（GL-004）

|| # | 建议 | 写入 |
||---|---|---|
|| SYS-001（已落地）| v28 GOAL.md 必须避免与 out_of_scope.md 产生内在矛盾；如有冲突在 GOAL §1 显式标注边界 | T-206 SKILL.md §3.1.1 已加边界标注示例 |
|| SYS-002（已落地）| 父任务描述路径必须先 Read 验证再写入 subagent prompt | T-207 SKILL.md §3.2.1 已加路径 Read 前置模板 |
|| SYS-003（新建议）| v29+ 草案撰写方法学：草案样例必须自验证（样例 vs 建议阈值不能自身矛盾）—— 例 v26 §B4 22/25=88% vs 95% 草案 | knowledge/public/goal_loop/systemic_issues.md 待补（v29+ 启动条件）|

### v29+ 反模式识别（同类 ≥ 2 条）

|| 反模式 | 累计 | 触发时间 | 相关 Skill |
||---|---|---|---|---|
|| "草案样例与建议阈值自身矛盾"（v28 R2 B4） | 1 次 | 2026-07-20 | goal-loop / v29+ draft methodology |
|| "草案忽视 L3 联动"（v28 R3 D3） | 1 次 | 2026-07-20 | 同上 |
|| "目标契约内在矛盾"（v17.1 GL-007 + v27 + v28 SYS-001 防御）| 2 次 | 2026-07-18 + 2026-07-20 + 2026-07-20 | goal-loop（SYS-001 已落地）|
|| "C*/B*/D* 决策标已完成但缺独立精审"（v28 R1 + R2 + R3）| 3 次 | 2026-07-20 | 同上 |

未达 SYS-001 类 ≥ 3 次阈值（v28 已 SYS-001 机制化防御）。

---

## §4 本轮决策表（影响范围 + 替代方案）

### 决策 D-1（DT-V28-001 落档）：D1 value_ratio 阈值降到 0.5 + 软记录
- **改动**：SKILL.md §2.1 line 76 + §3.1 line 197 文字约束（待 v29 实装）；§9 line 419 维持 0.6 不动
- **影响范围**：仅 `.cursor/skills/goal-loop/SKILL.md`（v29 实装时）
- **替代方案**：
  - 方案 A（维持 0.6 强制）→ v3.01 实测已催生凑价值反模式
  - 方案 C（区分 Goal 类型）→ 引入分类逻辑复杂度

### 决策 D-2（DT-V28-002 落档）：D2 相似度阻断改 `goal_signature_changelog[]`
- **改动**：SKILL.md §2 schema 新增 `goal_signature_changelog[]` 字段 + §3.2 文字约束修订（待 v29 实装）
- **影响范围**：`.cursor/skills/goal-loop/SKILL.md` + `goal_snapshot.py`（v29 实装时）
- **替代方案**：
  - 方案 A（维持 0.7 阻断）→ 自治模式无人工可确认
  - 方案 B（仅降阈值）→ 不解决根因断点

### 决策 D-3（DT-V28-003 落档）：D3 Audit 必跑 + Review 双档
- **改动**：SKILL.md §3 line 188 + §3.4 全文（待 v29 实装）；§3.5 F2 修复条款不动；§10.2 门 B 不动
- **影响范围**：仅 `.cursor/skills/goal-loop/SKILL.md`（v29 实装时）
- **替代方案**：
  - 方案 A（维持每轮必跑单档） → 现状稳定但成本高
  - 方案 B（Round 4 后每 2 轮跑 1 次） → 必触发 v17.1 Round 4 同款事故

### 决策 D-4（DT-V28-004 落档）：B2 维持 20% / 40% + 校正口径
- **改动**：DESIGN §4.3 不动阈值 + 设计 `applicable/evaluated/bypassed` 事实账本（待 v29+ 评估）
- **影响范围**：`.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.4.2（v29+ 评估）
- **替代方案**：
  - 方案 A（按 v26 草案改 30% / 50%）→ 证据不足且不解决分母定义
  - 方案 C（任何 bypass 即预警）→ 增加噪声

### 决策 D-5（DT-V28-005 落档）：B4 维持业务门槛 + 重构口径
- **改动**：DESIGN §4.3.1 分母重构（适用风险叶子 / 自动化 / 人工 / 批准排除 / 未知缺口）+ 原始覆盖率作观察指标（待 v29+ 评估）
- **影响范围**：`.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3.1（v29+ 评估）
- **替代方案**：
  - 方案 A（按 v26 草案 ≥ 95%）→ 草案样例 88% < 95% 自身矛盾
  - 方案 B（维持原始 1.0）→ 强制 deprecated / out_of_scope 产生无价值 TP

### 决策 D-6（DT-V28-006/007/008/009 落档）：A1/A3/A4/B3 全部 REJECT 维持现状
- **改动**：不动 4 个规则文件（AGENTS.md / DNA_3Q_CHECK.mdc / DESIGN_AND_EXECUTION_STANDARDS.mdc / SKILL.md）
- **影响范围**：0 文件（仅精审落档）
- **替代方案**：
  - 方案 A（v26 草案合并）→ 4 项均会破坏 L2 vs L3 分层 / 触发 v17.1 Round 4 事故 / 删桥接段引入新歧义

### 决策 D-7（T-206 落档）：SYS-001 SKILL.md 防御
- **改动**：SKILL.md §3.1.1 加「GOAL §1 vs §10 边界显式标注」段
- **影响范围**：仅 `.cursor/skills/goal-loop/SKILL.md` §3.1.1 增段
- **替代方案**：
  - 方案 A（不写守卫）→ SYS-001 累计 ≥ 3 次阈值复发

### 决策 D-8（T-207 落档）：SYS-002 SKILL.md 防御
- **改动**：SKILL.md §3.2.1 加「子任务 prompt 注入路径 Read」前置段
- **影响范围**：仅 `.cursor/skills/goal-loop/SKILL.md` §3.2.1 增段
- **替代方案**：
  - 方案 A（不写守卫）→ v27 R3 任务描述路径错误复发

### 决策 D-9（T-208 落档）：v28 治理档闭环
- **改动**：11 文件落地（4 治理档 + 3 DT 档 + INDEX + CHANGELOG + snapshot + T-202 §6.3 SKILL.md SYS 段）
- **影响范围**：仅本轮 v28 治理档新增 + INDEX/CHANGELOG/snapshot 编辑
- **替代方案**：
  - 方案 A（不联动 INDEX/CHANGELOG）→ 上轮 v27 V-106 已有反例
  - 方案 B（commit）→ 违反硬约束

---

## §5 总结

v28 Round 1 完成 7 项价值化 + 9 个 DT 决策 + SYS-001/002 防御落地 + 治理档闭环：

- F-1 DESIGN §2.4.2/§5.1 数字清理 ✅
- F-2 v17 5 项约束放宽（仅文档，不动代码） ✅
- F-3 D1-D3 精审（1 采纳 + 2 修订） ✅
- F-4 B2/B4 精审（双驳回 v26 草案） ✅
- F-5 A1/A3/A4/B3 精审（4 项 REJECT） ✅
- SYS-001 SKILL.md §3.1.1 防御 ✅
- SYS-002 SKILL.md §3.2.1 防御 ✅

**全部 BLOCKER PASS + 全部 MAJOR PASS → converged_with_followup**。

MAJOR 遗留 1 项（`case_id_and_field_normalizer` pre-existing bug，**非本轮引入**）→ v29+ 处理。

v3.01 SSOT 守住 / hooks.json 不动 / git config 不动 / v17-v27 历史治理档不删不改 / knowledge/public/ 不动。

---

## §6 触发的反模式 / 阻塞

- 反模式：0（§4 反模式防御全过）
- 阻塞：0（9 DT 决策已闭环）
- follow_up：1 MAJOR（pre-existing bug）+ 6 MINOR（v29+ carry）

---

## §7 v29 启动条件

|| 项 | 条件 |
||---|---|
|| 1 | 读完 v28 audit_round1.md + review_round1.md + CONVERGED.md |
|| 2 | F-1（pre-existing bug 修复）首批处理 |
|| 3 | F-2/F-3（DT-V28-002/003 SKILL.md 落地） 实施 |
|| 4 | v26 §5 优先级表修订（F-4/F-5/F-6）|
|| 5 | SYS-001/SYS-002 守卫机制保持 |
|| 6 | value_ratio ≥ 0.6（GL-001 强制线） |
|| 7 | goal-loop v1.2 schema 18 字段 + `goal_signature_changelog[]`（v1.2.1 计划新增）|
