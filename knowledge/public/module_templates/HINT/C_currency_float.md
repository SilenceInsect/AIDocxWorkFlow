# C. 战斗飘字（伤害/治疗/暴击/Buff/Debuff）

> **子类代码**：`CURRENCY_FLOAT`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 C（v1.7 从 v1.6.1 `CURRENCY_FLOAT` 拆分独立，专注于战斗飘字）
>
> **测什么**：战斗中伤害/治疗/暴击/buff 增益/debuff 减益/免疫/闪避/格挡**临时文字提示**的显示、颜色、位置、优先级。
> **不测什么**：战斗伤害**计算公式**（归 BIZ `A.BIZ_LOGIC`）、飘字**动画样式**（归 UI `E.ANIMATION`）、资源类飘字（归 B `ITEM_FLOAT`）。
> **与其他子类的差异**：C 是"战斗"飘字；B 是"资源"飘字；C 涉及"实时战斗事件"、B 涉及"资源获取/扣除"。

---

## 1. 典型场景

### 场景 1：普通伤害飘字
- 业务背景：玩家攻击怪物
- 涉及元素：伤害飘字
- 触发动作：造成伤害
- 验证点：白色飘字、显示伤害值

### 场景 2：暴击伤害飘字
- 业务背景：玩家暴击
- 涉及元素：暴击飘字
- 触发动作：触发暴击
- 验证点：黄色/红色飘字、放大、显示"暴击"前缀

### 场景 3：治疗飘字
- 业务背景：玩家被治疗
- 涉及元素：治疗飘字
- 触发动作：获得治疗
- 验证点：绿色飘字、向上飘动、显示"+治疗量"

### 场景 4：Buff 增益飘字
- 业务背景：玩家获得"攻击 +10%" buff
- 涉及元素：buff 飘字
- 触发动作：施加 buff
- 验证点：蓝色/增益色飘字、显示 buff 名

### 场景 5：Debuff 减益飘字
- 业务背景：玩家被施加"中毒"
- 涉及元素：debuff 飘字
- 触发动作：施加 debuff
- 验证点：紫色/减益色飘字、显示 debuff 名

### 场景 6：免疫
- 业务背景：玩家免疫一次伤害
- 涉及元素：免疫飘字
- 触发动作：受到攻击被免疫
- 验证点：显示"免疫"、不显示伤害数字

### 场景 7：闪避
- 业务背景：玩家闪避攻击
- 涉及元素：闪避飘字
- 触发动作：受到攻击闪避
- 验证点：显示"闪避"、不显示伤害

### 场景 8：格挡
- 业务背景：玩家格挡攻击
- 涉及元素：格挡飘字
- 触发动作：格挡成功
- 验证点：显示"格挡" + 减伤数字

### 场景 9：多目标 AOE 飘字
- 业务背景：AOE 技能命中 5 个目标
- 涉及元素：5 个飘字
- 触发动作：AOE 技能
- 验证点：5 个飘字分别显示、不重叠

### 场景 10：持续伤害（DOT）
- 业务背景：中毒效果每秒跳一次
- 涉及元素：DOT 飘字
- 触发动作：每 1s
- 验证点：每秒显示伤害飘字、不卡顿

---

## 2. 种子测试点（TP 模板）

### TP-001（CURRENCY_FLOAT）：普通伤害飘字
- **scenario**：场景 1
- **module**：`CURRENCY_FLOAT`
- **precondition**：战斗场景
- **test_data**：造成 100 伤害
- **expected**：白色飘字"100"
- **notes**：默认颜色配置

### TP-002（CURRENCY_FLOAT）：暴击伤害飘字
- **scenario**：场景 2
- **module**：`CURRENCY_FLOAT`
- **precondition**：暴击率触发
- **test_data**：暴击 500 伤害
- **expected**：黄色/红色飘字"500"、放大 1.5x、显示"暴击"或图标
- **notes**：与 TP-001 视觉差异

### TP-003（CURRENCY_FLOAT）：暴击伤害前缀文案
- **scenario**：场景 2
- **module**：`CURRENCY_FLOAT`
- **precondition**：暴击
- **test_data**：暴击
- **expected**：飘字"暴击!500" 或 "500!"（按设计）
- **notes**：文案样式多变

