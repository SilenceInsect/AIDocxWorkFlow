# H. 风控 & 合规特殊约束

> **子类代码**：`COMPLIANCE_RISK`
> **归属模块**：`SPECIAL`
> **来源**：用户细化定义 §8「风控 & 合规特殊约束」（原定义缺失补充）
>
> **测什么**：**防沉迷超时强制下线**（未成年累计游戏时长 / 宵禁 / 强制休息）、**未成年付费限额拦截**（单笔/月累计）、**敏感词拦截**（聊天/昵称/留言）、**实名认证缺失限制功能**（未实名不可充值）、**地区合规功能屏蔽**（不同国家/地区屏蔽功能，如 GDPR 区域屏蔽 PII、版号限制功能、跨境支付限制）。
> **不测什么**：账号注册/登录业务流程（归 BIZ）、UI 验证码样式（归 UI）、业务反作弊（归 SPECIAL B）。
> **与其他子类的差异**：H 关注"法规合规"——A/B/E 关注"业务/对抗/HA"；H 是法规层，B 是对抗层，E 是 HA 层。

---

## 1. 典型场景

### 场景 1：未成年游戏时长超时
- 业务背景：未成年玩家累计游戏 1.5h（超 1h 限制）
- 涉及字段/工具：minor_play_time、play_limit
- 触发动作：玩家游戏 1.5h
- 验证点：强制下线 + 提示"已达游戏时长上限"

### 场景 2：未成年宵禁
- 业务背景：22:00 - 8:00 禁止未成年游戏
- 涉及字段/工具：minor_curfew、curfew_check
- 触发动作：未成年玩家 22:01 尝试登录
- 验证点：拒绝登录 + 提示"宵禁时间"

### 场景 3：未成年付费单笔限额
- 业务背景：未成年单笔付费 ≤ 50 元
- 涉及字段/工具：minor_pay_limit、pay_validate
- 触发动作：未成年尝试充值 100 元
- 验证点：拒绝 + 提示"超出单笔限额"

### 场景 4：未成年付费月累计限额
- 业务背景：未成年月累计付费 ≤ 200 元
- 涉及字段/工具：minor_month_pay、monthly_sum
- 触发动作：未成年本月已充值 180 元，尝试再充 50 元
- 验证点：拒绝 + 提示"超出月累计限额"

### 场景 5：聊天敏感词拦截
- 业务背景：玩家发送含敏感词的消息
- 涉及字段/工具：chat_text、sensitive_filter
- 触发动作：玩家发送"违禁词1"
- 验证点：消息拦截 + 提示"消息含敏感内容"

### 场景 6：昵称敏感词拦截
- 业务背景：玩家创建昵称含敏感词
- 涉及字段/工具：nickname、sensitive_filter
- 触发动作：玩家创建昵称"敏感昵称"
- 验证点：拒绝 + 提示"昵称不合规"

### 场景 7：未实名认证限制
- 业务背景：玩家未实名
- 涉及字段/工具：real_name、feature_restrict
- 触发动作：未实名玩家尝试充值
- 验证点：拒绝 + 引导实名认证

### 场景 8：未实名限制功能
- 业务背景：未实名不可进入聊天
- 涉及字段/工具：real_name、chat_restrict
- 触发动作：未实名玩家进入聊天
- 验证点：聊天功能禁用 + 引导实名

### 场景 9：地区功能屏蔽
- 业务背景：GDPR 区域屏蔽 PII
- 涉及字段/工具：region、feature_geo_block
- 触发动作：欧盟玩家访问 PII 展示页
- 验证点：PII 字段屏蔽（仅显示 *）

### 场景 10：版号限制功能
- 业务背景：某副本未获版号
- 涉及字段/工具：isbn、feature_license
- 触发动作：玩家尝试进入该副本
- 验证点：入口隐藏 + 服务端拒绝

### 场景 11：跨境支付限制
- 业务背景：某地区不支持某支付方式
- 涉及字段/工具：region、pay_method
- 触发动作：跨境玩家尝试支付
- 验证点：支付方式过滤 + 提示"当前地区不支持"

