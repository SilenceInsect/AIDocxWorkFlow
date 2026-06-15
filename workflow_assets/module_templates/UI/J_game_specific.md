# J. 游戏项目额外专属（UI 游戏专项）

> **非测试类型**——本文件是**仅游戏项目**的 UI 测试点补充。
> 非游戏项目（PC 后台、移动端 App、Web 工具）**忽略**本文件。
>
> **来源**：`.cursor/MODULES.md` §4.5 J

---

## 1. 帧率适配

### 场景
- 业务背景：游戏战斗场景
- 触发动作：战斗中 UI（血条、技能栏、BUFF 图标）
- 验证点：低帧率（30fps）下 UI 不撕裂、不闪烁、切后台回前台 UI 正常

### 种子 TP

#### TP-001（J-帧率）：低帧率 UI 不撕裂
- **module**：`EDGE_UI`（UI 子类）
- **precondition**：战斗场景、30fps 设置
- **test_data**：战斗 5 分钟
- **expected**：UI 元素（血条/BUFF）位置正确、无残影、无错位
- **notes**：用 Performance 面板验证 FPS

#### TP-002（J-帧率）：切后台回前台恢复
- **module**：`EDGE_UI`
- **precondition**：游戏中
- **test_data**：切到后台 30 秒 → 切回前台
- **expected**：UI 正常显示、无错位、动画继续
- **notes**：与 SPECIAL 模块的 SWITCH_TO_BACKGROUND 配合

---

## 2. 触摸交互

### 场景
- 业务背景：手游
- 涉及元素：摇杆、虚拟按键、触摸区域
- 验证点：触摸响应、摇杆灵敏度、按键区域大小

### 种子 TP

#### TP-003（J-触摸）：摇杆灵敏度
- **module**：`PURE_INTERACTION`
- **precondition**：战斗场景
- **test_data**：轻推摇杆、全推摇杆
- **expected**：角色按比例移动、松手立即停止
- **notes**：注意不同角色移动速度

#### TP-004（J-触摸）：虚拟按键触摸区域
- **module**：`CONTROL_BOUNDARY`
- **precondition**：战斗场景
- **test_data**：用小拇指点击技能按键
- **expected**：按键可触发、触摸区域 ≥ 44×44pt（iOS HIG）
- **notes**：注意误触防护

#### TP-005（J-触摸）：多指触控
- **module**：`PURE_INTERACTION`
- **precondition**：技能连招
- **test_data**：3 指同时点击不同技能
- **expected**：3 个技能都触发、互不干扰
- **notes**：注意最大触控点数

---

## 3. 战斗 UI

### 场景
- 业务背景：战斗
- 涉及元素：战斗飘字、伤害数字、BUFF 图标
- 验证点：飘字轨迹、伤害颜色、BUFF 状态

### 种子 TP

#### TP-006（J-战斗）：伤害飘字颜色
- **module**：`HINT`（内容）/ `UI`（承载）
- **precondition**：战斗中
- **test_data**：造成普通伤害 / 暴击 / 治疗
- **expected**：普通伤害白色、暴击黄色放大、治疗绿色上升
- **notes**：HINT 测内容、UI 测样式

#### TP-007（J-战斗）：BUFF 图标显示
- **module**：`STATIC_DISPLAY`
- **precondition**：玩家获得 BUFF
- **test_data**：BUFF 持续 30 秒
- **expected**：BUFF 图标显示、倒计时进度条、BUFF 结束后消失
- **notes**：注意 BUFF 叠加

#### TP-008（J-战斗）：飘字轨迹不重叠
- **module**：`EDGE_UI`
- **precondition**：AOE 技能
- **test_data**：AOE 命中 5 个目标
- **expected**：5 个飘字不重叠、可分别识别
- **notes**：注意性能（5+ 飘字同时动画）

---

## 4. 背包 / 道具 UI

### 场景
- 业务背景：背包
- 涉及元素：道具图标、背包格子、拖拽
- 验证点：格子布局、拖拽流畅、堆叠

### 种子 TP

#### TP-009（J-背包）：道具图标
- **module**：`STATIC_DISPLAY`
- **precondition**：背包有道具
- **test_data**：查看所有道具
- **expected**：图标清晰、堆叠显示数量（>1）
- **notes**：注意品质色边框

#### TP-010（J-背包）：背包格子布局
- **module**：`LAYOUT_ADAPT`
- **precondition**：背包打开
- **test_data**：观察格子
- **expected**：4×6 排列整齐、间距一致、可滚动
- **notes**：与 C 布局配合

#### TP-011（J-背包）：拖拽道具
- **module**：`PURE_INTERACTION`
- **precondition**：背包有空间
- **test_data**：拖拽道具 A → 格子 1
- **expected**：拖拽半透明预览、目标格高亮、放置成功、源格清空
- **notes**：注意拖到已占用格子的逻辑（替换/合并）

