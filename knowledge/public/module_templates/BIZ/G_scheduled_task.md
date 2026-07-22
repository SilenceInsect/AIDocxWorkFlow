# G. 定时 & 异步任务业务

> **子类代码**：`BIZ_SCHEDULED_TASK`
> **归属模块**：`BIZ`
> **来源**：用户细化定义 §7「定时&异步任务业务」（原定义完全缺失，新增）
>
> **测什么**：每日零点重置、定时活动、邮件发放、buff 过期、定时排行榜、异步任务延迟与服务重启续跑。
> **不测什么**：业务逻辑（归 A）、状态机（归 D）、DB 落库（归 E）、定时器组件本身（归 UTIL）。
> **与其他子类的差异**：G 关注"定时/异步业务的执行"——A 关注"业务"，D 关注"状态切换"，H 关注"付费"。

---

## 1. 典型场景

### 场景 1：每日零点重置
- 业务背景：日常任务、体力、商店
- 涉及数据：玩家每日数据
- 触发动作：跨过 0 点
- 验证点：日常数据清空、体力恢复

### 场景 2：每周一重置
- 业务背景：周常任务
- 涉及数据：周常数据
- 触发动作：周一 0 点
- 验证点：周常数据清空

### 场景 3：限时活动开启/关闭
- 业务背景：节日活动
- 涉及数据：活动状态
- 触发动作：定时开启/关闭
- 验证点：活动按时间正确切换

### 场景 4：定时邮件发放
- 业务背景：生日祝福、节日礼物
- 涉及数据：玩家邮件
- 触发动作：定时任务
- 验证点：玩家在 0 点收到邮件

### 场景 5：Buff 定时过期
- 业务背景：战斗 Buff
- 涉及数据：Buff 状态
- 触发动作：Buff 持续时间到
- 验证点：Buff 过期、属性回退

### 场景 6：定时排行榜结算
- 业务背景：赛季结算
- 涉及数据：排行榜
- 触发动作：赛季结束
- 验证点：排名归档、奖励发放

### 场景 7：异步任务延迟执行
- 业务背景：发奖、清理
- 涉及数据：异步队列
- 触发动作：触发异步任务
- 验证点：5s 内完成

### 场景 8：服务重启后定时任务续跑
- 业务背景：服务宕机重启
- 涉及数据：未执行的定时任务
- 触发动作：服务恢复
- 验证点：补跑未执行任务

### 场景 9：定时清理过期数据
- 业务背景：临时邮件、临时道具
- 涉及数据：临时数据
- 触发动作：定时清理
- 验证点：过期数据被清

### 场景 10：定时数据备份
- 业务背景：DB 备份
- 涉及数据：全量数据
- 触发动作：凌晨 3 点
- 验证点：备份文件生成

### 场景 11：多定时任务并发
- 业务背景：0 点同时有 100 个任务
- 涉及数据：定时任务
- 触发动作：0 点触发
- 验证点：所有任务按序执行、无遗漏

### 场景 12：定时任务依赖
- 业务背景：任务 A 完成后才能执行 B
- 涉及数据：任务依赖
- 触发动作：触发 A
- 验证点：A 完成后 B 自动执行

---

## 2. 种子测试点（TP 模板）

### TP-001（BIZ_SCHEDULED_TASK）：日常任务零点重置
- **scenario**：场景 1
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：日常任务已领
- **test_data**：跨过 0 点
- **expected**：日常任务进度清空、状态重置
- **notes**：注意"重置"vs"清空"+"时区"

### TP-002（BIZ_SCHEDULED_TASK）：体力零点恢复
- **scenario**：场景 1
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：玩家体力 0/100
- **test_data**：跨过 0 点
- **expected**：体力恢复 100
- **notes**：注意"满体力"vs"上限"

### TP-003（BIZ_SCHEDULED_TASK）：商店刷新
- **scenario**：场景 1
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：玩家已购 5 件
- **test_data**：跨过 0 点
- **expected**：商店商品重置、限购次数清零
- **notes**：注意"每日刷新"vs"每周刷新"

### TP-004（BIZ_SCHEDULED_TASK）：周常任务周一重置
- **scenario**：场景 2
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：周常任务已领
- **test_data**：跨过周一 0 点
- **expected**：周常任务进度清空
- **notes**：注意"周一 0 点"vs"周日 24 点"+"时区"