### 场景 12：实名认证缺失拦截
- 业务背景：玩家未实名
- 涉及字段/工具：real_name_status
- 触发动作：玩家登录
- 验证点：首次登录强制要求实名 + 未实名部分功能不可用

### 场景 13：未成年强制休息
- 业务背景：未成年累计游戏 1h，强制休息 15min
- 涉及字段/工具：minor_rest、rest_enforce
- 触发动作：未成年游戏 1h
- 验证点：强制踢下线 + 15min 后可重新登录

### 场景 14：游客模式限制
- 业务背景：未实名游客模式限制
- 涉及字段/工具：guest_mode、guest_restrict
- 触发动作：游客充值
- 验证点：游客不可充值 + 引导注册

### 场景 15：地区合规数据脱敏
- 业务背景：GDPR 玩家数据
- 涉及字段/工具：pii_data、data_mask
- 触发动作：客服查询 GDPR 玩家数据
- 验证点：PII 字段脱敏（如手机号 138****1234）

---

## 2. 种子测试点（TP 模板）

### TP-001（COMPLIANCE_RISK）：未成年游戏时长限制
- **scenario**：场景 1
- **module**：`COMPLIANCE_RISK`
- **precondition**：未成年玩家（身份证解析 = 未成年）
- **test_data**：玩家累计游戏 1.5h
- **expected**：强制下线 + 提示"已达游戏时长上限（1h）" + 当日不可再登录
- **notes**：注意"未成年" vs "实名缺失"——后者未实名不是未成年

### TP-002（COMPLIANCE_RISK）：未成年宵禁
- **scenario**：场景 2
- **module**：`COMPLIANCE_RISK`
- **precondition**：未成年玩家
- **test_data**：22:01 尝试登录
- **expected**：拒绝登录 + 提示"宵禁时间（22:00-8:00 禁止游戏）"
- **notes**：注意"宵禁" vs "时长"——宵禁是固定时段

### TP-003（COMPLIANCE_RISK）：未成年单笔限额
- **scenario**：场景 3
- **module**：`COMPLIANCE_RISK`
- **precondition**：未成年玩家
- **test_data**：尝试充值 100 元
- **expected**：拒绝 + 提示"单笔付费限额 50 元"
- **notes**：注意"单笔" vs "月累计"——单笔是单次

### TP-004（COMPLIANCE_RISK）：未成年月累计限额
- **scenario**：场景 4
- **module**：`COMPLIANCE_RISK`
- **precondition**：未成年玩家本月已充 180 元
- **test_data**：尝试再充 50 元
- **expected**：拒绝 + 提示"月累计限额 200 元"
- **notes**：注意"月累计" vs "单笔"——月累计是按月

### TP-005（COMPLIANCE_RISK）：聊天敏感词拦截
- **scenario**：场景 5
- **module**：`COMPLIANCE_RISK`
- **precondition**：玩家登录
- **test_data**：发送消息"违禁词1"
- **expected**：消息拦截 + 提示"消息含敏感内容" + 记录日志
- **notes**：注意"敏感词" vs "广告"——广告是另一类

### TP-006（COMPLIANCE_RISK）：昵称敏感词拦截
- **scenario**：场景 6
- **module**：`COMPLIANCE_RISK`
- **precondition**：玩家注册
- **test_data**：创建昵称"敏感昵称"
- **expected**：拒绝 + 提示"昵称不合规" + 要求修改
- **notes**：注意"昵称" vs "聊天"——昵称是注册时

### TP-007（COMPLIANCE_RISK）：未实名限制充值
- **scenario**：场景 7
- **module**：`COMPLIANCE_RISK`
- **precondition**：未实名玩家
- **test_data**：尝试充值
- **expected**：拒绝 + 引导实名认证（必须先实名才能充值）
- **notes**：注意"未实名" vs "未成年"——未实名不一定未成年

### TP-008（COMPLIANCE_RISK）：未实名限制聊天
- **scenario**：场景 8
- **module**：`COMPLIANCE_RISK`
- **precondition**：未实名玩家
- **test_data**：进入聊天界面
- **expected**：聊天功能禁用 + 引导实名
- **notes**：注意"未实名" vs "未成年"——限制功能可能不同

