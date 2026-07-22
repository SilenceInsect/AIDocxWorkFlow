# 子任务 2.1 — STAGE_S5 §1.9 改写状态确认

> **本档**：确认 STAGE_S5_TEST_POINTS.mdc §1.9 当前已为"字段溯源版"，无需再改
> **对应治理档**：v17/PLAN.md §2.1 必改约束文件（5 处）
> **v17 阶段定位**：Phase 2 子任务 2.1 — 状态确认（非改动）

---

## 1. 现状摘要

| 项 | 值 |
|---|---|
| 文件 | `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` |
| 章节 | §1.9 命名一致性 & 产出标准化门禁（字段溯源版） |
| 当前状态 | **已是字段溯源版**（v17 字段方案要求） |
| 改写必要性 | ❌ 不需要再改 |
| 标题版本标记 | ❌ 无（标题写"字段溯源版"，不带 v17） |
| §11 违规数 | 0 |

---

## 2. 已落实的字段溯源规范（§1.9.1-§1.9.7）

### §1.9.1 核心规范（line 38-54）

- `obj_name` 字段必须存在，100% 原样写入 S2 `requirement_objects[].obj_name`
- `fp_name` LLM 自创中性功能名（命名规则：含动词 + 长度 ≤ 20 字符 + 不与 S2 `fp_desc` 字面量重复）
- `title` 纯场景简短标题（不带锚点）
- `description` 纯测试逻辑（不带锚点）

### §1.9.2 校验方式（line 56-69）

- L1 校验项：`field_traceability`
- 校验通过率硬门禁：100%

### §1.9.4 命名来源约束（line 76-81）

- `obj_name` 唯一来源 = S2 `requirement_objects.json` 的 `obj_name` 字段（100% 逐字相等）
- `fp_name` 唯一来源 = LLM 自创（含动词 + ≤ 20 字符 + 不与 S2 `fp_desc` 重复）

### §1.9.5 标准格式（line 83-94）

```
title: {4-12字场景摘要}（不带锚点）
description: {完整测试逻辑，前置+步骤+预期}（不带锚点）
```

### §1.9.6 L1 校验函数（line 96-108）

- 函数：`L1S5Validator.validate_field_traceability()`
- 无版本号后缀（已合规）

### §1.9.7 产出 Schema（line 110-130）

```json
{
  "tp_id": "TP-001",
  "s5_ref": "TP-001",
  "module": "UI",
  "obj_id": "UI-ITEM-MALL-01-002-OBJ-01",
  "obj_name": "商城首页道具列表",
  "feature_point_ref": "UI-ITEM-MALL-01-002-OBJ-01-FP-2",
  "fp_name": "首页销量排序展示",
  ...
}
```

---

## 3. §11 违规扫描结果

```
$ grep -E "\b(v\d+(?:\.\d+)?)\s+(v\d+(?:\.\d+)?)\b" STAGE_S5_TEST_POINTS.mdc
（无输出）

$ grep -E "\b(v\d+(?:\.\d+)?)\s*(\+?\s*(?:新增|SSOT|强制))(规则)?" STAGE_S5_TEST_POINTS.mdc
（无输出）

$ grep "v\d+" STAGE_S5_TEST_POINTS.mdc
607:breakdown = {'epics': [...], '_version': 'v1.0'}  ← Python 数据字面量（豁免）
```

---

## 4. 上一轮违规修复回顾（v17_phase2_self_violation_postmortem_20260718）

| 维度 | 数据 |
|---|---|
| 违规类型 | `PERMANENT_RULE_VERSION_TAG`（HIGH severity） |
| 违规总数 | 14 处（1 处初始重写 + 13 处批量 StrReplace 修复） |
| 当前残留 | 0 处（仅 Python 字面量 v1.0，属豁免） |
| 修复时间 | 2026-07-18 |

---

## 5. 子任务 2.1 判定

| 检查项 | 状态 |
|---|---|
| §1.9 是否已为字段溯源版 | ✅ 是 |
| 标题是否含版本号 | ❌ 否 |
| §11 违规数 | 0 |
| L1 校验函数名是否含版本号 | ❌ 否 |
| 产出 Schema 是否含字段溯源字段 | ✅ 是（obj_name/fp_name/feature_point_ref） |

**结论**：STAGE_S5 §1.9 已是字段溯源版，无需再改。**本子任务直接完成**。

---

## 6. 落档协议

- 本档已落档到 `governance/design_iter/plans/v17/deliverables/2_1_stage_s5_section_19_status.md`
- 修改文件：1（本档）
- 单次响应工具调用：≤ 10
- v17 §1.9 改写状态：✅ 已合规（无需再改）