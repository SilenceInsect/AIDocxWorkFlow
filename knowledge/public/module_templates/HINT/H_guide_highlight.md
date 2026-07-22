# H. 新手引导高亮提示

> **子类代码**：`GUIDE_HIGHLIGHT`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 H（v1.7 新增）
>
> **测什么**：新手引导遮罩、箭头高亮、步骤文字气泡、点击引导浮窗、新手奖励弹窗的**内容、触发逻辑、引导步骤流程**。
> **不测什么**：引导 UI 容器样式（归 UI `F.GUIDE_HINT`）、引导底层框架（步骤管理器）→ UTIL、新手业务奖励逻辑（归 BIZ `A.BIZ_LOGIC`）。
> **与其他子类的差异**：H 是"事件驱动、玩家驱动"引导；UI `F.GUIDE_HINT` 是 UI 容器样式；H 测内容、UI 测样式。

---

## 1. 典型场景

### 场景 1：新手遮罩指引
- 业务背景：首次进入游戏
- 涉及元素：全屏遮罩 + 高亮挖空
- 触发动作：进入新功能
- 验证点：遮罩显示、点击高亮区域进入下一步

### 场景 2：箭头高亮指引
- 业务背景：引导某个按钮
- 涉及元素：高亮框 + 箭头 + 提示文字
- 触发动作：进入引导
- 验证点：箭头指向按钮、文字描述功能

### 场景 3：步骤文字气泡
- 业务背景：步骤说明
- 涉及元素：文字气泡
- 触发动作：触发引导
- 验证点：气泡显示步骤说明

### 场景 4：点击引导浮窗
- 业务背景：强制点击引导
- 涉及元素：引导浮窗
- 触发动作：玩家点击引导
- 验证点：点击后进入下一步

### 场景 5：新手奖励弹窗
- 业务背景：完成新手任务
- 涉及元素：奖励弹窗
- 触发动作：完成新手步骤
- 验证点：弹窗显示奖励

### 场景 6：引导步骤切换
- 业务背景：多步引导
- 涉及元素：步骤指示器
- 触发动作：完成步骤 1
- 验证点：步骤切换、指示器更新

### 场景 7：引导可跳过
- 业务背景：玩家不耐烦
- 涉及元素：跳过按钮
- 触发动作：点击跳过
- 验证点：跳过按钮可点

### 场景 8：引导不可跳过
- 业务背景：关键引导
- 涉及元素：无跳过按钮
- 触发动作：观察
- 验证点：无跳过按钮

### 场景 9：引导完成后不再显示
- 业务背景：引导完成
- 涉及元素：引导
- 触发动作：完成引导
- 验证点：再次进入不显示

### 场景 10：引导断点续玩
- 业务背景：玩家中途退出
- 涉及元素：引导状态
- 触发动作：重新进入
- 验证点：从断点继续

---

## 2. 种子测试点（TP 模板）

### TP-001（GUIDE_HIGHLIGHT）：新手遮罩指引
- **scenario**：场景 1
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：首次进入
- **test_data**：进入新功能
- **expected**：遮罩显示、高亮区域可点击
- **notes**：与 UI F.GUIDE_HINT 配合

### TP-002（GUIDE_HIGHLIGHT）：箭头高亮指向
- **scenario**：场景 2
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：引导已启动
- **test_data**：观察引导
- **expected**：箭头指向目标按钮
- **notes**：UI 测样式

### TP-003（GUIDE_HIGHLIGHT）：步骤文字气泡
- **scenario**：场景 3
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：引导启动
- **test_data**：观察
- **expected**：气泡显示步骤说明
- **notes**：文案内容

### TP-004（GUIDE_HIGHLIGHT）：点击引导进入下一步
- **scenario**：场景 4
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：引导第 1 步
- **test_data**：点击高亮
- **expected**：进入第 2 步
- **notes**：与 B 资源飘字或 D 弹窗配合

### TP-005（GUIDE_HIGHLIGHT）：新手奖励弹窗
- **scenario**：场景 5
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：完成新手
- **test_data**：完成
- **expected**：弹窗显示新手奖励
- **notes**：与 D 奖励弹窗配合

