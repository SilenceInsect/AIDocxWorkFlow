# A. 边界极端场景（数值 / 时间 / 权限 / 中断 / 冲突）

> **子类代码**：`BOUNDARY_EXTREME`
> **归属模块**：`SPECIAL`
> **来源**：用户细化定义 §1「全系统边界极端场景、业务级异常分支」
>
> **测什么**：系统在**数值、时间、权限、互斥、中断**这五类边界上的极端场景是否符合预期——无数据/零值/负数/溢出/超大值、资源不足、活动未开启/已过期、未解锁/等级不足/跨服权限、操作中途被中断/切后台/断线/退出/重启、互斥活动/互斥道具/资源锁抢占。
> **不测什么**：通用业务正向流程（归 BIZ）、底层网络重连框架（归 UTIL）、第三方/跨服异常拦截（归 LINK）、UI 控件异常渲染（归 UI）。
> **与其他子类的差异**：A 关注"业务能正常运转"——B 关注"对抗行为"（反作弊）、C 关注"环境降级"（弱网/防刷）；A 是边界值，B/C 是对抗/异常环境。

---

## 1. 典型场景

### 场景 1：道具数量 0 时使用
- 业务背景：玩家背包某道具数量为 0
- 涉及字段/工具：item_count、use_item
- 触发动作：玩家点击"使用"
- 验证点：拒绝使用并提示"数量不足"

### 场景 2：金币为负数异常状态
- 业务背景：金币余额被改包篡改为 -1
- 涉及字段/工具：gold_balance
- 触发动作：购买商品时金币校验
- 验证点：服务端二次校验拦截，返回错误码

### 场景 3：等级不足时开启功能
- 业务背景：副本要求等级 30，玩家等级 5
- 涉及字段/工具：player_level、required_level
- 触发动作：进入副本入口
- 验证点：入口置灰 + 提示"等级不足"

### 场景 4：活动未开启时领取奖励
- 业务背景：限时活动 19:00 开启，当前 18:59
- 涉及字段/工具：activity_start_time、claim_reward
- 触发动作：玩家点击"领取"
- 验证点：拒绝并提示"活动未开启"

### 场景 5：CD 冷却中再次释放技能
- 业务背景：技能 CD 5s，当前剩余 2s
- 涉及字段/工具：skill_cd
- 触发动作：玩家再次点击技能按钮
- 验证点：技能按钮置灰，释放请求被服务端拦截

### 场景 6：购买中途切后台
- 业务背景：玩家点击"购买"，正在拉起支付
- 涉及字段/工具：purchase_state、bg_fg_event
- 触发动作：玩家按 Home 键
- 验证点：返回前台后状态正确，订单未生成重复扣款

### 场景 7：赛季已结算后访问入口
- 业务背景：赛季 4 已结束，玩家仍持有 S4 入口
- 涉及字段/工具：season_status、season_id
- 触发动作：玩家点击 S4 入口
- 验证点：入口消失/置灰，提示"赛季已结束"

### 场景 8：限时奖励超时未领取
- 业务背景：登录奖励 24h 内可领，超时清空
- 涉及字段/工具：reward_expire_time
- 触发动作：玩家 25h 后登录
- 验证点：奖励已清空，无补发

### 场景 9：互斥道具同时使用
- 业务背景：玩家背包有 A 道具和 B 道具，配置为互斥
- 涉及字段/工具：mutex_group、item_use
- 触发动作：先使用 A，5s 内使用 B
- 验证点：B 使用被拒，提示"已使用同类道具"

### 场景 10：多操作抢占同一资源锁
- 业务背景：限时 Boss 战 1 个名额，多玩家同时进入
- 涉及字段/工具：boss_lock、player_count
- 触发动作：5 个玩家同时点击"进入"
- 验证点：仅 1 个玩家成功，其余排队/提示"名额已满"

---

## 2. 种子测试点（TP 模板）

