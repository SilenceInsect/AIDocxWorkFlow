#!/usr/bin/env python3
"""AIDocxWorkFlow bypass_log 聚合器（v14 §5 第二阶段第三项）。

来源：
  - .cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc §2.4.1 + §4.3：
    BYPASS_EXCEPTION_RATE_WARNING = 0.20（🟡 黄）
    BYPASS_EXCEPTION_RATE_CRITICAL = 0.40（🔴 红）
  - .cursor/skills/aidocx-s7-review/SKILL.md §183-200：
    bypass_log 路径 + 3 统计维度（单项目/阶段/时间）

职责：
  1. 扫描 workflow_assets/<req_name>/<version>/「S{n} 阶段」/<version>/bypass_log.json
  2. 聚合 + 计算例外率
  3. 按 20%/40% 双阈值输出预警等级
  4. 写入 review_report.json 期望字段（供 S7 审查员消费）

调用：
  python3 scripts/bypass_log_aggregator.py <req_name> <version> [--output review_report_addon.json]
  python3 scripts/bypass_log_aggregator.py --self-test

退出码：
  0 = 绿色（例外率 ≤ 20%）
  1 = 黄色（20% < 例外率 ≤ 40%）
  2 = 红色（例外率 > 40%）
  3 = 无 bypass_log（不报错，输出空统计）
  4 = 参数错误
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# SSOT：DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3
WARNING_THRESHOLD = 0.20  # 🟡
CRITICAL_THRESHOLD = 0.40  # 🔴

# 项目根：scripts/ 在 governance/design_iter/scripts/ 或根目录 scripts/
_ROOT = Path(__file__).resolve().parents[2] if "design_iter" in str(Path(__file__).resolve()) else Path(__file__).resolve().parents[1]


def _find_workflow_assets(req_name: str, version: str) -> list[Path]:
    """找到所有阶段的 bypass_log.json 路径。"""
    req_dir = _ROOT / "workflow_assets" / req_name / version
    if not req_dir.exists():
        return []
    logs = []
    for stage_dir in req_dir.iterdir():
        if not stage_dir.is_dir():
            continue
        # 路径模式：<stage>/<version>/bypass_log.json
        version_bypass = stage_dir / version / "bypass_log.json"
        if version_bypass.exists():
            logs.append(version_bypass)
        # 也兼容：<stage>/bypass_log.json
        direct_bypass = stage_dir / "bypass_log.json"
        if direct_bypass.exists():
            logs.append(direct_bypass)
    return sorted(logs)


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _extract_stage(path: Path) -> str:
    """从路径提取阶段名（如「SS6 测试用例生成」→ 'S6'）。"""
    parts = path.parts
    for p in parts:
        if p.startswith("「") and "S" in p:
            # 「S6 测试用例生成」→ 提取 S6
            inside = p.strip("「」")
            for token in inside.split():
                if token.startswith("S") and token[1:].split(".")[0].isdigit():
                    return token.split(".")[0]
    return "UNKNOWN"


def aggregate(req_name: str, version: str) -> dict:
    """聚合所有阶段 bypass_log.json。"""
    bypass_logs = _find_workflow_assets(req_name, version)

    if not bypass_logs:
        return {
            "found": False,
            "warning_level": "GREEN",
            "exception_rate": 0.0,
            "stats": {
                "bypass_count": 0,
                "total_gates": 0,
                "by_stage": {},
                "by_gate": {},
                "by_priority": {},
                "logs_scanned": 0,
            },
        }

    total_bypass = 0
    total_gates = 0
    by_stage: dict[str, dict] = {}
    by_gate: dict[str, int] = {}
    by_priority: dict[str, int] = {}

    for log_path in bypass_logs:
        data = _load_json(log_path)
        stage = _extract_stage(log_path)

        # 解析 bypass_log.json（v14 格式：见 DESIGN_AND_EXECUTION_STANDARDS.mdc §2.4.1）
        entries = data.get("bypassed_gates", [])
        if not entries and "gates" in data:
            entries = data["gates"]

        stage_stats = by_stage.setdefault(
            stage,
            {"bypass_count": 0, "total_gates": 0, "logs": []},
        )

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            gate = entry.get("gate_name", "UNKNOWN")
            bypassed = entry.get("bypassed", entry.get("bypass", True))
            priority = entry.get("priority", "P1")

            stage_stats["total_gates"] += 1
            total_gates += 1
            by_gate[gate] = by_gate.get(gate, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

            if bypassed:
                stage_stats["bypass_count"] += 1
                total_bypass += 1

        stage_stats["logs"].append(str(log_path.relative_to(_ROOT)))

    exception_rate = total_bypass / total_gates if total_gates > 0 else 0.0
    if exception_rate > CRITICAL_THRESHOLD:
        warning_level = "RED"
    elif exception_rate > WARNING_THRESHOLD:
        warning_level = "YELLOW"
    else:
        warning_level = "GREEN"

    return {
        "found": True,
        "warning_level": warning_level,
        "exception_rate": round(exception_rate, 4),
        "stats": {
            "bypass_count": total_bypass,
            "total_gates": total_gates,
            "by_stage": by_stage,
            "by_gate": by_gate,
            "by_priority": by_priority,
            "logs_scanned": len(bypass_logs),
        },
    }


def self_test() -> int:
    """自测：3 case（无 bypass_log / 绿色 / 黄色 / 红色）。"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # 模拟项目根 + workflow_assets 结构
        req_dir = tmp / "workflow_assets" / "测试需求" / "v1.0" / "「S6 测试用例生成」" / "v1.0"
        req_dir.mkdir(parents=True)

        # Case 1: 无 bypass_log
        result = aggregate("测试需求", "v1.0")
        assert not result["found"], f"无 log 应 found=False: {result}"
        assert result["warning_level"] == "GREEN"

        # Case 2: 绿色（10 gates / 1 bypass = 10% < 20%）
        bypass_log = {
            "meta": {"req_name": "测试需求", "version": "v1.0", "stage": "S6"},
            "bypassed_gates": [
                {"gate_name": "S6_FIELD_COMPLETION_RATE", "bypassed": True, "priority": "P1"},
            ] + [
                {"gate_name": f"S6_GATE_{i}", "bypassed": False, "priority": "P1"}
                for i in range(9)
            ],
        }
        (req_dir / "bypass_log.json").write_text(
            json.dumps(bypass_log, ensure_ascii=False), encoding="utf-8"
        )
        # 重新跑聚合（需重置 _ROOT）
        import importlib
        # 由于 _ROOT 在模块加载时已确定，临时改目录不可行——简化：mock _ROOT
        original_root = bypass_log_aggregator_module_level_var()
        try:
            globals()["_ROOT"] = tmp
            result = aggregate("测试需求", "v1.0")
            assert result["found"]
            assert result["exception_rate"] == 0.1, f"应 10%: {result}"
            assert result["warning_level"] == "GREEN"
        finally:
            globals()["_ROOT"] = original_root

        # Case 3: 黄色（10 gates / 3 bypass = 30%）
        bypass_log_yellow = {
            "meta": {"req_name": "测试需求", "version": "v1.0", "stage": "S6"},
            "bypassed_gates": [
                {"gate_name": f"G_{i}", "bypassed": True, "priority": "P1"} for i in range(3)
            ] + [
                {"gate_name": f"G_{i}", "bypassed": False, "priority": "P1"} for i in range(3, 10)
            ],
        }
        (req_dir / "bypass_log.json").write_text(
            json.dumps(bypass_log_yellow, ensure_ascii=False), encoding="utf-8"
        )
        try:
            globals()["_ROOT"] = tmp
            result = aggregate("测试需求", "v1.0")
            assert result["exception_rate"] == 0.3
            assert result["warning_level"] == "YELLOW", f"30% 应 YELLOW: {result}"
        finally:
            globals()["_ROOT"] = original_root

        # Case 4: 红色（10 gates / 5 bypass = 50%）
        bypass_log_red = {
            "meta": {"req_name": "测试需求", "version": "v1.0", "stage": "S6"},
            "bypassed_gates": [
                {"gate_name": f"G_{i}", "bypassed": True, "priority": "P0"} for i in range(5)
            ] + [
                {"gate_name": f"G_{i}", "bypassed": False, "priority": "P1"} for i in range(5, 10)
            ],
        }
        (req_dir / "bypass_log.json").write_text(
            json.dumps(bypass_log_red, ensure_ascii=False), encoding="utf-8"
        )
        try:
            globals()["_ROOT"] = tmp
            result = aggregate("测试需求", "v1.0")
            assert result["exception_rate"] == 0.5
            assert result["warning_level"] == "RED", f"50% 应 RED: {result}"
        finally:
            globals()["_ROOT"] = original_root

    print("[self-test OK] 4 cases passed")
    return 0


