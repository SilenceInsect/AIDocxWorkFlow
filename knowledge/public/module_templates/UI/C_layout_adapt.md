# C. 布局适配

> **子类代码**：`LAYOUT_ADAPT`（聚合 5 子项）
> **归属模块**：`UI`
> **来源**：`.cursor/MODULES.md` §4.5 C
>
> **测什么**：不同屏幕/窗口/终端/分辨率下的布局自适应，以及排版规范。
> **不测什么**：具体控件功能（归 A）、样式主题（归 D）、加载逻辑（归 BIZ）。
> **与其他子类的差异**：C 关注"容器/位置/适配"——A 测控件本身、C 测控件在容器中的位置。

---

## 1. 典型场景

### 场景 1：分辨率适配
- 业务背景：商城页面
- 涉及控件：整体页面布局
- 触发动作：拖动浏览器窗口大小
- 验证点：1920×1080、1366×768、1280×720 下布局正常

### 场景 2：移动端/平板适配
- 业务背景：商城页面
- 涉及控件：响应式布局
- 触发动作：移动端浏览器访问
- 验证点：iPhone 14、iPad 下布局不崩坏

### 场景 3：游戏窗口缩放
- 业务背景：游戏内商城
- 涉及控件：游戏内 UI
- 触发动作：拖动游戏窗口边角
- 验证点：UI 跟随缩放、不溢出、保持比例

### 场景 4：全屏/窗口模式切换
- 业务背景：游戏
- 涉及控件：全屏 UI
- 触发动作：F11 切换全屏
- 验证点：全屏后 UI 居中、窗口模式 UI 正常

### 场景 5：横竖版切换（游戏）
- 业务背景：手游
- 涉及控件：游戏 UI
- 触发动作：旋转手机
- 验证点：横屏布局正常、竖屏布局正常、切换过程不崩

### 场景 6：DPI 高分屏
- 业务背景：PC 端
- 涉及控件：所有 UI 元素
- 触发动作：4K 屏 / Retina 屏
- 验证点：图标清晰、文字不模糊、不拉伸失真

### 场景 7：排版规范
- 业务背景：列表页
- 涉及控件：列表项
- 触发动作：常规浏览
- 验证点：间距一致、字体统一、行高统一、像素级对齐

### 场景 8：滚动溢出
- 业务背景：长列表
- 涉及控件：页面
- 触发动作：内容超出窗口
- 验证点：无横向滚动条、纵向滚动正常、不出现内容截断

---

## 2. 种子测试点（TP 模板）

### TP-001（LAYOUT_ADAPT）：多分辨率无横向滚动
- **scenario**：场景 1
- **module**：`LAYOUT_ADAPT`
- **precondition**：商城页面
- **test_data**：窗口宽度 1920 / 1366 / 1280
- **expected**：3 种宽度下均无横向滚动溢出、内容完整可见
- **notes**：注意最小宽度设计值

### TP-002（LAYOUT_ADAPT）：移动端布局
- **scenario**：场景 2
- **module**：`LAYOUT_ADAPT`
- **precondition**：移动浏览器
- **test_data**：iPhone 14 (390×844) / iPhone SE (375×667) / iPad (1024×768)
- **expected**：3 种设备下布局自适应、按钮可点、文字可读
- **notes**：注意 viewport meta 标签

### TP-003（LAYOUT_ADAPT）：游戏窗口缩放
- **scenario**：场景 3
- **module**：`LAYOUT_ADAPT`
- **precondition**：游戏窗口
- **test_data**：窗口从 1920×1080 拖动到 1280×720
- **expected**：UI 跟随缩放、相对位置不变、不溢出
- **notes**：注意锚点（左上/居中）

### TP-004（LAYOUT_ADAPT）：全屏切换
- **scenario**：场景 4
- **module**：`LAYOUT_ADAPT`
- **precondition**：窗口模式
- **test_data**：F11 全屏 → F11 恢复
- **expected**：全屏后 UI 居中、字体清晰、状态栏不遮挡
- **notes**：注意游戏 UI 的锚点策略

