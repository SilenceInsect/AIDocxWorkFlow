#!/usr/bin/env python3
"""
fix_s5_boundary_and_duplicates.py
修复 S5 测试点两问题：
  S5-001: BOUNDARY → BOUNDARY_MIN/MAX/MIN-1/MAX+1
  S5-002: TP ID 重复
"""

import json
import re
from pathlib import Path
from collections import Counter

TP_PATH = Path("workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json")
OUT_PATH = TP_PATH

# ── 辅助：判断边界子类型 ────────────────────────────────────────────────
def classify_boundary(title: str, description: str) -> str:
    """根据 title/description 文本推断边界子类型"""
    combined = (title + " " + description).lower()

    # MAX+1：超过、超额、超出、上限+1、最大数+1
    if re.search(r"(超过|超出|上限\s*\+?\s*1?|最多\s*\+?\s*1?|最大\s*\+?\s*1?|超限额|超库存|超额|超购)", combined):
        return "BOUNDARY_MAX+1"
    # MIN-1：低于、下限-1、最少-1、最小-1、不足、零个、空
    if re.search(r"(低于|下限\s*-?\s*1?|最少\s*-?\s*1?|最小\s*-?\s*1?|不足\s*1?|零个|空\s*输入|0\s*个)", combined):
        return "BOUNDARY_MIN-1"
    # MIN：最小值、底限、起始、首次、空字符串、空名称
    if re.search(r"(最小值|底限|起始|首次|边界|端点|0\s*条?|一个|空字符串|空输入)", combined):
        return "BOUNDARY_MIN"
    # MAX：最大值、上限、满、最大数、最多
    if re.search(r"(最大值|上限|最多|满|最大数|最大)", combined):
        return "BOUNDARY_MAX"

    # 默认按最小值边界处理（大多数 UI 边界为第一项）
    return "BOUNDARY_MIN"


def fix_file():
    raw = TP_PATH.read_text(encoding="utf-8")
    data = json.loads(raw)

    results = {
        "S5-001": {"total_boundary": 0, "changes": []},
        "S5-002": {"duplicates": [], "fixed": 0},
    }

    # ── Step 1: 修复 BOUNDARY 枚举 ─────────────────────────────────────
    boundary_counter = Counter()

    for tp in data.get("test_points", []):
        if tp.get("test_point_type") == "BOUNDARY":
            old_type = tp["test_point_type"]
            new_type = classify_boundary(
                tp.get("title", ""), tp.get("description", "")
            )
            tp["test_point_type"] = new_type
            results["S5-001"]["total_boundary"] += 1
            results["S5-001"]["changes"].append({
                "tp_id": tp["tp_id"],
                "title": tp.get("title", ""),
                "old": old_type,
                "new": new_type,
            })
            boundary_counter[new_type] += 1

    # ── Step 2: 修复 TP ID 重复 ───────────────────────────────────────
    tp_ids = [tp["tp_id"] for tp in data.get("test_points", [])]
    counter = Counter(tp_ids)
    seen = {}  # tp_id → 下一个可用序号

    for tp in data.get("test_points", []):
        tid = tp["tp_id"]
        if counter[tid] > 1:
            # 记录重复
            if tid not in results["S5-002"]["duplicates"]:
                results["S5-002"]["duplicates"].append(tid)
                results["S5-002"]["fixed"] += counter[tid] - 1

            # 递增重命名
            seen[tid] = seen.get(tid, 1) + 1
            old_id = tid
            # 末尾 -NN 模式：替换最后一位数字
            new_id = re.sub(r'(\d+)$', str(seen[tid]).zfill(2), tid)
            tp["tp_id"] = new_id
            tp["s5_ref"] = new_id

    # ── Step 3: 保存 ─────────────────────────────────────────────────
    TP_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return results, boundary_counter


def report(results, boundary_counter):
    lines = []
    lines.append("## S5 测试点修复报告\n")
    lines.append(f"修复时间: 2026-07-21\n\n")

    # S5-001
    lines.append("### S5-001: BOUNDARY 枚举修复\n")
    lines.append(f"总计修复: {results['S5-001']['total_boundary']} 项\n\n")
    lines.append("| tp_id | 标题 | 原类型 | 新类型 |\n")
    lines.append("|------|------|--------|--------|\n")
    for c in results["S5-001"]["changes"]:
        lines.append(f"| {c['tp_id']} | {c['title'][:30]} | {c['old']} | {c['new']} |\n")

    lines.append("\n**分布统计**:\n")
    for k, v in sorted(boundary_counter.items()):
        lines.append(f"- {k}: {v}\n")

    # S5-002
    lines.append("\n### S5-002: TP ID 重复修复\n")
    lines.append(f"重复 ID 数量: {len(results['S5-002']['duplicates'])}\n")
    lines.append(f"修复数量: {results['S5-002']['fixed']} 项\n\n")
    for dup in results["S5-002"]["duplicates"]:
        lines.append(f"- `{dup}`\n")

    return "".join(lines)


if __name__ == "__main__":
    results, bc = fix_file()
    rpt = report(results, bc)
    print(rpt)
    print("\n修复完成。文件已保存。")
