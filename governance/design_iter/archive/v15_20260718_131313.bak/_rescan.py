#!/usr/bin/env python3
"""Re-scan target files and report violations per file."""
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(".").resolve()
spec = importlib.util.spec_from_file_location(
    "cc", ROOT / ".cursor/hooks/content_compliance_check.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
cfg = m.load_rules_config()
pats = m.get_compiled_patterns(cfg)

if len(sys.argv) > 1:
    rels = sys.argv[1:]
else:
    rels = sys.argv[1:]
total_high = 0
total_med = 0
for r in rels:
    vs = m.scan_file(ROOT / r, pats)
    high = sum(1 for v in vs if v["severity"] == "HIGH")
    med = sum(1 for v in vs if v["severity"] == "MEDIUM")
    total_high += high
    total_med += med
    print(f"{r}: HIGH={high} MEDIUM={med} TOTAL={len(vs)}")
    for v in vs:
        ctx = v["context"][:120]
        print(f"  [{v['type']}] {v['pattern']!r} ctx={ctx!r}")
print(f"TOTAL_HIGH={total_high} TOTAL_MED={total_med}")