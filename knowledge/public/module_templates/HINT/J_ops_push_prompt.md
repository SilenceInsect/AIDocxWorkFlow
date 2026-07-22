# J. 运营推送类提示

> **子类代码**：`OPS_PUSH_PROMPT`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 J（v1.7 新增）
>
> **测什么**：登录弹窗福利、限时折扣推送、节日活动弹窗、问卷调研弹窗、版本更新引导弹窗的**展示、触发、玩家响应**。
> **不测什么**：弹窗 UI 样式（归 UI `A.CONTROL_BASE_FUNC`）、运营业务逻辑（归 BIZ `A.BIZ_LOGIC`）、推送通道（归 LINK `D.EXTERNAL_THIRD_PARTY`）。
> **与其他子类的差异**：J 是"运营事件"提示；D 是"系统事件"提示；F 是"非阻塞"运营通知；J 多为模态。

---

## 1. 典型场景

### 场景 1：登录弹窗福利
- 业务背景：每日首次登录
- 涉及元素：福利弹窗
- 触发动作：登录
- 验证点：弹窗显示福利

### 场景 2：限时折扣推送
- 业务背景：限时折扣
- 涉及元素：折扣弹窗
- 触发动作：进入商城
- 验证点：弹窗显示折扣

### 场景 3：节日活动弹窗
- 业务背景：节日活动
- 涉及元素：节日弹窗
- 触发动作：节日首次登录
- 验证点：弹窗显示节日

### 场景 4：问卷调研弹窗
- 业务背景：调研推送
- 涉及元素：调研弹窗
- 触发动作：登录后
- 验证点：弹窗显示调研

### 场景 5：版本更新引导弹窗
- 业务背景：版本更新
- 涉及元素：更新引导
- 触发动作：登录
- 验证点：弹窗引导更新

### 场景 6：限时礼包推送
- 业务背景：限时礼包
- 涉及元素：礼包弹窗
- 触发动作：进入商城
- 验证点：弹窗显示礼包

### 场景 7：活动预热弹窗
- 业务背景：活动预热
- 涉及元素：预热弹窗
- 触发动作：活动开始前 1 天
- 验证点：弹窗预热

### 场景 8：用户调研奖励
- 业务背景：完成调研
- 涉及元素：奖励弹窗
- 触发动作：完成问卷
- 验证点：弹窗显示奖励

### 场景 9：节日登录奖励
- 业务背景：节日登录
- 涉及元素：节日奖励
- 触发动作：节日登录
- 验证点：弹窗显示节日奖励

### 场景 10：活动结束倒计时推送
- 业务背景：活动即将结束
- 涉及元素：倒计时弹窗
- 触发动作：活动结束前 1h
- 验证点：弹窗倒计时

---

## 2. 种子测试点（TP 模板）

### TP-001（OPS_PUSH_PROMPT）：登录福利弹窗
- **scenario**：场景 1
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：每日首次登录
- **test_data**：登录
- **expected**：弹窗显示登录福利
- **notes**：与 D 登录礼包区分（运营 vs 系统）

### TP-002（OPS_PUSH_PROMPT）：限时折扣推送弹窗
- **scenario**：场景 2
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：限时折扣
- **test_data**：进入商城
- **expected**：弹窗显示折扣信息
- **notes**：与 F 浮窗区分

### TP-003（OPS_PUSH_PROMPT）：节日活动弹窗
- **scenario**：场景 3
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：节日首次登录
- **test_data**：登录
- **expected**：弹窗显示节日活动
- **notes**：含节日元素

### TP-004（OPS_PUSH_PROMPT）：问卷调研弹窗
- **scenario**：场景 4
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：调研推送
- **test_data**：登录
- **expected**：弹窗显示调研
- **notes**：含"稍后"/"立即参与"

### TP-005（OPS_PUSH_PROMPT）：版本更新引导弹窗
- **scenario**：场景 5
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：新版本
- **test_data**：登录
- **expected**：弹窗引导更新
- **notes**：与 D 版本过低区分（强制 vs 引导）

### TP-006（OPS_PUSH_PROMPT）：限时礼包推送
- **scenario**：场景 6
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：限时礼包配置
- **test_data**：进入商城
- **expected**：弹窗显示礼包
- **notes**：与 LINK 支付通道配合

