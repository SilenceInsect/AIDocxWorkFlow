# G. 环境与渠道特殊异常

> **子类代码**：`CHANNEL_GRAY_BIZ`
> **归属模块**：`SPECIAL`
> **来源**：用户细化定义 §7「环境 & 渠道特殊异常」（原定义缺失补充）
>
> **测什么**：**渠道分包异常**（渠道 SDK 升级 / 渠道参数错误 / 渠道包名冲突）、**灰度白名单异常**（白名单玩家进入非灰度服 / 非白名单玩家进入灰度服）、**测试服与正式服互通隔离异常**（测试数据泄漏到正式服 / 正式玩家误入测试服）、**离线包损坏**（下载中断 / checksum 错误 / 版本不匹配）、**资源热更缺失/损坏后的业务降级**（占位资源 + 提示重下）。
> **不测什么**：渠道登录/支付业务对接（归 LINK）、配置灰度字段（归 CONFIG）、底层离线更新框架（归 AUX F）。
> **与其他子类的差异**：G 关注"环境/渠道"——A 关注"业务边界"、F 关注"版本兼容"、H 关注"法规合规"；G 是环境/分发渠道异常，H 是法规约束，F 是版本兼容。

---

## 1. 典型场景

### 场景 1：渠道 SDK 升级
- 业务背景：渠道 SDK 升级到 V2
- 涉及字段/工具：channel_sdk_version、sdk_compat
- 触发动作：玩家使用渠道登录
- 验证点：SDK V1 客户端兼容 V2 渠道（降级）

### 场景 2：渠道包名冲突
- 业务背景：同一应用市场多个包名
- 涉及字段/工具：package_name、channel_id
- 触发动作：玩家安装
- 验证点：渠道 ID 正确识别 + 活动正确发放

### 场景 3：渠道参数错误
- 业务背景：渠道配置错误（如 cp_id 缺失）
- 涉及字段/工具：channel_config、config_validate
- 触发动作：玩家登录
- 验证点：参数错误时使用默认渠道 + 日志告警

### 场景 4：白名单玩家进非灰度服
- 业务背景：白名单玩家应进灰度服
- 涉及字段/工具：whitelist、server_type
- 触发动作：白名单玩家登录
- 验证点：自动路由到灰度服

### 场景 5：非白名单进灰度服
- 业务背景：非白名单不应进灰度服
- 涉及字段/工具：whitelist_check、server_redirect
- 触发动作：非白名单玩家尝试进灰度服
- 验证点：拒绝 + 路由到正式服

### 场景 6：测试服数据泄漏到正式服
- 业务背景：测试服充值订单发到正式服
- 涉及字段/工具：env_isolation、data_filter
- 触发动作：测试服支付回调
- 验证点：环境隔离 + 测试订单不写到正式服

### 场景 7：正式玩家误入测试服
- 业务背景：玩家通过测试入口进入测试服
- 涉及字段/工具：env_check、login_restrict
- 触发动作：正式服玩家进入测试服
- 验证点：拒绝 + 提示"测试服需测试账号"

### 场景 8：离线包下载中断
- 业务背景：离线包下载到 80% 时网络断开
- 涉及字段/工具：download_status、resume_download
- 触发动作：玩家下载离线包
- 验证点：断点续传 + 重试

### 场景 9：离线包 checksum 错误
- 业务背景：离线包文件损坏
- 涉及字段/工具：checksum、file_verify
- 触发动作：玩家使用离线包
- 验证点：检测损坏 + 重新下载

### 场景 10：离线包版本不匹配
- 业务背景：客户端版本 = 1.0，离线包版本 = 1.5
- 涉及字段/工具：package_version、version_check
- 触发动作：玩家尝试加载离线包
- 验证点：版本不匹配拦截 + 提示下载对应版本

