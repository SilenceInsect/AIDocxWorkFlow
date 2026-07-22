# SPECIAL 模块测试点模板（概览）

> **模块代码**：`SPECIAL`
> **来源**：`.cursor/MODULES.md` §1 总表 + 用户细化定义
> **作用**：S5 生成 SPECIAL 模块测试点时，按 story 实际涉及子类**按需加载**对应子模板。
> **v1.11 核心**：**SPECIAL = 异常 + 高危 + 对抗 + 极限 + 合规 + 资源耗尽** 类业务风控与容错逻辑；
> 底层网络重连、崩溃捕获、缓存工具等基础设施归 **UTIL**；正常正向业务流程归 **BIZ**；
> 第三方 / 跨服互通异常归 **LINK**。
>
> **完整覆盖范围**（一句话）：
> 全系统数值/时间/权限/中断类边界极端场景、非正常业务异常分支处理；客户端本地篡改、伪造协议、挂机脚本等反作弊校验与非法数据拦截；本地存档、传输参数数据安全防护；弱网/抖动/断网环境业务操作容错、高频重复请求限流防刷；移动端前后台切换、进程杀除后状态与资源恢复逻辑；服务宕机、数据库抖动、版本回档、万人并发极限场景事务兜底；背包/邮件/服务器资源耗尽降级策略；新旧客户端版本兼容异常拦截；防沉迷、未成年付费、敏感内容等合规风控；批量清零/大额发奖/全服重置等高风险操作二次校验；灰度/渠道/离线资源损坏环境降级处理（底层网络、缓存工具等基础设施归 UTIL 模块，本模块仅覆盖业务层对抗、容错、安全风控规则）。

---

## v1.11 核心定位（边界隔离）

> **SPECIAL = "非正常、高危、极端、对抗性场景"**

| 归 SPECIAL（业务层对抗/容错/安全风控） | 不归 SPECIAL（归其他模块）|
|-----------------------------------|------------------------|
| 异常/高危/对抗/极限/合规/资源耗尽 业务规则 | 底层网络 SDK/缓存工具/崩溃框架 → **UTIL** |
| 业务层容错（弱网/切后台/CD/资源耗尽/合规）| 正常业务流程 → **BIZ** |
| 第三方接口异常 + 跨服数据作弊拦截 | 第三方/跨服正常同步 → **LINK** |
| 界面异常导致的业务错乱 | 界面加载失败纯视觉 → **UI** |
| 反作弊行为检测/审计 | 加密算法底层 → **UTIL M** |
| GM 高危操作拦截 | GM 权限配置字段 → **CONFIG** |
| 业务审计日志（执行层）| 通用行为日志/埋点 → **LOG** |
| 限流弹窗（"操作太频繁"）| 弹窗样式/触发逻辑 → **HINT** |

> **本模块仅覆盖异常、高危、对抗、极限、合规限制类业务规则；正常正向业务流程归入 BIZ，底层通信 / 工具框架归入 UTIL，第三方跨服正常互通归入 LINK，各模块无用例范围重叠。**

---

## 子类索引

| 字母 | 子类名 | 子类代码（v1.2 枚举） | 模板 | 细化段 |
|------|--------|----------------------|------|--------|
| A | 边界极端场景 | `BOUNDARY_EXTREME` | [A_boundary_extreme.md](./SPECIAL/A_boundary_extreme.md) | §1 |
| B | 反作弊 / 数据安全 | `ANTI_CHEAT` | [B_anti_cheat.md](./SPECIAL/B_anti_cheat.md) | §2 |
| C | 弱网 / 断网 / 限流 | `WEAK_NET_RATE_LIMIT` | [C_weak_net_rate_limit.md](./SPECIAL/C_weak_net_rate_limit.md) | §3 |
| D | 前后台切换 / 生命周期 | `BG_FG_SWITCH` | [D_bg_fg_switch.md](./SPECIAL/D_bg_fg_switch.md) | §4 |
| E | 宕机 / 回档 / 并发极限 / 高危风控 | `SERVER_HA_RISK` | [E_server_ha_risk.md](./SPECIAL/E_server_ha_risk.md) | §5 |
| F | 版本兼容异常 | `VERSION_COMPAT_BIZ` | [F_version_compat_biz.md](./SPECIAL/F_version_compat_biz.md) | §6（新增）|
| G | 环境与渠道特殊异常 | `CHANNEL_GRAY_BIZ` | [G_channel_gray_biz.md](./SPECIAL/G_channel_gray_biz.md) | §7（新增）|
| H | 风控 & 合规 | `COMPLIANCE_RISK` | [H_compliance_risk.md](./SPECIAL/H_compliance_risk.md) | §8（新增）|
| I | 资源耗尽极端场景 | `RESOURCE_EXHAUST` | [I_resource_exhaust.md](./SPECIAL/I_resource_exhaust.md) | §9（新增）|
| O | 边界区分 | —（判定规则，非测试类型）| [O_boundary.md](./SPECIAL/O_boundary.md) | §4 边界 |
| P | 游戏项目补充 | —（游戏项目专项，非通用测试类型）| [P_game_specific.md](./SPECIAL/P_game_specific.md) | §5 游戏 |

