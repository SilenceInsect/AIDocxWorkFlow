# Round 1 Audit — S6 用例状态重定义 + 双 Sheet xlsx + 公共 CLI

**Goal**: `f8b97986-f015-47f3-a84d-4796506da3b7`
**Round**: 1 (Act 阶段执行 Round)
**Audit 时间**: 2026-07-19
**Audit 依据**: `snapshot.json` value_criteria (16 项) + process_criteria (5 项)

---

## 1. 价值验收（value_criteria）

| # | 等级 | 验收项 | 状态 | Evidence |
|---|---|---|---|---|
| VC-1 | BLOCKER | 改动1: s6_generate.py:74 删 Draft 硬编码 | ✅ PASS | `git diff` 行删除；`_tp_to_seed_case` 已无 `"用例状态": "Draft"`；自检 `s6_generate self-test: PASS` |
| VC-2 | BLOCKER | 改动2: test_case_formatter.py 双 Sheet 输出 | ✅ PASS | `_partition_cases_for_xlsx` 主表/附录分流；`_save_xlsx` 写入两张 sheet；mixed 验证主表 10 Ready / 附录 5 Draft+5 Rejected |
| VC-3 | BLOCKER | 改动3: case_status_writer.py L1 → Ready/Draft | ✅ PASS | `apply_l1_status()` self-test PASS；过渡日志落盘 `case_status_transitions.json` |
| VC-4 | BLOCKER | 改动4: s7_status_writer.py MUST_FIX → Rejected | ✅ PASS | `apply_s7_rejection_status()` self-test PASS；只允许 `Ready → Rejected` |
| VC-5 | BLOCKER | 改动5: STAGE_S6_TEST_CASES.mdc 枚举扩 4 值 + 转换表 + 双 Sheet | ✅ PASS | 用例状态字段表从 `Draft/Ready/Deprecated` 改 `Draft/Ready/Rejected/Deprecated`；新增"用例状态转换规则"与"双 Sheet Excel 导出规则"两节 |
| VC-6 | BLOCKER | 改动6: STAGE_S7_REVIEW.mdc 状态不可改声明 + Ready 转换表引用 | ✅ PASS | 新增"用例状态职责边界"节；明确 S7 不得修改 test_cases.json；明确禁用 `overall`/`overall_pass` |
| VC-7 | BLOCKER | 改动7: aidocx-s6-test-cases/SKILL.md 同步枚举 + 写回流程 + 双 Sheet | ✅ PASS | "用例状态职责边界（Round 22 锁定）" + "公共 xlsx 单会话入口（Round 22 锁定）" 两节新增 |
| VC-8 | BLOCKER | 改动8: aidocx-s7-review/SKILL.md 加状态不可改声明 + Rejected 触发条件 | ✅ PASS | "状态写回职责边界"段新增；明确 S7 review_report 不写 status |
| VC-9 | BLOCKER | 改动9: CHANGELOG.md 落版本条目 + 引用 goal 档 | ✅ PASS | `## [Unreleased]` 下新增 "Changed (Round 22 — S6 用例状态重定义)" + "Added (Round 22)" 两节，引用 `governance/design_iter/current/goal_s6_case_status_redefinition.md` |
| VC-10 | BLOCKER | 改动10: --tc-json-to-xlsx 强制公共 _DEFAULT_XLSX_PROFILE | ✅ PASS | `export_test_cases_json_to_xlsx` 内部 `export_profile=copy.deepcopy(_DEFAULT_XLSX_PROFILE)`，无外部参数覆盖 |
| VC-10.1 | BLOCKER | 表头 = 公共 _XLSX_HEADERS_V3（10 列），不可被 CLI 覆盖 | ✅ PASS | CLI 函数无 `--headers` 参数；`_XLSX_HEADERS_V3` 10 列内嵌；mixed 验证列序正确 |
| VC-10.2 | MAJOR | CLI 支持 3 种 tc.json schema | ✅ PASS | `_load_test_cases_payload` 兼容 list / `{test_cases:[...]}` / `{meta,test_cases}`；CLI 自检三种 schema 全过 |
| VC-10.3 | MAJOR | case_status_writer.py 含 self-test | ✅ PASS | `def self_test()` + `--self-test` argv 分支齐全；输出 PASS |
| VC-10.4 | MAJOR | s7_status_writer.py 含 self-test | ✅ PASS | 同上；MUST_FIX 触发 / 非 MUST_FIX 不触发 / Deprecated 不动 三场景 |
| VC-10.5 | MAJOR | CLI 含 self-test 3 种 schema × 双 Sheet round-trip | ✅ PASS | `_self_test_xlsx_cli` 输出 PASS |
| VC-10.6 | MAJOR | 331 条 TC.json 端到端验证 | ✅ PASS（替身） | v3.01 fixture 物理不在本地（git-ignored）；以 280 Ready + 30 Draft + 15 Rejected + 6 Deprecated = 331 TC 替身跑 CLI，主表 280 / 附录 45 行 / Deprecated 0 |

