# C. 缓存层

> **子类代码**：`CACHE_HIT_RATE`
> **归属模块**：`UTIL`
> **来源**：用户细化定义 §3「缓存层（客户端 + 服务端双端缓存）」
>
> **测什么**：客户端本地缓存、服务端 Redis 缓存、缓存一致性、过期清理、击穿雪崩。
> **不测什么**：网络传输（归 B）、业务数据流（归 BIZ）、配置缓存（归 CONFIG）。
> **与其他子类的差异**：C 关注"缓存读写"——B 关注"网络"，D 关注"资源"，E 关注"换算"。

---

## 1. 典型场景

### 场景 1：客户端本地缓存
- 业务背景：玩家设置存档
- 触发动作：保存音量设置
- 验证点：下次启动读取新值

### 场景 2：内存临时缓存
- 业务背景：当前会话数据
- 触发动作：缓存玩家信息
- 验证点：内存中可读取

### 场景 3：图片资源缓存
- 业务背景：图标
- 触发动作：第一次加载图片 → 第二次加载
- 验证点：第二次无网络请求

### 场景 4：缓存过期清理
- 业务背景：缓存 TTL
- 触发动作：缓存 1 小时过期
- 验证点：过期后重新请求

### 场景 5：缓存读写冲突
- 业务背景：并发读写
- 触发动作：两个线程同时写
- 验证点：最后写入胜出

### 场景 6：服务端 Redis 缓存
- 业务背景：排行榜
- 触发动作：从 Redis 读排行榜
- 验证点：返回排行榜数据

### 场景 7：缓存击穿
- 业务背景：热点 key 过期
- 触发动作：1000 个请求同时访问
- 验证点：只有 1 个请求 DB，其他走缓存重建

### 场景 8：缓存雪崩
- 业务背景：大量 key 同时过期
- 触发动作：100 个 key 同时过期
- 验证点：避免 DB 被打挂

### 场景 9：缓存双写一致性
- 业务背景：DB + Redis
- 触发动作：先写 DB → 再写 Redis
- 验证点：Redis 与 DB 一致

### 场景 10：缓存与 DB 一致性
- 业务背景：DB 更新
- 触发动作：DB 更新 → 缓存失效
- 验证点：缓存读最新值

---

## 2. 种子测试点（TP 模板）

### TP-001（CACHE_HIT_RATE）：客户端本地缓存读写
- **scenario**：场景 1
- **module**：`CACHE_HIT_RATE`
- **precondition**：无
- **test_data**：`set("volume", 80)` → 重启 → `get("volume")`
- **expected**：80（持久化）
- **notes**：注意"LocalStorage"vs"IndexedDB"vs"文件"

### TP-002（CACHE_HIT_RATE）：内存临时缓存
- **scenario**：场景 2
- **module**：`CACHE_HIT_RATE`
- **precondition**：无
- **test_data**：`set("user", {id:1})` → `get("user")`
- **expected**：`{id:1}`（内存）
- **notes**：注意"内存"vs"持久"

### TP-003（CACHE_HIT_RATE）：图片资源缓存命中
- **scenario**：场景 3
- **module**：`CACHE_HIT_RATE`
- **precondition**：图片首次加载完成
- **test_data**：第二次进入相同图片页
- **expected**：第二次 Network 面板无图片请求
- **notes**：注意"内存缓存"vs"磁盘缓存"

### TP-004（CACHE_HIT_RATE）：缓存过期清理
- **scenario**：场景 4
- **module**：`CACHE_HIT_RATE`
- **precondition**：缓存 TTL = 1h
- **test_data**：写缓存 → 1h 后读
- **expected**：缓存失效（null）
- **notes**：注意"惰性删除"vs"定时删除"

### TP-005（CACHE_HIT_RATE）：缓存过期后重建
- **scenario**：场景 4
- **module**：`CACHE_HIT_RATE`
- **precondition**：缓存过期
- **test_data**：读缓存 → null → 自动重建
- **expected**：重建后再次读到值
- **notes**：注意"主动重建"vs"惰性重建"

### TP-006（CACHE_HIT_RATE）：并发写冲突
- **scenario**：场景 5
- **module**：`CACHE_HIT_RATE`
- **precondition**：两个线程同时写
- **test_data**：A 写 "value1"、B 写 "value2"
- **expected**：最终值 = 某个值（按设计）
- **notes**：注意"锁"vs"无锁"

### TP-007（CACHE_HIT_RATE）：清除缓存功能
- **scenario**：场景 1
- **module**：`CACHE_HIT_RATE`
- **precondition**：缓存有数据
- **test_data**：玩家点"清除缓存"
- **expected**：缓存清空、设置中可见"已使用 0KB"
- **notes**：注意"全部清除"vs"按类型清除"

