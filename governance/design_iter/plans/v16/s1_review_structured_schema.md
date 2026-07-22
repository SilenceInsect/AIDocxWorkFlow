# v16 T4 — S1 结构化评审包 Schema 定义

> **版本**: v16 T4（2026-07-17）
> **来源**: `governance/design_iter/plans/v16/PLAN.md` §2.4 + `详细执行方案.md` T4
> **核心变更**: S1 评审新增 `review_structured.json` 6 字段结构化产出物；S1.5 引用；S2 消费 4 类字段
> **SSOT**: 本文件是 6 字段结构的唯一权威定义；SKILL.md / REVIEW.mdc 通过引用本文件同步

---

## §0 职责边界（C1 解决）

| 阶段 | 职责 | 产出物 |
|------|------|--------|
| **S1** | **识别问题**（5 维度评分 + 结构化洞察） | `review_report.md` + **`review_structured.json`**（新增）|
| **S1.5** | **回答问题 + 准出**（人工审核 + exit_permission） | `exit_permission.json`（5 字段，已存在）|
| **S2** | **消费结构化包**（边界/假设/风险/缺失注入 OBJ/Story） | `requirement_objects.json`（新增 4 类字段）|

---

## §1 review_structured.json 完整 Schema

### 顶层结构（6 字段）

```json
{
  "meta": {
    "req_name": "string 项目名",
    "version": "string 版本号（如 v1.0）",
    "stage": "string 固定值 \"S1\"",
    "s1_verdict": "enum PASS | NEEDS_REVISION | REJECT",
    "total_score": "number 0-10",
    "created_at": "ISO 8601 timestamp",
    "created_by": "string 'AIDocxWorkFlow'"
  },
  "requirement_quality": { ... },
  "confirmed_boundaries": [ ... ],
  "explicit_assumptions": [ ... ],
  "risk_points_preview": [ ... ],
  "missing_scenarios": [ ... ],
  "final_requirement_text": "string"
}
```

### 1.1 `requirement_quality`

```json
{
  "total_score": "number 0-10（与 meta.total_score 同步）",
  "dimension_scores": {
    "completeness": "number 0-10（权重 25%）",
    "clarity": "number 0-10（权重 25%）",
    "consistency": "number 0-10（权重 20%）",
    "testability": "number 0-10（权重 20%）",
    "feasibility": "number 0-10（权重 10%）"
  }
}
```

> S1.5 消费：≥ 7.0 → PASS / 4.0-6.9 → NEEDS_REVISION / < 4.0 → REJECT

### 1.2 `confirmed_boundaries`

需求文档**已明确**的边界条件。

```json
[
  {
    "id": "string CB-XXX（从 CB-001 起，可选填）",
    "object": "string 业务对象名（如 '商城订单'）",
    "scope": "string 边界描述（如 '单笔订单购买上限 99 件/天'）",
    "source": "string 来源（需求文档章节定位）"
  }
]
```

> S2 消费：每条边界注入对应 OBJ 的 `boundary_definition` 字段

### 1.3 `explicit_assumptions`

LLM **主动识别**的假设（需求未写但 LLM 必须假设才能继续）。

```json
[
  {
    "id": "string ASM-XXX（必须，XXX = 3 位序号，从 ASM-001 起）",
    "content": "string 假设内容（≤ 80 字）",
    "confidence": "enum high | medium | low",
    "category": "string 分类（业务逻辑推断 | 行业常识 | 技术约束 | 其他）"
  }
]
```

> S2 消费：Story 前置条件自动继承，带 `is_assumed: true` + `assumption_reason` 字段

### 1.4 `risk_points_preview`

LLM 识别的潜在风险点（S4 异常树种子）。

```json
[
  {
    "id": "string R-XXX（S4 生成异常树时自行编号，可选填）",
    "area": "string 风险领域（如 '支付安全' / '并发性能'）",
    "risk_level": "enum high | medium | low",
    "reason": "string 风险原因（≤ 100 字）"
  }
]
```

> S2 消费：`backlog.json#summary.risk_seeds` 字段透传到 S4

### 1.5 `missing_scenarios`

需求文档**缺失**的关键场景。

```json
[
  {
    "id": "string MSC-XXX（必须，XXX = 3 位序号，从 MSC-001 起）",
    "scenario": "string 缺失场景描述",
    "status": "enum need_clarification | assumed",
    "impact": "enum high | medium | low"
  }
]
```

> S2 消费：`need_clarification` → S1.5 必须答疑；`assumed` → 自动 is_assumed

### 1.6 `final_requirement_text`

LLM 整理后的终版需求全文（Markdown 格式，标注 `[需澄清]` 前缀）。

---

## §2 填写率检查与 fallback 机制

### 2.1 字段填写率检查

6 字段填写率 ≥ 90%（除合理 is_assumed / need_clarification）。未达标 → 触发补全 prompt。

### 2.2 fallback 机制

LLM 因 prompt 截断未填全时：

| 场景 | Fallback |
|------|---------|
| 填了 4-5 个字段 | 缺失字段用 `null` + `"_fallback_note": "字段因 prompt 截断未填写"` |
| 完全未生成 | **不允许** — 必须生成（即使内容为空）|
| S2 读到缺失字段 | 静默跳过（warning 日志）|

---

## §3 S2 消费逻辑（伪代码）

```python
structured = load_json("review_structured.json")

# 1. confirmed_boundaries → OBJ 边界注入
for b in structured.get("confirmed_boundaries", []):
    obj = find_obj(b["object"])
    if obj:
        obj["boundary_definition"] = b["scope"]

# 2. explicit_assumptions → Story 前置条件
for a in structured.get("explicit_assumptions", []):
    story.precondition.append({
        "text": a["content"],
        "is_assumed": True,
        "assumption_reason": a["category"],
        "source": f"S1.{a['id']}"
    })

# 3. risk_points_preview → risk_seeds
summary["risk_seeds"] = [
    {"area": r["area"], "level": r["risk_level"], "reason": r["reason"]}
    for r in structured.get("risk_points_preview", [])
]

# 4. missing_scenarios → S1.5 答疑 or 自动 assumed
need_cla = [m for m in structured.get("missing_scenarios", []) if m["status"] == "need_clarification"]
if need_cla:
    log_warning(f"S1 留下 {len(need_cla)} 个待澄清项，需 S1.5 已处理")
```

---

## §4 版本与维护

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-17 | v16 T4 首次落地（6 字段 Schema + fallback + S2 消费逻辑）|

**修改原则**：改 6 字段 Schema 必须先改本文件，再同步 `STAGE_S1_REVIEW.mdc §1.5.4` 与 SKILL.md。
