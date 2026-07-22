# v14.5 — S3 增强路径分离（L1 落地）

> **状态**：✅ 全部完成（4 步全部落地 + 4/4 文件验证通过）
> **完成时间**：2026-07-14
> **位置**：`governance/design_iter/current/v14_5_l1_s3_path_split.md`
> **关联**：外部方案 §4.2 修订版 + v14 PLAN.md 附录 A
> **目标**：解决 "纯后端需求强制走 S3 冗余" 问题，不破坏 9 阶段契约

---

## 1. 增强路径设计（外部方案 §4.2）

### 1.1 三类增强路径触发条件

| 增强路径 | 触发条件 | 深度版产出 |
|---------|---------|-----------|
| **UI 原型增强** | UI 模块占比 > 30% 或需求含前端页面 | S3 深度版产出完整 UI 节点清单 + 交互状态机 |
| **异常风险增强** | 涉及支付 / 并发 / 分布式事务 | S4 深度版产出 7 类风险点 + 对抗场景矩阵 |
| **日志审计增强** | 涉及资产流水 / 合规审计 | LOG 模块独立深化，产出审计对账用例集 |

### 1.2 默认（轻量版）vs 深度版对比

| 维度 | 轻量版（默认） | 深度版（增强） |
|------|---------------|---------------|
| **S3 产出** | 页面清单 + 核心流图 | 页面清单 + UI 节点清单 + 交互状态机 + Mermaid |
| **S4 产出** | 基础流程 + 4 类风险点 | 7 类风险点全覆盖 + 对抗场景矩阵 |
| **LOG 模块** | 标准 TP/TC | 独立深化 + 审计对账用例集 |
| **适用需求** | 纯后端 / 轻 UI | 含 UI/支付/合规 |

---

## 2. 环境变量定义（AIDOCX_S3_MODE）

### 2.1 开关语义

| 环境变量 | 默认 | 含义 |
|---------|-----|-----|
| `AIDOCX_S3_MODE` | **未设置（lightweight）** | S3 模式：`lightweight`（轻量，页面清单+核心流图）/ `depth`（深度，完整 UI 节点清单） |

### 2.2 触发判断逻辑

```
AIDOCX_S3_MODE=depth       → 强制深度版
AIDOCX_S3_MODE=lightweight  → 强制轻量版（默认）
未设置                       → 智能判定（按 S2 UI 模块占比 > 30% 自动切换到 depth）
```

> ⚠️ **默认不强制 light**——S2 拆解结束后 LLM 自动判定 UI 占比，超过 30% 走 depth。

### 2.3 智能判定阈值

- UI 模块 Story 数 / 总 Story 数 > 0.30 → 走 depth 版
- 否则走 lightweight 版

---

## 3. 涉及文件清单

| # | 文件 | 改动 |
|---|------|-----|
| 3.1 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | §4.3 加 `AIDOCX_S3_MODE` 阈值常量 |
| 3.2 | `.cursor/skills/aidocx-s3-prototype/SKILL.md` | 加 "模式选择" 章节（轻量版 vs 深度版） |
| 3.3 | `.cursor/skills/aidocx-s2-breakdown/SKILL.md` | 加 UI 占比统计辅助输出 |
| 3.4 | `AIDocxWorkFlow.mdc` | 加 `AIDOCX_S3_MODE` 编排开关说明 |

---

## 4. 实施步骤（4 步）

| 步骤 | 动作 |
|------|-----|
| 4.1 | 在 SSOT §4.3 加 `AIDOCX_S3_MODE` 常量（默认值 + 判定规则） |
| 4.2 | 更新 AIDocxWorkFlow.mdc 编排开关章节 |
| 4.3 | 更新 S3 SKILL.md 增加 "模式选择" 章节（轻量 vs 深度产出差异） |
| 4.4 | 更新 S2 SKILL.md 在 Epic 拆解后输出 UI 占比统计（供 S3 判定用） |

---

## 5. 验收标准

- [ ] 纯后端需求：自动走轻量版，节省 30%-50% 时间（估算）
- [ ] 含 UI 需求：自动走深度版，UI 节点清单 100% 覆盖
- [ ] 用户可控：`AIDOCX_S3_MODE=depth|lightweight` 环境变量强制切换
- [ ] 阶段契约不破坏：S3 输出文件命名/路径/格式不变，只是内容深度差异
- [ ] 编排开关在 AIDocxWorkFlow.mdc 显式声明

---

## 6. 决策拍板清单（D-V14.5-001~003）

| 决策 | 内容 | 默认 |
|------|-----|-----|
| **D-V14.5-001** | 默认模式是否走轻量版？ | ✅ 默认 lightweight（节省成本） |
| **D-V14.5-002** | UI 占比阈值 = 30%？ | ✅ 30%（外部方案建议值） |
| **D-V14.5-003** | 是否保留 LLM 智能判定？ | ✅ 保留（用户可强制覆盖） |

---

## 落档协议执行记录（§9.5）

- 占位文件 → content 展开：`governance/design_iter/current/v14_5_l1_s3_path_split.md`
- 涉及文件：4 个（SSOT + AIDocxWorkFlow.mdc + S3 SKILL.md + S2 SKILL.md）
- 落地时间：2026-07-14
- 验证：`python3` 4/4 文件全部包含新增内容 + ReadLints 无错误

## 7. 实际改动清单

| # | 文件 | 改动 | 行号 |
|---|------|------|------|
| 1 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | §4.3 加 2 行常量（`AIDOCX_S3_MODE` + `AIDOCX_S3_UI_THRESHOLD`） | 506-507 |
| 2 | `.cursor/rules/AIDocxWorkFlow.mdc` | 编排开关表加 1 行（AIDOCX_S3_MODE） | 21 |
| 3 | `.cursor/skills/aidocx-s3-prototype/SKILL.md` | 新增 "模式选择" 章节（判定 Python + 输出差异表） | 21-47 |
| 4 | `.cursor/skills/aidocx-s2-breakdown/SKILL.md` | 新增 "§v14.5 UI 占比统计" 章节 | 394-414 |
