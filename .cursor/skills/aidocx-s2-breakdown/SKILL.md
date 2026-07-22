---
name: aidocx-s2-breakdown
description: >
  AIDocxWorkFlow Stage 2 — 需求拆解。采用五层业务语义分层（Release → Epic → Story → Object → FP），每层按"业务自然划分"决定粒度而非硬性数值，含游戏行业增强字段（角色句式、模块归属、正向/异常流程、数据变更、验证手段）、统一边界判定流程、跨模块自动拆 OBJ 规则。使用当用户执行 /aidocx-s2-breakdown、粘贴 S1.5 准出许可路径、或进行 S2 需求拆解任务。
  Use when the user runs /aidocx-s2-breakdown, provides S1.5 exit_permission path, or starts requirement breakdown.
  使用当用户执行 /aidocx-s2-breakdown、提供 S1.5 准出许可路径、或进行 S2 需求拆解任务时。
disable-model-invocation: true
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s2-breakdown
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# AIDocxWorkFlow S2 — 需求拆解

**独立阶段**：可单独调用。上游材料（S1.5 准出许可）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发方式**：`/aidocx-s2-breakdown` 或粘贴 S1.5 准出许可路径

**前置材料**：
- 终版需求.md：`workflow_assets/<req_name>/<version>/「S1 需求评审」/终版需求.md`
- S1.5 准出许可：`workflow_assets/<req_name>/<version>/「S1 需求评审」/exit_permission.json`
- clarification_checklist.md：`workflow_assets/<req_name>/<version>/「S1 需求评审」/clarification_checklist.md`
- **review_structured.json（v16 T4 新增）**：`workflow_assets/<req_name>/<version>/「S1 需求评审」/review_structured.json`

**材料缺失或 `can_proceed_to_s2 == false` 时**：生成失败报告，停止 S2。

---

## 核心范式：五层业务语义分层（游戏行业适配）

S2 采用**五层业务语义分层**，整合通用敏捷 + 游戏研发语义：

```
Release（版本基线，元数据归集容器，不进 ID 段）
 └─ Epic（大系统 / 大型业务史诗）
     └─ Story（用户故事，可交付最小业务价值）
         └─ Object（需求对象，按业务载体拆分）
             └─ FP（功能点，最小不可拆分执行单元）
```

> **关键设计**：
> 1. **粒度不由硬性数值决定**——每层按"业务自然划分"给出指导档位，**禁止凑数 / 拆细**
> 2. **业务语义驱动**——引入角色句式、模块归属、正向/异常流程分离等游戏行业专属字段
> 3. **跨模块自动拆 OBJ**——一条业务涉及多模块时，按模块拆多 OBJ（不标[待确认]）
> 4. **统一边界判定流程**——8 大模块匹配优先级 + 兜底评审归档

---

## §1.4 必读材料与违规认定

> ⚠️ **违反本节禁令 → 产出不合格，必须补读后重新生成。**

### 违规认定（满足任一 → 产出不合格）

- ❌ 未读取本节材料，直接凭印象生成
- ❌ 跳过标注"强制"的材料，用其他来源替代
- ❌ 产出的 module 与材料内容明显不符
- ❌ 用"业务常识"替代必须读取的材料

### 必读材料清单

**生成任何产出前，必须先 Read 以下材料。禁止凭印象直接生成。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| ① | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| Epic/Story/OBJ 必须有模块前缀；模块分类是 §1.4 边界判定的基准 |
| ② | 模块边界区分 | `.cursor/MODULES.md`（§4 各模块 O_boundary.md）| 8 模块边界是拆解的核心约束；尤其是 BIZ vs CONFIG、UI vs HINT、LINK vs UTIL |
| ③ | S1.5 准出许可（强制） | `workflow_assets/<req_name>/<version>/「S1 需求评审」/exit_permission.json` | quality_level / fallback_rules / can_proceed_to_s2 决定拆解深度；未读取 → 无法执行 |
| ④ | **S1 结构化评审包（v16 T4）** | `workflow_assets/<req_name>/<version>/「S1 需求评审」/review_structured.json` | 4 类字段消费：边界注入/假设继承/风险种子/缺失标记；未读取 → 跳过消费逻辑 |
| ⑤ | 终版需求（完善版）| `workflow_assets/<req_name>/<version>/「S1 需求评审」/终版需求.md` | 所有 Epic/Story 的业务来源 |
| ⑥ | 命中模块子模板 | `knowledge/public/module_templates/<Module>/<Module>.md`（按命中模块）| OBJ 层功能点需按模块子模板判定测试类型和数量 |
| ⑦ | **模块边界决策树** | `knowledge/public/module_templates/_decision_tree.md` | 8 模块快速归类的二叉决策树；先命中模块,再读 ② 二次验证；拆 OBJ 时避免 HINT/UI/BIZ/CONFIG 等高频混淆 |

### 模块归类两步法

> **强制流程**：拆 OBJ 前,先按以下两步判定模块归属,禁止直接凭印象标注 module 字段。

1. **第一步：决策树快速命中**——读 `_decision_tree.md` §0 顶层决策树,沿问题分叉走到模块
2. **第二步：判定三问二次验证**——读该模块 `O_boundary.md` §1 的"判定三问",确认无矛盾
3. **跨模块场景**（命中 2 模块交集,如 HINT+UI / BIZ+LINK）→ 按 v12 S2 跨模块规则**拆多 OBJ**,不标 [待确认]

