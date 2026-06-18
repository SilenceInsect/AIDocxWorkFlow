#!/usr/bin/env bash
# AIDocxWorkFlow — one-shot install script
#
# What this does (in order, all idempotent):
#   1. Verify Python ≥ 3.10 and pip available.
#   2. (optional) install Python deps from requirements.txt.
#   3. Install the Hermes-only skill `aidocx-batch-runner` if `hermes` is on
#      PATH.  Skipped silently if hermes is not installed (so the script
#      still works for Cursor-only users).
#   4. Run `python3 ai_workflow/validate_skills.py .cursor/skills` to
#      confirm the 13 SKILL.md files match agentskills.io 1.0.
#   5. Enable local git hooks (.githooks/) so codegraph sync runs on
#      git checkout / pull / rebase. Skipped silently if not a git repo
#      or if the user has set core.hooksPath to something custom.
#   6. Print a one-page summary of what's installed and what's next.
#
# Usage:
#   ./install.sh            # full run
#   ./install.sh --no-deps  # skip pip install (for offline machines)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

INSTALL_DEPS=1
for arg in "$@"; do
  case "$arg" in
    --no-deps) INSTALL_DEPS=0 ;;
    -h|--help)
      sed -n '2,18p' "$0"
      exit 0
      ;;
  esac
done

# ── colors (ANSI-C quoting so \033 is a real escape, not 4 chars) ───────
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
RED=$'\033[0;31m'
CYAN=$'\033[0;36m'
BOLD=$'\033[1m'
RESET=$'\033[0m'

step() { printf "\n${CYAN}${BOLD}▶ %s${RESET}\n" "$1"; }
ok()   { printf "  ${GREEN}✓${RESET} %s\n" "$1"; }
warn() { printf "  ${YELLOW}!${RESET} %s\n" "$1"; }
fail() { printf "  ${RED}✗${RESET} %s\n" "$1"; }

# ── 1. python sanity ─────────────────────────────────────────────────────
step "1/6 Checking Python"
if ! command -v python3 >/dev/null 2>&1; then
  fail "python3 not found on PATH. Install Python 3.10+ first."
  exit 1
fi
PY_VERSION="$(python3 -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PY_MAJOR="${PY_VERSION%%.*}"
PY_MINOR="${PY_VERSION#*.}"
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  fail "Python $PY_VERSION found; need 3.10+."
  exit 1
fi
ok "Python $PY_VERSION"

# ── 2. pip install ───────────────────────────────────────────────────────
step "2/6 Python dependencies"
if [ "$INSTALL_DEPS" -eq 0 ]; then
  warn "Skipped (--no-deps)."
elif [ -f requirements.txt ]; then
  if python3 -m pip install -q -r requirements.txt 2>/dev/null; then
    ok "Installed from requirements.txt"
  else
    warn "pip install failed; continuing (deps may already be present or pip is locked)."
  fi
else
  warn "No requirements.txt found; skipping."
fi

# ── 3. Hermes install (optional) ────────────────────────────────────────
step "3/6 Hermes skill: aidocx-batch-runner (optional)"
HERMES_SKILL_SRC="workflow_assets/hermes_skills/aidocx-batch-runner"
if [ ! -d "$HERMES_SKILL_SRC" ]; then
  warn "Source directory $HERMES_SKILL_SRC missing — skipped. (Hermes integration is optional; this repo ships only Cursor skills.)"
elif command -v hermes >/dev/null 2>&1; then
  HERMES_VERSION="$(hermes --version 2>/dev/null || echo 'unknown')"
  ok "hermes CLI detected (${HERMES_VERSION})"
  if hermes skills install "$HERMES_SKILL_SRC" 2>&1 | tee /tmp/hermes-install.log; then
    ok "Installed $HERMES_SKILL_SRC into hermes."
  else
    warn "hermes skills install returned non-zero; check /tmp/hermes-install.log."
  fi
