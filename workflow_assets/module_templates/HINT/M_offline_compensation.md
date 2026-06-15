# M. 离线补偿&补发提示

> **子类代码**：`OFFLINE_COMPENSATION`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 M（v1.7 新增）
>
> **测什么**：离线奖励弹窗、服务器维护补偿、回档补发道具弹窗、邮件批量奖励提示的**展示、玩家确认、领取确认**。
> **不测什么**：离线业务逻辑（归 BIZ `A.BIZ_LOGIC`）、邮件发送协议（归 LINK `C.MULTI_CLIENT_SYNC`）、维护业务（归 BIZ `G.SCHEDULED_TASK`）。
> **与其他子类的差异**：M 是"补发/补偿"提示；D 是"系统事件"提示；K 是"状态变更"提示；M 强提示"你获得了补偿"。

---

## 1. 典型场景

### 场景 1：离线奖励弹窗
- 业务背景：离线 8 小时
- 涉及元素：离线奖励
- 触发动作：登录
- 验证点：弹窗显示离线奖励

### 场景 2：服务器维护补偿
- 业务背景：维护 4 小时
- 涉及元素：维护补偿
- 触发动作：维护结束登录
- 验证点：弹窗显示补偿

### 场景 3：回档补发道具
- 业务背景：服务器回档
- 涉及元素：回档补发
- 触发动作：登录
- 验证点：弹窗显示补发

### 场景 4：邮件批量奖励
- 业务背景：批量补偿
- 涉及元素：邮件提示
- 触发动作：登录
- 验证点：弹窗显示邮件

### 场景 5：数据异常补偿
- 业务背景：数据异常
- 涉及元素：异常补偿
- 触发动作：登录
- 验证点：弹窗显示补偿

### 场景 6：节日离线礼包
- 业务背景：节日离线
- 涉及元素：节日礼包
- 触发动作：节日后登录
- 验证点：弹窗显示节日礼包

### 场景 7：周/月签到补偿
- 业务背景：漏签
- 涉及元素：补签
- 触发动作：登录
- 验证点：弹窗显示补签

### 场景 8：活动失败补偿
- 业务背景：活动 BUG
- 涉及元素：活动补偿
- 触发动作：登录
- 验证点：弹窗显示补偿

### 场景 9：连接中断恢复
- 业务背景：连接中断
- 涉及元素：恢复提示
- 触发动作：连接恢复
- 验证点：弹窗显示恢复

### 场景 10：版本升级补偿
- 业务背景：低版本升级
- 涉及元素：升级补偿
- 触发动作：升级
- 验证点：弹窗显示补偿

---

## 2. 种子测试点（TP 模板）

### TP-001（OFFLINE_COMPENSATION）：离线奖励弹窗
- **scenario**：场景 1
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：离线 8h
- **test_data**：登录
- **expected**：弹窗显示离线奖励
- **notes**：与 B 资源飘字配合

### TP-002（OFFLINE_COMPENSATION）：离线奖励按时间计算
- **scenario**：场景 1
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：离线 8h
- **test_data**：登录
- **expected**：奖励按时间计算
- **notes**：与 BIZ 计算配合

### TP-003（OFFLINE_COMPENSATION）：服务器维护补偿
- **scenario**：场景 2
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：维护 4h
- **test_data**：维护后登录
- **expected**：弹窗显示维护补偿
- **notes**：与 LOG 维护事件配合

### TP-004（OFFLINE_COMPENSATION）：回档补发道具
- **scenario**：场景 3
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：服务器回档
- **test_data**：登录
- **expected**：弹窗显示补发道具
- **notes**：与 BIZ 数据恢复配合

### TP-005（OFFLINE_COMPENSATION）：邮件批量奖励
- **scenario**：场景 4
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：批量补偿
- **test_data**：登录
- **expected**：弹窗显示邮件
- **notes**：与 D 弹窗配合

### TP-006（OFFLINE_COMPENSATION）：数据异常补偿
- **scenario**：场景 5
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：数据异常
- **test_data**：登录
- **expected**：弹窗显示补偿
- **notes**：异常修复后

