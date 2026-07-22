# D. 状态机

> **子类代码**：`BIZ_STATE_MACHINE`
> **归属模块**：`BIZ`
> **来源**：用户细化定义 §4「状态机（游戏全场景）」
>
> **测什么**：游戏系统状态机（活动/副本/邮件/礼包）、角色/对象状态机、状态流转约束、并发多状态兼容。
> **不测什么**：业务逻辑（归 A）、UI 展示（归 UI）、数据库存储（归 E）。
> **与其他子类的差异**：D 关注"状态切换合法性+流转约束"——A 关注"业务结果"，F 关注"多玩家并发"。

---

## 1. 典型场景

### 场景 1：活动状态机
- 业务背景：限时活动
- 涉及状态：未开启 → 预热 → 进行中 → 即将结束 → 已结束 → 重置
- 触发动作：时间推进
- 验证点：状态按时间正确切换

### 场景 2：副本状态机
- 业务背景：PVE 副本
- 涉及状态：未进入 → 战斗中 → 胜利 / 失败 → 结算 → 退出
- 触发动作：进入副本、战斗结束
- 验证点：状态正确切换、副本次数扣减

### 场景 3：邮件状态机
- 业务背景：玩家邮件
- 涉及状态：未读 → 已读 → 领取 → 删除 / 过期
- 触发动作：查看邮件、领取附件
- 验证点：状态机单向流转

### 场景 4：礼包状态机
- 业务背景：节日礼包
- 涉及状态：可领取 → 已领 → 过期
- 触发动作：领取、过期
- 验证点：已领后不能再领

### 场景 5：玩家在线/离线
- 业务背景：玩家连接状态
- 涉及状态：在线 → 离线 → 重连
- 触发动作：断线、重连
- 验证点：状态机切换

### 场景 6：角色死亡/复活
- 业务背景：PVP / PVE 战斗
- 涉及状态：存活 → 濒死 → 死亡 → 复活
- 触发动作：HP=0、复活技能
- 验证点：死亡后不能攻击、复活后状态恢复

### 场景 7：技能冷却
- 业务背景：技能释放
- 涉及状态：可用 → 冷却中 → 可用
- 触发动作：释放技能、等冷却
- 验证点：冷却中不能再次释放

### 场景 8：Buff 叠加/刷新/过期
- 业务背景：战斗 Buff
- 涉及状态：未激活 → 激活中 → 过期 / 叠加 / 刷新
- 触发动作：施加 Buff、叠加同类 Buff
- 验证点：Buff 计时正确

### 场景 9：道具锁定/可交易/过期
- 业务背景：交易系统
- 涉及状态：锁定 → 可交易 → 交易中 → 已交易 / 过期
- 触发动作：交易流程
- 验证点：锁定期间不能重复操作

### 场景 10：非法状态跳转拦截
- 业务背景：未开启活动不能领奖
- 涉及状态：未开启
- 触发动作：尝试领奖
- 验证点：拦截 + 错误码

### 场景 11：状态切换触发配套业务
- 业务背景：活动结束清空临时道具
- 涉及状态：进行中 → 已结束
- 触发动作：活动结束
- 验证点：临时道具自动清理

### 场景 12：多状态并发兼容
- 业务背景：同时多个 Buff、多个限时活动
- 涉及状态：多状态叠加
- 触发动作：施加多个 Buff
- 验证点：状态互不干扰

---

## 2. 种子测试点（TP 模板）

### TP-001（BIZ_STATE_MACHINE）：活动未开启
- **scenario**：场景 1
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：活动 6/15 开启，当前 6/14
- **test_data**：`activity_enter(player_id, activity_id=1)`
- **expected**：拦截 + 错误码 `ACTIVITY_NOT_OPEN`、入口隐藏
- **notes**：注意"未开启"vs"已结束"

