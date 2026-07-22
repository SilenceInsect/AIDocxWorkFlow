# AIDocxWorkFlow Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed (2026-07-21 — DNA 生态下线)
- **DNA 文档与 5 配套 hook 全删**（用户拍板"删掉DNA"）—— `.cursor/rules/DNA_3Q_CHECK.mdc`（491 行规则档）+ 7 个 hook 实现（`before_prompt_dna_check.py` / `project_dna_inject.py` / `dna_decision_density_check.py` / `dna_decision_persistence_check.py` / `dna_read_before_answer_check.py` / `dna_violation_check.py`）
- **hooks.json** 5 处 DNA 注册项清除（sessionStart 1 处、beforeSubmitPrompt 1 处、sessionEnd 4 处）
- **8 个文档引用同步清理**：`AGENTS.md`（关键引用表减 1 行）、`README.md`（hooks 列表 -4 / rules 列表 -1）、`MODULES.md`（无引用，已验）、`.cursor/hooks/README.md`（`## dna_decision_density_check.py 详解`整章 51 行删除）、`.cursor/skills/goal-loop/SKILL.md`（§3.2 + §10.5 引用改）、`ai_workflow/runtime_contracts.py`（`GLOBAL_RULES` 减 1 项）、`install.sh`（DNA 自检段 + hook 列表减 2）、`.cursor/rules/product_format_rules.yaml`（referenced_by 减 1 项 + 头注释删 1 行）
- 历史 lineage 段（v30 / v20 等已闭环条目）保留不动——审计铁律

- **2026-07-21 — v31 achieved**：完成 S5/S6 方法论重写 5 轮收敛，归档 `PLAN.md`、`coverage_report.md`、`v31_SCC.md`、`s8_knowledge_backflow_diagnosis.md`、双报告与 `CONVERGED.md` 至 `governance/design_iter/archive/v31_20260721_020714.bak/`。

### Changed (v18.2 — S1/S1.5/S2 三阶段对齐需求拆解规范 · 2026-07-20)

#### S2 产出模版规范化（v18.3）

- `knowledge/public/module_templates/s2_output_template.md`（v18.3 新建）—— S2 阶段产出固定模版，定义 backlog.json / backlog.md / requirement_objects.json 的标准化结构、必填字段、枚举值、验收检查清单
  - §1 backlog.json 完整结构（meta / summary / priority_epics / risk_seeds / confirmed_boundaries / epics / stories / feature_points）
  - §2 backlog.md 完整结构（版本信息 / Epic 统计 / 测试时序 / 风险种子 / 确认边界）
  - §3 requirement_objects.json 完整结构（Object 9 标准字段 / FP 4 字段 / 派生链）
  - §4 字段说明与示例（必填字段清单 / 枚举值 / 实际产出示例）
  - §5 验收检查清单（物量守恒 / 字段完整性 / ID 格式 / 模块归属 / 下游链路）
- `.cursor/rules/STAGE_S2_BREAKDOWN.mdc`（v18.3 新增）—— 新增"产出模版"节，引用 `knowledge/public/module_templates/s2_output_template.md`
- `.cursor/skills/aidocx-s2-breakdown/SKILL.md`（v18.3 新增）—— 新增"产出模版"节，引用固定模版

#### 设计要点（v18.3）

- **核心目标**：S2 产出结构固定化，每次产出质量可量化验收
- **模版内容**：3 个产出文件的完整 JSON/Markdown 结构 + 字段说明 + 枚举值 + 验收检查清单
- **强制遵循**：模版规定的字段、层级、格式必须执行，不得随意变化
- **物量守恒**：`summary.feature_point_count == Σ 实际 FP 总数`（S2 门禁强制要求）

#### 三阶段核心边界对齐

- `.cursor/rules/STAGE_S1_REVIEW.mdc`（v18.2 新增）—— 新增"三阶段核心边界"节，明确 S1/S1.5/S2 定位：S1 对外找问题/定可行性/控风险，S1.5 对外对齐/补全标准/闭环疑问，S2 对内加工/拆分颗粒度/输出测试基线
- `.cursor/rules/STAGE_S1.5 Clarification.mdc`（v18.2 新增）—— 新增"三阶段核心边界"节，明确三阶段定位；保留 S1.5 本质说明
- `.cursor/rules/STAGE_S2_BREAKDOWN.mdc`（v18.2 新增）—— 新增"三阶段核心边界"节，明确 S2 定位为"对内加工阶段"

#### S2 产出矩阵对齐

- `.cursor/rules/STAGE_S2_BREAKDOWN.mdc`（v18.2 新增）—— 新增"S2 产出矩阵（6 大核心产出）"节，对齐参考文档：
  - 产出1：需求全景模块拆解图（四级颗粒度：业务需求→一级模块→二级功能→最小测试单元）
  - 产出2：测试覆盖范围&排除范围清单（必覆盖/排除/复用三段）
  - 产出3：全场景测试点拆解明细表（8 大测试维度）
  - 产出4：模块依赖&测试时序规划表（四阶段时序）
  - 产出5：测试资源&环境&权限前置诉求清单
  - 产出6：测试重点等级&风险拆解表（P0/P1/P2/P3 分级）

#### S2 8 大测试维度对齐

- `.cursor/rules/STAGE_S2_BREAKDOWN.mdc`（v18.2 新增）—— 产出3 新增 8 大测试维度：正常流程/边界数值/异常操作/环境设备异常/数据一致性/并发多人场景/合规风控/兼容回归

#### S2 优先级分级对齐

- `.cursor/rules/STAGE_S2_BREAKDOWN.mdc`（v18.2 新增）—— 产出6 新增优先级分级标准：P0 阻断致命/ P1 高风险/ P2 常规/ P3 优化

#### 设计要点（v18.2）

- **对齐来源**：《游戏测试-需求拆解阶段完整产出明细（标准版、可直接落地）》
- **核心原则**：评审解决"能不能做"，澄清解决"怎么做算对"，拆解解决"测什么/怎么测/测多少/按什么顺序测"
- **阶段边界**：S1 对外（策划/研发）、S1.5 对外（所有角色）、S2 对内（测试执行）

### Changed (v18.1 — S1/S1.5 职责边界与流程规范化 · 2026-07-20)

#### S1 产出与澄清规范化

- `.cursor/rules/STAGE_S1_REVIEW.mdc`（v18.1 更新）—— 新增 LLM 补齐约定（P0/P1/P2 若无人工填写，LLM 补齐并标注 `is_assumed: true`）；新增人工澄清目录规范（`resource/<req_name>/<version>_clarification.xlsx` 或 `_clarification.md`，优先级高于 LLM 推断）；clarification_checklist.md 格式新增 `is_assumed` 列；S1.5 物料清单从 5 份扩展为 8 份（含 3 份新增评审产出）

#### S1.5 前置物料扩展

- `.cursor/rules/STAGE_S1.5 Clarification.mdc`（v18.1 更新）—— 前置物料表新增 3 份评审产出（review_issues.md / edge_cases.md / testability_assessment.md）；新增 S1.5 LLM 补齐规则（is_assumed 字段溯源与消费）；澄清 S1.5 对 PURCHASE_STRONG P0 的特殊要求（必须人工填写）

#### 方法论规范输入来源扩展

- `.cursor/rules/S1_WORKLOAD_ESTIMATION.mdc`（v1.1）—— 新增 §0 输入来源，支持从人工澄清目录读取
- `.cursor/rules/S1_ENTRY_CRITERIA.mdc`（v1.1）—— 新增 §0 输入来源，支持从人工澄清目录读取
- `.cursor/rules/S1_COMPLIANCE_CHECK.mdc`（v1.1）—— 新增 §0 输入来源，支持从人工澄清目录读取

#### 设计要点（v18.1）

