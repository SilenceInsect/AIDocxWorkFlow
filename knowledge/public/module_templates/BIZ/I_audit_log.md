# I. 日志与审计溯源

> **子类代码**：`BIZ_AUDIT_LOG`
> **归属模块**：`BIZ`
> **来源**：用户细化定义 §9「日志与审计溯源」（原定义完全缺失，新增）
>
> **测什么**：资源产出消耗日志、操作行为日志、付费日志、状态变更日志；可追溯性、对账、风控。
> **不测什么**：通用日志工具（归 UTIL）、业务逻辑（归 A）、状态机（归 D）、付费业务（归 H）。
> **与其他子类的差异**：I 关注"业务审计日志"——UTIL J 关注"通用日志工具"，LOG 模块关注"通用行为日志"，H 关注"付费业务"。

---

## 1. 典型场景

### 场景 1：资源产出日志
- 业务背景：杀怪掉落、邮件发放
- 涉及数据：玩家 ID、道具、来源、数量
- 触发动作：产出道具
- 验证点：日志记录产出轨迹

### 场景 2：资源消耗日志
- 业务背景：购买、合成、使用
- 涉及数据：玩家 ID、道具、去向、数量
- 触发动作：消耗道具
- 验证点：日志记录消耗轨迹

### 场景 3：操作行为日志
- 业务背景：玩家登录、退出、聊天
- 涉及数据：玩家 ID、操作类型、时间
- 触发动作：玩家操作
- 验证点：日志记录操作

### 场景 4：付费日志
- 业务背景：充值、购买、退款
- 涉及数据：玩家 ID、金额、渠道
- 触发动作：付费操作
- 验证点：日志记录付费

### 场景 5：状态变更日志
- 业务背景：玩家升级、Buff 获得、活动开启
- 涉及数据：玩家 ID、状态变化
- 触发动作：状态变更
- 验证点：日志记录状态变化

### 场景 6：每笔业务可追溯
- 业务背景：玩家反馈"钻石少了"
- 涉及数据：玩家钻石流水
- 触发动作：查询玩家日志
- 验证点：找到具体哪笔操作扣的

### 场景 7：风控对账
- 业务背景：风控系统分析玩家行为
- 涉及数据：玩家操作序列
- 触发动作：风控扫描
- 验证点：从日志还原玩家行为

### 场景 8：日志完整性
- 业务背景：所有业务操作均有日志
- 涉及数据：日志覆盖率
- 触发动作：审计检查
- 验证点：100% 业务有日志

### 场景 9：日志不可篡改
- 业务背景：防止运营删日志
- 涉及数据：日志存储
- 触发动作：尝试删日志
- **expected**：拦截 + 失败
- 验证点：日志不可改

### 场景 10：日志查询性能
- 业务背景：玩家查询 1 年前日志
- 涉及数据：日志存储
- 触发动作：查询
- 验证点：< 1s 返回

### 场景 11：日志归档
- 业务背景：1 年前日志
- 涉及数据：日志冷热
- 触发动作：归档任务
- 验证点：冷数据归档、可查询

### 场景 12：玩家问题排查
- 业务背景：玩家反馈 bug
- 涉及数据：玩家操作流水
- 触发动作：客服查询
- 验证点：能从日志还原现场

---

## 2. 种子测试点（TP 模板）

### TP-001（BIZ_AUDIT_LOG）：资源产出日志
- **scenario**：场景 1
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：玩家杀怪掉落 1 把铁剑
- **test_data**：`monster_drop(player_id, item_id=1001, count=1)`
- **expected**：日志记录 `ASSET_CHANGE type=ADD item=1001 count=1 reason=monster_drop`
- **notes**：注意"产出"vs"消耗"日志区分

### TP-002（BIZ_AUDIT_LOG）：资源消耗日志
- **scenario**：场景 2
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：玩家使用 1 个血瓶
- **test_data**：`use_item(player_id, item_id=2001, count=1)`
- **expected`：日志记录 `ASSET_CHANGE type=SUB item=2001 count=1 reason=use`
- **notes**：注意"使用"vs"丢弃"vs"出售"

### TP-003（BIZ_AUDIT_LOG）：GM 发奖日志
- **scenario**：场景 1
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：GM 给玩家发 100 钻
- **test_data**：`gm_add_item(player_id, item_id=1, count=100, op_id=GM001)`
- **expected`：日志记录 GM 操作人 + 道具 + 时间
- **notes**：注意"GM"vs"业务"+"审计"

### TP-004（BIZ_AUDIT_LOG）：玩家登录日志
- **scenario**：场景 3
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：玩家登录
- **test_data**：`login(player_id, ip, device)`
- **expected`：日志记录 `LOGIN player_id=xxx ip=xxx device=xxx time=xxx`
- **notes**：注意"登录"vs"重连"+"IP 风控"

### TP-005（BIZ_AUDIT_LOG）：玩家退出日志
- **scenario**：场景 3
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：玩家退出
- **test_data**：`logout(player_id)`
- **expected`：日志记录 `LOGOUT time=xxx duration=Xmin`
- **notes**：注意"主动"vs"超时"

