# 测试点库总索引（8 模块 × 4 类型 × 子类三级）

> **本文件**：S5 阶段的快速查询入口——按模块/类型/子类三维定位 TP 模板。
> **底层数据**：`knowledge/public/test_point_library/<MODULE>/` 下各 `.md` 文件
> **维护原则**：与 `.cursor/MODULES.md` §1 总表 + §4 矩阵 + `module_templates/` 严格对齐

---

## 0. 一句话总览

| 维度 | 数量 | 备注 |
|------|------|------|
| 模块数 | 8 | CONFIG / UI / BIZ / AUX / LINK / SPECIAL / LOG / HINT |
| 类型数 | 4 | POSITIVE / BOUNDARY / NEGATIVE / EXCEPTION |
| 子类数（v1.7+ 累计）| 87 | 跨 8 模块 |
| TP 库文件 | 87 | 每个子类 1 个 `.md` |
| TP 模板目标 | 1000+ | 每个 `.md` 10-20 个 TP 模板 |

---

## 1. 8 模块 × 子类索引

| # | 模块 | 子类数 | 子模板文件 | TP 库目录 |
|---|------|-------|-----------|----------|
| 1 | **CONFIG**（配置）| 9 + 边界 + 专项 = 11 | [`module_templates/CONFIG/`](../module_templates/CONFIG/) | [`CONFIG/`](./CONFIG/) |
| 2 | **UI**（界面）| 8 + 边界 + 专项 = 10 | [`module_templates/UI/`](../module_templates/UI/) | [`UI/`](./UI/) |
| 3 | **BIZ**（业务）| 9 + 边界 + 专项 = 11 | [`module_templates/BIZ/`](../module_templates/BIZ/) | [`BIZ/`](./BIZ/) |
| 4 | **AUX**（辅助）| 14 + 边界 + 专项 = 16 | [`module_templates/AUX/`](../module_templates/AUX/) | [`AUX/`](./AUX/) |
| 5 | **LINK**（关联）| 6 + 边界 + 专项 = 8 | [`module_templates/LINK/`](../module_templates/LINK/) | [`LINK/`](./LINK/) |
| 6 | **SPECIAL**（特殊）| 9 + 边界 + 专项 = 11 | [`module_templates/SPECIAL/`](../module_templates/SPECIAL/) | [`SPECIAL/`](./SPECIAL/) |
| 7 | **LOG**（日志）| 13 + 边界 + 专项 = 15 | [`module_templates/LOG/`](../module_templates/LOG/) | [`LOG/`](./LOG/) |
| 8 | **HINT**（提示）| 13 + 边界 + 专项 = 16 | [`module_templates/HINT/`](../module_templates/HINT/) | [`HINT/`](./HINT/) |
| **合计** | | **98** | | **98 个 TP 库文件** |

---

## 2. CONFIG（配置）— 9 测试子模板

| 字母 | 子类 | 子类代码（v1.2）| 模板 | TP 库 |
|------|------|----------------|------|------|
| A | 字段合法性 | `FIELD_LEGALITY` | [A_field_legality.md](../module_templates/CONFIG/A_field_legality.md) | [A_field_legality.md](./CONFIG/A_field_legality.md) |
| B | 同表一致性 | `FIELD_INTRA_DEP` | [B_consistency.md](../module_templates/CONFIG/B_consistency.md) | [B_consistency.md](./CONFIG/B_consistency.md) |
| C | 跨表依赖 | `FIELD_CROSS_DEP` | [C_cross_dep.md](../module_templates/CONFIG/C_cross_dep.md) | [C_cross_dep.md](./CONFIG/C_cross_dep.md) |
| D | 热更新 | `RELOAD_4_MODE` | [D_hot_reload.md](../module_templates/CONFIG/D_hot_reload.md) | [D_hot_reload.md](./CONFIG/D_hot_reload.md) |
| E | 解析加载 | `PARSE_LOAD` | [E_parse_load.md](../module_templates/CONFIG/E_parse_load.md) | [E_parse_load.md](./CONFIG/E_parse_load.md) |
| F | 版本兼容 | `VERSION_COMPAT` | [F_version_compat.md](../module_templates/CONFIG/F_version_compat.md) | [F_version_compat.md](./CONFIG/F_version_compat.md) |
| G | 数值逻辑 | `VALUE_LOGIC` | [G_value_logic.md](../module_templates/CONFIG/G_value_logic.md) | [G_value_logic.md](./CONFIG/G_value_logic.md) |
| H | 导出发布 | `EXPORT_PUBLISH` | [H_export_publish.md](../module_templates/CONFIG/H_export_publish.md) | [H_export_publish.md](./CONFIG/H_export_publish.md) |
| I | 服务端专属 | `SERVER_CONFIG` | [I_server_specific.md](../module_templates/CONFIG/I_server_specific.md) | [I_server_specific.md](./CONFIG/I_server_specific.md) |

