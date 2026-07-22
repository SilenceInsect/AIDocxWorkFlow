# out_of_scope.md（Goal 禁区清单）

> **本档按 GL-003 强制产出**——`.cursor/skills/goal-loop/SKILL.md` §3.1：每类至少列举 1 项（若确实无禁区，写"（无）"）。
> **执行过程中发现新越界项，同步更新本文件。**

## 功能禁区

- 不涉及 S1-S5 阶段产物改造（输入材料范围锁定在 S6 产出 + S7 review_report）
- 不涉及 S8 自迭代阶段（Deprecated 状态由 S8 赋予，本 Goal 只定义枚举与转换，不实现 S8 写回逻辑）
- **不动** `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`（用户线上产物，331 条用例，隔离保护）
- **不动** 任何已有 `review_report.json` 历史产物（v3.01 暂无 review_report，但 v1.0 等历史版本的 review_report 禁止回溯改动）

## 技术栈禁区

- 不引入新依赖（`pip install` 任何包都禁止；只使用 Python 标准库 + 仓库现有依赖）
- 不使用 `eval()` / `exec()` / `compile()` 动态执行（任何代码片段必须显式写入文件）
- L2 校验器必须基于 L1 校验器接口扩展（duck-type 实现 `validate(test_cases) -> list[dict]`），不另起新框架
- case_status_writer / s7_status_writer 必须独立模块（不嵌入已有 .py，必须新增文件）
- 所有新增 .py 必须含 `def self_test() -> int` + `--self-test` argv 分支（按 DNA §9.1.1 豁免条款 1/2）
- 所有代码改动必须 `python3 -m py_compile <file>` 通过（按 DESIGN_AND_EXECUTION_STANDARDS.mdc §3.7）

## 职责边界禁区

- 不动 S7 的整体 SSOT（只在 SSOT 范围内"移除废弃噪音" + 加引用段，不修改 v14 废除 PASS/FAIL 硬判决的设计）
- 不动 goal-loop runner 自身（`goal_loop_runner.py` 不存在，无需实现——本 Goal 走手动五段式）
- 不修改 AGENTS.md / DNA_3Q_CHECK.mdc / goal-loop SKILL.md（约束档 SSOT 不在本 Goal 改造范围）
- 不动 `.md / .mdc` 以外的 `.json` 业务产物（除 test_cases.json 用例状态字段写回 + review_report.json 字段清理外）
- 不 commit（用户未授权 commit；所有改动保留在工作区，待 Plan 审核后用户明确决定）
- 不调起新一轮 background subagent（本任务本身就是 worker，禁止 spawn sub-subagent）