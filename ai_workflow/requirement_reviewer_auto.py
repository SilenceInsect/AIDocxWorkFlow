#!/usr/bin/env python3
"""S1 — 需求自动评分引擎（规则引擎，非 AI）。

输入：原始需求文本（字符串或 dict）
输出：评分结果 + 判决
"""

from __future__ import annotations
import re, math
from typing import Optional


# ── 评分维度 ───────────────────────────────────────────────────────────────

_DIMENSIONS = {
    "completeness":  {"weight": 0.25, "max": 10.0},
    "clarity":        {"weight": 0.25, "max": 10.0},
    "consistency":    {"weight": 0.20, "max": 10.0},
    "testability":   {"weight": 0.20, "max": 10.0},
    "feasibility":   {"weight": 0.10, "max": 10.0},
}

_GATE_THRESHOLD = 7.0


# ── 评分规则 ───────────────────────────────────────────────────────────────

def _score_completeness(text: str) -> float:
    """完整性：是否覆盖关键要素（角色、流程、量化指标、验收标准）"""
    score = 5.0
    checks = [
        (r"用户|玩家|管理员|角色", 1.0),
        (r"流程|步骤|操作|购买|支付", 1.5),
        (r"\d+[元%个]", 1.0),
        (r"验收|标准|acceptance|criteria", 1.5),
    ]
    for pat, pts in checks:
        if re.search(pat, text):
            score += pts
    return min(score, 10.0)


def _score_clarity(text: str) -> float:
    """清晰度：语义明确，无歧义句子"""
    score = 5.0
    ambiguous = [r"可能|也许|大概|或许|应该|尽量", r"\?\?|__|\[\s*\]"]
    for pat in ambiguous:
        matches = re.findall(pat, text)
        score -= len(matches) * 0.3
    # 有结构化列表加分
    if re.search(r"^\d+[.)：:、]", text, re.MULTILINE):
        score += 1.5
    if re.search(r"\n[─\-=]{3,}", text):
        score += 1.0
    return max(min(score, 10.0), 0.0)


def _score_consistency(text: str) -> float:
    """一致性：前后术语统一，无明显冲突"""
    score = 8.0
    # 检查矛盾模式
    conflicts = [
        (r"实时.*?定时", -0.5),
        (r"同步.*?异步", -0.3),
    ]
    for pat, delta in conflicts:
        if re.search(pat, text):
            score += delta
    return max(min(score, 10.0), 0.0)


def _score_testability(text: str) -> float:
    """可测试性：是否有明确的输入/输出/前置条件"""
    score = 5.0
    checks = [
        (r"输入|output|input|参数|数据", 1.0),
        (r"预期.*?结果|assert|验证|确认", 1.5),
        (r"前置|前提|precondition|given", 1.5),
        (r"边界|异常|edge|boundary|error", 1.0),
    ]
    for pat, pts in checks:
        if re.search(pat, text, re.IGNORECASE):
            score += pts
    return min(score, 10.0)


def _score_feasibility(text: str) -> float:
    """可行性：技术描述是否合理"""
    score = 7.5
    red_flags = [r"无限|无限制|实时.*?海量", r"100%.*?保证"]
    for pat in red_flags:
        if re.search(pat, text):
            score -= 1.0
    return max(min(score, 10.0), 0.0)


# ── 主函数 ─────────────────────────────────────────────────────────────────

def auto_review_requirement(req_text: str | dict) -> dict:
    """
    对需求文本进行自动评分（规则引擎，非 AI）。

    参数:
        req_text: 原始需求文本字符串，或 dict（取 "text" 字段）

    返回:
        dict: {
            "score_total": float,       # 总分（加权）
            "verdict": str,             # PASS | NEEDS_REVISION | REJECT
            "scores": dict,             # 各维度分数
            "breakdown": dict,          # 详细评分
            "gate_passed": bool,
            "recommendation": str,
        }
    """
    if isinstance(req_text, dict):
        req_text = req_text.get("text", str(req_text))

    if not req_text or len(req_text.strip()) < 50:
        return {
            "score_total": 0.0,
            "verdict": "REJECT",
            "scores": {},
            "breakdown": {},
            "gate_passed": False,
            "recommendation": "需求文本过短或为空，无法评审。",
        }

    # 计算各维度得分
    scores = {
        "completeness": _score_completeness(req_text),
        "clarity":       _score_clarity(req_text),
        "consistency":   _score_consistency(req_text),
        "testability":  _score_testability(req_text),
        "feasibility":  _score_feasibility(req_text),
    }

    # 加权总分
    weighted = sum(
        scores[dim] * _DIMENSIONS[dim]["weight"]
        for dim in _DIMENSIONS
    )

    # 判决
    if weighted >= _GATE_THRESHOLD:
        verdict = "PASS"
    elif weighted >= 5.0:
        verdict = "NEEDS_REVISION"
    else:
        verdict = "REJECT"

    breakdown = {
        dim: {
            "score": round(scores[dim], 2),
            "max": _DIMENSIONS[dim]["max"],
            "weight": _DIMENSIONS[dim]["weight"],
            "weighted": round(scores[dim] * _DIMENSIONS[dim]["weight"], 3),
        }
        for dim in _DIMENSIONS
    }

    recommendation = {
        "PASS": "需求质量合格，建议进入 S2 需求拆解。",
        "NEEDS_REVISION": "需求质量中等，建议补充缺失信息后进入 S2。",
        "REJECT": "需求质量不足，建议完善后再提交评审。",
    }[verdict]

    return {
        "score_total": round(weighted, 3),
        "verdict": verdict,
        "scores": {k: round(v, 2) for k, v in scores.items()},
        "breakdown": breakdown,
        "gate_passed": verdict != "REJECT",
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    sample = """
    游戏道具商城系统：
    1. 玩家可以在商城购买游戏道具，支持游戏币和人民币两种支付方式
    2. 道具价格根据渠道（Android/iOS/Web）使用不同汇率换算
    3. VIP用户享有专属折扣（VIP1:95折，VIP2:90折，VIP3:85折）
    4. 购买成功后道具立即到账，并发送邮件通知
    5. 热门道具在首页推荐区展示（前10个）
    6. 限时折扣可以与VIP折扣叠加，计算最优价
    验收标准：支付成功到道具到账 < 3秒，余额不足时拒绝交易
    """
    result = auto_review_requirement(sample)
    print(f"总分: {result['score_total']}/10 → {result['verdict']}")
    for dim, s in result["scores"].items():
        print(f"  {dim}: {s}/10")
    print(result["recommendation"])
