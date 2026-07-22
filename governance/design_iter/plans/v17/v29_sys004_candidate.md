# v29 SYS-004 候选（待人工审核后入库 knowledge/public/goal_loop/systemic_issues.md）

> **来源**: v29 GOAL §5 SYS-004 + DT-V28-010 §9.3 + §10 防御建议
> **入库路径**: `knowledge/public/goal_loop/systemic_issues.md`（AGENTS.md Git 分类铁律：公共知识库 Agent 不得直接入库，本档仅作候选）
> **审核人**: 待人工

## 候选条目

### SYS-004 — snapshot 写入未走 update_snapshot API（含字符串拼接 JSON / 直接 Edit）

**漏洞描述**:

Agent 在修改 `snapshot.json` 时绕过 `goal_snapshot.update_snapshot()` API，
改用以下反模式路径之一：

1. 直接 `Edit` snapshot.json 字符串拼接 JSON（破坏 schema + 易引入转义错误）
2. 用 `json.dump(...)` 手工构造字段而非 `update_snapshot()` 提供的字段映射
3. 字符串 `replace` 改字段值（绕过 schema 校验 + 丢失 audit trail）

**首次出现时间**: 2026-07-18（v17.1 DT-v17.1-001 §DT-2 问题 1）
**末次出现时间**: 2026-07-20（v28 audit_round1.md §反模式触发复盘）
**出现次数**: ≥ 3（v17 / v18 / v27 各 1 次实证）
**严重度**: BLOCKER

**防御建议**（DT-V28-010 §9.3）:

1. 在 `.cursor/skills/goal-loop/SKILL.md` §3.2.1 后新增 §3.2.2 "snapshot 写入强制走 update_snapshot API" 段
2. 在 `goal_snapshot.py` 加 L2 校验：检测 `snapshot.json` 修改时间 vs `update_snapshot` 调用栈日志时间，若 snapshot 改动未对应 API 调用 → 触发 BLOCKER
3. 在 `goal_snapshot.update_snapshot()` 内部加 json.dump + atomic write（防止半写文件）

**相关 Skill**: goal-loop

## 候选区元数据

- 创建时间: 2026-07-20（v29 Round 1 T-108 worker）
- 候选决策表: governance/design_iter/plans/v29/GOAL.md §5 SYS-004
- 关联 DT: DT-V28-010
