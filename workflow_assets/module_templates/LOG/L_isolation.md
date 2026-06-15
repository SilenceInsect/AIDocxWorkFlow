# L. 多语言/多渠道日志隔离

> **子类代码**：`LOG_ISOLATION`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §12「多语言 / 多渠道日志隔离（原定义完全缺失，新增）」
>
> **测什么**：渠道分包日志隔离、灰度白名单日志区分、测试服/正式服日志存储隔离、数据互不污染。
> **不测什么**：渠道业务（归 LINK）、灰度业务（归 BIZ）、测试服业务（归 LINK）、日志底层存储（归 F）。
> **与其他子类的差异**：L 关注"**多环境/多渠道日志隔离**"——H 关注"字段合规"，F 关注"存储分层"，K 关注"第三方交互"。

---

## 1. 典型场景

### 场景 1：iOS 包日志
- 业务背景：iOS 玩家
- 涉及数据：iOS
- 触发动作：日志
- 验证点：iOS 标签

### 场景 2：Android 包日志
- 业务背景：Android 玩家
- 涉及数据：Android
- 触发动作：日志
- 验证点：Android 标签

### 场景 3：iOS 与 Android 隔离
- 业务背景：跨平台
- 涉及数据：双端
- 触发动作：日志
- 验证点：数据不混

### 场景 4：渠道 A 日志
- 业务背景：渠道 A
- 涉及数据：A
- 触发动作：日志
- 验证点：A 标签

### 场景 5：渠道 B 日志
- 业务背景：渠道 B
- 涉及数据：B
- 触发动作：日志
- 验证点：B 标签

### 场景 6：渠道 A 与 B 隔离
- 业务背景：跨渠道
- 涉及数据：多渠道
- 触发动作：日志
- 验证点：不混

### 场景 7：灰度白名单
- 业务背景：白名单玩家
- 涉及数据：白名单
- 触发动作：日志
- 验证点：白名单标签

### 场景 8：非白名单
- 业务背景：非白名单
- 涉及数据：常规
- 触发动作：日志
- 验证点：常规标签

### 场景 9：测试服日志
- 业务背景：测试服
- 涉及数据：test
- 触发动作：日志
- 验证点：test 标签

### 场景 10：正式服日志
- 业务背景：正式服
- 涉及数据：prod
- 触发动作：日志
- 验证点：prod 标签

### 场景 11：测试服与正式服隔离
- 业务背景：跨环境
- 涉及数据：env
- 触发动作：日志
- 验证点：数据不混

### 场景 12：服 1 日志
- 业务背景：服 1
- 涉及数据：server
- 触发动作：日志
- 验证点：server 标签

### 场景 13：服 2 日志
- 业务背景：服 2
- 涉及数据：server
- 触发动作：日志
- 验证点：server 标签

### 场景 14：多语言 i18n
- 业务背景：海外
- 涉及数据：i18n
- 触发动作：日志
- 验证点：i18n 标签

### 场景 15：时区隔离
- 业务背景：多时区
- 涉及数据：tz
- 触发动作：日志
- 验证点：tz 标签

### 场景 16：货币隔离
- 业务背景：多币种
- 涉及数据：currency
- 触发动作：日志
- 验证点：currency 标签

### 场景 17：版本隔离
- 业务背景：多版本
- 涉及数据：version
- 触发动作：日志
- 验证点：version 标签

### 场景 18：渠道-平台交叉
- 业务背景：iOS + 渠道 A
- 涉及数据：组合
- 触发动作：日志
- 验证点：组合标签

### 场景 19：日志不可跨服读
- 业务背景：跨服查日志
- 涉及数据：隔离
- 触发动作：查询
- 验证点：拒绝

### 场景 20：日志聚合查询
- 业务背景：聚合
- 涉及数据：跨渠道
- 触发动作：聚合
- 验证点：可聚合

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_ISOLATION）：iOS 标签
- **scenario**：场景 1
- **module**：`LOG_ISOLATION`
- **precondition**：iOS 包
- **test_data`：登录
- **expected`：日志含 `platform=ios`
- **notes**：注意"平台"vs"渠道"

