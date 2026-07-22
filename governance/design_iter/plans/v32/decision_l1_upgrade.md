# DT-V32-001 — L1 `ssot_citation_path` 升级决策

> **决策 ID**: DT-V32-001
> **触发**: v31 6 项遗留 L1（`review_5.md` D1）
> **日期**: 2026-07-21
> **状态**: 已落档（推荐走选项 C）

---

## 触发背景

v31 §3.2.2 列出 4 个 v31 扩展 COULD 字段（`is_exploratory` / `verified_against_s2_path` / `module_boundary_check` / `ssot_citation_path`）。Round 3 生成器只填了前 3 个，**`ssot_citation_path` 在 v3.01 中 0/230 填充**（coverage_report.md §3.1）。

**v3.01 实测数据**（`archive/v31_20260721_020714.bak/coverage_report.md` §3 表）：

| 字段 | 填充策略 | 填充数 / 总数 | 填充率 |
|------|---------|--------------|--------|
| `is_exploratory` | 必填 | 230 / 230 | **100%** |
| `verified_against_s2_path` | 必填 | 230 / 230 | **100%** |
| `module_boundary_check` | 必填 | 230 / 230 | **100%** |
| **`ssot_citation_path`** | 可选（v31 §3.2 草案列表字段，但 Round 3 生成器未填）| **0 / 230 = 0%** | ⚠️ 未填 |

**字段定义来源**：`archive/v31_20260721_020714.bak/PLAN.md` §3.2.2：

```json
{
  "ssot_citation_path": "string",
  "取值约束": "STAGE_S6 §字段语义规范路径",
  "上游来源": "DNA Q1.1 字段溯源"
}
```

**v31 §3.2.2 §9.2 已将 `ssot_citation_path` 标记为 COULD**（非必填），故 Round 3 生成器实现时未填不构成"违规"。

---

## 用户表态（Round 5）

`archive/v31_20260721_020714.bak/audit_5.md` Round 5 收尾时，用户对 4 项选项的表态：

| 选项 | 含义 | 用户态度 |
|----|----|----|
| A | 保留四选项全部展开 | ❌ 未选 |
| B | 推进 SCC 软下限修订 | ❌ 未选 |
| C | L1 留 COULD（L2 softloor/L3 defer/L4 defer/L5 defer/L6 defer）| ❌ 未选 |
| **scope-a**：3 文件收尾（D1 L1 升级决策 + D2 L2 softloor + D3 L3 defer） | ✅ **已采纳** |

> **引自 v31 CONVERGED.md 解决栏**：scope-a = audit_5 + review_5 + CONVERGED 三文件收尾，**默认走 L1 retain（C 留 COULD）**。

---

## 候选方案

| 选项 | 内容 | 影响范围 | 与 v31 SSOT 兼容性 |
|----|----|----|----|
| **A**：升级必填 | 把 `ssot_citation_path` 改为 MUST；补填 230 TC + 修改生成器 | `.mdc` / `.py` / v31 `PLAN.md` §3.2.2 + §9.2 | ❌ **改 SSOT**（v31 已 achieved）|
| **B**：移除字段 | 从 v31 §3.2.2 / §9.2 删除 `ssot_citation_path` 字段 | v31 `PLAN.md` 字段字典 | ❌ **改 SSOT** |
| **C（已选）**| 保留 COULD + 列入 L1 校验脚本"建议项"（warn 但不阻断）| L1 校验脚本 `.py`（不破坏 SSOT）| ✅ **不破坏 v31 SSOT** |

---

## 决策

**选项 C**：保留 `ssot_citation_path` 为可选字段（COULD），列入 L1 校验脚本"建议项"（warn 但不阻断）。

### 决策依据

1. **用户 Round 5 表态 scope-a**：D1 L1 升级决策走默认 C（RETAIN），不升级必填
2. **不破坏 v31 SSOT**：v31 已 achieved，COULD 字段定义保持不变
3. **可审计追溯**：决策落档 `v32/decision_l1_upgrade.md`，后续 v32 Round 3+ 若有 v32_04 多项目样本，可回查 C 选项是否需要调整
4. **COULD 不是真空字段**：虽然不强制填，但建议填——L1 校验脚本可加 warn 提示

### 执行结果

| 项 | 状态 |
|----|----|
| 修改 `STAGE_S5_TEST_POINTS.mdc` | ❌ 不动（v31 SSOT）|
| 修改 `STAGE_S6_TEST_CASES.mdc` | ❌ 不动（v31 SSOT）|
| 修改 `MODULES.md` | ❌ 不动（v31 SSOT）|
| 修改 `DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 | ❌ 不动（v31 SSOT）|
| 修改 `archive/v31_20260721_020714.bak/PLAN.md` §3.2.2 | ❌ 不动（v31 已归档）|
| `v32/decision_l1_upgrade.md` 落档 | ✅ 本档 |

---

## 后续验证（Round 3 act 启动条件）

- **触发条件**：v32_04 多项目样本回归（`v32_04_candidate_samples.md`）启动了至少 2 个新样本，且新样本中 `ssot_citation_path` 仍然 0/N 填充
- **若触发**：Round 3 act 重新评估 C 选项 → 是否升级 A（必填）或保持现状
- **若不触发**：`ssot_citation_path` 维持 COULD 状态，决策落档保留

---

## 验证证据

| 来源 | 关键数据 |
|----|----|
| `archive/v31_20260721_020714.bak/coverage_report.md` §3 | v31 扩展字段填充率：3/4 = 75%（`ssot_citation_path` 0/230）|
| `archive/v31_20260721_020714.bak/PLAN.md` §3.2.2 | `ssot_citation_path` 字段定义（COULD）|
| `archive/v31_20260721_020714.bak/PLAN.md` §9.2 | TC 字段字典（`ssot_citation_path` 为 COULD）|
| `archive/v31_20260721_020714.bak/review_5.md` D1 | "Round 3 生成器未实现该字段写入；用户 Round 5 表态保留 COULD（v32 决策）"|
| `archive/v31_20260721_020714.bak/CONVERGED.md` §遗留 L1 | "LOW — 保留 COULD（v32 决策）"|

---

## 跨阶段影响

| 资产 | 影响 |
|----|----|
| S6 L1 校验脚本 | ⚠️ 后续可加 warn（不阻断）— Round 3 act 决定是否实施 |
| S7 审查员 | ❌ 不变（v31 §3.4 三条铁律未含 ssot_citation_path）|
| v32_04 多项目样本 | ⏳ 验证触发条件 — Round 3 act 决策 |

---

> **DT-V32-001 决策落档** — 选项 C（保留 COULD）生效，与 v31 SSOT 兼容；后续 Round 3 act 由 v32_04 触发条件决定是否重评
