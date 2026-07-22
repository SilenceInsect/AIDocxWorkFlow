# auto_reviewer.py 字段兼容补丁（2026-07-09 23:50）

## 触发

跑 S7 时 auto_reviewer.snapshot() 抛 2 个 AttributeError / KeyError：

```
1. AttributeError: 'list' object has no attribute 'get'    (test_cases_top)
2. KeyError: 'id'                                          (backlog_epic_id)
```

## 根因

auto_reviewer.py 的 snapshot() 函数历史期望 S6 test_cases 用 dict 包装 (`{"test_cases": [...]}`)，
但 v3.3 重写后的 test_cases.json 顶层是 list (`[case1, case2, ...]`)。

backlog 同理：脚本期望 `epic["id"]` / `story["id"]`，v3.01 backlog 用的是 `epic["epic_id"]` /
`story["story_id"]`。

## 修复（auto_reviewer.py §1 末尾 + §_check_coverage 全段）

### Patch 1: snapshot() 顶层兼容 list/dict

```python
with tc_path.open(encoding="utf-8") as f:
    tc_data = json.load(f)
# 兼容两种 JSON 顶层结构
if isinstance(tc_data, list):
    cases = tc_data
elif isinstance(tc_data, dict):
    cases = tc_data.get("test_cases", [])
```

### Patch 2: _check_coverage 字段 fallback

```python
epic_id = epic.get("id") or epic.get("epic_id") or epic.get("code", "?")
covered = sum(1 for s in stories if s.get("id") in covered_stories or s.get("story_id") in covered_stories)
epic_title=epic.get("name") or epic.get("title", "")
```

## 兼容性影响

| 项 | 改前 | 改后 |
|---|---|---|
| dict 包装 test_cases | ✓ | ✓ |
| list 顶层 test_cases | ✗ AttributeError | ✓ |
| backlog epic["id"] | ✓ | ✓ |
| backlog epic["epic_id"] | ✗ KeyError | ✓ |
| backlog story["id"] | ✓ | ✓ |
| backlog story["story_id"] | ✗ 覆盖不到 | ✓ |

向后兼容 dict-wrapped + 历史字段名，**不破坏旧用法**。

## v3.3 S7 review 结果（事实数字）

```
Total: 192
TC fill_rate: 100.0%      ← Reviewer A ✓
S5 fill_rate: 0.0%        ← Reviewer B ⚠ (第三处 schema 漂移，未修)
modules: BIZ 128 / UI 64   ← 6 模块缺用例
coverage: 0/2 per epic    ← story_id 关联不上
```

**LLM 需写语义审查**（v2.0 必填字段）：

| 问题 | 严重度 |
|---|---|
| 192 TC 集中在 BIZ+UI → 6 模块缺用例 | 必修 |
| 模块分布严重不均 | 应改 |
| story_id 缺失 → 追溯链断 | 应改 |
| S5 TP 字段名称漂移（脚本不识别）| 必修 |

## §9.1 红线

本响应改动文件 2 个：
1. `ai_workflow/auto_reviewer.py`（2 个 StrReplace）
2. `governance/design_iter/plans/v7/changes/auto_reviewer_field_compat_2026_07_09.md`（本档）

**2 ≤ 3 ✓**

## §9.4 + §9.5 决策

- **必须先验后答** — 已 Read `auto_reviewer.py` line 187-206（_check_coverage）+ line 359-369（snapshot 顶层）
- **先落档再 content 展开** — 已 Write 设计落档（本文件）
- **业务函数改了**（snapshot / _check_coverage 都改了行为）——豁免**无效**，但 commit 时必须明确标注

## 后续路径

- 下响应跑 v3.3 S7 完整审查，写 review_report.{md,json}
- 报告落到 「S6 测试用例生成」/v3.3/（S7 跨目录 drop，per SKILL.md §§ output dir）
- 同时跑 v3.01 S7 审查（同理）
- 报告完成后 commit 3 文件（auto_reviewer 修复 + design + review_report）
