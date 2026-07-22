#!/usr/bin/env python3
"""Round 15 — 同源用例聚合器（修复步骤碎裂）。

Why
----
v3.01 test_cases.json 全部 331 条 TC 都是 `steps=[1]`（单步）+ `expected_results=[1]`（单预期）。
同一 `obj_id + feature_point_ref + test_scenario` 下被拆成 6~11 条独立 TC，每条只承载
一个动作（"玩家点击商城入口"/"系统加载商城首页"/"观察销量排序"...），下游高级测试工程师
拿到 xlsx 后认为"像任务清单，不像用例"。

This module 在内存中**幂等**地把同源 TC 合并为 1 条多步 TC：

- 聚合键：`{obj_id} + {feature_point_ref} + {test_scenario}` 完全相同视为同源
- steps：按 step_num 顺序拼接为 `[ {step_num:1, action:A1}, ..., {step_num:N, action:AN} ]`
- expected_results：按 TC 出现顺序拼接为 `[E1, E2, ..., EN]`
- 保留字段（首条 TC）：用例描述 / 功能描述 / priority / preconditions / module / obj_name /
  fp_name / case_id / s5_ref / tp_ref / obj_id / feature_point_ref
- 反向保护：obj_id 不同 / scenario 不同 → 不合并

This module 是 pure data plumbing——无 I/O、无全局状态。driver script 拥有 orchestration。

SSOT 对齐
---------
- `STAGE_S6_TEST_CASES.mdc` §11（同源合并例外条款由 Round 15 写入）
- `aidocx-s6-test-cases/SKILL.md` §11（同源合并例外条款由 Round 15 写入）
- `l1_s6.L1S6Validator`（合并后字段不变，重新跑 L1/L2 验证）

Testing
-------
`def self_test()` + `--self-test` argv 覆盖 5 critical paths：

- 同源 2 TC 合并 → 1 TC × 2 steps
- 同源 3 TC 合并 → 1 TC × 3 steps
- 不同 obj_id 不合并 → 2 TC × 1 step
- 不同 test_scenario 不合并 → 2 TC × 1 step
- 合并后字段保留（用例描述/优先级/前置条件）
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_REPO_ROOT / "ai_workflow") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "ai_workflow"))


# ---------------------------------------------------------------------------
# Group key + merge logic
# ---------------------------------------------------------------------------

# Fields that form the group identity. Two cases share identity iff all four
# keys match exactly (after strip). Empty/None on either side is treated as
# "no group key" → never merged (defensive against missing-data fallout).
_GROUP_KEY_FIELDS = ("obj_id", "feature_point_ref", "test_scenario")


def _group_key(case: Mapping[str, Any]) -> tuple[str, ...] | None:
    """Return the merge key for a case, or None if any key field is empty.

    Returning None means "this case cannot be merged with anything" — the
    caller treats it as a singleton group. This avoids accidental merging
    when upstream data is incomplete (e.g. legacy English schema).
    """
    key: list[str] = []
    for field in _GROUP_KEY_FIELDS:
        val = case.get(field)
        if val is None:
            return None
        val_str = str(val).strip()
        if not val_str:
            return None
        key.append(val_str)
    return tuple(key)


def _merge_steps(first_steps: list[Any], extra_steps: list[Any]) -> list[dict[str, Any]]:
    """Concatenate steps with re-numbered step_num starting at 1.

    Both inputs are expected to already be in 1-based order (Round 12/14
    convention is ``steps=[{step_num:1, action:...}]``), but we renumber
    defensively so out-of-order legacy payloads still produce a clean
    output.
    """
    merged: list[dict[str, Any]] = []
    all_steps: list[Any] = list(first_steps) + list(extra_steps)
    for idx, step in enumerate(all_steps, start=1):
        if isinstance(step, dict):
            new_step = dict(step)
            new_step["step_num"] = idx
            merged.append(new_step)
        else:
            merged.append({"step_num": idx, "action": str(step)})
    return merged


def _merge_expected(first_exp: list[Any], extra_exp: list[Any]) -> list[str]:
    """Concatenate expected_results preserving the source ordering.

    Round 19 (V-003 BLOCKER fix): deduplicate while preserving order. Merged
    expected_results must not contain literal duplicate strings — downstream
    xlsx H-column rendering shows the deduped list joined with ``\\n``, and
    a triple-printed line ("普通玩家可在商城道具列表或搜索结果中看到该道具"
    ×3 in BIZ-TC-232) is a downstream blocking defect. The dedup preserves
    first-occurrence order; if a later case brings a new expectation, that
    new expectation still appends after the originals. We dedupe the **list**
    level — strings that are themselves newlines/whitespace get normalised
    to empty via ``strip()`` and dropped (matches the legacy
    ``_get_field`` list→newline behaviour).
    """
    seen: set[str] = set()
    out: list[str] = []
    for raw in list(first_exp) + list(extra_exp):
        s = str(raw).strip()
        if not s:
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


# Fields that survive the merge as-is from the FIRST case in the group.
# Anything not listed here is intentionally dropped from later cases — the
# goal is "single TC, single set of metadata, multiple steps/expectations".
_PRESERVED_FIELDS = (
    "case_id", "tc_id", "module", "用例描述", "功能描述", "priority", "优先级",
    "preconditions", "前置条件", "s5_ref", "tp_ref", "obj_id", "feature_point_ref",
    "obj_name", "fp_name", "用例状态", "备注", "test_methods", "assertion",
)


# List-valued fields that must stay in sync between their canonical Chinese
# key and any legacy English mirror. After a merge, the canonical Chinese
# field may still hold a stale string-ified value from a prior
# ``mirror_bilingual_aliases`` pass (Round 14 normalizer treats canonical
# keys as authoritative, so it never overwrites). We force the canonical
# Chinese key back to the freshly merged list so downstream
# ``test_case_formatter._get_field`` reads the list, not the stale string.
_LIST_FIELDS_TO_SYNC: tuple[tuple[str, ...], ...] = (
    ("steps", "操作步骤"),
    ("expected_results", "预期结果"),
    ("preconditions", "前置条件"),
)


def _sync_list_fields_after_merge(case: dict[str, Any]) -> None:
    """Force canonical Chinese list fields to mirror the merged English list.

    Round 14's normalizer uses an idempotent mirror: ``预期结果`` once filled
    with ``"ok"`` is never overwritten by ``mirror_bilingual_aliases`` even if
    ``expected_results`` later grows to ``["ok", "completed"]``. After a merge
    we explicitly push the merged English list back into the canonical Chinese
    key, overwriting the stale string. This is safe because the canonical
    Chinese key is downstream-consumed only via ``_get_field``'s list→newline
    rendering path.
    """
    if not isinstance(case, dict):
        return
    for english_key, chinese_key in _LIST_FIELDS_TO_SYNC:
        english_val = case.get(english_key)
        if not isinstance(english_val, list):
            continue
        # Only overwrite if the canonical Chinese value is missing, a stale
        # string, or a list whose length differs from the English list.
        chinese_val = case.get(chinese_key)
        if (
            not chinese_val
            or isinstance(chinese_val, str)
            or (isinstance(chinese_val, list) and len(chinese_val) != len(english_val))
        ):
            case[chinese_key] = list(english_val)


def merge_grouped(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """In-place dedupe-and-merge of same-scenario test cases.

    Returns the merged case list (same dict objects as the merged-first
    representatives; later dicts in each group are dropped). The original
    ``cases`` list is mutated: surviving cases may have their ``steps`` /
    ````expected_results`` arrays rewritten, but all other fields stay
    untouched.

    Behaviour:

    1. Sort by group key (stable; preserves upstream case ordering for
       first case within a group).
    2. Walk sorted cases; same key → merge into accumulator; new key → flush
       accumulator and start a fresh one.
    3. Cases whose group key is ``None`` (incomplete metadata) are flushed
       immediately as singletons — they can never be merged.
    4. Round 16: every merged TC receives a ``source_case_ids`` field
       (list[str]) — the original ``case_id`` of every TC that contributed
       to the merge. The first case's id is the survivor; later ids are the
       source. Singletons receive a one-element list containing only their
       own id (so downstream consumers always see a list).
    """
    if not isinstance(cases, list) or not cases:
        return list(cases) if isinstance(cases, list) else []

    # Decorate-sort-undecorate to preserve first-occurrence order within groups.
    decorated: list[tuple[tuple[str, ...] | None, int, dict[str, Any]]] = []
    for idx, case in enumerate(cases):
        if not isinstance(case, dict):
            decorated.append((None, idx, case))  # type: ignore[arg-type]
            continue
        key = _group_key(case)
        decorated.append((key, idx, case))

    decorated.sort(key=lambda item: (
        0 if item[0] is not None else 1,
        item[0] if item[0] is not None else (),
        item[1],
    ))

    merged: list[dict[str, Any]] = []
    current_key: tuple[str, ...] | None = None
    current_repr: dict[str, Any] | None = None
    # Round 16: track the source case_ids contributing to the current group so
    # we can attach them to the surviving TC as ``source_case_ids``.
    current_source_ids: list[str] = []

    def _flush() -> None:
        nonlocal current_repr, current_source_ids
        if current_repr is not None:
            # Round 16: write the source_case_ids field. The first TC's id is
            # already in current_repr["case_id"]; source_case_ids records the
            # full lineage so downstream consumers (xlsx formatter, audit
            # tooling) can trace each merged TC back to its origin TC(s).
            if current_source_ids:
                current_repr["source_case_ids"] = list(current_source_ids)
            merged.append(current_repr)
            current_repr = None
            current_source_ids = []

    for key, _idx, case in decorated:
        # Capture the source id before any merging — survives even when the
        # case dict is later dropped from the input list.
        source_id = (
            str(case.get("case_id") or case.get("tc_id") or "")
            if isinstance(case, Mapping)
            else ""
        )
        if key is None or not isinstance(case, dict):
            _flush()
            # Round 16: singletons still get a one-element source_case_ids
            # so downstream consumers always see a list-shaped value.
            if source_id and isinstance(case, dict):
                case["source_case_ids"] = [source_id]
            merged.append(case)  # type: ignore[arg-type]
            continue
        if key != current_key:
            _flush()
            current_key = key
            current_repr = case
            current_source_ids = [source_id] if source_id else []
            continue
        # Same group → merge into current_repr.
        assert current_repr is not None
        current_repr["steps"] = _merge_steps(
            current_repr.get("steps", []),
            case.get("steps", []),
        )
        current_repr["expected_results"] = _merge_expected(
            current_repr.get("expected_results", []),
            case.get("expected_results", []),
        )
        # Round 16: extend source_case_ids with this case's id. Empty ids are
        # silently skipped (defensive — the input may have cases with no
        # case_id assigned, though normalize_case_id usually fixes that).
        if source_id:
            current_source_ids.append(source_id)
        # Drop the consumed case from the merge output (we mutate the
        # in-memory list; caller is expected to use the returned merged
        # list as the canonical truth).
        # Note: we don't touch the original case dict — it's still in the
        # input list until the caller discards it.

    _flush()
    # Round 15 fix: canonical Chinese list fields may be stale from a prior
    # mirror pass (Round 14 normalizer treats them as authoritative, so the
    # merge grew the English list but the Chinese string stayed single-item).
    # Force-sync after merge so downstream formatter reads the merged list.
    for case in merged:
        if isinstance(case, dict):
            _sync_list_fields_after_merge(case)
    return merged


def merge_grouped_inplace(payload: Any) -> list[dict[str, Any]]:
    """Convenience wrapper: handles dict-wrapped payloads too.

    Returns the merged case list. Mutates the dict-wrapped payload's
    ``test_cases`` array in-place so subsequent ``payload.get("test_cases")``
    reads see the merged view.
    """
    if isinstance(payload, dict):
        cases = payload.get("test_cases")
        if not isinstance(cases, list):
            return []
        merged = merge_grouped(cases)
        payload["test_cases"] = merged
        return merged
    if isinstance(payload, list):
        merged = merge_grouped(payload)
        return merged
    return []


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _build_merge_payload() -> dict[str, Any]:
    """5-case fixture covering the merge / no-merge matrix."""
    return {
        "test_cases": [
            # Group A (same obj+fp+scenario) — 2 cases, merge to 1×2 steps
            {
                "case_id": "UI-TC-001", "module": "UI",
                "obj_id": "OBJ-A", "feature_point_ref": "OBJ-A-FP-1",
                "test_scenario": "用户登录",
                "用例描述": "登录", "功能描述": "登录",
                "preconditions": ["已注册"],
                "steps": [{"step_num": 1, "action": "输入账号"}],
                "expected_results": ["账号栏已填"],
                "priority": "P0",
            },
            {
                "case_id": "UI-TC-002", "module": "UI",
                "obj_id": "OBJ-A", "feature_point_ref": "OBJ-A-FP-1",
                "test_scenario": "用户登录",
                "用例描述": "登录", "功能描述": "登录",
                "preconditions": ["已注册"],
                "steps": [{"step_num": 1, "action": "点击登录"}],
                "expected_results": ["进入首页"],
                "priority": "P0",
            },
            # Group B (same obj+fp+scenario) — 3 cases, merge to 1×3 steps
            {
                "case_id": "BIZ-TC-010", "module": "BIZ",
                "obj_id": "OBJ-B", "feature_point_ref": "OBJ-B-FP-1",
                "test_scenario": "下单流程",
                "用例描述": "下单", "功能描述": "下单",
                "preconditions": ["已登录"],
                "steps": [{"step_num": 1, "action": "选商品"}],
                "expected_results": ["已加购"],
                "priority": "P0",
            },
            {
                "case_id": "BIZ-TC-011", "module": "BIZ",
                "obj_id": "OBJ-B", "feature_point_ref": "OBJ-B-FP-1",
                "test_scenario": "下单流程",
                "用例描述": "下单", "功能描述": "下单",
                "preconditions": ["已登录"],
                "steps": [{"step_num": 1, "action": "提交订单"}],
                "expected_results": ["订单已创建"],
                "priority": "P0",
            },
            {
                "case_id": "BIZ-TC-012", "module": "BIZ",
                "obj_id": "OBJ-B", "feature_point_ref": "OBJ-B-FP-1",
                "test_scenario": "下单流程",
                "用例描述": "下单", "功能描述": "下单",
                "preconditions": ["已登录"],
                "steps": [{"step_num": 1, "action": "支付"}],
                "expected_results": ["支付成功"],
                "priority": "P0",
            },
            # Group C (different obj_id) — must NOT merge
            {
                "case_id": "UI-TC-020", "module": "UI",
                "obj_id": "OBJ-C", "feature_point_ref": "OBJ-C-FP-1",
                "test_scenario": "用户登录",
                "用例描述": "登录C", "功能描述": "登录C",
                "preconditions": [],
                "steps": [{"step_num": 1, "action": "输入账号C"}],
                "expected_results": ["账号栏已填C"],
                "priority": "P1",
            },
            # Group D (different test_scenario) — must NOT merge
            {
                "case_id": "UI-TC-030", "module": "UI",
                "obj_id": "OBJ-A", "feature_point_ref": "OBJ-A-FP-1",
                "test_scenario": "用户登出",
                "用例描述": "登出", "功能描述": "登出",
                "preconditions": ["已登录"],
                "steps": [{"step_num": 1, "action": "点击登出"}],
                "expected_results": ["退出登录"],
                "priority": "P1",
            },
            # Group E (incomplete metadata → singleton, must NOT merge)
            {
                "case_id": "UI-TC-040", "module": "UI",
                # obj_id intentionally missing
                "feature_point_ref": "OBJ-X-FP-1",
                "test_scenario": "未知",
                "用例描述": "兜底", "功能描述": "兜底",
                "preconditions": [],
                "steps": [{"step_num": 1, "action": "兜底操作"}],
                "expected_results": ["兜底结果"],
                "priority": "P2",
            },
        ]
    }


def self_test() -> int:
    """Cover the 5 critical merge paths; return 0 on PASS, 1 on FAIL."""
    payload = _build_merge_payload()
    merged = merge_grouped_inplace(payload)
    assert isinstance(merged, list), type(merged)

    # Group A: 2 cases → 1×2 steps
    group_a = [c for c in merged if c.get("obj_id") == "OBJ-A" and c.get("test_scenario") == "用户登录"]
    assert len(group_a) == 1, f"Group A merge failed: {[c['case_id'] for c in group_a]}"
    assert len(group_a[0]["steps"]) == 2, group_a[0]["steps"]
    assert len(group_a[0]["expected_results"]) == 2, group_a[0]["expected_results"]
    assert group_a[0]["steps"][0]["step_num"] == 1
    assert group_a[0]["steps"][1]["step_num"] == 2

    # Group B: 3 cases → 1×3 steps
    group_b = [c for c in merged if c.get("obj_id") == "OBJ-B"]
    assert len(group_b) == 1, f"Group B merge failed: {[c['case_id'] for c in group_b]}"
    assert len(group_b[0]["steps"]) == 3, group_b[0]["steps"]
    assert len(group_b[0]["expected_results"]) == 3, group_b[0]["expected_results"]

    # Group C: different obj_id → must stay separate
    group_c = [c for c in merged if c.get("obj_id") == "OBJ-C"]
    assert len(group_c) == 1, f"Group C should be singleton: {[c['case_id'] for c in group_c]}"

    # Group D: different scenario → must stay separate
    group_d = [c for c in merged if c.get("test_scenario") == "用户登出"]
    assert len(group_d) == 1, f"Group D should be singleton: {[c['case_id'] for c in group_d]}"

    # Group E: incomplete obj_id → singleton
    group_e = [c for c in merged if c.get("case_id") == "UI-TC-040"]
    assert len(group_e) == 1, "Group E should be singleton (incomplete metadata)"

    # Total: 7 → 5 (Group A 2→1, Group B 3→1, C+D+E singletons = 5)
    assert len(merged) == 5, f"expected 5 merged cases, got {len(merged)}: {[c['case_id'] for c in merged]}"

    # Preserve field check: Group B's 用例描述 / priority survive
    assert group_b[0]["用例描述"] == "下单"
    assert group_b[0]["priority"] == "P0"

    # Round 16 — source_case_ids field exists and contains the right ids.
    # Group A (2→1) → source_case_ids = [UI-TC-001, UI-TC-002]
    assert group_a[0]["source_case_ids"] == ["UI-TC-001", "UI-TC-002"], (
        group_a[0].get("source_case_ids")
    )
    # Group B (3→1) → source_case_ids = [BIZ-TC-010, BIZ-TC-011, BIZ-TC-012]
    assert group_b[0]["source_case_ids"] == [
        "BIZ-TC-010", "BIZ-TC-011", "BIZ-TC-012"
    ], group_b[0].get("source_case_ids")
    # Singletons → source_case_ids = [own_id] (one-element list)
    assert group_c[0]["source_case_ids"] == ["UI-TC-020"], group_c[0].get("source_case_ids")
    assert group_d[0]["source_case_ids"] == ["UI-TC-030"], group_d[0].get("source_case_ids")
    assert group_e[0]["source_case_ids"] == ["UI-TC-040"], group_e[0].get("source_case_ids")
    # Every merged TC must have a list-typed source_case_ids (contract).
    for tc in merged:
        assert isinstance(tc.get("source_case_ids"), list), tc
        assert len(tc["source_case_ids"]) >= 1, tc

    print("scenario_group_merger self-test: PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    raise SystemExit("usage: scenario_group_merger.py --self-test")
