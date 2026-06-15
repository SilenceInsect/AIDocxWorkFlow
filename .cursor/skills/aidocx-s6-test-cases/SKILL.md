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

> **设计哲学（v2.0 重构 — 2026-06-15）**：
> - **LLM 负责推理**：从 S5 TP 派生出几个 TC、用什么方法、步骤怎么写——全是 LLM 推理决定
> - **脚本只负责整理**：ID 分配 / 字段归一化 / 写文件
> - **不设硬指标**：1:1 也行、1:5 也行、1:20 也行——业务复杂度自然决定
> - **真实需求多种多样**，硬指标脚本只服务一种结构；**LLM 推理 + 脚本整理**能适配任意结构

**独立阶段**：可单独调用。上游材料（S5 test_points.json）审查合格后开始，失败写失败报告。

---

## §1.4 LLM 必读材料（阶段前置）

**生成测试用例前，必须先 Read 以下材料。禁止凭印象直接生成。**

| # | 材料 | 路径 | 必读原因 |
|---|---|---|---|
| 1 | 8 模块总表 | `.cursor/MODULES.md`（§1 总表）| 所有 TP 必须有模块前缀；模块 × 类型双维度决定 TC 拓宽方向 |
| 2 | 模块边界区分 | `.cursor/MODULES.md`（§4 各模块 O_boundary.md）| HINT vs UI、BIZ vs CONFIG 是 S6 高误标区；判定前必读 |
| 3 | S5 test_points | `workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json` | 每个 TP 的 module / test_type 是 TC 拓宽的输入 |
| 4 | S4 business_flow | `workflow_assets/<req_name>/「S4 流程图导出」/<version>/business_flow.md` | 异常决策树和风险点是 EXCEPTION TC 的核心来源 |
| 5 | 模块子模板 | `workflow_assets/module_templates/`（按 TP 的 module 字段）| 每个模块的子类枚举（如 BIZ→A-I、HINT→A-M）决定 TC 方法选择 |

---

## 字段语义（LLM 自由创作，不是模板填充）

| 字段 | 定义 | 内容要求 |
|------|------|----------|
| **用例描述** | 用例标题 | **纯 Story 名称**（S2 backlog 的 Story.title），禁止加后缀、禁止加括号、禁止任何分隔符 |
| **功能描述** | 该用例验证的具体功能点 | **LLM 自然语言创作**，描述"验证什么"，禁止复制 S4/S5 的节点名称 |
| **前置条件** | 进入用例前系统所处的初始状态 | 具体数值（余额=xxx、道具备注=xxx），禁止模糊描述 |
| **操作步骤** | 玩家或策划的具体行动 | **每步包含具体 UI 元素名或具体数值**；禁止模板语言 |
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
❌ 操作步骤: 执行操作：验证结果                     （模板语言）
❌ 预期结果: 余额不足提示（引用S4-1.3异常树）      （括号引用）
```

---

## 用例格式（10列）

> **重要（与 `ai_workflow/test_case_formatter.py` 严格一致）**：
> - **用例ID 前缀**采用 8 模块英文全名（按 `MODULES.md` §1 总表顺序）：`CONFIG-TC-NNN` / `UI-TC-NNN` / `BIZ-TC-NNN` / `AUX-TC-NNN` / `LINK-TC-NNN` / `LOG-TC-NNN` / `SPECIAL-TC-NNN` / `HINT-TC-NNN`（**禁止**用旧 4 字母缩写 `CFG/LNK/SPC/HNT`）
> - **模块字段**支持中英双语并存：`UI` 或 `界面` 任一；S6 阶段统一由 `test_case_formatter.py` 的 `normalize_module_name()` 归一化为 8 模块全名
> - **v1.6.1 旧枚举**（`RED_DOT` / `SYS_MSG` 等）由 `format_test_cases()` 自动迁移到 v1.7+ 现行枚举
> - 中英并存规则见 [`.cursor/MODULES.md` §3 中英映射表](../../MODULES.md)

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

- [ ] 用例描述是否只含纯 Story 标题（无 `—`、无括号）？
- [ ] 功能描述是否自然语言（无 S4/S5 节点名、无括号说明）？
- [ ] 操作步骤是否无任何模板语言（无「执行操作：」「执行：」）？
- [ ] 预期结果是否无任何括号引用（无 `（引用S4-xxx）`）？
- [ ] **全文搜索"引用"应为 0 处**

> **不强制 test_method / test_scenario 字段**——LLM 视业务需要自由标注。
> **不强制 1:N 拓宽**——LLM 根据业务复杂度自然决定 1:1 / 1:3 / 1:18。

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
