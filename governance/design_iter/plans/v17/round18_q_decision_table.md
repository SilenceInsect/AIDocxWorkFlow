# Round 18 q_decision_table.md — FU-2 + FU-4 + FU-5 pipeline 集成 + L1 --auto + open_questions 归档

> **性质**：DNA §9.5 落档协议（先落档再展开）
> **Goal**: 32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3（GL-009 · v3.01 test case 审查治理）
> **Round**: Round 18（loop_round=8）
> **决策人**：架构师 worker（按 user 委托全权决策）
> **决策时间**：2026-07-19
> **来源**：snapshot.json Round 17 延后 3 项 follow_up（FU-2/4/5）— 本轮全清
> **GL-009 语义校验**：Round 18 follow_up 自迭代走 §3.2 合法目标变更路径（用户层面已确认："GL-009 语义校验已在用户层面确认为'当前 goal follow_up 自迭代'"）

---

## §0 元信息（强制）

| 维度 | 值 |
|---|---|
| `goal_id` | `32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3` |
| `round` | 8 |
| `loop_round` | 8 |
| `created_at` | 2026-07-19 |
| `author` | 架构师 worker |
| `severity_label` | MINOR（FU-2/4/5 三项 MINOR） |
| `follow_up_items_count` | 3（Round 17 延后 FU-2/4/5）→ 本轮清 3 → 0 延后 |
| `out_of_scope.guard` | v3.01 JSON 字节不变（338192）/ v3.01 xlsx 字节不变（41572）/ v3.02 全套不变（400677/73188/25158） |
| `latest_artifact` | `ai_workflow/l1_format_validator.py`（--auto argv + C23/C24；改动最大） |
| **本轮决策** | **FU-2 + FU-4 + FU-5 全清** · 业务文件改动 = 3（stage_gatekeeper + coverage_validator + l1_format_validator，均走 §9.1.1 自洽豁免） |

---

## §1 决策表

### §1.1 整体策略：FU-2 + FU-4 + FU-5 三联（pipeline 集成 + argv + open_questions 归档）

| 维度 | 决策 |
|---|---|
| **背景** | Round 17 延后 3 项 follow_up，全 MINOR；FU-2（pipeline 集成 assertion 校验）+ FU-4（l1 `--auto` argv）强相关（同 pipeline）；FU-5（open_questions 归档）弱相关（治理档），并列处理 |
| **策略** | 3 项同时清：FU-2 + FU-4 合并 pipeline 接入块；FU-5 单独立项归档 |
| **业务文件改动** | 3（stage_gatekeeper.py + coverage_validator.py + l1_format_validator.py）—— §9.1 红线 ✅（≤ 3） |
| **§9.1.1 豁免** | 3 文件都是「加 self_test 函数 + --self-test argv 分支 + 不动业务函数签名」结构，自然满足 §9.1.1 全部 4 条件（详见 §3） |
| **替代方案** | B. 拆 Round 19/20/21（每轮 1 项）—— **拒绝**：3 项都是 MINOR 且彼此低耦合可并；分轮纯属浪费轮次 |
| **当前决策** | **采用 A**（3 项同时清，预期 Round 18 后 status=achieved） |

### §1.2 FU-2 [MINOR] pipeline 集成 assertion 校验

| 维度 | 决策 |
|---|---|
| **目标** | stage_gatekeeper / coverage_validator 集成 F-E/F-F assertion 校验；S6 postflight 调用 `check_assertion_completeness` + 统计输出 |
| **改动文件 1** | `ai_workflow/stage_gatekeeper.py`：S6 postflight gate 段加 assertion 校验调用（不动原有 `run_postflight_gate` / `run_runtime_consistency_gate` / `run_preflight_gate` / `write_read_ack` 签名） |
| **改动文件 2** | `ai_workflow/coverage_validator.py`：加 `compute_assertion_gap_report(test_cases)` 辅助函数 + 在 `_finalize_ledger` 输出里挂入 `assertion_stats`（不动原有 9 个公开函数签名） |
| **L1 self-test 增量** | C23：测试 `compute_assertion_gap_report` 在 fixture 上的输出 (`total_tcs=3 / with_assertion=2 / without_assertion=1 / types_distribution={...}`) |
| **影响范围** | S6 postflight 调用方 + 任何依赖 coverage ledger 的下游（coverage_ledger.json 增量挂字段，向后兼容） |
| **替代方案** | B. 只加纯函数不动 stage_gatekeeper（仅算半截；FU-2 不完整）/ C. 改 readiness_gate 名字（变动大）|
| **当前决策** | **采用 A**（stage_gatekeeper + coverage_validator 双改） |

### §1.3 FU-4 [MINOR] l1 `--auto` argv + L1 self-test C24

