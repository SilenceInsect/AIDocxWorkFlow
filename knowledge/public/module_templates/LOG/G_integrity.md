# G. 日志完整性校验

> **子类代码**：`LOG_INTEGRITY`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §7「日志完整性校验（业务校验规则）」
>
> **测什么**：日志链路完整（跨业务 trace_id 串联）、幂等校验（重复操作日志完整）、一致性校验（日志数值 = DB 数值）、丢失校验（断线/宕机/切后台日志本地缓存重连补传）。
> **不测什么**：业务逻辑（归 BIZ）、业务审计链（归 BIZ-I）、资产流水（归 B）、链路追踪 ID（归 I）、底层存储（归 F）。
> **与其他子类的差异**：G 关注"日志**完整性/一致性**校验"——B 关注"资产对账"，I 关注"链路追溯"，F 关注"存储规范"。

---

## 1. 典型场景

### 场景 1：充值-发奖-扣资源链路
- 业务背景：完整充值流程
- 涉及数据：3 步业务
- 触发动作：玩家充值
- 验证点：3 步日志 trace_id 一致

### 场景 2：购买-扣款-发货链路
- 业务背景：商城购买
- 涉及数据：扣款 + 发货
- 触发动作：购买
- 验证点：扣款 + 发货日志串联

### 场景 3：合成-扣材料-加产物
- 业务背景：道具合成
- 涉及数据：扣 + 加
- 触发动作：合成
- 验证点：双向日志串联

### 场景 4：交易-双方-双向
- 业务背景：A 卖 B
- 涉及数据：双方
- 触发动作：交易
- 验证点：A 流水 + B 流水 trade_id 一致

### 场景 5：重复购买幂等
- 业务背景：玩家点购买 5 次
- 涉及数据：重复
- 触发动作：5 次点击
- 验证点：日志去重或 5 次完整

### 场景 6：操作中断幂等
- 业务背景：操作中断重试
- 涉及数据：中断
- 触发动作：重试
- 验证点：日志幂等

### 场景 7：日志与 DB 一致
- 业务背景：玩家钻石 100
- 涉及数据：日志 + DB
- 触发动作：购买后
- 验证点：日志钻石 = DB 钻石

### 场景 8：日志与配置一致
- 业务背景：商品价格 100
- 涉及数据：日志 + 配置
- 触发动作：购买
- 验证点：日志价格 = 配置

### 场景 9：日志与协议一致
- 业务背景：协议返回 amount=100
- 涉及数据：日志 + 协议
- 触发动作：回调
- 验证点：日志 amount = 协议

### 场景 10：断线日志缓存
- 业务背景：断线
- 涉及数据：断网
- 触发动作：本地缓存
- 验证点：本地缓存不丢

### 场景 11：重连补传
- 业务背景：重连
- 涉及数据：补传
- 触发动作：重连
- 验证点：补传不丢

### 场景 12：宕机恢复补传
- 业务背景：宕机
- 涉及数据：宕机
- 触发动作：恢复
- 验证点：补传

### 场景 13：切后台补传
- 业务背景：切后台
- 涉及数据：切后台
- 触发动作：回前台
- 验证点：补传

### 场景 14：日志事务回滚
- 业务背景：业务回滚
- 涉及数据：回滚
- 触发动作：业务回滚
- 验证点：反向日志

### 场景 15：补传幂等
- 业务背景：补传 2 次
- 涉及数据：补传
- 触发动作：重试
- 验证点：去重

### 场景 16：补传顺序
- 业务背景：补传 100 条
- 涉及数据：顺序
- 触发动作：补传
- 验证点：按时间顺序

### 场景 17：补传失败处理
- 业务背景：补传失败
- 涉及数据：失败
- 触发动作：补传
- 验证点：再次缓存

### 场景 18：日志分片
- 业务背景：1GB 日志
- 涉及数据：分片
- 触发动作：分片
- 验证点：分片完整

### 场景 19：跨日对账
- 业务背景：跨日
- 涉及数据：跨日
- 触发动作：对账
- 验证点：跨日一致

### 场景 20：跨服链路
- 业务背景：跨服交易
- 涉及数据：跨服
- 触发动作：跨服
- 验证点：双服链路一致

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_INTEGRITY）：充值链路
- **scenario**：场景 1
- **module**：`LOG_INTEGRITY`
- **precondition**：玩家充值 100 元
- **test_data**：观察 3 步日志
- **expected**：3 步日志 `trace_id=xxx` 一致
- **notes**：注意"trace_id"vs"order_id"

