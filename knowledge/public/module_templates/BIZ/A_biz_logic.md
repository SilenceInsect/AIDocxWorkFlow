# A. 核心业务逻辑

> **子类代码**：`BIZ_LOGIC`
> **归属模块**：`BIZ`
> **来源**：用户细化定义 §1「核心业务逻辑」
>
> **测什么**：游戏核心业务逻辑的全链路闭环、分支/中断/限制类异常、数值业务运算、风控约束规则、系统间联动业务。
> **不测什么**：页面 UI 渲染（归 UI）、网络底层收发包（归 UTIL B）、配置表字段（归 CONFIG）、单笔操作日志（归 LOG）。
> **与其他子类的差异**：A 关注"业务逻辑/计算/规则"——B 关注"数据流"，C 关注"协议"，D 关注"状态机"，E 关注"数据库"，F 关注"并发"，G 关注"定时任务"，H 关注"付费"，I 关注"审计"。

---

## 1. 典型场景

### 场景 1：道具产出 / 消耗闭环
- 业务背景：杀怪掉落、商城购买、邮件发放、NPC 给予
- 涉及业务：背包增减、堆叠、过期清理
- 触发动作：完成一笔产出或消耗
- 验证点：背包数量正确、堆叠正确、产出/消耗日志落库

### 场景 2：抽卡 / 概率保底
- 业务背景：角色卡池、武器卡池
- 涉及业务：概率计算、保底计数、累计奖励
- 触发动作：单次抽卡 / 触发保底
- 验证点：概率分布在合理范围；保底计数累计正确

### 场景 3：任务流程
- 业务背景：主线/支线/日常/周常任务
- 涉及业务：进度更新、奖励发放、刷新周期
- 触发动作：完成任务条件 / 领取奖励
- 验证点：进度累计、奖励正确、过期清理

### 场景 4：战斗结算
- 业务背景：PVE 副本 / PVP 对战
- 涉及业务：伤害计算、暴击/闪避、胜负判定、奖励发放
- 触发动作：完成战斗
- 验证点：伤害公式正确、奖励正确发放

### 场景 5：商城购买 + 兑换合成
- 业务背景：商城购买、道具合成
- 涉及业务：扣款、限购次数扣减、合成公式、产出道具
- 触发动作：购买 / 合成
- 验证点：扣款正确、限购扣减、合成产出符合配方

### 场景 6：邮件收发
- 业务背景：系统邮件、玩家邮件、附件
- 涉及业务：发件、收件、附件领取、过期清理
- 触发动作：发送邮件 / 领取附件
- 验证点：邮件状态机正确、附件发放正确、过期清理

### 场景 7：组队社交 + 赛季活动
- 业务背景：组队副本、赛季任务
- 涉及业务：组队匹配、队长权限、赛季积分累计
- 触发动作：完成组队 / 赛季结算
- 验证点：组队状态正确、赛季积分与奖励发放

### 场景 8：分支/中断/限制异常
- 业务背景：操作中途退出 / 网络中断 / 资源不足 / 等级未解锁 / 活动过期
- 涉及业务：操作回滚、状态恢复、提示拦截
- 触发动作：触发任一异常分支
- 验证点：资源不丢失、状态可恢复、限制正确拦截

### 场景 9：数值业务计算
- 业务背景：伤害、属性加成、暴击/闪避、成长属性、概率、扣减
- 涉及业务：伤害公式、加成计算、保底、扣减
- 触发动作：触发一次数值计算
- 验证点：计算结果与预期一致（边界值 0/1/最大）

### 场景 10：风控与约束
- 业务背景：每日上限、堆叠上限、付费档位、防沉迷
- 涉及业务：上限校验、付费限额、时长限制
- 触发动作：达到上限 / 超时
- 验证点：上限正确拦截、防沉迷生效

### 场景 11：系统间联动
- 业务背景：完成副本解锁商城、充值触发累充、活动完成发礼包
- 涉及业务：跨系统触发、状态同步
- 触发动作：完成前置 / 触发后置
- 验证点：联动链路完整、无重复触发

---

## 2. 种子测试点（TP 模板）

### TP-001（BIZ_LOGIC）：道具产出闭环
- **scenario**：场景 1
- **module**：`BIZ_LOGIC`
- **precondition**：玩家背包空，杀怪掉落 1 把"铁剑"
- **test_data**：`monster_drop(player_id, item_id=1001, count=1)`
- **expected**：背包 +1、堆叠正确、产出日志 `ASSET_CHANGE` 上报
- **notes**：注意"产出"vs"消耗"日志区分

