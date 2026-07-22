# G. 限时提醒浮窗 + 错误提示文案专项

> **子类代码**：`TIMED_REMINDER`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 G（v1.7 合并：限时倒计时 + 错误文案 + 资源过期 + 定时提醒）
>
> **测什么**：限时活动倒计时、buff 持续倒计时、道具过期、每日次数重置、定时推送弹窗；统一规范错误文案、分级文案样式、特殊场景文案（离线/跨服/权限/作弊/过期）。
> **不测什么**：浮窗 UI 样式（归 UI `F.GUIDE_HINT`）、倒计时定时器逻辑（归 BIZ `G.SCHEDULED_TASK`）、弹窗容器（归 D `MODAL_DIALOG`）。
> **与其他子类的差异**：G 是"时间/规则触发"的提醒；E 是"事件触发"的短提示；D 是"事件触发"的强制弹窗。

---

## 1. 典型场景

### 场景 1：活动倒计时弹窗
- 业务背景：限时活动
- 涉及元素：活动倒计时
- 触发动作：活动剩余 1 小时
- 验证点：弹窗显示倒计时、点击进入活动

### 场景 2：Buff 持续倒计时
- 业务背景：buff 持续中
- 涉及元素：buff 倒计时浮窗
- 触发动作：获得 buff
- 验证点：浮窗显示倒计时、归零后消失

### 场景 3：道具过期提醒
- 业务背景：限时道具
- 涉及元素：道具过期提示
- 触发动作：道具即将过期
- 验证点：弹窗显示"X 天后过期"

### 场景 4：每日次数重置提醒
- 业务背景：副本次数重置
- 涉及元素：重置提醒
- 触发动作：每日 0:00
- 验证点：弹窗显示"次数已重置"

### 场景 5：每日签到弹窗
- 业务背景：每日签到
- 涉及元素：签到弹窗
- 触发动作：每日首次登录
- 验证点：定时弹出签到弹窗

### 场景 6：限时活动开启定时推送
- 业务背景：活动开启
- 涉及元素：活动开启推送
- 触发动作：到达活动开始时间
- 验证点：定时推送弹窗

### 场景 7：统一错误文案
- 业务背景：玩家看到错误
- 涉及元素：错误文案
- 触发动作：触发错误
- 验证点：同一种错误全局文案一致

### 场景 8：分级错误文案样式
- 业务背景：不同等级错误
- 涉及元素：错误样式
- 触发动作：触发不同级别错误
- 验证点：普通/警告/严重样式区分

### 场景 9：离线提示
- 业务背景：玩家离线
- 涉及元素：离线文案
- 触发动作：网络断开
- 验证点：文案"网络断开，请检查"

### 场景 10：跨服限制提示
- 业务背景：跨服操作
- 涉及元素：跨服文案
- 触发动作：尝试跨服操作
- 验证点：文案"该功能跨服不可用"

### 场景 11：权限不足提示
- 业务背景：权限不足
- 涉及元素：权限文案
- 触发动作：访问受限功能
- 验证点：文案"权限不足"

### 场景 12：作弊拦截提示
- 业务背景：检测到作弊
- 涉及元素：反作弊文案
- 触发动作：作弊行为
- 验证点：文案"检测到异常"

### 场景 13：资源过期提示
- 业务背景：道具过期
- 涉及元素：过期文案
- 触发动作：道具过期
- 验证点：文案"已过期"

### 场景 14：定时弹窗周期
- 业务背景：定时弹窗
- 涉及元素：弹窗
- 触发动作：定时器
- 验证点：弹窗周期正确

### 场景 15：定时弹窗跨场景
- 业务背景：定时弹窗
- 涉及元素：弹窗
- 触发动作：切场景
- 验证点：弹窗跨场景正常

---

## 2. 种子测试点（TP 模板）

