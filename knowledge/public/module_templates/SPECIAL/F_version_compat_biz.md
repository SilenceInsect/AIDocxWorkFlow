# F. 兼容类异常（新旧版本 / 跨版本）

> **子类代码**：`VERSION_COMPAT_BIZ`
> **归属模块**：`SPECIAL`
> **来源**：用户细化定义 §6「兼容类异常场景」（原定义缺失补充）
>
> **测什么**：**新旧版本客户端不兼容**、**旧端访问新功能**、**新端读取旧配置**、**低版本客户端非法功能入口拦截**、**数据兼容兜底**——版本回退、配置降级、协议升级后老客户端兜底逻辑。
> **不测什么**：配置表字段合法性（归 CONFIG）、通用业务流程（归 BIZ）、灰度/AB 测试（归 LINK）。
> **与其他子类的差异**：F 关注"版本间兼容"——A 关注"业务边界"、G 关注"环境/渠道"、H 关注"合规"；F 是版本兼容，G 是环境兼容，H 是法规兼容。

---

## 1. 典型场景

### 场景 1：旧客户端访问新功能
- 业务背景：服务端上线新功能"X 副本"，玩家客户端是旧版
- 涉及字段/工具：client_version、feature_flag
- 触发动作：玩家客户端收到新功能推送
- 验证点：旧端不显示新功能入口 + 服务端拒绝

### 场景 2：新端读取旧配置
- 业务背景：客户端升级后，配置表还未更新
- 涉及字段/工具：config_version、config_fallback
- 触发动作：新端读取旧配置
- 验证点：默认配置兜底 + 无 NPE

### 场景 3：旧端读取新协议
- 业务背景：服务端协议升级
- 涉及字段/工具：protocol_version、protocol_compat
- 触发动作：旧端发新协议
- 验证点：服务端协议版本校验 + 拒绝/降级

### 场景 4：低版本功能入口拦截
- 业务背景：某功能要求客户端 V2.0+
- 涉及字段/工具：min_client_version、entry_block
- 触发动作：V1.0 客户端访问入口
- 验证点：入口置灰 + 提示"请升级客户端"

### 场景 5：服务端版本回退
- 业务背景：服务端从 V3 回退到 V2
- 涉及字段/工具：server_rollback、protocol_fallback
- 触发动作：运营回退
- 验证点：V2 客户端可继续访问 + V3 客户端降级

### 场景 6：资源热更缺失
- 业务背景：客户端热更资源缺失
- 涉及字段/工具：resource_missing、fallback_asset
- 触发动作：客户端发现资源缺失
- 验证点：使用占位资源 + 提示更新

### 场景 7：协议字段缺失
- 业务背景：新端协议新增了字段
- 涉及字段/工具：protocol_field、default_value
- 触发动作：服务端未升级
- 验证点：服务端忽略新字段 + 默认值兜底

### 场景 8：低版本功能不兼容
- 业务背景：某副本要求 V2 客户端
- 涉及字段/工具：feature_compatibility、entry_hide
- 触发动作：V1 客户端访问
- 验证点：入口消失 + 服务端拒绝

### 场景 9：旧存档读取
- 业务背景：玩家用 V1 存档进入 V2 客户端
- 涉及字段/工具：save_migration、data_upgrade
- 触发动作：V2 客户端读取 V1 存档
- 验证点：自动迁移 + 数据完整

### 场景 10：旧数据格式兼容
- 业务背景：服务端数据库格式升级
- 涉及字段/工具：db_migration、data_convert
- 触发动作：读取旧数据
- 验证点：自动转换 + 业务可用

### 场景 11：协议号已废弃
- 业务背景：旧协议号已废弃
- 涉及字段/工具：deprecated_protocol、protocol_redirect
- 触发动作：客户端发废弃协议
- 验证点：返回 ERR_PROTOCOL_DEPRECATED + 引导新协议

### 场景 12：资源版本不匹配
- 业务背景：客户端资源版本与服务端不一致
- 涉及字段/工具：resource_version、sync_required
- 触发动作：客户端启动
- 验证点：提示资源更新 + 阻塞游戏

---

## 2. 种子测试点（TP 模板）

### TP-001（VERSION_COMPAT_BIZ）：旧端访问新功能
- **scenario**：场景 1
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：服务端上线新副本"V2 深渊"，玩家客户端是 V1.5
- **test_data**：V1.5 客户端尝试进入 V2 深渊
- **expected**：服务端返回 ERR_FEATURE_NOT_AVAILABLE；客户端入口隐藏或置灰
- **notes**：注意"隐藏" vs "置灰"——置灰保留入口给玩家看

### TP-002（VERSION_COMPAT_BIZ）：新端读取旧配置
- **scenario**：场景 2
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：客户端升级 V2，配置表未更新（仍是 V1 配置）
- **test_data**：V2 客户端读取 config.json
- **expected**：默认值兜底 + 提示"配置已过期，请重新下载"
- **notes**：注意"兜底" vs "崩溃"——必须兜底