### TP-002（BIZ_STATE_MACHINE）：活动进行中
- **scenario**：场景 1
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：活动 6/15-6/30，当前 6/20
- **test_data**：`activity_enter(player_id, activity_id=1)`
- **expected**：进入活动、状态可操作
- **notes**：注意"进行中"vs"预热"vs"即将结束"

### TP-003（BIZ_STATE_MACHINE）：活动即将结束
- **scenario**：场景 1
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：活动结束前 1 小时
- **test_data**：`activity_enter(player_id, activity_id=1)`
- **expected**：进入活动、显示"即将结束"提示
- **notes**：注意"倒计时"vs"状态字段"

### TP-004（BIZ_STATE_MACHINE）：活动已结束
- **scenario**：场景 1
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：活动已结束
- **test_data**：`activity_enter(player_id, activity_id=1)`
- **expected**：拦截 + 错误码 `ACTIVITY_EXPIRED`、入口隐藏
- **notes**：注意"结束拦截"vs"已领奖玩家可查看记录"

### TP-005（BIZ_STATE_MACHINE）：活动重置
- **scenario**：场景 1
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：活动每周重置
- **test_data**：跨过周一 0 点
- **expected**：活动进度清空、状态重置为 未开启→进行中
- **notes**：注意"重置"vs"清空"vs"归档"

### TP-006（BIZ_STATE_MACHINE）：副本进入
- **scenario**：场景 2
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：副本可进入
- **test_data**：`dungeon_enter(player_id, dungeon_id=10)`
- **expected**：副本状态 未进入→战斗中
- **notes**：注意"前置条件"（体力/次数/等级）

### TP-007（BIZ_STATE_MACHINE）：副本胜利
- **scenario**：场景 2
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：副本中
- **test_data**：击杀最终 BOSS
- **expected**：副本状态 战斗中→胜利→结算
- **notes**：注意"胜利"vs"失败"+"状态切换条件"

### TP-008（BIZ_STATE_MACHINE）：副本失败
- **scenario**：场景 2
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：副本中
- **test_data**：玩家死亡
- **expected**：副本状态 战斗中→失败→结算、奖励按失败规则发放
- **notes**：注意"团灭"vs"单人失败"

### TP-009（BIZ_STATE_MACHINE）：副本退出
- **scenario**：场景 2
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：副本中
- **test_data**：玩家主动退出
- **expected**：副本状态 战斗中→退出、次数是否扣除看配置
- **notes**：注意"主动退出"vs"被踢出"vs"断线"

### TP-010（BIZ_STATE_MACHINE）：邮件未读
- **scenario**：场景 3
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：新邮件
- **test_data**：`mail_list(player_id)`
- **expected**：邮件状态 = 未读、加粗显示
- **notes**：注意"未读"vs"未领"vs"已读未领"

### TP-011（BIZ_STATE_MACHINE）：邮件已读
- **scenario**：场景 3
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：邮件未读
- **test_data**：`mail_read(player_id, mail_id)`
- **expected**：邮件状态 未读→已读
- **notes**：注意"查看"vs"打开详情"+"自动标记已读"

### TP-012（BIZ_STATE_MACHINE）：邮件领取
- **scenario**：场景 3
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：邮件未领
- **test_data**：`mail_claim(player_id, mail_id)`
- **expected**：邮件状态 已读→已领、附件发放
- **notes**：注意"部分领取"vs"全部领取"+"有附件"vs"无附件"

### TP-013（BIZ_STATE_MACHINE）：邮件过期
- **scenario**：场景 3
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：邮件 7 天有效期
- **test_data**：第 8 天查看
- **expected**：邮件状态 已读→过期、附件作废
- **notes**：注意"过期"vs"删除"+"未读邮件过期"

### TP-014（BIZ_STATE_MACHINE）：礼包可领取
- **scenario**：场景 4
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：玩家满足领取条件
- **test_data**：`gift_claim(player_id, gift_id)`
- **expected**：礼包状态 可领取→已领
- **notes**：注意"条件校验"+"条件不满足时不可见/不可点"

