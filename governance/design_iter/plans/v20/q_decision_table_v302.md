# v3.02 Round 1 — DT 决策记录

> **Goal ID**：`4c1eedec-14d9-4de0-8d7c-51b21713b0c2`
> **Round**：1 / final
> **闭环日期**：2026-07-19

---

## DT-V302-001: V-004 诊断 — OpenPyXL 合并填充语义非 bug

### 触发

Round 18 审查质疑 OBJ-02 块 row 27/28 B 列"看似 None"的合并现象, 怀疑是数据缺失或 merge bug。

### 分析

- OpenPyXL 在 merged range 内的非 top-left cell 返回 None（这是标准库行为，非数据缺失）
- 物理读 B27='BIZ-TC-026', B28='BIZ-TC-027' (top-left cell)
- 验证脚本须显式读 top-left cell 才能看到真实值

### 判定

**PASS** — V-004 不需要 patch, OpenPyXL 行为符合预期。

### 证据

- `verify_xlsx_physical.py` 输出: B27='BIZ-TC-026', B28='BIZ-TC-027'
- Round 18 audit_round18.md §4 第 06 行 (OBJ-02 块 = row 26-28, B=M)

---

## DT-V302-002: V-002 enforce_obj_p0_coverage → Draft status 正交处理

### 触发

OBJ 风险矩阵要求 16/16 OBJ 至少 1 P0 用例。Round 14 evidence: 12/16 OBJ 零 P0。

### 冲突分析

enforce 写 `priority='P0'` 与 evaluate_status 写 `用例状态='Draft'` (如果 L1/L2 FAIL) 可能冲突。

### 判定

**PASS** — priority 与 status 是两个独立维度:

- `enforce_obj_p0_coverage` 只读 `obj_id` + `priority`, 不读 `status`
- `evaluate_status` 只读 L1/L2 结果, 不读 priority
- 正交: OBJ-A 可有 P0 priority 的 Draft 状态用例 (priority 重要, status 待 L1 修复后转 Ready)

### 证据

- `case_id_and_field_normalizer.py:enforce_obj_p0_coverage` L303-422
- Round 20 verify: 16/16 OBJ 至少 1 P0 ✓

---

## DT-V302-003: V-001 renumber_cases_per_module 内存重排 + apply=False 默认

### 触发

V-001 BLOCKER 要求 case_id 每模块内连续 (1, 2, 3, ...)。
Round 18 evidence: BIZ-TC-064, BIZ-TC-232, BIZ-TC-236 ... (跳号).

### 风险

直接持久化会破坏 test_cases.json 字节 (P-001 BLOCKER)。

### 判定

**PASS** — 默认 `apply=False` (pure 内存重排):

- 函数签名: `renumber_cases_per_module(cases, *, apply: bool = False)`
- driver `run_round15_merge_export.py:merge_and_export` 默认 `apply_renumber=True` (写到 xlsx)
- JSON 文件 (src_json) 永远 read-only

### 证据

- `case_id_and_field_normalizer.py:renumber_cases_per_module` L451-559
- 86 rewrites in v3.02 R1 export
- test_cases.json SHA-256 重导前后一致 = 7d6359f8...316ca ✓

---

## DT-V302-004: V-003 _merge_expected 保序去重

### 触发

Round 18 H 列字面重复 72/87 TC (e.g. BIZ-TC-232 "普通玩家可在商城道具列表或搜索结果中看到该道具" ×3)。

### 方案

`scenario_group_merger._merge_expected` 用 `list(dict.fromkeys())` 模式保序去重:

```python
seen: set[str] = set()
out: list[str] = []
for raw in list(first_exp) + list(extra_exp):
    s = str(raw).strip()
    if not s: continue
    if s in seen: continue
    seen.add(s)
    out.append(s)
```

### 判定

**PASS** — 保序去重保留 first-occurrence order, 新期望值仍可追加。

### 证据

- `scenario_group_merger.py:_merge_expected` L102-126
- Round 20 verify: 87 H cells, 0 literal duplicate

---

## DT-V302-005: T-004 driver 集成 bug 修复

### 触发

Round 20 verify_xlsx_physical 第一次运行 V-002 FAIL — 12/16 OBJ 零 P0。

### 根因诊断

