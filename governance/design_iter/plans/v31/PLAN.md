# v31 — S5/S6 方法论重写正式 PLAN

> **Goal**: 重新设计 S5（测试点生成）+ S6（测试用例生成）方法论
> **Goal ID**: v31-s5-s6-methodology-rewrite-001
> **Round**: 4（落档正式 PLAN.md）
> **Date**: 2026-07-21
> **SSOT 引用**: `.cursor/MODULES.md` + `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` + `.cursor/rules/STAGE_S6_TEST_CASES.mdc` + `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3
> **验证样本**: 游戏道具商城系统 v3.01（16 Story / 36 OBJ / 99 FP / 25 risks / 66 leaves / 230 TP / 230 TC）
> **正式 PLAN.md 性质**: 本文件是 v31 重写项目的治理 SSOT；`v31_方法论_草案.md` 是演进草稿（保留作版本演进而非治理 SSOT）

---

## 1. 背景与诊断

### 1.1 现状（基于读取的事实）

| 维度 | 现状 | 依据 |
|------|------|------|
| 8 模块测试点模板 | 全部到位（CONFIG / UI / BIZ / UTIL / LINK / SPECIAL / LOG / HINT） | `knowledge/public/module_templates/<MODULE>.md` |
| 8 模块边界规则 | 全部到位 | `knowledge/public/module_templates/<MODULE>/<boundary>.md` |
| 测试点库（成品 TP 模板）| ⏳ 待补（v31 完成后激活入库机制） | `knowledge/public/test_point_library/` |
| S5/S6 STAGE 规则 | 已有完整规则 | `STAGE_S5_TEST_POINTS.mdc` / `STAGE_S6_TEST_CASES.mdc` |
| v3.01 S2 backlog | 已落档 | `workflow_assets/.../「S2 需求拆解」/backlog.json` |
| v3.01 S3 prototype | 已落档（11 page） | `「S3 原型导出」/prototype.json` |
| v3.01 S4 business_flow | 已落档（25 risks / 66 leaves / 31 branches） | `「S4 流程图导出」/business_flow.json` |
| 覆盖率验证工具 | `ai_workflow/coverage_validator.py` 已实现 | 已存在 |

### 1.2 用户 4 项反馈归纳（驱动 v31 重写）

| # | 用户诉求 | 现状缺口 | v31 治理方案 |
|---|---------|---------|-------------|
| **1** | S8 应把通过的 TP/TC 抽象化回灌到 TP 库 | S8 双段归档链路从未触发（v3.01 未走完 S5→S6→S7→S8）| §8 两段制归档契约 + `iteration.json#pending_candidates` 触发机制 |
| **2** | TC 字段必须严格对应 S2 OBJ/FP 条目，禁止模型自由发挥 | STAGE §字段语义规范仅约束命名继承，未约束语义继承 | §3.4 TC 字段语义收紧三条铁律 + `is_exploratory` 标注探索性 |
| **3** | TP ≤ 50/Story 硬上限不合理 | STAGE §1.5 硬上限对复杂业务场景严重低估 | §2.5 SCC 公式动态估算（5 维度乘积 + 软下限）|
| **4** | 通用性、可复用性、越用越成长 | TP 库为空 + 模块子类表无 SSOT 索引 | §4 子类表引 SSOT 不重写 + §8.6 TP 库激活阈值（≥ 10 条）|

### 1.3 与既有规则的不重复声明

| 本文件 § | 不重写（SSOT 维持） |
|---------|-------------------|
| §2 / §3 输入契约 | `STAGE_S5_TEST_POINTS.mdc` §输入要求 + `STAGE_S6_TEST_CASES.mdc` §输入要求 |
| §2.2 / §3.2 输出契约 | `STAGE_S5_TEST_POINTS.mdc` §必填字段 + `STAGE_S6_TEST_CASES.mdc` §字段语义 |
| §4 模块边界 | `module_templates/<MODULE>/<boundary>.md` |
| §4 子类枚举 | `module_templates/<MODULE>.md` + `test_point_library/<MODULE>/README.md` |
| §6 覆盖率阈值 | `DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 |
| §7 公共表头 | `ai_workflow/test_case_formatter.py` `_XLSX_HEADERS_V3` |
| §7 格式违规清单 | `.cursor/rules/product_format_rules.yaml` |

> **本文件的增量价值**在 §2.5（SCC）+ §3.4（TC 语义收紧）+ §8（S8 回灌契约）+ §6（覆盖率自检口径）——这是 STAGE 规则未明确的部分。

---

## 2. 输入契约

### 2.1 S5 必读材料清单

```
[必读]
1. workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.json
   → 字段：epics[].id, epics[].stories[].id, epics[].stories[].title,
          epics[].stories[].acceptance_criteria, epics[].stories[].preconditions,
          epics[].stories[].scope_module
2. workflow_assets/<req_name>/<version>/「S2 需求拆解」/requirement_objects.json
   → 字段：objects[].obj_id, objects[].obj_name, objects[].feature_points[].fp_id,
          objects[].feature_points[].fp_name, objects[].feature_points[].fp_desc,
          objects[].feature_points[].input, objects[].feature_points[].normal_flow,
          objects[].feature_points[].exception_flow
3. workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.json
   → 字段：risks[].risk_id_machine, exception_tree_leaves[].leaf_id,
          exception_tree_leaves[].epic_id, risk_to_leaves_mapping
4. （可选，UI/HINT 模块推荐）workflow_assets/<req_name>/<version>/「S3 原型导出」/prototype.json

[按需读]
5. .cursor/MODULES.md（模块定义 SSOT，必读）
6. knowledge/public/module_templates/<MODULE>.md（按 story.scope_module 命中）
7. knowledge/public/module_templates/<MODULE>/O_boundary.md（命中边界判定时）
8. knowledge/public/test_point_library/<MODULE>/<subclass>.md（TP 库）
```

### 2.2 S6 必读材料清单

S6 必读材料 = S5 必读 + S5 产物 `test_points.json`（每条 TP 含 `module / obj_id / feature_point_ref / test_point_type / s4_reference / applies_rule / is_assumed`）。

### 2.3 字段溯源规则（DNA §9.4 Q1 三子问）

每次生成下游产物时必答：

| 子问 | 答 |
|------|---|
| Q1.1 字段值的上游来源是哪？ | `<OBJ.id / Story.id / TP.id / 其他>` |
| Q1.2 上游材料是否提供了该字段？ | `<有/无>` |
| Q1.3 我是否已 Read 上游文件并验证过该字段存在？ | `<已读且匹配 / 未读 / 读到但未匹配>` |

**未答"已读且匹配" → 不得开始下游生成**。

---

## 3. 方法论

### 3.1 S5 方法论（测试点生成）

#### 3.1.1 输入 → 推理 → 输出

```
[Input] S2 backlog + requirement_objects + S4 business_flow（+ 可选 S3 prototype）
    ↓
[Reasoning]
  1. 读 scope_module → 决定主 module（多 module 时按 MODULES.md §3.6 冲突矩阵判定）
  2. 读每个 FP → 决定 module.subclass（按 §4 关键词命中规则）
  3. 读 FP.verification_method + flow 类型 → 决定 test_point_type（POSITIVE / BOUNDARY / NEGATIVE / EXCEPTION）
  4. 命中 S4 风险点 → 填 s4_reference（leaf_id，间接覆盖 risk_id）
  5. 命中 S4 异常叶子 → 填 scenario_test_points
  6. 计算 SCC（§3.1.3） → 估算 TP 数量
  7. 输出 description（人话、≤ 80 字）
    ↓
[Output] test_points.json（每 TP 含 §3.1.2 字段）
```

#### 3.1.2 TP 字段契约（STAGE_S5 §1.6 + §1.9 双源 SSOT）

| 字段 | 类型 | 取值约束 | 上游来源 |
|------|------|---------|----------|
| `tp_id` | string | `{StoryID}-TP-NNN`（3 位零填充） | S2 story.id |
| `module` | enum(8) | 8 模块全名 | `STORY.scope_module` ∩ `MODULES.md §1` |
| `obj_id` | string | S2 OBJ.obj_id | `requirement_objects.json` |
| `obj_name` | string | == S2 OBJ.obj_name（100% 严格相等）| `requirement_objects.json#objects[].obj_name` |
| `feature_point_ref` | string | S2 FP.id | `requirement_objects.json#objects[].feature_points[].fp_id` |
| `fp_name` | string | LLM 自创中文中性功能名 | LLM 自创（≠ S2 fp_desc 字面量）|
| `case_type` | string | `功能测试` / `接口测试` / `性能测试` 等 | LLM 自决 |
| `test_method` | array<string> | ≥ 1 | LLM 自决 |
| `test_point_type` | enum(4) | `POSITIVE` / `BOUNDARY` / `NEGATIVE` / `EXCEPTION` | FP 类型推导 |
| `title` | string | ≤ 50 字，4-12 字简短场景摘要 | LLM 自创（不带锚点）|
| `description` | string | ≤ 80 字，纯测试逻辑 | LLM 自创（不带锚点）|
| `priority` | enum(4) | `P0` / `P1` / `P2` / `P3` | S2 story.risk_level |
| `status` | enum(4) | `Draft` / `Ready` / `Rejected` / `Deprecated` | 默认 `Draft` |
| `s4_reference` | string | S4 leaf_id（如 `S4-UI-001-1.2.1`）| `business_flow.json#exception_tree_leaves[].leaf_id` |
| `boundary` | string | 具体边界值或"无" | LLM 推断 |
| `is_assumed` | bool | 上游缺失时 true | 默认 false |
| `assumption_reason` | string | is_assumed=true 时必填 | LLM 自决 |
| `applies_rule` | string | 4 步判定 + 反例对照结果 | LLM 必填 |

#### 3.1.3 SCC（Story Complexity Coefficient）

> **来源**：`v31_SCC.md`（独立文件，§6.4 SSOT 引用）

