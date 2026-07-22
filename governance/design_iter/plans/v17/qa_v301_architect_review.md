# v3.01 test_cases_public.xlsx 架构师视角审查报告

> **Author**: 架构师（worker）
> **Target**: `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` + `test_cases.json`
> **Inputs**: 资深测试审查 `qa_v301_tester_review.md`（已 Read）
> **Scope**: 上下游契约 / 字段映射 / 数据契约 / 模块接口一致性
> **Review Date**: 2026-07-19
> **Out_of_scope**: 见 `.goal-log-db/active/32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3/out_of_scope.md`

---

## 0. 概要

| 维度 | 评级 | 关键问题数 |
|---|---|---|
| S1 → S1.5 → S2 链路完整性 | A | 1 |
| S2 → S5 字段映射一致性 | B | 3 |
| S5 → S6 字段映射一致性 | **D** | 6 |
| v3.01 vs v3.0 改动点可追溯性 | C | 2 |
| 数据契约（JSON ↔ xlsx） | **D** | 5 |
| 模块枚举一致性（SSOT 8 模块） | B | 3 |
| TC ↔ TP ↔ FP ↔ OBJ 引用闭环 | A | 1 |

**总计**：21 条架构师判定问题（5 P0 / 9 P1 / 7 P2）

---

## 1. S1 → S1.5 → S2 → S5 → S6 链路完整性

### A-001 [P1] S1 评审产物与 S2 OBJ 命名漂移

- **现状**：`S1/requirement_objects.json` 中 OBJ 命名（早期产物）与 S2 `backlog.json` 实际 stories 不对齐
- **证据**：
  - `workflow_assets/游戏道具商城系统/v3.01/「S1 需求评审」/requirement_objects.json` 顶层 `objects: []`（空数组）——S1 阶段未实质拆分 OBJ
  - 但 S2 `backlog.json` 有 6 Epic / 15 Story，OBJ 命名（如 `UI-ITEM-MALL-01-001-OBJ-01`）完全由 S2 派生
- **影响**：S1 → S2 的 OBJ 命名契约断裂——追溯 OBJ 来源时无法回溯到 S1
- **修复方向**：要么 S1 必须产生 OBJ 拆分，要么在 S2 backlog 中加 `s1_origin_story_id` 字段链接 S1 评估对象

### A-002 [P2] S5 TP 与 S4 异常树叶子标识符不一致

- **现状**：S4 `business_flow.md` 中异常树叶子用 `S4-{Epic}-X.Y.Z` 格式（如 `S4-UI-ITEM-MALL-01-1.1.1`）
- **但** S5 TP 的 `s4_reference` 字段同时含 `S4-{Epic}-X.Y.Z` 与 `ET-001-DBFail` 自定义标识
- **证据**：
  - S5 TP 样例 `s4_reference`: `S4-BIZ-PURCHASE-01-1.2.2`, `ET-001-DBFail`, `S4-BIZ-VIP-01-1.1.1`, `S4-BIZ-PROMO-01-1.4.1`, `S4-UI-ITEM-MALL-01-1.1.2`
  - `ET-001-DBFail` 不在 S4 异常树中（自定义），S4 business_flow.md 中无 `ET-NNN` 节点定义
- **影响**：S4 异常树 → S5 TP 的引用不可枚举（无法计算异常路径覆盖率）
- **修复方向**：S5 引用统一为 `S4-{Epic}-X.Y.Z` 格式；`ET-NNN` 自定义标识必须先在 S4 注册

---

## 2. S5 → S6 字段映射一致性

### A-003 [P0 BLOCKER] S5 TP 的 `s5_ref` 命名空间在 S6 TC 中出现两种格式

- **现状**：S5 TP 顶层字段同时有 `s5_ref` 和 `tp_id`，两者值不同（`s5_ref = "TP-001"`，`tp_id = "UI-TP-001"`）
- **证据**：S5 `test_points.json` 第一个 TP：`s5_ref: "TP-001"` + `tp_id: "UI-TP-001"`（双标识）
- **影响**：S6 TC 引用 S5 时，到底该用 `s5_ref`（`TP-001`）还是 `tp_id`（`UI-TP-001`）？当前 S6 TC 同时引用两者——**字段语义重叠**
- **修复方向**：SSOT 收敛为一个字段（建议保留 `tp_id` 含模块前缀）

### A-004 [P0 BLOCKER] S6 TC 的 `case_id` 与 `tc_id` 完全冗余

