# D. 前后台切换 / 生命周期恢复

> **子类代码**：`BG_FG_SWITCH`
> **归属模块**：`SPECIAL`
> **来源**：用户细化定义 §4「前后台切换、生命周期异常恢复」
>
> **测什么**：移动端**切后台长时间挂起**、**后台进程被杀**、**内存不足自动清理资源**、**锁屏唤醒**等生命周期异常；切回前台的**校验服务端最新数据**、同步过期状态、刷新缓存、重置临时交互状态；后台**释放渲染资源**、前台**重新加载不闪退**、丢失临时道具/buff **自动校正**。
> **不测什么**：底层进程管理框架（归 UTIL N）、UI 控件渲染（归 UI）、BIZ 业务状态保存。
> **与其他子类的差异**：D 关注"应用生命周期异常"——A 关注"业务边界"、B 关注"对抗行为"、C 关注"环境异常（弱网）"；D 是 App 生命周期，B/C/A 是业务/环境边界。

---

## 1. 典型场景

### 场景 1：切后台短时间挂起
- 业务背景：玩家按 Home 键切后台 30s
- 涉及字段/工具：app_lifecycle、bg_timestamp
- 触发动作：切后台 → 30s → 返回前台
- 验证点：返回前台后状态正确，无数据错乱

### 场景 2：切后台长时间挂起
- 业务背景：玩家切后台 8h（睡觉）
- 涉及字段/工具：bg_hang_time、expire_check
- 触发动作：切后台 8h
- 验证点：返回前台时同步服务端最新数据 + 过期资源清理

### 场景 3：后台进程被杀
- 业务背景：玩家切后台后系统杀进程
- 涉及字段/工具：process_kill、resume_state
- 触发动作：系统杀进程
- 验证点：重新启动后从服务端拉取最新状态，本地缓存可丢失

### 场景 4：内存不足自动清理
- 业务背景：玩家切后台时系统内存紧张
- 涉及字段/工具：memory_pressure、resource_release
- 触发动作：系统通知低内存
- 验证点：客户端主动释放非关键资源，回到前台按需重新加载

### 场景 5：锁屏唤醒
- 业务背景：玩家锁屏后解锁
- 涉及字段/工具：lock_state、unlock_event
- 触发动作：锁屏 5min → 解锁
- 验证点：解锁后状态正确，无卡死

### 场景 6：切回前台校验服务端数据
- 业务背景：玩家切后台期间其他玩家操作了相关数据
- 涉及字段/工具：server_state、client_state_diff
- 触发动作：切回前台
- 验证点：客户端主动拉取服务端最新数据 + 校正本地状态

### 场景 7：切回前台刷新缓存
- 业务背景：玩家切后台 1h，缓存已过期
- 涉及字段/工具：cache_ttl、cache_refresh
- 触发动作：切回前台
- 验证点：自动刷新过期缓存 + 重新拉取数据

### 场景 8：切回前台重置临时交互状态
- 业务背景：玩家切后台时打开了 Modal 弹窗
- 涉及字段/工具：modal_state、temp_state
- 触发动作：切回前台
- 验证点：临时弹窗/输入框/拖拽状态重置

### 场景 9：后台释放渲染资源
- 业务背景：玩家切后台时场景渲染暂停
- 涉及字段/工具：render_pause、gpu_release
- 触发动作：切后台
- 验证点：GPU/渲染资源释放，回到前台不卡顿

### 场景 10：前台重新加载不闪退
- 业务背景：玩家从后台切回前台
- 涉及字段/工具：scene_reload、resource_reload
- 触发动作：切回前台
- 验证点：场景/资源重新加载成功，不闪退、不卡死

### 场景 11：丢失临时道具/buff 自动校正
- 业务背景：玩家切后台时获得 buff，回前台发现 buff 消失
- 涉及字段/工具：temp_buff、server_buff
- 触发动作：切回前台
- 验证点：以服务端 buff 为准重新校正

### 场景 12：切回前台推送通知补发
- 业务背景：玩家切后台期间有未读邮件
- 涉及字段/工具：pending_mail、notification
- 触发动作：切回前台
- 验证点：未读邮件 + 推送通知补发

---

## 2. 种子测试点（TP 模板）

### TP-001（BG_FG_SWITCH）：切后台短时间返回无错乱
- **scenario**：场景 1
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家在副本战斗中
- **test_data**：按 Home 键 → 30s → 返回前台
- **expected**：副本状态正确，战斗继续，无数据丢失
- **notes**：注意"切后台" vs "切后台被杀"——后者需重新拉数据

### TP-002（BG_FG_SWITCH）：切后台长时间返回同步数据
- **scenario**：场景 2
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家在邮件界面
- **test_data**：切后台 8h → 返回前台
- **expected**：拉取服务端最新邮件列表（新增邮件可见），本地缓存刷新
- **notes**：注意"长时间" vs "短时间"——长时间需校验过期

