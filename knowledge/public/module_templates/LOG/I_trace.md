# I. 线上问题溯源日志

> **子类代码**：`LOG_TRACE`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §9「线上问题溯源日志（补充链路追踪能力）」
>
> **测什么**：全链路 TraceID（端→网关→逻辑服→DB/跨服/支付）、上下文快照（配置/玩家/网络/并发）、检索支持（按角色/时间/事件/订单号检索+导出）。
> **不测什么**：日志完整性（归 G）、业务审计（归 BIZ-I）、跨服务数据同步（归 LINK）、业务协议（归 BIZ C）。
> **与其他子类的差异**：I 关注"**全链路追踪 & 溯源**"——A 关注"行为埋点"，G 关注"完整性"，B 关注"对账"。

---

## 1. 典型场景

### 场景 1：客户端 trace
- 业务背景：玩家购买
- 涉及数据：客户端 trace
- 触发动作：购买
- 验证点：客户端 trace_id 生成

### 场景 2：网关 trace
- 业务背景：购买请求
- 涉及数据：网关
- 触发动作：网关接收
- 验证点：trace_id 透传

### 场景 3：逻辑服 trace
- 业务背景：业务处理
- 涉及数据：逻辑服
- 触发动作：处理
- 验证点：trace_id 透传

### 场景 4：DB trace
- 业务背景：DB 写
- 涉及数据：DB
- 触发动作：DB 写入
- 验证点：trace_id 透传到 DB

### 场景 5：跨服 trace
- 业务背景：跨服交易
- 涉及数据：跨服
- 触发动作：跨服
- 验证点：双服 trace_id 一致

### 场景 6：第三方支付 trace
- 业务背景：支付
- 涉及数据：支付
- 触发动作：支付
- 验证点：trace_id 透传到支付

### 场景 7：上下文 - 配置
- 业务背景：异常时
- 涉及数据：配置
- 触发动作：异常
- 验证点：快照配置

### 场景 8：上下文 - 玩家
- 业务背景：异常
- 涉及数据：玩家
- 触发动作：异常
- 验证点：玩家状态

### 场景 9：上下文 - 网络
- 业务背景：异常
- 涉及数据：网络
- 触发动作：异常
- 验证点：网络参数

### 场景 10：上下文 - 并发
- 业务背景：异常
- 涉及数据：并发
- 触发动作：异常
- 验证点：并发环境

### 场景 11：按角色检索
- 业务背景：问题定位
- 涉及数据：player_id
- 触发动作：检索
- 验证点：返回日志

### 场景 12：按时间检索
- 业务背景：问题时间
- 涉及数据：time
- 触发动作：检索
- 验证点：返回

### 场景 13：按事件检索
- 业务背景：事件
- 涉及数据：event
- 触发动作：检索
- 验证点：返回

### 场景 14：按订单号检索
- 业务背景：订单
- 涉及数据：order_id
- 触发动作：检索
- 验证点：返回

### 场景 15：检索导出
- 业务背景：复盘
- 涉及数据：导出
- 触发动作：导出
- 验证点：CSV/JSON

### 场景 16：跨服务检索
- 业务背景：跨服务
- 涉及数据：跨服务
- 触发动作：检索
- 验证点：合并

### 场景 17：trace 索引
- 业务背景：性能
- 涉及数据：索引
- 触发动作：检索
- 验证点：< 1s

### 场景 18：trace 聚合
- 业务背景：聚合
- 涉及数据：trace
- 触发动作：聚合
- 验证点：trace 详情

### 场景 19：trace 异常标记
- 业务背景：异常
- 涉及数据：异常
- 触发动作：标记
- 验证点：trace 标红

### 场景 20：trace 仪表盘
- 业务背景：可视化
- 涉及数据：trace
- 触发动作：查看
- 验证点：可视化

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_TRACE）：客户端 trace
- **scenario**：场景 1
- **module**：`LOG_TRACE`
- **precondition**：购买
- **test_data`：观察
- **expected**：客户端生成 `trace_id`
- **notes**：注意"生成"vs"接收"

### TP-002（LOG_TRACE）：网关透传
- **scenario**：场景 2
- **module**：`LOG_TRACE`
- **precondition**：网关接收
- **test_data`：观察
- **expected**：trace_id 透传
- **notes**：注意"网关"+"透传"

