# Round 16 Review — Round 15 §11.5 遗留 follow_up + 格式治理（GL-017 Round 1）

**日期**：2026-07-19
**Goal ID**：`6d3edb03-352d-4a3f-921c-b880db0625f5`
**触发**：GL-017（新 Goal-loop 编号）Round 1 Act——合并 Round 15 §11.5 遗留 4 项 follow_up（normalizer list mirror bug / source_case_ids / FU-A2 拆约束对象 / FU-A4 step 错位）+ Round 16 用户新诉求 1 项（用例描述/功能描述格式治理）。

---

## 1. 缺陷汇总

| # | 缺陷 | 等级 | 状态 |
|---|---|---|---|
| 1 | normalizer `mirror_bilingual_aliases` 把 list 字段 join 成字符串 → Round 15 §3 根因 C | MAJOR | ✅ Round 16 直接修复（`_resolve_field` 保留 raw type）|
| 2 | 合并 TC 缺 `source_case_ids` 追溯字段 → Round 15 §11.7 关键观察 2 缺工具 | MINOR | ✅ Round 16 merger 加字段 + self_test 覆盖 |
| 3 | xlsx 主表无 OBJ→FP 分组排序 + 同 OBJ 同色背景 → Round 16 用户新诉求 | MAJOR | ✅ Round 16 formatter 加 sort_options + 同色背景 + 空行 |
| 4 | 缺 Sheet 2「用例描述索引」→ Round 16 用户新诉求（OBJ/FP 全局视图）| MAJOR | ✅ Round 16 formatter 加 description_index_sheet |
| 5 | SSOT 缺测试设计层级原则 → LLM 生成 TC 时无层级化指引 | MAJOR | ✅ Round 16 SKILL.md + .mdc 双写 §11.1 |
| 6 | v3.01 数据 step/expected 错位（Round 15 §11.5 FU-A4）| MINOR | ❌ 推 Round 17（v3.02 prompt 治理；out_of_scope §10）|
| 7 | SSOT 拆约束对象（Round 15 §11.5 FU-A2 LLM 生成 vs 数据存储）| MAJOR | ❌ 推 Round 17（v3.02 治理；超出本轮范围）|

---

## 2. 根因定位

### 根因 A：normalizer `_resolve_field` 行为契约错位

- v17 设计：`_resolve_field` 返回 `(str, bool)`——所有值走 `_coerce_text` 统一字符串化
- 根因：v17 设计时只考虑了"canonical 字段是 string"——但 L1 校验器同时接受 `前置条件`/`操作步骤`/`预期结果` 为 list（v17 字段映射表已明文）
- 后果：`mirror_bilingual_aliases` 把 list join 成单字符串 → Round 15 §3 根因 C → 触发 `_sync_list_fields_after_merge` 兜底
- Round 16 修复：`_resolve_field` 返回 `tuple[Any, bool]`，`mirror_bilingual_aliases` 加 `_LIST_CANONICAL_KEYS` 白名单——list 保持 list

### 根因 B：xlsx 主表无用户视角的视觉分组

- v17 Round 12 设计：xlsx 主表按输入顺序铺排，10 列固定
- 根因：v17 设计时关注"xlsx 双 Sheet 分流"（Ready 主表 + Draft 附录），但未关注"用户在主表内 OBJ 分组浏览"的视觉体验
- 后果：v3.01 87 TC 在主表里看似随机排列，下游测试工程师需要肉眼按用例描述分组
- Round 16 修复：OBJ→FP→case_id 三键排序 + 同 OBJ 同色背景 + OBJ 边界空行 + Sheet 2 索引

### 根因 C：SSOT 缺测试设计层级原则

- v17 Round 12-15 设计：SSOT 含"单步原则 / 单预期原则" + Round 15 例外条款（合并多步），但缺**层级化展开规则**
- 根因：v17 设计时把"LLM 应生成什么样的 TC"和"数据存储应保留什么样的 TC"两层约束混在一段，**未明确"1 OBJ 下几个 TC / 1 FP 下几个 TC"的层级映射规则**
- 后果：LLM 生成 TC 时无层级指引——可能 1 OBJ 下只生成 1 条 TC（覆盖不足）或 1 步 1 TC（碎裂过度）
- Round 16 修复：SKILL.md + .mdc 双写 §11.1「测试设计层级原则（4 层级 + 反模式 5 项 + 正反例）」

---

## 3. 可落地修复方案（已落地）

### 修复 A：normalizer 行为契约变更（Round 16 已落地）

- `_resolve_field` 返回 `(Any, bool)`——保留 raw Python 类型
- `mirror_bilingual_aliases` 加 `_LIST_CANONICAL_KEYS = {"前置条件", "操作步骤", "预期结果"}` 白名单
- list 输入 → list 镜像（`list(value)` 复制避免引用共享）
- 其它字段（dict / 非白名单 list）→ 走 `_coerce_text` 兜底

**影响范围**：仅 `mirror_bilingual_aliases` 内部——`_resolve_field` 不被外部调用。Round 15 `_sync_list_fields_after_merge` 补丁**不再必要**（可后续 Round 17 清理，但保留不影响正确性）。

### 修复 B：xlsx 视觉分层（Round 16 已落地）

- `_save_xlsx` 新增 opt-in 参数：
  - `sort_options: dict | None`：None 时保持原行为（向后兼容）
  - `description_index_sheet: bool`：False 时不生成 Sheet 2
