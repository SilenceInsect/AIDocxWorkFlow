# LOG 模块测试点模板（概览）

> **模块代码**：`LOG`
> **来源**：`.cursor/MODULES.md` §1 总表 + 用户细化定义（9 段 + 4 新增大类）
> **作用**：S5 生成 LOG 模块测试点时，按 story 实际涉及子类**按需加载**对应子模板。
>
> **完整覆盖范围**（一句话）：
> 全场景玩家生命周期 & 功能操作行为埋点；货币/道具/付费全链路资产审计流水；玩家、GM 运营、定时任务全量业务操作日志；
> 服务性能指标、业务转化率、异常拦截监控埋点；客户端崩溃堆栈、业务报错异常日志并附带上下文快照；
> 日志分级区分存储、冷热数据归档、定时生命周期清理；全链路 TraceID 串联、日志完整性对账校验、宕机断线缓存补报；
> 埋点必填字段统一规范、隐私信息脱敏、渠道合规字段校验；安全反作弊拦截日志、第三方外部交互链路日志；
> 日志检索溯源、线上问题复盘导出校验。**日志底层采集/存储/上报 SDK、文件读写工具归 AUX 模块，本模块仅覆盖日志业务规范、审计、埋点触发与合规校验规则**。

---

## 子类索引

| 字母 | 子类名 | 子类代码（v1.2 枚举） | 模板 | 细化段 |
|------|--------|----------------------|------|--------|
| A | 玩家行为埋点采集 | `LOG_EVENT_TRACK` | [A_event_track.md](./LOG/A_event_track.md) | 用户细化 §1 |
| B | 资产产出消耗审计 | `LOG_ASSET_AUDIT` | [B_asset_audit.md](./LOG/B_asset_audit.md) | 用户细化 §2 |
| C | 全量业务操作日志 | `LOG_OPERATION` | [C_operation.md](./LOG/C_operation.md) | 用户细化 §3 |
| D | 服务监控埋点 | `LOG_MONITOR` | [D_monitor.md](./LOG/D_monitor.md) | 用户细化 §4 |
| E | 客户端崩溃/报错 | `LOG_CRASH_REPORT` | [E_crash_report.md](./LOG/E_crash_report.md) | 用户细化 §5 |
| F | 日志分级存储&生命周期 | `LOG_LEVEL_STORAGE` | [F_level_storage.md](./LOG/F_level_storage.md) | 用户细化 §6 |
| G | 日志完整性校验 | `LOG_INTEGRITY` | [G_integrity.md](./LOG/G_integrity.md) | 用户细化 §7 |
| H | 埋点字段合规 | `LOG_FIELD_COMPLIANCE` | [H_field_compliance.md](./LOG/H_field_compliance.md) | 用户细化 §8 |
| I | 线上问题溯源 | `LOG_TRACE` | [I_trace.md](./LOG/I_trace.md) | 用户细化 §9 |
| J | 安全&反作弊日志 | `LOG_SECURITY` | [J_security.md](./LOG/J_security.md) | 用户细化 §10（新增）|
| K | 第三方关联链路 | `LOG_THIRD_PARTY` | [K_third_party.md](./LOG/K_third_party.md) | 用户细化 §11（新增）|
| L | 多语言/多渠道隔离 | `LOG_ISOLATION` | [L_isolation.md](./LOG/L_isolation.md) | 用户细化 §12（新增）|
| M | 日志上报容错 | `LOG_REPORT_FAULT_TOLERANT` | [M_report_fault_tolerant.md](./LOG/M_report_fault_tolerant.md) | 用户细化 §13（新增）|
| O | 边界区分 | —（判定规则，非测试类型）| [O_boundary.md](./LOG/O_boundary.md) | §4 边界（重点 AUX/LOG 隔离）|
| P | 游戏专项 | —（游戏项目专项）| [P_game_specific.md](./LOG/P_game_specific.md) | §5 游戏专项 |

