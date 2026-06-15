# E. 宕机 / 回档 / 并发极限 / 高危风控

> **子类代码**：`SERVER_HA_RISK`
> **归属模块**：`SPECIAL`
> **来源**：用户细化定义 §5「宕机、回档、高并发极限、高危操作风控」
>
> **测什么**：逻辑服/充值服**宕机**、数据库**抖动**、分库分表读写失败、热更服务**崩溃**；**宕机未落地事务回滚**、重启后**补偿未发放奖励**、**回档资源回收/补发**；**全服批量发奖**、**万人同活动**、**拍卖行并发竞价**、多人争夺有限资源的**分布式锁 + 事务隔离**、**无超发/无重复领取/无数据错乱**；**批量删除道具**、**清零货币**、**重置角色**、**批量封号**、**大额资源发放**、**跨服数据重置**的**二次确认 + 操作日志留痕 + 灰度执行 + 可回滚机制 + 权限分级拦截**。
> **不测什么**：通用业务流程（归 BIZ）、底层 HA 集群（归 AUX）、性能监控（归 AUX K）。
> **与其他子类的差异**：E 关注"服务端 + 高危操作"——A/B/C/D 都是客户端/单次操作；E 是服务端 HA + 高危 + 并发极限，是 SPECIAL 中最严重的"运营级"异常。

---

## 1. 典型场景

### 场景 1：逻辑服宕机
- 业务背景：游戏逻辑服崩溃
- 涉及字段/工具：server_health、failover
- 触发动作：服务器崩溃
- 验证点：客户端重连备用服 + 未落地事务回滚

### 场景 2：充值服宕机
- 业务背景：玩家支付时充值服无响应
- 涉及字段/工具：payment_server、retry_queue
- 触发动作：发起支付
- 验证点：订单进入重试队列 + 不重复扣款

### 场景 3：数据库抖动
- 业务背景：DB 主从切换，读写慢
- 涉及字段/工具：db_health、query_timeout
- 触发动作：玩家操作
- 验证点：读写超时后重试 + 业务降级

### 场景 4：分库分表读写失败
- 业务背景：某分片 DB 不可用
- 涉及字段/工具：shard_status、failover_read
- 触发动作：玩家读写
- 验证点：路由到备用分片 + 业务不中断

### 场景 5：热更服务崩溃
- 业务背景：热更中途服务崩溃
- 涉及字段/工具：hotupdate_status、rollback
- 触发动作：热更执行中
- 验证点：回滚到上一版本 + 玩家无感知

### 场景 6：宕机未落地事务回滚
- 业务背景：事务执行中服务器宕机
- 涉及字段/工具：transaction_log、recovery
- 触发动作：宕机
- 验证点：重启后未提交事务回滚，玩家数据一致

### 场景 7：重启后补偿未发放奖励
- 业务背景：宕机期间有未发放奖励
- 涉及字段/工具：pending_reward、compensation_task
- 触发动作：服务器重启
- 验证点：定时任务扫描 + 补偿发放

### 场景 8：版本回档资源回收
- 业务背景：版本回退到上一版本
- 涉及字段/工具：version_rollback、resource_reclaim
- 触发动作：运营决定回档
- 验证点：新版本发放的资源回收 + 旧版本玩家无感知

### 场景 9：版本回档资源补发
- 业务背景：版本回退后玩家已消耗的资源
- 涉及字段/工具：version_rollback、resource_compensate
- 触发动作：回档完成
- 验证点：玩家已消耗的道具按规则补发

### 场景 10：全服批量发奖
- 业务背景：节日活动全服 1000 万玩家发奖
- 涉及字段/工具：batch_reward、distributed_task
- 触发动作：运营触发
- 验证点：分布式任务分片执行 + 全员到账 + 无重复

### 场景 11：万人同活动
- 业务背景：限时活动 1min 内 10 万人参与
- 涉及字段/工具：concurrent_users、queue
- 触发动作：活动开启
- 验证点：队列/限流保护 + 业务不卡死

### 场景 12：拍卖行并发竞价
- 业务背景：1 个商品 1000 人同时出价
- 涉及字段/工具：auction_lock、bid_order
- 触发动作：并发出价
- 验证点：分布式锁 + 按出价时间/价格排序 + 无超卖

### 场景 13：批量删除道具
- 业务背景：运营删除某违规道具
- 涉及字段/工具：bulk_delete、confirmation
- 触发动作：运营执行
- **expected**：二次确认 + 灰度执行 + 可回滚 + 操作日志

