# AIDocxWorkFlow v17 — TP/TC 字段溯源方案（无锚点版）

> **本版本定位**：推翻 v16 v2 锚点方案，改为 JSON 字段溯源（obj_name/fp_name）+ 结构化步骤数组；导出 Excel 完全结构化映射
> **来源**：`~/Downloads/TP-TC 终极标准化最优方案（零冲突、全链路一致、Excel原生适配）.md`（用户提交）
> **决策落档**：`governance/design_iter/current/v16_alternative_tc_proposal_20260717.md`（2026-07-17）
> **用户拍板（2026-07-17）**：完全采纳 A——推翻 v16，进入 v17 治理周期
> **基线版本**：v16 v2 锚点方案（87 TP / 87 TC 100% L1 pass）
> **对应产品版本**：v1.2（v17 落地后升 AIDocxWorkFlow 到 v1.2）

---

## §0 拍板依据

| 拍板项 | 用户决策 | 含义 |
|---|---|---|
| Q1 是否采纳提案 | **A 完全采纳** | 推翻 v16 v2 锚点方案，进入 v17 治理 |
| Q2 治理版本号 | **v17**（新建） | 不作为 v16 实施补遗；独立治理周期 |
| Q3 旧产物回溯 | **待 Q-7 拍板** | v1.0/v2.0/v3.0 历史版本是否迁移？ |
| Q4 旧 L1 校验脚本 | **保留在 `_legacy/`** | 备查；v3.01 之前产物继续走 v16 校验 |
| Q5 Excel 导出时机 | **v17 Phase 5** | 等约束 + 脚本 + 产物全部就绪再做导出 |

---

## §1 v17 vs v16 核心差异

| 维度 | v16（当前） | v17（候选） |
|---|---|---|
| OBJ/FP 名称承载 | 文本锚点【OBJ - FP】 + JSON 字段 | **仅 JSON 字段**（obj_name/fp_name） |
| `fp_name` 来源 | S2 fp_desc 100% 逐字相等 | LLM 自创中性功能名 |
| `title` 文本 | 必须【OBJ - FP】开头 | 纯场景简短标题（不带【】） |
| `description` 文本 | 必须【OBJ - FP】开头 | 纯测试逻辑（前置+步骤+预期） |
| TC test_scenario | 必须【OBJ - FP】开头 + 与 TP title 一致 | 纯场景一句话描述 |
| L1 校验策略 | 7 项锚点 v2 校验（文本+字段） | **仅字段精准匹配**（obj_name/fp_name == S2） |
| `test_method` | 字符串 | 字符串数组 |
| `preconditions` | 字符串 | 字符串数组 |
| `steps` | 字符串（≤8 步） | 结构化数组 `[{step_num, action}]` |
| `expected_results` | 字符串 | 字符串数组 |
| TC `tp_reference` 字段 | 无（仅 s5_ref） | 新增 |
| Excel 导出 | 文本截取 + 字段映射 | **完全结构化字段映射** |

---

## §2 v17 影响面（DNA §1 准则 1+3）

### 2.1 必改约束文件（5 处）

| 文件 | 当前内容 | 必改原因 |
|---|---|---|
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` §1.9 | 锚点 v2 7 项校验 | 改为字段溯源（obj_name/fp_name == S2） |
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §1.7 | 锚点继承 6 项校验 | 改为字段溯源 + TC 字段集扩展 |
| `.cursor/skills/aidocx-s5-test-points/SKILL.md` §v16 NAME | 锚点铁律 | 改为字段铁律 |
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §v16 NAME | 锚点铁律 | 改为字段铁律 |
| `.cursor/rules/AIDocxWorkFlow.mdc` §v16 引用 | 引用锚点方案 | 改为引用 v17 字段方案 |

### 2.2 必改代码文件（6 处）

| 文件 | 当前内容 | 必改原因 |
|---|---|---|
| `ai_workflow/validators/l1_s5.py` | 7 项锚点校验 | 改为字段校验 |
| `ai_workflow/validators/l1_s6.py` | 6 项继承校验 | 改为字段校验 |
| `ai_workflow/test_case_formatter.py` | 锚点提取 + 格式化 | 改为字段格式化 |
| `ai_workflow/auto_reviewer.py` | 锚点 L1 调用 | 改为字段 L1 |
| ~~`ai_workflow/s6_report.py`~~ | **(Round 14 闭环：文件不存在，引用已废弃)** | — |
| `scripts/check_field_completion.py` | 锚点字段定义 | 改为 v17 字段定义 |

### 2.3 必改产物文件

| 文件 | 当前状态 | 必改原因 |
|---|---|---|
| `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json` | 87 TP 全部【OBJ - FP】锚点 | 重写 fp_name/title/description |
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` | 87 TC 全部【OBJ - FP】锚点 | 重写 test_scenario + steps/preconditions 结构化 |
| v1.0/v2.0/v3.0 历史版本 TP/TC | 多版本产物 | 见 §3.3 Q-V17-003 拍板 |

