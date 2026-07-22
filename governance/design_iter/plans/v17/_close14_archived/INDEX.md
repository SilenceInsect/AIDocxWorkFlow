# AIDocxWorkFlow 方案迭代总览

> **定义**：**版本迭代落地进度**记录 + **版本交接**的总览表。
> **触发时机**（自动/手动均触发）：
> 1. **主动停止**（用户明说"停了 / 暂停迭代"）
> 2. **完整迭代**（v{N} 闭环 / 全部 Q 已 resolve）
> 3. **切换迭代版本**（执行 `new` / `rollback` / `switch` 命令）
>
> **详情**：见 [`plans/v{N}/PLAN.md`](plans/)（每个方案自己维护"解决 / 新增 / 遗留"3 栏）。

---

## 1. 当前生效 + 进度

| 版本 | 状态 | 进度 | 关键交付 | 下一动作 | 接手 |
|---|---|---|---|---|---|
| [`v19`](plans/v19/) | **current** | （v19 Goal日志库初始化 — .goal-log-db/ 替换 workflow_assets/goals/ 实现；8条 AC 全部验收通过；self_test 10/10 PASS；路径迁移 + 索引维护 + 5文件模板 + CHANGELOG 记录） | — | — | 归档 |
| [`v18`](plans/v18/) | 已闭环 | （goal_loop_runner.py PARTIAL 修复 + 越界保护 + self_test Case 8-9） | — | — | v19 启动 |
| [`v17`](plans/v17/) | 已闭环 | （字段溯源方案落地周期 + v17.1 增量收尾） | — | — | v18 启动 |
| [`v16`](plans/v16/) | 已闭环 | （v16 治理方案 — **v1.1 迭代方案落地周期**：10 项改动 + 10 项冲突点统一治理；§3 阶段 1（P0 6 项：#2 模块矩阵 / #4 L1 基类 / #1 S1 结构化 / #3 related_tags / #5 三级覆盖率 / C5 红警确认）；§3 阶段 2（P1 3 项：#6 黄金库 / #7 S7 三层重构 / C8 RCA 命名 5 类新增）；§3 阶段 3（P2 2 项：#8 SPECIAL 变体 / #9+#10 自动分流 + 经验库）。**用户 Q4-Q6 拍板（2026-07-17）**：B/A/B；启动条件 = 先跑 ≥ 1 个真实项目解锁 v15 BLOCKED → 由 v17 承接） | — | — | v17 §3 字段溯源方案 100% 完成 |
| [`v15`](plans/v15/) | 已闭环 | （v15 治理方案 — **阶段 1 L3 缺陷模式聚类 100%**（`ai_workflow/defect_cluster.py` + self-test 5 cases + S7 SKILL §S7 缺陷模式输出）；**阶段 2 L1+L2 100%**：L1=`A1_enhanced_path_feasibility.md`（S3 轻量/标准/深度版触发决策树方案 2 / 阈值 0.30/0.50 / P0 强制深度版）；L2=`A2_case_value_scoring.md`（3 维度 effectiveness/independence/executability + 加权 0.5/0.3/0.2 + 4 级阈值 4.0/3.0/2.0 + 试点方案）；**阶段 3 v16 规划 100%**：A3=`A3_dashboard_tech_design.md`（CLI POC → MCP 升级 / 1 周 POC + v16 阶段 1 4 周 MCP）+ v15 经验归档入口 `knowledge/project_local/v15_experience/README.md`（项目级默认 .gitignore）） | — | — | v15 §5 三阶段全部完成 |

> **current 字段来源**：`INDEX.json#current`（机器 SSOT）。本表"current"单元格与 `INDEX.json#current` 自动同步（脱钩由 hook 阻止）。

---

## 2. 进度看板（按版本历史）

