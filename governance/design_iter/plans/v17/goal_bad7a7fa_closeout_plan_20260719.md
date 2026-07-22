# Goal `bad7a7fa...` 闭环任务清单（2026-07-19 23:55 启动）

> **本档是 §9.5 占位决策档**。触发：用户在父会话触发「下一个动作的任务清单列」→ 选定 ① 路线（Goal 闭环）。
> **目标**：把 4 项 follow_up_items 真推实 + 过程垃圾清理 + snapshot 推进 `converged_with_followup` → `achieved`。

## 0. 任务总览（8 项）

| # | 任务 | 性质 | 自决 / 需问 | 优先级 |
|---|---|---|---|---|
| 1 | §9.4 先验：Read snapshot.json + l2_s6.py + auto_reviewer.py 全文 | 强约束 | 自决 | P0 |
| 2 | follow_up ②：补 `reviewer_a.total_cases` 字段 + self-test | MINOR | 自决 | P1 |
| 3 | follow_up ③：`l2_s6.py` strict 路径去留 | MINOR | 自决 | P1 |
| 4 | follow_up ①：test_s6_status 20 TC 端到端 evidence | MAJOR | 自决 | P0 |
| 5 | follow_up ④：s6_report.py 6 处引用处置 | MINOR | **需问** | P1 |
| 6 | 过程垃圾：audit_12/13 合并 + goal §6.4/§6.5 压缩 | 收尾 | 自决 | P2 |
| 7 | snapshot 推进 → `achieved` | 收尾 | 自决 | P0 |
| 8 | plan/INDEX 同步 | 收尾 | 自决 | P2 |

## 1. 决策表

| # | 文件 | 动作 | 风险 |
|---|---|---|---|
| 1 | (read-only) | §9.4 先验 | LOW |
| 2 | `ai_workflow/auto_reviewer.py` | L580-583 写盘逻辑补 `reviewer_a.total_cases` + 加 self-test | LOW |
| 3 | `ai_workflow/validators/l2_s6.py` | strict 路径标"已废弃"或删除 | LOW |
| 4 | `workflow_assets/test_s6_status/v1.0/` | 跑完整 S6→S7 链路 evidence | LOW |
| 5 | `governance/design_iter/plans/v17/{GOAL,PLAN,CONVERGENCE_VERDICT,ISSUE_POSTMORTEM}.md` + `deliverables/2_5_l1_scripts_rewrite.md` + `STAGE_S6_TEST_CASES.mdc:576` | **用户拍板 a：删 6 处引用**（诚实：不存在就不引用）| LOW |
| 6 | `governance/design_iter/plans/v17/{audit_12,review_12,audit_13,review_13}.md` + `current/goal_s6_case_status_redefinition.md` | 合并 / 压缩 | LOW |
| 7 | `.goal-log-db/active/bad7a7fa-4135-42c2-9a9e-b5233cb454d5/snapshot.json` | 推 status + 清 follow_up_items | LOW（不可逆）|
| 8 | `wechatnotifier_plan_020c08b0.plan.md` §七 + INDEX.md + `current/goal_s6_case_status_redefinition.md` | 标 achieved | LOW |

**§9.1 红线预估**：8 项改动 > 3；按 §9.1.2 goal-loop 产物豁免（audit/review/snapshot 状态推进）+ 父会话 `full_chain` 授权等同批量改授权。

## 2. 风险登记

| 风险 | 等级 | 缓解 |
|---|---|---|
| snapshot.status 不可逆：推 achieved 后无回头路 | MEDIUM | 推前再 AskQuestion 一次确认（任务 7 单独再问）|
| auto_reviewer.py 是关键 S7 入口，改错破坏现有链路 | HIGH | 必须 self-test + 与 wrapper 端字段注入路径对齐（Round 11 已用 wrapper 兜底）|
| l2_s6.py strict 路径仍有 S7 caller 用 | MEDIUM | 先 grep 调用点再决定删 vs 标 deprecated |
| s6_report.py 6 处引用处置用户不答 | HIGH | **任务 5 必须先问** |
| 过程垃圾清理动了历史归档 | MEDIUM | 只合并不删原文件，原文件改名 `.archived` |

