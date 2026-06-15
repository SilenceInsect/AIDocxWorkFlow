# P. LOG 游戏项目专项补充（仅游戏项目）

> **非测试类型**——本文件是**仅游戏项目**的 LOG 测试点补充。
> 非游戏项目（PC 后台、移动端 App、Web 工具）**忽略**本文件。
>
> **来源**：用户 LOG 细化定义 + 游戏项目高频日志场景

---

## 1. 战斗日志专项

> 业务背景：技能释放、伤害结算、战斗帧同步、死亡复活

### 场景
- 技能释放日志
- 伤害结算日志
- 战斗帧同步日志
- 死亡复活日志
- BOSS 战日志

### 种子 TP

#### TP-001（P-战斗）：技能释放日志
- **module**：`LOG_EVENT_TRACK`（A 子类）
- **precondition**：玩家释放技能
- **test_data**：`cast_skill(player_id, skill_id=1)`
- **expected**：埋点 `cast_skill` 含 skill_id、damage、target
- **notes**：注意"释放"vs"命中"+"技能等级"

#### TP-002（P-战斗）：暴击日志
- **module**：`LOG_EVENT_TRACK`
- **precondition**：暴击
- **test_data**：`crit_log(damage, crit_rate)`
- **expected`：埋点含 `crit=true`、`crit_damage`
- **notes**：注意"暴击"vs"暴伤"

#### TP-003（P-战斗）：战斗帧同步
- **module**：`LOG_MONITOR`（D 子类）
- **precondition**：PVP 4 人
- **test_data`：1 分钟战斗
- **expected`：埋点 `battle_frame fps=30 sync_delay=Xms`
- **notes**：注意"帧率"vs"延迟"+"丢包"

#### TP-004（P-战斗）：死亡日志
- **module**：`LOG_EVENT_TRACK`
- **precondition`：HP=0
- **test_data`：`player_death(player_id, killer)`
- **expected`：埋点 `death player_id killer cause`
- **notes**：注意"PVE 死亡"vs"PVP 死亡"

#### TP-005（P-战斗）：BOSS 战日志
- **module**：`LOG_OPERATION`（C 子类）
- **precondition`：世界 BOSS
- **test_data`：`boss_kill(boss_id, killer, damage_rank)`
- **expected`：操作日志含 boss_id、killer、伤害排名
- **notes**：注意"首杀"vs"末刀"

#### TP-006（P-战斗）：PVP 胜负日志
- **module**：`LOG_EVENT_TRACK`
- **precondition`：PVP
- **test_data`：`pvp_settle(A, B, result)`
- **expected`：埋点 `pvp winner loser score_change`
- **notes**：注意"胜"vs"平"vs"负"

#### TP-007（P-战斗）：战斗崩溃
- **module**：`LOG_CRASH_REPORT`（E 子类）
- **precondition**：战斗中崩溃
- **test_data`：观察
- **expected`：崩溃日志含 battle_id、role、frame
- **notes**：注意"战斗状态"+"复现"

#### TP-008（P-战斗）：战斗作弊检测
- **module**：`LOG_SECURITY`（J 子类）
- **precondition`：检测到脚本
- **test_data`：`cheat_detect(player_id, type=auto_skill)`
- **expected`：安全日志 `SECURITY type=cheat type=auto_skill`
- **notes**：注意"自动脚本"vs"外挂"

---

## 2. 社交日志专项

> 业务背景：好友、公会、组队、聊天

### 场景
- 好友互动日志
- 公会操作日志
- 组队日志
- 聊天日志

### 种子 TP

#### TP-009（P-社交）：好友添加日志
- **module**：`LOG_EVENT_TRACK`
- **precondition**：玩家加好友
- **test_data`：`add_friend(A, B)`
- **expected**：埋点 `add_friend player_id target source`
- **notes**：注意"添加"vs"接受"+"单向"vs"双向"

#### TP-010（P-社交）：好友赠送日志
- **module**：`LOG_ASSET_AUDIT`（B 子类）
- **precondition`：好友送体力
- **test_data`：`gift_stamina(A→B, count=20)`
- **expected`：资产流水双向 `A:-20 B:+20 source=friend`
- **notes**：注意"赠送"vs"交易"

#### TP-011（P-社交）：公会加入日志
- **module**：`LOG_OPERATION`
- **precondition`：玩家加入
- **test_data`：`guild_join(player_id, guild_id)`
- **expected`：操作日志 `OPERATION op=join_guild`
- **notes**：注意"申请"vs"加入"

