# Round 18 五列合并收尾目标与决策

## 1. Goal

在不修改 `test_cases.json`、不改写既有修复 patch、不引入依赖、不删除 Round 17 备份、不提交 Git 的前提下，重新导出 `test_cases_public.xlsx`，并通过 OpenPyXL 物理读取验证 OBJ 色带、B-F 五列合并意图、H 列单 TC 独立性及数据保护契约。

## 2. Plan

1. Read 并确认 `_block_is_field_uniform` 从内存 `block_cases` 判断均匀性。
2. 执行 `py_compile`、formatter self-test、merge/export self-test。
3. 保存受保护文件 hash，重导 xlsx，再校验 hash 不变。
4. OpenPyXL 物理读取 88 × 11、排序、颜色、merge ranges、H cell 类型和值。
5. 生成视觉 PNG，记录真实合并边界和 H 列独立边界。
6. 将 PASS/FAIL、反模式和后续决策写入 Round 18 治理产物与新 snapshot。

## 3. Act 结果

- 编译与两组 self-test 全部通过。
- 输入 331 TC，经同场景聚合得到 87 TC；L1/L2 全通过。
- 重导产物为 88 行 × 11 列，OBJ 与 case_id 排序通过，五色块通过。
- 实际合并为 46，不是预期的 48：B=14、C=16、D=16、E=0、F=0、H=0。
- 两个 B 列未合并不是 worksheet `MergedCell(None)` 副作用，而是内存数据确实非均匀：
  - `BIZ-PURCHASE-01-001-OBJ-01` 同时包含 `BIZ`、`LOG`、`SPECIAL`。
  - `BIZ-PURCHASE-01-002-OBJ-01` 同时包含 `BIZ`、`SPECIAL`。
- 因硬约束禁止重新发明 patch，本轮没有把 mixed module 强行归一为 BIZ，也没有绕过 uniform guard。

## 4. Decision Table

### DT-R18-001：从三列意图升级到五列意图

- 决策：`merge_obj_headers` 包含 `用例描述 / 所属模块 / 关联需求 / 功能描述 / 前置条件`。
- 保护：五列是候选列，不是无条件合并列；最终合并必须通过内存 uniform guard。
- 实测：C/D 在 16 个 OBJ 全均匀；B 在 14 个 OBJ 均匀；E/F 在 16 个 OBJ 全非均匀。

### DT-R18-002：H 列永不合并

- 决策：`预期结果` H 列不进入 `merge_obj_headers`。
- 依据：OpenPyXL 物理读取 87 个 H cell，全部是独立 `Cell`、非空 string，并与 87 个唯一 case_id 一一对应。
- 结论：H 内换行表示单个 TC 的多步预期；跨行合并会丢失其他 TC 的预期值。

### DT-R18-003：非均匀字段必须使用 uniform guard

- 决策：任何 OBJ 块只要候选列存在两个以上实际值，就不合并。
- 依据：E/F 在 16/16 OBJ 非均匀；B 在 2/16 OBJ 非均匀。
- 结论：请求中的 `16 OBJ × B/C/D = 48` 与实际 B 列 per-TC module 数据契约冲突。强制 48 会让 `LOG`/`SPECIAL` 值在 Excel 中不可见。

### DT-R18-004：cell 内 concat 检测

- 决策：将 `merge_grouped_inplace` 对同场景单 TC 的步骤/预期拼接视为预期聚合，不认定为跨 TC 的 Excel 合并缺陷。
- 依据：87/87 H cell 均为独立单元格，且 87/87 值包含多行；H 没有任何 merge range。
- 结论：字符串内换行是同一 TC 内容，worksheet 跨行合并才是需要禁止的数据损失路径。

## 5. 收敛标准与当前判决

- V-001 编译与 self-test：PASS。
- V-002 88 × 11、排序、五色：PASS。
- V-003 48 merges 且 B=16：FAIL，实际 46 且 B=14。
- V-004 E/F 非均匀保护：PASS。
- V-005 H 列独立性：PASS。
- P-001 至 P-003：PASS。

当前状态为 `blocked`，不能写成 `achieved`。解除阻塞需要人工在以下两种语义中选择一种：

1. 保留 per-TC module 真值：接受 46 为正确安全结果。
2. 将 B 改为 OBJ 归属模块：新增独立展示字段或明确的 canonicalization 规则后，再评估 48；不能直接覆盖现有 per-TC module。

## 6. 落档执行记录

本轮新增治理文件、视觉 PNG 和新 goal snapshot；未提交 Git，未修改 `test_cases.json`，未修改 L1S6Validator 或 S7 review_report。
