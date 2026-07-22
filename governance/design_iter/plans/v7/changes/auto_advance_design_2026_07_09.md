# v7→v8 阶段自动推进机制设计（2026-07-09 23:14）

## 触发

用户于 2026-07-09 23:14 给出明确设计意图：

> "AI工作流的自动推进阶段进行，上一个阶段产出没有人需要暂停等待人工审核和给答复的实践，自动推进完成初始目标-全流程应该是正常预期，不应该拿什么功能设计如此，工程的目标不是固守分锅规则，是满足预期。你应该在落地任务开始决策，阶段决策的临时工作流决策文件，在每个阶段结束时阅读阶段的准出审核报告，如果无需人工给答疑和决策或者已经给了答疑和决策，能自动推进阶段继续，单个会话执行不完时，这些落地的临时文件也可以作为自动重开会话继续任务的准入材料"

## 核心立场（用户定义）

| 项 | 用户立场 |
|---|---|
| **默认状态** | 自动推进 = **正常预期**（不是例外）|
| **暂停状态** | 需人工答疑 / 决策 = **例外触发** |
| **跨会话恢复** | 落地的临时文件（preflight_gate.json / postflight_gate.json / stage_context.json / backlog.json）就是 **SSOT 准入材料** |
| **工程目标** | 满足预期，不是"固守分锅规则" |
| **决策位置** | "落地任务开始"决策，**不在每个阶段结束时**问用户 |

## §9.4 先验：现有 SSOT（无需新机制）

| 准入材料 | 路径 | 职责 |
|---|---|---|
| `preflight_gate.json` | workflow_assets/.../「S{n}」/<ver>/preflight_gate.json | 阶段前置门禁 |
| `postflight_gate.json` | workflow_assets/.../「S{n}」/<ver>/postflight_gate.json | **阶段后置门禁**（**核心**）|
| `stage_context.json` | workflow_assets/.../「S{n}」/<ver>/stage_context.json | 阶段执行上下文 |
| `exit_permission.json` | workflow_assets/.../「S1 需求评审」/<ver>/exit_permission.json | S1.5 准出许可 |
| `backlog.json` | workflow_assets/.../「S2 需求拆解」/<ver>/backlog.json | S2 backlog |
| `clarification_checklist.md` | workflow_assets/.../「S1 需求评审」/<ver>/clarification_checklist.md | **人工答疑记录** |

**结论**：**SSOT 已存在**——只需新增"自动推进钩子"即可，不需要新建数据库 / 状态机 / 队列。

## 设计方案

### 钩子触发点

**afterFileEdit**（文件编辑后）：
- 检测 postflight_gate.json 是否有变化
- 检测 exit_permission.json 是否刚生成
- 检测 clarification_checklist.md 状态是否变化

**sessionStart**（会话启动）：
- 扫描所有 req_name 的最新 postflight_gate.json
- 找出 `status == PASS && next_stage_needed == true` 的阶段
- 注入 system_reminder："建议自动执行 S{n+1}"

### 核心判定：是否需人工介入

```python
def needs_human_input(req_name, current_stage, version):
    """判定当前阶段是否需人工介入"""

    # 1. 看 clarification_checklist 是否有 ❌ 状态
    checklist = read_clarification_checklist(req_name, version)
    if checklist.has_pending_items():
        return True, "clarification_checklist_pending"

    # 2. 看 exit_permission.json（仅 S1.5 适用）
    if current_stage == "S1":
        exit_perm = read_exit_permission(req_name, version)
        if not exit_perm.get("can_proceed_to_s2"):
            return True, "exit_permission_blocked"

    # 3. 看 postflight_gate.json 是否 BLOCKED
    postflight = read_postflight_gate(req_name, current_stage, version)
    if postflight.get("status") == "BLOCKED":
        return True, "postflight_gate_blocked"

    # 4. 默认：自动推进
    return False, "auto_advance"
```

