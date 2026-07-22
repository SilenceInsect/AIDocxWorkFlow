# B. 端服数据流

> **子类代码**：`BIZ_DATA_FLOW`
> **归属模块**：`BIZ`
> **来源**：用户细化定义 §2「数据流（端-服-库完整链路）」
>
> **测什么**：客户端到服务端的上行/下行数据流、跨服分布式数据流、多操作并发时序一致性。
> **不测什么**：网络协议字段格式（归 C）、网络底层收发包（归 AUX B）、单笔业务逻辑（归 A）。
> **与其他子类的差异**：B 关注"链路数据流向+时序"——A 关注"业务规则"，C 关注"协议字段"，E 关注"DB 落库"，F 关注"多玩家并发"。

---

## 1. 典型场景

### 场景 1：客户端上行参数完整性
- 业务背景：购买请求、合成请求
- 涉及数据：操作指令 + 参数
- 触发动作：发送上行请求
- 验证点：参数齐全时正常处理；缺参/非法参拦截

### 场景 2：客户端非法参数过滤
- 业务背景：购买数量为负数、ID 超长
- 涉及数据：参数合法性
- 触发动作：构造非法参数
- 验证点：服务端拦截 + 不造成脏数据

### 场景 3：重复请求拦截
- 业务背景：玩家连点购买按钮、客户端重发
- 涉及数据：重复请求识别
- 触发动作：同一请求 1s 内发 10 次
- 验证点：服务端幂等处理、只扣一次款

### 场景 4：服务端下行推送
- 业务背景：道具变动、活动状态、实时战斗帧
- 涉及数据：服务端主动推
- 触发动作：服务端变更数据
- 验证点：客户端实时收到、UI 同步

### 场景 5：跨服数据透传
- 业务背景：跨服交易、跨服组队、跨服排行榜
- 涉及数据：网关、逻辑服、活动服、聊天服之间
- 触发动作：跨服操作
- 验证点：数据无丢失、不错乱

### 场景 6：多操作并发时序
- 业务背景：玩家同时购买 + 合成 + 出售
- 涉及数据：多操作并发
- 触发动作：3 个操作同时下发
- 验证点：数据更新顺序正确、无先扣后发/重复发放/多扣

### 场景 7：全服广播
- 业务背景：世界 BOSS 击杀、全服公告
- 涉及数据：全服推送
- 触发动作：服务端触发广播
- 验证点：在线玩家全部收到、离线玩家登录后看到

### 场景 8：红点推送
- 业务背景：新邮件红点、活动开启红点
- 涉及数据：增量推送
- 触发动作：服务端变更状态
- 验证点：客户端红点实时显示

### 场景 9：实时战斗帧同步
- 业务背景：PVP 战斗、技能释放
- 涉及数据：高频帧数据
- 触发动作：服务端帧同步
- 验证点：客户端实时显示、无明显延迟

### 场景 10：服务端异步队列
- 业务背景：发奖异步任务
- 涉及数据：消息队列
- 触发动作：触发异步任务
- 验证点：异步任务最终一致

---

## 2. 种子测试点（TP 模板）

### TP-001（BIZ_DATA_FLOW）：上行参数缺失
- **scenario**：场景 1
- **module**：`BIZ_DATA_FLOW`
- **precondition**：购买协议要求 `item_id, count, currency_type`
- **test_data**：缺 `count` 字段
- **expected**：拦截 + 错误码 `PARAM_MISSING`
- **notes**：注意"缺字段"vs"字段为 null"vs"字段为 0"

### TP-002（BIZ_DATA_FLOW）：上行参数非法
- **scenario**：场景 2
- **module**：`BIZ_DATA_FLOW`
- **precondition**：购买数量字段类型 int
- **test_data**：`count = "abc" / -1 / 0 / 2147483648`（越界）
- **expected**：拦截 + 错误码 `PARAM_INVALID`
- **notes**：注意"类型错"vs"越界"vs"业务非法"

### TP-003（BIZ_DATA_FLOW）：超长参数容错
- **scenario**：场景 2
- **module**：`BIZ_DATA_FLOW`
- **precondition**：玩家名最长 32 字符
- **test_data**：玩家名 = 1MB 字符串
- **expected**：服务端拒绝接收、不打爆内存
- **notes**：注意"长度校验"vs"协议体大小限制"

