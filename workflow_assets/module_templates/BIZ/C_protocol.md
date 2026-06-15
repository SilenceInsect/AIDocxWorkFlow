# C. 协议交互

> **子类代码**：`BIZ_PROTOCOL`
> **归属模块**：`BIZ`
> **来源**：用户细化定义 §3「协议交互」
>
> **测什么**：前后端协议的基础字段校验、交互场景覆盖、异常协议拦截、标准错误码体系。
> **不测什么**：网络底层收发包（归 AUX B）、业务逻辑（归 A）、数据链路（归 B）。
> **与其他子类的差异**：C 关注"协议字段+错误码"——B 关注"链路数据"，A 关注"业务"，SPECIAL 关注"高频/重复/伪造包"。

---

## 1. 典型场景

### 场景 1：协议字段齐全性
- 业务背景：所有客户端上行协议
- 涉及字段：必填字段、可选字段
- 触发动作：缺字段/多余字段
- 验证点：服务端按协议文档校验

### 场景 2：字段类型匹配
- 业务背景：int / string / enum / array
- 涉及字段：类型定义
- 触发动作：发错类型
- 验证点：服务端类型校验拦截

### 场景 3：枚举值统一
- 业务背景：协议中的 enum 字段
- 涉及字段：枚举值集合
- 触发动作：发非法枚举
- 验证点：拦截 + 不接受未定义值

### 场景 4：可选字段缺省兜底
- 业务背景：可空字段
- 涉及字段：nullable 字段
- 触发动作：不传该字段
- 验证点：服务端用默认值处理

### 场景 5：超长/空参数容错
- 业务背景：玩家名、聊天内容
- 涉及字段：字符串长度
- 触发动作：发 1MB 字符串 / 空字符串
- 验证点：服务端容错

### 场景 6：协议版本兼容
- 业务背景：旧客户端连新服、新客户端连旧服
- 涉及字段：协议号、版本号
- 触发动作：模拟不同版本客户端
- 验证点：协议号匹配、字段缺失优雅降级

### 场景 7：同步请求-应答
- 业务背景：商城购买、任务领取
- 涉及字段：req/resp 配对
- 触发动作：客户端发起请求
- 验证点：服务端正确应答

### 场景 8：异步推送
- 业务背景：道具变动、活动开启
- 涉及字段：push 包
- 触发动作：服务端主动推
- 验证点：客户端正确解析

### 场景 9：长连接心跳保活
- 业务背景：客户端-服务端长连接
- 涉及字段：heartbeat 包
- 触发动作：30s 一次心跳
- 验证点：连接保持

### 场景 10：断线重连协议重传
- 业务背景：断线 30s 后重连
- 涉及字段：seq 号、重传包
- 触发动作：断线重连
- 验证点：断线期间消息不丢失

### 场景 11：批量协议打包
- 业务背景：批量发奖、批量查询
- 涉及字段：array 类型
- 触发动作：发 100 条批量协议
- 验证点：服务端按 array 处理

### 场景 12：错误码体系
- 业务背景：所有业务失败
- 涉及字段：错误码 + 错误描述
- 触发动作：触发每种业务失败
- 验证点：返回标准错误码、客户端正确显示

### 场景 13：非法协议拦截
- 业务背景：伪造包、未知协议号
- 涉及字段：协议号
- 触发动作：发协议号 = 99999
- 验证点：拦截 + 断开连接

### 场景 14：越权请求拦截
- 业务背景：玩家 A 调"删除玩家 B"协议
- 涉及字段：player_id 参数
- 触发动作：玩家 A 操作玩家 B 数据
- 验证点：服务端校验 owner

---

## 2. 种子测试点（TP 模板）

### TP-001（BIZ_PROTOCOL）：必填字段缺失
- **scenario**：场景 1
- **module**：`BIZ_PROTOCOL`
- **precondition**：购买协议必填 `item_id, count`
- **test_data**：缺 `count`
- **expected**：拦截 + 错误码 `PARAM_MISSING` + 错误描述
- **notes**：注意"必填"vs"可空"+"默认值"

