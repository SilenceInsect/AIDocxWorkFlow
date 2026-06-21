#!/usr/bin/env python3
"""S1 — 材料门禁（纯检查，非评分）+ S1 评分辅助 + 优化识别（S1.8）。

职责：
1. check_material_gate() — 仅检查输入材料是否满足最低可处理条件（文件可解析 / 正文≥50字）
2. auto_review_requirement() — 辅助 S1 LLM 评审，按 5 维度评分格式生成结构化评审框架
3. detect_optimization_blocks() — 识别需求文档中的优化块，生成多选项（形式 A/B/C）
4. generate_regression_guidance() — 根据选中的优化块生成回归测试建议

S1 的 5 维度评分和判决由 LLM 按 STAGE_S1_REVIEW.mdc 执行。
本模块仅提供结构化评审框架模板，不产生最终评分。
quality_level 由 S1.5 的 P0/P1/P2 填写情况决定，与本模块返回值无关。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal, Optional


# ─────────────────────────────────────────────────────────────────────────────
# S1.8 — 优化识别（S1.8 子阶段）
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class OptimizationBlock:
    """单个优化块。"""
    block_id: str
    block_name: str
    block_type: Literal["full_doc", "section", "mixed"]
    marker_style: str
    anchor: str
    scope: str
    summary: str
    content_snippet: str
    affected_modules: list[str] = field(default_factory=list)
    old_content_affected: str = ""  # 被推翻/修改的旧需求范围


@dataclass
class OptimizationManifest:
    """优化识别结果清单。"""
    is_optimization: bool
    optimization_type: Literal["full_doc", "incremental", "none"]
    base_version: Optional[str]
    blocks: list[OptimizationBlock]
    base_summary: Optional[str]


# 优化识别关键词（用于启发式快速预判）
OPTIMIZATION_KEYWORDS = [
    "优化", "变更", "新增", "修改", "重构", "调整",
    "V2", "V3", "v2.", "v3.", "upgrade", "enhancement",
    "2.0", "3.0", "迭代", "版本更新",
    "【优化", "【变更", "【新增", "【修改",
    "## 优化", "## 新增", "## 变更", "## 修改",
]

OPTIMIZATION_MARKER_PATTERNS = [
    # 方括号标记
    (r"【优化[】\s]", "section"),
    (r"【变更[】\s]", "section"),
    (r"【新增[】\s]", "section"),
    (r"【修改[】\s]", "section"),
    (r"\[\[优化\]\]", "section"),
    # 引用块高亮标记
    (r">\s*\*\*变更", "mixed"),
    (r">\s*\*\*新增", "mixed"),
    (r">\s*\*\*优化", "mixed"),
    (r">\s*\*\*修改", "mixed"),
    # 章节标题标记
    (r"^## .*(优化|变更|新增|修改|重构)", re.MULTILINE, "section"),
    (r"^### .*(优化|变更|新增|修改|重构)", re.MULTILINE, "section"),
    # 文档名后缀标记
    (r"优化|重构|升级|v2|v3", "full_doc"),
]


def detect_optimization_blocks(text: str) -> OptimizationManifest:
    """
    识别需求文档中的优化内容块，生成多选项供用户选择。

    返回 OptimizationManifest：
      - optimization_type == "none"       → 非优化文档，执行标准 S1
      - optimization_type == "incremental" → 增量优化文档，呈现多选项
      - optimization_type == "full_doc"  → 全量替换文档，直接执行 S1

    参数:
        text: 需求文档原文（Markdown / plain text）

    返回:
        OptimizationManifest
    """
    if not text or not text.strip():
        return OptimizationManifest(
            is_optimization=False,
            optimization_type="none",
            base_version=None,
            blocks=[],
            base_summary=None,
        )

    lines = text.splitlines()
    blocks: list[OptimizationBlock] = []
    block_id_counter = 1

    # ── 启发式预判：快速扫描关键词密度 ───────────────────────────────
    keyword_count = sum(1 for kw in OPTIMIZATION_KEYWORDS if kw in text)
    keyword_density = keyword_count / max(len(text), 1) * 1000

    # ── 文档名后缀检测（形式 C：全量替换）───────────────────────────
    doc_name_pattern = re.compile(r"(优化|重构|升级|v2|v3|2\.0|3\.0)", re.IGNORECASE)
    first_line = lines[0] if lines else ""
    if doc_name_pattern.search(first_line):
        return OptimizationManifest(
            is_optimization=True,
            optimization_type="full_doc",
            base_version=None,
            blocks=[],
            base_summary="全量替换文档（文档名含优化/升级标识），全文执行 S1 标准评审。",
        )

    # ── 扫描标题行，识别独立优化章节（形式 B）────────────────────────
    current_section = ""
    current_section_start = 0
    section_blocks: list[tuple[int, str, str]] = []  # (line_no, title, anchor)

    for i, line in enumerate(lines):
        stripped = line.strip()
        # 匹配优化章节标题：## 优化、## 新增、## 变更、### 优化 XXX
        m = re.match(r"^(#{1,3})\s+(.*?(优化|变更|新增|修改|重构).*)$", stripped)
        if m:
            if current_section:
                section_blocks.append((current_section_start, current_section, ""))
            current_section = m.group(2).strip()
            current_section_start = i

    if current_section:
        section_blocks.append((current_section_start, current_section, ""))

    # ── 扫描引用块标记（形式 A：混杂高亮）────────────────────────────
    mixed_markers: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if re.match(r"^\s*>\s*\*\*", line) and any(
            kw in line for kw in ["变更", "新增", "优化", "修改"]
        ):
            mixed_markers.append((i, line.strip()[:100]))

    # ── 组装 OptimizationBlock ──────────────────────────────────────
    for start_line, title in section_blocks:
        block_id = f"OPT-{block_id_counter:03d}"
        block_id_counter += 1

        # 采集该章节的前 200 字内容作为 snippet
        section_text = "\n".join(lines[start_line:start_line + 20])
        snippet = section_text.strip()[:200]

        # 推测影响模块
        affected = _infer_affected_modules(title + " " + snippet)

        blocks.append(OptimizationBlock(
            block_id=block_id,
            block_name=title,
            block_type="section",
            marker_style="section_header",
            anchor=f"第 {start_line + 1} 行",
            scope=title,
            summary=title[:50],
            content_snippet=snippet,
            affected_modules=affected,
        ))

    # ── 形式 A：混杂高亮块（识别到但无法精确定位章节）───────────────
    if mixed_markers and not blocks:
        for i, marker_line in mixed_markers[:5]:
            block_id = f"OPT-{block_id_counter:03d}"
            block_id_counter += 1
            affected = _infer_affected_modules(marker_line)
            blocks.append(OptimizationBlock(
                block_id=block_id,
                block_name=marker_line.replace(">", "").replace("**", "").strip()[:60],
                block_type="mixed",
                marker_style="blockquote_highlight",
                anchor=f"第 {i + 1} 行",
                scope="引用块高亮内容",
                summary=marker_line[:50],
                content_snippet=marker_line,
                affected_modules=affected,
            ))

    # ── 最终判定 ─────────────────────────────────────────────────────
    if not blocks:
        if keyword_density > 5:
            # 有关键词但无法结构化 → 标记为需 LLM 深度分析
            blocks.append(OptimizationBlock(
                block_id="OPT-001",
                block_name="全文含优化关键词（需人工定位）",
                block_type="mixed",
                marker_style="keyword_density",
                anchor="全文",
                scope="全文",
                summary="文档中含优化/变更关键词，请人工确认优化范围",
                content_snippet=text[:300],
                affected_modules=[],
            ))

    is_optimization = len(blocks) > 0
    opt_type: Literal["incremental", "none"] = "incremental" if is_optimization else "none"

    # 提取 base_version（如有）
    version_match = re.search(r"v(\d+\.\d+)", text)
    base_version = f"v{version_match.group(1)}" if version_match else None

    # base_summary：取前 100 字
    base_summary = text.strip()[:100] if text else None

    return OptimizationManifest(
        is_optimization=is_optimization,
        optimization_type=opt_type,
        base_version=base_version,
        blocks=blocks,
        base_summary=base_summary,
    )


def _infer_affected_modules(text: str) -> list[str]:
    """从文本内容推断受影响的 8 大模块。"""
    MODULE_KEYWORDS = {
        "CONFIG": ["配置", "数值", "档位", "参数", "config"],
        "UI":     ["界面", "UI", "页面", "弹窗", "按钮", "布局", "展示"],
        "BIZ":    ["业务", "逻辑", "流程", "订单", "购买", "支付", "发奖", "biz"],
        "AUX":    ["缓存", "网络", "SDK", "工具", "aux"],
        "LINK":   ["第三方", "回调", "接口", "对接", "link"],
        "LOG":    ["日志", "埋点", "监控", "log"],
        "SPECIAL":["异常", "风控", "边界", "边界值", "special"],
        "HINT":   ["提示", "红点", "飘字", "Toast", "hint"],
    }
    found = []
    for module, keywords in MODULE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            found.append(module)
    return found or ["BIZ"]  # 兜底为 BIZ（最常见）


# ─────────────────────────────────────────────────────────────────────────────
# S1.8 — 增量上下文（传递给下游阶段）
# ─────────────────────────────────────────────────────────────────────────────

# 增量审查上下文的关键字段
INCREMENTAL_CONTEXT_KEYS = [
    "is_incremental",        # bool：是否增量审查
    "selected_blocks",       # list[str]：选中的 OPT-XXX 块
    "base_version",          # str | None：基础版本（如 v3.01）
    "old_backlog_ref",       # str | None：旧版 backlog 路径
    "affected_modules",       # list[str]：影响模块
    "regression_required",   # bool：是否需要回归用例
    "new_risk_modules",      # list[str]：新引入风险的模块
    "incremental_epics",     # list[str]：增量 Epic ID 列表
    "regression_epics",      # list[str]：需回归的旧 Epic ID 列表
]


def build_incremental_context(
    manifest: OptimizationManifest,
    selected_block_ids: list[str],
    old_backlog_path: Optional[str] = None,
) -> dict:
    """
    根据用户选择的优化块，构建增量上下文，供下游 S1.5→S2→S4→S5→S6→S7→S8 使用。

    参数:
        manifest: detect_optimization_blocks() 的输出
        selected_block_ids: 用户选中的块 ID 列表（如 ["OPT-001"] 或 ["base", "OPT-001"]）
        old_backlog_path: 旧版本 backlog.json 路径（自动推断或手动指定）

    返回:
        dict：增量上下文（携带 INCREMENTAL_CONTEXT_KEYS）
    """
    selected = [b for b in manifest.blocks if b.block_id in selected_block_ids]

    # 聚合影响模块
    affected = list({m for b in selected for m in b.affected_modules})

    # 增量 Epic 数：每个选中块预计 1 个新 Epic
    incremental_epics = [f"OPT-{b.block_id}-001" for b in selected]

    # 回归判断：选中块涉及 BIZ/LINK/SPECIAL 模块时，需要回归
    risk_modules = {"BIZ", "LINK", "SPECIAL", "CONFIG"}
    regression_required = bool(affected & risk_modules)
    new_risk_modules = list(set(affected) & risk_modules)

    return {
        "is_incremental": True,
        "selected_blocks": selected_block_ids,
        "base_version": manifest.base_version,
        "old_backlog_ref": old_backlog_path,
        "affected_modules": affected,
        "regression_required": regression_required,
        "new_risk_modules": new_risk_modules,
        "incremental_epics": incremental_epics,
        "regression_epics": [],  # 由 LLM 在 S2 阶段读取旧 backlog 后填充
        "block_details": [
            {
                "block_id": b.block_id,
                "block_name": b.block_name,
                "block_type": b.block_type,
                "affected_modules": b.affected_modules,
                "scope": b.scope,
            }
            for b in selected
        ],
    }


def generate_regression_guidance(
    manifest: OptimizationManifest,
    selected_block_ids: list[str],
    old_backlog_path: Optional[str] = None,
) -> dict:
    """
    生成回归测试引导，供 S5/S6 使用。

    读取旧版 backlog.json（如存在），识别哪些 Epic/Story 可能受增量变更影响，
    输出回归 Epic 列表 + 回归测试建议。

    参数:
        manifest: OptimizationManifest
        selected_block_ids: 用户选中的块 ID
        old_backlog_path: 旧版 backlog.json 路径

    返回:
        dict：{
            "regression_epics": [...],       # 需回归的 Epic ID
            "regression_reasons": {...},     # 每个 Epic 的回归原因
            "guidance_text": "...",          # 供 S5/S6 直接引用的文字说明
        }
    """
    selected = [b for b in manifest.blocks if b.block_id in selected_block_ids]

    if not old_backlog_path:
        # 无法读取旧 backlog，提供通用引导
        return {
            "regression_epics": [],
            "regression_reasons": {},
            "guidance_text": (
                "[回归建议] 增量审查模式：无法读取旧版 backlog.json，"
                "建议在 S5/S6 阶段对所有 Epic 产出增量测试用例，"
                "同时参考选中优化块的 affected_modules 推断可能受影响的旧流程。"
            ),
        }

    old_backlog = _try_load_json(old_backlog_path)
    if not old_backlog:
        return {
            "regression_epics": [],
            "regression_reasons": {},
            "guidance_text": (
                "[回归建议] 增量审查模式：旧版 backlog.json 读取失败，"
                "基于关键词匹配推断受影响 Epic。"
            ),
        }

    # 收集选中块的关键词
    keywords = " ".join(b.scope + " " + b.summary for b in selected)

    # 遍历旧 Epic，找可能受影响的
    regression_epics = []
    regression_reasons = {}
    for epic in old_backlog.get("epics", []):
        epic_text = epic.get("title", "") + " " + epic.get("domain", "")
        # 粗略匹配：有相同关键词 → 需回归
        if any(kw in epic_text for kw in [b.scope[:10] for b in selected]):
            regression_epics.append(epic["id"])
            regression_reasons[epic["id"]] = (
                f"Epic[{epic['id']}] 可能受优化块 {', '.join(b.block_id for b in selected)} 影响。"
            )

    guidance_lines = [
        "[回归测试建议 — 增量审查模式]",
        f"选中优化块：{', '.join(b.block_id + ':' + b.block_name for b in selected)}",
        f"推断影响模块：{', '.join(list({m for b in selected for m in b.affected_modules}))}",
        "",
        "需回归的旧 Epic：",
    ]
    if regression_epics:
        for eid in regression_epics:
            guidance_lines.append(f"  - {eid}: {regression_reasons.get(eid, '')}")
    else:
        guidance_lines.append("  （无直接关联 Epic，建议全面回归核心购买/VIP流程）")

    guidance_lines.append("")
    guidance_lines.append("回归策略：")
    guidance_lines.append("  1. 优先回归 regression_epics 中的 Epic（全量用例）")
    guidance_lines.append("  2. 其余 Epic 产出增量用例（仅覆盖变更点）")
    guidance_lines.append("  3. 新旧 Epic 关联映射在 S2 backlog.json 中标注")

    return {
        "regression_epics": regression_epics,
        "regression_reasons": regression_reasons,
        "guidance_text": "\n".join(guidance_lines),
    }


def _try_load_json(path: str) -> Optional[dict]:
    """尝试加载 JSON 文件，失败返回 None。"""
    try:
        from pathlib import Path
        p = Path(path)
        if p.exists():
            import json as _json
            return _json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


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
