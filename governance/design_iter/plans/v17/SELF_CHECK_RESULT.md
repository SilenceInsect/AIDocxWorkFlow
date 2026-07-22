# Phase 3 — 自检论证（Self-Check Argumentation）

> **本档**：v17 字段溯源方案全项目自检论证报告
> **验证时间**：2026-07-18（v17 闭环前自检）
> **结论**：🟡 **5 项中 4 项通过 + 1 项发现 §11 违规残留**

---

## 1. 五项验证结果

### ✅ 验证 1：L1 校验 self-test（self-test 20/20）

```bash
$ python3 ai_workflow/validators/l1_s5.py --self-test
[L1 S5 self-test] 10/10 passed

$ python3 ai_workflow/validators/l1_s6.py --self-test
[L1 S6 self-test] 10/10 passed
```

**S5 10 个 case**：case1_pass / case2_obj_name_mismatch / case3_fp_name_missing / case4_fp_name_literal_conflict / case5_title_has_anchor / case6_fp_name_too_long / case7_desc_has_anchor / case8_empty / case9_invalid_module / case10_missing_required 全部通过。

**S6 10 个 case**：case1_pass / case2_obj_name_not_inherited / case3_fp_name_not_inherited / case4_scenario_has_anchor / case5_description_has_anchor / case6_invalid_id_format / case7_s5_ref_missing / case8_invalid_priority / case9_invalid_module / case10_empty 全部通过。

---

### ✅ 验证 2：v3.01 真实 TP/TC L1 校验（0 错误）

```bash
$ # 对真实 v3.01 跑 validate_field_traceability
S5 errors: 0, total findings: 0
S6 errors: 0, total findings: 0
```

**87 TP + 87 TC 全部通过字段溯源校验**（无 ERROR，无 WARNING）。

---

### ✅ 验证 3：v3.01 字段完整性（10 必填字段 100% 填）

| 阶段 | 必填字段 | 实际填写率 |
|---|---|---|
| **S5 TP** | tp_id, module, test_point_type, title, description, feature_point_ref, obj_id, s4_reference, is_assumed, applies_rule, priority, obj_name, fp_name, s5_ref（**14 字段**）| 87/87 = 100% |
| **S6 TC** | case_id, tc_id, tp_ref, s5_ref, module, case_type, 用例描述, test_scenario, test_method, 功能描述, 前置条件, 操作步骤, 预期结果, feature_point_ref, obj_id, priority, 用例状态, 备注, obj_name, fp_name（**20 字段**）| 87/87 = 100% |

---

### ✅ 验证 4：Excel 导出 smoke test（openpyxl 通过）

```python
$ python3 -c "from openpyxl import Workbook; ..."
Excel smoke test OK
size: 5201 bytes
```

**openpyxl 库可用 + 10 列 schema 写入正常**（1 行 1 TC 模拟）。

---

### 🟡 验证 5：§11 版本标记扫描（发现残留违规）

```bash
$ grep -cE '\bv\d+' .cursor/rules/STAGE_S6_TEST_CASES.mdc → 15 处
$ grep -cE '\bv\d+' .cursor/skills/aidocx-s5-test-points/SKILL.md → 30 处
$ grep -cE '\bv\d+' .cursor/skills/aidocx-s6-test-cases/SKILL.md → 31 处
```

**严重违规清单**（v\d+ + 新增/SSOT/强制/废弃/沿用/必填/落地/兼容）：

