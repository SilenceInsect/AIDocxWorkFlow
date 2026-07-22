---
name: aidocx-s6-test-cases
description: >
  AIDocxWorkFlow Stage 6 — 测试用例生成。LLM 读 S5 test_points + S4 业务流 + 8 模块子模板，推理出测试用例（不设硬性 1:N / 不强制 18 种方法），脚本仅做 ID 分配 / 字段归一化 / 输出 JSON+MD+XLSX。
  使用当用户执行 /aidocx-s6-test-cases、粘贴 S5 test_points.json、或进行 S6 测试用例生成任务。
disable-model-invocation: true
  Use when the user runs /aidocx-s6-test-cases, pastes S5 test_points.json, or starts test case generation.
  使用当用户执行 /aidocx-s6-test-cases、粘贴 S5 test_points.json、或进行 S6 测试用例生成任务时。
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: s6-test-cases
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

## 🔴 命名继承一致性铁律（字段溯源版 — 最高优先级，违反直接 L1 打回）

> **NAME-FIELD-001**：本节是命名追溯性修复的核心约束。S6 TC 必须从 S5 TP 继承正式 OBJ/FP 名称字段，且必须有显式字段，继承链路才算完整。
> **校验精度**：字段溯源版（字段精准匹配——obj_name == 源 TP）+ LLM 自由文本溯源（test_scenario 不带锚点）
>
> **v28 修订注**：约束① `fp_name` 必须 100% 等于 S2 `fp_desc`（v26 §判定 ①）已于 **Round 15 F-F 删除 fp_name 字段**（约束已变空对象，本节规则 1/3 已同步注明）；约束④ `s5_ref` 必填单值（v26 §判定 ④）放宽为 `s5_ref` 单值 或 `tp_references[]` 数组二选一；约束② `steps[]` 结构化数组强制（v26 §判定 ②）放宽为允许字符串数组；约束③ `test_method[]` 字符串数组强制（v26 §判定 ③）放宽为允许单字符串 或 字符串数组。约束⑤ `preconditions[]` 维持。详见 `governance/design_iter/plans/v28/GOAL.md`。

### 一、核心基准规则

#### 规则 1：TC 必须包含显式字段 obj_name 和 feature_point_ref

每条 TC 必须有以下两个字段，从源 TP 原样继承：
- `obj_name`：从源 TP.obj_name 取值（100% 原样继承，最终来源 = S2 obj_name）
- `feature_point_ref`：从源 TP.feature_point_ref 取值（100% 原样继承，最终来源 = S2 FP ID）
- `fp_name` 字段已 Round 15 F-F 删除（`feature_point_ref` 已结构化足以反查 FP）——历史字段，仅作 v3.01 legacy 兼容

#### 规则 2：test_scenario 不带锚点（纯场景文本）

格式：纯场景一句话描述
- **禁止** test_scenario 以 `【OBJ - FP】` 锚点开头
- 锚点仅存 JSON 字段（obj_name / feature_point_ref），不重复进文本
- TC.obj_name 必须 == TP.obj_name（继承性）

#### 规则 3：名称必须继承，不得改写

- TC.obj_name **必须从源 TP.obj_name 原样继承**（最终来源 = S2 obj_name，100% 逐字相等）
- TC.feature_point_ref **必须从源 TP.feature_point_ref 原样继承**（结构化 FP ID，反查 FP 元数据）
- 禁止在生成过程中"优化"、简化、意译
- 禁止从 TP 到 TC 的过程中丢失正式名称字段
- `fp_name` 字段已 Round 15 F-F 删除（不再要求继承）——历史字段治理

### 二、字段格式模板

#### test_scenario 字段
```
{纯场景一句话描述}（不带锚点）
```
示例：
- 源 TP.obj_name = "商城首页道具列表"，TP.fp_name = "首页销量排序展示"
- 生成 TC：test_scenario = "玩家进入商城首页，验证道具列表按销量降序排列"

### 三、自检流程（输出前必须执行）

生成完所有 TC 后，逐条检查：

| 检查项 | 通过标准 |
|--------|---------|
| obj_name 字段存在 | TC.obj_name == 源 TP.obj_name（继承性，最终 == S2 obj_name） |
| feature_point_ref 字段存在 | TC.feature_point_ref == 源 TP.feature_point_ref（继承性，反查 FP） |
| **assertion 字段 ≥ 1**（Round 15 F-E 新增） | TC.assertion 数组长度 ≥ 1，每项含 `assertion_type` 必填字段 |
| test_scenario 无锚点 | 开头不是【xxx - xxx】格式 |
| OBJ 字段正确 | TC.obj_name = S2 obj_name（逐字相等，继承自 TP） |
| FP 字段正确 | TC.feature_point_ref = TP.feature_point_ref（继承自 TP，结构化 FP ID） |

**批量统计要求**：
- 字段继承一致性 = 100%
- assertion 覆盖率 = 100%（每 TC ≥ 1 assertion）
- 锚点分离率 = 100%（test_scenario 不含【】）
- 不达标则逐条修正，直到达标再输出

**批量统计要求**：
- 字段继承一致性 = 100%
- 锚点分离率 = 100%（test_scenario 不含【】）
- 不达标则逐条修正，直到达标再输出

### 四、常见错误对照表

| 错误类型 | 错误示例 | 正确示例 |
|---------|---------|---------|
| test_scenario 带锚点 | "【道具搜索功能 - 支持道具名称模糊搜索】验证搜索结果正确" | "搜索结果正确验证" |
| 锚点丢失 | TP：obj_name="A"/feature_point_ref="B" → TC：无 obj_name/feature_point_ref 字段 | TC 字段完整继承自 TP |
| 锚点改写 | TP：obj_name="A"/feature_point_ref="B" → TC：obj_name="A'"/feature_point_ref="B'" | TC.obj_name/feature_point_ref 100% 继承 |
| 简化 FP 名 | TP：feature_point_ref="BIZ-PURCHASE-01-001-OBJ-01-FP-1" → TC：feature_point_ref="FP-1" | TC.feature_point_ref = TP.feature_point_ref 完整继承 |
| 缺少 obj_name 字段 | TC 无 obj_name 字段 | TC.obj_name = "商城首页道具列表"（继承自 TP） |
| 缺少 feature_point_ref 字段 | TC 无 feature_point_ref 字段 | TC.feature_point_ref = TP.feature_point_ref 完整继承 |
| 含历史 fp_name 字段（Round 15 F-F 警告） | TC：{..., "fp_name": "首页销量排序展示"} | TC 不含 `fp_name`（已 Round 15 F-F 删除，用 `feature_point_ref` 反查） |
| 缺 assertion 字段（Round 15 F-E 警告） | TC：{..., "expected_results": ["..."]} 无 assertion | TC.assertion 数组 ≥ 1 项，每项含 `assertion_type` 必填 |

### 五、L1 校验入口

校验函数：`ai_workflow/validators/l1_s6.py` 的 `L1S6Validator.validate_field_traceability()`
调用方式：
```python
from ai_workflow.validators.l1_s6 import L1S6Validator
v = L1S6Validator()
v.set_requirement_objects_and_tp_list(objs, tps)
passed, errors, stats = v.validate_field_traceability(test_cases)
# passed=True 且 errors=[] 才可进入 S7
```

### 六、Schema 要求

每条 TC 必须包含以下字段：

```json
{
  "case_id": "UI-TC-001",
  "s5_ref": "TP-001",
  "obj_name": "商城首页道具列表",
  "feature_point_ref": "BIZ-PURCHASE-01-001-OBJ-01-FP-1",
  "test_scenario": "玩家进入商城首页，验证道具列表按销量降序排列",
  ...
}
```

> **字段语义说明（Round 14 F-D 修订）**：
> - `case_id`：S6 TC 唯一主键（**唯一 ID**）
> - `tc_id`：历史冗余字段，**新版本请忽略**——决策档 `governance/design_iter/current/s6_id_dedupe_decision.md` 推荐方案 A：保留 case_id 作为唯一 ID
> - v3.01 JSON 仍含 `tc_id`（out_of_scope 不动 JSON），新生成 TC 不再含该字段
>
> **`fp_name` 字段（Round 15 F-F 修订）**：
> - `fp_name` 已于 Round 15 F-F 删除（feature_point_ref 已结构化足以反查 FP）
> - 历史字段：`fp_name`（人类可读 FP 名）—— 与 `feature_point_ref` 双字段冗余，治理类删除
> - 一致性约束：`l1_format_validator.check_no_fp_name_field`（默认 WARN 模式兼容 v3.01 legacy；`--new-only` ERROR 模式强约束新数据）
> - v3.01 JSON 仍含 `fp_name`（out_of_scope 不动 JSON），新生成 TC 不再含该字段
> - 同步修订：`§NAME-FIELD-001` 规则 1/3 描述已改（"fp_name 字段已 Round 15 F-F 删除，请用 `feature_point_ref` 反查"）
>
> **`assertion` 字段（Round 15 F-E 新增 · 机器可读断言）**：
> - 每条 TC **必须**含 ≥ 1 个 `assertion`（数组），QA 可直接执行断言验证，无需人工翻译 `expected_results` 文本
> - 必填子字段：`assertion_type`（枚举：numeric / string_contains / enum_match / regex_match / range_check / exists_check）
> - 可选子字段：`assertion_target`（验证目标字段，如 `balance` / `error_msg` / `order_status`）、`expected_value`、`operator`
> - 示例 1（数值）：`{"assertion_type": "numeric", "assertion_target": "balance", "operator": "==", "expected_value": 0}`
> - 示例 2（字符串包含）：`{"assertion_type": "string_contains", "assertion_target": "error_msg", "expected_value": "余额不足"}`
> - 示例 3（枚举匹配）：`{"assertion_type": "enum_match", "assertion_target": "order_status", "expected_value": "PAID"}`
> - 示例 4（正则匹配）：`{"assertion_type": "regex_match", "assertion_target": "log_line", "expected_value": "^\\[ERROR\\].*支付失败.*$"}`
> - 一致性约束：`l1_format_validator.check_assertion_completeness`（默认 min_count=1，ERROR 模式）
> - v3.01 JSON 暂未含 `assertion` 字段（属 Round 16+ 数据迁移范围，本轮 out_of_scope 不动 JSON）

---

## §生成前必答 · 思维约束（v3.02 新增 · 强制）

> **背景**：Agent 的默认工作模式是「找字段模板 → 填引用 → 套格式 → 结束」。
> 这个模式产出的是「看起来合规的废话」——字段全填了，但操作步骤、预期结果、前置条件都在套模板，没有传递任何有用的测试意图。
> S5 的字段溯源铁律已经能保证 TC 不丢失 OBJ/FP 名称字段，但**仍然无法阻止 Agent 在步骤和预期里写废话**。
> 本节是从根子上改变这个模式的约束——强制 Agent 在生成内容前先思考、再动笔。

### 核心约束

**在写每一条 TC 之前，先用一句话回答这个问题**：

> "这套操作步骤 + 这个预期结果，能不能让一个没看过 S5/S4/S2 的人复现这个测试？"

如果答不出来——说明在套模板，不是在写测试用例。回去重写。

### 5 条强制规则

| # | 规则 | 反例 | 正例 |
|---|------|------|------|
| 1 | **操作步骤必须含具体 UI 元素名或具体数值**（禁止「执行操作/执行测试/验证预期结果」模板）| "1. 执行操作\n2. 验证预期结果" | "1. 点击【购买】按钮\n2. 弹窗显示道具名称='屠龙刀'、价格=500金币\n3. 输入数量=99" |
| 2 | **预期结果必须含具体可断言内容**（禁止「无/系统正常响应/预期结果正确」占位或循环）| "无" / "系统正常响应" / "预期结果正确" | "弹窗关闭，余额=300游戏币，道具A数量+1，玩家收到邮件通知" |
| 3 | **前置条件必须填具体初始状态**（禁止「无/无特殊」占位）| "无" | "玩家已登录，余额=500游戏币，道具A库存=99，VIP=0" |
| 4 | **禁止照抄 S4 节点编号**（S4 是参考源，不是引用源）| "[S4-1.3.2] 异常分支" | "余额不足时弹出'余额不足，请充值'提示，购买按钮置灰" |
| 5 | **每条 TC 必须有 ≥ 1 个 assertion**（机器可读断言）| 无 assertion 字段 | `assertion: [{assertion_type: "numeric", assertion_target: "balance", operator: "==", expected_value: 0}]` |

### 反模式示例（任一命中 → 该 TC 不合格）

| 反模式 | 描述 |
|--------|------|
| 泛化描述 | "系统正常响应" / "验证XX正常" / "功能正常" |
| 模板语言 | "执行操作" / "执行测试" / "验证预期结果" / "准备符合XX的环境" |
| 占位文本 | 操作步骤/预期结果/前置条件 = ["无"] / ["无特殊"] |
| 循环定义 | "预期结果正确" / "系统按预期响应" |
| S4 引用 | 字段中含 `[S4-xxx]` / `[风险R-001]` 类节点编号 |
| 复制粘贴型 | 多条 TC 的操作步骤高度相似（仅改 OBJ/FP 名） |

