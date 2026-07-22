# Rule / SKILL.md 一致性审查报告

> 审查日期：2026-06-15
> 审查范围：`.cursor/rules/STAGE_S*.mdc` ↔ `.cursor/skills/aidocx-s*-*/SKILL.md`（共 10 对，20 个文件）
> 审查原则：设计哲学「LLM 负责推理 + 脚本只做格式整理」，8 模块定义见 `.cursor/MODULES.md`

---

## 总览

| 指标 | 值 |
|------|-----|
| 整体一致性评分 | **5.5 / 10** |
| P0 级冲突（必须修） | **7** |
| P1 级冲突（建议修） | **12** |
| P2 级问题（小修小补） | **5** |
| 硬指标残留总数 | **4 个硬指标块**（S5 数量约束 / S6 派生规则 / S7 硬判决 / S8 硬判决） |

### 核心设计哲学违反统计

| 违反项 | 涉及阶段 | 严重度 |
|--------|---------|--------|
| 硬指标残留（≥N / =N% 数量约束）| S5（.mdc）、S6（.mdc）、S7（.mdc）、S8（.mdc）| **P0** |
| PASS/FAIL 硬判决块未删除 | S7（.mdc §"质量门禁"）、S8（.mdc）| **P0** |
| §1.4 节缺失 | S2.5（.mdc 无）、S3（.mdc 无）| **P0** |
| 跨阶段引用字段名不一致 | S5→S6（S4 ID 格式）、S6→S7（s4_reference）| **P1** |

---

## 按阶段逐项审查

---

### S1 (STAGE_S1_REVIEW.mdc ↔ aidocx-s1-review/SKILL.md)

#### 1. 硬指标残留

**✓ 无（符合 v2.0 设计哲学）**

S1 的评分是 `≥ 7.0 PASS`，但这是**判决门槛**（而非测试点数量约束），属于流水线流程判决，不属于"硬性数量指标"。两文件均无"≥N 个"类型的硬性产出数量约束。

#### 2. 核心定义冲突

**✓ 无重大冲突**

两文件对以下核心概念定义一致：
- 5 维度评审维度与权重
- 判决规则（≥7.0 PASS / 4.0-6.9 NEEDS_REVISION / <4.0 REJECT）
- 强付费项（PURCHASE_STRONG）3 段质量闭环
- 8 模块标签体系（CONFIG/UI/BIZ/HINT/LINK/SPECIAL/LOG/AUX）

#### 3. 章节结构错位

**⚠️ 小偏差**

| 节 | .mdc 位置 | SKILL.md 位置 |
|----|-----------|-------------|
| 物料门禁 | §物料门禁（第 23 行）| §阶段入口（第 26 行）|
| 审查产物 | §审查产物（第 61 行）| §审查产物 1/2/3（第 90-229 行）|
| 5 维度评审 | §核心任务（第 130 行）| §5维度评审（第 232 行）|
| §1.4 LLM 必读材料 | **SKILL.md 独有**（第 40 行），.mdc 无对应节 | ✅ |

> **注意**：SKILL.md 第 329 行有一条 ⚠️ 注释：`自动化引擎：ai_workflow/requirement_reviewer_auto.py（⚠️ 仍按"4 项内容门禁"实现，待对齐本次重构）`——说明自动化脚本尚未对齐最新规范，**需要更新 `requirement_reviewer_auto.py`**（P1 建议）。

#### 4. SSoT 引用合规

**✓ 合规**

两文件均引用 `.cursor/MODULES.md` 作为 8 模块的 SSoT，未自创模块表。

#### 5. 决策 push 块状态

**✓ 均有体现**

SKILL.md 引用了 `review_report.md` 末尾"补充材料建议"小节（第 54 行），与 .mdc §前置材料建议（第 46 行）一致。

#### 6. 跨阶段引用

**✓ 合规**

S1 → S1.5 物料链（5 份）定义一致。

#### 评分

**8 / 10**

---

### S1.5 (STAGE_S1.5 Clarification.mdc ↔ aidocx-s1-5-clarification/SKILL.md)

#### 1. 硬指标残留

**✓ 无**

两文件均无硬性数量指标。

#### 2. 核心定义冲突

**✓ 无**

exit_permission.json 的字段结构、quality_level（HIGH/MEDIUM/LOW/BLOCKED）定义完全一致。

#### 3. 章节结构错位

**⚠️ 轻微偏差**

