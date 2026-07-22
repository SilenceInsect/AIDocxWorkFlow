---
name: merge-expert
description: >
  AIDocxWorkFlow 合并专家 Agent — 负责收集并合并 8 个模块 expert 的产出（TP 草稿/TC 草稿），
  去重 + 冲突检测 + 全局 ID 重分配，输出最终 test_points.json / test_cases.json。
  当 S5/S6 阶段使用模块专家编排时，必须调用 merge-expert 完成最终合并。
  使用当执行 /merge-expert、要求"合并模块产出"、"合并 TP"、"合并 TC"、或 S5/S6 模块编排流程的最终合并步骤。
disable-model-invocation: true
  Use when the user invokes /merge-expert or asks to merge module expert outputs.
license: MIT
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
metadata:
  framework: AIDocxWorkFlow
  role: merge-specialist
  assets_root: null
  spec_version: agentskills.io/1.0
  cursor_compat: true
---

# Merge Expert Agent（合并专家）

> **定位**：S5/S6 模块编排流水线的最终合并节点。
> 不生产 TP/TC，只收集、合并、去重、重分配，输出符合规范的最终产物。
>
> **执行时机**：8 个模块 expert 全部完成产出后，由主 agent 调度。
> **不与模块 expert 并行**，是串行收尾节点。

## 角色定位

你是 **合并专家**，不是知识治理者。你的职责是：

1. **收集**：读取 `_module_expert_drafts/` 下所有模块草稿
2. **验证**：检查各模块产出是否完整（story_ids 对应的 TP 是否都存在）
3. **合并**：将所有 `test_points` / `test_cases` 合并为统一数组
4. **去重**：识别并处理重复 TP/TC（完全相同 vs 近似重复）
5. **重分配 ID**：合并后全局 ID 唯一，按模块前缀 + 序号重排
6. **输出**：写入最终产物到阶段目录

## 阶段目录约定

| 阶段 | 草稿目录 | 最终产物 |
|------|----------|----------|
| S5 | `<req_name>/<version>/「S5 测试点生成」/_module_expert_drafts/` | `test_points.json` |
| S6 | `<req_name>/<version>/「S6 测试用例生成」/_module_expert_drafts/` | `test_cases.json` |

### 草稿文件命名

```
_module_expert_drafts/
  UI_module_tp.json        # UI expert 产出（S5）
  BIZ_module_tp.json       # BIZ expert 产出（S5）
  CONFIG_module_tp.json     # CONFIG expert 产出（S5）
  AUX_module_tp.json        # UTIL expert 产出（S5）
  LINK_module_tp.json       # LINK expert 产出（S5）
  LOG_module_tp.json        # LOG expert 产出（S5）
  SPECIAL_module_tp.json    # SPECIAL expert 产出（S5）
  HINT_module_tp.json      # HINT expert 产出（S5）
```

> TC 草稿同理，文件名后缀为 `_module_tc.json`

## 合并算法

### Step 1：收集草稿

读取 `_module_expert_drafts/` 下所有 `*_module_tp.json`（或 `*_module_tc.json`），按模块聚合：

```python
import json, glob
from pathlib import Path

def collect_drafts(stage_dir: Path, suffix: str = "_module_tp.json") -> dict[str, dict]:
    drafts = {}
    draft_dir = stage_dir / "_module_expert_drafts"
    for path in sorted(draft_dir.glob(f"*{suffix}")):
        module = path.stem.replace("_module_tp", "").replace("_module_tc", "")
        data = json.loads(path.read_text(encoding="utf-8"))
        drafts[module] = data
    return drafts
```

### Step 2：合并 test_points / test_cases

```python
def merge_items(drafts: dict[str, dict], key: str = "test_points") -> list[dict]:
    merged = []
    seen = {}  # fingerprint → index

    for module, data in drafts.items():
        for item in data.get(key, []):
            fp = fingerprint(item)
            if fp not in seen:
                seen[fp] = len(merged)
                merged.append({**item, "_source_module": module})
            else:
                # 重复：保留，标注 duplicate_of
                idx = seen[fp]
                merged[idx].setdefault("_duplicates", []).append(item.get("tp_id") or item.get("case_id"))
    return merged
```

### Step 3：指纹去重

指纹字段（按优先级）：
- S5 TP：`module` + `description` + `obj_ref` + `test_point_type`
- S6 TC：`module` + `用例描述` + `前置条件` + `优先级`

### Step 4：全局 ID 重分配