### Bad pattern 检测（强制阻断）

`L1S6Validator.validate_bad_patterns()` 自动检测上述反模式，任一命中即阻断（BLOCK 级别）。

调用入口：
```python
from ai_workflow.validators.l1_s6 import L1S6Validator
v = L1S6Validator()
v.set_requirement_objects_and_tp_list(objs, tps)
errors = v.validate_bad_patterns(test_cases)
# errors 非空 → 该 TC 不合格，必须重写
```

### 自检清单（生成 TC 后必走）

写完所有 TC 后，逐条检查：

- [ ] 每条 TC 的操作步骤都能让我（没看过 S5 的人）知道具体点哪个按钮、输什么值
- [ ] 每条 TC 的预期结果都是可断言的具体内容（数值/字符串/枚举/状态变化）
- [ ] 每条 TC 的前置条件都有具体初始状态
- [ ] 没有任何 TC 的预期含 `[S4-xxx]` 节点编号引用
- [ ] 不同 TC 的操作步骤没有「只改 OBJ/FP 名，其他完全相同」的复制粘贴
- [ ] 每条 TC 都有 ≥ 1 个 assertion

**任一项不通过 → 重写该 TC，再继续**。

---

# AIDocxWorkFlow S6 — 测试用例生成

> **设计哲学**：
> - **LLM 负责推理**：从 S5 TP 派生出几个 TC、用什么方法、步骤怎么写——全是 LLM 推理决定
> - **脚本只负责整理与门禁**：ID 分配 / 字段归一化 / 写文件 / stage_context / read_ack / coverage gate
> - **不设硬比例**：1:1 也行、1:5 也行、1:20 也行——业务复杂度自然决定
> - **coverage-first**：不设硬比例 ≠ 可以收缩覆盖；默认目标是闭合覆盖缺口，而不是最少用例

**独立阶段**：可单独调用。上游材料（S5 test_points.json）审查合格后开始，失败写失败报告。

## 第一原则

你当前不是在做代码实现，也不是在写最短答案，而是在闭合需求覆盖缺口。
任何没有被测试用例覆盖的点，必须进入 `omission_ledger.json`，不允许静默消失。

---

## §1.4 必读材料与违规认定

> ⚠️ **违反本节禁令 → 产出不合格，必须补读后重新生成。**

### 违规认定（满足任一 → 产出不合格）

- ❌ 未读取本节材料，直接凭印象生成
- ❌ 跳过标注"强制"的材料，用其他来源替代
- ❌ 产出的 module / s4_reference 与材料内容明显不符
- ❌ 用"业务常识"替代必须读取的材料

### 必读材料清单

**生成测试用例前，必须先 Read 以下材料。禁止凭印象直接生成。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| ① | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| 所有 TP 必须有模块前缀；模块 × 类型双维度决定 TC 拓宽方向 |
| ② | 模块边界区分 | `.cursor/MODULES.md`（§4 各模块 O_boundary.md）| HINT vs UI、BIZ vs CONFIG 是 S6 高误标区；判定前必读 |
| ③ | S5 test_points（强制） | `workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json` | 每个 TP 的 module / test_type 是 TC 拓宽的输入；未读取 → 无法拓宽 |
| ④ | S4 business_flow（强制） | `workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md` | 异常决策树和风险点是 EXCEPTION TC 的核心来源 |
| ⑤ | 命中模块子模板 | `knowledge/public/module_templates/<Module>/<Module>.md` | 子类枚举决定 TC 方法选择 |

## 运行顺序（强制）

1. 先生成并读取 `stage_context.md` / `stage_context.json`
2. 再写 `read_ack.json`
3. 再读取 S5 的 `coverage_ledger.json` / `omission_ledger.json`（如存在）
4. 再生成 `test_cases.json`
5. 生成 `test_cases.json` 和 `test_cases.xlsx`（公共默认强制产物）；只有确认具体项目且存在项目级导出配置时，才额外生成 `test_cases.md`
6. 最后刷新 `coverage_ledger.json` / `omission_ledger.json`

缺少前 2 步任一项，不允许开始正式 TC 设计。

---

## §5 一致性检查（SKILL ↔ Rule 自动对齐）

> **触发时机**：本节读取后、正式执行前。**仅执行一次**（同一次对话中多次触发本阶段，不重复检查）。

**检查类型**：A = 必读材料对齐 / B = 输出路径对齐 / C = 字段名对齐 / D = 模块枚举对齐

```python
from ai_workflow.consistency_check import run_consistency_check

result = run_consistency_check(stage="s6")
if not result["passed"]:
    print(f"[一致性检查] 发现 {len(result['issues'])} 个问题（见日志）")
```

检查结果不阻断阶段执行，仅输出到日志供人工参考。

---

## §1.6 评审门禁触发（强制，不可跳过）

S6 执行时，**每个产物生成后必须立即触发对应门禁检查**。跳过任一检查即提交 → 该产物不合格。

### 产物 → 门禁检查 → 失败动作

| 产物 | 门禁检查 | 失败时动作 |
|------|---------|-----------|
| `test_cases.json` | 运行 `auto_reviewer.snapshot()` 并检查 `fill_rate ≥ 90%` | 触发三步自问；若依然无法提升，允许带理由放行（见下文例外条款）|
| `test_cases.md` | 对比 md 中 TC 数量与 json 一致 | 回 LLM 迭代 md |
| `test_cases.xlsx` | 检查文件存在且可被 openpyxl 打开 | fail_report_S6.md |

### fill_rate < 90% 的例外条款：三步自问

> 脚本统计的是"字段是否填写"，但业务上有些字段确实无值可填（如无前置条件、无边界值）。
> 因此允许 LLM 经"三步自问"论证后带理由放行。

当 `fill_rate < 0.9` 时，进入以下决策树：

```
fill_rate < 90%
 ↓
[三步自问]
 Q1：该字段在本业务场景下是否实际存在？
   → 存在 → 必须填，回 LLM 补充
   → 不存在 → 进入 Q2
 Q2：S5 TP 是否提供了该字段的来源信息？
   → 有 → 必须填，回 LLM 补充
   → 无 → 进入 Q3
 Q3：该字段缺失是否影响测试用例的可执行性？
   → 影响 → 必须填，回 LLM 补充
   → 不影响 → 允许放行，记录 skip_reason
```

- **Q1/Q2 回答"存在"或"有"** → 回 LLM 迭代 json，禁止生成 xlsx
- **Q1/Q2 回答"不存在"且 Q3 回答"不影响"** → 允许放行，备案到 `bypass_log.json`（路径：`workflow_assets/<req_name>/<version>/「S6 测试用例生成」/bypass_log.json`）

### 脚本入口（必须在 LLM 生成产物后立即执行）

```python
from ai_workflow.auto_reviewer import snapshot
from pathlib import Path

tc_path = Path("workflow_assets/<req_name>/<version>/「S6 测试用例生成」/test_cases.json")
bd_path = Path("workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.json")
tp_path = Path("workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json")

snap = snapshot(tc_path, bd_path, tp_path)

# 读取事实数字（禁止跳过此步骤直接写报告）
print(snap.ai_input_summary)
print(f"[S6 GATE] TC 填写率: {snap.structure.fill_rate:.1%}")
if snap.structure.fill_rate < 0.9:
    print(f"[S6 GATE] 填写率 {snap.structure.fill_rate:.1%} < 90%")
    print("[S6 GATE] 触发三步自问（见 §1.6 例外条款）")
    # → 进入三步自问决策树，LLM 判断是否可放行
```

### 用例状态职责边界（Round 12 修订 · 在 Round 22 锁定基础上）

- `用例状态` 字段只在 L1∧L2 / S7 / S8 写回时变更；**S7 审查报告本身不修改 `test_cases.json`**。
- S6 L1∧L2 写回：`L1S6Validator.run_l1_check().passed == true` **AND** `L2S6Validator`（`evaluate_status` 的 `l2_mode` 默认 `"lenient"`）无该 case 的 failed_id → `Ready`；否则 `Draft`。详见 `case_status_writer.apply_l1_l2_status_per_case`（Round 12 新增，per-case 写回取代 bulk）。
- S7 Rejected 写回：当 `recommendations.must_fix[]` 至少一条 `severity == MUST_FIX` 时，`Ready → Rejected`（详见 `s7_status_writer.py`）。`apply_l1_l2_status_per_case` 不会覆盖 `Rejected` / `Deprecated`。
- S8 Deprecated 写回：S8 迭代流程赋值（仅 S8 领地）。
- 禁用枚举：`discarded`（与 `Deprecated` 语义重叠，已废弃）。
- 禁止读取或依赖已废除的 `overall` / `overall_pass` 字段。

#### l2_mode 三档（与 SKILL.md §NAME-FIELD-001 SSOT 对齐）

| mode | 行为 | 适用场景 |
|---|---|---|
| `"lenient"`（默认） | L2 PASS = SSOT 字段齐全（`obj_name` / `fp_name` / `s5_ref` / `obj_id` / `feature_point_ref`），不要求文本锚点 | v17 字段溯源版生成的数据 / v3.01 legacy 经 normalizer 后 |
| `"strict"` | L2 PASS = 文本锚点（`【OBJ-XXX】`）+ 步骤动词 + 预期断言 token（保留 `l2_s6.run_l2_check` 原行为） | v15 时代数据 / Round 11 测试覆盖 |
| `"off"` | 跳过 L2，回退 L1-only（`apply_l1_status` 旧 API 等价） | 旧调用方兼容 |

**SSOT 优先级（v17+ 字段溯源版）**：`l2_mode="lenient"` 是 SSOT 默认路径。SKILL.md §NAME-FIELD-001 明确"test_scenario 不带锚点"，因此 strict 模式的锚点检查与 SSOT 冲突，仅作旧数据兼容路径保留。

#### legacy 数据前置归一化（Round 12 新增）

`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` 等 legacy 产物（English 字段名 + `TC-NNN` case_id）**不**满足 L1S6Validator 的中文字段 + 模块前缀 ID 校验，必须先经 `ai_workflow.case_id_and_field_normalizer.normalize_payload()` 归一化再喂给 L1∧L2 链路。该归一化是**幂等 in-memory** 操作，不修改源 JSON（遵守 `goal_s6_case_status_redefinition.md §out_of_scope` §10）。

驱动入口：`ai_workflow/run_normalize_and_export.py`（包含 `--self-test` argv）；端到端 surrogate：`workflow_assets/test_s6_status/v1.0/「S6 测试用例生成」/run_round12_e2e.py`。

### 公共 xlsx 单会话入口（Round 22 锁定）

`ai_workflow/test_case_formatter.py` 暴露 `--tc-json-to-xlsx` 子命令，强制走 `_DEFAULT_XLSX_PROFILE` 与 `_XLSX_HEADERS_V3`，不受项目级 profile 覆盖。

```bash
python3 ai_workflow/test_case_formatter.py --tc-json-to-xlsx <tc.json> \
    [--xlsx-output <output.xlsx>]
```

- 主 Sheet（按 profile `sheet_name`，公共为 `测试用例`）：仅 `Ready`。
- 附录 Sheet（固定 `Draft-Rejected附录`）：`Draft` + `Rejected`。
- `Deprecated` 不进入执行 Sheet，仍留在 JSON 真相源。
- 支持 3 种 tc.json 结构：顶层 list / `{test_cases:[...]}` / `{meta:...,test_cases:[...]}`。

### 禁止行为

- ❌ 跳过 `snapshot()` 直接输出产物
- ❌ 跳过门禁检查直接生成 xlsx
- ❌ 在未经三步自问的情况下直接放行
- ❌ 三步自问 Q1/Q2 回答"存在"或"有"时仍放行
- ❌ 因为"实现可能共用逻辑"而合并不同需求对象的测试意图
- ❌ 因为"代码层已覆盖"而省略产品层测试设计
- ❌ 因为不确定而静默省略；必须记录到 omission ledger
- ❌ S6 脚本硬编码 `用例状态` 值；状态必须由 `case_status_writer` 写回
- ❌ 用项目级 profile 覆盖公共 `--tc-json-to-xlsx` 的表头/Sheet 结构

## 强制账本

- `coverage_ledger.json`：按 Story 记录 expected/covered scenario families、covered_by、status
- `omission_ledger.json`：记录所有 partial/uncovered 点和原因

每个 Story 默认至少要有：
- 一条主路径
- 一条风险路径

如果没有，必须在 omission ledger 写明原因。

---

## §1.5 决策 push 块

> **哲学**：不告诉 LLM 多少算合格，告诉 LLM 怎么思考产出质量。
>
> ⚠️ **未走 Push 即写 TC → 该 TC 不合格。**

