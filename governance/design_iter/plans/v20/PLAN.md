# v20 — v3.02 Round 1 PLAN

> **Goal ID**：`4c1eedec-14d9-4de0-8d7c-51b21713b0c2`
> **Goal 名**：v3.02 跟进清单（基于 v3.01 Round 18 审查的 8 项问题）
> **Round**：1 / final
> **创建日期**：2026-07-19
> **闭环日期**：2026-07-19

---

## 1. 背景

v3.01 Round 18 二次重导后审查（`governance/design_iter/plans/v18/round18_audit_round18.md`）发现 8 项问题，其中 5 项 V-001~V-005 为 BLOCKER/MAJOR 业务成效，5 项 P-001~P-005 为 BLOCKER/MAJOR 过程约束。

本轮执行 T-001~T-005：

| Task | 内容 | 阶段 | 状态 |
|---|---|---|---|
| T-001 | V-003 expected_results 去重保序 | scenario_group_merger | 已落地 (Round 19) |
| T-002 | V-004 B 列合并诊断（已知 PASS） | test_case_formatter | 已落地 (Round 18) |
| T-003 | V-001 ID 重排连续编号 | case_id_and_field_normalizer | 已落地 |
| T-004 | V-002 OBJ 风险矩阵 | case_id_and_field_normalizer | 已落地 + driver 集成修复 (Round 20) |
| T-005 | V-005 + 全套验证 + 视觉 PNG + v20 治理档 | run_round15_merge_export + verify_xlsx_physical + render_v302_visual + 本文件 | **本轮 final** |

---

## 2. DT 决策清单

### DT-V302-001: V-004 诊断 → OpenPyXL 合并填充语义非 bug

- **触发**: Round 18 审查质疑 OBJ-02 块 row 27/28 B 列"看似 None"的合并现象
- **判定**: OpenPyXL 在 merged range 内的非 top-left cell 返回 None（这是标准库行为，非数据缺失）
- **依据**: Round 18 物理读 B27='BIZ-TC-026', B28='BIZ-TC-027' (top-left cell)
- **状态**: PASS — V-004 不需要 patch, 验证脚本须显式读 top-left

### DT-V302-002: V-002 enforce_obj_p0_coverage → Draft status 正交处理

- **触发**: OBJ 风险矩阵要求 16/16 OBJ 至少 1 P0
- **冲突**: enforce 写 `priority='P0'` 与 evaluate_status 写 `用例状态='Draft'`（如果 L1/L2 FAIL）正交
- **判定**: priority 与 status 是两个独立维度, enforce 不感知 status, evaluate 不感知 priority
- **依据**: case_id_and_field_normalizer.py:enforce_obj_p0_coverage 只读 obj_id + priority, 不读 status
- **状态**: PASS — T-004 改写后 (优先 promote first case 不论 status), 16/16 OBJ P0 覆盖

### DT-V302-003: V-001 renumber_cases_per_module 内存重排 + apply=False 默认（保护 P-001）

- **触发**: V-001 BLOCKER 要求 case_id 每模块内连续
- **风险**: 直接持久化会破坏 test_cases.json 字节 (P-001 BLOCKER)
- **判定**: 默认 `apply=False` (pure 内存重排), driver `apply_renumber=True` (写到 xlsx), JSON 文件不动
- **依据**: case_id_and_field_normalizer.py:renumber_cases_per_module 函数签名 `apply: bool = False`
- **状态**: PASS — xlsx 体现连续编号 (BIZ-1..64, UI-1..19, LOG-1, SPECIAL-1..3), JSON 字节 7d6359f8... 不变

### DT-V302-004: V-003 _merge_expected 保序去重

- **触发**: Round 18 H 列字面重复 72/87 TC, V-003 BLOCKER
- **方案**: scenario_group_merger._merge_expected 用 `list(dict.fromkeys())` 模式保序去重
- **依据**: scenario_group_merger.py:_merge_expected L116-126
- **状态**: PASS — H 列字面重复 = 0, 87 H cell 全部 unique, multi-line 单 TC 81/87 (merged scenario 内部)

---

## 3. v20 产物清单

| 文件 | 用途 |
|---|---|
| `governance/design_iter/plans/v20/PLAN.md` | 本文件 |
| `governance/design_iter/plans/v20/audit_round1.md` | V/P 全套证据 + OpenPyXL 物理读详细输出 |
| `governance/design_iter/plans/v20/review_round1.md` | 复盘 + 触发的反模式 |
| `governance/design_iter/plans/v20/CONVERGED.md` | 闭环判决 |
| `governance/design_iter/plans/v20/audit_evidence_obj_blocks.json` | 16 OBJ 块结构化证据 |
| `governance/design_iter/plans/v20/q_decision_table_v302.md` | DT-V302-001~004 完整记录 |
| `ai_workflow/verify_xlsx_physical.py` | OpenPyXL 物理验证脚本 |
| `ai_workflow/render_v302_visual.py` | 视觉 PNG 渲染脚本 |
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.v302.visual.png` | 视觉确认 PNG |

---

## 4. 修复 / 新增 / 遗留

### 4.1 解决 (Resolved)

| ID | 描述 | 状态 |
|---|---|---|
| V-001 | case_id 连续编号 | PASS |
| V-002 | 16/16 OBJ P0 覆盖 | PASS |
| V-003 | H 列字面重复 = 0 | PASS |
| V-004 | B 列 row 27/28 物理读 | PASS |
| V-005 | 88 行 × 11 列重导 | PASS |
| P-001 | test_cases.json hash 不变 | PASS |
| P-004 | py_compile + self-test 全过 | PASS |
| P-005 | v18 治理档不删不改 | PASS |

### 4.2 新增 (Added)

| ID | 描述 |
|---|---|
| DT-V302-005 | T-004 集成 bug 修复: driver 必须用 `normalize_payload` 调用 enforce_obj_p0_coverage |
| DT-V302-006 | P-002 保护: driver 增加 `AIDOCX_ROUND15_XLSX_BACKUP` 环境变量, 默认不覆盖 round17.bak.xlsx |
| DT-V302-007 | run_round15_merge_export 自测修复: 应用 apply_renumber=False 避免 T-003 重排干扰测试 fixture |

### 4.3 遗留 (Follow-up)

| ID | 描述 | 影响 |
|---|---|---|
| F-001 | P-002 partial: round17.bak.xlsx 当前 hash = 63fb18779... 与 Round 18 审计记录的 dc2fa66d... 不一致; driver 在 T-005 第一次重导时 overwrite 了. 后续轮次已加 env var 保护 | audit 锚点漂移, 但 v20 自带 archive_round1/round17_bak.preround1.xlsx 副本 |
| F-002 | T-005 第一次执行 verify_xlsx_physical 时未带 V-002 fix driver 路径, 直接发现 V-002 FAIL; 修复 driver 后 PASS | 已在本轮闭环 |

---

## 5. 闭环判决

`converged_with_followup` — V-001~V-005 + P-001/P-003/P-004/P-005 全 PASS, P-002 PARTIAL (driver 行为 vs spec 冲突, 需后续 DT 修复 round17.bak 备份机制, 不阻塞本轮产物)

详见 `CONVERGED.md`。
