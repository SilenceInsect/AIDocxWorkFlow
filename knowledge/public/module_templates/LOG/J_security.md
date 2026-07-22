# J. 安全 & 反作弊日志

> **子类代码**：`LOG_SECURITY`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §10「安全 & 反作弊日志（原定义完全缺失，新增）」
>
> **测什么**：作弊行为拦截、参数篡改检测、高频限流封禁、异地登录、批量建号、外挂行为完整日志留痕，作为风控溯源依据。
> **不测什么**：反作弊业务逻辑（归 SPECIAL）、参数篡改拦截（归 SPECIAL）、业务操作日志（归 C）、GM 操作日志（归 C）。
> **与其他子类的差异**：J 关注"**安全/反作弊**日志留痕"——C 关注"操作日志"，E 关注"崩溃日志"，D 关注"异常告警"。

---

## 1. 典型场景

### 场景 1：作弊拦截
- 业务背景：检测到外挂
- 涉及数据：作弊
- 触发动作：检测
- 验证点：日志留痕

### 场景 2：参数篡改
- 业务背景：客户端修改金币
- 涉及数据：篡改
- 触发动作：服务端检测
- 验证点：日志留痕

### 场景 3：高频限流
- 业务背景：玩家 1s 1000 次
- 涉及数据：限流
- 触发动作：限流
- 验证点：日志留痕

### 场景 4：封禁
- 业务背景：违规封号
- 涉及数据：封禁
- 触发动作：封号
- 验证点：日志留痕

### 场景 5：异地登录
- 业务背景：玩家从上海到纽约
- 涉及数据：异地
- 触发动作：登录
- 验证点：日志留痕

### 场景 6：批量建号
- 业务背景：同 IP 1 小时 100 号
- 涉及数据：批量
- 触发动作：建号
- 验证点：日志留痕

### 场景 7：外挂行为
- 业务背景：自动脚本
- 涉及数据：外挂
- 触发动作：检测
- 验证点：日志留痕

### 场景 8：内存修改器
- 业务背景：玩家改内存
- 涉及数据：修改
- 触发动作：检测
- 验证点：日志留痕

### 场景 9：协议篡改
- 业务背景：改协议
- 涉及数据：协议
- 触发动作：检测
- 验证点：日志留痕

### 场景 10：模拟点击
- 业务背景：脚本点击
- 涉及数据：脚本
- 触发动作：检测
- 验证点：日志留痕

### 场景 11：多端登录冲突
- 业务背景：A 设备 + B 设备同登
- 涉及数据：冲突
- 触发动作：登录
- 验证点：日志留痕

### 场景 12：设备指纹异常
- 业务背景：同设备多账号
- 涉及数据：指纹
- 触发动作：登录
- 验证点：日志留痕

### 场景 13：IP 黑名单
- 业务背景：黑 IP
- 涉及数据：IP
- 触发动作：访问
- 验证点：日志留痕

### 场景 14：风控告警
- 业务背景：风控
- 涉及数据：风控
- 触发动作：告警
- 验证点：日志留痕

### 场景 15：玩家举报
- 业务背景：被举报
- 涉及数据：举报
- 触发动作：举报
- 验证点：日志留痕

### 场景 16：客服审核
- 业务背景：违规审核
- 涉及数据：审核
- 触发动作：审核
- 验证点：日志留痕

### 场景 17：申诉
- 业务背景：玩家申诉
- 涉及数据：申诉
- 触发动作：申诉
- 验证点：日志留痕

### 场景 18：异常登录
- 业务背景：凌晨 3 点登录
- 涉及数据：异常时间
- 触发动作：登录
- 验证点：日志留痕

### 场景 19：账号绑定异常
- 业务背景：异常绑定
- 涉及数据：绑定
- 触发动作：绑定
- 验证点：日志留痕

### 场景 20：风控画像
- 业务背景：玩家画像
- 涉及数据：画像
- 触发动作：生成
- 验证点：日志留痕

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_SECURITY）：作弊拦截
- **scenario**：场景 1
- **module**：`LOG_SECURITY`
- **precondition**：检测到外挂
- **test_data`：`cheat_detect(player_id, type=aimbot)`
- **expected**：日志 `SECURITY type=cheat player_id type`
- **notes**：注意"检测"vs"封号"

### TP-002（LOG_SECURITY）：参数篡改
- **scenario**：场景 2
- **module**：`LOG_SECURITY`
- **precondition**：客户端改金币
- **test_data`：`param_tamper(field=coin, expected=100, actual=99999)`
- **expected**：日志 `SECURITY type=tamper field expected actual`
- **notes**：注意"篡改"vs"业务"

### TP-003（LOG_SECURITY）：高频限流
- **scenario**：场景 3
- **module**：`LOG_SECURITY`
- **precondition**：玩家 1s 1000 次
- **test_data`：`rate_limit_hit(player_id, count=1000)`
- **expected`：日志 `SECURITY type=rate_limit player_id count`
- **notes**：注意"限流"vs"业务"

