# A. 红点 / 角标 / 数字提醒

> **子类代码**：`RED_DOT_BADGE`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 A（v1.6.1 `RED_DOT` 升级，语义扩展为"角标+数字"）
>
> **测什么**：功能入口红点（任务/活动/邮件/背包未读标记）、数值角标（未读数/剩余次数/待领取）、特殊标记（倒计时红点/可升级/好友申请）的**显示/隐藏/同步/清除**。
> **不测什么**：红点/角标**图标本身的 UI 样式**（归 UI `F.GUIDE_HINT`，本模块测"何时显示/何时清除"的业务规则）。
> **与其他子类的差异**：A 是"事件触发"红点；UI `F.GUIDE_HINT` 是"常驻"红点样式；A 测内容/触发逻辑，F 测样式/动画。

---

## 1. 典型场景

### 场景 1：任务入口红点
- 业务背景：玩家有未完成任务奖励可领
- 涉及元素：任务按钮右上角红点
- 触发动作：完成任务
- 验证点：红点出现、领取后自动消失、跨系统同步

### 场景 2：邮件未读数字角标
- 业务背景：玩家收到未读邮件 5 封
- 涉及元素：邮件按钮右上角数字角标
- 触发动作：收到邮件
- 验证点：显示"5"、>99 显示"99+"、进入邮件后角标归零

### 场景 3：商城限时活动红点
- 业务背景：限时商城活动开启
- 涉及元素：商城按钮红点
- 触发动作：活动开启
- 验证点：红点出现、活动结束后自动消失

### 场景 4：背包新道具红点
- 业务背景：玩家获得新道具
- 涉及元素：背包按钮红点
- 触发动作：获得新道具
- 验证点：红点出现、点击进入查看后红点消失

### 场景 5：签到待领取红点
- 业务背景：每日签到有可领奖励
- 涉及元素：签到按钮红点
- 触发动作：签到未领
- 验证点：红点出现、领取后立即消失、跨日重新出现

### 场景 6：公会消息红点
- 业务背景：公会有新消息
- 涉及元素：公会按钮红点
- 触发动作：公会消息到达
- 验证点：红点出现、查看消息后消失

### 场景 7：限时副本红点
- 业务背景：限时副本可挑战次数 > 0
- 涉及元素：副本入口红点
- 触发动作：副本次数刷新
- 验证点：红点出现、次数耗尽后红点消失

### 场景 8：福利红点
- 业务背景：福利中心有可领奖励
- 涉及元素：福利按钮红点
- 触发动作：福利刷新
- 验证点：红点出现、领完后消失

### 场景 9：好友申请红点
- 业务背景：有新好友申请
- 涉及元素：好友按钮红点
- 触发动作：收到好友申请
- 验证点：红点出现、处理申请后消失

### 场景 10：可升级红点
- 业务背景：玩家等级/装备可升级
- 涉及元素：角色/装备图标红点
- 触发动作：满足升级条件
- 验证点：红点出现、升级完成后消失

---

## 2. 种子测试点（TP 模板）

### TP-001（RED_DOT_BADGE）：任务红点触发时机
- **scenario**：场景 1
- **module**：`RED_DOT_BADGE`
- **precondition**：玩家有未完成任务
- **test_data**：完成任务
- **expected**：任务按钮右上角红点出现
- **notes**：与 LOG `LOG_EVENT_TRACK` 配合（红点触发事件埋点）

### TP-002（RED_DOT_BADGE）：任务红点领取后自动清除
- **scenario**：场景 1
- **module**：`RED_DOT_BADGE`
- **precondition**：任务红点存在
- **test_data**：进入任务界面领取奖励
- **expected**：红点立即消失、刷新任务按钮无红点
- **notes**：注意异步清除时序

### TP-003（RED_DOT_BADGE）：邮件数字角标显示
- **scenario**：场景 2
- **module**：`RED_DOT_BADGE`
- **precondition**：收到 5 封未读邮件
- **test_data**：查看邮件按钮
- **expected**：显示数字"5"
- **notes**：测试数字 1-99 区间

