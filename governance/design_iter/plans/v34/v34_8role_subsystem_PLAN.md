# v34 子方案 — 8 模块角色子系统（草稿，待用户拍板）

> **状态**：🚧 **DRAFT** — 不进入 goal-loop Act 阶段，等用户对角色契约 + 行为契约 + 接入点逐项拍板。
>
> **触发来源**：2026-07-22 用户原话（按出现顺序）：
> 1. "S1 的需求拆解，需要有一个拆解的角色，角色按规则进行拆解"
> 2. "S1 需要做一个多角色并行任务，8 个模块对应 8 个角色，每个角色按自己的模块，对文档进行深度阅读和思考"
> 3. "需求对象常见的背景、状态、边界等等，都可以在模块的 A～XXX 的模板说明里面找到启发"
> 4. "补齐策划需求没有的，明确策划需求有的，找到策划需求和通用经验矛盾的"
> 5. "8 模块的模版，对审查也是有大的启发和导向作用的"
> 6. "生成对应的模块专项资深的专家，他们负责从模块的模板里学习和思考怎么进行预审和补全，也负责补充模块沉淀知识和经验"
> 7. "你需要思考怎么进行角色创造，行为创造，行为约束，行为推进，确定行为计划，行为执行规范，方法论，行为结果审计，反思，迭代，经验沉淀，模板维护"
>
> **v34 已有的工作**：`link_module_chain_map.md`（LINK 模块双职责工程化落档）。本方案是 v34 的**横向扩展**——把"单模块深度视角"从 LINK 推广到全 8 模块。

---

## 1. 原始目标

```
/goal-loop v34-extension 构建 8 模块角色子系统，让 S1 预审 + S2 拆解按模块并行深度工作
```

---

## 2. 验收标准（Accept Criteria · 待用户确认）

|| # | 标准 | 验证方式 |
|---|---|---|---|
| AC1 | 8 角色卡齐备（CONFIG/UI/BIZ/UTIL/LINK/SPECIAL/LOG/HINT），每卡含：身份 / 行为契约 / 输入 / 输出 / 产物 / 学习来源 | `governance/design_iter/plans/v34/v34_8role_contracts.md` |
| AC2 | 8 角色行为契约覆盖"角色创造 / 行为创造 / 行为约束 / 行为推进 / 行为计划 / 行为执行规范 / 行为结果审计 / 反思 / 迭代 / 经验沉淀 / 模板维护"11 项 | 同上文件 + 用户对每项拍板 |
| AC3 | S1 接入点明确：8 角色在 S1 阶段如何并行预审，产出如何汇聚到 `clarification_checklist.md` | `governance/design_iter/plans/v34/v34_S1_S2_integration_points.md` |
| AC4 | S2 接入点明确：8 角色在 S2 阶段如何并行拆解，产出 OBJ / FP / `template_refs` / `requirement_diff` 如何落档 | 同上文件 |
| AC5 | 臆造防御机制明确：参考 v34 §7 自我纠正日志（3 轮被否），本方案必须有"用户原话 → 角色契约"的强引用链 | `v34_8role_contracts.md` 每条契约段后附用户原话引用 |
| AC6 | 与已有工作的兼容性明确：`module_templates/<MODULE>/<X>_*.md` 保持 SSOT；不引入新的模板目录 | 兼容性矩阵 |
| AC7 | §9.1 ≤ 5 文件改动清单明确：本方案落地涉及哪几个文件 | §5 |

---

## 3. task_queue

