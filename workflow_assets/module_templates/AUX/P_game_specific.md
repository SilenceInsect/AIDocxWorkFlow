# P. AUX 游戏项目额外专属（仅游戏项目）

> **非测试类型**——本文件是**仅游戏项目**的 AUX 测试点补充。
> 非游戏项目（PC 后台、移动端 App、Web 工具）**忽略**本文件。
>
> **来源**：用户细化定义 §5「游戏项目重点补充高频辅助测试点」

---

## 1. 多端适配工具

### 场景
- 业务背景：手游/端游/页游
- 涉及工具：跨平台工具
- 验证点：跨端兼容

### 种子 TP

#### TP-001（P-多端）：移动端省电模式
- **module**：`PERF_TOOL`（AUX 子类）
- **precondition**：手机低电量
- **test_data**：玩家开省电模式
- **expected**：游戏自动降帧/降画质
- **notes**：注意"省电"vs"流畅"

#### TP-002（P-多端）：后台切前台资源恢复
- **module**：`RESOURCE_MGMT`
- **precondition**：玩家切后台 30 分钟
- **test_data**：切回前台
- **expected**：资源恢复、不报错
- **notes**：注意"恢复"vs"重启"

#### TP-003（P-多端）：模拟器兼容
- **module**：`COMMON_UTIL`
- **precondition**：玩家用模拟器
- **test_data**：登录游戏
- **expected**：正常运行
- **notes**：注意"模拟器"vs"真机"

#### TP-004（P-多端）：横竖屏切换
- **module**：`COMMON_UTIL`
- **precondition**：手游
- **test_data**：旋转手机
- **expected**：布局正确、不崩溃
- **notes**：与 UI-C 配合

#### TP-005（P-多端）：多分辨率
- **module**：`COMMON_UTIL`
- **precondition**：不同屏幕
- **test_data**：iPhone SE vs iPad
- **expected**：UI 正常
- **notes**：与 UI-C 配合

---

## 2. 渠道差异化辅助

### 场景
- 业务背景：iOS/Android/Web
- 涉及工具：渠道 SDK
- 验证点：渠道差异

### 种子 TP

#### TP-006（P-渠道）：渠道登录 SDK
- **module**：`COMMON_UTIL`
- **precondition**：玩家用微信登录
- **test_data**：点击微信登录
- **expected**：拉起微信授权
- **notes**：注意"渠道 SDK"vs"业务"

#### TP-007（P-渠道）：支付 SDK 封装
- **module**：`COMMON_UTIL`
- **precondition**：玩家用支付宝
- **test_data**：点击支付
- **expected**：拉起支付宝
- **notes**：注意"SDK"vs"业务"

#### TP-008（P-渠道）：渠道分包更新
- **module**：`OFFLINE_UPDATE`
- **precondition**：iOS App Store
- **test_data**：iOS 玩家启动
- **expected**：走 App Store 更新
- **notes**：注意"商店"vs"自建"

#### TP-009（P-渠道）：渠道专属礼包
- **module**：`OPS_TOOL`
- **precondition**：iOS 玩家
- **test_data**：查看礼包
- **expected**：仅 iOS 玩家可见
- **notes**：注意"渠道"vs"大区"

#### TP-010（P-渠道）：渠道参数上报
- **module**：`STORAGE_LOG`
- **precondition**：玩家启动
- **test_data**：上报渠道 ID
- **expected**：埋点含渠道 ID
- **notes**：注意"渠道"vs"平台"

---

## 3. 灰度 / 白名单辅助工具

### 场景
- 业务背景：分批上线
- 涉及工具：灰度白名单
- 验证点：定向生效

### 种子 TP

#### TP-011（P-灰度）：分服分批次活动
- **module**：`OPS_TOOL`
- **precondition**：服 1/2/3
- **test_data**：先开服 1
- **expected**：仅服 1 玩家可见
- **notes**：注意"分服"vs"全服"

#### TP-012（P-灰度）：白名单玩家
- **module**：`OPS_TOOL`
- **precondition**：白名单玩家 ID
- **test_data**：新功能
- **expected**：白名单可见
- **notes**：注意"白名单"vs"灰度"

#### TP-013（P-灰度）：定向发放奖励
- **module**：`OPS_TOOL`
- **precondition**：100 目标玩家
- **test_data**：定向发奖
- **expected**：仅 100 玩家收到
- **notes**：注意"定向"vs"全员"

#### TP-014（P-灰度）：灰度比例生效
- **module**：`OPS_TOOL`
- **precondition**：10% 灰度
- **test_data**：1000 玩家
- **expected**：约 100 玩家命中
- **notes**：注意"比例"vs"名单"

