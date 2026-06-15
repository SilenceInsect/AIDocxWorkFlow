# I. 聊天&社交提示

> **子类代码**：`SOCIAL_PROMPT`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 I（v1.7 新增）
>
> **测什么**：私聊红点、公会消息提醒、赠送道具回执弹窗、好友申请通知、组队邀请弹窗的**展示、触发、内容确认**。
> **不测什么**：聊天 UI 渲染（归 UI `D.STATIC_DISPLAY`）、社交业务逻辑（归 BIZ `H.PAYMENT` 赠送 / `A.BIZ_LOGIC`）、聊天协议（归 LINK `B.CROSS_SERVER_SYNC`）。
> **与其他子类的差异**：I 测"社交事件触发"的提示；A 红点测"功能入口"红点；F 浮动通知测"活动类"通知。

---

## 1. 典型场景

### 场景 1：私聊红点
- 业务背景：收到好友私聊
- 涉及元素：聊天按钮红点
- 触发动作：好友发消息
- 验证点：红点出现、查看后消失

### 场景 2：公会消息提醒
- 业务背景：公会有新消息
- 涉及元素：公会消息提示
- 触发动作：公会推送
- 验证点：弹窗/浮窗显示

### 场景 3：赠送道具回执
- 业务背景：收到玩家赠送
- 涉及元素：回执弹窗
- 触发动作：好友赠送
- 验证点：弹窗显示赠送详情

### 场景 4：好友申请通知
- 业务背景：收到好友申请
- 涉及元素：申请弹窗
- 触发动作：收到申请
- 验证点：弹窗显示申请

### 场景 5：组队邀请弹窗
- 业务背景：被邀请组队
- 涉及元素：邀请弹窗
- 触发动作：玩家邀请
- 验证点：弹窗显示邀请

### 场景 6：跨服好友消息
- 业务背景：跨服好友消息
- 涉及元素：消息提示
- 触发动作：跨服推送
- 验证点：弹窗显示跨服标识

### 场景 7：多人组队邀请
- 业务背景：多人邀请
- 涉及元素：邀请队列
- 触发动作：3 人邀请
- 验证点：邀请队列

### 场景 8：邀请超时
- 业务背景：邀请未响应
- 涉及元素：邀请
- 触发动作：超时
- 验证点：邀请自动消失

### 场景 9：好友申请已读
- 业务背景：申请已处理
- 涉及元素：申请
- 触发动作：处理申请
- 验证点：申请不再显示

### 场景 10：私聊屏蔽
- 业务背景：屏蔽玩家
- 涉及元素：私聊
- 触发动作：被屏蔽玩家发消息
- 验证点：不显示消息提示

---

## 2. 种子测试点（TP 模板）

### TP-001（SOCIAL_PROMPT）：私聊红点
- **scenario**：场景 1
- **module**：`SOCIAL_PROMPT`
- **precondition**：收到好友私聊
- **test_data**：好友发消息
- **expected**：聊天按钮红点出现
- **notes**：与 A 红点区分

### TP-002（SOCIAL_PROMPT）：私聊红点查看后消失
- **scenario**：场景 1
- **module**：`SOCIAL_PROMPT`
- **precondition**：私聊红点
- **test_data**：查看聊天
- **expected**：红点消失
- **notes**：与 BIZ 私聊已读配合

### TP-003（SOCIAL_PROMPT）：公会消息提醒浮窗
- **scenario**：场景 2
- **module**：`SOCIAL_PROMPT`
- **precondition**：公会推送
- **test_data**：公会消息
- **expected**：浮窗显示、点击进入公会
- **notes**：与 F 浮动通知区分

### TP-004（SOCIAL_PROMPT）：赠送道具回执弹窗
- **scenario**：场景 3
- **module**：`SOCIAL_PROMPT`
- **precondition**：好友赠送
- **test_data**：收到赠送
- **expected**：弹窗显示赠送详情、道具名、赠送人
- **notes**：与 D 弹窗配合

### TP-005（SOCIAL_PROMPT）：好友申请弹窗
- **scenario**：场景 4
- **module**：`SOCIAL_PROMPT`
- **precondition**：收到申请
- **test_data**：查看申请
- **expected**：弹窗显示申请
- **notes**：含"同意"/"拒绝"按钮

### TP-006（SOCIAL_PROMPT）：组队邀请弹窗
- **scenario**：场景 5
- **module**：`SOCIAL_PROMPT`
- **precondition**：被邀请
- **test_data**：玩家邀请
- **expected**：弹窗显示邀请、倒计时
- **notes**：含"接受"/"拒绝"按钮

