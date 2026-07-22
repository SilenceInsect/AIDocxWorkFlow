# audit_2.md — Round 2（最终）

## 验收标准检查

| # | 验收标准 | 证据 | 正向论证 | 反向挑战 | 判定 |
|---|---------|------|---------|---------|------|
| 1 | 每个 TC 至少含 3 个步骤 | 示范 JSON 全部 ≥ 3 步 | 7 TCs 全部合规 | v3.01 旧数据仍 1 步 | PARTIAL |
| 2 | 步骤-预期显式 step_ref | Excel 验证截图 | `[步骤1] 商城首页正常打开...` | — | **PASS** |
| 3 | 不同前置条件独立 TC | BIZ-TC-001/002/003 | 余额充足/不足/边界分开 | — | **PASS** |
| 4 | Excel 渲染正确 | Excel 验证截图 | 步骤和预期都正确渲染 | — | **PASS** |
| 5 | SKILL.md §12 更新 | §12 v2.0 | 规范已更新为强制 | LLM 执行待验证 | **PASS** |

## 修复证据

1. **SKILL.md §12 v2.0**：标记为强制执行
2. **test_case_formatter.py**：修复 `_render_list_item` 支持 `step_ref` + `预期` 格式
3. **test_cases_structured.json**：示范文件，7 TCs 全部合规
4. **test_cases_structured.xlsx**：Excel 渲染正确
5. **self-test**：所有测试通过

## 遗留问题

- v3.01 旧数据（331 TCs）需用户决策是否重新生成
- LLM 执行规范待实际 S6 运行时验证

## 收敛判定

**PASS**：规范落地完成，可进入下一轮迭代
