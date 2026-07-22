# B. 反作弊 / 数据安全 / 参数篡改拦截

> **子类代码**：`ANTI_CHEAT`
> **归属模块**：`SPECIAL`
> **来源**：用户细化定义 §2「反作弊、数据安全、参数篡改拦截（游戏核心对抗场景补充）」
>
> **测什么**：客户端本地数据篡改、伪造协议、挂机脚本、批量建号、瞬移/无限技能、重复发包、越权协议、本地存档篡改、作弊检测与处罚联动等**游戏核心对抗场景**——服务端二次校验拦截、行为反作弊、存储安全校验、作弊触发封禁/扣回非法资源/异常数据清除。
> **不测什么**：加密算法底层（归 UTIL M）、账号安全业务（归 BIZ）、UI 验证码样式（归 UI）、支付渠道对接（归 LINK）。
> **与其他子类的差异**：B 关注"作弊/篡改的识别与拦截"——A 关注"业务边界"（数值/时间/权限）、C 关注"环境异常"（弱网/限流）；B 是对抗行为，C 是环境降级。

---

## 1. 典型场景

### 场景 1：本地修改金币数量
- 业务背景：玩家用改包工具修改客户端内存中的金币
- 涉及字段/工具：local_gold_balance、server_gold_balance
- 触发动作：购买商品时使用修改后的金币
- 验证点：服务端二次校验拦截，金额异常告警

### 场景 2：重复发包攻击
- 业务背景：玩家在 1s 内点击"领取" 100 次
- 涉及字段/工具：claim_packet、client_timestamp
- 触发动作：脚本/外挂批量发包
- 验证点：服务端去重 + 限流拦截

### 场景 3：伪造协议参数
- 业务背景：玩家构造不属于自己角色 ID 的协议
- 涉及字段/工具：player_id、token
- 触发动作：调用 cast_skill(player_id=他人的)
- 验证点：服务端 token 校验拒绝

### 场景 4：越权协议
- 业务背景：玩家调用未开放功能的协议号
- 涉及字段/工具：protocol_id、permission_flag
- 触发动作：构造未开放的协议调用
- 验证点：服务端协议白名单拦截

### 场景 5：瞬移作弊
- 业务背景：玩家通过改包将坐标改为 Boss 房间
- 涉及字段/工具：player_position、map_id
- 触发动作：移动到非法位置
- 验证点：服务端校验路径合法性

### 场景 6：无限技能
- 业务背景：玩家脚本自动释放技能，绕过 CD
- 涉及字段/工具：cast_skill、skill_cd
- 触发动作：1s 内调用 cast_skill 100 次
- 验证点：服务端 CD 校验拒绝

### 场景 7：后台挂机
- 业务背景：玩家用脚本挂机 24h 不操作
- 涉及字段/工具：heartbeat、afk_detect
- 触发动作：无输入但客户端发包活跃
- 验证点：服务端检测 AFK 行为 + 减少奖励/警告

### 场景 8：批量脚本刷资源
- 业务背景：1000 个脚本账号同时刷副本
- 涉及字段/工具：script_detect、batch_pattern
- 触发动作：识别脚本行为模式
- 验证点：批量封禁 + 资源回收

### 场景 9：多开批量建号
- 业务背景：1 台设备开 50 个客户端批量建号
- 涉及字段/工具：device_fingerprint、account_count
- 触发动作：检测多开 + 设备指纹
- 验证点：限制同设备账号数 + 告警

### 场景 10：本地存档篡改
- 业务背景：玩家修改本地存档文件
- 涉及字段/工具：local_save、save_checksum
- 触发动作：登录时上传存档
- 验证点：服务端校验 checksum 拒绝

### 场景 11：作弊触发封禁
- 业务背景：检测到玩家使用外挂
- 涉及字段/工具：cheat_log、ban_status
- 触发动作：标记 + 封禁
- 验证点：玩家无法登录 + 资产冻结

### 场景 12：作弊行为日志留痕
- 业务背景：所有反作弊检测触发均留痕
- 涉及字段/工具：cheat_log、audit_trail
- 触发动作：作弊检测
- 验证点：日志包含玩家 ID、作弊类型、时间、设备指纹

