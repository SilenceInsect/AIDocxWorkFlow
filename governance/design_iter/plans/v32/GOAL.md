# v32 GOAL — v31 6 项遗留渐进式推进（路线规划轮）

> **Goal ID**: v32-v31-legacy-progressive-001
> **Date**: 2026-07-21
> **Round**: 1（路线立项 + 草案）
> **上游**: v31 achieved（`governance/design_iter/plans/v31/CONVERGED.md`）
> **状态**: 启动阶段（active, loop_round=1）

---

## 顶层目标

v31 S5/S6 方法论重写在 5 轮收敛后 achieved：14 文件归档 + v3.01 样本 230 TP / 230 TC 跑通 + 4 项覆盖率 100% + TC 字段语义收紧 230/230。

v31 收尾报告（`v31/review_5.md` §Round 5 缺陷汇总）留下 **6 项遗留（L1~L6）**，分布在 3 个用户选项：

| 用户选项 | 立项 | 遗留项 |
|----|----|----|
| A: L1 retain | 保留 COULD | L1 `ssot_citation_path` 字段升级决策 |
| B: L2 softloor | 软下限修订 | L2 SCC 软下限 80% → 50% + 商城加权 |
| C: L3 defer | 留 v32 处理 | L3 UI TP 交叉 S3 prototype |
| scope-a | 3 文件收尾（audit_5 + review_5 + CONVERGED）已采纳 | D1~D3 落档已闭合 |

v32 核心推进 6 项遗留中的 4 项（L2/L3/L4/L5/L6），**渐进式收敛**——不重写 v31 SSOT、不修改 `.mdc` 强制规则。

---

## 任务范围（v32_01 ~ v32_05）

| 路由 | 主题 | 来源 | 严重度 |
|----|----|----|----|
| **v32_01** | UI TP 交叉 S3 prototype（UI 控件级覆盖率）| `v31/review_5.md` D3 / L3 | LOW |
| **v32_02** | density-OBJ 维度（per-OBJ 4 类型齐全率）| `v31/review_5.md` D4 / L4 | MEDIUM |
| **v32_03** | SCC 软下限修订（80% → 50% + 商城加权）| `v31/review_5.md` D2 / L2 | MEDIUM |
| **v32_04** | 多项目样本回归（2~3 个 v3.01 之外的版本）| `v31/review_5.md` D5 / L5 | MEDIUM |
| **v32_05** | 测试点库首批回灌（依赖 S7/S8 实际跑通 + 人工审核）| `v31/review_5.md` D6 / L6 | LOW |

**L1 待决**：v32 Round 2 act 决策项（升级必填 / 移除该字段 / 留 COULD）。

---

## 不在范围（明确禁止）

- ❌ 重写 `v31/PLAN.md`（v31 SSOT 已 achieve，不得漂移）
- ❌ 修改 `.cursor/MODULES.md`
- ❌ 修改 `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` / `STAGE_S6_TEST_CASES.mdc`
- ❌ 修改 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3
- ❌ 修改 `.cursor/rules/product_format_rules.yaml`
- ❌ 修改 `.mdc` 强制规则（本轮仅出治理草案，不动约束文件）

---

## 依赖

| 依赖项 | 路径 | 状态 |
|----|----|----|
| v31 archive 17 文件 | `governance/design_iter/archive/v31_20260721_020714.bak/` | ✅ byte_identical 已确认 |
| v31 6 项遗留（D1~D6）| `v31/review_5.md` Round 5 缺陷汇总 | ✅ 已读 |
| v31 5 治理方向（v32_01~v32_05）| `v31/review_5.md` §v32 治理路线 | ✅ 已读 |
| 用户 Round 5 表态 | `v31/audit_5.md` 4 选项 | ✅ retain/softloor/defer/scope-a |
| v31 PLAN.md 治理 SSOT | `archive/v31_20260721_020714.bak/PLAN.md` 680 行 | ✅ 已读（§3.1.3 SCC + §3.2.2 TC 字段 + §8.3 pending_candidates + §10.1 C1~C6）|

---

## Round 1 任务边界

本轮为**路线规划轮**（与 v31 Round 0 同质），仅出 5 文件：
1. `v32/GOAL.md`（本文件）
2. `v32/PLAN.md`（五段式治理 SSOT，~500 行）
3. `v32/audit_1.md`（AC 论证）
4. `v32/review_1.md`（复盘）
5. `v32/snapshot.json`（goal-loop 快照）

不实际启动任何治理项（v32_01~v32_05 详情留至 Round 2+ act 轮）；task_queue 由后续 act 轮填充。

---

## ACCEPT 标准（4 条全 PASS）

| # | 标准 | 验证 |
|----|----|----|
| **AC-1** | v32_01 ~ v32_05 全部有草案路径 | `PLAN.md` §3 完整列出 |
| **AC-2** | L2 SCC 软下限公式落地（修订前后对照）| `PLAN.md` §3.3 给出新公式 |
| **AC-3** | 不修改 `.mdc` 强制规则（v31 SSOT 不漂移）| `git diff --name-only` 限于 `governance/design_iter/plans/v32/` |
| **AC-4** | 文档均引用 v31 archive 路径（不引用 v31/ 现役目录）| `grep "archive/v31_20260721_020714.bak"` 引用 ≥ 3 处 |

---

> **v32 GOAL 落档** — Round 1 启动，仅做路线规划 + 草案 + 4 条 AC，不启动任何治理项执行
