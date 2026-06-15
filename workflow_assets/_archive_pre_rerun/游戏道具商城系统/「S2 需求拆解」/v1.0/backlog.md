# Requirement Backlog — 游戏道具商城系统

**Version**: v1.0
**Date**: 2026-06-12
**Source**: S1.5 exit_permission (quality_level: MEDIUM)
**Fallback rules applied**: 2 / 2
**Open questions handled**: 2 (L1 折扣叠加, L2 VIP时效)

---

## Epic & Story Summary

| 指标 | 数量 |
|------|------|
| Epics | 10 |
| Stories | 27 |
| 需求对象总数 | 10 |
| 功能点总数 | 75+ |
| Fallback Stories | 2 (marked with [fallback]) |
| [待确认] 分类边界 | 2 (L1, L2) |

---

## Epic & Story 一览

| Epic ID | 模块 | 名称 | Story数 | 需求对象 | 功能点数 | 估算 |
|---------|------|------|---------|---------|---------|------|
| BIZ-PURCHASE | BIZ | 购买流程 | 5 | 购买流程 | 12 | 3周 |
| CONFIG-VIP | CONFIG | VIP体系 | 3 | VIP配置 | 8 | 2周 |
| CONFIG-DISCOUNT | CONFIG | 促销配置 | 5 | 促销配置 | 12 | 2周 |
| UI-SHOP | UI | 商城首页 | 3 | 道具展示 | 9 | 1周 |
| UI-DETAIL | UI | 道具详情页 | 2 | 道具详情 | 6 | 1周 |
| BIZ-ORDER | BIZ | 订单管理 | 2 | 订单查询 | 6 | 1周 |
| AUX-CACHE | AUX | 道具数据缓存 | 1 | 数据缓存 | 4 | 0.5周 |
| AUX-EXRATE | AUX | 汇率配置 | 1 | 汇率管理 | 4 | 0.5周 |
| LINK-PAYMENT | LINK | 支付接口 | 1 | 支付集成 | 3 | 1周 |
| LOG-PAYMENT | LOG | 支付日志 | 1 | 操作日志 | 3 | 0.5周 |
| SPECIAL-VIP-CHANGE | SPECIAL | VIP等级变更 | 2 | 等级变更 | 6 | 0.5周 |

---

## Epics & Stories

---

### BIZ-PURCHASE: 购买流程

**Module**: BIZ | **Estimated**: 3 weeks | **Priority Epic**: Yes

#### BIZ-PURCHASE-001: 购买确认流程

**Acceptance Criteria:**
- AC1: 玩家在道具详情页点击购买后，展示购买确认弹窗，包含道具名称、数量、总价
- AC2: 确认弹窗显示玩家当前余额和所需金额，余额不足时购买按钮禁用
- AC3: 购买前需完成数量选择（1-99），数量超出时前端拦截并提示

**Precondition:** 玩家已登录，余额充足，道具可购买
**Input:** 道具ID，购买数量
**Expected Output:** 购买确认弹窗（道具名称+数量+总价+余额对比）

---

#### BIZ-PURCHASE-002: 游戏币支付

**Acceptance Criteria:**
- AC1: 玩家选择游戏币支付后，系统扣减对应游戏币余额，余额冻结/锁定防止重复扣款
- AC2: 扣款成功后道具立即到账，到账时间 < 3秒
- AC3: 余额不足时拒绝交易并提示，扣款失败时原路回滚

**Precondition:** 玩家游戏币余额 >= 道具价格
**Input:** 道具ID，购买数量，游戏币余额
**Expected Output:** 扣款成功+道具到账，或余额不足拒绝

---

#### BIZ-PURCHASE-003: 人民币支付与汇率换算

**Acceptance Criteria:**
- AC1: 玩家选择人民币支付时，程序以订单创建时的汇率为准进行换算，汇率锁定不随后续变动
- AC2: 各渠道（Android/iOS/Web）按各自的汇率配置独立换算
- AC3: 汇率换算以分为最小单位，角分四舍五入

**Precondition:** 玩家选择人民币支付，汇率配置存在
**Input:** 道具ID，数量，渠道ID，汇率表
**Expected Output:** 换算后的人民币价格（角分四舍五入），汇率锁定订单

---

#### BIZ-PURCHASE-004: 道具即时到账

**Acceptance Criteria:**
- AC1: 支付成功后道具立即到账，无延迟
- AC2: 到账后玩家背包/仓库中可见对应道具
- AC3: 到账结果通知前端刷新背包数据