**核心公式**：
```
SCC = |actors| × |states| × |timings| × |boundaries| × |exceptions|
理论 TP 数 = SCC × TP_TYPE_FACTOR
TP_TYPE_FACTOR = { POSITIVE: 1.5, BOUNDARY: 1.0, NEGATIVE: 1.0, EXCEPTION: 0.5 }
软下限 = 理论 TP 数 × 0.8
```

**维度 S2 字段映射**：

| 维度 | S2 字段来源 |
|------|-------------|
| actors | `requirement_objects.json#objects[].scene` 中独立主体数 |
| states | `requirement_objects.json#objects[].feature_points[].normal_flow` 状态节点 |
| timings | `backlog.json#stories[].acceptance_criteria[]` 步骤数 + FP 时序节点 |
| boundaries | `requirement_objects.json#objects[].feature_points[].input` 数值范围 + 显式边界 |
| exceptions | `requirement_objects.json#objects[].feature_points[].exception_flow[]` + S4 `exception_tree_leaves[]` |

#### 3.1.4 S5 LLM Prompt 模板

```text
# Role
你是 S5 测试点生成 LLM。基于 S2 + S4 输入材料输出 test_points.json。

# Output contract（每个 TP）
| 字段 | 规则 |
| tp_id | {StoryID}-TP-NNN，3 位零填充 |
| module | 8 选 1，按 §4 模块子类映射 |
| obj_id / obj_name | 100% == S2 OBJ |
| feature_point_ref / fp_name | FP.id 必填，fp_name LLM 自创 |
| test_point_type | POSITIVE / BOUNDARY / NEGATIVE / EXCEPTION |
| title | ≤ 50 字，4-12 字简短场景摘要（不带锚点）|
| description | ≤ 80 字，纯测试逻辑（不带锚点）|
| priority | P0/P1/P2/P3（P0 = 阻塞主流程）|
| s4_reference | S4 leaf_id |
| applies_rule | 4 步判定 + 反例对照结果 |
| is_assumed / assumption_reason | 上游缺失时 true + 必填 reason |

# Reasoning steps（必填）
1. 该 Story 的主 module 是？理由？
2. 命中哪些 FP？每个 FP 派生什么 test_point_type？
3. 引用了哪些 S4 叶子（间接覆盖风险点）？
4. 哪些字段是 is_assumed？假设依据？

# Forbidden
- 禁止编造 OBJ.id / FP.id
- 禁止 LLM 自创 obj_name
- 禁止 fp_name 与 S2 fp_desc 字面量重复

# Self-check before output
□ obj_id 在 requirement_objects.json 实际存在
□ feature_point_ref 在 OBJ.feature_points[] 实际存在
□ s4_reference 在 business_flow.json 实际存在
□ 每个 Story 的 TP 数 ≥ SCC 软下限（§3.1.3）
```

### 3.2 S6 方法论（测试用例生成）

#### 3.2.1 输入 → 推理 → 输出

```
[Input] S5 test_points.json + S2/S3/S4 上游材料
    ↓
[Reasoning]
  1. 取 TP.test_point_type → 决定 scenario
  2. 取 TP.title → 拆为 steps[].action
  3. 取 TP.description → 拆为 expected_results
  4. 取 TP.precondition → 拆为 preconditions[]
  5. 取 TP.obj_id + TP.feature_point_ref → 填 TC.obj_id + feature_point_id
  6. 校验 TC.用例描述 ∈ S2 Epic.title（铁律 A）
  7. 校验 TC.功能描述 ∈ S2 Story.title（铁律 B）
  8. 生成 case_id = {Module}-TC-NNN
    ↓
[Output] test_cases.json（每 TC 含 §3.2.2 字段）
```

#### 3.2.2 TC 字段契约（STAGE_S6 §字段语义规范 + v31 扩展）

| 字段 | 类型 | 取值约束 | 上游来源 |
|------|------|---------|----------|
| `case_id` | string | `{Module}-TC-NNN`（3 位零填充） | `module` + 序号 |
| `模块` | enum(8) | 8 模块全名 | TP.module |
| `用例描述` | string | **100% 严格相等 S2 Epic.title** | S2 `backlog.epics[].title` |
| `功能描述` | string | **100% 严格相等 S2 Story.title** | S2 `backlog.epics[].stories[].title` |
| `前置条件` | string | 具体数值，禁止模糊 | TP + LLM 推导 |
| `steps` | array<{step_num:int, action:string}> | ≥ 1 元素 | TP.title + LLM 推导 |
| `expected_results` | array<string> | ≥ 1 元素 | TP.description + LLM 推导 |
| `优先级` | enum(4) | `P0` / `P1` / `P2` / `P3` | TP.priority |
| `用例状态` | enum(4) | `Draft` / `Ready` / `Rejected` / `Deprecated` | L1∧L2 校验后写回 |
| `备注` | string | 边界条件、测试数据要求 | LLM 自决 |
| `obj_id` | string | S2 OBJ.obj_id | TP.obj_id |
| `feature_point_id` | string | S2 FP.fp_id | TP.feature_point_ref |
| `s5_ref` | string | TP.tp_id（必填） | S5 `test_points.json` |
| **v31 扩展字段** | — | — | — |
| `is_exploratory` | bool | true/false | TC.功能描述关键词 ⊈ OBJ∪FP 时为 true |
| `exploratory_reason` | string | is_exploratory=true 时必填 | LLM 自决 |
| `verified_against_s2_path` | string | S2 OBJ/FP 校验路径 | DNA Q1.1 字段溯源 |
| `module_boundary_check` | object | `{checked_against, conflict_with, verdict}` | MODULES.md §4 校验 |
| `ssot_citation_path` | string | STAGE_S6 §字段语义规范路径 | DNA Q1.1 字段溯源 |

