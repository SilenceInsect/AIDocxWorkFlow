# GOAL — v3.03 跟进 V-002 OBJ P0 覆盖率 1.0

> **任务来源**：v3.02 CONVERGED 报告 §5.1 BLOCKER follow_up（v3.02/CONVERGED.md）
> **Goal ID**：（生成后回填）
> **创建日期**：2026-07-20
> **目标签名（GL-009）**：`v303_v002_obj_p0_coverage_fix`

---

## 1. 顶层目标（Top-level Goal）

修复 v3.01 test_cases Public xlsx 中 12/16 OBJ 缺 P0 覆盖率（实测 75% OBJ 缺 P0），让 xlsx 重导后达成 **16/16 OBJ 至少各有 1 个 P0**（覆盖率 1.0）。

## 2. 根因诊断

### 2.1 实测确认

- `test_cases.json` 16 个 OBJ 中 **12 个 OBJ 0 P0**，集中在 BACKEND 3 个 / ORDER 2 个 / PROMO 3 个 / VIP-002 / UI 3 个
- 4 个 OBJ ≥ 1 P0：BACKEND-004 + PURCHASE-001/002 + VIP-001

### 2.2 代码根因

`ai_workflow/case_id_and_field_normalizer.py` 的 `enforce_obj_p0_coverage(cases, min_p0_per_obj=1)` 函数（line 303-422）**已实现并 self-test PASS（第 10/11 项）**：

- ✅ 函数本身 OK
- ✅ `normalize_payload()`（line 566-605）自动调用 enforce_obj_p0_coverage
- ❌ **但** `ai_workflow/run_normalize_and_export.py`（line 180-197）**手动展开** in-memory normalize 步骤，**漏调** `enforce_obj_p0_coverage`

**结论**：Driver 漏调，不是个别数据问题。

### 2.3 影响

- v3.01 `test_cases_public.xlsx` 87 个合并 TC 后，16 个 OBJ 中至少 12 个 OBJ 无 P0 覆盖
- S7 审查员 B（覆盖率审计）和 S8 自迭代会持续标记 OBJ 风险矩阵未达标
- V-002 BLOCKER 不消除 → 已 is_assumed=true，假设风险矩阵是 L1/L2 校验的非阻塞项

---

## 3. 修复目标（value_criteria）

| ID | 标准 | 严重度 | 来源 |
|---|---|---|---|
| **V-001** | xlsx 16/16 OBJ 每 OBJ ≥ 1 P0（覆盖率 = 1.0）| BLOCKER | V-302-002 修复 |
| **V-002** | xlsx 重导后 P0 case 数 ≥ 4 + 12 增量（之前 4 个 OBJ 有 P0 + 新补 12 OBJ 各 1 P0 = ≥ 16）| BLOCKER | V-302-002 修复 |
| **V-003** | test_cases_public.xlsx 物理打开，主体 + 附录 sheet 仍存在且行数合理 | MAJOR | 防回归 |

## 4. 过程约束（process_criteria）

| ID | 标准 | 严重度 |
|---|---|---|
| P-001 | v3.01 test_cases.json hash 不变 | BLOCKER |
| P-002 | test_cases_public.round17.bak.xlsx 字节不变（如果存在）| BLOCKER |
| P-003 | case_id_and_field_normalizer.py 业务函数签名不变 | BLOCKER |
| P-004 | run_normalize_and_export.py 业务函数签名不变 | MAJOR |
| P-005 | py_compile + self-test 全部通过（normalizer + driver）| BLOCKER |
| P-006 | 不引入新依赖 | MAJOR |
| P-007 | v3.02 CONVERGED 不删 | MAJOR |

## 5. 正确范例

跑一次 `run_normalize_and_export.py`（不带 --self-test）后，`openpyxl.load_workbook` 读 xlsx，统计 OBJ 维度 P0 覆盖：

```
# 期望（最小 16 P0，因为 16 OBJ）
OBJ P0 计数：16/16 OBJ 有 P0
P0 case 总数：≥ 16
```

## 6. task_queue（v1.2 并行化）

| ID | title | parallelizable | depends_on | parallel_group | artifact |
|---|---|---|---|---|---|
| T-001 | run_normalize_and_export.py 在 line 184 后加 `enforce_obj_p0_coverage(cases)` 调用 | false | [] | 1 | ai_workflow/run_normalize_and_export.py |
| T-002 | py_compile case_id_and_field_normalizer + run_normalize_and_export + self-test | false | [T-001] | 2 | runtime |
| T-003 | 跑 run_normalize_and_export 重导 v3.01 xlsx | false | [T-002] | 3 | test_cases_public.xlsx |
| T-004 | openpyxl 物理读 xlsx 验证 16/16 OBJ P0 ≥ 1 + P0 case ≥ 16 + 全 sheet 完整 | false | [T-003] | 4 | audit_1.md evidence |

## 7. 禁区（out_of_scope.md）

见 `<goal_dir>/out_of_scope.md`

## 8. 收敛条件

- V-001 16/16 OBJ P0 = 1.0（PASS）
- V-002 P0 case ≥ 16（PASS）
- V-003 sheet 完整（PASS）
- P-001/002/003/004/005 全过
- 反模式扫描无触发