### TP-004（CURRENCY_FLOAT）：治疗飘字
- **scenario**：场景 3
- **module**：`CURRENCY_FLOAT`
- **precondition**：被治疗
- **test_data**：+200 治疗
- **expected**：绿色飘字"+200"、向上飘动
- **notes**：绿色（增益）vs 白色（伤害）

### TP-005（CURRENCY_FLOAT）：群体治疗飘字
- **scenario**：场景 3
- **module**：`CURRENCY_FLOAT`
- **precondition**：AOE 治疗 5 个队友
- **test_data**：5 个 +100 治疗
- **expected**：5 个绿飘字分别显示
- **notes**：与 AOE 伤害区分

### TP-006（CURRENCY_FLOAT）：Buff 增益飘字
- **scenario**：场景 4
- **module**：`CURRENCY_FLOAT`
- **precondition**：施加 buff
- **test_data**：获得"攻击 +10%" 持续 30s
- **expected**：蓝色飘字"攻击 +10%"或"获得增益"
- **notes**：增益色（蓝/白）

### TP-007（CURRENCY_FLOAT）：Debuff 减益飘字
- **scenario**：场景 5
- **module**：`CURRENCY_FLOAT`
- **precondition**：被施加 debuff
- **test_data**：中毒 5s
- **expected**：紫色飘字"中毒"或图标
- **notes**：减益色（紫/红）

### TP-008（CURRENCY_FLOAT）：免疫飘字
- **scenario**：场景 6
- **module**：`CURRENCY_FLOAT`
- **precondition**：被攻击时免疫
- **test_data**：触发免疫
- **expected**：飘字"免疫"、不显示伤害数字
- **notes**：纯文字、不带数字

### TP-009（CURRENCY_FLOAT）：闪避飘字
- **scenario**：场景 7
- **module**：`CURRENCY_FLOAT`
- **precondition**：受到攻击时闪避
- **test_data**：触发闪避
- **expected**：飘字"闪避"、不显示伤害
- **notes**：与免疫区分

### TP-010（CURRENCY_FLOAT）：格挡飘字
- **scenario**：场景 8
- **module**：`CURRENCY_FLOAT`
- **precondition**：受到攻击时格挡
- **test_data**：格挡 50% 减伤
- **expected**：飘字"格挡" + 减伤数字（如"格挡 -30"）
- **notes**：格挡文字+减伤

### TP-011（CURRENCY_FLOAT）：AOE 5 目标飘字队列
- **scenario**：场景 9
- **module**：`CURRENCY_FLOAT`
- **precondition**：AOE 技能
- **test_data**：命中 5 个目标
- **expected**：5 个飘字分别显示在 5 个目标位置
- **notes**：位置区分、不重叠

### TP-012（CURRENCY_FLOAT）：AOE 20 目标性能
- **scenario**：场景 9
- **module**：`CURRENCY_FLOAT`
- **precondition**：大型 AOE
- **test_data**：命中 20 个目标
- **expected**：20 个飘字、FPS ≥ 25
- **notes**：性能边界

### TP-013（CURRENCY_FLOAT）：DOT 每秒跳伤害
- **scenario**：场景 10
- **module**：`CURRENCY_FLOAT`
- **precondition**：中毒
- **test_data**：每 1s 跳 50 伤害
- **expected**：每秒显示飘字
- **notes**：持续 5s → 5 个飘字

### TP-014（CURRENCY_FLOAT）：多 buff 叠加飘字
- **scenario**：场景 4
- **module**：`CURRENCY_FLOAT`
- **precondition**：连续施加 3 个 buff
- **test_data**：攻击+10% + 防御+10% + 速度+10%
- **expected**：3 个 buff 飘字分别显示
- **notes**：叠加 vs 替换逻辑

### TP-015（CURRENCY_FLOAT）：暴击+暴击+暴击连击
- **scenario**：场景 2
- **module**：`CURRENCY_FLOAT`
- **precondition**：高频暴击
- **test_data**：1 秒内 3 次暴击
- **expected**：3 个暴击飘字队列
- **notes**：连击视觉强化

