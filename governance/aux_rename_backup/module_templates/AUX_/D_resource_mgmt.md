# D. 资源管理

> **子类代码**：`RESOURCE_MGMT`
> **归属模块**：`UTIL`
> **来源**：用户细化定义 §4「资源管理」
>
> **测什么**：资源加载、生命周期、引用计数、内存释放、资源分包、资源校验。
> **不测什么**：网络下载（归 B/F）、业务逻辑（归 BIZ）、UI 渲染（归 UI）。
> **与其他子类的差异**：D 关注"资源生命周期"——C 关注"数据缓存"，E 关注"换算"。

---

## 1. 典型场景

### 场景 1：异步加载
- 业务背景：场景资源
- 触发动作：进入新场景
- 验证点：异步加载、不卡主线程

### 场景 2：预加载
- 业务背景：关卡预加载
- 触发动作：进入战斗前预加载
- 验证点：战斗时无加载卡顿

### 场景 3：分块加载
- 业务背景：大资源
- 触发动作：边玩边下
- 验证点：分块下载、内存可控

### 场景 4：加载优先级
- 业务背景：多资源同时加载
- 触发动作：核心资源 vs 装饰资源
- 验证点：核心资源优先

### 场景 5：资源队列
- 业务背景：连续场景切换
- 触发动作：5 个场景资源依次加载
- 验证点：队列管理、不乱序

### 场景 6：引用计数
- 业务背景：资源引用
- 触发动作：A 加载 → A 释放
- 验证点：引用计数 = 0 时释放

### 场景 7：自动释放
- 业务背景：切场景
- 触发动作：旧场景资源释放
- 验证点：内存不暴涨

### 场景 8：内存泄漏
- 业务背景：长时间运行
- 触发动作：连续切场景 100 次
- 验证点：内存稳定、不持续增长

### 场景 9：资源完整性校验
- 业务背景：资源下载完成
- 触发动作：MD5 校验
- 验证点：MD5 一致

### 场景 10：缺失资源占位
- 业务背景：资源缺失
- 触发动作：图标加载失败
- 验证点：占位图、不空白

### 场景 11：热更资源校验
- 业务背景：热更包下载
- 触发动作：校验资源完整性
- 验证点：损坏资源自动重下

### 场景 12：资源分包
- 业务背景：首包 vs 资源包
- 触发动作：首包安装
- 验证点：分包下载、可断点续传

---

## 2. 种子测试点（TP 模板）

### TP-001（RESOURCE_MGMT）：异步加载
- **scenario**：场景 1
- **module**：`RESOURCE_MGMT`
- **precondition**：场景资源未加载
- **test_data**：进入新场景
- **expected**：异步加载、不阻塞主线程
- **notes**：用 Performance 面板验证

### TP-002（RESOURCE_MGMT）：预加载生效
- **scenario**：场景 2
- **module**：`RESOURCE_MGMT`
- **precondition**：玩家在战斗前
- **test_data**：预加载战斗场景
- **expected**：战斗时无加载卡顿
- **notes**：注意"预加载"vs"按需加载"

### TP-003（RESOURCE_MGMT）：分块加载
- **scenario**：场景 3
- **module**：`RESOURCE_MGMT`
- **precondition**：大场景资源 500MB
- **test_data**：玩家边走边下
- **expected**：分块下载、单块 < 50MB
- **notes**：注意"边下边玩"vs"全部下完"

### TP-004（RESOURCE_MGMT）：加载优先级
- **scenario**：场景 4
- **module**：`RESOURCE_MGMT`
- **precondition**：10 个资源同时加载
- **test_data**：核心资源（角色）+ 装饰资源（粒子）
- **expected**：核心资源先加载完成
- **notes**：注意"优先级"配置

### TP-005（RESOURCE_MGMT）：加载队列顺序
- **scenario**：场景 5
- **module**：`RESOURCE_MGMT`
- **precondition**：5 个资源入队
- **test_data**：资源 A → B → C → D → E
- **expected**：按 A → B → C → D → E 顺序加载
- **notes**：注意"队列"vs"并行"

### TP-006（RESOURCE_MGMT）：资源并发数限制
- **scenario**：场景 5
- **module**：`RESOURCE_MGMT`
- **precondition**：100 个资源入队
- **test_data**：观察并发数
- **expected**：并发数 ≤ N（按设计，如 3）
- **notes**：注意"并发限制"vs"全部并发"

### TP-007（RESOURCE_MGMT）：引用计数增减
- **scenario**：场景 6
- **module**：`RESOURCE_MGMT`
- **precondition**：资源 X 引用数 = 0
- **test_data**：A 加载 X → 引用数 = 1
- **expected**：引用数 = 1
- **notes**：注意"强引用"vs"弱引用"

