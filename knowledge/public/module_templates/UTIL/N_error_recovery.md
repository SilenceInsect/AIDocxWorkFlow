# N. 全局崩溃捕获 + 底层异常兜底

> **子类代码**：`ERROR_RECOVERY`
> **归属模块**：`AUX`
> **来源**：用户细化定义 §16「异常兜底辅助组件」（**v1.6.1 业务异常部分已迁出**）
>
> **v1.6.1 变更**：剔除原"业务异常处理"部分（业务异常归 **BIZ 模块**）——本子模板**只保留底层崩溃捕获/重试/操作队列**。
>
> **测什么**：全局崩溃捕获、错误上报、数据损坏修复、断线操作缓存、操作失败重试。
> **不测什么**：网络异常（归 B）、业务异常（归 BIZ）、UI 异常（归 UI）、特殊场景（归 SPECIAL）。

---

## 1. 典型场景

### 场景 1：全局崩溃捕获
- 业务背景：游戏崩溃
- 涉及工具：异常捕获器
- 触发动作：未捕获异常
- 验证点：捕获、上报

### 场景 2：崩溃堆栈
- 业务背景：游戏崩溃
- 涉及工具：堆栈捕获
- 触发动作：崩溃发生
- 验证点：堆栈 + 设备信息

### 场景 3：错误上报
- 业务背景：异常收集
- 涉及工具：错误上报
- 触发动作：异常发生
- 验证点：上报服务端

### 场景 4：上报失败兜底
- 业务背景：上报时网络断开
- 涉及工具：本地缓存
- 触发动作：本地缓存 → 重连上报
- 验证点：本地缓存、不丢

### 场景 5：数据损坏自动修复
- 业务背景：存档损坏
- 涉及工具：数据修复
- 触发动作：启动游戏
- 验证点：自动修复

### 场景 6：断线操作缓存
- 业务背景：断线
- 涉及工具：操作队列
- 触发动作：断线时玩家操作
- 验证点：操作缓存、重连后执行

### 场景 7：操作队列顺序
- 业务背景：断线
- 涉及工具：操作队列
- 触发动作：5 个操作缓存
- 验证点：重连后按顺序执行

### 场景 8：操作幂等
- 业务背景：操作缓存
- 涉及工具：去重
- 触发动作：重发相同操作
- 验证点：服务端幂等、不重复

### 场景 9：操作失败重试
- 业务背景：操作失败
- 涉及工具：失败重试
- 触发动作：操作失败
- 验证点：自动重试

### 场景 10：指数退避
- 业务背景：连续失败
- 涉及工具：退避策略
- 触发动作：观察重试间隔
- 验证点：1s → 2s → 4s

### 场景 11：全局崩溃不闪退
- 业务背景：未捕获异常
- 触发动作：崩溃发生
- 验证点：捕获后不闪退（按设计）

---

## 2. 种子测试点（TP 模板）

### TP-001（ERROR_RECOVERY）：全局崩溃捕获
- **scenario**：场景 1
- **module**：`ERROR_RECOVERY`
- **precondition**：游戏运行
- **test_data**：触发未捕获异常
- **expected**：崩溃捕获、上报
- **notes**：注意"捕获"vs"闪退"

### TP-002（ERROR_RECOVERY）：崩溃堆栈
- **scenario**：场景 2
- **module**：`ERROR_RECOVERY`
- **precondition**：崩溃
- **test_data**：观察崩溃报告
- **expected**：含堆栈、设备信息
- **notes**：注意"堆栈"vs"位置"

### TP-003（ERROR_RECOVERY）：错误上报
- **scenario**：场景 3
- **module**：`ERROR_RECOVERY`
- **precondition**：异常发生
- **test_data**：观察上报
- **expected**：上报服务端
- **notes**：注意"上报"vs"丢失"

### TP-004（ERROR_RECOVERY）：上报失败本地缓存
- **scenario**：场景 4
- **module**：`ERROR_RECOVERY`
- **precondition**：上报时网络断开
- **test_data**：本地缓存
- **expected**：本地缓存、重连后上报
- **notes**：注意"缓存"vs"丢"

### TP-005（ERROR_RECOVERY）：数据损坏自动修复
- **scenario**：场景 5
- **module**：`ERROR_RECOVERY`
- **precondition**：存档损坏
- **test_data**：启动游戏
- **expected**：自动修复
- **notes**：注意"修复"vs"重置"

### TP-006（ERROR_RECOVERY）：断线操作缓存
- **scenario**：场景 6
- **module**：`ERROR_RECOVERY`
- **precondition**：玩家在线
- **test_data**：断线时点击购买
- **expected**：操作缓存、重连后执行
- **notes**：注意"缓存"vs"丢"

### TP-007（ERROR_RECOVERY）：操作队列顺序
- **scenario**：场景 7
- **module**：`ERROR_RECOVERY`
- **precondition**：断线
- **test_data**：5 个操作缓存
- **expected**：重连后按顺序执行
- **notes**：注意"顺序"vs"并行"

