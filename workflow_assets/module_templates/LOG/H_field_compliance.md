# H. 埋点字段合规校验

> **子类代码**：`LOG_FIELD_COMPLIANCE`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §8「埋点字段合规校验（合规 & 隐私专项补充）」
>
> **测什么**：必填字段校验（区服/角色/账号/时间戳/设备/渠道/版本/事件 ID）、隐私脱敏（手机/实名/设备 ID 加密）、渠道规范对齐（SDK 字段名/枚举统一）、合规过滤（敏感行为禁止采集/未成年人数据隔离）。
> **不测什么**：行为埋点业务规则（归 A）、埋点底层采集（归 AUX）、隐私合规法务（项目外）、存储加密（归 AUX M）。
> **与其他子类的差异**：H 关注"**埋点字段合规 & 隐私**规范"——A 关注"埋点业务触发"，D 关注"指标聚合"，F 关注"存储分层"。

---

## 1. 典型场景

### 场景 1：必填字段校验
- 业务背景：所有埋点
- 涉及字段：必填集
- 触发动作：埋点
- 验证点：必填字段齐全

### 场景 2：区服字段
- 业务背景：多区服
- 涉及字段：server_id
- 触发动作：埋点
- 验证点：含 server_id

### 场景 3：角色 ID
- 业务背景：多角色
- 涉及字段：role_id
- 触发动作：埋点
- 验证点：含 role_id

### 场景 4：账号 ID
- 业务背景：账号
- 涉及字段：account_id
- 触发动作：埋点
- 验证点：含 account_id

### 场景 5：时间戳
- 业务背景：埋点
- 涉及字段：timestamp
- 触发动作：埋点
- 验证点：含 timestamp

### 场景 6：设备字段
- 业务背景：iOS/Android
- 涉及字段：device
- 触发动作：埋点
- 验证点：含 device

### 场景 7：渠道字段
- 业务背景：渠道
- 涉及字段：channel_id
- 触发动作：埋点
- 验证点：含 channel_id

### 场景 8：版本号
- 业务背景：版本
- 涉及字段：client_version
- 触发动作：埋点
- 验证点：含 client_version

### 场景 9：事件 ID
- 业务背景：埋点
- 涉及字段：event_id
- 触发动作：埋点
- 验证点：含 event_id

### 场景 10：手机号脱敏
- 业务背景：日志含手机号
- 涉及字段：phone
- 触发动作：写入
- 验证点：手机号脱敏

### 场景 11：实名脱敏
- 业务背景：日志含实名
- 涉及字段：real_name
- 触发动作：写入
- 验证点：实名脱敏

### 场景 12：设备 ID 加密
- 业务背景：日志含设备 ID
- 涉及字段：device_id
- 触发动作：写入
- 验证点：设备 ID 加密

### 场景 13：渠道 SDK 规范
- 业务背景：苹果/安卓
- 涉及字段：字段名
- 触发动作：上报
- 验证点：字段名规范

### 场景 14：枚举值统一
- 业务背景：渠道枚举
- 涉及字段：channel
- 触发动作：上报
- 验证点：枚举统一

### 场景 15：禁止采集敏感行为
- 业务背景：聊天
- 涉及字段：内容
- 触发动作：禁止
- 验证点：不采集聊天内容

### 场景 16：未成年人隔离
- 业务背景：未成年
- 涉及字段：age
- 触发动作：上报
- 验证点：未成年数据隔离

### 场景 17：GDPR 合规
- 业务背景：海外
- 涉及字段：consent
- 触发动作：采集
- 验证点：用户同意

### 场景 18：字段类型校验
- 业务背景：埋点
- 涉及字段：type
- 触发动作：埋点
- 验证点：类型正确

### 场景 19：字段长度
- 业务背景：埋点
- 涉及字段：长度
- 触发动作：埋点
- 验证点：长度限制

### 场景 20：合规告警
- 业务背景：不合规
- 涉及字段：合规
- 触发动作：触发
- 验证点：告警

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_FIELD_COMPLIANCE）：必填字段
- **scenario**：场景 1
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：埋点
- **test_data**：观察字段
- **expected**：必填字段齐全
- **notes**：注意"必填"vs"可空"

