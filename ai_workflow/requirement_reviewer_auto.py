#!/usr/bin/env python3
"""S1 — 材料门禁（纯检查，非评分）+ S1 评分辅助。

职责：
1. check_material_gate() — 仅检查输入材料是否满足最低可处理条件（文件可解析 / 正文≥50字）
2. auto_review_requirement() — 辅助 S1 LLM 评审，按 5 维度评分格式生成结构化评审框架

S1 的 5 维度评分和判决由 LLM 按 STAGE_S1_REVIEW.mdc 执行。
本模块仅提供结构化评审框架模板，不产生最终评分。
quality_level 由 S1.5 的 P0/P1/P2 填写情况决定，与本模块返回值无关。
"""

from __future__ import annotations

from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# S1 物料门禁（纯检查，非评分）
# ─────────────────────────────────────────────────────────────────────────────

def check_material_gate(req_text: str | dict) -> dict:
    """
    纯材料门禁检查。

    参数:
        req_text: 原始需求文本字符串，或 dict（取 "text" 字段）

    返回:
        dict: {
            "gate_passed": bool,   # 门禁是否通过
            "reason": str,         # 通过 / 失败原因
        }
    """
    if isinstance(req_text, dict):
        req_text = req_text.get("text", str(req_text))

    if not req_text or not req_text.strip():
        return {
            "gate_passed": False,
            "reason": "需求文本为空，无法进入评审流程。",
        }

    if len(req_text.strip()) < 50:
        return {
            "gate_passed": False,
            "reason": f"需求文本过短（{len(req_text.strip())} 字），不足 50 字，无法进入评审流程。",
        }

    return {
        "gate_passed": True,
        "reason": "材料门禁通过，进入 S1 LLM 评审。",
    }


# ─────────────────────────────────────────────────────────────────────────────
# S1 评分辅助 — 5 维度评审框架模板
# ─────────────────────────────────────────────────────────────────────────────

# 5 维度权重（与 STAGE_S1_REVIEW.mdc 严格一致）
S1_DIMENSIONS = [
    ("完整性",   0.25, "角色定义、需求对象拆解、功能覆盖、验收标准是否齐全"),
    ("清晰度",   0.25, "无模糊术语、有量化指标、术语定义一致"),
    ("一致性",   0.20, "角色 / 需求对象 / 功能三层之间无矛盾"),
    ("可测试性", 0.20, "每个业务故事有明确通过/失败条件（业务故事数 / 功能点数 = 100%，1:1 配对）"),
    ("可行性",   0.10, "技术约束已识别，无未定义的外部依赖"),
]

# 判决阈值（与 STAGE_S1_REVIEW.mdc 严格一致）
S1_VERDICT_THRESHOLDS = [
    (7.0,  "PASS",          "生成终版需求.md → S1.5"),
    (4.0,  "NEEDS_REVISION", "输出修改建议，等待修订后重审"),
    (0.0,  "REJECT",        "输出失败报告，停止流水线"),
]


