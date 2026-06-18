#!/usr/bin/env python3
"""AIDocxWorkFlow 方案迭代 CLI（6 子命令）

子命令：
  - new <version> <title>     从 current 复制 → plans/{version}/ + 强制填 3 栏
  - list                       列出所有方案 + 状态 + 未解决问题数
  - diff <v1> <v2>             生成 changes/diff_v1_to_v2.md
  - rollback <version>         整份替换 current → plans/{version}/
  - resolve <version> <Q-XXX>  把 open_questions 的 Q-XXX 移到 resolved_questions
  - status                     输出 current + 未解决问题 + 已解决问题

设计原则：
  - 不生成事实（不扫代码）——只操作"已经写过的方案"
  - 覆盖前自动备份到 archive/
  - current 用软链——回滚 = 改软链
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# SIGPIPE 防御（head/tail 截断时）
try:
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

# scripts 在 design_iter/scripts/ 下 → parents[3] = 项目根
_ROOT = Path(__file__).resolve().parents[3]
DESIGN_ITER = _ROOT / ".cursor" / "design_iter"
PLANS_DIR = DESIGN_ITER / "plans"
ARCHIVE_DIR = DESIGN_ITER / "archive"
CURRENT_LINK = DESIGN_ITER / "current"
INDEX_JSON = DESIGN_ITER / "INDEX.json"


# ---------- 辅助函数 ----------

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _plan_dir(version: str) -> Path:
    return PLANS_DIR / version


def _current_target() -> Path | None:
    if not CURRENT_LINK.exists() and not CURRENT_LINK.is_symlink():
        return None
    try:
        target = CURRENT_LINK.resolve()
        return target
    except Exception:  # noqa: BLE001
        return None


def _count_open_questions(version: str) -> int:
    """统计 open_questions.md 中形如 **Q-XXX**: 的未决问题数。

    文件格式允许标记候选答案（`- [ A ] **Q-001**: ...`），
    因此不能用 `- [ ]` 计数；按 Q-XXX 标题数计。
    """
    import re
    oq_file = _plan_dir(version) / "open_questions.md"
    if not oq_file.exists():
        return 0
    text = oq_file.read_text(encoding="utf-8")
    return len(re.findall(r"\*\*Q-\d+\*\*:", text))


def _count_resolved(version: str) -> int:
    """统计 resolved_questions.md 中已闭环问题数。

    同时支持两种格式：`- [x]` 复选框 / `- ✅` 决议条目。
    """
    rq_file = _plan_dir(version) / "resolved_questions.md"
    if not rq_file.exists():
        return 0
    n = 0
    for line in rq_file.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("- [x]") or s.startswith("- ✅") or s.startswith("- [X]"):
            n += 1
    return n


# ---------- 子命令 ----------

def cmd_status(_args: argparse.Namespace) -> int:
    target = _current_target()
    print("=" * 60)
    print("[design_iter status]")
    print("=" * 60)
    if target is None:
        print("current 软链: (未设置)")
    else:
        rel = target.relative_to(_ROOT) if target.is_relative_to(_ROOT) else target
        print(f"current 软链: → {rel}")
    print()
    print("所有方案:")
    if not PLANS_DIR.exists():
        print("  (plans 目录不存在)")
        return 0
    for plan in sorted(PLANS_DIR.iterdir()):
        if not plan.is_dir():
            continue
        oq = _count_open_questions(plan.name)
        rq = _count_resolved(plan.name)
        dec = _read_json(plan / "decisions.json")
        status = dec.get("status", "未知")
        title = dec.get("title", "(无标题)")
        print(f"  - {plan.name}: {title} [{status}] open={oq} resolved={rq}")
    print("=" * 60)
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    return cmd_status(_args)


def cmd_new(args: argparse.Namespace) -> int:
    version = args.version
    title = args.title
    src = _current_target()
    if src is None:
        # 第一次创建——从备份复制
        bak = _ROOT / "workflow_assets" / "_refactor_backup" / "RULES_REFACTOR_PLAN_v1_2026-06-17.md"
        if not bak.exists():
            print(f"[ERROR] current 未设置 + 备份文件不存在: {bak}", file=sys.stderr)
            return 1
        src = bak
    dst = _plan_dir(version)
    if dst.exists():
        print(f"[ERROR] {dst} 已存在", file=sys.stderr)
        return 1
    dst.mkdir(parents=True)
    # 复制 PLAN.md（如果源是目录）
    if src.is_dir():
        if (src / "PLAN.md").exists():
            shutil.copy(src / "PLAN.md", dst / "PLAN.md")
    else:
        # 源是 .md 文件
        shutil.copy(src, dst / "PLAN.md")
    # 必填 3 栏
    (dst / "open_questions.md").write_text(
        f"# v{version} 遗留问题\n\n> 启动时先答\n",
        encoding="utf-8",
    )
    (dst / "resolved_questions.md").write_text(
        f"# v{version} 已解决的问题\n",
        encoding="utf-8",
    )
    _write_json(dst / "decisions.json", {
        "version": version,
        "title": title,
        "status": "草稿",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "based_on": src.name if isinstance(src, Path) else None,
        "open_questions": [],
        "resolved_questions": [],
    })
    # 切 current 软链
    if CURRENT_LINK.is_symlink() or CURRENT_LINK.exists():
        CURRENT_LINK.unlink()
    CURRENT_LINK.symlink_to(dst.relative_to(DESIGN_ITER))
    print(f"✅ 已创建 {version}: {dst}")
    print(f"   - 必填 3 栏：{dst}/PLAN.md (顶部加 3 栏框架)")
    print(f"   - 当前生效：{CURRENT_LINK} → {dst.relative_to(DESIGN_ITER)}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    v1, v2 = args.v1, args.v2
    p1, p2 = _plan_dir(v1), _plan_dir(v2)
    if not p1.exists() or not p2.exists():
        print(f"[ERROR] 方案不存在: v1={p1} v2={p2}", file=sys.stderr)
        return 1
    f1 = p1 / "PLAN.md"
    f2 = p2 / "PLAN.md"
    if not f1.exists() or not f2.exists():
        print("[ERROR] PLAN.md 缺失", file=sys.stderr)
        return 1
    out = p2 / "changes" / f"diff_{v1}_to_{v2}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# 方案差异 {v1} → {v2}\n",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        "## PLAN.md 行数对比\n",
        f"- {v1}: {len(f1.read_text(encoding='utf-8').splitlines())} 行",
        f"- {v2}: {len(f2.read_text(encoding='utf-8').splitlines())} 行\n",
        "## 遗留问题数对比\n",
        f"- {v1}: {_count_open_questions(v1)}",
        f"- {v2}: {_count_open_questions(v2)}\n",
        "## 已解决问题数对比\n",
        f"- {v1}: {_count_resolved(v1)}",
        f"- {v2}: {_count_resolved(v2)}\n",
        "> **注**：完整文本差异用 `git diff {v1} {v2}` 自行查看\n",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ diff 已生成: {out}")
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    version = args.version
    target = _plan_dir(version)
    if not target.exists():
        print(f"[ERROR] {version} 不存在: {target}", file=sys.stderr)
        return 1
    # 备份 current → archive/
    cur = _current_target()
    if cur is not None and cur.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_name = f"{cur.name}_{ts}.bak"
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        if cur.is_dir():
            shutil.copytree(cur, ARCHIVE_DIR / bak_name)
        else:
            shutil.copy(cur, ARCHIVE_DIR / bak_name)
        print(f"  - 备份当前: {cur.name} → archive/{bak_name}")
    # 改软链
    if CURRENT_LINK.is_symlink() or CURRENT_LINK.exists():
        CURRENT_LINK.unlink()
    CURRENT_LINK.symlink_to(target.relative_to(DESIGN_ITER))
    print(f"✅ 回滚完成: current → {target.relative_to(DESIGN_ITER)}")
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    version = args.version
    qid = args.question_id
    p = _plan_dir(version)
    oq = p / "open_questions.md"
    rq = p / "resolved_questions.md"
    if not oq.exists() or not rq.exists():
        print(f"[ERROR] {p} 缺 open_questions.md 或 resolved_questions.md", file=sys.stderr)
        return 1
    oq_text = oq.read_text(encoding="utf-8")
    # 支持两种行首格式：`- [ ]` 复选框 / `- [ X ]` 候选标记
    pattern = f"**{qid}**:"
    if pattern not in oq_text:
        print(f"[ERROR] {qid} 不在 open_questions.md", file=sys.stderr)
        return 1
    # 提取整行（去掉候选标记字母，改为复选框已勾）
    import re
    new_oq = []
    resolved_line = None
    for line in oq_text.splitlines():
        if pattern in line and line.lstrip().startswith("-"):
            # 把行首的 `- [ <letter> ]` 改为 `- [x]`，保留其余内容
            resolved_line = re.sub(r"^(\s*)-\s*\[\s*[A-Z]\s*\]", r"\1- [x]", line, count=1)
        else:
            new_oq.append(line)
    oq.write_text("\n".join(new_oq) + "\n", encoding="utf-8")
    rq_text = rq.read_text(encoding="utf-8")
    rq_text += f"\n{resolved_line}\n  - 解决时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    rq.write_text(rq_text, encoding="utf-8")
    print(f"✅ {qid} 已标记为已解决")
    return 0


# ---------- main ----------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="design_iter.py",
        description="AIDocxWorkFlow 方案迭代 CLI",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", help="创建新方案 v{N}")
    p_new.add_argument("version", help="版本号（如 v2）")
    p_new.add_argument("title", help="方案标题")
    p_new.set_defaults(func=cmd_new)

    p_list = sub.add_parser("list", help="列出所有方案")
    p_list.set_defaults(func=cmd_list)

    p_status = sub.add_parser("status", help="状态总览")
    p_status.set_defaults(func=cmd_status)

    p_diff = sub.add_parser("diff", help="生成方案 diff")
    p_diff.add_argument("v1", help="旧版本")
    p_diff.add_argument("v2", help="新版本")
    p_diff.set_defaults(func=cmd_diff)

    p_rb = sub.add_parser("rollback", help="回滚到指定版本")
    p_rb.add_argument("version", help="目标版本")
    p_rb.set_defaults(func=cmd_rollback)

    p_resolve = sub.add_parser("resolve", help="标记问题已解决")
    p_resolve.add_argument("version", help="方案版本")
    p_resolve.add_argument("question_id", help="问题 ID（如 Q-001）")
    p_resolve.set_defaults(func=cmd_resolve)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
