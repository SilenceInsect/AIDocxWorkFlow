# 目录主轴调整：先版本再阶段（v8 启动议题）

> **触发**：用户反馈 v3.0 已落地为 `workflow_assets/游戏道具商城系统/「S1 需求评审」/v3.0/raw/` 路径，
> 但希望改为 `workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」/raw/`（先版本再阶段）。
>
> **本档是 v8 启动候选方案**——v7 主体已闭环（参见 open_questions.md §v6.2 闭环汇总）。

---

## 1. 问题陈述

当前约束（`DESIGN_AND_EXECUTION_STANDARDS.mdc §2.6` + `§4.5 STAGE_PATTERNS`）规定目录主轴：

```
workflow_assets/<req_name>/「S{n} 阶段」/<version>/...
```

用户希望改为：

```
workflow_assets/<req_name>/<version>/「S{n} 阶段」/...
```

### 1.1 用户决策（2026-07-09 AskQuestion 收集）

| Q | 选项 | 决定 |
|---|---|---|
| 1 约束同步范围 | `all_stage_mdcs` | ✅ 全部 10 份 STAGE_S*.mdc 同步扫引用 |
| 2 v3.0/raw 处理 | `mv_to_new_structure` | ✅ mv 到新结构 |
| 3 resource/ 是否对齐 | `keep_resource_old` | ✅ 不调整（resource 保持现状） |
| 4 历史版本回填 | `all_versions` | ✅ 所有版本都迁移（当前只有 v3.0，所以 = 迁移这一份） |

---

## 2. 影响面（先验后答 §9.4 — 都已 Read/Grep 验证）

### 2.1 约束文件（SSOT + 阶段规则）

| 文件 | 引用数 | 备注 |
|---|---|---|
| `DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.6 + §4.5 + §0.1 | 3 处 + STAGE_PATTERNS 字典 | SSOT，必先改 |
| `STAGE_S1_REVIEW.mdc` | ≥ 6 处路径 | |
| `STAGE_S1.5 Clarification.mdc` | ≥ 9 处路径 | |
| `STAGE_S2_BREAKDOWN.mdc` | ≥ 5 处路径 | |
| `STAGE_S2_5_ITERATION.mdc` | ≥ 8 处路径 | |
| `STAGE_S3_PROTOTYPE.mdc` | ≥ 5 处路径 | |
| `STAGE_S4_FLOWCHART.mdc` | ≥ 6 处路径 | |
| `STAGE_S5_TEST_POINTS.mdc` | ≥ 5 处路径 | |
| `STAGE_S6_TEST_CASES.mdc` | ≥ 6 处路径 | |
| `STAGE_S7_REVIEW.mdc` | ≥ 3 处路径 | |
| `STAGE_S8_SELF_ITERATION.mdc` | ≥ 9 处路径 | |

### 2.2 技能文件（SKILL.md）

| 文件 | 引用数 |
|---|---|
| `aidocx-s1-review/SKILL.md` | ≥ 3 |
| `aidocx-s1-5-clarification/SKILL.md` | ≥ 9 |
| `aidocx-s2-breakdown/SKILL.md` | ≥ 6 |
| `aidocx-s2-5-iteration/SKILL.md` | ≥ 4 |
| `aidocx-s3-prototype/SKILL.md` | ≥ 3 |
| `aidocx-s4-flowchart/SKILL.md` | ≥ 3 |
| `aidocx-s5-test-points/SKILL.md` | ≥ 3 |
| `aidocx-s6-test-cases/SKILL.md` | ≥ 6 |
| `aidocx-s7-review/SKILL.md` | ≥ 6 |
| `aidocx-s8-self-iteration/SKILL.md` | ≥ 5 |

### 2.3 根规则

| 文件 | 引用 |
|---|---|
| `AIDocxWorkFlow.mdc` | 目录结构示例（含 v1.0/v2.0/v3.0） |

### 2.4 Hooks

| 文件 | 影响 |
|---|---|
| `.cursor/hooks/auto_advance_check.py` | STAGE_PATTERNS 字典（S1-S8 路径常量） |

### 2.5 代码（实现）

| 文件 | 影响 |
|---|---|
| `ai_workflow/conversation_skills.py` | STAGE_PATTERNS + 5 处路径构造 |
| `ai_workflow/runtime_contracts.py` | STAGE_PATTERNS + 6 处 JSON 路径字段 |
| `ai_workflow/test_case_formatter.py` | 默认 output_dir |
| `ai_workflow/stage_s1_input/utils/constants.py` | 默认 output_dir |

### 2.6 README

| 文件 | 影响 |
|---|---|
| `README.md` 第 271-272 行 | 目录结构示例 |

### 2.7 现有数据

| 路径 | 处理 |
|---|---|
| `workflow_assets/游戏道具商城系统/「S1 需求评审」/v3.0/` 整目录（含 raw/） | mv 到新结构 |

---

## 3. 候选方案

### 3.1 候选 A：先版本再阶段（用户提出）

```
workflow_assets/<req_name>/<version>/「S{n} 阶段」/...
```

**优点**：
- 同一版本的所有阶段产物一目了然（"看 v3.0 全长啥样"）
- 与 `resource/<req_name>/<version>_raw.docx` 路径模式对齐（都先版本）

**缺点**：
- 25+ 文件改动，跨约束/代码/数据 4 层
- 需要 mv 现有 v3.0 数据

### 3.2 候选 B：保持现状（拒绝改动）

**优点**：0 改动
**缺点**：用户已明示希望改

### 3.3 候选 C：仅改约束示例，不改代码（折中）

**优点**：约束文档改、代码不动
**缺点**：代码与约束失配，运行时会按旧路径生成产物 → 双轨状态

---

## 4. 推荐决策

**采用 A**（用户决定已通过 AskQuestion 收集）。理由：

1. 用户已明确方向（决策优先于方案优先）
2. DNA §0.1 禁止"约束 / 实现 / 文档失配"
3. 影响虽大但都是**模板路径**改动 + **1 次 mv**，可用脚本批量完成

---

## 5. 执行计划（待用户最终点头）

### Phase 1：批量模板替换

- 工具：`sed`（或 Python `pathlib` 脚本）
- 模式：`workflow_assets/<req_name>/「S{N} 阶段名」/<version>` → `workflow_assets/<req_name>/<version>/「S{N} 阶段名」`
- 范围：`.cursor/rules/` + `.cursor/skills/` + `ai_workflow/` + `README.md` + `AIDocxWorkFlow.mdc`

### Phase 2：mv 现有数据

```
mv "workflow_assets/游戏道具商城系统/「S1 需求评审」/v3.0" \
   "workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」"
