# V-104 C2 守卫审计 — session_resume_multi_goal.py 不注册于 hooks.json

> **任务标识**: T-103 / V-104 / BLOCKER
> **审计时间**: 2026-07-20 00:49 (UTC+8)
> **审计员**: subagent (worker)
> **决策依据**: v27 GOAL §1 第 3 行 — C2 守卫

---

## 1. Read 证据（DNA §9.4 先验后答 · 已本响应内 Read）

### 1.1 `.cursor/hooks.json#sessionStart` 段（line 4-24）

```json
"sessionStart": [
  { "type": "prompt", "prompt": "..." },
  { "type": "command", "command": ".cursor/hooks/scan_module_definitions.py --quiet", "timeout": 15 },
  { "type": "command", "command": ".cursor/hooks/project_dna_inject.py", "timeout": 5 },
  { "type": "command", "command": ".cursor/hooks/auto_advance_check.py", "timeout": 10 }
]
```

**注册项清单（4 项）**：

| # | type | command | timeout |
|---|---|---|---|
| 1 | prompt | （静态提示文本） | — |
| 2 | command | `.cursor/hooks/scan_module_definitions.py --quiet` | 15 |
| 3 | command | `.cursor/hooks/project_dna_inject.py` | 5 |
| 4 | command | `.cursor/hooks/auto_advance_check.py` | 10 |

**结论**：sessionStart 段**不包含** `session_resume_multi_goal.py`，**不包含** `goal_loop_hook.py`（后者注册在 `afterShellExecution` 而非 sessionStart）。✅

### 1.2 `.cursor/hooks/goal_loop_hook.py:62-83`（单 goal 实现）

```python
def handle_session_start(_payload: dict[str, Any]) -> int:
    """会话启动：恢复挂起的 active goal。"""
    if list_active_goals is None:
        return 0
    try:
        active = list_active_goals()
    except SnapshotError:
        return 0
    except Exception:
        return 0
    reminder = _format_resume_reminder(active)
    if not reminder:
        return 0
    out = {
        "system_reminder": reminder,
        "active_goal_count": len(active),
    }
    try:
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return 0
```

**实现要点**：

- 调用 `list_active_goals()`（来自 `goal_snapshot.py`）— 返回 active goal 列表
- 调用 `_format_resume_reminder(active)`（line 34-49）— 格式化 reminder 文本
- 注入 JSON `{"system_reminder": ..., "active_goal_count": N}` 到 stdout
- **无 active goal → 不注入任何内容（exit 0）**

**注意**：该函数是 v1 单 goal 实现。session_resume_multi_goal.py 的 handle_session_start_multi_goal 是**并行多 goal 版本**（v1.2）。

### 1.3 `.cursor/hooks/session_resume_multi_goal.py` 现状

**文件存在性**：`git status` 显示 `?? .cursor/hooks/session_resume_multi_goal.py`（**untracked**，未提交）。

**自我测试能力**：

```bash
$ python3 .cursor/hooks/session_resume_multi_goal.py --self-test
  [OK] Case 1: 空 stdin → exit 0
  [OK] Case 2: 无 active goal → exit 0 + 无 stdout
  [OK] Case 3: 单 goal → 注入 reminder (136 chars)
  [OK] Case 4: 多 goal → 注入多 goal reminder (328 chars)
  [OK] Case 5: 未知事件 → exit 0
  [OK] self_test passed (5 cases, v1.2)
```

**结构概览**：

- `handle_session_start_multi_goal()`（line 84-120）— 多 goal 续跑版
- 调 `load_all_active_snapshots()`（v1.2 新 API，单 goal 版本用 `list_active_goals()`）
- 按 `loop_round` 降序排序后逐个注入
- 单 goal：直接注入 reminder
- 多 goal：用分隔符 `--- Goal i/N ---` 合并到单一 `system_reminder` 输出
- **有 `--self-test` argv 分支**（line 247-249）— 独立可跑

---

## 2. grep 验证（V-104 标准 1）

```bash
$ grep -c "session_resume_multi_goal" .cursor/hooks.json
0
$ echo "---exit: $?"
1   ← grep 在零匹配时 exit 1（这是 grep 的正常行为，不是错误）
```