**Precondition:** 支付成功
**Input:** 玩家ID，道具ID，数量
**Expected Output:** 道具到账确认，背包数据更新

---

#### BIZ-PURCHASE-005: 购买邮件通知

**Acceptance Criteria:**
- AC1: 购买成功后发送系统邮件，邮件字段包含：玩家名称、道具名称、购买数量、金额（含币种）、购买时间、订单号
- AC2: 邮件异步发送，不阻塞购买流程，支持重试机制
- AC3: 发送时机为购买流程完成后

**Precondition:** 购买流程完成，道具到账成功
**Input:** 订单号，玩家ID，道具信息，购买信息
**Expected Output:** 邮件发送成功（异步），邮件字段完整

**来源**: clarification (P0 Q5)

---

### CONFIG-VIP: VIP体系

**Module**: CONFIG | **Estimated**: 2 weeks | **Priority Epic**: Yes

#### CONFIG-VIP-001: VIP等级配置管理

**Acceptance Criteria:**
- AC1: 策划可通过配置后台编辑VIP等级规则（VIP1/2/3的折扣比例、解锁条件）
- AC2: 各等级有独立解锁条件（累计消费额/在线时长/持有道具等类型）
- AC3: 配置表变更后实时生效（以配置表最新数据为准）

**Precondition:** 策划登录配置后台
**Input:** VIP等级配置数据（折扣比例，解锁条件）
**Expected Output:** 配置保存成功，VIP等级规则更新

**来源**: clarification (P0 Q1)

---

#### CONFIG-VIP-002: VIP折扣计算

**Acceptance Criteria:**
- AC1: VIP1享95折，VIP2享9折，VIP3享85折
- AC2: VIP折扣在结算时自动计算（不可叠加，详见CONFIG-DISCOUNT）
- AC3: VIP等级变更后折扣判定实时生效

**Precondition:** 玩家为VIP用户，VIP等级已配置
**Input:** 玩家ID，原始价格，VIP等级
**Expected Output:** VIP折扣后价格

---

#### CONFIG-VIP-003: VIP专属道具可见性

**Acceptance Criteria:**
- AC1: VIP专属道具仅对对应等级及以上VIP用户可见
- AC2: 非VIP用户或等级不足时，道具不在商城中展示
- AC3: 玩家尝试访问专属道具URL时返回权限不足提示

**Precondition:** 玩家登录，已知VIP等级
**Input:** 玩家ID，道具ID
**Expected Output:** VIP专属道具可见/隐藏判定结果

**来源**: original

---

### CONFIG-DISCOUNT: 促销配置

**Module**: CONFIG | **Estimated**: 2 weeks

#### CONFIG-DISCOUNT-001: 促销配置管理

**Acceptance Criteria:**
- AC1: 策划可通过配置后台/配置文件配置促销规则
- AC2: 配置项包含：促销名称、活动时间段、折扣比例/满减规则、适用道具/分类、标签字段
- AC3: 促销配置变更后实时生效

**Precondition:** 策划登录配置后台
**Input:** 促销配置数据
**Expected Output:** 促销规则保存成功

**来源**: clarification (P0 Q2, P0 Q6)

---

#### CONFIG-DISCOUNT-002: 限时折扣管理

**Acceptance Criteria:**
- AC1: 限时折扣通过配置中的折扣标签字段控制（含生效时间段）
- AC2: 程序定时检查或事件触发折扣状态变更
- AC3: 折扣标签展示样式由前端根据标签内容渲染（折扣角标、划线原价、倒计时）

**Precondition:** 限时折扣配置已存在且在生效时间窗口内
**Input:** 道具ID，当前时间
**Expected Output:** 折扣标签渲染，折扣价计算

**来源**: clarification (P0 Q6)

---

#### CONFIG-DISCOUNT-003: 满减活动管理

**Acceptance Criteria:**
- AC1: 单笔订单满100元减10元，满200元减25元
- AC2: 满减在结算时自动判定，不超过订单总额
- AC3: 满减与折扣叠加时，满减在折扣之后计算

**Precondition:** 订单金额满足满减门槛
**Input:** 订单原价
**Expected Output:** 满减后价格

**来源**: original

---

#### CONFIG-DISCOUNT-004: 新手礼包管理

**Acceptance Criteria:**
- AC1: 新注册玩家7天内可购买一次新手礼包
- AC2: 购买后礼包立即下架（同一玩家不可重复购买）
- AC3: 非新注册玩家或超过7天期限后不可购买