### 场景 11：热更资源缺失
- 业务背景：客户端热更资源丢失
- 涉及字段/工具：resource_missing、fallback
- 触发动作：玩家访问使用热更资源的页面
- 验证点：占位资源 + 提示重下

### 场景 12：热更资源损坏
- 业务背景：热更资源文件被篡改/损坏
- 涉及字段/工具：resource_checksum、verify
- 触发动作：玩家使用热更资源
- 验证点：检测损坏 + 重新下载 + 业务降级

### 场景 13：渠道活动跨服
- 业务背景：A 渠道玩家在 B 渠道登录
- 涉及字段/工具：channel_id、cross_channel
- 触发动作：玩家换渠道登录
- 验证点：渠道 ID 校验 + 活动不混

### 场景 14：灰度服宕机数据丢失
- 业务背景：灰度服宕机未备份
- 涉及字段/工具：gray_data_backup、recovery
- 触发动作：灰度服宕机
- 验证点：从正式服恢复数据 + 不影响正式服

### 场景 15：渠道登录失败
- 业务背景：渠道登录超时
- 涉及字段/工具：channel_login、fallback_login
- 触发动作：玩家登录
- 验证点：超时后重试 + 失败后提示游客登录

---

## 2. 种子测试点（TP 模板）

### TP-001（CHANNEL_GRAY_BIZ）：渠道 SDK 升级兼容
- **scenario**：场景 1
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：渠道 SDK 升级到 V2，玩家客户端集成 V1
- **test_data**：V1 客户端通过 V2 渠道登录
- **expected**：渠道兼容（V1 客户端调用 V2 SDK V1 兼容 API）+ 登录成功
- **notes**：注意"渠道兼容" vs "协议兼容"——前者是渠道侧

### TP-002（CHANNEL_GRAY_BIZ）：渠道包名冲突
- **scenario**：场景 2
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：同一应用市场多个包名
- **test_data**：玩家从不同包名登录
- **expected**：渠道 ID 正确识别 + 活动按渠道发放
- **notes**：注意"包名" vs "渠道 ID"——渠道 ID 是逻辑标识

### TP-003（CHANNEL_GRAY_BIZ）：渠道参数错误兜底
- **scenario**：场景 3
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：渠道配置错误（cp_id 缺失）
- **test_data**：玩家登录
- **expected**：使用默认渠道参数 + 告警日志（运营修复）+ 玩家可登录
- **notes**：注意"兜底" vs "拒绝"——兜底保留可用性

### TP-004（CHANNEL_GRAY_BIZ）：白名单路由
- **scenario**：场景 4
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：白名单玩家 ID = 10001，应进入灰度服
- **test_data**：玩家 10001 登录
- **expected**：自动路由到灰度服（不在正式服）
- **notes**：注意"白名单" vs "灰度用户"——白名单是名单形式

### TP-005（CHANNEL_GRAY_BIZ）：非白名单拒入灰度
- **scenario**：场景 5
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：玩家 20002 不在白名单
- **test_data**：玩家 20002 尝试进入灰度服
- **expected**：拒绝 + 自动路由到正式服 + 不暴露灰度服信息
- **notes**：注意"拒绝" vs "暴露"——拒绝不暴露灰度服

### TP-006（CHANNEL_GRAY_BIZ）：测试服订单隔离
- **scenario**：场景 6
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：测试服玩家支付
- **test_data**：测试服支付回调
- **expected**：订单写入测试服 DB + 不写入正式服 DB
- **notes**：注意"环境隔离" vs "DB 共享"——隔离是必要

### TP-007（CHANNEL_GRAY_BIZ）：正式玩家误入测试服
- **scenario**：场景 7
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：正式服玩家尝试访问测试服入口
- **test_data**：玩家访问测试服
- **expected**：拒绝 + 提示"请使用正式服"
- **notes**：注意"误入" vs "恶意"——误入是友善提示

