---
name: aidocx-s6-test-cases
description: >
  AIDocxWorkFlow Stage 6 — 测试用例生成。将 S5 测试点转化为详细可执行的测试用例（Markdown + JSON + Excel 3 Sheet）。
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

**独立阶段**：可单独调用。上游材料（S5 test_points.json）审查合格后开始，失败写失败报告。

---

## 阶段入口

**触发**：`/aidocx-s6-test-cases` 或粘贴 S5 test_points.json

**前置材料**：
- S5 test_points.json：`workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json`
- S2 backlog（参考）：`workflow_assets/<req_name>/「S2 需求拆解」/<version>/backlog.md`
- S4 business_flow.md（**强烈推荐参考**）：`workflow_assets/<req_name>/「S4 流程图导出」/<version>/business_flow.md`

**材料缺失时**：生成失败报告，停止 S6。

---

## 字段语义（禁止颠倒）

> **AI 独立创作，不是模板填充。** 以下定义必须严格遵守。

| 字段 | 定义 | 内容要求 |
|------|------|----------|
| **用例描述** | 用例标题，唯一标识 | **纯 Story 名称**（S2 backlog 的 Story.title），禁止加后缀、禁止加括号、禁止任何分隔符 |
| **功能描述** | 该用例验证的具体功能点 | **AI 自然语言创作**，描述"验证什么"，禁止复制 S4/S5 的节点名称，禁止带 `—`，禁止带括号说明 |
| **前置条件** | 进入用例前系统所处的初始状态 | 具体数值（余额=xxx、道具备注=xxx），禁止模糊描述 |
| **操作步骤** | 玩家或策划的具体行动 | **每步包含具体 UI 元素名或具体数值**；禁止模板语言 |
| **预期结果** | 操作后系统应产生的行为 | **纯业务结果**；禁止引用 S4 编号，禁止括号说明 |

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

```json
[
  {
    "用例ID": "界面-TC-001",
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

---

## 质量门禁（生成后自检）

> **用例生成后、输出前，必须逐条自检。发现任意一条立即修正。**

### 自检清单

对所有生成的用例执行以下扫描：

- [ ] 用例描述是否只含纯 Story 标题（无 `—`、无括号）？
- [ ] 功能描述是否自然语言（无 S4/S5 节点名、无括号说明）？
- [ ] 操作步骤是否无任何模板语言（无「执行操作：」「执行：」）？
- [ ] 预期结果是否无任何括号引用（无 `（引用S4-xxx）`）？
- [ ] **全文搜索"引用"应为 0 处**

### 自检扫描命令

```python
import json
with open("test_cases.json") as f:
    cases = json.load(f)
for c in cases:
    for fld in ["用例描述","功能描述","前置条件","操作步骤","预期结果"]:
        v = c.get(fld,"")
        if "引用" in v or "—" in fld or "执行操作：" in v or "执行：" in v:
            print(f"[{c['用例ID']}] {fld}: {v[:60]}")
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
3. **Excel**：`test_cases.xlsx`（3个 Sheet：Sheet1用例详情 / Sheet2执行追踪 / Sheet3分层统计）

---

## 失败报告

路径：`workflow_assets/<req_name>/「S6 测试用例生成」/<version>/fail_report_S6.md`

---

## 自动化支持

```python
from ai_workflow.test_case_formatter import format_test_cases, compute_layered_stats
cases, meta = format_test_cases(tp_list, breakdown, test_points, 'test_cases')

from ai_workflow.excel.test_case_writer import write_test_cases
write_test_cases(cases, version, filename, metadata=meta)

from ai_workflow.s6_report import generate_s6_report
generate_s6_report(cases, version, req_name, filename, duration_s=0.0,
                   s5_tp_count=total_tp, s5_output_path=tp_path, save=True)
```

---

## 参考文档

- 完整阶段规范：`.cursor/rules/STAGE_S6_TEST_CASES.mdc`
- 用例库：`workflow_assets/test_case_library/`
- 示例参考：`workflow_assets/example_test_cases/`
