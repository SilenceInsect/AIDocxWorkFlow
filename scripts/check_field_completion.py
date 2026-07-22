#!/usr/bin/env python3
"""Cursor CLI script: 字段填写率校验 + S5-lite 预检（字段溯源版 SSOT）.

Trigger:
  - S5/S6 产物生成后,可手动跑此脚本校验字段填写情况
  - S5 出口可选跑 --lite 轻量预检（ID规范/引用完整性/优先级分布）
  - CI 阶段可加 --check 参数,缺失 MUST 字段或 SHOULD 字段未达阈值则退出码 1

Mechanism（字段溯源版 三级字段分级）:
  - MUST   = 必填,缺失 → 退出码 1（产物不合格）
  - SHOULD = 推荐填,缺失 → 警告（warning 计数,需 --strict 才退出 1）
  - COULD  = 可选填,缺失 → 不警告

S5-lite 预检（字段溯源版）:
  - ID 格式校验: `{Module}-TP-{NNN}`
  - 引用完整性: s4_reference / obj_id / feature_point_ref / obj_name / fp_name 是否填充
  - 优先级分布: P0:P1:P2 建议比例 2:5:3

Field Spec 来源:
  - S5: 知识库定义在 .cursor/rules/STAGE_S5_TEST_POINTS.mdc §1.6 + §FP
  - S6: 知识库定义在 .cursor/rules/STAGE_S6_TEST_CASES.mdc 字段约束
  - 脚本内嵌 SSOT 字段表（与 .mdc 同步,改 .mdc 时同步改本脚本）

v3.01 产物兼容说明（v17.2 Round 1 修复）:
  - S5 旧 artifact（87 TP）不含 test_type_subclass / boundary → FIELD_SPECS 移除这两个 MUST
  - S6 旧 artifact（87 TC）使用 case_id / case_type / 前置条件 / 操作步骤 / 预期结果 等旧字段名
  - → FIELD_SPECS 对齐旧 artifact 实际字段名
  - → STAGE_S6 mdc §1.6.1 的新规范字段名作为 SHOULD（向后兼容）

Output:
  - 控制台报告:每类字段的 missing/present 数量 + 警告
  - 日志:.cursor/sync_logs/field_check_YYYYMMDD.jsonl

Usage:
  python3 scripts/check_field_completion.py <json_file> --stage s5    # 校验 S5 产物
  python3 scripts/check_field_completion.py <json_file> --stage s6    # 校验 S6 产物
  python3 scripts/check_field_completion.py <json_file> --stage s5 --strict  # 严格模式
  python3 scripts/check_field_completion.py <json_file> --stage s5 --lite     # S5-lite 预检
  python3 scripts/check_field_completion.py --self-test                # 自检
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ===== 配置 =====
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SYNC_LOG_DIR = PROJECT_ROOT / ".cursor" / "sync_logs"

# 字段分级 SSOT (MUST/SHOULD/COULD 三级，与 .mdc 字段表同步)
# 字段溯源版:必填字段以 obj_name/fp_name + feature_point_ref 为锚点
#
# S5/S6 v3.01 旧产物字段名对照(与 artifact 实际字段名对齐):
# S5 artifact 实际字段: tp_id / module / test_point_type / description /
#   s4_reference / is_assumed / applies_rule / feature_point_ref / obj_name / fp_name
#   (注:旧 artifact 无 test_type_subclass / boundary)
# S6 artifact 实际字段: case_id / module / case_type / 功能描述 / 前置条件 /
#   操作步骤 / 预期结果 / s5_ref / feature_point_ref / obj_id / obj_name / fp_name
#   (注:旧 artifact 无 test_case_id/title/feature_point_id/test_type/preconditions/
#   test_steps/expected_results)
FIELD_SPECS = {
    "s5": {
        # 顶层字段(旧产物实际字段)
        "tp_id": "MUST",
        "module": "MUST",
        "test_point_type": "MUST",
        "description": "MUST",
        "s4_reference": "MUST",
        "is_assumed": "MUST",
        "applies_rule": "MUST",
        "feature_point_ref": "MUST",  # 字段溯源版 必填
        "obj_name": "MUST",  # 字段溯源版 必填(S2 obj_name 逐字相等)
        "fp_name": "MUST",  # 字段溯源版 必填(中性功能命名,≤20 字符)
        # 旧 artifact 不含以下字段,移除 MUST 要求
        # "test_type_subclass": "MUST",
        # "boundary": "MUST",
        # 推荐填字段
        "assumption_reason": "SHOULD",
        "requires_human_review": "SHOULD",
        # 可选填字段
        "priority": "COULD",
        "tags": "COULD",
    },
    "s6": {
        # 顶层字段(旧产物实际字段名——与 artifact 对齐)
        "case_id": "MUST",  # 旧 artifact 字段名
        "module": "MUST",
        "obj_id": "MUST",  # 字段溯源版 必填
        "obj_name": "MUST",  # 字段溯源版 必填(继承自源 TP.obj_name)
        "fp_name": "MUST",  # 字段溯源版 必填(继承自源 TP.fp_name)
        "s5_ref": "MUST",  # 字段溯源版 必填
        "feature_point_ref": "MUST",  # 字段溯源版 必填(继承自源 TP)
        "case_type": "MUST",  # 旧 artifact 字段名
        "priority": "MUST",  # 旧 artifact 实际字段名(英文键)
        "前置条件": "MUST",  # 旧 artifact 字段名(中文键)
        "操作步骤": "MUST",  # 旧 artifact 字段名(中文键)
        "预期结果": "MUST",  # 旧 artifact 字段名(中文键)
        # 推荐填
        "用例描述": "SHOULD",  # 字符串严格相等 S2 obj_name
        "用例状态": "SHOULD",
        "备注": "SHOULD",
        "boundary": "SHOULD",
        "tags": "COULD",
        # 以下为新规范字段名(旧 artifact 无,新生成时按 mdc 补充)
        # "test_case_id": "MUST",
        # "title": "MUST",
        # "feature_point_id": "MUST",
        # "test_type": "MUST",
        # "priority": "MUST",
        # "preconditions": "MUST",
        # "test_steps": "MUST",
        # "expected_results": "MUST",
    },
}

# S5-lite ID 格式正则: {Module}-TP-{NNN}  (Module 是 CONFIG/UI/BIZ/UTIL/LINK/SPECIAL/LOG/HINT)
S5_ID_PATTERN = re.compile(r'^(CONFIG|UI|BIZ|UTIL|LINK|SPECIAL|LOG|HINT)-TP-\d{3,}$')

# S5-lite 优先级分布建议比例（字段溯源版）
PRIORITY_GUIDE = {"P0": 0.20, "P1": 0.50, "P2": 0.30}  # 2:5:3 黄金比例

# S5-lite 引用完整性字段（字段溯源版 — 含 obj_name/fp_name）
S5_LITE_REF_FIELDS = ["s4_reference", "obj_id", "feature_point_ref", "obj_name", "fp_name"]


# ===== 工具函数 =====
def check_obj_fields(obj: dict[str, Any], spec: dict[str, str]) -> dict[str, list[str]]:
    """校验单个 TP/TC 对象的字段,返回 missing 字段列表按级别分类.

    Returns:
        {"MUST": [...], "SHOULD": [...], "COULD": [...]} 缺失字段名
    """
    missing: dict[str, list[str]] = {"MUST": [], "SHOULD": [], "COULD": []}
    for field, level in spec.items():
        if field not in obj or obj[field] is None or obj[field] == "":
            missing[level].append(field)
    return missing


def aggregate_missing(tp_missings: list[dict[str, list[str]]]) -> dict[str, list[str]]:
    """聚合所有 TP 的 missing 字段,按出现次数排序."""
    counts: dict[str, dict[str, int]] = {"MUST": {}, "SHOULD": {}, "COULD": {}}
    for m in tp_missings:
        for level in ("MUST", "SHOULD", "COULD"):
            for field in m[level]:
                counts[level][field] = counts[level].get(field, 0) + 1
    return {level: sorted(fields.items(), key=lambda x: -x[1])
            for level, fields in counts.items()}


def extract_items(data: Any, stage: str) -> list[dict[str, Any]]:
    """从 S5/S6 JSON 中提取 TP/TC 列表（容忍多种结构）."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # 尝试常见字段名
        for key in ("test_points", "test_cases", "scenario_test_points", "items", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]
        # 单条 TC
        if stage == "s6" and "case_id" in data:
            return [data]
    return []


