# Round 17 Audit — xlsx 同 OBJ 纵向合并与空行移除

**日期**：2026-07-19  
**Goal ID**：`66727af9-fffd-4be3-965b-d63f78269530`  
**上游 Goal**：Round 16 `6d3edb03-352d-4a3f-921c-b880db0625f5`  
**范围**：只修复 xlsx 视觉布局；不修改 `v3.01 test_cases.json`，不动 L1S6Validator / S7 review_report，不 commit。

## 1. 审计结论

5 项 Value Criteria 与 3 项 Process Criteria 全部 PASS。Round 17 workbook 主表为 88 行 × 11 列，包含 48 个纵向合并区域、0 个空行、16 个连续 OBJ 块和 5 种轮转背景色。

## 2. V/P 验收证据

### V-001 [BLOCKER] 三个 OBJ 共享列纵向合并

**物理证据**：

- OpenPyXL 重新打开 `test_cases_public.xlsx`。
- `len(ws.merged_cells.ranges) == 48`。
- 按列统计：`B=16 / C=16 / D=16`。
- 表头映射：B=`所属模块`，C=`用例描述`，D=`关联需求`。
- 每个 OBJ 块的 D 列合并区域连续覆盖主表第 2~88 行，无缝相接。

**正向论证**：16 个 OBJ 均有多条 Ready TC，因此每个 OBJ 产生 3 个有效纵向区域，满足 `16 × 3 = 48`。

**反向挑战**：为什么不合并 `功能描述`？

同 OBJ 内存在多个 `feature_point_ref` 和多个功能描述。合并 `功能描述` 会只保留首个 FP 的文本并造成数据损失，因此 `功能描述` 保持逐 TC 展示。

**判定**：PASS。

### V-002 [BLOCKER] 主表无空行且行数为 88

**物理证据**：

- `ws.max_row == 88`。
- `ws.max_column == 11`。
- 对第 2~88 行逐列检查，整行空白列表为 `[]`。
- Round 16 备份物理基线仍是 103 行 × 10 列，spacer 为 `[6, 11, 16, 25, 30, 34, 39, 44, 49, 63, 71, 78, 82, 91, 95]`。
- 行数变化：`103 - 15 spacer = 88`。

**判定**：PASS。

### V-003 [BLOCKER] 背景与排序保持正确

**物理证据**：

- 16 个 OBJ ID 按字符串升序排列。
- 每个 OBJ 块内读取 A 列 `case_id`，均等于自身排序结果。
- 每个 OBJ 块内部 A 列背景色唯一，同块一致。
- 全表背景色集合为 5 种：`FFE6E6E6 / FFE3F2FD / FFFFF8E1 / FFE8F5E9 / FFF3E5F5`。

**判定**：PASS。

### V-004 [MAJOR] 用例描述索引保持正确

**物理证据**：

- `用例描述索引` 为 17 行 × 5 列，即 1 header + 16 OBJ。
- 表头为 `OBJ ID / 用例描述(OBJ 名) / FP 数 / TC 数 / Ready 数`。
- OBJ ID 顺序与主表 OBJ 块顺序完全一致。
- 合计：FP=49，TC=87，Ready=87。

**审计更正**：Round 16 `audit_16.md` 曾写 FP 合计 50，但该文档列出的 16 个 FP 数实际相加为 49，且 `test_cases.json meta.fp_count` 也是 49。Round 17 以物理 workbook 与源 JSON 双证据采用 49，不沿用 Round 16 算术误报。

**判定**：PASS。

### V-005 [MAJOR] Draft-Rejected 附录保持 0 cases

**物理证据**：

- `Draft-Rejected附录` 为 1 行 × 11 列。
- 唯一行是 Round 17 profile 的 header。
- 数据 case 数为 0。

**判定**：PASS。

### P-001 [MAJOR] formatter self-test cases 7-9

**证据**：

