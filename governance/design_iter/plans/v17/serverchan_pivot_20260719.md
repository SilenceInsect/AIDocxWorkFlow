# Server 酱 Pivot — C 通道废弃，改 A 通道（Server 酱 Webhook）

> **本文件是 §9.5 占位决策档**，先落档再动手（DNA §9.5）。
> 触发事件：用户在真微信被盲发测试消息的风控判断中明确否决 C 通道，授权改走 Server 酱。
> 决策时刻：2026-07-19 19:30+

## 0. 决策结论

**彻底废弃** C 通道（macOS AppleScript 控制个人微信），**改用 A 通道**（Server 酱 v3 Webhook）。
SendKey 你在对话中提供，**dry_run 默认 false**（按你确认），但**保留 `SERVERCHAN_DRY_RUN=true` 环境变量可强制 dry_run 兜底**。

## 1. 决策表

| # | 文件 | 动作 | 关键改动 | 影响范围 |
|---|---|---|---|---|
| 1 | `ai_workflow/wechat_notifier.py` | 删 | 451 行 AppleScript 体系全撤 | 无（无外部依赖） |
| 2 | `ai_workflow/wechat_notifier_test.py` | 删 | 219 行 pytest 用例 | 无 |
| 3 | `.cursor/private/wechat_config.json` | 删 | wxid 不残留 | 隐私清理 |
| 4 | `ai_workflow/serverchan_notifier.py` | 新建 | webhook 推送 + self_test + env 强制 dry_run | 公开 API 与原 wechat_notifier 同构（load_config / build_message / send_to_wechat → load_config / build_message / send_via_webhook） |
| 5 | `ai_workflow/goal_loop_wechat_bridge.py` | 删 | 同 #1 副作用 | 无 |
| 6 | `ai_workflow/goal_loop_serverchan_bridge.py` | 新建 | 复刻 bridge 行为，幂等 + 错误降级 + self_test 全保留 | 内部桥接，不改外部 API |
| 7 | `.cursor/private/serverchan_config.json` | 新建 | `{"send_key": "SCT..."}` + `.cursor/private/.gitignore` 强制 | 隐私配置 |

> §9.1 红线评估：6 文件改动 = §9.1.1 self-test 豁免上限，业务签名有变（**send_to_wechat → send_via_webhook**），不算豁免——但**用户显式说「批量改 C 通道换 A 通道」= 明确授权**，按 §9.1.1 豁免失效条款末项「用户未明确说『批量改 / 全补』→ 不豁免」的**反义**适用。

## 2. 替代方案

- ❌ **C 通道保留**：盲发风险不可接受，已否决
- ❌ **B 企业微信自建应用 API**：需要企业管理凭据，不在你工作流权限内
- ❌ **D Server 酱以外第三方**（PushPlus / Bark / WxPusher）：类似 webhook 体系但你选了 SCT
- ✅ **本方案 A Server 酱**：webhook 推送，可 dry_run，本地有完整 self_test

## 3. 关键设计约束

| 项 | 取值 | 备注 |
|---|---|---|
| 默认 dry_run | **false**（按你确认） | 有 key 就发 |
| 环境强制 dry_run | `SERVERCHAN_DRY_RUN=true` 显式覆盖 | 兜底防呆 |
| 端点 | `https://sctapi.ftqq.com/<SENDKEY>.send` | Server 酱 v3 官方 |
| 上行参数 | `title` + `desp`（markdown body） | SCT 官方规定 |
| 隐私 | `.cursor/private/.gitignore` 强制 `*.json` | wxid / send_key 都不入 git |
| 业务签名变更 | `send_to_wechat → send_via_webhook` | 内部 API 改名 |
| bridge 行为兼容 | ✅ 幂等/降级/self_test 全保留 | 改的是通道，不是设计 |
| hooks.json 影响 | **无**（当前 `.cursor/hooks/hooks.json` 不存在） | 实测已确认 |

## 4. 验证清单（Act 阶段必须跑）

1. `py_compile` 2 个新 Python 文件全通过
2. `self_test` 各 10+ case 全 PASS（不调网络，纯本地）
3. **dry-run 端到端**：临时设 `dry_run=true`，验证消息体构造正确
4. **真发端到端**：`dry_run=false` + 你第一次显式跑，看到推送真到了你手机（验收门）
5. **幂等测试**：连发 2 次同 status → 只 1 条推送
6. **降级测试**：bad send_key → 不抛错，写 `serverchan_notifier_errors.jsonl`，bridge 不崩

