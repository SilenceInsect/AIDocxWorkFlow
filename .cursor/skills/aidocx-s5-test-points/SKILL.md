---
name: aidocx-s5-test-points
description: >
  AIDocxWorkFlow Stage 5 — 测试点生成。模块定义完整见 `.cursor/MODULES.md`（项目级唯一真相源），不重写压缩版。完整类型数量约束见 §1.1 + §1.4 + 各模块 .md 子模板（无硬数字）。
  Use when the user runs /aidocx-s5-test-points, pastes S2 backlog, or starts test point generation.
  使用当用户执行 /aidocx-s5-test-points、粘贴 S2 backlog、或进行 S5 测试点生成任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s5-test-points
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

## 🔴 命名一致性铁律（字段溯源版 — 最高优先级，违反直接 L1 打回）

> **NAME-FIELD-001**：本节是命名追溯性修复的核心约束。S5 TP 必须包含正式 OBJ/FP 名称字段，且必须有显式字段，文本语义链路才算完整。
> **校验精度**：字段溯源版（字段精准匹配——obj_name/fp_name == S2）+ LLM 自由文本溯源（title/description 不带锚点）

### 一、核心基准规则

#### 规则 1：TP 必须包含显式字段 obj_name 和 fp_name

每条 TP 必须有以下两个字段，逐字匹配 S2：
- `obj_name`：从 S2 `requirement_objects[].obj_name` 取值，100% 原样写入；**必须是实体名词**
- `fp_name`：LLM 自创中性功能名，**命名规则：必须是动词/动作 + 长度 ≤ 20 字符 + 不与 S2 `fp_desc` 字面量重复**；**禁止名词性描述**（如"道具数据配置"应改为"道具从配置加载"）

#### 规则 2：title 和 description 不带锚点（纯场景文本）

格式：纯场景简短标题 / 完整测试逻辑
- **禁止** title / description 以 `【OBJ - FP】` 锚点开头
- 锚点仅存 JSON 字段，不重复进文本
- 锚点中的名称必须和 S2 正式名称逐字相等（仅在 JSON 字段中校验）

#### 规则 3：名称来源唯一，禁止 LLM 自创 OBJ

- OBJ 的正式名称**只能从 S2 requirement_objects.json 原样取用**（100% 逐字相等）
- 禁止改写、缩写、意译、口语化替换
- FP 的名称由 LLM 自创（中性功能名），但禁止与 S2 `fp_desc` 字面量重复

### 二、字段格式模板

#### title 字段
```
{4-12字场景摘要}（不带锚点）
```
示例：
- ✅ 首页销量排序展示验证

#### description 字段
```
{完整测试逻辑：前置+操作+预期}（不带锚点）
```
示例：
- ✅ 玩家已登录游戏，进入商城首页。验证按销量降序展示前10个道具，与 S2 OBJ 对比字段值一致。

### 三、自检流程（输出前必须执行）

生成完所有 TP 后，逐条检查：

| 检查项 | 通过标准 |
|--------|---------|
| obj_name 字段存在 | TP.obj_name == S2 obj_name（逐字相等） |
| fp_name 字段存在 | TP.fp_name 满足命名规则（必须是动词/动作 + ≤ 20 字符 + 不与 S2 fp_desc 重复） |
| title 无锚点 | 开头不是【xxx - xxx】格式 |
| description 无锚点 | 开头不是【xxx - xxx】格式 |
| 锚点分离 | title 和 description 不含【】锚点（仅 JSON 字段承载名称） |
| OBJ 名正确 | TP.obj_name = S2 obj_name（逐字相等）；**必须是实体名词** |
| FP 名正确 | TP.fp_name ≠ S2 fp_desc（避免语义重定义）；**禁止名词性描述** |
| 无简称替代 | 没有用简称、缩写、口语化词替代正式 OBJ 名称 |

**批量统计要求**：
- 字段匹配率 = 100%
- 锚点分离率 = 100%（无【】在文本字段）
- 不达标则逐条修正，直到达标再输出

### 四、常见错误对照表

| 错误类型 | 错误示例 | 正确示例 |
|---------|---------|---------|
| title 带锚点 | "【道具搜索功能 - 支持道具名称模糊搜索】验证模糊搜索功能正常" | "模糊搜索功能正常验证" |
| description 带锚点 | "【道具搜索 - 模糊搜索】验证..." | "玩家输入道具名称关键字，系统返回匹配道具列表" |
| fp_name 重复 S2 fp_desc | "支持道具名称模糊搜索"（== S2 fp_desc） | "道具搜索功能启用"（LLM 自创中性名） |
| OBJ 名改写 | "【道具搜索 - 模糊搜索】..." | "TP.obj_name = '道具搜索功能'"（S2 严格匹配） |
| 锚点不在开头 | "测试：【道具搜索功能 - xxx】..." | TP 无【】锚点；OBJ/FP 仅存 JSON 字段 |
| 缺少 obj_name 字段 | TP 无 obj_name 字段 | TP.obj_name = "商城首页道具列表" |
| 缺少 fp_name 字段 | TP 无 fp_name 字段 | TP.fp_name = "首页销量排序展示"（LLM 自创中性名） |

### 五、L1 校验入口