#### 3.2.3 TC 字段语义收紧三条铁律（§3.4）

| 铁律 | 规则 | 违规处理 |
|------|------|---------|
| **铁律 A** | `用例描述` == `S2 backlog.epics[].title`（严格相等） | 违规 → 强制改写 |
| **铁律 B** | `功能描述` ∈ `S2 backlog.epics[].stories[].title`（严格相等） | 违规 → 强制改写 |
| **铁律 C** | `obj_id` ∈ TP.obj_id + `feature_point_id` ∈ TP.feature_point_ref | 违规 → 强制回退到 TP 的字段值 |

**判断方法**（LLM 自检）：
1. 从 S2 提取 `epic_title_set = {epic.title}` + `story_title_set = {story.title}`
2. 对每 TC：
   - `用例描述 ∈ epic_title_set`？否 → 强制改写
   - `功能描述 ∈ story_title_set`？否 → 强制改写
   - `obj_id ∈ TP.obj_id`？否 → 回退到 TP
3. 探索性测试：`is_exploratory=true` + `exploratory_reason` 说明 + `suggested_obj` + `suggested_fp`

#### 3.2.4 S6 LLM Prompt 模板

```text
# Role
你是 S6 测试用例生成 LLM。基于 S5 test_points.json + 上游材料输出 test_cases.json。

# Output contract（每 TC）
| 字段 | 规则 |
| case_id | {Module}-TC-NNN |
| 模块 | 8 模块全名 |
| 用例描述 | 100% == S2 Epic.title（铁律 A）|
| 功能描述 | 100% == S2 Story.title（铁律 B）|
| 前置条件 | 具体数值 |
| steps | [{step_num, action}] |
| expected_results | 与 steps 一一对应 |
| 优先级 | 继承 TP.priority |
| obj_id | 继承 TP.obj_id（铁律 C）|
| feature_point_id | 继承 TP.feature_point_ref |
| s5_ref | TP.tp_id 必填 |
| is_exploratory / exploratory_reason | 探索性测试标注 |
| verified_against_s2_path | S2 OBJ/FP 路径 |
| module_boundary_check | 边界对照结果 |
| ssot_citation_path | STAGE_S6 引用路径 |

# Reasoning steps
1. 该 TP 派生几个 TC？边界 3 条；其他 1 条
2. 每 TC 的 steps 如何拆分？
3. 每步的 expected 如何判定？
4. 是否需要 is_exploratory 标注？

# Forbidden
- 禁止编造 OBJ.id / FP.id
- 禁止用例描述/功能描述含 LLM 自由发挥
- 禁止 s5_ref 为空

# Self-check
□ 用例描述 ∈ epic_title_set（铁律 A）
□ 功能描述 ∈ story_title_set（铁律 B）
□ obj_id ∈ TP.obj_id（铁律 C）
□ feature_point_id ∈ TP.feature_point_ref
□ s5_ref 在 test_points.json 实际存在
□ 无模板语言（无"执行操作："/"验证预期结果"）
```

### 3.3 S5 → S6 链路规则

| 关系 | 规则 |
|------|------|
| TC.case_id → TP | `{Module}-TC-NNN`，独立命名空间 |
| TC.模块 → TP.module | 完全继承 |
| TC.优先级 → TP.priority | 完全继承 |
| TC.obj_id → TP.obj_id | 完全继承（铁律 C） |
| TC.feature_point_id → TP.feature_point_ref | 完全继承 |
| TC.s5_ref → TP.tp_id | 必填，1:1 反向引用 |
| TC.用例描述 → S2 Epic.title | 严格相等（铁律 A） |
| TC.功能描述 → S2 Story.title | 严格相等（铁律 B） |
| TC.用例状态 | L1∧L2 校验后由 `case_status_writer` 写回（per-case 决策） |

---

## 4. 模块 × 子类映射（SSOT 引而不重写）

### 4.1 模块判定（8 模块第一层）

| 命中信号 | 主 module |
|---------|----------|
| 配置表字段、枚举、资源、ID、热更、解析、数值公式、版本兼容 | CONFIG |
| 页面、控件、按钮、输入框、列表、布局、分辨率、动效、皮肤 | UI |
| 业务逻辑、扣款发货、合成、抽卡、保底、限购、概率、状态机、并发、付费、审计 | BIZ |
| 工具、组件、路由、缓存、Redis、资源加载、网络、SDK、加密、崩溃、GM | UTIL |
| 上下游、跨服务、跨服、多端、外部 SDK、第三方登录、异步消息、灰度 | LINK |
| 弱网、断网、高频包、反作弊、切后台、宕机、版本兼容异常、渠道灰度 | SPECIAL |
| 埋点、点击事件、资产流水、崩溃日志、日志分级、脱敏、trace、监控 | LOG |
| 红点、飘字、Toast、弹窗、浮窗、倒计时、新手引导、社交提示、状态变更 | HINT |

