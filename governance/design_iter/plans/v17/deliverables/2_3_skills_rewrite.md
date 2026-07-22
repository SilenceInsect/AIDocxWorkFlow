# 子任务 2.3 — s5/s6 SKILL.md 改写

> **本档**：s5/s6 SKILL.md NAME 段（v16 锚点铁律）改为字段溯源铁律
> **治理基线**：v17/PLAN.md §2.1 必改约束文件（5 处）
> **v17 阶段定位**：Phase 2 子任务 2.3

---

## 1. 改写范围

| 文件 | 范围 | 行号 |
|---|---|---|
| `.cursor/skills/aidocx-s5-test-points/SKILL.md` | "🔴 命名一致性铁律" NAME 段 | line 17-120 |
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | "🔴 命名继承一致性铁律" NAME 段 | line 18-112 |

**Out of Scope**（不在本次治理）：
- s5 SKILL.md §v12 S3/S4→TP 字段溯源（line 429+）
- s6 SKILL.md §v12 BIZ TC 4 层引用模板（line 540+）/ §v12 UI TC 4 字段模板（line 509+）/ §v11 S5→S6 链路（line 664+）
- 其他 v10/v11/v12 历史治理产物

---

## 2. s5 SKILL.md 改写内容清单

### 2.1 标题 / 标识变更

| 改前 | 改后 |
|---|---|
| `## 🔴 命名一致性铁律（ — 最高优先级，违反直接 L1 打回）` | `## 🔴 命名一致性铁律（字段溯源版 — 最高优先级，违反直接 L1 打回）` |
| `> **v16-NAME-001**：` | `> **NAME-FIELD-001**：` |
| `校验精度：v2 精确锚点版（格式校验 + 名称精确匹配 + 字段校验）` | `校验精度：字段溯源版（字段精准匹配——obj_name/fp_name == S2）+ LLM 自由文本溯源（title/description 不带锚点）` |

### 2.2 核心规则变更

| 维度 | 改前 | 改后 |
|---|---|---|
| 规则 2 | title/description **必须以** `【OBJ - FP】` 锚点开头 | title/description **不带锚点**（纯场景文本） |
| 规则 3 | OBJ/FP 都禁止 LLM 自创 | OBJ 禁止 LLM 自创（S2 100% 匹配）；FP 由 LLM 自创（中性名） |
| fp_name 来源 | S2 `fp_desc` 100% 逐字相等 | **LLM 自创中性功能名**（含动词 + ≤ 20 字符 + 不与 S2 `fp_desc` 字面量重复） |

### 2.3 字段格式模板变更

| 字段 | 改前 | 改后 |
|---|---|---|
| title | `【{OBJ - FP}】{4-12字场景摘要}` | `{4-12字场景摘要}（不带锚点）` |
| description | `【{OBJ - FP}】{完整测试逻辑}` | `{完整测试逻辑}（不带锚点）` |

### 2.4 自检流程变更

| 改前校验项 | 改后校验项 |
|---|---|
| title 有锚点（开头是【xxx - xxx】） | title 无锚点（开头不是【xxx - xxx】） |
| description 有锚点 | description 无锚点 |
| 锚点一致（title 和 description 锚点完全相同） | 锚点分离（title 和 description 不含【】锚点） |
| FP 名正确（锚点 FP 名 = S2 fp_desc） | FP 名正确（TP.fp_name ≠ S2 fp_desc） |

### 2.5 错误对照表变更

| 改前错误示例 | 改后正确示例 |
|---|---|
| `【道具搜索功能 - 支持道具名称模糊搜索】验证模糊搜索功能正常` | `模糊搜索功能正常验证` |
| `【道具搜索 - 模糊搜索】...`（名称缩写） | `TP.obj_name = '道具搜索功能'`（S2 严格匹配） |
| `缺少 obj_name 字段 → TP.obj_name = "商城首页道具列表"` | 同（保留） |
| `缺少 fp_name 字段 → TP.fp_name = "首页按销量展示前10个热门道具"` | `TP.fp_name = "首页销量排序展示"`（LLM 自创中性名） |

### 2.6 L1 校验函数变更

| 改前 | 改后 |
|---|---|
| `L1S5Validator.validate_formal_name_v2()` | `L1S5Validator.validate_field_traceability()` |

