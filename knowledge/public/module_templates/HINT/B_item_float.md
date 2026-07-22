# B. 资源飘字（道具/货币/积分动态数值）

> **子类代码**：`ITEM_FLOAT`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 B（v1.6.1 升级，专注于资源类飘字）
>
> **测什么**：道具/货币/积分**获取/扣除**时的飘字显示，包括数字大小、正负号、多飘字队列、消失动画、层级遮挡。
> **不测什么**：战斗伤害/治疗/buff 飘字（归 C `CURRENCY_FLOAT`）；飘字 UI 样式/动画（归 UI `E.ANIMATION`）。
> **与其他子类的差异**：B 是"资源类"飘字（道具/货币/积分）；C 是"战斗类"飘字（伤害/治疗/buff）；B 与 C 在某些游戏中可能合并实现，但语义/场景/规则不同。

---

## 1. 典型场景

### 场景 1：获得道具飘字
- 业务背景：玩家开启宝箱获得"强化石×3"
- 涉及元素：屏幕中央飘字
- 触发动作：开宝箱
- 验证点：飘字显示"+强化石×3"、1.5s 后淡出

### 场景 2：货币增加飘字
- 业务背景：完成任务获得金币
- 涉及元素：金币飘字
- 触发动作：完成任务
- 验证点：飘字显示"+100 金币"、带金币图标

### 场景 3：货币扣除飘字
- 业务背景：购买道具消耗钻石
- 涉及元素：钻石飘字
- 触发动作：购买道具
- 验证点：飘字显示"-50 钻石"、带负号或红色

### 场景 4：积分类资源
- 业务背景：竞技场积分变化
- 涉及元素：积分飘字
- 触发动作：战斗结束
- 验证点：飘字显示"+30 积分"或"-10 积分"

### 场景 5：体力恢复
- 业务背景：体力自动恢复
- 涉及元素：体力飘字
- 触发动作：跨时间点
- 验证点：飘字显示"+10 体力"

### 场景 6：抽卡稀有道具高亮
- 业务背景：抽卡获得 SSR 道具
- 涉及元素：高亮飘字
- 触发动作：抽卡
- 验证点：飘字高亮（金色/动效）、显示道具名

### 场景 7：排行榜名次变化
- 业务背景：玩家排名提升
- 涉及元素：排名变化飘字
- 触发动作：结算
- 验证点：飘字显示"↑排名 +5"

### 场景 8：多飘字不重叠
- 业务背景：连续开启 10 个宝箱
- 涉及元素：飘字队列
- 触发动作：连续开宝箱
- 验证点：每个飘字独立显示、不重叠

### 场景 9：跨语言飘字适配
- 业务背景：切到德语
- 涉及元素：长德语飘字
- 触发动作：触发飘字
- 验证点：长复合词不被截断

### 场景 10：离线获得到账飘字
- 业务背景：登录时离线奖励到账
- 涉及元素：奖励飘字
- 触发动作：登录
- 验证点：飘字显示离线获得的所有道具/货币

---

## 2. 种子测试点（TP 模板）

### TP-001（ITEM_FLOAT）：道具获取飘字
- **scenario**：场景 1
- **module**：`ITEM_FLOAT`
- **precondition**：玩家开启宝箱
- **test_data**：触发飘字
- **expected**：屏幕中央显示"+强化石×3"飘字
- **notes**：注意道具图标渲染

### TP-002（ITEM_FLOAT）：货币增加带图标
- **scenario**：场景 2
- **module**：`ITEM_FLOAT`
- **precondition**：完成任务
- **test_data**：获得 100 金币
- **expected**：飘字"+100 金币" + 金币图标
- **notes**：图标与数字对齐

### TP-003（ITEM_FLOAT）：货币扣除飘字
- **scenario**：场景 3
- **module**：`ITEM_FLOAT`
- **precondition**：购买道具
- **test_data**：消耗 50 钻石
- **expected**：飘字"-50 钻石"、带负号或红色显示
- **notes**：扣除 vs 获取的视觉区分

### TP-004（ITEM_FLOAT）：积分增加飘字
- **scenario**：场景 4
- **module**：`ITEM_FLOAT`
- **precondition**：竞技场战斗胜利
- **test_data**：+30 积分
- **expected**：飘字"+30 积分"
- **notes**：与排名变化飘字区分

