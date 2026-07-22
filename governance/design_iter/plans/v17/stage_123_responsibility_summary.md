# S1 / S1.5 / S2 三阶段职责对照

> **SSOT**：`AGENTS.md` §三阶段核心边界
> **更新时间**：2026-07-20（v31 重新规定后）

---

## 一句话定位

| 阶段 | 谁做 | 干什么 | 产出什么 |
|------|------|--------|---------|
| **S1 需求评审** | AI | 审查需求，找问题，定可行性 | 评审报告 + 澄清清单（clarification_checklist） |
| **S1.5 需求澄清** | 人工为主 + LLM 补齐 | 人工对澄清清单给出决策；LLM 补齐缺口（标注 `[LLM 推导]`） | 准出许可（exit_permission.json） |
| **S2 需求拆解** | AI | 把需求拆成可测试的颗粒度 | backlog + 需求对象（Epic → Story → OBJ → FP） |

---

## S1 需求评审

### 干什么

- 丢入原始需求文档（.docx / .md）
- AI 做质量闭环评审：找漏洞、模糊点、风险点
- 核心：**强付费项 3 段完整性验证**（程序自测点 / 测试覆盖 / 策划验收）
- 识别 P0/P1/P2 未闭环问题，写入澄清清单

### 产出什么（6 + 1 份）

| # | 文件 | 用途 | 去向 |
|---|------|------|------|
| 1 | `clarification_checklist.md` | **P0/P1/P2 待确认问题清单** | → S1.5（唯一验收对象）|
| 2 | `终版需求.md` | S1 整理后的需求草稿 | → S1.5 完善 → S2 |
| 3 | `review_report.md` | S1 评分报告（参考） | S1.5 参考，不验收 |
| 4 | `gm_commands.md` | GM 命令清单 | → S2（直接，不经 S1.5）|
| 5 | `test_coverage.md` | 测试覆盖矩阵 | → S2（直接，不经 S1.5）|
| 6 | `planning_acceptance.md` | 策划验收方案 | → S2（直接，不经 S1.5）|
| 7 | `quality_loop_report.md` | 强付费项 3 段闭环报告 | → S2（直接，不经 S1.5）|
| — | `role_definitions.md` | 角色定义 | → S2（直接，不经 S1.5）|

**S1 产出后做什么**：等人工填写 `clarification_checklist.md`

---

## S1.5 需求澄清

### 干什么

- 读 `clarification_checklist.md`
- **人工填写** P0/P1/P2 的**处理方案**
- **LLM 补齐缺口**：空白 / 占位内容由 LLM 推导（标注 `[LLM 推导]`），提示人工确认
- AI 将决策落档，完善终版需求.md，生成准出许可

### 核心原则

> **人工为主，LLM 补齐。**
> - LLM 推导内容**必须**标注 `[LLM 推导]`，不得冒充人工决策
> - P0 必须有人工填写或人工确认；P1/P2 可由 LLM 推导建议

### 核心原则

> **S1.5 不生产新知识，只归档人工决策。**
> AI 产出文档（gm_commands.md / test_coverage.md 等）不经过 S1.5，直接进入 S2。

### 产出什么（3 份）

| # | 文件 | 用途 |
|---|------|------|
| 1 | `exit_permission.json` | **准出许可**——can_proceed_to_s2 / quality_level / s2_guidance |
| 2 | `终版需求.md`（更新） | 基于人工决策完善后的版本 |
| 3 | `clarification_checklist.md`（更新） | 状态改为「✅ 已处理」 |

**唯一验收对象**：`clarification_checklist.md`（P0 必须填完）

### 门禁

| 条件 | 结果 |
|------|------|
| P0 100% 填写完毕 | `can_proceed_to_s2 = true`，S2 可执行 |
| P0 未全部填写 | `can_proceed_to_s2 = false`，S2 阻塞 |

### quality_level 评价

| 等级 | 条件 | S2 策略 |
|------|------|---------|
| HIGH | P0 + P1 + P2 全部填写 | 标准拆解 |
| MEDIUM | P0 + P1 填完，P2 部分 | 标准拆解 + 关注 open_questions |
| LOW（轻量跑通） | P0 填完，P1/P2 可不填 | 标准拆解 + 标注遗留项 |

---

## S2 需求拆解

### 干什么

- 读 `exit_permission.json`（can_proceed_to_s2 / quality_level / s2_guidance）
- 读 `终版需求.md`（已由 S1.5 完善）
- 将需求拆解为五层结构：**Release → Epic → Story → Object → FP**
- 明确测试范围（必测 / 排除 / 复用）

### 产出什么（4 份核心）

| # | 文件 | 用途 |
|---|------|------|
| 1 | `backlog.json` | Epic + Story 结构化数据（脚本解析用） |
| 2 | `backlog.md` | Epic + Story 人类可读版本 |
| 3 | `requirement_objects.json` | OBJ + FP 结构化数据（S5/S6 引用） |
| 4 | `requirement_objects.md` | OBJ + FP 人类可读版本 |

**S2 产出后做什么**：→ S3/S4/S5 并行

---

## 流程总览

```
原始需求文档（.docx/.md）
  ↓
┌─────────────┐
│  S1 评审    │  AI：审查需求，找问题，强付费项3段验证
│  产出6+1份  │  人工：等待填写 clarification_checklist
└─────────────┘
  ↓ clarification_checklist（P0/P1/P2）
┌─────────────┐
│  S1.5 澄清  │  人工：填写处理方案
│  产出3份    │  AI：落档，生成 exit_permission.json
└─────────────┘
  ↓ exit_permission.json（can_proceed_to_s2）
┌─────────────┐
│  S2 拆解    │  AI：Epic → Story → OBJ → FP
│  产出4份    │
└─────────────┘
  ↓
S3/S4/S5 并行
```

---

## 关键约束

| 规则 | 说明 |
|------|------|
| S1.5 不可缺省 | S2 执行前必须有 `exit_permission.json` 且 `can_proceed_to_s2 == true` |
| S1.5 不验收 AI 产出 | gm_commands.md / test_coverage.md 等直接进 S2，不经过 S1.5 |
| P0 是唯一门禁 | P0 填完 → S2 可执行；P0 未填 → S2 阻塞 |
| S2 读 exit_permission | S2 根据 quality_level 和 s2_guidance 调整拆解策略 |
