# Goal: Round 17 xlsx 同 OBJ 纵向合并与空行移除

> **触发源**：Round 16 `test_cases_public.xlsx` 的 15 个 OBJ spacer 行和 0 个合并区域造成视觉割裂与重复字段。
> **范围**：只修改公共 xlsx 导出表现、formatter 自测和本轮治理资产；`v3.01 test_cases.json` 保持只读。
> **状态**：执行中。

## 1. 现状与上游结论

### 1.1 Round 16 已完成

1. 主表 87 条 Ready TC 已按 `obj_id → feature_point_ref → case_id` 排序；Round 17 验收将排序契约收敛为 `obj_id → case_id`，确保同 OBJ 内 case_id 单调升序。
2. 同 OBJ 使用 5 色背景轮转。
3. 主表在 16 个 OBJ 之间插入 15 个 spacer 行，因此总行数为 103（1 header + 87 TC + 15 spacer）。
4. `用例描述索引` 保持 16 OBJ × 5 列；`Draft-Rejected附录` 只有 header。
5. Round 16 workbook 没有任何 `merge_cells` 区域。

### 1.2 Round 17 要清理的遗留

- FU-B1 的排序、背景和索引已落地，但 spacer 行造成视觉断裂。
- 同 OBJ 的共享字段逐行重复，用户无法快速识别 OBJ 块。
- Round 16 其余遗留（v3.01 step/expected、SSOT 拆约束对象、normalizer 兜底、source_case_ids 展示）不进入本轮。

## 2. 目标与验收

### 2.1 Value Criteria

- V-001：16 个 OBJ 的 3 个共享列均纵向合并，物理合并区域数为 48。
- V-002：主表无空行，物理行数为 88（1 header + 87 TC）。
- V-003：5 色背景、`obj_id` 升序和同 OBJ 内 `case_id` 升序保持正确。
- V-004：`用例描述索引` 保持 16 OBJ × 5 列，FP/TC/Ready 汇总不变。
- V-005：`Draft-Rejected附录` 保持 0 cases。

### 2.2 Process Criteria

- P-001：`test_case_formatter.py --self-test` 增加并通过 case 7-9。
- P-002：`v3.01 test_cases.json` 字节数与 SHA-256 均保持不变。
- P-003：Round 16 workbook 备份保存为 `test_cases_public.round16.bak.xlsx`。

## 3. 合并与空行策略

### 3.1 主表列契约

Round 16 实际公共表头为 10 列：`用例ID / 模块 / 用例描述 / 功能描述 / 前置条件 / 操作步骤 / 预期结果 / 优先级 / 用例状态 / 备注`。

用户要求的 3 个 OBJ 共享字段中，`模块` 与 `用例描述` 已存在；`关联需求` 在 Round 16 主表不存在。Round 17 采用 opt-in 项目导出 profile：

1. `模块` 显示名调整为 `所属模块`，值仍取 `模块/module`。
2. 在 `用例描述` 后加入 `关联需求`，值取 `obj_id`，形成对 `用例描述索引` 中 OBJ ID 的明确引用。
3. 保留 `功能描述`；不得把 `功能描述` 跨 OBJ 合并，因为同 OBJ 内存在多个 FP，强行合并会丢失功能点信息。
4. 保留其余现有字段；本轮不把 `feature_point_ref` 或 `source_case_ids` 新增到可见列。

### 3.2 OBJ 块写入

1. 先按 `obj_id → case_id` 稳定排序；`feature_point_ref` 保留为逐 TC 元数据，但不再介于 OBJ 与 case_id 之间，避免 case_id 在同 OBJ 内回跳。
2. 每个 OBJ 连续写入所有 TC，不写 spacer。
3. 记录每个 OBJ 的 `start_row` 与 `end_row`。
4. OBJ 块写完后，对 `所属模块 / 用例描述 / 关联需求` 三列分别调用 `merge_cells`。
5. 单 TC OBJ 只有一行，不创建单格合并区域；当前 16 个 OBJ 均有多条 TC，因此目标 workbook 应产生 48 个区域。
6. 合并单元格保持顶端值，设置垂直居中；OBJ 背景继续覆盖整块全部列。

### 3.3 不合并列

- `用例ID`
- `功能描述`
- `前置条件`
- `操作步骤`
- `预期结果`
- `优先级`
- `用例状态`
- `备注`
- 任何未来加入的 `feature_point_ref / source_case_ids / 标签` 等逐 TC 字段

### 3.4 Sheet 2 与 Sheet 3

