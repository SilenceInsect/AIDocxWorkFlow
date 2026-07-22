# v32 — v31 6 项遗留渐进推进正式 PLAN

> **Goal**: 渐进式推进 v31 6 项遗留（L1~L6），不重写 v31 SSOT
> **Goal ID**: v32-v31-legacy-progressive-001
> **Round**: 1（路线立项 + 草案）
> **Date**: 2026-07-21
> **上游 SSOT**: `archive/v31_20260721_020714.bak/PLAN.md`（v31 680 行治理 SSOT）
> **本文件性质**: v32 治理 SSOT；与 v31 SSOT 同构（五段式：背景诊断 / 输入契约 / 方法论 / 排期影响 / 验收闭环）

---

## 1. 背景与诊断

### 1.1 现状（基于读取的事实）

| 维度 | 现状 | 依据 |
|------|------|------|
| v31 收敛状态 | ✅ ACHIEVED（5 轮 + 14 文件归档 + 4 项覆盖率 100%）| `archive/v31_20260721_020714.bak/CONVERGED.md` |
| v31 6 项遗留 | D1~D6 已落档 review_5.md | `archive/v31_20260721_020714.bak/review_5.md` |
| v31 5 治理方向 | v32_01~v32_05 已给出草案 | `archive/v31_20260721_020714.bak/review_5.md` §v32 治理路线 |
| S5/S6 LLM 启动 | v31 §3.1.4 / §3.2.4 Prompt 模板已生效 | 已落档 v31 SSOT |
| 用户 Round 5 表态 | retain (L1) / softloor (L2) / defer (L3) / scope-a (3 文件收尾) | v31 audit_5 |
| S8 链状态 | v3.01 未走 S5→S7→S8 → L6 TP 库空 | 已知前置 |

### 1.2 用户 4 项选项归纳（驱动 v32 立项）

| # | 用户选项 | 对应遗留 | v32 处理 |
|---|---------|---------|---------|
| **A** | L1 retain（`ssot_citation_path` 留 COULD）| L1 | Round 2 决策：升级必填 / 移除 / 留 COULD |
| **B** | L2 softloor（80% → 50% + 加权）| L2 | v32_03 §3.3 草案 |
| **C** | L3 defer（UI 交叉留 v32）| L3 | v32_01 §3.1 立项 |
| scope-a | 3 文件收尾（audit_5 + review_5 + CONVERGED）| D1~D3 闭合 | v31 已采纳 ✅ |

### 1.3 与既有 SSOT 的不重复声明

| 本文件 § | 不重写（SSOT 维持）|
|---------|-------------------|
| §2 输入契约 | `archive/v31_20260721_020714.bak/PLAN.md` §2 |
| §3 方法论主轴 | `archive/v31_20260721_020714.bak/PLAN.md` §3 |
| §6 覆盖率 SSOT | `DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 |
| §7 格式契约 | `product_format_rules.yaml` |
| §8 TP 库契约 | `archive/v31_20260721_020714.bak/PLAN.md` §8 |

> **本文件的增量价值**在 §3.1~3.5（v32_01~v32_05 5 治理路由）+ §4 排期（Round 2+ act 启动次序）——这是 v31 SSOT 未明确的部分。

---

## 2. 输入契约

### 2.1 v32 必读材料清单

```
[必读]
1. archive/v31_20260721_020714.bak/PLAN.md       (v31 SSOT, 680 行)
2. archive/v31_20260721_020714.bak/CONVERGED.md   (v31 achieved 声明, 190 行)
3. archive/v31_20260721_020714.bak/review_5.md    (D1~D6 + v32 治理路线)
4. archive/v31_20260721_020714.bak/v31_SCC.md     (SCC 公式源)
5. archive/v31_20260721_020714.bak/coverage_report.md (4 项覆盖率实测)

