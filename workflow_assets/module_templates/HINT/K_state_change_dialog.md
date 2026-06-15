# K. 状态变更全局提示

> **子类代码**：`STATE_CHANGE_DIALOG`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 K（v1.7 新增）
>
> **测什么**：升级弹窗、突破升星弹窗、段位晋升、赛季结算、战力大幅变化等"玩家状态变更"触发的全局提示。
> **不测什么**：状态机本身（归 BIZ `D.STATE_MACHINE`）、等级计算业务（归 BIZ `A.BIZ_LOGIC`）、弹窗 UI 容器（归 D `MODAL_DIALOG`）。
> **与其他子类的差异**：K 是"状态变更触发"的全局弹窗；D 是"系统事件触发"的弹窗；K 强提示"你变了"。

---

## 1. 典型场景

### 场景 1：升级弹窗
- 业务背景：玩家升级
- 涉及元素：升级弹窗
- 触发动作：玩家升级
- 验证点：弹窗显示新等级、特效

### 场景 2：突破升星弹窗
- 业务背景：装备/角色升星
- 涉及元素：升星弹窗
- 触发动作：装备升星
- 验证点：弹窗显示新星级

### 场景 3：段位晋升
- 业务背景：竞技场段位
- 涉及元素：晋升弹窗
- 触发动作：段位提升
- 验证点：弹窗显示新段位

### 场景 4：赛季结算
- 业务背景：赛季结束
- 涉及元素：结算弹窗
- 触发动作：赛季结束
- 验证点：弹窗显示结算

### 场景 5：战力大幅变化
- 业务背景：战力跃升
- 涉及元素：战力变化弹窗
- 触发动作：战力增加 X%
- 验证点：弹窗显示新战力

### 场景 6：等级衰减
- 业务背景：经验衰减
- 涉及元素：衰减提示
- 触发动作：经验衰减
- 验证点：弹窗显示衰减

### 场景 7：转职成功
- 业务背景：玩家转职
- 涉及元素：转职弹窗
- 触发动作：完成转职
- 验证点：弹窗显示新职业

### 场景 8：觉醒/飞升
- 业务背景：觉醒系统
- 涉及元素：觉醒弹窗
- 触发动作：觉醒
- 验证点：弹窗显示觉醒

### 场景 9：称号获得
- 业务背景：获得称号
- 涉及元素：称号弹窗
- 触发动作：获得称号
- 验证点：弹窗显示称号

### 场景 10：成就达成
- 业务背景：完成成就
- 涉及元素：成就弹窗
- 触发动作：达成成就
- 验证点：弹窗显示成就

---

## 2. 种子测试点（TP 模板）

### TP-001（STATE_CHANGE_DIALOG）：玩家升级弹窗
- **scenario**：场景 1
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：玩家升级
- **test_data**：经验值满
- **expected**：弹窗显示新等级、特效
- **notes**：与 BIZ 升级业务配合

### TP-002（STATE_CHANGE_DIALOG）：升级弹窗特效
- **scenario**：场景 1
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：升级弹窗
- **test_data**：观察
- **expected**：升级特效（光效/音效）
- **notes**：UI 测样式

### TP-003（STATE_CHANGE_DIALOG）：装备升星弹窗
- **scenario**：场景 2
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：装备升星
- **test_data**：装备升 5 星
- **expected**：弹窗显示新星级、特效
- **notes**：含属性变化

### TP-004（STATE_CHANGE_DIALOG）：竞技场段位晋升
- **scenario**：场景 3
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：段位提升
- **test_data**：黄金 → 白金
- **expected**：弹窗显示新段位
- **notes**：与 K 关联

### TP-005（STATE_CHANGE_DIALOG）：赛季结算弹窗
- **scenario**：场景 4
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：赛季结束
- **test_data**：进入赛季末
- **expected**：弹窗显示结算（排名/奖励）
- **notes**：含奖励

### TP-006（STATE_CHANGE_DIALOG）：战力大幅变化弹窗
- **scenario**：场景 5
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：战力 +50%
- **test_data**：装备升级
- **expected**：弹窗显示新战力
- **notes**：阈值配置

