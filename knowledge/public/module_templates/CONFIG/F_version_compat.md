# F. 版本兼容与配置灰度

> **子类代码**：`VERSION_COMPAT`
> **归属模块**：`CONFIG`
> **来源**：用户细化定义 §5(2)「版本兼容与配置灰度」
>
> **测什么**：新旧版本前后兼容、版本隔离、灰度配置（白名单/渠道/测试服）。
> **不测什么**：单字段合法性（归 A）、热更（归 D）、解析性能（归 E）。
> **与其他子类的差异**：F 关注"跨版本/跨环境兼容"——A 关注"字段本身"，D 关注"运行时变更"。

---

## 1. 典型场景

### 场景 1：向前兼容（旧客户端读新配置）
- 业务背景：玩家没更新客户端
- 触发动作：服务端发新配置
- 验证点：旧客户端不报错、忽略新字段

### 场景 2：向后兼容（新客户端读旧配置）
- 业务背景：玩家更新了客户端但服务端没更新
- 触发动作：新客户端读旧配置
- 验证点：新客户端不报错、字段兼容

### 场景 3：废弃字段兼容
- 业务背景：旧配置有 `old_field`，新配置已删除
- 触发动作：新客户端读旧配置（带 old_field）
- 验证点：忽略废弃字段、不报错

### 场景 4：版本隔离
- 业务背景：赛季/活动配置
- 涉及字段：版本号
- 触发动作：上个赛季配置被新赛季使用
- 验证点：版本隔离、不跨赛季生效

### 场景 5：白名单配置
- 业务背景：测试服/灰度服专属配置
- 涉及字段：`whitelist` 字段
- 触发动作：非白名单玩家访问
- 验证点：白名单玩家可见、非白名单不可见

### 场景 6：渠道专属配置
- 业务背景：iOS/Android/不同商店
- 涉及字段：`channel` 字段
- 触发动作：iOS 渠道玩家看到 iOS 专属配置
- 验证点：渠道配置互不干扰

### 场景 7：测试服专属配置
- 业务背景：测试服有，正式服没有
- 涉及字段：环境标识
- 触发动作：测试服配置被正式服加载
- 验证点：测试服配置不污染正式服

---

## 2. 种子测试点（TP 模板）

### TP-001（VERSION_COMPAT）：旧客户端读新配置（新增字段）
- **scenario**：场景 1
- **module**：`VERSION_COMPAT`
- **precondition**：旧版本客户端（v1.0）
- **test_data**：新配置（v2.0）新增 `new_field`
- **expected**：旧客户端不报错、自动忽略新字段
- **notes**：注意"必需"vs"可选"新字段

### TP-002（VERSION_COMPAT）：旧客户端读新配置（删除字段）
- **scenario**：场景 1
- **module**：`VERSION_COMPAT`
- **precondition**：旧版本客户端（v1.0）
- **test_data**：新配置（v2.0）删除 `old_field`
- **expected**：旧客户端不报错
- **notes**：注意"删除"vs"重命名"

### TP-003（VERSION_COMPAT）：新客户端读旧配置
- **scenario**：场景 2
- **module**：`VERSION_COMPAT`
- **precondition**：新版本客户端（v2.0）
- **test_data**：旧配置（v1.0）无 `new_field`
- **expected**：新客户端兼容、按默认值处理
- **notes**：注意"默认值"vs"必需值"

### TP-004（VERSION_COMPAT）：废弃字段兜底
- **scenario**：场景 3
- **module**：`VERSION_COMPAT`
- **precondition**：新客户端
- **test_data**：旧配置含废弃字段 `legacy_field`
- **expected**：忽略废弃字段、不影响业务
- **notes**：注意"软废弃"vs"硬废弃"

### TP-005（VERSION_COMPAT）：版本隔离 - 赛季配置
- **scenario**：场景 4
- **module**：`VERSION_COMPAT`
- **precondition**：赛季 1 配置
- **test_data**：赛季 2 启动时，赛季 1 配置被加载
- **expected**：赛季 1 配置不生效、只加载赛季 2
- **notes**：注意"赛季 ID"vs"日期范围"