### TP-003（LOG_TRACE）：逻辑服透传
- **scenario**：场景 3
- **module**：`LOG_TRACE`
- **precondition**：业务处理
- **test_data`：观察
- **expected`：trace_id 透传
- **notes**：注意"逻辑"vs"网关"

### TP-004（LOG_TRACE）：DB 透传
- **scenario**：场景 4
- **module**：`LOG_TRACE`
- **precondition**：DB 写
- **test_data`：观察
- **expected`：trace_id 写入 DB
- **notes**：注意"DB"+"应用日志"

### TP-005（LOG_TRACE）：跨服 trace
- **scenario**：场景 5
- **module**：`LOG_TRACE`
- **precondition**：跨服交易
- **test_data`：观察
- **expected`：双服 trace_id 一致
- **notes**：注意"跨服"+"一致"

### TP-006（LOG_TRACE）：支付 trace
- **scenario**：场景 6
- **module**：`LOG_TRACE`
- **precondition**：支付
- **test_data`：观察
- **expected`：trace_id 传给支付
- **notes**：注意"支付"+"回调"

### TP-007（LOG_TRACE）：上下文 - 配置
- **scenario**：场景 7
- **module**：`LOG_TRACE`
- **precondition**：异常
- **test_data`：观察
- **expected`：快照配置
- **notes**：注意"快照"vs"实时"

### TP-008（LOG_TRACE）：上下文 - 玩家
- **scenario**：场景 8
- **module**：`LOG_TRACE`
- **precondition**：异常
- **test_data`：观察
- **expected`：玩家状态快照
- **notes**：注意"状态"+"快照"

### TP-009（LOG_TRACE）：上下文 - 网络
- **scenario**：场景 9
- **module**：`LOG_TRACE`
- **precondition**：异常
- **test_data`：观察
- **expected`：网络参数快照
- **notes**：注意"网络"+"延迟"

### TP-010（LOG_TRACE）：上下文 - 并发
- **scenario**：场景 10
- **module**：`LOG_TRACE`
- **precondition**：异常
- **test_data`：观察
- **expected`：并发环境
- **notes**：注意"并发"+"线程"

### TP-011（LOG_TRACE）：按角色检索
- **scenario**：场景 11
- **module**：`LOG_TRACE`
- **precondition`：问题定位
- **test_data`：`query(player_id, 1day)`
- **expected`：返回所有相关 trace
- **notes**：注意"角色"vs"账号"

### TP-012（LOG_TRACE）：按时间检索
- **scenario**：场景 12
- **module**：`LOG_TRACE`
- **precondition`：问题时间
- **test_data`：`query(time_range)`
- **expected`：返回
- **notes**：注意"时间"+"窗口"

### TP-013（LOG_TRACE）：按事件检索
- **scenario**：场景 13
- **module**：`LOG_TRACE`
- **precondition**：事件
- **test_data`：`query(event=login)`
- **expected`：返回
- **notes**：注意"事件"vs"动作"

### TP-014（LOG_TRACE）：按订单号
- **scenario**：场景 14
- **module**：`LOG_TRACE`
- **precondition`：订单
- **test_data`：`query(order_id)`
- **expected`：返回订单全链路
- **notes**：注意"订单"+"支付"

### TP-015（LOG_TRACE）：检索导出
- **scenario**：场景 15
- **module**：`LOG_TRACE`
- **precondition**：复盘
- **test_data`：导出
- **expected`：CSV/JSON
- **notes**：注意"导出"+"格式"

### TP-016（LOG_TRACE）：跨服务合并
- **scenario**：场景 16
- **module**：`LOG_TRACE`
- **precondition`：跨服务
- **test_data`：检索
- **expected`：合并双服
- **notes**：注意"合并"+"视图"

### TP-017（LOG_TRACE）：trace 索引
- **scenario**：场景 17
- **module**：`LOG_TRACE`
- **precondition**：1 亿条
- **test_data`：检索
- **expected`：< 1s
- **notes**：注意"索引"+"性能"

