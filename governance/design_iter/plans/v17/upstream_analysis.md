# 上游阶段字段溯源分析报告

> **分析日期**：2026-07-20
> **分析范围**：S2 requirement_objects.json → S5 test_points.json → S6 test_cases.json
> **分析目的**：为 goal-loop 提供整改基线

---

## 一、S2 阶段产物分析

### 1.1 S2 产出结构

| 字段 | 状态 | 说明 |
|------|------|------|
| `objects[].id` | ✅ 完整 | OBJ 唯一标识符（16 个 OBJ） |
| `objects[].obj_name` | ✅ 完整 | OBJ 名称（例："商城首页道具列表"） |
| `objects[].belong_module` | ✅ 完整 | 归属模块（UI/BIZ 等） |
| `objects[].feature_points[].id` | ✅ 完整 | FP 唯一标识符（49 个 FP） |
| `objects[].feature_points[].fp_desc` | ✅ 完整 | FP 功能描述（例："首页按销量展示前10个热门道具"） |

### 1.2 S2 fp_desc 字段示例

| OBJ | FP ID | fp_desc |
|-----|-------|---------|
| 商城首页道具列表 | UI-ITEM-MALL-01-001-OBJ-01-FP-1 | "首页按销量展示前10个热门道具" |
| 道具搜索功能 | UI-ITEM-MALL-01-001-OBJ-02-FP-1 | "支持道具名称模糊搜索" |
| 游戏币购买流程 | BIZ-PURCHASE-01-001-OBJ-01-FP-1 | "游戏币余额校验" |

---

## 二、S5 阶段产物分析（test_points.json）

### 2.1 S5 产出统计

| 指标 | 值 | 规范要求 | 差距 |
|------|-----|---------|------|
| TP 总数 | 87 | ≥ OBJ×6 | ✅ 达标 |
| OBJ 覆盖率 | 16/16 | 100% | ✅ 达标 |
| FP 覆盖率 | 49/49 | 100% | ✅ 达标 |

### 2.2 字段溯源问题清单

#### 问题 1：TP 缺少 `obj_name` 字段（严重）

| 检查项 | 规范要求 | 实际情况 |
|--------|---------|---------|
| `obj_name` 字段存在 | S5 SKILL.md §一 规则1：必须包含 | ❌ **缺失** |
| `obj_name` 值来源 | S2 `requirement_objects[].obj_name` | 未填写 |
| 字段匹配率 | 100% | 0% |

**根因**：`test_points.json` 中每个 TP 只含 `obj_id`（如 `"UI-ITEM-MALL-01-001-OBJ-01"`），缺少人类可读的 `obj_name` 字段（如 `"商城首页道具列表"`）。

**影响**：S6 无法直接通过 `obj_name` 字段验证继承关系，必须回溯 S2 查询。

#### 问题 2：TP 缺少 `fp_name` 字段（中等）

| 检查项 | 规范要求 | 实际情况 |
|--------|---------|---------|
| `fp_name` 字段存在 | S5 SKILL.md §一 规则1：必须包含 | ❌ **缺失** |
| `fp_name` 命名规则 | 含动词 + ≤ 20 字符 + 不与 S2 fp_desc 重复 | 未填写 |

**根因**：S5 TP 只有 `feature_point_ref`（结构化 ID），缺少 LLM 自创的 `fp_name` 中性功能名。

**示例对比**：

```json
// 规范期望
{
  "tp_id": "UI-TP-001",
  "obj_name": "商城首页道具列表",
  "fp_name": "首页销量排序展示",  // LLM 自创中性名
  "feature_point_ref": "UI-ITEM-MALL-01-001-OBJ-01-FP-1"
}

// 实际产出
{
  "tp_id": "UI-TP-001",
  "obj_id": "UI-ITEM-MALL-01-001-OBJ-01",
  "feature_point_ref": "UI-ITEM-MALL-01-001-OBJ-01-FP-1"
  // 缺少 obj_name 和 fp_name
}
```

#### 问题 3：TP 缺少 `preconditions` 字段（严重）

| 检查项 | 规范要求 | 实际情况 |
|--------|---------|---------|
| `preconditions` 字段存在 | S5 SKILL.md §七：必须包含 | ❌ **缺失** |
| `preconditions` 非空 | 至少 1 条 | 空数组或缺失 |
| 禁止空占位 "无" | 业务确实无前置条件才用 | 未检查 |

**根因**：S5 产出没有包含前置条件字段，导致 S6 步骤碎裂（无法继承 TP 的前置条件）。

**规范要求示例**：

