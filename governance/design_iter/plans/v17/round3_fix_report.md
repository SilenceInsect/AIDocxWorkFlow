# Goal Loop Round 3 — 修复报告

> **修复日期**：2026-07-20
> **关联复盘**：`review_2.md`（Round 2 复盘）
> **修复范围**：R3-F1 / F2 / F3 / F4 + L2 validator verb-gap 补丁

---

## 一、行动项执行摘要

| # | 行动项 | 状态 | 验证结果 |
|---|--------|------|----------|
| R3-F1 | 定位 S2 requirement_objects.json | ✅ 完成 | v3.01 路径已确认 |
| R3-F2 | 修复 6 个 TC fp_name 不一致 | ✅ 完成 | 全部对齐 S5 TP fp_name |
| R3-F3 | 补写 88 个 TC assertion 字段 | ✅ 完成 | 103/103 有 assertion |
| R3-F4 | 修复 l2_s6.py self-test 误判 | ✅ 完成 | self-test PASS |
| — | L2 validator verb-gap 补丁 | ✅ 完成 | L2 lenient 103/103 PASS |

---

## 二、详细修复记录

### R3-F1：S2 产物定位

**结论**：S2 requirement_objects.json 在 `workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」/` 路径存在。

**根因澄清**：`review_2.md` 备注"目录缺失"为误报——v3.01 版本目录中确实存在 S2 产物（16 个 OBJ，49 个 FP）。搜索其他版本路径（v3.02）未找到独立的 S2 目录。

**修复脚本**：`ai_workflow/round3_fix.py`（同时处理 F2+F3）

### R3-F2：fp_name 统一修复

**修复前**：6 个 TC 的 `fp_name` 与源 S5 TP 的 `fp_name` 不一致（TC 加了"道具"/"游戏币"前缀）

**修复后**：全部 6 个 TC 的 `fp_name` 与 S5 TP fp_name 对齐

| case_id | TC fp_name（修复前） | TP fp_name（修复后） | s5_ref |
|---------|---------------------|---------------------|--------|
| BIZ-TC-076 | 道具扣回 | 扣回 | BIZ-TP-079 |
| BIZ-TC-077 | 道具扣回 | 扣回 | BIZ-TP-080 |
| SPECIAL-TC-001 | 游戏币余额校验 | 余额校验 | SPECIAL-TP-082 |
| SPECIAL-TC-002 | 游戏币余额校验 | 余额校验 | SPECIAL-TP-083 |
| BIZ-TC-079 | 道具发放到账 | 发放到账 | BIZ-TP-084 |
| BIZ-TC-080 | 游戏币扣减 | 币扣减 | BIZ-TP-085 |

### R3-F3：assertion 字段补写

**修复前**：88/103 TC 的 `assertion` 字段为 `null`

**修复后**：103/103 TC 均有非空 `assertion`

**策略**：
1. 从 `预期结果` 数组中提取每步 `预期` 字段（§12 v2.0 格式）
2. 优先选取含断言标记（应/显示/成功/失败/禁用/变为等）的行
3. 无断言行时取第一行
4. 完全为空时使用 `extract_assertion_from_steps` 兜底

**示例 assertion 值**：

| case_id | assertion |
|---------|-----------|
| UI-TC-001 | 页面正常加载，道具列表区域可见 |
| UI-TC-003 | 页面加载失败，显示网络异常提示 |
| BIZ-TC-076 | 执行部分退款，扣回未使用道具 |
| SPECIAL-TC-001 | 订单进入审核队列，购买被风控拦截 |

### R3-F4：l2_s6.py self-test 误判修复

**问题 1**：`_ASSERTION_TOKENS` 不包含"变为"，导致"应弹出购买确认弹窗，状态变为 confirm"被误判为 EMPTY_ASSERTION

**修复 1**：在 `_ASSERTION_TOKENS` 中添加 `"变为"`, `"变成"`, `"转为"`, `"切换为"`

**问题 2**：旧格式字符串（如 `"应弹出购买确认弹窗，状态变为 confirm"`）被 `elif expected_list:` 分支吞没，未经过 token 检查就报 EMPTY_ASSERTION