else
  warn "hermes CLI not on PATH. Skipped."
  warn "To install hermes + this skill later, follow SETUP_SUPERPOWERS_HERMES.md."
fi

# ── 4. validate SKILL.md ────────────────────────────────────────────────
step "4/6 Validating SKILL.md (agentskills.io 1.0)"
if python3 ai_workflow/validate_skills.py .cursor/skills 2>&1 | tee /tmp/skill-validate.log | tail -3; then
  if grep -q "0 errors, 0 warnings" /tmp/skill-validate.log; then
    ok "13/13 SKILL.md files pass agentskills.io 1.0."
  else
    warn "Validation produced warnings — see /tmp/skill-validate.log."
  fi
else
  fail "validate_skills.py failed; see /tmp/skill-validate.log."
  exit 1
fi

# v3 DNA 3 问 hook 自检（确保 hook 能跑）
if python3 .cursor/hooks/dna_violation_check.py --self-test >/dev/null 2>&1; then
  ok "[3Q-CHECK] dna_violation_check.py self-test passed (v3 mechanism live)"
else
  warn "[3Q-CHECK] dna_violation_check.py self-test failed; DNA violation detection disabled."
fi

# ── 5. git hooks ──────────────────────────────────────────────────────────
step "5/6 Enabling local git hooks (.githooks/)"
if [ ! -d .git ]; then
  warn "Not a git repository; skipped. (git hooks only apply inside git repos.)"
elif [ ! -d .githooks ]; then
  warn ".githooks/ directory missing; skipped. (Are you on an old checkout?)"
else
  CURRENT_HOOKS_PATH="$(git config --get core.hooksPath 2>/dev/null || echo '')"
  if [ "$CURRENT_HOOKS_PATH" = ".githooks" ]; then
    ok "core.hooksPath already set to .githooks — nothing to do."
  elif [ -n "$CURRENT_HOOKS_PATH" ]; then
    warn "core.hooksPath is already '$CURRENT_HOOKS_PATH' (custom); not overriding."
    warn "If you want AIDocxWorkFlow's hooks, run: git config core.hooksPath .githooks"
  else
    if git config core.hooksPath .githooks; then
      ok "Set core.hooksPath = .githooks (3 hooks: post-checkout / post-merge / post-rewrite)"
    else
      warn "Failed to set core.hooksPath; you can do it manually:"
      warn "  git config core.hooksPath .githooks"
    fi
  fi
fi

# ── 6. summary ───────────────────────────────────────────────────────────
step "6/6 Summary"
cat <<EOF

${BOLD}Installed:${RESET}
  • 12 stage SKILL.md + 1 aidocx-feedback-logger (Cursor auto-loaded)
  • Cursor hooks: sync_modules_table, codegraph_sync, feedback_logger, docx_hook, project_dna_inject, before_prompt_dna_check
    (afterFileEdit + beforeSubmitPrompt + sessionStart + sessionEnd, see .cursor/hooks.json)
  • git hooks: post-checkout / post-merge / post-rewrite (codegraph sync on git ops)
  • (Optional) Hermes skill: aidocx-batch-runner — installed only if 'hermes' CLI is on PATH and the source dir exists.

${BOLD}Next steps:${RESET}
  1. Restart Cursor so the new hooks.json takes effect.
  2. Open this folder in Cursor. Type ${CYAN}/aidocx-workflow${RESET} to start.
  3. (Optional) In Cursor chat run: ${CYAN}/add-plugin superpowers${RESET}
     to add the Superpowers meta-skills (TDD, systematic-debugging, etc.).

${BOLD}Troubleshooting:${RESET}
  • Logs: /tmp/skill-validate.log, /tmp/hermes-install.log
  • Per-stage failures: workflow_assets/<req>/「S*」/fail_report_S*.md
  • Per-session feedback: workflow_assets/feedback_logs/session_*.jsonl

EOF
