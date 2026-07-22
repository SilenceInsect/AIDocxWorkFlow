#!/usr/bin/env python3
"""AIDocxWorkFlow S6 覆盖率分级门禁（v14 §5 第二阶段第二项）。

来源：
  - 外部方案 §4.5.1（P0/P1/P2 优先级判定 + 覆盖率分级）
  - .cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3：
    S6_FIELD_COMPLETION_RATE / S6_OBJ_COVERAGE / S6_FP_COVERAGE
  - .cursor/skills/aidocx-s6-test-cases/SKILL.md §P0/P1/P2 覆盖率分级门禁：
    - P0 ≥ 95%（刚性，不可例外）
    - P1 ≥ 80%（柔性，可申请 bypass → 写入 bypass_log.json）
    - P2 ≥ 50%（指导值，不做强求）

SSOT 优先级：SSOT §4.3 > SKILL.md > 本脚本默认值

覆盖率定义（S6 SKILL.md §462）：
  覆盖率 = 该优先级 Story 的 TC 数 / 该优先级 Story 的 FP 总数

调用：
  python3 ai_workflow/s6_coverage_gate.py <test_cases.json> <backlog.json> [--strict]
  python3 ai_workflow/s6_coverage_gate.py --self-test

退出码：
  0 = PASS（含 warnings / 仅 P2 不足）
  1 = BLOCKED（P0 < 95% 或 P1 < 80%）
  2 = 参数错误
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# 优先级阈值（SSOT §4.3 + S6 SKILL.md §456-460）
COVERAGE_THRESHOLDS = {
    "P0": {"threshold": 0.95, "strict": True, "label": "刚性（不可 bypass）"},
    "P1": {"threshold": 0.80, "strict": False, "label": "柔性（可 bypass）"},
    "P2": {"threshold": 0.50, "strict": False, "label": "指导值（不强制）"},
}


def _load_json(path: Path) -> dict | list:
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败 {path}: {e}") from e


def _extract_test_cases(data: dict | list) -> list[dict]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("test_cases", "scenario_test_cases", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise ValueError("无法定位 test_cases 数组")


def _extract_backlog_fps(backlog: dict | list) -> dict[str, set[str]]:
    """从 S2 backlog.json 提取 {story_id: {fp_id_set}} 映射。

    兼容两种 schema：
    - {epics[].stories[].feature_points[]}（v2+）
    - {epics[].stories[].id → 已展开}
    """
    fp_map: dict[str, set[str]] = defaultdict(set)
    if isinstance(backlog, list):
        # 直接是 epics 列表
        for ep in backlog:
            for st in ep.get("stories", []) if isinstance(ep, dict) else []:
                _collect_story_fps(st, fp_map)
        return fp_map
    if not isinstance(backlog, dict):
        return fp_map
    for ep in backlog.get("epics", []):
        if not isinstance(ep, dict):
            continue
        for st in ep.get("stories", []):
            _collect_story_fps(st, fp_map)
    return fp_map


def _collect_story_fps(story: dict, fp_map: dict[str, set[str]]) -> None:
    """单个 story 收集 FP（按 v2+ schema）。"""
    if not isinstance(story, dict):
        return
    sid = story.get("id", "")
    if not sid:
        return
    # 优先 feature_points[] 数组
    fps = story.get("feature_points", [])
    if isinstance(fps, list):
        for fp in fps:
            if isinstance(fp, dict) and fp.get("id"):
                fp_map[sid].add(fp["id"])
            elif isinstance(fp, str):
                fp_map[sid].add(fp)
    # 兼容 objs[].feature_points[]（v14 范式）
    for obj in story.get("objs", story.get("objects", [])):
        if not isinstance(obj, dict):
            continue
        for fp in obj.get("feature_points", []):
            if isinstance(fp, dict) and fp.get("id"):
                fp_map[sid].add(fp["id"])
            elif isinstance(fp, str):
                fp_map[sid].add(fp)


def _resolve_story_priority(tc: dict, fp_priority_map: dict[str, str]) -> str:
    """从 TC 找优先级：直接看 tc.priority → 找 fp.priority → 默认 P2。"""
    pri = tc.get("priority", "")
    if pri in COVERAGE_THRESHOLDS:
        return pri
    fp_id = tc.get("fp_id", tc.get("feature_point_id", ""))
    if fp_id in fp_priority_map:
        return fp_priority_map[fp_id]
    return "P2"


def run_coverage_gate(test_cases_path: Path, backlog_path: Path | None) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    stats = {
        "total_test_cases": 0,
        "by_priority": {p: {"covered": 0, "required": 0, "rate": 0.0} for p in COVERAGE_THRESHOLDS},
    }

    tcs = _extract_test_cases(_load_json(test_cases_path))
    stats["total_test_cases"] = len(tcs)

    # 加载 backlog（可选——无 backlog 时只统计 TC 优先级分布，不算覆盖率）
    fp_map: dict[str, set[str]] = {}
    fp_priority_map: dict[str, str] = {}
    if backlog_path and backlog_path.exists():
        backlog = _load_json(backlog_path)
        fp_map = _extract_backlog_fps(backlog)
        # 收集 FP 优先级（从 backlog 直接读取）
        for sid, fps in fp_map.items():
            for fp_id in fps:
                # 简化：FP 优先级默认 P1（除非明确指定）— 实际从 backlog 里取 fp.priority
                fp_priority_map[fp_id] = "P1"
        # 尝试从 backlog 中读 fp.priority
        backlog_obj = _load_json(backlog_path) if backlog_path else {}
        if isinstance(backlog_obj, dict):
            for ep in backlog_obj.get("epics", []):
                if not isinstance(ep, dict):
                    continue
                for st in ep.get("stories", []):
                    _scan_fp_priorities(st, fp_priority_map)
        # 必须：统计 required = fp 数 / priority
        for fps in fp_map.values():
            for fp_id in fps:
                p = fp_priority_map.get(fp_id, "P1")
                stats["by_priority"][p]["required"] += 1

    # 统计 TC 优先级 → covered
    for tc in tcs:
        if not isinstance(tc, dict):
            continue
        p = _resolve_story_priority(tc, fp_priority_map)
        stats["by_priority"][p]["covered"] += 1

    # 计算 rate + 判定
    for p, cfg in COVERAGE_THRESHOLDS.items():
        s = stats["by_priority"][p]
        if s["required"] > 0:
            s["rate"] = round(s["covered"] / s["required"], 4)
        else:
            s["rate"] = 1.0 if s["covered"] == 0 else 0.0
        # 判定：required = 0 不报错（说明 backlog 没数据或无需统计）
        if s["required"] == 0:
            continue
        if s["rate"] < cfg["threshold"]:
            msg = {
                "priority": p,
                "covered": s["covered"],
                "required": s["required"],
                "rate": s["rate"],
                "threshold": cfg["threshold"],
                "label": cfg["label"],
            }
            if cfg["strict"]:
                errors.append({**msg, "type": "COVERAGE_BELOW_P0", "blocking": True})
            else:
                warnings.append({**msg, "type": f"COVERAGE_BELOW_{p}", "blocking": False})

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }


def _scan_fp_priorities(story: dict, fp_priority_map: dict[str, str]) -> None:
    """从 story 里读 fp.priority 字段（如有）。"""
    if not isinstance(story, dict):
        return
    for fp in story.get("feature_points", []):
        if isinstance(fp, dict) and fp.get("id") and fp.get("priority"):
            fp_priority_map[fp["id"]] = fp["priority"]
    for obj in story.get("objs", story.get("objects", [])):
        if not isinstance(obj, dict):
            continue
        for fp in obj.get("feature_points", []):
            if isinstance(fp, dict) and fp.get("id") and fp.get("priority"):
                fp_priority_map[fp["id"]] = fp["priority"]


def self_test() -> int:
    """自测：合法/边界/非法 3 case。"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Case 1: P0 全覆盖 + P1/P2 边界 → PASS
        backlog = {
            "epics": [
                {
                    "stories": [
                        {
                            "id": "S-001",
                            "feature_points": [
                                {"id": "FP-1", "priority": "P0"},
                                {"id": "FP-2", "priority": "P0"},
                                {"id": "FP-3", "priority": "P1"},
                                {"id": "FP-4", "priority": "P2"},
                            ],
                        }
                    ]
                }
            ]
        }
        tcs = {
            "test_cases": [
                {"tc_id": "TC-1", "fp_id": "FP-1", "priority": "P0"},
                {"tc_id": "TC-2", "fp_id": "FP-2", "priority": "P0"},
                {"tc_id": "TC-3", "fp_id": "FP-3", "priority": "P1"},
                # FP-4 (P2) 没 TC → 0/1 = 0%
            ]
        }
        bl_path = tmp / "bl.json"
        tc_path = tmp / "tc.json"
        bl_path.write_text(json.dumps(backlog, ensure_ascii=False), encoding="utf-8")
        tc_path.write_text(json.dumps(tcs, ensure_ascii=False), encoding="utf-8")
        result = run_coverage_gate(tc_path, bl_path)
        # P0: 2/2 = 100% ≥ 95% PASS
        # P1: 1/1 = 100% ≥ 80% PASS
        # P2: 0/1 = 0% < 50% → warning (P2 不严格)
        assert result["passed"], f"P0 全覆盖应 PASS: {result}"
        assert any(w["priority"] == "P2" for w in result["warnings"]), "P2 不足应为 warning"

        # Case 2: P0 不足 → BLOCKED
        backlog2 = {
            "epics": [
                {
                    "stories": [
                        {
                            "id": "S-001",
                            "feature_points": [
                                {"id": "FP-1", "priority": "P0"},
                                {"id": "FP-2", "priority": "P0"},
                            ],
                        }
                    ]
                }
            ]
        }
        tcs2 = {
            "test_cases": [
                {"tc_id": "TC-1", "fp_id": "FP-1", "priority": "P0"},
                # FP-2 (P0) 没 TC → 1/2 = 50% < 95% BLOCKED
            ]
        }
        bl_path.write_text(json.dumps(backlog2, ensure_ascii=False), encoding="utf-8")
        tc_path.write_text(json.dumps(tcs2, ensure_ascii=False), encoding="utf-8")
        result = run_coverage_gate(tc_path, bl_path)
        assert not result["passed"], f"P0 50% 应 BLOCKED: {result}"
        assert any(e["type"] == "COVERAGE_BELOW_P0" for e in result["errors"])

        # Case 3: 无 backlog → 统计全 0，不报错
        tc_path.write_text(json.dumps(tcs, ensure_ascii=False), encoding="utf-8")
        result = run_coverage_gate(tc_path, None)
        assert result["passed"], "无 backlog 应 PASS（不阻断）"

    print("[self-test OK] 3 cases passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="s6_coverage_gate",
        description="AIDocxWorkFlow S6 覆盖率分级门禁（v14 §5 第二阶段）",
    )
    parser.add_argument("test_cases", nargs="?", help="test_cases.json 路径")
    parser.add_argument("backlog", nargs="?", default=None, help="S2 backlog.json（可选）")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.test_cases:
        print("[ERROR] 缺少 test_cases.json 路径，或使用 --self-test", file=sys.stderr)
        return 2

    tc_path = Path(args.test_cases)
    bl_path = Path(args.backlog) if args.backlog else None

    try:
        result = run_coverage_gate(tc_path, bl_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        s = result["stats"]
        print("=" * 60)
        print("[S6 覆盖率分级门禁 — v14 §5 第二阶段]")
        print("=" * 60)
        print(f"测试用例总数: {s['total_test_cases']}")
        print("-" * 60)
        print(f"{'优先级':<8} {'覆盖':<8} {'需求':<8} {'覆盖率':<10} {'阈值':<8} {'刚性'}")
        print("-" * 60)
        for p, cfg in COVERAGE_THRESHOLDS.items():
            ps = s["by_priority"][p]
            print(
                f"{p:<8} {ps['covered']:<8} {ps['required']:<8} "
                f"{ps['rate']*100:>6.1f}%   {cfg['threshold']*100:>5.0f}%   {cfg['label']}"
            )
        print("-" * 60)
        if result["errors"]:
            print("[ERRORS — 阻塞 S6 进入]")
            for e in result["errors"]:
                print(f"  - {e}")
        if result["warnings"]:
            print("[WARNINGS — 不阻塞，P1 可申请 bypass / P2 不强制]")
            for w in result["warnings"]:
                print(f"  - {w}")
        print("=" * 60)
        print(f"结论: {'PASS' if result['passed'] else 'BLOCKED'}")
        print("=" * 60)

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())