# P. BIZ 游戏项目专项补充（仅游戏项目）

> **非测试类型**——本文件是**仅游戏项目**的 BIZ 测试点补充。
> 非游戏项目（PC 后台、移动端 App、Web 工具）**忽略**本文件。
>
> **来源**：用户细化定义 §5「游戏专项补充高频测试点」——战斗业务 / 社交业务 / 运营活动 / 兜底回滚 4 大类

---

## 1. 战斗业务

> 业务背景：技能释放、伤害结算、仇恨、复活、掉落分配、多人同步帧

### 场景
- 技能释放、伤害公式、仇恨系统
- 死亡复活机制
- 多人战斗同步帧
- 掉落分配规则

### 种子 TP

#### TP-001（P-战斗）：技能释放业务
- **module**：`BIZ_LOGIC`（A 子类）
- **precondition**：玩家 MP 100、技能 50 消耗、CD 0
- **test_data**：`cast_skill(player_id, skill_id=1)`
- **expected**：MP -50、CD 5s、伤害生效
- **notes**：与 BIZ-D（技能冷却状态机）配合

#### TP-002（P-战斗）：伤害结算业务
- **module**：`BIZ_LOGIC`
- **precondition**：ATK 100、DEF 50、暴击率 20%
- **test_data**：`calc_damage(100, 50, 0.2)`
- **expected**：基础 50、暴击 75、暴伤 1.5 倍
- **notes**：注意"减法公式"vs"除法公式"+"暴伤独立"

#### TP-003（P-战斗）：仇恨系统
- **module**：`BIZ_LOGIC`
- **precondition**：BOSS 初始仇恨 A=100
- **test_data**：A 攻击、B 攻击
- **expected**：BOSS 优先攻击仇恨高者
- **notes**：注意"仇恨"vs"治疗量"vs"伤害量"

#### TP-004（P-战斗）：PVP 复活
- **module**：`BIZ_STATE_MACHINE`（D 子类）
- **precondition**：玩家死亡
- **test_data**：`revive(player_id)`
- **expected**：状态 死亡→存活、HP 30%、无敌 3s
- **notes**：注意"原地"vs"回城"+"无敌状态"

#### TP-005（P-战斗）：多人同步帧
- **module**：`BIZ_DATA_FLOW`（B 子类）
- **precondition**：4 人副本战斗
- **test_data**：1 分钟战斗
- **expected**：服务端帧同步 30 FPS、客户端延迟 < 200ms
- **notes**：与 P-F（百人同屏）区分

#### TP-006（P-战斗）：BOSS 掉落分配
- **module**：`BIZ_CONCURRENCY`（F 子类）
- **precondition**：4 人组队击杀 BOSS
- **test_data**：BOSS 死亡
- **expected**：按 roll/分配规则、每人得对应道具
- **notes**：注意"roll"vs"分配"vs"队长分配"+"每人必得"vs"概率"

#### TP-007（P-战斗）：PVE 副本结算
- **module**：`BIZ_LOGIC`
- **precondition**：4 人副本通关
- **test_data**：副本胜利
- **expected**：每人按贡献度发奖、副本次数 -1
- **notes**：注意"贡献"vs"平分"+"队长加成"

#### TP-008（P-战斗）：PVP 段位积分
- **module**：`BIZ_LOGIC`
- **precondition**：玩家段位黄金 III
- **test_data**：赢 1 场 +25、输 1 场 -20
- **expected**：积分正确更新、连胜/连败奖励
- **notes**：注意"胜"vs"平"vs"负"+"段位升降"

---

## 2. 社交业务

> 业务背景：好友、公会、组队、私聊/公聊、赠送道具、跨服社交

### 场景
- 好友添加/删除/赠送
- 公会创建/解散/贡献
- 组队邀请/匹配
- 私聊/公聊/世界聊天
- 跨服社交

### 种子 TP

#### TP-009（P-社交）：好友添加
- **module**：`BIZ_LOGIC`
- **precondition**：玩家 A 搜索玩家 B
- **test_data**：`add_friend(A, B)`
- **expected**：B 收到好友申请、接受后双向好友
- **notes**：注意"单向"vs"双向"+"黑名单"

