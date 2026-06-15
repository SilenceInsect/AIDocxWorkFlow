# E. 客户端崩溃/报错异常日志

> **子类代码**：`LOG_CRASH_REPORT`
> **归属模块**：`LOG`
> **来源**：用户细化定义 §5「客户端崩溃/报错异常日志」
>
> **测什么**：崩溃堆栈日志（闪退/卡死/内存溢出/空指针/资源加载失败）、业务报错日志（参数非法/配置缺失/协议错误/UI 渲染异常/网络失败）、异常上下文（角色/界面/操作/网络/设备）、过滤校验（无垃圾/脱敏/完整上传）。
> **不测什么**：业务异常处理（归 BIZ）、崩溃底层捕获（归 AUX N）、异常兜底组件（归 AUX N）、业务操作日志（归 C）。
> **与其他子类的差异**：E 关注"**客户端异常**上报日志"——C 关注"业务操作日志"，D 关注"服务指标"，J 关注"安全反作弊留痕"。

---

## 1. 典型场景

### 场景 1：闪退崩溃
- 业务背景：游戏闪退
- 涉及数据：崩溃堆栈
- 触发动作：app crash
- 验证点：堆栈完整上报

### 场景 2：卡死
- 业务背景：游戏卡死 ANR
- 涉及数据：ANR 堆栈
- 触发动作：主线程 5s 未响应
- 验证点：ANR 日志含主线程堆栈

### 场景 3：内存溢出
- 业务背景：内存占用 2GB
- 涉及数据：OOM
- 触发动作：内存爆
- 验证点：OOM 日志含内存堆

### 场景 4：空指针
- 业务背景：访问 null 对象
- 涉及数据：NPE
- 触发动作：空指针异常
- 验证点：NPE 日志含堆栈

### 场景 5：资源加载失败
- 业务背景：UI 资源加载失败
- 涉及数据：资源路径
- 触发动作：load 失败
- 验证点：日志含资源路径

### 场景 6：参数非法
- 业务背景：购买参数 -1
- 涉及数据：参数
- 触发动作：业务校验失败
- 验证点：日志含非法参数

### 场景 7：配置缺失
- 业务背景：道具表缺失
- 涉及数据：配置 ID
- 触发动作：配置缺失
- 验证点：日志含 config_id

### 场景 8：协议错误
- 业务背景：服务端返回错误码
- 涉及数据：错误码
- 触发动作：业务失败
- 验证点：日志含 protocol_error

### 场景 9：UI 渲染异常
- 业务背景：UI 渲染失败
- 涉及数据：UI 节点
- 触发动作：渲染异常
- 验证点：日志含 UI 路径

### 场景 10：网络业务失败
- 业务背景：购买网络失败
- 涉及数据：API
- 触发动作：网络异常
- 验证点：日志含 network_error

### 场景 11：崩溃时角色信息
- 业务背景：玩家崩溃
- 涉及数据：角色
- 触发动作：崩溃前快照
- 验证点：日志含 role_id、level

### 场景 12：当前界面信息
- 业务背景：崩溃时
- 涉及数据：页面
- 触发动作：崩溃
- 验证点：日志含 current_page

### 场景 13：操作步骤
- 业务背景：最近 5 步操作
- 涉及数据：操作序列
- 触发动作：崩溃
- 验证点：日志含 last 5 steps

### 场景 14：网络环境
- 业务背景：崩溃时网络
- 涉及数据：网络
- 触发动作：崩溃
- 验证点：日志含 network_type

### 场景 15：设备机型
- 业务背景：崩溃设备
- 涉及数据：设备
- 触发动作：崩溃
- 验证点：日志含 device_model

### 场景 16：无垃圾报错
- 业务背景：try-catch 滥用
- 涉及数据：catch 块
- 触发动作：catch 异常
- 验证点：仅关键异常上报

### 场景 17：敏感信息脱敏
- 业务背景：日志含 token
- 涉及数据：token
- 触发动作：写入日志
- 验证点：token 脱敏

### 场景 18：崩溃日志完整上传
- 业务背景：玩家崩溃
- 涉及数据：堆栈
- 触发动作：下次启动
- 验证点：下次启动上传

### 场景 19：崩溃率监控
- 业务背景：崩溃率 0.5%
- 涉及数据：DAU 崩溃数
- 触发动作：定时统计
- 验证点：埋点含 crash_rate

