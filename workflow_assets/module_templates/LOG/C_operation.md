# C. 全量业务操作日志

> **子类代码**：`LOG_OPERATION`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §3「全量业务操作日志（后台/GM/运营审计）」
>
> **测什么**：玩家操作日志（领奖/限购/竞技/拍卖/公会/邮件）、GM/运营后台日志（批量发奖/封号/重置/回档/配置/白名单）、系统定时任务日志（零点/定时邮件/活动/排行榜/清理）、权限操作日志（管理员/高危/二次确认）。
> **不测什么**：业务逻辑（归 BIZ）、埋点业务触发（归 A）、资产流水（归 B）、审计对账（归 BIZ-I）、日志底层 SDK（归 AUX）。
> **与其他子类的差异**：C 关注"**操作行为**留痕"——A 关注"行为埋点触发"，B 关注"资产流水"，D 关注"服务指标"，J 关注"安全反作弊留痕"。

---

## 1. 典型场景

### 场景 1：玩家领奖
- 业务背景：领取任务奖励
- 涉及行为：玩家领奖
- 触发动作：`task_claim`
- 验证点：操作日志含 task_id、奖励

### 场景 2：玩家限购
- 业务背景：玩家买限购商品
- 涉及行为：限购扣减
- 触发动作：`purchase_limited`
- 验证点：操作日志含商品 ID、剩余次数

### 场景 3：玩家竞技
- 业务背景：PVP 战斗
- 涉及行为：竞技
- 触发动作：`pvp_settle`
- 验证点：操作日志含对手、胜负

### 场景 4：拍卖行操作
- 业务背景：玩家竞拍
- 涉及行为：出价
- 触发动作：`auction_bid`
- 验证点：操作日志含物品、金额

### 场景 5：公会操作
- 业务背景：玩家加入公会
- 涉及行为：公会加入
- 触发动作：`guild_join`
- 验证点：操作日志含 guild_id

### 场景 6：邮件收发
- 业务背景：玩家发邮件
- 涉及行为：邮件发送
- 触发动作：`mail_send`
- 验证点：操作日志含收件人、内容

### 场景 7：GM 批量发奖
- 业务背景：GM 给 1000 玩家发奖
- 涉及行为：GM 操作
- 触发动作：`gm_reward`
- 验证点：操作日志含 op_id、玩家列表

### 场景 8：GM 封号
- 业务背景：违规玩家封号
- 涉及行为：封号
- 触发动作：`gm_ban`
- 验证点：操作日志含 reason、duration

### 场景 9：数据重置
- 业务背景：服务器回档
- 涉及行为：数据重置
- 触发动作：`data_reset`
- 验证点：操作日志含 affected_count

### 场景 10：回档补偿
- 业务背景：回档后批量补偿
- 涉及行为：补偿
- 触发动作：`compensation`
- 验证点：操作日志含 batch_id

### 场景 11：配置修改
- 业务背景：运营修改活动配置
- 涉及行为：配置变更
- 触发动作：`config_update`
- 验证点：操作日志含 before/after

### 场景 12：白名单操作
- 业务背景：添加白名单玩家
- 涉及行为：白名单
- 触发动作：`whitelist_add`
- 验证点：操作日志含 player_id

### 场景 13：零点重置
- 业务背景：日常任务零点
- 涉及行为：定时任务
- 触发动作：定时器
- 验证点：操作日志含 task=reset_daily

### 场景 14：定时邮件
- 业务背景：生日祝福邮件
- 涉及行为：定时邮件
- 触发动作：定时器
- 验证点：操作日志含 recipients

### 场景 15：活动开关
- 业务背景：活动自动开启
- 涉及行为：活动状态
- 触发动作：定时器
- 验证点：操作日志含 activity_id

### 场景 16：排行榜结算
- 业务背景：赛季结算
- 涉及行为：排行榜
- 触发动作：定时器
- 验证点：操作日志含 season_id

### 场景 17：资源清理
- 业务背景：过期道具清理
- 涉及行为：定时清理
- 触发动作：定时器
- 验证点：操作日志含 cleaned_count

### 场景 18：管理员登录
- 业务背景：管理员登录后台
- 涉及行为：登录
- 触发动作：`admin_login`
- 验证点：操作日志含 admin_id、ip

### 场景 19：高危操作
- 业务背景：管理员删玩家数据
- 涉及行为：高危操作
- 触发动作：`danger_op`
- 验证点：操作日志含二次确认

