# v31 — Achieved（S5/S6 方法论重写收敛报告）

> **Goal**: 重新设计 S5（测试点生成）+ S6（测试用例生成）方法论
> **Goal ID**: v31-s5-s6-methodology-rewrite-001
> **收敛时间**: 2026-07-21
> **收敛轮次**: 5 轮 goal-loop（Round 1 ~ Round 5）
> **状态**: ✅ **ACHIEVED**

---

## 收敛摘要

| 项 | 值 |
|----|----|
| 起 | v31 方法论重写 goal-loop Round 1（2026-07-20）|
| 止 | Round 5 双报告 + achieved 声明（2026-07-21）|
| 历时 | 5 轮 goal-loop |
| 产出文件 | ~14 个核心文件 + S5/S6 产物（v3.01 共 230 TP / 230 TC）|
| 验证 | v3.01 样本跑通 + 4 项覆盖率 100% + TC 字段语义收紧 230/230 PASS |

---

## 核心交付（14 个 v31 文件 + S5/S6 产物）

### v31 治理档（11 个）

| 文件 | 性质 | 大小 |
|------|------|------|
| `v31/PLAN.md` | **正式治理 SSOT**（5 段结构）| 680 行 / 32 KB |
| `v31/coverage_report.md` | 覆盖率自检报告 | 212 行 / 9 KB |
| `v31/v31_方法论_草案.md` | 演进档（Round 1-3 历史版本）| 894 行 |
| `v31/v31_SCC.md` | 故事复杂度系数独立文件 | 218 行 |
| `v31/s8_knowledge_backflow_diagnosis.md` | S8 回灌根因诊断 | 305 行 |
| `v31/audit_1.md` ~ `audit_5.md` | 5 轮 audit 报告 | ~38 KB |
| `v31/review_1.md` ~ `review_5.md` | 5 轮 review 报告 | ~38 KB |
| `v31/CONVERGED.md` | **本文件（achieved 声明）**| — |

### v31 归档（3 个旧残留）

| 文件 | 说明 |
|------|------|
| `v31/archive/s1_5_GOAL.md` | s1-regen-20260720 goal-loop 残留 + 头部注释 |
| `v31/archive/s1_5_PLAN.md` | s1-clarification-redesign-001 PLAN 残留 + 头部注释 |
| `v31/archive/s1_5_CONVERGENCE_VERDICT.md` | S1.5 重设计 CONVERGED 残留 + 头部注释 |

### S5/S6 产物（v3.01 商城样本）

