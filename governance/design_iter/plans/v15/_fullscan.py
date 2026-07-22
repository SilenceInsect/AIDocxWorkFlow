#!/usr/bin/env python3
"""Full repo scan: every file tracked by git, no exempt filter."""
import importlib.util
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(".").resolve()
spec = importlib.util.spec_from_file_location(
    "cc", ROOT / ".cursor/hooks/content_compliance_check.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
cfg = m.load_rules_config()
pats = m.get_compiled_patterns(cfg)

result = subprocess.run(
    ["git", "ls-files"],
    cwd=ROOT, capture_output=True, text=True, timeout=30,
)
files = [f for f in result.stdout.splitlines() if f]
all_v = []
for f in files:
    p = ROOT / f
    if not p.exists():
        continue
    if m.is_path_exempt(f, cfg):
        continue
    vs = m.scan_file(p, pats)
    all_v.extend(vs)
print(f"TOTAL HIGH={sum(v['severity']=='HIGH' for v in all_v)} MEDIUM={sum(v['severity']=='MEDIUM' for v in all_v)}")
buckets: dict[str, list] = {}
for v in all_v:
    buckets.setdefault(v["file"], []).append(v)
for f, vs in buckets.items():
    print(f"{f}: HIGH={sum(v['severity']=='HIGH' for v in vs)} MEDIUM={sum(v['severity']=='MEDIUM' for v in vs)}")
    for v in vs:
        ctx = v["context"][:100]
        print(f"  [{v['type']}] {v['pattern']!r} ctx={ctx!r}")