| # | 操作 | 目的 |
|---|------|------|
| Push 1 | 读 S5 test_points.json，确认每个 TP 的 module / test_point_type | 确认 TC 拓宽输入 |
| Push 2 | 读 MODULES.md §3.5，确认模块归属无误 | 防止 HINT vs UI 误标 |
| Push 3 | 读命中模块的 `<MODULE>.md`，匹配子类枚举，决定 TC 方法 | 确认 TC 方法 |
| Push 4 | 读 S4 业务流，找到 EXCEPTION TC 的风险场景来源 | 异常流覆盖 |

**4 步全部回答后，再开始写 TC。**

---

> **16 种方法学体系**：
>
> | # | 方法学 | 核心思路 | 主要适用 |
> |---|---|---|---|
> | 1 | 等价类划分（equivalence） | 把输入域划分为等价类，从每类取代表值 | 输入枚举 |
> | 2 | 边界值分析（boundary） | 取等价类边界（边界-1/边界/边界+1/最小/最大/0/空/null） | 数值/长度/时间 |
> | 3 | 判定表驱动（decision_table） | 条件/动作穷举组合 | 多条件业务规则 |
> | 4 | 因果图（cause_effect_graph） | 输入→结果因果关系 | 复杂逻辑依赖 |
> | 5 | 正交实验法（orthogonal） | N 因子 K 水平正交覆盖 | 多参数组合 |
> | 6 | 状态迁移测试（state_transition） | 状态机合法/非法转换 | 状态机业务 |
> | 7 | 状态转换覆盖（switch_coverage） | N-switch / 0-switch 路径覆盖 | 状态机深度 |
> | 8 | 路径覆盖（path_coverage） | 语句/分支/条件/路径 | 流程逻辑 |
> | 9 | 场景法（scenario） | 业务场景模拟 | E2E 业务流 |
> | 10 | 错误猜测（error_guessing） | 基于经验列可能错误 | 防御性测试 |
> | 11 | 探索性测试（exploratory） | 边测边设计 | 不可预知场景 |
> | 12 | 基于检查表（checklist） | 通用检查清单（UI/兼容性/无障碍） | UI/兼容性 |
> | 13 | 基于需求/规格（specification） | 严格按需求逐项 | 合规测试 |
> | 14 | 基于风险（risk_based） | 高风险优先覆盖 | 优先级排序 |
> | 15 | 基于经验（experience） | 测试人员经验库（历史缺陷） | 回归缺陷 |
> | 16 | 变异测试（mutation） | 注入故障验证检测 | 鲁棒性/容错 |
>
> **每个 TC 在 JSON 中必须声明以下三个字段**：
> - `test_method`：测试方法（如"等价类划分" / "边界值分析" / "等价类+边界+判定表+状态迁移"）
> - `methodology_tag`：方法学 tag 数组，必须含 ≥ 4 个 tag（从 16 种枚举中）
> - `methodology_reason`：为什么选这 4 种方法的理由（≤ 80 字）
>
> **覆盖率门禁（违反任一 → S6 不合格）**：
> 1. 每个功能（Story/requirement_object）的 TC 集合，`methodology_tag` union 后必须 **≥ 4 种**（从 16 种枚举中）
> 2. 每条 TC 自身 `methodology_tag` 长度 **≥ 2**
> 3. 16 种方法学中**至少 8 种**必须在某个 TC 中出现（业务广度）
> 4. 未达 → 回 LLM 迭代，禁止生成 xlsx
>
> **禁用模式**（不构成覆盖）：
> - ❌ TC 全是"等价类"一种方法学 → 必须配 3 种以上
> - ❌ `methodology_tag` 长度 < 2 → 不合格
> - ❌ 全局 16 种中只出现 4 种以下 → 不合格
> - ❌ 16 种中只有"等价类/边界/状态迁移"这老 3 件套 → 不合格
> - ❌ HINT 模块用 `HINT-TC-NNN` 前缀（**HINT 不作前缀**——HINT 仅作 module 字段值，前缀必须从 8 模块其他中取）

### §1.5.1 边界值展开规则

**四点法（默认规则）**：有明确数值范围 `[min, max]` 的输入字段，必须展开为 **4 条独立 TC**：

| TC 序号 | 类型 | 输入取值 | 预期结果 | test_point_type |
|---------|------|---------|---------|-----------------|
| TC-01 | 最小有效值 | 输入 = min | 验证通过 | BOUNDARY_MIN |
| TC-02 | 最大有效值 | 输入 = max | 验证通过 | BOUNDARY_MAX |
| TC-03 | 最小无效值 | 输入 = min - 1（或最小粒度减 1）| 验证拒绝 | BOUNDARY_MIN_1 |
| TC-04 | 最大无效值 | 输入 = max + 1（或最小粒度加 1）| 验证拒绝 | BOUNDARY_MAX_1 |

**六点法（核心字段 / 高风险字段）**：增加标称值和零值检查：

| TC 序号 | 类型 | 说明 |
|---------|------|------|
| TC-05 | 标称值 | 输入 = (min + max) / 2 取整 |
| TC-06 | 零值 | 输入 = 0（特殊边界） |

**不同数据类型取值规则**：

| 类型 | 范围示例 | 边界值 |
|------|---------|--------|
| 整数 | [1, 9999] | min=1, max=9999, min-1=0, max+1=10000 |
| 浮点/金额 | [0.01, 9999.99]，精度2位 | min=0.01, max=9999.99, min-0.01=0.00, max+0.01=10000.00 |
| 字符串长度 | [1, 50] 字符 | min=1, max=50, min-1=0(空串), max+1=51 |
| 枚举 | [A, B, C] | 每个枚举值各1条正向 TC；非法枚举值/null/空另1条异常 TC |
| 列表/数组 | [0, 100] 个元素 | min=0(空数组), max=100, max+1=101 |

**隐式边界（主动检查，即使需求未明确写）**：

| 隐式边界类型 | 检查内容 |
|------------|---------|
| 零值 | 0 / 0.00 / 空字符串 / 空数组 |
| 负数 | -1 / -0.01（数值字段） |
| 极大值 | 接近数据类型上限（如 int32 max）|
| 特殊字符 | SQL注入字符 / XSS字符 / emoji / 换行符 |
| 空白字符 | 首尾空格 / 全角空格 / 制表符 |
| null / undefined | 不传值 / 传 null |
| 类型不匹配 | 数字字段传字符串 / 字符串字段传数字 |

**多字段组合边界**：每个字段各自展开 4 条边界 TC（单字段边界验证）+ 关键字段组合 1-2 条组合边界 TC（多字段同时取边界值）。组合边界不替代单字段边界。

### §1.5.2 正交表选型与展开规则

**基本概念**：因素（Factor）= 影响结果的输入变量；水平（Level）= 每个因素的取值个数。

**正交表选型决策树**：

| 因素数 | 水平 | 正交表 | 实验次数 |
|--------|------|--------|---------|
| 2因素 | 直接全组合 | 2×水平数 | 量少不用正交 |
| 3-4因素 | 全2水平 | L4(2^3) 或 L8(2^7) | 4-8次 |
| 3-4因素 | 全3水平 | L9(3^4) | 9次 |
| 3-4因素 | 混合水平 | L8(2^4×4^1) 等混合表 | 8次 |
| 5-7因素 | 全2水平 | L8(2^7) | 8次 |
| 5-7因素 | 全3水平 | L18(3^7×2^1) 或 L27(3^13) | 18-27次 |
| 7+因素 | — | L16 / L18 / L27 起步 | — |

**正交实验生成步骤**：
1. 识别因素和水平（例：3因素×3水平 → L9(3^4)，9条用例）
2. 选正交表模板（按因素数×水平数查表）
3. 映射实际值（1/2/3 替换为实际枚举值）
4. 每行正交实验 → 1 条 OA 类型 TP → 1 条 TC

**选型原则**：够用就好（选能容纳所有因素的最小正交表）、水平对齐优先、混合水平用混合表或拟水平法降水平处理、2因素以内直接全组合更简单。

### §1.5.3 判定表驱动法展开规则

**适用场景**：多条件组合决定一个结果、业务规则复杂有多个分支、条件之间有逻辑与/或关系、权限控制/校验规则/计费逻辑。

**不适用**：单条件简单逻辑（直接等价类）、纯数值输入（边界值更合适）、流程类测试（场景法）、状态机类（状态迁移）。

**生成步骤**：
1. **提取条件桩和动作桩**：从 FP 描述中找出所有输入条件（C1/C2...）和所有可能的输出动作（A1/A2...）
2. **确定规则数**：n 个条件各2种取值（Y/N）→ 2^n 条初始规则
3. **填充初始判定表**：每条规则是条件的一个组合，填入对应动作
4. **合并化简**：动作相同的规则组（如只有1个条件取值不同）→ 合并，该条件标记为 "-"（无关）；多轮合并直到不能再合并；动作不同的规则绝对不能合并
5. **生成 TP**：每条化简后的规则 → 1 条 TP；test_point_type：正向规则=POSITIVE，负向规则=NEGATIVE

**示例（优惠券使用规则，4个条件→化简为5条规则）**：

| 规则 | C1(有效期) | C2(门槛) | C3(支持) | C4(权限) | 动作 |
|------|-----------|---------|---------|---------|------|
| R1 | Y | Y | Y | Y | 抵扣成功 |
| R2 | Y | Y | Y | N | 无权限 |
| R3 | Y | Y | N | - | 商品不支持 |
| R4 | Y | N | - | - | 未满足门槛 |
| R5 | N | - | - | - | 已过期 |

### §1.5.4 状态迁移测试展开规则

**适用场景**：订单生命周期、用户账号状态、审批流程、游戏状态机。

**四级覆盖等级**：

| 覆盖等级 | 覆盖内容 | 用例数 | 适用场景 |
|---------|---------|--------|---------|
| L1 状态覆盖 | 每个状态至少到达一次 | = 状态数 | 最低要求 |
| **L2 转换覆盖** | 每条转换至少执行一次 | = 转换数 | **标准要求，默认** |
| L3 转换对覆盖（0-switch）| 每两个相邻转换组合至少一次 | = 转换对数 | 核心状态机 |
| L4 路径覆盖 | 所有可能路径 | 指数级 | 极核心功能 |

**L2 转换覆盖生成步骤**：
1. 从需求/流程图提取所有状态和事件，构建状态迁移矩阵（行=当前状态，列=事件，格=下一状态）
2. 识别所有有效转换（非"-"的格子）
3. 每条转换生成1条 TC：前置状态构造 + 触发事件 + 预期状态 + 预期动作
4. 每个状态下选1-2个典型非法事件验证（已终态再触发、非法转换）
5. 高风险状态机升到 L3：覆盖所有相邻转换对（T1→T2, T1→T3...）

**示例（订单状态机，7个状态+7个事件→8条转换+非法转换验证）**：

| 转换 | 前置状态 | 事件 | 预期状态 | 预期动作 |
|------|---------|------|---------|---------|
| T1 | S0待创建 | 创建订单 | S1待支付 | 生成订单号 |
| T2 | S1待支付 | 支付成功 | S2已支付 | 扣减库存 |
| T3 | S1待支付 | 支付失败 | S1待支付 | 重试提示 |
| T4 | S1待支付 | 取消订单 | S5已取消 | 释放库存 |
| T5 | S2已支付 | 发货 | S3已发货 | 更新物流 |
| T6 | S2已支付 | 申请退款 | S6已退款 | 回滚库存 |
| T7 | S3已发货 | 确认收货 | S4已完成 | 完成交易 |
| T8 | S3已发货 | 申请退款 | S6已退款 | 回滚物流 |

### §1.5.5 TP → TC 展开总表与 Prompt 片段

**按 test_point_type 匹配展开策略**：

| test_point_type | 展开 TC 数 | 核心展开规则 |
|----------------|-----------|------------|
| EP_VALID | 1-2 条 | 典型有效值输入，验证通过 |
| EP_INVALID | 每类 1 条 | 每个无效维度各一条，验证错误提示 |
| BOUNDARY_MIN / BOUNDARY_MAX / BOUNDARY_MIN_1 / BOUNDARY_MAX_1 | **各 1 条** | 按 §1.5.1 四点法独立展开，禁止合并 |
| OA_2N / OA_3N / OA_MIXED | 正交表行数 | 每行组合 1 条 TC |
| POSITIVE | 1 条 | 主路径从头到尾成功 |
| NEGATIVE | 每条分支 1 条 | 每个失败分支各一条 |
| EXCEPTION | 1-2 条 | 异常注入 + 恢复验证 |
| PERFORMANCE | 1-3 条 | 响应/并发/吞吐各一条 |
| SECURITY | 2-5 条 | 越权/注入/敏感数据等 |
| CONFIG | 每维度 2 条 | 默认值 + 变更后各一条 |
| LOG | 1-2 条 | 验证日志字段完整性 |

