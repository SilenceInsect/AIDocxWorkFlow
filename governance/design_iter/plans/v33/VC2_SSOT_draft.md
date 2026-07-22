# VC2 SSOT 修订提案 — .mdc §4.3 + v31 §2.5

> **VC**: VC2（.mdc L2 SSOT 修订）
> **Round**: 7
> **Date**: 2026-07-21
> **依据**: v31 §2.5 SCC 方法论 + v33 goal-loop 遗留项
> **提案状态**: 待用户决策

---

## 1. 问题：当前 SSOT 失配

### 1.1 症状

| 文件 | SCC 相关内容 | 状态 |
|------|-------------|------|
| `v31_方法论_草案.md` §2.5 | 完整 SCC 公式 + TP_TYPE_FACTOR + 软下限 | ✅ 草案已写 |
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` §2.5 | 同上引用 | ⚠️ 引用草案（未落地）|
| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 | **无 SCC 常量** | ❌ SSOT 缺失 |
| `governance/design_iter/plans/v31/v31_SCC.md` | 详细定义 | ✅ 存在但孤岛 |

### 1.2 根因

v31 §2.5 **从未进入 .mdc §4.3 SSOT**——SCC 公式存在于草案层，未进入约束正文。

后果：
- Agent 读 .mdc §4.3 **看不到** SCC 软下限
- `S5_MIN_TP_PER_STORY = ≥ 6` 与 SCC 公式并存，造成歧义
- v31_SCC.md 是孤岛文件，无人引用

---

## 2. 提案：修订 .mdc §4.3 + §4.3.2

### 2.1 修订范围

**文件**：`.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`

| 操作 | 内容 |
|------|------|
| **新增** §4.3.2 | 故事复杂度系数（SCC）SSOT 常量 + 统计公式 |
| **废除** | `S5_MIN_TP_PER_STORY = ≥ 6`（被 SCC 公式取代）|
| **新增** | `S5_SCC_SOFT_LOWER_FACTOR = 0.8` 到 §4.3 主表 |
| **新增** | `S5_TP_TYPE_FACTOR` 映射表到 §4.3 主表 |
| **更新** | v31_方法论_草案.md §2.5 引用路径（指向 SSOT）|

### 2.2 §4.3 新增常量

在 `§4.3 质量阈值常量` 主表末尾新增：

```
| `S5_SCC_SOFT_LOWER_FACTOR` | 0.8 | S5 每 Story TP 数软下限系数 | `软下限 = 理论TP数 × 0.8`（低于此值 → assumption_basis 说明缺少维度）|
| `S5_TP_TYPE_FACTOR_POSITIVE` | 1.5 | POSITIVE 类 TP 类型系数 | 理论 TP 数 = SCC × TP_TYPE_FACTOR |
| `S5_TP_TYPE_FACTOR_BOUNDARY` | 1.0 | BOUNDARY 类 TP 类型系数 | 同上 |
| `S5_TP_TYPE_FACTOR_NEGATIVE` | 1.0 | NEGATIVE 类 TP 类型系数 | 同上 |
| `S5_TP_TYPE_FACTOR_EXCEPTION` | 0.5 | EXCEPTION 类 TP 类型系数 | 同上 |
```

### 2.3 新增 §4.3.2 章节

在 `§4.3.1 异常路径覆盖率统计公式` 之后新增：

```markdown
### 4.3.2 故事复杂度系数（SCC）

> **v33 VC2 修订**：从 v31 §2.5 草案迁移至 SSOT，替代旧约束 `S5_MIN_TP_PER_STORY ≥ 6`。

**核心公式**：

```
SCC = |actors| × |states| × |timings| × |boundaries| × |exceptions|
理论 TP 数 = SCC × TP_TYPE_FACTOR
软下限 = 理论 TP 数 × 0.8
```

**TP_TYPE_FACTOR 映射**：

| test_point_type | 系数 | 说明 |
|----------------|------|------|
| POSITIVE | 1.5 | 正常路径权重最高 |
| BOUNDARY | 1.0 | 边界值 |
| NEGATIVE | 1.0 | 负面验证 |
| EXCEPTION | 0.5 | 异常路径 |