```

### Phase 3：SSOT 同步

- `DESIGN_AND_EXECUTION_STANDARDS.mdc §2.6`：目录树示例更新
- `DESIGN_AND_EXECUTION_STANDARDS.mdc §4.5`：STAGE_PATTERNS 字典更新（如需，因为 §4.5 只是常量引用示例）

### Phase 4：验证

- `grep -r "「S[1-8]" .cursor/ ai_workflow/` 应该**0 命中**（除新约束里的示例）
- `ls workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」/raw/` 应有 raw/ 内容
- `python3 -m py_compile` 跑改动过的 .py 文件

---

## 6. 待用户确认

- [ ] 方案 A 确认？（用户已通过 AskQuestion 表态，但还没"动手"前最终点头）
- [ ] Phase 1 用 `sed` 还是 Python 脚本？（脚本可逆、可追溯；sed 单次更快）
- [ ] Phase 4 验证标准是否需要更严格（除 py_compile 外是否跑 self-test）？

---

## 7. 落档协议执行记录（§9.5）

- **本文件创建于**：governance/design_iter/current/q_decision_table.md（v7 跟踪）
- **创建时机**：本响应决策展开**前**先落档（§9.5 §9.4 同时满足）
- **改动文件清单**（已完成，2026-07-09）：

### Phase 1: 路径批量重写（脚本执行）

| 批次 | 文件 | 替换数 |
|---|---|---|
| B1 | `DESIGN_AND_EXECUTION_STANDARDS.mdc` | 1 |
| B2 | `STAGE_S1_REVIEW.mdc` | 4 |
| B2 | `STAGE_S1.5 Clarification.mdc` | 9 |
| B2 | `STAGE_S2_BREAKDOWN.mdc` | 10 |
| B2 | `STAGE_S2_5_ITERATION.mdc` | 11 |
| B2 | `STAGE_S3_PROTOTYPE.mdc` | 5 |
| B2 | `STAGE_S4_FLOWCHART.mdc` | 9 |
| B2 | `STAGE_S5_TEST_POINTS.mdc` | 7 |
| B2 | `STAGE_S6_TEST_CASES.mdc` | 10 |
| B2 | `STAGE_S7_REVIEW.mdc` | 13 |
| B2 | `STAGE_S8_SELF_ITERATION.mdc` | 11 |
| B3 | `aidocx-s1-review/SKILL.md` | 6 |
| B3 | `aidocx-s1-5-clarification/SKILL.md` | 12 |
| B3 | `aidocx-s2-breakdown/SKILL.md` | 10 |
| B3 | `aidocx-s2-5-iteration/SKILL.md` | 6 |
| B3 | `aidocx-s3-prototype/SKILL.md` | 4 |
| B3 | `aidocx-s4-flowchart/SKILL.md` | 8 |
| B3 | `aidocx-s5-test-points/SKILL.md` | 4 |
| B3 | `aidocx-s6-test-cases/SKILL.md` | 8 |
| B3 | `aidocx-s7-review/SKILL.md` | 9 |
| B3 | `aidocx-s8-self-iteration/SKILL.md` | 12 |
| B4 | `README.md` | 2 |
| B4 | `ai_workflow/runtime_contracts.py` | 15 |
| B4 | `ai_workflow/stage_s1_input/utils/constants.py` | 1 |
| 第二轮 | `ai_workflow/stage_s1_input/pipeline.py` | 1 |
| 第二轮 | `ai_workflow/conversation_skills.py` | 1 |
| 第二轮 | `ai_workflow/tools/convert_md_to_docx.py` | 1 |
| 第二轮 | `ai_workflow/requirement_reviewer_auto.py` | 1 |
| 第二轮 | `ai_workflow/prompts/requirement_review.md` | 2 |
| 第二轮 | `ai_workflow/s6_xlsx_enhance.py` | 2 |
| 第二轮 | `ai_workflow/prompts/test_point_gen.md` | 4 |
| 第二轮 | `ai_workflow/prompts/flowchart_export.md` | 2 |
| 第二轮 | `ai_workflow/test_case_formatter.py` | 1 |
| 第二轮 | `.cursor/hooks/docx_hook.py` | 4 |
| 第二轮 | `.cursor/skills/aidocx-feedback-logger/SKILL.md` | 1 |
| 第三轮 | `knowledge/public/test_point_library/README.md` | 1 |
| 第三轮 | `governance/design_iter/plans/v7/changes/s7_review_reports_2026_07_09.md` | 4 |
| 第三轮 | `governance/design_iter/plans/v7/changes/s1_5_audit_v3_01_2026_07_09.md` | 1 |
| 第三轮 | `governance/design_iter/plans/v7/q_decision_table.md` | 3 |
| **总计** | **38 个文件** | **~217 处路径替换** |

### Phase 1b: 手工修复（脚本覆盖不到）

| 文件 | 改动 |
|---|---|
| `.cursor/rules/AIDocxWorkFlow.mdc` | 表格 10 行 + 138 行格式说明 + 树状结构 8 段（含 S1 raw 修复） |
| `ai_workflow/conversation_skills.py` | 6 处 Python 裸路径拼接 |
| `ai_workflow/test_case_formatter.py` | 1 处 Python 裸路径拼接 |
| `.cursor/hooks/auto_advance_check.py` | `_stage_dir_path` 函数（96 行） |

### Phase 2: 数据 mv

```
mv "workflow_assets/游戏道具商城系统/「S1 需求评审」/v3.0/raw" \
   "workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」/raw"
