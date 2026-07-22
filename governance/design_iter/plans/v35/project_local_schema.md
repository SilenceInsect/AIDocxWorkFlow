# v35 — 项目级规则库架构（草稿）

> **本文件状态**：🚧 **DRAFT** — 不进入 goal-loop Act 阶段。
>
> **严格基于用户原话**：本文件所有"项目级 vs 通用级"判定都附用户原话引用（**用户原话 ≠ Agent 臆造**）。
>
> **触发场景**：ui-expert 在身份卡 v1（2026-07-22）落地后，用户以 AMRD 项目为例指出"通用规则不能套所有项目"。

---

## 1. 背景与问题陈述

### 1.1 用户原话（关键输入）

> **用户原话 #1（2026-07-22）**：
> *"老 UI，后续会建一些项目级的，非通用的 UI 规则，项目可能会越来越多，所以项目级规定和知识，你要做好管理，比如手游项目 AMRD，他的按钮没有 8 态，8 态是网页的，手游一般只有常态，点击态，置灰，高亮（有奖励可领取等）你懂的我说的是大白话，而你要规整成条理清楚的专业术语"*

### 1.2 从原话拆出的 3 个核心需求

| # | 需求 | 原话锚点 |
|---|------|---------|
| 1 | **项目级规则必须存在** | "后续会建一些项目级的，非通用的 UI 规则" |
| 2 | **通用规则不能套所有项目** | "AMRD 的按钮没有 8 态，8 态是网页的" |
| 3 | **大白话 ↔ 专业术语双向翻译** | "你懂的我说的是大白话，而你要规整成条理清楚的专业术语" |

### 1.3 现状诊断

| 维度 | 现状 | 不足 |
|------|------|------|
| **通用 UI 规则** | `module_templates/UI/`（网页向 8 态为基线）| ✅ 存在 |
| **项目级 override 目录** | ❌ 无 | 治理空缺 |
| **项目级查找顺序** | ❌ 无 | S5 永远先读通用 → 永远用 8 态 |
| **项目级生命周期** | ❌ 无 | 项目死了规则没归档 |
| **回灌机制（项目 → 通用）** | ❌ 无 | 珍贵经验沉淀不到通用库 |
| **大白话 → 术语训练** | ❌ 隐式 | 散在 agent 上下文，无训练样本 |

---

## 2. 目标

| # | 目标 | 验证方式 |
|---|------|---------|
| **G1** | 项目级规则有独立存放目录（不入 git） | `knowledge/project_local/<PROJECT>/` 存在 |
| **G2** | 项目级 override 与通用库明确分离 | 治理违规检查（hook + 人工） |
| **G3** | S5 生成 TP 时**自动优先**项目级 | 查找顺序测试 |
| **G4** | 项目级有完整生命周期（立项 → 运行 → 结项 → 回灌）| 每个项目有 `_lifecycle.md` |
| **G5** | ui-expert 能听懂大白话并翻译成专业术语 | 身份卡训练样本 ≥ 10 条 |
| **G6** | 8 个专家统一支持项目级（CONFIG / UI / BIZ / UTIL / LINK / SPECIAL / LOG / HINT）| 模式一致 |

---

## 3. 架构设计

### 3.1 3 层规则库

```
knowledge/
├── public/module_templates/                 ← 通用规则层（SSOT，入 git）
│   ├── UI/                                  ← 通用 UI 模板（网页 8 态为基线）
│   ├── BIZ/ ... UTIL/ ... LOG/ ... HINT/ ... LINK/ ... SPECIAL/ ... CONFIG/
│   └── ❌ 禁止放任何项目级 override（治理违规）
│
├── project_local/                            ← 项目级私有层（不入 git）
│   └── <PROJECT_CODE>/                       ← 按项目代号分（如 AMRD / MP01）
│       ├── _README.md                        ← 项目基本盘
│       ├── _lifecycle.md                     ← 立项/运行/结项/回灌状态
│       ├── _decisions.md                     ← override 决策记录（与通用冲突时的判定）
│       ├── ui/                               ← 项目级 UI 规则
│       │   ├── _rules.md                     ← 入口索引
│       │   ├── A_button_mobile_4state.md     ← AMRD 4 态按钮 override
│       │   └── _excluded_states.md           ← 主动排除的通用规则 + 理由
│       ├── biz/ ... UTIL/ ...                ← 其他模块项目级
│       └── ...
│
└── (public) 治理方案 → governance/design_iter/plans/vN/    ← 治理 SSOT（不入 git）
```

### 3.2 目录权限矩阵（v35 新增）

