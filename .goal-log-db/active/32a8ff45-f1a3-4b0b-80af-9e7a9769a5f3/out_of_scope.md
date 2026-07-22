# out_of_scope.md（Goal 禁区清单 — v3.01 用例审查）

> **本档按 GL-003 强制产出**——`.cursor/skills/goal-loop/SKILL.md` §3.1：每类至少列举 1 项（若确实无禁区，写"（无）"）。
> **执行过程中发现新越界项，同步更新本文件。**
> **继承**：本 Goal 继承上一 Goal (`bad7a7fa-4135-42c2-9a9e-b5233cb454d5`) out_of_scope §10 的技术栈禁区与职责边界禁区。

---

## 功能禁区

- **不动** `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`（331 条用例，隔离保护）
- **不动** `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx`（**本轮只审查不修复**——Round 2 Act 才动）
- **不动** `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json`（上游 S5 产物）
- **不动** `workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」/backlog.json` / `requirement_objects.json`（上游 S2 产物）
- **不动** `workflow_assets/游戏道具商城系统/v3.01/「S4 流程图导出」/business_flow.md/json`（上游 S4 产物）
- **不动** `workflow_assets/游戏道具商城系统/v3.01/「S1 需求评审」/review_report.*` / `requirement_objects.*`（上游 S1 产物）
- **不动** 上一 Goal (`bad7a7fa-4135-42c2-9a9e-b5233cb454d5`) 的 snapshot.json / audit_*.md / review_*.md / out_of_scope.md
- 本 Goal 只产出 3 份**审查报告**（tester / architect / pm）——不产出修复代码 / 重导产物 / audit_13.md / review_13.md

## 技术栈禁区

- 不引入新依赖（`pip install` 任何包都禁止；只使用 Python 标准库 + 仓库现有依赖 + openpyxl）
- 不使用 `eval()` / `exec()` / `compile()` 动态执行
- 不调用 LLM API（保持纯 deterministic + 主 Agent 推理）
- 审查脚本若新增 `.py`，必须含 `def self_test() -> int` + `--self-test` argv 分支（按 DNA §9.1.1 豁免条款 1/2）
- 所有代码改动必须 `python3 -m py_compile <file>` 通过（按 DESIGN_AND_EXECUTION_STANDARDS.mdc §3.7）

## 职责边界禁区

- 不重做 s6_generate.py 主流程（v3.01 已收敛 331/331 Ready，**不动**）
- 不修复 auto_reviewer.total_cases 字段缺失（属上一 Goal 已知 blocker，移交 Round 14）
- 不实现 s6_report.py（属上一 Goal 已知 follow-up）
- 不动 `.cursor/rules/*.mdc` 与 `.cursor/skills/*/SKILL.md`（约束档 SSOT 不在本 Goal 改造范围；本 Goal 只**审查**用例实质问题，**不改** SSOT 文档）
- 不动 `goal-loop SKILL.md` / `goal_snapshot.py` / `goal_parallel_executor.py`
- 不 commit（用户未授权 commit；所有改动保留在工作区，待用户审核）
- 不开 subagent（独立完成 3 份审查——资深测试 + 架构师 + 资深产品视角本就是主 Agent 推理）
- 不调起新一轮 background subagent（本任务本身就是 worker）