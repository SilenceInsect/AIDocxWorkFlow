# M. 日志上报容错逻辑

> **子类代码**：`LOG_REPORT_FAULT_TOLERANT`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §13「日志上报容错逻辑（原定义完全缺失，新增）」
>
> **测什么**：断网缓存日志、批量合并上报、上报失败重试、超大日志分片上传、不阻塞游戏主线程。
> **不测什么**：日志底层采集（归 UTIL）、日志存储（归 F）、业务逻辑（归 BIZ）、网络层（归 UTIL B）。
> **与其他子类的差异**：M 关注"**日志上报容错**机制"——F 关注"存储规范"，G 关注"完整性"，K 关注"第三方日志"。

---

## 1. 典型场景

### 场景 1：断网缓存
- 业务背景：断网
- 涉及数据：缓存
- 触发动作：断网
- 验证点：本地缓存

### 场景 2：缓存上限
- 业务背景：本地满
- 涉及数据：缓存
- 触发动作：满
- 验证点：覆盖最旧

### 场景 3：批量合并
- 业务背景：1s 100 埋点
- 涉及数据：批量
- 触发动作：合并
- 验证点：1 次上报

### 场景 4：合并窗口
- 业务背景：1s 窗口
- 涉及数据：窗口
- 触发动作：定时
- 验证点：1s 合并

### 场景 5：合并大小
- 业务背景：满 100 条
- 涉及数据：大小
- 触发动作：触发
- 验证点：满上报

### 场景 6：上报失败重试
- 业务背景：网络失败
- 涉及数据：重试
- 触发动作：失败
- 验证点：重试 3 次

### 场景 7：重试退避
- 业务背景：失败
- 涉及数据：退避
- 触发动作：退避
- 验证点：指数退避

### 场景 8：超大日志分片
- 业务背景：1MB 日志
- 涉及数据：分片
- 触发动作：分片
- 验证点：分片上传

### 场景 9：分片顺序
- 业务背景：分片
- 涉及数据：顺序
- 触发动作：分片
- 验证点：按序

### 场景 10：分片合并
- 业务背景：服务端
- 涉及数据：合并
- 触发动作：合并
- 验证点：合并为完整

### 场景 11：分片超时
- 业务背景：分片超时
- 涉及数据：超时
- 触发动作：超时
- 验证点：重传

### 场景 12：不阻塞主线程
- 业务背景：日志
- 涉及数据：线程
- 触发动作：写入
- 验证点：业务延迟不变

### 场景 13：异步队列
- 业务背景：高频日志
- 涉及数据：队列
- 触发动作：队列
- 验证点：异步消费

### 场景 14：队列堆积
- 业务背景：网络差
- 涉及数据：堆积
- 触发动作：堆积
- 验证点：堆积处理

### 场景 15：上报优先级
- 业务背景：FATAL vs DEBUG
- 涉及数据：优先级
- 触发动作：上报
- 验证点：FATAL 优先

### 场景 16：上报压缩
- 业务背景：网络差
- 涉及数据：压缩
- 触发动作：压缩
- 验证点：压缩

### 场景 17：上报加密
- 业务背景：敏感
- 涉及数据：加密
- 触发动作：加密
- 验证点：加密

### 场景 18：上报采样
- 业务背景：高频
- 涉及数据：采样
- 触发动作：采样
- 验证点：采样率

### 场景 19：上报降级
- 业务背景：网络极差
- 涉及数据：降级
- 触发动作：降级
- 验证点：仅本地

### 场景 20：上报恢复
- 业务背景：网络恢复
- 涉及数据：恢复
- 触发动作：恢复
- 验证点：恢复

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_REPORT_FAULT_TOLERANT）：断网缓存
- **scenario**：场景 1
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition**：断网
- **test_data`：观察
- **expected**：本地缓存 < 1MB
- **notes**：注意"本地"vs"丢"

### TP-002（LOG_REPORT_FAULT_TOLERANT）：缓存上限
- **scenario**：场景 2
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：本地满
- **test_data`：观察
- **expected**：覆盖最旧、不报错
- **notes**：注意"覆盖"vs"丢"

