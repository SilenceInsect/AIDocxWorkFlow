---
name: aidocx-s1-5-clarification
description: >
  AIDocxWorkFlow Stage 1.5 — 业务澄清与准出许可。在 S1 评审通过后，人工填写 clarification_checklist.md 处理方案后执行。基于人工反馈完善终版需求.md，输出 exit_permission（准出许可），为 S2 提供质量评价和可选的保底规则建议。使用当用户完成 clarification_checklist.md 填写后说「已填写」「好了」或类似表达。
  Use when the user has finished filling clarification_checklist.md and says '已完成'/'已填写'/'好了'.
  使用当 S1 评审通过后，用户已人工填写 clarification_checklist.md 并准备完善终版需求.md 时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s1-5-clarification
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S1.5 — 业务澄清与准出许可

> **独立子阶段**：在 S1 评审通过后、S2 需求拆解前执行。
> 上游材料（S1 终版需求.md 草稿 + 人工填写的 clarification_checklist.md）审查合格后开始。

---

## 阶段入口

**触发**：用户填写完 `clarification_checklist.md` 后告知 AI，或 AI 感知到清单已填写。

**前置材料**：
- S1 终版需求（草稿）：`workflow_assets/<req_name>/「S1 需求评审」/<version>/终版需求.md`
- 待确认清单：`workflow_assets/<req_name>/「S1 需求评审」/<version>/clarification_checklist.md`
- S1 评审报告：`workflow_assets/<req_name>/「S1 需求评审」/<version>/review_report.md`

**材料缺失时**：
- 若 `clarification_checklist.md` 未填写 → 提示用户先填写
- 若 P0 项未填写 → 提示用户必须填写 P0 项

---

## 核心职责

1. **完善终版需求.md**：基于人工填写的处理方案，补充缺失的业务规则、修正歧义、更新待确认项
2. **生成准出许可（exit_permission）**：输出结构化的质量评价和准出判定，供 S2 读取
3. **给出保底规则建议**：若输入质量存在局限，为 S2 提供可选的保底拆解规则

---

## 输入审查（门禁前置）

| 检查项 | 要求 | 缺失时 |
|--------|------|--------|
| **S1 5 份物料齐全** | review_report / role_definitions / requirement_objects / 终版需求 / clarification_checklist **5 份都存在** | 退回 S1 |
| P0 问题已填写 | P0 100% 填写 | 触发 `fail_report_S1_5.md`（BLOCKED） |
| 强付费项 P0 | `SPECIAL_FLAG = PURCHASE_STRONG` 的 P0 **必须**全部答完 | 与 P0 缺失同等处理 |
| 处理方案有效 | 处理方案不为空或无意义占位文字 | 提示用户填写具体决策 |
| clarification_checklist.md 存在 | 文件存在且 `## 问题需求（→ S1.5 准入物料）` 节非空 | 提示用户先走 S1 生成清单 |

> **S1.5 不可被缺省**——S2 执行前**必须**有 `exit_permission.json` 且 `can_proceed_to_s2 == true`，否则 S2 拒绝执行。
> **轻量跑通** = P0 全填 + P1/P2 可不填（quality_level = LOW），S2 仍可执行。

---

## 输出规范

### 产出1：完善的终版需求.md（更新）

路径：`workflow_assets/<req_name>/「S1 需求评审」/<version>/终版需求.md`

在 S1 草稿基础上，基于处理方案进行以下更新：
- 补充缺失的业务规则（将处理方案转化为标准业务语言）
- 修正歧义或冲突
- 更新待确认项状态（已解决/遗留）
- 标注需要 S2 关注的风险点

### 产出2：准出许可（exit_permission.json）

路径：`workflow_assets/<req_name>/「S1 需求评审」/<version>/exit_permission.json`

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
    "can_proceed_to_s2": true | false,
    "quality_level": "HIGH | MEDIUM | LOW | BLOCKED",
    "quality_summary": "<一句话质量评价>",
    "items_filled": {
      "p0": 1,
      "p1": 3,
      "p2": 2
    },
    "items_total": {
      "p0": 1,
      "p1": 3,
      "p2": 2
    },
    "strong_purchase_p0_resolved": true | false
  },
  "fallback_rules": [
    {
      "trigger": "<触发条件（如：某字段为空）>",
      "rule": "<保底规则内容>",
      "source": "clarification | derivation | default"
    }
  ],
  "s2_guidance": {
    "priority_epics": ["<EpicID>", ...],
    "risk_points": ["<风险点>", ...],
    "open_questions": ["<待确认问题>", ...]
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

### 产出3：更新 clarification_checklist.md 状态

将状态字段改为「✅ 已处理（S1.5 准出许可已生成）」。

---

## 质量评价标准（exit_permission）

| quality_level | 判定条件 | can_proceed_to_s2 | S2 拆解深度 |
|---------------|----------|-------------------|-------------|
| **HIGH** | P0 全部填写 + P1 全部填写 + P2 全部填写 + 无遗留歧义 | true | 标准拆解 |
| **MEDIUM** | P0 全部填写 + P1 全部填写 + P2 部分填写 | true | 标准拆解 + 关注 s2_guidance open_questions |
| **LOW**（**轻量跑通**） | P0 全部填写 + P1/P2 可不填 | true | 标准拆解 + 应用所有 fallback_rules + 重点标注遗留项 |
| **BLOCKED** | P0 未填写 或 强付费项 P0 未答完 | false | —（S1.5 失败报告） |

> **轻量跑通** = 非正式验收流程下，S1.5 仍能产出 `exit_permission.json`、S2 可执行——**简单流程跑通测试专用**。
> **轻量跑通** ≠ **跳过 S1.5**——S1.5 不可被缺省这条**独立于验收深度**。
> `can_proceed_to_s2 == true` 的**唯一必要条件** = P0 全部填写（含强付费项 P0）。

---

## 与 S2 的衔接

S2 执行前必须读取 `exit_permission.json`：
- 若 `can_proceed_to_s2 == true` → 正常执行 S2
- 若 `can_proceed_to_s2 == false` → 停止，提示用户填写 P0 项
- 根据 `fallback_rules` 决定是否在拆解时补充保底规则
- 根据 `s2_guidance` 的 `priority_epics` 和 `risk_points` 优先关注高风险区域

S2 根据 `quality_level` 可选择性增强拆解深度：
- HIGH：标准拆解即可
- MEDIUM：标准拆解 + 关注 s2_guidance 中的 open_questions
- LOW：标准拆解 + 应用所有 fallback_rules + 重点标注遗留项

---

## 失败报告

路径：`workflow_assets/<req_name>/「S1 需求评审」/<version>/fail_report_S1_5.md`

触发条件：P0 项未填写，或所有检查项均为无效内容。

---

## 代码入口

```python
from ai_workflow.stage_s1_input import read_clarification_checklist

checklist = read_clarification_checklist(req_name="游戏道具商城系统", version="v1.0")
# 返回 dict: {"items": [...], "status": "pending"/"filled", "p0_filled": bool, ...}
```

---

## 参考文档

- S1 评审规范：`.cursor/rules/STAGE_S1_REVIEW.mdc`
- S2 拆解规范：`.cursor/rules/STAGE_S2_BREAKDOWN.mdc`
- 清单文件：`workflow_assets/<req_name>/「S1 需求评审」/<version>/clarification_checklist.md`
- 终版需求：`workflow_assets/<req_name>/「S1 需求评审」/<version>/终版需求.md`
- 准出许可：`workflow_assets/<req_name>/「S1 需求评审」/<version>/exit_permission.json`