校验函数：`ai_workflow/validators/l1_s5.py` 的 `L1S5Validator.validate_field_traceability()`
调用方式：
```python
from ai_workflow.validators.l1_s5 import L1S5Validator
v = L1S5Validator()
v.set_requirement_objects(objs)
passed, errors, stats = v.validate_field_traceability(test_points)
# passed=True 且 errors=[] 才可进入 S6
```

### 六、Schema 要求

每条 TP 必须包含以下字段：

```json
{
  "tp_id": "TP-001",
  "obj_name": "商城首页道具列表",
  "fp_name": "首页销量排序展示",
  "title": "首页销量排序展示验证",
  "description": "玩家已登录游戏，进入商城首页。验证按销量降序展示前10个道具，与 S2 OBJ 对比字段值一致。",
  ...
}
```

---

## §七 TP 前置条件规范（v1.1 新增）

> **来源**: `governance/design_iter/plans/v28/TC_STRUCTURAL_MAPPING_SPEC.md`
> **目的**: S5 TP 为 S6 TC 提供前置条件，解决 S6 步骤碎裂、预期分散问题

### 7.1 preconditions 字段（必填）

**每个 TP 必须包含 `preconditions` 字段**，用于告诉 S6 这个测试点的前置条件：

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

**规则**：
- 每条前置条件必须是**独立可验证的初始状态**
- 避免"无"占位（除非业务确实无前置条件）
- 长度建议 1-5 条
- 禁止空数组 `[]`

### 7.2 tc_generation_hints 字段（可选）

**用于指导 S6 生成多条 TC 的场景变体**：

```json
{
  "tc_generation_hints": {
    "expected_tc_count": 2,
    "scenario_variants": [
      {
        "variant_id": "A",
        "scenario": "正常展示",
        "preconditions_additional": [],
        "expected_results": [
          "道具列表展示前10个道具",
          "销量从高到低降序排列"
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

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `expected_tc_count` | number | 期望生成的 TC 数量（指导值） |
| `scenario_variants` | array | 场景变体列表 |
| `variant_id` | string | 变体 ID（如 A/B/C） |
| `scenario` | string | 场景名称 |
| `preconditions_additional` | array | 相对于 base preconditions 的增量 |
| `expected_results` | array | 该场景的预期结果列表 |

### 7.3 S5 → S6 链路

```
S5 TP
  ├── preconditions: [玩家已登录, 商城有数据, ...]
  ├── title: "验证首页按销量降序展示"
  └── tc_generation_hints: {场景A, 场景B}
         │
         ▼ S6 LLM 推理

S6 TC 1 (场景A: 正常展示)
  ├── 前置条件: [玩家已登录, 商城有数据, ...]  ← 继承 TP.preconditions
  ├── 操作步骤: [点击入口 → 加载首页 → 观察排序] ← LLM 推理
  └── 预期结果: [展示10个, 降序排列] ← 继承 TP.tc_generation_hints.variant.expected_results

S6 TC 2 (场景B: 空状态)
  ├── 前置条件: [玩家已登录, 商城数据为空] ← TP.preconditions + variant.additional
  ├── 操作步骤: [点击入口 → 加载首页 → 观察空状态] ← LLM 推理
  └── 预期结果: [显示插画, 显示暂无道具] ← variant.expected_results
