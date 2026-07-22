# v9 启动决策表（2026-07-10）

> **本档是 v9 启动决策展开**——v8 期间识别 2 个 v9 议题 + 用户新加 1 个 v7 治理层议题（共 3 大议题）。
> **v8 实战发现 2 个议题**（v3.0/v3.01 重复 + INDEX v8 段未加）+ **v7 治理层遗留 3 项**（v7.1/v7.2/v7.3）。

---

## 议题清单

| Q | 主题 | 来源 | 候选 | 决定 |
|---|---|---|---|---|
| Q-V9-001 | v3.0/raw 与 v3.01 重复 | v8 §3.2 实战发现 | A: 重命名 / B: 重跑 / C: 保留 | **A（重命名 v3.0 → v3.01）** |
| Q-V9-002 | INDEX.md v8 段未加 | v8 §3.3 残留 | A: 加 / B: 留 v9 | **A（加 v8 段 + v9 段）** |
| Q-V9-003 | v7.1: 9 阶段 .mdc 同步 | v7 §3 遗留 | A: 跑 v7.1 / B: 留 v9.x | **A（启动 v7.1）** |
| Q-V9-004 | v7.2: S7 审查脚本适配 | v7 §3 遗留 | A: 跑 / B: 留 | **A（启动 v7.2）** |
| Q-V9-005 | v7.3: S8 review_report.json 适配 | v7 §3 遗留 | A: 跑 / B: 留 | **A（启动 v7.3）** |

**用户决定（2026-07-10 AskQuestion）**：
- v9 范围 = 3 议题都跑（all_3_topics）
- v7 治理层在 v9 内推进实质改动

---

## 执行计划（分 4 阶段）

### Phase 1: Q-V9-001 数据修复（最快，立竿见影）

**改动**：
1. `mv workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」/raw/ workflow_assets/游戏道具商城系统/v3.01/「S1 需求评审」/raw/`
2. `rmdir workflow_assets/游戏道具商城系统/v3.0`（清理空目录）
3. `mkdir -p workflow_assets/游戏道具商城系统/v3.01/「S1 需求评审」`

**文件数**：0（只 mv 目录）
**风险**：低（mv 不丢内容，目录原子操作）
**验证**：`ls -la workflow_assets/游戏道具商城系统/v3.01/「S1 需求评审」/raw/`

### Phase 2: Q-V9-002 INDEX.md 更新（1 个文件）

**改动**：
- `governance/design_iter/INDEX.md`：
  - 加 v8 段（"v8 已闭环 / single-issue 修复"）
  - 加 v9 段（"v9 启动 / 数据修复 + INDEX + v7 治理"）
  - 目录结构图更新（v8 加进 plans/）
  - 关键概念"current 软链"补注（v8 实际是 cp 不是软链——与设计意图不符）

**文件数**：1（仅 INDEX.md）
**风险**：低
**验证**：INDEX.md 含 v8 + v9 两段

### Phase 3: Q-V9-003 v7.1 - 9 阶段 .mdc 同步（最复杂）

**改动范围**（基于 v7 §2 第一批输入 15 条 + 第二批 37 条 = 52 条 Q-501~Q-552）：
- 9 份 STAGE_*.mdc + STAGE_S1.5 Clarification.mdc = 10 份
- 各阶段 .mdc 必加 §1.4（LLM 必读材料）+ §1.5（决策 push 块）
- STAGE_S5_TEST_POINTS.mdc 删硬性数量指标
- STAGE_S6_TEST_CASES.mdc 删硬性数值
- STAGE_S7_REVIEW.mdc 改 LLM 写建议
- STAGE_S8_SELF_ITERATION.mdc 删 PASS/FAIL 判决
- JSON 字段统一（`tp_id` / `test_point_type` / `case_id` / `obj_id`）

**文件数**：10 份 STAGE_*.mdc
**风险**：高（破坏 v8 已有路径变更吗？——不冲突，v8 是路径，v7.1 是内容）
**验证**：`grep -c "决策 push" .cursor/rules/STAGE_*.mdc` 应该增加

**注意**：超出本响应红线（10 > 3），需用户明确豁免——已通过 AskQuestion 确认（all_3_topics）

### Phase 4: Q-V9-004 + Q-V9-005 v7.2/v7.3 脚本适配

**改动范围**：
- `ai_workflow/auto_reviewer.py`：4 项指标 → 5 项指标（s4_risk/s4_exception/is_assumed/s4_reference/applies_rule）
- `ai_workflow/self_iteration.py`（旧名 `iteration_aggregator.py`）：重命名 + 字段映射
- 多个 SKILL.md 引用更新

**文件数**：~5 份（auto_reviewer.py / iteration_aggregator.py / 3 份 SKILL.md）
**风险**：中（脚本改了影响 S7/S8 实际行为）
**验证**：`python3 -m py_compile` + `auto_reviewer.py --self-test`

---

## 影响面（先验 §9.4 — 都已 Read/Grep 验证）

