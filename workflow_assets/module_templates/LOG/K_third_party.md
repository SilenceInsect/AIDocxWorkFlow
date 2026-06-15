# K. 第三方关联链路日志

> **子类代码**：`LOG_THIRD_PARTY`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §11「第三方关联链路日志（联动 LINK 模块）」（原定义完全缺失，新增）
>
> **测什么**：渠道登录回调日志、支付订单回调日志、外部 API 请求/响应日志、跨服同步收发日志、第三方数据同步完整日志。
> **不测什么**：第三方业务逻辑（归 LINK）、协议字段（归 BIZ C）、业务回调处理（归 BIZ H）、底层网络（归 AUX B）。
> **与其他子类的差异**：K 关注"**第三方交互全流程**日志"——A 关注"玩家行为"，B 关注"资产对账"，C 关注"内部操作日志"，J 关注"安全日志"。

> **与 LINK 模块的关系**：
> - **LINK** 测"第三方交互业务规则"——业务对接、跨服同步、回调幂等
> - **K** 测"第三方交互日志留痕"——所有第三方请求/响应/回调都有日志
> 重叠但不冲突：同一笔第三方交互 → LINK 校验"业务侧是否正确"，K 校验"日志是否完整"

---

## 1. 典型场景

### 场景 1：渠道登录
- 业务背景：微信登录
- 涉及数据：渠道回调
- 触发动作：渠道回调
- 验证点：日志留痕

### 场景 2：渠道登录失败
- 业务背景：登录失败
- 涉及数据：失败
- 触发动作：失败
- 验证点：日志留痕

### 场景 3：支付订单
- 业务背景：支付宝订单
- 涉及数据：订单
- 触发动作：支付
- 验证点：日志留痕

### 场景 4：支付回调
- 业务背景：支付宝回调
- 涉及数据：回调
- 触发动作：回调
- 验证点：日志留痕

### 场景 5：退款回调
- 业务背景：退款
- 涉及数据：退款
- 触发动作：退款
- 验证点：日志留痕

### 场景 6：外部 API 请求
- 业务背景：调用外部 API
- 涉及数据：API
- 触发动作：请求
- 验证点：日志留痕

### 场景 7：外部 API 响应
- 业务背景：API 响应
- 涉及数据：响应
- 触发动作：响应
- 验证点：日志留痕

### 场景 8：外部 API 失败
- 业务背景：API 失败
- 涉及数据：失败
- 触发动作：失败
- 验证点：日志留痕

### 场景 9：跨服同步发送
- 业务背景：服 A→服 B
- 涉及数据：发送
- 触发动作：发送
- 验证点：日志留痕

### 场景 10：跨服同步接收
- 业务背景：服 B 接收
- 涉及数据：接收
- 触发动作：接收
- 验证点：日志留痕

### 场景 11：第三方登录 token
- 业务背景：第三方 token
- 涉及数据：token
- 触发动作：登录
- 验证点：日志脱敏

### 场景 12：第三方用户信息
- 业务背景：拉取用户信息
- 涉及数据：信息
- 触发动作：拉取
- 验证点：日志留痕

### 场景 13：数据同步成功
- 业务背景：数据同步
- 涉及数据：同步
- 触发动作：成功
- 验证点：日志留痕

### 场景 14：数据同步失败
- 业务背景：数据同步失败
- 涉及数据：失败
- 触发动作：失败
- 验证点：日志留痕

### 场景 15：重试机制
- 业务背景：同步重试
- 涉及数据：重试
- 触发动作：重试
- 验证点：日志留痕

### 场景 16：第三方限流
- 业务背景：被第三方限流
- 涉及数据：限流
- 触发动作：限流
- 验证点：日志留痕

### 场景 17：第三方超时
- 业务背景：API 超时
- 涉及数据：超时
- 触发动作：超时
- 验证点：日志留痕

### 场景 18：第三方错误码
- 业务背景：第三方错误
- 涉及数据：错误码
- 触发动作：错误
- 验证点：日志留痕

### 场景 19：双向 trace
- 业务背景：第三方全链路
- 涉及数据：trace
- 触发动作：全链路
- 验证点：trace 串联

### 场景 20：第三方数据脱敏
- 业务背景：第三方数据
- 涉及数据：敏感
- 触发动作：写入
- 验证点：脱敏

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_THIRD_PARTY）：渠道登录成功
- **scenario**：场景 1
- **module**：`LOG_THIRD_PARTY`
- **precondition**：微信登录
- **test_data`：`wechat_login(code=xxx)`
- **expected`：日志 `THIRD_LOGIN channel=wechat code=xxx result=success`
- **notes**：注意"code"vs"token"

### TP-002（LOG_THIRD_PARTY）：渠道登录失败
- **scenario**：场景 2
- **module**：`LOG_THIRD_PARTY`
- **precondition**：登录失败
- **test_data`：失败
- **expected`：日志 `THIRD_LOGIN channel=wechat result=fail reason=invalid_code`
- **notes**：注意"失败"+"原因"