### TP-002（LOG_FIELD_COMPLIANCE）：区服字段
- **scenario**：场景 2
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：多服
- **test_data`：埋点
- **expected`：含 `server_id`
- **notes**：注意"区服"vs"渠道"

### TP-003（LOG_FIELD_COMPLIANCE）：角色 ID
- **scenario**：场景 3
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：多角色
- **test_data`：埋点
- **expected`：含 `role_id`
- **notes**：注意"角色"vs"账号"

### TP-004（LOG_FIELD_COMPLIANCE）：账号 ID
- **scenario**：场景 4
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：账号
- **test_data`：埋点
- **expected`：含 `account_id`
- **notes**：注意"账号"vs"角色"

### TP-005（LOG_FIELD_COMPLIANCE）：时间戳
- **scenario**：场景 5
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：埋点
- **test_data`：观察
- **expected`：含 `timestamp` ISO 8601
- **notes**：注意"时区"+"格式"

### TP-006（LOG_FIELD_COMPLIANCE）：设备字段
- **scenario**：场景 6
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：iOS/Android
- **test_data`：埋点
- **expected`：含 `device_model/os/version`
- **notes**：注意"机型"+"OS"

### TP-007（LOG_FIELD_COMPLIANCE）：渠道字段
- **scenario**：场景 7
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：多渠道
- **test_data`：埋点
- **expected`：含 `channel_id`
- **notes**：注意"渠道"vs"大区"

### TP-008（LOG_FIELD_COMPLIANCE）：版本号
- **scenario**：场景 8
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：版本
- **test_data`：埋点
- **expected`：含 `client_version`
- **notes**：注意"客户端"vs"服务端"

### TP-009（LOG_FIELD_COMPLIANCE）：事件 ID
- **scenario**：场景 9
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：埋点
- **test_data`：观察
- **expected`：含 `event_id` 唯一
- **notes**：注意"事件"vs"操作"

### TP-010（LOG_FIELD_COMPLIANCE）：手机号脱敏
- **scenario**：场景 10
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：日志含手机号
- **test_data`：写入
- **expected**：脱敏为 `138****5678`
- **notes**：注意"脱敏"vs"加密"

### TP-011（LOG_FIELD_COMPLIANCE）：实名脱敏
- **scenario**：场景 11
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：日志含实名
- **test_data`：写入
- **expected`：脱敏为 `张*`
- **notes**：注意"实名"vs"昵称"

### TP-012（LOG_FIELD_COMPLIANCE）：设备 ID 加密
- **scenario**：场景 12
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition`：设备 ID
- **test_data`：写入
- **expected`：加密为 hash
- **notes**：注意"加密"vs"脱敏"

### TP-013（LOG_FIELD_COMPLIANCE）：苹果 SDK 字段
- **scenario**：场景 13
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：苹果渠道
- **test_data`：上报
- **expected`：字段名匹配苹果规范
- **notes**：注意"平台差异"

### TP-014（LOG_FIELD_COMPLIANCE）：安卓 SDK 字段
- **scenario**：场景 13
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：安卓渠道
- **test_data`：上报
- **expected`：字段名匹配安卓规范
- **notes**：注意"平台差异"

### TP-015（LOG_FIELD_COMPLIANCE）：枚举统一
- **scenario**：场景 14
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：枚举
- **test_data`：观察
- **expected`：枚举值统一
- **notes**：注意"iOS"vs"ios"vs"IOS"

### TP-016（LOG_FIELD_COMPLIANCE）：禁止采集聊天
- **scenario**：场景 15
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition`：聊天
- **test_data`：尝试
- **expected`：拦截、不采集
- **notes**：注意"敏感"+"禁止"

### TP-016+1（LOG_FIELD_COMPLIANCE）：禁止采集密码
- **scenario**：场景 15
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：密码
- **test_data**：尝试
- **expected`：拦截
- **notes**：注意"密码"+"敏感"

### TP-017（LOG_FIELD_COMPLIANCE）：未成年人隔离
- **scenario**：场景 16
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：未成年
- **test_data`：观察
- **expected`：数据单独存储
- **notes**：注意"隔离"vs"删除"

