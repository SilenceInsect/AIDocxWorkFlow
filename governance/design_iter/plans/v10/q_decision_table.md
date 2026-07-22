# v10 启动决策表

> 本档是 v10 决策跟踪表，对应 `decisions.json` 的可视化版本。
> 完整决策内容见 `decisions.json`。

## 决策跟踪

| 决策 ID | Q ID | 议题 | 选择 | 状态 | 备注 |
|---|---|---|---|---|---|
| D-V10-001 | Q-V10-001 | OBJ 链接覆盖率阈值 | B（100%） | ✅ 已决 | 对齐 S4 §4.3.1 严格档位 |
| D-V10-002 | Q-V10-002 | 落地路径 | A（governance 优先） | ✅ 已决 | DNA 准则 1 + 准则 3 |
| D-V10-003 | Q-V10-003 | L3 门禁记录位置 | A（postflight_gate 项） | ✅ 已决 | 不分散管理 |
| D-V10-004 | Q-V10-004 | OBJ 未引用处理 | A（skip_reason 标注） | ✅ 已决 | 沿用 S4 五类表 |
| D-V10-005 | Q-V10-005 | 范围 | C（S6 + S7 双层） | ✅ 已决 | S6 生成 + S7 反向 |

## 执行阶段跟踪

| Phase | 内容 | 状态 | 涉及文件 |
|---|---|---|---|
| 1 | governance/PLAN.md（本档）| ✅ 已完成 | plans/v10/PLAN.md |
| 2 | 约束层 | ⏳ 待执行 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` / `.cursor/rules/STAGE_S6_TEST_CASES.mdc` / `.cursor/rules/DNA_3Q_CHECK.mdc` |
| 3 | 实现层 | ⏳ 待执行 | `ai_workflow/test_case_formatter.py` |
| 4 | 数据层（回填） | ⏳ 待执行 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` |