# VC3 L3 — UI TP 交叉 S3 prototype 方法论草案

> **VC**: VC3-L3（v33 Round 8）
> **来源**: v32 §3.1 v32_01 立项
> **Round**: 8
> **Date**: 2026-07-21
> **提案状态**: 待用户决策

---

## 1. 目标

UI TP 引用具体 prototype 控件 ID（S3 prototype.json），实现**机器可校验的 UI 控件级覆盖率**。

---

## 2. 问题诊断

### 2.1 v3.01 样本基线

| 指标 | 值 |
|---|---|
| S3 prototype 页面数 | 11 |
| S3 prototype ui_nodes 总数 | **73 个** |
| 含 `ui_node_refs` 字段的 UI TP | **0 个** |
| ui_node_coverage | **0%**（无引用）|

### 2.2 根因

- S5 TP 字段契约**无 `ui_node_refs` 字段**
- S5 生成时无法引用 `prototype.json#pages[].ui_nodes[].id`
- S7 无法机器校验"UI TP 是否覆盖了 prototype 的所有控件"

---

## 3. 提案：S5 TP 字段 + S7 覆盖率扩展

### 3.1 S5 test_points.json 新增字段

**字段名**: `ui_node_refs`

**位置**: 每个 UI 模块 TP 的 `scenario_test_points[]` 对象内

**类型**: `string[]`（数组，引用 prototype.ui_nodes[].id）

**示例**:

```json
{
  "tp_id": "UI-001-001-TP-001",
  "module": "UI",
  "test_point_type": "POSITIVE",
  "description": "商城首页加载完成，验证热门道具展示",
  "ui_node_refs": [
    "page_001_node_hot_item_list",
    "page_001_node_search_box",
    "page_001_node_category_nav"
  ]
}
```

### 3.2 S5 字段契约新增

在 `STAGE_S5_TEST_POINTS.mdc` §TP 字段契约中新增：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ui_node_refs` | `string[]` | UI TP 必填，BIZ/LOG/LINK TP 不适用 | 引用 `prototype.json#pages[].ui_nodes[].id` |

### 3.3 S7 新增覆盖率项

**覆盖率公式**:

```
ui_node_coverage = len(TP.ui_node_refs ∪ prototype.ui_nodes) / prototype.ui_nodes 总数
```

**阈值**: 1.0（100%，未覆盖控件需 `skip_reason`）

**示例**:

| 指标 | 值 |
|---|---|
| prototype.ui_nodes 总数 | 73 |
| TP.ui_node_refs 并集 | 12 |
| ui_node_coverage | 12/73 = 16.4% |

**未覆盖节点处理**: 标注 `covered: false` + `skip_reason`（同 §4.3.1 异常路径规则）

### 3.4 S6 TC steps 间接引用

S6 衍生 TC 时，`steps[].action` 可引用 `ui_node_refs` 中的控件 ID 作为操作目标。

```
{
  "steps": [
    {"action": "点击 [page_001_node_hot_item_list] 热门道具第1个卡片"},
    {"action": "验证 [page_001_node_price_label] 显示价格"}
  ]
}
```

---

## 4. 影响范围

| 文件 | 改动 |
|---|---|
| `STAGE_S5_TEST_POINTS.mdc` §字段契约 | + `ui_node_refs` 字段定义 |
| `STAGE_S6_TEST_CASES.mdc` §steps.action | + 控件 ID 引用说明 |
| `STAGE_S7_REVIEW.mdc` §覆盖率 | + `ui_node_coverage` 公式 |
| `DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 | + `S5_UI_NODE_COVERAGE = 1.0` 常量 |

---

## 5. 解决 / 新增 / 遗留

| 类型 | 内容 |
|------|------|
| **解决** | UI TP 无控件引用的根因（S5 字段缺失）|
| **新增** | `ui_node_refs` 字段 + `ui_node_coverage` 覆盖率 |
| **新增** | prototype.ui_nodes[] 需稳定 ID（提案纳入风险）|
| **遗留** | 存量 v3.01 样本补填 ui_node_refs（需 S5 re-run）|

---

## 6. v3.01 基线重算

提案后重算 v3.01 预期值：

| 指标 | 现状 | 提案后目标 |
|---|---|---|
| ui_node_refs 字段存在 | 0/230 | UI TP 全部有 |
| ui_node_coverage | 0% | ≥ 100%（skip_reason 兜底）|

---

## 7. 用户决策

| 决策点 | 选项 A（推荐）| 选项 B |
|--------|-------------|--------|
| ui_node_refs 必填性 | **UI TP 必填**（强约束）| UI TP 建议填（COULD）|
| 存量样本 | **无需 re-run**（新需求生效）| 要求 v3.01 补填 |
| 生效时机 | **立即生效**（新生成 TP）| 等所有存量补完后生效 |
