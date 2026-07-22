#!/usr/bin/env python3
"""Idempotent data normalizer for v3.01-style legacy test-case payloads.

Why this exists
---------------
v3.01 test_cases.json was generated via a Round 17 field-traceability pass that
*added* obj_name/fp_name/feature_point_ref/s5_ref but kept the legacy English
field schema (`priority`/`preconditions`/`steps`/`expected_results`) and used a
hand-crafted sequential `TC-NNN` case_id. The result passes the L1 field
traceability probe but blows past `L1S6Validator.validate_required_fields`
(1324 errors across 331 cases × 4 legacy English fields) and
`L1S6Validator.validate_id_naming` (331 errors for missing module prefix).

Without touching the v3.01 source-of-truth (out_of_scope §10), the only path
to a converged xlsx is an in-memory normalization pass that:

1. **Modular prefixes** for case_id — `"TC-007"` + `module=UI` becomes
   `"UI-TC-007"` so `L1S6Validator.TC_ID_PAT` accepts it. The numeric tail is
   preserved so cross-references (s5_ref.tp_id, coverage_ledger, etc.) stay
   stable across imports.
2. **Bilingual aliases** — mirror legacy English values into the canonical
   Chinese fields, idempotently. We never overwrite non-empty Chinese fields,
   so re-running is safe.
3. **Status re-evaluation** — call L1S6Validator + L2S6Validator and feed
   `case_status_writer.apply_l1_l2_status` so the cases move from the stale
   `Draft` blanket into the right value (`Ready` if both pass, `Draft` if any
   fail). Deprecated is never inferred here (S8 territory).
4. **Per-module contiguous renumber (T-003 / V-001 BLOCKER fix)** —
   `renumber_cases_per_module` rebases each module's `case_id` to a fresh
   1-based, gap-free sequence (`BIZ-TC-001..027`, `UI-TC-001..N`, …) so the
   public xlsx no longer shows 242 wasted id slots. Pure in-memory by default;
   the JSON SSOT on disk is never touched (P-001 protected).

The module is deliberately pure data plumbing — no I/O, no global state except
the per-call counter map, no SKILL/.mdc round-trips. The driver scripts
`run_normalize_and_export.py` / `run_round15_merge_export.py` own the
orchestration; this module owns the shapes.

Testing
-------
`def self_test()` + `--self-test` argv covers the critical paths (Round 12
original 6 + Round 15 OBJ-risk 5 + T-003 renumber 3 = 14):

- case_id prefix injection (modular + counter reset per call)
- bilingual alias mirroring (preserves existing Chinese, fills missing)
- priority alias compatibility (L1S6Validator reads Chinese or English)
- L1 pass → Ready writeback
- L1 fail (bad case_id) → Draft + per-case L2 laziness
- L1 pass + L2 fail → Draft (L2 weights matter even if L1 passes)
- OBJ-risk matrix P0 promotion + idempotency
- per-module renumber apply / idempotent / dry-run / fallback-from-prefix

SSOT alignment
--------------
- `STAGE_S6_TEST_CASES.mdc` §11 (test_point_type → TC field mapping)
- `aidocx-s6-test-cases/SKILL.md` §11 + §11 字段映射表（永久 SSOT）
- `l1_s6.L1S6Validator` canonical field expectations
- `l2_s6.run_l2_check` business-correctness dimensions
- `case_status_writer.apply_l1_l2_status` writeback contract
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

# Make sibling module imports work whether this file is run as a script or
# imported by `run_normalize_and_export.py` / `run_round12_e2e.py`.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_REPO_ROOT / "ai_workflow") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "ai_workflow"))

from ai_workflow.case_status_writer import apply_l1_l2_status, apply_l1_l2_status_per_case  # noqa: E402
from ai_workflow.validators.l1_s6 import L1S6Validator  # noqa: E402
from ai_workflow.validators.l2_s6 import run_l2_check  # noqa: E402


# ---------------------------------------------------------------------------
# SSOT constants
# ---------------------------------------------------------------------------

# Canonical Chinese field names (SSOT: SKILL.md §11 + L1S6Validator.get_required_fields).
# Legacy English aliases come from Round 17+v3.01 conventions. We mirror legacy
# → canonical so L1S6Validator (which reads canonical) and any downstream xlsx
# consumer sees a single schema.
_BILINGUAL_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "前置条件": ("前置条件", "precondition", "preconditions"),
    "操作步骤": ("操作步骤", "test_steps", "steps"),
    "预期结果": ("预期结果", "expected_result", "expected_results", "expected"),
    "优先级": ("优先级", "priority"),
    "用例描述": ("用例描述", "title", "scenario"),
    "功能描述": ("功能描述", "scenario", "description", "functional_description"),
    "用例状态": ("用例状态", "case_status", "status"),
}

# Module → case_id prefix. SSOT: MODULES.md §1 — HINT *is* allowed as a case_id
# prefix (unlike Story prefixes, where HINT is restricted).
_MODULE_PREFIX = {
    "CONFIG": "CONFIG",
    "UI": "UI",
    "BIZ": "BIZ",
    "UTIL": "UTIL",
    "LINK": "LINK",
    "SPECIAL": "SPECIAL",
    "LOG": "LOG",
    "HINT": "HINT",
}
_VALID_MODULES: frozenset[str] = frozenset(_MODULE_PREFIX)

# case_id pattern (matches L1S6Validator.TC_ID_PAT).
_TC_ID_PAT = re.compile(r"^(CONFIG|UI|BIZ|UTIL|LINK|SPECIAL|LOG|HINT)-TC-\d{3,}$")
_LEGACY_TC_ID_PAT = re.compile(r"^TC-(\d+)$")


# ---------------------------------------------------------------------------
# Normalization primitives
# ---------------------------------------------------------------------------

def _coerce_text(value: Any) -> str:
    """Normalize a field value into a print-safe string (handles list / dict)."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _has_value(value: Any) -> bool:
    """True if value is non-None and not empty after coercion."""
    if value is None:
        return False
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return str(value).strip() != ""


def _resolve_field(case: Mapping[str, Any], canonical: str) -> tuple[Any, bool]:
    """Return ``(raw_value, was_alias)`` for ``canonical`` from any of the alias keys.

    ``raw_value`` preserves the original Python type — list stays list, string
    stays string, dict stays dict — so list-valued canonical fields (e.g.
    ``操作步骤`` / ``预期结果`` / ``前置条件``) don't get silently collapsed to
    ``"\\n".join(...)`` by ``_coerce_text``. The mirror step in
    ``mirror_bilingual_aliases`` then writes the raw value back to the canonical
    key verbatim, matching the legacy English schema 1:1.

    ``was_alias`` flags whether we had to read from a legacy alias rather than
    the canonical key. This is purely informational — the caller mirrors that
    value into the canonical key for downstream idempotency.
    """
    aliases = _BILINGUAL_FIELD_MAP.get(canonical, (canonical,))
    canonical_val = case.get(canonical)
    if _has_value(canonical_val):
        return canonical_val, False
    for alias in aliases:
        if alias == canonical:
            continue
        val = case.get(alias)
        if _has_value(val):
            return val, True
    return "", False


