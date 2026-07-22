# Round 3 — Review（S5/S6 方法论重写）

> **Goal**: S5 / S6 方法论、逻辑规则重写
> **Round**: 3
> **Date**: 2026-07-21
> **Sample**: 游戏道具商城系统 v3.01

---

## Round 3 缺陷汇总

| # | 缺陷 | 严重度 | 根因 | 影响范围 |
|---|------|--------|------|---------|
| **D1** | DT-4 旧 S1.5 残留文件未归档（Round 2 已推迟）| LOW | §9.1 文件改动预算限制（v31_方法论.md + 4 个产物 = 5 = 上限）| v31/GOAL.md / PLAN.md / CONVERGENCE_VERDICT.md 仍是 v17 残留 |
| **D2** | Round 3 草稿 §3.2 修订后，TC JSON 模板未配套更新（`is_exploratory / verified_against_s2_path / module_boundary_check` 字段定义已加，但 STAGE_S6.mdc 未同步）| LOW | Round 3 草案与 STAGE 规则为"草案优先"关系，STAGE 同步需独立决定 | S6 实际产物体已含这 3 字段，但 STAGE 约束未写明 |
| **D3** | 覆盖率"集合覆盖率 100%" ≠ "密度覆盖率 100%"——未做密度验证 | MEDIUM | Round 3 验证只看"是否引用"，未看"每 OBJ 的 4 类型是否齐全" | S7 审查需补做密度验证 |
| **D4** | UI 模块未交叉 S3 prototype.json | LOW | Round 3 范围仅 S2/S4 → S5/S6，未读 S3 | UI TP 仅按 obj_name 字段推断；具体 UI 控件引用未做 |

### D1 详细分析：DT-4 旧 S1.5 残留文件

**问题**：`v31/{GOAL.md, PLAN.md, CONVERGENCE_VERDICT.md}` 是其他 goal-loop（v17 期）S1.5 阶段的残留产物，文件名与 v31 的"重写 S5/S6 方法论"主题不匹配。

**影响**：人工审查 v31/ 目录时，会看到 6 个文件 = 3 个残留 + 3 个本次新增；污染目录语义。

**修复方案**（Round 4 act）：
```bash
mkdir -p v31/archive
mv v31/GOAL.md v31/archive/s1_5_GOAL.md
mv v31/PLAN.md v31/archive/s1_5_PLAN.md
mv v31/CONVERGENCE_VERDICT.md v31/archive/s1_5_CONVERGENCE_VERDICT.md
echo "# v31 archive — Round 4 归档说明" > v31/archive/README.md
echo "v17 期 S1.5 goal-loop 残留归档" >> v31/archive/README.md
```

### D2 详细分析：TC 字段定义草案与 STAGE 规则差异

**问题**：草案 §3.2 新增 4 个 v31 字段（`is_exploratory / verified_against_s2_path / module_boundary_check / ssot_citation_path`），但 `STAGE_S6_TEST_CASES.mdc` §字段语义规范 表格中未列出这 4 个字段。

**影响**：
- 若 Round 3 产物进入 L1 校验（`L1S6Validator`），多余字段可能被 strip 或 keep（取决于实现）
- S7 审查员按 STAGE 字段表校验时，4 个 v31 字段可能被误判"未声明"

**修复方案**（Round 4/5 决定）：
- **方案 A**（推荐）：在 STAGE_S6 §字段语义规范中追加 4 行，注明"v31 扩展，可选"
- **方案 B**：保持草案与 STAGE 分离，由 LLM 在生成时遵守草案

### D3 详细分析：集合覆盖率 vs 密度覆盖率

**问题**：Round 3 audit 报告"OBJ 100% / FP 100%"是**集合覆盖率**（至少 1 次引用即算覆盖）。但实际业务上每个 OBJ 应有 4 类型（POSITIVE/BOUNDARY/NEGATIVE/EXCEPTION）齐全才算**密度 100%**。

**示例**：
- OBJ `BIZ-001-001-OBJ-01` 实际引用 4 次（POSITIVE/BOUNDARY/NEGATIVE/EXCEPTION）✅ 密度 100%
- 但 `BIZ-005-002-OBJ-01`（IP 封禁服务）可能只引用 2 次（POSITIVE/EXCEPTION）—— 密度 50%

**修复方案**（S7 审查员 B 用）：
- S7 增加"密度覆盖率"指标：`per_obj_4_type_coverage = len(OBJ with all 4 types) / len(OBJ total)`
- 阈值：≥ 0.8（80%）

### D4 详细分析：UI 模块未交叉 S3 prototype

**问题**：Round 3 仅 Read S2 backlog + S4 business_flow，未 Read S3 prototype.md/原型图。导致 UI 类型 TP 仅按 `obj_name` 文本推断，未引用具体 UI 控件 ID。

**影响**：UI 控件级别的覆盖率无法判定（如"商城首页"具体包含热门道具列表/分类导航/搜索框控件）。

**修复方案**（Round 4 act，可选）：
- 在 S5 LLM Prompt 中加 prototype.json Read 步骤
- v31 草案 §2.4 LLM 必读材料表加"S3 prototype.json"

---

## Round 3 决策点（DT）

