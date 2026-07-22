# v33 Round 2 Act — TP 抽取规则起草

> **Goal**: v33 goal-loop：接力 v32 治理路线剩余 6 项移交任务
> **Round**: 2
> **Date**: 2026-07-21
> **关联**: VC5（v32_05 TP 库首批回灌）

---

## 1. v3.01 TP 实测数据

### 1.1 样本概况

| 指标 | 值 |
|---|---|
| TP 总数 | **230 条** |
| Story 数 | **16 个** |
| Epic 数 | **8 个**（按 Epic ID 分布推断）|

### 1.2 模块分布（v3.01 实测）

| 模块 | TP 数 | 占比 |
|---|---|---|
| **BIZ** | 163 | 70.9% |
| **UI** | 47 | 20.4% |
| **LOG** | 16 | 7.0% |
| **LINK** | 4 | 1.7% |
| **CONFIG / AUX / SPECIAL / HINT** | 0 | 0% |
| **合计** | **230** | **100%** |

### 1.3 单条 TP 字段结构（v3.01 实测）

| 字段 | 类型 | 取值样例 |
|---|---|---|
| `tp_id` | string | `UI-001-001-TP-001` |
| `module` | enum(8) | `UI` / `BIZ` / `LOG` / `LINK` |
| `story_id` | string | `UI-001-001` |
| `epic_id` | string | `UI-001` |
| `obj_id` | string | `UI-001-001-OBJ-01` |
| `obj_name` | string | `商城首页布局与控件` |
| `feature_point_ref` | string | `FP-01-01` |
| `fp_name` | string | `热门道具展示` |
| `case_type` | enum | `功能测试` / `边界测试` 等 |
| `test_method` | list[str] | `["等价类划分", "边界值分析"]` |
| `test_point_type` | enum | `POSITIVE` / `NEGATIVE` / `BOUNDARY` 等 |
| `title` | string | `商城首页布局热门道具展示正常流程` |
| `description` | string | `玩家在商城首页布局与控件场景下触发热门道具展示功能...` |
| `priority` | enum | `P0` / `P1` / `P2` |
| `status` | enum | `Draft` / `Final` 等 |
| `s4_reference` | string | `S4-UI-001-1.1.1` |
| `boundary` | string | `无` |
| `is_assumed` | bool | `false` |
| `applies_rule` | string | `Push1: UI模块...` |

---

## 2. 抽取规则（v33 Round 2 起草）

### 2.1 抽取目标

首批抽取 **5~10 条** TP 入候选区（`knowledge/public/test_point_library/_candidates/`），作为 v32_05 启动的第一步。

### 2.2 抽取原则（三轴筛选）

| 轴 | 筛选目标 | 具体规则 |
|---|---|---|
| **轴 1：模块分布** | 覆盖主要模块 | 每模块至少抽 1 条（BIZ 优先，因占比最高 70.9%）|
| **轴 2：test_point_type 多样** | 覆盖主流类型 | POSITIVE / NEGATIVE / BOUNDARY / ERROR 至少各 1 条 |
| **轴 3：Story 分布** | 跨 Epic | 至少覆盖 3 个不同 Epic ID |

### 2.3 候选 TP 清单（v3.01 首批抽取）

按三轴原则，从 230 条中预选：

| 序号 | tp_id | 模块 | test_point_type | Epic | Story | 抽取理由 |
|---|---|---|---|---|---|---|
| **1** | `BIZ-001-001-TP-001` | BIZ | POSITIVE | BIZ-001 | BIZ-001-001 | BIZ 模块（占比最高）|
| **2** | `BIZ-001-001-TP-002` | BIZ | BOUNDARY | BIZ-001 | BIZ-001-001 | 边界类型（type 多样）|
| **3** | `UI-001-001-TP-001` | UI | POSITIVE | UI-001 | UI-001-001 | UI 模块（20.4%）|
| **4** | `UI-001-001-TP-002` | UI | NEGATIVE | UI-001 | UI-001-001 | 负向类型（type 多样）|
| **5** | `LOG-001-001-TP-001` | LOG | POSITIVE | LOG-001 | LOG-001-001 | LOG 模块（7%）|
| **6** | `BIZ-002-001-TP-001` | BIZ | ERROR | BIZ-002 | BIZ-002-001 | 跨 Epic（BIZ-002 ≠ BIZ-001）|
| **7** | `LINK-001-001-TP-001` | LINK | POSITIVE | LINK-001 | LINK-001-001 | LINK 模块（1.7%，最低占比）|

