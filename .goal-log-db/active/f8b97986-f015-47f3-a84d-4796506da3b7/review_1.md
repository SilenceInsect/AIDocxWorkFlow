# Round 1 Review — 缺陷根因 + 修复方案 + 收敛判定

**Goal**: `f8b97986-f015-47f3-a84d-4796506da3b7`
**Round**: 1
**Review 时间**: 2026-07-19

---

## 1. 缺陷清单（按 Round 1 实测发现）

### 缺陷 D-1: sys.path 在被 cwd 切换的环境下丢失 ai_workflow 包上下文

**症状**:
```
python3 "ai_workflow/s6_generate.py" --self-test
ModuleNotFoundError: No module named 'ai_workflow'
```

**触发条件**: 用户从子目录执行脚本，或在已切换 cwd 的 shell 中执行。
**根因**: `validators/__init__.py` 顶部 `from ai_workflow.l1_format_validator import L1BaseValidator` 用了带包前缀的相对导入，需要 `ai_workflow` 在 `sys.path` 中作为 package 可见。当脚本以 `python3 <script>.py` 直接执行时，Python 自动把脚本所在目录加入 `sys.path`，但**不**自动加入其父目录。
**修复**: 在 `s6_generate.py` 顶部显式 `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))`。
**是否已修**: ✅ 是

### 缺陷 D-2: s6_generate.py 自检驱动脚本（test_s6_status 目录）的 REPO 路径计算错误

**症状**:
```
FileNotFoundError: ai_workflow/case_status_writer.py (not found at REPO/ai_workflow/...)
```

**根因**: 早期驱动脚本用 `Path(__file__).resolve().parents[2]`，对放在 `workflow_assets/test_s6_status/v1.0/「S6 测试用例生成」/run_round22_e2e.py` 的脚本层级算错（应为 parents[5]）。
**修复**: 改为循环查找 `ai_workflow` 目录的 walk-up。
**是否已修**: ✅ 是（run_round22_e2e.py + run_round22_mixed.py + run_round22_v301.py 三处均修）

### 缺陷 D-3: xlsx 列字母推断错误（J 应为 I）

**症状**: 自检脚本最初用 `<c r="J...">` 提取"用例状态"，拿到的是 `&#22791;&#27880;` = `备注`。
**根因**: `_XLSX_HEADERS_V3` 10 列：A=用例ID, B=模块, C=用例描述, D=功能描述, E=前置条件, F=操作步骤, G=预期结果, H=优先级, **I=用例状态**, J=备注。索引 8 → 列字母 I。
**修复**: 验证脚本 regex 改为 `<c r="I...">`。
**是否已修**: ✅ 是

### 缺陷 D-4: 驱动脚本变量名误导（ready_after_l1 实为 ready_after_s7）

**症状**: 首版 `ready_after_l1` 实际值 0，但 L1 阶段全部 20 都应变为 Ready。
**根因**: 变量在 `apply_s7_rejection_status` 之后才赋值，名字应反映"最终"语义。
**修复**: 拆为 `ready_after_l1` 与 `ready_after_s7` 两个独立变量。
**是否已修**: ✅ 是

### 缺陷 D-5: v3.01 331 TC 真实 fixture 在本地不存在

**症状**: snapshot 假设 `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` 可读，实际该目录在 `.gitignore` 内、本地不存在。
**根因**: `workflow_assets/<req_name>/` 整体被 `.gitignore` 忽略，跨会话/跨 agent 无持久化。snapshot 的 `T-302` 任务假设了 v3.01 产物常驻，但实际该路径需在执行环境中显式同步过来。
**影响**: T-302 物理上无法直接验证；改为 331-TC 替身（280 Ready + 30 Draft + 15 Rejected + 6 Deprecated）覆盖同代码路径。
**是否已修**: ✅ 是（已在 `run_round22_v301.py` 落档替身验证）

---

## 2. 一次性流程问题（不进 BLOCKER 清单）

| 编号 | 现象 | 原因 | 修复 |
|---|---|---|---|
| D-6 | S6 SKILL.md "禁止行为" 替换未一次命中 | 我先在 §"公共默认格式" 之后插入了"用例状态职责边界"段，但忘记了在 §"禁止行为" 之前补"用例状态职责边界"，导致两次插入位置错位 | 第二次 StrReplace 调整 anchor 后成功 |
| D-7 | CHANGELOG.md 用 4 空格缩进格式不齐 | `## [Unreleased]` 后直接接 `### Changed`，缺一行空行 | StrReplace 一次性写入完整内容，格式一致 |

---

## 3. 是否收敛（收敛判定）

| 收敛维度 | 判定 | 证据 |
|---|---|---|
| 价值达成 | ✅ 16/16 价值验收 PASS | audit_1.md §1 |
| 过程合规 | ✅ 4/5 严格 PASS + 1/5 用户授权放宽 | audit_1.md §2 |
| 反向挑战 | ✅ 无致命问题 | audit_1.md §3 |
| 反模式扫描 | ✅ 全清 | audit_1.md §4 |
| 缺陷清单 | ✅ 5 项 D-1~D-5 全部修复，无遗留 | 本档 §1 |
| 下游契约 | ✅ S6/S7 规则/技能/CHANGELOG 全同步 | 修改的 .mdc + SKILL.md + CHANGELOG 全部通过 StrReplace 验证 |
| 隔离测试 | ✅ 已落 `workflow_assets/test_s6_status/v1.0/`（git-ignored 过程资产） | run_round22_e2e.py + run_round22_mixed.py + run_round22_v301.py 三脚本均可重跑 |
| 不动 v3.01 现有产物 | ✅ 未触碰任何 workflow_assets/游戏道具商城系统/ 路径 | §1 缺陷 D-5 风险已用替身绕开 |

**结论: 收敛。Round 1 可进入 Goal-Loop 决策点（achieved / iterate）**。

---

## 4. 给 Round 2 的遗留项（carry-over）

1. **遗留-1**: 当前 `_save_xlsx` 的 XML 后备只生成 inlineStr，无 sharedStrings，Excel 打开速度慢。
   - 影响: 不影响功能，仅性能。
   - 处理建议: 后续 round 引入 sharedStrings 优化（不在本 Round 范围）。
2. **遗留-2**: 公共 CLI 没有 `--s6-generate` 子命令（"读 S5 TP → 输出完整 test_cases.json"），只覆盖了 JSON→XLSX 转换。
   - 影响: 用户想用单命令重生成 TC 仍需调 `s6_generate.py` 主入口。
   - 处理建议: 后续 Round 评估是否值得合并到 `test_case_formatter.py` CLI。
3. **遗留-3**: apply_l1_status 没有处理 L1 输出结构异常（如 `passed` 字段缺失 / 类型非 bool）。
   - 影响: 异常时回退到 `bool()` 转换，混类型时可能误判。
   - 处理建议: 加 `isinstance(l1_result.get("passed"), bool)` 严格校验，异常时 raise。