### TP-015（BIZ_STATE_MACHINE）：礼包已领后不可再领
- **scenario**：场景 4
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：礼包已领
- **test_data**：再次 `gift_claim`
- **expected**：拦截 + 错误码 `GIFT_CLAIMED`、按钮置灰
- **notes**：注意"幂等"vs"拦截"

### TP-016（BIZ_STATE_MACHINE）：礼包过期
- **scenario**：场景 4
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：礼包已过期
- **test_data**：`gift_claim`
- **expected**：拦截 + 错误码 `GIFT_EXPIRED`、入口隐藏
- **notes**：注意"过期"vs"未开启"

### TP-017（BIZ_STATE_MACHINE）：玩家在线转离线
- **scenario**：场景 5
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：玩家在线
- **test_data**：断线 30s
- **expected**：状态 在线→离线、推送停止
- **notes**：注意"心跳超时"vs"主动退出"

### TP-018（BIZ_STATE_MACHINE）：玩家离线转在线
- **scenario**：场景 5
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：玩家离线
- **test_data**：重连
- **expected**：状态 离线→在线、推送恢复
- **notes**：注意"重连"vs"重新登录"

### TP-019（BIZ_STATE_MACHINE）：角色死亡不可攻击
- **scenario**：场景 6
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：玩家 HP=0 死亡
- **test_data**：`attack(player_id)`
- **expected**：拦截 + 错误码 `STATE_DEAD`、技能栏置灰
- **notes**：注意"死亡"vs"濒死"+"无敌状态"

### TP-020（BIZ_STATE_MACHINE）：角色复活
- **scenario**：场景 6
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：玩家死亡
- **test_data**：`revive(player_id)`
- **expected**：状态 死亡→存活、HP 恢复、可操作
- **notes**：注意"复活"vs"原地复活"vs"回城复活"

### TP-021（BIZ_STATE_MACHINE）：技能冷却拦截
- **scenario**：场景 7
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：技能 5s 冷却，已释放
- **test_data**：`cast_skill(player_id, skill_id)` 1s 后
- **expected**：拦截 + 错误码 `SKILL_COOLDOWN`、按钮倒计时
- **notes**：注意"冷却中"vs"沉默中"vs"眩晕"

### TP-022（BIZ_STATE_MACHINE）：技能冷却结束
- **scenario**：场景 7
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：技能冷却 5s
- **test_data**：等 5s 后释放
- **expected**：状态 冷却中→可用
- **notes**：注意"前端倒计时"vs"服务端计时"

### TP-023（BIZ_STATE_MACHINE）：Buff 叠加
- **scenario**：场景 8
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：玩家已有攻击力 Buff +20
- **test_data**：再施加攻击力 Buff +20
- **expected**：根据配置叠加（+40 或刷新为 +20）
- **notes**：注意"叠加"vs"刷新"vs"取最高"vs"独立"

### TP-024（BIZ_STATE_MACHINE）：Buff 过期
- **scenario**：场景 8
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：Buff 持续 30s
- **test_data**：第 31 秒查看
- **expected**：Buff 状态 激活中→过期、属性回退
- **notes**：注意"过期"vs"被驱散"vs"被覆盖"

### TP-025（BIZ_STATE_MACHINE）：道具锁定
- **scenario**：场景 9
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：玩家发起交易、道具锁定
- **test_data**：玩家尝试重复使用道具
- **expected**：拦截 + 错误码 `ITEM_LOCKED`、道具置灰
- **notes**：注意"锁定"vs"使用中"

### TP-026（BIZ_STATE_MACHINE）：状态非法跳转拦截
- **scenario**：场景 10
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：活动未开启
- **test_data**：`activity_claim(player_id, activity_id=1)`
- **expected**：拦截 + 错误码 `ACTIVITY_NOT_OPEN`
- **notes**：注意"按状态机跳转"vs"按业务规则"

