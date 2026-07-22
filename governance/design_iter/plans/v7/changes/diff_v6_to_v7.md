# v6.2 → v7 决策 diff

> **本文件是 governance 内部版本号差异**——非代码版本号。
> **v6.2 是 DNA 闭环阶段号**（指 v6 版本号下的 §六~§九 4 阶段 self-test 闭环），**v7 是方案版本号**。
> **本文件记录：从 v6.2 闭环状态 → v7 启动状态的决策差异**。

---

## 1. 起点：v6.2 闭环状态（2026-07-05）

v6.2 = DNA v6 版本下的"§六 ~ §九"4 阶段 self-test 闭环：

| 阶段 | 议题 | 状态 |
|---|---|---|
| §六 | dna_decision_persistence self-test | ✅ 已闭环 |
| §七 | feedback_logger self-test + cleanup | ✅ 已闭环 |
| §八 | 5 hook self-test（含 docx_hook bug 发现）| ✅ 已闭环 |
| §九 | docx_hook.py bug 修复 + §9.1.1 豁免条款 + 本档 | ✅ 已闭环 |

**v6.2 闭环产出**（DNA L3 hook 自测试 10/10 覆盖）：
- 11 个 hook 文件全部含 `def self_test() → int` + `--self-test` argv 分支
- DNA_3Q_CHECK.mdc §9.1.1 self-test 豁免条款（4 边界 + 4 失效条件）
- DESIGN_AND_EXECUTION_STANDARDS.mdc §3.7 大文件改动 SOP

**v6.2 未触及**：
- ❌ 9 阶段 `.cursor/rules/STAGE_S*.mdc` 的硬指标残留
- ❌ 12 个 `.cursor/skills/aidocx-*/SKILL.md` 与 .mdc 的双轨问题
- ❌ `ai_workflow/` 11 个 Python 脚本与 SKILL.md 的逻辑闭环
- ❌ SKILL.md 自身 9 阶段逻辑性问题

---

## 2. 终点：v7 启动状态（2026-07-09）

v7 = `.mdc / SKILL.md 9 阶段规则层修复执行` 方案。

**v7 4 件套就位**：
- ✅ plans/v7/PLAN.md（9.9KB / §2 表格 56 行）
- ✅ plans/v7/open_questions.md（13.9KB / Q-501~Q-569 共 69 条）
- ✅ plans/v7/resolved_questions.md（2.6KB / D-701~D-704 启动决策）
- ✅ plans/v7/decisions.json（6.9KB / D-701~D-704 已决 + D-705~D-711 占位）
- ✅ plans/v7/changes/diff_v6_to_v7.md（本档）
- ✅ current 软链切换 → plans/v7

**v7 输入归档**（从根目录 3 份历史审查报告归位）：
- ✅ plans/v7/audit_input.md（27KB / RULE_SKILL 24 条）
- ✅ plans/v7/audit_input_scripts_skill.md（29KB / SCRIPT_SKILL 14 条）
- ✅ plans/v7/audit_input_skill_logic.md（45KB / SKILL_LOGIC 31 条）

**v7 期间跟踪范围**：
- Q-501~Q-569（69 条 P0/P1/P2，全部 v7 主体答完移 resolved_questions.md）
- Q-301 / Q-401 / Q-402（v6.x 闭环——v7 不重开）

---

## 3. 决策差异表（v6.2 → v7）

| 决策点 | v6.2 决策 | v7 决策 | 差异原因 |
|---|---|---|---|
| 治理版本号命名 | "v6.2" 用于 §六~§九 闭环号 | "v7" 用于方案版本号 | 避免与 open_questions.md §v6.2 闭环段同名（混淆）|
| current 软链指向 | v2（50 天未切）| **v7**（2026-07-09 切）| v7 4 件套就位后切 current |
| Q 编号起点 | Q-301/Q-401/Q-402（v6.x）| Q-501~Q-569（v7）| v7 自身决策链 |
| open_questions.md 归属 | v2/open_questions.md §v7 启动版段 | **v7/open_questions.md**（迁移）| v7 启动时 4 件套就位 |
| 索引同步 | INDEX.md / INDEX.json 未列 v7 | **v7 段已加**（2026-07-09）| 治理层完整化 |
| 决策占位 | D-101~D-105（v2 5 主决策）| D-701~D-704（启动）+ D-705~D-769（Q-501~Q-769 占位）| v7 自身决策链 |
| changes/ 目录 | v2/changes/ 空 | **v7/changes/diff_v6_to_v7.md**（决策 diff）| v7 启动就位 |
| 根目录游离文件 | 12 个（含已删文件跟踪）| 11 个（合 4 类）| 根目录治理已落地 |

