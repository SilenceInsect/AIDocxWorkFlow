---
name: aidocx-s6-test-cases
description: AIDocxWorkFlow Stage 6 — 测试用例生成。将 S5 测试点转化为详细可执行的测试用例（Markdown + JSON + Excel 3 Sheet）。使用当用户执行 /aidocx-s6-test-cases、粘贴 S5 test_points.json、或进行 S6 测试用例生成任务。
disable-model-invocation: true
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
  - 异常/错误决策树和风险点清单可补充 EXCEPTION 类用例的具体步骤和预期结果
  - 时序图可确保用例步骤顺序与系统调用链路一致

**材料缺失时**：生成失败报告，停止 S6。

---

## 用例格式（10列）

| 字段 | 说明 |
|------|------|
| 用例ID | `{Module}-TC-{NNN}`，如 `UI-TC-001` |
| 模块 | UI/BIZ/CONFIG/HINT/LINK/SPECIAL/LOG/AUX |
| 功能描述 | 来自 Story 标题 |
| 用例描述 | 具体功能点 |
| 前置条件 | 系统状态要求（具体账号、等级、VIP等） |
| 操作步骤 | 编号步骤，每步精确描述（UI元素名称 + 具体数值） |
| 预期结果 | 每步对应的可验证结果 |
| 优先级 | P0（必须）/ P1（重要）/ P2（可选） |
| 用例状态 | Draft / Ready / Deprecated |
| 备注 | 边界条件、测试数据要求 |

### 步骤写作规则

- ✅ 正确：`点击【购买】按钮，弹出订单确认对话框`
- ❌ 错误：`点击购买按钮` | `验证页面正常`
- 每步必须包含具体 UI 元素名称或具体数值
- 每步独立可验证
- 最大 8 步，超过则拆分

### 优先级判断

| 优先级 | 适用场景 |
|--------|----------|
| P0 | 支付、购买、VIP折扣、促销、安全、日志 |
| P1 | 普通业务逻辑、订单、邮件、权限 |
| P2 | 界面展示、搜索、分页、加载 |

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
- Prompt 模板：`ai_workflow/prompts/test_case_gen.md`
- 用例库：`workflow_assets/test_case_library/`
- 示例参考：`workflow_assets/example_test_cases/`
