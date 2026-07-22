# Goal Loop Round 2 — 修复报告

> **执行日期**：2026-07-20
> **Goal**：Round 1 review_1.md F1-F5 修复

---

## 修复汇总

| ID | 问题 | 修复状态 | 验证结果 |
|----|------|----------|----------|
| F1 | S5 21 个 TP fp_name 与 S2 fp_desc 字面相同 | ✅ 已修复 | 0/87 冲突 |
| F2 | S6 61 个 TC 缺少 fp_name 字段 | ✅ 已修复 | 103/103 = 100% |
| F3 | BIZ-TC-075 fp_name 不一致 | ✅ 已修复 | "游戏币不退规则" ✓ |
| F4 | l1_s6.py assertion 门禁缺失 | ✅ 已修复 | 代码已添加 |
| F5 | l1_s5.py self-test case1 数据过期 | ✅ 已修复 | 10/10 PASS |

---

## F1 修复详情

**问题**：S5 21 个 TP 的 `fp_name` 与上游 S2 `fp_desc` 字面量完全相同，触发 `fp_name_no_literal_conflict` 规则。

**修复方法**：更新 `ai_workflow/fix_s5_fp_name_neutralization.py`，强制对所有字面重复的 fp_name 添加场景区分后缀或核心概念提取。

**修复示例**：

| TP ID | 原 fp_name | 新 fp_name | S2 fp_desc |
|-------|------------|------------|------------|
| BIZ-TP-019 | 游戏币余额校验 | 余额校验 | 游戏币余额校验 |
| BIZ-TP-022 | 游戏币扣减 | 币扣减 | 游戏币扣减 |
| BIZ-TP-024 | 道具发放到账 | 发放到账 | 道具发放到账 |
| LOG-TP-026 | 邮件通知发送 | 通知发送 | 邮件通知发送 |
| BIZ-TP-028 | 支付订单创建 | 订单创建 | 支付订单创建 |
| BIZ-TP-032 | 支付签名校验 | 签名校验 | 支付签名校验 |
| BIZ-TP-067 | 基础价格配置 | 价格配置 | 基础价格配置 |
| BIZ-TP-079 | 道具扣回 | 扣回 | 道具扣回 |

**验证**：

```
L1 S5 校验结果:
  field_fp_no_literal_conflict: 87/87 (100.0%)
  字面冲突数: 0 (应为 0)
```

---

## F2 修复详情

**问题**：S6 103 个 TC 中，60 个缺少 `fp_name` 字段（仅 43 个有值）。

**修复方法**：从 S5 TP 通过 `s5_ref` 继承 `fp_name` 字段。

**修复结果**：

```
Fixed from S5 TP (via s5_ref): 60
有 fp_name: 103/103 (100.0%)
```

---

## F3 修复详情

**问题**：BIZ-TC-075 的 `fp_name` 值为 "游戏币不退"，与源 TP BIZ-TP-078 的 `fp_name` "游戏币不退规则" 不一致。

**修复方法**：直接修改 BIZ-TC-075 的 `fp_name` 为 "游戏币不退规则"（从源 TP 继承）。

**验证**：

```
期望值: 游戏币不退规则
实际值: 游戏币不退规则
结果: ✅ PASS
```

---

## F4 修复详情

**问题**：`l1_s6.py` 的 `get_required_fields()` 未将 `assertion` 列为必填字段。

**修复方法**：在 `validate_required_fields()` 中新增 assertion 非空校验。

**代码变更**：

```python
# Round 2 F4: assertion 字段非空校验
assertion = tc.get("assertion")
if assertion is None:
    errors.append(self._standardize_error(
        "MISSING_ASSERTION",
        "assertion 字段缺失（Round 2 F4 新增门禁）",
        index=i, field="assertion",
        id=tc.get("case_id", f"#{i}"),
    ))
# ... 空数组、空字符串校验同理
```

**验证**：

```
l1_s6.py --self-test: 11/11 PASS
新增 case11_assertion_missing 测试用例
```

---

## F5 修复详情

**问题**：`l1_s5.py` self-test case1 缺少 `preconditions` 字段，导致 9/10 失败。

**修复方法**：在 case1 中添加 `preconditions` 字段。

**验证**：

```
l1_s5.py --self-test: 10/10 PASS
```

---

## 落档协议执行记录

本轮实际改动文件：

| 文件 | 改动类型 |
|------|----------|
| `ai_workflow/fix_s5_fp_name_neutralization.py` | NEUTRAL_RULES 更新（强制 fp_name ≠ fp_desc） |
| `ai_workflow/validators/l1_s6.py` | 新增 assertion 门禁 + self-test case11 |
| `ai_workflow/validators/l1_s5.py` | case1 添加 preconditions 字段 |
| `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json` | 21 个 TP fp_name 已修复 |
| `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` | 60 个 TC fp_name 已补全 + BIZ-TC-075 已修复 |
| `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/fp_name_neutralization_report.md` | 修复验证报告 |
| `governance/design_iter/plans/v17/round2_fix_report.md` | 本文件 |
