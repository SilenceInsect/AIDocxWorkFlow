#!/usr/bin/env python3
"""Context-aware cleanup for the 14 target files.

Strategies:
  PERMANENT_RULE_VERSION_TAG: remove `<version_tag>` patterns like `v12 新增`, `v12+ 强制`, `v12 SSOT`
    - In tables: drop the parenthetical/grouped version-tag entirely
    - In paragraphs/headings: drop the parenthetical/grouped version-tag entirely
    - Preserve the rest of the surrounding text
  DOUBLE_VERSION: keep only the LAST version number
  FORBIDDEN_JSON_FIELDS: remove the whole `"version_note": "..."` or `"changelog": "..."` key/value pair
  ISO_TIMESTAMP: default KEEP (per task instructions: product meta.created_at style)

The script makes targeted per-line edits while preserving structure.
"""
from __future__ import annotations
import io
import re
import sys
import pathlib
from collections import OrderedDict

ROOT = pathlib.Path(".").resolve()

# Patterns
RE_DOUBLE_VERSION = re.compile(r"\b(v\d+(?:\.\d+)?)\s+(v\d+(?:\.\d+)?)\b")
RE_PERM_TAG = re.compile(r"\s*[（(](v\d+(?:\.\d+)?)\s*(\+?\s*(?:新增|SSOT|强制))(规则)?[)）]")
RE_PERM_TAG_NARRATIVE = re.compile(r"v\d+(?:\.\d+)?\s*(\+?\s*(?:新增|SSOT|强制))(规则)?")
RE_FORBIDDEN_JSON = re.compile(r'^\s*"(version_note|changelog)"\s*:\s*("[^"\n]*"|[^,\n}]+)\s*,?\s*\n', re.MULTILINE)


def strip_version_tag_in_table_row(line: str) -> str:
    """For table rows like `| xxx | xxx（v12 新增）| xxx |` → drop `（v12 新增）`."""
    new = RE_PERM_TAG.sub("", line)
    return new


def clean_perm_tag_inline(line: str) -> str:
    """Drop inline `v12 新增` patterns when not in parens (e.g. '**v16 新增**')."""
    # patterns like `**v16 新增 — ...**` or `**v16 新增（v16-NAME-001）：...**`
    # we want to drop `v16 新增` but keep the rest including the parenthetical tag id like v16-NAME-001
    return RE_PERM_TAG_NARRATIVE.sub("", line)


def clean_double_version(line: str) -> str:
    """Keep only the LAST version number, dropping the FIRST."""
    matches = list(RE_DOUBLE_VERSION.finditer(line))
    if not matches:
        return line
    # Replace each match by the second group
    for m in reversed(matches):
        line = line[: m.start()] + m.group(2) + line[m.end() :]
    return line


def clean_file(rel: str) -> tuple[int, str]:
    """Return (lines_changed, new_content)."""
    path = ROOT / rel
    content = path.read_text(encoding="utf-8")
    orig_lines = content.splitlines(keepends=True)
    new_lines: list[str] = []
    changes = 0

    for line in orig_lines:
        new = line

        # Step 1: forbidden JSON field lines (whole-line removal)
        if RE_FORBIDDEN_JSON.match(line):
            new = ""
            changes += 1
        else:
            # Step 2: double_version
            if RE_DOUBLE_VERSION.search(new):
                new = clean_double_version(new)
                changes += 1
            # Step 3: perm_tag in parens (table or paragraph context)
            if RE_PERM_TAG.search(new):
                new = strip_version_tag_in_table_row(new)
                changes += 1
            # Step 4: perm_tag inline (headings like `（v6.3 新增）` already covered)
            if RE_PERM_TAG_NARRATIVE.search(new):
                # only act if not already handled by parens; check if perm tags remain
                if RE_PERM_TAG_NARRATIVE.search(new):
                    new = clean_perm_tag_inline(new)
                    changes += 1
        new_lines.append(new)

    new_content = "".join(new_lines)
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
    return changes, new_content


def main() -> int:
    rels = sys.argv[1:]
    total_changes = 0
    for r in rels:
        changes, _ = clean_file(r)
        total_changes += changes
        print(f"{r}: changes={changes}")
    print(f"TOTAL_CHANGES={total_changes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())