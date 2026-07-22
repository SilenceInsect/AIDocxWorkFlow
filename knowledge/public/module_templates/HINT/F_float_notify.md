# F. 浮动通知 / 悬浮浮窗

> **子类代码**：`FLOAT_NOTIFY`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 F
>
> **测什么**：侧边非阻塞常驻轻提示，包括活动悬浮小图标、限时倒计时悬浮条、新活动开启侧边浮窗、好友私聊/公会消息/跨服广播、限时优惠/折扣/赛季倒计时浮窗。
> **不测什么**：模态弹窗（归 D `MODAL_DIALOG`）、Toast（归 E `TOAST`）、浮窗 UI 样式（归 UI `F.GUIDE_HINT`）。
> **与其他子类的差异**：F 非阻塞、侧边常驻；D 居中强制；E 居中短暂。

---

## 1. 典型场景

### 场景 1：活动悬浮小图标
- 业务背景：限时活动开启
- 涉及元素：活动悬浮小图标
- 触发动作：活动开启
- 验证点：侧边出现活动图标、点击进入活动

### 场景 2：限时倒计时悬浮条
- 业务背景：活动倒计时
- 涉及元素：倒计时悬浮条
- 触发动作：进入活动页
- 验证点：显示倒计时、每秒刷新

### 场景 3：新活动开启侧边浮窗
- 业务背景：新活动推送
- 涉及元素：侧边浮窗
- 触发动作：活动开启
- 验证点：浮窗从侧边滑入、可关闭

### 场景 4：好友私聊通知
- 业务背景：收到好友私聊
- 涉及元素：聊天悬浮通知
- 触发动作：好友发消息
- 验证点：悬浮通知显示、点击进入聊天

### 场景 5：公会消息通知
- 业务背景：公会有新消息
- 涉及元素：公会消息浮窗
- 触发动作：公会推送
- 验证点：浮窗显示、点击进入公会

### 场景 6：跨服广播
- 业务背景：跨服世界频道
- 涉及元素：跨服广播浮窗
- 触发动作：跨服广播
- 验证点：浮窗显示、跨服标识

### 场景 7：限时优惠浮窗
- 业务背景：限时折扣
- 涉及元素：优惠浮窗
- 触发动作：进入商城
- 验证点：浮窗显示折扣信息

### 场景 8：赛季倒计时浮窗
- 业务背景：赛季即将结束
- 涉及元素：赛季倒计时
- 触发动作：进入赛季面板
- 验证点：浮窗显示倒计时

### 场景 9：多浮窗叠加
- 业务背景：多个浮窗同时
- 涉及元素：浮窗队列
- 触发动作：多事件同时
- 验证点：浮窗堆叠显示

### 场景 10：浮窗关闭后不再显示
- 业务背景：玩家关闭浮窗
- 涉及元素：浮窗
- 触发动作：手动关闭
- 验证点：浮窗不再出现

---

## 2. 种子测试点（TP 模板）

### TP-001（FLOAT_NOTIFY）：活动悬浮小图标出现
- **scenario**：场景 1
- **module**：`FLOAT_NOTIFY`
- **precondition**：活动开启
- **test_data**：进入主界面
- **expected**：侧边出现活动图标
- **notes**：与 LOG 活动事件配合

### TP-002（FLOAT_NOTIFY）：活动图标点击进入
- **scenario**：场景 1
- **module**：`FLOAT_NOTIFY`
- **precondition**：活动图标存在
- **test_data**：点击图标
- **expected**：进入活动页面
- **notes**：链接正确

### TP-003（FLOAT_NOTIFY）：活动倒计时悬浮条
- **scenario**：场景 2
- **module**：`FLOAT_NOTIFY`
- **precondition**：活动进行中
- **test_data**：进入活动
- **expected**：显示倒计时（XX:XX:XX）、每秒刷新
- **notes**：与服务端时间同步

### TP-004（FLOAT_NOTIFY）：新活动侧边浮窗滑入
- **scenario**：场景 3
- **module**：`FLOAT_NOTIFY`
- **precondition**：新活动开启
- **test_data**：登录
- **expected**：侧边浮窗滑入、可关闭
- **notes**：动画流畅

### TP-005（FLOAT_NOTIFY）：好友私聊悬浮通知
- **scenario**：场景 4
- **module**：`FLOAT_NOTIFY`
- **precondition**：收到好友私聊
- **test_data**：好友发消息
- **expected**：悬浮通知显示、点击进入聊天
- **notes**：与 I 社交提示区分

### TP-006（FLOAT_NOTIFY）：公会消息浮窗
- **scenario**：场景 5
- **module**：`FLOAT_NOTIFY`
- **precondition**：公会推送
- **test_data**：公会消息
- **expected**：浮窗显示、点击进入公会
- **notes**：与 I 社交提示区分

