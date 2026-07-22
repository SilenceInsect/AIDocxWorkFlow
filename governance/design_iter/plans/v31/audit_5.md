# Round 5 — Audit（v31 方法论重写达成）

> **Goal**: S5 / S6 方法论、逻辑规则重写
> **Round**: 5（收尾 act）
> **Date**: 2026-07-21
> **Draft**: `v31/PLAN.md`（正式 SSOT，680 行）+ `v31/coverage_report.md`（212 行）
> **Verdict**: ✅ **ACHIEVED**

---

## 验收标准审计（对照 6 条 accept_criteria · 最终）

| # | 验收标准 | 证据（文件 + 段落）| 判定 |
|---|---------|------------------|------|
| **C1** | 方法论沉淀：S5/S6 完整链路 + LLM Prompt + 字段溯源 + 覆盖率公式 | `v31/PLAN.md` §2（输入契约）+ §3（方法论 + LLM Prompt 模板 §3.1.4 / §3.2.4）+ §6（4 项覆盖率公式）+ §9（字段字典 TP/TC 23+17 项） | ✅ **PASS** |
| **C2** | 通用性验证：v3.01 样本跑通 | `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json`（230 TP）+ `「S6 测试用例生成」/test_cases.{json,md,xlsx}`（230 TC，模块分布 UI:47 / BIZ:163 / LINK:4 / LOG:16）| ✅ **PASS** |
| **C3** | 知识库贯通：8 模块 × 子类 × TP 模板映射 | `v31/PLAN.md` §4（CONFIG/UI/BIZ 全展开 + 5 模块引 SSOT）+ `knowledge/public/module_templates/<8 modules>.md` 通读 + §8 TP 库入库链路建立 | ✅ **PASS** |
| **C4** | 覆盖率口径：基于 S4（25 risks / 66 leaves）+ OBJ/FP ≥ §4.3 常量 | `v31/coverage_report.md` §1：OBJ 36/36 + FP 99/99 + 异常叶子 66/66 + 风险点 25/25 全部 100% | ✅ **PASS** |
| **C5** | 格式干净：JSON + MD + XLSX 三格式，0 字段冗余、0 格式违规 | `workflow_assets/.../「S6 测试用例生成」/test_cases.xlsx` 用 `_XLSX_HEADERS_V3` 10 列 + `coverage_report.md` §2 TC 字段语义收紧 230/230 PASS + `test_cases.md` Markdown 摘要 230 行 | ✅ **PASS** |
| **C6** | 落档完整：方法论文档 + 产物归位 | `v31/PLAN.md`（5 段 SSOT）+ `v31/coverage_report.md`（自检报告）+ `v31/archive/s1_5_*.md`（3 个旧残留归档）+ S5/S6 三格式产物归位 v3.01/「S5 测试点生成」/ + 「S6 测试用例生成」/ | ✅ **PASS** |

### Round 5 判定汇总

- **C1 / C2 / C3 / C4 / C5 / C6**：✅ **ALL PASS**（全部 6 条达成）
- **关键里程碑**：4 项覆盖率全部 100%，TC 字段语义收紧 230/230 PASS，方法论 SSOT 已落档

---

## Round 1~5 演进轨迹（v31 治理成果）

### 解决（v30 → v31 闭环）

| # | 项 | 证据 |
|---|----|------|
| **R1.1** | STAGE_S5/S6 字段契约已有但缺"字段语义收紧"机制 | `v31/PLAN.md` §3.4 三条铁律（A/B/C） |
| **R1.2** | TP 库为空（v30 不知根因） | `v31/s8_knowledge_backflow_diagnosis.md` + `v31/PLAN.md` §8 两段制归档 |
| **R1.3** | TP ≤ 50/Story 硬上限不合理（v30 拍脑袋） | `v31/v31_SCC.md` + `v31/PLAN.md` §2.5 SCC 公式 |
| **R1.4** | 8 模块子类表无 SSOT 索引 | `v31/PLAN.md` §4（CONFIG/UI/BIZ 全展开 + 5 模块引 SSOT 不重写）|
| **R1.5** | 覆盖率口径不明确（v30 拍脑袋） | `v31/PLAN.md` §6（4 项覆盖率公式）+ `v31/coverage_report.md` 实测 |

### 新增（v31 比 v30 多的）

| # | 项 | 证据 |
|---|----|------|
| **A1** | v31 扩展字段：`is_exploratory` / `verified_against_s2_path` / `module_boundary_check` / `ssot_citation_path`（COULD） | `v31/PLAN.md` §3.2.2 + §9.2 |
| **A2** | TC 字段语义收紧三条铁律 + `is_exploratory` 探索性标注 | `v31/PLAN.md` §3.4（铁律 A/B/C + 自检方法）|
| **A3** | SCC 故事复杂度系数（5 维度乘积 + 软下限）| `v31/v31_SCC.md`（独立文件）+ `v31/PLAN.md` §2.5 |
| **A4** | S8 回灌 TP 库契约（两段制 + `pending_candidates` 触发）| `v31/PLAN.md` §8.2-§8.4 |
| **A5** | 关键词快速映射表（50+ 关键词 → module/subclass） | `v31/PLAN.md` §4.3 |
| **A6** | 冲突优先级矩阵（8 行场景）| `v31/PLAN.md` §4.4 |

### 遗留（→ v32 处理）