```

### 7.4 自检清单（v1.1 新增）

| 检查项 | 通过标准 |
|--------|----------|
| `preconditions` 字段存在 | TP 含 `preconditions` 数组 |
| `preconditions` 非空 | `len(preconditions) >= 1` |
| `preconditions` 内容合理 | 每条是独立可验证的初始状态 |
| `tc_generation_hints` 存在（可选） | TP 含 `tc_generation_hints` 对象 |
| `scenario_variants` 有预期结果 | 每个 variant 含 `expected_results` 数组 |

### 7.5 错误对照

| 错误类型 | 错误示例 | 正确示例 |
|---------|---------|---------|
| 缺少 preconditions | TP 无 preconditions 字段 | `preconditions: ["玩家已登录"]` |
| preconditions 为空 | `"preconditions": []` | `preconditions: ["玩家已登录", "商城有数据"]` |
| preconditions 占位 | `"preconditions": ["无"]` | `preconditions: ["玩家已登录游戏客户端"]` |

---

## §生成前必答 · 思维约束（v3.02 新增 · 强制）

> **背景**：Agent 的默认工作模式是「找字段模板 → 填引用 → 套格式 → 结束」。
> 这个模式产出的是「看起来合规的废话」——字段全填了，但 description/title/preconditions 都在套模板，没有传递任何有用的测试意图。
> 本节是从根子上改变这个模式的约束——强制 Agent 在生成内容前先思考、再动笔。

### 核心约束

**在写每一条 TP 之前，先用一句话回答这个问题**：

> "这段 description 写出来，能不能让一个没看过 S2 的人知道在测什么？"

如果答不出来——说明在套模板，不是在写测试。回去重写。

### 5 条强制规则

| # | 规则 | 反例 | 正例 |
|---|------|------|------|
| 1 | **description 必须包含具体场景 + 具体预期**（包含数值/对象/动作） | "验证系统正常响应" | "余额=500时购买道具A（单价=200），验证购买成功，余额=300，道具A数量+1" |
| 2 | **title 必须是被测对象或场景**（不以「验证/测试/检查」开头）| "验证道具列表功能" | "余额充足时购买成功" |
| 3 | **preconditions 必须填具体初始状态**（禁止「无」「无特殊」占位）| preconditions: ["无"] | preconditions: ["玩家已登录游戏客户端", "余额=500游戏币", "道具A可购买"] |
| 4 | **每个数据点必须可断言**（数值/字符串/枚举/regex/range/exists） | "显示道具信息" | "道具名称='屠龙刀'，价格=500金币，数量=99" |
| 5 | **未读 S2 AC 不准动笔** | 直接生成 TP | 先 Read S2 `requirement_objects.json` 找到 fp_desc + verify_method + data_change 字段，提取具体数据点 |

### 反模式示例（任一命中 → 该 TP 不合格）

| 反模式 | 描述 |
|--------|------|
| 泛化描述 | "验证功能正常" / "业务流程正常" / "测试该功能" / "系统正常响应" |
| 模板语言 | "执行操作" / "执行测试" / "验证预期结果" / "准备符合XX的环境" |
| 占位文本 | preconditions = ["无"] / ["无特殊"] / ["无前置条件"] |
| 字段标题型 | title = "验证道具列表"（以测试动作开头，不是场景） |
| 复制粘贴型 | 多条 TP 的 description 高度相似（仅改 OBJ/FP 名） |

### Bad pattern 检测（强制阻断）

`L1S5Validator.validate_bad_patterns()` 自动检测上述反模式，任一命中即阻断（BLOCK 级别）。

调用入口：
```python
from ai_workflow.validators.l1_s5 import L1S5Validator
v = L1S5Validator()
errors = v.validate_bad_patterns(test_points)
# errors 非空 → 该 TP 不合格，必须重写
```

### 自检清单（生成 TP 后必走）

写完所有 TP 后，逐条检查：

- [ ] 每条 TP 的 description 都能让我（没看过 S2 的人）知道在测什么
- [ ] 每条 TP 的 title 都是场景式（不以动作动词开头）
- [ ] 每条 TP 的 preconditions 都有具体数据（数值/对象名）
- [ ] 不同 TP 的 description 没有「只改 OBJ 名，其他完全相同」的复制粘贴
- [ ] 我能就这条 TP 设计出至少 1 条 TC（含具体步骤和预期）

**任一项不通过 → 重写该 TP，再继续**。

---

# AIDocxWorkFlow S5 — 测试点生成

**独立阶段**：可单独调用。上游材料（S2 backlog）审查合格后开始，失败写失败报告。

## 第一原则

你当前不是在做代码实现，也不是在写最短答案，而是在做需求覆盖设计。
默认目标不是少写，而是找全；不是压缩，而是显式列出覆盖和未覆盖。
任何未设计成 TP 的点，必须进入 `omission_ledger.json`。

---

## 阶段入口

**触发**：`/aidocx-s5-test-points` 或粘贴 S2 backlog

**前置材料**：S2 backlog.md + S4 business_flow.md。详见 §1.4 必读材料清单。

**材料缺失时**：生成失败报告，停止 S5。

## 运行顺序（强制）

1. 先生成并读取 `stage_context.md` / `stage_context.json`
2. 再写 `read_ack.json`
3. 再输出 `coverage_ledger.json` 草稿
4. 再生成 `test_points.json`
5. 最后补全 `omission_ledger.json`

缺少前 3 步任一项，不允许开始正式 TP 设计。

---

## 8 模块测试类型（**模块 × 类型双维度必填**）

> ⚠️ 模块定义见 [`.cursor/MODULES.md`](../../../MODULES.md)（项目级唯一真相源）。
> 本文件不重写模块表。如模块定义调整，只改 MODULES.md。

### 测试类型枚举

> 完整定义见 [`.cursor/MODULES.md` §4 测试类型矩阵](../../../MODULES.md)。

### 1.2 模块归类 checklist（S5 单一可执行入口）

> **本节是模块归类的唯一执行入口。**
> 读完本节 = 完成全部归类决策（不等跳 6 个材料路径）。
> 详细边界 + 误判案例 → `O_boundary.md`（按需展开）。

#### Step 1：顶层二叉决策（8 选 1）

**沿问题选是/否，走到底命中模块。每个 TP 必须先走这一步。**

```
新业务元素 → ①是玩家可见界面元素？
  ├─ 是 → ②是页面常驻控件 还是事件触发临时提示？
  │       ├─ 常驻控件/样式/动画  → UI
  │       └─ 临时/飘字/红点/Toast → ③测样式 还是测内容？
  │               ├─ 样式/位置/动画 → UI
  │               └─ 内容/触发/文案  → HINT
  └─ 否 → ④是配置表字段 还是业务规则？
          ├─ 配置表/参数/价格表  → CONFIG
          └─ 业务规则/状态机/扣款 → ⑤常规业务流程 还是异常/对抗/边界？
                  ├─ 常规/协议/数据流 → BIZ
                  └─ 异常/对抗/弱网/反作弊 → SPECIAL

（新元素 → ⑥是底层通用工具 还是业务辅助？）
  ├─ 底层工具/SDK/加密/网络  → AUX
  └─ 业务辅助 → ⑦测行为轨迹 还是互通一致性？
          ├─ 埋点/审计/监控    → LOG
          └─ 跨服/跨端/外部三方 → LINK
