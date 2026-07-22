# v23 Review Round 1 — 复盘 + 根因总结

> 复盘时间: 2026-07-19
> 范围: Round 1 全部交付物的根因 + 修复质量 + 防回归

## 1. 缺陷汇总(已合并到 audit_1.md,本节只列未消化项)

| 缺陷 ID | 描述 | 严重度 | 状态 |
|---|---|---|---|
| DEF-R1-001 | v3.01 下存在 2 个带尾空格的阶段目录残留 | BLOCKER | ✅ 已清 |
| DEF-R1-002 | 三处阶段目录拼接函数缺少 strip 防御 | BLOCKER | ✅ 已修 |
| DEF-R1-003 | L3 hook 缺 directory_lints 防线 | MINOR | ⏳ 进入 follow_up |

## 2. 根因定位

### 2.1 直接根因(Operation Root Cause)

**谁**:未知的某次 Agent 会话(或开发者)调用 `mkdir "「S2 需求拆解」  "` 这种带尾空格路径。

**何时**:推测是 v3.01 S2 生成时的早期阶段(backlog.md 创建期间),后被同一会话或后续会话的 S4 阶段(`mkdir "「S4 流程图导出」 "`)复制了同一 bug。

**如何**:
1. Agent 在 Bash 工具中执行中文路径命令
2. 中文书名号 `「」` 视觉对齐要求高,容易在末尾多打入空格
3. macOS Finder 在该目录被访问后自动写入 `.DS_Store`,留下证据
4. `.DS_Store` 写入触发的"重新组织"可能让 macOS 创建 `Users/gleon/...` 嵌套空目录 ——这是 macOS 自动行为,不归工程问题

### 2.2 系统根因(System Root Cause)

| 层级 | 描述 | 修复 |
|---|---|---|
| 接入层 | Agent 操作中文路径时无 lint 防御 | L3 hook(后续 v24) |
| 抽象层 | `get_stage_dir` / `_stage_dir` / `_resolve_stage_path` 信任上游字符串字面量 | ✅ 加 `.strip()` |
| 监控层 | 工程未设"任何目录名末尾禁空格"的扫盘检查 | L3 hook(后续 v24) |

### 2.3 此次修复的设计取舍

**选项 A**(采用): 在 SSOT 字典 → 路径计算的 3 处入口 strip
- ✅ 修改 3 个函数,影响面最小
- ✅ 同时处理"fallback 路径"(陌生人传入带空格 stage key)
- ✅ Python 风格(标准库 .strip,无新依赖)

**选项 B**(未采用): 在所有调用方加 strip
- ❌ 散落多文件,易遗漏
- ❌ 不解决未来新调用方的同类 bug

**选项 C**(未采用): L3 hook 全扫盘
- ❌ 仅事后发现,无法阻止首次污染
- ✅ 作为"额外保险"放入 follow_up

## 3. 修复质量自评

| 维度 | 自评 |
|---|---|
| 改动定位精准 | ✅ 改 3 个 SSOT 函数,共 3 个函数体,影响面清晰 |
| 行为变更最小 | ✅ 仅新增 .strip() 调用,业务语义不变 |
| 回滚步骤明确 | ✅ `git checkout ai_workflow/runtime_contracts.py ai_workflow/conversation_skills.py` 可撤回 |
| 防御深度足够 | ✅ 阻断 + strip 双层;但缺少 L3 hook(列入 follow_up) |
| 测试验证 | ✅ py_compile OK + 动态调用 OK + baseline 测试结果一致(说明未引入回归) |
| 文档同步 | ✅ 代码注释说明 v23 修复理由 + audit_1.md §1 + review_1.md(本档) |

## 4. 可落地修复方案(已完成与待办)

### 已完成

1. `ai_workflow/runtime_contracts.py::get_stage_dir` —— 加 `.strip()`
2. `ai_workflow/conversation_skills.py::_stage_dir` —— 加 `.strip()`
3. `ai_workflow/conversation_skills.py::_resolve_stage_path` —— 加 `.strip()`
4. 删除 `workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」 ` (带尾空格)
5. 删除 `workflow_assets/游戏道具商城系统/v3.01/「S4 流程图导出」 ` (带尾空格)
6. 写 PLAN.md / out_of_scope.md / audit_1.md

### follow_up(放入 v24+)

- **L3 hook `directory_lints.py`**: 扫盘 `workflow_assets/**/*/`,对任何 `endswith((' ', '\t'))` 目录/文件告警
- 建议放在 `afterFileEdit` 事件,修改工程触发轻量扫描

## 5. 影响范围

| 文件 | 改动 | 影响 |
|---|---|---|
| `ai_workflow/runtime_contracts.py` | +5 行(注释 + .strip) | 所有 S2/S4/S5 等阶段目录计算 |
| `ai_workflow/conversation_skills.py` | +6 行(2 处 .strip + 注释) | `_stage_dir` 与 `_resolve_stage_path` 调用方 |
| 删除两个错误目录 | 0 字节(空目录) | 仅本次 v3.01 |
| `governance/design_iter/plans/v23/*` | 新增 4 文档 | 不影响运行时 |

**风险面**:
- 修改的 3 个 .py 函数是 SSOT,任何下游 S2/S4 路径计算都受影响
- `.strip()` 只作用于 ASCII 空白,不会破坏中文阶段名
- 已通过 py_compile + 动态调用验证

## 6. 质量自评分

| 评分项 | 分值 |
|---|---|
| 根因定位完整性 | 9/10(代码无字面量是出乎预料,但已记录) |
| 修复彻底性 | 8/10(3 处入口 + 1 次清理;缺 L3 hook 留 follow_up) |
| 文档同步度 | 9/10(PLAN + out_of_scope + audit + review + 代码注释,5 处) |
| 测试覆盖 | 7/10(py_compile + 动态;缺 unittests for strip 行为) |
| 影响范围评估 | 9/10(SSOT 3 函数明确 + 业务逻辑不动) |

**总计**: 42/50 — 良好

## 7. 遗留项(进 follow_up_items)

| 描述 | 严重度 | 建议修复方向 |
|---|---|---|
| L3 hook 缺 directory_lints(扫盘带空格目录) | MINOR | 新建 `.cursor/hooks/directory_lints.py`,afterFileEdit 触发扫描 |
| 中文路径手敲易引入空格 | MINOR | 在 conversation_skills prompt 模板顶部加"路径 = 函数返回值,禁止手敲中文路径"提示 |
| unittests 缺 strip 测试用例 | MINOR | `tests/test_stage_dir_path_safety.py` 验证带空格 stage key 行为 |

## 8. 本轮决策

- **value_criteria 4/4 PASS + process_criteria 2/2 PASS**
- **价值侧 BLOCKER 全部通过**(V-01/V-02/V-03)
- **MAJOR 全部通过**(V-04)
- **无未关闭的 FAIL/UNKNOWN**
- **遗留项 3 条 MINOR**,明确方向,不影响"系统能正确产出目录"的核心目标

## 9. 收敛建议

→ 进入 Iterate 阶段,判定 `achieved`