### TP-003（LOG_THIRD_PARTY）：支付订单
- **scenario**：场景 3
- **module**：`LOG_THIRD_PARTY`
- **precondition**：支付宝
- **test_data`：`alipay_order(100)`
- **expected`：日志 `THIRD_PAY channel=alipay amount=100 order_id=xxx`
- **notes**：注意"订单"vs"回调"

### TP-004（LOG_THIRD_PARTY）：支付回调
- **scenario**：场景 4
- **module**：`LOG_THIRD_PARTY`
- **precondition`：支付宝回调
- **test_data`：回调
- **expected`：日志 `THIRD_CALLBACK channel=alipay order_id=xxx status=success`
- **notes**：注意"回调"+"验签"

### TP-005（LOG_THIRD_PARTY）：退款回调
- **scenario**：场景 5
- **module**：`LOG_THIRD_PARTY`
- **precondition`：退款
- **test_data`：退款
- **expected`：日志 `THIRD_REFUND channel=alipay order_id=xxx`
- **notes**：注意"退款"vs"支付"

### TP-006（LOG_THIRD_PARTY）：外部 API 请求
- **scenario**：场景 6
- **module**：`LOG_THIRD_PARTY`
- **precondition**：调外部
- **test_data`：`api_request(url=xxx, params=xxx)`
- **expected`：日志 `THIRD_API url method params`
- **notes**：注意"请求"+"payload 脱敏"

### TP-007（LOG_THIRD_PARTY）：外部 API 响应
- **scenario**：场景 7
- **module**：`LOG_THIRD_PARTY`
- **precondition`：API 响应
- **test_data`：响应
- **expected`：日志 `THIRD_API response status body`
- **notes**：注意"响应"+"耗时"

### TP-008（LOG_THIRD_PARTY）：API 失败
- **scenario**：场景 8
- **module**：`LOG_THIRD_PARTY`
- **precondition**：API 失败
- **test_data`：失败
- **expected`：日志 `THIRD_API status=fail code reason`
- **notes**：注意"失败"+"错误码"

### TP-009（LOG_THIRD_PARTY）：跨服同步发送
- **scenario**：场景 9
- **module**：`LOG_THIRD_PARTY`
- **precondition**：A→B
- **test_data`：发送
- **expected`：日志 `CROSS_SYNC from=A to=B payload`
- **notes**：注意"发送"vs"接收"

### TP-010（LOG_THIRD_PARTY）：跨服同步接收
- **scenario**：场景 10
- **module**：`LOG_THIRD_PARTY`
- **precondition**：B 接收
- **test_data`：接收
- **expected`：日志 `CROSS_SYNC from=A to=B status=success`
- **notes**：注意"接收"vs"发送"

### TP-011（LOG_THIRD_PARTY）：第三方 token 脱敏
- **scenario**：场景 11
- **module**：`LOG_THIRD_PARTY`
- **precondition**：token
- **test_data`：写入
- **expected`：token 脱敏
- **notes**：注意"脱敏"vs"加密"

### TP-012（LOG_THIRD_PARTY）：第三方用户信息
- **scenario**：场景 12
- **module**：`LOG_THIRD_PARTY`
- **precondition**：拉取
- **test_data`：拉取
- **expected`：日志 `THIRD_USER_INFO channel=xxx fields`
- **notes**：注意"敏感字段"

### TP-013（LOG_THIRD_PARTY）：同步成功
- **scenario**：场景 13
- **module**：`LOG_THIRD_PARTY`
- **precondition**：数据同步
- **test_data`：成功
- **expected`：日志 `SYNC source=xxx target=xxx status=success`
- **notes**：注意"成功"+"耗时"

### TP-014（LOG_THIRD_PARTY）：同步失败
- **scenario**：场景 14
- **module**：`LOG_THIRD_PARTY`
- **precondition**：同步失败
- **test_data`：失败
- **expected`：日志 `SYNC status=fail reason`
- **notes**：注意"失败"+"重试"

### TP-015（LOG_THIRD_PARTY）：重试机制
- **scenario**：场景 15
- **module**：`LOG_THIRD_PARTY`
- **precondition`：重试
- **test_data`：重试 3 次
- **expected`：3 条日志 `SYNC_RETRY count=N`
- **notes**：注意"重试"vs"成功"

### TP-016（LOG_THIRD_PARTY）：第三方限流
- **scenario**：场景 16
- **module**：`LOG_THIRD_PARTY`
- **precondition**：被限流
- **test_data`：限流
- **expected`：日志 `THIRD_API status=rate_limit`
- **notes**：注意"限流"vs"失败"