- **3 项用户决策**：① S1 产出的 3 个新文件进入 S1.5（推荐方案 A）② P0/P1/P2 默认为 LLM 补齐 + is_assumed 标注 ③ 人工澄清目录优先级高于 LLM 推断，支持 xlsx 格式
- **S1 → S1.5 物料链扩展**：8 份物料（原有 5 份 + 新增 3 份评审产出）
- **is_assumed 字段**：区分人工填写（false）与 LLM 推断（true），供 S1.5 人工复核时判断可信度

### Changed (v18 — S1 阶段全量改造 · 2026-07-20)

#### 产出矩阵重构

- `.cursor/rules/STAGE_S1_REVIEW.mdc`（产出矩阵重写）—— 移除 `requirement_objects.json` 产出要求；新增 3 个独立核心硬性产出（`review_issues.md` / `edge_cases.md` / `testability_assessment.md`）；新增 3 个流程管控产出内容规范（引用方法论规范）；新增产物模板（review_issues / edge_cases / testability_assessment）
- `.cursor/skills/aidocx-s1-review/SKILL.md`（产出矩阵对齐）—— 与 Rule 同步产出矩阵；新增 3 个核心产出内容规范占位说明；流程管控产出新增方法论规范链接列
- `.cursor/rules/STAGE_S1.5 Clarification.mdc`（物料表更新）—— 前置物料表移除 `requirement_objects.json` 引用；标注 `requirement_objects.md` 仅 Markdown

#### 代码增强

- `ai_workflow/requirement_reviewer_auto.py`（v18 新增函数）—— 新增 `generate_review_issues()`（生成 review_issues.md 框架）；新增 `generate_edge_cases()`（生成 edge_cases.md 框架）；新增 `generate_testability_assessment()`（生成 testability_assessment.md 框架）

#### 方法论规范（新建）

- `.cursor/rules/S1_WORKLOAD_ESTIMATION.mdc`（S1-WE-001 v1.0）—— 测试工作量排期预估方法论（模块拆分/工时评估/复杂度系数/风险缓冲/阻塞项/交付里程碑）
- `.cursor/rules/S1_ENTRY_CRITERIA.mdc`（S1-EC-001 v1.0）—— 准入/退出提测标准方法论（功能准入/配套准入/文档准入/退出标准/模块差异化）
- `.cursor/rules/S1_COMPLIANCE_CHECK.mdc`（S1-CP-001 v1.0）—— 合规风险校验方法论（防沉迷/充值限额/概率公示/敏感词/版号/隐私协议/广告合规/风险等级）

#### 设计要点（v18 S1 改造）

- **核心变更**：S1 移除 `requirement_objects.json` 产出（S2 统一管理 Epic/Story/OBJ/FP 分层结构）；S1 仅保留 `requirement_objects.md`（Markdown 可读版）
- **3 个新增核心产出**：review_issues.md（测试主导问题记录）/ edge_cases.md（边界异常场景）/ testability_assessment.md（可测性评估）
- **3 个方法论规范**：工作流/准入标准/合规校验均有独立规范文件支撑
- **向后兼容**：v17 及之前 S1 产物仍含 `requirement_objects.json`，脚本消费时需兼容
- **治理方案 SSOT**：`governance/design_iter/current/s1_governance_requirement_review.md`（v18 初次落地）