### 场景 20：版本号关联
- 业务背景：崩溃定位
- 涉及数据：版本
- 触发动作：崩溃
- 验证点：日志含 client_version

---

## 2. 种子测试点（TP 模板）

### TP-001（LOG_CRASH_REPORT）：闪退崩溃
- **scenario**：场景 1
- **module**：`LOG_CRASH_REPORT`
- **precondition**：app 崩溃
- **test_data**：构造崩溃
- **expected**：崩溃日志 `CRASH type=crash stack=xxx`
- **notes**：注意"原生"vs"JVM"+"堆栈完整"

### TP-002（LOG_CRASH_REPORT）：ANR 卡死
- **scenario**：场景 2
- **module**：`LOG_CRASH_REPORT`
- **precondition**：主线程 5s 未响应
- **test_data`：构造 ANR
- **expected**：ANR 日志 `CRASH type=ANR main_thread_stack=xxx`
- **notes**：注意"主线程"vs"子线程"

### TP-003（LOG_CRASH_REPORT）：内存溢出
- **scenario**：场景 3
- **module**：`LOG_CRASH_REPORT`
- **precondition**：内存占用 2GB
- **test_data`：构造 OOM
- **expected**：OOM 日志 `CRASH type=OOM heap_dump=xxx`
- **notes**：注意"堆"+"分析"

### TP-004（LOG_CRASH_REPORT）：空指针
- **scenario**：场景 4
- **module**：`LOG_CRASH_REPORT`
- **precondition**：null 对象
- **test_data`：构造 NPE
- **expected**：NPE 日志 `CRASH type=NPE stack=xxx`
- **notes**：注意"局部"vs"全局"

### TP-005（LOG_CRASH_REPORT）：资源加载失败
- **scenario**：场景 5
- **module**：`LOG_CRASH_REPORT`
- **precondition**：资源路径不存在
- **test_data**：构造 load fail
- **expected**：日志 `CRASH type=resource path=xxx`
- **notes**：注意"图片"vs"音频"vs"模型"

### TP-006（LOG_CRASH_REPORT）：业务报错
- **scenario**：场景 6
- **module**：`LOG_CRASH_REPORT`
- **precondition**：参数非法
- **test_data`：`purchase(count=-1)`
- **expected`：日志 `BIZ_ERROR type=invalid_param param=count`
- **notes**：注意"业务"vs"崩溃"

### TP-007（LOG_CRASH_REPORT）：配置缺失
- **scenario**：场景 7
- **module**：`LOG_CRASH_REPORT`
- **precondition**：道具表缺 item_id
- **test_data`：`get_item(item_id=9999)`
- **expected`：日志 `BIZ_ERROR type=config_missing config_id=item_9999`
- **notes**：注意"配置"vs"业务"

### TP-008（LOG_CRASH_REPORT）：协议错误
- **scenario**：场景 8
- **module**：`LOG_CRASH_REPORT`
- **precondition`：服务端返回错误
- **test_data`：`api_response(code=500)`
- **expected`：日志 `BIZ_ERROR type=protocol code=500`
- **notes**：注意"客户端"vs"服务端"

### TP-009（LOG_CRASH_REPORT）：UI 渲染异常
- **scenario**：场景 9
- **module**：`LOG_CRASH_REPORT`
- **precondition**：UI 渲染失败
- **test_data`：构造渲染异常
- **expected`：日志 `BIZ_ERROR type=ui_render path=shop`
- **notes**：注意"控件"vs"页面"

### TP-010（LOG_CRASH_REPORT）：网络业务失败
- **scenario**：场景 10
- **module**：`LOG_CRASH_REPORT`
- **precondition**：购买网络失败
- **test_data`：`purchase_api()` fail
- **expected`：日志 `BIZ_ERROR type=network api=purchase`
- **notes**：注意"网络"vs"业务"

### TP-011（LOG_CRASH_REPORT）：崩溃角色信息
- **scenario**：场景 11
- **module**：`LOG_CRASH_REPORT`
- **precondition**：玩家崩溃
- **test_data`：观察
- **expected`：崩溃日志含 `role_id=xxx level=10`
- **notes**：注意"崩溃前"+"最后状态"

