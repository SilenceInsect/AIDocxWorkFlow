# A. 公共工具（底层基础组件）

> **子类代码**：`COMMON_UTIL`
> **归属模块**：`AUX`
> **来源**：用户细化定义 §1「公共工具」
>
> **v1.6.1 变更**：**剔除高层业务辅助**（红点/弹窗/Toast/埋点/提示）——本子模板**只保留底层基础工具能力**。
> - 红点/弹窗/Toast → 归 **HINT 模块**（v1.7 待建）
> - 埋点 SDK → 归 **LOG 模块**（v1.8 待建）
>
> **测什么**：时间转换、随机数、ID 生成、字符串、加密解密、计算工具、路由、本地存储、剪贴板。
> **不测什么**：业务逻辑（归 BIZ）、网络底层（归 B）、运行时缓存（归 C）、红点/提示（归 HINT）、日志/埋点（归 LOG）。

---

## 1. 典型场景

### 场景 1：时间转换
- 业务背景：倒计时、时长显示
- 涉及工具：时间转换工具
- 触发动作：Unix 时间戳 → "HH:mm:ss"
- 验证点：转换正确

### 场景 2：随机数
- 业务背景：抽卡、随机事件
- 涉及工具：随机数生成
- 触发动作：调用 `random(1, 100)`
- 验证点：分布合理、可指定种子

### 场景 3：ID 生成
- 业务背景：玩家 ID、订单 ID
- 涉及工具：唯一 ID 生成
- 触发动作：调用 `gen_id()`
- 验证点：全局唯一、不可预测

### 场景 4：字符串处理
- 业务背景：玩家名、聊天消息
- 涉及工具：字符串工具
- 触发动作：截取、拼接、过滤特殊字符
- 验证点：正确处理 UTF-8

### 场景 5：加密解密
- 业务背景：玩家数据、协议加密
- 涉及工具：加解密工具
- 触发动作：AES 加密
- 验证点：加解密一致

### 场景 6：弹窗公共封装
- 业务背景：通用确认弹窗
- 涉及组件：弹窗公共封装
- 触发动作：调用 `showConfirmDialog()`
- 验证点：弹窗样式统一

### 场景 7：全局红点
- 业务背景：未读消息、新功能
- 涉及组件：全局红点
- 触发动作：注册红点、清除红点
- 验证点：跨页面同步

### 场景 8：跳转路由
- 业务背景：从 A 页跳 B 页
- 涉及组件：路由
- 触发动作：`navigate("shop")`
- 验证点：跳转正确、参数传递

### 场景 9：本地存储读写
- 业务背景：玩家设置存档
- 涉及组件：本地存储
- 触发动作：`localStorage.set/get`
- 验证点：读写一致

### 场景 10：剪贴板工具
- 业务背景：复制兑换码
- 涉及组件：剪贴板
- 触发动作：复制 → 粘贴
- 验证点：内容一致

---

## 2. 种子测试点（TP 模板）

### TP-001（COMMON_UTIL）：时间戳转字符串
- **scenario**：场景 1
- **module**：`COMMON_UTIL`
- **precondition**：Unix 时间戳 1718390400（2024-06-15 00:00:00）
- **test_data**：`formatTime(1718390400, "yyyy-MM-dd HH:mm:ss")`
- **expected**："2024-06-15 00:00:00"
- **notes**：注意时区（UTC vs 本地）

### TP-002（COMMON_UTIL）：字符串转时间戳
- **scenario**：场景 1
- **module**：`COMMON_UTIL`
- **precondition**：字符串 "2024-06-15 00:00:00"
- **test_data**：`parseTime("2024-06-15 00:00:00")`
- **expected**：1718390400
- **notes**：注意夏令时

### TP-003（COMMON_UTIL）：随机数范围
- **scenario**：场景 2
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：`random(1, 100)` 调用 1000 次
- **expected**：值在 [1, 100] 区间
- **notes**：注意"开区间"vs"闭区间"

### TP-004（COMMON_UTIL）：随机数分布
- **scenario**：场景 2
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：`random(1, 100)` 调用 10000 次
- **expected**：每个值出现次数 ≈ 100
- **notes**：注意"均匀分布"vs"高斯分布"

### TP-005（COMMON_UTIL）：随机种子复现
- **scenario**：场景 2
- **module**：`COMMON_UTIL`
- **precondition**：种子 = 12345
- **test_data**：调用 random 两次
- **expected**：两次结果一致
- **notes**：注意"可复现"用于测试和录像

### TP-006（COMMON_UTIL）：ID 全局唯一
- **scenario**：场景 3
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：连续生成 10000 个 ID
- **expected**：所有 ID 不重复
- **notes**：注意"分布式 ID"（雪花算法 vs UUID）

### TP-007（COMMON_UTIL）：ID 不可预测
- **scenario**：场景 3
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：连续生成 2 个 ID
- **expected**：ID 增量不可猜测（无明显规律）
- **notes**：注意"安全"vs"性能"（UUID vs 自增）

### TP-008（COMMON_UTIL）：字符串 UTF-8 处理
- **scenario**：场景 4
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：`"你好世界"`、`"🎮游戏"`、`"ㄚㄣˊ"`
- **expected**：正确处理多字节字符
- **notes**：注意 emoji 长度计算

