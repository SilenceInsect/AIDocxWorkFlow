#!/usr/bin/env python3
"""Before/after stats for the 14 target files."""
import importlib.util
import pathlib

ROOT = pathlib.Path(".").resolve()
spec = importlib.util.spec_from_file_location(
    "cc", ROOT / ".cursor/hooks/content_compliance_check.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
cfg = m.load_rules_config()
pats = m.get_compiled_patterns(cfg)

orig = {
    ".cursor/MODULES.md": (20, 0),
    ".cursor/rules/AIDocxWorkFlow.mdc": (1, 0),
    ".cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc": (15, 1),
    ".cursor/rules/DNA_3Q_CHECK.mdc": (17, 3),
    ".cursor/rules/STAGE_S5_TEST_POINTS.mdc": (3, 0),
    ".cursor/rules/STAGE_S6_TEST_CASES.mdc": (6, 0),
    ".cursor/skills/aidocx-s2-breakdown/SKILL.md": (4, 0),
    ".cursor/skills/aidocx-s3-prototype/SKILL.md": (1, 0),
    ".cursor/skills/aidocx-s5-test-points/SKILL.md": (3, 0),
    ".cursor/skills/aidocx-s6-test-cases/SKILL.md": (2, 0),
    ".cursor/skills/aidocx-s7-review/SKILL.md": (1, 0),
    "ai_workflow/auto_reviewer.py": (3, 0),
    "ai_workflow/test_case_formatter.py": (3, 0),
    "governance/design_iter/plans/v13/PRODUCT_MANUAL.md": (1, 0),
}

h_o = h_n = m_o = m_n = 0
for r, (oh, om) in orig.items():
    vs = m.scan_file(ROOT / r, pats)
    nh = sum(1 for v in vs if v["severity"] == "HIGH")
    nm = sum(1 for v in vs if v["severity"] == "MEDIUM")
    h_o += oh
    h_n += nh
    m_o += om
    m_n += nm
    print(f"{r}  H {oh}->{nh}  M {om}->{nm}")

print()
print(f"HIGH  before={h_o}  after={h_n}  delta={h_o - h_n}")
print(f"MED   before={m_o}  after={m_n}  delta={m_o - m_n}")