---

## 2. 种子测试点（TP 模板）

### TP-001（ANTI_CHEAT）：本地修改金币拦截
- **scenario**：场景 1
- **module**：`ANTI_CHEAT`
- **precondition**：玩家真实金币 = 1000，通过改包工具将客户端显示改为 999999
- **test_data**：客户端发起购买请求，附带 client_gold = 999999
- **expected**：服务端独立校验 DB 真实余额（1000），若不足则拒绝 + 记录异常日志 `cheat.gold_mismatch`
- **notes**：注意"客户端显示" vs "服务端真实"——服务端必须独立查 DB，不信任客户端

### TP-002（ANTI_CHEAT）：重复发包去重
- **scenario**：场景 2
- **module**：`ANTI_CHEAT`
- **precondition**：玩家持有合法 token，奖励未领取
- **test_data**：1s 内调用 claim_packet 100 次
- **expected**：第 1 次成功，2-100 次返回 ERR_ALREADY_CLAIMED；服务端按 request_id 去重
- **notes**：注意"重复发包" vs "刷接口"——后者需 C 限流配合

### TP-003（ANTI_CHEAT）：伪造协议参数拦截
- **scenario**：场景 3
- **module**：`ANTI_CHEAT`
- **precondition**：玩家 A 登录，token 绑定 A
- **test_data**：调用 cast_skill(player_id=B)
- **expected**：服务端校验 token 对应 player_id == A，否则 ERR_PLAYER_MISMATCH
- **notes**：注意"伪造身份" vs "代理登录"——代理登录需独立权限

### TP-004（ANTI_CHEAT）：越权协议白名单
- **scenario**：场景 4
- **module**：`ANTI_CHEAT`
- **precondition**：玩家未解锁"GM 后台"
- **test_data**：构造 protocol_id = GM_CMD_001
- **expected**：返回 ERR_PROTOCOL_FORBIDDEN + 记录越权访问日志
- **notes**：注意"越权" vs "协议错误"——后者可能是协议号错误

### TP-005（ANTI_CHEAT）：瞬移路径校验
- **scenario**：场景 5
- **module**：`ANTI_CHEAT`
- **precondition**：玩家在地图 A 的 (100, 100)
- **test_data**：提交 move_to(map_id=BOSS_ROOM, x=9999, y=9999)
- **expected**：服务端校验路径（从 A 到 BOSS_ROOM 无传送点），返回 ERR_INVALID_PATH
- **notes**：注意"路径" vs "地图切换"——后者需有合法传送点

### TP-006（ANTI_CHEAT）：技能 CD 服务端校验
- **scenario**：场景 6
- **module**：`ANTI_CHEAT`
- **precondition**：技能 CD 5s，已释放 1s
- **test_data**：脚本调用 cast_skill 100 次
- **expected**：第 1 次成功，2-100 次返回 ERR_SKILL_IN_CD
- **notes**：注意"脚本" vs "正常 CD"——服务端 CD 必须独立计时

### TP-007（ANTI_CHEAT）：AFK 行为检测
- **scenario**：场景 7
- **module**：`ANTI_CHEAT`
- **precondition**：玩家挂机 24h，无任何操作
- **test_data**：仅有心跳包 + 自动战斗
- **expected**：服务端检测 AFK > 12h 警告，> 24h 减少副本奖励 50%
- **notes**：注意"AFK" vs "挂机脚本"——AFK 是真实玩家不操作，脚本是无人值守

### TP-008（ANTI_CHEAT）：批量脚本封禁
- **scenario**：场景 8
- **module**：`ANTI_CHEAT`
- **precondition**：1000 个脚本账号并发刷副本
- **test_data**：1min 内 1000 个账号完成同一副本
- **expected**：服务端识别批量行为模式，封禁账号 + 回收资源 + 留痕
- **notes**：注意"批量" vs "高活跃"——区分正常高活跃玩家