### TP-004（RED_DOT_BADGE）：邮件数字角标 99+
- **scenario**：场景 2
- **module**：`RED_DOT_BADGE`
- **precondition**：收到 150 封未读邮件
- **test_data**：查看邮件按钮
- **expected**：显示"99+"，不显示"150"
- **notes**：边界值测试

### TP-005（RED_DOT_BADGE）：邮件角标查看后归零
- **scenario**：场景 2
- **module**：`RED_DOT_BADGE`
- **precondition**：邮件未读
- **test_data**：进入邮件界面 → 阅读全部邮件
- **expected**：邮件按钮角标归零/消失
- **notes**：单封 vs 全部已读逻辑

### TP-006（RED_DOT_BADGE）：活动红点定时出现
- **scenario**：场景 3
- **module**：`RED_DOT_BADGE`
- **precondition**：限时活动配置开启
- **test_data**：到达活动开始时间
- **expected**：商城按钮红点自动出现
- **notes**：与服务端时间同步

### TP-007（RED_DOT_BADGE）：活动红点定时消失
- **scenario**：场景 3
- **module**：`RED_DOT_BADGE`
- **precondition**：活动进行中
- **test_data**：到达活动结束时间
- **expected**：红点自动消失
- **notes**：定时器精度

### TP-008（RED_DOT_BADGE）：背包新道具红点
- **scenario**：场景 4
- **module**：`RED_DOT_BADGE`
- **precondition**：获得新道具
- **test_data**：检查背包按钮
- **expected**：红点出现
- **notes**：仅新获得显示，已查看过的同类道具不显示

### TP-009（RED_DOT_BADGE）：背包红点查看后清除
- **scenario**：场景 4
- **module**：`RED_DOT_BADGE`
- **precondition**：背包红点存在
- **test_data**：进入背包查看新道具
- **expected**：红点消失
- **notes**：清除条件可能因游戏而异

### TP-010（RED_DOT_BADGE）：签到红点每日刷新
- **scenario**：场景 5
- **module**：`RED_DOT_BADGE`
- **precondition**：签到未领
- **test_data**：跨日刷新（UTC 0:00）
- **expected**：新一天签到红点出现
- **notes**：注意时区处理

### TP-011（RED_DOT_BADGE）：公会消息红点
- **scenario**：场景 6
- **module**：`RED_DOT_BADGE`
- **precondition**：公会有新消息
- **test_data**：公会消息推送
- **expected**：公会按钮红点出现
- **notes**：与 LOG 推送事件埋点配合

### TP-012（RED_DOT_BADGE）：副本次数红点
- **scenario**：场景 7
- **module**：`RED_DOT_BADGE`
- **precondition**：副本挑战次数 > 0
- **test_data**：检查副本入口
- **expected**：副本按钮红点出现
- **notes**：次数耗尽时红点消失

### TP-013（RED_DOT_BADGE）：福利红点全领后清除
- **scenario**：场景 8
- **module**：`RED_DOT_BADGE`
- **precondition**：福利有 3 项可领
- **test_data**：逐项领取奖励
- **expected**：每领取一项红点可能仍存在（按设计），全领后红点消失
- **notes**：根据具体游戏设计决定

### TP-014（RED_DOT_BADGE）：好友申请红点
- **scenario**：场景 9
- **module**：`RED_DOT_BADGE`
- **precondition**：收到好友申请
- **test_data**：查看好友列表
- **expected**：好友按钮红点出现
- **notes**：与 I 社交提示配合

### TP-015（RED_DOT_BADGE）：可升级红点
- **scenario**：场景 10
- **module**：`RED_DOT_BADGE`
- **precondition**：角色等级可提升
- **test_data**：检查角色按钮
- **expected**：红点显示
- **notes**：升级完成后立即消失