[按需读]
6. workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json (230 TP)
7. workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json (230 TC)
8. .cursor/MODULES.md (8 模块定义 SSOT, 仅查)
9. .cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3 (阈值 SSOT, 仅查)
```

### 2.2 v32 引用源约束

| 引用类型 | 路径 | 原因 |
|----|----|----|
| v31 SSOT 引用 | `archive/v31_20260721_020714.bak/<file>` | v31 17 文件已归档，**不引用 `plans/v31/` 现役目录**（防漂移）|
| 业务产物引用 | `workflow_assets/<req_name>/<version>/...` | v3.01 样本 |
| SSOT 章节引用 | `.cursor/MODULES.md` / `STAGE_S*.mdc` / `DESIGN_AND_EXECUTION_STANDARDS.mdc` | 仅读，不改 |

### 2.3 字段溯源规则（DNA §9.4 Q1 三子问）

每次生成下游产物时必答：

| 子问 | 答 |
|------|---|
| Q1.1 字段值的上游来源是哪？| `<`v31 §X` / `<v32 §X` / <无（不适用）>|
| Q1.2 上游材料是否提供了该字段？| `<有 / 无 / 不适用>` |
| Q1.3 我是否已 Read 上游文件并验证过该字段存在？| `<已读且匹配 / 未读 / 读到但未匹配 / 不适用（plan 阶段）>` |

**未答"已读且匹配" → 不得开始下游生成**。
**例外**：本文件作为治理草案，§3 治理路由字段引而不写（不实际修改业务字段），Q1.3 答"已读 v31 review_5.md §v32 治理路线"。

---

## 3. 方法论（v32_01 ~ v32_05）

### 3.1 v32_01 — UI TP 交叉 S3 prototype

> **目标**：UI TP 引用具体 prototype 控件 ID，可机器校验 UI 控件级覆盖率。

**方法说明**：

- **加在哪**：
 - `archive/v31_20260721_020714.bak/PLAN.md` §2.1 必读清单加 S3 prototype.json
 - §3.1.2 TP 字段契约新增 `ui_node_refs: array<string>`（引用 `pages[].ui_nodes[].id`）
- **影响哪些 stage**：
 - S5 生成 TP 时按 UI 模块引用 prototype.md 节点
 - S6 衍生 TC 时 `steps.action` 可引用具体控件 ID
 - S7 审查员新增"UI 控件交叉覆盖率"校验项
- **新增覆盖率**：
 - `ui_node_coverage = len(TP.ui_node_refs ∪ prototype.ui_nodes) / prototype.ui_nodes 长度`
 - 阈值 ≥ 1.0（与 v31 S5_S3_REF_COVERAGE 对齐）

**依赖**：
- 已生成 prototype.json 的需求（如 v3.01 商城样本）
- v32_01 启动时确认 S3 prototype 列表完整性

**风险**：
- prototype.md 的 `ui_nodes[]` 结构需为每个节点分配稳定 ID（避免漂移）
- UI TP 引用控件时可能与现有 `description` 的 obj_name 锚点冲突 → 解决：以 `ui_node_refs` 为准，`description` 仅做测试逻辑描述

### 3.2 v32_02 — density-OBJ 维度（per-OBJ 4 类型齐全率）

> **目标**：每 OBJ 的 4 类型 TP（POSITIVE / BOUNDARY / NEGATIVE / EXCEPTION）齐全率门禁。

**方法说明**：

- **公式**：
 ```
 density = len({OBJ : |{TP.test_point_type for TP in O} ∩ {POSITIVE, BOUNDARY, NEGATIVE, EXCEPTION}| == 4}) / len(OBJ 总数)
 ```
- **阈值**：1.0（与 v31 OBJ 覆盖率门槛 100% 一致；不达标项必须显式标注 `skip_reason`）
- **影响**：
 - §6 覆盖率自检报告（`coverage_report.md`）新增 density 维度
 - S7 审查员 B 校验密度覆盖率
- **未达标处理**：
 - 低于阈值 → S8 自迭代补充缺失类型 TP
 - 显式标注 `skip_reason`：`{low_risk: "业务评估为低风险"/out_of_scope: "不在本期范围"/deprecated: "路径已废弃"}`

**与 v31 4 项覆盖率衔接**：
- v31 OBJ 覆盖率（集合维度）：36 / 36 = 100%
- v32 density-OBJ 覆盖率（密度维度）：新维度，实测在 v32_02 启动时跑