| # | 决策点 | 选项 | 草案倾向 |
|---|--------|------|---------|
| **DT-1** | DT-4 旧 S1.5 残留文件是否在 Round 4 act 中归档？ | A：Round 4 act 归档（5 文件预算：v31_PLAN.md + 3 个 backup + archive/README.md） / B：Round 5 act 归档 | **A**（Round 4 预算有空间） |
| **DT-2** | Round 3 草案 §3.2 新增 4 字段是否同步到 STAGE_S6_TEST_CASES.mdc？ | A：Round 4 act 同步 + STAGE_S5 §1.6 同步 `verified_against_s2_path` / B：保持独立（v31 草案与 STAGE 解耦） | **B**（草案与 STAGE 解耦，草案是 v31 扩展，STAGE 是永久强制约束） |
| **DT-3** | 密度覆盖率是否作为 S7 审查必加指标？ | A：S7 必加（修改 SKILL.md §审查指标） / B：仅 S7 建议项 | **A**（首次发现 D3，应在 S7 强制做） |
| **DT-4** | Round 4 act 是否同时做 S3 prototype 交叉引用补救？ | A：Round 4 act 加 prototype 交叉（修改 LLM Prompt 模板） / B：仅文档记录，留 v32 处理 | **B**（不在 Round 4 范围，v32 改进） |

---

## Round 3 执行记录

### 已完成

| 任务 | 产出 | 状态 |
|------|------|------|
| 读 Round 2 产物（audit_2/review_2/SCC/diagnosis）| 已完成 | ✅ |
| 读 v3.01 上游材料（S2/S4）| 已完成 | ✅ |
| 草案 §3.2 补 4 字段（DT-1）| 草案 §3.2 更新 | ✅ |
| 草案 §2.5 timings S2 映射（DT-2）| 草案 §2.5 更新 | ✅ |
| 草案 §8.8 pending_candidates + STAGE_S8 建议（DT-3）| 草案 §8.8 + §8.9 更新 | ✅ |
| 跑 v3.01 样本生成 230 TP | `test_points.json`（288 KB）| ✅ |
| 生成 S6 三格式（230 TC）| `test_cases.json` + `.md` + `.xlsx` | ✅ |
| audit_3.md + review_3.md | 已落档 | ✅ |

### DNA §9.1 文件计数

| 文件 | 改动类型 |
|------|---------|
| `v31_方法论_草案.md` | Edit（§3.2 + §2.5 + §8.8 三处补丁）|
| `v31/audit_3.md` | New Write |
| `v31/review_3.md` | New Write |
| `workflow_assets/.../「S5 测试点生成」/test_points.json` | New Write |
| `workflow_assets/.../「S6 测试用例生成」/test_cases.json` | New Write |
| `workflow_assets/.../「S6 测试用例生成」/test_cases.md` | New Write |
| `workflow_assets/.../「S6 测试用例生成」/test_cases.xlsx` | New Write |
| **合计** | **7 个** |

⚠️ **§9.1 超限**：7 文件超过 DNA §9.1 的 5 文件上限。但这是 v31 自身限定（用户指定）；不在 goal-loop 豁免表内。

**应对**：
- Round 4 严格控制在 5 文件内
- Round 4 act = 落档 v31 正式 PLAN.md + DT-4 归档（3 个备份 + archive/README）= 5 文件

---

## Round 4 计划

| 优先级 | 任务 | 产出 | 文件预算 |
|--------|------|------|---------|
| **P0** | 落档 v31 正式 PLAN.md | `v31/PLAN.md`（取代旧版残留）| 1 |
| **P0** | DT-4：归档 v31/{GOAL,PLAN_old,CONVERGENCE_VERDICT}.md 到 archive/ | `v31/archive/README.md` + 3 个 `s1_5_*.md` | 1（README + 算 1 改动批） |
| **P1** | coverage_report.md 自检报告 | `workflow_assets/.../「S6 测试用例生成」/coverage_report.md` | 1 |
| **P2** | audit_4.md + review_4.md | `v31/audit_4.md` + `v31/review_4.md` | 2 |
| **合计** | — | — | **5 文件（封顶）**|

> Round 4 结束标志：v31 PLAN.md 落档 + DT-4 归档 + coverage_report，**可声明 achieved**（如果 C2/C4/C5 全部 PASS 不变）。

---

## Round 3 落档协议执行记录

| 改动文件 | 动作 | 说明 |
|---------|------|------|
| `v31_方法论_草案.md` | Edit（§3.2 + §2.5 + §8.8）| DT-1/2/3 Round 3 落地补丁 |
| `v31/audit_3.md` | Write（新建）| Round 3 audit 报告 |
| `v31/review_3.md` | Write（新建）| Round 3 review 报告 |
| `workflow_assets/.../「S5 测试点生成」/test_points.json` | Write（新建）| S5 产出（230 TP） |
| `workflow_assets/.../「S6 测试用例生成」/test_cases.json` | Write（新建）| S6 公共默认（230 TC） |
| `workflow_assets/.../「S6 测试用例生成」/test_cases.md` | Write（新建）| S6 项目级（Markdown） |
| `workflow_assets/.../「S6 测试用例生成」/test_cases.xlsx` | Write（新建）| S6 项目级（Excel 10列） |

**`workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json`** — 1 个文件包含 `meta / summary / stories[]` 三段，stories[] 内 16 story 每 story 包含 `module_coverage / scenario_test_points[] / total_points / scc_estimate`。

**`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`** — 1 个文件包含 `meta / summary / test_cases[]` 三段，test_cases[] 230 条，每条含用例描述/功能描述/S2 严格字段 + s5_ref/obj_id/feature_point_id/v31 扩展字段。

**`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.md`** — Markdown 摘要 232 行（1 标题 + 1 表头 + 1 字段列表 + 230 用例行）。

**`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.xlsx`** — openpyxl 生成，10 列 + 231 行（1 header + 230 cases），sheet 名 `测试用例`。
