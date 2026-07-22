# B. 纯前端交互

> **子类代码**：`PURE_INTERACTION`（聚合 5 子项）
> **归属模块**：`UI`
> **来源**：`.cursor/MODULES.md` §4.5 B
>
> **测什么**：不依赖后端接口的纯前端交互（单击/双击/拖拽/键盘、弹窗浮层联动、本地筛选/排序/分页）。
> **不测什么**：涉及接口调用的交互（归 BIZ）、跨服务交互（归 LINK）。
> **与其他子类的差异**：B 强调"多操作/联动/本地"——A 测控件基础、B 测控件之间。

---

## 1. 典型场景

### 场景 1：鼠标多操作
- 业务背景：道具列表
- 涉及控件：道具项
- 触发动作：单击 / 双击 / 右键 / 滚轮滚动
- 验证点：单击进入详情、双击快速购买、右键菜单弹出、滚轮滑动

### 场景 2：键盘快捷键
- 业务背景：背包界面
- 涉及控件：背包格
- 触发动作：方向键 / 数字键 / 快捷键（I 打开背包）
- 验证点：方向键移动焦点、数字键使用道具、快捷键开关背包

### 场景 3：Tab 焦点切换
- 业务背景：表单填写
- 涉及控件：输入框、下拉框
- 触发动作：Tab 键
- 验证点：Tab 顺序合理、Shift+Tab 反向、焦点环可见

### 场景 4：弹窗浮层联动
- 业务背景：确认弹窗
- 涉及控件：模态弹窗、抽屉
- 触发动作：点击触发元素
- 验证点：弹窗层级正确、遮罩锁定底层、抽屉从侧边滑入

### 场景 5：表单联动
- 业务背景：收货地址
- 涉及控件：省市区下拉、地址输入框
- 触发动作：选省份 → 城市列表刷新；选城市 → 区县列表刷新
- 验证点：联动刷新、级联数据正确

### 场景 6：Tab 标签页切换
- 业务背景：商品详情
- 涉及控件：Tab 标签（介绍 / 评价 / 详情）
- 触发动作：点击不同 Tab
- 验证点：内容区切换、当前 Tab 高亮、切换动画

### 场景 7：前端校验
- 业务背景：注册表单
- 涉及控件：手机号、邮箱输入框
- 触发动作：输入手机号、邮箱
- 验证点：实时格式校验、失焦校验、错误提示、提交时统一校验

### 场景 8：本地筛选/排序/分页
- 业务背景：商品列表
- 涉及控件：筛选器、排序按钮、分页器
- 触发动作：选筛选项 / 排序 / 翻页
- 验证点：本地筛选无需请求接口、排序结果正确、分页流畅

---

## 2. 种子测试点（TP 模板）

### TP-001（PURE_INTERACTION）：单击 vs 双击 vs 右键区分
- **scenario**：场景 1
- **module**：`PURE_INTERACTION`
- **precondition**：道具列表
- **test_data**：单击、双击、右键同一道具
- **expected**：单击进入详情、双击快速购买（按设计）、右键弹出菜单
- **notes**：注意单击和双击的时序区分

### TP-002（PURE_INTERACTION）：拖拽道具到背包
- **scenario**：场景 1
- **module**：`PURE_INTERACTION`
- **precondition**：背包有空间
- **test_data**：拖拽道具 A 从列表到背包格 1
- **expected**：拖拽过程有半透明预览、目标格高亮、放置成功
- **notes**：拖出背包边界、目标格已有道具的覆盖逻辑

### TP-003（PURE_INTERACTION）：键盘快捷键
- **scenario**：场景 2
- **module**：`PURE_INTERACTION`
- **precondition**：进入游戏
- **test_data**：按 I 打开背包 / Esc 关闭 / 数字键 1-9 使用对应道具
- **expected**：快捷键响应正确、与其他快捷键无冲突
- **notes**：注意输入框聚焦时快捷键应被屏蔽

### TP-004（PURE_INTERACTION）：Tab 焦点切换
- **scenario**：场景 3
- **module**：`PURE_INTERACTION`
- **precondition**：表单打开
- **test_data**：连续按 Tab 键
- **expected**：焦点按视觉顺序切换、Shift+Tab 反向、焦点环可见
- **notes**：与 G.无障碍 联动