### 场景 20：二次确认
- 业务背景：高危操作前确认
- 涉及行为：确认
- 触发动作：`confirm`
- 验证点：操作日志含 confirm_by

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_OPERATION）：玩家领奖
- **scenario**：场景 1
- **module**：`LOG_OPERATION`
- **precondition**：玩家日常任务可领
- **test_data**：`task_claim(player_id, task_id=t001)`
- **expected**：操作日志 `OPERATION op=task_claim player_id task_id reward`
- **notes**：注意"玩家操作"vs"系统发放"

### TP-002（LOG_OPERATION）：限购扣减
- **scenario**：场景 2
- **module**：`LOG_OPERATION`
- **precondition**：商品限购 2 次、已购 1 次
- **test_data**：`purchase_limited(item=i001)`
- **expected**：操作日志 `OPERATION op=purchase item_id limit_used=2`
- **notes**：注意"限购"vs"限量"

### TP-003（LOG_OPERATION）：PVP 结算
- **scenario**：场景 3
- **module**：`LOG_OPERATION`
- **precondition**：玩家 A vs B
- **test_data**：`pvp_settle(A, B, result=A_win)`
- **expected**：操作日志 `OPERATION op=pvp winner=A loser=B`
- **notes**：注意"胜负"vs"平局"+"段位"

### TP-004（LOG_OPERATION）：拍卖出价
- **scenario**：场景 4
- **module**：`LOG_OPERATION`
- **precondition**：玩家出价
- **test_data**：`auction_bid(player_id, item_id, price=100)`
- **expected**：操作日志 `OPERATION op=bid player_id item_id price`
- **notes**：注意"出价"vs"中标"

### TP-005（LOG_OPERATION）：加入公会
- **scenario**：场景 5
- **module**：`LOG_OPERATION`
- **precondition**：玩家申请加入
- **test_data**：`guild_join(player_id, guild_id=g001)`
- **expected**：操作日志 `OPERATION op=join_guild player_id guild_id`
- **notes**：注意"申请"vs"加入"+"通过"

### TP-006（LOG_OPERATION）：邮件发送
- **scenario**：场景 6
- **module**：`LOG_OPERATION`
- **precondition**：玩家发邮件
- **test_data**：`mail_send(from=A, to=B, content=xxx)`
- **expected**：操作日志 `OPERATION op=mail from to content_hash`
- **notes**：注意"内容"+"敏感词"+"脱敏"

### TP-007（LOG_OPERATION）：GM 批量发奖
- **scenario**：场景 7
- **module**：`LOG_OPERATION`
- **precondition**：GM 给 1000 玩家发奖
- **test_data**：`gm_reward(1000_players, 100_diamond, op_id=GM001)`
- **expected**：操作日志 `OPERATION op=gm_reward op_id=GM001 count=1000 batch_id=xxx`
- **notes**：注意"批量"+"审计"+"可追溯"

### TP-008（LOG_OPERATION）：GM 封号
- **scenario**：场景 8
- **module**：`LOG_OPERATION`
- **precondition**：玩家违规
- **test_data**：`gm_ban(player_id, reason=cheat, duration=7day, op_id=GM001)`
- **expected**：操作日志 `OPERATION op=ban player_id reason duration op_id`
- **notes**：注意"封号"vs"禁言"+"永久"vs"临时"

### TP-009（LOG_OPERATION）：数据回档
- **scenario**：场景 9
- **module**：`LOG_OPERATION`
- **precondition**：运营回档
- **test_data**：`data_reset(time=1hour_ago, affected=1000, op_id=OP001)`
- **expected**：操作日志 `OPERATION op=reset time affected op_id`
- **notes**：注意"回档"vs"回滚"+"影响范围"

### TP-010（LOG_OPERATION）：回档补偿
- **scenario**：场景 10
- **module**：`LOG_OPERATION`
- **precondition**：回档影响 1000 玩家
- **test_data**：`compensation(batch_id=c001, 1000_players, 100_diamond)`
- **expected**：操作日志 `OPERATION op=compensation batch_id count`
- **notes**：注意"补偿"vs"补发"+"审计"

### TP-011（LOG_OPERATION）：配置修改
- **scenario**：场景 11
- **module**：`LOG_OPERATION`
- **precondition**：运营改活动配置
- **test_data**：`config_update(config=activity_5, key=reward, before=100, after=200, op_id=OP001)`
- **expected**：操作日志 `OPERATION op=config_update key before after op_id`
- **notes**：注意"配置"审计链路