**Precondition:** 玩家账号注册时间 <= 7天，未购买过新手礼包
**Input:** 玩家ID，账号注册时间
**Expected Output:** 新手礼包购买资格判定

**来源**: original

---

#### CONFIG-DISCOUNT-005: 折扣叠加规则 [fallback]

**Acceptance Criteria:**
- AC1: 限时折扣先于VIP折扣执行，最终价格为 min(限时折后价, VIP折后价)
- AC2: 或按配置表中的优先级字段决定叠加规则
- AC3: 测试时需覆盖：限时折扣生效时叠加VIP折扣的边界场景

**Precondition:** 同时存在限时折扣和VIP折扣
**Input:** 原价，限时折扣比例，VIP折扣比例
**Expected Output:** 最优价（两者最低）

**来源**: fallback (L1 遗留项，触发：限时折扣与VIP折扣叠加规则)

---

### UI-SHOP: 商城首页

**Module**: UI | **Estimated**: 1 week

#### UI-SHOP-001: 热门道具展示

**Acceptance Criteria:**
- AC1: 首页推荐区展示前10个热门道具（由策划手动标记hot标签）
- AC2: 按策划配置的优先级+自然序展示，hot标签变更后前端按配置刷新时机展示
- AC3: 热门道具数量少于10个时全部展示

**Precondition:** 存在已标记hot标签的道具
**Input:** 无（前端读取配置）
**Expected Output:** 热门道具列表（前10个）

**来源**: clarification (P0 Q4)

---

#### UI-SHOP-002: 分类导航与道具列表

**Acceptance Criteria:**
- AC1: 分类导航栏包含：武器、时装、坐骑、消耗品、礼包
- AC2: 每页展示20个道具，显示：名称、图标、价格（渠道换算后）、折扣标签
- AC3: 点击分类后正确筛选并分页展示

**Precondition:** 玩家已登录商城首页
**Input:** 分类ID，页码
**Expected Output:** 道具列表（当前页，最多20个）

**来源**: original

---

#### UI-SHOP-003: 搜索功能

**Acceptance Criteria:**
- AC1: 支持道具名称模糊搜索（最小2个字符触发）
- AC2: 搜索结果展示匹配道具列表（名称、图标、价格）
- AC3: 无匹配结果时展示空状态提示

**Precondition:** 玩家在商城页面
**Input:** 搜索关键词（>= 2字符）
**Expected Output:** 搜索结果列表或空状态

**来源**: original

---

### UI-DETAIL: 道具详情页

**Module**: UI | **Estimated**: 1 week

#### UI-DETAIL-001: 道具详情展示

**Acceptance Criteria:**
- AC1: 道具详情页展示：名称、描述、属性加成、价格（已换算）、折扣标签
- AC2: 支持道具预览（角色穿戴效果）
- AC3: 价格显示已应用所有折扣后的最终价

**Precondition:** 玩家点击道具进入详情页
**Input:** 道具ID
**Expected Output:** 道具详情信息（完整）

**来源**: original

---

#### UI-DETAIL-002: 数量选择与购买

**Acceptance Criteria:**
- AC1: 购买数量选择范围1-99，数量超出时前端拦截
- AC2: 购买按钮在余额不足时禁用并显示提示
- AC3: 购买后更新总价实时计算

**Precondition:** 玩家在道具详情页，余额充足
**Input:** 选择数量
**Expected Output:** 总价更新（实时），购买按钮状态正确

**来源**: original

---

### BIZ-ORDER: 订单管理

**Module**: BIZ | **Estimated**: 1 week

#### BIZ-ORDER-001: 订单列表查看

**Acceptance Criteria:**
- AC1: 展示最近30天内的购买记录
- AC2: 订单字段包含：订单号、道具名称、数量、金额（含币种）、支付方式、购买时间
- AC3: 支持按时间范围和道具名称筛选

**Precondition:** 玩家已登录
**Input:** 玩家ID
**Expected Output:** 订单列表（最近30天）

**来源**: original

---

#### BIZ-ORDER-002: 订单详情查看

**Acceptance Criteria:**
- AC1: 点击订单可查看完整订单详情
- AC2: 订单详情包含所有购买信息及邮件通知状态

**Precondition:** 玩家有订单记录
**Input:** 订单号
**Expected Output:** 订单详情页

**来源**: original

---

### AUX-CACHE: 道具数据缓存

**Module**: AUX | **Estimated**: 0.5 week

