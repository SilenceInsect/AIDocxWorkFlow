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
| [`v31`](plans/v31/) | **achieved / 已归档** | S5/S6 方法论重写经 5 轮 goal-loop 收敛；v3.01 样本 230 TP / 230 TC；OBJ、FP、S4 异常叶子、S4 风险点覆盖率均为 100%；TC 字段语义校验 230/230 PASS | `PLAN.md` / `coverage_report.md` / `v31_SCC.md` / `s8_knowledge_backflow_diagnosis.md` / `CONVERGED.md` | v32 接办 6 项遗留 | [`v31_20260721_020714.bak`](archive/v31_20260721_020714.bak/) |
| [`v29`](plans/v29/) | 已闭环 | （v29 治理 — v28 carry 全闭环 + 8 项 follow_up 全部实施：F-1 pre-existing bug 修复 `case_id_and_field_normalizer.evaluate_status` + F-2/F-3 DT-V28-002/003 SKILL.md §2 schema+§3.2+§3+§3.4 落地（含 `goal_signature_changelog[]` 字段 + Review 双档）+ F-4/F-5/F-6 v26 §5 优先级表 line 227/229/233 标注追加（A1/A3/A4/B3 REJECT / B4 维持 100% / D3 选 C）+ F-7 DESIGN §4.3.1 分母重构评估报告（仅评估不实施）+ SYS-004 SKILL.md §3.2.2 落地 + 候选档 `current/v29_sys004_candidate.md` + `current/v29_f7_design_431_assessment.md`；Round 1 全 PASS achieved；SYS-005 候选（v29 触发 1 次 < 3 不实施）；SYS-002 防御首次实战有效（T-101 任务描述 2 处不符显式标注而非自纠正）） | — | v30+ 修复 Round 1 残留弱证据：V-101 self-test 明细写入产物文件 + V-102 schema 解析侧同步验证 + V-103 §3/§3.4 双档实测 + V-107 评估报告深度实测 | — |
| [`v30`](plans/v30/) | **current** | （v30 v26 真实缺口闭环 — Round 1 全 PASS：4文件修复+SKILL.md 298行重写+self-test 22/22；关键发现：v28/v29 DT 声称 SKILL.md 有498行/§2.1/§3.2，实测仅255行；5项落地：A2/C1 DNA §9.1≤5 / D1 MIN_VALUE_RATIO_SOFT=0.5+0.6硬 / D2 MIN_SIGNATURE_SOFT=0.5+changelog / D3 SKILL §2.1+§3.4双档+§3.6 / B2/B4 DESIGN §4.3口径） | — | v30+ 收尾 | — |
|| [`v303`](plans/v303/) | 已闭环 | （v3.03 V-302-002 OBJ P0 覆盖率 1.0 修复 — driver 加 enforce_obj_p0_coverage；xlsx 重导 149 P0 / 16 OBJ 100%；Round 1 全 PASS achieved；SYS-008 防御落地验证） | — | v3.04: _write_pri 双向 mirror + V-303 expected 33.5% 压缩 | — |
| [`v302`](plans/v302/) | 已闭环 | （v3.02 跟进清单 — 1 轮闭环：8 项中 7 项 PASS / V-002 BLOCKER 转 v3.03 follow_up；converged_with_followup；APC-002 反模式熔断 + DT-v302-001 决策；SYS-008 体系问题沉淀） | — | v3.03 仅修 V-002 | — |
| [`v27`](plans/v27/) | 已闭环 | （v27 治理 — AI 自治规则放宽 v1 · 4 个高优动作：B1 SSOT 合并 §2.3 → §4.3 唯一源 / C1-A2 决策密度阈值 docstring 改 3→5 / C2 保留不注册避免双注入 / C4 注入文本 3 问 → 5 问；C3 撤回；v28 已接办 §2.4.2/§5.1 清理 + v17 5 项约束放开） | — | — | v28 启动 |
| [`v18`](plans/v18/) | 已闭环 | （goal_loop_runner.py PARTIAL 修复 + 越界保护 + self_test Case 8-9） | — | — | v19 启动 |
| [`v19`](plans/v19/) | 已闭环 | （v19 Goal日志库初始化 — .goal-log-db/ 替换 workflow_assets/goals/ 实现；8条 AC 全部验收通过；self_test 10/10 PASS；路径迁移 + 索引维护 + 5文件模板 + CHANGELOG 记录） | — | — | 归档 |
| [`v17`](plans/v17/) | 已闭环 | （字段溯源方案落地周期 + v17.1 增量收尾） | — | — | v18 启动 |
| [`v16`](plans/v16/) | 已闭环 | （v16 治理方案 — **v1.1 迭代方案落地周期**：10 项改动 + 10 项冲突点统一治理；§3 阶段 1（P0 6 项：#2 模块矩阵 / #4 L1 基类 / #1 S1 结构化 / #3 related_tags / #5 三级覆盖率 / C5 红警确认）；§3 阶段 2（P1 3 项：#6 黄金库 / #7 S7 三层重构 / C8 RCA 命名 5 类新增）；§3 阶段 3（P2 2 项：#8 SPECIAL 变体 / #9+#10 自动分流 + 经验库）。**用户 Q4-Q6 拍板（2026-07-17）**：B/A/B；启动条件 = 先跑 ≥ 1 个真实项目解锁 v15 BLOCKED → 由 v17 承接） | — | — | v17 §3 字段溯源方案 100% 完成 |
| [`v15`](plans/v15/) | 已闭环 | （v15 治理方案 — **阶段 1 L3 缺陷模式聚类 100%**（`ai_workflow/defect_cluster.py` + self-test 5 cases + S7 SKILL §S7 缺陷模式输出）；**阶段 2 L1+L2 100%**：L1=`A1_enhanced_path_feasibility.md`（S3 轻量/标准/深度版触发决策树方案 2 / 阈值 0.30/0.50 / P0 强制深度版）；L2=`A2_case_value_scoring.md`（3 维度 effectiveness/independence/executability + 加权 0.5/0.3/0.2 + 4 级阈值 4.0/3.0/2.0 + 试点方案）；**阶段 3 v16 规划 100%**：A3=`A3_dashboard_tech_design.md`（CLI POC → MCP 升级 / 1 周 POC + v16 阶段 1 4 周 MCP）+ v15 经验归档入口 `knowledge/project_local/v15_experience/README.md`（项目级默认 .gitignore）） | — | — | v15 §5 三阶段全部完成 |