### 2.7 Schema 变更

| 字段 | 改前 | 改后 |
|---|---|---|
| title | `"【商城首页道具列表 - 首页按销量展示前10个热门道具】验证销量排序"` | `"首页销量排序展示验证"` |
| description | `"【商城首页道具列表 - ...】验证玩家进入..."` | `"玩家已登录游戏，进入商城首页。验证按销量降序展示前10个道具..."` |
| fp_name | `"首页按销量展示前10个热门道具"` | `"首页销量排序展示"`（LLM 自创中性名） |

---

## 3. s6 SKILL.md 改写内容清单

### 3.1 标题 / 标识变更

| 改前 | 改后 |
|---|---|
| `## 🔴 命名继承一致性铁律（ — 最高优先级，违反直接 L1 打回）` | `## 🔴 命名继承一致性铁律（字段溯源版 — 最高优先级，违反直接 L1 打回）` |
| `> **v16-NAME-001**：` | `> **NAME-FIELD-001**：` |

### 3.2 核心规则变更

| 维度 | 改前 | 改后 |
|---|---|---|
| 规则 1 | obj_name 从 TP 取值；fp_name 从 TP 取值 | obj_name 从 TP 取值（最终 == S2 obj_name 100% 匹配）；fp_name 从 TP 取值（LLM 自创中性名） |
| 规则 2 | test_scenario **必须以** `【OBJ - FP】` 锚点开头 | test_scenario **不带锚点**（纯场景文本） |
| 规则 3 | OBJ/FP 必须从 TP 继承 | TC.obj_name 必须 == TP.obj_name（最终 == S2 obj_name 100% 匹配）；TC.fp_name 必须 == TP.fp_name |

### 3.3 字段格式模板变更

| 字段 | 改前 | 改后 |
|---|---|
| test_scenario | `【{OBJ - FP}】{场景描述}` | `{纯场景一句话描述}（不带锚点）` |

### 3.4 L1 校验函数变更

| 改前 | 改后 |
|---|---|
| `L1S6Validator.validate_formal_name_v2()` | `L1S6Validator.validate_field_traceability()` |

### 3.5 Schema 变更

| 字段 | 改前 | 改后 |
|---|---|---|
| fp_name | `"首页按销量展示前10个热门道具"` | `"首页销量排序展示"`（LLM 自创中性名） |
| test_scenario | `"【商城首页道具列表 - 首页按销量展示前10个热门道具】玩家进入商城首页..."` | `"玩家进入商城首页，验证道具列表按销量降序排列"` |

---

## 4. §11 违规扫描结果

```
$ grep -E "\b(v\d+(?:\.\d+)?)\s+(v\d+(?:\.\d+)?)\b" aidocx-s5-test-points/SKILL.md
（无输出）

$ grep -E "\b(v\d+(?:\.\d+)?)\s*(\+?\s*(?:新增|SSOT|强制))(规则)?" aidocx-s5-test-points/SKILL.md
（无输出）

$ grep -E "\b(v\d+(?:\.\d+)?)\s+(v\d+(?:\.\d+)?)\b" aidocx-s6-test-cases/SKILL.md
（无输出）

$ grep -E "\b(v\d+(?:\.\d+)?)\s*(\+?\s*(?:新增|SSOT|强制))(规则)?" aidocx-s6-test-cases/SKILL.md
（无输出）
```

> **NAME 段内 0 处 §11 违规**。

---

## 5. 大文件改动 SOP 执行（§3.7）

| 检查项 | s5 SKILL.md | s6 SKILL.md |
|---|---|---|
| Read 全文 | ✅（line 1-719） | ✅（line 1-1015） |
| 文件总行数 | 719 行 > 400 | 1015 行 > 400 |
| 走 StrReplace | ✅（仅改 NAME 段） | ✅（仅改 NAME 段） |
| 额外验证（grep 自检） | ✅ 0 处违规 | ✅ 0 处违规 |

---

## 6. 落档协议

- 本档已落档
- 修改文件数：2（s5/s6 SKILL.md NAME 段）+ 1（落档）= 3 ≤ §9.1 红线
- 单次响应工具调用：≤ 10
- §11 违规数：0
- 子任务 2.3 状态：✅ 完成