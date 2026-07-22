# out_of_scope.md（v27 — AI 自治规则放宽 v1）

> **依据**：goal-loop SKILL v1.2 §3.1 强制产出
> **Goal ID**：`9b1ca386-de47-4d0a-bd60-0206781429be`
> **承接**：`governance/design_iter/plans/v27/GOAL.md`（用户拍板版，2026-07-19）
> **创建日期**：2026-07-20

---

## 功能禁区

- ❌ **不动 v17 阶段 5 项约束**（fp_name / steps[] / test_method[] / tp_reference / preconditions[]）——v28 carry（GOAL.md §2 已声明 Out of Scope）
- ❌ **不动 D1-D3 goal-loop 早期约束放宽** ——v29 carry
- ❌ **不动 B2 / B4 业务门禁放宽**（A 组中优 / E 组）——v30 carry
- ❌ **不动 A1/A3/A4/B3 内部冗余合并** ——v30 carry
- ❌ **不重做 v3.02 Goal（test_cases 8 项修复）**——独立 goal `4c1eedec`，本轮 paused 状态
- ❌ **不动 v17-v22 / v25 归档档**——已闭环方案，本轮不动
- ❌ **不重写 DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3**（唯一阈值 SSOT）——只改 §2.3 索引指 §4.3

## 技术栈禁区

- ❌ **不引入新依赖**（DNA §9.1 红线）
- ❌ **不动 dna_decision_density_check.py 业务函数**（已支持 env 覆盖 = 5，v27 GOAL.md §1 第 2 行已完成）
- ❌ **不动 hooks.json 中已注册的 hook 列表**（sessionStart v1 单 goal `goal_loop_hook.py` 已实现——C2 决策保留不注册避免双注入）
- ❌ **不动 .mdc / SKILL.md 已闭环方案的字段映射 / 枚举定义**（如 11.3 SSOT 清单）

## 职责边界禁区

- ❌ **不动 knowledge/public/goal_loop/**（公共知识库，Agent 不得直接入库）
- ❌ **不动 .gitignore**
- ❌ **不 commit**（用户硬约束）
- ❌ **不动 git config / git history**
- ❌ **不触碰 .pytest_cache/**
- ❌ **不动 v18/v19 已 achieved goal 的快照**（保留为审计锚点）

## 反向边界（特别标注）

1. **C2 决策已确定 = 不动 hooks.json**（避免双注入）——验证 §6 中应**保留 GOAL.md 原话**不得静默改成"已注册"
2. **C4 决策已确定 = 5 问对齐**——验证前需 Read `before_prompt_dna_check.py` 实际注入文本确认已对齐
3. **C1/A2 决策已确定 = 默认 5**——验证前需 Read `dna_decision_density_check.py:45` 确认 `DENSITY_THRESHOLD = int(..., "5")` 已落地

## 触发熔断条件

| 条件 | 触发动作 |
|---|---|
| §2.3 / §4.3 / §11.3 任一处出现非索引指向 SSOT 的硬编码 | BLOCKER：撤销 + 写 DT-v27.1 |
| hook 改动未跑 self-test | BLOCKER：撤销 + 写 DT-v27.2 |
| 补注册 hooks.json 后未验证会话启动不报错 | MAJOR：人工确认 |
| v17 5 项约束在本轮被私自处理 | BLOCKER：撤销 + 写 DT-v27.3 |
| C2 被偷改为"已注册 session_resume_multi_goal.py" | BLOCKER：撤销 + 写 DT-v27.4（违反 v27 §1 第 3 行精审决策） |