def auto_review_requirement(requirement_text: str) -> dict:
    """
    生成 S1 5 维度评审的结构化框架。

    本函数**不产生评分**（评分由 LLM 给出），仅提供：
    1. 分维度评审提示（每维度的评审要点）
    2. 审查产物清单（role_definitions / requirement_objects / clarification_checklist 格式）
    3. PURCHASE_STRONG 识别规则
    4. 最终判决阈值

    参数:
        requirement_text: 需求文本字符串

    返回:
        dict: {
            "verdict": str,          # PASS / NEEDS_REVISION / REJECT（由 LLM 填写）
            "score_total": float,     # 加权总分（由 LLM 填写，范围 0.0-10.0）
            "dimension_scores": list,  # 每维度得分（由 LLM 填写）
            "review_framework": dict,  # 结构化评审框架（脚本生成）
            "products": dict,         # 审查产物模板（脚本生成）
        }
    """
    if isinstance(requirement_text, dict):
        requirement_text = requirement_text.get("text", str(requirement_text))

    # ── 维度评审框架 ────────────────────────────────────────────────────
    dimension_frames = []
    for name, weight, points in S1_DIMENSIONS:
        dimension_frames.append({
            "dimension": name,
            "weight": weight,
            "review_points": points,
            "score": None,          # LLM 填写：1.0-10.0
            "findings": [],         # LLM 填写：具体发现
            "issues": [],           # LLM 填写：缺失/冲突项
        })

    # ── PURCHASE_STRONG 识别 ────────────────────────────────────────────
    purchase_strong_subtypes = [
        ("发奖", "邮件 / 背包 / 资产生成 / 补发 / 补偿"),
        ("排行", "个人榜 / 团队榜 / 赛季榜 / 服务端权威榜"),
        ("订单", "充值 / 退款 / 对账 / 发票 / 风控拦截"),
        ("兑换", "商店 / 兑换码 / 补款 / 限时礼包"),
        ("VIP",  "VIP 等级 / 月卡 / 季卡 / 永久卡 / 状态机失效"),
        ("战令", "多档位发奖 / 经验计算 / 等级解锁"),
    ]

    # ── 审查产物模板 ────────────────────────────────────────────────────
    product_templates = {
        "role_definitions": {
            "description": "角色定义与分类",
            "format": "主角色 / 次角色 / 边界角色 + 典型场景（无数量下限）",
            "source": "从需求文本抽取；无显式角色时必须反推并标注【反推】",
        },
        "requirement_objects": {
            "description": "需求对象拆解 + 8 模块标签",
            "format": "角色 → 需求对象 → 功能 → 业务故事（1:1 配对 = 100%）",
            "modules": ["CONFIG", "UI", "BIZ", "AUX", "LINK", "LOG", "SPECIAL", "HINT"],
            "module_source": ".cursor/MODULES.md §1（项目级唯一真相源）",
        },
        "clarification_checklist": {
            "description": "问题需求清单（S1.5 准入物料）",
            "format": "P0/P1/P2 三级 + SPECIAL_FLAG 列",
            "special_flag_rules": "强付费项（PURCHASE_STRONG）识别后必须检查3段契约：程序自测点 / 测试覆盖 / 策划验收",
        },
    }

    # ── 强付费项3段契约 ────────────────────────────────────────────────
    purchase_contract = {
        "段1_程序自测点": "程序自行验证的入口（GM 命令 / 测试脚本 / 沙盒）",
        "段2_测试覆盖": "列出该功能需覆盖的测试场景",
        "段3_策划验收": "策划验收的方式（数值表比对 / 案例回放 / 抽检比例）",
        "缺失判定": {
            "缺1段": "生成 1 条 P0（SPECIAL_FLAG = PURCHASE_STRONG）",
            "缺2段": "生成 2 条 P0（SPECIAL_FLAG = PURCHASE_STRONG）",
            "缺3段": "生成 3 条 P0（SPECIAL_FLAG = PURCHASE_STRONG）",
        },
        "注意": "不阻断 S1，但 S1.5 必须由人工补齐；强付费项 P0 未全部答完 → S2 拒绝执行",
    }

    return {
        # LLM 填写区
        "verdict": None,           # 由 LLM 填写：PASS / NEEDS_REVISION / REJECT
        "score_total": None,       # 由 LLM 填写：0.0-10.0
        "dimension_scores": None,   # 由 LLM 填写：[{"dimension": "...", "score": 7.5, ...}]

        # 脚本生成区（框架模板）
        "review_framework": {
            "dimensions": dimension_frames,
            "verdict_thresholds": [
                {"min_score": 7.0,  "verdict": "PASS"},
                {"min_score": 4.0,  "verdict": "NEEDS_REVISION"},
                {"min_score": 0.0,  "verdict": "REJECT"},
            ],
            "purchase_strong_subtypes": purchase_strong_subtypes,
            "purchase_contract": purchase_contract,
            "output_dir": "workflow_assets/<req_name>/「S1 需求评审」/<version>/",
        },

        "products": product_templates,

        # 元数据
        "text_length": len(requirement_text.strip()) if requirement_text else 0,
        "note": (
            "本函数仅生成评审框架模板。评分和判决由 LLM 在 S1 评审中按 "
            "STAGE_S1_REVIEW.mdc 的 5 维度评审规范填写。函数本身不产生最终评分。"
        ),
    }


def compute_weighted_score(dimension_scores: list[dict]) -> float:
    """
    根据 5 维度得分计算加权总分。

    参数:
        dimension_scores: [{"dimension": str, "score": float}, ...]

    返回:
        float: 加权总分（0.0-10.0，保留 1 位小数）
    """
    total = 0.0
    dim_map = {d["dimension"]: d["score"] for d in dimension_scores}

    for name, weight, _ in S1_DIMENSIONS:
        score = dim_map.get(name, 0.0)
        total += score * weight

    return round(total, 1)


def get_verdict(score_total: float) -> str:
    """
    根据加权总分返回判决。

    参数:
        score_total: 加权总分（0.0-10.0）

    返回:
        str: PASS / NEEDS_REVISION / REJECT
    """
    for threshold, verdict, _ in S1_VERDICT_THRESHOLDS:
        if score_total >= threshold:
            return verdict
    return "REJECT"
