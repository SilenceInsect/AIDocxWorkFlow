#!/usr/bin/env python3
"""Fix S5 EXCEPTION TP s4_reference — Round 6 T11.

Extracts S4 leaf ID from applies_rule field (format: "... | Push4: S4-XXX-Y-Z")
for all EXCEPTION TPs that have null s4_reference.
"""

import json
import re
import sys

TP_FILE = "workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json"

def extract_s4_from_applies_rule(rule: str) -> str | None:
    """Extract S4 leaf ID from applies_rule field.
    Pattern: ... | Push{N}: S4-{EpicID}-X.Y.Z
    """
    if not rule:
        return None
    # Match S4-{module}-{epic}-{number}
    m = re.search(r'S4-[A-Z]+-[A-Z0-9]+-\d+(?:\.\d+)*', rule)
    return m.group(0) if m else None

def main():
    with open(TP_FILE, encoding="utf-8") as f:
        data = json.load(f)

    total_test_points = len(data.get("test_points", []))
    exception_tps = [tp for tp in data["test_points"]
                     if tp.get("test_point_type") == "EXCEPTION"]

    fixed = []
    already_filled = []
    still_null = []

    for tp in exception_tps:
        s4_ref = tp.get("s4_reference")
        applies = tp.get("applies_rule", "")

        if s4_ref is None or s4_ref == "":
            # Try to extract from applies_rule
            extracted = extract_s4_from_applies_rule(applies)
            if extracted:
                tp["s4_reference"] = extracted
                fixed.append({
                    "tp_id": tp["tp_id"],
                    "epic_id": tp["epic_id"],
                    "extracted_from_rule": extracted,
                    "applies_rule": applies
                })
            else:
                still_null.append({
                    "tp_id": tp["tp_id"],
                    "epic_id": tp["epic_id"],
                    "applies_rule": applies
                })
        else:
            already_filled.append({
                "tp_id": tp["tp_id"],
                "s4_reference": s4_ref,
                "applies_rule": applies
            })

    # Report
    print("=" * 70)
    print("T11 — S5 EXCEPTION TP s4_reference Fix Report")
    print("=" * 70)
    print(f"Total test_points in file:  {total_test_points}")
    print(f"Total EXCEPTION TPs:        {len(exception_tps)}")
    print(f"Already filled (non-null):  {len(already_filled)}")
    print(f"Fixed (null→extracted):     {len(fixed)}")
    print(f"Still null (no S4 in rule): {len(still_null)}")
    print()

    if already_filled:
        print("--- Already Filled ---")
        for item in already_filled[:5]:
            print(f"  {item['tp_id']} → {item['s4_reference']}")
        if len(already_filled) > 5:
            print(f"  ... ({len(already_filled)-5} more)")
        print()

    if fixed:
        print("--- Fixed (null → extracted from applies_rule) ---")
        for item in fixed[:10]:
            print(f"  {item['tp_id']} → {item['extracted_from_rule']}")
        if len(fixed) > 10:
            print(f"  ... ({len(fixed)-10} more)")
        print()

    if still_null:
        print("--- Still Null (no S4 in applies_rule) ---")
        for item in still_null:
            print(f"  {item['tp_id']} epic={item['epic_id']}")
            print(f"    applies_rule: {item['applies_rule'][:80]}...")
        print()

    # Save fixed file
    out_path = TP_FILE
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved fixed {TP_FILE}")

    # Write detail report
    report_path = TP_FILE.replace(".json", "_r6_s4_ref_fix.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_tps": total_test_points,
                "total_exception_tps": len(exception_tps),
                "already_filled": len(already_filled),
                "fixed": len(fixed),
                "still_null": len(still_null)
            },
            "already_filled": already_filled,
            "fixed": fixed,
            "still_null": still_null
        }, f, ensure_ascii=False, indent=2)
    print(f"Saved detail report: {report_path}")

    return len(fixed), len(still_null)

if __name__ == "__main__":
    fixed_count, null_count = main()
    sys.exit(0 if null_count == 0 else 1)
