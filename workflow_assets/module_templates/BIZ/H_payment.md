# H. 付费 & 商业化专属业务

> **子类代码**：`BIZ_PAYMENT`
> **归属模块**：`BIZ`
> **来源**：用户细化定义 §8「付费&商业化专属业务」（原定义完全缺失，新增）
>
> **测什么**：充值订单流程、回调校验、累充/首充奖励、礼包限购、补发、退款、渠道订单、多端付费对账。
> **不测什么**：业务逻辑（归 A）、协议字段（归 C）、第三方支付 SDK 集成（归 LINK）、审计日志（归 I）。
> **与其他子类的差异**：H 关注"付费订单+对账"——A 关注"业务"，C 关注"协议"，LIN K 关注"第三方集成"，I 关注"日志"。

---

## 1. 典型场景

### 场景 1：充值订单创建
- 业务背景：玩家充值
- 涉及数据：订单 ID、金额、商品
- 触发动作：玩家选择充值档位
- 验证点：订单创建成功

### 场景 2：订单支付
- 业务背景：调起支付
- 涉及数据：支付渠道、订单状态
- 触发动作：玩家完成支付
- 验证点：订单状态 待支付→已支付

### 场景 3：订单回调校验
- 业务背景：支付平台回调
- 涉及数据：回调签名、订单号
- 触发动作：支付平台发回调
- 验证点：签名校验通过

### 场景 4：首充奖励
- 业务背景：玩家首次充值
- 涉及数据：首充标记
- 触发动作：玩家首次充值
- 验证点：触发首充奖励

### 场景 5：累充奖励
- 业务背景：累计充值
- 涉及数据：累充进度
- 触发动作：充值成功
- 验证点：累充进度更新

### 场景 6：充值补发
- 业务背景：支付成功但未到账
- 涉及数据：补发机制
- 触发动作：玩家反馈未到账
- 验证点：补发成功

### 场景 7：退款回滚
- 业务背景：玩家退款
- 涉及数据：退款流程
- 触发动作：支付平台退款
- 验证点：道具回滚

### 场景 8：礼包限购
- 业务背景：付费礼包
- 涉及数据：限购次数
- 触发动作：购买付费礼包
- 验证点：限购扣减

### 场景 9：多端付费
- 业务背景：iOS + Android + Web
- 涉及数据：玩家 ID 关联
- 触发动作：跨端充值
- 验证点：账号数据统一

### 场景 10：渠道订单对账
- 业务背景：每日对账
- 涉及数据：服订单 vs 渠道订单
- 触发动作：定时对账
- 验证点：差异 < 0.01%

### 场景 11：黑卡/盗刷
- 业务背景：信用卡盗刷
- 涉及数据：风控
- 触发动作：异常充值
- 验证点：拦截 + 退款

### 场景 12：支付失败重试
- 业务背景：网络抖动支付失败
- 涉及数据：重试机制
- 触发动作：支付失败
- 验证点：自动重试或提示

---

## 2. 种子测试点（TP 模板）

### TP-001（BIZ_PAYMENT）：订单创建
- **scenario**：场景 1
- **module**：`BIZ_PAYMENT`
- **precondition**：玩家选 100 元档位
- **test_data**：`create_order(player_id, amount=100)`
- **expected**：订单创建成功、返回订单号、状态待支付
- **notes**：注意"订单号唯一性"+"幂等"

### TP-002（BIZ_PAYMENT）：订单幂等
- **scenario**：场景 1
- **module**：`BIZ_PAYMENT`
- **precondition**：玩家点击充值 2 次
- **test_data**：连续 `create_order` 2 次
- **expected**：仅 1 个订单、另一个返回"已创建"
- **notes**：注意"幂等键"

### TP-003（BIZ_PAYMENT）：调起支付
- **scenario**：场景 2
- **module**：`BIZ_PAYMENT`
- **precondition**：订单待支付
- **test_data**：调起支付宝
- **expected**：拉起支付宝、订单状态 待支付→支付中
- **notes**：注意"调起"vs"取消"+"支付中状态"