### TP-003（LOG_REPORT_FAULT_TOLERANT）：批量合并
- **scenario**：场景 3
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition**：1s 100 埋点
- **test_data`：观察
- **expected`：1 次批量上报
- **notes**：注意"合并"vs"逐条"

### TP-004（LOG_REPORT_FAULT_TOLERANT）：合并窗口
- **scenario**：场景 4
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition**：1s 窗口
- **test_data`：定时
- **expected`：1s 触发合并
- **notes**：注意"窗口"+"定时"

### TP-005（LOG_REPORT_FAULT_TOLERANT）：合并大小
- **scenario**：场景 5
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition**：满 100 条
- **test_data`：触发
- **expected**：满即上报
- **notes**：注意"大小"+"触发"

### TP-006（LOG_REPORT_FAULT_TOLERANT）：上报重试
- **scenario**：场景 6
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：网络失败
- **test_data`：重试
- **expected`：重试 3 次
- **notes**：注意"重试"vs"丢"

### TP-007（LOG_REPORT_FAULT_TOLERANT）：指数退避
- **scenario**：场景 7
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：失败
- **test_data`：退避
- **expected**：1s/3s/9s
- **notes**：注意"指数"vs"固定"

### TP-008（LOG_REPORT_FAULT_TOLERANT）：分片上传
- **scenario**：场景 8
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：1MB 日志
- **test_data`：分片
- **expected**：分片 100KB 上传
- **notes**：注意"分片"vs"单"

### TP-009（LOG_REPORT_FAULT_TOLERANT）：分片顺序
- **scenario**：场景 9
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：分片
- **test_data`：观察
- **expected**：按序
- **notes**：注意"顺序"vs"乱序"

### TP-010（LOG_REPORT_FAULT_TOLERANT）：分片合并
- **scenario**：场景 10
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：服务端
- **test_data`：合并
- **expected**：完整
- **notes**：注意"合并"vs"丢"

### TP-011（LOG_REPORT_FAULT_TOLERANT）：分片重传
- **scenario**：场景 11
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition**：分片超时
- **test_data`：超时
- **expected**：重传
- **notes**：注意"重传"vs"丢"

### TP-012（LOG_REPORT_FAULT_TOLERANT）：不阻塞主线程
- **scenario**：场景 12
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：日志慢
- **test_data`：业务
- **expected**：业务延迟 < 10ms
- **notes**：注意"异步"+"主线程"

### TP-013（LOG_REPORT_FAULT_TOLERANT）：异步队列
- **scenario**：场景 13
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：高频
- **test_data`：观察
- **expected`：异步消费
- **notes**：注意"队列"+"异步"

### TP-014（LOG_REPORT_FAULT_TOLERANT）：队列堆积
- **scenario**：场景 14
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：网络差
- **test_data`：观察
- **expected`：堆积 < 阈值
- **notes**：注意"堆积"+"告警"

### TP-015（LOG_REPORT_FAULT_TOLERANT）：FATAL 优先
- **scenario**：场景 15
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：FATAL + DEBUG
- **test_data`：网络恢复
- **expected**：FATAL 先上报
- **notes**：注意"优先级"vs"顺序"

### TP-016（LOG_REPORT_FAULT_TOLERANT）：上报压缩
- **scenario**：场景 16
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：网络差
- **test_data`：压缩
- **expected`：压缩 5x
- **notes**：注意"压缩"+"带宽"

