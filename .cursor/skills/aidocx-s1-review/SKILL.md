---
name: aidocx-s1-review
description: >
  AIDocxWorkFlow Stage 1 — 需求评审。执行需求文档的5维度评审（完整性/清晰度/一致性/可测试性/可行性），输出评分与判决（PASS/NEEDS_REVISION/REJECT），并对需求做"角色定义 → 需求对象 → 功能 → 业务故事"拆解，打上 8 模块分类标签，同时汇总待人工审核的"问题需求"作为 S1.5 的准入物料。使用当用户执行 /aidocx-s1-review、附带原始需求文件（.docx / .md / .txt）、或进行 S1 需求评审任务时。
  Use when the user runs /aidocx-s1-review with a requirement file (.docx / .md / .txt) or starts a Stage 1 review task.
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s1-review
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S1 — 需求评审

**独立阶段**：可单独调用。丢入材料 → 审查材料 → [合格] 开始评审产出 / [不合格] 生成失败报告。

---

## 阶段入口

**触发**：`/aidocx-s1-review` + 需求文件，**不接受纯文本粘贴**

**支持的文件格式**：

| 格式 | 处理方式 | 产出 |
|------|----------|------|
| `.docx` / `.doc` | `run_s1_pipeline()` 解析 + OCR + 图片归档 | `extracted_text.md` + `image_index.json` + `extracted_images/` + `ocr_results/` |
| `.md` | 直接进入评审，跳过 OCR | 直接进入 5 维度评审 |
| `.txt` | 直接进入评审，跳过 OCR | 直接进入 5 维度评审 |

**物料门禁失败**（文件不存在 / 不可解析 / 解析后正文 < 50 字）：
- **不进入** 5 维度评审
- 直接生成 `fail_report_S1.md`（仅含"失败原因 = 物料缺失"一段）
- 停止流水线

---

## 【第 0 步】优化识别（S1.8 子阶段）⚠️ 新增

> 当用户上传的文档为**优化文档**（非全新需求）时，先执行本步识别。
> 识别后呈现多选项，用户选择后再执行增量或全量 S1 评审。

### Step 0.1 提取文档结构

扫描所有标题和关键词，识别优化内容：

```
优化识别关键词（启发式）：
  【优化 / 【变更 / 【新增 / 【修改   →  方括号标记块
  ## 优化 / ## 新增 / ## 变更        →  章节标题块
  > **变更 / > **新增                  →  引用块高亮
  文档名含"优化/升级/v2/v3"           →  全量替换文档
```

### Step 0.2 分类优化类型

| 类型 | 判断规则 | AI 动作 |
|------|----------|---------|
| **形式 A（混杂）** | 优化内容穿插在长文中，新的用颜色/标记，旧的可能划线/置灰 | 识别优化块，呈现多选项 |
| **形式 B（独立新增）** | 文档中有明确"## 优化项N"或"## 新增功能"章节 | 识别优化块，呈现多选项 |
| **形式 C（全量替换）** | 文档名含"XX优化/重构"，全文都是新内容 | 直接执行标准 S1（全量评审）|
| **非优化文档** | 无上述任何标记 | 直接执行标准 S1 |

### Step 0.3 调用优化识别脚本

```python
from ai_workflow.requirement_reviewer_auto import (
    detect_optimization_blocks,
    build_incremental_context,
    generate_regression_guidance,
)

manifest = detect_optimization_blocks(extracted_text)
# manifest.is_optimization = True  → 增量文档
# manifest.optimization_type:
#   "none"       → 非优化，直接走标准 S1
#   "full_doc"   → 全量替换，直接走标准 S1
#   "incremental"→ 增量文档，呈现多选项
```

### Step 0.4 生成多选项（仅增量文档触发）

当 `manifest.optimization_type == "incremental"` 时，输出以下多选项供用户选择：

```
【S1.8 优化识别结果】

检测到 N 个优化块，请选择审查范围：

| 选项 ID | 优化块名称 | 影响模块 | 摘要 |
|---------|-----------|---------|------|
| 基础文档 | 原始需求基线（vX.XX） | 全模块 | ... |
| OPT-001 | [优化块名称] | BIZ/SPECIAL | [摘要] |
| OPT-002 | [优化块名称] | CONFIG/UI | [摘要] |
| 全部优化 | 全部 N 个优化块 | ... | ... |
| 全文档 | 基础文档 + 全部优化块 | 全模块 | 执行全量 S1 评审 |

请从上方选项中选择一个或多个（可多选）。
```