---

## 3. UI（界面）— 8 测试子模板

| 字母 | 子类 | 子类代码（v1.2）| 模板 | TP 库 |
|------|------|----------------|------|------|
| A | 控件基础 | `CONTROL_RENDER` / `CONTROL_STATE` / `CONTROL_BASE_FUNC` / `CONTROL_BOUNDARY` | [A_control_basic.md](../module_templates/UI/A_control_basic.md) | [A_control_basic.md](./UI/A_control_basic.md) |
| B | 纯前端交互 | `PURE_INTERACTION` | [B_pure_interaction.md](../module_templates/UI/B_pure_interaction.md) | [B_pure_interaction.md](./UI/B_pure_interaction.md) |
| C | 布局适配 | `LAYOUT_ADAPT` | [C_layout_adapt.md](../module_templates/UI/C_layout_adapt.md) | [C_layout_adapt.md](./UI/C_layout_adapt.md) |
| D | 静态展示 | `STATIC_DISPLAY` | [D_static_display.md](../module_templates/UI/D_static_display.md) | [D_static_display.md](./UI/D_static_display.md) |
| E | 动效动画 | `ANIMATION` | [E_animation.md](../module_templates/UI/E_animation.md) | [E_animation.md](./UI/E_animation.md) |
| F | 引导浮窗 | `GUIDE_HINT` | [F_guide_hint.md](../module_templates/UI/F_guide_hint.md) | [F_guide_hint.md](./UI/F_guide_hint.md) |
| G | 无障碍 | `ACCESSIBILITY` | [G_accessibility.md](../module_templates/UI/G_accessibility.md) | [G_accessibility.md](./UI/G_accessibility.md) |
| H | 异常场景 | `EDGE_UI` | [H_edge_ui.md](../module_templates/UI/H_edge_ui.md) | [H_edge_ui.md](./UI/H_edge_ui.md) |

---

## 4. BIZ（业务）— 9 测试子模板

| 字母 | 子类 | 子类代码（v1.2）| 模板 | TP 库 |
|------|------|----------------|------|------|
| A | 核心业务逻辑 | `BIZ_LOGIC` | [A_biz_logic.md](../module_templates/BIZ/A_biz_logic.md) | [A_biz_logic.md](./BIZ/A_biz_logic.md) |
| B | 端服数据流 | `BIZ_DATA_FLOW` | [B_data_flow.md](../module_templates/BIZ/B_data_flow.md) | [B_data_flow.md](./BIZ/B_data_flow.md) |
| C | 协议交互 | `BIZ_PROTOCOL` | [C_protocol.md](../module_templates/BIZ/C_protocol.md) | [C_protocol.md](./BIZ/C_protocol.md) |
| D | 状态机 | `BIZ_STATE_MACHINE` | [D_state_machine.md](../module_templates/BIZ/D_state_machine.md) | [D_state_machine.md](./BIZ/D_state_machine.md) |
| E | 数据库持久化 | `BIZ_DB_PERSIST` | [E_db_persist.md](../module_templates/BIZ/E_db_persist.md) | [E_db_persist.md](./BIZ/E_db_persist.md) |
| F | 并发/多玩家 | `BIZ_CONCURRENCY` | [F_concurrency.md](../module_templates/BIZ/F_concurrency.md) | [F_concurrency.md](./BIZ/F_concurrency.md) |
| G | 定时&异步任务 | `BIZ_SCHEDULED_TASK` | [G_scheduled_task.md](../module_templates/BIZ/G_scheduled_task.md) | [G_scheduled_task.md](./BIZ/G_scheduled_task.md) |
| H | 付费&商业化 | `BIZ_PAYMENT` | [H_payment.md](../module_templates/BIZ/H_payment.md) | [H_payment.md](./BIZ/H_payment.md) |
| I | 日志与审计 | `BIZ_AUDIT_LOG` | [I_audit_log.md](../module_templates/BIZ/I_audit_log.md) | [I_audit_log.md](./BIZ/I_audit_log.md) |

