# D. 模态系统弹窗（错误/确认/公告/奖励汇总）

> **子类代码**：`MODAL_DIALOG`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 D
>
> **测什么**：模态阻断式系统弹窗（强制交互、阻塞底层操作），包括错误阻断、确认弹窗、公告弹窗、奖励汇总弹窗。
> **不测什么**：非模态的轻量 Toast（归 E `TOAST`）、浮动通知（归 F `FLOAT_NOTIFY`）、弹窗 UI 样式（归 UI `A.CONTROL_BASE_FUNC`）。
> **与其他子类的差异**：D 强制交互、阻塞底层；E 不强制交互、可被忽略；F 非阻塞。

---

## 1. 典型场景

### 场景 1：登录失败弹窗
- 业务背景：登录失败
- 涉及元素：错误弹窗
- 触发动作：登录失败
- 验证点：弹窗强制出现、点击"确定"前不能继续

### 场景 2：充值异常弹窗
- 业务背景：支付失败
- 涉及元素：充值异常弹窗
- 触发动作：支付回调失败
- 验证点：弹窗显示错误信息、引导重试

### 场景 3：版本过低弹窗
- 业务背景：客户端版本过低
- 涉及元素：版本升级弹窗
- 触发动作：协议返回版本过低
- 验证点：弹窗强制、点击"去升级"跳转应用商店

### 场景 4：服务器维护弹窗
- 业务背景：服务器维护
- 涉及元素：维护公告弹窗
- 触发动作：登录时收到维护通知
- 验证点：弹窗显示维护时间、点击"确定"退出

### 场景 5：防沉迷强制下线
- 业务背景：未成年超时
- 涉及元素：防沉迷弹窗
- 触发动作：累计游戏时长超限
- 验证点：弹窗强制、不可关闭、退出游戏

### 场景 6：消耗稀有道具二次确认
- 业务背景：使用 SS 道具
- 涉及元素：二次确认弹窗
- 触发动作：使用稀有道具
- 验证点：弹窗显示"是否使用"、确认后执行

### 场景 7：删除物品确认
- 业务背景：删除永久道具
- 涉及元素：删除确认弹窗
- 触发动作：点击删除
- 验证点：弹窗显示"不可恢复"、二次确认

### 场景 8：退出未保存编辑确认
- 业务背景：编辑中退出
- 涉及元素：未保存提示
- 触发动作：退出编辑
- 验证点：弹窗提示"未保存"

### 场景 9：大额付费二次确认
- 业务背景：充值 6480 元
- 涉及元素：大额支付确认
- 触发动作：选择大额支付
- 验证点：弹窗二次确认、显示金额

### 场景 10：全服更新公告
- 业务背景：版本更新
- 涉及元素：更新公告
- 触发动作：登录时
- 验证点：弹窗显示更新内容、可滚动、点击关闭

### 场景 11：活动规则弹窗
- 业务背景：参加活动
- 涉及元素：活动规则
- 触发动作：点击"活动规则"
- 验证点：弹窗显示活动规则、可滚动

### 场景 12：登录礼包汇总
- 业务背景：每日登录
- 涉及元素：登录礼包
- 触发动作：每日首次登录
- 验证点：弹窗显示登录奖励、点击领取

### 场景 13：在线奖励汇总
- 业务背景：在线时长奖励
- 涉及元素：在线奖励
- 触发动作：在线满 X 分钟
- 验证点：弹窗显示奖励、点击领取

### 场景 14：累充达成弹窗
- 业务背景：累计充值达档位
- 涉及元素：累充奖励
- 触发动作：充值达档位
- 验证点：弹窗显示档位奖励、点击领取

### 场景 15：维护后登录失败
- 业务背景：维护结束
- 涉及元素：维护通知
- 触发动作：维护期间登录
- 验证点：弹窗显示"维护中"

---

## 2. 种子测试点（TP 模板）

### TP-001（MODAL_DIALOG）：登录失败错误弹窗
- **scenario**：场景 1
- **module**：`MODAL_DIALOG`
- **precondition**：登录失败
- **test_data**：网络错误
- **expected**：弹窗显示"登录失败"、强制、点击"重试"再次登录
- **notes**：与 LINK 登录链路配合