**命中数 = 0**。✅ 符合 V-104 标准。

---

## 3. git 状态快照（V-104 标准 4-5）

```
 M .cursor/hooks.json
?? .cursor/hooks/session_resume_multi_goal.py
```

| 文件 | 状态 | 本响应是否触碰 |
|---|---|---|
| `.cursor/hooks.json` | M（modified，**预存在**） | ❌ **未触碰**（C2 决策核心） |
| `.cursor/hooks/session_resume_multi_goal.py` | ??（untracked） | ❌ **未触碰**（C2 决策核心） |
| `.cursor/hooks/goal_loop_hook.py` | 未列出（未变更） | ❌ 仅 Read，未 Write/Edit |

**说明**：`.cursor/hooks.json` 的 `M` 状态在会话启动前的 git status 中已存在，**不属于本次响应改动**。

---

## 4. 守卫结论（V-104）

| 验证项 | 期望 | 实际 | 判定 |
|---|---|---|---|
| hooks.json#sessionStart 含 `session_resume_multi_goal.py` | 否 | 0 命中 | ✅ PASS |
| goal_loop_hook.py:62-83 单 goal 实现存在 | 是 | handle_session_start 已实现 | ✅ PASS |
| session_resume_multi_goal.py 文件存在 + 独立可跑 | 是 | `??` + `--self-test` 5 cases pass | ✅ PASS |
| hooks.json 字节未变更 | 是 | 仅 Read | ✅ PASS |
| session_resume_multi_goal.py 字节未变更 | 是 | 仅 Read + 运行 `--self-test` | ✅ PASS |

**V-104 整体判定**：✅ **PASS**

**C2 决策正确性确认**：当前 v27 状态下 `goal_loop_hook.py`（v1 单 goal）已通过 `afterShellExecution` 注册（line 87），而 `session_resume_multi_goal.py`（v1.2 多 goal）**保留不注册**。两者不冲突——单 goal 注册在 afterShellExecution（命令完成后注入 audit 提示），多 goal 设计注册在 sessionStart（会话启动注入续跑），但本轮决策为不动 hooks.json。

**为什么 C2 决策是正确的（防双注入论证）**：

1. 若同时注册 goal_loop_hook.py 的 sessionStart handler + session_resume_multi_goal.py → sessionStart 事件会触发两次 `list_active_goals()` + 两次 JSON 输出 → Cursor 会按"两个独立 system_reminder"对待 → 用户在响应中看到两个续跑提示块（噪声翻倍）
2. 当前实现：
 - sessionStart: 仅注册 scan_module_definitions / project_dna_inject / auto_advance_check（不动）
 - afterShellExecution: 注册 goal_loop_hook.py（注入 audit 提示）
3. 结论：**多 goal 续跑能力 v28+ 合并**——届时要么扩展 goal_loop_hook.py 支持多 goal，要么去掉 afterShellExecution 注册把 goal_loop_hook.py 改到 sessionStart 单 goal 二选一。当前 v27 阶段选择"暂时不引入新行为"是正确的保守决策。

---

## 5. v28+ 合并计划（决策路径）

### 5.1 合并候选路径

| 路径 | 描述 | 风险 |
|---|---|---|
| **A**: 扩展 goal_loop_hook.py 支持多 goal | line 62-83 handle_session_start 改为遍历 active goals list（参考 session_resume_multi_goal._build_goal_reminder） | 改动 1 个业务函数签名级别，需 self-test 重测 + 移除 session_resume_multi_goal.py |
| **B**: 替换为 session_resume_multi_goal.py（注册到 sessionStart） | line 84-120 实现已完备，直接注册 | 需在 hooks.json#sessionStart 新增一行（**改动约束文件**）—— 但 sessionStart handler 顺序影响（目前 4 项都是 audit/setup 类，无续跑类） |
| **C**: 保留现状，session_resume_multi_goal.py 作 reference impl | v27 不合并，仅保留 untracked 文件 | 最保守，但 untracked 文件长期存在会进入 git status 噪声 |