### TP-001（TIMED_REMINDER）：活动倒计时弹窗
- **scenario**：场景 1
- **module**：`TIMED_REMINDER`
- **precondition**：活动剩余 1 小时
- **test_data**：登录
- **expected**：弹窗"活动倒计时 1 小时"、点击进入
- **notes**：与 F 浮窗区分

### TP-002（TIMED_REMINDER）：Buff 持续倒计时浮窗
- **scenario**：场景 2
- **module**：`TIMED_REMINDER`
- **precondition**：获得 buff 30s
- **test_data**：获得 buff
- **expected**：浮窗显示倒计时、归零消失
- **notes**：与服务端时间同步

### TP-003（TIMED_REMINDER）：buff 倒计时与服务器时间同步
- **scenario**：场景 2
- **module**：`TIMED_REMINDER`
- **precondition**：本地时间被修改
- **test_data**：调整本地时间
- **expected**：倒计时仍按服务器时间
- **notes**：防止本地时间作弊

### TP-004（TIMED_REMINDER）：道具过期提醒
- **scenario**：场景 3
- **module**：`TIMED_REMINDER`
- **precondition**：道具 3 天后过期
- **test_data**：登录
- **expected**：弹窗"X 天后过期"
- **notes**：邮件附件型过期

### TP-005（TIMED_REMINDER）：每日次数重置提醒
- **scenario**：场景 4
- **module**：`TIMED_REMINDER`
- **precondition**：每日 0:00
- **test_data**：跨日
- **expected**：弹窗"次数已重置"
- **notes**：与 BIZ 定时任务配合

### TP-006（TIMED_REMINDER）：每日签到弹窗
- **scenario**：场景 5
- **module**：`TIMED_REMINDER`
- **precondition**：每日首次登录
- **test_data**：登录
- **expected**：定时弹出签到弹窗
- **notes**：与 D 登录礼包区分

### TP-007（TIMED_REMINDER）：限时活动开启定时推送
- **scenario**：场景 6
- **module**：`TIMED_REMINDER`
- **precondition**：活动开始时间
- **test_data**：到达活动开始
- **expected**：定时推送弹窗
- **notes**：与 J 运营推送区分

### TP-008（TIMED_REMINDER）：统一错误文案
- **scenario**：场景 7
- **module**：`TIMED_REMINDER`
- **precondition**：金币不足错误
- **test_data**：多个场景触发金币不足
- **expected**：所有场景下文案一致"金币不足"
- **notes**：文案库统一

### TP-009（TIMED_REMINDER）：普通错误样式
- **scenario**：场景 8
- **module**：`TIMED_REMINDER`
- **precondition**：普通错误
- **test_data**：触发
- **expected**：普通样式（白底/灰字）
- **notes**：分级

### TP-010（TIMED_REMINDER）：警告错误样式
- **scenario**：场景 8
- **module**：`TIMED_REMINDER`
- **precondition**：警告错误
- **test_data**：触发
- **expected**：警告样式（黄底/深字）
- **notes**：分级

### TP-011（TIMED_REMINDER）：严重错误样式
- **scenario**：场景 8
- **module**：`TIMED_REMINDER`
- **precondition**：严重错误
- **test_data**：触发
- **expected**：严重样式（红底/白字/警示）
- **notes**：分级

### TP-012（TIMED_REMINDER）：离线提示文案
- **scenario**：场景 9
- **module**：`TIMED_REMINDER`
- **precondition**：网络断开
- **test_data**：操作
- **expected**：文案"网络断开，请检查"
- **notes**：与 UTIL 网络检测配合

### TP-013（TIMED_REMINDER）：跨服限制提示
- **scenario**：场景 10
- **module**：`TIMED_REMINDER`
- **precondition**：跨服玩家
- **test_data**：访问跨服限制功能
- **expected**：文案"该功能跨服不可用"
- **notes**：与 LINK 跨服配合

### TP-014（TIMED_REMINDER）：权限不足提示
- **scenario**：场景 11
- **module**：`TIMED_REMINDER`
- **precondition**：权限不足
- **test_data**：访问受限功能
- **expected**：文案"权限不足"
- **notes**：与 BIZ 权限检查配合

