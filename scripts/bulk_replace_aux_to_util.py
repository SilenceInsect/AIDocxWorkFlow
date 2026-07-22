"""
bulk_replace_aux_to_util.py - 批量替换所有 UTIL -> UTIL 引用

处理范围：
1. 所有 .md/.mdc/.json 文件中的路径引用
2. 所有 .py 文件中的模块名、变量名、字符串
3. .cursor/skills/UTIL-expert/ 目录 -> util-expert/
"""
import re
import subprocess
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GIT_EXE = r"C:\Program Files\Git\bin\git.exe"

# 文件替换规则：匹配模式 -> 替换文本
# 注意：只替换作为独立标识符的 UTIL/UTIL，不替换文件内容中的自然语言 UTIL
REPLACEMENTS = [
    # === 路径引用 ===
    # module_templates/UTIL/ -> UTIL/
    (r"module_templates/UTIL/", "module_templates/UTIL/"),
    # test_point_library/UTIL/ -> UTIL/
    (r"test_point_library/UTIL/", "test_point_library/UTIL/"),
    # module_templates/UTIL\.md -> UTIL.md
    (r"module_templates/UTIL\.md", "module_templates/UTIL.md"),

    # === 文本引用（作为模块名）===
    # 匹配 "UTIL" 作为独立单词（前后有空格/标点/边界）
    (r"\bAUX\b", "UTIL"),

    # === UTIL-expert 目录和文件引用 ===
    # UTIL-expert -> util-expert
    (r"UTIL-expert", "util-expert"),
    (r"util_expert", "util_expert"),

    # === JSON 中的枚举值 ===
    (r'"UTIL"', '"UTIL"'),
    (r"'UTIL'", "'UTIL'"),

    # === 注释中的 UTIL 模块 ===
    (r"UTIL 模块", "UTIL 模块"),
    (r"UTIL 模块", "util 模块"),
]

# 需要跳过的文件（不处理这些文件的内容）
SKIP_FILES = {
    # 已改名完成的文件
    "knowledge/public/module_templates/UTIL/",
    "knowledge/public/module_templates/UTIL.md",
    "knowledge/public/test_point_library/UTIL/",
    "governance/aux_rename_backup/",  # 备份目录
    ".git/",
    "ai_workflow/__pycache__/",
    "workflow_assets/",  # 需求产物不处理
}

# 需要重命名的目录
DIR_RENAMES = [
    (".cursor/skills/UTIL-expert", ".cursor/skills/util-expert"),
]

# 需要在 git 中处理的路径（从 UTIL-* -> util-*）
GIT_RENAME_PATHS = [
    (".cursor/skills/UTIL-expert", ".cursor/skills/util-expert"),
]


def should_process(file_path: Path) -> bool:
    """判断是否处理该文件"""
    path_str = str(file_path)
    for skip in SKIP_FILES:
        if skip in path_str:
            return False
    # 只处理文本文件
    if file_path.suffix.lower() in {'.md', '.mdc', '.json', '.py', '.txt'}:
        return True
    return False


def replace_content(content: str) -> tuple[str, int]:
    """替换文件内容，返回 (新内容, 替换次数)"""
    new_content = content
    count = 0
    for pattern, replacement in REPLACEMENTS:
        new_content, n = re.subn(pattern, replacement, new_content, flags=re.IGNORECASE)
        count += n
    return new_content, count


def process_file(file_path: Path) -> int:
    """处理单个文件，返回替换次数"""
    if not should_process(file_path):
        return 0

    try:
        # 读取文件（尝试 UTF-8，失败则用 GBK）
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="gbk")
            except:
                return 0

        new_content, count = replace_content(content)

        if count > 0:
            # 写回文件
            file_path.write_text(new_content, encoding="utf-8")
            return count
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
    return 0


def rename_directory_git(src: Path, dst: Path):
    """通过 git mv 重命名目录"""
    if not src.exists():
        print(f"  Skip (not found): {src}")
        return

    print(f"  Renaming directory: {src} -> {dst}")

    # 读取所有文件
    files = list(src.rglob("*"))

    # 创建目标目录
    dst.mkdir(parents=True, exist_ok=True)

    # 复制所有文件到新位置
    for f in files:
        if f.is_file():
            rel = f.relative_to(src)
            dest_file = dst / rel
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest_file)

    # 从 git index 删除旧路径
    result = subprocess.run(
        [GIT_EXE, "rm", "--cached", "-r", "--sparse", str(src)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True
    )

    # 添加新路径到 git
    result = subprocess.run(
        [GIT_EXE, "add", str(dst)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True
    )

    # 删除旧目录
    shutil.rmtree(src)
    print(f"  Done: {src.name} -> {dst.name}")


def main():
    print("=" * 60)
    print("Step 1: Rename directories (UTIL-expert -> util-expert)")
    print("=" * 60)

    for src, dst in DIR_RENAMES:
        src_path = REPO_ROOT / src
        dst_path = REPO_ROOT / dst
        rename_directory_git(src_path, dst_path)

    print("\n" + "=" * 60)
    print("Step 2: Replace UTIL -> UTIL in all files")
    print("=" * 60)

    total_count = 0
    file_count = 0

    for file_path in REPO_ROOT.rglob("*"):
        if file_path.is_file() and should_process(file_path):
            count = process_file(file_path)
            if count > 0:
                print(f"  {file_path.relative_to(REPO_ROOT)}: {count} replacements")
                total_count += count
                file_count += 1

    print(f"\n  Total: {total_count} replacements in {file_count} files")

    print("\n" + "=" * 60)
    print("Step 3: Show git status")
    print("=" * 60)

    result = subprocess.run(
        [GIT_EXE, "status", "--short"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True
    )
    print(result.stdout)

    print("\nDone! Review changes above.")


if __name__ == "__main__":
    main()
