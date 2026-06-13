#!/usr/bin/env python3
"""AIDocxWorkFlow 计费查看器

Usage:
  python3 viewer.py --total        # 累计汇总
  python3 viewer.py --today       # 今日记录
  python3 viewer.py --all         # 全部记录（默认）
  python3 viewer.py --by-source   # 按来源分组（conv/tool/mcp/session）
  python3 viewer.py --sessions     # 按会话分组汇总
  python3 viewer.py --session <id> # 指定会话的详细记录
"""

import json, sys, argparse
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BILLING_DIR = Path(__file__).parent.resolve()
SESSION_LOG = BILLING_DIR / "session_log.jsonl"
CUMULATIVE = BILLING_DIR / "cumulative.json"


def load_cumulative():
    if CUMULATIVE.exists():
        try:
            with CUMULATIVE.open(encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_tokens": 0.0, "total_cost": 0.0, "records": 0}


def load_records():
    records = []
    if SESSION_LOG.exists():
        try:
            with SESSION_LOG.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except Exception:
            pass
    return records


def fmt_cost(cost):
    return f"${cost:.4f}"


def fmt_duration(ms):
    if ms >= 3_600_000:
        return f"{ms/3_600_000:.1f}h"
    if ms >= 60_000:
        return f"{ms/60_000:.1f}m"
    if ms >= 1000:
        return f"{ms/1000:.1f}s"
    return f"{ms}ms"


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_total():
    data = load_cumulative()
    print(f"\n{'═'*52}")
    print(f"  AIDocxWorkFlow 计费累计汇总")
    print(f"{'═'*52}")
    print(f"  总 Token:  {int(data['total_tokens']):>14,}")
    print(f"  总费用:    {fmt_cost(data['total_cost']):>14}")
    print(f"  记录条数: {data['records']:>14}")
    print(f"{'═'*52}\n")


def cmd_today():
    today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    records  = [r for r in load_records() if r.get("timestamp","").startswith(today)]
    print(f"\n{'═'*72}")
    print(f"  今日计费 ({today}) — 共 {len(records)} 条")
    print(f"{'═'*72}")
    if not records:
        print("  (暂无记录)")
        print(f"{'═'*72}\n")
        return
    print(f"  {'时间':<22} {'来源':<8} {'标签':<22} {'Token':>10} {'费用':>10}")
    print(f"  {'-'*72}")
    tt, tc = 0, 0.0
    for r in records:
        ts   = r.get("timestamp","")[:19]
        src  = r.get("source","?")
        lbl  = r.get("step_label","") or r.get("tool_name","") or r.get("record_type","")
        toks = r.get("total_tokens", 0)
        cost = r.get("estimated_cost_usd", 0.0)
        ok   = "✓" if r.get("success",True) else "✗"
        tt  += toks; tc += cost
        print(f"  {ts:<22} {src:<8} {lbl:<22} {toks:>10,} {fmt_cost(cost):>10}  {ok}")
    print(f"  {'-'*72}")
    print(f"  {'今日合计':<54} {tt:>10,} {fmt_cost(tc):>10}")
    print(f"{'═'*72}\n")


def cmd_all():
    records = load_records()
    if not records:
        print("暂无计费记录。")
        return
    print(f"\n{'═'*80}")
    print(f"  会话计费记录 — 共 {len(records)} 条")
    print(f"{'═'*80}")
    print(f"  {'时间':<22} {'来源':<8} {'类型':<10} {'标签':<20} {'Token':>10} {'费用':>10}")
    print(f"  {'-'*80}")
    for r in records:
        ts   = r.get("timestamp","")[:19]
        src  = r.get("source","")
        typ  = r.get("record_type","")
        lbl  = r.get("step_label","") or r.get("tool_name","") or r.get("record_type","")
        toks = r.get("total_tokens", 0)
        cost = r.get("estimated_cost_usd", 0.0)
        print(f"  {ts:<22} {src:<8} {typ:<10} {lbl:<20} {toks:>10,} {fmt_cost(cost):>10}")
    print(f"{'═'*80}\n")


def cmd_by_source():
    records = load_records()
    if not records:
        print("暂无计费记录。")
        return
    by_src = defaultdict(lambda: {"tokens":0,"cost":0.0,"count":0})
    for r in records:
        src = r.get("source","unknown")
        by_src[src]["tokens"] += r.get("total_tokens", 0)
        by_src[src]["cost"]   += r.get("estimated_cost_usd", 0.0)
        by_src[src]["count"]  += 1
    print(f"\n{'═'*52}")
    print(f"  按来源分组统计")
    print(f"{'═'*52}")
    print(f"  {'来源':<12} {'记录数':>8} {'Token':>12} {'费用':>12}")
    print(f"  {'-'*52}")
    for src, d in sorted(by_src.items()):
        print(f"  {src:<12} {d['count']:>8} {d['tokens']:>12,} {fmt_cost(d['cost']):>12}")
    print(f"{'═'*52}\n")


def cmd_sessions():
    records = load_records()
    if not records:
        print("暂无计费记录。")
        return
    by_sid = defaultdict(lambda: {"toks":0,"cost":0.0,"count":0,"turns":0,"first":None,"last":None})
    for r in records:
        sid  = r.get("session_id","?")
        d    = by_sid[sid]
        d["toks"] += r.get("total_tokens", 0)
        d["cost"] += r.get("estimated_cost_usd", 0.0)
        d["count"] += 1
        if r.get("record_type") == "turn":
            d["turns"] = max(d["turns"], r.get("turn_number", 0))
        ts = r.get("timestamp","")
        if not d["first"]: d["first"] = ts[:19]
        d["last"] = ts[:19]

    print(f"\n{'═'*78}")
    print(f"  会话汇总 — 共 {len(by_sid)} 个会话")
    print(f"{'═'*78}")
    print(f"  {'会话ID':<14} {'首条':<20} {'末条':<20} {'轮次':>5} {'记录':>6} {'Token':>12} {'费用':>10}")
    print(f"  {'-'*78}")
    for sid, d in sorted(by_sid.items()):
        print(f"  {sid[:12]:<14} {d['first']:<20} {d['last']:<20} {d['turns']:>5} {d['count']:>6} {d['toks']:>12,} {fmt_cost(d['cost']):>10}")
    print(f"{'═'*78}\n")


def cmd_session_detail(sid_prefix: str):
    records = [r for r in load_records() if r.get("session_id","").startswith(sid_prefix)]
    if not records:
        print(f"未找到会话: {sid_prefix}")
        return
    sid  = records[0].get("session_id","?")
    tt, tc = 0, 0.0
    print(f"\n{'═'*78}")
    print(f"  会话详情: {sid}")
    print(f"{'═'*78}")
    print(f"  {'时间':<22} {'来源':<8} {'类型':<12} {'标签':<20} {'Token':>10} {'费用':>10}")
    print(f"  {'-'*78}")
    for r in records:
        ts   = r.get("timestamp","")[:19]
        src  = r.get("source","")
        typ  = r.get("record_type","")
        lbl  = r.get("step_label","") or r.get("tool_name","") or r.get("record_type","")
        toks = r.get("total_tokens", 0)
        cost = r.get("estimated_cost_usd", 0.0)
        dur  = r.get("duration_ms", 0)
        tt  += toks; tc += cost
        dur_str = f" ({fmt_duration(dur)})" if dur else ""
        print(f"  {ts:<22} {src:<8} {typ:<12} {lbl:<20} {toks:>10,} {fmt_cost(cost):>10}{dur_str}")
    print(f"  {'-'*78}")
    print(f"  {'会话合计':<64} {tt:>10,} {fmt_cost(tc):>10}")
    print(f"{'═'*78}\n")


# ── main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AIDocxWorkFlow 计费查看器")
    parser.add_argument("--total",       action="store_true", help="累计汇总")
    parser.add_argument("--today",      action="store_true", help="今日记录")
    parser.add_argument("--all",        action="store_true", help="全部记录")
    parser.add_argument("--by-source", action="store_true", help="按来源分组")
    parser.add_argument("--sessions",    action="store_true", help="按会话分组")
    parser.add_argument("--session",     metavar="ID",        help="指定会话详情（前缀匹配）")
    args = parser.parse_args()

    if args.total:
        cmd_total()
    elif args.today:
        cmd_today()
    elif args.by_source:
        cmd_by_source()
    elif args.sessions:
        cmd_sessions()
    elif args.session:
        cmd_session_detail(args.session)
    else:
        cmd_all()


if __name__ == "__main__":
    main()
