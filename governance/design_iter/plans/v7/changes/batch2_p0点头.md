# v7 P0 决策点头（Batch 2）

> 用途：记录 Q-501~Q-547（共 20 条 P0）的决策点头结果
> 依据：v7/open_questions.md P0 节 + v7/decisions.json default_value
> 状态：Batch 2 执行中

## 决策规则

**批量点头原则**（D-702 "Q-501~Q-569 必答" 的子集）：

所有 P0 均采用 v7/open_questions.md 中的"当前默认"候选方案（A / B / C）。
若需 override，必须显式说明理由。

## P0 决策结果

| D-xxx | Q-xxx | 标题 | 点头结果 | 理由 |
|---|---|---|---|---|
| D-705 | Q-501 | S2.5 .mdc 缺 Step 0 | ✅ A | .mdc 是 SSOT，SKILL.md 是执行版——SSOT 补全 |
| D-706 | Q-502 | S5 .mdc 残留硬性数量指标 | ✅ A | v2.0 LLM 推理原则（不设硬数字）已确定 |
| D-707 | Q-503 | S5 TP JSON 字段名不一致 | ✅ A | tp_id + test_point_type 已在 SKILL.md 强约束 |
| D-708 | Q-504 | S6 .mdc 残留 18 种派生系数 | ✅ A | 与"不强制 1:N / 不强制 18 种方法"精神对齐 |
| D-709 | Q-505 | S6 TC JSON 字段名不一致 | ✅ A | case_id 已在 SKILL.md 强约束 |
| D-710 | Q-506 | S7 .mdc 三重残留 | ✅ A | S7 SKILL.md v2.0 已废弃硬判决 |
| D-711 | Q-507 | S8 .mdc PASS/FAIL 残留 | ✅ A | 与 S7 v2.0 对齐 |
| D-712 | Q-508~Q-519 | RULE_SKILL P1 12 条 | ✅ A | 补全 .mdc 缺失的 §1.4/§1.5 |
| D-713 | Q-525~Q-528 | SCRIPT_SKILL P0 4 条 | ✅ A | 脚本逻辑与 SKILL.md 对齐 |
| D-714 | Q-539~Q-540 | SKILL_LOGIC P0 2 条 | ✅ A(B) | S8/S3 与 S7 v2.0 对齐 |
| D-715 | Q-541~Q-543 | SKILL_LOGIC P0 3 条 | ✅ A | S3/S2/S5 命名规则/重名/必填 |
| D-716 | Q-544~Q-547 | SKILL_LOGIC P0 4 条 | ✅ A | S2.5/S5/S6/S7 细节对齐 |

## 落档执行记录

- Batch 2 写入 decisions.json（D-705~D-716 共 12 条 P0 决策）
- Batch 3 执行 9 阶段 .mdc 修复（按 D-705~D-716 执行）