### TP-002（LOG_INTEGRITY）：购买链路
- **scenario**：场景 2
- **module**：`LOG_INTEGRITY`
- **precondition**：购买 50 钻道具
- **test_data**：观察
- **expected**：扣款 + 发货日志 `tx_id=xxx` 一致
- **notes**：注意"扣款"vs"发货"

### TP-003（LOG_INTEGRITY）：合成双向
- **scenario**：场景 3
- **module**：`LOG_INTEGRITY`
- **precondition**：3 铁矿合 1 铁锭
- **test_data`：观察
- **expected**：双向日志 `compose_id=xxx` 一致
- **notes**：注意"双向"原子性

### TP-004（LOG_INTEGRITY）：交易双向
- **scenario**：场景 4
- **module**：`LOG_INTEGRITY`
- **precondition**：A 卖 B
- **test_data**：观察
- **expected**：双方日志 `trade_id=xxx` 一致
- **notes**：注意"双服"或"同服"

### TP-005（LOG_INTEGRITY）：重复幂等
- **scenario**：场景 5
- **module**：`LOG_INTEGRITY`
- **precondition**：玩家 5 次购买
- **test_data**：1s 5 次
- **expected**：日志去重、仅 1 条业务日志
- **notes**：注意"业务幂等"vs"日志去重"

### TP-006（LOG_INTEGRITY）：操作重试幂等
- **scenario**：场景 6
- **module**：`LOG_INTEGRITY`
- **precondition**：操作重试
- **test_data`：客户端重试
- **expected**：服务端幂等、日志去重
- **notes**：注意"幂等键"

### TP-007（LOG_INTEGRITY）：日志 vs DB
- **scenario**：场景 7
- **module**：`LOG_INTEGRITY`
- **precondition**：玩家购买后
- **test_data`：对比
- **expected**：日志钻石 = DB 钻石
- **notes**：注意"主从延迟"

### TP-008（LOG_INTEGRITY）：日志 vs 配置
- **scenario**：场景 8
- **module**：`LOG_INTEGRITY`
- **precondition**：商品价格 100
- **test_data`：购买
- **expected**：日志价格 = 配置
- **notes**：注意"热更"+"价格"

### TP-009（LOG_INTEGRITY）：日志 vs 协议
- **scenario**：场景 9
- **module**：`LOG_INTEGRITY`
- **precondition**：协议返回 amount=100
- **test_data**：回调
- **expected**：日志 amount = 协议
- **notes**：注意"协议"vs"日志"

### TP-010（LOG_INTEGRITY）：断线缓存
- **scenario**：场景 10
- **module**：`LOG_INTEGRITY`
- **precondition**：断线
- **test_data`：本地缓存
- **expected**：本地缓存 < 1MB
- **notes**：注意"本地"vs"上报"

### TP-011（LOG_INTEGRITY）：重连补传
- **scenario**：场景 11
- **module**：`LOG_INTEGRITY`
- **precondition**：断线 + 本地缓存
- **test_data`：重连
- **expected**：本地缓存全量补传
- **notes**：注意"补传"vs"丢"

### TP-012（LOG_INTEGRITY）：宕机恢复补传
- **scenario**：场景 12
- **module**：`LOG_INTEGRITY`
- **precondition**：宕机
- **test_data`：恢复
- **expected**：补传
- **notes**：注意"宕机"vs"断线"

### TP-013（LOG_INTEGRITY）：切后台补传
- **scenario**：场景 13
- **module**：`LOG_INTEGRITY`
- **precondition**：切后台
- **test_data`：回前台
- **expected**：补传
- **notes**：注意"切后台"vs"断线"

### TP-014（LOG_INTEGRITY）：事务回滚反向
- **scenario**：场景 14
- **module**：`LOG_INTEGRITY`
- **precondition**：业务回滚
- **test_data`：观察
- **expected**：反向日志
- **notes**：注意"正向"vs"反向"

### TP-015（LOG_INTEGRITY）：补传去重
- **scenario**：场景 15
- **module**：`LOG_INTEGRITY`
- **precondition**：补传 2 次
- **test_data`：观察
- **expected**：去重
- **notes**：注意"去重键"

### TP-016（LOG_INTEGRITY）：补传顺序
- **scenario**：场景 16
- **module**：`LOG_INTEGRITY`
- **precondition**：补传 100 条
- **test_data**：观察
- **expected**：按时间顺序
- **notes**：注意"顺序"vs"乱序"

### TP-017（LOG_INTEGRITY）：补传失败
- **scenario**：场景 17
- **module**：`LOG_INTEGRITY`
- **precondition**：补传失败
- **test_data**：观察
- **expected**：再次本地缓存
- **notes**：注意"再次"vs"丢"