#### TP-010（P-社交）：好友赠送体力
- **module**：`BIZ_LOGIC`
- **precondition**：玩家 A 体力满、好友 B 体力 0
- **test_data**：`gift_stamina(B)` from A
- **expected**：B 收到体力、A 不扣、每日 1 次
- **notes**：注意"每日"vs"每周"+"双向赠送"

#### TP-011（P-社交）：公会创建
- **module**：`BIZ_LOGIC`
- **precondition**：玩家满足条件（等级/VIP）
- **test_data**：`create_guild(player_id, name)`
- **expected**：公会创建成功、扣 1000 钻、玩家成为会长
- **notes**：注意"重名"vs"敏感词"+"费用"

#### TP-012（P-社交）：公会解散
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：公会 1 人（会长）
- **test_data**：`dissolve_guild(guild_id)`
- **expected**：公会解散、所有成员通知、资金按规则处理
- **notes**：注意"会长"vs"管理员"+"强制解散"

#### TP-013（P-社交）：公会贡献
- **module**：`BIZ_LOGIC`
- **precondition**：公会成员
- **test_data**：`contribute(player_id, 100 diamond)`
- **expected**：公会资金 +100、玩家贡献值 +100
- **notes**：注意"个人贡献"vs"公会总贡献"

#### TP-014（P-社交）：组队邀请
- **module**：`BIZ_LOGIC`
- **precondition**：玩家 A 邀请 B 组队
- **test_data**：`invite_team(A, B)`
- **expected**：B 收到邀请、接受后组队
- **notes**：注意"邀请"vs"申请"+"离线邀请"

#### TP-015（P-社交）：组队匹配
- **module**：`BIZ_LOGIC`
- **precondition**：3 人匹配队列
- **test_data**：第 3 人加入
- **expected**：匹配成功、组队成功、自动入副本
- **notes**：注意"匹配中"vs"匹配成功"+"超时"

#### TP-016（P-社交）：私聊
- **module**：`BIZ_DATA_FLOW`（B 子类）
- **precondition**：A 与 B 为好友
- **test_data**：`send_private_msg(A, B, content)`
- **expected**：B 实时收到、A 收到回执
- **notes**：注意"在线"vs"离线"+"消息持久化"

#### TP-017（P-社交）：世界聊天
- **module**：`BIZ_CONCURRENCY`（F 子类）
- **precondition**：1000 玩家在线
- **test_data`：`send_world_msg(player_id, content)`
- **expected**：所有在线 1s 内收到、敏感词拦截
- **notes**：注意"全服"vs"频道"+"广播风暴"

#### TP-018（P-社交）：跨服好友
- **module**：`BIZ_DATA_FLOW`
- **precondition**：服 A 玩家想加服 B 玩家
- **test_data`：`add_cross_friend(A, B)`
- **expected**：跨服好友关系建立、私聊跨服转发
- **notes**：注意"跨服协议"+"数据同步"

#### TP-019（P-社交）：公会跨服战
- **module**：`BIZ_CONCURRENCY`
- **precondition**：服 A 公会 vs 服 B 公会
- **test_data`：触发跨服战
- **expected**：双方可匹配、跨服战斗正常
- **notes**：注意"跨服匹配"+"延迟"

---

## 3. 运营活动

> 业务背景：限时活动、签到、节日活动、排行榜、全服奖励批量发放

### 场景
- 限时活动开启/结束
- 每日签到
- 节日活动
- 排行榜/赛季
- 全服奖励批量发

### 种子 TP

#### TP-020（P-活动）：每日签到
- **module**：`BIZ_LOGIC`
- **precondition**：玩家未签到
- **test_data`：`sign_in(player_id, day=1)`
- **expected**：第 1 天奖励、签到日历 +1
- **notes**：注意"补签"vs"断签重置"+"连签奖励"

#### TP-021（P-活动）：节日活动开启
- **module**：`BIZ_SCHEDULED_TASK`（G 子类）
- **precondition**：春节活动 2/1-2/15
- **test_data`：2/1 0:00
- **expected**：活动开启、玩家可进入
- **notes**：注意"开服时间"vs"绝对时间"+"时区"

#### TP-022（P-活动）：节日活动结束
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：春节活动结束
- **test_data`：2/15 24:00
- **expected**：活动关闭、临时道具清理
- **notes**：注意"清理"vs"保留"+"活动回顾"

