# C. 弱网 / 断网 / 限流防刷

> **子类代码**：`WEAK_NET_RATE_LIMIT`
> **归属模块**：`SPECIAL`
> **来源**：用户细化定义 §3「弱网/断网、限流防刷业务容错」
>
> **测什么**：弱网高延迟、网络抖动、4G/WiFi 切换、完全断网、网关连接失败、跨服通道断开的**业务容错**（重连后自动续执行、未完成操作缓存队列、失败回滚不重复扣发、不出现数据半写/不卡死界面/不丢失操作）；高频点击/批量重复请求/短时间大量发包/批量领取/批量建号的**限流拦截**、冷却限制、弹窗提示、防雪崩保护。
> **不测什么**：底层网络重连框架（归 AUX B）、通用业务异常处理（归 BIZ）、崩溃捕获（归 AUX N）。
> **与其他子类的差异**：C 关注"环境异常 + 流量限流"——A 关注"业务边界"（数值/时间/权限）、B 关注"对抗行为"（反作弊）；C 是环境 + 流量，B 是对抗。

---

## 1. 典型场景

### 场景 1：弱网高延迟
- 业务背景：玩家在地铁中 4G 弱网，延迟 2s
- 涉及字段/工具：network_latency、request_timeout
- 触发动作：玩家点击"购买"
- 验证点：请求超时后重试 + 友好提示，不卡死界面

### 场景 2：网络抖动
- 业务背景：WiFi 不稳定，频繁断连
- 涉及字段/工具：network_jitter、reconnect_count
- 触发动作：玩家进行副本战斗
- 验证点：战斗数据不丢、不卡顿

### 场景 3：4G/WiFi 切换
- 业务背景：玩家从 WiFi 切到 4G
- 涉及字段/工具：network_type_switch、session_keep
- 触发动作：副本进行中切换网络
- 验证点：会话保持，数据不丢

### 场景 4：完全断网
- 业务背景：玩家进入电梯，完全断网
- 涉及字段/工具：network_disconnect、offline_cache
- 触发动作：玩家点击"购买"
- 验证点：未完成操作缓存 + 网络恢复后自动重试

### 场景 5：网关连接失败
- 业务背景：网关服宕机
- 涉及字段/工具：gateway_status、failover
- 触发动作：玩家所有请求
- 验证点：客户端重连备用网关 + 业务不中断

### 场景 6：跨服通道断开
- 业务背景：跨服战斗时通道断开
- 涉及字段/工具：cross_server_channel、sync_status
- 触发动作：跨服战斗中
- 验证点：通道恢复后数据同步，玩家正常返回

### 场景 7：高频点击
- 业务背景：玩家 1s 内点击"领取" 50 次
- 涉及字段/工具：click_count、cooldown
- 触发动作：UI 高频点击
- 验证点：客户端冷却 + 服务端去重

### 场景 8：批量重复请求
- 业务背景：脚本 1s 发 1000 个相同请求
- 涉及字段/工具：request_rate、rate_limit
- 触发动作：批量重复
- 验证点：服务端限流 + 丢弃非法请求

### 场景 9：短时间大量发包
- 业务背景：脚本 1min 发 10 万个协议包
- 涉及字段/工具：packet_rate、ddos_detect
- 触发动作：批量发包攻击
- 验证点：服务端流量限流 + IP 封禁

### 场景 10：批量领取奖励
- 业务背景：脚本 1min 领取 10000 次奖励
- 涉及字段/工具：claim_count、daily_limit
- 触发动作：批量领取
- 验证点：每日领取上限 + 限流

### 场景 11：未完成操作缓存队列
- 业务背景：玩家在断网前点击"购买"
- 涉及字段/工具：pending_operation、offline_queue
- 触发动作：断网时操作未完成
- 验证点：网络恢复后自动重发（幂等）

### 场景 12：失败回滚资源
- 业务背景：业务操作中途失败
- 涉及字段/工具：transaction_rollback、resource_lock
- 触发动作：业务失败
- 验证点：已扣资源回滚 + 无数据半写

---

## 2. 种子测试点（TP 模板）

### TP-001（WEAK_NET_RATE_LIMIT）：弱网请求超时重试
- **scenario**：场景 1
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：网络延迟 2s（弱网模拟）
- **test_data**：调用 purchase_item API
- **expected**：请求 5s 超时后客户端自动重试 1 次 + 弹窗"网络较慢"；服务端去重避免重复扣款
- **notes**：注意"超时" vs "失败"——超时要重试，失败要回滚

### TP-002（WEAK_NET_RATE_LIMIT）：网络抖动数据不丢
- **scenario**：场景 2
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：WiFi 频繁断连（5s/次）
- **test_data**：副本战斗中网络断开
- **expected**：副本数据不丢，重连后继续战斗
- **notes**：注意"抖动" vs "断网"——抖动需快速重连