### TP-009（COMPLIANCE_RISK）：GDPR 区域 PII 屏蔽
- **scenario**：场景 9
- **module**：`COMPLIANCE_RISK`
- **precondition**：欧盟玩家（region = EU）
- **test_data**：访问个人资料页
- **expected**：PII 字段屏蔽（如手机号 138****1234）
- **notes**：注意"PII" vs "非 PII"——后者可正常显示

### TP-010（COMPLIANCE_RISK）：版号限制入口
- **scenario**：场景 10
- **module**：`COMPLIANCE_RISK`
- **precondition**：某副本未获版号（isbn_status = PENDING）
- **test_data**：玩家尝试进入
- **expected**：入口隐藏 + 服务端拒绝
- **notes**：注意"版号" vs "功能开放"——版号是法规要求

### TP-011（COMPLIANCE_RISK）：跨境支付限制
- **scenario**：场景 11
- **module**：`COMPLIANCE_RISK`
- **precondition**：跨境玩家（region = A，pay_methods 不含 B 支付）
- **test_data**：尝试用 B 支付
- **expected**：支付方式过滤 + 提示"当前地区不支持"
- **notes**：注意"跨境" vs "跨渠道"——前者是地区

### TP-012（COMPLIANCE_RISK）：首次登录强制实名
- **scenario**：场景 12
- **module**：`COMPLIANCE_RISK`
- **precondition**：玩家首次登录
- **test_data**：登录
- **expected**：首次登录强制要求实名（未实名不可继续游戏）
- **notes**：注意"首次" vs "后续"——首次是强制

### TP-013（COMPLIANCE_RISK）：未成年强制休息
- **scenario**：场景 13
- **module**：`COMPLIANCE_RISK`
- **precondition**：未成年玩家
- **test_data**：累计游戏 1h
- **expected**：强制踢下线 + 15min 休息期 + 15min 后可重新登录
- **notes**：注意"休息" vs "下线"——休息是限时下线

### TP-014（COMPLIANCE_RISK）：游客模式限制
- **scenario**：场景 14
- **module**：`COMPLIANCE_RISK`
- **precondition**：游客登录
- **test_data**：尝试充值
- **expected**：游客不可充值 + 引导注册
- **notes**：注意"游客" vs "未实名"——游客是未注册

### TP-015（COMPLIANCE_RISK）：客服查询数据脱敏
- **scenario**：场景 15
- **module**：`COMPLIANCE_RISK`
- **precondition**：GDPR 玩家数据
- **test_data**：客服查询玩家信息
- **expected**：PII 字段脱敏（如手机号 138****1234）
- **notes**：注意"客服" vs "玩家"——客服查询需脱敏

### TP-016（COMPLIANCE_RISK）：敏感词库更新
- **scenario**：场景 5 扩展
- **module**：`COMPLIANCE_RISK`
- **precondition**：敏感词库需要更新
- **test_data**：运营更新敏感词库
- **expected**：新词立即生效（无需重启）
- **notes**：注意"热更" vs "重启"——热更更优

### TP-017（COMPLIANCE_RISK）：实名信息加密
- **scenario**：场景 7 扩展
- **module**：`COMPLIANCE_RISK`
- **precondition**：玩家实名认证
- **test_data**：提交身份证号
- **expected**：身份证号加密存储 + 业务查询时脱敏
- **notes**：注意"加密" vs "脱敏"——存储加密、显示脱敏

### TP-018（COMPLIANCE_RISK）：防沉迷申诉
- **scenario**：场景 1 扩展
- **module**：`COMPLIANCE_RISK`
- **precondition**：玩家被强制下线
- **test_data**：玩家申诉
- **expected**：人工审核入口 + 30 天反馈
- **notes**：注意"申诉" vs "投诉"——申诉是合规流程

### TP-019（COMPLIANCE_RISK）：地区合规配置
- **scenario**：场景 9 扩展
- **module**：`COMPLIANCE_RISK`
- **precondition**：不同地区合规要求不同
- **test_data**：根据 region 加载合规配置
- **expected**：按地区动态启用/禁用功能
- **notes**：注意"配置" vs "代码"——配置化更灵活

