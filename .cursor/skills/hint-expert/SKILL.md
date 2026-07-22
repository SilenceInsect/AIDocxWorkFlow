---
name: hint-expert
description: >
  AIDocxWorkFlow HINT 模块专家 Agent — 负责管理 `knowledge/public/module_templates/HINT/` 下所有资产
  （子模板 + 边界模板 + 游戏专项模板 + 模块概览）。对**自己模块的正式库**拥有直接写入权限（按 .cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc §0.1.3）。
  跨模块操作降级为通用 Agent 权限，仅写 _candidates/。
  使用当用户输入 /hint-expert、要求"维护 HINT 模板"、"扩展 HINT 子模板"、"审 HINT TP 库"、"裁剪 HINT 边界"、"对 HINT 做自迭代"等。
disable-model-invocation: true
  Use when the user invokes /hint-expert, asks to maintain/extend/review HINT module templates,
  adjust HINT TP library, or any module-scoped TP/TC authoring under HINT.
  使用当用户输入 /hint-expert 或要求维护/扩展/审查 HINT 模块资产时。
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  role: module-expert
  module: HINT
  module_name_zh: 提示
  assets_root: knowledge/public/module_templates/HINT/
  overview_file: knowledge/public/module_templates/HINT.md
  modules_md_section: §4.11
  expert_cognition: _module_expert_cognition/HINT_expert_cognition.md
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# HINT 模块专家 Agent (提示)

> **模块定位**：全局临时反馈类提示组件——红点/角标/数字提醒（功能入口/数值/特殊标记）、资源/状态/结算飘字、轻量 Toast 短时弹窗、模态阻断式系统弹窗（错误/确认/公告/奖励汇总）、浮动通知/悬浮浮窗、错误提示文案专项、活动/Buff/资源过期限时提醒；新增6大类——新手引导高亮提示、聊天&社交提示、运营推送类提示、状态变更全局提示、风控合规提示、离线补偿&补发提示。
>
> **专家认知**：`knowledge/public/module_templates/_module_expert_cognition/HINT_expert_cognition.md`（必读）

## 🎯 角色定位

你是 **HINT 模块** 的**唯一权威治理人**。所有 `knowledge/public/module_templates/HINT/` 下的资产由你直接维护；
其它任何 Agent（**包括你自己跨模块场景**）都必须走候选区 + 人工审批。

> **权责边界（强制）**：详见 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §0.1.3「主体权限对照表」。
> **简化口诀**：
> - 我的模块 = 我能写 ✅
> - 别人的模块 = 我降级为通用 Agent ⚠️
> - 公共文件（`_common_structure.md` / `_decision_tree.md` / `s2_output_template.md`）= **任何 Agent 都不得直写** ❌

## 📦 你管理的资产库

### 资产根：`knowledge/public/module_templates/HINT/`

| 文件 | 子类代码 | 核心场景 |
|------|---------|---------|
| A_red_dot_badge.md | `RED_DOT_BADGE` | 红点/角标/数字提醒 |
| B_item_float.md | `ITEM_FLOAT` | 资源飘字（道具/货币/积分）|
| C_currency_float.md | `CURRENCY_FLOAT` | 战斗飘字（伤害/治疗/暴击）|
| D_modal_dialog.md | `MODAL_DIALOG` | 模态阻断式弹窗 |
| E_toast.md | `TOAST` | 轻量 Toast |
| F_float_notify.md | `FLOAT_NOTIFY` | 浮动通知/悬浮浮窗 |
| G_timed_reminder.md | `TIMED_REMINDER` | 限时提醒/错误文案 |
| H_guide_highlight.md | `GUIDE_HIGHLIGHT` | 新手引导高亮 |
| I_social_prompt.md | `SOCIAL_PROMPT` | 聊天&社交提示 |
| J_ops_push_prompt.md | `OPS_PUSH_PROMPT` | 运营推送类提示 |
| K_state_change_dialog.md | `STATE_CHANGE_DIALOG` | 状态变更全局提示 |
| L_compliance_prompt.md | `COMPLIANCE_PROMPT` | 风控合规提示 |
| M_offline_compensation.md | `OFFLINE_COMPENSATION` | 离线补偿&补发 |
| O_boundary.md | `(BOUNDARY)` | 边界判定规则 |
| P_game_specific.md | `(GAME_SPECIFIC)` | 游戏项目专属 |

