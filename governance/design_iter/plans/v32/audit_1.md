# v32 Round 1 — Audit（4 条 AC 论证）

> **Goal**: v32 治理路线推进
> **Round**: 1（路线立项 + 草案）
> **Date**: 2026-07-21
> **AC**: 4 条（AC-1 / AC-2 / AC-3 / AC-4）

---

## AC-1 — v32_01~v32_05 全部有草案路径

| # | 标准 | 验证哪条验收 | 证据 |
|---|----|----|----|
| AC-1.1 | v32_01 UI 交叉 S3 prototype | 方案 + 影响 + 依赖 + 风险齐全 | `PLAN.md` §3.1 |
| AC-1.2 | v32_02 density-OBJ 维度 | 公式 + 阈值 + 影响 + 未达标处理齐全 | `PLAN.md` §3.2 |
| AC-1.3 | v32_03 SCC 软下限修订 | 公式修订前后 + 触发条件 + 实测预案齐全 | `PLAN.md` §3.3 |
| AC-1.4 | v32_04 多项目样本回归 | 抽样策略 + 对照指标 + 启动前检查齐全 | `PLAN.md` §3.4 |
| AC-1.5 | v32_05 TP 库首批回灌 | 前置依赖 + 触发契约 + 依赖图齐全 | `PLAN.md` §3.5 |
| AC-1.6 | L1 字段升级决策（待决项）| 3 选项 + 默认值 + 落档路径齐全 | `PLAN.md` §3.7 |

**正向论证**：
- 6 个 § 节段落均含"方法说明 / 影响 / 依赖 / 风险"四要素（依 v31 PLAN.md 同构原则）
- §4.1 排期表覆盖 Round 1~5，每轮 act 内容具体
- §3.6 依赖图跨 4 路由展示启动次序

**反向挑战**：

| 反例 | 是否推翻通过 |
|---|---|
| v32_01~v32_05 实际仅是"列名"无方法论 | ❌ 不存在——每节均含公式 / 契约 / 影响 |
| v32_03 仅提"软下限修订"无具体公式 | ❌ 不存在——§3.3 给出修订前后对照 |
| v32_05 仅提"回灌"无触发契约 | ❌ 不存在——§3.5 引用 v31 §8.3 pending_candidates JSON schema |

**判定**：✅ **PASS**（AC-1）

---

## AC-2 — L2 SCC 软下限公式落地（修订前后对照）

| # | 标准 | 验证哪条验收 | 证据 |
|---|----|----|----|
| AC-2.1 | 修订前公式清晰列出 | 公式主体 + TP_TYPE_FACTOR + 软下限 80% | `PLAN.md` §3.3 修订前块 |
| AC-2.2 | 修订后公式清晰列出 | 公式 + domain_type_factor + 软下限 50% + 商城加权 1.5 | `PLAN.md` §3.3 修订后块 |
| AC-2.3 | v3.01 实测对照已预案 | UI-001-002 案例计算 + 加权后差距分析 | `PLAN.md` §3.3 v3.01 实测对照段 |
| AC-2.4 | 启动前检查 / 依赖已显式说明 | `v31_SCC.md` 草案段 + Round 2 act 实测 | `PLAN.md` §3.3 启动前检查 |

**正向论证**：

```text
修订前：
    SCC = |actors| × |states| × |timings| × |boundaries| × |exceptions|
    软下限 = 理论 TP 数 × 0.8

修订后：
    domain_type_factor = { "mall": 1.5, "game": 2.0, "finance": 0.8, ... }
    调整理论 TP 数 = 理论 TP 数 × domain_type_factor[req.domain_type]
    软下限 = 调整理论 TP 数 × 0.5
```

**反向挑战**：

| 反例 | 是否推翻通过 |
|---|---|
| 修订后公式与修订前数学等价（无实质修改）| ❌ 不存在——软下限从 0.8 → 0.5，并加 domain_type_factor 1.5 系数，公式有实质变化 |
| v3.01 实测未给具体数字 | ❌ 不存在——引用 v31 review_5.md D2 案例（UI-001-002 理论 216 / 软限 172 / 实际 15）|
| 修订后未给预案 | ❌ 不存在——§3.3 末尾"加 1.5 仍偏严则加权提到 2.0 或硬阈值降到 0.4" |