### Step 0.5 用户选择后，构建增量上下文

```python
# 用户选择了 [OPT-001, OPT-002] 后
context = build_incremental_context(
    manifest,
    selected_block_ids=["OPT-001", "OPT-002"],
    old_backlog_path="workflow_assets/<req_name>/「S2 需求拆解」/vX.XX/backlog.json",
)
# context["is_incremental"] = True
# context["affected_modules"] = ["BIZ", "SPECIAL"]
# context["regression_required"] = True

regression = generate_regression_guidance(
    manifest,
    selected_block_ids=["OPT-001", "OPT-002"],
    old_backlog_path="workflow_assets/<req_name>/「S2 需求拆解」/vX.XX/backlog.json",
)
# regression["regression_epics"] = [...]
# regression["guidance_text"] → 供 S5/S6 使用
```

### Step 0.6 增量 S1 评审（用户选择后执行）

**对选中块执行增量 S1（不重复评审基础文档）**：

1. 读取基础文档（旧版 `终版需求.md`）
2. 读取旧 backlog（若存在）
3. **仅对选中优化块进行 S1 评审**（5 维度评分 + 需求对象拆解）
4. 识别新引入的风险点和关联模块
5. 产出增量 `review_report.md`（标注：增量内容 vs 旧内容）
6. 生成回归测试建议（写入 `review_report.md` 的"回归建议"小节）
7. 版本号：`base_version + 0.01`（如 v3.01 → v3.02）

**增量评审重点**：
- 不重复评审基础文档已有内容（只评审 OPT-XXX 块内的新内容）
- 识别优化引入的新风险（如：原来 VIP 折扣不叠加，现在改为叠加 → SPECIAL 模块新风险）
- 识别关联模块变化（CONFIG 字段变更 → 影响 BIZ 逻辑 → 回归 Epic）

### Step 0.7 全流程传递增量上下文

在 `review_report.json` 的 meta 中携带增量上下文：

```json
{
  "meta": {
    "is_incremental": true,
    "selected_blocks": ["OPT-001", "OPT-002"],
    "base_version": "v3.01",
    "affected_modules": ["BIZ", "SPECIAL"],
    "regression_required": true,
    "regression_epics": ["BIZ-PURCHASE-01", "CONFIG-VIP-01"],
    "incremental_epics": ["OPT-001-001", "OPT-002-001"]
  }
}
```

该 `meta` 字段在 S1.5 → S2 → S4 → S5 → S6 → S7 → S8 的每阶段**必须读取**，以确定增量审查范围。

---

## §1.4 必读材料与违规认定

> ⚠️ **违反本节禁令 → 产出不合格，必须补读后重新生成。**

### 违规认定（满足任一 → 产出不合格）

- ❌ 未读取本节材料，直接凭印象生成
- ❌ 跳过标注"强制"的材料，用其他来源替代
- ❌ 产出的 module 与材料内容明显不符
- ❌ 用"业务常识"替代必须读取的材料

### 必读材料清单

**生成任何产出前，必须先 Read 以下材料。禁止凭印象/常识/历史产物直接生成。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| ① | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| 所有 Epic/Story 必须有模块前缀；模块分类决定后续所有判断 |
| ② | S1 产物目录结构 | `workflow_assets/<req_name>/「S1 需求评审」/<version>/` | 知道产出物落在哪、文件叫什么 |
| ③ | 模块边界区分 | `.cursor/MODULES.md`（§4 各模块 O_boundary.md）| 8 模块边界容易混淆（如 HINT vs UI、BIZ vs CONFIG），判定前必读 |

---

## §5 一致性检查（SKILL ↔ Rule 自动对齐）

> **触发时机**：本节读取后、正式执行前。**仅执行一次**（同一次对话中多次触发本阶段，不重复检查）。

**检查类型**：A = 必读材料对齐 / B = 输出路径对齐 / C = 字段名对齐 / D = 模块枚举对齐

```python
from ai_workflow.consistency_check import run_consistency_check

result = run_consistency_check(stage="s1")
# result["passed"] = True 时正常执行
# result["issues"] 非空时日志输出问题，但不阻断执行
if not result["passed"]:
    print(f"[一致性检查] 发现 {len(result['issues'])} 个问题（见日志）")
```