### TP-004（BIZ_PAYMENT）：支付成功
- **scenario**：场景 2
- **module**：`BIZ_PAYMENT`
- **precondition**：支付中
- **test_data`：支付完成
- **expected**：订单状态 支付中→已支付、道具发放
- **notes**：注意"已支付"vs"已发放"

### TP-005（BIZ_PAYMENT）：支付取消
- **scenario**：场景 2
- **module**：`BIZ_PAYMENT`
- **precondition**：支付中
- **test_data`：玩家取消支付
- **expected**：订单状态 支付中→已取消
- **notes**：注意"取消"vs"超时"

### TP-006（BIZ_PAYMENT）：回调签名校验
- **scenario**：场景 3
- **module**：`BIZ_PAYMENT`
- **precondition**：支付平台发回调
- **test_data`：篡改签名
- **expected**：拦截 + 错误码 `INVALID_SIGN`、不发货
- **notes**：注意"签名"vs"加密"

### TP-007（BIZ_PAYMENT）：回调幂等
- **scenario**：场景 3
- **module**：`BIZ_PAYMENT`
- **precondition**：支付平台重复回调
- **test_data`：同一订单 10 次回调
- **expected**：仅 1 次发货、其他 9 次幂等
- **notes**：注意"幂等"vs"去重"

### TP-008（BIZ_PAYMENT）：回调订单不存在
- **scenario**：场景 3
- **module**：`BIZ_PAYMENT`
- **precondition**：回调订单号 = `not_exist_order`
- **test_data`：回调
- **expected**：拦截 + 错误码 `ORDER_NOT_FOUND`
- **notes**：注意"伪造订单"+"风控"

### TP-009（BIZ_PAYMENT）：首充奖励
- **scenario**：场景 4
- **module**：`BIZ_PAYMENT`
- **precondition**：玩家首充标记 false
- **test_data`：充值 100 元成功
- **expected**：首充标记 true、触发首充奖励发放
- **notes**：注意"首充"vs"二次充值"+"档位"

### TP-010（BIZ_PAYMENT）：二次首充拦截
- **scenario**：场景 4
- **module**：`BIZ_PAYMENT`
- **precondition**：首充标记 true
- **test_data`：再次充值
- **expected`：不重复触发首充奖励
- **notes**：注意"幂等"vs"状态机"

### TP-011（BIZ_PAYMENT）：累充进度
- **scenario**：场景 5
- **module**：`BIZ_PAYMENT`
- **precondition**：累充 0/100
- **test_data`：充值 100 元
- **expected**：累充 0→100、可领累充奖励
- **notes**：注意"累充"vs"单笔"+"档位跳级"

### TP-012（BIZ_PAYMENT）：累充档位跳级
- **scenario**：场景 5
- **module**：`BIZ_PAYMENT`
- **precondition**：累充 50/100
- **test_data`：充值 100 元
- **expected`：累充 50→150、档位跳 2 级（100+150 各一次）
- **notes**：注意"跳级"vs"逐级"

### TP-013（BIZ_PAYMENT）：充值补发
- **scenario**：场景 6
- **module**：`BIZ_PAYMENT`
- **precondition**：订单已支付但未到账
- **test_data`：玩家反馈、GM 补发
- **expected**：补发成功、玩家收到道具
- **notes**：注意"补发"vs"重发"+"幂等"

### TP-014（BIZ_PAYMENT）：补发幂等
- **scenario**：场景 6
- **module**：`BIZ_PAYMENT`
- **precondition**：补发过 1 次
- **test_data`：再次点击补发
- **expected`：不重复补发
- **notes**：注意"防重"+"审计"

### TP-015（BIZ_PAYMENT）：退款资源回滚
- **scenario**：场景 7
- **module**：`BIZ_PAYMENT`
- **precondition`：玩家已购买 100 元道具
- **test_data**：支付平台退款
- **expected`：道具回收、钻石扣除、订单状态 已支付→已退款
- **notes**：注意"道具已使用"vs"未使用"+"部分退款"