### TP-002（LOG_ISOLATION）：Android 标签
- **scenario**：场景 2
- **module**：`LOG_ISOLATION`
- **precondition**：Android 包
- **test_data`：登录
- **expected**：日志含 `platform=android`
- **notes**：注意"包名"+"标签"

### TP-003（LOG_ISOLATION）：iOS vs Android 不混
- **scenario**：场景 3
- **module**：`LOG_ISOLATION`
- **precondition**：iOS + Android 玩家
- **test_data`：观察
- **expected`：iOS 日志仅 iOS、Android 日志仅 Android
- **notes**：注意"隔离"vs"合并"

### TP-004（LOG_ISOLATION）：渠道 A
- **scenario**：场景 4
- **module**：`LOG_ISOLATION`
- **precondition`：渠道 A
- **test_data`：登录
- **expected`：日志含 `channel=A`
- **notes**：注意"渠道"vs"平台"

### TP-005（LOG_ISOLATION）：渠道 B
- **scenario**：场景 5
- **module**：`LOG_ISOLATION`
- **precondition`：渠道 B
- **test_data`：登录
- **expected`：日志含 `channel=B`
- **notes**：注意"渠道"+"隔离"

### TP-006（LOG_ISOLATION）：A vs B 不混
- **scenario**：场景 6
- **module**：`LOG_ISOLATION`
- **precondition`：A+B
- **test_data`：观察
- **expected`：A 日志仅 A、B 日志仅 B
- **notes**：注意"渠道"+"数据"

### TP-007（LOG_ISOLATION）：白名单标签
- **scenario**：场景 7
- **module**：`LOG_ISOLATION`
- **precondition`：白名单
- **test_data`：登录
- **expected`：日志含 `whitelist=true`
- **notes**：注意"白名单"vs"灰度"

### TP-008（LOG_ISOLATION）：非白名单
- **scenario**：场景 8
- **module**：`LOG_ISOLATION`
- **precondition`：常规
- **test_data`：登录
- **expected`：日志含 `whitelist=false`
- **notes**：注意"标签"+"区分"

### TP-009（LOG_ISOLATION）：测试服
- **scenario**：场景 9
- **module**：`LOG_ISOLATION`
- **precondition`：test 服
- **test_data`：登录
- **expected`：日志含 `env=test`
- **notes**：注意"环境"+"标签"

### TP-010（LOG_ISOLATION）：正式服
- **scenario**：场景 10
- **module**：`LOG_ISOLATION`
- **precondition`：prod 服
- **test_data`：登录
- **expected`：日志含 `env=prod`
- **notes**：注意"环境"+"标签"

### TP-011（LOG_ISOLATION）：test vs prod 不混
- **scenario**：场景 11
- **module**：`LOG_ISOLATION`
- **precondition`：双环境
- **test_data`：观察
- **expected`：test 仅 test、prod 仅 prod
- **notes**：注意"环境"+"隔离"

### TP-012（LOG_ISOLATION）：服 1 标签
- **scenario**：场景 12
- **module**：`LOG_ISOLATION`
- **precondition`：服 1
- **test_data`：登录
- **expected`：日志含 `server_id=1`
- **notes**：注意"区服"+"标签"

### TP-013（LOG_ISOLATION）：服 2 标签
- **scenario**：场景 13
- **module**：`LOG_ISOLATION`
- **precondition`：服 2
- **test_data`：登录
- **expected`：日志含 `server_id=2`
- **notes**：注意"区服"+"隔离"

### TP-014（LOG_ISOLATION）：i18n 标签
- **scenario**：场景 14
- **module**：`LOG_ISOLATION`
- **precondition`：海外
- **test_data`：登录
- **expected`：日志含 `locale=zh_CN/en_US`
- **notes**：注意"语言"vs"国家"

### TP-015（LOG_ISOLATION）：时区标签
- **scenario**：场景 15
- **module**：`LOG_ISOLATION`
- **precondition**：多时区
- **test_data`：登录
- **expected`：日志含 `tz=UTC+8/UTC+0`
- **notes**：注意"时区"+"标签"

### TP-016（LOG_ISOLATION）：币种标签
- **scenario**：场景 16
- **module**：`LOG_ISOLATION`
- **precondition`：多币种
- **test_data`：充值
- **expected`：日志含 `currency=CNY/USD`
- **notes**：注意"币种"+"隔离"

### TP-017（LOG_ISOLATION）：版本标签
- **scenario**：场景 17
- **module**：`LOG_ISOLATION`
- **precondition`：多版本
- **test_data`：登录
- **expected`：日志含 `client_version=1.2.3`
- **notes**：注意"版本"+"区分"

