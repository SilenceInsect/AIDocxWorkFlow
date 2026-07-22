# Round 1 复盘与触发的反模式

> **Goal ID**：`4c1eedec-14d9-4de0-8d7c-51b21713b0c2`
> **Round**：1 / final
> **复盘日期**：2026-07-19

---

## 1. 执行复盘

### 1.1 触发顺序

1. **T-001~T-004 (Round 19)**: 已知 patch 已落地, 4 个 V-001~V-004 修复 (T-001: V-003 scenario_group_merger 去重 / T-003: V-001 renumber_cases_per_module / T-004: V-002 enforce_obj_p0_coverage / T-002: V-004 已知 PASS)
2. **T-005 启动**: 重导 + 物理验证 + 视觉 PNG + 治理档
3. **T-005.1**: py_compile + self-test 全过 — **但发现一个 stale self-test bug**
   - run_round15_merge_export.py:self_test 因 T-003 默认 apply_renumber=True 导致 fixture 失效
   - 修复: 加 `apply_renumber=False` 到 self-test 调用 (1 行改动, 不影响生产路径)
4. **T-005.2**: 第一次 verify_xlsx_physical 物理读
   - **重大发现**: V-002 FAIL — 12/16 OBJ 零 P0
   - **根因诊断**: T-004 patch 加在 `case_id_and_field_normalizer.py:normalize_payload` 内, 但 `run_round15_merge_export.py:merge_and_export` 没调用 `normalize_payload`, 而是手动循环调 `normalize_case_id` + `mirror_bilingual_aliases`, **绕过了 enforce_obj_p0_coverage**
5. **T-005 driver 集成修复**: 把 driver Step 1 改为 `normalize_payload` 一行调用 — 直接走"原子"路径
6. **T-005 第二次 verify**: V-001~V-005 + P-001/P-005 全 PASS, P-002 PARTIAL
7. **P-002 缓解**: driver main() 增加 `AIDOCX_ROUND15_XLSX_BACKUP` env var, 默认 = 0 (不覆盖 round17.bak.xlsx); 当前的 round17.bak.xlsx 已 archive 到 `archive_round1/round17_bak.preround1.xlsx`
8. **T-005.4**: 生成视觉 PNG (1.6MB)
9. **T-005.5**: 写 5 份治理档 (PLAN + audit + review + CONVERGED + DT)

### 1.2 关键决策

| 决策 | 选择 | 依据 |
|---|---|---|
| T-001~T-004 patch 复用 | 不重新发明 | 用户硬约束 + DNA §3 反模式"只补局部闭环不审全局一致性" |
| run_round15_merge_export 自测修复 | 加 `apply_renumber=False` 参数 | 测试 fixture 本意是 merge+xlsx 验证, 非 renumber 验证 |
| T-004 driver 集成 bug 修复 | 改用 `normalize_payload` 一行调用 | 避免再分裂"原语 vs 高阶"两套路径, 减少未来 drift |
| P-002 缓解 | env var 控制 backup 行为 | 不改 driver 默认 (保护其他调用者), 提供 escape hatch |
| 治理档放置 | `governance/design_iter/plans/v20/` | 与 v17/v18 一致 |

### 1.3 时间分配 (粗估)

- T-005.1: 20% (compile + self-test + bug fix)
- T-005.2: 30% (verify + V-002 driver 集成修复)
- T-005.3: 5% (P-001~P-005 校验)
- T-005.4: 10% (PNG render)
- T-005.5: 25% (5 份治理档)
- T-005.6: 10% (snapshot 更新)

---

## 2. 触发的反模式 / 教训

### 2.1 ❌ Round 18 patch 集成未验证 (教训 1)

**症状**: T-004 `enforce_obj_p0_coverage` patch 加在 `normalize_payload` 内, 但 driver `run_round15_merge_export.py` 没调用 `normalize_payload` — 直接调 `normalize_case_id` + `mirror_bilingual_aliases` 两个原语, 跳过 enforce。

**根因**:
- patch 加在高层 wrapper (`normalize_payload`) 而非 driver 直接调用点
- T-004 patcher 没跑端到端 verify_xlsx_physical 验证 V-002 实际生效
- Round 18 治理档 P-001 已确认 hash 不变, 但 V-002 没在 Round 18 检查范围

**修复**:
- 改用 `normalize_payload` 一行调用 (统一原子路径)
- T-005.2 verify_xlsx_physical 强制覆盖 V-001~V-005 全 5 项, 而非只 V-001/V-003