### TP-018（LOG_TRACE）：trace 详情
- **scenario**：场景 18
- **module**：`LOG_TRACE`
- **precondition`：trace
- **test_data`：详情
- **expected`：trace 全链路详情
- **notes**：注意"详情"+"瀑布图"

### TP-019（LOG_TRACE）：异常标红
- **scenario**：场景 19
- **module**：`LOG_TRACE`
- **precondition**：异常
- **test_data`：观察
- **expected`：trace 标红
- **notes**：注意"标红"+"异常"

### TP-020（LOG_TRACE）：trace 仪表盘
- **scenario**：场景 20
- **module**：`LOG_TRACE`
- **precondition**：可视化
- **test_data`：查看
- **expected`：仪表盘
- **notes**：注意"可视化"+"甘特图"

### TP-021（LOG_TRACE）：trace 关联业务
- **scenario**：场景 18
- **module**：`LOG_TRACE`
- **precondition**：trace
- **test_data`：观察
- **expected`：关联业务日志
- **notes**：注意"trace"vs"业务"

### TP-022（LOG_TRACE）：trace 持续时间
- **scenario**：场景 1
- **module**：`LOG_TRACE`
- **precondition**：1 次操作
- **test_data`：观察
- **expected`：含 start/end/duration
- **notes**：注意"duration"vs"timestamp"

### TP-023（LOG_TRACE）：跨 trace 关联
- **scenario**：场景 5
- **module**：`LOG_TRACE`
- **precondition`：跨服
- **test_data`：观察
- **expected`：parent_trace_id 关联
- **notes**：注意"parent"vs"sibling"

### TP-024（LOG_TRACE）：trace 持久化
- **scenario**：场景 1
- **module**：`LOG_TRACE`
- **precondition**：trace
- **test_data`：观察
- **expected`：trace 持久化
- **notes**：注意"持久"vs"内存"

### TP-025（LOG_TRACE）：trace 采样
- **scenario**：场景 1
- **module**：`LOG_TRACE`
- **precondition**：1 万 trace
- **test_data`：观察
- **expected`：全量或采样
- **notes**：注意"采样"vs"全量"

---

## 3. 边界陷阱

### 边界 1：vs G. 完整性
- **混淆点**：「trace"完整"」——I 测追踪、G 测完整
- **判定规则**：测"trace 串联" → I；测"日志不丢" → G
- **实例**：trace_id 透传 → I；补传 → G

### 边界 2：vs BIZ-I. 业务审计
- **混淆点**：「业务"审计"」——BIZ-I 测业务侧、I 测追踪
- **判定规则**：测"业务落点" → BIZ-I；测"链路追溯" → I
- **实例**：购买日志 → BIZ-I；全链路 trace → I

### 边界 3：vs LINK 跨服务
- **混淆点**：「跨服务"trace"」——I 测追踪、LIN K 测跨服务
- **判定规则**：测"trace 透传" → I；测"跨服务数据" → LINK
- **实例**：trace_id 跨服 → I；跨服交易数据 → LINK

### 边界 4：vs A. 行为埋点
- **混淆点**：「trace"埋点"」——A 测埋点、I 测 trace
- **判定规则**：测"埋点业务" → A；测"trace_id" → I
- **实例**：购买埋点 → A；trace_id 串联 → I

### 边界 5：vs D. 监控
- **混淆点**：「trace"指标"」——D 测指标、I 测单 trace
- **判定规则**：测"trace 详情" → I；测"trace 聚合" → D
- **实例**：单 trace 详情 → I；trace P99 → D

---

## 4. 验证证据

### 视觉证据
- trace 详情截图（瀑布图）
- 跨服 trace 截图

### 日志证据
- `trace_id=xxx step=Y service=Z duration=Xms`
- `parent_trace_id=xxx child_trace_id=yyy`
- `CONTEXT_SNAPSHOT config player network thread`
- `TRACE_ERROR status=fail`

### 数据证据
- trace 表 `trace.trace_id, parent_id, step, service, duration, status`
- trace 索引（trace_id, parent_id, player_id, time）
- trace 采样率
- trace 异常率

### 性能证据
- trace 生成 < 1ms
- trace 检索 < 1s
- trace 详情加载 < 1s
- 跨服务 trace 合并 < 1s
- trace 仪表盘 5min 刷新