### TP-008（ERROR_RECOVERY）：操作幂等
- **scenario**：场景 8
- **module**：`ERROR_RECOVERY`
- **precondition**：操作缓存
- **test_data**：重发相同操作
- **expected**：服务端幂等、不重复
- **notes**：注意"幂等"vs"重复"

### TP-009（ERROR_RECOVERY）：操作失败重试
- **scenario**：场景 9
- **module**：`ERROR_RECOVERY`
- **precondition**：操作失败
- **test_data**：自动重试
- **expected**：3 次后放弃
- **notes**：注意"重试次数"

### TP-010（ERROR_RECOVERY）：指数退避
- **scenario**：场景 10
- **module**：`ERROR_RECOVERY`
- **precondition**：连续失败
- **test_data**：观察重试间隔
- **expected**：1s → 2s → 4s 指数退避
- **notes**：注意"退避"vs"固定"

### TP-011（ERROR_RECOVERY）：全局崩溃不闪退
- **scenario**：场景 11
- **module**：`ERROR_RECOVERY`
- **precondition**：未捕获异常
- **test_data**：崩溃发生
- **expected**：捕获后优雅退出（按设计）
- **notes**：注意"不闪退"vs"无感"

### TP-012（ERROR_RECOVERY）：服务端异常重试
- **scenario**：通用
- **module**：`ERROR_RECOVERY`
- **precondition**：服务端 500
- **test_data**：客户端重试
- **expected**：自动重试 + 错误上报
- **notes**：注意"客户端"vs"服务端"重试

### TP-013（ERROR_RECOVERY）：数据兜底默认值
- **scenario**：场景 5
- **module**：`ERROR_RECOVERY`
- **precondition**：数据缺失
- **test_data**：读取数据
- **expected**：返回默认值
- **notes**：注意"兜底"vs"崩溃"

### TP-014（ERROR_RECOVERY）：ANR 监控（移动端）
- **scenario**：通用
- **module**：`ERROR_RECOVERY`
- **precondition**：游戏卡住 5s
- **test_data**：ANR 触发
- **expected**：ANR 报告生成
- **notes**：注意"ANR"vs"崩溃"

---

## 3. 边界陷阱

### 边界 1：vs B. 网络层
- **混淆点**：「网络"异常"」——B 测网络层异常、N 测全局
- **判定规则**：测"网络断开/超时" → B；测"全局崩溃捕获" → N
- **实例**：网络超时错误回调 → B；全局崩溃 → N-001

### 边界 2：vs J. 存储
- **混淆点**：「错误"上报"」——N 测异常、J 测存储
- **判定规则**：测"异常兜底/重试" → N；测"日志/埋点工具" → J
- **实例**：异常弹窗 → N；崩溃日志 → J

### 边界 3：vs SPECIAL
- **混淆点**：「异常"处理"」——N 测通用兜底、SPECIAL 测业务
- **判定规则**：测"通用异常框架" → N；测"特殊场景处理" → SPECIAL
- **实例**：全局崩溃 → N；弱网降级 → SPECIAL

### 边界 4：vs F. 离线/版本更新
- **混淆点**：「断线"恢复"」——F 测下载、N 测操作
- **判定规则**：测"断点续传" → F；测"断线操作缓存" → N
- **实例**：离线包断点续传 → F；断线时购买操作缓存 → N

### 边界 5：vs BIZ
- **混淆点**：「异常"业务"」——N 测底层、BIZ 测业务
- **判定规则**：测"底层崩溃/重试" → N；测"业务异常处理（如购买失败补偿）" → BIZ
- **实例**：操作失败重试 3 次 → N；购买失败补偿金币 → BIZ

---

## 4. 验证证据

### 视觉证据
- 异常弹窗截图
- 崩溃报告截图

### 日志证据
- 异常捕获日志
- 错误上报日志
- 重试日志
- 数据修复日志

### 数据证据
- 崩溃报告表
- 错误率统计
- 修复成功率

### 性能证据
- 异常捕获耗时 < 1ms
- 重连后操作恢复 < 3s

---

## 5. 迁移说明（v1.6 → v1.6.1）

**原 v1.6 的 N_error_recovery 含两类内容**：

| 旧内容 | 新位置 |
|---|---|
| 全局崩溃、错误上报、断线操作、失败重试 | **N_error_recovery.md（当前文件，保留）** |
| 业务异常弹窗（如"购买失败"提示）| **BIZ 模块**（v1.11 待建） |
| 业务异常补偿 | **BIZ 模块**（v1.11 待建） |

**调整说明**：
- 子类代码不变：`ERROR_RECOVERY`
- 模板名不变：`N_error_recovery.md`
- 职责变窄：原"全局 + 业务异常" → 现"仅底层全局 + 兜底"
- TP 数量：18 → 14（移除 4 个业务异常项）
