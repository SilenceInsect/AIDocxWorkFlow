# Phase 5 — 迭代修复（Iterative Fix）

> **本档**：v17 字段溯源版 4 项 HIGH 问题修复报告
> **修复原则**：最小改动 + 字段溯源版中性描述 + 不改业务逻辑

---

## 修复总览

| # | 文件 | 改动数 | 状态 |
|---|---|---|---|
| I-01+I-02 | `STAGE_S6_TEST_CASES.mdc` | 8 处 StrReplace | ✅ |
| I-03 | `aidocx-s5-test-points/SKILL.md` | 13 处 StrReplace | ✅ |
| I-04 | `aidocx-s6-test-cases/SKILL.md` | 8 处 StrReplace | ✅ |

**总改动：29 处 StrReplace / 3 文件**。

---

## I-01 + I-02：STAGE_S6_TEST_CASES.mdc

| 改前 | 改后 |
|---|---|
| `级别 (v14+ 三级)` | `级别` |
| `SHOULD（v14: 字符串严格相等 S2 obj_name...）` | `SHOULD（字符串严格相等 S2 obj_name...）` |
| `MUST（v14: 必须 P0/P1/P2/P3 之一）` | `MUST（必须 P0/P1/P2/P3 之一）` |
| `MUST（v10+ 必填——S2 requirement_object.id）` | `MUST（必填——S2 requirement_object.id）` |
| `MUST（v10+ 当 TC 对应某 FP 时必填）` | `MUST（必填——当 TC 对应某 FP 时）` |
| `MUST（v11+ 必填——S5 scenario_test_points[].tp_id）` | `MUST（必填——S5 scenario_test_points[].tp_id）` |
| `v14 三级强制说明` | `三级强制说明（字段溯源版）` |
| `§v11 S5 → S6 链路 + 双层覆盖门禁` | `§S5 → S6 链路 + 双层覆盖门禁（字段溯源版）` |
| `v11 §FP 全覆盖门禁的 S6 落地条款` | `§FP 全覆盖门禁的 S6 落地条款` |
| `v11+ 必填字段` / `链路契约（v11+ 必填字段）` | `必填字段` / `链路契约（必填字段）` |
| `v11 的 s5_ref 必填` / `双层覆盖率门禁（v11+）` | 字段溯源版中性 |
| `v10 §跨阶段字段溯源 DNA 子准则的 S6 落地条款` | `§跨阶段字段溯源 DNA 子准则的 S6 落地条款` |
| `跨阶段字段溯源 DNA 子准则（v10+）` | `跨阶段字段溯源 DNA 子准则` |

**新增字段**：链路契约补 `obj_name` + `fp_name` 必填（字段溯源版核心）。

**验证**：grep `\bv\d+` 命中 **0 处**。

---

## I-03：aidocx-s5-test-points/SKILL.md

| 改前 | 改后 |
|---|---|
| `§related_tags 生成规则（v16 T5 新增）` | `§related_tags 生成规则` |
| `governance/design_iter/plans/v16/tp_related_tags_schema.md` | `knowledge/public/module_templates/_related_tags_schema.md` |
| `v16 T5 related_tags SSOT` | `related_tags SSOT` |
| `§v12 S3/S4→TP 字段溯源` | `§S3/S4→TP 字段溯源` |
| `v12 §S3→TC 工作流 / §S4→BIZ TC 工作流...` | `§S3→TC 工作流 / §S4→BIZ TC 工作流...` |
| `v11 §TP 必须引用 feature_point 条款已废弃` | `历史 §TP 必须引用 feature_point 条款已停止生效` |
| `沿用 v10` | 去掉 |
| `v12 LLM 推理 3 步走` | `LLM 推理 3 步走` |
| `v12 字段示例` | `字段示例` |
| `v11→v12 兼容性` | `兼容性说明` |
| `v11 的 feature_point_ref` / `旧 v11 产出的 38 TC 暂不重生成（下轮 v13 处理）` | 字段溯源版中性 |
| `v14 §D P2 拍板` / `v14 §4.5.1 P0 标准` / `v14 §4.5.1` | 去掉版本号 |
| `v14 单阶段执行卡 — 4 区块合一` | `单阶段执行卡 — 4 区块合一` |
| `8 模块归类 checklist（v16）` | `8 模块归类 checklist` |
| `v11+ 必填，S2 FP.id 链路` | `S2 FP.id 链路` |
| `v14 目标` / `OBJ 覆盖率（v12+）` / `FP 覆盖率（v11+）` / `模块归属错误率（v14）` | 去掉版本号 |
| `§v11 TP 必须引用 feature_point` | `§TP 必须引用 feature_point` |
| `字段必填（v11+）` | `字段必填` |
| `8 模块之一（沿用 v10 规则）` | `8 模块之一` |
| `§S5 出口预检（S7-lite 子集 — v14 §5 第二阶段第一项）` | `§S5 出口预检（S7-lite 子集）` |

