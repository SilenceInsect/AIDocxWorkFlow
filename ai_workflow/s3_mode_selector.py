#!/usr/bin/env python3
"""AIDocxWorkFlow S3 路径选择器（v15 §5 阶段 2 POC — A1 决策树逻辑脚本化）。

来源：
  - v15/PLAN.md §附录 A（增强路径论证）
  - v15/A1_enhanced_path_feasibility.md §3（触发决策树方案 2）

性质标注（v15 修正）：
  **A1 是 LLM 决策辅助，不强制。**
  触发条件（ui_ratio / priority / story 数）已由 S2 backlog 直接提供，
  本脚本仅将规则脚本化，供 Agent 参考。S3 实际产出模式由 LLM
  结合 backlog 字段 + 业务实际自主判断。

职责：
  输入 backlog.json（ui_ratio + P0/P1/P2 优先级 + Story 数 + 跨模块数）
  输出 s3_mode_recommend（lightweight / standard / depth）+ 触发原因

边界（POC 模式）：
  - 仅实现决策树逻辑验证，不改 S3 实际产出
  - 真实需求触发由 v16 阶段 1 数据驱动

调用：
  python3 ai_workflow/s3_mode_selector.py <backlog.json> [--json]
  python3 ai_workflow/s3_mode_selector.py --self-test

退出码：
  0 = 成功
  1 = 文件不存在或 JSON 解析失败
  2 = 参数错误
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# v15/A1 §3.2 强制规则
UI_RATIO_STANDARD_THRESHOLD = 0.30
UI_RATIO_DEPTH_THRESHOLD = 0.50
MIN_STORIES_FOR_LIGHTWEIGHT = 3
CROSS_MODULE_THRESHOLD = 3
P0_RATIO_FORCE_DEPTH = 0.0  # 任一 P0 → 强制 depth


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析失败 {path}: {e}", file=sys.stderr)
        return None


def _calc_metrics(backlog: dict) -> dict:
    """从 backlog 提取 ui_ratio / priority / Story 数 / 模块数。

    兼容 v2+ schema（epics[].stories[]）和 flat list。
    """
    stories: list[dict] = []
    cross_modules: set[str] = set()
    if isinstance(backlog, list):
        for ep in backlog:
            if isinstance(ep, dict):
                for st in ep.get("stories", []):
                    if isinstance(st, dict):
                        stories.append(st)
    elif isinstance(backlog, dict):
        for ep in backlog.get("epics", []):
            if isinstance(ep, dict):
                for st in ep.get("stories", []):
                    if isinstance(st, dict):
                        stories.append(st)
                        # 收集模块
                        for obj in st.get("objs", st.get("objects", [])):
                            if isinstance(obj, dict):
                                mod = obj.get("module")
                                if mod:
                                    cross_modules.add(mod)

    total = len(stories)
    if total == 0:
        return {
            "total_stories": 0,
            "ui_stories": 0,
            "ui_ratio": 0.0,
            "p0_count": 0,
            "p0_ratio": 0.0,
            "cross_module_count": len(cross_modules),
        }

    ui_count = sum(1 for st in stories if st.get("module") == "UI" or any(
        obj.get("module") == "UI" for obj in st.get("objs", st.get("objects", []))
        if isinstance(obj, dict)
    ))
    p0_count = sum(1 for st in stories if st.get("priority") == "P0")

    return {
        "total_stories": total,
        "ui_stories": ui_count,
        "ui_ratio": round(ui_count / total, 4),
        "p0_count": p0_count,
        "p0_ratio": round(p0_count / total, 4),
        "cross_module_count": len(cross_modules),
    }


def recommend_mode(metrics: dict) -> dict:
    """v15/A1 §3.1 决策树（方案 2：风险等级优先）。

    规则：
      1. 任一 P0 → depth（强制）
      2. 跨 ≥ 3 模块 → standard（强制）
      3. Story 数 ≤ 3 且无 UI → lightweight（强制）
      4. P1 → standard (UI > 0.30) / lightweight (UI ≤ 0.30)
      5. P2 → standard (UI > 0.50) / lightweight (UI ≤ 0.50)
    """
    reasons: list[str] = []
    p0_count = metrics["p0_count"]
    p0_ratio = metrics["p0_ratio"]
    ui_ratio = metrics["ui_ratio"]
    total = metrics["total_stories"]
    cross = metrics["cross_module_count"]
    ui_count = metrics["ui_stories"]

    # 规则 1：P0 强制 depth
    if p0_count > 0:
        reasons.append(f"强制深度版：P0 Story 数 = {p0_count}（任一 P0 触发）")
        return {"mode": "depth", "reasons": reasons}

    # 规则 2：跨 ≥ 3 模块强制 standard
    if cross >= CROSS_MODULE_THRESHOLD:
        reasons.append(f"强制标准版：跨模块数 = {cross} ≥ {CROSS_MODULE_THRESHOLD}")
        return {"mode": "standard", "reasons": reasons}

    # 规则 3：Story 数 ≤ 3 且无 UI
    if total <= MIN_STORIES_FOR_LIGHTWEIGHT and ui_count == 0:
        reasons.append(f"强制轻量版：Story 数 = {total} ≤ {MIN_STORIES_FOR_LIGHTWEIGHT} 且无 UI")
        return {"mode": "lightweight", "reasons": reasons}

    # 默认按 P1/P2 + UI ratio 决策（v15/A1 §3.1）
    if ui_ratio > UI_RATIO_DEPTH_THRESHOLD:
        reasons.append(f"UI ratio = {ui_ratio} > {UI_RATIO_DEPTH_THRESHOLD} → 标准版")
        return {"mode": "standard", "reasons": reasons}
    if ui_ratio > UI_RATIO_STANDARD_THRESHOLD:
        reasons.append(f"UI ratio = {ui_ratio} > {UI_RATIO_STANDARD_THRESHOLD} → 标准版")
        return {"mode": "standard", "reasons": reasons}

    reasons.append(
        f"UI ratio = {ui_ratio} ≤ {UI_RATIO_STANDARD_THRESHOLD} + 无 P0 → 轻量版"
    )
    return {"mode": "lightweight", "reasons": reasons}


def self_test() -> int:
    """自测：5 cases 覆盖决策树所有分支。"""
    # Case 1: P0 触发 → depth
    m1 = {"total_stories": 10, "ui_stories": 3, "ui_ratio": 0.3, "p0_count": 1, "p0_ratio": 0.1, "cross_module_count": 1}
    r1 = recommend_mode(m1)
    assert r1["mode"] == "depth", f"P0 应 depth: {r1}"
    assert "强制深度版" in r1["reasons"][0]

    # Case 2: 跨 ≥ 3 模块 → standard（即使无 P0）
    m2 = {"total_stories": 5, "ui_stories": 1, "ui_ratio": 0.2, "p0_count": 0, "p0_ratio": 0.0, "cross_module_count": 4}
    r2 = recommend_mode(m2)
    assert r2["mode"] == "standard", f"跨 ≥ 3 模块应 standard: {r2}"
    assert "跨模块" in r2["reasons"][0]

    # Case 3: Story ≤ 3 + 无 UI → lightweight
    m3 = {"total_stories": 2, "ui_stories": 0, "ui_ratio": 0.0, "p0_count": 0, "p0_ratio": 0.0, "cross_module_count": 1}
    r3 = recommend_mode(m3)
    assert r3["mode"] == "lightweight", f"小需求应 lightweight: {r3}"
    assert "Story 数" in r3["reasons"][0]

    # Case 4: UI > 0.30 → standard
    m4 = {"total_stories": 10, "ui_stories": 4, "ui_ratio": 0.4, "p0_count": 0, "p0_ratio": 0.0, "cross_module_count": 1}
    r4 = recommend_mode(m4)
    assert r4["mode"] == "standard", f"UI > 0.30 应 standard: {r4}"

    # Case 5: UI ≤ 0.30 → lightweight
    m5 = {"total_stories": 10, "ui_stories": 2, "ui_ratio": 0.2, "p0_count": 0, "p0_ratio": 0.0, "cross_module_count": 1}
    r5 = recommend_mode(m5)
    assert r5["mode"] == "lightweight", f"UI ≤ 0.30 应 lightweight: {r5}"

    print("[self-test OK] 5 cases passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="s3_mode_selector",
        description="A1 POC — S3 路径选择器（决策树方案 2）",
    )
    parser.add_argument("backlog", nargs="?", help="backlog.json 路径")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.backlog:
        print("[ERROR] 缺少 backlog.json 路径，或使用 --self-test", file=sys.stderr)
        return 2

    path = Path(args.backlog)
    data = _load_json(path)
    if data is None:
        return 1

    metrics = _calc_metrics(data)
    rec = recommend_mode(metrics)

    result = {
        "meta": {"input_file": str(path), "schema_known": "v15/A1 §3.2"},
        "metrics": metrics,
        "recommendation": rec,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("[S3 路径选择器 — v15/A1 POC]")
        print("=" * 60)
        print(f"Story 总数: {metrics['total_stories']}")
        print(f"UI Story 数: {metrics['ui_stories']} (ratio {metrics['ui_ratio']*100:.1f}%)")
        print(f"P0 Story 数: {metrics['p0_count']}")
        print(f"跨模块数: {metrics['cross_module_count']}")
        print("-" * 60)
        print(f"推荐路径: {rec['mode']}")
        print("触发原因:")
        for r in rec["reasons"]:
            print(f"  - {r}")
        print("=" * 60)
        print("[POC 模式] 不改 S3 实际产出，仅决策树逻辑验证")
        print("=" * 60)
        print("⚠️ A1 是 LLM 决策辅助，不强制。S3 实际模式由 LLM 自主判断。")
        print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())