### TP-002（MODAL_DIALOG）：充值异常弹窗
- **scenario**：场景 2
- **module**：`MODAL_DIALOG`
- **precondition**：支付失败
- **test_data**：余额不足
- **expected**：弹窗"充值失败"、可重试
- **notes**：与 LINK 支付通道配合

### TP-003（MODAL_DIALOG）：版本过低强制升级
- **scenario**：场景 3
- **module**：`MODAL_DIALOG`
- **precondition**：客户端版本 < 服务端要求
- **test_data**：登录
- **expected**：弹窗"版本过低"、点击"去升级"跳转应用商店
- **notes**：阻塞游戏

### TP-004（MODAL_DIALOG）：服务器维护弹窗
- **scenario**：场景 4
- **module**：`MODAL_DIALOG`
- **precondition**：服务器维护中
- **test_data**：登录
- **expected**：弹窗显示维护时间、点击"确定"退出
- **notes**：维护公告配合

### TP-005（MODAL_DIALOG）：防沉迷强制下线
- **scenario**：场景 5
- **module**：`MODAL_DIALOG`
- **precondition**：未成年累计游戏 3 小时
- **test_data**：第 3 小时 0 分
- **expected**：弹窗"已超过时长"、不可关闭、强制退出
- **notes**：与 L 防沉迷配合、合规

### TP-006（MODAL_DIALOG）：消耗稀有道具二次确认
- **scenario**：场景 6
- **module**：`MODAL_DIALOG`
- **precondition**：使用 SS 级强化石
- **test_data**：点击使用
- **expected**：弹窗"是否使用"、显示道具名+效果、确认后扣除
- **notes**：二次确认防误操作

### TP-007（MODAL_DIALOG）：删除物品不可恢复确认
- **scenario**：场景 7
- **module**：`MODAL_DIALOG`
- **precondition**：删除永久道具
- **test_data**：点击删除
- **expected**：弹窗"删除后不可恢复"、要求输入"删除"文字或点击两次
- **notes**：高风险操作

### TP-008（MODAL_DIALOG）：退出未保存编辑
- **scenario**：场景 8
- **module**：`MODAL_DIALOG`
- **precondition**：编辑资料未保存
- **test_data**：点击返回
- **expected**：弹窗"未保存"、提供"保存"/"丢弃"选项
- **notes**：数据保护

### TP-009（MODAL_DIALOG）：大额付费二次确认
- **scenario**：场景 9
- **module**：`MODAL_DIALOG`
- **precondition**：充值 6480 元
- **test_data**：选择 6480 档位
- **expected**：弹窗显示金额、要求二次确认
- **notes**：合规、防止误操作

### TP-010（MODAL_DIALOG）：更新公告可滚动
- **scenario**：场景 10
- **module**：`MODAL_DIALOG`
- **precondition**：版本更新
- **test_data**：登录
- **expected**：弹窗显示更新内容、长内容可滚动
- **notes**：注意滚动到底

### TP-011（MODAL_DIALOG）：活动规则可滚动
- **scenario**：场景 11
- **module**：`MODAL_DIALOG`
- **precondition**：点击活动规则
- **test_data**：打开活动面板
- **expected**：弹窗显示长活动规则、可滚动到底
- **notes**：长文案处理

### TP-012（MODAL_DIALOG）：登录礼包领取
- **scenario**：场景 12
- **module**：`MODAL_DIALOG`
- **precondition**：每日首次登录
- **test_data**：登录
- **expected**：弹窗显示登录奖励、点击"领取"获得
- **notes**：与 B 资源飘字配合

### TP-013（MODAL_DIALOG）：在线奖励达成
- **scenario**：场景 13
- **module**：`MODAL_DIALOG`
- **precondition**：在线满 30 分钟
- **test_data**：在线计时
- **expected**：弹窗显示在线奖励、点击"领取"
- **notes**：定时提醒 G 配合

### TP-014（MODAL_DIALOG）：累充档位达成
- **scenario**：场景 14
- **module**：`MODAL_DIALOG`
- **precondition**：累计充值达 1000 元
- **test_data**：充值
- **expected**：弹窗显示累充奖励、点击"领取"
- **notes**：与 BIZ 支付业务配合

