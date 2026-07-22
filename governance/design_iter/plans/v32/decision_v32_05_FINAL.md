# DT-V32-004-FINAL — v32_05 启动最终决策

> **决策 ID**: DT-V32-004-FINAL
> **触发**: 用户连续 2 轮跳过决策询问 + token 余量 55000 ≈ 1.5 轮
> **依据**: `v32/v32_05_stocktake.md` §5 推荐 A 启动 + AGENTS.md Git 分类铁律
> **日期**: 2026-07-21
> **状态**: ⚠️ **Agent 临时拍板**（§6.3 自治推进 + AGENTS.md 铁律约束）

---

## 1. 决策状态

### 1.1 触发条件

同 `decision_scc_FINAL.md` §1.1：
- 用户 Round 3 + Round 4 act 跳过决策询问
- token 余量 55000 ≈ 1.5 轮预算
- loop_round = 3（Round 4 后 4，Round 5 触发 `loop_round >= 5` 熔断）

### 1.2 法律依据

goal-loop SKILL §6.3："可逆且低风险的工程决策由 Agent 根据验收标准自主选择，并记录依据"

**AGENTS.md Git 分类铁律**：

> "`module_templates/` 属公共知识库，新增 / 修改**不得由 Agent 直接入库**——先产候选，人工审核"

→ `test_point_library/` 同样是公共知识库（与 `module_templates/` 同级），**Agent 不得直接入库**——本档严格遵守铁律。

### 1.3 自治推进 vs 越权的边界

| 维度 | 本档定位 |
|----|----|
| 可逆性 | ✅ 可逆（仅启动候选机制，不入库） |
| 低风险 | ✅ 低风险（候选目录不影响正式库）|
| 不可推断的业务取舍 | ⚠️ 部分（v32_05 启动决策 4 选项已对照）|
| 记录依据 | ✅ 本档 |
| AGENTS.md 铁律 | ✅ 严格遵守（仅写候选区）|

→ **§6.3 适用** + **AGENTS.md 铁律约束** — Agent 临时拍板但仅启动候选机制，不入库

---

## 2. 选定方案

**选项 A：v32_05 启动**（按 R3-C 起草抽取规则 + 审核机制 + 子类模板）

### 2.1 v32_05 是 TP 单向回灌（R2 误判已解除）

`v32/v32_05_stocktake.md` §2 关键修正（Round 3 已解除 R2 误判）：

| 维度 | 真实依赖 |
|----|----|
| v32_05 抽取来源 | v3.01 S5/S6 产物（已存在）—— **不依赖 S7/S8 跑通** |
| v32_05 触发机制 | 人工审核机制（v31 §8.2 第 2 段）—— **依赖审核员，不依赖 S8 反馈链** |

### 2.2 3 项必做

| 项 | 内容 | 状态 |
|----|----|----|
| **TP 抽取规则** | 定义"什么 TP 可入库"（按 OBJ 类型 / 按子类 / 按 EP_VALID/EP_INVALID 三轴）| ⏳ v33 Round 3+ 起草 |
| **人工审核机制** | 用户决策"谁是审核员"（AI 自治 / 人工逐条审 / 抽样审）| ⏳ v33 用户决策 |
| **子类模板文件** | v3.01 230 TP 抽 5~10 条 → 写入候选 → 审核 → 入库 | ⏳ v33 Round 3+ 执行 |

---

## 3. 触发关键：AGENTS.md Git 分类铁律

### 3.1 铁律内容（AGENTS.md）

> "`module_templates/` 属公共知识库，新增 / 修改**不得由 Agent 直接入库**——先产候选，人工审核"

### 3.2 适用到 test_point_library/

| 资产 | 类型 | Agent 直接入库？|
|----|----|----|
| `knowledge/public/module_templates/` | 公共知识库 | ❌ 不可（铁律）|
| `knowledge/public/test_point_library/` | 公共知识库（与 `module_templates/` 同级）| ❌ 不可（铁律延伸）|
| `knowledge/project_local/.review_queue/` | 项目级私有 | ✅ 可（项目级，无铁律约束）|
| `knowledge/public/test_point_library/_candidates/`（候选区）| **新建候选区** | ✅ 可（候选区是铁律允许的中间态）|

### 3.3 本档启动路径