### TP-004（LOG_SECURITY）：封禁
- **scenario**：场景 4
- **module**：`LOG_SECURITY`
- **precondition**：违规
- **test_data`：`ban(player_id, reason, duration)`
- **expected`：日志 `SECURITY type=ban player_id reason duration`
- **notes**：注意"封号"vs"禁言"

### TP-005（LOG_SECURITY）：异地登录
- **scenario**：场景 5
- **module**：`LOG_SECURITY`
- **precondition**：异地
- **test_data`：`login(player_id, ip=纽约, normal_ip=上海)`
- **expected`：日志 `SECURITY type=abnormal_ip player_id current normal`
- **notes**：注意"异地"vs"正常"

### TP-006（LOG_SECURITY）：批量建号
- **scenario**：场景 6
- **module**：`LOG_SECURITY`
- **precondition**：同 IP 1h 100 号
- **test_data`：`mass_register(ip, count=100, window=1h)`
- **expected`：日志 `SECURITY type=mass_register ip count`
- **notes**：注意"批量"vs"个人"

### TP-007（LOG_SECURITY）：外挂行为
- **scenario**：场景 7
- **module**：`LOG_SECURITY`
- **precondition**：自动脚本
- **test_data`：`detect(player_id, type=auto_script)`
- **expected`：日志 `SECURITY type=cheat player_id type`
- **notes**：注意"脚本"vs"手动"

### TP-008（LOG_SECURITY）：内存修改
- **scenario**：场景 8
- **module**：`LOG_SECURITY`
- **precondition**：玩家改内存
- **test_data`：`memory_tamper(field=hp, value=99999)`
- **expected`：日志 `SECURITY type=memory_tamper field value`
- **notes**：注意"内存"vs"协议"

### TP-009（LOG_SECURITY）：协议篡改
- **scenario**：场景 9
- **module**：`LOG_SECURITY`
- **precondition**：改协议
- **test_data`：`protocol_tamper(proto=purchase, param=count=-1)`
- **expected`：日志 `SECURITY type=protocol_tamper proto param`
- **notes**：注意"协议"vs"参数"

### TP-010（LOG_SECURITY）：模拟点击
- **scenario**：场景 10
- **module**：`LOG_SECURITY`
- **precondition**：脚本点击
- **test_data`：`auto_click(player_id, freq=10/s)`
- **expected`：日志 `SECURITY type=auto_click player_id freq`
- **notes**：注意"脚本"+"频率"

### TP-011（LOG_SECURITY）：多端冲突
- **scenario**：场景 11
- **module**：`LOG_SECURITY`
- **precondition**：A+B 同登
- **test_data`：`multi_login(player_id, devices=[A, B])`
- **expected`：日志 `SECURITY type=multi_login player_id devices`
- **notes**：注意"多端"vs"踢出"

### TP-012（LOG_SECURITY）：设备指纹
- **scenario**：场景 12
- **module**：`LOG_SECURITY`
- **precondition**：同设备多账号
- **test_data`：`device_abnormal(device_id, account_count=5)`
- **expected`：日志 `SECURITY type=device_abnormal device count`
- **notes**：注意"指纹"vs"设备"

### TP-013（LOG_SECURITY）：IP 黑名单
- **scenario**：场景 13
- **module**：`LOG_SECURITY`
- **precondition`：黑 IP
- **test_data`：`ip_blacklist_hit(ip)`
- **expected`：日志 `SECURITY type=ip_blacklist ip`
- **notes**：注意"黑名单"vs"白名单"

### TP-014（LOG_SECURITY）：风控告警
- **scenario**：场景 14
- **module**：`LOG_SECURITY`
- **precondition**：风控触发
- **test_data`：`risk_alert(player_id, type)`
- **expected`：日志 `SECURITY type=risk_alert player_id type`
- **notes**：注意"告警"vs"拦截"

### TP-015（LOG_SECURITY）：玩家举报
- **scenario**：场景 15
- **module**：`LOG_SECURITY`
- **precondition`：被举报
- **test_data`：`report(reporter=A, target=B, reason)`
- **expected`：日志 `SECURITY type=report reporter target reason`
- **notes**：注意"举报"vs"违规"

### TP-016（LOG_SECURITY）：客服审核
- **scenario**：场景 16
- **module**：`LOG_SECURITY`
- **precondition**：违规审核
- **test_data`：`review(case_id, op_id, decision)`
- **expected`：日志 `SECURITY type=review case op_id decision`
- **notes**：注意"审核"vs"自动"