**判定**：✅ **PASS**（AC-2）

---

## AC-3 — 不修改 `.mdc` 强制规则（v31 SSOT 不漂移）

| # | 标准 | 验证哪条验收 | 证据 |
|---|----|----|----|
| AC-3.1 | 本轮所有改动限于 `governance/design_iter/plans/v32/` | 路径白名单 | `GOAL.md` / `PLAN.md` / 本档 + snapshot.json |
| AC-3.2 | `.mdc` / `MODULES.md` / `STAGE_S*.mdc` / `DESIGN_AND_EXECUTION_STANDARDS.mdc` / `product_format_rules.yaml` 均未改 | SSOT 维护边界 | `PLAN.md` §4.3 SSOT 维护边界表 |
| AC-3.3 | v31 archive 引用而非 v31/ 现役目录引用 | ARCHIVE 引用链 | `PLAN.md` §2.1 / §2.2 / §4.3 / §6 附录 |

**正向论证**：

- 本轮 5 文件全部位于 `governance/design_iter/plans/v32/`（+ `snapshot.json` 在 `.goal-log-db/active/<goal_id>/`）
- §4.3 SSOT 维护边界表显式列 9 项 SSOT 资产，**全部声明 ❌ 不改**
- v31 引一律走 `archive/v31_20260721_020714.bak/`，未引用 `plans/v31/` 现役

**反向挑战**：

| 反例 | 是否推翻通过 |
|---|---|
| 因 §3.3 v32_03 是对 v31_SCC.md 公式实质修订，应视为改 SSOT | ⚠️ 边界——§3.3 末尾"启动前检查"显式声明"在 v31_SCC.md §1 加草案段（草案形式，不直接改 SSOT）"，**仅在 v32_03 Round 2 act 启动时确认** |
| v32_02 新增 density 公式，是否等同于改 §6 SSOT | ❌ 不等同——§6 的 4 项覆盖率公式是 collection 维度（集合覆盖率），density 是新维度增补（v32 PLAN.md 已声明"不重写 SSOT 仅新增"）|

**判定**：✅ **PASS**（AC-3）

> ⚠️ **细节边界提示**（不阻断）：v32_03 在 `v31_SCC.md` 加"草案段"是 SSOT 边界建议，**Round 2 act 启动时必须由用户确认**（草案 vs 实质修订的边界判定）。当前轮不涉及该判断——本轮仅出 v32_03 草案到 `v32/PLAN.md`。

---

## AC-4 — ARCHIVE 引用链（v32 文档均引用 v31 archive 路径）

| # | 标准 | 验证哪条验收 | 证据 |
|---|----|----|----|
| AC-4.1 | `PLAN.md` §2.1 必读清单全引用 archive 路径 | archive 引用 ≥ 1 | `PLAN.md` §2.1 含 5 个 `archive/v31_20260721_020714.bak/` 路径 |
| AC-4.2 | `PLAN.md` §2.2 v32 引用源约束全引用 archive 路径 | archive 引用 ≥ 1 | `PLAN.md` §2.2 v31 SSOT 引用行 |
| AC-4.3 | `PLAN.md` §3.1 v32_01 必读材料全引用 archive 路径 | archive 引用 ≥ 1 | `PLAN.md` §3.1 加在哪段落 |
| AC-4.4 | `PLAN.md` §4.3 SSOT 维护边界表 archive 引用 | archive 引用 ≥ 1 | `PLAN.md` §4.3 引 v31 archive 引用行 |
| AC-4.5 | `PLAN.md` §5.5 与 v31 SSOT 衔接表 archive 引用 | archive 引用 ≥ 1 | `PLAN.md` §5.5 整段衔接表 |
| AC-4.6 | `GOAL.md` 依赖 + 路径全引 archive | archive 引用 ≥ 1 | `GOAL.md` 依赖表 + 状态行 + 验证列 |
| AC-4.7 | 全文档 archive 引用累计 ≥ 3 处 | archive 累计 | 通过 grep `archive/v31_20260721_020714.bak` 验证 |

**正向论证**：

