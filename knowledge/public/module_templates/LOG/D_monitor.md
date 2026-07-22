# D. 服务监控埋点

> **子类代码**：`LOG_MONITOR`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §4「服务监控埋点（服务侧运维监控）」
>
> **测什么**：服务性能埋点（接口耗时/并发/队列/DB/缓存）、业务指标埋点（在线/付费转化/活动参与/消耗/流失）、异常监控埋点（接口报错/DB失败/超时/跨服失败/限流）、告警埋点（资源耗尽/负载过高/异常充值/作弊）。
> **不测什么**：业务逻辑（归 BIZ）、底层监控工具（归 AUX K）、服务性能压测（归 SPECIAL）、业务操作日志（归 C）、资产流水（归 B）。
> **与其他子类的差异**：D 关注"**服务侧运维监控**埋点"——A 关注"玩家行为埋点"，C 关注"操作日志"，B 关注"资产对账"。

---

## 1. 典型场景

### 场景 1：接口耗时埋点
- 业务背景：商城购买接口
- 涉及数据：API P50/P99
- 触发动作：API 调用
- 验证点：埋点含 duration_ms

### 场景 2：并发量埋点
- 业务背景：1000 并发
- 涉及数据：QPS
- 触发动作：每请求
- 验证点：埋点含 concurrent_count

### 场景 3：队列堆积埋点
- 业务背景：消息队列堆积
- 涉及数据：队列深度
- 触发动作：定时采样
- 验证点：埋点含 queue_depth

### 场景 4：DB 读写耗时
- 业务背景：DB 查询
- 涉及数据：DB 耗时
- 触发动作：每次查询
- 验证点：埋点含 db_duration_ms

### 场景 5：缓存命中率
- 业务背景：Redis 缓存
- 涉及数据：命中率
- 触发动作：每次读写
- 验证点：埋点含 hit/miss

### 场景 6：在线人数
- 业务背景：1 万在线
- 涉及数据：CCU
- 触发动作：定时采样
- 验证点：埋点含 ccu

### 场景 7：付费转化率
- 业务背景：1000 玩家付费
- 涉及数据：付费率
- 触发动作：定时聚合
- 验证点：埋点含 pay_rate

### 场景 8：活动参与率
- 业务背景：春日活动
- 涉及数据：参与率
- 触发动作：定时聚合
- 验证点：埋点含 activity_join_rate

### 场景 9：道具消耗总量
- 业务背景：血瓶消耗
- 涉及数据：消耗统计
- 触发动作：定时聚合
- 验证点：埋点含 item_consume_total

### 场景 10：流失节点
- 业务背景：玩家流失
- 涉及数据：流失 funnel
- 触发动作：触发流失
- 验证点：埋点含 churn_stage

### 场景 11：接口报错频次
- 业务背景：API 报错
- 涉及数据：错误计数
- 触发动作：每次报错
- 验证点：埋点含 error_count

### 场景 12：DB 失败
- 业务背景：DB 写失败
- 涉及数据：DB 错误
- 触发动作：DB 报错
- 验证点：埋点含 db_error_type

### 场景 13：超时请求
- 业务背景：API 5s 超时
- 涉及数据：超时
- 触发动作：超时
- 验证点：埋点含 timeout

### 场景 14：跨服同步失败
- 业务背景：跨服同步
- 涉及数据：同步失败
- 触发动作：同步失败
- 验证点：埋点含 cross_server_fail

### 场景 15：限流拦截
- 业务背景：玩家触发限流
- 涉及数据：限流
- 触发动作：被限流
- 验证点：埋点含 rate_limit_hit

### 场景 16：资源耗尽告警
- 业务背景：磁盘满
- 涉及数据：资源
- 触发动作：资源告警
- 验证点：埋点含 resource_alert

### 场景 17：服务负载过高
- 业务背景：CPU 95%
- 涉及数据：负载
- 触发动作：负载告警
- 验证点：埋点含 load_alert

### 场景 18：异常充值告警
- 业务背景：单玩家 1 分钟 5 笔充值
- 涉及数据：异常付费
- 触发动作：触发告警
- 验证点：埋点含 pay_alert

### 场景 19：高频作弊告警
- 业务背景：作弊检测
- 涉及数据：作弊
- 触发动作：触发告警
- 验证点：埋点含 cheat_alert

### 场景 20：聚合统计对账
- 业务背景：日终聚合
- 涉及数据：日活/付费
- 触发动作：定时聚合
- 验证点：埋点日报生成

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_MONITOR）：接口耗时埋点
- **scenario**：场景 1
- **module**：`LOG_MONITOR`
- **precondition**：商城购买接口
- **test_data**：`purchase_api()` 调用 1000 次
- **expected**：埋点 `API_PERF api=purchase duration_ms=X p50/p99`
- **notes**：注意"接口"vs"协议"

### TP-002（LOG_MONITOR）：并发量采样
- **scenario**：场景 2
- **module**：`LOG_MONITOR`
- **precondition**：1000 并发
- **test_data**：观察 1 分钟
- **expected**：埋点 `QPS api=purchase qps=1000`
- **notes**：注意"瞬时"vs"平均"

