# P. HINT 游戏项目额外专属（HINT 游戏专项）

> **非测试类型**——本文件是**仅游戏项目**的 HINT 测试点补充。
> 非游戏项目（PC 后台、移动端 App、Web 工具）**忽略**本文件。
>
> **来源**：`.cursor/MODULES.md` §4.11 P

---

## 1. 战斗场景 HINT 强化

### 场景
- 业务背景：游戏战斗
- 涉及元素：战斗飘字、伤害数字、BUFF 飘字、状态变更弹窗
- 验证点：战斗实时性、飘字队列、抗压性能

### 种子 TP

#### TP-001（P-战斗）：战斗中 100 飘字抗压
- **module**：`CURRENCY_FLOAT`
- **precondition**：大型 AOE 战斗
- **test_data**：命中 100 个目标
- **expected**：100 个飘字队列渲染、FPS ≥ 25
- **notes**：与 B/C 配合

#### TP-002（P-战斗）：DOT 持续伤害飘字无卡顿
- **module**：`CURRENCY_FLOAT`
- **precondition**：中毒 10 秒
- **test_data**：每 1s 跳伤害
- **expected**：10 个飘字流畅显示
- **notes**：性能边界

#### TP-003（P-战斗）：PVP 战斗飘字区分
- **module**：`CURRENCY_FLOAT`
- **precondition**：PvP 战斗
- **test_data**：玩家对玩家
- **expected**：飘字颜色按设计区分（友方/敌方）
- **notes**：PvP 视觉

#### TP-004（P-战斗）：战斗内升级弹窗
- **module**：`STATE_CHANGE_DIALOG`
- **precondition**：战斗中升级
- **test_data**：经验满
- **expected**：弹窗显示、不阻塞战斗过久
- **notes**：与 K 配合

#### TP-005（P-战斗）：战斗内 buff 弹窗
- **module**：`CURRENCY_FLOAT`
- **precondition**：战斗中 buff
- **test_data**：获得 buff
- **expected**：飘字显示
- **notes**：与 C 配合

---

## 2. 社交场景 HINT 强化

### 场景
- 业务背景：游戏社交
- 涉及元素：私聊、公会、好友申请、组队邀请
- 验证点：社交提示与战斗兼容、跨服社交

### 种子 TP

#### TP-006（P-社交）：战斗中组队邀请
- **module**：`SOCIAL_PROMPT`
- **precondition**：战斗中
- **test_data**：被邀请组队
- **expected**：弹窗显示、不立即打断战斗
- **notes**：可配置

#### TP-007（P-社交）：跨服好友消息
- **module**：`SOCIAL_PROMPT`
- **precondition**：跨服好友
- **test_data**：跨服消息
- **expected**：弹窗显示跨服标识
- **notes**：与 I 配合

#### TP-008（P-社交）：公会战邀请
- **module**：`SOCIAL_PROMPT`
- **precondition**：公会战期间
- **test_data**：公会战邀请
- **expected**：弹窗强调
- **notes**：特殊活动

#### TP-009（P-社交）：好友赠送回执
- **module**：`SOCIAL_PROMPT`
- **precondition**：好友赠送
- **test_data**：收到赠送
- **expected**：回执弹窗
- **notes**：与 I 配合

#### TP-010（P-社交）：黑名单玩家消息
- **module**：`SOCIAL_PROMPT`
- **precondition**：玩家被拉黑
- **test_data**：黑名单玩家发消息
- **expected**：不显示消息提示
- **notes**：屏蔽逻辑

---

## 3. 运营场景 HINT 强化

### 场景
- 业务背景：游戏运营活动
- 涉及元素：节日活动、限时折扣、登录福利
- 验证点：运营推送、玩家偏好

### 种子 TP

#### TP-011（P-运营）：节日活动运营弹窗
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：节日首次登录
- **test_data**：登录
- **expected**：弹窗显示节日活动
- **notes**：与 J 配合

#### TP-012（P-运营）：玩家偏好设置
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：玩家设置"不再推送"
- **test_data**：触发
- **expected**：不显示
- **notes**：持久化偏好

#### TP-013（P-运营）：运营弹窗频次限制
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：每日弹窗上限 1 次
- **test_data**：关闭后再触发
- **expected**：当日不再弹
- **notes**：防骚扰

#### TP-014（P-运营）：运营弹窗定时推送
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：定时推送
- **test_data**：到达推送时间
- **expected**：弹窗按时间推送
- **notes**：定时器