- 新增 helper：
  - `_sort_cases_by_obj_fp()`：按 `obj_id → feature_point_ref → case_id` 升序
  - `_populate_worksheet_with_obj_grouping()`：5 色轮转 + OBJ 边界空行
  - `_build_case_description_index_rows()`：聚合 Ready cases by OBJ
  - `_populate_description_index_sheet()`：写 Sheet 2 索引
- 主调 `run_round15_merge_export.py` 升级调用 opt-in 参数

**影响范围**：xlsx 视觉升级；JSON 数据源不动（out_of_scope）；双 Sheet 分流契约不变。

### 修复 C：SSOT 测试设计层级原则（Round 16 已落地）

- SKILL.md 新增 `#### 测试设计层级原则（Round 16 新增 · 永久强制）` 段
- .mdc 新增 `### §11 测试设计层级原则（Round 16 新增 · 同步 SKILL.md §11.1）` 段
- 内容：4 层级 + 反模式 5 项 + 正反例对比 + Round 16 强制条款 5 条

**影响范围**：未来 Round 17+ LLM 生成 TC 时按层级原则展开；本轮不重跑 S5/S6（out_of_scope）。

---

## 4. 决策表（落档符合 DNA §9.5）

| # | 决策项 | 选择 | 理由 |
|---|---|---|---|
| 1 | normalizer 行为契约变更 | `_resolve_field` 返回 `Any` + list 镜像白名单 | 修复 list→list 语义丢失误；与 SKILL.md §11 L1 校验器字段类型对齐 |
| 2 | merger source_case_ids 字段类型 | `list[str]`（singleton 也强制 1 元素 list）| 契约统一；下游用 `case.get("source_case_ids") or []` 兼容 |
| 3 | xlsx 主表排序键 | `obj_id → feature_point_ref → case_id` 三键 | OBJ 分组 + FP 内排序 + case_id 稳定 |
| 4 | 同 OBJ 同色背景 | 5 色轮转（gray/blue/yellow/green/purple）| 视觉区分 + WCAG AA 对比度 |
| 5 | OBJ 边界空行 | True（默认）| 视觉分隔；末尾 OBJ 不插 trailing spacer |
| 6 | Sheet 2 列定义 | OBJ ID / 用例描述(OBJ 名) / FP 数 / TC 数 / Ready 数 | 用户原话："OBJ 名 / FP 数 / TC 数 / Ready 数" |
| 7 | sort_options 默认值 | None（保持原行为）| 向后兼容；opt-in 升级路径 |
| 8 | description_index_sheet 默认值 | False | 向后兼容；按需启用 |
| 9 | 是否修 v3.01 JSON | ❌ 不修（out_of_scope §10）| 继承 Round 12-15 约束 |
| 10 | 是否 commit | ❌ 不 commit（用户明确）| 沿用本 Goal 硬约束 |

---

## 5. 遗留项（推 Round 17 / v3.02 治理）

| 遗留项 | 等级 | 修复方向 |
|---|---|---|
| v3.01 数据 step/expected 错位（Round 15 §11.7 关键观察 2）| MINOR | v3.02 prompt 治理（FU-A4 · Round 15 §11.5）|
| SSOT 拆约束对象（LLM 生成 vs 数据存储）| MAJOR | v3.02 治理（FU-A2 · Round 15 §11.5）|
| `_sync_list_fields_after_merge` 补丁清理 | LOW | Round 17 验证 normalizer 修复后可移除（防御性兜底）|
| source_case_ids 在 xlsx 主表渲染 | LOW | Round 17 可扩展主表 +1 列展示 source TC id 列表 |

---

## 6. 影响范围

| 范围 | 影响 |
|---|---|
| **用户可见** | xlsx 主表 87 TC 按 OBJ 分组（5 色背景 + 空行隔离）；Sheet 2「用例描述索引」16 OBJ 全局视图；OBJ/FP/TC/Ready 数一目了然 |
| **下游消费** | 测试工程师打开 xlsx 即知"哪些 OBJ 有 TC / 各 OBJ 几个 TC / 哪些 FP 被覆盖"——无需再翻主表数行 |
| **SSOT** | SKILL.md + .mdc 双写 §11.1「测试设计层级原则」——未来 LLM 生成 TC 时按层级原则展开（OBJ→FP→前置条件→TC）|
| **代码** | normalizer 行为契约变更 + merger 加 1 字段 + formatter 加 4 helper 函数（opt-in）+ 主调调用入口 |
| **v3.01 JSON** | 未触碰（out_of_scope §10 继承）|
| **v3.01 xlsx** | 重导出（核心审查对象）；旧版备份为 `.round16.precheck.bak.xlsx`（20265 bytes）|

---

## 7. 反模式自检

- ❌ **未**"为通过检查改 SSOT"——SKILL.md §11.1 是真实业务需要（LLM 缺层级指引），不是为 PASS 而改
- ❌ **未**"只补最小闭环"——本次同时修了 normalizer（行为契约）+ merger（加字段）+ formatter（加 4 helper）+ SKILL.md + .mdc 5 个文件
- ❌ **未**"跳过 round audit"——本档 + audit_16.md + snapshot 全部落档
- ❌ **未**"虚构 Codex 内部行为"——所有判定基于实测数据（self_test + xlsx 物理验证 + pytest）
- ✅ **质量基线叠加校验**：4 项 BLOCKER + 2 项 MAJOR 全部 PASS，含至少 1 条反向挑战
- ✅ **out_of_scope 严守**：v3.01 test_cases.json 字节级不变（338192）；不改 auto_reviewer / S7 审查 / S5 / S2 / S3 / S4
- ✅ **不 commit**：所有改动保留在工作区，等用户审核后决策
