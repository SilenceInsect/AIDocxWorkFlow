# M. 加密安全（底层算法）

> **子类代码**：`SECURITY`
> **归属模块**：`AUX`
> **来源**：用户细化定义 §15「加密安全辅助」
>
> **v1.6.1 变更**：**剔除风控/反作弊检测**（行为分析、异常行为识别）——风控/反作弊归 **SPECIAL 模块**（v1.10 待建）。
> 本子模板**只保留加密算法与签名底层**。
>
> **测什么**：资源加密、协议加密、本地存档加密、防篡改、签名验证、密钥管理。
> **不测什么**：账号安全（归 BIZ）、UI 验证码（归 UI）、业务风控/反作弊（归 SPECIAL）、第三方平台（归 LINK）。
> **与其他子类的差异**：M 关注"加密技术"——N 关注"异常处理"，M 是技术，N 是流程。

---

## 1. 典型场景

### 场景 1：资源加密
- 业务背景：游戏资源保护
- 涉及工具：资源加密
- 触发动作：玩家提取资源
- 验证点：资源不可直接读

### 场景 2：协议加密
- 业务背景：网络协议加密
- 涉及工具：协议加密
- 触发动作：网络包抓包
- 验证点：包内容密文

### 场景 3：本地存档加密
- 业务背景：玩家数据保护
- 涉及工具：存档加密
- 触发动作：存档文件读取
- 验证点：文件密文

### 场景 4：防篡改校验
- 业务背景：客户端防作弊
- 涉及工具：防篡改
- 触发动作：玩家改客户端
- 验证点：检测到篡改

### 场景 5：参数防篡改
- 业务背景：业务参数保护
- 涉及工具：参数签名
- 触发动作：修改请求参数
- 验证点：服务端拒绝

### 场景 6：密钥管理
- 业务背景：密钥轮换
- 涉及工具：密钥管理
- 触发动作：定期更新密钥
- 验证点：密钥生效

---

## 2. 种子测试点（TP 模板）

### TP-001（SECURITY）：资源加密 - 不可读
- **scenario**：场景 1
- **module**：`SECURITY`
- **precondition**：游戏资源
- **test_data**：用编辑器打开 .png
- **expected**：密文、不可读
- **notes**：注意"加密"vs"压缩"

### TP-002（SECURITY）：协议加密 - 抓包验证
- **scenario**：场景 2
- **module**：`SECURITY`
- **precondition**：游戏运行
- **test_data**：用 Wireshark 抓包
- **expected**：包内容密文
- **notes**：注意"明文 vs 密文"

### TP-003（SECURITY）：本地存档加密
- **scenario**：场景 3
- **module**：`SECURITY`
- **precondition**：玩家存档
- **test_data**：用编辑器打开存档
- **expected**：密文、不可读
- **notes**：注意"存档"vs"配置"

### TP-004（SECURITY）：防篡改 - 客户端修改
- **scenario**：场景 4
- **module**：`SECURITY`
- **precondition**：玩家用改端工具
- **test_data**：改客户端文件
- **expected**：检测到篡改、提示
- **notes**：注意"检测"vs"封号"

### TP-005（SECURITY）：参数签名 - 改参数拒绝
- **scenario**：场景 5
- **module**：`SECURITY`
- **precondition**：玩家抓包改参数
- **test_data**：把价格 100 改成 1
- **expected**：服务端验证签名、拒绝
- **notes**：注意"签名"vs"明文"

### TP-006（SECURITY）：密钥管理 - 轮换
- **scenario**：场景 6
- **module**：`SECURITY`
- **precondition**：定期密钥轮换
- **test_data**：密钥 v1 → v2
- **expected**：v1 失效、v2 生效
- **notes**：注意"旧密钥"vs"过渡期"

### TP-007（SECURITY）：加密算法标准
- **scenario**：场景 1
- **module**：`SECURITY`
- **precondition**：无
- **test_data**：AES-256 加密
- **expected**：符合国密标准
- **notes**：注意"AES"vs"RSA"vs"国密"

### TP-008（SECURITY）：HTTPS 强制
- **scenario**：场景 2
- **module**：`SECURITY`
- **precondition**：客户端
- **test_data**：所有网络请求
- **expected**：HTTPS、禁用 HTTP
- **notes**：注意"证书锁定"

### TP-009（SECURITY）：反调试
- **scenario**：场景 4
- **module**：`SECURITY`
- **precondition**：玩家用调试器
- **test_data**：附加到进程
- **expected**：检测到、退出
- **notes**：注意"反调试"vs"反作弊"

### TP-010（SECURITY）：代码混淆
- **scenario**：场景 1
- **module**：`SECURITY`
- **precondition**：客户端代码
- **test_data**：反编译
- **expected**：难以读懂
- **notes**：注意"混淆"vs"加密"

### TP-011（SECURITY）：签名验证完整性
- **scenario**：场景 5
- **module**：`SECURITY`
- **precondition**：业务请求
- **test_data**：篡改请求
- **expected**：签名验证失败
- **notes**：注意"签名"vs"加密"

### TP-012（SECURITY）：密钥存储安全
- **scenario**：场景 6
- **module**：`SECURITY`
- **precondition**：密钥存储
- **test_data**：逆向工程
- **expected**：密钥不暴露
- **notes**：注意"硬编码"vs"动态获取"

---

## 3. 边界陷阱

### 边界 1：vs B. 网络层
- **混淆点**：「协议"加密"」——B 测传输、M 测加密
- **判定规则**：测"协议打包解包" → B；测"加密算法本身" → M
- **实例**：协议字节流打包 → B；AES-256 加密 → M

### 边界 2：vs SPECIAL
- **混淆点**：「反"作弊"」——M 测加密、SPECIAL 测反作弊
- **判定规则**：测"加密/防篡改" → M；测"反作弊检测" → SPECIAL
- **实例**：客户端防篡改 → M；异常行为检测 → SPECIAL

### 边界 3：vs BIZ
- **混淆点**：「风控"安全"」——M 测加密、BIZ 测业务安全
- **判定规则**：测"加密技术" → M；测"账号安全策略" → BIZ
- **实例**：参数签名 → M；账号风控 → BIZ

### 边界 4：vs J. 存储+日志
- **混淆点**：「存档"加密"」——M 测加密、J 测存储
- **判定规则**：测"存档读写" → J；测"加密算法" → M
- **实例**：玩家设置存档 → J；AES-256 加密 → M

---

## 4. 验证证据

### 视觉证据
- 加密前后文件对比
- 抓包内容截图

### 日志证据
- 加密/解密日志
- 篡改检测日志
- 密钥轮换日志

### 数据证据
- 加密算法说明文档
- 密钥版本记录
- 篡改事件表

### 性能证据
- 加密/解密耗时 < 1ms
- 密钥轮换不影响业务