**铁律**：
- 每个 TP 独立展开，**禁止跨 TP 合并**
- **禁止按 obj_id 聚合多条 TP 到一条 TC**
- 边界值 4 种类型必须各自生成独立 TC，不能合并
- TC 命名格式：`{Module}-TC-{NNN}` 或 `{Module}-TC-{TP_ID}-{序号}`

**方法学标签映射表**：

| TC 类型 | 必选方法 | 可选补充方法 |
|---------|---------|-------------|
| 输入校验类（EP/BOUNDARY）| 等价类划分 + 边界值分析 | 错误猜测法 |
| 业务流程类（POSITIVE）| 场景法 + 基于规格 | 路径覆盖 |
| 异常类（NEGATIVE/EXCEPTION）| 错误猜测法 + 边界值分析 | 基于风险 |
| 组合类（OA）| 正交实验法 + 等价类划分 | 判定表驱动 |
| 状态机类（状态迁移）| 状态迁移测试 + 路径覆盖 | 场景法 |
| 规则类（判定表）| 判定表驱动 + 基于规格 | 因果图 |
| 性能/安全专项 | 基于风险 + 基于经验 | 探索性测试 |

## §1.6 自检清单（提交前必走）

> **v31 修订**：`用例描述` = backlog.epics[].title；`功能描述` = backlog.stories[].title。

| 字段 | 定义 | 内容要求 |
|------|------|----------|
| **用例描述** | Epic 标题 = 需求对象（**必须是实体名词**）| 来自 `S2 backlog.epics[].title`，禁止加后缀、禁止加括号、禁止任何分隔符；**必须是实体名词**（如"退款订单"而非"退款处理"，"商城首页"而非"首页展示"） |
| **功能描述** | Story 标题 = 功能特性（**必须是动词/动作**）| 来自 `S2 backlog.stories[].title`；**禁止名词性描述**（如"道具数据配置"应改为"道具从配置加载"） |
| **前置条件** | 进入用例前系统所处的初始状态 | 具体数值（余额=xxx、道具备注=xxx），**禁止"无"占位**（除非业务确实无前置条件） |
| **操作步骤** | 玩家或策划的具体行动 | **每步包含具体 UI 元素名或具体数值**；禁止 `执行测试场景`/`验证预期结果`/`执行操作` 等模板语言 |
| **预期结果** | 操作后系统应产生的行为 | **纯业务结果**；禁止引用 S4 编号，禁止括号说明；**一 TC 一预期原则**（每条 TC 的 `expected_results` 数组只含 1 项），禁止多条预期并置 |
| **steps** | 操作步骤字段（v28 放宽） | **每条 TC 的 `steps` 字段允许两种形态**：① 结构化数组（必须含至少 2 个元素 `{step_num:N, action:...}`： ● 步骤 1：操作（触发行为） ● 步骤 2：验证（执查结果） ● 步骤 3+：可选（较界条件、异常路径等） ▂ **禁止**：1 步 1 TC ② 字符串数组（兼容 v3.01 legacy，按原 TC 出现顺序拼接）。**Round 15 例外条款**：当 `{obj_id, feature_point_ref, test_scenario}` 三元组完全相同的同源 TC 在 v3.01 数据中被拆成多步时，导出前允许合并为 1 条多步 TC；steps 数组含 1~N 元素（按原 TC 出现顺序拼接），expected_results 含 1~N 项。详见 §11.1 同源合并例外条款。 |
| **test_method** | （可选）LLM 标注的测试方法 | 自由字符串，例如"等价类划分" / "异常流容错"——**不强制必须填** |
| **test_scenario** | （可选）方法下的具体场景 | 自由字符串，例如"空值" / "边界+1" / "超时30s"——**不强制必须填** |
| **obj_id** | S2 需求对象 ID | **必填**——S2 `requirement_object.id`（如 `BIZ-001-001-OBJ-01`），未填 → S6 不合格 |
| **feature_point_id** | S2 OBJ 的 FP ID | 当 TC 对应某 FP 时必填——S2 `requirement_object.feature_points[].id`（如 `BIZ-001-001-OBJ-01-FP-2`） |
| **s5_ref** / **tp_references**（v28 放宽） | S5 TP 引用 | **必填**（`s5_ref` 单值 或 `tp_references[]` 数组均合法）。① `s5_ref`：单 TP 引用，值 = S5 `scenario_test_points[].tp_id`（如 `BIZ-001-001-TP-001`），通过 `s5_ref.feature_point_ref` 推导 FP。② `tp_references[]`：数组形态，支持单 TP 时长度 = 1，多 TP 引用时长度 ≥ 2，向后兼容 v3.01 legacy 单值写法。**优先使用 `s5_ref`**（SSOT）；`tp_references[]` 为扩展形态，仅在多 TP 合并 TC 场景下使用。 |
| **obj_name** | TC 继承的需求对象名称 | **从源 TP.obj_name 继承**（100% 原样继承），最终来源 = S2 obj_name，禁止改写/简化 |
| **feature_point_ref** | TC 继承的功能点引用 | **从源 TP.feature_point_ref 继承**（100% 原样继承），结构化 FP ID，反查 FP 元数据 |
| **fp_name**（Round 15 F-F 删除） | TC 继承的功能点名称 | **已删除**——新数据不再含 `fp_name` 字段；历史 v3.01 JSON 仍含（out_of_scope 不动 JSON）；用 `feature_point_ref` 反查 FP 名 |
| **assertion**（Round 15 F-E 新增） | 机器可读断言数组 | **必填 ≥ 1 项**，每项含 `assertion_type` 必填子字段；QA 可直接执行断言验证 |

### §S3→TC / S4→TC 字段溯源（字段溯源版 必填）

> **SSOT**：本节是 §S3→TC / §S4→BIZ TC 工作流在 S6 阶段的落地条款。
> **历史 §S5→S6 链路 + 双层覆盖门禁条款已停止生效**——S6 TC 按"模块来源"分类引用。

### §UI TC 4 字段模板（UI 模块必填）

每个 UI TC **必须**包含以下 4 字段：

```json
{
  "case_id": "UI-TC-P002-btn-01",
  "module": "UI",
  "用例标题": "道具详情页 - 点击购买按钮 - 余额充足",
  "page_id": "P-002",                    // 必填：S3 page_id
  "node_id": "P-002-button-01",          // 必填：S3 UI 节点 ID
  "操作": "点击【购买】按钮",              // 必填：LLM 推理（点击/输入/滑动/...）
  "预期": "弹出购买确认弹窗 P-003",        // 必填：LLM 推理（界面状态/数据/弹窗）
  "前置条件": "余额 ≥ 道具价格",            // 选填
  "priority": "P0"
}
```

**字段溯源**：

| 字段 | 上游来源 | 校验 |
|---|---|---|
| `page_id` | S3 prototype.md §UI 节点清单 | 必填；必存在 S3 页面列表 |
| `node_id` | S3 prototype.md §UI 节点清单 | 必填；必属于该 page_id |
| `操作` | LLM 推理 | 不预设边界——穷举所有可能 |
| `预期` | LLM 推理 | 不预设边界——穷举所有可能 |

**L3 覆盖率门禁**：
- `ui_page_coverage = TC 引用的 page 数 / prototype.md 页面数 ≥ 1.0`
- `ui_node_coverage = TC 引用的 node 数 / prototype.md §UI 节点清单节点数 ≥ 1.0`

### §BIZ TC 4 层引用模板（BIZ 模块必填）

> **用户原话**："什么叫各一个模板，AI 能想出来多少就多少，不要省 token"
> **字段溯源版不预设 BIZ TC 模板边界**——LLM 按 scenario + state + exception + risk 4 层引用穷举所有可能 TC。

每个 BIZ TC **至少 1 个** S4 引用字段必填：

```json
{
  "case_id": "BIZ-TC-SC001-01",
  "module": "BIZ",
  "用例标题": "正常购买游戏币道具 - 主流程",
  "s4_ref": {
    "scenario_id": "SC-001",                // 必填：S4 scenario
    "state_ref": "SM-001:待支付→已支付",     // 选填：S4 状态机迁移
    "exception_ref": null,                   // 选填：S4 异常决策树叶子
    "risk_ref": null                         // 选填：S4 风险点 ID
  },
  "操作步骤": [...],                          // 必填
  "预期结果": [...],                          // 必填
  "priority": "P0"
}
```

**4 层引用语义**：

| 层 | 含义 | 适用 TC 类型（不预设边界）|
|---|---|---|
| `scenario_id` | 主流程场景 | 正常购买/正常退款/正常升级 |
| `state_ref` | 状态机迁移 | 状态转换类：待支付→已支付、待支付→已退款 |
| `exception_ref` | 异常决策树叶子 | 异常类：余额不足/SDK 失败/超时 |
| `risk_ref` | 风险点 ID | 高风险类：风控拦截/超时补单/VIP 叠加 |

**LLM 推理态度**：
- **4 层字段至少有 1 个必填**（通常 scenario_id 必填）
- **LLM 可按场景自由组合**——如"scenario + exception"组合（"正常购买 + 余额不足"边界场景）
- **不省 token**——LLM 想出多少 BIZ TC 就多少

**L3 覆盖率门禁**：
- `scenario_coverage = TC 引用的 scenario 数 / S4 scenarios 数 ≥ 1.0`
- `state_machine_coverage = TC 引用的 state 数 / S4 state_machine states 数 ≥ 1.0`
- `exception_tree_coverage = TC 引用的 exception leaf 数 / S4 exception leaf 总数 ≥ 1.0`
- `risk_point_coverage = TC 引用的 risk 数 / S4 risk_points 总数 ≥ 1.0`

### §11 test_point_type → TC 字段映射规范（永久强制）

> **目的**：S5 test_point_type 是「测试方法学」的分类标签，S6 必须把这个标签落到**具体 TC 字段**——这是"正反例落到测试用例产出规范"的强制落地。

#### 字段映射表（永久 SSOT）

| test_point_type | TC test_method 字段（v28 放宽：单字符串 或 字符串数组） | TC test_scenario 字段 | TC 操作步骤模板（v28 放宽：结构化数组 或 字符串数组） | 适用模块 |
|---|---|---|---|---|
| `EP_VALID` | "等价类划分-有效类" | "取有效等价类代表值" | 1. 输入有效数据<br>2. 执行操作<br>3. 验证通过 | UI/BIZ/CONFIG |
| `EP_INVALID` | "等价类划分-无效类" | "取无效等价类代表值" | 1. 输入无效数据<br>2. 执行操作<br>3. 验证拒绝 | UI/BIZ/CONFIG |
| `BOUNDARY_MIN` | "边界值分析-最小有效" | "min 边界点" | 1. 输入边界值=min<br>2. 执行操作<br>3. 验证通过 | BIZ/SPECIAL |
| `BOUNDARY_MAX` | "边界值分析-最大有效" | "max 边界点" | 1. 输入边界值=max<br>2. 执行操作<br>3. 验证通过 | BIZ/SPECIAL |
| `BOUNDARY_MIN_1` | "边界值分析-min-1" | "min-1 越界点" | 1. 输入边界值=min-1<br>2. 执行操作<br>3. 验证拒绝 | BIZ/SPECIAL |
| `BOUNDARY_MAX_1` | "边界值分析-max+1" | "max+1 越界点" | 1. 输入边界值=max+1<br>2. 执行操作<br>3. 验证拒绝 | BIZ/SPECIAL |
| `OA_2N` | "正交试验-L4(2^3)" | "2因素×2水平组合" | 1. 取正交表 4 行<br>2. 依次执行<br>3. 验证全部组合 | BIZ/LINK |
| `OA_3N` | "正交试验-L9(3^4)" | "3因素×3水平组合" | 1. 取正交表 9 行<br>2. 依次执行<br>3. 验证全部组合 | BIZ/LINK |
| `OA_MIXED` | "正交试验-混合水平" | "N×M 混合水平组合" | 1. 取混合正交表<br>2. 依次执行<br>3. 验证全部组合 | BIZ |
| `POSITIVE` | "正向流程" | "标准主流程" | 1. 进入功能<br>2. 按主流程操作<br>3. 验证业务结果 | UI/BIZ/SPECIAL |
| `NEGATIVE` | "负向流程" | "拒绝分支" | 1. 输入不当数据<br>2. 执行操作<br>3. 验证拒绝逻辑 | UI/BIZ |
| `EXCEPTION` | "异常流容错" | "系统异常场景" | 1. 模拟异常<br>2. 验证重试/回滚/告警 | BIZ/LINK/LOG |
| `PERFORMANCE` | "性能测试" | "响应时间/并发量" | 1. 准备性能场景<br>2. 执行<br>3. 验证指标 | BIZ/UTIL |
| `SECURITY` | "安全测试" | "注入/越权/签名伪造" | 1. 构造攻击向量<br>2. 执行<br>3. 验证拒绝 | SPECIAL/LINK |
| `CONFIG` | "配置变更测试" | "配置生效验证" | 1. 修改配置<br>2. 等待生效<br>3. 验证行为变化 | CONFIG |
| `LOG` | "日志测试" | "日志内容/格式/级别" | 1. 触发事件<br>2. 查询日志<br>3. 验证字段 | LOG |