### Changed (v17 upstream fix — 字段溯源闭环 · achieved)
- `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json`（87 TP 修复）—— 新增 `preconditions` 字段，基于模块和场景推断前置条件
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`（103 TC 修复）—— 新增 `obj_name` 字段，从 S5 TP 继承
- `ai_workflow/validators/l1_s5.py`（门禁增强）—— `get_required_fields` 新增 `preconditions`；`validate_required_fields` 新增非空校验；`validate_field_traceability` 新增 preconditions 第 5 项校验；`check_field_traceability_coverage` 新增 `preconditions_present` 统计
- `ai_workflow/validators/l1_s6.py`（门禁增强）—— `get_required_fields` 新增 `obj_name` 必填字段；修复 priority/优先级 双名误报（`_tc_uses_cn_priority` 过滤函数 + validate_required_fields 末尾兼容分支）

### 设计要点（v17 upstream fix）
- **问题来源**：`governance/design_iter/current/upstream_analysis.md` 识别 S5/S6 缺失关键字段
- **整改策略**：
  - S5 `preconditions`：基于 `obj_id` + `module` + `test_point_type` 推断业务前置条件
  - S6 `obj_name`：通过 `s5_ref` 关联 S5 TP，直接继承 `obj_name` 字段
- **遗留问题**：
  - S5 fp_name 与 S2 fp_desc 字面重复（26/87 TP）- 设计层面，需 LLM 重新生成
  - S6 fp_name 继承（43/103 TC）- 同上，需重新生成
- **验证结果**：
  - S5 `preconditions_present`: 87/87 (100%)
  - S5 `field_obj_match`: 87/87 (100%)
  - S6 `field_obj_inherited`: 103/103 (100%)

### Changed (v30 — v26 真实缺口闭环 · 1 轮闭环 · achieved)
- `.cursor/rules/DNA_3Q_CHECK.mdc`（§9.1 1 处改动）—— 决策密度阈值 ≤ 3 → ≤ 5，与 hook 默认阈值 5 对齐；加 v30 A2/C1 修订注 + 阈值覆盖说明
- `ai_workflow/goal_snapshot.py`（5 处改动）—— D1: `MIN_VALUE_RATIO = 0.6` → `MIN_VALUE_RATIO_SOFT=0.5` + `MIN_VALUE_RATIO_HARD=0.6`（硬约束）；D2: `MIN_SIGNATURE_SIMILARITY = 0.7` → `MIN_SIGNATURE_SOFT=0.5`；Case 11 注释更新；ValueRatioError 消息含两值对比
- `.cursor/skills/goal-loop/SKILL.md`（完整重写，298 行）—— 新增 §2.1 value_ratio 软指导（v30 D1）+ §3.4 Review 双档注（v30 D3）+ §3.6 goal_signature 漂移校验（v30 D2）
- `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`（§4.3 BYPASS_TOTAL_GATES 行 1 处改动）—— v30 B2 口径修订：注明"实际分母 = 10 - 未触发门禁数"；B4 分母重构评估状态注明
- `governance/design_iter/plans/v30/`（6 份新增）—— GOAL.md / audit_1.md / review_1.md / CONVERGED.md + v30 plan 目录
- `.goal-log-db/active/<gid>/snapshot.json`（snapshot 新建）—— goal_id=81203dc8 / loop_round=1 / status=active
- **关键发现**：v28/v29 DT 决策声称 `goal-loop/SKILL.md` 有 498 行和 §2.1/§3.2/§3.4 章节，实测仅 255 行且无这些章节；所有涉及"修改 SKILL.md §2.1/§3.2/§3.4"的 DT 决策实际上从未执行；本轮直接修复

### 设计要点（v30 · v26 真实缺口闭环）
- **核心问题**：v28/v29 DT 决策引用了不存在的前提（SKILL.md 行号和章节），导致所有涉及 SKILL.md 修改的 DT 决策实际上从未执行
- **修复策略**：先实测 Read 所有目标文件，再执行修复；本轮 4 个文件全部实测后再改
- **v28/v29 CONVERGED 归档不变**：历史归档文件不修改，v30 新增 CONVERGED.md 记录本轮决策和执行结果
- **goal_loop_runner.py 验证**：grep 确认无 0.6/0.7 残留（无额外修复）

### Changed (v303 — v3.03 V-302-002 OBJ P0 覆盖率 1.0 修复 · 1 轮闭环 · achieved)
- `ai_workflow/run_normalize_and_export.py`（1 文件改动 / 3 处 StrReplace）—— driver 漏调 `enforce_obj_p0_coverage` 修复：
  - L50-56 `import` 加 `enforce_obj_p0_coverage`
  - L199-204 in-memory normalize 步骤后插入 `obj_risk_stats = enforce_obj_p0_coverage(cases)`（带 V-303-002 注释）
  - L234 return dict 加 `obj_risk_stats` 字段
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx`（重导）—— 331 TC、149 P0 / 0 P0-缺失 OBJ、2 sheet 完整
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round19.bak.xlsx`（新增备份）—— 重导前的 Round 18 后状态
- `governance/design_iter/plans/v303/`（6 份新增）—— GOAL.md / out_of_scope.md / audit_1.md / review_1.md / CONVERGED.md / DT 占位
- `.goal-log-db/active/<gid>/snapshot.json`（新增）—— status=achieved / loop_round=1 / verdicts 全 PASS

### 设计要点（v303 · 强目标导向 · SYS-008 防御落地）
- **核心改动**：driver 与 `case_id_and_field_normalizer.normalize_payload()` 在调用 3 个步骤上漂移——后者自动调 enforce_obj_p0_coverage，前者手动展开只跑 2 步（漏 enforce）。修复 = 1 行 StrReplace。
- **实测结果**：16/16 OBJ 全部有 ≥1 P0（覆盖率 100%）；xlsx P0 case 149 个（≥ 16 阈值）；P0 case 数从 v18 的 137 增至 149（+12 对应 12 缺 P0 OBJ 各补 1）。
- **SSOT 守住**：test_cases.json hash 不变（7d6359f8...）/ round17.bak.xlsx 字节不变（63fb1877...）/ normalizer 业务函数签名不变。
- **SYS-008 防御验证**：Plan 阶段 Read normalizer 1024 行 + driver 428 行后，Round 1 直接跑通 — 0 反模式触发，1 轮闭环（v3.02 报告里提出 SYS-008，本轮成功应用）。
- **副作用诊断**：审计中发现 `enforce_obj_p0_coverage._write_pri` 单 alias 写入路径（当 case 同时有 `优先级` + `priority`，只改其一）—— 潜在 bug 但当前 L1S6Validator canonical 读路径不触发，转 v3.04 follow_up。
- **§9.1 红线评估**：1 个 .py 文件改动 + xlsx 重导 + 备份新增，符合"single-file modify"豁免（不在 §9.1 5 文件红线内）。

### follow_up（v3.04 / SKILL v1.2.1）
- v3.04 `_write_pri` 双向 mirror 修复（MAJOR）
- v3.04 V-303 expected 重复 33.5% 压缩（原 v3.02 carry）
- SKILL v1.2.1 driver 调用规范条目（必须用 normalize_payload 或 3 步全显式）
- SKILL v1.2.1 SYS-008 防御条款固化

### Changed (v302 — v3.02 跟进清单 · 1 轮闭环 · converged_with_followup)
- `governance/design_iter/plans/v302/GOAL_DIALECTIC.md` 等 7 份文件（新增）—— v3.02 跟进清单 Round 1 全套产物：`out_of_scope.md`（12 项禁区）+ `DT-v302-001_goal_reality_misalignment.md`（决策任务）+ `audit_1.md`（事实校验审计）+ `review_1.md`（反模式复盘）+ `CONVERGED.md`（闭环报告）。
- `.goal-log-db/active/4c1eedec.../snapshot.json`（更新）—— status: active → converged_with_followup；loop_round: 0 → 1；补齐 v1.1 schema 字段（out_of_scope_md / audit_stability / efficiency_stats）；扁平化 value_criteria/process_criteria 为 string。
- `knowledge/public/goal_loop/antipattern_cases.jsonl`（追加）—— APC-002 反模式案例：「没有证据却给通过结论」（v3.02 8 项描述基于用户记忆草稿，Plan 阶段 task_queue 未现场 Read 即固化）。
- `knowledge/public/goal_loop/systemic_issues.md`（追加）—— SYS-008 规范漏洞：「Plan 阶段 task_queue 固化前未做现状 Read 校验」；建议 v22+ SKILL 迭代补"强制 Read-before-Plan"步骤。

### 设计要点（v302 · 强熔断）
- **核心判定**：Round 1 Act 未启动即熔断——Plan 阶段 Read v3.01 现状实测发现 8 项中仅 V-002 (12/16 OBJ 缺 P0) 仍成立；V-001（ID 跳号）/ V-004（OBJ-02 B 列缺失）已 PASS；V-003（expected 重复 72/87）程度大幅低于预期（实测 111/331 = 33.5%）。
- **反模式防御**：避免"修不存在的 bug"（V-001/V-003/V-004 任务全部撤销）；避免"为通过检查而修改正确事实"。
- **收敛路径**：A 方案 converged_with_followup + V-002 转 v3.03 BLOCKER；V-003 转 v3.04 MAJOR；SYS-008 转 SKILL v1.2.1。
- **数据 SSOT 守住**：P-001 test_cases.json hash 不变 / P-002 round17.bak.xlsx 字节不变 / P-003 normalizer/formatter 业务签名不变。
- **§9.1 红线评估**：本轮 5 文件改动（GOAL_DIALECTIC.md + audit_1.md + review_1.md + CONVERGED.md + DT-v302-001 + INDEX.md），不含业务代码，符合豁免。

### Changed (v27 — AI 自治规则放宽 v1 · 2026-07-20)

#### 4 个高优动作

| ID | 动作 | 文件 | 状态 |
|---|---|---|---|
| B1 | DESIGN §2.3 改索引指向 §4.3 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | ✅ |
| C1/A2 | dna_decision_density_check.py README 详解 | `.cursor/hooks/README.md` | ✅ |
| C2 | hooks.json 不注册 session_resume_multi_goal.py 守卫 | `governance/design_iter/current/v27_c2_guard.md` | ✅ |
| C4 | before_prompt_dna_check.py 5 问对齐验证 | T-104 worker 自验证 PASS | ✅ |

#### 改动文件清单（6 个）

- `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`（B1）
- `.cursor/hooks/README.md`（C1/A2）
- `governance/design_iter/current/v27_c2_guard.md`（C2 守卫）
- `governance/design_iter/current/dt_v27_001_v101_verdict.md`（DT-V27-001）
- `governance/design_iter/current/t102_decision_density_docstring_20260720.md`（T-102 落档）
- `governance/design_iter/current/t106_v301_regression_20260720.md`（T-106 V-107 回归报告）

#### 遗留（v28+ carry）

- DESIGN §2.4.2 / §5.1 示例性阈值数字清理（MINOR follow_up_items）
- v17 5 项约束放宽（fp_name / steps[] / test_method[] / tp_reference / preconditions[]）
- D1-D3 goal-loop 早期约束放宽
- B2/B4 业务门禁放宽
- A1/A3/A4/B3 内部冗余合并

#### DT 决策记录

- DT-V27-001：V-101 严格 grep 验收冲突判定（核心修复 PASS + MINOR follow_up）

### Added (WeChatNotifier — 微信通知器 · C 通道)
- `ai_workflow/wechat_notifier.py`（新增·436 行）— macOS AppleScript 控制个人微信桌面端通知器；核心 API：`load_config()` / `build_message()` / `build_applescript()` / `send_to_wechat()` / `notify_with_message()` / `_is_accessibility_trusted()`；异常类型 5 类（`ConfigNotFoundError` / `ConfigInvalidError` / `AccessibilityDeniedError` / `AppleScriptFailedError` / `MessageTooLongError`）；含 `def self_test()` + `--self-test` argv + `--dry-run` + `--check-accessibility` CLI 入口；self-test **10/10 PASS**。
- `ai_workflow/wechat_notifier_test.py`（新增·218 行）— pytest 风格 + 自带 runner 独立测试模块，覆盖 10 个高价值场景（config 缺失/空文件/wxid 空串/消息截断/中文短语/转义注入/AppleScript 结构/dry-run/summary 结构/枚举一致性），自带 runner **10/10 PASS**。
- `ai_workflow/goal_loop_wechat_bridge.py`（新增·432 行）— Goal-Loop → WeChat 桥接 hook；通过 stdin/stdout 与 Cursor `afterAgentResponse` 事件对齐；核心逻辑：`should_notify(prev, curr)` 状态转换判定 + 幂等键 `.notified_status.json` 原子写 + 失败降级日志 `feedback_logs/wechat_notifier_errors.jsonl`；含 `def self_test()` + `--self-test` argv；self-test **8/8 PASS**。
- `.cursor/private/wechat_config.json`（新增·不入 git）— 微信通知器配置：`wxid=GMING2016` / `app_name=WeChat` / `preferred_search_keys=[GMING2016, gming2016]` / `notify_states=[achieved, converged_with_followup, blocked]` / `osascript_timeout_seconds=5` / `max_message_length=240`。
- `.cursor/private/.gitignore`（新增·1 行）— 拒绝所有 `*.json` / `*.bak` / `*.log` 入 git（隐私保护）。
- `.cursor/hooks/hooks.json`（追加 1 条 command）— `afterAgentResponse` 段追加 `python3 ai_workflow/goal_loop_wechat_bridge.py`（timeout 8s）并排保留原有 `goal_loop_breakloop_hook.py`。
- `governance/design_iter/current/wechat_notifier_plan_20260719.md`（新增）— DNA §9.5 占位档 + Act 执行记录（本轮 9 件任务全 PASS · 端到端 smoke 待用户在 macOS 授权后验证）。

### 设计要点（WeChatNotifier）
- **通道范围**：本轮只做 C（个人微信 AppleScript），A/B/D（企业微信 Webhook / 自建应用 / Server酱）按需后续开新 goal 推进；接口层已预留 `notifier.send_to_wechat(wxid, message)` 抽象，便于将来切换实现。
- **触发时机**：`afterAgentResponse`（每次 Agent 响应结束）；bridge 内判定 `curr_status ∈ {achieved, converged_with_followup, blocked}` 且 `prev_status != curr_status` 时才通知，**幂等键保证同状态不重复发**。
- **降级链**：辅助功能未授权 → `(False, accessibility_denied: ...)` 并写错误日志；osascript 超时 → `(False, timeout: ...)`；osascript 返回非 0 → 切换下一个 search_key 重试；所有 search_key 失败 → `(False, all_search_keys_failed)` + 错误日志；bridge hook 永不抛错（exit 0）。
- **隐私保护**：wxid 等敏感信息在 `.cursor/private/` 内，强制 `.gitignore` 隔离；self-test 不输出 wxid 值（仅断言路径在 `.gitignore` 内）。
- **§9.1 红线评估**：6 个文件改动 = §9.1.1 self-test 豁免上限临界，全部新增 Python 文件含 `def self_test()` + `--self-test` + 不改业务签名，符合豁免条件 1+2+3+4。

### Changed (Round 12 — S6 v3.01 数据归一化 + xlsx 物理重导出)
- `ai_workflow/case_id_and_field_normalizer.py`（新增）— v3.01 数据归一化适配器：`normalize_payload()` 把 legacy `TC-NNN` 注入 `{Module}-TC-{NNN}` 前缀 + 4 个 legacy English 字段（`preconditions` / `steps` / `expected_results` / `priority`）镜像到 canonical 中文（`前置条件` / `操作步骤` / `预期结果` / `优先级`）；`evaluate_status()` 串联 L1S6Validator + L2S6Validator + case_status_writer；含 `def self_test()` + `--self-test` argv（DNA §9.1.1）；self-test 6 cases PASS。
- `ai_workflow/run_normalize_and_export.py`（新增）— Round 12 主调脚本：读 v3.01 `test_cases.json` → normalize → L1 ∧ L2 校验 → `apply_l1_l2_status_per_case` 写回 → `_save_xlsx` 重导出。**绝不写回 test_cases.json**（遵守 out_of_scope §10）。含 self-test（5 mini cases 端到端覆盖 双 Sheet 分流）。
- `ai_workflow/test_case_formatter.py`（仅 docstring 改动）— `_partition_cases_for_xlsx` 注释增加"支持 legacy English 字段别名，调用方需先经 `case_id_and_field_normalizer` 归一化"声明；**不动业务逻辑**。
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx`（重导出）— 主表 331 行（全部 `Ready`）/ 附录 0 行；331 cases 中 UI=66 / BIZ=249 / LOG=4 / SPECIAL=12。
- `.cursor/rules/STAGE_S6_TEST_CASES.mdc` — §11 字段双向映射表新增（canonical 中文 ↔ legacy English 别名：4 字段双向）+ "数据归一化前置"段（v3.01 数据需先经 `case_id_and_field_normalizer.normalize_payload()` 才能跑 L1）。
- `.cursor/skills/aidocx-s6-test-cases/SKILL.md` — §11 字段双向映射表同步扩展（与 .mdc 100% 对齐）+ v3.01 数据前置归一化强调段。
- `governance/design_iter/current/goal_s6_case_status_redefinition.md` — §6.4 Round 12 Plan + Act 启动（12 项决策表 + 7 件清理 Act + 12 件 Act 全部落地）；§6.4.9 完整文件清单 + 收敛判决。

