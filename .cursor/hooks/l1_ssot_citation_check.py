#!/usr/bin/env python3
"""L1 SSOT 引用路径校验 hook（afterFileEdit 事件）

作用：
  - 扫描编辑后的 .mdc / .md / SKILL.md 文件，提取 SSOT 引用路径
  - 验证引用路径在 SSOT 文件（DESIGN_AND_EXECUTION_STANDARDS.mdc / STAGE_S*.mdc / MODULES.md）中是否存在
  - WARN 级别（不阻断执行），记录到 feedback_logs/ssot_citation_warns.jsonl

SSOT 参考源（按优先级）：
  1. .cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc
  2. .cursor/rules/STAGE_S*.mdc
  3. .cursor/MODULES.md
  4. .cursor/skills/aidocx-*/SKILL.md

触发：
  .cursor/hooks.json -> afterFileEdit array -> {command: l1_ssot_citation_check.py}

协议：
  stdin: JSON {"file_path": "...", "session_id": "..."}
  stdout: 无
  exit 0: 软记录 / exit 1: 严重错误（如 SSOT 文件本身解析失败）
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── 配置 ─────────────────────────────────────────────────────────────────────
WORKSPACE = Path("/Users/gleon/Documents/TestDev/AIDocxWorkFlow")
SSOT_FILES = [
    WORKSPACE / ".cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc",
    WORKSPACE / ".cursor/MODULES.md",
]
SSOT_RULES_DIR = WORKSPACE / ".cursor/rules"
SSOT_SKILLS_DIR = WORKSPACE / ".cursor/skills"
LOG_FILE = WORKSPACE / "workflow_assets/feedback_logs/ssot_citation_warns.jsonl"

# 支持的文件后缀
TARGET_EXTENSIONS = {".mdc", ".md", ".SKILL.md"}

# SSOT 引用正则（匹配 §X.X / §X.X.X / §X.X.X.X 格式）
# 也匹配如 "DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3" 等显式路径引用
SSOT_REF_PATTERN = re.compile(
    r"""
    §(?P<section>\d+(?:\.\d+)*)          # §4.3 格式（主要）
    """,
    re.VERBOSE | re.IGNORECASE,
)

# 排除的章节（常见非 SSOT 引用）
EXCLUDED_PATTERNS = [
    re.compile(r"^§1\b"),  # §1 泛指，无具体章节
    re.compile(r"^§9\b"),  # 同上
    re.compile(r"§[A-Z]"),  # §A, §B 等字母引用
]


def get_all_ssot_files() -> list[Path]:
    """动态收集所有 SSOT 文件"""
    files = list(SSOT_FILES)
    if SSOT_RULES_DIR.exists():
        files.extend(SSOT_RULES_DIR.glob("STAGE_S*.mdc"))
        files.extend(SSOT_RULES_DIR.glob("*.mdc"))
    if SSOT_SKILLS_DIR.exists():
        files.extend(SSOT_SKILLS_DIR.glob("*/SKILL.md"))
    return [f for f in files if f.exists()]


def load_ssot_content() -> dict[Path, str]:
    """加载所有 SSOT 文件内容（缓存）"""
    content: dict[Path, str] = {}
    for f in get_all_ssot_files():
        try:
            content[f] = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass
    return content


def extract_citations(text: str) -> list[dict]:
    """从文本中提取所有 SSOT 引用"""
    citations = []
    for m in SSOT_REF_PATTERN.finditer(text):
        raw = m.group(0).strip()
        section = m.group("section") or ""
        # 跳过排除模式
        skip = False
        for pat in EXCLUDED_PATTERNS:
            if pat.match(raw) or pat.match(section):
                skip = True
                break
        if skip:
            continue
        citations.append({
            "raw": raw,
            "section": section,
        })
    return citations


def validate_citation(citation: dict, ssot_content: dict[Path, str]) -> dict:
    """验证单个引用是否存在"""
    section = citation["section"]
    if not section:
        return {"status": "WARN", "message": f"无法解析引用字段: {citation['raw']}"}

    found = False
    for fpath, text in ssot_content.items():
        # 匹配 §X.X 或 §X.X.X
        pattern = re.compile(rf"§\s*{re.escape(section)}\b", re.IGNORECASE)
        if pattern.search(text):
            found = True
            break

    if found:
        return {"status": "OK", "message": f"§{section} 在 SSOT 中存在"}
    else:
        return {
            "status": "WARN",
            "message": f"§{section} 在 SSOT 文件中未找到（当前已知 {len(ssot_content)} 个 SSOT 文件）",
        }


def check_file(file_path: str, ssot_content: dict[Path, str]) -> list[dict]:
    """检查单个文件，返回警告列表"""
    path = Path(file_path)
    if path.suffix not in TARGET_EXTENSIONS and not path.name.endswith("SKILL.md"):
        return []

    if not path.exists():
        return []

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    warnings = []
    citations = extract_citations(text)
    for cite in citations:
        result = validate_citation(cite, ssot_content)
        if result["status"] != "OK":
            # 定位行号
            lines = text.splitlines()
            line_num = 1
            for i, line in enumerate(lines):
                if cite["raw"] in line:
                    line_num = i + 1
                    break
            try:
                relative = str(path.relative_to(WORKSPACE))
            except ValueError:
                relative = str(path)
            warnings.append({
                "file": relative,
                "line": line_num,
                "citation": cite["raw"],
                "section": cite["section"],
                "status": result["status"],
                "message": result["message"],
                "checked_at": datetime.now(timezone.utc).isoformat(),
            })
    return warnings


def log_warnings(warnings: list[dict]) -> None:
    """追加警告到 JSONL 日志"""
    if not warnings:
        return
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        for w in warnings:
            f.write(json.dumps(w, ensure_ascii=False) + "\n")


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return 0

    file_path = payload.get("file_path") or payload.get("path") or ""
    if not file_path:
        return 0

    ssot_content = load_ssot_content()
    warnings = check_file(file_path, ssot_content)

    if warnings:
        log_warnings(warnings)
        sys.stderr.write(
            f"[SSOT-CITATION] {len(warnings)} warn(s) for {file_path}: "
            f"{[w['message'] for w in warnings]}\n"
        )

    return 0


# ── self-test ────────────────────────────────────────────────────────────────
def self_test() -> int:
    """python3 .cursor/hooks/l1_ssot_citation_check.py --self-test"""
    import tempfile

    # 1. 提取测试
    test_text = """
    根据 DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3 配置常量执行。
    参照 STAGE_S5_TEST_POINTS.mdc §11 枚举定义。
    MODULES.md §2.1 定义了模块边界。
    请参考 §1 总则和 §9 决策标准。
    """
    cites = extract_citations(test_text)
    assert len(cites) >= 3, f"expected ≥3 citations, got {cites}"
    # §1 / §9 应被排除
    section_nums = [c["section"] for c in cites]
    assert "1" not in section_nums, f"§1 should be excluded: {cites}"
    assert "9" not in section_nums, f"§9 should be excluded: {cites}"
    print(f"  [OK] extract_citations: {cites}")

    # 2. 验证测试（使用真实 SSOT）
    ssot_content = load_ssot_content()
    assert len(ssot_content) > 0, "no SSOT files loaded"

    # §4.3 在 DESIGN_AND_EXECUTION_STANDARDS.mdc 中应存在
    result = validate_citation({"section": "4.3", "raw": "§4.3"}, ssot_content)
    assert result["status"] == "OK", f"§4.3 should exist: {result}"
    print(f"  [OK] validate_citation §4.3: {result}")

    # 随机不存在章节
    result = validate_citation({"section": "99.99", "raw": "§99.99"}, ssot_content)
    assert result["status"] == "WARN", f"§99.99 should warn: {result}"
    print(f"  [OK] validate_citation §99.99: {result}")

    # 3. 端到端测试（用临时文件）
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write("依据 §4.3 执行。\n引用 §99.99 无效章节。\n")
        temp_path = f.name

    warnings = check_file(temp_path, ssot_content)
    assert len(warnings) == 1, f"expected 1 warn, got {warnings}"
    assert warnings[0]["section"] == "99.99", f"wrong section: {warnings}"
    print(f"  [OK] check_file: {warnings}")

    Path(temp_path).unlink()

    # 4. 日志写入测试
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log_warnings(warnings)
    assert LOG_FILE.exists(), "log file not created"
    print(f"  [OK] log_warnings: wrote to {LOG_FILE}")

    print("  [OK] self-test passed")
    return 0


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
            sys.exit(self_test())
        sys.exit(main())
    except Exception as exc:
        sys.stderr.write(f"[SSOT-CITATION-ERROR] {type(exc).__name__}: {exc}\n")
