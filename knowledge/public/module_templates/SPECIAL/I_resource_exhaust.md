# I. 资源耗尽极端场景

> **子类代码**：`RESOURCE_EXHAUST`
> **归属模块**：`SPECIAL`
> **来源**：用户细化定义 §9「资源耗尽极端场景」（原定义缺失补充）
>
> **测什么**：**背包满**、**仓库上限**、**邮件容量上限**、**服务器内存/CPU 打满**、**数据库连接耗尽**等极端场景下的**业务降级策略**、**排队限流**、**拒绝新操作**——业务侧如何优雅降级、提示用户、避免崩溃。
> **不测什么**：底层资源管理（归 AUX D）、性能监控（归 AUX K）、业务正常流程（归 BIZ）。
> **与其他子类的差异**：I 关注"系统资源耗尽"——A 关注"业务边界"、B 关注"对抗"、E 关注"HA"；I 是系统级资源耗尽，E 是服务级 HA，A 是业务级边界。

---

## 1. 典型场景

### 场景 1：玩家背包满
- 业务背景：玩家背包 100 格已满
- 涉及字段/工具：bag_capacity、bag_full_check
- 触发动作：玩家拾取新道具
- 验证点：拾取失败 + 提示"背包已满"

### 场景 2：仓库上限
- 业务背景：玩家仓库已达最大容量
- 涉及字段/工具：warehouse_capacity
- 触发动作：玩家存新道具到仓库
- 验证点：存入失败 + 提示"仓库已满"

### 场景 3：邮件容量上限
- 业务背景：玩家邮件 1000 封已满
- 涉及字段/工具：mail_capacity
- 触发动作：系统发送新邮件
- 验证点：邮件发送失败 + 提示"邮件已满，请清理"

### 场景 4：服务器内存打满
- 业务背景：服务器内存使用率 95%
- 涉及字段/工具：server_memory、mem_alert
- 触发动作：玩家发请求
- 验证点：业务降级 + 限流 + 排队

### 场景 5：服务器 CPU 打满
- 业务背景：服务器 CPU 使用率 95%
- 涉及字段/工具：server_cpu、cpu_alert
- 触发动作：玩家发请求
- 验证点：业务降级 + 限流 + 提示

### 场景 6：数据库连接耗尽
- 业务背景：DB 连接池满
- 涉及字段/工具：db_pool、pool_exhaust
- 触发动作：玩家读写
- 验证点：等待 + 超时 + 提示

### 场景 7：业务降级策略
- 业务背景：系统资源紧张
- 涉及字段/工具：degrade_strategy、priority
- 触发动作：玩家发请求
- 验证点：低优先级功能降级（隐藏/禁用），高优先级保留

### 场景 8：排队限流
- 业务背景：服务器资源紧张
- 涉及字段/工具：queue、position
- 触发动作：玩家发请求
- 验证点：玩家进入排队队列 + 显示位置 + 倒计时

### 场景 9：拒绝新操作
- 业务背景：系统资源打满 + 业务不可用
- 涉及字段/工具：service_unavailable、reject_strategy
- 触发动作：玩家发请求
- 验证点：拒绝 + 友好提示 + 重试入口

### 场景 10：资源耗尽时玩家数据保护
- 业务背景：资源耗尽但业务在写
- 涉及字段/工具：data_protect、write_reject
- 触发动作：玩家写操作
- 验证点：拒绝写 + 玩家数据无半写

### 场景 11：邮件附件提取失败
- 业务背景：玩家提取邮件附件时背包满
- 涉及字段/工具：mail_attach、bag_full
- 触发动作：玩家提取邮件附件
- 验证点：拒绝 + 提示"背包已满，请先清理"

### 场景 12：拍卖行商品数量限制
- 业务背景：拍卖行已达商品数量上限
- 涉及字段/工具：auction_capacity
- 触发动作：玩家上架商品
- 验证点：上架失败 + 提示"拍卖行已满"