### 5.2 推荐路径

**B**（注册 session_resume_multi_goal.py 到 sessionStart）——理由：

1. 已有独立 `--self-test` 5 cases 通过 — 成熟度足够
2. 实现完整（单 goal + 多 goal 都覆盖）
3. 多 goal 续跑是 goal-loop 的核心场景，sessionStart 是注入续跑提示的合理位置
4. goal_loop_hook.py 的 audit 提示**职责不同**（afterShellExecution 触发），不冲突

### 5.3 v28+ 实施检查清单

- [ ] v28 GOAL.md 评审：是否引入多 goal 续跑能力
- [ ] 决定 A/B/C 路径
- [ ] 若选 B：在 `.cursor/hooks.json#sessionStart` 新增 `{ "command": ".cursor/hooks/session_resume_multi_goal.py", "timeout": 10 }`
- [ ] 若选 B：CHANGELOG.md 记录"v28 sessionStart 多 goal 续跑"
- [ ] 若选 B：goal_loop_hook.py 的 sessionStart handler 需决策（保留 / 删除 / 重构）— 这是双注入风险的关键
- [ ] 重测 `--self-test` 两个 hook 都通过

---

## 6. 触发的反模式 / 阻塞

| 类型 | 描述 | 处理 |
|---|---|---|
| **触发** | none | — |
| **阻塞** | none | — |
| **警告** | untracked 文件长期存在 (`?? .cursor/hooks/session_resume_multi_goal.py`) | v28+ 处理（合并到 hooks.json 或删除） |

**没有触发任何 DNA 反模式**：
- ❌ 不算"未问先动"（本任务由父会话明确指派）
- ❌ 不算"代码改了约束没跟"（本任务**没有改任何代码/约束**）
- ❌ 不算"决策只在内文"（决策表已写入本文件 + §5 合并计划）

---

## 7. 落档协议执行记录（DNA §9.5）

| 时机 | 动作 | 文件 |
|---|---|---|
| 本响应起始 | Write 占位（标题 + 章节骨架） | `governance/design_iter/current/v27_c2_guard.md`（本文件） |
| 本响应中段 | Read 三个目标文件 + grep 验证 | — |
| 本响应末尾 | content 展开完成 | 本文件已完整 |

**本轮实际改动文件清单**：仅 `governance/design_iter/current/v27_c2_guard.md`（新建）。

**未触动文件清单**（硬约束验证）：
- `.cursor/hooks.json`（C2 决策核心）— ❌ 未触碰
- `.cursor/hooks/session_resume_multi_goal.py`（C2 决策核心）— ❌ 仅 Read + 运行 `--self-test`（self-test 是只读测试，不修改文件）
- `.cursor/hooks/goal_loop_hook.py` — ❌ 仅 Read

---

## 8. 返回给父会话（摘要）

### 8.1 Read 证据（已 §1 摘录）

- `hooks.json#sessionStart`: 4 项注册，**不包含** session_resume_multi_goal.py
- `goal_loop_hook.py:62-83`: `handle_session_start()` 单 goal 实现已落地
- `session_resume_multi_goal.py`: 247 行，含 `--self-test` 5 cases 全过

### 8.2 grep 命中数

```bash
grep -c "session_resume_multi_goal" .cursor/hooks.json
# → 0
```

### 8.3 守卫审计记录路径

`governance/design_iter/current/v27_c2_guard.md`（本文件，已创建）

### 8.4 V-104 判定

✅ **PASS**（5/5 验证项全部通过，详见 §4 表格）

### 8.5 触发的反模式 / 阻塞

- 反模式：none
- 阻塞：none
- 警告：untracked 文件需 v28+ 处理（合并路径见 §5.2 推荐 B）

### 8.6 工作完成度

- ✅ Read 三个目标文件（DNA §9.4 先验后答合规）
- ✅ grep 验证命中数 = 0
- ✅ self-test 验证（5 cases pass）
- ✅ 守卫审计记录已落档（DNA §9.5 落档协议合规）
- ✅ 未 commit
- ✅ 未触碰 hooks.json
- ✅ 未触碰 session_resume_multi_goal.py