### TP-002（BIZ_PROTOCOL）：多余字段忽略
- **scenario**：场景 1
- **module**：`BIZ_PROTOCOL`
- **precondition**：购买协议字段集
- **test_data**：加 `extra_field=xxx` 字段
- **expected**：服务端忽略多余字段
- **notes**：注意"忽略"vs"严格模式"+"扩展性"

### TP-003（BIZ_PROTOCOL）：字段类型错误
- **scenario**：场景 2
- **module**：`BIZ_PROTOCOL`
- **precondition**：`count` 字段 int 类型
- **test_data**：`count = "abc"` / `[1,2]` / `null`
- **expected**：拦截 + 错误码 `PARAM_TYPE_INVALID`
- **notes**：注意"int"vs"int64"vs"long"

### TP-004（BIZ_PROTOCOL）：枚举值非法
- **scenario**：场景 3
- **module**：`BIZ_PROTOCOL`
- **precondition**：`currency_type` 枚举值 = `{GOLD, DIAMOND, TICKET}`
- **test_data**：`currency_type = "BITCOIN"`
- **expected**：拦截 + 错误码 `ENUM_INVALID`
- **notes**：注意"大小写"（"gold"vs"GOLD"）

### TP-005（BIZ_PROTOCOL）：可空字段缺省
- **scenario**：场景 4
- **module**：`BIZ_PROTOCOL`
- **precondition**：`comment` 字段可空
- **test_data**：不传 `comment`
- **expected**：服务端用 `""` 处理、不报错
- **notes**：注意"可空"vs"有默认"vs"必填"

### TP-006（BIZ_PROTOCOL）：超长字符串
- **scenario**：场景 5
- **module**：`BIZ_PROTOCOL`
- **precondition**：玩家名最长 32 字符
- **test_data**：`player_name = 1MB 字符串`
- **expected**：拦截 + 错误码 `PARAM_TOO_LONG`
- **notes**：注意"协议体大小"vs"字段长度"+"资源耗尽防护"

### TP-007（BIZ_PROTOCOL）：空字符串
- **scenario**：场景 5
- **module**：`BIZ_PROTOCOL`
- **precondition**：聊天消息必填
- **test_data**：`message = ""`
- **expected**：拦截 + 错误码 `PARAM_EMPTY`
- **notes**：注意"空字符串"vs"纯空格"vs"null"

### TP-008（BIZ_PROTOCOL）：客户端版本兼容
- **scenario**：场景 6
- **module**：`BIZ_PROTOCOL`
- **precondition**：旧版协议 v1.0、新版协议 v1.1
- **test_data**：旧客户端发 v1.0 协议到 v1.1 服务端
- **expected**：服务端识别 v1.0、缺字段用默认值
- **notes**：注意"协议号"vs"字段集"+"灰度"

### TP-009（BIZ_PROTOCOL）：新字段优雅降级
- **scenario**：场景 6
- **module**：`BIZ_PROTOCOL`
- **precondition**：旧服务端不支持 `new_feature_id`
- **test_data**：新客户端发含 `new_feature_id` 协议
- **expected**：服务端忽略新字段、不影响主流程
- **notes**：注意"前向兼容"vs"后向兼容"

### TP-010（BIZ_PROTOCOL）：同步应答
- **scenario**：场景 7
- **module**：`BIZ_PROTOCOL`
- **precondition**：购买协议
- **test_data**：发 `purchase` 请求
- **expected**：服务端返回 `{result: 0, item_id, count, balance}`
- **notes**：注意"成功"vs"失败"应答结构