T-004 patch `enforce_obj_p0_coverage` 加在 `case_id_and_field_normalizer.py:normalize_payload` 内, 但 `run_round15_merge_export.py:merge_and_export` 没调用 `normalize_payload`, 而是手动循环调 `normalize_case_id` + `mirror_bilingual_aliases` 两个原语, 跳过 enforce。

### 修复

把 driver Step 1 改为 `normalize_payload` 一行调用 — 直接走"原子"路径, 避免"原语 vs 高阶"两套路径分裂。

```python
# 修复前
counters: dict[str, int] = {}
for case in cases_in:
    if isinstance(case, dict):
        normalize_case_id(case, counters)
        mirror_bilingual_aliases(case)

# 修复后
cases_in, _counters = normalize_payload(payload if isinstance(payload, dict) else cases_in)
```

### 判定

**PASS** — 修复后 Round 20 第二次 verify: 16/16 OBJ P0 ✓

### 教训

- "patch 加在哪个文件" 和 "patch 是否被实际调用" 是两个问题
- 验证脚本必须覆盖 V 的"实际产物"而非"理论产物"

---

## DT-V302-006: P-002 driver backup 行为缓解 (env var 保护)

### 触发

T-005 第一次重导 (V-002 fix 前) 时 driver `xlsx_backup=True` 默认把当前 xlsx copy 到 round17.bak.xlsx, 覆盖了 Round 18 审计记录的 dc2fa66d... 值, P-002 spec 违反。

### 缓解方案

driver `main()` 增加 `AIDOCX_ROUND15_XLSX_BACKUP` 环境变量控制:

```python
import os
backup = os.environ.get("AIDOCX_ROUND15_XLSX_BACKUP", "0") == "1"
summary = merge_and_export(... xlsx_backup=backup ...)
```

默认 = 0 (不覆盖 round17.bak.xlsx), 只有显式 set `=1` 才覆盖。

### 当前状态

- 当前 round17.bak.xlsx hash = 63fb18779... (T-005 第一次重导时被覆盖)
- Round 18 audit 参考值 = dc2fa66d... (已不可恢复)
- archive_round1/round17_bak.preround1.xlsx = 63fb18779... (Round 20 第二次重导前快照)

### 判定

**PARTIAL** — 缓解已落, 但 Round 17 原 audit 锚点已漂移。根治需 F-001 (driver 默认 backup 改 immutable, audit anchor 走独立文件名)。

---

## DT-V302-007: run_round15_merge_export 自测修复

### 触发

T-005 第一次跑 self-test 失败: `merged_pair = []` (UI-TC-001 找不到)。

### 根因

- self_test fixture 期望 TC-1 → UI-TC-001
- T-003 patch 加 `apply_renumber=True` 默认后, renumber 把 TC-1 重排成 BIZ-TC-001 (因 sort by obj_id)
- fixture 期望值与 renumber 后实际值不一致

### 修复

1 行加 `apply_renumber=False` 到 self-test 调用, 保持测试意图不变 (merge+xlsx 验证, 非 renumber 验证)。

```python
summary = merge_and_export(
    src_json=src, xlsx_out=xlsx,
    objs_json=None, tps_json=None, xlsx_backup=False,
    apply_renumber=False,  # ← 修复
)
```

renumber 行为独立在 case_id_and_field_normalizer 测试 12-15 覆盖。

### 判定

**PASS** — 自测修复后 run_round15_merge_export --self-test 全过。

### 教训

"加新参数默认" 必然影响既有 fixture — 必须跑既有 self-test 验证。

---

## 总结

| DT | 描述 | 判定 |
|---|---|---|
| DT-V302-001 | V-004 诊断 — OpenPyXL 合并填充语义非 bug | PASS |
| DT-V302-002 | V-002 enforce_obj_p0_coverage → Draft 正交处理 | PASS |
| DT-V302-003 | V-001 renumber 内存重排 + apply=False 默认 | PASS |
| DT-V302-004 | V-003 _merge_expected 保序去重 | PASS |
| DT-V302-005 | T-004 driver 集成 bug 修复 (Round 20 本轮新加) | PASS |
| DT-V302-006 | P-002 driver backup 行为缓解 (Round 20 本轮新加) | PARTIAL |
| DT-V302-007 | run_round15_merge_export 自测修复 (Round 20 本轮新加) | PASS |
