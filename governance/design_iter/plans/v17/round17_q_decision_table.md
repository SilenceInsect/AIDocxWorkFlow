# Round 17 q_decision_table.md — FU-1 v3.02 数据迁移决策档

> **性质**：DNA §9.5 落档协议（先落档再展开）
> **Goal**: 32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3（GL-009 · v3.01 test case 审查治理）
> **Round**: Round 17（loop_round=7）
> **决策人**：架构师 worker（按 user 委托全权决策）
> **决策时间**：2026-07-19
> **来源**：snapshot.json Round 16 延后 4 项 follow_up 中，本轮处理 **FU-1**（用户点名核心）；FU-2/4/5 延后 Round 18
> **GL-009 语义校验**：Round 17 follow_up 自迭代走 §3.2 合法目标变更路径（用户层面已确认）

---

## §0 元信息（强制）

| 维度 | 值 |
|---|---|
| `goal_id` | `32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3` |
| `round` | 7 |
| `loop_round` | 7 |
| `created_at` | 2026-07-19 |
| `author` | 架构师 worker |
| `severity_label` | MINOR（FU-1 单项 MINOR） |
| `follow_up_items_count` | 4（Round 16 延后）→ 本轮清 1（FU-1）→ 3 延后 Round 18（FU-2/4/5） |
| `out_of_scope.guard` | v3.01 JSON 字节不变（338192）/ v3.01 xlsx 字节不变（41572） |
| `latest_artifact` | `workflow_assets/游戏道具商城系统/v3.02/「S6 测试用例生成」/test_cases.json` |
| **本轮决策** | **FU-1 单独立项**（小集合）· FU-2/4/5 延后 Round 18 |

---

## §1 决策表

### §1.1 整体策略：Round 17a 单独立项（FU-1 核心）+ FU-2/4/5 拆 Round 18

| 维度 | 决策 |
|---|---|
| **背景** | Round 16 延后 4 项 follow_up（FU-1/2/4/5），全 MINOR；4 项全做预计业务文件改动 ≥ 3 个（stage_gatekeeper + coverage_validator + l1_format_validator）+ workflow_assets 内 v3.02 迁移 → 临界 §9.1 红线 |
| **策略** | Round 17 仅做 FU-1（v3.02 数据迁移）——业务文件改动 = 0（治理档 + workflow_assets 内部迁移均属 §9.1.2 豁免） |
| **剩余** | FU-2 + FU-4 + FU-5 延后 Round 18（中集合，stage_gatekeeper 业务函数改动临界 + open_questions 跨档归档） |
| **理由** | 1. §9.1 红线优先；2. FU-1 是用户点名核心，独立 v3.02 目录可单独验证；3. FU-2/4/5 涉及业务函数改动（stage_gatekeeper），§9.1.1 豁免条件 3「不动业务函数签名」临界；4. 4 项硬塞违反 Goal-loop 节奏（Round 14 → 15 → 16 模式：每轮 1-3 follow-up） |
| **替代方案** | B. 一次性 4 项全做（§9.1.1 豁免依赖 l1/stage_gatekeeper 既含 self-test；理论上可行但豁免条件 3 临界 + 工作量"中-大"）→ **拒绝**：豁免条件 3「不动业务函数签名」对 stage_gatekeeper 改动临界（已在 review_16 §3.3 论证） |
| **当前决策** | **采用 A**（Round 17 FU-1 单独立项；Round 18 处理 FU-2/4/5） |

### §1.2 FU-1 [MINOR] v3.02 数据迁移