| 路径 | 通用 Agent | ui-expert（UI 模块） | 项目 owner | 治理违规（hook） |
|------|----------|---------------------|-----------|----------------|
| `public/module_templates/UI/*` | ❌ 仅候选 | ✅ 直写（**专家特权**）| ⚠️ 需走候选 + ui-expert 审核 | ❌ 严格保护 |
| `public/module_templates/UI/_candidates/*` | ✅ | ✅ | ✅ | ✅ 允许 |
| `project_local/<PROJECT>/_README.md` | ⚠️ 需项目 owner 授权 | ⚠️ 需项目 owner 授权 | ✅ 创建 | ⚠️ 项目级私有 |
| `project_local/<PROJECT>/ui/*` | ⚠️ 需项目 owner + ui-expert 联合授权 | ✅ 直写（**项目内 UI 专家特权**）| ✅ 提案 | ✅ 允许（项目级不归通用 hook 管）|
| `project_local/<PROJECT>/_decisions.md` | ⚠️ 需项目 owner 签字 | ⚠️ 建议但不擅自 | ✅ 决策权 | ✅ 允许 |

### 3.3 查找顺序（S5 生成 TP 时）

```
输入：项目代号 PROJECT_CODE（如 "AMRD"）+ Story 文本

Step 1: 识别项目代号
  → 从 workflow_assets/<req>/<ver>/「S5」/project_code.txt 读
  → 或从 stage context 的 STAGE_CTX.project_code 读
  → 若识别不出 → fallback 到通用库

Step 2: 读项目级入口
  → 读 knowledge/project_local/<PROJECT>/ui/_rules.md
  → 若不存在 → fallback 到通用库

Step 3: 合并规则（override 优先）
  → 项目级 _rules.md 列出"本项目适用的 override 文档清单"
  → 按清单读 override 文档
  → override 与通用冲突时：
      a. override 优先（项目级有最终解释权）
      b. 记录到 _decisions.md（决策时间 / 决策人 / 决策理由）

Step 4: 生成 TP 时显式标注规则来源
  → TP 字段加 source: "project_local/AMRD/ui/A_button_mobile_4state.md" 或
                  "通用 module_templates/UI/A_control_basic.md"

Step 5: 复盘时主动提议回灌
  → override 文档被引用 ≥ 3 次时，主动问项目 owner：
    "这个 override 是不是通用？要不要走候选区升格到通用库？"
```

### 3.4 大白话 → 专业术语翻译矩阵（v35 落地训练样本）

> **来源**：用户原话 #1（"常态 / 点击态 / 置灰 / 高亮"）

| 用户大白话 | 专业术语（中文）| 英文术语 | 行业标准词 | 状态语义 |
|----------|--------------|---------|----------|---------|
| "常态" / "默认" / "空闲" | **默认态** | `IDLE` | Normal / Resting | 无交互时的常态 |
| "点击态" / "按下" | **按下态** | `PRESSED` | Pressed / Highlighted / Active | 手指按下瞬间的视觉反馈 |
| "置灰" / "不可点" / "灰掉" | **禁用态** | `DISABLED` | Disabled / Inactive | 控件存在但不可交互 |
| "高亮（有奖励可领取）" / "闪烁" / "跳动" | **可行动态** | `ACTIONABLE` | Actionable / Badge Pulse | 控件有效且需引起注意 |
| "鼠标放上去变色" | **悬停态** | `HOVERED` | Hover | 鼠标悬停反馈（**仅网页端**）|
| "Tab 键选中" / "键盘焦点" | **焦点态** | `FOCUSED` | Focus | 键盘焦点（**罕见于移动端**）|
| "选中" / "勾选" / "打钩" | **选中态** | `SELECTED` | Selected | 由 Radio/Check 独立承载 |
| "按钮变 loading" | **状态错误** | (N/A) | — | 按钮不放 loading，用 skeleton/spinner |
| "网页按钮 8 态" | 8 态基线 | `8-State Baseline` | Material Design / Apple HIG | IDLE/HOVERED/FOCUSED/PRESSED/SELECTED/DISABLED/LOADING/DRAGGING |
| "手游按钮 4 态" | 4 态基线 | `4-State Baseline (Mobile)` | iOS HIG / Material Mobile | IDLE/PRESSED/DISABLED/ACTIONABLE |

**为什么是 4 态不是 8 态（移动端）**：

| 8 态里被砍的 | 砍的理由（移动端特有）|
|------------|---------------------|
| `HOVERED` | 手指没有"悬停"——touch-based UI 无此概念 |
| `FOCUSED` | Tab 焦点在移动端语义弱（外接键盘场景外罕见）|
| `SELECTED` | 单选 / 多选由独立组件管（`RadioGroup` / `CheckBox`）|
| `LOADING` | 不是按钮状态——是内容状态（用骨架屏 / spinner）|

---

## 4. 项目生命周期

### 4.1 4 阶段

| 阶段 | 动作 | owner | 产出 |
|------|------|-------|------|
| **1. 立项** | 建 `project_local/<PROJECT>/_README.md` + `<MODULE>/` 空目录 | 项目发起人 | `_README.md` + `_lifecycle.md`（status: active）|
| **2. 运行** | 累计 override 文档 / TP / 决策记录 | 项目 `<MODULE>` owner + ui-expert | override 文档 / `_decisions.md` 增量 |
| **3. 结项** | **复盘**：哪些 override 应该回灌到通用库？ | 项目 owner + ui-expert | `_lifecycle.md`（status: archived）+ 回灌建议清单 |
| **4. 回灌** | 走候选区 → ui-expert 审核 → 升格到通用库 | ui-expert | 通用库 `_candidates/` → 正式库 |