| 维度 | 决策 |
|---|---|
| **目标** | l1_format_validator.py CLI 加 `--auto <json_path>` argv：批量对生产产物跑 `check_assertion_completeness` + `check_no_fp_name_field(mode="error")` 并打印违规 |
| **新增 argv** | `--auto <json_path> [<json_path>...]`：每个 path 读 JSON → 取 test_cases 数组 → 跑断言 + fp_name 校验 → 打印 `path: N violations` + 列表 |
| **L1 self-test 增量** | C24：测试 `--auto` argv 在 fixture 上的输出（fixture: 3 TC 含 fp_name + 缺 assertion）→ 期望 `2 violations (1 DEPRECATED_FP_NAME + 1 MISSING_ASSERTION)` |
| **改动文件** | 仅 `ai_workflow/l1_format_validator.py`（main() 函数 + argparse + self_test() 函数） |
| **影响范围** | CLI 调用方（手动跑生产产物校验）；不影响 import 调用方 |
| **替代方案** | B. 独立写一个 CLI 脚本（重复 argparse 逻辑）—— **拒绝**（违反 DRY） |
| **当前决策** | **采用 A**（l1_format_validator 内嵌 argv） |

### §1.4 FU-5 [MINOR] open_questions 归档

| 维度 | 决策 |
|---|---|
| **目标** | 按"已解 / 未解 / 无主"分类 `governance/design_iter/plans/v17/open_questions.md`（共 7 个 Q-V17-001~007）；已解归档到 `governance/open_questions_archive_v17.md` |
| **分类依据** | Q-V17-001~007：在 round17_q_decision_table.md / audit_17.md / review_17.md 等 R17 档中均有对应决策落档 → **已解**（默认值已采纳） |
| **新建档** | `governance/open_questions_archive_v17.md` —— 留存 Q-V17-001~007 全文 + 标注"已解（R17）" |
| **原档保留** | `governance/design_iter/plans/v17/open_questions.md` 保留 active 内容（7 Q 都已解则原档可清空 + 加 "待归档" 标记指向 archive_v17）；这里**不动**原档，仅在档首加 `> 状态: 本档全部已解，详见 ../open_questions_archive_v17.md` |
| **改动文件** | `governance/open_questions_archive_v17.md`（新建）+ 编辑原档头部 |
| **影响范围** | 治理档（governance/）；不入 git 业务路径 |
| **替代方案** | B. 全文复制到 archive 然后删原档（动 v17 目录结构；本轮最小化为"加档首标注 + 建 archive_v17"）|
| **当前决策** | **采用 A**（新建 archive_v17 + 原档头部标注） |

### §1.5 历史 Q 处理说明

| Round | 已 Q-V17 范围 | 备注 |
|---|---|---|
| R14~R16 治理 | 各 round_q_decision_table.md / audit_*.md / review_*.md 自带"已解 / 延后"状态 | 本轮不重复归档（已在各 round 档中明示） |
| Round 17 治理 Q | Q-V17-001~007 全在本档 `governance/design_iter/plans/v17/open_questions.md` | **本轮专项归档**（FU-5 目标） |

**§1.5 决策**：仅归档 Q-V17-001~007；R14~R16 的 Q 视为已就地解决（不在 open_questions 主档列表）。

---

## §2 Read 清单（§9.4 先验后答约束）

### 本响应内 Read 的文件清单（≥ 11 项）

