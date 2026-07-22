# UTIL 模块 TP 库

> **TP 库位置**：`knowledge/public/test_point_library/UTIL/`
> **子模板来源**：`knowledge/public/module_templates/UTIL/`
> **v1.2 枚举数**：14（COMMON_UTIL / NETWORK_LAYER / CACHE_HIT_RATE / RESOURCE_MGMT / CURRENCY_EXCHANGE / OFFLINE_UPDATE / GM_TOOL / TEST_SCRIPT / ACCEPTANCE_CHECKLIST / LOCAL_STORAGE / PERF_TOOL / OPS_TOOL / SECURITY / ERROR_RECOVERY）

---

## TP 库文件清单

| 字母 | 子类 | 子类代码 | TP 库文件 | 状态 |
|------|------|---------|----------|------|
| A | 公共工具 | `COMMON_UTIL` | [A_common_util.md](./A_common_util.md) | ⏳ 待补 |
| B | 网络层 | `NETWORK_LAYER` | [B_network_layer.md](./B_network_layer.md) | ⏳ 待补 |
| C | 缓存层 | `CACHE_HIT_RATE` | [C_cache_layer.md](./C_cache_layer.md) | ⏳ 待补 |
| D | 资源管理 | `RESOURCE_MGMT` | [D_resource_mgmt.md](./D_resource_mgmt.md) | ⏳ 待补 |
| E | 汇率换算 | `CURRENCY_EXCHANGE` | [E_currency_exchange.md](./E_currency_exchange.md) | ⏳ 待补 |
| F | 离线/版本更新 | `OFFLINE_UPDATE` | [F_offline_update.md](./F_offline_update.md) | ⏳ 待补 |
| G | GM 工具 | `GM_TOOL` | [G_gm_tool.md](./G_gm_tool.md) | ⏳ 待补 |
| H | 测试脚本 | `TEST_SCRIPT` | [H_test_script.md](./H_test_script.md) | ⏳ 待补 |
| I | 策划验收 | `ACCEPTANCE_CHECKLIST` | [I_acceptance_checklist.md](./I_acceptance_checklist.md) | ⏳ 待补 |
| J | 本地存储 | `LOCAL_STORAGE` | [J_storage.md](./J_storage.md) | ⏳ 待补 |
| K | 画质/性能 | `PERF_TOOL` | [K_perf_tool.md](./K_perf_tool.md) | ⏳ 待补 |
| L | 运营辅助 | `OPS_TOOL` | [L_ops_tool.md](./L_ops_tool.md) | ⏳ 待补 |
| M | 加密安全 | `SECURITY` | [M_security.md](./M_security.md) | ⏳ 待补 |
| N | 异常兜底 | `ERROR_RECOVERY` | [N_error_recovery.md](./N_error_recovery.md) | ⏳ 待补 |

---

## UTIL 与其他模块的边界（**v1.6.1 严格隔离**）

| 对比模块 | UTIL 测 | 其他模块测 |
|----------|--------|------------|
| vs **HINT** | 底层通知框架 API | 通知内容/触发逻辑 |
| vs **LOG** | 日志底层 SDK/采集框架 | 业务埋点规范/审计/合规 |
| vs **LINK** | 网络底层传输（TCP/长连接）| 业务层面第三方/跨服通信 |
| vs **SPECIAL** | 底层网络重连/崩溃捕获 | 业务安全/极端场景校验 |
| vs **UI** | UI 框架底层 API | 页面控件渲染/布局 |
| vs **BIZ** | 底层工具（断线重连/缓存）| 业务流程（充值/任务）|
| vs **CONFIG** | GM 工具底层（执行层）| GM 权限/参数配置（声明层）|

> **UTIL = "水管"**——只管底层能力底座，**不**含业务联动逻辑。
> 完整边界见 [`module_templates/UTIL/O_boundary.md`](../../module_templates/UTIL/O_boundary.md)。

---

## 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引（待补 TP 模板）|
