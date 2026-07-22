# v14 三级根因分类体系 — 执行档

> **状态**：v14 P1 落地（2026-07-14）
> **位置**：`governance/design_iter/current/rca_three_level_classification.md`
> **关联**：v14 PLAN.md §4.6、STAGE_S7_REVIEW.mdc、STAGE_S8_SELF_ITERATION.mdc
> **执行者**：S7 审查报告 + S8 迭代报告共同使用本体系

---

## 1. 三级根因体系（统一分类标准）

> 适用场景：S7 recommendations 每条缺陷 / S8 iteration 每条根因追溯
> **一级阶段** × **二级类型** × **三级条款** = 完整根因定位

### 1.1 一级：根因来源阶段

| 一级代码 | 含义 | 说明 |
|---|---|---|
| `S4` | 流程图导出 | 风险点清单遗漏 / 异常树不完整 / Epic 归属错误 |
| `S5` | 测试点生成 | TP 遗漏 / module 误标 / s4_reference 缺失 / 规则引用缺失 |
| `S6` | 测试用例生成 | TC 步骤质量差 / 字段缺失 / 优先级错误 / 方法学标签不足 |
| `S2` | 需求拆解 | OBJ 拆分粗糙 / Epic 模块归属错误 / FP 遗漏 |
| `S1` | 需求评审 | 角色定义不清 / 功能描述模糊 / 验收标准缺失 |

### 1.2 二级：缺陷类型

| 二级代码 | 含义 | 典型症状（S7 recommendations） |
|---|---|---|
| `OMISSION` | 遗漏 | 该覆盖的风险点/TP/TC 没有生成 |
| `BOUNDARY_ERR` | 边界错误 | module 归属与 O_boundary.md 冲突（如 HINT 标成 UI） |
| `QUALITY_LOW` | 质量不足 | 步骤不够原子 / 预期不清晰 / 数值模糊 |
| `FIELD_MISSING` | 字段缺失 | MUST 字段未填写 / s4_reference 缺失 |
| `LINKAGE_BROKEN` | 链路断裂 | S4→S5 引用断 / S5→S6 引用断 / FP 链路断 |
| `RULE_VIOLATION` | 规则违反 | applies_rule 未填 / is_assumed 未标注 |
| `ID_NONCOMPLIANT` | ID 不合规 | TC ID 不是 `{Module}-TC-{NNN}` 格式 |

### 1.3 三级：条款映射（关联 PRODUCT_MANUAL 章节号）

> 每条根因追溯到**具体规则章节**，便于 Agent 直接定位修改位置。

| 三级条款代码 | 指向文件 | 指向章节 | 条款内容摘要 |
|---|---|---|---|
| `S5.§1.4` | `STAGE_S5_TEST_POINTS.mdc` | §1.4 必读材料 | 执行前必须读取模块子模板和边界文件 |
| `S5.§2.2` | `STAGE_S5_TEST_POINTS.mdc` | §2.2 OBJ 拆分规则 | OBJ → TP 的拆分要求和精度标准 |
| `S5.§3` | `STAGE_S5_TEST_POINTS.mdc` | §3 模块决策树 | 8 模块判定的两步法 |
| `S6.§1.4` | `STAGE_S6_TEST_CASES.mdc` | §1.4 必读材料 | 执行前必须读取 S5 TP 和模块子模板 |
| `S6.§2` | `STAGE_S6_TEST_CASES.mdc` | §2 核心原则 | coverage-first + v3.3 方法学要求 |
| `S7.§1.5` | `STAGE_S7_REVIEW.mdc` | §1.5 决策 push 块 | 双审查员分工（脚本/语义） |
| `S7.§2` | `STAGE_S7_REVIEW.mdc` | §2 质量门禁 | 无硬阈值，按业务实际判断 |
| `S8.§2` | `STAGE_S8_SELF_ITERATION.mdc` | §2 核心任务 | 4 步根因追溯流程 |
| `SKILL.S5.§1.6.5` | `aidocx-s5-test-points/SKILL.md` | §1.6.5 字段分级 | MUST/SHOULD/COULD 分级强制 |
| `SKILL.S6.§1.6` | `aidocx-s6-test-cases/SKILL.md` | §1.6 字段分级 | TC 必填字段 10 列 |
| `SKILL.S7.§3` | `aidocx-s7-review/SKILL.md` | §3 审查员分工 | 审查员 A/B 具体分工 |
| `SKILL.S8.§2` | `aidocx-s8-self-iteration/SKILL.md` | §2 分析流程 | 4 步根因追溯流程 |
| `MODULES.§4.{X}` | `.cursor/MODULES.md` | §4.11 各模块边界 | 8 模块 O_boundary.md 具体边界规则 |
| `DESIGN.§2.3` | `DESIGN_AND_EXECUTION_STANDARDS.mdc` | §2.3 质量门禁 | 全阶段质量门禁阈值定义 |