### TP-005（ITEM_FLOAT）：积分扣除飘字
- **scenario**：场景 4
- **module**：`ITEM_FLOAT`
- **precondition**：竞技场战斗失败
- **test_data**：-10 积分
- **expected**：飘字"-10 积分"
- **notes**：失败时的红色/警告色

### TP-006（ITEM_FLOAT）：体力恢复飘字
- **scenario**：场景 5
- **module**：`ITEM_FLOAT`
- **precondition**：体力 < 上限
- **test_data**：体力恢复 +10
- **expected**：飘字"+10 体力"
- **notes**：定时恢复 vs 道具恢复的飘字可能不同

### TP-007（ITEM_FLOAT）：SSR 抽卡高亮
- **scenario**：场景 6
- **module**：`ITEM_FLOAT`
- **precondition**：抽卡获得 SSR
- **test_data**：SSR 道具到账
- **expected**：高亮（金色/动效）飘字、显示 SSR 道具名
- **notes**：品质颜色映射：N/绿、R/蓝、SR/紫、SSR/金

### TP-008（ITEM_FLOAT）：SR 抽卡普通飘字
- **scenario**：场景 6
- **module**：`ITEM_FLOAT`
- **precondition**：抽卡获得 SR
- **test_data**：SR 道具到账
- **expected**：紫色飘字、显示 SR 道具名
- **notes**：与 TP-007 区分

### TP-009（ITEM_FLOAT）：排行榜上升飘字
- **scenario**：场景 7
- **module**：`ITEM_FLOAT`
- **precondition**：玩家排名 +5
- **test_data**：战斗结束
- **expected**：飘字"↑排名 +5"或类似
- **notes**：上升 vs 下降的视觉

### TP-010（ITEM_FLOAT）：排行榜下降飘字
- **scenario**：场景 7
- **module**：`ITEM_FLOAT`
- **precondition**：玩家排名 -3
- **test_data**：战斗结束
- **expected**：飘字"↓排名 -3"（可能红色）
- **notes**：负向排名变化

### TP-011（ITEM_FLOAT）：连续 10 个飘字队列
- **scenario**：场景 8
- **module**：`ITEM_FLOAT`
- **precondition**：连续开启 10 个宝箱
- **test_data**：1 秒内触发 10 个飘字
- **expected**：飘字按顺序或队列显示、不重叠
- **notes**：注意性能和动画

### TP-012（ITEM_FLOAT）：AOE 100 个飘字性能
- **scenario**：场景 8
- **module**：`ITEM_FLOAT`
- **precondition**：AOE 技能命中 100 个目标
- **test_data**：100 个飘字同时弹出
- **expected**：100 飘字队列渲染、FPS ≥ 25
- **notes**：性能边界

### TP-013（ITEM_FLOAT）：长德语飘字不截断
- **scenario**：场景 9
- **module**：`ITEM_FLOAT`
- **precondition**：切到德语
- **test_data**：德语长道具名飘字
- **expected**：长德语不被截断、自动换行
- **notes**：多语言适配

### TP-014（ITEM_FLOAT）：离线奖励到账飘字
- **scenario**：场景 10
- **module**：`ITEM_FLOAT`
- **precondition**：离线 24h
- **test_data**：登录
- **expected**：飘字显示离线获得的所有道具/货币
- **notes**：与 M 离线补偿弹窗配合

### TP-015（ITEM_FLOAT）：飘字层级不遮挡关键 UI
- **scenario**：场景 1
- **module**：`ITEM_FLOAT`
- **precondition**：战斗中
- **test_data**：战斗获得道具飘字
- **expected**：飘字在战斗 UI 上方但不完全遮挡技能按键
- **notes**：z-index 层级设计

### TP-016（ITEM_FLOAT）：飘字消失动画
- **scenario**：场景 1
- **module**：`ITEM_FLOAT`
- **precondition**：飘字已显示
- **test_data**：观察 1.5s
- **expected**：飘字向上飘动 + 淡出
- **notes**：UI 测动画本身、HINT 测触发

### TP-017（ITEM_FLOAT）：0 飘字不显示
- **scenario**：场景 2
- **module**：`ITEM_FLOAT`
- **precondition**：获得 0 金币（异常）
- **test_data**：触发飘字
- **expected**：不显示飘字（按设计）
- **notes**：边界值

### TP-018（ITEM_FLOAT）：超大数值不溢出
- **scenario**：场景 2
- **module**：`ITEM_FLOAT`
- **precondition**：获得 999,999,999 金币
- **test_data**：触发飘字
- **expected**：完整显示数字、不溢出 UI
- **notes**：数字格式（千分位/缩写 K/M）

