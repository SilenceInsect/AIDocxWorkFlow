# CONVERGED — Round 17 xlsx 同 OBJ 合并与空行移除

**日期**：2026-07-19  
**Goal ID**：`66727af9-fffd-4be3-965b-d63f78269530`  
**状态**：`achieved`  
**loop_round**：1。

## 1. 收敛状态

Round 17 单轮收敛。5 项 Value Criteria 与 3 项 Process Criteria 全部 PASS，BLOCKER residual 为 0，value ratio 为 `5 / (5 + 3) = 0.625`。

## 2. 完成任务

| ID | 任务 | 状态 | 证据 |
|---|---|---|---|
| T-001 | 读取 Round 16 audit/review/CONVERGED、formatter、主调与源 JSON | done | Round 16 spacer、排序、索引、只读边界均已核实 |
| T-002 | 落 Round 17 Plan 与合并策略 | done | `goal_round17_merge_cells.md` |
| T-003 | formatter 移除 spacer、记录 OBJ 块、合并三列 | done | 48 merge regions |
| T-004 | 增 self-test cases 7-9 并验证 | done | formatter 与 export-driver self-test PASS |
| T-005 | 备份 Round 16 并重导 workbook | done | `.round16.bak.xlsx` + 新 workbook |
| T-006 | OpenPyXL 物理验收 | done | 88 行、0 空行、48 merge、5 色、16 OBJ |
| T-007 | 生成并读取视觉 PNG | done | `test_cases_public.round17.visual.png` |
| T-008 | 落 audit/review/snapshot/CONVERGED | done | 四项治理资产齐全 |

## 3. V/P 终态

### Value Criteria

| ID | 判定 | 证据 |
|---|---|---|
| V-001 | PASS | 48 merge regions；B/C/D 各 16，对应所属模块/用例描述/关联需求 |
| V-002 | PASS | 主表 88 行 × 11 列，0 个整行空白 |
| V-003 | PASS | OBJ ID 升序、同 OBJ case_id 升序、5 色背景保持 |
| V-004 | PASS | 索引 17 行 × 5 列；16 OBJ；TC=87，Ready=87，FP=49 |
| V-005 | PASS | Draft-Rejected附录只有 header，0 cases |

### Process Criteria

| ID | 判定 | 证据 |
|---|---|---|
| P-001 | PASS | formatter case 7-9、formatter self-test、主调 self-test、py_compile、lint 全通过 |
| P-002 | PASS | `test_cases.json` 为 338192 bytes；SHA-256 `7d6359f...d4316ca` |
| P-003 | PASS | `test_cases_public.round16.bak.xlsx` 物理复核为 103 行、0 merge、15 spacer |

## 4. 核心产物

| 产物 | 路径 |
|---|---|
| Plan | `governance/design_iter/current/goal_round17_merge_cells.md` |
| audit | `governance/design_iter/plans/v17/audit_round17.md` |
| review | `governance/design_iter/plans/v17/review_round17.md` |
| CONVERGED | `governance/design_iter/plans/v17/CONVERGED_round17.md` |
| 新 workbook | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` |
| Round 16 备份 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round16.bak.xlsx` |
| 视觉 PNG | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round17.visual.png` |
| snapshot | `.goal-log-db/active/66727af9-fffd-4be3-965b-d63f78269530/snapshot.json` |

## 5. 反向挑战结论

纵向合并满足用户的块状视觉审查，但无法让三列在每一行都保持自包含：

- 按合并列逐行 filter 的语义不完整。
- 在合并区域直接 sort 不可靠。
- 复制块内非首行会缺三列共享值。

Round 17 选择视觉版优先，JSON 与索引 Sheet 保留结构化入口。若后续出现逐行操作需求，新增未合并 machine-readable workbook，不覆盖当前视觉版。

## 6. 跨 Goal 衔接

### 上游

Round 16 Goal `6d3edb03-352d-4a3f-921c-b880db0625f5` 建立：

- 87 条 Ready TC 的 normalize/merge/L1/L2/xlsx 链路。
- OBJ 分组排序与 5 色背景。
- 用例描述索引。
- Round 16 使用 spacer，无 merge。

### Round 17 增量

- 清理 FU-B1 剩余视觉缺陷：15 spacer → 0；0 merge → 48。
- 新增 `关联需求=obj_id` 可见列。
- 保留上游 JSON、校验器、索引和附录契约。

### 历史证据更正

Round 16 audit 的 FP 合计 50 是算术误报。Round 17 物理 workbook 与源 meta 均为 49。本轮没有修改源数据，只在 audit/review 中明确纠正。

## 7. 遗留项

1. FU-A2 SSOT 拆约束对象继续留在 v3.02 治理。
2. FU-A4 v3.01 step/expected 错位继续留在 v3.02 prompt 治理。
3. `_sync_list_fields_after_merge` 防御性兜底清理未进入本轮。
4. `source_case_ids` 主表渲染未进入本轮。
5. 若需要逐行机器操作，考虑独立未合并 workbook。

## 8. 影响范围与约束遵守

- 修改实现：`test_case_formatter.py`、`run_round15_merge_export.py`。
- 新增治理与过程资产：Plan、audit、review、CONVERGED、snapshot、备份、PNG。
- 未修改：`test_cases.json`、L1S6Validator、S7 review_report、`.mdc`、SKILL、AGENTS、hooks。
- 未引入依赖：matplotlib 不可用后使用已安装 Pillow。
- 未 commit。

## 9. 完成声明

Round 17 的 xlsx 同 OBJ 纵向合并、空行移除、排序与背景回归、索引与附录回归、源 JSON 只读、备份保存、视觉验证和治理落档均已完成。Goal 状态为 `achieved`。