---

## 2. S7 review_report.json 字段扩展（v14 新增）

> **扩展位置**：`aidocx-s7-review/SKILL.md` §1.4 执行步骤 3 表格
> **变更内容**：recommendations 每条增加 `rca` 字段

### 2.1 扩展后 recommendations 字段结构

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `recommendations[].id` | string | MUST | 建议序号 `REC-{NNN}` |
| `recommendations[].severity` | string | MUST | `MUST_FIX` / `SHOULD_FIX` / `COULD_FIX` |
| `recommendations[].description` | string | MUST | 具体问题描述 |
| `recommendations[].affected_cases` | string[] | SHOULD | 涉及的 case_id 列表 |
| `recommendations[].affected_test_points` | string[] | SHOULD | 涉及的 test_point_id 列表 |
| `recommendations[].rca` | object | **SHOULD**（v14 新增） | 三级根因定位 |
| `recommendations[].rca.stage` | string | MUST | 一级：`S4` / `S5` / `S6` / `S2` / `S1` |
| `recommendations[].rca.type` | string | MUST | 二级：`OMISSION` / `BOUNDARY_ERR` / `QUALITY_LOW` / `FIELD_MISSING` / `LINKAGE_BROKEN` / `RULE_VIOLATION` / `ID_NONCOMPLIANT` |
| `recommendations[].rca.clause` | string | MUST | 三级：条款代码（如 `S5.§3` / `SKILL.S6.§1.6`） |
| `recommendations[].rca.explanation` | string | SHOULD | 根因简述（≤ 50 字） |

### 2.2 扩展位置（锚定文本）

> 插入位置：`aidocx-s7-review/SKILL.md` 第 96-106 行之间
> 锚定 old_string：
> ```
> ### 步骤 3：生成 review_report.json（5 个顶层字段）
> 
> || 字段 | 来源 |
> ||------|------|
> || `reviewer_a` | 来自 `snap.structure`（事实统计） |
> || `reviewer_b` | 来自 `snap.s5_structure`（覆盖率事实） |
> || `llm_review_a_semantic` | LLM 填写（语义审查结论） |
> || `llm_review_b_semantic` | LLM 填写（覆盖率语义评判） |
> || `recommendations` | LLM 填写（必修/应改/可改） |
> ```

---

## 3. S8 iteration_report.json 字段扩展（v14 新增）

> **扩展位置**：`aidocx-s8-self-iteration/SKILL.md` 第 142-150 行之间
> **变更内容**：每条 iteration item 增加 `rca` 字段

### 3.1 扩展后 iteration item 字段结构

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `iteration_items[].id` | string | MUST | 迭代项序号 `ITER-{NNN}` |
| `iteration_items[].problem` | string | MUST | 具体问题描述（S7 报告中的具体缺口） |
| `iteration_items[].evidence` | string | MUST | 数据支撑（S7 报告中的数值） |
| `iteration_items[].root_cause` | string | MUST | 根因定位（哪个阶段、哪个环节断裂） |
| `iteration_items[].fix` | string | MUST | 具体修复动作 |
| `iteration_items[].affected_stage` | string[] | MUST | 需要修改的阶段（`["S5", "SKILL.S5"]` 等） |
| `iteration_items[].expected_impact` | string | SHOULD | 预期改善效果 |
| `iteration_items[].rca` | object | **MUST**（v14 新增） | 三级根因定位 |
| `iteration_items[].rca.stage` | string | MUST | 一级 |
| `iteration_items[].rca.type` | string | MUST | 二级 |
| `iteration_items[].rca.clause` | string | MUST | 三级：条款代码 |
| `iteration_items[].rca.explanation` | string | SHOULD | 根因简述 |
| `iteration_items[].archive_target` | string | SHOULD | 归档目标（`knowledge/project_local/.review_queue/`） |