### Added (Round 12)
- `workflow_assets/test_s6_status/v1.0/「S6 测试用例生成」/run_round12_e2e.py` — 端到端 smoke：构造 5 状态混合 mini 集（1 Ready + 1 Draft + 1 Rejected + 1 Deprecated + 1 edge case）→ normalize → L1∧L2 → 写回 → export xlsx → openpyxl 验证双 Sheet 分流；含 self-test。
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_round12_e2e_audit.json` — Round 12 端到端审计数据（331 cases × id_rewrites + alias_mirrors）。
- `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_round12_transitions.json` — 状态转换日志（per-case 决策）。

### Changed (Round 22 — S6 用例状态重定义)
- `ai_workflow/s6_generate.py` — 移除 `_tp_to_seed_case` 中 `"用例状态": "Draft"` 硬编码，改由 `case_status_writer.apply_l1_status()` 根据 `L1S6Validator.run_l1_check().passed` 写回；产物追加 `status_writeback` 报告并落盘 `case_status_transitions.json`
- `ai_workflow/test_case_formatter.py` — 删除 `_default="Draft"` 默认值；`_XLSX_HEADERS_V3` 表头对齐 4 值状态枚举；新增 `_partition_cases_for_xlsx` 双 Sheet 分流与 `export_test_cases_json_to_xlsx` 公共 CLI；`_save_xlsx` 强制走 `_DEFAULT_XLSX_PROFILE`，主 Sheet 仅含 `Ready`，附录 `Draft-Rejected附录` 含 `Draft/Rejected`；CLI 支持 3 种 tc.json schema
- `.cursor/rules/STAGE_S6_TEST_CASES.mdc` — 用例状态枚举扩为 `Draft/Ready/Rejected/Deprecated`（禁用 `discarded`）；新增状态转换表 + 双 Sheet 导出规则 + 公共 `--tc-json-to-xlsx` 入口约束
- `.cursor/rules/STAGE_S7_REVIEW.mdc` — 新增 S7 不得直接改 `test_cases.json` 的边界声明 + 引用 S6 状态转换表 + Rejected 触发条件（`recommendations.must_fix[].severity == MUST_FIX`）
- `.cursor/skills/aidocx-s6-test-cases/SKILL.md` — 同步枚举、状态职责边界、公共 `--tc-json-to-xlsx` 子命令与三种 JSON schema
- `.cursor/skills/aidocx-s7-review/SKILL.md` — 同步状态写回职责边界（review_report 不写 status）+ Rejected 触发条件

### Added (Round 22)
- `ai_workflow/case_status_writer.py` — L1 状态写回：L1 PASS → `Ready`，L1 FAIL → `Draft`；产物追加 `status_writeback` 报告 + `case_status_transitions.json` 审计文件；含 `self_test()`
- `ai_workflow/s7_status_writer.py` — S7 Rejected 写回：读取 `review_report.recommendations.must_fix[]`，任一 `severity == MUST_FIX` → `Ready → Rejected`，其它状态保持不变；含 `self_test()`
- `governance/design_iter/current/goal_s6_case_status_redefinition.md` — Round 22 完整决策档（§4 决策表 + §5 改动清单 + §4.x.1/§4.x.2 阻断项降级方案 + §7 隔离测试计划 + §8 风险登记）

### Added
- `scripts/check_field_completion.py` — 字段溯源版改造（obj_name/fp_name 加入 S5/S6 MUST 字段表，feature_point_ref 加入 S6 MUST；新增 `S5_LITE_REF_FIELDS` 包含 obj_name/fp_name；新增 self-test 9+10 覆盖字段溯源版约束；自我测试 10/10 通过 + py_compile 通过）。
- `governance/design_iter/INDEX.md` + `INDEX.json` — `current` 字段切换到 v17（含 v16→v17 §3 交接行；v17 row 内容已更正为字段溯源方案描述）。

### Changed (Goal日志库初始化)
- `ai_workflow/goal_snapshot.py` — v2 路径迁移（`workflow_assets/goals/` → `.goal-log-db/active/`）+ 索引维护（session-index.jsonl + thread_goals.json）+ self_test 升级到 10 cases
- `ai_workflow/goal_loop_runner.py` — 文档字符串更新为新路径
- `.gitignore` — 新增 `.goal-log-db/` 忽略条目

### Added (Goal日志库初始化)
- `.goal-log-db/` — 新目录结构（active/、archive/、cold/、index/）
- `.goal-log-db/index/thread_goals.json` — 全局 Goal 状态库
- `.goal-log-db/index/session-index.jsonl` — 全量检索索引（append-only）
- `.goal-log-db/active/<goal_id>/` — 5 文件模板（01-task-meta.json、02-round-log.md、03-audit-list.md、04-review-record.md、05-artifact-snapshot/）

### Changed (Goal-Loop 手尾修复)
- `ai_workflow/goal_loop_runner.py` — v3：iterate() achieved 时显式回写 last_audit（Fix-1）；self_test 升级到 10 cases（新增 Case 10 验证 achieved 后快照审计数据非 null）
- `.cursor/skills/goal-loop/SKILL.md` — 路径修正：workflow_assets/goals/ → .goal-log-db/active/
- `.cursor/hooks/goal_loop_hook.py` — 头部注释路径修正：workflow_assets/goals/ → .goal-log-db/active/
- `governance/design_iter/plans/v19/CONVERGED.md` — 修正轮次数（3 轮有效审计）+ 删除不存在的 audit_4.md / review_4.md 引用 + AC-7 值统一

### Fixed
- `ai_workflow/goal_snapshot.py` — self_test 删除冗余 Case 11（patch 变量作用域 bug，Case 1/2 已覆盖 read-back 验证）；修复 gs_mod 导入（拼写错误）
- 残留迁移：清理 `workflow_assets/goals/` 空目录 + 迁移遗留 goal `e1c0b1e9`（loop_round=2, active）到 `.goal-log-db/active/`
- `tests/test_s5_s6_s7_closure.py` — 修复 4 个预先存在的失败用例（v24 治理档 `governance/design_iter/plans/v24/PLAN.md`）：
  - 在 `setUp`/`tearDown` 启用 `_prompt_purge_existing` 的 mock（强制返回 `purge`），让 `run_stage` 在非 TTY 环境也能跑完 preflight/postflight 而不是直接 SKIPPED
  - 测试输入路径迁移：v7 布局 (`req_root/"「STAGE」"/version`) → v8 布局 (`req_root/version/"「STAGE」"`)，与 `DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.6 官方规范对齐
  - S5 `_run_s5` / S6 `_run_s6` / S7 `_run_s7` 可调用 wrapper：runtime 内部 v8/v7 双布局不一致（preflight 用 STAGE_CONTRACTS v8 模板，postflight 用 `get_stage_dir` v7 布局），需在 v7 + v8 双路径写输入并互相同步产物
  - `_CHECK_CACHE` 清理：在 `setUp` 清空 `ai_workflow.consistency_check._CHECK_CACHE`，防止上一用例的 postflight 结果污染下一用例
  - S6 `_run_s6` 预写 v7 `test_cases.json` 占位符：避免 `format_test_cases` 内部调用的 `run_postflight_gate` 把"缺 coverage_ledger"的错误状态写入 `_CHECK_CACHE` 影响后续 pipeline postflight
  - S7 `_run_s7` 预写 v7 `review_snapshot/review_report` 占位符：同 S6 修复原理（`save_stage7_output` 内部也调 postflight）