### TP-008（CACHE_HIT_RATE）：服务端 Redis 读写
- **scenario**：场景 6
- **module**：`CACHE_HIT_RATE`
- **precondition**：Redis 服务运行
- **test_data**：`redis.set("rank", ...)` → `redis.get("rank")`
- **expected**：值一致
- **notes**：注意"Redis 集群"vs"单机"

### TP-009（CACHE_HIT_RATE）：缓存击穿
- **scenario**：场景 7
- **module**：`CACHE_HIT_RATE`
- **precondition**：热点 key 过期
- **test_data**：1000 个请求同时访问
- **expected**：只有 1 个请求 DB（用分布式锁）
- **notes**：注意"分布式锁"vs"互斥锁"

### TP-010（CACHE_HIT_RATE）：缓存雪崩
- **scenario**：场景 8
- **module**：`CACHE_HIT_RATE`
- **precondition**：100 个 key 同时过期
- **test_data**：100 个 key 同时过期时大量请求
- **expected**：错峰过期（加随机 TTL）
- **notes**：注意"随机 TTL"vs"提前过期"

### TP-011（CACHE_HIT_RATE）：缓存与 DB 双写一致
- **scenario**：场景 9
- **module**：`CACHE_HIT_RATE`
- **precondition**：DB 写入
- **test_data**：先写 DB → 再写 Redis
- **expected**：Redis 与 DB 一致
- **notes**：注意"先 DB 再 Cache"vs"先 Cache 再 DB"

### TP-012（CACHE_HIT_RATE）：缓存与 DB 最终一致
- **scenario**：场景 10
- **module**：`CACHE_HIT_RATE`
- **precondition**：DB 已更新
- **test_data**：DB 更新 → 删缓存 → 读
- **expected**：缓存读最新 DB 值
- **notes**：注意"删缓存"vs"更新缓存"

### TP-013（CACHE_HIT_RATE）：缓存命中率
- **scenario**：场景 3
- **module**：`CACHE_HIT_RATE`
- **precondition**：图片缓存
- **test_data**：100 次访问同一图片
- **expected**：命中率 ≥ 99%
- **notes**：注意"命中率"vs"失效率"

### TP-014（CACHE_HIT_RATE）：缓存容量上限
- **scenario**：场景 1
- **module**：`CACHE_HIT_RATE`
- **precondition**：缓存容量 100MB
- **test_data**：写入 200MB 数据
- **expected**：触发 LRU 淘汰
- **notes**：注意"LRU"vs"FIFO"vs"LFU"

### TP-015（CACHE_HIT_RATE）：玩家视图状态缓存
- **scenario**：场景 1
- **module**：`CACHE_HIT_RATE`
- **precondition**：玩家在商城筛选"价格降序"
- **test_data**：退出 → 重新进入
- **expected**：筛选状态保留
- **notes**：与 UI-B-012 配合

---

## 3. 边界陷阱

### 边界 1：vs B. 网络层
- **混淆点**：「请求"结果"」——B 测网络、C 测缓存
- **判定规则**：测"网络传输/重试" → B；测"请求结果缓存" → C
- **实例**：请求超时重试 → B-012；请求结果缓存 5min → C

### 边界 2：vs J. 存储+日志
- **混淆点**：「本地"存储"」——C 测缓存、J 测持久化
- **判定规则**：测"运行时缓存（可丢）" → C；测"持久化存档" → J
- **实例**：商品列表缓存 → C-001；玩家设置存档 → J-001

### 边界 3：vs D. 资源管理
- **混淆点**：「图片"缓存"」——C 测通用缓存、D 测资源
- **判定规则**：测"通用 key-value 缓存" → C；测"图片资源加载/释放" → D
- **实例**：玩家信息缓存 → C-002；图标资源管理 → D-003

### 边界 4：vs BIZ
- **混淆点**：「业务"缓存"」——C 测缓存技术、BIZ 测业务缓存策略
- **判定规则**：测"Redis 读写" → C；测"业务缓存策略" → BIZ
- **实例**：Redis set/get → C-008；排行榜缓存 5min → BIZ

---

## 4. 验证证据

### 视觉证据
- 缓存命中率截图
- 缓存容量截图

### 日志证据
- 缓存命中日志
- 缓存过期日志
- 缓存淘汰日志
- 击穿/雪崩告警

### 数据证据
- Redis 监控面板
- DB 慢查询日志
- 命中率统计

### 性能证据
- 缓存读写 < 1ms
- 命中率 ≥ 90%
- DB 压力降低