---

## 4. 性能辅助采样工具

### 场景
- 业务背景：性能监控
- 涉及工具：采样工具
- 验证点：实时监控

### 种子 TP

#### TP-015（P-性能）：内存实时监控
- **module**：`PERF_TOOL`
- **precondition**：游戏运行
- **test_data**：观察内存
- **expected**：实时显示、阈值告警
- **notes**：注意"实时"vs"采样"

#### TP-016（P-性能）：CPU 实时监控
- **module**：`PERF_TOOL`
- **precondition**：游戏运行
- **test_data**：观察 CPU
- **expected**：实时显示
- **notes**：注意"CPU"vs"GPU"

#### TP-017（P-性能）：IO 实时监控
- **module**：`PERF_TOOL`
- **precondition**：游戏运行
- **test_data**：观察磁盘 IO
- **expected**：IO 正常
- **notes**：注意"磁盘"vs"网络"

#### TP-018（P-性能）：网络延迟面板
- **module**：`PERF_TOOL`
- **precondition**：游戏中
- **test_data**：观察网络延迟
- **expected**：实时显示延迟
- **notes**：注意"延迟"vs"丢包"

#### TP-019（P-性能）：战斗卡顿采样
- **module**：`PERF_TOOL`
- **precondition**：战斗
- **test_data**：5 分钟采样
- **expected**：FPS/CPU/内存报告
- **notes**：与 H 性能采样脚本配合

---

## 5. 补偿补发辅助

### 场景
- 业务背景：bug 补偿
- 涉及工具：补发工具
- 验证点：批量补发

### 种子 TP

#### TP-020（P-补偿）：批量补发道具
- **module**：`GM_TOOL`
- **precondition**：bug 影响 1000 玩家
- **test_data**：批量补发 100 钻石
- **expected**：1000 玩家各收到
- **notes**：注意"批量"vs"逐个"

#### TP-021（P-补偿）：邮件补发
- **module**：`GM_TOOL`
- **precondition**：玩家离线
- **test_data**：邮件补发
- **expected**：玩家上线收到
- **notes**：注意"邮件"vs"直接发"

#### TP-022（P-补偿）：回档补偿
- **module**：`OPS_TOOL`
- **precondition**：服务器回档
- **test_data**：批量补偿
- **expected**：受影响玩家收到
- **notes**：注意"回档"vs"回滚"

#### TP-023（P-补偿）：补偿到账通知
- **module**：`HINT`（提示内容）
- **precondition**：玩家收到补偿
- **test_data**：观察提示
- **expected**：红点 + 邮件提示
- **notes**：注意"提示"vs"静默"

#### TP-024（P-补偿）：补偿领取有效期
- **module**：`OPS_TOOL`
- **precondition**：补偿邮件 7 天有效期
- **test_data**：8 天后领
- **expected**：过期
- **notes**：注意"过期"vs"永久"

---

## 6. 边界陷阱

### 边界 1：vs K. 性能
- **混淆点**：「性能"工具"」——K 测通用性能、P 测游戏专项
- **判定规则**：测"通用性能监控组件" → K；测"游戏帧率/战斗性能" → P
- **实例**：FPS 监控 → K；战斗卡顿采样 → P-019

### 边界 2：vs G. GM 工具
- **混淆点**：「GM"补发"」——G 测 GM 指令、P 测补偿
- **判定规则**：测"GM 指令和权限" → G；测"批量补发工具" → P
- **实例**：`gm_add_item` → G；批量补发 → P-020

### 边界 3：vs UI-J 游戏专项
- **混淆点**：「游戏"UI"」——P 测游戏辅助、UI-J 测游戏 UI
- **判定规则**：测"游戏 SDK/工具" → P；测"游戏 UI 控件" → UI-J
- **实例**：摇杆灵敏度 → UI-J；模拟器兼容 → P-003

### 边界 4：vs CONFIG-K
- **混淆点**：「渠道"配置"」——P 测工具、CONFIG 测配置
- **判定规则**：测"渠道 SDK 工具" → P；测"渠道配置字段" → CONFIG-K
- **实例**：微信登录 SDK → P-006；渠道配置 → CONFIG-K

---

## 7. 验证证据

### 视觉证据
- 多端 UI 对比截图
- 灰度白名单效果截图

### 日志证据
- 渠道 ID 上报日志
- 灰度命中日志
- 性能采样日志
- 补发日志

### 数据证据
- 渠道分布统计
- 灰度命中率
- 性能数据采样表
- 补偿记录表

### 性能证据
- 跨端兼容 100%
- 性能采样精度 ≥ 1Hz
- 补发 1000 玩家 < 5min