### TP-001（BOUNDARY_EXTREME）：道具数量为 0
- **scenario**：场景 1
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家背包 item_X 数量 = 0
- **test_data**：item_X 数量 0，触发"使用"按钮
- **expected**：按钮置灰 + 提示"数量不足"，服务端拒绝（无道具消耗、无状态变更）
- **notes**：注意"前端禁用" vs "服务端拦截"——前端禁用只是 UX，服务端必须二次校验

### TP-002（BOUNDARY_EXTREME）：金币为负数拦截
- **scenario**：场景 2
- **module**：`BOUNDARY_EXTREME`
- **precondition**：通过改包工具将金币置为 -1
- **test_data**：gold_balance = -1，发起购买请求
- **expected**：服务端返回错误码（如 ERR_NEGATIVE_BALANCE），金币回滚至原值，记录异常日志
- **notes**：注意"客户端负数" vs "服务端负数"——服务端必须独立校验，不信任客户端值

### TP-003（BOUNDARY_EXTREME）：等级不足功能锁定
- **scenario**：场景 3
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家等级 5，副本要求等级 30
- **test_data**：直接调用 enter_dungeon API
- **expected**：前端入口置灰 + 提示"等级不足"；服务端返回 ERR_LEVEL_INSUFFICIENT
- **notes**：注意"前端隐藏" vs "前端置灰"——保留入口给玩家看进度比隐藏更好

### TP-004（BOUNDARY_EXTREME）：活动未开启领取拦截
- **scenario**：场景 4
- **module**：`BOUNDARY_EXTREME`
- **precondition**：活动 start_time = 19:00:00，当前 18:59:59
- **test_data**：调用 claim_activity_reward API
- **expected**：返回 ERR_ACTIVITY_NOT_START，记录未授权访问日志
- **notes**：注意"配置未到时间" vs "服务时钟错误"——验证服务端时钟同步

### TP-005（BOUNDARY_EXTREME）：技能 CD 中释放拦截
- **scenario**：场景 5
- **module**：`BOUNDARY_EXTREME`
- **precondition**：技能 CD 5s，已释放 3s
- **test_data**：再次调用 cast_skill API
- **expected**：前端按钮置灰 + 倒计时显示；服务端返回 ERR_SKILL_IN_CD
- **notes**：注意"客户端冷却" vs "服务端冷却"——客户端是 UX，服务端是业务

### TP-006（BOUNDARY_EXTREME）：购买中途切后台
- **scenario**：场景 6
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家点击"购买"，拉起支付界面
- **test_data**：按 Home 键切后台，5s 后返回前台
- **expected**：订单状态正确（未支付/已取消），返回前台后界面一致，无重复扣款
- **notes**：注意"切后台" vs "切后台被杀"——后者应触发 D 前后台切换的进程恢复

### TP-007（BOUNDARY_EXTREME）：赛季已结束入口拦截
- **scenario**：场景 7
- **module**：`BOUNDARY_EXTREME`
- **precondition**：赛季 4 状态 = ENDED，玩家缓存的入口未刷新
- **test_data**：点击 S4 入口
- **expected**：入口消失/置灰 + 提示"赛季已结束"；服务端返回 ERR_SEASON_ENDED
- **notes**：注意"客户端缓存" vs "服务端真实状态"——必须有版本号/赛季号校验

### TP-008（BOUNDARY_EXTREME）：限时奖励过期清空
- **scenario**：场景 8
- **module**：`BOUNDARY_EXTREME`
- **precondition**：登录奖励 expire_at = T+24h，玩家在 T+25h 登录
- **test_data**：登录事件触发 reward_check
- **expected**：奖励已清空，无补发；玩家界面显示"奖励已过期"
- **notes**：注意"过期清空" vs "过期补发"——不同业务规则不同，按配置执行

### TP-009（BOUNDARY_EXTREME）：互斥道具同时使用
- **scenario**：场景 9
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家背包有 item_A 和 item_B（配置 mutex_group = "buff_atk"）
- **test_data**：先 use item_A，3s 内 use item_B
- **expected**：item_B 失败 + 提示"已使用同类道具"；item_A 效果持续
- **notes**：注意"互斥组" vs "独立道具"——互斥组需在配置表正确声明

