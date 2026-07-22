"""Final commit helper"""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GIT_EXE = r"C:\Program Files\Git\bin\git.exe"

msg = """refactor: replace AUX with UTIL across entire codebase

Breaking change: AUX module renamed to UTIL to resolve Windows reserved
device name conflict. 'AUX' is a reserved name on Windows (device driver),
preventing git clone/checkout on Windows systems.

Changes:
- Rename module_templates/AUX/ -> UTIL/ (18 files)
- Rename module_templates/AUX.md -> UTIL.md
- Rename test_point_library/AUX/ -> UTIL/ (1 file)
- Rename .cursor/skills/aux-expert/ -> util-expert/ (2 files)
- Rename _module_expert_cognition/AUX_expert_cognition.md -> UTIL_
- Rename v3.01 AUX_module_tp.json -> UTIL_module_tp.json
- Update all AUX->UTIL references in 130+ files across:
  .cursor/rules/*.mdc
  .cursor/skills/*/SKILL.md + _identity_card.md
  .cursor/MODULES.md
  ai_workflow/*.py
  knowledge/public/module_templates/*.md
  knowledge/public/test_point_library/*.md
  governance/design_iter/ (historical plans)
  .goal-log-db/active/ (goal snapshots)
  workflow_assets/ (per-requirement artifacts)

Rationale: UTIL (Utilities) is semantically more accurate than
AUX (Auxiliary) for a module focused on public utility functions,
network layer, cache, resource management, etc.

Note: 3 commit strategy:
  1. bea3172 - rename directories (git mv via --sparse)
  2. <this commit> - update all text references
  3. <next commit> - final verification

Scripts preserved in scripts/ for future reference:
  git_aux_rename.py, bulk_replace_aux_to_util.py, etc.
"""

# Stage all tracked changes
r1 = subprocess.run([GIT_EXE, "add", "-A"], cwd=str(REPO_ROOT), capture_output=True, text=True)
print("git add -A:", r1.returncode)

# Commit
r2 = subprocess.run(
    [GIT_EXE, "commit", "-m", msg],
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True
)
print("stdout:", r2.stdout)
print("stderr:", r2.stderr)
print("returncode:", r2.returncode)
