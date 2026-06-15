# LOG 模块 TP 库

> **TP 库位置**：`workflow_assets/test_point_library/LOG/`
> **子模板来源**：`workflow_assets/module_templates/LOG/`
> **v1.9 枚举数**：13（LOG_EVENT_TRACK / LOG_ASSET_AUDIT / LOG_OPERATION / LOG_MONITOR / LOG_CRASH_REPORT / LOG_LEVEL_STORAGE / LOG_INTEGRITY / LOG_FIELD_COMPLIANCE / LOG_TRACE / LOG_SECURITY / LOG_THIRD_PARTY / LOG_ISOLATION / LOG_REPORT_FAULT_TOLERANT）

---

## TP 库文件清单

| 字母 | 子类 | 子类代码 | TP 库文件 | 状态 |
|------|------|---------|----------|------|
| A | 玩家行为埋点 | `LOG_EVENT_TRACK` | [A_event_track.md](./A_event_track.md) | ⏳ 待补 |
| B | 资产审计 | `LOG_ASSET_AUDIT` | [B_asset_audit.md](./B_asset_audit.md) | ⏳ 待补 |
| C | 全量业务操作 | `LOG_OPERATION` | [C_operation.md](./C_operation.md) | ⏳ 待补 |
| D | 服务监控埋点 | `LOG_MONITOR` | [D_monitor.md](./D_monitor.md) | ⏳ 待补 |
| E | 客户端崩溃 | `LOG_CRASH_REPORT` | [E_crash_report.md](./E_crash_report.md) | ⏳ 待补 |
| F | 分级存储&生命周期 | `LOG_LEVEL_STORAGE` | [F_level_storage.md](./F_level_storage.md) | ⏳ 待补 |
| G | 完整性校验 | `LOG_INTEGRITY` | [G_integrity.md](./G_integrity.md) | ⏳ 待补 |
| H | 字段合规 | `LOG_FIELD_COMPLIANCE` | [H_field_compliance.md](./H_field_compliance.md) | ⏳ 待补 |
| I | 线上问题溯源 | `LOG_TRACE` | [I_trace.md](./I_trace.md) | ⏳ 待补 |
| J | 安全&反作弊 | `LOG_SECURITY` | [J_security.md](./J_security.md) | ⏳ 待补 |
| K | 第三方关联链路 | `LOG_THIRD_PARTY` | [K_third_party.md](./K_third_party.md) | ⏳ 待补 |
| L | 多语言/多渠道隔离 | `LOG_ISOLATION` | [L_isolation.md](./L_isolation.md) | ⏳ 待补 |
| M | 日志上报容错 | `LOG_REPORT_FAULT_TOLERANT` | [M_report_fault_tolerant.md](./M_report_fault_tolerant.md) | ⏳ 待补 |

---

## LOG vs AUX 严格隔离（**v1.9 核心**）

| 归 LOG | 不归 LOG（归其他模块）|
|--------|---------------------|
| 业务埋点触发规则、字段规范、链路串联 | 日志采集 SDK、断网缓存 → **AUX** |
| 资产审计流水、batch_id 聚合对账 | 本地文件读写、Redis 缓存 → **AUX** |
| 全量操作日志留痕、覆盖率 100% | 通用网络层、断线重连 → **AUX** |
| 服务监控业务指标埋点、告警 | 通用性能组件、FPS 监控 → **AUX K** |
| 客户端崩溃日志内容（堆栈+上下文+设备）| 崩溃底层 Native 捕获 → **AUX N** |
| 日志分级/生命周期/冷热分离 | 通用 localStorage 工具 → **AUX J** |
| 日志完整性、幂等、链路一致 | 加密算法（AES/SHA）→ **AUX M** |
| 字段必填、隐私脱敏、未成年人隔离 | — |
| 全链路 TraceID 串联、检索、导出 | 业务流程本身（购买扣款/发货）→ **BIZ** |
| 安全/反作弊/封禁/异地/批量建号日志留痕 | 反作弊业务逻辑、检测算法 → **SPECIAL** |
| 第三方交互日志留痕、回调全链路 | 第三方业务集成（微信/支付宝）→ **LINK** |
| 多语言/多渠道/灰度/测试服日志隔离 | 渠道业务（iOS/Android 分包）→ **LINK** |
| 断网缓存、批量合并、重试、分片、压缩 | 通用网络层（HTTP 客户端）→ **AUX B** |

> **判定口诀**：（1）测"业务侧应该写什么日志、写什么字段、字段怎么脱敏、链路怎么串联" → **LOG**；（2）测"S SDK 怎么采集、文件怎么写、网络怎么传" → **AUX**。

---

## LOG vs BIZ-I 边界切分

- **`LOG_ASSET_AUDIT`**：测"全链路流水可对账"——跨业务正负匹配、batch_id 聚合、跨服对账、可导出
- **`BIZ_AUDIT_LOG`**：测"业务侧落点规范"——单笔业务日志格式正确、字段齐全、有审计链
- 同一笔业务 → BIZ-I 校验"是否写日志"，LOG 校验"日志能否对账"

---

## 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引（待补 TP 模板）|
