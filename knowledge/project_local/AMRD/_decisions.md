# AMRD · 项目级决策记录

> **本文件记录 AMRD 项目级 override 与通用库的所有冲突判定 + 决策理由**。
>
> **目的**：所有"override 优先于通用"的判定**必须留痕**——避免静默覆盖通用规则，确保可追溯。

---

## 决策 #1 — 按钮从 8 态砍到 4 态（2026-07-22）

### 决策概述

| 维度 | 内容 |
|------|------|
| **决策时间** | 2026-07-22 |
| **决策人** | 用户（项目发起人）+ ui-expert（草拟）|
| **关联 override** | [`ui/A_button_mobile_4state.md`](./ui/A_button_mobile_4state.md) |
| **关联通用基线** | [`module_templates/UI/A_control_basic.md`](../../public/module_templates/UI/A_control_basic.md) |

### 决策详情

**冲突描述**：
- 通用库：`A_control_basic.md` 定义按钮 8 态（IDLE / HOVERED / FOCUSED / PRESSED / SELECTED / DISABLED / LOADING / DRAGGING）
- AMRD 项目：移动端 touch UI 实际只需要 4 态（IDLE / PRESSED / DISABLED / ACTIONABLE）
- 冲突：通用库的 8 态在 AMRD 项目**不适用**

**决策**：AMRD 项目采用 4 态基线，**override 通用库的 8 态**

**决策理由**：

| 排除状态 | 理由（移动端特有）|
|---------|------------------|
| HOVERED | 手指没有"悬停"——touch-based UI 无此概念 |
| FOCUSED | Tab 焦点在移动端语义弱（外接键盘场景外罕见）|
| SELECTED | 单选/多选由独立组件管（`RadioGroup`/`CheckBox`）|
| LOADING | 按钮不放 loading，用 skeleton/spinner |
| DRAGGING | AMRD 按钮默认不可拖拽 |

**用户原话（决策依据）**：

> *"老 UI，后续会建一些项目级的，非通用的 UI 规则，项目可能会越来越多，所以项目级规定和知识，你要做好管理，比如手游项目 AMRD，他的按钮没有 8 态，8 态是网页的，手游一般只有常态，点击态，置灰，高亮（有奖励可领取等）"*

**风险评估**：

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 平板外接鼠标场景 | HOVERED 可能有用 | 后续若支持平板，回灌到 override 文档 |
| 蓝牙键盘玩家 | FOCUSED 可能有用 | 后续若支持键盘操作，回灌到 override 文档 |
| 跨项目复用 | 其他手游项目可能也需要 4 态 | 引用 ≥ 3 次后提议升格到通用库 |
| 通用库升级 | 通用库可能新增状态 | S5 自动检查项目级 override 是否过期 |

**回灌触发条件**（任一满足）：

1. override 被其他 ≥ 3 个手游项目复用
2. AMRD 项目结项，经验值得沉淀
3. 通用库 8 态理论被推翻（如全行业转向移动端）

---

## 决策 #2 — (TBD) 占位

> 后续 override 与通用库冲突时，按以下格式追加。

```markdown
## 决策 #N — <一句话标题>（YYYY-MM-DD）

### 决策概述
| 维度 | 内容 |
|------|------|
| 决策时间 | YYYY-MM-DD |
| 决策人 | <人> |
| 关联 override | <路径> |
| 关联通用基线 | <路径> |

### 决策详情
**冲突描述**：...
**决策**：...
**决策理由**：...
**用户原话**（如有）：...
**风险评估**：...
**回灌触发条件**：...
```

---

**最后更新**：v1（首个决策记录）
**维护者**：ui-expert（起草） + AMRD 项目 UI owner（TBD 接管）
**关联**：[`v35 project_local_schema`](../../../../governance/design_iter/plans/v35/project_local_schema.md) §3.4