### TP-009（COMMON_UTIL）：字符串特殊字符过滤
- **scenario**：场景 4
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：含 `\x00`、`<script>`、`' OR 1=1--`
- **expected**：过滤或转义
- **notes**：注意 SQL 注入、XSS

### TP-010（COMMON_UTIL）：AES 加解密一致
- **scenario**：场景 5
- **module**：`COMMON_UTIL`
- **precondition**：密钥 = "secret"
- **test_data**：原文 "hello" → 密文 → 原文
- **expected**：解密结果 = 原文
- **notes**：注意 IV 初始化向量

### TP-011（COMMON_UTIL）：弹窗公共封装
- **scenario**：场景 6
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：`showConfirmDialog({title: "退出", onConfirm: ...})`
- **expected**：弹窗样式与其他弹窗一致
- **notes**：注意"统一 UI"vs"自定义 UI"

### TP-012（COMMON_UTIL）：全局红点跨页面同步
- **scenario**：场景 7
- **module**：`COMMON_UTIL`
- **precondition**：A 页面有红点
- **test_data**：玩家在 A 页面清除红点 → 切到 B 页面
- **expected**：B 页面红点同步清除
- **notes**：注意"全局状态"vs"页面状态"

### TP-013（COMMON_UTIL）：路由跳转正确
- **scenario**：场景 8
- **module**：`COMMON_UTIL`
- **precondition**：商城页注册路由 "shop"
- **test_data**：`navigate("shop", {id: 100})`
- **expected**：跳到商城页、接收 id=100
- **notes**：注意"参数序列化"

### TP-014（COMMON_UTIL）：本地存储读写
- **scenario**：场景 9
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：`set("volume", 80)` → `get("volume")` → `remove("volume")` → `get("volume")`
- **expected**：依次返回 80 → null
- **notes**：注意"持久化"vs"内存"

### TP-015（COMMON_UTIL）：剪贴板复制粘贴
- **scenario**：场景 10
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：`copy("ABC123")` → 粘贴
- **expected**：粘贴内容 = "ABC123"
- **notes**：注意"系统剪贴板"vs"应用内剪贴板"

### TP-016（COMMON_UTIL）：概率计算
- **scenario**：通用计算
- **module**：`COMMON_UTIL`
- **precondition**：概率 0.3
- **test_data**：`hit(0.3)` 调用 1000 次
- **expected**：命中 ≈ 300 次
- **notes**：注意"概率工具"vs"业务抽卡逻辑"

### TP-017（COMMON_UTIL）：单位换算
- **scenario**：通用计算
- **module**：`COMMON_UTIL`
- **precondition**：1 金币 = 100 银币
- **test_data**：`convert(1, "gold", "silver")`
- **expected**：100
- **notes**：注意汇率配置（归 CONFIG）

### TP-018（COMMON_UTIL）：数值裁剪
- **scenario**：通用计算
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：`clamp(150, 0, 100)`
- **expected**：100
- **notes**：注意"上限"vs"下限"

### TP-019（COMMON_UTIL）：跨平台兼容
- **scenario**：通用
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：iOS / Android / Windows / Mac
- **expected**：行为一致
- **notes**：注意"平台差异"（如文件路径分隔符）

### TP-020（COMMON_UTIL）：性能达标
- **scenario**：通用
- **module**：`COMMON_UTIL`
- **precondition**：无
- **test_data**：100 万次 `formatTime` 调用
- **expected**：耗时 < 1s
- **notes**：注意"性能"vs"功能"

---

## 3. 边界陷阱

### 边界 1：vs BIZ
- **混淆点**：「玩家名脱敏"」——A 测通用工具、BIZ 测业务逻辑
- **判定规则**：测"通用脱敏工具" → A；测"业务逻辑中的脱敏" → BIZ
- **实例**：脱敏工具 "1234" → "****" → A；聊天消息发送时脱敏 → BIZ

### 边界 2：vs B. 网络层
- **混淆点**：「协议"工具"」——A 测通用工具、B 测网络
- **判定规则**：测"通用加解密/序列化" → A；测"网络协议打包解包" → B
- **实例**：AES 加解密工具 → A-010；网络包 AES 加密 → B

### 边界 3：vs J. 存储+日志
- **混淆点**：「本地"存储"」——A 测通用工具、J 测存储
- **判定规则**：测"通用 localStorage" → A；测"玩家设置/登录凭证" → J
- **实例**：通用 key-value 存储 → A-014；玩家设置存档 → J-001

### 边界 4：vs K. 性能
- **混淆点**：「性能"工具"」——A 测通用工具、K 测性能
- **判定规则**：测"通用性能采样工具" → A/K（按设计）；测"性能监控组件" → K
- **实例**：FPS 监控组件 → K；通用性能 stopwatch → A

---

## 4. 验证证据

### 视觉证据
- 弹窗样式对比截图
- 红点显示截图

### 日志证据
- 工具调用日志
- 性能采样日志

### 数据证据
- 工具单测覆盖率 ≥ 80%
- 工具运行结果对照表

### 性能证据
- 100 万次调用 < 1s
- 跨平台一致
