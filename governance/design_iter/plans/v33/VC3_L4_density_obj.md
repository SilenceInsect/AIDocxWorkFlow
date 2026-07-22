# VC3 L4 — density-OBJ 维度（per-OBJ 4 类型齐全率）

> **VC**: VC3-L4（v33 Round 8）
> **来源**: v32 §3.2 v32_02 立项
> **Round**: 8
> **Date**: 2026-07-21
> **提案状态**: 待用户决策

---

## 1. 目标

每 OBJ 的 4 类型 TP（POSITIVE / BOUNDARY / NEGATIVE / EXCEPTION）齐全率门禁，弥补现有 OBJ 覆盖率只看"有没有"、不看"密度够不够"的问题。

---

## 2. 问题诊断

### 2.1 v3.01 样本基线

| 指标 | 值 |
|---|---|
| 有 TP 的 OBJ 总数 | 36 |
| 4 类型齐全的 OBJ 数 | **8 个（22.2%）** |
| 缺 NEGATIVE 类型的 OBJ | **28 个（77.8%）** |
| 缺 BOUNDARY 类型的 OBJ | **12 个（33.3%）** |
| 各类型分布 | POSITIVE(99) / EXCEPTION(89) / BOUNDARY(25) / **NEGATIVE(17)** |

### 2.2 根因

- v31 OBJ 覆盖率只统计"OBJ 有没有 TP"，不统计"4 类型是否齐全"
- NEGATIVE 类（负面验证：验证错误路径/无效输入）被系统性忽视
- 22.2% density 说明大多数 OBJ 只有正面路径和异常路径，缺乏对错误输入的测试

### 2.3 典型缺陷 OBJ

| OBJ | 已有类型 | 缺失类型 |
|-----|---------|---------|
| BIZ-001-001-OBJ-03 | POSITIVE + EXCEPTION | **BOUNDARY + NEGATIVE** |
| UI-001-001-OBJ-01 | POSITIVE + EXCEPTION | **BOUNDARY + NEGATIVE** |
| UI-002-001-OBJ-02 | POSITIVE + EXCEPTION | **BOUNDARY + NEGATIVE** |
| BIZ-004-001-OBJ-01 | POSITIVE + BOUNDARY + EXCEPTION | **NEGATIVE** |

---

## 3. 提案：新增 density 维度

### 3.1 覆盖率公式

**v31 OBJ 覆盖率（集合维度）**：
```
OBJ 覆盖率 = 有 TP 的 OBJ 数 / OBJ 总数
```

**v32 density-OBJ 覆盖率（密度维度）**：
```
density = len({ OBJ : |{ TP.test_point_type for TP in OBJ } ∩ {POSITIVE, BOUNDARY, NEGATIVE, EXCEPTION}| == 4 }) / OBJ 总数
```

**含义**: OBJ 的 4 类型齐全率 = "4 类型都有至少 1 个 TP"的 OBJ 数 / OBJ 总数

### 3.2 阈值

`density = 1.0`（与 v31 OBJ 覆盖率门槛一致）

**未达标处理**（同 §4.3.1 异常路径规则）：

| skip_reason | 适用条件 |
|---|---|
| `low_risk` | 业务评估该类型为低风险（如纯展示类 OBJ 缺 NEGATIVE）|
| `out_of_scope` | 明确不在本期需求范围 |
| `deprecated` | 该类型路径已被废弃 |

### 3.3 §4.3 新增常量

```
| `S5_DENSITY_OBJ_COVERAGE` | 1.0 | S5 per-OBJ 4类型齐全率 | `density = 4类型齐全OBJ数 / OBJ总数` |
```

### 3.4 §4.3.3 新增章节

在 `§4.3.2` 后新增：

```markdown
### 4.3.3 per-OBJ 4类型齐全率（density-OBJ）

> **v33 VC3-L4 新增**：补充 v31 OBJ 覆盖率（集合维度）的密度维度。

**覆盖对象**：每 OBJ 的 4 类型 TP（POSITIVE / BOUNDARY / NEGATIVE / EXCEPTION）

**4 类型说明**：

| 类型 | 含义 | 典型场景 |
|------|------|---------|
| POSITIVE | 正常路径验证 | 余额充足时购买成功 |
| BOUNDARY | 边界值验证 | 数量=99（最大购买数）|
| NEGATIVE | 错误/无效输入验证 | 输入非法道具ID |
| EXCEPTION | 异常分支验证 | 余额不足时订单失败 |

**示例**（v3.01 样本）：

| 指标 | 值 |
|---|---|
| OBJ 总数 | 36 |
| 4 类型齐全 OBJ | 8 |
| density | 8/36 = 22.2% |
| 缺 NEGATIVE 的 OBJ | 28 |
| 缺 BOUNDARY 的 OBJ | 12 |

**阈值**: `S5_DENSITY_OBJ_COVERAGE = 1.0`
**未达标**: `skip_reason` 显式标注

**与其他覆盖率的关系**：

| 维度 | 公式 | v3.01 基线 |
|------|------|----------|
| OBJ 覆盖率（集合）| 有 TP 的 OBJ / OBJ 总数 | 36/36 = 100% |
| **density-OBJ（密度）**| 4类型齐全 OBJ / OBJ 总数 | 8/36 = 22.2% |
```

### 3.5 S7 新增审查项

S7 审查员 B 校验 `density-OBJ` 覆盖率，报告缺失类型清单。

---

## 4. 影响范围

| 文件 | 改动 |
|---|---|
| `DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 | + `S5_DENSITY_OBJ_COVERAGE` 常量 |
| `DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3.3 | + density-OBJ 章节（新增）|
| `STAGE_S7_REVIEW.mdc` §审查项 | + density-OBJ 审查说明 |

---

## 5. 解决 / 新增 / 遗留

| 类型 | 内容 |
|------|------|
| **解决** | OBJ 覆盖率"有 TP 无密度"的根因 |
| **新增** | `density-OBJ` 新覆盖率维度 |
| **新增** | NEGATIVE 类（错误输入验证）的价值说明 |
| **遗留** | 存量样本补填缺失类型（需 S5 re-run 或 S8 自迭代）|

---

## 6. v3.01 补填缺口估算

| 类型 | 缺失 OBJ 数 | 估算补填 TP 数 |
|------|-----------|-------------|
| 缺 NEGATIVE | 28 OBJ | 28~56 条 |
| 缺 BOUNDARY | 12 OBJ | 12~24 条 |
| 合计 | — | **40~80 条** |

---

## 7. 用户决策

| 决策点 | 选项 A（推荐）| 选项 B |
|--------|-------------|--------|
| density 阈值 | **1.0（100%，严格）** | 0.8（允许个别 skip）|
| skip_reason 认定 | **必须人工审核**（S7 审查员 B 逐条确认）| LLM 自动判断 |
| 存量样本 | **不要求 re-run**（新需求生效）| v3.01 必须补填 |
