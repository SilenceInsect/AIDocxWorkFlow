# E. 汇率换算

> **子类代码**：`CURRENCY_EXCHANGE`
> **归属模块**：`AUX`
> **来源**：用户细化定义 §5「汇率换算」
>
> **测什么**：多货币换算、商城折扣、跨区服汇率、货币溢出、取整逻辑。
> **不测什么**：配置层（归 CONFIG）、业务逻辑（归 BIZ）、UI 展示（归 UI）。
> **与其他子类的差异**：E 关注"换算规则"——A 关注"通用工具"，C 关注"缓存"。

---

## 1. 典型场景

### 场景 1：充值货币换算
- 业务背景：1 元 = 10 钻石
- 涉及工具：汇率换算
- 触发动作：玩家充值 100 元
- 验证点：到账 1000 钻石

### 场景 2：绑定/代币换算
- 业务背景：绑定钻石 ↔ 自由钻石
- 触发动作：1 自由钻石 = 10 绑定钻石
- 验证点：换算正确

### 场景 3：商城折扣汇率
- 业务背景：商品原价 100 钻石，5 折
- 触发动作：玩家购买
- 验证点：支付 50 钻石

### 场景 4：兑换商店比例
- 业务背景：100 金币 = 1 钻石
- 触发动作：玩家用 1000 金币兑换
- 验证点：获得 10 钻石

### 场景 5：跨区服汇率
- 业务背景：中国服 vs 美服
- 涉及字段：汇率配置
- 触发动作：跨服交易
- 验证点：按各服汇率换算

### 场景 6：礼包比例换算
- 业务背景：礼包内容按汇率
- 触发动作：玩家购买礼包
- 验证点：礼包内货币按汇率换算

### 场景 7：货币抵扣
- 业务背景：先扣金币，余额扣钻石
- 触发动作：购买 100 钻石商品
- 验证点：先扣金币、不足扣钻石

### 场景 8：汇率变更兼容
- 业务背景：1 元 = 10 钻石 → 1 元 = 12 钻石
- 涉及字段：旧玩家数据
- 触发动作：旧玩家查看钻石
- 验证点：旧数据按新汇率重算

### 场景 9：货币溢出
- 业务背景：货币上限
- 触发动作：玩家钻石接近上限
- 验证点：超出上限截断、不溢出

### 场景 10：最小单位取整
- 业务背景：金币最小单位 1
- 触发动作：汇率换算产生小数
- 验证点：四舍五入到整数

---

## 2. 种子测试点（TP 模板）

### TP-001（CURRENCY_EXCHANGE）：充值货币换算
- **scenario**：场景 1
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：1 元 = 10 钻石
- **test_data**：玩家充值 100 元
- **expected**：到账 1000 钻石
- **notes**：注意"首充双倍"vs"普通"

### TP-002（CURRENCY_EXCHANGE）：多档位充值
- **scenario**：场景 1
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：6/30/98/198/328/648 档
- **test_data**：玩家充 648
- **expected**：到账按档位汇率计算
- **notes**：注意"档位"vs"自定义金额"

### TP-003（CURRENCY_EXCHANGE）：绑定 ↔ 自由货币
- **scenario**：场景 2
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：1 自由 = 10 绑定
- **test_data**：100 绑定 → 自由
- **expected**：10 自由（按汇率）
- **notes**：注意"双向"vs"单向"

### TP-004（CURRENCY_EXCHANGE）：商城折扣换算
- **scenario**：场景 3
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：原价 100 钻石，5 折
- **test_data**：玩家购买
- **expected**：支付 50 钻石
- **notes**：注意"百分比折扣"vs"固定折扣"

### TP-005（CURRENCY_EXCHANGE）：叠加折扣
- **scenario**：场景 3
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：VIP 8 折 + 活动 9 折
- **test_data**：原价 100
- **expected**：100 × 0.8 × 0.9 = 72
- **notes**：注意"叠加"vs"互斥"

### TP-006（CURRENCY_EXCHANGE）：兑换比例正确
- **scenario**：场景 4
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：100 金币 = 1 钻石
- **test_data**：1000 金币兑换
- **expected**：10 钻石
- **notes**：注意"双向"vs"单向"

