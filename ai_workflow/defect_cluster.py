#!/usr/bin/env python3
"""AIDocxWorkFlow 缺陷模式聚类器（v15 §5 阶段 1 主轴）。

来源：
  - v15 PLAN.md §附录 C（L3 技术方案）
  - .cursor/skills/aidocx-s7-review/SKILL.md §118-122（S7 RCA 三级字段）
    rca.stage / rca.type / rca.clause
  - bypass_log.json schema（DESIGN_AND_EXECUTION_STANDARDS.mdc §2.4.1）

数据源：
  - workflow_assets/<req_name>/<version>/「S7 用例审查」/review_report.json
  - workflow_assets/<req_name>/<version>/「S{n} 阶段」/<version>/bypass_log.json

聚类维度（v15 §附录 C）：
  - module × rca.type × rca.clause（来自 S7 SKILL.md §118-122 + DESIGN §4.3）

输出：
  - defect_mode_latest.json（最近 N 个项目 = N=1 默认，可 --window N 调整）
  - defect_mode_trend.json（跨项目趋势——需 ≥ 3 项目 bypass_log 才输出）

调用：
  python3 ai_workflow/defect_cluster.py <req_name> [--window N] [--output-dir <dir>]
  python3 ai_workflow/defect_cluster.py --self-test

退出码：
  0 = 成功（含警告——如数据不足）
  1 = 错误（文件不存在 / JSON 解析失败）
  2 = 参数错误
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# S7 RCA 二级 type 枚举（S7 SKILL.md §120）
RCA_TYPES = {
    "OMISSION",
    "BOUNDARY_ERR",
    "QUALITY_LOW",
    "FIELD_MISSING",
    "LINKAGE_BROKEN",
    "RULE_VIOLATION",
    "ID_NONCOMPLIANT",
}

# S7 RCA 一级 stage 枚举（S7 SKILL.md §119）
RCA_STAGES = {"S1", "S2", "S4", "S5", "S6"}

# 8 模块（与 MODULES.md §1 一致）
VALID_MODULES = {"CONFIG", "UI", "BIZ", "AUX", "LINK", "LOG", "SPECIAL", "HINT"}

# 项目根
_ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[WARN] JSON 解析失败 {path}: {e}", file=sys.stderr)
        return None


def _find_review_reports(req_name: str, window: int = 1) -> list[Path]:
    """找最近 N 个版本的 review_report.json（按版本目录名排序后取末尾 N 个）。"""
    req_dir = _ROOT / "workflow_assets" / req_name
    if not req_dir.exists():
        return []
    version_dirs = sorted([d for d in req_dir.iterdir() if d.is_dir()])
    recent = version_dirs[-window:] if window > 0 else version_dirs
    reports = []
    for vd in recent:
        # 路径模式：<version>/「S7 用例审查」/review_report.json
        s7_dir = vd / "「S7 用例审查」"
        if s7_dir.exists():
            rp = s7_dir / "review_report.json"
            if rp.exists():
                reports.append(rp)
        # 兼容 v1 路径：<version>/「S6 测试用例生成」/review_report.json
        s6_dir = vd / "「S6 测试用例生成」"
        if s6_dir.exists():
            rp = s6_dir / "review_report.json"
            if rp.exists():
                reports.append(rp)
    return reports


def _find_bypass_logs(req_name: str, window: int = 1) -> list[Path]:
    """找最近 N 个版本所有阶段的 bypass_log.json。"""
    req_dir = _ROOT / "workflow_assets" / req_name
    if not req_dir.exists():
        return []
    version_dirs = sorted([d for d in req_dir.iterdir() if d.is_dir()])
    recent = version_dirs[-window:] if window > 0 else version_dirs
    logs = []
    for vd in recent:
        for stage_dir in vd.iterdir():
            if not stage_dir.is_dir():
                continue
            # 路径模式 1：<stage>/<version>/bypass_log.json
            version_log = stage_dir / vd.name / "bypass_log.json"
            if version_log.exists():
                logs.append(version_log)
            # 路径模式 2：<stage>/bypass_log.json
            direct_log = stage_dir / "bypass_log.json"
            if direct_log.exists():
                logs.append(direct_log)
    return sorted(set(logs))


def _extract_rca_entries(report: dict) -> list[dict]:
    """从 review_report.json 抽取所有 recommendations[] 里的 rca 字段。"""
    entries = []
    recs = report.get("recommendations", [])
    if not isinstance(recs, list):
        return entries
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        rca = rec.get("rca")
        if not isinstance(rca, dict):
            continue
        # 校验必填字段
        stage = rca.get("stage", "")
        rtype = rca.get("type", "")
        clause = rca.get("clause", "")
        if stage not in RCA_STAGES:
            continue
        if rtype not in RCA_TYPES:
            continue
        if not clause:
            continue
        entries.append({
            "module": rec.get("module", "UNKNOWN"),
            "stage": stage,
            "type": rtype,
            "clause": clause,
            "explanation": rca.get("explanation", ""),
            "must_fix": rec.get("suggestion_type") == "must_fix",
            "should_fix": rec.get("suggestion_type") == "should_fix",
        })
    return entries


def _extract_bypass_gates(log: dict) -> list[dict]:
    """从 bypass_log.json 抽取被 bypass 的门禁条目。"""
    entries = []
    bypassed = log.get("bypassed_gates", [])
    if not isinstance(bypassed, list):
        bypassed = log.get("gates", [])
    for entry in bypassed:
        if not isinstance(entry, dict):
            continue
        is_bypassed = entry.get("bypassed", entry.get("bypass", False))
        if is_bypassed:
            entries.append({
                "gate_name": entry.get("gate_name", "UNKNOWN"),
                "priority": entry.get("priority", "P1"),
                "stage": log.get("meta", {}).get("stage", "UNKNOWN"),
                "reason": entry.get("bypass_reason", ""),
            })
    return entries


def _cluster(entries: list[dict]) -> dict:
    """按 module × type × clause 三维聚类 + 频次统计。"""
    # 三维分组
    by_module_type_clause: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    # 边缘统计
    module_counter: Counter = Counter()
    type_counter: Counter = Counter()
    clause_counter: Counter = Counter()
    for e in entries:
        key = (e.get("module", "UNKNOWN"), e.get("type", "UNKNOWN"), e.get("clause", "UNKNOWN"))
        by_module_type_clause[key].append(e)
        module_counter[key[0]] += 1
        type_counter[key[1]] += 1
        clause_counter[key[2]] += 1

    clusters = []
    for (mod, typ, cl), items in sorted(by_module_type_clause.items(), key=lambda x: -len(x[1])):
        clusters.append({
            "module": mod,
            "type": typ,
            "clause": cl,
            "count": len(items),
            "must_fix_count": sum(1 for i in items if i.get("must_fix")),
            "sample_explanation": items[0].get("explanation", "")[:80] if items else "",
        })

    return {
        "total_entries": len(entries),
        "cluster_count": len(clusters),
        "by_module": dict(module_counter.most_common()),
        "by_type": dict(type_counter.most_common()),
        "by_clause": dict(clause_counter.most_common(10)),
        "top_clusters": clusters[:10],
    }


def cluster_project(req_name: str, window: int = 1) -> dict:
    """主入口：聚类一个项目（跨 N 版本）。"""
    reports = _find_review_reports(req_name, window)
    bypass_logs = _find_bypass_logs(req_name, window)

    rca_entries: list[dict] = []
    for rp in reports:
        data = _load_json(rp)
        if isinstance(data, dict):
            rca_entries.extend(_extract_rca_entries(data))

    bypass_entries: list[dict] = []
    for lp in bypass_logs:
        data = _load_json(lp)
        if isinstance(data, dict):
            bypass_entries.extend(_extract_bypass_gates(data))

    # RCA + bypass 合并（统一成 entries）
    all_entries = rca_entries + bypass_entries

    result = {
        "meta": {
            "req_name": req_name,
            "window": window,
            "aggregated_at": datetime.now().isoformat(timespec="seconds"),
            "reports_scanned": len(reports),
            "bypass_logs_scanned": len(bypass_logs),
            "rca_entries": len(rca_entries),
            "bypass_entries": len(bypass_entries),
            "total_entries": len(all_entries),
        },
        "cluster": _cluster(all_entries),
        "data_status": "OK" if all_entries else "EMPTY",
    }

    # 跨项目趋势判断（≥ 3 项目 bypass_log）
    if len(bypass_logs) >= 3:
        result["trend_available"] = True
        result["trend_note"] = f"已扫描 {len(bypass_logs)} 个 bypass_log，足够生成 defect_mode_trend.json"
    else:
        result["trend_available"] = False
        result["trend_note"] = f"仅 {len(bypass_logs)} 个 bypass_log（需 ≥ 3 才能生成 trend）——推迟到 v16"

    return result


def self_test() -> int:
    """自测：5 cases（空数据 / RCA / bypass / 合并 / 趋势可用）。"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 模拟项目结构
        req_dir = tmp / "workflow_assets" / "测试需求" / "v1.0"
        s7_dir = req_dir / "「S7 用例审查」"
        s6_dir = req_dir / "「S6 测试用例生成」"
        bypass_dir = req_dir / "「S6 测试用例生成」" / "v1.0"
        s7_dir.mkdir(parents=True)
        s6_dir.mkdir(parents=True)
        bypass_dir.mkdir(parents=True)

        # Case 1: 空数据 → EMPTY status
        try:
            globals()["_ROOT"] = tmp
            result = cluster_project("测试需求", window=1)
            assert result["data_status"] == "EMPTY"
            assert result["cluster"]["total_entries"] == 0
        finally:
            globals()["_ROOT"] = _ROOT

        # Case 2: RCA only
        report = {
            "recommendations": [
                {
                    "suggestion_type": "must_fix",
                    "module": "UI",
                    "rca": {
                        "stage": "S5",
                        "type": "BOUNDARY_ERR",
                        "clause": "SKILL.S5.§1.4",
                        "explanation": "测试用例缺边界场景",
                    },
                },
                {
                    "suggestion_type": "should_fix",
                    "module": "BIZ",
                    "rca": {
                        "stage": "S6",
                        "type": "FIELD_MISSING",
                        "clause": "SKILL.S6.§1.6",
                        "explanation": "字段未填",
                    },
                },
            ]
        }
        (s7_dir / "review_report.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )
        try:
            globals()["_ROOT"] = tmp
            result = cluster_project("测试需求", window=1)
            assert result["data_status"] == "OK"
            assert result["cluster"]["total_entries"] == 2
            assert result["cluster"]["by_module"]["UI"] == 1
            assert result["cluster"]["by_type"]["BOUNDARY_ERR"] == 1
        finally:
            globals()["_ROOT"] = _ROOT

        # Case 3: bypass_log only
        bypass_log = {
            "meta": {"stage": "S6"},
            "bypassed_gates": [
                {
                    "gate_name": "S6_FIELD_COMPLETION_RATE",
                    "priority": "P1",
                    "bypassed": True,
                    "bypass_reason": "业务实际",
                },
            ],
        }
        (bypass_dir / "bypass_log.json").write_text(
            json.dumps(bypass_log, ensure_ascii=False), encoding="utf-8"
        )
        try:
            globals()["_ROOT"] = tmp
            result = cluster_project("测试需求", window=1)
            assert result["meta"]["bypass_entries"] == 1
        finally:
            globals()["_ROOT"] = _ROOT

        # Case 4: 合并 RCA + bypass
        try:
            globals()["_ROOT"] = tmp
            result = cluster_project("测试需求", window=1)
            assert result["meta"]["rca_entries"] == 2
            assert result["meta"]["bypass_entries"] == 1
            assert result["cluster"]["total_entries"] == 3
        finally:
            globals()["_ROOT"] = _ROOT

        # Case 5: 趋势判断（< 3 bypass_log）
        try:
            globals()["_ROOT"] = tmp
            result = cluster_project("测试需求", window=1)
            assert not result["trend_available"]
            assert "≥ 3" in result["trend_note"]
        finally:
            globals()["_ROOT"] = _ROOT

    print("[self-test OK] 5 cases passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="defect_cluster",
        description="AIDocxWorkFlow 缺陷模式聚类器（v15 §5 阶段 1）",
    )
    parser.add_argument("req_name", nargs="?", help="需求名称")
    parser.add_argument("--window", type=int, default=1, help="跨最近 N 个版本聚类（默认 1）")
    parser.add_argument("--output-dir", help="输出目录（默认 workflow_assets/<req>/）")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.req_name:
        print("[ERROR] 缺少 req_name 参数，或使用 --self-test", file=sys.stderr)
        return 2

    result = cluster_project(args.req_name, window=args.window)

    # 输出文件
    output_dir = Path(args.output_dir) if args.output_dir else (
        _ROOT / "workflow_assets" / args.req_name
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_path = output_dir / "defect_mode_latest.json"
    latest_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if result["trend_available"]:
        trend_path = output_dir / "defect_mode_trend.json"
        trend_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        m = result["meta"]
        c = result["cluster"]
        print("=" * 60)
        print(f"[缺陷模式聚类器 — v15 §5 阶段 1]")
        print("=" * 60)
        print(f"需求: {args.req_name} | 窗口: 最近 {args.window} 个版本")
        print(f"扫描 review_report: {m['reports_scanned']} | bypass_log: {m['bypass_logs_scanned']}")
        print(f"RCA 条目: {m['rca_entries']} | bypass 条目: {m['bypass_entries']}")
        print(f"总条目: {m['total_entries']} | 数据状态: {result['data_status']}")
        print("-" * 60)
        if c["by_module"]:
            print("Top modules:")
            for mod, cnt in list(c["by_module"].items())[:5]:
                print(f"  - {mod}: {cnt}")
        if c["by_type"]:
            print("Top types:")
            for typ, cnt in list(c["by_type"].items())[:5]:
                print(f"  - {typ}: {cnt}")
        if c["top_clusters"]:
            print("Top 3 clusters (module × type × clause):")
            for cl in c["top_clusters"][:3]:
                print(f"  - {cl['module']} × {cl['type']} × {cl['clause']}: {cl['count']} 次")
        print("-" * 60)
        print(f"trend_available: {result['trend_available']}")
        print(f"trend_note: {result['trend_note']}")
        print("-" * 60)
        print(f"输出: {latest_path}")
        if result["trend_available"]:
            print(f"      {(output_dir / 'defect_mode_trend.json')}")
        print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())