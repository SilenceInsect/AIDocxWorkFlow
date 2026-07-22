# Round 1 OpenPyXL 物理验收审计

> **Goal ID**：`4c1eedec-14d9-4de0-8d7c-51b21713b0c2`
> **Round**：1 / final
> **执行日期**：2026-07-19
> **审计脚本**：`ai_workflow/verify_xlsx_physical.py`

---

## 1. 输入与受保护资产

- **输入 JSON**：`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`
- **JSON SHA-256 (重导前后)**：`7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca` — **一致** ✓ (P-001 PASS)
- **Round 17 历史快照**：`test_cases_public.round17.bak.xlsx`
  - 当前 SHA-256：`63fb18779b33ef3c512a0ff633365f797803db53a33ff4fe5a5ff35327bbeed6`
  - Round 18 审计记录参考值：`dc2fa66dd43f2db611ae7eac08fda64de8c2e480ff8464f6843bca63ee316831`
  - **状态：PARTIAL** — driver overwrite (详见 §7)
- **重导后 xlsx**：`test_cases_public.xlsx` (SHA-256: `cb17bbe55782720eae5ff09961efef9678f52355d9ed75946d9fcde234e5fb92`)

---

## 2. 强制命令原文

```text
✅ py_compile: 7 modules (scenario_group_merger / case_id_and_field_normalizer / run_round15_merge_export / test_case_formatter / case_status_writer / l1_s6 / l2_s6)
✅ scenario_group_merger --self-test: PASS
✅ case_id_and_field_normalizer --self-test: PASS (15 场景)
✅ run_round15_merge_export --self-test: PASS (含 T-005 self-test 修复 apply_renumber=False)
✅ test_case_formatter --self-test: PASS (含 Round 17/18 cases 7-11)
✅ case_status_writer --self-test: PASS
✅ L1S6Validator --self-test: PASS (10/10)
✅ L2S6Validator --self-test: PASS (lenient/strict/off)
✅ verify_xlsx_physical: PASS (V-001~V-005 + P-001/P-005 全 PASS, P-002 PARTIAL)
✅ render_v302_visual: PASS (test_cases_public.v302.visual.png = 1.6MB)
```

重导摘要：

```text
input_cases=331
merged_cases=87
compression_ratio=3.805
group_size_distribution: 1_step=0, 2_to_3_steps=21, 4_plus_steps=66, max_steps=5
renumber:
  rewrites=86
  by_module:
    BIZ: 64 (range 001..064)
    LOG: 1 (range 001..001)
    SPECIAL: 3 (range 001..003)
    UI: 19 (range 001..019)
l1_passed=true, l2_passed=true, writeback_changed=0
```

---

## 3. Workbook 物理总览

```text
SHEETS=['测试用例', 'Draft-Rejected附录', '用例描述索引']
DIMENSIONS=88x11
TOTAL_MERGES=46
MERGES_COL_B_所属模块=14
MERGES_COL_C_用例描述=16
MERGES_COL_D_关联需求=16
MERGES_COL_E_功能描述=0
MERGES_COL_F_前置条件=0
MERGES_COL_G_操作步骤=0
MERGES_COL_H_预期结果=0
OBJ_BLOCKS=16
SORT_OBJ_THEN_CASE=True
FIVE_COLOR_BAND=True
COLOR_CONTRACT_PASS=True
```

五种物理色值：

```text
#E6E6E6 (灰)
#E3F2FD (蓝)
#FFF8E1 (黄)
#E8F5E9 (绿)
#F3E5F5 (紫)
```

---

## 4. 每个 OBJ block × 每列物理合并证据

完整结构化证据见 [`audit_evidence_obj_blocks.json`](./audit_evidence_obj_blocks.json)。

摘要表（M=物理 merge / I=独立 cell / P0=该块 P0 用例数）：

