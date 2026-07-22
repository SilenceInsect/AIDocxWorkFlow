# B. 资产产出消耗审计追踪

> **子类代码**：`LOG_ASSET_AUDIT`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §2「资产产出消耗审计追踪（财务级日志，游戏对账核心）」
>
> **测什么**：全货币流水（钻石/绑定币/代币/体力/积分/赛季币）、道具/装备流水（获取/使用/合成/分解/交易/赠送/过期/回收/批量）、付费资产流水（充值/首充/累充/礼包/退款/补发/优惠券）、对账完整性（无缺漏/正负匹配/可对账/可批量导出）。
> **不测什么**：业务扣款发货（归 BIZ）、退款业务流程（归 BIZ H）、底层数据库存储（归 BIZ E）、日志底层采集（归 AUX）。
> **与其他子类的差异**：B 关注"**资产对账**审计流水"——A 关注"行为埋点"，C 关注"操作日志"，BIZ-I 关注"业务侧落点规范"，BIZ-H 关注"付费业务流程"。

> **与 BIZ-I `BIZ_AUDIT_LOG` 的边界切分**：
> - **BIZ-I** 测"该笔业务是否产生审计链"——单笔业务侧落点是否完整
> - **B** 测"全链路流水可对账"——跨业务正负匹配、对账可导出
> 重叠但不冲突：同一笔业务 → BIZ-I 校验"是否写日志"，B 校验"日志能否对账"

---

## 1. 典型场景

### 场景 1：货币产出流水
- 业务背景：每日签到发 100 钻
- 涉及数据：钻石
- 触发动作：签到
- 验证点：日志含 +100 钻、来源、批次

### 场景 2：货币消耗流水
- 业务背景：购买 50 钻道具
- 涉及数据：钻石
- 触发动作：购买
- 验证点：日志含 -50 钻、去向

### 场景 3：货币兑换
- 业务背景：1 钻 = 100 金币
- 涉及数据：钻石、金币
- 触发动作：兑换
- 验证点：日志含双向流水（-1 钻、+100 金币）

### 场景 4：货币补发
- 业务背景：bug 补偿
- 涉及数据：钻石
- 触发动作：运营补偿
- 验证点：日志含 +N 钻、reason=compensation

### 场景 5：货币退款扣回
- 业务背景：玩家退款
- 涉及数据：钻石
- 触发动作：退款
- 验证点：日志含 -N 钻、order_id

### 场景 6：道具获取流水
- 业务背景：杀怪掉落铁剑
- 涉及数据：道具
- 触发动作：掉落
- 验证点：日志含 +1 铁剑、来源 monster_id

### 场景 7：道具使用
- 业务背景：使用血瓶
- 涉及数据：道具
- 触发动作：使用
- 验证点：日志含 -1 血瓶、reason=use

### 场景 8：道具合成
- 业务背景：3 铁矿合 1 铁锭
- 涉及数据：道具
- 触发动作：合成
- 验证点：日志含 -3 铁矿 +1 铁锭、recipe_id

### 场景 9：道具交易
- 业务背景：A 卖给 B
- 涉及数据：道具、金币
- 触发动作：交易
- 验证点：日志含双向流水

### 场景 10：道具赠送
- 业务背景：好友赠送体力
- 涉及数据：体力
- 触发动作：赠送
- 验证点：日志含 A 扣 + B 加、source=friend

### 场景 11：道具过期删除
- 业务背景：限时道具 24h 过期
- 涉及数据：道具
- 触发动作：定时清理
- 验证点：日志含 -N 道具、reason=expire

### 场景 12：道具回收
- 业务背景：玩家卖商店
- 涉及数据：道具、金币
- 触发动作：出售
- 验证点：日志含 -道具 +金币

### 场景 13：批量发放
- 业务背景：全服发 100 钻
- 涉及数据：钻石
- 触发动作：GM 批量发
- 验证点：每玩家 1 条日志、batch_id 一致

### 场景 14：充值订单流水
- 业务背景：充值 100 元
- 涉及数据：订单
- 触发动作：支付成功
- 验证点：日志含 order_id、amount、channel

### 场景 15：首充奖励
- 业务背景：玩家首充 100 元
- 涉及数据：钻石
- 触发动作：首充达成
- 验证点：日志含 base 100 + bonus 200

### 场景 16：累充奖励
- 业务背景：累充达 100 元
- 涉及数据：钻石
- 触发动作：累充达成
- 验证点：日志含 reward 200、milestone=100

### 场景 17：礼包购买
- 业务背景：购买 30 元礼包
- 涉及数据：钻石、道具
- 触发动作：购买
- 验证点：日志含 -30 元 + 道具内容