| 节 | .mdc | SKILL.md |
|----|------|---------|
| §1.4 LLM 必读材料 | **无**（.mdc 从 §核心职责开始，无 §1.4）| ✅ 第 39 行有 §1.4 |
| 质量评价标准 | §轻量跑通 vs 完整跑通（第 76 行）| §质量评价标准（第 146 行）|

#### 4. SSoT 引用合规

**✓ 合规**

#### 5. 决策 push 块状态

**✓ 一致**

#### 6. 跨阶段引用

**✓ 一致**

#### 评分

**8.5 / 10**

---

### S2 (STAGE_S2_BREAKDOWN.mdc ↔ aidocx-s2-breakdown/SKILL.md)

#### 1. 硬指标残留

**✓ 无**

两文件均彻底移除了"Epic 1-4 周"、"Story 1-3 人天"、"Object 3-8 个"、"FP 3-8 个"等旧版硬性数值范围，改为"业务自然划分"。设计哲学完全对齐。

#### 2. 核心定义冲突

**⚠️ §1.5.6 OBJ 字段名不统一**

| 字段 | .mdc | SKILL.md |
|------|------|---------|
| ID 字段 | `id`（第 159 行）| `id`（第 148 行）| ✅ |
| 名称字段 | `title`（第 159 行）| `title`（第 149 行）| ✅ |
| OBJ ID 字段 | SKILL.md §1.5.5 列 `obj_id`（第 527 行）| .mdc 统称"Object ID"，无单独字段名规定 | **轻微偏差** |

SKILL.md §1.5.5（第 527 行）提到 `obj_id` 字段名，但 .mdc 中 Object JSON 示例（第 409 行）使用 `id` 字段。**建议统一为 `obj_id`**。

#### 3. 章节结构错位

**⚠️ SKILL.md 章节更丰富**

SKILL.md 独有而 .mdc 未单独设立：
- **§1.4 LLM 必读材料**（第 56 行）：SKILL.md 有，.mdc 无独立 §1.4 节
- **§1.5 决策 push 块**（第 475 行）：SKILL.md 有 6 个 push 块，.mdc 在各层叙述中零散提及，无独立 §1.5

#### 4. SSoT 引用合规

**✓ 合规**

两文件均引用 MODULES.md 作为 8 模块 SSoT。

#### 5. 决策 push 块状态

**✓ SKILL.md 有，.mdc 分散体现**

SKILL.md §1.5 有 6 个 push 块（§1.5.1~§1.5.6），.mdc 在各层叙述中零散提到 push 内容但未编号。**建议在 .mdc 中增加 §1.5 决策 push 块节，与 SKILL.md 对齐**。

#### 6. 跨阶段引用

**✓ 合规**

#### 评分

**7.5 / 10**

---

### S2.5 (STAGE_S2_5_ITERATION.mdc ↔ aidocx-s2-5-iteration/SKILL.md)

#### 1. 硬指标残留

**✓ 无**

两文件均无硬性数量指标。

#### 2. 核心定义冲突

**⚠️ Step 0 配置收集是否为强制前置（冲突）**

| 文件 | 规定 | 位置 |
|------|------|------|
| .mdc | 7 步规划，**无 Step 0** | §核心任务 |
| SKILL.md | **强制 Step 0** — "配置不全不得执行" | §Step 0 — 项目配置收集 |

**冲突描述**：SKILL.md §Step 0（第 23 行）规定「执行 S2.5 时，若检测到项目配置不完整，**必须主动询问用户**，不得自行假设默认值后跳过」，且"配置保存"产出一个 `project_config.json`。但 .mdc 的 §输入审查（门禁前置条件）（第 56 行）**完全没有提到 project_config.json 作为门禁条件**。

#### 3. 章节结构错位

**⚠️ SKILL.md 有 Step 0，.mdc 无**

- SKILL.md §Step 0（第 23 行）：强制配置收集
- SKILL.md §1.4 LLM 必读材料（第 72 行）：有独立 §1.4
- **.mdc 完全无 §1.4 节，也无 Step 0**

#### 4. SSoT 引用合规

**✓ 合规**

#### 5. 决策 push 块状态

**✓ 两者均无**

#### 6. 跨阶段引用

**✓ 一致**

#### 评分

**6 / 10**

#### P0 问题

> **P0-1：S2.5 .mdc 缺失 Step 0 配置收集强制前置**
> - **现象**：SKILL.md §Step 0 规定配置收集是强制前置（"配置不全不得执行"），但 .mdc 无此节也无此门禁
> - **后果**：.mdc 作为规则真理源，LLM 按 .mdc 执行会跳过配置收集，导致 S2.5 规划依赖未确认的参数
> - **修复**：在 .mdc 中增加 Step 0 + `project_config.json` 门禁条件