### TP-004（BIZ_DATA_FLOW）：重复请求幂等
- **scenario**：场景 3
- **module**：`BIZ_DATA_FLOW`
- **precondition**：玩家钻石 100
- **test_data**：1s 内发 10 次"购买 50 钻石道具"协议
- **expected**：仅第 1 次成功、其余返回"已处理"、扣款 1 次
- **notes**：注意"幂等键"vs"时间窗口"vs"业务状态"

### TP-005（BIZ_DATA_FLOW）：防刷限流
- **scenario**：场景 3
- **module**：`BIZ_DATA_FLOW`
- **precondition**：1s 限流 10 次
- **test_data**：1s 内发 100 次不同请求
- **expected**：前 10 次正常、后续被限流 + 错误码 `RATE_LIMIT`
- **notes**：注意"全局限流"vs"玩家级限流"vs"协议级限流"

### TP-006（BIZ_DATA_FLOW）：服务端下行推送
- **scenario**：场景 4
- **module**：`BIZ_DATA_FLOW`
- **precondition**：玩家在线
- **test_data**：GM 给玩家发 100 钻石
- **expected**：客户端 1s 内收到道具变动推送、UI 钻石 +100
- **notes**：注意"长连接推送"vs"轮询拉取"vs"HTTP 推送"

### TP-007（BIZ_DATA_FLOW）：离线推送
- **scenario**：场景 4
- **module**：`BIZ_DATA_FLOW`
- **precondition**：玩家离线
- **test_data**：GM 给玩家发邮件
- **expected**：玩家登录后看到邮件、推送不丢失
- **notes**：注意"离线消息队列"持久化

### TP-008（BIZ_DATA_FLOW）：活动状态推送
- **scenario**：场景 4
- **module**：`BIZ_DATA_FLOW`
- **precondition**：活动未开始
- **test_data**：服务端切换活动状态
- **expected**：客户端实时收到状态变更、活动入口出现
- **notes**：注意"状态推送"vs"全量拉取"

### TP-009（BIZ_DATA_FLOW）：跨服交易数据
- **scenario**：场景 5
- **module**：`BIZ_DATA_FLOW`
- **precondition**：服 A 玩家向服 B 玩家发起交易
- **test_data**：`cross_trade(A_player, B_player, item_id)`
- **expected**：服 A 扣道具、服 B 加道具、双方数据一致
- **notes**：注意"跨服"vs"全服"+"分布式事务"

### TP-010（BIZ_DATA_FLOW）：跨服排行榜
- **scenario**：场景 5
- **module**：`BIZ_DATA_FLOW`
- **precondition**：服 A 玩家积分变化
- **test_data**：玩家在服 A 赢 1 场
- **expected**：跨服排行榜数据更新、服 B 玩家看到服 A 玩家
- **notes**：注意"数据同步延迟"容忍度

### TP-011（BIZ_DATA_FLOW）：并发操作时序
- **scenario**：场景 6
- **module**：`BIZ_DATA_FLOW`
- **precondition**：玩家钻石 100
- **test_data**：同时发"购买 80 钻道具"和"购买 50 钻道具"
- **expected**：第 1 个成功 + 钻石 20；第 2 个失败 + 错误码 `NOT_ENOUGH`
- **notes**：注意"乐观锁"vs"悲观锁"vs"队列"

### TP-012（BIZ_DATA_FLOW）：先扣后发
- **scenario**：场景 6
- **module**：`BIZ_DATA_FLOW`
- **precondition**：购买流程分 2 步（扣款、发货）
- **test_data**：扣款后服务宕机
- **expected**：重启后回滚扣款、不丢钱
- **notes**：注意"事务"vs"补偿"vs"TCC"

### TP-013（BIZ_DATA_FLOW）：全服广播
- **scenario**：场景 7
- **module**：`BIZ_DATA_FLOW`
- **precondition**：1000 在线玩家
- **test_data**：世界 BOSS 击杀
- **expected**：所有在线 1s 内收到广播
- **notes**：注意"广播风暴"+"长连接吞吐"

### TP-014（BIZ_DATA_FLOW）：离线玩家补偿
- **scenario**：场景 7
- **module**：`BIZ_DATA_FLOW`
- **precondition**：全服奖励发放时玩家离线
- **test_data**：玩家上线
- **expected**：玩家看到离线期间的全服奖励
- **notes**：注意"离线消息"vs"重新拉取"

### TP-015（BIZ_DATA_FLOW）：红点推送
- **scenario**：场景 8
- **module**：`BIZ_DATA_FLOW`
- **precondition**：玩家无红点
- **test_data**：服务端收到新邮件
- **expected**：客户端邮件图标红点实时出现
- **notes**：注意"红点"vs"Toast"vs"飘字"是不同通道