| 文件 | 内容 |
|------|------|
| `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json` | 230 TP（288 KB）|
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` | 230 TC + v31 扩展字段（250 KB）|
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.md` | Markdown 摘要（17 KB）|
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.xlsx` | Excel（10 列 / 20 KB）|

---

## 解决（v30 → v31 闭环）

| # | 项 | 证据 |
|---|----|------|
| **R1** | STAGE_S5/S6 字段契约已有但缺"字段语义收紧"机制 | `v31/PLAN.md` §3.4 三条铁律（A/B/C）|
| **R2** | TP 库为空（v30 不知根因） | `v31/s8_knowledge_backflow_diagnosis.md` + `v31/PLAN.md` §8 两段制归档 |
| **R3** | TP ≤ 50/Story 硬上限不合理（v30 拍脑袋） | `v31/v31_SCC.md` + `v31/PLAN.md` §2.5 SCC 公式 |
| **R4** | 8 模块子类表无 SSOT 索引 | `v31/PLAN.md` §4（CONFIG/UI/BIZ 全展开 + 5 模块引 SSOT 不重写）|
| **R5** | 覆盖率口径不明确（v30 拍脑袋） | `v31/PLAN.md` §6（4 项覆盖率公式）+ `v31/coverage_report.md` 实测 |

---

## 新增（v31 比 v30 多的）

| # | 项 | 证据 |
|---|----|------|
| **A1** | v31 扩展字段（4 个 COULD） | `v31/PLAN.md` §3.2.2 + §9.2 |
| **A2** | TC 字段语义收紧三条铁律 + `is_exploratory` 探索性标注 | `v31/PLAN.md` §3.4 |
| **A3** | SCC 故事复杂度系数（5 维度乘积 + 软下限） | `v31/v31_SCC.md`（独立文件）+ `v31/PLAN.md` §2.5 |
| **A4** | S8 回灌 TP 库契约（两段制 + `pending_candidates` 触发） | `v31/PLAN.md` §8.2-§8.4 |
| **A5** | 关键词快速映射表（50+ 关键词 → module/subclass） | `v31/PLAN.md` §4.3 |
| **A6** | 冲突优先级矩阵（8 行场景） | `v31/PLAN.md` §4.4 |

---

## 遗留（→ v32 治理）

| # | 项 | 严重度 | 处理 |
|---|----|--------|------|
| **L1** | `ssot_citation_path` 字段是否升级为必填 | LOW | 保留 COULD（v32 决策）|
| **L2** | SCC 软下限修订（80% → 50% + 商城加权） | MEDIUM | Round 5 用户 scope-a（不在 PLAN.md 改动，v32 治理）|
| **L3** | UI TP 交叉 S3 prototype（UI 控件级覆盖率） | LOW | `v32_01` |
| **L4** | density-覆盖率（per-OBJ 4 类型齐全率） | MEDIUM | `v32_02` + S7 审查补做 |
| **L5** | 多项目样本回归（v3.01 之外的 2~3 个需求） | MEDIUM | `v32_04` |
| **L6** | 测试点库首批回灌（依赖 S7/S8 实际跑通 + 人工审核） | LOW | `v32_05` |

---

## 影响范围

### 项目层（无改动）

v31 严格遵循"PLAN.md 引而不重写 SSOT"原则：

| SSOT | v31 是否改动 |
|------|-------------|
| `.cursor/MODULES.md` | ❌ 未改（§1.3 声明引 SSOT 不重写）|
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` | ❌ 未改（v31 §3.1.2 字段契约与 STAGE 一致）|
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | ❌ 未改（v31 §3.2.2 字段契约与 STAGE 一致）|
| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 | ❌ 未改（§6 阈值引用 SSOT 常量）|
| `knowledge/public/module_templates/*.md` | ❌ 未改（§4 引用 SSOT 不重写）|
| `.cursor/rules/product_format_rules.yaml` | ❌ 未改（§7.4 引用 SSOT）|

### Agent 层（v31 启用后有确定性输入）

v31 后 S5/S6 LLM 调用时：
- S5 按 §3.1.4 Prompt 模板执行（输入/输出契约 + 推理步骤 + Forbidden + Self-check）
- S6 按 §3.2.4 Prompt 模板执行（同上）
- §3.4 三条铁律作为 LLM 自检 checklist 强制执行
- §8 三段制归档契约作为 S8 产出 schema 约束

### 人审层（v31 启用后可机器校验）

- §6 覆盖率公式提供 `coverage_report.md` 脚本路径（`ai_workflow/coverage_validator.py` 已实现 4 项公式）
- §3.4 三条铁律可通过 `tc.field_traceability` 自动校验
- §7 格式契约通过 `_XLSX_HEADERS_V3` 公共表头自动校验

---

## 跨阶段影响

### 阶段衔接

| 上游 | v31 影响 |
|------|---------|
| S1 / S1.5 / S2 | ❌ 无改动（v31 不重塑三阶段边界）|
| S3 prototype | ⚠️ v32_01 补 UI TP 交叉 |
| S4 business_flow | ✅ v31 §2.1 已纳入必读材料 |
| **S5** | ✅ v31 §2 输入契约 + §3.1 方法论 + §3.1.2 字段契约 + §3.1.4 Prompt |
| **S6** | ✅ v31 §2 输入契约 + §3.2 方法论 + §3.2.2 字段契约 + §3.2.4 Prompt |
| S7 审查 | ⚠️ v31 §3.4 三条铁律新增为 S7 审查员 B 的字段语义校验项 |
| S8 自迭代 | ✅ v31 §8 两段制归档 + `pending_candidates` 触发契约 |