---

## 5. AUX（辅助）— 14 测试子模板

| 字母 | 子类 | 子类代码（v1.2）| 模板 | TP 库 |
|------|------|----------------|------|------|
| A | 公共工具 | `COMMON_UTIL` | [A_common_util.md](../module_templates/AUX/A_common_util.md) | [A_common_util.md](./AUX/A_common_util.md) |
| B | 网络层 | `NETWORK_LAYER` | [B_network_layer.md](../module_templates/AUX/B_network_layer.md) | [B_network_layer.md](./AUX/B_network_layer.md) |
| C | 缓存层 | `CACHE_HIT_RATE` | [C_cache_layer.md](../module_templates/AUX/C_cache_layer.md) | [C_cache_layer.md](./AUX/C_cache_layer.md) |
| D | 资源管理 | `RESOURCE_MGMT` | [D_resource_mgmt.md](../module_templates/AUX/D_resource_mgmt.md) | [D_resource_mgmt.md](./AUX/D_resource_mgmt.md) |
| E | 汇率换算 | `CURRENCY_EXCHANGE` | [E_currency_exchange.md](../module_templates/AUX/E_currency_exchange.md) | [E_currency_exchange.md](./AUX/E_currency_exchange.md) |
| F | 离线/版本更新 | `OFFLINE_UPDATE` | [F_offline_update.md](../module_templates/AUX/F_offline_update.md) | [F_offline_update.md](./AUX/F_offline_update.md) |
| G | GM 工具 | `GM_TOOL` | [G_gm_tool.md](../module_templates/AUX/G_gm_tool.md) | [G_gm_tool.md](./AUX/G_gm_tool.md) |
| H | 测试脚本 | `TEST_SCRIPT` | [H_test_script.md](../module_templates/AUX/H_test_script.md) | [H_test_script.md](./AUX/H_test_script.md) |
| I | 策划验收 | `ACCEPTANCE_CHECKLIST` | [I_acceptance_checklist.md](../module_templates/AUX/I_acceptance_checklist.md) | [I_acceptance_checklist.md](./AUX/I_acceptance_checklist.md) |
| J | 本地存储 | `LOCAL_STORAGE` | [J_storage.md](../module_templates/AUX/J_storage.md) | [J_storage.md](./AUX/J_storage.md) |
| K | 画质/性能 | `PERF_TOOL` | [K_perf_tool.md](../module_templates/AUX/K_perf_tool.md) | [K_perf_tool.md](./AUX/K_perf_tool.md) |
| L | 运营辅助 | `OPS_TOOL` | [L_ops_tool.md](../module_templates/AUX/L_ops_tool.md) | [L_ops_tool.md](./AUX/L_ops_tool.md) |
| M | 加密安全 | `SECURITY` | [M_security.md](../module_templates/AUX/M_security.md) | [M_security.md](./AUX/M_security.md) |
| N | 异常兜底 | `ERROR_RECOVERY` | [N_error_recovery.md](../module_templates/AUX/N_error_recovery.md) | [N_error_recovery.md](./AUX/N_error_recovery.md) |

---

## 6. LINK（关联）— 6 测试子模板

