# v33 goal-loop — GOAL（目标骨架）

> **Goal**: v33 goal-loop：接力 v32 治理路线剩余 6 项移交任务 + 审查过往改动
> **Round**: 1
> **Date**: 2026-07-21
> **Snapshot**: 63302b9a-c13a-43c5-8bac-c4b730ea4159

---

## 1. 目标契约（v33）

### 1.1 原始目标

```
接力 v32 治理路线剩余 6 项移交任务 + 审查过往改动（S5/S6/SSOT/knowledge/ 一致性），
推进 L1~L6 6 治理项收敛落地
```

### 1.2 外部价值类验收（VC1~VC6）

| ID | 验收标准 | 来源 |
|---|---|---|
| VC1 | L1 ssot_citation_path 100% 落地且无漂移（选项 C 已落档）| `decision_l1_upgrade.md` DT-V32-001 |
| VC2 | L2 SCC 公式已落 SSOT（DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3 修订）| `decision_scc_FINAL.md` DT-V32-002 |
| VC3 | L3/L4 方法论草案已起草（v32_01+v32_02）| `PLAN.md` §3.1 + §3.2 |
| VC4 | v32_04 A 路径已执行或已实测论证（LLM 模拟 dry-run）| `decision_v32_04_FINAL.md` DT-V32-003 |
| VC5 | v32_05 候选目录已创建且首批 TP 已抽取入库（5~10 条 v3.01 TP）| `decision_v32_05_FINAL.md` DT-V32-004 |
| VC6 | 4 项 FINAL 决策用户已复核（接受/回滚/修改）| 4 FINAL 档 §1.1 触发条件 |

### 1.3 内部过程类验收（PC1~PC4）

| ID | 验收标准 | 来源 |
|---|---|---|
| PC1 | 每轮产 audit_N.md + review_N.md（Round 1~N）| SKILL §3 |
| PC2 | 零 SSOT 修改除非用户显式拍板 | AGENTS.md |
| PC3 | DNA §9.4 先验后答 + §9.5 落档协议 100% 兑现 | DNA_3Q_CHECK.mdc |
| PC4 | 零文件系统副作用（knowledge/ 未直接写入除非用户拍板 v32_05）| REPAIRING_report.md §3 |

---

## 2. v33 与 v32 的角色分工

| 角色 | v32（已完成）| v33（本 goal）|
|---|---|---|
| **已完成** | 6 治理项决策落档（4/6 FINAL + 2/6 立项）| 执行层落地 |
| **核心矛盾** | 决策已落，执行未动 | 需要逐项推进执行 |
| **token 预算** | 110000/150000（Round 4 耗尽）| 150000 |
| **用户参与** | 连续 2 轮 skip | 需用户复核 4 项 FINAL |

---

## 3. Round 1~N 排期

| Round | 核心行动 | 目标 VC |
|---|---|---|
| **Round 1**（本轮）| audit + review + GOAL（已完成）| — |
| **Round 2** | 用户复核 4 项 FINAL（VC6）+ TP 抽取规则起草（VC5）| VC6, VC5 |
| **Round 3** | v32_05 候选目录创建 + 抽取 5~10 条 v3.01 TP（VC5）| VC5 |
| **Round 4** | SSOT 修订草案（.mdc §4.3，VC2）| VC2 |
| **Round 5** | L3/L4 方法论草案（VC3）+ v32_04 B 路径 dry-run（VC4）| VC3, VC4 |
| **Round 6+** | CONVERGED（若 6 项 VC 全部 PASS）| VC1~VC6 |

---

## 4. 禁区清单（out_of_scope）

- ❌ 不修改 SSOT（.mdc/.yaml/MODULES.md）除非用户显式拍板 VC2（L2 SCC 公式）
- ❌ 不创建 v32_05 候选目录除非用户复核 VC6 后接受
- ❌ 不执行 v32_04 B 路径 dry-run 除非 Round 2 预算充足
- ❌ 不合并 v31 archive / INDEX.json 同步（架构层遗留，不在 v33 范围）

---

## 5. 历史坑点（v32 经验）

| 坑点 | 应对 |
|---|---|
| Round 4 act 设计超 token 余量（55000 ≈ 1.5 轮）| Round 2+ 限制单轮 ≤ 3 文件 |
| 用户连续 2 轮跳过决策询问 | Round 2 Act 强制发起 AskQuestion |
| decision_v32_05 FINAL.md 意图"新建候选区"但未实际创建 | v33 Round 3 明确区分"决策起草"vs"执行创建" |
| v32 是"决策轮"不是"执行轮" | v33 每轮必须有执行动作（不只是落档文档）|

---

## 6. 收敛判定（SKILL §9）

**全部通过才 achieved**：

| 条件 | 当前状态 |
|---|---|
| 6 项 VC 全部 PASS | ❌ 5 FAIL + 1 PARTIAL |
| 正确范例已实现 | ❌ v32_05 候选目录 NOT EXISTS |
| 无未处理 FAIL/UNKNOWN | ❌ 5 FAIL |
| 无真实阻塞 | ⚠️ 用户复核权悬空（VC6 FAIL）|
| 最终差异与目标范围一致 | ✅ v33 仅推进执行层，无越界 |

→ **Round 1 判定：🟡 继续 Act → Round 2**
