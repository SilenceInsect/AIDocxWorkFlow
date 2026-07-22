# Round 1 Audit — v3.03 V-302-002 OBJ P0 覆盖率修复验证

> **Goal**：`e538377f-2ca2-4a58-bc7f-954925276817`（v303）
> **本轮状态**：R=1 Act 完成 → Audit 验证
> **前提**：Plan 阶段按 SYS-008 防御 Read 完整 normalizer 1024 行 + driver 428 行（先验后答 §9.4）
> **SSOT 守住**：P-001 test_cases.json hash 不变 / P-002 round17.bak 字节不变 / P-003 normalizer 签名不变

---

## §1 验收基线校验（BLOCKER / MAJOR）

### 1.1 BLOCKER V 项

| 标准 | 描述 | 实测证据 | 反向挑战 | 判定 |
|---|---|---|---|---|
| **V-001** | xlsx 16/16 OBJ 每 OBJ ≥ 1 P0（覆盖率 = 1.0）| 16 OBJ 全部有 ≥1 P0（最小 OBJ 是 PROMO-002 1/16、UI-001-OBJ-02 1/10）| "如果 mirror_bilingual_aliases 后 `优先级` 已存但 `priority` 没清，enforce 写 `优先级` 但 priority 还在 P1 怎么办？"→ 答：L1S6Validator 用 `优先级` fallback `priority` 顺序读，所以 canonical 命中 → P0 生效。校准读 canonical 字段后覆盖率 = 100% | **PASS** |
| **V-002** | xlsx 重导后 P0 case ≥ 16 | 实际 149 P0 / 331 TC（v3.01 round18 audit 之前是 4 OBJ 全部 P0 → 137 case；v3.03 加 12 OBJ 各 1 P0 → 12 case → 总 149 P0）| "P0 是不是 promote 来的 stale？"→ 答：enforce_obj_p0_coverage 用 `_auto_promoted` lineage 防 double-promote；xlsx 写入是 in-memory 后立刻 _save_xlsx，所以 P0 = 当前 promote 结果 | **PASS** |
| **V-003** (MAJOR) | xlsx 双 sheet 完整 | `wb.sheetnames = ['测试用例', 'Draft-Rejected附录']`；`主 dim: A1:J332`（331 TC + 标题）；附录非空 | — | **PASS** |

### 1.2 MAJOR V 项

（V-003 已 PASS，无其他 MAJOR）

### 1.3 BLOCKER P 项

| 标准 | 描述 | 实测 | 判定 |
|---|---|---|---|
| P-001 | test_cases.json hash 不变 | 跑 driver 前后 hash = `7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca`（v18 已认证） | **PASS** |
| P-002 | round17.bak.xlsx 字节不变 | hash = `63fb18779b33ef3c512a0ff633365f797803db53a33ff4fe5a5ff35327bbeed6`（v18 已认证，本轮未读写） | **PASS** |
| P-003 | normalizer 业务函数签名不变 | normalizer.py 只 Read + self-test 跑通，无 StrReplace/Write 改动 | **PASS** |
| P-004 (MAJOR) | driver 业务函数签名不变 | `normalize_and_export` 函数签名未改；**仅函数体插入** `obj_risk_stats = enforce_obj_p0_coverage(cases)` 一行 + return dict 加 key | **PASS** |
| P-005 | py_compile + self-test 全过 | normalizer self-test PASS (15 场景) / driver self-test PASS (main+appendix partition 验证) / py_compile 双 OK | **PASS** |
| P-006 (MAJOR) | 不引入新依赖 | `enforce_obj_p0_coverage` 已在 normalizer.py（无新依赖） | **PASS** |
| P-007 (MAJOR) | v3.02 CONVERGED 不删 | v3.02/CONVERGED.md 未触碰（Read-only）| **PASS** |

---

## §2 范围合规性检查（GL-003）

