# S4 业务流程图导出 — 游戏道具商城系统 v1.0

> 重跑于 2026-06-15（/aidocx-workflow-conversation 全量流水线）

## 1. 核心业务流程图

### 1.1 购买流程（主路径）

```mermaid
flowchart TD
    A[玩家登录] --> B[进入商城首页]
    B --> C[浏览/搜索道具]
    C --> D[点击道具查看详情]
    D --> E{余额是否充足?}
    E -->|否| E1[按钮置灰 + Toast提示]
    E -->|是| F[选择购买数量 1-99]
    F --> G[点击购买]
    G --> H[弹出购买确认弹窗]
    H --> I{选择支付方式}
    I -->|游戏币| J[扣款]
    I -->|微信| K[拉起微信 SDK]
    I -->|支付宝| L[拉起支付宝 SDK]
    J --> M{扣款成功?}
    K --> N{支付回调}
    L --> N
    M -->|是| P[道具入背包]
    M -->|否| Q[提示失败 + 保留余额]
    N -->|成功| P
    N -->|失败| Q
    P --> R[发送邮件通知]
    P --> S[弹出购买成功弹窗]
    R --> T[完成]
    S --> T
```

### 1.2 VIP 折扣与促销叠加流程

```mermaid
flowchart TD
    A[玩家下单] --> B{玩家 VIP 等级}
    B -->|VIP0| C[无折扣]
    B -->|VIP1| D[× 0.95]
    B -->|VIP2| E[× 0.90]
    B -->|VIP3| F[× 0.85]
    C --> G{是否在限时促销}
    D --> G
    E --> G
    F --> G
    G -->|是| H[限时价 = 原价 × 促销折扣]
    G -->|否| I[VIP 价 = 原价 × VIP 折扣]
    H --> J{满减条件}
    I --> J
    J -->|满 100-10| K[再 -10]
    J -->|满 200-25| L[再 -25]
    J -->|满 500-60| M[再 -60]
    J -->|不满足| N[最终价 = 当前价]
    K --> O[取较低价：VIP/限时 vs 满减]
    L --> O
    M --> O
    N --> T[结算]
    O --> T
```

## 2. 时序图

### 2.1 微信支付时序

```mermaid
sequenceDiagram
    participant U as 玩家客户端
    participant S as 游戏服务端
    participant W as 微信支付
    participant DB as 数据库
    U->>S: 下单请求（道具、数量）
    S->>DB: 创建订单（状态=待支付）
    S->>W: 拉起支付 SDK
    W-->>U: 支付界面
    U->>W: 输入密码支付
    W->>S: 异步回调（order_id, status）
    S->>S: 验签 + 幂等检查
    S->>DB: 更新订单状态=已支付
    S->>DB: 道具入背包
    S->>U: 推送购买成功（websocket）
    S-->>W: 返回 200 OK
    alt 回调失败
        W->>S: 重试回调（最多 3 次）
        S->>S: 幂等拦截
    end
```

## 3. 异常决策树

### 3.1 支付回调异常

```mermaid
flowchart TD
    A[支付回调] --> B{验签通过?}
    B -->|否| C[返回 401 + 告警]
    B -->|是| D{订单存在?}
    D -->|否| E[返回 404 + 记录异常订单]
    D -->|是| F{订单已支付?}
    F -->|是| G[幂等：返回 200]
    F -->|否| H[更新订单 + 发货]
    H --> I{发货成功?}
    I -->|是| J[返回 200]
    I -->|否| K[事务回滚 + 30 分钟后客服介入]
```

### 3.2 高并发异常决策

```mermaid
flowchart TD
    A[请求进入] --> B{QPS > 10000?}
    B -->|是| C[限流：429 + 排队]
    B -->|否| D{缓存命中?}
    D -->|是| E[返回数据]
    D -->|否| F{是否热 key?}
    F -->|是| G[互斥锁单飞]
    F -->|否| H[直接查 DB]
    G --> I[回源 DB + 写缓存]
    H --> I
    I --> E
```

## 4. 风险点清单

| 风险 ID | 描述 | 等级 | 涉及模块 |
|---|---|---|---|
| R-N01 | 支付回调延迟/失败 | HIGH | BIZ/LINK |
| R-N02 | 10000 并发压垮 DB | HIGH | BIZ/AUX/SPECIAL |
| R-N03 | 金额篡改攻击 | HIGH | BIZ/SPECIAL |
| R-N04 | 重复下单 | MEDIUM | BIZ/SPECIAL |
| R-N05 | 缓存击穿 | MEDIUM | AUX |
| R-N06 | 弱网重试 | MEDIUM | BIZ/SPECIAL/LINK |
| R-N07 | VIP 折扣叠加争议 | LOW | BIZ |
| R-N08 | 邮件服务宕机 | LOW | HINT |
| R-N09 | 监控平台 5xx | LOW | LOG |
| R-N10 | 灰度环境不一致 | LOW | BIZ/SPECIAL |