- **现状**：331 TC 的 `case_id` 和 `tc_id` 字段值完全相同（`"TC-001"` ~ `"TC-331"`）
- **证据**：test_cases.json 抽样 `case_id == tc_id` 100%
- **影响**：
  - 字段冗余 = 数据治理负担（两个字段必须同步更新）
  - 与 xlsx 端 `用例ID = "UI-TC-001"`（带模块前缀）冲突——三方命名空间不一致
- **修复方向**：
  - 方案 1：删除 `tc_id` 字段（保留 `case_id`）
  - 方案 2：将 `case_id` 改为模块前缀（`UI-TC-001`），与 xlsx 一致

### A-005 [P1] S5 TP 的 `test_point_type` 在 S6 字段映射中语义弱化

- **现状**：S5 TP 的 `test_point_type` 字段含 `POSITIVE` / `NEGATIVE` / `BOUNDARY` / `EXCEPTION` 等枚举
- **但** S6 TC 仅有 `case_type` 字段（功能/异常/边界 3 类）——S5 的 6+ 种枚举被压缩到 3 类
- **证据**：S5 test_points.json 样例 `test_point_type: "POSITIVE"`, `test_type: "POSITIVE"`（双字段）
- **影响**：S5 → S6 枚举降级 → 业务审计损失（如 OA_*、EP_VALID/INVALID 等）
- **修复方向**：S6 TC 增加 `test_point_type` 字段镜像 S5 TP（SSOT L138 已要求"test_method" 字段可选）

### A-006 [P1] S6 TC 的 `test_method` 字段被映射为 `test_methods`（数组）但与 SSOT 不一致

- **现状**：S6 TC 用 `test_methods: ["正向流程"]` 数组形式，SSOT L536-540 期望 `test_method` 字符串
- **证据**：test_cases.json 抽样：`test_methods: ["正向流程"]`（数组，1 元素）
- **影响**：normalizer 字段别名映射需多走一步
- **修复方向**：normalizer 兼容两种格式（数组 → 单元素字符串）或统一为数组

### A-007 [P1] S5 TP 的 `applies_rule` 字段未传递到 S6 TC

- **现状**：S5 TP 含 `applies_rule`（如 `"S5 §1.2 UI module; POSITIVE flow; S4 §1.3 exception tree"`），描述 TP 的"规则锚点"
- **但** S6 TC 无对应字段——`applies_rule` 在 S5→S6 阶段丢失
- **影响**：S7 审查时无法回溯 TC 适用规则（"为什么这条 TC 是 P0 / 为什么这条 TC 属于 BIZ 模块"）
- **修复方向**：S6 normalizer 镜像 `applies_rule` 到 TC 的"备注"字段

### A-008 [P2] S6 TC `case_id` 命名空间违反 SSOT L136

- **现状**：SSOT `STAGE_S6_TEST_CASES.mdc` L136 规定 `case_id = "{Module}-TC-{NNN}"`
- **但** 331 TC 的 `case_id` 都是 `TC-NNN` 无前缀
- **影响**：normalizer 必须每轮注入前缀（参见 `case_id_and_field_normalizer.py`）——**额外治理负担**
- **修复方向**：从源头（s6_generate.py）输出正确格式，避免 normalizer 补丁式修复

---

## 3. v3.01 vs v3.0 改动点可追溯性

### A-009 [P1] v3.01 changelog 未结构化

- **现状**：v3.01 S2 backlog 中无 `changelog` 字段，无法定位"v3.01 相对 v3.0 改了哪些 OBJ"
- **证据**：`backlog.json` 顶层无 `changelog` 字段；各 OBJ 无 `version_history`
- **影响**：v3.0 → v3.01 增量变更不可追溯——下游（TP/TC）无法基于 changelog 增量生成
- **修复方向**：backlog.json 顶层加 `changelog: { from: "v3.0", added: [...], modified: [...], removed: [...] }`

### A-010 [P2] S5 TP 与 S4 业务流的发布版本不一致

- **现状**：S4 `business_flow.md` 标头 `Version: v3.01`；S5 `test_points.json` `meta.version: "v3.01"`
- **但** S5 `test_points.json.bak`（66878 bytes，备份）可能对应 v3.0——未确认
- **影响**：备份文件是否还有参考价值？
- **修复方向**：明确备份版本号；归档到 `archive/v3.0/` 子目录

---

## 4. 数据契约（JSON ↔ xlsx）

### A-011 [P0 BLOCKER] JSON `用例状态` 100% Draft，但 xlsx 100% Ready