### TP-008（RESOURCE_MGMT）：引用计数归零释放
- **scenario**：场景 6
- **module**：`RESOURCE_MGMT`
- **precondition**：资源 X 引用数 = 1
- **test_data**：A 释放 X → 引用数 = 0
- **expected**：资源自动释放
- **notes**：注意"立即释放"vs"延迟释放"

### TP-009（RESOURCE_MGMT）：切场景自动释放
- **scenario**：场景 7
- **module**：`RESOURCE_MGMT`
- **precondition**：场景 A 资源 100MB
- **test_data**：切到场景 B
- **expected**：场景 A 资源释放、内存回到基线
- **notes**：注意"释放"vs"保留"

### TP-010（RESOURCE_MGMT）：长时间运行内存稳定
- **scenario**：场景 8
- **module**：`RESOURCE_MGMT`
- **precondition**：无
- **test_data**：连续切场景 100 次
- **expected**：内存稳定（±5%）
- **notes**：注意"内存泄漏"检测

### TP-011（RESOURCE_MGMT）：资源 MD5 校验
- **scenario**：场景 9
- **module**：`RESOURCE_MGMT`
- **precondition**：资源下载完成
- **test_data**：MD5 校验
- **expected**：MD5 与预期一致
- **notes**：注意"完整资源"vs"分块资源"

### TP-012（RESOURCE_MGMT）：资源缺失占位
- **scenario**：场景 10
- **module**：`RESOURCE_MGMT`
- **precondition**：图标 URL 失效
- **test_data**：加载失败
- **expected**：占位图显示、不空白
- **notes**：与 UI-D 配合

### TP-013（RESOURCE_MGMT）：热更资源损坏重下
- **scenario**：场景 11
- **module**：`RESOURCE_MGMT`
- **precondition**：热更包下载完成
- **test_data**：MD5 校验失败
- **expected**：自动重新下载
- **notes**：注意"自动重试"vs"提示用户"

### TP-014（RESOURCE_MGMT）：资源分包下载
- **scenario**：场景 12
- **module**：`RESOURCE_MGMT`
- **precondition**：首包 100MB + 资源包 500MB
- **test_data**：玩家只下载首包
- **expected**：首包可玩、按需下载资源包
- **notes**：注意"分包策略"

### TP-015（RESOURCE_MGMT）：资源解压
- **scenario**：场景 12
- **module**：`RESOURCE_MGMT`
- **precondition**：资源包已下载
- **test_data**：解压资源
- **expected**：解压成功、可加载
- **notes**：注意"解压"vs"运行时解压"

### TP-016（RESOURCE_MGMT）：资源分包校验
- **scenario**：场景 12
- **module**：`RESOURCE_MGMT`
- **precondition**：资源包损坏
- **test_data**：解压失败
- **expected**：自动重下、不卡玩家
- **notes**：注意"自动重试"次数

### TP-017（RESOURCE_MGMT）：资源释放时机
- **scenario**：场景 7
- **module**：`RESOURCE_MGMT`
- **precondition**：资源有引用
- **test_data**：观察释放时机
- **expected**：引用为 0 时立即释放（按设计）
- **notes**：注意"立即"vs"GC 时机"

---

## 3. 边界陷阱

### 边界 1：vs C. 缓存层
- **混淆点**：「图片"缓存"」——C 测通用缓存、D 测资源
- **判定规则**：测"通用 key-value 缓存" → C；测"图片资源加载/释放" → D
- **实例**：玩家信息缓存 → C-002；图标资源管理 → D-003

### 边界 2：vs B. 网络层
- **混淆点**：「资源"下载"」——B 测网络、D 测资源
- **判定规则**：测"网络下载/重试" → B；测"资源加载/释放" → D
- **实例**：断点续传 → F；资源加载队列 → D-005

### 边界 3：vs F. 离线/版本更新
- **混淆点**：「热更"资源"」——D 测运行时资源、F 测离线包
- **判定规则**：测"运行时资源加载/释放" → D；测"离线包下载/更新" → F
- **实例**：资源引用计数 → D-007；首包下载 → F-014

### 边界 4：vs UI
- **混淆点**：「资源"渲染"」——D 测资源、UI 测渲染
- **判定规则**：测"资源加载/释放" → D；测"资源渲染展示" → UI
- **实例**：图标资源加载 → D-001；图标渲染 → UI

---

## 4. 验证证据

### 视觉证据
- 资源加载进度条
- 资源占位截图

### 日志证据
- 资源加载日志
- 资源释放日志
- 引用计数日志
- 内存监控日志

### 数据证据
- 内存快照对比
- 资源 MD5
- 加载耗时统计

### 性能证据
- 加载耗时 < 5s
- 内存无泄漏
- CPU 占用 < 30%
