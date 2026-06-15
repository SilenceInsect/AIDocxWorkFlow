# 需求对象 — 游戏道具商城系统 v1.0

> S2 产物（轻量）— 数据实体与功能点

## 需求对象

| 实体 | 字段 | 关联 |
|---|---|---|
| Player | id, name, vip_level, balance | Order, Promo |
| Item | id, name, type, price, discount | Order, Promo |
| Order | id, player_id, item_id, qty, amount, status, payment_method, created_at | Player, Item, Payment |
| Promo | id, type, start_at, end_at, rule | Order |
| VIP | level, discount_rate, expires_at | Player |
| Payment | id, order_id, channel, status, callback_payload | Order |

## 功能点（80 个，从 30 个 Story 拆出）

- 浏览商城首页
- 查看道具详情
- 搜索道具
- 选择购买数量
- 点击购买
- 选择支付方式
- 余额校验
- 支付下单
- 支付回调
- 道具发货
- 邮件通知
- 订单查询
- 订单筛选
- VIP 折扣计算
- VIP 叠加规则
- 限时打折
- 满减活动
- 新手礼包
- 微信支付
- 支付宝支付
- 支付幂等
- 缓存命中
- 缓存过期
- 缓存击穿保护
- 10000 并发
- 弱网重试
- 宕机回档
- 重复下单拦截
- 金额篡改拦截
- 风控放行
- 页面加载埋点
- 接口耗时埋点
- 埋点上报重试
- 货币流水审计
- 风控拦截日志
- 道具字段配置
- 折扣率配置
- 余额不足 Toast
- 购买成功弹窗
- 邮件降级