- `用例描述索引` 不做纵向合并：每个 OBJ 本来只有一行，继续保持 16 行数据 × 5 列。
- `Draft-Rejected附录` 不启用 OBJ 合并：保持原输入顺序和双 Sheet 分流契约。

## 4. Self-test 设计

### Case 7：OBJ 纵向合并

构造 2 个 OBJ、每个 OBJ 至少 2 条 Ready TC，使用 Round 17 profile 写出 workbook；读取 `merged_cells.ranges`，断言区域数等于 `OBJ 数 × 3`，并断言三列均覆盖完整 OBJ 行段。

### Case 8：spacer 移除

读取 synthetic workbook 主表，断言 header 以下不存在整行空白，且 `max_row == TC 数 + 1`。

### Case 9：排序回归

从 synthetic workbook 的 `用例ID` 列读取非空行，并结合输入映射验证 `obj_id` 升序、同 OBJ 内 `case_id` 升序；同时验证 2 个 OBJ 使用不同背景色。

## 5. 执行任务

1. 修改 `ai_workflow/test_case_formatter.py`：移除 spacer，完成 OBJ 块合并与 case 7-9。
2. 修改 `ai_workflow/run_round15_merge_export.py`：使用 Round 17 opt-in profile，并将备份名固定为 `.round16.bak.xlsx`。
3. 运行 `py_compile`、formatter self-test、主调 self-test。
4. 备份并重导 `test_cases_public.xlsx`。
5. 使用 OpenPyXL 重新打开 workbook，逐项验证 48 merge、88 行、0 空行、排序、背景、索引与附录。
6. 使用现有 matplotlib 生成行 1-30 / 列 1-5 的视觉 PNG，并读取 PNG 做人工检查。
7. 落 `audit_round17.md / review_round17.md / CONVERGED_round17.md` 与新 snapshot。

## 6. 反向挑战与取舍

### 6.1 合并后还能否 filter / sort / copy 单行

- Excel 自动筛选仍可挂在 header，但对包含纵向合并单元格的三列执行逐行排序并不可靠，排序前应先取消合并。
- 复制单行时，只有 OBJ 块首行携带三列实际值；块内后续行是 `MergedCell`，单行复制会缺共享字段。
- 本轮选择视觉审查优先，原因是用户明确要求纵向合并；JSON 和 `用例描述索引` 继续提供机器消费与逐 OBJ 查找能力。
- 风险会写入 Round 17 review，不把“可筛选/可排序/可复制单行”误报为完全兼容。

### 6.2 不合并功能描述

同 OBJ 内 `功能描述` 随 `feature_point_ref` 变化。跨 OBJ 块合并 `功能描述` 会只保留首个 FP 值并造成数据损失，因此明确禁止。

## 7. 决策任务（DT）

- DT-R17-001：Round 16 主表没有 `关联需求` 列；选择 opt-in profile 新增 `关联需求=obj_id`，不挪用 `功能描述`，避免 FP 数据丢失。
- DT-R17-002：纵向合并与逐行筛选/排序/复制存在天然冲突；按用户要求选择视觉块审查优先，并保留 JSON/索引作为结构化入口。
- DT-R17-003：只修改 formatter 与既有导出主调，不创建新的 Round 17 Python 驱动，避免重复导出链路。

## 8. 影响范围与 Git 分类

- 实现资产：`ai_workflow/test_case_formatter.py`、`ai_workflow/run_round15_merge_export.py`。
- 治理资产：本 Plan、Round 17 audit/review/CONVERGED。
- 过程资产：xlsx、备份、PNG、snapshot；不提交 Git。
- 约束文件：不修改 `.mdc / SKILL.md / AGENTS.md / hooks.json`，因此不改变 Agent 阶段契约。
- 禁区：不修改 `test_cases.json`、L1S6Validator、S7 review_report，不重跑 v3.01 S6 数据生成，不 commit。

## 9. 落档协议执行记录

1. Plan 已在代码修改前创建。
2. 实现改动：`ai_workflow/test_case_formatter.py`、`ai_workflow/run_round15_merge_export.py`。
3. 物理产物：Round 17 workbook 为 88 行 × 11 列、48 merge、0 空行；Round 16 备份为 103 行 × 10 列、0 merge、15 spacer。
4. 验证：formatter self-test cases 7-9、export-driver self-test、py_compile 与 lint 全部通过。
5. 治理落档：`audit_round17.md`、`review_round17.md`、`CONVERGED_round17.md`、`.goal-log-db/active/66727af9-fffd-4be3-965b-d63f78269530/snapshot.json`。
6. 源保护：`test_cases.json` 仍为 338192 bytes，SHA-256 `7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca`。
7. 本轮未 commit。
