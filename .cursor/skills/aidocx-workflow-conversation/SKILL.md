---
name: aidocx-workflow-conversation
description: >
  AIDocxWorkFlow 对话编排入口。使用 run_stage() / run_pipeline() 串联阶段 gate、阶段执行与产物校验。
  Use when the user wants the conversation layer to orchestrate the workflow through the runtime contract instead of manual per-stage narration.
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: workflow-conversation
  spec_version: agentskills.io/1.0
  cursor_compat: true
  cursor_mode_hint: multi_task
---

# AIDocxWorkFlow 编排契约

> **v35 新增四大能力**：
> 1. **S1 项目级需求检测** — 显式识别项目需求 vs 单次需求，找到或创建项目目录
> 2. **项目级-模块级知识沉淀** — 后续阶段收到项目级需求时整理知识沉淀到知识库
> 3. **8 expert 并行 + merge-expert 串行收尾** — 8 个模块专家并行产出 TP/TC，merge-expert 专门合并，防止主 agent 长上下文脱轨
> 4. **S6 强制公共级 xlsx** — 不受 project_name 影响，始终产出公共级 xlsx
>
> 本 skill 不再承担"完整手工操作指南"职责。
> 它只定义一件事：对话层如何通过 `run_stage()` / `run_pipeline()` 驱动运行时编排。

## 1. 目标

- 统一单阶段与多阶段入口，避免脚本绕过 gate / ledger / review 资产。
- 让“人看到的入口说明”和“代码实际编排路径”保持一致。
- 把旧式“分阶段手工说明”降级为历史兼容背景，而不是当前推荐入口。

## 2. 唯一推荐入口

```python
from ai_workflow.conversation_skills import run_stage, run_pipeline
```

### 单阶段

```python
result = run_stage("S6", req_name="游戏道具商城系统", project_name="<project_name>", version="v3.01")
print(result["status"])
```

### 多阶段

```python
pipeline = run_pipeline(
    ["S5", "S6", "S7"],
    req_name="游戏道具商城系统",
    project_name="<project_name>",
    version="v3.01",
)
for item in pipeline["stages"]:
    print(item["stage"], item["status"])
```

### 阶段开始前：旧产物清理询问（v8 实战决策）

`run_stage()` / `run_pipeline()` / `run_s1_pipeline()` 在执行每个阶段前会自动检测
**该阶段目录是否存在且非空**——若命中，会在 `preflight` 之前询问：

```
┌─ [AIDocxWorkFlow] 阶段开始前询问 ─────────────────────────────┐
│ 检测到阶段目录已存在且非空，是否删除旧产物后重新执行？       │
└──────────────────────────────────────────────────────────────┘
  阶段        ：S6
  需求        ：游戏道具商城系统
  版本        ：v3.01
  阶段目录    ：workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」
  现有文件数  ：7
  现有总大小  ：28.4 KB
  最近修改    ：2026-07-09T23:54:17
  文件清单    ：
    - test_cases.json
    - test_cases.md
    - ...

请选择：
  [Y] 删除旧产物，重新跑该阶段（推荐）
  [N] 保留旧产物，跳过该阶段（status=SKIPPED）
  [A] 中止整个流水线（abort）
```

**决策语义**：

| 用户输入 | 行为 | 返回 status |
|---|---|---|
| `Y` | `shutil.rmtree(stage_dir)` 删除整个阶段目录（含 raw + ledger），重新执行 | 阶段正常推进 |
| `N` / 空回车 | 保留旧产物，**跳过该阶段** | `SKIPPED` + `skip_reason=user_chose_keep_existing` |
| `A` | 中止整个流水线 | `SystemExit`（run_pipeline 抛出后停） |
| 非交互环境（无 TTY） | 默认 `auto_keep`（不阻塞 CI） | `SKIPPED` + `skip_reason=non_interactive_env_default_keep` |

**作用域**：

- `run_stage("S6", ...)` → 仅 S6 询问
- `run_pipeline(["S5","S6","S7"], ...)` → 每个阶段独立询问（不会批量问）
- `run_s1_pipeline(...)` → S1 子模块入口同样询问（覆盖直接调用场景）

