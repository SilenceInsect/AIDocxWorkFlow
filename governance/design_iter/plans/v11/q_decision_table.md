# v11 启动决策表

> 本档是 v11 决策跟踪表，对应 `decisions.json` 的可视化版本。

## 决策跟踪

| 决策 ID | Q ID | 议题 | 选择 | 状态 | 备注 |
|---|---|---|---|---|---|
| D-V11-001 | Q-V11-001 | S5 TP 必填 feature_point_id | A（必填） | ✅ 已决 | 硬契约 |
| D-V11-002 | Q-V11-002 | S6 TC 必填 s5_ref | A（必填） | ✅ 已决 | 硬契约 |
| D-V11-003 | Q-V11-003 | FP 覆盖率阈值 100% | A（100%） | ✅ 已决 | 对齐 v10 OBJ 档位 |
| D-V11-004 | Q-V11-004 | 未覆盖 FP skip_reason | A（5 类复用） | ✅ 已决 | 与 OBJ 同表 |
| D-V11-005 | Q-V11-005 | 现有 TC 映射策略 | B（全部重审） | ✅ 已决 | 用户明确"现有的不一定对" |

## 关键洞察

> 用户原话："现有的不一定对，87个FP"

**含义解读**：
- 当前 38 个 TC 是 S6 阶段 LLM 自由生成 → Phase 4 round-robin 分配 FP → 不保证 TC 实际验证业务与 FP 描述匹配
- 必须**重审**：每个 TC 看其功能描述 / 操作步骤 / 预期结果，是否**真**在验证它声称的 FP
- 错配的 TC → 改 `feature_point_id` 到正确 FP 或加 `skip_reason`
- 缺 FP → 补 TC（增加新的 49 个 TC）或标 `skip_reason`
- 全程要有 s5_ref 字段支撑追溯

## 执行阶段跟踪

| Phase | 内容 | 状态 | 涉及文件 |
|---|---|---|---|
| 1 | governance/PLAN.md（本档）| ✅ 已完成 | plans/v11/PLAN.md / decisions.json / q_decision_table.md |
| 2 | 约束层 | ⏳ 待执行 | `.cursor/skills/aidocx-s5-test-points/SKILL.md` / `.cursor/skills/aidocx-s6-test-cases/SKILL.md` / `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` / `.cursor/rules/STAGE_S6_TEST_CASES.mdc` |
| 3 | 实现层 | ⏳ 待执行 | `ai_workflow/test_case_formatter.py`（升级 _validate_obj_linkage → _validate_obj_fp_linkage） |
| 4 | 数据层 | ⏳ 待执行 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`（38 TC 重审 + 87 FP 全覆盖 + 38 个 s5_ref） |