### TP-009（ANTI_CHEAT）：多开设备指纹
- **scenario**：场景 9
- **module**：`ANTI_CHEAT`
- **precondition**：1 台设备尝试登录 50 个不同账号
- **test_data**：50 个并发 login 请求，device_id 相同
- **expected**：第 1-3 个成功（合理多开），4+ 拒绝 + 标记设备
- **notes**：注意"多开" vs "渠道分包"——后者需 G 渠道异常

### TP-010（ANTI_CHEAT）：本地存档 checksum 校验
- **scenario**：场景 10
- **module**：`ANTI_CHEAT`
- **precondition**：玩家修改本地 save.dat 中金币字段
- **test_data**：登录时上传存档
- **expected**：服务端校验 checksum 不匹配 → 拒绝上传 + 使用服务端存档
- **notes**：注意"存档" vs "配置"——存档是玩家数据

### TP-011（ANTI_CHEAT）：作弊封禁联动
- **scenario**：场景 11
- **module**：`ANTI_CHEAT`
- **precondition**：检测到玩家使用外挂（瞬移）
- **test_data**：自动触发 ban 流程
- **expected**：玩家无法登录 + 资产冻结 + 邮件通知 + 申诉入口
- **notes**：注意"自动封禁" vs "人工审核"——大额资产需人工审核

### TP-012（ANTI_CHEAT）：作弊日志留痕
- **scenario**：场景 12
- **module**：`ANTI_CHEAT`
- **precondition**：所有反作弊检测触发
- **test_data**：查询 cheat_log 表
- **expected**：每条日志含 player_id、cheat_type、timestamp、device_fingerprint、action_taken
- **notes**：注意"日志" vs "审计"——审计在 LOG 模块，反作弊触发由 SPECIAL B 负责

### TP-013（ANTI_CHEAT）：道具数量篡改拦截
- **scenario**：场景 1 扩展
- **module**：`ANTI_CHEAT`
- **precondition**：玩家背包 item_X 真实数量 = 1
- **test_data**：客户端修改 item_X = 9999，使用 1 个
- **expected**：服务端按真实数量 1 处理 + 告警 `cheat.item_count_mismatch`
- **notes**：注意"使用" vs "丢弃"——丢弃也需校验

### TP-014（ANTI_CHEAT）：坐标篡改拦截
- **scenario**：场景 5 扩展
- **module**：`ANTI_CHEAT`
- **precondition**：玩家在 (100, 100)
- **test_data**：提交 position = (99999, 99999)
- **expected**：服务端校验坐标在地图范围内，否则 ERR_INVALID_POSITION
- **notes**：注意"坐标" vs "地图切换"——跨地图需走传送协议

### TP-015（ANTI_CHEAT）：冷却时间篡改拦截
- **scenario**：场景 6 扩展
- **module**：`ANTI_CHEAT`
- **precondition**：技能 CD 5s
- **test_data**：客户端修改 CD = 0，立即释放技能
- **expected**：服务端按服务端计时，CD 未结束返回 ERR_SKILL_IN_CD
- **notes**：注意"客户端 CD 显示" vs "服务端 CD 计时"——客户端是 UX

### TP-016（ANTI_CHEAT）：身份令牌校验
- **scenario**：场景 3 扩展
- **module**：`ANTI_CHEAT`
- **precondition**：玩家 A 登录
- **test_data**：使用 A 的 token 但 protocol player_id 字段填 B
- **expected**：服务端校验 token.player_id == protocol.player_id，否则 ERR_PLAYER_MISMATCH
- **notes**：注意"token" vs "session"——token 是登录凭证

### TP-017（ANTI_CHEAT）：资源回收
- **scenario**：场景 11 扩展
- **module**：`ANTI_CHEAT`
- **precondition**：玩家通过作弊获得 10000 钻石
- **test_data**：检测到作弊
- **expected**：自动回收非法资源（仅扣 10000 钻石，不动合法资产）
- **notes**：注意"回收" vs "封号"——轻度过错回收资源，重度过错封号

### TP-018（ANTI_CHEAT）：异常数据清除
- **scenario**：场景 11 扩展
- **module**：`ANTI_CHEAT`
- **precondition**：玩家通过作弊刷出非法装备
- **test_data**：检测到非法装备
- **expected**：从背包中清除非法装备 + 日志记录
- **notes**：注意"清除" vs "锁定"——锁定需玩家申诉后处理