### 场景 18：退款扣回
- 业务背景：玩家退款
- 涉及数据：钻石、道具
- 触发动作：退款
- 验证点：日志含 -道具 -钻石、order_id

### 场景 19：渠道补发
- 业务背景：苹果渠道补发
- 涉及数据：订单
- 触发动作：苹果回调
- 验证点：日志含 channel=apple、order_id、status=resent

### 场景 20：优惠券抵扣
- 业务背景：50 元券抵扣
- 涉及数据：订单
- 触发动作：使用券
- 验证点：日志含 coupon_id、discount=50

### 场景 21：对账完整性
- 业务背景：日终对账
- 涉及数据：服订单 vs 渠道订单
- 触发动作：对账任务
- 验证点：差异 = 0

### 场景 22：可对账导出
- 业务背景：财务对账
- 涉及数据：1 月流水
- 触发动作：导出
- 验证点：导出 CSV/Excel、字段齐全

### 场景 23：跨货币对账
- 业务背景：钻石+金币合计
- 涉及数据：多币种
- 触发动作：聚合对账
- 验证点：各币种 + 合计 = 0

### 场景 24：负值资产对账
- 业务背景：退款后玩家钻石 -50
- 涉及数据：钻石
- 触发动作：退款扣回
- 验证点：日志含 -钻石、检测负值告警

### 场景 25：批量对账报告
- 业务背景：月对账
- 涉及数据：1 个月流水
- 触发动作：运营导出
- 验证点：每笔资产变动有日志

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_ASSET_AUDIT）：钻石产出流水
- **scenario**：场景 1
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家签到
- **test_data**：`daily_signin(player_id, reward=100_diamond)`
- **expected**：日志 `ASSET_CHANGE type=ADD currency=DIAMOND count=100 reason=daily_signin source=system`
- **notes**：注意"产出"vs"消耗"日志区分

### TP-002（LOG_ASSET_AUDIT）：钻石消耗流水
- **scenario**：场景 2
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家钻石 100
- **test_data**：`shop_purchase(item=item_001, price=50_diamond)`
- **expected**：日志 `ASSET_CHANGE type=SUB currency=DIAMOND count=50 reason=purchase`
- **notes**：注意"使用"vs"购买"vs"出售"

### TP-003（LOG_ASSET_AUDIT）：货币兑换双向
- **scenario**：场景 3
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家钻石 1、金币 0
- **test_data**：`exchange(from=diamond, to=gold, count=1)`
- **expected**：2 条日志 `-1 钻 +100 金币`、exchange_id 一致
- **notes**：注意"双向"流水原子性

### TP-004（LOG_ASSET_AUDIT）：货币补发
- **scenario**：场景 4
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：bug 影响 1000 玩家
- **test_data**：`gm_compensate(player_id, 100_diamond, reason=bug_xxx)`
- **expected**：日志 `+100 钻 reason=compensation op_id=GM001`
- **notes**：注意"bug 补偿"vs"运营补偿"vs"节日补偿"

### TP-005（LOG_ASSET_AUDIT）：退款扣回
- **scenario**：场景 5
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家已充值 100 元
- **test_data**：`refund(order_id)`
- **expected**：日志 `-100 钻 order_id=xxx reason=refund`
- **notes**：注意"已用"vs"未用"+"部分退款"

### TP-006（LOG_ASSET_AUDIT）：道具掉落
- **scenario**：场景 6
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：杀怪掉落铁剑
- **test_data**：`monster_drop(item=iron_sword, count=1)`
- **expected**：日志 `+1 铁剑 source=monster_001`
- **notes**：注意"产出"vs"邮件发送"

### TP-007（LOG_ASSET_AUDIT）：道具使用
- **scenario**：场景 7
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家有 5 血瓶
- **test_data**：`use_item(item=blood, count=1)`
- **expected**：日志 `-1 血瓶 reason=use`
- **notes**：注意"使用"vs"丢弃"vs"出售"

### TP-008（LOG_ASSET_AUDIT）：道具合成双向
- **scenario**：场景 8
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：3 铁矿合成
- **test_data**：`compose(recipe=iron_ingot)`
- **expected**：2 条日志 `-3 铁矿 +1 铁锭 compose_id=xxx`
- **notes**：注意"合成"vs"打造"vs"升级"

### TP-009（LOG_ASSET_AUDIT）：交易双向
- **scenario**：场景 9
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：A 道具 1 件、金币 100
- **test_data**：`trade(A, B, item=xxx, price=100_gold)`
- **expected**：4 条日志 `A:-道具 +金币`、`B:+道具 -金币`、trade_id 一致
- **notes**：注意"双方"流水原子性