### 场景 13：好友上限
- 业务背景：玩家好友数量已达上限
- 涉及字段/工具：friend_capacity
- 触发动作：玩家添加好友
- 验证点：添加失败 + 提示"好友数量已达上限"

### 场景 14：工会成员上限
- 业务背景：工会成员已满
- 涉及字段/工具：guild_capacity
- 触发动作：玩家申请加入工会
- 验证点：申请失败 + 提示"工会已满"

### 场景 15：玩家邮件清理提示
- 业务背景：邮件接近容量上限
- 涉及字段/工具：mail_capacity_alert
- 触发动作：玩家收到新邮件
- 验证点：提示"邮件将满，请清理"

---

## 2. 种子测试点（TP 模板）

### TP-001（RESOURCE_EXHAUST）：背包满拾取拦截
- **scenario**：场景 1
- **module**：`RESOURCE_EXHAUST`
- **precondition**：玩家背包 100/100
- **test_data**：拾取新道具
- **expected**：拾取失败 + 提示"背包已满，请先清理"
- **notes**：注意"拾取" vs "购买"——购买也可能背包满

### TP-002（RESOURCE_EXHAUST）：仓库满存入拦截
- **scenario**：场景 2
- **module**：`RESOURCE_EXHAUST`
- **precondition**：玩家仓库 200/200
- **test_data**：存新道具到仓库
- **expected**：存入失败 + 提示"仓库已满"
- **notes**：注意"仓库" vs "背包"——两者独立

### TP-003（RESOURCE_EXHAUST）：邮件满发送拦截
- **scenario**：场景 3
- **module**：`RESOURCE_EXHAUST`
- **precondition**：玩家邮件 1000/1000
- **test_data**：系统发新邮件
- **expected**：发送失败 + 提示"邮件已满，请清理"
- **notes**：注意"系统邮件" vs "玩家邮件"——系统邮件也会失败

### TP-004（RESOURCE_EXHAUST）：内存打满限流
- **scenario**：场景 4
- **module**：`RESOURCE_EXHAUST`
- **precondition**：服务器内存 > 95%
- **test_data**：玩家发请求
- **expected**：业务降级（低优先级功能禁用）+ 限流 + 排队
- **notes**：注意"内存" vs "CPU"——两者都需监控

### TP-005（RESOURCE_EXHAUST）：CPU 打满降级
- **scenario**：场景 5
- **module**：`RESOURCE_EXHAUST`
- **precondition**：服务器 CPU > 95%
- **test_data**：玩家发请求
- **expected**：业务降级 + 限流 + 提示"系统繁忙"
- **notes**：注意"CPU" vs "内存"——不同资源不同策略

### TP-006（RESOURCE_EXHAUST）：DB 连接池耗尽
- **scenario**：场景 6
- **module**：`RESOURCE_EXHAUST`
- **precondition**：DB 连接池 100/100
- **test_data**：玩家读写
- **expected**：等待 1s + 超时 + 提示"服务繁忙，请重试"
- **notes**：注意"连接池" vs "DB 抖动"——前者是连接数

### TP-007（RESOURCE_EXHAUST）：业务降级优先级
- **scenario**：场景 7
- **module**：`RESOURCE_EXHAUST`
- **precondition**：系统资源紧张
- **test_data**：玩家发请求
- **expected**：高优先级保留（登录/充值），低优先级降级（聊天/排行榜）
- **notes**：注意"优先级" vs "全部"——优先级是分级保护

### TP-008（RESOURCE_EXHAUST）：排队队列
- **scenario**：场景 8
- **module**：`RESOURCE_EXHAUST`
- **precondition**：服务器资源紧张
- **test_data**：玩家发请求
- **expected**：进入排队队列 + 显示位置（"您前面还有 100 位"）+ 倒计时
- **notes**：注意"排队" vs "限流"——排队是有序等待

