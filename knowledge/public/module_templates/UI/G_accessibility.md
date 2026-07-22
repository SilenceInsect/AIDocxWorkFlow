# G. 无障碍 / 基础体验补充

> **子类代码**：`ACCESSIBILITY`
> **归属模块**：`UI`
> **来源**：`.cursor/MODULES.md` §4.5 G
>
> **测什么**：焦点指示器、键盘遍历、色盲配色、对比度等无障碍基础体验。
> **不测什么**：通用布局（归 C）、交互逻辑（归 A/B）、业务内容（归 BIZ）。
> **与其他子类的差异**：G 关注"所有用户可达"——A/B/C/D/E/F 关注"主要用户"。

---

## 1. 典型场景

### 场景 1：焦点指示器
- 业务背景：表单填写
- 涉及元素：所有可交互控件
- 验证点：Tab 切换时焦点环清晰可见

### 场景 2：键盘遍历
- 业务背景：表单/页面
- 涉及元素：所有按钮、输入框、链接
- 验证点：Tab 顺序合理、无焦点陷阱、Shift+Tab 反向

### 场景 3：色盲友好
- 业务背景：错误提示
- 涉及元素：错误状态
- 验证点：红绿色盲也能区分（不仅靠颜色，加图标）

### 场景 4：文字对比度
- 业务背景：提示文字
- 涉及元素：所有文字
- 验证点：对比度满足 WCAG AA（4.5:1）

### 场景 5：长按复制
- 业务背景：玩家名
- 涉及元素：文字
- 验证点：长按弹出复制菜单

### 场景 6：屏幕阅读器
- 业务背景：辅助功能
- 涉及元素：所有 UI
- 验证点：VoiceOver / TalkBack 朗读正确

### 场景 7：放大镜
- 业务背景：辅助功能
- 涉及元素：所有 UI
- 验证点：系统放大功能下 UI 不崩坏

---

## 2. 种子测试点（TP 模板）

### TP-001（ACCESSIBILITY）：焦点环可见
- **scenario**：场景 1
- **module**：`ACCESSIBILITY`
- **precondition**：表单打开
- **test_data**：按 Tab 键切换焦点
- **expected**：当前焦点元素有清晰焦点环（高亮边框/背景）
- **notes**：与 B-004 配合

### TP-002（ACCESSIBILITY）：键盘遍历所有可交互元素
- **scenario**：场景 2
- **module**：`ACCESSIBILITY`
- **precondition**：页面打开
- **test_data**：连续按 Tab 至页面末尾
- **expected**：所有可点击/可输入元素都可被 Tab 到达、顺序符合视觉顺序
- **notes**：注意隐藏元素的处理

### TP-003（ACCESSIBILITY）：Shift+Tab 反向
- **scenario**：场景 2
- **module**：`ACCESSIBILITY`
- **precondition**：已 Tab 到中间元素
- **test_data**：按 Shift+Tab
- **expected**：焦点回退到上一个元素
- **notes**：与 B-004 配合

### TP-004（ACCESSIBILITY）：无焦点陷阱
- **scenario**：场景 2
- **module**：`ACCESSIBILITY`
- **precondition**：弹窗打开
- **test_data**：在弹窗内按 Tab 多次
- **expected**：焦点在弹窗内循环、不卡死在某个元素
- **notes**：弹窗关闭后焦点回到触发按钮

### TP-005（ACCESSIBILITY）：色盲友好（不仅靠颜色）
- **scenario**：场景 3
- **module**：`ACCESSIBILITY`
- **precondition**：错误提示
- **test_data**：模拟红绿色盲（用工具）
- **expected**：错误状态除颜色外还有图标/文字提示
- **notes**：WCAG 1.4.1

### TP-006（ACCESSIBILITY）：文字对比度 WCAG AA
- **scenario**：场景 4
- **module**：`ACCESSIBILITY`
- **precondition**：所有页面
- **test_data**：用对比度检查工具
- **expected**：正文字对比度 ≥ 4.5:1、大字体 ≥ 3:1
- **notes**：用 WebAIM Contrast Checker 验证

### TP-007（ACCESSIBILITY）：按钮对比度
- **scenario**：场景 4
- **module**：`ACCESSIBILITY`
- **precondition**：按钮存在
- **test_data**：检查禁用态、激活态对比度
- **expected**：禁用态对比度 ≥ 3:1（按设计）
- **notes**：与 D-011 配合

### TP-008（ACCESSIBILITY）：长按复制菜单
- **scenario**：场景 5
- **module**：`ACCESSIBILITY`
- **precondition**：玩家名/聊天消息
- **test_data**：长按文字
- **expected**：弹出系统复制菜单（移动端）
- **notes**：注意 web 端 vs 移动端

### TP-009（ACCESSIBILITY）：屏幕阅读器朗读
- **scenario**：场景 6
- **module**：`ACCESSIBILITY`
- **precondition**：启用 VoiceOver / TalkBack
- **test_data**：浏览页面
- **expected**：朗读所有元素角色、状态、内容
- **notes**：图片 alt、按钮 aria-label

### TP-010（ACCESSIBILITY）：键盘快捷键提示
- **scenario**：场景 2
- **module**：`ACCESSIBILITY`
- **precondition**：游戏内
- **test_data**：按 ? 键
- **expected**：显示所有快捷键说明
- **notes**：与 F-007 配合

### TP-011（ACCESSIBILITY）：系统放大不崩坏
- **scenario**：场景 7
- **module**：`ACCESSIBILITY`
- **precondition**：系统放大 200%
- **test_data**：浏览页面
- **expected**：UI 放大、不溢出、不被截断
- **notes**：与 C.布局 配合

### TP-012（ACCESSIBILITY）：减少动画选项
- **scenario**：场景 1
- **module**：`ACCESSIBILITY`
- **precondition**：系统启用"减少动画"
- **test_data**：触发弹窗、转场
- **expected**：动画时长缩短或禁用、不引起不适
- **notes**：prefers-reduced-motion

---

## 3. 边界陷阱

### 边界 1：vs B. 纯前端交互
- **混淆点**：「Tab 切换"」——B 测操作、G 测可达性
- **判定规则**：测"Tab 切焦点的功能性" → B；测"焦点环可见/键盘遍历所有元素" → G
- **实例**：Tab 顺序合理 → B-004；焦点环清晰可见 → G-001

### 边界 2：vs D. 静态展示
- **混淆点**：「颜色"对比"」——D 测颜色本身、G 测对比度
- **判定规则**：测"颜色区分信息" → D；测"对比度满足 WCAG" → G
- **实例**：红字表示错误 → D-011；红字与背景对比度 ≥ 4.5:1 → G-006

### 边界 3：vs A. 控件基础
- **混淆点**：「按钮"禁用"」——A 测状态、G 测可访问性
- **判定规则**：测"按钮禁用变灰" → A；测"禁用按钮对屏幕阅读器友好（aria-disabled）" → G
- **实例**：按钮禁用态样式 → A-003；禁用按钮不被屏幕阅读器朗读为"可点击" → G-009

---

## 4. 验证证据

### 视觉证据
- 焦点环截图
- 色盲模拟截图
- 放大 200% 截图

### 日志证据
- `focus.change` 事件
- `keyboard.shortcut` 事件

### 数据证据
- `tabindex` 顺序
- `aria-*` 属性
- 对比度计算结果

### 性能证据
- 屏幕阅读器响应 < 100ms
- 焦点切换无延迟
