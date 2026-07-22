# case_id_and_field_normalizer.self_test_report

## 1. 测试环境

| 项 | 值 |
|---|---|
| 生成时间（UTC） | 2026-07-19T18:25:23.074716+00:00 |
| Python 版本 | 3.14.5 (macOS-26.5.2-arm64-arm-64bit-Mach-O) |
| 文件路径 | `/Users/gleon/Documents/TestDev/AIDocxWorkFlow/ai_workflow/case_id_and_field_normalizer.py` |
| 文件大小 | 62676 bytes |
| 文件 mtime (UTC) | 2026-07-19T18:24:55.439323+00:00 |
| 文件 sha256 | `5cd4a7dc436c45b49c29fb3a00517492c77e8664c7bfddc0aea5cf13e1d2b727` |
| 测试用例常量 | `_SELF_TEST_CASES` (18 项) |

## 2. 测试项明细

| # | case_id | description | verdict | evidence |
|---|---|---|---|---|
| 1 | `TC-01` | case_id prefix injection (modular + counter reset) | PASS | ids=['BIZ-TC-001', 'UI-TC-007', 'UI-TC-015'], counters={'UI': 0, 'BIZ': 0} |
| 2 | `TC-02` | bilingual alias mirroring preserves canonical Chinese | PASS | mirrored=['优先级', '前置条件', '操作步骤', '预期结果'] |
| 3 | `TC-03` | priority alias compatibility (L1S6Validator reads Chinese/English) | PASS | req_errors=0, id_errors=0 |
| 4 | `TC-04` | L1 pass → Ready writeback | PASS | 用例状态=Ready, l1.passed=True |
| 5 | `TC-05` | L1 fail (bad id) → Draft | PASS | 用例状态=Draft, l1.passed=False |
| 6 | `TC-06` | L1 pass + L2 fail → Draft | PASS | l1.passed=True, l2.passed=False |
| 7 | `TC-07` | Round 16 fix — list→list mirror (3-element list) | PASS | mirrored=['前置条件', '操作步骤', '预期结果'] |
| 8 | `TC-08` | Round 16 fix — string→string mirror (scalar string) | PASS | mirrored=['优先级', '前置条件'] |
| 9 | `TC-09` | Round 16 fix — mixed canonical fields (idempotency) | PASS | mirrored=['预期结果'] |
| 10 | `TC-10` | T-004 / Round 15 — OBJ-level P0 risk matrix | PASS | stats.objs_promoted=3, cases_promoted=3 |
| 11 | `TC-11` | T-004 — idempotency on re-run | PASS | first.cases_promoted=1, second.cases_promoted=0, lineage_len=1 |
| 12 | `TC-12` | T-003 / V-001 — renumber_cases_per_module (apply=True) | PASS | UI=['UI-TC-001', 'UI-TC-002'], BIZ=['BIZ-TC-001', 'BIZ-TC-002', 'BIZ-TC-003'], rewrites=5 |
| 13 | `TC-13` | T-003 — idempotency on already-rewritten payload | PASS | already_canonical=True, rewrites=0 |
| 14 | `TC-14` | T-003 — dry-run path (apply=False) | PASS | by_module.UI.count=2, rewrites=0 |
| 15 | `TC-15` | T-003 — fallback from case_id prefix when no module field | PASS | by_module.LOG.count=2, skipped_no_prefix=0 |
| 16 | `TC-16` | v29 T-101 — evaluate_status accepts list[dict] tps | PASS | l1.passed=True, tps_entries=1 |
| 17 | `TC-17` | v29 T-101 — evaluate_status rejects list[str] tps with TypeError | PASS | TypeError raised: msg~="evaluate_status: `tps` must be a list of dicts (each with at least a 'tp_id' key" |
| 18 | `TC-18` | v29 T-101 — passing tps=None still works | PASS | l1.passed=True |

**合计**: total=18 passed=18 failed=0

## 3. 反向挑战（什么情况会推翻 PASS）

以下反例可证伪本轮 PASS：

- **反例 1**：若 worker 修 `evaluate_status` 修复但漏掉 `extract_refs` 路径 → TC-16/TC-17 部分 FAIL（list[dict] 与 list[str] 类型校验漏检）。
- **反例 2**：若 self-test 实际只跑 `list[dict]` → `list[str]` 路径未覆盖 → TC-17 FAIL（防御性 TypeError 校验漏跑）。
- **反例 3**：若 `--self-test` argv 兼容破坏（删了 `SystemExit(self_test())` 或忘了 verbose=False 兼容分支）→ 旧 CI 调用失败（exit code 异常 + 无 'PASS' 行）。

## 4. 结论

- 本轮 18 项 self-test 全部 PASS（18/18）
- 详细产物已落档 `ai_workflow/case_id_and_field_normalizer.self_test_report.md`
- 数据契约 100% 可复核（不再只信 worker 报告 — V-101R 价值叙事兑现）