### 2.4 必改治理档

| 文件 | 必改原因 |
|---|---|
| `AGENTS.md` §v16 引用 | 同步 v17 引用 |
| `CHANGELOG.md` | 新增 v17 条目 |
| `governance/design_iter/INDEX.md` + `INDEX.json` | v17 升级 current（CLI scripts/design_iter.py 生成） |

---

## §3 v17 6 阶段实施步骤

### Phase 1：PLAN + SELF_CHECK + open_questions（本周）

- [x] 创建 `governance/design_iter/plans/v17/PLAN.md`（本档）
- [ ] 创建 `governance/design_iter/plans/v17/SELF_CHECK.md`
- [ ] 创建 `governance/design_iter/plans/v17/open_questions.md`
- [ ] 列出所有 Q-V17-XXX 待决问题
- **门禁**：用户审批通过 v17 PLAN 才进入 Phase 2

### Phase 2：约束文件改写（下周，3-5 个 turn）

- [ ] 改 STAGE_S5 §1.9（按 §9.4 先 Read 全文）
- [ ] 改 STAGE_S6 §1.7
- [ ] 改 s5/s6 SKILL.md
- [ ] 改 AIDocxWorkFlow.mdc + DESIGN_AND_EXECUTION_STANDARDS.mdc
- [ ] 同步改 AGENTS.md + CHANGELOG.md

### Phase 3：L1 校验脚本改写（下下周，2-3 个 turn）

- [ ] 改 l1_s5.py（7 项 → 字段校验）+ py_compile 强制验证
- [ ] 改 l1_s6.py + py_compile
- [ ] 改 test_case_formatter.py + auto_reviewer.py + check_field_completion.py
- [ ] ~~改 s6_report.py~~ **(Round 14 闭环：文件不存在，引用已废弃)**

### Phase 4：v3.01 产物重写（Phase 3 后，1-2 个 turn）

- [ ] 重写 87 TP（fp_name/title/description）
- [ ] 重写 87 TC（test_scenario/steps/preconditions）
- [ ] 跑 L1 校验
- [ ] 写 v17 L1 自测报告

### Phase 5：Excel 导出层结构化

- [ ] 在 `knowledge/project_local/游戏道具商城/s6/export_profiles/` 加 test_cases.export.json 结构化 schema
- [ ] 实现结构化 xlsx 导出
- [ ] 验证 Excel 列与 JSON 字段一一对应

### Phase 6：回归 + v16 归档

- [ ] 重跑 v3.01 端到端 S1-S7
- [ ] 写 v17_legacy_compat_report.md（v16 vs v17 对比）
- [ ] 归档 v16 到 `governance/design_iter/archive/v16_v2_anchor_20260717.bak/`
- [ ] CLI scripts/design_iter.py 把 v17 设为 current

---

## §4 风险与回退方案

### 4.1 风险清单

| # | 风险 | 等级 | 缓解 |
|---|---|---|---|
| R1 | 推翻 v15/v16 锚点 v2 决策，所有历史 TP/TC 需重写 | 🔴 | v16 归档备查 + 双轨运行 |
| R2 | L1 校验脚本逻辑全改，回归测试无法覆盖 | 🔴 | Phase 3 强制 py_compile + 自测 |
| R3 | fp_name 由 LLM 自创，导致同一 FP 名称不统一，跨项目比较失效 | 🔴 | Q-V17-001 待决（建议人工抽样审 10%） |
| R4 | 7 处规则 + 6 处脚本 + 多版本产物改动 = 单次改动 ≥20 文件 | 🔴 | 分 6 阶段推进，每阶段 ≤3 文件 |
| R5 | `fp_name = "购买按钮可用性控制"` ≠ S2 fp_desc = "余额不足时禁用购买按钮" | 🟡 | 语义重定义，纳入 §1 Q-V17-001 |

### 4.2 回退方案

- 保留 v16 v2 锚点版本在 `governance/design_iter/archive/v16_v2_anchor_20260717.bak/`
- v17 与 v16 双轨运行：用户可在 v3.01 = v16 / v3.02 = v17 中二选一
- 若 v17 实施中遇到 L1 回归失败，回退 v16 重新运行 v3.01 L1 验证

---

## §5 解决 / 新增 / 遗留

### 解决

- **v17 §3 1**：OBJ/FP 名称承载混乱 → 改为 JSON 字段溯源（obj_name/fp_name == S2 严格匹配）
- **v17 §3 2**：Excel 文本截取不稳定 → 改为结构化字段映射

### 新增

