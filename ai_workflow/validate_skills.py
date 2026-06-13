"""
agentskills.io 规范验证器 — AIDocxWorkFlow skills 合规性检查

规范来源：https://agentskills.io/specification
- SKILL.md 必须存在
- YAML frontmatter 必填 name + description
- name: 1-64 字符，kebab-case（[a-z0-9-]，不以 - 开头/结尾，无连续 --）
- name 必须 == 父目录名
- description: 1-1024 字符，必须包含触发短语（"Use when"/"使用当"/"Triggered"/"用于" 之一）
- 可选字段 license / compatibility / metadata / allowed-tools

退出码：
  0 = 全部合规
  1 = 至少一个 skill 有 ERROR 级违规（阻断性）
  2 = 有 WARNING 但无 ERROR（如可选字段缺失、字段未识别）
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# agentskills.io 规范定义
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_OPTIONAL_FIELDS = {"license", "compatibility", "metadata", "allowed-tools"}
# Cursor 私有但与 agentskills.io 兼容的字段（不视为违规）
CURSOR_COMPAT_FIELDS = {"disable-model-invocation"}
# description 必含触发短语，但触发短语只能从以下词集中识别
ALL_KNOWN_FIELDS = ALLOWED_OPTIONAL_FIELDS | CURSOR_COMPAT_FIELDS
TRIGGER_PHRASES = [
    "use when", "use this", "use for", "use to",
    "使用当", "用于", "触发", "triggered", "trigger when",
    "load when", "activate when", "apply when",
]
MIN_DESCRIPTION_LEN = 50  # 经验值，太短难以让 agent 识别触发场景
RECOMMENDED_DESCRIPTION_LEN = 100
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_COMPATIBILITY_LEN = 500


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    """解析 --- ... --- 之间的 YAML frontmatter。返回 (frontmatter, error)。"""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, "文件不以 --- 开头，缺少 YAML frontmatter"
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, "YAML frontmatter 未闭合（缺少第二个 ---）"
    yaml_block = "\n".join(lines[1:end_idx])
    if not HAS_YAML:
        # 退化：手写极简解析
        fm: dict[str, Any] = {}
        current_key = None
        current_val_lines: list[str] = []
        in_multiline = False
        for line in yaml_block.split("\n"):
            if in_multiline:
                if line.startswith("  ") or line.strip() == "":
                    current_val_lines.append(line.strip())
                    continue
                else:
                    fm[current_key] = " ".join(s for s in current_val_lines if s)
                    in_multiline = False
                    current_val_lines = []
            if ":" in line and not line.startswith(" "):
                key, _, val = line.partition(":")
                val = val.strip()
                if val == ">" or val == "|" or val == "":
                    in_multiline = True
                    current_key = key.strip()
                    current_val_lines = []
                else:
                    fm[key.strip()] = val
        if in_multiline and current_key:
            fm[current_key] = " ".join(s for s in current_val_lines if s)
        return fm, None
    try:
        data = yaml.safe_load(yaml_block)
        if not isinstance(data, dict):
            return None, f"YAML frontmatter 不是字典（实际类型 {type(data).__name__}）"
        return data, None
    except yaml.YAMLError as e:
        return None, f"YAML 解析失败：{e}"


def validate_skill(skill_path: Path) -> dict[str, Any]:
    """验证单个 SKILL.md。返回带 errors/warnings 的报告。"""
    report: dict[str, Any] = {
        "name": skill_path.parent.name,
        "path": str(skill_path),
        "errors": [],
        "warnings": [],
        "info": [],
    }
    if not skill_path.exists():
        report["errors"].append("SKILL.md 不存在")
        return report
    text = skill_path.read_text(encoding="utf-8")
    if not text.strip():
        report["errors"].append("SKILL.md 为空")
        return report
    fm, err = parse_frontmatter(text)
    if err:
        report["errors"].append(err)
        return report
    if fm is None:
        report["errors"].append("frontmatter 解析失败")
        return report
    # name 校验
    if "name" not in fm:
        report["errors"].append("缺少必填字段 'name'")
    else:
        name = str(fm["name"])
        if not isinstance(name, str) or not name:
            report["errors"].append("'name' 必须是非空字符串")
        else:
            if len(name) > MAX_NAME_LEN:
                report["errors"].append(f"'name' 长度 {len(name)} 超过 {MAX_NAME_LEN} 字符上限")
            if not NAME_RE.match(name):
                report["errors"].append(
                    f"'name' 格式不合法（必须是 kebab-case：仅小写字母/数字/单连字符，不以 - 开头或结尾）"
                )
            if name != skill_path.parent.name:
                report["errors"].append(
                    f"'name' 字段值 '{name}' 与父目录名 '{skill_path.parent.name}' 不一致"
                )
    # description 校验
    if "description" not in fm:
        report["errors"].append("缺少必填字段 'description'")
    else:
        desc = str(fm["description"])
        if not desc.strip():
            report["errors"].append("'description' 为空")
        else:
            if len(desc) > MAX_DESCRIPTION_LEN:
                report["errors"].append(
                    f"'description' 长度 {len(desc)} 超过 {MAX_DESCRIPTION_LEN} 字符上限"
                )
            if len(desc) < MIN_DESCRIPTION_LEN:
                report["warnings"].append(
                    f"'description' 仅 {len(desc)} 字符，低于建议下限 {MIN_DESCRIPTION_LEN}（影响 agent 触发识别）"
                )
            elif len(desc) < RECOMMENDED_DESCRIPTION_LEN:
                report["info"].append(
                    f"'description' {len(desc)} 字符，介于 {MIN_DESCRIPTION_LEN}-{RECOMMENDED_DESCRIPTION_LEN}，建议补充更多触发短语"
                )
            desc_lower = desc.lower()
            has_trigger = any(phrase in desc_lower for phrase in TRIGGER_PHRASES)
            if not has_trigger:
                report["warnings"].append(
                    f"'description' 未包含任何触发短语（推荐：{TRIGGER_PHRASES[:3]}）"
                )
    # 可选字段校验
    for key, val in fm.items():
        if key in {"name", "description"}:
            continue
        if key not in ALLOWED_OPTIONAL_FIELDS:
            if key in CURSOR_COMPAT_FIELDS:
                report["info"].append(
                    f"Cursor 兼容字段 '{key}'（agentskills.io 不识别但 Cursor Agent 需要，保留）"
                )
            else:
                report["warnings"].append(
                    f"未识别的字段 '{key}'（agentskills.io 仅识别：{', '.join(sorted(ALLOWED_OPTIONAL_FIELDS))}）"
                )
        elif key == "compatibility" and len(str(val)) > MAX_COMPATIBILITY_LEN:
            report["errors"].append(
                f"'compatibility' 长度 {len(str(val))} 超过 {MAX_COMPATIBILITY_LEN} 字符上限"
            )
    # 必备段落检查（弱警告）
    body = text.split("---", 2)[-1].lower() if text.count("---") >= 2 else text.lower()
    if "## " not in body and "# " not in body:
        report["warnings"].append("正文缺少 Markdown 标题结构（建议至少 1 个 H1/H2）")
    return report


def main(skills_dir: str, output_json: str | None = None) -> int:
    root = Path(skills_dir)
    if not root.is_dir():
        print(f"[FATAL] skills 目录不存在：{root}", file=sys.stderr)
        return 2
    skill_files = sorted(root.glob("*/SKILL.md"))
    if not skill_files:
        print(f"[FATAL] 在 {root} 下未发现任何 */SKILL.md", file=sys.stderr)
        return 2
    reports = [validate_skill(p) for p in skill_files]
    # 打印人读报告
    print("=" * 70)
    print(f" agentskills.io 合规性报告 — {root}")
    print("=" * 70)
    total_errors = 0
    total_warnings = 0
    for r in reports:
        status = "✓" if not r["errors"] else "✗"
        print(f"\n[{status}] {r['name']}")
        for e in r["errors"]:
            print(f"    ERROR   : {e}")
            total_errors += 1
        for w in r["warnings"]:
            print(f"    WARNING : {w}")
            total_warnings += 1
        for i in r["info"]:
            print(f"    INFO    : {i}")
    print("\n" + "=" * 70)
    print(f" 扫描 {len(reports)} 个 skill：{total_errors} errors, {total_warnings} warnings")
    print("=" * 70)
    if output_json:
        Path(output_json).write_text(
            json.dumps(
                {
                    "skills_dir": str(root),
                    "total": len(reports),
                    "errors": total_errors,
                    "warnings": total_warnings,
                    "reports": reports,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\n[JSON 报告] {output_json}")
    if total_errors:
        print("\n结论：存在阻断性违规，修复后方可发布到 Hermes / Claude Code / Codex")
        return 1
    if total_warnings:
        print("\n结论：合规但有警告，建议优化以提升 agent 触发识别率")
        return 0
    print("\n结论：全部合规 ✓")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python validate_skills.py <skills_dir> [output_json]")
        sys.exit(2)
    skills_dir = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(main(skills_dir, output_json))
