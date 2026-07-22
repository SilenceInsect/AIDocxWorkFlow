# Audit Round 3

**Goal**: TC 结构化映射关系治理（v1.1）
**Date**: 2026-07-20
**Auditor**: AI 需求全流程治理工程师

---

## accept_criteria 对照

### AC-1: TC 内部结构化映射规范文档

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 规范文档存在 | ✅ PASS | `TC_STRUCTURAL_MAPPING_SPEC.md` v1.1 |
| TP → TC 链路 | ✅ PASS | 用户确认 TP=测试意图，1 TP → N TC |
| preconditions 字段 | ✅ PASS | 新增 preconditions 必填字段 |
| tc_generation_hints 字段 | ✅ PASS | 新增场景变体指导 |

**判定**: ✅ PASS

---

### AC-2: S5 SKILL.md 集成前置条件规范

| 检查项 | 状态 | 证据 |
|--------|------|------|
| §七章节新增 | ✅ PASS | SKILL.md 新增 §七 TP 前置条件规范 |
| preconditions 字段规范 | ✅ PASS | 必填、规则、错误对照 |
| tc_generation_hints 字段规范 | ✅ PASS | 可选、场景变体指导 |
| S5 → S6 链路图 | ✅ PASS | 流程图展示继承关系 |

**判定**: ✅ PASS

---

### AC-3: S6 SKILL.md §12 TP → TC 链路

| 检查项 | 状态 | 证据 |
|--------|------|------|
| §12 更新到 v1.1 | ✅ PASS | SKILL.md §12 已更新 |
| TP → TC 链路图 | ✅ PASS | 展示继承关系 |
| 字段继承规则 | ✅ PASS | 7 个字段的继承关系 |
| 禁止模式 | ✅ PASS | 1 步 1 TC 等 4 种禁止 |

**判定**: ✅ PASS

---

### AC-4: test_case_formatter.py 支持新映射

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 新函数存在 | ✅ PASS | is_new_structural_mapping_format() |
| 渲染函数 | ✅ PASS | render_steps_with_expected() |
| 校验函数 | ✅ PASS | validate_structural_mapping() |
| 语法验证 | ✅ PASS | py_compile 通过 |

**判定**: ✅ PASS

---

### AC-5: v3.01 TP 按新结构重新生成

| 检查项 | 状态 | 证据 |
|--------|------|------|
| TP 重新生成 | ⏳ 待执行 | 需要触发 S5 重新生成 |

**判定**: ⏳ 待执行

---

## 汇总

| accept_criteria | 状态 |
|-----------------|------|
| AC-1 规范文档 | ✅ PASS |
| AC-2 S5 SKILL.md | ✅ PASS |
| AC-3 S6 SKILL.md §12 | ✅ PASS |
| AC-4 formatter.py | ✅ PASS |
| AC-5 TP 重新生成 | ⏳ 待执行 |

**判定**: 规范和代码工作完成（AC-1~AC-4），需要触发 S5 重新生成（AC-5）

---

## 根因分析与迭代

### 用户决策：重新设计 TP 结构

**决策点**: S5 TP 缺少前置条件字段，1 步 1 TC 问题无法在现有结构下解决

**用户选择**: 方案C - 重新设计 TP 结构
- TP = 测试意图（告诉 S6 要测什么）
- 1 TP → N TC
- TP 包含公共表头字段

**迭代结果**: 规范从 v1.0 升级到 v1.1，新增：
- S5 TP.preconditions 字段（必填）
- S5 TP.tc_generation_hints 字段（可选）
- S6 TC 继承 TP 前置条件和预期结果

---

## 建议

AC-5 需要用户决策：
1. **触发 S5 重新生成**：使用新规范生成 TP
2. **暂不生成**：规范完成，用户后续手动触发
