# v17 Goal Lock — 字段溯源方案闭环目标

> **本档作用**：v17 治理闭环的目标锁定——一句话目标、In/Out Scope、收敛判定、反模式、落档协议
> **基线方案**：`v17/PLAN.md`（182 行，6 阶段实施步骤 + 7 个 Q-V17-XXX）
> **前置分析档**：`v16_alternative_tc_proposal_20260717.md`（用户 2026-07-17 拍板"完全采纳 A"）
> **复盘档**：`v17_phase2_self_violation_postmortem_20260718.md`（§1.9 字段溯源版已修复 13 处违规）

---

## 1. 一句话目标

把 v16 锚点方案（7 项锚点校验）切换到字段溯源方案（obj_name/fp_name 字段精准匹配），同时保证：

1. L1 校验 0 错误通过
2. 产物字段语义清晰（Excel 直接读字段）
3. v3.01 87 TP / 87 TC 全部按新方案重写

---

## 2. 范围（In/Out of Scope）

### In Scope（必须做）

- STAGE_S5 §1.9 / STAGE_S6 §1.7 改写（已完成 §1.9，待改 §1.7）
- s5/s6 SKILL.md 改写（v16 NAME 段 → 字段溯源 NAME 段）
- AIDocxWorkFlow.mdc + DESIGN_AND_EXECUTION_STANDARDS.mdc + AGENTS.md + CHANGELOG.md 同步
- L1 校验脚本 6 处改写（l1_s5.py / l1_s6.py / test_case_formatter.py / auto_reviewer.py / ~~s6_report.py~~ **(Round 14 闭环：文件不存在，引用已废弃)** / check_field_completion.py）
- v3.01 87 TP + 87 TC 重写
- Excel 导出层结构化 schema

### Out of Scope（不做）

- v1.0/v2.0/v3.0 历史版本回溯（按 open_questions Q-V17-003 默认决议冻结）
- L2/L3 Hook（按 open_questions Q-V17-004 默认决议不改）
- 8 模块子模板重写（保留 v16 现状）
- 8 模块 O_boundary.md（保留 v16 现状）

---

## 3. 收敛判定（Completion Criteria）

满足以下全部 → v17 闭环：

- [ ] 5 个规则文档全部改为"字段溯源版"且 0 版本标记违规
- [ ] 6 个代码文件全部改完，py_compile + self-test 10/10
- [ ] v3.01 87 TP / 87 TC 重写 + L1 校验 100% pass
- [ ] Excel 导出测试通过（10 字段映射 + 1 行 1 TC）
- [ ] AGENTS.md + CHANGELOG.md 同步更新
- [ ] INDEX.md / INDEX.json 标 v17 = current（CLI scripts/design_iter.py 生成）

---

## 4. 反模式（Anti-pattern）

- ❌ 把版本号写进规则正文
- ❌ 单 turn 改 ≥ 3 个文件
- ❌ 跳过 grep 自检
- ❌ 不 Read 上游就动手
- ❌ 把"候选规则"当"已发布硬约束"

---

## 5. 落档协议

- 本档已落档
- 修改文件数：1
- 单次响应 tool call ≤ 10