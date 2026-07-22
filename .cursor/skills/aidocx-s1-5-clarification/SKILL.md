---
name: aidocx-s1-5-clarification
description: >
  AIDocxWorkFlow Stage 1.5 — 需求澄清与准出许可。在 S1 评审通过后，人工填写 clarification_checklist.md 处理方案后执行。
  基于人工反馈完善终版需求.md，输出 exit_permission（准出许可）。
  使用当用户完成 clarification_checklist.md 填写后说「已完成」「好了」或类似表达。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s1-5-clarification
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S1.5 — 需求澄清与准出许可

> **独立子阶段**：在 S1 评审通过后、S2 需求拆解前执行。
> 上游材料（clarification_checklist.md + 终版需求.md）审查合格后开始。

---

## 阶段入口

**触发**：用户填写完 `clarification_checklist.md` 后告知 AI，或 AI 感知到清单已填写。

---

## 澄清清单交互方式

用户可通过以下任一方式填写澄清清单：

| 方式 | 说明 | 操作 |
|---|---|---|
| **A. 链接跳转** | 点击跳转链接，直接在 IDE 中打开文件编辑 | ✅ **推荐** |
| **B. 对话确认 + LLM 推导** | 用户给出关键词/方向，AI 推导补充完整内容 | ✅ **推荐（最快）** |
| C. 对话内表格 | 在对话中用 AskQuestion 表格填写（限简单字段）| 适用于简短字段 |
| D. 直接粘贴 | 用户自行填写文件后说"已填写" | 适用于复杂内容 |

**方式 A 操作步骤**：

```
1. AI 输出：点击下方链接跳转编辑
2. AI 输出：[跳转到 clarification_checklist.md](file:///Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets/<req_name>/<version>/「S1 需求评审」/clarification_checklist.md)
3. 用户：点击链接 → 文件在 IDE 中打开 → 填写 → 保存
4. AI：读取文件 → 验证 P0 填写 → 执行 S1.5
```

**方式 B 操作步骤（推荐，最快）**：

```
1. AI 列出 P0 问题清单（表格或列表）
2. 用户给出关键词/方向（如"LLM定"/"游戏币用内建系统"/"VIP链式开通永久"）
3. AI 基于关键词推导完整内容，填充到 clarification_checklist.md
4. AI 输出 exit_permission.json → S2 可执行
```

> ⚠️ **方式 B 约束**：仅适用于 P0 问题。AI 推导内容需在输出中标注来源（"LLM 推导补充"或"用户确认"）。

---

## 前置材料

| # | 材料 | 路径 | 说明 |
|---|---|---|---|
| 1 | clarification_checklist.md | `workflow_assets/<req_name>/<version>/「S1 需求评审」/` | **唯一验收对象**：人工填写 P0/P1/P2 处理方案；LLM 补齐缺口（标注 `[LLM 推导]`） |
| 2 | 终版需求.md（草稿） | `workflow_assets/<req_name>/<version>/「S1 需求评审」/` | S1.5 完善后的输出 |
| 3 | review_report.md | `workflow_assets/<req_name>/<version>/「S1 需求评审」/` | S1 质量评价，参考不验收 |

**交互原则**：clarification_checklist 以**人工填写为主**；空白 / 占位内容由 LLM 补齐。

**材料缺失时**：
- 若 `clarification_checklist.md` 未填写 → 提示用户先填写 P0 项
- 若 P0 项未填写 → 提示用户必须填写 P0 项

---

## 核心职责

1. **完善终版需求.md**：基于人工填写的处理方案，补充缺失的业务规则
2. **生成准出许可（exit_permission.json）**：输出质量评价和准出判定，供 S2 读取
3. **更新 clarification_checklist.md 状态**：标记为已处理

### LLM 补齐机制

> **前提**：人工填写是主要来源；LLM 在人工填写的**基础上**补齐缺口。
> **约束**：LLM 推导内容**必须**标注来源（`[LLM 推导]`），不得冒充人工决策。

**触发条件**：clarification_checklist 中存在以下情况时，AI 自动补齐：
- P0/P1/P2 处理方案为空或为占位文字
- P1/P2 未填写（LOW 模式下 P1/P2 可选，但 LLM 应给出推导建议供人工确认）
- 强付费项 3 段缺失时，LLM 推导合理的保底规则

**补齐方式**：
```
1. 识别空白 / 占位处理方案
2. 基于终版需求.md 中的上下文，LLM 推导合理的处理方案
3. 标注 [LLM 推导] 前缀
4. 输出时提示人工确认（或标记为 [待确认]）
```

**示例**：

| 字段 | 原始 | LLM 补齐后 |
|------|------|-----------|
| 处理方案 | （空） | `[LLM 推导] VIP 月卡与季卡不可叠加开通；需运营确认是否允许同时持有` |