检查结果不阻断阶段执行，仅输出到日志供人工参考。

---

## 前置材料建议（仅提示，不阻断）

> **仅在 `review_report.md` 的"补充材料建议"小节出现**，不进入物料门禁、不进入问题清单、**不阻断**任何环节。
> 现实场景：用户通常只丢 1 个 docx，下表的"原型稿 / 配套资料 / 排期初稿"三项一般缺失——AI 不做阻断，只做建议。

| 准备产物 | 现实状态 | 缺失时 AI 建议补充什么 |
|----------|----------|------------------------|
| **原始需求文档 PRD** | ✅ 必有 | docx 文档主体，承载玩法/系统/活动/付费/剧情/UI 交互/配置规则 |
| **需求原型 / 交互稿** | ⚠️ 多数缺失 | docx 内"UI 交互"章节，附图片（OCR 自动归档） |
| **配套参考资料** | ⚠️ 多数缺失 | docx 内"配套资料"章节（竞品 / 美术 / 数值 / 埋点 / 本地化 合并） |
| **需求排期初稿** | ⚠️ 多数缺失 | docx 内"排期"章节（开发工期 / 上线节点 / 关联依赖模块） |

### docx 内部推荐章节命名

> 策划写 docx 时使用以下章节名，AI 识别准确率更高：

```
# 标题
## 玩法
## 系统
## 活动
## 付费
## 剧情
## UI 交互    ← 原型稿承载位（带图片）
## 配置规则
## 配套资料    ← 竞品 / 美术设定稿 / 数值表 / 埋点 / 本地化文案 合并
## 排期       ← 开发工期 / 版本上线节点 / 关联依赖模块
```

### AI 行为约束

- ✅ 允许在 `review_report.md` 末尾追加"补充材料建议"小节（5 行内，**只列缺失项**）
- ❌ **不**把材料缺失写入"问题需求清单"（P0/P1/P2）
- ❌ **不**触发任何 fail_report
- ❌ **不**因材料缺失扣 5 维度评分

---

## 审查产物 1 — 角色定义与分类

> **覆盖关系说明**：以下 3 段审查产物（角色 / 需求对象 / 问题需求）+ 5 维度评审，**完全覆盖**了原"内容门禁"4 项的诉求。AI 不再另设"输入审查"环节——所有 4 项检查项都直接落到产物里：
>
> | 原内容门禁项 | 归宿 |
> |-------------|------|
> | 用户角色定义 | → 审查产物 1（角色定义与分类） |
> | 功能描述 | → 审查产物 2（需求对象拆解 / 功能列表） |
> | 量化指标 | → 5 维度评审"清晰度"维度 |
> | 验收标准 | → 审查产物 2（业务故事的通过/失败条件） |

AI 必须**从需求文本中抽取并定义**所有角色，按以下分类打标签：

| 类别 | 含义 | 典型来源 |
|------|------|----------|
| **主角色** | 需求服务的核心用户 | 需求中显式提到"玩家/用户/管理员" |
| **次角色** | 辅助或分支场景中的角色 | "游客 / 未登录 / 灰度账号" |
| **边界角色** | 极端 / 异常场景中的角色 | "黑名单 / 封禁 / VIP 过期" |

每条角色的产出格式：

```markdown
### <role_id>: <角色名>
- **类别**: 主 / 次 / 边界
- **来源**: <需求原文引用>
- **核心目标**: <该角色使用本系统要达成的目标>
- **典型场景**: <覆盖该角色在需求文档中触达的所有功能点，无数量下限>
- **隐含权限**: <可见 / 可改 / 可删 范围>
```

> 若需求文档**完全没有角色描述**，AI 必须主动**从功能描述反推**角色，并在产物中标注 `【反推】`，待 S1.5 人工确认。
>
> **典型场景 = 需求文档覆盖检查项**：AI 须遍历需求文档，把**该角色出现过的所有功能点**都列入"典型场景"，**不设数量下限**。若一个角色在文档中只触达 1 个功能点，列 1 个；触达 N 个，列 N 个。**不要求"至少 N 个"**。

---

## 审查产物 2 — 需求对象拆解 + 8 模块标签

按"**需求对象 → 功能 → 业务故事**"三层下钻，每条拆解结果打**8 模块分类标签**之一。

### 8 模块标签

