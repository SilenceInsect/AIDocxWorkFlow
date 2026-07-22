# S6 MINOR follow-up 决策档（Q-013 / Q-026 / A-018 / A-019 / A-020）

> **决策档性质**：5 条 MINOR follow-up 处置决策（接受遗留 / 移交下一轮 / 立即修）
> **决策人**：架构师 worker（按 user 委托全权决策）
> **决策时间**：2026-07-19
> **来源**：review_13.md §1.3 MINOR 级别（5 项 · 全部 follow-up）

---

## §1 来源数据（review_13.md §1.3 真实原文）

| ID | 标题 | review_13 §1.3 原因列 |
|----|------|---------------------|
| Q-013 | 缺机器可读断言字段（`assertion: {field, op, value}`） | 需 LLM 生成阶段扩展，SSOT 改动大 |
| Q-026 | 28 TC 中 unique step action = 23（5 重复） | 同 Q-025 同源问题（OBJMall OBJ-01 内 28 TC step 重复） |
| A-018 | LOG 结构性欠测（同 Q-019） | ✅ 已修复 |
| A-019 | tc_tp_gap_report.md 陈旧（同 Q-018） | ⏳ follow-up |
| A-020 | feature_point_ref 与 fp_name 字段冗余 | 字段治理类 |

---

## §2 逐条处置决策

### M-1：Q-013 [MINOR] 缺机器可读断言字段（`assertion: {field, op, value}`）

**真实描述（§1.3）**：v3.01 TC 缺 `assertion: {field, op, value}` 机器可读断言；QA 跑用例需人工翻译 expected_results

**影响范围**：
- v3.01 386 TC × 缺 assertion 字段 → QA 自动化消费方需自行解析 expected_results 文本
- 字段级结构化断言缺失 → CI/CD 集成时人工维护成本高

**处置决策**：⏳ **移交下一轮（Round 15+）**

**理由**：
1. SSOT 改动大（SKILL aidocx-s6-test-cases §六 Schema 加字段 + LLM Prompt 强制每 TC 含 ≥ 1 assertion）
2. 涉及 LLM Prompt 工程（强制 schema 遵循）
3. 不阻塞 v3.01 业务发布（v3.01 已收敛 386/386 Ready）
4. 风险：v3.01 331 JSON TC 迁移需重生成（**out_of_scope 故不本轮动**）

**下一步动作**（Round 15+）：
- SKILL aidocx-s6-test-cases §六 Schema 加 `assertion: {field, op, value}` 字段模板
- LLM Prompt 强制每条 TC 含 ≥ 1 个 machine-readable assertion
- 新生成 TC 必须满足；v3.01 JSON 数据按需评估是否迁移

**优先级**：P2（不阻塞 v3.01）

---

### M-2：Q-026 [MINOR] 28 TC 中 unique step action = 23（5 重复）

**真实描述（§1.3）**：OBJMall OBJ-01 内 28 TC 中有 5 条 step action 重复（同 Q-025 同源问题）

**影响范围**：
- OBJMall OBJ-01 × 28 TC × 5 条 step 重复 → 阅读体验差（同一动作出现多次）
- 同 Q-025（30 天退款 12 TC 重复 8 个）同源——qa_fixer_v301 dim1 已删 9 个，但 OBJ-01 内 step 重复未触及

**处置决策**：⏳ **移交下一轮（Round 14）**

**理由**：
1. 与 Q-025 同源但范围更窄（仅 OBJ-01 内部）
2. 本轮 qa_fixer_v301 已修复 30 天退款重复（9 个），但未扫"同 OBJ 内 step 重复"
3. SSOT 改动小（仅 s6_generate.py 加约束："同 OBJ 内 unique step action ≥ 80%"）
4. 风险低（仅是数据生成约束，不影响已生成数据）

**下一步动作**（Round 14）：
- s6_generate.py 加"同 OBJ 内 unique step action ≥ 80%"硬约束
- qa_fixer_v301 加 normalizer 步骤：dedup 后再扫一遍 step 重复
- v3.01 数据按需评估是否重扫（5 条重复工作量小，可手动修）

**优先级**：P2（不阻塞 v3.01；5 条重复影响有限）

---

### M-3：A-018 [MINOR] LOG 结构性欠测（同 Q-019）→ ✅ 已修复

**真实描述（§1.3）**：v3.01 LOG 模块仅 1 TP / 1-2 TC

**Round 2 Act 实际修复状态**：
- qa_fixer_v301 dim2 supplement_log_module 已补 30 条 LOG TC（登录日志/支付日志/操作日志/异常日志 4 类 × 6+ 条）
- xlsx LOG 模块从 1 TC 增至 34 TC（gap_report §Module Distribution 表已确认）