### TP-016（RED_DOT_BADGE）：多系统红点叠加
- **scenario**：场景 1+2
- **module**：`RED_DOT_BADGE`
- **precondition**：任务未领 + 邮件未读
- **test_data**：查看主界面
- **expected**：任务红点 + 邮件角标同时显示
- **notes**：多系统红点独立、不互相影响

### TP-017（RED_DOT_BADGE）：跨系统红点同步
- **scenario**：场景 1
- **module**：`RED_DOT_BADGE`
- **precondition**：多端登录同一账号
- **test_data**：设备 A 完成任务 → 设备 B 同步
- **expected**：设备 B 任务红点同步清除
- **notes**：与 LINK `MULTI_CLIENT_SYNC` 配合

### TP-018（RED_DOT_BADGE）：红点角标视觉不溢出
- **scenario**：场景 2
- **module**：`RED_DOT_BADGE`
- **precondition**：邮件 999+ 封
- **test_data**：查看按钮
- **expected**：角标不撑爆 UI 布局、保持原设计尺寸
- **notes**：UI 样式由 F 测；A 测"业务侧不溢出规则"

### TP-019（RED_DOT_BADGE）：红点 0 不显示
- **scenario**：场景 5
- **module**：`RED_DOT_BADGE`
- **precondition**：签到已领
- **test_data**：查看签到按钮
- **expected**：无角标（数字 0 不显示）
- **notes**：注意 0 vs 隐藏的逻辑

### TP-020（RED_DOT_BADGE）：离线后红点重新计算
- **scenario**：场景 1
- **module**：`RED_DOT_BADGE`
- **precondition**：玩家离线 24 小时
- **test_data**：登录后查看
- **expected**：离线期间新任务的红点正确显示
- **notes**：与离线补偿弹窗（M）区分

---

## 3. 边界陷阱

### 边界 1：vs UI `F.GUIDE_HINT`
- **混淆点**：「红点"显示"」——A 测业务规则、F 测 UI 样式
- **判定规则**：测"何时显示/何时清除" → A；测"红点位置/大小/闪烁动画" → F
- **实例**：任务红点领取后消失 → A；红点闪烁帧率 → F

### 边界 2：vs UI `D.STATIC_DISPLAY`
- **混淆点**：「商城按钮"红点+角标"」——A 测红点业务、D 测按钮本身
- **判定规则**：测"红点是否出现" → A；测"按钮位置/图标加载" → D
- **实例**：商城红点提示新活动 → A；商城按钮图标资源加载 → D

### 边界 3：vs I. 社交提示
- **混淆点**：「好友申请"通知"」——A 测红点、I 测弹窗
- **判定规则**：测"红点出现/清除" → A；测"好友申请弹窗" → I
- **实例**：好友按钮红点 → A；点击查看弹出好友申请列表 → I

### 边界 4：vs LOG `LOG_EVENT_TRACK`
- **混淆点**：「红点"触发"」——A 测业务规则、LOG 测埋点
- **判定规则**：测"红点是否显示" → A；测"红点事件是否上报" → LOG
- **实例**：任务红点显示 → A；`red_dot.task.show` 事件埋点 → LOG

### 边界 5：vs BIZ `BIZ_STATE_MACHINE`
- **混淆点**：「任务"状态机"」——A 测红点触发、BIZ 测状态流转
- **判定规则**：测"红点出现/清除" → A；测"任务状态变更的完整流转" → BIZ
- **实例**：任务完成后红点消失 → A；任务从"未接取"到"已完成"的状态机 → BIZ

---

## 4. 验证证据

### 视觉证据
- 红点出现/消失截图（红框标注）
- 数字角标 "99+" vs "5" vs "0" 截图对比
- 多系统红点叠加截图

### 日志证据
- `red_dot.show` 事件（参数：模块/类型/来源）
- `red_dot.clear` 事件
- `badge.update` 事件（参数：旧值/新值）

### 数据证据
- 用户表 `red_dot_state` 字段（按模块存储）
- 邮件未读数表 `mail_unread_count`

### 性能证据
- 红点刷新延迟 < 200ms
- 100+ 红点同屏渲染 FPS ≥ 30
