# F. 引导、浮窗、提示类 UI

> **子类代码**：`GUIDE_HINT`
> **归属模块**：`UI`
> **来源**：`.cursor/MODULES.md` §4.5 F
>
> **测什么**：引导遮罩、高亮指引、Toast 提示 UI、悬浮气泡、红点/未读、倒计时等**承载样式**。
> **不测什么**：提示**内容**（归 HINT）、业务触发逻辑（归 BIZ）。
> **与其他子类的差异**：F 测"提示的 UI 容器"——HINT 测"提示的内容"；F 与 E 区分：F 静态/局部、E 全局/动效。

---

## 1. 典型场景

### 场景 1：新手引导遮罩
- 业务背景：首次进入游戏
- 涉及元素：全屏遮罩、高亮挖空
- 触发动作：进入新功能
- 验证点：遮罩半透明、高亮区域可点击、其他区域不可点

### 场景 2：高亮指引
- 业务背景：引导某个按钮
- 涉及元素：高亮框、手指图标、提示文字
- 触发动作：点击"下一步"
- **expected**：高亮框跟随按钮、文字描述功能、引导可关闭

### 场景 3：Toast 轻提示
- 业务背景：操作成功
- 涉及元素：Toast 弹窗
- 触发动作：点击"购买"成功
- 验证点：Toast 在顶部/底部弹出、2-3 秒后自动消失

### 场景 4：悬浮气泡说明
- 业务背景：hover 某个图标
- 涉及元素：气泡浮层
- 触发动作：鼠标悬停
- 验证点：气泡在图标附近、显示说明文字

### 场景 5：红点角标
- 业务背景：新功能未读
- 涉及元素：红点
- 触发动作：登录
- 验证点：红点出现在图标右上角、点击后消失

### 场景 6：数字未读
- 业务背景：邮件未读
- 涉及元素：数字角标
- 触发动作：收到邮件
- 验证点：数字 > 99 显示 99+、0 不显示

### 场景 7：倒计时提示
- 业务背景：活动倒计时
- 涉及元素：倒计时 UI
- 触发动作：进入活动页
- 验证点：倒计时每秒 -1、归零后按钮激活

---

## 2. 种子测试点（TP 模板）

### TP-001（GUIDE_HINT）：新手引导遮罩
- **scenario**：场景 1
- **module**：`GUIDE_HINT`
- **precondition**：首次进入游戏
- **test_data**：进入新功能 → 引导启动
- **expected**：全屏半透明遮罩、高亮区域可点击、其他区域不响应
- **notes**：与 D-010 配合（D 测视觉层级）

### TP-002（GUIDE_HINT）：高亮挖空效果
- **scenario**：场景 1
- **module**：`GUIDE_HINT`
- **precondition**：引导已启动
- **test_data**：观察高亮区域
- **expected**：高亮区域显示完整、其他区域半透明
- **notes**：注意 z-index 和 mask 实现

### TP-003（GUIDE_HINT）：引导步骤切换
- **scenario**：场景 2
- **module**：`GUIDE_HINT`
- **precondition**：引导第 1 步
- **test_data**：点击"下一步" → 第 2 步
- **expected**：高亮框移到新按钮、文字描述更新、步骤指示更新
- **notes**：与 B-008 配合

### TP-004（GUIDE_HINT）：引导可关闭
- **scenario**：场景 2
- **module**：`GUIDE_HINT`
- **precondition**：引导已启动
- **test_data**：点击关闭按钮 / 按 ESC
- **expected**：引导立即关闭、不再显示（标记已完成）
- **notes**：与 A-009 配合（弹窗关闭）

### TP-005（GUIDE_HINT）：Toast 弹出样式
- **scenario**：场景 3
- **module**：`GUIDE_HINT`
- **precondition**：操作成功
- **test_data**：触发 Toast
- **expected**：Toast 在屏幕顶部/底部居中、半透明背景、清晰文字
- **notes**：与 HINT 模块边界：F 测样式、HINT 测内容

### TP-006（GUIDE_HINT）：Toast 自动消失
- **scenario**：场景 3
- **module**：`GUIDE_HINT`
- **precondition**：Toast 已弹出
- **test_data**：观察 3 秒
- **expected**：Toast 2-3 秒后自动消失（按设计）、可手动滑动关闭（按设计）
- **notes**：与 E-002 配合（淡入淡出动画）