### TP-007（OPS_PUSH_PROMPT）：活动预热弹窗
- **scenario**：场景 7
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：活动开始前 1 天
- **test_data**：登录
- **expected**：弹窗预热活动
- **notes**：提前推送

### TP-008（OPS_PUSH_PROMPT）：调研奖励弹窗
- **scenario**：场景 8
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：完成调研
- **test_data**：提交问卷
- **expected**：弹窗显示奖励
- **notes**：与 B 资源飘字配合

### TP-009（OPS_PUSH_PROMPT）：节日登录奖励
- **scenario**：场景 9
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：节日首次登录
- **test_data**：登录
- **expected**：弹窗显示节日奖励
- **notes**：与 D 登录礼包区分

### TP-010（OPS_PUSH_PROMPT）：活动结束倒计时弹窗
- **scenario**：场景 10
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：活动结束前 1h
- **test_data**：登录
- **expected**：弹窗倒计时
- **notes**：与 G 倒计时区分

### TP-011（OPS_PUSH_PROMPT）：运营弹窗每日次数限制
- **scenario**：场景 4
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：每日弹窗上限 1 次
- **test_data**：关闭后再触发
- **expected**：当日不再弹
- **notes**：防骚扰

### TP-012（OPS_PUSH_PROMPT）：运营弹窗玩家偏好
- **scenario**：场景 4
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：玩家设置"不再推送"
- **test_data**：触发
- **expected**：不显示
- **notes**：偏好持久化

### TP-013（OPS_PUSH_PROMPT）：运营弹窗定时推送
- **scenario**：场景 7
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：定时推送配置
- **test_data**：到达推送时间
- **expected**：弹窗按时间推送
- **notes**：与 BIZ 定时任务配合

### TP-014（OPS_PUSH_PROMPT）：活动入口浮窗
- **scenario**：场景 1
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：活动开启
- **test_data**：进入主界面
- **expected**：活动入口浮窗
- **notes**：与 F 浮窗配合

### TP-015（OPS_PUSH_PROMPT）：多渠道运营推送
- **scenario**：场景 4
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：站内+游戏内推送
- **test_data**：触发
- **expected**：去重、不重复推送
- **notes**：去重逻辑

---

## 3. 边界陷阱

### 边界 1：vs D. 模态弹窗
- **混淆点**：「弹窗」——J 运营、D 系统
- **判定规则**：测"运营事件触发" → J；测"系统事件触发" → D
- **实例**：节日活动弹窗 → J；维护公告弹窗 → D

### 边界 2：vs F. 浮动通知
- **混淆点**：「运营"通知"」——J 弹窗、F 浮窗
- **判定规则**：测"居中弹窗" → J；测"侧边浮窗" → F
- **实例**：节日活动弹窗 → J；侧边活动浮窗 → F

### 边界 3：vs BIZ `A.BIZ_LOGIC`
- **混淆点**：「运营"奖励"」——J 测弹窗、BIZ 测业务
- **判定规则**：测"奖励弹窗显示" → J；测"奖励发放业务" → BIZ
- **instance**：节日奖励弹窗 → J；节日奖励发放业务 → BIZ

### 边界 4：vs LINK `D.EXTERNAL_THIRD_PARTY`
- **混淆点**：「推送"通道"」——J 测弹窗、LINK 测通道
- **判定规则**：测"运营弹窗显示" → J；测"推送通道（Push/微信）" → LINK
- **instance**：问卷调研弹窗 → J；推送通道 SDK → LINK

### 边界 5：vs G. 限时提醒
- **混淆点**：「活动"倒计时"」——J 弹窗、G 浮窗
- **判定规则**：测"活动弹窗" → J；测"倒计时浮窗" → G
- **instance**：节日活动弹窗 → J；活动倒计时 23:45:12 浮窗 → G

---

## 4. 验证证据

### 视觉证据
- 各种运营弹窗截图（福利/折扣/节日/调研）
- 节日元素截图
- 多渠道推送截图

### 日志证据
- `ops_push.show` 事件（参数：type/campaign_id）
- `ops_push.dismiss` 事件
- `ops_push.click` 事件

### 数据证据
- 运营弹窗配置表
- 玩家偏好表
- 弹窗触发表

### 性能证据
- 弹窗弹出 < 200ms
- 多弹窗队列性能