### TP-016（BIZ_DATA_FLOW）：实时战斗帧
- **scenario**：场景 9
- **module**：`BIZ_DATA_FLOW`
- **precondition**：PVP 战斗 30 帧/秒
- **test_data**：1 分钟战斗
- **expected**：客户端帧同步延迟 < 200ms
- **notes**：注意"帧率"vs"延迟"+"丢包容错"

### TP-017（BIZ_DATA_FLOW）：高频协议性能
- **scenario**：场景 9
- **module**：`BIZ_DATA_FLOW`
- **precondition**：1000 人 PVP
- **test_data**：服务端 30s 推 30 万帧
- **expected**：P99 延迟 < 200ms、CPU < 60%
- **notes**：注意"性能"vs"正确性"（与 K 性能配合）

### TP-018（BIZ_DATA_FLOW）：异步任务最终一致
- **scenario**：场景 10
- **module**：`BIZ_DATA_FLOW`
- **precondition**：发奖异步任务
- **test_data**：触发 1000 笔异步发奖
- **expected**：5 分钟内全部到账、无重复无丢失
- **notes**：注意"最终一致"vs"强一致"+"补偿重试"

### TP-019（BIZ_DATA_FLOW）：消息队列堆积
- **scenario**：场景 10
- **module**：`BIZ_DATA_FLOW`
- **precondition**：消息队列积压 10 万条
- **test_data**：消费端扩容
- **expected**：积压逐步消化、无丢失
- **notes**：注意"幂等消费"vs"重复消费"

### TP-020（BIZ_DATA_FLOW）：下行字段过滤
- **scenario**：场景 4
- **module**：`BIZ_DATA_FLOW`
- **precondition**：服务端下行含玩家敏感字段
- **test_data**：抓包查看下行
- **expected**：敏感字段（密码、token）不下发
- **notes**：注意"服务端过滤"vs"客户端过滤"

---

## 3. 边界陷阱

### 边界 1：vs C. 协议交互
- **混淆点**：「参数"非法"」——B 测数据流、C 测协议
- **判定规则**：测"链路数据" → B；测"协议字段格式" → C
- **实例**：参数非法拦截 → B-002；协议字段类型 → C

### 边界 2：vs E. 数据库持久化
- **混淆点**：「数据"落库"」——B 测数据流、E 测 DB
- **判定规则**：测"传输链路" → B；测"DB 写入" → E
- **实例**：服务端下行推送 → B-006；DB 写入事务 → E

### 边界 3：vs F. 并发多玩家
- **混淆点**：「并发"时序"」——B 测时序、F 测多玩家
- **判定规则**：测"单玩家多操作时序" → B；测"多玩家并发" → F
- **实例**：单玩家同时购买 + 合成 → B-011；100 人同时抢拍 → F

### 边界 4：vs AUX B. 网络层
- **混淆点**：「网络"收发"」——B 测数据流、AUX B 测网络
- **判定规则**：测"业务数据语义" → B；测"网络协议打包/重连" → AUX B
- **实例**：上行参数缺失 → B-001；网络包 AES 加密 → AUX B

### 边界 5：vs A. 核心业务
- **混淆点**：「购买"业务"」——A 测业务、B 测数据流
- **判定规则**：测"业务结果" → A；测"传输链路" → B
- **实例**：购买扣款 100 → A-011；上行参数 → B-001

---

## 4. 验证证据

### 视觉证据
- 客户端实时收到推送后的 UI 更新截图
- 红点出现/消失截图

### 日志证据
- 服务端接收上行日志 `RECV_REQ`
- 服务端下行推送日志 `SEND_PUSH`
- 客户端接收日志 `RECV_PUSH`
- 限流拦截日志 `RATE_LIMIT_HIT`
- 重复请求拦截日志 `DUP_REQUEST_BLOCKED`

### 数据证据
- 服务端请求日志表 `req_log.method, params, status`
- 推送消息表 `push_msg.from, to, type, status`
- 跨服交易流水表 `cross_trade_log`（双服一致）
- 客户端收包顺序日志（应与服务端发送顺序一致）

### 性能证据
- 单协议 P99 延迟 < 100ms
- 推送吞吐 ≥ 10 万 QPS
- 跨服数据同步延迟 < 1s
- 异步任务消费速度 ≥ 1000 笔/秒