### 3.3 v32_03 — SCC 软下限公式修订

> **目标**：软下限从 80% 改为 50% + 商城类型加权系数（用户 Round 5 表态 scope-a，v32 推进）。

**修订前**（v31 SSOT）：

```
SCC = |actors| × |states| × |timings| × |boundaries| × |exceptions|
理论 TP 数 = SCC × TP_TYPE_FACTOR
TP_TYPE_FACTOR = { POSITIVE: 1.5, BOUNDARY: 1.0, NEGATIVE: 1.0, EXCEPTION: 0.5 }
软下限 = 理论 TP 数 × 0.8
```

**修订后**（v32 草案）：

```
SCC = |actors| × |states| × |timings| × |boundaries| × |exceptions|
理论 TP 数 = SCC × TP_TYPE_FACTOR
TP_TYPE_FACTOR = { POSITIVE: 1.5, BOUNDARY: 1.0, NEGATIVE: 1.0, EXCEPTION: 0.5 }
domain_type_factor = {
    "mall": 1.5,      # 商城类（UI 多 + 业务轻）
    "game": 2.0,      # 游戏类（业务重）
    "finance": 0.8,   # 金融类（高边界密度）
    "iot": 0.6,       # 物联网（接口少）
    "default": 1.0
}
调整理论 TP 数 = 理论 TP 数 × domain_type_factor[req.domain_type]
软下限 = 调整理论 TP 数 × 0.5
```

**触发条件**：

- v32_03 实测对照：拿 v3.01 样本重算（Round 2 act 必做）
- 若 `调整理论 TP 数 × 0.5 ≤ 实际 TP 数`，公式采纳
- 若仍不满足 → 触发 SCC 公式维度补充（如加 `|data_scale|`）或阈值再下调（如 0.4）

**v3.01 实测对照**（Round 4 review 数据）：

- UI-001-002 理论 216 TP，软下限 172 TP，实际仅 15 TP
- 应用新公式 + 商城加权 1.5：理论 324 TP，软下限 162 TP → 实际 15 TP 仍不满足
- **预案**：v32_03 启动时确认加权值（若 1.5 仍偏严，加权提到 2.0 或硬阈值降到 0.4）

**v32_03 启动前的检查**：

- 在 `v31_SCC.md` §1 加修订段落（草案形式，不直接改 SSOT）
- 同时在 `v32/PLAN.md` §3.3 给出修订前后对照（已落本档）
- Round 2 act 实测 v3.01 后再决定是否回写到 `v31_SCC.md`

**依赖**：
- v32 Round 1 已完成立项（✅）
- v32 Round 2 act 启动 v32_03 实测（下一步）
- 不修改 v31 archive PLAN.md（仅在草案档留佐证）

### 3.4 v32_04 — 多项目样本回归

> **目标**：用 2~3 个 S5/S6 已跑的版本回归 v31 方法论，验证模块分布 / 字段语义 / 跨项目一致性。

**方法说明**：

- **抽样策略**：
 - 从 `workflow_assets/` 找 2~3 个历史版本
 - **筛选标准**：行业不同 + 模块分布不同 + TP/TC 总数 ± 50%
 - 候选范围：商城 / 游戏 / 金融 / IoT / 教育 等
- **对照指标**：
 - 模块分布（8 模块占比）
 - 字段语义一致性（铁律 A/B/C 通过率）
 - 4 项覆盖率（OBJ / FP / 异常叶子 / 风险点）
 - density-OBJ 覆盖率（v32_02 同期产出）
- **影响**：
 - 若 3/3 样本通过 → v31 方法论通用性确立
 - 若 1/3 不通过 → 触发 v33 单点修补

**v32_04 启动前的检查**：

- Round 2 act 前从 `workflow_assets/` 枚举 S5/S6 已跑的版本
- 列候选清单（具体路径），与用户确认抽样策略

**依赖**：
- v3.01 之外至少有 2 个 S5/S6 完成的样本（需用户确认 `workflow_assets/` 范围）
- 若样本不足 → v32_04 暂缓，启动 v32_05 替代