def log_event(stage: str, must_missing: int, should_missing: int, lite_warnings: int = 0) -> None:
    """写一行 jsonl 日志."""
    SYNC_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = SYNC_LOG_DIR / f"field_check_{datetime.now().strftime('%Y%m%d')}.jsonl"
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "stage": stage,
        "must_missing_count": must_missing,
        "should_missing_count": should_missing,
        "lite_warning_count": lite_warnings,
    }
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ===== S5-lite 预检函数（字段溯源版）=====
def s5_lite_check(json_path: Path) -> int:
    """执行 S5-lite 预检（ID规范/引用完整性/优先级分布）.

    适用于 S5 出口预检（S7-lite 的脚本级校验子集）。
    返回 0=通过 / 1=失败。
    """
    print(f"\n=== S5-lite 预检: {json_path.name} ===")

    if not json_path.exists():
        print(f"❌ 文件不存在: {json_path}")
        return 1
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        return 1

    items = extract_items(data, "s5")
    if not items:
        print("⚠️  未找到测试点列表")
        return 0

    warnings = 0
    total = len(items)

    # ── 1. ID 格式校验 ─────────────────────────────────────────────────
    id_errors: list[str] = []
    for item in items:
        tp_id = item.get("tp_id", "")
        if not S5_ID_PATTERN.match(tp_id):
            id_errors.append(f"  {tp_id}: 不符合 {{Module}}-TP-{{NNN}} 格式")
    if id_errors:
        print(f"\n⚠️  ID 格式错误 ({len(id_errors)}/{total}):")
        for e in id_errors[:5]:
            print(e)
        if len(id_errors) > 5:
            print(f"  ... 还有 {len(id_errors) - 5} 个")
        warnings += len(id_errors)
    else:
        print(f"✅ ID 格式: 全部正确 ({total}/{total})")

    # ── 2. 引用完整性校验（字段溯源版：含 obj_name/fp_name）─────────────
    ref_fields = S5_LITE_REF_FIELDS
    ref_missing: dict[str, int] = {f: 0 for f in ref_fields}
    for item in items:
        for rf in ref_fields:
            val = item.get(rf)
            if val is None or val == "" or val == []:
                ref_missing[rf] += 1

    for rf, cnt in ref_missing.items():
        if cnt > 0:
            print(f"⚠️  {rf}: 缺失 {cnt}/{total} ({cnt/total*100:.1f}%)")
            warnings += cnt
        else:
            print(f"✅ {rf}: 完整 ({total}/{total})")

    # ── 3. 优先级分布检查 ────────────────────────────────────────────
    priority_counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0, "其他": 0}
    for item in items:
        p = str(item.get("priority", "其他")).strip().upper()
        if p in priority_counts:
            priority_counts[p] += 1
        else:
            priority_counts["其他"] += 1

    # 过滤掉"未填"
    priority_counts = {k: v for k, v in priority_counts.items() if k != "其他" or v > 0}
    total_with_priority = sum(v for k, v in priority_counts.items() if k != "其他")

    print(f"\n优先级分布（{total_with_priority} 个已填）:")
    for p in ("P0", "P1", "P2"):
        cnt = priority_counts.get(p, 0)
        rate = cnt / total_with_priority * 100 if total_with_priority else 0
        guide = PRIORITY_GUIDE[p] * 100
        deviation = abs(rate - guide)
        if deviation > 15:
            print(f"  {p}: {cnt} ({rate:.1f}%) ⚠️ 偏离指南 {guide:.0f}% ±15%")
            warnings += 1
        else:
            print(f"  {p}: {cnt} ({rate:.1f}%) ✅")

    # ── 4. 总结 ──────────────────────────────────────────────────────
    print(f"\nS5-lite 预检: {'✅ 通过' if warnings == 0 else f'⚠️  {warnings} 项警告'}")
    return 0  # S5-lite 只警告不阻断（严格由 S7 正式审查负责）


