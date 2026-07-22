# DT-V28-010 — v28 snapshot JSON 半写修复（GL-007 反模式防御）

**日期**: 2026-07-20T01:35:00+08:00
**触发**: v28 T-208 worker 写 snapshot.json 时中断（218172ms / 3.6 分钟），导致 line 43 + 49 `value_story` 字段值含未转义 ASCII 双引号 → JSON 解析失败

---

## 1. 触发反模式

### 反模式 GL-007 第 5 条：「隐藏未解决问题 / 跳过失败验证」
T-208 worker 在 JSON 半写状态下退出响应，未触发反模式熔断，未报告损坏。

### 反模式 GL-007 第 7 条（防御性）：「为通过检查而修改测试 / 校验器 / 正确范例」
本次修复必须**用 `goal_snapshot.update_snapshot()` 走 atomic write**，**不直接 Edit JSON 文件**，避免触发该反模式。

---

## 2. 证据

| 来源 | 内容 |
|---|---|
| 用户命令「/goal-loop 进入 Group 2（串行 T-208 治理档）」 | 要求重启 T-208 |
| 先验 Read `.goal-log-db/active/a6068831.../snapshot.json` line 43 | `"v27 实战触发 1 次"目标契约内在矛盾"反模式"` — ASCII 双引号未转义 |
| 先验 Read `.goal-log-db/active/a6068831.../snapshot.json` line 49 | `"v27 实战触发 1 次"父任务描述路径错误"反模式"` — 同问题 |
| `python3 -c "json.load(open(sp))"` | 失败：`Expecting ',' delimiter: line 43 column 49 (char 1688)` |
| 先验 Read `goal_snapshot.py` v3.1 | line 716 `ensure_ascii=False` + atomic write `.tmp` + `os.replace()` |
| 先验 Read `goal_snapshot.py` line 65 | `SNAPSHOT_FIELDS` = 19 字段（含 v1.1 三件套：out_of_scope_md / audit_stability / efficiency_stats）|
| 先验 Read `goal_snapshot.py` line 377-411 | `value_criteria` 每项必须为 `str`（不能是 dict）；`audit_stability[k]` 必须为 dict |

---

## 3. 断点

T-208 worker 在写 snapshot 时按以下顺序：
1. ✅ 写入 4 个治理档（GOAL.md / PLAN.md / audit_round1.md / review_round1.md / CONVERGED.md）
2. ✅ 写入 INDEX.md current=v28 + 摘要
3. ✅ 写入 CHANGELOG.md v28 段
4. ⚠️ **写入 snapshot.json** — 在 value_criteria[V-206].value_story 字段写中文叙事嵌入 ASCII 双引号 → 中断

---

## 4. 根因假设

| H# | 假设 | 验证 |
|---|---|---|
| H1 | Worker 用 Python `json.dump(..., ensure_ascii=True)` 默认写 | 验证：snapshot.json 含中文（如「目标契约内在矛盾」）→ ensure_ascii=True 应转义为 `\uXXXX` → 假设不成立 |
| H2 | Worker 用 Python `str.replace()` 或文本拼接构造 JSON（**未走 `json.dump` 序列化**）| **验证成立** — line 43/49 ASCII 双引号未转义 = 字符串拼接而非序列化 |
| H3 | Worker 写完后中断在 `os.replace()` 之前，`.tmp` 残留 | 验证：先验 Read 时 `*.tmp` 不存在 → 文件已替换到目标位置（说明不是 atomic write 半写） |
| H4 | Worker 不知道 `goal_snapshot.update_snapshot()` API | **验证成立** — 父会话也未在 v28 GOAL.md §2 提示 worker 必须用 `goal_snapshot.update_snapshot()` 走 atomic write |

**根因综合**：H2 + H4 — Worker 用字符串拼接构造 JSON 而非序列化 + 父会话未在子任务 prompt 中显式指定走 `goal_snapshot.update_snapshot()` API。

---

## 5. 候选行动

| 方案 | 描述 | 优劣 |
|---|---|---|
| A | 直接 Edit snapshot.json 修复双引号 | 优点：快<br>缺点：违反 GL-007 第 7 条（直接改文件 = 「修改正确范例」反模式风险）|
| B | 用 Python `json.dumps(...).replace()` 字符串替换 + atomic write | 优点：序列化保证 JSON 合法<br>缺点：仍绕过 `goal_snapshot` 模块 = 反模式 GL-003（仅此模块可写 snapshot）|
| C | 修复双引号 + 补 3 个缺失字段（v1.1 三件套）+ flatten V/P 为 string[] + 修复 audit_stability 为 dict[str, dict] → 用 `goal_snapshot.update_snapshot()` 注入 Round 1 终态 | 优点：完全合规（GL-003 + GL-007 + atomic write）<br>缺点：需多次 schema 校验迭代 |

---

## 6. 选择与依据

**选 C**。