### TP-002（BIZ_LOGIC）：道具消耗闭环
- **scenario**：场景 1
- **module**：`BIZ_LOGIC`
- **precondition**：背包有 5 个"血瓶"
- **test_data**：`use_item(player_id, item_id=2001, count=1)`
- **expected**：背包 -1、回血生效、消耗日志上报
- **notes**：注意"使用"vs"丢弃"vs"出售"

### TP-003（BIZ_LOGIC）：堆叠上限
- **scenario**：场景 1
- **module**：`BIZ_LOGIC`
- **precondition**：血瓶堆叠上限 99
- **test_data**：连续产出 200 个血瓶
- **expected**：第 100 个时溢出提示，背包不超 99
- **notes**：注意"堆叠"vs"分格"

### TP-004（BIZ_LOGIC）：抽卡保底计数
- **scenario**：场景 2
- **module**：`BIZ_LOGIC`
- **precondition**：玩家已抽 89 次无 UP
- **test_data**：第 90 次抽卡
- **expected**：必出 UP 角色、保底计数清零
- **notes**：注意"硬保底"vs"软保底"vs"概率 UP"

### TP-005（BIZ_LOGIC）：抽卡概率分布
- **scenario**：场景 2
- **module**：`BIZ_LOGIC`
- **precondition**：UP 概率 1.6%
- **test_data**：100 万次模拟
- **expected**：UP 出现比例 ≈ 1.6% ± 0.1%
- **notes**：注意"模拟"vs"实际"误差，伪随机种子影响

### TP-006（BIZ_LOGIC）：任务进度累计
- **scenario**：场景 3
- **module**：`BIZ_LOGIC`
- **precondition**：日常任务"完成 3 把副本"，进度 2/3
- **test_data**：`dungeon_complete(player_id, dungeon_id=1)`
- **expected**：进度 3/3、任务完成、奖励可领
- **notes**：注意"任务进度"vs"任务奖励"两个时点

### TP-007（BIZ_LOGIC）：日常任务零点重置
- **scenario**：场景 3
- **module**：`BIZ_LOGIC`
- **precondition**：日常任务已领奖
- **test_data**：跨过 0 点
- **expected**：任务刷新、未领奖励清空
- **notes**：注意"重置"vs"清空"vs"累计"

### TP-008（BIZ_LOGIC）：战斗伤害公式
- **scenario**：场景 4
- **module**：`BIZ_LOGIC`
- **precondition**：攻击力 100，防御 50，暴击率 20%
- **test_data**：`calc_damage(atk=100, def=50, crit=0.2)`
- **expected**：基础伤害 = max(1, 100-50)=50；暴击伤害 = 50*1.5=75
- **notes**：注意"减法公式"vs"除法公式"

### TP-009（BIZ_LOGIC）：暴击独立随机
- **scenario**：场景 4
- **module**：`BIZ_LOGIC`
- **precondition**：100 次战斗
- **test_data**：观察暴击率
- **expected**：暴击次数 ≈ 20 次
- **notes**：注意"暴击"vs"暴伤"是两参数

### TP-010（BIZ_LOGIC）：PVP 胜负判定
- **scenario**：场景 4
- **module**：`BIZ_LOGIC`
- **precondition**：玩家 A vs 玩家 B
- **test_data**：`pvp_settle(A, B)`
- **expected**：按规则判定胜负、双方积分/MMR 更新
- **notes**：注意"胜"vs"平"vs"负"三种结局

### TP-011（BIZ_LOGIC）：商城限购扣减
- **scenario**：场景 5
- **module**：`BIZ_LOGIC`
- **precondition**：玩家已购 1/2（限购 2 次）
- **test_data**：`purchase(player_id, item_id, count=1)`
- **expected**：第二次成功、扣款 + 限购 -1
- **notes**：注意"日限购"vs"周限购"vs"永久限购"

### TP-012（BIZ_LOGIC）：限购上限拦截
- **scenario**：场景 5
- **module**：`BIZ_LOGIC`
- **precondition**：玩家已购 2/2
- **test_data**：第 3 次购买
- **expected**：拦截 + 标准错误码 `PURCHASE_LIMIT_REACHED`
- **notes**：注意"前端拦截"vs"后端拦截"

### TP-013（BIZ_LOGIC）：合成公式正确
- **scenario**：场景 5
- **module**：`BIZ_LOGIC`
- **precondition**：3 个"铁矿"合成 1 个"铁锭"
- **test_data**：`compose(player_id, recipe_id=3001)`
- **expected**：铁矿 -3、铁锭 +1、合成日志
- **notes**：注意"合成"vs"打造"vs"升级"

