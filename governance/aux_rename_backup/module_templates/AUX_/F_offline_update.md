# F. 离线资源 + 版本更新

> **子类代码**：`OFFLINE_UPDATE`
> **归属模块**：`UTIL`
> **来源**：用户细化定义 §6「离线资源」+ §13「版本更新/热更辅助」（合并）
>
> **测什么**：离线包下载、断点续传、空间不足、离线模式、整包/增量更新、版本校验。
> **不测什么**：资源运行时（归 D）、网络层（归 B）、配置热更（归 CONFIG-D）。
> **与其他子类的差异**：F 关注"下载/更新流程"——D 关注"运行时资源"，B 关注"网络传输"。

---

## 1. 典型场景

### 场景 1：离线包下载
- 业务背景：玩家 WiFi 下预下载
- 触发动作：触发离线包下载
- 验证点：下载成功

### 场景 2：断点续传
- 业务背景：下载中断
- 触发动作：网络断开 → 恢复
- 验证点：从断点继续

### 场景 3：后台静默下载
- 业务背景：玩家切到后台
- 触发动作：进入后台
- 验证点：继续下载（省电模式）

### 场景 4：空间不足校验
- 业务背景：玩家存储空间不足
- 触发动作：下载 500MB 包
- 验证点：提示空间不足

### 场景 5：离线模式
- 业务背景：网络断开
- 触发动作：玩家无网络
- 验证点：本地界面/缓存可玩

### 场景 6：资源修复
- 业务背景：资源损坏
- 触发动作：MD5 校验失败
- 验证点：自动重新下载

### 场景 7：损坏资源自动重下
- 业务背景：游戏崩溃后启动
- 触发动作：资源校验
- 验证点：损坏资源自动重下

### 场景 8：离线包版本兼容
- 业务背景：旧版本客户端
- 触发动作：旧客户端下载新离线包
- 验证点：兼容处理

### 场景 9：整包更新
- 业务背景：新版本发布
- 触发动作：玩家启动客户端
- 验证点：提示整包更新

### 场景 10：增量热更
- 业务背景：补丁发布
- 触发动作：玩家启动客户端
- 验证点：下载增量包

### 场景 11：渠道分包更新
- 业务背景：iOS/Android/Web
- 触发动作：玩家启动
- 验证点：按渠道更新

### 场景 12：版本校验
- 业务背景：版本不匹配
- 触发动作：旧版本访问新服
- 验证点：强制更新

### 场景 13：更新弹窗
- 业务背景：新版本可用
- 触发动作：启动客户端
- 验证点：弹出更新提示

### 场景 14：更新失败修复
- 业务背景：更新失败
- 触发动作：增量包损坏
- 验证点：回滚到旧版本

---

## 2. 种子测试点（TP 模板）

### TP-001（OFFLINE_UPDATE）：离线包下载成功
- **scenario**：场景 1
- **module**：`OFFLINE_UPDATE`
- **precondition**：WiFi 环境、空间充足
- **test_data**：下载 500MB 离线包
- **expected**：下载成功、可玩
- **notes**：注意"WiFi"vs"移动网络"判定

### TP-002（OFFLINE_UPDATE）：断点续传
- **scenario**：场景 2
- **module**：`OFFLINE_UPDATE`
- **precondition**：下载 500MB 离线包
- **test_data**：下载到 300MB 断开 → 5min 后恢复
- **expected**：从 300MB 继续下载、不重头
- **notes**：注意"分块"vs"整包"

### TP-003（OFFLINE_UPDATE）：后台静默下载
- **scenario**：场景 3
- **module**：`OFFLINE_UPDATE`
- **precondition**：离线包下载中
- **test_data**：玩家切到后台
- **expected**：继续下载（按设计决定省电模式）
- **notes**：注意"省电"vs"全速"

### TP-004（OFFLINE_UPDATE）：空间不足拦截
- **scenario**：场景 4
- **module**：`OFFLINE_UPDATE`
- **precondition**：手机剩余 200MB
- **test_data**：下载 500MB 离线包
- **expected**：提示"空间不足"、不下载
- **notes**：注意"提示"vs"自动清理"

### TP-005（OFFLINE_UPDATE）：离线模式启动
- **scenario**：场景 5
- **module**：`OFFLINE_UPDATE`
- **precondition**：玩家下载过离线包
- **test_data**：飞行模式启动客户端
- **expected**：进入离线模式、可玩单机内容
- **notes**：注意"单机"vs"网游"内容

### TP-006（OFFLINE_UPDATE）：离线模式不可用
- **scenario**：场景 5
- **module**：`OFFLINE_UPDATE`
- **precondition**：未下载离线包
- **test_data**：飞行模式启动
- **expected**：提示"无网络"
- **notes**：注意"网络不可用"vs"已离线"

