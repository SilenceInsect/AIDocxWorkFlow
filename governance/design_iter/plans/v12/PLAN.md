# AIDocxWorkFlow 方案 v12 — S3/S4→TC 工作流+约束（UI 节点驱动 + BIZ 4 层引用驱动）

> **本方案承接 v11 §3 替代（v11 实战发现：FP 全覆盖 ≠ UI/BIZ 覆盖）+ 用户 2026-07-10 02:02 关键战略指令「UI 相关的用例要根据 S3 的原型图做全覆盖，业务相关的用例要根据 S4 的业务流程和算法、逻辑分支，状态迁移做全覆盖，落地工作流和规则约束」**。
> **核心动作**：4 大议题 = (1) S3/S4 产出丰富化 (2) S3→UI TC 工作流 (3) S4→BIZ TC 工作流 (4) S5/S6 字段溯源重构。
> **版本号说明**：v11 = OBJ+FP 双层覆盖；v12 = **S3/S4→TC 引用驱动工作流**（v11 替代，**v11 知识层标 obsolete，数据暂不重生成**）。

---

## ⚠️ 启动必读：v12 决策清单

> v12 包含 **5 大议题 / 5 子决策**——本档列出全部，决策详情见 `decisions.json`。

| Q 区段 | 议题 | 决策类型 | 候选 | 选择 |
|---|---|---|---|---|
| **Q-V12-001** | v12 与 v11 关系 | 版本策略 | A: 叠加 / B: 替代 / C: 暂停 v11 | **B（v12 完全替代 v11；v11 知识层标 obsolete）** |
| **Q-V12-002** | UI TC 引用粒度 | 引用契约 | A: 3 层 / B: 4 层 / C: 引用 prototype.md 章节 | **用户澄清：prototype.md 中"页面→UI 节点" 已是 TC 的功能点——无需复杂分层；4 字段紧凑（page + 节点 + 操作 + 预期）** |
| **Q-V12-003** | BIZ TC 引用粒度 | 引用契约 | A: 4 层 / B: 1 层 / C: 3 层 | **A（4 层：场景名 + 状态机节点 + 异常决策树叶子 + 风险点 ID）** |
| **Q-V12-004** | BIZ TC 模板边界 | 模板策略 | A: 4 类独立模板 / B: 1 统一模板 / C: 2 类 | **用户批评：不要预设模板边界，AI 能想出来多少就多少——不省 token** |
| **Q-V12-005** | v12 首批交付范围 | 范围决策 | A: 仅 PLAN + SKILL / B: PLAN + SKILL + STAGE_*.mdc / C: 端到端 | **A（PLAN + 4 个 SKILL，不动数据；用户明确"先别修结果，先把流程步骤，内容，标准，约束做到位"）** |

**用户决定（2026-07-10 AskQuestion）**：Q-V12-001=B / Q-V12-002=4字段紧凑 / Q-V12-003=A / Q-V12-004=不限模板 / Q-V12-005=A。

---

## 用户原话关键澄清（v12 核心思想）

> "原型的是界面，界面就是需求对象，界面的UI节点就是功能"
> "什么叫各一个模板，AI能想出来多少就多少，不要省token"
> "S3/S4 都要"
> "先别修结果，先把流程步骤，内容，标准，约束做到位"

**v12 核心思想**：

1. **UI TC 来源**：不是从 S2 OBJ/FP 推导，**直接从 S3 `prototype.md` 的 UI 节点清单推导**——prototype.md 的"页面列表/关键页面布局/组件列表"是 UI 需求的 SSOT
2. **BIZ TC 来源**：不是从 S2 OBJ/FP 推导，**直接从 S4 `business_flow.md` 的 4 层引用推导**——business_flow.md 的"主流程/时序图/异常决策树/状态机"是 BIZ 需求的 SSOT
3. **不要预设模板边界**：LLM 按场景+状态+异常+风险穷举所有可能 TC 类型——不预设"4 类模板"或"1 类模板"
4. **先建流程+规则再做数据**：本轮（Phase 6.5 末）只交付 v12 PLAN + 4 个 SKILL，**不动 S5/S6 数据**

---

## v{N} 必备 3 栏