#### 字段双向映射表（canonical 中文 ↔ legacy English 别名 · Round 12 新增）

> **本节是 SSOT** — S6 接受 legacy English 字段别名。下表列出 canonical（中文）与 legacy（v17/v3.01 历史产物）的双向映射关系；legacy 列出的字段名在 S6 L1 校验器中**等价于** canonical 字段，可互相镜像。

| Canonical（中文 · SSOT） | Legacy（英文别名） | 别名优先级（按列顺序） | 备注 |
|---|---|---|---|
| `前置条件` | `precondition` / `preconditions` | canonical > precondition > preconditions | 列表自动 `\n` join 成字符串 |
| `操作步骤` | `test_steps` / `steps` | canonical > test_steps > steps | 列表/dict 自动 join/dumps |
| `预期结果` | `expected_result` / `expected_results` / `expected` | canonical > expected_result > expected_results > expected | 列表/dict 自动 join/dumps |
| `优先级` | `priority` | canonical > priority | 必须是 `P0/P1/P2/P3` |
| `用例描述` | `title` / `scenario` | canonical > title > scenario | 仅用作 LLM 描述 |
| `功能描述` | `scenario` / `description` / `functional_description` | canonical > scenario > description > functional_description | LLM 自然语言 |
| `用例状态` | `case_status` / `status` | canonical > case_status > status | 必须是 `Draft/Ready/Rejected/Deprecated` |

**幂等性保证**：

- 已填 canonical 字段**绝不覆盖**（idempotency contract）—— legacy 仅作 fallback。
- 已填 legacy 字段值**自动镜像**到 canonical（`mirror_bilingual_aliases` 函数）。
- L1 校验器与 xlsx formatter 都先读 canonical，再回退 legacy——同源表现。

**case_id 命名空间（Round 12 修订）**：

- Canonical 格式：`{Module}-TC-{NNN}`（如 `UI-TC-007`）
- Legacy 格式：`TC-{NNN}`（如 `TC-007`）—— 由 `normalize_case_id` 自动按 `module` 注入前缀
- 已为 canonical 格式的 `case_id` **不重复处理**（idempotency）

#### v3.01 数据前置归一化（Round 12 新增 · 强调段）

> **本节是 v3.01 数据的硬性前置**——任何未先经 `case_id_and_field_normalizer.normalize_payload()` 归一化的 v3.01 数据，跑 L1S6Validator 时会**全部 FAIL**（331 cases × 4 fields = 1324 errors）。

**v3.01 数据合规步骤**：

1. **必须先调用** `case_id_and_field_normalizer.normalize_payload(cases)`：
   - `case_id` 加模块前缀（`TC-NNN` → `{Module}-TC-{NNN}`）
   - 4 个字段别名（preconditions / steps / expected_results / priority）→ 中文镜像
2. **再调** `L1S6Validator.run_l1_check()` 跑校验
3. **再调** `case_status_writer.apply_l1_l2_status()` 写回 `Ready` / `Draft`

**入口**：

```python
from ai_workflow.case_id_and_field_normalizer import normalize_payload, evaluate_status
from ai_workflow.case_status_writer import apply_l1_l2_status_per_case
from ai_workflow.test_case_formatter import _save_xlsx

cases = normalize_payload(payload)[0]                    # (1) 归一化
result = evaluate_status(cases, objs=objs, tps=tps)       # (2) L1 + L2 校验
_save_xlsx(cases, output_dir, output_path=xlsx_path)     # (3) xlsx 导出
```

**典型错误路径**（v3.01 直接喂 L1）：

```
L1S6Validator.validate_required_fields → 1324 errors (331 cases × 4 字段)
L1S6Validator.validate_id_naming → 331 errors (缺模块前缀)
→ 所有 TC 全部写回 Draft → 双 Sheet 附录 332 行 / 主表 0 行 ❌
```

**正确路径**（v3.01 先归一化）：

```
normalize_payload → 331 id_rewrites + 1324 alias_mirrors
L1S6Validator → 0 errors（全部合规）
L2S6Validator (lenient mode) → 0 failed_ids（v17 字段溯源版 SSOT 对齐）
→ 全部 331 TC 写回 Ready → 双 Sheet 主表 331 行 / 附录 0 行 ✅
```

#### 落地强制（永久）

| 规则 | 违规处理 |
|---|---|
| `test_point_type == EP_VALID` 时，TC `test_scenario` 必须含「有效值/合法值/正常值」 | TC 不合格 |
| `test_point_type == EP_INVALID` 时，TC `test_scenario` 必须含「无效值/非法值/异常值」 | TC 不合格 |
| `test_point_type == BOUNDARY_*` 时，TC `操作步骤` 必须含具体边界数值 | TC 不合格 |
| `test_point_type == OA_*` 时，TC `操作步骤` 必须含 factors / levels 字段 | TC 不合格 |
| `test_point_type` 与 `test_method` 命名不对应（如 EP_VALID 写成「边界值」） | TC 不合格 |

#### 引用 S5 test_point_type_defs 正反例（永久强制）

S6 生成 TC 时，**必须 Read** S5 test_points.json 中的 `test_point_type_defs`，参照其 `positive_example` 和 `negative_example`：
- `positive_example` → TC `操作步骤` 模板来源
- `negative_example.reason` → TC 禁忌规则（禁止这样写）

#### TC 示例（永久强制）

```json
{
  "case_id": "BIZ-TC-OB004-min-01",
  "module": "BIZ",
  "test_method": "边界值分析-最小有效",
  "test_scenario": "数量 min 边界点",
  "obj_id": "OBJ-004",
  "feature_point_id": "FP-004-01",
  "s5_ref": {
    "tp_id": "TP-017",
    "test_point_type": "BOUNDARY_MIN",
    "boundary_value": {"min": 1, "max": 99, "test_value": 1}
  },
  "操作步骤": [
    "1. 输入购买数量=1",
    "2. 点击购买按钮",
    "3. 观察系统响应"
  ],
  "预期结果": [
    "通过校验",
    "购买按钮可点击",
    "数量显示为 1"
  ],
  "priority": "P0"
}
```

#### 测试设计层级原则（Round 16 新增 · 永久强制）

> **SSOT**：本节是测试用例"一对多"展开的层级化设计原则——明确"1 OBJ → N FP / 1 FP → N 前置条件 / 1 前置条件 → N 步骤 → N TC"的多层级映射关系，避免 LLM 在生成 TC 时"按 TP 数量 1:1 出 TC"或"把所有步骤压成 1 条 TC"两个极端。

**核心原则（4 层级）**：

| 层级 | 关系 | 示例 |
|---|---|---|
| **L1 OBJ** | 1 个 OBJ 下可含 N 个 FP | `BIZ-PURCHASE-01-001-OBJ-01` 下有 FP-1（购买主流程）/ FP-2（退款分支）/ FP-3（库存校验） |
| **L2 FP** | 1 个 FP 下可含 N 个前置条件 | FP-1 购买主流程下：余额充足 / 余额不足 / 道具备注=0 / 数量=0 等前置条件 |
| **L3 前置条件** | 1 个前置条件可展开为 N 条步骤 | 余额充足下：选择道具→选择数量→点击购买→确认订单→支付→检查到账 |
| **L4 步骤组** | 1 套完整步骤序列 = 1 条独立 TC（除非按业务要求再拆）| 上述 6 步对应 1 条多步 TC；不再拆成 6 条单步 TC（除非 Round 15 例外条款） |

**关键决策规则**：

1. **OBJ → FP 展开**：每个 FP **至少 1 条 TC**；高风险 FP（P0 优先级）建议 3-5 条 TC（覆盖正常流 / 边界值 / 异常流）。
2. **FP → 前置条件展开**：每个独立前置条件 = **至少 1 条 TC**。禁止把"余额充足/余额不足/余额=0"3 个前置条件合并到 1 条 TC（会丢业务分支）。
3. **前置条件 → 步骤**：1 条 TC 含 **1~N 步连贯操作**（Round 15 例外条款允许合并同源步骤，禁止重新拆碎）。
4. **步骤 → TC**：1 套连贯步骤序列 = 1 条 TC。**禁止**"1 步 1 TC"的过细拆分（Round 15 §3 根因 B 已证伪）。

**反模式（违反任一 = 产出不合格）**：

| 反模式 | 后果 | 修复 |
|---|---|---|
| 1 OBJ 下所有 FP 共享 1 条 TC | 失去 FP 维度的覆盖完整性 | 按 FP 拆分，每个 FP 独立 TC |
| 1 FP 下不同前置条件合并成 1 条 TC | 丢失业务分支（如余额充足和不足不应在同一 TC） | 按前置条件拆分 |
| 1 前置条件下 1 步 = 1 TC（碎裂）| 像任务清单不像用例，下游难用 | **禁止**：新生成 TC 必须 ≥ 2 步。Round 15 例外仅限 v3.01 历史数据 |
| 1 TC 含完整业务的所有分支（如"正常流+异常流"）| 1 个 FAIL 污染整个 TC，定位困难 | 按分支拆分 |
| OBJ 缺失 obj_id | L1 字段溯源失败 | 必须填 S2 `requirement_object.id` |

**正反例对比**：

```
❌ 反模式（步骤碎裂 · Round 15 §3 根因 B）：
  TC-001: 玩家点击商城入口
  TC-002: 系统加载商城首页
  TC-003: 玩家选择道具
  TC-004: 系统显示道具详情
  TC-005: 玩家点击购买
  TC-006: 系统弹出支付确认

✅ 正确（Round 15 合并 + Round 16 层级原则）：
  TC-001: 进入商城 - 浏览道具（步骤 1-2 + 预期）
  TC-002: 选择道具 - 查看详情（步骤 1-4 + 预期）
  TC-003: 点击购买 - 弹出支付确认（步骤 1-3 + 预期）
  TC-004: 余额充足 - 完成购买（步骤 1-6 + 预期）
  TC-005: 余额不足 - 拒绝购买（步骤 1-3 + 预期）
```

**Round 16 强制条款**：

- 每个 TC 的 `obj_id` + `feature_point_ref` 必填（§S3→TC / S4→TC 字段溯源版）。
- 1 OBJ 下建议 N 条 TC，N ≥ FP 数（P0 FP 至少 1 条；高风险 FP 建议 3-5 条）。
- 1 FP 下不同前置条件必须独立 TC（禁止跨前置合并）。
- 1 前置条件展开 N 步连贯操作 = 1 TC（禁止按步骤拆碎）。
- xlsx 主表排序按 `obj_id` → `feature_point_ref` → `case_id` 升序（Round 16 §11 formatter 实现）。

### §其他模块 TC（CONFIG/LINK/LOG/SPECIAL）

沿用 OBJ+FP 引用（`obj_id` + `feature_point_id` 必填）。字段溯源版不重新设计。

#### §LOG 模块 TC seed 模板（Round 2 Act 新增 · qa_fixer_v301）

> **背景**：v3.01 LOG 模块仅 1 个 TP（邮件通知 LOG-TP-026）+ 1-2 TC——严重欠测（资深测试 Q-019 / 架构师 A-018 / 资深产品 P12 三方共识）。
> **本节是 SSOT**：补充 LOG 模块 30+ TC 的字段模板与 4 类日志场景标准。

**LOG TC 字段模板**（与 v3.01 schema 一致，遵循 §11 字段映射）：

```json
{
  "case_id": "LOG-TC-XXX",
  "module": "LOG",
  "case_type": "功能测试",
  "用例描述": "日志-登录日志",
  "test_scenario": "玩家登录成功时验证登录日志记录 device_id/ip/timestamp",
  "功能描述": "玩家登录成功时验证登录日志记录 device_id/ip/timestamp",
  "feature_point_ref": "BIZ-PURCHASE-01-001-OBJ-01-FP-4",
  "obj_id": "BIZ-PURCHASE-01-001-OBJ-01",
  "priority": "P1",
  "用例状态": "Ready",
  "备注": "qa_fixer_v301 Round 2 Act · LOG seed LOG_LOGIN_OK",
  "obj_name": "日志-登录日志",
  "fp_name": "日志记录-LOG_LOGIN_OK",  // Round 15 F-F：fp_name 已删除；新数据不生成此字段；v3.01 legacy 保留兼容
  "steps": [
    {"step_num": 1, "action": "触发场景：玩家登录..."},
    {"step_num": 2, "action": "查询日志系统"},
    {"step_num": 3, "action": "校验日志含 LOG_LOGIN_OK 事件及关键字段"}
  ],
  "preconditions": [
    "日志系统已部署",
    "日志采集 pipeline 正常",
    "LOG category = 登录日志"
  ],
  "expected_results": [
    "日志记录 event_code = LOG_LOGIN_OK",
    "日志含 timestamp + player_id + 关键字段",
    "日志级别 = INFO / WARN（按事件）"
  ],
  "test_methods": ["日志验证"]
}
```