**删除范围**：

- `shutil.rmtree` 整个阶段目录（含 `raw/`、`*.json`、`*.md`、`*.xlsx`、`coverage_ledger.json`、`omission_ledger.json`、`preflight_gate.json`、`postflight_gate.json` 等所有产物）
- **不删** `resource/<req_name>/<version>_raw.docx`（gitignore 区，原始输入材料）

**为什么是固定行为（不再每次口头约定）**：

- v8 实战（2026-07-10）用户明确要求固化——避免每次跑 v3.01 都口头"先问一下"
- 防止 stage_callable 覆盖写入时与旧 `coverage_ledger.json` / `omission_ledger.json` 串味
- 人本可审查准则：删除前必须让用户看见具体文件清单

## 3. 编排顺序

`run_stage()` 的固定顺序是：

1. `run_stage_preflight(stage, req_name, version, project_name)`
2. 执行 `stage_callable`（如有）
3. `run_stage_postflight(stage, req_name, version, project_name)`

阶段若未生成以下运行时资产，不算完成：

- `stage_context.json`
- `stage_context.md`
- `read_ack.json`
- 对应阶段的 `postflight_gate.json`

S5 / S6 还必须补齐：

- `coverage_ledger.json`
- `omission_ledger.json`

S7 还必须补齐：

- `review_snapshot.json`
- `review_snapshot.md`
- `review_report.json`
- `review_report.md`

## 4. run_pipeline 契约

`run_pipeline()` 是顺序编排器，不是并发执行器。

默认行为：

- 按传入顺序依次执行阶段
- 默认 `stop_on_failure=True`
- 任一阶段状态不是 `PASS`，后续阶段标记为 `SKIPPED`
- 返回 `halted=true` 和 `halt_reason`

返回结构的关键字段：

```json
{
  "req_name": "xxx",
  "project_name": "<project_name>",
  "version": "v1.0",
  "stop_on_failure": true,
  "halted": false,
  "halt_reason": null,
  "stages": [
    {
      "stage": "S5",
      "status": "PASS",
      "preflight": {},
      "stage_result": {},
      "postflight": {},
      "runtime_gate": {}
    }
  ]
}
```

## 5. 阶段状态枚举

- `PASS`：preflight / runtime gate / postflight 全部通过
- `FAIL_PRECHECK`：输入或前置资产不满足
- `FAIL_RUNTIME_GATE`：runtime consistency gate 阻断
- `FAIL_POSTCHECK`：阶段产物未闭合
- `NEED_LLM_OUTPUT`：preflight 已过，但未提供 `stage_callable`
- `SKIPPED`：由于上游阶段失败被跳过

## 6. 推荐阶段 callable

当前实现层已经可直接复用的 callable：

- S5：`save_stage5_output(...)`
- S6：`format_test_cases(...)`
- S7：`save_stage7_output(...)`

示例：

```python
from ai_workflow.conversation_skills import run_pipeline, save_stage5_output, save_stage7_output
from ai_workflow.test_case_formatter import format_test_cases

pipeline = run_pipeline(
    ["S5", "S6", "S7"],
    req_name="游戏道具商城系统",
    project_name="<project_name>",
    version="v3.01",
    stage_callables={
        "S5": lambda: save_stage5_output("游戏道具商城系统", test_points_payload, version="v3.01", project_name="<project_name>"),
        "S6": lambda: format_test_cases(test_cases_payload, backlog_payload, test_points_payload, req_name="游戏道具商城系统", version="v3.01", project_name="<project_name>"),
        "S7": lambda: save_stage7_output("游戏道具商城系统", version="v3.01", project_name="<project_name>"),
    },
)
```

## 7. 旧入口地位

以下函数仍保留，但不代表当前编排主入口：

- `execute_simple_flow()`
- `execute_full_flow()`

它们可用于兼容旧调用方或状态查询，但不应替代 `run_stage()` / `run_pipeline()`。

## 8. 约束边界

本 skill 只描述编排契约，不重复各阶段内容规范。

