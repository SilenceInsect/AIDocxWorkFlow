#!/usr/bin/env python3
"""知识库增量索引钩子：在 Cursor 编辑 module_templates 文件后自动触发增量索引。

触发：
  afterFileEdit（Cursor hook 协议）
  stdin JSON: {"event":"afterFileEdit","tool_input":{"file_path":"..."}}

行为：
  - 检测编辑的 .md 文件属于哪个模块（从路径解析）
  - 提取模块 ID（如 UI/CONFIG/BIZ/UTIL/LINK/SPECIAL/LOG/HINT）
  - 异步执行增量索引（subprocess，不阻塞主线程）
  - 错误降级：任何异常 → exit 0

设计约束：
  - 失败绝不让 IDE 卡顿（subprocess + timeout）
  - 只索引变更的模块，不全量重跑
  - 与 knowledge_indexer.py 共用 manifest diff 逻辑
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HOOK_SCRIPT = REPO_ROOT / "ai_workflow" / "knowledge_indexer.py"
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python3"

# 8 个合法模块 ID（与 .cursor/MODULES.md §1 总表 1:1 对齐）
LEGAL_MODULES = ("CONFIG", "UI", "BIZ", "UTIL", "LINK", "SPECIAL", "LOG", "HINT")


def _extract_module(target_path: str) -> str | None:
    """从 knowledge/public/module_templates/<MODULE>/... 提取模块 ID。"""
    normalized = target_path.replace("\\", "/")
    parts = normalized.split("/")
    try:
        idx = parts.index("module_templates")
    except ValueError:
        return None
    if len(parts) <= idx + 1:
        return None
    module = parts[idx + 1]
    return module if module in LEGAL_MODULES else None


def _run_indexer(module: str) -> None:
    """在后台线程执行增量索引。"""
    try:
        subprocess.run(
            [
                str(VENV_PYTHON),
                str(HOOK_SCRIPT),
                "--module", module,
                "--incremental",
                "--quiet",
            ],
            capture_output=True,
            timeout=120,
            cwd=str(REPO_ROOT),
        )
    except Exception:
        # 静默降级，不影响用户工作流
        pass


def main() -> None:
    """Hook 入口：解析 stdin → 提取模块 → 触发增量索引。"""
    try:
        raw = sys.stdin.read()
        if not raw:
            sys.exit(0)
        payload = json.loads(raw)
    except Exception:
        sys.exit(0)

    event = payload.get("event", "")
    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if event != "afterFileEdit" or not file_path:
        sys.exit(0)

    module = _extract_module(file_path)
    if not module:
        sys.exit(0)

    # 后台线程执行，不阻塞 Cursor
    t = threading.Thread(target=_run_indexer, args=(module,), daemon=True)
    t.start()

    sys.exit(0)


if __name__ == "__main__":
    # self-test
    if "--self-test" in sys.argv:
        tests = [
            # (input, expected_module_or_none)
            ("knowledge/public/module_templates/UI/A_control_basic.md", "UI"),
            ("knowledge/public/module_templates/CONFIG/H_export_publish.md", "CONFIG"),
            ("knowledge/public/module_templates/BIZ/B_business_flow.md", "BIZ"),
            ("knowledge/public/module_templates/_candidates/UI/foo.md", None),
            ("knowledge/public/module_templates/UI.md", None),
            ("some/other/path.md", None),
        ]
        passed = 0
        for path, expected in tests:
            result = _extract_module(path)
            ok = result == expected
            status = "PASS" if ok else "FAIL"
            print(f"  [{status}] _extract_module({path!r}) → {result!r} (expected {expected!r})")
            if ok:
                passed += 1
        print(f"\n{passed}/{len(tests)} passed")
        sys.exit(0 if passed == len(tests) else 1)

    main()