### TP-005（LAYOUT_ADAPT）：横竖版切换
- **scenario**：场景 5
- **module**：`LAYOUT_ADAPT`
- **precondition**：手游
- **test_data**：横屏 → 旋转手机 → 竖屏
- **expected**：横屏 UI 完整、竖屏 UI 完整、切换过程不白屏
- **notes**：注意旋转过程的事件处理

### TP-006（LAYOUT_ADAPT）：DPI 高分屏
- **scenario**：场景 6
- **module**：`LAYOUT_ADAPT`
- **precondition**：4K 屏或 Retina 屏
- **test_data**：访问页面
- **expected**：图标清晰（2x/3x 图）、文字不模糊、不拉伸
- **notes**：注意位图 vs 矢量图

### TP-007（LAYOUT_ADAPT）：排版规范一致性
- **scenario**：场景 7
- **module**：`LAYOUT_ADAPT`
- **precondition**：多个列表页
- **test_data**：对比首页、商城页、详情页的列表项
- **expected**：间距、字体、行高一致、像素对齐
- **notes**：用设计稿比对工具

### TP-008（LAYOUT_ADAPT）：无内容溢出
- **scenario**：场景 8
- **module**：`LAYOUT_ADAPT`
- **precondition**：长列表页
- **test_data**：滚到最底部
- **expected**：纵向滚动正常、无横向滚动条、底部内容完整
- **notes**：注意 box-sizing 设置

### TP-009（LAYOUT_ADAPT）：文字不溢出容器
- **scenario**：场景 7
- **module**：`LAYOUT_ADAPT`
- **precondition**：长文字
- **test_data**：输入超长标题
- **expected**：超长省略、容器不被撑大、布局不崩坏
- **notes**：与 A-010 配合（控件边界）

### TP-010（LAYOUT_ADAPT）：极端窗口尺寸
- **scenario**：场景 1
- **module**：`LAYOUT_ADAPT`
- **precondition**：窗口可调
- **test_data**：窗口拖到 800×600、500×400
- **expected**：布局优雅降级、不崩溃、关键内容可见
- **notes**：注意最小宽度的设计

---

## 3. 边界陷阱

### 边界 1：vs A. 控件基础
- **混淆点**：「按钮在禁用态变灰」——A 测状态、C 测位置
- **判定规则**：测"按钮状态切换" → A；测"按钮在不同窗口/分辨率下的位置" → C
- **实例**：按钮禁用变灰 → A-003；按钮在 1366 下偏左、1920 下居中 → C-001

### 边界 2：vs D. 页面级静态展示
- **混淆点**：「图标加载失败"占位"」——D 测资源、C 测布局
- **判定规则**：测"图标本身是否加载" → D；测"图标缺失时占位区域是否仍占空间" → C
- **实例**：图标加载失败 → D-001；图标加载中、容器高度不变 → C-007

### 边界 3：vs BIZ
- **混淆点**：「分页"请求"」——本地分页是 B、远程分页是 BIZ
- **判定规则**：测"已加载数据的本地分页" → B；测"分页触发新接口" → BIZ
- **实例**：100 条数据本地分页 → B-011；第 11-20 条触发 GET /items?page=2 → BIZ

---

## 4. 验证证据

### 视觉证据
- 多分辨率截图（1920 / 1366 / 1280）
- 多设备截图（iPhone / iPad / Android）
- 横竖版对比

### 日志证据
- `window.resize` 事件
- `orientationchange` 事件
- `devicePixelRatio` 值

### 数据证据
- `screen.width/height` 值
- `window.innerWidth/innerHeight` 值
- `navigator.userAgent` 设备信息

### 性能证据
- 布局重排时间 < 16ms（60fps）
- 旋转切换响应 < 500ms