阶段内容生成、字段要求、必读材料、质量门禁，仍以以下文件为准：

- `AGENTS.md`
- `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`
- `.cursor/rules/STAGE_S*.mdc`
- `.cursor/skills/aidocx-s*/SKILL.md`

---

## §A1 S1 项目级需求检测（v35 新增）

> **目的**：S1 入口必须显式思考需求是"项目级需求文档"还是"单次需求文档"，找到或创建对应项目目录，为后续项目级知识沉淀建立入口锚点。

### A1.1 项目需求 vs 单次需求判定规则

| 特征 | 项目级需求（归入 `project_local/`） | 单次需求（归入 `workflow_assets/<req_name>/`） |
|------|---|---|
| 适用场景 | 多版本迭代、跨版本复用、公共 TP/TC 积累 | 一次性文档、不需要版本追踪 |
| 目录归属 | `knowledge/project_local/<project_name>/` | `workflow_assets/<req_name>/<version>/` |
| 知识沉淀 | 产出可沉淀到公共知识库 | 不沉淀，仅本次使用 |
| 版本追踪 | 强版本管理（v1.0 / v2.0 / v3.0...） | 弱版本管理 |
| 模块专家关联 | 强关联——项目级 TP/TC 应归档到对应模块 | 弱关联 |

### A1.2 判定流程（LLM 执行）

```
用户粘贴需求文档
     ↓
分析需求特征（是否跨版本迭代、是否有公共复用价值）
     ↓
┌─ 是项目需求 → 查找或创建 project_local/<project_name>/
│                      ↓
│                  询问用户确认项目名（如未提供）
│                      ↓
│                  在 knowledge/project_local/<project_name>/ 建立项目锚点
│                      ↓
│                  需求文档 → resource/<req_name>/<version>_raw.docx
│                  项目关联 → knowledge/project_local/<project_name>/backlog/
└─ 否（单次需求）→ 直接走 workflow_assets/<req_name>/<version>/
                       ↓
                   不建立项目锚点
```

### A1.3 项目目录结构（已确认项目时）

```
knowledge/
 project_local/
   <project_name>/          ← 项目根目录（不纳入 git）
     backlog/               ← 项目级 backlog（可跨版本复用）
     s6/                   ← 项目级导出配置
       export_profiles/
         test_cases.export.json
       xlsx_templates/
         test_cases.template.xlsx
     module_knowledge/      ← 项目级-模块级知识沉淀（v35 新增）
       UI.md
       BIZ.md
       CONFIG.md
       ...
     metadata.json          ← 项目元数据（项目名/创建时间/版本历史）
```

### A1.4 交互询问模板

```
┌─ [AIDocxWorkFlow] 项目需求检测 ─────────────────────────────────┐
│ 检测到需求文档可能为项目级需求，请问：                              │
│                                                                     │
│ 项目名称：[用户填写 / 识别到的项目名]                              │
│ 需求类型：□ 项目级需求（多版本迭代，需沉淀到知识库）              │
│           □ 单次需求（一次性，不沉淀）                            │
│                                                                     │
│ 是否创建/关联项目目录？                                            │
│   [Y] 是，这是项目需求，创建/关联项目目录                         │
│   [N] 否，单次需求，直接进入 workflow_assets/                      │
└─────────────────────────────────────────────────────────────────┘
```

### A1.5 强制要求

- **S1 入口必须显式判定**：用户粘贴需求文档时，必须先问项目级/单次需求，不允许跳过
- **项目名不得为空**：如用户未提供，必须询问
- **项目锚点持久化**：确认项目名后，写入 `knowledge/project_local/<project_name>/metadata.json`
- **project_name 参数传递**：后续 `run_pipeline()` / `run_stage()` 必须携带 `project_name` 参数

### A1.6 调用示例

```python
# S1 入口：自动检测项目需求
result = run_stage(
    "S1",
    req_name="游戏道具商城系统",
    project_name="游戏道具商城系统",  # ← S1 检测后确认的项目名
    version="v3.01",
)
# downstream stages automatically use project_name from context
```

---

