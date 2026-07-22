#!/usr/bin/env python3
"""v34 B1 防御 hook：阻止非授权 Agent 写入 knowledge/public/module_templates/ 正式库

触发：
  beforeFileEdit / beforeSubmitPrompt（Cursor hook 协议）
  stdin JSON:
    beforeFileEdit: {"event":"beforeFileEdit","tool_input":{"file_path":"..."}}
    beforeSubmitPrompt: {"event":"beforeSubmitPrompt","prompt":"...","target_file":"..."}

行为：
  - 命中 knowledge/public/module_templates/ 正式库路径（详见 _is_protected_module_template）
    → exit 2 + stderr 错误信息（Cursor 协议：exit 2 = block）
  - 环境变量 MODULE_TEMPLATE_EDIT_ALLOWED=1 → 绕过（仅 v34 B1 验收/紧急用）
  - 命中 _candidates/ 子路径 → 允许（候选区是 Agent 的合法落地）
  - 其他路径 → exit 0（允许）

设计约束：
  - 失败绝不让 IDE 崩溃（任何异常返回 exit 0）
  - 必须含 self_test() + --self-test argv 分支
  - 与 goal_loop_skill_md_protection.py / goal_loop_breakloop_hook.py 共享 REPO_ROOT + sys.path 约定
  - 路径前缀必须容错（绝对路径 / 相对路径 / 含项目根）

参考：
  - .cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc §0.1.3（主体权限对照表）
  - .cursor/skills/_module-experts/README.md（8 模块专家 + 权限对照）
  - .cursor/skills/<module>-expert/SKILL.md（每个专家自述的边界）
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# 受保护路径前缀：knowledge/public/module_templates/ 下所有非候选 / 非公共豁免文件
PROTECTED_PREFIX = "knowledge/public/module_templates/"
# 允许落地的子路径（在 PROTECTED_PREFIX 内）：候选区
ALLOWED_SUBPATHS = ("_candidates",)
# 公共文件豁免语义（这些文件即使不在候选区，也**任何 Agent 都不得直写**）
# 实现上：把它们留在 PROTECTED_PREFIX 内（命中即拒绝），下面这段仅用于错误提示
NEVER_WRITE_PUBLIC_FILES = (
    "_common_structure.md",
    "_decision_tree.md",
    "s2_output_template.md",
)
BYPASS_ENV = "MODULE_TEMPLATE_EDIT_ALLOWED"

# 8 个合法模块 ID（与 .cursor/MODULES.md §1 总表 1:1 对齐）
LEGAL_MODULES = ("CONFIG", "UI", "BIZ", "AUX", "LINK", "SPECIAL", "LOG", "HINT")


def _normalize_path(target_path: str) -> PurePosixPath:
    """归一化路径为 PurePosixPath，兼容绝对/相对/Windows 反斜杠。"""
    return PurePosixPath(target_path.replace("\\", "/"))


def _extract_module_from_path(target_path: str) -> str:
    """从 knowledge/public/module_templates/<X>/... 抽出 X（可能是模块或公共前缀 _xxx）。

    Returns:
        "<MODULE>" | "_<common>" | "<MODULE>.md"（顶层模块概览） | ""（不在 templates 下）
    """
    p = _normalize_path(target_path)
    parts = p.parts
    try:
        idx = parts.index("module_templates")
    except ValueError:
        return ""
    # 紧跟 module_templates 的下一段
    if len(parts) <= idx + 1:
        return ""
    return parts[idx + 1]


def _is_protected_module_template(target_path: str) -> tuple[bool, str]:
    """判定目标路径是否命中受保护的 module_templates 正式库。

    Returns:
        (is_protected, reason) — True 表示必须拒绝
    """
    if not target_path:
        return False, "empty path"

    p = _normalize_path(target_path)
    parts = p.parts

    # 必须命中 knowledge/public/module_templates/ 前缀
    try:
        idx = parts.index("module_templates")
    except ValueError:
        return False, "not under module_templates/"
    # 前面必须含 knowledge/public
    if idx < 2 or parts[idx - 1] != "public" or parts[idx - 2] != "knowledge":
        return False, "not under knowledge/public/module_templates/"

    # 紧跟 module_templates 的下一段（模块 ID 或公共前缀）
    if len(parts) <= idx + 1:
        return False, "module_templates/ 后无内容"

    next_part = parts[idx + 1]

    # 模块概览文件路径：knowledge/public/module_templates/<MODULE>.md
    # PurePosixPath 不太好直接判断，这里转 str
    p_str = str(p)
    overview_match = False
    for mod in LEGAL_MODULES:
        if p_str == f"knowledge/public/module_templates/{mod}.md":
            overview_match = True
            break

    # 公共豁免文件检查（任何 Agent 都不得直写）
    for public_file in NEVER_WRITE_PUBLIC_FILES:
        if p_str == f"knowledge/public/module_templates/{public_file}":
            return True, (
                f"Blocked: {target_path} 命中公共豁免文件 {public_file}。"
                f"任何 Agent（含 8 个模块专家）都不得直接写入公共文件，"
                f"必须走候选区 _candidates/ + 人工审核。"
            )

    if overview_match:
        return True, (
            f"Blocked: {target_path} 是模块概览正式库。"
            f"仅对应模块的 `<MODULE>-expert` skill 可写（commit 标注 [<MODULE>-专家直写]），"
            f"其他 Agent（含通用 Agent / 其它模块专家）必须走候选区 _candidates/。"
        )

    # 命中某模块子目录
    if next_part in LEGAL_MODULES:
        # 子目录内的所有路径
        # 排除 _candidates/
        if len(parts) > idx + 2 and parts[idx + 2] in ALLOWED_SUBPATHS:
            # 在 _candidates/ 内 → 允许
            return False, f"under {next_part}/_candidates/ → allowed"

        # 其它都是受保护的正式库
        return True, (
            f"Blocked: {target_path} 命中 {next_part}/ 正式库。"
            f"仅 `{next_part.lower()}-expert` skill 可写（commit 标注 [{next_part}-专家直写]），"
            f"其他 Agent 必须走候选区 _candidates/。"
        )

    # 其它前缀（_xxx 公共文件已被前面 NEVER_WRITE_PUBLIC_FILES 拦截，这里兜底）
    if next_part.startswith("_"):
        return True, (
            f"Blocked: {target_path} 命中公共前缀 {next_part}/。"
            f"任何 Agent 都不得直接写入公共文件，"
            f"必须走候选区 _candidates/ + 人工审核。"
        )

    # 未知前缀（理论上不应出现，因为 LEGAL_MODULES 已覆盖全部 8 模块）
    return True, (
        f"Blocked: {target_path} 不在 8 个合法模块（{LEGAL_MODULES}）内。"
        f"如新增模块，请同步 .cursor/MODULES.md §1 + .cursor/skills/_module-experts/README.md + 本 hook LEGAL_MODULES。"
    )


def check(target_path: str) -> tuple[bool, str]:
    """检查目标路径是否允许写入。

    Returns:
        (allowed, reason) — allowed=True 允许；allowed=False + reason 解释
    """
    if not target_path:
        return True, "no target path provided"

    if os.environ.get(BYPASS_ENV) == "1":
        return True, f"bypassed by {BYPASS_ENV}=1"

    is_protected, reason = _is_protected_module_template(target_path)
    if is_protected:
        return False, f"{reason}\n若需紧急编辑请设置环境变量 {BYPASS_ENV}=1。"

    return True, "not a protected module_templates path"


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
    """python3 .cursor/hooks/module_template_protection.py --self-test

    验证 ≥ 12 项：覆盖 8 模块正式库 / 8 模块概览 / 候选区 / 公共豁免 / 边界外 / bypass env。
    """
    cases = [
        # === 8 模块正式库：必须拒绝（通用 Agent 视角）===
        ("knowledge/public/module_templates/CONFIG/A_field_legality.md", False, "CONFIG 正式库"),
        ("knowledge/public/module_templates/UI/A_control_basic.md", False, "UI 正式库"),
        ("knowledge/public/module_templates/BIZ/A_biz_logic.md", False, "BIZ 正式库"),
        ("knowledge/public/module_templates/AUX/A_common_util.md", False, "AUX 正式库"),
        ("knowledge/public/module_templates/LINK/A_internal_biz_linkage.md", False, "LINK 正式库"),
        ("knowledge/public/module_templates/SPECIAL/A_boundary_extreme.md", False, "SPECIAL 正式库"),
        ("knowledge/public/module_templates/LOG/A_event_track.md", False, "LOG 正式库"),
        ("knowledge/public/module_templates/HINT/A_red_dot_badge.md", False, "HINT 正式库"),
        # === 8 模块概览（顶层 <MODULE>.md）：必须拒绝 ===
        ("knowledge/public/module_templates/CONFIG.md", False, "CONFIG 模块概览"),
        ("knowledge/public/module_templates/UI.md", False, "UI 模块概览"),
        ("knowledge/public/module_templates/HINT.md", False, "HINT 模块概览"),
        # === 3 个公共豁免文件：必须拒绝（任何 Agent）===
        ("knowledge/public/module_templates/_common_structure.md", False, "_common_structure.md 公共文件"),
        ("knowledge/public/module_templates/_decision_tree.md", False, "_decision_tree.md 公共文件"),
        ("knowledge/public/module_templates/s2_output_template.md", False, "s2_output_template.md 公共文件"),
        # === 候选区：必须允许 ===
        ("knowledge/public/module_templates/CONFIG/_candidates/20260722_new_subclass.md", True, "CONFIG 候选区"),
        ("knowledge/public/module_templates/UI/_candidates/x.md", True, "UI 候选区"),
        ("knowledge/public/module_templates/HINT/_candidates/foo/bar.md", True, "HINT 候选区子目录"),
        # === 边界外路径：必须允许 ===
        (".cursor/skills/config-expert/SKILL.md", True, "skill 目录（不是 module_templates）"),
        (".cursor/MODULES.md", True, "MODULES.md"),
        (".cursor/rules/xxx.mdc", True, "rules 目录"),
        ("knowledge/public/test_point_library/foo.json", True, "test_point_library（其他公共库）"),
        ("workflow_assets/foo/v1.0/「S5」/test_points.json", True, "过程资产目录"),
        # === 空 / 异常输入 ===
        ("", True, "empty path"),
        # === 未知前缀（防御性）===
        ("knowledge/public/module_templates/UNKNOWN/foo.md", False, "未知模块前缀"),
        # === 绝对路径 ===
        ("/Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/public/module_templates/BIZ/O_boundary.md", False, "绝对路径 BIZ 正式库"),
    ]

    failed = 0
    for path, expected_allowed, desc in cases:
        allowed, reason = check(path)
        if allowed != expected_allowed:
            failed += 1
            print(f"  [❌ FAIL] Case '{desc}': expected allowed={expected_allowed}, got allowed={allowed} (reason={reason!r})")
        else:
            print(f"  [OK] Case '{desc}': allowed={allowed}")

    # bypass env 测试
    os.environ[BYPASS_ENV] = "1"
    try:
        allowed, reason = check("knowledge/public/module_templates/BIZ/A_biz_logic.md")
        if not allowed:
            failed += 1
            print(f"  [❌ FAIL] bypass env: 应 allowed, got blocked (reason={reason!r})")
        else:
            print(f"  [OK] Case 'bypass env': {BYPASS_ENV}=1 → allowed")
    finally:
        os.environ.pop(BYPASS_ENV, None)

    # 移除 env 后再次拒绝
    allowed, reason = check("knowledge/public/module_templates/BIZ/A_biz_logic.md")
    if allowed:
        failed += 1
        print(f"  [❌ FAIL] 移除 bypass env 后应再次拒绝，但 got allowed")
    else:
        print(f"  [OK] Case 'remove bypass env': 再次拒绝")

    if failed:
        print(f"\n  [❌] self_test FAILED: {failed} case(s) failed")
        return 1
    print(f"\n  [OK] self_test passed ({len(cases) + 2} cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())