```json
{
  "tp_id": "UI-TP-001",
  "preconditions": [
    "玩家已登录游戏客户端",
    "商城已配置道具数据",
    "道具按销量有排序"
  ]
}
```

#### 问题 4：TP 缺少 `tc_generation_hints` 字段（轻微）

| 检查项 | 规范要求 | 实际情况 |
|--------|---------|---------|
| `tc_generation_hints` 字段 | S5 SKILL.md §七.2：可选但推荐 | ❌ **缺失** |
| `scenario_variants` | 每个 variant 含 `expected_results` | 未填写 |

**根因**：缺少对 S6 TC 拓宽的指导信息。

### 2.3 S5 字段完整性统计

| 字段 | 规范要求 | 实际存在 | 缺失率 |
|------|---------|---------|--------|
| `tp_id` | 必须 | ✅ | 0% |
| `module` | 必须 | ✅ | 0% |
| `test_point_type` | 必须 | ✅ | 0% |
| `feature_point_ref` | 必须 | ✅ | 0% |
| `obj_id` | 必须 | ✅ | 0% |
| `s4_reference` | 必须 | ✅ | 0% |
| `obj_name` | 必须 | ❌ | **100%** |
| `fp_name` | 必须 | ❌ | **100%** |
| `preconditions` | 必须 | ❌ | **100%** |
| `tc_generation_hints` | 推荐 | ❌ | 100% |

---

## 三、S6 阶段产物分析（test_cases.json）

### 3.1 S6 产出统计

| 指标 | 值 | 规范要求 | 差距 |
|------|-----|---------|------|
| TC 总数 | 331+ | 按 S5 TP 拓宽 | - |
| `用例描述` 继承 | ✅ | 必须 = S2 obj_name | 正确 |
| `feature_point_ref` 继承 | ✅ | 必须 = S5 TP.feature_point_ref | 正确 |

### 3.2 字段溯源问题清单

#### 问题 1：TC 缺少 `obj_name` 字段（严重）

| 检查项 | 规范要求 | 实际情况 |
|--------|---------|---------|
| `obj_name` 字段存在 | S6 SKILL.md §一 规则1：必须包含 | ❌ **缺失** |
| `obj_name` 值来源 | 从 S5 TP.obj_name 继承 | 未填写 |
| 字段匹配率 | 100% | 0% |

**根因**：S5 TP 本身没有 `obj_name`，S6 无法继承。

**示例对比**：

```json
// 规范期望
{
  "case_id": "UI-TC-001",
  "obj_name": "商城首页道具列表",  // 继承自 TP
  "feature_point_ref": "UI-ITEM-MALL-01-001-OBJ-01-FP-1",
  "用例描述": "商城首页道具列表按销量降序展示"
}

// 实际产出
{
  "case_id": "UI-TC-001",
  "用例描述": "商城首页道具列表按销量降序展示",  // 只有这个
  "obj_id": "UI-ITEM-MALL-01-001-OBJ-01",
  "feature_point_ref": "UI-ITEM-MALL-01-001-OBJ-01-FP-1"
  // 缺少显式 obj_name
}
```

#### 问题 2：TC 缺少 `assertion` 字段（严重）

| 检查项 | 规范要求 | 实际情况 |
|--------|---------|---------|
| `assertion` 字段存在 | S6 SKILL.md Round 15 F-E：必须 ≥ 1 | ❌ **缺失** |
| `assertion[].assertion_type` | 必须（numeric/string_contains/enum_match 等） | 未填写 |

**根因**：S6 产出只有 `预期结果` 文本字段，缺少机器可读的 `assertion` 数组。

**规范要求示例**：

```json
{
  "case_id": "UI-TC-001",
  "assertion": [
    {
      "assertion_type": "enum_match",
      "assertion_target": "item_order",
      "expected_value": "DESC"
    },
    {
      "assertion_type": "numeric",
      "assertion_target": "item_count",
      "operator": "<=",
      "expected_value": 10
    }
  ]
}
```

#### 问题 3：TC 缺少 `preconditions` 字段（轻微）

| 检查项 | 规范要求 | 实际情况 |
|--------|---------|---------|
| `preconditions` 字段 | S6 SKILL.md §12.4：必须继承 TP.preconditions | ❌ **缺失** |

**根因**：S5 TP 没有 `preconditions`，S6 只能自己填写 `前置条件`。

### 3.3 S6 字段完整性统计