### TP-003（VERSION_COMPAT_BIZ）：旧端发新协议
- **scenario**：场景 3
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：服务端协议升级到 V2（新增字段）
- **test_data**：V1 客户端发 V1 协议
- **expected**：服务端按 V1 协议处理 + 新字段默认空 + 业务可用
- **notes**：注意"协议升级" vs "协议重写"——升级是兼容的

### TP-004（VERSION_COMPAT_BIZ）：低版本功能拦截
- **scenario**：场景 4
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：某功能要求 V2.0+ 客户端
- **test_data**：V1.0 客户端点击入口
- **expected**：入口置灰 + 提示"请升级到 V2.0+"；服务端拒绝
- **notes**：注意"客户端拦截" vs "服务端拦截"——服务端必须独立校验

### TP-005（VERSION_COMPAT_BIZ）：服务端版本回退
- **scenario**：场景 5
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：服务端 V3 回退到 V2
- **test_data**：V2 客户端继续访问
- **expected**：V2 客户端正常使用；V3 客户端降级（部分功能不可用）
- **notes**：注意"回退" vs "升级"——回退是回到旧版本

### TP-006（VERSION_COMPAT_BIZ）：资源缺失兜底
- **scenario**：场景 6
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：客户端热更资源缺失（如 icon.png）
- **test_data**：访问使用该 icon 的页面
- **expected**：使用占位资源 + 提示"资源已损坏，请重新下载"
- **notes**：注意"占位" vs "崩溃"——必须占位

### TP-007（VERSION_COMPAT_BIZ）：新协议字段忽略
- **scenario**：场景 7
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：服务端 V1 协议不识别 V2 新增字段 `player_title`
- **test_data**：V2 客户端发 V2 协议（含 player_title）
- **expected**：服务端忽略 player_title + 按 V1 处理 + 业务正常
- **notes**：注意"忽略" vs "拒绝"——忽略是向前兼容

### TP-008（VERSION_COMPAT_BIZ）：低版本副本入口
- **scenario**：场景 8
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：副本要求 V2 客户端
- **test_data**：V1 客户端访问副本入口
- **expected**：入口消失/置灰 + 服务端 ERR_CLIENT_VERSION
- **notes**：注意"消失" vs "置灰"——保留入口更友好

### TP-009（VERSION_COMPAT_BIZ）：存档自动迁移
- **scenario**：场景 9
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：玩家 V1 存档（无新字段）登录 V2 客户端
- **test_data**：V2 客户端读取 V1 存档
- **expected**：自动迁移（V1 存档 + V2 默认值）+ 数据完整
- **notes**：注意"迁移" vs "重置"——迁移保留数据

### TP-010（VERSION_COMPAT_BIZ）：数据库迁移
- **scenario**：场景 10
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：DB schema 升级（新增字段）
- **test_data**：读取旧数据
- **expected**：自动转换 + 业务可用 + 旧数据无丢失
- **notes**：注意"迁移" vs "删除"——迁移保留旧数据

### TP-011（VERSION_COMPAT_BIZ）：废弃协议号
- **scenario**：场景 11
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：协议 1000 已废弃
- **test_data**：客户端发 protocol_id=1000
- **expected**：返回 ERR_PROTOCOL_DEPRECATED + 推荐新协议 1001
- **notes**：注意"废弃" vs "删除"——废弃保留兼容期

### TP-012（VERSION_COMPAT_BIZ）：资源版本不匹配
- **scenario**：场景 12
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：客户端资源版本 = 1.0，服务端要求 1.5
- **test_data**：客户端启动
- **expected**：提示资源更新 + 阻塞游戏（强制更新）
- **notes**：注意"提示" vs "强制"——重要资源强制

### TP-013（VERSION_COMPAT_BIZ）：协议号不存在
- **scenario**：场景 11 扩展
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：客户端发不存在的协议 9999
- **test_data**：发 protocol_id=9999
- **expected**：返回 ERR_UNKNOWN_PROTOCOL + 引导更新
- **notes**：注意"不存在" vs "废弃"——前者是协议号错误

### TP-014（VERSION_COMPAT_BIZ）：配置降级
- **scenario**：场景 2 扩展
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：新配置 V2 包含 V1 不识别的字段
- **test_data**：V1 客户端读取 V2 配置
- **expected**：V1 客户端忽略新字段 + 按 V1 配置运行
- **notes**：注意"降级" vs "崩溃"——降级保留可用性

### TP-015（VERSION_COMPAT_BIZ）：强制升级提示
- **scenario**：场景 4 扩展
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：服务端强制要求 V2+
- **test_data**：V1 客户端登录
- **expected**：弹窗"必须升级到 V2"+ 跳转应用商店
- **notes**：注意"强制" vs "可选"——强制是不升级无法使用