### TP-007（FLOAT_NOTIFY）：跨服广播浮窗
- **scenario**：场景 6
- **module**：`FLOAT_NOTIFY`
- **precondition**：跨服广播
- **test_data**：跨服事件
- **expected**：浮窗显示、跨服标识
- **notes**：与 LINK 跨服配合

### TP-008（FLOAT_NOTIFY）：限时优惠浮窗
- **scenario**：场景 7
- **module**：`FLOAT_NOTIFY`
- **precondition**：限时折扣
- **test_data**：进入商城
- **expected**：浮窗显示折扣信息
- **notes**：与 J 运营推送区分

### TP-009（FLOAT_NOTIFY）：赛季倒计时浮窗
- **scenario**：场景 8
- **module**：`FLOAT_NOTIFY`
- **precondition**：赛季结束前 3 天
- **test_data**：进入赛季面板
- **expected**：浮窗显示倒计时
- **notes**：与 K 状态变更配合

### TP-010（FLOAT_NOTIFY）：多浮窗堆叠
- **scenario**：场景 9
- **module**：`FLOAT_NOTIFY`
- **precondition**：3 个浮窗同时
- **test_data**：触发多事件
- **expected**：3 个浮窗堆叠显示
- **notes**：层级管理

### TP-011（FLOAT_NOTIFY）：浮窗手动关闭
- **scenario**：场景 10
- **module**：`FLOAT_NOTIFY`
- **precondition**：浮窗存在
- **test_data**：点击关闭
- **expected**：浮窗消失
- **notes**：关闭按钮

### TP-012（FLOAT_NOTIFY）：浮窗关闭后不再显示
- **scenario**：场景 10
- **module**：`FLOAT_NOTIFY`
- **precondition**：浮窗已关闭
- **test_data**：刷新页面
- **expected**：浮窗不出现（按设计）
- **notes**：持久化关闭状态

### TP-013（FLOAT_NOTIFY）：浮窗自动消失
- **scenario**：场景 4
- **module**：`FLOAT_NOTIFY`
- **precondition**：浮窗显示
- **test_data**：观察 5-10s
- **expected**：自动消失（按设计）
- **notes**：自动 vs 手动

### TP-014（FLOAT_NOTIFY）：浮窗不阻塞底层
- **scenario**：场景 1
- **module**：`FLOAT_NOTIFY`
- **precondition**：浮窗显示
- **test_data**：点击底层
- **expected**：底层可操作
- **notes**：与 D 模态区分

### TP-015（FLOAT_NOTIFY）：浮窗 z-index 正确
- **scenario**：场景 1
- **module**：`FLOAT_NOTIFY`
- **precondition**：浮窗显示
- **test_data**：观察层级
- **expected**：浮窗在 UI 之上、不被遮挡
- **notes**：层级管理

---

## 3. 边界陷阱

### 边界 1：vs D. 模态弹窗
- **混淆点**：「通知"弹窗"」——F 非阻塞、D 阻塞
- **判定规则**：测"侧边非阻塞" → F；测"居中强制" → D
- **实例**：好友私聊浮窗 → F；登录失败弹窗 → D

### 边界 2：vs E. Toast
- **混淆点**：「提示」——F 侧边常驻、E 居中短暂
- **判定规则**：测"侧边常驻" → F；测"居中短时" → E
- **实例**：活动倒计时浮窗 → F；购买成功 Toast → E

### 边界 3：vs I. 社交提示
- **混淆点**：「消息"通知"」——F 浮窗、I 弹窗
- **判定规则**：测"侧边浮窗显示" → F；测"好友申请弹窗" → I
- **实例**：好友消息浮窗 → F；好友申请弹窗 → I

### 边界 4：vs UI `F.GUIDE_HINT`
- **混淆点**：「浮窗"样式"」——F 测业务内容、UI 测样式
- **判定规则**：测"浮窗显示什么" → F；测"浮窗位置/动画" → UI
- **实例**：好友消息浮窗 → F；浮窗滑入动画 → UI

### 边界 5：vs J. 运营推送
- **混淆点**：「活动"推送"」——F 浮窗、J 弹窗
- **判定规则**：测"活动侧边浮窗" → F；测"登录福利弹窗" → J
- **实例**：活动倒计时浮窗 → F；登录福利弹窗 → J

---

## 4. 验证证据

### 视觉证据
- 各种浮窗截图（活动/倒计时/消息）
- 多浮窗堆叠截图
- 浮窗关闭状态截图

### 日志证据
- `float_notify.show` 事件（参数：type/source）
- `float_notify.dismiss` 事件
- `float_notify.click` 事件

### 数据证据
- 浮窗显示记录
- 玩家关闭记录

### 性能证据
- 浮窗滑入动画 ≥ 30fps
- 多浮窗堆叠性能
