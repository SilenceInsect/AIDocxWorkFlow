# out_of_scope.md — v3.03 Goal 禁区清单

## 功能禁区
- ❌ 不改 v3.01 `test_cases.json`（P-001 守住 SSOT）
- ❌ 不删 Round 17 历史 xlsx 备份（P-002 字节不变）
- ❌ 不改 v3.01 S5/S6 阶段上游产物（backlog / tp / flow）
- ❌ 不动 v3.02 CONVERGED 文档（v3.02 已闭环，是审计锚点）
- ❌ 不修 V-302-001/V-003/V-004/V-005（v3.02 报告已认定 PASS 或降级 MAJOR；本 Goal 不重开）
- ❌ 不修 S6 校验器脚本（validators/l1_s6.py / l2_s6.py）
- ❌ 不重做 OBJ 业务逻辑定义（MODULES.md）— P0 矩阵是覆盖率策略，不动 MODULES.md

## 技术栈禁区
- ❌ 不引入新 Python 依赖（P-006）
- ❌ 不改 `case_id_and_field_normalizer.enforce_obj_p0_coverage` 函数签名（P-003）
- ❌ 不改 `normalize_payload` 函数签名
- ❌ 不改 `_save_xlsx` / `_partition_cases_for_xlsx`（写入链路）
- ❌ 不调用 LLM / 网络 / eval
- ❌ 不动 `case_status_writer.py`（status 与 priority 是正交维度）

## 职责边界禁区
- ❌ 不动 goal-loop SKILL.md / hooks.json / AGENTS.md（v27 刚改完）
- ❌ 不动 v3.01 stage outputs（review_report.md / fail_report 等）
- ❌ 不修复 mini payload self-test 的另 3 个 OBJ（test-only fixture，不动）
- ❌ 不为提升覆盖率把 MAJOR 改 BLOCKER（仅补 1 P0，不增加等级）
- ❌ 不重跑整个 S6 生成（不触发上游 LLM/产物重算）

## 历史坑点禁区
- ❌ 不直接改 test_cases.json（即便 JSON 也有 12/16 缺 P0 — 但强制约束是不动 JSON）
- ❌ 不破坏 enforce_obj_p0_coverage 的 idempotency（line 400 `if c.get("_auto_promoted")`）
- ❌ 不把"OBJs_already_covered" 4 OBJ 的 P0 移到其他 OBJ（P0 集中度是 SSOT；只补缺 OBJ）
- ❌ 不为追求 PASS 把 Draft case 优先级改 P0（enforce_obj_p0_coverage 已自动处理 Draft，需保持现行逻辑）

## 本 Goal 完成后禁止
- ❌ 不在 xlsx 主表追加未在 test_cases.json 出现的行
- ❌ 不修改 Round 17/18 治理档
- ❌ 不为 PASS 删除验收项（反模式）
- ❌ 不得回退 v3.02 已 PASS 的 V-001/V-004
