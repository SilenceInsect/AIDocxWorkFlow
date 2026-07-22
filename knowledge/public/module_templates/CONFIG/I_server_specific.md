# I. 服务端专属配置校验

> **子类代码**：`SERVER_CONFIG`
> **归属模块**：`CONFIG`
> **来源**：用户细化定义 §5(5)「服务端专属配置校验」
>
> **测什么**：全局服务器常量、定时任务、GM 权限、分布式服配置。
> **不测什么**：单字段合法性（归 A）、热更（归 D）、客户端解析（归 E）。
> **与其他子类的差异**：I 关注"服务端业务配置"——A 关注"字段本身"，E 关注"解析性能"。

---

## 1. 典型场景

### 场景 1：开服时间
- 业务背景：新服开启
- 涉及字段：`server_open_time`
- 触发动作：到达开服时间
- 验证点：服务端开启、玩家可进入

### 场景 2：防沉迷阈值
- 业务背景：未成年保护
- 涉及字段：`anti_addiction_minutes_per_day` = 90
- 触发动作：玩家玩 90 分钟
- 验证点：服务端踢出、提示"已超过防沉迷时长"

### 场景 3：服务器倍率
- 业务背景：开荒/追赶
- 涉及字段：`server_exp_rate` = 2.0
- 触发动作：玩家获得经验
- 验证点：玩家获得 2 倍经验

### 场景 4：定时任务 - 活动开启
- 业务背景：限时活动
- 涉及字段：`activity_start_time`
- 触发动作：到达开始时间
- 验证点：活动自动开启

### 场景 5：定时任务 - 活动关闭
- 业务背景：限时活动
- 涉及字段：`activity_end_time`
- 触发动作：到达结束时间
- 验证点：活动自动关闭、奖励停止发放

### 场景 6：定时任务 - 邮件发放
- 业务背景：节日福利
- 涉及字段：`mail_schedule_cron`
- 触发动作：到达定时时间
- 验证点：邮件自动发放到玩家邮箱

### 场景 7：GM 指令
- 业务背景：运营操作
- 涉及字段：`gm_command_permission`
- 触发动作：GM 玩家使用指令
- 验证点：GM 指令执行、权限校验

### 场景 8：多服共享配置
- 业务背景：分布式服
- 涉及字段：基础配置
- 触发动作：服 1 修改基础配置
- 验证点：服 2/3/4 同步生效

### 场景 9：单服独有配置
- 业务背景：每个服独立
- 涉及字段：开服时间、玩家数据
- 触发动作：服 1 独有
- 验证点：不影响服 2/3/4

---

## 2. 种子测试点（TP 模板）

### TP-001（SERVER_CONFIG）：开服时间生效
- **scenario**：场景 1
- **module**：`SERVER_CONFIG`
- **precondition**：新服 `server_open_time` = 2026-06-15 10:00
- **test_data**：到达 10:00
- **expected**：服务端开启、玩家可进入
- **notes**：注意"开服前"vs"开服后"

### TP-002（SERVER_CONFIG）：开服时间倒计时
- **scenario**：场景 1
- **module**：`SERVER_CONFIG`
- **precondition**：开服前
- **test_data**：开服前 1 小时进入
- **expected**：显示倒计时、提示"距离开服还有 X 小时"
- **notes**：注意"提前进入"vs"开服后"

### TP-003（SERVER_CONFIG）：防沉迷阈值触发
- **scenario**：场景 2
- **module**：`SERVER_CONFIG`
- **precondition**：`anti_addiction_minutes_per_day` = 90
- **test_data**：玩家玩 90 分钟后继续
- **expected**：服务端踢出、提示"已超过防沉迷时长"
- **notes**：注意"未成年人"vs"成年人"

### TP-004（SERVER_CONFIG）：防沉迷重置
- **scenario**：场景 2
- **module**：`SERVER_CONFIG`
- **precondition**：玩家已被踢出
- **test_data**：次日 0 点
- **expected**：时长计数重置、玩家可继续
- **notes**：注意"自然日"vs"24 小时"

### TP-005（SERVER_CONFIG）：服务器倍率生效
- **scenario**：场景 3
- **module**：`SERVER_CONFIG`
- **precondition**：`server_exp_rate` = 2.0
- **test_data**：玩家击杀怪物获 100 经验
- **expected**：玩家获得 200 经验
- **notes**：注意"全服"vs"个人"倍率

### TP-006（SERVER_CONFIG）：定时活动开启
- **scenario**：场景 4
- **module**：`SERVER_CONFIG`
- **precondition**：`activity_start_time` = 2026-06-15 12:00
- **test_data**：到达 12:00
- **expected**：活动自动开启、玩家可见
- **notes**：注意"全服活动"vs"分服活动"