|| ID | 任务 | 依赖 | 状态 |
|---|---|---|---|---|
| T-001 | 起草 8 角色卡（身份 / 输入 / 输出 / 产物 / 学习来源）| 用户原话 1-5 | ✅ done（v34_8role_contracts.md） |
| T-002 | 起草 8 角色行为契约 11 项（行为创造 / 约束 / 推进 / 计划 / 规范 / 审计 / 反思 / 迭代 / 经验沉淀 / 模板维护）| 用户原话 7 | ✅ done（v34_8role_contracts.md） |
| T-003 | 起草 S1 预审接入点（8 角色 → clarification_checklist P0/P1/P2）| 用户原话 1-2 | ✅ done（v34_S1_S2_integration_points.md） |
| T-004 | 起草 S2 拆解接入点（8 角色 → OBJ / FP / template_refs / requirement_diff）| 用户原话 3-4 | ✅ done（同上） |
| T-005 | 起草臆造防御（参考 v34 §7 自我纠正日志）| v34 §7 | ✅ done（v34_antipattern_guards.md） |
| T-006 | 用户拍板 8 角色契约 + 11 项行为契约 + S1/S2 接入点 + 臆造防御 | T-001 ~ T-005 | ⏳ 待启动 |
| T-007 | 用户拍板后落地到 §9.1 ≤ 5 文件 | T-006 | ⏳ 待启动 |

---

## 4. 全局约束（锁定）

### 4.1 历史坑点（v33 / v34 已暴露）

- **v34 §7 自我纠正 3 轮**：Agent 把"关联"臆造为"测试可追溯 4 层链"被否 → 把"回归"臆造为"系统级拓扑"被否 → 把"回归"臆造为"子功能静态范围扩展"被否 → **第 3 轮才按用户多层副本实例拍板**。
- **本方案强制**：任何角色契约 / 行为契约 / 接入点，**必须基于用户给过的原话**——不允许 Agent 扩展臆造。

### 4.2 禁止行为

- 不修改 `module_templates/<MODULE>/<X>_*.md` 的现有内容（**只读 + 学习来源**）
- 不创建新的模板目录（**SSOT 集中**）
- 不修改 `.cursor/MODULES.md` 的模块枚举（**8 模块边界是项目铁律**）
- 不修改 S1 / S2 的阶段硬性产物（gm_commands.md / quality_loop_report.md / backlog.json / requirement_objects.json 字段保持不变，**只增 OBJ 内字段**）

### 4.3 兼容性矩阵（待用户拍板）

|| 已有产物 | 本方案是否动 | 备注 |
|---|---|---|---|
| `.cursor/MODULES.md` §4.X 8 模块边界 | ❌ 不动 | SSOT |
| `knowledge/public/module_templates/<MODULE>/<X>_*.md` | ❌ 不动（**只读**） | SSOT |
| `_decision_tree.md` §0 mermaid + §2 拆 8 组 | ❌ 不动 | 你 2026-07-21 已拍板升级 |
| `STAGE_S1_REVIEW.mdc` 评审维度 4 条 | ⚠️ **待定**（T-006） | 是否加 5 维度"8 模块覆盖预审"|
| `STAGE_S2_BREAKDOWN.mdc` OBJ 9 字段 + FP 派生链 | ⚠️ **待定**（T-006） | 是否增 `template_refs` / `requirement_diff` 字段 |
| S2 OBJ 9 字段 | ❌ 不动 | 9 字段是 SSOT |
| S2 FP 派生链（5 字段）| ❌ 不动 | SSOT |
| S1 6 产出（gm_commands / test_coverage / planning_acceptance / quality_loop_report / role_definitions / clarification_checklist）| ❌ 不动 | SSOT |

---

## 5. §9.1 ≤ 5 文件改动清单（本方案落地后 · 待定）

> **本节是预测——T-006 用户拍板后才填**。
>
> **预估**（基于 T-006 拍板结果）：

| # | 文件 | 改动类型 | 备注 |
|---|---|---|---|
| 1 | `.cursor/rules/STAGE_S1_REVIEW.mdc` §新评审维度 | 新增 5 维度"8 模块覆盖预审" 25% 权重 | 仅当 T-006 选项 1 选中 |
| 2 | `STAGE_S1_REVIEW.mdc` §S1 产出清单 | 新增 `module_gap_analysis.md`（8 模块覆盖矩阵）| 仅当 T-006 选项 1 选中 |
| 3 | `.cursor/rules/STAGE_S2_BREAKDOWN.mdc` §OBJ 9 字段 | 新增 `template_refs[]` + `requirement_diff{}` 字段 | 仅当 T-006 选项 2 选中 |
| 4 | `.cursor/skills/aidocx-s5-test-points/SKILL.md` §必读材料 | 升级 §"模板强制遍历产物" | 可选 |
| 5 | `ai_workflow/validators/l1_s6.py` | 增 `template_refs` 非空校验 | 可选 |

