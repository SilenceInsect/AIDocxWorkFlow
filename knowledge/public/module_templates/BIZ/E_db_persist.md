# E. 数据库持久化

> **子类代码**：`BIZ_DB_PERSIST`
> **归属模块**：`BIZ`
> **来源**：用户细化定义 §5「数据库持久化（存储/加载/更新全链路）」
>
> **测什么**：业务数据落地存储、加载恢复、事务并发锁、数据清理归档、容错兜底。
> **不测什么**：业务逻辑（归 A）、缓存层（归 UTIL C）、分布式中间件（归 UTIL）。
> **与其他子类的差异**：E 关注"DB 落库+事务+恢复"——A 关注"业务"，B 关注"链路"，F 关注"多玩家并发"。

---

## 1. 典型场景

### 场景 1：操作后实时落库
- 业务背景：购买、合成、领取
- 涉及数据：玩家属性、背包、任务、邮件
- 触发动作：完成业务操作
- 验证点：DB 立即写入、读时与业务结果一致

### 场景 2：分库分表隔离
- 业务背景：玩家 ID 哈希分库
- 涉及数据：player_0/1/2 db、bag_0/1/2 table
- 触发动作：玩家 A 购买道具
- 验证点：数据落在正确分库分表

### 场景 3：重登录数据一致
- 业务背景：玩家下线后重新登录
- 涉及数据：玩家全量数据
- 触发动作：重连
- 验证点：DB 读出数据 = 下线前内存状态

### 场景 4：切服数据一致
- 业务背景：玩家从服 A 切到服 B
- 涉及数据：玩家数据迁移
- 触发动作：切服协议
- 验证点：服 B 读到服 A 的全量数据

### 场景 5：服务重启数据恢复
- 业务背景：服务宕机重启
- 涉及数据：所有在线玩家数据
- 触发动作：服务重启
- 验证点：DB 读出数据 = 宕机前状态

### 场景 6：断线未完成操作回滚
- 业务背景：购买进行中网络断开
- 涉及数据：扣款数据
- 触发动作：断线超时
- 验证点：扣款回滚、玩家无损失

### 场景 7：多玩家并发修改同条数据
- 业务背景：排行榜、拍卖行
- 涉及数据：竞拍同一物品
- 触发动作：100 玩家同时出价
- 验证点：数据库事务锁生效、串行处理

### 场景 8：单玩家并发扣发
- 业务背景：玩家同时购买 2 个道具
- 涉及数据：钻石余额
- 触发动作：并发扣款
- 验证点：余额正确、避免超扣

### 场景 9：过期临时数据清理
- 业务背景：限时道具、限时邮件
- 涉及数据：临时数据
- 触发动作：定时清理
- 验证点：过期数据被清理、不污染主库

### 场景 10：赛季数据归档
- 业务背景：赛季结束
- 涉及数据：赛季积分、排名
- 触发动作：赛季结算
- 验证点：数据归档、可查询、不丢

### 场景 11：删号逻辑删除
- 业务背景：玩家主动删号
- 涉及数据：玩家全量数据
- 触发动作：删号协议
- 验证点：数据标记删除、可恢复期内恢复

### 场景 12：DB 抖动自动重试
- 业务背景：DB 短暂不可用
- 涉及数据：业务写入
- 触发动作：DB 报错
- 验证点：自动重试 N 次、不出现半写脏数据

### 场景 13：宕机恢复数据无丢失
- 业务背景：宕机后重启
- 涉及数据：宕机前已确认但未落库的数据
- 触发动作：服务恢复
- 验证点：所有已确认数据均落库

---

## 2. 种子测试点（TP 模板）

### TP-001（BIZ_DB_PERSIST）：购买后落库
- **scenario**：场景 1
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家钻石 100
- **test_data**：`purchase(player_id, item_id, cost=50)`
- **expected**：1s 内 DB 写入：钻石 = 50、背包 +1 道具
- **notes**：注意"实时"vs"异步落库"

### TP-002（BIZ_DB_PERSIST）：DB 读取与业务结果一致
- **scenario**：场景 1
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家购买后
- **test_data**：`SELECT * FROM bag WHERE player_id=xxx`
- **expected**：与业务返回结果完全一致
- **notes**：注意"主从同步延迟"

### TP-003（BIZ_DB_PERSIST）：分库正确性
- **scenario**：场景 2
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家 ID = 12345
- **test_data**：`purchase(player_id=12345, ...)`
- **expected**：数据写入 `db_5.bag_5`（按 player_id % 32）
- **notes**：注意"分片键"+"跨分片事务"

### TP-004（BIZ_DB_PERSIST）：跨分片禁止
- **scenario**：场景 2
- **module**：`BIZ_DB_PERSIST`
- **precondition**：跨分片事务
- **test_data**：尝试跨分片事务
- **expected**：拦截或分布式事务 + 性能可接受
- **notes**：注意"分片"vs"分布式事务"+"性能"

