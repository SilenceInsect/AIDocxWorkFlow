#!/usr/bin/env python3
"""R4 防御 hook A：阻止写入 .cursor/skills/*/SKILL.md

触发：
  beforeFileEdit / beforeSubmitPrompt（Cursor hook 协议）
  stdin JSON:
    beforeFileEdit: {"event":"beforeFileEdit","tool_input":{"file_path":"..."}}
    beforeSubmitPrompt: {"event":"beforeSubmitPrompt","prompt":"...","target_file":"..."}

行为：
  - 命中 .cursor/skills/*/SKILL.md → exit 2 + stderr 错误信息（Cursor 协议：exit 2 = block）
  - 环境变量 GOAL_SKILL_EDIT_ALLOWED=1 → 绕过（仅 R4 验收用）
  - 其他路径 → exit 0（允许）

设计约束：
  - 失败绝不让 IDE 崩溃（任何异常返回 exit 0）
  - 必须含 self_test() + --self-test argv 分支
  - 与 goal_loop_breakloop_hook.py 共享 REPO_ROOT + sys.path.insert 约定
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PROTECTED_PATTERN = ".cursor/skills/*/SKILL.md"
BYPASS_ENV = "GOAL_SKILL_EDIT_ALLOWED"


def _is_protected_skill_md(target_path: str) -> bool:
    """判断目标路径是否命中 .cursor/skills/*/SKILL.md 模式。"""
    if not target_path:
        return False
    # 归一化（兼容 Windows / 绝对路径 / 相对路径）
    try:
        p = PurePosixPath(target_path.replace("\\", "/"))
    except Exception:
        return False
    return p.match(".cursor/skills/*/SKILL.md") or p.match("*/.cursor/skills/*/SKILL.md")


def check(target_path: str) -> tuple[bool, str]:
    """检查目标路径是否允许写入。

    Returns:
        (allowed, reason) — allowed=True 允许；allowed=False + reason 解释
    """
    if not target_path:
        return True, "no target path provided"

    if os.environ.get(BYPASS_ENV) == "1":
        return True, f"bypassed by {BYPASS_ENV}=1"

    if _is_protected_skill_md(target_path):
        return False, (
            f"Blocked: {target_path} 命中 SKILL.md 防护模式 {PROTECTED_PATTERN}。"
            f"SKILL.md 只允许人工/Plan 阶段编辑，禁止 subagent/afterFileEdit 写入。"
            f"若需紧急编辑请设置环境变量 {BYPASS_ENV}=1。"
        )

    return True, "not a protected SKILL.md path"


def _extract_target_path(payload: dict) -> str:
    """从 stdin payload 抽取目标路径（兼容多 event 形态）。"""
    if not isinstance(payload, dict):
        return ""
    # beforeFileEdit: tool_input.file_path
    ti = payload.get("tool_input") or {}
    if isinstance(ti, dict):
        fp = ti.get("file_path") or ti.get("path") or ti.get("filePath")
        if fp:
            return str(fp)
    # beforeSubmitPrompt: target_file（扩展字段）
    tf = payload.get("target_file") or payload.get("file_path")
    if tf:
        return str(tf)
    # 兜底：grep string fields
    for k in ("file_path", "target_file", "path"):
        v = payload.get(k)
        if isinstance(v, str) and v:
            return v
    return ""


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return 0
    except Exception:
        return 0

    target = _extract_target_path(payload)
    allowed, reason = check(target)
    if not allowed:
        # Cursor hook 协议：exit 2 = block；stderr 给错误信息
        print(reason, file=sys.stderr)
        return 2
    return 0


def self_test() -> int:
    """python3 .cursor/hooks/goal_loop_skill_md_protection.py --self-test

    验证 8 项：
      1. 命中 .cursor/skills/goal-loop/SKILL.md → blocked
      2. 命中 .cursor/skills/aidocx-s7-review/SKILL.md → blocked
      3. 命中绝对路径 /Users/.../.cursor/skills/x/SKILL.md → blocked
      4. 命中 .cursor/skills/goal-loop/README.md → allowed（非 SKILL.md）
      5. 命中 .cursor/skills/goal-loop/SKILL.md.bak → allowed（不在 glob 范围）
      6. 命中 .cursor/rules/xxx.mdc → allowed
      7. 空 payload → allowed
      8. bypass env GOAL_SKILL_EDIT_ALLOWED=1 → allowed
    """
    import os

    cases = [
        (".cursor/skills/goal-loop/SKILL.md", False, "relative goal-loop SKILL.md"),
        (".cursor/skills/aidocx-s7-review/SKILL.md", False, "aidocx-* SKILL.md"),
        ("/Users/x/project/.cursor/skills/x/SKILL.md", False, "absolute path SKILL.md"),
        (".cursor/skills/goal-loop/README.md", True, "README.md (not SKILL.md)"),
        (".cursor/skills/goal-loop/SKILL.md.bak", True, ".bak extension"),
        (".cursor/rules/xxx.mdc", True, "rules dir"),
        ("", True, "empty path"),
    ]

    for path, expected_allowed, desc in cases:
        allowed, reason = check(path)
        assert allowed == expected_allowed, (
            f"Case '{desc}': expected allowed={expected_allowed}, got {allowed} (reason={reason!r})"
        )
        print(f"  [OK] Case '{desc}': allowed={allowed}")

    # Case 8: bypass env
    os.environ[BYPASS_ENV] = "1"
    try:
        allowed, reason = check(".cursor/skills/goal-loop/SKILL.md")
        assert allowed, f"Case 8: bypass env 应 allowed, got blocked (reason={reason!r})"
        print(f"  [OK] Case 8: {BYPASS_ENV}=1 → allowed")
    finally:
        os.environ.pop(BYPASS_ENV, None)

    # 验证未被破坏：移除 env 后再次拒绝
    allowed, reason = check(".cursor/skills/goal-loop/SKILL.md")
    assert not allowed, "Case 9: 移除 bypass env 后应再次拒绝"
    print(f"  [OK] Case 9: 移除 bypass env 后再次拒绝")

    print(f"  [OK] self_test passed (9 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())