#### P1 问题

> **P1-1：.mdc 缺失 §1.4 LLM 必读材料**
> - SKILL.md §1.4 列出了 3 项必读材料（MODULES.md / backlog / requirement_objects.json），.mdc 无对应节

---

### S3 (STAGE_S3_PROTOTYPE.mdc ↔ aidocx-s3-prototype/SKILL.md)

#### 1. 硬指标残留

**✓ 无**

#### 2. 核心定义冲突

**✓ 无**

#### 3. 章节结构错位

**⚠️ SKILL.md 有 §1.4，.mdc 无**

- SKILL.md §1.4 LLM 必读材料（第 33 行）：有独立节，列出 2 项必读
- .mdc：完全无 §1.4 节

#### 4. SSoT 引用合规

**✓ 合规**

#### 5. 决策 push 块状态

**✓ 两者均无**

#### 6. 跨阶段引用

**✓ 一致**

#### 评分

**7 / 10**

#### P1 问题

> **P1-2：S3 .mdc 缺失 §1.4 LLM 必读材料**
> - .mdc 作为规则真理源，应与 SKILL.md 保持一致的章节结构

---

### S4 (STAGE_S4_FLOWCHART.mdc ↔ aidocx-s4-flowchart/SKILL.md)

#### 1. 硬指标残留

**⚠️ 有（警告级，非阻断）**

| 检查项 | 阈值 | 位置 | 性质 |
|--------|------|------|------|
| 风险点数量 | ≥ 3 | .mdc §输入审查 + SKILL.md §输入审查 | 软约束（警告，不阻断） |
| 异常树叶子节点 | 每个 Epic ≥ 3 个 | .mdc §输入审查 + SKILL.md §输入审查 | 软约束（警告，不阻断） |
| 风险点 ↔ 异常树叶子交叉引用 | ≥ 50% | .mdc §质量门禁 + SKILL.md §质量门禁 | 软约束（警告，不阻断） |

这些"≥3" / "≥50%"指标在两文件中**完全一致**，且都标注为"警告"而非阻断。但与 S5/S7/S8 的"无硬指标"哲学存在不一致——**建议 S4 也彻底去掉"≥3"类数字约束，改用决策 push**。

#### 2. 核心定义冲突

**✓ 无**

4 类可机检 ID 格式（R-NNN / R-{EpicID}-NN / S4-{EpicID}-X.Y.Z / S4-{EpicID}-FNN）、7 类风险点典型清单完全一致。

#### 3. 章节结构错位

**✓ 结构高度一致**

两文件章节对应良好。SKILL.md 独有 §1.5 决策 push 块（§1.5.1~§1.5.3），.mdc 无独立 §1.5。

#### 4. SSoT 引用合规

**✓ 合规**

两文件均引用 MODULES.md §1 / §3.5 / §4.11.2 作为模块边界 SSoT。

#### 5. 决策 push 块状态

**SKILL.md 有（§1.5.1~§1.5.3），.mdc 分散体现**

SKILL.md §1.5.1（Epic 命名反例）、§1.5.2（异常树叶子归属判定）、§1.5.3（风险点 s4_reference 格式）在 .mdc 中无独立编号节，但内容在 §与其他阶段的衔接（第 232 行）等处有体现。

#### 6. 跨阶段引用

**⚠️ S4 → S5 引用格式需对齐**

S4 SKILL.md §核心任务（第 81 行）推荐 S5 TP 的 `s4_reference` 使用 `R-{EpicID}-NN` 格式（与 `epic.id` 对齐），但 S5 SKILL.md §1.5.5 字段约束（第 203 行）中 `s4_reference` 字段说明为"R-NNN 或 F-XX 或 S4-{EpicID}-X.Y.Z"，未明确推荐 `R-{EpicID}-NN`。**建议 S5 引用规范中明确推荐 `R-{EpicID}-NN` 格式**。

#### 评分

**7.5 / 10**

---

### S5 (STAGE_S5_TEST_POINTS.mdc ↔ aidocx-s5-test-points/SKILL.md)

#### 1. 硬指标残留

**✗ 有（P0 级）**

**.mdc §核心任务（第 39-44 行）残留硬性数量指标**：

