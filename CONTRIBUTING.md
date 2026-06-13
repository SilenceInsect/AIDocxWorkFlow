# Contributing to AIDocxWorkFlow

Thanks for your interest in making this workflow better. This file covers
the **day-to-day** contribution flow. If you only want to *use* the
pipeline, see `README.md` instead.

---

## TL;DR

```bash
git checkout -b feat/<short-topic>
# …make your changes…
python3 ai_workflow/validate_skills.py .cursor/skills   # must print "13/13 PASS"
git add -A
git commit -m "feat: <what & why>"
git push origin feat/<short-topic>
# Open a PR against main. Tag @SilenceInsect.
```

---

## What this repo is (and isn't)

| Layer | Lives in | Mutable on `main`? |
|---|---|---|
| **Prompts** (`.cursor/rules/*.mdc`) | yes | yes |
| **Skills** (`.cursor/skills/*/SKILL.md`) | yes | yes |
| **Validation tooling** (`ai_workflow/validate_skills.py`, `ai_workflow/upgrade_skills.py`) | yes | yes |
| **Stage example outputs** (`workflow_assets/<req_name>/「Stage」/<version>/`) | yes | yes (additive only) |
| **S1–S8 core Python modules** (`ai_workflow/{auto_reviewer,feedback_logger,…}.py`) | yes | **rarely** — see "Core modules" below |
| **`.gitignore`**, **`.cursor/hooks.json`** | yes | **rarely** — see "Hooks" below |

If your change touches something in the "rarely" rows, open the PR with
`CHANGELOG.md` updated and expect review from a maintainer.

---

## Branches

- **`main`** — the clean, pure-conversation workflow. Must always:
  - Build: `python3 ai_workflow/validate_skills.py .cursor/skills` returns 13/13 PASS.
  - Be self-contained: no required external services, no broken links.
- **`<type>/<short-topic>`** — feature/bugfix branches off `main`.
- **Legacy / experimental** — e.g.
  `cursor/integrate-superpowers-and-hermes-with-skill-standardization`:
  experimental thin-pipeline rewrite. May be force-pushed or rebased.
  **Do not** branch from it for production changes.

Branch types: `feat` `fix` `docs` `refactor` `chore` `test`.

---

## Editing prompts and skills

### `SKILL.md` rules

Every `SKILL.md` must follow
[agentskills.io 1.0](.cursor/rules/SKILL_STANDARDS.md). The two mandatory
top-of-file fields are:

```yaml
---
name: <kebab-case-skill-name>
description: <one-sentence; < 1024 chars; no "I"/"you"/"we">
---
```

Use the `disable-model-invocation: true` field on skills that should only
be triggered **manually** by the user (e.g. `aidocx-batch-runner`).

`validate_skills.py` will catch missing fields, bad frontmatter, and the
old v1 `name:`/`summary:` format. **Do not merge until the script prints
`0 errors, 0 warnings`.**

### Adding a new skill

1. Pick a directory: `.cursor/skills/<name>/SKILL.md` for general skills,
   or `workflow_assets/hermes_skills/<name>/SKILL.md` for Hermes-only skills.
2. Write the `SKILL.md` (see the standard).
3. If the skill should be discoverable from chat, register it in
   `ai_workflow/__init__.py`.
4. Run `python3 ai_workflow/validate_skills.py .cursor/skills`.
5. Add a one-line entry to `CHANGELOG.md` under `[Unreleased] / Added`.

### Editing a `STAGE_*.mdc` rule

1. Read the current rule in full — stage rules cross-reference each other
   (e.g. S7 references S4 risk points; S6 references S5 design methods).
2. Edit the **Markdown body** of the rule (gates, checklists, output schemas).
3. If the change is structural, update the matching
   `workflow_assets/<req_name>/` example output if you can.
4. Re-run the validation tooling and any stage example that depends on
   the rule.

---

## Core Python modules (rarely touched)

The 6 modules under `ai_workflow/` (`auto_reviewer.py`, `feedback_logger.py`,
`iteration_aggregator.py`, `requirement_reviewer_auto.py`, `test_case_formatter.py`,
`conversation_skills.py`) implement the **offline** parts of the pipeline
(S1 scoring, S7 review, S8 feedback, S6 formatting). They are intentionally
**not** required for a normal chat-driven run of the pipeline.

> If you're thinking of deleting or rewriting one of these, stop and
> think about whether the change is "switch to the agentskills.io
> version" (in which case, the answer might be a separate experimental
> branch, **not** `main`). The previous attempt to do this in commit
> `45f658d` was deliberately **not** merged into `main`.

If you must change one:

1. Open an issue first describing the use case.
2. Keep the public function signatures stable.
3. Update the corresponding example in `workflow_assets/<req_name>/` if
   the JSON shape changes.
4. Add a `CHANGELOG.md` entry.

---

## Hooks

`.cursor/hooks.json` controls what runs on `sessionStart`,
`beforeSubmitPrompt`, `afterAgentResponse`, etc. Changes here affect
**every developer** on the project. Touch this file only if:

- You're adding a hook that helps everyone (e.g. the SKILL validator
  proposed in the experimental branch).
- You can run it locally for a week without false positives.
- The hook's output is **idempotent** (running it twice must be safe).

If unsure, open a draft PR with the hook disabled
(`"type": "prompt"`) so reviewers can see the intent without auto-running it.

---

## Commit messages

```
<type>(<scope>): <one-line summary, imperative mood, < 72 chars>

<body — why, not what; wrap at 72 chars>

<footer — closes #123, breaks-change notes>
```

Common types: `feat` `fix` `docs` `refactor` `chore` `test` `perf`.

For multi-commit work, **rebase** rather than merging `main` into your
feature branch (keeps the log linear and the PR diff clean).

---

## Pull request checklist

- [ ] Branch is off `main` and rebased on it.
- [ ] `python3 ai_workflow/validate_skills.py .cursor/skills` passes.
- [ ] If you changed a `STAGE_*.mdc` rule, you re-ran the corresponding
      stage example and updated its output if needed.
- [ ] `CHANGELOG.md` updated under `[Unreleased]` (or `[X.Y.Z]` for
      breaking changes).
- [ ] No `.DS_Store` / `__pycache__` / `*.pyc` accidentally staged.
- [ ] PR description has: what / why / how to test / screenshots if UI.

---

## Code of conduct

Be kind. Be patient. The workflow is for everyone, not just you. Reviews
are not gatekeeping; they're a sanity check. If a reviewer is unclear,
ask.

---

## License

By contributing, you agree that your contributions will be licensed
under the [MIT License](LICENSE).