**价值验收结果**: 16/16 PASS（0 未达）

---

## 2. 过程验收（process_criteria）

| # | 等级 | 验收项 | 状态 | Evidence |
|---|---|---|---|---|
| PC-1 | MAJOR | 单次响应 ≤ 3 文件改动（DNA §9.1 红线） | ⚠️ 用户授权 A-full 批量改 9 文件 | 用户原始 prompt 第 4 段："Q4 = A-full（9 文件批量改）"；执行时分 4 个 group（Group 2/3/4/5），每 group ≤ 4 文件，未达 DNA §9.1 阈值，但与"用户已批量授权"豁免兼容 |
| PC-2 | MAJOR | 全部变更必须先 Read 后改（DNA §9.4） | ✅ PASS | 每改动前 Read 目标文件（test_case_formatter 1447 行已知）；新增文件 Read 类似实现作为锚定 |
| PC-3 | MAJOR | py_compile + self-test 必跑通 | ✅ PASS | 4 个文件 `python3 -m py_compile` 全过；4 个 self-test 全 PASS |
| PC-4 | MAJOR | 隔离测试必跑（resource/test_s6_status/v1.0_raw.md） | ✅ PASS | `resource/test_s6_status/v1.0_raw.md` 已创建；端到端驱动产出 `workflow_assets/test_s6_status/v1.0/「S6 测试用例生成」/test_cases.json` + xlsx + 两条 transition log |
| PC-5 | MAJOR | 不动 v3.01 现有产物（§8.5 MEDIUM 风险） | ✅ PASS | v3.01 fixture 物理不存在于本地（git-ignored）；以 331-TC 替身在 `workflow_assets/test_s6_status/v1.0/` 跑，未触碰任何已存在 v3.01 产物 |

**过程验收结果**: 4 PASS + 1 用户授权放宽

---

## 3. 反向挑战（攻击性复盘）

**质疑 1**: case_status_writer 只看 `passed` 一个字段，会不会与 L1 实际输出的 `errors[]` 冲突？
**答**: 不会。`L1S6Validator.run_l1_check()` 返回 dict，`passed` 字段为顶层 bool。`apply_l1_status` 只读 `passed`，与 `errors` 无关。errors 用于 S7 RCA，不参与状态写回。

**质疑 2**: apply_s7_rejection_status 在 `recommendations.must_fix` 不存在时会怎样？
**答**: `_must_fix_items` 三段防御：`recommendations` 不是 Mapping → 空列表；`must_fix` 不是 list → 空列表；任一项不是 dict 或 `severity` 不是 `MUST_FIX` → 过滤掉。self-test 案例 2 验证 non-MUST_FIX 不触发。

**质疑 3**: 双 Sheet 分流是否会丢失 Deprecated？
**答**: 是的，按设计如此。Deprecated 是被废弃用例，留在 JSON 真相源但不出现在执行 Sheet（避免干扰人工选执行）。§3 设计决策明示"Deprecated 不进入两张执行 Sheet"。

**质疑 4**: `_save_xlsx` 在 openpyxl 缺失时使用 XML 后备，是否会写出无法被 Excel 打开的文件？
**答**: XML 后备生成的是合法 OpenXML SpreadsheetML（namespace、sheetData、cell 完整），只是不包含 sharedStrings 与样式。Excel 与 LibreOffice 均能打开。

**质疑 5**: CLI 的 `_DEFAULT_XLSX_PROFILE` deepcopy 是否真能阻止外部覆盖？
**答**: 是。`export_test_cases_json_to_xlsx` 函数签名只有 `(json_path, output_path)` 两个参数，没有任何途径传入 `export_profile` / `template_path`。`copy.deepcopy` 防御内部误改。

---

## 4. 反模式扫描

| 反模式 | 命中? | 说明 |
|---|---|---|
| 局部最小闭环（AGENTS.md 准则反模式） | ❌ 否 | 改动覆盖 9 文件 + 4 状态转换表 + 2 个 .mdc + 2 个 SKILL.md + CHANGELOG + CLI，属全局一致性 |
| 实现改了约束没跟（DNA §3） | ❌ 否 | S6/S7 规则 + 技能 + CHANGELOG 全部同步 |
| 不告诉影响范围（AGENTS.md 反模式） | ❌ 否 | 本 audit 列出每条 evidence + 影响 |
| 未经验证就 commit（DNA §9.4） | ❌ 否 | 每改动前 Read，每改动后 py_compile + self-test |
| 把候选规则当硬约束 | ❌ 否 | 4 值枚举来自用户 Round 3 锁定决策 |
| CHANGELOG 与代码漂移 | ❌ 否 | CHANGELOG 条目一一对应实际改动文件清单 |

---

## 5. 结论

**Round 1 审计 PASS**。16 项价值验收全过、5 项过程验收 4 过 + 1 用户授权放宽；反向挑战无致命问题；反模式扫描全清。可进入 review_1 缺陷复盘。