| 类型 | .mdc 硬指标 | SKILL.md 态度 |
|------|------------|--------------|
| POSITIVE | ≥ 2 | SKILL.md §1.5.1："数量原则（去硬数字）"，已废除"至少 3 module" |
| BOUNDARY | ≥ 2 | SKILL.md §1.5.1：已废除硬指标 |
| NEGATIVE | ≥ 1 | 同上 |
| EXCEPTION | ≥ 1 | 同上 |

**冲突本质**：.mdc 是"设计哲学违反"——v2.0 的核心原则就是"LLM 负责推理，脚本只做格式整理"，.mdc 中的"≥2/≥1"数量约束正是 v1.x 旧版硬指标的代表。SKILL.md 已正确移除，.mdc 未同步。

#### 2. 核心定义冲突

**✗ 有（P0 级）**

**S5 TP 字段名在两文件中不一致**：

| 字段 | .mdc JSON 示例（第 81 行）| SKILL.md §1.5.5 强约束（第 198 行）| 状态 |
|------|-------------------------|----------------------------------|------|
| ID | `id` | `tp_id` | **冲突** |
| 类型 | `type` | `test_point_type` | **冲突** |

.mdc 的 JSON 示例（第 81 行）使用 `"id": "UI-001-001-TP-001"` 和 `"type": "POSITIVE"`；SKILL.md §1.5.5 强约束（第 198 行）规定字段名为 `tp_id` 和 `test_point_type`。**两文件对 TP JSON 字段名定义不一致**。

#### 3. 章节结构错位

**✓ SKILL.md 章节更完整**

SKILL.md 有完整的 §1.5 决策 push 块（§1.5.1~§1.5.6），.mdc 无独立 §1.5 节。

#### 4. SSoT 引用合规

**✓ 合规**

两文件均引用 MODULES.md 作为 8 模块 SSoT。SKILL.md §1.1（第 46 行）正确引用了 MODULES.md。

#### 5. 决策 push 块状态

**SKILL.md 有（§1.5.1~§1.5.6），.mdc 无**

#### 6. 跨阶段引用

**⚠️ S5 TP JSON → S6 TC 的字段名传递问题**

S5 TP 的字段名（`id` vs `tp_id`、`type` vs `test_point_type`）会传递到 S6 SKILL.md 读取 S5 test_points.json 时的处理逻辑。如果 .mdc 执行者用 `id`/`type`，SKILL.md 用 `tp_id`/`test_point_type`，则 S6 读取 S5 JSON 时字段匹配会出现问题。

#### 评分

**4 / 10**

#### P0 问题

> **P0-2：S5 .mdc 残留硬性数量指标**
> - 位置：.mdc §核心任务（第 39-44 行）
> - 内容：POSITIVE ≥ 2、BOUNDARY ≥ 2、NEGATIVE ≥ 1、EXCEPTION ≥ 1
> - 冲突：与 SKILL.md §1.5.1 "数量原则（去硬数字）"直接矛盾
> - 修复：删除 .mdc 中的"≥2/≥1"数量约束，改用"LLM 根据业务自然分布决定"

> **P0-3：S5 .mdc 与 SKILL.md TP JSON 字段名不一致**
> - .mdc JSON 示例用 `id` + `type`
> - SKILL.md §1.5.5 强约束用 `tp_id` + `test_point_type`
> - 修复：统一为 `tp_id` + `test_point_type`（SKILL.md 版本为正确版本）

---

### S6 (STAGE_S6_TEST_CASES.mdc ↔ aidocx-s6-test-cases/SKILL.md)

#### 1. 硬指标残留

**✗ 有（P0 级）**

**.mdc §核心原则（第 29 行）明确说明了 v2.0 重构精神**：
> "脚本不推导 TC 数量 / 不强制 1:N / 不分配 test_method"

但 .mdc §"18 种测试方法派生规则"（第 59 行）**仍然列出了硬性派生系数**：

| TP 类型 | 派生系数 | 性质 |
|---------|---------|------|
| POSITIVE | 3-5 | 硬性范围 |
| BOUNDARY | 4-7 | 硬性范围 |
| NEGATIVE | 5-10 | 硬性范围 |
| EXCEPTION | 4-8 | 硬性范围 |

同样，.mdc §"模块风险加权"（第 68 行）也列出了硬性加权值（`BIZ ×1.5` 等）。

**SKILL.md §字段语义（第 44 行）已正确改为"LLM 自由创作，不是模板填充"**，两文件设计哲学不一致。

#### 2. 核心定义冲突

**✗ 有（P0 级）**

**S6 TC JSON 字段名在两文件中不一致**：