### TP-015（MODAL_DIALOG）：维护后强制重新登录
- **scenario**：场景 15
- **module**：`MODAL_DIALOG`
- **precondition**：维护期间
- **test_data**：登录
- **expected**：弹窗"维护中"、点击"确定"退出
- **notes**：与 LOG 维护事件配合

### TP-016（MODAL_DIALOG）：弹窗遮罩层
- **scenario**：场景 1
- **module**：`MODAL_DIALOG`
- **precondition**：弹窗打开
- **test_data**：点击弹窗外区域
- **expected**：底层 UI 不可点击（强制）
- **notes**：UI 测样式、HINT 测行为

### TP-017（MODAL_DIALOG）：ESC 键关闭弹窗（按设计）
- **scenario**：场景 1
- **module**：`MODAL_DIALOG`
- **precondition**：可关闭弹窗
- **test_data**：按 ESC
- **expected**：弹窗关闭（按设计）
- **notes**：强制弹窗不可用 ESC

### TP-018（MODAL_DIALOG）：返回键关闭弹窗（移动端）
- **scenario**：场景 1
- **module**：`MODAL_DIALOG`
- **precondition**：可关闭弹窗
- **test_data**：按返回键
- **expected**：弹窗关闭
- **notes**：移动端特定

### TP-019（MODAL_DIALOG）：弹窗点击外部不关闭
- **scenario**：场景 1
- **module**：`MODAL_DIALOG`
- **precondition**：强制弹窗
- **test_data**：点击遮罩
- **expected**：弹窗不关闭（按设计）
- **notes**：强制 vs 可关闭

### TP-020（MODAL_DIALOG）：弹窗按钮置灰等待
- **scenario**：场景 1
- **module**：`MODAL_DIALOG`
- **precondition**：弹窗打开
- **test_data**：点击"确定" → 接口请求中
- **expected**：按钮立即置灰、避免重复点击
- **notes**：防重复提交

---

## 3. 边界陷阱

### 边界 1：vs E. Toast
- **混淆点**：「提示」——D 强制、E 短暂
- **判定规则**：测"强制交互/阻塞底层" → D；测"短暂自动消失" → E
- **实例**：登录失败弹窗 → D；登录成功 Toast → E

### 边界 2：vs F. 浮动通知
- **混淆点**：「通知"弹窗"」——D 居中、F 侧边
- **判定规则**：测"居中强制" → D；测"侧边非阻塞" → F
- **实例**：维护公告弹窗 → D；侧边活动浮窗 → F

### 边界 3：vs UI `A.CONTROL_BASE_FUNC`
- **混淆点**：「弹窗"打开"」——D 测业务内容、UI 测控件
- **判定规则**：测"弹窗显示什么内容" → D；测"弹窗 UI 控件渲染" → UI
- **实例**：登录失败弹窗内容 → D；弹窗 UI 样式 → UI

### 边界 4：vs BIZ `BIZ_LOGIC`
- **混淆点**：「错误"处理"」——D 测弹窗内容、BIZ 测错误处理
- **判定规则**：测"弹窗显示什么错误文案" → D；测"错误处理业务逻辑" → BIZ
- **实例**：登录失败弹窗 → D；登录失败重试逻辑 → BIZ

### 边界 5：vs L. 风控合规
- **混淆点**：「防沉迷"弹窗"」——D 测弹窗容器、L 测合规内容
- **判定规则**：测"弹窗 UI/触发" → D；测"防沉迷规则/时长" → L
- **实例**：防沉迷强制弹窗 → D；未成年累计 3 小时规则 → L

---

## 4. 验证证据

### 视觉证据
- 各种弹窗截图（错误/确认/公告/奖励）
- 弹窗遮罩层截图
- 弹窗按钮置灰状态截图

### 日志证据
- `modal_dialog.show` 事件（参数：type/title/content）
- `modal_dialog.click_confirm/cancel` 事件
- `modal_dialog.close` 事件

### 数据证据
- 弹窗触发记录
- 玩家操作记录（确认/取消）

### 性能证据
- 弹窗弹出延迟 < 100ms
- 弹窗关闭动画帧率 ≥ 30fps