### TP-016（BIZ_PAYMENT）：道具已使用退款
- **scenario**：场景 7
- **module**：`BIZ_PAYMENT`
- **precondition`：玩家已用 100 钻
- **test_data`：退款
- **expected`：钻石扣成负数或拦截 + 提示
- **notes**：注意"风控"vs"强行回滚"

### TP-017（BIZ_PAYMENT）：付费礼包限购
- **scenario**：场景 8
- **module**：`BIZ_PAYMENT`
- **precondition**：付费礼包限购 1 次
- **test_data`：购买 1 次后再次购买
- **expected`：拦截 + 错误码 `LIMIT_REACHED`
- **notes**：注意"永久限购"vs"周期限购"

### TP-018（BIZ_PAYMENT）：多端账号绑定
- **scenario**：场景 9
- **module**：`BIZ_PAYMENT`
- **precondition**：玩家在 iOS + Android 同一账号
- **test_data`：iOS 充值 100 元
- **expected`：Android 登录后看到 100 元到账、同一玩家数据
- **notes**：注意"账号绑定"vs"多端登录"+"平台 ID 关联"

### TP-019（BIZ_PAYMENT）：多端数据隔离
- **scenario**：场景 9
- **module**：`BIZ_PAYMENT`
- **precondition**：iOS 账号 vs Android 账号未绑定
- **test_data`：iOS 充值
- **expected**：Android 账号无影响
- **notes**：注意"账号隔离"vs"数据互通"

### TP-020（BIZ_PAYMENT）：每日对账
- **scenario**：场景 10
- **module**：`BIZ_PAYMENT`
- **precondition**：服订单 1000 笔、渠道订单 999 笔
- **test_data`：每日对账
- **expected`：差异 1 笔、生成对账报告
- **notes**：注意"对账"vs"补单"+"差异处理"

### TP-021（BIZ_PAYMENT）：对账差异补单
- **scenario**：场景 10
- **module**：`BIZ_PAYMENT`
- **precondition**：服有但渠道无
- **test_data**：运营补单
- **expected**：补发道具
- **notes**：注意"补单"vs"补发"

### TP-022（BIZ_PAYMENT）：黑卡拦截
- **scenario**：场景 11
- **module**：`BIZ_PAYMENT`
- **precondition**：玩家用黑卡
- **test_data`：充值成功
- **expected`：风控拦截 + 退款 + 封号
- **notes**：注意"风控"vs"业务"+"延迟拦截"

### TP-023（BIZ_PAYMENT）：黑卡延迟拦截
- **scenario**：场景 11
- **module**：`BIZ_PAYMENT`
- **precondition`：黑卡充值 1 天后银行拒付
- **test_data`：银行拒付
- **expected`：道具回收、玩家封号
- **notes**：注意"延迟"vs"实时"

### TP-024（BIZ_PAYMENT）：支付失败重试
- **scenario**：场景 12
- **module**：`BIZ_PAYMENT`
- **precondition**：支付失败（网络问题）
- **test_data`：玩家点重试
- **expected**：重新调起支付
- **notes**：注意"重试"vs"换渠道"

### TP-025（BIZ_PAYMENT）：订单超时关闭
- **scenario**：场景 2
- **module**：`BIZ_PAYMENT`
- **precondition**：订单 30 分钟未支付
- **test_data`：等 31 分钟
- **expected**：订单状态 待支付→已关闭
- **notes**：注意"超时"vs"取消"

### TP-026（BIZ_PAYMENT）：订单金额校验
- **scenario**：场景 3
- **module**：`BIZ_PAYMENT`
- **precondition**：订单 100 元
- **test_data`：回调金额 = 1000 元
- **expected**：拦截 + 错误码 `AMOUNT_MISMATCH`、不发货
- **notes**：注意"金额校验"vs"商品校验"