### 1. 本次 v12 解决的问题（来自 v11 §3 替代 + 用户指令）

#### 来自 v11 实战发现

- ✅ **v10-LEFTOVER-006**：HINT OBJ ID 命名规则（v12 §v12-LEFTOVER-001 跟踪）
- ⚠️ **v11 实战发现**：FP 全覆盖 ≠ UI/BIZ 全覆盖——S5 87/87 FP 覆盖、38 TC 全部带 s5_ref，但 UI TC 没引用 S3 prototype.md 中的页面布局/UI 节点；BIZ TC 没引用 S4 业务流图/状态机/异常决策树
- ⚠️ **跨阶段引用断**：S5/S6 不知道 prototype.md 有哪些页面/UI 节点（因为 S3 SKILL 没强制输出"UI 节点清单"）
- ⚠️ **S4 输出未结构化**：business_flow.md 的 Mermaid 图是给人看的，不是给 LLM/脚本消费的——缺少"状态机表 + 异常树叶子列表"的结构化产出

#### 来自用户 2026-07-10 02:02 指令

> 「UI 相关的用例要根据 S3 的原型图做全覆盖，业务相关的用例要根据 S4 的业务流程和算法、逻辑分支，状态迁移做全覆盖，落地工作流和规则约束。先别修结果，先把流程步骤，内容，标准，约束做到位」

**解读**：
- **UI TC 全覆盖**：以 S3 prototype.md 为唯一来源（页面 → UI 节点 → TC）
- **BIZ TC 全覆盖**：以 S4 business_flow.md 为唯一来源（场景 → 状态机 → 异常 → 风险 → TC）
- **落地工作流 + 规则约束**：4 个 SKILL.md 必须把流程步骤 + 内容标准 + 字段约束写清楚
- **先别修结果**：本轮不动 S5/S6 数据，只建规则

### 2. 本次 v12 新增内容

#### Phase 6.1: 知识层（governance/PLAN.md）—— 本档

- ✅ v12 启动决策表（Q-V12-001 ~ Q-V12-005）
- ✅ 3 栏框架
- ✅ S3→UI TC 工作流 + S4→BIZ TC 工作流 + L3 拍点脚本契约

#### Phase 6.2: v11 知识层 obsolete 标注

- 🔄 `governance/design_iter/plans/v11/PLAN.md` 顶部加 "**已被 v12 替代**" banner
- 🔄 `governance/design_iter/plans/v11/decisions.json` 加 `obsoleted_by: "v12"` 字段
- 🔄 `governance/design_iter/plans/v11/q_decision_table.md` 加废弃说明

#### Phase 6.3: S3/S4 SKILL.md 批改（产出丰富化 + L3 拍点脚本契约）

- 🔄 `.cursor/skills/aidocx-s3-prototype/SKILL.md` 加 §UI 节点清单强制输出条款
- 🔄 `.cursor/skills/aidocx-s4-flowchart/SKILL.md` 加 §状态机表+异常树叶子列表强制输出条款
- 🔄 `ai_workflow/s3_extract_ui_nodes.py`（新增 L3 脚本）：从 prototype.md 自动拍出 UI 节点清单 JSON
- 🔄 `ai_workflow/s4_extract_state_and_exceptions.py`（新增 L3 脚本）：从 business_flow.md 自动拍出状态机迁移表 + 异常决策树叶子列表 JSON

#### Phase 6.4: S5/S6 SKILL.md 批改（S3 ref/S4 ref 字段 + 4 层引用）

- 🔄 `.cursor/skills/aidocx-s5-test-points/SKILL.md` 替换 §v11 FP 必填条款为 §v12 S3 ref + S4 ref 字段溯源
- 🔄 `.cursor/skills/aidocx-s6-test-cases/SKILL.md` 加 §UI TC 4 字段模板 + §BIZ TC 4 层引用模板（不预设边界）

#### Phase 6.5: 现状交付（不动数据）

- 🔄 4 个 SKILL.md 已批改完成 + 2 个 L3 拍点脚本已建
- 🔄 S5/S6 数据暂不动（用户明确"等规则调整到位再处理"）

### 3. 本次 v12 仍遗留的问题（→ v13 解决）