#### TP-023（P-活动）：活动积分累计
- **module**：`BIZ_LOGIC`
- **precondition`：玩家活动积分 0
- **test_data`：`add_activity_score(player_id, 50)`
- **expected`：积分 +50、可领对应档位奖励
- **notes**：注意"档位跳级"vs"逐级"

#### TP-024（P-活动）：活动排行榜
- **module**：`BIZ_LOGIC`
- **precondition`：100 玩家参与
- **test_data`：观察排行榜
- **expected`：按积分排序、TopN 有额外奖励
- **notes**：注意"实时"vs"定时"+"作弊检测"

#### TP-025（P-活动）：赛季积分结算
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition`：赛季结束
- **test_data`：赛季结算
- **expected`：排名归档、段位奖励发放、积分清零
- **notes**：注意"归档"vs"清空"+"下赛季开启"

#### TP-026（P-活动）：赛季奖励发放
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition`：玩家赛季黄金段位
- **test_data`：赛季结束
- **expected`：玩家收到黄金段位奖励邮件
- **notes**：注意"按段位"vs"按排名"+"全服发放"

#### TP-027（P-活动）：全服奖励批量发
- **module**：`BIZ_CONCURRENCY`
- **precondition`：10 万玩家
- **test_data`：运营触发全服发奖
- **expected**：5 分钟内全部到账、无丢失
- **notes**：注意"队列"+"幂等"+"断点续发"

#### TP-028（P-活动）：活动预热
- **module**：`BIZ_STATE_MACHINE`
- **precondition`：活动开始前 1 天
- **test_data`：活动预热
- **expected`：活动入口显示"明日开启"、可看预告
- **notes**：注意"预热"vs"开启"+"倒计时"

#### TP-029（P-活动）：活动参与限制
- **module**：`BIZ_LOGIC`
- **precondition**：活动要求 Lv.30
- **test_data`：Lv.20 玩家尝试参与
- **expected`：拦截 + 错误码 `LEVEL_NOT_ENOUGH`
- **notes**：注意"等级"vs"前置任务"vs"Vip"

#### TP-030（P-活动）：活动排行榜作弊
- **module**：`BIZ_AUDIT_LOG`（I 子类）
- **precondition`：玩家 1 分钟刷 1 万分
- **test_data`：风控扫描
- **expected**：从日志检测异常、封号
- **notes**：注意"实时"vs"事后"+"误封"

---

## 4. 兜底回滚

> 业务背景：充值退款、操作回档、误操作补偿对应的资源增减业务逻辑

### 场景
- 充值退款
- 操作回档
- 误操作补偿
- 资源增减业务

### 种子 TP

#### TP-031（P-回滚）：充值退款回滚
- **module**：`BIZ_PAYMENT`（H 子类）
- **precondition**：玩家已购买 100 钻道具
- **test_data`：支付平台退款
- **expected**：道具回收、钻石扣除、订单状态 已支付→已退款
- **notes**：注意"已使用"vs"未使用"+"部分退款"

#### TP-032（P-回滚）：道具已使用退款
- **module**：`BIZ_PAYMENT`
- **precondition`：玩家已用 100 钻
- **test_data`：退款
- **expected**：钻石扣成负数或拦截 + 提示
- **notes**：注意"风控"vs"强行回滚"

#### TP-033（P-回滚）：操作回档
- **module**：`BIZ_DB_PERSIST`（E 子类）
- **precondition**：服务器回档到 1 小时前
- **test_data`：运营回档
- **expected**：玩家数据回滚到 1 小时前状态
- **notes**：注意"全部"vs"部分"回档

#### TP-034（P-回滚）：回档补偿
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition`：服务器回档影响 1000 玩家
- **test_data`：批量补偿
- **expected`：受影响的玩家收到补偿邮件
- **notes**：注意"补偿"vs"补发"+"补偿方案"

#### TP-035（P-回滚）：误操作补偿
- **module**：`BIZ_LOGIC`
- **precondition`：玩家误卖 100 钻装备
- **test_data`：客服补偿
- **expected**：玩家收到 100 钻装备
- **notes**：注意"客服"vs"自动"+"补偿额度"

#### TP-036（P-回滚）：GM 强制回收
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：发现玩家非法所得
- **test_data**：GM 强制回收
- **expected**：道具回收、写审计日志
- **notes**：注意"GM"vs"自动"+"审计"