### 场景 14：清零货币
- 业务背景：封号时清零玩家货币
- 涉及字段/工具：clear_currency、permission
- 触发动作：GM 执行
- **expected**：权限分级（高级 GM）+ 二次确认 + 日志留痕

### 场景 15：重置角色
- 业务背景：玩家申请重置角色
- 涉及字段/工具：character_reset、backup
- 触发动作：玩家触发
- **expected**：二次确认 + 备份 + 可回滚 + 7 天恢复期

### 场景 16：批量封号
- 业务背景：检测到批量作弊需封禁
- 涉及字段/工具：bulk_ban、gray_release
- 触发动作：风控系统触发
- **expected**：灰度封禁（先 10%）+ 观察 + 全量 + 可解封

### 场景 17：大额资源发放
- 业务背景：发放 1000 钻石给 VIP
- 涉及字段/工具：large_reward、limit_check
- 触发动作：GM 触发
- **expected**：单笔上限拦截 + 二次确认 + 日志 + 灰度

### 场景 18：跨服数据重置
- 业务背景：跨服赛季重置
- 涉及字段/工具：cross_server_reset、sync
- 触发动作：赛季结束
- **expected**：各服同步重置 + 玩家可登录查看 + 无错乱

---

## 2. 种子测试点（TP 模板）

### TP-001（SERVER_HA_RISK）：逻辑服宕机 Failover
- **scenario**：场景 1
- **module**：`SERVER_HA_RISK`
- **precondition**：玩家在副本中
- **test_data**：kill 逻辑服进程
- **expected**：客户端重连备用服 + 玩家副本数据从备用服拉取；未落地事务回滚
- **notes**：注意"主备" vs "集群"——主备是简单 failover

### TP-002（SERVER_HA_RISK）：充值服宕机重试
- **scenario**：场景 2
- **module**：`SERVER_HA_RISK`
- **precondition**：玩家发起支付
- **test_data**：支付中途充值服宕机
- **expected**：订单进入重试队列；客户端提示"支付处理中"；不重复扣款
- **notes**：注意"充值服" vs "支付渠道"——前者是游戏侧

### TP-003（SERVER_HA_RISK）：DB 抖动超时重试
- **scenario**：场景 3
- **module**：`SERVER_HA_RISK`
- **precondition**：DB 主从切换中
- **test_data**：玩家发起购买
- **expected**：读写超时后重试 3 次 + 失败后业务降级（提示稍后重试）
- **notes**：注意"重试" vs "熔断"——重试是短期，熔断是长期

### TP-004（SERVER_HA_RISK）：分片故障路由
- **scenario**：场景 4
- **module**：`SERVER_HA_RISK`
- **precondition**：某分片 DB 不可用
- **test_data**：玩家读写故障分片数据
- **expected**：路由到备用分片 + 业务不中断；故障分片恢复后数据同步
- **notes**：注意"分片" vs "主从"——分片是水平拆分

### TP-005（SERVER_HA_RISK）：热更崩溃回滚
- **scenario**：场景 5
- **module**：`SERVER_HA_RISK`
- **precondition**：热更执行中
- **test_data**：热更服务崩溃
- **expected**：回滚到上一版本 + 玩家无感知（仍在旧版本）
- **notes**：注意"热更" vs "版本更新"——热更是补丁

### TP-006（SERVER_HA_RISK）：宕机事务回滚
- **scenario**：场景 6
- **module**：`SERVER_HA_RISK`
- **precondition**：事务执行中（玩家购买商品 + 扣款 + 发货）
- **test_data**：扣款成功后发货前宕机
- **expected**：重启后事务回滚（玩家金币恢复）+ 玩家无感知
- **notes**：注意"事务" vs "补偿"——事务保证 ACID

### TP-007（SERVER_HA_RISK）：宕机后补偿发奖
- **scenario**：场景 7
- **module**：`SERVER_HA_RISK`
- **precondition**：宕机期间有 1000 个玩家未发放奖励
- **test_data**：服务器重启
- **expected**：补偿任务扫描 + 1000 玩家全部到账 + 幂等（不重复）
- **notes**：注意"补偿" vs "实时"——补偿是异步补救

### TP-008（SERVER_HA_RISK）：回档资源回收
- **scenario**：场景 8
- **module**：`SERVER_HA_RISK`
- **precondition**：版本 V2 发放了新道具"V2 限定"，现回退到 V1
- **test_data**：运营决定回档
- **expected**：所有玩家的 V2 限定道具回收（玩家背包减少）；日志留痕
- **notes**：注意"回收" vs "保留"——按业务规则决定

