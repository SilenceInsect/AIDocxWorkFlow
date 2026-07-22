"""Commit helper for git UTIL rename"""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GIT_EXE = r"C:\Program Files\Git\bin\git.exe"

msg = """rename: UTIL->UTIL to resolve Windows reserved name conflict

- Rename all module_templates/UTIL/ and test_point_library/UTIL/ to UTIL/
- Rename module_templates/UTIL.md to module_templates/UTIL.md
- UTIL (Auxiliary) -> UTIL (Utilities): more semantically accurate
- Fixes Windows checkout failure due to reserved device name 'UTIL'
- Backup of AUX_ local copies preserved in governance/aux_rename_backup/
- All 19 files renamed via git rm --cached --sparse + git add
"""

result = subprocess.run(
    [GIT_EXE, "commit", "-m", msg],
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True
)
print("stdout:", result.stdout)
print("stderr:", result.stderr)
print("returncode:", result.returncode)