### TP-010（LOG_ASSET_AUDIT）：好友赠送
- **scenario**：场景 10
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：好友 A 给 B 送体力
- **test_data**：`gift_stamina(A→B, count=20)`
- **expected**：2 条日志 `A:-20 体力 source=friend_gift`、`B:+20 体力 source=friend`
- **notes**：注意"赠送"vs"交易"+"限额"

### TP-011（LOG_ASSET_AUDIT）：道具过期
- **scenario**：场景 11
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：限时道具 24h 过期
- **test_data**：第 25 小时
- **expected**：日志 `-N 道具 reason=expire expire_at=xxx`
- **notes**：注意"过期"vs"销毁"vs"回收"

### TP-012（LOG_ASSET_AUDIT）：道具回收
- **scenario**：场景 12
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家出售铁剑
- **test_data**：`sell(item=iron_sword, count=1, price=50_gold)`
- **expected**：2 条日志 `-1 铁剑 +50 金币 reason=sell`
- **notes**：注意"出售"vs"丢弃"vs"赠送"

### TP-013（LOG_ASSET_AUDIT）：批量发放 batch_id
- **scenario**：场景 13
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：10 万玩家
- **test_data**：`gm_batch_reward(100000, 100_diamond, op_id=GM001)`
- **expected**：10 万条日志、batch_id=`reward_20260615_xxx` 一致
- **notes**：注意"batch_id"是聚合对账关键

### TP-014（LOG_ASSET_AUDIT）：充值订单流水
- **scenario**：场景 14
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家充值 100 元
- **test_data**：`recharge(player_id, 100, channel=alipay)`
- **expected**：日志 `RECHARGE order_id=xxx amount=100 channel=alipay status=success`
- **notes**：注意"发起"vs"成功"+"回调"

### TP-015（LOG_ASSET_AUDIT）：首充奖励
- **scenario**：场景 15
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家首充 100 元
- **test_data**：`first_recharge(player_id, 100)`
- **expected**：2 条日志 `RECHARGE 100` + `REWARD type=FIRST 200`
- **notes**：注意"基础"vs"奖励"分 2 条

### TP-016（LOG_ASSET_AUDIT）：累充奖励
- **scenario**：场景 16
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：累充达 100 元
- **test_data**：`accumulate_recharge(player_id, milestone=100)`
- **expected**：日志 `REWARD type=ACCUMULATE 200 milestone=100`
- **notes**：注意"档位"vs"金额"

### TP-017（LOG_ASSET_AUDIT）：礼包购买
- **scenario**：场景 17
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家买 30 元礼包
- **test_data**：`purchase_gift(gift_id=g001, 30)`
- **expected**：多条日志 `-30 元` + `+道具` + `+钻石`
- **notes**：注意"礼包"多资源发放

### TP-018（LOG_ASSET_AUDIT）：退款扣回完整
- **scenario**：场景 18
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家已买 100 元礼包、已用道具
- **test_data**：`refund(order_id)`
- **expected**：多条日志 `-钻石 -道具`、检测负值告警
- **notes**：注意"已用"vs"未用"+"强制回滚"

### TP-019（LOG_ASSET_AUDIT）：渠道补发
- **scenario**：场景 19
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：苹果补发
- **test_data**：`channel_resend(channel=apple, order_id=xxx)`
- **expected**：日志 `RECHARGE status=resent channel=apple`
- **notes**：注意"补发"vs"重试"vs"幂等"

### TP-020（LOG_ASSET_AUDIT）：优惠券抵扣
- **scenario**：场景 20
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家用 50 元券
- **test_data**：`use_coupon(coupon_id=c001, discount=50)`
- **expected**：日志 `COUPON_USE coupon_id=c001 discount=50`
- **notes**：注意"券"+"实付"对账

### TP-021（LOG_ASSET_AUDIT）：日终对账
- **scenario**：场景 21
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：1 天 10000 笔变动
- **test_data**：定时对账
- **expected**：服变动 = 渠道变动、差异 = 0
- **notes**：注意"对账"vs"补单"+"差异处理"

### TP-022（LOG_ASSET_AUDIT）：批量导出对账
- **scenario**：场景 22
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：1 月流水 1000 万条
- **test_data**：财务导出
- **expected**：CSV/Excel 导出、含 player_id/currency/count/reason/time
- **notes**：注意"导出"性能+"字段完整"

### TP-023（LOG_ASSET_AUDIT）：跨币种对账
- **scenario**：场景 23
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：1 天涉及钻石+金币+代币
- **test_data**：聚合对账
- **expected**：各币种分别对账、合计正确
- **notes**：注意"多币种"+"汇率"