| # | 文件 | 行数 | 用途 |
|---|---|---|---|
| 1 | `.goal-log-db/active/32a8ff45-.../snapshot.json` | 423 | follow_up_items + Round 17 状态 |
| 2 | `ai_workflow/stage_gatekeeper.py` | 213 | FU-2 改造目标 + 已确认无 self_test（需新增） |
| 3 | `ai_workflow/coverage_validator.py` | 380 | FU-2 改造目标 + 已确认无 self_test（需新增） |
| 4 | `ai_workflow/l1_format_validator.py` | 888 | FU-2/FU-4 改造目标 + 已有 self_test（22 cases）需扩 24 + 需加 --auto |
| 5 | `ai_workflow/test_case_formatter.py` | 1665 | `_partition_cases_for_xlsx` 行为确认 + 主表 1 行原因（R17 决策档 §5.4 已说明） |
| 6 | `governance/design_iter/plans/v17/open_questions.md` | 142 | FU-5 归档源（Q-V17-001~007） |
| 7 | `governance/design_iter/current/round17_q_decision_table.md` | 259 | 学习模板 + 拆分策略 |
| 8 | `.goal-log-db/active/32a8ff45-.../audit_17.md` | 100+ (部分) | Round 17 审计决策依据 |
| 9 | (隐式) `.cursor/rules/DNA_3Q_CHECK.mdc` | §9.1 / §9.1.1 / §9.4 / §9.5 | |
| 10 | (隐式) `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | §4.3 阈值常量 + §0.1 Git 分类 | |
| 11 | (隐式) `AGENTS.md` | 4 准则 + Git 分类铁律 | |

**判定**：✅ §9.4 先验后答约束满足（11 个文件 Read 完毕）

---

## §3 §9.1.1 豁免检查（红线条文）

### §3.1 §9.1 红线（≤ 3 业务文件改动）

| 文件 | 类型 | 是否计入 §9.1 | 说明 |
|---|---|---|---|
| `ai_workflow/stage_gatekeeper.py` | 业务文件（入 git） | ✅ **计入** | FU-2 |
| `ai_workflow/coverage_validator.py` | 业务文件（入 git） | ✅ **计入** | FU-2 |
| `ai_workflow/l1_format_validator.py` | 业务文件（入 git） | ✅ **计入** | FU-2 + FU-4 |
| `governance/open_questions_archive_v17.md` | 治理档（新建） | ❌ 不计入（过程资产） | FU-5 |
| `governance/design_iter/plans/v17/open_questions.md` | 治理档（编辑头部） | ❌ 不计入（过程资产） | FU-5 |
| `governance/design_iter/current/round18_q_decision_table.md` | 决策档（新建） | ❌ 不计入（§9.5） | 本档 |
| `.goal-log-db/active/.../audit_18.md` | goal-loop 过程资产 | ❌ 不计入（§9.1.2） | |
| `.goal-log-db/active/.../review_18.md` | goal-loop 过程资产 | ❌ 不计入（§9.1.2） | |
| `.goal-log-db/active/.../snapshot.json` | goal-loop 状态 | ❌ 不计入（§9.1.2） | |
| **业务文件小计** | | **3** | **≤ 3 ✅（正好红线内）** |

### §3.2 §9.1.1 豁免条件（每文件逐条验证）

| 条件 | stage_gatekeeper.py | coverage_validator.py | l1_format_validator.py |
|---|---|---|---|
| 1. 含 `def self_test() → int` | ✅ 加 | ✅ 加 | ✅ 已含（扩展到 24） |
| 2. 含 `--self-test` argv 分支 | ✅ 加 | ✅ 加 | ✅ 已含 |
| 3. 不动业务函数签名 | ✅（仅加 import + 1 段校验调用 + self_test） | ✅（仅加辅助函数 + _finalize_ledger 挂字段 + self_test） | ✅（仅加 main() 新 argv + self_test 增 C23/C24） |
| 4. 改动文件 ≤ 6（绝对硬上限） | ✅ 1 文件 | ✅ 1 文件 | ✅ 1 文件（未超 6） |

**判定**：✅ **§9.1.1 豁免条件 全部满足**——3 文件均符合「加 self_test 函数 + --self-test argv + 不动业务签名」自洽豁免模式。本轮**不需要** 走 §9.4「先验后答」之外的额外豁免路径。

### §3.3 治理档落档清单（§9.5）

| # | 文件 | 路径 | 状态 |
|---|---|---|---|
| 1 | round18_q_decision_table.md（本档） | `governance/design_iter/current/` | ✅ W7 |
| 2 | audit_18.md | `.goal-log-db/active/32a8ff45-.../` | ⏳ W8 |
| 3 | review_18.md | `.goal-log-db/active/32a8ff45-.../` | ⏳ W9 |
| 4 | snapshot.json（atomic write） | `.goal-log-db/active/32a8ff45-.../` | ⏳ W10 |

---

## §4 改动清单（计划 · W1-W10）

| # | 文件 | 类型 | 状态 |
|---|---|---|---|
| 1 | `ai_workflow/stage_gatekeeper.py` | 改（加 self_test + --self-test + S6 gate 调用 assertion 校验） | ⏳ W2-W3 |
| 2 | `ai_workflow/coverage_validator.py` | 改（加 compute_assertion_gap_report + _finalize_ledger 挂字段 + self_test） | ⏳ W2-W3 |
| 3 | `ai_workflow/l1_format_validator.py` | 改（加 --auto argv + self_test 增 C23/C24） | ⏳ W4-W5 |
| 4 | `governance/open_questions_archive_v17.md` | 新建 | ⏳ W6 |
| 5 | `governance/design_iter/plans/v17/open_questions.md` | 编辑（档首加 "已解" 标注） | ⏳ W6 |
| 6 | `governance/design_iter/current/round18_q_decision_table.md` | 新建 | ✅ W7 |
| 7 | `.goal-log-db/active/32a8ff45-.../audit_18.md` | 新建 | ⏳ W8 |
| 8 | `.goal-log-db/active/32a8ff45-.../review_18.md` | 新建 | ⏳ W9 |
| 9 | `.goal-log-db/active/32a8ff45-.../snapshot.json` | 修改（loop_round=8 / status=achieved / follow_up_count=0） | ⏳ W10 |

**v3.01 byte-lock 守住**：JSON 338192 bytes / xlsx 41572 bytes（不变）
**v3.02 byte-lock 守住**：JSON 400677 bytes / md 73188 / xlsx 25158 bytes（不变）

---

## §5 验证证据（计划）

### §5.1 self-test 24 cases（22 + C23 + C24）

```
$ python3 ai_workflow/l1_format_validator.py --self-test 2>&1 | tail -5
[预期] 24 cases passed（C23 + C24 PASS）
```

### §5.2 --auto argv（v3.02 / v3.01 验证）

```
$ python3 ai_workflow/l1_format_validator.py --auto workflow_assets/.../v3.02/.../test_cases.json
[预期] 0 violations（v3.02 已应用 F-E/F-F SSOT）

