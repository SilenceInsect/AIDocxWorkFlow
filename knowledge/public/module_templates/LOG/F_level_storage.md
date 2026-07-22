# F. 日志分级存储 & 生命周期管理

> **子类代码**：`LOG_LEVEL_STORAGE`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §6「日志分级存储 & 生命周期管理（新增细分规则）」
>
> **测什么**：日志分级标准（FATAL/ERROR/WARN/INFO/DEBUG）、存储分层（客户端本地/服务端磁盘/时序库/冷热分离）、生命周期（调试日志清理/审计长期归档/过期清理/分片切割）、容灾（写入重试/磁盘满降级）。
> **不测什么**：业务日志内容（归 A/B/C）、日志底层采集 SDK（归 AUX）、本地存档（归 AUX J）、数据库存储（归 BIZ E）。
> **与其他子类的差异**：F 关注"日志**存储/生命周期/容灾**规范"——A 关注"行为埋点"，B 关注"资产对账"，C 关注"操作日志"。与 AUX 严格隔离：AUX 测"底层存储技术能力"，F 测"日志业务分层/分级/生命周期规范"。

---

## 1. 典型场景

### 场景 1：FATAL 崩溃日志
- 业务背景：崩溃
- 涉及数据：FATAL
- 触发动作：崩溃
- 验证点：FATAL 级别标记、长期保留

### 场景 2：ERROR 业务异常
- 业务背景：业务报错
- 涉及数据：ERROR
- 触发动作：异常
- 验证点：ERROR 级别标记

### 场景 3：WARN 风险操作
- 业务背景：异常操作
- 涉及数据：WARN
- 触发动作：触发
- 验证点：WARN 级别标记

### 场景 4：INFO 正常业务
- 业务背景：登录/购买
- 涉及数据：INFO
- 触发动作：常规
- 验证点：INFO 级别标记

### 场景 5：DEBUG 调试日志
- 业务背景：开发期
- 涉及数据：DEBUG
- 触发动作：调试
- 验证点：DEBUG 级别仅开发可见

### 场景 6：客户端本地临时日志
- 业务背景：崩溃前临时
- 涉及数据：本地日志
- 触发动作：临时写入
- 验证点：本地缓存

### 场景 7：服务端磁盘持久
- 业务背景：服务端日志
- 涉及数据：磁盘
- 触发动作：写入
- 验证点：磁盘持久

### 场景 8：时序库归档
- 业务背景：监控指标
- 涉及数据：时序
- 触发动作：写入时序库
- 验证点：时序库

### 场景 9：冷热数据分离
- 业务背景：1 年前日志
- 涉及数据：冷数据
- 触发动作：归档
- 验证点：冷数据归档

### 场景 10：调试日志自动清理
- 业务背景：DEBUG 满
- 涉及数据：DEBUG
- 触发动作：自动清理
- 验证点：DEBUG 自动清

### 场景 11：审计/付费日志长期归档
- 业务背景：审计日志
- 涉及数据：审计
- 触发动作：长期保留
- 验证点：审计日志 5 年

### 场景 12：过期临时清理
- 业务背景：临时日志
- 涉及数据：临时
- 触发动作：定时清理
- 验证点：过期清

### 场景 13：日志分片切割
- 业务背景：日志 1GB
- 涉及数据：分片
- 触发动作：自动切割
- 验证点：分片 200MB

### 场景 14：写入失败重试
- 业务背景：DB 抖动
- 涉及数据：写入
- 触发动作：失败
- 验证点：重试 3 次

### 场景 15：磁盘满降级
- 业务背景：磁盘满
- 涉及数据：磁盘
- 触发动作：满
- 验证点：降级缓存

### 场景 16：不阻塞主业务
- 业务背景：日志慢
- 涉及数据：业务
- 触发动作：写入慢
- 验证点：业务正常

### 场景 17：日志查询性能
- 业务背景：1 亿条
- 涉及数据：查询
- 触发动作：查询
- 验证点：< 1s

### 场景 18：日志压缩
- 业务背景：磁盘满
- 涉及数据：压缩
- 触发动作：自动压缩
- 验证点：压缩 10x

### 场景 19：日志轮转
- 业务背景：日志 1 天
- 涉及数据：轮转
- 触发动作：0 点轮转
- 验证点：日志按天分文件