### TP-006（VERSION_COMPAT）：版本隔离 - 活动配置
- **scenario**：场景 4
- **module**：`VERSION_COMPAT`
- **precondition**：活动 A 已结束
- **test_data**：活动 B 启动时，活动 A 配置被加载
- **expected**：活动 A 配置不生效
- **notes**：注意"活动结束时间"vs"活动清理"

### TP-007（VERSION_COMPAT）：白名单配置可见性
- **scenario**：场景 5
- **module**：`VERSION_COMPAT`
- **precondition**：白名单玩家 ID = [1, 2, 3]
- **test_data**：玩家 ID=1 vs 玩家 ID=4
- **expected**：白名单玩家可见专属配置、非白名单不可见
- **notes**：注意"白名单"vs"黑名单"

### TP-008（VERSION_COMPAT）：白名单配置不污染
- **scenario**：场景 5
- **module**：`VERSION_COMPAT`
- **precondition**：白名单玩家已下线
- **test_data**：非白名单玩家访问
- **expected**：看不到白名单专属配置
- **notes**：注意"缓存"vs"实时"

### TP-009（VERSION_COMPAT）：渠道配置 - iOS
- **scenario**：场景 6
- **module**：`VERSION_COMPAT`
- **precondition**：iOS 渠道
- **test_data**：iOS 专属礼包 `ios_gift_pack`
- **expected**：iOS 玩家看到、Android 玩家看不到
- **notes**：注意"渠道 ID"vs"包名"

### TP-010（VERSION_COMPAT）：渠道配置 - Android
- **scenario**：场景 6
- **module**：`VERSION_COMPAT`
- **precondition**：Android 渠道
- **test_data**：Android 专属礼包 `android_gift_pack`
- **expected**：Android 玩家看到、iOS 玩家看不到
- **notes**：注意"应用商店"vs"渠道"

### TP-011（VERSION_COMPAT）：测试服配置不污染正式服
- **scenario**：场景 7
- **module**：`VERSION_COMPAT`
- **precondition**：测试服有 `debug_drop_rate=10.0`
- **test_data**：正式服玩家访问
- **expected**：正式服玩家按基础掉率、不受测试服配置影响
- **notes**：注意"环境标识"vs"IP 段"

### TP-012（VERSION_COMPAT）：灰度配置生效范围
- **scenario**：场景 5
- **module**：`VERSION_COMPAT`
- **precondition**：灰度 10% 玩家
- **test_data**：灰度玩家 vs 普通玩家
- **expected**：灰度玩家看到新配置、普通玩家看到旧配置
- **notes**：注意"灰度比例"vs"灰度名单"

---

## 3. 边界陷阱

### 边界 1：vs D. 热更新
- **混淆点**：「热更"版本"」——D 测运行时切换、F 测版本兼容
- **判定规则**：测"运行时热更" → D；测"新/旧版本/新/旧客户端兼容" → F
- **实例**：热更切换 → D-001；旧客户端读新配置 → F-001

### 边界 2：vs B. 同表一致性
- **混淆点**：「废弃"字段"」——B 测同表一致、F 测版本兼容
- **判定规则**：测"同表多字段一致" → B；测"废弃字段不影响业务" → F
- **实例**：同表 5 处基础倍率一致 → B-005；废弃字段忽略 → F-004

### 边界 3：vs K. 游戏专项
- **混淆点**：「本地化"配置"」——F 测版本/渠道、K 测本地化
- **判定规则**：测"跨版本/跨渠道" → F；测"多区服/多语言" → K
- **实例**：iOS vs Android 渠道 → F-009；中国服 vs 美服 → K-001

### 边界 4：vs I. 服务端专属
- **混淆点**：「服务端"灰度"」——I 测服务端配置、F 测版本/渠道
- **判定规则**：测"服务端全局常量" → I；测"灰度/白名单/渠道" → F
- **实例**：开服时间配置 → I-001；灰度玩家白名单 → F-012

---

## 4. 验证证据

### 视觉证据
- 多版本客户端对比截图
- 多渠道客户端对比截图

### 日志证据
- 配置加载日志（含版本号）
- 灰度命中日志
- 渠道识别日志

### 数据证据
- 配置文件版本号
- 灰度命中统计
- 渠道分布统计

### 性能证据
- 版本检查耗时 < 100ms
- 灰度匹配耗时 < 10ms