| 字母 | 子类 | 子类代码（v1.2）| 模板 | TP 库 |
|------|------|----------------|------|------|
| A | 内部业务关联 | `INTERNAL_BIZ_LINKAGE` | [A_internal_biz_linkage.md](../module_templates/LINK/A_internal_biz_linkage.md) | [A_internal_biz_linkage.md](./LINK/A_internal_biz_linkage.md) |
| B | 跨服务分布式 | `CROSS_SERVER_SYNC` | [B_cross_server_sync.md](../module_templates/LINK/B_cross_server_sync.md) | [B_cross_server_sync.md](./LINK/B_cross_server_sync.md) |
| C | 多端一致性 | `MULTI_CLIENT_SYNC` | [C_multi_client_sync.md](../module_templates/LINK/C_multi_client_sync.md) | [C_multi_client_sync.md](./LINK/C_multi_client_sync.md) |
| D | 外部第三方 | `EXTERNAL_THIRD_PARTY` | [D_external_third_party.md](../module_templates/LINK/D_external_third_party.md) | [D_external_third_party.md](./LINK/D_external_third_party.md) |
| E | 跨模块资源互通 | `CROSS_MODULE_RESOURCE` | [E_cross_module_resource.md](../module_templates/LINK/E_cross_module_resource.md) | [E_cross_module_resource.md](./LINK/E_cross_module_resource.md) |
| F | 对外数据透出 | `OUTBOUND_DATA` | [F_outbound_data.md](../module_templates/LINK/F_outbound_data.md) | [F_outbound_data.md](./LINK/F_outbound_data.md) |

---

## 7. SPECIAL（特殊情境）— 9 测试子模板

| 字母 | 子类 | 子类代码（v1.2）| 模板 | TP 库 |
|------|------|----------------|------|------|
| A | 边界极端场景 | `BOUNDARY_EXTREME` | [A_boundary_extreme.md](../module_templates/SPECIAL/A_boundary_extreme.md) | [A_boundary_extreme.md](./SPECIAL/A_boundary_extreme.md) |
| B | 反作弊 / 数据安全 | `ANTI_CHEAT` | [B_anti_cheat.md](../module_templates/SPECIAL/B_anti_cheat.md) | [B_anti_cheat.md](./SPECIAL/B_anti_cheat.md) |
| C | 弱网 / 限流 | `WEAK_NET_RATE_LIMIT` | [C_weak_net_rate_limit.md](../module_templates/SPECIAL/C_weak_net_rate_limit.md) | [C_weak_net_rate_limit.md](./SPECIAL/C_weak_net_rate_limit.md) |
| D | 前后台切换 | `BG_FG_SWITCH` | [D_bg_fg_switch.md](../module_templates/SPECIAL/D_bg_fg_switch.md) | [D_bg_fg_switch.md](./SPECIAL/D_bg_fg_switch.md) |
| E | 宕机/并发/高危 | `SERVER_HA_RISK` | [E_server_ha_risk.md](../module_templates/SPECIAL/E_server_ha_risk.md) | [E_server_ha_risk.md](./SPECIAL/E_server_ha_risk.md) |
| F | 版本兼容 | `VERSION_COMPAT_BIZ` | [F_version_compat_biz.md](../module_templates/SPECIAL/F_version_compat_biz.md) | [F_version_compat_biz.md](./SPECIAL/F_version_compat_biz.md) |
| G | 渠道/灰度 | `CHANNEL_GRAY_BIZ` | [G_channel_gray_biz.md](../module_templates/SPECIAL/G_channel_gray_biz.md) | [G_channel_gray_biz.md](./SPECIAL/G_channel_gray_biz.md) |
| H | 合规风控 | `COMPLIANCE_RISK` | [H_compliance_risk.md](../module_templates/SPECIAL/H_compliance_risk.md) | [H_compliance_risk.md](./SPECIAL/H_compliance_risk.md) |
| I | 资源耗尽 | `RESOURCE_EXHAUST` | [I_resource_exhaust.md](../module_templates/SPECIAL/I_resource_exhaust.md) | [I_resource_exhaust.md](./SPECIAL/I_resource_exhaust.md) |

---

