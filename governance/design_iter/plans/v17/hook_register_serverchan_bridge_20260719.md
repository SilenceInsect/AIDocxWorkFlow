# Goal-Loop Bridge 真接入 hooks.json — afterAgentResponse 注册

> **本档是 §9.5 占位决策档**。触发场景：
> 1. 用户在 2026-07-19 19:40 要求「接入 .cursor/hooks/hooks.json，让 afterAgentResponse 真挂上 bridge」
> 2. 但同时**前序 pivot 错误删除 `goal_loop_wechat_bridge.py` 后未清理 hooks.json 第 99 行**，
>    导致当前 afterAgentResponse 每次响应必抛 `ModuleNotFoundError`，是已知 bug。

## 0. 紧急修复优先

**Step 0 必做**：在接新 bridge 前，先承认现状 bug —— `hooks.json:99` 仍指向已删除的 `goal_loop_wechat_bridge.py`。

修复路径选项：

| 方案 | 影响 | 推荐 |
|---|---|---|
| **A** 删除第 99 行（旧 bridge 引用） | 不挂 bridge，afterAgentResponse 仅剩 breakloop hook | 🟡 短期最低风险 |
| **B** 改成 `goal_loop_serverchan_bridge.py`（接新 SCT） | 完整 SCT 自动推送 | ✅ 用户要求 |
| **C** 完全删除整个 `afterAgentResponse` 数组 | breakloop 也失去 | ❌ 砍太多 |

**先 A 后 B** 还是**直接 B**：取决于你是否在乎修复窗口期里 push 是否能跑。先 A 把当前炸的修掉，再 B 接新桥。

## 1. 决策表

| # | 文件 | 动作 | 风险 |
|---|---|---|---|
| 1 | `.cursor/hooks.json` 第 99 行 | 改 `goal_loop_wechat_bridge.py` → `goal_loop_serverchan_bridge.py` | LOW（只是路径名） |
| 2 | `.cursor/hooks.json` 第 100 行 `timeout` | 8 → 10（HTTP webhook 调用可能比 AppleScript 慢） | LOW |
| 3 | `.cursor/hooks/README.md` 表格 | 加 `goal_loop_serverchan_bridge.py` 一行（如果有 wechat bridge 旧条目则删除） | LOW |
| 4 | `goal_loop_serverchan_bridge.py` 的 stdout 行为 | 已自测 PASS（system_reminder 走 stdout 不阻断） | 0 |

**总影响**：仅 1 个 JSON 文件 + 1 个 README 表格 + 行为契约不变。

## 2. 验证清单

| 项 | 期望 |
|---|---|
| py_compile hooks.json 解析 | ✅ valid JSON |
| 手工触发 afterAgentResponse（mock payload 走 stdin） | bridge exit 0，stdout 空（无 active goal）|
| 手工触发 with active goal（status=achieved） | SCT 真发 + 幂等文件更新 |
| 模拟「旧 bridge 文件不存在」场景 | 当前实测就是这状态 → hook 必须不崩 |
| 会话真实跑一轮 Agent 响应 | 不抛 ModuleNotFoundError，无污染日志 |

## 3. 风险登记

| 风险 | 等级 | 缓解 |
|---|---|---|
| Agent 响应频繁触发 webhook（每句一次）| HIGH | bridge 幂等 + `should_notify` 双层判定 |
| 推送打扰用户 | MEDIUM | dry_run=false 按用户确认；SERVERCHAN_DRY_RUN=true 兜底 |
| breakloop hook 与新 bridge hook 顺序冲突 | LOW | JSON 数组按顺序执行，breakloop 在前（先停 loop 再推）|
| hooks.json 路径改错导致整个 IDE 不响应 | LOW | StrReplace 必须 unique + 后续 IDE 自检 |

## 4. Act 阶段执行记录

### 4.1 自证错误 + 修复（前序 pivot 漏掉的）

- **错误**：前序 v20 pivot 删 `goal_loop_wechat_bridge.py` 时，未清 `.cursor/hooks.json:99` 的引用 → 当前 afterAgentResponse 每次 Agent 响应必抛 `ModuleNotFoundError`
- **根因**：我之前说「`.cursor/hooks/hooks.json` 不存在」是搜索路径写错导致 0 命中；真实文件在 `.cursor/hooks.json`（不在 hooks 子目录）
- **§9.4 违规**：未先 Read 就答「零风险」。**已在响应顶部声明并认错**。
- **修复**：本档 Step 1 改 hooks.json 第 99 行 → `goal_loop_serverchan_bridge.py`，timeout 8→10。

### 4.2 实际改动文件

| # | 文件 | 动作 |
|---|---|---|
| 1 | `.cursor/hooks.json` 第 99-101 行 | 改路径 `goal_loop_wechat_bridge.py` → `goal_loop_serverchan_bridge.py`，timeout 8 → 10 |
| 2 | `.cursor/hooks/README.md` §Files | 加 `goal_loop_breakloop_hook.py` + `goal_loop_serverchan_bridge.py` 两行说明 |
| 3 | `governance/design_iter/current/hook_register_serverchan_bridge_20260719.md` | 本档 |

### 4.3 验证结果

| 项 | 期望 | 实际 |
|---|---|---|
| hooks.json JSON parse | valid | ✅ |
| 新 bridge 注册到 afterAgentResponse | True | ✅ |
| 旧 wechat bridge 已清理 | False | ✅ |
| breakloop hook 仍在 | True | ✅ |
| Mock stdin（afterAgentResponse payload）| exit 0，无 stdout | ✅ |
| 空 stdin | exit 0 | ✅ |
| 真实 active goal 路径 + 真发 | SCT http=200 | ✅ `process_goal result: notified` |
| 幂等文件写入 | channel=serverchan, status=achieved | ✅ |

### 4.4 真发证据

手机应收到一条：
```
[Goal-Loop 通知] 已完成（achieved）
目标: hooks.json 接入测试
轮次: round=99
产物: governance/design_iter/current/hook_register_serverchan_bridge_20260719.md
```

---