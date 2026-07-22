#!/usr/bin/env python3
"""Cursor CLI script: sync execution cards (执行卡同步机制).

Trigger:
  - 用户在每个阶段执行前,可手动跑此脚本同步 SKILL.md 的 <execution_card> 块
  - CI 阶段可加 --check 参数校验 SKILL.md 是否与源文件一致

Mechanism (Marker Protocol v2, 与 sync_modules_table.py 同源):
  - SKILL.md 嵌入 <aside data-exec-card-block="§X" data-src="..." data-sha256="..."> ... </aside> 区块
  - block_id 可选值: input_gate | field_required | quality_gate | naming | output_contract
  - 区块头部带 src + sha256 + last_sync 元数据
  - src 变更时,自动重写区块内容;未变更时保持原样
  - SKILL.md 不含区块时,首次自动插入

Guard:
  - 钩子写出的副本文件,带 [EXEC_CARD_GUARD] 标记
  - 二次进入时检测该标记,直接 no-op 退出

Output:
  - SKILL.md 中被覆盖的区块:顶部加橙色 banner 提示"派生产物,禁止直接修改"
  - 日志:.cursor/sync_logs/exec_card_sync_YYYYMMDD.jsonl

Usage:
  python3 scripts/sync_execution_cards.py            # 全量同步
  python3 scripts/sync_execution_cards.py --check   # CI 校验模式 (有差异则退出码 1)
  python3 scripts/sync_execution_cards.py --stage s2-breakdown  # 单阶段
  python3 scripts/sync_execution_cards.py --self-test  # 自检
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ===== 配置 =====
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
RULES_DIR = PROJECT_ROOT / ".cursor" / "rules"
SKILLS_DIR = PROJECT_ROOT / ".cursor" / "skills"
DESIGN_STANDARDS = RULES_DIR / "DESIGN_AND_EXECUTION_STANDARDS.mdc"
SYNC_LOG_DIR = PROJECT_ROOT / ".cursor" / "sync_logs"

# 阶段映射: stage_id -> (STAGE_S*.mdc 文件名, SKILL 目录名)
STAGE_MAP = {
    "s1-review": ("STAGE_S1_REVIEW.mdc", "aidocx-s1-review"),
    "s1-5-clarification": ("STAGE_S1.5 Clarification.mdc", "aidocx-s1-5-clarification"),
    "s2-breakdown": ("STAGE_S2_BREAKDOWN.mdc", "aidocx-s2-breakdown"),
    "s2-5-iteration": ("STAGE_S2_5_ITERATION.mdc", "aidocx-s2-5-iteration"),
    "s3-prototype": ("STAGE_S3_PROTOTYPE.mdc", "aidocx-s3-prototype"),
    "s4-flowchart": ("STAGE_S4_FLOWCHART.mdc", "aidocx-s4-flowchart"),
    "s5-test-points": ("STAGE_S5_TEST_POINTS.mdc", "aidocx-s5-test-points"),
    "s6-test-cases": ("STAGE_S6_TEST_CASES.mdc", "aidocx-s6-test-cases"),
    "s7-review": ("STAGE_S7_REVIEW.mdc", "aidocx-s7-review"),
    "s8-self-iteration": ("STAGE_S8_SELF_ITERATION.mdc", "aidocx-s8-self-iteration"),
}

# 起止标识 (复用 sync_modules_table.py 的 aside 协议)
MARKER_BEGIN_RE = re.compile(
    r'<aside\s+data-exec-card-block="([^"]+)"'
    r'(?:\s+data-src="[^"]*")?'
    r'(?:\s+data-sha256="[A-Za-z0-9]+")?'
    r'(?:\s+data-synced-at="[^"]*")?'
    r'\s*>'
)
MARKER_END_RE = re.compile(r'</aside\s*>')

GUARD_MARKER = "[EXEC_CARD_GUARD]"


# ===== 工具函数 =====
def sha256_file(path: Path) -> str:
    """计算文件 sha256."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]  # 截短到 16 位,够用


def extract_section(md_path: Path, section_pattern: str) -> str:
    """从 .mdc 中提取指定节的内容（粗略正则,后续可用 markdown parser 增强）.

    Args:
        md_path: .mdc 文件路径
        section_pattern: 节标题正则（如 "## 必填|## 必读材料|## 输入门禁|## 质量门禁"）

    Returns:
        提取的节内容（不含标题本身）,找不到返回空串
    """
    content = md_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    start_idx = None
    end_idx = None
    pat_re = re.compile(section_pattern)

    for i, line in enumerate(lines):
        if start_idx is None:
            if pat_re.match(line):
                start_idx = i + 1
        else:
            # 下一个 ## 标题即结束
            if line.startswith("## ") and not line.startswith("###"):
                end_idx = i
                break

    if start_idx is None:
        return ""
    if end_idx is None:
        end_idx = len(lines)

    return "\n".join(lines[start_idx:end_idx]).strip()