> **结构说明**：
> - A-I 覆盖用户给的 9 段原有日志（行为/资产/操作/监控/崩溃/分级/完整性/合规/溯源）
> - J-M 覆盖用户给的 4 大类"原定义完全缺失"补充（安全/第三方/隔离/上报容错）
> - O/P 是判定规则和游戏专项
> - 13 个 v1.2 枚举全部带 `LOG_` 前缀以避免与其他模块枚举撞名

---

## 加载规则（S5 prompt 使用方式）

1. **检测** `epic.module == "LOG"` → 必读本概览
2. **按 story 内容** 识别涉及的子类（如"购买日志"→ 涉及 A 行为埋点 + B 资产审计 + C 操作日志 + H 字段合规）
3. **按需加载** 对应子模板
4. **交叉参考** `O_boundary.md` 防止误标 LOG 标签（实际是 AUX / BIZ / SPECIAL / LINK / UI）

---

## 边界总览（与 AUX 严格隔离）

> ⚠️ **核心原则**：LOG = 日志**业务规范 + 审计 + 埋点触发 + 合规**；
> AUX = 日志**底层采集 SDK + 文件读写 + 网络上报框架**。两者**严格隔离、无职责重叠**。

| 归 LOG | 不归 LOG（归其他模块）|
|------------|--------------------------|
| 玩家行为埋点业务触发规则 | 日志采集 SDK、底层打印工具（归 AUX）|
| 资产产出消耗审计流水 | 本地文件读写框架（归 AUX）|
| 全量业务操作日志留痕 | 网络上报底层框架（归 AUX）|
| 服务监控埋点业务指标 | 日志压缩分片工具（归 AUX）|
| 客户端崩溃堆栈 + 上下文 | 通用 localStorage 工具（归 AUX J）|
| 日志分级/分层/生命周期规范 | Redis 缓存（归 AUX C）|
| 日志完整性/一致性校验 | 通用网络断线重连（归 AUX B）|
| 埋点字段合规/脱敏 | 加密算法（归 AUX M）|
| 全链路 TraceID 串联 | 全局崩溃捕获（归 AUX N）|
| 安全/反作弊日志留痕 | — |
| 第三方交互日志留痕 | 第三方业务（归 LINK）|
| 多语言/多渠道日志隔离 | 渠道业务（归 LINK）|
| 上报容错/重试/分片 | 业务异常处理（归 BIZ）|

> 完整边界规则见 [`O_boundary.md`](./LOG/O_boundary.md)

---

## 关键词快速映射

| 关键词 / 上下文 | 子类 |
|----------------|------|
| 玩家点击、登录、登出、行为触发、生命周期、路径 | A 玩家行为埋点 |
| 货币、道具、装备、付费、对账、流水、batch_id | B 资产产出消耗审计 |
| 领奖、限购、竞技、拍卖、公会、GM 操作、定时任务 | C 全量业务操作日志 |
| 性能指标、QPS、CCU、DAU、转化率、异常告警 | D 服务监控埋点 |
| 崩溃、ANR、OOM、NPE、堆栈、上下文 | E 客户端崩溃/报错 |
| FATAL/ERROR/WARN/INFO/DEBUG、分级、冷热、生命周期 | F 日志分级存储 |
| 链路完整、幂等、一致性、断线补传 | G 日志完整性校验 |
| 必填字段、脱敏、隐私、GDPR、未成年人 | H 埋点字段合规 |
| TraceID、跨服务、跨服、上下文、检索、导出 | I 线上问题溯源 |
| 作弊、篡改、限流、封禁、异地、风控告警 | J 安全&反作弊日志 |
| 渠道回调、支付回调、外部 API、跨服同步 | K 第三方关联链路 |
| iOS/Android、渠道、灰度、测试服/正式服、时区、币种 | L 多语言/多渠道隔离 |
| 断网缓存、批量合并、重试、分片、压缩、不阻塞 | M 日志上报容错 |

---

## 进度

- v1.0 (2026-06-15)：LOG 模块 13 测试子模板（A-M）+ 2 规则（O/P）全部到位