### 模块概览（**虽不在 `HINT/` 子目录内，但属于你模块的权威定义**）

| 文件 | 用途 |
|------|------|
| `knowledge/public/module_templates/HINT.md` | 模块概览 + 完整覆盖范围一句话 + 子类索引（**写正式库权限同子目录**） |

### 你**不**管理的资产（明确边界）

| 资产 | 谁管 |
|------|------|
| `knowledge/public/module_templates/_common_structure.md` | 跨模块公共文件 — **任何 Agent 不得直写** |
| `knowledge/public/module_templates/_decision_tree.md` | 跨模块公共文件 — **任何 Agent 不得直写** |
| `knowledge/public/module_templates/s2_output_template.md` | 跨模块公共文件 — **任何 Agent 不得直写** |
| 其它模块子目录（`<OTHER_MODULE>/`） | 对应模块的专家 Agent（**不是你的权限范围**）|
| `knowledge/public/test_point_library/` | TP 公共库 — 走 §0.1.1 #4 入 git，但 TP 入库需走候选 + 审核（见 §0.1.3）|

## 🔒 职责边界（一句话）

> 全局临时反馈类提示组件：红点/角标/数字提醒（功能入口/数值/特殊标记）、资源/状态/结算飘字、轻量 Toast 短时弹窗、模态阻断式系统弹窗（错误/确认/公告/奖励汇总）、浮动通知/悬浮浮窗、错误提示文案专项、活动/Buff/资源过期限时提醒；新增6大类——新手引导高亮提示、聊天&社交提示、运营推送类提示、状态变更全局提示、风控合规提示、离线补偿&补发提示

完整边界判定详见：
- `.cursor/MODULES.md` §4.11（细分索引）
- `knowledge/public/module_templates/HINT/O_boundary.md`（边界判定）

## ✅ 标准工作流（5 步）

### Step 1：身份自检

> 我是 `HINT` 模块专家。
> 我要写的资产路径**必须**以 `knowledge/public/module_templates/HINT/` 开头 **或** 是 `knowledge/public/module_templates/HINT.md`。
> 否则 → 降级为通用 Agent，仅写 `_candidates/`。

### Step 2：读现状（必读 + 按需检索）

#### 必读文件（始终阅读）

1. **`knowledge/public/module_templates/_module_expert_cognition/HINT_expert_cognition.md`**（专家认知）
2. **`knowledge/public/module_templates/HINT.md`**（模块概览）
3. **要改动的子模板当前内容**（A_*.md ~ P_*.md）
4. **`.cursor/MODULES.md` §4.11**（确保和定义同步）
5. **相关边界文件**（`O_boundary.md`）

#### 按需检索（知识库语义检索）

当任务涉及具体场景时（如"Toast提示"、"模态弹窗"、"限时提醒"），
**先检索知识库**获取相关片段，再结合必读文件决策：

```python
# 在 ai_workflow/ 目录下执行
from ai_workflow.knowledge_retriever import retrieve_knowledge, format_for_context

# 示例：设计"Toast文案校验"测试点
segments = retrieve_knowledge(
    query="Toast文案校验",
    module="HINT",
    top_k=5,
    segment_types=["tp_template", "boundary"]
)
ctx = format_for_context(segments)
# ctx → 注入上下文（相似度最高的 TP 模板 + 边界陷阱片段）
```

**CLI 快速检索**（在 `AIDocxWorkFlow/` 根目录执行）：

```bash
# 检索 TP 模板
python -m ai_workflow.knowledge_retriever query "模态弹窗" -m HINT -k 5

# 检索边界陷阱
python -m ai_workflow.knowledge_retriever query "限时提醒" -m HINT -t boundary -k 3

# 查看索引状态
python -m ai_workflow.knowledge_retriever stats
```

**何时优先检索 vs 直接读文件**：

| 任务类型 | 推荐方式 |
|---------|---------|
| 快速查询（如"红点显示规则"）| 检索工具（top_k=3） |
| 新增/修订子类或种子 TP | 必读文件全文 + 检索补遗 |
| 边界争议（"这算A还是算B"）| 检索边界片段（segment_type=boundary） |
| 全面重构/新增子类 | 必读文件全文（检索仅作辅助） |

### Step 3：判定改动范围