### TP-010（BOUNDARY_EXTREME）：资源锁抢占 - Boss 战名额
- **scenario**：场景 10
- **module**：`BOUNDARY_EXTREME`
- **precondition**：Boss 战名额 = 1，5 个玩家同时点击"进入"
- **test_data**：5 个并发 enter_boss 请求
- **expected**：仅 1 个成功，其余返回 ERR_BOSS_FULL（带排队队列 ID）；进入后锁释放
- **notes**：注意"分布式锁" vs "进程内锁"——多服架构需 Redis 分布式锁

### TP-011（BOUNDARY_EXTREME）：数值溢出上限
- **scenario**：场景 1 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家经验值 = INT32_MAX
- **test_data**：调用 add_exp(exp=1000)
- **expected**：服务端校验 + 截断/拒绝 + 日志告警；玩家不会"经验值回绕"或清零
- **notes**：注意"溢出截断" vs "溢出回绕"——游戏一般要求拒绝 + 告警

### TP-012（BOUNDARY_EXTREME）：空数据场景
- **scenario**：场景 1 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家首次登录，背包/邮件/任务均为空
- **test_data**：打开背包/邮件/任务界面
- **expected**：显示空态占位（"暂无道具"），无崩溃、无 NPE
- **notes**：注意"空数据" vs "加载中"——必须有占位文案

### TP-013（BOUNDARY_EXTREME）：GM 高危指令二次拦截
- **scenario**：场景 3 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：GM 工具调用 drop_all_items
- **test_data**：在生产服执行 drop_all_items
- **expected**：要求二次确认（验证码/密码），操作日志留痕，灰度执行可回滚
- **notes**：注意"GM 权限" vs "GM 高危"——高危指令必须独立拦截，不信任权限

### TP-014（BOUNDARY_EXTREME）：跨服权限不足
- **scenario**：场景 3 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家在 A 服，等级 50；B 服活动要求等级 60
- **test_data**：从 A 服发起跨服 join_B_server_event
- **expected**：返回 ERR_CROSS_SERVER_LEVEL_INSUFFICIENT，本地缓存不更新
- **notes**：注意"跨服权限" vs "本服权限"——跨服场景需独立校验

### TP-015（BOUNDARY_EXTREME）：操作中途断线
- **scenario**：场景 6 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家进行副本结算
- **test_data**：结算中网络断开
- **expected**：网络恢复后重连，结算数据一致（不掉奖励、不重复扣费）
- **notes**：注意"断线" vs "网络抖动"——重连逻辑需幂等

### TP-016（BOUNDARY_EXTREME）：操作中途客户端退出
- **scenario**：场景 6 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家进行购买
- **test_data**：拉起支付后直接杀进程
- **expected**：订单状态正确（未支付/超时取消），玩家资产不变
- **notes**：注意"客户端退出" vs "客户端被杀"——需服务端有超时清理

### TP-017（BOUNDARY_EXTREME）：操作中途重启客户端
- **scenario**：场景 6 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家进行副本挑战
- **test_data**：副本中途重启客户端
- **expected**：登录后显示"副本进行中"或"副本中断"，可继续或重新开始
- **notes**：注意"强制重启" vs "断电"——服务端需记录进度

### TP-018（BOUNDARY_EXTREME）：操作被其他事件打断
- **scenario**：场景 6 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：玩家进行强化操作
- **test_data**：强化中收到系统弹窗（断线重连提示）
- **expected**：强化操作可继续或可取消，无数据错乱
- **notes**：注意"业务中断" vs "系统中断"——区分业务态/系统态

### TP-019（BOUNDARY_EXTREME）：互斥活动同时开启
- **scenario**：场景 9 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：活动 A 和活动 B 互斥（同一时间段）
- **test_data**：配置活动 A 时间 = 活动 B 时间
- **expected**：服务端启动时告警，运营无法同时开启
- **notes**：注意"互斥活动" vs "叠加活动"——配置层校验