### 4.2 子类判定（按 module 内部）

> **SSOT 引而不重写**——本节只列出模块→子类索引，**完整子类枚举见 `knowledge/public/module_templates/<MODULE>.md`**：

| module | 子类枚举索引 | SSOT 路径 |
|--------|-------------|-----------|
| CONFIG | 9 子类（A-I：FIELD_LEGALITY / FIELD_INTRA_DEP / FIELD_CROSS_DEP / RELOAD_4_MODE / PARSE_LOAD / VERSION_COMPAT / VALUE_LOGIC / EXPORT_PUBLISH / SERVER_CONFIG）| `knowledge/public/module_templates/CONFIG.md` |
| UI | 11 子类（A-H：CONTROL_RENDER / CONTROL_STATE / PURE_INTERACTION / LAYOUT_ADAPT / STATIC_DISPLAY / ANIMATION / GUIDE_HINT / ACCESSIBILITY / EDGE_UI 等）| `knowledge/public/module_templates/UI.md` |
| BIZ | 9 子类（A-I：BIZ_LOGIC / BIZ_DATA_FLOW / BIZ_PROTOCOL / BIZ_STATE_MACHINE / BIZ_DB_PERSIST / BIZ_CONCURRENCY / BIZ_SCHEDULED_TASK / BIZ_PAYMENT / BIZ_AUDIT_LOG）| `knowledge/public/module_templates/BIZ.md` |
| UTIL | 14 子类（A-N）| `knowledge/public/module_templates/UTIL.md` |
| LINK | 6 子类（A-F）| `knowledge/public/module_templates/LINK.md` |
| SPECIAL | 9 子类（A-I）| `knowledge/public/module_templates/SPECIAL.md` |
| LOG | 13 子类（A-M）| `knowledge/public/module_templates/LOG.md` |
| HINT | 13 子类（A-M）| `knowledge/public/module_templates/HINT.md` |

### 4.3 关键词快速映射表

| 关键词 | module | subclass |
|--------|--------|----------|
| 购买 / 支付 / 订单 / 扣款 / 发货 / 退款 | BIZ | A_biz_logic / H_payment |
| 限时 / 折扣 / 满减 / 促销 / 礼包 | BIZ | A_biz_logic / G_scheduled_task |
| 风控 / 反作弊 / 弱网 / 封禁 / 自动化 | SPECIAL | A_weak_net / B_risk |
| 列表 / 详情 / 搜索 / 控件 / 弹窗 | UI | A_control_basic / B_pure_interaction |
| 跨服务 / 异步 / 回调 / 第三方 | LINK | A_cross_service |
| 日志 / 埋点 / 审计 / 流水 | LOG | A_click / B_asset_log / C_crash_log |
| 红点 / 飘字 / Toast / 引导 | HINT | A_red_dot / B_toast / C_popup |
| 配置 / 资源 / 热更 / 数值表 | CONFIG | A_field_legality / D_hot_reload / G_value_logic |
| 缓存 / SDK / 加密 / 网络 / GM | UTIL | A_util / B_sdk / C_crypto |

### 4.4 冲突优先级矩阵

| # | 冲突 | 优先级 |
|---|------|--------|
| 1 | 异常/对抗 vs 常规业务 | SPECIAL > BIZ/UI |
| 2 | 跨服务 vs 业务逻辑 | LINK > BIZ |
| 3 | 配置驱动 vs 业务逻辑 | CONFIG > BIZ |
| 4 | 纯日志 vs 业务附带日志 | 纯 LOG / 附 BIZ |
| 5 | 红点/弹窗样式 vs 内容触发 | 样式 UI / 触发 HINT |
| 6 | 辅助功能 vs 业务功能 | UTIL < BIZ（业务优先）|
| 7 | 关联影响 vs 主业务 | LINK 独立 / BIZ 主归 |
| 8 | 特殊配置 vs 配置通用 | SPECIAL > CONFIG |

---

## 5. 推导规则（S5 → S6 by module × subclass）

### 5.1 推导原则

| TP 类型 | TC 派生规则 | 典型 TC 数 |
|---------|-----------|----------|
| POSITIVE | 1 个 TC（标准操作）| 1 |
| BOUNDARY | 1~3 个 TC（min/max/边界+1）| 1~3 |
| NEGATIVE | 1 个 TC（异常输入 + 错误码断言）| 1 |
| EXCEPTION | 1~N 个 TC（按异常路径数量）| ≥ 1 |

### 5.2 按 module 的 TC 字段填充重点