### TP-011（BIZ_PROTOCOL）：异步推送格式
- **scenario**：场景 8
- **module**：`BIZ_PROTOCOL`
- **precondition**：道具变动推送协议
- **test_data**：服务端发推送
- **expected**：客户端正确解析 `push_type, item_id, change_count`
- **notes**：注意"主动推"vs"拉取"+"字段顺序"

### TP-012（BIZ_PROTOCOL）：心跳保活
- **scenario**：场景 9
- **module**：`BIZ_PROTOCOL`
- **precondition**：长连接空闲
- **test_data**：30s 无心跳
- **expected**：服务端断开连接、客户端收到断开事件
- **notes**：注意"心跳超时"vs"业务超时"

### TP-013（BIZ_PROTOCOL）：断线重传
- **scenario**：场景 10
- **module**：`BIZ_PROTOCOL`
- **precondition**：断线前 seq=100
- **test_data**：断线 30s 后重连
- **expected**：客户端拉取 seq=101 之后所有消息、不丢失
- **notes**：注意"seq 持久化"vs"消息持久化"

### TP-014（BIZ_PROTOCOL）：批量协议
- **scenario**：场景 11
- **module**：`BIZ_PROTOCOL`
- **precondition**：批量发奖协议
- **test_data**：`rewards = [{player_id, item_id, count}, ...]` 1000 条
- **expected**：服务端正确解析、1000 笔全部发放
- **notes**：注意"批量大小"限制（防单包过大）

### TP-015（BIZ_PROTOCOL）：高频协议性能
- **scenario**：场景 11
- **module**：`BIZ_PROTOCOL`
- **precondition**：战斗帧 30/s
- **test_data**：30s 推 900 帧
- **expected**：P99 延迟 < 200ms
- **notes**：与 SPECIAL 高频包配合

### TP-016（BIZ_PROTOCOL）：错误码体系
- **scenario**：场景 12
- **module**：`BIZ_PROTOCOL`
- **precondition**：所有业务失败场景
- **test_data**：触发 10 种失败（资源不足/等级不够/活动过期/重复领取...）
- **expected**：每种失败返回对应标准错误码、客户端按错误码显示文案
- **notes**：注意"错误码"vs"错误描述"+"i18n"

### TP-017（BIZ_PROTOCOL）：错误码客户端解析
- **scenario**：场景 12
- **module**：`BIZ_PROTOCOL`
- **precondition**：服务端返回 `NOT_ENOUGH_CURRENCY`
- **test_data**：客户端收到
- **expected**：客户端显示"钻石不足，请充值"
- **notes**：注意"错误码映射表"+"多语言"

### TP-018（BIZ_PROTOCOL）：未知协议号
- **scenario**：场景 13
- **module**：`BIZ_PROTOCOL`
- **precondition**：协议号集合 {1000-2000}
- **test_data**：发协议号 = 99999
- **expected**：拦截 + 错误码 `UNKNOWN_PROTOCOL` + 断开
- **notes**：注意"未知协议"vs"已废弃协议"

### TP-019（BIZ_PROTOCOL）：伪造参数
- **scenario**：场景 13
- **module**：`BIZ_PROTOCOL`
- **precondition**：玩家 A 登录态
- **test_data**：伪造 `player_id = B_player_id`
- **expected**：服务端校验 token 中的 player_id、不匹配拦截
- **notes**：注意"签名"vs"加密"+"重放攻击"

### TP-020（BIZ_PROTOCOL）：越权请求
- **scenario**：场景 14
- **module**：`BIZ_PROTOCOL`
- **precondition**：玩家 A token
- **test_data**：玩家 A 调"删除玩家 B 邮件"协议
- **expected**：拦截 + 错误码 `NO_PERMISSION`
- **notes**：注意"owner 校验"+"协议级"vs"业务级"

### TP-021（BIZ_PROTOCOL）：协议体大小限制
- **scenario**：场景 5
- **module**：`BIZ_PROTOCOL`
- **precondition**：协议体上限 64KB
- **test_data**：发 1MB 协议体
- **expected**：服务端拒绝接收 + 断开连接
- **notes**：注意"DDoS 防护"

