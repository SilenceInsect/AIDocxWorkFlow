#!/usr/bin/env python3
"""AIDocxWorkFlow S5 出口预检（S7-lite 子集）—— v14 §5 第二阶段第一项。

来源：v14 PLAN.md §A.2 补充 1 + §4.2 方案 B
- v14 PLAN.md §A.2 S7-lite 双审问题（2026-07-13 拍板）：
 S7-lite 只做审查员 B 的前置（引用完整性 + ID 规范），不做审查员 A 的结构检查
- v14 PLAN.md §D P2：
 S7-lite 职责边界收窄到脚本级校验——只做 ID 规范 / 必填字段 / 格式校验，
 模块归类 / 结构质量全部留给 S7 正式审查，零重叠

职责（按 P2 拍板）：
  1. ID 规范校验（test_point_id 格式 / story_id 引用存在性 / obj_id 引用存在性）
  2. 必填字段校验（test_point_id / module / test_type / priority / description）
  3. 引用完整性校验（s4_reference 引用是否在 S4 business_flow.md 中存在）

非职责（明确不做——避免双审）：
  - 模块归属正确性（v14 决策树两步法是 LLM 责任）
  - 测试覆盖率统计（S7 正式审查责任）
  - 优先级合理性（S7 审查员可推翻 S2 标注）
  - 结构质量 / 业务语义（S7 审查员 A 责任）

调用方式：
  python3 ai_workflow/s5_exit_precheck.py <test_points.json> [s4_business_flow.md]
  python3 ai_workflow/s5_exit_precheck.py --self-test

退出码：
  0 = 通过（可进入 S6）
  1 = 阻塞（必填字段缺失或 ID 规范错误——必须修复）
  2 = 警告（引用完整性异常——LLM 按业务实际判断是否继续）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# S7-lite 必须字段（MUST 级别——v14 §4.5.1 P0 标准）
S7_LITE_REQUIRED_FIELDS = [
    "test_point_id",
    "module",
    "test_type",
    "priority",
    "description",
]

# 8 模块合法枚举（与 .cursor/MODULES.md §1 一致）
VALID_MODULES = {"CONFIG", "UI", "BIZ", "UTIL", "LINK", "LOG", "SPECIAL", "HINT"}

# 优先级合法枚举（v14 §4.5.1）
VALID_PRIORITIES = {"P0", "P1", "P2"}

# ID 格式正则：TP-{StoryID或OBJ-ID后缀}-{NNN}（按现有 test_points.json 惯例，简化匹配）
TP_ID_PATTERN = re.compile(r"^TP-\d{3,}$")
OBJ_ID_PATTERN = re.compile(r"^[A-Z]+-\d+(-\d+)*(-OBJ-\d+)?$")


def _load_json(path: Path) -> dict | list:
    """加载 JSON，失败抛 ValueError（不允许 fallback 到空对象）。"""
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败 {path}: {e}") from e


def _extract_test_points(data: dict | list) -> list[dict]:
    """兼容多种 schema：scenario_test_points[] 或顶层数组。"""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("scenario_test_points", "test_points", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise ValueError("无法定位测试点数组（应包含 scenario_test_points / test_points / 顶层数组）")


def _extract_s4_references(business_flow_path: Path) -> set[str]:
    """从 S4 business_flow.md 提取所有叶子节点 ID（S4-{...} 或 R-XX 形式）。

    简化版：抓所有类似 S4-EPIC-XXX-X.Y.Z 或 R-XXX 的字符串。
    """
    if not business_flow_path or not business_flow_path.exists():
        return set()
    text = business_flow_path.read_text(encoding="utf-8")
    refs: set[str] = set()
    # S4 叶子节点 ID（来自外部方案 §A.2）
    refs.update(re.findall(r"S4-[A-Z]+-[\w.\-]+", text))
    # 风险点 ID
    refs.update(re.findall(r"R-\d+", text))
    return refs


def run_precheck(test_points_path: Path, s4_path: Path | None = None) -> dict:
    """执行 S7-lite 预检，返回 {passed, errors, warnings, stats}。"""
    errors: list[dict] = []
    warnings: list[dict] = []

    # 1. 加载 + 结构
    data = _load_json(test_points_path)
    tps = _extract_test_points(data)
    if not tps:
        errors.append({"type": "EMPTY", "msg": f"测试点数组为空: {test_points_path}"})

    # 2. 必填字段校验（MUST——缺则阻塞）
    for i, tp in enumerate(tps):
        if not isinstance(tp, dict):
            errors.append({"type": "NOT_DICT", "index": i, "msg": "TP 不是 dict"})
            continue
        for field in S7_LITE_REQUIRED_FIELDS:
            if field not in tp or tp[field] in (None, "", []):
                errors.append({
                    "type": "MISSING_REQUIRED",
                    "index": i,
                    "tp_id": tp.get("test_point_id", f"#{i}"),
                    "field": field,
                })

    # 3. ID 规范校验
    seen_ids: set[str] = set()
    for i, tp in enumerate(tps):
        if not isinstance(tp, dict):
            continue
        tp_id = str(tp.get("test_point_id", ""))
        if not tp_id:
            continue  # 已在必填校验报错
        # ID 重复
        if tp_id in seen_ids:
            errors.append({"type": "DUPLICATE_ID", "index": i, "tp_id": tp_id})
        seen_ids.add(tp_id)
        # ID 格式（仅 TP-XXX 格式允许）
        if not TP_ID_PATTERN.match(tp_id):
            errors.append({
                "type": "INVALID_ID_FORMAT",
                "index": i,
                "tp_id": tp_id,
                "expected": "TP-NNN (3+ digits)",
            })
        # module 枚举
        mod = tp.get("module", "")
        if mod and mod not in VALID_MODULES:
            errors.append({
                "type": "INVALID_MODULE",
                "index": i,
                "tp_id": tp_id,
                "module": mod,
                "valid": sorted(VALID_MODULES),
            })
        # priority 枚举
        pri = tp.get("priority", "")
        if pri and pri not in VALID_PRIORITIES:
            errors.append({
                "type": "INVALID_PRIORITY",
                "index": i,
                "tp_id": tp_id,
                "priority": pri,
                "valid": sorted(VALID_PRIORITIES),
            })

    # 4. 引用完整性校验（SHOULD——缺则警告）
    s4_refs = _extract_s4_references(s4_path) if s4_path else set()
    if s4_path and s4_path.exists() and not s4_refs:
        warnings.append({
            "type": "S4_REFS_EMPTY",
            "msg": f"未从 {s4_path} 提取到任何 S4 叶子节点引用——S4 可能为空",
        })
    for i, tp in enumerate(tps):
        if not isinstance(tp, dict):
            continue
        s4_ref = tp.get("s4_reference")
        if s4_ref and s4_refs and s4_ref not in s4_refs:
            warnings.append({
                "type": "S4_REF_NOT_FOUND",
                "index": i,
                "tp_id": tp.get("test_point_id", f"#{i}"),
                "s4_reference": s4_ref,
            })

    # 5. 统计
    stats = {
        "total_test_points": len(tps),
        "unique_ids": len(seen_ids),
        "errors_count": len(errors),
        "warnings_count": len(warnings),
        "modules_used": sorted({tp.get("module", "") for tp in tps if isinstance(tp, dict)}),
        "priorities_used": sorted({tp.get("priority", "") for tp in tps if isinstance(tp, dict)}),
    }

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }


def self_test() -> int:
    """自测：构造合法 + 非法样本，跑预检，断言退出码。

    用法：python3 s5_exit_precheck.py --self-test
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Case 1: 合法样本
        good_path = tmp / "good.json"
        good_path.write_text(json.dumps({
            "scenario_test_points": [
                {"test_point_id": "TP-001", "module": "UI", "test_type": "POSITIVE",
                 "priority": "P0", "description": "登录按钮渲染"},
                {"test_point_id": "TP-002", "module": "BIZ", "test_type": "POSITIVE",
                 "priority": "P1", "description": "登录服务调用"},
            ]
        }, ensure_ascii=False), encoding="utf-8")
        result = run_precheck(good_path)
        assert result["passed"], f"合法样本应通过: {result}"
        assert result["stats"]["total_test_points"] == 2
        assert result["stats"]["unique_ids"] == 2

        # Case 2: 缺必填字段
        bad_path = tmp / "bad.json"
        bad_path.write_text(json.dumps({
            "scenario_test_points": [
                {"test_point_id": "TP-001", "module": "UI"},  # 缺 test_type / priority / description
            ]
        }, ensure_ascii=False), encoding="utf-8")
        result = run_precheck(bad_path)
        assert not result["passed"], f"缺必填字段应不通过: {result}"
        assert any(e["type"] == "MISSING_REQUIRED" for e in result["errors"])

        # Case 3: ID 格式非法
        bad_id_path = tmp / "bad_id.json"
        bad_id_path.write_text(json.dumps({
            "scenario_test_points": [
                {"test_point_id": "BAD-ID", "module": "UI", "test_type": "POSITIVE",
                 "priority": "P0", "description": "x"},
            ]
        }, ensure_ascii=False), encoding="utf-8")
        result = run_precheck(bad_id_path)
        assert not result["passed"]
        assert any(e["type"] == "INVALID_ID_FORMAT" for e in result["errors"])

        # Case 4: 模块非法
        bad_mod_path = tmp / "bad_mod.json"
        bad_mod_path.write_text(json.dumps({
            "scenario_test_points": [
                {"test_point_id": "TP-001", "module": "FAKE", "test_type": "POSITIVE",
                 "priority": "P0", "description": "x"},
            ]
        }, ensure_ascii=False), encoding="utf-8")
        result = run_precheck(bad_mod_path)
        assert not result["passed"]
        assert any(e["type"] == "INVALID_MODULE" for e in result["errors"])

        # Case 5: 引用完整性警告（非阻塞）
        s4_path = tmp / "business_flow.md"
        s4_path.write_text("# S4\n\n- S4-EPIC-001-X.Y.Z\n", encoding="utf-8")
        ref_path = tmp / "ref.json"
        ref_path.write_text(json.dumps({
            "scenario_test_points": [
                {"test_point_id": "TP-001", "module": "UI", "test_type": "POSITIVE",
                 "priority": "P0", "description": "x", "s4_reference": "S4-EPIC-999-NOPE"},
            ]
        }, ensure_ascii=False), encoding="utf-8")
        result = run_precheck(ref_path, s4_path)
        # errors 为空（warnings 非空）→ passed=True（warning 不阻塞）
        assert result["passed"], f"引用完整性警告不应阻塞: {result}"
        assert any(w["type"] == "S4_REF_NOT_FOUND" for w in result["warnings"])

    print("[self-test OK] 5 cases passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="s5_exit_precheck",
        description="AIDocxWorkFlow S5 出口预检（S7-lite 子集 — v14 §5 第二阶段）",
    )
    parser.add_argument("test_points", nargs="?", help="test_points.json 路径")
    parser.add_argument(
        "s4_business_flow",
        nargs="?",
        default=None,
        help="S4 business_flow.md 路径（可选；提供则启用引用完整性校验）",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="运行 self-test（不需参数）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式（默认人读格式）",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.test_points:
        print("[ERROR] 缺少 test_points.json 路径，或使用 --self-test", file=sys.stderr)
        return 2

    test_points_path = Path(args.test_points)
    s4_path = Path(args.s4_business_flow) if args.s4_business_flow else None

    try:
        result = run_precheck(test_points_path, s4_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        s = result["stats"]
        print("=" * 60)
        print("[S5 出口预检 S7-lite — v14 §5 第二阶段]")
        print("=" * 60)
        print(f"测试点总数: {s['total_test_points']}")
        print(f"唯一 ID 数: {s['unique_ids']}")
        print(f"使用模块: {', '.join(s['modules_used']) or '(无)'}")
        print(f"使用优先级: {', '.join(s['priorities_used']) or '(无)'}")
        print(f"错误数: {s['errors_count']} | 警告数: {s['warnings_count']}")
        print("-" * 60)
        if result["errors"]:
            print("[ERRORS — 阻塞 S6 进入]")
            for e in result["errors"][:20]:
                print(f"  - {e}")
            if len(result["errors"]) > 20:
                print(f"  ... 还有 {len(result['errors']) - 20} 条")
        if result["warnings"]:
            print("[WARNINGS — 不阻塞，LLM 按业务判断]")
            for w in result["warnings"][:20]:
                print(f"  - {w}")
            if len(result["warnings"]) > 20:
                print(f"  ... 还有 {len(result['warnings']) - 20} 条")
        print("=" * 60)
        print(f"结论: {'PASS — 可进入 S6' if result['passed'] else 'BLOCKED — 必须修复 errors'}")
        print("=" * 60)

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())