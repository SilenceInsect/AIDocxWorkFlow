#!/usr/bin/env python3
"""AIDocxWorkFlow 产物格式合规检测 hook（afterFileEdit 事件）

作用：
  - 检测最近修改的文件中是否出现违规：
    * DOUBLE_VERSION               - 双版本标签（如 "v16 v2"）
    * PERMANENT_RULE_VERSION_TAG   - 永久规范版本标记（如 "v17 新增"、"v17+ 强制"）
    * FORBIDDEN_JSON_FIELDS        - 禁止 JSON 字段（如 "version_note"、"changelog"）
    * ISO_TIMESTAMP                - ISO 8601 时间戳（如 "2026-07-17T18:00:00+08:00"）
  - 规则配置统一从 .cursor/rules/product_format_rules.yaml 读取

规则来源（SSOT）：
  .cursor/rules/product_format_rules.yaml

触发：
  .cursor/hooks.json -> afterFileEdit array -> {command: content_compliance_check.py}

协议：
  stdin: JSON {"file_path": "..."}（afterFileEdit 传入）
  stdout: 无
  exit 0: 正常 / exit 1: 严重违规（block）
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# ── 路径常量 ─────────────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
_RULES_CONFIG = _PROJECT_ROOT / ".cursor" / "rules" / "product_format_rules.yaml"
_LOG_FILE = Path("workflow_assets/feedback_logs/format_violations.jsonl")
_SCAN_WINDOW_MINUTES = int(os.environ.get("COMPLIANCE_SCAN_WINDOW_MINUTES", "5"))

# ── 规则配置加载器 ───────────────────────────────────────────────────────────
def load_rules_config() -> dict[str, Any]:
    """从 YAML 配置文件加载规则（SSOT）"""
    try:
        import yaml
        if _RULES_CONFIG.exists():
            with open(_RULES_CONFIG, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except ImportError:
        pass
    except Exception:
        pass
    return {}


def get_compiled_patterns(config: dict[str, Any]) -> dict[str, tuple[re.Pattern, dict[str, Any]]]:
    """获取编译后的所有检测正则（从配置读取）

    Returns:
        dict[str, tuple[re.Pattern, dict[str, Any]]] — key 是 pattern 名，
        value 是 (编译后的正则, 规则配置 dict)。
    """
    patterns: dict[str, tuple[re.Pattern, dict[str, Any]]] = {}
    detection = config.get("detection_patterns", {})

    for key, rule in detection.items():
        if not rule.get("enabled", True):
            continue
        pattern_str = rule.get("pattern")
        if not pattern_str:
            continue
        try:
            patterns[key] = (re.compile(pattern_str), rule)
        except re.error:
            continue

    return patterns


def is_path_exempt(file_path: str, config: dict[str, Any]) -> bool:
    """检查文件是否豁免检测"""
    exempt_paths = config.get("exempt_paths", [])
    for pattern in exempt_paths:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
            os.path.basename(file_path), pattern
        ):
            return True
        stripped = pattern.strip("/")
        if stripped in file_path:
            return True
    return False


def is_file_exempt_by_name(basename: str, exempt_names: list[str]) -> bool:
    """检查文件名是否在豁免列表中"""
    for name in exempt_names:
        if fnmatch.fnmatch(basename, name) or basename == name:
            return True
    return False


# ── 检测函数 ─────────────────────────────────────────────────────────────────
def scan_file(
    file_path: Path,
    patterns: dict[str, tuple[re.Pattern, dict[str, Any]]],
) -> list[dict[str, Any]]:
    """扫描单个文件的违规内容（遍历所有 patterns）

    每个 pattern 独立检测；违规 type 字段 = pattern key 的大写形式。
    """
    violations: list[dict[str, Any]] = []

    try:
        if not file_path.exists():
            return violations

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        basename = file_path.name

        for pattern_key, (pattern, rule) in patterns.items():
            # 检查豁免文件
            exempt_files = rule.get("exempt_files", [])
            if is_file_exempt_by_name(basename, exempt_files):
                continue

            violation_type = pattern_key.upper()
            for match in pattern.finditer(content):
                start = max(0, match.start() - 30)
                end = min(len(content), match.end() + 30)
                context = content[start:end].replace("\n", " ").strip()
                violations.append(
                    {
                        "type": violation_type,
                        "pattern": match.group(0),
                        "file": str(file_path),
                        "context": f"...{context}...",
                        "severity": rule.get("severity", "HIGH"),
                    }
                )

    except Exception:
        pass

    return violations


def get_recently_modified_files() -> list[str]:
    """获取最近 SCAN_WINDOW_MINUTES 分钟内修改的文件"""
    try:
        since = datetime.now(timezone.utc) - timedelta(minutes=_SCAN_WINDOW_MINUTES)
        since_str = since.strftime("%Y-%m-%d %H:%M:%S")

        result = subprocess.run(
            ["git", "diff", "--name-only", f"--since={since_str}"],
            cwd=_PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=_PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                return [f for f in files if f]
            return []

        files = result.stdout.strip().split("\n")
        return [f for f in files if f]

    except (subprocess.TimeoutExpired, Exception):
        return []


# ── 主逻辑 ──────────────────────────────────────────────────────────────────
def main() -> int:
    """主入口：加载规则 → 扫描文件 → 记录违规"""
    # 1. 加载规则配置（SSOT）
    config = load_rules_config()

    if not config:
        sys.stderr.write(
            f"[FORMAT-CHECK] 规则配置不存在: {_RULES_CONFIG}，跳过检测\n"
        )
        return 0

    # 2. 获取检测模式（多模式，遍历 detection_patterns 中所有 enabled 的 pattern）
    patterns = get_compiled_patterns(config)
    if not patterns:
        return 0

    # 3. 获取最近修改的文件
    recent_files = get_recently_modified_files()

    if not recent_files:
        return 0

    # 4. 扫描每个文件
    all_violations: list[dict[str, Any]] = []
    for file_rel in recent_files:
        file_path = _PROJECT_ROOT / file_rel
        if not file_path.exists():
            continue

        # 检查豁免路径
        if is_path_exempt(file_rel, config):
            continue

        # 检测违规（遍历所有 patterns）
        violations = scan_file(file_path, patterns)
        all_violations.extend(violations)

    # 5. 记录违规
    if all_violations:
        _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        with _LOG_FILE.open("a", encoding="utf-8") as f:
            for v in all_violations:
                record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **v,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # 输出警告
        violation_types = set(v["type"] for v in all_violations)
        file_count = len(set(v["file"] for v in all_violations))
        sys.stderr.write(
            f"[FORMAT-WARN] Found {len(all_violations)} violation(s) in {file_count} file(s): "
            f"{', '.join(sorted(violation_types))}\n"
        )
        sys.stderr.write(f"[FORMAT-WARN] Logged to {_LOG_FILE}\n")
        sys.stderr.flush()

        # HIGH severity → 阻断
        high_severity = [v for v in all_violations if v["severity"] == "HIGH"]
        if high_severity:
            sys.stderr.write(
                f"[FORMAT-BLOCK] {len(high_severity)} HIGH severity violation(s). "
                "Review: .cursor/rules/product_format_rules.yaml\n"
            )
            sys.stderr.flush()
            return 1

    return 0


# ── self-test ────────────────────────────────────────────────────────────────
def self_test() -> int:
    """python3 .cursor/hooks/content_compliance_check.py --self-test"""
    import tempfile

    print("  [INFO] Testing with YAML config (4 patterns expected)")

    # Case 1: 规则配置加载（确认有 4 个 pattern）
    config = load_rules_config()
    assert config, "Case 1: 规则配置应加载成功"
    detection = config.get("detection_patterns", {})
    enabled_patterns = {k: v for k, v in detection.items() if v.get("enabled", True)}
    assert len(enabled_patterns) >= 4, (
        f"Case 1: 应有 ≥ 4 个 enabled pattern，实际 {len(enabled_patterns)}"
    )
    print(
        f"  [OK] Case 1: 规则配置加载 ({len(enabled_patterns)} patterns: "
        f"{', '.join(enabled_patterns.keys())})"
    )

    # Case 2: 双版本标签检测
    patterns = get_compiled_patterns(config)
    assert "double_version" in patterns, "Case 2: 应有 double_version pattern"
    dv_pattern, _ = patterns["double_version"]
    test_text = "## v16 v2 完整版"
    match = dv_pattern.search(test_text)
    assert match, "Case 2: 应检测到双版本标签"
    print(f"  [OK] Case 2: 双版本标签检测 ({match.group(0)})")

    # Case 3: 永久规范版本标记检测（v17 新增 / v17+ 强制 / v17 SSOT）
    assert "permanent_rule_version_tag" in patterns, (
        "Case 3: 应有 permanent_rule_version_tag pattern"
    )
    pr_pattern, _ = patterns["permanent_rule_version_tag"]
    pr_samples = [
        "v17 新增",
        "v17 新增规则",
        "v17+ 强制",
        "v17 SSOT",
    ]
    pr_hits = sum(1 for s in pr_samples if pr_pattern.search(s))
    assert pr_hits >= 3, (
        f"Case 3: 至少 3 个永久规范版本标记样本应命中，实际 {pr_hits}/{len(pr_samples)}"
    )
    print(f"  [OK] Case 3: 永久规范版本标记检测 ({pr_hits}/{len(pr_samples)} 命中)")

    # Case 4: 豁免路径检测
    # knowledge/ 下文件不再豁免（knowledge/public/ 入 Git 必须扫描；knowledge/project_local/ 虽 .gitignore 但违规需发现）
    exempt_tests = [
        ("/workflow_assets/test.json", True),
        ("/resource/test.json", True),
        ("/knowledge/public/test.json", False),
        ("/knowledge/project_local/test.json", False),
        ("src/test.json", False),
    ]
    for path, expected in exempt_tests:
        result = is_path_exempt(path, config)
        assert result == expected, (
            f"Case 4: {path} 应豁免={expected}, 实际={result}"
        )
    print("  [OK] Case 4: 豁免路径检测（含 knowledge/ 子目录不再豁免）")

    # Case 5: scan_file 检测（用含双版本标签的内容）
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write("# v16 v2 完整版\n\n这是违规内容\n")
        test_path = Path(f.name)

    violations = scan_file(test_path, patterns)
    assert len(violations) >= 1, f"Case 5: 应检测到违规，实际 {len(violations)}"
    assert violations[0]["type"] == "DOUBLE_VERSION", (
        f"Case 5: 违规类型应为 DOUBLE_VERSION（pattern key 大写），"
        f"实际 {violations[0]['type']}"
    )
    test_path.unlink()
    print(
        f"  [OK] Case 5: scan_file 检测 ({len(violations)} violations, "
        f"type={violations[0]['type']})"
    )

    # Case 6: CHANGELOG 豁免（双版本标签命中但文件名豁免）
    changelog_path = Path("/tmp/CHANGELOG.md")
    changelog_path.write_text("# v16 v2 变更记录")
    violations = scan_file(changelog_path, patterns)
    assert len(violations) == 0, (
        f"Case 6: CHANGELOG 应豁免，实际 {len(violations)} violations"
    )
    changelog_path.unlink()
    print("  [OK] Case 6: CHANGELOG 豁免")

    # Case 7: 禁止字段（JSON）检测 - version_note / changangelog 字段
    assert "forbidden_json_fields" in patterns, (
        "Case 7: 应有 forbidden_json_fields pattern"
    )
    fj_pattern, _ = patterns["forbidden_json_fields"]
    fj_samples = [
        '"version_note": "..."',
        '"changelog": "..."',
        '{"version_note": "x"}',
    ]
    fj_hits = sum(1 for s in fj_samples if fj_pattern.search(s))
    assert fj_hits == 3, (
        f"Case 7: 3 个禁止字段样本应全部命中，实际 {fj_hits}/{len(fj_samples)}"
    )
    print(f"  [OK] Case 7: 禁止字段（JSON）检测 ({fj_hits}/{len(fj_samples)} 命中)")

    # Case 8: ISO 时间戳检测（2026-07-17T18:00:00+08:00 等格式）
    assert "iso_timestamp" in patterns, "Case 8: 应有 iso_timestamp pattern"
    iso_pattern, iso_rule = patterns["iso_timestamp"]
    assert iso_rule.get("severity") == "MEDIUM", (
        f"Case 8: iso_timestamp 严重度应为 MEDIUM，实际 {iso_rule.get('severity')}"
    )
    iso_samples = [
        "2026-07-17T18:00:00+08:00",
        "2026-07-17T18:00:00.123+08:00",
        "2026-01-01T00:00:00-05:00",
    ]
    iso_hits = sum(1 for s in iso_samples if iso_pattern.search(s))
    assert iso_hits == 3, (
        f"Case 8: 3 个 ISO 时间戳样本应全部命中，实际 {iso_hits}/{len(iso_samples)}"
    )
    # 负样本：非 ISO 格式不应命中
    assert not iso_pattern.search("2026-07-17 18:00:00"), (
        "Case 8: 空格分隔的时间不应被当作 ISO 时间戳"
    )
    print(f"  [OK] Case 8: ISO 时间戳检测 ({iso_hits}/{len(iso_samples)} 命中, severity=MEDIUM)")

    # Case 9: scan_file 端到端 - 含 4 类违规的小文件
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(
            "# 测试文件\n\n"
            "- v16 v2 双版本\n"  # DOUBLE_VERSION
            "- v17 新增 永久标记\n"  # PERMANENT_RULE_VERSION_TAG
            '- "version_note": "x"\n'  # FORBIDDEN_JSON_FIELDS
            "- 2026-07-17T18:00:00+08:00 ISO\n"  # ISO_TIMESTAMP
        )
        test_path = Path(f.name)

    violations = scan_file(test_path, patterns)
    types_seen = {v["type"] for v in violations}
    expected_types = {
        "DOUBLE_VERSION",
        "PERMANENT_RULE_VERSION_TAG",
        "FORBIDDEN_JSON_FIELDS",
        "ISO_TIMESTAMP",
    }
    missing = expected_types - types_seen
    assert not missing, (
        f"Case 9: 应检测到全部 4 类违规，缺少 {missing}, 实际 {types_seen}"
    )
    # 验证严重度：ISO 应为 MEDIUM，其余为 HIGH
    iso_violations = [v for v in violations if v["type"] == "ISO_TIMESTAMP"]
    assert iso_violations and iso_violations[0]["severity"] == "MEDIUM", (
        f"Case 9: ISO 时间戳严重度应为 MEDIUM"
    )
    high_violations = [
        v for v in violations
        if v["type"] in ("DOUBLE_VERSION", "PERMANENT_RULE_VERSION_TAG", "FORBIDDEN_JSON_FIELDS")
    ]
    assert all(v["severity"] == "HIGH" for v in high_violations), (
        f"Case 9: 其余三类违规严重度应为 HIGH"
    )
    test_path.unlink()
    print(
        f"  [OK] Case 9: 端到端 4 类违规扫描 "
        f"({len(violations)} violations, types={sorted(types_seen)})"
    )

    # Case 10: 正常内容无违规
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(
            "# 正常文档\n\n"
            "本节介绍模块定义。\n"
            "需求使用 v1.0 版本进行发布。\n"
            "字段: priority, module, test_point_id\n"
            "时间字段使用 meta.created_at 统一处理。\n"
        )
        test_path = Path(f.name)

    violations = scan_file(test_path, patterns)
    assert len(violations) == 0, (
        f"Case 10: 正常内容不应触发违规，实际 {len(violations)}: {violations}"
    )
    test_path.unlink()
    print("  [OK] Case 10: 正常内容无违规")

    print(f"  [OK] self-test passed (10 cases)")
    return 0


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
            sys.exit(self_test())
        sys.exit(main())
    except Exception as exc:
        sys.stderr.write(f"[FORMAT-CHECK-CRASH] {type(exc).__name__}: {exc}\n")
        sys.stderr.flush()
        sys.exit(0)