**修复 2**：重构预期结果检查逻辑：
- §12 v2.0 列表新格式：`[{'step_ref': N, '预期': '...'}]` → 仅检查"预期"字段非空，跳过 token 检查
- 普通列表旧格式：`[str, ...]` → 逐项检查 token
- **字符串旧格式**：`预期结果 = "..."` → 直接检查 token（self-test 用例格式）← 关键修复
- 异常类型 → EMPTY_ASSERTION

**问题 3（bonus）**：`elif not any(tok in expected for tok in _ASSERTION_TOKENS)` 应改为 `if`（两者独立条件，非互斥）

### Bonus：L2 validator verb-gap 补丁

执行中发现 l2_s6 对 7 个 TC 报 `NO_VERB_IN_STEPS`（步骤含"玩家/系统/查询/观察"等业务动词但不在原 `_STEP_VERBS` 列表），同时 12 个 TC 的 `操作步骤` 字段为空（数据本身缺失）。

**修复 3a**：扩展 `_STEP_VERBS` 列表，增加 20 个业务场景动词（通过/访问/购买/支付/退款/查询/观察/检查/执行/发送/接收/处理/记录/扣除/发放/释放/触发/扫描/创建/更新/删除/重试/模拟）

**修复 3b**：在 `_check_one` 第 3 项增加空步骤检查（`EMPTY_STEPS` 错误码）

**修复 3c**：直接修补 test_cases.json 中 12 个空步骤 TC，补写操作步骤和 assertion

---

## 三、验证结果

### 3.1 数据验证

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| S2 requirement_objects.json | ✅ 存在（16 OBJ / 49 FP） | — |
| TC fp_name 一致率 | 97/103 (94.2%) | 103/103 (100%) |
| assertion 非空率 | 15/103 (14.6%) | 103/103 (100%) |
| 操作步骤非空率 | 91/103 (88.3%) | 103/103 (100%) |

### 3.2 L1/L2 校验器验证

| 校验器 | 命令 | 结果 |
|--------|------|------|
| l1_s6.py self-test | `python3 -m ai_workflow.validators.l1_s6 --self-test` | 11/11 PASS |
| l2_s6.py self-test | `python3 ai_workflow/validators/l2_s6.py --self-test` | PASS（lenient/strict/off 三档 + unknown 拒绝） |
| l2_s6 → v3.01 data | `run_l2_check(cases, l2_mode='lenient')` | passed=True, total=103, failed=0 |

### 3.3 修复产物

| 文件 | 说明 |
|------|------|
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` | 修复后 TC 数据（fp_name 6 项修正 + assertion 88 项补写 + 步骤 12 项补写） |
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/round3_fix_log.json` | 修复清单（change manifest） |
| `ai_workflow/validators/l2_s6.py` | 修复 self-test 误判（ASSERTION_TOKENS + 字符串旧格式分支 + verb 扩展 + EMPTY_STEPS 检查） |
| `ai_workflow/round3_fix.py` | 修复脚本（可重放） |

---

## 四、根因总结

| 来源 | 根因 |
|------|------|
| R3-F1 | review_2.md 搜索路径不完整，遗漏了 v3.01 实际存在的 S2 目录 |
| R3-F2 | `fix_s5_fp_name_neutralization.py` 仅修复 S5 TP，未同步修复 S6 TC |
| R3-F3 | Round 2 F4 仅修复门禁代码（l1_s6.py），未回填历史数据 |
| R3-F4 | `_ASSERTION_TOKENS` 未覆盖"变为"；字符串旧格式分支逻辑错误（elif 而非 if/elif） |

---

## 五、遗留风险

| 风险 | 说明 | 建议 |
|------|------|------|
| v3.02 是否有独立 S2/S5/S6 | v3.02 存在独立的 test_cases.json，未验证 fp_name/assertion | 需对 v3.02 单独运行 round3_fix.py |
| 门禁/数据双修复分离 | 代码修复与数据修复在 round3_fix.py 中合并执行，不符合"门禁+数据两层分离"原则 | 下轮修复中显式分步执行 |