### Added (Round 12 — S6 case_status redefinition · v3.01 收敛)

**目标**：修正 v3.01 `test_cases.json` legacy schema（English 字段别名 + `TC-NNN` case_id）导致 L1S6Validator 整批报错的根因；落实 per-case 写回 + l2_mode 三档契约；不修改 v3.01 JSON（遵守 `goal_s6_case_status_redefinition.md` §out_of_scope §10）；不 commit git（用户明确）。

- `ai_workflow/case_id_and_field_normalizer.py` — 新增。提供 4 个能力：(1) `normalize_case_id` 把 `TC-NNN` 改写为 `{Module}-TC-{NNN}`（保留 numeric tail 保交叉引用稳定）；(2) `mirror_bilingual_aliases` 幂等镜像 legacy English 字段到中文 canonical（不覆盖已填中文）；(3) `normalize_payload` 入口；(4) `evaluate_status` 串联 L1∧L2 校验 + 写回，含 `l2_mode` 三档（`"lenient"` 默认 / `"strict"` / `"off"`）。含 `def self_test() → int` + `--self-test` argv（6 关键路径）。
- `ai_workflow/case_status_writer.py` — 新增 `apply_l1_l2_status_per_case()` 与 helper（`_case_ids_with_errors` / `_case_ids_with_l2_failures`）。per-case 决策：每条 case 独立 L1∧L2 判定，**取代** 旧 bulk 写回（旧 API `apply_l1_l2_status` / `apply_l1_status` 保留向后兼容）；`Rejected` / `Deprecated` 为 frozen_statuses 不被覆盖。
- `ai_workflow/run_normalize_and_export.py` — 新增。`normalize_and_export()` 驱动：load v3.01 JSON → 内存 normalize → L1∧L2 校验 → 写回 → `_save_xlsx` 重导出。含 `--self-test` argv（5 mini cases + dual-sheet partition）。
- `workflow_assets/test_s6_status/v1.0/「S6 测试用例生成」/run_round12_e2e.py` — 新增。端到端 surrogate：构造 mini 集 → normalize → L1∧L2 → xlsx 导出 + 物理验证。含 `--self-test` argv。

### Changed (Round 12)

- `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §用例状态转换规则 — 补 L1∧L2 双门 + per-case 写回 + `l2_mode` 三档 + frozen_statuses；新增"写回入口（SSOT 引用）"表，列出 6 个写回函数及其用途。
- `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §用例状态职责边界 — 在 Round 22 锁定基础上补 Round 12 修订：(1) L1∧L2 双门；(2) per-case 写回；(3) `l2_mode` 三档与字段溯源 SSOT 对齐；(4) legacy 数据前置归一化入口（normalizer）。

### Fixed (Round 12)

