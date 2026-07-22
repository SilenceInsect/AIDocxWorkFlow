# A. 控件基础校验

> **子类代码**：`CONTROL_RENDER` / `CONTROL_STATE` / `CONTROL_BASE_FUNC` / `CONTROL_BOUNDARY`（4 个枚举）
> **归属模块**：`UI`
> **来源**：`.cursor/MODULES.md` §4.5 A
>
> **测什么**：控件本身的渲染正确性、状态切换正确性、基础功能正确性、输入边界容错性。
> **不测什么**：业务逻辑（归 BIZ）、网络请求（归 BIZ/AUX）、样式主题切换（归 D）。
> **与其他子类的差异**：A 关注"控件本身"，B 关注"控件之间的交互"，C 关注"控件布局"。

---

## 1. 典型场景

### 场景 1：按钮渲染
- 业务背景：商城道具列表页
- 涉及控件：购买按钮
- 触发动作：进入页面
- 验证点：按钮无白屏、无错位、无叠层

### 场景 2：按钮状态切换
- 业务背景：购买按钮根据余额变化切换禁用/激活
- 涉及控件：购买按钮
- 触发动作：余额不足 → 余额充足
- 验证点：禁用态灰显、激活态可点击、hover 态样式变化

### 场景 3：输入框基础功能
- 业务背景：兑换码输入
- 涉及控件：文本输入框
- 触发动作：输入文字、复制粘贴、清空
- 验证点：输入字符正确、粘贴自动去空格、清空按钮可点

### 场景 4：输入框边界
- 业务背景：兑换码输入
- 涉及控件：文本输入框
- 触发动作：输入超长字符串 / 特殊字符 / 多语言
- 验证点：超长截断、特殊字符过滤、多语言不截断

### 场景 5：下拉 / 单选 / 多选 / 开关
- 业务背景：筛选面板
- 涉及控件：下拉框、单选按钮组、多选框、开关
- 触发动作：展开、勾选、切换
- 验证点：展开收起动画、勾选状态正确、开关切换即时

### 场景 6：弹窗基础
- 业务背景：确认弹窗
- 涉及控件：模态弹窗、确认按钮、关闭按钮
- 触发动作：触发弹窗、点击确认/关闭
- 验证点：弹窗正确打开、遮罩层锁定底层、确认关闭

### 场景 7：加载/空态/报错
- 业务背景：列表页首次加载
- 涉及控件：加载占位、空数据占位、报错占位
- 触发动作：加载中、空数据、加载失败
- 验证点：3 种占位样式正确切换

---

## 2. 种子测试点（TP 模板）

### TP-001（CONTROL_RENDER）：按钮首次加载无白屏
- **scenario**：场景 1
- **module**：`CONTROL_RENDER`
- **precondition**：登录态、首次进入商城
- **test_data**：N/A
- **expected**：购买按钮首屏可见、无错位、无叠层遮挡其他元素
- **notes**：检查资源加载时序，避免"白一下"再出现

### TP-002（CONTROL_RENDER）：弹窗渲染无错位
- **scenario**：场景 6
- **module**：`CONTROL_RENDER`
- **precondition**：触发弹窗入口
- **test_data**：N/A
- **expected**：弹窗居中、遮罩层覆盖全屏、底层 UI 不穿透
- **notes**：注意多分辨率下弹窗居中

### TP-003（CONTROL_STATE）：按钮禁用态切换
- **scenario**：场景 2
- **module**：`CONTROL_STATE`
- **precondition**：余额 < 商品价格
- **test_data**：商品价格 100、余额 50
- **expected**：按钮灰显、不可点击、hover 无响应
- **notes**：注意 hover 态和禁用态的优先级

### TP-004（CONTROL_STATE）：按钮 8 种状态完整切换
- **scenario**：场景 2
- **module**：`CONTROL_STATE`
- **precondition**：按钮存在
- **test_data**：8 种状态分别截图：默认 / 禁用 / hover / 激活 / 只读 / 加载中 / 空数据 / 报错
- **expected**：每种状态视觉差异明确、可区分
- **notes**：用截图工具批量对比

### TP-005（CONTROL_STATE）：输入框失焦/聚焦状态
- **scenario**：场景 3
- **module**：`CONTROL_STATE`
- **precondition**：进入输入框所在页面
- **test_data**：点击输入框、点击页面空白处
- **expected**：聚焦时高亮边框、失焦后边框颜色变化、键盘弹起/收起
- **notes**：移动端特别注意键盘遮挡

### TP-006（CONTROL_BASE_FUNC）：输入框输入/清空/复制粘贴
- **scenario**：场景 3
- **module**：`CONTROL_BASE_FUNC`
- **precondition**：进入输入框
- **test_data**：手动输入"ABC123"、粘贴"DEF456"、清空
- **expected**：输入实时显示、粘贴自动去前后空格、清空按钮可见可点
- **notes**：粘贴内容含不可见字符时的处理

