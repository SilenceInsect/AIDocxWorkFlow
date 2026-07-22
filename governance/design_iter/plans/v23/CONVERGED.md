# v23 CONVERGED — 错误目录产出根因审查与修复

## 收敛状态

- **状态**: `achieved`
- **goal_id**: 见 `.goal-log-db/active/80257891-99f3-4828-b23c-0fcb85b1b13e/snapshot.json`
- **收敛轮次**: Round 1 / 1(一次达成)
- **收敛时间**: 2026-07-19

## 完成内容

### A. 问题诊断
- 锁定 2 个错误目录根因: `workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」 ` 与 `「S4 流程图导出」 ` (末尾 1 空格)
- 内部分析: 它们只含 `.DS_Store` (macOS 自动) 与空目录嵌套 `Users/gleon/...`(macOS 自动)
- 代码层根因: SSOT 路径计算函数 (`get_stage_dir` / `_stage_dir` / `_resolve_stage_path`) 信任上游字符串,未做 strip

### B. 代码修复
- 3 个 SSOT 函数加 `.strip()`,影响 3 个 .py:
  - `ai_workflow/runtime_contracts.py::get_stage_dir`
  - `ai_workflow/conversation_skills.py::_stage_dir`
  - `ai_workflow/conversation_skills.py::_resolve_stage_path`

### C. 磁盘清理
- 安全删除 2 个错误目录(含 .DS_Store)
- 验证 v3.01 父目录结构回到标准 6 阶段

### D. 验证
- `python3 -m py_compile` 通过
- 动态调用三个函数确认返回值字节数 = 21(= 正常目录字节数)
- baseline 测试: 已存在的 4 个失败与本次改动无关(对比 git stash 前后一致)

## 验收证据

| 项 | 证据 |
|---|---|
| V-01 错误目录已清 | Python 脚本输出 `remaining_bad = []`, v3.01 现 6 个阶段目录 + .DS_Store |
| V-02 代码定位 | runtime_contracts.py 第 383-388 行 / conversation_skills.py 第 24-37 行 / 第 1278-1283 行 |
| V-03 strip 防御 | 三处都加 `.strip()`,已 grep 验证 |
| V-04 端到端验证 | 三个函数返回值 path.name = `「S2 需求拆解」`,byte_len = 21(等于正常目录) |
| P-01 落档 | v23/PLAN.md + out_of_scope.md + audit_1.md + review_1.md(4 文档齐) |
| P-02 根因完整 | audit_1.md § V-02 含文件+函数+行号 |
| range 合规 | out_of_scope.md 8 项禁区全部未触碰 |

## 自迭代记录

- **Round 1**: Plan → Act → Audit → Review → Iterate(一次达成)
- 反模式扫描: 未命中"只产出不验证 / 静默删除 / 范围漂移" 等
- 防御层次: SSOT strip(本轮) + 未来 L3 hook directory_lints(follow_up)

## 遗留项(follow_up_items)

| description | severity | suggested_fix | source_round | source_criterion |
|---|---|---|---|---|
| L3 hook 缺 directory_lints 扫盘防御 | MINOR | 新建 `.cursor/hooks/directory_lints.py`,afterFileEdit 触发 | 1 | V-03 |
| 中文路径手敲易引入空格(Agent 提示) | MINOR | conversation_skills prompt 顶部加禁手敲提示 | 1 | V-02 |
| unittests 缺 strip 测试用例 | MINOR | 新建 tests/test_stage_dir_path_safety.py | 1 | V-03 |

## 影响范围

| 文件 | 类型 | 行数变化 |
|---|---|---|
| `ai_workflow/runtime_contracts.py` | modify | +5 (docstring + .strip) |
| `ai_workflow/conversation_skills.py` | modify | +6 (2 处 .strip + 注释) |
| `workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」 ` | delete (空目录) | -6148 (主要是 .DS_Store) |
| `workflow_assets/游戏道具商城系统/v3.01/「S4 流程图导出」 ` | delete (空目录) | 0 (无文件) |
| `governance/design_iter/plans/v23/PLAN.md` | new | 73 |
| `governance/design_iter/plans/v23/out_of_scope.md` | new | 28 |
| `governance/design_iter/plans/v23/audit_1.md` | new | 178 |
| `governance/design_iter/plans/v23/review_1.md` | new | 132 |
| `.goal-log-db/active/<id>/snapshot.json` | new | — |

**回滚步骤**:
```bash
git checkout ai_workflow/runtime_contracts.py ai_workflow/conversation_skills.py
# 重新 mkdir 不会重建,因为原错误目录是空的
```
