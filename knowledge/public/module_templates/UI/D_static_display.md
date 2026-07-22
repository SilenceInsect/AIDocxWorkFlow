# D. 页面级静态展示

> **子类代码**：`STATIC_DISPLAY`（聚合 5 子项）
> **归属模块**：`UI`
> **来源**：`.cursor/MODULES.md` §4.5 D
>
> **测什么**：页面静态资源的展示（图片/图标/文案/主题/层级）——不涉及交互。
> **不测什么**：交互响应（归 A/B）、动态内容（归 BIZ）、动效（归 E）。
> **与其他子类的差异**：D 关注"展示层"——A/B 关注操作层、E 关注动效层。

---

## 1. 典型场景

### 场景 1：资源展示
- 业务背景：商品列表
- 涉及元素：商品图、图标
- 验证点：图片清晰、无裂图、无错位、无拉伸

### 场景 2：多语言文案
- 业务背景：商品详情
- 涉及元素：标题、描述、按钮文字
- 验证点：英文/日文/韩文/阿语切换、文案正确、特殊符号正常

### 场景 3：空页面
- 业务背景：搜索无结果
- 涉及元素：空状态占位
- 验证点：空状态图、提示文字、推荐按钮

### 场景 4：主题/皮肤切换
- 业务背景：设置中切换主题
- 涉及元素：全局 UI
- 验证点：深色/浅色模式正常、游戏多套皮肤切换、样式无冲突

### 场景 5：弹窗层级
- 业务背景：嵌套弹窗
- 涉及元素：弹窗 A → 弹窗 B
- 验证点：弹窗 B 在 A 之上、引导弹窗不被底层 UI 遮挡

### 场景 6：颜色与字体
- 业务背景：警告/提示
- 涉及元素：错误提示文字
- 验证点：颜色区分（红/黄/绿）、字体统一、对比度足够

### 场景 7：分割线/间距
- 业务背景：列表项
- 涉及元素：分割线、间距
- 验证点：间距一致、分割线清晰、模块分明

---

## 2. 种子测试点（TP 模板）

### TP-001（STATIC_DISPLAY）：图片资源正常加载
- **scenario**：场景 1
- **module**：`STATIC_DISPLAY`
- **precondition**：商品列表
- **test_data**：查看 20 个商品的图片
- **expected**：所有图片清晰加载、无裂图、无加载失败占位
- **notes**：用 Network 面板检查所有图片 200 响应

### TP-002（STATIC_DISPLAY）：图标无拉伸
- **scenario**：场景 1
- **module**：`STATIC_DISPLAY`
- **precondition**：列表页
- **test_data**：查看所有图标
- **expected**：图标比例正确（未变形）、清晰度足够
- **notes**：注意矢量图 vs 位图

### TP-003（STATIC_DISPLAY）：立绘/动效资源
- **scenario**：场景 1
- **module**：`STATIC_DISPLAY`
- **precondition**：角色详情页
- **test_data**：查看角色立绘、待机动画
- **expected**：立绘正常显示、动画流畅无卡顿
- **notes**：游戏专项

### TP-004（STATIC_DISPLAY）：多语言文案
- **scenario**：场景 2
- **module**：`STATIC_DISPLAY`
- **precondition**：切换语言
- **test_data**：英文/日文/韩文/阿语 4 种语言
- **expected**：4 种语言文案正确显示、无 i18n key 残留（如 `${title}` 直接显示）
- **notes**：注意阿语 RTL 布局

### TP-005（STATIC_DISPLAY）：特殊符号文案
- **scenario**：场景 2
- **module**：`STATIC_DISPLAY`
- **precondition**：商品描述
- **test_data**：含 emoji、特殊符号（™、©、®）、换行
- **expected**：emoji 正确显示、特殊符号正常、换行按设计
- **notes**：注意版权符号

