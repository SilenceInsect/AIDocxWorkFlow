# Round 1 Review — check_field_completion.py 字段溯源版改造

> **Round**: 1
> **Goal ID**: b5ae664f-62ea-4823-87eb-cfc6d6bc2f9c
> **时间**: 2026-07-18

---

## 1. 缺陷汇总

### 1.1 严重缺陷（必须修）

**D-R1-01: s6_report.py 缺口 — 治理档 vs 工程脱钩**

| 维度 | 描述 |
|---|---|
| 严重度 | HIGH |
| 表现 | v17 治理档 6 处引用 `ai_workflow/s6_report.py`，但工程中无该文件 |
| 影响 | T2 任务无法执行；下游若按 STAGE_S6_TEST_CASES.mdc line 576 引用 `generate_s6_report()` 会 NameError |
| 根因 | v17 PLAN.md §2.2 / §4 列入 s6_report.py 作为待改清单，但 v17 之前从未有人创建该文件 |
| 修复建议 | v17.2 治理档收敛时决定：(a) 删除 v17 治理档中所有 s6_report.py 引用 + 删除 STAGE_S6_TEST_CASES.mdc line 576 引用，或 (b) 真正创建该文件并实现 generate_s6_report() |
| 影响范围 | 5 个治理档 + 1 个 .mdc 规则文档 |

### 1.2 一般缺陷（建议修）

**D-R1-02: T1 改造期间新增 MUST 字段 → 旧 S5/S6 产物 CI 必失败**

| 维度 | 描述 |
|---|---|
| 严重度 | MEDIUM |
| 表现 | check_field_completion.py 现在检查 obj_name/fp_name MUST，旧产物（v17 之前的）会判不合格 |
| 影响 | CI 流水线需先升级产物到字段溯源版（v17 治理档 v3.01 已完成 87 TP/87 TC 字段补齐）|
| 根因 | 字段溯源版是收紧型升级，符合预期行为 |
| 修复建议 | 在 v17.1 闭环报告 + CHANGELOG.md 中明确"CI 升级到字段溯源版产物为前置条件" |
| 影响范围 | 所有 S5/S6 产物生成流水线 |

### 1.3 优化项

**D-R1-03: check_field_completion.py S5_LITE_REF_FIELDS 顺序可读性**

| 维度 | 描述 |
|---|---|
| 严重度 | LOW |
| 表现 | S5_LITE_REF_FIELDS 顺序按"历史顺序 + 新增字段" |
| 修复建议 | 可按"必填链路顺序"重新排列：s4_reference → obj_id → obj_name → feature_point_ref → fp_name |
| 优先级 | LOW（不影响行为）|

---

## 2. 根因定位

### 2.1 机制问题

**M-01: v17 治理档 "必改清单" 缺乏 "文件存在性校验" 环节**

- v17 PLAN.md §2.2 把 s6_report.py 列入"必改清单"
- 但 v17 治理流程（GOAL.md / CONVERGENCE_VERDICT.md）只校验"代码文件改完"——未校验"清单中文件是否存在"
- 修复方向：CONVERGENCE_VERDICT.md 增加"必改清单 vs `ls` 双向校验"步骤

**M-02: Goal-loop Task 描述层面 "T1+T2" 是平级，但 T2 是不可执行的（文件不存在）**

- Goal-loop §6 "不可逆或破坏性操作" 应扩展到 "依赖文件存在性"
- 修复方向：snapshot.json task_queue 应预校验 `artifact` 字段对应的文件存在

### 2.2 规范问题

**S-01: v17.1 任务描述（T1 = "移除 v2 锚点报告"）基于错误前提**

- 任务描述假设 s6_report.py 存在
- 实际：从未存在 → 任务不可执行
- 修复方向：v17.2 任务起草前必须先 `ls` + `git ls-files` 双向校验

### 2.3 习惯问题

**H-01: Agent 在新需求清单上倾向"按列表逐项执行"，未优先执行存在性预检**

- v17 治理档 6 处引用 → Agent 直接接受 → 把 T2 当成正常任务分配
- 修复方向：Agent 应在 Round 1 起始前，对所有目标文件做"先验后答"（DNA §9.4 已强制要求，本轮已按此执行，发现 T2 缺口）

---

## 3. 可落地修复方案

### 3.1 Round 1 后续（已完成）

- ✅ T1 完成 — check_field_completion.py 字段溯源版改造通过
- ✅ T2 缺口识别 — 不造新文件，标记 cancelled + 在 deliverables 落档

### 3.2 Round 2 待办

| ID | 内容 | 影响范围 |
|---|---|---|
| T3 | INDEX 标 v17 = current | INDEX.md + INDEX.json |
| T4 | CHANGELOG 追加 v17 闭环条目 | CHANGELOG.md |

### 3.3 Round 3 待办

- Hook self-test 跑通
- §11 grep 全项目扫描
- py_compile 全工程扫描

### 3.4 v17.2 治理档收敛建议（不在 v17.1 范围）

| 议题 | 建议 |
|---|---|
| s6_report.py 缺口处置 | 用户拍板：(a) 删除引用 vs (b) 真正实现 |
| v17 治理流程增加文件存在性校验 | 列入 v17.2 |
| 字段溯源版 CI 升级声明 | CHANGELOG.md 加 "v17.1 CI 前置" 备注 |

---

## 4. 落档协议

- 本档已落档
- 修改文件数：1（本档）+ 1（audit_1.md）+ 1（snapshot.json 更新）= 3 ≤ §9.1 红线
- 单次响应工具调用 ≤ 10
- §11 违规：0 处（check_field_completion.py 已 grep 验证）
