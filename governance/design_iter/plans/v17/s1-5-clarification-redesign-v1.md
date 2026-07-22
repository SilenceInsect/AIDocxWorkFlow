# S1.5 重新设计方案

> **状态**：Round 1 Act 产出
> **目标**：推翻旧的 S1.5 阶段，重新规定需求澄清阶段

---

## §1 核心决策

### D1：S1.5 本质重定义

**旧定义**（S1.5 Clarification.mdc）：
> S1.5 是"业务澄清与准出"——完善终版需求 + 生成准出许可 + 给出保底规则

**问题**：S1 已经做了"完善"，S2 才有"保底规则"——S1.5 夹在中间价值说不清。

**新定义**：
> S1.5 是**人工决策阶段**——将 S1 评审结论中未闭环的问题（clarification_checklist P0/P1/P2），由人工给出决策，AI 将决策落档并生成准出许可。
> S1.5 **不生产新知识**，只**归档人工决策**。

| 阶段 | 产出类型 | 谁做 |
|------|---------|------|
| S1 | AI 评审 + 整理需求 + 提出问题清单 | AI |
| S1.5 | 人工决策归档 + 准出许可 | 人工 + AI 落档 |
| S2 | 需求拆解 + 产出测试基线 | AI |

### D2：S1.5 前置物料精简为 3 份（强制）

**旧方案**：10 份物料（S1 产出全部过 S1.5）
**问题**：S1 的 gm_commands.md/test_coverage.md/planning_acceptance.md 等是 S2 的输入，不应该被 S1.5 二次验收。

**新方案**：S1.5 只验收 3 份：

| # | 物料 | S1.5 用途 |
|---|------|----------|
| 1 | `clarification_checklist.md` | **唯一验收对象**——P0/P1/P2 人工填写处理方案 |
| 2 | `终版需求.md`（草稿） | S1.5 完善后的输出（S1.5 修改它） |
| 3 | `review_report.md` | S1.5 参考，不验收（AI 产出） |

其余 S1 产出（gm_commands.md / test_coverage.md / planning_acceptance.md / quality_loop_report.md / role_definitions.md）**直接进入 S2**，不经过 S1.5。

**理由**：S1.5 是人工决策阶段，不是文档整理阶段。AI 产出不需要二次验收。

### D3：强付费项 3 段闭环由 S1 负责，S1.5 不重复检查

**旧方案**：S1 识别 3 段缺失 → S1.5 必须补齐 → can_proceed_to_s2 = true
**问题**：3 段补齐需要人工参与策划验收方案，S1.5 的澄清清单应该能承接这个工作。但两套体系（P0/P1/P2 + PURCHASE_STRONG 3段）重复。

**新方案**：
- S1 识别强付费项 3 段缺失 → P0 写入 clarification_checklist
- S1.5 验收 P0（含强付费项 P0）→ can_proceed_to_s2 = true
- 两套体系**合二为一**：clarification_checklist 的 P0 项 = 所有阻塞性问题（含强付费项 3 段缺失）

### D4：三阶段边界统一 SSOT

**决策**：三阶段定位只在 AGENTS.md 写一次（SSOT），STAGE_S*.mdc 只引用。

| 阶段 | 定位 | 核心原则 | 谁做 |
|------|------|----------|------|
| S1 | 审查需求、发现问题、定可行性 | **评审解决"能不能做"** | AI |
| S1.5 | 归档人工决策、给出准出许可 | **决策归档解决"歧义怎么定"** | 人工+AI落档 |
| S2 | 需求拆解、输出测试基线 | **拆解解决"测什么"** | AI |

---

## §2 新旧对比

| 维度 | 旧 S1.5 | 新 S1.5 |
|------|---------|---------|
| 核心职责 | 完善终版需求 + 生成准出许可 | 归档人工决策 + 生成准出许可 |
| 前置物料 | 10 份（S1 产出全部） | 3 份（clarification_checklist + 终版需求 + review_report） |
| 强付费项处理 | S1.5 二次验收 P0（含强付费项） | S1 识别 → P0 写入 checklist → S1.5 验收 P0 |
| 产出文件 | 终版需求.md + exit_permission.json + clarification_report.md | 终版需求.md（完善）+ exit_permission.json |
| exit_permission 字段 | 7 个顶层字段（遗留项/s2_guidance/fallback_rules等） | 4 个顶层字段（精简为必要字段） |
| clarification_report.md | 有（旧产出） | 删除（AI 不生产新知识） |

---

## §3 新 S1.5 流程

```
S1 PASS
  ↓（S1 产出 clarification_checklist.md）
S1.5 业务澄清
  ↓（人工填写 P0/P1/P2 处理方案）
  ↓（可选：AI 辅助推导 P0 答案）
AI 落档：
  1. 完善 终版需求.md（基于人工决策）
  2. 生成 exit_permission.json（can_proceed + quality_level）
  3. 更新 clarification_checklist.md 状态
  ↓（can_proceed_to_s2 == true）
S2 需求拆解
```

---

## §4 exit_permission.json 新字段（精简版）

```json
{
  "version": "v1.0",
  "date": "YYYY-MM-DD",
  "stage": "S1.5",
  "upstream": {
    "s1_verdict": "PASS | NEEDS_REVISION",
    "s1_score": 7.425,
    "req_name": "<req_name>"
  },
  "exit_permission": {
    "can_proceed_to_s2": true,
    "quality_level": "HIGH | MEDIUM | LOW",
    "quality_summary": "<一句话评价>",
    "items_filled": {
      "p0": 1,
      "p1": 3,
      "p2": 2
    },
    "items_total": {
      "p0": 1,
      "p1": 3,
      "p2": 2
    }
  },
  "s2_guidance": {
    "priority_epics": ["<EpicID>"],
    "risk_points": ["<风险点>"],
    "open_questions": ["<待确认问题>"]
  },
  "遗留项": [
    {
      "id": "L1",
      "description": "<描述>",
      "impact": "<影响范围>",
      "resolution": "<建议处理方式>"
    }
  ]
}
```

**精简说明**：
- 删除 `strong_purchase_p0_resolved`（已在 S1 闭环，S1.5 不重复检查）
- 删除 `fallback_rules`（保底规则是 S2 的职责，不是 S1.5 的）
- 保留 `s2_guidance`（S1.5 的人工决策对 S2 有指导价值）
- 保留 `遗留项`（人工未决策的项需要 S2 承接）

---

## §5 验收标准

| # | 验收标准 | 完成状态 |
|---|---------|---------|
| AC-1 | 新 STAGE_S1.5 Clarification.mdc 完成 | 待产出 |
| AC-2 | 新 aidocx-s1-5-clarification/SKILL.md 完成 | 待产出 |
| AC-3 | S1/S1.5/S2 衔接契约清晰（无死循环） | 待验证（T6） |
| AC-4 | S1.5 前置物料从 10 份精简为 3 份 | 已决策 |
| AC-5 | 新 S1.5 流程有实际需求场景引用 | 待补充 |
