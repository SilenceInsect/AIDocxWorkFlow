# v23 方案归档 — 错误目录产出根因审查与修复

## 元数据

- **方案版本**: v23
- **创建时间**: 2026-07-19
- **上游**: v22 goal-loop multitask 三层并行化(已 CONVERGED)
- **触发**: 用户请求 `/goal-loop 审查错误目录产出根因，修复相关错误逻辑`
- **状态**: 进行中 (Round 1)

## 目标陈述

`workflow_assets/游戏道具商城系统/v3.01/` 下存在 2 个错误产物目录——

| 错误目录 | 字节 | 内部内容 |
|---|---|---|
| `「S2 需求拆解」 ` (末尾 1 空格) | 22 字节 | 空 + `.DS_Store` + 嵌套 `Users/gleon/...` |
| `「S4 流程图导出」 ` (末尾 1 空格) | 25 字节 | 空 + 嵌套 `Users/gleon/...` |

对应的正常目录同名同字节结构,只是末尾**没有空格**——正常目录里有产物(backlog.json/md/requirement_objects.json;business_flow.json/md),错误目录里**只有 macOS `.DS_Store` 与嵌套的绝对路径目录**。

**根因假设(待验证)**: 某个 .py 脚本在调用 `os.makedirs` / `os.path.join` 时,
- `base = "workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」"` (无尾空格)
- 同时另一条调用路径使用了 `stage_dir()` 返回值末尾含空格、或 `os.path.join("base/", " 「S2...」")` 多打了一个空格
- 两个调用都执行了 `mkdir`,生成了"正常目录 + 带空格目录",但代码中后续的 `write()` 只对正常路径生效,带空格目录仅被 mkdir 而无文件写入
- `.DS_Store` 是 macOS Finder 自动写入
- 嵌套的 `Users/gleon/...` 表明绝对路径被作为相对路径传入 `os.path.join`,触发 Python `os.path.join` 半绝对路径覆盖前置段的语义

> **v23 任务目标**: 在代码层找到上述 bug 并修复,清理两个错误目录,补防御性检查。

## 验收标准

### value_criteria(外部价值)

| ID | 内容 | 严重度 |
|---|---|---|
| V-01 | 错误目录 `「S2 需求拆解」 ` 与 `「S4 流程图导出」 ` 已被识别根因并从磁盘移除 | BLOCKER |
| V-02 | 在 `ai_workflow/*.py` / `tests/*` / `.cursor/skills/*` 中找到创建该错误目录的代码,定位到具体函数与行号 | BLOCKER |
| V-03 | 在代码中加入"目录名 normalize + 末尾空格禁止"防御(如 `os.makedirs(strip_name)` 或 `pathlib.Path` rstrip),确保再运行时不再产生带空格目录 | BLOCKER |
| V-04 | 修复后,执行一次端到端生成,验证产物落到正确目录、无错误目录残留 | MAJOR |

### process_criteria(内部过程)

| ID | 内容 |
|---|---|
| P-01 | 在 `governance/design_iter/plans/v23/` 落档 `PLAN.md`、`out_of_scope.md`、每轮 `audit_<N>.md` + `review_<N>.md`,最终 `CONVERGED.md` |
| P-02 | 错误目录的根因必须列出(1)文件路径、(2)函数名、(3)行号 |
| P-03 | 修复方案必须含 diff、影响范围、回滚步骤 |
| P-04 | `value_ratio >= 0.6`(实测 4/4 = 1.0) |

## out_of_scope 边界

详见 `out_of_scope.md` ——本 goal 不重写整个流水线;只动用了错误目录产出的根因 + 防御。

## 执行计划

| Round | 主题 | 状态 |
|---|---|---|
| Round 1 | grep 代码找根因 + 修复 + 清理错误目录 + 端到端验证 | 本轮 |
| (后续) | 待 Round 1 复盘决定 | — |

## 产物清单(预计)

| 路径 | 变更类型 |
|---|---|
| `governance/design_iter/plans/v23/PLAN.md` | 新建 |
| `governance/design_iter/plans/v23/out_of_scope.md` | 新建 |
| `governance/design_iter/plans/v23/audit_1.md` | 新建 |
| `governance/design_iter/plans/v23/review_1.md` | 新建 |
| `ai_workflow/<...>.py` 或 `.cursor/skills/aidocx-*/SKILL.md` | 根因修复(待定位) |
| `workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」 ` | 删除 |
| `workflow_assets/游戏道具商城系统/v3.01/「S4 流程图导出」 ` | 删除 |

## 落档协议执行记录

- Round 1: PLAN.md + out_of_scope.md + 根因定位 + 修复 + 测试(本轮)