### TP-007（CONTROL_BASE_FUNC）：下拉展开收起
- **scenario**：场景 5
- **module**：`CONTROL_BASE_FUNC`
- **precondition**：进入筛选面板
- **test_data**：点击下拉
- **expected**：下拉浮层展开、点击外部自动收起、动画流畅
- **notes**：注意下拉方向（向上/向下）适配

### TP-008（CONTROL_BASE_FUNC）：单选/多选/开关
- **scenario**：场景 5
- **module**：`CONTROL_BASE_FUNC`
- **precondition**：筛选面板已展开
- **test_data**：单选 A 取消 / 勾选 B / 切换开关 C
- **expected**：单选互斥、多选可叠加、开关状态实时切换
- **notes**：注意多选数量限制

### TP-009（CONTROL_BASE_FUNC）：弹窗打开关闭
- **scenario**：场景 6
- **module**：`CONTROL_BASE_FUNC`
- **precondition**：进入弹窗触发入口
- **test_data**：点击触发 → 确认 → 弹窗关闭；点击触发 → 关闭按钮 → 弹窗关闭；点击遮罩 → 弹窗关闭（按设计）
- **expected**：3 种关闭方式都正常，遮罩点击按 UI 设计决定
- **notes**：区分"强制弹窗"和"可关闭弹窗"

### TP-010（CONTROL_BOUNDARY）：超长文本省略
- **scenario**：场景 4
- **module**：`CONTROL_BOUNDARY`
- **precondition**：输入框/列表项存在
- **test_data**：输入 100 字符 / 列表项名称 50 字
- **expected**：超出部分省略号代替、hover 提示完整内容（可选）
- **notes**：单行省略 vs 多行省略的策略

### TP-011（CONTROL_BOUNDARY）：数字限制
- **scenario**：场景 4
- **module**：`CONTROL_BOUNDARY`
- **precondition**：数字输入框
- **test_data**：输入 -1 / 0 / 999999999 / 含字母
- **expected**：负数拒绝、超过上限截断、字母不接收
- **notes**：注意游戏内货币单位（钻石/金币/点券）转换

### TP-012（CONTROL_BOUNDARY）：特殊字符兼容
- **scenario**：场景 4
- **module**：`CONTROL_BOUNDARY`
- **precondition**：玩家名输入框
- **test_data**：emoji 🎮 / 火星文 ㄚㄣˊ / SQL 注入 `' OR 1=1--` / 换行符
- **expected**：emoji 正常显示、特殊字符过滤或转义、SQL 注入无影响
- **notes**：安全性检查

### TP-013（CONTROL_BOUNDARY）：多语言不截断
- **scenario**：场景 4
- **module**：`CONTROL_BOUNDARY`
- **precondition**：切换语言为英文/日文/阿拉伯文
- **test_data**：阿语从右到左布局、长德语复合词
- **expected**：UI 不溢出、布局不崩坏、阿语 RTL 镜像
- **notes**：阿语、希伯来语是 RTL

---

## 3. 边界陷阱

### 边界 1：vs B. 纯前端交互
- **混淆点**：「按钮点击响应」——这是 A 的 `CONTROL_BASE_FUNC`，不是 B 的 `PURE_INTERACTION`
- **判定规则**：测"按钮按下去有反应"→ A；测"单击/双击/右键/拖拽等多操作的区别" → B
- **实例**：按钮单击响应 → A-009；按钮单击 vs 双击 vs 长按的差异化处理 → B-002

### 边界 2：vs D. 页面级静态展示
- **混淆点**：「按钮图标显示」——A 测渲染、D 测图标本身
- **判定规则**：测"按钮位置/状态/可点性" → A；测"图标本身是否加载/清晰" → D
- **实例**：按钮在禁用态时图标变灰 → A-003；按钮图标资源加载失败 → D-001

### 边界 3：vs E. 动效与动画
- **混淆点**：「弹窗打开"动画"」——A 测打开后状态、E 测动画过程
- **判定规则**：测"打开/关闭后状态正确" → A；测"打开/关闭过程动画流畅" → E
- **实例**：弹窗打开后遮罩层是否锁定底层 → A-009；弹窗打开动画是否卡顿 → E-001

---

## 4. 验证证据

### 视觉证据
- 按钮 8 种状态截图（红框标注当前状态）
- 弹窗打开/关闭前后对比图
- 输入框失焦/聚焦边框对比

### 日志证据
- `Button.onClick` 触发 log
- `Input.onChange` 内容变化 log
- `Modal.open/close` 事件 log

### 数据证据
- 玩家设置表中按钮自定义状态（如自定义皮肤）
- A/B Test 平台按钮点击事件

### 性能证据
- 控件首次渲染时间 < 100ms
- 弹窗打开动画帧率 ≥ 30fps