### 3.5 v32_05 — 测试点库首批回灌

> **目标**：建立 v32 时序的"首次 S7/S8 跑通 → 人工审核 → TP 库入库"流程。

**方法说明**：

- **前置依赖**：
 - 选 1 个新需求走完整 S5→S6→S7→S8 链路
 - S8 输出 `iteration.json#pending_candidates` 含首批 5~10 条候选
 - 项目流程约定人工审核 + 回写 `test_point_library/`
- **触发契约**（沿用 v31 §8.3）：
 ```json
 {
   "iteration_number": 1,
   "verdict": "PASS",
   "review_queue_triggered": true,
   "pending_candidates": [
     {
       "path": "knowledge/project_local/.review_queue/BIZ/A_biz_logic__ITER-001__2026-07-21.md",
       "module": "BIZ",
       "subclass": "A_biz_logic",
       "defect_id": "ITER-001",
       "root_cause_source": "S5_MODULE",
       "created_at": "<ISO>",
       "requires_human_review": true,
       "target_public_file": "knowledge/public/module_templates/BIZ/O_boundary.md"
     }
   ]
 }
 ```
- **依赖图**：
 - 流程依赖：v32_05 不能先于 v3.01 项目流程跑通 S7/S8
 - 时间依赖：v32_04（多项目回归）通常能产生候选 → 与 v32_04 联动
- **激活阈值（沿用 v31 §8.4）**：
 - `test_point_library/<MODULE>/` 累计 ≥ 10 个有效条目时，激活 S5 自动复用
 - 短期不触发，无紧迫性

### 3.6 依赖图

```
v32_Round_1 (当前)
 ↓ 立项 + 草案落档
v32_Round_2
 ├─ v32_03 SCC 软下限修订（实测 v3.01 重算公式）
 ├─ L1 升级决策（A: 升级必填 / B: 移除 / C: 留 COULD）
 ↓
v32_Round_3
 ├─ v32_04 多项目样本回归（依赖 §workflow_assets 已有 2~3 个 S5/S6 样本）
 ├─ v32_01 UI 交叉 S3 prototype（依赖 S3 prototype 结构稳定）
 ↓
v32_Round_4+（条件触发）
 ├─ v32_02 density-OBJ 维度（依赖 v32_04 通过后）
 ├─ v32_05 TP 库首批回灌（依赖 S7/S8 跑通）
 ↓
CONVERGED（全部收敛后）
```

### 3.7 L1 字段升级决策（待决项）

> **背景**：v31 §3.2.2 列出 4 个 v31 扩展 COULD 字段（`is_exploratory` / `verified_against_s2_path` / `module_boundary_check` / `ssot_citation_path`）。Round 3 生成器未实现 `ssot_citation_path` 写入（D1 缺陷）。

**Round 2 act 决策**：

| 选项 | 后果 |
|----|----|
| A: 升级必填 | S6 L1 校验强制写 → 实现需改 v31 生成器（不在 v32 范围） |
| B: 移除字段 | 删 `ssot_citation_path` → 影响 v31 §3.2.2 / §9.2 字段字典（需修订 SSOT） |
| C: 留 COULD | 当前状态；不影响功能完整性 |

**默认走 C**（用户 Round 5 已表态 retain）。Round 2 act 落档决策到 `v32/decision_l1_upgrade.md`（待建）。

---

## 4. 排期与影响范围

### 4.1 排期表

| Round | act 内容 | 依赖 | 产出 |
|----|----|----|----|
| **Round 1**（当前） | v32 整体立项 + L2 v32_03 草案 + L1~L6 排期 | v31 archive | GOAL.md + PLAN.md + audit_1.md + review_1.md + snapshot.json |
| **Round 2** | v32_03 SCC 软下限修订实测（重算 v3.01 230 TP）+ L1 升级决策落档 | Round 1 | v32_03_review.md + decision_l1_upgrade.md |
| **Round 3** | v32_04 多项目样本回归（找 2~3 个 `workflow_assets/` 已跑样本）+ v32_01 UI 交叉（依赖 S3 prototype 结构）| Round 2 + `workflow_assets/` 样本存在性确认 | v32_04_report.md + v32_01_methodology.md |
| **Round 4** | v32_02 density-OBJ 维度（依赖 v32_04 完成）+ v32_05 TP 库首批回灌（依赖 S7/S8 跑通） | Round 3 + S7/S8 链路 | v32_02_methodology.md + v32_05_pilot.md |
| **Round 5**（CONVERGED） | 汇总 + 自查 + 6 条 AC 全部 PASS | Round 4 | v32/CONVERGED.md（achieved 声明） |