### TP-012（LOG_CRASH_REPORT）：崩溃时界面
- **scenario**：场景 12
- **module**：`LOG_CRASH_REPORT`
- **precondition**：玩家在商城崩溃
- **test_data`：观察
- **expected`：崩溃日志含 `page=shop`
- **notes**：注意"页面"+"路由"

### TP-013（LOG_CRASH_REPORT）：崩溃前操作
- **scenario**：场景 13
- **module**：`LOG_CRASH_REPORT`
- **precondition**：玩家崩溃
- **test_data`：观察
- **expected`：崩溃日志含 `last_steps=[click_buy, click_confirm, ...]`
- **notes**：注意"最近 5 步"+"操作序列"

### TP-014（LOG_CRASH_REPORT）：崩溃网络环境
- **scenario**：场景 14
- **module**：`LOG_CRASH_REPORT`
- **precondition**：玩家崩溃
- **test_data`：观察
- **expected`：崩溃日志含 `network=wifi/4G/5G`
- **notes**：注意"网络类型"+"延迟"

### TP-015（LOG_CRASH_REPORT）：设备机型
- **scenario**：场景 15
- **module**：`LOG_CRASH_REPORT`
- **precondition**：玩家崩溃
- **test_data`：观察
- **expected`：崩溃日志含 `device=iPhone 14 / Xiaomi 13`
- **notes**：注意"机型"+"OS 版本"

### TP-016（LOG_CRASH_REPORT）：垃圾报错过滤
- **scenario**：场景 16
- **module**：`LOG_CRASH_REPORT`
- **precondition**：try-catch 频繁
- **test_data`：观察
- **expected**：仅关键异常上报、不刷屏
- **notes**：注意"过滤规则"+"白名单"

### TP-017（LOG_CRASH_REPORT）：敏感信息脱敏
- **scenario**：场景 17
- **module**：`LOG_CRASH_REPORT`
- **precondition**：日志含 token/password
- **test_data`：观察
- **expected**：日志脱敏为 `***`
- **notes**：注意"脱敏规则"+"合规"

### TP-018（LOG_CRASH_REPORT）：崩溃日志完整上传
- **scenario**：场景 18
- **module**：`LOG_CRASH_REPORT`
- **precondition**：玩家崩溃
- **test_data`：下次启动
- **expected**：下次启动上传崩溃日志
- **notes**：注意"本地缓存"+"上传"

### TP-019（LOG_CRASH_REPORT）：崩溃率统计
- **scenario**：场景 19
- **module**：`LOG_CRASH_REPORT`
- **precondition**：DAU 10000 崩溃 50
- **test_data`：观察
- **expected`：埋点 `CRASH_RATE dau=10000 crash=50 rate=0.5%`
- **notes**：注意"崩溃率"+"告警阈值"

### TP-020（LOG_CRASH_REPORT）：版本号关联
- **scenario**：场景 20
- **module**：`LOG_CRASH_REPORT`
- **precondition**：玩家 v1.2.3 崩溃
- **test_data`：观察
- **expected`：崩溃日志含 `version=1.2.3`
- **notes**：注意"客户端"+"服务端"版本

### TP-021（LOG_CRASH_REPORT）：崩溃堆栈完整
- **scenario**：场景 1
- **module**：`LOG_CRASH_REPORT`
- **precondition**：崩溃
- **test_data`：观察堆栈
- **expected**：含文件/行号/函数名
- **notes**：注意"release"也含符号

### TP-022（LOG_CRASH_REPORT）：崩溃去重
- **scenario**：场景 1
- **module**：`LOG_CRASH_REPORT`
- **precondition**：同一崩溃 100 次
- **test_data`：观察
- **expected**：聚合 1 个 issue
- **notes**：注意"指纹"+"聚合"

### TP-023（LOG_CRASH_REPORT）：网络异常上下文
- **scenario**：场景 10
- **module**：`LOG_CRASH_REPORT`
- **precondition**：网络失败
- **test_data`：观察
- **expected`：日志含 `request_url=xxx status=500`
- **notes**：注意"URL"+"状态码"

### TP-024（LOG_CRASH_REPORT）：崩溃统计可视化
- **scenario**：场景 19
- **module**：`LOG_CRASH_REPORT`
- **precondition`：1 周崩溃数据
- **test_data`：查看崩溃后台
- **expected**：含崩溃率、Top 崩溃、版本分布
- **notes**：注意"可视化"+"Top 10"

### TP-025（LOG_CRASH_REPORT）：崩溃告警
- **scenario**：场景 19
- **module**：`LOG_CRASH_REPORT`
- **precondition**：崩溃率 > 1%
- **test_data`：观察
- **expected**：告警
- **notes**：注意"告警阈值"+"通知"