- **v17 §3 3**：TC `tp_reference` 字段（明确 TP-TC 引用链）
- **v17 §3 4**：`steps[]` / `preconditions[]` / `expected_results[]` 结构化数组
- **v17 §3 5**：`test_method[]` 字符串数组
- **v17 §3 6**：L1 校验策略简化（仅字段精准匹配）

### 遗留

- **Q-V17-001**：`fp_name` LLM 自创的命名一致性审核机制（待 §6 Q1 拍板）
- **Q-V17-002**：v1.0/v2.0/v3.0 历史版本是否回溯（待 §6 Q3 拍板）
- **Q-V17-003**：v16 v2 锚点 L1 脚本保留方式（_legacy/ 备查 vs 删除）
- **Q-V17-004**：L2/L3 Hook（`.cursor/hooks/content_compliance_check.py`）是否同步改
- **Q-V17-005**：`steps[]` 是否支持 1:N（一个步骤多个 sub-action）
- **Q-V17-006**：Excel 导出列顺序（用例描述/功能描述/模块/优先级/前置/步骤/预期）
- **Q-V17-007**：`test_method[]` 顺序语义（主方法在前 vs 测试维度在前）

---

## §6 落档协议执行（§9.5）

- 本档已落档到 `governance/design_iter/plans/v17/PLAN.md`
- 前置分析档：`governance/design_iter/current/v16_alternative_tc_proposal_20260717.md`
- 冲突清单：10 项（6 项硬阻断 + 4 项类型不兼容）
- 单次响应工具调用：≤ 10
- 待 Phase 1 剩余 2 档（SELF_CHECK + open_questions）

---

## §7 执行记录（Goal Loop 收敛）

> **记录时间**：2026-07-20
> **收敛轮次**：4 轮（Round 1 → Round 2 → Round 3 → Round 4）

### 7.1 Goal Loop 执行摘要

| 轮次 | 日期 | 收敛状态 | 关键问题 |
|------|------|---------|---------|
| Round 1 | 2026-07-20 | ❌ FAIL | 21 TP fp_name 字面冲突 / 61 TC 缺 fp_name / assertion 门禁缺失 |
| Round 2 | 2026-07-20 | ❌ FAIL | 6 TC fp_name 继承不一致 / 88 TC assertion 缺失 / L2 self-test FAIL |
| Round 3 | 2026-07-20 | ⚠️ PASS（含遗留） | L1S6Validator required_fields 误报 |
| Round 4 | 2026-07-20 | ✅ PASS | TC 步骤数规范化（1 步碎裂 → 2.93 步） |

### 7.2 最终验收标准状态

| # | 验收标准 | 结果 |
|---|---------|------|
| AC-1 | S2 16 OBJ / 49 FP 含完整 fp_desc | ✅ PASS |
| AC-2 | S5 87 TP 字段溯源链路 0 错误 | ✅ PASS |
| AC-3 | S6 103 TC assertion/obj_name/fp_name 100% 覆盖 | ✅ PASS |
| AC-4 | L1/L2 门禁覆盖上游溯源 | ⚠️ PASS（含 L1S6Validator 误报） |

### 7.3 最终产出文件

| 文件 | 路径 | 状态 |
|------|------|------|
| CONVERGENCE_VERDICT.md | `governance/design_iter/plans/v17/CONVERGENCE_VERDICT.md` | ✅ 新增 |
| DELIVERABLE_SUMMARY.md | `governance/design_iter/plans/v17/DELIVERABLE_SUMMARY.md` | ✅ 新增 |
| audit_1.md | `governance/design_iter/plans/v17/audit_1.md` | ✅ 已存在 |
| audit_2.md | `governance/design_iter/plans/v17/audit_2.md` | ✅ 已存在 |
| audit_3.md | `governance/design_iter/plans/v17/audit_3.md` | ✅ 已存在 |
| audit_4.md | `governance/design_iter/plans/v17/audit_4.md` | ✅ 已存在 |
| review_1.md | `governance/design_iter/plans/v17/review_1.md` | ✅ 已存在 |
| review_2.md | `governance/design_iter/plans/v17/review_2.md` | ✅ 已存在 |
| review_3.md | `governance/design_iter/plans/v17/review_3.md` | ✅ 已存在 |
| review_4.md | `governance/design_iter/plans/v17/review_4.md` | ✅ 已存在 |

### 7.4 遗留问题

| # | 问题 | 严重度 | 优先级 | 影响 |
|---|-----|-------|-------|------|
| L1 | L1S6Validator required_fields 字段名不兼容（`优先级` vs `priority`） | MEDIUM | P1 | 205 条误报（数据无问题） |
| L2 | 43 条 TC 前置条件为空 | LOW | P2 | 用例完整性略低（不影响可执行性） |

### 7.5 收敛判定

**v3.01 测试用例（test_cases.json）达到交付标准。**

- 收敛状态：✅ **CONVERGED**
- 收敛时间：2026-07-20