## §A2 项目级-模块级知识沉淀（v35 新增）

> **目的**：后续阶段（S5/S6）收到项目级需求时，整理项目级-模块级知识沉淀到 `knowledge/project_local/<project_name>/module_knowledge/` 目录，方便后续复用和模块专家归档。

### A2.1 沉淀时机

| 阶段 | 沉淀内容 | 沉淀路径 |
|------|----------|----------|
| S5 完成后 | 按模块汇总的 TP 分布（按 8 模块分组统计）| `module_knowledge/s5_summary.md` |
| S6 完成后 | 按模块汇总的 TC 分布 + 模块复杂度评估 | `module_knowledge/s6_summary.md` |
| S7 完成后 | 按模块汇总的审查结果 + 缺陷模式 | `module_knowledge/s7_summary.md` |
| S8 完成后 | 根因分析 + 模块级改进建议 | `module_knowledge/s8_summary.md` |

### A2.2 沉淀格式模板

```markdown
# 项目级-模块级知识沉淀 — <project_name> <version>

生成时间：<timestamp>
沉淀阶段：S5 / S6 / S7 / S8

## 按模块分布

| 模块 | TP/TC 数 | 覆盖率 | 缺陷模式 | 备注 |
|------|----------|--------|----------|------|
| UI | N | XX% | ... | ... |
| BIZ | N | XX% | ... | ... |
| CONFIG | N | XX% | ... | ... |
| UTIL | N | XX% | ... | ... |
| LINK | N | XX% | ... | ... |
| LOG | N | XX% | ... | ... |
| SPECIAL | N | XX% | ... | ... |
| HINT | N | XX% | ... | ... |

## 模块复杂度评估

| 模块 | 复杂度 | 评估依据 |
|------|--------|----------|
| UI | HIGH/MEDIUM/LOW | Epic 数 × Story 数 × 边界条件数 |
| BIZ | ... | ... |

## 缺陷模式汇总

| 缺陷模式 | 模块 | 出现次数 | 根因 |
|----------|------|----------|------|
| ... | ... | ... | ... |

## 沉淀状态

- [x] 已沉淀到 `knowledge/project_local/<project_name>/module_knowledge/`
- [ ] 已通知对应模块专家 Agent 审核
```

### A2.3 模块专家通知机制

沉淀完成后，自动通知对应模块专家 Agent（通过 Agent 消息）：

```
通知：项目 <project_name> 已完成 S5/S6/S7/S8，对应模块专家请审核沉淀内容：
- UI 模块沉淀 → 通知 /ui-expert
- BIZ 模块沉淀 → 通知 /biz-expert
- CONFIG 模块沉淀 → 通知 /config-expert
- UTIL 模块沉淀 → 通知 /UTIL-expert
- LINK 模块沉淀 → 通知 /link-expert
- LOG 模块沉淀 → 通知 /log-expert
- SPECIAL 模块沉淀 → 通知 /special-expert
- HINT 模块沉淀 → 通知 /hint-expert
```

### A2.4 与公共知识库的关系

- **项目级沉淀**：存入 `knowledge/project_local/<project_name>/module_knowledge/`（不纳入 git）
- **模块专家审核后**：可提取为公共知识，存入 `knowledge/public/module_templates/<MODULE>/`
- **审核流程**：项目级沉淀 → 模块专家审核 → 人工确认 → 入公共库

### A2.5 调用示例

```python
from ai_workflow.knowledge_indexer import index_project_module_knowledge

# S5/S6/S7/S8 完成后调用
index_project_module_knowledge(
    project_name="游戏道具商城系统",
    stage="S5",
    version="v3.01",
    summary={
        "UI": {"tp_count": 45, "coverage": 0.95},
        "BIZ": {"tp_count": 120, "coverage": 0.98},
        # ...
    }
)
```

---

## §A3 模块专家编排进 S5/S6 + merge-expert + S6 强制公共级 xlsx（v35 新增）

> **目的**：将 8 个模块专家的 TP/TC 产出并行编排进 S5/S6，引入 merge-expert 专门负责合并，解决主 agent 长上下文脱轨问题。
> **与 project_name 无关**：并行是 S5/S6 的标准工作模式，不受项目级/单次需求影响。

