# Round 1 Review — GL-001 + GL-002 P0 落地

> **Round**: 1
> **Goal**: Goal Loop Skill v1.1 版本优化
> **日期**: 2026-07-18

---

## 缺陷汇总

| # | 缺陷 | 严重度 | 说明 |
|---|---|---|---|
| D1 | SKILL.md §2 Schema 中"每条验收项严重度"未细化到字段 | MAJOR | 当前严重度只贴在 Goal 层面（severity_label），方案要求每条 criteria 独立标注严重度 |
| D2 | goal_signature 生成逻辑未实现 | MAJOR | GL-009 Round 4 才完整落地，当前 Plan 阶段无签名生成机制 |
| D3 | value_criteria / process_criteria 拆分需人工判断 | MINOR | 当前无自动化辅助工具，判断"价值类 vs 过程类"依赖人工经验 |

---

## 根因定位

| 根因 | 类别 | 分析 |
|---|---|---|
| D1: 字段粒度不足 | 机制问题 | SKILL.md 只描述了 Goal 级别严重度，每条 criteria 的严重度通过 Audit 输出体现（verdicts 中 severity 字段），但 snapshot Schema 中未预留独立存储 |
| D2: GL-009 延期到 Round 4 | 实施策略 | GL-009 属于 P3，原计划 Round 4 落地，当前 Plan 阶段仅有占位符 |
| D3: 分类标准缺失 | 规范问题 | 缺乏"价值类 vs 过程类"的判定标准文档，Agent 执行时可能判断不一致 |

---

## 可落地修复方案

### D1 修复方向（Round 2+）

在 audit verdicts 中补充 `severity` 字段（已在 `_audit_supports_done` 中读取 `v.get("severity")`），snapshot Schema 无需变更（严重度通过审计结果传递）。

### D2 修复方向（Round 4）

在 Plan 阶段调用签名生成逻辑（使用 hashlib.sha256 对 `raw_user_goal` 生成摘要），写入 `goal_signature` 字段。

### D3 修复方向（Round 2）

在 SKILL.md 或 QUALITY_BASELINE.mdc 中补充"价值类/过程类验收判断标准"（示例：最终用户/业务可见的成效 → 价值类；执行过程规范 → 过程类）。

---

## Round 1 执行记录

| 产出物 | 路径 | 状态 |
|---|---|---|
| SKILL.md v1.1 | `.cursor/skills/goal-loop/SKILL.md` | ✅ 重写（255→~350行） |
| goal_snapshot.py v3 | `ai_workflow/goal_snapshot.py` | ✅ 重写（521→~780行，15字段，14项self-test通过） |
| goal_loop_breakloop_hook.py v2 | `.cursor/hooks/goal_loop_breakloop_hook.py` | ✅ 更新（支持converged_with_followup，7项self-test通过） |
| audit_1.md | `governance/design_iter/plans/v21/audit_1.md` | ✅ 本文件 |
| review_1.md | `governance/design_iter/plans/v21/review_1.md` | ✅ 本文件 |