### TP-009（SERVER_HA_RISK）：回档资源补发
- **scenario**：场景 9
- **module**：`SERVER_HA_RISK`
- **precondition**：回档后玩家已消耗 V1 道具
- **test_data**：回档完成
- **expected**：按规则补发玩家已消耗的 V1 道具（若该道具在 V1 已存在）
- **notes**：注意"补发" vs "不补发"——按业务规则

### TP-010（SERVER_HA_RISK）：全服发奖分布式
- **scenario**：场景 10
- **module**：`SERVER_HA_RISK`
- **precondition**：1000 万玩家待发奖
- **test_data**：运营触发批量发奖
- **expected**：分片执行（10 个 worker 每个 100 万）+ 30min 完成 + 0 重复
- **notes**：注意"分片" vs "单点"——单点会卡死

### TP-011（SERVER_HA_RISK）：万人并发队列
- **scenario**：场景 11
- **module**：`SERVER_HA_RISK`
- **precondition**：活动开启 1min 内 10 万人进入
- **test_data**：10 万并发 enter_event 请求
- **expected**：队列保护（活动容量 1 万）+ 超出排队 + 业务不卡死
- **notes**：注意"容量" vs "无限"——活动有容量上限

### TP-012（SERVER_HA_RISK）：拍卖行并发分布式锁
- **scenario**：场景 12
- **module**：`SERVER_HA_RISK`
- **precondition**：1 件商品 1000 人同时出价
- **test_data**：1000 个并发 bid
- **expected**：Redis 分布式锁 + 按出价时间/价格排序 + 仅 1 人成交 + 无超卖
- **notes**：注意"分布式锁" vs "进程锁"——多服需分布式锁

### TP-013（SERVER_HA_RISK）：批量删除二次确认
- **scenario**：场景 13
- **module**：`SERVER_HA_RISK`
- **precondition**：运营需删除违规道具
- **test_data**：执行 bulk_delete(item_id=违规)
- **expected**：二次确认（输入"确认删除"）+ 灰度（先删 10% 玩家）+ 可回滚
- **notes**：注意"灰度" vs "全量"——灰度更安全

### TP-014（SERVER_HA_RISK）：清零货币权限分级
- **scenario**：场景 14
- **module**：`SERVER_HA_RISK`
- **precondition**：普通 GM 执行 clear_currency
- **test_data**：尝试清零玩家 10000 钻石
- **expected**：权限不足拦截（需高级 GM）+ 拒绝 + 日志
- **notes**：注意"权限" vs "二次确认"——权限是基础，确认是补充

### TP-015（SERVER_HA_RISK）：重置角色备份
- **scenario**：场景 15
- **module**：`SERVER_HA_RISK`
- **precondition**：玩家申请重置角色
- **test_data**：执行 character_reset
- **expected**：备份当前角色数据 + 二次确认 + 7 天恢复期（玩家可撤销）
- **notes**：注意"备份" vs "不可逆"——可逆更安全

### TP-016（SERVER_HA_RISK）：批量封号灰度
- **scenario**：场景 16
- **module**：`SERVER_HA_RISK`
- **precondition**：检测到 1000 个作弊账号
- **test_data**：风控系统触发批量封号
- **expected**：灰度封禁（先 100 个观察 24h）+ 全量 + 可解封 + 申诉入口
- **notes**：注意"灰度" vs "一次性"——灰度降低误封风险

### TP-017（SERVER_HA_RISK）：大额发奖单笔上限
- **scenario**：场景 17
- **module**：`SERVER_HA_RISK`
- **precondition**：GM 触发发放 10000 钻石
- **test_data**：执行 grant_diamond(player, 10000)
- **expected**：单笔上限拦截（如 5000）+ 要求分笔 + 二次确认 + 日志
- **notes**：注意"上限" vs "无限制"——上限防误操作

### TP-018（SERVER_HA_RISK）：跨服赛季重置同步
- **scenario**：场景 18
- **module**：`SERVER_HA_RISK`
- **precondition**：赛季结束，所有服需重置
- **test_data**：运营触发跨服赛季重置
- **expected**：各服按顺序重置（先 A 服后 B 服）+ 玩家登录看到新赛季 + 无数据错乱
- **notes**：注意"顺序" vs "并发"——顺序更可控

### TP-019（SERVER_HA_RISK）：分布式锁释放
- **scenario**：场景 12 扩展
- **module**：`SERVER_HA_RISK`
- **precondition**：拍卖行分布式锁
- **test_data**：业务完成后
- **expected**：锁正常释放（不残留）+ 超时自动释放（防死锁）
- **notes**：注意"释放" vs "残留"——残留会导致死锁

