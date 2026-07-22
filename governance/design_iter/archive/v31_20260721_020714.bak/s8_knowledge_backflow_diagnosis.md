# S8 未回灌 TP 库根因诊断

> **诊断日期**：2026-07-21
> **Round**：Round 2
> **诊断目标**：回答"TP 库为空（⏳ 待补）的根因是 S8 哪个环节断裂"
> **依据文件（已 Read）**：
> - `.cursor/skills/aidocx-s8-self-iteration/SKILL.md`（313 行）
> - `.cursor/rules/STAGE_S8_SELF_ITERATION.mdc`（417 行）
> - `ai_workflow/recurring_failures.py`（255 行）
> - `workflow_assets/游戏道具商城系统/v3.01/`（目录列表，无 S7/S8 产物）
> - `knowledge/public/test_point_library/<MODULE>/README.md`（8 模块，均 ⏳ 待补）

---

## 0. 诊断结论（先说结论再展开）

**TP 库为空的根因不是"S8 没执行"，而是"S8 的双段归档链路从未被触发"**：

| 链路段 | 预期行为 | 实际行为 | 根因 |
|--------|---------|---------|------|
| 第 1 段（本地队列）| S8 识别 must_fix/should_fix → 写入 `knowledge/project_local/.review_queue/` | v3.01 无 S7/S8 产物 → **链路从未触发** | v3.01 未执行 S7 → 无 S8 输入 → 无归档触发 |
| 第 2 段（公共库）| 人工审核 `.review_queue/` → 回写 `knowledge/public/test_point_library/` | **从未执行**（无人工审核流程） | 人工程序缺失 |
| 整体 | 跨项目知识积累 | 零积累 | 整个 v3.01 流程未走完 S5→S6→S7→S8 |

---

## 1. S8 归档链路现状（基于 Read 的事实）

### 1.1 S8 SKILL.md §归档机制（lines 176-186）

```
归档位置：
- knowledge/project_local/.review_queue/  ← 本地待审候选（可写）
- knowledge/public/test_point_library/      ← 公共测试点库（只读，不自动写入）
- knowledge/public/test_case_library/       ← 公共用例库（只读，不自动写入）
```

**关键发现**：S8 SKILL.md **从未提及** `test_point_library/` 的"自动入库"——入库需要人工审核这一约束已写入 SKILL 层。

### 1.2 STAGE_S8_SELF_ITERATION.mdc §归档机制（lines 150-169）

**归档触发条件（必须执行）**：

| 条件 | 触发动作 |
|------|---------|
| 根因为 `S5_MODULE` | 写入 `.review_queue/` 待审候选 |
| 根因为 `S5_EXEC` | 写入 `.review_queue/` 待审候选 |
| 根因为 `S6_EXEC` | 写入 `.review_queue/` 待审候选 |
| 根因涉及 Prompt 规则不明确 | 写入 `.cursor/rules/prompt_fixes/<Stage>_<日期>.md` |

**关键发现**：归档**必须由 S8 执行**（按根因分类写入），但 v3.01 无 S7 产物 → S8 无输入 → 无根因 → 无归档。

### 1.3 S8 §1.5.2 禁止直接改公共库

```markdown
> **禁止 S8 直接修改公共 knowledge/public/module_templates/。**
> 所有经验先写入 knowledge/project_local/.review_queue/：
> - 候选中必须注明目标公共文件
> - 候选中必须注明目标段落
> - 候选中必须注明来源缺陷 ID、根因类型、建议补充内容
> - 其余测试点库/用例模板库同理，先出候选，后人工审核入公共库
```

### 1.4 recurring_failures.py — S8 聚合逻辑（lines 207-258）

`build_failures_from_iteration_result()` 消费 `iteration.json`：
- 读取 `fact_summary.s4_reference_fill_rate`
- 读取 `defect_frequencies.by_root_cause`
- 写入 `recurring_failures.json`（本地记录）

**关键发现**：`recurring_failures.json` 是**项目内本地**失败模式记录，不是公共 TP 库。S8 聚合并写入的是本地记录，不是 `test_point_library/`。

---

## 2. v3.01 实际情况（基于目录扫描的事实）

```
workflow_assets/游戏道具商城系统/v3.01/
├── 「S1 需求评审」/ ← 有产物
├── 「S2 需求拆解」/ ← 有产物
├── 「S3 原型导出」/ ← 有产物
├── 「S4 流程图导出」/ ← 有产物
├── （无 S5 目录）
├── （无 S6 目录）
├── （无 S7 目录）
└── （无 S8 目录）
```

**v3.01 实际只走到 S4**。S5/S6/S7/S8 均未执行。

---

## 3. 根因链路图

```
v3.01 只执行到 S4（S1-S4 有产物）
    ↓
无 S5 test_points.json → 无 S6 TC
    ↓
无 S6 TC → 无 S7 审查
    ↓
无 S7 review_report.json → S8 无输入（前置材料缺失）
    ↓
S8 §核心任务 "读取 S7 review_report" 失败 → 生成 fail_report_S8.md
    ↓
fail_report S8 → 不触发归档链路第 1 段（本地队列）
    ↓
第 2 段（人工审核）从未执行
    ↓
TP 库为空（test_point_library/）← 不是 S8 不想写，是从来没触发写入条件
```

---

## 4. 根因分类

### 根因 A：流程未走完（主因）

| 项目 | v3.01 |
|------|-------|
| S1-S4 | ✅ 执行完毕 |
| S5 | ❌ 未执行 |
| S6 | ❌ 未执行（依赖 S5） |
| S7 | ❌ 未执行（依赖 S6） |
| S8 | ❌ 未执行（依赖 S7） |

**结论**：整个 S5→S6→S7→S8 链路从未触发。TP 库入库的前提条件（S7 review_report.json 存在）从未满足。

