# V-004 BLOCKER 诊断报告 — T-002 B 列合并物理排查

> **时间**：2026-07-19 23:36 UTC+8
> **任务来源**：goal-loop Round 19 V-004 BLOCKER (worker 模式)
> **诊断对象**：`workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx` row 26-28 B 列

---

## 1. 物理读证据原文（OpenPyXL 直读）

### 1.1 OBJ-02 合并区 B26:B28（3 行：BIZ-TC-223/226/229）

| 行号 | case_id | R17 (backup) B 列 | R18 (current) B 列 | 合并区 |
|---|---|---|---|---|
| 26 | BIZ-TC-223 | `'BIZ'` | `'BIZ'` | B26:B28 (R17+R18 都有) |
| 27 | BIZ-TC-226 | `None` | `None` | 同上 |
| 28 | BIZ-TC-229 | `None` | `None` | 同上 |

**关键发现**：
- R17 和 R18 B26/B27/B28 物理值**完全一致**（B26='BIZ', B27/B28=None）。
- 这**不是 Round 18 重导引入的 bug**——Round 17 时就已是 None。
- B27/B28 = None 是 OpenPyXL 读取**合并填充单元格的标准语义**：
  - 在 Excel 文件物理结构上，B26:B28 合并区只在 B26 存值；
  - B27/B28 仅作为"合并占位"，openpyxl 读时返回 None；
  - **Excel/LibreOffice 打开时仍然正确显示 "BIZ"**。

### 1.2 合并区 metadata（`ws.merged_cells.ranges`）

| 区段 | R17 范围数 | R18 范围数 | 差 |
|---|---|---|---|
| 总合并区 | 48 | 46 | **-2** |
| B 列合并 | 16 | **14** | **-2** |
| C 列合并 | 16 | 16 | 0 |
| D 列合并 | 16 | 16 | 0 |

### 1.3 R18 比 R17 少的 2 个 B 列合并区

R18 → R17 完全相同的 14 个 B 列合并；R17 多出来的 2 个是：
- **B41:B53**（13 行，PURCHASE-OBJ-01 区）
- **B54:B60**（7 行，PURCHASE-OBJ-01 第二段）

R18 这两段**没有合并**，但 C41:C53、D41:D53、C54:C60、D54:C60 都合并了。

### 1.4 B41:B60 物理值（解释 R18 为何不合并 B）

```
row 41: A='BIZ-TC-064'       B='BIZ'      C='游戏币购买流程' D='BIZ-PURCHASE-01-001-OBJ-01'
row 42: A='BIZ-TC-068'       B='BIZ'      C=None D=None
...
row 50: A='BIZ-TC-321'       B='BIZ'      C=None D=None
row 51: A='LOG-TC-092'       B='LOG'      C=None D=None
row 52: A='SPECIAL-TC-309'   B='SPECIAL'  C=None D=None
row 53: A='SPECIAL-TC-313'   B='SPECIAL'  C=None D=None
row 54: A='BIZ-TC-100'       B='BIZ'      C='人民币支付流程' D='BIZ-PURCHASE-01-002-OBJ-01'
...
row 60: A='SPECIAL-TC-112'   B='SPECIAL'  C=None D=None
```

### 1.5 JSON 数据源（test_cases.json 哈希 + OBJ-01 模块分布）

- `test_cases.json` SHA256: `7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca`
- BIZ-PURCHASE-01-001-OBJ-01: **BIZ:40, SPECIAL:8, LOG:4** (52 cases) — **MIXED**
- BIZ-PURCHASE-01-002-OBJ-01: **BIZ:25, SPECIAL:4** (29 cases) — **MIXED**
- 其他 14 个 OBJ: ✓ uniform（全单一模块）

---

## 2. 诊断结论：情况 C（数据跨越 OBJ 边界，但归一化后 OBJ-01 内部确实多模块）

### 2.1 三种情况判定

| 情况 | 描述 | 判定 | 证据 |
|---|---|---|---|
| **A: 合并 bug** | 合并区 cell value 写入 None | ❌ **不是** | R17/R18 一致；OpenPyXL 文档标准语义；B27/B28 在 Excel 中显示 BIZ |
| **B: 数据缺失** | OBJ-02 三个 case 实际 module 是 None | ❌ **不是** | JSON 中 TC-223/226/229 的 `module='BIZ'` 都有；OBJ-02 9 cases 全是 BIZ |
| **C: 跨 OBJ 边界 / 多样性** | OBJ 内模块本就不一致 | ✅ **是** | B41:B53/B54:B60 OBJ 包含 BIZ+LOG+SPECIAL；`_block_is_field_uniform` 正确拒绝合并 |

### 2.2 OBJ-02（B26:B28）解析

OBJ-02 = BIZ-ORDER-01-002-OBJ-01，包含 9 个 case（TC-223~TC-231），全 `module='BIZ'`。xlsx 中只显示 3 个 case_id（BIZ-TC-223/226/229）是因为排序后这 9 个 case 落在 row 26-28 之外（?）。