| 字段 | .mdc JSON 示例（第 138 行）| SKILL.md JSON 示例（第 86 行）| 状态 |
|------|--------------------------|------------------------------|------|
| ID | `"用例ID"` | `"case_id"` | **冲突** |
| 模块 | `"模块"` | `"模块"`（双语均可）| ✅ 一致 |
| 优先级 | `"优先级"` | `"优先级"` | ✅ 一致 |

SKILL.md 使用 `"case_id"`（英文蛇形），.mdc 使用 `"用例ID"`（中文）。两文件对 JSON key 名的定义不同。

#### 3. 章节结构错位

**✓ 结构基本一致**

SKILL.md 有 §1.4 LLM 必读材料（5 项），.mdc 无独立 §1.4 节。

#### 4. SSoT 引用合规

**✓ 合规**

#### 5. 决策 push 块状态

**SKILL.md 有（无独立编号），.mdc 无**

#### 6. 跨阶段引用

**⚠️ S6 用例描述字段命名需与 S7 审查对齐**

S6 TC 的"用例描述"字段（.mdc 用"用例ID"、SKILL.md 用"case_id"）将传递到 S7 审查。如果命名不统一，S7 审查脚本需要做额外的字段映射。

#### 评分

**4 / 10**

#### P0 问题

> **P0-4：S6 .mdc §"18 种测试方法派生规则"残留硬性派生系数**
> - 位置：.mdc §核心原则下 §18 种测试方法派生规则（第 59 行）
> - 内容：POSITIVE 3-5 / BOUNDARY 4-7 / NEGATIVE 5-10 / EXCEPTION 4-8
> - 冲突：与 .mdc 自身 §核心原则（第 29 行）的"不强制 1:N / 不强制 18 种方法"精神矛盾
> - 修复：删除派生系数表，改用"LLM 根据 TP 类型和业务复杂度自由决定"

> **P0-5：S6 .mdc §"模块风险加权"残留硬性加权值**
> - 位置：.mdc §模块风险加权（第 68 行）
> - 冲突：与 .mdc 自身"LLM 推理 + 脚本整理"原则矛盾
> - 修复：删除加权表，改为"LLM 根据业务风险自由决定优先级"

> **P0-6：S6 .mdc 与 SKILL.md TC JSON 字段名不一致**
> - .mdc JSON key：`用例ID`（中文）
> - SKILL.md JSON key：`case_id`（英文蛇形）
> - 修复：统一为 `case_id`（SKILL.md 版本为更规范的版本，且与 test_case_formatter.py 的实现一致）

---

### S7 (STAGE_S7_REVIEW.mdc ↔ aidocx-s7-review/SKILL.md)

#### 1. 硬指标残留

**✗ 有（P0 级 — 最严重冲突）**

**.mdc §质量门禁（第 50 行）残留 PASS/FAIL 硬判决**：

```markdown
## 质量门禁
| 条件 | 判决 |
|------|------|
| 覆盖率 ≥ 85% 且 结构完整性 ≥ 90% | PASS |
| 否则 | FAIL（需修改后重审）|
```

SKILL.md §3（质量门禁 v2.0）（第 93 行）**明确废弃了硬判决**：

```markdown
> S7 阶段不设硬指标（不强制"覆盖率=100% = PASS"）——真实业务有取舍，让 LLM 审查员按业务实际写建议。
> v1.0 旧规则已废弃
```

**这是全项目最严重的冲突**：SKILL.md v2.0 明确标注"v1.0 旧规则已废弃"，但 .mdc 仍然保留了旧版硬判决。

**.mdc §审查员 B 覆盖率（第 43 行）残留硬性阈值**：

```markdown
| 指标 | 阈值 | 说明 |
|------|------|------|
| 需求覆盖率 | ≥ 85% | 每个 Story/AC 至少 1 个正向用例 |
| 边界覆盖率 | ≥ 85% | 所有边界值测试点被覆盖 |
| 异常覆盖率 | ≥ 85% | 关键异常场景被覆盖 |
| 负向覆盖率 | ≥ 30% | 无效输入、权限违规场景被覆盖 |
```

SKILL.md §审查员 B（第 73 行）已改为：
> "脚本只输出事实数字，**LLM 评判"质量是否够"**——真实业务有取舍，不强制 100%。"

#### 2. 核心定义冲突

**✗ 有（P0 级）**

**审查员 B 的工作分配完全矛盾**：

