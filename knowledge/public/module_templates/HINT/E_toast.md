# E. 轻量 Toast / 短暂弹窗

> **子类代码**：`TOAST`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 E
>
> **测什么**：轻量短时无阻断提示，包括操作成功/失败/中性提示、Toast 队列管理、多语言文案、弱网不丢失。
> **不测什么**：强制模态弹窗（归 D `MODAL_DIALOG`）、浮动通知（归 F `FLOAT_NOTIFY`）、Toast UI 样式（归 UI `F.GUIDE_HINT`）。
> **与其他子类的差异**：E 不强制交互、不阻塞；D 强制；F 侧边非阻塞。

---

## 1. 典型场景

### 场景 1：购买成功 Toast
- 业务背景：购买道具
- 涉及元素：成功 Toast
- 触发动作：购买成功
- 验证点：Toast 显示"购买成功"、2-3s 消失

### 场景 2：使用成功 Toast
- 业务背景：使用道具
- 涉及元素：成功 Toast
- 触发动作：使用成功
- 验证点：Toast 显示"使用成功"

### 场景 3：兑换完成 Toast
- 业务背景：兑换码兑换
- 涉及元素：成功 Toast
- 触发动作：兑换成功
- 验证点：Toast 显示"兑换成功 + 道具名"

### 场景 4：分享成功 Toast
- 业务背景：分享活动
- 涉及元素：成功 Toast
- 触发动作：分享回调成功
- 验证点：Toast 显示"分享成功"

### 场景 5：资源不足 Toast
- 业务背景：购买失败
- 涉及元素：失败 Toast
- 触发动作：金币不足
- 验证点：Toast 显示"金币不足"、红色/警告色

### 场景 6：等级不足 Toast
- 业务背景：进入副本失败
- 涉及元素：失败 Toast
- 触发动作：等级不够
- 验证点：Toast 显示"等级不足"

### 场景 7：冷却未结束 Toast
- 业务背景：技能冷却
- 涉及元素：失败 Toast
- 触发动作：技能在冷却
- 验证点：Toast 显示"冷却中" + 剩余秒数

### 场景 8：活动未开启 Toast
- 业务背景：访问未开启活动
- 涉及元素：失败 Toast
- 触发动作：活动未开始
- 验证点：Toast 显示"活动未开启"

### 场景 9：参数非法 Toast
- 业务背景：输入非法字符
- 涉及元素：失败 Toast
- 触发动作：提交非法参数
- 验证点：Toast 显示"参数非法"

### 场景 10：已达每日上限 Toast
- 业务背景：副本次数耗尽
- 涉及元素：中性 Toast
- 触发动作：第 5 次挑战
- 验证点：Toast 显示"今日次数已用完"

### 场景 11：背包已满 Toast
- 业务背景：拾取道具
- 涉及元素：中性 Toast
- 触发动作：背包满
- 验证点：Toast 显示"背包已满"

### 场景 12：保存设置成功 Toast
- 业务背景：保存设置
- 涉及元素：中性 Toast
- 触发动作：保存设置
- 验证点：Toast 显示"保存成功"

### 场景 13：连续 10 个 Toast 队列
- 业务背景：连续操作
- 涉及元素：Toast 队列
- 触发动作：1s 触发 10 个 Toast
- 验证点：Toast 按队列显示、不刷屏

### 场景 14：弱网下 Toast 不丢失
- 业务背景：弱网环境
- 涉及元素：Toast
- 触发动作：操作成功
- 验证点：Toast 正常显示（本地渲染）

### 场景 15：多语言 Toast 文案
- 业务背景：切到日语
- 涉及元素：Toast
- 触发动作：触发 Toast
- 验证点：Toast 显示日语文案

---

## 2. 种子测试点（TP 模板）

### TP-001（TOAST）：购买成功 Toast
- **scenario**：场景 1
- **module**：`TOAST`
- **precondition**：购买道具
- **test_data**：购买成功
- **expected**：Toast"购买成功"、2-3s 消失
- **notes**：与 B 资源飘字区分

### TP-002（TOAST）：使用成功 Toast
- **scenario**：场景 2
- **module**：`TOAST`
- **precondition**：使用道具
- **test_data**：使用成功
- **expected**：Toast"使用成功"
- **notes**：简短文案

### TP-003（TOAST）：兑换完成 Toast
- **scenario**：场景 3
- **module**：`TOAST`
- **precondition**：兑换码
- **test_data**：兑换成功
- **expected**：Toast"兑换成功 + 道具名"
- **notes**：动态文案

### TP-004（TOAST）：分享成功 Toast
- **scenario**：场景 4
- **module**：`TOAST`
- **precondition**：分享回调
- **test_data**：分享成功
- **expected**：Toast"分享成功"
- **notes**：与 LINK 分享通道配合

### TP-005（TOAST）：资源不足 Toast（红色）
- **scenario**：场景 5
- **module**：`TOAST`
- **precondition**：金币不足
- **test_data**：购买 100 金币道具、金币 50
- **expected**：Toast"金币不足"、红色/警告色
- **notes**：失败色 vs 成功色

### TP-006（TOAST）：等级不足 Toast
- **scenario**：场景 6
- **module**：`TOAST`
- **precondition**：玩家 10 级、副本要求 20 级
- **test_data**：进入副本
- **expected**：Toast"等级不足"
- **notes**：清晰文案

### TP-007（TOAST）：冷却中 Toast
- **scenario**：场景 7
- **module**：`TOAST`
- **precondition**：技能冷却中
- **test_data**：点击技能
- **expected**：Toast"冷却中" + 剩余秒数
- **notes**：动态数字

