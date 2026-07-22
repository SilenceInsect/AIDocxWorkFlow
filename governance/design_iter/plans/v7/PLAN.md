# AIDocxWorkFlow 方案 v9 — 数据修复 + INDEX 同步 + v7 治理层推进

> **本方案承接 v8 §3 遗留（Q-V9-001 + Q-V9-002）+ v7 §3 遗留（v7.1/v7.2/v7.3 5 项）**。
> **核心动作**：3 大议题 = (1) v3.0/v3.01 数据修复 + (2) INDEX.md v8/v9 段补齐 + (3) v7 治理层 9 阶段 .mdc 同步 + S7/S8 脚本适配。
> **版本号说明**：v8 = single-issue 修复（1 议题）；v9 = 复合议题（3 议题，含 v7 治理层重接）。

---

## ⚠️ 启动必读：v9 决策清单

> v9 包含 **3 大议题 / 5 子决策**——本档列出全部，决策详情见 `decisions.json`。

| Q 区段 | 议题 | 决策类型 | 候选 | 选择 |
|---|---|---|---|---|
| **Q-V9-001** | v3.0/v3.01 数据重复 | 数据修复 | A: 重命名 / B: 重跑 / C: 保留 | **A（重命名 v3.0 → v3.01）** |
| **Q-V9-002** | INDEX.md v8 段缺失 | 索引同步 | A: 加 v8 段 / B: 留 v9 | **A（加 v8 + v9 段）** |
| **Q-V9-003** | v7.1 - 9 阶段 .mdc 同步 | 治理层 | A: 跑 v7.1 / B: 留 v9.x | **A（v9 内启动 v7.1）** |
| **Q-V9-004** | v7.2 - S7 审查脚本适配 | 治理层 | A: 跑 v7.2 / B: 留 | **A** |
| **Q-V9-005** | v7.3 - S8 review_report 适配 | 治理层 | A: 跑 v7.3 / B: 留 | **A** |

**用户决定（2026-07-10 AskQuestion）**：3 议题都跑（`all_3_topics`）+ v7 治理层 v9 内推进。

---

## v{N} 必备 3 栏

### 1. 本次 v9 解决的问题（来自 v8 + v7）

#### 来自 v8 §3 实战发现

- ✅ **v3.0/raw 与 v3.01 内容重复**（v8 期间未答）——resource/ 只有 v3.01，v3.0/raw 派生自 v3.01
- ✅ **INDEX.md v8 段未加**（v8 期间未答）——current 跟随 v8 但 INDEX 未同步

#### 来自 v7 §3 遗留

- ✅ **9 阶段 .mdc 同步更新工作量**（v7.1 启动）——基于 52 条 Q-501~Q-552 修复
- ✅ **S7 审查脚本适配**（v7.2 启动）——auto_reviewer 4 项指标 → 5 项
- ✅ **S8 读取 S7 review_report.json 适配**（v7.3 启动）——`s4_risk_coverage` 等 5 字段

### 2. 本次 v9 新增内容

#### Phase 1: Q-V9-001 数据修复

```bash
# 操作
mv "workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」/raw/" \
   "workflow_assets/游戏道具商城系统/v3.01/「S1 需求评审」/raw/"
rmdir "workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」"
rmdir "workflow_assets/游戏道具商城系统/v3.0"
```

**结果**：
```
workflow_assets/游戏道具商城系统/
└── v3.01/
    └── 「S1 需求评审」/
        └── raw/
            ├── extracted_images/
            ├── ocr_results/
            ├── extracted_text.md
            └── image_index.json
```

**理由**：v3.0 在 resource 没有原档（只有 v3.01_raw.docx）——v3.0 目录是 S1 Pipeline 误命名（应是 v3.01）。重命名后路径与 resource 一对一。

#### Phase 2: Q-V9-002 INDEX.md 同步

**变更**：
- INDEX.md v8 段（"v8 single-issue 修复 / 已闭环"）
- INDEX.md v9 段（"v9 复合议题 / 进行中"）
- 目录结构图加 plans/v8/ 和 plans/v9/
- "current 软链" 注释更新（v8 实际 cp 不是软链）

#### Phase 3: Q-V9-003 v7.1 - 9 阶段 .mdc 同步

**核心动作**（基于 v7 §2 第一批 15 条 + 第二批 37 条 = 52 条 Q）：