### TP-016（VERSION_COMPAT_BIZ）：协议双向兼容
- **scenario**：场景 3 扩展
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：服务端同时支持 V1 和 V2 协议
- **test_data**：V1 客户端发 V1 协议
- **expected**：服务端按 V1 协议处理 + 业务可用
- **notes**：注意"双向兼容" vs "单向"——双向是过渡期

### TP-017（VERSION_COMPAT_BIZ）：存档结构不匹配
- **scenario**：场景 9 扩展
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：玩家 V1 存档结构与 V2 不兼容
- **test_data**：V2 客户端读取 V1 存档
- **expected**：自动迁移 + 备份原存档（可回退）
- **notes**：注意"备份" vs "覆盖"——备份更安全

### TP-018（VERSION_COMPAT_BIZ）：灰度期间协议兼容
- **scenario**：场景 3 扩展
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：灰度发布期间 50% 服务支持 V2
- **test_data**：V2 客户端访问
- **expected**：根据服务端能力自动选 V1/V2 协议
- **notes**：注意"灰度" vs "全量"——灰度期间需同时支持

### TP-019（VERSION_COMPAT_BIZ）：热更版本不匹配
- **scenario**：场景 12 扩展
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：客户端热更版本与服务端热更版本不一致
- **test_data**：客户端启动
- **expected**：提示重新热更 + 阻塞游戏
- **notes**：注意"热更版本" vs "客户端版本"——热更是补丁

### TP-020（VERSION_COMPAT_BIZ）：数据格式降级
- **scenario**：场景 10 扩展
- **module**：`VERSION_COMPAT_BIZ`
- **precondition**：服务端数据格式从 V2 降到 V1
- **test_data**：V1 客户端读取 V2 数据
- **expected**：服务端自动降级 + V1 客户端可读
- **notes**：注意"降级" vs "升级"——降级是回退

---

## 3. 边界陷阱

### 边界 1：vs CONFIG（配置版本）
- **混淆点**："配置版本兼容" 看似 CONFIG → 实际 CONFIG 测"配置表字段 + 版本字段配置"，F 测"配置不兼容时的业务降级"
- **判定规则**：测"配置表结构 + 版本号" → 归 CONFIG；测"版本不兼容的业务兜底/拦截" → 归 SPECIAL F
- **instance**：配置表新增字段校验 → 归 CONFIG；旧端读新配置崩溃 → 归 F

### 边界 2：vs BIZ（业务流程）
- **混淆点**："版本升级流程" 看似 BIZ → 实际 BIZ 测"版本升级业务"（如升级奖励），F 测"版本不兼容的异常处理"
- **判定规则**：测"版本升级业务（升级奖励/活动）" → 归 BIZ；测"版本不兼容拦截/降级" → 归 SPECIAL F
- **instance**：玩家升级 V2 送 100 钻石 → 归 BIZ；V1 客户端访问 V2 副本 → 归 F

### 边界 3：vs LINK（灰度发布）
- **混淆点**："灰度兼容" 看似 LINK → 实际 LINK 测"灰度业务规则"（多服数据同步），F 测"客户端版本兼容"
- **判定规则**：测"灰度业务规则" → 归 LINK；测"客户端/协议版本兼容" → 归 SPECIAL F
- **instance**：灰度服 50% 玩家 → 归 LINK；V1 客户端访问 V2 副本 → 归 F

### 边界 4：vs UTIL F（离线更新）
- **混淆点**："资源更新" 看似 UTIL F → 实际 UTIL F 测"离线更新底层框架"（下载/校验/修复），F 测"资源版本不兼容的业务降级"
- **判定规则**：测"资源更新底层能力" → 归 UTIL F；测"资源版本不兼容时业务如何降级" → 归 SPECIAL F
- **instance**：资源下载失败重试 → 归 UTIL F；资源缺失使用占位 → 归 F

---

## 4. 验证证据

### 视觉证据
- 旧客户端访问新功能时"功能未开放"提示
- 资源缺失时占位图 + "请更新资源"提示
- 强制升级弹窗

### 日志证据
- `compat.client_version_old` 关键词：客户端版本过低
- `compat.protocol_unknown` 关键词：协议未识别
- `compat.protocol_deprecated` 关键词：协议已废弃
- `compat.config_migrated` 关键词：配置已迁移
- `compat.save_migrated` 关键词：存档已迁移
- `compat.resource_missing` 关键词：资源缺失

### 数据证据
- `client_version_log` 表记录每个客户端版本的使用情况
- `protocol_compat_log` 表记录协议版本兼容情况
- 资源版本号在 `resource_version` 表中
- 存档迁移记录在 `save_migration_log` 表中
- 数据库迁移记录在 `db_migration_log` 表中
- 旧客户端访问新功能时无数据写入

### 性能证据
- 版本校验耗时 < 5ms / 请求
- 资源缺失检测 < 100ms
- 存档迁移耗时 < 500ms / 玩家
- 协议版本识别 < 1ms
