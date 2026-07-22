# out_of_scope.md（Round 16 Goal 禁区清单）

> **新 goal_id**：`6d3edb03-352d-4a3f-921c-b880db0625f5`
> **关联 Plan**：`governance/design_iter/current/goal_round16_followup_and_format.md`

## 功能禁区

- ❌ 不重生成 v3.01 test_cases.json（继承 Round 12 out_of_scope §10）
- ❌ 不重跑 S5/S6 prompt 治理（推 v3.02 单独治理）
- ❌ 不修改 S7 review_report schema（与本 Goal 无关）
- ❌ 不改 stage_gatekeeper / coverage_validator（与本 Goal 无关）
- ❌ 不修复 v3.01 数据 step/expected 错位（推 v3.02 prompt 治理；属 FU-A4）

## 技术栈禁区

- ❌ 不引入新依赖（如 pandas / xlsxwriter）—— 沿用 openpyxl
- ❌ 不改 `apply_l1_l2_status` / `apply_l1_l2_status_per_case` 行为契约
- ❌ 不动 L1S6Validator / L2S6Validator 校验规则
- ❌ 不动 v17 单步原则的 LLM 生成约束语义（仅加同源合并例外 + 测试设计层级原则）

## 职责边界禁区

- ❌ 不动 auto_reviewer / S7 审查链路
- ❌ 不动 S5 test_points.json / S2 requirement_objects.json / S3 prototype.json
- ❌ 不 commit（用户明确禁止）
- ❌ 不重置 / clear 用户已有未提交改动
- ❌ 不开 subagent（Round 12 已禁止）