### TP-007（OFFLINE_UPDATE）：资源 MD5 校验
- **scenario**：场景 6
- **module**：`OFFLINE_UPDATE`
- **precondition**：离线包下载完成
- **test_data**：MD5 校验
- **expected**：MD5 一致
- **notes**：注意"完整"vs"分块"

### TP-008（OFFLINE_UPDATE）：资源损坏自动重下
- **scenario**：场景 7
- **module**：`OFFLINE_UPDATE`
- **precondition**：游戏崩溃前
- **test_data**：游戏崩溃 → 启动
- **expected**：资源校验、损坏资源自动重下
- **notes**：注意"自动"vs"提示"

### TP-009（OFFLINE_UPDATE）：离线包版本兼容
- **scenario**：场景 8
- **module**：`OFFLINE_UPDATE`
- **precondition**：旧版客户端 v1.0
- **test_data**：尝试下载 v2.0 离线包
- **expected**：拒绝下载、提示更新客户端
- **notes**：注意"客户端版本"vs"离线包版本"

### TP-010（OFFLINE_UPDATE）：整包更新
- **scenario**：场景 9
- **module**：`OFFLINE_UPDATE`
- **precondition**：新版本 v2.0
- **test_data**：旧 v1.0 启动
- **expected**：提示整包更新（按设计）
- **notes**：注意"强制"vs"可选"更新

### TP-011（OFFLINE_UPDATE）：增量热更
- **scenario**：场景 10
- **module**：`OFFLINE_UPDATE`
- **precondition**：补丁包 50MB
- **test_data**：玩家启动
- **expected**：下载增量包、应用补丁
- **notes**：注意"增量"vs"全量"

### TP-012（OFFLINE_UPDATE）：渠道分包更新
- **scenario**：场景 11
- **module**：`OFFLINE_UPDATE`
- **precondition**：iOS App Store / Android 商店
- **test_data**：iOS 玩家 vs Android 玩家
- **expected**：按渠道包更新
- **notes**：注意"商店"vs"自建 CDN"

### TP-013（OFFLINE_UPDATE）：版本校验 - 客户端太旧
- **scenario**：场景 12
- **module**：`OFFLINE_UPDATE`
- **precondition**：服务端要求最低 v1.5
- **test_data**：v1.0 客户端访问
- **expected**：强制更新
- **notes**：注意"强制"vs"灰度强制"

### TP-014（OFFLINE_UPDATE）：更新弹窗可关闭
- **scenario**：场景 13
- **module**：`OFFLINE_UPDATE`
- **precondition**：可选更新
- **test_data**：玩家点"稍后"
- **expected**：弹窗关闭、玩家继续玩
- **notes**：注意"可选"vs"强制"

### TP-015（OFFLINE_UPDATE）：更新失败回滚
- **scenario**：场景 14
- **module**：`OFFLINE_UPDATE`
- **precondition**：增量包损坏
- **test_data**：下载失败 → 应用失败
- **expected**：回滚到旧版本、可玩
- **notes**：注意"回滚"vs"卡死"

### TP-016（OFFLINE_UPDATE）：分块下载
- **scenario**：场景 1
- **module**：`OFFLINE_UPDATE`
- **precondition**：离线包 500MB
- **test_data**：分块下载（每块 5MB）
- **expected**：分块下载、可中断可恢复
- **notes**：注意"分块"vs"整包"

---

## 3. 边界陷阱

### 边界 1：vs D. 资源管理
- **混淆点**：「资源"下载"」——D 测运行时资源、F 测离线
- **判定规则**：测"运行时资源加载/释放" → D；测"离线包下载" → F
- **实例**：场景资源加载 → D-001；离线包下载 → F-001

### 边界 2：vs B. 网络层
- **混淆点**：「下载"网络"」——B 测网络、F 测下载
- **判定规则**：测"网络传输/重连" → B；测"下载流程/版本" → F
- **实例**：断线重连 → B-003；断点续传 → F-002

### 边界 3：vs CONFIG-D
- **混淆点**：「配置"热更"」——CONFIG-D 测配置、F 测包
- **判定规则**：测"配置文件热更" → CONFIG-D；测"游戏包/离线包更新" → F
- **实例**：道具表热更 → CONFIG-D；客户端版本更新 → F-010

### 边界 4：vs N. 异常兜底
- **混淆点**：「更新"失败"」——F 测更新流程、N 测异常
- **判定规则**：测"下载/更新流程" → F；测"失败重试/兜底" → N
- **实例**：更新失败回滚 → F-015；失败重试 3 次 → N

---

## 4. 验证证据

### 视觉证据
- 下载进度条截图
- 更新弹窗截图
- 空间不足提示

### 日志证据
- 下载开始/结束日志
- 断点续传日志
- 版本校验日志
- 更新失败日志

### 数据证据
- 下载进度（已下载/总大小）
- 包 MD5
- 玩家版本号

### 性能证据
- 下载速度
- 断点续传恢复 < 1s
- 资源校验 < 5s