**判定冲突处理**：决策树命中 X 模块,三问判定属于 Y 模块 → 以**三问判定为准**,决策树简化版可能漏判

---

## 第二层：Release（版本基线，归集容器）

**粒度（指导档位，禁止硬性卡死）**：
- 完整大版本：4-12 周完整客户端包
- 热更增量包：0.5-2 周配置 / 逻辑更新包
- 临时运营补丁：0.5-3 天紧急修复包

**实现策略**：
- v1.x 存量产物**不强制回填 REL 段**（避免破坏下游 S3/S4/S5/S6 链接）
- 新拆解：在 backlog.json 顶层加 `release` 字段（**元数据级**，不进 Epic/Story ID 段）：

```json
{
  "release": {
    "id": "REL-2606-MAIN-01",
    "type": "MAIN" | "HOTFIX" | "PATCH",
    "cycle": "大版本" | "热更增量" | "运营补丁",
    "window": "2026-06 上线窗口",
    "owner": "主策/主测 姓名"
  }
}
```

**核心作用**：所有 Epic 必须归属唯一 Release，区分迭代基线，避免跨版本需求混杂。

---

## §5 一致性检查（SKILL ↔ Rule 自动对齐）

> **触发时机**：本节读取后、正式执行前。**仅执行一次**（同一次对话中多次触发本阶段，不重复检查）。

**检查类型**：A = 必读材料对齐 / B = 输出路径对齐 / C = 字段名对齐 / D = 模块枚举对齐

```python
from ai_workflow.consistency_check import run_consistency_check

result = run_consistency_check(stage="s2")
if not result["passed"]:
    print(f"[一致性检查] 发现 {len(result['issues'])} 个问题（见日志）")
```

检查结果不阻断阶段执行，仅输出到日志供人工参考。

---

## §1.5 决策 push 块

> **S2 阶段的关键使命**：跨模块拆 OBJ，否则下游 S5 无法做正确的跨模块 TP。

### §1.5.1 Story `scope_module` 强制填

**决策 push 3 问**（S2 写 Story 时必走）：

- Q1. 这个 Story 的"业务流"涉及哪些模块？（CONFIG/UI/BIZ/UTIL/LINK/LOG/SPECIAL/HINT，全 8 选多）
- Q2. 业务流的"数据/状态变化"会触发哪些 UI/HINT/LOG/SPECIAL 反馈？
- Q3. 业务流是否涉及第三方/缓存/合规风控？

**3 问任一为"是" → scope_module 必填对应模块**。

### §1.5.2 OBJ 跨模块拆分强制检查

**S2 写 OBJ 必走 4 步**（任一空答 → 暂停补 Read）：

| # | 操作 |
|---|------|
| Push 1 | 读 Story.scope_module 字段（由 §1.5.1 推得）|
| Push 2 | 读命中模块的 `<MODULE>.md`，找该模块涉及的功能点 |
| Push 3 | 读 MODULES.md §3.5，找跨模块边界对照表 |
| Push 4 | scope_module 有 N 个模块 → OBJ 必须覆盖 ≥ N 个模块归属 |

### §1.5.3 FP 模糊语义标注

- `is_assumed: true` + `assumption_reason`（说明来源）
- `ambiguity`（选填，标记未明确区分的业务流，如"邮件通知"未区分类型）

### §1.5.4 OBJ 误标反例强制对照

写 OBJ 前必须扫反例库（BIZ 误判 1-10 / UI 误判 1-5 / HINT 误判 1-8）：

- 与某反例同 pattern → 改 module 或删除
- 与反例无冲突 → 记录"已对照反例 N，无冲突"

### §1.5.5 OBJ 字段名强约束

| 字段 | 要求 |
|------|------|
| `obj_id` | 必填，格式 `{StoryID}-OBJ-{NNN}` |
| `belong_module` | 必填，Enum: CONFIG/UI/BIZ/UTIL/LINK/LOG/SPECIAL/HINT |
| `obj_name` | 必填 |
| `scene` | 必填 |
| `normal_flow` | 必填 |
| `exception_flow` | 必填 |
| `data_change` | 必填 |
| `output_display` | 必填 |
| `verify_method` | 必填 |
| `ambiguity` | 选填 |

### §1.5.6 OBJ 5 问质量 push

每个 OBJ 必须能回答 5 问（任一空答 → 不合格，删除或重写）：

| # | 问题 |
|---|------|
| Q1 | 这个 OBJ 的业务载体是什么？ |
| Q2 | 归属哪个模块？（8 选 1）|
| Q3 | 涉及哪些上下游模块？（scope_module 字段）|
| Q4 | 异常流程有哪些？（SPECIAL/风控/弱网/…）|
| Q5 | 对应 S5 TP 必填哪些字段？（module/test_type/s4_reference）|

---

## §结构化评审包消费逻辑（v16 T4 新增）

> **来源**：`governance/design_iter/plans/v16/s1_review_structured_schema.md`
> **触发时机**：S2 读取 `review_structured.json` 后、Epic/Story 拆分前。

### 读取 + 兼容性

