# v17 PLAN 候选 — TP/TC 字段溯源方案（无锚点版）

> **来源**：用户提交的 `TP-TC 终极标准化最优方案（零冲突、全链路一致、Excel原生适配）.md` + 2026-07-17 用户拍板"完全采纳（推 v17）"
> **状态**：🟡 草案待批（v17 PLAN 入口文件）
> **替代关系**：推 v16 v2 锚点方案；本方案作为下一版（v17）治理入口

---

## 1. v17 vs v16 核心差异

| 维度 | v16（当前） | v17（候选） |
|---|---|---|
| OBJ/FP 名称承载 | 文本锚点【OBJ - FP】 + JSON 字段 | **仅 JSON 字段**（obj_name/fp_name） |
| `fp_name` 来源 | S2 fp_desc 逐字相等 | LLM 自创中性功能名 |
| `title` 文本 | 必须【OBJ - FP】开头 | 纯场景简短标题 |
| `description` 文本 | 必须【OBJ - FP】开头 | 纯测试逻辑（前置+步骤+预期） |
| TC test_scenario | 必须【OBJ - FP】开头 + 与 TP title 一致 | 纯场景一句话描述 |
| L1 校验策略 | 7 项锚点 v2 校验（文本+字段） | **仅字段精准匹配**（obj_name/fp_name == S2） |
| `test_method` | 字符串 | 字符串数组 |
| `preconditions` | 字符串 | 字符串数组 |
| `steps` | 字符串（≤8 步） | 结构化数组 `[{step_num, action}]` |
| `expected_results` | 字符串 | 字符串数组 |
| TC 字段 `tp_reference` | 无（仅 s5_ref） | 新增 |
| Excel 导出 | 文本截取 + 字段映射 | **完全结构化字段映射** |

## 2. 影响面（DNA §1 准则 1 一致性 + 准则 3 全局考虑）

### 2.1 必改文件

| 文件 | 当前内容 | 必改原因 |
|---|---|---|
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` §1.9 | 锚点 v2 7 项校验 | 改为字段溯源 |
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` §1.7 | 锚点继承 6 项校验 | 改为字段溯源 |
| `.cursor/skills/aidocx-s5-test-points/SKILL.md` §v16 NAME 段 | 锚点铁律 | 改为字段铁律 |
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §v16 NAME 段 | 锚点铁律 | 改为字段铁律 |
| `.cursor/rules/AIDocxWorkFlow.mdc` §v16 引用 | 引用锚点方案 | 改为引用 v17 字段方案 |
| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §11 永久规范 | 字段映射表 | 增加 v17 字段定义 |
| `ai_workflow/validators/l1_s5.py` | 7 项锚点校验 | 改为字段校验 |
| `ai_workflow/validators/l1_s6.py` | 6 项继承校验 | 改为字段校验 |
| `ai_workflow/test_case_formatter.py` | 锚点提取 + 格式化 | 改为字段格式化 |
| `ai_workflow/auto_reviewer.py` | 锚点 L1 调用 | 改为字段 L1 |
| `ai_workflow/s6_report.py` | 锚点报告 | 改为字段报告 |
| `scripts/check_field_completion.py` | 锚点字段定义 | 改为 v17 字段定义 |
| `knowledge/public/module_templates/` 下所有引用 fp_desc 的文件 | 用 fp_desc 当字面量 | 同步改 fp_name 引用 |

### 2.2 产物改动

