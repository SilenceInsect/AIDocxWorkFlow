---
name: aidocx-s5-test-points
description: >
  AIDocxWorkFlow Stage 5 — 测试点生成。模块定义完整见 `.cursor/MODULES.md`（项目级唯一真相源），不重写压缩版。完整类型数量约束见 §1.1 + §1.4 + 各模块 .md 子模板（无硬数字）。
  Use when the user runs /aidocx-s5-test-points, pastes S2 backlog, or starts test point generation.
  使用当用户执行 /aidocx-s5-test-points、粘贴 S2 backlog、或进行 S5 测试点生成任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s5-test-points
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S5 — 测试点生成

**独立阶段**：可单独调用。上游材料（S2 backlog）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s5-test-points` 或粘贴 S2 backlog

**前置材料**：
- S2 backlog.md：`workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.md`
- S4 business_flow.md（**强烈推荐参考**）：`workflow_assets/<req_name>/「S4 流程图导出」/<version>/business_flow.md`
  - 包含异常/错误决策树和风险点清单，用于补充 EXCEPTION 类型测试点
  - 若 S4 未执行，EXCEPTION 测试点需自行推导异常路径，可能遗漏风险场景

**材料缺失时**：生成失败报告，停止 S5。

---

## 8 模块测试类型（**模块 × 类型双维度必填**）

> ⚠️ 模块定义见 [`.cursor/MODULES.md`](../../MODULES.md)（项目级唯一真相源）。
> 本文件不重写模块表。如模块定义调整，只改 MODULES.md。**S5 LLM 在生成任何 TP 前，必须先 Read MODULES.md §1 总表 + 命中模块的 `<MODULE>.md` + 命中模块的 `O_boundary.md`（详见 §1.4）。**

本阶段涉及的模块（按 MODULES.md §1 总表顺序）：`CONFIG` / `UI` / `BIZ` / `AUX` / `LINK` / `LOG` / `SPECIAL` / `HINT`
（`HINT` 是独立模块，专指"红点/飘字/弹窗/Toast"等提示反馈类测试点）
完整测试类型矩阵见 [`.cursor/MODULES.md` §4](../../MODULES.md)。

### 1.1 测试类型枚举（**4 个全局类型，必填**）

| 枚举值 | 中文 | 含义 |
|--------|------|------|
| `POSITIVE` | 正向 | 正常流程测试 |
| `BOUNDARY` | 边界值 | 边界条件测试（0、负、上限、跨日等）|
| `NEGATIVE` | 负向 | 异常输入测试（非法参数、缺资源）|
| `EXCEPTION` | 异常 | 系统异常处理测试（网络、断电、宕机）|

> **必填**：每个 `scenario_test_points[]` 条目**必须**包含 `module` 字段 + `test_point_type` 字段（4 选 1）。
> 模块字段取值集合定义见 [`.cursor/MODULES.md` §1 总表](../../MODULES.md)。
> 缺任意一个字段 → S5 失败报告 `fail_report_S5.md` 阻断。

### 1.2 模块 × 类型 双维度强制判定（S5 误标高发区）

> **每个测试点必须同时回答 2 问**：
> 1. **属于哪个模块？**（8 模块之一）
> 2. **属于哪种类型？**（4 类型之一）
>
> 同一个功能点常跨多模块 → **每个模块都要单独生成 TP**（不是"取主"）

| 场景 | 模块 | 类型 | 备注 |
|------|------|------|------|
| 购买按钮按下响应 | UI | POSITIVE | UI 测样式 |
| 购买按钮调支付接口 | BIZ | POSITIVE | BIZ 测业务 |
| 购买按钮按下报错 Toast | HINT | EXCEPTION | HINT 测提示内容 |
| 购买按钮按下上报日志 | LOG | EXCEPTION | LOG 测埋点 |
| 购买按钮切弱网容错 | SPECIAL | EXCEPTION | SPECIAL 测降级 |
| 红包系统反作弊 | SPECIAL | NEGATIVE | 反作弊校验 |

### 1.3 HINT vs UI 二次判定（**S5 误标高发区**）

> 完整边界规则 + 决策树见 [`module_templates/HINT/O_boundary.md`](../../workflow_assets/module_templates/HINT/O_boundary.md)。
> **核心判定三问**：
> 1. 该元素是**事件触发弹出**还是**页面常驻可见**？事件触发 → HINT；常驻 → UI
> 2. 该元素是**操作后自动消失**还是**玩家手动关闭**？自动消失 → HINT；长期保留 → UI
> 3. 该测试点是测"**显示什么内容/数字/文案**"（HINT）还是测"**UI 容器的样式/位置/动画**"（UI F.GUIDE_HINT）？内容 → HINT；样式 → UI

| 场景 | 归 HINT | 归 UI |
|------|---------|-------|
| 背包页面里**固定显示的金币数字** | ❌ | ✅（UI 测常驻数字显示）|
| 使用道具弹出**金币+100 飘字** | ✅ | ❌（HINT 测飘字内容）|
| 活动页面**常驻活动标题** | ❌ | ✅（UI 测常驻标题渲染）|
| 上线自动弹出**活动奖励弹窗** | ✅ | ❌（HINT 测弹窗内容）|
| 战斗中**血条/技能图标** | ❌ | ✅（UI 常驻渲染）|
| 战斗中**暴击 +9999 飘字** | ✅ | ❌（HINT 测飘字内容）|

**HINT 子类映射**（v1.7+ 13 大类）：
- `RED_DOT_BADGE`（红点/角标/数字）| `ITEM_FLOAT`（资源飘字）| `CURRENCY_FLOAT`（战斗飘字）| `MODAL_DIALOG`（模态弹窗）| `TOAST`（短时轻提示）| `FLOAT_NOTIFY`（浮动通知）| `TIMED_REMINDER`（限时+错误文案）| `GUIDE_HIGHLIGHT`（新手引导）| `SOCIAL_PROMPT`（社交提示）| `OPS_PUSH_PROMPT`（运营推送）| `STATE_CHANGE_DIALOG`（状态变更）| `COMPLIANCE_PROMPT`（风控合规）| `OFFLINE_COMPENSATION`（离线补偿）

**v1.6.1 旧枚举迁移**（自动升级）：
- `RED_DOT` → `RED_DOT_BADGE`（语义升级：扩展为"红点+角标+数字"）
- `SYS_MSG`（v1.6.1 凭空出现）→ `MODAL_DIALOG` 或 `TOAST`（按场景）
- 执行 `python ai_workflow/test_case_formatter.py --migrate-modules <test_points.json>` 批量升级

### 1.4 S5 LLM 必读指令（**模块归属判定**）

**S5 LLM 在生成任何 TP 前,必须先 Read 命中模块的 `<MODULE>.md` 全文 + `MODULES.md §3.5` 全文。**
**禁止凭印象/常识/旧 TP 模式生成,禁止在没有 §3.5 判定依据时直接产出。**

**8 模块定义全文（原文链接,以下为 Read 路径,无需 LLM 自学,直接 Read 即可）**：

| 模块 | 模块文件 | 边界文件 |
|---|---|---|
| <a id="aux-m" href="../../workflow_assets/module_templates/AUX.md">AUX</a> | `workflow_assets/module_templates/AUX.md` | <a id="aux-b" href="../../workflow_assets/module_templates/AUX/O_boundary.md">AUX/O_boundary.md</a> |
| <a id="biz-m" href="../../workflow_assets/module_templates/BIZ.md">BIZ</a> | `workflow_assets/module_templates/BIZ.md` | <a id="biz-b" href="../../workflow_assets/module_templates/BIZ/O_boundary.md">BIZ/O_boundary.md</a> |
| <a id="config-m" href="../../workflow_assets/module_templates/CONFIG.md">CONFIG</a> | `workflow_assets/module_templates/CONFIG.md` | <a id="config-b" href="../../workflow_assets/module_templates/CONFIG/J_boundary.md">CONFIG/J_boundary.md</a> |
| <a id="hint-m" href="../../workflow_assets/module_templates/HINT.md">HINT</a> | `workflow_assets/module_templates/HINT.md` | <a id="hint-b" href="../../workflow_assets/module_templates/HINT/O_boundary.md">HINT/O_boundary.md</a> |
| <a id="link-m" href="../../workflow_assets/module_templates/LINK.md">LINK</a> | `workflow_assets/module_templates/LINK.md` | <a id="link-b" href="../../workflow_assets/module_templates/LINK/O_boundary.md">LINK/O_boundary.md</a> |
| <a id="log-m" href="../../workflow_assets/module_templates/LOG.md">LOG</a> | `workflow_assets/module_templates/LOG.md` | <a id="log-b" href="../../workflow_assets/module_templates/LOG/O_boundary.md">LOG/O_boundary.md</a> |
| <a id="special-m" href="../../workflow_assets/module_templates/SPECIAL.md">SPECIAL</a> | `workflow_assets/module_templates/SPECIAL.md` | <a id="special-b" href="../../workflow_assets/module_templates/SPECIAL/O_boundary.md">SPECIAL/O_boundary.md</a> |
| <a id="ui-m" href="../../workflow_assets/module_templates/UI.md">UI</a> | `workflow_assets/module_templates/UI.md` | <a id="ui-b" href="../../workflow_assets/module_templates/UI/I_boundary.md">UI/I_boundary.md</a> |

**判定规则完整见** <a href="../../MODULES.md">`.cursor/MODULES.md`</a> **§3.5 交叉场景归属判定表（必读,见 §1.4）+ §4.11.2 HINT vs UI 边界隔离规则（见 §1.4）**。

**反例库(强制对照,见 PROMPT-PUSH-4)** — 写 TP 前,先扫一次以下反例,对照当前 TP 描述 + module 字段:
- 若与某反例同 pattern → 改 module 或删除
- 若不与任何反例撞 → 简单记录"与反例无冲突"

> ⚠️ [PUSH-V2-ITER-3] **反例库升级**: 之前的"反例仅作参考"已废除。**现在反例是判定 guard,每个 TP 必走反例对照**。LLM 必须在 TP JSON 的 `applies_rule` 字段里声明"与反例 N 无冲突 / 已应用反例 N"。

<a href="../../workflow_assets/游戏道具商城系统/「S5 测试点生成」/v1.0/test_points.json">`workflow_assets/游戏道具商城系统/「S5 测试点生成」/v1.0/test_points.json`</a> 75 个 TP 是 S5 旧规则下的产物,**保留作反例库**——其中已发现的 5 处误判 (S4.1-TP-001 LINK / S4.2-TP-004 BIZ / S5.4-TP-004 BIZ+LOG 重叠 / S7.1-TP-003 HINT vs BIZ 模糊 / S2.1-TP-010 字段名 typo) **不得再犯**。

---

## 每个 Story 必须生成

> **数量原则（去硬数字）**：每个 Story 的 TP 数量由 LLM 根据业务复杂度自由决定——
> S5 LLM 必先 Read 该 Story 命中模块的 `<MODULE>.md` 全文 + 各子模板，
> 再据业务自然分布决定每个 Story 应有 1 个还是 10 个 TP。**不设硬指标**。
>
> **S5 LLM 必做**:在生成任何 TP 之前,先 Read 该 Story 命中模块的 `<MODULE>.md` 全文,再据子模板判定类型与数量。
>
> **类型枚举(4 选 1)**:POSITIVE(正向) / BOUNDARY(边界) / NEGATIVE(负向) / EXCEPTION(异常)——见 §1.1。
>
> **多模块覆盖**:同一功能点跨多模块 → 每个模块都要单独生成 TP(不是"取主")。

**ID 格式**:`{StoryID}-TP-{3位序号}`,如 `UI-001-001-TP-001`

---

## 1.5 决策 push 块(无硬指标版本,见 [PUSH-V2-ITER-3] 标签)

> **哲学**: 不告诉 LLM 多少算合格,告诉 LLM 怎么思考产出质量。

### 1.5.1 [PUSH-V2-ITER-3] 跨模块拆分 push(对应 PROMPT-PUSH-1)

> 旧版要求"每个 Story 至少 3 module"——硬指标易凑数。**新版用 3 问决策 push**:

**写 TP 前先问自己 3 问**:
- Q1. 这个 Story 的"业务流"是单系统还是涉及上下游/第三方?(如购买涉及支付/订单/邮件)
- Q2. "业务流"的数据/状态变化会触发哪些 UI/HINT/LOG 反馈?
- Q3. 这个 Story 是否会暴露配置/缓存/异常/合规风险?

**3 问任一为"是"→ 必须为该模块单独生成 TP,不偷懒合并**。

### 1.5.2 [PUSH-V2-ITER-3] 4 步判定 push(对应 PROMPT-PUSH-2)

> 旧版要求"先过 4 步判定"——软约束 LLM 易跳过。**新版改为必走 checklist**:

**每个 TP 写之前必走 4 步(任一空答→暂停,先补 Read)**:
- Push 1: 读 §3.5 找命中模块(8 选 1)
- Push 2: 读该模块 .md 找命中子类(枚举 13 选 1)
- Push 3: 读该模块 `O_boundary.md` 边界对照表,确认不与 X 模块冲突
- Push 4: 读 S4 业务流找对应 F-XX 节点/异常树叶子/R-XX 风险点

**4 步全部回答后,再开始写 TP**。LLM 必须在 TP JSON 的 `applies_rule` 字段里说明走了哪 4 步。

### 1.5.3 [PUSH-V2-ITER-3] is_assumed 标记(对应 PROMPT-PUSH-3)

> 旧版要求"未明确数值标 [待定]"——LLM 偷懒不标。**新版改为 JSON 强字段**:

**业务数字/事件名等 LLM 自由推理的字段,必须满足**:
- 必须在 TP JSON 中加 `is_assumed: true` 标记
- 加 `assumption_reason` 字段说明来源(S2 backlog / S4 / 业务常识)
- 若来源于业务常识,加 `requires_human_review: true`

### 1.5.4 [PUSH-V2-ITER-3] 反例对照 push(对应 PROMPT-PUSH-4)

> 旧版要求"参考反例库"——LLM 真的不照抄。**新版改为强制对照**:

**写 TP 前,先扫一次反例表**(HINT 误判 1-8 / BIZ 误判 1-10 / UI 误判 1-5 / AUX vs BIZ 误判 5 / LOG 误判 8):
- 若与某反例同 pattern → 改 module 或删除
- 若不与任何反例撞 → 简单记录"与反例无冲突"

**LLM 必须在 TP JSON 的 `applies_rule` 字段里声明"与反例 N 关系"**。

### 1.5.5 [PUSH-V2-ITER-3] JSON Schema 字段名强约束(对应 PROMPT-PUSH-5)

> 旧版无字段名清单——S2.1-TP-010 字段名 typo 就是这么来的。**新版改为 schema 强约束**:

**TP JSON 字段必须严格按以下 schema(任何字段名拼写错误 → 写错)**:
- `tp_id` (String, 必填)
- `module` (Enum: UI/BIZ/AUX/LINK/LOG/SPECIAL/CONFIG/HINT, 必填)
- `test_point_type` (Enum: POSITIVE/BOUNDARY/NEGATIVE/EXCEPTION, 必填)
- `test_type_subclass` (String, 命中模块子模板的枚举, 必填)
- `description` (String, 必填)
- `s4_reference` (String, R-NNN 或 F-XX 或 S4-{EpicID}-X.Y.Z, 必填)
- `boundary` (String, 描述边界/无, 必填)
- `is_assumed` (Boolean, 默认 false, 必填)
- `applies_rule` (String, 引用模板路径, 必填)

### 1.5.6 [PUSH-V2-ITER-3] 5 问质量 push(对应 PROMPT-PUSH-6)

> 旧版要求"至少 1 个 TP"——软约束 LLM 偷懒。**新版改为 5 问自查**:

**质量 push — 不要追求 TP 数量,先追求 TP 质量**。每个 TP 必须能回答 5 问:
1. 测什么(明确场景)
2. 命中哪个模块 + 哪个子类(精确不模糊)
3. 边界值/异常输入是什么(具体不抽象)
4. 预期结果可验证吗(pass/fail 明确)
5. 对应 S4 哪个节点(链路可追溯)

**5 问任一空答→TP 不合格,删除或重写**。

---

## 1.6 [PUSH-V2-ITER-3] 强制输出字段清单(本轮新增)

**S5 v3 产物(test_points-iter3.json)必须包含以下字段,缺一视为 TP 不完整**:
- `s4_reference`: 每个 TP 必填,引用 S4 R-NNN / F-XX / Epic 节点
- `test_type_subclass`: 必填,用细分枚举(如 `BIZ.H_payment` 而非大类 `BIZ_PAYMENT`)
- `applies_rule`: 必填,说明走了哪 4 步 + 反例对照 + 模块引用路径
- `is_assumed`: 业务数字/事件名 LLM 自由推理的必填 true + 业务常识的必填 true + 加 `requires_human_review: true`
- `boundary`: 描述具体边界值(0/1/100/9999/...)或"无"
- `module_judgment_basis`: 选填,记录 LLM 的 §3.5 判定过程(帮助审计)

---

## 成功产出

路径：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json`

---

## 失败报告

路径：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/fail_report_S5.md`

---

## 自动化支持

```python
from ai_workflow.test_case_formatter import compose_test_points_from_structure, _build_fallback_scenarios
breakdown = {'epics': [...], '_version': 'v1.0'}
skeleton = compose_test_points_from_structure(breakdown)
# skeleton 中每个 Story 有 module + 真实测试点内容

from ai_workflow.conversation_skills import save_stage5_output
save_stage5_output(version, breakdown, flowchart_text, raw_output, parsed, req_name)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S5_TEST_POINTS.mdc`
- Prompt 模板：`ai_workflow/prompts/test_point_gen.md`
- 测试点库：`workflow_assets/test_point_library/`
- 示例参考：`workflow_assets/example_test_points/`