```python
import json, logging
from pathlib import Path

struct_path = stage_dir / "review_structured.json"
structured = json.loads(struct_path.read_text()) if struct_path.exists() else {}

# 字段缺失 → 静默跳过（S1 fallback 机制保证基本可读）
confirmed_boundaries = structured.get("confirmed_boundaries") or []
explicit_assumptions = structured.get("explicit_assumptions") or []
risk_points_preview = structured.get("risk_points_preview") or []
missing_scenarios = structured.get("missing_scenarios") or []
```

### 消费规则

| 源字段 | S2 注入目标 | 注入方式 |
|--------|------------|---------|
| `confirmed_boundaries` | `requirement_objects.json#objects[].boundary_definition` | 每条边界注入同名 OBJ |
| `explicit_assumptions` | `backlog.json#stories[].precondition`（追加） | 带 `is_assumed: true` + `source: "S1.ASM-XXX"` |
| `risk_points_preview` | `backlog.json#summary.risk_seeds` | 透传到 S4（异常树种子）|
| `missing_scenarios` | `backlog.json#stories[].is_assumed` / `need_clarification` | `status=need_clarification` → 警告；`status=assumed` → 自动标注 |

### confirmed_boundaries → OBJ 边界注入

```python
for b in confirmed_boundaries:
    target_obj_id = b.get("source", "")   # 格式: "StoryID-OBJ-NN"
    for obj in objects:
        if obj["id"] == target_obj_id:
            obj["boundary_definition"] = b.get("scope", "")
            obj["_boundary_source"] = f"S1.CB-{b.get('id', '?')}"
```

### explicit_assumptions → Story 前置条件继承

```python
for a in explicit_assumptions:
    for story in stories:
        if a.get("id"):   # ASM-XXX
            story.setdefault("precondition", []).append({
                "text": a["content"],
                "is_assumed": True,
                "assumption_reason": a.get("category", "其他"),
                "confidence": a.get("confidence", "medium"),
                "source": f"S1.{a['id']}"
            })
```

### risk_points_preview → risk_seeds

```python
summary["risk_seeds"] = [
    {
        "area": r.get("area", ""),
        "level": r.get("risk_level", "medium"),
        "reason": r.get("reason", ""),
        "source": f"S1.{r.get('id', '?')}"
    }
    for r in risk_points_preview
]
```

### missing_scenarios 处理

```python
need_cla = [m for m in missing_scenarios if m.get("status") == "need_clarification"]
if need_cla:
    logging.warning(
        f"S1 留下 {len(need_cla)} 个 MSC-XXX（need_clarification）："
        f"{[m.get('id') for m in need_cla]}。"
        f"S2 需确保 S1.5 已处理才能执行。"
    )
assumed = [m for m in missing_scenarios if m.get("status") == "assumed"]
for m in assumed:
    # 注入对应 Story 的 is_assumed 标记
    ...
```

---

## 第二层：Epic（大系统 / 大型业务史诗）

**定义**：完整独立业务域，对应 8 大模块（CONFIG/UI/BIZ/UTIL/LINK/LOG/SPECIAL/HINT，详见 `.cursor/MODULES.md` §1 总表），单一完整系统 / 大型活动。

**粒度（按业务自然划分的三档，禁止硬性卡死工期）**：

| 档位 | 典型场景 | 周期指导 |
|------|----------|----------|
| 重型 Epic | 完整新系统（养成、抽卡、跨服竞技场）、老系统大规模重构 | 2-8 周 |
| 中型 Epic | 中型限时活动、商城重构、配置解析升级 | 1-3 周 |
| 轻型 Epic | 基础提示优化、日志埋点迭代、GM 工具迭代 | 0.25-1 周 |

**ID 格式**：`{Module}-{Number}`，如 `CONFIG-001`（alias `REL-2606-MAIN-01-CONFIG-001` 作为冗余标记，**不影响主 ID**）

**必填元数据**：
- `module`（8 大模块归属）
- `domain`（业务域描述）
- `related_systems`（关联系统列表）
- `release_window`（版本上线窗口）
- `owner`（负责人）
- `risk_level`（P0/P1/P2）
- `scale`（`HEAVY` / `MEDIUM` / `LIGHT`，对应上表三档）

**拆分判定（满足任一条独立成 Epic）**：
1. 跨 3 个及以上模块
2. 交付周期 ≥ 1 周
3. 独立可灰度开关 + 独立配置包
4. 完整闭环业务（产出 - 消耗 - 结算 - 奖励）

---

## 第三层：Story（用户故事，可交付最小业务价值）

**定义**：玩家 / 运营 / GM / 策划可感知的完整闭环价值——一段独立可验收、可灰度、可单独上线的业务能力。

**粒度（按业务自然划分）**：

| 档位 | 典型场景 | 周期指导 |
|------|----------|----------|
| 标准 Story | 90% 游戏需求 | 0.5-3 人天 |
| 微型 Story | 单文案修改、单点埋点、红点修复 | 0.25 人天 |
| 重型 Story | 完整抽卡流程、充值全链路 | 3-7 人天 |

**ID 格式**：`{EpicID}-{StoryNumber}`，如 `CONFIG-001-001`（alias `{ReleaseID}-{EpicID}-S{StoryNumber}`）

**游戏行业增强必填字段**：