#### TP-012（P-社交）：公会贡献日志
- **module**：`LOG_ASSET_AUDIT`
- **precondition`：玩家贡献
- **test_data`：`contribute(player_id, 100_diamond)`
- **expected`：资产流水 `-100 钻 +公会资金`
- **notes**：注意"个人"vs"公会"

#### TP-013（P-社交）：组队匹配日志
- **module**：`LOG_EVENT_TRACK`
- **precondition`：3 人匹配
- **test_data`：`match_team(player_ids)`
- **expected`：埋点 `match_team players count duration`
- **notes**：注意"匹配"+"耗时"

#### TP-014（P-社交）：组队邀请日志
- **module**：`LOG_EVENT_TRACK`
- **precondition`：玩家邀请
- **test_data`：`invite_team(A, B)`
- **expected`：埋点 `invite_team from to result`
- **notes**：注意"接受"vs"拒绝"+"超时"

#### TP-015（P-社交）：私聊日志
- **module**：`LOG_EVENT_TRACK`
- **precondition**：A 私聊 B
- **test_data`：`send_private_msg(A, B, content)`
- **expected`：埋点 `private_msg from to content_hash`
- **notes**：注意"内容脱敏"+"敏感词"

#### TP-016（P-社交）：世界聊天日志
- **module**：`LOG_EVENT_TRACK`
- **precondition`：世界聊天
- **test_data`：`send_world_msg(player_id, content)`
- **expected`：埋点含敏感词标记
- **notes**：注意"敏感词"+"违规模型"

---

## 3. 运营活动日志专项

> 业务背景：限时活动、签到、节日活动、排行榜、全服奖励

### 场景
- 限时活动日志
- 签到日志
- 排行榜日志
- 全服奖励日志
- 赛季结算日志

### 种子 TP

#### TP-017（P-活动）：活动开启日志
- **module**：`LOG_OPERATION`
- **precondition`：定时开启
- **test_data`：`cron_activity_open(activity_id=5)`
- **expected`：操作日志 `OPERATION op=activity_open activity_id`
- **notes**：注意"自动"vs"手动"

#### TP-018（P-活动）：活动关闭日志
- **module**：`LOG_OPERATION`
- **precondition`：活动结束
- **test_data`：`cron_activity_close(activity_id=5)`
- **expected`：操作日志含 affected_players
- **notes**：注意"结束"+"清临时道具"

#### TP-019（P-活动）：签到日志
- **module**：`LOG_ASSET_AUDIT`
- **precondition`：玩家签到
- **test_data`：`daily_signin(player_id, day)`
- **expected`：资产流水 `+100 钻 reason=signin day`
- **notes**：注意"连签"vs"断签"

#### TP-020（P-活动）：活动积分日志
- **module**：`LOG_EVENT_TRACK`
- **precondition`：玩家积分
- **test_data`：`add_score(player_id, 50)`
- **expected`：埋点 `add_score player_id score total`
- **notes**：注意"累加"vs"重置"

#### TP-021（P-活动）：排行榜作弊检测
- **module**：`LOG_SECURITY`
- **precondition`：1 分钟刷 1 万分
- **test_data`：风控扫描
- **expected`：安全日志 `SECURITY type=cheat_rank`
- **notes**：注意"实时"vs"事后"风控

#### TP-022（P-活动）：全服奖励发放
- **module**：`LOG_ASSET_AUDIT`
- **precondition`：10 万玩家
- **test_data`：`gm_batch_reward(100000, 100_diamond)`
- **expected**：资产流水 10 万条、batch_id 一致
- **notes**：注意"批量"+"幂等"

#### TP-023（P-活动）：赛季结算日志
- **module**：`LOG_OPERATION`
- **precondition`：赛季结束
- **test_data`：`cron_season_settle(season_id)`
- **expected`：操作日志含 season_id、player_count
- **notes**：注意"归档"+"清空"

#### TP-024（P-活动）：赛季奖励发放
- **module**：`LOG_ASSET_AUDIT`
- **precondition`：玩家黄金段位
- **test_data`：`season_reward(player_id, rank)`
- **expected`：资产流水 `+道具 rank=gold`
- **notes**：注意"按段位"vs"按排名"

---

## 4. 兜底回滚日志专项

> 业务背景：充值退款、操作回档、误操作补偿

### 场景
- 充值退款日志
- 操作回档日志
- 误操作补偿日志
- 强制回收日志

### 种子 TP

#### TP-025（P-回滚）：退款反向日志
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家已买
- **test_data`：`refund(order_id)`
- **expected`：资产流水 `-道具 -钻 order_id +refund_id`
- **notes**：注意"正向"vs"反向"+"链路"

#### TP-026（P-回滚）：操作回档日志
- **module**：`LOG_OPERATION`
- **precondition`：运营回档
- **test_data`：`data_reset(time=1hour_ago, affected=1000)`
- **expected`：操作日志 `OPERATION op=reset time affected`
- **notes**：注意"回档"vs"回滚"