### TP-008（CHANNEL_GRAY_BIZ）：离线包断点续传
- **scenario**：场景 8
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：离线包下载 80% 时断网
- **test_data**：10min 后恢复网络
- **expected**：从 80% 续传 + 不重新下载
- **notes**：注意"续传" vs "重下"——续传是断点续传

### TP-009（CHANNEL_GRAY_BIZ）：离线包损坏检测
- **scenario**：场景 9
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：离线包文件被损坏
- **test_data**：玩家使用离线包
- **expected**：checksum 校验失败 + 删除损坏包 + 重新下载
- **notes**：注意"损坏" vs "缺失"——损坏是文件错误

### TP-010（CHANNEL_GRAY_BIZ）：离线包版本不匹配
- **scenario**：场景 10
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：客户端 = V1.0，离线包 = V1.5
- **test_data**：玩家加载离线包
- **expected**：版本不匹配拦截 + 提示下载 V1.0 对应离线包
- **notes**：注意"客户端版本" vs "离线包版本"——离线包是补丁

### TP-011（CHANNEL_GRAY_BIZ）：热更资源缺失
- **scenario**：场景 11
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：客户端热更资源丢失
- **test_data**：玩家访问使用热更资源的页面
- **expected**：占位资源 + 提示"资源已损坏，请重新下载"
- **notes**：注意"热更" vs "整包"——热更是补丁

### TP-012（CHANNEL_GRAY_BIZ）：热更资源损坏
- **scenario**：场景 12
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：热更资源被篡改
- **test_data**：玩家使用热更资源
- **expected**：checksum 校验失败 + 重新下载 + 业务降级
- **notes**：注意"篡改" vs "损坏"——损坏是文件错误，篡改是恶意

### TP-013（CHANNEL_GRAY_BIZ）：跨渠道活动隔离
- **scenario**：场景 13
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：A 渠道活动只给 A 渠道玩家
- **test_data**：B 渠道玩家尝试领取 A 渠道活动
- **expected**：拒绝 + 提示"活动不适用"
- **notes**：注意"渠道活动" vs "全渠道活动"——前者有渠道限制

### TP-014（CHANNEL_GRAY_BIZ）：灰度服数据恢复
- **scenario**：场景 14
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：灰度服宕机 + 数据丢失
- **test_data**：灰度服重启
- **expected**：从正式服恢复数据（部分）+ 灰度数据可丢失
- **notes**：注意"灰度" vs "正式"——灰度可承受数据丢失

### TP-015（CHANNEL_GRAY_BIZ）：渠道登录超时降级
- **scenario**：场景 15
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：渠道登录超时
- **test_data**：玩家点击"渠道登录"
- **expected**：超时后重试 1 次 + 失败后提示游客登录
- **notes**：注意"渠道登录" vs "游客登录"——降级是 fallback

### TP-016（CHANNEL_GRAY_BIZ）：灰度白名单生效
- **scenario**：场景 4 扩展
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：灰度白名单为空
- **test_data**：所有玩家尝试进灰度服
- **expected**：全部拒绝 + 路由到正式服
- **notes**：注意"白名单为空" vs "白名单有"——空是默认拒绝

### TP-017（CHANNEL_GRAY_BIZ）：测试服数据导出
- **scenario**：场景 6 扩展
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：测试服需导出测试报告
- **test_data**：运营触发 export_test_data
- **expected**：仅导出测试服数据 + 不包含正式服数据
- **notes**：注意"导出" vs "导入"——导出是从测试服到外部

### TP-018（CHANNEL_GRAY_BIZ）：离线包升级提示
- **scenario**：场景 10 扩展
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：服务端有新离线包
- **test_data**：客户端启动
- **expected**：检测到新离线包 + 提示下载 + 可选/强制
- **notes**：注意"提示" vs "强制"——根据业务决定

### TP-019（CHANNEL_GRAY_BIZ）：热更资源降级
- **scenario**：场景 12 扩展
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：热更资源损坏 + 网络断开
- **test_data**：玩家使用热更资源
- **expected**：业务降级（隐藏该功能）+ 提示"稍后重试"
- **notes**：注意"降级" vs "崩溃"——降级保留可用性