### TP-018（LOG_FIELD_COMPLIANCE）：GDPR 同意
- **scenario**：场景 17
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：海外用户
- **test_data`：未同意
- **expected`：不采集
- **notes**：注意"同意"vs"默认"

### TP-019（LOG_FIELD_COMPLIANCE）：字段类型
- **scenario**：场景 18
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition`：埋点
- **test_data`：观察类型
- **expected`：类型符合 schema
- **notes**：注意"类型"vs"格式"

### TP-020（LOG_FIELD_COMPLIANCE）：字段长度
- **scenario**：场景 19
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition`：埋点
- **test_data`：超长
- **expected`：截断
- **notes**：注意"长度"+"截断"

### TP-021（LOG_FIELD_COMPLIANCE）：合规告警
- **scenario**：场景 20
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：不合规
- **test_data`：触发
- **expected`：告警
- **notes**：注意"告警"vs"阻断"

### TP-022（LOG_FIELD_COMPLIANCE）：必填缺失拦截
- **scenario**：场景 1
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：缺 server_id
- **test_data`：埋点
- **expected**：拦截 + 告警
- **notes**：注意"拦截"vs"补全"

### TP-023（LOG_FIELD_COMPLIANCE）：隐私分级
- **scenario**：场景 10
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：敏感数据
- **test_data`：分级
- **expected`：高敏脱敏、低敏可保留
- **notes**：注意"分级"vs"一刀切"

### TP-024（LOG_FIELD_COMPLIANCE）：玩家主动删除
- **scenario**：场景 17
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：玩家请求删除
- **test_data`：`delete_my_data(player_id)`
- **expected`：数据删除
- **notes**：注意"被遗忘权"

### TP-025（LOG_FIELD_COMPLIANCE）：未成年人保护
- **scenario**：场景 16
- **module**：`LOG_FIELD_COMPLIANCE`
- **precondition**：未成年
- **test_data`：观察
- **expected`：防沉迷数据独立、限时
- **notes**：注意"防沉迷"vs"采集"

---

## 3. 边界陷阱

### 边界 1：vs A. 行为埋点
- **混淆点**：「埋点"字段"」——A 测业务触发、H 测合规
- **判定规则**：测"埋点业务" → A；测"字段合规" → H
- **实例**：购买埋点 → A；手机号脱敏 → H

### 边界 2：vs D. 监控
- **混淆点**：「埋点"指标"」——D 测指标、H 测字段
- **判定规则**：测"指标聚合" → D；测"字段合规" → H
- **实例**：CCU 指标 → D；必填字段 → H

### 边界 3：vs AUX M. 加密
- **混淆点**：「脱敏"加密"」——H 测合规、AUX M 测加密
- **判定规则**：测"脱敏规则" → H；测"加密算法" → AUX M
- **实例**：手机号脱敏 → H；AES 加密 → AUX M

### 边界 4：vs F. 存储
- **混淆点**：「日志"存储"」——F 测存储、H 测字段
- **判定规则**：测"日志存储" → F；测"字段合规" → H
- **实例**：日志分片 → F；脱敏存储 → H

### 边界 5：vs B. 资产
- **混淆点**：「资产"日志"」——B 测资产、H 测字段
- **判定规则**：测"资产对账" → B；测"字段合规" → H
- **实例**：资产流水 → B；交易脱敏 → H

---

## 4. 验证证据

### 视觉证据
- 合规扫描报告截图
- 脱敏日志样本

### 日志证据
- `FIELD_CHECK missing=server_id`
- `PRIVACY_MASK type=phone mask=****`
- `COMPLIANCE_ALERT type=field_missing`
- `CONSENT_REQUIRED type=gdpr`

### 数据证据
- 字段必填率 = 100%
- 脱敏覆盖率 = 100%
- 渠道字段规范匹配率 = 100%
- 隐私分级表
- 未成年人数据隔离率
- GDPR 同意率

### 性能证据
- 字段校验 < 1ms
- 脱敏 < 1ms
- 合规扫描 < 1min
- 必填缺失告警 < 1s