| 字段 | 说明 | 必须 |
|------|------|------|
| `id` | 唯一编码 | ✅ |
| `title` | **标准化用户故事句式**：`作为[角色]，我希望[功能]，以便[价值]` | ✅ |
| `user_role` | 角色（玩家 / 运营 / GM / 策划） | ✅ |
| `precondition` | 前置依赖（配置 / 系统 / 版本 / 权限） | ✅ |
| `input_data` | 触发输入（玩家操作、配置参数、后台指令、网络场景） | ✅ |
| `acceptance_criteria` | ≥ 2 条，**区分三类**（开发验收 / 测试验收 / 策划数值验收） | ✅ |
| `scope_module` | 涉及的 8 大模块列表（多模块则后续 OBJ 自动拆分） | ✅ |
| `risk` | 风险等级 + 依赖项 | ✅ |
| `expected_output` | 业务最终产出（界面展示 / 数据变更 / 日志 / 奖励） | ✅ |
| `offline_verify` | 是否支持离线配置验证（`true` / `false`） | ✅ |
| `source` | 来源：`original` / `clarification` / `fallback` | ✅ |

**合法 vs 不合法**：
- ✅ 合法 Story：作为玩家，我希望完成每日任务领取积分奖励，以便兑换商城道具
- ❌ 不合法：每日任务红点显示（仅局部 UI，属于下层 Object）

---

## 第四层：Object（Story 内拆分单元）

**定义**：Story 内部**独立业务载体 / 独立场景域**，载体之间无强耦合、可单独验证、分属不同模块 / 不同交付对象。常见载体分类：配置表、页面弹窗、业务服务流程、第三方渠道交互、风控异常场景、埋点采集逻辑、缓存 / 热更逻辑、GM 操作能力。

**ID 格式**：`{StoryID}-OBJ-{两位自增序号}`，如 `CONFIG-001-001-OBJ-01`
（alias：`REL-2606-MAIN-01-CONFIG-001-S001-OBJ-01`）

**Object 数量**：**不设任何区间约束**，数量由下方"拆分判定规则 + 落地约束"自然产出。

---

### 拆分判定规则（唯一依据，不靠主观"简单/复杂"）

满足**任意一条**，必须拆分独立新 Object：

1. **归属顶层 8 大模块不同**（CONFIG/UI/BIZ/UTIL/LINK/LOG/SPECIAL/HINT 之一不同；详见 `MODULES.md` §1）
2. **业务载体完全隔离**（例：任务配置表、任务领取服务逻辑、任务奖励弹窗是 3 类完全独立载体）
3. **验证链路完全独立**（配置可用 Excel 工具校验、业务逻辑需要客户端操作、埋点需要日志平台查看——三者必须分开）
4. **交付责任人不同**（配置策划 / 前端 / 服务端 / 测试埋点 / 风控，分人开发验收）
5. **正常流程与异常 / 风控场景解耦**（正向领取奖励归 BIZ，弱网领取失败、作弊拦截归 SPECIAL，拆为两个 Object）

> **关键转变**：数量是"按规则自然产出的结果"，不是"拆解前必须遵守的硬性规则"。本末倒置的"先定区间再拆"被彻底删除。

---

### 落地约束（解决拆分随意、过度拆分两种极端问题）

**约束 1：禁止过度拆分（无意义碎片化）**
- 同一个模块、同一个载体、同一套验证链路 → **不允许拆多个 Object**
- ❌ 错误示例：同一弹窗内红点、飘字、按钮提示同属 HINT 载体，被拆 3 个 OBJ
- ✅ 正确做法：合并为 1 个 HINT Object，内部用多条 FP 区分不同提示能力

**约束 2：禁止过度合并（多载体揉进同一个 Object）**
- 一个 Object 只能对应**一类业务载体**
- ❌ 错误示例：把"配置表 + 服务业务 + 第三方渠道"塞进一个 OBJ
- ✅ 正确做法：按上方 5 条判定规则强制拆分

**约束 3：边界模糊兜底（不强行凑数 / 不强行合并）**
无法判定是否拆分新 Object 时，**不强行凑数量**，执行两步评审：

1. 标注 `[待确认-Object拆分边界]`，列明两种拆分方案、差异影响
2. 同步主策划 / AI 拆解规则管理员评审，**归档判定结论**，更新团队标准案例库

---

### 实战示例：玩家充值购买礼包完整全链路

按 5 条判定规则，**自然产出 13 个 Object**（不卡 12 上限、不强行合并）：

| OBJ ID | 归属模块 | obj_name | 业务载体 |
|--------|----------|----------|----------|
| OBJ-01 | CONFIG | 礼包档位配置表校验 | 配置表 |
| OBJ-02 | UI | 充值商城礼包页面布局 | 页面 |
| OBJ-03 | BIZ | 下单 / 订单创建 / 库存扣减 | 服务流程 |
| OBJ-04 | LINK | 渠道 SDK 支付拉起 / 订单回调 | 第三方渠道 |
| OBJ-05 | SPECIAL | 重复下单 / 篡改金额 / 作弊拦截 | 风控 |
| OBJ-06 | BIZ | 支付成功后道具 / 货币发放事务 | 服务流程 |
| OBJ-07 | HINT | 充值成功弹窗 / 资源飘字 | 提示 |
| OBJ-08 | LOG | 付费资产流水 / 充值行为埋点 | 埋点 |
| OBJ-09 | UTIL | 本地支付凭证缓存 / 断线续单 | 底层能力 |
| OBJ-10 | SPECIAL | 退款回滚 / 异常订单兜底 | 风控 |
| OBJ-11 | LINK | 渠道付费数据对账同步 | 第三方渠道 |
| OBJ-12 | HINT | 付费失败 Toast | 提示 |
| OBJ-13 | BIZ | 累充进度同步 / 累充奖励自动发放 | 服务流程 |

