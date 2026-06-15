# LINK 模块 TP 库

> **TP 库位置**：`workflow_assets/test_point_library/LINK/`
> **子模板来源**：`workflow_assets/module_templates/LINK/`
> **v1.2 枚举数**：6（INTERNAL_BIZ_LINKAGE / CROSS_SERVER_SYNC / MULTI_CLIENT_SYNC / EXTERNAL_THIRD_PARTY / CROSS_MODULE_RESOURCE / OUTBOUND_DATA）

---

## TP 库文件清单

| 字母 | 子类 | 子类代码 | TP 库文件 | 状态 |
|------|------|---------|----------|------|
| A | 内部业务关联 | `INTERNAL_BIZ_LINKAGE` | [A_internal_biz_linkage.md](./A_internal_biz_linkage.md) | ⏳ 待补 |
| B | 跨服务分布式 | `CROSS_SERVER_SYNC` | [B_cross_server_sync.md](./B_cross_server_sync.md) | ⏳ 待补 |
| C | 多端一致性 | `MULTI_CLIENT_SYNC` | [C_multi_client_sync.md](./C_multi_client_sync.md) | ⏳ 待补 |
| D | 外部第三方 | `EXTERNAL_THIRD_PARTY` | [D_external_third_party.md](./D_external_third_party.md) | ⏳ 待补 |
| E | 跨模块资源互通 | `CROSS_MODULE_RESOURCE` | [E_cross_module_resource.md](./E_cross_module_resource.md) | ⏳ 待补 |
| F | 对外数据透出 | `OUTBOUND_DATA` | [F_outbound_data.md](./F_outbound_data.md) | ⏳ 待补 |

---

## AUX vs LINK 核心区分（**"水管 vs 业务"**）

| 维度 | AUX 辅助 | LINK 关联 |
|------|---------|----------|
| 定位 | 底层通用框架/工具/SDK/传输基础设施 | 业务层面的关联/互通/外部对接逻辑 |
| 职责 | 提供"能力底座"，**不含业务联动逻辑** | 基于 AUX 底层能力，实现**业务互通规则、数据同步约束、上下游联动** |
| 典型 | 网络长连接、协议编解码、SDK 加密、消息队列底层、HTTP 请求工具、TCP 重连 | 支付下单+回调解析+补发、跨服组队数据同步、多端登录冲突、第三方登录角色绑定 |
| **一句话** | **AUX 是"水管"** | **LINK 是"水管里流通什么业务数据、两端业务怎么对齐"** |

> 完整边界见 [`module_templates/LINK/O_boundary.md`](../../module_templates/LINK/O_boundary.md)（含 7 大类边界 + 7 误判案例 + 判定流程图 + 6 子类口诀）。

---

## 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引（待补 TP 模板）|