### TP-003（BG_FG_SWITCH）：进程被杀后重新拉取
- **scenario**：场景 3
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家在战斗中
- **test_data**：切后台 → 系统杀进程 → 重启 App
- **expected**：重新登录拉取服务端最新状态，本地缓存可丢失
- **notes**：注意"被杀" vs "正常退出"——被杀需重新登录

### TP-004（BG_FG_SWITCH）：内存压力释放资源
- **scenario**：场景 4
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家切后台，内存紧张
- **test_data**：触发 onLowMemory()
- **expected**：客户端释放非关键资源（贴图/音频），关键数据保留
- **notes**：注意"非关键" vs "关键"——关键数据需持久化

### TP-005（BG_FG_SWITCH）：锁屏唤醒状态正常
- **scenario**：场景 5
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家在副本中
- **test_data**：锁屏 5min → 解锁
- **expected**：副本状态正确（未掉线、未结算）
- **notes**：注意"锁屏" vs "切后台"——锁屏可能更短

### TP-006（BG_FG_SWITCH）：切回前台校验服务端数据
- **scenario**：场景 6
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家 A 在公会界面
- **test_data**：切后台期间另一玩家 B 修改了公会名 → 切回前台
- **expected**：A 看到最新公会名（B 修改后的）+ 本地缓存更新
- **notes**：注意"切回前台校验" vs "主动轮询"——切回前台是触发点

### TP-007（BG_FG_SWITCH）：切回前台刷新过期缓存
- **scenario**：场景 7
- **module**：`BG_FG_SWITCH`
- **precondition**：客户端缓存 TTL = 1h
- **test_data**：切后台 2h → 切回前台
- **expected**：自动检测缓存过期 → 重新拉取服务端数据
- **notes**：注意"过期" vs "有效"——过期才刷新

### TP-008（BG_FG_SWITCH）：重置临时交互状态
- **scenario**：场景 8
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家打开了 Modal 弹窗 + 输入了文字
- **test_data**：切后台 → 切回前台
- **expected**：弹窗关闭 + 输入框清空（不保留临时态）
- **notes**：注意"临时态" vs "持久态"——临时态重置

### TP-009（BG_FG_SWITCH）：后台释放渲染资源
- **scenario**：场景 9
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家在 3D 场景中
- **test_data**：切后台
- **expected**：渲染线程暂停 + GPU 资源释放
- **notes**：注意"释放" vs "销毁"——释放可恢复，销毁需重新加载

### TP-010（BG_FG_SWITCH）：前台重新加载不闪退
- **scenario**：场景 10
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家在副本中
- **test_data**：切后台 5min → 切回前台
- **expected**：场景重新加载成功，不闪退、不卡死
- **notes**：注意"重新加载" vs "无缝恢复"——非关键场景可重新加载

### TP-011（BG_FG_SWITCH）：临时 buff 自动校正
- **scenario**：场景 11
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家本地显示有 5min buff
- **test_data**：切后台 10min → 切回前台
- **expected**：以服务端为准（buff 已过期或缩短）
- **notes**：注意"本地" vs "服务端"——服务端为准

### TP-012（BG_FG_SWITCH）：未读通知补发
- **scenario**：场景 12
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家有未读邮件
- **test_data**：切后台 1h → 切回前台
- **expected**：未读邮件红点 + 推送通知补发
- **notes**：注意"补发" vs "实时推送"——补发是切换时触发

### TP-013（BG_FG_SWITCH）：切后台时未完成操作保存
- **scenario**：场景 1 扩展
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家正在输入聊天
- **test_data**：切后台
- **expected**：输入内容保存到草稿（切回前台可继续）
- **notes**：注意"草稿" vs "已发送"——草稿可继续编辑

### TP-014（BG_FG_SWITCH）：切回前台时数据冲突解决
- **scenario**：场景 6 扩展
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家本地有未提交数据 + 服务端已更新
- **test_data**：切回前台
- **expected**：弹窗提示冲突（本地 vs 服务端）+ 玩家选择覆盖/取消
- **notes**：注意"冲突" vs "一致"——冲突需用户介入

### TP-015（BG_FG_SWITCH）：切回前台资源懒加载
- **scenario**：场景 10 扩展
- **module**：`BG_FG_SWITCH`
- **precondition**：切回前台
- **test_data**：打开未访问过的页面
- **expected**：按需懒加载，不一次性加载所有资源
- **notes**：注意"懒加载" vs "预加载"——按需是关键