### TP-008（TOAST）：活动未开启 Toast
- **scenario**：场景 8
- **module**：`TOAST`
- **precondition**：活动未开始
- **test_data**：访问活动入口
- **expected**：Toast"活动未开启"
- **notes**：提示而非强制

### TP-009（TOAST）：参数非法 Toast
- **scenario**：场景 9
- **module**：`TOAST`
- **precondition**：输入非法
- **test_data**：输入 SQL 注入
- **expected**：Toast"参数非法"
- **notes**：安全相关

### TP-010（TOAST）：每日上限 Toast
- **scenario**：场景 10
- **module**：`TOAST`
- **precondition**：副本次数 0
- **test_data**：挑战副本
- **expected**：Toast"今日次数已用完"
- **notes**：中性提示

### TP-011（TOAST）：背包已满 Toast
- **scenario**：场景 11
- **module**：`TOAST`
- **precondition**：背包满
- **test_data**：拾取道具
- **expected**：Toast"背包已满"
- **notes**：提示

### TP-012（TOAST）：保存设置成功 Toast
- **scenario**：场景 12
- **module**：`TOAST`
- **precondition**：设置页面
- **test_data**：保存设置
- **expected**：Toast"保存成功"
- **notes**：即时反馈

### TP-013（TOAST）：连续 10 个 Toast 队列
- **scenario**：场景 13
- **module**：`TOAST`
- **precondition**：连续操作
- **test_data**：1s 触发 10 个 Toast
- **expected**：10 个 Toast 按队列显示
- **notes**：FIFO

### TP-014（TOAST）：弱网 Toast 不丢失
- **scenario**：场景 14
- **module**：`TOAST`
- **precondition**：弱网
- **test_data**：操作成功
- **expected**：Toast 正常显示
- **notes**：Toast 是本地渲染

### TP-015（TOAST）：多语言 Toast
- **scenario**：场景 15
- **module**：`TOAST`
- **precondition**：切到日语
- **test_data**：触发 Toast
- **expected**：Toast 显示日语
- **notes**：i18n

### TP-016（TOAST）：Toast 不阻塞底层操作
- **scenario**：场景 1
- **module**：`TOAST`
- **precondition**：Toast 显示
- **test_data**：点击底层按钮
- **expected**：底层可操作、Toast 自动消失
- **notes**：与 D 模态弹窗区分

### TP-017（TOAST）：Toast 可手动滑动关闭
- **scenario**：场景 1
- **module**：`TOAST`
- **precondition**：Toast 显示
- **test_data**：滑动 Toast
- **expected**：Toast 关闭（按设计）
- **notes**：按设计

### TP-018（TOAST）：Toast 位置可配置
- **scenario**：场景 1
- **module**：`TOAST`
- **precondition**：Toast 显示
- **test_data**：检查 Toast 位置
- **expected**：顶部居中/底部居中（按设计）
- **notes**：UI 测样式

### TP-019（TOAST）：Toast 队列打断
- **scenario**：场景 13
- **module**：`TOAST`
- **precondition**：Toast 队列中
- **test_data**：触发新 Toast
- **expected**：新 Toast 加入队列
- **notes**：堆叠策略

### TP-020（TOAST）：Toast 数量上限
- **scenario**：场景 13
- **module**：`TOAST`
- **precondition**：连续 100 个 Toast
- **test_data**：触发
- **expected**：按队列上限截断（按设计）
- **notes**：防内存泄漏

---

## 3. 边界陷阱

### 边界 1：vs D. 模态弹窗
- **混淆点**：「提示」——E 不阻塞、D 阻塞
- **判定规则**：测"短时不阻塞" → E；测"强制交互" → D
- **实例**：购买成功 Toast → E；登录失败弹窗 → D

### 边界 2：vs F. 浮动通知
- **混淆点**：「通知"提示"」——E 居中短暂、F 侧边常驻
- **判定规则**：测"居中短时" → E；测"侧边常驻" → F
- **实例**：购买成功 Toast → E；侧边活动浮窗 → F

### 边界 3：vs UI `F.GUIDE_HINT`
- **混淆点**：「Toast"样式"」——E 测内容、F 测样式
- **判定规则**：测"Toast 显示什么文字" → E；测"Toast 位置/时长/动画" → F
- **实例**：Toast"购买成功" → E；Toast 顶部居中 → F

### 边界 4：vs BIZ `BIZ_LOGIC`
- **混淆点**：「失败"提示"」——E 测弹窗内容、BIZ 测错误处理
- **判定规则**：测"Toast 显示什么" → E；测"为什么失败的业务逻辑" → BIZ
- **实例**：Toast"金币不足" → E；金币不足检查逻辑 → BIZ

### 边界 5：vs G. 限时提醒
- **混淆点**：「倒计时"提示"」——E 静态文案、G 动态倒计时
- **判定规则**：测"短时静态文案" → E；测"活动倒计时浮窗" → G
- **实例**：Toast"技能冷却 5s" → E；活动倒计时 23:45:12 浮窗 → G

---

## 4. 验证证据

### 视觉证据
- 各种 Toast 截图（成功/失败/中性）
- Toast 队列截图
- 弱网下 Toast 截图

### 日志证据
- `toast.show` 事件（参数：type/content/level）
- `toast.queue` 事件
- `toast.dismiss` 事件

### 数据证据
- Toast 触发记录
- 玩家操作记录

### 性能证据
- Toast 弹出 < 50ms
- 10 Toast 队列渲染流畅