### TP-022（BIZ_PROTOCOL）：协议加密校验
- **scenario**：场景 13
- **module**：`BIZ_PROTOCOL`
- **precondition**：协议 AES 加密
- **test_data**：用错误密钥加密的协议
- **expected**：拦截 + 错误码 `DECRYPT_FAILED`
- **notes**：与 AUX M 加密配合

### TP-023（BIZ_PROTOCOL）：废弃协议
- **scenario**：场景 6
- **module**：`BIZ_PROTOCOL`
- **precondition**：协议 1001 已废弃
- **test_data**：客户端发协议 1001
- **expected**：服务端返回 `PROTOCOL_DEPRECATED` + 新协议号
- **notes**：注意"强制升级"vs"灰度废弃"

### TP-024（BIZ_PROTOCOL）：错误码穷举
- **scenario**：场景 12
- **module**：`BIZ_PROTOCOL`
- **precondition**：错误码表 100 个
- **test_data**：触发每种业务失败
- **expected**：100 个错误码均被覆盖、无遗漏
- **notes**：注意"错误码覆盖率" 100%

### TP-025（BIZ_PROTOCOL）：协议号分布
- **scenario**：场景 13
- **module**：`BIZ_PROTOCOL`
- **precondition**：协议号 1-30000
- **test_data**：边界值 0、-1、30001
- **expected**：全部拦截
- **notes**：注意"协议号空间"

---

## 3. 边界陷阱

### 边界 1：vs B. 数据流
- **混淆点**：「参数"非法"」——B 测数据流、C 测协议
- **判定规则**：测"协议字段格式" → C；测"数据链路传输" → B
- **实例**：协议字段类型错 → C-003；上行参数链路 → B-001

### 边界 2：vs AUX M. 加密安全
- **混淆点**：「协议"加密"」——C 测协议字段、M 测加密
- **判定规则**：测"协议解密失败" → C；测"加密算法本身" → AUX M
- **实例**：错误密钥拦截 → C-022；AES 加解密一致性 → AUX M

### 边界 3：vs SPECIAL. 高频/伪造
- **混淆点**：「高频"包"」——C 测协议格式、SPECIAL 测行为
- **判定规则**：测"协议性能" → C；测"高频包行为后果" → SPECIAL
- **实例**：高频帧延迟 → C-015；高频包导致封号 → SPECIAL

### 边界 4：vs LINK. 跨服务
- **混淆点**：「跨服"协议"」——C 测协议、LIN K 测跨服务
- **判定规则**：测"协议字段" → C；测"跨服务调用" → LINK
- **实例**：跨服协议字段 → C；跨服数据一致性 → LINK

### 边界 5：vs A. 业务
- **混淆点**：「错误码"业务"」——A 测业务、C 测协议
- **判定规则**：测"业务逻辑" → A；测"错误码体系" → C
- **实例**：购买扣款 → A；错误码映射 → C-016

---

## 4. 验证证据

### 视觉证据
- 客户端错误提示截图（按错误码显示不同文案）

### 日志证据
- 协议解析日志 `PROTOCOL_PARSE`
- 字段校验失败日志 `PARAM_INVALID field=xxx reason=xxx`
- 协议号拦截日志 `UNKNOWN_PROTOCOL id=xxx`
- 错误码返回日志 `RESP_CODE code=xxx`

### 数据证据
- 协议文档 vs 实际实现一致性检查
- 错误码覆盖矩阵（业务失败 ↔ 错误码）
- 协议版本兼容矩阵（v1.0 vs v1.1 vs v2.0）
- 必填/可空字段对照表

### 性能证据
- 单协议解析耗时 < 1ms
- 协议错误码表加载 < 100ms
- 心跳包 P99 延迟 < 50ms