**维度说明**：

| 维度 | 来源 | 简单 | 复杂 |
|------|------|------|------|
| actors（行为主体）| `requirement_objects.json#objects[].scene` 中主体角色 | 1 | ≥ 3 |
| states（对象状态）| `requirement_objects.json#objects[].feature_points[].normal_flow` 中的状态节点 | 1~2 | ≥ 5 |
| timings（时序变体）| `backlog.json#stories[].acceptance_criteria[]` 步骤数 + 时序关键词（零/跨日/并发）| 1 | ≥ 3 |
| boundaries（边界条件）| `requirement_objects.json#objects[].feature_points[].input` 中数值范围 | 1~4 | ≥ 4 |
| exceptions（异常分支）| `requirement_objects.json#objects[].feature_points[].exception_flow[]` + S4 `business_flow.json#exception_tree_leaves[]` | 1 | ≥ 5 |

**使用规则**：

1. 对每个 Story，先估算 5 个维度的值
2. 计算 SCC = 5 维度连乘
3. 确定主 test_point_type，计算理论 TP 数
4. **若实际 TP 数 < 软下限** → `assumption_basis` 说明"缺少 {维度} 维度 TP"
5. 不设硬上限（复杂 Story 可以 SCC ≥ 100，对应 150+ 理论 TP）

**示例**（商城道具购买 Story）：

```
actors=2（玩家+系统）× states=5 × timings=3 × boundaries=4 × exceptions=5
= SCC=600
→ 理论 TP（POSITIVE）= 600 × 1.5 = 900
→ 软下限 = 900 × 0.8 = 720
```

**与其他阈值的关系**：

| 旧约束 | 状态 | 替代 |
|--------|------|------|
| `S5_MIN_TP_PER_STORY = ≥ 6` | **废除** | 被 SCC 软下限取代 |
| `≤ 50 TP/Story` 硬上限 | **废除**（v31 已废）| 无上限 |

---

## 3. 联动修订

### 3.1 v31_方法论_草案.md §2.5

更新第一段：

```diff
> **Round 2 新增**：替代"≤ 50 TP/Story"旧约束。
- > **详细定义**：见 `governance/design_iter/plans/v31/v31_SCC.md`
+ > **详细定义（SSOT）**：见 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3.2
+ > 本草案 §2.5 引用 SSOT，具体常量以 §4.3.2 为准。
```

### 3.2 STAGE_S5_TEST_POINTS.mdc

检查是否有重复引用，移除草案路径，改为引用 SSOT。

---

## 4. 解决 / 新增 / 遗留

| 类型 | 内容 |
|------|------|
| **解决** | SCC 公式从草案孤岛迁移至 .mdc §4.3.2 SSOT |
| **解决** | `S5_MIN_TP_PER_STORY ≥ 6` 歧义废除 |
| **新增** | 5 个 SCC 常量进入 §4.3 SSOT |
| **新增** | §4.3.2 完整 SCC 统计公式 |
| **遗留** | v31_SCC.md 孤岛文件：可考虑归档（待用户决策）|

---

## 5. 用户决策

| 决策点 | 选项 A（推荐）| 选项 B |
|--------|-------------|--------|
| §4.3.2 格式 | 完整迁移（SCC公式+维度+示例）| 极简版（只含常量+公式，维度细节留 v31_SCC.md）|
| v31_SCC.md | 归档到 `v31/archive/` | 保留（仍有参考价值）|
| `S5_MIN_TP_PER_STORY` | 明确废除（显式标记）| 保留但标注"已被SCC取代" |

---

## 6. 落档路径（若用户批准）

```
governance/design_iter/plans/v33/VC2_SSOT_draft.md  ← 本文件
        ↓ [用户批准]
.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc      ← §4.3 + §4.3.2 修订
governance/design_iter/plans/v31/v31_方法论_草案.md  ← §2.5 引用路径更新
```