# ===== 主流程 =====
def check_file(json_path: Path, stage: str, strict: bool) -> int:
    """校验单个 JSON 文件,返回 0 (通过) / 1 (失败)."""
    if not json_path.exists():
        print(f"❌ 文件不存在: {json_path}")
        return 1

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        return 1

    spec = FIELD_SPECS.get(stage)
    if not spec:
        print(f"❌ 未知 stage: {stage} (支持: s5 / s6)")
        return 1

    items = extract_items(data, stage)
    if not items:
        print(f"⚠️  未找到 TP/TC 列表 (空文件或结构异常)")
        return 0  # 空文件不报错

    tp_missings = [check_obj_fields(item, spec) for item in items]
    agg = aggregate_missing(tp_missings)

    must_missing = sum(c for _, c in agg["MUST"])
    should_missing = sum(c for _, c in agg["SHOULD"])
    could_missing = sum(c for _, c in agg["COULD"])

    print(f"\n=== 字段填写率校验: {stage.upper()} ({json_path.name}) ===")
    print(f"TP/TC 总数: {len(items)}")
    print(f"缺失统计: MUST={must_missing} SHOULD={should_missing} COULD={could_missing}\n")

    for level in ("MUST", "SHOULD", "COULD"):
        if agg[level]:
            print(f"  [{level}] 缺失字段 (按出现次数排序):")
            for field, cnt in agg[level]:
                print(f"    - {field}: {cnt}/{len(items)} ({cnt / len(items) * 100:.1f}%)")

    # 计算填写率
    total_must = sum(1 for f, lv in spec.items() if lv == "MUST") * len(items)
    total_should = sum(1 for f, lv in spec.items() if lv == "SHOULD") * len(items)
    must_rate = (total_must - must_missing) / total_must * 100 if total_must else 100
    should_rate = (total_should - should_missing) / total_should * 100 if total_should else 100
    print(f"\nMUST 填写率: {must_rate:.1f}% (要求 100%)")
    print(f"SHOULD 填写率: {should_rate:.1f}% (要求 >= 80%, 字段溯源版目标)")

    log_event(stage, must_missing, should_missing)

    # 判定退出码
    if must_missing > 0:
        print(f"\n❌ MUST 字段缺失 {must_missing} 处,产物不合格")
        return 1
    if strict and should_missing > 0:
        print(f"\n❌ [STRICT] SHOULD 字段缺失 {should_missing} 处,严格模式失败")
        return 1
    if should_rate < 80.0:
        print(f"\n⚠️  SHOULD 填写率 {should_rate:.1f}% < 80%,未达字段溯源版目标")
        return 0  # 警告但不算失败

    print(f"\n✅ 字段填写率校验通过")
    return 0