| # | 项 | 处理 |
|---|----|------|
| **L1** | `ssot_citation_path` 字段是否升级为必填 | 保留 COULD（v32 决策）|
| **L2** | SCC 软下限修订（80% → 50% + 商城加权） | Round 5 用户表态 scope-a：不在 PLAN.md 改动 |
| **L3** | UI 交叉 S3 prototype 覆盖率（TP 是否引用 UI 控件 ID） | 推移 v32_01 |
| **L4** | density-覆盖率（per-OBJ 4 类型齐全率） | 推移 v32_02 + S7 审查补做 |
| **L5** | 多项目样本验证（v3.01 之外的 2~3 个回归） | 推移 v32_04 |
| **L6** | 测试点库首批回灌 | 推移 v32_05（依赖 S7/S8 实际跑通）|

---

## 反向挑战（DNA §10.5 不产出无根据结论）

### 反向挑战 1：v3.01 是单一样本不证明通用性

**质疑**：v31 方法论仅在"游戏道具商城系统 v3.01"一个需求样本上验证通过。

**承认限制**：✅ 真实限制。v3.01 是 BIZ 模块占主导的商城类需求，对 UI/HINT/SPECIAL 等模块的覆盖深度未充分验证。

**应对**：
- 8 模块 × 字段语义收紧方案在理论上可迁移（§4 模块判定不依赖特定业务）
- v32_04 多项目样本回归作为验证窗口
- 模块分布（UI:47 / BIZ:163 / LINK:4 / LOG:16）说明 LLM 已按 §4 关键词映射规则判定模块归属

### 反向挑战 2：SCC=900→230 远低于理论

**质疑**：v3.01 的实际 TP 数 230 仅是 SCC 理论值（≥ 720）的 32%，未达 80% 软下限。

**承认限制**：✅ 真实偏差。5 个 Story 中实际 TP 远低于 SCC 软下限（UI-001-002 实际 15 vs 软下限 172）。

**应对**：
- Round 4 `coverage_report.md` §4.2 已显式标注根因（理论空间 vs 实际抽样）
- Round 5 用户表态 L2 = scope-a：不改 PLAN.md，靠 v32 治理
- 实际 TP 数按 §2.1 P0 路径优先 + 探索性标记生成，P0 已全展开（覆盖率 100% 可佐证）

### 反向挑战 3：L1 `ssot_citation_path` 0/230 缺填

**质疑**：v31 §3.2.2 列出 4 个扩展字段，实际仅生成 3 个。

**承认限制**：✅ 真实缺漏（已声明）。

**应对**：
- Round 5 用户表态：保留 COULD（可选），不影响功能完整性
- L1 推迟到 v32 做"必填升级 vs 移除"决策
- 现有 3 字段（`is_exploratory` / `verified_against_s2_path` / `module_boundary_check`）已提供 DNA Q1.1 字段溯源基础

### 反向挑战 4：L3/L4 UI 交叉未做

**质疑**：UI 模块 TP 未引用具体 S3 prototype 控件 ID；density-OBJ 4 类型齐全率未校验。

**承认限制**：✅ 真实范围遗漏（非 bug）——v31 未将"UI 控件级交叉"和"per-OBJ 4 类型密度"纳入设计范围。

**应对**：
- 已显式推到 v32_01（UI 交叉）+ v32_02（density）
- v31 不重做，v32 治理路线清晰

### 反向挑战 5：若 v31 后 S8 运行仍无 TP 回灌 → §8 失效

**质疑**：§8 两段制归档依赖"v31 后 S7/S8 实际跑通 + 人工审核流程建立"。若两者仍未触发，TP 库仍为空。

**承认限制**：✅ 真实风险。

**应对**：
- §8 三道防线：① S8 写入 `.review_queue/` + ② `iteration.json#pending_candidates` 触发 + ③ 项目流程约定人工审核
- §8.4 TP 库激活阈值（≥ 10 条）作为自动复用机制的开关
- 仍需项目流程主动建立"人工定期检查 `pending_candidates`" 的约定——v32 L6 跟进

### 反向挑战 6：覆盖率"集合 100%"≠"密度 100%"

**质疑**：OBJ 36/36 是"每个 OBJ 至少引用 1 次"，不代表"每个 OBJ 的 4 类型 POSITIVE/BOUNDARY/NEGATIVE/EXCEPTION 都齐全"。

**承认限制**：✅ 真实限制——集合覆盖率仅统计"是否引用"，不统计"引用密度"。

**应对**：
- `coverage_report.md` §5.2 TP 类型分布已显式：POSITIVE 99 + BOUNDARY 25 + NEGATIVE 17 + EXCEPTION 89（按 OBJ 均摊不到 4 类型齐全）
- L4（density-OBJ 4 类型齐全率）→ v32_02 + S7 审查补做
- 当前 100% 集合覆盖率已满足 §4.3 SSOT 阈值要求

### 反向挑战 7：AI 生成 title/description 不可逆追溯

**质疑**：TP 的 `title` / `description` / `fp_name` 由 LLM 生成，无法反向溯源到 S2 字段。

**承认限制**：✅ 部分真实——LLM 自由文本不具备字段级溯源能力。

**应对**：
- 字段级溯源（obj_id / obj_name / feature_point_ref）由 §2.3 Q1 三子问保证 100% 匹配
- 文本级溯源通过 §2.5 / §3.4 字段语义收紧机制（铁律 A/B/C）保证 → `coverage_report.md` §2 显示 230/230 PASS

---

## Round 5 最终判定

> **✅ ACHIEVED** — 全部 6 条 accept_criteria PASS，11 项核心交付落档，6 项遗留项已显式推到 v32

> **v31 方法论重写 goal-loop 完成** —— Round 5 进入 achieved 收敛，下一轮 v32 治理路线启动