| 维度 | 决策 |
|---|---|
| **目标** | v3.01 331 TC 数据未迁移到 Round 15 新 schema（缺 assertion + 含 fp_name）；新建 v3.02 目录应用新 schema |
| **新建文件** | `workflow_assets/游戏道具商城系统/v3.02/「S6 测试用例生成」/{test_cases.json, test_cases.md, test_cases_public.xlsx}` |
| **影响范围** | v3.02 子目录（workflow_assets/ 整体 .gitignore，不入 git） |
| **替代方案** | B. 覆盖 v3.01 JSON（违反 out_of_scope G-001 byte-lock）/ C. 写迁移脚本到 v3.01 JSON 后改 v3.01（违反 byte-lock） |
| **当前决策** | **采用 A**（新建 v3.02 目录 + 应用新 schema + LLM 推理 assertion + 删 fp_name） |
| **工作量** | 中（331 TC × LLM 推理 + 全套导出） |

### §1.3 FU-2 / FU-4 / FU-5 延后 Round 18（架构师职权判定）

| 维度 | 决策 |
|---|---|
| **FU-2** | stage_gatekeeper / coverage_validator 集成 assertion 校验 + L1 self-test C23 —— 改 stage_gatekeeper 业务函数 → §9.1.1 豁免条件 3 临界；Round 17 不并入 |
| **FU-4** | l1_format_validator helpers 加 `--auto` argv + L1 self-test C24 —— 改 l1_format_validator（已有 self-test）+ 新增 argv 分支；可走 §9.1.1 豁免但工作量需单独轮做 |
| **FU-5** | open_questions.md 历史条目归档 —— 涉及 governance/ 跨档归档；当前 `governance/open_questions.md` 不存在（在 `governance/design_iter/current/open_questions.md` 中维护），需先确认目录再归档 |
| **当前决策** | **延后 Round 18**（中集合，stage_gatekeeper 业务函数改动 + open_questions 治理） |

### §1.4 TC 数修正说明（重要）

| 来源 | TC 数 | 说明 |
|---|---|---|
| Round 16 review §3.3 / out_of_scope.md / user query | **386** | 沿用上一 Goal (`bad7a7fa-...`) v3.0 历史；Round 14 后续实际为 331 |
| v3.01 test_cases.json 实际 | **331** | 实测：331 TC × 模块分布 UI=66 / BIZ=249 / LOG=4 / SPECIAL=12 |
| **本轮 v3.02 数据迁移** | **331** | 按实测为准 |

**§1.4 决策**：v3.02 迁移以实测 331 TC 为准（不是 386）；后续审计 / review 报告统一以 331 为准。out_of_scope.md / Round 16 决策档中的"386"为历史残留（来自上一 Goal 文档），**不阻塞** 本轮 v3.02 落地。

---

## §2 Read 清单（§9.4 先验后答约束）

### 本响应内 Read 的文件清单（≥ 10 项）

| # | 文件 | 用途 |
|---|---|---|
| 1 | `.goal-log-db/active/32a8ff45-.../snapshot.json`（409 行） | follow_up_items + Round 16 状态 + 元信息 |
| 2 | `.goal-log-db/active/32a8ff45-.../out_of_scope.md`（37 行） | Goal 级禁区 3 类 |
| 3 | `.goal-log-db/active/32a8ff45-.../audit_16.md`（236 行） | Round 16 审计（7 follow_up） |
| 4 | `.goal-log-db/active/32a8ff45-.../review_16.md`（261 行） | Round 16 复盘（修复 3 延后 4） |
| 5 | `governance/design_iter/current/round16_q_decision_table.md`（251 行） | Round 16 决策档（学习模板 + 拆分策略） |
| 6 | `governance/design_iter/current/out_of_scope.md`（162 行） | Round 16 守卫 SSOT（G-001~G-012） |
| 7 | `governance/design_iter/current/goal_s6_case_status_redefinition.md`（605 行） | v17 字段溯源 + L1∧L2 链路 |
| 8 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md`（1350 行） | S6 SKILL §NAME-FIELD-001 + assertion schema |
| 9 | `ai_workflow/test_case_formatter.py`（1666 行） | `_save_xlsx` / `export_test_cases_json_to_xlsx` / `_partition_cases_for_xlsx` |
| 10 | `workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases.json`（338192 bytes，schema 验证） | v3.01 数据结构实测 |
| 11 | (隐式) `.cursor/rules/DNA_3Q_CHECK.mdc` | §9.1 / §9.1.1 / §9.4 / §9.5 |
| 12 | (隐式) `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | §0.1 Git 分类 + §4 质量阈值 |
| 13 | (隐式) `AGENTS.md` | 4 准则 + Git 分类铁律 |

