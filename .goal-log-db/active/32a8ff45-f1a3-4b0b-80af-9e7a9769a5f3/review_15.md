# Round 15 Review — Act 阶段根因复盘 + 修复方案

> **性质**：Goal-loop review（按 `aidocx-s1-5-clarification` 等 SKILL §3.3 三段式模板）
> **Goal**: 32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3（游戏道具商城 v3.01 test_cases_public.xlsx）
> **复盘轮次**: Round 15（loop_round=5）
> **复盘人**: 架构师 worker
> **复盘时间**: 2026-07-19
> **来源**: audit_15.md 2 项 MINOR follow-up

---

## §1 缺陷汇总

### 1.1 数量与分级

| severity | 总数 | 本轮新发现 | 已修复 | 留 follow-up |
|---|---|---|---|---|
| BLOCKER | 0 | 0 | 0 | 0 |
| MAJOR | 0 | 0 | 0 | 0 |
| MINOR | 2（F-E / F-F） | 0 | 2 | 0 |
| **合计** | **2** | **0** | **2** | **0** |

### 1.2 F-E / F-F 缺陷明细

#### F-E：缺机器可读断言字段

- **症状**：v3.01 386 TC × 缺 `assertion` 字段；QA 跑用例需人工翻译 `expected_results` 文本 → 自动化执行能力受限
- **影响范围**：S6 阶段产出物 + S7 审查 + QA 执行 + 自动化测试脚本
- **影响深度**：MINOR（不阻塞 v3.01 业务发布；限制自动化覆盖率）

#### F-F：feature_point_ref / fp_name 字段冗余

- **症状**：v3.01 386 TC × 双字段（`feature_point_ref` 结构化 OBJ-FP-ID + `fp_name` 人类可读 FP 名）
- **影响范围**：S6 字段定义 + L1 校验器 + Round 17 SSOT 物化
- **影响深度**：MINOR（字段治理类，与 A-003 / A-004 同源；不阻塞业务）

### 1.3 与上一轮缺陷的对比

| Round | 缺陷数（总数） | 修复数 | follow-up |
|---|---|---|---|
| Round 14 (loop_round=4) | 4 | 2 | 2（F-E / F-F） |
| Round 15 (loop_round=5) | 2 | 2 | 0 |

---

## §2 根因分析（Root Cause）

### 2.1 F-E 根因：规格层缺位（Specification Gap）

**机制层根因**：
- S6 SKILL.md 早期版本未约束 `assertion` 字段——LLM 推理时只生成 `expected_results` 文本（自然语言），未结构化为机器可读断言
- L1 校验器（L1S6Validator / l1_format_validator 基类）未提供 `assertion` 完整性检查 helper

**规格层根因**：
- SSOT §六 Schema 段仅列已用字段，未前瞻性设计"机器可读断言"层
- 决策档 `s6_id_dedupe_decision.md` 仅修订 `tc_id` 冗余，未涉及 assertion 字段治理

**触发条件**：v3.01 386 TC 数据沉淀期（资深测试 Q-019 / 架构师 A-018 / 资深产品 P12 三方共识时已识别）

### 2.2 F-F 根因：双字段治理类（Specification Drift）

**机制层根因**：
- Round 17 SSOT 物化时，`feature_point_ref`（结构化 OBJ-FP-ID）+ `fp_name`（人类可读）同时并存
- LLM 推理时为求稳定两字段都生成（保守策略），但维护成本翻倍
- `feature_point_ref` 已结构化足以反查 FP 元数据，`fp_name` 实质冗余

**规格层根因**：
- §NAME-FIELD-001 段（Round 17 物化）当时未前瞻"双字段治理"问题
- §六 Schema 段未显式声明字段主键优先级

**触发条件**：v3.01 386 TC × 双字段维护成本（资深架构师 A-019 在 Round 2 Act 已识别）

---

## §3 修复方案

### 3.1 F-E 修复落地（4 件套）

| # | 落地项 | 文件 | 行数变化 |
|---|---|---|---|
| 1 | §六 Schema 加 assertion 字段模板 + 4 个示例 | `aidocx-s6-test-cases/SKILL.md` | +30 行 |
| 2 | §三自检流程 + 常见错误对照表加 assertion 强制 | `aidocx-s6-test-cases/SKILL.md` | 包含在 #1 |
| 3 | §11 自检清单 + json 评审门禁加 assertion 完整性 | `aidocx-s6-test-cases/SKILL.md` | +2 行 |
| 4 | `check_assertion_completeness(min_count=1)` + 4 self-test | `l1_format_validator.py` | +120 行 |

### 3.2 F-F 修复落地（5 件套）

| # | 落地项 | 文件 | 行数变化 |
|---|---|---|---|
| 1 | §六 Schema 加 fp_name 历史字段注释 | `aidocx-s6-test-cases/SKILL.md` | +8 行 |
| 2 | §NAME-FIELD-001 规则 1/3 描述改（"fp_name 已 F-F 删除，请用 feature_point_ref 反查"） | `aidocx-s6-test-cases/SKILL.md` | 包含在 #1 |
| 3 | 常见错误对照表加 fp_name 警告 + §11 自检清单同步 | `aidocx-s6-test-cases/SKILL.md` | +4 行 |
| 4 | LOG seed / 业务盲区 seed fp_name 字段加注释（保留兼容 v3.01 fixer 实际产物） | `aidocx-s6-test-cases/SKILL.md` | +4 行 |
| 5 | `check_no_fp_name_field(mode="warn")` + 3 self-test | `l1_format_validator.py` | +60 行 |

### 3.3 修复策略原则

| 原则 | 体现 |
|---|---|
| **SSOT 与 L1 同步** | SSOT 修订 + L1 校验器 helper 同时落——避免 Round 1/2 已踩坑的 SSOT-LLM 不同步 |
| **LLM Prompt 隐式约束** | 自检流程段即视为 LLM 强制约束——LLM 生成时必读 |
| **out_of_scope 守** | v3.01 JSON 字节不变（338192 不变）；xlsx 字节不变（41572 不变） |
| **mode 双档** | `mode="warn"`（默认）兼容 v3.01 legacy；`mode="error"` 强约束新数据（与 F-D tc_id 策略一致） |
| **§9.5 落档协议** | `round15_q_decision_table.md` 已先 Write 占位后 content 展开 |

---

## §4 新 follow_up_items

**结论**：✅ **本轮 2 项全部 PASS，无遗留 follow_up_items**

| ID | 描述 | severity | 状态 |
|---|---|---|---|
| — | （无） | — | follow_up_count = 0 |

---

## §5 收敛判定

| 维度 | 值 | 判定 |
|---|---|---|
| `follow_up_count` | 0 | ✅ 全部清空 |
| `status` | `achieved` | ✅ 目标达成 |
| `loop_round` | 5 | ✅ Round 5 收敛 |
| `efficiency_stats.convergence_round` | 5 | ✅ Round 5 收敛 |
| `efficiency_stats.total_iterations` | 5 | ✅ 5 轮迭代 |
| `efficiency_stats.follow_up_count` | 0 | ✅ 无遗留 |
| `test_cases_json_bytes_unchanged` | true | ✅ 严守 out_of_scope |
| `test_cases_xlsx_bytes_unchanged` | true | ✅ 严守 out_of_scope |

---

> 本 review 档：`review_15.md`（loop_round=5）
> 配套 audit 档：`audit_15.md`
> 配套决策档：`governance/design_iter/current/round15_q_decision_table.md`
> 配套 snapshot：`.goal-log-db/active/32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3/snapshot.json`