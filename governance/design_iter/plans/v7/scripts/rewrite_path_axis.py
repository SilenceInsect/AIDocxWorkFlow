#!/usr/bin/env python3
"""目录主轴批量重写脚本：先阶段再版本 -> 先版本再阶段.

用法:
  python3 rewrite_path_axis.py --dry-run    # 预览改动
  python3 rewrite_path_axis.py --execute    # 实际改动

DNA 合规:
  - 先 Read 完整规则文件，改动基于 Read 结果 (9.4)
  - dry-run 先输出 diff，不动文件
  - 可重入（双阶段间不会误伤）
"""
import re
import sys
from pathlib import Path

ROOT = Path("/Users/gleon/Documents/TestDev/AIDocxWorkFlow")

L = "\u300c"
R = "\u300d"
STAGES = [
    f"{L}S1 需求评审{R}",
    f"{L}S1.5 业务澄清{R}",
    f"{L}S1 业务澄清{R}",
    f"{L}S2 需求拆解{R}",
    f"{L}S2.5 迭代规划{R}",
    f"{L}S3 原型导出{R}",
    f"{L}S4 流程图导出{R}",
    f"{L}S5 测试点生成{R}",
    f"{L}S6 测试用例生成{R}",
    f"{L}S7 用例审查{R}",
    f"{L}S8 自迭代{R}",
]

VERSION_PATTERN = r"v[\d]+(?:\.[\d]+)?|vX\.XX|v<ver>|<VER>|<version>|<ver>|<X\.XX>"

# 模式 A: 带版本号
PATTERN_WITH_VER = re.compile(
    r"((?:workflow_assets/)?(?:<REQ>|<req_name>/)?)("
    + "|".join(re.escape(s) for s in STAGES)
    + r")/(?P<ver>"
    + VERSION_PATTERN
    + r")"
)

# 模式 B: 无版本号 (AIDocxWorkFlow.mdc 表格 + 树状结构)
PATTERN_NO_VER = re.compile(
    r"((?:workflow_assets/)?<req_name>/)("
    + "|".join(re.escape(s) for s in STAGES)
    + r")/(?=[`\s\)\]\|])"
)


def rewrite_text(text):
    count = 0

    def repl_with_ver(m):
        nonlocal count
        count += 1
        return f"{m.group(1)}{m.group('ver')}/{m.group(2)}"

    def repl_no_ver(m):
        nonlocal count
        count += 1
        return f"{m.group(1)}<version>/{m.group(2)}/"

    text = PATTERN_WITH_VER.sub(repl_with_ver, text)
    text = PATTERN_NO_VER.sub(repl_no_ver, text)
    return text, count


def rewrite_file(path, dry_run=True):
    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
        return 0
    new, count = rewrite_text(original)
    if count > 0 and not dry_run:
        path.write_text(new, encoding="utf-8")
    return count


if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv
    targets = []
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            continue
        targets.append(Path(arg))

    total = 0
    for path in targets:
        if not path.exists():
            print(f"SKIP (missing): {path}")
            continue
        n = rewrite_file(path, dry_run=dry_run)
        if n > 0:
            print(f"{'DRY' if dry_run else 'OK '}: {path}  ({n} replacements)")
        total += n
    print(f"---\nTotal replacements: {total}")