**说明**：
- 优先抽取 BIZ（70.9%）→ 2 条
- UI（20.4%）→ 2 条
- LOG（7%）→ 1 条
- LINK（1.7%）→ 1 条
- 覆盖 5 个 Epic（BIZ-001 / UI-001 / LOG-001 / BIZ-002 / LINK-001）
- 覆盖 5 种 test_point_type（POSITIVE / BOUNDARY / NEGATIVE / ERROR / POSITIVE）

### 2.4 抽取比例

| 指标 | 值 |
|---|---|
| 首批抽取数 | 7 条（选 7 条，覆盖 4 模块 + 5 Epic + 5 type）|
| 总样本池 | 230 条 |
| 抽取比例 | 3.0% |
| 是否满足 v31 §8.4 激活阈值（≥ 10 条）| ⚠️ 不足（7 < 10），首批为种子，后续补充至 ≥ 10 条 |

---

## 3. 抽取格式规范

### 3.1 候选文件名

```
<TP-ID>__v3.01__YYYYMMDD.md
```

示例：`BIZ-001-001-TP-001__v3.01__20260721.md`

### 3.2 候选文件内容模板

```markdown
# TP候选：<TP-ID>（v3.01首批抽取）

## 来源信息
- **需求**: 游戏道具商城系统
- **版本**: v3.01
- **模块**: <MODULE>
- **Epic**: <EPIC_ID>
- **Story**: <STORY_ID>
- **抽取日期**: YYYY-MM-DD

## TP 字段（原始值）

| 字段 | 值 |
|------|-----|
| tp_id | <TP_ID> |
| module | <MODULE> |
| story_id | <STORY_ID> |
| epic_id | <EPIC_ID> |
| obj_id | <OBJ_ID> |
| obj_name | <OBJ_NAME> |
| feature_point_ref | <FP_REF> |
| fp_name | <FP_NAME> |
| case_type | <CASE_TYPE> |
| test_point_type | <TP_TYPE> |
| priority | <PRIORITY> |
| s4_reference | <S4_REF> |
| is_assumed | <IS_ASSUMED> |

## 用例描述

<DESCRIPTION>

## 边界条件

<BOUNDARY>

## 审核意见（人工填写）

- [ ] 格式规范
- [ ] 字段完整
- [ ] 可作为子类模板

审核员签字：__________ 日期：__________
```

---

## 4. 审核机制

### 4.1 审核层级（v31 §8.2 两段制对齐）

| 段 | 动作 | 负责方 |
|---|---|---|
| 第 1 段 | 写候选文件 → `knowledge/public/test_point_library/_candidates/` | Agent（v33 Round 3）|
| 第 2 段 | 人工审核 → 通过/拒绝 → 入库 | 人工审核员（用户决策）|

### 4.2 审核标准

| 维度 | 检查项 |
|---|---|
| 格式规范 | 字段齐全、无截断 |
| 字段语义 | test_point_type / module / obj_id 与上游一致 |
| 可复用性 | 是否可作为同类 Story 的 TP 模板 |
| 无歧义 | description 是否清晰、可操作 |

### 4.3 审核决策

| 决策 | 动作 |
|---|---|
| **通过** | 复制到 `knowledge/public/test_point_library/<MODULE>/<Subclass>.md` |
| **拒绝** | 保留在 `_candidates/` 标记 `rejected: true` + 原因 |
| **修改后通过** | Agent 按意见修改 → 重写候选文件 |

---

## 5. 实施计划

### 5.1 v33 Round 2（本档）

| 动作 | 内容 |
|---|---|
| 起草抽取规则 | ✅ 本档 |
| 创建候选目录 | `knowledge/public/test_point_library/_candidates/` + README |
| 更新 VC5 决策档 | `v33_05_decision_FINAL.md` |

### 5.2 v33 Round 3（下一轮）

| 动作 | 内容 |
|---|---|
| 抽取首批 7 条 TP | 写 7 个候选文件到 `_candidates/` |
| 用户审核 | 人工审核 7 条（通过/拒绝/修改）|
| 入库（如通过）| 复制到正式 `test_point_library/<MODULE>/` 子类文件 |

---

## 6. 验证证据

| 来源 | 关键数据 |
|---|---|
| `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json` | 230 TP / 16 stories / 4 modules 实测 |
| `archive/v31_20260721_020714.bak/PLAN.md` §8.4 | 激活阈值 ≥ 10 条 |
| `v32/decision_v32_05_FINAL.md` §4.2 | 3 项必做：抽取规则 + 审核机制 + 首批入库 |
| `v32/SUMMARY.md` §2.1 | VC5 FAIL：候选目录 NOT EXISTS，抽取规则未起草 |

---

> **v33 TP 抽取规则起草落档** — 覆盖三轴筛选（模块 / type / Epic）+ 7 条候选清单 + 格式模板 + 审核机制 + Round 2/3 实施计划。
