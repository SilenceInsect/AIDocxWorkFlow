# Round 5 — Review（v31 方法论重写收尾）

> **Goal**: S5 / S6 方法论、逻辑规则重写
> **Round**: 5（收尾 act）
> **Date**: 2026-07-21
> **Verdict**: ✅ **ACHIEVED**

---

## Round 5 缺陷汇总

| # | 缺陷 | 严重度 | 根因 | 处理 |
|---|------|--------|------|------|
| **D1** | L1：`ssot_citation_path` 字段 0/230 填充 | LOW | Round 3 生成器未实现该字段写入；用户 Round 5 表态保留 COULD（v32 决策）| 保留 COULD |
| **D2** | L2：SCC 软下限 80% 未被 5/16 Story 满足（实际 31%） | MEDIUM | Round 2 自创 SCC 公式 + 用户 Round 5 表态 scope-a：不在 PLAN.md 改动（v32 治理） | v32 处理 |
| **D3** | L3：UI TP 未交叉 S3 prototype.json（未引用 UI 控件 ID） | LOW | v31 设计未将"UI 控件级交叉"纳入范围 | v32_01 |
| **D4** | L4：density-覆盖率（per-OBJ 4 类型齐全率）未校验 | MEDIUM | v31 设计只做"集合覆盖率"，未做"密度覆盖率" | v32_02 + S7 审查 |
| **D5** | L5：单一项目样本（v3.01）不证明通用性 | MEDIUM | v31 时间预算 + 项目流程约束 | v32_04 多项目回归 |
| **D6** | L6：测试点库首批回灌未触发（依赖 S7/S8 跑通） | LOW | v3.01 未走完 S5→S7→S8 链路 | v32_05 |

### D1 详细分析：`ssot_citation_path` 字段缺填

**问题**：v31 §3.2.2 列出 4 个 v31 扩展字段（`is_exploratory` / `verified_against_s2_path` / `module_boundary_check` / **`ssot_citation_path`**）。Round 3 生成器实现前 3 个，第 4 个未填。

**影响**：
- 当前 v3.01 产物中 0/230 TC 含 `ssot_citation_path` 字段
- 若 S7 审查员按 §3.2.2 严格校验，可能误判 v31 不完整

**根因**：
- Round 3 生成器实现时未读完整 §3.2.2 字段表
- §3.2.2 列出 4 个 COULD 字段时未加 `[R3 实现状态]` 标记

**修复方案**：用户 Round 5 表态 scope-a → 保留 COULD（可选），不影响功能完整性。v32 决策：升级必填 / 移除该字段 / 留 COULD。

### D2 详细分析：SCC 软下限未满足

**问题**：Round 2 自创 SCC 公式后，Round 4 实测 5/16 Story 的实际 TP 远低于软下限。例：UI-001-002 理论 216 TP，软下限 172 TP，实际仅 15 TP。

**根因**：
- SCC 公式计算的是"理论最大测试点空间"（5 维度乘积）
- 实际生成按"每 OBJ × 每 FP × 1~4 类型"抽样
- 5 维度空间远大于 FP 数 × 类型抽样的实际需求

**现状**：Round 4 `coverage_report.md` §4.2 已显式标注 5 个 Story 的实际 SCC 与软下限对比。

**修复方案**：用户 Round 5 表态 scope-a → 不在 PLAN.md 改动；v32 处理（修订公式或降低软下限）。

### D3 详细分析：UI 交叉 S3 prototype

**问题**：v31 §3.1 仅要求读 S2 + S4，未要求读 S3 prototype.json。导致 UI 模块 TP 的 `description` 仅按 `obj_name` 字段推断（"商城首页布局与控件"），未引用具体 UI 控件 ID。

**影响**：
- UI 控件级覆盖率无法机器校验（如"商城首页"具体包含热门道具列表/分类导航/搜索框）
- UI 类型测试意图可能被 LLM 模糊化

**根因**：v31 设计未将"UI 交叉"纳入必读材料清单。

**修复方案**：v32_01 增加 "S3 prototype 必读" 条款到 §2.1，并在 §3.1.2 TP 字段契约新增 `ui_node_refs: array<string>`（引用 S3 prototype `pages[].ui_nodes[]`）。

### D4 详细分析：density-覆盖率未校验

**问题**：当前 v31 覆盖率统计 `len(OBJ_referenced_set) / len(OBJ_total)` = "集合覆盖率"。不统计"每个 OBJ 的 POSITIVE/BOUNDARY/NEGATIVE/EXCEPTION 都齐全"。

**影响**：
- "OBJ 100%" = "每个 OBJ 至少引用 1 次"，不代表"每个 OBJ 的 4 类型 TP 都齐全"
- S7 审查员按此判定会误判覆盖率满足

**根因**：v31 §6 覆盖率公式只做集合维度。

**修复方案**：v32_02 新增 `density_coverage` 公式：`per_obj_4_type_coverage = len(OBJ with all 4 types) / len(OBJ total)`，阈值 ≥ 0.8。

### D5 详细分析：单一样本局限