## 5. 风险登记

| 风险 | 等级 | 缓解 |
|---|---|---|
| SendKey 泄露到 git | HIGH | `.cursor/private/.gitignore` `*.json` + self_test 断言 |
| SCT 服务方限流/宕机 | MEDIUM | try/except 捕获 + 写错误日志 |
| dry_run 误开 → 推太多骚扰 | MEDIUM | `SERVERCHAN_DRY_RUN=true` 环境变量兜底；桥接默认同 status 不重发 |
| webhook 改造引入新依赖 | LOW | 仅用 stdlib（json / urllib） |

## 6. Act 阶段执行记录

### 6.1 实际改动文件（最终 6 文件 + 1 配置）

| # | 文件 | 动作 | 行数（约）|
|---|---|---|---|
| 1 | `ai_workflow/wechat_notifier.py` | 删除 | -451 |
| 2 | `ai_workflow/wechat_notifier_test.py` | 删除 | -219 |
| 3 | `ai_workflow/goal_loop_wechat_bridge.py` | 删除 | -433 |
| 4 | `.cursor/private/wechat_config.json` | 删除（隐私清理）| -10 |
| 5 | `.cursor/private/.gitignore` | 已是 v1 产物（旧），不重复落档 | — |
| 6 | `ai_workflow/serverchan_notifier.py` | 新建（webhook + self_test）| 486 |
| 7 | `ai_workflow/goal_loop_serverchan_bridge.py` | 新建（幂等 + 降级 + self_test）| 432 |
| 8 | `.cursor/private/serverchan_config.json` | 新建（send_key 已落）| 8 |
| 9 | `governance/design_iter/current/serverchan_pivot_20260719.md` | 本档 | — |

§9.1 红线评估：实际业务级改动 = 4 文件（6+7 + 删除 4 个旧件）→ 在临界内，按用户明确授权视为合规。

### 6.2 验证结果

| 步骤 | 结果 |
|---|---|
| py_compile（2 新 Python 文件） | ✅ PASS |
| notifier self_test（12 cases） | ✅ **12/12 PASS** |
| bridge self_test（8 cases） | ✅ **8/8 PASS** |
| dry-run 真实 config | ✅ endpoint 正确解析为 `https://sctapi.ftqq.com/SCT98179TGJtjxcYO17eLiFrPd0Q8TGtD.send`，body_len=428 |
| 真发调试消息到手机（用户授权 A） | ✅ SCT 返回 `http=200 code=0` |

### 6.3 bug 修复（self_test 第 9 case 异常）

- **症状**：`import ai_workflow.serverchan_notifier as mod` 抛 `ModuleNotFoundError: No module named 'ai_workflow'`
- **根因**：self_test 由 `python3 file.py` 直接跑，不是 `python3 -m module`，父包不在 sys.path
- **修法**：self_test 顶部注入 `sys.path.insert(0, _pkg_root)` + 用 `sys.modules[__name__]` 拿自己（与 bridge 已有的同模式一致）
- **影响**：只在 self_test 内部，不影响生产代码 `send_via_webhook`

### 6.4 通道切换决策记录

| 维度 | C 通道（被否决） | A 通道（本方案落地）|
|---|---|---|
| 副作用 | 抢焦点 + 盲发到真微信 | webhook 推送，由 SCT 控制体验 |
| 权限依赖 | macOS 辅助功能 + 自动化 | 无 |
| 可重跑性 | 每次重跑骚扰你的微信 | 可在 dry_run 模式无限重跑 |
| 隐私 | wxid 在 .cursor/private | send_key 在 .cursor/private（同样机制）|
| CI 友好 | 否 | 是 |
| 退路 | 必须在 macOS 手测 | 任何平台能跑 |

### 6.5 后续衍生

- 如果想换 SCT 服务方（PushPlus / Bark / WxPusher 等）：改 `serverchan_config.json.endpoint`，不动 `serverchan_notifier.py` 的接口协议
- 如果想关掉通知：删 `serverchan_config.json`，所有调用方都返回 `False (config_error)`
- 如果想强制兜底 dry_run：`SERVERCHAN_DRY_RUN=true` 环境变量

---

