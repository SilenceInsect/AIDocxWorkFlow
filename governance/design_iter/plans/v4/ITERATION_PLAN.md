# AIDocxWorkFlow v4 迭代执行计划

> 本文件是 v4 的实施计划，不替代 `PLAN.md`。
> `PLAN.md` 说明为什么改、改成什么；本文件说明按什么顺序落地、怎么验收、哪些问题未闭合。

---

## 0. 当前基线

### 当前审计结论（2026-06-28）

- **结论**：v4 属于“部分落地，未闭环”。
- **已落地**：
  - `stage_context_builder.py` / `stage_gatekeeper.py` / `coverage_validator.py` / `recurring_failures.py` 已存在
  - S5/S6 已具备 `stage_context` / `read_ack` / ledger 生成骨架
  - S7 已能读取 coverage/omission ledger 摘要，并在 rule/skill 中声明账本为前置材料
- **未闭环**：
  - `aidocx-workflow-conversation` 文档与实际 v4 编排实现仍不一致，仍残留“手工步骤说明”与旧 API 叙述
  - runtime consistency gate 只有 severity 映射，尚未完整检查 `stage_context/read_ack/ledger` 这类运行时资产
  - S7 对账本的消费已进入代码，但缺少“真实产物证据 + 回归样例”来证明链路跑通
  - recurring failures 已支持读取和注入，但 S7/S8 还没有稳定写回闭环
  - `decisions.json` 仍停留在 `draft / proposal`，治理记录未同步实现状态
- **本轮目标**：先写清上述审计结论，再完成一个“有证据的最小闭环”：
  1. workflow skill 与 v4 编排实现对齐
  2. runtime gate 增补最关键的运行时阻断检查
  3. 跑出 S5/S6/S7 的 gate + ledger + review 证据产物
  4. 回写 v4 决策状态

### 本轮闭环结果（2026-06-28）

- **已完成**：
  - `aidocx-workflow-conversation/SKILL.md` 已补 v4 推荐入口，和 `run_stage()` / `run_pipeline()` 对齐
  - runtime gate 已区分 `preflight` / `postflight`，不再把“未来产物”提前当作 preflight 阻断项
  - `save_stage7_output()` 已落到 S7 正确目录，S7 契约与产物路径一致
  - 样例 `游戏道具商城系统 / v3.01` 已跑通以下证据：
    - S5：`stage_context.*` / `read_ack.json` / `preflight_gate.json` / `postflight_gate.json` / `coverage_ledger.json` / `omission_ledger.json` / `test_points_summary.json` / `test_points_summary.md`
    - S6：`stage_context.*` / `read_ack.json` / `preflight_gate.json` / `postflight_gate.json` / `coverage_ledger.json` / `omission_ledger.json`
    - S7：`stage_context.*` / `read_ack.json` / `preflight_gate.json` / `postflight_gate.json` / `review_snapshot.*` / `review_report.*`
- **仍未完成**：
  - recurring failures 仍是“可注入”，还不是“S7/S8 自动写回”
  - workflow conversation 仍有旧式说明段落，尚未完全收束成纯编排契约
  - 尚未补最小自动化回归测试文件

### 已完成

- 新增 v4 草案：`PLAN.md` / `open_questions.md` / `resolved_questions.md` / `decisions.json`
- 新增运行时上下文机制：
  - `ai_workflow/runtime_contracts.py`
  - `ai_workflow/stage_context_builder.py`
  - `ai_workflow/stage_gatekeeper.py`
  - `ai_workflow/recurring_failures.py`
- 新增覆盖账本机制：
  - `ai_workflow/coverage_validator.py`
- S5/S6 已接入：
  - `stage_context.md`
  - `stage_context.json`
  - `read_ack.json`
  - `coverage_ledger.json`
  - `omission_ledger.json`
- S5/S6 rule 和 skill 已加入 `coverage-first` 与 anti-coding-mindset 约束
- 基础验证已通过：
  - `python3 -m py_compile ...`
  - `run_preflight_gate('S6', ...)`
  - `run_postflight_gate('S6', ...)`

### 当前风险

- S7 还没有真正消费 `coverage_ledger.json` / `omission_ledger.json`
- workflow-conversation 仍偏说明文档，尚未成为真实 orchestrator
- `consistency_check.py` 仍是诊断型，不是 runtime 阻断型
- v4 gate 目前主要覆盖 S5/S6，S1-S4/S7/S8 还未完全纳入
- 工作区存在未归属变更：`requirements.txt`、`ai_workflow/skillopt_poc.py`