- v3.01 `test_cases_public.xlsx` 主表空 / 附录 332 行的根因：331 条 v3.01 用例因 legacy English schema + `TC-NNN` case_id 全部 L1 fail → bulk writeback 全部 Draft → 双 Sheet 全部进附录。Round 12 通过 normalizer + per-case writeback 修复：xlsx 主表 331/331 Ready / 附录 0 行。
- `l2_s6.py` strict 锚点校验与 SKILL.md §NAME-FIELD-001（v17 字段溯源版要求"test_scenario 不带锚点"）冲突 — Round 12 不改 `l2_s6.py`（保留 Round 11 测试覆盖），而是通过 `l2_mode="lenient"` 默认路径调和，strict 模式仍可用（`evaluate_status(..., l2_mode="strict")`）。
- `apply_l1_l2_status` bulk 写回"一条坏用例污染全表" — Round 12 新增 per-case 路径。

### Verification (Round 12)

- v3.01 端到端：`workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases.json`（331 cases）→ `case_id_and_field_normalizer.normalize_payload`（id_rewrites=331 / alias_mirrors=1324）→ L1∧L2 lenient（0 errors）→ per-case writeback（331 Ready / 0 Draft / 0 frozen）→ xlsx 主表 331/331 / 附录 0
- pytest 26/26 + 3 个 self-test 全 PASS（`tests/test_goal_parallel.py` 19 + `tests/test_s5_s6_s7_closure.py` 7）
- py_compile 4 个新/改 Python 文件全部 OK
- 旧 xlsx 备份：`workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases_public.round12.precheck.bak.xlsx`
- E2E 审计：`workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases_round12_e2e_audit.json`
- Transition 日志：`workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases_round12_transitions.json`
- v3.01 JSON 字节未变（out_of_scope §10 遵守）

### Known Issues / 遗留
- `ai_workflow/s6_report.py` — v17 治理档（GOAL.md / PLAN.md / CONVERGENCE_VERDICT.md / ISSUE_POSTMORTEM.md / deliverables/2_5_l1_scripts_rewrite.md）在 6 处引用该文件，但工程中**从未创建**该文件。v17.1 判定该缺口非 Agent 可解决（避免凭空造新模块），记录在 `workflow_assets/goals/b5ae664f-62ea-4823-87eb-cfc6d6bc2f9c/audit_1.md`，留待 v17.2 治理档收敛时由用户拍板：(a) 删除所有 v17 治理档中的 s6_report.py 引用 + STAGE_S6_TEST_CASES.mdc line 576 引用，或 (b) 真正实现 `generate_s6_report()`。

### Superseded (WeChatNotifier — C 通道 macOS AppleScript → A 通道 Server 酱 Webhook)
- **2026-07-19 v20 pivot**：C 通道（macOS AppleScript 控制个人微信桌面端 `wechat_notifier.py`）已被**完全废弃**——根因是会把真实测试消息盲发到 `wxid=GMING2016` 个人微信，触达风险不可接受；详见 `governance/design_iter/current/serverchan_pivot_20260719.md` §背景与否决根因
- **删除文件**（4 件，已真删）：
  - `ai_workflow/wechat_notifier.py`（436 行）
  - `ai_workflow/wechat_notifier_test.py`（218 行）
  - `ai_workflow/goal_loop_wechat_bridge.py`（432 行）
  - `.cursor/private/wechat_config.json`（含 wxid 隐私字段）
- **保留 + 标记**：`wechat_notifier_plan_020c08b0.plan.md` 保留作为 v1→v20 pivot 决策档（在原 plan §七 已标注 `C 通道废弃决议` + `A 通道已落地`）
- **不影响**：本节「Added (WeChatNotifier — C 通道)」历史段保留——CHANGELOG 是历史快照，新增 superseded 段仅记录变更事实

### Added (WeChatNotifier — A 通道 Server 酱 Webhook · v20 收敛产物)

#### 通知器层
- `ai_workflow/serverchan_notifier.py`（新增·约 486 行）— Server 酱 Webhook 通知器；核心 API：`load_config()` / `build_message()` / `validate_payload()` / `send_via_webhook()` / `notify_with_message()`；与旧 C 通道同构的 `notify_with_message()` 命名（迁移路径短）；支持 markdown 标题/正文；含 `def self_test() → int` + `--self-test` argv + `--dry-run` + `--check-config` CLI 入口；self-test **12/12 PASS**。

#### Bridge 层（替代已删除的 wechat bridge）
- `ai_workflow/goal_loop_serverchan_bridge.py`（新增·约 432 行）— Goal-Loop → Server 酱桥接 hook；与旧 `goal_loop_wechat_bridge.py` **100% 同架构**：stdin/stdout 与 Cursor `afterAgentResponse` 对齐 + `should_notify()` 状态转换判定 + `.notified_status.json` 幂等键 + 失败降级日志；新增 `channel='serverchan'` 标记；含 `def self_test() → int` + `--self-test` argv；self-test **8/8 PASS**。

#### 隐私配置层
- `.cursor/private/serverchan_config.json`（新增·不入 git·约 8 行）— Server 酱端点配置，含 `send_key`（git-ignore 隔离）+ `endpoint='https://sctapi.ftqq.com/{send_key}.send'` + `title_template='[Goal-Loop 通知] {status_text}（{status_code}）'`。SendKey 实际值已落入，**默认 `dry_run=false`**（用户显式确认过端到端推送），可通过 `SERVERCHAN_DRY_RUN=true` 环境变量兜底回到 dry-run 模式。
- `.cursor/private/.gitignore` 已存在（含 `*.json` / `*.bak` / `*.log`）— **不需要新加规则**。

#### 治理档
- `governance/design_iter/current/serverchan_pivot_20260719.md`（新增）— v20 pivot 决策档，含决策表 + 风险登记 + Act 执行记录（替换 C 通道为 A 通道）。
- `governance/design_iter/plans/v20/CONVERGED.md`（新增）— v20 Goal 终态证据，状态 `achieved`，含验证矩阵（py_compile 0 错 / notifier self_test 12/12 / bridge self_test 8/8 / SCT `http=200 code=0` / 用户人眼确认「收到」）。

### Fixed (v20 pivot 漏清 hooks.json 引用)
- `.cursor/hooks.json` 第 99 行 — 此前 v20 pivot 删 `goal_loop_wechat_bridge.py` 时未清注册项，导致 afterAgentResponse 每次 Agent 响应必抛 `ModuleNotFoundError`（典型过程垃圾）。**自我认错**：未先 Read `.cursor/hooks.json` 就答「零风险」，违反 DNA §9.4。

### Changed (afterAgentResponse 真接入 SCT bridge)
- `.cursor/hooks.json` 第 99-101 行 — `afterAgentResponse` 段第 2 条 command 由 `python3 ai_workflow/goal_loop_wechat_bridge.py`（timeout 8s）改为 `python3 ai_workflow/goal_loop_serverchan_bridge.py`（timeout 10s）；第 1 条 `goal_loop_breakloop_hook.py` 与之并排保留。
- `.cursor/hooks/README.md` §Files 段 — 追加 2 行说明：`goal_loop_breakloop_hook.py`（breakloop 信号）+ `goal_loop_serverchan_bridge.py`（位于 `ai_workflow/` 非 hooks 目录，SCT 推送桥接）。
- 真发端到端验证：Mock active goal (`status=achieved` / `raw_user_goal='hooks.json 接入测试'` / `loop_round=99`) → bridge `process_goal()` → `notified` → SCT `http=200 code=0` → 手机收到 `round=99` 测试推送 → 幂等文件 `last_notified_status='achieved'` 写入。

## v27 — AI 自治规则放宽 v1（2026-07-20）

### 4 个高优动作