### TP-017（LOG_SECURITY）：玩家申诉
- **scenario**：场景 17
- **module**：`LOG_SECURITY`
- **precondition`：玩家申诉
- **test_data`：`appeal(player_id, case_id, reason)`
- **expected`：日志 `SECURITY type=appeal player_id case`
- **notes**：注意"申诉"vs"封号"

### TP-018（LOG_SECURITY）：异常时间登录
- **scenario**：场景 18
- **module**：`LOG_SECURITY`
- **precondition`：凌晨 3 点
- **test_data`：`login(player_id, time=03:00)`
- **expected`：日志 `SECURITY type=abnormal_time player_id time`
- **notes**：注意"时间"vs"行为"

### TP-019（LOG_SECURITY）：账号绑定异常
- **scenario**：场景 19
- **module**：`LOG_SECURITY`
- **precondition**：异常绑定
- **test_data`：`bind_abnormal(player_id, type)`
- **expected`：日志 `SECURITY type=bind_abnormal player_id type`
- **notes**：注意"绑定"vs"异常"

### TP-020（LOG_SECURITY）：风控画像
- **scenario**：场景 20
- **module**：`LOG_SECURITY`
- **precondition**：玩家画像
- **test_data`：`risk_profile(player_id, score)`
- **expected`：日志 `SECURITY type=risk_profile player_id score`
- **notes**：注意"画像"vs"实时"

### TP-021（LOG_SECURITY）：安全溯源
- **scenario**：场景 1
- **module**：`LOG_SECURITY`
- **precondition**：玩家违规
- **test_data`：`trace(player_id, 30day)`
- **expected`：返回所有安全日志
- **notes**：注意"溯源"vs"实时"

### TP-022（LOG_SECURITY）：风控规则
- **scenario**：场景 14
- **module**：`LOG_SECURITY`
- **precondition**：风控规则
- **test_data`：`rule_hit(rule_id, player_id)`
- **expected`：日志 `SECURITY type=rule_hit rule_id player_id`
- **notes**：注意"规则"vs"决策"

### TP-023（LOG_SECURITY）：设备封禁
- **scenario**：场景 4
- **module**：`LOG_SECURITY`
- **precondition**：设备封禁
- **test_data`：`device_ban(device_id, reason)`
- **expected`：日志 `SECURITY type=device_ban device_id reason`
- **notes**：注意"设备"vs"账号"

### TP-024（LOG_SECURITY）：IP 段封禁
- **scenario**：场景 13
- **module**：`LOG_SECURITY`
- **precondition**：IP 段封禁
- **test_data`：`ip_range_ban(ip_range, reason)`
- **expected`：日志 `SECURITY type=ip_range_ban ip_range reason`
- **notes**：注意"段"vs"单 IP"

### TP-025（LOG_SECURITY）：风控报告
- **scenario**：场景 20
- **module**：`LOG_SECURITY`
- **precondition**：周风控
- **test_data`：`weekly_report()`
- **expected`：含拦截数、误封率、Top 规则
- **notes**：注意"报告"vs"实时"

---

## 3. 边界陷阱

### 边界 1：vs SPECIAL 反作弊
- **混淆点**：「作弊"检测"」——SPECIAL 测逻辑、J 测日志
- **判定规则**：测"反作弊业务逻辑" → SPECIAL；测"反作弊日志" → J
- **实例**：外挂检测算法 → SPECIAL；检测日志留痕 → J

### 边界 2：vs C. 操作日志
- **混淆点**：「封号"操作"」——C 测操作、J 测安全
- **判定规则**：测"操作留痕" → C；测"安全违规" → J
- **实例**：GM 封号操作 → C；作弊检测 → J

### 边界 3：vs E. 崩溃
- **混淆点**：「异常"日志"」——E 测崩溃、J 测安全
- **判定规则**：测"崩溃" → E；测"安全" → J
- **实例**：NPE 崩溃 → E；外挂检测 → J

### 边界 4：vs BIZ. 业务
- **混淆点**：「参数"校验"」——BIZ 测业务、J 测日志
- **判定规则**：测"业务校验" → BIZ；测"安全日志" → J
- **实例**：购买参数校验 → BIZ；参数篡改日志 → J

### 边界 5：vs D. 监控
- **混淆点**：「安全"告警"」——D 测指标、J 测日志
- **判定规则**：测"告警指标" → D；测"安全日志" → J
- **实例**：风控告警率 → D；作弊日志 → J

---

## 4. 验证证据

### 视觉证据
- 风控后台截图
- 安全日志检索截图

### 日志证据
- `SECURITY type=cheat/tamper/rate_limit/ban/abnormal_ip/mass_register`
- `report/review/appeal`
- `risk_profile/rule_hit`

### 数据证据
- 安全日志表 `security_log.type, player_id, target, time, op_id`
- 封禁记录
- 风控画像
- 误封率
- 玩家申诉记录

### 性能证据
- 安全检测 < 50ms
- 风控告警 < 1s
- 安全溯源 < 1s
- 风控周报 < 5min