### TP-003（LOG_MONITOR）：队列堆积
- **scenario**：场景 3
- **module**：`LOG_MONITOR`
- **precondition**：消息队列 1 万条堆积
- **test_data**：观察
- **expected**：埋点 `QUEUE_DEPTH queue=async_reward depth=10000`
- **notes**：注意"堆积"vs"正常"

### TP-004（LOG_MONITOR）：DB 耗时
- **scenario**：场景 4
- **module**：`LOG_MONITOR`
- **precondition**：DB 查询
- **test_data**：`SELECT * FROM bag`
- **expected**：埋点 `DB_PERF sql=bag_select duration_ms=X`
- **notes**：注意"慢查询"阈值

### TP-005（LOG_MONITOR）：缓存命中
- **scenario**：场景 5
- **module**：`LOG_MONITOR`
- **precondition**：Redis 缓存
- **test_data**：1000 次读写
- **expected**：埋点 `CACHE_PERF key hit=N miss=M hit_rate=X`
- **notes**：注意"命中率"指标

### TP-006（LOG_MONITOR）：在线人数
- **scenario**：场景 6
- **module**：`LOG_MONITOR`
- **precondition**：1 万在线
- **test_data`：观察 1 分钟
- **expected`：埋点 `CCU ccu=10000 time`
- **notes**：注意"采样"频率

### TP-007（LOG_MONITOR）：付费转化率
- **scenario**：场景 7
- **module**：`LOG_MONITOR`
- **precondition**：1000 玩家付费
- **test_data`：1 天数据
- **expected`：埋点 `PAY_RATE active=10000 pay=1000 rate=10%`
- **notes**：注意"日"vs"周"vs"月"

### TP-008（LOG_MONITOR）：活动参与率
- **scenario**：场景 8
- **module**：`LOG_MONITOR`
- **precondition**：春日活动
- **test_data`：1 天数据
- **expected`：埋点 `ACTIVITY_JOIN activity=5 active=10000 join=8000 rate=80%`
- **notes**：注意"参与"vs"完成"

### TP-009（LOG_MONITOR）：消耗统计
- **scenario**：场景 9
- **module**：`LOG_MONITOR`
- **precondition**：血瓶消耗
- **test_data`：1 天数据
- **expected`：埋点 `ITEM_CONSUME item=blood total=1000000`
- **notes**：注意"消耗"vs"产出"

### TP-010（LOG_MONITOR）：流失节点
- **scenario**：场景 10
- **module**：`LOG_MONITOR`
- **precondition**：玩家 7 天未登录
- **test_data`：`churn_detect(player_id, stage=lvl_10)`
- **expected`：埋点 `CHURN player_id stage=10`
- **notes**：注意"节点"+"funnel"

### TP-011（LOG_MONITOR）：接口报错
- **scenario**：场景 11
- **module**：`LOG_MONITOR`
- **precondition**：API 报错
- **test_data`：`purchase_api()` 失败 100 次
- **expected`：埋点 `API_ERROR api=purchase code=X count=100`
- **notes**：注意"4xx"vs"5xx"+"错误码"

### TP-012（LOG_MONITOR）：DB 失败
- **scenario**：场景 12
- **module**：`LOG_MONITOR`
- **precondition**：DB 写失败
- **test_data`：`db_write()` 失败
- **expected`：埋点 `DB_ERROR type=timeout count=N`
- **notes**：注意"超时"vs"约束"+"死锁"

### TP-013（LOG_MONITOR）：超时请求
- **scenario**：场景 13
- **module**：`LOG_MONITOR`
- **precondition`：API 5s 超时
- **test_data`：`api_timeout()`
- **expected`：埋点 `TIMEOUT api=purchase duration=5000ms`
- **notes**：注意"超时"vs"慢"

### TP-014（LOG_MONITOR）：跨服同步失败
- **scenario**：场景 14
- **module**：`LOG_MONITOR`
- **precondition**：跨服同步失败
- **test_data`：`cross_sync(from=A, to=B)` 失败
- **expected`：埋点 `CROSS_FAIL from=A to=B reason=timeout`
- **notes**：注意"跨服"+"重试"

### TP-015（LOG_MONITOR）：限流拦截
- **scenario**：场景 15
- **module**：`LOG_MONITOR`
- **precondition`：玩家 1s 100 次
- **test_data`：被限流
- **expected`：埋点 `RATE_LIMIT api=purchase player_id limit=10/s`
- **notes**：注意"限流"vs"业务拦截"

### TP-016（LOG_MONITOR）：资源耗尽告警
- **scenario**：场景 16
- **module**：`LOG_MONITOR`
- **precondition**：磁盘 100%
- **test_data`：观察
- **expected`：埋点 `RESOURCE_ALERT disk usage=100%`
- **notes**：注意"资源"+"阈值"

### TP-017（LOG_MONITOR）：负载告警
- **scenario**：场景 17
- **module**：`LOG_MONITOR`
- **precondition**：CPU 95%
- **test_data`：观察
- **expected`：埋点 `LOAD_ALERT cpu=95% memory=80%`
- **notes**：注意"持续"vs"瞬时"

