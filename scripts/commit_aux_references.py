"""
commit_aux_to_util_references.py - 提交所有 AUX->UTIL 引用替换

提交信息说明：
- git mv 改名（AUX_expert_cognition.md -> UTIL_expert_cognition.md）
- git mv 改名（AUX_module_tp.json -> UTIL_module_tp.json）
- git add 所有文本替换
"""
import subprocess
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GIT_EXE = r"C:\Program Files\Git\bin\git.exe"


def run_git(*args, check=True):
    cmd = [GIT_EXE] + list(args)
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    if result.stdout:
        print(f"    stdout: {result.stdout.strip()}")
    if result.stderr:
        print(f"    stderr: {result.stderr.strip()}")
    if check and result.returncode != 0:
        print(f"  FAILED: returncode={result.returncode}")
    return result


def git_mv(src, dst):
    """git mv with fallback to manual rename"""
    r = run_git("mv", src, dst, check=False)
    if r.returncode != 0:
        # Fallback: manual rename
        src_path = REPO_ROOT / src
        dst_path = REPO_ROOT / dst
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            run_git("rm", "--cached", src)
            run_git("add", dst)
            print(f"  Manual mv: {src} -> {dst}")


def main():
    print("=" * 60)
    print("Step 1: Rename remaining files with AUX in name")
    print("=" * 60)

    renames = [
        ("knowledge/public/module_templates/_module_expert_cognition/AUX_expert_cognition.md",
         "knowledge/public/module_templates/_module_expert_cognition/UTIL_expert_cognition.md"),
        ("workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/_module_expert_drafts/AUX_module_tp.json",
         "workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/_module_expert_drafts/UTIL_module_tp.json"),
    ]

    for src, dst in renames:
        src_path = REPO_ROOT / src
        if src_path.exists():
            print(f"\n  Renaming: {src}")
            git_mv(src, dst)
        else:
            print(f"\n  Not found (skip): {src}")

    print("\n" + "=" * 60)
    print("Step 2: Stage all modified files")
    print("=" * 60)
    run_git("add", "-A")

    print("\n" + "=" * 60)
    print("Step 3: Git status")
    print("=" * 60)
    run_git("status", "--short")


if __name__ == "__main__":
    main()