**经验**:
- "patch 加在哪个文件" 和 "patch 是否被实际调用" 是两个问题
- 验证脚本必须覆盖 V 的"实际产物"而非"理论产物"
- Round 18 漏的 V-002 检查, Round 20 补上

### 2.2 ❌ driver backup 行为 vs spec (教训 2)

**症状**: P-002 spec 要求 round17.bak.xlsx 字节不变, 但 driver `xlsx_backup=True` 每次重导都 overwrite。

**根因**:
- driver `xlsx_backup` 参数最初设计意图是"迭代开发友好" (每次重导保留旧 xlsx 为 backup), 与"审计锚点"语义冲突
- 用户 spec "Round 17 历史快照" 假设 backup 是 immutable, 但 driver 行为不满足

**缓解**:
- T-005 第二次重导加 env var `AIDOCX_ROUND15_XLSX_BACKUP=0` 默认不覆盖
- 当前的 round17.bak.xlsx 已 archive 到 `archive_round1/round17_bak.preround1.xlsx`
- 后续可立 DT 修复 driver 默认 (F-001 follow-up)

**经验**:
- "备份"在不同 context 下有不同语义: 迭代开发 backup vs 审计锚点 backup
- 同一文件不应该同时承担两个角色 (audit anchor + iteration snapshot)
- 应明确命名: `round17.audit_anchor.xlsx` vs `round17.iter.bak.xlsx`, driver 不 overwrite audit_anchor

### 2.3 ❌ stale self-test (教训 3)

**症状**: run_round15_merge_export.py:self_test 因 T-003 默认 apply_renumber=True 失效 (fixture 期望 TC-1 → UI-TC-001, 实际被 renumber 改成 BIZ-TC-001)

**根因**:
- self_test 写在 Round 15, 当时 renumber 不存在
- T-003 patcher 加了 renumber 默认值, 但没跑 self_test 验证 fixture 兼容

**修复**:
- 1 行加 `apply_renumber=False` 到 self-test 调用, 保持测试意图不变 (merge+xlsx, 非 renumber)
- renumber 行为独立在 case_id_and_field_normalizer 测试 12-15 覆盖

**经验**:
- "加新参数" 必然会影响 "既有 fixture" — 必须跑既有 self-test 验证
- self-test 是文档: 它的输入输出 = 旧 API contract, 默认参数变更 = 隐性 contract 变更

### 2.4 ✓ 做得对的 (确认)

| 项 | 评价 |
|---|---|
| 第一次 verify_xlsx_physical 立即暴露 V-002 FAIL | 物理读不绕过 — 救了 V-002 |
| 修复 driver 后第二次 verify 立即 PASS | 修复 → 验证闭环 |
| P-001 hash 始终守住 (整个 T-005 全程) | 用户硬约束遵守 |
| 不修改 test_case_formatter / L1S6Validator / S7 review | 跨阶段所有权尊重 |
| 不 commit, 不重发明 T-001~T-004 | DNA §3 反模式规避 |
| 治理档落档 v20 目录 | 路径一致性, v18 不动 |

---

## 3. 留给未来的 follow-up

| ID | 描述 | 优先级 |
|---|---|---|
| F-001 | P-002 根治: driver 默认 backup 行为改成 immutable (audit anchor), 单独 backup 走 `xlsx_backup=True` 显式开关 | MAJOR |
| F-002 | v17/v18/v19 治理档链 P-002 状态复盘: 3 个 Round 间的 round17.bak.xlsx hash drift 表 | MINOR |
| F-003 | case_id_and_field_normalizer.py 自测加一个"renumber + enforce + merge" 三步集成场景 | MINOR |
| F-004 | verify_xlsx_physical.py 升级为 S6 阶段标配验证脚本 (纳入 SKILL.md §11 SSOT) | MINOR |

---

## 4. 总评

T-005 Round 1 在触发了 2 个真实 bug 后 (T-004 集成遗漏 + P-002 driver overwrite) 实现了 5/5 V + 4/5 P 全 PASS (P-002 PARTIAL 已 archive + 加 env var 保护)。

整个 Round 闭环判决: `converged_with_followup` — 业务成效全部达成, 1 项过程约束需后续 DT 修复。

未触发的硬约束违规: 0
已落档: 5 份治理档 (PLAN + audit + review + CONVERGED + DT) + 2 个脚本 (verify_xlsx_physical + render_v302_visual) + 1 个视觉 PNG + 1 个 OB