---

## 4. 执行约束（Agent 行为规则）

### 4.1 S7 审查员填写 RCA 规则

1. 每条 `recommendations` **尽量填写** `rca` 字段（SHOULD）
2. 如果缺陷无法定位到具体阶段 → `rca.stage = "UNKNOWN"` + `rca.explanation` 说明原因
3. 如果缺陷跨越多个阶段 → 填写**主要根因阶段**，次要阶段写入 `affected_stage` 数组
4. clause 代码必须从 §1.3 表格中选择，禁止自创条款代码

### 4.2 S8 根因追溯填写 RCA 规则

1. 每条 `iteration_items` **必须填写** `rca` 字段（MUST）
2. `rca.stage` 必须与根因链路图中的"根本原因"层对应
3. `affected_stage` 数组必须包含 `rca.stage` 及所有受影响的阶段
4. clause 代码必须从 §1.3 表格中选择，禁止自创

### 4.3 禁止出现的行为

- ❌ RCA stage 填 `S1`/`S2` 时未在 S7/S8 的 upstream 材料中验证该阶段存在
- ❌ RCA type 填 `BOUNDARY_ERR` 但未引用对应的 O_boundary.md 文件
- ❌ RCA clause 填自定义代码而非 §1.3 表格中的标准化代码
- ❌ S8 跳过 S7 review_report 直接生成 iteration_items

---

## 5. 映射表（条款代码 → 文件路径）

| 条款代码 | 完整文件路径 | 说明 |
|---|---|---|
| `S5.§1.4` | `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` §1.4 |
| `S5.§2.2` | `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` §2.2 |
| `S5.§3` | `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` §3 |
| `S6.§1.4` | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §1.4 |
| `S6.§2` | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §2 |
| `S7.§1.5` | `.cursor/rules/STAGE_S7_REVIEW.mdc` §1.5 |
| `S7.§2` | `.cursor/rules/STAGE_S7_REVIEW.mdc` §2 |
| `S8.§2` | `.cursor/rules/STAGE_S8_SELF_ITERATION.mdc` §2 |
| `SKILL.S5.§1.6.5` | `.cursor/skills/aidocx-s5-test-points/SKILL.md` §1.6.5 |
| `SKILL.S6.§1.6` | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §1.6 |
| `SKILL.S7.§3` | `.cursor/skills/aidocx-s7-review/SKILL.md` §3 |
| `SKILL.S8.§2` | `.cursor/skills/aidocx-s8-self-iteration/SKILL.md` §2 |
| `MODULES.§4.{X}` | `.cursor/MODULES.md` §4.11.{X} |
| `DESIGN.§2.3` | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.3 |

---

## 6. 实施步骤

| 步骤 | 动作 | 涉及文件 |
|---|---|---|
| 6.1 | 扩展 S7 SKILL.md recommendations 字段表（§2.1） | `aidocx-s7-review/SKILL.md` |
| 6.2 | 扩展 S8 SKILL.md iteration_items 字段表（§3.1） | `aidocx-s8-self-iteration/SKILL.md` |
| 6.3 | 更新 S7 STAGE_S7_REVIEW.mdc 质量门禁节（新增 RCA 建议） | `STAGE_S7_REVIEW.mdc` |
| 6.4 | 更新 S8 STAGE_S8_SELF_ITERATION.mdc 核心任务节 | `STAGE_S8_SELF_ITERATION.mdc` |
| 6.5 | 升级 auto_reviewer.py 支持 RCA 统计（如需要） | `ai_workflow/auto_reviewer.py` |
| 6.6 | 升级 self_iteration.py 支持 RCA 归档 | `ai_workflow/self_iteration.py` |

---

## 落档协议执行记录

- 创建占位文件 + content 展开：`governance/design_iter/current/rca_three_level_classification.md`
- 执行时间：2026-07-14
- 涉及文件：
  - `aidocx-s7-review/SKILL.md`（recommendations 字段扩展）
  - `aidocx-s8-self-iteration/SKILL.md`（iteration_items 字段扩展）
  - `STAGE_S7_REVIEW.mdc`（质量门禁节）
  - `STAGE_S8_SELF_ITERATION.mdc`（核心任务节）