> **F-D 字段修订（Round 14）**：
> - 本模板删除 `tc_id` 字段（历史冗余字段，新数据不再生成）
> - `case_id` 作为 S6 TC 唯一 ID（决策档 `s6_id_dedupe_decision.md` 推荐方案 A）
> - L1S6Validator 加"禁止 `tc_id` 字段"检查（默认 OFF，`--new-only` flag 启用——避免硬 FAIL 阻塞 v3.01 out_of_scope 数据）

**4 类 LOG 场景分布**（每类 ≥ 6 条 · 目标 ≥ 30 条）：

| 类别 | event_code 前缀 | 覆盖场景 |
|---|---|---|
| 登录日志 | `LOG_LOGIN_*` | 登录成功 / 失败 / 二次验证 / 异地 IP / brute force / 账号锁定 / token 刷新 / 退出登录 |
| 支付日志 | `LOG_PAY_*` | 订单创建 / 回调成功 / 回调失败 / 重复回调 / 超时关闭 / 退款 / 部分退款 / 渠道切换 |
| 操作日志 | `LOG_OP_*` | 购买 / 查看道具 / 加购 / 移出购物车 / VIP 变更 / 地址修改 / 密码修改 / 强制下线 |
| 异常日志 | `LOG_EXC_*` | DB 连接失败 / API 超时 / 限流 / 库存负数 / 重复订单 / OSS 失败 |

**字段约束**：
- `priority = P1`（日志验证是观测类，不阻塞主流程——除非是 P0 告警事件如 EXC 类）
- `用例状态 = Ready`（日志校验规则明确，无需 LLM 二次评审）
- `steps` 3 步：触发场景 → 查询日志 → 校验字段
- `expected_results` 至少 3 条：event_code / 关键字段 / 日志级别

**对应 fixer**：`ai_workflow.qa_fixer_v301.supplement_log_module`，目标 `log_target=30`。

#### §业务盲区 6 类 TC seed 模板（Round 2 Act 新增 · qa_fixer_v301）

> **背景**：资深产品审查识别 6 类核心业务盲区（账号安全 / 风控 / 性能 / 国际化 / 边界 / 业务规则），部分场景 v3.01 完全缺失。
> **本节是 SSOT**：补齐这 6 类 TC 的字段模板与最低数量要求。

| 类别 | 目标 TC 数 | module | 优先级 | 关键场景 |
|---|---|---|---|---|
| 账号安全 | ≥ 6 | SPECIAL | P0 | 密码强度 / 大额支付二次验证 / 异地登录告警 / 登录失败锁定 / 改密验证 / Token 失效 |
| 风控 | ≥ 4 | SPECIAL | P0 | 高频下单拦截 / 大额支付二次确认 / 退款欺诈 / 渠道切换逃单 |
| 性能 | ≥ 4 | BIZ | P0 | 1000 并发查询 / 100 并发创建订单 / 首屏 1s 加载 / 支付回调堆积不丢单 |
| 国际化 | ≥ 6 | UI/BIZ | P1 | 英文 / 繁体 / 日文 UI / 货币符号自动识别 / 小数点半角 / 跨时区活动 |
| 边界 | ≥ 8 | BIZ | P0-P1 | 库存 0 / 库存 1 / 库存上限 / 价格 0 / 余额 0 / VIP 0 / 退款 0 / 数量 0 |
| 业务规则 | ≥ 6 | BIZ | P0-P1 | 限购 1 / 限购 N / 限购跨账号 / 限购跨设备 / 限时过期 / 折扣叠加 |

**TC 字段模板**（与 §11 字段映射一致）：

```json
{
  "case_id": "{Module}-TC-XXX",
  "module": "{Module}",
  "case_type": "功能测试",
  "用例描述": "{obj_name}",
  "test_scenario": "{具体场景描述}",
  "功能描述": "{具体场景描述}",
  "feature_point_ref": "FIXER-{case_id}-FP-1",
  "obj_id": "FIXER-{case_id}-OBJ",
  "priority": "P0/P1（按类别）",
  "用例状态": "Ready",
  "备注": "qa_fixer_v301 Round 2 Act · {类别}",
  "obj_name": "{obj_name}",
  "fp_name": "{fp_name}",  // Round 15 F-F：fp_name 已删除；新数据不生成此字段；v3.01 legacy 保留兼容
  "steps": [
    {"step_num": 1, "action": "{前置动作}"},
    {"step_num": 2, "action": "{触发动作}"},
    {"step_num": 3, "action": "{验证动作}"}
  ],
  "preconditions": ["{前置条件1}", "{前置条件2}"],
  "expected_results": ["{可断言的具体响应}", "{UI 状态变化}", "{error_code}"]
}
```

**对应 fixer**：`ai_workflow.qa_fixer_v301.supplement_business_blindspots`，各类 targets 通过 kwargs 覆盖（默认 sec=6 / risk=4 / perf=4 / i18n=6 / boundary=8 / biz_rule=6）。

**优先级重排规则（qa_fixer_v301.reset_critical_priority）**：

| 关键词命中 | 目标优先级 | 适用场景 |
|---|---|---|
| `支付` / `退款` / `库存` / `登录` / `实名` | P0 | 关键路径（资深产品判定） |
| `已扣款` / `扣款未到账` / `支付超时`（含"网络"） | P0 | 资损风险（资深产品 P4） |
| `页面加载` / `首屏` / `道具列表展示` | 保持原值 | UI 烟测不强制改 |

**约束**：
- 补 TC 全部 `用例状态 = Ready`（fixer 已 L1+L2 校验）
- `备注` 字段统一标记 `qa_fixer_v301 Round 2 Act · {类别}`——便于 review_*.md 追溯
- `feature_point_ref` / `obj_id` 用 `FIXER-*` 占位（避免与 S2 OBJ 命名冲突）
- 后续 S7 审查可识别这些 TC 并标记为 `Round 2 Act 补 TC`

### 兼容性说明

- `s5_ref` 字段保留（不强制新数据填，但旧数据兼容）
- `obj_id` + `feature_point_id` 对 CONFIG/LINK/LOG/SPECIAL 仍强制
- 历史产出的 TC 暂不重生成（按需重新评估）

### §S5 → S6 链路强制条款

> **SSOT**：本节是 §FP 全覆盖门禁的 S6 落地条款。配合 `.cursor/skills/aidocx-s5-test-points/SKILL.md` §TP 必须引用 feature_point 使用。

#### 链路契约（必填字段）

| 字段 | 上游来源 | 校验规则 |
|---|---|---|
| `s5_ref` / `tp_references[]`（v28 放宽） | S5 `scenario_test_points[].tp_id` | **必填**（`s5_ref` 单值 或 `tp_references[]` 数组均合法）。① `s5_ref` 单值形态：必存在于 S5 TP 列表；② `tp_references[]` 数组形态（v28 放宽）：数组长度 ≥ 1，每项均必存在于 S5 TP 列表。**优先使用 `s5_ref` 单值**（SSOT），`tp_references[]` 仅在多 TP 合并 TC 时使用。 |
| `obj_id` | S2 `requirement_object.id` | 必填 |
| `feature_point_id` | 由 `s5_ref.feature_point_ref` 推导 | 与 `s5_ref` 一致（推导冗余校验） |

#### 双层覆盖率门禁

- `obj_linkage_coverage = len(TC 引用的 OBJ 集合) / len(S2 OBJ 列表)` ≥ **1.0**
- `fp_linkage_coverage = len(TC 引用的 FP 集合) / len(S2 feature_points 总数)` ≥ **1.0**

#### 冗余校验：TC.obj_id == s5_ref 推导的 OBJ.id

每个 TC 必须保证 `obj_id` 字段与 `s5_ref → tp.feature_point_ref → obj.id` 推导一致。否则触发 `obj_mismatch_via_s5_ref` 错误。

#### LLM 自检 3 步走（生成 TC 前）

1. **列 S5 TP**：从 S5 `test_points.json` 列出**全部 TP** 的 `tp_id` + `feature_point_ref`
2. **设计 TC 1:N 拓宽**：每个 TP 至少 1 个 TC（1:1）或 N 个（methodology 拓宽）
3. **覆盖率自检**：
   - `TC 引用的 TP 集合 ⊆ S5 TP 集合`
   - `TC 引用的 FP 集合 == S2 FP 集合`

#### 与 OBJ 链接条款的关系

- 保证 `obj_id` 必填 + `用例描述 == obj_name`
- 叠加 `s5_ref` 必填 + FP 全覆盖 + TC.obj_id == s5_ref 推导的 OBJ.id
- **字段溯源版检查都通过才算 S6 合格**

### 字段溯源提示

> **v31 字段溯源修订**：`用例描述` 来源从 `S2 OBJ.obj_name` 改为 `S2 backlog.epics[].title`；`功能描述` 来源从 LLM 自由创作改为 `S2 backlog.stories[].title`。

**字段溯源规则（必须遵守）**：

| S6 TC 字段 | S2 溯源路径 | 说明 |
|------------|------------|------|
| `用例描述` | `backlog.epics[].title` | Epic 标题 = 需求对象名称 |
| `功能描述` | `backlog.stories[].title` | Story 标题 = 功能描述 |
| `obj_id` | `backlog.epics[].requirement_objects[].id` | Epic 关联的 OBJ ID |
| `obj_name` | `backlog.epics[].requirement_objects[].name` | Epic 关联的 OBJ 名称（与用例描述对应） |
| `feature_point_ref` | `backlog.stories[].feature_points[].id` | Story 关联的 FP ID |

**溯源验证要求**：

- `用例描述` 必须与 `backlog.epics[].title` 严格相等
- `功能描述` 必须与 `backlog.stories[].title` 严格相等
- `obj_id` 必须在 backlog 的 requirement_objects 列表中存在
- 禁止用 `requirement_objects.json` 的 OBJ 替代 `backlog.json` 的 Epic/Story 溯源

**正确 vs 错误对比**：

```text
✅ 用例描述: 商城首页          （backlog Epic.title = "商城首页"）
✅ 功能描述: 商城首页展示       （backlog Story.title = "商城首页展示"，动词"展示"）
✅ 操作步骤: 1. 玩家余额=1000游戏币，道具单价=500
            2. 尝试购买数量=3（总价=1500）
            3. 系统检测余额不足
✅ 预期结果: 1. 购买确认弹窗显示余额不足提示
            2. 【购买】按钮禁用（灰色不可点击）

✅ 用例描述: 商城道具配置       （Epic = "商城道具配置"）
✅ 功能描述: 道具从配置加载      （动词"加载"，描述系统行为）

❌ 用例描述: 道具列表项         （错误：用了 OBJ.obj_name，应为 Epic.title）
❌ 功能描述: 道具数据配置        （错误：名词"配置"是配置动作本身，应为"道具从配置加载"）
❌ 功能描述: 价格配置           （错误：名词"配置"，应为"道具按配置价格展示"）
❌ 操作步骤: 执行操作：验证结果 / 执行测试场景 / 验证预期结果 （模板语言）
❌ 预期结果: 余额不足提示（引用S4-1.3异常树）      （括号引用）
❌ 前置条件: 无                                     （占位文本，业务有实际前置条件时禁止）
```

---

## 用例格式（10列）

> **重要（与 `ai_workflow/test_case_formatter.py` 严格一致）**：
> - **用例ID 前缀**采用 8 模块英文全名（按 `MODULES.md` §1 总表顺序）：`CONFIG-TC-NNN` / `UI-TC-NNN` / `BIZ-TC-NNN` / `UTIL-TC-NNN` / `LINK-TC-NNN` / `LOG-TC-NNN` / `SPECIAL-TC-NNN` / `HINT-TC-NNN`（**禁止**用旧 4 字母缩写 `CFG/LNK/SPC/HNT`）
> - **模块字段**支持中英双语并存：`UI` 或 `界面` 任一；S6 阶段统一由 `test_case_formatter.py` 的 `normalize_module_name()` 归一化为 8 模块全名
> **旧枚举**（`RED_DOT` / `SYS_MSG` 等）由 `format_test_cases()` 自动迁移到现行枚举
> - 中英并存规则见 [`.cursor/MODULES.md` §3 中英映射表](../../../MODULES.md)