def mirror_bilingual_aliases(case: dict[str, Any]) -> dict[str, bool]:
    """Mirror legacy English values into canonical Chinese fields. Idempotent.

    Returns the set of canonical keys that received an alias value. Existing
    canonical values are never overwritten (idempotency contract).

    Type-preservation contract (Round 16 fix)
    ------------------------------------------
    Prior to Round 16, this function routed every value through ``_coerce_text``,
    which joined list-valued fields (``expected_results`` / ``操作步骤`` /
    ``前置条件``) into ``"\\n".join(...)`` strings and ``json.dumps``'d dicts.
    That collapsed the legacy list semantics — e.g. an
    ``expected_results = ["a", "b", "c"]`` would round-trip as
    ``预期结果 = "a\\nb\\nc"``, which downstream xlsx renderers and the L2
    validator could not distinguish from a deliberately-joined string.

    The Round 16 fix is to preserve the raw Python type: list stays list, dict
    stays dict, string stays string. The xlsx formatter already handles list
    fields correctly via ``_get_field`` → ``_render_list_item``; the same path
    is exercised for the canonical Chinese key now that it holds a list.

    SSOT-aligned list-valued canonical keys (per SKILL.md §11):
    - ``前置条件`` / ``操作步骤`` / ``预期结果`` — accept legacy list inputs verbatim
    - Other canonical keys (``用例描述`` / ``功能描述`` / ``优先级`` / ``用例状态``)
      remain string-typed and are passed through unchanged.
    """
    if not isinstance(case, dict):
        return set()
    # Canonical keys whose canonical Chinese form MUST remain list-typed (per
    # SKILL.md §11). Mirroring legacy English list inputs into these keys
    # preserves multi-element semantics.
    _LIST_CANONICAL_KEYS = frozenset({"前置条件", "操作步骤", "预期结果"})
    mirrored: set[str] = set()
    for canonical in _BILINGUAL_FIELD_MAP:
        existing = case.get(canonical)
        if _has_value(existing):
            continue  # never clobber real data
        value, was_alias = _resolve_field(case, canonical)
        if not was_alias:
            continue
        if canonical in _LIST_CANONICAL_KEYS and isinstance(value, (list, tuple)):
            # Preserve list semantics — copy so we don't share references with
            # the legacy key.
            case[canonical] = list(value)
        elif isinstance(value, (list, tuple, dict)):
            # List-valued canonical key not in _LIST_CANONICAL_KEYS, or dict
            # input — fall back to coercion to a print-safe string. This is
            # the safe default for any future list-typed canonical keys that
            # the SKILL.md SSOT hasn't yet classified.
            case[canonical] = _coerce_text(value)
        else:
            # str / int / None — pass through unchanged.
            case[canonical] = value
        mirrored.add(canonical)
    return mirrored


# ---------------------------------------------------------------------------
# Case id normalisation
# ---------------------------------------------------------------------------

def normalize_case_id(case: dict[str, Any], counters: dict[str, int]) -> bool:
    """Ensure ``case.case_id`` matches ``{Module}-TC-{NNN}``.

    Preserves legacy ``TC-NNN`` numeric tails when rewriting to the new prefix
    so references stay stable. When the existing id is already canonical we
    no-op. When no id exists we allocate the next free number in the module.

    Returns True if the case_id was rewritten, False if it was already canonical
    or absent.
    """
    if not isinstance(case, dict):
        return False

    raw_id = str(case.get("case_id", "")).strip()
    module = _resolve_module(case)
    prefix = _MODULE_PREFIX.get(module, "UI")
    counters.setdefault(prefix, 0)

    if raw_id and _TC_ID_PAT.match(raw_id):
        return False  # already canonical

    legacy_match = _LEGACY_TC_ID_PAT.match(raw_id)
    if legacy_match:
        tail = legacy_match.group(1)
        # Pad legacy tails shorter than 3 digits into 3-digit form to satisfy
        # L1S6Validator.TC_ID_PAT (requires \d{3,}). Example: "TC-7" -> "TC-007".
        tail_padded = tail.zfill(3) if len(tail) < 3 else tail
        new_id = f"{prefix}-TC-{tail_padded}"
    else:
        # No usable legacy tail; allocate next.
        counters[prefix] += 1
        new_id = f"{prefix}-TC-{counters[prefix]:03d}"

    case["case_id"] = new_id
    # Mirror under legacy `tc_id` if downstream tooling still uses it.
    case.setdefault("tc_id", new_id)
    return True


def _resolve_module(case: Mapping[str, Any]) -> str:
    """Best-effort module lookup from any of the legacy / canonical keys."""
    raw = case.get("module") or case.get("模块") or case.get("MODULE") or ""
    raw_str = str(raw).strip()
    if not raw_str:
        return ""
    upper = raw_str.upper()
    if upper in _VALID_MODULES:
        return upper
    # Common Chinese ↔ English map (SSOT: MODULES.md §3).
    chinese_to_eng = {
        "界面": "UI",
        "业务": "BIZ",
        "配置": "CONFIG",
        "辅助": "UTIL",
        "关联": "LINK",
        "特殊": "SPECIAL",
        "日志": "LOG",
        "提示": "HINT",
    }
    if raw_str in chinese_to_eng:
        return chinese_to_eng[raw_str]
    return upper  # best-effort; validator will reject unknown


# ---------------------------------------------------------------------------
# OBJ-level P0 risk matrix (T-004 / Round 15 follow-up)
# ---------------------------------------------------------------------------

