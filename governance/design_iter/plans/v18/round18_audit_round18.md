# Round 18 OpenPyXL 物理验收审计

## 1. 输入与受保护资产

- 输入 JSON：`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`
- JSON 重导前后 SHA-256：`7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca`，一致。
- Round 17 备份：`test_cases_public.round17.bak.xlsx`
- 备份重导前后 SHA-256：`dc2fa66dd43f2db611ae7eac08fda64de8c2e480ff8464f6843bca63ee316831`，一致。

## 2. 强制命令原文

```text
✅ _validate_obj_linkage self-test: 4 场景全过
✅ _validate_obj_fp_linkage self-test: 4 场景全过
test_case_formatter xlsx CLI self-test: PASS
test_case_formatter Round 17/18 cases 7-11: PASS
run_round15_merge_export self-test: PASS
```

重导摘要：

```text
input_cases=331
merged_cases=87
compression_ratio=3.805
l1_passed=true
required_errors=0
id_errors=0
trace_errors=0
l2_passed=true
l2_failed_count=0
```

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
FFE6E6E6
FFE3F2FD
FFFFF8E1
FFE8F5E9
FFF3E5F5
```

## 4. 每个 OBJ block × 每列物理合并证据

说明：`M` = 该 OBJ 行区间存在物理 merge range；`I` = 独立 cell。E/F distinct 为该块物理值去重数。

| # | 行 | OBJ | B | C | D | E | F | H | E distinct | F distinct |
|---|---|---|---|---|---|---|---|---|---:|---:|
| 01 | 2-5 | BIZ-BACKEND-01-001-OBJ-01 | M | M | M | I | I | I | 3 | 4 |
| 02 | 6-9 | BIZ-BACKEND-01-002-OBJ-01 | M | M | M | I | I | I | 3 | 3 |
| 03 | 10-13 | BIZ-BACKEND-01-003-OBJ-01 | M | M | M | I | I | I | 3 | 3 |
| 04 | 14-21 | BIZ-BACKEND-01-004-OBJ-01 | M | M | M | I | I | I | 5 | 8 |
| 05 | 22-25 | BIZ-ORDER-01-001-OBJ-01 | M | M | M | I | I | I | 2 | 4 |
| 06 | 26-28 | BIZ-ORDER-01-002-OBJ-01 | M | M | M | I | I | I | 2 | 3 |
| 07 | 29-32 | BIZ-PROMO-01-001-OBJ-01 | M | M | M | I | I | I | 2 | 4 |
| 08 | 33-36 | BIZ-PROMO-01-002-OBJ-01 | M | M | M | I | I | I | 3 | 4 |
| 09 | 37-40 | BIZ-PROMO-01-003-OBJ-01 | M | M | M | I | I | I | 2 | 4 |
| 10 | 41-53 | BIZ-PURCHASE-01-001-OBJ-01 | I | M | M | I | I | I | 4 | 13 |
| 11 | 54-60 | BIZ-PURCHASE-01-002-OBJ-01 | I | M | M | I | I | I | 4 | 7 |
| 12 | 61-66 | BIZ-VIP-01-001-OBJ-01 | M | M | M | I | I | I | 4 | 6 |
| 13 | 67-69 | BIZ-VIP-01-002-OBJ-01 | M | M | M | I | I | I | 2 | 3 |
| 14 | 70-77 | UI-ITEM-MALL-01-001-OBJ-01 | M | M | M | I | I | I | 4 | 8 |
| 15 | 78-80 | UI-ITEM-MALL-01-001-OBJ-02 | M | M | M | I | I | I | 2 | 3 |
| 16 | 81-88 | UI-ITEM-MALL-01-002-OBJ-01 | M | M | M | I | I | I | 4 | 7 |

## 5. 48 与 46 的根因诊断

内存 `block_cases` 证据：

```text
BLOCK_10 obj=BIZ-PURCHASE-01-001-OBJ-01 modules=['BIZ', 'LOG', 'SPECIAL'] B_uniform=False
  SPECIAL-TC-309 module='SPECIAL'
  SPECIAL-TC-313 module='SPECIAL'
  LOG-TC-092 module='LOG'
  其余该块为 module='BIZ'

BLOCK_11 obj=BIZ-PURCHASE-01-002-OBJ-01 modules=['BIZ', 'SPECIAL'] B_uniform=False
  SPECIAL-TC-112 module='SPECIAL'
  其余该块为 module='BIZ'
```

结论：最初“少两个 B merge 是 merged-cell None 副作用”的诊断不成立。修复后的内存 guard 仍返回 False，是因为实际数据有多个 module 值。46 = `B14 + C16 + D16`。E/F 的 `16/16` 非均匀跳过是正确行为；B 的 `2/16` 非均匀跳过也同样是正确行为。

## 6. H 列独立性物理证据

```text
H_MERGE_RANGES=[]
H_CELLS=87
H_CELL_OBJECTS=87
H_NONEMPTY_STRINGS=87
CASE_IDS=87
H_MULTILINE_SINGLE_TC_CELLS=87
```

- 87 个 H cell 全部是普通 `Cell`，没有 `MergedCell`。
- 87 个 H cell 全部是非空 string。
- 87 个 case_id 全部唯一，与 H cell 一一对应。
- 87 个 H cell 都含多行，来源是 `merge_grouped_inplace` 对同一 TC 场景步骤/预期的预期拼接，不是跨 TC 合并。

## 7. V/P 审计结论

| 标准 | 判定 | 证据 |
|---|---|---|
| V-001 patch 生效且 mandatory tests 通过 | PASS | compile + 两个 self-test 返回 0 |
| V-002 88×11、OBJ/case 排序、五色 | PASS | DIMENSIONS / SORT / COLOR 全 True |
| V-003 48 merges，B/C/D 各 16 | FAIL | 46；B=14，C=16，D=16 |
| V-004 E/F uniform guard 不丢值 | PASS | E=0/F=0；16/16 block 非均匀 |
| V-005 H 单 TC 独立 string | PASS | 87 普通 Cell、87 string、87 unique case_id、H merges=0 |
| P-001 不重新发明 patch、不引依赖、不 commit | PASS | 本轮只重导、读审计、视觉与治理落档 |
| P-002 不修改 v3.01 test_cases.json | PASS | SHA-256 重导前后一致 |
| P-003 保留 backup，不动 L1/S7 | PASS | backup SHA-256 一致；未改 L1S6Validator/S7 review_report |

## 8. 审计终判

`BLOCKED`。V-003 与实际 per-TC module 数据契约冲突，不能在禁止重新设计 patch 的条件下合法达成 48。其余 V/P 通过。
