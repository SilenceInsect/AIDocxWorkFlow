#!/usr/bin/env python3
"""
coverage_dual_track.py — 双轨覆盖率统计（v16 T5）

双轨：
  1. 主模块轨道（module）：按 TP.module 字段分组统计
  2. 维度轨道（related_tags）：按 related_tags 展开分组统计

差异 > 10% 时输出 WEAK_OVERLAP 警告。

用法：
  python3 ai_workflow/coverage_dual_track.py <tp.json> <obj.json> [--json] [--verbose]
  python3 ai_workflow/coverage_dual_track.py --self-test

输入：
  tp.json : test_points.json（S5 产出）
  obj.json: requirement_objects.json（S2 产出，含 OBJ 总数统计）

输出示例：
  {
    "module_coverage": {"BIZ": {"tp_count": 12, "obj_count": 8, "coverage": 0.92}, ...},
    "dimension_coverage": {"BIZ": {"tp_count": 18, "obj_count": 8, "coverage": 0.95}, ...},
    "warnings": [{"type": "WEAK_OVERLAP", "module": "BIZ", "module_cov": 0.85, "dim_cov": 0.95, "diff": 0.10}],
    "summary": {"total_tp": 128, "total_obj": 64, "warn_count": 1}
  }
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────
# 8 模块枚举（与 MODULES.md §1 同步）
# ─────────────────────────────────────────────
VALID_MODULES = {"CONFIG", "UI", "BIZ", "UTIL", "LINK", "SPECIAL", "LOG", "HINT"}


def load_json(path: str | Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize_tps(tps: list) -> list:
    """确保每条 TP 有 related_tags 字段（旧 TP 兼容）。"""
    for tp in tps:
        if "related_tags" not in tp or tp["related_tags"] is None:
            tp["related_tags"] = []
    return tps


def count_by_module(tps: list, objs: list) -> dict:
    """
    主模块轨道：按 module 字段分组统计。

    module_coverage[MOD] = {
        "tp_count": TP数(module=MOD),
        "obj_count": OBJ数(module=MOD),
        "coverage": tp_count / obj_count  (若 obj_count > 0)
    }
    """
    # OBJ 按 module 分组
    obj_by_module: dict[str, int] = {}
    for obj in objs:
        mod = obj.get("belong_module") or obj.get("module") or "UNKNOWN"
        if mod not in obj_by_module:
            obj_by_module[mod] = 0
        obj_by_module[mod] += 1

    # TP 按 module 分组
    tp_by_module: dict[str, int] = {}
    for tp in tps:
        mod = tp.get("module", "UNKNOWN")
        if mod not in tp_by_module:
            tp_by_module[mod] = 0
        tp_by_module[mod] += 1

    result = {}
    all_mods = VALID_MODULES | set(obj_by_module.keys()) | set(tp_by_module.keys())
    for mod in sorted(all_mods):
        tp_cnt = tp_by_module.get(mod, 0)
        obj_cnt = obj_by_module.get(mod, 0)
        cov = tp_cnt / obj_cnt if obj_cnt > 0 else None
        result[mod] = {
            "tp_count": tp_cnt,
            "obj_count": obj_cnt,
            "coverage": round(cov, 4) if cov is not None else None,
        }
    return result


def count_by_dimension(tps: list, objs: list) -> dict:
    """
    维度轨道：related_tags 展开分组统计。

    每条 TP 的 related_tags 数组展开（去重 + 去掉主 module 外的无效 tag），
    统计含该 tag 的 TP 数 / OBJ 数（module 同主 module）。

    dim_coverage[MOD] = {
        "tp_count": 有TP含MOD的TP总数,
        "obj_count": OBJ总数(module=MOD),
        "coverage": tp_count / obj_count
    }
    """
    # OBJ 按 module 分组
    obj_by_module: dict[str, int] = {}
    for obj in objs:
        mod = obj.get("belong_module") or obj.get("module") or "UNKNOWN"
        if mod not in obj_by_module:
            obj_by_module[mod] = 0
        obj_by_module[mod] += 1

    # TP related_tags 展开计数（只计 module 在 VALID_MODULES 内的）
    tp_dim_count: dict[str, int] = {mod: 0 for mod in VALID_MODULES}
    for tp in tps:
        mod = tp.get("module", "UNKNOWN")
        if mod not in VALID_MODULES:
            continue
        tags = set(tp.get("related_tags", []))
        for tag in tags:
            if tag in VALID_MODULES:
                tp_dim_count[tag] += 1

    result = {}
    all_mods = VALID_MODULES | set(obj_by_module.keys())
    for mod in sorted(all_mods):
        tp_cnt = tp_dim_count.get(mod, 0)
        obj_cnt = obj_by_module.get(mod, 0)
        cov = tp_cnt / obj_cnt if obj_cnt > 0 else None
        result[mod] = {
            "tp_count": tp_cnt,
            "obj_count": obj_cnt,
            "coverage": round(cov, 4) if cov is not None else None,
        }
    return result


def diff_warning(
    module_cov: dict, dim_cov: dict, threshold: float = 0.10
) -> list:
    """
    双轨差异告警。

    当 |module_cov - dim_cov| > threshold 时，输出 WEAK_OVERLAP 警告。
    返回警告列表。
    """
    warnings = []
    all_mods = set(module_cov.keys()) | set(dim_cov.keys())
    for mod in sorted(all_mods):
        m = module_cov.get(mod, {})
        d = dim_cov.get(mod, {})
        m_cov = m.get("coverage")
        d_cov = d.get("coverage")
        if m_cov is None or d_cov is None:
            continue
        diff = abs(m_cov - d_cov)
        if diff > threshold:
            warnings.append(
                {
                    "type": "WEAK_OVERLAP",
                    "module": mod,
                    "module_cov": m_cov,
                    "dim_cov": d_cov,
                    "diff": round(diff, 4),
                    "threshold": threshold,
                    "message": (
                        f"WEAK_OVERLAP: module={mod} "
                        f"module_coverage={m_cov:.2f}, "
                        f"dimension_coverage={d_cov:.2f}, "
                        f"diff={diff:.2f} > {threshold}"
                    ),
                }
            )
    return warnings


def run_dual_track(tp_path: str, obj_path: str, verbose: bool = False) -> dict:
    """主入口：加载文件 → 统计双轨 → 差异告警 → 返回结果 dict。"""
    tps_raw = load_json(tp_path)
    objs_raw = load_json(obj_path)

    # 兼容 S5 test_points.json 结构（顶层含 meta + test_points 数组）
    if isinstance(tps_raw, dict) and "test_points" in tps_raw:
        tps = tps_raw["test_points"]
    elif isinstance(tps_raw, list):
        tps = tps_raw
    else:
        raise ValueError(f"Unknown TP JSON structure: {tp_path}")

    # 兼容 S2 requirement_objects.json 结构
    if isinstance(objs_raw, dict):
        if "requirement_objects" in objs_raw:
            objs = objs_raw["requirement_objects"]
        elif "objects" in objs_raw:
            objs = objs_raw["objects"]
        else:
            objs = []
    elif isinstance(objs_raw, list):
        objs = objs_raw
    else:
        objs = []

    tps = normalize_tps(tps)
    module_cov = count_by_module(tps, objs)
    dim_cov = count_by_dimension(tps, objs)
    warnings = diff_warning(module_cov, dim_cov)

    result = {
        "module_coverage": module_cov,
        "dimension_coverage": dim_cov,
        "warnings": warnings,
        "summary": {
            "total_tp": len(tps),
            "total_obj": len(objs),
            "warn_count": len(warnings),
        },
    }

    if verbose:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


# ─────────────────────────────────────────────
# self-test
# ─────────────────────────────────────────────

def self_test() -> int:
    """5 个测试用例。退出码 0 = 全部通过。"""
    import tempfile, os

    # ─── Fixtures（独立 list，不共享引用）──────────────────────────────────
    # 最小 S2 OBJ fixture
    objs = [
        {"belong_module": "BIZ", "id": "OBJ-01"},
        {"belong_module": "BIZ", "id": "OBJ-02"},
        {"belong_module": "UI", "id": "OBJ-03"},
        {"belong_module": "UI", "id": "OBJ-04"},
    ]

    # TP fixture 1: BIZ TP 有 LOG tag → 维度轨道 BIZ tp_count=2
    tps_case1 = [
        {"tp_id": "TP-01", "module": "BIZ", "related_tags": ["BIZ", "LOG"]},
        {"tp_id": "TP-02", "module": "BIZ", "related_tags": ["BIZ"]},
        {"tp_id": "TP-03", "module": "UI", "related_tags": ["UI"]},
    ]
    tps_case1 = normalize_tps(tps_case1)

    # TP fixture 2: 旧 TP（无 related_tags → normalize_tps 补 []）
    tps_case2 = [
        {"tp_id": "TP-01", "module": "BIZ"},                        # → []
        {"tp_id": "TP-02", "module": "BIZ"},                        # → []
    ]
    tps_case2 = normalize_tps(tps_case2)

    # TP fixture 3: 跨模块 TP（验证维度轨道展开计数）
    # TP-01 → {BIZ, LOG, CONFIG}; TP-02 → {BIZ, LINK}; TP-03 → {UI, BIZ}
    # dim_coverage: BIZ=3(3个TP各含BIZ), LOG=1, CONFIG=1, LINK=1, UI=1
    tps_case3 = [
        {"tp_id": "TP-01", "module": "BIZ", "related_tags": ["BIZ", "LOG", "CONFIG"]},
        {"tp_id": "TP-02", "module": "BIZ", "related_tags": ["BIZ", "LINK"]},
        {"tp_id": "TP-03", "module": "UI", "related_tags": ["UI", "BIZ"]},
    ]
    tps_case3 = normalize_tps(tps_case3)

    # TP fixture 4: 空 OBJ（全部 0 分母 → coverage=None）
    tps_case4 = [{"tp_id": "TP-01", "module": "CONFIG", "related_tags": ["CONFIG"]}]
    tps_case4 = normalize_tps(tps_case4)
    objs_empty = []

    # TP fixture 5: WEAK_OVERLAP 触发
    # TP-01: module=BIZ, [BIZ]; TP-02: module=UI, [UI,BIZ,CONFIG,LINK,SPECIAL,HINT]
    #         TP-03: module=BIZ, [BIZ,CONFIG,LINK,SPECIAL,HINT]
    # objs_biz_only = 5 BIZ OBJ
    # → module_cov[BIZ] = 2/5 = 0.4; dim_cov[BIZ] = 3/5 = 0.6; diff = 0.2 > 0.10 ✓
    tps_case5 = [
        {"tp_id": "TP-01", "module": "BIZ", "related_tags": ["BIZ"]},
        {"tp_id": "TP-02", "module": "UI", "related_tags": ["UI", "BIZ", "CONFIG", "LINK", "SPECIAL", "HINT"]},
        {"tp_id": "TP-03", "module": "BIZ", "related_tags": ["BIZ", "CONFIG", "LINK", "SPECIAL", "HINT"]},
    ]
    tps_case5 = normalize_tps(tps_case5)
    objs_biz_only = [
        {"belong_module": "BIZ", "id": f"OBJ-{i:02d}"} for i in range(1, 6)
    ]

    cases = [
        ("主模块 + 维度统计", tps_case1, objs,
         lambda r: (
             r["module_coverage"]["BIZ"]["tp_count"] == 2
             and r["module_coverage"]["UI"]["tp_count"] == 1
             and r["dimension_coverage"]["BIZ"]["tp_count"] == 2   # 2条BIZ-TP含LOG → LOG=2
             and r["dimension_coverage"]["LOG"]["tp_count"] == 1   # TP-01含LOG
             and r["dimension_coverage"]["CONFIG"]["tp_count"] == 0
         )),
        ("旧TP兼容（无related_tags）", tps_case2, objs,
         lambda r: (
             r["module_coverage"]["BIZ"]["tp_count"] == 2
             and r["module_coverage"]["UI"]["tp_count"] == 0
             and r["dimension_coverage"]["BIZ"]["tp_count"] == 0  # [] → 无tag可计
             and len(r["warnings"]) == 1                         # |1.0-0.0|=1.0 → WEAK_OVERLAP
             and r["warnings"][0]["type"] == "WEAK_OVERLAP"
             and r["warnings"][0]["module"] == "BIZ"
             and r["warnings"][0]["diff"] > 0.10
         )),
        ("跨模块（3 tags）", tps_case3, objs,
         lambda r: (
             r["module_coverage"]["BIZ"]["tp_count"] == 2
             and r["dimension_coverage"]["BIZ"]["tp_count"] == 3  # 3个TP各含BIZ
             and r["dimension_coverage"]["LOG"]["tp_count"] == 1  # TP-01含LOG
             and r["dimension_coverage"]["CONFIG"]["tp_count"] == 1  # TP-01含CONFIG
             and r["dimension_coverage"]["LINK"]["tp_count"] == 1  # TP-02含LINK
             and r["dimension_coverage"]["UI"]["tp_count"] == 1   # TP-03含UI
         )),
        ("0分母（coverage=None）", tps_case4, objs_empty,
         lambda r: (
             r["module_coverage"]["CONFIG"]["coverage"] is None
             and r["summary"]["warn_count"] == 0
         )),
        ("WEAK_OVERLAP触发", tps_case5, objs_biz_only,
         lambda r: (
             len(r["warnings"]) == 1
             and r["warnings"][0]["type"] == "WEAK_OVERLAP"
             and r["warnings"][0]["module"] == "BIZ"
             and r["warnings"][0]["diff"] > 0.10
             and r["module_coverage"]["BIZ"]["tp_count"] == 2
             and r["dimension_coverage"]["BIZ"]["tp_count"] == 3
         )),
    ]

    passed = 0
    for name, tps, objs, check in cases:
        try:
            m = count_by_module(tps, objs)
            d = count_by_dimension(tps, objs)
            w = diff_warning(m, d)
            r = {"module_coverage": m, "dimension_coverage": d, "warnings": w, "summary": {"total_tp": len(tps), "total_obj": len(objs), "warn_count": len(w)}}
            if check(r):
                print(f"  ✅ {name}")
                passed += 1
            else:
                print(f"  ❌ {name}: check failed")
                print(f"     module_cov={m}")
                print(f"     dim_cov={d}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    print(f"\nself-test: {passed}/{len(cases)} passed")
    return 0 if passed == len(cases) else 1


# ─────────────────────────────────────────────
# __main__
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="双轨覆盖率统计（v16 T5）")
    parser.add_argument("tp_json", nargs="?", help="test_points.json 路径")
    parser.add_argument("obj_json", nargs="?", help="requirement_objects.json 路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--self-test", action="store_true", help="运行自我测试")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(self_test())

    if not args.tp_json or not args.obj_json:
        parser.print_help()
        print("\n示例：python3 ai_workflow/coverage_dual_track.py tp.json obj.json --json")
        sys.exit(2)

    result = run_dual_track(args.tp_json, args.obj_json, verbose=args.verbose)
    if not args.verbose:
        print(json.dumps(result, ensure_ascii=False, indent=2))
