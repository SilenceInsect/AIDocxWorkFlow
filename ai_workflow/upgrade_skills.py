"""
批量升级现有 skills 到 agentskills.io 完全兼容 + Cursor 兼容。

策略：在 frontmatter 末尾追加可选字段 + 在 description 中追加触发短语，
不动 name / description 的核心内容（不破坏现有 Cursor 触发行为）。
同时为每个 skill 加 compatibility / license / metadata 块。

用法:
    python3 ai_workflow/upgrade_skills.py .cursor/skills --dry-run
    python3 ai_workflow/upgrade_skills.py .cursor/skills
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

TRIGGER_LINE_EN = "Use when the user runs an AIDocxWorkFlow stage command, pastes stage input material, or asks to perform this stage's task."

# 13 个 skill 各自的追加触发短语（中文 + 英文双重触发）
TRIGGERS_PER_SKILL: dict[str, list[str]] = {
    "aidocx-feedback-logger": [
        "Use when importing test case execution feedback from Excel/CSV/JSON files.",
        "使用当需要从 Excel/CSV/JSON 文件导入测试用例执行反馈时。",
    ],
    "aidocx-s1-5-clarification": [
        "Use when the user has finished filling clarification_checklist.md and says '已完成'/'已填写'/'好了'.",
        "使用当 S1 评审通过后，用户已人工填写 clarification_checklist.md 并准备完善终版需求.md 时。",
    ],
    "aidocx-s1-review": [
        "Use when the user runs /aidocx-s1-review, pastes raw requirements, or starts a Stage 1 review task.",
        "使用当用户执行 /aidocx-s1-review、粘贴原始需求文档、或进行 S1 需求评审任务时。",
    ],
    "aidocx-s2-5-iteration": [
        "Use when the user runs /aidocx-s2-5-iteration, pastes S2 backlog, or starts iteration planning.",
        "使用当用户执行 /aidocx-s2-5-iteration、粘贴 S2 backlog、或进行 S2.5 迭代规划任务时。",
    ],
    "aidocx-s2-breakdown": [
        "Use when the user runs /aidocx-s2-breakdown, provides S1.5 exit_permission path, or starts requirement breakdown.",
        "使用当用户执行 /aidocx-s2-breakdown、提供 S1.5 准出许可路径、或进行 S2 需求拆解任务时。",
    ],
    "aidocx-s3-prototype": [
        "Use when the user runs /aidocx-s3-prototype, pastes S2 backlog, or starts prototype export.",
        "使用当用户执行 /aidocx-s3-prototype、粘贴 S2 backlog、或进行 S3 原型导出任务时。",
    ],
    "aidocx-s4-flowchart": [
        "Use when the user runs /aidocx-s4-flowchart, pastes S2 backlog + S3 prototype, or starts flowchart export.",
        "使用当用户执行 /aidocx-s4-flowchart、粘贴 S2 backlog + S3 prototype、或进行 S4 流程图导出任务时。",
    ],
    "aidocx-s5-test-points": [
        "Use when the user runs /aidocx-s5-test-points, pastes S2 backlog, or starts test point generation.",
        "使用当用户执行 /aidocx-s5-test-points、粘贴 S2 backlog、或进行 S5 测试点生成任务时。",
    ],
    "aidocx-s6-test-cases": [
        "Use when the user runs /aidocx-s6-test-cases, pastes S5 test_points.json, or starts test case generation.",
        "使用当用户执行 /aidocx-s6-test-cases、粘贴 S5 test_points.json、或进行 S6 测试用例生成任务时。",
    ],
    "aidocx-s7-review": [
        "Use when the user runs /aidocx-s7-review, pastes S6 test_cases.json, or starts test case review.",
        "使用当用户执行 /aidocx-s7-review、粘贴 S6 test_cases.json、或进行 S7 用例审查任务时。",
    ],
    "aidocx-s8-self-iteration": [
        "Use when the user runs /aidocx-s8-self-iteration, pastes S7 review report, or starts self-iteration/root-cause analysis.",
        "使用当用户执行 /aidocx-s8-self-iteration、粘贴 S7 审查报告、或进行 S8 自迭代/根因分析任务时。",
    ],
    "aidocx-workflow": [
        "Use when generating test cases from requirements, breaking down requirements, creating prototypes/flowcharts, or any test case generation task.",
        "使用当从需求生成测试用例、拆解需求、创建原型/流程图、或任何测试用例生成任务时。",
    ],
    "aidocx-workflow-conversation": [
        "Use when the user wants to run the full S1-S7 pipeline in conversation mode, save tokens via Python automation engine + AI collaboration.",
        "使用当用户希望在纯对话模式下执行 AI 测试用例生成流水线（S1-S7）、通过 Python 自动化引擎 + AI 协作节省 token 时。",
    ],
}


def split_frontmatter_and_body(text: str) -> tuple[list[str], list[str], bool]:
    """把 SKILL.md 切成 (frontmatter 行列表, body 行列表, 是否有闭标记)。"""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return [], lines, False
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return [], lines, False
    return lines[1:end_idx], lines[end_idx + 1 :], True


def find_description_block(fm_lines: list[str]) -> tuple[int, int, bool]:
    """定位 description 字段起始行和结束行。返回 (start_idx, end_idx_exclusive, is_multiline)。"""
    start = None
    key = None
    for i, line in enumerate(fm_lines):
        stripped = line.strip()
        if stripped.startswith("description:"):
            key = "description"
            start = i
            value = stripped[len("description:"):].strip()
            if value in {">", "|"}:
                return i, len(fm_lines), True
            else:
                return i, i + 1, False
        if key == "description" and start is not None:
            if line.startswith(" ") or line.startswith("\t") or stripped == "":
                continue
            else:
                return start, i, False
    return start if start is not None else -1, len(fm_lines), False


def has_optional_field(fm_lines: list[str], field: str) -> bool:
    for line in fm_lines:
        if re.match(rf"^{re.escape(field)}\s*:", line):
            return True
    return False


def upgrade_one(skill_md: Path, dry_run: bool) -> tuple[bool, str]:
    """升级单个 SKILL.md。返回 (changed, summary)。"""
    text = skill_md.read_text(encoding="utf-8")
    fm_lines, body_lines, ok = split_frontmatter_and_body(text)
    if not ok:
        return False, "frontmatter 格式错误，跳过"
    parent_name = skill_md.parent.name
    triggers = TRIGGERS_PER_SKILL.get(parent_name)
    if triggers is None:
        return False, f"未配置 {parent_name} 的触发短语，跳过"
    original_len = len(fm_lines)
    new_fm = list(fm_lines)
    # 1. 追加触发短语到 description（如果 description 是 > 多行块，append 到块里；否则保持不动）
    desc_start, desc_end, is_multi = find_description_block(new_fm)
    if desc_start >= 0 and is_multi:
        # 在多行 description 块末尾追加触发短语
        for trig in triggers:
            new_fm.insert(desc_end, f"  {trig}")
            desc_end += 1
    elif desc_start >= 0 and not is_multi:
        # 单行 description：转成多行块 + 追加触发
        existing = new_fm[desc_start].split(":", 1)[1].strip()
        new_fm[desc_start] = "description: >"
        insert_at = desc_start + 1
        # 把原内容作为多行块第一行
        new_fm.insert(insert_at, f"  {existing}")
        insert_at += 1
        for trig in triggers:
            new_fm.insert(insert_at, f"  {trig}")
            insert_at += 1
    # 2. 追加 license（如缺失）
    if not has_optional_field(new_fm, "license"):
        new_fm.append("license: MIT")
    # 3. 追加 compatibility（如缺失）
    if not has_optional_field(new_fm, "compatibility"):
        new_fm.append(
            "compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent"
        )
    # 4. 追加 metadata（如缺失）
    if not has_optional_field(new_fm, "metadata"):
        new_fm.append("metadata:")
        new_fm.append("  framework: AIDocxWorkFlow")
        new_fm.append("  pipeline_stage: " + parent_name.replace("aidocx-", ""))
        new_fm.append("  spec_version: agentskills.io/1.0")
        new_fm.append("  cursor_compat: true")
    # 重组
    if len(new_fm) == original_len and desc_start < 0:
        return False, "无需修改"
    new_text = "---\n" + "\n".join(new_fm) + "\n---\n" + "\n".join(body_lines)
    # 前置条件：保持原文件结构
    if new_text == text:
        return False, "已合规（无修改）"
    if not dry_run:
        skill_md.write_text(new_text, encoding="utf-8")
    added = len(new_fm) - original_len
    return True, f"frontmatter +{added} 行（触发短语、license、compatibility、metadata）"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skills_dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(args.skills_dir)
    if not root.is_dir():
        print(f"[FATAL] 目录不存在：{root}")
        return 2
    files = sorted(root.glob("*/SKILL.md"))
    if not files:
        print(f"[FATAL] 在 {root} 下未发现 */SKILL.md")
        return 2
    print(f"=== 升级 skills 到 agentskills.io 全合规{' (DRY-RUN)' if args.dry_run else ''} ===\n")
    changed = 0
    for f in files:
        ok, msg = upgrade_one(f, args.dry_run)
        marker = "✓" if ok else "·"
        print(f"[{marker}] {f.parent.name}: {msg}")
        if ok:
            changed += 1
    print(f"\n共修改 {changed}/{len(files)} 个 skill")
    if args.dry_run:
        print("（DRY-RUN 模式：未实际写文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