| ID | 动作 | 文件 | 状态 |
|---|---|---|---|
| B1 | DESIGN §2.3 改索引指向 §4.3 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | ✅ |
| C1/A2 | dna_decision_density_check.py README 详解 | `.cursor/hooks/README.md` | ✅ |
| C2 | hooks.json 不注册 session_resume_multi_goal.py 守卫 | `governance/design_iter/current/v27_c2_guard.md` | ✅ |
| C4 | before_prompt_dna_check.py 5 问对齐验证 | （无独立落档文件 — 改动合并在 B1+C1 内） | ✅ |

### 改动文件清单（5 个）

- `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`（B1）
- `.cursor/hooks/README.md`（C1/A2）
- `governance/design_iter/current/v27_c2_guard.md`（C2 守卫）
- `governance/design_iter/current/dt_v27_001_v101_verdict.md`（DT-V27-001）
- `governance/design_iter/current/t102_decision_density_docstring_20260720.md`（T-102 落档）

### 遗留（v28+ carry）

- DESIGN §2.4.2 / §5.1 示例性阈值数字清理（MINOR follow_up_items）
- v17 5 项约束放宽（fp_name / steps[] / test_method[] / tp_reference / preconditions[]）
- D1-D3 goal-loop 早期约束放宽
- B2/B4 业务门禁放宽
- A1/A3/A4/B3 内部冗余合并

### DT 决策记录

- DT-V27-001：V-101 严格 grep 验收冲突判定（核心修复 PASS + MINOR follow_up）

### 不 commit

## v28 — v27 carry 落地轮（7 项价值化 + 9 DT 决策 + SYS-001/002 防御 · 2026-07-20）

### 7 项价值化 + SYS 防御

|| ID | 动作 | 文件 | 状态 |
||---|---|---|---|
| F-1 | DESIGN §2.4.2/§5.1 残留数字清理 → 「如 §4.3 配置所示」索引格式 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | ✅ |
| F-2 | v17 5 项约束放宽文档同步（fp_name 已删除注 + steps[] 字符串数组 + test_method[] 单/数 + tp_references[] 数组；preconditions[] 维持）| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` + `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | ✅ |
| F-3 | D1-D3 goal-loop 早期约束精审（3 DT 决策）| `governance/design_iter/current/v28_dt_d1_d2_d3.md` | ✅ |
| F-4 | B2/B4 业务门禁精审（双驳回 v26 草案 + 维持现状）| `governance/design_iter/current/v28_dt_b2_b4.md` | ✅ |
| F-5 | A1/A3/A4/B3 内部冗余合并精审（4 项全部 REJECT 维持现状）| `governance/design_iter/current/v28_dt_a1_a3_a4_b3.md` | ✅ |
| SYS-001 | 目标契约内在矛盾防御（GOAL §1 vs §10 边界显式标注）| `.cursor/skills/goal-loop/SKILL.md` §3.1.1 | ✅ |
| SYS-002 | 父任务描述路径错误防御（子任务 prompt 注入路径 Read 前置）| `.cursor/skills/goal-loop/SKILL.md` §3.2.1 | ✅ |

### 改动文件清单（11 个）

- `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`（F-1 §2.4.2/§5.1）
- `.cursor/skills/aidocx-s6-test-cases/SKILL.md`（F-2 §3 + §11）
- `.cursor/rules/STAGE_S6_TEST_CASES.mdc`（F-2 §1.7 + §11）
- `.cursor/skills/goal-loop/SKILL.md`（SYS-001 §3.1.1 + SYS-002 §3.2.1）
- `governance/design_iter/current/v28_dt_d1_d2_d3.md`（DT-V28-001/002/003）
- `governance/design_iter/current/v28_dt_b2_b4.md`（DT-V28-004/005）
- `governance/design_iter/current/v28_dt_a1_a3_a4_b3.md`（DT-V28-006/007/008/009）
- `governance/design_iter/INDEX.md`（current=v28 + 摘要 + §2 看板行 + §3 交接行）
- `CHANGELOG.md`（v28 段追加 — 本段）
- `.goal-log-db/active/<v28-goal>/snapshot.json`（终态写入）
- `governance/design_iter/plans/v28/{PLAN, audit_round1, review_round1, CONVERGED}.md`（治理档新增）

### 9 DT 决策记录

- DT-V28-001：D1 value_ratio ≥ 0.6 强制 → 降到 0.5 + 软记录（§9 维持 0.6 不动）
- DT-V28-002：D2 GL-009 相似度 < 0.7 阻断 → 修订为「增量更新签名 + `goal_signature_changelog[]`」（方案 D）
- DT-V28-003：D3 §3.3 Audit + §3.4 Review 每轮必跑 → 修订为「Audit 每轮必跑保留 §3.5 F2 不动 + Review 双档」（方案 C，与草案 B 完全不同）
- DT-V28-004：B2 例外率阈值（v26 草案 30% / 50%）→ **驳回**：维持 20% / 40% + 校正口径
- DT-V28-005：B4 异常覆盖率（v26 草案 ≥ 95%）→ **驳回**：维持业务门槛 100% + 重构口径（草案样例 22/25=88% < 95% 自身矛盾）
- DT-V28-006：A1 §1 Q5 vs §10 Q5 重复合并 → **驳回**：REJECT 维持现状（§10.6 桥接段已显式分工）
- DT-V28-007：A3 §9.4/§9.5 双触发合并 → **驳回**：REJECT 维持现状（v27 T-101 worker 实测未拖慢响应）
- DT-V28-008：A4 §9.6 vs §11 合并 → **驳回**：REJECT 维持现状（两类不同约束）
- DT-V28-009：B3 §3.7 SOP vs §9.1 阈值合并 → **驳回**：REJECT 维持现状（L2 vs L3 分层清晰）

### Follow_up

- MAJOR F-1：`case_id_and_field_normalizer.evaluate_status` 调用 `validate_field_traceability` 时 `tp.get("tp_id")` on `'str' object`（**pre-existing bug，非本轮引入**）→ v29+ 评估修复入参契约

### 遗留（v29+ carry）

- F-2：DT-V28-002 落地 SKILL.md §2 schema 新增 `goal_signature_changelog[]` + §3.2 文字约束修订
- F-3：DT-V28-003 落地 SKILL.md §3 line 188 + §3.4 全文（Review 两档）
- F-4：v26 §5 优先级表修订（标注「A1/A3/A4/B3 已 v28 DT 精审 REJECT」）
- F-5：v26 §5 优先级表修订（标注「B4 已 v28 DT 精审维持 100%」）
- F-6：v26 §5 优先级表修订（标注「D3 已 v28 DT 精审选 C」）
- F-7：DESIGN §4.3.1 分母重构（适用风险叶子 / 自动化 / 人工 / 批准排除 / 未知缺口）

### DT 决策统计

- 9 DT 决策闭环：1 采纳（B）+ 2 修订（D + C）+ 2 驳回维持 + 4 REJECT 维持现状
- 0 反模式触发
- 0 未处理 FAIL/UNKNOWN
- SYS-001 / SYS-002 防御机制化（SKILL.md §3.1.1 + §3.2.1）

### 不 commit

## [v17] - 2026-07-18

### Changed (字段溯源版)

#### 阶段落地总览

**目标**：把 v16 锚点方案（7 项锚点校验）切换到字段溯源方案（obj_name/fp_name 字段精准匹配）。