```json
[
  {
    "case_id": "UI-TC-001",
    "模块": "界面",
    "用例描述": "购买确认流程",
    "功能描述": "购买确认弹窗正常展示道具信息",
    "前置条件": "玩家已登录，余额充足，道具可购买",
    "steps": [
      {"step_num": 1, "action": "玩家已登录，进入道具详情页"}
    ],
    "expected_results": [
      "弹窗展示道具名称"
    ],
    "优先级": "P0",
    "用例状态": "Draft",
    "备注": ""
  },
  {
    "case_id": "UI-TC-002",
    "模块": "界面",
    "用例描述": "购买确认流程",
    "功能描述": "购买确认弹窗正常展示道具信息",
    "前置条件": "玩家已登录，余额充足，道具可购买",
    "steps": [
      {"step_num": 1, "action": "玩家已登录，进入道具详情页"}
    ],
    "expected_results": [
      "弹窗展示购买数量"
    ],
    "优先级": "P0",
    "用例状态": "Draft",
    "备注": ""
  },
  {
    "case_id": "UI-TC-003",
    "模块": "界面",
    "用例描述": "购买确认流程",
    "功能描述": "购买确认弹窗正常展示道具信息",
    "前置条件": "玩家已登录，余额充足，道具可购买",
    "steps": [
      {"step_num": 1, "action": "玩家已登录，进入道具详情页"}
    ],
    "expected_results": [
      "弹窗展示总价"
    ],
    "优先级": "P0",
    "用例状态": "Draft",
    "备注": ""
  },
  {
    "case_id": "UI-TC-004",
    "模块": "界面",
    "用例描述": "购买确认流程",
    "功能描述": "购买确认弹窗正常展示道具信息",
    "前置条件": "玩家已登录，余额充足，道具可购买",
    "steps": [
      {"step_num": 1, "action": "玩家已登录，进入道具详情页"}
    ],
    "expected_results": [
      "弹窗展示当前余额充足提示"
    ],
    "优先级": "P0",
    "用例状态": "Draft",
    "备注": ""
  }
]
```

### 步骤写作规则

- 每步必须包含具体 UI 元素名称（按钮名、输入框名、菜单名）或具体数值（价格、数量、时间戳）
- **禁止任何模板语言**：「执行操作：」「执行：」「准备符合前置条件的测试环境」「执行测试输入中的操作」全部禁止
- 每步独立可验证（能判断该步通过/失败）
- 最大 8 步，超过则拆分为多个用例
- 涉及配置的用例，必须包含具体的配置字段名和配置值

### 优先级判断

| 优先级 | 适用场景 |
|--------|---------|
| P0 | 支付、购买、VIP折扣、促销、安全、日志 |
| P1 | 普通业务逻辑、订单、邮件、权限 |
| P2 | 界面展示、搜索、分页、加载 |

> 优先级**由 LLM 根据业务风险自由决定**，脚本不强制套用任何映射表。


### P0/P1/P2 覆盖率分级门禁

> **来源**：外部方案 §4.5.1 + SSOT §4.3

S6 生成的 TC 必须满足优先级覆盖率分级：

| 优先级 | 覆盖率要求 | 刚性 |
|--------|-----------|------|
| **P0** | ≥ 95% | 刚性，不可例外 |
| **P1** | ≥ 80% | 柔性，可申请 bypass |
| **P2** | ≥ 50% | 指导值，不做强求 |

> 覆盖率 = 该优先级 Story 的 TC 数 / 该优先级 Story 的 FP 总数
---

## 自检清单（LLM 生成后、提交前必走）

**评审驱动**：按产物分阶段自检——**前一阶段不通过，禁止进入下一阶段**。

### json 评审门禁（5 项，写完 test_cases.json 后立即执行）

- [ ] **ID 唯一性 100%**：`{Module}-TC-{NNN}` 无重复
- [ ] **12 字段完整 100%**：case_id/module/用例描述/功能描述/前置条件/**steps**/expected_results/优先级/用例状态/备注/obj_id/feature_point_id
- [ ] **前置条件不为准"无"**：必须包含具体初始状态（余额/道具数量/玩家等级等），"无" 仅在业务确实无前置条件时使用
- [ ] **steps ≥2 步原则（v33 C1）**：每条 TC 的 `steps` 数组**至少含 2 个元素**（`{step_num:N, action:...}`），禁止 1 步 1 TC。**Round 15 例外适用范围**：仅限 v3.01 历史数据，**不适用于新生成的 TC**。
- [ ] **expected_results 单预期原则**：每条 TC 的 `expected_results` 数组只含 1 项，禁止多条预期并置。**Round 15 例外**：同上（仅 v3.01 历史数据）。
- [ ] **5 项业务自检**：用例描述为需求对象名称 / 功能描述为需求对象功能点自然语言 / steps 单步 / expected_results 单预期 / 全文搜索"引用"为 0 处
- [ ] **优先级分布合理**：**P0 覆盖率 ≥ 95%（刚性）/ P1 ≥ 80%（柔性）/ P2 ≥ 50%（指导值，不做强求）**
- [ ] **8 模块覆盖**：CONFIG/UI/BIZ/UTIL/LINK/LOG/SPECIAL/HINT 至少 1 个用例
- [ ] **OBJ 链接覆盖率 100%**：每个 TC 有 `obj_id`；`obj_id` 在 S2 OBJ 列表中；`用例描述 == obj_name`（字符串严格相等）；未引用 OBJ 进入 omission ledger + skip_reason
- [ ] **字段溯源检查**：TC.obj_name == TP.obj_name（100% 继承）；TC.feature_point_ref == TP.feature_point_ref（100% 继承，结构化 FP ID）；TC.fp_name 已 Round 15 F-F 删除（新数据不再生成）；未通过 → S6 不合格
- [ ] **assertion 字段完整性**（Round 15 F-E）：每条 TC.assertion 数组 ≥ 1 项，每项含 `assertion_type` 必填子字段；未通过 → S6 不合格
- [ ] **🚨 不通过禁止生成 xlsx**——回 LLM 迭代 json

### md 评审门禁（写完 test_cases.md 后立即执行）

- [ ] md 中 TC 简表与 json 一致（数量/用例ID/优先级）
- [ ] md 总览统计数字与 json 一致（模块分布/优先级分布）
- [ ] md 分组（Epic）正确——按 S2 backlog 4 Epic 分

### 公共 xlsx 评审门禁（每次执行时）

- [ ] xlsx 可被 openpyxl 重新打开（round-trip 校验）
- [ ] 表头 / Sheet / 列顺序符合公共默认格式（`_XLSX_HEADERS_V3`）

### 项目级 xlsx 评审门禁（仅在已确认项目且存在项目级配置时执行）

- [ ] 已确认当前产出目标项目
- [ ] 已存在 `knowledge/project_local/<project_name>/s6/export_profiles/test_cases.export.json`
- [ ] xlsx 可被 openpyxl 重新打开（round-trip 校验）
- [ ] 表头 / Sheet / 列顺序符合项目级导出配置

> **用例状态**：`Draft / Ready / Rejected / Deprecated`（4 值）。`Ready` 由 `case_status_writer.apply_l1_status()` 根据 `L1S6Validator.run_l1_check().passed` 写回，`Rejected` 由 `s7_status_writer.apply_s7_rejection_status()` 在 S7 产生 `recommendations.must_fix[].severity == MUST_FIX` 时触发，禁止在 S6 脚本内硬编码 `Draft` 或依赖已废除的 S7 字段。

### 公共 xlsx 单会话入口（Round 22 锁定）

`ai_workflow/test_case_formatter.py` 暴露 `--tc-json-to-xlsx` 子命令，强制走 `_DEFAULT_XLSX_PROFILE` 与 `_XLSX_HEADERS_V3`，不受项目级 profile 覆盖。

```bash
python3 ai_workflow/test_case_formatter.py --tc-json-to-xlsx <tc.json> \
    [--xlsx-output <output.xlsx>]
```

- 主 Sheet（按 profile `sheet_name`，公共为 `测试用例`）：仅 `Ready`。
- 附录 Sheet（固定 `Draft-Rejected附录`）：`Draft` + `Rejected`。
- `Deprecated` 不进入执行 Sheet，仍留在 JSON 真相源。
- 支持 3 种 tc.json 结构：顶层 list / `{test_cases:[...]}` / `{meta:...,test_cases:[...]}`。

| 检查项 | 要求 | 缺失时 |
|--------|------|--------|
| `test_cases.json` 生成 | 公共默认必须 | fail_report_S6.md |
| `test_cases.xlsx` 生成 | 公共默认必须 | fail_report_S6.md |
| `test_cases.md` | 仅项目级配置存在时要求 | fail_report_S6.md |
| 项目级 xlsx 可被 openpyxl 重新打开 | 项目级导出时 100% | fail_report_S6.md |

**生成命令**：
```python
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from collections import Counter

with open("test_cases.json") as f:
    cases = json.load(f)

wb = Workbook()
wb.remove(wb.active)

# 公共默认 xlsx：固定路径 test_cases.xlsx，使用公共默认表头/Sheet/列顺序
# 项目级 xlsx（如已确认项目）：路径为「<project_name>/test-case_<project_name>.xlsx」，使用项目级模板
# 未确认项目时，不生成项目级 xlsx
```

---

## S4 参考规则

S4 流程图是 S6 **理解业务**的重要来源，但引用规则如下：

- **可以参考**：阅读 S4 理解业务流程、异常路径、风险场景，据此设计用例步骤和预期结果
- **禁止照抄**：不得将 S4 的节点名称、异常树编号、风险点名直接写入任何字段
- **如需注明**：仅在「备注」字段中写 `[参考S4-章节]`（非强制）

---

## 成功产出

路径：`workflow_assets/<req_name>/<version>/「S6 测试用例生成」/`
1. **JSON**：`test_cases.json`（公共默认强制产物）
2. **Markdown**：`test_cases.md`（仅在已确认项目且存在项目级导出配置时生成）
3. **Excel**：`test_cases.xlsx`（公共默认强制产物）

---

## 失败报告

路径：`workflow_assets/<req_name>/<version>/「S6 测试用例生成」/fail_report_S6.md`

---

## 自动化支持（thin wrapper）

```python
# 脚本只做整理：ID 分配 / 字段归一化 / 写文件
from ai_workflow.s6_generate import collect_cases
from ai_workflow.test_case_formatter import _assign_ids, _build_summary, _save_md, _save_xlsx

# LLM 在对话中生成的 case 列表 → 写入 test_points.json 的 llm_generated_cases 字段
# 脚本读取后只做：
# 1. 分配 case_id（按模块分组递增）
# 2. 模块字段归一化（中英 → 8 模块全名）
# 3. 写 JSON / Markdown / XLSX

# 兜底：若无 llm_generated_cases，从 scenario_test_points 1:1 转种子 case
# （保留 LLM 后续在对话中改写步骤/预期的入口）
```

> **重要**：脚本不推导 TC 数量、不分配 test_method、不做模块加权——这些全是 LLM 推理工作。

---

## §12 TC 内部结构化映射规范（v2.0 · 强制执行）

> **🔴 强制执行**：本节是 S6 TC 生成的**强制规范**，违反任一条款 → 该 TC 不合格。
> **来源**: `governance/design_iter/current/TC_STRUCTURAL_MAPPING_SPEC.md`

### 12.1 问题定义

**当前问题（1 步 1 TC 反模式）**：
```json
TC-001: {"steps": [{"step_num": 1, "action": "玩家点击商城入口"}]}
TC-002: {"steps": [{"step_num": 2, "action": "系统加载商城首页"}]}
TC-003: {"steps": [{"step_num": 3, "action": "观察道具列表..."}]}
```

**期望模式（四层映射）**：
```
1 用例描述 = N 功能描述
1 功能描述 = N 前置条件
1 前置条件 = N 操作步骤
1 预期结果 = N 操作步骤（步骤-预期对应）
```

### 12.2 TP → TC 链路

**TP = 测试意图**，**TC = 测试步骤**，**1 TP → N TC**：

```
S5 TP
  ├── preconditions: [玩家已登录, 商城有数据]
  ├── tc_generation_hints:
  │     ├── scenario_variants[0]: {预期: [展示10个, 降序]}
  │     └── scenario_variants[1]: {预期: [空状态插画]}
  │
  ▼ S6 LLM 推理

S6 TC 1 (场景A)
  ├── 前置条件: 继承 TP.preconditions
  ├── 操作步骤: [点击入口 → 加载首页 → 观察]
  └── 预期结果: [展示10个, 降序]

S6 TC 2 (场景B)
  ├── 前置条件: TP.preconditions + variant.additional
  ├── 操作步骤: [点击入口 → 加载首页 → 观察]
  └── 预期结果: [空状态插画]
```

### 12.3 四层映射模型

> **v31 修订**：L1/L2 来源从 requirement_objects.json 改为 backlog.json。

| 层级 | 来源 | 说明 | 强制度 |
|------|------|------|--------|
| **L1 用例描述** | S2 backlog.epics[].title | Epic 标题 = 需求对象 | MUST |
| **L2 功能描述** | S2 backlog.stories[].title | Story 标题 = 功能描述 | MUST |
| **L3 前置条件** | S5 TP.preconditions + variant | 测试初始状态 | MUST |
| **L4 步骤预期** | S6 LLM 推理操作 + TP.expected_results | 操作步骤 + 预期结果 | MUST |

