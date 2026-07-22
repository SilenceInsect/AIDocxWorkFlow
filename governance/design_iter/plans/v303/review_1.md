# Round 1 Review — v3.03 V-302-002 OBJ P0 覆盖率修复复盘

## 1. 缺陷汇总（去重 / 按严重度排序）

### BLOCKER（必须修复）
- **（无）** — 本轮所有 BLOCKER V/P 全 PASS

### MAJOR
- **SYS-008 残留**（v3.02 提出 / 本轮响应）—— Plan 阶段**先 Read 1024 行 normalizer + 428 行 driver** 已落地 SYS-008 防御；TaskQueue 4 项全部对齐 v3.02 CONVERGED §5.1 唯一 BLOCKER follow_up。无新触发。
- **§5 _write_pri 双向 mirror 缺失（侧记）** —— `enforce_obj_p0_coverage._write_pri` 在 case 同时有 `priority` + `优先级` 时仅改其中一个。**当前路径下不触发**，但属潜在 bug，建议转 v3.04 / SKILL v1.2.1。

---

## 2. 根因定位

### 机制问题
- **正向** — driver 直接展开 in-memory normalize 步骤时，漏调 `enforce_obj_p0_coverage`（vs `normalize_payload()` 已自动调用）。这是 v3.02 Round 18 修复体系外的设计空白 —— driver **不重用 `normalize_payload` 而自己改写三步**，导致规范与实现漂移。
- **修复路径最简** —— 用 **1 行 StrReplace** 把漏调的 enforce_obj_p0_coverage 补回来，**不动 normalizer 本身**（守住 P-003）。

### 规范问题
- **driver 与 normalizer.normalize_payload 不一致** —— `normalize_payload()` 函数是"完整 4 步归一化"（normalize_case_id + mirror + enforce），driver 手动展开只跑 2 步。这是 SKILL.md §NAME-FIELD-001 SSOT 之外的隐性规则（应明确"driver 必须走 normalize_payload"或"driver 必须显式调全部 3 个步骤"）。
- **SKILL.md v1.2.1 建议**：补"driver 调用 normalize_payload"或"driver 必须显式调 enforce"规范条款。

### 习惯问题
- **（无）** — 本轮严格按 5 问 / Read-before-Act / StrReplace+py_compile+self-test SOP，没出现 v3.02 Round 17/18 那些 "snapshot 不写 / 决策不落档 / 自检验证缺失"。

---

## 3. 可落地修复方案

### 立即（已完成）
- ✅ `run_normalize_and_export.py` line 197 后插入 `obj_risk_stats = enforce_obj_p0_coverage(cases)`
- ✅ return dict 加 `obj_risk_stats` 字段便于审计
- ✅ T-001/T-002/T-003/T-004 全过

### 沉淀（v3.04 / SKILL v1.2.1）
1. **§5 _write_pri 双向 mirror 修复**：把 `enforce_obj_p0_coverage._write_pri` 改为同时写两个 alias 字段（mirror_pri = bilingual 同步），保证 P0 promotion 在任意单字段读视角下都生效。
2. **driver 调用规范条目**：在 SKILL.md §3.1 Plan 阶段或 §aidocx-s6-test-cases SKILL.md 增加"driver 必须调 normalize_payload 或等效的 3 步"明示约束。
3. **driver summary 扩展**：把 `obj_risk_stats` 字段暴露到 stdout（让 driver `main()` 打印时显示 OBJ promotion 摘要），参考 `_summary_for_stdout` 已有的 trim 逻辑。

### 经验沉淀（systemic_issues）
- **SYS-008 验证**：本轮把 SYS-008 防御（Plan 阶段必须 Read 现状）应用后，Round 1 一次跑通，0 反模式触发 → **SYS-008 防御规则有效**，建议固化到 SKILL v1.2.1。

---

## 4. 修复优先级

| # | 动作 | 优先级 | 状态 |
|---|---|---|---|
| 1 | driver 加 enforce 调用 | BLOCKER | ✅ |
| 2 | T-002 验证（py_compile + self-test）| BLOCKER | ✅ |
| 3 | T-003 跑 driver 重导 xlsx | BLOCKER | ✅ |
| 4 | T-004 物理读 xlsx 验证 16/16 OBJ | BLOCKER | ✅ |
| 5 | sys_id 候选：driver 必须用 normalize_payload | MAJOR | 转 v3.04 |
| 6 | _write_pri 双向 mirror | MAJOR | 转 v3.04 |
| 7 | SYS-008 防御条款生效验证 | MAJOR | ✅（待 CONVERGED 收尾时固化）|

---

## 5. 影响范围

### 直接影响
- v3.01 `test_cases_public.xlsx` 主表 331 行 149 P0 / 附录 sheet 0 行（all Draft due to v3.01 数据本身 Ready status leak）
- xlsx P0 case 数从 137 增至 149（+12，对应 V-303-002 12 OBJ promoted）
- Round 17 历史字节不变（P-002 守住）
- test_cases.json hash 不变（P-001 守住）

### 间接影响
- v3.04 follow_up：`_write_pri` 双向 mirror + driver 调用规范条目
- v3.04 follow_up：V-303 expected 重复 33.5% 压缩（原 v3.02 报告里 carry）
- SKILL v1.2.1：SYS-008 防御条款 + driver 必走 normalize_payload 规范

### 治理档更新
- `governance/design_iter/plans/v303/audit_1.md`（本档）
- `governance/design_iter/plans/v303/review_1.md`（本档）
- `governance/design_iter/plans/v303/CONVERGED.md`（回填）
- `governance/design_iter/INDEX.md` current=v303
- `CHANGELOG.md` v303 段