### TP-006（STATIC_DISPLAY）：空页面占位
- **scenario**：场景 3
- **module**：`STATIC_DISPLAY`
- **precondition**：无数据列表
- **test_data**：列表为空
- **expected**：显示空状态图、提示文字"暂无数据"、推荐按钮
- **notes**：与 H. 异常场景 配合（H 测加载失败、D 测空数据）

### TP-007（STATIC_DISPLAY）：主题切换
- **scenario**：场景 4
- **module**：`STATIC_DISPLAY`
- **precondition**：设置中切换主题
- **test_data**：深色 ↔ 浅色
- **expected**：全局 UI 切换正确、无样式残留（如浅色按钮在深色背景）
- **notes**：注意自定义皮肤

### TP-008（STATIC_DISPLAY）：游戏多套皮肤
- **scenario**：场景 4
- **module**：`STATIC_DISPLAY`
- **precondition**：游戏设置
- **test_data**：切换 3 套皮肤
- **expected**：3 套皮肤样式完整、按钮/字体/布局全替换
- **notes**：注意资源加载完整性

### TP-009（STATIC_DISPLAY）：弹窗层级
- **scenario**：场景 5
- **module**：`STATIC_DISPLAY`
- **precondition**：主弹窗打开
- **test_data**：在主弹窗内触发子弹窗
- **expected**：子弹窗在主弹窗之上、阴影/层级正确
- **notes**：与 B-005 配合（B 测打开/关闭、D 测视觉层级）

### TP-010（STATIC_DISPLAY）：引导弹窗不被遮挡
- **scenario**：场景 5
- **module**：`STATIC_DISPLAY`
- **precondition**：新手引导
- **test_data**：引导高亮某个按钮
- **expected**：被高亮的按钮在最上层、其他 UI 变暗
- **notes**：注意 z-index 设置

### TP-011（STATIC_DISPLAY）：文字对比度
- **scenario**：场景 6
- **module**：`STATIC_DISPLAY`
- **precondition**：警告提示
- **test_data**：红字/黄字/绿字 3 种警告
- **expected**：颜色清晰可辨、对比度满足 WCAG 标准
- **notes**：与 G.无障碍 联动

### TP-012（STATIC_DISPLAY）：排版分割
- **scenario**：场景 7
- **module**：`STATIC_DISPLAY`
- **precondition**：长列表
- **test_data**：滚到列表中部
- **expected**：列表项间距一致、分割线清晰
- **notes**：与 C-007 配合

---

## 3. 边界陷阱

### 边界 1：vs A. 控件基础
- **混淆点**：「按钮图标显示」——D 测资源、A 测渲染
- **判定规则**：测"图标本身是否加载/清晰" → D；测"图标在按钮上的渲染" → A
- **实例**：图标裂图 → D-001；按钮在禁用态时图标变灰 → A-003

### 边界 2：vs BIZ
- **混淆点**：「商品图"渲染"」——D 测静态展示、BIZ 测数据获取
- **判定规则**：测"图片加载/显示" → D；测"接口返回图片 URL" → BIZ
- **实例**：图片清晰度 → D-001；接口返回的图片 URL 是否正确 → BIZ

### 边界 3：vs E. 动效
- **混淆点**：「加载动画"占位"」——D 测静态资源、E 测动画
- **判定规则**：测"加载占位图的样式" → D；测"加载动画的流畅度" → E
- **实例**：占位图灰色块 → D-006；loading spinner 动画 → E-003

---

## 4. 验证证据

### 视觉证据
- 资源加载截图（红框标注）
- 多语言对比截图
- 主题切换对比

### 日志证据
- 资源加载失败 log（应有，但应少）
- `i18n.change` 事件
- `theme.change` 事件

### 数据证据
- Network 面板：所有图片/字体 200 响应
- i18n 资源文件加载完成
- 主题/皮肤资源加载完成

### 性能证据
- 首屏图片加载 < 1s
- 主题切换响应 < 200ms