### TP-020（CHANNEL_GRAY_BIZ）：灰度服玩家回退正式服
- **scenario**：场景 5 扩展
- **module**：`CHANNEL_GRAY_BIZ`
- **precondition**：灰度服停服
- **test_data**：灰度服玩家登录
- **expected**：自动回退到正式服 + 数据合并（按业务规则）
- **notes**：注意"回退" vs "丢失"——回退保留数据

---

## 3. 边界陷阱

### 边界 1：vs LINK（渠道对接）
- **混淆点**："渠道登录失败" 看似 G → 实际 LINK 测"渠道登录业务"（正常登录），G 测"渠道异常处理"（SDK 升级/参数错误/超时）
- **判定规则**：测"渠道业务对接" → 归 LINK；测"渠道异常 + 降级 + 隔离" → 归 SPECIAL G
- **instance**：微信登录成功 → 归 LINK；微信登录超时降级 → 归 G

### 边界 2：vs CONFIG（灰度配置）
- **混淆点**："灰度白名单" 看似 CONFIG → 实际 CONFIG 测"灰度配置字段"，G 测"白名单生效/路由"
- **判定规则**：测"灰度配置字段" → 归 CONFIG；测"灰度路由 + 隔离" → 归 SPECIAL G
- **instance**：白名单配置 → 归 CONFIG；白名单玩家进灰度服 → 归 G

### 边界 3：vs AUX F（离线更新）
- **混淆点**："离线包下载" 看似 G → 实际 AUX F 测"离线包下载/校验底层"，G 测"离线包损坏/版本不匹配的业务降级"
- **判定规则**：测"离线包底层" → 归 AUX F；测"离线包异常的业务处理" → 归 SPECIAL G
- **instance**：断点续传 → 归 AUX F；离线包版本不匹配拦截 → 归 G

### 边界 4：vs LINK（灰度业务）
- **混淆点**："灰度服" 看似 LINK → 实际 LINK 测"灰度业务规则"（灰度策略），G 测"灰度服环境隔离"
- **判定规则**：测"灰度业务规则" → 归 LINK；测"灰度环境隔离 + 数据不泄漏" → 归 SPECIAL G
- **instance**：灰度 10% 玩家 → 归 LINK；测试服数据泄漏到正式服 → 归 G

---

## 4. 验证证据

### 视觉证据
- 渠道登录失败时"请稍后重试"提示
- 灰度服停服时"正在维护"提示
- 离线包损坏时"请重新下载"提示
- 热更资源缺失时占位图

### 日志证据
- `channel.sdk_upgrade` 关键词：渠道 SDK 升级
- `channel.param_invalid` 关键词：渠道参数错误
- `gray.whitelist_match` 关键词：白名单匹配
- `gray.whitelist_miss` 关键词：白名单未命中
- `env.isolation_breach` 关键词：环境隔离突破
- `offline.checksum_fail` 关键词：离线包 checksum 失败
- `offline.version_mismatch` 关键词：离线包版本不匹配
- `hotupdate.resource_missing` 关键词：热更资源缺失
- `hotupdate.resource_corrupt` 关键词：热更资源损坏

### 数据证据
- `channel_config` 表记录渠道配置（含 version、cp_id）
- `whitelist` 表记录灰度白名单
- `env_isolation_log` 表记录环境隔离事件
- `offline_package_log` 表记录离线包下载/校验
- `hotupdate_log` 表记录热更资源事件
- 测试服订单不写入正式服 DB
- 热更资源损坏后 checksum 不匹配

### 性能证据
- 渠道登录超时检测 < 5s
- 白名单匹配 < 1ms
- 环境隔离校验 < 10ms
- 离线包 checksum 校验 < 100ms / MB
- 热更资源检测 < 200ms