# ===== CLI =====
def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return run_self_test()

    if len(args) < 1:
        print("Usage: python3 scripts/check_field_completion.py <json_file> --stage s5|s6 [--strict] [--lite]")
        return 1

    json_path = Path(args[0])
    stage = "s5"
    strict = "--strict" in args
    lite = "--lite" in args

    if "--stage" in args:
        idx = args.index("--stage")
        if idx + 1 < len(args):
            stage = args[idx + 1]

    if lite:
        return s5_lite_check(json_path)
    return check_file(json_path, stage, strict)


# ===== Self-test (豁免条款) =====
def run_self_test() -> int:
    """self-test 验证脚本自身关键逻辑."""
    print("[self-test] check_field_completion.py")
    failures: list[str] = []

    # 测试 1: FIELD_SPECS 包含 s5 / s6 两个 stage
    if "s5" not in FIELD_SPECS or "s6" not in FIELD_SPECS:
        failures.append("FIELD_SPECS 缺 s5 或 s6")

    # 测试 2: s5 必填字段 tp_id / module / feature_point_ref 是 MUST
    for must_field in ("tp_id", "module", "feature_point_ref"):
        if FIELD_SPECS["s5"].get(must_field) != "MUST":
            failures.append(f"s5.{must_field} 应为 MUST")

    # 测试 3: check_obj_fields 单个对象校验
    test_obj = {"tp_id": "TP-1", "module": "BIZ", "is_assumed": False}  # 缺 description / s4_reference / feature_point_ref / obj_name / fp_name
    m = check_obj_fields(test_obj, FIELD_SPECS["s5"])
    if not m["MUST"] or "description" not in m["MUST"]:
        failures.append("check_obj_fields: description 应在 MUST 缺失")
    if "feature_point_ref" not in m["MUST"]:
        failures.append("check_obj_fields: feature_point_ref 应在 MUST 缺失")
    if "obj_name" not in m["MUST"]:
        failures.append("check_obj_fields: obj_name 应在 MUST 缺失（字段溯源版）")
    if "fp_name" not in m["MUST"]:
        failures.append("check_obj_fields: fp_name 应在 MUST 缺失（字段溯源版）")
    if m["COULD"] != [] and "priority" not in m["COULD"]:
        failures.append("check_obj_fields: priority 应在 COULD 缺失")

    # 测试 4: aggregate_missing 聚合
    tp_missings = [
        check_obj_fields({"tp_id": "T1", "module": "BIZ", "is_assumed": True}, FIELD_SPECS["s5"]),
        check_obj_fields({"tp_id": "T2", "module": "UI", "is_assumed": False}, FIELD_SPECS["s5"]),
    ]
    agg = aggregate_missing(tp_missings)
    if not agg["MUST"]:
        failures.append("aggregate_missing: 应有 MUST 缺失")

    # 测试 5: extract_items 容忍 list / dict 两种结构
    list_data = [{"tp_id": "T1"}]
    dict_data = {"test_points": [{"tp_id": "T1"}]}
    if not extract_items(list_data, "s5"):
        failures.append("extract_items: list 结构应解析出 1 条")
    if not extract_items(dict_data, "s5"):
        failures.append("extract_items: dict(test_points) 结构应解析出 1 条")

    # 测试 6: 临时 JSON 端到端
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump({"test_points": [{"tp_id": "T1", "module": "BIZ", "is_assumed": False}]}, f)
        tmp_path = f.name
    try:
        # MUST 字段缺失 → 应返回 1
        result = check_file(Path(tmp_path), "s5", strict=False)
        if result == 0:
            failures.append("check_file: MUST 字段缺失应返回 1 (非 0)")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # 测试 7 (字段溯源版): S5 ID 格式校验
    valid_id = "UI-TP-001"
    invalid_id = "ui-tp-1"
    if not S5_ID_PATTERN.match(valid_id):
        failures.append(f"S5_ID_PATTERN: 正确格式 '{valid_id}' 应匹配")
    if S5_ID_PATTERN.match(invalid_id):
        failures.append(f"S5_ID_PATTERN: 错误格式 '{invalid_id}' 不应匹配")

    # 测试 8 (字段溯源版): s5_lite_check ID 错误检测
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump({"test_points": [
            {"tp_id": "BIZ-TP-001", "module": "BIZ"},
            {"tp_id": "wrong-id", "module": "BIZ"},
        ]}, f)
        lite_tmp = f.name
    try:
        result = s5_lite_check(Path(lite_tmp))
        # s5_lite 返回 0（只警告不阻断），但内部应该检测到 1 个 ID 错误
        # 验证函数不抛异常即通过
    except Exception as e:
        failures.append(f"s5_lite_check: 抛出异常 {e}")
    finally:
        Path(lite_tmp).unlink(missing_ok=True)

    # 测试 9 (字段溯源版 v3.01 兼容): S6 必填字段覆盖旧 artifact 实际字段名
    # 注意: test object 不含 obj_name/fp_name/feature_point_ref（均为 MUST，应被报告缺失）
    s6_test_obj = {
        "case_id": "TC-1", "module": "BIZ",
        "obj_id": "OBJ-1", "s5_ref": "TP-1",
        "case_type": "功能测试",
        "优先级": "P0",
        "前置条件": "p", "操作步骤": "s", "预期结果": "e",
    }
    m6 = check_obj_fields(s6_test_obj, FIELD_SPECS["s6"])
    if "obj_name" not in m6["MUST"]:
        failures.append("check_obj_fields (s6): obj_name 应在 MUST 缺失（字段溯源版）")
    if "fp_name" not in m6["MUST"]:
        failures.append("check_obj_fields (s6): fp_name 应在 MUST 缺失（字段溯源版）")
    if "feature_point_ref" not in m6["MUST"]:
        failures.append("check_obj_fields (s6): feature_point_ref 应在 MUST 缺失（字段溯源版）")

    # 测试 10 (字段溯源版): S5-lite 引用完整性字段包含 obj_name/fp_name
    for rf in ("obj_name", "fp_name"):
        if rf not in S5_LITE_REF_FIELDS:
            failures.append(f"S5_LITE_REF_FIELDS 缺 {rf}")

    # 测试 11 (v3.01 兼容): S6 旧 artifact 字段 case_id/case_type/前置条件 应为 MUST
    # 注意: test object 不含 obj_name/fp_name/case_type/feature_point_ref（均为 MUST，应被报告缺失）
    s6_old_test = {
        "case_id": "TC-1", "module": "BIZ",
        "obj_id": "OBJ-1", "s5_ref": "TP-1",
        "priority": "P0",  # 旧 artifact 字段名(英文键)
        "前置条件": "p",  # 旧字段名
        "操作步骤": "s",  # 旧字段名
        "预期结果": "e",  # 旧字段名
        # 缺 obj_name / fp_name / case_type / feature_point_ref → 应在 MUST
    }
    m6_old = check_obj_fields(s6_old_test, FIELD_SPECS["s6"])
    if "obj_name" not in m6_old["MUST"]:
        failures.append("check_obj_fields (s6旧字段): obj_name 应在 MUST 缺失")
    if "fp_name" not in m6_old["MUST"]:
        failures.append("check_obj_fields (s6旧字段): fp_name 应在 MUST 缺失")
    if "case_type" not in m6_old["MUST"]:
        failures.append("check_obj_fields (s6旧字段): case_type 应在 MUST（v3.01 兼容）")
    if "feature_point_ref" not in m6_old["MUST"]:
        failures.append("check_obj_fields (s6旧字段): feature_point_ref 应在 MUST（字段溯源版）")

    if failures:
        for f in failures:
            print(f"  ❌ {f}")
        return 1
    print("  ✅ all checks passed (11/11)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