### TP-020（SERVER_HA_RISK）：事务隔离
- **scenario**：场景 12 扩展
- **module**：`SERVER_HA_RISK`
- **precondition**：拍卖行成交 + 扣款 + 发货
- **test_data**：3 个并发
- **expected**：3 个事务隔离（脏读/不可重复读/幻读防护）+ 无超发
- **notes**：注意"隔离级别" vs "串行化"——隔离级别需根据业务选

---

## 3. 边界陷阱

### 边界 1：vs BIZ（业务并发）
- **混淆点**："拍卖行并发" 看似 BIZ → 实际 BIZ 测"业务正常流程"（出价/成交），E 测"高并发极限 + 分布式锁 + 无超卖"
- **判定规则**：测"业务正常流转" → 归 BIZ；测"高并发极限 + HA + 高危风控" → 归 SPECIAL E
- **实例**：拍卖行出价 → 归 BIZ；1000 人并发拍卖 + 分布式锁 → 归 E

### 边界 2：vs BIZ（业务事务）
- **混淆点**："事务回滚" 看似 BIZ → 实际 BIZ 测"业务事务"（正常事务），E 测"宕机后事务恢复"
- **判定规则**：测"业务事务（ACID）" → 归 BIZ；测"宕机 + 重启 + 补偿" → 归 SPECIAL E
- **实例**：正常购买事务 → 归 BIZ；宕机后事务恢复 → 归 E

### 边界 3：vs AUX N（异常兜底）
- **混淆点**："服务崩溃" 看似 N → 实际 N 测"应用崩溃捕获"（客户端/服务异常），E 测"服务端 HA + 恢复"
- **判定规则**：测"应用层异常兜底" → 归 AUX N；测"服务器宕机 + Failover + 补偿" → 归 SPECIAL E
- **instance**：客户端崩溃后下次启动 → 归 N；服务端宕机后 Failover → 归 E

### 边界 4：vs CONFIG（GM 配置）
- **混淆点**："GM 权限" 看似 CONFIG → 实际 CONFIG 测"GM 权限配置字段"，E 测"GM 操作拦截 + 日志 + 回滚"
- **判定规则**：测"GM 权限/参数配置" → 归 CONFIG；测"GM 高危操作拦截（执行层）" → 归 SPECIAL E
- **instance**：GM 权限配置 → 归 CONFIG；GM 批量发奖二次确认 → 归 E

### 边界 5：vs LINK（跨服）
- **混淆点**："跨服数据重置" 看似 LINK → 实际 LINK 测"跨服数据同步业务"（正常业务），E 测"跨服 HA + 重置"
- **判定规则**：测"跨服数据正常同步" → 归 LINK；测"跨服重置 + 同步" → 归 SPECIAL E
- **instance**：跨服组队 → 归 LINK；跨服赛季重置 → 归 E

---

## 4. 验证证据

### 视觉证据
- 服务宕机时客户端"正在重连"提示
- 充值服宕机时"支付处理中"提示
- 大额发奖时"确认发奖"弹窗
- 灰度封禁时"账号异常"通知

### 日志证据
- `ha.server_crash` 关键词：服务器崩溃
- `ha.failover` 关键词：Failover 切换
- `ha.compensation` 关键词：补偿发奖
- `ha.rollback` 关键词：版本回档
- `concurrent.lock_acquired` 关键词：分布式锁获取
- `concurrent.lock_released` 关键词：分布式锁释放
- `risk.bulk_delete` 关键词：批量删除
- `risk.clear_currency` 关键词：清零货币
- `risk.bulk_ban` 关键词：批量封号
- `risk.gray_release` 关键词：灰度发布

### 数据证据
- `server_status` 表记录每次宕机 + Failover
- `transaction_log` 表记录未提交事务（回滚依据）
- `pending_reward` 表记录未发放奖励（补偿依据）
- `operation_audit` 表记录 GM 高危操作（player_id/operator/action/result/timestamp）
- 分布式锁的 `lock_key` + `lock_holder` + `expire_at`
- 玩家金币/道具在事务回滚后无变化
- 全服发奖 0 重复 + 100% 到账

### 性能证据
- Failover 切换耗时 < 30s
- 事务回滚耗时 < 1s
- 1000 万发奖耗时 < 30min
- 拍卖行并发 1000 人响应 < 500ms
- 补偿任务扫描 1000 万玩家 < 1h
