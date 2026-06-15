#!/usr/bin/env python3
"""scan_module_definitions.py - 精准扫描项目中的 8 模块定义副本。

区别于 sync_modules_table.py 的宽扫描（任何含 8 模块名的文件）,
本工具只找"含 8 模块职责定义表"的文件,即可能被 LLM 误用为"模块判定依据"的
简化版/快照版定义。

使用:
    python3 .cursor/hooks/scan_module_definitions.py
    python3 .cursor/hooks/scan_module_definitions.py --fix    # 自动加 MARKER
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


if __name__ == "__main__":
    sys.exit(main())
