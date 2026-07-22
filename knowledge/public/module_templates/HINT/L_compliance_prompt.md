# L. 风控合规提示

> **子类代码**：`COMPLIANCE_PROMPT`
> **归属模块**：`HINT`
> **来源**：`.cursor/MODULES.md` §4.11 L（v1.7 新增）
>
> **测什么**：防沉迷时长预警弹窗、未成年付费限额提醒、实名认证缺失提示、敏感词拦截提示的**展示、文案分级、强制行为**。
> **不测什么**：合规校验逻辑（归 SPECIAL `E.SERVER_HA_RISK` / `H.COMPLIANCE_RISK`）、防沉迷规则（归 BIZ `A.BIZ_LOGIC`）、实名认证 SDK（归 LINK `D.EXTERNAL_THIRD_PARTY`）。
> **与其他子类的差异**：L 是"合规相关"的提示；K 是"状态变更"提示；D 是"通用系统"弹窗；L 必须严格按法规处理。

---

## 1. 典型场景

### 场景 1：防沉迷时长预警
- 业务背景：未成年游戏 2.5h
- 涉及元素：预警弹窗
- 触发动作：累计 2.5h
- 验证点：弹窗"再玩 30 分钟强制下线"

### 场景 2：未成年付费限额
- 业务背景：未成年付费
- 涉及元素：限额提示
- 触发动作：付费超限
- 验证点：弹窗"已达本月限额"

### 场景 3：实名认证缺失
- 业务背景：未实名
- 涉及元素：实名弹窗
- 触发动作：进入游戏
- 验证点：弹窗"请先实名"

### 场景 4：敏感词拦截
- 业务背景：聊天敏感词
- 涉及元素：拦截提示
- 触发动作：发送敏感词
- 验证点：Toast"内容包含敏感词"

### 场景 5：防沉迷强制下线
- 业务背景：未成年 3h
- 涉及元素：强制下线
- 触发动作：3h 整
- 验证点：弹窗强制退出

### 场景 6：游戏宵禁
- 业务背景：夜间 22:00-8:00
- 涉及元素：宵禁提示
- 触发动作：进入宵禁时间
- 验证点：弹窗"宵禁中"

### 场景 7：充值退款提示
- 业务背景：家长申请退款
- 涉及元素：退款提示
- 触发动作：退款
- 验证点：弹窗"退款成功"

### 场景 8：违规警告
- 业务背景：检测到违规
- 涉及元素：警告弹窗
- 触发动作：违规
- 验证点：弹窗警告

### 场景 9：IP 属地限制
- 业务背景：IP 限制
- 涉及元素：IP 提示
- 触发动作：受限地区
- 验证点：弹窗"该地区不可用"

### 场景 10：版本合规
- 业务背景：版本合规
- 涉及元素：合规提示
- 触发动作：低版本
- 验证点：弹窗"请更新"

---

## 2. 种子测试点（TP 模板）

### TP-001（COMPLIANCE_PROMPT）：防沉迷时长预警
- **scenario**：场景 1
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：未成年游戏 2.5h
- **test_data**：继续游戏
- **expected**：弹窗"再玩 30 分钟强制下线"
- **notes**：与 D 强制弹窗配合

### TP-002（COMPLIANCE_PROMPT）：未成年付费限额
- **scenario**：场景 2
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：未成年本月付费已达 200 元
- **test_data**：再次付费
- **expected**：弹窗"已达本月限额"
- **notes**：与 LINK 支付配合

### TP-003（COMPLIANCE_PROMPT）：实名认证缺失弹窗
- **scenario**：场景 3
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：未实名
- **test_data**：进入游戏
- **expected**：弹窗"请先实名认证"
- **notes**：与 LINK 实名 SDK 配合

### TP-004（COMPLIANCE_PROMPT）：实名弹窗强制
- **scenario**：场景 3
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：未实名
- **test_data**：观察
- **expected**：弹窗不可关闭（强制）
- **notes**：合规要求

### TP-005（COMPLIANCE_PROMPT）：敏感词拦截 Toast
- **scenario**：场景 4
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：发送敏感词
- **test_data**：输入敏感词
- **expected**：Toast"内容包含敏感词"
- **notes**：与 E Toast 配合

### TP-006（COMPLIANCE_PROMPT）：防沉迷强制下线
- **scenario**：场景 5
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：未成年累计 3h
- **test_data**：3h 整
- **expected**：弹窗强制退出
- **notes**：与 D 配合

### TP-007（COMPLIANCE_PROMPT）：游戏宵禁
- **scenario**：场景 6
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：夜间 22:00
- **test_data**：登录
- **expected**：弹窗"宵禁中、不可游戏"
- **notes**：未成年专属

### TP-008（COMPLIANCE_PROMPT）：充值退款提示
- **scenario**：场景 7
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：家长退款
- **test_data**：退款回调
- **expected**：弹窗"退款成功"
- **notes**：与 BIZ 退款业务配合