| module | TC 字段填充重点 |
|--------|----------------|
| BIZ | steps.action 引用具体 API 路径；expected_results 引用业务状态 + 错误码 |
| UI | steps.action 引用具体控件 ID + 交互手势；expected_results 引用 UI 状态变化 |
| CONFIG | steps.data 引用具体配置项 ID / 字段值；expected_results 引用配置 schema 验证结果 |
| LINK | steps.data 引用跨服务 RPC + 消息 ID；expected_results 引用跨端一致性 + 回调幂等 |
| SPECIAL | steps.data 引用异常注入方式（弱网、改包、切后台）；expected_results 引用异常拦截 + 降级行为 |
| LOG | steps.data 引用触发动作；expected_results 引用日志字段必填 + 脱敏 + trace 串联 |
| HINT | steps.action 引用触发场景；expected_results 引用提示内容 + 触发时机 + 自动消失 |
| UTIL | steps.data 引用底层 SDK 调用参数；expected_results 引用 SDK 返回值 |

---

## 6. 覆盖率计算公式

### 6.1 OBJ 覆盖率

```
OBJ 覆盖率 = TP 集合引用的 OBJ 总数 / S2 OBJ 总数
分母 = requirement_objects.json#objects 长度 = 36
分子 = ∪(test_points.json#scenario_test_points[].obj_id) 长度
阈值（SSOT §4.3 S5_OBJ_COVERAGE = 1.0）
```

### 6.2 FP 覆盖率

```
FP 覆盖率 = TC 集合引用的 {obj_id, feature_point_id} 对总数 / S2 FP 总数
分母 = ∑(objects[].feature_points.length) = 99
分子 = ∪({(tc.obj_id, tc.feature_point_id) for tc in test_cases})
阈值（SSOT §4.3 S5_FP_COVERAGE = 1.0）
```

### 6.3 S4 异常叶子覆盖率

```
异常叶子覆盖率 = TP 引用的 leaf 数 / S4 异常叶子总数
分母 = business_flow.json#exception_tree_leaves 长度 = 66
分子 = ∪(test_points.json#scenario_test_points[].s4_reference) 长度
阈值（SSOT §4.3 S4_ANOMALY_COVERAGE = 1.0）
```

### 6.4 S4 风险点覆盖率（经叶子映射）

```
风险点覆盖率 = 经叶子推导的 risk 数 / S4 风险点总数
分母 = business_flow.json#risks 长度 = 25
分子 = {risk_id for leaf in tp_leaves for risk_id in risk_to_leaves_mapping[leaf]}
```

### 6.5 计算实现

**SSOT**：`ai_workflow/coverage_validator.py`（已实现 §6.1-6.4 计算）。

**Round 4 实测结果**（v3.01 样本）：

| 指标 | 实测 | 阈值 | 判定 |
|------|------|------|------|
| OBJ 覆盖率 | 36 / 36 = 100% | 100% | ✅ |
| FP 覆盖率 | 99 / 99 = 100% | 100% | ✅ |
| S4 异常叶子覆盖率 | 66 / 66 = 100% | 100% | ✅ |
| S4 风险点覆盖率（经叶子）| 25 / 25 = 100% | ≥ 95% | ✅ |

详细报告：`governance/design_iter/plans/v31/coverage_report.md`

---

## 7. 格式契约（公共表头 _XLSX_HEADERS_V3）

### 7.1 XLSX 表头（10 列）

```python
_XLSX_HEADERS_V3 = [
    '用例ID', '模块', '用例描述', '功能描述', '前置条件',
    '操作步骤', '预期结果', '优先级', '用例状态', '备注'
]
```

**SSOT**：`ai_workflow/test_case_formatter.py` `_XLSX_HEADERS_V3`。

### 7.2 JSON 契约

```json
{
  "meta": { "req_name", "stage": "S5/S6", "version", "created_at" },
  "summary": { "story_count", "total_test_points"/"case_count" },
  "stories" / "test_cases": [/* TP/TC 对象数组 */]
}
```

### 7.3 Markdown 契约（项目级导出）

```
| 用例ID | 模块 | 用例描述 | 功能描述 | 优先级 | 状态 |
| --- | --- | --- | --- | --- | --- |
```

### 7.4 格式违规清单（SSOT: `.cursor/rules/product_format_rules.yaml`）

- ❌ 双版本标签（如 `v2`、`v3.01` 出现在字段值）
- ❌ 永久规范版本标记（如 `版本号+新增`）
- ❌ 禁止 JSON 字段（如 `{field:"..."}` 内嵌版本/变更）
- ❌ ISO 时间戳（如 `YYYY-MM-DDTHH:MM:SS+HH:MM`）
- ✅ 业务事实描述归口 `CHANGELOG.md`

---

## 8. S8 回灌 TP 库契约

### 8.1 根因诊断（v31 期新增）

**TP 库为空的根因**："S8 的双段归档链路从未被触发"——v3.01 未执行 S7 → 无 S8 输入 → 无归档触发。

### 8.2 两段制归档链路

```
S8 识别 must_fix/should_fix 根因
    ↓
[第 1 段] 写入 knowledge/project_local/.review_queue/<Module>/<Subclass>__<defect_id>__<date>.md
    ↓
[人工审核] iteration.json#pending_candidates 触发 → 人工阅读候选 → 通过/拒绝
    ↓
[第 2 段] 通过 → 回写 knowledge/public/test_point_library/<MODULE>/<Subclass>.md
    ↓
TP 库累计条目 → S5 生成时优先复用 → tpl_id + usage_count++
```