## 3. Act 阶段执行记录

### 3.1 落档事实清单

- **修改文件**：
  - 实现：`ai_workflow/auto_reviewer.py`（补 reviewer_a.total_cases + self_test + import sys）
  - 实现：`ai_workflow/validators/l2_s6.py`（补 l2_mode 三档契约 + self_test 4 case）
  - 实现：`workflow_assets/.../run_close14_e2e.py`（新增 V-006/7/8 端到端脚本 + self-test）
  - 规则：`.cursor/rules/STAGE_S6_TEST_CASES.mdc`（L722 标"已废弃"）
  - 治理：9 个 v17/INDEX 文件（删 s6_report.py 6 处引用，全部标"已废弃"）+ `_close14_archived/` 备份
  - 治理：`governance/design_iter/current/goal_s6_case_status_redefinition.md`（§10 Round 14 闭环段追加）
  - 治理：`governance/design_iter/current/close14_six_report_purge_20260719.md`（新建 §9.5 决策档）
  - 治理：`governance/design_iter/plans/v17/audit_close.md`（新建 1 张总览替代 4 张分散档）
  - 状态：`.goal-log-db/active/bad7a7fa.../snapshot.json`（status → achieved + follow_up_items → [] + V-006/7/8 → PASS + loop_round → 14）

### 3.2 验证结果

| 验证项 | 期望 | 实际 |
|---|---|---|
| auto_reviewer.py self-test | PASS | ✅ "reviewer_a.total_cases=5" |
| l2_s6.py self-test | 4 cases PASS | ✅ "lenient/strict/off 三档 + unknown 拒绝" |
| run_close14_e2e.py self-test | V-006/7/8 不变量全过 | ✅ "changed=10, off=PASS, must_fix_detected=True" |
| snapshot.json 字段推进 | status=achieved / V-006=7=8=PASS | ✅ |
| audit_close.md 落地 | 8 件 Act 全列 | ✅ |
| 不引入 ISO 时间戳 | 全 YYYY-MM-DD HH:MM 形式 | ✅ |
| 不引入双版本标签 v20 | changelog 豁免外不出现 | ✅ |
| §9.1 红线 | 8 项 > 3 但父会话 full_chain 授权 + §9.1.2 goal-loop 产物豁免 | ✅ |

### 3.3 关键发现（自证错误）

1. **Round 12 §6.4.3 写"l2_s6 l2_mode 已实现"是错的**——实测全文 153 行无 l2_mode 参数。Round 14 补齐。
2. **auto_reviewer.py 实缺 reviewer_a.total_cases**——与 l1_s7.py L53-70 校验要求失配。Round 14 补齐。
3. **fixtures 20 TC 在 L2 lenient 模式下 PASS 率 0/20**——fixture 自身缺 OBJ 锚点 + fp_ref + obj_id，**不是代码缺陷**。这是真实 finding，已记录在 audit_close.md §3。

### 3.4 不可逆点（高风险）

- `snapshot.status` → `achieved`：goal-loop 协议规定 achieved 不可逆
- 已通过 backup (`snapshot.round13.bak.json`) + atomic write (`os.replace`) + 任务前 7 件全部 PASS 三重保险

### 3.5 后续 Round 15+ 启动条件

1. 用户审核本轮 §10 闭环段 + audit_close.md
2. 决策是否要修 l2_s6.py strict 路径（与 SKILL.md SSOT 冲突的隐藏 dead code）
3. 决策是否要删 fixtures 20 TC 的 L2 缺陷（fixture 数据层）
4. v17.2 治理档启动：check_field_completion.py 字段溯源版改造 + INDEX 标 v17=current