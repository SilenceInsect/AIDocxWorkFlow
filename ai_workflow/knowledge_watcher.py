#!/usr/bin/env python3
"""
knowledge_watcher.py
====================
后台守护进程：监听 module_templates 目录，文件变更时自动触发增量索引。

用法
----
```bash
# 前台运行（调试）
python -m ai_workflow.knowledge_watcher

# 后台常驻
python -m ai_workflow.knowledge_watcher --daemon

# 指定监听目录
python -m ai_workflow.knowledge_watcher --watch knowledge/public/module_templates

# 指定 debounce（ms）
python -m ai_workflow.knowledge_watcher --debounce 2000

# 立即触发一次全量重建后退出
python -m ai_workflow.knowledge_watcher --full-once
```
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path

# ── 依赖检查 ────────────────────────────────────────────────────────────────
try:
    import watchfiles
except ImportError:
    print("ERROR: watchfiles not installed. Run: pip install watchfiles", file=sys.stderr)
    sys.exit(1)

# ── 常量 ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
WATCH_ROOT = REPO_ROOT / "knowledge" / "public" / "module_templates"
INDEXER_SCRIPT = REPO_ROOT / "ai_workflow" / "knowledge_indexer.py"
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python3"
PID_FILE = REPO_ROOT / ".knowledge_watcher.pid"
LOG_FILE = REPO_ROOT / ".knowledge_watcher.log"

# 8 个合法模块 ID
LEGAL_MODULES = ("CONFIG", "UI", "BIZ", "UTIL", "LINK", "SPECIAL", "LOG", "HINT")

# ── 日志 ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
LOG = logging.getLogger("knowledge_watcher")


# ── 工具 ────────────────────────────────────────────────────────────────────
def _extract_module(file_path: str) -> str | None:
    """从 knowledge/public/module_templates/<MODULE>/... 提取模块 ID。"""
    normalized = file_path.replace("\\", "/")
    parts = normalized.split("/")
    try:
        idx = parts.index("module_templates")
    except ValueError:
        return None
    if len(parts) <= idx + 1:
        return None
    module = parts[idx + 1]
    return module if module in LEGAL_MODULES else None


def _run_indexer(module: str, incremental: bool = True, quiet: bool = True) -> dict | None:
    """执行索引脚本，返回解析后的 stats。"""
    cmd = [str(VENV_PYTHON), "-m", "ai_workflow.knowledge_indexer", "--module", module]
    if incremental:
        cmd.append("--incremental")
    if quiet:
        cmd.append("--quiet")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=180,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        else:
            LOG.error("Indexer failed for %s: %s", module, result.stderr.decode()[:200])
            return None
    except Exception as e:
        LOG.error("Indexer exception for %s: %s", module, e)
        return None


# ── 主类 ────────────────────────────────────────────────────────────────────
class KnowledgeWatcher:
    """
    文件监听器：监听 module_templates，变更时触发增量索引。

    核心逻辑：
    - watchfiles 检测文件变化（CREATE / MODIFY / DELETE）
    - debounce 合并同一模块的多次变更（如连续快速保存）
    - 变更聚合：等 debounce 窗口结束后对同一模块只触发一次增量
    """

    def __init__(
        self,
        watch_root: Path | None = None,
        debounce_ms: int = 1500,
        batch_interval_ms: int = 300,
    ):
        self.watch_root = Path(watch_root) if watch_root else WATCH_ROOT
        self.debounce_ms = debounce_ms
        self.batch_interval_ms = batch_interval_ms

        # 模块 → 最后触发时间
        self._last_triggered: dict[str, float] = {}
        # 待处理模块集合（debounce 窗口内的变更）
        self._pending_modules: set[str] = set()
        # 锁
        self._lock = threading.Lock()
        # 退出信号
        self._stop = threading.Event()

    def _is_relevant(self, file_path: str) -> bool:
        """是否是需要监听的相关文件。"""
        normalized = file_path.replace("\\", "/")
        return (
            normalized.endswith(".md")
            and "module_templates" in normalized
            and "_candidates" not in normalized
            and _extract_module(normalized) is not None
        )

    def _should_trigger(self, module: str) -> bool:
        """判断是否应该真正触发（debounce 过滤）。"""
        now = time.time() * 1000  # ms
        last = self._last_triggered.get(module, 0)
        return (now - last) >= self.debounce_ms

    def _trigger_module(self, module: str) -> None:
        """执行模块的增量索引。"""
        with self._lock:
            if not self._should_trigger(module):
                return
            self._last_triggered[module] = time.time() * 1000

        LOG.info("→ Triggering incremental index for module: %s", module)
        stats = _run_indexer(module, incremental=True, quiet=True)
        if stats:
            added = stats.get("added", "?")
            deleted = stats.get("deleted", "?")
            skipped = stats.get("skipped", "?")
            LOG.info(
                "  ✓ Indexed %s: deleted=%s, added=%s, skipped=%s",
                module, deleted, added, skipped,
            )
        else:
            LOG.warning("  ✗ Indexer failed for %s", module)

    def _process_changes(self, changed: list[tuple[str, int]]) -> None:
        """处理一批变更文件，聚合到模块级别后触发。"""
        modules_seen: set[str] = set()
        for file_path, _ in changed:
            if self._is_relevant(file_path):
                mod = _extract_module(file_path)
                if mod:
                    modules_seen.add(mod)

        for module in sorted(modules_seen):
            self._trigger_module(module)

    def run(self, once: bool = False) -> None:
        """启动监听循环。"""
        LOG.info(
            "Watching %s (debounce=%dms)...",
            self.watch_root,
            self.debounce_ms,
        )

        if not self.watch_root.exists():
            LOG.error("Watch root does not exist: %s", self.watch_root)
            sys.exit(1)

        if once:
            # 立即全量重建
            LOG.info("Full-once mode: rebuilding all modules...")
            for module in LEGAL_MODULES:
                LOG.info("→ Rebuilding: %s", module)
                _run_indexer(module, incremental=False, quiet=False)
            LOG.info("Full-once done.")
            return

        # 持续监听
        try:
            for changes in watchfiles.watch(
                self.watch_root,
                debounce=self.debounce_ms,
                step=50,
            ):
                if self._stop.is_set():
                    break
                if changes:
                    self._process_changes(changes)
        except KeyboardInterrupt:
            LOG.info("Interrupted by user.")
        finally:
            LOG.info("Watcher stopped.")


# ── PID 文件管理 ─────────────────────────────────────────────────────────────
def write_pid() -> None:
    pid_file = PID_FILE
    pid_file.write_text(str(os.getpid()), encoding="utf-8")
    LOG.info("PID %d written to %s", os.getpid(), pid_file)


def remove_pid() -> None:
    try:
        PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass


# ── CLI ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="监听 module_templates 文件变更，自动触发增量索引",
    )
    parser.add_argument(
        "--watch",
        type=Path,
        default=None,
        help="监听根目录（默认: knowledge/public/module_templates）",
    )
    parser.add_argument(
        "--debounce", "-d",
        type=int,
        default=1500,
        help="去抖动窗口 ms（默认 1500）",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="后台守护进程模式",
    )
    parser.add_argument(
        "--full-once",
        action="store_true",
        help="立即全量重建所有模块后退出",
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="停止后台守护进程",
    )
    args = parser.parse_args()

    # stop 命令
    if args.stop:
        if PID_FILE.exists():
            old_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            try:
                os.kill(old_pid, 15)
                print(f"Killed watcher PID {old_pid}")
            except ProcessLookupError:
                print(f"PID {old_pid} not found, removing stale PID file")
            except PermissionError:
                print(f"Permission denied to kill PID {old_pid}")
            remove_pid()
        else:
            print("No watcher running (PID file not found)")
        sys.exit(0)

    # daemon 模式
    if args.daemon:
        import daemon

        with daemon.DaemonContext(working_directory=REPO_ROOT):
            remove_pid()
            write_pid()
            watcher = KnowledgeWatcher(watch_root=args.watch, debounce_ms=args.debounce)
            watcher.run()
            remove_pid()
        sys.exit(0)

    # 前台模式
    if args.full_once:
        watcher = KnowledgeWatcher(watch_root=args.watch, debounce_ms=args.debounce)
        watcher.run(once=True)
    else:
        try:
            write_pid()
            watcher = KnowledgeWatcher(watch_root=args.watch, debounce_ms=args.debounce)
            watcher.run()
        finally:
            remove_pid()