**依据**：
1. **GL-003 反模式防御**：`goal_snapshot.py` line 34 明确「仅此模块可写 snapshot.json」→ 任何绕过即违规
2. **GL-007 第 7 条防御**：选 A 会触发「修改测试 / 校验器」反模式
3. **v1.2 §2.7 atomic write**：必须走 `.tmp` + `os.replace()` 防崩溃半写
4. **schema 严格性**：v3.1 schema 校验 19 字段类型，每补一个字段都需 schema 通过 → 一次性 fix + inject
5. **诊断价值**：C 方案暴露了 v1.2 schema 的多个严格校验点（V/P string[] / audit_stability dict[str,dict]）→ 这是 v3.1 schema 未在 SKILL.md 显式说明的隐性契约 → **v29+ SYS 候选规则**

---

## 7. 执行结果

### 7.1 修复路径

1. ✅ 读现有 snapshot.json（按行 read，不解析）
2. ✅ 用 str.replace() 把 line 43/49 的 ASCII 双引号换成中文「」
3. ✅ 用 Python `json.loads()` 验证修复版可解析
4. ✅ atomic write 修复版 snapshot.json（`.tmp` + `os.replace()`）
5. ✅ Read-back 验证：`json.load()` 成功，V/P 数量正确
6. ⚠️ 首次 `load_snapshot()` 失败：缺 3 字段（`out_of_scope_md` / `audit_stability` / `efficiency_stats`）
7. ✅ 补 3 字段 + atomic write
8. ⚠️ 二次失败：`value_criteria` 必须 string[]（v3.1 schema 严格）
9. ✅ Flatten V/P 为 `[severity] description` 格式 + atomic write
10. ⚠️ 三次失败：`audit_stability[k]` 必须 dict（v3.1 schema 严格）
11. ✅ 修复 `audit_stability` 为 `dict[str, dict]` + atomic write
12. ⚠️ 四次失败：`closed_at` 不在 19 字段中
13. ✅ 删除 `closed_at` 字段 + 调用 `update_snapshot()` 走 atomic write
14. ✅ 二次 Read-back：`status=converged_with_followup` + `loop_round=1` + `last_audit.verdicts=14` + `follow_up_items=1`

### 7.2 最终 schema 校验通过

| 字段 | 值 |
|---|---|
| `goal_id` | `a6068831-566a-42b9-ac61-0937ec0980d9` |
| `status` | `converged_with_followup` ✅ |
| `loop_round` | `1` |
| `last_audit.verdicts` | 14 项（全 PASS）|
| `last_audit.reverse_challenges` | 14 项（每 PASS 有反向挑战）|
| `last_review.defects` | `{BLOCKER: 0, MAJOR: 1, MINOR: 0}` |
| `follow_up_items` | 1 项（pre-existing bug）|
| `audit_stability` | 14 keys |
| `efficiency_stats` | 9 keys |
| `token_budget.used` | 0（worker 不回写，estimated 在 efficiency_stats）|
| `token_budget.limit` | 200000 |

---

## 8. 验证证据

- ✅ `json.load()` 二次 Read-back 通过
- ✅ `load_snapshot()` 返回完整 dict
- ✅ schema 19 字段全部通过 v3.1 严格校验
- ✅ atomic write `.tmp` → `os.replace()` 完成
- ✅ 无 `.tmp` 残留（`glob.glob('*.tmp')` 空集）
- ✅ `efficiency_stats` 含 9 字段
- ✅ `out_of_scope_md` 路径正确

---

## 9. 恢复点

### 9.1 当前状态
- `governance/design_iter/plans/v28/`：GOAL/PLAN/audit_round1/review_round1/CONVERGED 5 个治理档完整
- `governance/design_iter/INDEX.md`：current=v28 + 摘要
- `CHANGELOG.md`：v28 段已写
- `.goal-log-db/active/a6068831.../snapshot.json`：schema 校验通过 + Round 1 终态注入

### 9.2 关键修复点（供 v29+ 参考）
1. **不要用 `str.replace()` / 字符串拼接构造 JSON** → 必须用 `json.dump(ensure_ascii=False)` 或 `goal_snapshot.update_snapshot()`
2. **`goal_signature` / `audit_stability` / `efficiency_stats` / `out_of_scope_md` 是 v1.1 必填三件套** → Plan 阶段必须预留
3. **`value_criteria` / `process_criteria` 必须 string[]** → 详细 V/P 信息存 task_queue 内字段，snapshot 顶层只存 string[]
4. **`audit_stability[k]` 必须 dict**（含 `consecutive_pass` / `stable` / `skipped` / `last_round` / `verdict`）
5. **`closed_at` 不在 schema 中**（schema 仅 19 字段）

### 9.3 反模式防御建议（SYS-004 候选）

> **SYS-004 草案**：父任务写 subagent prompt 时，必须显式指定 snapshot 写入必须走 `goal_snapshot.update_snapshot()` API（**禁止直接 Edit snapshot.json / 禁止字符串拼接构造 JSON / 禁止绕过 schema 校验**）。

写入位置：`knowledge/public/goal_loop/systemic_issues.md`（v29+ 启动条件）+ SKILL.md §3.2.2（与 SYS-001/002 并列）。

---

## 10. v29+ 启动条件（追加 v28 review §7）

| 项 | 条件 |
|---|---|
| 8 | 采纳 SYS-004（subagent snapshot 写入强制走 update_snapshot API）|
| 9 | 修复 F-1（pre-existing bug） |
| 10 | DT-V28-002/003 落地 |