### TP-006（BIZ_AUDIT_LOG）：聊天消息日志
- **scenario**：场景 3
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：玩家发世界聊天
- **test_data**：`send_msg(player_id, channel=world, content=xxx)`
- **expected`：日志记录 `CHAT player_id channel content`、敏感词过滤日志
- **notes**：注意"敏感词"+"违规"+"封禁"

### TP-007（BIZ_AUDIT_LOG）：充值日志
- **scenario**：场景 4
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：玩家充值 100 元
- **test_data**：`recharge(player_id, amount=100, channel=alipay)`
- **expected`：日志记录 `RECHARGE player_id amount channel order_id`
- **notes**：注意"金额"+"渠道"+"订单号"

### TP-008（BIZ_AUDIT_LOG）：退款日志
- **scenario**：场景 4
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：玩家退款
- **test_data**：`refund(player_id, order_id, reason)`
- **expected`：日志记录 `REFUND player_id order_id reason operator`
- **notes**：注意"主动"vs"被动"+"原因"

### TP-009（BIZ_AUDIT_LOG）：状态变更日志
- **scenario**：场景 5
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：玩家升级 Lv.10 → Lv.11
- **test_data**：`level_up(player_id, from=10, to=11)`
- **expected`：日志记录 `LEVEL_UP from to time`
- **notes**：注意"升级"vs"经验"+"触发奖励"

### TP-010（BIZ_AUDIT_LOG）：Buff 获得日志
- **scenario**：场景 5
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：玩家获得 Buff
- **test_data**：`add_buff(player_id, buff_id=5, duration=30s)`
- **expected`：日志记录 `BUFF_ADD player_id buff_id duration`
- **notes**：注意"获得"vs"刷新"vs"过期"

### TP-011（BIZ_AUDIT_LOG）：活动开启日志
- **scenario**：场景 5
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：活动状态变化
- **test_data`：`activity_state_change(activity_id, from=CLOSED, to=OPEN)`
- **expected`：日志记录 `ACTIVITY_STATE_CHANGE id from to operator=auto`
- **notes**：注意"定时"vs"手动"

### TP-012（BIZ_AUDIT_LOG）：每笔业务可追溯
- **scenario**：场景 6
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：玩家反馈"钻石少了 100"
- **test_data`：客服查询 `query_logs(player_id, type=ASSET_CHANGE, 1day)`
- **expected`：找到具体哪笔操作（购买 100 钻）
- **notes**：注意"日志完整"+"可追溯"+"索引"

### TP-013（BIZ_AUDIT_LOG）：玩家完整流水
- **scenario**：场景 6
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：玩家 1 天 100 个操作
- **test_data`：`query_logs(player_id, 1day)`
- **expected`：返回 100 条日志、按时间排序
- **notes**：注意"全量"vs"采样"

### TP-014（BIZ_AUDIT_LOG）：风控对账
- **scenario**：场景 7
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：玩家 1 分钟交易 50 次
- **test_data`：风控扫描
- **expected`：从日志还原 50 次交易、触发风控规则
- **notes**：注意"实时"vs"离线"风控

### TP-015（BIZ_AUDIT_LOG）：日志完整性
- **scenario**：场景 8
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：所有业务操作
- **test_data`：审计检查
- **expected`：100% 业务有对应日志
- **notes**：注意"业务"vs"日志"+"埋点覆盖率"

### TP-016（BIZ_AUDIT_LOG）：日志不可篡改
- **scenario**：场景 9
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：运营尝试删日志
- **test_data`：`delete_log(log_id, op_id=OP001)`
- **expected`：拦截 + 失败 + 写审计告警
- **notes**：注意"软删"vs"硬删"+"只追加"

### TP-017（BIZ_AUDIT_LOG）：日志可查询
- **scenario**：场景 10
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：1 年前日志
- **test_data`：`query_logs(player_id, type=RECHARGE, 1year)`
- **expected`：< 1s 返回
- **notes**：注意"索引"+"归档"

### TP-018（BIZ_AUDIT_LOG）：日志归档
- **scenario**：场景 11
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：1 年前日志
- **test_data`：归档任务
- **expected`：冷数据归档、热数据可查
- **notes**：注意"冷热"+"保留期"

### TP-019（BIZ_AUDIT_LOG）：玩家问题排查
- **scenario**：场景 12
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：玩家反馈 bug
- **test_data`：客服查询
- **expected`：从日志还原操作流水、定位问题
- **notes**：注意"现场"+"全链路"

### TP-020（BIZ_AUDIT_LOG）：日志字段完整性
- **scenario**：场景 8
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：资源变动日志
- **test_data`：检查日志字段
- **expected`：含 player_id, item_id, change_type, count, before, after, reason, time, op_id
- **notes**：注意"业务字段"+"审计字段"

### TP-021（BIZ_AUDIT_LOG）：跨服日志合并
- **scenario**：场景 7
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：玩家在服 A 和服 B 都有操作
- **test_data`：`query_logs(player_id)`
- **expected`：合并双服日志、统一展示
- **notes**：注意"跨服"+"全局视图"

### TP-022（BIZ_AUDIT_LOG）：付费审计
- **scenario**：场景 4
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：100 笔充值
- **test_data`：审计
- **expected`：每笔有完整审计链（订单→回调→发货）
- **notes**：注意"对账"+"审计"+"法规"

### TP-023（BIZ_AUDIT_LOG）：GM 审计
- **scenario**：场景 1
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：GM 发了 1000 笔补偿
- **test_data`：审计
- **expected`：每笔有 GM ID + 时间 + 原因 + 道具
- **notes**：注意"GM"+"审计"+"事后追溯"

### TP-024（BIZ_AUDIT_LOG）：敏感操作审计
- **scenario**：场景 3
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：删号、改名、转区
- **test_data`：敏感操作
- **expected`：独立审计日志、不可删除
- **notes**：注意"敏感"+"强审计"

### TP-025（BIZ_AUDIT_LOG）：日志量级
- **scenario**：场景 8
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：10 万玩家在线
- **test_data`：1 天
- **expected`：日志量级评估（如 1GB/s 写入）
- **notes**：注意"量级"+"存储"+"成本"

### TP-026（BIZ_AUDIT_LOG）：日志关联性
- **scenario**：场景 6
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：一笔购买
- **test_data`：查询相关日志
- **expected`：可关联到订单、回调、发货、状态变更
- **notes**：注意"链路"+"trace_id"

### TP-027（BIZ_AUDIT_LOG）：日志告警
- **scenario**：场景 7
- **module**：`BIZ_AUDIT_LOG`
- **precondition**：异常行为
- **test_data`：风控触发
- **expected`：实时告警 + 写特殊日志
- **notes**：注意"实时"vs"事后"

### TP-028（BIZ_AUDIT_LOG）：合规留存
- **scenario**：场景 8
- **module**：`BIZ_AUDIT_LOG`
- **precondition`：法规要求 5 年留存
- **test_data`：合规检查
- **expected`：5 年日志可查、不可删
- **notes**：注意"法规"+"隐私"+"GDPR"

