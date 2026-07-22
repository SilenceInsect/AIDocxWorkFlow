#!/usr/bin/env python3
"""scan_module_definitions.py - 精准扫描项目中的 8 模块定义副本。

区别于 sync_modules_table.py 的宽扫描（任何含 8 模块名的文件）,
本工具只找"含 8 模块职责定义表"的文件,即可能被 LLM 误用为"模块判定依据"的
简化版/快照版定义。

使用:
    python3 .cursor/hooks/scan_module_definitions.py
    python3 .cursor/hooks/scan_module_definitions.py --fix    # 自动加 MARKER
    python3 .cursor/hooks/scan_module_definitions.py --self-test
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
MARKER_BEGIN = "<!-- BEGIN: MODULES_TABLE_SYNC"

# 真正"8 模块定义"特征
DEFINITION_PATTERNS = [
    # 旧简化表（已废弃的"| 1 | CONFIG | 仅配置表..." 格式）
    # 关键:CONFIG 在第 3 列, 描述在第 4 列, 中间用 | 分隔, 描述列开头含"仅配置表"或"配置表"特征词
    re.compile(r'\|\s*1\s*\|[^|]*CONFIG\s*\|[^|]*(?:仅\s*)?配置表', re.MULTILINE),
    # "8 模块总表" 标题
    re.compile(r'^#{2,3}\s*8\s*大?模块\s*总表', re.MULTILINE),
    # "模块定义总表" 标题
    re.compile(r'^#{2,3}\s*模块\s*定义\s*总表', re.MULTILINE),
    # "模块职责" + 简化表格（"| 模块 | 职责"）
    re.compile(r'^\|\s*模块\s*\|\s*职责\s*\|', re.MULTILINE),
    # "8 模块职责" 标题（独立段落，可能含定义表）
    re.compile(r'^##\s*8\s*模块职责', re.MULTILINE),
    # v1 协议副本（防止历史 v1 副本没被升级）
    re.compile(r'<!-- BEGIN: MODULES_TABLE_SYNC', re.MULTILINE),
]


def is_already_synced(content: str) -> bool:
    return MARKER_BEGIN in content


def has_definition_table(content: str) -> tuple[bool, list[tuple[int, str]]]:
    """返回 (是否含定义表, [(行号, 匹配片段)])"""
    matches = []
    for pat in DEFINITION_PATTERNS:
        for m in pat.finditer(content):
            line_no = content[:m.start()].count("\n") + 1
            matches.append((line_no, m.group()[:80]))
    return (len(matches) > 0, matches)


def scan(verbose: bool = True) -> dict[str, list[Path]]:
    """扫描项目, 返回 {状态: [文件列表]}"""
    candidates = list(PROJECT_ROOT.rglob("*.md")) + list(PROJECT_ROOT.rglob("*.mdc"))
    candidates = [
        c for c in candidates
        if ".cursor/MODULES.md" not in str(c)
        and ".codegraph" not in str(c)
        and "__pycache__" not in str(c)
        and ".git" not in str(c)
    ]

    buckets = {
        "synced": [],          # 已含 MARKER
        "has_definition": [],  # 含真定义表,需迁移
        "clean": [],           # 仅引用/枚举,无需处理
    }

    for p in candidates:
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if is_already_synced(content):
            buckets["synced"].append(p)
            continue

        has, matches = has_definition_table(content)
        if has:
            buckets["has_definition"].append(p)
            if verbose:
                rel = p.relative_to(PROJECT_ROOT)
                print(f"  ⚠️  {rel}  含 {len(matches)} 处定义表")
                for ln, snippet in matches[:3]:
                    print(f"      L{ln}: {snippet}")
        else:
            buckets["clean"].append(p)

    return buckets


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    print("=== 8 模块定义副本扫描 ===\n")
    buckets = scan(verbose=not args.quiet)

    print(f"\n=== 汇总 ===")
    print(f"  已同步副本:     {len(buckets['synced'])} 个")
    print(f"  含定义表需迁移: {len(buckets['has_definition'])} 个")
    print(f"  干净（仅引用）: {len(buckets['clean'])} 个")

    if buckets["has_definition"]:
        print(f"\n⚠️  以下文件含'8 模块定义表',建议用 MARKER 协议迁移:")
        for p in buckets["has_definition"]:
            print(f"  - {p.relative_to(PROJECT_ROOT)}")
        return 1  # 退出码 1: 有需要处理的
    return 0


# ── self-test ───────────────────────────────────────────────────────
def self_test() -> int:
    """python3 .cursor/hooks/scan_module_definitions.py --self-test

    验证 4 项：
      1. is_already_synced：MARKER 命中/未命中
      2. has_definition_table：6 种 DEFINITION_PATTERNS 命中
      3. scan() 桶分类（synced/has_definition/clean）
      4. main() exit code（有定义表 → exit 1，无 → exit 0）
    """
    # Case 1: is_already_synced
    assert is_already_synced("<!-- BEGIN: MODULES_TABLE_SYNC v1 -->") is True
    assert is_already_synced("# 8 模块总表") is False
    assert is_already_synced("") is False
    print("  [OK] Case 1: is_already_synced 3 sub-cases pass")

    # Case 2: has_definition_table 命中 6 种模式
    test_cases_2 = [
        ("| 1 | CONFIG | 仅配置表 |", "旧简化表"),
        ("## 8 大模块总表", "8 大模块总表标题"),
        ("### 模块定义总表", "模块定义总表标题"),
        ("| 模块 | 职责 |", "模块/职责简化表"),
        ("## 8 模块职责", "8 模块职责段落"),
        ("<!-- BEGIN: MODULES_TABLE_SYNC v1 -->", "v1 MARKER 协议"),
        # 负面 case（不应命中）：
        ("| 模块 | 描述 |", "无关表格"),
        ("", "空内容"),
    ]
    for content, desc in test_cases_2:
        has, _ = has_definition_table(content)
        if desc.startswith("无关") or desc == "空内容":
            assert not has, f"Case 2 (negative): shouldn't match '{desc}'"
        else:
            assert has, f"Case 2: should match '{desc}' (content='{content[:40]}')"
    print(f"  [OK] Case 2: has_definition_table {len(test_cases_2)} sub-cases pass")

    # Case 3: scan() 桶分类（用临时子目录构造 fixture）
    import tempfile as _tf
    with _tf.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        (tmp_root / "synced.md").write_text("# 8 模块\n<!-- BEGIN: MODULES_TABLE_SYNC v1 -->\n", encoding="utf-8")
        (tmp_root / "dirty.md").write_text("# 8 模块总表\n| 模块 | 职责 |\n", encoding="utf-8")
        (tmp_root / "clean.md").write_text("# 普通文档，没有定义表\n", encoding="utf-8")

        original_root = PROJECT_ROOT
        globals()["PROJECT_ROOT"] = tmp_root
        try:
            buckets = scan(verbose=False)
        finally:
            globals()["PROJECT_ROOT"] = original_root

        assert len(buckets["synced"]) == 1, f"Case 3: expected 1 synced, got {len(buckets['synced'])}"
        assert len(buckets["has_definition"]) == 1, f"Case 3: expected 1 has_definition, got {len(buckets['has_definition'])}"
        assert len(buckets["clean"]) == 1, f"Case 3: expected 1 clean, got {len(buckets['clean'])}"
        print(f"  [OK] Case 3: scan() 桶分类 3 buckets 正确")

    # Case 4: main() exit code
    with _tf.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        (tmp_root / "dirty.md").write_text("## 8 模块职责\n", encoding="utf-8")
        original_root = PROJECT_ROOT
        globals()["PROJECT_ROOT"] = tmp_root
        try:
            import sys as _sys
            _sys_backup = list(_sys.argv)
            _sys.argv = [__file__]
            rc_has = main()
            assert rc_has == 1, f"Case 4a: expected exit 1 (含定义表), got {rc_has}"
            print(f"  [OK] Case 4a: main() 有定义表 → exit {rc_has}")

            (tmp_root / "clean2.md").write_text("无定义表\n", encoding="utf-8")
            (tmp_root / "dirty.md").unlink()
            rc_clean = main()
            assert rc_clean == 0, f"Case 4b: expected exit 0 (干净), got {rc_clean}"
            print(f"  [OK] Case 4b: main() 无定义表 → exit {rc_clean}")

            _sys.argv = _sys_backup
        finally:
            globals()["PROJECT_ROOT"] = original_root

    print("  [OK] self-test passed (4 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())