### TP-015（TIMED_REMINDER）：作弊拦截提示
- **scenario**：场景 12
- **module**：`TIMED_REMINDER`
- **precondition**：触发反作弊
- **test_data**：异常操作
- **expected**：文案"检测到异常"、不上报具体原因（防绕过）
- **notes**：与 SPECIAL 反作弊配合

### TP-016（TIMED_REMINDER）：资源过期文案
- **scenario**：场景 13
- **module**：`TIMED_REMINDER`
- **precondition**：道具过期
- **test_data**：使用过期道具
- **expected**：文案"已过期"
- **notes**：清晰简洁

### TP-017（TIMED_REMINDER）：定时弹窗周期正确
- **scenario**：场景 14
- **module**：`TIMED_REMINDER`
- **precondition**：定时弹窗配置
- **test_data**：观察 24h
- **expected**：弹窗按周期弹出
- **notes**：与 BIZ 定时任务配合

### TP-018（TIMED_REMINDER）：定时弹窗跨场景
- **scenario**：场景 15
- **module**：`TIMED_REMINDER`
- **precondition**：定时弹窗即将弹出
- **test_data**：切场景
- **expected**：弹窗在新场景弹出
- **notes**：跨场景正确

### TP-019（TIMED_REMINDER）：多语言错误文案
- **scenario**：场景 7
- **module**：`TIMED_REMINDER`
- **precondition**：切到日语
- **test_data**：触发错误
- **expected**：错误文案日文化
- **notes**：i18n

### TP-020（TIMED_REMINDER）：错误文案长度
- **scenario**：场景 7
- **module**：`TIMED_REMINDER`
- **precondition**：长错误信息
- **test_data**：超长错误
- **expected**：文案截断或自动换行
- **notes**：UI 样式

---

## 3. 边界陷阱

### 边界 1：vs D. 模态弹窗
- **混淆点**：「提醒"弹窗"」——G 浮窗、D 强制
- **判定规则**：测"非强制浮窗" → G；测"强制弹窗" → D
- **实例**：活动倒计时浮窗 → G；防沉迷强制弹窗 → D

### 边界 2：vs E. Toast
- **混淆点**：「倒计时"提示"」——G 动态倒计时、E 静态文案
- **判定规则**：测"动态倒计时浮窗" → G；测"静态短提示" → E
- **实例**：活动倒计时 23:45:12 → G；Toast"购买成功" → E

### 边界 3：vs BIZ `G.SCHEDULED_TASK`
- **混淆点**：「定时"弹窗"」——G 测弹窗、BIZ 测定时器
- **判定规则**：测"弹窗显示内容" → G；测"定时任务调度" → BIZ
- **实例**：每日签到弹窗 → G；定时任务调度逻辑 → BIZ

### 边界 4：vs BIZ `BIZ_LOGIC`
- **混淆点**：「错误"提示"」——G 测文案、BIZ 测逻辑
- **判定规则**：测"错误文案样式" → G；测"为什么错误" → BIZ
- **实例**：错误文案"金币不足" → G；金币不足检查逻辑 → BIZ

### 边界 5：vs SPECIAL `SPECIAL.ANTI_CHEAT`
- **混淆点**：「作弊"提示"」——G 测文案、SPECIAL 测检测
- **判定规则**：测"反作弊文案" → G；测"反作弊检测逻辑" → SPECIAL
- **实例**：反作弊文案 → G；反作弊检测 → SPECIAL

---

## 4. 验证证据

### 视觉证据
- 各种倒计时浮窗截图
- 分级错误样式截图
- 多语言错误截图

### 日志证据
- `timed_reminder.show` 事件
- `error.toast` 事件（参数：error_code/level）
- `scheduled.push` 事件

### 数据证据
- 倒计时同步记录
- 错误触发记录
- 文案库

### 性能证据
- 倒计时刷新精度 1s 内
- 多弹窗堆叠性能