### TP-014（BIZ_LOGIC）：邮件附件领取
- **scenario**：场景 6
- **module**：`BIZ_LOGIC`
- **precondition**：邮件含 100 钻石
- **test_data**：`mail_claim(player_id, mail_id)`
- **expected**：钻石 +100、邮件状态 领取→已领
- **notes**：注意"部分领取"vs"全部领取"

### TP-015（BIZ_LOGIC）：邮件过期清理
- **scenario**：场景 6
- **module**：`BIZ_LOGIC`
- **precondition**：邮件 7 天有效期
- **test_data**：第 8 天查看
- **expected**：邮件隐藏、附件作废
- **notes**：注意"未读"vs"未领"vs"已领"三种状态

### TP-016（BIZ_LOGIC）：组队匹配成功
- **scenario**：场景 7
- **module**：`BIZ_LOGIC`
- **precondition**：3 人匹配队列
- **test_data**：第 3 人加入
- **expected**：匹配成功、组队状态 队列→组队中
- **notes**：注意"匹配中"vs"匹配成功"vs"副本中"

### TP-017（BIZ_LOGIC）：赛季积分累计
- **scenario**：场景 7
- **module**：`BIZ_LOGIC`
- **precondition**：赛季积分 0
- **test_data**：完成 1 场 PVP 胜利 +20 分
- **expected**：积分 0→20、排行榜同步
- **notes**：注意"积分"vs"段位"vs"奖励"

### TP-018（BIZ_LOGIC）：操作中途退出
- **scenario**：场景 8
- **module**：`BIZ_LOGIC`
- **precondition**：玩家购买流程进行中
- **test_data**：玩家强制退出客户端
- **expected**：未完成操作回滚、资源不丢失
- **notes**：注意"中途退出"vs"网络中断"vs"主动取消"

### TP-019（BIZ_LOGIC）：网络中断恢复
- **scenario**：场景 8
- **module**：`BIZ_LOGIC`
- **precondition**：合成操作进行中网络断开
- **test_data**：网络恢复 + 客户端重连
- **expected**：操作幂等回放或回滚、不出现重复扣款
- **notes**：注意"幂等"vs"重试"vs"补偿"

### TP-020（BIZ_LOGIC）：等级未解锁
- **scenario**：场景 8
- **module**：`BIZ_LOGIC`
- **precondition**：玩家 Lv.10、副本要求 Lv.20
- **test_data**：`enter_dungeon(player_id, dungeon_id=2)`
- **expected**：拦截 + 错误码 `LEVEL_NOT_ENOUGH`、背包不扣
- **notes**：注意"等级"vs"前置任务"vs"vip 等级"

### TP-021（BIZ_LOGIC）：活动过期
- **scenario**：场景 8
- **module**：`BIZ_LOGIC`
- **precondition**：活动已结束
- **test_data**：`activity_enter(player_id, activity_id=5)`
- **expected**：拦截 + 错误码 `ACTIVITY_EXPIRED`、活动入口隐藏
- **notes**：注意"未开启"vs"进行中"vs"已结束"

### TP-022（BIZ_LOGIC）：属性加成叠加
- **scenario**：场景 9
- **module**：`BIZ_LOGIC`
- **precondition**：基础攻击 100、装备 +20、Buff +30
- **test_data**：`calc_final_atk(player_id)`
- **expected**：最终攻击 = 100+20+30 = 150
- **notes**：注意"加法"vs"乘法"叠加

### TP-023（BIZ_LOGIC）：伤害边界 0
- **scenario**：场景 9
- **module**：`BIZ_LOGIC`
- **precondition**：防御 100、攻击 50
- **test_data**：`calc_damage(50, 100)`
- **expected**：基础伤害 = max(1, 50-100) = 1（不破 0）
- **notes**：注意"穿透"vs"真实伤害"

### TP-024（BIZ_LOGIC）：防沉迷时长限制
- **scenario**：场景 10
- **module**：`BIZ_LOGIC`
- **precondition**：未成年玩家已在线 90 分钟
- **test_data**：在线到 91 分钟
- **expected**：强制下线提示 + 在线奖励停止
- **notes**：注意"未成年"vs"成年"+"节假日"

### TP-025（BIZ_LOGIC）：付费档位限制
- **scenario**：场景 10
- **module**：`BIZ_LOGIC`
- **precondition**：单笔 648 上限
- **test_data**：尝试 1000 元
- **expected**：拦截 + 错误码 `AMOUNT_EXCEED`
- **notes**：注意"单笔"vs"单日"vs"单月"上限

