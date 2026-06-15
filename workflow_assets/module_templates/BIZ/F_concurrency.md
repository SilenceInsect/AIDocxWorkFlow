# F. 并发 / 多玩家场景

> **子类代码**：`BIZ_CONCURRENCY`
> **归属模块**：`BIZ`
> **来源**：用户细化定义 §6「并发/多玩家场景」（原定义完全缺失，新增）
>
> **测什么**：单玩家高频重复操作、多玩家同时触发同一种奖励、跨服多人组队/战斗/拍卖/公会多人操作的并发业务。
> **不测什么**：单玩家业务逻辑（归 A）、DB 锁（归 E）、协议字段（归 C）、网络层（归 AUX B）。
> **与其他子类的差异**：F 关注"多玩家/多操作并发业务结果"——A 关注"业务"，E 关注"DB 锁"，B 关注"单玩家时序"。

---

## 1. 典型场景

### 场景 1：单玩家高频操作
- 业务背景：玩家快速点击
- 涉及行为：1s 内发 100 次同一请求
- 触发动作：客户端脚本或快速点击
- 验证点：服务端正确去重

### 场景 2：多玩家抢同一奖励
- 业务背景：首杀 BOSS、限时礼包
- 涉及行为：100 玩家同时抢
- 触发动作：100 并发请求
- 验证点：仅 1 玩家获得奖励

### 场景 3：全服活动批量发奖
- 业务背景：运营活动奖励
- 涉及行为：10 万玩家同时领
- 触发动作：全服奖励发放
- 验证点：所有玩家都领到、无丢失

### 场景 4：跨服多人组队
- 业务背景：跨服组队副本
- 涉及行为：服 A + 服 B 玩家组队
- 触发动作：跨服组队协议
- 验证点：组队成功、数据一致

### 场景 5：多人同屏战斗
- 业务背景：百人战场
- 涉及行为：100 玩家同屏
- 触发动作：进入战场
- 验证点：所有玩家状态同步、无超发

### 场景 6：拍卖行并发竞价
- 业务背景：拍卖行
- 涉及行为：100 玩家同时出价
- 触发动作：100 并发 bid
- 验证点：最高价者得、串行处理

### 场景 7：公会多人操作
- 业务背景：公会贡献、公会战
- 涉及行为：50 公会成员同时操作
- 触发动作：并发贡献/参战
- 验证点：所有操作正确、无冲突

### 场景 8：多玩家同时升级
- 业务背景：升级触发全服通知
- 涉及行为：1000 玩家同时升级
- 触发动作：触发升级
- 验证点：所有玩家收到广播、服务端无超载

### 场景 9：聊天消息风暴
- 业务背景：世界聊天
- 涉及行为：1000 玩家同时发言
- 触发动作：并发发消息
- 验证点：消息按序到达、无丢失

### 场景 10：公会战积分
- 业务背景：100 人对 100 人公会战
- 涉及行为：双方同时获取积分
- 触发动作：参战
- 验证点：积分正确累计

### 场景 11：全服公告推送
- 业务背景：全服广播
- 涉及行为：100 万在线玩家
- 触发动作：全服公告
- 验证点：所有在线 1s 内收到

### 场景 12：跨服拍卖
- 业务背景：跨服拍卖
- 涉及行为：服 A 玩家拍服 B 玩家物品
- 触发动作：跨服竞拍
- 验证点：跨服并发处理

---

## 2. 种子测试点（TP 模板）

### TP-001（BIZ_CONCURRENCY）：单玩家高频去重
- **scenario**：场景 1
- **module**：`BIZ_CONCURRENCY`
- **precondition**：玩家钻石 100
- **test_data**：1s 内发 100 次"购买 50 钻道具"
- **expected**：仅 1 次成功、其他 99 次被去重拦截
- **notes**：注意"高频去重"vs"业务防刷"

### TP-002（BIZ_CONCURRENCY）：单玩家操作间隔
- **scenario**：场景 1
- **module**：`BIZ_CONCURRENCY`
- **precondition**：操作间隔 100ms
- **test_data**：200ms 内发 3 次操作
- **expected**：仅前 2 次正常、第 3 次被防刷
- **notes**：注意"防刷"vs"业务限制"

### TP-003（BIZ_CONCURRENCY）：多玩家抢首杀
- **scenario**：场景 2
- **module**：`BIZ_CONCURRENCY`
- **precondition**：100 玩家攻击世界 BOSS
- **test_data**：BOSS 死亡
- **expected**：仅最后 1 击玩家获首杀奖励
- **notes**：注意"并发锁"+"行锁"+"状态机"

### TP-004（BIZ_CONCURRENCY）：多玩家抢限时礼包
- **scenario**：场景 2
- **module**：`BIZ_CONCURRENCY`
- **precondition**：100 玩家抢限量 10 份的礼包
- **test_data**：100 并发 claim
- **expected**：仅前 10 玩家成功、其余失败
- **notes**：注意"限量"vs"限购"+"分布式锁"