### 12.4 TC Schema（强制）

每条 TC 必须包含：

```json
{
  "case_id": "UI-TC-001",
  "module": "UI",
  "用例描述": "商城首页道具列表",
  "功能描述": "首页销量排序展示",
  "前置条件": "玩家已登录游戏客户端，商城已配置道具数据",

  "操作步骤": [
    {"step_num": 1, "action": "玩家点击商城入口"},
    {"step_num": 2, "action": "系统加载商城首页"},
    {"step_num": 3, "action": "观察道具列表排序"}
  ],

  "预期结果": [
    {"step_ref": 1, "预期": "商城首页正常打开"},
    {"step_ref": 2, "预期": "道具列表展示前10个道具，销量从高到低降序排列"},
    {"step_ref": 3, "预期": "每个道具显示完整名称和价格"}
  ],

  "obj_id": "UI-ITEM-MALL-01-001-OBJ-01",
  "feature_point_ref": "UI-ITEM-MALL-01-001-OBJ-01-FP-1",
  "s5_ref": "UI-TP-001",
  "priority": "P1",
  "用例状态": "Ready"
}
```

### 12.5 字段继承规则

| S6 TC 字段 | S5 TP 来源 | 规则 |
|-------------|-------------|------|
| `用例描述` | `用例描述` | 直接继承 |
| `功能描述` | `功能描述` | 直接继承 |
| `前置条件` | `preconditions` + variant.additional | 合并 |
| `预期结果` | `tc_generation_hints.variant.expected_results` | 直接引用 |
| `操作步骤` | **LLM 推理** | 根据前置条件和预期生成 |
| `obj_id` | `obj_id` | 直接继承 |
| `feature_point_ref` | `feature_point_ref` | 直接继承 |
| `s5_ref` | `tp_id` | 引用 |

### 12.6 禁止模式（违反 = TC 不合格）

| 禁止 | 错误示例 | 正确做法 |
|------|---------|---------|
| **1 步 1 TC** | TC-001: 玩家点击商城入口 | 合并为 1 条 TC，含连贯步骤序列 |
| 步骤碎裂 | TC-001~TC-005 每条 1 步 | 1 TC 含连贯步骤序列 |
| **预期缺失 step_ref** | expected_results: ["验证通过"] | 每条预期必须有 step_ref |
| 前置条件为空 | "前置条件": "" | 继承 TP.preconditions |
| 预期结果为空 | "预期结果": [] | 至少 1 个预期 |

> **步骤数要求**：按业务风险灵活调整（典型 2-3 步），禁止"1 步 1 TC"碎裂模式，无硬性阈值。

### 12.7 LLM 自检要求（强制）

生成完所有 TC 后，必须逐条检查：

| 检查项 | 通过标准 | 失败动作 |
|--------|---------|---------|
| 步骤连贯性 | 无 1 步 1 TC 碎裂 | 回 LLM 合并步骤 |
| 预期数 ≥ 1 | `len(expected) >= 1` | 回 LLM 补充预期 |
| 预期含 step_ref | `e.get("step_ref")` | 回 LLM 添加 step_ref |
| 前置条件非空 | `precondition != ""` | 继承 TP.preconditions |

### 12.8 Excel 渲染规则

#### 步骤列渲染

```python
def render_steps(steps):
    """输出格式：每步一行，格式为 "{step_num}. {action}" """
    return "\n".join(f"{s['step_num']}. {s['action']}" for s in steps)
```

#### 预期列渲染

```python
def render_expected(expected):
    """输出格式：按 step_ref 对应 "[步骤{step_ref}] {预期}" """
    return "\n".join(f"[步骤{e['step_ref']}] {e['预期']}" for e in expected)
```

### 12.9 自检清单（提交前必走）

- [ ] 无步骤碎裂（同一 TC 内 steps 数组连续，无 1 步 1 TC 模式）
- [ ] 预期结果数 ≥ 1
- [ ] 每条预期含显式 step_ref
- [ ] 前置条件非空
- [ ] 步骤与预期 step_ref 对应

> **步骤数要求**：按业务风险灵活调整（典型 2-3 步），无硬性阈值。

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S6_TEST_CASES.mdc`
- 用例库：`knowledge/public/test_case_library/`
- 示例参考：`knowledge/public/example_test_cases/`
- TC 结构化映射规范：`governance/design_iter/plans/v28/TC_STRUCTURAL_MAPPING_SPEC.md`
- S5 前置条件规范：`.cursor/skills/aidocx-s5-test-points/SKILL.md §七`

---

## 执行卡（单阶段执行卡 — 4 区块合一）

<aside data-exec-card-block="input_gate" data-src=".cursor/rules/STAGE_S6_TEST_CASES.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

> ⚠️ **派生产物，禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成
> src: `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | synced_at: `2026-07-14`
> 修改请改源文件，然后跑 `python3 scripts/sync_execution_cards.py --stage s6-test-cases` 重新同步。

### 输入门禁（input_gate）

| 必备材料 | 路径 | 缺失处理 |
|---|---|---|
| S5 test_points.json（必须） | `workflow_assets/<req_name>/<version>/「S5 测试点生成」/test_points.json` | 生成 fail_report_S6.md，停止 |
| S2 backlog.md（必须） | `workflow_assets/<req_name>/<version>/「S2 需求拆解」/backlog.md` | 作为优先级参考 |
| S4 business_flow.md（必须） | `workflow_assets/<req_name>/<version>/「S4 流程图导出」/business_flow.md` | 异常决策树来源 |
| 模块子模板（必须） | `knowledge/public/module_templates/<MODULE>.md` | 按 TP module 读取对应子模板 |

**触发命令**：`/aidocx-s6-test-cases` 或粘贴 S5 test_points.json

</aside>

---

## §S6 覆盖率分级门禁

> **派生产物**：本节基于外部方案 §4.5.1 + SSOT §4.3，于 2026-07-16 落地。
> **职责**：脚本级校验 P0/P1/P2 优先级覆盖率门禁，不依赖 LLM 主观判断。

### 调用方式

```bash
python3 ai_workflow/s6_coverage_gate.py <test_cases.json> [backlog.json] [--json]
python3 ai_workflow/s6_coverage_gate.py --self-test
```

### 退出码语义

| 退出码 | 含义 | 动作 |
|--------|------|------|
| `0` | PASS（P0 全过 / 仅 P2 警告） | 可进入 S7 |
| `1` | BLOCKED（P0 < 95% / 必要 P1 < 80%） | 必须修复或走 bypass |
| `2` | 参数错误 | 重跑 |

### 阈值常量（SSOT §4.3）

| 优先级 | 阈值 | 刚性 |
|--------|------|------|
| **P0** | ≥ 95% | 刚性（不可 bypass） |
| **P1** | ≥ 80% | 柔性（可走 bypass → `bypass_log.json`） |
| **P2** | ≥ 50% | 指导值（不强制） |

### 与 S7 正式审查的边界

- ✅ 本脚本算 P0/P1/P2 优先级覆盖率（机械）
- ❌ 不算：模块覆盖率 / OBJ 覆盖率 / FP 覆盖率（这些归其他门禁）
- ✅ S7 审查员 B 消费本脚本输出 + bypass_log.json 做整体审查

### 自我测试

`python3 ai_workflow/s6_coverage_gate.py --self-test` — 3 cases 全覆盖。

<aside data-exec-card-block="naming" data-src=".cursor/rules/STAGE_S6_TEST_CASES.mdc" data-sha256="INIT_seed" data-synced-at="2026-07-14">

### ID 命名规范（naming）

| 层级 | 格式 | 示例 |
|---|---|---|
| 用例 | `{Module}-TC-{NNN}` | `UI-TC-001`, `BIZ-TC-047` |
| 引用 S5 | `s5_ref` | `TP-001` |
| 引用 FP | `feature_point_id` | `01-01-OBJ-01-FP-1` |
| 输出文件 | `test_cases.json`（公共默认强制）+ `test_cases.xlsx`（公共默认强制）+ `test_cases.md`（项目级可选） | |

</aside>






> **派生产物**：本节基于外部方案 §4.5.1 + SSOT §4.3，于 2026-07-16 落地。
> **职责**：脚本级校验 P0/P1/P2 优先级覆盖率门禁，不依赖 LLM 主观判断。

### 调用方式

```bash
python3 ai_workflow/s6_coverage_gate.py <test_cases.json> [backlog.json] [--json]
python3 ai_workflow/s6_coverage_gate.py --self-test
```

### 退出码语义

| 退出码 | 含义 | 动作 |
|--------|------|------|
| `0` | PASS（P0 全过 / 仅 P2 警告） | 可进入 S7 |
| `1` | BLOCKED（P0 < 95% / 必要 P1 < 80%） | 必须修复或走 bypass |
| `2` | 参数错误 | 重跑 |

### 阈值常量（SSOT §4.3）

| 优先级 | 阈值 | 刚性 |
|--------|------|------|
| **P0** | ≥ 95% | 刚性（不可 bypass） |
| **P1** | ≥ 80% | 柔性（可走 bypass → `bypass_log.json`） |
| **P2** | ≥ 50% | 指导值（不强制） |

### 与 S7 正式审查的边界

- ✅ 本脚本算 P0/P1/P2 优先级覆盖率（机械）
- ❌ 不算：模块覆盖率 / OBJ 覆盖率 / FP 覆盖率（这些归其他门禁）
- ✅ S7 审查员 B 消费本脚本输出 + bypass_log.json 做整体审查

### 自我测试

`python3 ai_workflow/s6_coverage_gate.py --self-test` — 3 cases 全覆盖。

---

## §新增 S6 模块编排模式（v35 新增）

> **触发条件**：当执行 `/aidocx-s6-test-cases` 且 `project_name` 参数存在（或显式指定"模块编排模式"）时，启用本模式。
> **不改变默认行为**：单 agent 直接生成 TC 的方式仍然保留，本节是**额外编排路径**。

### §1 模式切换

| 模式 | 触发 | 主 agent 角色 |
|------|------|--------------|
| **默认模式**（直接生成） | 无 `project_name` | 直接生成 TC 写入 test_cases.json |
| **模块编排模式**（v35 新增）| 有 `project_name` | orchestrator：调度 8 expert + merge-expert |

### §2 流水线

主 agent（orchestrator，不自己写 TC）
  ↓ orchestrator prompt（由 conversation_skills 生成）
  ├─ Task(/ui-expert)   → _module_expert_drafts/UI_module_tc.json
  ├─ Task(/biz-expert)  → _module_expert_drafts/BIZ_module_tc.json
  ├─ Task(/config-expert) → _module_expert_drafts/CONFIG_module_tc.json
  ├─ Task(/util-expert)  → _module_expert_drafts/UTIL_module_tc.json
  ├─ Task(/link-expert) → _module_expert_drafts/LINK_module_tc.json
  ├─ Task(/log-expert)  → _module_expert_drafts/LOG_module_tc.json
  ├─ Task(/special-expert) → _module_expert_drafts/SPECIAL_module_tc.json
  └─ Task(/hint-expert) → _module_expert_drafts/HINT_module_tc.json
  ↓（全部完成）
  /merge-expert → test_cases.json
  ↓
主 agent 调用 format_test_cases()（强制公共级 xlsx）

### §3 草稿格式

每个 expert 写入 `<stage_dir>/_module_expert_drafts/<MODULE>_module_tc.json`：

```json
{
  "meta": {
    "module": "UI",
    "expert": "ui-expert",
    "req_name": "游戏道具商城系统",
    "version": "v3.01",
    "created_at": "2026-07-22T09:30:00+08:00",
    "tp_source": "S5 test_points.json"
  },
  "test_cases": [...]
}
```

### §4 与默认模式的差异

| 方面 | 默认模式 | 模块编排模式 |
|------|----------|--------------|
| 主 agent 产出 | 自己写 TC | 只做编排，不写 TC |
| 并行性 | 无 | 8 expert 并行（≤5 批）|
| 合并 | 无 | merge-expert 串行收尾 |
| 上下文长度 | 所有 TC 在上下文中 | 上下文只含 orchestrator prompt |
| 知识复用 | 无 | 各 expert 复用自己模块知识库 |
| 覆盖率保证 | 依赖主 agent 能力 | 各 expert 专注自己模块，覆盖更全 |

### §5 v35 xlsx 强制产出约束

S6 模块编排模式的最终产物必须包含：

| 产出 | 路径 | 强制？ |
|------|------|--------|
| `test_cases.json` | 同上目录 | ✅ 强制 |
| `test_cases.xlsx`（公共级） | 同上目录 | ✅ **强制**（v35 新增） |
| `merge_report.json` | 同上目录 | ✅ 强制 |