#### TP-037（P-回滚）：误发补偿
- **module**：`BIZ_LOGIC`
- **precondition**：GM 误发 10 万钻给玩家
- **test_data`：GM 回收
- **expected`：玩家钻石扣除、通知玩家
- **notes**：注意"误发"vs"故意"+"回收合法性"

#### TP-038（P-回滚）：BUFF 误施加
- **module**：`BIZ_STATE_MACHINE`
- **precondition`：玩家被误施加永久 Buff
- **test_data`：GM 移除 Buff
- **expected**：Buff 移除、属性回退
- **notes**：注意"移除"vs"过期"+"属性回退"

#### TP-039（P-回滚）：活动异常关闭
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：活动因 bug 中途关闭
- **test_data`：运营关闭
- **expected**：已参与玩家补偿、未参与玩家通知
- **notes**：注意"已参与"vs"未参与"+"补偿标准"

#### TP-040（P-回滚）：删号恢复
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家已删号 5 天
- **test_data`：`restore_account(player_id)`
- **expected**：玩家数据恢复、可登录
- **notes**：注意"恢复期"内有效

---

## 5. 边界陷阱

### 边界 1：vs A. 业务
- **混淆点**：「战斗"业务"」——A 测通用业务、P 测游戏专项
- **判定规则**：测"通用业务逻辑" → A；测"游戏专项" → P
- **实例**：通用抽卡 → A-004；战斗伤害公式 → P-002

### 边界 2：vs D. 状态机
- **混淆点**：「Buff"状态"」——D 测通用状态机、P 测游戏专项
- **判定规则**：测"通用状态流转" → D；测"游戏专项状态" → P
- **实例**：通用 Buff 状态机 → D；战斗 Buff → P

### 边界 3：vs F. 并发
- **混淆点**：「组队"并发"」——F 测通用并发、P 测游戏专项
- **判定规则**：测"通用多玩家并发" → F；测"游戏专项" → P
- **实例**：通用抢拍 → F；战斗同步帧 → P-005

### 边界 4：vs G. 定时任务
- **混淆点**：「活动"定时"」——G 测通用定时、P 测游戏专项
- **判定规则**：测"通用定时" → G；测"游戏专项" → P
- **实例**：通用 0 点重置 → G；赛季结算 → P-025

### 边界 5：vs H. 付费
- **混淆点**：「退款"回滚"」——H 测付费、P 测游戏专项
- **判定规则**：测"付费业务" → H；测"游戏专项回滚" → P
- **实例**：退款业务 → H；战斗补偿 → P

### 边界 6：vs I. 审计
- **混淆点**：「回滚"日志"」——I 测业务审计、P 测游戏专项
- **判定规则**：测"业务审计" → I；测"游戏专项补偿" → P
- **实例**：资源变动审计 → I；GM 误发补偿 → P-037

---

## 6. 验证证据

### 视觉证据
- 战斗伤害飘字截图
- 好友列表截图
- 公会战积分榜截图
- 赛季奖励发放截图

### 日志证据
- `BATTLE_SKILL/HIT/CRIT/DEATH/REVIVE` 战斗日志
- `SOCIAL_FRIEND/GUILD/TEAM/CHAT` 社交日志
- `ACTIVITY_ENTER/FINISH/CLAIM` 活动日志
- `ROLLBACK_REFUND/RESTORE/COMPENSATE` 回滚日志
- `GM_OPERATION` GM 操作审计日志

### 数据证据
- 战斗表 `battle.player_id, skill_id, damage, crit, time`
- 好友表 `friend.player_id, friend_id, added_at, intimacy`
- 公会表 `guild.guild_id, name, level, members, fund`
- 活动表 `activity.player_id, activity_id, score, claimed`
- 赛季表 `season.player_id, rank, score, reward_claimed`
- 回滚补偿表 `compensation.player_id, type, amount, reason, op_id`

### 性能证据
- 战斗帧同步延迟 < 200ms
- 好友查询 < 100ms
- 公会成员列表 < 200ms
- 聊天消息延迟 < 1s
- 跨服战斗延迟 < 500ms
- 全服奖励 100 万玩家 5 分钟内完成
- 赛季结算 1 万玩家 < 1 分钟
- 战斗技能释放 < 100ms
