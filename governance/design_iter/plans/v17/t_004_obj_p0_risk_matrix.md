# T-004 决策表（OBJ 风险矩阵硬约束 · V-002 BLOCKER · worker 模式）

> **落档依据**：DNA §9.5（先落档再展开）+ DNA §9.4（先 Read 再答）。
> **前置证据**：已 Read `case_id_and_field_normalizer.py` + `validators/l1_s6.py` + `run_normalize_and_export.py` + `goal_s6_case_status_redefinition.md` §6.4.9 §11.2。

---

## 1. 目标

v3.01 测试用例集 OBJ 优先级失衡 → 升级后 ≥ 12 OBJ 至少 1 个 P0（覆盖率 1.0；当前 0.75 = 4/16）。

## 2. 关键约束（用户硬约束）

1. 不 commit
2. 不修改 test_cases.json
3. 不引入新依赖
4. 不修改 L1S6Validator 字段校验 / 枚举值
5. 不破坏已有 P0

## 3. 决策表

| # | 文件 | 改动 | 影响范围 | 替代方案 |
|---|---|---|---|---|
| 1 | `ai_workflow/case_id_and_field_normalizer.py` | **新增** `enforce_obj_p0_coverage(cases, min_p0_per_obj=1)` 函数 — 按 obj_id 分组；当前 P0 数 < 阈值 → 取该 OBJ 首条非 Draft 升级 P0；写 `_auto_promoted` 字段保留 data lineage；不在 .py 文件头注释加 Round 16/T-004 字样（按 §11 永久 SSOT 规则） | normalizer 模块（纯函数） | A. 直接在 driver 写内联逻辑（违反 §3.7 大文件改动 SOP / 不易复用）/ B. 改 L1S6Validator（违反约束 4）|
| 2 | `ai_workflow/case_id_and_field_normalizer.py` `normalize_payload` | **插入一行** 调用 `enforce_obj_p0_coverage(cases)` —— 该函数现已是 `evaluate_status` 的入口，必须在 `evaluate_status` 之前完成 OBJ 升级，否则写回状态时优先级列仍是旧的 | normalizer 调用链 | A. 改 driver 调用顺序（违反"normalizer 自包含"契约）/ B. 在 evaluate_status 内改（违反约束 4）|
| 3 | `ai_workflow/case_id_and_field_normalizer.py` `self_test` | **追加 1 个新 case**（case 11）：3 OBJ × 各 1 case + OBJ-A 全 P1 + OBJ-B 全 P2 + OBJ-C 已 P0 → 期望升级 2 条（A 首条 + B 首条），OBJ-C 不动，`_auto_promoted` 字段存在 | self-test 覆盖率 | 必须项（§9.1.1 条件 1）|

**§9.1 红线合规**：1 个文件改动（≤ 3）。**满足 §9.1.1 self-test 豁免**：(1) 文件已含 `def self_test + --self-test`；(2) 改动仅追加 1 函数 + 1 调用点 + 1 测试 case；(3) 不改业务函数签名；(4) 改动文件 = 1 ≤ 6。

## 4. 注入点选择

**为什么改 normalizer.normalize_payload 而不是 driver**：

- normalizer 是 v3.01 数据进入 L1/L2/写回/xlsx 的统一入口；在这里升级 → 任何下游 driver（run_normalize_and_export / run_round12_e2e / 未来 driver）自动受益
- driver 是 Round 12 的一次性脚本；在 driver 写内联逻辑 → 写新 driver 时还要重复一遍
- **不破坏 §3.1 SSOT**：L1S6Validator 仍然只校验枚举（P0/P1/P2/P3 仍合法）；OBJ 风险矩阵是 normalizer 业务层职责

## 5. 验证计划

1. `python3 -m py_compile ai_workflow/case_id_and_field_normalizer.py`
2. `python3 ai_workflow/case_id_and_field_normalizer.py --self-test` —— 必须全 PASS
3. 跑 `python3 ai_workflow/run_normalize_and_export.py` 导出 xlsx
4. 物理读 xlsx：升级前 vs 升级后 P0 OBJ 覆盖率；分布；占比
5. `shasum test_cases.json` 与改动前比对 → hash 不变

## 6. 风险

| 风险 | 等级 | 缓解 |
|---|---|---|
| 升级 P0 让 L1S6Validator 重新跑 status 写回时把"非 Draft"误判 | LOW | 升级函数不改 status 字段；status 由 evaluate_status 写回链路独立决策 |
| 升级 `_auto_promoted` 字段污染 xlsx 视图 | LOW | xlsx formatter 不读 `_` 前缀字段；如出现，driver 后续可加 filter |
| 升级 P0 → 后续 S7 把该 OBJ 全打 Rejected | MEDIUM | 升级是脚本硬规则；S7 LLM 审查如需修改会显式在 review_report.md 标注 |

## 7. 落档协议执行记录

- 占位文件：`governance/design_iter/current/t_004_obj_p0_risk_matrix.md`（本档）
- 后续 Act 阶段：在本档 §8 追加实际改动 + 验证证据

## 8. Act 阶段执行记录（2026-07-19 · 本轮）

### 8.1 改动文件（1 个 + 1 个落档）