### 8.3 iteration.json#pending_candidates 字段定义

```json
{
  "iteration_number": 1,
  "verdict": "PASS",
  "review_queue_triggered": true,
  "pending_candidates": [
    {
      "path": "knowledge/project_local/.review_queue/BIZ/A_biz_logic__ITER-012__2026-07-21.md",
      "module": "BIZ",
      "subclass": "A_biz_logic",
      "defect_id": "ITER-012",
      "root_cause_source": "S5_MODULE",
      "created_at": "2026-07-21T00:00:00+08:00",
      "requires_human_review": true,
      "target_public_file": "knowledge/public/module_templates/BIZ/O_boundary.md"
    }
  ],
  "next_iteration_focus": []
}
```

**触发流程**：
1. S8 写入 `.review_queue/` 候选文件
2. S8 iteration.json 自动填 `review_queue_triggered: true` + `pending_candidates: [...]`
3. 项目流程约定（人工）定期检查 `iteration.json#pending_candidates`
4. 审核通过 → 回写 `test_point_library/` + `tpl_id` 登记
5. 审核拒绝 → 标记 `rejected`，由 S8 下一轮迭代处理

### 8.4 TP 库激活阈值

当 `test_point_library/<MODULE>/` 累计 ≥ 10 个有效条目时，激活"自动复用"机制：
```
S5 生成 TP 前：
1. 在 test_point_library/ 中匹配相同 module + subclass + test_point_type 的条目
2. 匹配成功 → 复用模板 + 填入当前需求特定信息 + tpl_id + usage_count++
3. 匹配失败 → 从 module_templates 生成新 TP
```

### 8.5 与 recurring_failures.json 的区别

| 维度 | recurring_failures.json | test_point_library/ |
|------|------------------------|---------------------|
| 写入者 | `recurring_failures.py`（S8 聚合）| 人工审核后回写 |
| 位置 | `workflow_assets/_governance/` | `knowledge/public/` |
| 性质 | 项目内本地失败模式记录 | 公共可复用 TP 模板 |
| 用途 | 防止同类错误重复出现 | 供后续需求 S5 生成时复用 |

### 8.6 SSOT 引用

- S8 SKILL.md：`.cursor/skills/aidocx-s8-self-iteration/SKILL.md`
- STAGE_S8：`.cursor/rules/STAGE_S8_SELF_ITERATION.mdc`
- TP 库入库标准：`knowledge/public/test_point_library/README.md`
- 根因诊断：`governance/design_iter/plans/v31/s8_knowledge_backflow_diagnosis.md`

---

## 9. 字段字典（SSOT 索引）

### 9.1 TP 字段字典

| 字段 | 类型 | 必填 | 来源 | 备注 |
|------|------|------|------|------|
| `tp_id` | string | MUST | S2 story.id | `{StoryID}-TP-NNN` |
| `s5_ref` | string | MUST | == tp_id | 反向引用别名 |
| `module` | enum(8) | MUST | scope_module | 8 模块全名 |
| `obj_id` | string | MUST | requirement_objects | 必填 |
| `obj_name` | string | MUST | == S2 OBJ.obj_name | 100% 严格相等 |
| `feature_point_ref` | string | MUST | S2 OBJ.feature_points[].fp_id | 必填 |
| `fp_name` | string | MUST | LLM 自创 | 不与 S2 fp_desc 字面量重复 |
| `case_type` | string | MUST | LLM | 功能测试/接口测试/... |
| `test_method` | array | MUST | LLM | ≥ 1 |
| `test_point_type` | enum(4) | MUST | FP 推导 | POSITIVE/BOUNDARY/NEGATIVE/EXCEPTION |
| `title` | string | MUST | LLM | ≤ 50 字，不带锚点 |
| `description` | string | MUST | LLM | ≤ 80 字，不带锚点 |
| `priority` | enum(4) | MUST | S2 risk_level | P0/P1/P2/P3 |
| `status` | enum(4) | MUST | 默认 Draft | |
| `s4_reference` | string | MUST | S4 leaf_id | |
| `boundary` | string | MUST | LLM | 具体值或"无" |
| `is_assumed` | bool | MUST | 默认 false | |
| `applies_rule` | string | MUST | LLM | 4 步判定 + 反例对照 |

### 9.2 TC 字段字典

