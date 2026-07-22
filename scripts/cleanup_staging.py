"""Clean up unwanted staged files before commit"""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GIT_EXE = r"C:\Program Files\Git\bin\git.exe"

# Reset these from staging area (don't untrack)
UNSTAGE = [
    "ai_workflow/__pycache__/",
    "governance/aux_rename_backup/",
    "scripts/bulk_replace_aux_to_util.py",
    "scripts/commit_aux_references.py",
    "scripts/git_aux_rename.py",
    "scripts/git_commit_rename.py",
    ".cursor/skills/merge-expert/",
]

def run_git(*args):
    cmd = [GIT_EXE] + list(args)
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    print(f"  {' '.join(cmd)}: {result.returncode}")
    if result.stdout:
        print(f"    {result.stdout.strip()}")
    return result

def main():
    print("Unstaging unwanted files...")
    for path in UNSTAGE:
        run_git("reset", "HEAD", "--", path)

    print("\nFinal git status (first 30 lines):")
    result = run_git("status", "--short")

if __name__ == "__main__":
    main()