**处置决策**：✅ **接受 / 关闭**

**理由**：
1. v3.01 LOG 模块已 34 TC（xlsx）/ 4 TC（JSON 未变）——结构性欠测已修复
2. 本轮 gap_report 已重生成（详见 tc_tp_gap_report.md "Module Distribution" 表 LOG 行：1 TP / 4 TC JSON / 34 TC xlsx）
3. 无后续动作

**优先级**：✅ 已关闭

---

### M-4：A-019 [MINOR] tc_tp_gap_report.md 陈旧（同 Q-018）→ ✅ 本轮已修复

**真实描述（§1.3）**：tc_tp_gap_report.md 写 87 TC，实际 331 JSON / 386 xlsx

**Round 3 Act 实际修复状态**：
- ✅ 本轮 W2 已用 openpyxl + JSON 重新统计，重写 `workflow_assets/.../tc_tp_gap_report.md`：
  - Total S5 TP: 87（不变）
  - Total S6 TC (JSON, out_of_scope): 331
  - Total S6 TC (xlsx, post Round 2 Act): 386 + 1 附录
  - Coverage: 100% (87/87)
  - 含 Module Distribution 表 + Round 2 Act 补测明细
- ✅ 已用 Read tool 验证新 gap_report.md 行数 142、含 87 TP 表行

**处置决策**：✅ **本轮已修复 / 关闭**

**理由**：
1. tc_tp_gap_report.md 已重生成（数据真实同步）
2. A-019 与 BLOCKER Q-018 是同一问题——本轮 W2 一并修复

**后续动作**（F-2 follow-up，Round 14+）：
- gap_report 重生成自动化管线（每次 S6 完成自动跑）
- SSOT 加 "gap_report 是 S6 完成强制子步骤"

**优先级**：✅ 本轮关闭；自动化移交 F-2

---

### M-5：A-020 [MINOR] feature_point_ref 与 fp_name 字段冗余

**真实描述（§1.3）**：S6 TC 同时含 `feature_point_ref`（结构化 OBJ-FP-ID）与 `fp_name`（人类可读 FP 名）——两个字段表达"FP 是哪一个"语义

**影响范围**：
- v3.01 386 TC × 双字段 → 数据冗余 + 同步维护成本（改一处要改两处）
- 字段治理类（与 A-003 / A-004 同类）

**处置决策**：⏳ **移交下一轮（Round 15+）**

**理由**：
1. 字段治理类问题不阻塞业务
2. SSOT 改动需协调（SKILL aidocx-s6-test-cases §六 Schema 删字段 + L1S6Validator 加"禁止 fp_name"行）
3. v3.01 JSON 数据迁移需重生成（**out_of_scope 故不本轮动**）
4. 与 A-003 / A-004 决策档同源——一并移交 SSOT 治理范畴

**下一步动作**（Round 15+）：
- 删除 `fp_name` 字段（`feature_point_ref` 已结构化足以反查）
- L1S6Validator 加一致性行：`feature_point_ref` 存在 → `fp_name` 可选
- 新生成 TC 不再填 `fp_name`（v3.01 JSON 字段按需迁移）

**优先级**：P2（不阻塞 v3.01）

---

## §3 决策汇总

| ID | 标题 | 处置 | 优先级 | Round |
|----|------|------|-------|-------|
| M-1 / Q-013 | 缺机器可读断言字段 | ⏳ 移交 Round 15+ | P2 | 15+ |
| M-2 / Q-026 | 28 TC 中 step 重复 5 条 | ⏳ 移交 Round 14 | P2 | 14 |
| M-3 / A-018 | LOG 结构性欠测 | ✅ 已修复（Round 2 Act） | — | 关闭 |
| M-4 / A-019 | tc_tp_gap_report.md 陈旧 | ✅ 已修复（Round 3 Act W2） | — | 关闭 |
| M-5 / A-020 | feature_point_ref / fp_name 冗余 | ⏳ 移交 Round 15+ | P2 | 15+ |

**MINOR 总览**：
- 已关闭：2 条（M-3 + M-4）
- 移交 Round 14：1 条（M-2，SSOT 改动小）
- 移交 Round 15+：2 条（M-1 + M-5，SSOT 改动大）
- 本轮新增动作：0 条

---

## §4 落档协议执行记录

- **DNA §9.5**：✅ Write 占位后再展开 content
- **DNA §9.4 先验后答**：✅ 已 Read review_13.md §1.3 全文（5 条 MINOR 表格）+ S6 test_cases.json fp_name/feature_point_ref 字段样本
- **改动文件清单**：本档新增 1 个决策档；SSOT / 代码 / 数据 0 改动