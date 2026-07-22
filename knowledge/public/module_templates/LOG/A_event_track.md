# A. 玩家行为埋点采集

> **子类代码**：`LOG_EVENT_TRACK`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §1「用户行为埋点采集（细化游戏全场景行为）」
>
> **测什么**：玩家操作行为埋点（点击/功能/道具/副本/抽卡/商城/任务/社交/充值/活动）、生命周期行为埋点（登录/创角/切角色/切前后台/重连/删号/切服）、路径行为埋点（跳转/弹窗/引导/放弃/退出）、埋点触发时机、重复/中断/漏埋校验。
> **不测什么**：日志底层采集 SDK（归 AUX）、日志存储/上报（归 F）、埋点字段合规（归 H）、埋点链路追踪（归 I）、业务审计对账（归 BIZ-I）。
> **与其他子类的差异**：A 关注"行为埋点**业务触发**规范"——H 关注"字段合规"，I 关注"链路追溯"，D 关注"业务指标统计"。

---

## 1. 典型场景

### 场景 1：界面点击埋点
- 业务背景：商城购买按钮
- 涉及行为：玩家点击"购买"
- 触发动作：点击按钮
- 验证点：埋点上报 1 次、含按钮 ID + 时间戳

### 场景 2：功能开启埋点
- 业务背景：玩家解锁某功能（如"竞技场 Lv.10 解锁"）
- 涉及行为：玩家进入功能
- 触发动作：功能首次进入
- 验证点：埋点 `feature_unlock`

### 场景 3：道具使用埋点
- 业务背景：玩家使用血瓶
- 涉及行为：道具使用
- 触发动作：`use_item`
- 验证点：埋点含 item_id、count

### 场景 4：副本挑战埋点
- 业务背景：玩家进入副本
- 涉及行为：副本进入
- 触发动作：`dungeon_enter`
- 验证点：埋点含 dungeon_id、难度

### 场景 5：抽卡埋点
- 业务背景：玩家单抽
- 涉及行为：单次抽卡
- 触发动作：`gacha_draw`
- 验证点：埋点含卡池 ID、是否单抽

### 场景 6：商城购买埋点
- 业务背景：购买 100 钻礼包
- 涉及行为：商城购买
- 触发动作：`shop_purchase`
- 验证点：埋点含商品 ID、金额、渠道

### 场景 7：任务领取埋点
- 业务背景：玩家领取任务奖励
- 涉及行为：领奖
- 触发动作：`task_claim`
- 验证点：埋点含 task_id、奖励内容

### 场景 8：社交互动埋点
- 业务背景：玩家加好友
- 涉及行为：好友添加
- 触发动作：`add_friend`
- 验证点：埋点含 target_player_id

### 场景 9：充值埋点
- 业务背景：玩家充值 100 元
- 涉及行为：充值成功
- 触发动作：`recharge`
- 验证点：埋点含 order_id、amount、channel

### 场景 10：活动参与埋点
- 业务背景：玩家参与春日活动
- 涉及行为：活动参与
- 触发动作：`activity_enter`
- 验证点：埋点含 activity_id、入口

### 场景 11：登录/登出生命周期
- 业务背景：玩家登录
- 涉及行为：登录
- 触发动作：`login`
- 验证点：埋点含 player_id、ip、device、time

### 场景 12：创角/切角色
- 业务背景：玩家新建角色
- 涉及行为：创角
- 触发动作：`create_role`
- 验证点：埋点含 role_id、职业

### 场景 13：切前后台
- 业务背景：玩家切后台
- 涉及行为：切后台
- 触发动作：`bg_enter` / `fg_enter`
- 验证点：埋点含进入/离开时间

### 场景 14：删号/切服
- 业务背景：玩家主动删号
- 涉及行为：删号
- 触发动作：`delete_account`
- 验证点：埋点含 player_id、reason

### 场景 15：路径行为 - 弹窗查看
- 业务背景：玩家查看活动规则弹窗
- 涉及行为：弹窗打开
- 触发动作：`dialog_open`
- 验证点：埋点含 dialog_id、source

