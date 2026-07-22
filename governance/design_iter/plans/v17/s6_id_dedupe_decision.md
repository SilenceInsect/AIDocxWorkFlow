# S6 `case_id` vs `tc_id` 冗余 SSOT 治理决策档（A-004 follow-up）

> **决策档性质**：仅落档决策方向，不直接修改 `.cursor/skills/aidocx-s6-test-cases/SKILL.md`
> **决策人**：架构师 worker（按 user 委托全权决策）
> **决策时间**：2026-07-19
> **来源**：review_13.md §1.2 (A-004 [MAJOR]) + review_13.md §3.1 (F-1) + audit_13.md §1 (V-006)

---

## §1 现状复盘

### 1.1 v3.01 S6 test_cases.json 实际数据

每条 TC 同时含两个字段：

```json
{
  "case_id": "TC-001",
  "tc_id": "TC-001",
  ...
}
```

**验证证据**（已 Read S6 test_cases.json 331 条 TC）：

| 字段 | 取值样本 | 数量 |
|------|---------|------|
| `case_id` | "TC-001" ~ "TC-331" | 331 |
| `tc_id` | "TC-001" ~ "TC-331" | 331 |

**100% 同值同类型**——纯冗余字段。

### 1.2 SKILL 现状（aidocx-s6-test-cases/SKILL.md §六 Schema）

§100-101 模板字段表：

```
{
  "case_id": "UI-TC-001",
  "s5_ref": "TP-001",
  ...
}
```

§775-776 又写：

```
{
  "case_id": "LOG-TC-XXX",
  "tc_id": "LOG-TC-XXX",
  ...
}
```

**SKILL 内部 schema 已自相矛盾**：
- §六 默认 schema 只列 `case_id`
- §LOG 模块 seed 模板又同时列 `case_id` 和 `tc_id`

### 1.3 xlsx 输出 vs JSON

xlsx 输出"用例ID"列由 normalizer 加前缀（`TC-001` → `UI-TC-001`），**只读 `case_id` 字段，不读 `tc_id`**——意味着 `tc_id` 在 xlsx 输出链路中是死字段。

### 1.4 上下游消费方

| 消费方 | 用 `case_id` | 用 `tc_id` |
|--------|-------------|-----------|
| `ai_workflow/s6_generate.py` | ✅（主键） | ❌ |
| `ai_workflow/qa_fixer_v301.py` | ✅ | ❌ |
| `ai_workflow/case_id_and_field_normalizer.py` | ✅（归一化前缀） | ❌ |
| `ai_workflow/test_case_formatter.py` / `_save_xlsx` | ✅ | ❌ |
| `case_status_writer` | ✅ | ❌ |
| 审计 / gap_report | ✅（间接） | ❌ |
| 人工审查 | ✅ | ❌ |

**结论**：`case_id` 是事实上的唯一主键；`tc_id` 是历史遗留死字段。

---

## §2 候选方案

### 方案 A：保留 `case_id`，删除 `tc_id`

- **动作**：SKILL.md §六 Schema 删除 `tc_id` 字段；所有 v3.01 数据迁移时移除 `tc_id` 字段
- **影响**：
  - SKILL.md 实质改动：§六 Schema 删除 1 行
  - v3.01 test_cases.json 331 条均含 `tc_id`，需迁移时移除（**out_of_scope 故本轮不动 JSON**）
  - Round 15+ 新生成 TC 不再含 `tc_id` 字段
- **风险**：JSON 数据迁移需协调（属 out_of_scope）；但新数据生成路径无风险

### 方案 B：`tc_id` 改名 = `case_id`（别名共存）

- **动作**：SKILL.md 明确 `case_id` 是主键，`tc_id` 是别名（必须 == `case_id`）
- **影响**：
  - SKILL.md 仅文档调整（§六 Schema 加注释）
  - L1S6Validator 加 1 行一致性检查（`case_id == tc_id`）
  - v3.01 数据天然满足（331 条 `tc_id == case_id`）
- **风险**：本质是用文档维持冗余

### 方案 C：`tc_id` 完全删除（不留 alias）

- **动作**：SKILL.md §六 Schema 删除 `tc_id`；v3.01 数据迁移时删除字段；新数据不再生成
- **影响**：
  - 与方案 A 类似但更激进——不留任何 alias
  - L1S6Validator 加 1 行"禁止 `tc_id` 字段存在"
