# J. 本地持久化存储

> **子类代码**：`LOCAL_STORAGE`
> **归属模块**：`AUX`
> **来源**：用户细化定义 §10「本地持久存储辅助」（**§11 日志与埋点已迁出**）
>
> **v1.6.1 变更**：剔除原"日志/埋点"部分（日志/埋点/崩溃上报由 **LOG 模块**承接）——本子模板**只保留本地持久化存储**。
>
> **测什么**：本地存档、玩家设置、本地账号缓存、隐私设置、存储损坏兜底。
> **不测什么**：运行时缓存（归 C）、日志/埋点（归 LOG）、业务数据流（归 BIZ）、崩溃捕获（归 N）。

---

## 1. 典型场景

### 场景 1：本地存档
- 业务背景：玩家设置存档
- 触发动作：保存音量
- 验证点：重启后保留

### 场景 2：玩家设置
- 业务背景：音量、画质、帧率
- 触发动作：调整设置
- 验证点：保存并恢复

### 场景 3：登录账号缓存
- 业务背景：自动登录
- 触发动作：玩家上次登录
- 验证点：下次启动自动登录

### 场景 4：隐私设置存储
- 业务背景：拒绝个性化推荐
- 触发动作：玩家拒绝
- 验证点：下次启动仍是拒绝

### 场景 5：多账号本地隔离
- 业务背景：多账号切换
- 触发动作：账号 A 切换到账号 B
- 验证点：A 和 B 设置隔离

### 场景 6：存储损坏兜底
- 业务背景：存档文件损坏
- 触发动作：存档读取失败
- 验证点：兜底默认值、不崩溃

---

## 2. 种子测试点（TP 模板）

### TP-001（LOCAL_STORAGE）：本地存档
- **scenario**：场景 1
- **module**：`LOCAL_STORAGE`
- **precondition**：无
- **test_data**：设置音量 80 → 重启
- **expected**：音量仍为 80
- **notes**：注意"LocalStorage"vs"IndexedDB"vs"文件"

### TP-002（LOCAL_STORAGE）：玩家设置 - 画质
- **scenario**：场景 2
- **module**：`LOCAL_STORAGE`
- **precondition**：默认画质"高"
- **test_data**：调整为"低" → 重启
- **expected**：画质仍为"低"
- **notes**：注意"画质"vs"分辨率"

### TP-003（LOCAL_STORAGE）：玩家设置 - 操作布局
- **scenario**：场景 2
- **module**：`LOCAL_STORAGE`
- **precondition**：手游
- **test_data**：调整摇杆位置 → 重启
- **expected**：摇杆位置保留
- **notes**：注意"自定义布局"

### TP-004（LOCAL_STORAGE）：登录账号缓存
- **scenario**：场景 3
- **module**：`LOCAL_STORAGE`
- **precondition**：玩家登录过
- **test_data**：重启客户端
- **expected**：自动登录到上次账号
- **notes**：注意"自动登录"vs"手动登录"

### TP-005（LOCAL_STORAGE）：隐私设置存储
- **scenario**：场景 4
- **module**：`LOCAL_STORAGE`
- **precondition**：玩家拒绝个性化推荐
- **test_data**：重启客户端
- **expected**：设置仍是拒绝
- **notes**：注意"隐私"vs"个性化"

### TP-006（LOCAL_STORAGE）：多账号本地隔离
- **scenario**：场景 5
- **module**：`LOCAL_STORAGE`
- **precondition**：账号 A 音量 80、账号 B 音量 50
- **test_data**：A 登录 → 切换到 B
- **expected**：B 音量 50
- **notes**：注意"本地隔离"vs"云端"

### TP-007（LOCAL_STORAGE）：存储损坏兜底
- **scenario**：场景 6
- **module**：`LOCAL_STORAGE`
- **precondition**：存档文件损坏
- **test_data**：读取存档
- **expected**：兜底默认值、不崩溃
- **notes**：注意"重置"vs"修复"

### TP-008（LOCAL_STORAGE）：存储加密
- **scenario**：场景 1
- **module**：`LOCAL_STORAGE`
- **precondition**：本地存档含敏感信息
- **test_data**：存档文件
- **expected**：加密存储
- **notes**：与 M-005 配合

### TP-009（LOCAL_STORAGE）：存储空间监控
- **scenario**：场景 1
- **module**：`LOCAL_STORAGE`
- **precondition**：玩家设置存档
- **test_data**：观察存储空间
- **expected**：存储空间用尽时清理或提示
- **notes**：注意"自动清理"vs"提示"

### TP-010（LOCAL_STORAGE）：跨设备同步
- **scenario**：场景 2
- **module**：`LOCAL_STORAGE`
- **precondition**：玩家在多设备登录
- **test_data**：A 设备设置 → B 设备登录
- **expected**：云端同步、本地生效
- **notes**：注意"云端"vs"本地"

---

## 3. 边界陷阱

### 边界 1：vs C. 缓存层
- **混淆点**：「本地"存储"」——C 测缓存、J 测持久化
- **判定规则**：测"运行时缓存（可丢）" → C；测"持久化存档" → J
- **实例**：商品列表缓存 → C；玩家设置存档 → J

### 边界 2：vs LOG 模块（v1.8+）
- **混淆点**：「日志"存储"」——J 测存储、LOG 测日志
- **判定规则**：测"存档读写" → J；测"日志文件/埋点上报" → LOG
- **实例**：玩家设置存档 → J-001；崩溃日志文件 → LOG

### 边界 3：vs M. 加密安全
- **混淆点**：「存档"加密"」——J 测存储、M 测加密
- **判定规则**：测"存档读写" → J；测"加密算法" → M
- **实例**：玩家设置存档 → J；AES-256 加密 → M

### 边界 4：vs N. 异常兜底
- **混淆点**：「存储"损坏"」——J 测兜底、N 测异常
- **判定规则**：测"存储损坏兜底" → J；测"全局崩溃捕获" → N
- **实例**：存档损坏重置 → J-007；游戏崩溃 → N

---

## 4. 验证证据

### 视觉证据
- 设置界面截图

### 日志证据
- 存档读写日志

### 数据证据
- 存档文件
- 存储空间统计

### 性能证据
- 存档读写 < 100ms
- 加密不影响性能

---

## 5. 迁移说明（v1.6 → v1.6.1）

**原 v1.6 的 J_storage_log 含两类内容**：

| 旧内容 | 新位置 |
|---|---|
| 本地存档、玩家设置、隐私设置、多账号 | **J_storage.md（当前文件）** |
| 日志采集、日志分级、崩溃堆栈、用户埋点、日志导出 | **LOG 模块**（v1.8 待建） |
| 埋点校验脚本 | **LOG 模块**（v1.8 待建） |
| 存储加密（存档视角）| **J_storage.md TP-008**（保留）+ **M_security.md**（加密算法）|

**新增的子模板**：
- 暂无（LOG 模块待 v1.8 由其他 Agent 接手）
- 临时占位：`J_log_moved_to_LOG.md` 记录迁移去向
