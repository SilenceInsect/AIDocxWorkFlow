# Round 18 Convergence Verdict — Blocked

## 1. Verdict

Round 18 未收敛到用户指定的 `48 merges`，当前状态为 `blocked`，不是 `achieved`。

已完成并可复用的安全结果：

- `test_cases_public.xlsx` 重导成功。
- 88 行 × 11 列。
- 16 个 OBJ 块、五种色带、OBJ/case 排序通过。
- 46 个物理 merge：B=14、C=16、D=16。
- E=0、F=0、H=0，均保护了 per-TC 值。
- H 为 87 个独立非空 string，与 87 个唯一 case_id 一一对应。

## 2. DT-R18-001 至 DT-R18-004

### DT-R18-001

B/C/D 三列不足以表达五列合并意图，配置升级为 B-F 五列候选；候选列仍必须通过 uniform guard。实测真正合并为 B14/C16/D16。

### DT-R18-002

H 列永不合并。每个 H cell 是一个 TC 的独立 string；内部多行是同场景步骤/预期聚合，合并 worksheet 行会丢其他 TC 的信息。

### DT-R18-003

合并会丢单 TC 字段值时，使用内存 uniform guard 跳过。E/F 在 16/16 OBJ 非均匀；B 在 2/16 OBJ 非均匀。B 的两个跳过与 E/F 的跳过属于同一数据保护规则。

### DT-R18-004

cell string 内 concat 经物理审计为 `merge_grouped_inplace` 同场景预期拼接，不是跨 TC Excel 合并 bug。判定依据是 H merge ranges 为空且每行保持普通 Cell。

## 3. 为什么不能宣告 48 PASS

两个 OBJ 块存在以下 module 真值：

- `BIZ-PURCHASE-01-001-OBJ-01`: `BIZ / LOG / SPECIAL`
- `BIZ-PURCHASE-01-002-OBJ-01`: `BIZ / SPECIAL`

强制合并 B 会只保留左上角 BIZ，导致 `LOG-TC-092`、`SPECIAL-TC-309`、`SPECIAL-TC-313`、`SPECIAL-TC-112` 的模块值在视觉表中消失。该行为违反 DT-R18-003，也违反 V-005 所强调的单 TC 字段独立契约。

## 4. 收敛条件

满足以下任一条件后，才能把 snapshot 更新为 achieved：

1. 用户接受动态安全合并，验收基线由 48 改为 46；或
2. 用户批准 B 列改为 OBJ 归属模块，并提供独立的 per-TC module 展示位置与字段来源契约。

## 5. 当前产物

- Workbook：`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx`
- Visual：`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round18.visual.png`
- Audit：`governance/design_iter/plans/v18/round18_audit_round18.md`
- Review：`governance/design_iter/plans/v18/round18_review_round18.md`

本轮未 commit，未修改输入 JSON，未删除或改变 Round 17 备份。