| 修复项 | 涉及文件 | 来源 Q |
|---|---|---|
| 删硬性数量指标（POSITIVE ≥2 / BOUNDARY ≥2 / NEGATIVE ≥1 / EXCEPTION ≥1）| `STAGE_S5_TEST_POINTS.mdc` | Q-502 |
| JSON 字段统一 `tp_id` + `test_point_type` | `STAGE_S5_TEST_POINTS.mdc` + `aidocx-s5-test-points/SKILL.md` | Q-503 |
| 删 18 种测试方法派生系数 + 模块风险加权 | `STAGE_S6_TEST_CASES.mdc` | Q-504 |
| JSON 字段统一 `case_id` | `STAGE_S6_TEST_CASES.mdc` + `aidocx-s6-test-cases/SKILL.md` | Q-505 |
| 删 PASS/FAIL 硬判决 | `STAGE_S7_REVIEW.mdc` | Q-506 |
| review_report.json schema 对齐（`s4_risk_coverage` 等 5 项）| `STAGE_S7_REVIEW.mdc` | Q-506 |
| 删 PASS/FAIL 判决条件 | `STAGE_S8_SELF_ITERATION.mdc` | Q-507 |
| Step 0 配置收集强制前置 | `STAGE_S2_5_ITERATION.mdc` | Q-501 |
| 9 阶段 .mdc 普遍补 §1.4 + §1.5 | 10 份 .mdc | Q-508~Q-519 |
| Object ID 字段统一 `obj_id` | `STAGE_S2_BREAKDOWN.mdc` | Q-509 |
| 软性数字约束改为决策 push | `STAGE_S4_FLOWCHART.mdc` | Q-512 |
| 4 字段结构（Problem/Evidence/Root Cause/Fix）| `STAGE_S8_SELF_ITERATION.mdc` | Q-520 |
| 异常树 ID 格式 `S4-{EpicID}-X.Y.Z` | `aidocx-s4-flowchart/SKILL.md` | Q-562 |
| LLM 根因 + 改进建议（S8）| `STAGE_S8_SELF_ITERATION.mdc` | Q-540/Q-568 |

**预计改动**：~10 份 STAGE_*.mdc + 5 份 SKILL.md = 15 文件

#### Phase 4: Q-V9-004 + Q-V9-005 v7.2 + v7.3 脚本适配

**v7.2 S7 审查脚本**：
- `ai_workflow/auto_reviewer.py`：4 项指标 → 5 项（`s4_risk` / `s4_exception` / `is_assumed` / `s4_reference` / `applies_rule`）
- `aidocx-s7-review/SKILL.md` §自动化支持更新

**v7.3 S8 适配**：
- `ai_workflow/self_iteration.py`（旧 `iteration_aggregator.py`）：字段映射 `s4_risk_coverage` 等
- `aidocx-s8-self-iteration/SKILL.md` 字段说明
- 5 项审查指标与 S8 根因链路表建立映射（is_assumed / s4_reference / applies_rule）

**预计改动**：~5 份（auto_reviewer.py / self_iteration.py / 3 份 SKILL.md）

### 3. 本次 v9 仍遗留的问题（→ v10 解决）

- 🚧 **v7.1 完整同步**（如本响应未完结）——9 阶段 .mdc 同步工作量较大
- 🚧 **v7.2 + v7.3 脚本验证**——`auto_reviewer.py --self-test` 需跑通
- 🚧 **跨阶段引用一致性回归测试**——v9 修改 15+ 份规则后需跑 S1-S8 全流程验证
- 🚧 **`before_prompt_dna_check.py` 适配 v7 决策表落档协议**——v9 启动时新增落档协议但 hook 未同步

---

## 关键引用

| 内容 | 路径 |
|---|---|
| v9 决策表（详细）| `governance/design_iter/current/q_decision_table_v9.md` |
| v9 决策清单（机读）| `governance/design_iter/plans/v9/decisions.json` |
| v8 决策表 | `governance/design_iter/current/q_decision_table.md`（v8 启动时落档）|
| v7 治理档（未完成）| `governance/design_iter/plans/v7/PLAN.md` + `audit_input*.md` |
| SSOT | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` |
| 项目根铁律 | `AGENTS.md` |
| DNA §9 落档协议 | `.cursor/rules/DNA_3Q_CHECK.mdc §9.4 + §9.5` |

---

> **维护者**：v9 是 v7 治理层的"重接"——3 大议题含数据/索引/治理，跨 v7 遗留 + v8 实战。后续 v10 应聚焦"跨阶段引用一致性回归测试"——保证 v9 改完 15+ 份规则后全流程仍可跑。