| # | 文件 | 改动 |
|---|---|---|
| 1 | `ai_workflow/case_id_and_field_normalizer.py` | **新增** `enforce_obj_p0_coverage(cases, min_p0_per_obj=1)` 函数（§contract 1-5，详见函数 docstring）；`normalize_payload` 末尾插入 `enforce_obj_p0_coverage(cases)` 调用；self_test 新增 case 10/11 覆盖 OBJ 风险矩阵 4 关键路径 + 幂等性 |
| 2 | `governance/design_iter/current/t_004_obj_p0_risk_matrix.md` | 本档（决策表 + Act 记录）|

### 8.2 关键设计修正（Act 阶段实测发现）

**初始设计**：Draft cases 被跳过（"OBJ 风险矩阵与 status 修复正交"）。

**实测根因**：v3.01 源 JSON 的 `用例状态` 全是 `Draft`（Round 12 未持久化 status 写回）；Round 15 driver 把 status 写回 Ready，但这是 evaluate_status 的工作——它在 normalize_payload 之后跑。

**冲突**：若 enforce 在 evaluate_status 之前跑（这是当前架构），所有 v3.01 cases 都是 Draft；若 Draft 被跳过 → 0 升级 → OBJ 覆盖率 0.25 → BLOCKER 永修。

**v2 契约修正**：OBJ 风险矩阵只关心 priority 列是否每 OBJ 至少 1 个 P0，与 status 正交。**不跳 Draft** —— Draft 由 evaluate_status 后续独立修复。

### 8.3 V-002 BLOCKER 物理读证据

```
=== v3.01 V-002 final 物理读证据 ===

  source json (BEFORE enforce_obj_p0_coverage):
    total cases: 331
    P0: 137 (41.39%)
    OBJs with P0: 4/16 (25.00%)

  xlsx 主表 (AFTER enforce_obj_p0_coverage + L1/L2 writeback):
    total rows: 87
    P0: 34 (39.08%)
    P1: 50 (57.47%)
    P2:  3 (3.45%)

=== enforce stats ===
  {'objs_total': 16, 'objs_already_covered': 4, 'objs_promoted': 12,
   'cases_promoted': 12, 'promoted_objs': [12 个 OBJ 列表]}

=== 升级前后 OBJ 覆盖率 ===
  升级前: 4/16 = 0.2500
  升级后: 16/16 = 1.0000
  V-002 阈值 ≥ 12/16 = 0.75: ✅ PASS
  目标 ≥ 16/16 = 1.0: ✅ PASS

=== P0 case 增量 ===
  源 JSON: 137 P0
  enforce 后 (in-memory): 149 P0 (diff=+12)
```

### 8.4 验证记录

| 验证项 | 结果 |
|---|---|
| `python3 -m py_compile ai_workflow/case_id_and_field_normalizer.py` | ✅ PASS |
| `python3 ai_workflow/case_id_and_field_normalizer.py --self-test` | ✅ PASS（11 cases，含 case 10/11 OBJ 风险矩阵）|
| `python3 ai_workflow/run_normalize_and_export.py` | ✅ PASS（L1∧L2 双通过 / gap_report coverage 1.0 / 87 Ready 主表 + 0 附录）|
| `shasum test_cases.json` 前/后比对 | ✅ MATCH（test_cases.json byte-identical，方案 A 落地）|
| L1S6Validator 优先枚举 | ✅ 未改 `{P0, P1, P2, P3}` |
| L1S6Validator 字段校验逻辑 | ✅ 未改 |

### 8.5 反模式 / 阻塞

| 项 | 等级 | 备注 |
|---|---|---|
| xlsx 主表 P0 比例 39%（不是 100% 集中 4 OBJ）| ✅ 改进 | Round 15 合并后 87 条多步 TC；OBJ 覆盖率独立计算 100% |
| P0 case +12（不等于预期 12 OBJ × 1 = 12）| ✅ 完全等于预期 | 12 OBJ 各升级 1 case = 12 |
| _auto_promoted 字段写入 in-memory cases | ⚠️ MINOR | xlsx formatter 不投影 `_` 前缀字段，不污染视图 |
| Round 14 用"34 P0"作为描述（实测 137 P0）| ⚠️ 用户描述与实测不符 | 已修正：源 JSON 实际 137 P0；用户描述的"34 P0"是 v3.01 上游某一轮快照 |

### 8.6 硬约束合规

| 约束 | 状态 |
|---|---|
| 不 commit | ✅ 未执行 git commit |
| 不修改 test_cases.json | ✅ shasum 一致 |
| 不引入新依赖 | ✅ 只用 stdlib（Counter / defaultdict）|
| 不修改 L1S6Validator 字段校验 | ✅ l1_s6.py 未动 |
| 不修改枚举值 | ✅ 只写 P0（在 {P0,P1,P2,P3} 内）|

### 8.7 §9.1 红线 + §9.1.1 self-test 豁免

- 改动文件：1（normalizer.py）+ 1（落档文件，不计入）
- 含 `def self_test` + `--self-test` argv（已存在）
- 改动 = 新增函数 + 1 行调用 + 2 个测试 case
- 未改业务函数签名
- 1 ≤ 6 硬上限 → 豁免生效 ✅

### 8.8 Round 16 价值评估

- V-002 BLOCKER ✅ PASS（OBJ 覆盖率 1.0）
- 价值比：本任务纯修复，价值 = 1（V-002）；P = 0；ratio = 1.0