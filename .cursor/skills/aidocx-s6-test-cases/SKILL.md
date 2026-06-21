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

# AIDocxWorkFlow S6 — 测试用例生成

> **设计哲学（2026-06-15）**：
> - **LLM 负责推理**：从 S5 TP 派生出几个 TC、用什么方法、步骤怎么写——全是 LLM 推理决定
> - **脚本只负责整理**：ID 分配 / 字段归一化 / 写文件
> - **不设硬指标**：1:1 也行、1:5 也行、1:20 也行——业务复杂度自然决定
> - **真实需求多种多样**，硬指标脚本只服务一种结构；**LLM 推理 + 脚本整理**能适配任意结构

**独立阶段**：可单独调用。上游材料（S5 test_points.json）审查合格后开始，失败写失败报告。

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
| ③ | S5 test_points（强制） | `workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json` | 每个 TP 的 module / test_type 是 TC 拓宽的输入；未读取 → 无法拓宽 |
| ④ | S4 business_flow（强制） | `workflow_assets/<req_name>/「S4 流程图导出」/<version>/business_flow.md` | 异常决策树和风险点是 EXCEPTION TC 的核心来源 |
| ⑤ | 命中模块子模板 | `workflow_assets/module_templates/<Module>/<Module>.md` | 子类枚举决定 TC 方法选择 |

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
| `test_cases.xlsx` | 运行 `_save_xlsx` 后检查 10 列全部非空 | 重生成 xlsx（不修改 json）|

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
- **Q1/Q2 回答"不存在"且 Q3 回答"不影响"** → 允许放行，备案到 `bypass_log.json`（路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/bypass_log.json`）

### 脚本入口（必须在 LLM 生成产物后立即执行）

```python
from ai_workflow.auto_reviewer import snapshot
from pathlib import Path

tc_path = Path("workflow_assets/<req_name>/「S6 测试用例生成」/<version>/test_cases.json")
bd_path = Path("workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.json")
tp_path = Path("workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json")

snap = snapshot(tc_path, bd_path, tp_path)

# 读取事实数字（禁止跳过此步骤直接写报告）
print(snap.ai_input_summary)
print(f"[S6 GATE] TC 填写率: {snap.structure.fill_rate:.1%}")
if snap.structure.fill_rate < 0.9:
    print(f"[S6 GATE] 填写率 {snap.structure.fill_rate:.1%} < 90%")
    print("[S6 GATE] 触发三步自问（见 §1.6 例外条款）")
    # → 进入三步自问决策树，LLM 判断是否可放行
```

### 禁止行为

- ❌ 跳过 `snapshot()` 直接输出产物
- ❌ 跳过门禁检查直接生成 xlsx
- ❌ 在未经三步自问的情况下直接放行
- ❌ 三步自问 Q1/Q2 回答"存在"或"有"时仍放行

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

## §1.6 自检清单（提交前必走）

| 字段 | 定义 | 内容要求 |
|------|------|----------|
| **用例描述** | 用例标题 | **需求对象名称**（来自 S2 requirement_object.title），禁止加后缀、禁止加括号、禁止任何分隔符 |
| **功能描述** | 该用例验证的需求对象的功能点 | **LLM 自然语言创作**，描述"这个需求对象做了什么/起了什么作用"，禁止复制 S4/S5 的节点名称 |
| **前置条件** | 进入用例前系统所处的初始状态 | 具体数值（余额=xxx、道具备注=xxx），**禁止"无"占位**（除非业务确实无前置条件） |
| **操作步骤** | 玩家或策划的具体行动 | **每步包含具体 UI 元素名或具体数值**；禁止 `执行测试场景`/`验证预期结果`/`执行操作` 等模板语言 |
| **预期结果** | 操作后系统应产生的行为 | **纯业务结果**；禁止引用 S4 编号，禁止括号说明 |
| **test_method** | （可选）LLM 标注的测试方法 | 自由字符串，例如"等价类划分" / "异常流容错"——**不强制必须填** |
| **test_scenario** | （可选）方法下的具体场景 | 自由字符串，例如"空值" / "边界+1" / "超时30s"——**不强制必须填** |

**正确 vs 错误对比**：

```text
✅ 用例描述: 购买确认流程
✅ 功能描述: 余额不足时购买按钮禁用
✅ 操作步骤: 1. 玩家余额=1000游戏币，道具单价=500
            2. 尝试购买数量=3（总价=1500）
            3. 系统检测余额不足
