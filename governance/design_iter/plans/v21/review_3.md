# Round 3 Review — GL-005 + GL-006 P2 落地

> **Round**: 3
> **Goal**: Goal Loop Skill v1.1 版本优化
> **日期**: 2026-07-18

---

## 缺陷汇总

| # | 缺陷 | 严重度 | 说明 |
|---|---|---|---|
| D1 | audit_stability 变更追踪无自动化 | MAJOR | 产出物变更时需 Agent 主动调用 update_snapshot，依赖执行纪律而非代码保证 |
| D2 | 基线项校验无代码层实现 | MAJOR | QUALITY_BASELINE.mdc 是文档约定，Audit 阶段的基线叠加校验依赖 Agent 人工执行，无脚本自动化 |
| D3 | 基线库按类型加载未实现 | MINOR | SKILL.md 提到"按 Goal 类型加载子集"，但当前基线库未提供类型映射配置 |

---

## 根因定位

| 根因 | 类别 | 分析 |
|---|---|---|
| D1: 无自动追踪 | 实现复杂度 | audit_stability 需要跨轮次追踪产出物 hash，当前 snapshot 无内置 hash 计算，需 Agent 人工比对 |
| D2: 文档 vs 代码 | 实施策略 | 基线校验是 LLM 推理任务（判断产物是否符合规范），难以用脚本自动化；当前以文档约定为主 |
| D3: 配置缺失 | 规范问题 | 基线库未提供 `baseline_by_goal_type` 映射表 |

---

## 可落地修复方案

### D1 修复方向（Round 4+）

在 goal_snapshot.py 新增 `compute_artifact_hash()` 辅助函数，计算产出物目录的哈希值，存储到 audit_stability。Agent 在 Act 结束后调用。

### D2 修复方向（长期）

在 ai_workflow/ 中新增 `baseline_validator.py`，对 JSON 产物提供 L1 基线校验（字段完整性/枚举合法性），与 L1 校验器集成。

### D3 修复方向（立即）

在 QUALITY_BASELINE.mdc 末尾补充类型映射表：

```markdown
## 按 Goal 类型加载

| Goal 类型 | 适用基线 |
|---|---|
| development | FMT-01/03, NAM-01/02, STR-01/02, QUA-01/02/03, TRC-01/02 |
| documentation | FMT-01/02, NAM-03, STR-01, QUA-03, TRC-01 |
| analysis | STR-01, QUA-01, TRC-01/02 |
```

---

## Round 3 执行记录

| 产出物 | 路径 | 状态 |
|---|---|---|
| SKILL.md §3.3 强化 | `.cursor/skills/goal-loop/SKILL.md` | ✅ 更新（增量审计详情 + 基线校验详情） |
| SKILL.md §2 Schema | `.cursor/skills/goal-loop/SKILL.md` | ✅ 更新（17字段，与 goal_snapshot.py 同步） |
| goal_snapshot.py v3.1 | `ai_workflow/goal_snapshot.py` | ✅ 更新（out_of_scope_md + audit_stability，16项self-test通过） |
| antipattern_cases.md 清理 | `knowledge/public/goal_loop/` | ✅ 删除 .md，保留 .jsonl |
| audit_3.md | `governance/design_iter/plans/v21/audit_3.md` | ✅ 本文件 |
| review_3.md | `governance/design_iter/plans/v21/review_3.md` | ✅ 本文件 |
