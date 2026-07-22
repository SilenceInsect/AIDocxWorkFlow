#!/usr/bin/env python3
"""Fix S5/S6 field traceability: add missing fields.

Tasks:
1. S5 test_points.json: add preconditions field (based on obj_id/module)
2. S6 test_cases.json: add obj_name field (inherited from S5 TP via s5_ref)
"""

import json
import sys
from pathlib import Path

# Paths
BASE_DIR = Path("workflow_assets/游戏道具商城系统/v3.01")
S2_JSON = BASE_DIR / "「S2 需求拆解」/requirement_objects.json"
S5_JSON = BASE_DIR / "「S5 测试点生成」/test_points.json"
S6_JSON = BASE_DIR / "「S6 测试用例生成」/test_cases.json"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict, indent: int = 2):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def generate_preconditions(tp: dict, obj_name: str, module: str) -> list[str]:
    """Generate preconditions based on obj_id, obj_name, and module."""
    obj_id = tp.get("obj_id", "")
    tp_type = tp.get("test_point_type", "")
    
    # Base preconditions for all scenarios
    base_preconditions = ["玩家已登录游戏客户端"]
    
    # Module-specific preconditions
    if module == "UI":
        if "商城" in obj_name or "道具" in obj_name:
            base_preconditions.append("商城已配置道具数据")
        if "搜索" in obj_name:
            base_preconditions.append("商城有可搜索的道具数据")
        if "详情" in obj_name:
            base_preconditions.append("玩家已进入道具详情页")
    elif module == "BIZ":
        if "购买" in obj_name or "支付" in obj_name:
            base_preconditions.append("玩家游戏币余额充足")
        if "折扣" in obj_name or "VIP" in obj_name:
            base_preconditions.append("玩家VIP等级已激活")
        if "促销" in obj_name or "活动" in obj_name:
            base_preconditions.append("促销活动已配置生效")
        if "退款" in obj_name:
            base_preconditions.append("玩家有有效退款订单")
        if "上下架" in obj_name:
            base_preconditions.append("运营人员已登录后台系统")
        if "配置" in obj_name or "管理" in obj_name:
            base_preconditions.append("运营人员有相应权限")
        if "订单" in obj_name:
            base_preconditions.append("玩家有购买历史")
    elif module == "LOG":
        base_preconditions.append("邮件服务正常运行")
    elif module == "SPECIAL":
        base_preconditions.append("风控系统已启用")
    
    # Type-specific preconditions
    if tp_type == "NEGATIVE":
        base_preconditions.append("异常场景已配置")
    elif tp_type == "EXCEPTION":
        base_preconditions.append("异常环境已准备")
    elif tp_type == "BOUNDARY_MIN":
        base_preconditions.append("边界测试数据已准备")
    elif tp_type == "BOUNDARY_MAX":
        base_preconditions.append("边界测试数据已准备")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_preconditions = []
    for p in base_preconditions:
        if p not in seen:
            seen.add(p)
            unique_preconditions.append(p)
    
    return unique_preconditions


def fix_s5():
    """Fix S5 test_points.json: add preconditions field."""
    print("=" * 60)
    print("Task 1: Fix S5 test_points.json - add preconditions")
    print("=" * 60)
    
    # Load S2 for obj_name mapping
    s2_data = load_json(S2_JSON)
    obj_id_to_name = {}
    for obj in s2_data.get("objects", []):
        obj_id_to_name[obj["id"]] = obj["obj_name"]
    
    # Load S5
    s5_data = load_json(S5_JSON)
    tps = s5_data.get("test_points", [])
    
    fixed_count = 0
    for tp in tps:
        # Check if preconditions already exists and is not empty
        existing_precond = tp.get("preconditions", None)
        if existing_precond is None or (isinstance(existing_precond, list) and len(existing_precond) == 0):
            # Generate preconditions based on obj_id and module
            obj_id = tp.get("obj_id", "")
            obj_name = obj_id_to_name.get(obj_id, "")
            module = tp.get("module", "")
            
            tp["preconditions"] = generate_preconditions(tp, obj_name, module)
            fixed_count += 1
            print(f"  [{tp['tp_id']}] Added {len(tp['preconditions'])} preconditions for {module}/{obj_name}")
    
    print(f"\nFixed {fixed_count} TPs (out of {len(tps)} total)")
    
    # Update meta
    s5_data["meta"]["regenerated"] = "v17_preconditions_fix"
    s5_data["meta"]["preconditions_added"] = fixed_count
    
    # Save
    save_json(S5_JSON, s5_data)
    print(f"Saved: {S5_JSON}")
    
    return s5_data


def fix_s6(s5_data: dict):
    """Fix S6 test_cases.json: add obj_name field inherited from S5 TP."""
    print("\n" + "=" * 60)
    print("Task 2: Fix S6 test_cases.json - add obj_name field")
    print("=" * 60)
    
    # Build TP lookup: tp_id -> obj_name
    tp_id_to_obj_name = {}
    for tp in s5_data.get("test_points", []):
        tp_id = tp.get("tp_id", "")
        obj_name = tp.get("obj_name", "")
        if tp_id and obj_name:
            tp_id_to_obj_name[tp_id] = obj_name
    
    print(f"Built TP lookup: {len(tp_id_to_obj_name)} entries")
    
    # Load S6
    s6_data = load_json(S6_JSON)
    tcs = s6_data.get("test_cases", [])
    
    fixed_count = 0
    no_ref_count = 0
    for tc in tcs:
        s5_ref = tc.get("s5_ref", "")
        existing_obj_name = tc.get("obj_name", "")
        
        if existing_obj_name:
            # Already has obj_name, skip
            continue
        
        if not s5_ref:
            no_ref_count += 1
            continue
        
        # Inherit obj_name from S5 TP
        inherited_obj_name = tp_id_to_obj_name.get(s5_ref, "")
        if inherited_obj_name:
            tc["obj_name"] = inherited_obj_name
            fixed_count += 1
            if fixed_count <= 10:
                print(f"  [{tc['case_id']}] Inherited obj_name='{inherited_obj_name}' from {s5_ref}")
        else:
            print(f"  WARNING: [{tc['case_id']}] s5_ref={s5_ref} not found in TP lookup")
            no_ref_count += 1
    
    print(f"\nFixed {fixed_count} TCs (out of {len(tcs)} total)")
    print(f"Skipped: {no_ref_count} (no s5_ref)")
    
    # Update meta (if exists)
    if "meta" in s6_data:
        s6_data["meta"]["regenerated"] = "v17_obj_name_fix"
        s6_data["meta"]["obj_name_added"] = fixed_count
    else:
        s6_data["obj_name_added"] = fixed_count
    
    # Save
    save_json(S6_JSON, s6_data)
    print(f"Saved: {S6_JSON}")
    
    return s6_data


def main():
    print("S5/S6 Field Traceability Fix Script")
    print("=" * 60)
    
    # Verify files exist
    for path in [S2_JSON, S5_JSON, S6_JSON]:
        if not path.exists():
            print(f"ERROR: {path} not found!")
            sys.exit(1)
        print(f"Found: {path}")
    
    print()
    
    # Task 1: Fix S5
    s5_data = fix_s5()
    
    # Task 2: Fix S6
    s6_data = fix_s6(s5_data)
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"S5 TPs fixed: {s5_data['meta'].get('preconditions_added', 0)}")
    print(f"S6 TCs fixed: {s6_data['meta'].get('obj_name_added', 0)}")
    print("\nDone!")


if __name__ == "__main__":
    main()
