# TC 结构化映射规范 (TC-STRUCTURAL-MAPPING-SPEC)

> **版本**: v1.1
> **日期**: 2026-07-20
> **目标**: 建立测试用例内部结构化映射关系，解决 Excel 生成质量差、结构混乱问题
> **角色**: AI 需求全流程治理工程师

---

## 1. 问题定义

### 1.1 当前问题

| 问题 | 表现 | 影响 |
|------|------|------|
| **步骤碎裂** | 1 个功能被拆成 6 条 TC（TC-001~TC-006），每条只有 1 步 | Excel 行数膨胀，结构混乱 |
| **前置条件重复** | 多条 TC 的 preconditions 完全相同（复用） | 数据冗余，难以维护 |
| **预期结果碎片** | 1 个功能的多条预期分散在不同 TC | 无法在一行内看到完整验证逻辑 |
| **映射关系丢失** | 无显式层级：功能描述→前置条件→步骤→预期 | 下游难以理解测试意图 |
| **TP 与 TC 脱节** | S5 TP 缺少前置条件/步骤/预期字段 | S6 需要 LLM 自己推断，质量不稳定 |

### 1.2 根因

S5 TP 是**测试意图**（告诉 S6 要测什么），但缺少**前置条件**字段，导致：
- S6 生成 TC 时需要 LLM 自己推断前置条件
- 步骤被拆碎（1步1TC）因为没有统一的前置条件指导
- 预期结果分散在多条 TC 中

---

## 2. TP → TC 映射设计

### 2.1 核心原则

| 原则 | 说明 |
|------|------|
| **TP = 测试意图** | 告诉 S6 要测什么，包含公共表头字段和前置条件 |
| **TC = 测试步骤** | 告诉 QA 怎么测，包含具体操作步骤和预期结果 |
| **1 TP → N TC** | 一个 TP 可以生成多条 TC（不同前置条件/场景） |

### 2.2 新 TP Schema（v1.1）

```json
{
  "tp_id": "UI-TP-001",
  "module": "UI",

  // ===== 公共表头字段（继承自 S2）=====
  "用例描述": "商城首页道具列表",
  "功能描述": "首页销量排序展示",
  "obj_id": "UI-ITEM-MALL-01-001-OBJ-01",
  "feature_point_ref": "UI-ITEM-MALL-01-001-OBJ-01-FP-1",

  // ===== 测试意图（TP 核心）=====
  "test_point_type": "POSITIVE",
  "title": "验证首页按销量降序展示前10个热门道具",
  "description": "验证玩家进入商城首页时，道具列表前10个道具按销量降序排列显示",

  // ===== 前置条件（公共）- v1.1 新增 ======
  "preconditions": [
    "玩家已登录游戏客户端",
    "商城已配置道具数据",
    "道具按销量有排序"
  ],

  // ===== 测试方法（可选）=====
  "test_methods": ["正向流程", "场景法"],

  // ===== 优先级 ======
  "priority": "P1",

  // ===== S4/S2 引用 ======
  "s4_reference": "S4-UI-ITEM-MALL-01-1.0",
  "story_id": "UI-ITEM-MALL-01-002",
  "is_assumed": false,
  "applies_rule": "S5 §1.2 UI module; POSITIVE flow; S4 §1.3 exception tree",

  // ===== 1 TP → N TC 生成提示 ======
  "tc_generation_hints": {
    "expected_tc_count": 2,
    "scenario_variants": [
      {
        "variant_id": "A",
        "scenario": "正常展示",
        "preconditions_additional": [],
        "expected_results": [
          "道具列表展示前10个道具",
          "销量从高到低降序排列",
          "每个道具显示完整名称和价格"
        ]
      },
      {
        "variant_id": "B",
        "scenario": "空状态",
        "preconditions_additional": ["商城道具数据为空"],
        "expected_results": [
          "显示空状态插画",
          "显示暂无道具提示"
        ]
      }
    ]
  }
}
```

### 2.3 新 TC Schema（简化版）

```json
{
  "case_id": "UI-TC-001",
  "module": "UI",

  // ===== 公共表头字段（继承自 TP）=====
  "用例描述": "商城首页道具列表",
  "功能描述": "首页销量排序展示",
  "obj_id": "UI-ITEM-MALL-01-001-OBJ-01",
  "feature_point_ref": "UI-ITEM-MALL-01-001-OBJ-01-FP-1",
  "s5_ref": "UI-TP-001",

  // ===== 测试方法 ======
  "test_point_type": "POSITIVE",
  "test_methods": ["正向流程", "场景法"],

  // ===== 优先级 ======
  "priority": "P1",

  // ===== 前置条件（继承自 TP + 场景增量）=====
  "前置条件": "玩家已登录游戏客户端，商城已配置道具数据，道具按销量有排序",

  // ===== 操作步骤 ======
  "操作步骤": [
    {"step_num": 1, "action": "玩家点击商城入口"},
    {"step_num": 2, "action": "系统加载商城首页"},
    {"step_num": 3, "action": "观察道具列表前10个道具的销量排序"}
  ],

  // ===== 预期结果（与步骤对应）=====
  "预期结果": [
    {"step_ref": 1, "预期": "道具列表展示前10个道具"},
    {"step_ref": 2, "预期": "销量从高到低降序排列"},
    {"step_ref": 3, "预期": "每个道具显示完整名称和价格"}
  ],

  // ===== 状态 ======
  "用例状态": "Draft",
  "备注": "v1.1 新结构映射"
}
```