### TP-020（COMPLIANCE_RISK）：未成年退款
- **scenario**：场景 3 扩展
- **module**：`COMPLIANCE_RISK`
- **precondition**：未成年超额充值
- **test_data**：家长申请退款
- **expected**：支持退款 + 7-15 工作日处理
- **notes**：注意"退款" vs "禁止"——退款是补救

---

## 3. 边界陷阱

### 边界 1：vs BIZ（账号业务）
- **混淆点**："实名认证" 看似 H → 实际 BIZ 测"实名认证业务流程"（提交流程/字段），H 测"未实名限制功能"
- **判定规则**：测"实名认证业务（注册/校验/存储）" → 归 BIZ；测"未实名的功能限制" → 归 SPECIAL H
- **instance**：实名认证接口 → 归 BIZ；未实名不可充值 → 归 H

### 边界 2：vs BIZ（支付业务）
- **混淆点**："未成年支付" 看似 H → 实际 BIZ 测"支付业务"（正常支付），H 测"未成年支付限额"
- **判定规则**：测"支付业务（正常/退款）" → 归 BIZ；测"合规限额拦截" → 归 SPECIAL H
- **instance**：正常支付 → 归 BIZ；未成年超额拦截 → 归 H

### 边界 3：vs LOG（合规审计）
- **混淆点**："合规日志" 看似 H → 实际 H 测"合规规则拦截"，LOG 测"合规日志完整性与审计"
- **判定规则**：测"合规规则（防沉迷/未成年/敏感词/地区）" → 归 SPECIAL H；测"合规日志的完整性与查询" → 归 LOG
- **instance**：未成年游戏时长拦截 → 归 H；合规日志查询 → 归 LOG

### 边界 4：vs LINK（跨地区）
- **混淆点**："地区合规" 看似 LINK → 实际 LINK 测"跨地区业务对接"（如 GDPR 接入），H 测"地区合规规则"
- **判定规则**：测"跨地区业务对接" → 归 LINK；测"地区合规功能屏蔽/限额" → 归 SPECIAL H
- **instance**：GDPR 数据接口对接 → 归 LINK；GDPR 区域 PII 屏蔽 → 归 H

### 边界 5：vs CONFIG（合规配置）
- **混淆点**："合规配置" 看似 H → 实际 CONFIG 测"合规配置字段"（如未成年时长上限），H 测"合规规则拦截执行"
- **判定规则**：测"合规配置字段" → 归 CONFIG；测"合规规则执行（拦截/屏蔽/限额）" → 归 SPECIAL H
- **instance**：未成年时长配置字段 → 归 CONFIG；未成年时长 1h 强制下线 → 归 H

---

## 4. 验证证据

### 视觉证据
- 未成年游戏时长到限时强制下线提示
- 宵禁时段拒绝登录提示
- 单笔/月累计付费限额提示
- 敏感词拦截提示
- 未实名功能限制提示
- GDPR 区域 PII 脱敏截图

### 日志证据
- `compliance.minor_play_time_exceeded` 关键词：未成年时长超额
- `compliance.minor_curfew_block` 关键词：未成年宵禁
- `compliance.minor_pay_exceeded` 关键词：未成年支付超额
- `compliance.sensitive_word_block` 关键词：敏感词拦截
- `compliance.real_name_missing` 关键词：未实名
- `compliance.gdpr_pii_masked` 关键词：GDPR PII 脱敏
- `compliance.isbn_pending` 关键词：版号待审
- `compliance.region_blocked` 关键词：地区屏蔽

### 数据证据
- `minor_player_log` 表记录未成年玩家游戏时长
- `pay_limit_log` 表记录未成年支付限额
- `sensitive_word_log` 表记录敏感词拦截
- `real_name_status` 表记录实名认证状态
- `region_compliance` 表记录地区合规配置
- `gdpr_pii_log` 表记录 PII 脱敏事件
- 未成年玩家游戏时长到限时强制下线
- 未实名玩家不可充值

### 性能证据
- 防沉迷检测耗时 < 10ms / 请求
- 敏感词检测耗时 < 50ms / 消息
- 实名校验耗时 < 100ms
- 地区合规配置加载 < 50ms
- PII 脱敏耗时 < 5ms / 字段
