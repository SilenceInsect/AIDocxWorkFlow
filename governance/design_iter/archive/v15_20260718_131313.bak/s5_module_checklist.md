# 分模块方法论 — SKILL.md §1.2 单一化

> 2026-07-16 决策
> 触发：用户确认"Prompt 不足"定义，要求在 SKILL.md §1.2 里做单一可执行 checklist

---

## 问题

6 个材料分散在 4 个路径，S5 Agent 归类时容易漏读 O_boundary / _decision_tree。

## 决策

**不改新增文件——直接扩写 SKILL.md §1.2**

把分散在 6 个材料里的归类决策，合并进 SKILL.md §1.2 的一个 checklist。Agent 读 SKILL.md 就完成所有归类决策。

---

## 改动范围

| 文件 | 改动 |
|---|---|
| `.cursor/skills/aidocx-s5-test-points/SKILL.md` §1.2 | 扩写：决策树 + 判定三问 + 核心反例表（全并入 1 节） |

---

## 改动摘要

### .cursor/skills/aidocx-s5-test-points/SKILL.md

| 位置 | 改动 |
|---|---|
| §1.2 | 替换"模块 × 类型双维度强制判定" + "HINT vs UI 二次判定" → 新 checklist（4 步 + 6 大误判表）|
| §1.4 必读材料表 | 删"两步法"段落 + 删第⑥条（_decision_tree.md）→ 指向 §1.2 |
| §S7-lite 边界表 | "决策树两步法" → "§1.2 checklist" |
| 执行卡 input_gate | "8 模块决策树（v14）_decision_tree.md" → "8 模块归类 checklist（v16）本 SKILL.md §1.2" |
| 执行卡 quality_gate | "通过决策树两步法控制" → "通过 §1.2 checklist 控制" |

---

## 落档协议执行记录

- 2026-07-16 新增本文件
- 2026-07-16 执行：SKILL.md §1.2 checklist 落地（4 步 + 6 大误判表）