### TP-007（STATE_CHANGE_DIALOG）：经验衰减提示
- **scenario**：场景 6
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：超过衰减时间
- **test_data**：登录
- **expected**：弹窗显示衰减
- **notes**：与 G 配合

### TP-008（STATE_CHANGE_DIALOG）：转职成功弹窗
- **scenario**：场景 7
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：转职任务完成
- **test_data**：提交任务
- **expected**：弹窗显示新职业
- **notes**：含新职业技能

### TP-009（STATE_CHANGE_DIALOG）：觉醒弹窗
- **scenario**：场景 8
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：觉醒条件满足
- **test_data**：觉醒
- **expected**：弹窗显示觉醒状态
- **notes**：高阶系统

### TP-010（STATE_CHANGE_DIALOG）：称号获得弹窗
- **scenario**：场景 9
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：获得称号
- **test_data**：触发条件
- **expected**：弹窗显示称号
- **notes**：与 LOG 配合

### TP-011（STATE_CHANGE_DIALOG）：成就达成弹窗
- **scenario**：场景 10
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：完成成就
- **test_data**：达成条件
- **expected**：弹窗显示成就
- **notes**：含成就奖励

### TP-012（STATE_CHANGE_DIALOG）：连升多级弹窗
- **scenario**：场景 1
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：连升 5 级
- **test_data**：大量经验
- **expected**：弹窗显示"+5 级"
- **notes**：合并显示

### TP-013（STATE_CHANGE_DIALOG）：弹窗可关闭但可查看
- **scenario**：场景 1
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：升级弹窗
- **test_data**：关闭弹窗
- **expected**：可关闭、状态保留
- **notes**：可逆

### TP-014（STATE_CHANGE_DIALOG）：状态变更埋点
- **scenario**：场景 1
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：升级
- **test_data**：观察日志
- **expected**：上报 `player.level_up` 事件
- **notes**：与 LOG 配合

### TP-015（STATE_CHANGE_DIALOG）：多状态变更合并弹窗
- **scenario**：场景 1+2
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：升级 + 升星
- **test_data**：同时触发
- **expected**：合并弹窗或队列
- **notes**：合并策略

---

## 3. 边界陷阱

### 边界 1：vs D. 模态弹窗
- **混淆点**：「弹窗」——K 测状态变更、D 测系统
- **判定规则**：测"状态变更触发的弹窗" → K；测"系统事件触发的弹窗" → D
- **instance**：升级弹窗 → K；登录失败弹窗 → D

### 边界 2：vs BIZ `D.STATE_MACHINE`
- **混淆点**：「状态"机"」——K 测弹窗、BIZ 测状态机
- **判定规则**：测"状态变更弹窗显示" → K；测"状态机流转" → BIZ
- **instance**：升级弹窗 → K；升级状态机 → BIZ

### 边界 3：vs B. 资源飘字
- **混淆点**：「升级"奖励"」——K 测弹窗、B 测飘字
- **判定规则**：测"升级弹窗" → K；测"奖励飘字" → B
- **instance**：升级弹窗 → K；奖励+100 金币飘字 → B

### 边界 4：vs UI `D.STATIC_DISPLAY`
- **混淆点**：「等级"显示"」——K 测弹窗、UI 测常驻
- **判定规则**：测"等级变更弹窗" → K；测"等级常驻显示" → UI
- **instance**：升级弹窗 → K；玩家面板等级常驻 → UI

### 边界 5：vs K. 状态变更（v1.6.1 旧 vs v1.7 新）
- **混淆点**：v1.6.1 没有 K，v1.7 新增
- **判定规则**：升级/升星/段位/赛季结算/战力变化 → K
- **instance**：玩家升级弹窗 → K（v1.7 新增子类）

---

## 4. 验证证据

### 视觉证据
- 各种状态变更弹窗截图（升级/升星/段位/赛季）
- 弹窗特效截图
- 多状态合并截图

### 日志证据
- `state_change.show` 事件（参数：type/old_value/new_value）
- `player.level_up` 事件
- `equipment.star_up` 事件

### 数据证据
- 玩家状态表
- 状态变更历史
- 弹窗触发表

### 性能证据
- 弹窗弹出 < 200ms
- 特效帧率 ≥ 30fps
