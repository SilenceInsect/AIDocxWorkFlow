# v15 BLOCKED 项汇总

> **来源**：v15 §5 执行过程中 BLOCKED 项
> **整理日期**：2026-07-16

---

## BLOCKED 项总表

| # | BLOCKED 项 | 对应任务 | 根因 | 预计解除时间 |
|---|---|---|---|---|
| B1 | S7 从未在 workflow_assets/ 执行过 | 任务 4 | S7 是 v2.0 新增阶段，workflow_assets/ 中无历史数据 | 需真实需求执行 S7 后解除 |
| B2 | test_cases.json 不存在 | 任务 7 | S6 依赖 S5，S5 依赖真实需求 | 需真实需求执行 S6 后解除 |

---

## B1 详细分析

### 根因

- S7 是 v2.0 新增阶段（2026-07 引入）
- workflow_assets/ 中的历史需求均执行于 v2.0 之前
- v15 §5 任务 4 设计为"在最近 1 个需求上跑 defect_cluster.py"，但最近 1 个需求无 S7 产出物

### 影响

- `defect_mode_latest.json` 无法生成（需 S7 review_report.json）
- `defect_mode_trend.json` 无法生成（需 ≥ 3 项目 S7 数据）
- v16 看板技术方案 A3 已完成，但无数据可验证

### 缓解措施

1. **blocker 备案**：见 `governance/design_iter/current/v15_L3_blocker.md`
2. **技术方案冻结**：defect_cluster.py + A3 schema 不变，等待数据
3. **v16 前提条件**：v16 看板阶段需 ≥ 3 项目 S7 数据积累

### 关联问题

- L7（缺陷模式 → Prompt 反哺闭环）依赖 B1 解除
- L8（增强路径触发条件实际验证）依赖真实需求执行 S2/S3

---

## B2 详细分析

### 根因

- v15 §5 任务 7 试点需"最近 1 个需求 ≥ 50 TC"
- workflow_assets/ 中无 test_cases.json（因 S6 也从未执行）
- 根本原因：pipeline 9 阶段从未在真实数据上完整执行过

### 影响

- L2 用例价值评分试点无法进行
- v16 自动化评分闭环无法提前验证

### 缓解措施

1. **试点延迟**：等待第一个完整执行 S1-S7 的需求
2. **试点范围调整**：若首个需求 TC < 50，改为"全量 TC 打分"
3. **v15 自检记录**：本 blocker 记录到 SELF_CHECK.md §遗留问题

---

## 与 v16 的桥接

| v15 BLOCKED 项 | v16 关联任务 |
|---|---|
| B1（S7 未执行）| v16 看板 → 需 S7 数据源 |
| B2（test_cases.json 不存在）| v16 自动化评分 → 需 TC 数据 |

**v16 启动条件**（D-V15-005 拍板）：≥ 3 项目 S7 + review_report 积累 → 隐含 B1/B2 必须先解除

---

## 执行记录

- 2026-07-16 新建本文件
- 2026-07-16 BLOCKED 项汇总完成