```

最终结构：

```
workflow_assets/游戏道具商城系统/
└── v3.0/
    └── 「S1 需求评审」/
        └── raw/
            ├── extracted_images/
            ├── ocr_results/
            ├── extracted_text.md
            └── image_index.json
```

### Phase 3: SSOT 同步

- `DESIGN_AND_EXECUTION_STANDARDS.mdc §2.6` 目录树 + §4.5 STAGE_PATTERNS 注释 + `stage_dir()` 工厂函数

### Phase 4: 验证

- ✅ `python3 -m py_compile` 10 个改动 Python 文件全部通过
- ✅ grep "旧路径模式" 在约束/技能/代码/公共知识库 0 命中
- ✅ 实际目录结构与约束文件描述一致
- ⚠️ 残留（按 DNA §10.5 保留为历史快照）：
  - `CHANGELOG.md` 4 处（v1.0/v2.0 历史快照）
  - `governance/design_iter/plans/v2/q_decision_table_q_audit_001_v2.md` 1 处（v2 历史方案档）
  - `governance/design_iter/plans/v7/audit_input_scripts_skill.md` 1 处（v7 审计档——脚本示例，不影响实际行为）

**v8 启动决策总结**：

- **目录主轴**：先阶段再版本 → **先版本再阶段** ✅
- **执行工具**：Python 脚本（dry-run + execute 两阶段）
- **改动文件总数**：约 42 个
- **路径替换总数**：约 217 处
- **v8 治理档完成**（2026-07-10）：
  - ✅ `governance/design_iter/plans/v8/PLAN.md`（11KB）
  - ✅ `plans/v8/open_questions.md`（v7 §3 遗留 + v8 实战发现 2 条）
  - ✅ `plans/v8/resolved_questions.md`（D-V8-001 ~ D-V8-007 全部闭环）
  - ✅ `plans/v8/decisions.json`（机读决策清单 + execution_summary）
  - ✅ `plans/v8/q_decision_table.md`（从 current/ 迁移）
  - ✅ `current/scripts/rewrite_path_axis.py`（v8 启动脚本）
  - ✅ `CHANGELOG.md [v8]` 章节写入
  - ✅ current/ 已切 v8（v7 audit_input*.md + changes/ 保留作为归档）
  - ⚠️ **未完成（→ v9）**：
    - Q-V9-001：v3.0/raw 与 v3.01 内容重复（resource/ 只有 v3.01）
    - Q-V9-002：INDEX.md v8 章节未加
    - INDEX.md 表格更新 v8 段状态