### TP-026（BIZ_LOGIC）：完成任务解锁商城道具
- **scenario**：场景 11
- **module**：`BIZ_LOGIC`
- **precondition**：主线任务"通关第一章"未完成
- **test_data**：`chapter_complete(player_id, chapter=1)`
- **expected**：商城"专属礼包"出现、可购买
- **notes**：注意"解锁"vs"显示"vs"可购买"是 3 个时点

### TP-027（BIZ_LOGIC）：充值触发累充奖励
- **scenario**：场景 11
- **module**：`BIZ_LOGIC`
- **precondition**：累充 0/100
- **test_data**：`recharge(player_id, amount=100)`
- **expected**：累充进度 0→100、累充奖励可领
- **notes**：注意"首充"vs"累充"vs"单笔"

### TP-028（BIZ_LOGIC）：活动完成发限时礼包
- **scenario**：场景 11
- **module**：`BIZ_LOGIC`
- **precondition**：活动"春日签到"完成 7/7
- **test_data**：`activity_finish(player_id, activity_id)`
- **expected**：限时礼包邮件发送、邮件含 24h 倒计时
- **notes**：注意"限时"vs"永久"+"过期清理"

### TP-029（BIZ_LOGIC）：道具过期自动清理
- **scenario**：场景 1
- **module**：`BIZ_LOGIC`
- **precondition**：限时道具 24h 过期
- **test_data**：第 25 小时查看背包
- **expected**：道具消失、清理日志上报
- **notes**：注意"过期"vs"销毁"vs"回收"

### TP-030（BIZ_LOGIC）：交易风控拦截
- **scenario**：场景 10
- **module**：`BIZ_LOGIC`
- **precondition**：玩家 1 分钟内交易 50 次
- **test_data**：`trade(player_id, item_id)` 第 51 次
- **expected**：拦截 + 风控告警 + 临时封禁
- **notes**：注意"频次"vs"金额"风控

---

## 3. 边界陷阱

### 边界 1：vs C. 协议交互
- **混淆点**：「购买"扣款"」——A 测业务逻辑、C 测协议
- **判定规则**：测"扣款/发货业务逻辑" → A；测"协议字段/错误码" → C
- **实例**：商城购买扣 100 钻石 → A-011；购买协议字段 type=2001 → C

### 边界 2：vs D. 状态机
- **混淆点**：「活动"状态"」——A 测业务逻辑、D 测状态机
- **判定规则**：测"业务结果" → A；测"状态切换合法性" → D
- **实例**：活动结束清空临时道具 → A-029；活动状态 未开启→进行中→结束 → D

### 边界 3：vs E. 数据库持久化
- **混淆点**：「道具"持久化"」——A 测业务逻辑、E 测 DB
- **判定规则**：测"业务加减" → A；测"DB 落库/事务/恢复" → E
- **实例**：背包 +1 业务逻辑 → A-001；DB 落库与事务 → E

### 边界 4：vs H. 付费商业化
- **混淆点**：「充值"业务"」——A 测业务逻辑、H 测付费
- **判定规则**：测"业务触发" → A；测"订单流程/回调" → H
- **实例**：充值触发累充 → A-027；订单回调 → H

### 边界 5：vs UI
- **混淆点**：「购买"按钮"」——A 测业务、UI 测界面
- **判定规则**：测"扣款发货" → A；测"按钮样式" → UI
- **实例**：购买扣款发货 → A；购买按钮 disabled 样式 → UI

---

## 4. 验证证据

### 视觉证据
- 背包数量变化截图
- 商城购买完成截图
- 任务进度条更新截图

### 日志证据
- `ASSET_CHANGE` 资源变动日志
- `PURCHASE_SUCCESS` 购买成功日志
- `ACTIVITY_ENTER` 活动进入日志
- `PROGRESS_TRIGGER` 进度触发日志
- `ERROR_LIMIT_REACHED` 限制拦截日志

### 数据证据
- 玩家背包表 `bag.item_id, count, expire_at`
- 玩家任务表 `task.progress, status`
- 商城限购表 `purchase_limit.used, total`
- 邮件表 `mail.status, claimed_at, expire_at`
- 数据库应与业务结果完全一致

### 性能证据
- 单笔业务耗时 < 100ms
- 批量业务（如 1000 笔 GM 发奖）< 30s
- 概率模拟误差 < 0.1%
