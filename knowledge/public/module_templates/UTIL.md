# UTIL 模块测试点模板（概览）

> **模块代码**：`UTIL`
> **来源**：`.cursor/MODULES.md` §1 总表 + 用户细化定义
> **作用**：S5 生成 UTIL 模块测试点时，按 story 实际涉及子类**按需加载**对应子模板。
> **v1.6.1 变更**：**UTIL 模块职责收窄——只保留底层基础工具，剔除日志/提示/第三方/风控**等高层业务辅助。
>
> **完整覆盖范围**（一句话）：
> 底层全局公共工具类、通用基础框架组件；网络底层传输封装、消息队列、断线重连底层能力；
> 客户端本地缓存、服务端 Redis 缓存、缓存生命周期管理；
> 游戏资源加载/引用计数/卸载/分包更新底层能力；多货币汇率换算工具、数值格式化组件；
> 离线资源包底层下载/校验/修复；分级 GM 后台工具、批量造数/自动化测试脚本；
> 本地玩家设置持久化存储；画质帧率性能监控底层组件；
> 整包/增量热更底层更新框架；资源&协议加密安全工具；全局崩溃捕获、底层异常兜底组件。

---

## v1.6.1 裁剪说明（**已全部完成**）

**剔除内容**（**已迁出/已落地**）：

| 剔除项 | 迁移去向 | 状态 |
|---|---|---|
| 日志采集/分级/导出/埋点 SDK | **LOG 模块** | ✅ **v1.9 已落地**（13 枚举 + 15 文件）|
| 红点/弹窗/Toast/飘字（提示）| **HINT 模块** | ✅ **v1.7+ 已落地**（13 枚举 + 16 文件）|
| 第三方 SDK（微信/支付宝/渠道）| **LINK 模块** | ✅ **v1.8 已落地**（6 枚举 + 8 文件）|
| 风控检测/反作弊 | **SPECIAL 模块** | ✅ **v1.11 已落地**（9 枚举 + 11 文件）|
| 业务异常处理（购买失败补偿等）| **BIZ 模块** | ✅ **v1.7 已落地**（9 枚举 + 11 文件）|
| **运营业务（批量发奖/公告后台/活动配置）** | **BIZ 模块** | ✅ **v1.7 已落地** |

> **占位文件清理**：
> - `UTIL/J_log_moved_to_LOG.md`（v1.6.1 占位）—— LOG v1.9 落地后已**删除**
> - `UTIL/L_ops_moved_to_BIZ.md`（v1.6.1+ 占位）—— BIZ v1.7 落地后已**删除**

**保留内容**（v1.6.1 子模板，14 测试子模板 + 2 规则 = **16 文件**）：

| 子类 | 子类代码 | 文件 | 状态 |
|---|---|---|---|
| A 公共工具（底层）| `COMMON_UTIL` | A_common_util.md | ✅ |
| B 网络层（底层）| `NETWORK_LAYER` | B_network_layer.md | ✅ |
| C 缓存层 | `CACHE_HIT_RATE` | C_cache_layer.md | ✅ |
| D 资源管理 | `RESOURCE_MGMT` | D_resource_mgmt.md | ✅ |
| E 汇率换算 | `CURRENCY_EXCHANGE` | E_currency_exchange.md | ✅ |
| F 离线/版本更新 | `OFFLINE_UPDATE` | F_offline_update.md | ✅ |
| G GM 工具 | `GM_TOOL` | G_gm_tool.md | ✅ |
| H 测试脚本 | `TEST_SCRIPT` | H_test_script.md | ✅ |
| I 策划验收 | `ACCEPTANCE_CHECKLIST` | I_acceptance_checklist.md | ✅ |
| J 本地存储（日志已迁出）| `LOCAL_STORAGE` | **J_storage.md**（重命名自 J_storage_log.md）| ✅ |
| K 性能/画质 | `PERF_TOOL` | K_perf_tool.md | ✅ |
| L 运营辅助（底层）| `OPS_TOOL` | L_ops_tool.md | ✅（业务层已迁出）|
| M 加密安全（底层）| `SECURITY` | M_security.md | ✅ |
| N 异常兜底（底层）| `ERROR_RECOVERY` | N_error_recovery.md | ✅（业务异常已迁出）|
| O 边界区分 | — | O_boundary.md | ✅ |
| P 游戏专项 | — | P_game_specific.md | ✅ |

---

## 子类索引