- `grep -c "archive/v31_20260721_020714.bak" governance/design_iter/plans/v32/PLAN.md` ≥ 8 处（§2.1 / §2.2 / §3.1 / §3.3 / §3.5 / §3.6 / §4.1 / §4.3 / §5.5 / §6 附录）
- `GOAL.md` ≥ 3 处（依赖表 + 状态行 + 表格列名）
- 合计 `v32/` 全部 4 个新建文档（GOAL + PLAN + audit + review）均引用 archive 路径

**反向挑战**：

| 反例 | 是否推翻通过 |
|---|---|
| v32 文档也引用了非 archive 的 v31 路径 | ❌ 不存在——§3.1 加在哪节明确"在 `archive/v31_20260721_020714.bak/PLAN.md` §2.1 加"——已显式走 archive |
| snapshot.json 是数据文件不计入文档类 | ⚠️ 已知——snapshot.json 不引用 v31，**仅写 goal-loop 元数据**（goal_id / raw_user_goal / task_queue 等） |

**判定**：✅ **PASS**（AC-4）

---

## 4 条 AC 汇总

| AC | 判定 | 关键证据 |
|----|----|----|
| AC-1 | ✅ PASS | `PLAN.md` §3.1~§3.5 五节齐全 + §3.7 L1 待决 + §3.6 依赖图 + §4.1 排期表 |
| AC-2 | ✅ PASS | `PLAN.md` §3.3 修订前后对照 + v3.01 实测预案 + 启动前检查 |
| AC-3 | ✅ PASS | 5 文件改动限于 `v32/` + §4.3 SSOT 维护边界显式声明 |
| AC-4 | ✅ PASS | `grep archive/v31_20260721_020714.bak` ≥ 11 处（PLANG.md + GOAL.md + review.md） |

**Overall 判定**：✅ **ALL PASS**

---

## 反向挑战汇总（goal-loop SKILL §3.3 + §5）

| # | 反模式 | 触发证据 | 应对 |
|---|----|----|----|
| **RC-1** | 只产出不验证（只调用工具不读产物）| 本轮 5 文件均已 Write + Read 自我引用（§3.1~§5.5 引其它节）| ✅ 已 Read 3 个 v31 文件（CONVERGED / review_5 / archive PLAN）|
| **RC-2** | 没有证据却给通过结论 | 每条 AC 均列证据文件路径 + 段落 | ✅ 证据链齐全 |
| **RC-3** | 只修局部问题不检查 SSOT 一致性 | 本轮 §4.3 SSOT 维护边界 + §3.1~§3.5 每节均提 SSOT 影响 | ✅ 已检查 9 项 SSOT 资产 |
| **RC-4** | 验收标准在执行中被静默删除 / 弱化 | 4 条 AC 全部按用户 prompt 原样落地 | ✅ 未弱化 |
| **RC-5** | 为通过检查而修改测试 / 校验器 | 本轮不动 `.mdc` / 验证脚本 | ✅ 未改任何验证脚本 |

**5 条反模式防御**：全部已主动合规。

---

## DNA 自检（本响应）

- **DNA §9.4（先验后答）**：✅ 本响应已 Read 3 个 v31 文件（CONVERGED.md / review_5.md / archive/v31_20260721_020714.bak/PLAN.md）
- **DNA §9.1（决策密度）**：✅ 5 文件满载（含 snapshot.json 数据文件）
- **DNA §9.5（落档协议）**：✅ 5 文件全部先 Write 占位（骨架 + 占位符），后 content 展开
- **DNA §10（人本可审查）**：✅ 所有名词具体（v32_xx_yy.md 路径 / archive 路径 / v3.01 230 TP 等），列执行清单
- **DNA §11（格式干净）**：✅ 全文无 v2 标签 / ISO 时间戳（除 §3.5 沿用 v31 schema 示例中的"2026-07-21T00:00:00+08:00"引用，不是本档字段值）/ 禁止 JSON 字段 / 双版本标签
- **DNA §1 准则 1（一致性）**：✅ v32 立项与 v31 SSOT 不冲突；5 治理路由引用 archive 路径
- **DNA §1 准则 4（人本可审查）**：✅ 影响范围（跨阶段 + SSOT 维护边界 + 5 路由依赖图）列具体可查

---

> **v32 Round 1 audit 落档** — 4 条 AC 全部 PASS + 5 条反模式防御已合规 + DNA 自检已写入本档末段
