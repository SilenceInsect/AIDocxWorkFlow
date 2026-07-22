# Round 2 Review — GL-003 + GL-004 P1 落地

> **Round**: 2
> **Goal**: Goal Loop Skill v1.1 版本优化
> **日期**: 2026-07-18

---

## 缺陷汇总

| # | 缺陷 | 严重度 | 说明 |
|---|---|---|---|
| D1 | out_of_scope.md 缺失时无强制兜底 | MAJOR | Plan 阶段强制产出，但无代码层强制校验，若 Agent 跳过则 Audit 无文件可读 |
| D2 | Skill 规范漏洞识别依赖人工判断 | MINOR | 当前 Review 阶段规范定义了识别逻辑，但无自动化辅助，需 Agent 主动识别 |
| D3 | antipattern_cases.jsonl 与 .md 并存 | MINOR | 同时存在 JSONL 数据文件和 Markdown 说明文件，可能造成维护混乱 |

---

## 根因定位

| 根因 | 类别 | 分析 |
|---|---|---|
| D1: 无强制兜底 | 机制问题 | out_of_scope.md 是文件层面的约定，不在 snapshot Schema 中，Audit 阶段无文件则无法检查 |
| D2: 识别依赖人工 | 规范问题 | Skill 漏洞识别是 LLM 推理任务，当前无结构化规则辅助 |
| D3: 文件类型混乱 | 规范问题 | antipattern_cases.jsonl 是数据文件，antipattern_cases.md 是说明文件，应统一格式 |

---

## 可落地修复方案

### D1 修复方向（Round 3）

在 snapshot Schema 新增 `out_of_scope_md` 字段（可选，路径），Audit 阶段检查该字段是否存在。也可在 goal_snapshot.py `create_snapshot` 时默认创建空 out_of_scope.md。

### D2 修复方向（长期）

考虑在 QUALITY_BASELINE.mdc 中补充"漏洞识别检查表"，Agent Review 阶段逐项勾选，降低识别门槛。

### D3 修复方向（立即）

删除 antipattern_cases.md（说明文件），仅保留 antipattern_cases.jsonl + 本文件顶部的格式说明。

---

## Round 2 执行记录

| 产出物 | 路径 | 状态 |
|---|---|---|
| SKILL.md §3.1 强化 | `.cursor/skills/goal-loop/SKILL.md` | ✅ 更新（out_of_scope.md 强制产出规范） |
| SKILL.md §3.3 越界检查 | `.cursor/skills/goal-loop/SKILL.md` | ✅ 更新（范围合规性检查 + 分级告警） |
| SKILL.md §3.4 漏洞识别 | `.cursor/skills/goal-loop/SKILL.md` | ✅ 更新（Skill 规范漏洞识别 + SYS-001 示例） |
| QUALITY_BASELINE.mdc | `knowledge/public/goal_loop/QUALITY_BASELINE.mdc` | ✅ 新建（5类13项） |
| systemic_issues.md | `knowledge/public/goal_loop/systemic_issues.md` | ✅ 新建（空表，格式完整） |
| antipattern_cases.jsonl | `knowledge/public/goal_loop/antipattern_cases.jsonl` | ✅ 新建（占位记录） |
| audit_2.md | `governance/design_iter/plans/v21/audit_2.md` | ✅ 本文件 |
| review_2.md | `governance/design_iter/plans/v21/review_2.md` | ✅ 本文件 |