> **≤ 5 红线**：5 项改动是上限。任何超出 5 项的改动，必须拆 v35 处理。

---

## 6. 子方案文件清单

|| 文件 | 说明 | 行数（草稿） |
|---|---|---|---|
| `v34_8role_subsystem_PLAN.md` | **本文件** — 草稿 + 任务队列 + 验收标准 + 全局约束 | ~150 |
| `v34_8role_contracts.md` | 8 角色卡 + 11 项行为契约（**每条契约后附用户原话引用**）| ~250 |
| `v34_S1_S2_integration_points.md` | S1 预审接入点 + S2 拆解接入点 | ~200 |
| `v34_antipattern_guards.md` | 臆造防御机制（参考 v34 §7 自我纠正日志）| ~180 |

---

## 7. 自我纠正日志（本方案草稿阶段）

|| 轮次 | 时间 | 错误 | 修正 |
|---|---|---|---|---|
| Round 1 | 2026-07-22 00:16 | Agent 把"8 角色"狭隘理解为"评审维度加一栏"（=25% 权重 8 模块覆盖）| 用户 00:17 纠正——"你需要思考怎么进行角色创造，行为创造..." 11 项机制 |
| Round 2 | 2026-07-22 00:20 | Agent 把"8 角色"窄化在 S1 / S2 两个阶段 | 用户 00:21 隐含纠正——"8 模块对应 8 个角色，每个角色...也负责补充模块沉淀知识和经验" → **8 角色是子系统，不限于 S1/S2** |
| Round 3 | （待） | （待用户拍板 T-006 后填）| — |

**核心学习**：
1. **8 角色不是"加一栏"**——是"角色创造 + 行为创造 + 行为约束 + 行为推进 + 行为计划 + 行为执行规范 + 方法论 + 行为结果审计 + 反思 + 迭代 + 经验沉淀 + 模板维护" **11 项子系统机制**
2. **8 角色不是"阶段工具"**——是"模块子系统"，贯穿 S1 预审 / S2 拆解 / S3-S6 校验 / S8 沉淀的**全生命周期**
3. **8 角色不是"Agent 自主"**——是"基于用户原话 + 模块模板的约束角色"，**任何扩展必须经用户拍板**

---

## 8. 遗留问题

|| # | 问题 | 严重度 | 备注 |
|---|---|---|---|
| Q-001 | 8 角色卡细节：每个角色"专家身份"的深度（如 BIZ 角色 = 服务端业务逻辑专家 vs 业务架构师 vs DBA）| MAJOR | T-006 拍板 |
| Q-002 | 8 角色"并行执行"是 goal_parallel_executor.py 真并行，还是 LLM 上下文分块思考 | MAJOR | T-006 拍板 |
| Q-003 | 8 角色"经验沉淀"落到哪：`module_templates/<MODULE>/P_game_specific.md` vs 新增 `module_templates/<MODULE>/_experience.md` vs 单独目录 | MAJOR | T-006 拍板 |
| Q-004 | 8 角色"反思 / 迭代"周期：每 Story 一次 vs 每 Epic 一次 vs 每 Release 一次 | MINOR | T-006 拍板 |
| Q-005 | 8 角色"模板维护"权限：角色提议修改模板 vs 角色写候选等人工审核入库 | MAJOR | T-006 拍板（候选制 vs 提案制）|
| Q-006 | 与 v34 `link_module_chain_map.md` 的 LINK 双职责视角是否冲突 | MINOR | 已核——LINK 角色承担双职责，**不冲突** |
| Q-007 | 角色与 v3.01 实际产物的对接：`requirement_objects.json` 现有 15 OBJ 如何回标 `template_refs` / `requirement_diff` | MAJOR | 产物不回改（v34 4.2 节原则）—— 仅用于 v3.02 起新版本 |

---

**最后修改**：2026-07-22 00:30 草稿
**goal-loop 轮次**：未启动（**等 T-006 用户拍板**）