# Round 18 Review — FU-2 + FU-4 + FU-5 自迭代复盘

> **性质**：Goal-loop review（Round 18 复盘）
> **Goal**: 32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3（GL-009 · test case 审查治理）
> **Review 轮次**: Round 18（loop_round=8）
> **Review 人**: 架构师 worker（按 user 委托全权决策）
> **Review 时间**: 2026-07-19
> **来源**: audit_18.md 已 PASS；本档为三段式复盘

---

## §1 本轮做了什么（做了什么 + 怎么验证 + 影响范围）

### 1.1 FU-2 pipeline 集成 assertion 校验（PIPELINE 接入 · MINOR）

**做了什么**：
1. `ai_workflow/coverage_validator.py` 新增 `compute_assertion_gap_report(test_cases) → dict` 辅助函数（不动原 11 个公开函数签名）
2. `ai_workflow/stage_gatekeeper.py` S6 postflight gate 段集成 `check_assertion_completeness` + `check_no_fp_name_field(error)` + `compute_assertion_gap_report`，写入 `result["assertion_validation"]`（不动原 4 个公开函数签名）
3. `coverage_validator.py` + `stage_gatekeeper.py` 各加 `def self_test() → int` + `def main()` + `if __name__ == "__main__"` argv 分支（§9.1.1 豁免条款）

**怎么验证**：
- `python3 -m py_compile` 三件套全 OK
- `coverage_validator.py --self-test`：4 scenarios 全 PASS
- `stage_gatekeeper.py --self-test`：4 scenarios 全 PASS

**影响范围**：
- S6 postflight 调用方：现在会触发 assertion 校验并写 `postflight_gate.json` 的 `assertion_validation` 一节
- coverage_ledger.json 增量挂字段：未动（避免破坏 schema）
- 向后兼容：旧调用方不读 `assertion_validation` 仍能运行

### 1.2 FU-4 l1 `--auto` argv + C24（CLI 便利化 · MINOR）

**做了什么**：
1. `l1_format_validator.py main()` 新增 `--auto <JSON_PATH>` argparse（nargs="+" 支持多文件）
2. `_run_auto(json_paths)` 实现：每 path 读 JSON（3 schema 兼容）→ 跑 `check_assertion_completeness` + `check_no_fp_name_field(error)` → 打印 `path: N violations` + 每条 violation 简述
3. `self_test` 增 C24（fixture：4 TC = 2 全有 + 1 缺 assertion + 1 含 fp_name → 期望 2 violations；subprocess 隔离 argv + PYTHONPATH 透传确保子进程能找到 ai_workflow module）

**怎么验证**：
- `self_test` 24 cases 全 PASS（C1~C22 原有 + C23 FU-2 跨模块 + C24 FU-4 --auto）
- 实测 v3.02 = 0 violations（v3.02 已应用 F-E/F-F SSOT）
- 实测 v3.01 = 662 violations（331 MISSING_ASSERTION + 331 DEPRECATED_FP_NAME）

**影响范围**：
- CLI 用户：可手跑 `--auto <tc.json>` 单文件或批量校验
- 退出码语义：0 = 全过；1 = 任一违反（shell script 可直接 `&&` 链）
- 不动 import 路径：仍 `from ai_workflow.l1_format_validator import check_assertion_completeness`

### 1.3 FU-5 open_questions 归档（治理档清理 · MINOR）

**做了什么**：
1. Read `governance/design_iter/plans/v17/open_questions.md` 全文（142 行）确认文件实际路径
2. 按"已解 / 未解 / 无主"分类 7 条 Q——**全部已解**（Q-V17-001~007 在 R17 决策档 / audit_17 / review_17 中均有落档）
3. 新建 `governance/open_questions_archive_v17.md`（287 行）：每条 Q 完整迁移 + 标"已解（R17）"段 + 引用下游决策档
4. 原档 `governance/design_iter/plans/v17/open_questions.md` 档首加"📦 状态更新（Round 18 FU-5 · 2026-07-19）"段 + 指向 archive_v17.md

**怎么验证**：
- 7/7 Q 全部标"已解"，0 项无主（无 active Q 待人工认领）
- archive_v17.md 含每 Q 的"下游档"引用（`round17_q_decision_table.md` §1.4 + `audit_17.md` §1 FU-1）