> ⚠️ 模块定义见 [`.cursor/MODULES.md`](../../MODULES.md)（项目级唯一真相源）。
> 本文件不重写模块表。如模块定义调整，只改 MODULES.md。

### 业务属性标签

> 模块定义见 [`.cursor/MODULES.md`](../../MODULES.md)（项目级唯一真相源）。

### 强付费项质量闭环 3 段

> 定义见 [`.cursor/rules/STAGE_S1_REVIEW.mdc`](../../rules/STAGE_S1_REVIEW.mdc)（强付费项质量闭环 3 段节）。

### 拆解格式

```markdown
### <obj_id>: <需求对象名>
- **所属角色**: <role_id>
- **模块**: <8 模块之一，定义见 [`.cursor/MODULES.md`](../../MODULES.md) §1 总表>
- **功能列表**:
  1. <功能 1>（输入 → 处理 → 输出）
  2. <功能 2>（输入 → 处理 → 输出）
  3. ...
- **业务故事**（每条功能配 1 个，**1:1 配对 = 100% 覆盖率**）:
  - 故事 1：作为 <role>，我希望 <功能 1>，以便 <业务价值>
  - 故事 2：...
  > **覆盖率约束**：业务故事数 / 功能点数 = 100%，**不能少**（少了覆盖率 < 100%，不通过 S5/S6 风险点全量覆盖检查）/**不能多**（多了重复浪费）。
  > 这条是**结构性配对约束**，**不是数量指标陷阱**——区别于"典型场景"那种"≥ N 个"的下限陷阱。
- **数据流转 / 落地**:
  - 入口: <来源表 / 接口 / 状态>
  - 处理: <核心服务 / 状态机>
  - 出口: <落库表 / 推送事件 / 缓存失效>
- **风险点**: <该对象最易出错的 1-2 个点，> 0 字符
```

---

## 审查产物 3 — 问题需求清单（S1.5 准入物料）

把所有"AI 无法判定 / 文档自相矛盾 / 缺失关键约束"的需求条目，汇总为**问题需求清单**，作为 S1.5 阶段人工审核与回答的对象。

### 优先级

| 等级 | 含义 | 处理人 | 阻断 S1？ |
|------|------|--------|----------|
| **P0** | 阻断 S2 拆解（如主流程行为未定义、核心角色缺失） | S1.5 人工**必须**回答 | ❌ 不阻断 S1 |
| **P1** | 影响 S5/S6 测试覆盖（边界值、错误码、状态机） | S1.5 人工**建议**回答 | ❌ |
| **P2** | 文案 / 命名 / 风格类（不影响逻辑） | S1.5 人工**可选**回答 | ❌ |

> S1 **不阻断任何环节**——所有 P0/P1/P2 都进入 S1.5 准入物料，由人工审核决定是否补齐。S2 的阻断门禁由 S1.5 的 `exit_permission.json` 控制（详见 S1.5 规则）。

### 输出位置

**复用 `clarification_checklist.md`**，新增 `## 问题需求（→ S1.5 准入物料）` 一节，结构如下：

```markdown
## 问题需求（→ S1.5 准入物料）

| ID | 需求对象 | 问题描述 | 优先级 | SPECIAL_FLAG | 答案（人工填写） |
|----|----------|----------|--------|--------------|-----------------|
| Q-P0-001 | 商城下单 | 下单后库存为 0 时，是阻塞下单还是允许下单？ | P0 | — | |
| Q-P0-002 | 发奖系统 | 缺"程序自测点"段 | P0 | `PURCHASE_STRONG` | |
| Q-P1-001 | 礼包兑换 | 同一礼包每日兑换上限未定义 | P1 | — | |
```

---

## 5维度评审

| 维度 | 权重 | 评审要点 |
|------|------|----------|
| 完整性 | 25% | 角色定义、需求对象拆解、功能覆盖、验收标准是否齐全 |
| 清晰度 | 25% | 无模糊术语、有量化指标、术语定义一致 |
| 一致性 | 20% | 角色 / 需求对象 / 功能三层之间无矛盾 |
| 可测试性 | 20% | 每个业务故事有明确通过/失败条件 |
| 可行性 | 10% | 技术约束已识别，无未定义的外部依赖 |

---

## 判决规则