### TP-026（LOG_CRASH_REPORT）：堆栈脱敏
- **scenario**：场景 17
- **module**：`LOG_CRASH_REPORT`
- **precondition**：堆栈含敏感信息
- **test_data**：观察
- **expected**：敏感字段脱敏
- **notes**：注意"堆栈"脱敏

### TP-027（LOG_CRASH_REPORT）：ANR 检测
- **scenario**：场景 2
- **module**：`LOG_CRASH_REPORT`
- **precondition**：主线程 5s 未响应
- **test_data`：构造
- **expected`：ANR 日志 + 主线程堆栈
- **notes**：注意"Android"+"iOS"差异

### TP-028（LOG_CRASH_REPORT）：卡顿检测
- **scenario**：场景 2
- **module**：`LOG_CRASH_REPORT`
- **precondition**：主线程 1s 慢
- **test_data`：构造
- **expected**：卡顿日志
- **notes**：注意"卡顿"vs"ANR"

### TP-029（LOG_CRASH_REPORT）：网络抖动
- **scenario**：场景 10
- **module**：`LOG_CRASH_REPORT`
- **precondition**：网络抖动 1s
- **test_data`：观察
- **expected**：日志含 network_type=poor
- **notes**：注意"网络质量"

### TP-030（LOG_CRASH_REPORT）：崩溃后行为
- **scenario**：场景 1
- **module**：`LOG_CRASH_REPORT`
- **precondition`：玩家崩溃
- **test_data`：下次启动
- **expected**：日志含 `recovery_status=ok/...`
- **notes**：注意"恢复"+"重连"

---

## 3. 边界陷阱

### 边界 1：vs C. 操作日志
- **混淆点**：「业务"报错"」——E 测崩溃/异常、C 测操作
- **判定规则**：测"异常堆栈" → E；测"操作日志" → C
- **实例**：崩溃堆栈 → E；购买操作 → C

### 边界 2：vs D. 监控
- **混淆点**：「崩溃"指标"」——E 测单点、D 测聚合
- **判定规则**：测"单次崩溃" → E；测"崩溃率统计" → D
- **实例**：单次崩溃堆栈 → E；崩溃率 → D

### 边界 3：vs AUX N. 异常兜底
- **混淆点**：「异常"捕获"」——AUX N 测兜底、E 测日志
- **判定规则**：测"异常兜底组件" → AUX N；测"崩溃日志上报" → E
- **实例**：全局崩溃捕获 → AUX N；崩溃日志内容 → E

### 边界 4：vs BIZ. 业务
- **混淆点**：「业务"异常"」——BIZ 测业务处理、E 测日志
- **判定规则**：测"业务异常处理" → BIZ；测"业务报错日志" → E
- **实例**：购买失败补偿 → BIZ；购买错误日志 → E

### 边界 5：vs J. 安全日志
- **混淆点**：「异常"日志"」——E 测崩溃、J 测安全
- **判定规则**：测"崩溃/技术异常" → E；测"安全违规" → J
- **实例**：空指针崩溃 → E；作弊检测 → J

---

## 4. 验证证据

### 视觉证据
- 崩溃后台截图（崩溃率/Top 10）
- 崩溃详情截图（堆栈 + 上下文）

### 日志证据
- `CRASH type=crash/ANR/OOM/NPE stack=xxx`
- `BIZ_ERROR type=invalid_param/config_missing/protocol/ui_render/network`
- 上下文 `role_id/level/page/last_steps/network/device/version`
- 脱敏日志 `***`

### 数据证据
- 崩溃日志表 `crash_log.type, stack, context, time, version`
- 崩溃率 = 崩溃数 ÷ DAU
- Top 崩溃聚合（指纹去重）
- 崩溃率告警阈值 = 1%
- 敏感字段脱敏 100%

### 性能证据
- 崩溃日志本地缓存 < 1MB
- 崩溃日志上传 < 10s
- 崩溃后台查询 < 1s
- 崩溃率计算 < 1min
- 崩溃告警延迟 < 1min