> 旧规则"复杂最多 12 个"会强制合并其中 2 个独立载体，导致单个 OBJ 混杂多模块逻辑，FP 拆解和测试用例生成出现交叉混乱。

---

### 游戏行业 9 标准必填字段

| 字段 | 含义 | 说明 |
|------|------|------|
| `obj_name` | 对象名称 | （旧字段：`name` / `对象名称`） |
| `belong_module` | 归属 8 大核心模块（CONFIG/UI/BIZ/UTIL/LINK/LOG/SPECIAL/HINT；详见 `MODULES.md` §1） | **单选**；多模块业务按规则 1 拆多 OBJ |
| `scene` | 业务场景描述 | 该对象所处的业务场景 |
| `input` | 触发输入条件 | 触发该对象的输入 / 前置 |
| `normal_flow` | 正向标准流程 | 输入→处理→输出 |
| `exception_flow` | 全分支异常流程 | 异常输入→处理→输出（兜底 / 重试 / 降级 / 风控） |
| `data_change` | 数据变更范围 | **5 选一**：`配置` / `内存` / `DB` / `缓存` / `第三方` |
| `output_display` | 对外表现 | 5 选多：`UI 弹窗` / `飘字` / `日志` / `推送` / `后台数据` |
| `verify_method` | 验证手段 | 5 选多：`配置工具` / `客户端操作` / `GM 指令` / `抓包` / `日志平台` |

> **字段迁移说明**：
> - 原 `object_states`（对象状态拆解）→ 拆分为 `normal_flow` 的状态分支 + `exception_flow` 的异常分支
> - 原 `interaction_forms`（交互形态）→ 合并到 `normal_flow` / `exception_flow` 流程中
> - 原 `business_logic`（业务逻辑）→ 改名为 `normal_flow`（语义更精准：流程而非逻辑）
> - 原 `exception_boundaries`（异常业务边界）→ 合并到 `exception_flow`
> - 原 `exception_interactions`（异常交互）→ 合并到 `exception_flow`
> - 原 `module_inference`（关联模块推理）→ 简化为 `belong_module`（单选）
> - 原 `logs_and_tracking`（日志与埋点）→ 拆分为 `data_change`（数据）+ `output_display`（日志部分）
> - 原 `related_protocols`（关联协议）→ 合并到 `normal_flow` / `exception_flow`
> - 原 `object_name` 字段名 → 改 `obj_name`

---

## 第五层：FP（功能点，最小不可拆分执行单元）

**定义**：需求对象 Object 内最小单一校验 / 开发单元，对应单条开发逻辑、单条测试用例、单条配置规则。

**粒度（按业务自然拆分，无强制 3-8 限制）**：
- 极简 OBJ：1-2 个 FP（单文案修改、单点红点）
- 复杂 OBJ：8-15 个 FP（跨表配置校验、全链路支付流程）

**ID 格式**：`{ObjectID}-FP-{N}`，如 `CONFIG-001-001-OBJ-1-FP-1`

**游戏行业 3 标准字段**：

| 字段 | 含义 | 说明 |
|------|------|------|
| `fp_desc` | 功能描述 | 一句话描述该 FP 做什么 |
| `check_type` | 校验类型 | `配置` / `界面` / `业务` / `日志` / `安全` 五选一 |
| `verify_standard` | 单一验收标准 | 一条可断言的标准（出现"且/同时/另外"必须拆分） |

> **粒度控制硬规则**（防 AI 凑数 / 拆细）：
> - 一个 FP 只描述**单一动作 / 单一规则**
> - 出现"且、同时、另外" → **必须拆分新 FP**
> - 例：❌ "下拉展示道具，道具不足置灰按钮" → ✅ 拆分为 FP1（渲染）+ FP2（置灰）+ FP3（Toast）

**派生链**（与原范式保持一致，可机检）：
- 每个 FP 必须能溯源到 Object 的某个字段（normal_flow / exception_flow / data_change / output_display / verify_method）
- 派生链写入 `requirement_objects.md` 的「FP 派生链」段
- 字段级覆盖：5 个核心字段每个至少派生 ≥ 1 个 FP；不足则标【待补充】+ 原因
- `summary.feature_point_count` 必须 == `Σ FPs`，否则 **S2 失败**

### §UI 占比统计（S3 模式选择辅助）

> **SSOT**：`.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3 `AIDOCX_S3_UI_THRESHOLD`

S2 拆解完成后，在 `backlog.json#summary` 段必须输出 `ui_ratio` 字段，供 S3 模式选择判断：

```json
{
  "summary": {
    "epic_count": 4,
    "story_count": 12,
    "feature_point_count": 38,
    "ui_ratio": 0.42,
    "ui_story_count": 5,
    "s3_mode_recommend": "depth",
    "s3_mode_reasons": [         // （可审计决策链）
      "UI Story count = 5 / total = 12 → ui_ratio = 0.42 > 0.30"
    ]
  }
}
```

