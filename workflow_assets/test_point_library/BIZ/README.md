# BIZ 模块 TP 库

> **TP 库位置**：`workflow_assets/test_point_library/BIZ/`
> **子模板来源**：`workflow_assets/module_templates/BIZ/`
> **v1.2 枚举数**：9（BIZ_LOGIC / BIZ_DATA_FLOW / BIZ_PROTOCOL / BIZ_STATE_MACHINE / BIZ_DB_PERSIST / BIZ_CONCURRENCY / BIZ_SCHEDULED_TASK / BIZ_PAYMENT / BIZ_AUDIT_LOG）

---

## TP 库文件清单

| 字母 | 子类 | 子类代码 | TP 库文件 | 状态 |
|------|------|---------|----------|------|
| A | 核心业务逻辑 | `BIZ_LOGIC` | [A_biz_logic.md](./A_biz_logic.md) | ⏳ 待补 |
| B | 端服数据流 | `BIZ_DATA_FLOW` | [B_data_flow.md](./B_data_flow.md) | ⏳ 待补 |
| C | 协议交互 | `BIZ_PROTOCOL` | [C_protocol.md](./C_protocol.md) | ⏳ 待补 |
| D | 状态机 | `BIZ_STATE_MACHINE` | [D_state_machine.md](./D_state_machine.md) | ⏳ 待补 |
| E | 数据库持久化 | `BIZ_DB_PERSIST` | [E_db_persist.md](./E_db_persist.md) | ⏳ 待补 |
| F | 并发/多玩家 | `BIZ_CONCURRENCY` | [F_concurrency.md](./F_concurrency.md) | ⏳ 待补 |
| G | 定时&异步任务 | `BIZ_SCHEDULED_TASK` | [G_scheduled_task.md](./G_scheduled_task.md) | ⏳ 待补 |
| H | 付费&商业化 | `BIZ_PAYMENT` | [H_payment.md](./H_payment.md) | ⏳ 待补 |
| I | 日志与审计 | `BIZ_AUDIT_LOG` | [I_audit_log.md](./I_audit_log.md) | ⏳ 待补 |

---

## BIZ vs LOG 边界（**审计日志必读**）

> **BIZ-I `BIZ_AUDIT_LOG`** 测"业务侧落点是否完整"——单笔业务日志格式正确、字段齐全、有审计链。
> **LOG-B `LOG_ASSET_AUDIT`** 测"全链路流水可对账"——跨业务正负匹配、batch_id 聚合、跨服对账、可导出。
>
> **同一笔业务 → BIZ-I 校验"是否写日志"，LOG 校验"日志能否对账"**——无重叠。
> 完整边界见 [`module_templates/BIZ/O_boundary.md`](../../module_templates/BIZ/O_boundary.md) + [`module_templates/LOG/O_boundary.md`](../../module_templates/LOG/O_boundary.md)。

---

## 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引（待补 TP 模板）|