### TP-003（WEAK_NET_RATE_LIMIT）：网络切换会话保持
- **scenario**：场景 3
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：玩家副本进行中
- **test_data**：WiFi 切 4G（IP 变化）
- **expected**：会话保持（重连后玩家继续副本），不踢下线
- **notes**：注意"切换" vs "断网"——切换需重连但不踢

### TP-004（WEAK_NET_RATE_LIMIT）：完全断网操作缓存
- **scenario**：场景 4
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：玩家在断网前点击"购买"
- **test_data**：电梯中无网络
- **expected**：操作进入 pending_queue，提示"网络异常，将在恢复后重试"；网络恢复后自动重发（幂等）
- **notes**：注意"缓存" vs "丢弃"——重要操作需缓存

### TP-005（WEAK_NET_RATE_LIMIT）：网关失败 Failover
- **scenario**：场景 5
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：主网关宕机
- **test_data**：玩家发请求
- **expected**：客户端重连备用网关（DNS 切换），业务不中断
- **notes**：注意"网关" vs "逻辑服"——网关是流量入口

### TP-006（WEAK_NET_RATE_LIMIT）：跨服通道恢复同步
- **scenario**：场景 6
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：跨服战斗中通道断开
- **test_data**：战斗持续 30s 通道断开
- **expected**：通道恢复后战斗数据同步，玩家正常返回本服
- **notes**：注意"跨服断" vs "跨服失败"——断可恢复，失败需重试

### TP-007（WEAK_NET_RATE_LIMIT）：高频点击客户端冷却
- **scenario**：场景 7
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：玩家连续点击"领取"
- **test_data**：1s 内点击 50 次
- **expected**：客户端 0.5s 冷却（按钮置灰），最多发 2 个请求
- **notes**：注意"客户端" vs "服务端"——客户端是 UX，服务端是业务

### TP-008（WEAK_NET_RATE_LIMIT）：批量重复请求去重
- **scenario**：场景 8
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：脚本发送 1000 个相同 request_id
- **test_data**：1000 个 claim_reward 请求
- **expected**：第 1 个成功，2-1000 个返回 ERR_ALREADY_PROCESSED；服务端按 request_id 去重
- **notes**：注意"重复" vs "并发"——重复是同 request_id，并发是不同

### TP-009（WEAK_NET_RATE_LIMIT）：流量限流防雪崩
- **scenario**：场景 9
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：单 IP 1min 超过 10000 包
- **test_data**：1min 100000 协议包
- **expected**：超过阈值（10000）后限流 + 临时封禁 IP 5min
- **notes**：注意"限流" vs "DDoS"——DDoS 需 WAF 配合

### TP-010（WEAK_NET_RATE_LIMIT）：每日领取上限
- **scenario**：场景 10
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：每日奖励上限 10 次
- **test_data**：脚本 1min 领取 10000 次
- **expected**：第 1-10 次成功，11+ 返回 ERR_DAILY_LIMIT；触发脚本检测 + 封号
- **notes**：注意"日上限" vs "次上限"——日上限是按天累计

### TP-011（WEAK_NET_RATE_LIMIT）：未完成操作缓存重发
- **scenario**：场景 11
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：玩家在断网前点击"购买"
- **test_data**：网络断开 10min 后恢复
- **expected**：pending_queue 中的操作自动重发（幂等），玩家收到购买结果通知
- **notes**：注意"重发" vs "重复扣款"——必须幂等

### TP-012（WEAK_NET_RATE_LIMIT）：业务失败资源回滚
- **scenario**：场景 12
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：玩家购买商品，金币已扣
- **test_data**：扣款后发货失败
- **expected**：事务回滚，金币退还；玩家无损失
- **notes**：注意"回滚" vs "补偿"——回滚是同一事务，补偿是异步补救

### TP-013（WEAK_NET_RATE_LIMIT）：数据半写检测
- **scenario**：场景 4 扩展
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：业务涉及多个 DB 写
- **test_data**：第 1 个写成功，第 2 个写时断网
- **expected**：事务回滚，第 1 个写也回滚；玩家无数据半写
- **notes**：注意"事务" vs "补偿"——事务保证 ACID

### TP-014（WEAK_NET_RATE_LIMIT）：UI 不卡死
- **scenario**：场景 1 扩展
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：网络延迟 5s
- **test_data**：玩家点击"购买"
- **expected**：UI 显示 loading 状态，可取消；不卡死主线程
- **notes**：注意"卡死" vs "慢"——卡死是 ANR，慢是体验

### TP-015（WEAK_NET_RATE_LIMIT）：操作指令不丢失
- **scenario**：场景 4 扩展
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：玩家在断网前输入 10 个操作指令
- **test_data**：断网 10s 后恢复
- **expected**：10 个指令按顺序重发（重要操作），玩家无感知
- **notes**：注意"丢失" vs "延迟"——丢失是数据没了

