# out_of_scope.md（Goal 禁区清单）

> **本清单是 v23 goal-loop 的范围护栏（GL-003）。命中禁区 → 立即暂停主任务，触发 DT 决策任务。**

## 功能禁区

- **不动其它已 CONVERGED 的方案档**：v13 ~ v22 任何 `PLAN.md` / `CONVERGED.md` / `CHANGELOG.md` 不允许修改——除非与本 goal 直接相关
- **不动 `resource/` 目录**：输入材料不重写、不搬迁、不 git add
- **不动 `.gitignore` 与 `.cursor/hooks.json`**：除非发现 hook 自身存在类似 bug（需先触发 DT）

## 技术栈禁区

- **不引入新依赖**（`requirements.txt` / `pyproject.toml` 不动）：修复用 Python 标准库 (`pathlib`, `os`, `string`) 完成
- **不修改 `goal_snapshot.py` 的 schema**：本次 bug 与 snapshot 无关，不要顺手"重构"
- **不修改 `goal_parallel_executor.py`**：同理非本次根因

## 职责边界禁区

- **不重写流水线**：S2 / S4 业务逻辑不动；只修"目录名拼接"的纯基础设施 bug
- **不修改 `.cursor/rules/*.mdc` 阶段规则**：除非发现规则文字指引到了错误目录名（极小概率）
- **不清理 macOS 系统文件**（`.DS_Store`）：归 macOS Finder 管理，不入 git，不在工程改动范围

## 关键边界判断

| 情形 | 判断 |
|---|---|
| 找到根因但修复需要改 5+ 个文件 | 暂停 → DT 决策（是否缩范围到 grep + 防御） |
| 找到根因但需要改 .mdc 规则 | 先列影响范围 → 问用户是否同步改约束 |
| 错误目录内部未发现的隐藏产物 | 先用 Python 脚本精确列出再删，**不**用 `rm -rf` |