**计算规则**：
- `ui_story_count = Σ(Story.module == "UI")`
- `ui_ratio = ui_story_count / story_count`
- `s3_mode_recommend = "depth" if ui_ratio > 0.30 else "lightweight"`
- `s3_mode_reasons = [判定原因字符串...]`（便于审计，避免黑箱）

> ⚠️ 仅为推荐值——用户可设置 `AIDOCX_S3_MODE=lightweight|depth` 强制覆盖。

---

## 统一边界判定流程（替代单纯 [待确认] 标注）

### 第一步：模块快速匹配（8 大模块归属判定，按优先级匹配——仅用于 Epic 主模块判定）

> ⚠️ **重要**：本表是 **Epic 层级**的"主模块判定"优先级，**不是** S5 TP 层级 module 字段的判定。
> S5 TP 字段判定见 [`.cursor/MODULES.md` §3.5 交叉场景归属判定规则](../../MODULES.md) 和 [`.cursor/skills/aidocx-s5-test-points/SKILL.md` §1.2](../../skills/aidocx-s5-test-points/SKILL.md) 模块 × 类型双维度判定。
>
## §1.4 8 模块总表（必读，代替原自动同步区块）

**S2 LLM 必须先 Read `.cursor/MODULES.md` §1 总表 + §4 各模块 O_boundary.md。8 模块 ID 前缀 + 职责边界**：

| # | 模块 | ID 前缀 | 职责边界 |
|---|---|---|---|
| 1 | 配置 | `CONFIG` | 配置表/字段/枚举/ID 合法性；同表/全表/环境一致性；跨表 ID 依赖；解析与加载；数值逻辑；热更；版本兼容与灰度；导出/导入/发布；服务端业务配置 |
| 2 | 界面 | `UI` | 纯前端 UI 层：控件/状态/交互/布局/静态展示/动效/引导/无障碍/异常场景 |
| 3 | 业务 | `BIZ` | 服务端业务逻辑/数据流/协议/状态机/DB 持久化/并发事务/付费/定时任务/业务联动 |
| 4 | 辅助 | `UTIL` | 底层公共工具/框架；网络/缓存/资源/汇率/GM/本地存档/性能/离线包/加密/崩溃兜底（**仅底层**）|
| 5 | 关联 | `LINK` | 内部业务联动/跨服务同步/多端一致性/第三方对接/跨模块资源互通/异步消息/灰度隔离/对外数据透出（**与 UTIL 严格隔离**）|
| 6 | 特殊情境 | `SPECIAL` | 异常/高危/对抗/极限/合规/资源耗尽业务容错；反作弊；弱网/限流；前后台；宕机 Failover/高危；版本兼容；渠道灰度；防沉迷 |
| 7 | 日志 | `LOG` | 行为埋点/资产审计/操作留痕/监控/崩溃/分级/完整性对账/脱敏/trace/安全反作弊/第三方链路（**底层 SDK 归 UTIL**）|
| 8 | 提示 | `HINT` | 红点/角标/飘字/Toast/模态弹窗/浮动通知/限时提醒/错误文案/新手引导/社交/运营推送/状态变更/合规/离线补偿（**与 UI 严格隔离——仅临时弹出**）|

**ID 前缀说明**：
- `CONFIG / UI / BIZ / UTIL / LINK / SPECIAL / LOG` — 用作 Epic ID 前缀（如 `CONFIG-VIP-001`）
- `HINT` — **不**用作 Epic ID 前缀；HINT 仅作为 `scenario_test_points[].module` 字段的取值

### 第二步：跨模块场景处理（一条 Story/OBJ 多模块 → 拆多 OBJ）

一条业务同时涉及多模块时，**不标[待确认]，直接按模块拆多个独立 Object**：

**示例**——"领取任务奖励"Story 拆分为 4 个 OBJ：
- `OBJ01 (CONFIG)`：任务奖励配置表字段校验
- `OBJ02 (BIZ)`：服务端扣发奖励、更新任务状态落地 DB
- `OBJ03 (HINT)`：弹出奖励汇总弹窗 + 资源飘字
- `OBJ04 (LOG)`：产出资产流水埋点记录

### 第三步：无法匹配任一模块（兜底流程）

1. 填写【边界判定表】：列出 2 个候选模块、冲突场景、不确定原因
2. 标注 `[待确认-模块归属]`，绑定对应主策划 / 主测负责人
3. **24 小时内**完成评审，评审后更新模块归属并拆分 Object，**禁止长期搁置**
4. 评审记录归档到 `release` 元数据中，作为后续拆解参考标准

---

## 输入审查（门禁前置条件）

| 检查项 | 要求 | 缺失时 |
|--------|------|--------|
| exit_permission.json 存在 | 必须存在 | 生成失败报告 |
| can_proceed_to_s2 == true | P0 反馈已填写 | 生成失败报告 |
| 终版需求.md 存在 | 内容完整 | 生成失败报告 |
| Epic 数量 | ≥ 1 | 生成失败报告 |
| 每个 Story 有 ≥ 2 条 AC | 必须满足（区分三类验收） | 补充提示 |
| 每个 Object 9 字段完整 | obj_name/belong_module/scene/input/normal_flow/exception_flow/data_change/output_display/verify_method | 标注缺失项 |
| Object 字段命名符合新范式 | 必须使用 `belong_module`/`normal_flow`/`exception_flow`/`data_change`/`output_display`/`verify_method` | 字段重命名 |
| 模块归属单选 | `belong_module` 单选；多模块则拆多 OBJ | 强制拆分 |
| 物量守恒 | `summary.feature_point_count` == `Σ FPs` | S2 失败 |
| 派生链完整 | 每个 Object 在 requirement_objects.md 中显式列出"从哪些字段派生出了哪些 FP" | 补充派生链 |
| 字段级 FP 覆盖 | Object 5 个核心字段（normal_flow / exception_flow / data_change / output_display / verify_method）每个至少派生 ≥ 1 个 FP | 字段旁标【待补充】+ 原因 |