### TP-005（BIZ_DB_PERSIST）：重登录数据一致
- **scenario**：场景 3
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家购买 5 个道具、钻石 50
- **test_data**：登出 → 重新登录
- **expected**：登录后看到 5 个道具、钻石 50
- **notes**：注意"登录"vs"重连"+"登录拉取数据"

### TP-006（BIZ_DB_PERSIST）：切服数据迁移
- **scenario**：场景 4
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家在服 A 有 5 个道具
- **test_data**：`switch_server(player_id, from=A, to=B)`
- **expected**：服 B 可查到服 A 的全量数据
- **notes**：注意"数据迁移"vs"数据复制"+"数据一致性"

### TP-007（BIZ_DB_PERSIST）：服务重启恢复
- **scenario**：场景 5
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家购买 5 个道具后服务宕机
- **test_data**：服务重启 + 玩家登录
- **expected**：DB 读出 5 个道具
- **notes**：注意"已落库"vs"未落库"+"宕机前最后状态"

### TP-008（BIZ_DB_PERSIST）：断线回滚
- **scenario**：场景 6
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家购买中
- **test_data**：断线超时（30s）
- **expected**：扣款回滚、玩家钻石恢复
- **notes**：注意"已扣未发"vs"已扣已发"+"事务回滚"

### TP-009（BIZ_DB_PERSIST）：并发竞拍
- **scenario**：场景 7
- **module**：`BIZ_DB_PERSIST`
- **precondition**：100 玩家竞拍同一物品
- **test_data**：100 个 bid 请求
- **expected**：串行处理、最高价者得、无超发
- **notes**：注意"行锁"vs"乐观锁"+"死锁"

### TP-010（BIZ_DB_PERSIST）：排行榜并发写
- **scenario**：场景 7
- **module**：`BIZ_DB_PERSIST`
- **precondition**：100 玩家同时更新积分
- **test_data**：100 个 score_update
- **expected**：所有积分正确更新、无丢失
- **notes**：注意"批量写"vs"逐行写"+"性能"

### TP-011（BIZ_DB_PERSIST）：单玩家并发扣款
- **scenario**：场景 8
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家钻石 100
- **test_data**：同时发 2 个"购买 80 钻"协议
- **expected**：第 1 个成功、扣到 20；第 2 个失败、不扣
- **notes**：注意"行锁"vs"乐观锁"+"余额不足拦截"

### TP-012（BIZ_DB_PERSIST）：道具过期清理
- **scenario**：场景 9
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家有 5 个 7 天限时道具
- **test_data**：第 8 天查看
- **expected**：DB 中道具行已删或标记 expired
- **notes**：注意"硬删"vs"软删"+"清理任务"

### TP-013（BIZ_DB_PERSIST）：赛季数据归档
- **scenario**：场景 10
- **module**：`BIZ_DB_PERSIST`
- **precondition**：赛季结束
- **test_data**：赛季结算
- **expected**：赛季数据写入 `season_archive` 表、可查询
- **notes**：注意"归档"vs"删除"+"查询性能"

### TP-014（BIZ_DB_PERSIST）：删号逻辑删除
- **scenario**：场景 11
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家申请删号
- **test_data**：`delete_account(player_id)`
- **expected**：玩家表标记 deleted、保留 30 天可恢复
- **notes**：注意"逻辑删除"vs"物理删除"+"恢复机制"

### TP-015（BIZ_DB_PERSIST）：DB 抖动重试
- **scenario**：场景 12
- **module**：`BIZ_DB_PERSIST`
- **precondition**：DB 网络抖动 1s
- **test_data**：`purchase(...)`
- **expected**：服务端自动重试 3 次、最终成功或失败
- **notes**：注意"重试"vs"降级"+"幂等"

### TP-016（BIZ_DB_PERSIST）：事务回滚
- **scenario**：场景 12
- **module**：`BIZ_DB_PERSIST`
- **precondition**：购买流程 2 步（扣款 + 发货）
- **test_data**：第 2 步失败
- **expected**：第 1 步回滚、玩家无损失
- **notes**：注意"本地事务"vs"分布式事务"+"补偿"

### TP-017（BIZ_DB_PERSIST）：宕机恢复
- **scenario**：场景 13
- **module**：`BIZ_DB_PERSIST`
- **precondition**：宕机前有 100 笔已确认交易
- **test_data**：服务恢复
- **expected**：100 笔交易均落库、无丢失
- **notes**：注意"WAL"+"binlog"+"checkpoint"

### TP-018（BIZ_DB_PERSIST）：半写脏数据
- **scenario**：场景 12
- **module**：`BIZ_DB_PERSIST`
- **precondition**：DB 写入一半宕机
- **test_data**：DB 恢复
- **expected**：要么全成功、要么全失败、无中间状态
- **notes**：注意"ACID"+"事务原子性"

