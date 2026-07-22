#!/usr/bin/env python3
"""R4 防御 hook B：验证 .cursor/skills/*/SKILL.md 完整性

触发：
  sessionStart（Cursor hook 协议）
  stdin JSON: {"event":"sessionStart", ...}（可忽略具体 payload）

行为：
  - 扫描 .cursor/skills/ 下每个子目录的 SKILL.md
  - 每个 SKILL.md 检查 3 项：
    1. 首行 = YAML frontmatter `---`
    2. 含 `# ` 标题（不是 `# T-NNN Worker 报告`）
    3. 含至少 1 个 `## ` 二级标题
  - 任一不通过 → print stderr 警告 + 建议 `git checkout HEAD -- <path>`
  - 可选 `--restore <path>` argv 分支：人工恢复（HEAD checkout）

设计约束：
  - 失败绝不让 IDE 崩溃（任何异常返回 exit 0）
  - 必须含 self_test() + --self-test argv 分支
  - 与 goal_loop_breakloop_hook.py 共享 REPO_ROOT
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = REPO_ROOT / ".cursor" / "skills"

# YAML frontmatter 第一行
EXPECTED_FRONT_MATTER_LINE = "---"
# 损坏信号：worker 报告的开头
WORKER_REPORT_PREFIX = "# T-"


def check_skill_md(skill_path: Path) -> tuple[bool, list[str]]:
    """检查单个 SKILL.md 完整性。

    Returns:
        (ok, issues) — ok=True 无问题；ok=False + issues 描述问题列表
    """
    issues: list[str] = []

    if not skill_path.exists():
        return True, []  # 文件不存在不属于完整性问题（可能未初始化）

    try:
        text = skill_path.read_text(encoding="utf-8")
    except OSError as e:
        return False, [f"无法读取: {e}"]

    lines = text.splitlines()
    if not lines:
        return False, ["文件为空"]

    # Check 1: 首行 = YAML frontmatter
    if lines[0].strip() != EXPECTED_FRONT_MATTER_LINE:
        issues.append(
            f"首行非 YAML frontmatter (实际: {lines[0][:60]!r})"
        )

    # Check 2: 不是 worker 报告开头
    first_50 = "\n".join(lines[:50])
    if any(line.startswith(WORKER_REPORT_PREFIX) for line in lines[:5]):
        issues.append("疑似被 worker 报告覆盖（首 5 行含 '# T-NNN'）")

    # Check 3: 含至少 1 个 `## ` 二级标题
    if "## " not in first_50:
        issues.append("首 50 行无 `## ` 二级标题")

    # Check 4: 含 `# ` 一级标题
    if "# " not in first_50:
        issues.append("首 50 行无 `# ` 一级标题")

    return (len(issues) == 0), issues


def scan_all_skills() -> list[tuple[Path, bool, list[str]]]:
    """扫描所有 .cursor/skills/*/SKILL.md。

    Returns:
        [(skill_path, ok, issues), ...]
    """
    results: list[tuple[Path, bool, list[str]]] = []
    if not SKILLS_DIR.exists():
        return results

    for sub in sorted(SKILLS_DIR.iterdir()):
        if not sub.is_dir():
            continue
        skill_md = sub / "SKILL.md"
        ok, issues = check_skill_md(skill_md)
        results.append((skill_md, ok, issues))

    return results


def _emit_warning(results: list[tuple[Path, bool, list[str]]]) -> None:
    """打印警告到 stderr（不阻塞）。"""
    bad = [(p, iss) for p, ok, iss in results if not ok]
    if not bad:
        return
    print(
        f"[SKILL.md 完整性警告] 共 {len(bad)} 个 SKILL.md 异常:",
        file=sys.stderr,
    )
    for p, issues in bad:
        rel = p.relative_to(REPO_ROOT)
        print(f"  - {rel}", file=sys.stderr)
        for iss in issues:
            print(f"      · {iss}", file=sys.stderr)
        print(
            f"      · 恢复: git checkout HEAD -- {rel}",
            file=sys.stderr,
        )


def _restore_skill(skill_path: Path) -> int:
    """人工恢复：从 HEAD checkout 指定 SKILL.md。"""
    rel = str(skill_path.relative_to(REPO_ROOT))
    try:
        result = subprocess.run(
            ["git", "checkout", "HEAD", "--", rel],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print(f"已恢复: {rel}")
            return 0
        print(f"恢复失败 (exit={result.returncode}): {result.stderr}", file=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f"恢复异常: {e}", file=sys.stderr)
        return 1


def main() -> int:
    try:
        raw = sys.stdin.read()
        # sessionStart 可能无 payload；正常解析即可
        if raw.strip():
            try:
                json.loads(raw)
            except json.JSONDecodeError:
                pass
    except OSError:
        return 0
    except Exception:
        return 0

    # 扫描 + 警告（不阻断，仅 stderr + JSON stdout 注入 reminder）
    try:
        results = scan_all_skills()
    except Exception:
        return 0

    bad = [(p, iss) for p, ok, iss in results if not ok]
    if bad:
        _emit_warning(results)
        # 通过 stdout 注入 system_reminder（Cursor 协议）
        try:
            reminder = {
                "system_reminder": (
                    "[SKILL.md 完整性告警] "
                    f"{len(bad)} 个 SKILL.md 异常，请人工运行 "
                    "`python3 .cursor/hooks/goal_loop_skill_md_integrity.py --scan` "
                    "查看详情，或 `git checkout HEAD -- <path>` 恢复。"
                )
            }
            print(json.dumps(reminder, ensure_ascii=False), flush=True)
        except Exception:
            pass

    return 0


def self_test() -> int:
    """python3 .cursor/hooks/goal_loop_skill_md_integrity.py --self-test

    验证 6 项：
      1. 检查完整的 SKILL.md → ok=True
      2. 检查首行非 `---` 的损坏文件 → ok=False + issue 含 "首行非 YAML"
      3. 检查 worker 报告风格的损坏文件 → ok=False + issue 含 "worker 报告"
      4. 检查无 `## ` 二级标题的文件 → ok=False + issue 含 "无 `## `"
      5. 不存在的路径 → ok=True（不视为完整性问题）
      6. scan_all_skills 找到当前真实 SKILL.md（goal-loop）
    """
    import tempfile

    # Case 1: 完整 SKILL.md
    with tempfile.TemporaryDirectory() as td:
        good_skill = Path(td) / "good" / "SKILL.md"
        good_skill.parent.mkdir(parents=True)
        good_skill.write_text(
            "---\nname: test\n---\n# Test Title\n\n## Section 1\n",
            encoding="utf-8",
        )
        ok, issues = check_skill_md(good_skill)
        assert ok, f"Case 1: 完整 SKILL.md 应 ok, got issues={issues}"
        print(f"  [OK] Case 1: 完整 SKILL.md → ok")

    # Case 2: 首行非 `---`
    with tempfile.TemporaryDirectory() as td:
        bad_skill = Path(td) / "bad1" / "SKILL.md"
        bad_skill.parent.mkdir(parents=True)
        bad_skill.write_text(
            "# T-203 Worker Report\n\n## Section\n",
            encoding="utf-8",
        )
        ok, issues = check_skill_md(bad_skill)
        assert not ok, f"Case 2: 首行非 YAML 应 not ok, got ok"
        assert any("首行" in i for i in issues), f"Case 2: issues 应含'首行', got {issues}"
        print(f"  [OK] Case 2: 首行非 YAML → not ok + issue 含'首行'")

    # Case 3: worker 报告风格
    with tempfile.TemporaryDirectory() as td:
        bad_skill = Path(td) / "bad2" / "SKILL.md"
        bad_skill.parent.mkdir(parents=True)
        bad_skill.write_text(
            "# T-205 Worker 报告\n## Section\n",
            encoding="utf-8",
        )
        ok, issues = check_skill_md(bad_skill)
        assert not ok
        assert any("worker" in i.lower() for i in issues), f"Case 3: 应含 'worker', got {issues}"
        print(f"  [OK] Case 3: worker 报告风格 → not ok + issue 含 'worker'")

    # Case 4: 无 `## ` 二级标题
    with tempfile.TemporaryDirectory() as td:
        bad_skill = Path(td) / "bad3" / "SKILL.md"
        bad_skill.parent.mkdir(parents=True)
        bad_skill.write_text(
            "---\nname: test\n---\n# Title only\n",
            encoding="utf-8",
        )
        ok, issues = check_skill_md(bad_skill)
        assert not ok
        assert any("## " in i for i in issues), f"Case 4: 应含 '## ', got {issues}"
        print(f"  [OK] Case 4: 无 `## ` → not ok + issue 含 '## '")

    # Case 5: 不存在路径 → ok=True
    fake = Path("/nonexistent/path/SKILL.md")
    ok, issues = check_skill_md(fake)
    assert ok and issues == [], f"Case 5: 不存在应 ok=True, got {ok}/{issues}"
    print(f"  [OK] Case 5: 不存在路径 → ok=True")

    # Case 6: scan_all_skills 找到当前真实 SKILL.md（goal-loop）
    results = scan_all_skills()
    skill_names = [p.parent.name for p, _, _ in results]
    assert "goal-loop" in skill_names, f"Case 6: scan 应找到 goal-loop, got {skill_names}"
    # 验证 goal-loop 当前是 ok（刚刚 git checkout HEAD -- 恢复过）
    goal_loop_result = next(r for r in results if r[0].parent.name == "goal-loop")
    assert goal_loop_result[1], (
        f"Case 6: goal-loop SKILL.md 应 ok（已被 R3 恢复），got issues={goal_loop_result[2]}"
    )
    print(f"  [OK] Case 6: scan_all_skills 找到 goal-loop SKILL.md 且 ok=True ({len(results)} skills total)")

    print(f"  [OK] self_test passed (6 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) > 2 and sys.argv[1] == "--restore":
        target = Path(sys.argv[2])
        if not target.is_absolute():
            target = REPO_ROOT / target
        sys.exit(_restore_skill(target))
    if len(sys.argv) > 1 and sys.argv[1] == "--scan":
        # 人工调用：扫描并打印结果（exit 0 = 全 ok, exit 1 = 有损坏）
        results = scan_all_skills()
        bad = [(p, iss) for p, ok, iss in results if not ok]
        for p, ok, iss in results:
            rel = p.relative_to(REPO_ROOT)
            status = "OK" if ok else "BAD"
            print(f"[{status}] {rel}")
            for i in iss:
                print(f"      - {i}")
        sys.exit(1 if bad else 0)
    sys.exit(main())