**问题**：v31 方法论验证仅在"游戏道具商城系统 v3.01"（一个 BIZ 模块占主导的需求）跑通。

**影响**：
- UI/HINT/SPECIAL 等模块的覆盖深度未充分验证
- v3.01 是 7 个 Epic × 16 Story × 36 OBJ × 99 FP 的中型需求，不覆盖超大型（> 100 OBJ）或超小型（< 10 OBJ）需求

**根因**：v31 时间预算 + 单项目验证。

**修复方案**：v32_04 从 `workflow_assets/` 找 2~3 个 S5/S6 已跑的版本回归测试。

### D6 详细分析：TP 库首批回灌未触发

**问题**：`knowledge/public/test_point_library/` 仍为空，因 v3.01 未走 S7/S8。

**影响**：
- §8.4 TP 库激活阈值（≥ 10 条）短期不会触发
- v31 §8.6 S5 LLM 自动复用机制短期不生效

**根因**：v3.01 项目流程未跑完 S5→S7→S8 + 人工审核未建立。

**修复方案**：v32_05 待 S7/S8 跑通后回灌首批 + 人工审核机制建立。

---

## v32 治理路线（建议起跑条件：v31 achieved 后 1~2 周）

### v32_01：补 S5↔S3 UI 交叉覆盖

**目标**：UI TP 引用具体 prototype 控件 ID，可机器校验 UI 控件级覆盖率。

**计划**：
- `v31/PLAN.md` §2.1 必读清单加 S3 prototype.json
- §3.1.2 TP 字段契约加 `ui_node_refs: array<string>`（引用 `pages[].ui_nodes[].id`）
- §6 覆盖率公式加 UI 控件交叉覆盖率：`ui_node_coverage = len(TP 引用 UI 节点数) / prototype.md UI 节点总数`
- 阈值 ≥ 1.0（与 S5_S3_REF_COVERAGE 对齐）

### v32_02：补 density-OBJ 维度

**目标**：每 OBJ 的 4 类型 TP 齐全率门禁。

**计划**：
- §6 新增 density 覆盖率公式：`per_obj_4_type_coverage = len(OBJ with all 4 types) / len(OBJ total)`
- 阈值 ≥ 0.8
- `coverage_report.md` 增加 density 维度实测

### v32_03：SCC 软下限公式修订

**目标**：软下限从 80% 改为 50% + 商城类型加权系数（用户已表态 scope-a，v32 推进）。

**计划**：
- `v31_SCC.md` §1 修订 `软下限 = 理论 TP 数 × 0.5`
- 加 `domain_type_factor`：`{mall: 1.5, game: 2.0, finance: 0.8, ...}`
- 第 4 章"商城样本计算"同步更新

### v32_04：多项目样本回归

**目标**：用 2~3 个 S5/S6 已跑的版本回归 v31 方法论，验证模块分布 / 字段语义 / 跨项目一致性。

**计划**：
- 从 `workflow_assets/` 找 2~3 个历史版本（不同行业 / 不同模块分布）
- 用 v31 生成器重跑样本
- 对比：模块分布 / 覆盖率 / 字段语义一致性

### v32_05：测试点库首批回灌

**目标**：建立 v32 时序的"首次 S7/S8 跑通 → 人工审核 → TP 库入库"流程。

**计划**：
- 选 1 个新需求走完整 S5→S6→S7→S8 链路
- S8 输出 `iteration.json#pending_candidates` 含首批 5~10 条候选
- 项目流程约定人工审核 + 回写 `test_point_library/`
- §8.4 激活阈值触发后验证 S5 自动复用机制

---

## Round 5 执行记录

### 已完成

| 任务 | 产出 | 状态 |
|------|------|------|
| 读 Round 4 PLAN.md + coverage_report.md 现状 | 已完成 | ✅ |
| audit_5.md（6 条 accept_criteria 最终判定 + 7 条反向挑战）| 已落档 | ✅ |
| review_5.md（6 项遗留 + v32 治理路线 5 个方向）| 已落档 | ✅ |
| CONVERGED.md（achieved 声明 + 解决/新增/遗留三栏 + 影响范围 + 跨阶段影响 + DNA 自检） | 已落档 | ✅ |

### DNA §9.1 文件计数

| 文件 | 改动类型 |
|------|---------|
| `v31/audit_5.md` | New Write |
| `v31/review_5.md` | New Write |
| `v31/CONVERGED.md` | New Write |
| **合计** | **3 个** |

✅ Round 5 在 §9.1 3 文件预算内（满载）。

---

## Round 5 落档协议执行记录（DNA §9.5）

| 改动文件 | 动作 | 说明 |
|---------|------|------|
| `v31/audit_5.md` | Write（新建）| Round 5 audit 报告（6 条 accept_criteria + 7 条反向挑战）|
| `v31/review_5.md` | Write（新建）| Round 5 review 报告（6 项遗留 + v32 治理路线）|
| `v31/CONVERGED.md` | Write（新建）| v31 achieved 收敛报告 |

---

> **v31 goal-loop achieved 收敛**——Round 5 落档，v31 重写项目正式闭环