- Case 7：synthetic 2 OBJ × 3 列，断言 6 个精确合并区域。
- Case 8：断言 `max_row == cases + 1` 且无整行空白。
- Case 9：断言 `obj_id → case_id` 排序与同 OBJ 同色、异 OBJ 异色。
- `python3 ai_workflow/test_case_formatter.py --self-test` 输出 `Round 17 cases 7-9: PASS`。
- `PYTHONPATH=. python3 ai_workflow/run_round15_merge_export.py --self-test` 输出 PASS。
- 两个文件 `py_compile` 通过；编辑文件 lint 为 0。

**判定**：PASS。

### P-002 [MAJOR] v3.01 JSON 严格只读

**物理证据**：

- 字节数：338192。
- SHA-256：`7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca`。
- 导出前后均为同一字节数与哈希。

**判定**：PASS。

### P-003 [MAJOR] Round 16 workbook 备份保留

**物理证据**：

- 路径：`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.round16.bak.xlsx`。
- 字节数：22535。
- SHA-256：`d0bd03b041e4682e732186f5138d0497d6f46048d47fb74a8407a74f385ffa83`。
- 重新打开备份后确认：103 行 × 10 列、0 merge、15 spacer，证明备份确为 Round 16 产物。
- Round 16 的更早备份 `test_cases_public.round16.precheck.bak.xlsx` 未删除。

**判定**：PASS。

## 3. 导出与视觉证据

- 新 workbook：22729 bytes，SHA-256 `dc2fa66dd43f2db611ae7eac08fda64de8c2e480ff8464f6843bca63ee316831`。
- 视觉 PNG：`test_cases_public.round17.visual.png`，158071 bytes。
- 视觉范围：主表行 1~30 / 列 1~5。
- 人工读取结果：OBJ 共享列形成连续纵向色块，OBJ 之间无空白间隔，行 1 header 与 5 种背景区分清晰。
- 环境没有 matplotlib；系统 Python 和项目 venv 均复现 `ModuleNotFoundError`。按“不引入新依赖”约束，改用已安装 Pillow 渲染，未安装任何包。

## 4. 反向挑战：合并后 filter / sort / copy 单行

1. **Filter**：header 可继续加筛选器，但三个合并列的块内后续行是 `MergedCell`，按这些列逐行筛选语义不完整。
2. **Sort**：对含纵向合并区域的主表直接执行逐行排序不可靠，排序前应取消合并。
3. **Copy 单行**：只有 OBJ 块首行持有三列值，复制块内后续单行会缺少所属模块、用例描述、关联需求。
4. **取舍**：本轮按用户明确要求选择视觉审查优先。JSON 保持结构化真相源，`用例描述索引` 保持逐 OBJ 查找入口。
5. **后续选择**：如使用者需要逐行机器操作，应新增未合并的 machine-readable workbook，不覆盖视觉版。

## 5. DT 决策任务与反模式

| ID | 决策 | 结论 |
|---|---|---|
| DT-R17-001 | Round 16 无 `关联需求` 列 | 新增 opt-in `关联需求=obj_id`，不挪用 `功能描述` |
| DT-R17-002 | 纵向合并与逐行操作冲突 | 视觉审查优先，限制显式落档 |
| DT-R17-003 | 是否创建新导出脚本 | 不创建；复用既有 `run_round15_merge_export.py` |
| DT-R17-004 | Round 16 FP 合计 50 是否可信 | 否；物理值和源 meta 均为 49 |

**触发的反模式检查**：

- 未触发“修改 JSON 制造 PASS”。
- 未触发“跳过物理验证”。
- 未触发“新建重复 Python 驱动”。
- 未触发“安装新依赖”。
- 检测到并纠正历史审计算术误报：FP 50 → 49；未改业务数据。

## 6. 审计终态

- V PASS：5/5。
- P PASS：3/3。
- BLOCKER residual：0。
- value ratio：`5 / (5 + 3) = 0.625`。
- 状态：`achieved`。