- **风险**：v3.01 数据迁移需先归一化（mirror 删除）；下游若有任何脚本读 `tc_id` 会立即报错

---

## §3 推荐方案 = 方案 A（保留 `case_id`，删除 `tc_id`）

### 3.1 选 A 的理由

1. **符合 §1.4 事实**：`case_id` 是唯一事实主键（xlsx / L1 / L2 / status_writer 全部只读 `case_id`）
2. **影响范围可控**：SKILL.md 改 1 行；v3.01 JSON 因 out_of_scope 不动，新数据不再生成 `tc_id`
3. **审计友好**：L1S6Validator 加 1 行"禁止 `tc_id` 字段"——机械化保证不留死字段
4. **演进路径清晰**：未来 Round 15+ 真要字段收敛时，可平滑迁移到方案 C

### 3.2 SKILL 改动建议（仅文档级）

| 位置 | 改动 |
|------|------|
| SKILL aidocx-s6-test-cases §六 Schema | 删除 `tc_id` 行（或加注释"deprecated，禁止新数据填"） |
| SKILL aidocx-s6-test-cases §LOG seed 模板（§775-776） | 删除 `"tc_id": "LOG-TC-XXX"` 行 |
| L1S6Validator | 新增 1 行："若 TC 含 `tc_id` 字段 → 报错，severity MINOR（向后兼容留缓冲）" |
| L1S6Validator (Round 15+ 强化) | 升级为 "若 TC 含 `tc_id` 字段 → 报错，severity MAJOR（强制移除）" |

### 3.3 影响范围

| 类别 | 影响 |
|------|------|
| **代码改动** | L1S6Validator 加 1 行检查；其他代码 0 改动（xlsx / formatter / status_writer 全部只读 case_id） |
| **SKILL 改动** | §六 Schema + §LOG seed 模板注释修订（约 5 行） |
| **数据兼容性** | v3.01 331 TC × `tc_id` 字段**保留**（out_of_scope 不动 JSON）；新生成 TC 不再含 `tc_id` |
| **下游消费** | 无变化 |
| **审计成本** | +1 行 L1 校验（机械化标记 tc_id 死字段），-N 行人工审查（无需手动判断冗余） |

### 3.4 上下游联动

- **s6_generate.py**：当前 LLM Prompt 让 case_id / tc_id 双填——改为只填 case_id
- **mirror_bilingual_aliases**：当前不涉及 tc_id 镜像——无需改
- **case_id_and_field_normalizer**：当前不读 tc_id——无需改
- **qa_fixer_v301**：当前 dedup_30day_refund 复合键是 `(s5_ref + feature_point_ref + test_scenario)`——不含 tc_id——无需改

**所有业务脚本均不依赖 tc_id**——方案 A 实施风险极低。

---

## §4 决策记录

| 维度 | 决策 |
|------|------|
| **采用方案** | A（保留 `case_id`，删除 `tc_id`） |
| **优先级别** | P2（不阻塞 v3.01 业务；Round 15+ 可演进到方案 C） |
| **SKILL owner** | 架构师（修订 aidocx-s6-test-cases/SKILL.md §六 Schema 注释 + L1S6Validator 死字段检查） |
| **数据迁移** | 0 迁移（v3.01 JSON 不动 out_of_scope；新数据不再生成 tc_id） |
| **验证证据** | Read v3.01 S6 test_cases.json：331/331 TC 同时含 `case_id == tc_id`，100% 同值 |
| **Round 3 Act 落地** | 仅落档本档，**不实际改 SKILL**（遵循"只落档，不改 SKILL"约束） |
| **Round 15+ 演进路径** | L1S6Validator 升级为 MAJOR（强制移除 `tc_id`）；届时 v3.01 JSON 同步移除字段 |

---

## §5 落档协议执行记录

- **DNA §9.5**：✅ Write 占位后再展开 content
- **DNA §9.4 先验后答**：✅ 已 Read aidocx-s6-test-cases/SKILL.md §六 Schema + §LOG seed + s6_generate.py + qa_fixer_v301.py + case_id_and_field_normalizer.py + S6 test_cases.json 331 TC 字段
- **改动文件清单**：本档新增 1 个决策档；SKILL / 代码 0 改动