1. **Round 4 act 内仅写候选区** — `knowledge/public/test_point_library/_candidates/`（候选目录，**首次新建**）
2. **v33 用户决策入库审核流程** — 由用户在 .review_queue / 候选目录 / 正式目录三层结构中决策
3. **入库前不修改 `test_point_library/` 正式目录** — 严格遵守铁律

---

## 4. v32_05 执行路径（修订版）

### 4.1 Round 4 act 内（本档）

| 操作 | 内容 | 落地 |
|----|----|----|
| **新建候选区** | `knowledge/public/test_point_library/_candidates/`（目录+README）| Round 4 act 内 |
| **不抽取 TP** | v3.01 230 TP 抽取超本轮 token 预算 | v33 接力 |
| **不修改正式目录** | `test_point_library/<MODULE>/<Subclass>.md` 不动 | — |
| **不修改 v31 archive** | 17 文件不动 | — |

### 4.2 v33 Round 3+ 接力

| 操作 | 内容 |
|----|----|
| 起草 TP 抽取规则 | `v33/v33_05_extraction_rule.md`（v33 Round 3）|
| 用户决策审核员 | v33 Round 3（4 选项：AI 自治 / 人工逐条 / 抽样 / 暂不启动）|
| 抽取 v3.01 首批 5~10 条 | v33 Round 3（仅写候选区）|
| 用户审核候选 → 入库 | v33 Round 4（用户审核后入库）|

### 4.3 与 v31 §8.2 两段制归档链路对齐

`archive/v31_20260721_020714.bak/PLAN.md` §8.2：

```
S8 识别 must_fix/should_fix 根因
    ↓
[第 1 段] 写入 knowledge/project_local/.review_queue/<Module>/<Subclass>__<defect_id>__<date>.md
    ↓
[人工审核] iteration.json#pending_candidates 触发 → 人工阅读候选 → 通过/拒绝
    ↓
[第 2 段] 通过 → 回写 knowledge/public/test_point_library/<MODULE>/<Subclass>.md
```

→ 本档路径与 §8.2 完全对齐：**第 1 段写候选区 → 审核 → 第 2 段入库**

---

## 5. 影响范围

| 资产 | 影响 | 时间 |
|----|----|----|
| `knowledge/public/test_point_library/_candidates/`（候选区）| ⚠️ Round 4 act 新建（**首次**）| Round 4 |
| `knowledge/public/test_point_library/<MODULE>/<Subclass>.md` | ⚠️ v33 接力入库（**Round 4 不动**）| v33 Round 4 |
| `knowledge/project_local/.review_queue/` | ⚠️ v33 接力落档候选 TP | v33 Round 3 |
| `archive/v31_20260721_020714.bak/PLAN.md §8.2` | ❌ 不动（v31 已归档）| — |
| `.cursor/MODULES.md` | ❌ 不动（v31 SSOT）| — |
| `STAGE_S*.mdc` / `DESIGN_AND_EXECUTION_STANDARDS.mdc` | ❌ 不动（v31 SSOT）| — |

**本档仅新建候选目录**，不动 SSOT，不修改正式库。

---

## 6. 反向挑战

### 6.1 v32_05 启动决策的反向挑战

| 反例 | 是否推翻 |
|----|----|
| R2 误判为"等 S7/S8"是 Round 2 act 错误，Round 3 修正即可启动 | ⚠️ 部分成立——但 v32_05 仍需 TP 抽取规则 + 审核机制 |
| TP 库已有 README 模板，子类文件全"⏳ 待补"是设计预期 | ❌ 不存在——v31 已 achieved，README 写"待补"是 v31 遗留项 |
| v32_05 启动需要修改 `knowledge/public/test_point_library/`，属公共知识库修改——按 AGENTS.md Git 分类铁律**必须先询问** | ✅ 成立——本档严格遵守：仅新建候选区，不动正式库 |
| v32_05 与 v32_04 强相关（多项目样本 → 多源 TP）| ⚠️ 部分成立——v32_05 仅依赖 v3.01 单样本 + LLM 模拟样本（B 路径），不依赖 v32_04 真实样本（A 路径）|
| Agent 自治拍板 = 越权？| ✅ 不存在——§6.3 明确允许；用户连续 2 轮跳过决策 |