✅ 预期结果: 1. 购买确认弹窗显示余额不足提示
            2. 【购买】按钮禁用（灰色不可点击）

❌ 用例描述: 购买确认弹窗 — 正常展示道具信息   （加了后缀，分隔符）
❌ 功能描述: 余额不足时购买按钮禁用（引用S4-R01）  （加了括号引用）
❌ 操作步骤: 执行操作：验证结果 / 执行测试场景 / 验证预期结果 （模板语言）
❌ 预期结果: 余额不足提示（引用S4-1.3异常树）      （括号引用）
❌ 前置条件: 无                                     （占位文本，业务有实际前置条件时禁止）
```

---

## 用例格式（10列）

> **重要（与 `ai_workflow/test_case_formatter.py` 严格一致）**：
> - **用例ID 前缀**采用 8 模块英文全名（按 `MODULES.md` §1 总表顺序）：`CONFIG-TC-NNN` / `UI-TC-NNN` / `BIZ-TC-NNN` / `AUX-TC-NNN` / `LINK-TC-NNN` / `LOG-TC-NNN` / `SPECIAL-TC-NNN` / `HINT-TC-NNN`（**禁止**用旧 4 字母缩写 `CFG/LNK/SPC/HNT`）
> - **模块字段**支持中英双语并存：`UI` 或 `界面` 任一；S6 阶段统一由 `test_case_formatter.py` 的 `normalize_module_name()` 归一化为 8 模块全名
> - **v1.6.1 旧枚举**（`RED_DOT` / `SYS_MSG` 等）由 `format_test_cases()` 自动迁移到 v1.7+ 现行枚举
> - 中英并存规则见 [`.cursor/MODULES.md` §3 中英映射表](../../../MODULES.md)

```json
[
  {
    "case_id": "UI-TC-001",
    "模块": "界面",
    "用例描述": "购买确认流程",
    "功能描述": "购买确认弹窗正常展示道具信息",
    "前置条件": "玩家已登录，余额充足，道具可购买",
    "操作步骤": "1. 玩家已登录，进入道具详情页\n2. 点击【购买】按钮\n3. 系统展示购买确认弹窗",
    "预期结果": "1. 弹窗展示道具名称\n2. 弹窗展示购买数量\n3. 弹窗展示总价\n4. 弹窗展示当前余额充足提示",
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
|--------|----------|
| P0 | 支付、购买、VIP折扣、促销、安全、日志 |
| P1 | 普通业务逻辑、订单、邮件、权限 |
| P2 | 界面展示、搜索、分页、加载 |

> 优先级**由 LLM 根据业务风险自由决定**，脚本不强制套用任何映射表。

---

## 自检清单（LLM 生成后、提交前必走）

> **评审驱动（v2.08+）**：按产物分阶段自检——**前一阶段不通过，禁止进入下一阶段**。

### json 评审门禁（5 项，写完 test_cases.json 后立即执行）

- [ ] **ID 唯一性 100%**：`{Module}-TC-{NNN}` 无重复
- [ ] **10 字段完整 100%**：case_id/module/用例描述/功能描述/前置条件/操作步骤/预期结果/优先级/用例状态/备注
- [ ] **前置条件不为准"无"**：必须包含具体初始状态（余额/道具数量/玩家等级等），"无" 仅在业务确实无前置条件时使用
- [ ] **操作步骤不为模板语言**：禁止 `执行测试场景`/`验证预期结果`/`执行操作` 等占位文本，每步必须有具体 UI 元素名或具体数值
- [ ] **5 项业务自检**：用例描述为需求对象名称 / 功能描述为需求对象功能点自然语言 / 操作步骤无模板语言 / 预期结果无括号引用 / 全文搜索"引用"为 0 处
- [ ] **优先级分布合理**：P0 ≥ 60%（关键路径优先）
- [ ] **8 模块覆盖**：CONFIG/UI/BIZ/AUX/LINK/LOG/SPECIAL/HINT 至少 1 个用例
- [ ] **🚨 不通过禁止生成 xlsx**——回 LLM 迭代 json

### md 评审门禁（写完 test_cases.md 后立即执行）

- [ ] md 中 TC 简表与 json 一致（数量/用例ID/优先级）
- [ ] md 总览统计数字与 json 一致（模块分布/优先级分布）
- [ ] md 分组（Epic）正确——按 S2 backlog 4 Epic 分

### xlsx 评审门禁（生成 test_cases.xlsx 后立即执行）

- [ ] **🚨 3 个文件全部生成**：test_cases.md + test_cases.json + **test_cases.xlsx**
- [ ] **xlsx 3 Sheet 全部存在**：Sheet1 用例详情 + Sheet2 模块统计 + Sheet3 类型统计
- [ ] **Sheet 1 行数 = json TC 数**
- [ ] **Sheet 2 模块数 = json 实际模块数**
- [ ] **Sheet 1 含 10 列字段**
- [ ] **xlsx 可被 openpyxl 重新打开**（round-trip 校验）

> **不强制 test_method / test_scenario 字段**——LLM 视业务需要自由标注。
> **不强制 1:N 拓宽**——LLM 根据业务复杂度自然决定 1:1 / 1:3 / 1:18。

### xlsx 生成强制规范（v2.08+ 关键约束）

**xlsx 是 S6 核心产物，缺它 = 阶段失败。**

| 检查项 | 要求 | 缺失时 |
|--------|------|--------|
| Sheet 1（用例详情）存在 | 必须 | fail_report_S6.md |
| Sheet 2（模块统计）存在 | 必须 | fail_report_S6.md |
| Sheet 3（类型统计）存在 | 必须 | fail_report_S6.md |
| Sheet 1 用例数 = JSON 用例数 | 100% | fail_report_S6.md |
| Sheet 1 含 10 列字段 | 100% | fail_report_S6.md |
| xlsx 可被 openpyxl 重新打开 | 100% | fail_report_S6.md |

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

# Sheet 1: 用例详情
ws1 = wb.create_sheet("测试用例详情")
headers = ["用例ID", "模块", "用例描述", "功能描述", "前置条件",
           "操作步骤", "预期结果", "优先级", "用例状态", "备注"]
ws1.append(headers)
for c in cases:
    ws1.append([c["case_id"], c["module"], c["用例描述"], c["功能描述"],
                c["前置条件"], c["操作步骤"], c["预期结果"],
                c["优先级"], c["用例状态"], c["备注"]])

# Sheet 2: 模块统计
ws2 = wb.create_sheet("模块统计")
ws2.append(["模块", "用例数", "占比", "P0", "P1", "P2"])
mc = Counter(c["module"] for c in cases)
total = len(cases)
for m, cnt in sorted(mc.items()):
    p = Counter(c["优先级"] for c in cases if c["module"] == m)
    ws2.append([m, cnt, f"{cnt/total*100:.1f}%",
                p.get("P0",0), p.get("P1",0), p.get("P2",0)])

# Sheet 3: 类型统计
ws3 = wb.create_sheet("类型统计")
ws3.append(["优先级", "用例数", "占比"])
pc = Counter(c["优先级"] for c in cases)
for p in ["P0", "P1", "P2"]:
    cnt = pc.get(p, 0)
    ws3.append([p, cnt, f"{cnt/total*100:.1f}%"])

wb.save("test_cases.xlsx")
```

---

## S4 参考规则

S4 流程图是 S6 **理解业务**的重要来源，但引用规则如下：

- **可以参考**：阅读 S4 理解业务流程、异常路径、风险场景，据此设计用例步骤和预期结果
- **禁止照抄**：不得将 S4 的节点名称、异常树编号、风险点名直接写入任何字段
- **如需注明**：仅在「备注」字段中写 `[参考S4-章节]`（非强制）

---

## 成功产出（3个文件）

路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/`
1. **Markdown**：`test_cases.md`
2. **JSON**：`test_cases.json`
3. **Excel**：`test_cases.xlsx`（3 个 Sheet：测试用例 / 模块统计 / 类型统计）

---

## 失败报告

路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/fail_report_S6.md`

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

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S6_TEST_CASES.mdc`
- 用例库：`workflow_assets/test_case_library/`
- 示例参考：`workflow_assets/example_test_cases/`