---

## 产出模版（v18.3 新增）

> **模版来源**：`knowledge/public/module_templates/s2_output_template.md`（固定模版，强制遵循）
>
> 本阶段 3 个产出文件（backlog.json / backlog.md / requirement_objects.json）的结构、字段、格式必须符合模版规定。
> 详见模版文件的 §1-§3（完整结构定义）+ §5（验收检查清单）。

---

## 成功产出

| 文件 | 路径 |
|------|------|
| backlog.md | `workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.md` |
| backlog.json | `workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.json` |
| requirement_objects.md | `workflow_assets/<req_name>/<version>/「S2 需求拆解」/requirement_objects.md` |
| requirement_objects.json | `workflow_assets/<req_name>/<version>/「S2 需求拆解」/requirement_objects.json` |

### backlog.json 新顶层字段

```json
{
  "version": "v2.0",
  "release": {
    "id": "REL-2606-MAIN-01",
    "type": "MAIN",
    "cycle": "大版本",
    "window": "2026-06 上线窗口",
    "owner": "主策/主测 姓名"
  },
  "epics": [
    {
      "id": "CONFIG-001",
      "module": "CONFIG",
      "scale": "HEAVY" | "MEDIUM" | "LIGHT",
      "domain": "VIP 等级体系",
      "related_systems": ["VIP", "支付"],
      "release_window": "2026-06",
      "owner": "主策张三",
      "risk_level": "P0",
      "stories": [
        {
          "id": "CONFIG-001-001",
          "title": "作为 VIP 玩家，我希望查看当前等级权益，以便了解可用折扣",
          "user_role": "玩家",
          "acceptance_criteria": [
            {"type": "开发验收", "desc": "..."},
            {"type": "测试验收", "desc": "..."},
            {"type": "策划数值验收", "desc": "..."}
          ],
          "scope_module": ["BIZ", "UI"],
          "risk": {"level": "P1", "depends": ["支付系统"]},
          "offline_verify": true
        }
      ]
    }
  ]
}
```

### requirement_objects.json 新 Object 字段

```json
{
  "id": "CONFIG-001-001-OBJ-1",
  "obj_name": "VIP 等级查询",
  "belong_module": "BIZ",
  "scene": "玩家在 VIP 页面查询当前等级",
  "input": "玩家登录态 + 玩家 ID",
  "normal_flow": "查询 DB → 读取 VIP 配置表 → 返回等级权益",
  "exception_flow": "DB 异常 → 返回缓存旧数据 + 提示刷新",
  "data_change": "DB（VIP 表读）",
  "output_display": "UI 页面（等级徽章 + 权益列表）",
  "verify_method": "客户端操作 + 配置校验工具",
  "feature_points": [
    {
      "id": "CONFIG-001-001-OBJ-1-FP-1",
      "fp_desc": "正确读取玩家当前 VIP 等级",
      "check_type": "业务",
      "verify_standard": "VIP 页面等级显示与 DB 一致"
    }
  ]
}
```

---

## 完整分层示例

**Release**: `REL-2606-MAIN-01` 6 月主线大版本
**Epic**: `REL-2606-MAIN-01-CONFIG-002` 夏日活动配置体系（中型 Epic，2 周）
**Story**: `REL-2606-MAIN-01-CONFIG-002-S001` 玩家可领取夏日每日任务积分

**OBJ01 (CONFIG)** 夏日任务配置表校验：
- FP01：任务 ID 全局唯一不重复（check_type: 配置）
- FP02：奖励道具 ID 跨表依赖校验（check_type: 配置）
- FP03：每日次数上限数值约束校验（check_type: 配置）

**OBJ02 (BIZ)** 每日任务完成与积分发放逻辑：
- FP01：完成任务标记落地数据库（check_type: 业务）
- FP02：积分发放、背包道具新增事务锁（check_type: 业务）
- FP03：跨零点重置每日任务次数（check_type: 业务）

**OBJ03 (HINT)** 任务完成奖励提示：
- FP01：完成任务弹出奖励汇总弹窗（check_type: 界面）
- FP02：获取积分弹出积分飘字（check_type: 界面）

**OBJ04 (LOG)** 任务资产流水埋点：
- FP01：积分产出记录审计日志（check_type: 日志）
- FP02：任务完成行为埋点上报客户端（check_type: 日志）

---

## 失败报告

路径：`workflow_assets/<req_name>/<version>/「S2 需求拆解」/fail_report_S2.md`

---

## 自动化支持

```python
from ai_workflow.conversation_skills import save_stage2_output
save_stage2_output(version, req_text, raw_output, parsed, req_name)
```

---

## 执行卡（v14 单阶段执行卡样板 — 4 区块合一）

