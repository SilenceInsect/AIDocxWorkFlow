# G. GM 工具

> **子类代码**：`GM_TOOL`
> **归属模块**：`AUX`
> **来源**：用户细化定义 §7「GM 工具（后台/客户端 GM）」
>
> **测什么**：GM 指令、后台运营 GM、权限管控、参数校验、审计日志。
> **不测什么**：业务逻辑（归 BIZ）、配置（归 CONFIG）、UI（归 UI）、网络（归 B）。
> **与其他子类的差异**：G 关注"运营工具"——L 关注"运营后台"，G 强调"指令 + 权限"。

---

## 1. 典型场景

### 场景 1：GM 指令 - 发道具
- 业务背景：客服补发
- 涉及指令：`gm_add_item player_id item_id count`
- 触发动作：GM 玩家使用指令
- 验证点：玩家收到道具

### 场景 2：GM 指令 - 改等级
- 业务背景：测试
- 涉及指令：`gm_set_level player_id level`
- 触发动作：GM 玩家使用
- 验证点：玩家等级变化

### 场景 3：GM 指令 - 清 CD
- 业务背景：测试
- 涉及指令：`gm_clear_cd player_id skill_id`
- 触发动作：GM 玩家使用
- 验证点：玩家技能 CD 清除

### 场景 4：GM 指令 - 开关活动
- 业务背景：紧急开关活动
- 涉及指令：`gm_toggle_activity activity_id on/off`
- 触发动作：GM 玩家使用
- 验证点：活动开关

### 场景 5：后台批量发奖
- 业务背景：补偿活动
- 涉及工具：后台运营 GM
- 触发动作：选择 1000 个玩家 → 发奖
- 验证点：1000 个玩家收到奖励

### 场景 6：全服公告
- 业务背景：维护通知
- 涉及工具：后台 GM
- 触发动作：发全服公告
- 验证点：全服玩家收到

### 场景 7：玩家查询
- 业务背景：客服查询
- 涉及工具：后台 GM
- 触发动作：输入玩家 ID 查询
- 验证点：返回玩家信息

### 场景 8：封号禁言
- 业务背景：违规处理
- 涉及工具：后台 GM
- 触发动作：封禁玩家 7 天
- 验证点：玩家无法登录

### 场景 9：补发补偿
- 业务背景：bug 补偿
- 涉及工具：后台 GM
- 触发动作：批量补发道具
- 验证点：玩家收到补偿

### 场景 10：GM 权限分级
- 业务背景：不同级别 GM
- 涉及配置：权限表
- 触发动作：低级 GM 尝试高危指令
- 验证点：拒绝

### 场景 11：操作日志
- 业务背景：GM 操作审计
- 涉及工具：日志
- 触发动作：GM 发指令
- 验证点：审计日志记录

### 场景 12：高危指令二次确认
- 业务背景：删号等高危操作
- 触发动作：GM 用 `gm_delete_player`
- 验证点：二次确认

### 场景 13：操作回滚
- 业务背景：误操作
- 触发动作：GM 误发 10000 钻石
- 验证点：可回滚

### 场景 14：非法 ID 拦截
- 业务背景：防误操作
- 触发动作：GM 输入不存在的 player_id
- 验证点：拒绝、不执行

### 场景 15：超上限发放拦截
- 业务背景：防误操作
- 触发动作：GM 发 999999999 钻石
- 验证点：拒绝、提示上限

---

## 2. 种子测试点（TP 模板）

### TP-001（GM_TOOL）：发道具指令
- **scenario**：场景 1
- **module**：`GM_TOOL`
- **precondition**：GM 玩家
- **test_data**：`gm_add_item player_id=1 item_id=100 count=10`
- **expected**：玩家 1 收到 10 个道具 100
- **notes**：注意"在线"vs"离线"玩家

### TP-002（GM_TOOL）：改等级指令
- **scenario**：场景 2
- **module**：`GM_TOOL`
- **precondition**：玩家 1 当前等级 1
- **test_data**：`gm_set_level player_id=1 level=50`
- **expected**：玩家 1 等级 50
- **notes**：注意"等级上限"vs"任意等级"

### TP-003（GM_TOOL）：清 CD 指令
- **scenario**：场景 3
- **module**：`GM_TOOL`
- **precondition**：玩家技能有 CD
- **test_data**：`gm_clear_cd player_id=1 skill_id=100`
- **expected**：技能 CD 清除
- **notes**：注意"全部技能"vs"单技能"

### TP-004（GM_TOOL）：开关活动
- **scenario**：场景 4
- **module**：`GM_TOOL`
- **precondition**：活动存在
- **test_data**：`gm_toggle_activity 100 off`
- **expected**：活动关闭
- **notes**：注意"立刻"vs"延迟"

### TP-005（GM_TOOL）：批量发奖
- **scenario**：场景 5
- **module**：`GM_TOOL`
- **precondition**：1000 个玩家
- **test_data**：后台选 1000 个玩家 → 发 100 钻石
- **expected**：1000 个玩家各收到 100 钻石
- **notes**：注意"批量上限"（如 10000/次）

### TP-006（GM_TOOL）：批量发奖进度
- **scenario**：场景 5
- **module**：`GM_TOOL`
- **precondition**：1000 个玩家
- **test_data**：观察后台进度
- **expected**：进度条 0% → 100%、耗时 < 5min
- **notes**：注意"异步"vs"同步"

