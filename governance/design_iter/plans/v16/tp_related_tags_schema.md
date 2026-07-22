# v16 T5 — TP related_tags 字段 Schema 定义

> **版本**: v16 T5（2026-07-17）
> **来源**: `governance/design_iter/plans/v16/PLAN.md` §2.6 + `详细执行方案.md` T5
> **核心变更**: TP JSON 新增 `related_tags` 数组 + 双轨覆盖率统计脚本
> **SSOT**: 本文件是 TP Schema 扩展的唯一权威定义；SKILL.md / REVIEW.mdc 通过引用同步

---

## §0 拍板依据（C3 解决）

- **保留 `module`**（不引入 `primary_module`，避免字段重复）
- **新增 `related_tags`**：数组，元素为模块名（CONFIG / UI / BIZ / AUX / LINK / SPECIAL / LOG / HINT）
- **不新增 `verification_points`**（简化版：related_tags 直接承担跨模块关联职责）

---

## §1 TP JSON Schema 变更

### 完整字段结构（JSON schema）

```json
{
  "tp_id": "TP-BIZ-001-001-01",
  "module": "BIZ",
  "related_tags": ["LOG", "CONFIG"],
  "description": "string",
  "test_point_type": "enum EP_VALID | EP_INVALID | BOUNDARY_MIN | ...",
  "test_type_subclass": "string（如 BIZ.H_payment）",
  "precondition": "string",
  "test_input": "string",
  "expected_result": "string",
  "s4_reference": "string",
  "boundary": "string | null",
  "is_assumed": "boolean",
  "applies_rule": "string",
  "assumption_reason": "string | null",
  "feature_point_ref": "string | null",
  "priority": "enum P0 | P1 | P2 | null",
  "tags": ["string"]   // 已有，可选
}
```

### 字段说明

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `tp_id` | string | ✅ | TP 唯一 ID |
| `module` | string | ✅ | 主模块（8 模块之一） |
| **`related_tags`** | **string[]** | **✅** | **v16 T5 新增** — 关联模块数组 |
| `description` | string | ✅ | TP 描述 |
| `test_point_type` | string | ✅ | 测试类型枚举 |
| `test_type_subclass` | string | ✅ | 细分枚举 |
| `precondition` | string | ✅ | 前置条件 |
| `test_input` | string | ✅ | 测试输入 |
| `expected_result` | string | ✅ | 预期结果 |
| `s4_reference` | string | ✅ | S4 节点引用 |
| `boundary` | string/null | ✅ | 边界值 |
| `is_assumed` | boolean | ✅ | 是否假设 |
| `applies_rule` | string | ✅ | 判定规则 |
| `assumption_reason` | string/null | ⭓ | is_assumed=true 时建议填 |
| `feature_point_ref` | string/null | ⭓ | FP 引用（v11+）|
| `priority` | string/null | ⭑ | 优先级（可选）|
| `tags` | string[] | ⭑ | 标签（已有，可选）|

> ⭕ = SHOULD（建议填）/ ⭑ = COULD（可选）

---

## §2 `related_tags` 枚举与生成规则

### 2.1 枚举值（8 模块）

```
CONFIG / UI / BIZ / AUX / LINK / SPECIAL / LOG / HINT
```

> 枚举集合与 `module` 字段相同（同一 8 模块体系）。

### 2.2 生成规则

**主模块判定**：
- TP 的主模块 = `module` 字段（由 §1.2 checklist 判定）

**关联模块扫描**（生成 `related_tags` 时）：

每个 TP 生成前，必须扫描其业务场景是否涉及**其他模块的验证点**：

| 场景 | 添加 related_tags |
|------|-----------------|
| BIZ 业务流程含**日志验证** | 添加 `LOG` |
| BIZ 业务流程含**配置读取** | 添加 `CONFIG` |
| BIZ 业务流程含**第三方调用** | 添加 `LINK` |
| BIZ 业务流程含**异常/对抗** | 添加 `SPECIAL` |
| UI 业务流程含**服务端拉取数据** | 添加 `BIZ` |
| UI 业务流程含**临时提示** | 添加 `HINT` |
| CONFIG 含**解析/热更** | 添加 `BIZ`（业务层影响）|
| 任意模块含**跨服/跨端同步** | 添加 `LINK` |

**硬约束**：

1. `module` **必须**出现在 `related_tags` 中（自己关联自己）
2. `related_tags` 最多 **3 个**元素（防止标签爆炸）
3. `related_tags` 元素**互异**（去重）

**正确示例**：

```json
{
  "tp_id": "TP-BIZ-P001-001-01",
  "module": "BIZ",
  "related_tags": ["BIZ", "LOG", "CONFIG"],
  "description": "购买后货币扣减"
}
```

**错误示例**（违反约束 1）：

```json
{
  "module": "BIZ",
  "related_tags": ["LOG", "CONFIG"]   // ❌ BIZ 不在数组中
}
```

**错误示例**（违反约束 2）：

```json
{
  "module": "BIZ",
  "related_tags": ["BIZ", "LOG", "CONFIG", "LINK", "SPECIAL"]   // ❌ 超过 3 个
}
```

---

## §3 双轨覆盖率统计

### 3.1 双轨定义

| 轨道 | 统计口径 | 计算公式 |
|------|---------|---------|
| **主模块轨道** | 按 `module` 字段分组 | `module_cov[MOD] = TP数(module=MOD) / OBJ数(module=MOD)` |
| **维度轨道** | 按 `related_tags` 展开 | `dim_cov[MOD] = 有TP含MOD的OBJ数 / OBJ总数(module=MOD)` |

### 3.2 差异告警

双轨差异 > 10% 时触发 `WEAK_OVERLAP` 警告：

```
WEAK_OVERLAP: module=BIZ coverage=0.85, dimension=0.92, diff=0.07 (≤0.10, no warning)
WEAK_OVERLAP: module=BIZ coverage=0.70, dimension=0.92, diff=0.22 (>0.10, WARNING)
```

### 3.3 统计脚本

详见 `ai_workflow/coverage_dual_track.py`（独立脚本，导入使用）。

---

## §4 兼容性

### 4.1 旧 TP 升级

旧 TP（无 `related_tags` 字段）视为默认 `related_tags = []`：

```python
related_tags = tp.get("related_tags", [])  # 旧 TP → []
```

脚本校验时不因 `related_tags = []` 报错。

### 4.2 字段迁移

已有 `tags` 字段（可选）与 `related_tags`（必须）共存：

- `tags` = 自由标签（检索用）
- `related_tags` = 跨模块关联（覆盖率统计用）

---

## §5 版本与维护

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-17 | v16 T5 首次落地（related_tags + 双轨覆盖率 + 兼容性）|

**修改原则**：改 `related_tags` 枚举必须先改本文件，再同步 SKILL.md + REVIEW.mdc。