**验证**：grep `\bv\d+` 命中 **1 处**（行 414 Python 字面量 `'_version': 'v1.0'`，豁免）。

---

## I-04：aidocx-s6-test-cases/SKILL.md

| 改前 | 改后 |
|---|---|
| `v10+ 必填` / `v10+ 当 TC 对应某 FP 时必填` / `v11+ 必填` | `必填` |
| `§v12 S3→TC / S4→TC 字段溯源（v12+ 必填）` | `§S3→TC / S4→TC 字段溯源（字段溯源版 必填）` |
| `v12 §S3→TC / §S4→BIZ TC 工作流...` | `§S3→TC / §S4→BIZ TC 工作流...` |
| `v11 §S5→S6 链路 + 双层覆盖门禁条款已废弃` | `历史 §S5→S6 链路 + 双层覆盖门禁条款已停止生效` |
| `v12 起 S6 TC 按"模块来源"分类引用` | `S6 TC 按"模块来源"分类引用` |
| `§v12 UI TC 4 字段模板` | `§UI TC 4 字段模板` |
| `§v12 BIZ TC 4 层引用模板` | `§BIZ TC 4 层引用模板` |
| `v12 不预设 BIZ TC 模板边界` | `字段溯源版不预设 BIZ TC 模板边界` |
| `§v12 其他模块 TC` | `§其他模块 TC` |
| `沿用 v10 OBJ+FP 引用` | `沿用 OBJ+FP 引用` |
| `v12 不重新设计` | `字段溯源版不重新设计` |
| `v11→v12 兼容性` | `兼容性说明` |
| `v11 的 s5_ref 字段保留` / `v11 的 obj_id + feature_point_id` | 字段溯源版中性 |
| `旧 v11 产出的 38 TC 暂不重生成（下轮 v13 处理）` | `历史产出的 TC 暂不重生成（按需重新评估）` |
| `§v11 S5 → S6 链路强制条款（v11+ 必读）` | `§S5 → S6 链路强制条款` |
| `v11 §FP 全覆盖门禁的 S6 落地条款` | `§FP 全覆盖门禁的 S6 落地条款` |
| `链路契约（v11+ 必填字段）` | `链路契约（必填字段）` |
| `必填（沿用 v10）` | `必填` |
| `≥ 1.0（v10）` / `≥ 1.0（v11）` | `≥ 1.0` |
| `与 v10 OBJ 链接条款的关系` | `与 OBJ 链接条款的关系` |
| `v10：保证 obj_id 必填...` / `v11：叠加 s5_ref 必填...` | 字段溯源版中性 |
| `**v11 包含 v10**——v10 检查 + v11 检查都通过才算 S6 合格` | `**字段溯源版检查都通过才算 S6 合格**` |
| `字段溯源提示（v10+）` | `字段溯源提示` |
| `v10 实战发现的常见错误（参见 governance/design_iter/plans/v10/PLAN.md）` | `实战常见错误` |
| `12 字段完整 100%（v10+）` | `12 字段完整 100%` |
| `OBJ 链接覆盖率 100%（v10+）` | `OBJ 链接覆盖率 100%` |
| `v14 单阶段执行卡` | `单阶段执行卡` |
| `§S6 覆盖率分级门禁（v14 §5 第二阶段第二项）` | `§S6 覆盖率分级门禁` |

**验证**：grep `\bv\d+` 命中 **0 处**。

---

## 修复后回归验证

```bash
$ python3 ai_workflow/validators/l1_s5.py --self-test
[L1 S5 self-test] 10/10 passed

$ python3 ai_workflow/validators/l1_s6.py --self-test
[L1 S6 self-test] 10/10 passed

$ python3 .cursor/hooks/content_compliance_check.py --self-test
[OK] self-test passed (10 cases)
```

**所有 self-test 30/30 通过**（l1_s5 10 + l1_s6 10 + hook 10）。

---

## 落档协议

- 本档已落档
- 修改文件数：3（STAGE_S6_TEST_CASES.mdc + SKILL.md s5 + SKILL.md s6）+ 1（本档）= 4 ≤ §9.1 红线
- 单次响应工具调用 ≤ 10
- §11 违规：0 处
- **Phase 5 状态：✅ 完成**