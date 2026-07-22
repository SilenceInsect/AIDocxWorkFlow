# TP 候选区 — _candidates

> **性质**：公共知识库候选区（AGENTS.md Git 分类铁律允许的中间态）
> **创建日期**：2026-07-21（v33 Round 2）
> **依据**：DT-V33-005-FINAL
> **Round 4 质量修订**：2026-07-21（description 占位符 → 回溯 S2 AC 补充可执行描述）

---

## 用途

`test_point_library/` 的候选 TP 暂存区。
Agent 不得直接入库（公共知识库铁律），必须先产候选 → 人工审核 → 入库。

## 质量标准（Round 4 确立）

| 维度 | 要求 | 说明 |
|---|---|---|
| description | **具体可执行** | 含操作步骤 + 数值边界 + 可判断预期结果 |
| 来源追溯 | **S2 锚定** | 预期结果必须来自 `backlog.json` acceptance_criteria |
| 类型一致性 | **S5↔S2 一致** | test_point_type 需与 S2 normal_flow/exception_flow 对应 |
| 激活阈值 | **≥ 10 条** | 严格口径：必须可执行描述才算入阈值 |

## 候选文件格式

```
<TP-ID>__v3.01__YYYYMMDD.md
```

## 审核流程

1. Agent 从 `workflow_assets/` 抽取候选 TP → 写入本目录
2. **Round 4 新增**：Agent 必须回溯 S2 补充 description（不可用模板占位符）
3. 人工审核（通过/拒绝/修改）
4. 通过 → 复制到 `test_point_library/<MODULE>/<Subclass>.md`
5. 拒绝 → 标记 `rejected: true` + 原因，保留在本目录

## 首批候选（v33 Round 2/3/4/5）

| 序号 | 文件 | 模块 | 类型 | 修复状态 |
|---|---|---|---|---|
| 1 | `BIZ-001-001-TP-001__v3.01__20260721.md` | BIZ | POSITIVE | ✅ 修复版（有1秒到账数值）|
| 2 | `BIZ-001-001-TP-002__v3.01__20260721.md` | BIZ | EXCEPTION | ✅ 修复版（余额不足→不扣款）|
| 3 | `UI-001-001-TP-001__v3.01__20260721.md` | UI | POSITIVE | ✅ 修复版（有3秒/10个/降序数值）|
| 4 | `UI-001-001-TP-002__v3.01__20260721.md` | UI | EXCEPTION | ✅ 修复版（网络异常→重试按钮）|
| 5 | `UI-002-001-TP-007__v3.01__20260721.md` | LOG | POSITIVE | ✅ 修复版（有4字段日志记录）|
| 6 | `BIZ-002-001-TP-001__v3.01__20260721.md` | BIZ | POSITIVE | ✅ 修复版（有30天/6字段边界）|
| 7 | `BIZ-001-002-TP-001__v3.01__20260721.md` | LINK | POSITIVE | ✅ 修复版（有1秒/5秒时效数值）|
| 8 | `BIZ-003-001-TP-001__v3.01__20260721.md` | BIZ | POSITIVE | ✅ Round5补充（新Epic BIZ-003覆盖，VIP1折扣95折）|
| 9 | `UI-001-001-TP-014__v3.01__20260721.md` | UI | BOUNDARY | ✅ Round5补充（库首个BOUNDARY，价格=null边界）|
| 10 | `BIZ-004-001-TP-001__v3.01__20260721.md` | BIZ | POSITIVE | ✅ Round5补充（新Epic BIZ-004覆盖，满减100-10元）|

**覆盖**：4 模块（BIZ/UI/LOG/LINK）+ **6 Epic**（BIZ-001/BIZ-002/BIZ-003/BIZ-004/UI-001/UI-002）+ **6 type**（POSITIVE×5/EXCEPTION×2/BOUNDARY×1）

## 激活进度

| 指标 | 值 | 说明 |
|---|---|---|
| 当前候选数 | **10 条** | ✅ 达到阈值 |
| 严格激活阈值 | ≥ 10 条 | ✅ **已激活** |
| 质量债务 | ✅ 已清零 | 10 条全部有具体 AC |
| 激活日期 | 2026-07-21（Round 5）| |

---

> 本目录由 v33 goal-loop 创建，依据 DT-V33-005-FINAL。
> 未经人工审核，任何 TP 不得直接移入 `test_point_library/<MODULE>/` 正式目录。
