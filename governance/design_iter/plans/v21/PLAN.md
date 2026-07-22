# v21 Goal Loop v1.1 实施计划

> **日期**：2026-07-18
> **方案来源**：`Goal Loop Skill v1.1 版本优化需求.md`
> **本版目标**：完成 GL-001~GL-009 全部 9 项优化落地

---

## 一、优化项清单与落地状态

| 编号 | 名称 | 优先级 | Round | 状态 |
|---|---|---|---|---|
| GL-001 | 外部价值校验 | P0 | 1 | 待落地 |
| GL-002 | 验收标准分级 | P0 | 1 | 待落地 |
| GL-003 | out_of_scope 禁区清单 | P1 | 2 | 待落地 |
| GL-004 | 体系级复盘沉淀 | P1 | 2 | 待落地 |
| GL-005 | 质量基线兜底 | P2 | 3 | 待落地 |
| GL-006 | 增量审计去冗余 | P2 | 3 | 待落地 |
| GL-007 | 反模式案例沉淀 | P3 | 4 | 待落地 |
| GL-008 | 体系效能度量 | P3 | 4 | 待落地 |
| GL-009 | 目标签名防漂移 | P3 | 4 | 待落地 |

---

## 二、Round 分工

### Round 1 — P0 落地（GL-001 + GL-002）
- 重写 SKILL.md §2 Schema（accept_criteria 拆分 + 严重度 + follow-up）
- 重写 SKILL.md §3.1 Plan（新增 value_ratio 预检）
- 重写 SKILL.md §3.3 Audit（按严重度分级输出）
- 重写 SKILL.md §9 收敛判定（BLOCKER 全 PASS → CONVERGED_WITH_FOLLOWUP）
- 更新 goal_snapshot.py（扩展 Schema + 新字段支持）

### Round 2 — P1 落地（GL-003 + GL-004）
- 重写 SKILL.md §3.1 Plan（out_of_scope.md 强制产出）
- 重写 SKILL.md §3.3 Audit（新增越界检查模块）
- 新增 `knowledge/public/goal_loop/systemic_issues.md`
- 更新 SKILL.md §3.4 Review（自动识别 Skill 规范漏洞 → systemic_issues.md）
- 新增 `knowledge/public/goal_loop/QUALITY_BASELINE.mdc`（占位）

### Round 3 — P2 落地（GL-005 + GL-006）
- 完善 `QUALITY_BASELINE.mdc`（5 类通用质量要求）
- 重写 SKILL.md §3.3 Audit（叠加基线校验 + 增量审计逻辑）
- 更新 goal_snapshot.py（audit_stability 字段）
- 更新 goal_loop_breakloop_hook.py（支持 CONVERGED_WITH_FOLLOWUP 状态）

### Round 4 — P3 落地（GL-007 + GL-008 + GL-009）
- 新增 `knowledge/public/goal_loop/antipattern_cases.jsonl`
- 更新 goal_snapshot.py（efficiency_stats + goal_signature 字段）
- 重写 SKILL.md §3.2 Act（每轮执行前语义相似度校验）
- 更新 session-index.jsonl（新增效能统计字段）
- 完善 SKILL.md §5（反模式命中 → antipattern_cases.jsonl）

### Round 5 — 文档 + 回归 + 整理
- 更新 `knowledge/public/product_docs/goal_loop_product_spec.md`（v1.1）
- 整理所有 governance/design_iter/plans/v{N}/ 归档
- 验证向后兼容性
- 验证所有新产出路径符合 Git 分类铁律

---

## 三、产物路径

```
.cursor/skills/goal-loop/SKILL.md                    ← v1.1 核心规范
ai_workflow/goal_snapshot.py                         ← 快照持久化（v3，扩展 Schema）
.cursor/hooks/goal_loop_breakloop_hook.py            ← 破环 hook（v2，支持新状态）
knowledge/public/goal_loop/
  QUALITY_BASELINE.mdc                               ← 质量基线库
  systemic_issues.md                                 ← 体系问题沉淀
  antipattern_cases.jsonl                            ← 反模式案例库
  session-index-schema.md                            ← 效能统计字段说明
knowledge/public/product_docs/
  goal_loop_product_spec.md                          ← v1.1 产品说明
```

---

## 四、验收标准

1. **功能完整性**：9 项全部按设计方案落地
2. **向后兼容**：v1.0 Goal 在 v1.1 下正常运行
3. **文档完备性**：所有新增机制均有规范文档
4. **回归测试通过**：v1.0 测试用例通过率 ≥ 95%