- ❓ **v12-LEFTOVER-001**：HINT OBJ ID 命名规则（v10 遗留，跟踪）
- ❓ **v12-LEFTOVER-002**：UI TC 的 UI 节点覆盖率 = prototype.md 的 UI 节点数？脚本拍点的"UI 节点"定义与 LLM 拍的"UI 节点"对不上怎么办
- ❓ **v12-LEFTOVER-003**：BIZ TC 4 层引用——LLM 推理出的"场景名" vs S4 business_flow.md 中的"场景名"对不上如何容错
- ❓ **v12-LEFTOVER-004**：LOG/SPECIAL/LINK/CONFIG 4 类模块（非 UI/非 BIZ）——v12 没有覆盖规则，下轮补充
- ❓ **v12-LEFTOVER-005**：现有 38 TC 是否按 v12 标准回炉重审——用户明确"先别修结果"，所以下轮再决定

---

## v12 核心设计：S3/S4→TC 工作流

### 工作流 1：S3 prototype.md → UI TC（UI 模块）

```
S3 prototype.md 产出（按 S3 SKILL.md 强制规范）
 ↓ 包含：
 ├─ 页面清单（如：商城首页/道具详情页/订单确认页/支付页/购买成功页...）
 ├─ 关键页面布局（每个页面的 UI 节点列表）
 └─ 状态机/弹窗状态机
 ↓
L3 脚本 s3_extract_ui_nodes.py 拍点
 ↓ 输出：ui_nodes.json
 ├─ pages: [{page_id, page_name, nodes: [{node_id, node_type, ...}]}]
 ├─ page_flow: Mermaid 流图（保留）
 └─ page_states: {page_id: {state_id: trigger}}
 ↓
S5 TP 生成（S5 SKILL.md §S3 ref 字段溯源）
 ├─ 每个 UI TP 带 s3_ref: page_id
 ├─ 每个 UI TP 带 ui_node_ref: node_id
 └─ 每个 UI TP 带 ui_state_ref: state_id (optional)
 ↓
S6 UI TC 生成（S6 SKILL.md §UI TC 4 字段模板）
 ├─ page_id (必填, prototype.md 页面 ID)
 ├─ node_id (必填, 拍点的 UI 节点 ID)
 ├─ 操作 (必填, LLM 推理: 点击/输入/滑动/...)
 └─ 预期 (必填, LLM 推理: 界面状态变更/数据提交/弹窗弹出...)
 ↓
覆盖率校验（v12 L3 兜底脚本）
 ├─ ui_node_linkage_coverage = TC 引用的 UI 节点数 / prototype.md UI 节点数 ≥ 1.0
 └─ ui_page_coverage = TC 引用的页面数 / prototype.md 页面数 ≥ 1.0
```

### 工作流 2：S4 business_flow.md → BIZ TC（BIZ 模块）

```
S4 business_flow.md 产出（按 S4 SKILL.md 强制规范）
 ↓ 包含：
 ├─ 主流程 Mermaid 图（步骤 + 决策）
 ├─ 时序图（actor 间调用）
 ├─ 异常决策树（每个异常决策树的叶子节点）
 ├─ 状态机（Mermaid stateDiagram）
 └─ 风险点清单（risk_id + 描述 + 缓解策略）
 ↓
L3 脚本 s4_extract_state_and_exceptions.py 拍点
 ↓ 输出：s4_state_and_exceptions.json
 ├─ scenarios: [{scenario_id, scenario_name, steps: [...]}]
 ├─ state_machines: [{machine_id, states, transitions: [{from, to, trigger, guard}]}]
 ├─ exception_trees: [{tree_id, leaves: [{leaf_id, condition, action}]}]
 └─ risk_points: [{risk_id, risk_desc, mitigation}]
 ↓
S5 BIZ TP 生成（S5 SKILL.md §S4 ref 字段溯源）
 ├─ 每个 BIZ TP 带 s4_ref: {scenario, state, exception_leaf, risk}
 └─ 4 层引用任一必填
 ↓
S6 BIZ TC 生成（S6 SKILL.md §BIZ TC 4 层引用模板）
 ├─ scenario_id (必填, S4 scenario)
 ├─ state_transition (选填, from→to + trigger)
 ├─ exception_leaf_ref (选填, 异常决策树叶)
 ├─ risk_point_ref (选填, 风险点 ID)
 └─ 不预设模板边界——LLM 按场景自由组合
 ↓
覆盖率校验（v12 L3 兜底脚本）
 ├─ scenario_coverage = TC 引用的 scenario 数 / S4 scenario 数 ≥ 1.0
 ├─ state_machine_coverage = TC 引用的 state 数 / S4 state machine state 数 ≥ 1.0
 ├─ exception_tree_coverage = TC 引用的 exception leaf 数 / S4 exception leaf 总数 ≥ 1.0
 └─ risk_point_coverage = TC 引用的 risk 数 / S4 risk 总数 ≥ 1.0
```

