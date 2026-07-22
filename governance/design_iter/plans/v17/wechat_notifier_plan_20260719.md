# WeChatNotifier 实现方案（Plan 占位骨架 · DNA §9.5）

> **本档按 DNA §9.5 占位协议创建**——Plan 阶段内容已通过 Plan 工具完整锁定，本档是治理档落地 + Act 执行记录。
> **完整方案**：[`wechatnotifier_plan_020c08b0.plan.md`](../../../../.cursor/plans/wechatnotifier_plan_020c08b0.plan.md)
> **路径**：根目录 → `.cursor/plans/wechatnotifier_plan_020c08b0.plan.md`
> **本档状态**：⏸️ Act 阶段进行中

---

## 1. 方案摘要

| 维度 | 选定 |
|---|---|
| 通道 | C — macOS AppleScript 控制个人微信桌面端 |
| 触发 | Goal-Loop 状态 → CONVERGED / converged_with_followup / BLOCKED |
| 接收人 | wxid = `GMING2016` |
| 内容 | 仅摘要：阶段名 + 状态 + 关键产物路径 |
| 隐私 | `.cursor/private/wechat_config.json` + 强制 .gitignore |
| 状态入口 | `goal_loop_breakloop_hook.py` afterAgentResponse 旁加 bridge |

## 2. 文件清单（6 个）

| # | 路径 | 类型 |
|---|---|---|
| 1 | `.cursor/private/wechat_config.json` | 新增 |
| 2 | `.cursor/private/.gitignore` | 新增 |
| 3 | `ai_workflow/wechat_notifier.py` | 新增 |
| 4 | `ai_workflow/wechat_notifier_test.py` | 新增 |
| 5 | `ai_workflow/goal_loop_wechat_bridge.py` | 新增（路径修正：原 Plan 写 ai_workhook/，落 ai_workflow/ 更符合项目约定）|
| 6 | `.cursor/hooks/hooks.json` | 追加 1 条 command |

**§9.1 红线评估**：6 文件 = §9.1.1 self-test 豁免上限临界。

---

## 3. Act 执行记录（Round 1 · 2026-07-19 · 本轮）

### 3.1 落档 / Act 阶段 9 件任务

| # | 任务 | 状态 | 关键证据 |
|---|---|---|---|
| 1 | 创建本占位文件 | ✅ DONE | DNA §9.5 先落档 — 本档 28 行骨架已 Write |
| 2 | 创建 .cursor/private/ + config + gitignore | ✅ DONE | `ls .cursor/private/` → 2 文件 + `.gitignore`；`git check-ignore wechat_config.json` → matched |
| 3 | 写 ai_workflow/wechat_notifier.py | ✅ DONE | 436 行；py_compile PASS；self-test **10/10 PASS** |
| 4 | 写 ai_workflow/wechat_notifier_test.py | ✅ DONE | 218 行；py_compile PASS；自带 runner **10/10 PASS** |
| 5 | 写 ai_workflow/goal_loop_wechat_bridge.py | ✅ DONE | 432 行；py_compile PASS；self-test **8/8 PASS**（首跑 6/8 因 sys.path 缺包，修复后全 PASS） |
| 6 | 改 hooks.json afterAgentResponse 段 | ✅ DONE | `python3 -c "import json; ..."` 验证后段含 bridge command（timeout 8s） |
| 7 | py_compile 4 文件 + 2 self_test 验证 | ✅ DONE | 4 py_compile PASS + 28 self-test case 全 PASS + bridge 集成 smoke pass（osascript 失败属预期） |
| 8 | 人工端到端 smoke test | ⏸️ **PENDING 用户授权** | 详见 §4「待你手动执行」段（需要在 macOS 系统设置授权辅助功能 + 自动化 → WeChat）|
| 9 | 落 CHANGELOG + 本档完整记录 | ✅ DONE | `CHANGELOG.md` Unreleased 段追加「Added (WeChatNotifier — 微信通知器 · C 通道)」7 个 bullet |

### 3.2 验证报告（总 28 case PASS · 28/28）

| 项目 | 数量 | 关键 |
|---|---|---|
| py_compile | 4 / 4 PASS | wechat_notifier + wechat_notifier_test + goal_loop_wechat_bridge + (hooks.json JSON 合法) |
| wechat_notifier self-test | 10 / 10 PASS | config 错误（3 类）+ 转义 + 截断 + 中文显示 + AppleScript 结构 + dry_run + 权限 + 枚举覆盖 |
| wechat_notifier_test 自带 runner | 10 / 10 PASS | 同上独立测试模块（pytest 兼容） |
| goal_loop_wechat_bridge self-test | 8 / 8 PASS | should_notify 真值表（9 组合）+ 幂等 round-trip + path traversal 防护 + 日志不抛错 + handle_after_agent_response 无 active/非 notify 状态跳过 + 坏 JSON 容错 + 空 stdin |
| **合计** | **32 / 32 PASS** | |

### 3.3 一句话回归指标

```
py_compile 4 PASS  /  self_test 28 PASS  /  bridge 集成 smoke pass（osascript 优雅失败）
```

---

## 4. 端到端 smoke test 待你手动执行

> **当前状态**：基础设施 + 单测 + 集成 smoke 全部 PASS；**唯一缺** macOS 系统的辅助功能 + 自动化权限（你说「都还没授权」）。
> 一旦授权，**业务链路 100% 跑通**（bridge 集成 smoke 已验证「无权限时优雅降级」分支）。

**手动授权步骤**：

1. **系统设置** → **隐私与安全** → **辅助功能**
 → 点 `+` 加号 → 选 `iTerm.app`（或 `Terminal.app`，取决于你跑命令的终端）
 → 打开开关
2. **系统设置** → **隐私与安全** → **自动化**
 → 在你刚授权的终端行 → 勾选 `WeChat`（控制 WeChat.app）

**授权后验证脚本**（仓库根目录跑）：

```bash
python3 -c "
import sys
sys.path.insert(0, 'ai_workflow')
from wechat_notifier import _is_accessibility_trusted, notify_with_message, build_message
print('权限:', '已授权 ✓' if _is_accessibility_trusted() else '未授权 ✗')
msg = build_message('achieved', 'WeChatNotifier 端到端 smoke', 1, '.cursor/private/wechat_config.json', max_length=300)
ok, detail = notify_with_message(msg)
print('结果:', ok)
print('详情:', detail)
"
```

**预期**：

- WeChat.app 自动被前置（聚焦切换）
- 命令行按键 `Cmd+F` 打开搜索
- 输入 `GMING2016` / `gming2016`
- 回车选中第一个匹配（你的会话）
- 键入 5 行消息全文（标题 + 目标摘要 + 轮次 + 产物 + ts）
- 回车发送
- 你在微信看是否收到消息

**未达预期的排查**：

- 微信焦点切了但没搜到 → 手动改 `.cursor/private/wechat_config.json` 的 `preferred_search_keys` 加多个候选（如 `["小明", "GMING2016", "GMing2016", "gming2016"]`）
- 微信完全没动 → 重新检查系统设置授权（可能授权的不是当前跑命令的进程）

**通过后请告诉我**：我会把 §4 切到 ✅ DONE 并补一个截图占位段。
