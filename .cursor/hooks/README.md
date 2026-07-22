# Cursor Hooks for AIDocxWorkFlow

This directory contains hook scripts that automate behavior around agent events.

## Files

- `aidocx_feedback_logger_hook.py` - **阶段反馈自动收集器**: 在 `beforeSubmitPrompt` / `sessionEnd` 触发,扫描 `workflow_assets/<req>/「S*」/v*/` 下的产物,自动写入 `stage_started` / `stage_finished` / `session_summary` 事件到 `workflow_assets/feedback_logs/session_*.jsonl`
- `docx_hook.py` - **DOCX 快速启动钩子**: 当用户说"开始全流程/完整流程/快速流程/快速流水线"等触发语,自动收集 prompt 中的 `.md` 引用、运行简化流水线 (S1→S2→S4→S5→S6),把产物路径写回 prompt
- `sync_modules_table.py` - **SSoT 同步钩子**: 编辑 `MODULES.md` 后, 自动同步所有 `<aside data-modules-sync-block="§X">` 标记的副本
- `scan_module_definitions.py` - **SSoT 一致性体检钩子**: sessionStart 时扫所有未迁移的 8 模块定义副本
- `goal_loop_breakloop_hook.py` - **goal-loop breakloop 钩子**: afterAgentResponse 时扫描 active goals，判断是否该 break（仅负责 break 信号，不发推送）
- `goal_loop_serverchan_bridge.py` - **goal-loop SCT 推送桥接**（位于 `ai_workflow/`，非 hooks 目录）: afterAgentResponse 时扫 active goals，状态真变化时通过 Server 酱 Webhook 推送摘要。SendKey 在 `.cursor/private/serverchan_config.json`，git-ignore 隔离。幂等 + 错误降级全保留（详见 `governance/design_iter/current/serverchan_pivot_20260719.md`）

## sync_modules_table.py 详解

### 触发机制
注册到 `.cursor/hooks.json` 的 `afterFileEdit` 事件:
```json
"afterFileEdit": [
  { "command": ".cursor/hooks/sync_modules_table.py", "timeout": 10 }
]
```

### 标记协议 (Marker Protocol v2 — HTML 标签配对)

**核心设计**: 使用真实 HTML 标签 `<aside>` 包裹,起止标签**完美配对**,
metadata 放在 attribute 里,Markdown 内容嵌在标签内,渲染时 HTML 容器对 Markdown 透明。

```html
<aside data-modules-sync-block="§3.5"
       data-src=".cursor/MODULES.md#§3.5"
       data-sha256="6a78501637918d426c5e11c226c8f36c56ef0a97276b70c4c3eb1975ba8f33af"
       data-synced-at="2026-06-15 10:30:00">

> **🔴 [自动同步区块 `§3.5`]** 本区块由 `.cursor/MODULES.md#§3.5` 自动生成,
> 人工修改将被覆盖。源 SHA: `6a7850163791` · 同步时间: `2026-06-15 10:30:00`

## 3.5 交叉场景归属判定规则

| 场景 | 归模块 |
|------|--------|
| ...  | ...    |

</aside>
```

**支持的 block_id** (与 `BLOCK_DEFINITIONS` 一一对应):
- `§1` — 8 模块总表 + ID 前缀说明
- `§3.5` — 交叉场景归属判定规则 (S5/S6 快速归类)
- `§4.11.2` — HINT vs UI 关键边界隔离规则

**v1 协议兼容** (历史副本, 单区块, 无 id, 视为 §1):
```html
<!-- BEGIN: MODULES_TABLE_SYNC v1 src=... sha256=... -->
... 8 模块表格 ...
<!-- END: MODULES_TABLE_SYNC -->
```

### 工作流
1. 编辑 `MODULES.md` → 钩子扫所有已含 MARKER 的副本 → 强制同步(覆盖)
2. 人工编辑副本 → 钩子检测到 MARKER → 强制恢复(覆盖)
3. 副本被钩子改写后, 带 `MODULES_SYNC_GUARD` 标记 → 二次触发自动 no-op (防级联)

### 同步日志
`.cursor/sync_logs/modules_sync_YYYYMMDD.jsonl`, 每行一条 JSON:
```json
{"ts": "...", "trigger": ".cursor/MODULES.md", "block_id": "§1", "target": ".cursor/skills/.../SKILL.md", "src_sha": "abc123...", "status": "synced"}
```

### 如何添加新副本 / 新区块

**添加新副本** (引用已有 block_id):
- 在目标文件加入 `<aside data-modules-sync-block="§X">...</aside>` 即可
- 下次编辑 MODULES.md 时自动填充正确内容

**添加新 block_id**:
1. 在 `sync_modules_table.py` 的 `BLOCK_DEFINITIONS` 增加条目 + `EXTRACTORS` 增加抽取函数
2. 在 `MODULES.md` 目标章节加锚点 (如 `## §3.6 边界规则`)
3. 副本文件加入 `<aside data-modules-sync-block="§3.6">...</aside>` 占位
4. 触发钩子 (编辑 MODULES.md 或运行 `python3 -c "import sys; sys.stdin=open('/dev/null'); sys.path.insert(0,'.cursor/hooks'); from sync_modules_table import main; main()"`)

## scan_module_definitions.py 详解

### 触发机制
注册到 `.cursor/hooks.json` 的 `sessionStart` 事件:
```json
"sessionStart": [
  { "command": ".cursor/hooks/scan_module_definitions.py --quiet", "timeout": 15 }
]
```

### 检测规则
- v1 协议副本 (`<!-- BEGIN: MODULES_TABLE_SYNC`) 视为"未迁移", 报告需升级
- 8 模块简化表 (`| 1 | CONFIG | 仅配置表...`) 视为"未迁移", 报告需迁移
- "模块定义总表" 等标题视为"含定义表", 报告需迁移
- 已含 v2 协议 (`<aside data-modules-sync-block="§X">`) 视为"已同步"

### 退出码
- `0` — 一致性 OK
- `1` — 发现未迁移副本, 需处理

## 防级联 GUARD 机制

所有由钩子写出的副本文件, 在内容顶部加:
```html
<!-- MODULES_SYNC_GUARD: auto-written, do not edit manually -->
```

二次进入钩子时检测该标记, 直接 `return 0` 退出。
**不要**手动删除 GUARD 标记, 否则会陷入同步级联。