### 关键：UI 模块 vs BIZ 模块 vs 其他模块

| 模块 | 引用源 | 引用层 | v12 模板 |
|---|---|---|---|
| **UI** | S3 prototype.md | 4 字段（page + node + 操作 + 预期）| §工作流 1 |
| **BIZ** | S4 business_flow.md | 4 层（scenario + state + exception + risk）| §工作流 2 |
| **CONFIG** | S2 OBJ + FP（沿用 v10） | obj_id + feature_point_id | 暂不纳入 v12（v12-LEFTOVER-004）|
| **LINK** | 同 CONFIG | 同 CONFIG | 暂不纳入 v12 |
| **LOG** | 同 CONFIG | 同 CONFIG | 暂不纳入 v12 |
| **SPECIAL** | 同 CONFIG | 同 CONFIG | 暂不纳入 v12 |
| **HINT** | 同 CONFIG + S3 部分（Toast/飘字属于 UI 节点）| 混合 | 暂不纳入 v12 |

---

## L3 拍点脚本契约

### s3_extract_ui_nodes.py

```python
def extract_ui_nodes(prototype_md_path: Path) -> dict:
    """从 prototype.md 自动拍出 UI 节点清单 + 页面状态机。
    
    输出结构：
    {
      "pages": [
        {"page_id": "P-001", "page_name": "商城首页", "nodes": [...]}
      ],
      "page_flow": "<Mermaid flowchart>",
      "page_states": {
        "P-001": {"normal": null, "loading": "load_trigger", "error": "..."}
      }
    }
    """
    ...
```

### s4_extract_state_and_exceptions.py

```python
def extract_state_and_exceptions(business_flow_md_path: Path) -> dict:
    """从 business_flow.md 自动拍出状态机迁移表 + 异常决策树叶子列表。
    
    输出结构：
    {
      "scenarios": [...],
      "state_machines": [...],
      "exception_trees": [...],
      "risk_points": [...]
    }
    """
    ...
```

---

## 关键引用

| 内容 | 路径 |
|---|---|
| v11（已废弃）| `governance/design_iter/plans/v11/PLAN.md` |
| v12 决策清单 | `governance/design_iter/plans/v12/decisions.json` |
| v12 启动决策表 | `governance/design_iter/plans/v12/q_decision_table.md` |
| v12 遗留问题 | `governance/design_iter/plans/v12/open_questions.md` |
| S3 SKILL（待改）| `.cursor/skills/aidocx-s3-prototype/SKILL.md` |
| S4 SKILL（待改）| `.cursor/skills/aidocx-s4-flowchart/SKILL.md` |
| S5 SKILL（待改）| `.cursor/skills/aidocx-s5-test-points/SKILL.md` |
| S6 SKILL（待改）| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` |
| L3 拍点脚本（新增）| `ai_workflow/s3_extract_ui_nodes.py` + `ai_workflow/s4_extract_state_and_exceptions.py` |
| 当前 S3 产物 | `workflow_assets/游戏道具商城系统/v3.01/「S3 原型导出」/prototype.md`（13 页面）|
| 当前 S4 产物 | `workflow_assets/游戏道具商城系统/v3.01/「S4 流程图导出」/business_flow.md`（6 流程图 + 4 风险点）|
| 当前 S5 产物 | `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json`（94 TP）|
| 当前 S6 产物 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`（38 TC，FP 覆盖率 100%）|

---

## 执行记录（待补充）

> 本节在 v12 执行过程中追加，记录每阶段实际改动文件清单。