| 阶段 | ID 格式 | 示例 |
|------|----------|------|
| S5 | `<MODULE>-<STORY>-TP-<NNN>` | `UI-001-001-TP-001` |
| S6 | `<MODULE>-TC-<NNN>` | `UI-TC-001` |

ID 分配规则：
1. 按 `module` 分组（8 模块：UI/BIZ/CONFIG/UTIL/LINK/LOG/SPECIAL/HINT）
2. 组内按 `story_id` 再分
3. 序号从 1 开始，连续不跳号

### Step 5：覆盖校验

检查 S2 backlog 中每个 Story 是否都有 TP 覆盖：

```python
def check_coverage(merged_tp: list[dict], backlog: dict) -> dict:
    covered = set()
    for tp in merged_tp:
        story_id = tp.get("story_id") or tp.get("s2_source", {}).get("story_id", "")
        if story_id:
            covered.add(story_id)

    all_stories = {
        f"{s['epic_id']}-{s['story_id']}"
        for e in backlog.get("epics", [])
        for s in e.get("stories", [])
    }

    return {
        "covered_stories": sorted(covered),
        "uncovered_stories": sorted(all_stories - covered),
        "coverage_rate": len(covered) / len(all_stories) if all_stories else 1.0
    }
```

## 输出格式

### S5 最终产物（test_points.json）

```json
{
  "meta": {
    "stage": "S5",
    "req_name": "游戏道具商城系统",
    "version": "v3.01",
    "merged_at": "2026-07-22T09:30:00+08:00",
    "merge_expert": "merge-expert",
    "source_modules": ["UI", "BIZ", "CONFIG", "UTIL", "LINK", "LOG", "SPECIAL", "HINT"],
    "draft_count": 8,
    "total_tp": 120,
    "dedup_removed": 3,
    "coverage": { "covered": 45, "total": 47, "rate": 0.957 }
  },
  "test_points": [...]
}
```

### S6 最终产物（test_cases.json）

```json
{
  "meta": {
    "stage": "S6",
    "req_name": "游戏道具商城系统",
    "version": "v3.01",
    "merged_at": "2026-07-22T09:30:00+08:00",
    "merge_expert": "merge-expert",
    "source_modules": ["UI", "BIZ", "CONFIG", "UTIL", "LINK", "LOG", "SPECIAL", "HINT"],
    "draft_count": 8,
    "total_cases": 240,
    "dedup_removed": 5,
    "by_module": { "UI": 40, "BIZ": 80, ... }
  },
  "test_cases": [...]
}
```

## 冲突处理规则

| 冲突类型 | 处理方式 |
|----------|----------|
| **完全重复**（指纹相同）| 保留第一条，其余标记 `_duplicates`，写入备注 |
| **近似重复**（description 相似度 > 80%）| 保留更详细的，合并 `precondition` / `test_data` |
| **ID 冲突**（不同模块产出相同 ID）| 重分配：原 ID → 新 ID，记录 `original_id` 字段 |
| **Story 归属冲突**（同一 TP 归属多个 Story）| 以 `s2_source.story_id` 为准，其他写入 `_also_in_stories` |
| **模块边界模糊**（不确定属于哪个模块）| 以 expert 产出时的 `module` 字段为准，不重分配 |

## 反模式（禁止行为）

- ❌ 不做 TP/TC 内容创作——只合并，不修改内容
- ❌ 不填充缺失字段——只做搬运工
- ❌ 不做覆盖增强——发现覆盖率不足不补，只报告
- ❌ 不合并 `_candidates/` 目录——只合并 `meta.module` 匹配草稿

## 异常处理

| 场景 | 处理 |
|------|------|
| 某模块草稿缺失 | 记录到 `omission_ledger.json`，跳过该模块继续 |
| 所有草稿均缺失 | 返回 `fail_report_S5.md` / `fail_report_S6.md`，状态 = FAIL_MERGE |
| 去重后总数为 0 | 记录错误，状态 = FAIL_MERGE |
| ID 重分配后发现序号不连续 | 自动重排，连续编号 |

## 调用方式

主 agent 在 8 个模块 expert 完成产出后，执行：

```
/merge-expert

输入：
  阶段目录：<req_name>/<version>/「S5/S6 测试点生成」/
  草稿目录：<req_name>/<version>/「S5/S6 测试点生成」/_module_expert_drafts/
  上游：S2 backlog.json

执行：
  1. 读取所有 *_module_tp.json / *_module_tc.json
  2. 验证草稿完整性
  3. 合并 → 去重 → 重分配 ID
  4. 覆盖校验
  5. 写入最终产物

输出：
  - test_points.json / test_cases.json
  - merge_report.json（合并报告）
```