### 场景 16：路径行为 - 引导点击/放弃
- 业务背景：新手引导
- 涉及行为：玩家点引导
- 触发动作：`guide_click` / `guide_skip`
- 验证点：埋点含 guide_step、是否完成

### 场景 17：活动中途退出
- 业务背景：玩家进入副本中途退出
- 涉及行为：副本中途退出
- 触发动作：`dungeon_quit`
- 验证点：埋点含退出时间、进度

### 场景 18：重复操作不冗余
- 业务背景：玩家快速点击购买 5 次
- 涉及行为：5 次点击
- 触发动作：5 次点击
- 验证点：埋点去重、只 1 次有效埋点上报

### 场景 19：中断操作留存埋点
- 业务背景：购买进行中网络断开
- 涉及行为：操作中断
- 触发动作：断线超时
- 验证点：仍上报 `purchase_abort` 埋点

### 场景 20：无漏埋核心行为
- 业务背景：全量核心行为覆盖检查
- 涉及行为：登录/付费/关键任务
- 触发动作：审计
- 验证点：100% 核心行为有埋点

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_EVENT_TRACK）：商城购买点击埋点
- **scenario**：场景 1
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家在商城页
- **test_data**：点击"购买"按钮 1 次
- **expected**：埋点 `click_buy` 上报 1 次、含 button_id=shop_buy
- **notes**：注意"点击"vs"成功购买"——点击埋点 ≠ 业务成功埋点

### TP-002（LOG_EVENT_TRACK）：抽卡单抽埋点
- **scenario**：场景 5
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家在卡池页
- **test_data**：点击"单抽"1 次
- **expected**：埋点 `gacha_draw type=single pool_id=xxx` 上报
- **notes**：注意"单抽"vs"十连"+"免费"vs"付费"

### TP-003（LOG_EVENT_TRACK）：登录埋点
- **scenario**：场景 11
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家登录
- **test_data**：`login(player_id)`
- **expected**：埋点 `login` 含 player_id、ip、device、login_at
- **notes**：注意"首次登录"vs"重连"vs"切服登录"

### TP-004（LOG_EVENT_TRACK）：创角埋点
- **scenario**：场景 12
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家首次创角
- **test_data**：`create_role(role_id, class)`
- **expected**：埋点 `create_role` 含 role_id、class、create_at
- **notes**：注意"创角"vs"切角色"+"首次"vs"删除重建"

### TP-005（LOG_EVENT_TRACK）：切后台埋点
- **scenario**：场景 13
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家在线
- **test_data**：玩家切后台 30 分钟
- **expected**：埋点 `bg_enter` + 30 分钟后 `fg_enter`（或仅 `fg_enter` 含停留时长）
- **notes**：注意"切后台"vs"退出游戏"vs"锁屏"

### TP-006（LOG_EVENT_TRACK）：充值埋点
- **scenario**：场景 9
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家充值 100 元
- **test_data**：`recharge(100)`
- **expected**：埋点 `recharge` 含 order_id、amount=100、channel
- **notes**：注意"充值发起"vs"充值成功"——埋点要分两个时点

### TP-007（LOG_EVENT_TRACK）：副本进入埋点
- **scenario**：场景 4
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家满足副本条件
- **test_data**：`dungeon_enter(dungeon_id=10, difficulty=hard)`
- **expected**：埋点 `dungeon_enter` 含 dungeon_id、difficulty
- **notes**：注意"进入"vs"退出"+"胜利"vs"失败"

### TP-008（LOG_EVENT_TRACK）：好友添加埋点
- **scenario**：场景 8
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家 A 搜索 B
- **test_data**：`add_friend(A, B)`
- **expected**：埋点 `add_friend` 含 target_id=B、source=search
- **notes**：注意"添加"vs"接受"+"单向"vs"双向"