---

## 4. 治理层影响（v6.2 → v7）

| 维度 | v6.2 状态 | v7 状态 | 影响范围 |
|---|---|---|---|
| **Agent 启动加载** | AGENTS.md + DNA_3Q_CHECK.mdc（DNA 入口） | + DESIGN_AND_EXECUTION_STANDARDS.mdc §3.7 SOP | 不变（v7 是 governance 不是约束）|
| **current 软链读取** | `cat current/open_questions.md` → v2 内容 | `cat current/open_questions.md` → **v7 内容** | Agent 看 current/ 路径会看到 v7 |
| **INDEX 索引查询** | 仅 v1 / v2 / v4 | **+ v7**（v3 仍缺——未补）| Agent 查 INDEX 知道 v7 存在 |
| **决策表归档** | v2/q_decision_table.md + q_decision_table_q_audit_001_v2.md | + **q_decision_table_round2.md** + v2_vs_v7_truth_report.md | v7 启动前的状态澄清 |
| **git 工作树** | 5 个 `D` + 4 个 `??` | 5 个 `D`（删除已 mv）+ 4 个 `??`（新文件：tools/, round2.md, q_audit_001_v2.md, v7/）+ 1 个 `M` v2/open_questions.md | 待 git add -u + git add 同步 |

---

## 5. 不变更项（v6.2 → v7 不动）

- **DNA 三层对位**（L1 AGENTS.md / L2 DNA_3Q_CHECK.mdc / L3 hook）—— 不动
- **9 阶段流水线**（S1 → S1.5 → S2 → S2.5 → S3 → S4 → S5 → S6 → S7 → S8）—— 不动
- **12 份 STAGE_S*.mdc**（`.cursor/rules/`）—— 不动（v7 期间逐条答 Q 修复）
- **13 个 SKILL.md**（`.cursor/skills/`）—— 不动（v7 期间逐条答 Q 修复）
- **ai_workflow/ 11 个 Python 脚本**—— 不动（v7 期间逐条答 Q 修复）
- **v2 主体决策**（D-101~D-105 5 主决策）—— 不动（v2 仍有效，current 切 v7 不代表 v2 失效——v2/open_questions.md §v6.2 闭环段保留）

---

## 6. 已知遗留（→ v8 评估）

- **v3 索引缺失**：INDEX.md / INDEX.json 没列 v3（v3 目录存在但未索引）—— 待 v8 补全
- **git 工作树同步**：5 个 `D` + 4 个 `??` 未同步到 git index —— 待 `git add -u` + `git add`
- **hooks 治理**：2 个 untracked hooks（`dna_decision_persistence_check.py` / `dna_read_before_answer_check.py`）—— 待入 git 或归档
- **Q-501~Q-569 逐条答完**：v7 主体工作量——69 条决策需逐条点头 + 9 阶段 .mdc + 12 SKILL.md 修复

---

## 7. 时间线（v6.2 → v7）

| 日期 | 事件 |
|---|---|
| 2026-07-05 | v6.2 DNA 闭环（§六~§九 4 阶段）完成；CHANGELOG [v6.2] 段写入 |
| 2026-07-08 | v7 目录骨架建立：mv 3 份 audit_input.md + Write PLAN.md |
| 2026-07-09 00:05 | 根目录治理：mv 2 个游离文件 + 创建 ai_workflow/tools/__init__.py + INDEX 加 v7 段 |
| 2026-07-09 00:11 | INDEX.md / INDEX.json v7 段加入 + q_decision_table_round2.md 落档 |
| 2026-07-09 00:23 | v2 vs v7 现状澄清：v2_vs_v7_truth_report.md 落档 |
| 2026-07-09 00:42 | 用户明示 v7 4 件套补齐 + 切 current |
| 2026-07-09 00:53 | v7 4 件套补齐 + changes/ 建 + current 切换 + v2 §v7 启动版段删除 |
| **未来** | v7 主体答 Q-501~Q-569 + 9 阶段 .mdc / 12 SKILL.md / 11 脚本 修复