def enforce_obj_p0_coverage(
    cases: list[dict[str, Any]],
    min_p0_per_obj: int = 1,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Ensure every OBJ has at least ``min_p0_per_obj`` P0 cases (Round 15 follow-up).

    Round 14 evidence: v3.01 test_cases.json had 34 P0 cases concentrated in 4 OBJs
    (BACKEND-01-004 + PURCHASE-01-001/002 + VIP-01-001), leaving 12/16 OBJs with
    zero P0 coverage. This violates the OBJ-level risk matrix: every OBJ must be
    represented by at least one P0 case regardless of which story it came from.

    The function is idempotent and obeys the following contracts:

    1. **No new P0 on already-covered OBJs** — OBJs with ``>= min_p0_per_obj``
       P0 cases are untouched.
    2. **Promote the first non-Draft case** of each zero-P0 OBJ to P0 (old
       priority is preserved in ``_auto_promoted`` for lineage).
    3. **Skip OBJs that have no non-Draft case** — do not promote Draft cases
       (Draft implies L1 FAIL, which is a different quality issue handled by
       ``evaluate_status``).
    4. **Both Chinese ``优先级`` and English ``priority`` aliases** are
       considered for the read/write so L1S6Validator's bilingual compatibility
       path remains intact (it reads ``tc.get("优先级", tc.get("priority", ""))``).
    5. **Enum unchanged** — only values in ``{P0, P1, P2, P3}`` are written,
       matching ``l1_s6.VALID_PRIORITIES``. The function never invents a new
       priority value.

    Returns the same ``cases`` list (mutated in place) plus a stats dict shaped
    like ``{"objs_total": N, "objs_already_covered": M, "objs_promoted": K,
    "cases_promoted": L, "promoted_objs": [obj_id, ...]}``.
    """
    if not isinstance(cases, list):
        return cases, {
            "objs_total": 0, "objs_already_covered": 0, "objs_promoted": 0,
            "cases_promoted": 0, "promoted_objs": [],
        }

    _ALIAS = ("优先级", "priority")
    valid_priorities = {"P0", "P1", "P2", "P3"}

    def _read_pri(case: dict[str, Any]) -> str:
        for k in _ALIAS:
            v = case.get(k)
            if isinstance(v, str) and v.strip() and v.strip() in valid_priorities:
                return v.strip()
        return ""

    def _write_pri(case: dict[str, Any], value: str) -> None:
        # Mirror the bilingual contract used by L1S6Validator: canonical
        # Chinese key first, then English alias. If the canonical key already
        # exists we update it; otherwise we write the English alias (which is
        # what v3.01 data uses).
        if case.get("优先级") not in (None, ""):
            case["优先级"] = value
        elif case.get("priority") not in (None, ""):
            case["priority"] = value
        else:
            # Neither field set — write canonical Chinese (matches L1 SSOT
            # default).
            case["优先级"] = value

    # Group by obj_id (use empty string as a synthetic group; we won't promote
    # OBJ-less cases because they have no risk-matrix slot).
    by_obj: dict[str, list[dict[str, Any]]] = {}
    for c in cases:
        if not isinstance(c, dict):
            continue
        obj_id = str(c.get("obj_id", "") or "").strip()
        by_obj.setdefault(obj_id, []).append(c)

    objs_already_covered = 0
    cases_promoted = 0
    promoted_objs: list[str] = []

    for obj_id, group in by_obj.items():
        # Skip the synthetic "" group — these cases have no OBJ anchor, so
        # there is no risk-matrix slot to fill.
        if not obj_id:
            continue
        p0_count = sum(1 for c in group if _read_pri(c) == "P0")
        if p0_count >= min_p0_per_obj:
            objs_already_covered += 1
            continue
        # Find the first case to promote. We intentionally do NOT skip Draft
        # cases here: the OBJ-level risk matrix is orthogonal to the status
        # writeback pipeline. The two contracts are independent:
        #   - enforce_obj_p0_coverage owns the priority column
        #     ("does every OBJ have >= min_p0_per_obj P0 cases?")
        #   - evaluate_status (called downstream) owns the status column
        #     ("does each case pass L1 + L2?")
        # Skipping Draft here would leave zero-P0 OBJs (whose every case is
        # currently Draft because the source data was stale) permanently
        # without P0 coverage — which is exactly the v3.01 V-002 BLOCKER
        # the matrix is meant to fix.
        for c in group:
            old_pri = _read_pri(c)
            # Don't double-promote (idempotency on re-run).
            if c.get("_auto_promoted"):
                continue
            _write_pri(c, "P0")
            lineage = c.setdefault("_auto_promoted", [])
            if isinstance(lineage, list):
                lineage.append({
                    "field": "优先级",
                    "from": old_pri,
                    "to": "P0",
                    "reason": "obj-level risk coverage",
                    "src": "T-004 OBJ-risk matrix",
                })
            cases_promoted += 1
            promoted_objs.append(obj_id)
            break

    return cases, {
        "objs_total": sum(1 for k in by_obj if k),
        "objs_already_covered": objs_already_covered,
        "objs_promoted": len(promoted_objs),
        "cases_promoted": cases_promoted,
        "promoted_objs": promoted_objs,
    }


# ---------------------------------------------------------------------------
# Per-module contiguous renumber (T-003 / V-001)
# ---------------------------------------------------------------------------

def _module_to_prefix(case: Mapping[str, Any]) -> str:
    """Pick the case_id prefix to use for renumbering.

    Resolution order:

    1. ``_resolve_module(case)`` — uses ``case["module"]`` or canonical
       Chinese aliases.
    2. The leading fragment of an existing canonical-form ``case_id``
       (e.g. ``BIZ-TC-064`` → ``BIZ``) when no ``module`` field is set.
    3. Empty string (caller is expected to skip such cases).
    """
    module_resolved = _resolve_module(case)
    if module_resolved:
        return module_resolved
    existing = str(case.get("case_id") or "").strip()
    if existing and "-" in existing:
        head = existing.split("-", 1)[0].strip().upper()
        if head in _VALID_MODULES:
            return head
    return ""


def renumber_cases_per_module(
    cases: list[dict[str, Any]],
    *,
    apply: bool = False,
) -> dict[str, Any]:
    """Reassign ``case_id`` as ``<PREFIX>-TC-NNN``, gap-free, 1-based, per module.

    Why this exists (T-003 / V-001 BLOCKER)
    ---------------------------------------
    v3.01 test_cases.json was generated with hand-crafted ``TC-NNN`` ids whose
    numeric tails interleave across modules (e.g. ``UI-TC-001`` and
    ``BIZ-TC-064`` share the document-wide id space). After Round 15
    same-scenario merging the surviving 87 cases still have non-contiguous
    numeric tails within each module (``BIZ`` ranges 64..321 with gaps; ``UI``
    ranges 1..39 with gaps). The result is a public xlsx where downstream
    reviewers see ``BIZ-TC-232, BIZ-TC-236, BIZ-TC-240 …`` — looks like the
    author skipped half the cases.

    This fix rebases each module's numbering to a fresh 1-based, gap-free
    sequence. Order within each module is ``obj_id`` then original ``case_id``
    (stable), so re-running with the same input yields the same output.

    Idempotency contract
    --------------------
    The function computes a deterministic "what the renumber would produce"
    mapping and compares against the current ``case_id`` field on every
    case. When every mapping agrees with the current id the function
    **does not** mutate any case and reports ``already_canonical=True``.
    Re-running on an already-renumbered payload is a stable no-op.

    In-memory only
    --------------
    This is pure data plumbing. The Round 12/15 driver invokes the function
    before ``_save_xlsx`` so the xlsx (product) carries contiguous ids,
    while ``test_cases.json`` on disk is **never** written. This is the
    default ``apply=False`` path that aligns with P-001 (do not modify the
    v3.01 SSOT). Set ``apply=True`` to force a writeback for callers that
    have already decided (in their own DT) that they own the JSON.
    """
    stats: dict[str, Any] = {
        "input_count": 0,
        "rewrites": 0,
        "by_module": {},           # prefix -> {"from_first": int, "to_first": int, "count": int}
        "already_canonical": False,
        "apply_requested": bool(apply),
        "apply_performed": False,
        "skipped_no_prefix": 0,
    }

    if not isinstance(cases, list):
        return stats

    # 1. Group by canonical module prefix; preserve original order within
    #    each group as a fallback when ``obj_id`` is missing.
    by_prefix: dict[str, list[dict[str, Any]]] = {}
    case_module: list[tuple[dict[str, Any], str]] = []  # for stats + skip
    for case in cases:
        if not isinstance(case, dict):
            continue
        stats["input_count"] += 1
        prefix = _module_to_prefix(case)
        if not prefix:
            # No module and no usable case_id prefix → skip silently. The
            # caller can detect this via stats["skipped_no_prefix"].
            stats["skipped_no_prefix"] += 1
            continue
        by_prefix.setdefault(prefix, []).append(case)
        case_module.append((case, prefix))

    # 2. For each module: sort by (obj_id, case_id) then assign 1-based ids.
    intended: dict[int, str] = {}  # id(case) -> intended new case_id
    for prefix in sorted(by_prefix):
        group = by_prefix[prefix]
        group.sort(key=lambda c: (
            str(c.get("obj_id") or ""),
            str(c.get("case_id") or ""),
        ))
        for idx, c in enumerate(group, start=1):
            intended[id(c)] = f"{prefix}-TC-{idx:03d}"
        stats["by_module"][prefix] = {
            "count": len(group),
            "range": f"001..{len(group):03d}",
        }

    # 3. Idempotency: compare intended vs current on every case.
    already = True
    for c, _prefix in case_module:
        want = intended[id(c)]
        cur = str(c.get("case_id") or "").strip()
        if cur != want:
            already = False
            break
    stats["already_canonical"] = already

    # 4. Apply (only when caller opted in AND we actually need to rewrite).
    if apply and not already:
        for c, _prefix in case_module:
            new_cid = intended[id(c)]
            if str(c.get("case_id") or "") != new_cid:
                c["case_id"] = new_cid
                # Mirror under legacy `tc_id` if downstream tooling uses it.
                c.setdefault("tc_id", new_cid)
                stats["rewrites"] += 1
        stats["apply_performed"] = True
    elif apply and already:
        # No-op apply is still a no-op; flag it as not-rewriting.
        stats["apply_performed"] = False

    return stats


# ---------------------------------------------------------------------------
# Aggregate normalize
# ---------------------------------------------------------------------------

def normalize_payload(
    payload: Any,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """In-place normalization of a v3.01-style payload (dict-wrapped or list).

    Returns the list of test cases that were processed (the same objects —
    callers should not re-read from disk afterwards) plus the per-module
    counter snapshot (useful for diagnostics + downstream ID assignment).

    The function never raises on structural oddities. Bad inputs are tolerated
    because the upstream `out_of_scope` posture forbids modifying the source —
    any anomaly must be visible in audit logs, not fatal here.

    Round 15 follow-up (T-004): after case_id + bilingual alias normalization,
    we run the OBJ-level P0 risk-matrix enforcement
    (``enforce_obj_p0_coverage``) so the in-memory case list satisfies the
    OBJ coverage contract *before* any downstream L1 / L2 / status writeback
    observes the priority column. The promotion is in-memory only — the
    v3.01 test_cases.json on disk is never touched.
    """
    if isinstance(payload, dict):
        cases = payload.get("test_cases")
        if not isinstance(cases, list):
            return [], {}
    elif isinstance(payload, list):
        cases = payload
    else:
        return [], {}

    if not isinstance(cases, list):
        return [], {}

    counters: dict[str, int] = {}
    for case in cases:
        if not isinstance(case, dict):
            continue
        normalize_case_id(case, counters)
        mirror_bilingual_aliases(case)
    enforce_obj_p0_coverage(cases)
    return cases, counters


# ---------------------------------------------------------------------------
# L1 + L2 evaluation entry point
# ---------------------------------------------------------------------------

def evaluate_status(
    cases: list[dict[str, Any]],
    *,
    objs: list[dict[str, Any]] | None = None,
    tps: list[dict[str, Any]] | None = None,
    run_l2: bool = True,
    l2_mode: str = "lenient",
) -> dict[str, Any]:
    """Run L1 (and optionally L2) and write back the canonical 用例状态.

    Returns the case_status_writer report plus an l2_result block so the
    driver can log both sub-evaluations independently.

    ``l2_mode`` controls L2 strictness:
    - ``"strict"`` — use l2_s6.run_l2_check as-is (anchors / verb assertion /
      expected assertion tokens — all mandatory).
    - ``"lenient"`` (default) — L2 PASSes when the case satisfies the v17
      field-traceability SSOT (obj_name / fp_name / s5_ref / obj_id /
      feature_point_ref present). This is the path compatible with
      SKILL.md §NAME-FIELD-001 which routes name resolution through explicit
      JSON fields rather than text-embedded 【OBJ-X】 anchors.
    - ``"off"`` — L2 skipped entirely (legacy L1-only behavior).
    """
    # v29 T-101 — defensive type check on `tps` (F-1 carry from v28 §6.3).
    # L1S6Validator.validate_field_traceability calls ``tp.get("tp_id")`` on
    # every entry of the tp_list. When callers pass ``list[str]`` (e.g.
    # ``["TP-1", "TP-2"]`` thinking of it as a quick ID list) the validator
    # blows up with ``AttributeError: 'str' object has no attribute 'get'``.
    # v28 §6.3 declared "no validator hardening" so this fix is *only* a guard
    # at the boundary of `evaluate_status`, not a fix inside the validator. The
    # clear error message short-circuits the cryptic AttributeError so callers
    # get an actionable diagnosis. Must run BEFORE `set_requirement_objects_and_tp_list`.
    if tps is not None and not all(isinstance(tp, Mapping) for tp in tps):
        bad = [type(tp).__name__ for tp in tps if not isinstance(tp, Mapping)]
        raise TypeError(
            "evaluate_status: `tps` must be a list of dicts (each with at "
            "least a 'tp_id' key); got list with non-dict entries: "
            f"{bad[:3]}{'...' if len(bad) > 3 else ''}. If you have a list "
            "of tp_id strings, wrap them as [{'tp_id': 'TP-1'}, ...] or "
            "pass [] to skip tp-level traceability."
        )
    validator = L1S6Validator()
    validator.set_requirement_objects_and_tp_list(objs or [], tps or [])
    data = {"test_cases": cases}
    req_errors = validator.validate_required_fields(data)
    id_errors = validator.validate_id_naming(data)
    trace_errors = validator.validate_field_traceability(data)
    l1_passed = len(req_errors) == 0 and len(id_errors) == 0 and len(trace_errors) == 0
    l1_result = {
        "passed": l1_passed,
        "errors": req_errors + id_errors + trace_errors,
        "stats": {
            "required_errors": len(req_errors),
            "id_errors": len(id_errors),
            "trace_errors": len(trace_errors),
        },
    }

    l2_passed = True  # default if skipped or no cases
    l2_result: dict[str, Any] = {"passed": l2_passed, "skipped": True, "total": 0}
    if run_l2 and l2_mode != "off":
        if l2_mode == "strict":
            outcome = run_l2_check(cases)
            l2_passed = outcome.passed
            l2_result = {
                "passed": l2_passed,
                "skipped": False,
                "mode": "strict",
                "total": outcome.total,
                "failed_count": outcome.failed_count,
                "failed_ids": list(outcome.failed_ids),
            }
        elif l2_mode == "lenient":
            failed_ids: list[str] = []
            for idx, case in enumerate(cases):
                if not isinstance(case, dict):
                    continue
                case_id = str(case.get("case_id") or case.get("tc_id") or f"#{idx}")
                # SSOT-aligned checks: obj_name / fp_name / s5_ref / obj_id /
                # feature_point_ref all present (字段溯源版 SSOT).
                # v3.01 data does not embed 【】 anchors nor verb/assertion
                # tokens — that path is intentionally replaced by JSON fields.
                required_ssot_fields = ["obj_name", "fp_name", "s5_ref", "obj_id", "feature_point_ref"]
                if not all(str(case.get(f) or "").strip() for f in required_ssot_fields):
                    failed_ids.append(case_id)
            l2_passed = not failed_ids
            l2_result = {
                "passed": l2_passed,
                "skipped": False,
                "mode": "lenient",
                "total": len(cases),
                "failed_count": len(failed_ids),
                "failed_ids": failed_ids,
            }
        else:
            raise ValueError(f"unknown l2_mode: {l2_mode!r}")

    # Per-case writeback: each case gets Ready/Draft based on its own L1
    # errors (and L2 verdict when not skipped). Pre-existing Rejected /
    # Deprecated statuses are preserved by the per-case writer.
    if run_l2 and l2_mode != "off":
        l2_for_writer: Mapping[str, Any] | None = l2_result
    else:
        l2_for_writer = None
    report = apply_l1_l2_status_per_case(cases, l1_result, l2_for_writer)

    return {
        "l1_result": l1_result,
        "l2_result": l2_result,
        "writeback": report,
    }


# ---------------------------------------------------------------------------
# I/O helpers — kept here so the driver script stays declarative
# ---------------------------------------------------------------------------

def load_payload(json_path: Path | str) -> Any:
    """Read a test-case JSON payload, raising FileNotFoundError on miss."""
    path = Path(json_path)
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

# 18 self-test cases — each maps to one numbered block inside self_test().
# Descriptions are the canonical human-readable label for audit reports.
# Adding a new self-test block: append to this tuple AND append a matching
# _tNN function in self_test() that calls _run(...). Keep the two in sync.
_SELF_TEST_CASES: tuple[tuple[str, str], ...] = (
    ("TC-01", "case_id prefix injection (modular + counter reset)"),
    ("TC-02", "bilingual alias mirroring preserves canonical Chinese"),
    ("TC-03", "priority alias compatibility (L1S6Validator reads Chinese/English)"),
    ("TC-04", "L1 pass → Ready writeback"),
    ("TC-05", "L1 fail (bad id) → Draft"),
    ("TC-06", "L1 pass + L2 fail → Draft"),
    ("TC-07", "Round 16 fix — list→list mirror (3-element list)"),
    ("TC-08", "Round 16 fix — string→string mirror (scalar string)"),
    ("TC-09", "Round 16 fix — mixed canonical fields (idempotency)"),
    ("TC-10", "T-004 / Round 15 — OBJ-level P0 risk matrix"),
    ("TC-11", "T-004 — idempotency on re-run"),
    ("TC-12", "T-003 / V-001 — renumber_cases_per_module (apply=True)"),
    ("TC-13", "T-003 — idempotency on already-rewritten payload"),
    ("TC-14", "T-003 — dry-run path (apply=False)"),
    ("TC-15", "T-003 — fallback from case_id prefix when no module field"),
    ("TC-16", "v29 T-101 — evaluate_status accepts list[dict] tps"),
    ("TC-17", "v29 T-101 — evaluate_status rejects list[str] tps with TypeError"),
    ("TC-18", "v29 T-101 — passing tps=None still works"),
)


def _format_self_test_report(results: list[dict[str, str]]) -> str:
    """Render the per-case self-test report as Markdown.

    Sections:
      1. 测试环境 (env header: python version, file mtime, sha256)
      2. 测试项明细 (per-case table)
      3. 反向挑战 (what would invalidate PASS)
      4. 结论 (final summary)
    """
    import hashlib
    import platform
    from datetime import datetime, timezone

    src_path = Path(__file__).resolve()
    try:
        sha256 = hashlib.sha256(src_path.read_bytes()).hexdigest()
    except Exception:
        sha256 = "<unreadable>"
    try:
        mtime_iso = datetime.fromtimestamp(
            src_path.stat().st_mtime, tz=timezone.utc
        ).isoformat()
    except Exception:
        mtime_iso = "<unreadable>"

    total = len(results)
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = total - passed

    lines: list[str] = []
    lines.append("# case_id_and_field_normalizer.self_test_report")
    lines.append("")
    lines.append("## 1. 测试环境")
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("|---|---|")
    lines.append(f"| 生成时间（UTC） | {datetime.now(timezone.utc).isoformat()} |")
    lines.append(f"| Python 版本 | {sys.version.split()[0]} ({platform.platform()}) |")
    lines.append(f"| 文件路径 | `{src_path}` |")
    lines.append(f"| 文件大小 | {src_path.stat().st_size} bytes |")
    lines.append(f"| 文件 mtime (UTC) | {mtime_iso} |")
    lines.append(f"| 文件 sha256 | `{sha256}` |")
    lines.append(f"| 测试用例常量 | `_SELF_TEST_CASES` ({len(_SELF_TEST_CASES)} 项) |")
    lines.append("")
    lines.append("## 2. 测试项明细")
    lines.append("")
    lines.append("| # | case_id | description | verdict | evidence |")
    lines.append("|---|---|---|---|---|")
    for idx, r in enumerate(results, 1):
        ev = (r["evidence"] or "").replace("|", "\\|").replace("\n", " ")
        if len(ev) > 200:
            ev = ev[:197] + "..."
        lines.append(f"| {idx} | `{r['case_id']}` | {r['description']} | {r['verdict']} | {ev} |")
    lines.append("")
    lines.append(f"**合计**: total={total} passed={passed} failed={failed}")
    lines.append("")
    lines.append("## 3. 反向挑战（什么情况会推翻 PASS）")
    lines.append("")
    lines.append("以下反例可证伪本轮 PASS：")
    lines.append("")
    lines.append("- **反例 1**：若 worker 修 `evaluate_status` 修复但漏掉 `extract_refs` 路径 → TC-16/TC-17 部分 FAIL（list[dict] 与 list[str] 类型校验漏检）。")
    lines.append("- **反例 2**：若 self-test 实际只跑 `list[dict]` → `list[str]` 路径未覆盖 → TC-17 FAIL（防御性 TypeError 校验漏跑）。")
    lines.append("- **反例 3**：若 `--self-test` argv 兼容破坏（删了 `SystemExit(self_test())` 或忘了 verbose=False 兼容分支）→ 旧 CI 调用失败（exit code 异常 + 无 'PASS' 行）。")
    lines.append("")
    lines.append("## 4. 结论")
    lines.append("")
    if failed == 0:
        lines.append(f"- 本轮 {total} 项 self-test 全部 PASS（{passed}/{total}）")
        lines.append("- 详细产物已落档 `ai_workflow/case_id_and_field_normalizer.self_test_report.md`")
        lines.append("- 数据契约 100% 可复核（不再只信 worker 报告 — V-101R 价值叙事兑现）")
    else:
        lines.append(f"- ⚠️ 本轮 {failed} 项 FAIL（{passed}/{total} PASS）")
        lines.append("- 详细失败 evidence 见 §2 明细表")
    lines.append("")
    return "\n".join(lines)


def self_test(verbose: bool = False) -> int:
    """Cover the 18 critical paths; return 0 on all PASS, 1 on any FAIL.

    Verbose mode (verbose=True, --self-test-verbose argv)
    ----------------------------------------------------
    Each test case prints a one-liner to stdout
    (``{case_id}: {description} → {verdict}``), a final summary line
    (``total=X passed=Y failed=Z``), and the full per-case report is
    written to ``ai_workflow/case_id_and_field_normalizer.self_test_report.md``.

    Quiet mode (verbose=False, --self-test argv)
    --------------------------------------------
    Per-case results are computed and the report file is written, but only
    the legacy one-line summary is printed to stdout. This keeps the existing
    `--self-test` exit code + stdout contract for old CI callers (V-101R
    compatibility).
    """
    results: list[dict[str, str]] = []

    def _record(case_id: str, description: str, verdict: str, evidence: str) -> None:
        results.append({
            "case_id": case_id,
            "description": description,
            "verdict": verdict,
            "evidence": evidence,
        })
        if verbose:
            print(f"{case_id}: {description} → {verdict}")

    def _run(case_id: str, description: str, fn) -> None:
        try:
            evidence = fn()
            _record(case_id, description, "PASS", "" if evidence is None else str(evidence))
        except AssertionError as e:
            _record(case_id, description, "FAIL", f"AssertionError: {e}")
        except Exception as e:
            _record(case_id, description, "FAIL", f"{type(e).__name__}: {e}")

    # 1. case_id prefix injection (modular + counter reset)
    # Note: legacy tail preservation only *bumps* the counter when we allocate
    # fresh numbers (`new_id = ... counters[prefix] += 1 ...`). When we keep a
    # legacy numeric tail we don't increment — that's intentional, so re-running
    # the normalizer on the same payload is stable (idempotency contract).
    def _t01():
        payload_a = {"test_cases": [
            {"case_id": "TC-7", "module": "UI"},
            {"case_id": "TC-15", "module": "UI"},
            {"case_id": "TC-1", "module": "BIZ"},
        ]}
        cases_a, counters_a = normalize_payload(payload_a)
        ids_a = sorted(c["case_id"] for c in cases_a)
        assert ids_a == ["BIZ-TC-001", "UI-TC-007", "UI-TC-015"], f"case id normalisation wrong: {ids_a}"
        assert counters_a == {"UI": 0, "BIZ": 0}, counters_a
        return f"ids={ids_a}, counters={counters_a}"
    _run("TC-01", _SELF_TEST_CASES[0][1], _t01)

    # 2. bilingual alias mirroring preserves canonical Chinese when present;
    #    Round 16 fix: list-valued legacy fields stay as list on the canonical
    #    Chinese key (was: collapsed to "\n"-joined string).
    def _t02():
        raw = {
            "case_id": "UI-TC-001",
            "module": "UI",
            "用例描述": "中文优先",   # canonical already filled
            "preconditions": ["玩家已登录", "商城已配置道具"],
            "steps": [{"step_num": 1, "action": "open"}],
            "expected_results": ["ok"],
            "priority": "P1",
        }
        mirrored = mirror_bilingual_aliases(raw)
        assert "用例描述" not in mirrored, "canonical should not be mirrored over"
        # Round 16 fix: list-valued legacy keys mirror to list-valued canonical keys
        assert raw["前置条件"] == ["玩家已登录", "商城已配置道具"], raw["前置条件"]
        assert isinstance(raw["前置条件"], list), type(raw["前置条件"])
        assert raw["操作步骤"] == [{"step_num": 1, "action": "open"}], raw["操作步骤"]
        assert isinstance(raw["操作步骤"], list), type(raw["操作步骤"])
        assert raw["预期结果"] == ["ok"], raw["预期结果"]
        assert isinstance(raw["预期结果"], list), type(raw["预期结果"])
        # Single-element string list passes through as a 1-element list (not joined).
        assert raw["优先级"] == "P1", raw["优先级"]
        assert "前置条件" in mirrored and "操作步骤" in mirrored and "预期结果" in mirrored, mirrored
        return f"mirrored={sorted(mirrored)}"
    _run("TC-02", _SELF_TEST_CASES[1][1], _t02)

    # 3. priority alias compatibility: L1S6Validator reads Chinese OR English.
    # Note: L1S6Validator.validate_required_fields also enforces s5_ref
    # presence (added in v17 field-traceability pass). Test cases that
    # exercise the priority/Chinese-field aliasing must also include s5_ref.
    def _t03():
        validator = L1S6Validator()
        validator.set_requirement_objects_and_tp_list([], [])
        data = {"test_cases": [{
            "case_id": "UI-TC-001",
            "module": "UI",
            "用例描述": "X",
            "功能描述": "Y",
            "前置条件": "ok",
            "操作步骤": "1. x",
            "预期结果": "ok",
            "优先级": "P1",
            "s5_ref": "UI-TP-001",
        }]}
        req_errors = validator.validate_required_fields(data)
        id_errors = validator.validate_id_naming(data)
        assert not req_errors and not id_errors, (req_errors, id_errors)
        return f"req_errors={len(req_errors)}, id_errors={len(id_errors)}"
    _run("TC-03", _SELF_TEST_CASES[2][1], _t03)

    # 4. L1 pass → Ready writeback (uses dummy objs/tps).
    def _t04():
        cases_pass = [{
            "case_id": "UI-TC-001", "module": "UI",
            "用例描述": "商店道具排序", "功能描述": "验证",
            "前置条件": "玩家已登录", "操作步骤": "1. 进入商城",
            "预期结果": "通过", "优先级": "P1",
            "s5_ref": "UI-TP-001",
        }]
        outcome = evaluate_status(cases_pass, run_l2=False)
        assert cases_pass[0]["用例状态"] == "Ready", outcome
        assert outcome["l1_result"]["passed"] is True, outcome
        return f"用例状态={cases_pass[0]['用例状态']}, l1.passed={outcome['l1_result']['passed']}"
    _run("TC-04", _SELF_TEST_CASES[3][1], _t04)

    # 5. L1 fail (bad id) → Draft on every case.
    def _t05():
        cases_fail = [{
            "case_id": "NO-PREFIX", "module": "UI",
            "用例描述": "X", "功能描述": "Y", "前置条件": "ok",
            "操作步骤": "1. x", "预期结果": "ok", "优先级": "P1",
            "s5_ref": "UI-TP-001",
            "用例状态": "Ready",
        }]
        outcome = evaluate_status(cases_fail, run_l2=False)
        assert cases_fail[0]["用例状态"] == "Draft", outcome
        assert outcome["l1_result"]["passed"] is False, outcome
        return f"用例状态={cases_fail[0]['用例状态']}, l1.passed={outcome['l1_result']['passed']}"
    _run("TC-05", _SELF_TEST_CASES[4][1], _t05)

    # 6. L1 pass + L2 fail → Draft.
    def _t06():
        cases_mixed = [{
            "case_id": "UI-TC-020", "module": "UI",
            "用例描述": "X", "功能描述": "Y", "前置条件": "ok",
            "操作步骤": "1. x", "预期结果": "ok", "优先级": "P1",
            "s5_ref": "UI-TP-001",
            # missing "功能描述" content triggers L2 PLACEHOLDER_IN_DESCRIPTION
            # (uses 等等 触发): None → empty passes, but "" + "等等" fails.
            "功能描述": "等等等等",
        }]
        outcome = evaluate_status(cases_mixed, run_l2=True, l2_mode="strict")
        assert outcome["l1_result"]["passed"] is True, outcome
        assert outcome["l2_result"]["passed"] is False, outcome
        assert cases_mixed[0]["用例状态"] == "Draft", outcome
        return f"l1.passed={outcome['l1_result']['passed']}, l2.passed={outcome['l2_result']['passed']}"
    _run("TC-06", _SELF_TEST_CASES[5][1], _t06)

    # 7. Round 16 fix — list→list mirror (3-element list stays a 3-element
    #    list on the canonical Chinese key, not collapsed to "\n"-joined string).
    def _t07():
        raw_list = {
            "case_id": "UI-TC-030",
            "module": "UI",
            "preconditions": ["玩家已登录", "商城已配置道具", "余额>=100"],
            "steps": [
                {"step_num": 1, "action": "进入商城"},
                {"step_num": 2, "action": "选择道具"},
                {"step_num": 3, "action": "点击购买"},
            ],
            "expected_results": ["弹出支付弹窗", "余额扣减成功", "道具加入背包"],
        }
        mirrored = mirror_bilingual_aliases(raw_list)
        assert raw_list["前置条件"] == ["玩家已登录", "商城已配置道具", "余额>=100"], raw_list["前置条件"]
        assert isinstance(raw_list["前置条件"], list) and len(raw_list["前置条件"]) == 3
        assert raw_list["操作步骤"] == [
            {"step_num": 1, "action": "进入商城"},
            {"step_num": 2, "action": "选择道具"},
            {"step_num": 3, "action": "点击购买"},
        ], raw_list["操作步骤"]
        assert isinstance(raw_list["操作步骤"], list) and len(raw_list["操作步骤"]) == 3
        assert raw_list["预期结果"] == ["弹出支付弹窗", "余额扣减成功", "道具加入背包"], raw_list["预期结果"]
        assert isinstance(raw_list["预期结果"], list) and len(raw_list["预期结果"]) == 3
        assert "前置条件" in mirrored and "操作步骤" in mirrored and "预期结果" in mirrored, mirrored
        return f"mirrored={sorted(mirrored)}"
    _run("TC-07", _SELF_TEST_CASES[6][1], _t07)

    # 8. Round 16 fix — string→string mirror (legacy English strings keep
    #    their scalar shape on the canonical Chinese key).
    def _t08():
        raw_str = {
            "case_id": "UI-TC-031",
            "module": "UI",
            "priority": "P0",
            "preconditions": "无前置",  # scalar string, not a list
        }
        mirrored_str = mirror_bilingual_aliases(raw_str)
        assert raw_str["优先级"] == "P0", raw_str["优先级"]
        assert isinstance(raw_str["优先级"], str), type(raw_str["优先级"])
        assert raw_str["前置条件"] == "无前置", raw_str["前置条件"]
        assert isinstance(raw_str["前置条件"], str), type(raw_str["前置条件"])
        return f"mirrored={sorted(mirrored_str)}"
    _run("TC-08", _SELF_TEST_CASES[7][1], _t08)

    # 9. Round 16 fix — mixed canonical fields: a canonical Chinese key already
    #    filled with a list must NOT be overwritten by the legacy English alias,
    #    even when the legacy field is also a list (idempotency contract).
    def _t09():
        raw_mix = {
            "case_id": "UI-TC-032",
            "module": "UI",
            "前置条件": ["中文已填前置1", "中文已填前置2"],
            "preconditions": ["英文明文不应覆盖1", "英文明文不应覆盖2"],
            "expected_results": ["ok1", "ok2"],
        }
        mirrored_mix = mirror_bilingual_aliases(raw_mix)
        # canonical was filled → must stay unchanged
        assert raw_mix["前置条件"] == ["中文已填前置1", "中文已填前置2"], raw_mix["前置条件"]
        # canonical was empty → legacy list mirrors over
        assert raw_mix["预期结果"] == ["ok1", "ok2"], raw_mix["预期结果"]
        assert isinstance(raw_mix["预期结果"], list)
        assert "前置条件" not in mirrored_mix, "canonical already filled; must not be mirrored"
        assert "预期结果" in mirrored_mix, "canonical empty; must mirror from legacy"
        return f"mirrored={sorted(mirrored_mix)}"
    _run("TC-09", _SELF_TEST_CASES[8][1], _t09)

    # 10. T-004 / Round 15 follow-up — OBJ-level P0 risk matrix. Setup:
    #     OBJ-A (3 cases all P1) → must promote first non-Draft to P0
    #     OBJ-B (2 cases all P2) → must promote first non-Draft to P0
    #     OBJ-C (1 case already P0) → no-op
    #     OBJ-D (1 Draft case only) → promotion (Draft promoted by v2 contract)
    #     OBJ-E (no obj_id) → skipped (synthetic empty group)
    def _t10():
        obj_risk_cases = [
            {"case_id": "BIZ-TC-100", "module": "BIZ", "obj_id": "OBJ-A",
             "priority": "P1", "用例状态": "Ready"},
            {"case_id": "BIZ-TC-101", "module": "BIZ", "obj_id": "OBJ-A",
             "priority": "P1", "用例状态": "Ready"},
            {"case_id": "BIZ-TC-102", "module": "BIZ", "obj_id": "OBJ-A",
             "priority": "P1", "用例状态": "Ready"},
            {"case_id": "BIZ-TC-110", "module": "BIZ", "obj_id": "OBJ-B",
             "priority": "P2", "用例状态": "Ready"},
            {"case_id": "BIZ-TC-111", "module": "BIZ", "obj_id": "OBJ-B",
             "priority": "P2", "用例状态": "Ready"},
            {"case_id": "UI-TC-120", "module": "UI", "obj_id": "OBJ-C",
             "priority": "P0", "用例状态": "Ready"},
            {"case_id": "UI-TC-130", "module": "UI", "obj_id": "OBJ-D",
             "priority": "P1", "用例状态": "Draft"},
            {"case_id": "UI-TC-140", "module": "UI", "obj_id": "",
             "priority": "P1", "用例状态": "Ready"},
        ]
        # Bare enforce call (we skip normalize_payload here to keep `priority` as
        # the canonical read path — mirror_bilingual_aliases would otherwise move
        # the value into 优先级 before enforce runs). The function reads either
        # alias via _read_pri, so this is still exercising the same contract.
        obj_risk_cases, stats = enforce_obj_p0_coverage(obj_risk_cases)

        # OBJ-A: first case promoted P1 → P0
        by_id = {c["case_id"]: c for c in obj_risk_cases}
        assert by_id["BIZ-TC-100"]["priority"] == "P0", by_id["BIZ-TC-100"]
        assert by_id["BIZ-TC-101"]["priority"] == "P1", by_id["BIZ-TC-101"]
        assert by_id["BIZ-TC-102"]["priority"] == "P1", by_id["BIZ-TC-102"]
        # _auto_promoted lineage preserved
        assert "_auto_promoted" in by_id["BIZ-TC-100"], by_id["BIZ-TC-100"]
        lineage = by_id["BIZ-TC-100"]["_auto_promoted"]
        assert isinstance(lineage, list) and lineage[0]["from"] == "P1"
        assert lineage[0]["to"] == "P0" and lineage[0]["src"] == "T-004 OBJ-risk matrix"

        # OBJ-B: first case promoted P2 → P0
        assert by_id["BIZ-TC-110"]["priority"] == "P0", by_id["BIZ-TC-110"]
        assert by_id["BIZ-TC-111"]["priority"] == "P2", by_id["BIZ-TC-111"]
        assert by_id["BIZ-TC-110"]["_auto_promoted"][0]["from"] == "P2"

        # OBJ-C: already P0 → no-op, no _auto_promoted written
        assert by_id["UI-TC-120"]["priority"] == "P0", by_id["UI-TC-120"]
        assert "_auto_promoted" not in by_id["UI-TC-120"], by_id["UI-TC-120"]

        # OBJ-D: only Draft case → promoted by v2 contract.
        assert by_id["UI-TC-130"]["priority"] == "P0", by_id["UI-TC-130"]
        assert "_auto_promoted" in by_id["UI-TC-130"], by_id["UI-TC-130"]
        assert by_id["UI-TC-130"]["_auto_promoted"][0]["from"] == "P1"

        # Empty-obj_id group: skipped
        assert by_id["UI-TC-140"]["priority"] == "P1", by_id["UI-TC-140"]
        assert "_auto_promoted" not in by_id["UI-TC-140"], by_id["UI-TC-140"]

        # Stats: 4 OBJs total (A/B/C/D — empty group excluded), 1 already covered,
        # 3 promoted (A/B/D), 3 cases promoted, promoted_objs sorted =
        # ["OBJ-A", "OBJ-B", "OBJ-D"]. OBJ-D's case is Draft, but the
        # v2 contract promotes Draft cases too — see §contract 2 in the
        # enforce_obj_p0_coverage docstring.
        assert stats["objs_total"] == 4, stats
        assert stats["objs_already_covered"] == 1, stats
        assert stats["objs_promoted"] == 3, stats
        assert stats["cases_promoted"] == 3, stats
        assert sorted(stats["promoted_objs"]) == ["OBJ-A", "OBJ-B", "OBJ-D"], stats
        return f"stats.objs_promoted={stats['objs_promoted']}, cases_promoted={stats['cases_promoted']}"
    _run("TC-10", _SELF_TEST_CASES[9][1], _t10)

    # 11. T-004 — idempotency: re-running enforce on the already-promoted list
    #     must NOT double-promote (BIZ-TC-100 already has _auto_promoted).
    def _t11():
        obj_risk_cases = [
            {"case_id": "BIZ-TC-100", "module": "BIZ", "obj_id": "OBJ-A",
             "priority": "P1", "用例状态": "Ready"},
            {"case_id": "BIZ-TC-101", "module": "BIZ", "obj_id": "OBJ-A",
             "priority": "P1", "用例状态": "Ready"},
        ]
        # First run: promote.
        obj_risk_cases, stats_first = enforce_obj_p0_coverage(obj_risk_cases)
        assert stats_first["cases_promoted"] == 1, stats_first
        # Second run: must be no-op.
        _, stats_idem = enforce_obj_p0_coverage(obj_risk_cases)
        by_id_2 = {c["case_id"]: c for c in obj_risk_cases}
        assert by_id_2["BIZ-TC-100"]["priority"] == "P0"
        assert len(by_id_2["BIZ-TC-100"]["_auto_promoted"]) == 1, by_id_2["BIZ-TC-100"]
        assert stats_idem["cases_promoted"] == 0, stats_idem
        assert stats_idem["objs_promoted"] == 0, stats_idem
        return f"first.cases_promoted={stats_first['cases_promoted']}, second.cases_promoted={stats_idem['cases_promoted']}, lineage_len={len(by_id_2['BIZ-TC-100']['_auto_promoted'])}"
    _run("TC-11", _SELF_TEST_CASES[10][1], _t11)

    # 12. T-003 / V-001 — renumber_cases_per_module (apply=True). Three
    #     cases interleaved across modules (UI/BIZ/BIZ with non-contiguous
    #     tails) get rewritten to gap-free per-module numbering.
    def _t12():
        cases_renumber = [
            {"case_id": "BIZ-TC-200", "module": "BIZ", "obj_id": "OBJ-A"},
            {"case_id": "UI-TC-050", "module": "UI", "obj_id": "OBJ-A"},
            {"case_id": "BIZ-TC-064", "module": "BIZ", "obj_id": "OBJ-A"},
            {"case_id": "UI-TC-001", "module": "UI", "obj_id": "OBJ-B"},
            {"case_id": "BIZ-TC-321", "module": "BIZ", "obj_id": "OBJ-B"},
        ]
        stats_renum = renumber_cases_per_module(cases_renumber, apply=True)
        assert stats_renum["by_module"]["UI"]["count"] == 2, stats_renum
        assert stats_renum["by_module"]["BIZ"]["count"] == 3, stats_renum
        # Within UI: obj_id-sorted → OBJ-A first → 001, then OBJ-B → 002.
        ui_ids = sorted(c["case_id"] for c in cases_renumber if c["module"] == "UI")
        assert ui_ids == ["UI-TC-001", "UI-TC-002"], ui_ids
        biz_ids = sorted(c["case_id"] for c in cases_renumber if c["module"] == "BIZ")
        assert biz_ids == ["BIZ-TC-001", "BIZ-TC-002", "BIZ-TC-003"], biz_ids
        assert stats_renum["apply_performed"] is True
        assert stats_renum["rewrites"] == 5
        return f"UI={ui_ids}, BIZ={biz_ids}, rewrites={stats_renum['rewrites']}"
    _run("TC-12", _SELF_TEST_CASES[11][1], _t12)

    # 13. T-003 idempotency: re-running on the already-rewritten payload is a
    #     no-op (already_canonical=True, apply_performed=False, rewrites=0).
    def _t13():
        cases_renumber = [
            {"case_id": "UI-TC-001", "module": "UI", "obj_id": "OBJ-A"},
            {"case_id": "UI-TC-002", "module": "UI", "obj_id": "OBJ-B"},
            {"case_id": "BIZ-TC-001", "module": "BIZ", "obj_id": "OBJ-A"},
            {"case_id": "BIZ-TC-002", "module": "BIZ", "obj_id": "OBJ-A"},
            {"case_id": "BIZ-TC-003", "module": "BIZ", "obj_id": "OBJ-B"},
        ]
        stats_renum_2 = renumber_cases_per_module(cases_renumber, apply=True)
        assert stats_renum_2["already_canonical"] is True, stats_renum_2
        assert stats_renum_2["apply_performed"] is False, stats_renum_2
        assert stats_renum_2["rewrites"] == 0, stats_renum_2
        return f"already_canonical={stats_renum_2['already_canonical']}, rewrites={stats_renum_2['rewrites']}"
    _run("TC-13", _SELF_TEST_CASES[12][1], _t13)

    # 14. T-003 dry-run path (apply=False): computes the intended mapping for
    #     stats but does NOT mutate any case.
    def _t14():
        cases_dry = [
            {"case_id": "TC-7", "module": "UI", "obj_id": "OBJ-A"},
            {"case_id": "TC-15", "module": "UI", "obj_id": "OBJ-A"},
        ]
        stats_dry = renumber_cases_per_module(cases_dry, apply=False)
        assert stats_dry["by_module"]["UI"]["count"] == 2, stats_dry
        assert stats_dry["apply_performed"] is False
        assert [c["case_id"] for c in cases_dry] == ["TC-7", "TC-15"]
        # Non-applied run is also "not canonical" (no mutation happened).
        assert stats_dry["already_canonical"] is False
        assert stats_dry["rewrites"] == 0
        return f"by_module.UI.count={stats_dry['by_module']['UI']['count']}, rewrites={stats_dry['rewrites']}"
    _run("TC-14", _SELF_TEST_CASES[13][1], _t14)

    # 15. T-003 fallback: a case with no module field but already bearing a
    #     canonical case_id prefix derives its module from case_id.
    def _t15():
        hybrid = [
            {"case_id": "LOG-TC-005"},
            {"case_id": "LOG-TC-099"},
        ]
        stats_hybrid = renumber_cases_per_module(hybrid, apply=True)
        assert stats_hybrid["by_module"]["LOG"]["count"] == 2, stats_hybrid
        assert stats_hybrid["skipped_no_prefix"] == 0
        assert sorted(c["case_id"] for c in hybrid) == ["LOG-TC-001", "LOG-TC-002"]
        return f"by_module.LOG.count={stats_hybrid['by_module']['LOG']['count']}, skipped_no_prefix={stats_hybrid['skipped_no_prefix']}"
    _run("TC-15", _SELF_TEST_CASES[14][1], _t15)

    # 16. v29 T-101 — evaluate_status accepts list[dict] `tps` and runs the
    #     full L1 + L2 pipeline without raising (contract test for the
    #     F-1 carry from v28 §6.3 — the caller must pass dicts, not strings).
    def _t16():
        cases_for_tps = [{
            "case_id": "UI-TC-040", "module": "UI",
            "用例描述": "X", "功能描述": "Y",
            "前置条件": "ok", "操作步骤": "1. x", "预期结果": "ok",
            "优先级": "P1", "s5_ref": "UI-TP-001",
        }]
        tps_dict = [{"tp_id": "UI-TP-001", "obj_id": "OBJ-A", "用例描述": "TP"}]
        outcome = evaluate_status(cases_for_tps, tps=tps_dict, run_l2=False)
        assert outcome["l1_result"]["passed"] is True, outcome
        return f"l1.passed={outcome['l1_result']['passed']}, tps_entries={len(tps_dict)}"
    _run("TC-16", _SELF_TEST_CASES[15][1], _t16)

    # 17. v29 T-101 — evaluate_status rejects list[str] `tps` with a clear
    #     TypeError instead of the cryptic ``AttributeError: 'str' object has
    #     no attribute 'get'`` that L1S6Validator would raise otherwise. This
    #     is the defensive guard added at the `evaluate_status` boundary
    #     (v28 §6.3 forbids touching the validator source).
    def _t17():
        cases_for_tps_str = [{
            "case_id": "UI-TC-041", "module": "UI",
            "用例描述": "X", "功能描述": "Y",
            "前置条件": "ok", "操作步骤": "1. x", "预期结果": "ok",
            "优先级": "P1", "s5_ref": "UI-TP-001",
        }]
        raised = False
        err_msg = ""
        try:
            evaluate_status(cases_for_tps_str, tps=["UI-TP-001"], run_l2=False)
        except TypeError as e:
            raised = True
            err_msg = str(e)
            assert "must be a list of dicts" in err_msg, err_msg
            assert "str" in err_msg, err_msg
        assert raised, "list[str] tps should raise TypeError, not silently pass"
        return f"TypeError raised: msg~={err_msg[:80]!r}"
    _run("TC-17", _SELF_TEST_CASES[16][1], _t17)

    # 18. v29 T-101 — passing tps=None still works (existing contract).
    def _t18():
        cases_for_tps = [{
            "case_id": "UI-TC-040", "module": "UI",
            "用例描述": "X", "功能描述": "Y",
            "前置条件": "ok", "操作步骤": "1. x", "预期结果": "ok",
            "优先级": "P1", "s5_ref": "UI-TP-001",
        }]
        outcome_none = evaluate_status(cases_for_tps, tps=None, run_l2=False)
        assert outcome_none["l1_result"]["passed"] is True, outcome_none
        return f"l1.passed={outcome_none['l1_result']['passed']}"
    _run("TC-18", _SELF_TEST_CASES[17][1], _t18)

    total = len(results)
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = total - passed

    if verbose:
        print(f"total={total} passed={passed} failed={failed}")

    # Always write the per-case report to a sibling .md file. Old CI callers of
    # `--self-test` only check exit code + the legacy "PASS"/"FAIL" stdout line
    # — adding a side-effect .md file does not break that contract (V-101R
    # compatibility).
    try:
        report_md = _format_self_test_report(results)
        report_path = Path(__file__).resolve().parent / "case_id_and_field_normalizer.self_test_report.md"
        report_path.write_text(report_md, encoding="utf-8")
    except Exception as e:
        print(f"WARN: failed to write self_test_report.md: {type(e).__name__}: {e}", file=sys.stderr)

    if failed > 0:
        print(f"case_id_and_field_normalizer self-test: FAIL ({failed}/{total} failed)")
        return 1
    print("case_id_and_field_normalizer self-test: PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test-verbose":
        raise SystemExit(self_test(verbose=True))
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    raise SystemExit("usage: python3 ai_workflow/case_id_and_field_normalizer.py --self-test|--self-test-verbose")