---

## 3. 字段映射表

### 3.1 S2 → S5 TP 映射

| S5 TP 字段 | S2 来源 | 说明 |
|-------------|----------|------|
| `用例描述` | `obj_name` | 直接继承 |
| `功能描述` | `fp_name` | 直接继承 |
| `obj_id` | `requirement_object.id` | 直接继承 |
| `feature_point_ref` | `requirement_object.feature_points[].id` | 直接继承 |

### 3.2 S5 TP → S6 TC 映射

| S6 TC 字段 | S5 TP 来源 | 说明 |
|-------------|-------------|------|
| `用例描述` | `用例描述` | 直接继承 |
| `功能描述` | `功能描述` | 直接继承 |
| `obj_id` | `obj_id` | 直接继承 |
| `feature_point_ref` | `feature_point_ref` | 直接继承 |
| `s5_ref` | `tp_id` | 引用 |
| `test_point_type` | `test_point_type` | 直接继承 |
| `优先级` | `priority` | 直接继承 |
| `前置条件` | `preconditions` + `tc_generation_hints.variant.preconditions_additional` | 合并 |
| `操作步骤` | **S6 LLM 推理** | 根据前置条件和预期生成 |
| `预期结果` | `tc_generation_hints.variant.expected_results` | 直接引用 |

---

## 4. 四层映射模型

### 4.1 映射关系

```
┌─────────────────────────────────────────────────────────────────┐
│  L1: 用例描述 (case_description)                                 │
│  = 1 个需求对象 (来自 S2 obj_name)                              │
│  = S5 TP.用例描述                                               │
├─────────────────────────────────────────────────────────────────┤
│  L2: 功能描述列表 (functional_descriptions[])                    │
│  = 1 个用例描述 → N 个功能描述                                   │
│  = 每个 FP 对应 1 个功能描述                                     │
│  = S5 TP.功能描述                                               │
├─────────────────────────────────────────────────────────────────┤
│  L3: 前置条件列表 (preconditions[])                             │
│  = 1 个功能描述 → N 个前置条件                                   │
│  = S5 TP.preconditions + tc_generation_hints.variant.additional │
├─────────────────────────────────────────────────────────────────┤
│  L4: 步骤预期组 (step_expected_groups[])                          │
│  = 1 个前置条件 → N 个步骤 + M 个预期                            │
│  = S6 LLM 推理操作步骤                                          │
│  = S5 TP.tc_generation_hints.expected_results                   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 映射关系表

| 关系 | 基数 | 说明 |
|------|------|------|
| 用例描述 → 功能描述 | 1:N | 1 个需求对象可含多个功能点 |
| 功能描述 → 前置条件 | 1:N | 1 个功能可测多个初始状态（如余额充足/不足） |
| 前置条件 → 步骤 | 1:N | 1 个前置条件展开为 N 步连贯操作 |
| 步骤 → 预期结果 | N:M | 多个步骤对应多个预期（每步可有独立预期） |

---

## 5. S5 生成规范

### 5.1 TP 必填字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tp_id` | string | 是 | 测试点 ID |
| `module` | string | 是 | 模块 |
| `用例描述` | string | 是 | 来自 S2 obj_name |
| `功能描述` | string | 是 | 来自 S2 fp_name |
| `test_point_type` | string | 是 | POSITIVE/NEGATIVE/BOUNDARY_*等 |
| `title` | string | 是 | 测试点标题 |
| `description` | string | 是 | 测试点描述 |
| `preconditions` | array | 是 | **v1.1 新增** 前置条件列表 |
| `priority` | string | 是 | P0/P1/P2 |
| `obj_id` | string | 是 | 来自 S2 |
| `feature_point_ref` | string | 是 | 来自 S2 |

### 5.2 preconditions 字段规范

```json
{
  "preconditions": [
    "玩家已登录游戏客户端",
    "商城已配置道具数据",
    "道具按销量有排序"
  ]
}
```

**规则**：
- 每条前置条件必须是**独立可验证的初始状态**
- 避免"无"占位（除非业务确实无前置条件）
- 长度建议 1-5 条

### 5.3 tc_generation_hints 字段规范（可选）

```json
{
  "tc_generation_hints": {
    "expected_tc_count": 2,
    "scenario_variants": [
      {
        "variant_id": "A",
        "scenario": "正常展示",
        "preconditions_additional": [],
        "expected_results": ["预期1", "预期2"]
      }
    ]
  }
}
```

**规则**：
- `expected_tc_count`：期望生成的 TC 数量（指导值）
- `scenario_variants`：场景变体列表
- `preconditions_additional`：相对于 base preconditions 的增量
- `expected_results`：该场景的预期结果列表

---

## 6. S6 生成规范