### TP-016（BG_FG_SWITCH）：切回前台心跳恢复
- **scenario**：场景 1 扩展
- **module**：`BG_FG_SWITCH`
- **precondition**：切后台期间心跳超时
- **test_data**：切回前台
- **expected**：自动重连 + 心跳恢复
- **notes**：注意"心跳" vs "会话"——心跳是 keepalive

### TP-017（BG_FG_SWITCH）：切后台被杀通知
- **scenario**：场景 3 扩展
- **module**：`BG_FG_SWITCH`
- **precondition**：切后台期间被杀
- **test_data**：重新启动
- **expected**：客户端检测到"上次异常退出" + 提供恢复入口
- **notes**：注意"通知" vs "静默"——通知更友好

### TP-018（BG_FG_SWITCH）：锁屏期间事件累计
- **scenario**：场景 5 扩展
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家锁屏期间有事件
- **test_data**：解锁
- **expected**：事件按顺序补发，不丢失
- **notes**：注意"累计" vs "丢弃"——重要事件需累计

### TP-019（BG_FG_SWITCH）：切回前台检查版本更新
- **scenario**：场景 2 扩展
- **module**：`BG_FG_SWITCH`
- **precondition**：切后台期间服务端发布了新版本
- **test_data**：切回前台
- **expected**：检测到新版本 → 提示更新
- **notes**：注意"版本" vs "资源热更"——后者是资源更新

### TP-020（BG_FG_SWITCH）：切回前台时区变化
- **scenario**：场景 1 扩展
- **module**：`BG_FG_SWITCH`
- **precondition**：玩家跨时区
- **test_data**：切回前台
- **expected**：活动剩余时间按当前时区重新计算
- **notes**：注意"时区" vs "服务器时间"——服务器时间为准

---

## 3. 边界陷阱

### 边界 1：vs UI（页面状态）
- **混淆点**："切回前台状态重置" 看似 UI → 实际 UI 测"页面渲染状态"（如按钮置灰），D 测"应用生命周期"（App 状态）
- **判定规则**：测"页面内控件状态" → 归 UI；测"App 前后台切换/进程生命周期" → 归 SPECIAL D
- **实例**：弹窗关闭 → 归 UI（页面状态）；切后台后弹窗关闭 → 归 D（生命周期）

### 边界 2：vs BIZ（业务状态保存）
- **混淆点**："切后台状态保存" 看似 BIZ → 实际 BIZ 测"业务状态存储到服务端"，D 测"切回前台客户端状态如何恢复"
- **判定规则**：测"业务数据落库/状态机" → 归 BIZ；测"客户端状态恢复（缓存/重连/重置）" → 归 SPECIAL D
- **实例**：副本中途退出记录进度到 DB → 归 BIZ；切后台后返回查看进度 → 归 D

### 边界 3：vs UTIL N（异常兜底）
- **混淆点**："进程被杀恢复" 看似 N → 实际 N 测"崩溃捕获 + 上报"（异常兜底），D 测"被系统杀的恢复"（生命周期）
- **判定规则**：测"崩溃/异常捕获" → 归 UTIL N；测"系统主动杀进程/内存不足" → 归 SPECIAL D
- **实例**：App 崩溃后下次启动上报 → 归 N；切后台被杀后重启 App → 归 D

### 边界 4：vs C（弱网断网）
- **混淆点**："切回前台拉数据" 看似 C → 实际 C 测"网络异常时的请求处理"，D 测"切回前台触发的数据刷新"
- **判定规则**：测"网络异常处理" → 归 SPECIAL C；测"切回前台主动拉数据" → 归 SPECIAL D
- **实例**：断网时重发 → 归 C；切回前台拉最新数据 → 归 D

---

## 4. 验证证据

### 视觉证据
- 切后台 → 切回前台的 loading 提示
- 长时间挂起后邮件列表刷新
- 临时 buff 消失的提示
- 内存不足时的资源释放日志

### 日志证据
- `lifecycle.bg_to_fg` 关键词：后台切前台
- `lifecycle.process_killed` 关键词：进程被杀
- `lifecycle.low_memory` 关键词：内存不足
- `lifecycle.lock_unlock` 关键词：锁屏解锁
- `lifecycle.cache_expired` 关键词：缓存过期
- `lifecycle.data_sync` 关键词：数据同步
- `lifecycle.resource_released` 关键词：资源释放
- `lifecycle.resource_reloaded` 关键词：资源重新加载

### 数据证据
- `lifecycle_log` 表记录每次前后台切换 + 持续时长
- 切回前台后玩家数据与服务端一致
- 缓存 TTL 过期后正确刷新
- 临时 buff 以服务端为准
- 进程被杀后无未保存数据丢失

### 性能证据
- 切回前台数据刷新耗时 < 2s
- 资源重新加载耗时 < 3s
- 切后台资源释放耗时 < 500ms
- 切回前台场景恢复帧率 > 30 FPS