### TP-009（RESOURCE_EXHAUST）：拒绝新操作
- **scenario**：场景 9
- **module**：`RESOURCE_EXHAUST`
- **precondition**：系统资源打满 + 业务不可用
- **test_data**：玩家发请求
- **expected**：返回 ERR_SERVICE_UNAVAILABLE + 友好提示"系统繁忙，请稍后再试"
- **notes**：注意"拒绝" vs "排队"——拒绝是立即返回

### TP-010（RESOURCE_EXHAUST）：写操作拒绝防半写
- **scenario**：场景 10
- **module**：`RESOURCE_EXHAUST`
- **precondition**：资源耗尽但业务在写
- **test_data**：玩家写操作
- **expected**：拒绝 + 玩家数据无半写
- **notes**：注意"写" vs "读"——读可以降级，写必须拒绝

### TP-011（RESOURCE_EXHAUST）：邮件附件提取
- **scenario**：场景 11
- **module**：`RESOURCE_EXHAUST`
- **precondition**：玩家背包满 + 有未提取邮件
- **test_data**：提取邮件附件
- **expected**：拒绝 + 提示"背包已满，请先清理"
- **notes**：注意"邮件" vs "背包"——跨模块资源检查

### TP-012（RESOURCE_EXHAUST）：拍卖行满
- **scenario**：场景 12
- **module**：`RESOURCE_EXHAUST`
- **precondition**：拍卖行商品数量 10000/10000
- **test_data**：玩家上架商品
- **expected**：上架失败 + 提示"拍卖行已满"
- **notes**：注意"拍卖行" vs "玩家拍卖"——前者是服级

### TP-013（RESOURCE_EXHAUST）：好友满
- **scenario**：场景 13
- **module**：`RESOURCE_EXHAUST`
- **precondition**：玩家好友 500/500
- **test_data**：添加好友
- **expected**：添加失败 + 提示"好友数量已达上限"
- **notes**：注意"好友" vs "黑名单"——两者独立

### TP-014（RESOURCE_EXHAUST）：工会满
- **scenario**：场景 14
- **module**：`RESOURCE_EXHAUST`
- **precondition**：工会成员 100/100
- **test_data**：玩家申请加入
- **expected**：申请失败 + 提示"工会已满"
- **notes**：注意"工会" vs "群组"——后者容量可能不同

### TP-015（RESOURCE_EXHAUST）：邮件将满提示
- **scenario**：场景 15
- **module**：`RESOURCE_EXHAUST`
- **precondition**：邮件 950/1000
- **test_data**：玩家收到新邮件
- **expected**：弹窗"邮件将满，请清理" + 提供清理入口
- **notes**：注意"将满" vs "已满"——预防优于补救

### TP-016（RESOURCE_EXHAUST）：资源耗尽自动恢复
- **scenario**：场景 4 扩展
- **module**：`RESOURCE_EXHAUST`
- **precondition**：资源耗尽 + 业务降级
- **test_data**：资源恢复后
- **expected**：自动恢复业务 + 玩家无感知
- **notes**：注意"自动" vs "手动"——自动更友好

### TP-017（RESOURCE_EXHAUST）：资源耗尽告警
- **scenario**：场景 4 扩展
- **module**：`RESOURCE_EXHAUST`
- **precondition**：资源使用 > 80%
- **test_data**：触发告警
- **expected**：运维告警（钉钉/邮件）+ 自动扩容
- **notes**：注意"告警" vs "静默"——告警更安全

### TP-018（RESOURCE_EXHAUST）：核心功能降级保留
- **scenario**：场景 7 扩展
- **module**：`RESOURCE_EXHAUST`
- **precondition**：资源紧张
- **test_data**：玩家发请求
- **expected**：核心功能（登录/充值/购买）保留，非核心功能（聊天/排行/推荐）降级
- **notes**：注意"核心" vs "非核心"——核心是 P0