- **现状**：
  - test_cases.json: 331 TC 全部 `用例状态: "Draft"`
  - test_cases_public.xlsx: 331 TC 全部 `用例状态: "Ready"`
- **证据**：`test_cases.json` `用例状态: 'Draft': 331`；xlsx `col9 = 'Ready': 331`
- **影响**：
  - JSON 是源数据，xlsx 是衍生品——**两端状态字段不一致**说明导出链路有 bug
  - Draft-Rejected 附录 Sheet 为空（max_row=1）——**与"双 Sheet 分流"的 SSOT 承诺完全脱节**
- **修复方向**：
  - 选项 A：xlsx 是错的，JSON 是对的 → xlsx 重导
  - 选项 B：JSON 是过时的，xlsx 是当前态 → JSON 应更新为 Ready（但需 normalizer 写回）

### A-012 [P0 BLOCKER] xlsx 操作步骤列 100% 是 Python dict repr 字符串

- **现状**：xlsx 第 6 列（操作步骤）值形如 `"{'step_num': 1, 'action': '玩家点击商城入口'}"`
- **根因**：`test_case_formatter.py` L828-830 `_get_field` 对 list 元素直接 `str(v)`，dict 被 str() 为 repr
- **影响**：
  - Excel 不可读
  - 人工审查时拿到 dict 字符串无法执行
  - QA 跑用例时无法解析步骤
- **修复方向**：`test_case_formatter.py` 改为 `f"{v.get('step_num', i+1)}. {v.get('action', '')}"` 格式化

### A-013 [P0 BLOCKER] JSON `用例状态` 字段名与 xlsx 表头不一致

- **现状**：
  - JSON 字段名 = `"用例状态"`
  - xlsx 表头 = `"用例状态"`
  - **但**：normalizer 字段别名表要求 `"用例状态" → "case_status" / "status"` 兼容（SSOT L170）
- **影响**：别名映射正常但容易混淆——需文档明确"哪个是源哪个是别名"
- **修复方向**：SSOT 文档加 "canonical = 中文用例状态；alias = case_status / status" 章节

### A-014 [P1] xlsx 用例ID 命名空间与 JSON `case_id` 不一致

- **现状**：
  - xlsx `用例ID` = `UI-TC-001`（带模块前缀，331 个全有前缀）
  - JSON `case_id` = `TC-001`（无前缀）
- **影响**：
  - 人工 cross-check 时找不到对应行
  - 自动化消费方不知该信任哪一端
- **修复方向**：以 SSOT L136 为准（带前缀）——normalizer 写回时统一

### A-015 [P2] xlsx `用例状态` 列值未被 case_status_writer 自动写回（Round 12 修复后状态丢失）

- **现状**：Round 12 已实现 `case_status_writer.apply_l1_l2_status` 写回 Ready，但 xlsx 中所有 331 TC 都是 Ready 而 JSON 都是 Draft——说明 case_status_writer **只写了 xlsx，没同步回 JSON**
- **影响**：JSON 与 xlsx 长期处于"状态不一致"状态
- **修复方向**：case_status_writer 加 `write_to_json=True` 选项，或在写 xlsx 前先 patch JSON

---

## 5. 模块枚举一致性（SSOT 8 模块）

### A-016 [P1] S6 TC `module` 字段未严格收敛到 8 模块 SSOT

- **现状**：SSOT L137 规定 8 模块：`UI / BIZ / CONFIG / AUX / LINK / SPECIAL / LOG / HINT`
- **但** S6 TC `module` 分布：`UI: 66, BIZ: 249, LOG: 4, SPECIAL: 12`（仅 4 种模块，缺 `CONFIG / AUX / LINK / HINT`）
- **影响**：是否 v3.01 项目确实只有 4 模块（不需要 8 模块）？若否，模块覆盖不全
- **修复方向**：业务侧确认模块清单；如需 8 模块则 S5/S6 应补 TP/TC

### A-017 [P2] `SPECIAL` 模块定义模糊

- **现状**：SSOT L137 列出 `SPECIAL`（4 个 TC：风控/支付幂等），但未明确 SPECIAL 的判定标准
- **影响**：什么场景归 SPECIAL 模糊——例如"VIP专属可见"被归 BIZ，但"VIP专属防穿透"应该归 SPECIAL 还是 BIZ？
- **修复方向**：MODULES.md 补 SPECIAL 判定规则

### A-018 [P2] `LOG` 模块仅 1 TP / 1-2 TC —— 结构性欠测（与资深测试 Q-019 一致）

