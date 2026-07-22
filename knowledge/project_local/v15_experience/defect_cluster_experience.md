# v15 缺陷模式聚类器经验归档

> **来源**：v15 §5 阶段 1 任务 1-3
> **执行日期**：2026-07-16（开发完成）

---

## 1. 核心决策

### 1.1 为什么选"频次统计"而非 ML

**决策**：v15 不引入 ML，按 `module × rca.type × rca.clause` 三维分组 + 频次统计。

**依据**：
- v15 数据量不足以训练有效模型（需 ≥ 10 项目 bypass_log）
- 频次统计可解释性强，QA 能直接看懂
- v16 可在数据积累后引入聚类算法

### 1.2 输出 schema 设计

**最终 schema**：

```json
{
  "defect_cluster_id": "CLS-{module}-{type}-{clause}-{hash}",
  "module": "tp",
  "rca_type": "incomplete_coverage",
  "rca_clause": "P0_item_missed",
  "count": 3,
  "projects": ["商城v1.0", "游戏v2.1"],
  "first_seen": "2026-07-01",
  "last_seen": "2026-07-15"
}
```

**设计理由**：
- `defect_cluster_id` 含 module + type + clause → 可快速过滤特定模块
- `projects` 字段为趋势分析预留（跨项目聚合时需要）

---

## 2. 实现细节

### 2.1 self-test 5 cases 设计原则

```python
# 5 cases 覆盖：
# 1. bypass_log 为空（正常返回）
# 2. review_report 中无 rca 字段（降级处理）
# 3. 单项目单条 bypass（基本路径）
# 4. 多项目多条 bypass（聚合路径）
# 5. bypass_log 和 review_report 均缺失（早停）
```

### 2.2 defect_cluster_id 生成规则

```
module: 来自 rca.stage（S1-S8）映射到 module（req/backlog/tp/tc...）
type: 来自 rca.type（incomplete_coverage / logic_error / format_issue...）
clause: 来自 rca.clause（P0_item_missed / boundary_omitted...）
hash: 取前 4 位 md5(projects) 确保同组合唯一
```

---

## 3. 已知的局限

| 局限 | 影响 | 缓解措施 |
|---|---|---|
| 无跨项目 trend（需 ≥ 3 项目）| trend.json 无法生成 | blocker 备案，等待数据积累 |
| bypass_log 可能为空 | 聚类结果仅来自 review_report | 接受，按 SKILL.md §5 统计 |
| rca.clause 依赖 S7 SKILL.md | schema 变更需同步更新 | SKILL.md 变更 checklist 加 rca 同步 |

---

## 4. 与 v16 看板的桥接

v16 看板数据源 = `defect_cluster.py` 输出的 `defect_mode_latest.json` + `defect_mode_trend.json`。

**看板展示的 3 个核心指标**：
1. **高频缺陷模式 TOP 5**：按 count 降序，取前 5
2. **模块 RCA 分布**：按 module 分组饼图
3. **跨项目趋势**：缺陷模式随时间的数量变化（需 trend.json）

---

## 5. 执行记录

- 2026-07-16 新建本文件
- 2026-07-16 defect_cluster.py 开发完成 + self-test 通过