### TP-018（LOG_ISOLATION）：iOS+A 组合
- **scenario**：场景 18
- **module**：`LOG_ISOLATION`
- **precondition`：iOS + 渠道 A
- **test_data`：登录
- **expected`：日志含 `platform=ios, channel=A`
- **notes**：注意"组合"+"标签"

### TP-019（LOG_ISOLATION）：跨服查询拒绝
- **scenario**：场景 19
- **module**：`LOG_ISOLATION`
- **precondition**：服 1
- **test_data`：查服 2 日志
- **expected**：拒绝
- **notes**：注意"权限"+"拒绝"

### TP-020（LOG_ISOLATION）：跨服聚合允许
- **scenario**：场景 20
- **module**：`LOG_ISOLATION`
- **precondition`：管理员
- **test_data`：聚合查询
- **expected`：聚合结果
- **notes**：注意"权限"+"聚合"

### TP-021（LOG_ISOLATION）：灰度比例
- **scenario**：场景 7
- **module**：`LOG_ISOLATION`
- **precondition`：灰度 10%
- **test_data`：1000 玩家
- **expected`：约 100 玩家带 `whitelist=true`
- **notes**：注意"灰度"+"比例"

### TP-022（LOG_ISOLATION）：测试服数据清理
- **scenario**：场景 9
- **module**：`LOG_ISOLATION`
- **precondition`：测试服结束
- **test_data`：清理
- **expected`：测试服日志清理
- **notes**：注意"清理"vs"保留"

### TP-023（LOG_ISOLATION）：渠道差异
- **scenario**：场景 4
- **module**：`LOG_ISOLATION`
- **precondition`：多渠道
- **test_data`：观察
- **expected`：A 渠道日志仅 A、B 仅 B
- **notes**：注意"渠道"+"数据"

### TP-024（LOG_ISOLATION）：跨服玩家日志
- **scenario**：场景 12
- **module**：`LOG_ISOLATION`
- **precondition`：玩家切服
- **test_data`：观察
- **expected`：每服带 `server_id` 标签
- **notes**：注意"切服"+"标签"

### TP-025（LOG_ISOLATION）：跨服对账隔离
- **scenario**：场景 19
- **module**：`LOG_ISOLATION`
- **precondition`：服 1 + 服 2
- **test_data`：对账
- **expected`：仅同服对账
- **notes**：注意"对账"+"范围"

---

## 3. 边界陷阱

### 边界 1：vs LINK 渠道
- **混淆点**：「渠道"业务"」——LINK 测业务、L 测日志隔离
- **判定规则**：测"渠道业务" → LINK；测"渠道日志隔离" → L
- **实例**：渠道业务 → LINK；渠道日志 → L

### 边界 2：vs BIZ. 业务
- **混淆点**：「灰度"业务"」——BIZ 测业务、L 测日志
- **判定规则**：测"灰度业务" → BIZ；测"灰度日志" → L
- **实例**：灰度新功能 → BIZ；灰度日志 → L

### 边界 3：vs F. 存储
- **混淆点**：「多环境"存储"」——F 测存储、L 测隔离
- **判定规则**：测"存储分层" → F；测"环境隔离" → L
- **实例**：磁盘分层 → F；环境隔离 → L

### 边界 4：vs H. 合规
- **混淆点**：「合规"标签"」——H 测合规字段、L 测隔离
- **判定规则**：测"合规字段" → H；测"标签隔离" → L
- **实例**：必填字段 → H；env 标签 → L

### 边界 5：vs D. 监控
- **混淆点**：「跨服"指标"」——D 测指标、L 测隔离
- **判定规则**：测"跨服聚合" → D；测"跨服隔离" → L
- **实例**：跨服 CCU 指标 → D；跨服日志不可互读 → L

---

## 4. 验证证据

### 视觉证据
- 多环境日志管理后台截图
- 渠道分布截图

### 日志证据
- `platform=ios/android`
- `channel=A/B/...`
- `whitelist=true/false`
- `env=test/prod`
- `server_id=1/2/...`
- `locale=zh_CN/en_US`
- `tz=UTC+8`
- `currency=CNY/USD`

### 数据证据
- 多环境日志表（按 env 分表或分字段）
- 渠道日志表（按 channel 分）
- 灰度日志表（按 whitelist 分）
- 跨服查询权限
- 跨环境数据不混

### 性能证据
- 多环境查询 < 1s
- 跨服聚合 < 5s
- 标签过滤 < 100ms
- 跨环境查询拒绝 < 10ms
