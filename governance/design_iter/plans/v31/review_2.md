# Round 2 — Review（S5/S6 方法论重写）

> **Goal**: S5 / S6 方法论、逻辑规则重写
> **Round**: 2
> **Date**: 2026-07-21
> **Draft**: `governance/design_iter/plans/v31/v31_方法论_草案.md`

---

## Round 2 缺陷汇总

| # | 缺陷 | 严重度 | 根因 | Round |
|---|------|--------|------|-------|
| **D1** | §3.4 is_exploratory 字段在 S6 TC JSON schema 中未声明（草案 §3.2 未更新） | MEDIUM | Round 2 新增 is_exploratory 字段，但只写入了 §3.4 自检方法，未在 §3.2 输出契约表中声明该字段 | Round 3 act 补充 §3.2 契约表 |
| **D2** | §2.5 SCC 维度"actors / states / timings / boundaries / exceptions"中，`states` 和 `timings` 计数规则在 v31_SCC.md 中未给出与 S2 字段的直接映射 | LOW | 草案和 v31_SCC.md 中 states 提到"state_machine 字段"，timings 未给出明确的 S2 来源映射 | Round 3 act 补充 v31_SCC.md §2 |
| **D3** | §8 S8 契约的"人工审核触发机制"未建立（SKILL/STAGE 层面无自动通知） | MEDIUM | S8 SKILL.md §归档只说"归档到 .review_queue/"，没有说"如何通知人工" | Round 3 act 建议在 STAGE_S8 中加 §归档触发通知机制 |

### D1 详细分析：is_exploratory 字段 Schema 缺失

**问题**：§3.4.3 新增了 `is_exploratory: true` 时需要的三个字段（`is_exploratory`、`exploratory_reason`、`suggested_obj`、`suggested_fp`），但 §3.2 输出契约表中只列了 TC 原始字段（scenario/title/preconditions/steps/...），未包含这四个新增字段。

**影响**：S6 生成的 TC JSON 中可能出现 is_exploratory=true 时字段缺失，或字段顺序不固定（违反 §7 格式契约）。

**修复方案**：
在草案 §3.2 输出契约表中新增两行：

| 字段 | 类型 | 取值约束 | 从 TP 派生 |
|------|------|---------|-----------|
| `is_exploratory` | bool | true/false | 当 description 关键词 ⊈ OBJ∪FP 时为 true |
| `exploratory_reason` | string | 非空（当 is_exploratory=true 时必填）| — |
| `suggested_obj` | string | OBJ 名称（选填）| — |
| `suggested_fp` | string | FP 名称（选填）| — |

### D2 详细分析：SCC 维度与 S2 字段的直接映射缺失

**问题**：v31_SCC.md §2 中 states 和 timings 的来源描述不够精确：
- states 提到"来自 `requirement_objects.json` state_machine 字段"（✅ 有明确来源）
- timings 未给出明确的 S2 字段来源，只说"正常/零点/跨日/并发时序"（❌ 无 S2 字段映射）

**影响**：LLM 在计算 SCC 时可能无法确定 timings 的精确计数方式。

**修复方案**：
在 v31_SCC.md §2.3 中补充 timings 的 S2 字段来源：

| 维度 | S2 字段来源 |
|------|----------|
| timings | `backlog.json#stories[].acceptance_criteria`（查找"零点"/"跨日"/"活动期间"等关键词）+ `requirement_objects.json#objects[].feature_points[].normal_flow`（时序节点）|

### D3 详细分析：人工审核触发机制缺失

**问题**：§8 S8 契约描述了"人工审核 → 回写公共库"链路，但没有说"如何触发人工审核"。

**影响**：即使 S8 写入了 `.review_queue/`，也没有人知道"有新的候选需要审核"。

**修复方案**（Round 3 act）：
在 `review_report.json` 或 `iteration.json` 中新增字段：
```json
{
  "review_queue_triggered": true,
  "pending_candidates": [
    "knowledge/project_local/.review_queue/BIZ/A_biz_logic__ITER-012__2026-07-21.md"
  ]
}
```
并在 STAGE_S8 中要求 S8 执行后输出此字段，由项目流程约定"人工定期检查 pending_candidates"。