### TP-005（BIZ_CONCURRENCY）：全服奖励批量发放
- **scenario**：场景 3
- **module**：`BIZ_CONCURRENCY`
- **precondition**：10 万玩家在线
- **test_data**：全服发 100 钻石
- **expected**：所有玩家 5 分钟内收到、每人 100 钻
- **notes**：注意"批量"vs"逐个"+"队列"

### TP-006（BIZ_CONCURRENCY）：跨服组队匹配
- **scenario**：场景 4
- **module**：`BIZ_CONCURRENCY`
- **precondition**：服 A 2 人 + 服 B 1 人匹配
- **test_data**：服 B 玩家点击匹配
- **expected**：匹配成功、跨服队伍创建
- **notes**：注意"跨服协议"+"延迟"

### TP-007（BIZ_CONCURRENCY）：跨服组队解散
- **scenario**：场景 4
- **module**：`BIZ_CONCURRENCY`
- **precondition**：跨服队伍 3 人
- **test_data**：队长解散
- **expected**：3 玩家同时收到解散通知
- **notes**：注意"跨服通知"+"时序"

### TP-008（BIZ_CONCURRENCY）：百人同屏战斗
- **scenario**：场景 5
- **module**：`BIZ_CONCURRENCY`
- **precondition**：100 玩家进入战场
- **test_data**：持续战斗 10 分钟
- **expected**：所有玩家状态同步、CPU < 80%、延迟 < 200ms
- **notes**：注意"性能"+"帧同步"

### TP-009（BIZ_CONCURRENCY）：同屏战斗死亡
- **scenario**：场景 5
- **module**：`BIZ_CONCURRENCY`
- **precondition**：100 人战斗
- **test_data**：1 玩家 HP=0
- **expected**：仅该玩家死亡、其他人继续战斗
- **notes**：注意"状态机"+"广播"

### TP-010（BIZ_CONCURRENCY）：拍卖行并发
- **scenario**：场景 6
- **module**：`BIZ_CONCURRENCY`
- **precondition**：100 玩家竞拍同一物品
- **test_data**：100 并发出价
- **expected**：最高价者得、串行处理、出价历史完整
- **notes**：注意"竞拍锁"+"出价队列"

### TP-011（BIZ_CONCURRENCY）：拍卖行超时
- **scenario**：场景 6
- **module**：`BIZ_CONCURRENCY`
- **precondition**：拍卖 5 分钟
- **test_data**：5 分钟后无人出价
- **expected**：拍卖结束、最后出价者得
- **notes**：注意"超时"vs"立即成交"

### TP-012（BIZ_CONCURRENCY）：公会贡献并发
- **scenario**：场景 7
- **module**：`BIZ_CONCURRENCY`
- **precondition**：50 成员同时贡献
- **test_data**：50 并发 contribute
- **expected**：所有贡献正确累计、公会资金正确
- **notes**：注意"行锁"vs"批量写"

### TP-013（BIZ_CONCURRENCY）：公会战积分
- **scenario**：场景 10
- **module**：`BIZ_CONCURRENCY`
- **precondition**：100 vs 100 公会战
- **test_data**：双方同时击杀
- **expected**：双方积分正确累计
- **notes**：注意"双方并发"+"对账"