> **结构说明**：
> - A-E 是用户原定义的 5 大类（边界极端 / 反作弊 / 弱网 / 前后台 / 宕机并发）
> - F-I 是用户新增的 4 大类（版本兼容 / 渠道灰度 / 合规 / 资源耗尽）—— 原定义缺失补充
> - A-I 共同构成 v1.11 完整覆盖范围
> - O/P 是判定规则和游戏专项

---

## v1.2 枚举 vs v1.1 旧枚举

| v1.2 枚举（现行）| 归属子类 | v1.1 旧枚举（已废弃）| 兼容规则 |
|------------------|---------|---------------------|----------|
| `BOUNDARY_EXTREME` | A.边界极端场景 | （新增）| 历史数据无对应项，v1.11 首次出现（含原 `DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` 部分场景）|
| `ANTI_CHEAT` | B.反作弊 | `ANTI_CHEAT` | 1:1 映射（语义升级：从"反作弊"扩展为"反作弊 + 数据安全 + 参数篡改"）|
| `WEAK_NET_RATE_LIMIT` | C.弱网/限流 | `WEAK_NETWORK` / `HIGH_FREQ_PACKET`（部分）| 涉及"弱网/断网/限流"归 `WEAK_NET_RATE_LIMIT` |
| `BG_FG_SWITCH` | D.前后台切换 | `SWITCH_TO_BACKGROUND` | 1:1 映射（语义升级）|
| `SERVER_HA_RISK` | E.宕机/并发/高危 | （新增）| 历史数据无对应项，v1.11 首次出现（含原 `DUPLICATE_PACKET` 服端场景）|
| `VERSION_COMPAT_BIZ` | F.版本兼容 | （新增）| 历史数据无对应项，v1.11 首次出现（原 v1.1 完全缺失）|
| `CHANNEL_GRAY_BIZ` | G.渠道灰度 | （新增）| 历史数据无对应项，v1.11 首次出现（原 v1.1 完全缺失）|
| `COMPLIANCE_RISK` | H.合规风控 | （新增）| 历史数据无对应项，v1.11 首次出现（原 v1.1 完全缺失）|
| `RESOURCE_EXHAUST` | I.资源耗尽 | （新增）| 历史数据无对应项，v1.11 首次出现（原 v1.1 完全缺失）|

> **拆分说明**：
> - v1.1 旧 `DUPLICATE_PACKET` 在 v1.2 中**按场景拆分**——业务层去重 → `BOUNDARY_EXTREME` A / 流量层限流 → `WEAK_NET_RATE_LIMIT` C
> - v1.1 旧 `HIGH_FREQ_PACKET` 在 v1.2 中**按场景拆分**——客户端业务 → `BOUNDARY_EXTREME` A / 服务端 HA → `SERVER_HA_RISK` E / 流量层限流 → `WEAK_NET_RATE_LIMIT` C
> - v1.1 旧 `WEAK_NETWORK` 升级为 `WEAK_NET_RATE_LIMIT`（语义从"网络异常"扩展为"网络异常 + 流量限流"）
> - v1.1 旧 `SWITCH_TO_BACKGROUND` 升级为 `BG_FG_SWITCH`（语义扩展为"前后台切换 + 生命周期恢复"）
> - v1.1 旧 `ANTI_CHEAT` 升级为 `ANTI_CHEAT`（语义从"反作弊"扩展为"反作弊 + 数据安全 + 参数篡改"）
> - v1.2 新增 5 个全新枚举（`SERVER_HA_RISK` / `VERSION_COMPAT_BIZ` / `CHANNEL_GRAY_BIZ` / `COMPLIANCE_RISK` / `RESOURCE_EXHAUST`）——对应用户"原定义缺失的 SPECIAL 专属场景"中的 5 类

