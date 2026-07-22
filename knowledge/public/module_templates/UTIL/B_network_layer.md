# B. 网络层（底层传输）

> **子类代码**：`NETWORK_LAYER`
> **归属模块**：`AUX`
> **来源**：用户细化定义 §2「网络层（游戏端服通信底层辅助）」
>
> **v1.6.1 变更**：**剔除第三方 SDK 封装**（微信/支付宝/渠道登录）—— 第三方 SDK 归 **LINK 模块**（v1.9 待建）。
> 本子模板**只保留底层网络传输**。
>
> **测什么**：长连接心跳、断线重连、协议打包解包、消息队列、节流防抖、超时重试、网络监控。
> **不测什么**：第三方 SDK（归 LINK）、业务协议字段（归 BIZ）、UI 展示（归 UI）、配置（归 CONFIG）。
> **与其他子类的差异**：B 关注"网络传输"——A 关注"通用工具"，C 关注"缓存"，D 关注"资源"。

---

## 1. 典型场景

### 场景 1：长连接心跳
- 业务背景：游戏保持连接
- 触发动作：客户端每 30s 发心跳包
- 验证点：服务端收到心跳、连接保持

### 场景 2：断线重连
- 业务背景：网络中断
- 触发动作：网络断开 5s → 恢复
- 验证点：自动重连、状态恢复

### 场景 3：自动重登
- 业务背景：服务端踢下线
- 触发动作：token 过期
- 验证点：自动重新登录

### 场景 4：弱网切换
- 业务背景：4G ↔ WiFi
- 触发动作：网络类型变化
- 验证点：连接保持或重连

### 场景 5：协议打包解包
- 业务背景：客户端 ↔ 服务端
- 触发动作：发送协议 → 接收协议
- 验证点：解包正确

### 场景 6：消息队列
- 业务背景：高频请求
- 触发动作：连续发 100 个请求
- 验证点：按顺序处理

### 场景 7：节流防抖
- 业务背景：按钮重复点击
- 触发动作：1s 内点击 10 次
- 验证点：只发 1 个请求

### 场景 8：超时重试
- 业务背景：网络超时
- 触发动作：发请求 30s 无响应
- 验证点：自动重试 3 次

### 场景 9：网络异常容错
- 业务背景：网络断开
- 触发动作：请求失败
- 验证点：不崩溃、错误回调

### 场景 10：网络监控
- 业务背景：性能监控
- 触发动作：网络延迟统计
- 验证点：日志记录

---

## 2. 种子测试点（TP 模板）

### TP-001（NETWORK_LAYER）：长连接心跳
- **scenario**：场景 1
- **module**：`NETWORK_LAYER`
- **precondition**：客户端已连接服务端
- **test_data**：30s 内无业务请求
- **expected**：客户端自动发心跳包、服务端收到
- **notes**：注意心跳频率（30s/60s）

### TP-002（NETWORK_LAYER）：心跳超时断连
- **scenario**：场景 1
- **module**：`NETWORK_LAYER`
- **precondition**：客户端已连接
- **test_data**：客户端网络断开 60s 不发心跳
- **expected**：服务端主动断连、客户端重连
- **notes**：注意"服务端主动断"vs"客户端检测断"

### TP-003（NETWORK_LAYER）：断线自动重连
- **scenario**：场景 2
- **module**：`NETWORK_LAYER`
- **precondition**：玩家在线
- **test_data**：网络断开 5s → 恢复
- **expected**：自动重连成功、玩家无需重新登录
- **notes**：注意"重连"vs"重登"

### TP-004（NETWORK_LAYER）：重连后状态恢复
- **scenario**：场景 2
- **module**：`NETWORK_LAYER`
- **precondition**：玩家有未完成的操作
- **test_data**：断线时玩家在商城页 → 重连
- **expected**：玩家仍在商城页、操作不丢失
- **notes**：注意"操作队列"（归 N）

### TP-005（NETWORK_LAYER）：token 过期自动重登
- **scenario**：场景 3
- **module**：`NETWORK_LAYER`
- **precondition**：玩家在线、token 过期
- **test_data**：服务端返回 401
- **expected**：自动用 refresh_token 重登、玩家无感知
- **notes**：注意"refresh_token"vs"完全重登"

### TP-006（NETWORK_LAYER）：4G ↔ WiFi 切换
- **scenario**：场景 4
- **module**：`NETWORK_LAYER`
- **precondition**：玩家 WiFi 在线
- **test_data**：切换到 4G
- **expected**：连接保持（IP 变化不重连）或重连成功
- **notes**：注意"IP 变化"vs"端口变化"