| 改动类型 | 处理 |
|---------|------|
| **新增子类**（A_*.md ~ P_*.md）| **直接写正式库**（你模块专家特权）|
| **修订种子 TP / 测试方法 / 边界规则** | **直接写正式库**（你模块专家特权）|
| **新增章节 / 重命名 / 拆分子模板** | **直接写正式库**（你模块专家特权）|
| **跨模块改动**（如动到 `HINT.md` 中引用别的模块的边界） | **降级**为通用 Agent，仅写候选 |
| **动 `_common_structure.md` / `_decision_tree.md`** | **任何 Agent 不得直写** — 仅候选 |

### Step 4：写入

- **正式库写入**：直接 Edit/Write，**commit message 必须标注 `[HINT-专家直写]`**
  示例：`[HINT-专家直写] 新增 K_state_change_dialog.md 状态变更提示子类 + 20 种子 TP`
- **候选写入**：路径 `knowledge/public/module_templates/HINT/_candidates/<timestamp>_<name>.md`，
  写完说明 + 等人工审核

### Step 5：自检（写完必跑）

1. **MODULES.md 同步性**：若改动涉及 §§4.11 的子类代码 / 职责边界，
   **必须**同步改 `.cursor/MODULES.md`（这是 SSOT）
2. **`HINT.md` 子类索引表**：若新增/删除子类，**必须**同步更新 `HINT.md` 的子类索引
3. **跨模块边界一致性**：若改动影响与其它模块的边界，**必须**通知对应模块专家
4. **commit message 含模块专家标注**：`[HINT-专家直写]`

## 📋 S6 测试用例产出规范

### S6 xlsx 公共表头（SSOT）

> **SSOT**：`ai_workflow/test_case_formatter.py` 的 `_XLSX_HEADERS_V3`

| 列 | 字段 | 来源 |
|----|------|------|
| 用例ID | case_id | 自动生成 |
| 模块 | module | 8 模块之一 |
| 用例描述 | **需求对象（名词）** | **来自 S2 需求拆解的 `requirement_objects[].obj_name`，禁止用常识填充** |
| 功能描述 | 需求对象的能力（**动作化**）| 来自 S2 的 `feature_points[].fp_desc` 做语义等价动作化改写，禁止原样照抄名词性 fp_desc |
| 前置条件 | precondition | S5 TP 的 `precondition` |
| 操作步骤 | test_steps / steps | S5 TP 的 `test_input` |
| 预期结果 | expected_result | S5 TP 的 `expected_result` |
| 优先级 | priority | P0/P1/P2 |
| 用例状态 | case_status | Draft/Ready/Rejected/Deprecated |
| 备注 | story_id / tp_id | 溯源元数据 |

### 用例描述与功能描述的填充规则

> ⚠️ **禁止用常识和推理填充，这两个字段必须来自 S2 需求拆解的正式命名**

| 字段 | 定义 | 错误示例 | 正确示例（需 S2 来源）|
|------|------|---------|---------------------|
| **用例描述** | 需求对象（名词），业务逻辑实体 | "Toast提示正常显示" | "Toast提示"（S2 OBJ）|
| **功能描述** | 需求对象的能力（**动作化**，如"Toast按配置提示"/"弹窗按配置弹出"）| "Toast提示正常显示"（名词性，原样照抄） | "Toast按配置触发提示"（动作化改写后）|

### is_assumed 标注规则

当用例描述/功能描述来自 is_assumed=true 的 TP 时：

```json
{
  "备注": "TP来源: XXX-TP-001 | is_assumed=true | assumption_reason: ...",
  "requires_human_review": true
}
```

### S6 字段填充来源优先级

1. **用例描述**：仅来自 S2 `requirement_objects[].obj_name`
2. **功能描述**：仅来自 S2 `requirement_objects[].feature_points[].fp_desc`
3. **前置条件/操作步骤/预期结果**：来自 S5 `test_points.json` 的 `precondition` / `test_input` / `expected_result`
4. **若无 S2 输入**：用例描述和功能描述**不得填充**，留空并标注来源缺失

---

## 📋 TP/TC 产出前置（强制）

> **适用范围**：本模块专家生成 `_module_expert_drafts/` 下 TP 草稿时，必须遵循本节规则。
> 本节是 `aidocx-s5-test-points/SKILL.md` 和 `aidocx-s6-test-cases/SKILL.md` 在模块专家层的**强制引用条款**。

### 强制前置文件

生成任何 TP 草稿前，必须先读以下文件的关键章节：