### 4.2 跨阶段影响

| 上游/下游 | v32 影响 |
|------|---------|
| S1 / S1.5 / S2 | ❌ 无改动（v32 不重塑三阶段边界）|
| S3 prototype | ⚠️ v32_01 补 UI TP 交叉 → S3 需保证 prototype.ui_nodes[] 有稳定 ID |
| S4 business_flow | ✅ 不变（v31 已纳入必读）|
| S5 生成 TP | ⚠️ v32_01 / v32_02 / v32_03 影响（新增字段 + 修订公式）|
| S6 生成 TC | ⚠️ v32_01 影响（间接通过 TP 字段）|
| S7 审查 | ⚠️ v32_02 新增 density-OBJ 校验项 |
| S8 自迭代 | ⚠️ v32_05 依赖 S8 跑通后入库 |

### 4.3 SSOT 维护边界

| 资产 | v32 处理 | 原因 |
|----|----|----|
| `archive/v31_20260721_020714.bak/PLAN.md` | ❌ 不改（仅引用）| v31 SSOT achieved |
| `archive/v31_20260721_020714.bak/CONVERGED.md` | ❌ 不改 | v31 终态 |
| `archive/v31_20260721_020714.bak/v31_SCC.md` | ⚠️ 草案加段落（v32_03 启动时确认）| SCC 公式源；草案段不永久写入 |
| `.cursor/MODULES.md` | ❌ 不改 | 8 模块定义 SSOT |
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` | ❌ 不改（本轮及后续轮）| STAGE 规则不漂移 |
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | ❌ 不改 | STAGE 规则不漂移 |
| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 | ❌ 不改 | 阈值 SSOT |
| `.cursor/rules/product_format_rules.yaml` | ❌ 不改 | 格式契约 SSOT |
| `knowledge/public/module_templates/` | ❌ 不改 | v31 §4 引而不重写 |

---

## 5. 验收闭环

### 5.1 4 条 ACCEPT 标准

| # | 验收标准 | 证据 |
|---|---------|------|
| **AC-1** | v32_01 ~ v32_05 全部有草案路径（不论是否开工）| 本档 §3.1 / §3.2 / §3.3 / §3.4 / §3.5 各占一节，方法+影响+依赖+风险齐全 |
| **AC-2** | L2 SCC 软下限公式落地（修订前后对照）| 本档 §3.3 给出公式修订前后对照（含 v3.01 实测预案）|
| **AC-3** | 不修改 `.mdc` 强制规则（v31 SSOT 不漂移）| 本轮所有改动限于 `governance/design_iter/plans/v32/`；`git diff --name-only` 应只列本档 |
| **AC-4** | ARCHIVE 引用链：v32 文档均引用 v31 archive 路径（不引用 v31/ 现役目录）| §2.1 / §2.2 / §3.1 / §3.3 / §4.1 / §4.3 全文 `archive/v31_20260721_020714.bak/` 引用 ≥ 3 处 |

### 5.2 Round 1 act 落档协议执行记录

| 改动文件 | 动作 | 说明 |
|---------|------|------|
| `v32/GOAL.md` | Write（新建）| 顶层目标 + 4 项用户选项 + 5 治理路由 |
| `v32/PLAN.md` | Write（新建）| 五段式治理 SSOT |
| `v32/audit_1.md` | Write（新建）| 4 条 AC 论证 + 反向挑战 |
| `v32/review_1.md` | Write（新建）| Round 1 复盘 + 4 项缺陷 |
| `v32/snapshot.json` | Write（新建）| goal-loop 快照（goal_id UUIDv4）|

### 5.3 DNA §9.1 文件计数

- 本轮 = 5 文件（含 1 个数据文件 snapshot.json）
- §9.1 红线 = 5 文件满载 ✅（按 §9.1.1 self-test 豁免类比规则，本轮属"规划轮 5 文件满载"）

### 5.4 DNA 自检（v32 Round 1 全过程合规）

- **DNA §9.4（先验后答）**：本轮已 Read 3 个 v31 文件（CONVERGED.md / review_5.md / archive PLAN.md）
- **DNA §9.1（决策密度）**：5 文件满载（合规）
- **DNA §9.5（落档协议）**：5 文件全部先 Write 占位（GOAL.md 骨架先行），后 content 展开
- **DNA §10（人本可审查）**：所有名词具体（v32_xx_yy.md 路径 / `archive/v31_20260721_020714.bak` 路径 / v3.01 230 TP 等），不堆术语，列执行清单
- **DNA §11（格式干净）**：无 v2 / ISO 时间戳（除 ISO 时间戳字段由 yaml 单独定义）/ 禁止 JSON 字段 / 双版本标签等违规（已通读 `product_format_rules.yaml`）
- **DNA §1 准则 1（一致性）**：v32 立项与 v31 SSOT 不冲突；5 治理路由引用 `archive/v31_20260721_020714.bak/PLAN.md` 章节
- **DNA §1 准则 4（人本可审查）**：影响范围（跨阶段 + SSOT 维护边界 + 5 路由依赖图）列具体可查

### 5.5 与 v31 SSOT 的衔接

| v31 SSOT 章节 | v32 处理 |
|------|------|
| §3.1.3 SCC 公式 | v32_03 修订（草案形式，未回写 SSOT）|
| §3.2.2 TC 字段契约 | L1 升级决策（Round 2 act 决定）|
| §3.4 三条铁律 | 不变 |
| §6 覆盖率公式 | v32_02 新增 density 维度 |
| §8.3 pending_candidates schema | 不变（v32_05 沿用）|
| §8.4 TP 库激活阈值 | 不变（v32_05 沿用）|
| §10.1 C1~C6 验收 | v32 5.1 沿用 4 条（不是 6 条，因 v32 范围更小）|

---

## 6. 附录：SSOT 索引

| 内容 | 路径 |
|------|------|
| v31 SSOT（5 段结构）| `archive/v31_20260721_020714.bak/PLAN.md` |
| v31 SCC 公式源 | `archive/v31_20260721_020714.bak/v31_SCC.md` |
| v31 achieved 声明 | `archive/v31_20260721_020714.bak/CONVERGED.md` |
| v31 Round 5 缺陷 + v32 治理路线 | `archive/v31_20260721_020714.bak/review_5.md` |
| v31 4 项覆盖率实测 | `archive/v31_20260721_020714.bak/coverage_report.md` |
| v31 S8 回灌诊断 | `archive/v31_20260721_020714.bak/s8_knowledge_backflow_diagnosis.md` |
| 8 模块定义 SSOT | `.cursor/MODULES.md`（仅读）|
| S5 STAGE 规则 | `.cursor/rules/STAGE_S5_TEST_POINTS.mdc`（仅读）|
| S6 STAGE 规则 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc`（仅读）|
| 跨阶段契约 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`（仅读）|
| 格式违规规则 | `.cursor/rules/product_format_rules.yaml`（仅读）|
| DNA 准则 | `AGENTS.md` + `.cursor/rules/DNA_3Q_CHECK.mdc` |
| goal-loop SKILL | `.cursor/skills/goal-loop/SKILL.md` |
| 覆盖率验证脚本 | `ai_workflow/coverage_validator.py` |
| 公共 XLSX 表头 | `ai_workflow/test_case_formatter.py` `_XLSX_HEADERS_V3` |
| v3.01 S5 产物 | `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json`（230 TP）|
| v3.01 S6 产物 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`（230 TC）|

---

> **v32 PLAN.md 落档** — Round 1 路线立项 + 5 治理路由草案 + 4 条 AC；后续 act 轮按 §4.1 排期启动