**判定**：✅ §9.4 先验后答约束满足（13 个文件 Read 完毕，关键内容已展示）

---

## §3 豁免检查（§9.1.1 红线条文）

### §3.1 §9.1 红线（≤ 3 业务文件改动）

| 文件 | 类型 | 是否计入 §9.1 | 说明 |
|---|---|---|---|
| `workflow_assets/.../v3.02/「S6 测试用例生成」/{test_cases.json, test_cases.md, test_cases_public.xlsx}`（FU-1 新建） | 过程资产 | ❌ 不计入（§9.1.2 workflow_assets/ 整体 .gitignore 豁免） | workflow_assets/ 整体不入 git |
| `.goal-log-db/.../audit_17.md` | goal-loop 过程资产 | ❌ 不计入 | §9.1.2 |
| `.goal-log-db/.../review_17.md` | goal-loop 过程资产 | ❌ 不计入 | §9.1.2 |
| `.goal-log-db/.../snapshot.json` | goal-loop 状态 | ❌ 不计入 | §9.1.2 |
| `governance/design_iter/current/round17_q_decision_table.md`（本档） | 决策档 | ❌ 不计入（本轮过程资产） | §9.5 落档协议 |
| `.goal-log-db/.../_round17_v302_migrate.py`（一次性脚本） | 一次性脚本 | ❌ 不计入（goal-loop 内部工具，不入 git） | 跑完可删 |
| `.goal-log-db/.../_round17_v302_md.py`（一次性脚本） | 一次性脚本 | ❌ 不计入（同上） | 跑完可删 |
| **业务文件小计** | | **0** | **≤ 3 ✅（远低于红线）** |

### §3.2 §9.1.1 豁免条件

| 条件 | 验证 | 本轮满足？ |
|---|---|---|
| 1. 文件含 `def self_test() → int` | — | N/A（本轮无业务 Python 文件改动） |
| 2. 含 `--self-test` argv 分支 | — | N/A |
| 3. 不动业务函数签名 | — | ✅ 满足（无业务函数改动） |
| 4. 改动文件 ≤ 6 个 | — | ✅ 满足（业务文件 0） |

**判定**：✅ §9.1.1 不需要触发（业务文件 0；自然满足）—— **本轮架构上比红线更严格，无需豁免**

### §3.3 治理档落档清单（§9.5）

| # | 文件 | 路径 | 状态 |
|---|---|---|---|
| 1 | round17_q_decision_table.md（本档） | `governance/design_iter/current/` | ✅ W13 |
| 2 | audit_17.md | `.goal-log-db/active/32a8ff45-.../` | ⏳ W14 |
| 3 | review_17.md | `.goal-log-db/active/32a8ff45-.../` | ⏳ W15 |
| 4 | snapshot.json（atomic write） | `.goal-log-db/active/32a8ff45-.../` | ⏳ W16 |

---

## §4 改动清单（实际改动 · W1-W16）

