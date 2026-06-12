---
name: aidocx-s2-5-iteration
description: AIDocxWorkFlow Stage 2.5 — 迭代规划。7步迭代规划（负载平衡/任务确认/启动会/任务录入/资源锁定/并行工作/执行跟进），产出迭代计划报告。使用当用户执行 /aidocx-s2-5-iteration、粘贴 S2 backlog、或进行 S2.5 迭代规划任务。
disable-model-invocation: true
---

# AIDocxWorkFlow S2.5 — 迭代规划

**独立阶段**：可单独调用。上游材料（S2 backlog）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s2-5-iteration` 或粘贴 S2 backlog

**前置材料**：S2 backlog.md：`workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.md`

**材料缺失时**：生成失败报告，停止 S2.5。

---

## 7步执行规划

| Step | 名称 | 核心目标 |
|------|------|----------|
| 1 | 迭代负载平衡 | 计算每人总工时 vs 迭代周期，识别过载/富余 |
| 2 | 一对一任务确认 | 与每个任务负责人确认能按时完成、依赖项能交付 |
| 3 | 迭代启动会（全员对齐） | 同步目标/任务/截止/里程碑/风险点，需求冻结 |
| 4 | 任务录入与配置 | 录入 Jira/禅道：状态/负责人/截止/依赖/风险/里程碑 |
| 5 | 资源锁定与申请 | 申请压测服务器、测试环境、特殊账号、云资源 |
| 6 | 启动前置并行工作 | 测试提前写用例；开发技术预研；产品补文档 |
| 7 | 进入执行与跟进 | 每日站会/任务状态跟进/风险调整 |

**需求冻结原则**：启动会上宣告需求已锁定，中途不得新增（线上 P0 除外）。

**小需求简化**：不用开启动会，只和相关人员同步任务与排期。

---

## 成功产出

路径：`workflow_assets/<req_name>/「S2.5 迭代规划」/<version>/iteration_plan.md`

同时生成 JSON：`workflow_assets/<req_name>/「S2.5 迭代规划」/<version>/iteration_plan.json`

报告内容：迭代目标 → 负载平衡表 → 里程碑 → 资源锁定 → 风险点 → 任务分配

---

## 失败报告

路径：`workflow_assets/<req_name>/「S2.5 迭代规划」/<version>/fail_report_S2_5.md`

---

## 自动化支持

```python
from ai_workflow.conversation_skills import save_iteration_plan
save_iteration_plan(version, backlog, raw_output, parsed, req_name)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S2_5_ITERATION.mdc`
- Prompt 模板：`ai_workflow/prompts/iteration_planning.md`