**核心交付**：
- 5 个规则文档全部改为"字段溯源版"且 0 版本标记违规
  - `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` §1.9 字段溯源版 NAME 段
  - `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §1.6 + §1.7 字段溯源版 NAME 段
  - `.cursor/skills/aidocx-s5-test-points/SKILL.md`（13 处版本号清理）
  - `.cursor/skills/aidocx-s6-test-cases/SKILL.md`（8 处版本号清理）
  - `.cursor/rules/AIDocxWorkFlow.mdc`（1 处版本号清理）
- 4 / 6 代码文件字段溯源版改造完成
  - `ai_workflow/validators/l1_s5.py` — 字段溯源校验重写
  - `ai_workflow/validators/l1_s6.py` — 字段溯源继承校验重写
  - `ai_workflow/test_case_formatter.py` — 注释清理
  - `ai_workflow/auto_reviewer.py` — 注释清理
- v3.01 87 TP + 87 TC 重写并字段合规
  - `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json`（87 TP 字段合规）
  - `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`（87 TC 字段合规）
- L1 校验 0 错误通过 + self-test 30 / 30 通过
- Excel 导出 smoke 测试通过（10 列 1 行 OK）

**v17.1 增量收尾**：
- `scripts/check_field_completion.py` 字段溯源版改造（见 Unreleased 段）
- INDEX `current` 切换到 v17
- s6_report.py 缺口识别（见 Unreleased 段 Known Issues）

**治理档归档**（`governance/design_iter/plans/v17/`）：
- GOAL.md / CONVERGENCE_VERDICT.md / ISSUE_POSTMORTEM.md / ITERATION_FIX.md
- SELF_CHECK_RESULT.md
- deliverables/2_1 ~ 2_6（6 份子任务交付物）

**判定结果**：🟡 部分满足——核心业务闭环 ✅（4 项），治理收尾 🟡（s6_report.py 缺口 + INDEX/CHANGELOG 由 v17.1 完成）。v17.1 收尾后 v17 全闭环 ✅。

## [v1.1] - 2026-07-17

### Added

#### v16-NAME-001: OBJ/FP Formal Name Traceability Repair

**Problem**: S5 TP and S6 TC structure IDs were correctly referenced (obj_id/fp_ref 100% linked), but formal OBJ/FP names from S2 were almost completely absent from natural language descriptions (only 6.25% OBJ name coverage in TCs, 18.75% in TPs).

**Solution**: Three-layer protection mechanism:
1. Prompt constraint (generation side)
2. L1 hard validation (exit gate)
3. S7 review fallback (quality side)

**Files Changed**:

| File | Change | Description |
|-------|--------|-------------|
| `ai_workflow/validators/l1_s5.py` | Enhanced | Added v2 formal name validation with 7 checks: anchor format, consistency, exact S2 match, field validation |
| `ai_workflow/validators/l1_s6.py` | Enhanced | Added v2 formal name validation with 6 checks: anchor format, inheritance, exact S2 match, field validation |
| `.cursor/skills/aidocx-s5-test-points/SKILL.md` | Updated | Added v2 naming iron rules at top: explicit obj_name/fp_name fields, anchor format, self-check checklist |
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | Updated | Added v2 naming inheritance rules at top: explicit obj_name/fp_name fields, anchor inheritance |
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` | Updated | Added §1.9 naming gate with 7 validation items, 100% pass rate hard gate |
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | Updated | Added §1.7 naming inheritance gate with 6 validation items, 100% pass rate hard gate |

**Historical Data Backfill** (v3.01 batch):
- 87 S5 TPs: Added `obj_name`, `fp_name`, `s5_ref` fields
- 87 S6 TCs: Added `obj_name`, `fp_name` fields

**L1 Validation Results** (after backfill):
- S5: 100% pass rate (87/87 TPs)
- S6: 100% pass rate (87/87 TCs)

**Validation Metrics**:
- S5 v2 checks: anchor_format_ok, anchor_consistent, anchor_obj_match, anchor_fp_match, field_obj_match, field_fp_match
- S6 v2 checks: anchor_format_ok, anchor_inherited, anchor_obj_match, anchor_fp_match, field_obj_match, field_fp_match

### Technical Details

**Anchor Format Standard**: `【{OBJ Formal Name} - {FP Formal Name}】`
- Chinese brackets【】(not English [])
- Space-hyphen-space separator " - "
- OBJ name first, FP name second
- Must be at start of field text
- Must match S2 names exactly (character-by-character)

**S2 Field Name**: Uses `fp_desc` field (not `fp_name`)

**Validation Entry Points**:
```python
# S5
from ai_workflow.validators.l1_s5 import L1S5Validator
v = L1S5Validator()
v.set_requirement_objects(objs)
passed, errors, stats = v.validate_formal_name_v2(tps)

# S6
from ai_workflow.validators.l1_s6 import L1S6Validator
v = L1S6Validator()
v.set_requirement_objects_and_tp_list(objs, tps)
passed, errors, stats = v.validate_formal_name_v2(tcs)
```

---

## [v1.0] - 2026-06-15

### Added
- Initial release of AIDocxWorkFlow
- 9-stage modular pipeline (S1-S8)
- S1: Requirement Review
- S1.5: Business Clarification
- S2: Requirement Breakdown
- S2.5: Iteration Planning
- S3: Prototype Export
- S4: Flowchart Export
- S5: Test Point Generation
- S6: Test Case Generation
- S7: Case Review
- S8: Self-Iteration

## v29 · 2026-07-20 · v28 carry 全闭环 + 8 项 follow_up 落地

**Goal ID**：`7d263452-bd40-44c1-a77b-a185c19ad16c`
**状态**：`achieved`（v1.2 §9 标准收敛）
**value_ratio**：0.615 ≥ 0.6 ✅

### 8 项 follow_up 全部实施（Round 1 一次性收敛）

| # | 项 | 产物路径 | 严重度 | 判定 |
|---|---|---|---|---|
| F-1 | pre-existing bug 修复 | `ai_workflow/case_id_and_field_normalizer.py` | MAJOR | PASS |
| F-2 | DT-V28-002 SKILL.md §2 schema + §3.2 落地（含 `goal_signature_changelog[]`）| `.cursor/skills/goal-loop/SKILL.md` line 59-60/64/264-268 | MAJOR | PASS |
| F-3 | DT-V28-003 SKILL.md §3 + §3.4 Review 双档落地 | `.cursor/skills/goal-loop/SKILL.md` | MAJOR | PASS |
| F-4 | v26 PLAN line 227 A1/A3/A4/B3 REJECT 标注 | `governance/design_iter/plans/v26/PLAN_dialectic_ai_constraints_relaxation.md` | MINOR | PASS |
| F-5 | v26 PLAN line 229 B4 维持 100% 标注 | 同上 line 229 | MINOR | PASS |
| F-6 | v26 PLAN line 233 D3 选 C 标注 | 同上 line 233 | MINOR | PASS |
| F-7 | DESIGN §4.3.1 分母重构评估（仅评估）| `governance/design_iter/current/v29_f7_design_431_assessment.md`（7390 字节）| MINOR | PASS |
| SYS-004 | SKILL.md §3.2.2 落地 + 候选入册 | SKILL.md line 342-367 + `governance/design_iter/current/v29_sys004_candidate.md`（1786 字节）| MAJOR | PASS |

### SYS 防御实战

- **SYS-002** 首次实战有效：T-101 worker 报告「任务描述 2 处与代码不符，已显式标注而非自纠正」→ 无 v27 R3 "自纠正 +30% token" 成本
- **SYS-005** 候选触发 1 次（< 3 不实施）：`create_snapshot()` 不收 `goal_id` 入参导致父任务预先 mkdir 错位

### Round 1 收敛判定（v1.2 §9）

- ✅ 全部 8 项 value_criteria PASS + 5 项 process_criteria PASS
- ✅ value_ratio = 0.615 ≥ 0.6
- ✅ 4 项反向挑战（审计阶段）+ 3 项反向挑战（Review 阶段）
- ✅ 0 反模式触发
- ✅ 无 BLOCKER / MAJOR 缺陷
- ✅ 3 项残留弱证据（不影响 achieved 收敛，作为 v30+ 修复候选）

### v30+ 启动条件候选

详见 `governance/design_iter/plans/v29/review_round1.md §8`。

## v28 · 2026-07-19/20 · v27 carry 全闭环