### TP-007（GM_TOOL）：全服公告
- **scenario**：场景 6
- **module**：`GM_TOOL`
- **precondition**：无
- **test_data**：发全服公告 "维护通知"
- **expected**：全服玩家收到
- **notes**：注意"在线"vs"全服"（含离线）

### TP-008（GM_TOOL）：玩家查询
- **scenario**：场景 7
- **module**：`GM_TOOL`
- **precondition**：无
- **test_data**：输入玩家 ID=1
- **expected**：返回玩家信息（等级、VIP、最近登录）
- **notes**：注意"敏感信息"脱敏

### TP-009（GM_TOOL）：封号
- **scenario**：场景 8
- **module**：`GM_TOOL`
- **precondition**：玩家 1 正常
- **test_data**：`gm_ban player_id=1 days=7`
- **expected**：玩家 1 7 天无法登录
- **notes**：注意"封号"vs"禁言"

### TP-010（GM_TOOL）：补发补偿
- **scenario**：场景 9
- **module**：`GM_TOOL`
- **precondition**：bug 影响 1000 玩家
- **test_data**：批量补发 100 钻石
- **expected**：1000 玩家各收到 100 钻石
- **notes**：注意"邮件"vs"直接发"

### TP-011（GM_TOOL）：权限分级 - 低级 GM 高危指令
- **scenario**：场景 10
- **module**：`GM_TOOL`
- **precondition**：低级 GM 玩家
- **test_data**：尝试 `gm_delete_player`
- **expected**：拒绝、提示"无权限"
- **notes**：注意"权限表"配置（归 CONFIG）

### TP-012（GM_TOOL）：权限分级 - 高级 GM 正常
- **scenario**：场景 10
- **module**：`GM_TOOL`
- **precondition**：高级 GM 玩家
- **test_data**：`gm_delete_player player_id=2`
- **expected**：执行（需二次确认）
- **notes**：注意"权限"vs"操作"

### TP-013（GM_TOOL）：操作日志记录
- **scenario**：场景 11
- **module**：`GM_TOOL`
- **precondition**：GM 发指令
- **test_data**：GM A 用 `gm_add_item`
- **expected**：审计日志含 GM A、操作、时间、内容
- **notes**：注意"审计"vs"匿名"

### TP-014（GM_TOOL）：高危指令二次确认
- **scenario**：场景 12
- **module**：`GM_TOOL`
- **precondition**：GM 玩家
- **test_data**：`gm_delete_player player_id=2`
- **expected**：弹窗"确认删除？"
- **notes**：注意"二次确认"vs"立即执行"

### TP-015（GM_TOOL）：操作回滚
- **scenario**：场景 13
- **module**：`GM_TOOL`
- **precondition**：GM 误发 10000 钻石
- **test_data**：GM 撤回
- **expected**：10000 钻石扣回
- **notes**：注意"回滚"vs"补扣"

### TP-016（GM_TOOL）：非法 ID 拦截
- **scenario**：场景 14
- **module**：`GM_TOOL`
- **precondition**：无
- **test_data**：`gm_add_item player_id=999999 count=10`
- **expected**：拒绝、提示"玩家不存在"
- **notes**：注意"非法 ID"vs"已删除"

### TP-017（GM_TOOL）：超上限发放拦截
- **scenario**：场景 15
- **module**：`GM_TOOL`
- **precondition**：钻石上限 999999
- **test_data**：`gm_add_diamond player_id=1 count=999999999`
- **expected**：拒绝、提示"超出上限"
- **notes**：注意"业务上限"vs"int 上限"

### TP-018（GM_TOOL）：批量操作容错
- **scenario**：场景 5
- **module**：`GM_TOOL`
- **precondition**：1000 个玩家，其中 10 个已删
- **test_data**：批量发奖
- **expected**：990 个玩家成功、10 个失败、报告失败原因
- **notes**：注意"部分失败"vs"全部回滚"

---

## 3. 边界陷阱

### 边界 1：vs BIZ
- **混淆点**：「GM"发"道具」——G 测 GM 工具、BIZ 测业务
- **判定规则**：测"GM 指令和权限" → G；测"道具发放业务" → BIZ
- **实例**：`gm_add_item` 指令 → G；发放道具业务 → BIZ

### 边界 2：vs L. 运营辅助
- **混淆点**：「运营"工具"」——G 测 GM 工具、L 测运营
- **判定规则**：测"GM 指令（发道具/改等级）" → G；测"公告/邮件编辑器" → L
- **实例**：`gm_add_item` → G；发全服公告 → L

### 边界 3：vs CONFIG
- **混淆点**：「GM"权限配置"」——G 测 GM、CONFIG 测配置
- **判定规则**：测"GM 指令/权限" → G；测"权限表配置" → CONFIG
- **实例**：低级 GM 高危指令拒绝 → G；权限表配置 → CONFIG

### 边界 4：vs LOG
- **混淆点**：「GM"日志"」——G 测 GM 工具、LOG 测埋点
- **判定规则**：测"GM 指令本身" → G；测"GM 操作审计上报" → LOG
- **实例**：GM 发指令 → G；上报 `gm_operation` 事件 → LOG

---

## 4. 验证证据

### 视觉证据
- GM 指令执行截图
- 二次确认弹窗
- 玩家收到道具截图

### 日志证据
- GM 指令日志
- 操作审计日志
- 权限拒绝日志

### 数据证据
- DB 中玩家道具变化
- 审计日志表
- 批量发奖报告

### 性能证据
- 单条 GM 指令 < 1s
- 批量 1000 玩家 < 5min
