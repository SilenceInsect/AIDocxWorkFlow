# 子任务 2.6 — v3.01 87 TP + 87 TC 字段溯源改写完成

> **本档**：v17 字段溯源方案对 v3.01 87 TP / 87 TC 的实际重写报告
> **结论**：✅ **L1 校验 0 错误**（S5 0 findings + S6 0 findings）

---

## 1. 上游材料 Read 摘要

| 文件 | 行数 | 关键字段 |
|---|---|---|
| `v3.01/「S5 测试点生成」/test_points.json` | 1973 | 87 TP，17 字段（meta + tp_id + module + related_tags + test_point_type + title + description + feature_point_ref + obj_id + s4_reference + is_assumed + applies_rule + test_point_id + test_type + priority + obj_name + fp_name + s5_ref）|
| `v3.01/「S6 测试用例生成」/test_cases.json` | 1879 | 87 TC，20 字段（meta + case_id + tc_id + tp_ref + s5_ref + module + case_type + 用例描述 + test_scenario + test_method + 功能描述 + 前置条件 + 操作步骤 + 预期结果 + feature_point_ref + obj_id + priority + 用例状态 + 备注 + obj_name + fp_name）|
| `v3.01/「S2 需求拆解」/requirement_objects.json` | — | 16 OBJ（位于 `objects` 字段），含 obj_name / feature_points |

---

## 2. 字段溯源对齐情况（重写前）

| 维度 | 状况 |
|---|---|
| **obj_name vs S2 OBJ.obj_name** | ✅ 87/87 完全一致（无需修复）|
| **fp_name** | ✅ 87/87 已是中性名（不是 S2 fp_desc 字面重复）|
| **TP title 锚点【OBJ-FP】** | ❌ 87/87 含锚点 → 需移除 |
| **TP description 锚点【OBJ-FP】** | ❌ 87/87 含锚点 → 需移除 |
| **TC 用例描述 锚点** | ❌ 87/87 含锚点 → 需移除 |
| **TC test_scenario 锚点** | ❌ 87/87 含锚点 → 需移除 |
| **字段完整性** | ✅ 17 字段（TP）+ 20 字段（TC）齐全 |

---

## 3. 改写策略

**最小改动原则**：字段已合规（obj_name 精准匹配 OBJ、fp_name 中性名），**唯一违规是文本中的【OBJ-FP】锚点前缀**。

**操作**：用一次性 Python 脚本批量去除 348 处（174 TP + 174 TC）锚点前缀，保留其余字段不动。

**脚本核心逻辑**：

```python
ANCHOR = re.compile(r"^【[^】]+】\s*")
def strip_anchor(text):
    return ANCHOR.sub("", text, count=1)
# 应用于 TP.title, TP.description, TC.用例描述, TC.test_scenario
```

---

## 4. 改写后验证

| 检查项 | 改写前 | 改写后 | 结果 |
|---|---|---|---|
| TP title 锚点残留 | 87/87 | 0/87 | ✅ |
| TP description 锚点残留 | 87/87 | 0/87 | ✅ |
| TC 用例描述 锚点残留 | 87/87 | 0/87 | ✅ |
| TC test_scenario 锚点残留 | 87/87 | 0/87 | ✅ |
| TP 数量 | 87 | 87 | ✅ |
| TC 数量 | 87 | 87 | ✅ |
| obj_name 字段一致性 | 87/87 | 87/87 | ✅ |
| fp_name 中性 | 87/87 | 87/87 | ✅ |

**样例（改写后）**：

```
TP-001 title: 验证首页按销量降序展示前10个热门道具
TP-001 description: 验证玩家进入商城首页时，道具列表前10个道具按销量降序排列显示
TC-001 test_scenario: 玩家进入商城首页，验证道具列表前10个道具按销量降序排列
```

---

## 5. L1 校验结果

```bash
$ python3 ai_workflow/validators/l1_s5.py --self-test
[L1 S5 self-test] 10/10 passed

$ python3 ai_workflow/validators/l1_s6.py --self-test
[L1 S6 self-test] 10/10 passed

$ # 对真实 v3.01 跑 validate_field_traceability
S5 errors: 0, total findings: 0
S6 errors: 0, total findings: 0
```

**L1 校验 100% 通过**（S5 0 ERROR + S6 0 ERROR + 0 警告）。

---

## 6. §11 版本标记自检

- 改写后文件 grep `v\d+`：仅 `meta.version = "v3.01"`（目录结构语义，正确用法），文本内容 0 处版本标记违规
- Python 辅助脚本 `_strip_anchors.py` 已删除（一次性使用，避免污染 git）

---

## 7. 落档协议

- 本档已落档
- 修改文件数：2（test_points.json + test_cases.json）+ 1（本档）+ 1（一次性脚本，已删）= 4
- 单次响应工具调用 ≤ 10
- §11 违规：0
- L1 校验：100% pass
- **子任务 2.6 状态：✅ 完成**