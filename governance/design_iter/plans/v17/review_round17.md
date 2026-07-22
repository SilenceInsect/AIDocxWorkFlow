# Round 17 Review — xlsx 合并、空行与可操作性复盘

**日期**：2026-07-19  
**Goal ID**：`66727af9-fffd-4be3-965b-d63f78269530`  
**状态**：achieved。

## 1. 用户可见缺陷

1. Round 16 主表没有合并区域，同 OBJ 的共享字段重复 87 行。
2. 16 个 OBJ 之间插入 15 个空行，主表从应有的 88 行膨胀到 103 行。
3. Round 16 主表没有 `关联需求` 可见列，用户提出的第三个共享字段无法直接合并。

## 2. 根因

### 根因 A：Round 16 把 spacer 当作主要视觉分隔手段

Round 16 `_populate_worksheet_with_obj_grouping` 在 OBJ 切换时 append 空行。该设计能切色，但把一个连续执行表拆成 16 段，视觉代价高于收益。

### 根因 B：Round 16 只做背景，没有记录 OBJ 行段

Round 16 writer 按行写色，没有保留 `group_start_row/end_row`，因此无法在 OBJ 块结束时执行 `merge_cells`。

### 根因 C：字段语义未区分 OBJ 共享字段与 FP/TC 字段

- OBJ 共享：所属模块、用例描述、关联需求（obj_id）。
- FP/TC 独有：功能描述、步骤、预期、优先级、状态等。

没有先做字段分类时，容易把 `功能描述` 误当作可合并字段，导致只保留首个 FP 文本。

## 3. 已落地修复

### 3.1 Formatter

- 新增 Round 17 opt-in profile：11 列，加入 `关联需求=obj_id`，把 `模块` 显示名调整为 `所属模块`。
- `_populate_worksheet_with_obj_grouping` 改为记录连续 OBJ 块，不再写 spacer。
- 每块结束后合并 `所属模块 / 用例描述 / 关联需求`。
- 合并首格垂直居中并换行；5 色背景继续覆盖完整 OBJ 块。
- 默认 profile 和公共 `--tc-json-to-xlsx` 的 10 列契约保持不变，只有 Round 17 主调 opt-in。

### 3.2 导出主调

- 复用 `run_round15_merge_export.py`，不创建新脚本。
- 排序键调整为 `obj_id → case_id`，满足“同 OBJ 内 case_id 升序”。
- 覆盖前备份为 `test_cases_public.round16.bak.xlsx`。
- 源 JSON 只读，导出仍走 normalize → merge → L1/L2 → xlsx。

### 3.3 测试

- Case 7 验证 `OBJ 数 × 3` 个合并区域。
- Case 8 验证零 spacer 与 `TC 数 + header` 行数。
- Case 9 验证排序和颜色回归。
- Formatter、export driver、py_compile、lint 全部通过。

## 4. 验收结果

| 项 | 结果 |
|---|---|
| 主表尺寸 | 88 行 × 11 列 |
| merge regions | 48 |
| merge 列分布 | B/C/D 各 16 |
| 空行 | 0 |
| OBJ | 16，升序 |
| 同 OBJ case_id | 全部升序 |
| 背景 | 5 色轮转 |
| 索引 | 16 OBJ，TC=87，Ready=87，FP=49 |
| 附录 | 0 cases |
| 源 JSON | 338192 bytes，SHA-256 不变 |
| Round 16 备份 | 已保留并可物理打开 |

## 5. 反向挑战：合并后的工作表是否仍适合逐行操作

### 5.1 Filter

header 层面仍可设置筛选器，但合并列只有块首行有值。对 `所属模块 / 用例描述 / 关联需求` 执行逐行过滤，块内后续行可能被视为空值，不能宣称完全兼容。

### 5.2 Sort

Excel 对包含纵向合并单元格的区域排序有限制。使用者需要先取消合并，或使用 JSON/未合并导出完成机器排序。

### 5.3 Copy 单行

复制 OBJ 块首行可以带出三列共享值；复制块内后续行会缺共享值。视觉版适合块审查，不适合逐行数据交换。

### 5.4 结论

本轮没有同时满足“纵向合并视觉审查”和“每行完全自包含机器数据”，两者在同一个 Sheet 内存在结构冲突。用户本轮明确要求合并，因此选择视觉审查优先；JSON 与索引 Sheet 保留结构化入口。若后续要求两者并存，应新增独立未合并 workbook，而不是撤销视觉版。

## 6. 历史证据纠正

Round 16 audit 写“Sheet 2 FP 数合计 50”，但列出的数字相加为 49：

`3+3+3+5+2+2+2+3+2+4+4+4+2+4+2+4 = 49`。

Round 17 workbook 物理求和为 49，源 `test_cases.json meta.fp_count` 也是 49。本轮只纠正审计结论，不修改源 JSON。

## 7. Follow-up 清理

- FU-B1 视觉分组残留：已完成，spacer 删除、三列合并。
- FU-A2 SSOT 拆约束对象：继续留在 v3.02 治理。
- FU-A4 step/expected 错位：继续留在 v3.02 prompt 治理。
- `_sync_list_fields_after_merge` 兜底清理：未进入本轮。
- `source_case_ids` 主表渲染：未进入本轮。
- 新增可选 follow-up：如需要逐行筛选/排序/复制，单独导出未合并 machine-readable workbook。

## 8. 影响范围

### 实现

- `ai_workflow/test_case_formatter.py`
- `ai_workflow/run_round15_merge_export.py`

### 治理

- `governance/design_iter/current/goal_round17_merge_cells.md`
- `governance/design_iter/plans/v17/audit_round17.md`
- `governance/design_iter/plans/v17/review_round17.md`
- `governance/design_iter/plans/v17/CONVERGED_round17.md`

### 过程资产

- `test_cases_public.xlsx`
- `test_cases_public.round16.bak.xlsx`
- `test_cases_public.round17.visual.png`
- Round 17 snapshot。

### 未影响

- `.mdc / SKILL.md / AGENTS.md` 阶段约束。
- `v3.01 test_cases.json`。
- L1/L2 validator 行为。
- S7 review_report。
- Git 历史；本轮未 commit。

## 9. 反模式自检

1. 没有用修改源 JSON 的方式让验收通过。
2. 没有只看代码推断 merge；实际重新打开 workbook 并数了 48 个区域。
3. 没有用空行数推断行数；实际检查了 88 行和空行列表。
4. 没有安装 matplotlib；缺包后改用现有 Pillow，遵守无新依赖。
5. 没有掩盖合并对 filter/sort/copy 的限制。
6. 没有把 Round 16 的 FP 算术误报继续复制到新审计。