### TP-012（LOG_OPERATION）：白名单添加
- **scenario**：场景 12
- **module**：`LOG_OPERATION`
- **precondition**：运营加白名单
- **test_data**：`whitelist_add(player_id, feature=new_func, op_id=OP001)`
- **expected**：操作日志 `OPERATION op=whitelist player_id feature op_id`
- **notes**：注意"白名单"vs"灰度"

### TP-013（LOG_OPERATION）：零点重置
- **scenario**：场景 13
- **module**：`LOG_OPERATION`
- **precondition**：定时器
- **test_data**：`cron(reset_daily, 00:00)`
- **expected**：操作日志 `OPERATION op=cron task=reset_daily time`
- **notes**：注意"定时"vs"手动"

### TP-014（LOG_OPERATION）：定时邮件
- **scenario**：场景 14
- **module**：`LOG_OPERATION`
- **precondition**：生日祝福
- **test_data**：`cron(birthday_mail, 00:00)`
- **expected**：操作日志 `OPERATION op=cron_mail task=birthday count=N`
- **notes**：注意"全员"vs"指定"

### TP-015（LOG_OPERATION）：活动自动开启
- **scenario**：场景 15
- **module**：`LOG_OPERATION`
- **precondition**：定时器
- **test_data**：`cron(activity_open, 2026-06-15 00:00, activity_id=5)`
- **expected**：操作日志 `OPERATION op=cron_activity activity_id status=open`
- **notes**：注意"自动"vs"手动"开启

### TP-016（LOG_OPERATION）：赛季结算
- **scenario**：场景 16
- **module**：`LOG_OPERATION`
- **precondition**：赛季结束
- **test_data**：`cron(season_settle, season_id=s001)`
- **expected**：操作日志 `OPERATION op=season_settle season_id`
- **notes**：注意"结算"+"归档"

### TP-017（LOG_OPERATION）：过期清理
- **scenario**：场景 17
- **module**：`LOG_OPERATION`
- **precondition**：定时清理
- **test_data**：`cron(clean_expired)`
- **expected**：操作日志 `OPERATION op=clean count=N`
- **notes**：注意"清理"vs"回收"

### TP-018（LOG_OPERATION）：管理员登录
- **scenario**：场景 18
- **module**：`LOG_OPERATION`
- **precondition**：管理员登录后台
- **test_data**：`admin_login(admin_id=A001, ip=10.0.0.1)`
- **expected**：操作日志 `OPERATION op=login admin_id ip time`
- **notes**：注意"成功"vs"失败"+"异地"

### TP-019（LOG_OPERATION）：高危操作
- **scenario**：场景 19
- **module**：`LOG_OPERATION`
- **precondition**：管理员删玩家数据
- **test_data**：`danger_op(op=delete_player, target=xxx, op_id=A001)`
- **expected**：操作日志 `OPERATION op=danger op target op_id confirm_by=A001`
- **notes**：注意"高危"清单+"二次确认"

### TP-020（LOG_OPERATION）：二次确认记录
- **scenario**：场景 20
- **module**：`LOG_OPERATION`
- **precondition**：高危操作前
- **test_data**：`confirm(op=delete_player, confirm_by=A001, confirm_at=xxx)`
- **expected`：操作日志 `OPERATION op=confirm op confirm_by confirm_at`
- **notes**：注意"二次确认"vs"单人操作"

### TP-021（LOG_OPERATION）：管理员登出
- **scenario**：场景 18
- **module**：`LOG_OPERATION`
- **precondition**：管理员已登录
- **test_data**：`admin_logout(admin_id=A001)`
- **expected**：操作日志 `OPERATION op=logout admin_id time duration`
- **notes**：注意"主动"vs"超时"vs"踢出"

### TP-022（LOG_OPERATION）：定时任务失败
- **scenario**：场景 13
- **module**：`LOG_OPERATION`
- **precondition**：定时任务执行失败
- **test_data**：观察日志
- **expected**：操作日志 `OPERATION op=cron status=fail reason`
- **notes**：注意"失败"vs"重试"

### TP-023（LOG_OPERATION）：管理员操作 IP 记录
- **scenario**：场景 18
- **module**：`LOG_OPERATION`
- **precondition**：管理员操作
- **test_data**：`admin_op(op=ban, op_id=A001, ip=10.0.0.1)`
- **expected`：操作日志含 ip
- **notes**：注意"异地"+"风控"