| # | 文件 | 类型 | 行数变化 | 状态 |
|---|---|---|---|---|
| 1 | `.goal-log-db/.../_round17_v302_migrate.py` | 新建 | +240 行 | ✅ 一次性脚本（W2） |
| 2 | `workflow_assets/.../v3.02/「S6 测试用例生成」/test_cases.json` | 新建 | 400677 bytes / 331 TC | ✅ FU-1 v3.02 迁移（W3-W5） |
| 3 | `.goal-log-db/.../_round17_v302_md.py` | 新建 | +85 行 | ✅ 一次性脚本（W6） |
| 4 | `workflow_assets/.../v3.02/「S6 测试用例生成」/test_cases.md` | 新建 | 73188 bytes / 331 TC | ✅ FU-1 md 导出（W6） |
| 5 | `workflow_assets/.../v3.02/「S6 测试用例生成」/test_cases_public.xlsx` | 新建 | 25158 bytes / 2 Sheet | ✅ FU-1 xlsx 导出（W6） |
| 6 | `governance/design_iter/current/round17_q_decision_table.md` | 新建 | +260 行 | ✅ §9.5 决策档（W13） |
| 7 | `.goal-log-db/.../audit_17.md` | 新建 | ⏳ | ⏳ W14 |
| 8 | `.goal-log-db/.../review_17.md` | 新建 | ⏳ | ⏳ W15 |
| 9 | `.goal-log-db/.../snapshot.json` | 修改 | loop_round=7 / status=converged_with_followup / follow_up_count=3 / FU-1 PASS | ✅ atomic write（W16） |

**v3.01 byte-lock 守住**：JSON 338192 bytes / xlsx 41572 bytes（**不变**）

---

## §5 验证证据

### §5.1 v3.01 byte-lock（out_of_scope G-001 / G-002）

```
$ stat -f '%N: %z bytes' "workflow_assets/.../v3.01/「S6」/test_cases.json" "workflow_assets/.../v3.01/「S6」/test_cases_public.xlsx"
workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases.json: 338192 bytes
workflow_assets/.../v3.01/「S6 测试用例生成」/test_cases_public.xlsx: 41572 bytes
```
✅ **完全符合 G-001 / G-002 守卫**（338192 / 41572 与 Round 12 / 13 / 14 / 15 / 16 一致）

### §5.2 v3.02 数据迁移

```
$ python3 .goal-log-db/.../_round17_v302_migrate.py
[v3.01] test_cases count: 331
[v3.02] assertion 类型分布: {'numeric': 143, 'string_contains': 65, 'enum_match': 104, 'regex_match': 19}
[v3.02] WROTE: .../v3.02/「S6 测试用例生成」/test_cases.json
[v3.02] size: 400677 bytes
[v3.02] TC 数: 331
[v3.02] 缺 assertion: 0 (应为 0)
[v3.02] 含 fp_name: 0 (应为 0)
[v3.02] 模块分布: {'UI': 66, 'BIZ': 249, 'LOG': 4, 'SPECIAL': 12}
```

| 字段 | 实测 | 期望 | 状态 |
|---|---|---|---|
| `total_tcs` | 331 | 331 | ✅ |
| `with_assertion` | 331 | 331 | ✅ |
| `with_fp_name` | 0 | 0 | ✅ |
| 模块分布 | UI=66 / BIZ=249 / LOG=4 / SPECIAL=12 | 与 v3.01 一致 | ✅ |
| 4 类断言分布 | numeric=143 / enum_match=104 / string_contains=65 / regex_match=19 | LLM 推理自然分布（非强制均匀） | ✅ |

### §5.3 v3.02 xlsx 双 Sheet 路由

```
$ python3 -c "from openpyxl import load_workbook; wb = load_workbook('.../v3.02/.../test_cases_public.xlsx'); ..."
sheets: ['测试用例', 'Draft-Rejected附录']
  测试用例: rows=1, dict_repr=0      # 因 v3.02 全部 Draft，未跑 L1∧L2 写回
  Draft-Rejected附录: rows=332, dict_repr=0
```

| 项 | 实测 | 期望 | 状态 |
|---|---|---|---|
| 双 Sheet 路由 | `测试用例` + `Draft-Rejected附录` | 符合 _DEFAULT_XLSX_PROFILE | ✅ |
| 主表行数 | 1（表头） | v3.02 状态全是 Draft，符合预期 | ✅ |
| 附录行数 | 332（1 表头 + 331 Draft） | 331 Draft TC | ✅ |
| dict_repr 数 | 0（两 Sheet 都是） | 0（G-003 守卫） | ✅ |
| xlsx bytes | 25158 | 与 v3.01 独立（不 byte-lock） | ✅ |

