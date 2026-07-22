# GL-009 阶段 review — test case 审查治理

**Goal ID**：`32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3`
**日期**：2026-07-19
**对应状态**：snapshot.status = `achieved` / loop_round = 8 / follow_up_count = 0
**位置**：`governance/design_iter/current/gl009_stage_review.md`（与决策档同层）

> **本档性质**：GL-009 **阶段 review**——不是 R18 单轮 review（见 `.goal-log-db/.../review_18.md`），而是跨 R14-R18 五轮的 **Goal 阶段系统性复盘**。
> 目的：识别 GL-009 治理模式的可复用经验、Skill 规范漏洞、体系性问题，供未来 Goal 设计参考。

---

## 0. 摘要

GL-009 是 AIDocxWorkFlow 治理类 Goal 的典型样本——**8 项 follow-up（4 MAJOR + 4 MINOR）+ 7 项边界问题 follow_up = 15 项任务**，分 5 轮（Round 14-18）执行，每轮 1-4 项，最终完全收敛（status=achieved / follow_up=0）。

**核心经验**：治理类 Goal 应当 **"按依赖而非按数量"分轮**——独立子项目（v3.02 数据迁移）单独成轮、pipeline 接入合并成轮、归档治理合并成轮。

---

## 1. 五轮轨迹回顾

| Round | 任务数 | 类型 | 耗时（估算） | 关键成果 |
|---|---|---|---|---|
| R14 | 4 项 | BLOCKER + MINOR + MAJOR×2 | ~30 min | tc_tp_gap_report.py 新建 + qa_fixer_v301 normalizer + SSOT 注释 + L1 15 cases |
| R15 | 2 项 | MINOR×2 | ~15 min | L1 22 cases（+7） + SKILL Schema 注释 + F-E/F-F SSOT |
| R16 | 7 项（清 3）| MINOR×7 | ~25 min | out_of_scope.md 守卫 SSOT（G-001~G-012）+ .bak 清理（FU-6）+ CONVERGED 初版（FU-7）+ 延后 4 项 |
| R17 | 1 项（核心）| MINOR | ~20 min | v3.02 数据迁移（331 TC + 100% assertion + 0 fp_name + 全套导出）|
| R18 | 3 项 | MINOR×3 | ~25 min | pipeline 接入 assertion 校验 + --auto argv + open_questions 归档 |

**总耗时估算**：~115 min（5 轮，平均 23 min/轮）

---

## 2. 关键模式识别（可复用）

### 2.1 模式 1：按"依赖紧密度"分轮，而非按"任务数"

GL-009 共 15 项任务（8 项主 follow-up + 7 项边界 follow_up），**没有**硬塞 1 轮或 2 轮，而是按依赖拆 5 轮：

| 依赖类型 | 拆分理由 | 实证 |
|---|---|---|
| **独立子项目**（FU-1 v3.02）| 与 pipeline 接入（FU-2/4）解耦 | R17 单独立项 |
| **pipeline 集成**（FU-2 + FU-4）| 同一文件族（stage_gatekeeper / coverage_validator / l1）改 | R18 合并 |
| **归档治理**（FU-5）| 跨档归档（open_questions.md → archive_v17.md） | R18 合并 |
| **守卫 / 清理 / 收尾**（FU-3 / FU-6 / FU-7）| 都是"治理闭环"动作 | R16 合并 |
| **SSOT 注释**（F-A/B/C/D + F-E/F-F）| 业务代码 + L1 校验配套改 | R14 + R15 拆分 |

**结论**：**任务数不是分轮依据，依赖紧密度才是**。

### 2.2 模式 2：byte-lock 守卫 = 治理类 Goal 的硬约束

GL-009 始终守 v3.01 byte-lock（338192 / 41572 bytes 不变），从 R1 到 R18 严守：

| 守卫 | 实测 | 结论 |
|---|---|---|
| G-001 v3.01 test_cases.json | 338192 bytes | ✅ R14-R18 全程严守 |
| G-002 v3.01 test_cases_public.xlsx | 41572 bytes | ✅ R14-R18 全程严守 |
| G-003 v3.01 xlsx dict_repr | 0 | ✅ R14-R18 全程严守 |

**意义**：v3.01 是历史快照（"已交付"基线），治理改造**不应回溯污染**。新建 v3.02 独立目录应用新 SSOT 是正确的"前进式迁移"策略。

**复用建议**：未来治理类 Goal 一律引入 byte-lock 守卫（G-001~G-003 模板），写入 `out_of_scope.md` SSOT。

### 2.3 模式 3：SSOT 修订 + L1 校验器 = 规范-执行闭环

GL-009 的关键收尾——SSOT 注释（SKILL.md / .mdc）+ L1 校验器（l1_format_validator）配套改：

| SSOT 修订 | L1 校验器 helper | self-test |
|---|---|---|
| SKILL §六 Schema（F-D） | check_no_redundant_field | 1 case |
| SKILL §六 Schema（F-E） | check_assertion_completeness | 4 case |
| SKILL §六 Schema（F-F） | check_no_fp_name_field | 3 case |
| STAGE_S5 §1.9.7（F-C） | consistency check | 1 case |

