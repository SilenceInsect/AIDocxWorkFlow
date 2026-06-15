# SPECIAL 模块 TP 库

> **TP 库位置**：`workflow_assets/test_point_library/SPECIAL/`
> **子模板来源**：`workflow_assets/module_templates/SPECIAL/`
> **v1.2 枚举数**：9（BOUNDARY_EXTREME / ANTI_CHEAT / WEAK_NET_RATE_LIMIT / BG_FG_SWITCH / SERVER_HA_RISK / VERSION_COMPAT_BIZ / CHANNEL_GRAY_BIZ / COMPLIANCE_RISK / RESOURCE_EXHAUST）

---

## TP 库文件清单

| 字母 | 子类 | 子类代码 | TP 库文件 | 状态 |
|------|------|---------|----------|------|
| A | 边界极端场景 | `BOUNDARY_EXTREME` | [A_boundary_extreme.md](./A_boundary_extreme.md) | ⏳ 待补 |
| B | 反作弊 / 数据安全 | `ANTI_CHEAT` | [B_anti_cheat.md](./B_anti_cheat.md) | ⏳ 待补 |
| C | 弱网 / 限流 | `WEAK_NET_RATE_LIMIT` | [C_weak_net_rate_limit.md](./C_weak_net_rate_limit.md) | ⏳ 待补 |
| D | 前后台切换 | `BG_FG_SWITCH` | [D_bg_fg_switch.md](./D_bg_fg_switch.md) | ⏳ 待补 |
| E | 宕机/并发/高危 | `SERVER_HA_RISK` | [E_server_ha_risk.md](./E_server_ha_risk.md) | ⏳ 待补 |
| F | 版本兼容 | `VERSION_COMPAT_BIZ` | [F_version_compat_biz.md](./F_version_compat_biz.md) | ⏳ 待补 |
| G | 渠道/灰度 | `CHANNEL_GRAY_BIZ` | [G_channel_gray_biz.md](./G_channel_gray_biz.md) | ⏳ 待补 |
| H | 合规风控 | `COMPLIANCE_RISK` | [H_compliance_risk.md](./H_compliance_risk.md) | ⏳ 待补 |
| I | 资源耗尽 | `RESOURCE_EXHAUST` | [I_resource_exhaust.md](./I_resource_exhaust.md) | ⏳ 待补 |

---

## AUX vs BIZ vs LINK vs SPECIAL 核心区分（**"水管 vs 业务 vs 互通 vs 对抗"**）

| 维度 | AUX 辅助 | BIZ 业务 | LINK 关联 | SPECIAL 特殊 |
|------|---------|---------|----------|--------------|
| 定位 | 底层通用框架/SDK | 业务层正常流转规则 | 业务层多系统互通规则 | 业务层对抗/容错/安全风控 |
| 职责 | 提供"能力底座" | 单系统独立业务流程 | 多系统/多端/外部互通规则 | 异常/高危/对抗/极限/合规/资源耗尽 |
| 典型 | 网络长连接、Redis、SDK 加密、崩溃捕获、TCP 重连 | 充值购买、任务领取、状态机、数据库持久化 | 跨服组队、第三方支付回调、多端登录 | 反作弊、限流、弱网降级、宕机 Failover、防沉迷、版本兼容 |
| **一句话** | **AUX 是"水管"** | **BIZ 是"水管里流什么"** | **LINK 是"两管怎么对接"** | **SPECIAL 是"水管破裂/泄漏/污染时怎么办"** |

> 完整边界见 [`module_templates/SPECIAL/O_boundary.md`](../../module_templates/SPECIAL/O_boundary.md)。

---

## SPECIAL 7 类典型风险（S4 必覆盖）

S5 阶段 EXCEPTION 类型 TP 必引用的 S4 风险点 + 异常树叶子节点，**核心 7 类**：

| 序号 | 风险类型 | 典型场景 | SPECIAL 子类 |
|------|---------|---------|--------------|
| 1 | **竞态条件** | 同一玩家并发发起 N 个购买 | F.并发 / E.并发极限 |
| 2 | **时间依赖** | 促销倒计时最后一秒、跨日重置 | A.边界极端 / G.限时 |
| 3 | **状态损坏** | 配置热更期间订单进行中 | D.状态机 / F.版本兼容 |
| 4 | **支付幂等性** | 渠道回调重复推送 | D.外部第三方 |
| 5 | **数据一致性** | 扣款成功但到账失败 | E.宕机 / I.事务 |
| 6 | **资源/容量** | 背包满、邮件容量满 | I.资源耗尽 |
| 7 | **安全/合规** | 客户端篡改、防沉迷拦截 | B.反作弊 / H.合规 |

---

## 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引（待补 TP 模板）|
