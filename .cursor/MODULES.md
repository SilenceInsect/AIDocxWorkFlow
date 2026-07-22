# AIDocxWorkFlow — 8 模块系统（项目级唯一真相源）

> ⚠️ **本文件是项目级唯一真相源（Single Source of Truth, SSoT）**。
> 任何规范（`SKILL.md` / `*.mdc`）、代码（`ai_workflow/*.py`）、数据（`workflow_assets/**/*.json`）、
> **测试点模板**（`knowledge/public/module_templates/*.md`）中提到的"模块"必须与本文件保持一致。
>
> **修改原则**：模块定义有调整时，**只改本文件**，下游文件通过引用自动同步。

**目录**：§1 总表 → §2 废弃 → §3 映射 → §3.5 交叉场景判定规则 → §4 矩阵 → §4.5 UI 细分索引 → §4.6 CONFIG 细分索引 → §4.7 UTIL 细分索引 → §4.8 BIZ 细分索引 → §4.9 LINK 细分索引 → §4.10 SPECIAL 细分索引（v1.11 落地）→ §4.11 HINT 细分索引（v1.11 编号迁移，§4.10 → §4.11；v1.7+ 16 文件全落地）→ §4.12 LOG 细分索引（v1.9 落地）→ §5 引用规范 → §6 维护流程 → §8 影响审计 → §9 兼容映射 → §10 模块测试点模板 → §11 单写源规则 → 附录（版本历史）

---

## 1. 8 模块总表

| #  | 模块     | ID 前缀   | 中文简称 | 英文简称 | 职责边界                                                                 |
| -- | -------- | --------- | -------- | -------- | ------------------------------------------------------------------------ |
| 1  | 配置     | `CONFIG`  | 配置     | CONFIG   | 配置表结构与字段合法性、枚举/资源/ID/时间格式约束；同表/全表/环境一致性；跨表 ID 依赖 + 循环依赖；解析与加载（双端一致/性能/容错）；数值逻辑（概率/公式/上限/平衡）；热更（流程/状态/异常）；版本兼容与灰度；导出/导入/发布流程；服务端业务配置（开服/防沉迷/GM/多服）（9 大类详见 §4.5 + `module_templates/CONFIG/`）|
| 2  | 界面     | `UI`      | 界面     | UI       | 纯前端 UI 层：控件渲染/状态/交互/布局/静态展示/动效/引导/无障碍/异常场景（详见 §4.5 + `module_templates/UI/`）|
| 3  | 业务     | `BIZ`     | 业务     | BIZ      | 服务端业务逻辑、端服数据流、前后端协议交互、对象/活动状态机、数据库持久化、并发事务、付费/定时异步任务、业务联动（9 大类详见 §4.8 + `module_templates/BIZ/`）|
| 4  | 辅助     | `UTIL`     | 辅助     | UTIL      | 底层全局公共工具类、通用基础框架组件；网络底层传输封装、消息队列、断线重连底层能力；客户端本地缓存、服务端 Redis 缓存、缓存生命周期管理；游戏资源加载/引用计数/卸载/分包更新底层能力；多货币汇率换算工具、数值格式化组件；离线资源包底层下载/校验/修复；分级 GM 后台工具、批量造数/自动化测试脚本；本地玩家设置持久化存储；画质帧率性能监控底层组件；整包/增量热更底层更新框架；资源&协议加密安全工具；全局崩溃捕获、底层异常兜底组件（详见 §4.7 + `module_templates/UTIL/`）|
| 5  | 关联     | `LINK`    | 关联     | LINK     | 内部业务上下游联动、多活动并行相交 / 重复开赛季重置逻辑；跨分布式服务数据同步、跨服互通业务与时序一致性；多端同账号数据实时对齐、多端登录冲突约束；第三方渠道登录 / 支付 / 上报业务对接、外部开放 API 交互与回调幂等处理；跨模块通用资源 / 限购互通约束；业务异步消息队列上下游透传；灰度 / 多服环境数据隔离与同步；游戏数据对外平台透出、客服 / 对账数据同步（**与 UTIL 底层传输框架隔离，仅覆盖业务互通规则**）|
| 6  | 特殊情境 | `SPECIAL` | 特殊     | SPECIAL  | 全系统数值/时间/权限/中断类边界极端场景、非正常业务异常分支处理；客户端本地篡改、伪造协议、挂机脚本等反作弊校验与非法数据拦截；本地存档、传输参数数据安全防护；弱网/抖动/断网环境业务操作容错、高频重复请求限流防刷；移动端前后台切换、进程杀除后状态与资源恢复逻辑；服务宕机、数据库抖动、版本回档、万人并发极限场景事务兜底；背包/邮件/服务器资源耗尽降级策略；新旧客户端版本兼容异常拦截；防沉迷、未成年付费、敏感内容等合规风控；批量清零/大额发奖/全服重置等高风险操作二次校验；灰度/渠道/离线资源损坏环境降级处理（底层网络、缓存工具等基础设施归 UTIL 模块，本模块仅覆盖业务层对抗、容错、安全风控规则）（9 大类详见 §4.10 v1.10 待建 + `module_templates/SPECIAL/`）|
| 7  | 日志     | `LOG`     | 日志     | LOG      | 全场景玩家生命周期 & 功能操作行为埋点；货币/道具/付费全链路资产审计流水；玩家、GM 运营、定时任务全量业务操作日志；服务性能指标、业务转化率、异常拦截监控埋点；客户端崩溃堆栈、业务报错异常日志并附带上下文快照；日志分级区分存储、冷热数据归档、定时生命周期清理；全链路 TraceID 串联、日志完整性对账校验、宕机断线缓存补报；埋点必填字段统一规范、隐私信息脱敏、渠道合规字段校验；安全反作弊拦截日志、第三方外部交互链路日志；日志检索溯源、线上问题复盘导出校验（**日志底层采集/存储 SDK、文件读写工具归 UTIL 模块，本模块仅覆盖日志业务规范、审计、埋点触发与合规校验规则**）（13 大类详见 §4.12 + `module_templates/LOG/`）|
| 8  | 提示     | `HINT`    | 提示     | HINT     | 全局临时反馈类提示组件：红点/角标/数字提醒（功能入口/数值/特殊标记）、资源/状态/结算飘字、轻量 Toast 短时弹窗、模态阻断式系统弹窗（错误/确认/公告/奖励汇总）、浮动通知/悬浮浮窗、错误提示文案专项、活动/Buff/资源过期限时提醒；新增 6 大类原定义缺失场景——新手引导高亮提示、聊天&社交提示、运营推送类提示、状态变更全局提示（升级/段位/赛季）、风控合规提示（防沉迷/付费限额/实名）、离线补偿&补发提示；与 UI 模块严格边界隔离——本模块仅覆盖临时弹出、一次性反馈、操作后自动消失的提示组件；页面常驻控件/固定布局/页面内置按钮输入框分页/静态展示/页面内常驻数值显示统归 UI 模块，二者无重叠（13 大类详见 §4.10 + `module_templates/HINT/`）|