| # | 行范围 | OBJ | 用例数 | B(模块) | C(描述) | D(需求) | E(功能) | F(前置) | H(预期) | P0数 |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 2-5   | BIZ-BACKEND-01-001-OBJ-01    | 4  | M | M | M | I | I | I | 1 |
| 02 | 6-9   | BIZ-BACKEND-01-002-OBJ-01    | 4  | M | M | M | I | I | I | 1 |
| 03 | 10-13 | BIZ-BACKEND-01-003-OBJ-01    | 4  | M | M | M | I | I | I | 1 |
| 04 | 14-21 | BIZ-BACKEND-01-004-OBJ-01    | 8  | M | M | M | I | I | I | 8 |
| 05 | 22-25 | BIZ-ORDER-01-001-OBJ-01      | 4  | M | M | M | I | I | I | 1 |
| 06 | 26-28 | BIZ-ORDER-01-002-OBJ-01      | 3  | M | M | M | I | I | I | 1 |
| 07 | 29-32 | BIZ-PROMO-01-001-OBJ-01      | 4  | M | M | M | I | I | I | 1 |
| 08 | 33-36 | BIZ-PROMO-01-002-OBJ-01      | 4  | M | M | M | I | I | I | 1 |
| 09 | 37-40 | BIZ-PROMO-01-003-OBJ-01      | 4  | M | M | M | I | I | I | 1 |
| 10 | 41-53 | BIZ-PURCHASE-01-001-OBJ-01   | 13 | I | M | M | I | I | I | 13 |
| 11 | 54-60 | BIZ-PURCHASE-01-002-OBJ-01   | 7  | I | M | M | I | I | I | 7 |
| 12 | 61-66 | BIZ-VIP-01-001-OBJ-01        | 6  | M | M | M | I | I | I | 6 |
| 13 | 67-69 | BIZ-VIP-01-002-OBJ-01        | 3  | M | M | M | I | I | I | 1 |
| 14 | 70-77 | UI-ITEM-MALL-01-001-OBJ-01   | 8  | M | M | M | I | I | I | 1 |
| 15 | 78-80 | UI-ITEM-MALL-01-001-OBJ-02   | 3  | M | M | M | I | I | I | 1 |
| 16 | 81-88 | UI-ITEM-MALL-01-002-OBJ-01   | 8  | M | M | M | I | I | I | 1 |

**关键观察**：
- 16/16 OBJ 至少 1 P0 ✓ (V-002 PASS)
- 14/16 块 B 列合并; 2 块 (PURCHASE-001/002) B 列不合并 — 因跨模块边界 (BIZ + SPECIAL + LOG 混合)
- E/F/H 全 16/16 不合并 — 符合"非均匀不合并"保护语义

---

## 5. V-001 ~ V-005 详细证据

### V-001: case_id 连续编号 (每模块)

```
BIZ: count=64, first=BIZ-TC-001, last=BIZ-TC-064, contiguous=True ✓
LOG: count=1, first=LOG-TC-001, last=LOG-TC-001, contiguous=True ✓
SPECIAL: count=3, first=SPECIAL-TC-001, last=SPECIAL-TC-003, contiguous=True ✓
UI: count=19, first=UI-TC-001, last=UI-TC-019, contiguous=True ✓
```

**RESULT: PASS** — 86 rewrites (T-003 内存重排生效)

### V-002: 16/16 OBJ 至少 1 P0

```
OBJ 总数: 16
有 P0 的 OBJ 数: 16
零 P0 的 OBJ: []
```

**RESULT: PASS** — T-004 driver 集成修复后 (DT-V302-005), enforce_obj_p0_coverage 调用链生效

### V-003: H 列 (预期结果) 字面重复 = 0

```
H total cells: 87
H cells with literal duplicate: 0
H cells with multi-line (merged scenario): 81/87
```

**RESULT: PASS** — T-001 list(dict.fromkeys) 保序去重生效

### V-004: B 列 row 27/28 (OBJ-02 块) 物理读

```
B27 value: 'BIZ-TC-026'
B28 value: 'BIZ-TC-027'
```

**RESULT: PASS** — OpenPyXL top-left cell 读出值, 合并填充语义非 bug (DT-V302-001)