| 字母 | 子类名           | 子类代码（v1.2 枚举）            | 模板                                                                | 细化段 |
| ---- | ---------------- | --------------------------------- | ------------------------------------------------------------------- | ------ |
| A    | 公共工具         | `COMMON_UTIL`                     | [A_common_util.md](./UTIL/A_common_util.md)                          | §1 |
| B    | 网络层           | `NETWORK_LAYER`                   | [B_network_layer.md](./UTIL/B_network_layer.md)                      | §2 |
| C    | 缓存层           | `CACHE_HIT_RATE`                  | [C_cache_layer.md](./UTIL/C_cache_layer.md)                          | §3 |
| D    | 资源管理         | `RESOURCE_MGMT`                   | [D_resource_mgmt.md](./UTIL/D_resource_mgmt.md)                      | §4 |
| E    | 汇率换算         | `CURRENCY_EXCHANGE`               | [E_currency_exchange.md](./UTIL/E_currency_exchange.md)              | §5 |
| F    | 离线/版本更新    | `OFFLINE_UPDATE`                  | [F_offline_update.md](./UTIL/F_offline_update.md)                    | §6+§13 |
| G    | GM 工具          | `GM_TOOL`                         | [G_gm_tool.md](./UTIL/G_gm_tool.md)                                  | §7 |
| H    | 测试脚本         | `TEST_SCRIPT`                     | [H_test_script.md](./UTIL/H_test_script.md)                          | §8 |
| I    | 策划验收         | `ACCEPTANCE_CHECKLIST`            | [I_acceptance_checklist.md](./UTIL/I_acceptance_checklist.md)        | §9 |
| J    | 本地持久化存储 | `LOCAL_STORAGE`（v1.6.1 收窄为仅本地存档）| [J_storage.md](./UTIL/J_storage.md)                                  | §10 |
| K    | 画质/性能        | `PERF_TOOL`                       | [K_perf_tool.md](./UTIL/K_perf_tool.md)                              | §12 |
| L    | 运营辅助         | `OPS_TOOL`                        | [L_ops_tool.md](./UTIL/L_ops_tool.md)                                | §14 |
| M    | 加密安全         | `SECURITY`                        | [M_security.md](./UTIL/M_security.md)                                | §15 |
| N    | 异常兜底         | `ERROR_RECOVERY`                  | [N_error_recovery.md](./UTIL/N_error_recovery.md)                    | §16 |
| O    | 边界区分         | —（判定规则，非测试类型）        | [O_boundary.md](./UTIL/O_boundary.md)                                | §4 边界 |
| P    | 游戏项目补充     | —（游戏项目专项，非通用测试类型）| [P_game_specific.md](./UTIL/P_game_specific.md)                      | §5 游戏 |

> **结构说明**：
> - A-N 是 14 个 v1.2 测试子模板（覆盖你给的 16 大类）
> - F 合并了 §6 离线 + §13 版本更新（两者强相关，共享枚举 `OFFLINE_UPDATE`）
> - J 合并了 §10 本地存储 + §11 日志埋点（v1.6.1 起日志/埋点部分已迁出 LOG 详见 `LOG/O_boundary.md`；J 仅保留本地存档）
> - O/P 是判定规则和游戏专项

---

## 加载规则（S5 prompt 使用方式）

1. **检测** `epic.module == "UTIL"` → 必读本概览
2. **按 story 内容** 识别涉及的子类（如"GM 发道具"→ 涉及 G GM 工具 + M 加密安全 + L 运营辅助）
3. **按需加载** 对应子模板
4. **交叉参考** `O_boundary.md` 防止误标 UTIL 标签（实际是 BIZ / CONFIG / UI / HINT）

---

## 边界总览

| 归 UTIL                              | 不归 UTIL（归其他模块）              |
| ----------------------------------- | ---------------------------------- |
| 底层通用基础能力、工具、框架组件    | 业务流程、玩家交互逻辑 → BIZ       |
| GM / 测试 / 运营工具                | 配置表字段、跨表数值依赖 → CONFIG  |
| 网络 / 缓存 / 资源底层封装          | 页面视觉、前端交互展示 → UI        |
| 离线更新、日志埋点、全局公共工具    | 业务协议的业务逻辑校验 → BIZ       |
| 加密 / 异常兜底 / 性能监控          | 提示内容、状态逻辑 → HINT          |

> 完整边界规则见 [`O_boundary.md`](./UTIL/O_boundary.md)

---

## 关键词快速映射

| 关键词 / 上下文                          | 子类         |
| ---------------------------------------- | ------------ |
| 工具类、组件、封装、路由、埋点、本地存储  | A 公共工具   |
| 网络、断线、重连、心跳、超时、抓包        | B 网络层     |
| 缓存、Redis、过期、刷新、击穿、雪崩       | C 缓存层     |
| 资源、加载、释放、引用、内存、分包        | D 资源管理   |
| 货币、汇率、兑换、比例、取整              | E 汇率换算   |
| 离线、断点续传、版本更新、增量            | F 离线/更新  |
| GM、指令、发奖、补发、权限、审计          | G GM 工具    |
| 自动化、压测、批量造数、回归脚本          | H 测试脚本   |
| 验收、Checklist、复现核对、上线自检       | I 策划验收   |
| 存档、玩家设置、日志、埋点、崩溃          | J 存储+日志  |
| 帧率、画质、内存、卡顿、降帧              | K 性能画质   |
| 公告、邮件、排行榜、对账、灰度            | L 运营辅助   |
| 加密、防篡改、密钥、协议安全              | M 加密安全   |
| 异常、崩溃、修复、重试、降级              | N 异常兜底   |
| 渠道 SDK、省电、模拟器、补偿补发          | P 游戏专项   |

---

## 进度

- v1.6.1 (2026-06-15)：UTIL 模块 14 测试子模板 + 2 规则全部到位（A-P 共 16 文件）；J 重命名 J_storage_log → J_storage（日志/埋点部分迁出 LOG）；N 缩窄为底层（业务异常迁出 BIZ）
- v1.6.1+ (2026-06-15)：UTIL 模块职责收窄——剔除 4 类高层业务辅助（LOG v1.9 / HINT v1.7+ / LINK v1.8 / SPECIAL v1.11 / BIZ v1.7），占位文件 `J_log_moved_to_LOG.md` 和 `L_ops_moved_to_BIZ.md` 全部删除