## 8. LOG（日志）— 13 测试子模板

| 字母 | 子类 | 子类代码（v1.9）| 模板 | TP 库 |
|------|------|----------------|------|------|
| A | 玩家行为埋点 | `LOG_EVENT_TRACK` | [A_event_track.md](../module_templates/LOG/A_event_track.md) | [A_event_track.md](./LOG/A_event_track.md) |
| B | 资产审计 | `LOG_ASSET_AUDIT` | [B_asset_audit.md](../module_templates/LOG/B_asset_audit.md) | [B_asset_audit.md](./LOG/B_asset_audit.md) |
| C | 全量业务操作 | `LOG_OPERATION` | [C_operation.md](../module_templates/LOG/C_operation.md) | [C_operation.md](./LOG/C_operation.md) |
| D | 服务监控埋点 | `LOG_MONITOR` | [D_monitor.md](../module_templates/LOG/D_monitor.md) | [D_monitor.md](./LOG/D_monitor.md) |
| E | 客户端崩溃 | `LOG_CRASH_REPORT` | [E_crash_report.md](../module_templates/LOG/E_crash_report.md) | [E_crash_report.md](./LOG/E_crash_report.md) |
| F | 分级存储&生命周期 | `LOG_LEVEL_STORAGE` | [F_level_storage.md](../module_templates/LOG/F_level_storage.md) | [F_level_storage.md](./LOG/F_level_storage.md) |
| G | 完整性校验 | `LOG_INTEGRITY` | [G_integrity.md](../module_templates/LOG/G_integrity.md) | [G_integrity.md](./LOG/G_integrity.md) |
| H | 字段合规 | `LOG_FIELD_COMPLIANCE` | [H_field_compliance.md](../module_templates/LOG/H_field_compliance.md) | [H_field_compliance.md](./LOG/H_field_compliance.md) |
| I | 线上问题溯源 | `LOG_TRACE` | [I_trace.md](../module_templates/LOG/I_trace.md) | [I_trace.md](./LOG/I_trace.md) |
| J | 安全&反作弊 | `LOG_SECURITY` | [J_security.md](../module_templates/LOG/J_security.md) | [J_security.md](./LOG/J_security.md) |
| K | 第三方关联链路 | `LOG_THIRD_PARTY` | [K_third_party.md](../module_templates/LOG/K_third_party.md) | [K_third_party.md](./LOG/K_third_party.md) |
| L | 多语言/多渠道隔离 | `LOG_ISOLATION` | [L_isolation.md](../module_templates/LOG/L_isolation.md) | [L_isolation.md](./LOG/L_isolation.md) |
| M | 日志上报容错 | `LOG_REPORT_FAULT_TOLERANT` | [M_report_fault_tolerant.md](../module_templates/LOG/M_report_fault_tolerant.md) | [M_report_fault_tolerant.md](./LOG/M_report_fault_tolerant.md) |

---

## 9. HINT（提示）— 13 测试子模板