### TP-009（LOG_EVENT_TRACK）：任务领奖埋点
- **scenario**：场景 7
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家日常任务可领
- **test_data**：`task_claim(task_id, day=1)`
- **expected**：埋点 `task_claim` 含 task_id、day、reward
- **notes**：注意"任务进度"vs"任务领奖"——两个埋点

### TP-010（LOG_EVENT_TRACK）：活动参与埋点
- **scenario**：场景 10
- **module**：`LOG_EVENT_TRACK`
- **precondition**：活动开启
- **test_data**：`activity_enter(activity_id=5)`
- **expected**：埋点 `activity_enter` 含 activity_id、entry=main
- **notes**：注意"进入"vs"完成"+"入口"追踪

### TP-011（LOG_EVENT_TRACK）：路径 - 弹窗打开
- **scenario**：场景 15
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家点"活动规则"
- **test_data**：`dialog_open(dialog_id=rule_5)`
- **expected**：埋点 `dialog_open` 含 dialog_id、source=activity_5
- **notes**：注意"打开"vs"关闭"+"停留时长"

### TP-012（LOG_EVENT_TRACK）：路径 - 引导跳过
- **scenario**：场景 16
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家在引导中
- **test_data**：点击"跳过"
- **expected**：埋点 `guide_skip` 含 step、reason
- **notes**：注意"完成"vs"跳过"+"主动跳过"vs"超时跳过"

### TP-013（LOG_EVENT_TRACK）：副本中途退出
- **scenario**：场景 17
- **module**：`LOG_EVENT_TRACK`
- **precondition**：副本中
- **test_data**：玩家主动退出
- **expected**：埋点 `dungeon_quit` 含 progress=50%、duration
- **notes**：注意"主动"vs"断线"vs"踢出"

### TP-014（LOG_EVENT_TRACK）：重复点击去重
- **scenario**：场景 18
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家快速点击 5 次
- **test_data**：1s 内 5 次点击
- **expected**：埋点 1 次（去重）或 5 次（保留每次）
- **notes**：注意"业务去重"vs"埋点去重"——按业务设计

### TP-015（LOG_EVENT_TRACK）：操作中断上报
- **scenario**：场景 19
- **module**：`LOG_EVENT_TRACK`
- **precondition**：购买进行中
- **test_data**：网络断开
- **expected**：埋点 `purchase_abort` 上报、含 stage
- **notes**：注意"中断"vs"取消"vs"失败"

### TP-016（LOG_EVENT_TRACK）：登录重连埋点
- **scenario**：场景 11
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家在线、断线 30s
- **test_data**：重连
- **expected**：埋点 `reconnect` 含 disconnect_reason、reconnect_at
- **notes**：注意"重连"vs"重新登录"

### TP-017（LOG_EVENT_TRACK）：删号埋点
- **scenario**：场景 14
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家主动删号
- **test_data**：`delete_account(player_id)`
- **expected**：埋点 `delete_account` 含 reason、retain_days
- **notes**：注意"主动"vs"封号"vs"超时"

### TP-018（LOG_EVENT_TRACK）：切服埋点
- **scenario**：场景 14
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家从服 A 切到服 B
- **test_data**：`switch_server(A, B)`
- **expected**：埋点 `switch_server` 含 from=A、to=B、reason=player_request
- **notes**：注意"主动"vs"合服"

### TP-019（LOG_EVENT_TRACK）：无漏埋核心行为
- **scenario**：场景 20
- **module**：`LOG_EVENT_TRACK`
- **precondition**：全量核心行为清单
- **test_data**：审计
- **expected**：100% 核心行为有对应埋点
- **notes**：注意"核心"vs"次要"+"埋点覆盖率"指标

### TP-020（LOG_EVENT_TRACK）：触发时机精准
- **scenario**：场景 1
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家点击"购买"
- **test_data**：观察埋点时间戳
- **expected**：埋点时间 = 业务时点（不是 UI 渲染时、不是网络回包时）
- **notes**：注意"业务时点"vs"技术时点"