**结论**：**L1 校验器是 SSOT 落地的"机械锚"**——光改 SKILL 注释没用，必须有 self-test case 强制执行。R14 15 cases → R15 22 cases → R18 24 cases（+C24 --auto argv）。

### 2.4 模式 4：FU 拆分原则（用户识别 vs 架构师判断）

GL-009 的 15 项 follow_up 来自两个来源：

| 来源 | 数量 | 处理 |
|---|---|---|
| **用户识别**（Round 3 三方审查）| 8 项 F-A~F-H | 架构师按依赖分 R14+R15 |
| **边界问题**（Round 16 用户追加）| 7 项 FU-1~FU-7 | 架构师按依赖分 R16+R17+R18 |

**架构师决策原则**：

1. **FU-1 v3.02 独立**：因为是"新建目录"，与 pipeline 接入解耦 → 单独立项
2. **FU-2 + FU-4 合并**：因为同源（l1 校验器接入）→ 同轮处理
3. **FU-5 单独延后**：因为是"跨档归档"，工作量"中" → 单独轮做更稳
4. **FU-3 + FU-6 + FU-7 合并**：因为都是"治理闭环"动作（守卫 SSOT + 清理 + 收尾）→ 同轮处理

**结论**：**用户给任务清单，架构师做依赖分析 + 拆分决策**——这是 Goal-loop 模式的精华。

---

## 3. 经验沉淀（写入 knowledge/public/goal_loop/）

### 3.1 QUALITY_BASELINE 候选项

GL-009 验证了以下 baseline 项应进入 `knowledge/public/goal_loop/QUALITY_BASELINE.mdc`：

| 候选 baseline | 当前状态 | 建议 |
|---|---|---|
| byte-lock 守卫（G-001~G-003）| 项目级（out_of_scope.md）| **升级到 baseline**——所有治理类 Goal 强制 |
| SSOT 修订 + L1 校验器配套 | 项目级 | **升级到 baseline**——所有 SSOT 修订必须有 L1 self-test |
| --auto argv 支持外部 JSON 校验 | l1 项目级 | **保留项目级**——非通用 |
| open_questions 主档 + archive 分离 | governance/ 项目级 | **保留项目级**——治理档特有 |

### 3.2 systemic_issues 候选

GL-009 全程**未触发反模式熔断**（§5 反模式检测 0 命中），但识别以下体系性问题：

| 编号 | 问题 | 出现次数 | 处理 |
|---|---|---|---|
| SYS-GL009-001 | v3.01 byte-lock 守则文档化 | 1 次 | 已写入 out_of_scope.md（G-001/G-002/G-003）|
| SYS-GL009-002 | L1 self-test 数量与 SSOT 修订不匹配 | 0 次 | 防御——R14+R15+R18 每改 SSOT 必加 ≥1 self-test |
| SYS-GL009-003 | CONVERGED.md 跨 Goal 覆盖 | 2 次 | 规范——CONVERGED.md 写明"覆盖前档 GL-XXX" + 保留上游 Goal ID |

---

## 4. Skill 规范漏洞（GL-009 视角）

GL-009 实战中识别以下 Skill 规范可优化点：

### 4.1 漏洞 1：Round 6+ 延后 follow_up 缺省机制

**现象**：R16 用户追加 7 项 FU，架构师判断延后 4 项到 R17，但 SKILL v1.2 §3.2 没有"延后到具体 Round N"的字段——本轮通过 `audit_stability.round_16_deferred` 自定义字段补全。

**建议**：SKILL §2.5 task_queue 新增字段 `deferred_to_round: int | null`，schema 显式声明。

### 4.2 漏洞 2：byte-lock 守卫无模板

**现象**：R16 FU-3 创建 out_of_scope.md 时，byte-lock 守则（G-001~G-003）是手动写的，没有 SSOT 模板。

**建议**：`governance/design_iter/templates/byte_lock_guard.md` 模板化"字节级 byte-lock"声明格式。

### 4.3 漏洞 3：SSOT 修订 + L1 校验器配套改无强约束

**现象**：R14/R15 SSOT 修订配套加了 self-test，但 SKILL.md 没强制要求。

**建议**：SKILL §3.3 Audit 阶段新增 baseline 项："SSOT 修订必须配套 ≥1 self-test case"。

### 4.4 漏洞 4：CONVERGED.md 覆盖前档的"链式声明"

**现象**：R18 本档覆盖 R16 CONVERGED.md，需要显式说明"覆盖 GL-XXX · Round X-Y"。

**建议**：CONVERGED.md 模板新增 §0.5 "覆盖链"段，强制声明前档 Goal ID + Round 范围。

---

## 5. Goal-loop 模式评估

### 5.1 收敛轨迹