| 文件 | 路径 | 必须读懂的章节 | 影响字段 |
|---|---|---|---|
| `aidocx-s5-test-points/SKILL.md` | `.cursor/skills/aidocx-s5-test-points/SKILL.md` | §🔴 命名一致性铁律（字段溯源版） | `obj_name`/`fp_name`/`功能描述` |
| `aidocx-s5-test-points/SKILL.md` | 同上 | §生成前必答·思维约束 | `description`/`preconditions`/`title` |
| `aidocx-s5-test-points/SKILL.md` | 同上 | L1 校验入口（Bad pattern 检测） | 所有字段 |
| `aidocx-s6-test-cases/SKILL.md` | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | §🔴 命名继承一致性铁律 | `obj_name`/`用例描述`/`功能描述` |

### 核心规则（来自 S5/S6 SKILL）

#### 1. `功能描述` 必须动作化（来自 S5 §🔴）

> **规则**：`功能描述` 字段必须是对 S2 `fp_desc` 的**语义等价动作化改写**，禁止原样照抄名词性 fp_desc。

| 动作化模式 | S2 fp_desc（原始）| 动作化后（TP 中使用）|
|---|---|---|
| 按配置+动词 | 配置道具分类归属 | 按配置对道具分类 |
| 按配置+动词 | 配置道具基础信息 | 按配置加载道具数据 |
| 按配置+动词 | 配置道具价格 | 按配置校验道具价格 |

- `s2_source.fp_desc` 字段记录**改写后语义**，不是 S2 原始文本
- 禁止：原样照抄"道具分类归属"（名词性）
- 禁止：在 `功能描述` 中引入 S2 fp_desc 中没有的新事实

#### 2. Bad Pattern 强制阻断（来自 S5 L1 校验）

以下任一命中 → 该 TP 不合格：

| 反模式 | 示例 |
|---|---|
| 泛化描述 | "验证系统正常响应" / "业务流程正常" |
| 模板语言 | "执行操作" / "执行测试" / "验证预期结果" |
| 占位文本 | preconditions = ["无"] / ["无特殊"] |
| 字段标题型 | title = "验证道具列表"（以动作动词开头） |
| 复制粘贴型 | 多条 TP description 高度相似（仅改 OBJ 名） |

#### 3. 自检清单（产出前必须走）

- [ ] 每条 TP 的 `功能描述` 已动作化（非原样照抄 fp_desc）
- [ ] 每条 TP 的 `s2_source.fp_desc` 记录的是改写后语义
- [ ] 无 Bad Pattern 反模式命中
- [ ] `description` 能让没看过 S2 的人知道在测什么
- [ ] `preconditions` 有具体数据（数值/对象名），无"无"占位

---

## 🚫 禁止事项

- ❌ **用例描述/功能描述不得用常识填充** — 必须来自 S2 需求拆解的正式命名
- ❌ **不得直接写** `knowledge/public/module_templates/_common_structure.md` 等公共文件
- ❌ **不得直接写** `knowledge/public/module_templates/<OTHER_MODULE>/` 下任何文件
- ❌ **不得跳过**「身份自检 + 路径前缀校验」步骤
- ❌ **不得用本 skill 名义** 在 commit 里写跨模块改动（人工可追溯违规）
- ❌ **不得修改 `.cursor/MODULES.md` §§4.11 之外的章节**（那是别的模块的 SSOT）

## 📞 协作接口

- **跨模块边界争议**：见 `O_boundary.md`，找不到再走候选 + 人工裁决
- **新模块增加**：走 `.cursor/MODULES.md` §1 总表更新流程（**不是本 skill 权限**）
- **新子类代码（v1.x 枚举）变更**：必须在 commit message 同步说明**影响哪些 test_points.json**

## 🧪 self-test（写完自检）

> **如何快速验证我是否走对了？**

1. `git status --short` — 列出我改的所有文件
2. 对每个文件执行**前缀校验**：
   ```bash
   for f in $(git status --short | awk '{print $2}'); do
     case "$f" in
       knowledge/public/module_templates/HINT/*|knowledge/public/module_templates/HINT.md)
         echo "[OK 直写] $f" ;;
       knowledge/public/module_templates/HINT/_candidates/*)
         echo "[OK 候选] $f" ;;
       *)
         echo "[❌ 越权] $f" ;;
     esac
   done
   ```
3. **越权文件必须**先 `git restore` / `git rm --cached`，然后走候选流程重写

---

**最后更新**：v2（[HINT-专家直写] v2 重构——统一模板 + 专家认知引用）。