### TP-007（NETWORK_LAYER）：协议打包正确
- **scenario**：场景 5
- **module**：`NETWORK_LAYER`
- **precondition**：无
- **test_data**：发协议 `{cmd: 1001, data: {x: 1}}` → 字节流
- **expected**：字节流符合协议格式
- **notes**：注意"字节序"vs"对齐"

### TP-008（NETWORK_LAYER）：协议解包正确
- **scenario**：场景 5
- **module**：`NETWORK_LAYER`
- **precondition**：无
- **test_data**：接收字节流 → `{cmd: 2001, data: {y: 2}}`
- **expected**：解包结果 = 期望值
- **notes**：注意"加密"vs"明文"

### TP-009（NETWORK_LAYER）：消息队列顺序
- **scenario**：场景 6
- **module**：`NETWORK_LAYER`
- **precondition**：无
- **test_data**：连续发 100 个请求
- **expected**：服务端按发送顺序处理
- **notes**：注意"有序"vs"并行"

### TP-010（NETWORK_LAYER）：节流防抖
- **scenario**：场景 7
- **module**：`NETWORK_LAYER`
- **precondition**：无
- **test_data**：1s 内点击购买按钮 10 次
- **expected**：只发 1 个购买请求
- **notes**：注意"throttle"vs"debounce"

### TP-011（NETWORK_LAYER）：重复请求过滤
- **scenario**：场景 7
- **module**：`NETWORK_LAYER`
- **precondition**：玩家点击购买
- **test_data**：相同请求 2 次
- **expected**：服务端只处理 1 次（去重）
- **notes**：注意"客户端去重"vs"服务端幂等"

### TP-012（NETWORK_LAYER）：超时重试
- **scenario**：场景 8
- **module**：`NETWORK_LAYER`
- **precondition**：无
- **test_data**：发请求 → 30s 无响应
- **expected**：自动重试 3 次、3 次都失败则错误回调
- **notes**：注意"指数退避"vs"固定间隔"

### TP-013（NETWORK_LAYER）：网络异常不崩溃
- **scenario**：场景 9
- **module**：`NETWORK_LAYER`
- **precondition**：玩家在线
- **test_data**：请求时网络断开
- **expected**：客户端不崩溃、错误回调
- **notes**：注意"全局异常捕获"（归 N）

### TP-014（NETWORK_LAYER）：跨服网关切换
- **scenario**：场景 9
- **module**：`NETWORK_LAYER`
- **precondition**：玩家在服 1
- **test_data**：跨服到服 2
- **expected**：网关切换、连接保持
- **notes**：注意"跨服"vs"同服"

### TP-015（NETWORK_LAYER）：网络延迟统计
- **scenario**：场景 10
- **module**：`NETWORK_LAYER`
- **precondition**：玩家在线
- **test_data**：请求耗时 50ms / 100ms / 500ms
- **expected**：日志记录平均延迟、丢包率
- **notes**：注意"延迟"vs"带宽"

### TP-016（NETWORK_LAYER）：网络状态全局监听
- **scenario**：场景 10
- **module**：`NETWORK_LAYER`
- **precondition**：玩家在线
- **test_data**：网络状态变化
- **expected**：全局事件触发（断网/恢复）
- **notes**：注意"全局事件"vs"单页面事件"

---

## 3. 边界陷阱

### 边界 1：vs BIZ
- **混淆点**：「协议"字段"」——B 测网络、BIZ 测业务
- **判定规则**：测"网络传输/重连/超时" → B；测"业务协议字段校验" → BIZ
- **实例**：断线重连 → B-003；商城协议字段校验 → BIZ

### 边界 2：vs C. 缓存层
- **混淆点**：「网络"请求"」——B 测网络、C 测缓存
- **判定规则**：测"网络层" → B；测"请求结果缓存" → C
- **实例**：请求超时重试 → B-012；请求结果缓存 5min → C

### 边界 3：vs M. 加密安全
- **混淆点**：「协议"加密"」——B 测传输、M 测加密
- **判定规则**：测"协议打包解包" → B；测"加密算法本身" → M
- **实例**：协议字节流打包 → B-007；AES-256 加密 → M

### 边界 4：vs N. 异常兜底
- **混淆点**：「网络"异常"」——B 测网络层异常、N 测全局异常
- **判定规则**：测"网络断开/超时" → B；测"全局崩溃捕获" → N
- **实例**：网络超时错误回调 → B-013；全局崩溃 → N-001

---

## 4. 验证证据

### 视觉证据
- 网络断开/恢复 Toast 提示截图
- 网络延迟显示截图

### 日志证据
- 心跳日志
- 重连日志
- 网络异常日志
- 延迟统计日志

### 数据证据
- Network 面板（请求/响应）
- 重连成功率统计
- 平均延迟统计

### 性能证据
- 心跳包大小 < 100B
- 重连耗时 < 3s
- 心跳 CPU 占用 < 1%