### TP-005（BIZ_SCHEDULED_TASK）：限时活动开启
- **scenario**：场景 3
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：活动 6/15 0 点开启
- **test_data**：6/15 0:00
- **expected**：活动状态 未开启→进行中、玩家可进入
- **notes**：注意"定时"vs"运营手动"+"预热"

### TP-006（BIZ_SCHEDULED_TASK）：限时活动关闭
- **scenario**：场景 3
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：活动 6/30 24 点结束
- **test_data**：6/30 24:00
- **expected**：活动状态 进行中→已结束、入口隐藏
- **notes**：注意"结束"vs"即将结束"+"清临时道具"

### TP-007（BIZ_SCHEDULED_TASK）：生日邮件
- **scenario**：场景 4
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：玩家生日 6/15
- **test_data**：6/15 0:00
- **expected**：玩家收到生日祝福邮件
- **notes**：注意"0 点"vs"游戏内时间"+"离线玩家也收"

### TP-008（BIZ_SCHEDULED_TASK）：节日礼物
- **scenario**：场景 4
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：节日 6/1
- **test_data**：6/1 0:00
- **expected**：所有玩家收到节日礼物邮件
- **notes**：注意"全员"vs"活跃玩家"+"10 万级批量"

### TP-009（BIZ_SCHEDULED_TASK）：Buff 30s 过期
- **scenario**：场景 5
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：Buff 持续 30s
- **test_data**：第 31 秒查看
- **expected**：Buff 已过期、属性回退
- **notes**：注意"过期"vs"被驱散"+"定时清理"

### TP-010（BIZ_SCHEDULED_TASK）：赛季结算
- **scenario**：场景 6
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：赛季 6/30 结束
- **test_data**：6/30 24:00
- **expected**：排行榜归档、段位奖励发放、积分清零
- **notes**：注意"归档"vs"清空"+"下赛季开启"

### TP-011（BIZ_SCHEDULED_TASK）：异步发奖
- **scenario**：场景 7
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：GM 触发 1000 笔发奖
- **test_data**：`gm_reward(1000 players, 100 diamond)`
- **expected**：5 分钟内全部到账
- **notes**：注意"异步"vs"同步"+"队列"

### TP-012（BIZ_SCHEDULED_TASK）：异步任务延迟
- **scenario**：场景 7
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：异步任务期望 5s 后执行
- **test_data**：触发任务
- **expected**：5s 后执行（容忍 ±1s）
- **notes**：注意"延迟"vs"定时"+"调度精度"

### TP-013（BIZ_SCHEDULED_TASK）：宕机后任务续跑
- **scenario**：场景 8
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：服务宕机、错过 0 点任务
- **test_data**：服务恢复
- **expected**：补跑 0 点任务、无遗漏
- **notes**：注意"补跑"vs"跳过"+"幂等"

### TP-014（BIZ_SCHEDULED_TASK）：重复执行拦截
- **scenario**：场景 8
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：定时任务已执行过
- **test_data**：服务重启后再次扫描
- **expected**：不重复执行
- **notes**：注意"幂等"vs"去重"

### TP-015（BIZ_SCHEDULED_TASK）：过期邮件清理
- **scenario**：场景 9
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：1000 封 7 天前邮件
- **test_data**：定时任务执行
- **expected**：过期邮件标记删除
- **notes**：注意"硬删"vs"软删"+"清理任务频率"

### TP-016（BIZ_SCHEDULED_TASK）：过期道具清理
- **scenario**：场景 9
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：10000 个 7 天前限时道具
- **test_data**：定时任务执行
- **expected**：过期道具清理
- **notes**：注意"批量清理"vs"逐个"

### TP-017（BIZ_SCHEDULED_TASK）：定时数据备份
- **scenario**：场景 10
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：凌晨 3 点备份
- **test_data**：3:00
- **expected**：备份文件生成、大小正常
- **notes**：注意"全量"vs"增量"+"备份保留天数"

### TP-018（BIZ_SCHEDULED_TASK）：多定时任务并发
- **scenario**：场景 11
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：0 点有 100 个任务
- **test_data**：0:00
- **expected**：所有任务按序执行、无遗漏、CPU 不超载
- **notes**：注意"并发"vs"串行"+"线程池"

### TP-019（BIZ_SCHEDULED_TASK）：定时任务依赖
- **scenario**：场景 12
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：任务 A 完成后才能 B
- **test_data**：触发 A
- **expected**：A 完成后 B 自动执行
- **notes**：注意"工作流"vs"DAG"