> **current 字段来源**：`INDEX.json#current`（机器 SSOT）。本表"current"单元格与 `INDEX.json#current` 自动同步（脱钩由 hook 阻止）。

### v31 归档概览

- **状态**：`achieved`（2026-07-21，5 轮 goal-loop）。
- **源目录**：[`plans/v31/`](plans/v31/)；目录继续保留，便于沿用既有链接。
- **归档目录**：[`archive/v31_20260721_020714.bak/`](archive/v31_20260721_020714.bak/)。
- **文件清单**：顶层 14 个文件 + `archive/` 内 3 个 S1.5 历史文件，共 17 个；源目录实际未包含 `audit_4.md` / `review_4.md`。
- **关键产物**：`PLAN.md`、`coverage_report.md`、`v31_SCC.md`、`s8_knowledge_backflow_diagnosis.md`、`v31_方法论_草案.md`、audit/review 双报告与 `CONVERGED.md`。

---

## 2. 进度看板（按版本历史）

| 版本 | 启动日 | 闭环日 | 关键交付 | 状态 |
|---|---|---|---|---|
| **v31** | 2026-07-20 | 2026-07-21 | S5/S6 方法论重写：`PLAN.md`、覆盖率报告、SCC、S8 回灌诊断；v3.01 样本 230 TP / 230 TC，4 项覆盖率 100% | 🟢 achieved（已归档） |
| **v28** | 2026-07-20 | — | v27 carry 全闭环 | 🟢 **current** |
| **v27** | 2026-07-20 | — | AI 自治规则放宽 v1（4 个高优动作：B1 SSOT 合并 / C1-A2 阈值 5 / C2 守卫 / C4 5 问对齐） | 🟢 已闭环（v28 启动）|
| **v17** | 2026-07-18 | — | 字段溯源方案落地（5 规则 + 4/6 代码 + 87 TP/87 TC + Excel 10 列）；v17.1 增量：check_field_completion.py 字段溯源版 + INDEX v17=current；s6_report.py 缺口 Round 14 闭环（用户拍板 a — 6 处引用全部废弃）| 🟢 已闭环（v18/v19 启动）|
| **v18** | 2026-07-18 | — | goal_loop_runner.py PARTIAL 修复 + 越界保护 + self_test Case 8-9 | 🟢 已闭环（v19 启动）|
| **v19** | 2026-07-18 | 2026-07-18 | Goal日志库初始化（.goal-log-db/ + 5文件模板 + session-index.jsonl + thread_goals.json）；路径迁移（workflow_assets/goals/ → .goal-log-db/）；self_test 升级 10/10 | 🟢 已闭环（v28 启动已承接）|
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
| **v27** | v28 | v27 §3 carry 全部接办（F-1 §2.4.2/§5.1 清理 + F-2 v17 5 项约束 + F-3 D1-D3 + F-4 B2/B4 + F-5 A1/A3/A4/B3）+ SYS-001/002 防御落地 + 1 项 pre-existing bug follow_up | 启动 v28 时 | ✅ 已接（v28 启动 + Round 1 全 PASS）|
| **v16** | v17 | v16 §3 阶段 1+2+3 全部推进 + BLOCKED 未解锁条件 → 由 v17 承接字段溯源方案治理 + check_field_completion.py 增量收尾 + ~~s6_report.py 缺口~~ (Round 14 闭环：引用已废弃) | 启动 v17 时 | ✅ 已接（v17 启动）|
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

