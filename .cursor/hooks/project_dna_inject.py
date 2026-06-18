#!/usr/bin/env python3
"""AIDocxWorkFlow 项目 DNA 注入器（sessionStart hook）

作用：
  - 会话启动时强制注入项目 DNA（AGENTS.md 内容）到 system reminder
  - 提示 v1 方案 + 5 决策状态
  - DNA 文件缺失则阻断（exit 1）

触发：
  .cursor/hooks.json -> sessionStart array -> {command: project_dna_inject.py}

输出：
  stdout: DNA 文本（被 Cursor 注入到 system reminder）
  exit 0: 正常 / exit 1: DNA 缺失（阻断会话）
"""

from __future__ import annotations

import signal
import sys
from pathlib import Path

# SIGPIPE 防御：head/tail 等管道关闭时不抛 BrokenPipeError
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DNA_FILE = _PROJECT_ROOT / "AGENTS.md"
PLAN_FILE = _PROJECT_ROOT / ".cursor" / "design_iter" / "plans" / "v1" / "PLAN.md"
OPEN_Q_FILE = _PROJECT_ROOT / ".cursor" / "design_iter" / "plans" / "v1" / "open_questions.md"


def _read_safely(path: Path, max_lines: int | None = None) -> str:
    """读取文件，失败/不存在返回空字符串——不抛异常"""
    try:
        if not path.exists():
            return ""
        text = path.read_text(encoding="utf-8")
        if max_lines:
            text = "\n".join(text.splitlines()[:max_lines])
        return text
    except Exception as exc:  # noqa: BLE001
        return f"[读取失败: {type(exc).__name__}: {exc}]"


def main() -> int:
    # 1) DNA 必读——缺失则阻断
    dna = _read_safely(DNA_FILE)
    if not dna:
        sys.stderr.write(
            f"[DNA-FAIL] AGENTS.md 不存在或为空：{DNA_FILE}\n"
            "项目铁律未注入——按项目 DNA 准则，会话必须阻断。\n"
        )
        sys.stderr.flush()
        return 1

    # 2) v1 方案状态（不阻断，仅提示）
    plan_exists = PLAN_FILE.exists()
    open_q_exists = OPEN_Q_FILE.exists()

    open_q_count = 0
    if open_q_exists:
        for line in _read_safely(OPEN_Q_FILE).splitlines():
            if line.strip().startswith("- [ ]"):
                open_q_count += 1

    # 3) 输出到 stdout（被 Cursor 注入到 system reminder）
    sep = "=" * 60
    sys.stdout.write(
        "\n"
        + sep + "\n"
        + "[AIDocxWorkFlow 项目 DNA 已注入]\n"
        + sep + "\n\n"
        + dna + "\n\n"
        + sep + "\n"
        + "[方案迭代状态]\n"
        + sep + "\n"
        + f"- v1 方案文件存在: {plan_exists}\n"
        + f"- v1 遗留问题清单存在: {open_q_exists}\n"
        + f"- v1 未解决问题数: {open_q_count}\n"
        + "- 当前生效: .cursor/design_iter/current 软链\n"
        + "- 操作: python3 .cursor/design_iter/scripts/design_iter.py status\n\n"
        + sep + "\n"
        + "[必做自检] 每次回答前问 3 问：\n"
        + "  Q1: 人能不能直接看懂？\n"
        + "  Q2: 方案有'必然好'论证吗？\n"
        + "  Q3: 内容是'约束'还是'知识'？\n"
        + sep + "\n"
    )
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        # hook 自身崩了——降级到 exit 0，不阻断会话
        sys.stderr.write(f"[DNA-HOOK-CRASH] {type(exc).__name__}: {exc}\n")
        sys.stderr.flush()
        sys.exit(0)