| 文件 | 当前状态 | 必改原因 |
|---|---|---|
| `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json` | 87 TP 全部【OBJ - FP】锚点 | 重写 fp_name/title/description |
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` | 87 TC 全部【OBJ - FP】锚点 | 重写 test_scenario + steps/preconditions 结构化 |
| 其他版本 v1.0/v2.0/v3.0 的 TP/TC | 多版本产物 | 全部回溯或冻结旧版本 |
| `knowledge/project_local/游戏道具商城/s6/export_profiles/test_cases.export.json` | 当前无结构化 schema | 新增结构化 schema |

### 2.3 知识库 / 治理档

| 文件 | 必改原因 |
|---|---|
| `AGENTS.md` §v16 引用 | 同步 v17 引用 |
| `CHANGELOG.md` | 新增 v17 条目 |
| `governance/design_iter/INDEX.md` | 新增 v17 索引 |
| `governance/design_iter/plans/v17/PLAN.md` | 新建 |
| `governance/design_iter/plans/v17/SELF_CHECK.md` | 新建 |
| `governance/design_iter/plans/v17/open_questions.md` | 新建 |

## 3. 风险与回退方案

### 3.1 风险

| # | 风险 | 等级 |
|---|---|---|
| 1 | 推翻 v15/v16 锚点 v2 决策，所有历史 TP/TC 需重写 | 🔴 |
| 2 | L1 校验脚本逻辑全改，回归测试无法覆盖 | 🔴 |
| 3 | fp_name 由 LLM 自创，导致同一 FP 名称不统一，跨项目比较失效 | 🔴 |
| 4 | 7 处规则文件 + 5 处代码文件 + 多版本产物改动 = 单次改动 ≥15 文件 | 🔴 |
| 5 | 用户提交的方案中 `fp_name = "购买按钮可用性控制"` ≠ S2 fp_desc = "余额不足时禁用购买按钮" | 🟡 语义重定义 |

### 3.2 回退方案

- 保留 v16 v2 锚点版本在 `governance/design_iter/archive/v16_*/` 下
- v17 与 v16 双轨运行：用户可在 v3.01 = v16 / v3.02 = v17 中二选一
- 若 v17 实施中遇到 L1 回归失败，回退 v16 重新运行 v3.01 L1 验证

## 4. v17 实施步骤（分阶段）

### Phase 1：PLAN 文档 + 影响面确认（本周）

- [ ] 创建 `governance/design_iter/plans/v17/PLAN.md`
- [ ] 创建 `governance/design_iter/plans/v17/SELF_CHECK.md`
- [ ] 创建 `governance/design_iter/plans/v17/open_questions.md`
- [ ] 列出所有待决问题
- [ ] **必须**：用户审批通过 v17 PLAN 才进入 Phase 2

### Phase 2：约束文件改写（下周）

- [ ] 改 STAGE_S5 §1.9
- [ ] 改 STAGE_S6 §1.7
- [ ] 改 s5/s6 SKILL.md
- [ ] 改 AIDocxWorkFlow.mdc + DESIGN_AND_EXECUTION_STANDARDS.mdc
- [ ] 同步改 AGENTS.md + CHANGELOG.md

### Phase 3：L1 校验脚本改写（下下周）

- [ ] 改 l1_s5.py（7 项 → 字段校验）
- [ ] 改 l1_s6.py（6 项 → 字段校验）
- [ ] 改 test_case_formatter.py
- [ ] 改 auto_reviewer.py
- [ ] 改 s6_report.py
- [ ] 改 check_field_completion.py

### Phase 4：v3.01 产物重写（Phase 3 后）

- [ ] 重写 87 TP（fp_name/title/description）
- [ ] 重写 87 TC（test_scenario/steps/preconditions）
- [ ] 跑 L1 校验
- [ ] 写 v17 L1 自测报告

### Phase 5：Excel 导出层结构化

- [ ] 在 `knowledge/project_local/游戏道具商城/s6/export_profiles/` 加 test_cases.export.json 结构化 schema
- [ ] 实现结构化 xlsx 导出
- [ ] 验证 Excel 列与 JSON 字段一一对应

### Phase 6：回归测试 + 归档

- [ ] 重跑 v3.01 端到端
- [ ] 写 v17_legacy_compat_report.md（v16 vs v17 对比）
- [ ] 归档 v16 到 archive/

## 5. 待决问题（open_questions）

- Q1: `fp_name` 由 LLM 自创是否需要审核机制？建议：人工抽样审 10%。
- Q2: `steps[]` 结构化是否要支持 1:N（一个步骤多个 sub-action）？建议：先不支持，避免 schema 膨胀。
- Q3: `test_method` 数组顺序是否影响输出？建议：按"主方法在前"排序。
- Q4: Excel 导出列顺序按"用例描述 / 功能描述 / 模块 / 优先级 / 前置条件 / 测试步骤 / 预期结果"是否合理？建议：与 S6 §3.7 模板对齐。
- Q5: 历史版本（v1.0/v2.0/v3.0）是否需要迁移？建议：冻结历史版本，不迁移；新需求走 v3.01+。
- Q6: 是否同步改 L2 Hook（L3 机制 .cursor/hooks/dna_decision_density_check.py）？建议：保持现有。
- Q7: `fp_name` 命名规则——是否需要约束命名空间（如必须包含动词）？建议：LLM 自决 + 一致性自查。

## 6. 与 v16 决策回退

- v17 实施后，v16 v2 锚点方案不再生效
- 但保留 v16 校验脚本在 `ai_workflow/validators/_legacy/` 备查
- 任何旧版本产物（v3.01 之前）继续按 v16 校验

## 7. 落档协议执行（§9.5）

- 本档已落档
- 修改文件：1（本 PLAN 草案）
- 单次响应工具调用：≤ 10
- 决策点：本 PLAN 需用户审批后才进入 Phase 2