```

#### Step 2：判定三问二次验证（命中后必做）

| 模块 | 判定三问 | 典型混淆 |
|---|---|---|
| **UI** | ①页面元素吗？②常驻还是临时？③测样式还是内容？ | — |
| **HINT** | ①事件触发还是常驻？②自动消失还是长期保留？③测内容还是样式？ | 易误标 UI（见下方 6 大误判） |
| **CONFIG** | ①字段还是规则？②配置还是热更？③字段校验还是业务逻辑？ | 易误标 BIZ |
| **BIZ** | ①服务端业务还是通用工具？②业务流程还是行为异常？③业务日志还是通用日志？ | 易误标 SPECIAL/CONFIG/AUX |
| **SPECIAL** | ①常规业务还是异常行为？②对抗还是正常？③底层还是业务？ | 易误标 BIZ |
| **AUX** | ①通用工具还是业务逻辑？②底层还是上层？③通用技术还是业务场景？ | 易误标 BIZ/LINK |
| **LINK** | ①跨服务/跨端？②互通协议还是底层传输？③一致性校验还是数据流？ | 易误标 AUX |
| **LOG** | ①业务日志还是通用日志？②审计还是埋点？③SDK还是业务规范？ | 易误标 BIZ |

**冲突处理**：Step1 命中 X，Step2 三问判定属于 Y → 以**三问判定为准**。

#### Step 3：命中多模块时——拆多 TP（不合并）

| 场景 | 拆法 |
|---|---|
| HINT + UI | 拆 HINT（内容）+ UI（样式）|
| BIZ + LINK | 拆 BIZ（业务）+ LINK（跨服同步）|
| BIZ + LOG | 拆 BIZ（业务）+ LOG（审计埋点）|
| SPECIAL + BIZ | 拆 SPECIAL（异常）+ BIZ（正常路径）|
| BIZ + CONFIG | 拆 BIZ（业务逻辑）+ CONFIG（配置表字段）|

#### Step 4：高频混淆边界（6 大误判，对照检查）

**HINT vs UI（最易混淆）**

| 场景 | 错标 | 正确归法 |
|---|---|---|
| Toast "购买成功" | UI | UI 测样式；HINT 测内容文案 |
| 红点显示/隐藏 | UI | UI 测图标样式；HINT 测显示逻辑 |
| 飘字 "+100 金币" | UI | UI 测轨迹动画；HINT 测数字内容 |
| 升级弹窗 | BIZ | BIZ 测状态机；HINT 测弹窗内容 |
| 新手引导高亮 | UI | UI 测遮罩样式；HINT 测引导内容；AUX 测步骤管理器 |
| 战斗暴击飘字 | UI | UI 测动画；HINT 测伤害数字内容 |

**核心原则**：HINT 测"内容/触发/文案"，UI 测"样式/位置/动画"。

**BIZ vs 其他**

| 场景 | 错标 | 正确归法 |
|---|---|---|
| 抽卡 | BIZ（1个）| BIZ 业务逻辑 + CONFIG 概率配置 + BIZ 状态机 + LOG 审计（4-5个TP）|
| 商城购买 | BIZ（1个）| BIZ 扣款发货 + BIZ 协议 + BIZ 状态机 + UI 渲染 + HINT 提示 + LOG 埋点（6个TP）|
| 网络断线 | BIZ | BIZ 断线业务处理 + SPECIAL 弱网降级 + AUX 断线重连（拆3个）|
| 充值 | BIZ | BIZ 订单流程 + LINK 第三方支付集成（拆2个）|

#### 产出要求

每个 TP 的 `applies_rule` 字段必须声明：
1. 走了 Step1 的哪个问题分叉（路径）
2. Step2 三问回答（确认无冲突）
3. 若命中多模块，说明 Step3 拆法
4. 对照 Step4 误判表（无冲突 → 记录"与误判 N 无冲突"）

---

## §related_tags 生成规则

> **SSOT**：`knowledge/public/module_templates/_related_tags_schema.md`

每条 TP 必须同时填写 `module`（主模块）+ `related_tags`（关联模块数组）。

### 规则速查

| 约束 | 说明 |
|------|------|
| R1 | `module` **必须**出现在 `related_tags` 中（自己关联自己）|
| R2 | `related_tags` 最多 **3 个**元素 |
| R3 | 元素**互异**（自动去重）|
| R4 | 枚举仅限 8 模块：`CONFIG / UI / BIZ / AUX / LINK / SPECIAL / LOG / HINT` |

### 扫描规则（每条 TP 生成前必走）

扫描该 TP 业务场景是否涉及**其他模块的验证点**：

| 场景 | 添加 related_tags |
|------|-----------------|
| BIZ 含日志验证 | 添加 `LOG` |
| BIZ 含配置读取 | 添加 `CONFIG` |
| BIZ 含第三方调用 | 添加 `LINK` |
| BIZ 含异常/对抗 | 添加 `SPECIAL` |
| UI 含服务端拉取数据 | 添加 `BIZ` |
| UI 含临时提示 | 添加 `HINT` |
| CONFIG 含解析/热更 | 添加 `BIZ` |
| 任意模块含跨服/跨端同步 | 添加 `LINK` |

### 正确 / 错误示例

```json
// ✅ 正确：module 在数组 + ≤ 3 个元素
{ "module": "BIZ", "related_tags": ["BIZ", "LOG", "CONFIG"] }

