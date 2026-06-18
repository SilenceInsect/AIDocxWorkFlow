#!/usr/bin/env python3
"""AIDocxWorkFlow 每次提问前置自检（beforeSubmitPrompt hook）

作用：
  - 用户按 Enter 提交 prompt 时检测"方案/设计/重构"类问题
  - 强制注入"3 问自检"到 system reminder
  - 不阻断——只提醒

触发：
  .cursor/hooks.json -> beforeSubmitPrompt array -> {command: before_prompt_dna_check.py}

协议：
  stdin: JSON {"prompt": "..."}
  stdout: JSON {"system_reminder": "..."}（追加到 system reminder）
  exit 0: 正常 / 其它: 失败
"""

from __future__ import annotations

import json
import re
import sys

DNA_3Q_CHECK = """[项目 DNA 必做自检——每次回答前先问 3 问]

Q1（人本可审查）: 我的回答/方案，人能不能在 5 分钟内直接看懂？
                反模式: 术语堆砌 / 多层嵌套 / "技术正确但人难懂"
Q2（必然好论证）: 我有"为什么这个结构能避免再发生"的论证吗？
                反模式: 只列方案不论证 / 给方案不解释"为什么"
Q3（约束 vs 知识）: 内容是"约束"(Agent 必读) 还是"知识"(人查阅)？
                反模式: 混在一起 / alwaysApply: true 滥用

违反任一 → 重新组织答案。

参考: AGENTS.md + .cursor/design_iter/INDEX.md
"""

DESIGN_KEYWORDS = [
    # 中文
    "方案", "设计", "重构", "规划", "建议", "怎么改", "怎么调", "策略", "架构", "如何", "怎么",
    # 英文
    "plan", "design", "refactor", "how to", "should", "strategy", "architecture",
]


def is_design_question(prompt: str) -> bool:
    pl = prompt.lower()
    return any(kw.lower() in pl for kw in DESIGN_KEYWORDS)


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0
    except Exception:  # noqa: BLE001
        return 0

    prompt = data.get("prompt", "") or ""
    if not prompt or not is_design_question(prompt):
        return 0

    # 输出 system reminder（Cursor 会追加到 system reminder）
    output = {
        "system_reminder": DNA_3Q_CHECK,
    }
    print(json.dumps(output, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        # hook 崩了——降级，不阻断用户 prompt
        sys.stderr.write(f"[DNA-PROMPT-CHECK-CRASH] {type(exc).__name__}: {exc}\n")
        sys.stderr.flush()
        sys.exit(0)