| 字段 | 规范要求 | 实际存在 | 缺失率 |
|------|---------|---------|--------|
| `case_id` | 必须 | ✅ | 0% |
| `module` | 必须 | ✅ | 0% |
| `用例描述` | 必须 | ✅ | 0% |
| `功能描述` | 必须 | ✅ | 0% |
| `前置条件` | 必须 | ✅ | 0% |
| `操作步骤` | 必须 | ✅ | 0% |
| `预期结果` | 必须 | ✅ | 0% |
| `obj_id` | 必须 | ✅ | 0% |
| `feature_point_ref` | 必须 | ✅ | 0% |
| `s5_ref` | 必须 | ✅ | 0% |
| `obj_name` | 必须 | ❌ | **100%** |
| `assertion` | 必须（Round 15 新增） | ❌ | **100%** |
| `preconditions` | 必须（结构化） | ❌（用 前置条件 文本） | 100% |

---

## 四、跨阶段字段溯源链路分析

### 4.1 当前链路（断裂）

```
S2 requirement_objects.json
├── objects[].obj_name = "商城首页道具列表"  ✅
├── objects[].feature_points[].fp_desc = "首页按销量展示前10个热门道具"  ✅
│
▼ S5 test_points.json
├── tp[].obj_id = "UI-ITEM-MALL-01-001-OBJ-01"  ✅ (ID only)
├── tp[].feature_point_ref = "UI-ITEM-MALL-01-001-OBJ-01-FP-1"  ✅
├── tp[].obj_name = ❌ 缺失
├── tp[].fp_name = ❌ 缺失
├── tp[].preconditions = ❌ 缺失
│
▼ S6 test_cases.json
├── tc[].obj_id = "UI-ITEM-MALL-01-001-OBJ-01"  ✅ (ID only)
├── tc[].feature_point_ref = "UI-ITEM-MALL-01-001-OBJ-01-FP-1"  ✅
├── tc[].用例描述 = "商城首页道具列表按销量降序展示"  ✅ (文本匹配)
├── tc[].obj_name = ❌ 缺失
├── tc[].assertion = ❌ 缺失
```

### 4.2 期望链路（完整）

```
S2 requirement_objects.json
├── objects[].obj_name = "商城首页道具列表"  ✅
├── objects[].feature_points[].fp_desc = "首页按销量展示前10个热门道具"  ✅
│
▼ S5 test_points.json
├── tp[].obj_name = "商城首页道具列表"  ✅ (100% 继承 S2)
├── tp[].fp_name = "首页销量排序展示"  ✅ (LLM 自创中性名)
├── tp[].feature_point_ref = "UI-ITEM-MALL-01-001-OBJ-01-FP-1"  ✅
├── tp[].preconditions = ["玩家已登录", "商城有道具数据"]  ✅
│
▼ S6 test_cases.json
├── tc[].obj_name = "商城首页道具列表"  ✅ (100% 继承 TP)
├── tc[].feature_point_ref = "UI-ITEM-MALL-01-001-OBJ-01-FP-1"  ✅
├── tc[].assertion = [{...}]  ✅
├── tc[].用例描述 = "商城首页道具列表按销量降序展示"  ✅ (基于 obj_name)
```

---

## 五、整改建议

### 5.1 新增门禁项

| 门禁项 | 触发阶段 | 校验内容 | 违规处理 |
|--------|---------|---------|---------|
| **S5-TP-OBJ-NAME** | S5 出口 | TP.obj_name 字段存在且 = S2 obj_name（逐字相等） | 退出码 1，阻塞 |
| **S5-TP-FP-NAME** | S5 出口 | TP.fp_name 字段存在且满足命名规则 | 退出码 1，阻塞 |
| **S5-TP-PRECONDITIONS** | S5 出口 | TP.preconditions 数组长度 ≥ 1 | 退出码 1，阻塞 |
| **S6-TC-OBJ-NAME** | S6 入口 | TC.obj_name 字段存在且 = S5 TP.obj_name | 退出码 1，阻塞 |
| **S6-TC-ASSERTION** | S6 出口 | TC.assertion 数组长度 ≥ 1 | 退出码 1，阻塞 |

### 5.2 门禁脚本实现建议

```python
# S5 出口门禁新增检查
def validate_tp_field_traceability(tps, objs):
    errors = []
    s2_obj_names = {o["id"]: o["obj_name"] for o in objs["objects"]}

    for tp in tps:
        # 检查 obj_name
        if "obj_name" not in tp:
            errors.append(f"TP {tp['tp_id']}: 缺少 obj_name 字段")
        elif tp["obj_name"] != s2_obj_names.get(tp.get("obj_id", "")):
            errors.append(f"TP {tp['tp_id']}: obj_name 与 S2 不匹配")

        # 检查 fp_name
        if "fp_name" not in tp:
            errors.append(f"TP {tp['tp_id']}: 缺少 fp_name 字段")

        # 检查 preconditions
        if "preconditions" not in tp or len(tp["preconditions"]) == 0:
            errors.append(f"TP {tp['tp_id']}: 缺少 preconditions 或为空")

    return errors
```

