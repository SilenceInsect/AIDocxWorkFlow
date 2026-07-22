---
name: aidocx-s3-prototype
description: >
  AIDocxWorkFlow Stage 3 — 原型导出。根据 S2 Epic/Story 列表生成页面原型（文本描述 + Mermaid 页面流图）。使用当用户执行 /aidocx-s3-prototype、粘贴 S2 backlog、或进行 S3 原型导出任务。
  Use when the user runs /aidocx-s3-prototype, pastes S2 backlog, or starts prototype export.
  使用当用户执行 /aidocx-s3-prototype、粘贴 S2 backlog、或进行 S3 原型导出任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s3-prototype
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S3 — 原型导出

**独立阶段**：可单独调用。上游材料（S2 backlog）审查合格后开始，失败写失败报告。

---

## 模式选择

> **SSOT**：`.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 `AIDOCX_S3_MODE`

S3 支持两种模式，按需切换：

| 模式 | 触发条件 | 产出深度 | 适用场景 |
|------|---------|---------|---------|
| **lightweight** | `AIDOCX_S3_MODE=lightweight` | 页面清单 + 核心流图 | 纯后端需求 / 轻 UI |
| **depth**（默认） | 未设置环境变量（**默认 v16+**）| 页面清单 + 完整 UI 节点清单 + 交互状态机 + Mermaid | **默认模式，S5/S6 UI 节点锚点** |

**判定规则**（LLM 在 S2 → S3 切换时执行）：

```python
import os

# v16+ 默认 depth，lightweight 需要显式强制
forced = os.environ.get("AIDOCX_S3_MODE")
if forced == "lightweight":
    mode = "lightweight"
else:
    # 默认 depth（S5/S6 需要 UI 节点锚点）
    mode = "depth"
```

**决策树（判定流程图示）**：

```
开始
  ↓
A. 用户强制 lightweight？ → AIDOCX_S3_MODE=lightweight → lightweight（强制）
  ↓ 否
B. 默认 → depth（强制）
```

> **v16+ 变更**：默认 depth，lightweight 需要 `AIDOCX_S3_MODE=lightweight` 显式强制。
> **原因**：S5/S6 生成测试用例需要引用 UI 节点 ID，S3 不可跳过。

**输出差异**：

- **depth 版（默认）**：在 lightweight 基础上**必须**追加 `§UI 节点清单`（见下方 §输出）
- **lightweight 版**：`prototype.md` 仅含 §3 关键页面布局 + §4 Mermaid 页面流图

> ⭐ **v16+ 推荐默认 depth**：S5/S6 测试用例生成需要引用 UI 节点 ID，depth 模式的 UI 节点清单是 S5/S6 的锚点来源。

---

## 阶段入口

**触发**：`/aidocx-s3-prototype` 或粘贴 S2 backlog

**前置材料**：S2 backlog.md：`workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.md`

**材料缺失时**：生成失败报告，停止 S3。

---

## §1.4 LLM 必读材料（阶段前置）

**生成原型前，必须先 Read 以下材料。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| 1 | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| UI 模块 Story 对应页面原型；其他模块 Story 生成文本描述 |
| 2 | S2 backlog | `workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.md` | 每个 Story 的功能点是原型生成的核心输入 |

---

## §5 一致性检查（SKILL ↔ Rule 自动对齐）

> **触发时机**：本节读取后、正式执行前。**仅执行一次**（同一次对话中多次触发本阶段，不重复检查）。

**检查类型**：A = 必读材料对齐 / B = 输出路径对齐 / C = 字段名对齐 / D = 模块枚举对齐

```python
from ai_workflow.consistency_check import run_consistency_check

result = run_consistency_check(stage="s3")
if not result["passed"]:
    print(f"[一致性检查] 发现 {len(result['issues'])} 个问题（见日志）")
```

检查结果不阻断阶段执行，仅输出到日志供人工参考。

---

## 核心任务

为每个 Story 生成：
1. **文本原型**：页面原型（含关键 UI 元素、状态变化）
2. **Mermaid 页面流图**：页面之间的导航关系

### 原型内容要求

| 要素 | 内容 |
|------|------|
| 页面名称 | 明确的页面/面板名称 |
| 关键UI元素 | 按钮、输入框、显示区、指示器 |
| 布局描述 | 从上到下或从左到右 |
| 状态变化 | 默认、加载中、错误、成功、禁用 |
| 测试隔离点 | 需要特殊状态（如登录态、冷却时间） |

每个 Epic 至少 1 个完整页面流。

### §v12 UI 节点清单强制输出（v12+ 必填）

> **SSOT**：本节是 v12 §S3→TC 工作流的产品化条款。配合 `.cursor/skills/aidocx-s6-test-cases/SKILL.md` §v12 UI TC 4 字段模板使用。

#### 强制要求

`prototype.md` 在"关键页面布局"节（§3）后**必须**新增"§UI 节点清单"小节，**每个页面**给出结构化 UI 节点列表：

```markdown
### UI 节点清单