// ❌ 错误：module 不在数组
{ "module": "BIZ", "related_tags": ["LOG", "CONFIG"] }

// ❌ 错误：超过 3 个元素
{ "module": "BIZ", "related_tags": ["BIZ", "LOG", "CONFIG", "LINK", "SPECIAL"] }
```

### 旧 TP 兼容性

旧 TP（无 `related_tags` 字段）默认 `related_tags = []`，脚本校验不报错。

> **related_tags SSOT**：`knowledge/public/module_templates/_related_tags_schema.md`

> ⚠️ **违反本节禁令 → 产出不合格，必须补读后重新生成。**

### 违规认定（满足任一 → 产出不合格）

- ❌ 未读取本节材料，直接凭印象生成
- ❌ 跳过标注"强制"的材料，用其他来源替代
- ❌ 产出的 module / s4_reference 与材料内容明显不符
- ❌ 用"业务常识"替代必须读取的材料

### 必读材料清单

**生成任何 TP 前，必须先 Read 以下材料。禁止凭印象/常识/历史产物直接生成。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| ① | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| 所有 Epic/Story 必须有模块前缀；模块分类决定后续所有判断 |
| ② | 模块边界区分 | `.cursor/MODULES.md`（§3.5 快速归类表）| 8 模块边界容易混淆（尤其 HINT vs UI、BIZ vs CONFIG），判定前必须读取 |
| ③ | 命中模块概览 | `knowledge/public/module_templates/<Module>/<Module>.md` | 该模块的子类枚举和测试方法决定 TP 类型 |
| ④ | 命中模块边界文件 | `knowledge/public/module_templates/<Module>/O_boundary.md` | 边界对照表 + 误判案例（按需展开） |
| ⑤ | S4 业务流（强制） | `workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md` | 异常决策树和风险点清单是 EXCEPTION 类型 TP 的核心来源；未读取 → s4_reference 无法填写 |

**模块归类唯一入口 → §1.2 checklist（4 步 + 6 大误判表）。不再跳 _decision_tree.md 和 6 个 O_boundary 独立路径。**

**判定规则完整见** [MODULES.md §3.5](.cursor/MODULES.md) + [§4.11.2 HINT vs UI 边界](.cursor/MODULES.md)。

---

## 决策 push 块

> **哲学**：不告诉 LLM 多少算合格，告诉 LLM 怎么思考产出质量。
>
> ⚠️ **未走 Push 即写 TP → 该 TP 不合格。**

### 跨模块拆分 push

写 TP 前先问自己 3 问：

- Q1. 这个 Story 的"业务流"是单系统还是涉及上下游/第三方？（如购买涉及支付/订单/邮件）
- Q2. "业务流"的数据/状态变化会触发哪些 UI/HINT/LOG 反馈？
- Q3. 这个 Story 是否会暴露配置/缓存/异常/合规风险？

**3 问任一为"是"→ 必须为该模块单独生成 TP，不偷懒合并。**

### 4 步判定 push

每个 TP 写之前必走 4 步（任一空答 → 暂停，先补 Read）：

| # | 操作 | 目的 |
|---|------|------|
| Push 1 | 读 MODULES.md §3.5，找命中模块（8 选 1） | 确认模块归属 |
| Push 2 | 读命中模块的 `<MODULE>.md`，找命中子类 | 确认类型枚举 |
| Push 3 | 读命中模块的 `O_boundary.md`，确认不与相邻模块冲突 | 边界 guard |
| Push 4 | 读 S4 business_flow.json，找对应 **leaf_id**（`S4-XXX`）+ **risk_id_machine**（`R-XXX`） | 同时填写 `s4_reference` 的 leaf_id 和 R-ID；**BIZ 模块必须引用 R-ID** |

**4 步全部回答后，再开始写 TP。** LLM 必须在 TP JSON 的 `applies_rule` 字段里说明走了哪 4 步。

## 账本要求

- `coverage_ledger.json`：按 Story 记录 expected/covered scenario families、covered_by、status
- `omission_ledger.json`：记录所有 partial/uncovered 点和原因

默认场景族：
- `positive`
- `boundary`
- `negative`
- `exception`
- `config_change`
- `permission_role`
- `state_transition`
- `concurrency_timing`
- `recovery_rollback`
- `observability_hint_log`

如果某类场景不适用，必须写入 omission ledger，而不是直接不写。

### is_assumed 强制要求

> 定义见 [`.cursor/MODULES.md`](../../../MODULES.md)（全局强制）。

### 反例库强制对照

> 定义见 [`.cursor/MODULES.md`](../../../MODULES.md) 各模块 O_boundary.md。

### JSON Schema 字段名强约束

> 定义见各阶段 SKILL.md。

### 5 问质量 push

> ⚠️ **5 问任一空答 → TP 不合格，删除或重写。**

| # | 问题 |
|---|------|
| Q1 | 测什么（明确场景）？ |
| Q2 | 命中哪个模块 + 哪个子类（精确不模糊）？ |
| Q3 | 边界值/异常输入是什么（具体不抽象）？ |
| Q4 | 预期结果可验证吗（pass/fail 明确）？ |
| Q5 | 对应 S4 哪个节点（链路可追溯）？ | **BIZ 模块必填**：① leaf_id（`S4-XXX`）+ ② risk_id（`R-XXX`）；非 BIZ 模块填 leaf_id 即可 |

---

## 成功产出

路径：`workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json`

---

## 失败报告

路径：`workflow_assets/<req_name>/<version>/「S5 测试点生成」/fail_report_S5.md`

---

## 自动化支持

```python
from ai_workflow.test_case_formatter import compose_test_points_from_structure
breakdown = {'epics': [...], '_version': 'v1.0'}
skeleton = compose_test_points_from_structure(breakdown)
# skeleton 中每个 Story 仅含原始字段
# scenario_test_points: [] — LLM 按 §1.4 推理填入，4 类型必填 + s4_reference 必填