### 5.3 整改优先级

| 优先级 | 整改项 | 影响范围 | 整改难度 |
|--------|--------|---------|---------|
| P0 | S5 增加 `obj_name` 字段 | 全部 87 个 TP | 中（需重新生成或补丁） |
| P0 | S5 增加 `preconditions` 字段 | 全部 87 个 TP | 高（需补充前置条件） |
| P1 | S5 增加 `fp_name` 字段 | 全部 87 个 TP | 中（需 LLM 自创中性名） |
| P1 | S6 增加 `obj_name` 字段 | 全部 331+ 个 TC | 中（从 S2 继承） |
| P1 | S6 增加 `assertion` 字段 | 全部 331+ 个 TC | 高（需 LLM 补充断言） |

---

## 六、规范一致性检查

### 6.1 S5 SKILL.md vs 实际产出

| 规范条款 | 规范要求 | 实际状态 | 差距 |
|---------|---------|---------|------|
| §一 规则1 | TP 必须包含 `obj_name` 和 `fp_name` | 只有 `obj_id` 和 `feature_point_ref` | **缺失 obj_name/fp_name** |
| §一 规则2 | title/description 不带锚点 | title 含 "验证" 动词，符合 | ✅ |
| §七 7.1 | TP 必须包含 `preconditions` | 无此字段 | **缺失 preconditions** |
| §七 7.2 | TP 可包含 `tc_generation_hints` | 无此字段 | **缺失 tc_generation_hints** |

### 6.2 S6 SKILL.md vs 实际产出

| 规范条款 | 规范要求 | 实际状态 | 差距 |
|---------|---------|---------|------|
| §一 规则1 | TC 必须包含 `obj_name` 和 `feature_point_ref` | 只有 `feature_point_ref` | **缺失 obj_name** |
| Round 15 F-E | TC 必须包含 `assertion` 数组 ≥ 1 | 无此字段 | **缺失 assertion** |
| §12.4 | TC 必须继承 TP.preconditions | 无此链路 | **链路断裂** |

---

## 七、附录：字段溯源映射表

### 7.1 S2 → S5 → S6 继承关系

| 字段 | S2 来源 | S5 状态 | S6 继承 |
|------|--------|---------|---------|
| `obj_id` | `requirement_object.id` | ✅ 继承 | ✅ 继承 |
| `obj_name` | `requirement_object.obj_name` | ❌ 缺失 | ❌ 缺失 |
| `feature_point_ref` | `requirement_object.feature_points[].id` | ✅ 继承 | ✅ 继承 |
| `fp_name` | LLM 自创（基于 fp_desc） | ❌ 缺失 | ❌ 缺失（Round 15 F-F 已删除） |
| `preconditions` | S5 LLM 补充 | ❌ 缺失 | ❌ 链路断裂 |
| `assertion` | S6 LLM 补充 | N/A | ❌ 缺失 |

### 7.2 规范要求的字段链路

```
S2 obj_name ──────────→ S5 TP.obj_name ──────────→ S6 TC.obj_name
                         (LLM 自创)
S2 fp_desc ───────────→ S5 TP.fp_name ───────────→ (Round 15 F-F 已删除)
S5 TP.preconditions ───→ S6 TC.preconditions ─────→ TC.assertion
```

---

## 八、总结

### 8.1 核心问题

1. **S5 TP 缺少 3 个关键字段**：`obj_name`、`fp_name`、`preconditions`
2. **S6 TC 缺少 2 个关键字段**：`obj_name`、`assertion`
3. **字段溯源链路断裂**：下游无法直接验证字段继承关系

### 8.2 整改目标

1. **S5 产出达标**：所有 TP 含 `obj_name`、`fp_name`、`preconditions`
2. **S6 产出达标**：所有 TC 含 `obj_name`、`assertion`
3. **门禁完善**：新增 5 个门禁项，阻塞未达标产物

### 8.3 下一步行动

| 行动 | 负责方 | 期限 |
|------|--------|------|
| 在 governance/design_iter/ 新增整改方案 | Agent | 立即 |
| 更新 S5 SKILL.md 明确字段要求 | Agent | 下一轮 |
| 实现 S5 出口门禁脚本新增检查 | Agent | 下一轮 |
| 补充现有 TP 的缺失字段 | 人工/Auto | 待定 |
| 补充现有 TC 的缺失字段 | 人工/Auto | 待定 |