### TP-019（RESOURCE_EXHAUST）：背包扩容
- **scenario**：场景 1 扩展
- **module**：`RESOURCE_EXHAUST`
- **precondition**：玩家背包满
- **test_data**：玩家使用扩容道具
- **expected**：背包扩容 + 可继续拾取
- **notes**：注意"扩容" vs "清理"——扩容是道具付费

### TP-020（RESOURCE_EXHAUST）：资源监控埋点
- **scenario**：场景 4 扩展
- **module**：`RESOURCE_EXHAUST`
- **precondition**：资源监控
- **test_data**：每秒上报资源使用率
- **expected**：监控埋点（内存/CPU/DB 连接/玩家资源）+ 异常告警
- **notes**：注意"埋点" vs "告警"——埋点是数据采集，告警是通知

---

## 3. 边界陷阱

### 边界 1：vs AUX D（资源管理）
- **混淆点**："资源管理" 看似 I → 实际 AUX D 测"资源加载/卸载底层"，I 测"业务资源耗尽如何降级"
- **判定规则**：测"资源底层（加载/释放/引用计数）" → 归 AUX D；测"业务资源耗尽 + 降级" → 归 SPECIAL I
- **instance**：贴图资源释放 → 归 AUX D；背包满拾取失败 → 归 I

### 边界 2：vs AUX K（性能监控）
- **混淆点**："性能监控" 看似 I → 实际 AUX K 测"性能监控底层"（FPS/内存），I 测"资源耗尽业务降级"
- **判定规则**：测"性能监控底层" → 归 AUX K；测"资源耗尽业务处理" → 归 SPECIAL I
- **instance**：FPS 监控组件 → 归 AUX K；CPU 打满时业务降级 → 归 I

### 边界 3：vs BIZ（业务资源）
- **混淆点**："玩家资源" 看似 I → 实际 BIZ 测"玩家资源正常流程"，I 测"资源耗尽异常"
- **判定规则**：测"业务资源正常流转" → 归 BIZ；测"资源耗尽时的拦截/降级" → 归 SPECIAL I
- **instance**：购买商品扣款 → 归 BIZ；背包满购买失败 → 归 I

### 边界 4：vs E（服务 HA）
- **混淆点**："服务器资源" 看似 E → 实际 E 测"服务宕机 + Failover"，I 测"服务资源耗尽（未宕机）"
- **判定规则**：测"服务宕机恢复" → 归 SPECIAL E；测"服务资源耗尽降级" → 归 SPECIAL I
- **instance**：服务宕机 → 归 E；内存 95% 业务降级 → 归 I

---

## 4. 验证证据

### 视觉证据
- 背包满时"背包已满，请清理"提示
- 邮件满时"邮件已满"提示
- 系统繁忙时"系统繁忙，请稍后重试"提示
- 排队时"您前面还有 X 位"提示
- 邮件将满时"邮件将满，请清理"弹窗

### 日志证据
- `resource.bag_full` 关键词：背包满
- `resource.warehouse_full` 关键词：仓库满
- `resource.mail_full` 关键词：邮件满
- `resource.memory_high` 关键词：内存高
- `resource.cpu_high` 关键词：CPU 高
- `resource.db_pool_exhaust` 关键词：DB 连接池耗尽
- `resource.degrade_enabled` 关键词：业务降级启用
- `resource.queue_entered` 关键词：进入排队队列
- `resource.rejected` 关键词：拒绝新操作

### 数据证据
- `player_bag` 表 `capacity_used` = `capacity_total` 时拒绝
- `player_mail` 表 `mail_count` = `mail_limit` 时拒绝
- `server_metrics` 表记录内存/CPU/DB 连接使用率
- `degrade_log` 表记录业务降级事件
- 资源耗尽时玩家数据无半写
- 排队队列长度记录在 `queue_log` 表

### 性能证据
- 资源检查耗时 < 5ms / 请求
- 业务降级启用耗时 < 100ms
- 排队队列入队 < 10ms
- 资源监控上报 < 1s / 周期
- 资源恢复后业务恢复 < 5s