#### TP-027（P-回滚）：回档补偿日志
- **module**：`LOG_ASSET_AUDIT`
- **precondition`：1000 玩家补偿
- **test_data`：`compensation(1000, 100_diamond)`
- **expected`：资产流水 batch_id 一致
- **notes**：注意"补偿"vs"补发"

#### TP-028（P-回滚）：误操作补偿
- **module**：`LOG_OPERATION`
- **precondition**：玩家误卖
- **test_data`：客服补偿
- **expected`：操作日志 `OPERATION op=compensation op_id=CS001`
- **notes**：注意"客服"vs"自动"

#### TP-029（P-回滚）：GM 强制回收
- **module**：`LOG_ASSET_AUDIT`
- **precondition`：非法所得
- **test_data`：`gm_reclaim(player_id, item, reason=cheat)`
- **expected`：资产流水 `-道具 op_id reason`
- **notes**：注意"强制"vs"业务"+"审计"

#### TP-030（P-回滚）：活动异常补偿
- **module**：`LOG_ASSET_AUDIT`
- **precondition`：活动异常关闭
- **test_data`：批量补偿
- **expected`：资产流水 `+补偿 reason=activity_bug`
- **notes**：注意"已参与"vs"未参与"

#### TP-031（P-回滚）：退款链可追溯
- **module**：`LOG_INTEGRITY`（G 子类）
- **precondition`：退款
- **test_data`：观察日志
- **expected`：refund_id 反向关联 purchase_id、trace_id 一致
- **notes**：注意"链路"+"可追溯"

#### TP-032（P-回滚）：删号恢复
- **module**：`LOG_TRACE`（I 子类）
- **precondition`：玩家删号
- **test_data`：`restore_account(player_id)`
- **expected`：历史日志保留 30 天
- **notes**：注意"软删"vs"硬删"

---

## 5. 边界陷阱

### 边界 1：vs A. 行为埋点
- **混淆点**：「战斗"埋点"」——A 测通用、P 测游戏
- **判定规则**：测"通用行为埋点" → A；测"游戏专项" → P
- **实例**：登录埋点 → A；战斗技能 → P-001

### 边界 2：vs B. 资产审计
- **混淆点**：「战斗"流水"」——B 测通用、P 测游戏
- **判定规则**：测"通用资产审计" → B；测"游戏专项" → P
- **实例**：通用资产 → B；战斗伤害 → P-001

### 边界 3：vs C. 操作日志
- **混淆点**：「活动"操作"」——C 测通用、P 测游戏
- **判定规则**：测"通用操作" → C；测"游戏专项" → P
- **实例**：通用 GM 操作 → C；BOSS 击杀 → P-005

### 边界 4：vs E. 崩溃
- **混淆点**：「崩溃"日志"」——E 测通用、P 测游戏
- **判定规则**：测"通用崩溃日志" → E；测"游戏专项" → P
- **实例**：通用崩溃 → E；战斗中崩溃 → P-007

### 边界 5：vs J. 安全
- **混淆点**：「游戏"反作弊"」——J 测通用、P 测游戏
- **判定规则**：测"通用安全日志" → J；测"游戏专项" → P
- **实例**：参数篡改 → J；自动脚本 → P-008

---

## 6. 验证证据

### 视觉证据
- 战斗日志查询截图
- 社交日志分析截图
- 活动日志报表截图
- 退款链路截图

### 日志证据
- `cast_skill/crit/death/pvp/boss_kill` 战斗日志
- `add_friend/guild_join/team_match/private_msg` 社交日志
- `activity_open/signin/season_settle` 活动日志
- `refund/data_reset/compensation/gm_reclaim` 回滚日志

### 数据证据
- 战斗日志表 `battle_log.player_id, skill_id, damage, time`
- 社交日志表 `social_log.player_id, target, action, time`
- 活动日志表 `activity_log.player_id, activity_id, score, time`
- 回滚日志表 `rollback_log.op_id, type, affected, time`
- 退款链路表 `refund_id → purchase_id` 关联
- 全服奖励 batch_id 完整

### 性能证据
- 战斗日志 < 5ms
- 社交日志 < 5ms
- 活动日志 < 5ms
- 回滚链路查询 < 1s
- 战斗作弊检测 < 1s