---

## 加载规则（S5 prompt 使用方式）

1. **检测** `epic.module == "SPECIAL"` → 必读本概览
2. **按 story 内容** 识别涉及的子类（如"反作弊"→ 涉及 B 反作弊 + A 边界值）
3. **按需加载** 对应子模板
4. **交叉参考** `O_boundary.md` 防止误标 SPECIAL 标签（实际是 BIZ / UTIL / LINK / UI / HINT / LOG / CONFIG）

---

## 边界总览

| 归 SPECIAL | 不归 SPECIAL（归其他模块）|
|------------|--------------------------|
| 异常/高危/对抗/极限/合规/资源耗尽 业务规则 | 业务流程、玩家交互逻辑 → BIZ |
| 反作弊检测/数据篡改识别 | 底层网络/工具/SDK → UTIL |
| 弱网业务容错/限流防刷 | 跨服/第三方正常业务 → LINK |
| 切后台状态恢复/进程被杀 | 配置表字段/跨表数值 → CONFIG |
| 宕机 Failover/事务回滚 | 页面视觉/前端交互 → UI |
| 高危操作拦截/灰度执行 | 提示内容/弹窗样式 → HINT |
| 反作弊审计/作弊日志 | 通用行为日志/埋点 → LOG |
| 版本兼容/资源缺失兜底 | 正常网络/缓存底层 → UTIL |

> 完整边界规则见 [`O_boundary.md`](./SPECIAL/O_boundary.md)

---

## 关键词快速映射

| 关键词 / 上下文 | 子类 |
|----------------|------|
| 数值边界、CD、未开启、过期、权限不足、中断、互斥 | A 边界极端 |
| 改包、作弊、外挂、挂机、脚本、篡改、封禁、瞬移、无限技能 | B 反作弊 |
| 弱网、断网、网络抖动、限流、防刷、雪崩、流量 | C 弱网/限流 |
| 切后台、进程被杀、内存不足、锁屏、生命周期、状态恢复 | D 前后台 |
| 宕机、Failover、回档、并发、万人、批量发奖、灰度、分布式锁 | E 宕机/高危 |
| 版本兼容、新旧客户端、协议升级、资源缺失、热更失败 | F 版本兼容 |
| 渠道、灰度白名单、测试服、隔离、离线包 | G 渠道/灰度 |
| 防沉迷、未成年、敏感词、实名、地区合规、GDPR | H 合规 |
| 背包满、仓库满、邮件满、CPU 高、内存高、DB 连接满、降级 | I 资源耗尽 |
| 战斗、社交、经济、活动、赛事、游戏专项 | P 游戏专项 |

---

## 进度

- v1.0 (2026-06-15)：SPECIAL 模块 9 测试子模板（A-I）+ 2 规则（O 边界 + P 游戏专项）全部到位
  - A 边界极端（数值/时间/权限/中断/冲突）= `BOUNDARY_EXTREME`
  - B 反作弊 / 数据安全 = `ANTI_CHEAT`
  - C 弱网 / 断网 / 限流 = `WEAK_NET_RATE_LIMIT`
  - D 前后台切换 / 生命周期 = `BG_FG_SWITCH`
  - E 宕机 / 回档 / 并发极限 / 高危风控 = `SERVER_HA_RISK`
  - F 版本兼容异常（新增）= `VERSION_COMPAT_BIZ`
  - G 环境与渠道特殊异常（新增）= `CHANNEL_GRAY_BIZ`
  - H 风控 & 合规（新增）= `COMPLIANCE_RISK`
  - I 资源耗尽极端场景（新增）= `RESOURCE_EXHAUST`