---

## 输入审查（门禁前置）

| 检查项 | 要求 | 缺失时 |
|--------|------|--------|
| clarification_checklist.md 存在 | 文件存在且 P0 项非空 | 提示用户先完成 S1 |
| P0 项已填写 | P0 100% 填写 | `can_proceed_to_s2 = false`，S2 阻塞 |
| 处理方案有效 | 处理方案不为空 / 不为占位文字 | 提示用户填写具体决策 |

> **强付费项闭环**：S1 识别的强付费项 3 段（程序自测点/测试覆盖/策划验收）缺失，以 P0 项写入 clarification_checklist。S1.5 验收 P0（含强付费项 P0）即完成闭环。
> S1.5 **不再重复检查**强付费项 3 段（S1 已检查，S1.5 只检查 P0 是否填完）。

---

## 输出规范

### 产出1：完善的终版需求.md（更新）

路径：`workflow_assets/<req_name>/<version>/「S1 需求评审」/终版需求.md`

在 S1 草稿基础上，基于人工处理方案进行以下更新：
- 补充缺失的业务规则（将处理方案转化为标准业务语言）
- 修正歧义或冲突
- 更新待确认项状态（已解决 / 遗留）

### 产出2：准出许可 exit_permission.json

路径：`workflow_assets/<req_name>/<version>/「S1 需求评审」/exit_permission.json`

```json
{
  "version": "v1.0",
  "date": "YYYY-MM-DD",
  "stage": "S1.5",
  "upstream": {
    "s1_verdict": "PASS",
    "s1_score": 7.425,
    "req_name": "<req_name>"
  },
  "exit_permission": {
    "can_proceed_to_s2": true,
    "quality_level": "HIGH | MEDIUM | LOW",
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

### 产出3：更新 clarification_checklist.md 状态

将状态字段改为「✅ 已处理（S1.5 准出许可已生成）」。

---

## 质量评价标准

| quality_level | 判定条件 | can_proceed_to_s2 | S2 拆解策略 |
|---------------|----------|-------------------|-------------|
| **HIGH** | P0 全填 + P1 全填 + P2 全填 | true | 标准拆解 |
| **MEDIUM** | P0 全填 + P1 全填 + P2 部分填写 | true | 标准拆解 + 关注 s2_guidance.open_questions |
| **LOW**（轻量跑通） | P0 全填 + P1/P2 可不填 | true | 标准拆解 + 重点标注遗留项 |

| 状态 | 条件 | 结果 |
|------|------|------|
| P0 全部填写完毕 | — | `can_proceed_to_s2 = true` |
| P0 未全部填写 | — | `can_proceed_to_s2 = false`，S2 阻塞 |

> **轻量跑通** = P0 全填 + P1/P2 可不填，S2 仍可执行。轻量跑通 ≠ 跳过 S1.5。S1.5 不可被缺省。

---

## 与 S2 的衔接

S2 执行前必须读取 `exit_permission.json`：
- 若 `can_proceed_to_s2 == true` → 正常执行 S2
- 若 `can_proceed_to_s2 == false` → 停止，提示用户填写 P0 项
- 根据 `s2_guidance` 的 `priority_epics` 和 `risk_points` 优先关注高风险区域

---

## 失败报告

路径：`workflow_assets/<req_name>/<version>/「S1 需求评审」/fail_report_S1_5.md`

触发条件：P0 项未填写，或所有 P0 项均为无效内容。

---

## 代码入口

```python
from ai_workflow.stage_s1_input import read_clarification_checklist, read_exit_permission

# 读取 S1.5 准入物料
checklist = read_clarification_checklist(req_name="游戏道具商城系统", version="v1.0")
# 返回 dict: {"items": [...], "status": "pending"/"filled", "p0_filled": bool, ...}

# 读取 S1.5 产出准出许可
permission = read_exit_permission(req_name="游戏道具商城系统", version="v1.0")
# permission['exit_permission']['can_proceed_to_s2'] → bool
```

---

## 参考文档

- 三阶段边界 SSOT：`AGENTS.md` §三阶段核心边界
- S1 评审规范：`.cursor/rules/STAGE_S1_REVIEW.mdc`
- S2 拆解规范：`.cursor/rules/STAGE_S2_BREAKDOWN.mdc`
- 清单文件：`workflow_assets/<req_name>/<version>/「S1 需求评审」/clarification_checklist.md`
- 终版需求：`workflow_assets/<req_name>/<version>/「S1 需求评审」/终版需求.md`
- 准出许可：`workflow_assets/<req_name>/<version>/「S1 需求评审」/exit_permission.json`