# 保存（LLM 手工 write_file）
# 输出: workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json
```

---

## §S3/S4→TP 字段溯源

> **SSOT**：本节是 §S3→TC 工作流 / §S4→BIZ TC 工作流 在 S5 阶段的落地条款。
> **历史 §TP 必须引用 feature_point 条款已停止生效**——S5 TP 必须按"模块来源"分类引用。

### 按模块来源的字段必填规则

| 模块 | 必填字段 | 上游来源 |
|------|---------|----------|
| **UI** | `s3_ref.page_id` | S3 `prototype.md` §UI 节点清单 |
| **UI** | `s3_ref.node_id` | S3 `prototype.md` §UI 节点清单（如 `P-002-button-01`）|
| **UI** | `s3_ref.node_type` | button / input / display / list / navigator / dialog / indicator |
| **BIZ** | `s4_ref.scenario_id` | S4 `business_flow.md` §4 层结构化清单（scenarios）|
| **BIZ** | `s4_ref.state_ref`（选填）| S4 状态机表（machine_id + state）|
| **BIZ** | `s4_ref.exception_ref`（选填）| S4 异常决策树叶子（tree_id + leaf_id）|
| **BIZ** | `s4_ref.risk_ref`（选填）| S4 风险点 ID |
| **CONFIG** | `obj_id` + `feature_point_id` | S2 `requirement_object.feature_points` |
| **LINK** | 同 CONFIG | 同 CONFIG |
| **LOG** | 同 CONFIG | 同 CONFIG |
| **SPECIAL** | 同 CONFIG | 同 CONFIG |
| **HINT** | 混合（HINT-UI 部分走 S3，HINT-BIZ 部分走 S4）| 视场景判定 |

### per-OBJ 4类型约束（v33 VC3-L4）

> **来源**: `DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3.3（`S5_DENSITY_OBJ_COVERAGE = 1.0`）

**规则**: 每个 OBJ 至少覆盖 4 种 TP 类型（POSITIVE + BOUNDARY + NEGATIVE + EXCEPTION），缺一必须有 `skip_reason`。

**操作步骤**:

1. **列出全部 OBJ**：从 S2 `requirement_objects.json` 列出所有 OBJ 的 `obj_id` + `obj_name`
2. **逐 OBJ 检查 4 类型**：
   - POSITIVE：正常路径（如"余额充足时购买成功"）
   - BOUNDARY：边界值（如"数量=99件最大购买数"）
   - NEGATIVE：无效输入（如"非法道具ID被拦截"）
   - EXCEPTION：异常分支（如"余额不足时订单失败"）
3. **缺失类型处理**：
   - 若某类型确实不适用 → 在对应 TP 加上 `"covered": false, "skip_reason": "out_of_scope"`
   - 若未设计 → 必须补设计
4. **自检**: `4类型齐全OBJ数 / OBJ总数 = density-OBJ` → 目标 100%

**示例**（v3.01 BIZ-001-001-OBJ-03）:

| 类型 | 是否覆盖 | TP 标题 | skip_reason |
|------|---------|---------|------------|
| POSITIVE | ✅ | "道具购买正向流程" | — |
| BOUNDARY | ✅ | "购买数量=99件边界" | — |
| NEGATIVE | ❌ | — | 需补充 |
| EXCEPTION | ✅ | "余额不足购买失败" | — |

**v3.01 实测**（230 TP / 36 OBJ）：
- 4类型齐全: 8 OBJ（22.2%）
- 缺 NEGATIVE: 28 OBJ（77.8%）
- 缺 BOUNDARY: 12 OBJ（33.3%）

### LLM 推理 3 步走（生成 TP 前）

1. **判定模块**：每个 Story → module 标签（UI/BIZ/CONFIG/...）
2. **列引用源**：
   - UI → 列 S3 prototype.md §UI 节点清单（page_id + node_id）
   - BIZ → 列 S4 business_flow.md §4 层结构化清单（scenario/state/exception/risk）
   - 其他 → 列 S2 requirement_objects.json OBJ/FP
3. **设计 TP**：每个引用源至少 1 个 TP，按场景穷举

### 字段示例

**UI TP**：
```json
{
  "tp_id": "TP-UI-P002-button-01-01",
  "module": "UI",
  "test_type": "POSITIVE",
  "title": "点击购买按钮 - 余额充足",
  "s3_ref": {
    "page_id": "P-002",
    "node_id": "P-002-button-01",
    "node_type": "button"
  }
}
```

