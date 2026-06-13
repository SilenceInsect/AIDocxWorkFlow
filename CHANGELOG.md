# Changelog

All notable changes to **AIDocxWorkFlow** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
for the **workflow pipeline** (S1 → S1.5 → S2 → S2.5 → S3 → S4 → S5 → S6 → S7 → S8).

`prompt` / `skill` / `rule` revisions do not bump the major version; they are
noted in the *Unreleased* section as they accumulate.

---

## [Unreleased]

### Added
- `aidocx-feedback-logger` skill — captures per-stage human feedback into
  `workflow_assets/feedback_logs/*.json` for later analysis.
- `aidocx-batch-runner` skill — Hermes-only helper to drive multiple
  requirements through the full 9-stage pipeline in sequence.
- `ai_workflow/validate_skills.py` — checks every `SKILL.md` against the
  [agentskills.io 1.0](.cursor/rules/SKILL_STANDARDS.md) spec. 0 errors / 0 warnings on the current set.
- `ai_workflow/upgrade_skills.py` — converts legacy `SKILL.md` frontmatter to the agentskills.io 1.0 format.
- `workflow_assets/validation_reports/skills_validation_v{1,2,3}.json` — three historical validation runs.
- `SETUP_SUPERPOWERS_HERMES.md` — manual install guide for Superpowers + Hermes skills.

### Changed
- `AIDocxWorkFlow.mdc` and the 7 `STAGE_*.mdc` rules: rewritten prompts to align
  with agentskills.io 1.0 naming and to reference the new verification tooling.
- All 12 existing `SKILL.md` files: upgraded to the agentskills.io 1.0
  `name` + `description` frontmatter format. Verified by
  `python3 ai_workflow/validate_skills.py .cursor/skills` (13/13 PASS).
- `README.md`: rewritten for public-facing team use; no longer assumes the reader
  has internal context.

### Notes
- The `cursor/integrate-superpowers-and-hermes-with-skill-standardization`
  branch is kept as a parallel "thin-pipeline" experiment. Its 6 deleted
  core Python modules and altered `hooks.json` are **intentionally not**
  merged into `main` — `main` is positioned as a clean, pure-conversation
  workflow.

---

## [1.0.0] — 2026-06-13

### Added
- Initial 9-stage pipeline (S1 → S8) under `workflow_assets/<req_name>/「Stage」/<version>/`.
- `.docx` / `.doc` input pipeline (`ai_workflow/stage_s1_input/`): `DocxExtractor`,
  `ImageRenamer`, `OCREngine`, `MarkdownConverter`, `S1Pipeline`.
- First end-to-end example: `游戏道具商城系统` (S1, S2.5, S3, S4, S5, S6, S8
  artifacts present; S1.5 / S2 / S7 documented in rules).
- Core Python modules for offline automation:
  - `ai_workflow/requirement_reviewer_auto.py` (S1 scoring)
  - `ai_workflow/feedback_logger.py` (S8)
  - `ai_workflow/iteration_aggregator.py` (S8)
  - `ai_workflow/auto_reviewer.py` (S7)
  - `ai_workflow/test_case_formatter.py` (S6)
  - `ai_workflow/conversation_skills.py` (chat-side skill routing)
- 12 `SKILL.md` (v1 format) under `.cursor/skills/`.
- 9 stage rules (`.cursor/rules/STAGE_S*.mdc`) and the top-level
  `.cursor/rules/AIDocxWorkFlow.mdc`.
