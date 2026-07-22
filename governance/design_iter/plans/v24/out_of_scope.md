# v24 out_of_scope — 4 测试失败根因审查的禁区清单

## 功能禁区

- 不重写 `_prompt_purge_existing` 整套 prompt 逻辑（保持 v8 SKILL.md 决策承诺）
- 不动 `runtime_consistency_gate` 内部实现（仅观察，不改）
- 不重构 `conversation_skills.py` `run_pipeline` 整体编排逻辑
- 不修改 `STAGE_S*.mdc` / `SKILL.md` 阶段规则（除非本次根因证明规则与实现不一致）
- 不删除任何测试用例（即使是"看似不合理的"测试——只能改 assertion 或加 skip 标记）

## 技术栈禁区

- 不引入新依赖（pytest 已装，禁止新增 mock 库）
- 不修改 `.venv/` / `pyproject.toml` / `requirements.txt`
- 不改 pytest 配置文件（除非 DT-3 选 C 需要加 skip marker）

## 职责边界禁区

- 不修 `tests/test_goal_parallel.py` 任何测试
- 不修 `tests/test_s1_markitdown_path.py` 任何测试（本 Goal 仅限 S5/S6/S7 闭环测试）
- 不动 `workflow_assets/游戏道具商城系统/v3.01/` 实际产物（与本 Goal 无关）
- 不重跑 v23 治理档的所有审计流程（v23 已 CONVERGED，闭环）

## 待定禁区（DT 决策后补充）

- 是否修改 `ai_workflow/conversation_skills.py` `run_stage` 函数 → 取决于 DT-1.B/C 是否被选中
- 是否修改 `ai_workflow/stage_gatekeeper.py` → 取决于 DT-2.A 是否需深入