### TP-016（WEAK_NET_RATE_LIMIT）：限流弹窗提示
- **scenario**：场景 7 扩展
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：玩家高频点击触发限流
- **test_data**：1s 内点击 50 次
- **expected**：弹窗"操作太频繁，请稍后再试"+ 5s 倒计时
- **notes**：注意"提示" vs "静默限流"——提示更友好

### TP-017（WEAK_NET_RATE_LIMIT）：非法重复请求丢弃
- **scenario**：场景 8 扩展
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：同一玩家 1s 发 100 个相同请求
- **test_data**：100 个相同 claim_reward
- **expected**：第 1 个处理，2-100 个直接丢弃（不返回错误，避免被利用）
- **notes**：注意"丢弃" vs "拒绝"——丢弃更安全（不暴露服务端状态）

### TP-018（WEAK_NET_RATE_LIMIT）：防雪崩保护
- **scenario**：场景 9 扩展
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：上游服务慢响应
- **test_data**：下游并发请求
- **expected**：熔断器触发 + 快速失败 + 限流 + 不拖垮下游
- **notes**：注意"雪崩" vs "限流"——雪崩是级联故障

### TP-019（WEAK_NET_RATE_LIMIT）：网关重连提示
- **scenario**：场景 5 扩展
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：网关断开
- **test_data**：玩家发请求
- **expected**：客户端显示"正在重连"+ 进度条；不影响其他功能
- **notes**：注意"提示" vs "静默"——提示更友好

### TP-020（WEAK_NET_RATE_LIMIT）：冷却限制
- **scenario**：场景 7 扩展
- **module**：`WEAK_NET_RATE_LIMIT`
- **precondition**：玩家点击"购买"按钮
- **test_data**：1s 内点击 100 次
- **expected**：客户端 1s 冷却（按钮置灰），服务端独立校验
- **notes**：注意"冷却" vs "限流"——冷却是单点，限流是全局

---

## 3. 边界陷阱

### 边界 1：vs AUX B（网络层底层）
- **混淆点**："断网重连" 看似 SPECIAL → 实际 B 测"底层网络重连框架"（TCP/HTTP 重试），C 测"业务容错"（业务数据如何不丢）
- **判定规则**：测"网络 SDK 底层（重连/心跳/超时）" → 归 AUX B；测"业务容错（重发/回滚/限流）" → 归 SPECIAL C
- **实例**：TCP 断线重连 → 归 B；业务请求重发不重复扣款 → 归 C

### 边界 2：vs BIZ（业务异常处理）
- **混淆点**："业务失败回滚" 看似 BIZ → 实际 BIZ 测"业务正常失败处理"（如购买失败提示），C 测"异常环境下的回滚"（弱网/断网）
- **判定规则**：测"正常业务流程失败" → 归 BIZ；测"异常环境（弱网/断网/限流）" → 归 SPECIAL C
- **实例**：库存不足购买失败 → 归 BIZ；弱网下购买超时重试 → 归 C

### 边界 3：vs SPECIAL B（反作弊去重）
- **混淆点**："重复发包" 看似 C → 实际 B 测"作弊去重"（业务层幂等），C 测"流量限流"（流量层限速）
- **判定规则**：测"作弊行为（脚本/外挂）" → 归 SPECIAL B；测"流量限流（防雪崩/防 DDoS）" → 归 SPECIAL C
- **实例**：脚本批量发包 → 归 B；正常玩家网络抖动重发 → 归 C

### 边界 4：vs LINK（跨服通道）
- **混淆点**："跨服通道断开" 看似跨服 → 实际 LINK 测"跨服数据同步业务"（正常业务），C 测"跨服通道容错"（异常环境）
- **判定规则**：测"跨服数据正常同步/时序一致性" → 归 LINK；测"跨服通道异常（断/重连/超时）" → 归 SPECIAL C
- **实例**：跨服拍卖行出价 → 归 LINK；跨服通道断开重连 → 归 C

---

## 4. 验证证据

### 视觉证据
- 弱网时"网络较慢"提示弹窗
- 断网时"网络异常"提示
- 限流时"操作太频繁"弹窗
- 购买中 loading 状态
- 重连进度条

### 日志证据
- `network.timeout` 关键词：请求超时
- `network.reconnect` 关键词：网络重连
- `network.switch` 关键词：网络切换
- `ratelimit.exceeded` 关键词：限流触发
- `ratelimit.banned` 关键词：IP 临时封禁
- `pending.queue` 关键词：未完成操作缓存
- `transaction.rollback` 关键词：事务回滚
- `circuit.breaker` 关键词：熔断器触发

### 数据证据
- `network_log` 表记录每次网络异常 + 重连
- `ratelimit_log` 表记录每次限流 + 触发原因
- `pending_queue` 表记录断网期间的操作
- DB 事务回滚后无半写数据
- 玩家资源在业务失败后无变化

### 性能证据
- 网络重连耗时 < 3s
- 业务失败回滚耗时 < 1s
- 限流响应延迟 < 50ms
- 熔断器触发耗时 < 100ms
- 弱网下 UI 响应帧率 > 30 FPS
