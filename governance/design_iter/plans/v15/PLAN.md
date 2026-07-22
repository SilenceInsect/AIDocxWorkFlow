# v15 治理方案 — 缺陷模式聚类 + 增强路径论证 + 用例价值评分

> **方案来源**：v14 §3 遗留项 L1 / L2 / L3 + v14 §5 第二阶段 bypass_log 产物（L3 数据基础）
> **与 v14 关系**：v14 落地了第一阶段（必做 4 项）+ 第二阶段（应做 3 项）共 7 项；v15 继承 v14 全部产物，把遗留的"论证型"任务转为"实施型"
> **本档状态**：草案（v15 PLAN.md 首版，等 D-V15-001~005 + P-V15-1~3 拍板）
> **关键约束**：本档遵守 3 栏框架（解决 / 新增 / 遗留）—— L4 缺陷率看板明确推迟 v16

---

## v15 必备 3 栏

### 1. 本次 v15 解决的问题（来自 v14 §3 遗留）

| # | 遗留项 | v15 落地形态 |
|---|---|---|
| L1 | 增强路径分离（S3 轻量/深度版）可行性论证 | 出可行性报告（**§附录 A**） + S3 触发条件决策树 |
| L2 | 用例价值评分（有效性/独立性/可执行性）| 设计 3 维度评分标准 + 在最近 1 个需求上试点 |
| L3 | 缺陷模式自动聚类（跨项目分析管道）| **新建 `ai_workflow/defect_cluster.py`**——消费 S7 RCA + bypass_log，按 `module × rca.type × rca.clause` 三维聚类 |
| ~~L4~~ | ~~缺陷率趋势看板~~ | ❌ **推迟 v16**——依赖 L3 数据积累（需 3+ 项目 bypass_log） |
| ~~L5~~ | ~~8 模块种子 TP 重组~~ | ❌ 永久遗留——v14 已决定不采纳（§附录 D 决议记录）|

### 2. 本次 v15 新增内容

| 新增项 | 来源 | 创新点 |
|---|---|---|
| 缺陷模式聚类器 | v15 主轴 | 从 S7 RCA 三级（stage × type × clause）+ bypass_log 抽取 defect_mode；输出 `defect_mode_latest.json`（聚类结果）+ `defect_mode_trend.json`（跨项目趋势）|
| 增强路径触发决策树 | v14 L1 论证 | S3 轻量版 / 深度版的触发条件（UI ratio + Story 数 + 风险等级） → 出可行性报告 + 嵌入 S2/S3 prompt |
| 用例价值 3 维评分 | v14 L2 试点 | effectiveness（业务覆盖有效性）/ independence（用例独立性）/ executability（可执行性）；每维 1-5 分；总评分 = 加权平均 |
| L3 → v16 看板规划 | v15 占位 | 在 v15 末段产出 v16 L4 看板技术方案稿（含数据源 + 选型 + POC 计划）|

### 3. 本次 v15 仍遗留的问题（→ v16）

| # | 遗留项 | 状态 | 去向 |
|---|---|---|---|
| L4 | 缺陷率趋势看板 | ⏳ 依赖 L3 数据积累（≥ 3 项目 bypass_log）| → v16（v15 末段出技术方案稿） |
| L6 | 用例价值评分全量自动化 | ⏳ 试点数据决定是否扩大 | → v16 |
| L7 | 缺陷模式 → Prompt 反哺闭环 | ⏳ 需聚类结果稳定 | → v16 |
| L8 | 增强路径触发条件实际验证 | ⏳ 需 1 个真实需求跑通 | → v16 |

---

## §5 实施路线（v15 三阶段）

### 阶段 1：主轴 L3 缺陷模式聚类（2-3 周，必做）

| # | 任务 | 产出物 | 文件 |
|---|---|---|---|
| 1 | Read S7 RCA 完整 schema + bypass_log 字段 | 数据契约清单 | — |
| 2 | 新建 `ai_workflow/defect_cluster.py`（消费 RCA + bypass_log + module × type × clause 三维聚类 + self-test 5 cases）| 脚本 + self-test | `ai_workflow/defect_cluster.py` |
| 3 | S7 SKILL.md 追加 §S7 缺陷模式输出段 | 文档 | `.cursor/skills/aidocx-s7-review/SKILL.md` |
| 4 | 在最近 1 个需求 workflow_assets/ 上跑一次（生成 defect_mode_latest.json + trend.json）| ❌ **BLOCKED**——S7 从未在 workflow_assets/ 执行过；详见 `governance/design_iter/current/v15_L3_blocker.md` | — |

### 阶段 2：L1 增强路径论证 + L2 用例价值评分标准（1-2 周，应做）

| # | 任务 | 产出物 |
|---|---|---|
| 5 | L1 可行性报告（外部方案 §4.2 修订版为基础 + 本次决策树设计）| `governance/design_iter/plans/v15/A1_enhanced_path_feasibility.md` |
| 6 | L1 触发决策树嵌入 S2/S3 prompt | ✅ 已完成——S3 §23 加决策树图示 + S2 §409 加 `s3_mode_reasons` 字段 |
| 7 | L2 用例价值评分标准 + 试点（最近 1 个需求 50 个 TC 打分）| `governance/design_iter/plans/v15/A2_case_value_scoring.md` + `workflow_assets/<req>/<v>/case_value_pilot.json` |

### 阶段 3：v16 规划 + 经验归档（并行论证）

| # | 任务 | 产出物 |
|---|---|---|
| 8 | L4 缺陷率看板技术方案稿（MCP 工具 vs CLI vs Web）| `governance/design_iter/plans/v15/A3_dashboard_tech_design.md` |
| 9 | v15 经验归档到 `knowledge/project_local/v15_experience/` | 经验库 |
| 10 | v15 自检（按 §10 三问 + §3.7 SOP）| `governance/design_iter/plans/v15/SELF_CHECK.md` |