#### AUX-CACHE-001: 道具数据缓存

**Acceptance Criteria:**
- AC1: 道具数据缓存5分钟（配置变更时主动失效）
- AC2: 缓存失效后自动从配置表重新加载
- AC3: 缓存命中率有监控埋点

**Precondition:** 道具数据存在
**Input:** 道具ID
**Expected Output:** 道具数据（来自缓存或重新加载）

**来源**: original

---

### AUX-EXRATE: 汇率配置

**Module**: AUX | **Estimated**: 0.5 week

#### AUX-EXRATE-001: 汇率表管理

**Acceptance Criteria:**
- AC1: 各渠道（Android/iOS/Web）有独立的汇率配置
- 程序启动时加载汇率表，支持热更新
- AC2: 汇率下单时锁定（以订单创建时的汇率为准）

**Precondition:** 汇率配置存在
**Input:** 渠道ID，基准价（人民币）
**Expected Output:** 渠道换算后价格

**来源**: clarification (P0 Q3)

---

### LINK-PAYMENT: 支付接口

**Module**: LINK | **Estimated**: 1 week

#### LINK-PAYMENT-001: 支付接口集成

**Acceptance Criteria:**
- AC1: 游戏币支付走内部账户系统扣款
- AC2: 人民币支付调用渠道支付接口（Android/iOS/Web各渠道独立）
- AC3: 支付结果回调后更新订单状态

**Precondition:** 玩家发起支付，选择支付方式
**Input:** 订单信息，支付方式
**Expected Output:** 支付结果（成功/失败）

**来源**: original

---

### LOG-PAYMENT: 支付日志

**Module**: LOG | **Estimated**: 0.5 week

#### LOG-PAYMENT-001: 支付操作日志

**Acceptance Criteria:**
- AC1: 所有支付操作需记录日志（日志字段：玩家ID、道具ID、数量、金额、支付方式、时间戳、结果）
- AC2: 日志需持久化存储，支持审计查询
- AC3: 支付异常时记录错误码和错误信息

**Precondition:** 支付操作发生
**Input:** 支付操作上下文
**Expected Output:** 日志写入成功

**来源**: original

---

### SPECIAL-VIP-CHANGE: VIP等级变更

**Module**: SPECIAL | **Estimated**: 0.5 week

#### SPECIAL-VIP-CHANGE-001: VIP等级变更生效 [fallback]

**Acceptance Criteria:**
- AC1: VIP等级变更后折扣判定实时生效（以配置表最新数据为准）
- AC2: 变更后玩家在下次购买时立即享受新等级折扣
- AC3: 测试时需覆盖：配置表等级变更后已购玩家的折扣重新判定场景

**Precondition:** VIP等级配置发生变更
**Input:** 玩家ID，新VIP等级
**Expected Output:** 折扣判定以新等级为准

**来源**: fallback (L2 遗留项，触发：VIP等级时效)

---

#### SPECIAL-VIP-CHANGE-002: VIP等级时效处理

**Acceptance Criteria:**
- AC1: 策划在配置表中设置等级是否有时效（永久 or 定时考核）
- AC2: 当前默认按「配置即有效」处理，不自动续期
- AC3: 等级到期后按配置表定义处理（降级/保留资格）

**Precondition:** VIP等级有时效配置
**Input:** 玩家ID，当前时间，VIP时效配置
**Expected Output:** 等级有效性判定

**来源**: fallback (L2 遗留项)

---

## 遗留待确认项

| ID | 问题 | 影响Epic | 状态 |
|----|------|---------|------|
| L1 | 限时折扣与VIP折扣叠加规则 | CONFIG-DISCOUNT-005 | [待确认] 以策划配置为准 |
| L2 | VIP等级是否按时长自动降级 | SPECIAL-VIP-CHANGE-002 | [待确认] 以策划配置为准 |

---

## Fallback Rules 消费记录

| ID | 触发条件 | 补充内容 | 来源 |
|----|---------|---------|------|
| FR-1 | 限时折扣与VIP折扣叠加规则 | 默认取最优价（min），CONFIG-DISCOUNT-005生成[fallback]标注Story | derivation |
| FR-2 | VIP等级时效（是否自动降级） | 默认配置表定义即永久有效，SPECIAL-VIP-CHANGE-002生成[fallback]标注Story | derivation |

---

*由 AIDocxWorkFlow S2 需求拆解生成*
*四层结构：Epic → Story → 需求对象 → 功能点*
*详细需求对象见 requirement_objects.md*