### TP-024（LOG_OPERATION）：权限升级审计
- **scenario**：场景 19
- **module**：`LOG_OPERATION`
- **precondition**：管理员权限提升
- **test_data**：`permission_upgrade(admin=A001, from=normal, to=admin)`
- **expected`：操作日志 `OPERATION op=permission from to op_id`
- **notes**：注意"权限"审计

### TP-025（LOG_OPERATION）：定时任务批量
- **scenario**：场景 16
- **module**：`LOG_OPERATION`
- **precondition**：0 点 100 个任务
- **test_data`：观察日志
- **expected**：100 个 OPERATION 日志、独立 ID
- **notes**：注意"批量"独立日志

### TP-026（LOG_OPERATION）：全量操作覆盖率
- **scenario**：场景 13
- **module**：`LOG_OPERATION`
- **precondition**：1 天业务 100 万笔
- **test_data`：操作日志覆盖率
- **expected`：100% 业务有操作日志
- **notes**：注意"覆盖率"+"审计"

### TP-027（LOG_OPERATION）：玩家自助查询
- **scenario**：场景 1
- **module**：`LOG_OPERATION`
- **precondition`：玩家查自己 30 天操作
- **test_data`：`query_ops(player_id, 30day)`
- **expected`：返回所有玩家操作日志
- **notes**：注意"玩家可见"vs"管理员可见"+"脱敏"

### TP-028（LOG_OPERATION）：操作日志不可篡改
- **scenario**：场景 19
- **module**：`LOG_OPERATION`
- **precondition`：操作日志已写入
- **test_data`：尝试改日志
- **expected`：拦截 + 写告警
- **notes**：注意"软删"vs"硬删"+"只追加"

### TP-029（LOG_OPERATION）：高危操作熔断
- **scenario**：场景 19
- **module**：`LOG_OPERATION`
- **precondition`：1 分钟 10 次高危操作
- **test_data`：观察
- **expected`：熔断 + 告警
- **notes**：注意"高频"+"风控"

### TP-030（LOG_OPERATION）：操作日志检索
- **scenario**：场景 1
- **module**：`LOG_OPERATION`
- **precondition**：1 亿条日志
- **test_data`：按 player_id + 时间范围查询
- **expected`：< 1s 返回
- **notes**：注意"索引"+"分页"

---

## 3. 边界陷阱

### 边界 1：vs A. 行为埋点
- **混淆点**：「购买"操作"」——A 测行为触发、C 测操作留痕
- **判定规则**：测"埋点触发" → A；测"操作留痕完整性" → C
- **实例**：购买埋点 → A；购买操作日志 → C

### 边界 2：vs B. 资产流水
- **混淆点**：「购买"流水"」——B 测资产、C 测操作
- **判定规则**：测"资产变动" → B；测"操作行为" → C
- **实例**：购买扣款流水 → B；购买操作日志 → C-001

### 边界 3：vs BIZ-I. 业务审计
- **混淆点**：「操作"审计"」——C 测操作、BIZ-I 测业务侧落点
- **判定规则**：测"操作日志完整性" → C；测"业务审计链" → BIZ-I
- **实例**：操作日志覆盖 → C；业务审计 → BIZ-I

### 边界 4：vs J. 安全日志
- **混淆点**：「违规"日志"」——C 测操作、J 测安全
- **判定规则**：测"操作留痕" → C；测"安全拦截" → J
- **实例**：GM 封号操作 → C；作弊检测 → J

### 边界 5：vs D. 监控
- **混淆点**：「操作"指标"」——C 测单点、D 测聚合
- **判定规则**：测"单次操作日志" → C；测"操作聚合指标" → D
- **实例**：领奖操作 → C；领奖率统计 → D

---

## 4. 验证证据

### 视觉证据
- 后台操作日志查询截图
- 高危操作确认弹窗截图

### 日志证据
- `OPERATION op=xxx player_id/admin_id target payload time op_id`
- `CRON task=xxx status=success/fail time`
- `DANGER_OP op=xxx confirm_by time`
- `PERMISSION_UPGRADE from to time op_id`

### 数据证据
- 操作日志表 `op_log.op_id, type, player_id, target, op_id, time`
- 定时任务表 `cron_log.task_id, status, time, duration`
- 高危操作白名单 + 二次确认记录
- 操作日志覆盖率 = 100%
- 操作日志不可篡改（仅追加）

### 性能证据
- 单次操作日志 < 5ms
- 操作日志查询 < 100ms（按 player_id 1 天）
- 高危操作熔断延迟 < 100ms
- 1 亿条操作日志分页 < 1s