### 知识库影响

| 知识库 | v31 影响 |
|--------|---------|
| `knowledge/public/module_templates/*.md` | ❌ 未改（§4 引用 SSOT 不重写）|
| `knowledge/public/test_point_library/` | ⏳ §8.4 激活阈值（≥ 10 条）短期未触发；v32_05 待首批回灌 |
| `knowledge/project_local/.review_queue/` | ⏳ §8.2 第 1 段归档路径；v32_05 首次触发 |
| `workflow_assets/_governance/recurring_failures.json` | ❌ 未改（§8.5 与 TP 库的区别已显式说明）|

---

## DNA 自检（v31 全过程合规）

- **DNA §9.4（先验后答）**：全部 5 轮所有引用文件已 Read（详见各 round 的 audit / review）
- **DNA §9.1（决策密度）**：每轮 ≤ 5 文件（Round 4 = 5 / Round 5 = 3，符合上限）
- **DNA §9.5（落档协议）**：PLAN.md / coverage_report.md / CONVERGED.md 等关键文件先 Write 后 content 展开
- **DNA §10（人本可审查）**：所有名词具体（商城 v3.01 / OBJ 36 / FP 99 等），不堆术语
- **DNA §11（格式干净）**：无 v2 / ISO 时间戳 / 禁止 JSON 字段等违规（已通读 `product_format_rules.yaml`）
- **DNA §1 准则 1（一致性）**：v31 后所有 .mdc / SKILL.md / 产物对齐，§10.1 C1~C6 全部 PASS
- **DNA §1 准则 4（人本可审查）**：影响范围（项目层/Agent 层/人审层）+ 影响文件清单具体可查

---

## 跨阶段影响速查

| 角色 | 必读 | 必看 | 必记 |
|------|------|------|------|
| **Agent 执行 S5/S6** | `v31/PLAN.md` §3.1.4 / §3.2.4 Prompt | `v31/v31_SCC.md` | §3.4 三条铁律 |
| **项目流程审查** | `v31/PLAN.md` 全文 | `v31/coverage_report.md` | C1~C6 验收证据 |
| **人工审核 S8 候选** | `v31/PLAN.md` §8 | `v31/s8_knowledge_backflow_diagnosis.md` | §8.3 `pending_candidates` 字段定义 |
| **下一轮 goal-loop** | `v31/review_5.md` §v32 治理路线 | `v31/audit_5.md` 反向挑战 7 条 | L1~L6 6 项遗留 |

---

## 收敛证据链

| 链路段 | 证据文件 | 行号 |
|--------|---------|------|
| C1 方法论沉淀 | `v31/PLAN.md` | §2, §3, §6, §9 |
| C2 通用性验证 | `v31/coverage_report.md` §1 | §1.1~§1.5 |
| C3 知识库贯通 | `v31/PLAN.md` §4 | §4.1~§4.4 |
| C4 覆盖率口径 | `v31/coverage_report.md` §1 | 4 项 100% |
| C5 格式干净 | `v31/coverage_report.md` §2 + §3 | TC 字段语义收紧 230/230 |
| C6 落档完整 | `v31/PLAN.md` + `coverage_report.md` + `archive/` | 14 文件 |
| 反向挑战 7 条 | `v31/audit_5.md` §反向挑战 | §反向挑战 1~7 |
| 遗留 6 项 | `v31/review_5.md` §Round 5 缺陷 | D1~D6 |
| v32 治理路线 | `v31/review_5.md` §v32 治理路线 | v32_01~v32_05 |

---

> **v31 ACHIEVED** —— S5/S6 方法论重写闭环，下一轮 v32 治理路线开启（建议起跑时间：v31 achieved 后 1~2 周）