**BIZ TP**：
```json
{
  "tp_id": "TP-BIZ-SC-001-01",
  "module": "BIZ",
  "test_type": "POSITIVE",
  "title": "正常购买游戏币道具 - 主流程",
  "s4_ref": {
    "scenario_id": "SC-001",
    "state_ref": "SM-001:待支付→已支付",
    "exception_ref": null,
    "risk_ref": null
  }
}
```

**CONFIG TP**：
```json
{
  "tp_id": "TP-CONFIG-FP-01-01",
  "module": "CONFIG",
  "obj_id": "CONFIG-001-001-OBJ-01",
  "feature_point_id": "CONFIG-001-001-OBJ-01-FP-1"
}
```

### 兼容性说明

- `feature_point_ref` / `fp_id` 字段对 UI/BIZ 模块不再强制——但 CONFIG/LINK/LOG/SPECIAL 仍保留
- 历史产出的 TC 暂不重生成（按需重新评估）

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S5_TEST_POINTS.mdc`
- Prompt 模板：`ai_workflow/prompts/test_point_gen.md`
- 测试点库：`knowledge/public/test_point_library/`

---

## §S5 出口预检（S7-lite 子集）

> **派生产物**：本节基于 §A.2 补充 1 + §D P2 拍板，于 2026-07-16 落地。
> **职责边界**（**严禁越界**——避免与 S7 正式审查双审）：
> - ✅ 本脚本做：ID 规范 / 必填字段 / 格式校验 / 引用完整性（脚本级可机检）
> - ❌ 不做：模块归属正确性（§1.2 checklist 是 LLM 责任）/ 测试覆盖率（S7 正式审查）/ 结构质量（S7 审查员 A）

### 调用方式

```bash
# 基础：只校验 ID + 必填字段
python3 ai_workflow/s5_exit_precheck.py <test_points.json>

# 完整：附加 S4 业务流引用完整性校验
python3 ai_workflow/s5_exit_precheck.py <test_points.json> <S4_business_flow.md>

# 调试：JSON 输出
python3 ai_workflow/s5_exit_precheck.py <test_points.json> --json

# 自测
python3 ai_workflow/s5_exit_precheck.py --self-test
```

### 退出码语义

| 退出码 | 含义 | 动作 |
|--------|------|------|
| `0` | PASS（含 warnings） | 可进入 S6 |
| `1` | BLOCKED（有 errors） | 必须修复后再进 S6 |
| `2` | 参数错误 | 重跑 |

### 校验规则（§D P2 拍板）

#### Errors（阻塞）

| 类型 | 校验 | 来源 |
|------|------|------|
| `MISSING_REQUIRED` | 必填字段缺失：`test_point_id` / `module` / `test_type` / `priority` / `description` | P0 标准 |
| `INVALID_ID_FORMAT` | `test_point_id` 必须匹配 `TP-NNN`（3+ 位数字） | test_points.json 现有惯例 |
| `INVALID_MODULE` | `module` 必须 ∈ {CONFIG, UI, BIZ, AUX, LINK, LOG, SPECIAL, HINT} | MODULES.md §1 |
| `INVALID_PRIORITY` | `priority` 必须 ∈ {P0, P1, P2} | P0 标准 |
| `DUPLICATE_ID` | `test_point_id` 全局唯一 | ID 唯一性 |
| `EMPTY` | 测试点数组为空 | S5 最低产出 |
| `NOT_DICT` | TP 条目不是 dict | schema 校验 |

#### Warnings（不阻塞）

| 类型 | 校验 | LLM 处理建议 |
|------|--------------|-------------|
| `S4_REFS_EMPTY` | S4 business_flow.md 无任何叶子节点 ID | 检查 S4 是否真的没产出 |
| `S4_REF_NOT_FOUND` | TP.s4_reference 在 S4 中找不到对应 ID | 业务实际：可能是新风险点未入 S4，按业务判断 |

### 与 S7 正式审查的边界

**S7-lite（本脚本）只做"脚本级可机检"**——避免双审：

| 项 | S7-lite | S7 正式审查 |
|----|---------|-------------|
| ID 规范 | ✅ 脚本校验 | ❌ 不重复 |
| 必填字段 | ✅ 脚本校验 | ❌ 不重复 |
| 引用完整性 | ⚠️ 仅格式（S4 是否存在） | ✅ 审查员 B 全覆盖判定 |
| 模块归属 | ❌ §1.2 checklist LLM 责任 | ✅ 审查员 B |
| 覆盖率统计 | ❌ | ✅ 审查员 B |
| 结构质量 | ❌ | ✅ 审查员 A |
| 优先级合理性 | ❌ | ✅ 审查员可推翻 S2 标注 |

> **关键**：S7-lite 通过 ≠ S7 审查通过。S7-lite 只是**预防性门禁**——避免 ID/字段错误拖延 S6 进度。

### 集成时机（S5 流程）

S5 生成的 5 步流程（§"运行顺序"）末尾加一步：

```
1. stage_context.md / stage_context.json
2. read_ack.json
3. coverage_ledger.json 草稿
4. test_points.json
5. omission_ledger.json
6. 【新增】s5_exit_precheck.py 跑通
   ↓ PASS → 进入 S6
   ↓ BLOCKED → 修复 errors → 重跑