### A3.0 核心原则

1. **主 agent 不生产内容**：只做 orchestrator，负责调度，不自己写 TP/TC
2. **8 个 expert 并行**：每个 expert 独立产出，不互相阻塞（≤5 并发由 Cursor Task 工具控制）
3. **merge-expert 串行收尾**：等所有 expert 完成后合并，防止主 agent 长上下文脱轨
4. **Python 层只生成 prompt**：不调用 Cursor SDK，不做 IPC，把编排指令交给主 agent 执行

### A3.1 流水线架构

```
主 agent（编排者，不生产 TP/TC）
  ↓ orchestrator prompt（含 8 个 expert 指令 + merge-expert 指令）
  │
  ├─ 批次 1（≤5 并发）─────────────────────────────────────┐
  │  Task(/ui-expert)    → UI_module_tp.json              │
  │  Task(/biz-expert)   → BIZ_module_tp.json             │
  │  Task(/config-expert) → CONFIG_module_tp.json          │
  │  Task(/UTIL-expert)   → AUX_module_tp.json             │
  │  Task(/link-expert)  → LINK_module_tp.json            │
  └────────────────────────────────────────────────────────┘
  │
  ├─ 批次 2（≤5 并发）─────────────────────────────────────┐
  │  Task(/log-expert)   → LOG_module_tp.json            │
  │  Task(/special-expert) → SPECIAL_module_tp.json      │
  │  Task(/hint-expert)  → HINT_module_tp.json           │
  └────────────────────────────────────────────────────────┘
  │
  ↓（所有草稿就绪）
  │
  ├─ /merge-expert  ─────────────────────────────────────┐
  │  读取 _module_expert_drafts/*.json                     │
  │  合并 → 去重 → 重分配 ID → 覆盖校验                   │
  │  写入 test_points.json                                │
  └──────────────────────────────────────────────────────┘
  ↓
主 agent（收到 test_points.json → 调用 save_stage5_output()）
```

### A3.2 草稿目录约定

```
<req_name>/<version>/「S5 测试点生成」/
  _module_expert_drafts/
    UI_module_tp.json
    BIZ_module_tp.json
    CONFIG_module_tp.json
    AUX_module_tp.json
    LINK_module_tp.json
    LOG_module_tp.json
    SPECIAL_module_tp.json
    HINT_module_tp.json
  test_points.json        ← merge-expert 写入（最终产物）
  merge_report.json       ← merge-expert 写入（合并报告）
```

S6 同理，`_module_expert_drafts/` 下为 `*_module_tc.json`。

### A3.3 并行约束

| 约束 | 值 | 说明 |
|------|------|------|
| 每批并发上限 | 5 | Cursor Task 工具限制 |
| expert 总数 | 8 | 8 个模块 expert |
| 批次 | 2 批（第 1 批 5 个 + 第 2 批 3 个） | |

### A3.4 merge-expert 职责

| 职责 | 说明 |
|------|------|
| 收集 | 读取 `_module_expert_drafts/*.json` |
| 验证 | 检查各模块产出完整性 |
| 合并 | 合并所有 `test_points` / `test_cases` |
| 去重 | 指纹去重（module + description + obj_ref） |
| 重分配 ID | 全局唯一，按模块前缀 + 序号重排 |
| 覆盖校验 | 对照 S2 backlog 验证覆盖率 |
| 输出 | 写入 `test_points.json` / `test_cases.json` + `merge_report.json` |

详见 `/merge-expert` skill。

### A3.5 S5 orchestrator prompt 模板

主 agent 执行 S5 时，由 Python 层生成 orchestrator prompt（写入临时文件），主 agent 读取后执行：