| 版本 | 启动日 | 闭环日 | 关键交付 | 状态 |
|---|---|---|---|---|
| **v17** | 2026-07-18 | — | 字段溯源方案落地（5 规则 + 4/6 代码 + 87 TP/87 TC + Excel 10 列）；v17.1 增量：check_field_completion.py 字段溯源版 + INDEX v17=current + s6_report.py 缺口识别 | 🟢 已闭环（v18/v19 启动）|
| **v18** | 2026-07-18 | — | goal_loop_runner.py PARTIAL 修复 + 越界保护 + self_test Case 8-9 | 🟢 已闭环（v19 启动）|
| **v19** | 2026-07-18 | 2026-07-18 | Goal日志库初始化（.goal-log-db/ + 5文件模板 + session-index.jsonl + thread_goals.json）；路径迁移（workflow_assets/goals/ → .goal-log-db/）；self_test 升级 10/10 | 🟢 **current** |
| **v16** | 2026-07-17 | 2026-07-18 | v1.1 迭代方案落地周期（10 项改动 + 10 项冲突点） | 🟢 已闭环（v17 启动）|
| **v15** | 2026-07-16 | 2026-07-17 | L3 缺陷模式聚类 + L1+L2 方案 + v16 规划 | 🟢 已闭环（启动 v16）|
| **v14** | 2026-07-... | — | INDEX.md 重定义 + 同步机制 | 🟢 已闭环 |
| v13 | ... | 2026-07-... | ... | ⚪ 已闭环 |
| v9 | 2026-07-10 | 2026-07-... | 数据 + 索引 + v7 治理重接 | ⚪ 已闭环 |
| v8 | 2026-07-10 | 2026-07-... | 目录主轴变更（single-issue 修复已闭环） | ⚪ 已闭环 |
| v7 | 2026-07-08 | — | .mdc/SKILL.md 9 阶段规则层修复 | 🟡 治理层悬空（→ v9 重接） |
| v4 | ... | — | 5 决策占位 | 🟡 草案（Q-401~Q-406 待拍板） |
| v3 | ... | — | — | ⚪ 仅目录存在 / 未入 json |
| v2 | 2026-06-17 | — | 5 决策回答 + 4 步迁移 | 🟡 5 Q-001~005 待拍板 |
| v1 | 2026-06-17 | 2026-06-17 | 规则体系重构 + 3 栏框架 | ⚪ 已被 v2 取代 |
| v10 / v11 / v12 | ... | — | — | ⚪ 仅目录存在 / 未入 json |

> **状态枚举**：🟢 current / 🟡 草案或运行中 / ⚪ 已闭环或仅目录存在
> **数据来源**：`plans/v{N}/decisions.json` + `INDEX.json#plans[]`（脱钩由 hook 阻止）。

---

## 3. 交接承诺（v{N} → v{N+1}）

| 来源版本 | 目标版本 | 关键交付项 | 截止 | 状态 |
|---|---|---|---|---|
| **v16** | v17 | v16 §3 阶段 1+2+3 全部推进 + BLOCKED 未解锁条件 → 由 v17 承接字段溯源方案治理 + s6_report.py + check_field_completion.py 增量收尾 | 启动 v17 时 | ✅ 已接（v17 启动）|
| **v15** | v16 | v15 §5 三阶段全部完成 + 阶段 1 任务④ BLOCKED（待解锁）+ v15 §A.3 dashboard 设计 | 启动 v16 时 | ✅ 已接（v16 启动）|
| **v14** | v15 | Q-V15-001（plans 列表重生成）+ INDEX.md 4 段新结构落地 | 启动 v15 时 | 🟡 待接 |
| v9 | v10 | 数据契约 + 索引协议（已答 D-V9-001~005） | — | ✅ 已接（v10 目录存在） |
| v7 | v9 | 治理层重接（v7 悬空 → v9） | 2026-07-10 | ✅ 已接 |
| v1 | v2 | 10 个 Q-XXX 遗留 | 2026-06-17 | ✅ 已接 |

> **交接状态**：🟡 待接 / ✅ 已接 / ❌ 退回 / ⏸ 延迟
> **新交接**：执行 `python3 governance/design_iter/scripts/design_iter.py complete_iter <vN>` 自动写入本段。

---

## 4. 触发与维护

### 4.1 触发命令

| 时机 | 命令 | 落地动作 |
|---|---|---|
| **主动停止** | `python3 governance/design_iter/scripts/design_iter.py stop_iter [reason]` | §2 把当前 current 行"状态"改"🟡 暂停"，§3 标记当前 → 下一版交接"⏸ 延迟" |
| **完整迭代** | `python3 governance/design_iter/scripts/design_iter.py complete_iter <vN>` | §2 新增 v{N} 行"已闭环"+ §3 新增 v{N}→v{N+1} 交接行"🟡 待接" |
| **切换迭代版本** | `python3 governance/design_iter/scripts/design_iter.py switch <vN>` | §1 改 current + §2 加 v{N-1} 历史行（状态"已闭环"）+ §3 标记交接"✅ 已接" |

### 4.2 同步钩子（防脱钩）

- `.cursor/hooks/index_landing_hook.py`（afterFileEdit）——监听 `governance/design_iter/**` 改动，自动同步：
 - `INDEX.json#current` ↔ `INDEX.json#updated_at`
 - `INDEX.json#plans[]` ↔ `plans/` 实际目录
 - `INDEX.md §1 当前生效 current 单元格` ↔ `INDEX.json#current`
- **不维护** INDEX.md §2/§3/§4（人写，不爬）——避免改人写的内容

### 4.3 详细引用

- CLI 6 子命令（含本次新增 3 个）：见 [`scripts/design_iter.py`](scripts/design_iter.py)
- 3 栏框架 / 软链 vs cp 模式：见 [`README.md`](README.md)
<!-- stop_iter:v14:v14 §5 第一/二阶段已 100%  -->
| v14 | (v15 启动时填) | v14 §5 第一/二阶段已 100% 完成（第一阶段 4/4 + 第二阶段 3/3），第三阶段论证属 v15 范围 | 2026-07-16 | ⏸ 延迟 |