#### TP-015（P-运营）：充值推送
- **module**：`OPS_PUSH_PROMPT`
- **precondition**：充值优惠
- **test_data**：进入商城
- **expected**：弹窗显示优惠
- **notes**：与 LINK 配合

---

## 4. 合规场景 HINT 强化

### 场景
- 业务背景：合规要求
- 涉及元素：防沉迷、付费限额、实名、宵禁
- 验证点：合规强制、不可绕过

### 种子 TP

#### TP-016（P-合规）：未成年防沉迷强制
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：未成年 3h
- **test_data**：3h 整
- **expected**：强制下线
- **notes**：与 L 配合

#### TP-017（P-合规）：未成年付费限额严格
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：未成年本月付费已达
- **test_data**：再次付费
- **expected**：弹窗限制
- **notes**：合规

#### TP-018（P-合规）：宵禁不可玩
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：宵禁时间
- **test_data**：登录
- **expected**：不可游戏
- **notes**：强制

#### TP-019（P-合规）：实名弹窗强制
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：未实名
- **test_data**：进入游戏
- **expected**：不可关闭
- **notes**：合规

#### TP-020（P-合规）：合规文案规范
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：防沉迷
- **test_data**：观察文案
- **expected**：按法规
- **notes**：合规

---

## 5. 补偿&回滚场景 HINT 强化

### 场景
- 业务背景：服务器异常
- 涉及元素：维护补偿、回档补发、BUG 补偿
- 验证点：补偿及时、回档恢复

### 种子 TP

#### TP-021（P-补偿）：维护后补偿
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：维护 4h
- **test_data**：维护后登录
- **expected**：弹窗显示补偿
- **notes**：与 M 配合

#### TP-022（P-补偿）：回档补发
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：服务器回档
- **test_data**：登录
- **expected**：弹窗显示补发
- **notes**：与 M 配合

#### TP-023（P-补偿）：BUG 补偿
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：活动 BUG
- **test_data**：登录
- **expected**：弹窗显示补偿
- **notes**：与 M 配合

#### TP-024（P-补偿）：数据回滚
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：数据回滚
- **test_data**：登录
- **expected**：弹窗显示回滚
- **notes**：与 M 配合

#### TP-025（P-补偿）：补偿一键领取
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：补偿弹窗
- **test_data**：点击领取
- **expected**：一键到账
- **notes**：与 M 配合

---

## 6. 边界陷阱

### 边界 1：vs BIZ
- **混淆点**：「升级"游戏机制"」——HINT 测提示、BIZ 测机制
- **判定规则**：测"游戏内弹窗" → HINT；测"游戏机制" → BIZ
- **实例**：升级弹窗 → HINT K；升级计算 → BIZ

### 边界 2：vs UI
- **混淆点**：「战斗"UI"」——HINT 测飘字、UI 测血条
- **判定规则**：测"飘字内容" → HINT；测"血条常驻" → UI
- **实例**：暴击飘字"9999" → HINT C；血条常驻 → UI

### 边界 3：vs LOG
- **混淆点**：「HINT"事件"」——HINT 测提示、LOG 测埋点
- **判定规则**：测"HINT 弹窗显示" → HINT；测"HINT 触发事件上报" → LOG
- **实例**：升级弹窗 → HINT K；`player.level_up` 事件 → LOG

### 边界 4：vs SPECIAL
- **混淆点**：「游戏"反作弊"」——HINT 测提示、SPECIAL 测检测
- **判定规则**：测"反作弊弹窗" → HINT L；测"反作弊检测" → SPECIAL
- **实例**：反作弊弹窗 → HINT L；反作弊检测 → SPECIAL

### 边界 5：vs UTIL
- **混淆点**：「游戏"通知"」——HINT 测提示、UTIL 测框架
- **判定规则**：测"HINT 内容" → HINT；测"通知底层框架" → UTIL
- **实例**：飘字"+100" → HINT B；通知队列框架 → UTIL

---

## 7. 验证证据

### 视觉证据
- 战斗飘字序列截图
- 跨服好友消息截图
- 防沉迷强制弹窗截图
- 维护补偿弹窗截图

### 日志证据
- `combat.float_text` 事件
- `social.friend_request` 事件
- `compliance.anti_addiction` 事件
- `compensation.show` 事件

### 数据证据
- 战斗日志表
- 社交关系表
- 合规记录表
- 补偿记录表

### 性能证据
- 战斗 100 飘字 FPS ≥ 25
- 跨服消息延迟 < 500ms
- 合规弹窗强制 < 100ms
- 补偿弹窗 < 200ms