```
# S5 模块专家编排指令

## 上游输入
- backlog.json 路径：<req_name>/<version>/「S2 需求拆解」/backlog.json

## 阶段目录
<req_name>/<version>/「S5 测试点生成」/

## 草稿目录（每个 expert 产出写入这里）
<req_name>/<version>/「S5 测试点生成」/_module_expert_drafts/

## 你的角色
你是编排者，不自己写 TP。用 Task 工具调度 8 个 expert。

## 执行步骤

### Step 1：并行调度第 1 批 expert（≤5 并发）

使用 Task 工具，并行 launch 以下 5 个 expert：
- /ui-expert：生成 UI 模块 TP，写入 _module_expert_drafts/UI_module_tp.json
- /biz-expert：生成 BIZ 模块 TP，写入 _module_expert_drafts/BIZ_module_tp.json
- /config-expert：生成 CONFIG 模块 TP，写入 _module_expert_drafts/CONFIG_module_tp.json
- /UTIL-expert：生成 UTIL 模块 TP，写入 _module_expert_drafts/AUX_module_tp.json
- /link-expert：生成 LINK 模块 TP，写入 _module_expert_drafts/LINK_module_tp.json

每个 expert 的 task prompt 包含：
1. 读取 backlog.json
2. 筛选属于自己模块的 Story/Epic
3. 生成 TP（格式见 aidocx-s5-test-points/SKILL.md §3）
4. 写入 <module>_module_tp.json（含 meta.header：module/expert/req_name/version/story_ids）

### Step 2：并行调度第 2 批 expert（≤5 并发）

- /log-expert：写入 _module_expert_drafts/LOG_module_tp.json
- /special-expert：写入 _module_expert_drafts/SPECIAL_module_tp.json
- /hint-expert：写入 _module_expert_drafts/HINT_module_tp.json

### Step 3：调度 merge-expert

等所有 8 个草稿文件写入完成后：
1. /merge-expert
2. 读取 _module_expert_drafts/*.json
3. 合并 → 去重 → 重分配 ID → 覆盖校验
4. 写入 test_points.json + merge_report.json

### Step 4：调用 save_stage5_output()

调用 save_stage5_output() 将 test_points.json 规范化并写入最终产物。

## 成功标准
- _module_expert_drafts/ 下有 8 个 *_module_tp.json
- test_points.json 存在且含所有模块的 TP
- merge_report.json 存在且含去重报告
```

### A3.6 S6 orchestrator prompt 模板

与 S5 类似，区别：
- 上游输入为 `test_points.json`（S5 产物）
- 草稿目录为 `_module_expert_drafts/*_module_tc.json`
- 最终产物为 `test_cases.json` + `test_cases.xlsx`（公共级）
- `/merge-expert` 读 TC 草稿，输出 `test_cases.json`
- 最后调用 `format_test_cases()`（已内置强制公共 xlsx 逻辑）

### A3.7 S6 强制公共级 xlsx 产出（核心约束）

> ⚠️ **强制要求**：S6 阶段**必须**强制产出公共级 xlsx（使用 `_DEFAULT_XLSX_PROFILE`），不受 `project_name` 参数影响。

| 产出 | 路径 | 强制？ | 使用 profile |
|------|------|--------|-------------|
| `test_cases.json` | `<req_name>/<version>/「S6 测试用例生成」/test_cases.json` | ✅ 强制 | — |
| `test_cases.xlsx`（公共级） | 同上目录 | ✅ **强制** | `_DEFAULT_XLSX_PROFILE`（10 列） |
| `test_cases.xlsx`（项目级） | `<project_name>/test-case_<project_name>.xlsx` | ⚠️ 可选 | `export_profiles/` |
| `merge_report.json` | 同上目录 | ✅ 强制 | — |

### A3.8 `format_test_cases()` 返回值契约（v35 更新）

```python
{
    "json": str,           # test_cases.json 路径，始终有值
    "md": str | None,     # test_cases.md 路径，project_name 为 None 时为 None
    "xlsx": str,          # test_cases.xlsx（公共级），始终有值 ⚠️
    "xlsx_project": str | None,  # 项目级 xlsx（可选）
    "case_count": int,
    "summary": dict,
    "gate": dict,
    "status_writeback": dict,
    "export_profile": dict | None,
    "xlsx_template": str | None,
    "project_name": str | None,
}
```

