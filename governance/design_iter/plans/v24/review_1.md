# review_1.md — v24 Round 1 深度复盘

## 1. 缺陷汇总（去重、排序）

### 1.1 实际修复的缺陷（4 项）

| # | 缺陷 ID | 缺陷描述 | 严重度 | 修复位置 |
|---|---|---|---|---|
| 1 | D-24-01 | 测试 setup 用 v7 路径布局（`req_root/「stage」/ver`），preflight 用 v8 模板（`req_root/ver/「stage」`）→ preflight 找不到输入 | BLOCKER | `tests/test_s5_s6_s7_closure.py` setup 6 处 v7→v8 迁移 |
| 2 | D-24-02 | `_prompt_purge_existing` 在非 TTY 一律返回 `auto_keep` → `run_stage` 短路 SKIPPED → preflight 永远跑不到 | BLOCKER | `tests/test_s5_s6_s7_closure.py` setUp/tearDown 加 `unittest.mock.patch` |
| 3 | D-24-03 | runtime 内部 v7/v8 双布局不一致（`save_stage5_output` v7 / `format_test_cases` v8 / `save_stage7_output` v8 / `get_stage_dir` v7）→ 测试需在 v7+v8 双路径写输入并同步产物 | BLOCKER | `_run_s5` / `_run_s6` / `_run_s7` wrapper：v7↔v8 互相复制 |
| 4 | D-24-04 | `_CHECK_CACHE` 进程内共享，跨测试用例状态污染 → 上一用例失败的 postflight 状态被下一用例命中缓存 | BLOCKER | `tests/test_s5_s6_s7_closure.py` setUp 内 `ai_workflow.consistency_check._CHECK_CACHE.clear()` |

### 1.2 暴露的体系问题（3 项 → 见 follow_up_items）

| # | 问题 ID | 描述 | 严重度 | 是否已修 |
|---|---|---|---|---|
| 5 | SYS-024-01 | runtime v7/v8 布局不一致（核心问题），应全局收敛 | MAJOR | 否（遗留 → v25） |
| 6 | SYS-024-02 | `format_test_cases` / `save_stage7_output` 内部调 postflight 污染 `_CHECK_CACHE` | MAJOR | 否（防御在调用方） |
| 7 | SYS-024-03 | `_CHECK_CACHE` 跨进程污染理论可能 | MINOR | 否（仅同进程测试间） |

## 2. 根因定位

### 2.1 机制问题

- **runtime 演化与规范不同步**：v8 布局是 `DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.6 规范（v8 主轴变更），但核心运行时函数（`_stage_dir` / `get_stage_dir` / `save_stage5_output` / `format_test_cases` / `save_stage7_output`）未全部迁移。这是**机制层面**的债务，是 4 个失败的根本物理根因。
- **`_CHECK_CACHE` 设计**：作为进程内缓存（key=`stage:req_name:version:phase`），没有跨用例重置机制，导致单测间状态污染。这是**机制层面**的次要根因。
- **`_prompt_purge_existing` 设计**：为人类交互设计（TTY prompt），未考虑 CI / 自动化 / 测试环境的非 TTY 短路策略。这是**机制层面**的次要根因。

### 2.2 规范问题

- **`DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.6 与 runtime 实际行为冲突**：规范说 v8，但运行时多数函数写 v7。这是**规范与实现分裂**。
- **`STAGE_CONTRACTS` 与 `get_stage_dir` 冲突**：模板用 v8，运行时函数用 v7，postflight 跑 `STAGE_CONTRACTS` 校验时实际文件在 v7。这是**双源 SSOT**。

### 2.3 习惯问题

- **测试 setup 沿用旧代码风格**：commit `10d0c89` 引入测试时，runtime 已混合 v7/v8，作者未察觉差异直接用 v7 写。这导致 4 个失败用例**自引入起就 fail**（沉默失败，2.5 个月未被发现）。
- **测试用例缺失自检**：项目 `pytest tests/` 全套**从未在 CI/本地完整跑过**，否则 4 个失败会立刻暴露。

## 3. 可落地修复方案

### 3.1 本轮已落地（DT-1.A 路径）