### TP-019（ITEM_FLOAT）：负数值飘字
- **scenario**：场景 3
- **module**：`ITEM_FLOAT`
- **precondition**：扣除 -50
- **test_data**：负数飘字
- **expected**：显示"-50"、红色或带负号
- **notes**：注意"-"符号渲染

### TP-020（ITEM_FLOAT）：跨场景飘字不残留
- **scenario**：场景 1
- **module**：`ITEM_FLOAT`
- **precondition**：场景 A 飘字未消失
- **test_data**：切换到场景 B
- **expected**：飘字立即清除或完成动画后清除
- **notes**：场景切换清理逻辑

### TP-021（ITEM_FLOAT）：飘字点击响应（可选）
- **scenario**：场景 1
- **module**：`ITEM_FLOAT`
- **precondition**：飘字显示
- **test_data**：点击飘字
- **expected**：按设计决定（关闭飘字/打开物品详情/无响应）
- **notes**：按游戏设计决定

### TP-022（ITEM_FLOAT）：飘字队列打断
- **scenario**：场景 8
- **module**：`ITEM_FLOAT`
- **precondition**：飘字队列进行中
- **test_data**：触发新飘字
- **expected**：新飘字加入队列、按设计策略显示
- **notes**：FIFO/LIFO/堆叠

### TP-023（ITEM_FLOAT）：弱网下飘字不丢失
- **scenario**：场景 1
- **module**：`ITEM_FLOAT`
- **precondition**：弱网环境
- **test_data**：触发飘字
- **expected**：飘字正常显示（不依赖网络）
- **notes**：飘字是本地渲染

### TP-024（ITEM_FLOAT）：切后台回来飘字恢复
- **scenario**：场景 1
- **module**：`ITEM_FLOAT`
- **precondition**：飘字显示中
- **test_data**：切后台 → 回前台
- **expected**：飘字已消失（按设计）或保留
- **notes**：切后台处理策略

### TP-025（ITEM_FLOAT）：道具数量格式
- **scenario**：场景 1
- **module**：`ITEM_FLOAT`
- **precondition**：获得 1234 个道具
- **test_data**：触发飘字
- **expected**：显示"强化石×1234"或"强化石×1.2K"（按设计）
- **notes**：千分位/缩写

---

## 3. 边界陷阱

### 边界 1：vs C. 战斗飘字
- **混淆点**：「+100 飘字"」——B 测资源、C 测战斗
- **判定规则**：测"道具/货币/积分" → B；测"伤害/治疗/buff" → C
- **实例**：获得金币 +100 → B；暴击伤害 +9999 → C

### 边界 2：vs UI `E.ANIMATION`
- **混淆点**：「飘字"动画"」——B 测内容、E 测动画
- **判定规则**：测"飘字显示什么数字" → B；测"飘字轨迹/淡入淡出动画流畅" → E
- **实例**：飘字"+100 金币" → B；飘字淡出动画帧率 → E

### 边界 3：vs BIZ `BIZ_LOGIC`
- **混淆点**：「金币"获取"」——B 测飘字、BIZ 测计算
- **判定规则**：测"飘字显示什么" → B；测"金币计算公式/扣减逻辑" → BIZ
- **实例**：飘字"+100 金币" → B；金币计算公式（任务奖励 × 倍率） → BIZ

### 边界 4：vs D. 模态弹窗
- **混淆点**：「奖励"展示"」——B 测单个飘字、D 测汇总弹窗
- **判定规则**：测"单个道具/货币飘字" → B；测"批量奖励汇总弹窗" → D
- **实例**：开宝箱道具飘字 → B；登录礼包汇总弹窗 → D

---

## 4. 验证证据

### 视觉证据
- 各种飘字截图（+100/-50/SSR 高亮）
- 多飘字队列截图
- 跨语言飘字截图

### 日志证据
- `float_text.show` 事件（参数：item_id/数量/正负号）
- `float_text.batch` 事件
- `float_text.clear` 事件

### 数据证据
- 玩家资源表 `currency_balance`
- 道具表 `item_count`
- 飘字日志（按 player_id + 时间）

### 性能证据
- 单飘字渲染 < 50ms
- 100 飘字同屏 FPS ≥ 25
- 飘字动画帧率 ≥ 30fps