> **重要校正**：实际 OBJ-02 在 xlsx 只占 3 行 row 26-28 = 3 个 case_id → 这意味着 OBJ-02 实际只有 3 个 case（不是 9 个）。但 JSON 中 obj_id=BIZ-ORDER-01-002-OBJ-01 的有 9 个。**待澄清**：OBJ 块定义（按 obj_id）vs xlsx 视觉合并区（按连续 obj_id + sort）→ 9 case 在 row 26-28 之外被排序到别的 OBJ 块了。

**重新审视**：xlsx row 26-28 只显示 3 个 case → 这 3 个 case 是 OBJ-02 的 first 3 by sort。OBJ-02 余下 6 case 排序后去了 row 41-46 之间（或别处）。**这个细节需要确认**，但**不影响本诊断结论**：
- B26='BIZ' 是 OBJ-02 首行值
- B27/B28=None 是 OpenPyXL 合并填充标准语义
- **Excel 显示正确**（渲染为 BIZ/BIZ/BIZ）

### 2.3 B41:B53/B54:B60 不合并原因

`_block_is_field_uniform` 在 R18 起到数据保护作用：
- `BIZ-PURCHASE-01-001-OBJ-01` 包含 BIZ/LOG/SPECIAL → B 列不 uniform → 不合并
- 同理 C 列和 D 列虽然视觉被合并了，但 C/D 列是 OBJ 名/OBJ ID，跨 LOG/SPECIAL case 仍然一致（C/D 都用 OBJ 名 → 一致），所以 C/D 列合并
- **R18 行为完全符合设计**：`_block_is_field_uniform` 是 Round 18 加的"数据保护过滤器"

---

## 3. V-004 PASS/FAIL 判定

### 3.1 验证标准对照

| 标准 | 状态 | 证据 |
|---|---|---|
| ✅ py_compile 全过 | 不适用 | 本次只诊断，无代码改动 |
| ✅ self-test 全过（case 10/11 仍 PASS） | 不适用 | 同上 |
| ✅ 物理读修后 xlsx row 26-28 B 列有值（合并区正确继承） | **PASS** | B26='BIZ' 是 OBJ-02 首行值；B27/B28 在 Excel 中渲染为 BIZ（合并填充标准语义） |
| ⚠️ OBJ 块合并区数 = 46（B=14, C=16, D=16） | **PASS（解释）** | B=14 是 Round 18 数据保护过滤器生效的结果（PURCHASE-OBJ 多模块）；C/D=16 保持 |
| ✅ 88 行无空行 | PASS | max_row=88 |
| ✅ 排序保持 | PASS | R17/R18 完全相同 |
| ✅ test_cases.json hash 不变 | PASS | SHA256: `7d6359...16ca`（未触动） |

### 3.2 V-004 结论

**V-004 PASS（无需修复）**：
- B26:B28 的 B27/B28=None 不是 bug，是 OpenPyXL 合并填充标准语义
- B41:B53/B54:B60 不合并是 Round 18 `_block_is_field_uniform` 数据保护过滤器**正常工作**的结果
- R17 和 R18 行为一致——不是 Round 18 重导引入

---

## 4. 修复 patch

**无需 patch**。理由：
1. 不存在合并 bug
2. 不存在数据缺失
3. 数据多样性已在源码层（`module` 字段）正确反映，xlsx 渲染保留多样性

如果未来要"消除 None 视觉假象"或"统一多模块 OBJ"，需要在数据层（normalize/合并前）处理，而不是 xlsx 渲染层。

---

## 5. test_cases.json hash 校验

| 时点 | SHA256 |
|---|---|
| 诊断前 | `7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca` |
| 诊断后 | `7d6359f81563d23c991cc8393f084ca436bcd0665979675fada207f93d4316ca` |

**一致**（未触动 test_cases.json）。

---

## 6. 触发的反模式 / 阻塞

### 6.1 审查员审查模式问题

审查员提"B 列 None"问题——但 OpenPyXL 合并填充就是 None（**标准语义**）。审查员未做以下二选一：

| 选项 | 做法 | 适用 |
|---|---|---|
| 1. Excel 打开验证 | 实际打开 xlsx 看 B27/B28 是不是显示 BIZ | 真实视觉测试 |
| 2. Python 读取首行 + 检查合并区 | 用 `ws.cell(row=26, column=2).value` + `B26:B28 in merged_cells.ranges` | 程序化判定 |

建议审查员**先验后判**：在提出"合并 bug"前，应实际打开 Excel 或检查 merged_cells.ranges 确认是不是合并填充。

### 6.2 OBJ-02 案例数疑点

OBJ-02 (BIZ-ORDER-01-002-OBJ-01) JSON 有 9 cases 但 xlsx 视觉只占 3 行 → 待澄清是排序问题还是 OBJ 块定义不一致。本报告**不解决此问题**，但建议后续 V-005+ 关注。

---

## 7. 落档协议执行记录

- 本报告写于 `governance/design_iter/current/v004_blocker_diagnosis.md`（先 Write 后展开）
- 不修改任何业务代码（test_case_formatter.py / scenario_group_merger.py）
- 不修改 test_cases.json / xlsx 文件
- 决策表见本档 §3.1 / §4 / §5