### TP-005（PURE_INTERACTION）：弹窗层级
- **scenario**：场景 4
- **module**：`PURE_INTERACTION`
- **precondition**：主弹窗已打开
- **test_data**：在主弹窗内点击"帮助"按钮 → 子弹窗打开
- **expected**：子弹窗在主弹窗之上、关闭子弹窗后主弹窗仍存在
- **notes**：3 层以上弹窗的层级管理

### TP-006（PURE_INTERACTION）：抽屉式弹窗
- **scenario**：场景 4
- **module**：`PURE_INTERACTION`
- **precondition**：触发抽屉入口
- **test_data**：点击触发 → 抽屉从右滑入
- **expected**：抽屉滑入动画、遮罩可关闭（按设计）、主界面不响应底层操作
- **notes**：抽屉方向（左/右/上/下）

### TP-007（PURE_INTERACTION）：表单级联联动
- **scenario**：场景 5
- **module**：`PURE_INTERACTION`
- **precondition**：地址表单
- **test_data**：选"广东" → 城市列表变化 → 选"深圳" → 区县列表变化
- **expected**：级联刷新、级联数据正确、可清空重选
- **notes**：注意级联数据加载失败的处理

### TP-008（PURE_INTERACTION）：Tab 标签切换
- **scenario**：场景 6
- **module**：`PURE_INTERACTION`
- **precondition**：商品详情打开
- **test_data**：点击"评价" Tab
- **expected**：评价内容加载、当前 Tab 高亮、滚动位置重置（按设计）
- **notes**：注意 Tab 切换是否触发接口

### TP-009（PURE_INTERACTION）：前端实时格式校验
- **scenario**：场景 7
- **module**：`PURE_INTERACTION`
- **precondition**：注册表单
- **test_data**：输入手机号 13800138000 / 13800 / abc
- **expected**：11 位数字通过、位数不足错误提示、非数字拒绝
- **notes**：与提交时校验的差异化

### TP-010（PURE_INTERACTION）：本地筛选无需接口
- **scenario**：场景 8
- **module**：`PURE_INTERACTION`
- **precondition**：商品列表已加载
- **test_data**：选"价格降序"
- **expected**：列表立即重排、Network 面板无新请求、排序结果正确
- **notes**：与"远程筛选"区分

### TP-011（PURE_INTERACTION）：本地分页
- **scenario**：场景 8
- **module**：`PURE_INTERACTION`
- **precondition**：100 条数据已加载
- **test_data**：点击第 3 页
- **expected**：显示 21-30 条、Network 面板无新请求（按设计）、页码高亮
- **notes**：与远程分页的区分

### TP-012（PURE_INTERACTION）：本地缓存视图状态
- **scenario**：场景 8
- **module**：`PURE_INTERACTION`
- **precondition**：列表筛选为"价格降序"
- **test_data**：退出页面 → 重新进入
- **expected**：筛选状态保留（按设计）
- **notes**：是否需要缓存由产品设计决定

---

## 3. 边界陷阱

### 边界 1：vs A. 控件基础
- **混淆点**：「按钮点击」——A 测响应、B 测多操作
- **判定规则**：测"按钮按下" → A；测"单击/双击/拖拽等差异化" → B
- **实例**：单击进入详情 → A-009；单击 vs 双击的差异 → B-001

### 边界 2：vs BIZ（涉及接口）
- **混淆点**：「表单提交」——校验是 B、保存到后端是 BIZ
- **判定规则**：测"前端格式校验/本地状态" → B；测"接口调用/落库" → BIZ
- **实例**：手机号格式校验 → B-009；提交到后端的 200/500 响应 → BIZ

### 边界 3：vs F. 引导浮窗
- **混淆点**：「浮窗提示」——B 测弹窗容器、F 测引导内容
- **判定规则**：测"弹窗打开/关闭/层级" → B；测"引导遮罩/高亮挖空" → F
- **实例**：模态弹窗打开 → B-005；新手引导高亮某个按钮 → F-002

---

## 4. 验证证据

### 视觉证据
- 弹窗层级对比图（多层弹窗）
- 抽屉滑入过程截图
- Tab 切换前后对比

### 日志证据
- `Modal.open/close` 事件
- `Tab.change` 事件
- `Drag.start/end` 事件

### 数据证据
- Network 面板：本地操作**无**新请求
- LocalStorage：视图状态保存

### 性能证据
- 弹窗打开 < 100ms
- 拖拽过程 ≥ 30fps
- 1000 条数据本地筛选 < 50ms