### TP-018（LOG_MONITOR）：异常充值告警
- **scenario**：场景 18
- **module**：`LOG_MONITOR`
- **precondition`：单玩家 1 分钟 5 笔
- **test_data`：`pay_alert(player_id, count=5)`
- **expected`：埋点 `PAY_ALERT player_id type=high_freq`
- **notes**：注意"黑卡"vs"误操作"

### TP-019（LOG_MONITOR）：作弊告警
- **scenario**：场景 19
- **module**：`LOG_MONITOR`
- **precondition**：检测到外挂
- **test_data`：`cheat_detect(player_id, type=aimbot)`
- **expected`：埋点 `CHEAT_ALERT player_id type`
- **notes**：注意"检测"vs"封号"

### TP-020（LOG_MONITOR）：日活聚合
- **scenario**：场景 20
- **module**：`LOG_MONITOR`
- **precondition**：1 天 1000 玩家登录
- **test_data`：定时聚合
- **expected`：埋点 `DAU daily=1000 new=100 active=900`
- **notes**：注意"日活"vs"月活"vs"周活"

### TP-021（LOG_MONITOR）：业务指标对账
- **scenario**：场景 20
- **module**：`LOG_MONITOR`
- **precondition**：日活 + 付费
- **test_data`：聚合
- **expected`：日活 = 付费 ÷ 付费率
- **notes**：注意"对账"指标一致性

### TP-022（LOG_MONITOR）：分服监控
- **scenario**：场景 6
- **module**：`LOG_MONITOR`
- **precondition**：10 服
- **test_data`：观察
- **expected`：每服 1 条 CCU 埋点
- **notes**：注意"分服"+"标签"

### TP-023（LOG_MONITOR）：告警降噪
- **scenario**：场景 16
- **module**：`LOG_MONITOR`
- **precondition**：磁盘满持续 1 小时
- **test_data`：观察
- **expected`：1 条告警、后续降频
- **notes**：注意"告警风暴"+"降噪"

### TP-024（LOG_MONITOR）：监控大盘
- **scenario**：场景 20
- **module**：`LOG_MONITOR`
- **precondition**：全量指标
- **test_data`：查看监控大盘
- **expected`：实时显示、5min 刷新
- **notes**：注意"实时"vs"采样"

### TP-025（LOG_MONITOR）：分位数统计
- **scenario**：场景 1
- **module**：`LOG_MONITOR`
- **precondition**：1000 次 API
- **test_data`：观察
- **expected**：埋点含 p50/p95/p99/max
- **notes**：注意"长尾"问题

---

## 3. 边界陷阱

### 边界 1：vs A. 行为埋点
- **混淆点**：「玩家"行为"」——A 测玩家行为、D 测服务指标
- **判定规则**：测"玩家做了什么" → A；测"服务性能/业务指标" → D
- **实例**：玩家登录埋点 → A；CCU 统计 → D

### 边界 2：vs C. 操作日志
- **混淆点**：「操作"日志"」——C 测单次操作、D 测聚合
- **判定规则**：测"单次操作日志" → C；测"操作聚合指标" → D
- **实例**：领奖操作 → C；领奖率统计 → D

### 边界 3：vs B. 资产流水
- **混淆点**：「消耗"统计"」——B 测单笔流水、D 测总量
- **判定规则**：测"单笔资产变动" → B；测"资产消耗总量" → D
- **实例**：单笔血瓶消耗 → B；血瓶消耗总量 → D

### 边界 4：vs AUX K. 性能工具
- **混淆点**：「性能"埋点"」——D 测业务指标、AUX K 测工具
- **判定规则**：测"业务性能指标" → D；测"通用性能监控组件" → AUX K
- **实例**：接口 P99 业务埋点 → D；FPS 监控组件 → AUX K

### 边界 5：vs SPECIAL 性能
- **混淆点**：「性能"压测"」——D 测监控、SPECIAL 测压测
- **判定规则**：测"性能监控埋点" → D；测"性能压测场景" → SPECIAL
- **实例**：API P99 埋点 → D；高并发压测 → SPECIAL

---

## 4. 验证证据

### 视觉证据
- 监控大盘截图（CCU/QPS/P99）
- 告警列表截图

### 日志证据
- `API_PERF/QPS/DB_PERF/CACHE_PERF` 性能埋点
- `CCU/DAU/PAY_RATE/CHURN` 业务指标
- `API_ERROR/DB_ERROR/TIMEOUT/CROSS_FAIL/RATE_LIMIT` 异常监控
- `RESOURCE_ALERT/LOAD_ALERT/PAY_ALERT/CHEAT_ALERT` 告警

### 数据证据
- 性能指标表 `metric.api, p50, p99, max, time`
- 业务指标表 `metric.name, value, time, dim`
- 告警表 `alert.type, level, time, status`
- 监控大盘 5min 刷新
- 告警降噪规则

### 性能证据
- 监控埋点开销 < 5ms/请求
- 监控大盘 5min 刷新
- 告警延迟 < 1min
- 告警降噪 < 1 条/小时
- 业务指标聚合 < 1min