### TP-017（LOG_THIRD_PARTY）：第三方超时
- **scenario**：场景 17
- **module**：`LOG_THIRD_PARTY`
- **precondition`：超时
- **test_data`：超时
- **expected`：日志 `THIRD_API status=timeout duration=Xms`
- **notes**：注意"超时"+"重试"

### TP-018（LOG_THIRD_PARTY）：第三方错误码
- **scenario**：场景 18
- **module**：`LOG_THIRD_PARTY`
- **precondition`：错误
- **test_data`：错误
- **expected`：日志 `THIRD_API code=X msg=xxx`
- **notes**：注意"错误码"+"重试"

### TP-019（LOG_THIRD_PARTY）：双向 trace
- **scenario**：场景 19
- **module**：`LOG_THIRD_PARTY`
- **precondition`：第三方
- **test_data`：全链路
- **expected`：trace 串联
- **notes**：注意"双向"+"trace"

### TP-020（LOG_THIRD_PARTY）：第三方数据脱敏
- **scenario**：场景 20
- **module**：`LOG_THIRD_PARTY`
- **precondition**：敏感
- **test_data`：写入
- **expected`：脱敏
- **notes**：注意"脱敏"+"合规"

### TP-021（LOG_THIRD_PARTY）：第三方 SLA
- **scenario**：场景 7
- **module**：`LOG_THIRD_PARTY`
- **precondition`：API 响应
- **test_data`：观察
- **expected`：P99 延迟符合 SLA
- **notes**：注意"SLA"vs"超时"

### TP-022（LOG_THIRD_PARTY）：第三方可用率
- **scenario**：场景 7
- **module**：`LOG_THIRD_PARTY`
- **precondition**：1 天调用
- **test_data`：观察
- **expected`：可用率 99.9%
- **notes**：注意"可用率"

### TP-023（LOG_THIRD_PARTY）：第三方审计
- **scenario**：场景 1
- **module**：`LOG_THIRD_PARTY`
- **precondition`：1 天第三方调用
- **test_data`：审计
- **expected`：100% 调用有日志
- **notes**：注意"审计"+"覆盖率"

### TP-024（LOG_THIRD_PARTY）：回调幂等
- **scenario**：场景 4
- **module**：`LOG_THIRD_PARTY`
- **precondition**：重复回调
- **test_data`：回调 5 次
- **expected`：5 条日志、业务仅 1 次
- **notes**：注意"幂等"vs"业务"

### TP-025（LOG_THIRD_PARTY）：跨服对账
- **scenario**：场景 9
- **module**：`LOG_THIRD_PARTY`
- **precondition**：跨服
- **test_data`：对账
- **expected`：双服一致
- **notes**：注意"对账"vs"实时"

---

## 3. 边界陷阱

### 边界 1：vs LINK 跨服务
- **混淆点**：「跨服"交互"」——LINK 测业务、K 测日志
- **判定规则**：测"跨服业务" → LINK；测"跨服日志" → K
- **实例**：跨服交易数据 → LINK；跨服日志留痕 → K

### 边界 2：vs BIZ H. 付费
- **混淆点**：「支付"业务"」——BIZ H 测业务、K 测日志
- **判定规则**：测"支付业务" → BIZ H；测"支付日志" → K
- **实例**：订单回调业务 → BIZ H；订单回调日志 → K

### 边界 3：vs BIZ C. 协议
- **混淆点**：「协议"字段"」——BIZ C 测协议、K 测日志
- **判定规则**：测"协议字段" → BIZ C；测"协议日志" → K
- **实例**：协议字段格式 → BIZ C；协议日志 → K

### 边界 4：vs A. 行为埋点
- **混淆点**：「支付"埋点"」——A 测行为、K 测外部
- **判定规则**：测"玩家行为" → A；测"第三方交互" → K
- **实例**：玩家登录埋点 → A；渠道登录 → K

### 边界 5：vs B. 资产流水
- **混淆点**：「支付"流水"」——B 测对账、K 测日志
- **判定规则**：测"资产对账" → B；测"第三方日志" → K
- **实例**：资产对账 → B；第三方日志 → K

---

## 4. 验证证据

### 视觉证据
- 第三方日志检索截图
- 跨服 trace 截图

### 日志证据
- `THIRD_LOGIN/CALLBACK/PAY/REFUND` 第三方日志
- `CROSS_SYNC from=A to=B status=success/fail`
- `THIRD_API url method status code`
- `SYNC_RETRY count=N`

### 数据证据
- 第三方日志表 `third_log.channel, type, target, status, time`
- 跨服同步日志表 `cross_sync_log.from, to, status, time`
- 第三方可用率
- 第三方 SLA 监控
- 双向 trace 串联

### 性能证据
- 第三方调用日志 < 5ms
- 跨服同步日志 < 10ms
- 第三方可用率 ≥ 99.9%
- 第三方 P99 延迟符合 SLA
- 双向 trace 查询 < 1s