def bypass_log_aggregator_module_level_var():
    """helper for self_test only — returns the module's _ROOT."""
    return _ROOT


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="bypass_log_aggregator",
        description="AIDocxWorkFlow bypass_log 聚合器（v14 §5 第二阶段）",
    )
    parser.add_argument("req_name", nargs="?", help="需求名称")
    parser.add_argument("version", nargs="?", help="版本号（如 v1.0）")
    parser.add_argument("--output", help="输出 JSON 路径（可选）")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.req_name or not args.version:
        print("[ERROR] 缺少 req_name / version 参数，或使用 --self-test", file=sys.stderr)
        return 4

    result = aggregate(args.req_name, args.version)
    result["meta"] = {
        "req_name": args.req_name,
        "version": args.version,
        "aggregated_at": datetime.now().isoformat(timespec="seconds"),
    }

    if args.output:
        Path(args.output).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        level_emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}.get(
            result["warning_level"], "⚪"
        )
        print("=" * 60)
        print(f"[bypass_log 聚合器 — v14 §5 第二阶段]")
        print("=" * 60)
        print(f"需求: {args.req_name} {args.version}")
        print(f"扫描 log 文件数: {result['stats']['logs_scanned']}")
        print(f"门禁总数: {result['stats']['total_gates']}")
        print(f"已 bypass 数: {result['stats']['bypass_count']}")
        print(f"例外率: {result['exception_rate']*100:.1f}%")
        print(f"预警等级: {level_emoji} {result['warning_level']}")
        print("-" * 60)
        if result["stats"]["by_stage"]:
            print("阶段分布:")
            for stage, s in result["stats"]["by_stage"].items():
                rate = s["bypass_count"] / s["total_gates"] if s["total_gates"] > 0 else 0
                print(f"  - {stage}: {s['bypass_count']}/{s['total_gates']} ({rate*100:.0f}%)")
        if result["stats"]["by_gate"]:
            print("Top bypass 门禁:")
            for gate, cnt in sorted(result["stats"]["by_gate"].items(), key=lambda x: -x[1])[:5]:
                print(f"  - {gate}: {cnt} 次")
        print("=" * 60)
        # 动作建议
        if result["warning_level"] == "GREEN":
            print("动作: 无需动作（健康）")
        elif result["warning_level"] == "YELLOW":
            print("动作: S7 审查员在 overall_assessment 输出「人工关注建议」")
        elif result["warning_level"] == "RED":
            print("动作: S7 审查员在 overall_assessment 输出「建议暂停，重新评估需求质量」")
        print("=" * 60)

    # 退出码按预警等级映射
    exit_map = {"GREEN": 0, "YELLOW": 1, "RED": 2}
    return exit_map.get(result["warning_level"], 3)


if __name__ == "__main__":
    sys.exit(main())