#### TP-012（J-背包）：拖拽排序
- **module**：`PURE_INTERACTION`
- **precondition**：背包有多个道具
- **test_data**：拖拽道具 A 到 B 后
- **expected**：A 排在 B 后、其他道具位置不变
- **notes**：注意批量拖拽

---

## 5. 界面阻断逻辑

### 场景
- 业务背景：弹窗打开
- 触发动作：弹窗打开后角色是否能继续移动/技能
- 验证点：弹窗打开时游戏操作被屏蔽

### 种子 TP

#### TP-013（J-阻断）：弹窗屏蔽技能
- **module**：`CONTROL_BASE_FUNC`（UI 子类）
- **precondition**：战斗场景、弹窗打开
- **test_data**：点击屏幕/技能按键
- **expected**：技能不触发、移动不响应、弹窗关闭后立即恢复
- **notes**：注意弹窗类型（确认/教学/系统）

#### TP-014（J-阻断）：弹窗屏蔽角色移动
- **module**：`CONTROL_BASE_FUNC`
- **precondition**：战斗中、弹窗打开
- **test_data**：推动摇杆
- **expected**：角色不移动、弹窗关闭后立即响应
- **notes**：注意摇杆状态（释放/保持）

#### TP-015（J-阻断）：半透明弹窗不屏蔽
- **module**：`CONTROL_BASE_FUNC`
- **precondition**：半透明教学弹窗
- **test_data**：点击屏幕其他区域
- **expected**：游戏可继续操作、教学弹窗仍可见
- **notes**：与 TP-013 区分

#### TP-016（J-阻断）：技能选择 UI 锁定
- **module**：`CONTROL_STATE`
- **precondition**：技能选择中
- **test_data**：点击其他技能图标
- **expected**：不能切换、技能选定后弹窗关闭
- **notes**：注意 PVE/PVP 差异

---

## 6. 其他游戏专项

### 场景
- 业务背景：游戏
- 涉及元素：聊天、世界频道、公会
- 验证点：聊天 UI、表情包、@ 提醒

### 种子 TP

#### TP-017（J-聊天）：聊天表情
- **module**：`STATIC_DISPLAY`
- **precondition**：聊天输入
- **test_data**：发送表情
- **expected**：表情显示正确、其他人可见
- **notes**：注意表情大小

#### TP-018（J-聊天）：@ 提醒高亮
- **module**：`GUIDE_HINT`
- **precondition**：被 @ 提醒
- **test_data**：查看消息
- **expected**：@ 消息高亮、聊天面板红点
- **notes**：与 F.红点 配合

#### TP-019（J-游戏）：游戏内 FPS 显示
- **module**：`STATIC_DISPLAY`
- **precondition**：设置中开启 FPS 显示
- **test_data**：游戏中
- **expected**：右上角显示 FPS
- **notes**：注意性能

#### TP-020（J-游戏）：游戏内网络延迟
- **module**：`STATIC_DISPLAY`
- **precondition**：设置中开启延迟显示
- **test_data**：游戏中
- **expected**：显示延迟 ms、颜色随延迟变化
- **notes**：绿色<100 / 黄色<200 / 红色≥200

---

## 7. 边界陷阱

### 边界 1：vs HINT
- **混淆点**：「飘字"内容"」——HINT 测内容、UI 测样式
- **判定规则**：测"飘字显示什么数字" → HINT；测"飘字颜色/动画" → UI（E）
- **实例**：暴击显示"+9999" → HINT；暴击飘字放大 1.5x → E

### 边界 2：vs BIZ
- **混淆点**：「战斗"逻辑"」——BIZ 测伤害计算、UI 测飘字
- **判定规则**：测"伤害数值/暴击率" → BIZ；测"飘字显示" → UI/HINT
- **实例**：暴击率 30% → BIZ；暴击飘字显示 → UI

### 边界 3：vs SPECIAL
- **混淆点**：「切后台"恢复"」——SPECIAL 测逻辑、UI 测视觉
- **判定规则**：测"切后台处理（暂停计时）" → SPECIAL；测"回前台 UI 正常" → UI
- **实例**：切后台暂停战斗 → SPECIAL；回前台 UI 不错位 → UI（TP-002）

---

## 4. 验证证据

### 视觉证据
- 低帧率下 UI 截图
- 触摸区域红框截图
- 战斗飘字序列图

### 日志证据
- `frame.drop` 事件
- `touch.start/end` 事件
- `buff.add/remove` 事件
- `item.drag` 事件

### 数据证据
- FPS 值（Performance 面板）
- 触摸响应延迟 < 100ms
- DOM 节点数

### 性能证据
- 30fps 下 UI 流畅
- 触摸响应 < 50ms
- 100 飘字同时动画 FPS ≥ 25
