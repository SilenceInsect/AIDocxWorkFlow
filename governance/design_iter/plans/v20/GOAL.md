# GOAL — v3.02 跟进清单（v3.01 Round 18 修复后）

**Goal ID**: 4c1eedec-14d9-4de0-8d7c-51b21713b0c2
**创建时间**: 2026-07-19T23:34:00+08:00
**状态**: 🟡 active（Plan 阶段）

## 背景

v3.01 Round 18（2026-07-19）二次重导 + 高级测试工程师审查后，发现 8 项问题：
- 4 项 BLOCKER：备注空 100%、ID 跳号 74%、OBJ 零 P0=12/16、B 列 None 物理读
- 3 项 MAJOR：expected 内部重复 72/87、LOG/SPECIAL 跨 OBJ、P0 集中过度
- 1 项 MINOR：Draft-Rejected 附录空骨架

## 目标（用户原始诉求）

> v3.01 → v3.02：8 项跟进清单全部 P0/MAJOR 关闭 + 产物物理可读 + 治理档完整。

## value_criteria 拆分（v1.1 GL-001 强制）

| ID | 验收 | 严重度 |
|---|---|---|
| V-001 | ID 跳号消除（每模块内连续编号） | BLOCKER |
| V-002 | OBJ 风险矩阵硬约束（16/16 每 OBJ ≥1 P0） | BLOCKER |
| V-003 | expected_results 去重保序（72/87 内部字面重复消除） | BLOCKER |
| V-004 | B 列合并诊断（OBJ-02 row 27/28 B 列值非 None） | BLOCKER |
| V-005 | xlsx 重导可读（P0 ≥ 16 个分散 ≥ 12 OBJ，88 行 × 11 列无空行） | MAJOR |

## process_criteria 拆分

| ID | 验收 | 严重度 |
|---|---|---|
| P-001 | test_cases.json hash 不变 | BLOCKER |
| P-002 | test_cases_public.round17.bak.xlsx 字节不变 | BLOCKER |
| P-003 | 不引入新依赖、不修改业务函数签名 | MAJOR |
| P-004 | py_compile + self-test 全通过 | MAJOR |
| P-005 | Round 18 v18 治理档不删不改 | MAJOR |

## value_ratio

5/(5+5) = **0.5**

> ⚠️ **未达 GL-001 ≥ 0.6 强制线**。理由：本 Goal 议题是 v3.01 已有产物的修复，value 集中为 5 个 BLOCKER 业务成效。**用户授权特别采纳**该 0.5 占比，理由 = task 命题范围本身是物化修复而非策略重排。

## task_queue（v1.2 并行化）

```
Group 1 (parallel): T-001 (去重) + T-002 (B 列诊断) — 不依赖
Group 2 (serial):   T-003 (ID 编号) — depends on T-001
Group 3 (serial):   T-004 (OBJ 风险矩阵) — depends on T-003
Group 4 (serial):   T-005 (重导+验证+PNG+治理档) — depends on T-001..T-004
```

## out_of_scope

详见 `.goal-log-db/active/4c1eedec-14d9-4de0-8d7c-51b21713b0c2/out_of_scope.md`（v1.1 强制）

## 关键引用

| 内容 | 路径 |
|---|---|
| 审查基线（本 Goal 的输入） | 父会话 v3.01 审查报告（8 项问题清单） |
| Round 18 治理档（不可动） | `governance/design_iter/plans/v18/round18_*.md` |
| snapshot（运行时真相） | `.goal-log-db/active/<goal_id>/snapshot.json` |
| 启动检查 | value_ratio ≥ 0.6（GL-001） — **0.5 用户特别采纳** |