### 涉及文件清单（预计 ~17 个）

| Phase | 类别 | 文件 |
|---|---|---|
| P1 | 数据 mv | (0 文件，3 个目录) |
| P2 | 索引 | `governance/design_iter/INDEX.md` |
| P3 | STAGE 规则 | 10 份 STAGE_*.mdc |
| P4 | 代码 | `ai_workflow/auto_reviewer.py` / `iteration_aggregator.py` (重命名为 `self_iteration.py`) |
| P4 | SKILL | `aidocx-s7-review/SKILL.md` / `aidocx-s8-self-iteration/SKILL.md` / `aidocx-s5-test-points/SKILL.md` |
| 共计 | | **~17 个文件 + 3 个目录 mv** |

### 不变更

- v8 已修改的 42 个文件（路径主轴已切完）
- resource/ 目录（v8 决定 keep_resource_old）
- workflow_assets/ 数据（P1 是把 v3.0 内容搬到 v3.01，路径结构调整不是内容调整）

---

## 决策依据（5 问自检 §1）

| 问 | 答 |
|---|---|
| Q1 一致性 | v9 是"数据 + 索引 + 治理"3 议题——不冲突，串行可做 |
| Q2 设计 | v7.1-3 是治 v7 时期的"规则 vs 实际"双轨——是修结构不是补洞 |
| Q3 全局 | 17 文件改动是必要的——v7.1-3 不做则 v7 治理层永远悬空 |
| Q4 约束 vs 知识 | 改 .mdc = 改约束 + 改 .py = 改实现——必须 ask 已问 |
| Q5 人本可审查 | 决策表 + Phase 拆分 + 验证清单——可逐条审查 |

---

## 落档协议执行记录（§9.5）

- **本文件创建于**：governance/design_iter/current/q_decision_table_v9.md
- **创建时机**：本响应决策展开**前**先落档（§9.5 + §9.4 同时满足）
- **改动文件清单**：（待 Phase 1~4 执行后追加）

---

## 执行顺序（按风险/价值排序）

1. **Phase 1**（数据 mv，0 风险）→ ✅ **完成**（v3.0/raw → v3.01/raw）
2. **Phase 2**（INDEX.md，1 文件低风险）→ ✅ **完成**（INDEX.md v8/v9 段 + 目录图 + 引用表）
3. **Phase 3**（v7.1 9 阶段 .mdc，高工作量）→ 🔄 **已启动**（10 份 .mdc 待改）
4. **Phase 4**（v7.2/v7.3 脚本，中风险）→ 🔄 **已启动**（auto_reviewer.py + self_iteration.py 待改）

**单次响应执行范围**（§9.1 红线 3 文件 + §9.1.1 self-test 豁免类推）：
- Phase 1 + 2 = 数据 mv + 1 文件 → ✅ **本响应完成**（红线内）
- Phase 3 = 10 文件 → 🔄 **下个响应分批**（10/3 ≈ 4 批）
- Phase 4 = 5 文件 → 🔄 **后续响应**（v9.1/v9.2）

**实际执行计划**：
- ✅ **本响应（v9 Phase 1+2）**：
  - 4 个 v9 治理档新建（PLAN.md / open_questions.md / resolved_questions.md / decisions.json）
  - 1 个决策表新建（q_decision_table_v9.md）
  - 1 个数据 mv（v3.0 → v3.01）
  - 1 个 INDEX.md 更新
  - current/ 切到 v9
- 🔄 **后续响应（v9.1）**：
  - Phase 3: 9 阶段 .mdc 同步（分 3-4 批）
- 🔄 **后续响应（v9.2）**：
  - Phase 4: v7.2 + v7.3 脚本适配

---

## 落档协议执行记录（§9.5）

- **本文件创建于**：governance/design_iter/current/q_decision_table_v9.md
- **创建时机**：本响应决策展开**前**先落档（§9.5 + §9.4 同时满足）
- **本响应完成（2026-07-10）**：

| 类别 | 改动 | 状态 |
|---|---|---|
| 数据 mv | `workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」/raw/` → `v3.01/.../raw/` | ✅ |
| 索引更新 | `INDEX.md` 加 v8/v9 段 + 目录图 + 引用表 | ✅ |
| 治理档 | `plans/v9/{PLAN,open_questions,resolved_questions,decisions.json}` | ✅ |
| 决策表 | `current/q_decision_table_v9.md`（本文件）| ✅ |
| current 切换 | `current/PLAN.md` 等 4 件套 → v9（v7 audit/changes 保留归档） | ✅ |
| v7.1 启动 | 9 阶段 .mdc 待改（10 文件） | 🔄 |
| v7.2 启动 | auto_reviewer.py 字段映射（4→5 项）| 🔄 |
| v7.3 启动 | self_iteration.py 重命名 + 字段映射 | 🔄 |
| v9 → v10 必传 | 跨阶段引用回归测试 + before_prompt_dna_check.py 适配 | 🔄 |