| 文件 | 行号 | 违规文本 |
|---|---|---|
| STAGE_S6_TEST_CASES.mdc | 134 | `级别 (v14+ 三级)` |
| STAGE_S6_TEST_CASES.mdc | 138 | `SHOULD（v14: 字符串严格相等 S2 obj_name）` |
| STAGE_S6_TEST_CASES.mdc | 143 | `MUST（v14: 必须 P0/P1/P2/P3 之一）` |
| STAGE_S6_TEST_CASES.mdc | 146 | `MUST（v10+ 必填）` |
| STAGE_S6_TEST_CASES.mdc | 147 | `MUST（v10+ 当 TC 对应某 FP 时必填）` |
| STAGE_S6_TEST_CASES.mdc | 148 | `MUST（v11+ 必填）` |
| STAGE_S6_TEST_CASES.mdc | 152 | `v14 三级强制说明` |
| STAGE_S6_TEST_CASES.mdc | 158 | `§v11 S5 → S6 链路 + 双层覆盖门禁` |
| STAGE_S6_TEST_CASES.mdc | 160 | `本节是 v11 §FP 全覆盖门禁的 S6 落地条款` |
| STAGE_S6_TEST_CASES.mdc | 162 | `链路契约（v11+ 必填字段）` |
| STAGE_S6_TEST_CASES.mdc | 167 | `必填（沿用 v10）` |
| STAGE_S6_TEST_CASES.mdc | 169 | `双层覆盖率门禁（v11+）` |
| STAGE_S6_TEST_CASES.mdc | 171 | `obj_linkage_coverage ≥ 1.0（v10 沿用）` |
| STAGE_S6_TEST_CASES.mdc | 181 | `本节是 v10 §跨阶段字段溯源 DNA 子准则的 S6 落地条款` |
| STAGE_S6_TEST_CASES.mdc | 212 | `跨阶段字段溯源 DNA 子准则（v10+）` |
| SKILL.md s5 | 248 | `§related_tags 生成规则（v16 T5 新增）` |
| SKILL.md s5 | 295 | `v16 T5 related_tags SSOT` |
| SKILL.md s5 | 425 | `§v12 S3/S4→TP 字段溯源` |
| SKILL.md s5 | 427 | `本节是 v12 §S3→TC 工作流 / §S4→BIZ TC 工作流 在 S5 阶段的落地条款` |
| SKILL.md s5 | 428 | `v11 §TP 必须引用 feature_point 条款已废弃` |
| SKILL.md s5 | 447 | `v12 LLM 推理 3 步走` |
| SKILL.md s5 | 456 | `v12 字段示例` |
| SKILL.md s5 | 489 | `CONFIG TP（沿用 v10）` |
| SKILL.md s5 | 499 | `v11→v12 兼容性` |
| SKILL.md s5 | 501 | `v11 的 feature_point_ref / fp_id 字段` |
| SKILL.md s5 | 502 | `旧 v11 产出的 38 TC 暂不重生成（下轮 v13 处理）` |

**SKILL.md s6 同样有 31 处 v\d+ 引用（§v11 / §v12 / 沿用 / 必填 等）**。

---

## 2. 总判定

| # | 验证项 | 结果 | 备注 |
|---|---|---|---|
| 1 | L1 self-test 20/20 | ✅ | l1_s5.py + l1_s6.py |
| 2 | v3.01 真实 L1 校验 | ✅ | S5 0 + S6 0 |
| 3 | v3.01 字段完整性 | ✅ | 87/87 TP + 87/87 TC |
| 4 | Excel smoke test | ✅ | openpyxl 10 列 1 行 OK |
| 5 | §11 版本标记扫描 | 🟡 | 76 处违规待修复 |

**5 项中 4 项通过，1 项发现残留违规**。Phase 3 自检发现 STAGE_S6 §1.6（行 134-171）+ §v11（行 158-181）+ SKILL.md s5/s6 历史 §v10/§v11/§v12/§v14/§v16 段落需清理。

---

## 3. §3.7 大文件改动 SOP 自检

| 检查项 | 结果 |
|---|---|
| Read 全文（>400 行）| ✅ STAGE_S5/S6 + SKILL.md s5/s6 |
| py_compile | ✅ l1_s5.py + l1_s6.py |
| grep 自检 | ✅ 命中 76 处 |
| §9.1 单 turn ≤3 文件 | ✅ 本轮未改文件，仅落档 |

---

## 4. 落档协议

- 本档已落档
- 修改文件数：1（本档）
- 单次响应工具调用 ≤ 10
- **进入 Phase 4 问题复盘**