$ python3 ai_workflow/l1_format_validator.py --auto workflow_assets/.../v3.01/.../test_cases.json
[预期] 331 violations（含 fp_name + 缺 assertion）
```

### §5.3 v3.01 / v3.02 byte-lock（out_of_scope G-001/G-002/G-003）

```
$ stat -f '...'
v3.01 JSON: 338192 bytes (不变)
v3.01 xlsx: 41572 bytes (不变)
v3.02 JSON: 400677 bytes (不变)
v3.02 md: 73188 bytes (不变)
v3.02 xlsx: 25158 bytes (不变)
```

### §5.4 snapshot 终态

```
$ python3 -c "import json; s = json.load(open('.../snapshot.json')); print(s['status'], '/', s['loop_round'], '/', len(s['follow_up_items']))"
achieved / 8 / 0
```

---

## §6 GL-009 语义校验 + user-confirmed pass 记录

| 维度 | 值 |
|---|---|
| **GL-009 判定** | `goal-loop` 当前为 **follow_up 自迭代** 模式（Round 17 snapshot follow_up_count=3 → Round 18 清 3） |
| **§3.2 合法目标变更路径** | 走 follow_up 自迭代，不属于"用户追加新 goal" |
| **user-confirmed pass** | 用户层面已确认（user query 开头"GL-009 语义校验已在用户层面确认为'当前 goal follow_up 自迭代'"） |
| **本轮动作合法性** | ✅ 合法（Round 17 延后的 3 项 follow_up，本轮处理 3 项；不改变 goal 本身） |

**§6 判定**：✅ **GL-009 语义校验通过**（user-confirmed pass · 走 §3.2 合法目标变更路径）

---

## §7 总体判定（预期）

**Round 18 结论**（预期）：✅ **PASS — 本轮处理 3 项 follow_up 中的 3 项（FU-2 pipeline 集成 + FU-4 --auto argv + FU-5 open_questions 归档）**

- ✅ **FU-2** [MINOR]：stage_gatekeeper + coverage_validator 集成 assertion 校验（pipeline 接入）
  - `compute_assertion_gap_report(test_cases)` 返回 `{total_tcs, with_assertion, without_assertion, types_distribution}`
  - `_finalize_ledger` 挂 `assertion_stats` 字段（向后兼容）
  - `run_postflight_gate` S6 段调用校验调用 + 把违规写入 `result["assertion_validation"]`
- ✅ **FU-4** [MINOR]：l1 `--auto <json_path>...` argv 实现 + C24 自测通过
- ✅ **FU-5** [MINOR]：Q-V17-001~007 全部"已解（R17）"，新建 `governance/open_questions_archive_v17.md`；原档首加"已解"标注
- ✅ v3.01 JSON 不变（338192 bytes）；v3.01 xlsx 不变（41572 bytes）
- ✅ v3.02 全套不变（400677/73188/25158 bytes）
- ✅ self-test 24 cases（22 + C23 + C24）全部 PASS
- ✅ §9.1 红线内（业务文件 3 = ≤3，无需走 §9.1.1 豁免；3 文件均自洽满足豁免条件）
- ✅ §9.5 决策档 `round18_q_decision_table.md` 已落档
- ✅ §9.4 先验后答约束满足（11 个文件 Read）
- ✅ GL-009 语义校验通过（user-confirmed pass · §3.2 合法目标变更路径）
- ✅ snapshot 终态：`status=achieved` / `loop_round=8` / `follow_up_count=0`

---

> 本决策档：`round18_q_decision_table.md`（loop_round=8）
> 配套档：`.goal-log-db/active/32a8ff45-.../{audit_18.md, review_18.md, snapshot.json}`（atomic write）
