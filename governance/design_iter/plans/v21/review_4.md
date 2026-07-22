# Round 4 Review — GL-007 + GL-008 + GL-009 P3 落地

> **Round**: 4
> **Goal**: Goal Loop Skill v1.1 版本优化
> **日期**: 2026-07-18

---

## 缺陷汇总

| # | 缺陷 | 严重度 | 说明 |
|---|---|---|---|
| D1 | 聚合报告脚本未落地 | MAJOR | GL-008 效能统计字段已定义，但"每月自动生成报告"的聚合脚本未实现 |
| D2 | MIN_SIGNATURE_SIMILARITY 硬编码 | MINOR | 0.7 阈值硬编码在 goal_snapshot.py 中，无配置层 |
| D3 | Jaccard 相似度局限性 | MINOR | 无法检测词汇相似但语义相反的漂移 |

---

## 根因定位

| 根因 | 类别 | 分析 |
|---|---|---|
| D1: 工具层未实现 | 实施策略 | GL-008 方案定义的是"数据规范"，聚合报告属于"工具实现"，按方案设计分离 |
| D2: 配置层缺失 | 实现复杂度 | 阈值配置需独立 Config 层，超出 Skill 规范范围 |
| D3: 算法局限 | 技术约束 | Jaccard 是轻量级近似算法，语义级检测需要 LLM 辅助（成本高） |

---

## 可落地修复方案

### D1 修复方向（独立 Goal）

创建新 Goal："实现 Goal Loop 效能聚合报告脚本"，依赖 session-index-schema.md 规范，产出 `scripts/aggregate_efficiency_stats.py`。

### D2 修复方向（Round 5+）

在 `ai_workflow/goal_snapshot.py` 顶部新增 `GL009_SIMILARITY_THRESHOLD = 0.7` 配置常量，并导出供外部引用。

---

## Round 4 执行记录

| 产出物 | 路径 | 状态 |
|---|---|---|
| goal_snapshot.py v3.2 | `ai_workflow/goal_snapshot.py` | ✅ 更新（generate_goal_signature + compute_similarity + update_efficiency_stats，20项self-test通过） |
| SKILL.md §3.2 | `.cursor/skills/goal-loop/SKILL.md` | ✅ 更新（语义校验详情 + Python 示例） |
| SKILL.md §2 Schema | `.cursor/skills/goal-loop/SKILL.md` | ✅ 更新（efficiency_stats 字段，18字段） |
| session-index-schema.md | `knowledge/public/goal_loop/session-index-schema.md` | ✅ 新建 |
| audit_4.md | `governance/design_iter/plans/v21/audit_4.md` | ✅ 本文件 |
| review_4.md | `governance/design_iter/plans/v21/review_4.md` | ✅ 本文件 |