#### P-001 商城首页
- 顶部: [搜索框] [分类导航(武器/时装/坐骑/消耗品/礼包)]
- 中部: [热门推荐列表(前10个,按销量)]
- 下部: [分页列表(每页20个,道具卡片N)]
- 弹窗: 无
- 状态: 默认 / 加载中 / 错误

#### P-002 道具详情页
- 顶部: [道具图] [名称] [描述]
- 中部: [属性加成] [价格]
- 数量: [选择器(1-99)]
- 底部: [购买按钮]
- 弹窗: 无
- 状态: 默认 / 余额不足(置灰)
```

**UI 节点类型枚举**（v12 起固定）：
- `button` - 按钮（购买/确认/取消/搜索/支付）
- `input` - 输入框（数量/搜索关键字）
- `display` - 显示区（属性/价格/订单号）
- `list` - 列表（道具/订单/分类）
- `navigator` - 导航（分类切换/Tab/面包屑）
- `dialog` - 弹窗（确认/提示/Loading）
- `indicator` - 指示器（VIP徽章/库存/红点）

#### LLM 自检 3 步走

1. **列页面**：从 S2 Story 推出所有 UI 关联页面
2. **列节点**：每个页面的 UI 元素逐项列出（按钮/输入框/列表/弹窗）
3. **拍状态**：每个节点在默认/加载/错误/禁用等状态下的可访问性

#### 节点 ID 命名规范

```
{page_id}-{node_type}-{node_seq}
例：P-002-button-01（道具详情页的购买按钮）
例：P-002-input-01（道具详情页的数量选择器）
```

#### 与 L3 拍点脚本的衔接

`ai_workflow/s3_extract_ui_nodes.py` 脚本会从 `prototype.md` §UI 节点清单节拍出 `ui_nodes.json`，供 S6 引用。**LLM 必须严格按上述格式输出**——否则 L3 脚本无法解析。

### §v12 LLM 推理态度

- **不预设模板边界**：UI TC 类型由 LLM 按页面+节点穷举所有可能（点击/输入/滑动/选择/触发等操作 + 默认/加载/错误/禁用等状态）
- **质量优先于数量控制**：LLM 想出多少 UI TC 就多少——"不要省 token"

---

## 成功产出

路径：`workflow_assets/<req_name>/<version>/「S3 原型导出」/prototype.md`

---

## 失败报告

路径：`workflow_assets/<req_name>/<version>/「S3 原型导出」/fail_report_S3.md`

---

## 自动化支持

```python
from ai_workflow.conversation_skills import save_stage3_output
save_stage3_output(version, breakdown, raw_output, req_name)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S3_PROTOTYPE.mdc`
- Prompt 模板：`ai_workflow/prompts/prototype_export.md`

---

## 执行卡（v14 单阶段执行卡 — 4 区块合一）

<aside data-exec-card-block="input_gate" data-src=".cursor/rules/STAGE_S3_PROTOTYPE.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

> ⚠️ **派生产物，禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成
> src: `.cursor/rules/STAGE_S3_PROTOTYPE.mdc` | synced_at: `2026-07-14`
> 修改请改源文件，然后跑 `python3 scripts/sync_execution_cards.py --stage s3-prototype` 重新同步。

### 输入门禁（input_gate）

| 必备材料 | 路径 | 缺失处理 |
|---|---|---|
| S2 backlog.md | `workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.md` | 生成 fail_report_S3.md，停止 |
| Epic ≥ 1 + Story 有 acceptance_criteria | backlog 内容审查 | backlog 无 Epic → fail_report_S3.md |

**触发命令**：`/aidocx-s3-prototype` 或粘贴 S2 backlog

</aside>

<aside data-exec-card-block="field_required" data-src=".cursor/rules/STAGE_S3_PROTOTYPE.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### 必填字段（field_required）

| 字段 | 级别 | 校验 |
|---|---|---|
| 每个 Story 的页面名称 / 关键UI元素 / 布局描述 / 状态变化 | **MUST** | 每个 Story 必须有对应原型 |
| Mermaid 页面流图 | **MUST** | 每个 Epic 至少 1 个完整页面流 |
| `prototype.md` 输出文件 | **MUST** | 含文本原型 + Mermaid |

</aside>

<aside data-exec-card-block="quality_gate" data-src=".cursor/rules/STAGE_S3_PROTOTYPE.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### 质量门禁（quality_gate）

| 门禁 | 阈值 | 说明 |
|---|---|---|
| 文本原型 | 每个 Story ≥ 1 个页面原型 | 页面名 / UI元素 / 状态变化齐全 |
| Mermaid 语法 | 合法 | `python3 -m py_compile` 验证 markdown 内 mermaid 块 |
| 页面流完整性 | 每个 Epic ≥ 1 个页面流 | 页面导航关系完整 |

**SSOT**：`DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.3

</aside>

<aside data-exec-card-block="naming" data-src=".cursor/rules/STAGE_S3_PROTOTYPE.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### ID 命名规范（naming）

| 产物 | 格式 |
|---|---|
| 原型文档 | `prototype.md` |
| JSON 结构化 | `prototype.json`（可选） |
| 输出目录 | `workflow_assets/<req_name>/<version>/「S3 原型导出」/` |

</aside>