### TP-027（BIZ_STATE_MACHINE）：活动结束清理临时道具
- **scenario**：场景 11
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：活动进行中、玩家有"春日专属道具"
- **test_data**：活动结束
- **expected**：临时道具自动清理、清理日志
- **notes**：注意"临时"vs"永久"+"清理"vs"回收"

### TP-028（BIZ_STATE_MACHINE）：活动结束触发全服邮件
- **scenario**：场景 11
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：活动结束
- **test_data**：服务端切换活动状态
- **expected**：参与玩家收到"活动结束感谢"邮件
- **notes**：注意"参与"vs"未参与"

### TP-029（BIZ_STATE_MACHINE）：战斗中不能重置次数
- **scenario**：场景 10
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：副本中
- **test_data**：`reset_dungeon_count(player_id, dungeon_id=10)`
- **expected**：拦截 + 错误码 `IN_DUNGEON`
- **notes**：注意"战斗状态"vs"副本状态"

### TP-030（BIZ_STATE_MACHINE）：多 Buff 互不干扰
- **scenario**：场景 12
- **module**：`BIZ_STATE_MACHINE`
- **precondition**：玩家有攻击 +20 Buff 和防御 +30 Buff
- **test_data**：观察 30s
- **expected**：两个 Buff 独立计时、互不影响、到期各自清除
- **notes**：注意"独立"vs"互斥"vs"优先级"

---

## 3. 边界陷阱

### 边界 1：vs A. 业务
- **混淆点**：「活动"状态"」——A 测业务、D 测状态机
- **判定规则**：测"状态切换合法性" → D；测"业务结果" → A
- **实例**：活动状态 未开启→进行中 → D；活动结束清道具 → A

### 边界 2：vs F. 并发
- **混淆点**：「多状态"并发"」——D 测单对象状态、F 测多玩家
- **判定规则**：测"单玩家多状态叠加" → D；测"多玩家同时操作" → F
- **实例**：多 Buff 叠加 → D；100 玩家抢礼包 → F

### 边界 3：vs E. 数据库
- **混淆点**：「状态"持久化"」——D 测状态机、E 测 DB
- **判定规则**：测"状态切换规则" → D；测"DB 写入" → E
- **实例**：死亡状态机 → D；状态字段落库 → E

### 边界 4：vs CONFIG
- **混淆点**：「活动"配置"」——D 测状态机、CONFIG 测配置
- **判定规则**：测"状态字段值" → D；测"配置表字段" → CONFIG
- **实例**：活动开启时间字段 → CONFIG；活动开启后状态 → D

### 边界 5：vs G. 定时任务
- **混淆点**：「活动"结束"」——D 测状态机、G 测定时
- **判定规则**：测"结束状态" → D；测"定时器触发" → G
- **实例**：活动已结束拦截 → D；零点定时器 → G

---

## 4. 验证证据

### 视觉证据
- 活动倒计时显示截图
- 邮件状态图标截图（未读/已读/已领/过期）
- 礼包按钮置灰截图
- 技能冷却倒计时截图
- Buff 图标和剩余时间截图

### 日志证据
- `STATE_TRANSITION from=X to=Y reason=Z` 状态切换日志
- `STATE_INVALID_ATTEMPT` 非法状态操作日志
- `STATE_TRANSITION_TRIGGERED` 状态触发的配套业务日志
- `BUFF_ADD/REFRESH/EXPIRE` Buff 状态日志

### 数据证据
- 玩家状态表 `player.status, last_login_at, online`
- 副本状态表 `dungeon_run.status, enter_at, exit_at`
- 邮件状态表 `mail.status, read_at, claimed_at, expire_at`
- 礼包状态表 `gift_claim.status, claimed_at`
- Buff 状态表 `buff.player_id, buff_id, expire_at, stacks`
- 状态机历史记录表（状态切换流水）

### 性能证据
- 状态切换耗时 < 10ms
- 多状态查询（100 个 Buff）< 50ms
- 状态机驱动 cron 扫描 < 1s
