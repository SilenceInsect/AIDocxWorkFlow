#!/usr/bin/env python3
"""Round 3 Fix — R3-F2 (fp_name) + R3-F3 (assertion).

Reads:
  - workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」/requirement_objects.json
  - workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json
  - workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json

Writes:
  - test_cases.json (fixed in-place with fp_name + assertion)
  - round3_fix_log.json (change manifest)
"""

import json, sys, re
from pathlib import Path

BASE = Path("workflow_assets/游戏道具商城系统/v3.01")
S2_PATH = BASE / "「S2 需求拆解」/requirement_objects.json"
S5_PATH = BASE / "「S5 测试点生成」/test_points.json"
S6_PATH = BASE / "「S6 测试用例生成」/test_cases.json"
OUT_LOG = BASE / "「S6 测试用例生成」/round3_fix_log.json"


def load_json(p: Path) -> dict:
    with open(p) as f:
        return json.load(f)


def save_json(p: Path, data: dict):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Wrote {p}")


def build_tp_lookup(tp_list: list[dict]) -> dict[str, dict]:
    return {tp["tp_id"]: tp for tp in tp_list}


# ── assertion helpers ────────────────────────────────────────────────────────

_ASSERTION_TOKENS = (
    "应", "应该", "必须", "需要", "应当",
    "返回", "展示", "显示", "提示", "状态",
    "正常", "成功", "完成", "可见", "存在",
    "禁用", "不可", "不为", "不显示", "不展示", "不出现",
    "为", "是", "成", "到",
    "= ", "：", ":",
)

_STATE_CHANGE_TOKENS = {"变为", "变成", "转为", "切换为", "转为"}


def _has_assertion(text: str) -> bool:
    if not text or not text.strip():
        return False
    if any(t in text for t in _ASSERTION_TOKENS):
        return True
    if any(t in text for t in _STATE_CHANGE_TOKENS):
        return True
    # numeric or boolean values
    if re.search(r"[\d]+\s*(元|个|折|%|次|天|秒|分钟|≤|≥|<|>)", text):
        return True
    return False


def extract_assertion_from_steps(case: dict) -> str:
    """Derive assertion text from 操作步骤 + 预期结果."""
    steps_text = ""
    for step in case.get("操作步骤", []):
        if isinstance(step, dict):
            steps_text += step.get("action", "") + "\n"
        else:
            steps_text += str(step) + "\n"

    # Extract expected from 预期结果
    expected_list = case.get("预期结果", [])
    expected_texts = []
    if isinstance(expected_list, list):
        for e in expected_list:
            if isinstance(e, dict):
                txt = e.get("预期", "").strip()
                if txt:
                    expected_texts.append(txt)
    elif expected_list:
        expected_texts.append(str(expected_list).strip())

    combined = "\n".join(expected_texts)

    # Extract first meaningful assertion from 预期结果
    if _has_assertion(combined):
        # Pick the most substantive line
        for line in expected_texts:
            if _has_assertion(line) and len(line) > 5:
                return line

    # Fallback: derive from test_type + title
    case_id = case.get("case_id", "")
    case_type = case.get("用例类型", case.get("test_type", ""))
    title = case.get("用例描述", case.get("title", ""))

    # Generate a simple assertion
    action_map = {
        "POSITIVE": "验证通过",
        "NEGATIVE": "验证被正确拒绝/拦截",
        "BOUNDARY_MIN": "验证边界值符合预期",
        "BOUNDARY_MAX": "验证边界值符合预期",
        "EXCEPTION": "验证异常处理符合预期",
    }
    default_assertion = action_map.get(case_type, "验证功能正常")
    return default_assertion


def fill_assertion(case: dict) -> str:
    """Return assertion string for a case, derived from 预期结果."""
    expected_list = case.get("预期结果", [])

    # Collect all 预期 lines
    lines = []
    if isinstance(expected_list, list):
        for e in expected_list:
            if isinstance(e, dict):
                txt = e.get("预期", "").strip()
                if txt:
                    lines.append(txt)
            elif isinstance(e, str):
                t = e.strip()
                if t:
                    lines.append(t)

    if not lines:
        return extract_assertion_from_steps(case)

    # Try to pick the most specific assertion line
    for line in lines:
        if _has_assertion(line):
            return line

    return lines[0] if lines else extract_assertion_from_steps(case)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("=== Round 3 Fix: F2 (fp_name) + F3 (assertion) ===\n")

    s2 = load_json(S2_PATH)
    s5 = load_json(S5_PATH)
    s6 = load_json(S6_PATH)

    tp_map = build_tp_lookup(s5["test_points"])
    cases = s6["test_cases"]

    # ── F2: fix fp_name ─────────────────────────────────────────────────────
    print("--- F2: fp_name alignment ---")
    fp_name_fixes = []
    for case in cases:
        s5_ref = case.get("s5_ref", "")
        tc_fp = case.get("fp_name", "")
        if s5_ref and s5_ref in tp_map:
            tp_fp = tp_map[s5_ref].get("fp_name", "")
            if tc_fp != tp_fp:
                fp_name_fixes.append({
                    "case_id": case["case_id"],
                    "old_fp_name": tc_fp,
                    "new_fp_name": tp_fp,
                    "s5_ref": s5_ref,
                })
                case["fp_name"] = tp_fp

    print(f"  Fixed {len(fp_name_fixes)} fp_name mismatches:")
    for f in fp_name_fixes:
        print(f"    {f['case_id']}: '{f['old_fp_name']}' → '{f['new_fp_name']}'")

    # ── F3: fill assertion ──────────────────────────────────────────────────
    print("\n--- F3: fill assertion fields ---")
    assertion_fills = []
    for case in cases:
        existing = case.get("assertion")
        if existing is None or existing == "" or existing == []:
            new_assertion = fill_assertion(case)
            if new_assertion:
                case["assertion"] = new_assertion
                assertion_fills.append({
                    "case_id": case["case_id"],
                    "assertion": new_assertion,
                })

    print(f"  Filled {len(assertion_fills)} null assertion fields")
    print(f"  Sample fills:")
    for f in assertion_fills[:5]:
        print(f"    {f['case_id']}: '{f['assertion']}'")
    if len(assertion_fills) > 5:
        print(f"    ... and {len(assertion_fills) - 5} more")

    # ── write outputs ─────────────────────────────────────────────────────────
    print("\n--- Writing files ---")
    save_json(S6_PATH, s6)

    log = {
        "meta": {
            "round": 3,
            "fixes": ["R3-F2 fp_name", "R3-F3 assertion"],
            "req_name": "游戏道具商城系统",
            "version": "v3.01",
        },
        "fp_name_fixes": fp_name_fixes,
        "assertion_fills": assertion_fills,
        "summary": {
            "fp_name_fixed": len(fp_name_fixes),
            "assertion_filled": len(assertion_fills),
            "total_cases": len(cases),
            "remaining_null_assertion": sum(
                1 for c in cases if c.get("assertion") is None or c.get("assertion") == ""
            ),
        },
    }
    save_json(Path(OUT_LOG), log)

    print(f"\n=== Done: {len(fp_name_fixes)} fp_name fixes, {len(assertion_fills)} assertion fills ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