### TP-014（BIZ_CONCURRENCY）：多玩家同时升级
- **scenario**：场景 8
- **module**：`BIZ_CONCURRENCY`
- **precondition**：1000 玩家同时升级
- **test_data`：触发升级
- **expected**：所有玩家升级成功、广播正常、服务端不超载
- **notes**：注意"广播风暴"+"限流"

### TP-015（BIZ_CONCURRENCY）：聊天消息风暴
- **scenario**：场景 9
- **module**：`BIZ_CONCURRENCY`
- **precondition**：1000 玩家同时发言
- **test_data**：1000 并发 send_msg
- **expected**：所有消息按到达顺序处理、无丢失
- **notes**：注意"消息队列"+"敏感词过滤性能"

### TP-016（BIZ_CONCURRENCY）：全服公告推送
- **scenario**：场景 11
- **module**：`BIZ_CONCURRENCY`
- **precondition**：100 万在线
- **test_data**：全服公告
- **expected**：1s 内所有在线收到、推送吞吐 ≥ 100 万 QPS
- **notes**：注意"广播优化"+"长连接吞吐"

### TP-017（BIZ_CONCURRENCY）：跨服拍卖
- **scenario**：场景 12
- **module**：`BIZ_CONCURRENCY`
- **precondition**：服 A 玩家拍服 B 玩家物品
- **test_data**：服 A 玩家出价
- **expected**：跨服竞拍成功、双方数据一致
- **notes**：注意"跨服锁"+"分布式事务"

### TP-018（BIZ_CONCURRENCY）：公会多人同时退出
- **scenario**：场景 7
- **module**：`BIZ_CONCURRENCY`
- **precondition**：50 成员公会
- **test_data**：30 成员同时退出
- **expected**：公会人数 -30、剩余 20、无人掉数据
- **notes**：注意"批量更新"+"公会解散判断"

### TP-019（BIZ_CONCURRENCY）：战斗同时领奖
- **scenario**：场景 5
- **module**：`BIZ_CONCURRENCY`
- **precondition**：战斗结束
- **test_data**：100 玩家同时领奖
- **expected**：100 玩家都领到、奖励池正确
- **notes**：注意"奖励池预扣"vs"先到先得"

### TP-020（BIZ_CONCURRENCY）：组队邀请并发
- **scenario**：场景 4
- **module**：`BIZ_CONCURRENCY`
- **precondition**：玩家 A 同时被 5 人邀请
- **test_data**：5 邀请同时发
- **expected**：A 选择 1 个、其他邀请失效
- **notes**：注意"邀请互斥"vs"接受多个"

### TP-021（BIZ_CONCURRENCY）：多玩家同时拉取排行榜
- **scenario**：场景 11
- **module**：`BIZ_CONCURRENCY`
- **precondition**：1 万玩家同时拉
- **test_data**：10000 并发 query
- **expected**：所有玩家 1s 内拿到排行榜
- **notes**：注意"缓存"+"CDN"

### TP-022（BIZ_CONCURRENCY）：公会战胜负判定
- **scenario**：场景 10
- **module**：`BIZ_CONCURRENCY`
- **precondition**：公会战结束
- **test_data**：双方总积分对比
- **expected**：积分高者胜、奖励发放
- **notes**：注意"平局"vs"胜负"

### TP-023（BIZ_CONCURRENCY）：邮件附件并发领
- **scenario**：场景 3
- **module**：`BIZ_CONCURRENCY`
- **precondition**：1000 玩家同时领全服邮件
- **test_data**：1000 并发 claim
- **expected**：所有玩家 30s 内领到
- **notes**：注意"批量发奖"vs"逐个发"

### TP-024（BIZ_CONCURRENCY）：跨服交易并发
- **scenario**：场景 12
- **module**：`BIZ_CONCURRENCY`
- **precondition**：100 服 A 玩家 + 100 服 B 玩家同时交易
- **test_data**：200 并发 cross_trade
- **expected**：所有交易正确、双方数据一致
- **notes**：注意"分布式事务"+"跨服锁"

### TP-025（BIZ_CONCURRENCY）：死亡掉落并发
- **scenario**：场景 5
- **module**：`BIZ_CONCURRENCY`
- **precondition**：100 玩家击杀同一 BOSS
- **test_data**：BOSS 死亡
- **expected**：按规则分配掉落（roll / 分配）、无超发
- **notes**：注意"分配规则"+"并发安全"

---

## 3. 边界陷阱

### 边界 1：vs A. 业务
- **混淆点**：「购买"重复"」——A 测业务、F 测并发
- **判定规则**：测"单玩家业务" → A；测"多玩家并发" → F
- **实例**：单笔购买扣款 → A；100 玩家抢礼包 → F

### 边界 2：vs E. 数据库
- **混淆点**：「并发"锁"」——E 测 DB 锁、F 测业务并发
- **判定规则**：测"DB 行锁" → E；测"业务层并发处理" → F
- **实例**：DB 行锁 → E；拍卖行业务并发 → F

### 边界 3：vs SPECIAL 高频包
- **混淆点**：「高频"包"」——F 测业务并发、SPECIAL 测行为
- **判定规则**：测"业务结果" → F；测"高频包行为后果（封号）" → SPECIAL
- **实例**：1s 100 次购买结果 → F；高频包导致封号 → SPECIAL

### 边界 4：vs B. 数据流
- **混淆点**：「并发"时序"」——B 测单玩家时序、F 测多玩家
- **判定规则**：测"单玩家多操作时序" → B；测"多玩家同时" → F
- **实例**：单玩家同时购买+合成 → B；100 玩家同时购买 → F

### 边界 5：vs LINK 跨服务
- **混淆点**：「跨服"并发"」——F 测业务、LIN K 测跨服务
- **判定规则**：测"跨服业务并发" → F；测"跨服务协议" → LINK
- **实例**：跨服拍卖 → F；跨服数据同步 → LINK

---

## 4. 验证证据

### 视觉证据
- 拍卖行最高价者得截图
- 全服邮件领奖截图
- 公会战积分榜截图

### 日志证据
- `CONCURRENT_OP count=N resource=xxx` 并发操作日志
- `LIMITED_REACHED limit=xxx` 限量拦截日志
- `BROADCAST count=N duration=Xms` 广播日志
- `LOCK_WAIT timeout=Xms` 锁等待日志
- `DISTRIBUTED_LOCK acquire/release` 分布式锁日志

### 数据证据
- 拍卖行表 `auction.bid_history` 完整
- 限量礼包表 `limited_gift.claimed_count <= total`
- 排行榜表 `rank.score` 与业务一致
- 跨服交易流水表 `cross_trade_log` 双方一致
- 死锁检测日志

### 性能证据
- 100 并发业务请求 P99 < 500ms
- 1000 并发去重正确率 = 100%
- 全服广播 100 万玩家 < 2s
- 跨服并发数据同步延迟 < 1s
- 死锁率 = 0
- 限量竞争 100% 准确
