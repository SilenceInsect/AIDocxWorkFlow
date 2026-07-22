# Goal: TC Excel 层级映射结构化规范

## 任务目标

设计并落地测试用例内部结构化映射关系，解决测试用例 Excel 生成质量差、结构混乱的问题。

**核心要求**：
- 1 用例描述（用例标题）= N 功能描述
- 1 功能描述（测试场景）= N 前置条件
- 1 前置条件 = N 操作步骤
- 1 预期结果 = N 操作步骤（步骤-预期对应）

## 验收标准

| # | 验收标准 | 正确范例 |
|---|---------|---------|
| 1 | 每个 TC 至少含 3 个步骤 | `steps: [{step_num:1},{step_num:2},{step_num:3}]` |
| 2 | 步骤-预期有显式对应关系 | `expected_results` 含 `step_ref` 或按顺序对应 |
| 3 | 不同前置条件独立 TC | "余额充足"/"余额不足"分开，不合并 |
| 4 | Excel 渲染正确 | 无 dict repr，无 steps 碎裂 |
| 5 | 新规范落地到 SKILL.md | §12 TC 结构化映射规范 |

## 预期产出

1. `governance/design_iter/current/tc_structural_mapping_spec.md` - 规范文档
2. `ai_workflow/test_case_formatter.py` 更新 - 支持新映射
3. `.cursor/skills/aidocx-s6-test-cases/SKILL.md` 更新 - §12 章节
4. `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_structured.json` - 示范文件

## 任务计划

1. 分析现有 TC 数据结构问题
2. 设计四层映射模型
3. 定义新的 TC Schema
4. 更新 SKILL.md §12
5. 更新 test_case_formatter.py 渲染逻辑
6. 生成示范文件验证