---

## 1. 迭代目标

v4 后续迭代目标是把当前“已能运行的骨架”推进为“全流程可依赖机制”。

核心结果：

1. S7 必须基于 coverage/omission 账本审查质量。
2. workflow-conversation 必须固定执行 preflight -> stage -> postflight。
3. consistency check 必须能区分阻断问题和警告问题。
4. S8 必须把重复失败写回 governance 目录。
5. 全流程必须有最小回归样例验证。

---

## 2. Milestone 1：稳住 v4 基线

### 目标

确保当前已落地的 v4 骨架不会污染正式资产，也不会因为基础校验缺失继续漂移。

### 任务

| ID | 任务 | 文件/命令 | 验收 |
|---|---|---|---|
| M1-1 | 清理 v4 自测资产 | `workflow_assets/v4_gate_demo*` | 不出现在正式资产目录 |
| M1-2 | 跑 skill 合规校验 | `python3 ai_workflow/validate_skills.py .cursor/skills` | 无 ERROR |
| M1-3 | 跑规则一致性检查 | `python3 -m ai_workflow.consistency_check --all` | 输出问题分级清楚 |
| M1-4 | 为新模块补最小测试 | `tests/` 或现有测试入口 | stage context / gate / ledger 均有样例覆盖 |
| M1-5 | 更新 v4 决策状态 | `decisions.json` | 已落地项从 proposal 改为 decided |

### 完成判定

- 编译通过
- skill 合规无 ERROR
- S5/S6 preflight/postflight 样例通过
- v4 自测资产不混入正式需求目录

---

## 3. Milestone 2：S7 账本审查

### 目标

让 S7 从“字段填充率 + Story 覆盖事实统计”升级为“覆盖缺口审查”。

### 任务

| ID | 任务 | 文件 | 验收 |
|---|---|---|---|
| M2-1 | 读取 coverage/omission ledger | `ai_workflow/auto_reviewer.py` | snapshot 中包含 ledger 摘要 |
| M2-2 | 增加遗漏风险分级 | `auto_reviewer.py` | uncovered = P0，partial = P1/P2 |
| M2-3 | 更新 S7 输出报告 | `auto_reviewer.py` | Markdown 报告含覆盖缺口、遗漏原因、人工复核项 |
| M2-4 | 更新 S7 skill/rule | `.cursor/skills/aidocx-s7-review/SKILL.md`、`.cursor/rules/STAGE_S7_REVIEW.mdc` | 明确 S7 必读账本 |
| M2-5 | 新增 S7 样例测试 | 测试文件 | 缺 coverage ledger 时能给出明确问题 |

### S7 最低审查项

- `coverage_ledger.summary`
- `omission_ledger.summary`
- `status = uncovered` 的 Story
- `requires_human_review = true` 的 omission
- 没有 `covered_by` 的需求对象/功能点

### 完成判定

S7 报告必须能回答：

- 哪些需求点没被用例闭合？
- 哪些遗漏需要人工确认？
- 哪些遗漏可以带理由放行？
- 哪些问题必须回 S5/S6 迭代？

---

## 4. Milestone 3：workflow-conversation 编排器

### 目标

把 workflow-conversation 从“操作指南”升级为“阶段编排契约”，防止脚本绕过 skill/gate。

### 任务

| ID | 任务 | 文件 | 验收 |
|---|---|---|---|
| M3-1 | 新增 `run_stage()` | `ai_workflow/conversation_skills.py` | 每阶段固定 preflight -> stage -> postflight |
| M3-2 | 新增 `run_pipeline()` | `conversation_skills.py` | 可声明阶段列表执行 |
| M3-3 | 定义 stage result schema | `conversation_skills.py` 或 `runtime_contracts.py` | 每阶段返回 status / outputs / gates / next |
| M3-4 | 更新 workflow skill | `.cursor/skills/aidocx-workflow-conversation/SKILL.md` | 不再只是说明手工步骤 |
| M3-5 | 失败报告接入 | `stage_gatekeeper.py` / `conversation_skills.py` | preflight/postflight fail 时写 fail_report |

### 编排状态枚举

- `PASS`
- `FAIL_PRECHECK`
- `FAIL_POSTCHECK`
- `NEED_LLM_OUTPUT`
- `PASS_WITH_BYPASS`
- `SKIPPED`

### 完成判定

任意阶段不能绕过：

- `stage_context.*`
- `read_ack.json`
- preflight gate
- postflight gate

---

## 5. Milestone 4：runtime consistency gate

### 目标