### A3.9 与 `run_pipeline()` 的集成

```python
# 完整流水线（S5 → S6 → S7），集成模块专家编排
pipeline = run_pipeline(
    ["S5", "S6", "S7"],
    req_name="游戏道具商城系统",
    project_name="游戏道具商城系统",
    version="v3.01",
    # 注意：模块编排由主 agent 通过 orchestrator prompt 执行
    # stage_callable 只在 Python 层执行最终规范化
    stage_callables={
        "S5": lambda: save_stage5_output(
            "游戏道具商城系统",
            test_points_json,  # merge-expert 产出
            version="v3.01",
            project_name="游戏道具商城系统",
        ),
        "S6": lambda: format_test_cases(
            test_cases_json,   # merge-expert 产出
            backlog,
            test_points,
            req_name="游戏道具商城系统",
            version="v3.01",
            project_name="游戏道具商城系统",
        ),
        "S7": lambda: save_stage7_output(...),
    },
)
```

### A3.10 错误处理

| 场景 | 处理方式 |
|------|----------|
| expert 草稿缺失 | merge-expert 跳过该模块，记录到 `merge_report.json` |
| 某模块无 TP/TC 产出 | 记录到 `omission_ledger.json`，merge-expert 继续 |
| merge-expert 合并失败 | 返回 FAIL_MERGE，生成 `fail_report_S5.md` / `fail_report_S6.md` |
| S6 公共级 xlsx 强制产出失败 | 生成 `fail_report_S6.md`，阻塞后续阶段 |
| 主 agent 脱轨 | 由 orchestrator prompt 的结构化步骤约束；仍脱轨则人工介入 |

### A3.11 为什么需要 merge-expert

| 问题 | 无 merge-expert | 有 merge-expert |
|------|----------------|----------------|
| 主 agent 工作内容 | 生成 TP/TC + 合并 | 仅编排调度 |
| 主 agent 上下文长度 | 8 expert 产出全部涌入上下文 | 上下文只有 orchestrator prompt + merge 产物路径 |
| 长上下文风险 | 高（8×150+ TP/TC 涌入）| 低（只接收 merge 产物） |
| 合并质量 | 主 agent 合并时可能遗漏/冲突 | merge-expert 专司合并，有去重算法 |
| 专家一致性 | 主 agent 对 8 模块理解不一致 | 各 expert 独立产出，merge 保持一致性 |
| 懒思考风险 | 高（任务切换 + 长上下文）| 低（主 agent 只做编排） |

## 9. 何时使用

在以下场景应优先使用本 skill：

- 需要把多个阶段按运行时 gate 串起来执行
- 需要把端到端回归绑定到真实运行时资产
- 需要判断某一阶段失败后，下游是否应停止
- 需要让对话层入口与实现层编排保持同一套语义

---

## 10. goal-loop 驱动模式

> **来源**：goal-loop/SKILL.md 五段式自治闭环能力集成
> **目的**：使 `run_pipeline()` 支持 goal-loop 自治循环，在保留向后兼容的前提下实现 Plan→Act→Audit→Review→Iterate 五段式闭环

### 10.1 触发条件

当 `run_pipeline()` 接收到 `goal` 参数时，进入自治循环模式：

```python
pipeline = run_pipeline(
    ["S5", "S6", "S7"],
    req_name="游戏道具商城系统",
    project_name="<project_name>",
    version="v3.01",
    goal="完整生成游戏道具商城系统的测试用例，验收标准：S5 产出 test_points.json、S6 产出 test_cases.json、S7 审查通过",
    accept_criteria=[
        "S5 目录存在且含 test_points.json",
        "S6 目录存在且含 test_cases.json",
        "S7 审查覆盖率 ≥ 90%",
    ],
    token_limit=200_000,
    max_rounds=5,
)
```

### 10.2 参数契约

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `goal` | `str \| None` | `None` | 用户目标描述；有值时进入 goal-loop 模式 |
| `accept_criteria` | `list[str] \| None` | `None` | 可量化验收断言清单（≥ 1 条） |
| `token_limit` | `int` | `200_000` | Token 预算上限 |
| `max_rounds` | `int` | `5` | 最大迭代轮次 |
| `severity_label` | `str` | `"MAJOR"` | BLOCKER / MAJOR / MINOR |
| `process_criteria` | `list[str] \| None` | `None` | 内部过程类验收（可选） |

