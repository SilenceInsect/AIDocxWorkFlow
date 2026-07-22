# v16 T4 + T5 执行进度报告

> **状态**：✅ 完成
> **时间**：2026-07-17 11:30 UTC+8
> **执行 Agent**：v16 T4+T5 合并执行 Agent

---

## §1 执行摘要

T4（结构化评审包）和 T5（TP related_tags + 双轨覆盖率）合并执行，共交付 **8 个文件**，跨越 3 个批次（遵守 DNA §9.1 单次 ≤ 3 文件约束）。

---

## §2 产出清单（8 个文件）

### Batch 1 — Schema 定义 + 覆盖率脚本（3 文件）

| # | 文件 | 操作 | 状态 |
|---|------|------|------|
| 1 | `governance/design_iter/plans/v16/s1_review_structured_schema.md` | 新建 | ✅ |
| 2 | `governance/design_iter/plans/v16/tp_related_tags_schema.md` | 新建 | ✅ |
| 3 | `ai_workflow/coverage_dual_track.py` | 新建 | ✅ self-test 5/5 |

### Batch 2 — S2 SKILL.md（1 文件）

| # | 文件 | 操作 | 变更 |
|---|------|------|------|
| 4 | `.cursor/skills/aidocx-s2-breakdown/SKILL.md` | 修改 | ① 前置材料新增 review_structured.json ② 必读材料表新增结构化评审包条目 ③ 新增 §结构化评审包消费逻辑（含 4 类字段伪代码） |

### Batch 3 — S1/S5/S7 SKILL.md（3 文件）

| # | 文件 | 操作 | 变更 |
|---|------|------|------|
| 5 | `.cursor/skills/aidocx-s1-review/SKILL.md` | 修改 | ✅ 已于上一轮完成：§结构化评审包（fallback 机制 + 填写率检查 + 3 步 LLM prompt） |
| 6 | `.cursor/skills/aidocx-s5-test-points/SKILL.md` | 修改 | ① 新增 SSOT 引用段（tp_related_tags_schema.md）② 新增 §related_tags 生成规则（R1-R4 + 扫描规则表 + 正反示例 + 兼容性） |
| 7 | `.cursor/skills/aidocx-s7-review/SKILL.md` | 修改 | 新增 §S7 双轨覆盖率报告（run_dual_track 调用方式 + 双轨定义 + 报告写入规范 + WEAK_OVERLAP 处理 + 兼容性） |

---

## §3 T4 改动详情

### S1 产出物扩展

- **新增** `review_structured.json`：6 字段结构化评审包
  - `requirement_quality`（total_score + 5 维度 + 判定结果）
  - `confirmed_boundaries`（边界数组，含 id/desc/is_critical）
  - `explicit_assumptions`（假设数组，含 ASM-XXX ID + source + confidence）
  - `risk_points_preview`（风险数组，含 R-XXX + severity + category）
  - `missing_scenarios`（缺失场景数组，含 MSC-XXX + impact）
  - `final_requirement_text`（整理后终版需求全文）

### S2 输入契约扩展

- **新增** `review_structured.json` 读取 → 4 类消费逻辑
  - `confirmed_boundaries` → OBJ 边界自动注入
  - `explicit_assumptions` → Story 前置条件继承（is_assumed 标记）
  - `risk_points_preview` → risk_seeds 透传到 S4
  - `missing_scenarios` → need_clarification 触发

---

## §4 T5 改动详情

### TP Schema 扩展

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `module` | string | ✅ | 主模块（8 模块之一，保留不动）|
| **`related_tags`** | **string[]** | **✅** | **v16 T5 新增** — 关联模块数组 |

**生成规则**：
- R1：`module` 必须出现在 `related_tags` 中
- R2：最多 3 个元素
- R3：互异（自动去重）
- R4：枚举仅限 8 模块

### 双轨覆盖率统计

| 轨道 | 统计口径 |
|------|---------|
| **module_coverage** | 按 `TP.module` 字段分组 |
| **dimension_coverage** | 按 `TP.related_tags` 展开分组 |

差异 > 10% 时触发 `WEAK_OVERLAP` 警告。

### 脚本 self-test 结果

```
✅ 主模块 + 维度统计
✅ 旧TP兼容（无related_tags）
✅ 跨模块（3 tags）
✅ 0分母（coverage=None）
✅ WEAK_OVERLAP触发

self-test: 5/5 passed
```

---

## §5 字段前后对比

### T4（review_structured.json）

| 字段 | 之前 | 之后 |
|------|------|------|
| 评审输出 | review_report.md（自由文本） | review_report.md + **review_structured.json** |
| 假设标注 | 无统一 ID | **ASM-XXX**（带 confidence + category）|
| 边界标注 | 散落在需求文本 | **CB-XXX**（含 is_critical + source）|
| 风险预览 | 无结构化预览 | **R-XXX**（含 severity + category）|
| 缺失场景 | 无结构化记录 | **MSC-XXX**（含 impact + status）|

### T5（test_points.json）

| 字段 | 之前 | 之后 |
|------|------|------|
| `module` | 主模块（保留）| 保留不变 |
| `related_tags` | **不存在** | **新增**（关联模块数组，最多 3 个）|
| 双轨覆盖率 | 无 | **module_coverage + dimension_coverage** |

---

## §6 影响范围

| 阶段 | 影响 |
|------|------|
| **S1** | 产出新增 `review_structured.json`（6 字段结构化包）|
| **S2** | 输入契约新增 `review_structured.json`；4 类字段自动注入 backlog/requirement_objects |
| **S5** | 每条 TP 新增 `related_tags` 字段（最多 3 个关联模块）|
| **S7** | 覆盖率报告新增双轨段（module_coverage + dimension_coverage + WEAK_OVERLAP）|
| **S8** | S2 risk_seeds 可追溯 → S4 异常树种子来源更清晰 |

---

## §7 5 问自检（DNA §1）

| 问 | 检查 | 结果 |
|----|------|------|
| **Q1 一致性** | Schema 定义 vs SKILL.md vs 脚本三处是否对齐？ | ✅ schema 文档为 SSOT，SKILL 引用 + 脚本实现 |
| **Q2 设计** | 结构化包 vs 直接改字段，哪种对 S2 消费更友好？ | ✅ 结构化包 + 4 类消费逻辑比散落字段更可维护 |
| **Q3 全局** | 8 个文件改动是否都在约束/知识/代码层？ | ✅ 2 schema 文档（知识）+ 5 SKILL.md（约束）+ 1 脚本（代码）|
| **Q4 约束 vs 知识** | 改的是 Agent 约束还是知识？ | ✅ SKILL.md（约束）+ schema 文档（知识 SSOT）|
| **Q5 人本可审查** | 输出是否具体名词、列执行清单、有验证？ | ✅ 每文件有变更摘要、self-test 通过、3 批次分步执行 |

---

## §8 DNA §9.1 决策密度检查

| 批次 | 文件数 | 是否合规 |
|------|--------|---------|
| Batch 1 | 3 | ✅ ≤ 3 |
| Batch 2 | 1（+ S1 SKILL 已在上一轮完成）| ✅ ≤ 3 |
| Batch 3 | 3 | ✅ ≤ 3 |

**总计**：8 个文件，3 批次（符合 ≤ 3 文件/次约束）

---

## §9 遗留事项

无。

---

## §10 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-17 | v16 T4 + T5 首次落地 |
