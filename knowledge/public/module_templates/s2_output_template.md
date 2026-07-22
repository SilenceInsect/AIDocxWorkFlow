# S2 产出模版（S2 Output Template）

> 本文件是 S2 阶段产出的**固定模版**，定义 backlog.json / backlog.md / requirement_objects.json 的标准化结构。
> **强制遵循**：S2 产出的所有文件必须符合本模版规定的字段、层级、格式。
>
> **来源**：`.cursor/rules/STAGE_S2_BREAKDOWN.mdc`（阶段规范）+ `.cursor/MODULES.md`（模块定义）

---

## 目录

1. [backlog.json 完整结构](#1-backlogjson-完整结构)
2. [backlog.md 完整结构](#2-backlogmd-完整结构)
3. [requirement_objects.json 完整结构](#3-requirement_objectsjson-完整结构)
4. [字段说明与示例](#4-字段说明与示例)
5. [验收检查清单](#5-验收检查清单)

---

## 1. backlog.json 完整结构

### 1.1 顶层结构

```json
{
  "meta": {
    "req_name": "string（需求名称）",
    "version": "string（如 v3.01）",
    "stage": "S2",
    "created_at": "ISO 8601 时间戳",
    "created_by": "AIDocxWorkFlow",
    "quality_level": "HIGH | MEDIUM | LOW",
    "is_incremental": "boolean"
  },
  "summary": {
    "epic_count": "integer",
    "story_count": "integer",
    "requirement_object_count": "integer",
    "feature_point_count": "integer",
    "ui_ratio": "float（0.0-1.0）",
    "ui_story_count": "integer",
    "s3_mode_recommend": "depth | lightweight",
    "s3_mode_reasons": ["string（判定原因，可审计）"]
  },
  "priority_epics": ["string（Epic ID 列表，按优先级排序）"],
  "risk_seeds": [
    {
      "area": "string（风险区域）",
      "level": "high | medium | low",
      "reason": "string（风险原因）",
      "source": "string（如 S1.RP-001）"
    }
  ],
  "confirmed_boundaries": [
    {
      "scope": "string（已确认的边界范围）",
      "source": "string（如 S1.B-001）"
    }
  ],
  "epics": [
    {
      "id": "string（如 CONFIG-001）",
      "module": "string（CONFIG|UI|BIZ|AUX|LINK|SPECIAL|LOG|HINT）",
      "title": "string（Epic 标题）",
      "estimated_weeks": "number",
      "priority": "boolean",
      "stories": [ /* 见 1.2 */ ],
      "requirement_objects": [ /* 见 1.3 */ ]
    }
  ]
}
```

### 1.2 Story 结构（epics[].stories[]）

```json
{
  "id": "string（如 CONFIG-001-001）",
  "title": "string（标准化用户故事句式：作为[角色]，我希望[功能]，以便[价值]）",
  "acceptance_criteria": [
    "string（≥2 条，区分三类：开发验收/测试验收/策划数值验收）"
  ],
  "precondition": "string（前置依赖）",
  "input_data": "string（触发输入）",
  "expected_output": "string（业务最终产出）",
  "source": "original | clarification | fallback",
  "requirement_objects": ["string（OBJ ID 列表）"],
  "feature_points": [
    {
      "id": "string（如 FP-001-01）",
      "name": "string（功能点名称）",
      "type": "positive | negative | boundary | exception",
      "module": "string（模块归属）"
    }
  ]
}
```

### 1.3 Epic 内 OBJ 结构（epics[].requirement_objects[]）

> ⚠️ **弃用字段**：backlog.json 中 epic 内嵌的 `requirement_objects[]` 数组**仅用于摘要**。
> 完整 OBJ 定义在 `requirement_objects.json` 中。

```json
{
  "id": "string（如 OBJ-001）",
  "name": "string（对象名称）",
  "fields": ["string（字段列表，仅摘要）"]
}
```

---

## 2. backlog.md 完整结构

```markdown
# 需求拆解 Backlog — {req_name} {version}

## 版本信息

- **版本**：{version}
- **阶段**：S2 需求拆解
- **日期**：{YYYY-MM-DD}
- **质量等级**：{HIGH|MEDIUM|LOW}
- **Epic 数**：{N}
- **Story 数**：{M}
- **需求对象数**：{K}
- **功能点数**：{L}

---

## Epic N：{EpicID} — {Epic 标题}

**模块**：{模块} | **优先级**：{true|false} | **估算**：{N} 周

### Story

#### {StoryID} — {Story 标题}

- **前置条件**：{precondition}
- **验收标准**：
  1. {AC1}
  2. {AC2}
  ...

**需求对象**：
- {OBJ-ID} {OBJ名称}（{字段列表}）

**功能点**：
- {FP-ID-A} {FP名称}（{FP描述}）
- {FP-ID-B} {FP名称}（{FP描述}）

---

## Epic 统计摘要

| Epic ID | 模块 | 名称 | Story 数 | OBJ 数 | FP 数 | 优先级 |
|---------|------|------|----------|--------|-------|--------|
| ... | ... | ... | ... | ... | ... | ... |

---

## 测试时序规划

### 第一阶段：基础配置、后台参数
- {Epic 列表}

### 第二阶段：核心主流程功能
- {Epic 列表}

### 第三阶段：边界异常、并发、弱网
- {Epic 列表}

### 第四阶段：联动回归、合规校验
- {Epic 列表}

---

## 风险种子清单

| 风险 ID | 区域 | 等级 | 来源 |
|---------|------|------|------|
| RP-001 | {area} | {high|medium|low} | {source} |
| ... | ... | ... | ... |

---

## 确认边界清单

| 边界 ID | 范围 | 来源 |
|---------|------|------|
| B-001 | {scope} | {source} |
| ... | ... | ... |
```

---

## 3. requirement_objects.json 完整结构

### 3.1 顶层结构

```json
{
  "meta": {
    "req_name": "string",
    "version": "string",
    "stage": "S2",
    "created_at": "ISO 8601 时间戳",
    "created_by": "AIDocxWorkFlow"
  },
  "objects": [
    {
      "id": "string（如 UI-SHOP-001-OBJ-01）",
      "obj_name": "string",
      "belong_module": "string（CONFIG|UI|BIZ|AUX|LINK|SPECIAL|LOG|HINT）",
      "scene": "string（业务场景描述）",
      "input": "string（触发输入条件）",
      "normal_flow": "string（正向标准流程）",
      "exception_flow": "string（异常分支流程）",
      "data_change": "string（配置|内存|DB|缓存|第三方）",
      "output_display": "string（UI弹窗|飘字|日志|推送|后台数据，多选）",
      "verify_method": "string（配置工具|客户端操作|GM指令|抓包|日志平台，多选）",
      "epic_id": "string",
      "story_id": "string",
      "feature_points": [ /* 见 3.2 */ ]
    }
  ]
}
```

### 3.2 FP 结构（objects[].feature_points[]）

```json
{
  "id": "string（如 UI-SHOP-001-OBJ-01-FP-1）",
  "fp_desc": "string（功能描述）",
  "check_type": "string（配置|界面|业务|日志|安全）",
  "verify_standard": "string（单一验收标准）"
}
```

---

## 4. 字段说明与示例

### 4.1 backlog.json 必填字段清单

| 层级 | 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|------|
| **meta** | `req_name` | string | ✅ | 需求名称 |
| | `version` | string | ✅ | 版本号（如 v3.01） |
| | `stage` | string | ✅ | 固定为 "S2" |
| | `created_at` | string | ✅ | ISO 8601 时间戳 |
| | `created_by` | string | ✅ | 固定为 "AIDocxWorkFlow" |
| | `quality_level` | string | ✅ | HIGH / MEDIUM / LOW |
| | `is_incremental` | boolean | ✅ | 是否增量拆解 |
| **summary** | `epic_count` | integer | ✅ | Epic 总数 |
| | `story_count` | integer | ✅ | Story 总数 |
| | `requirement_object_count` | integer | ✅ | OBJ 总数 |
| | `feature_point_count` | integer | ✅ | FP 总数（必须等于实际 FP 总数） |
| | `ui_ratio` | float | ✅ | UI Story 占比（供 S3 模式选择） |
| | `ui_story_count` | integer | ✅ | UI Story 数量 |
| | `s3_mode_recommend` | string | ✅ | depth / lightweight |
| | `s3_mode_reasons` | array | ✅ | 判定原因（可审计） |
| **Epic** | `id` | string | ✅ | 格式：`{Module}-{NNN}` |
| | `module` | string | ✅ | 8 模块之一 |
| | `title` | string | ✅ | Epic 标题 |
| | `estimated_weeks` | number | ✅ | 估算周数 |
| | `priority` | boolean | ✅ | 是否优先 |
| | `stories` | array | ✅ | Story 数组（非空） |
| **Story** | `id` | string | ✅ | 格式：`{EpicID}-S{NN}` |
| | `title` | string | ✅ | 标准化用户故事句式 |
| | `acceptance_criteria` | array | ✅ | ≥2 条，区分三类验收 |
| | `precondition` | string | ✅ | 前置条件 |
| | `input_data` | string | ✅ | 触发输入 |
| | `expected_output` | string | ✅ | 预期产出 |
| | `source` | string | ✅ | original / clarification / fallback |
| | `feature_points` | array | ✅ | FP 数组 |

### 4.2 requirement_objects.json 必填字段清单

| 层级 | 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|------|
| **Object** | `id` | string | ✅ | 格式：`{StoryID}-OBJ-{NN}` |
| | `obj_name` | string | ✅ | 对象名称 |
| | `belong_module` | string | ✅ | 8 模块之一（单选） |
| | `scene` | string | ✅ | 业务场景描述 |
| | `input` | string | ✅ | 触发输入条件 |
| | `normal_flow` | string | ✅ | 正向标准流程（输入→处理→输出） |
| | `exception_flow` | string | ✅ | 异常分支流程 |
| | `data_change` | string | ✅ | 5 选一：配置/内存/DB/缓存/第三方 |
| | `output_display` | string | ✅ | 5 选多：UI弹窗/飘字/日志/推送/后台数据 |
| | `verify_method` | string | ✅ | 5 选多：配置工具/客户端操作/GM指令/抓包/日志平台 |
| | `epic_id` | string | ✅ | 归属 Epic ID |
| | `story_id` | string | ✅ | 归属 Story ID |
| | `feature_points` | array | ✅ | FP 数组 |
| **FP** | `id` | string | ✅ | 格式：`{OBJID}-FP-{N}` |
| | `fp_desc` | string | ✅ | 功能描述 |
| | `check_type` | string | ✅ | 配置/界面/业务/日志/安全 |
| | `verify_standard` | string | ✅ | 单一验收标准 |

### 4.3 字段枚举值

| 字段 | 合法值 |
|------|--------|
| `stage` | `S2` |
| `quality_level` | `HIGH` / `MEDIUM` / `LOW` |
| `module` / `belong_module` | `CONFIG` / `UI` / `BIZ` / `AUX` / `LINK` / `SPECIAL` / `LOG` / `HINT` |
| `source` | `original` / `clarification` / `fallback` |
| `data_change` | `配置` / `内存` / `DB` / `缓存` / `第三方` |
| `output_display` | `UI弹窗` / `飘字` / `日志` / `推送` / `后台数据` |
| `verify_method` | `配置工具` / `客户端操作` / `GM指令` / `抓包` / `日志平台` |
| `check_type` | `配置` / `界面` / `业务` / `日志` / `安全` |
| `risk.level` | `high` / `medium` / `low` |
| `s3_mode_recommend` | `depth` / `lightweight` |
| `FP.type` | `positive` / `negative` / `boundary` / `exception` |

---

## 5. 验收检查清单

### 5.1 物量守恒检查

> S2 门禁强制要求：`summary.feature_point_count == Σ 各 Epic 内 Story 内 FP 总数`

```bash
# 验证脚本（待实现）
python3 -c "
import json
with open('backlog.json') as f:
    data = json.load(f)
total_fp = sum(
    len(story['feature_points'])
    for epic in data['epics']
    for story in epic['stories']
)
assert total_fp == data['summary']['feature_point_count'], \
    f'物量不守恒：summary={data[\"summary\"][\"feature_point_count\"]}, 实际={total_fp}'
print('物量守恒检查通过')
"
```

### 5.2 字段完整性检查

| 检查项 | 要求 | 不通过 → |
|--------|------|----------|
| `summary.feature_point_count` | 必须等于实际 FP 总数 | **S2 失败** |
| 每个 Story 的 `acceptance_criteria` | ≥2 条 | 补充提示 |
| 每个 Story 的 `feature_points` | 非空数组 | 补充 FP |
| 每个 Object 的 9 标准字段 | 全部填写 | 标注缺失项 |
| OBJ 的 `feature_points` | 非空数组 | 补充 FP |
| 每个 FP 的 4 字段 | 全部填写 | 标注缺失项 |
| `meta.stage` | 必须为 "S2" | 修正 |

### 5.3 ID 格式检查

| 层级 | 正确格式 | 错误示例 |
|------|----------|----------|
| Epic | `{Module}-{NNN}` | `Epic01` / `商城首页` |
| Story | `{EpicID}-S{NN}` | `Story01` / `CONFIG-001-01` |
| OBJ | `{StoryID}-OBJ-{NN}` | `OBJ01` / `CONFIG-OBJ-1` |
| FP | `{OBJID}-FP-{N}` | `FP01` / `OBJ-1-FP1` |

### 5.4 模块归属检查

| 检查项 | 要求 | 不通过 → |
|--------|------|----------|
| Epic 的 `module` | 必须是 8 模块之一 | 修正 |
| Story 的 `feature_points[].module` | 必须是 8 模块之一 | 修正 |
| OBJ 的 `belong_module` | 必须是 8 模块之一（单选） | 修正 |

### 5.5 下游链路检查

| 检查项 | 要求 | 来源 |
|--------|------|------|
| `epic.id` 前缀 | 与 `epic.module` 对应 | S5/S6 读取 |
| `story.id` 前缀 | 与 `epic.id` 对应 | S5/S6 读取 |
| `obj_id` 字段名 | 必须为 `id`（非 `object_id`） | S5/S6 读取 |
| `FP.id` 引用 | 必须与 `requirement_objects.json` 一致 | S5/S6 读取 |

---

## 6. 实际产出示例（游戏道具商城系统 v3.01）

### 6.1 backlog.json 示例片段

```json
{
  "meta": {
    "req_name": "游戏道具商城系统",
    "version": "v3.01",
    "stage": "S2",
    "created_at": "2026-07-20T14:15:00+08:00",
    "created_by": "AIDocxWorkFlow",
    "quality_level": "HIGH",
    "is_incremental": false
  },
  "summary": {
    "epic_count": 7,
    "story_count": 20,
    "requirement_object_count": 14,
    "feature_point_count": 45,
    "ui_ratio": 0.2,
    "ui_story_count": 5,
    "s3_mode_recommend": "lightweight",
    "s3_mode_reasons": [
      "UI Story count = 5 / total = 20 → ui_ratio = 0.20 < 0.30"
    ]
  },
  "epics": [
    {
      "id": "BIZ-PURCHASE-001",
      "module": "BIZ",
      "title": "购买流程",
      "estimated_weeks": 3,
      "priority": true,
      "stories": [
        {
          "id": "BIZ-PURCHASE-001-S01",
          "title": "作为玩家，我希望使用游戏币购买道具，以便获得游戏内物品",
          "acceptance_criteria": [
            "[开发验收] 余额充足则扣减游戏币",
            "[测试验收] 余额不足时拒绝购买并提示",
            "[策划数值验收] 道具到账时间 ≤ 1000ms"
          ],
          "precondition": "玩家选择游戏币支付，余额充足",
          "input_data": "道具ID、数量、支付密码",
          "expected_output": "订单创建成功、道具到账",
          "source": "original",
          "requirement_objects": ["OBJ-PURCHASE-001", "OBJ-PURCHASE-002"],
          "feature_points": [
            {"id": "FP-PURCHASE-001-A", "name": "余额校验与扣减", "type": "positive", "module": "BIZ"},
            {"id": "FP-PURCHASE-001-B", "name": "订单创建", "type": "positive", "module": "BIZ"}
          ]
        }
      ],
      "requirement_objects": []
    }
  ]
}
```

### 6.2 requirement_objects.json 示例片段

```json
{
  "meta": {
    "req_name": "游戏道具商城系统",
    "version": "v3.01",
    "stage": "S2",
    "created_at": "2026-07-20T14:15:00+08:00",
    "created_by": "AIDocxWorkFlow"
  },
  "objects": [
    {
      "id": "BIZ-PURCHASE-001-OBJ-01",
      "obj_name": "购买流程",
      "belong_module": "BIZ",
      "scene": "玩家完成道具购买支付",
      "input": "道具ID + 数量 + 支付方式",
      "normal_flow": "校验余额 → 扣减资产 → 创建订单 → MQ下发道具 → 发送邮件通知",
      "exception_flow": "余额不足 → 拒绝购买；支付超时 → 订单超时；MQ失败 → 重试/工单",
      "data_change": "DB（订单表、玩家资产表）",
      "output_display": "DB数据变更 + MQ消息 + 邮件",
      "verify_method": "GM指令 + 日志平台",
      "epic_id": "BIZ-PURCHASE-001",
      "story_id": "BIZ-PURCHASE-001-S01",
      "feature_points": [
        {
          "id": "BIZ-PURCHASE-001-OBJ-01-FP-1",
          "fp_desc": "游戏币购买",
          "check_type": "业务",
          "verify_standard": "余额充足则扣减游戏币，生成已支付订单，道具到账≤1000ms"
        }
      ]
    }
  ]
}
```

---

## 7. 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-20 | 初始版本，定义 S2 三产出固定模版 |