### TP-007（SOCIAL_PROMPT）：跨服好友消息提示
- **scenario**：场景 6
- **module**：`SOCIAL_PROMPT`
- **precondition**：跨服好友
- **test_data**：跨服消息
- **expected**：弹窗显示跨服标识
- **notes**：与 LINK 跨服同步配合

### TP-008（SOCIAL_PROMPT）：多人组队邀请队列
- **scenario**：场景 7
- **module**：`SOCIAL_PROMPT`
- **precondition**：3 人邀请
- **test_data**：3 个邀请
- **expected**：3 个邀请队列显示
- **notes**：堆叠

### TP-009（SOCIAL_PROMPT）：组队邀请超时
- **scenario**：场景 8
- **module**：`SOCIAL_PROMPT`
- **precondition**：邀请未响应
- **test_data**：等待 30s
- **expected**：邀请自动消失
- **notes**：倒计时

### TP-010（SOCIAL_PROMPT）：好友申请已读不再显示
- **scenario**：场景 9
- **module**：`SOCIAL_PROMPT`
- **precondition**：已处理
- **test_data**：再次查看
- **expected**：不显示申请
- **notes**：持久化

### TP-011（SOCIAL_PROMPT）：屏蔽玩家消息不显示
- **scenario**：场景 10
- **module**：`SOCIAL_PROMPT`
- **precondition**：屏蔽玩家
- **test_data**：被屏蔽玩家发消息
- **expected**：不显示消息提示
- **notes**：屏蔽逻辑

### TP-012（SOCIAL_PROMPT）：公会邀请弹窗
- **scenario**：场景 4
- **module**：`SOCIAL_PROMPT`
- **precondition**：收到公会邀请
- **test_data**：查看
- **expected**：弹窗显示公会邀请
- **notes**：与好友申请区分

### TP-013（SOCIAL_PROMPT）：玩家在线状态提示
- **scenario**：场景 1
- **module**：`SOCIAL_PROMPT`
- **precondition**：好友上线
- **test_data**：好友登录
- **expected**：好友列表显示在线
- **notes**：与 LINK 在线状态同步配合

### TP-014（SOCIAL_PROMPT）：批量好友申请
- **scenario**：场景 4
- **module**：`SOCIAL_PROMPT`
- **precondition**：10 人申请
- **test_data**：10 个申请
- **expected**：批量显示
- **notes**：堆叠

### TP-015（SOCIAL_PROMPT）：社交提示埋点
- **scenario**：场景 4
- **module**：`SOCIAL_PROMPT`
- **precondition**：收到申请
- **test_data**：观察日志
- **expected**：上报 `friend_request.received` 等事件
- **notes**：与 LOG 配合

---

## 3. 边界陷阱

### 边界 1：vs A. 红点
- **混淆点**：「红点"提示"」——A 测功能入口、I 测社交
- **判定规则**：测"功能入口红点（任务/活动）" → A；测"社交消息红点" → I
- **实例**：任务红点 → A；私聊红点 → I

### 边界 2：vs F. 浮动通知
- **混淆点**：「消息"通知"」——I 弹窗、F 浮窗
- **判定规则**：测"居中弹窗" → I；测"侧边浮窗" → F
- **实例**：好友申请弹窗 → I；公会消息浮窗 → F

### 边界 3：vs BIZ `A.BIZ_LOGIC`
- **混淆点**：「好友"添加"」——I 测提示、BIZ 测业务
- **判定规则**：测"申请弹窗" → I；测"好友添加逻辑" → BIZ
- **instance**：好友申请弹窗 → I；好友添加业务 → BIZ

### 边界 4：vs LINK `B.CROSS_SERVER_SYNC`
- **混淆点**：「跨服"消息"」——I 测提示、LINK 测协议
- **判定规则**：测"跨服消息提示" → I；测"跨服消息协议" → LINK
- **instance**：跨服消息弹窗 → I；跨服消息协议 → LINK

### 边界 5：vs UI `D.STATIC_DISPLAY`
- **混淆点**：「聊天"UI"」——I 测提示、UI 测聊天界面
- **判定规则**：测"消息提示弹窗" → I；测"聊天界面渲染" → UI
- **instance**：聊天消息弹窗 → I；聊天界面 UI → UI

---

## 4. 验证证据

### 视觉证据
- 各种社交提示截图（私聊/公会/好友/组队）
- 邀请倒计时截图
- 跨服标识截图

### 日志证据
- `social.friend_request` 事件
- `social.team_invite` 事件
- `social.guild_invite` 事件
- `social.gift_received` 事件

### 数据证据
- 好友表 `friend_list`
- 公会表 `guild_members`
- 私聊表 `private_chat`

### 性能证据
- 邀请弹出 < 200ms
- 队列处理流畅