> **模块专家 skill 交叉引用（v34 B1 落地）**：8 业务模块各自对应一个**模块专家 skill**（项目内，纳入 git），
> 绑定本表该行的 `module_templates/<MODULE>/` 作为权威资产库。
>
> | # | 模块专家 skill | 路径 | 触发命令 |
> |---|---------------|------|---------|
> | 1 | `config-expert` | `.cursor/skills/config-expert/SKILL.md` | `/config-expert` |
> | 2 | `ui-expert` | `.cursor/skills/ui-expert/SKILL.md` | `/ui-expert` |
> | 3 | `biz-expert` | `.cursor/skills/biz-expert/SKILL.md` | `/biz-expert` |
> | 4 | `UTIL-expert` | `.cursor/skills/UTIL-expert/SKILL.md` | `/UTIL-expert` |
> | 5 | `link-expert` | `.cursor/skills/link-expert/SKILL.md` | `/link-expert` |
> | 6 | `special-expert` | `.cursor/skills/special-expert/SKILL.md` | `/special-expert` |
> | 7 | `log-expert` | `.cursor/skills/log-expert/SKILL.md` | `/log-expert` |
> | 8 | `hint-expert` | `.cursor/skills/hint-expert/SKILL.md` | `/hint-expert` |
>
> **索引**：`.cursor/skills/_module-experts/README.md`
> **权限对照**：`.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §0.1.3
> **本表与专家 skill 是 1:1 绑定关系**——本表加/删模块 = 同步加/删专家 skill + 同步 §0.1.3 权限表。

> **ID 前缀说明**：
> - `CONFIG / UI / BIZ / UTIL / LINK / SPECIAL / LOG` — 用作 Epic ID 前缀（如 `CONFIG-VIP-001`）
> - `HINT` — **不**用作 Epic ID 前缀；HINT 仅作为 `scenario_test_points[].module` 字段的取值，
>   表示"该测试点属于 UI 交互中的提示/反馈"（如 `BIZ-PURCHASE-002-TP-002`，Story 是 BIZ 类，但 TP 标 HINT）

---

## 2. 已废弃模块（保留名称仅用于旧数据迁移）

| 旧前缀  | 中文       | 废弃版本 | 替代方案                                                                       |
| ------- | ---------- | -------- | ------------------------------------------------------------------------------ |
| `BASE`  | 基础       | v1.1     | 重新归类到上述 8 模块之一（多数情况归 `UTIL`）                                  |

> **迁移规则**：旧数据中如有 `BASE-*` Epic，需在 S2 重跑时重新分配到现行 8 模块之一。
> 旧 JSON 文件不强制回改，但 S2 生成的 epic.module 字段必须从 8 模块中取值。

---

## 3. 中英映射表（双语）

| ID 前缀  | 中文 | 英文  | ID 范例                              |
| -------- | ---- | ----- | ------------------------------------ |
| CONFIG   | 配置 | CONFIG| `CONFIG-VIP-001`                     |
| UI       | 界面 | UI    | `UI-SHOP-001-TP-001`                 |
| BIZ      | 业务 | BIZ   | `BIZ-PURCHASE-001`                   |
| UTIL      | 辅助 | UTIL   | `UTIL-CACHE-001`                      |
| LINK     | 关联 | LINK  | `LINK-PAYMENT-001`                   |
| SPECIAL  | 特殊 | SPECIAL| `SPECIAL-VIP-CHANGE-001`           |
| LOG      | 日志 | LOG   | `LOG-PAYMENT-001`                    |
| HINT     | 提示 | HINT  | `BIZ-PURCHASE-002-TP-002`（HINT 仅作 module 标注）|

> **S6 Excel/JSON 输出双语并存**：`模块` 字段采用 `英文 (中文)` 格式（如 `UI (界面)`），
> 下游消费方（Excel 筛选/JSON 解析）可任选其一。

---

## 3.5 交叉场景归属判定规则（S5 写用例时快速归类）

> 本节是**S5 阶段生成测试点时**的快速归类参考——按"看到什么就归什么模块"对照表。
> 详细边界 + 误判案例 + 决策树见各模块的 `O_boundary.md`。

| 场景 / 关键字                                          | 归模块 |
| ------------------------------------------------------ | ------ |
| 底层框架/工具代码、SDK 封装、通用工具函数              | **UTIL** |
| 第三方渠道、外部接口、跨服数据同步业务                 | **LINK** |
| 反作弊、限流、弱网业务异常、并发边界安全逻辑           | **SPECIAL** |
| 资产审计、行为埋点、监控日志完整性校验                 | **LOG** |
| 红点、飘字、弹窗、Toast、全局临时通知                  | **HINT** |
| 页面按钮、输入框、页面布局、页面动效、页面内控件状态   | **UI** |
| 道具产出、任务流程、充值订单、战斗结算、系统联动流程   | **BIZ** |
| Excel 配置表、数值公式、跨表依赖、配置热更、配置导出工具 | **CONFIG** |

**反向参考（什么**不**归某模块）**：

| 模块 | 不归它（归其他模块）                       |
| ---- | ------------------------------------------ |
| UTIL  | 业务提示/日志/第三方/风控 → HINT/LOG/LINK/SPECIAL |
| LINK | 网络底层传输、纯内部协议 → UTIL / BIZ     |
| SPECIAL | 通用异常框架、网络超时 → UTIL / B         |
| LOG  | 业务计算、UI 渲染 → BIZ / UI             |
| HINT | 页面布局控件、永久 UI 元素 → UI           |
| UI   | 全局临时通知、飘字 → HINT                 |
| BIZ  | 配置字段、UI 渲染、底层 SDK → CONFIG/UI/UTIL |
| CONFIG | 业务流程、UI 交互 → BIZ / UI            |

---

## 3.6 冲突优先级矩阵（v16 T1 新增）

> **本节是 §3.5 快速归类表的"冲突场景优先级"补充**——当同一测试场景可同时归入 2 个模块时，按本表优先级判定归属。
> **本节为 v16 落地项**（2026-07-17 用户拍板 + 模块优先级矩阵落地）
> **触发入口**：STAGE_S5_TEST_POINTS.mdc §1.5.2 "4 步判定 push" 末尾 Step 2.5 + STAGE_S4_FLOWCHART.mdc §1.5.2 "异常树叶子归属判定" 末尾出口

### 8 行冲突场景清单（v1.1 5 行 + v16 审核档补充 3 行）

| # | 冲突场景 | 优先级 | 判定规则 |
|---|---------|--------|----------|
| 1 | 异常 / 对抗场景 vs 常规业务 | **SPECIAL > BIZ/UI** | 满足特殊场景定义（异常 / 极端 / 对抗）优先归 SPECIAL |
| 2 | 跨服务交互 vs 业务逻辑 | **LINK > BIZ** | 核心验证点是跨系统调用时优先归 LINK |
| 3 | 配置驱动 vs 业务逻辑 | **CONFIG > BIZ** | 行为由配置表 / 数值 / 热更控制时优先归 CONFIG |
| 4 | 纯日志验证 vs 业务附带日志 | **纯日志归 LOG / 附带归 BIZ** | 主目标是验证日志输出归 LOG，业务验证顺带日志归 BIZ |
| 5 | 红点 / 弹窗样式 vs 内容触发 | **样式归 UI / 触发归 HINT** | 验证 UI 样式归 UI，验证触发条件和内容归 HINT |
| 6 | 辅助功能 vs 业务功能 | **UTIL < BIZ（业务优先）** | 主要是业务逻辑附带辅助归 BIZ，纯辅助归 UTIL |
| 7 | 关联影响 vs 主业务 | **LINK 独立 / BIZ 主归** | 主流程验证归 BIZ，跨模块影响验证单独归 LINK |
| 8 | 特殊配置 vs 配置通用 | **SPECIAL > CONFIG** | 极端配置值 / 异常配置场景归 SPECIAL，常规配置验证归 CONFIG |

### 使用规则

1. **不替代 §3.5 决策树**：先走 §3.5 主判定流程，仅当 §3.5 输出"可归 X 或 Y"歧义时查本表
2. **机检形态**：每行 = 1 个 if-then 规则，可由 LLM 或脚本机检
3. **冲突回退**：本表未覆盖的冲突场景需升级到人工裁定，并登记为新冲突行

---

## 4. 模块测试类型矩阵

每个测试点必须标注其所属模块，并按以下矩阵填写 `test_point_type` 字段：

| 模块     | 必须覆盖的测试类型                                                                            |
| -------- | --------------------------------------------------------------------------------------------- |
| CONFIG   | **9 个 v1.2 枚举**（详见 §4.5）：`FIELD_LEGALITY` / `FIELD_INTRA_DEP` / `FIELD_CROSS_DEP` / `RELOAD_4_MODE` / `PARSE_LOAD` / `VERSION_COMPAT` / `VALUE_LOGIC` / `EXPORT_PUBLISH` / `SERVER_CONFIG` |
| UI       | **11 个 v1.2 枚举**（详见 §4.5）：`CONTROL_RENDER` / `CONTROL_STATE` / `CONTROL_BASE_FUNC` / `CONTROL_BOUNDARY` / `PURE_INTERACTION` / `LAYOUT_ADAPT` / `STATIC_DISPLAY` / `ANIMATION` / `GUIDE_HINT` / `ACCESSIBILITY` / `EDGE_UI` |
| BIZ      | **9 个 v1.2 枚举**（详见 §4.8）：`BIZ_LOGIC` / `BIZ_DATA_FLOW` / `BIZ_PROTOCOL` / `BIZ_STATE_MACHINE` / `BIZ_DB_PERSIST` / `BIZ_CONCURRENCY` / `BIZ_SCHEDULED_TASK` / `BIZ_PAYMENT` / `BIZ_AUDIT_LOG` |
| UTIL      | **14 个 v1.2 枚举**（详见 §4.7）：`COMMON_UTIL` / `NETWORK_LAYER` / `CACHE_HIT_RATE` / `RESOURCE_MGMT` / `CURRENCY_EXCHANGE` / `OFFLINE_UPDATE` / `GM_TOOL` / `TEST_SCRIPT` / `ACCEPTANCE_CHECKLIST` / `STORAGE_LOG` / `PERF_TOOL` / `OPS_TOOL` / `SECURITY` / `ERROR_RECOVERY`（v1.6.1 起：日志/埋点/崩溃业务侧已迁出 LOG 详见 §4.12；UTIL 仅保留"底层 SDK/采集/上报框架"能力）|
| LINK     | **6 个 v1.2 枚举**（详见 §4.9）：`INTERNAL_BIZ_LINKAGE` / `CROSS_SERVER_SYNC` / `MULTI_CLIENT_SYNC` / `EXTERNAL_THIRD_PARTY` / `CROSS_MODULE_RESOURCE` / `OUTBOUND_DATA` |
| SPECIAL  | **9 个 v1.2 枚举**（详见 §4.10）：`BOUNDARY_EXTREME` / `ANTI_CHEAT` / `WEAK_NET_RATE_LIMIT` / `BG_FG_SWITCH` / `SERVER_HA_RISK` / `VERSION_COMPAT_BIZ` / `CHANNEL_GRAY_BIZ` / `COMPLIANCE_RISK` / `RESOURCE_EXHAUST` |
| LOG      | **13 个 v1.9 枚举**（详见 §4.12）：`LOG_EVENT_TRACK` / `LOG_ASSET_AUDIT` / `LOG_OPERATION` / `LOG_MONITOR` / `LOG_CRASH_REPORT` / `LOG_LEVEL_STORAGE` / `LOG_INTEGRITY` / `LOG_FIELD_COMPLIANCE` / `LOG_TRACE` / `LOG_SECURITY` / `LOG_THIRD_PARTY` / `LOG_ISOLATION` / `LOG_REPORT_FAULT_TOLERANT` |
| HINT     | **13 个 v1.7 枚举**（详见 §4.10）：`RED_DOT_BADGE` / `ITEM_FLOAT` / `CURRENCY_FLOAT` / `MODAL_DIALOG` / `TOAST` / `FLOAT_NOTIFY` / `GUIDE_HIGHLIGHT` / `SOCIAL_PROMPT` / `OPS_PUSH_PROMPT` / `STATE_CHANGE_DIALOG` / `COMPLIANCE_PROMPT` / `OFFLINE_COMPENSATION` / `TIMED_REMINDER` |

---

## §4.1 test_point_type → TC 字段映射（SSOT）

> S5 test_point_type 是「测试方法学」分类标签，S6 必须将此标签落到具体 TC 字段。

| test_point_type | TC.test_method | TC.test_scenario | 禁止行为 |
|---|---|---|---|
| `EP_VALID` | "等价类划分-有效类" | 含「有效值/合法值」 | 写成「无效/非法」 |
| `EP_INVALID` | "等价类划分-无效类" | 含「无效值/非法值」 | 写成「有效/合法」 |
| `BOUNDARY_MIN` | "边界值分析-最小有效" | 含边界值 min | — |
| `BOUNDARY_MAX` | "边界值分析-最大有效" | 含边界值 max | — |
| `BOUNDARY_MIN_1` | "边界值分析-min-1" | 含边界值 min-1 | — |
| `BOUNDARY_MAX_1` | "边界值分析-max+1" | 含边界值 max+1 | — |
| `OA_2N` | "正交试验-L4(2^3)" | 含 factors/levels | — |
| `OA_3N` | "正交试验-L9(3^4)" | 含 factors/levels | — |
| `OA_MIXED` | "正交试验-混合水平" | 含 factors/levels | — |
| `POSITIVE` | "正向流程" | 含「主流程/标准」 | — |
| `NEGATIVE` | "负向流程" | 含「拒绝/不当输入」 | — |
| `EXCEPTION` | "异常流容错" | 含「系统异常/重试」 | — |
| `PERFORMANCE` | "性能测试" | 含性能指标 | — |
| `SECURITY` | "安全测试" | 含攻击向量 | — |
| `CONFIG` | "配置变更测试" | 含配置生效 | — |
| `LOG` | "日志测试" | 含日志字段 | — |

---

## 4.5 UI 模块细分（概览 + 边界 + 索引）

> 本节是 UI 模块的**索引**——概览 + 边界规则 + 枚举映射。
> **明细、场景、种子 TP、验证证据** 全部在 `knowledge/public/module_templates/UI/` 下，
> 本节不再重复（避免双写漂移）。
>
> 其他 7 模块（CONFIG/BIZ/UTIL/LINK/SPECIAL/LOG/HINT）保持总表定义，不在本节展开。

### 概览（10 大类 × 11 个 v1.2 枚举）

| 字母 | 子类 | 测试类型枚举 | 模板 |
| ---- | ---- | ----------- | ---- |
| A | 控件基础 | `CONTROL_RENDER` / `CONTROL_STATE` / `CONTROL_BASE_FUNC` / `CONTROL_BOUNDARY` | [`A_control_basic.md`](../knowledge/public/module_templates/UI/A_control_basic.md) |
| B | 纯前端交互 | `PURE_INTERACTION` | [`B_pure_interaction.md`](../knowledge/public/module_templates/UI/B_pure_interaction.md) |
| C | 布局适配 | `LAYOUT_ADAPT` | [`C_layout_adapt.md`](../knowledge/public/module_templates/UI/C_layout_adapt.md) |
| D | 静态展示 | `STATIC_DISPLAY` | [`D_static_display.md`](../knowledge/public/module_templates/UI/D_static_display.md) |
| E | 动效动画 | `ANIMATION` | [`E_animation.md`](../knowledge/public/module_templates/UI/E_animation.md) |
| F | 引导浮窗 | `GUIDE_HINT` | [`F_guide_hint.md`](../knowledge/public/module_templates/UI/F_guide_hint.md) |
| G | 无障碍 | `ACCESSIBILITY` | [`G_accessibility.md`](../knowledge/public/module_templates/UI/G_accessibility.md) |
| H | 异常场景 | `EDGE_UI` | [`H_edge_ui.md`](../knowledge/public/module_templates/UI/H_edge_ui.md) |
| I | 边界区分 | —（判定规则，非测试类型） | [`I_boundary.md`](../knowledge/public/module_templates/UI/I_boundary.md) |
| J | 游戏专项 | —（游戏项目专属，非通用测试类型） | [`J_game_specific.md`](../knowledge/public/module_templates/UI/J_game_specific.md) |

> **枚举值展开**：11 个 v1.2 枚举对应到上表——A 类含 4 个枚举（`CONTROL_RENDER` / `CONTROL_STATE` / `CONTROL_BASE_FUNC` / `CONTROL_BOUNDARY`），B~H 各 1 个，I/J 无枚举。

> **完整覆盖范围**（一句话）：UI 控件渲染与多状态校验、纯前端无接口交互、键盘/鼠标多操作、
> 弹窗浮层联动、页面布局/窗口/分辨率多端适配、页面静态资源与文案展示、动效转场动画、引导红点提示、
> 前端本地筛选排序、输入实时格式校验、空态/异常/加载占位页面、权限锁定控件样式、多主题皮肤展示、控件焦点与无障碍适配。

---

## 4.6 CONFIG 模块细分（概览 + 索引）

> 本节是 CONFIG 模块的**索引**——概览 + 枚举映射。
> **明细、场景、种子 TP、验证证据** 全部在 `knowledge/public/module_templates/CONFIG/` 下，本节不重复。

### 概览（11 大类）

| 字母 | 子类       | 测试类型枚举（v1.2）                          | 模板                                                                |
| ---- | ---------- | --------------------------------------------- | ------------------------------------------------------------------- |
| A    | 字段合法性 | `FIELD_LEGALITY`                              | [`A_field_legality.md`](../knowledge/public/module_templates/CONFIG/A_field_legality.md)  |
| B    | 同表一致性 | `FIELD_INTRA_DEP`                             | [`B_consistency.md`](../knowledge/public/module_templates/CONFIG/B_consistency.md)       |
| C    | 跨表依赖   | `FIELD_CROSS_DEP`                             | [`C_cross_dep.md`](../knowledge/public/module_templates/CONFIG/C_cross_dep.md)            |
| D    | 热更新     | `RELOAD_4_MODE`                               | [`D_hot_reload.md`](../knowledge/public/module_templates/CONFIG/D_hot_reload.md)         |
| E    | 解析加载   | `PARSE_LOAD`                                  | [`E_parse_load.md`](../knowledge/public/module_templates/CONFIG/E_parse_load.md)         |
| F    | 版本兼容   | `VERSION_COMPAT`                              | [`F_version_compat.md`](../knowledge/public/module_templates/CONFIG/F_version_compat.md) |
| G    | 数值逻辑   | `VALUE_LOGIC`                                 | [`G_value_logic.md`](../knowledge/public/module_templates/CONFIG/G_value_logic.md)       |
| H    | 导出发布   | `EXPORT_PUBLISH`                              | [`H_export_publish.md`](../knowledge/public/module_templates/CONFIG/H_export_publish.md) |
| I    | 服务端专属 | `SERVER_CONFIG`                               | [`I_server_specific.md`](../knowledge/public/module_templates/CONFIG/I_server_specific.md) |
| J    | 边界区分   | —（判定规则，非测试类型）                    | [`J_boundary.md`](../knowledge/public/module_templates/CONFIG/J_boundary.md)             |
| K    | 游戏专项   | —（游戏项目专属，非通用测试类型）            | [`K_game_specific.md`](../knowledge/public/module_templates/CONFIG/K_game_specific.md)   |

> **完整覆盖范围**（一句话）：
> 游戏数据表结构与字段合法性校验、枚举/资源/ID/时间格式约束、同表/全局配置数值一致性、
> 跨表 ID 关联依赖校验、循环依赖拦截；客户端 & 服务端配置解析、复杂嵌套结构解析、超大表加载性能；
> 概率/成长/上限数值逻辑校验；配置增量/全量热更新、在线/离线热更、异常回滚兜底；
> 新旧版本前后兼容、赛季/灰度/渠道专属配置隔离；Excel 导出打包发布流程校验；
> 服务端全局常量、定时任务、GM 参数配置校验；非法配置容错告警、配置变更日志追溯。

### 边界区分（vs 其他 7 模块）

> ⚠️ **完整边界规则 + 误判案例 + 决策树** 见 [`CONFIG/J_boundary.md`](../knowledge/public/module_templates/CONFIG/J_boundary.md)。
> 本节只保留**核心对照**（防止误标 CONFIG 标签）。

| 归 CONFIG                          | 不归 CONFIG（归其他模块）              |
| ---------------------------------- | -------------------------------------- |
| 配置文件本身的字段/枚举/资源/ID 校验 | 加载后 UI 展示（按钮颜色变了）→ UI      |
| 配置导出/解析/热更/版本兼容         | 玩家操作触发的业务逻辑 → BIZ           |
| 同表/跨表数值/ID 约束/循环依赖      | 后端接口读取配置做业务计算 → BIZ / LINK|
| 数值公式/概率/上限/平衡校验         | 埋点/日志（配置变更的 audit log）→ LOG  |
| 非法配置容错告警                    | 性能监控（加载耗时上报）→ LOG           |

### 维护原则

- **MODULES.md §4.6**：只写概览 + 边界 + 索引（不写明细/场景/种子 TP）
- **`module_templates/CONFIG/`**：写明细 + 场景 + 种子 TP + 验证证据
- **禁止双写**：明细/场景/种子 TP 只能出现在模板里——`§4.6` 和模板**只**通过**链接**同步
- 改模板**无需**改 §4.6（链接稳定即可）
- 改 §4.6 的边界规则**必须**同步改 `J_boundary.md`（边界是 SSoT 核心）

---

### 边界区分（vs 其他 7 模块）

> ⚠️ **完整边界规则 + 误判案例 + 决策树** 见 [`UI/I_boundary.md`](../knowledge/public/module_templates/UI/I_boundary.md)。
> 本节只保留**核心对照**（防止误标 UI 标签）。

| 归 UI                              | 不归 UI（归其他模块）                                                  |
| ---------------------------------- | ---------------------------------------------------------------------- |
| 只改页面视觉、前端本地逻辑         | 点击按钮后调接口、提交表单落库 → 归 **BIZ**                            |
| 不请求后端接口的本地状态变更       | 后端数据返回渲染 → 归 **BIZ** / **UTIL**                                |
| 纯前端本地筛选、排序、分页         | 付费弹窗拉起支付、跨系统跳转 → 归 **LINK**（第三方）/ **BIZ**（业务）  |
| 静态资源展示（无业务）             | 资源下载逻辑、缓存命中率 → 归 **UTIL**                                  |
| 动效展示                           | 动效触发的数据变化、日志埋点 → 归 **LOG**                              |
| 提示的承载样式（红点图标、Toast UI）| 提示内容本身（飘字文案、状态码）→ 归 **HINT**                          |

### 维护原则（**单写源**）

- **MODULES.md §4.5**：只写概览 + 边界 + 索引（不写明细/场景/种子 TP）
- **`module_templates/UI/`**：写明细 + 场景 + 种子 TP + 验证证据
- **禁止双写**：明细/场景/种子 TP 只能出现在模板里——`§4.5` 和模板**只**通过**链接**同步
- 改模板**无需**改 §4.5（链接稳定即可）
- 改 §4.5 的边界规则**必须**同步改 `I_boundary.md`（边界是 SSoT 核心）

---

## 4.7 UTIL 模块细分（概览 + 索引）

> 本节是 UTIL 模块的**索引**——概览 + 枚举映射。
> **明细、场景、种子 TP、验证证据** 全部在 `knowledge/public/module_templates/UTIL/` 下，本节不重复。

### 概览（16 大类）

| 字母 | 子类          | 测试类型枚举（v1.2）                | 模板                                                                |
| ---- | ------------- | ----------------------------------- | ------------------------------------------------------------------- |
| A    | 公共工具      | `COMMON_UTIL`                       | [`A_common_util.md`](../knowledge/public/module_templates/UTIL/A_common_util.md)        |
| B    | 网络层        | `NETWORK_LAYER`                     | [`B_network_layer.md`](../knowledge/public/module_templates/UTIL/B_network_layer.md)    |
| C    | 缓存层        | `CACHE_HIT_RATE`                    | [`C_cache_layer.md`](../knowledge/public/module_templates/UTIL/C_cache_layer.md)        |
| D    | 资源管理      | `RESOURCE_MGMT`                     | [`D_resource_mgmt.md`](../knowledge/public/module_templates/UTIL/D_resource_mgmt.md)    |
| E    | 汇率换算      | `CURRENCY_EXCHANGE`                 | [`E_currency_exchange.md`](../knowledge/public/module_templates/UTIL/E_currency_exchange.md) |
| F    | 离线/版本更新 | `OFFLINE_UPDATE`                    | [`F_offline_update.md`](../knowledge/public/module_templates/UTIL/F_offline_update.md)  |
| G    | GM 工具       | `GM_TOOL`                           | [`G_gm_tool.md`](../knowledge/public/module_templates/UTIL/G_gm_tool.md)                |
| H    | 测试脚本      | `TEST_SCRIPT`                       | [`H_test_script.md`](../knowledge/public/module_templates/UTIL/H_test_script.md)        |
| I    | 策划验收      | `ACCEPTANCE_CHECKLIST`              | [`I_acceptance_checklist.md`](../knowledge/public/module_templates/UTIL/I_acceptance_checklist.md) |
| J    | 存储         | `LOCAL_STORAGE`（v1.6.1 重命名 + 收窄为本地存档）  | [`J_storage.md`](../knowledge/public/module_templates/UTIL/J_storage.md)                  |
| K    | 画质/性能     | `PERF_TOOL`                         | [`K_perf_tool.md`](../knowledge/public/module_templates/UTIL/K_perf_tool.md)            |
| L    | 运营辅助      | `OPS_TOOL`                          | [`L_ops_tool.md`](../knowledge/public/module_templates/UTIL/L_ops_tool.md)              |
| M    | 加密安全      | `SECURITY`                          | [`M_security.md`](../knowledge/public/module_templates/UTIL/M_security.md)              |
| N    | 异常兜底      | `ERROR_RECOVERY`                    | [`N_error_recovery.md`](../knowledge/public/module_templates/UTIL/N_error_recovery.md)  |
| O    | 边界区分      | —（判定规则，非测试类型）          | [`O_boundary.md`](../knowledge/public/module_templates/UTIL/O_boundary.md)              |
| P    | 游戏项目补充  | —（游戏项目专属，非通用测试类型）  | [`P_game_specific.md`](../knowledge/public/module_templates/UTIL/P_game_specific.md)    |

> **完整覆盖范围**（一句话）：
> 底层全局公共工具类、通用基础框架组件；网络底层传输封装、消息队列、断线重连底层能力；
> 客户端本地缓存、服务端 Redis 缓存、缓存生命周期管理；
> 游戏资源加载/引用计数/卸载/分包更新底层能力；多货币汇率换算工具、数值格式化组件；
> 离线资源包底层下载/校验/修复；分级 GM 后台工具、批量造数/自动化测试脚本；
> 本地玩家设置持久化存储；画质帧率性能监控底层组件；
> 整包/增量热更底层更新框架；资源&协议加密安全工具；全局崩溃捕获、底层异常兜底组件。

### 边界区分（vs 其他 7 模块）

> ⚠️ **完整边界规则 + 误判案例 + 决策树** 见 [`UTIL/O_boundary.md`](../knowledge/public/module_templates/UTIL/O_boundary.md)。
> 本节只保留**核心对照**（防止误标 UTIL 标签）。

| 归 UTIL                              | 不归 UTIL（归其他模块）              |
| ----------------------------------- | ---------------------------------- |
| 底层通用基础能力、工具、框架组件    | 业务流程、玩家交互逻辑 → BIZ       |
| GM / 测试 / 运营工具（底层）       | 配置表字段、跨表数值依赖 → CONFIG  |
| 网络 / 缓存 / 资源底层封装          | 页面视觉、前端交互展示 → UI        |
| 离线更新、整包增量更新底层          | 业务协议的业务逻辑校验 → BIZ       |
| 加密算法 / 性能监控 / 异常兜底底层  | 红点/弹窗/Toast/飘字 → HINT（v1.7+）|
|                                     | 日志/埋点/崩溃上报 → LOG（v1.8+）  |
|                                     | 第三方 SDK（微信/支付宝/渠道）→ LINK（v1.9+）|
|                                     | 风控/反作弊 → SPECIAL（v1.10+）    |
|                                     | 业务异常处理 / 运营业务 → BIZ（v1.11+）|

#### UTIL 与各模块的边界区分（一一对照）

**vs HINT**：
- UTIL：底层通知框架 API（弹窗 API、红点 API、Toast API）
- HINT：通知内容、触发逻辑、玩家可见的反馈表现

**vs LOG**：
- UTIL：日志/埋点底层 SDK、采集框架
- LOG：业务埋点规范、审计日志完整性、监控日志业务规则

**vs LINK**：
- UTIL：网络底层传输框架（TCP/长连接封装）
- LINK：业务层面第三方/跨服通信逻辑（调用外部接口、解析渠道回调、跨服数据同步业务）

**vs SPECIAL**：
- UTIL：底层网络重连、崩溃捕获框架能力
- SPECIAL：基于底层能力的业务安全/极端场景校验逻辑（反作弊、限流、弱网业务补偿）

**vs UI**：
- UTIL：UI 框架底层 API（弹窗 API、路由 API）
- UI：页面控件渲染、布局、静态结构

**vs BIZ**：
- UTIL：底层工具（断线重连、缓存）
- BIZ：业务流程（充值购买、任务结算、运营批量发奖/公告后台业务）

**vs CONFIG**：
- UTIL：GM 工具底层（执行层）
- CONFIG：GM 权限/参数配置（声明层）

### v1.6.1 裁剪说明（**已全部完成**）

| 剔除项 | 迁移去向 | 状态 |
|---|---|---|
| 日志/埋点/崩溃上报 SDK | LOG 模块 | ✅ **v1.9 已落地**（15 文件）|
| 红点/弹窗/Toast/飘字 | HINT 模块 | ✅ **v1.7+ 已落地**（16 文件）|
| 第三方 SDK（微信/支付宝/渠道登录）| LINK 模块 | ✅ **v1.8 已落地**（8 文件）|
| 风控/反作弊 | SPECIAL 模块 | ✅ **v1.11 已落地**（11 文件）|
| 业务异常处理（购买失败补偿等）| BIZ 模块 | ✅ **v1.7 已落地**（11 文件）|
| **运营批量发奖/公告后台业务** | **BIZ 模块** | ✅ **v1.7 已落地** |

> **占位文件清理**：
> - `UTIL/J_log_moved_to_LOG.md`（v1.6.1 占位）—— LOG v1.9 落地后已**删除**
> - `UTIL/L_ops_moved_to_BIZ.md`（v1.6.1+ 占位）—— BIZ v1.7 落地后已**删除**

**保留子模板**：A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P（其中 J 已重命名 J_storage_log → J_storage，N 缩窄为底层）|

### 维护原则

- **MODULES.md §4.7**：只写概览 + 边界 + 索引（不写明细/场景/种子 TP）
- **`module_templates/UTIL/`**：写明细 + 场景 + 种子 TP + 验证证据
- **禁止双写**：明细/场景/种子 TP 只能出现在模板里——`§4.7` 和模板**只**通过**链接**同步
- 改模板**无需**改 §4.7（链接稳定即可）
- 改 §4.7 的边界规则**必须**同步改 `O_boundary.md`（边界是 SSoT 核心）

---

## 4.8 BIZ 模块细分（概览 + 索引）

> 本节是 BIZ 模块的**索引**——概览 + 枚举映射。
> **明细、场景、种子 TP、验证证据** 全部在 `knowledge/public/module_templates/BIZ/` 下，本节不重复。

### 概览（11 文件 = 9 测试子模板 + 2 规则）

| 字母 | 子类 | 测试类型枚举（v1.2） | 模板 |
| ---- | ---- | ------------------- | ---- |
| A    | 核心业务逻辑   | `BIZ_LOGIC`         | [`A_biz_logic.md`](../knowledge/public/module_templates/BIZ/A_biz_logic.md) |
| B    | 端服数据流     | `BIZ_DATA_FLOW`     | [`B_data_flow.md`](../knowledge/public/module_templates/BIZ/B_data_flow.md) |
| C    | 协议交互       | `BIZ_PROTOCOL`      | [`C_protocol.md`](../knowledge/public/module_templates/BIZ/C_protocol.md) |
| D    | 状态机         | `BIZ_STATE_MACHINE` | [`D_state_machine.md`](../knowledge/public/module_templates/BIZ/D_state_machine.md) |
| E    | 数据库持久化   | `BIZ_DB_PERSIST`    | [`E_db_persist.md`](../knowledge/public/module_templates/BIZ/E_db_persist.md) |
| F    | 并发/多玩家    | `BIZ_CONCURRENCY`   | [`F_concurrency.md`](../knowledge/public/module_templates/BIZ/F_concurrency.md) |
| G    | 定时&异步任务  | `BIZ_SCHEDULED_TASK`| [`G_scheduled_task.md`](../knowledge/public/module_templates/BIZ/G_scheduled_task.md) |
| H    | 付费&商业化    | `BIZ_PAYMENT`       | [`H_payment.md`](../knowledge/public/module_templates/BIZ/H_payment.md) |
| I    | 日志与审计     | `BIZ_AUDIT_LOG`     | [`I_audit_log.md`](../knowledge/public/module_templates/BIZ/I_audit_log.md) |
| O    | 边界区分       | —（判定规则，非测试类型）| [`O_boundary.md`](../knowledge/public/module_templates/BIZ/O_boundary.md) |
| P    | 游戏项目补充   | —（游戏项目专属）| [`P_game_specific.md`](../knowledge/public/module_templates/BIZ/P_game_specific.md) |

> **完整覆盖范围**（一句话）：
> 全链路核心业务流程闭环、分支/中断/限制类异常业务逻辑、数值运算与风控约束、多系统联动业务；
> 端服跨服完整数据流、并发时序数据一致性；
> 前后端协议交互、版本兼容、非法请求拦截、标准错误码处理；
> 角色/活动/副本/Buff 等完整状态机与合法流转约束；
> 数据库持久化存储、事务并发锁、宕机数据恢复、分库分表归档；
> 多玩家并发、定时异步任务、付费订单对账业务；
> 全链路操作日志审计溯源。

### 边界区分（vs 其他 7 模块）

> ⚠️ **完整边界规则 + 误判案例 + 决策树** 见 [`BIZ/O_boundary.md`](../knowledge/public/module_templates/BIZ/O_boundary.md)。
> 本节只保留**核心对照**（防止误标 BIZ 标签）。

| 归 BIZ                              | 不归 BIZ（归其他模块）              |
| ----------------------------------- | ---------------------------------- |
| 服务端业务逻辑、协议字段、错误码体系 | 仅页面视觉、前端本地交互 → UI     |
| 业务流程、数值计算、保底、风控约束 | 配置表字段、跨表数值依赖 → CONFIG  |
| 端服跨服数据流、推送、限流、幂等   | 网络底层、Redis 缓存 → UTIL         |
| 状态机流转、非法状态拦截           | 弱网/切后台/反作弊 → SPECIAL       |
| DB 落库、事务、并发锁、宕机恢复   | 通用行为日志/埋点 → LOG            |
| 多玩家并发（拍卖/抢购/全服奖励） | 第三方 SDK/支付集成 → LINK         |
| 定时/异步任务业务                  | 红点/飘字/Toast → HINT             |
| 充值订单/退款/对账业务             |                                    |
| 业务审计日志、链路追溯              |                                    |

### 维护原则

- **MODULES.md §4.8**：只写概览 + 边界 + 索引（不写明细/场景/种子 TP）
- **`module_templates/BIZ/`**：写明细 + 场景 + 种子 TP + 验证证据
- **禁止双写**：明细/场景/种子 TP 只能出现在模板里——`§4.8` 和模板**只**通过**链接**同步
- 改模板**无需**改 §4.8（链接稳定即可）
- 改 §4.8 的边界规则**必须**同步改 `O_boundary.md`（边界是 SSoT 核心）

---

## 4.9 LINK 模块细分（概览 + 边界 + 索引）

> 本节是 LINK 模块的**索引**——概览 + 边界规则 + 完整覆盖范围。
> **明细、场景、种子 TP、验证证据** 在 [`knowledge/public/module_templates/LINK/`](../knowledge/public/module_templates/LINK.md) 下（**v1.8 已建** 1 概览 + 6 子模板 + O 边界 + P 游戏专项 = 8 文件），本节不重复（避免双写漂移）。
>
> **UTIL 隔离（核心）**：LINK = 业务互通规则；UTIL = 底层能力底座。详见 §4.9.1。

### 4.9.0 核心一句话

**LINK 聚焦多系统、多服务、多端、外部第三方之间的业务互通规则与数据同步一致性校验；底层网络、SDK 封装、通信工具能力归属 UTIL 辅助模块，二者无重叠。**

> **LINK 双职责（v34 用户拍板 · 修正版 3）**：
>
> 之前两轮映射都是 Agent 臆造——以用户 2026-07-21 9:27 最终拍板为准：
>
> - **关联** = **功能 ↔ 功能** 之间的结构关系，4 种典型形态：
>   - **功能跳转**（如点击【购买】→ 跳转【支付页】→ 跳转【订单详情】）
>   - **从属关系**（如【商城首页】包含【道具卡片】→【道具卡片】从属【商城首页】）
>   - **数据传递**（如【确认订单】→ 传【道具 ID + 数量 + 价格】→【支付页】）
>   - **触发链**（如【支付成功】→ 触发【发邮件】→ 触发【刷新背包】）
> - **回归** = **变更视角：新功能/新逻辑（含新增/修改）波及到已有通用能力时，必须对该通用能力的原有流程做一次回归验证，确认未被破坏**
>   - 用户原话："你的完整的功能是，各个子功能系统上新增或者修改上构建出来的，所以，除了要测试需求本身，也要回归各个关联的子功能"
>   - 用户原话补充（多层副本实例）："新做的多层副本 = 新阶段 + 新重连逻辑 + 发奖逻辑 → 这些新逻辑**改动时**，**通用副本逻辑**的原有流程必须回归测一遍，确认改动后通用副本流程还是正常的"
>   - 关键 4 要素：
>     1. **触发器**：有"新功能/新逻辑上线"或"已有逻辑被修改"
>     2. **波及识别**：S2 拆解时识别哪些"通用能力 / 通用流程 / 共享底层 / 上游下游"会被这次改动碰到
>     3. **回归执行**：对该波及到的"通用能力原有流程"做一轮回归测试
>     4. **目的**：确认"改动后通用流程还是正常的"——不是测新逻辑本身，是**测通用流程没有被新逻辑破坏**
>   - **回归 ≠ 测试回归集**，**回归 = 变更 → 波及 → 通用能力回归验证**
>   - **回归 ≠ 新逻辑的功能测试**（新逻辑本身测属于 BIZ/UI 模块），**回归 = 通用流程的原有路径在新改动后是否仍正常**
>
> ⚠️ **前两轮错误映射的撤回日志**：
> - v34 Round 1 错误："关联 = 测试可追溯 4 层链（TC→TP→OBJ→原需求）"——用户 9:23 否认
> - v34 Round 2 错误："回归 = 系统级功能依赖拓扑（活动→任务/地图/日历/副本）"——用户 9:26 部分否认
> - v34 Round 2.5 半错："回归 = 完整功能 = 子功能叠加构建时的范围扩展"——静态视角有偏差，用户 9:27 明确**回归是"变更视角"**——需要触发器（改了 A）+波及识别（波及到通用能力 B）+回归 B
> - 关联部分三轮理解一致（功能↔功能）：✅ 保留
> - 回归部分从"系统间拓扑 → 静态范围扩展 → 变更视角回归"：✅ 本次升级到"变更视角"
>
> **链路图 A（关联）** = 功能跳转图 / 从属树 / 数据流图（**功能之间**的结构）
> **链路图 B（回归）** = **变更触发 → 波及识别 → 通用能力回归验证清单**（**变更视角下的回归触发链**）
>
> 详见 `governance/design_iter/plans/v34/link_module_chain_map.md`

### 4.9.1 UTIL vs LINK 核心区分（"水管 vs 业务"规则）

| 维度 | UTIL 辅助 | LINK 关联 |
| --- | --- | --- |
| 定位 | 底层通用框架、工具、SDK 封装、传输基础设施 | 业务层面的关联、互通、外部对接逻辑 |
| 职责 | 提供"能力底座"，**不含业务联动逻辑** | 基于 UTIL 底层能力，实现**业务互通规则、数据同步约束、上下游联动** |
| 典型 | 网络长连接、协议编解码、SDK 加密、消息队列底层、HTTP 请求工具、TCP 重连 | 支付下单+回调解析+补发、跨服组队数据同步、多端登录冲突、第三方登录角色绑定 |
| 一句话 | **UTIL 是"水管"** | **LINK 是"水管里流通什么业务数据、两端业务怎么对齐"** |

### 4.9.2 完整覆盖范围（5 大类）

| # | 类别 | 核心场景 |
| --- | --- | --- |
| 1 | 内部业务关联 | 系统上下游联动（前置/后置依赖、模块互通数据流转）、活动复开/重置（限时活动重置、多活动并行相交）、跨系统数据联动约束（一处修改全关联同步）|
| 2 | 跨服务/分布式关联 | 逻辑服/活动服/充值服之间业务互通（跨服组队/拍卖/竞技场/全服排行榜）、跨服务时序校验（多服并发同玩家数据不乱序/不丢失/不重复）、服务重启后跨服断点续同步、灰度/多服环境数据隔离 |
| 3 | 多端一致性关联 | 同账号多端数据实时同步（PC/移动端/模拟器）、多端登录冲突与顶号、客户端本地缓存与服务端真实数据差值刷新与兜底校正 |
| 4 | 外部第三方关联 | 第三方登录业务（游客转正式、账号绑定/解绑、渠道互通、登录态同步角色）、第三方支付业务（充值下单、回调解析、订单状态同步、补发/退款回滚、渠道对账）、第三方上报业务、平台外部 API 对接（运营后台、客服工单、防沉迷实名校验、超时/重试/幂等/兜底）|
| 5 | 新增 4 大类（原定义缺失）| 跨环境/跨服配置关联（测试服/正式服/灰度服数据隔离、白名单跨服配置同步）、上下游异步消息关联（业务消息队列、消息丢失/重复幂等）、跨模块资源互通约束（通用货币/道具全系统流通、跨系统限购共享）、对外数据透出关联（排行榜/玩家/付费数据透出、脱敏、字段对齐、实时/定时双模）|

### 4.9.3 边界区分（vs 其他 7 模块）

> ⚠️ **完整边界规则 + 误判案例 + 决策树** 见 [`LINK/O_boundary.md`](../knowledge/public/module_templates/LINK/O_boundary.md)（**v1.8 已建**——含 7 大类边界对照 + 7 个误判案例 + 判定流程图 + 6 子类判定口诀）。
> 本节只保留**核心对照**（防止误标 LINK 标签）。

| 归 LINK | 不归 LINK（归其他模块）|
| --- | --- |
| 内部多系统业务联动规则（上游解锁下游、模块互通数据流转）| 底层网络传输、SDK 底层封装、消息队列底层框架 → **UTIL** |
| 多活动并行相交、活动复开/重置业务规则 | 单系统独立业务流程（单独商城购买、单独任务领取）→ **BIZ** |
| 跨分布式服务数据同步、跨服业务与时序一致性 | 第三方接口恶意篡改、跨服数据作弊拦截 → **SPECIAL** |
| 多端同账号数据实时对齐、多端登录冲突约束 | 客户端本地缓存实现、缓存命中与淘汰 → **UTIL** |
| 第三方渠道登录/支付/上报业务对接、回调幂等 | 支付 SDK 底层加密、TCP 重连、HTTP 工具 → **UTIL** |
| 平台外部开放 API 交互（运营后台、客服工单、防沉迷）| 资源下载、断点续传、整包增量热更 → **UTIL** |
| 跨模块通用资源/限购互通约束（通用货币/道具全系统流通）| 业务资源加载、引用计数、卸载 → **UTIL** |
| 业务异步消息队列上下游透传（充值完成推送活动服）| 业务流程内部状态机、业务异常处理 → **BIZ** |
| 灰度/多服环境数据隔离与同步 | 灰度流量调度、防刷限流、外部接口限流 → **SPECIAL** |
| 游戏数据对外平台透出（排行榜/客服/对账）、脱敏 | UI 弹窗、飘字、红点 → **HINT** |
| 跨服异常时的业务兜底（外部接口超时/重试/幂等）| 业务行为日志、审计追踪、监控埋点 → **LOG** |

### 4.9.4 维护原则

- **MODULES.md §4.9**：只写概览 + 边界 + 索引（不写明细/场景/种子 TP）
- **`module_templates/LINK/`**（v1.8 已建）：1 概览 + 6 子模板（A 内部业务关联 / B 跨服务 / C 多端一致性 / D 外部第三方 / E 跨模块资源互通 / F 对外数据透出）+ 1 边界 O_boundary + 1 游戏专项 P_game_specific = **8 文件**；写明细 + 场景 + 种子 TP + 验证证据
- **禁止双写**：明细/场景/种子 TP 只能出现在模板里——`§4.9` 和模板**只**通过**链接**同步
- 改 §4.9 边界规则**必须**同步改 [`LINK/O_boundary.md`](../knowledge/public/module_templates/LINK/O_boundary.md)（v1.8 已建，含 7 大类边界对照 + 7 个误判案例 + 判定流程图 + 6 子类判定口诀）
- **与 UTIL §4.7 严格隔离**：UTIL 管"底层能力"、LINK 管"业务互通规则"——任何重叠项归 UTIL（基础设施）/ LINK（业务规则），**无第三选项**
- 判不出来的回归到 **3 步判定法**：（1）是底层能力/工具/SDK？→ UTIL；（2）是单系统独立业务？→ BIZ；（3）都不属于 + 涉及多系统/多服务/多端/外部互通？→ LINK
- 改模板**无需**改 §4.9（链接稳定即可）；改 §4.9 边界规则**必须**同步改 O_boundary.md 双向同步（按 §11.2 同步机制）

---

## 4.10 SPECIAL 模块细分（概览 + 边界 + 索引）

> 本节是 SPECIAL 模块的**索引**——概览 + 边界规则 + 完整覆盖范围。
> **明细、场景、种子 TP、验证证据** 全部在 `knowledge/public/module_templates/SPECIAL/` 下，本节不重复（避免双写漂移）。
>
> **UTIL 隔离（核心）**：SPECIAL = 业务层对抗/容错/安全风控规则；UTIL = 底层能力底座。详见 §4.10.1。

### 4.10.0 核心一句话

**SPECIAL 聚焦非正常、高危、极端、对抗性场景的业务风控与容错逻辑（边界极端/反作弊/弱网限流/前后台/宕机高危/版本兼容/渠道灰度/合规/资源耗尽）；底层网络重连、崩溃捕获、缓存工具等基础设施归 UTIL 模块，正常正向业务流程归 BIZ 模块，第三方/跨服互通异常归 LINK 模块——四者无重叠。**

### 4.10.1 UTIL vs BIZ vs LINK vs SPECIAL 核心区分（"水管 vs 业务 vs 对抗"规则）

| 维度 | UTIL 辅助 | BIZ 业务 | LINK 关联 | SPECIAL 特殊 |
| --- | --- | --- | --- | --- |
| 定位 | 底层通用框架、工具、SDK 封装、传输基础设施 | 业务层正常流转规则 | 业务层多系统互通规则 | 业务层对抗/容错/安全风控 |
| 职责 | 提供"能力底座"，**不含业务联动逻辑** | 单系统独立业务流程 | 多系统/多端/外部互通规则 | 异常/高危/对抗/极限/合规/资源耗尽 |
| 典型 | 网络长连接、Redis、SDK 加密、崩溃捕获、TCP 重连 | 充值购买、任务领取、状态机、数据库持久化 | 跨服组队、第三方支付回调、多端登录 | 反作弊、限流、弱网降级、宕机 Failover、防沉迷、版本兼容 |
| 一句话 | **UTIL 是"水管"** | **BIZ 是"水管里流什么"** | **LINK 是"两管怎么对接"** | **SPECIAL 是"水管破裂/泄漏/污染时怎么办"** |

### 4.10.2 完整覆盖范围（9 大类）

| # | 类别 | 子类代码 | 核心场景 |
| --- | --- | --- | --- |
| 1 | 边界极端场景 | `BOUNDARY_EXTREME` | 数值边界（0/负/溢出/超大）、时间边界（未开启/已过期/CD/赛季结束）、权限边界（未解锁/等级不足/跨服权限/GM 高危）、中断分支（切后台/断线/退出/重启/被事件打断）、冲突边界（互斥活动/互斥道具/资源锁抢占）|
| 2 | 反作弊 / 数据安全 | `ANTI_CHEAT` | 客户端数据校验（本地改金币/道具/坐标/冷却）、发包作弊（重复/伪造/越权）、行为反作弊（瞬移/无限技能/挂机/脚本/多开）、存储安全（本地存档篡改/本地缓存与服务端不一致）、处罚联动（封禁/扣回/清除/留痕）|
| 3 | 弱网 / 断网 / 限流 | `WEAK_NET_RATE_LIMIT` | 网络分层异常（弱网/抖动/切换/断网/网关失败/跨服通道断）、业务容错（操作缓存队列/续执行/回滚/不重复扣发/不半写/不卡死/不丢指令）、限流防刷（高频点击/批量请求/限流拦截/冷却/防雪崩）|
| 4 | 前后台切换 / 生命周期 | `BG_FG_SWITCH` | 切后台短/长时间挂起、进程被杀、内存不足、锁屏唤醒；切回前台校验最新数据/同步过期/刷新缓存/重置临时态；后台释放渲染资源、前台重新加载不闪退、丢失临时 buff 自动校正|
| 5 | 宕机 / 回档 / 并发极限 / 高危风控 | `SERVER_HA_RISK` | 服务故障（逻辑服/充值服/DB 抖动/分库分表/热更崩溃）、数据恢复（事务回滚/补偿未发放/回档回收补发）、并发极限（全服发奖/万人活动/拍卖竞价/分布式锁/无超发）、高危风控（批量删除/清零/重置/封号/大额/跨服重置/二次确认/灰度/可回滚）|
| 6 | 版本兼容异常 | `VERSION_COMPAT_BIZ` | 新旧客户端不兼容、旧端访问新功能、新端读取旧配置、低版本入口拦截、协议号已废弃/不存在、数据格式降级、资源版本不匹配、热更资源缺失/损坏、强制升级提示、灰度期间协议兼容|
| 7 | 环境与渠道特殊异常 | `CHANNEL_GRAY_BIZ` | 渠道分包异常（SDK 升级/包名冲突/参数错误）、灰度白名单异常（白名单进非灰度/非白名单进灰度）、测试服与正式服互通隔离（数据泄漏/玩家误入）、离线包损坏（下载中断/checksum 错误/版本不匹配）、热更资源缺失/损坏后业务降级|
| 8 | 风控 & 合规特殊约束 | `COMPLIANCE_RISK` | 防沉迷超时强制下线（时长/宵禁/强制休息）、未成年付费限额拦截（单笔/月累计）、敏感词拦截（聊天/昵称/留言）、实名认证缺失限制功能、地区合规功能屏蔽（GDPR PII 屏蔽/版号限制/跨境支付限制）|
| 9 | 资源耗尽极端场景 | `RESOURCE_EXHAUST` | 背包满/仓库上限/邮件容量上限、服务器内存/CPU 打满、DB 连接耗尽、业务降级策略、排队限流、拒绝新操作、邮件将满预警、好友/工会上限、跨资源检查（背包满时提取邮件附件）|

### 4.10.3 边界区分（vs 其他 7 模块）

> ⚠️ **完整边界规则 + 误判案例 + 决策树** 见 [`SPECIAL/O_boundary.md`](../knowledge/public/module_templates/SPECIAL/O_boundary.md)。
> 本节只保留**核心对照**（防止误标 SPECIAL 标签）。

| 归 SPECIAL | 不归 SPECIAL（归其他模块）|
| --- | --- |
| 异常/高危/对抗/极限/合规/资源耗尽 业务规则 | 业务流程、玩家交互逻辑 → **BIZ** |
| 反作弊检测/数据篡改识别/作弊行为检测 | 底层网络/工具/SDK/加密算法 → **UTIL** |
| 弱网业务容错/限流防刷/雪崩保护 | 跨服/第三方正常业务 → **LINK** |
| 切后台状态恢复/进程被杀后资源释放 | 页面视觉/前端交互/页面渲染 → **UI** |
| 宕机 Failover/事务回滚/补偿/高危风控 | 提示内容/弹窗样式/飘字 → **HINT** |
| 反作弊审计/作弊日志留痕（执行层）| 通用行为日志/埋点/审计完整性 → **LOG** |
| 版本兼容/资源缺失兜底/协议版本校验 | 配置表字段/跨表数值/版本号配置 → **CONFIG** |
| 防沉迷/未成年付费限额/敏感词/地区合规（执行层）| 合规配置字段（防沉迷时长配置）→ **CONFIG** |
| 业务资源耗尽（背包满/CPU 高/DB 满）降级 | 资源管理底层（加载/释放/引用计数）→ **UTIL D** |

### 4.10.4 枚举值与子类映射（9 个 v1.2 枚举）

| 枚举值 | 归属子类 | 模板 | 备注 |
| --- | --- | --- | --- |
| `BOUNDARY_EXTREME` | A.边界极端场景 | [A_boundary_extreme.md](../knowledge/public/module_templates/SPECIAL/A_boundary_extreme.md) | 数值/时间/权限/中断/冲突 5 类边界 |
| `ANTI_CHEAT` | B.反作弊 / 数据安全 | [B_anti_cheat.md](../knowledge/public/module_templates/SPECIAL/B_anti_cheat.md) | 含 v1.1 旧 `ANTI_CHEAT` 扩展（行为反作弊+数据安全+参数篡改）|
| `WEAK_NET_RATE_LIMIT` | C.弱网 / 限流 | [C_weak_net_rate_limit.md](../knowledge/public/module_templates/SPECIAL/C_weak_net_rate_limit.md) | 含 v1.1 旧 `WEAK_NETWORK` 升级（语义扩展为"网络异常+流量限流"）|
| `BG_FG_SWITCH` | D.前后台切换 | [D_bg_fg_switch.md](../knowledge/public/module_templates/SPECIAL/D_bg_fg_switch.md) | 含 v1.1 旧 `SWITCH_TO_BACKGROUND` 升级（生命周期恢复）|
| `SERVER_HA_RISK` | E.宕机/并发/高危 | [E_server_ha_risk.md](../knowledge/public/module_templates/SPECIAL/E_server_ha_risk.md) | 覆盖原 v1.1 缺失的"服务 HA + 万人并发 + 高危风控" |
| `VERSION_COMPAT_BIZ` | F.版本兼容 | [F_version_compat_biz.md](../knowledge/public/module_templates/SPECIAL/F_version_compat_biz.md) | 原 v1.1 完全缺失 |
| `CHANNEL_GRAY_BIZ` | G.渠道/灰度 | [G_channel_gray_biz.md](../knowledge/public/module_templates/SPECIAL/G_channel_gray_biz.md) | 原 v1.1 完全缺失 |
| `COMPLIANCE_RISK` | H.合规风控 | [H_compliance_risk.md](../knowledge/public/module_templates/SPECIAL/H_compliance_risk.md) | 原 v1.1 完全缺失 |
| `RESOURCE_EXHAUST` | I.资源耗尽 | [I_resource_exhaust.md](../knowledge/public/module_templates/SPECIAL/I_resource_exhaust.md) | 原 v1.1 完全缺失 |

### 4.10.5 维护原则

- **MODULES.md §4.10**：只写概览 + 边界 + 索引（不写明细/场景/种子 TP）
- **`module_templates/SPECIAL/`**：写明细 + 场景 + 种子 TP + 验证证据
- **禁止双写**：明细/场景/种子 TP 只能出现在模板里——`§4.10` 和模板**只**通过**链接**同步
- 改模板**无需**改 §4.10（链接稳定即可）
- 改 §4.10 边界规则**必须**同步改 `O_boundary.md`（边界是 SSoT 核心）
- **UTIL vs BIZ vs LINK vs SPECIAL 严格隔离**：UTIL 管"底层能力"、BIZ 管"正常业务流程"、LINK 管"业务互通规则"、SPECIAL 管"异常/对抗/容错/合规/资源耗尽 业务规则"——四者无重叠
- 判不出来的回归到 **3 步判定法**：（1）涉及底层能力/工具/SDK？→ UTIL；（2）涉及单系统独立业务？→ BIZ；（3）涉及多系统/多端/外部互通？→ LINK；（4）涉及异常/高危/对抗/极限/合规/资源耗尽？→ SPECIAL

### 4.10.6 v1.11 SPECIAL 核心定位

> **SPECIAL = "非正常、高危、极端、对抗性场景"**
> 1. **底层能力归 UTIL**（网络 SDK/缓存工具/崩溃框架等）——SPECIAL 校验**这套能力之上**的业务容错
> 2. **正常业务归 BIZ**（正常流程/常规分支）——SPECIAL 只处理**异常**场景
> 3. **第三方/跨服正常互通归 LINK**——SPECIAL 只处理**第三方接口异常 + 跨服数据作弊拦截**
> 4. **界面加载失败归 UI**（纯视觉）——SPECIAL 处理**界面异常导致的业务错乱**
> 5. **SPECIAL 专精**：异常/高危/对抗/极限/合规/资源耗尽——9 大类（A-I）各管一段，无重叠
> 6. **本模块仅覆盖异常、高危、对抗、极限、合规限制类业务规则；正常正向业务流程归入 BIZ，底层通信/工具框架归入 UTIL，第三方跨服正常互通归入 LINK，各模块无用例范围重叠**

---

## 4.11 HINT 模块细分（概览 + 边界 + 索引）

> ✅ **本节是 HINT 模块的完整索引**——v1.7+ 阶段 13 大类子模板**全部落地**。
> **明细、场景、种子 TP、验证证据** 全部在 [`knowledge/public/module_templates/HINT/`](../knowledge/public/module_templates/HINT/) 下，本节不重复（避免双写漂移）。
>
> **HINT vs UI 严格隔离（核心）**：HINT = 临时弹出/一次性反馈/操作后自动消失；UI = 页面常驻控件/固定布局/静态页面元素。详见 §4.11.2。

### 4.11.0 核心一句话

**HINT 聚焦玩家可见的全局临时反馈类提示组件（红点/飘字/Toast/弹窗/浮窗/引导气泡/合规预警/离线补偿弹窗）；页面常驻控件、固定布局、静态页面元素统归 UI 模块——两者无重叠范围。**

### 4.11.1 完整覆盖范围（13 大类，v1.7 规划）

| #  | 类别         | 核心场景                                                                                          |
| --- | ------------ | ------------------------------------------------------------------------------------------------- |
| 1  | 红点/角标/数字提醒 | 功能入口红点（任务/活动/商城/邮件/背包/签到/福利/公会/限时副本）；数值角标（未读数/剩余次数/待领取）；特殊标记（倒计时/可升级/好友申请）；红点触发时机、领取后清除、多条件叠加、跨系统同步 |
| 2  | 飘字类动态数值 | 资源飘字（钻石/金币/体力/积分/道具/暴击伤害/治疗）；状态飘字（buff/debuff/免疫/闪避/格挡）；结算飘字（通关奖励/抽卡稀有高亮/排行榜名次变化）；飘字层级、多飘字不重叠、超长文本适配、消失动画 |
| 3  | 轻量 Toast    | 操作成功/失败/中性提示（购买/使用/兑换/分享/资源不足/等级不足/冷却中/已达上限/背包已满）；多操作队列排队、不刷屏、弱网不丢失、多语言文案 |
| 4  | 模态阻断式系统弹窗 | 错误阻断（登录失败/充值异常/版本过低/维护中/防沉迷下线）；确认弹窗（消耗稀有道具/删除/退出未保存/大额付费二次确认）；公告弹窗（全服更新/活动规则/版本须知/活动结束结算）；奖励汇总弹窗（登录礼包/在线奖励/活动批量奖励/累充达成） |
| 5  | 浮动通知/悬浮浮窗 | 活动悬浮小图标、限时倒计时悬浮条、新活动开启侧边浮窗；好友私聊/公会消息/跨服广播临时悬浮；限时优惠/折扣礼包浮动提醒/赛季即将结束倒计时 |
| 6  | 错误提示文案专项 | 统一规范文案（全局一致无歧义）；分级文案（普通/警告/严重阻断配色样式）；特殊场景文案（离线提示/跨服限制/权限不足/作弊拦截/资源过期） |
| 7  | 限时提醒浮窗 | 活动倒计时弹窗、buff 持续倒计时、道具过期提醒、每日次数重置提醒；定时弹窗（每日签到/限时活动开启推送） |
| 8  | 新手引导高亮提示 | 遮罩指引、箭头高亮、步骤文字气泡、点击引导浮窗、新手奖励弹窗                                              |
| 9  | 聊天&社交提示 | 私聊红点、公会消息提醒、赠送道具回执弹窗、好友申请通知、组队邀请弹窗                                       |
| 10 | 运营推送类提示 | 登录弹窗福利、限时折扣推送、节日活动弹窗、问卷调研弹窗、版本更新引导弹窗                                    |
| 11 | 状态变更全局提示 | 升级弹窗、突破升星弹窗、段位晋升、赛季结算、战力大幅变化提示                                              |
| 12 | 风控合规提示 | 防沉迷时长预警、未成年付费限额提醒、实名认证缺失提示、敏感词拦截提示                                       |
| 13 | 离线补偿&补发提示 | 离线奖励弹窗、服务器维护补偿、回档补发道具弹窗、邮件批量奖励提示                                          |

### 4.11.2 关键边界隔离规则（HINT vs UI）

> ⚠️ **HINT 与 UI 容易混淆，是 S5 误标高发区**。核心判断原则：**临时弹出 = HINT；常驻 = UI**。

| 归 HINT（不归 UI） | 归 UI（不归 HINT） |
| --- | --- |
| 临时弹出、一次性反馈、全局浮动、操作后自动消失的提示组件 | 页面常驻控件、固定布局、页面内置按钮/输入框/分页 |
| 红点、飘字、Toast、弹窗、浮窗、引导气泡 | 静态展示、页面内置文字标签、页面内常驻数值显示 |
| **举例区分**：背包页面里固定显示的金币数字 → UI；使用道具弹出金币 +100 飘字 → HINT | **举例区分**：活动页面常驻活动标题 → UI；上线自动弹出活动奖励弹窗 → HINT |
| 邮件未读数角标（**触发弹性的**） | 邮件页面固定列表/分页器/搜索框 |
| 战斗中暴击伤害飘字（**一次性浮现后消失**） | 战斗血条/角色模型/技能图标（**常驻渲染**） |
| 限时活动倒计时浮窗（**事件触发弹出**） | 活动页面常驻倒计时数字（**页面常驻**） |
| 升级弹窗、突破升星弹窗（**事件触发**） | 升级页面常驻控件（**页面常驻**） |

### 4.11.3 边界区分（vs 其他 7 模块）

> ⚠️ **完整边界规则 + 误判案例 + 决策树** 见 `knowledge/public/module_templates/HINT/O_boundary.md`（v1.8 子模板待建）。
> 本节只保留**核心对照**（防止误标 HINT 标签）。

| 归 HINT | 不归 HINT（归其他模块）|
| --- | --- |
| 玩家可见的临时反馈、提示内容、文案 | 通知的底层 API、SDK、框架能力 → **UTIL** |
| 红点/飘字/Toast/弹窗文案/触发逻辑 | 业务流程中"什么条件下触发" → **BIZ** |
| 错误提示文案分级样式 | 错误码体系、错误处理业务逻辑 → **BIZ** |
| 活动弹窗的 UI 表现（弹窗本身）| 活动状态机、活动业务规则 → **BIZ** |
| 限时倒计时浮窗的展示 | 倒计时定时器、定时任务调度 → **UTIL** / **BIZ** |
| 合规弹窗内容（防沉迷文案）| 合规校验、风控逻辑 → **SPECIAL H** |
| 离线补偿弹窗的展示 | 离线补偿数据生成、回档补偿业务 → **BIZ** |
| 引导气泡、遮罩指引 | 引导底层框架（步骤管理器）→ **UTIL** |
| 飘字/Toast 多队列管理 | 通知底层队列框架 → **UTIL** |
| **承载样式（红点图标、Toast UI）** → **UI** | **提示内容本身（飘字文案、状态码）** → **HINT** |

### 4.11.4 枚举值与子类映射（13 个 v1.7 规划枚举）

| 枚举值                  | 归属子类          | 备注 |
| ----------------------- | ----------------- | ---- |
| `RED_DOT_BADGE`         | 1.红点/角标/数字提醒 | 含 v1.6.1 旧 `RED_DOT` 升级（语义扩展为「角标+数字」）|
| `ITEM_FLOAT`            | 2.飘字类动态数值  | 资源飘字（道具/货币/积分）|
| `CURRENCY_FLOAT`        | 2.飘字类动态数值  | 战斗飘字（伤害/治疗/暴击/buff），v1.7 拆分独立 |
| `MODAL_DIALOG`          | 4.模态阻断式系统弹窗 | 错误/确认/公告/奖励汇总 |
| `TOAST`                 | 3.轻量 Toast      | 短时无阻断 |
| `FLOAT_NOTIFY`          | 5.浮动通知/悬浮浮窗 | 侧边浮窗/倒计时悬浮条 |
| `GUIDE_HIGHLIGHT`        | 8.新手引导高亮提示 | 遮罩/箭头/气泡/点击引导|
| `SOCIAL_PROMPT`         | 9.聊天&社交提示   | 私聊/公会/好友/组队|
| `OPS_PUSH_PROMPT`       | 10.运营推送类提示 | 登录福利/折扣/节日/调研|
| `STATE_CHANGE_DIALOG`   | 11.状态变更全局提示 | 升级/升星/段位/赛季结算|
| `COMPLIANCE_PROMPT`     | 12.风控合规提示   | 防沉迷/付费限额/实名|
| `OFFLINE_COMPENSATION`  | 13.离线补偿&补发  | 离线奖励/维护补偿/回档补发|
| `TIMED_REMINDER`        | 6+7.限时提醒+错误文案 | 倒计时弹窗+过期提醒+错误文案专项（v1.7 合并）|

### 4.11.5 子类索引（v1.7+ 16 文件 = 13 测试子模板 + O 边界 + P 游戏专项 + 1 概览）

| 字母 | 子类         | 子类代码（v1.7 枚举）         | 模板                                                                | 备注 |
| ---- | ------------ | ------------------------------- | ------------------------------------------------------------------- | ---- |
| A    | 红点/角标/数字提醒 | `RED_DOT_BADGE`            | [`A_red_dot_badge.md`](../knowledge/public/module_templates/HINT/A_red_dot_badge.md)       | v1.6.1 `RED_DOT` 升级（语义扩展为"角标+数字"）|
| B    | 资源飘字     | `ITEM_FLOAT`                  | [`B_item_float.md`](../knowledge/public/module_templates/HINT/B_item_float.md)             | 资源飘字（道具/货币/积分）|
| C    | 战斗飘字     | `CURRENCY_FLOAT`              | [`C_currency_float.md`](../knowledge/public/module_templates/HINT/C_currency_float.md)     | 战斗飘字（伤害/治疗/暴击/buff），v1.7 拆分独立 |
| D    | 模态系统弹窗 | `MODAL_DIALOG`                | [`D_modal_dialog.md`](../knowledge/public/module_templates/HINT/D_modal_dialog.md)         | 错误/确认/公告/奖励汇总 |
| E    | 轻量 Toast   | `TOAST`                       | [`E_toast.md`](../knowledge/public/module_templates/HINT/E_toast.md)                       | 短时无阻断 |
| F    | 浮动通知/悬浮浮窗 | `FLOAT_NOTIFY`            | [`F_float_notify.md`](../knowledge/public/module_templates/HINT/F_float_notify.md)         | 侧边浮窗/倒计时悬浮条 |
| G    | 限时提醒+错误文案 | `TIMED_REMINDER`          | [`G_timed_reminder.md`](../knowledge/public/module_templates/HINT/G_timed_reminder.md)     | 倒计时弹窗+过期提醒+错误文案专项（v1.7+ 合并）|
| H    | 新手引导高亮提示 | `GUIDE_HIGHLIGHT`          | [`H_guide_highlight.md`](../knowledge/public/module_templates/HINT/H_guide_highlight.md)   | 遮罩/箭头/气泡/点击引导|
| I    | 聊天&社交提示   | `SOCIAL_PROMPT`           | [`I_social_prompt.md`](../knowledge/public/module_templates/HINT/I_social_prompt.md)       | 私聊/公会/好友/组队|
| J    | 运营推送类提示   | `OPS_PUSH_PROMPT`         | [`J_ops_push_prompt.md`](../knowledge/public/module_templates/HINT/J_ops_push_prompt.md)   | 登录福利/折扣/节日/调研|
| K    | 状态变更全局提示 | `STATE_CHANGE_DIALOG`     | [`K_state_change_dialog.md`](../knowledge/public/module_templates/HINT/K_state_change_dialog.md) | 升级/升星/段位/赛季结算|
| L    | 风控合规提示   | `COMPLIANCE_PROMPT`         | [`L_compliance_prompt.md`](../knowledge/public/module_templates/HINT/L_compliance_prompt.md) | 防沉迷/付费限额/实名|
| M    | 离线补偿&补发  | `OFFLINE_COMPENSATION`     | [`M_offline_compensation.md`](../knowledge/public/module_templates/HINT/M_offline_compensation.md) | 离线奖励/维护补偿/回档补发|
| O    | 边界区分       | —（判定规则，非测试类型）  | [`O_boundary.md`](../knowledge/public/module_templates/HINT/O_boundary.md)                 | 完整 vs UI 7 模块边界 + 8 个误判案例 + 判定流程图 |
| P    | 游戏项目补充   | —（游戏项目专项）          | [`P_game_specific.md`](../knowledge/public/module_templates/HINT/P_game_specific.md)       | 战斗/社交/运营/合规/回滚 5 类游戏专项 |

> **结构说明**：
> - A-G 是 v1.6.1 已有 6 枚举的细化展开（A 升级 1:1；B/C 拆分；D/E/F 1:1；G 合并限时提醒+错误文案）
> - H-M 是 6 大类（原 v1.6.1 暂存版"原定义完全缺失"）
> - O 是判定规则和 HINT vs UI 边界（**必读**——S5 误标高发区）
> - P 是游戏专项补充（非通用测试类型）
> - 总计 **16 文件**（1 概览 + 13 子模板 A-M + O 边界 + P 游戏专项）
> - **种子 TP 统计**：A20 + B25 + C20 + D20 + E20 + F15 + G20 + H15 + I15 + J15 + K15 + L20 + M15 = **235 个种子 TP** + P 15 = **250 个种子 TP**

### 4.11.6 维护原则

- **MODULES.md §4.11**：只写概览 + 边界 + 索引（不写明细/场景/种子 TP）
- **`module_templates/HINT/`**（v1.7+ 已建 16 文件）：写明细 + 场景 + 种子 TP + 验证证据
- 改模板**无需**改 §4.11（链接稳定即可）
- 改 §4.11 边界规则**必须**同步改 `HINT/O_boundary.md`（边界是 SSoT 核心）
- **HINT vs UI 严格隔离**：HINT 管"临时弹出/一次性反馈"、UI 管"常驻控件/静态布局"——判不出来的回归到 **临时 vs 常驻 判定法**：（1）事件触发弹出 + 一次性反馈？→ HINT；（2）页面常驻渲染 + 持续可见？→ UI
- **HINT 内部子类口诀**（按事件驱动类型分类）：
  - **事件触发临时反馈**（D 弹窗 / E Toast / F 浮窗 / G 限时提醒 / H 引导 / I 社交 / J 运营 / K 状态 / L 合规 / M 补偿）：测"内容/触发/文案"
  - **常驻浮动显示**（A 红点 / B 资源飘字 / C 战斗飘字）：测"显示/清除/数值"
  - **强制 vs 非强制**：D / L 强制；E / F / H 非强制

---

## 4.12 LOG 模块细分（概览 + 索引）

> 本节是 LOG 模块的**索引**——概览 + 边界规则 + 枚举映射。
> **明细、场景、种子 TP、验证证据** 全部在 `knowledge/public/module_templates/LOG/` 下，本节不重复。
>
> **v1.9 核心定位**：**LOG = 日志业务规范 + 审计 + 埋点触发 + 合规**；**UTIL = 日志底层采集 SDK + 文件读写 + 网络上报框架**——两者**严格隔离、无职责重叠**。

### 概览（15 文件 = 13 测试子模板 + 2 规则）

| 字母 | 子类 | 测试类型枚举（v1.9） | 模板 |
| ---- | ---- | ------------------- | ---- |
| A    | 玩家行为埋点采集 | `LOG_EVENT_TRACK`         | [`A_event_track.md`](../knowledge/public/module_templates/LOG/A_event_track.md) |
| B    | 资产产出消耗审计   | `LOG_ASSET_AUDIT`         | [`B_asset_audit.md`](../knowledge/public/module_templates/LOG/B_asset_audit.md) |
| C    | 全量业务操作日志   | `LOG_OPERATION`           | [`C_operation.md`](../knowledge/public/module_templates/LOG/C_operation.md) |
| D    | 服务监控埋点       | `LOG_MONITOR`             | [`D_monitor.md`](../knowledge/public/module_templates/LOG/D_monitor.md) |
| E    | 客户端崩溃/报错   | `LOG_CRASH_REPORT`        | [`E_crash_report.md`](../knowledge/public/module_templates/LOG/E_crash_report.md) |
| F    | 日志分级存储&生命周期 | `LOG_LEVEL_STORAGE`    | [`F_level_storage.md`](../knowledge/public/module_templates/LOG/F_level_storage.md) |
| G    | 日志完整性校验     | `LOG_INTEGRITY`           | [`G_integrity.md`](../knowledge/public/module_templates/LOG/G_integrity.md) |
| H    | 埋点字段合规       | `LOG_FIELD_COMPLIANCE`    | [`H_field_compliance.md`](../knowledge/public/module_templates/LOG/H_field_compliance.md) |
| I    | 线上问题溯源       | `LOG_TRACE`               | [`I_trace.md`](../knowledge/public/module_templates/LOG/I_trace.md) |
| J    | 安全&反作弊日志   | `LOG_SECURITY`            | [`J_security.md`](../knowledge/public/module_templates/LOG/J_security.md) |
| K    | 第三方关联链路     | `LOG_THIRD_PARTY`         | [`K_third_party.md`](../knowledge/public/module_templates/LOG/K_third_party.md) |
| L    | 多语言/多渠道隔离  | `LOG_ISOLATION`           | [`L_isolation.md`](../knowledge/public/module_templates/LOG/L_isolation.md) |
| M    | 日志上报容错       | `LOG_REPORT_FAULT_TOLERANT` | [`M_report_fault_tolerant.md`](../knowledge/public/module_templates/LOG/M_report_fault_tolerant.md) |
| O    | 边界区分           | —（判定规则，非测试类型）| [`O_boundary.md`](../knowledge/public/module_templates/LOG/O_boundary.md) |
| P    | 游戏项目补充       | —（游戏项目专项）| [`P_game_specific.md`](../knowledge/public/module_templates/LOG/P_game_specific.md) |

> **完整覆盖范围**（一句话）：
> 全场景玩家生命周期 & 功能操作行为埋点；货币/道具/付费全链路资产审计流水；玩家、GM 运营、定时任务全量业务操作日志；
> 服务性能指标、业务转化率、异常拦截监控埋点；客户端崩溃堆栈、业务报错异常日志并附带上下文快照；
> 日志分级区分存储、冷热数据归档、定时生命周期清理；全链路 TraceID 串联、日志完整性对账校验、宕机断线缓存补报；
> 埋点必填字段统一规范、隐私信息脱敏、渠道合规字段校验；安全反作弊拦截日志、第三方外部交互链路日志；
> 日志检索溯源、线上问题复盘导出校验。**日志底层采集/存储/上报 SDK、文件读写工具归 UTIL 模块，本模块仅覆盖日志业务规范、审计、埋点触发与合规校验规则**。

### LOG vs UTIL 严格隔离（核心边界）

> ⚠️ **完整边界规则 + 误判案例 + 决策树** 见 [`LOG/O_boundary.md`](../knowledge/public/module_templates/LOG/O_boundary.md)。
> 本节只保留**核心对照**（防止误标 LOG / UTIL 标签）。

| 归 LOG | 不归 LOG（归其他模块）              |
| ------ | ---------------------------------- |
| 业务埋点触发规则、字段规范、链路串联 | 日志采集 SDK、断网缓存 → **UTIL**     |
| 资产审计流水、batch_id 聚合对账     | 本地文件读写、Redis 缓存 → **UTIL**     |
| 全量操作日志留痕、覆盖率 100%       | 通用网络层、断线重连 → **UTIL**         |
| 服务监控业务指标埋点、告警          | 通用性能组件、FPS 监控 → **UTIL K**     |
| 客户端崩溃日志内容（堆栈+上下文+设备）| 崩溃底层 Native 捕获 → **UTIL N**     |
| 日志分级/生命周期/冷热分离          | 通用 localStorage 工具 → **UTIL J**    |
| 日志完整性、幂等、链路一致          | 加密算法（AES/SHA）→ **UTIL M**        |
| 字段必填、隐私脱敏、未成年人隔离    | —                                    |
| 全链路 TraceID 串联、检索、导出     | 业务流程本身（购买扣款/发货）→ **BIZ**  |
| 安全/反作弊/封禁/异地/批量建号日志留痕 | 反作弊业务逻辑、检测算法 → **SPECIAL** |
| 第三方交互日志留痕、回调全链路      | 第三方业务集成（微信/支付宝）→ **LINK** |
| 多语言/多渠道/灰度/测试服日志隔离   | 渠道业务（iOS/Android 分包）→ **LINK** |
| 断网缓存、批量合并、重试、分片、压缩 | 通用网络层（HTTP 客户端）→ **UTIL B**   |

### 维护原则

- **MODULES.md §4.12**：只写概览 + 边界 + 索引（不写明细/场景/种子 TP）
- **`module_templates/LOG/`**：写明细 + 场景 + 种子 TP + 验证证据
- **禁止双写**：明细/场景/种子 TP 只能出现在模板里——`§4.12` 和模板**只**通过**链接**同步
- 改模板**无需**改 §4.12（链接稳定即可）
- 改 §4.12 的边界规则**必须**同步改 `O_boundary.md`（边界是 SSoT 核心）
- **LOG vs UTIL 严格隔离**：LOG 管"业务规范/审计/埋点触发/合规"，UTIL 管"底层 SDK/采集/上报框架"——**判不出来的回归到 1 句话判定法**：（1）测"业务侧应该写什么日志、写什么字段、字段怎么脱敏、链路怎么串联" → **LOG**；（2）测"S SDK 怎么采集、文件怎么写、网络怎么传" → **UTIL**
- **LOG vs BIZ-I 区分**：LOG-B 测"资产对账可导出/全链路流水"，BIZ-I `BIZ_AUDIT_LOG` 测"业务侧落点是否完整"——同一笔业务 → BIZ-I 校验"是否写日志"，LOG 校验"日志能否对账"

---

## 5. 引用规范（下游必须遵守）

任何 `SKILL.md` / `*.mdc` / Prompt / `ai_workflow/*.py` 在描述模块时，**必须使用以下句式之一**：

### 句式 A：直接引用

```markdown
> 模块定义见 [`.cursor/MODULES.md`](./MODULES.md)（项目级唯一真相源）。本文件不重写模块表。
```

### 句式 B：单点扩展引用

```markdown
本阶段涉及的模块：`CONFIG` / `UI` / `BIZ`。
完整定义见 [`.cursor/MODULES.md`](./MODULES.md)。
```

### 句式 C：代码层引用

```python
# 模块定义见 .cursor/MODULES.md（项目级唯一真相源）
# 本文件不重写模块表，仅引用
_MODULE_SEQ = ["UI", "BIZ", "CONFIG", "UTIL", "LINK", "LOG", "SPECIAL", "HINT"]
```

### ❌ 反例（禁止在下游重写模块表）

```markdown
❌ 在 SKILL.md 中写：
| CONFIG | 配置 | RELOAD_4_MODE | FIELD_LEGALITY | ...
   → 模块表是 MODULES.md 的职责，SKILL.md 不应复制

❌ 在 test_case_formatter.py 中写：
_MODULE_SEQ = ["UI", "BIZ", "CONFIG", ...]   # 列出但不引用 MODULES.md
   → 必须同时注释 "见 .cursor/MODULES.md"
```

---

## 6. 维护流程

### 6.1 新增模块

1. 在本文件第 1 节表格**末尾追加**一行
2. 在第 3 节映射表同步追加
3. 在第 4 节测试类型矩阵追加必填类型
4. **不**需要修改任何下游文件（下游已通过引用自动同步）
5. 在 git commit message 中标注 `[MODULES]` 前缀

### 6.2 修改模块职责

1. **只改本文件**对应行
2. 在 git commit message 中标注 `[MODULES-EDIT]` 前缀
3. 下游文件无需改动（它们通过引用拿到最新定义）

### 6.3 废弃模块

1. 将对应行从第 1 节移到第 2 节"已废弃模块"
2. 标注废弃版本和替代方案
3. **不**主动删除旧数据；旧数据中如有引用，在加载时打 warning
4. 1 个版本周期后（≥ 30 天）才允许从本文件彻底删除

### 6.4 数据迁移规则

- **S2 backlog** 的 `epic.module` 字段必须从 8 模块中取值
- **S5 test_points** 的 `scenario_test_points[].module` 字段必须从 8 模块中取值
- **S5 test_points** 的 `module_coverage` keys 必须是 8 模块的子集
- **S6 test_cases** 的 `模块` 字段必须是 8 模块之一（中文或英文任一，遵循 S6 阶段的双语规范）

### 6.5 模块职责深化调整（子类展开）

> 当某模块的职责**深化**为多子类（如 UI 从 4 个测试类型扩展到 8 大类）时：

1. 在 §1 总表更新该模块的"职责边界"为压缩版（一句话）
2. 在 §4 测试类型矩阵**更新该模块行**，标注"详见 §X.Y 子类"
3. **新增子章节**（§4.5、§4.6...）展开子类、边界区分、专项补充
4. 在 git commit 标 `[MODULES-EXPAND]` 前缀
5. **复核下游 S5 prompt**（`ai_workflow/prompts/requirement_review.md` 等）：
   - 如果下游 prompt 直接列出了该模块的测试类型，**必须同步更新**
   - 如果下游 prompt 用"见 MODULES.md"引用，**无需改动**

**本次实例**：UI 模块从 4 个测试类型（`CONTROL_EXISTENCE / LAYOUT / RESOLUTION_COMPAT / INTERACTION`）扩展为 8 大类 + 边界区分 + 游戏专项，详见 §4.5。

---

## 8. 变更影响范围审计

> 改本文件时，**优先复核**以下下游文件（即使它们通过引用拉取，仍需人工确认无遗漏）：

| 变更类型 | 必须复核的下游文件                                                       |
| -------- | ------------------------------------------------------------------------ |
| 新增模块 | S2/S5/S6 规范、代码 `_MODULE_SEQ`、所有 backlog.json（出现新 epic 前缀时）|
| 修改职责 | 当前项目的 test_points.json（已生成的 TP 可能要重打 module 标签）         |
| 废弃模块 | 历史项目目录的 backlog.json / test_points.json（打 warning）             |
| 调整 ID 规则 | S2 prompt（epic 编号生成逻辑）、所有现存 epic_id 样本                  |

---

## 9. 枚举兼容映射（v1.1 → v1.2 旧数据平滑过渡）
> 原则：**历史数据不强制回改**（不破坏已有产出），但 S5 重跑时**自动升级**到 v1.2 枚举。

### 9.1 UI 测试类型兼容映射

| v1.2 枚举（现行）     | 归属子类       | v1.1 旧枚举（已废弃）   | 兼容规则（数据加载时执行）|
| --------------------- | -------------- | ----------------------- | -------------------------|
| `CONTROL_RENDER`      | A.控件基础校验 | `CONTROL_EXISTENCE`     | 1:1 映射（语义最强一致） |
| `CONTROL_STATE`       | A.控件基础校验 | `CONTROL_EXISTENCE`（部分）| 默认归 CONTROL_RENDER；人工判定时可拆出 |
| `CONTROL_BASE_FUNC`   | A.控件基础校验 | `INTERACTION`（基础操作）| 默认归 PURE_INTERACTION；UI 基础功能可拆出 |
| `CONTROL_BOUNDARY`    | A.控件基础校验 | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `PURE_INTERACTION`    | B.纯前端交互   | `INTERACTION`           | 1:1 映射（语义最强一致） |
| `LAYOUT_ADAPT`        | C.布局适配     | `LAYOUT` / `RESOLUTION_COMPAT` | 1:1 映射（合并两个旧枚举） |
| `STATIC_DISPLAY`      | D.页面级静态展示| （新增）               | 历史数据无对应项，v1.2 首次出现 |
| `ANIMATION`           | E.动效与动画   | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `GUIDE_HINT`          | F.引导浮窗提示 | （新增）                | 历史数据无对应项，v1.2 首次出现（**注**：与 HINT 模块正交，见 §4.5 F 节）|
| `ACCESSIBILITY`       | G.无障碍       | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `EDGE_UI`             | H.边界异常 UI  | （新增）                | 历史数据无对应项，v1.2 首次出现 |

### 9.2 加载/导出规则

- **加载 v1.1 旧数据**（S5/S6 JSON）：保留旧枚举值，**不强制重写**；如需升级到 v1.2，运行 `--migrate-modules` 命令
- **导出 v1.2 新数据**（S5/S6 JSON）：使用 v1.2 枚举
- **代码层（`test_case_formatter.py`）**：识别旧枚举时打 `DeprecationWarning`，不报错

> **本次实例**：UI 模块从 v1.1 的 4 个枚举升级为 v1.2 的 11 个枚举，详见本节。

### 9.3 CONFIG 测试类型兼容映射

| v1.2 枚举（现行）    | 归属子类       | v1.1 旧枚举（已废弃）   | 兼容规则（数据加载时执行）|
| -------------------- | -------------- | ----------------------- | -------------------------|
| `FIELD_LEGALITY`     | A.字段合法性   | `FIELD_LEGALITY`        | 1:1 映射                  |
| `FIELD_INTRA_DEP`    | B.同表一致性   | `FIELD_INTRA_DEP`       | 1:1 映射                  |
| `FIELD_CROSS_DEP`    | C.跨表依赖     | `FIELD_CROSS_DEP`       | 1:1 映射                  |
| `RELOAD_4_MODE`      | D.热更新       | `RELOAD_4_MODE`         | 1:1 映射                  |
| `PARSE_LOAD`         | E.解析与加载   | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `VERSION_COMPAT`     | F.版本兼容     | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `VALUE_LOGIC`        | G.数值逻辑     | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `EXPORT_PUBLISH`     | H.导出发布     | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `SERVER_CONFIG`      | I.服务端专属   | （新增）                | 历史数据无对应项，v1.2 首次出现 |

### 9.4 UTIL 测试类型兼容映射

| v1.2 枚举（现行）         | 归属子类       | v1.1 旧枚举（已废弃）   | 兼容规则（数据加载时执行）|
| ------------------------- | -------------- | ----------------------- | -------------------------|
| `COMMON_UTIL`             | A.公共工具     | `TOOL_UTIL`             | 1:1 映射（语义升级）      |
| `NETWORK_LAYER`           | B.网络层       | `NETWORK_LAYER`         | 1:1 映射                  |
| `CACHE_HIT_RATE`          | C.缓存层       | `CACHE_HIT_RATE`        | 1:1 映射                  |
| `RESOURCE_MGMT`           | D.资源管理     | `RESOURCE_MGMT`         | 1:1 映射                  |
| `CURRENCY_EXCHANGE`       | E.汇率换算     | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `OFFLINE_UPDATE`          | F.离线/版本更新| （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `GM_TOOL`                 | G.GM 工具      | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `TEST_SCRIPT`             | H.测试脚本     | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `ACCEPTANCE_CHECKLIST`    | I.策划验收     | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `STORAGE_LOG`             | J.存储+日志    | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `PERF_TOOL`               | K.画质/性能    | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `OPS_TOOL`                | L.运营辅助     | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `SECURITY`                | M.加密安全     | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `ERROR_RECOVERY`          | N.异常兜底     | （新增）                | 历史数据无对应项，v1.2 首次出现 |

### 9.5 BIZ 测试类型兼容映射

| v1.2 枚举（现行）         | 归属子类       | v1.1 旧枚举（已废弃）   | 兼容规则（数据加载时执行）|
| ------------------------- | -------------- | ----------------------- | -------------------------|
| `BIZ_LOGIC`               | A.核心业务逻辑 | `ACTIVITY_OPEN_CLOSE`（部分）| 涉及"业务规则/扣款发货/计算"默认归 BIZ_LOGIC；涉及"活动状态机"归 BIZ_STATE_MACHINE |
| `BIZ_DATA_FLOW`           | B.端服数据流   | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `BIZ_PROTOCOL`            | C.协议交互     | `PROTOCOL`              | 1:1 映射（语义升级） |
| `BIZ_STATE_MACHINE`       | D.状态机       | `ACTIVITY_OPEN_CLOSE`（部分）| 涉及"活动/副本/邮件/Buff 状态流转"归 BIZ_STATE_MACHINE |
| `BIZ_DB_PERSIST`          | E.数据库持久化 | `DB_PERSIST`            | 1:1 映射（语义升级） |
| `BIZ_CONCURRENCY`         | F.并发/多玩家  | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `BIZ_SCHEDULED_TASK`      | G.定时&异步任务| （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `BIZ_PAYMENT`             | H.付费&商业化  | （新增）                | 历史数据无对应项，v1.2 首次出现 |
| `BIZ_AUDIT_LOG`           | I.日志与审计   | （新增）                | 历史数据无对应项，v1.2 首次出现 |

> **拆分说明**：v1.1 旧枚举 `ACTIVITY_OPEN_CLOSE` 在 v1.2 中**拆分为 2 个**——
> - 业务结果（如"活动结束清空道具"）→ `BIZ_LOGIC`
> - 状态流转（如"活动状态机 未开启→进行中→结束"）→ `BIZ_STATE_MACHINE`
> - 涉及"定时器触发" → `BIZ_SCHEDULED_TASK`
>
> 旧 `ENTITY_CACHE` 在 v1.2 中**移交给 UTIL C**（`CACHE_HIT_RATE`），不再属于 BIZ。

### 9.6 LINK 测试类型兼容映射

| v1.2 枚举（现行）         | 归属子类       | v1.1 旧枚举（已废弃）   | 兼容规则（数据加载时执行）|
| ------------------------- | -------------- | ----------------------- | -------------------------|
| `INTERNAL_BIZ_LINKAGE`    | A.内部业务关联 | `CORRELATION_TEST`      | 1:1 映射（语义升级：聚焦"内部多系统业务联动"）|
| `CROSS_SERVER_SYNC`       | B.跨服务分布式 | `REGRESSION_TEST`（跨服部分）| 涉及"跨服数据同步/时序/灰度/断点续同步"默认归 `CROSS_SERVER_SYNC`；人工判定时按故事上下文确认 |
| `MULTI_CLIENT_SYNC`       | C.多端一致性   | `MULTI_TENANT_SYNC`     | 1:1 映射（语义升级：多端→多租户的纠正）|
| `EXTERNAL_THIRD_PARTY`    | D.外部第三方   | `REGRESSION_TEST`（第三方部分）| 涉及"渠道登录/支付/上报/API/回调幂等"归 `EXTERNAL_THIRD_PARTY` |
| `CROSS_MODULE_RESOURCE`   | E.跨模块资源互通 | （新增）              | 历史数据无对应项，v1.2 首次出现（原 v1.1 完全缺失）|
| `OUTBOUND_DATA`           | F.对外数据透出 | （新增）                | 历史数据无对应项，v1.2 首次出现（原 v1.1 完全缺失）|

### 9.7 HINT 测试类型兼容映射

| v1.7 枚举（现行）          | 归属子类          | v1.6.1 旧枚举（已废弃）   | 兼容规则（数据加载时执行）|
| ------------------------- | ----------------- | ------------------------- | -------------------------|
| `RED_DOT_BADGE`           | 1.红点/角标/数字提醒 | `RED_DOT`               | 1:1 映射（语义升级：扩展为「红点+角标+数字」）|
| `ITEM_FLOAT`              | 2.飘字类动态数值  | `ITEM_FLOAT`             | 1:1 映射（资源飘字——道具/货币/积分）|
| `CURRENCY_FLOAT`          | 2.飘字类动态数值  | `CURRENCY_FLOAT`         | 1:1 映射（战斗飘字——伤害/治疗/暴击/buff）|
| `MODAL_DIALOG`            | 4.模态阻断式系统弹窗 | `MODAL_DIALOG`        | 1:1 映射（错误/确认/公告/奖励汇总）|
| `TOAST`                   | 3.轻量 Toast      | `TOAST`                  | 1:1 映射（短时无阻断）|
| `FLOAT_NOTIFY`            | 5.浮动通知/悬浮浮窗 | `FLOAT_NOTIFY`        | 1:1 映射（侧边浮窗/倒计时悬浮条）|
| `GUIDE_HIGHLIGHT`         | 8.新手引导高亮提示 | （新增）                | 历史数据无对应项，v1.7 首次出现（原 v1.6.1 完全缺失）|
| `SOCIAL_PROMPT`           | 9.聊天&社交提示   | （新增）                | 历史数据无对应项，v1.7 首次出现（原 v1.6.1 完全缺失）|
| `OPS_PUSH_PROMPT`         | 10.运营推送类提示 | （新增）                | 历史数据无对应项，v1.7 首次出现（原 v1.6.1 完全缺失）|
| `STATE_CHANGE_DIALOG`     | 11.状态变更全局提示 | （新增）              | 历史数据无对应项，v1.7 首次出现（原 v1.6.1 完全缺失）|
| `COMPLIANCE_PROMPT`       | 12.风控合规提示   | （新增）                | 历史数据无对应项，v1.7 首次出现（原 v1.6.1 完全缺失）|
| `OFFLINE_COMPENSATION`    | 13.离线补偿&补发  | （新增）                | 历史数据无对应项，v1.7 首次出现（原 v1.6.1 完全缺失）|
| `TIMED_REMINDER`          | 6+7.限时提醒+错误文案 | （新增）              | 历史数据无对应项，v1.7 首次出现（原 v1.6.1 完全缺失；合并 v1.6.1 散落的限时提醒 + 错误文案专项）|

> **新增大类说明**：6 大类（`GUIDE_HIGHLIGHT` / `SOCIAL_PROMPT` / `OPS_PUSH_PROMPT` / `STATE_CHANGE_DIALOG` / `COMPLIANCE_PROMPT` / `OFFLINE_COMPENSATION` + `TIMED_REMINDER`），全部对应原 v1.6.1 HINT 暂存版"原定义完全缺失"的 6 大类场景（用户细化补充）。
>
> **与 UI 模块严格隔离**：`HINT` 仅覆盖临时弹出/一次性反馈，UI 覆盖页面常驻控件/静态布局；任何归属模糊项，回归 **临时 vs 常驻 判定法**（见 §4.10.5）。

### 9.8 SPECIAL 测试类型兼容映射

> **v1.11 SPECIAL 完整覆盖**：从原 v1.1 5 个模糊枚举（`DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` / `WEAK_NETWORK` / `SWITCH_TO_BACKGROUND` / `ANTI_CHEAT`）扩展为 9 个 v1.2 枚举（`BOUNDARY_EXTREME` / `ANTI_CHEAT` / `WEAK_NET_RATE_LIMIT` / `BG_FG_SWITCH` / `SERVER_HA_RISK` / `VERSION_COMPAT_BIZ` / `CHANNEL_GRAY_BIZ` / `COMPLIANCE_RISK` / `RESOURCE_EXHAUST`）。

| v1.2 枚举（现行）         | 归属子类       | v1.1 旧枚举（已废弃）   | 兼容规则（数据加载时执行）|
| ------------------------- | -------------- | ----------------------- | -------------------------|
| `BOUNDARY_EXTREME`        | A.边界极端场景 | （新增）                | 历史数据无对应项，v1.11 首次出现（含原 `DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` 客户端业务层语义）|
| `ANTI_CHEAT`              | B.反作弊 / 数据安全 | `ANTI_CHEAT`       | 1:1 映射（语义升级：扩展为"反作弊+数据安全+参数篡改+存储校验"）|
| `WEAK_NET_RATE_LIMIT`     | C.弱网 / 限流  | `WEAK_NETWORK`         | 1:1 映射（语义升级：扩展为"网络异常+流量限流+防雪崩"）|
| `BG_FG_SWITCH`            | D.前后台切换   | `SWITCH_TO_BACKGROUND`  | 1:1 映射（语义升级：扩展为"切后台+进程被杀+资源恢复"）|
| `SERVER_HA_RISK`          | E.宕机/并发/高危 | （新增）              | 历史数据无对应项，v1.11 首次出现（含原 `HIGH_FREQ_PACKET` 服务端 HA 语义）|
| `VERSION_COMPAT_BIZ`      | F.版本兼容     | （新增）                | 历史数据无对应项，v1.11 首次出现（原 v1.1 完全缺失）|
| `CHANNEL_GRAY_BIZ`        | G.渠道/灰度    | （新增）                | 历史数据无对应项，v1.11 首次出现（原 v1.1 完全缺失）|
| `COMPLIANCE_RISK`         | H.合规风控     | （新增）                | 历史数据无对应项，v1.11 首次出现（原 v1.1 完全缺失）|
| `RESOURCE_EXHAUST`        | I.资源耗尽     | （新增）                | 历史数据无对应项，v1.11 首次出现（原 v1.1 完全缺失）|

> **拆分说明**：
> - v1.1 旧 `DUPLICATE_PACKET` 在 v1.2 中**按场景拆分**——业务层去重（活动重复领奖）→ `BOUNDARY_EXTREME` A / 流量层限流（接口刷量）→ `WEAK_NET_RATE_LIMIT` C
> - v1.1 旧 `HIGH_FREQ_PACKET` 在 v1.2 中**按场景拆分**——客户端业务（高频点击）→ `BOUNDARY_EXTREME` A / 服务端 HA（万人并发）→ `SERVER_HA_RISK` E / 流量层限流（接口防刷）→ `WEAK_NET_RATE_LIMIT` C
> - v1.1 旧 `WEAK_NETWORK` 升级为 `WEAK_NET_RATE_LIMIT`（语义从"网络异常"扩展为"网络异常 + 流量限流 + 防雪崩"）
> - v1.1 旧 `SWITCH_TO_BACKGROUND` 升级为 `BG_FG_SWITCH`（语义从"切后台"扩展为"前后台切换 + 进程被杀 + 资源恢复"）
> - v1.1 旧 `ANTI_CHEAT` 升级为 `ANTI_CHEAT`（语义从"反作弊"扩展为"反作弊 + 数据安全 + 参数篡改 + 存储校验"）
> - 5 个全新枚举（`SERVER_HA_RISK` / `VERSION_COMPAT_BIZ` / `CHANNEL_GRAY_BIZ` / `COMPLIANCE_RISK` / `RESOURCE_EXHAUST`）——对应用户"原定义缺失的 SPECIAL 专属场景"中的 5 类
> - 旧 `DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` 的服务端/客户端归属在 S5 加载时**人工判定**——按"业务层" vs "流量层"维度分配

### 9.9 LOG 测试类型兼容映射

| v1.9 枚举（现行）                | 归属子类 | v1.1/v1.6 旧枚举 | 兼容规则（数据加载时执行）|
| --------------------------------- | -------- | ---------------- | -------------------------|
| `LOG_EVENT_TRACK`                 | A.行为埋点 | （新增）       | 历史数据无对应项（v1.1 散落在 BIZ/HINT/UI） |
| `LOG_ASSET_AUDIT`                 | B.资产审计 | `ASSET_CHANGE`（部分）| 涉及"业务侧落点"→ `BIZ_AUDIT_LOG`；涉及"全链路对账可导出"→ `LOG_ASSET_AUDIT` |
| `LOG_OPERATION`                   | C.操作日志 | `OPERATION_LOG` | 1:1 映射（语义升级加 LOG_ 前缀） |
| `LOG_MONITOR`                     | D.监控埋点 | `PROGRESS_TRIGGER`（部分）| 涉及"业务指标"→ `LOG_MONITOR`；涉及"通用行为日志"→ LOG 通用 |
| `LOG_CRASH_REPORT`                | E.崩溃日志 | `ANOMALY`（部分）| 涉及"崩溃/技术异常"→ `LOG_CRASH_REPORT`；涉及"业务异常"→ `BIZ_LOGIC` |
| `LOG_LEVEL_STORAGE`               | F.分级存储 | （新增）       | v1.9 首次出现 |
| `LOG_INTEGRITY`                   | G.完整性   | `AUDIT_TRAIL`（部分）| 涉及"业务审计链"→ `BIZ_AUDIT_LOG`；涉及"日志完整性"→ `LOG_INTEGRITY` |
| `LOG_FIELD_COMPLIANCE`            | H.字段合规 | （新增）       | v1.9 首次出现 |
| `LOG_TRACE`                       | I.溯源     | `AUDIT_TRAIL`（部分）| 涉及"线上问题溯源"→ `LOG_TRACE` |
| `LOG_SECURITY`                    | J.安全日志 | （新增）       | v1.9 首次出现（v1.1 完全缺失） |
| `LOG_THIRD_PARTY`                 | K.第三方   | （新增）       | v1.9 首次出现（v1.1 完全缺失） |
| `LOG_ISOLATION`                   | L.隔离     | （新增）       | v1.9 首次出现（v1.1 完全缺失） |
| `LOG_REPORT_FAULT_TOLERANT`       | M.上报容错 | （新增）       | v1.9 首次出现（v1.1 完全缺失） |

> **v1.6 → v1.9 重大变更**：v1.6 时代日志/埋点/崩溃归属 UTIL J（`STORAGE_LOG`）；
> v1.6.1 UTIL 收窄到"底层 SDK"，日志业务侧迁出；
> v1.9 LOG 完整承接——LOG 管"业务规范/审计/埋点触发/合规"、UTIL 管"底层 SDK/采集/上报框架"。
>
> **拆分说明（与 BIZ-I `BIZ_AUDIT_LOG` 边界切分）**：
> - **`LOG_ASSET_AUDIT`**：测"全链路流水可对账"——跨业务正负匹配、batch_id 聚合、跨服对账、可导出
> - **`BIZ_AUDIT_LOG`**：测"业务侧落点规范"——单笔业务日志格式正确、字段齐全、有审计链
> - 同一笔业务 → BIZ-I 校验"是否写日志"，LOG 校验"日志能否对账"
>
> **拆分说明（与 SPECIAL `ANTI_CHEAT` 边界切分）**：
> - **`LOG_SECURITY`**：测"作弊检测日志留痕"——检测到外挂写日志
> - **`SPECIAL` `ANTI_CHEAT`**：测"反作弊业务逻辑"——检测算法、封号业务

---

## 10. 模块测试点模板（S5 准入物料）

> **目的**：每个模块的"测试点种子"——作为 S5（测试点生成）阶段的**准入物料**，
> 提高 AI 推理生成质量，避免漏点/错点。
>
> **位置**：`knowledge/public/module_templates/`
>
> **维护者**：「模块定义维护人」（本角色）

### 10.1 模板结构

每个模块 1 概览 + N 子模板：

```
module_templates/
  _common_structure.md        ← 通用 5 段结构（每模板都遵循）
  UI.md + UI/                 ← 模块概览 + 子类
    A_*.md
    B_*.md
    ...
  BIZ.md + BIZ/
  ...
```

### 10.2 子模板 5 段结构

| 段                | 内容                                                            |
| ----------------- | --------------------------------------------------------------- |
| 1. 子类定义       | 测什么 / 不测什么 / 与其他子类的差异                            |
| 2. 典型场景       | 3-10 个具体业务场景                                              |
| 3. 种子测试点     | **全覆盖**——按你给的细化明细，每个子类每种类型 1-N 个种子 TP |
| 4. 边界陷阱       | 与相邻模块/子类的边界区分 + 常见误判                            |
| 5. 验证证据       | 视觉/日志/数据/性能证据清单                                    |

> 完整结构规范见 `knowledge/public/module_templates/_common_structure.md`

### 10.3 与 S5 的集成（自动加载）

S5 prompt 内置规则：

> 当 `backlog.json` 的 `epic.module == XXX` 时：
> 1. **必读** `knowledge/public/module_templates/<MODULE>.md`（模块概览）
> 2. **按需读** `knowledge/public/module_templates/<MODULE>/<X>_*.md`（按 story 涉及的子类）
> 3. 模板的"种子 TP"作为推理生成的基础，结合真实 story 信息展开

### 10.4 准入物料检查

S5 启动时检查：

| 物料                                  | 缺失时                            |
| ------------------------------------- | --------------------------------- |
| `module_templates/<MODULE>.md`        | **warning**（不阻断）— 退化为无模板推理 |
| `module_templates/<MODULE>/<X>.md`    | **不阻断**（按需加载）              |
| 模块名不在 8 模块总表                  | **阻断** + 生成 `fail_report_S5.md` |

### 10.5 当前进度

| 模块   | 概览 | 子模板数 | 状态      | 备注                       |
| ------ | ---- | -------- | --------- | -------------------------- |
| UI     | ✅    | 10       | v1.0 完整 | 你已给 8 大类细化          |
| CONFIG | ✅    | 11       | v1.0 完整 | 你已给 5 段+5 大类细化（含服务端/游戏专项）|
| UTIL    | ✅    | 16       | v1.6.1 裁剪 | 你已给 9 原有+7 新增 16 大类细化（含游戏专项）；v1.6.1 收窄为底层基础工具 |
| BIZ    | ✅    | 11       | v1.7 完整 | 你已给 5 段+4 新增大类细化（含游戏专项/边界区分）；建立 §4.8 BIZ 细分索引 + §9.5 兼容映射 + §1 总表完整描述 + §4 矩阵扩展；238 个种子 TP（A-I 各 20-30）+ P 40 = 278 |
| LINK   | ✅    | 8        | v1.8 完整 | 6 子模板（A 内部业务关联 / B 跨服务 / C 多端一致性 / D 外部第三方 / E 跨模块资源互通 / F 对外数据透出）+ O_boundary（7 大类边界 + 7 误判案例 + 判定流程图）+ P_game_specific（5 游戏子领域）= 共 8 文件；UTIL vs LINK "水管 vs 业务"边界规则在 8 文件中持续交叉引用 |
| SPECIAL| ✅    | 11（9 测试子模板 + O 边界 + P 游戏专项）| v1.11 完整 | 你已给 5 原有+4 新增 9 大类细化（含边界/反作弊/弱网/前后台/宕机/版本兼容/渠道灰度/合规/资源耗尽）+ 边界隔离 vs UTIL/BIZ/LINK/UI/HINT/LOG/CONFIG 7 模块；建立 §4.10 SPECIAL 细分索引 + §9.7 兼容映射 + §1 总表完整描述 + §4 矩阵扩展；192 个种子 TP（A-I 各 20 + P 12）；SPECIAL = 异常/高危/对抗/极限/合规/资源耗尽 业务规则；底层归 UTIL、正常归 BIZ、跨服正常归 LINK |
| LOG    | ✅    | 15（13 测试子模板 + O 边界 + P 游戏专项）| 13 | v1.9 完整 | 你已给 9 段+4 新增大类细化（含游戏专项/边界区分/与 UTIL 严格隔离）；建立 §4.12 LOG 细分索引 + §9.9 兼容映射 + §1 总表完整描述 + §4 矩阵扩展；321 个种子 TP（A-M 各 25-30）+ P 32 = 353；LOG vs BIZ-I `BIZ_AUDIT_LOG` 边界切分（LOG-B 测"全链路对账"、BIZ-I 测"业务侧落点"）；UTIL/J_log_moved_to_LOG.md 占位文件已删除 |
| HINT   | ✅    | 16（1 概览 + 13 测试子模板 + O 边界 + P 游戏专项）| v1.7+ 完整 | 13 大类职责边界 + 与 UI 关键边界隔离 + 临时 vs 常驻 判定法已落地；建立 16 文件子模板（A_*.md ~ M_*.md + O_boundary.md 含 7 模块边界对照 + 8 误判案例 + 判定流程图 + P_game_specific.md 含 5 游戏子领域）；**250 个种子 TP**（A20+B25+C20+D20+E20+F15+G20+H15+I15+J15+K15+L20+M15=235 + P 15）；§1 总表 / §4.11 完整索引 / §4.11.5 子类索引 / §9.7 兼容映射已建立；HINT vs UI 严格隔离——HINT 测"内容/触发/文案"、UI F.GUIDE_HINT 测"样式/位置/动画"，无重叠 |

### 10.6 维护流程

- **新增子类模板**：沿用 5 段结构，文件名 `X_<name>.md`（字母顺序）
- **修改模板**：直接改对应文件，无需改 S5 prompt（prompt 按路径加载）
- **废弃模板**：改名 `_deprecated_<原名>.md` 保留 30 天，在 `_common_structure.md` 登记
- **commit 前缀**：`[MODULES-TEMPLATE]`

### 10.7 LOG 模块特殊维护说明

- **LOG vs UTIL 严格隔离是 v1.9 核心**：每次 LOG 子模板新增/修改时，必须复核 `LOG/O_boundary.md` §4 速查表是否需要追加
- **LOG vs BIZ-I 边界切分**：
  - 测"业务侧落点是否完整" → `BIZ_AUDIT_LOG`
  - 测"全链路流水对账可导出" → `LOG_ASSET_AUDIT`
  - 同一笔业务 → BIZ-I 校验"是否写日志"，LOG 校验"日志能否对账"
- **v1.6.1 占位文件清理**：LOG 子模板落地后必须删除 `UTIL/J_log_moved_to_LOG.md`（已完成）

### 10.8 跨版本编号管理

- **§4.5-§4.12 编号保留**：UI=§4.5 / CONFIG=§4.6 / UTIL=§4.7 / BIZ=§4.8 / LINK=§4.9 / SPECIAL=§4.10 / HINT=§4.11 / LOG=§4.12
- **§9.1-§9.9 编号保留**：UI=§9.1 / CONFIG=§9.3 / UTIL=§9.4 / BIZ=§9.5 / LINK=§9.6 / HINT=§9.7 / SPECIAL=§9.8 / LOG=§9.9
- **新增模块时插入已有编号之间**（不要 append 到末尾，避免编号漂移）

---

## 11. 单写源规则（避免双写漂移）

> v1.3 后，模块相关内容分布在**两类文件**：
> - **MODULES.md（本文件）** = 概览 + 边界 + 索引（轻量）
> - **`knowledge/public/module_templates/`** = 明细 + 场景 + 种子 TP + 验证证据（重量）
>
> **单写源原则**："同样的内容只能在一个地方维护"——避免双写漂移。

### 11.1 内容归属表

| 内容类型               | 归属                 | 原因                                          |
| ---------------------- | -------------------- | --------------------------------------------- |
| 模块职责一句话定义     | MODULES §1 总表      | 总览必看                                      |
| 8 模块总览（CONFIG 等）| MODULES §1 总表      | 总览必看                                      |
| 模块测试类型枚举       | MODULES §4 矩阵      | S5/S6 数据契约                                |
| 模块 vs 模块边界规则   | MODULES §4.5 I + `module_templates/UI/I_boundary.md` | 边界是 SSoT 核心；双写但同步机制（每次改 I 都同步 §4.5）|
| 子类明细（控件基础/纯前端交互/...）| **`module_templates/UI/A_*.md` 等** | 明细是重量内容，单独维护 |
| 典型场景               | `module_templates/UI/<X>_*.md`  | 场景随实现变化，独立维护          |
| 种子测试点（TP）       | `module_templates/UI/<X>_*.md`  | TP 是 S5 推理输入，独立维护      |
| 验证证据（视觉/日志/...）| `module_templates/UI/<X>_*.md` | 证据随测试策略变化，独立维护      |
| 误判案例 + 决策树      | `module_templates/UI/I_boundary.md` | 误判案例积累需要独立维护        |
| 游戏专项               | `module_templates/UI/J_game_specific.md` | 游戏专属，独立维护            |

### 11.2 同步机制

- **改 MODULES §4.5 I 边界表** → **必须**同步改 `I_boundary.md`（每次）
- **改 `I_boundary.md` 边界表** → **必须**同步改 MODULES §4.5 I（每次）
- **改 `I_boundary.md` 误判案例 / 决策树** → **无需**改 MODULES（独立维护）
- **改 `A_*.md` ~ `H_*.md` 明细 / 场景 / 种子 TP** → **无需**改 MODULES（独立维护）
- **改 MODULES §1 / §4 矩阵** → **必须**同步改相关模板的"子类代码"行（防止枚举漂移）

### 11.3 检查清单（修改前自问）

| 修改点                                | 必做的同步                              |
| ------------------------------------- | --------------------------------------- |
| §1 总表某模块职责                     | 检查对应模板概览是否仍准确              |
| §4 矩阵某模块测试类型枚举             | 检查对应模板 A-H 的"子类代码"行         |
| §4.5 I 边界表                         | 同步 `I_boundary.md` §2 边界对照表      |
| `I_boundary.md` §2 边界对照表         | 同步 MODULES §4.5 I 边界表              |
| `I_boundary.md` §3 误判案例 / §4 决策树 | 无需同步 MODULES（独立维护）            |
| 模板 A-H 明细 / 场景 / 种子 TP        | 无需同步 MODULES（独立维护）            |

### 11.4 反模式（禁止）

- ❌ **在 MODULES.md 写"控件 8 种状态是哪些"**——这是明细，应在模板
- ❌ **在 `I_boundary.md` 复述 MODULES §4.5 I 边界表**——通过引用 §4.5 即可
- ❌ **在模板 A-H 复述 MODULES §1 UI 职责行**——通过引用 §1 即可
- ❌ **改 §4.5 I 不改 `I_boundary.md`**——会双写漂移

---

## 附录：版本历史

> 章节顺序：§1-§6 是核心定义；§4.5 是 UI 核心扩展；§8-§10 是核心扩展（影响审计/兼容映射/模板）；附录是版本历史。
> 本附录不参与编号序列。

| 版本  | 日期       | 变更                                                                                                  |
| ----- | ---------- | ----------------------------------------------------------------------------------------------------- |
| v1.1  | 2026-06-15 | 初版；合并 S2 8 模块 + S5 HINT 扩展；废弃 BASE；建立 SSOT 模式                                         |
| v1.2  | 2026-06-15 | **UI 模块深化**：从 4 个测试类型扩展为 8 大类（控件/交互/布局/静态/动效/引导/无障碍/异常）+ 边界区分 + 游戏专项，新增 §4.5 子节；维护流程加 §6.5「模块职责深化调整」|
| v1.3  | 2026-06-15 | **模块测试点模板**（S5 准入物料）落地：建立 `knowledge/public/module_templates/` 仓库 + 通用 5 段结构；UI 模块首发 10 子模板（A 控件基础 / B 纯前端交互 / C 布局适配 / D 静态展示 / E 动效 / F 引导浮窗 / G 无障碍 / H 异常场景 / I 边界区分 / J 游戏专项）+ 模块概览；新增 §10 章节；维护流程加 `[MODULES-TEMPLATE]` commit 前缀|
| v1.4  | 2026-06-15 | **职责归位 + 单写源收敛**：MODULES.md §4.5 从明细展开（100+ 行）→ 概览/边界/索引（67 行）；明细/场景/种子 TP 全部委托给 `module_templates/UI/`；新增 §11「单写源规则」章节（内容归属表 + 同步机制 + 反模式）；§1 总表 UI 职责行从 200+ 字 → 30 字；§4 矩阵 UI 行从「8 大类全覆盖」修正为「11 个 v1.2 枚举」 |
| v1.5  | 2026-06-15 | **CONFIG 模块深化**：从 4 个 v1.1 枚举扩展为 9 个 v1.2 枚举（保留 4 个 + 新增 5 个：PARSE_LOAD / VERSION_COMPAT / VALUE_LOGIC / EXPORT_PUBLISH / SERVER_CONFIG）；建立 11 大类细分（A 字段 / B 一致性 / C 跨表 / D 热更 / E 解析 / F 版本 / G 数值 / H 导出 / I 服务端 / J 边界 / K 游戏专项），覆盖用户给的 5 段+5 大类细化；新增 §4.6 CONFIG 细分索引章节；同步更新 §1 总表 + §4 矩阵 + §10 进度表 |
| v1.6  | 2026-06-15 | **UTIL 模块深化**：从 4 个 v1.1 枚举扩展为 14 个 v1.2 枚举（保留 4 个 + 新增 10 个：CURRENCY_EXCHANGE / OFFLINE_UPDATE / GM_TOOL / TEST_SCRIPT / ACCEPTANCE_CHECKLIST / STORAGE_LOG / PERF_TOOL / OPS_TOOL / SECURITY / ERROR_RECOVERY）；建立 16 大类细分（A 公共工具 / B 网络层 / C 缓存层 / D 资源管理 / E 汇率换算 / F 离线更新 / G GM 工具 / H 测试脚本 / I 策划验收 / J 存储日志 / K 性能画质 / L 运营辅助 / M 加密安全 / N 异常兜底 / O 边界 / P 游戏专项），覆盖用户给的 9 原有+7 新增 16 大类；新增 §4.7 UTIL 细分索引章节 + §9.3-9.4 兼容映射；同步更新 §1 总表 + §4 矩阵 + §10 进度表 |
| v1.7  | 2026-06-15 | **BIZ 模块深化**：从 4 个 v1.1 枚举扩展为 9 个 v1.2 枚举（`ACTIVITY_OPEN_CLOSE` 拆分为 `BIZ_LOGIC` / `BIZ_STATE_MACHINE` / `BIZ_SCHEDULED_TASK` 三类；`PROTOCOL` 升级为 `BIZ_PROTOCOL`；`DB_PERSIST` 升级为 `BIZ_DB_PERSIST`；新增 4 个完全缺失大类 `BIZ_CONCURRENCY` / `BIZ_SCHEDULED_TASK` / `BIZ_PAYMENT` / `BIZ_AUDIT_LOG`；`ENTITY_CACHE` 移交 UTIL C）；建立 11 文件细分（A 核心业务逻辑 / B 端服数据流 / C 协议交互 / D 状态机 / E 数据库持久化 / F 并发多玩家 / G 定时异步任务 / H 付费商业化 / I 日志审计 / O 边界 / P 游戏专项），覆盖用户给的 5 段原有 + 4 大类原定义完全缺失补充（并发/定时/付费/审计）+ 5 类游戏专项（战斗/社交/运营/回滚）；新增 §4.8 BIZ 细分索引章节 + §9.5 兼容映射（含 `ACTIVITY_OPEN_CLOSE` 拆分规则 + `ENTITY_CACHE` 迁移说明）；同步更新 §1 总表 + §4 矩阵 + §10 进度表 |
| v1.6.1| 2026-06-15 | **UTIL 模块职责收窄（裁剪）**：剔除 4 类高层业务辅助——日志/埋点（→LOG v1.8）、提示（→HINT v1.7）、第三方 SDK（→LINK，原计划 v1.9 提前至 v1.8 完成）、风控/反作弊（→SPECIAL v1.10）；J_storage_log 重命名为 J_storage（日志部分迁出）、N_error_recovery 缩窄为底层（业务异常迁出→BIZ v1.11）；A/B/L/M 顶部描述增加 v1.6.1 变更说明；新增 J_log_moved_to_LOG.md 占位文件（待 LOG v1.8 完成后删除）；§1 总表/§4.7 边界/§10 进度同步更新 |
| v1.6.1+| 2026-06-15 | **8 模块职责最终版 + 交叉判定规则**：BIZ/LINK/SPECIAL/LOG/HINT/CONFIG/UI 7 个模块描述按用户最终版重写；UTIL 描述加"运营批量发奖/公告后台业务 → BIZ"剔除项；新增 **§3.5 交叉场景归属判定规则**（8 条 + 8 条反向参考）；§4.7 UTIL 索引加"与各模块边界区分"一一对照（HINT/LOG/LINK/SPECIAL/UI/BIZ/CONFIG 7 个）；§4 矩阵 v1.2 枚举预规划（HINT 6 / LOG 5 / LINK 5 / SPECIAL 6 / BIZ 9）|
| v1.8  | 2026-06-15 | **LINK 模块完整落地（定义 + 子模板 + 边界）**：从原 v1.1 模糊的 3 个枚举 + v1.6.1 临时版 5 个枚举，重新归整为 **6 个 v1.2 枚举**（`INTERNAL_BIZ_LINKAGE` / `CROSS_SERVER_SYNC` / `MULTI_CLIENT_SYNC` / `EXTERNAL_THIRD_PARTY` / `CROSS_MODULE_RESOURCE` / `OUTBOUND_DATA`）；§1 总表替换为用户最终版"5 大类"定义（**与 UTIL 底层传输框架隔离**）；新增 **§4.9 LINK 细分索引**（4 子节：核心一句话 + **UTIL vs LINK "水管 vs 业务"核心区分表** + 5 大类完整覆盖 + 7 个其他模块边界对照表 + 维护原则含 3 步判定法）；新增 **§9.6 LINK 兼容映射**（含 `REGRESSION_TEST` 按场景拆分规则 + `MULTI_TENANT_SYNC` 改名为 `MULTI_CLIENT_SYNC` 语义纠正）；与 UTIL v1.6.1 "第三方 SDK→LINK" 裁剪方向 + §4.7 "vs LINK" 边界保持严格一致——UTIL 管底层能力底座、LINK 管业务互通规则、**无重叠**；**8 个模板文件全部到位**（`LINK.md` 概览 + `A_internal_biz_linkage.md` ~ `F_outbound_data.md` 6 子模板含 110 个种子 TP + `O_boundary.md` 含 7 大类边界 + 7 误判案例 + 判定流程图 + 6 子类口诀 + `P_game_specific.md` 含 5 游戏子领域含 15 个种子 TP）；同步更新 §1 总表 / §4 矩阵 / §4.9 维护原则（链接接通）/ §10 进度表 / 目录 |
| v1.7  | 2026-06-15 | **HINT 模块深化 + HINT vs UI 严格边界隔离**：从 v1.6.1 暂存版 6 枚举（`RED_DOT` / `ITEM_FLOAT` / `CURRENCY_FLOAT` / `MODAL_DIALOG` / `TOAST` / `FLOAT_NOTIFY`）扩展为 **13 个 v1.7 枚举**——保留 6 个 + 新增 7 个（`RED_DOT_BADGE` 语义升级 + `GUIDE_HIGHLIGHT` / `SOCIAL_PROMPT` / `OPS_PUSH_PROMPT` / `STATE_CHANGE_DIALOG` / `COMPLIANCE_PROMPT` / `OFFLINE_COMPENSATION` / `TIMED_REMINDER`），覆盖用户给的 7 原有细化（红点/飘字/Toast/模态/浮窗/错误文案/限时提醒）+ 6 大类原定义完全缺失补充（引导/社交/推送/状态变更/合规/离线补偿）；§1 总表 HINT 行从 1 行 30 字 → 13 大类一句话定义（含 HINT vs UI 边界声明）；新增 **§4.10 HINT 细分索引**（5 子节：核心一句话 + 13 大类完整覆盖表 + **HINT vs UI 关键边界隔离规则**（临时 vs 常驻 判定法 + 4 个举例区分）+ 8 个其他模块边界对照表 + 13 个 v1.7 枚举映射 + 维护原则）；新增 **§9.7 HINT 兼容映射**（v1.6.1 旧 6 枚举→v1.7 新 13 枚举 1:1 映射 + 7 个新枚举首现说明）；与 UI §4.5「提示的承载样式归 UI、提示内容本身归 HINT」边界声明保持严格一致；同步更新 §1 总表 / §4 矩阵 / §10 进度表 / 目录；HINT 子模板（A_*.md ~ M_*.md + O_boundary + P_game_specific）v1.7+ 后续补全 |
| v1.11 | 2026-06-15 | **SPECIAL 模块深化 + 与 UTIL/BIZ/LINK/UI/HINT/LOG/CONFIG 7 模块严格边界隔离**：从 v1.1 模糊的 5 个枚举（`DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` / `WEAK_NETWORK` / `SWITCH_TO_BACKGROUND` / `ANTI_CHEAT`）+ v1.6.1+ 临时版 6 枚举，重新归整为 **9 个 v1.2 枚举**（`BOUNDARY_EXTREME` / `ANTI_CHEAT` / `WEAK_NET_RATE_LIMIT` / `BG_FG_SWITCH` / `SERVER_HA_RISK` / `VERSION_COMPAT_BIZ` / `CHANNEL_GRAY_BIZ` / `COMPLIANCE_RISK` / `RESOURCE_EXHAUST`）；§1 总表 SPECIAL 行替换为用户最终版"5 原有+4 新增 9 大类"完整定义（边界极端/反作弊/弱网/前后台/宕机/版本兼容/渠道灰度/合规/资源耗尽 + 底层归 UTIL/正常归 BIZ/跨服正常归 LINK 边界声明）；新增 **§4.10 SPECIAL 细分索引**（6 子节：核心一句话 + **UTIL vs BIZ vs LINK vs SPECIAL "水管 vs 业务 vs 互通 vs 对抗"核心区分表** + 9 大类完整覆盖表 + 9 个其他模块边界对照表 + 9 个 v1.2 枚举映射 + 维护原则含 4 步判定法 + v1.11 SPECIAL 核心定位 6 条）；新增 **§9.7 SPECIAL 兼容映射**（v1.1 旧 5 枚举→v1.2 新 9 枚举：`DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` 按"业务层/流量层/服务端 HA"三维度拆分；`WEAK_NETWORK` 升级为 `WEAK_NET_RATE_LIMIT`；`SWITCH_TO_BACKGROUND` 升级为 `BG_FG_SWITCH`；5 个全新枚举首现说明）；§4.10 HINT 索引迁移到 §4.11（HINT 子模板待 v1.8 实施）；SPECIAL 子模板 11 个 = 9 测试子模板（A~I）+ O_boundary + P_game_specific，192 个种子 TP（A~I 各 20 + P 12）；与 UTIL v1.6.1 "风控/反作弊→SPECIAL" 裁剪方向 + §3.5 交叉判定规则 + §4.7 "vs SPECIAL" 边界保持严格一致——UTIL 管底层能力底座、BIZ 管正常业务、LINK 管业务互通、SPECIAL 管异常/对抗/容错/合规/资源耗尽，**四者无重叠**；同步更新 §1 总表 / §4 矩阵 / §10 进度表 / 目录 / 附录版本历史 |
| v1.9  | 2026-06-15 | **LOG 模块深化 + 与 UTIL 严格边界隔离**：从 v1.1 模糊的 4 个枚举（`ASSET_CHANGE` / `PROGRESS_TRIGGER` / `ANOMALY` / `AUDIT_TRAIL`）+ v1.6.1 暂存版 5 枚举（`EVENT_TRACK` / `ASSET_AUDIT` / `OPERATION_LOG` / `MONITOR` / `CRASH_REPORT`），重新归整为 **13 个 v1.9 枚举**（`LOG_EVENT_TRACK` / `LOG_ASSET_AUDIT` / `LOG_OPERATION` / `LOG_MONITOR` / `LOG_CRASH_REPORT` / `LOG_LEVEL_STORAGE` / `LOG_INTEGRITY` / `LOG_FIELD_COMPLIANCE` / `LOG_TRACE` / `LOG_SECURITY` / `LOG_THIRD_PARTY` / `LOG_ISOLATION` / `LOG_REPORT_FAULT_TOLERANT`）——按"业务规范/审计/埋点/合规"重新组织，覆盖用户给的 9 段原有（行为埋点/资产审计/操作日志/服务监控/客户端崩溃/分级存储/完整性/字段合规/问题溯源）+ 4 大类原定义完全缺失补充（安全反作弊/第三方关联/多渠道隔离/上报容错）+ 4 类游戏专项（战斗/社交/运营/兜底回滚）；§1 总表 LOG 行从 1 行 8 短语 → 13 大类一句话定义（含 LOG vs UTIL 边界声明"日志底层采集/存储 SDK、文件读写工具归 UTIL"）；新增 **§4.12 LOG 细分索引**（核心一句话 + 15 文件明细表 + 完整覆盖一句话 + **LOG vs UTIL 严格隔离对照表 12 行** + 维护原则含 2 句判定法 + LOG vs BIZ-I `BIZ_AUDIT_LOG` 边界切分说明）；新增 **§9.9 LOG 兼容映射**（v1.1 旧 4 枚举→v1.9 新 13 枚举：`ASSET_CHANGE` / `PROGRESS_TRIGGER` 按"业务侧/聚合"分；`ANOMALY` 按"崩溃/业务异常"分；`AUDIT_TRAIL` 按"审计链/溯源"分；4 个 v1.9 全新枚举首现说明）；LOG 子模板 15 文件 = 13 测试子模板（A~M）+ O_boundary（重点 vs UTIL 12 场景 + 10 误判案例 + LOG vs UTIL 严格隔离速查表）+ P_game_specific（4 类游戏专项 32 个 TP）；LOG 子模板 TP 统计 A25 + B30 + C30 + D25 + E30 + F25 + G25 + H26 + I25 + J25 + K25 + L25 + M25 = **321 个种子 TP** + P 32 = **353 个种子 TP**；与 UTIL v1.6.1 "日志/埋点/崩溃→LOG" 裁剪方向 + §3.5 交叉判定规则 + §4.7 "vs LOG" 边界保持严格一致——**UTIL 管底层 SDK/采集/上报框架、LOG 管业务规范/审计/埋点触发/合规，无重叠**；同步更新 §1 总表 / §4 矩阵 / §4.7 UTIL J 行注释 / §10 进度表 / 目录 / 附录版本历史；UTIL/J_log_moved_to_LOG.md 占位文件删除 |
| v1.7+ | 2026-06-15 | **HINT 模块完整落地（16 文件全到位）+ HINT vs UI 严格边界隔离**：在 v1.7"边界+职责优化"基础上，补全 16 个子模板文件——`HINT.md` 模块概览 + 13 测试子模板（A 红点 / B 资源飘字 / C 战斗飘字 / D 模态弹窗 / E Toast / F 浮窗 / G 限时提醒+错误文案 / H 新手引导 / I 社交 / J 运营推送 / K 状态变更 / L 风控合规 / M 离线补偿）+ O_boundary（含 7 模块边界对照 + 8 误判案例 + 判定流程图 + HINT vs UI "临时 vs 常驻"判定法 + 5 个举例区分）+ P_game_specific（含 5 类游戏专项 战斗/社交/运营/合规/补偿）；HINT 子模板 TP 统计 A20 + B25 + C20 + D20 + E20 + F15 + G20 + H15 + I15 + J15 + K15 + L20 + M15 = **235 个种子 TP** + P 15 = **250 个种子 TP**；与 UI §4.5 F 子类 `GUIDE_HINT`（承载样式）严格隔离——UI F 测样式/位置/动画、HINT H 测内容/触发逻辑/事件驱动；与 v1.6.1 UTIL 裁剪"红点/弹窗/Toast/飘字→HINT"方向 + §3.5 交叉判定规则 + §4.7 UTIL "vs HINT" 边界保持严格一致——UTIL 管底层通知 API 框架、HINT 管玩家可见的反馈内容与触发逻辑，**无重叠**；v1.6.1 旧 `RED_DOT` 已升级为 v1.7 `RED_DOT_BADGE`（语义扩展"角标+数字"）；同步更新 §1 总表 / §4 矩阵 / §4.11 HINT 索引（"v1.7 规划"→"v1.7+ 已建"）/ §4.11.5 子类索引（新增）/ §4.11.6 维护原则（新增含 3 步判定法）/ §10 进度表 / 附录版本历史 / `module_templates/HINT.md` 概览 |
