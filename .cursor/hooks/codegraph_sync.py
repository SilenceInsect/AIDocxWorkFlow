#!/usr/bin/env python3
"""Cursor afterFileEdit hook: codegraph 增量同步.

Trigger:
  - 任何 .py / .md / .mdc / .json 文件被编辑后,触发 codegraph sync

Mechanism:
  - 调 `codegraph sync -q`(增量, 静默)
  - codegraph 内部 lockfile 防重入, 钩子级联自动无副作用
  - 失败不阻塞 IDE 体验, 仅 stderr 提示

Output:
  - 日志:.cursor/sync_logs/codegraph_sync_YYYYMMDD.jsonl
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
SYNC_LOG_DIR = PROJECT_ROOT / ".cursor" / "sync_logs"
CODEGRAPH_BIN = os.environ.get("CODEGRAPH_BIN", "/Users/gleon/.local/bin/codegraph")

# 哪些扩展名触发 sync(与 CODEGRAPH 扫描范围对齐)
TRIGGER_EXTS = {".py", ".md", ".mdc", ".json"}

# 排除目录(避免噪音)
EXCLUDE_DIRS = {".git", ".cursor", ".codegraph", "__pycache__", "venv", "node_modules"}


def is_trigger_file(path: Path) -> bool:
    if path.suffix.lower() not in TRIGGER_EXTS:
        return False
    try:
        rel = path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        return False
    return not any(part in EXCLUDE_DIRS for part in rel.parts)


def write_log(entry: dict) -> None:
    try:
        SYNC_LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = SYNC_LOG_DIR / f"codegraph_sync_{datetime.now():%Y%m%d}.jsonl"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # 日志写不进不阻塞


def run_sync(file_rel: str) -> tuple[bool, str]:
    """调 codegraph sync -q. 返回 (success, stderr_text)."""
    if not Path(CODEGRAPH_BIN).exists():
        return (False, f"codegraph binary not found at {CODEGRAPH_BIN}")
    try:
        result = subprocess.run(
            [CODEGRAPH_BIN, "sync", "-q", str(PROJECT_ROOT)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (result.returncode == 0, result.stderr.strip())
    except subprocess.TimeoutExpired:
        return (False, "timeout after 30s")
    except Exception as exc:
        return (False, f"{type(exc).__name__}: {exc}")


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return 0

    file_path_str = payload.get("file_path", "")
    if not file_path_str:
        return 0

    edited = Path(file_path_str)
    if not edited.exists() or not is_trigger_file(edited):
        return 0

    try:
        rel = str(edited.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        rel = str(edited)

    # 防级联: codegraph 内部 lockfile 避免重入, 钩子级联调用会快速 no-op
    ok, err = run_sync(rel)

    write_log({
        "ts": datetime.now().isoformat(),
        "trigger_file": rel,
        "status": "synced" if ok else "error",
        "error": err if not ok else None,
    })

    if not ok:
        sys.stderr.write(f"[codegraph_sync] {rel}: {err}\n")
    return 0  # 永远返回 0, 不阻塞 IDE


if __name__ == "__main__":
    sys.exit(main())