---

## Round 2 决策点（DT）

| # | 决策点 | 选项 | 草案倾向 |
|---|--------|------|---------|
| **DT-1** | §3.2 契约表是否需要立即补充 is_exploratory 四个字段？ | A：立即补充（Round 3 act） / B：等 Round 3 跑样本时再补 | **A**（立即补，避免 Round 3 跑样本时 schema 不完整） |
| **DT-2** | v31_SCC.md 中 timings 的 S2 字段映射是否需要补充？ | A：补充（Round 3 act） / B：保持现状（已有说明性描述） | **A**（补充后 LLM 计算 SCC 时有确定性来源） |
| **DT-3** | §8 人工审核触发机制是否需要进入契约？ | A：进入契约（在 iteration.json 中加 pending_candidates 字段） / B：不进契约（只依赖项目人工约定） | **A**（契约化后有明确字段可查，避免"没人知道有新候选"） |
| **DT-4** | DT-1~3 的修复是否在 Round 3 act 中与样本生成一起做？ | A：是（合并做，节省轮次） / B：否（单独开 Round 3 做修复，Round 4 再跑样本） | **A**（Round 3 act 同时做修复 + 跑样本） |

---

## Round 2 执行记录

### 已完成

| 任务 | 产出 | 状态 |
|------|------|------|
| 反馈 1（DT-1 拒绝）：S8 诊断 | `s8_knowledge_backflow_diagnosis.md` + §8 | ✅ |
| 反馈 2：TC 字段语义收紧 | §3.4（三条铁律 + 自检 + is_exploratory）| ✅ |
| 反馈 3：SCC 替换硬上限 | `v31_SCC.md` + §2.5 | ✅ |
| DT-4 推迟（§9.1 上限）| §9 标注推迟 Round 3 | ✅ |
| DT-5 A×4（tpl_id/is_assumed/OBJ 强类型/TP 库 seed）| §2.2 + §8 | ✅ |
| audit_2.md + review_2.md | `audit_2.md` + `review_2.md` | ✅ |

### DNA §9.1 文件计数

| 文件 | 改动类型 |
|------|---------|
| `v31_方法论_草案.md` | Edit（§2.4 Forbidden + §2.5 新增 + §3.4 新增 + §8 新增 + §9+§10 更新）|
| `s8_knowledge_backflow_diagnosis.md` | New Write |
| `v31_SCC.md` | New Write |
| `audit_2.md` | New Write |
| `review_2.md` | New Write |
| **合计** | **5 个**（= §9.1 上限）|

✅ 未超 §9.1（DT-4 归档命令因上限约束已推迟到 Round 3）

---

## Round 3 计划

| 优先级 | 任务 | 产出 |
|--------|------|------|
| **P0** | DT-1：补充 §3.2 契约表（is_exploratory 四字段） | 草案 §3.2 更新 |
| **P0** | DT-2：补充 v31_SCC.md timings 的 S2 字段映射 | v31_SCC.md §2 更新 |
| **P0** | DT-3：iteration.json 加 pending_candidates 字段 | 草案 §8 更新 + STAGE_S8 建议 |
| **P1** | 跑 v3.01 样本生成 TP/TC | `test_points.json` + `test_cases.json` |
| **P1** | S6 三格式导出 | `.md` + `.xlsx` |
| **P2** | DT-4：旧 S1.5 残留文件归档 | `v31/archive/s1_5_*.md` |

---

## Round 2 落档协议执行记录

| 改动文件 | 动作 | 说明 |
|---------|------|------|
| `v31_方法论_草案.md` | Edit（5 处）| §2.4 Forbidden + §2.5 SCC 新增 + §3.4 新增 + §8 新增 + §9+§10 更新 |
| `s8_knowledge_backflow_diagnosis.md` | Write（新建）| Round 2 反馈 1 落地 |
| `v31_SCC.md` | Write（新建）| Round 2 反馈 3 落地 |
| `audit_2.md` | Write（新建）| Round 2 audit 报告 |
| `review_2.md` | Write（新建）| Round 2 review 报告 |
