# v14 §5 第一阶段启动决策表（2026-07-16）

## 触发

用户原话：
> 切到 v14 → 启动 v14 §5 第一阶段

## 范围（来自外部方案 §5）

**第一阶段 4 项必做**（1-2 周）：

| # | 优化项 | 涉及文件（来自外部方案） |
|---|---|---|
| 1 | 模块边界决策树 | S2/S5 SKILL.md |
| 2 | 引用字段分级强制 | S5/S6 校验脚本 + 门禁 |
| 3 | 单阶段执行卡 | 各阶段 SKILL.md |
| 4 | 三级根因分类 | S7 审查模板 + S8 迭代模板 |

## 现状（先验 §9.4：需在动手前 Read）

| 文件 | 状态 | 备注 |
|---|---|---|
| `.cursor/skills/aidocx-s2-breakdown/SKILL.md` | ❌ 未 Read | 待 Read |
| `.cursor/skills/aidocx-s5-test-points/SKILL.md` | ❌ 未 Read | 待 Read |
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | ❌ 未 Read | 待 Read |
| `.cursor/skills/aidocx-s7-review/SKILL.md` | ❌ 未 Read | 待 Read |
| `.cursor/skills/aidocx-s8-self-iteration/SKILL.md` | ❌ 未 Read | 待 Read |
| 5 个阶段的 STAGE_S*.mdc | ❌ 未 Read | 待 Read（执行卡的源文件）|
| 边界决策树的"5 组边界"原文 | ❌ 未 Read | 在 MODULES.md §4.x |
| 引用字段分级（MUST/SHOULD/COULD）的字段表 | ❌ 未 Read | 在 .cursor/MODULES.md |

## 候选方案（请拍 1）

### 候选 A（推荐）— 分 4 批，按"必做项 1 → 2 → 3 → 4"顺序，每批 ≤ 3 文件 + 必须先 Read 源文件 + 写完跑自测

- 批 1：模块边界决策树（涉及 S2/S5 SKILL.md × 2 + MODULES.md §4.x 决策树原文写入 ≤ 3 文件）
- 批 2：引用字段分级强制（S5/S6 SKILL.md × 2 + 校验脚本 ≤ 3 文件）
- 批 3：单阶段执行卡（每阶段 ≤ 6 项嵌入 SKILL.md <execution_card> 块；9 个阶段 SKILL.md → **超红线**——分 2 子批，每子批 ≤ 5 阶段）
- 批 4：三级根因分类（S7/S8 SKILL.md × 2 + PRODUCT_MANUAL §3.x 章节映射 ≤ 3 文件）
- **总时间**：跨多轮响应，每批都按 §3.7 SOP 强制验证
- **优点**：每批可独立审查、不超红线、决策密度低
- **缺点**：要 5-6 轮响应才能完整

### 候选 B（冒险）— 一轮全做齐 4 项 20+ 文件

- 1 轮响应改 20+ 文件
- **违反 §9.1 红线**（> 3 文件）
- **违反 §3.7 SOP**（> 400 行文件必须 Read 全文才能改）
- **风险**：决策密度失控、漏改、不可审查

### 候选 C（最慢）— 先 Read 所有源文件，生成完整执行方案，再分批改

- 1 轮响应：Read 全部相关源文件 + 生成 `governance/design_iter/plans/v14/phase1_execution_plan.md`（详细方案档）
- 后续轮：按方案档分批改
- **优点**：方案档作为落档源（§9.5 合规）
- **缺点**：先 Read 10+ 文件 + 写方案档 = 1 轮响应时间已经很长

### 候选 D（折中）— C + 每改一项落档

- C 的方案档基础上：每改一项往方案档追加"## 改动记录"
- 类似 §9.5 的"落档协议执行记录"

## 推荐

**候选 A**——分 4 批，按 §9.1 红线每批 ≤ 3 文件，先 Read 源文件再动手。

**前置：第 1 批之前必须先 Read**（先验 §9.4）：

| Read 目标 | 目的 |
|---|---|
| `.cursor/MODULES.md` §4.x 边界规则 | 决策树原文要嵌进 S2/S5 prompt |
| `.cursor/skills/aidocx-s2-breakdown/SKILL.md` | 改前必读 |
| `.cursor/skills/aidocx-s5-test-points/SKILL.md` | 改前必读 |
| `.cursor/rules/STAGE_S2_BREAKDOWN.mdc` | 执行卡源文件 |
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` | 执行卡源文件 |

## 影响范围（候选 A 总览）

| 批 | 文件改动数 | 涉及文件 |
|---|---|---|
| 批 1（决策树） | 2-3 | S2/S5 SKILL.md + 决策树原文 |
| 批 2（引用分级） | 2-3 | S5/S6 SKILL.md + 校验脚本 |
| 批 3a（执行卡上） | 5 | S1-S5 SKILL.md |
| 批 3b（执行卡下） | 4-5 | S6-S8 + S1.5/S2.5 SKILL.md |
| 批 4（根因三级） | 2-3 | S7/S8 SKILL.md + PRODUCT_MANUAL 映射 |

## 等待拍板

候选 A 还是 C？或者你想先看批 1 的执行方案？

## 落档协议执行记录

（本文件即落档——§9.5 合规）