### TP-020（BOUNDARY_EXTREME）：多操作抢占同一资源
- **scenario**：场景 10 扩展
- **module**：`BOUNDARY_EXTREME`
- **precondition**：拍卖行某商品 1 件，3 个玩家同时出价
- **test_data**：3 个并发 bid 请求
- **expected**：拍卖行按出价时间/价格排序，仅 1 个成交，无超发
- **notes**：注意"并发抢拍" vs "分布式锁"——需 Redis 分布式锁或 DB 行锁

---

## 3. 边界陷阱

### 边界 1：vs BIZ（业务正向流程）
- **混淆点**："活动开启" 看似业务 → 实际 BIZ 测"活动开启业务逻辑"（如开启时初始化数据），SPECIAL 测"活动未开启时玩家点击入口的拦截"（异常分支）
- **判定规则**：测"正常业务流（开启/进行/结束）" → 归 BIZ；测"边界异常（未开启/已过期/CD 中/越权/抢占）" → 归 SPECIAL
- **实例**：限时副本开启中玩家进入 → BIZ；未开启时玩家点击入口 → SPECIAL

### 边界 2：vs BIZ（业务流程中断）
- **混淆点**："切后台" 看似边界 → 实际 D 前后台切换测"恢复逻辑"，BIZ 测"业务状态保留"
- **判定规则**：测"切后台后状态/资源/缓存如何恢复" → 归 SPECIAL D；测"业务状态在内存中如何保留" → 归 BIZ
- **实例**：切后台 30min 后返回前台 → 资源重新加载 → 归 SPECIAL D；切回前台后显示上次未读邮件 → 归 BIZ

### 边界 3：vs SPECIAL C（弱网/限流）
- **混淆点**："CD 中释放技能" 看似弱网 → 实际弱网测"网络异常"（断线/延迟），边界测"业务规则拦截"（CD）
- **判定规则**：测"网络断开/抖动" → 归 SPECIAL C；测"业务规则拦截（CD/冷却/互斥）" → 归 SPECIAL A
- **实例**：CD 中释放技能 → 归 A；弱网下技能释放超时 → 归 C

### 边界 4：vs LINK（跨服）
- **混淆点**："跨服权限不足" 看似跨服 → 实际跨服权限同步归 LINK，跨服权限校验逻辑归 SPECIAL
- **判定规则**：测"跨服数据同步/玩家身份传递" → 归 LINK；测"跨服权限拦截/异常校验" → 归 SPECIAL
- **实例**：A 服玩家访问 B 服资源 → 归 LINK；B 服发现 A 服玩家权限不足 → 归 SPECIAL

---

## 4. 验证证据

### 视觉证据
- 道具数量 0 时的"数量不足"提示截图
- 活动未开启时入口置灰截图
- 赛季结束后入口消失截图
- 限时奖励过期后空态截图
- 互斥道具提示截图

### 日志证据
- `boundary.value.zero` 关键词：道具数量为 0 触发使用
- `boundary.value.negative` 关键词：金币为负数被拦截
- `boundary.activity.not_started` 关键词：活动未开启领取
- `boundary.skill.in_cd` 关键词：技能 CD 中释放
- `boundary.season.ended` 关键词：赛季已结束
- `boundary.resource.locked` 关键词：资源锁抢占失败

### 数据证据
- `player_bag` 表 `item_count` 字段在数量为 0 时不变
- `player_gold` 表 `balance` 字段在负数提交后未变更
- `activity_status` 表 `status` 字段与活动配置一致
- `skill_cd` 表 `last_cast_time + cd_duration > now` 时拒绝
- `boss_lock` 表 `lock_holder` 字段仅 1 个玩家

### 性能证据
- 边界值校验耗时 < 5ms
- 资源锁释放耗时 < 100ms
- 中断恢复（切后台/断线/退出）资源加载 < 2s