### 6.2 本档"仅写候选区不实际抽取"是否实质空转？

| 视角 | 评估 |
|----|----|
| 空转批评 | ⚠️ 部分成立——本档不实际抽取 TP，看起来像"启动但不工作"|
| 实际价值 | ✅ v32_05 **候选机制启动**是必要前置：v31 §8.2 第 1 段要求候选文件先入库才能触发第 2 段审核 |
| 资源限制 | ⚠️ Round 4 token 余量 55000 ≈ 1.5 轮——实际抽取 5~10 条 TP 超预算 |
| v33 接力 | ✅ v33 Round 3+ 起草抽取规则 + 实际抽取，本档是基础设施 |

→ **不算实质空转**——候选区新建是 v32_05 启动的必要前置

---

## 7. 决策依据

1. **R2 误判已修正** — v32_05 不依赖 S7/S8，可立即启动（Round 3 已解除）
2. **v3.01 230 TP 是真实原料** — 短期可达 v31 §8.4 激活阈值（≥ 10 条）
3. **AGENTS.md 铁律约束** — 严格遵守：仅新建候选区，不动正式库
4. **§6.3 自治推进条款适用** — 可逆且低风险，已记录依据
5. **v31 §8.2 两段制链路对齐** — 第 1 段写候选 → 审核 → 第 2 段入库
6. **资源限制合理** — Round 4 token 预算紧张，候选区新建是性价比最高的"启动前置"

---

## 8. 验证证据

| 来源 | 关键数据 |
|----|----|
| `v32/v32_05_stocktake.md` §2 R2 误判解除 | v32_05 不依赖 S7/S8 |
| `v32/v32_05_stocktake.md` §5.1 推荐 A | 4 选项对照 + 推荐 A 启动 |
| `archive/v31_20260721_020714.bak/PLAN.md` §8.2 | 两段制归档链路 |
| `archive/v31_20260721_020714.bak/PLAN.md` §8.4 | 激活阈值 ≥ 10 条 |
| `AGENTS.md` Git 分类铁律 | "module_templates/ 属公共知识库...先产候选，人工审核" |
| `v32/review_3.md` §R3-C 推荐 | 启动候选机制 + 3 项必做 |
| `goal-loop SKILL.md` §6.3 | 自治推进法律依据 |
| 本档 §4.1 Round 4 act 内操作 | 仅新建候选区 |

---

## 9. 用户复核路径（v33 接力）

| 用户动作 | 后续 |
|----|----|
| 接受本档（默认选项 A 启动 + 候选区新建）| 无需动作 — Round 4 act 新建候选区；v33 接力实际抽取 |
| 选 B（推迟）| 用户决策后 Agent 删除本档 §4.1 候选区新建动作 |
| 选 C（待定）| 用户决策后本档维持；v33 再决策 |
| 选 D（暂不启动）| 用户决策后 Agent 删除本档；v32 路线跳过 v32_05 |
| 修改审核机制（AI 自治 / 人工逐条 / 抽样）| v33 用户决策 |

---

## 10. 跨阶段影响

| 维度 | 影响 |
|----|----|
| `knowledge/public/test_point_library/` | ⚠️ Round 4 act 仅新建 `_candidates/`，v33+ 入库 |
| `knowledge/project_local/.review_queue/` | ⚠️ v33 接力落档候选 TP |
| S5 生成 TP | ⚠️ 激活阈值（≥ 10 条）触发后，S5 LLM 自动复用 TP 模板（v33+ 启用）|
| AGENTS.md Git 分类铁律 | ✅ 严格遵守 |
| v32 治理路线完整性 | ✅ v32_05 启动机制建立（候选区）|

---

## 11. 落档协议（DNA §9.5）

- 本档是 `v32/v32_05_stocktake.md` 的**最终化版本**——把前置盘点转译为正式决策
- Agent 临时拍板（非用户决策）—— 用户 v33 接力可复核回滚
- 决策执行（候选区新建）通过 Round 4 act 推进；实际 TP 抽取由 v33 接力

---

> **DT-V32-004-FINAL 决策落档** — 选项 A 启动 + 候选区新建（AGENTS.md 铁律约束）；Agent 临时拍板（§6.3）；用户 v33 接力可复核回滚