### TP-027（BIZ_PAYMENT）：商品 ID 校验
- **scenario**：场景 3
- **module**：`BIZ_PAYMENT`
- **precondition**：订单商品 1001
- **test_data`：回调商品 = 9999
- **expected`：拦截 + 错误码 `PRODUCT_MISMATCH`、不发货
- **notes**：注意"商品"vs"金额"+"版本"

### TP-028（BIZ_PAYMENT）：玩家 ID 校验
- **scenario**：场景 3
- **module**：`BIZ_PAYMENT`
- **precondition`：订单 player_id = A
- **test_data`：回调 player_id = B
- **expected`：拦截 + 不发货
- **notes**：注意"防替换"+"重放攻击"

### TP-029（BIZ_PAYMENT）：金额越权
- **scenario**：场景 1
- **module**：`BIZ_PAYMENT`
- **precondition`：单笔上限 10000
- **test_data`：尝试 999999
- **expected`：拦截 + 错误码 `AMOUNT_EXCEED`
- **notes**：注意"业务"vs"风控"

### TP-030（BIZ_PAYMENT）：退款对账
- **scenario**：场景 7
- **module**：`BIZ_PAYMENT`
- **precondition**：100 笔退款
- **test_data`：每日对账
- **expected`：服退款数 = 渠道退款数
- **notes**：注意"退款对账"vs"支付对账"

---

## 3. 边界陷阱

### 边界 1：vs A. 业务
- **混淆点**：「购买"业务"」——A 测业务、H 测付费
- **判定规则**：测"业务扣款" → A；测"付费订单" → H
- **实例**：商城购买扣款 → A；充值订单流程 → H

### 边界 2：vs LINK 第三方
- **混淆点**：「支付"SDK"」——H 测业务、LIN K 测第三方
- **判定规则**：测"付费业务" → H；测"第三方 SDK 集成" → LINK
- **实例**：订单回调业务 → H；支付宝 SDK 集成 → LINK

### 边界 3：vs C. 协议
- **混淆点**：「订单"协议"」——H 测业务、C 测协议
- **判定规则**：测"付费业务" → H；测"协议字段" → C
- **实例**：订单创建业务 → H；订单协议字段 → C

### 边界 4：vs I. 审计
- **混淆点**：「付费"日志"」——H 测业务、I 测日志
- **判定规则**：测"付费业务" → H；测"审计日志" → I
- **实例**：订单业务 → H；付费审计日志 → I

### 边界 5：vs F. 并发
- **混淆点**：「重复"充值"」——F 测并发、H 测业务
- **判定规则**：测"业务结果" → H；测"多用户并发" → F
- **实例**：单笔订单幂等 → H；100 玩家同时充值 → F

---

## 4. 验证证据

### 视觉证据
- 充值成功 UI 截图（金额 + 道具）
- 订单详情截图
- 退款记录截图

### 日志证据
- `ORDER_CREATE/PAY/CANCEL/REFUND` 订单状态日志
- `RECHARGE_SUCCESS player_id=xxx amount=xxx` 充值成功日志
- `REWARD_SEND type=FIRST_RECHARGE/ACCUMULATE` 奖励发放日志
- `REFUND_PROCESS` 退款处理日志
- `BLACK_CARD_DETECTED` 黑卡拦截日志
- `RECONCILE_DIFF count=1` 对账差异日志

### 数据证据
- 订单表 `order.order_id, player_id, amount, status, product_id`
- 充值记录表 `recharge.player_id, amount, channel, time`
- 首充标记表 `player.first_recharge = true`
- 累充进度表 `accumulate.player_id, total_amount, milestone`
- 退款表 `refund.order_id, reason, refund_at`
- 黑名单表 `blacklist.player_id, reason, ban_at`
- 对账报告 `reconcile_report.diff_count, diff_detail`

### 性能证据
- 订单创建 < 100ms
- 回调处理 < 200ms
- 对账 10000 笔 < 30s
- 黑卡识别延迟 < 1s
- 退款时效 ≤ 24h