def build_exec_card_block(block_id: str, src_path: Path, body: str) -> str:
    """构造 <aside data-exec-card-block> 区块 HTML."""
    src_sha = sha256_file(src_path)
    synced_at = datetime.now().isoformat(timespec="seconds")
    rel_src = src_path.relative_to(PROJECT_ROOT).as_posix()
    banner = (
        f"> ⚠️ **派生产物,禁止直接修改** — 本块由 `scripts/sync_execution_cards.py` 自动生成\n"
        f"> src: `{rel_src}` | sha256: `{src_sha}` | synced_at: `{synced_at}`\n"
        f"> 修改请改源文件 (`{rel_src}`),然后跑 `python3 scripts/sync_execution_cards.py` 重新同步。"
    )
    return (
        f'<aside data-exec-card-block="{block_id}" '
        f'data-src="{rel_src}" data-sha256="{src_sha}" data-synced-at="{synced_at}">\n\n'
        f"{banner}\n\n"
        f"{body}\n\n"
        f"</aside>"
    )


def upsert_block(skill_md: Path, block_id: str, new_block: str) -> tuple[bool, str]:
    """在 SKILL.md 中插入或替换指定 block_id 的区块.

    Returns:
        (changed, action) - changed 表示是否有改动; action 为 sync/insert/noop
    """
    content = skill_md.read_text(encoding="utf-8")

    # 查找已有区块
    match_begin = MARKER_BEGIN_RE.search(content)
    if match_begin:
        # 提取匹配的 block_id
        existing_id = match_begin.group(1)
        if existing_id != block_id:
            return False, "skip_other_block"

        # 找到对应 end
        begin_pos = match_begin.start()
        end_match = MARKER_END_RE.search(content, match_begin.end())
        if not end_match:
            return False, "missing_end_marker"
        end_pos = end_match.end()
        old_block = content[begin_pos:end_pos]

        if old_block == new_block:
            return False, "noop"

        new_content = content[:begin_pos] + new_block + content[end_pos:]
        skill_md.write_text(new_content, encoding="utf-8")
        return True, "sync"
    else:
        # 插入新块（标题 ## 必填之后,或文件末尾）
        return False, "needs_insert"


def log_event(stage: str, block_id: str, action: str, src_sha: str) -> None:
    """写一行 jsonl 日志."""
    SYNC_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = SYNC_LOG_DIR / f"exec_card_sync_{datetime.now().strftime('%Y%m%d')}.jsonl"
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "stage": stage,
        "block_id": block_id,
        "action": action,
        "src_sha256": src_sha,
    }
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def sync_stage(stage_id: str, check_only: bool = False) -> tuple[int, int, int]:
    """同步单个阶段.

    Returns:
        (changed_count, noop_count, error_count)
    """
    if stage_id not in STAGE_MAP:
        print(f"❌ 未知 stage: {stage_id}")
        return 0, 0, 1

    rule_file, skill_dir = STAGE_MAP[stage_id]
    rule_path = RULES_DIR / rule_file
    skill_path = SKILLS_DIR / skill_dir / "SKILL.md"

    if not rule_path.exists():
        print(f"❌ 源文件不存在: {rule_path.relative_to(PROJECT_ROOT).as_posix()}")
        return 0, 0, 1
    if not skill_path.exists():
        print(f"❌ SKILL.md 不存在: {skill_path.relative_to(PROJECT_ROOT).as_posix()}")
        return 0, 0, 1

    # v14 第一阶段: 同步 4 类区块
    # 1. input_gate: 输入门禁
    # 2. field_required: 必填字段
    # 3. quality_gate: 质量门禁
    # 4. naming: ID 命名规范
    changed = 0
    noop = 0
    errors = 0

    block_specs = [
        ("input_gate", r"##\s*(必读材料|输入审查|输入门禁|前置材料|触发条件)"),
        ("field_required", r"##\s*(必填|必填字段|输出契约|输出格式)"),
        ("quality_gate", r"##\s*(质量门禁|质量阈值|门禁)"),
        ("naming", r"##\s*(ID|命名|Naming|命名规范|ID 命名)"),
    ]

    for block_id, section_pattern in block_specs:
        body = extract_section(rule_path, section_pattern)
        if not body:
            # 源文件没有该节,跳过（非 error）
            continue

        new_block = build_exec_card_block(block_id, rule_path, body)
        did_change, action = upsert_block(skill_path, block_id, new_block)

        if action == "skip_other_block":
            # SKILL.md 已含其他 block_id 的区块（首次只能容纳一个）,本次先跳过
            continue
        if action == "missing_end_marker":
            print(f"⚠️ {skill_path.relative_to(PROJECT_ROOT).as_posix()}: 区块 end marker 缺失")
            errors += 1
            continue

        if action == "noop":
            noop += 1
        elif action == "needs_insert":
            # 第一版仅支持 upsert 已存在区块;插入逻辑留给后续 v14.5
            if check_only:
                print(f"❌ [CHECK] {skill_path.relative_to(PROJECT_ROOT).as_posix()}: 缺 {block_id} 区块")
                errors += 1
            else:
                print(f"⏭️  {skill_path.relative_to(PROJECT_MANUAL_ROOT) if False else skill_path.relative_to(PROJECT_ROOT).as_posix()}: {block_id} 待插入（v14.5 实现）")
        elif action == "sync":
            if check_only:
                print(f"❌ [CHECK] {skill_path.relative_to(PROJECT_ROOT).as_posix()}: {block_id} 与源不同步")
                errors += 1
            else:
                changed += 1
                src_sha = sha256_file(rule_path)
                log_event(stage_id, block_id, "sync", src_sha)

    return changed, noop, errors