---

## §6 关键指标基线（v15 目标）

| 指标 | v14 末基线 | v15 目标 | 度量方式 |
|---|---|---|---|
| 缺陷定位耗时 | 手工 grep RCA + module 维度 | 自动化（≤ 30 秒）| defect_cluster.py run time |
| 缺陷模式跨项目可比 | 不可比（无 schema） | defect_mode_trend.json 输出 | 文件存在 + 维度齐全 |
| 增强路径决策 | 全靠 LLM 主观 | 决策树 + ui_ratio 量化 ⚠️ BLOCKED | S2 输出 `s3_mode_recommend` 字段（需真实数据验证）|
| 用例价值评分 | 无 | 试点 50 个 TC 全 3 维评分 ⚠️ BLOCKED | case_value_pilot.json（需 S6 数据 + D-V15-003 拍板）|

---

## 附录 A：L1 增强路径论证（已采纳）

> **状态**：已采纳——基于 `governance/design_iter/plans/v15/A1_enhanced_path_feasibility.md` v1.0（2026-07-16）
> **D-V15-002 拍板记录**：三档阈值 UI ratio < 0.30 → 轻量版 / 0.30-0.50 → 标准版 / > 0.50 → 深度版；P0 强制深度版

## 附录 B：L2 用例价值评分标准（已采纳）

> **状态**：已采纳——基于 `governance/design_iter/plans/v15/A2_case_value_scoring.md` v1.0（2026-07-16）
> **D-V15-003 拍板记录**（见 PLAN.md §附录 D）

| 维度 | 定义 | 权重 |
|---|---|---|
| effectiveness（业务覆盖有效性）| 1-5 分：核心路径 5 → 装饰细节 1 | 0.5 |
| independence（用例独立性）| 1-5 分：完全独立 5 → 强依赖 1 | 0.2 |
| executability（可执行性）| 1-5 分：5 分钟内 5 → 难自动化 1 | 0.3 |

**分级阈值**：4.0+ 高价值（必修）/ 3.0-3.9 中价值（应修）/ 2.0-2.9 低价值（可改）/ <2.0 极低（可砍）

**试点**：最近 1 个 ≥ 50 TC 需求，1 周，QA + Agent 双重校验

## 附录 C：L3 缺陷模式聚类技术方案（已采纳）

> **状态**：已采纳——基于 `defect_cluster.py` 实现（2026-07-16）
> **D-V15-001 拍板记录**：defect_cluster.py 已实现，默认输出 defect_mode_latest.json + defect_mode_trend.json（跨项目需 ≥ 3 项目触发）

## 附录 D：v15 决策拍板位

> **D-V15-001**：[x] 已拍板（2026-07-16）——采纳附录C schema，defect_cluster.py 已实现，默认输出 defect_mode_latest.json + defect_mode_trend.json（跨项目≥3项目触发）
> **D-V15-002**：[x] 已拍板（2026-07-16）——采纳 A1 §2 三档阈值：UI ratio < 0.30 → 轻量版 / 0.30-0.50 → 标准版 / > 0.50 → 深度版；P0 强制深度版
> **D-V15-003**：[x] 已拍板（2026-07-16）——采纳 A2 v1.0 方案
>   - D-V15-003-A：[x] 3 维度采纳（effectiveness / independence / executability）
>   - D-V15-003-B：[x] 加权方案采纳（0.5 / 0.3 / 0.2）
>   - D-V15-003-C：[x] 分级阈值采纳（4.0/3.0/2.0）
>   - D-V15-003-D：[x] 试点范围采纳（≥ 50 TC，1 周，QA + Agent 双重）
> **D-V15-004**：[x] 已拍板（2026-07-16）——v15 全阶段完成后做一次自检（按 §10 三问 + §3.7 SOP），产出 SELF_CHECK.md
> **D-V15-005**：[x] 已拍板（2026-07-16）——v15 阶段 1/2/3 全部完成后 + 至少 3 个项目的 bypass_log + review_report 积累够 → 进入 v16

## 附录 E：v15 执行前提（P-V15-1~3）

> **P-V15-1**：v15 §5 阶段 1 L3 数据基础（最近 1 个需求 workflow_assets/ 真实数据）是否准备好
> **P-V15-2**：最近 1 个需求的 S7 RCA 三级字段是否齐全（rca.stage/type/clause）
> **P-V15-3**：QA 人工评分时间是否预留（≥ 50 TC × 3 维度 = 150 次评估）

---

## 版本与状态

| 项 | 值 |
|---|---|
| **版本** | v15（首版） |
| **状态** | 草案 / 等用户拍板 D-V15-001~005 + P-V15-1~3 |
| **继承来源** | v14 §3 遗留 L1/L2/L3 + v14 §5 bypass_log 产物 |
| **推迟项** | L4（→ v16）+ L6/L7/L8（→ v16） |
| **永久遗留** | L5（v14 已决定不采纳） |

---

## 落档协议执行记录

| 步骤 | 状态 |
|---|---|
| §9.5 决策表先 Write | ✅ `q_decision_table_v15_launch_2026_07_16.md` |
| 用户拍板候选 A | ✅ 已确认 |
| §9.4 先验（Read v14 PLAN.md §3 + §4 触发表 + INDEX.md） | ✅ |
| §3.7 SOP（新建 ≤ 400 行文件 Write + 验证） | ⏳ 本档 152 行 ≤ 400 → Write 后 Read 验证 |
| §10.5 边界说清 | ✅ L4 推迟 v16 / L5 永久遗留 / L1-L3 范围明确 |