### TP-019（BIZ_DB_PERSIST）：大表查询
- **scenario**：场景 1
- **module**：`BIZ_DB_PERSIST`
- **precondition**：1 亿玩家
- **test_data**：`SELECT * FROM player WHERE level > 50`
- **expected**：分页 + 索引、查询 < 1s
- **notes**：注意"索引"+"分页"+"慢查询"

### TP-020（BIZ_DB_PERSIST）：批量插入
- **scenario**：场景 1
- **module**：`BIZ_DB_PERSIST`
- **precondition**：1 万笔日志
- **test_data**：`batch_insert(10000 rows)`
- **expected**：< 5s、无死锁
- **notes**：注意"批量大小"+"事务大小"

### TP-021（BIZ_DB_PERSIST）：读写分离延迟
- **scenario**：场景 3
- **module**：`BIZ_DB_PERSIST`
- **precondition**：主从复制
- **test_data**：写入主库后立即从库读
- **expected**：延迟 < 1s 或从读主
- **notes**：注意"读写分离"+"一致性级别"

### TP-022（BIZ_DB_PERSIST）：历史日志归档
- **scenario**：场景 10
- **module**：`BIZ_DB_PERSIST`
- **precondition**：1 年前日志
- **test_data**：归档任务
- **expected**：旧日志移到归档表、主库性能恢复
- **notes**：注意"分区表"+"冷热数据分离"

### TP-023（BIZ_DB_PERSIST）：回档补偿
- **scenario**：场景 11
- **module**：`BIZ_DB_PERSIST`
- **precondition**：服务器回档
- **test_data**：批量补偿
- **expected**：受影响的玩家收到补偿
- **notes**：注意"回档"vs"回滚"+"补偿日志"

### TP-024（BIZ_DB_PERSIST）：删号恢复
- **scenario**：场景 11
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家已删号 5 天
- **test_data**：`restore_account(player_id)`
- **expected**：玩家数据恢复、可登录
- **notes**：注意"恢复期"内有效

### TP-025（BIZ_DB_PERSIST）：跨服查询
- **scenario**：场景 4
- **module**：`BIZ_DB_PERSIST`
- **precondition**：玩家在服 A
- **test_data**：`query_player(服B_player_id)`
- **expected**：从服 B DB 查、跨服网关路由
- **notes**：注意"跨服 DB 访问"+"安全"

---

## 3. 边界陷阱

### 边界 1：vs A. 业务
- **混淆点**：「购买"持久化"」——A 测业务、E 测 DB
- **判定规则**：测"业务结果" → A；测"DB 写入/事务" → E
- **实例**：购买扣 100 → A；DB 落库 + 事务 → E

### 边界 2：vs B. 数据流
- **混淆点**：「数据"流"」——B 测链路、E 测 DB
- **判定规则**：测"传输链路" → B；测"DB 落库" → E
- **实例**：服务端下行推送 → B；DB 落库 → E

### 边界 3：vs UTIL C. 缓存
- **混淆点**：「数据"缓存"」——UTIL C 测缓存、E 测 DB
- **判定规则**：测"Redis 缓存" → UTIL C；测"DB 落库" → E
- **实例**：Redis 缓存一致性 → UTIL C；DB 事务锁 → E

### 边界 4：vs F. 并发
- **混淆点**：「并发"锁"」——E 测 DB 锁、F 测多玩家
- **判定规则**：测"DB 行锁/事务" → E；测"业务层并发" → F
- **实例**：DB 行锁 → E；100 玩家同时抽奖 → F

### 边界 5：vs UTIL N. 异常兜底
- **混淆点**：「DB"异常"」——UTIL N 测通用异常、E 测 DB
- **判定规则**：测"通用异常兜底" → UTIL N；测"DB 特定异常" → E
- **实例**：全局崩溃 → UTIL N；DB 抖动重试 → E

---

## 4. 验证证据

### 视觉证据
- DB 客户端查询截图（如 Navicat）
- 慢查询日志截图

### 日志证据
- `DB_WRITE table=xxx pk=xxx status=success/fail` 写库日志
- `DB_TRANSACTION_BEGIN/COMMIT/ROLLBACK` 事务日志
- `DB_RETRY count=N` 重试日志
- `SLOW_QUERY duration=Xms sql=xxx` 慢查询日志
- `ARCHIVE_TABLE from=xxx to=xxx count=N` 归档日志

### 数据证据
- 玩家表 `player.player_id, level, exp, ...`
- 背包表 `bag.player_id, item_id, count, expire_at`
- 邮件表 `mail.mail_id, player_id, status, expire_at`
- 任务表 `task.player_id, task_id, progress, status`
- 排行榜表 `rank.player_id, score, rank`
- 事务隔离级别 = `READ_COMMITTED` 或 `REPEATABLE_READ`
- 分库分表规则文档
- 索引列表（覆盖高频查询）

### 性能证据
- 单条写入 < 10ms
- 事务提交 < 50ms
- 1000 笔批量插入 < 5s
- 1 亿数据查询 < 1s（带索引）
- DB 连接池利用率 < 80%
- 主从同步延迟 < 1s