### TP-017（LOG_REPORT_FAULT_TOLERANT）：上报加密
- **scenario**：场景 17
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：敏感
- **test_data`：加密
- **expected**：TLS 加密
- **notes**：注意"加密"+"传输"

### TP-018（LOG_REPORT_FAULT_TOLERANT）：上报采样
- **scenario**：场景 18
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition**：高频
- **test_data`：采样
- **expected`：10% 采样
- **notes**：注意"采样"+"FATAL 全量"

### TP-019（LOG_REPORT_FAULT_TOLERANT）：上报降级
- **scenario**：场景 19
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：网络极差
- **test_data`：降级
- **expected`：仅本地
- **notes**：注意"降级"vs"丢"

### TP-020（LOG_REPORT_FAULT_TOLERANT）：上报恢复
- **scenario**：场景 20
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition**：网络恢复
- **test_data`：恢复
- **expected`：补传本地缓存
- **notes**：注意"恢复"+"补传"

### TP-021（LOG_REPORT_FAULT_TOLERANT）：跨进程队列
- **scenario**：场景 13
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：多进程
- **test_data`：观察
- **expected`：每进程独立队列
- **notes**：注意"进程"vs"线程"

### TP-022（LOG_REPORT_FAULT_TOLERANT）：线程切换
- **scenario**：场景 12
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：写入
- **test_data`：观察
- **expected**：异步线程
- **notes**：注意"线程"+"切换"

### TP-023（LOG_REPORT_FAULT_TOLERANT）：上报签名
- **scenario**：场景 17
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：防伪造
- **test_data`：签名
- **expected`：签名通过
- **notes**：注意"签名"vs"加密"

### TP-024（LOG_REPORT_FAULT_TOLERANT）：QoS 策略
- **scenario**：场景 15
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition**：不同级别
- **test_data`：观察
- **expected**：FATAL > ERROR > INFO
- **notes**：注意"QoS"vs"先入先出"

### TP-025（LOG_REPORT_FAULT_TOLERANT）：上报统计
- **scenario**：场景 18
- **module**：`LOG_REPORT_FAULT_TOLERANT`
- **precondition`：1 天上报
- **test_data`：统计
- **expected`：含成功率、失败率、重试率
- **notes**：注意"统计"+"指标"

---

## 3. 边界陷阱

### 边界 1：vs F. 存储
- **混淆点**：「日志"缓存"」——F 测存储、M 测上报
- **判定规则**：测"日志存储" → F；测"日志上报" → M
- **实例**：磁盘分片 → F；上报分片 → M

### 边界 2：vs UTIL B. 网络层
- **混淆点**：「网络"重传"」——UTIL B 测网络、M 测日志
- **判定规则**：测"网络层重传" → UTIL B；测"日志上报重试" → M
- **实例**：断线重连 → UTIL B；日志重试 → M

### 边界 3：vs G. 完整性
- **混淆点**：「日志"补传"」——G 测一致、M 测上报
- **判定规则**：测"日志一致" → G；测"上报机制" → M
- **实例**：日志补传 → G；上报分片 → M

### 边界 4：vs K. 第三方
- **混淆点**：「外部"上报"」——K 测第三方、M 测通用
- **判定规则**：测"第三方日志" → K；测"通用上报" → M
- **实例**：支付回调日志 → K；客户端上报 → M

### 边界 5：vs A. 行为埋点
- **混淆点**：「埋点"触发"」——A 测业务、M 测上报
- **判定规则**：测"埋点业务" → A；测"埋点上报" → M
- **实例**：购买埋点 → A；埋点批量合并 → M

---

## 4. 验证证据

### 视觉证据
- 上报统计后台截图
- 队列堆积告警截图

### 日志证据
- `REPORT status=success/fail count=N`
- `RETRY count=N`
- `BACKOFF duration=1s/3s/9s`
- `SLICE id=N total=M`
- `FALLBACK status=local_only`
- `RECOVER status=ok`

### 数据证据
- 上报成功率 ≥ 99%
- 上报延迟 < 1s
- 队列堆积 < 阈值
- 分片重传率
- 上报采样率
- 上报压缩比

### 性能证据
- 主线程延迟 < 10ms
- 上报延迟 P99 < 1s
- 批量合并节省 50% 带宽
- 断网缓存 < 1MB
- 恢复补传 < 1min
- 退避策略 1s/3s/9s