| 维度 | .mdc | SKILL.md |
|------|------|---------|
| 覆盖率指标 | 固定 4 项（需求/边界/异常/负向）+ 固定阈值 | 5 项指标（S4风险点/异常树/is_assumed/s4_reference/applies_rule），**LLM 评判质量** |
| 审查员 B 谁做 | .mdc 无明确说明 | SKILL.md §审查员 B："**脚本只统计数字，LLM 评判质量**" |

#### 3. 章节结构错位

**✓ SKILL.md 章节更完整**

SKILL.md 有完整 §1.4 LLM 必读材料（5 项）、§1.5 决策 push 块（§1.5.1~§1.5.3）。.mdc 无 §1.4 和独立 §1.5 节。

#### 4. SSoT 引用合规

**✓ 合规**

#### 5. 决策 push 块状态

**SKILL.md 有（§1.5.1~§1.5.3），.mdc 无**

#### 6. 跨阶段引用

**⚠️ S7 审查报告字段与 S8 SKILL.md 期望的字段不一致**

S8 SKILL.md §核心任务（第 74 行）读取 S7 review_report.json 时期望字段：`s4_risk_coverage`（来自 SKILL.md 的新指标），但 .mdc 版本的 JSON 输出（第 122 行）只有 `requirement_coverage`、`boundary_coverage`、`exception_coverage`、`negative_coverage`（旧指标）。如果按 .mdc 执行，S8 读取 `s4_risk_coverage` 时会得到 undefined。

#### 评分

**2 / 10**（全项目最低分）

#### P0 问题

> **P0-7：S7 .mdc §质量门禁残留 PASS/FAIL 硬判决**
> - 位置：.mdc §质量门禁（第 50 行）
> - 内容："覆盖率 ≥ 85% 且 结构完整性 ≥ 90% = PASS，否则 FAIL"
> - 冲突：SKILL.md §3 明确标注"v1.0 旧规则已废弃"
> - 修复：**删除 .mdc §质量门禁节**，改用 SKILL.md 的"无硬阈值，LLM 按业务实际写建议"模式

> **P0-8：S7 .mdc §审查员 B 残留硬性阈值**
> - 位置：.mdc §审查员 B（第 43 行）
> - 内容：需求覆盖率 ≥ 85%、边界覆盖率 ≥ 85%、异常覆盖率 ≥ 85%、负向覆盖率 ≥ 30%
> - 冲突：与 SKILL.md §审查员 B "脚本只统计数字，LLM 评判质量"矛盾
> - 修复：改为 SKILL.md 的 5 项指标（S4 风险点/异常树/is_assumed/s4_reference/applies_rule）+ LLM 语义评判

> **P0-9：S7 .mdc 与 SKILL.md review_report.json 字段不一致**
> - .mdc 输出：requirement_coverage / boundary_coverage / exception_coverage / negative_coverage
> - SKILL.md 期望（供 S8 读取）：s4_risk_coverage / s4_exception_coverage / is_assumed 填充率 / s4_reference 填充率 / applies_rule 填充率
> - 冲突：按 .mdc 执行时 S8 无法正确读取覆盖率数据
> - 修复：统一 JSON schema 为 SKILL.md 版本

---

### S8 (STAGE_S8_SELF_ITERATION.mdc ↔ aidocx-s8-self-iteration/SKILL.md)

#### 1. 硬指标残留

**✗ 有（P0 级）**

**.mdc §核心任务（第 27 行）残留 PASS/FAIL 判决逻辑**：

```markdown
S7 PASS 时，审查报告 + 建议的补充用例作为 S8 输入。
S7 FAIL 时，返回 S6 修改建议，重新生成用例后重审。
```

SKILL.md §第 2 步（第 77 行）**明确给出了 PASS/FAIL 判决条件**：

```markdown
| 条件 | 判决 | 含义 |
|------|------|------|
| S4风险点覆盖率=100% 且 S4异常树覆盖率=100% 且 结构完整性≥90% | PASS | 所有风险已覆盖 |
| S4风险点覆盖率<100% 或 S4异常树覆盖率<100% | FAIL | 存在未被覆盖的风险点 |
```

**这与 S7 SKILL.md "v2.0 不再做 PASS/FAIL 硬判决"的精神直接冲突**。S7 SKILL.md 已废弃硬判决，S8 SKILL.md 却还在用"覆盖率=100%"作为 PASS 条件。

#### 2. 核心定义冲突

**✗ 有（P1 级）**

**建议数量不一致**：