### TP-007（GUIDE_HINT）：悬浮气泡位置
- **scenario**：场景 4
- **module**：`GUIDE_HINT`
- **precondition**：图标存在
- **test_data**：hover 图标
- **expected**：气泡在图标上方/下方（按设计）、箭头指向图标、不被截断
- **notes**：与 C.布局 配合（避免超出屏幕）

### TP-008（GUIDE_HINT）：红点显示与消失
- **scenario**：场景 5
- **module**：`GUIDE_HINT`
- **precondition**：有新功能
- **test_data**：查看图标 → 点击进入
- **expected**：红点显示、点击后消失、不再显示
- **notes**：与 LOG 模块联动（红点事件埋点）

### TP-009（GUIDE_HINT）：数字角标上限
- **scenario**：场景 6
- **module**：`GUIDE_HINT`
- **precondition**：邮件 150 封未读
- **test_data**：查看邮件图标
- **expected**：显示"99+"，不显示"150"
- **notes**：注意负数、零的边界

### TP-010（GUIDE_HINT）：数字角标 0 不显示
- **scenario**：场景 6
- **module**：`GUIDE_HINT`
- **precondition**：邮件已读
- **test_data**：查看邮件图标
- **expected**：不显示数字角标
- **notes**：注意隐藏 vs 显示的逻辑

### TP-011（GUIDE_HINT）：倒计时准确性
- **scenario**：场景 7
- **module**：`GUIDE_HINT`
- **precondition**：活动倒计时
- **test_data**：观察 60 秒
- **expected**：每秒 -1、归零后按钮激活、显示"已开始"
- **notes**：注意服务器时间 vs 本地时间

### TP-012（GUIDE_HINT）：倒计时刷新策略
- **scenario**：场景 7
- **module**：`GUIDE_HINT`
- **precondition**：页面长时间停留
- **test_data**：5 分钟后回来
- **expected**：倒计时仍准确（按设计刷新策略）
- **notes**：客户端倒计时 vs 服务端时间校准

---

## 3. 边界陷阱

### 边界 1：vs HINT
- **混淆点**：「Toast"提示"」——F 测样式、HINT 测内容
- **判定规则**：测"Toast 弹窗的 UI 样式/位置/时长" → F；测"Toast 显示什么文字/数字" → HINT
- **实例**：Toast 顶部居中显示 → F-005；Toast 显示"购买成功 +100 金币" → HINT

### 边界 2：vs A. 控件基础
- **混淆点**：「弹窗打开"」——A 测弹窗本身、F 测引导类弹窗
- **判定规则**：测"通用弹窗的开关" → A；测"引导/红点/倒计时" → F
- **实例**：弹窗打开/关闭 → A-009；引导遮罩打开/关闭 → F-001

### 边界 3：vs E. 动效
- **混淆点**：「红点"闪烁"」——E 测动画过程、F 测闪烁样式
- **判定规则**：测"闪烁动画流畅" → E；测"红点本身存在与消失" → F
- **实例**：红点闪烁帧率 → E-007；红点点击后消失 → F-008

### 边界 4：vs LOG
- **混淆点**：「引导"事件"」——F 测 UI、LOG 测埋点
- **判定规则**：测"引导 UI 显示与消失" → F；测"引导开始/结束/步骤事件上报" → LOG
- **实例**：引导第 1 步显示 → F-003；上报 `guide_step_1_start` → LOG

---

## 4. 验证证据

### 视觉证据
- 引导遮罩截图（高亮区域红框）
- Toast 弹出位置截图
- 红点/数字角标截图

### 日志证据
- `guide.start/step/end` 事件
- `toast.show/dismiss` 事件
- `red_dot.show/hide` 事件
- `countdown.tick` 事件

### 数据证据
- 引导完成状态表（用户表字段 `guide_finished: true`）
- 红点已读状态（`red_dot_cleared_at`）

### 性能证据
- 引导遮罩渲染 < 100ms
- Toast 弹出 < 50ms
- 倒计时 1 秒误差内