### 4.2 项目基本信息（`_README.md` 必填字段）

```yaml
project_code: AMRD              # 项目代号（唯一，跨模块一致）
project_name: AMRD 手游          # 项目正式名
business_type: 手游              # 业务类型（手游 / 端游 / 电商 / 金融 / ...）
platform: [iOS, Android]         # 平台清单
ui_owner: <人/角色>              # UI 规则 owner
biz_owner: <人/角色>             # 业务规则 owner
status: active                  # active / archived
created_at: 2026-07-22
amrd_rule_examples:
  - "按钮 4 态（IDLE/PRESSED/DISABLED/ACTIONABLE）"
  - "无 hover 语义"
  - "loading 用 skeleton 不放按钮"
```

---

## 5. 实施路径（3 阶段）

### 5.1 Phase 1：架构 + 范式（本周）

- ✅ **本方案 v35 落地**（`governance/design_iter/plans/v35/project_local_schema.md`）
- ✅ **ui-expert 身份卡 v3 增补「🏗️ 项目级规则管理」节**
- ✅ **首个示例**：`knowledge/project_local/AMRD/ui/A_button_mobile_4state.md`
- ✅ **治理规则补强**：`DESIGN_AND_EXECUTION_STANDARDS.mdc` §0.1 加 §0.1.5 "项目级规则库"

### 5.2 Phase 2：其他 7 专家补齐（本月）

- CONFIG / BIZ / UTIL / LINK / SPECIAL / LOG / HINT 7 个专家**各自补 `_identity_card.md`**
- 每个专家**复用本架构**（`<PROJECT>/<MODULE>/_rules.md` 模式一致）
- 每个专家**建立自己的大白话 → 术语样本**（如 BIZ 的"扣款" → "支付/扣款"）

### 5.3 Phase 3：自动化（季度）

- S5 stage_context_builder 自动识别项目代号
- S5 pipeline 自动按查找顺序合并规则
- 项目级 override 引用计数 + 主动回灌提醒

---

## 6. 解决 / 新增 / 遗留（v35 → v36 演进）

### 6.1 解决（v35 已落）

- ✅ 项目级规则有独立目录（`project_local/<PROJECT>/`）
- ✅ 项目级 override 与通用库分离（治理违规检查）
- ✅ 查找顺序明确（Step 1-5）
- ✅ 项目生命周期 4 阶段
- ✅ ui-expert 身份卡有训练样本（10 条大白话 → 术语）
- ✅ 首个项目示例（AMRD）

### 6.2 新增（v35 引入的新概念）

- 🆕 **项目代号（PROJECT_CODE）** 作为项目级目录命名（替代之前的"项目名"）
- 🆕 **大白话 → 专业术语翻译矩阵**（每个专家需维护自己的样本）
- 🆕 **override 优先 + 决策留痕** 机制（避免静默覆盖通用规则）
- 🆕 **项目级查找顺序**（Step 1-5 算法）

### 6.3 遗留（v36 议程）

| ID | 问题 | 优先级 |
|----|------|-------|
| Q-501 | 项目代号如何与 `workflow_assets/<req_name>/` 关联？（目前是两套命名）| P1 |
| Q-502 | S5 stage_context_builder 何时能识别 project_code？（需修改 schema）| P1 |
| Q-503 | override 引用计数如何自动化？（手动计数易遗漏）| P2 |
| Q-504 | 跨项目复用 override 的场景（如 AMRD 的 4 态适用于所有手游）| P1 |
| Q-505 | 项目 owner 与 ui-expert 的权限边界（治理违规风险）| P2 |
| Q-506 | 跨项目 8 态 → 4 态自动转换工具（避免每次手写 override）| P2 |
| Q-507 | 当项目级 owner 离职时，谁接管？| P3 |

---

## 7. 关联引用

| 文件 | 关联 |
|------|------|
| `.cursor/skills/ui-expert/_identity_card.md` | §「🏗️ 项目级规则管理」是本方案的轻量版 |
| `.cursor/MODULES.md` | 8 模块定义（本方案按模块分目录）|
| `governance/design_iter/plans/v34/v34_8role_contracts.md` | 8 角色契约（本方案扩展为项目级维度）|
| `knowledge/public/module_templates/UI/A_control_basic.md` | 通用基线 8 态（被 AMRD override）|
| `knowledge/project_local/AMRD/ui/A_button_mobile_4state.md` | 首个项目级示例 |

---

**最后更新**：v1（DRAFT 草稿）
**作者**：ui-expert（基于用户 2026-07-22 原话起草）
**待审**：人本（用户）审核 → 升格为 v35 stable → 进入 §0.1.5 SSOT