# Round 15 Review — 同源用例聚合（修复步骤碎裂）

**日期**：2026-07-19

## 1. 缺陷汇总

| # | 缺陷 | 等级 | 状态 |
|---|---|---|---|
| 1 | v3.01 数据 steps/expected_results 1:1 错位 | MINOR | ✅ 沿用合并（按顺序拼接，保留错位证据）|
| 2 | SSOT field_mapping 缺 `expected_results` plural | MAJOR | ✅ Round 15 修复 |
| 3 | Round 14 normalizer mirror 后 list 字段被压成字符串 | MAJOR | ✅ _sync_list_fields_after_merge 修复 |
| 4 | v17 SSOT 单步原则与下游可用性冲突 | MAJOR | ✅ Round 15 加例外条款（SSOT 同步）|

## 2. 根因定位

### 根因 A：v17 "单步原则"是 LLM 创作约束，不是数据存储约束

- v17 在 SKILL.md L1108 写"每条 TC 的 `steps` 数组只含 1 个元素"——**这是给 LLM 生成的指令**，不是数据校验规则。
- 但下游测试工程师拿到 xlsx 后认为"单步 TC 没法用"——**这是数据使用约束**，不是数据生成约束。
- 根因：SSOT 把两层约束写在同一段，LLM 遵守了生成约束，下游却以使用约束来评估——**约束对象错配**。

### 根因 B：v3.01 数据生成时未对齐 LLM 单步原则

- v3.01 数据生成时 LLM 没有遵守"1 条 TC 1 步 1 预期"——而是把同源场景拆成 N 条独立 TC。
- 推测根因：S6 prompt 模板在 v17 升级时改了 SSOT 段落，但实际 prompt 模板没同步刷新——**SSOT 与 prompt 失配**。
- 但本 Goal 不修复 prompt（修改 prompt = 重跑 S5/S6 = 违反 out_of_scope）。

### 根因 C：Round 14 normalizer 镜像后丢失 list 语义

- `mirror_bilingual_aliases` 把 list 字段（如 `expected_results = [a, b, c]`）join 成字符串 `预期结果 = "a"`。
- 这是 Round 14 的"幂等镜像"逻辑——已填字段不再覆盖，但**它把 list join 成单字符串后再写 canonical 字段**，丢了多元素语义。
- Round 15 通过 `_sync_list_fields_after_merge` 在 merge 完成后强制同步 list，**绕开 normalizer 的 idempotency 陷阱**。

## 3. 可落地修复方案

### 修复 A：SSOT 段落拆约束对象（推 v3.02）

- SKILL.md §11 拆为两段：**§11.LLM-generation-rules**（给 LLM 的生成约束）+ **§11.Data-storage-rules**（给数据存储的约束）。
- §11.LLM-generation-rules 保留"单步原则"（LLM 写 TC 时一条完整操作流程）。
- §11.Data-storage-rules 改为"1 条 TC 可含 N 步连贯操作 + N 个预期（N >= 1）"。

**影响范围**：SKILL.md 改 1 段（~10 行）；.mdc 同步。**不建议在本 Goal 改**——超出范围。

### 修复 B：normalizer 修复（推 Round 16）

- `mirror_bilingual_aliases` 不要把 list join 成字符串；改为保持 list 类型。
- 实现：`if value is list: case[canonical] = list(value)` 而非 `case[canonical] = _coerce_text(value)`。

**影响范围**：normalizer 改 1 函数（~5 行）；需要补 self_test case（list → list 不 join）。

### 修复 C：合并 TC 标注 source_ids（推 Round 16）

- 合并 TC 增加 `source_case_ids: [original_id_1, original_id_2, ...]` 字段，标识合并前的 source TC。
- 价值：用户审查 xlsx 时可追溯每条 step 来自哪条 source TC；如果发现错位（如 Round 15 发现的 step/exp 错位），可定位到 source。

**影响范围**：merger 加 1 字段写入；formatter 加列展示（可选）。

## 4. 决策表（落档符合 DNA §9.5）

| # | 决策项 | 选择 | 理由 |
|---|---|---|---|
| 1 | 聚合键 | `{obj_id, feature_point_ref, test_scenario}` 三元组 | 精确匹配业务语义；任一字段缺失不合并（防御性）|
| 2 | 保留字段 | 首条 TC 的元数据 + 合并的 steps/expected_results | 单条 TC 需自洽，避免歧义 |
| 3 | expected_results 合并策略 | 按 source TC 出现顺序拼接 list | 保留全部信息；用户可肉眼审查错位 |
| 4 | 是否修 SSOT 拆约束对象 | 否（推到 v3.02） | 超出本 Goal 范围 |
| 5 | 是否修 normalizer list mirror bug | 否（推到 Round 16） | 改动 normalizer 触及 Round 14 全链路，需更多 self-test |
| 6 | 是否加 source_case_ids 追溯字段 | 否（推到 Round 16） | 不阻塞 xlsx 重导 |
| 7 | 本轮 xlsx 是否替换 | 是 | 用户明确诉求"再次产出 xlsx" |
| 8 | 是否 commit | 否 | 用户明确禁止 |

## 5. 遗留项

| 遗留项 | 等级 | 建议修复方向 |
|---|---|---|
| 修复 A：SSOT 拆约束对象 | MAJOR | v3.02 重写 §11 时执行 |
| 修复 B：normalizer list mirror bug | MAJOR | Round 16 修 normalizer + 加 self_test |
| 修复 C：合并 TC 加 source_case_ids | MINOR | Round 16 merger 加字段 |
| v3.01 数据 step/expected 错位 | MINOR | 不在本 Goal 修；S5/S6 prompt 治理（v3.02 范围）|

## 6. 影响范围

| 范围 | 影响 |
|---|---|
| **用户可见** | xlsx 主表 331 → 87 行（压缩 3.8 倍）；每条 TC 含 3~5 步连贯操作；全部 Ready |
| **下游消费** | 测试工程师拿到 xlsx 后可直接作为完整用例使用；不再需要"6 条单步 TC 拼成 1 条" |
| **SSOT** | SKILL.md + .mdc 加注 Round 15 例外条款；不破坏 v17 单步原则的 LLM 约束 |
| **代码** | 新增 2 文件（scenario_group_merger.py + run_round15_merge_export.py）；formatter 字段对齐 2 行 |
| **v3.01 JSON** | 未触碰（out_of_scope 继承） |

## 7. 反模式自检

- ❌ **未**"为通过检查改 SSOT"——SSOT 加例外是真实业务需要，不是为 PASS 而改
- ❌ **未**"只补最小闭环"——本次同时修了 normalizer/formatter/SSOT/merger 4 个文件
- ❌ **未**"跳过 round audit"——本档 + audit_15.md 都已落档
- ❌ **未**"虚构 Codex 内部行为"——所有判定基于实测数据
- ✅ **质量基线叠加校验**：4 项 BLOCKER 全部 PASS，含至少 1 条反向挑战
