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

# scripts 在 governance/design_iter/scripts/ 下 → parents[3] = 项目根
_ROOT = Path(__file__).resolve().parents[3]
DESIGN_ITER = _ROOT / "governance" / "design_iter"
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


# ---------- 触发协议（2026-07-15 新增：主动停止 / 完整迭代 / 切版本） ----------

def _sync_index_json(trigger: str, version: str) -> None:
    """触发协议的统一写入：更新 INDEX.json#updated_at + current（如切版本）。

    不写 INDEX.md 正文（人写）；只保证 SSOT（INDEX.json）的事实正确。
    """
    data = _read_json(INDEX_JSON)
    if not data:
        data = {"schema_version": "1.0", "plans": []}
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    if trigger == "switch":
        data["current"] = version
    _write_json(INDEX_JSON, data)


def cmd_stop_iter(args: argparse.Namespace) -> int:
    """主动停止迭代：当前 current 状态 → "暂停"（写入 §3 交接行）。"""
    cur = _current_target()
    if cur is None:
        print("[ERROR] current 未设置，无法停止", file=sys.stderr)
        return 1
    version = cur.name
    reason = args.reason or "(未填原因)"
    idx = DESIGN_ITER / "INDEX.md"
    if not idx.exists():
        print("[ERROR] INDEX.md 不存在", file=sys.stderr)
        return 1
    text = idx.read_text(encoding="utf-8")
    # 在 §3 表格末尾追加 ⏸ 延迟行（幂等：同版本同原因不重复）
    stop_row = f"| {version} | (v15 启动时填) | {reason[:80]} | {datetime.now().strftime('%Y-%m-%d')} | ⏸ 延迟 |"
    marker = f"<!-- stop_iter:{version}:{reason[:20]} -->"
    if marker in text:
        print(f"⚠️ {version} 已记录过停止原因，跳过重复写入")
    else:
        # 找 §3 表格最后一行（"### 4. 触发与维护"之前）
        anchor = "### 4. 触发与维护"
        if anchor in text:
            text = text.replace(
                anchor,
                f"{marker}\n{stop_row}\n\n{anchor}",
                1,
            )
        else:
            # fallback：追加到末尾
            text += f"\n{marker}\n{stop_row}\n"
        idx.write_text(text, encoding="utf-8")
    _sync_index_json("stop", version)
    print(f"✅ {version} 已标记为「主动停止」：{reason}")
    print(f"   - INDEX.md §3 已加 ⏸ 延迟行（带 marker 防重）")
    print(f"   - INDEX.json#updated_at 已更新")
    return 0


def cmd_complete_iter(args: argparse.Namespace) -> int:
    """完整迭代完成：v{N} 闭环 + 在 §3 写入 v{N}→v{N+1} 交接承诺。"""
    version = args.version
    p = _plan_dir(version)
    if not p.exists():
        print(f"[ERROR] {version} 不存在: {p}", file=sys.stderr)
        return 1
    # 自动推导 next = 数字 + 1（v9 → v10）
    try:
        n = int(version.lstrip("v"))
        next_version = f"v{n + 1}"
    except ValueError:
        next_version = args.next_version or f"{version}_next"
    idx = DESIGN_ITER / "INDEX.md"
    if not idx.exists():
        print("[ERROR] INDEX.md 不存在", file=sys.stderr)
        return 1
    text = idx.read_text(encoding="utf-8")
    # 幂等 marker
    marker = f"<!-- complete_iter:{version} -->"
    if marker in text:
        print(f"⚠️ {version} 已记录过完成，跳过重复")
    else:
        # §3 加 v{N}→v{N+1} 交接"🟡 待接"
        handover_row = f"| {version} | {next_version} | （在 v{next_version} 启动时填关键交付） | {datetime.now().strftime('%Y-%m-%d')} | 🟡 待接 |"
        text = text.replace(
            "### 4. 触发与维护",
            f"{marker}\n{handover_row}\n\n### 4. 触发与维护",
            1,
        )
        idx.write_text(text, encoding="utf-8")
    # 同步 decisions.json status（如果有）
    dec_file = p / "decisions.json"
    if dec_file.exists():
        dec = _read_json(dec_file)
        dec["status"] = "已闭环"
        dec["closed_at"] = datetime.now().strftime("%Y-%m-%d")
        _write_json(dec_file, dec)
    _sync_index_json("complete", version)
    print(f"✅ {version} 已标记为「完整迭代」：")
    print(f"   - INDEX.md §3 加 v{version}→v{next_version} 交接行（🟡 待接）")
    print(f"   - plans/{version}/decisions.json#status → 已闭环")
    print(f"   - INDEX.json#updated_at 已更新")
    return 0


def cmd_switch(args: argparse.Namespace) -> int:
    """切换迭代版本：把 current 改为指定版本。"""
    version = args.version
    target = _plan_dir(version)
    if not target.exists():
        print(f"[ERROR] {version} 不存在: {target}", file=sys.stderr)
        return 1
    # 备份当前 current → archive
    cur = _current_target()
    if cur is not None and cur.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_name = f"{cur.name}_{ts}.bak"
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        if cur.is_dir():
            shutil.copytree(cur, ARCHIVE_DIR / bak_name)
        else:
            shutil.copy(cur, ARCHIVE_DIR / bak_name)
    # 改 current 软链
    if CURRENT_LINK.is_symlink() or CURRENT_LINK.exists():
        CURRENT_LINK.unlink()
    CURRENT_LINK.symlink_to(target.relative_to(DESIGN_ITER))
    # 同步 INDEX.json#current + §1 当前生效 current 单元格
    _sync_index_json("switch", version)
    idx = DESIGN_ITER / "INDEX.md"
    if idx.exists():
        text = idx.read_text(encoding="utf-8")
        # 精确替换 §1 表格中"current"单元格（在 markdown 表格行内匹配 `[vXX]`）
        import re
        new_text = re.sub(
            r"\[\`v\d+\`\]\(plans/v\d+/\)",
            f"[`{version}`](plans/{version}/)",
            text,
            count=1,
        )
        idx.write_text(new_text, encoding="utf-8")
    print(f"✅ 已切 current: {cur.name if cur else '(无)'} → {version}")
    print(f"   - current 软链 → {target.relative_to(DESIGN_ITER)}")
    print(f"   - INDEX.json#current 已同步")
    print(f"   - INDEX.md §1 current 单元格已替换")
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

    # 触发协议三命令（2026-07-15 新增）
    p_stop = sub.add_parser("stop_iter", help="主动停止迭代（写 INDEX.md §3 ⏸ 延迟行）")
    p_stop.add_argument("--reason", default="", help="停止原因（写入交接行）")
    p_stop.set_defaults(func=cmd_stop_iter)

    p_complete = sub.add_parser("complete_iter", help="完整迭代完成（写 §3 交接承诺）")
    p_complete.add_argument("version", help="完成版本（如 v14）")
    p_complete.add_argument("--next-version", default="", help="手动指定下一版本（默认自动 +1）")
    p_complete.set_defaults(func=cmd_complete_iter)

    p_switch = sub.add_parser("switch", help="切换 current 版本（同步 INDEX.json + INDEX.md §1）")
    p_switch.add_argument("version", help="目标版本（如 v15）")
    p_switch.set_defaults(func=cmd_switch)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
