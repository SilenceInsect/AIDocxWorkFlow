#!/usr/bin/env python3
"""Cursor afterFileEdit hook: 同步 INDEX.json#current 与 plans/ 目录（防脱钩）。

Trigger:
  - 任何 governance/design_iter/** 文件改动（不光是 INDEX.md / INDEX.json）
  - 重点保护:
    1. INDEX.json#current 与 current 软链不一致 → 以软链为准修 json
    2. INDEX.json#plans[] 与 plans/ 实际目录不一致 → 增删
    3. INDEX.json#updated_at 过期 → 更新为今天
    4. INDEX.md §1 当前生效表格中 current 单元格与软链不一致 → 替换

不维护:
  - INDEX.md §2 进度看板 / §3 交接承诺 / §4 触发与维护（人写）

Mechanism:
  - 幂等: 同状态多次触发 = 同样结果
  - 不写 IDENTITY_HINT: 这次重写不破坏前一次
  - 钩子写文件带 [INDEX_SYNC_GUARD] marker: 二次进入直接 no-op

Output:
  - 同步后: stdout 一行 JSON {"status": "synced" | "noop", "changes": [...]}
  - 日志: .cursor/sync_logs/index_sync_YYYYMMDD.jsonl
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ===== 配置 =====
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DESIGN_ITER = PROJECT_ROOT / "governance" / "design_iter"
INDEX_JSON = DESIGN_ITER / "INDEX.json"
INDEX_MD = DESIGN_ITER / "INDEX.md"
PLANS_DIR = DESIGN_ITER / "plans"
CURRENT_LINK = DESIGN_ITER / "current"
SYNC_LOG_DIR = PROJECT_ROOT / ".cursor" / "sync_logs"

GUARD_MARKER = "<!-- INDEX_SYNC_GUARD -->"


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _current_target() -> str | None:
    """读 current 软链的真实指向（文件系统的真相源）。"""
    if not CURRENT_LINK.exists() and not CURRENT_LINK.is_symlink():
        return None
    try:
        target = CURRENT_LINK.resolve()
        if target.is_relative_to(PLANS_DIR):
            return target.relative_to(PLANS_DIR).name
    except Exception:  # noqa: BLE001
        pass
    return None


def _scan_plans() -> list[str]:
    """扫 plans/ 实际存在的目录名。"""
    if not PLANS_DIR.exists():
        return []
    return sorted(p.name for p in PLANS_DIR.iterdir() if p.is_dir())


def _log_sync(changes: list[str]) -> None:
    SYNC_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = SYNC_LOG_DIR / f"index_sync_{datetime.now().strftime('%Y%m%d')}.jsonl"
    log_file.write_text(
        json.dumps(
            {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "changes": changes,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _sync_index_json() -> list[str]:
    """同步 INDEX.json —— 返回变更列表（空 = noop）。"""
    changes: list[str] = []
    actual_current = _current_target()
    actual_plans = _scan_plans()

    data = _read_json(INDEX_JSON)
    if not data:
        data = {"schema_version": "1.0", "plans": []}
        changes.append("recreate_empty_json")

    # 1. current 与软链对齐（软链是真相源）
    if actual_current and data.get("current") != actual_current:
        changes.append(f"current:{data.get('current')}→{actual_current}")
        data["current"] = actual_current

    # 2. plans 列表与 plans/ 目录对齐
    declared = {p.get("version") for p in data.get("plans", []) if isinstance(p, dict)}
    declared.discard(None)
    missing = set(actual_plans) - declared
    extra = declared - set(actual_plans)
    if missing:
        # 补缺失项（最小化：只补 version + path）
        for m in sorted(missing):
            data.setdefault("plans", []).append(
                {
                    "version": m,
                    "title": "(待补全)",
                    "status": "(待补全)",
                    "path": f"governance/design_iter/plans/{m}/",
                }
            )
            changes.append(f"plan_add:{m}")
    if extra:
        # 移除不存在项
        data["plans"] = [p for p in data["plans"] if p.get("version") not in extra]
        changes.append(f"plan_remove:{','.join(sorted(extra))}")

    # 3. updated_at
    today = datetime.now().strftime("%Y-%m-%d")
    if data.get("updated_at") != today:
        changes.append(f"updated_at:{data.get('updated_at')}→{today}")
        data["updated_at"] = today

    if changes:
        _write_json(INDEX_JSON, data)
    return changes


def _sync_index_md_current_cell() -> list[str]:
    """同步 INDEX.md §1 当前生效表格中 current 单元格。

    表格行结构（精确匹配）:
        | [`v{XX}`](plans/v{XX}/) | **current** | ...
    """
    if not INDEX_MD.exists():
        return []
    text = INDEX_MD.read_text(encoding="utf-8")
    if GUARD_MARKER in text:
        return []
    actual_current = _current_target()
    if not actual_current:
        return []
    # 匹配当前 §1 表格中的 current 行第一个 v{N}
    pattern = re.compile(
        r"(\|\s*\[`v\d+`\]\(plans/v\d+/\)\s*\|\s*\*\*current\*\*\s*\|)",
    )
    m = pattern.search(text)
    if not m:
        return []
    # 提取旧版本
    old_match = re.search(r"v(\d+)", m.group(1))
    if not old_match:
        return []
    old_ver = f"v{old_match.group(1)}"
    if old_ver == actual_current:
        return []
    new_cell = m.group(1).replace(f"[`{old_ver}`]", f"[`{actual_current}`]")
    new_text = text.replace(m.group(1), f"{new_cell}{GUARD_MARKER}", 1)
    INDEX_MD.write_text(new_text, encoding="utf-8")
    return [f"index_md_current:{old_ver}→{actual_current}"]


def _cleanup_guard_marker() -> None:
    """清掉 INDEX.md 里的 guard marker（下一次触发能再写）。"""
    if not INDEX_MD.exists():
        return
    text = INDEX_MD.read_text(encoding="utf-8")
    if GUARD_MARKER in text:
        INDEX_MD.write_text(text.replace(GUARD_MARKER, ""), encoding="utf-8")


def main() -> int:
    try:
        changes: list[str] = []
        changes.extend(_sync_index_json())
        # §1 改之前清掉上次的 marker（否则幂等失败）
        _cleanup_guard_marker()
        changes.extend(_sync_index_md_current_cell())
        if changes:
            _log_sync(changes)
            print(json.dumps({"status": "synced", "changes": changes}, ensure_ascii=False))
        else:
            print(json.dumps({"status": "noop"}, ensure_ascii=False))
        return 0
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1


# ---------- self-test ----------

def self_test() -> int:
    """hook 自测：dry-run + 验证 §1 同步。

    用法: python3 index_landing_hook.py --self-test
    行为: 备份 → 改 INDEX.json 模拟 current 漂移 → 跑 sync → 验证恢复。

    设计说明：
    - hook 的 source of truth = symlink (`current/`)
    - self-test 注入漂移值（v999），期望 hook 恢复为 symlink 指向（v17）
    - 不依赖 INDEX.json 的原始值（因为 INDEX.json 本身可能已漂移）
    """
    import subprocess
    import tempfile

    if not INDEX_JSON.exists() or not INDEX_MD.exists():
        print("[self-test FAIL] INDEX.json 或 INDEX.md 不存在")
        return 1
    # 备份
    bak_json = INDEX_JSON.with_suffix(".json.bak")
    bak_md = INDEX_MD.with_suffix(".md.bak")
    bak_json.write_text(INDEX_JSON.read_text(encoding="utf-8"), encoding="utf-8")
    bak_md.write_text(INDEX_MD.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        # 获取 symlink 的真实指向（source of truth）
        symlink_target = _current_target()
        if not symlink_target:
            print("[self-test FAIL] current 软链不存在或无法解析")
            return 1

        # 故意把 INDEX.json#current 写错 → 跑 hook → 期望恢复到 symlink 指向
        data = _read_json(INDEX_JSON)
        wrong_current = "v999"  # 不存在的版本
        data["current"] = wrong_current
        _write_json(INDEX_JSON, data)
        # 跑 main
        rc = main()
        # 验证: current 已自动修回 symlink 指向（hook 的 source of truth）
        after = _read_json(INDEX_JSON)
        if after.get("current") != symlink_target:
            print(f"[self-test FAIL] current 未恢复到 symlink 指向: 期望 {symlink_target}, 实际 {after.get('current')}")
            return 1
        if rc != 0:
            print(f"[self-test FAIL] main() 返回 {rc}")
            return 1
        # 幂等: 再跑一次应 noop
        out = subprocess.run(
            ["python3", __file__], capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        result = json.loads(out.stdout) if out.stdout else {}
        if result.get("status") != "noop":
            print(f"[self-test FAIL] 第二次跑不幂等: {result}")
            return 1
        print(f"[self-test OK] current={symlink_target}, 幂等={result.get('status')}")
        return 0
    finally:
        # 恢复
        INDEX_JSON.write_text(bak_json.read_text(encoding="utf-8"), encoding="utf-8")
        INDEX_MD.write_text(bak_md.read_text(encoding="utf-8"), encoding="utf-8")
        bak_json.unlink(missing_ok=True)
        bak_md.unlink(missing_ok=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())