### 场景 20：日志查询权限
- 业务背景：敏感日志
- 涉及数据：权限
- 触发动作：查询
- 验证点：审计日志仅管理员

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_LEVEL_STORAGE）：FATAL 级别
- **scenario**：场景 1
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：崩溃
- **test_data`：崩溃日志
- **expected**：日志 `level=FATAL`、长期保留
- **notes**：注意"FATAL"vs"ERROR"+"保留期"

### TP-002（LOG_LEVEL_STORAGE）：ERROR 级别
- **scenario**：场景 2
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：业务异常
- **test_data`：业务错误
- **expected**：日志 `level=ERROR`、保留 30 天
- **notes**：注意"业务"vs"崩溃"

### TP-003（LOG_LEVEL_STORAGE）：WARN 级别
- **scenario**：场景 3
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：风险操作
- **test_data`：异常操作
- **expected**：日志 `level=WARN`、保留 7 天
- **notes**：注意"WARN"vs"ERROR"

### TP-004（LOG_LEVEL_STORAGE）：INFO 级别
- **scenario**：场景 4
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：登录/购买
- **test_data`：常规操作
- **expected**：日志 `level=INFO`、保留 3 天
- **notes**：注意"业务"vs"运维"

### TP-005（LOG_LEVEL_STORAGE）：DEBUG 仅开发
- **scenario**：场景 5
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：开发期
- **test_data`：release 包
- **expected**：release 不含 DEBUG
- **notes**：注意"开发"vs"正式"

### TP-006（LOG_LEVEL_STORAGE）：客户端本地缓存
- **scenario**：场景 6
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：崩溃前
- **test_data`：本地日志
- **expected**：崩溃日志本地缓存 < 1MB
- **notes**：注意"本地"vs"上报"

### TP-007（LOG_LEVEL_STORAGE）：服务端磁盘持久
- **scenario**：场景 7
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：服务端写日志
- **test_data`：观察磁盘
- **expected**：日志持久化到磁盘
- **notes**：注意"磁盘"vs"内存"

### TP-008（LOG_LEVEL_STORAGE）：时序库归档
- **scenario**：场景 8
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：监控指标
- **test_data`：观察
- **expected**：监控指标写入时序库
- **notes**：注意"时序"vs"普通"

### TP-009（LOG_LEVEL_STORAGE）：冷热数据分离
- **scenario**：场景 9
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：1 年前日志
- **test_data`：归档
- **expected**：冷数据归档到 OSS
- **notes**：注意"冷"vs"热"+"归档"

### TP-010（LOG_LEVEL_STORAGE）：DEBUG 自动清理
- **scenario**：场景 10
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：DEBUG 满
- **test_data`：自动清理
- **expected**：DEBUG 自动清理
- **notes**：注意"自动"vs"手动"

### TP-011（LOG_LEVEL_STORAGE）：审计日志长期
- **scenario**：场景 11
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：审计日志
- **test_data`：1 年前审计
- **expected**：审计日志 5 年可查
- **notes**：注意"合规"+"长期"

### TP-012（LOG_LEVEL_STORAGE）：过期临时清理
- **scenario**：场景 12
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：临时日志 7 天
- **test_data`：第 8 天
- **expected**：临时日志清理
- **notes**：注意"临时"vs"永久"

### TP-013（LOG_LEVEL_STORAGE）：日志分片
- **scenario**：场景 13
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：日志 1GB
- **test_data**：自动切割
- **expected**：分片 200MB/文件
- **notes**：注意"分片"vs"单文件"

### TP-014（LOG_LEVEL_STORAGE）：写入重试
- **scenario**：场景 14
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：DB 抖动
- **test_data`：写入失败
- **expected**：重试 3 次、最终成功
- **notes**：注意"重试"vs"丢"

### TP-015（LOG_LEVEL_STORAGE）：磁盘满降级
- **scenario**：场景 15
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：磁盘 100%
- **test_data`：写入
- **expected**：降级写本地缓存
- **notes**：注意"降级"vs"丢"

### TP-016（LOG_LEVEL_STORAGE）：不阻塞业务
- **scenario**：场景 16
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：日志慢
- **test_data`：业务请求
- **expected**：业务延迟 < 50ms
- **notes**：注意"异步"+"队列"

### TP-017（LOG_LEVEL_STORAGE）：日志查询性能
- **scenario**：场景 17
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：1 亿条日志
- **test_data`：按 player_id 查询
- **expected**：< 1s 返回
- **notes**：注意"索引"+"分页"