把 `consistency_check.py` 从“发现问题”升级为“运行时分级门禁”。

### 任务

| ID | 任务 | 文件 | 验收 |
|---|---|---|---|
| M4-1 | 增加 severity 字段 | `ai_workflow/consistency_check.py` | issue 可标 `P0_BLOCK` / `P1_WARN` / `P2_INFO` |
| M4-2 | 增加 runtime check | `consistency_check.py` | 检查 stage_context/read_ack/ledger 是否存在 |
| M4-3 | 接入 stage_gatekeeper | `stage_gatekeeper.py` | P0_BLOCK 会阻断 |
| M4-4 | CLI 输出分级 | `python3 -m ai_workflow.consistency_check --all` | 报告按 severity 聚合 |

### P0_BLOCK 初始清单

- 缺 `stage_context.json`
- 缺 `read_ack.json`
- 缺当前阶段核心产物
- S5/S6 缺 `coverage_ledger.json`
- S5/S6 缺 `omission_ledger.json`
- 下游契约要求字段缺失

### 完成判定

脚本必须能明确返回：

- 是否阻断
- 阻断原因
- 修复建议

---

## 6. Milestone 5：反馈闭环

### 目标

把重复错误从“人提醒”变成“下一轮阶段启动自动注入”。

### 任务

| ID | 任务 | 文件 | 验收 |
|---|---|---|---|
| M5-1 | S7 写失败模式 | `auto_reviewer.py` / `recurring_failures.py` | 新失败可追加到 governance |
| M5-2 | S8 聚合失败模式 | `iteration_aggregator.py` / `self_iteration.py` | 高频失败可进入 recurring failures |
| M5-3 | stage_context 注入 Top N | `stage_context_builder.py` | 不同 stage 注入相关失败 |
| M5-4 | 失败模式去重 | `recurring_failures.py` | 同 pattern 不重复刷屏 |

### 完成判定

同类问题第二次出现时，`stage_context.md` 必须能显示历史失败模式和对应防护项。

---

## 7. Milestone 6：全流程回归样例

### 目标

用一个最小需求样例验证 v4 全链路。

### 样例要求

- 至少 2 个 Epic
- 至少 4 个 Story
- 至少包含：
  - 主路径
  - 异常路径
  - 配置变更
  - 提示/日志
  - 状态切换

### 验收产物

- `stage_context.md/json`
- `read_ack.json`
- `test_points.json`
- `test_cases.json`（公共默认）/ `test_cases.md,xlsx`（项目级导出）
- `coverage_ledger.json`
- `omission_ledger.json`
- `review_snapshot.md/json`
- `fail_report` 或 `PASS` 结论

### 完成判定

跑完整链路后，能直接回答：

- 覆盖了哪些需求对象？
- 遗漏了哪些场景族？
- 哪些遗漏必须人工确认？
- S7 建议回到哪个阶段修？

---

## 8. 推荐执行顺序

1. M1：稳住 v4 基线
2. M2：S7 账本审查
3. M3：workflow-conversation 编排器
4. M4：runtime consistency gate
5. M5：反馈闭环
6. M6：全流程回归样例

理由：

- M1 先防止当前改造继续漂移。
- M2 最快提升测试用例质量，因为 S7 会直接指出覆盖缺口。
- M3 解决脚本绕过 skill 的根因。
- M4 让规则一致性从建议变成阻断。
- M5/M6 负责长期稳定性和回归证明。

---

## 9. 本轮建议先做的最小闭环

如果只推进一个短迭代，建议范围控制在：

1. M1 全部
2. M2-1 到 M2-4
3. M3-1

短迭代验收：

- S6 产出账本
- S7 能读账本并报告遗漏
- `run_stage("S6")` 不能绕过 preflight/postflight

这个闭环完成后，v4 才从“局部机制已落地”进入“质量链路开始闭合”。

---

## 10. 暂不处理

以下事项暂缓，避免扩大改造面：

- S1-S4 全部接入 coverage ledger
- 彻底重写 `conversation_skills.py`
- 引入新的外部依赖
- 重构已有 `workflow_assets` 历史产物
- 自动修改全部历史 skill 文档

---

## 11. 退出条件

v4 迭代完成的最低退出条件：

- S5/S6/S7 均有 stage_context/read_ack/gate 记录
- S5/S6 均有 coverage/omission ledger
- S7 能消费 ledger 并给出覆盖缺口报告
- workflow-conversation 有统一 `run_stage()` 入口
- P0 runtime consistency issue 会阻断流程
- 有一个最小回归样例通过
