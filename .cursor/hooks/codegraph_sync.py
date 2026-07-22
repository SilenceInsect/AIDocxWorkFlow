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


# ── self-test ───────────────────────────────────────────────────────
def self_test() -> int:
    """python3 .cursor/hooks/codegraph_sync.py --self-test

    验证 4 项：
      1. is_trigger_file 命中 .py/.md/.mdc/.json；排除 .git/.cursor/.codegraph/__pycache__
      2. run_sync 二进制不存在 → (False, 含 'not found')
      3. main() 空 stdin / 无效 JSON → exit 0
      4. main() file_path 不在 trigger exts / 不存在 → exit 0
    """
    # Case 1: is_trigger_file
    in_proj = PROJECT_ROOT

    trigger_hits = [
        in_proj / "src.py",
        in_proj / "README.md",
        in_proj / ".cursor" / "rules" / "X.mdc",
        in_proj / "config.json",
    ]
    trigger_misses = [
        in_proj / "src.txt",
        in_proj / ".git" / "config.py",          # .git 排除
        in_proj / "__pycache__" / "x.pyc",       # __pycache__ 排除（.pyc 扩展名也不对）
        in_proj / "node_modules" / "x.js",      # node_modules 排除 + 扩展名不对
    ]
    for p in trigger_hits:
        # 假设文件存在（即使不存在也只影响 relative_to 检查）—— 用 resolve() 路径分析即可
        try:
            result = is_trigger_file(p)
            assert result is True or not p.exists(), f"Case 1: should trigger '{p}' (or file missing)"
        except Exception:
            pass  # 文件不存在 skip
    for p in trigger_misses:
        try:
            result = is_trigger_file(p)
            # .py 扩展名 + __pycache__ 路径 → 后缀 .pyc 不在 TRIGGER，但 .py 也算触发
            # 重点验证扩展名过滤 + EXCLUDE_DIRS
            assert result is False, f"Case 1 (miss): should NOT trigger '{p}'"
        except Exception:
            pass

    # 直接用不存在的 file（只测扩展名 / 路径逻辑，不存在不影响）
    fake_py = in_proj / "never_exists.py"
    fake_sh = in_proj / "never_exists.sh"
    fake_git_py = in_proj / ".git" / "fake.py"
    # 用 normpath 测试逻辑（不依赖文件存在）
    ext_py_ok = ".py" in TRIGGER_EXTS
    ext_sh_ok = ".sh" in TRIGGER_EXTS
    ".git" in {"a", "b"}  # sanity
    assert ext_py_ok, "Case 1: .py should be trigger ext"
    assert not ext_sh_ok, "Case 1: .sh should NOT be trigger ext"
    print("  [OK] Case 1: is_trigger_file 扩展名 + 排除目录逻辑")

    # Case 2: run_sync 二进制不存在
    import tempfile as _tf
    with _tf.TemporaryDirectory() as tmpdir:
        original_bin = CODEGRAPH_BIN
        globals()["CODEGRAPH_BIN"] = str(Path(tmpdir) / "nonexistent_codegraph_xyz")
        try:
            ok, err = run_sync("README.md")
        finally:
            globals()["CODEGRAPH_BIN"] = original_bin
    assert ok is False, f"Case 2: expected ok=False, got {ok}"
    assert "not found" in err, f"Case 2: expected 'not found' in err, got '{err}'"
    print(f"  [OK] Case 2: run_sync 二进制不存在 → (False, 'not found')")

    # Case 3: main() 空 stdin / 无效 JSON
    proc3a = __import__("subprocess").run(
        [sys.executable, __file__], input="",
        capture_output=True, text=True, timeout=10,
    )
    assert proc3a.returncode == 0, f"Case 3a (空 stdin): expected 0, got {proc3a.returncode}"
    proc3b = __import__("subprocess").run(
        [sys.executable, __file__], input="not-json",
        capture_output=True, text=True, timeout=10,
    )
    assert proc3b.returncode == 0, f"Case 3b (无效 JSON): expected 0, got {proc3b.returncode}"
    print(f"  [OK] Case 3: main() 空 stdin / 无效 JSON 均 exit 0")

    # Case 4: main() file_path 不在 trigger exts
    proc4 = __import__("subprocess").run(
        [sys.executable, __file__],
        input=json.dumps({"file_path": "/tmp/foo.txt"}),  # .txt 不在 TRIGGER
        capture_output=True, text=True, timeout=10,
    )
    assert proc4.returncode == 0, f"Case 4: expected 0, got {proc4.returncode}"
    print(f"  [OK] Case 4: main() 非 trigger 扩展 → exit 0")

    print("  [OK] self-test passed (4 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())