### 10.3 五段式集成映射

| goal-loop 阶段 | aidocx-workflow-conversation 映射 |
|---|---|
| **Plan** | 解析 `goal` → 拆分 `task_queue`（每 task 含 `id`/`title`/`status`/`artifact`）→ 映射到 `stages` 列表 |
| **Act** | 调用 `run_pipeline(stages, ...)` 执行阶段流水线；每次 Act 写入 `latest_artifact` |
| **Audit** | 每阶段完成后：读产物 + 对照 `accept_criteria` 逐条判定 `PASS` / `FAIL` / `UNKNOWN` |
| **Review** | 汇总本轮所有 `FAIL` → 缺陷分类（严重/一般/优化）+ 根因定位 + 修复方案 |
| **Iterate** | 全部 `PASS` → `status=achieved`；存在 `FAIL` 且未超限 → `loop_round+=1`，继续 Act；达到上限 → `status=budget-limited` |

**禁止跳轮条款**：每轮必须产出 `audit_<round>.md` + `review_<round>.md`，不得以"无新交付物"为由跳过 audit。

### 10.4 快照持久化

快照 20 字段定义见 `goal-loop/SKILL.md` §2，持久化路径：`.goal-log-db/active/<goal_id>/snapshot.json`。

| 操作 | 函数 |
|---|---|
| 创建快照 | `goal_snapshot.create_snapshot()` |
| 更新快照 | `goal_snapshot.update_snapshot()` |
| 读取快照 | `goal_snapshot.load_snapshot()` |
| 列出活跃目标 | `goal_snapshot.list_active_goals()` |
| 追加遗留项 | `goal_snapshot.add_follow_up_item()` |
| 更新效能统计 | `goal_snapshot.update_efficiency_stats()` |
| 签名漂移检测 | `goal_snapshot.compute_similarity()` |

### 10.5 三层熔断

| 熔断层 | 默认阈值 | 触发动作 |
|---|---|---|
| 最大迭代轮次 | `max_rounds=5`（`loop_round >= 5`） | `status=budget-limited`，暂停循环 |
| Token 预算 | `token_limit=200_000`（`token_budget.used >= limit`） | 同上 |
| 用户输入阻断 | 检测到未读用户消息 | `status=paused`，等待人工指令 |

### 10.6 事件驱动续跑

| 事件 | 触发器 | 动作 |
|---|---|---|
| `sessionStart` | Cursor 窗口重载 / 会话刷新 | 读快照 → 注入 system_reminder 提示继续 Act |
| `afterFileEdit` | Agent 写文件完成 | 触发 Audit（对比 `snapshot.latest_artifact` vs `accept_criteria`） |
| `afterAgentResponse` | Agent 每次响应结束 | 破环机制双门判定（见 `goal-loop/SKILL.md` §10） |

### 10.7 向后兼容保证

- `goal=None`（默认）时：完全走原有顺序编排逻辑，不创建快照，不进入五段式循环
- `run_stage()` 不受影响
- `execute_simple_flow()` / `execute_full_flow()` 不受影响
- 已有的 `stage_callables` 参数继续有效

### 10.8 与 goal-loop/SKILL.md 的关系

本 skill 是 goal-loop 能力在 AIDocxWorkFlow 流水线场景的**应用层集成**：

- **上游能力源**：`goal-loop/SKILL.md` 定义五段式闭环 + 快照 20 字段 + 三层熔断 + 事件驱动
- **本 skill 职责**：将 goal-loop 能力映射到 `run_pipeline()` 的 stages 流水线
- **不修改上游**：goal-loop/SKILL.md 独立维护，作为通用自治循环规范

**引用约束**：本 skill 引用 goal-loop/SKILL.md 的内容时，以 goal-loop/SKILL.md 最新版本为准，不在本 skill 中重复定义。