### TP-018（LOG_LEVEL_STORAGE）：日志压缩
- **scenario**：场景 18
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：磁盘满
- **test_data`：自动压缩
- **expected**：压缩 10x
- **notes**：注意"压缩"vs"清理"

### TP-019（LOG_LEVEL_STORAGE）：日志轮转
- **scenario**：场景 19
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：1 天日志
- **test_data`：0 点
- **expected**：日志按天分文件
- **notes**：注意"按天"vs"按大小"

### TP-020（LOG_LEVEL_STORAGE）：审计权限
- **scenario**：场景 20
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：敏感日志
- **test_data`：玩家查询
- **expected`：审计日志仅管理员
- **notes**：注意"权限"+"审计"

### TP-021（LOG_LEVEL_STORAGE）：级别动态调整
- **scenario**：场景 4
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：线上故障
- **test_data`：临时调 DEBUG
- **expected**：动态生效
- **notes**：注意"动态"vs"重启"

### TP-022（LOG_LEVEL_STORAGE）：级别对账
- **scenario**：场景 1
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：1 天日志
- **test_data`：统计各级别
- **expected`：FATAL 0、ERROR 100、WARN 1k、INFO 1M
- **notes**：注意"级别"分布

### TP-023（LOG_LEVEL_STORAGE）：告警日志保留
- **scenario**：场景 11
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：告警日志
- **test_data`：1 年后
- **expected**：告警日志可查
- **notes**：注意"告警"vs"业务"

### TP-024（LOG_LEVEL_STORAGE）：冷数据可恢复
- **scenario**：场景 9
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：冷数据 OSS
- **test_data`：查询
- **expected**：可恢复查询
- **notes**：注意"冷"vs"不可查"

### TP-025（LOG_LEVEL_STORAGE）：跨级别聚合
- **scenario**：场景 22
- **module**：`LOG_LEVEL_STORAGE`
- **precondition**：多级别
- **test_data`：聚合
- **expected`：跨级别聚合
- **notes**：注意"聚合"+"维度"

---

## 3. 边界陷阱

### 边界 1：vs AUX（本地存储）
- **混淆点**：「本地"存储"」——F 测日志业务分层、AUX J 测底层
- **判定规则**：测"日志业务分级/生命周期" → F；测"通用 localStorage 工具" → AUX J
- **实例**：DEBUG 自动清理 → F；玩家设置存档 → AUX J

### 边界 2：vs BIZ E. 数据库
- **混淆点**：「日志"存储"」——F 测日志、BIZ E 测业务 DB
- **判定规则**：测"日志存储分层" → F；测"业务数据落库" → BIZ E
- **实例**：日志磁盘持久 → F；玩家背包 DB → BIZ E

### 边界 3：vs A. 行为埋点
- **混淆点**：「埋点"存储"」——A 测触发、F 测存储
- **判定规则**：测"埋点业务规则" → A；测"埋点存储" → F
- **实例**：购买埋点 → A；埋点时序库 → F

### 边界 4：vs C. 操作日志
- **混淆点**：「操作"存储"」——C 测内容、F 测存储
- **判定规则**：测"操作日志内容" → C；测"操作日志存储" → F
- **实例**：GM 操作日志 → C；GM 日志归档 → F

### 边界 5：vs B. 资产流水
- **混淆点**：「流水"存储"」——B 测对账、F 测存储
- **判定规则**：测"资产对账" → B；测"流水存储" → F
- **实例**：资产对账 → B；流水归档 → F

---

## 4. 验证证据

### 视觉证据
- 日志查询后台截图（按级别过滤）
- 冷热数据存储分布截图

### 日志证据
- `level=FATAL/ERROR/WARN/INFO/DEBUG` 级别标记
- `STORAGE_LEVEL=local/disk/tsdb/cold` 存储层级
- `LIFECYCLE=temp/audit/permanent` 生命周期
- `CLEANUP type=auto/manual`
- `RETRY count=N`

### 数据证据
- 日志级别表 `log.level, count, retention`
- 存储分层表 `storage.type, capacity, used`
- 生命周期表 `lifecycle.type, retention_days, archive_path`
- 冷热分离比例
- 写入重试成功率

### 性能证据
- 日志写入 < 5ms
- 业务延迟不增 < 10ms
- 日志查询 < 1s
- DEBUG 自动清理 < 1s
- 磁盘满降级生效 < 1s
- 压缩比 ≥ 10x