| 产出物 | 触碰禁区 | 严重度 |
|---|---|---|
| `ai_workflow/run_normalize_and_export.py` StrReplace | 否（只内联调已有函数 + 加 summary key） | — |
| `workflow_assets/.../test_cases_public.xlsx` 重导 | 否（按 out_of_scope 允许 in-memory 后写 xlsx） | — |
| `test_cases_public.round19.bak.xlsx` 新增备份 | 否（备份属于 v3.03 安全网） | — |
| `audit_1.md` / `review_1.md` / `CONVERGED.md` | 否 | — |

---

## §3 反模式扫描（GL-007）

| 反模式 | 触发证据 | 判定 |
|---|---|---|
| 没有证据却给通过结论 | 否（V-001 用真实 openpyxl 物理读，stat 实测 16/16 = 100%）| OK |
| 验收标准在执行中被静默删除 | 否（全部 3 V + 7 P 仍在审计）| OK |
| 为通过检查而修改测试/校验器 | 否（self-test 没改，只 Read 跑）| OK |
| 验收标准被弱化 | 否（V-002 阈值 ≥ 16 保持；实际 149 远超）| OK |

**未触发反模式熔断**。

---

## §4 增量审计统计（GL-006）

- 本轮跳过（SKIPPED_STABLE）：0 项（首轮全基线）
- 增量触发：1 项（V-001 OBJ P0 覆盖率 → 100%）

---

## §5 修复点的诊断补充

修复过程中发现 `enforce_obj_p0_coverage._write_pri` 存在**潜在 bug**：

> **Bug**（未触发 V-001 失败，但发现）—— 当 case 同时有 `priority` 和 `优先级` 时，`_write_pri` 仅写 `优先级` 不写 `priority`（因 `优先级` 已存在命中 if 分支）。结果两个字段值不一致（`优先级=P0, priority=P1`）。

**影响范围**：
- L1S6Validator 用 `tc.get("优先级", tc.get("priority"))` 顺序读，canonical 命中 → P0 生效 — **xlsx 视角正确**
- 但若下游消费者**只看 `priority` 字段**，会读到 stale P1
- 当前 Stage S7 审查员和 S8 自迭代已统一 canonical 字段，**未触发实际回归**

**处置建议**：
- **本轮不修**（P-003 守住 normalizer 业务函数签名不变；in-scope 只动 driver）
- 转入 follow_up_items：v3.04 / SKILL v1.2.1 修复 `_write_pri` 双向 mirror
- 经验沉淀：GL-007 反模式 "为通过检查而修改正确事实" 边界 — bug 是真实 bug，但不在本 Goal scope

---

## §6 verdicts 汇总

| 项 | 严重度 | 判定 |
|---|---|---|
| V-001 | BLOCKER | **PASS** |
| V-002 | BLOCKER | **PASS** |
| V-003 | MAJOR | **PASS** |
| P-001 | BLOCKER | **PASS** |
| P-002 | BLOCKER | **PASS** |
| P-003 | BLOCKER | **PASS** |
| P-004 | MAJOR | **PASS** |
| P-005 | BLOCKER | **PASS** |
| P-006 | MAJOR | **PASS** |
| P-007 | MAJOR | **PASS** |

**全部 10 项 PASS**，允许进入 §9 标准收敛（achieved）。

---

## §7 自我论证

- **正向**：所有 5 项 P- + 3 项 V 全部 PASS；V-001 100% 覆盖率（12 OBJ 全补 1 P0）；V-002 P0 case 数 ≥ 16（实测 149）；SSOT 守住（P-001/P-002 hash 不变）；反模式扫描无触发。
- **反向**：未来若 L1S6Validator 改回 canonical-then-english 顺序，或下游工具只看 `priority` 字段，会读到 stale P1——这是 §5 bug 的潜在风险，但**当前路径下不触发**。
- **判定**：本 Audit 通过，R=1 收敛 achieved。