### TP-007（SERVER_CONFIG）：定时活动关闭
- **scenario**：场景 5
- **module**：`SERVER_CONFIG`
- **precondition**：`activity_end_time` = 2026-06-22 12:00
- **test_data**：到达 22 日 12:00
- **expected**：活动自动关闭、玩家不可见
- **notes**：注意"硬关闭"vs"软关闭（倒计时）"

### TP-008（SERVER_CONFIG）：活动结束后奖励停止
- **scenario**：场景 5
- **module**：`SERVER_CONFIG`
- **precondition**：活动已结束
- **test_data**：玩家尝试领取活动奖励
- **expected**：提示"活动已结束"、不可领取
- **notes**：注意"补发"vs"不补发"

### TP-009（SERVER_CONFIG）：定时邮件发放
- **scenario**：场景 6
- **module**：`SERVER_CONFIG`
- **precondition**：`mail_schedule_cron` = "0 0 * * *"
- **test_data**：到达每日 0 点
- **expected**：邮件自动发放到所有玩家邮箱
- **notes**：注意"在线玩家"vs"全服玩家"

### TP-010（SERVER_CONFIG）：邮件发放失败重试
- **scenario**：场景 6
- **module**：`SERVER_CONFIG`
- **precondition**：邮件发放时玩家离线
- **test_data**：玩家离线
- **expected**：邮件暂存、玩家上线时收到
- **notes**：注意"补发"vs"丢失"

### TP-011（SERVER_CONFIG）：GM 指令权限
- **scenario**：场景 7
- **module**：`SERVER_CONFIG`
- **precondition**：`gm_command_permission` 列表
- **test_data**：非 GM 玩家使用 `gm_add_item` 指令
- **expected**：权限拒绝、提示"无权限"
- **notes**：注意"普通玩家"vs"运营玩家"

### TP-012（SERVER_CONFIG）：GM 指令执行
- **scenario**：场景 7
- **module**：`SERVER_CONFIG`
- **precondition**：GM 玩家
- **test_data**：GM 使用 `gm_add_item` 指令 + item_id=100 + count=10
- **expected**：玩家获得 10 个道具 100
- **notes**：注意"GM 指令"vs"GM 后台"

### TP-013（SERVER_CONFIG）：GM 指令审计
- **scenario**：场景 7
- **module**：`SERVER_CONFIG`
- **precondition**：GM 玩家操作
- **test_data**：GM 发指令
- **expected**：审计日志含操作人/时间/内容
- **notes**：注意"审计"vs"匿名"

### TP-014（SERVER_CONFIG）：多服共享配置同步
- **scenario**：场景 8
- **module**：`SERVER_CONFIG`
- **precondition**：服 1/2/3 共享基础配置
- **test_data**：服 1 修改 `base_drop_rate`
- **expected**：服 2/3 同步生效
- **notes**：注意"主从"vs"P2P"同步

### TP-015（SERVER_CONFIG）：单服独有配置隔离
- **scenario**：场景 9
- **module**：`SERVER_CONFIG`
- **precondition**：每个服独立
- **test_data**：服 1 修改 `server_open_time`
- **expected**：不影响服 2/3/4
- **notes**：注意"基础"vs"独有"配置

---

## 3. 边界陷阱

### 边界 1：vs D. 热更新
- **混淆点**：「服务端"配置"」——I 测服务端配置、D 测热更流程
- **判定规则**：测"服务端全局常量生效" → I；测"热更切换" → D
- **实例**：开服时间生效 → I-001；服务端配置热更 → D-007

### 边界 2：vs E. 解析与加载
- **混淆点**：「服务端"解析"」——I 测业务配置、E 测解析性能
- **判定规则**：测"服务端全局常量" → I；测"服务端配置解析性能" → E
- **实例**：开服时间配置 → I-001；服务端配置解析耗时 → E-011

### 边界 3：vs BIZ
- **混淆点**：「开服"逻辑"」——I 测配置层、BIZ 测业务逻辑
- **判定规则**：测"开服时间配置生效" → I；测"开服后玩家创建/进入逻辑" → BIZ
- **实例**：开服时间到达 → I-001；玩家创建角色 → BIZ

### 边界 4：vs F. 版本兼容
- **混淆点**：「灰度"配置"」——F 测版本/渠道、I 测服务端
- **判定规则**：测"灰度/白名单/渠道" → F；测"服务端全局常量/定时" → I
- **实例**：灰度玩家白名单 → F-012；开服时间 → I-001

---

## 4. 验证证据

### 视觉证据
- 开服倒计时截图
- 防沉迷提示截图
- 活动开启截图

### 日志证据
- 定时任务执行日志
- GM 指令审计日志
- 配置同步日志

### 数据证据
- DB 中开服时间字段
- GM 指令记录表
- 多服配置 diff

### 性能证据
- 定时任务精度 < 1s
- 多服配置同步延迟 < 5s
