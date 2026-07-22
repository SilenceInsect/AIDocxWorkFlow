"""
git_aux_rename.py - 解决 Windows 保留名 UTIL 的 git 重命名脚本（修正版）

步骤：
1. 重置之前错误复制的 UTIL 路径
2. 禁用 sparse-checkout
3. 从 git index 删除旧 UTIL 路径（使用 --sparse 标志）
4. 添加正确位置的 UTIL 文件
5. 更新 sparse-checkout
6. 提交
"""
import subprocess
import sys
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BACKUP_ROOT = REPO_ROOT / "governance" / "aux_rename_backup"
GIT_EXE = r"C:\Program Files\Git\bin\git.exe"
SPARSE_CONFIG = REPO_ROOT / ".git" / "info" / "sparse-checkout"


def run_git(*args, check=True, capture=True):
    cmd = [GIT_EXE] + list(args)
    print(f"  Running: {' '.join(cmd)}")
    kwargs = {"capture_output": True, "text": True} if capture else {}
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), **kwargs)
    if capture:
        if result.stdout:
            print(f"    stdout: {result.stdout.strip()}")
        if result.stderr:
            print(f"    stderr: {result.stderr.strip()}")
    if check and result.returncode != 0:
        print(f"  FAILED: returncode={result.returncode}")
        # Don't exit on rm failures - they might be already gone
    return result


def main():
    print("=" * 60)
    print("Step 0: Reset incorrect UTIL additions (wrong path)")
    print("=" * 60)
    run_git("reset", "HEAD", "--", "module_templates/UTIL/", "module_templates/UTIL.md", "test_point_library/UTIL/", check=False)

    print("\n" + "=" * 60)
    print("Step 1: Disable sparse-checkout")
    print("=" * 60)
    write_sparse = SPARSE_CONFIG.write_text if SPARSE_CONFIG.exists() else lambda x: None
    # Read old sparse first
    old_sparse = SPARSE_CONFIG.read_text() if SPARSE_CONFIG.exists() else "/*"
    SPARSE_CONFIG.write_text("/*")
    print("  Set sparse-checkout to /* (all files)")

    print("\n" + "=" * 60)
    print("Step 2: Remove old UTIL from git index (with --sparse)")
    print("=" * 60)
    old_paths = [
        "knowledge/public/module_templates/UTIL/",
        "knowledge/public/module_templates/UTIL.md",
        "knowledge/public/test_point_library/UTIL/",
    ]
    for path in old_paths:
        print(f"\n  Removing: {path}")
        # Try with --sparse flag
        r = run_git("rm", "--cached", "--sparse", "-r", path, check=False)
        r = run_git("rm", "--cached", "--sparse", path, check=False)

    print("\n" + "=" * 60)
    print("Step 3: Stage correct UTIL files")
    print("=" * 60)
    util_src = [
        ("knowledge/public/module_templates/UTIL/", BACKUP_ROOT / "module_templates" / "AUX_"),
        ("knowledge/public/module_templates/UTIL.md", BACKUP_ROOT / "module_templates" / "AUX_.md"),
        ("knowledge/public/test_point_library/UTIL/", BACKUP_ROOT / "test_point_library" / "AUX_"),
    ]
    for git_path, src_path in util_src:
        dest = REPO_ROOT / git_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src_path.exists():
            if src_path.is_dir():
                shutil.copytree(src_path, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dest)
            print(f"  Copied: {src_path} -> {dest}")
        run_git("add", git_path)

    print("\n" + "=" * 60)
    print("Step 4: Restore sparse-checkout (UTIL -> UTIL)")
    print("=" * 60)
    new_sparse = old_sparse.replace("UTIL", "UTIL")
    SPARSE_CONFIG.write_text(new_sparse)
    print(f"New sparse-checkout:\n{new_sparse}")

    print("\n" + "=" * 60)
    print("Step 5: Delete local AUX_ copies")
    print("=" * 60)
    local_copies = [
        REPO_ROOT / "knowledge" / "public" / "module_templates" / "AUX_",
        REPO_ROOT / "knowledge" / "public" / "module_templates" / "AUX_.md",
        REPO_ROOT / "knowledge" / "public" / "test_point_library" / "AUX_",
    ]
    for path in local_copies:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"  Deleted: {path}")

    print("\n" + "=" * 60)
    print("Step 6: Git status")
    print("=" * 60)
    run_git("status", "--short")


if __name__ == "__main__":
    main()