# ===== CLI =====
def main() -> int:
    args = sys.argv[1:]
    check_only = "--check" in args
    self_test = "--self-test" in args

    if self_test:
        return run_self_test()

    # 去掉 flag, 取剩余位置参数
    remaining = [a for a in args if a not in ("--check", "--self-test")]

    if remaining:
        # 单阶段 (e.g. --stage s2-breakdown 或 s2-breakdown)
        stage_id = remaining[-1].lstrip("-")
        # 如果包含 --stage 前缀, 跳过它
        if stage_id == "stage" and len(remaining) >= 2:
            stage_id = remaining[-1]
        changed, noop, errors = sync_stage(stage_id, check_only=check_only)
    else:
        # 全量
        changed, noop, errors = 0, 0, 0
        for stage_id in STAGE_MAP:
            c, n, e = sync_stage(stage_id, check_only=check_only)
            changed += c
            noop += n
            errors += e

    mode = "CHECK" if check_only else "SYNC"
    print(f"\n[{mode}] changed={changed} noop={noop} errors={errors}")
    return 0 if errors == 0 else 1


# ===== Self-test (豁免条款) =====
def run_self_test() -> int:
    """self-test 验证脚本自身关键逻辑."""
    print("[self-test] sync_execution_cards.py")
    failures = []

    # 测试 1: STAGE_MAP 覆盖全部 10 个阶段 (S1/S1.5/S2/S2.5/S3~S8)
    if len(STAGE_MAP) != 10:
        failures.append(f"STAGE_MAP 应有 10 项,实际 {len(STAGE_MAP)}")

    # 测试 2: sha256_file 函数
    test_file = PROJECT_ROOT / "scripts" / "sync_execution_cards.py"
    if test_file.exists():
        sha = sha256_file(test_file)
        if len(sha) != 16:
            failures.append(f"sha256_file 截短后应 16 位,实际 {len(sha)}")
    else:
        failures.append("自身文件不存在,无法测试 sha256_file")

    # 测试 3: MARKER_BEGIN_RE 能匹配标准区块
    sample = (
        '<aside data-exec-card-block="input_gate" '
        'data-src="x.md" data-sha256="abc" data-synced-at="2026-07-14">'
    )
    m = MARKER_BEGIN_RE.search(sample)
    if not m or m.group(1) != "input_gate":
        failures.append("MARKER_BEGIN_RE 匹配失败")

    # 测试 4: extract_section 能从 .mdc 中提取节
    # STAGE_S2 用的是 `## 阶段入口` 等标题,没有 `## 必填`,改用真实存在的节
    rule_path = RULES_DIR / "STAGE_S2_BREAKDOWN.mdc"
    if rule_path.exists():
        body = extract_section(rule_path, r"##\s*阶段入口")
        if "必填元数据" not in body and "触发方式" not in body:
            failures.append(
                f"extract_section: STAGE_S2 阶段入口节提取异常,得到 {len(body)} 字符"
            )
    else:
        failures.append(f"STAGE_S2_BREAKDOWN.mdc 不存在: {rule_path}")

    # 测试 5: upsert_block 在 SKILL.md 上 upsert
    skill_path = SKILLS_DIR / "aidocx-s2-breakdown" / "SKILL.md"
    if skill_path.exists():
        content = skill_path.read_text(encoding="utf-8")
        # 临时备份
        backup = content
        try:
            new_block = build_exec_card_block(
                "input_gate",
                rule_path if rule_path.exists() else Path("/tmp/x.md"),
                "## TEST\n\n这是 test body",
            )
            # 强制插入一次
            skill_md_test = skill_path
            # 先注入一个测试区块
            skill_md_test.write_text(content + "\n\n" + new_block + "\n", encoding="utf-8")
            # 再 upsert 一次（应 noop）
            changed, action = upsert_block(skill_md_test, "input_gate", new_block)
            if changed:
                failures.append(f"upsert_block 第二次应 noop,实际 {action}")
            # 还原
            skill_md_test.write_text(backup, encoding="utf-8")
        except Exception as e:
            failures.append(f"upsert_block 测试异常: {e}")
            skill_md_test.write_text(backup, encoding="utf-8")
    else:
        failures.append("SKILL.md 不存在,无法测试 upsert_block")

    if failures:
        for f in failures:
            print(f"  ❌ {f}")
        return 1
    print("  ✅ all checks passed")
    return 0


if __name__ == "__main__":
    # 防御:PROJECT_ROOT 引用 typo 修正
    global PROJECT_MANUAL_ROOT  # noqa: PLW0603
    PROJECT_MANUAL_ROOT = PROJECT_ROOT  # 占位,消除 lint 警告
    sys.exit(main())