### TP-024（LOG_ASSET_AUDIT）：负值告警
- **scenario**：场景 24
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家钻石 -50
- **test_data**：退款扣回
- **expected**：日志记录 + 风控告警
- **notes**：注意"负值"+"对账失败"

### TP-025（LOG_ASSET_AUDIT）：月对账覆盖率
- **scenario**：场景 25
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：1 月业务数据 100 万笔
- **test_data**：对账覆盖率统计
- **expected**：100% 业务有对应日志
- **notes**：注意"覆盖率"指标

### TP-026（LOG_ASSET_AUDIT）：跨服资产对账
- **scenario**：场景 22
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家跨服交易
- **test_data**：跨服对账
- **expected**：双服流水一致
- **notes**：注意"跨服"对账

### TP-027（LOG_ASSET_AUDIT）：退款回滚反向日志
- **scenario**：场景 5
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：原购买日志 + 退款日志
- **test_data**：观察日志链
- **expected**：refund_id 反向关联原 purchase_id
- **notes**：注意"链路"+"可追溯"

### TP-028（LOG_ASSET_AUDIT）：玩家删除后日志保留
- **scenario**：场景 25
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家删号
- **test_data**：导出玩家历史日志
- **expected**：日志保留 5 年（合规）
- **notes**：注意"软删"vs"硬删"+"合规留存"

### TP-029（LOG_ASSET_AUDIT）：资产正负零
- **scenario**：场景 23
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：玩家 1 天操作 100 笔
- **test_data**：资产净变动 = 0
- **expected**：日志累计 = 0、对账通过
- **notes**：注意"原子性"+"对账规则"

### TP-030（LOG_ASSET_AUDIT）：GM 强制回收审计
- **scenario**：场景 12
- **module**：`LOG_ASSET_AUDIT`
- **precondition**：GM 强制回收玩家非法所得
- **test_data**：`gm_reclaim(player_id, item=xxx, reason=cheat)`
- **expected**：日志 `-道具 op_id=GM001 reason=cheat`
- **notes**：注意"GM"vs"业务"+"审计"

---

## 3. 边界陷阱

### 边界 1：vs BIZ-I. 业务审计
- **混淆点**：「购买"日志"」——B 测对账、BIZ-I 测业务落点
- **判定规则**：测"单笔业务是否写日志" → BIZ-I；测"全链路对账可导出" → B
- **实例**：购买日志格式 → BIZ-I；月对账覆盖率 → B-025

### 边界 2：vs BIZ-H. 付费
- **混淆点**：「充值"业务"」——B 测流水、H 测业务
- **判定规则**：测"充值业务" → BIZ-H；测"充值流水" → B
- **实例**：订单回调 → BIZ-H；充值流水 → B-014

### 边界 3：vs BIZ-E. 数据库
- **混淆点**：「资产"存储"」——B 测日志、BIZ-E 测 DB
- **判定规则**：测"业务数据落库" → BIZ-E；测"日志对账" → B
- **实例**：钻石 DB 字段 → BIZ-E；资产对账 → B

### 边界 4：vs A. 行为埋点
- **混淆点**：「购买"埋点"」——A 测行为、B 测资产
- **判定规则**：测"行为触发" → A；测"资产变动" → B
- **实例**：购买点击埋点 → A；购买资产变动 → B-002

### 边界 5：vs C. 操作日志
- **混淆点**：「购买"日志"」——B 测资产、C 测操作
- **判定规则**：测"资产流水" → B；测"操作行为" → C
- **实例**：购买扣款流水 → B；GM 退款操作 → C

---

## 4. 验证证据

### 视觉证据
- 对账报告截图
- 漏账告警截图
- 退款回滚记录截图

### 日志证据
- `ASSET_CHANGE type=ADD/SUB currency=xxx count=N reason=xxx time player_id` 资产变动流水
- `RECHARGE/REFUND order_id amount channel` 付费流水
- `BATCH_REWARD batch_id count=N` 批量流水
- `COUPON_USE coupon_id discount` 券流水
- `DAILY_RECONCILE diff=0` 日终对账

### 数据证据
- 资产流水表 `asset_log.player_id, currency, count, change_type, reason, time, batch_id`
- 付费流水表 `pay_log.order_id, player_id, amount, channel, time, status`
- 对账报告 `reconcile_report.diff_count, diff_detail`
- 资产覆盖率 = 100%
- 正负匹配校验通过
- batch_id 完整性
- 跨服流水一致性

### 性能证据
- 资产对账 < 30s/天
- 1 月 1000 万笔导出 < 5min
- 单笔日志写入 < 5ms
- 批量对账 100 万笔 < 30s
- 跨服对账 < 1s