---

## 3. 边界陷阱

### 边界 1：vs UTIL J. 存储+日志
- **混淆点**：「业务"日志"」——I 测业务、UTIL J 测通用
- **判定规则**：测"通用日志工具/采集" → UTIL J；测"业务审计日志" → I
- **实例**：日志 SDK → UTIL J；业务操作审计 → I

### 边界 2：vs LOG（专门 LOG 模块）
- **混淆点**：「玩家"日志"」——I 测业务、LOG 测通用
- **判定规则**：测"业务审计" → I；测"通用行为日志" → LOG
- **实例**：资源变动审计 → I；点击行为日志 → LOG

### 边界 3：vs A. 业务
- **混淆点**：「购买"业务"」——A 测业务、I 测日志
- **判定规则**：测"业务结果" → A；测"日志完整性" → I
- **实例**：购买扣款 → A；购买日志 → I

### 边界 4：vs H. 付费
- **混淆点**：「付费"日志"」——H 测业务、I 测审计
- **判定规则**：测"付费业务" → H；测"付费审计" → I
- **实例**：充值业务 → H；充值审计链 → I

### 边界 5：vs UTIL G. GM 工具
- **混淆点**：「GM"操作"」——UTIL G 测 GM、I 测审计
- **判定规则**：测"GM 指令" → UTIL G；测"GM 操作审计" → I
- **实例**：GM 指令工具 → UTIL G；GM 操作审计日志 → I

---

## 4. 验证证据

### 视觉证据
- 日志查询界面截图
- 风控告警截图

### 日志证据
- 资源变动日志 `ASSET_CHANGE type=ADD/SUB player_id item_id count before after reason time op_id`
- 行为日志 `LOGIN/LOGOUT/CHAT/TRADE player_id action time`
- 付费日志 `RECHARGE/REFUND player_id amount channel order_id`
- 状态变更日志 `STATE_CHANGE entity from to time op_id`
- 审计日志 `AUDIT op_id action target time`（不可删）

### 数据证据
- 日志表 `audit_log.log_id, type, player_id, payload, time, op_id`
- 业务操作 ↔ 日志 100% 覆盖
- 日志保留期 = 法规要求
- 审计日志独立存储、不可删
- 日志查询索引（按 player_id, time, type）
- 链路追踪 `trace_id` 串联多系统日志

### 性能证据
- 日志写入 < 1ms
- 日志查询（按 player_id 1 天）< 100ms
- 日志归档性能
- 风控实时扫描 < 1s
- 日志存储成本控制（采样、冷热分离）