| 文件 | 建议分类 | 位置 |
|------|---------|------|
| .mdc | 5 类建议（高优先级/中优先级）| §4. 归档摘要（第 93 行）|
| SKILL.md | 4 字段：Problem / Evidence / Root Cause / Fix | §第 4 步（第 111 行）|

具体分类：.mdc 的 `5. 下一轮迭代重点`（第 101 行）说"归档摘要 / 下一轮迭代重点"，未明确列出数量。SKILL.md §核心任务（第 111 行）有明确的 **4 字段结构**（Problem / Evidence / Root Cause / Fix / Affected Stage / Expected Impact）。

#### 3. 章节结构错位

**✓ SKILL.md 章节更完整**

SKILL.md 有完整 §1.4 LLM 必读材料（6 项）、§1.5 决策 push 块。.mdc 无 §1.4 和独立 §1.5 节。

#### 4. SSoT 引用合规

**✓ 合规**

#### 5. 决策 push 块状态

**SKILL.md 有，.mdc 无**

#### 6. 跨阶段引用

**✓ 一致**

两文件均依赖 S7 review_report.json 的 `overall_pass` 字段。

#### 评分

**5 / 10**

#### P0 问题

> **P0-10：S8 .mdc 残留 PASS/FAIL 判决条件**
> - 位置：.mdc §核心任务（第 27 行）
> - 冲突：与 S7 SKILL.md "v2.0 不再做 PASS/FAIL 硬判决"精神冲突；S8 SKILL.md §第 2 步也给出了硬性 PASS/FAIL 条件
> - 修复：删除 .mdc 中的判决逻辑，改为"LLM 分析 S7 报告，输出根因 + 改进建议"

---

## P0 级问题汇总（必须修）

| # | 阶段 | 问题 | 位置 | 修复方向 |
|---|------|------|------|---------|
| P0-1 | S2.5 | .mdc 缺失 Step 0 配置收集强制前置 | .mdc §核心任务 | 增加 Step 0 + project_config.json 门禁 |
| P0-2 | S5 | .mdc 残留硬性数量指标（≥2/≥1） | .mdc §核心任务 第 39-44 行 | 删除数量约束，改用"LLM 自然分布" |
| P0-3 | S5 | .mdc 与 SKILL.md TP JSON 字段名不一致 | .mdc JSON 示例 vs SKILL.md §1.5.5 | 统一为 `tp_id` + `test_point_type` |
| P0-4 | S6 | .mdc 残留"18 种测试方法派生系数"硬性范围 | .mdc §18 种测试方法 第 59 行 | 删除派生系数表 |
| P0-5 | S6 | .mdc 残留"模块风险加权"硬性加权值 | .mdc §模块风险加权 第 68 行 | 删除加权表 |
| P0-6 | S6 | .mdc 与 SKILL.md TC JSON 字段名不一致 | .mdc JSON key vs SKILL.md JSON key | 统一为 `case_id` |
| P0-7 | S7 | .mdc §质量门禁残留 PASS/FAIL 硬判决 | .mdc §质量门禁 第 50 行 | **删除整节**，改用"LLM 写建议"模式 |
| P0-8 | S7 | .mdc §审查员 B 残留硬性阈值（≥85%/≥30%）| .mdc §审查员 B 第 43 行 | 改为 SKILL.md 的 5 项指标 + LLM 评判 |
| P0-9 | S7 | .mdc 与 SKILL.md review_report.json 字段不一致 | .mdc JSON schema vs SKILL.md | 统一 JSON schema 为 SKILL.md 版本 |
| P0-10 | S8 | .mdc 残留 PASS/FAIL 判决条件 | .mdc §核心任务 第 27 行 | 删除判决逻辑 |

---

## P1 级问题汇总（建议修）