### TP-009（COMPLIANCE_PROMPT）：违规警告弹窗
- **scenario**：场景 8
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：检测到违规
- **test_data**：违规行为
- **expected**：弹窗警告
- **notes**：与 SPECIAL 反作弊配合

### TP-010（COMPLIANCE_PROMPT）：IP 属地限制
- **scenario**：场景 9
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：受限地区
- **test_data**：登录
- **expected**：弹窗"该地区不可用"
- **notes**：合规要求

### TP-011（COMPLIANCE_PROMPT）：版本合规更新
- **scenario**：场景 10
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：低版本
- **test_data**：登录
- **expected**：弹窗"请更新到最新版本"
- **notes**：与 D 版本过低区分

### TP-012（COMPLIANCE_PROMPT）：合规弹窗文案规范
- **scenario**：场景 1
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：防沉迷
- **test_data**：观察文案
- **expected**：文案符合法规要求
- **notes**：文案严格按法规

### TP-013（COMPLIANCE_PROMPT）：合规弹窗不可截图（按设计）
- **scenario**：场景 1
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：防沉迷
- **test_data**：尝试截图
- **expected**：按设计（防截屏/不防）
- **notes**：合规要求

### TP-014（COMPLIANCE_PROMPT）：合规埋点
- **scenario**：场景 1
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：防沉迷触发
- **test_data**：观察日志
- **expected**：上报 `compliance.anti_addiction` 事件
- **notes**：与 LOG 配合

### TP-015（COMPLIANCE_PROMPT）：合规弹窗无跳过按钮
- **scenario**：场景 1
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：合规弹窗
- **test_data**：观察
- **expected**：无跳过按钮
- **notes**：合规强制

### TP-016（COMPLIANCE_PROMPT）：未成年充值确认
- **scenario**：场景 2
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：未成年付费
- **test_data**：付费
- **expected**：弹窗"未成年需家长同意"
- **notes**：合规

### TP-017（COMPLIANCE_PROMPT）：实名弹窗填写校验
- **scenario**：场景 3
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：实名弹窗
- **test_data**：输入身份证
- **expected**：校验身份证格式
- **notes**：与 BIZ 校验配合

### TP-018（COMPLIANCE_PROMPT）：退款后道具回收提示
- **scenario**：场景 7
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：退款
- **test_data**：退款成功
- **expected**：弹窗"道具将回收"
- **notes**：与 BIZ 配合

### TP-019（COMPLIANCE_PROMPT）：多语言合规文案
- **scenario**：场景 1
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：切到英语
- **test_data**：防沉迷
- **expected**：英文合规文案
- **notes**：i18n 合规要求

### TP-020（COMPLIANCE_PROMPT）：合规弹窗顺序
- **scenario**：场景 1
- **module**：`COMPLIANCE_PROMPT`
- **precondition**：多个合规事件
- **test_data**：触发
- **expected**：按优先级弹窗
- **notes**：优先级

---

## 3. 边界陷阱

### 边界 1：vs D. 模态弹窗
- **混淆点**：「弹窗」——L 测合规、D 测系统
- **判定规则**：测"合规事件触发的弹窗" → L；测"系统事件弹窗" → D
- **instance**：防沉迷弹窗 → L；登录失败弹窗 → D

### 边界 2：vs SPECIAL `H.COMPLIANCE_RISK`
- **混淆点**：「合规"提示"」——L 测弹窗内容、SPECIAL 测合规检测
- **判定规则**：测"合规弹窗显示" → L；测"合规检测逻辑" → SPECIAL
- **instance**：防沉迷弹窗文案 → L；未成年 3h 检测 → SPECIAL

### 边界 3：vs BIZ `A.BIZ_LOGIC`
- **混淆点**：「未成年"规则"」——L 测弹窗、BIZ 测业务
- **判定规则**：测"弹窗文案" → L；测"未成年检查" → BIZ
- **instance**：未成年付费弹窗 → L；未成年检查业务 → BIZ

### 边界 4：vs E. Toast
- **混淆点**：「敏感词"提示"」——L 测内容、E 测 Toast 容器
- **判定规则**：测"敏感词拦截文案" → L；测"Toast 容器样式" → E
- **instance**：敏感词 Toast"内容违规" → L；Toast 弹出样式 → E

### 边界 5：vs LINK `D.EXTERNAL_THIRD_PARTY`
- **混淆点**：「实名"SDK"」——L 测提示、LINK 测 SDK
- **判定规则**：测"实名弹窗" → L；测"实名 SDK 调用" → LINK
- **instance**：实名弹窗 → L；实名 SDK 接入 → LINK

---

## 4. 验证证据

### 视觉证据
- 各种合规弹窗截图（防沉迷/付费/实名/敏感词）
- 合规文案截图（按法规）
- 强制弹窗截图

### 日志证据
- `compliance.show` 事件（参数：type/reason）
- `compliance.force_exit` 事件
- `anti_addiction.trigger` 事件

### 数据证据
- 防沉迷时长记录
- 未成年付费记录
- 实名认证状态

### 性能证据
- 合规弹窗弹出 < 100ms（强制）
- 强制退出无延迟
