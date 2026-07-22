# v7 用户质疑：阶段自动触发机制（2026-07-09 23:04）

## 触发

用户提问：
> "S2 可立即执行——无需任何人工介入. 那为什么钩子不自动触发向下执行要等人调度呢"

## §9.4 先验：两套机制现状

### 1. Cursor Hooks 系统（.cursor/hooks.json）

| 触发点 | 钩子 | 职责 |
|---|---|---|
| **sessionStart** | scan_module_definitions.py / project_dna_inject.py / aidocx-feedback-logger | 会话启动 |
| **beforeSubmitPrompt** | docx_hook.py / aidocx_feedback_logger_hook.py / before_prompt_dna_check.py | 每次提交 prompt 前置 |
| **afterFileEdit** | sync_modules_table.py / codegraph_sync.py | 文件编辑后 |
| **sessionEnd** | aidocx_feedback_logger_hook.py / dna_violation_check.py / dna_decision_density_check.py / dna_read_before_answer_check.py / dna_decision_persistence_check.py | 会话结束 |

**钩子作用域**：**会话级事件**（prompt 提交 / 文件编辑 / 会话结束）

### 2. Python 阶段编排 API（ai_workflow/conversation_skills.py）

| 函数 | 行号 | 职责 |
|---|---|---|
| `run_stage_preflight` | 50 | 阶段前置门禁 |
| `run_stage_postflight` | 61 | 阶段后置门禁 |
| `run_stage` | 72 | 统一阶段入口（preflight → callable → postflight）|
| `run_pipeline` | 123 | 顺序编排多阶段 |
| `save_stage5_output` / `format_test_cases` / `save_stage7_output` | 187/98/622 | 阶段 callable |

**API 作用域**：**阶段级编排**——LLM 或脚本手动调用 Python 函数

### 3. 两套机制的关键差异

| 维度 | Cursor Hooks | run_stage / run_pipeline |
|---|---|---|
| **触发方式** | Cursor IDE 自动（事件驱动）| LLM 主动调用 Python |
| **作用域** | 会话级（prompt / 编辑）| 阶段级（S1~S8）|
| **可见状态** | 钩子输出 = stdout（system reminder）| 函数返回 = dict |
| **阶段状态感知** | **无**（钩子不读 review_report.json）| **有**（preflight 检查文件存在性）|
| **自动触发下一阶段** | **否** | **否**（需 LLM 主动调用 run_pipeline）|

**核心矛盾**：

- 钩子系统是**事件驱动**（prompt 提交触发 beforeSubmitPrompt），不是**状态驱动**（阶段 PASS 触发下一阶段）
- run_pipeline 是**API**，不是**监听器**——LLM 调它就执行，不调就不执行
- **没有任何机制监控 stage_context.json + postflight_gate.json 的 PASS 状态并自动触发下一阶段**

## 用户质疑的本质

**期望 vs 现状**：

- 期望："S1.5 PASS → 自动调 S2"（**状态驱动自动编排**）
- 现状："S1.5 PASS → LLM 主动跑 `run_pipeline(["S2", ...])`"（**手动调度**）

## §9.3 候选方案

### 方案 A：新增阶段状态钩子（afterFileEdit 触发 + 阶段产物检查）

| 项 | 内容 |
|---|---|
| 思路 | afterFileEdit 钩子检测 stage_context.json / postflight_gate.json 变更，发现 PASS 时向 system_reminder 注入"建议运行 S{n+1}" |
| 优点 | 不需要新事件，复用 afterFileEdit |
| 缺点 | (1) 只能提示 LLM，不能自动跑 stage_callable；(2) S2~S7 stage_callable 需 LLM 生成 S6 test cases 等，不能 100% 脚本化；(3) 需人确认 LLM 是否响应提醒 |
| 风险 | 中（修改 hooks.json 影响所有会话）|

### 方案 B：新增 watchdog 后台脚本（cron / launchd）

| 项 | 内容 |
|---|---|
| 思路 | 写独立 Python 脚本 `auto_orchestrator.py` 扫描 workflow_assets/<req_name>/「S{n}」/postflight_gate.json，发现 PASS 自动调 `run_pipeline(["S{n+1}"])` |
| 优点 | 真正自动；与 Cursor 钩子解耦；可独立部署 |
| 缺点 | (1) 需机器常驻；(2) S6 等阶段需 LLM 输出测试用例，不能纯脚本跑；(3) 资源占用 |
| 风险 | 中高（可能误触发、需 LLM 介入的阶段卡住）|

### 方案 C：维持现状 + 加 LLM 提示（推荐）

| 项 | 内容 |
|---|---|
| 思路 | 在 beforeSubmitPrompt 钩子中追加"扫描最近阶段 PASS 状态 + 注入到 system_reminder：如果上次阶段 PASS，下一次 prompt 默认跑下一阶段" |
| 优点 | 改动最小；复用现有 beforeSubmitPrompt |
| 缺点 | 仍是 LLM 主动执行，本质没变 |
| 风险 | 低 |

### 方案 D：用户当面回答"为什么不用 LLM 主动调"

| 项 | 内容 |
|---|---|
| 思路 | 解释：S5/S6/S7 等阶段需 LLM 生成（测试点/测试用例/审查建议），脚本无法自动产出；钩子不能调 LLM |
| 优点 | 不改代码，澄清设计意图 |
| 缺点 | 用户可能仍要自动 |
| 风险 | 无 |

## 落档协议执行记录

本轮改动：
1. ✅ Read hooks.json + before_prompt_dna_check.py + conversation_skills.py
2. ✅ Write 本占位文件
3. ⏳ AskQuestion 选方案
4. ⏳ 按用户选方案动手

兼容性：
- 不改任何业务代码（仅 v7 治理文档）
- 不改 hooks.json（等用户点头）
- 不改 run_pipeline API（等用户点头）

## 当前 v7 OPEN Q 中相关项

无（v7 已 P0/P2 全部闭环，剩余 22 Q 中无"自动触发"问题）——这是**新提出的需求**，应在 v8 启动时纳入。