| 字母 | 子类 | 子类代码（v1.7）| 模板 | TP 库 |
|------|------|----------------|------|------|
| A | 红点/角标/数字 | `RED_DOT_BADGE` | [A_red_dot_badge.md](../module_templates/HINT/A_red_dot_badge.md) | [A_red_dot_badge.md](./HINT/A_red_dot_badge.md) |
| B | 资源飘字 | `ITEM_FLOAT` | [B_item_float.md](../module_templates/HINT/B_item_float.md) | [B_item_float.md](./HINT/B_item_float.md) |
| C | 战斗飘字 | `CURRENCY_FLOAT` | [C_currency_float.md](../module_templates/HINT/C_currency_float.md) | [C_currency_float.md](./HINT/C_currency_float.md) |
| D | 模态系统弹窗 | `MODAL_DIALOG` | [D_modal_dialog.md](../module_templates/HINT/D_modal_dialog.md) | [D_modal_dialog.md](./HINT/D_modal_dialog.md) |
| E | 轻量 Toast | `TOAST` | [E_toast.md](../module_templates/HINT/E_toast.md) | [E_toast.md](./HINT/E_toast.md) |
| F | 浮动通知/悬浮浮窗 | `FLOAT_NOTIFY` | [F_float_notify.md](../module_templates/HINT/F_float_notify.md) | [F_float_notify.md](./HINT/F_float_notify.md) |
| G | 限时提醒+错误文案 | `TIMED_REMINDER` | [G_timed_reminder.md](../module_templates/HINT/G_timed_reminder.md) | [G_timed_reminder.md](./HINT/G_timed_reminder.md) |
| H | 新手引导高亮 | `GUIDE_HIGHLIGHT` | [H_guide_highlight.md](../module_templates/HINT/H_guide_highlight.md) | [H_guide_highlight.md](./HINT/H_guide_highlight.md) |
| I | 聊天&社交提示 | `SOCIAL_PROMPT` | [I_social_prompt.md](../module_templates/HINT/I_social_prompt.md) | [I_social_prompt.md](./HINT/I_social_prompt.md) |
| J | 运营推送 | `OPS_PUSH_PROMPT` | [J_ops_push_prompt.md](../module_templates/HINT/J_ops_push_prompt.md) | [J_ops_push_prompt.md](./HINT/J_ops_push_prompt.md) |
| K | 状态变更 | `STATE_CHANGE_DIALOG` | [K_state_change_dialog.md](../module_templates/HINT/K_state_change_dialog.md) | [K_state_change_dialog.md](./HINT/K_state_change_dialog.md) |
| L | 风控合规 | `COMPLIANCE_PROMPT` | [L_compliance_prompt.md](../module_templates/HINT/L_compliance_prompt.md) | [L_compliance_prompt.md](./HINT/L_compliance_prompt.md) |
| M | 离线补偿 | `OFFLINE_COMPENSATION` | [M_offline_compensation.md](../module_templates/HINT/M_offline_compensation.md) | [M_offline_compensation.md](./HINT/M_offline_compensation.md) |

---

## 10. 4 类型 × 8 模块 速查表

| 类型 \ 模块 | CONFIG | UI | BIZ | AUX | LINK | SPECIAL | LOG | HINT |
|------------|--------|----|----|-----|------|---------|-----|------|
| **POSITIVE**（正向）| ✅ A_field_legality / B_consistency | ✅ A_control_basic / B_pure_interaction | ✅ A_biz_logic / D_state_machine | ✅ A_common_util / G_gm_tool | ✅ A_internal_biz_linkage | ✅ A_boundary_extreme | ✅ A_event_track | ✅ D_modal_dialog / E_toast |
| **BOUNDARY**（边界）| ✅ F_version_compat / G_value_logic | ✅ C_layout_adapt / H_edge_ui | ✅ E_db_persist / F_concurrency | ✅ C_cache_layer / D_resource_mgmt | ✅ C_multi_client_sync | ✅ A_boundary_extreme | ✅ F_level_storage | ✅ G_timed_reminder |
| **NEGATIVE**（负向）| ✅ C_cross_dep / H_export_publish | ✅ A_control_basic / H_edge_ui | ✅ C_protocol / H_payment | ✅ B_network_layer / M_security | ✅ D_external_third_party | ✅ B_anti_cheat / I_resource_exhaust | ✅ H_field_compliance | ✅ L_compliance_prompt |
| **EXCEPTION**（异常）| ✅ D_hot_reload / E_parse_load | ✅ H_edge_ui | ✅ G_scheduled_task / I_audit_log | ✅ N_error_recovery | ✅ B_cross_server_sync | ✅ C_weak_net / D_bg_fg / E_server_ha / F_version_compat / G_channel_gray | ✅ M_report_fault_tolerant / J_security | ✅ M_offline_compensation |

> **EXCEPTION 类型**优先使用 S4 风险点 + 异常树叶子节点（见 `test_point_gen.md` §3.1）。
> **POSITIVE / BOUNDARY / NEGATIVE** 可直接从 TP 库复用模板。

---

## 11. 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引；目录结构 + 8 模块 × 87 子类映射 |