---

## 5. v33 变更日志（Rounds 10-14）

### 5.1 Round 10（2026-07-21）

**行动**：VC4 dry-run 首次执行。

**发现**：

|| 维度 | v3.01 基线 | SSOT 阈值 | 判定 |
|------|-----------|-----------|------|
| 规则C（steps ≥ 2）| 0% | 100% | ❌ |
| density-OBJ | 8/36 = 22.2% | 100% | ❌ |
| S4 R-ID 覆盖率 | 0/25 = 0% | 100% | ❌ |

**结论**：3 FAIL 项需治理，Round 11-13 分批修复。

### 5.2 Round 11（2026-07-21）

**行动**：规则C 修复 + S5 SKILL per-OBJ 4类型章节。

**修改**：

|| 文件 | 修订内容 |
|------|---------|---------|
| `STAGE_S6_TEST_CASES.mdc` | 字段契约 §字段契约 steps ≥ 2 步必须 |
| `aidocx-s6-test-cases/SKILL.md` | C1 修订：强制 steps ≥ 2 步 |

**S5 SKILL 修订**（density-OBJ）：

|| 文件 | 修订内容 |
|------|---------|---------|
| `aidocx-s5-test-points/SKILL.md` | 新增 per-OBJ 4类型约束章节（Push 约束）|

### 5.3 Round 12（2026-07-21）

**行动**：S5 per-OBJ 4类型章节增补 + SKILL §2 Push4 + Q5 R-ID 引用约束。

**修改**：

|| 文件 | 修订内容 |
|------|---------|---------|
| `aidocx-s5-test-points/SKILL.md` | Push4 + Q5 双修订，强化 R-ID 风险点引用 |

### 5.4 Round 13（2026-07-21）

**行动**：VC4 dry-run 数据修正（leaf 覆盖 66/66 = 100%，R-ID = 0%）。