**影响范围**：
- 治理档：新增 1 文件 + 编辑 1 文件头部
- **Q-V17-006 / Q-V17-007 的"⚠️"备注**：v17 提案与 v3.02 实装 schema 有 3 列新增 + 2 字段命名差异（轻微）；不影响业务决策；如需修订 → 提 v18+ 治理议程

### 1.4 治理档 + snapshot（标准动作）

**做了什么**：
1. `governance/design_iter/current/round18_q_decision_table.md`（§9.5 先落档 · 决策档）
2. `.goal-log-db/active/32a8ff45-.../audit_18.md`（本轮审计）
3. `.goal-log-db/active/32a8ff45-.../review_18.md`（本档）
4. `.goal-log-db/active/32a8ff45-.../snapshot.json`（待 W10 atomic write：loop_round=8 / status=achieved / follow_up_count=0）

---

## §2 解决了什么 / 新增了什么 / 遗留什么

### 2.1 解决了什么（FU-2/4/5 全清）

| ID | 原状态 | 解决方式 | 解决证据 |
|---|---|---|---|
| FU-2 | stage_gatekeeper pipeline 未接 assertion 校验 | stage_gatekeeper S6 段调 check_assertion_completeness + compute_assertion_gap_report + 检查出 violations 写 postflight_gate.json | self_test 4 scenarios PASS + v3.01/3.02 实测 |
| FU-4 | l1 helpers 仅 --self-test 模式触发 | l1_format_validator 加 --auto argv + _run_auto 函数 + C24 | self_test 24 cases PASS + 0/662 violations 实测 |
| FU-5 | Q-V17-001~007 在主档堆积 | 7 全已解归档到 archive_v17.md + 主档首加"已解"标注 | archive_v17.md 287 行 + 主档首加标注段 |

### 2.2 新增了什么

| 新增 | 内容 |
|---|---|
| `compute_assertion_gap_report()` 函数 | （FU-2 物化）S6 TC assertion 缺失统计 + 4 类断言分布 |
| `stage_gatekeeper.assertion_validation` | （FU-2 物化）postflight_gate.json 新字段，含 {passed, violations, gap_report} |
| `l1_format_validator --auto` argv | （FU-4 物化）批量校验生产产物，shell-friendly 退出码 |
| `_run_auto()` 函数 | （FU-4 物化）argv 实现，支持 3 schema JSON 兼容 |
| `open_questions_archive_v17.md` | （FU-5 物化）v17 治理已解历史存档（287 行） |

### 2.3 遗留什么（无）

| 维度 | 内容 |
|---|---|
| BLOCKER | 0 |
| MAJOR | 0 |
| MINOR | 0（本轮 3 项全清 → 0 延后） |

**架构师判断**：**本轮后 GL-009 闭环**——8 阶段目标全部完成，所有修复合入且字节守约束。**下轮预期 status=achieved**（除非用户主动加新目标）。

**遗留预案**（仅为文档完整性，非 follow_up）：
- v3.02 当前 0 violations 但 L1∧L2 写回尚未触发（仍是 Draft 状态）—— 下次有用户跑 L1∧L2 写回 → 主表 331 / 附录 0（按 _partition_cases_for_xlsx 设计）
- v3.02 数据如有 prompt 改进 → 走 v18+ 治理（如需）

---

## §3 下一步 / 改进计划（不是 follow_up）

| 类别 | 计划 |
|---|---|
| **目标闭环** | Round 19（待）→ snapshot.status='achieved'：本轮已清 FU-2/4/5；8 项 P-* + 8 项 V-* + 4 项 BLOCKER/MAJOR 全清 |
| **v18 治理议程** | 如有 v17 schema 偏差修订（Q-V17-006/007 已记）→ 走下一 Goal |
| **L1∧L2 写回** | v3.02 数据如需触发 L1（L1S6Validator.run_l1_check）+ L2（assertion 完整性）写回 → 当前 FU-2 已为生产触发铺路（stage_gatekeeper.run_postflight_gate 内自动跑）；任何端到端跑 S6 流程的人会自然触发 |
| **hook 升级** | `.cursor/hooks/content_compliance_check.py` 加 v17 字段校验 — 当前走"agent-only"路径；如要做硬拦截 → 走 Round 19+ 治理 |

**核心结论**：**Round 18 后 GL-009 全清**——决策档 + 审计 + 复盘三件套落档；snapshot 待 W10 atomic write。

---

> 本复盘档：`review_18.md`（loop_round=8）
> 配套档：`.goal-log-db/active/32a8ff45-.../{audit_18.md, snapshot.json}`（atomic write 待 W10）