### TP-007（OFFLINE_COMPENSATION）：节日离线礼包
- **scenario**：场景 6
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：节日离线
- **test_data**：节日后登录
- **expected**：弹窗显示节日礼包
- **notes**：与 J 运营区分

### TP-008（OFFLINE_COMPENSATION）：补签弹窗
- **scenario**：场景 7
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：漏签
- **test_data**：登录
- **expected**：弹窗显示补签
- **notes**：与 BIZ 签到业务配合

### TP-009（OFFLINE_COMPENSATION）：活动 BUG 补偿
- **scenario**：场景 8
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：活动 BUG
- **test_data**：登录
- **expected**：弹窗显示补偿
- **notes**：与 LOG BUG 报告配合

### TP-010（OFFLINE_COMPENSATION）：连接中断恢复
- **scenario**：场景 9
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：连接中断
- **test_data**：连接恢复
- **expected**：弹窗显示恢复
- **notes**：与 AUX 网络检测配合

### TP-011（OFFLINE_COMPENSATION）：版本升级补偿
- **scenario**：场景 10
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：低版本升级
- **test_data**：升级
- **expected**：弹窗显示补偿
- **notes**：与 LINK 升级配合

### TP-012（OFFLINE_COMPENSATION）：补偿一键领取
- **scenario**：场景 1
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：补偿弹窗
- **test_data**：点击领取
- **expected**：所有道具到账
- **notes**：与 B 飘字配合

### TP-013（OFFLINE_COMPENSATION）：补偿过期
- **scenario**：场景 1
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：补偿有有效期
- **test_data**：超时
- **expected**：补偿过期
- **notes**：与 G 限时提醒配合

### TP-014（OFFLINE_COMPENSATION）：多补偿合并
- **scenario**：场景 1+2
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：多个补偿
- **test_data**：登录
- **expected**：合并弹窗
- **notes**：合并策略

### TP-015（OFFLINE_COMPENSATION）：补偿埋点
- **scenario**：场景 1
- **module**：`OFFLINE_COMPENSATION`
- **precondition**：补偿触发
- **test_data**：观察日志
- **expected**：上报 `compensation.show/claim` 事件
- **notes**：与 LOG 配合

---

## 3. 边界陷阱

### 边界 1：vs D. 模态弹窗
- **混淆点**：「弹窗」——M 测补偿、D 测系统
- **判定规则**：测"补偿/补发弹窗" → M；测"系统事件弹窗" → D
- **instance**：离线奖励弹窗 → M；登录失败弹窗 → D

### 边界 2：vs J. 运营推送
- **混淆点**：「奖励"弹窗"」——M 测补偿、J 测运营
- **判定规则**：测"补偿/补发" → M；测"运营福利" → J
- **instance**：维护补偿弹窗 → M；节日福利弹窗 → J

### 边界 3：vs BIZ `A.BIZ_LOGIC`
- **混淆点**：「离线"奖励"」——M 测弹窗、BIZ 测业务
- **判定规则**：测"奖励弹窗显示" → M；测"奖励计算业务" → BIZ
- **instance**：离线奖励弹窗 → M；离线奖励计算业务 → BIZ

### 边界 4：vs LINK `C.MULTI_CLIENT_SYNC`
- **混淆点**：「跨端"补偿"」——M 测弹窗、LINK 测同步
- **判定规则**：测"补偿弹窗显示" → M；测"跨端数据同步" → LINK
- **instance**：回档补发弹窗 → M；跨端数据同步 → LINK

### 边界 5：vs L. 风控合规
- **混淆点**：「提示"弹窗"」——M 测补偿、L 测合规
- **判定规则**：测"补偿/补发弹窗" → M；测"合规弹窗" → L
- **instance**：维护补偿弹窗 → M；防沉迷弹窗 → L

---

## 4. 验证证据

### 视觉证据
- 各种补偿弹窗截图（离线/维护/回档/批量）
- 一键领取截图
- 多补偿合并截图

### 日志证据
- `compensation.show` 事件（参数：type/source/amount）
- `compensation.claim` 事件
- `offline_reward.calc` 事件

### 数据证据
- 玩家补偿记录
- 维护记录
- 回档记录

### 性能证据
- 补偿弹窗弹出 < 200ms
- 一键领取 < 500ms