| 字段 | 类型 | 必填 | 来源 | 备注 |
|------|------|------|------|------|
| `case_id` | string | MUST | module + 序号 | `{Module}-TC-NNN` |
| `模块` | enum(8) | MUST | TP.module | |
| `用例描述` | string | MUST | == S2 Epic.title | 铁律 A，100% 严格相等 |
| `功能描述` | string | MUST | == S2 Story.title | 铁律 B，100% 严格相等 |
| `前置条件` | string | MUST | LLM | 具体数值 |
| `steps` | array | MUST | LLM | ≥ 1 元素 |
| `expected_results` | array | MUST | LLM | 与 steps 一一对应 |
| `优先级` | enum(4) | MUST | TP.priority | |
| `用例状态` | enum(4) | SHOULD | L1∧L2 校验 | Draft/Ready/Rejected/Deprecated |
| `备注` | string | SHOULD | LLM | |
| `obj_id` | string | MUST | TP.obj_id | 铁律 C |
| `feature_point_id` | string | MUST | TP.feature_point_ref | 铁律 C |
| `s5_ref` | string | MUST | TP.tp_id | 反向引用 |
| `is_exploratory` | bool | COULD | LLM | v31 扩展 |
| `exploratory_reason` | string | COULD | LLM | is_exploratory=true 时必填 |
| `verified_against_s2_path` | string | COULD | DNA Q1.1 | v31 扩展 |
| `module_boundary_check` | object | COULD | MODULES.md §4 | v31 扩展 |
| `ssot_citation_path` | string | COULD | DNA Q1.1 | v31 扩展 |

---

## 10. 验收闭环

### 10.1 6 条 accept_criteria 验证证据

| # | 验收标准 | 证据 | 判定 |
|---|---------|------|------|
| **C1** | 方法论沉淀：S5/S6 完整链路 + LLM Prompt + 字段溯源 + 覆盖率公式 | 本文件 §2（输入契约）+ §3（方法论 + LLM Prompt）+ §6（覆盖率公式）+ §9（字段字典） | ✅ PASS |
| **C2** | 通用性验证：v3.01 样本跑通 | `workflow_assets/.../「S5 测试点生成」/test_points.json`（230 TP）+ `「S6 测试用例生成」/test_cases.{json,md,xlsx}`（230 TC）| ✅ PASS |
| **C3** | 知识库贯通：8 模块 × 子类 × TP 模板映射 | §4 模块 × 子类映射（引 SSOT）+ §8 TP 库入库链路 | ✅ PASS |
| **C4** | 覆盖率口径：基于 S4（25 risks / 66 leaves）+ OBJ/FP ≥ §4.3 常量 | `coverage_report.md` §1（OBJ 100% + FP 100% + 异常叶子 100% + 风险 100%）| ✅ PASS |
| **C5** | 格式干净：JSON + MD + XLSX 三格式，0 字段冗余、0 格式违规 | `test_cases.xlsx` 用 `_XLSX_HEADERS_V3` 10 列 + `coverage_report.md` §2 字段语义收紧 230/230 PASS | ✅ PASS |
| **C6** | 落档完整：方法论文档 + 产物归位 | 本文件 §1-§9 + S5/S6 产物在 `workflow_assets/游戏道具商城系统/v3.01/` + `coverage_report.md` | ✅ PASS |

### 10.2 影响范围

| 维度 | 影响 |
|------|------|
| **项目层** | v3.01 商城样本（16 Story / 230 TP / 230 TC / 100% 4 项覆盖率）|
| **Agent 层** | S5/S6 LLM 调用时按 §3.1.4 / §3.2.4 Prompt 模板执行；STAGE 字段约束不重写 |
| **人审层** | §8.3 pending_candidates 触发审核；S7 审查员校验字段语义（铁律 A/B/C）|

### 10.3 Round 5 收尾承诺

- 落档 `v31/CONVERGED.md` 声明 achieved
- 闭合遗留项：L1（ssot_citation_path 补填 或 草案降级为可选）+ L2（SCC 软下限修订）+ L3（UI 交叉 S3 prototype，留 v32）+ L4（density 覆盖率，留 S7 审查补做）
- audit_5.md + review_5.md 收尾报告

---

## 11. 附录：SSOT 索引

| 内容 | 路径 |
|------|------|
| 8 模块定义 | `.cursor/MODULES.md` |
| 8 模块子模板 | `knowledge/public/module_templates/<MODULE>.md` |
| 8 模块边界规则 | `knowledge/public/module_templates/<MODULE>/<boundary>.md` |
| S5 STAGE 规则 | `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` |
| S6 STAGE 规则 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` |
| S8 STAGE 规则 | `.cursor/rules/STAGE_S8_SELF_ITERATION.mdc` |
| 跨阶段契约 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.3 / §4.3 |
| DNA 准则 | `AGENTS.md` + `.cursor/rules/DNA_3Q_CHECK.mdc` |
| SCC 定义 | `governance/design_iter/plans/v31/v31_SCC.md` |
| S8 回灌诊断 | `governance/design_iter/plans/v31/s8_knowledge_backflow_diagnosis.md` |
| v31 草案（演进草稿）| `governance/design_iter/plans/v31/v31_方法论_草案.md` |
| 覆盖率自检报告 | `governance/design_iter/plans/v31/coverage_report.md` |
| 格式违规规则 | `.cursor/rules/product_format_rules.yaml` |
| 公共 XLSX 表头 | `ai_workflow/test_case_formatter.py` `_XLSX_HEADERS_V3` |
| 覆盖率验证脚本 | `ai_workflow/coverage_validator.py` |

---

> **v31 PLAN.md 落档** — Round 5 进入收尾 audit_5 + review_5 + CONVERGED 报告