### TP-018（LOG_INTEGRITY）：分片完整
- **scenario**：场景 18
- **module**：`LOG_INTEGRITY`
- **precondition**：1GB 日志
- **test_data`：分片
- **expected**：分片完整
- **notes**：注意"分片"vs"缺"

### TP-019（LOG_INTEGRITY）：跨日对账
- **scenario**：场景 19
- **module**：`LOG_INTEGRITY`
- **precondition**：跨日
- **test_data`：对账
- **expected**：跨日一致
- **notes**：注意"跨日"+"业务日"

### TP-020（LOG_INTEGRITY）：跨服链路
- **scenario**：场景 20
- **module**：`LOG_INTEGRITY`
- **precondition**：跨服交易
- **test_data`：观察
- **expected`：双服链路一致
- **notes**：注意"跨服"+"trace_id"

### TP-021（LOG_INTEGRITY）：补传完整性
- **scenario**：场景 11
- **module**：`LOG_INTEGRITY`
- **precondition**：断线前 100 笔操作
- **test_data`：重连
- **expected**：100 笔全补
- **notes**：注意"全"vs"丢"

### TP-022（LOG_INTEGRITY）：跨业务日
- **scenario**：场景 19
- **module**：`LOG_INTEGRITY`
- **precondition**：23:59 触发、0:01 完成
- **test_data`：观察
- **expected**：日志归属当天
- **notes**：注意"业务日"vs"自然日"

### TP-023（LOG_INTEGRITY）：日志 vs 业务对象
- **scenario**：场景 7
- **module**：`LOG_INTEGRITY`
- **precondition**：购买后
- **test_data`：对比
- **expected**：日志 = 业务对象
- **notes**：注意"对象"vs"DB"

### TP-024（LOG_INTEGRITY）：补传超时
- **scenario**：场景 17
- **module**：`LOG_INTEGRITY`
- **precondition**：补传超时
- **test_data**：观察
- **expected`：超时处理
- **notes**：注意"超时"vs"丢"

### TP-025（LOG_INTEGRITY）：日志校验定时
- **scenario**：场景 19
- **module**：`LOG_INTEGRITY`
- **precondition`：每天对账
- **test_data`：定时
- **expected`：对账报告
- **notes**：注意"定时"vs"实时"

---

## 3. 边界陷阱

### 边界 1：vs BIZ-I. 业务审计
- **混淆点**：「审计"完整性"」——BIZ-I 测业务落点、G 测一致性
- **判定规则**：测"业务侧落点" → BIZ-I；测"日志链路完整性" → G
- **实例**：购买日志格式 → BIZ-I；链路串联 → G

### 边界 2：vs I. 链路追踪
- **混淆点**：「trace_id"完整"」——I 测 trace、G 测完整
- **判定规则**：测"trace_id 串联" → I；测"日志完整不丢" → G
- **实例**：trace_id 串联 → I；日志补传 → G

### 边界 3：vs B. 资产流水
- **混淆点**：「资产"对账"」——B 测对账、G 测一致
- **判定规则**：测"资产正负匹配" → B；测"日志 = DB" → G
- **实例**：资产对账 → B；日志 vs DB → G

### 边界 4：vs F. 存储规范
- **混淆点**：「日志"存储"」——F 测存储、G 测一致
- **判定规则**：测"日志存储" → F；测"日志完整性" → G
- **实例**：日志分片 → F；补传 → G

### 边界 5：vs A. 行为埋点
- **混淆点**：「埋点"完整"」——A 测触发、G 测完整
- **判定规则**：测"埋点业务规则" → A；测"埋点完整性" → G
- **实例**：购买埋点 → A；埋点不丢 → G

---

## 4. 验证证据

### 视觉证据
- 链路追踪截图（trace_id 全链路）
- 补传完成截图

### 日志证据
- `trace_id=xxx` 链路串联
- `补传=success count=N`
- `RECONCILE diff=0`
- `REPLAY log_id list`
- `REVERSE tx_id`

### 数据证据
- 链路追踪表 `trace.trace_id, step, log_id, status`
- 完整性校验报告 `integrity_report.diff_count, diff_detail`
- 补传成功率 = 100%
- 补传延迟 < 1min
- 跨服链路一致性

### 性能证据
- 链路追踪开销 < 1ms
- 补传延迟 < 1min
- 一致性校验 < 30s
- 跨服链路同步 < 1s
- 完整性报告生成 < 1min