### TP-006（GUIDE_HIGHLIGHT）：引导步骤指示器
- **scenario**：场景 6
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：多步引导
- **test_data**：步骤 1 完成
- **expected**：指示器更新到步骤 2
- **notes**：UI 测样式

### TP-007（GUIDE_HIGHLIGHT）：可跳过引导
- **scenario**：场景 7
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：非关键引导
- **test_data**：点击跳过
- **expected**：引导关闭
- **notes**：跳过按钮

### TP-008（GUIDE_HIGHLIGHT）：不可跳过关键引导
- **scenario**：场景 8
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：关键引导
- **test_data**：观察
- **expected**：无跳过按钮
- **notes**：强制

### TP-009（GUIDE_HIGHLIGHT）：引导完成后不再显示
- **scenario**：场景 9
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：已完成引导
- **test_data**：再次进入
- **expected**：不显示引导
- **notes**：状态持久化

### TP-010（GUIDE_HIGHLIGHT）：引导断点续玩
- **scenario**：场景 10
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：引导第 3 步退出
- **test_data**：重新进入
- **expected**：从第 3 步继续
- **notes**：断点恢复

### TP-011（GUIDE_HIGHLIGHT）：多引导并行
- **scenario**：场景 1
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：多个引导同时触发
- **test_data**：观察
- **expected**：按优先级显示
- **notes**：引导优先级

### TP-012（GUIDE_HIGHLIGHT）：引导触发条件
- **scenario**：场景 1
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：达到触发条件
- **test_data**：观察
- **expected**：引导正确触发
- **notes**：条件配置

### TP-013（GUIDE_HIGHLIGHT）：引导层级不互相遮挡
- **scenario**：场景 1
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：引导叠加
- **test_data**：观察
- **expected**：层级正确
- **notes**：z-index

### TP-014（GUIDE_HIGHLIGHT）：多语言引导文案
- **scenario**：场景 3
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：切到日语
- **test_data**：引导
- **expected**：日语文案
- **notes**：i18n

### TP-015（GUIDE_HIGHLIGHT）：引导埋点上报
- **scenario**：场景 1
- **module**：`GUIDE_HIGHLIGHT`
- **precondition**：引导开始
- **test_data**：观察日志
- **expected**：上报 `guide.start/step/end` 事件
- **notes**：与 LOG 配合

---

## 3. 边界陷阱

### 边界 1：vs UI `F.GUIDE_HINT`
- **混淆点**：「引导"显示"」——H 测内容、UI 测样式
- **判定规则**：测"引导内容/触发逻辑" → H；测"引导 UI 容器样式" → UI
- **实例**：引导文字气泡内容 → H；气泡位置/动画 → UI

### 边界 2：vs BIZ `A.BIZ_LOGIC`
- **混淆点**：「新手"奖励"」——H 测弹窗、BIZ 测业务
- **判定规则**：测"奖励弹窗显示" → H；测"奖励发放逻辑" → BIZ
- **实例**：新手奖励弹窗 → H；奖励发放业务逻辑 → BIZ

### 边界 3：vs UTIL `UTIL.GUIDE_FRAMEWORK`
- **混淆点**：「引导"框架"」——H 测引导本身、UTIL 测底层框架
- **判定规则**：测"具体引导内容" → H；测"步骤管理器底层" → UTIL
- **instance**：新手第 3 步内容 → H；步骤管理器状态机 → UTIL

### 边界 4：vs D. 模态弹窗
- **混淆点**：「新手"弹窗"」——H 是引导、D 是弹窗
- **判定规则**：测"引导流程" → H；测"独立弹窗" → D
- **实例**：新手引导浮窗 → H；防沉迷强制弹窗 → D

---

## 4. 验证证据

### 视觉证据
- 引导遮罩/高亮截图
- 多步引导步骤截图
- 跳过按钮截图

### 日志证据
- `guide.start` 事件
- `guide.step` 事件（参数：step_id）
- `guide.end` 事件
- `guide.skip` 事件

### 数据证据
- 玩家引导状态表 `guide_state`
- 引导完成度表

### 性能证据
- 引导响应 < 100ms
- 引导断点恢复 < 200ms
