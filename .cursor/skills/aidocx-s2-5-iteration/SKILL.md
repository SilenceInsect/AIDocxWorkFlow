---
name: aidocx-s2-5-iteration
description: >
  AIDocxWorkFlow Stage 2.5 — 迭代规划。7步迭代规划（负载平衡/任务确认/启动会/任务录入/资源锁定/并行工作/执行跟进），产出迭代计划报告。使用当用户执行 /aidocx-s2-5-iteration、粘贴 S2 backlog、或进行 S2.5 迭代规划任务。
  Use when the user runs /aidocx-s2-5-iteration, pastes S2 backlog, or starts iteration planning.
  使用当用户执行 /aidocx-s2-5-iteration、粘贴 S2 backlog、或进行 S2.5 迭代规划任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s2-5-iteration
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S2.5 — 迭代规划

> **⚠️ 全流程模式默认跳过本阶段（opt-in）**
>
> - S2.5 迭代规划只解决"开发节奏/资源/排期"问题，**对 S5 测试点、S6 用例的产出数量/质量无强关系**。
> - **全流程模式默认不执行 S2.5**。如需包含：执行 S2 之前显式声明 `AIDOCX_INCLUDE_S2_5=true`（详见 `.cursor/rules/AIDocxWorkFlow.mdc` 顶部「编排开关」节）。
> - **本 skill 被独立调用时（即用户输入 `/aidocx-s2-5-iteration` 或粘贴 S2 backlog）**：不受 `AIDOCX_INCLUDE_S2_5` 控制，**直接执行**。

**独立阶段**：可单独调用。上游材料（S2 backlog）审查合格后开始，失败写失败报告。

---

## Step 0 — 项目配置收集（执行前必须完成）

> **强制前置**：S2.5 在正式开始迭代规划前，必须先收集并确认项目配置参数。配置不全不得进入 7 步规划。

### 必须收集的配置参数

| 参数 | 说明 | 示例 |
|------|------|------|
| 项目名（req_name） | 需求名称 | 游戏道具商城系统 |
| 版本名（version） | 版本标识 | v1.0 |
| 排期开始日期 | 迭代第一天 | 2025-07-01 |
| 排期截止日期 | 迭代最后一天 | 2025-07-12 |
| 策划预估工时（h） | 产品策划阶段估算工时 | 40h |
| 前端预估工时（h） | 前端开发估算工时 | 80h |
| 后端预估工时（h） | 后端开发估算工时 | 120h |
| 测试预估工时（h） | 测试估算工时 | 60h |
| 团队规模 | 各角色人数 | 前端2人·后端3人·测试2人 |
| 迭代总工时（周） | 任务管线估算总时长 | 1.5周 |

### 快速迭代参考基准（1.5 周全流程）

```
迭代周期 1.5 周 ≈ 7.5 工作日 ≈ 60h/人
- 前端 2 人：共 120h
- 后端 3 人：共 180h
- 测试 2 人：共 120h
- 合计：420h
```

### 收集方式

执行 S2.5 时，若检测到项目配置不完整，**必须主动询问用户**，不得自行假设默认值后跳过。逐项列出待填写字段，逐项确认。

### 配置保存

收集完成后，将配置保存为 `project_config.json` 并写入输出目录。

---

## 阶段入口

**触发**：`/aidocx-s2-5-iteration` 或粘贴 S2 backlog

**前置材料**：S2 backlog.md + project_config.json（配置不全不得执行）

**材料缺失时**：生成失败报告，停止 S2.5。

---

## §1.4 LLM 必读材料（阶段前置）

**开始 7 步规划前，必须先 Read 以下材料。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| 1 | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| 迭代任务按模块前缀组织；负载均衡以模块为单位 |
| 2 | S2 backlog | `workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.md` | 迭代规划的对象；所有 Story/FP 的优先级和工作量是规划基准 |
| 3 | 需求对象 | `workflow_assets/<req_name>/「S2 需求拆解」/<version>/requirement_objects.json` | OBJ 层工作量估算更细 |

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

| 文件 | 路径 |
|------|------|
| 项目配置 | `workflow_assets/<req_name>/「S2.5 迭代规划」/<version>/project_config.json` |
| 迭代规划报告 | `workflow_assets/<req_name>/「S2.5 迭代规划」/<version>/iteration_plan.md` |
| 迭代规划数据 | `workflow_assets/<req_name>/「S2.5 迭代规划」/<version>/iteration_plan.json` |

报告内容：项目配置 → 迭代目标 → 负载平衡表 → 里程碑 → 资源锁定 → 风险点 → 任务分配

---

## 失败报告

路径：`workflow_assets/<req_name>/「S2.5 迭代规划」/<version>/fail_report_S2_5.md`

---

## 自动化支持

```python
from ai_workflow.conversation_skills import save_iteration_plan, make_stage2_5_skill

# 生成协作技能（可传入 project_config）
skill = make_stage2_5_skill(req_name="游戏道具商城系统", version="v1.0",
                           project_config={"req_name": "...", "schedule": {...}, ...})

# 保存结果
save_iteration_plan(req_name, plan_md, plan_json, version,
                    project_config={"req_name": "...", ...})
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S2_5_ITERATION.mdc`
- 保存逻辑：`ai_workflow/conversation_skills.py`