```

### 自我测试

脚本内置 `def self_test()`，5 cases 全覆盖：
1. 合法样本 → PASS
2. 缺必填字段 → BLOCKED
3. ID 格式非法 → BLOCKED
4. 模块非法 → BLOCKED
5. 引用完整性警告 → PASS（warning 不阻塞）

`python3 ai_workflow/s5_exit_precheck.py --self-test`

---

## §TP 必须引用 feature_point

> **SSOT**：本节是 §FP 全覆盖门禁的 S5 落地条款。完整约束见 `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` §FP 必填 + OBJ 覆盖率继承。

### 字段必填

| 字段 | 必填 | 来源 |
|------|------|------|
| `scenario_test_points[].feature_point_ref` | **必填** | S2 `requirement_object.feature_points[].id` |
| `scenario_test_points[].tp_id` | **必填** | 模块内唯一（如 `UI-001-001-TP-001`） |

### LLM 自检 3 步走（生成 TP 前）

1. **列 FP**：从 S2 `requirement_objects.json` 列出**全部 87 个 FP** 的 `id` + `fp_desc`
2. **设计 TP**：为每个 FP 设计至少 1 个 TP，写明 `feature_point_ref`
3. **覆盖率自检**：`TP 引用的 FP 集合 == S2 FP 集合` → 通过；未通过的 FP 进入 omission_ledger + skip_reason

### TP 字段溯源

| 字段 | 上游来源 |
|------|----------|
| `feature_point_ref` | S2 OBJ.feature_points[].id |
| `s4_reference` | S4 业务流节点（已有必填） |
| `module` | 8 模块之一 |

### S5 → S6 链路条款

S6 TC 将通过 `s5_ref` 字段（指向 `tp_id`）回溯到 S5 TP。每个 TP 必须有唯一 `tp_id` 让 S6 TC 能 1:N 拓宽。

### 未覆盖 FP 的 skip_reason（5 类复用 OBJ 表）

| skip_reason | 含义 |
|---|---|
| `no_test_needed` | 该 FP 无可测场景 |
| `merged` | 已合并到其他 FP 的 TC |
| `manual_only` | 仅人工可测 |
| `deprecated` | 该 FP 已被废弃 |
| `unknown` | LLM 理解不了，需回溯 S2 澄清 |

---

## 执行卡（单阶段执行卡 — 4 区块合一）

<aside data-exec-card-block="input_gate" data-src=".cursor/rules/STAGE_S5_TEST_POINTS.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

> ⚠️ **派生产物，禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成
> src: `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` | synced_at: `2026-07-14`
> 修改请改源文件，然后跑 `python3 scripts/sync_execution_cards.py --stage s5-test-points` 重新同步。

### 输入门禁（input_gate）

| 必备材料 | 路径 | 缺失处理 |
|---|---|---|
| S2 backlog.md（必须） | `workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.md` | 生成 fail_report_S5.md，停止 |
| S4 business_flow.md（必须） | `workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md` | 同上 |
| 8 模块归类 checklist | 本 SKILL.md §1.2 | 4 步 checklist = 完整 SOP，不再跳 _decision_tree.md |

**触发命令**：`/aidocx-s5-test-points` 或粘贴 S2 backlog

</aside>

<aside data-exec-card-block="field_required" data-src=".cursor/rules/STAGE_S5_TEST_POINTS.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### 必填字段（field_required）

| 字段 | 级别 | 校验 |
|---|---|---|
| `tp_id` / `module` / `test_point_type` / `test_type_subclass` | **MUST** | 缺失 → check_field_completion.py 退出码 1 |
| `description` / `s4_reference` / `boundary` / `is_assumed` / `applies_rule` | **MUST** | 同上 |
| `feature_point_ref` | **MUST** | S2 FP.id 链路 |
| `assumption_reason` | **SHOULD** | is_assumed=true 时建议必填 |
| `requires_human_review` | **SHOULD** | 业务常识假设时建议必填 |
| `priority` / `tags` | **COULD** | 可选填 |

**SSOT**：`scripts/check_field_completion.py --stage s5`

</aside>

<aside data-exec-card-block="quality_gate" data-src=".cursor/rules/STAGE_S5_TEST_POINTS.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### 质量门禁（quality_gate）

| 门禁 | 阈值 | 说明 |
|---|---|---|
| TP 填写率（MUST） | 100% | 脚本自动校验 |
| TP 填写率（SHOULD） | ≥ 80% | 默认警告，可 --strict |
| OBJ 覆盖率 | 1.0（100%） | TP 引用的 OBJ / S2 OBJ 总数 |
| FP 覆盖率 | 1.0（100%） | TP 引用的 FP / S2 FP 总数 |
| 模块归属错误率 | ≤ 5%（目标） | 通过 §1.2 checklist 控制 |

**SSOT**：`DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.3 + §4.3

</aside>

<aside data-exec-card-block="naming" data-src=".cursor/rules/STAGE_S5_TEST_POINTS.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### ID 命名规范（naming）

| 层级 | 格式 | 示例 |
|---|---|---|
| 测试点 | `TP-{NNN}` | `TP-001`, `TP-002` |
| 模块前缀 | 8 模块全名 | `BIZ-`, `UI-`, `CONFIG-` |
| 输出文件 | `test_points.json` | 含 scenario_test_points 数组 |

</aside>