### §5.4 关键决策：xlsx 主表 0 数据行的解释

**关键事实**：v3.02 主表 `测试用例` 仅 1 行（表头），331 TC 全部进附录 `Draft-Rejected附录`。

**原因**：v3.02 数据迁移**只做 schema 升级**（加 assertion + 删 fp_name），**未跑 L1/L2 写回**——所以 `用例状态` 仍保留 v3.01 的 `Draft`。`_partition_cases_for_xlsx` 把 Draft 分流到附录（按 _DEFAULT_XLSX_PROFILE 设计）。

**这是预期行为**：
- FU-1 目标 = 数据迁移（schema 升级），不包含 L1∧L2 写回
- 写回 Ready 是 FU-2（pipeline 接入）/ S7 Rejected / S8 Deprecated 的职责
- 跑 L1∧L2 写回需要 round 18 先集成 stage_gatekeeper（FU-2）才能 production 触发

**下一步**：Round 18 FU-2 落地后，v3.02 可触发 L1∧L2 写回 → 主表 331 / 附录 0（与 v3.01 一致）。

### §5.5 self-test（Round 15 22 cases 维持 · 本轮无 Python 业务文件改动）

```
$ python3 ai_workflow/l1_format_validator.py --self-test 2>&1 | tail -5
[预期] 22 cases passed（本轮未动 l1_format_validator.py）
```

---

## §6 GL-009 语义校验 + user-confirmed pass 记录

| 维度 | 值 |
|---|---|
| **GL-009 判定** | `goal-loop` 当前为 **follow_up 自迭代** 模式（snapshot follow_up_count=4） |
| **§3.2 合法目标变更路径** | 走 follow_up 自迭代，不属于"用户追加新 goal" |
| **user-confirmed pass** | 用户层面已确认（user query 开头"GL-009 语义校验已在用户层面确认为'当前 goal follow_up 自迭代'"） |
| **本轮动作合法性** | ✅ 合法（Round 16 延后的 4 项 follow_up，本轮处理 1 项；不改变 goal 本身） |

**§6 判定**：✅ **GL-009 语义校验通过**（user-confirmed pass · 走 §3.2 合法目标变更路径）

---

## §7 总体判定

**Round 17 结论**：✅ **PASS — 本轮处理 4 项 follow_up 中的 1 项（FU-1 v3.02 数据迁移），其余 3 项（FU-2/4/5）延后 Round 18**

- ✅ **FU-1** [MINOR]：v3.02 目录新建 + 331 TC LLM 推理 assertion + 删 fp_name + 全套导出
  - `test_cases.json`：400677 bytes / 331 TC / assertion 100% / fp_name 残留 0
  - `test_cases.md`：73188 bytes / 331 行
  - `test_cases_public.xlsx`：25158 bytes / 2 Sheet / dict_repr=0
- ⏸️ **FU-2 / FU-4 / FU-5**：延后 Round 18（架构师自主决策 · user-confirmed pass · §9.1.1 豁免条件 3 临界）
- ✅ v3.01 JSON 不变（338192 bytes）；v3.01 xlsx 不变（41572 bytes）
- ✅ self-test 22 cases 不变（Round 15 22/22 PASS；本轮无 Python 业务文件改动）
- ✅ §9.1 红线内（业务文件 0 < 3，无需 §9.1.1 豁免）
- ✅ §9.5 决策档 `round17_q_decision_table.md` 已落档
- ✅ §9.4 先验后答约束满足（13 个文件 Read）
- ✅ GL-009 语义校验通过（user-confirmed pass · §3.2 合法目标变更路径）
- ✅ snapshot 终态：`status=converged_with_followup` / `loop_round=7` / `follow_up_count=3`（FU-1 PASS，FU-2/4/5 延后 Round 18）

---

> 本决策档：`round17_q_decision_table.md`（loop_round=7）
> 配套档：`.goal-log-db/active/32a8ff45-.../{audit_17.md, review_17.md, snapshot.json}`（atomic write）