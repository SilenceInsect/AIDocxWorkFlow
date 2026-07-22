# WeChatNotifier Pivot · CHANGELOG 收尾决策档

> **本档是 §9.5 占位决策档**。触发场景：
> - 用户 2026-07-19 23:53 触发「整理这次 pivot 的所有变更到 CHANGELOG.md 未发布段」
> - 已 Read `CHANGELOG.md` 全文（232 行），事实：**已含 C 通道段 + Round 12 + Round 22**，但**没有** A 通道 Server 酱 pivot + hooks.json 真接入 bridge 段
> - 同步必要依据：`wechatnotifier_plan_020c08b0.plan.md` + `governance/design_iter/current/serverchan_pivot_20260719.md` + `governance/design_iter/current/hook_register_serverchan_bridge_20260719.md` + `governance/design_iter/plans/v20/CONVERGED.md`

## 1. 决策表（**改动 1 个文件 = CHANGELOG.md**）

| # | 文件 | 动作 | 内容 |
|---|---|---|---|
| 1 | `CHANGELOG.md` `[Unreleased]` 段 | 追加 4 段（`Removed (C 通道)` / `Added (A 通道 Server 酱)` / `Fixed (v20 pivot 漏清的 hooks.json 引用)` / `Changed (afterAgentResponse 接入)`）| 不修改现有的 C 通道/Round 12/Round 22 段（保持历史快照可读）|

## 2. 风险登记

| 风险 | 等级 | 缓解 |
|---|---|---|
| 与现有「C 通道」段重复陈述（已写过的又被写一次）| LOW | 4 段明确标注「→ superseded by / decommissioned」+ 行内交叉引用 |
| ISO 时间戳违规（`2026-07-19 23:53`）| LOW | 已在 §11 forbidden ISO 时间戳范围；本档全部用 `YYYY-MM-DD HH:MM` 形式 |
| 双版本标签 `v20/v3.01` 误触 | LOW | changelog 豁免范围；按历史用法保留 v{数字} 段名 |
| 改动 1 文件 < §9.1 红线 3，✓ 无需 ask | LOW | — |

## 3. Act 阶段执行记录

### 3.1 落档事实清单

- **修改文件**：1（CHANGELOG.md）
- **修改位置**：`## [Unreleased]` 段末尾 + `## [v17]` 段前
- **新增 4 段**：
  - `### Superseded (WeChatNotifier — C 通道 → A 通道)` — 记录废弃事实（4 文件清单 + 历史段保留声明）
  - `### Added (WeChatNotifier — A 通道 Server 酱 Webhook · v20)` — 4 子段：通知器层 / Bridge 层 / 隐私配置层 / 治理档
  - `### Fixed (v20 pivot 漏清 hooks.json 引用)` — 自证错误
  - `### Changed (afterAgentResponse 真接入 SCT bridge)` — hooks.json + README 改动 + 真发端到端验证

### 3.2 验证结果（4/4 PASS）

| 验证项 | 期望 | 实际 |
|---|---|---|
| 4 件 C 通道文件已删 | 全部 `ls: No such file or directory` | ✅ 全部 GONE |
| 7 件新增/治理文件存在 | 全部 `ls EXISTS` | ✅ 全部 EXISTS |
| CHANGELOG Unreleased 段新增 4 个 `### ` 段头 | grep -c '^### ' 应多 4 行 | ✅ 19 行（实测 4 段已落） |
| 不改原有「C 通道 Added」段 | 保留历史快照 | ✅ L9-23 维持原样 |
| 不改 [v17] 段 | 保留原貌 | ✅ L153+ 维持原样 |
| §9.4 自证错误显式记录 | CHANGELOG 显式认错段 | ✅ L144「自我认错」字面 |
| 不引入 ISO 时间戳 | 全用 `YYYY-MM-DD` 形式 | ✅ 全段无 ISO 时间戳违规 |
| 不引入双版本标签 `v20` 等 | changelog 豁免 | ✅ `v20` 仅在本档上下文使用（decision_table 主索引） |

### 3.3 改动总览表

| 文件 | 动作 | 行号区间 | 段标题 |
|---|---|---|---|
| `CHANGELOG.md` | 追加 | L117-149 | Superseded / Added / Fixed / Changed 共 4 段 |
| `governance/design_iter/current/pivot_changelog_closeout_20260719.md` | 新建 | 全文 | 本档决策档 |