### 根因 B：S8 设计本身有两段约束（设计正确，但执行空转）

| 约束 | 写入位置 | 说明 |
|------|---------|------|
| 第 1 段 | `knowledge/project_local/.review_queue/` | S8 执行 → 写入本地候选 |
| 第 2 段 | `knowledge/public/test_point_library/` | 人工审核 → 回写公共库 |

**问题**：第 2 段"人工审核 → 回写公共库"在项目中从未建立。即使 S8 写入了 `.review_queue/`，也没有后续人工流程把候选回写到 `test_point_library/`。

### 根因 C：S8 的"禁止直接改公共库"约束是正确的，但人工审核机制缺失

S8 STAGE 文件明确规定：
> 禁止 S8 直接修改公共 `knowledge/public/module_templates/`。

这一约束**本身是对的**——防止 S8 产生低质量内容直接污染公共知识库。但"人工审核后再入公共库"的人工程序在项目中**从未落地**。

---

## 5. TP 库为空不是 S8 的 Bug，是项目流程缺失

### 5.1 设计 vs 实现的差距

| 维度 | S8 设计（正确） | 项目实际（缺失） |
|------|----------------|-----------------|
| 归档入口 | S7 must_fix/should_fix → S8 → `.review_queue/` | v3.01 无 S7 → 无入口 |
| 人工审核 | `.review_queue/` → 人工审核 → 公共库 | 无人工审核流程 |
| 审核标准 | `test_point_library/README.md §入库流程`（复用门槛 ≥ 2 + S7 PASS）| 无审核流程 |
| 自动化 | 无（S8 不直接改公共库）| — |
| 积累速度 | 每项目 × 每 S8 循环 + 人工审核 | 零积累 |

### 5.2 "S8 没回灌"的本质

**不是 S8 没干活，而是两层条件都没满足**：

1. **触发条件**（S7 review_report.json 存在）→ 从未满足
2. **审核条件**（人工审核 `.review_queue/`）→ 从未建立

---

## 6. 修复方案

### 6.1 短期（S8 层改进，不改设计）

**方案 S1（采纳）**：在 v31 方法论草案 §8 新增"S8 回灌 TP 库契约"，明确：

| 字段 | 内容 |
|------|------|
| 输入 | `iteration.json#root_causes[].archive_summary` |
| 输出 | `knowledge/project_local/.review_queue/<Module>/<Subclass>__<defect_id>__<date>.md` |
| 人工审核 | 由 `.review_queue/` 触发人工审核，审核结果回写 `test_point_library/` |
| 审核标准 | `test_point_library/README.md §入库流程`（复用门槛 ≥ 2 + S7 PASS）|

**Round 2 act**：在 `v31_方法论_草案.md` 新增 §8"S8 回灌 TP 库契约"段（见草案 §8）。

### 6.2 中期（流程层改进）

**方案 M1**：在 S7 SKILL.md 或 STAGE_S7_REVIEW.mdc 中建立"审核触发"机制：

- S7 审查报告 PASS 后，自动通知人工（在 `review_report.json` 中加 `review_queue_triggered: true`）
- 人工审核 `.review_queue/` 中的候选
- 审核通过 → 回写 `test_point_library/`
- 审核不通过 → 标记 `rejected`，由 S8 下一轮迭代

**Round 2 act**：在 §8 中描述此方案（不立即执行，标记为"中期改进建议"）。

### 6.3 长期（TP 库自动激活）

**方案 L1**：当 `test_point_library/<MODULE>/` 累计 ≥ 10 个条目后，激活"自动复用"机制：

- S5 生成 TP 时，优先从 `test_point_library/` 匹配相似 TP
- 匹配成功 → 填充 `tpl_id` + `usage_count++`
- 匹配失败 → 从 module_templates 生成新 TP
- S8 迭代后 → 候选 → 人工审核 → 入库 → 形成正向积累

**Round 2 act**：在 §8 中描述此方案（不立即执行，标记为"长期目标"）。

---

## 7. 诊断结论

| 诊断项 | 结论 |
|--------|------|
| S8 有没有干活？ | ✅ S8 设计正确，机制完善 |
| 为什么 TP 库为空？ | ❌ S5→S6→S7→S8 链路从未触发（v3.01 只走到 S4）+ 人工审核机制缺失 |
| 根因是 S8 的 Bug 吗？ | ❌ 不是 Bug，是流程缺失 + 两段归档链路条件未满足 |
| S8 的禁止直接改公共库约束对吗？ | ✅ 对（防止低质量污染公共库）|
| 人工审核机制在哪里？ | ❌ 项目中从未建立 |
| 修复优先级 | 短期：§8 契约落地；中期：S7 触发人工审核；长期：TP 库自动激活 |

---

## 8. 附录：recurring_failures.json 与 test_point_library 的区别

| 维度 | `recurring_failures.json` | `test_point_library/` |
|------|--------------------------|---------------------|
| 写入者 | `recurring_failures.py`（S8 聚合）| 人工审核后回写 |
| 位置 | `workflow_assets/_governance/` | `knowledge/public/` |
| 性质 | **项目内本地**失败模式记录 | **公共可复用** TP 模板 |
| 用途 | 防止同类错误重复出现 | 供后续需求 S5 生成时复用 |
| 触发条件 | 每 S8 执行后更新 | 每人工审核通过后更新 |
| 积累速度 | 快（自动）| 慢（需人工审核）|
| 与 TP 库关系 | 独立；不直接贡献 TP 库 | 直接贡献 TP 库 |

**关键区别**：`recurring_failures.json` 是**防止再犯**的本地记录；`test_point_library/` 是**知识积累**的公共库。两者互补但不是同一机制。
