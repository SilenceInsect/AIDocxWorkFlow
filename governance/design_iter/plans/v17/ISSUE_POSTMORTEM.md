# Phase 4 — 问题复盘（Issue Postmortem）

> **本档**：v17 自检发现的问题清单
> **严重度分类**：HIGH（必须修）/ MEDIUM（建议修）/ LOW（可选）

---

## 问题清单

| # | 问题 | 严重度 | 修复方案 | 涉及文件 |
|---|---|---|---|---|
| **I-01** | STAGE_S6_TEST_CASES.mdc §1.6（行 134-171）有 12 处 `v14/v11/v10` + 强制/必填/沿用/落地组合——§11 严重违规 | **HIGH** | 改为中性"字段溯源方案"描述，去掉版本号和"强制/必填"等永久规范标记 | STAGE_S6_TEST_CASES.mdc |
| **I-02** | STAGE_S6_TEST_CASES.mdc §v11（行 158-181）整段标题和说明都用 v11 版本号 | **HIGH** | 整段重命名为"字段溯源版 S5→S6 链路 + 双层覆盖门禁"，去掉版本号 | STAGE_S6_TEST_CASES.mdc |
| **I-03** | SKILL.md s5 有 30 处 v\d+ 违规（含 v10/v11/v12/v16 T5 新增/SSOT/落地/废弃/沿用/兼容）| **HIGH** | 改为"字段溯源版"中性描述，去掉版本号和"废弃/沿用/兼容"等历史对照描述 | aidocx-s5-test-points/SKILL.md |
| **I-04** | SKILL.md s6 有 31 处 v\d+ 违规（§v11/§v12/沿用/必填/落地/SSOT）| **HIGH** | 改为"字段溯源版"中性描述 | aidocx-s6-test-cases/SKILL.md |
| **I-05** | STAGE_S5_TEST_POINTS.mdc 也有 `v1.0` 字面量（行 607 Python 示例）| LOW | 已知豁免（Python 字面量），不修 | STAGE_S5_TEST_POINTS.mdc |
| **I-06** | ~~s6_report.py 和 check_field_completion.py 仍延后~~ **(Round 14 闭环：s6_report.py 引用已废弃)** / check_field_completion.py 仍延后 | LOW | 已知豁免（本轮不修） | ~~ai_workflow/s6_report.py~~ + scripts/check_field_completion.py |
| **I-07** | AGENTS.md 未同步更新（按 v17 治理档判定冻结，CHANGELOG 由人工维护）| LOW | 不修 | AGENTS.md + CHANGELOG.md |
| **I-08** | INDEX.md / INDEX.json 未标 v17 = current | LOW | 需在 Phase 6 末尾用 CLI 生成，本轮不修 | INDEX.md + INDEX.json |

---

## 严重度统计

- **HIGH**：4 个（I-01 ~ I-04）
- **LOW**：4 个（I-05 ~ I-08）

**需修复总数：4 个 HIGH 项**。

---

## 修复优先级

1. **I-01 + I-02**（同文件 STAGE_S6_TEST_CASES.mdc）→ 一次 StrReplace 完成
2. **I-03**（SKILL.md s5）→ 多次 StrReplace（30 处）
3. **I-04**（SKILL.md s6）→ 多次 StrReplace（31 处）

**§9.1 单 turn ≤3 文件** → 分 3 批完成（每批 1-2 文件）。

---

## 落档协议

- 本档已落档
- 修改文件数：1（本档）
- 单次响应工具调用 ≤ 10
- **进入 Phase 5 迭代修复**（I-01 ~ I-04 按序修）