```
R14 (4 FU) → R15 (2 FU) → R16 (3 FU + 4 deferred) → R17 (1 FU + 3 deferred) → R18 (3 FU + 0 deferred) → achieved
```

**评估**：分轮节奏**理想**——每轮 1-4 项，最后 1 轮（4 项 → 3 deferred → 3 项全清）完成收敛。**没有出现"硬塞 1 轮"的反模式**。

### 5.2 GL-009 vs GL-002 对比

| 维度 | GL-002（S6 用例状态重定义）| GL-009（test case 审查治理）|
|---|---|---|
| 总轮数 | R1-R13（13 轮）| R1-R18（18 轮）|
| 主循环轮数 | R1-R11 | R1-R13 |
| Act 治理轮数 | R12-R13（2 轮）| R14-R18（5 轮）|
| follow_up 总数 | 8 项 | 15 项（8 项主 + 7 项边界）|
| 守卫规则数 | 0（未建立）| 12 条（G-001~G-012）|
| 收敛判定 | converged_with_followup | achieved |

**结论**：GL-009 是 GL-002 的"扩大型"——治理范围更大（15 vs 8）、分轮更细（5 vs 2）、守卫规则更系统（12 vs 0）。**GL-009 的治理经验可作为未来治理类 Goal 的标杆**。

### 5.3 GL-009 自身演进

GL-009 自身在 R14-R18 期间**不断优化治理**：

| 轮次 | 治理动作 |
|---|---|
| R14 | 治理起点——业务代码 + L1 校验器 |
| R15 | 治理深化——SSOT 注释 + L1 self-test 增量 |
| R16 | 治理系统化——out_of_scope.md 守卫 SSOT + 过程资产清理 + CONVERGED 收尾 |
| R17 | 治理应用——独立子项目（v3.02）数据迁移 |
| R18 | 治理接入——pipeline 自动校验 + 历史 Q 归档 |

**结论**：**GL-009 是"边治理边建治理"的样本**——每轮 Act 都同时强化治理本身（FU-3 out_of_scope + FU-5 open_questions + FU-7 CONVERGED）。

---

## 6. 未来 Goal 候选

基于 GL-009 的可复用经验，未来 Goal 候选：

| Goal | 来源 | 描述 |
|---|---|---|
| **GL-010** | GL-009 v3.02 落地 | 基于 v3.02 数据迁移完成 S7 正式审查 → S8 自迭代 |
| **GL-011** | GL-009 pipeline 接入 | 基于 --auto argv 接入 CI/CD pipeline 自动化 L1 校验 |
| **GL-012** | GL-009 治理经验 | 把 GL-009 的 SSOT 修订 + L1 校验器模式推广到其他阶段（S3/S4/S5/S7）|
| **GL-013** | GL-009 守卫规则 | 把 out_of_scope.md 12 条守卫规则模板化，未来治理类 Goal 复用 |

---

## 7. 总结

**GL-009 是 AIDocxWorkFlow 治理类 Goal 的标杆样本**：

- ✅ 8 项主 follow-up + 7 项边界 follow_up 全清
- ✅ byte-lock 守卫全程严守
- ✅ SSOT 修订 + L1 校验器配套改
- ✅ 分轮节奏合理（5 轮 / 1-4 项/轮）
- ✅ 治理自身也在进化（out_of_scope + open_questions + CONVERGED 收尾）
- ✅ snapshot.status = achieved（无遗留、无 blocker）

**经验复用路径**：

1. byte-lock 守卫 → 升级到 baseline（所有治理类 Goal 强制）
2. SSOT + L1 配套 → 升级到 baseline（所有 SSOT 修订必须有 self-test）
3. CONVERGED 覆盖链声明 → 模板化（治理档特有）
4. task_queue deferred_to_round 字段 → SKILL v1.3 候选
5. v3.02 数据迁移策略 → S7/S8 阶段推广

---

## 8. 引用

| 内容 | 路径 |
|---|---|
| 本 Goal CONVERGED（R14-R18 完整）| `governance/design_iter/plans/v17/CONVERGED.md` |
| 本 Goal 决策档（五轮）| `governance/design_iter/current/round{14,15,16,17,18}_q_decision_table.md` |
| 本 Goal 五轮 audit + review | `.goal-log-db/active/32a8ff45-.../{audit,review}_{14,15,16,17,18}.md` |
| 本 Goal 快照 | `.goal-log-db/active/32a8ff45-.../snapshot.json` |
| 守卫 SSOT | `governance/design_iter/current/out_of_scope.md` |
| Open Questions 主档 | `governance/open_questions.md` |
| Open Questions 归档 | `governance/open_questions_archive_v17.md` |
| 上游 Goal CONVERGED（GL-002 · R11~13）| 已被本 Goal CONVERGED 覆盖（保留引用链）|
| 全局 DNA | `AGENTS.md` + `.cursor/rules/DNA_3Q_CHECK.mdc` |
| Goal-loop Skill | `.cursor/skills/goal-loop/SKILL.md` |