| # | 阶段 | 问题 | 说明 |
|---|------|------|------|
| P1-1 | S1 | 自动化引擎未对齐 | `requirement_reviewer_auto.py` 仍按"4 项内容门禁"实现，待更新 |
| P1-2 | S2.5 | .mdc 缺失 §1.4 LLM 必读材料 | 应增加独立 §1.4 节 |
| P1-3 | S3 | .mdc 缺失 §1.4 LLM 必读材料 | 应增加独立 §1.4 节 |
| P1-4 | S2 | SKILL.md §1.5.5 OBJ 字段名 `obj_id` vs .mdc 的 `id` | 建议统一为 `obj_id` |
| P1-5 | S2 | SKILL.md 有完整 §1.5 决策 push 块（6 个），.mdc 无独立 §1.5 节 | 建议在 .mdc 中增加 §1.5 |
| P1-6 | S4 | S4 残留软性数字约束（≥3 风险点 / ≥50% 交叉引用）| 建议改用决策 push |
| P1-7 | S4 | S5 SKILL.md 未明确推荐 `R-{EpicID}-NN` 作为 s4_reference 格式 | 建议 S5 引用规范中明确推荐 |
| P1-8 | S5 | SKILL.md 有完整 §1.5（6 个 push 块），.mdc 无独立 §1.5 节 | 建议在 .mdc 中增加 §1.5 |
| P1-9 | S6 | SKILL.md 有完整 §1.4（5 项必读），.mdc 无独立 §1.4 节 | 建议在 .mdc 中增加 §1.4 |
| P1-10 | S7 | SKILL.md 有完整 §1.5（3 个 push 块），.mdc 无独立 §1.5 节 | 建议在 .mdc 中增加 §1.5 |
| P1-11 | S8 | .mdc §5 类建议 vs SKILL.md 4 字段结构（Problem/Evidence/Root Cause/Fix）| 建议统一为 SKILL.md 的 4 字段结构 |
| P1-12 | S8 | SKILL.md 有完整 §1.5（无独立编号），.mdc 无独立 §1.5 节 | 建议在 .mdc 中增加 §1.5 |

---

## P2 级问题汇总（小修小补）

| # | 阶段 | 问题 | 说明 |
|---|------|------|------|
| P2-1 | S1 | 章节编号方式不统一 | .mdc 用"§审查产物" / SKILL.md 用"§审查产物 1/2/3"，轻微偏差 |
| P2-2 | S1.5 | "质量评价标准"节在 .mdc 中为"轻量跑通 vs 完整跑通"，SKILL.md 中为"质量评价标准" | 命名不一致 |
| P2-3 | S2.5 | SKILL.md 独有"Step 0"编号，.mdc 的"7 步"编号中无 Step 0 | 编号不对齐 |
| P2-4 | S3 | SKILL.md §阶段入口前置处理描述比 .mdc 详细（OCR/图片归档/语义分类）| .mdc 描述较简略 |
| P2-5 | S4 | SKILL.md §核心任务行号"第 81 行"描述"推荐使用 R-{EpicID}-NN"，但 .mdc 同期内容未提及 | 描述粒度差异 |

---

## 根本原因分析

### 1. .mdc 文件普遍滞后于 SKILL.md 的 v2.0 重构

SKILL.md 文件在 2026-06-15 完成了 v2.0 重构（去除硬指标、移除 PASS/FAIL 硬判决、引入 §1.4 和 §1.5 决策 push 块），但 .mdc 文件**没有同步更新**。具体表现：

- S5 .mdc 仍保留"≥2/≥1"硬数量
- S6 .mdc 仍保留"18 种派生系数"和"模块加权"硬指标
- **S7 .mdc 仍保留 PASS/FAIL 硬判决（最严重）**
- S8 .mdc 仍保留 PASS/FAIL 判决条件
- S2.5 .mdc 和 S3 .mdc 无 §1.4 节

### 2. §1.4 / §1.5 章节结构不同步

SKILL.md 全面引入了 §1.4（LLM 必读材料）和 §1.5（决策 push 块），但 .mdc 文件普遍**没有对应的独立节**。这导致：
- Agent 按 .mdc 执行时不会自动走"必读材料"流程
- 决策 push 的强制力在 .mdc 中被稀释

### 3. JSON Schema 字段名不一致

S5 和 S6 的 JSON 字段名在 .mdc（中文 key）和 SKILL.md（英文蛇形 key）之间存在冲突，这会直接影响下游 S6/S7/S8 的数据消费。

---

## 修复优先级建议

**立即修复（P0，阻断性）**：
1. S7 .mdc §质量门禁的 PASS/FAIL 硬判决（P0-7）
2. S7 .mdc §审查员 B 的硬性阈值（P0-8）
3. S5 .mdc 的硬性数量指标（P0-2）
4. S6 .mdc 的派生系数和加权（P0-4, P0-5）
5. S5/S6 JSON 字段名统一（P0-3, P0-6）

**尽快修复（P1，建议性）**：
1. 所有 .mdc 缺失的 §1.4 和 §1.5 节
2. S2.5 .mdc Step 0 配置前置（P0-1）
3. S7 JSON schema 与 S8 期望对齐（P0-9）
4. S8 判决逻辑（P0-10）

---

*报告生成时间：2026-06-15*
*审查工具：人工逐文件 Read + 交叉比对*