| 总分 | 判决 | 后续动作 |
|------|------|----------|
| ≥ 7.0 | **PASS** | 进入 S2 |
| 4.0 – 6.9 | **NEEDS_REVISION** | 输出修改建议，等待修订后重审 |
| < 4.0 | **REJECT** | 输出失败报告，停止流水线 |

---

## 成功产出

路径：`workflow_assets/<req_name>/「S1 需求评审」/<version>/`

| 文件 | 必选 | 说明 |
|------|------|------|
| `raw/` | 物料门禁通过时 | `extracted_text.md` + `image_index.json` + `extracted_images/` + `ocr_results/`（仅 .docx） |
| `review_report.md` | 始终 | 5 维度评分报告 |
| `review_report.json` | 始终 | 结构化评分数据 |
| `role_definitions.md` | 始终 | 角色定义与分类（主/次/边界） |
| `requirement_objects.md` | 始终 | 需求对象拆解（角色→对象→功能→业务故事 + 8 模块标签） |
| `requirement_objects.json` | 始终 | 结构化拆解（供 S2 直接消费） |
| `clarification_checklist.md` | 始终 | 待确认问题 + **问题需求清单**（S1.5 准入物料） |
| `终版需求.md` | PASS / NEEDS_REVISION | AI 整理后的需求文档（含待确认项标注） |

报告内容（`review_report.md`）：评分表 → 角色定义摘要 → 需求对象清单 → 缺失信息 → 冲突项 → 问题需求 → 优先级建议 → 总结

---

## 失败报告

路径：`workflow_assets/<req_name>/「S1 需求评审」/<version>/fail_report_S1.md`

报告内容：失败原因（**物料缺失** / 内容冲突 / 不可行要求）→ 修改建议（阻断/可选）→ 后续动作

> **物料门禁失败时**：仅生成 `fail_report_S1.md`，**不**写 `review_report.md` / `requirement_objects.*` / `role_definitions.md` / `clarification_checklist.md`。

---

## 自动化支持

```python
from ai_workflow.requirement_reviewer_auto import auto_review_requirement
result = auto_review_requirement(requirement_text)
# result['verdict'] ∈ {'PASS', 'NEEDS_REVISION', 'REJECT'}
# result['score_total'] ∈ [0.0, 10.0]
```

---

## 反向契约（S1 必须知道的事）

S1 评审时**必须**意识到：

1. **S1 产出 = S1.5 准入物料**——5 份物料缺 1 份即被 S1.5 退回
2. **S1.5 不可被缺省**——任何"跳过 S1.5 直接进 S2"的尝试**必须 fail**（S2 触发 `fail_report_S2.md`）
3. **功能 × 业务故事 1:1 配对 = 100% 覆盖率**——S1 偷工减料（5 个功能只配 1 个故事）→ S2 拆解覆盖率 < 100% → S7 风险点全量覆盖 FAIL
4. **强付费项（PURCHASE_STRONG）的 P0** 缺失 = S1.5 强门禁——`SPECIAL_FLAG = PURCHASE_STRONG` 的 P0 **必须**全部答完才能 `can_proceed_to_s2 = true`
5. **轻量跑通 ≠ 跳过 S1.5**——S1.5 仍要执行（产出 `exit_permission.json`），但 `quality_level = LOW`（P0 全填 + P1/P2 可不填）

**S1 → S1.5 → S2 物料链**：

```
S1 产出（5 份）
  ├── review_report.md
  ├── role_definitions.md
  ├── requirement_objects.md + .json
  ├── 终版需求.md（草稿）
  └── clarification_checklist.md（含"问题需求（→ S1.5 准入物料）"节）
        ↓ S1.5 接收并验收
S1.5 产出（3 份）
  ├── 终版需求.md（完善）
  ├── exit_permission.json（can_proceed_to_s2 = true）
  └── clarification_checklist.md（状态：✅ 已处理）
        ↓ S2 读取
S2 需求拆解
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S1_REVIEW.mdc`
- Prompt 模板：`ai_workflow/prompts/requirement_review.md`
- 物料解析子流水线：`ai_workflow/stage_s1_input/run_s1_pipeline()`（DOCX→md+图片归档+OCR）
- 自动化引擎：`ai_workflow/requirement_reviewer_auto.py`（⚠️ 仍按"4 项内容门禁"实现，待对齐本次重构）
- 输出目录：`workflow_assets/<req_name>/「S1 需求评审」/<version>/`