### TP-021（LOG_EVENT_TRACK）：埋点失败不阻塞业务
- **scenario**：场景 1
- **module**：`LOG_EVENT_TRACK`
- **precondition**：埋点上报服务宕机
- **test_data`：玩家点击"购买"
- **expected**：业务正常、埋点失败仅写本地缓存
- **notes**：与 F 联容错配合

### TP-022（LOG_EVENT_TRACK）：埋点去重不漏埋
- **scenario**：场景 18
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家 1s 10 次点击
- **test_data`：10 次点击
- **expected**：10 次都生成埋点事件、由采集层去重（不丢业务）
- **notes**：注意"业务事件"vs"上报次数"分离

### TP-023（LOG_EVENT_TRACK）：删号审计
- **scenario**：场景 14
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家删号
- **test_data`：观察后续 30 天
- **expected**：30 天内可恢复、恢复后保留历史埋点
- **notes**：注意"软删"vs"硬删"

### TP-024（LOG_EVENT_TRACK）：跨端埋点统一
- **scenario**：场景 11
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家 iOS + Android 同一账号
- **test_data`：iOS 登录
- **expected**：埋点含 platform=ios；切 Android 登录后埋点 platform=android
- **notes**：注意"跨端"vs"同端"+"device_id 统一"

### TP-025（LOG_EVENT_TRACK）：埋点字段完整性
- **scenario**：场景 1
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家点击
- **test_data**：观察埋点字段
- **expected**：含 player_id、role_id、event_id、time、device、version、server_id
- **notes**：与 H 字段合规配合

---

## 3. 边界陷阱

### 边界 1：vs H. 字段合规
- **混淆点**：「埋点"字段"」——A 测业务触发、H 测字段
- **判定规则**：测"什么时候触发、触发什么事件" → A；测"字段是否齐全/是否脱敏" → H
- **实例**：购买点击触发 → A-001；埋点字段必填校验 → H

### 边界 2：vs I. 链路追踪
- **混淆点**：「埋点"链路"」——A 测单点埋点、I 测链路串联
- **判定规则**：测"单次埋点内容" → A；测"跨事件 trace_id 串联" → I
- **实例**：购买点击埋点 → A-001；购买-支付-发货 trace_id → I

### 边界 3：vs D. 监控
- **混淆点**：「行为"指标"」——A 测单点、D 测聚合
- **判定规则**：测"单次行为埋点" → A；测"行为聚合指标（活跃/转化）" → D
- **实例**：登录埋点 → A-003；DAU/MAU 指标 → D

### 边界 4：vs AUX（埋点 SDK）
- **混淆点**：「埋点"上报"」——A 测业务触发规则、AUX 测 SDK
- **判定规则**：测"业务应该埋什么点" → A；测"SDK 怎么采集/上报" → AUX
- **实例**：抽卡埋点触发 → A；埋点 SDK 断网缓存 → AUX

### 边界 5：vs BIZ（业务操作）
- **混淆点**：「购买"行为"」——A 测埋点、BIZ 测业务
- **判定规则**：测"埋点业务规则" → A；测"购买业务逻辑" → BIZ
- **实例**：购买按钮埋点 → A；购买扣款业务 → BIZ

---

## 4. 验证证据

### 视觉证据
- 埋点管理后台截图（事件列表）
- 漏埋告警截图

### 日志证据
- 埋点事件 `EVENT_TRACK event_id=xxx player_id=xxx time=xxx`
- 漏埋扫描 `MISSING_EVENT event=xxx`
- 重复埋点 `DUPLICATE_EVENT event=xxx count=N`

### 数据证据
- 埋点事件表 `event_log.event_id, player_id, time, payload`
- 埋点覆盖率（核心行为 ÷ 实际埋点数）
- 埋点字段必填率
- 埋点触发时机分布
- 埋点去重率

### 性能证据
- 单次埋点延迟 < 10ms
- 批量埋点合并上报 < 100ms
- 埋点不上报不阻塞业务 < 50ms
- 埋点覆盖率 = 100%