> **派生产物**：本卡由 `scripts/sync_execution_cards.py` 同步管理，源文件为 `.cursor/rules/STAGE_S2_BREAKDOWN.mdc`。
> **修改原则**：改源文件 `.mdc`，然后跑同步脚本刷新本卡；禁止直接改本卡（除自动同步外）。

<aside data-exec-card-block="input_gate" data-src=".cursor/rules/STAGE_S2_BREAKDOWN.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

> ⚠️ **派生产物，禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成
> src: `.cursor/rules/STAGE_S2_BREAKDOWN.mdc` | sha256: `INIT_seed` | synced_at: `2026-07-14`
> 修改请改源文件 (`.cursor/rules/STAGE_S2_BREAKDOWN.mdc`)，然后跑 `python3 scripts/sync_execution_cards.py --stage s2-breakdown` 重新同步。

### 输入门禁（input_gate）

| 必备材料 | 路径 | 缺失处理 |
|---|---|---|
| 终版需求.md | `workflow_assets/<req_name>/<version>/「S1 需求评审」/终版需求.md` | 生成 fail_report_S2.md，停止 |
| S1.5 准出许可 | `workflow_assets/<req_name>/<version>/「S1 需求评审」/exit_permission.json` | `can_proceed_to_s2=false` → 停止 |
| clarification_checklist.md | `workflow_assets/<req_name>/<version>/「S1 需求评审」/clarification_checklist.md` | 警告，不阻断 |
| 8 模块决策树（v14） | `knowledge/public/module_templates/_decision_tree.md` | 拆 OBJ 错误率 +50% |

**触发命令**：`/aidocx-s2-breakdown` 或粘贴 S1.5 准出许可路径

</aside>

<aside data-exec-card-block="field_required" data-src=".cursor/rules/STAGE_S2_BREAKDOWN.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

> ⚠️ **派生产物，禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成

### 必填字段（field_required）

| 字段 | 级别 | 校验 |
|---|---|---|
| `Epic.id` / `Epic.title` | **MUST** | 缺失 → fail_report_S2.md |
| `Story.id` / `Story.title` / `Story.module` | **MUST** | module 必为 8 模块全名 |
| `Story.user_role` / `Story.business_scenario` | **MUST** | v10+ 必填 |
| `OBJ.id` / `OBJ.title` / `OBJ.module` | **MUST** | 拆 OBJ 前先跑决策树两步法 |
| `FP.id` / `FP.test_type` / `FP.priority` | **MUST** | v11+ 必填（与 S5 链路对齐） |

#### P0/P1/P2 优先级判定规则

> **来源**：外部方案 §4.5.1。S2 拆解 FP 时必须按以下标准标注优先级。

| 优先级 | 判定标准（满足任一即可） | 覆盖率要求 |
|--------|--------------------------|------------|
| **P0** | ① 涉及支付 / 资产变更 ② 主流程核心路径 ③ 故障会导致 P0 级线上事故 | ≥ 95%（刚性，不可例外） |
| **P1** | ① 重要功能模块的常规流程 ② 常用配置项 ③ 故障影响用户体验但不阻塞核心 | ≥ 80%（柔性，可申请例外） |
| **P2** | ① 边缘场景 / 展示类 ② 低频操作 ③ 降级兜底路径 | ≥ 50%（指导值，不做强求） |

**回退路径**：
- S7 审查员可推翻 S2 标注的 FP 优先级
- 推翻时必须填写 `priority_correction_reason` 字段
- 同一类优先级错误出现 ≥ 3 次 → 触发 S2 判定规则优化迭代

**SSOT**：`scripts/check_field_completion.py --stage s2`（待扩展，目前 S2 复用 S5 脚本结构）

</aside>

<aside data-exec-card-block="quality_gate" data-src=".cursor/rules/STAGE_S2_BREAKDOWN.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

> ⚠️ **派生产物，禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成

### 质量门禁（quality_gate）

| 门禁 | 阈值 | 三步自问例外 |
|---|---|---|
| Epic 拆解精度 | ≥ 0.90 | 未达 → 三步自问 → bypass_log.json 备案 |
| FP 全覆盖（S5 链路）| 1.0（v11+） | 未达 → 三步自问 |
| 模块归属错误率 | ≤ 0.05（v14 目标） | 通过决策树两步法控制 |

**门禁常量 SSOT**：`DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.3 + §4.3

</aside>

<aside data-exec-card-block="naming" data-src=".cursor/rules/STAGE_S2_BREAKDOWN.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

> ⚠️ **派生产物，禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成

### ID 命名规范（naming）

| 层级 | 格式 | 示例 |
|---|---|---|
| Release | `<req_name>-<version>` | `游戏道具商城系统-v1.0` |
| Epic | `Epic-<NN>` | `Epic-01`, `Epic-02` |
| Story | `{EpicID}-{NN}` | `01-01`, `01-02` |
| Object | `{EpicID}-{StoryNN}-OBJ-<NN>` | `01-01-OBJ-01` |
| FP | `{OBJ-ID}-FP-<N>` | `01-01-OBJ-01-FP-1` |

**禁止**：旧 4 字母缩写（`biz` / `ui`）→ 必须 8 模块全名大写

</aside>

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S2_BREAKDOWN.mdc`
- Prompt 模板：`ai_workflow/prompts/requirement_breakdown.md`（待建）
