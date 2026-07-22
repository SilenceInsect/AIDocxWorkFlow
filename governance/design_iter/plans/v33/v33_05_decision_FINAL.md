# DT-V33-005-FINAL — v32_05 TP 库首批回灌最终决策

> **决策 ID**: DT-V33-005-FINAL
> **触发**: v33 Round 2 用户复核 DT-V32-004（选项 A）+ v33 Round 2 TP 抽取规则起草
> **依据**: `v33/v33_05_extraction_rule.md` + DT-V32-004 §1
> **日期**: 2026-07-21
> **状态**: ✅ **最终决策（用户已确认接受）**

---

## 1. 决策状态

| 条件 | 状态 |
|---|---|
| 用户复核 DT-V32-004（选项 A）| ✅ 接受（AskQuestion Round 2）|
| TP 抽取规则起草 | ✅ 本 Round 2 落档（`v33_05_extraction_rule.md`）|
| 候选目录创建 | ⏳ Round 2/3 执行 |
| 首批 TP 抽取 | ⏳ Round 3 执行 |
| 用户审核入库 | ⏳ Round 3/4 执行 |

---

## 2. 选定方案

**选项 A 启动（与 DT-V32-004 一致）**：

### 2.1 三项必做

| 项 | 内容 | 状态 |
|---|---|---|
| **TP 抽取规则** | v3.01 230 TP 按"模块 / type / Epic"三轴筛选 | ✅ 本 Round 2 起草 |
| **人工审核机制** | 人工审核 7 条候选（通过/拒绝/修改后通过）| ⏳ Round 3/4 |
| **首批 TP 入库** | 7 条候选通过后写入正式 `test_point_library/<MODULE>/` 子类文件 | ⏳ Round 4 |

### 2.2 首批抽取清单（7 条）

| 序号 | tp_id | 模块 | test_point_type | Epic |
|---|---|---|---|---|
| 1 | `BIZ-001-001-TP-001` | BIZ | POSITIVE | BIZ-001 |
| 2 | `BIZ-001-001-TP-002` | BIZ | BOUNDARY | BIZ-001 |
| 3 | `UI-001-001-TP-001` | UI | POSITIVE | UI-001 |
| 4 | `UI-001-001-TP-002` | UI | NEGATIVE | UI-001 |
| 5 | `LOG-001-001-TP-001` | LOG | POSITIVE | LOG-001 |
| 6 | `BIZ-002-001-TP-001` | BIZ | ERROR | BIZ-002 |
| 7 | `LINK-001-001-TP-001` | LINK | POSITIVE | LINK-001 |

**覆盖**：4 模块（BIZ/UI/LOG/LINK）+ 5 Epic（BIZ-001/UI-001/LOG-001/BIZ-002/LINK-001）+ 5 type（POSITIVE/BOUNDARY/NEGATIVE/ERROR/POSITIVE）

### 2.3 激活阈值说明

| 指标 | 值 | 说明 |
|---|---|---|
| 首批抽取 | 7 条 | 种子性质 |
| v31 §8.4 激活阈值 | ≥ 10 条 | 未达到 |
| 后续补充 | Round 4+ 补充至 ≥ 10 条 | 作为 v33 Round 4 执行项 |

→ 首批 7 条为"种子启动"，激活阈值通过后续补充达到。

---

## 3. 实施路径

### Round 2（本 Round）

| 动作 | 产出 |
|---|---|
| TP 抽取规则起草 | `v33_05_extraction_rule.md` ✅ |
| 创建候选目录 | `knowledge/public/test_point_library/_candidates/` |
| 更新 VC5 决策档 | `v33_05_decision_FINAL.md` ✅ |

### Round 3（下一轮）

| 动作 | 产出 |
|---|---|
| 抽取 7 条候选 TP | 7 个候选文件写入 `_candidates/` |
| 用户审核 7 条候选 | 人工审核（通过/拒绝/修改）|
| 拒绝条重抽 | 如有拒绝，从剩余 223 条补充 |

### Round 4+

| 动作 | 产出 |
|---|---|
| 补充至 ≥ 10 条 | 满足 v31 §8.4 激活阈值 |
| 正式入库 | 复制到 `test_point_library/<MODULE>/<Subclass>.md` |

---

## 4. AGENTS.md Git 分类铁律约束

> "`module_templates/` 属公共知识库，新增 / 修改**不得由 Agent 直接入库**——先产候选，人工审核"

本档严格遵守：
- ✅ 仅写 `_candidates/`（候选目录）
- ✅ 不直接写入 `test_point_library/<MODULE>/` 正式子类文件
- ✅ 人工审核后才可入库

---

## 5. 影响范围

| 资产 | 影响 | 时间 |
|---|---|---|
| `knowledge/public/test_point_library/_candidates/` | ⚠️ Round 2 新建 | 本 Round |
| `knowledge/public/test_point_library/<MODULE>/<Subclass>.md` | ⚠️ Round 4 入库 | Round 4+ |
| `v33_05_extraction_rule.md` | ✅ 本 Round 2 起草 | 本 Round |
| v3.01 S5 test_points.json | ❌ 不动（仅读取）| — |

---

## 6. 验证证据

| 来源 | 关键数据 |
|---|---|
| `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json` | 230 TP / 16 stories / 4 modules 实测 |
| `v33/v33_05_extraction_rule.md` | 三轴筛选 + 7 条候选清单 + 格式模板 |
| `v32/decision_v32_05_FINAL.md` §4.2 | 3 项必做：抽取规则 + 审核机制 + 首批入库 |
| AskQuestion Round 2 用户回应 | DT-V32-004 选项 A 接受 ✅ |

---

## 7. 落档协议（DNA §9.5）

- 本档是 v33 Round 2 **VC5 决策档**
- 与 DT-V32-004 保持一致（用户已确认接受选项 A）
- Round 3 执行抽取 7 条候选 TP 到 `_candidates/`

---

> **DT-V33-005-FINAL 决策落档** — 选项 A 启动（三项必做 + 首批 7 条候选 + 激活阈值后续补充）；用户已确认接受。