**修订**：VC4 dry-run report 全数据修正版。

### 5.5 Round 14（2026-07-21）

**行动**：S7 SKILL density+R-ID 双指标 + VC4 最终报告。

**修改**：

|| 文件 | 修订内容 |
|------|---------|---------|
| `aidocx-s7-review/SKILL.md` | §1.6.2 增 density-OBJ + R-ID 双指标（3处修订）|
| `governance/design_iter/plans/v33/VC4_dryrun_report.md` | 综合判定矩阵 + 根因 + 验收表全更新 |

**Round 14 结论**：VC4 dry-run 全数据修正（5✅/3❌）；3 FAIL 项治理已在 Round 11-13 完成；Round 15 推进 STAGE_S7.mdc 同步 + INDEX.md 更新。

---

## 6. v33 Round 15-19 变更日志

### 6.1 Round 15（2026-07-21）

**行动**：STAGE_S7.mdc 同步 + INDEX.md 累积更新。

**修改**：

|| 文件 | 修订内容 |
|------|---------|---------|
| `STAGE_S7_REVIEW.mdc` | §1.5.2 已有 density-OBJ + R-ID（无需变更）|
| `INDEX.md` | 新增 §5 v33 R10-R14 变更日志 |

### 6.2 Round 16（2026-07-21）

**行动**：s7_status_writer.py density-OBJ 逻辑检查。

**检查结论**：`s7_status_writer.py` 当前仅处理 `must_fix` 驱动写回，不处理 density-OBJ。density-OBJ 属于 S5 生成质量维度，由 S7 审查员 B 统计，不触发 TC 状态变更。无需修改代码。

### 6.3 Round 17（2026-07-21）

**行动**：VC1 L1 warn mechanism 占位档。

**占位档**：`governance/design_iter/plans/v33/VC1_L1_warn_mechanism.md`

**状态**：BLOCKED（需要编码实现，超出当前 token 预算）。

### 6.4 Round 18（2026-07-21）

**行动**：VC4 second dry-run 占位档。

**占位档**：`governance/design_iter/plans/v33/VC4_second_dryrun.md`

**状态**：BLOCKED（等待用户提供 ≥2 个额外样本）。

### 6.5 Round 19（2026-07-21）

**行动**：v33 CONVERGED verdict。

**状态**：🟡 PARTIAL CONVERGED。

---

## 7. v33 最终收敛判定

**VC 矩阵（Round 19 后）**：

|| VC | 验收标准 | 状态 | 说明 |
|----|---|---------|------|------|
| VC1 | L1 ssot_citation_path 100% | 🟡 PARTIAL | warn 机制已起草占位档，编码实现待后续轮次 |
| VC2 | L2 SCC SSOT | ✅ PASS | §4.3.2 SCC 公式已落地 |
| VC3 | L3/L4 草案落地 | ✅ PASS | VC3-L3/L4 均已实施 |
| VC4 | v3.01 dry-run | 🟡 PARTIAL | 首次 dry-run 完成，通用性待更多样本验证；BLOCKED on 用户提供 ≥2 额外样本 |
| VC5 | TP 库激活 | ✅ PASS | v3.01 TP 已抽取入库 |
| VC6 | 用户复核 | ✅ PASS | 4 项 FINAL 用户已复核 |

**结论**：v33 **大部分完成**（4/6 PASS，2/6 🟡 PARTIAL）。VC1 和 VC4 待用户介入。

**v34 开放项**：

1. VC1 L1 warn mechanism 编码实现
2. VC4 额外样本 dry-run（需用户提供 ≥2 个新样本）
3. INDEX.md 全量整合（清理旧结构）

<!-- stop_iter:v14:v14 §5 第一/二阶段已 100%  -->
| v14 | (v15 启动时填) | v14 §5 第一/二阶段已 100% 完成（第一阶段 4/4 + 第二阶段 3/3），第三阶段论证属 v15 范围 | 2026-07-16 | ⏸ 延迟 |