### TP-016（CURRENCY_FLOAT）：飘字颜色配置可读性
- **scenario**：场景 1
- **module**：`CURRENCY_FLOAT`
- **precondition**：色盲玩家
- **test_data**：触发各种飘字
- **expected**：飘字除颜色外有其他可区分特征（文字/图标）
- **notes**：无障碍 G 配合

### TP-017（CURRENCY_FLOAT）：0 伤害不显示
- **scenario**：场景 1
- **module**：`CURRENCY_FLOAT`
- **precondition**：造成 0 伤害
- **test_data**：触发飘字
- **expected**：不显示飘字
- **notes**：边界值

### TP-018（CURRENCY_FLOAT）：伤害破百万格式
- **scenario**：场景 2
- **module**：`CURRENCY_FLOAT`
- **precondition**：高级暴击
- **test_data**：999,999 伤害
- **expected**：完整显示数字或"999K"
- **notes**：大数字格式

### TP-019（CURRENCY_FLOAT）：治疗过量不显示
- **scenario**：场景 3
- **module**：`CURRENCY_FLOAT`
- **precondition**：满血
- **test_data**：治疗但满血
- **expected**：按设计（不显示/显示"溢出"）
- **notes**：治疗溢出规则

### TP-020（CURRENCY_FLOAT）：PvP 飘字区分
- **scenario**：场景 1
- **module**：`CURRENCY_FLOAT`
- **precondition**：PvP 战斗
- **test_data**：玩家对玩家
- **expected**：飘字颜色与 PvE 一致或区分（按设计）
- **notes**：PvP 视觉差异

---

## 3. 边界陷阱

### 边界 1：vs B. 资源飘字
- **混淆点**：「+100 飘字"」——C 测战斗、B 测资源
- **判定规则**：测"伤害/治疗/buff" → C；测"道具/货币/积分" → B
- **实例**：暴击 +9999 伤害 → C；开宝箱 +100 金币 → B

### 边界 2：vs UI `E.ANIMATION`
- **混淆点**：「飘字"动画"」——C 测内容、E 测动画
- **判定规则**：测"飘字显示什么" → C；测"飘字轨迹/动画流畅度" → E
- **实例**：暴击黄色飘字 → C；暴击放大动画 → E

### 边界 3：vs BIZ `A.BIZ_LOGIC`
- **混淆点**：「暴击"率"」——C 测飘字、BIZ 测计算
- **判定规则**：测"暴击飘字显示" → C；测"暴击率公式（30% 触发）" → BIZ
- **实例**：暴击飘字"暴击!500" → C；暴击计算 → BIZ

### 边界 4：vs UI `F.GUIDE_HINT`
- **混淆点**：「buff"图标"」——C 测飘字、F 测 buff 图标
- **判定规则**：测"获得 buff 的文字飘字" → C；测"buff 图标常驻显示" → F
- **instance**：获得 buff 飘字"攻击+10%" → C；buff 图标常驻在状态栏 → F

### 边界 5：vs UI `J.战斗 UI`（游戏专项）
- **混淆点**：「BUFF"显示"」——C 测飘字、J 测常驻图标
- **判定规则**：测"获得 buff 的瞬间飘字" → C；测"buff 图标常驻 30s 倒计时" → J
- **实例**：buff 飘字"攻击+10%" → C；buff 图标 + 倒计时进度条 → J

---

## 4. 验证证据

### 视觉证据
- 普通/暴击/治疗/buff/debuff 飘字截图对比
- 多目标 AOE 飘字位置截图
- 大数字飘字截图

### 日志证据
- `float_text.damage` 事件（参数：target_id/damage/critical）
- `float_text.heal` 事件
- `float_text.buff/debuff` 事件（参数：buff_id/source）

### 数据证据
- 战斗日志表 `combat_log`（含 damage 字段）
- 玩家 buff 表 `player_buff`

### 性能证据
- 单飘字渲染 < 30ms（战斗更严苛）
- 20 飘字同屏 FPS ≥ 25
- DOT 1s 跳伤害无卡顿