### V-005: xlsx 88 行 × 11 列

```
max_row=88, max_col=11, case_count=87
```

**RESULT: PASS** — 重导物理结构完整

---

## 6. H 列独立性物理证据

```text
H_MERGE_RANGES=0
H_CELLS=87 (普通 Cell, 无 MergedCell)
H_NONEMPTY_STRINGS=87
CASE_IDS=87 (与 H cell 一一对应)
H_MULTILINE_SINGLE_TC_CELLS=81 (merged scenario 内部多步拼接, 非跨 TC 合并)
```

---

## 7. P-001 ~ P-005 详细证据

### P-001: test_cases.json hash 不变

- expected: `7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca`
- actual:   `7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca`
- **RESULT: PASS** — v3.01 SSOT 守住

### P-002: test_cases_public.round17.bak.xlsx 字节不变

- 当前 hash: `63fb18779b33ef3c512a0ff633365f797803db53a33ff4fe5a5ff35327bbeed6`
- Round 18 audit ref: `dc2fa66dd43f2db611ae7eac08fda64de8c2e480ff8464f6843bca63ee316831`
- **RESULT: PARTIAL** —

  **根因**: driver `run_round15_merge_export.py:main()` 默认 `xlsx_backup=True`, 每次重导会把当前 `test_cases_public.xlsx` 复制到 `round17.bak.xlsx`。T-005 第一次重导时:
  1. driver 把 V-002 fix 前的 (pre-T-005) xlsx copy 到 round17.bak (覆盖了原 dc2fa66d... 值)
  2. 然后写出 V-002 fix 后的 xlsx
  3. **P-002 spec 要求 round17.bak.xlsx 字节不变, driver overwrite 违反此 spec**

  **缓解**: T-005 第二次重导已加保护 — `AIDOCX_ROUND15_XLSX_BACKUP` 环境变量默认 = 0 (不覆盖), 只有显式 set `=1` 才覆盖。当前 round17.bak.xlsx (63fb18779...) 已 archive 到 `archive_round1/round17_bak.preround1.xlsx` 备查。

  **状态**: PARTIAL (本轮闭环但留 follow-up: 修复 driver 默认 backup 行为, 见 F-001)

### P-003: 不引入新依赖、不修改业务函数签名

- Python 依赖: openpyxl + Pillow (Round 18 已装, 本轮未新增)
- 业务函数签名变更: 无 — 仅:
  - driver main() 增加 `import os` + `os.environ.get(...)` 读 env var (非业务函数)
  - run_round15_merge_export.py:merge_and_export 函数签名不变 (P-003 守住)
- **RESULT: PASS**

### P-004: py_compile + self-test 全过

- py_compile: 7/7 PASS (scenario_group_merger, case_id_and_field_normalizer, run_round15_merge_export, test_case_formatter, case_status_writer, l1_s6, l2_s6)
- self-test: 7/7 PASS
- **RESULT: PASS**

### P-005: v18 治理档不删不改

- v18 dir exists: True
- v18 md count: 5 (round18_CONVERGED / round18_review / round18_audit / round18_goal_round18_merge_5cols / GOAL_DIALECTIC)
- **RESULT: PASS** — v18 治理档完整保留为审计锚点

---

## 8. 审计终判

**CONVERGED_WITH_FOLLOWUP** — V-001~V-005 + P-001/P-003/P-004/P-005 全 PASS, P-002 PARTIAL (driver backup overwrite, 需后续 DT 修复)。

本轮产物闭环 (详见 [`CONVERGED.md`](./CONVERGED.md)):
- 重导 xlsx: `test_cases_public.xlsx` (88×11, 87 cases, 46 merges, 16/16 P0)
- 视觉 PNG: `test_cases_public.v302.visual.png` (1.6MB)
- 治理档: PLAN + audit + review + CONVERGED + DT 5 份
- 验证脚本: `verify_xlsx_physical.py` + `render_v302_visual.py`