| 修复 | 文件 | 验证方式 |
|---|---|---|
| 测试 setup v7→v8 迁移 | `tests/test_s5_s6_s7_closure.py` | pytest 7/7 PASS |
| mock `_prompt_purge_existing` | `tests/test_s5_s6_s7_closure.py` setUp | 同上 |
| 阶段 wrapper（`_run_s5`/`_run_s6`/`_run_s7`）处理 v7↔v8 双路径 | 同上 | 同上 |
| `_CHECK_CACHE` setUp 清空 | 同上 | 同上 |
| CHANGELOG.md Unreleased ### Fixed 段 | `CHANGELOG.md` | Read 确认 |

### 3.2 遗留项 / 下轮建议（follow_up_items）

| 优先级 | 修复方向 | 影响范围 | 建议执行 Goal |
|---|---|---|---|
| **MAJOR** | 全局迁移 `_stage_dir` / `get_stage_dir` / `save_stage5_output` / `format_test_cases` / `save_stage7_output` 到 v8 布局；`STAGE_CONTRACTS` / `resolve_contract_path` 维持 v8 → **所有路径统一 v8** | `ai_workflow/conversation_skills.py` / `runtime_contracts.py` / `test_case_formatter.py` / 全部相关测试 | v25（必须在 v24 后立刻跟进，否则新引入的 stage_callable 都需 wrapper） |
| **MAJOR** | 在 `format_test_cases` / `save_stage7_output` 内部 postflight 调用前增加"输入文件预检 + 早返回（不写 _CHECK_CACHE）"防御，避免污染调用方 | `ai_workflow/test_case_formatter.py:187` / `conversation_skills.py:224` | v25（同上） |
| MINOR | `_prompt_purge_existing` 在 `PYTEST_CURRENT_TEST` 环境变量存在时强制返回 `purge` | `ai_workflow/conversation_skills.py` | v25 可选 |
| MINOR | `_CHECK_CACHE` key 加入 `pid` 隔离跨进程 | `ai_workflow/consistency_check.py` | v25 可选 |

### 3.3 影响范围声明

| 范围 | 影响 |
|---|---|
| **生产代码** | **零修改**（仅测试侧 + CHANGELOG） |
| **测试** | `tests/test_s5_s6_s7_closure.py` 8 处修改（路径迁移 + mock + wrapper + _CHECK_CACHE 清空 + 预写占位符） |
| **文档** | `CHANGELOG.md` + `governance/design_iter/plans/v24/{PLAN,out_of_scope,audit_1,review_1,CONVERGED}.md` |
| **CI / 其它测试** | `pytest tests/` 26/26 PASS，无回归 |
| **可回滚性** | `git revert` 单 commit 即可（CHANGELOG 和 PLAN.md 单独 commit 或合并 commit 均可识别） |

## 4. v23 → v24 演进对比

| 维度 | v23（CONVERGED） | v24（本轮） |
|---|---|---|
| 范围 | 错误目录根因修复（strip 防御） | 4 个预先存在失败的修复 |
| 改动文件 | runtime（修复实现） | 测试 + CHANGELOG（按 DT-1.A 选改测试侧） |
| 价值标准达成 | 全 PASS | 全 PASS（含 v23 未识别的 SYS-024-01/02/03 3 个体系问题） |
| 遗留项 | 0 | 3（1 MAJOR + 2 MINOR） |

## 5. 元层观察

- **DT-1.A（改测试侧）选对了**：若当时选"改 runtime"会触碰更多函数（`_prompt_purge_existing` / `_stage_dir` / `get_stage_dir`），影响面更大，回滚成本高。改测试侧风险最低、收敛最快。
- **深度根因（第 3 个：runtime 内部 v7/v8 不一致 + 内部 postflight 污染缓存）是 Round 1 实战中发现的**，v23 PLAN 的根因清单不完整。这是**实战 > 文档**的典型例子。
- **测试 setup 写错导致 4 个失败沉默 2.5 个月**——暴露项目测试规范薄弱。建议 v25 引入"新增测试必须先在 pytest 跑通才能 commit"的 CI 门禁。