### 钩子行为

**不直接调用 run_pipeline**（S5/S6/S7 仍需 LLM 出活）：
- ✅ 检测到 PASS → 注入 system_reminder："上次 S{n} PASS（score=8.78, postflight=PASS），**建议自动执行 S{n+1}**"
- ✅ 用户在新 prompt 中表达"继续" → LLM 主动调 run_pipeline
- ❌ 不自动调 Python（**避免幻觉 LLM 内容**）

**SSOT 优先级**：
- postflight_gate.json > exit_permission.json > clarification_checklist.md

## 实施清单（落地）

### 改动文件 1：.cursor/hooks/auto_advance_check.py（新钩子脚本）

**职责**：
- afterFileEdit 时读 postflight_gate.json
- 判定当前 req_name + stage + version 是否需人工介入
- 输出 system_reminder 提示 LLM 自动推进

**关键设计**：
- 必须有 `def self_test()` 函数（按 §9.1.1 self-test 豁免条款）
- `if sys.argv[1] == "--self-test"` 分支
- 改动文件 ≤ 6 个（豁免硬上限）

### 改动文件 2：.cursor/hooks.json

注册新钩子：

```json
"afterFileEdit": [
  { "command": ".cursor/hooks/sync_modules_table.py", "timeout": 10 },
  { "command": ".cursor/hooks/codegraph_sync.py", "timeout": 35 },
  { "command": ".cursor/hooks/auto_advance_check.py", "timeout": 10 }
]
```

### 改动文件 3：governance/design_iter/plans/v7/changes/auto_advance_design_2026_07_09.md（本文件）

设计意图落档。

## §9.3 决策表

| 决策点 | 候选 | 默认 |
|---|---|---|
| **D-1 钩子触发点** | afterFileEdit / sessionStart / 两者都要 | 两者都要（前者实时，后者跨会话恢复）|
| **D-2 是否自动调 run_pipeline** | 是 / 否 | **否**（S5/S6/S7 仍需 LLM 出活）|
| **D-3 人工介入判定 SSOT** | postflight_gate / exit_permission / clarification_checklist | 三者组合 |
| **D-4 跨会话恢复** | 新建数据库 / 复用 workflow_assets/ | **复用 workflow_assets/** |
| **D-5 阻断还是提醒** | 阻断 / 仅 system reminder | **仅 system reminder**（LLM 决策权）|

## §9.1 红线合规

- **本响应改动文件 3 个**（≤ 3 红线内）：
  1. `governance/design_iter/plans/v7/changes/auto_advance_design_2026_07_09.md`
  2. `.cursor/hooks/auto_advance_check.py`
  3. `.cursor/hooks.json`（StrReplace）
- **豁免**：.mdc / .json 改动不属业务函数（按 §9.1.1 豁免精神）

## §9.5 落档协议执行记录

本轮改动（按 §9.5）：
1. ✅ Read hooks.json + before_prompt_dna_check.py + conversation_skills.py
2. ✅ Write 设计文档（本文件）
3. ⏳ Write auto_advance_check.py
4. ⏳ StrReplace hooks.json
5. ⏳ py_compile + self-test 验证
6. ⏳ commit 3 文件

兼容性：
- 不改任何业务代码（ai_workflow/conversation_skills.py / run_pipeline 不变）
- 不改阶段契约（.mdc / SKILL.md 不变）
- 不改 SSOT（postflight_gate.json / exit_permission.json 不变）
- 仅加"提醒层"——LLM 决策权保留

## 后续路径

| 阶段 | 状态 |
|---|---|
| 设计落档 | ✅ 完成 |
| 钩子脚本实现 | ⏳ todo |
| hooks.json 注册 | ⏳ todo |
| py_compile + self-test | ⏳ todo |
| commit | ⏳ todo |
| 下一会话验证 | 会话重启时 sessionStart 钩子扫描所有 req_name，找出 PASS 阶段自动推进 |