### TP-020（BIZ_SCHEDULED_TASK）：任务失败重试
- **scenario**：场景 7
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：异步任务失败
- **test_data**：触发任务
- **expected**：自动重试 3 次
- **notes**：注意"重试"vs"告警"+"幂等"

### TP-021（BIZ_SCHEDULED_TASK）：跨时区处理
- **scenario**：场景 1
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：海外服玩家（UTC+0）
- **test_data**：玩家本地 0 点
- **expected**：按玩家本地时区 0 点重置（不是服 0 点）
- **notes**：注意"服时区"vs"玩家时区"

### TP-022（BIZ_SCHEDULED_TASK）：定时任务监控
- **scenario**：场景 11
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：定时任务执行时间监控
- **test_data**：观察 30 天
- **expected**：任务执行时间稳定、异常告警
- **notes**：注意"监控"vs"日志"

### TP-023（BIZ_SCHEDULED_TASK）：跨天发奖
- **scenario**：场景 7
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：跨天批量发奖
- **test_data**：23:59 触发、0:01 完成
- **expected**：发奖归属当天（业务日）
- **notes**：注意"业务日"vs"自然日"

### TP-024（BIZ_SCHEDULED_TASK）：定时任务取消
- **scenario**：场景 7
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：定时任务已调度
- **test_data**：运营取消任务
- **expected**：任务被取消、不执行
- **notes**：注意"取消"vs"暂停"

### TP-025（BIZ_SCHEDULED_TASK）：定时任务并行度
- **scenario**：场景 11
- **module**：`BIZ_SCHEDULED_TASK`
- **precondition**：100 个定时任务、并行度 10
- **test_data**：触发
- **expected**：10 个一批、10 批完成、无遗漏
- **notes**：注意"并行度"vs"线程池"

---

## 3. 边界陷阱

### 边界 1：vs A. 业务
- **混淆点**：「活动"开启"」——A 测业务、G 测定时
- **判定规则**：测"业务结果" → A；测"定时触发" → G
- **实例**：活动开启业务 → A；0 点定时器 → G

### 边界 2：vs D. 状态机
- **混淆点**：「活动"状态切换"」——D 测状态机、G 测定时
- **判定规则**：测"状态切换规则" → D；测"定时触发" → G
- **实例**：活动状态机 → D；定时器触发 → G

### 边界 3：vs UTIL 定时器组件
- **混淆点**：「定时"组件"」——UTIL 测通用工具、G 测业务
- **判定规则**：测"定时器组件" → UTIL；测"定时业务" → G
- **实例**：cron 组件 → UTIL；零点重置业务 → G

### 边界 4：vs H. 付费
- **混淆点**：「充值"回调"」——H 测付费、G 测异步
- **判定规则**：测"订单回调" → H；测"异步任务" → G
- **实例**：订单回调 → H；批量发奖 → G

### 边界 5：vs LOG
- **混淆点**：「定时"日志"」——G 测业务、LOG 测日志
- **判定规则**：测"定时业务" → G；测"日志埋点" → LOG
- **实例**：零点重置业务 → G；重置操作日志 → LOG

---

## 4. 验证证据

### 视觉证据
- 0 点后日常任务重置截图
- 活动开启/关闭 UI 切换截图
- 定时邮件收到截图

### 日志证据
- `CRON_TRIGGER task=xxx time=2026-06-15T00:00:00` 定时器日志
- `TASK_START/TASK_END task=xxx duration=Xms` 任务执行日志
- `TASK_RETRY count=N` 任务重试日志
- `TASK_MISSED task=xxx` 漏跑告警
- `TASK_DUPLICATE_BLOCKED` 重复执行拦截

### 数据证据
- 玩家日常表 `daily_task.last_reset_at`
- 活动状态表 `activity.status, start_at, end_at`
- 定时任务表 `cron_task.last_run_at, next_run_at, status`
- 邮件表 `mail.send_at, sent_by_cron=true`
- 异步任务表 `async_task.status, retry_count`
- 备份文件大小、保留天数

### 性能证据
- 0 点 100 个任务 5 分钟内完成
- 异步任务 P99 延迟 < 1s
- 1000 笔批量发奖 < 5 分钟
- 定时器精度 ±1s
- 任务续跑补齐率 100%