### 6.1 TC 必填字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `case_id` | string | 是 | 用例 ID |
| `用例描述` | string | 是 | 继承自 TP |
| `功能描述` | string | 是 | 继承自 TP |
| `前置条件` | string | 是 | 合并 TP.preconditions + variant.additional |
| `操作步骤` | array | 是 | LLM 推理，每步含 step_num + action |
| `预期结果` | array | 是 | 继承自 TP + variant.expected_results |
| `obj_id` | string | 是 | 继承自 TP |
| `feature_point_ref` | string | 是 | 继承自 TP |
| `s5_ref` | string | 是 | 引用 TP ID |
| `用例状态` | string | 是 | Draft/Ready/Rejected/Deprecated |

### 6.2 步骤-预期对应规则

| 规则 | 说明 |
|------|------|
| `step_ref` 必填 | 每条预期必须关联对应步骤号 |
| 顺序映射 | 如果预期无 `step_ref`，按步骤顺序对应 |
| 步骤数 ≥ 2 | 禁止 1 步 1 TC |

### 6.3 禁止模式

| 禁止 | 示例 | 正确做法 |
|------|------|----------|
| 1 步 1 TC | TC-001: 玩家点击商城入口 | 合并为 1 条 TC，含多步 |
| 步骤与预期不对应 | steps=[1,2,3] 但 expected=[1个文本] | 每步有对应预期或显式 `step_ref` |
| 前置条件为空 | `"前置条件": ""` | 必须填写具体初始状态 |
| 预期结果缺失 | `"预期结果": []` | 每步至少 1 个预期 |

---

## 7. Excel 生成规则

### 7.1 列映射

| Excel 列 | 数据来源 | 说明 |
|----------|----------|------|
| A: 用例ID | case_id | 唯一标识 |
| B: 模块 | module | UI/BIZ/LOG 等 |
| C: 用例描述 | 用例描述 | L1 |
| D: 功能描述 | 功能描述 | L2 |
| E: 前置条件 | 前置条件 | L3 |
| F: 操作步骤 | 操作步骤 拼接为多行文本 | L4 |
| G: 预期结果 | 预期结果 拼接为多行文本 | L4 |
| H: 优先级 | priority | P0/P1/P2 |
| I: 用例状态 | 用例状态 | Draft/Ready |
| J: 备注 | 备注 | 元数据 |

### 7.2 步骤/预期 渲染规则

```python
def render_steps_with_expected(steps: list, expected: list) -> tuple[str, str]:
    """渲染步骤与预期，返回 (steps_text, expected_text)"""
    # 步骤渲染：按 step_num 顺序
    step_lines = [f"{s['step_num']}. {s['action']}" for s in steps]

    # 预期渲染：按 step_ref 对应步骤号输出
    if expected and isinstance(expected[0], dict) and "step_ref" in expected[0]:
        exp_lines = [f"[步骤{e.get('step_ref', '')}] {e['预期']}" for e in expected]
    else:
        exp_lines = [str(e) for e in expected]

    return "\n".join(step_lines), "\n".join(exp_lines)
```

---

## 8. 实现要求

### 8.1 test_case_formatter.py 改造（已实现）

```python
# 新增函数（v1.1）
def is_new_structural_mapping_format(tc: dict) -> bool:
    """检测 TC 是否为新的层级结构格式"""
    ...

def render_steps_with_expected(steps: list, expected: list) -> tuple[str, str]:
    """渲染步骤与预期"""
    ...

def validate_structural_mapping(tc: dict) -> dict:
    """校验 TC 的结构化映射合规性"""
    ...
```

### 8.2 S5 SKILL.md 改造（待完成）

在 S5 SKILL.md 中增加：
- `preconditions` 必填字段规范
- `tc_generation_hints` 字段规范

### 8.3 S6 SKILL.md §12 更新（已实现）

- 四层映射模型
- 禁止模式
- 自检清单

---

## 9. 验收标准

| # | 标准 | 验证方式 |
|---|------|----------|
| 1 | S5 TP 包含 preconditions 字段 | JSON schema 验证 |
| 2 | S5 TP 包含 tc_generation_hints 字段（可选） | JSON schema 验证 |
| 3 | S6 TC 包含步骤-预期对应关系 | 校验 `step_ref` 字段 |
| 4 | 步骤数 ≥ 2（禁止 1 步 1 TC） | 统计 `操作步骤` 长度 |
| 5 | Excel 导出结构清晰（多步可读） | 人工审查 |

---

## 10. 附录

### 10.1 术语表

| 术语 | 定义 |
|------|------|
| TP | 测试点（Test Point），测试意图，1 个 TP → N 个 TC |
| TC | 测试用例（Test Case），测试步骤 |
| 用例描述 | L1，需求对象名称 |
| 功能描述 | L2，功能点描述 |
| 前置条件 | L3，进入测试前的初始状态 |
| 操作步骤 | L4，具体操作序列 |
| 预期结果 | L4，每步的期望验证点 |

### 10.2 参考文件

- `ai_workflow/test_case_formatter.py`
- `.cursor/skills/aidocx-s5-test-points/SKILL.md`
- `.cursor/skills/aidocx-s6-test-cases/SKILL.md`
- `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json`