### TP-007（CURRENCY_EXCHANGE）：跨区服汇率
- **scenario**：场景 5
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：中国服 1 元 = 10 钻石，美服 1 USD = 100 钻石
- **test_data**：跨服交易
- **expected**：按各服汇率
- **notes**：注意"汇率表"配置（归 CONFIG）

### TP-008（CURRENCY_EXCHANGE）：礼包内容换算
- **scenario**：场景 6
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：礼包 = 1 钻石 + 100 金币
- **test_data**：玩家购买礼包
- **expected**：按汇率发放
- **notes**：注意"礼包内容"配置（归 CONFIG）

### TP-009（CURRENCY_EXCHANGE）：货币抵扣顺序
- **scenario**：场景 7
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：商品 100 钻石，金币可抵
- **test_data**：玩家有 50 金币 + 50 钻石
- **expected**：先扣金币（按汇率），不足扣钻石
- **notes**：注意"抵扣顺序"配置

### TP-010（CURRENCY_EXCHANGE）：汇率变更兼容
- **scenario**：场景 8
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：旧汇率 1 元 = 10 钻石
- **test_data**：汇率改为 1 元 = 12 钻石
- **expected**：旧玩家钻石按新汇率重算
- **notes**：注意"实时重算"vs"重启重算"

### TP-011（CURRENCY_EXCHANGE）：货币溢出截断
- **scenario**：场景 9
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：钻石上限 999999
- **test_data**：玩家已有 999000，再获得 1000
- **expected**：截断到 999999、不溢出
- **notes**：注意"int 上限"vs"业务上限"

### TP-012（CURRENCY_EXCHANGE）：四舍五入
- **scenario**：场景 10
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：1 钻石 = 99 金币
- **test_data**：1 钻石 → 99 金币
- **expected**：99（精确）
- **notes**：注意"汇率"vs"业务四舍五入"

### TP-013（CURRENCY_EXCHANGE）：取整规则
- **scenario**：场景 10
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：1 钻石 = 0.5 绑钻
- **test_data**：1 钻石 → 绑钻
- **expected**：0 或 1（按设计决定）
- **notes**：注意"四舍五入"vs"向下取整"vs"向上取整"

### TP-014（CURRENCY_EXCHANGE）：货币转换不丢精度
- **scenario**：场景 1
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：0.1 + 0.2 = 0.30000000000000004
- **test_data**：多次小额充值累加
- **expected**：金额无误差
- **notes**：注意"金融精度"（用整数或 Decimal）

### TP-015（CURRENCY_EXCHANGE）：多货币混合支付
- **scenario**：场景 7
- **module**：`CURRENCY_EXCHANGE`
- **precondition**：商品 100 钻石
- **test_data**：玩家用 30 自由 + 700 绑钻（按 1:10 汇率）
- **expected**：扣款 30 自由 + 700 绑钻
- **notes**：注意"混合支付"配置

---

## 3. 边界陷阱

### 边界 1：vs CONFIG
- **混淆点**：「汇率"配置"」——E 测换算逻辑、CONFIG 测配置
- **判定规则**：测"汇率表配置" → CONFIG；测"换算计算" → E
- **实例**：汇率表字段 → CONFIG；按汇率换算 → E-001

### 边界 2：vs BIZ
- **混淆点**：「货币"逻辑"」——E 测换算、BIZ 测业务
- **判定规则**：测"换算计算" → E；测"扣款/发放业务" → BIZ
- **实例**：1 元 = 10 钻石换算 → E；充值扣款 → BIZ

### 边界 3：vs G. GM 工具
- **混淆点**：「GM"发"钻石」——E 测换算、G 测 GM
- **判定规则**：测"汇率换算" → E；测"GM 发道具" → G
- **实例**：100 元 = 1000 钻石 → E；GM 发 1000 钻石 → G

### 边界 4：vs UI
- **混淆点**：「货币"显示"」——E 测换算、UI 测显示
- **判定规则**：测"换算后数值" → E；测"数值在 UI 上显示" → UI
- **实例**：1000 钻石换算 → E-001；UI 显示 1000 钻石 → UI

---

## 4. 验证证据

### 视觉证据
- 商城商品价格显示
- 兑换界面显示

### 日志证据
- 换算日志（含汇率）
- 充值到账日志
- 抵扣日志

### 数据证据
- 玩家账户流水
- 汇率变更记录
- 溢出截断记录

### 性能证据
- 换算耗时 < 1ms
- 精度无误差