- **现状**：SSOT 8 模块 LOG 仅 1 个 TP（邮件通知）+ 1-2 TC
- **影响**：业务上"订单日志 / 风控日志 / 审计日志 / 玩家操作日志" 全部未覆盖
- **修复方向**：与资深测试 Q-019 合并处理

---

## 6. TC ↔ TP ↔ FP ↔ OBJ 引用闭环

### A-019 [P1] tc_tp_gap_report.md 严重陈旧

- **现状**：报告写"87 TP / 87 TC / 100% 覆盖"，实际是 **87 TP / 331 TC**
- **证据**：`tc_tp_gap_report.md` L4-7 `Total TCs in S6: 87`（错误），实际 331
- **影响**：
  - 人工依赖 gap_report 决策会误判覆盖
  - Round 12 拆解 87→331 后未重生成报告
- **修复方向**：重生成 gap_report；或脚本自动化（每次 S6 完成自动跑）

### A-020 [P2] `feature_point_ref` 与 `fp_name` 字段冗余

- **现状**：S6 TC 同时存 `feature_point_ref`（结构化 ID）和 `fp_name`（人类可读名）
- **影响**：字段冗余——`fp_name` 可由 `feature_point_ref` 查 S2 派生
- **修复方向**：删除 `fp_name` 字段（或保留为 cache 但明确"派生字段，可重算"）

### A-021 [P2] OBJ ↔ Story 映射靠约定（无显式字段）

- **现状**：OBJ ID 命名约定 `{Module}-{Epic}-{Story}-{OBJ-N}`，但 OBJ 在 S2 中无独立字段——OBJ ID 是从 story_id + 后缀拼接推断的
- **影响**：OBJ 反查 story_id 需字符串解析
- **修复方向**：S2 requirement_objects.json 顶层加 `objects: [{id, story_id, title, feature_points: [...]}]` 显式字段

---

## 7. 架构师总评

### 7.1 关键 P0 问题（影响交付）

| ID | 一句话 | 修复 owner |
|---|---|---|
| A-003 | S5 双标识 `s5_ref` vs `tp_id` 语义重叠 | 架构师（SSOT 收敛） |
| A-004 | S6 `case_id` / `tc_id` 完全冗余 + 命名违反 SSOT | normalizer 修 |
| A-011 | JSON Draft / xlsx Ready 状态不一致 | case_status_writer |
| A-012 | xlsx 操作步骤列 dict repr 字符串 | test_case_formatter 修 |
| A-014 | xlsx `UI-TC-NNN` vs JSON `TC-NNN` 命名不一致 | normalizer 统一 |

### 7.2 架构师判定结论

- **数据契约层（JSON ↔ xlsx）严重失配**：5 条 P0 中有 4 条集中在数据契约
- **字段映射层（SSOT）有 6 处不一致**：枚举降级、字段冗余、命名空间冲突
- **链路完整性（A-001/A-002）尚可**：S1→S2 的 OBJ 命名约定隐式但可追溯
- **总评**：v3.01 在"覆盖率"指标上漂亮（OBJ 100%、FP 100%、TP 100%），但"数据契约"层是纸牌屋——任何下游消费方拿到 JSON 或 xlsx 都会发现不一致

### 7.3 架构师移交清单

1. **SSOT 收敛**：建议在 `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` 明确 `tp_id` 是唯一标识，删除 `s5_ref` 字段
2. **`test_case_formatter.py` L828-830 修复**：dict 元素格式化（与资深测试 Q-007 同源）
3. **case_status_writer 扩展**：加 JSON 同步写回选项
4. **`tc_tp_gap_report.md` 重生成脚本**：每次 S6 完成自动跑
5. **JSON ↔ xlsx 命名统一**：以 `UI-TC-NNN` 为准
6. **field_completion 脚本加测试**：mock 31 条重复用例 + 12 条 BOUNDARY TC 验证

---

## 8. 落档协议执行记录

- **本文件路径**：`governance/design_iter/current/qa_v301_architect_review.md`
- **DNA §9.5**：✓（Write 占位后再展开 content）
- **DNA §9.4**：✓（已 Read qa_v301_tester_review.md + 6 份 v3.01 JSON/MD 后回答）
- **改动文件清单**：1 个（`qa_v301_architect_review.md`）——DNA §9.1 不触发

---

> **下一阶段**：交付资深产品审查 → 汇总三方清单 → Round 2 Act 修复