### TP-019（ANTI_CHEAT）：协议号合法性校验
- **scenario**：场景 4 扩展
- **module**：`ANTI_CHEAT`
- **precondition**：玩家收到所有客户端协议
- **test_data**：构造不存在的 protocol_id = 99999
- **expected**：返回 ERR_UNKNOWN_PROTOCOL + 不处理
- **notes**：注意"协议白名单" vs "协议黑名单"——白名单更安全

### TP-020（ANTI_CHEAT）：发包频率异常检测
- **scenario**：场景 2 扩展
- **module**：`ANTI_CHEAT`
- **precondition**：正常玩家 1s 最多发包 5 个
- **test_data**：1s 发包 100 个
- **expected**：服务端检测异常频率 + 限流 + 标记可疑
- **notes**：注意"频率" vs "重复"——频率异常需配合 C 限流

---

## 3. 边界陷阱

### 边界 1：vs UTIL M（加密安全底层）
- **混淆点**："防篡改" 看似加密 → 实际 M 测"加密算法/签名"（技术底层），B 测"反作弊识别"（业务对抗）
- **判定规则**：测"加密算法/密钥管理/协议加密" → 归 UTIL M；测"作弊检测/数据篡改识别/行为反作弊" → 归 SPECIAL B
- **实例**：协议包加密传输 → 归 M；客户端修改金币被服务端识别 → 归 B

### 边界 2：vs BIZ（业务风控）
- **混淆点**："账号风控" 看似 BIZ → 实际 BIZ 测"账号业务流程"（注册/登录/找回），B 测"游戏内作弊"（改包/外挂）
- **判定规则**：测"账号系统业务流程" → 归 BIZ；测"游戏内行为反作弊" → 归 SPECIAL B
- **实例**：账号异地登录验证 → 归 BIZ；游戏内瞬移检测 → 归 B

### 边界 3：vs SPECIAL C（限流防刷）
- **混淆点**："重复发包" 看似限流 → 实际 C 测"高频限流拦截"（流量层），B 测"重复发包去重"（业务层）
- **判定规则**：测"流量限流/雪崩保护" → 归 SPECIAL C；测"业务去重/业务幂等" → 归 SPECIAL B
- **实例**：1s 内 10000 次发包限流 → 归 C；同一业务请求 100 次去重 → 归 B

### 边界 4：vs LINK（跨服作弊）
- **混淆点**："跨服数据篡改" 看似跨服 → 实际 LINK 测"跨服数据同步业务"（正常业务），B 测"跨服数据篡改识别"（对抗场景）
- **判定规则**：测"跨服数据正常同步/时序一致性" → 归 LINK；测"跨服数据被篡改/伪造" → 归 SPECIAL B
- **实例**：跨服拍卖行出价 → 归 LINK；跨服数据被伪造 → 归 B

---

## 4. 验证证据

### 视觉证据
- 作弊检测警告弹窗（"检测到数据异常"）
- 封禁通知邮件
- 申诉入口界面

### 日志证据
- `cheat.gold_mismatch` 关键词：金币客户端/服务端不一致
- `cheat.position_invalid` 关键词：坐标非法
- `cheat.skill_cd_bypass` 关键词：技能 CD 绕过
- `cheat.protocol_forbidden` 关键词：越权协议
- `cheat.duplicate_packet` 关键词：重复发包
- `cheat.afk_detected` 关键词：AFK 检测
- `cheat.script_pattern` 关键词：脚本模式识别
- `cheat.ban_executed` 关键词：封禁执行
- `cheat.save_checksum_mismatch` 关键词：存档 checksum 不匹配

### 数据证据
- `cheat_log` 表每条记录含 `player_id` / `cheat_type` / `timestamp` / `device_fingerprint` / `action_taken`
- `player_status` 表 `ban_status` 在封禁时为 `BANNED`
- `player_bag` 表非法装备被清除
- `player_gold` 表非法金币被回收

### 性能证据
- 反作弊检测耗时 < 10ms / 请求
- 批量检测（1000 账号）< 5s
- 作弊封禁执行 < 1s
