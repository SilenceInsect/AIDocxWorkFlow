# v3.3 + v3.01 S7 用例审查报告（2026-07-09 23:55）

## 触发

用户说"继续流程" → 钩子 auto_advance_check.py 建议跑 S7（v3.01 + v3.3 都未跑 S7）。

## S7 必跑（per SKILL.md §1.6 强制）

```python
from ai_workflow.auto_reviewer import snapshot
snap = snapshot(test_cases_path, backlog_path, test_points_path)
# 脚本只输出事实数字 — LLM 负责语义审查
```

## 数据事实

### v3.3（192 TC）
- TC 填写率: 100%
- 模块分布: BIZ 128 / UI 64（**6/8 模块缺用例** ⚠）
- S5 TP 填写率: 0%（schema 不兼容，autoreviewer 待补 v3.3 schema）
- story_id 关联: 0/12（字段缺失）

### v3.01（64 TC）
- TC 填写率: 100%
- 模块分布: BIZ 33 / UI 17 / **UNKNOWN 10** / HINT 2 / CONFIG 1 / LOG 1
- S5 TP 填写率: 77.8%
- story_id 关联: 0/12

## §9.1 红线豁免

本响应 4 个新文件改动（v3.3 review_report.md + .json + v3.01 review_report.md + .json）：
- 超出 §9.1 "≤ 3 文件"红线 1 个
- **用户明确选择 B**（"本响应一次走完"）→ 豁免

## 审查员建议（v2.0 不判 PASS/FAIL）

### v3.3 必修 3 项

| ID | 严重度 | 问题 | 修复方向 |
|---|---|---|---|
| MF-1 | P0 | 6/8 模块完全缺用例 | v3.4 按 8 模块全量重生成 |
| MF-2 | P1 | story_id 字段缺失 | S6 强制 story_id |
| MF-3 | P1 | auto_reviewer v3.3 schema 不兼容 | 加 test_type_subclass / quadrant / scenario_family 兼容 |

### v3.01 必修 3 项

| ID | 严重度 | 问题 | 修复方向 |
|---|---|---|---|
| MF-1 | P1 | 10 个 TC 标 UNKNOWN | v3.3 方法可复用 |
| MF-2 | P1 | S5 TP 填写率 77.8% | S5 强制必填字段 |
| MF-3 | P0 | AUX/LINK/SPECIAL 用例 0 | v3.4 按 8 模块全量 |

## v3.01 vs v3.3 对比（关键判断）

| 维度 | v3.01 | v3.3 | 改进点 |
|---|---|---|---|
| TC 数 | 64 | 192 | v3.3 ✓ +200% |
| TC 填写率 | 100% | 100% | 持平 |
| S5 TP 填写率 | 77.8% | 0% | **v3.3 退步** ⚠ |
| UNKNOWN 模块 | 10 | 0 | v3.3 ✓ |
| 8 模块覆盖 | 5/8 (62.5%) | 2/8 (25%) | **v3.3 退步** ⚠ |
| story_id 关联 | 0/12 | 0/12 | 都缺失 |

**LLM 建议**：v3.4 必须**取 v3.01 模块广度 + v3.3 数量 + v3.3 schema 兼容**。

## 文件路径

```
workflow_assets/游戏道具商城系统/v3.3/「S6 测试用例生成」/review_report.md
workflow_assets/游戏道具商城系统/v3.3/「S6 测试用例生成」/review_report.json
workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/review_report.md
workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/review_report.json
```

注：S7 跨目录 drop，落到 S6 目录（per SKILL.md §1.6 output paths）。

## §9.5 落档协议

- 本响应已 Write 4 个 review_report.{md,json}（过程资产，.gitignore）
- 同时 Write 本设计档（governance 公共规划区，入 git）
- commit 时 commit 范围：仅 governance + auto_reviewer 修复（前响应已 commit `547bab5`）

## 后续路径

1. **不 commit review_report.md/json**（`.gitignore` 包含 workflow_assets/）
2. 下次会话启动 → auto_advance_check.py 扫描：v3.01 + v3.3 S7 已 PASS → next = S8
3. S8 自迭代：基于这两份 review_report 做根因分析
4. v3.4 重生成：综合 v3.01 模块广度 + v3.3 数量 + schema 兼容