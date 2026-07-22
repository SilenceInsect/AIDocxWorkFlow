# S5 `s5_ref` vs `tp_id` 双标识 SSOT 治理决策档（A-003 follow-up）

> **决策档性质**：仅落档决策方向，不直接修改 `.cursor/rules/STAGE_S5_TEST_POINTS.mdc`
> **决策人**：架构师 worker（按 user 委托全权决策）
> **决策时间**：2026-07-19
> **来源**：review_13.md §1.2 (A-003 [MAJOR]) + review_13.md §3.1 (F-1) + audit_13.md §1 (V-006)

---

## §1 现状复盘

### 1.1 v3.01 S5 test_points.json 实际数据

每条 TP 同时含两个字段：

```json
{
  "tp_id": "UI-TP-001",
  "test_point_id": "UI-TP-001",
  "s5_ref": "UI-TP-001",
  ...
}
```

**验证证据**（已 Read S5 test_points.json）：

| 字段 | 取值 | 数量 |
|------|------|------|
| `tp_id` | "UI-TP-001" 等 | 87 |
| `test_point_id` | "UI-TP-001" 等 | 87 |
| `s5_ref` | "UI-TP-001" 等 | 87 |

**三者 100% 同值、同类型、同语义**——纯冗余。

### 1.2 SSOT 现状（STAGE_S5_TEST_POINTS.mdc §1.9.7）

```
每条 TP 必须包含：
{
  "tp_id": "TP-001",
  "s5_ref": "TP-001",
  ...
}
```

§481 又写："S6 TC 将通过 `s5_ref` 字段（指向 `tp_id`）回溯到 S5 TP"。

**SSOT 内部已自相矛盾**：
- §1.9.7 把 `s5_ref` 列为必填字段
- §481 把 `s5_ref` 当作"指向 `tp_id` 的指针"——意味着 `s5_ref` 是引用字段，不该作为 TP 主键

### 1.3 上下游消费方

| 消费方 | 用 `tp_id` | 用 `s5_ref` | 用 `test_point_id` |
|--------|----------|-----------|-------------------|
| `ai_workflow/s6_generate.py` | ✅ | ✅（与 tp_ref 同义） | ❌ |
| `ai_workflow/qa_fixer_v301.py` | ✅ | ✅（去重复合键） | ❌ |
| `ai_workflow/case_id_and_field_normalizer.py` | ❌ | ❌ | ❌ |
| `ai_workflow/test_case_formatter.py` | ❌ | ❌ | ❌ |
| xlsx 输出 | ❌ | ❌ | ❌ |
| 审计 / gap_report | ✅（间接） | ❌ | ❌ |

**结论**：`tp_id` 是事实上的主键，`s5_ref` 与 `test_point_id` 是别名式冗余。

---

## §2 候选方案

### 方案 A：保留 `s5_ref`，`tp_id` 改 alias

- **动作**：删除 SSOT 中 `tp_id` 必填要求，保留 `s5_ref` 必填；`tp_id` 字段保留但标记 deprecated
- **影响**：
  - 所有引用 `tp_id` 的代码需改读 `s5_ref`（qa_fixer_v301 / s6_generate）
  - SSOT 实质改动：删除 `tp_id` MUST 标注
  - gap_report 不受影响（按 ID 字符串匹配）
- **风险**：当前 S5 test_points.json 已含 87 条 `tp_id`，删除要求后兼容性靠 alias 维持，复杂

### 方案 B：删除 `s5_ref`，只保留 `tp_id`

- **动作**：SSOT 删除 `s5_ref` 必填要求；S6 TC 的 `s5_ref` 引用字段统一改为 `tp_ref`
- **影响**：
  - S6 SKILL.md §6 表 "s5_ref 字段" → 改为 "tp_ref"
  - s6_generate.py / qa_fixer_v301.py / case_id_and_field_normalizer.py 需改键名
  - gap_report 不受影响（仍按 TP ID 字符串匹配）
- **风险**：v3.01 test_cases.json 已含 331 条 `s5_ref` 字段——需兼容归一化（mirror 到 `tp_ref`）

### 方案 C：双标识并存，明确分工

- **动作**：SSOT 明确 `tp_id` = 实体主键，`s5_ref` = S6 TC 反向引用别名（指针字段）
- **影响**：
  - SSOT 仅文档调整（§1.9.7 注释 + §481 措辞统一）
  - 代码无需改动
  - L1/L2 校验器加一条规则：`tp_id` 与 `s5_ref` 值必须相等
- **风险**：本质是"用文档约束代替代码清理"，长期会埋"双重真相源"风险

---

## §3 推荐方案 = 方案 C（双标识并存 + 显式约束）

### 3.1 选 C 的理由

1. **影响范围最小**：不动代码（满足本轮"只落档不改 SSOT"约束）
2. **风险最低**：兼容 v3.01 数据（331 TC × `s5_ref` 字段无需迁移）
3. **审计友好**：L1 校验加 `tp_id == s5_ref` 一致性行——机械化保证双标识一致
4. **可演进**：后续 Round 15+ 真要做字段收敛时，可平滑迁移到方案 B

### 3.2 SSOT 改动建议（仅文档级）

| 位置 | 改动 |
|------|------|
| STAGE_S5_TEST_POINTS.mdc §1.9.7 | 增加注释：`tp_id` 为主键，`s5_ref` 是 S6 反向引用别名（必须 == `tp_id`） |
| STAGE_S5_TEST_POINTS.mdc §481 | 重写为："S6 TC 通过 `s5_ref` 别名字段（== `tp_id`）回溯到 S5 TP" |
| L1S5Validator | 新增一致性行：`tp_id == s5_ref`（若不等 → 报错，severity MAJOR） |
| SKILL aidocx-s5-test-points | LLM Prompt 强调："s5_ref 字段必须 == tp_id，禁止自创" |

### 3.3 影响范围

| 类别 | 影响 |
|------|------|
| **代码改动** | L1S5Validator 加 1 行一致性检查；其他代码 0 改动 |
| **SSOT 改动** | STAGE_S5_TEST_POINTS.mdc §1.9.7 + §481 注释修订（约 10 行） |
| **数据兼容性** | v3.01 87 TP × 2 字段均满足 `tp_id == s5_ref`，无迁移成本 |
| **下游消费** | 无变化（s6_generate / qa_fixer 仍按 `tp_ref` / `s5_ref` 双读） |
| **审计成本** | +1 行 L1 校验（机械化），-N 行人工审查（无需手动验证双标识一致性） |

### 3.4 上下游联动

- **S6 SKILL.md §6 表**（"字段"列）：当前已是 `s5_ref` / `tp_ref` 共存——**已符合方案 C**，无需改
- **S6 mirror_bilingual_aliases**：当前已支持 `s5_ref` ↔ `tp_ref` 互镜——**已符合方案 C**
- **S7 审查员**：审查模板增加 1 行 "S5 双标识一致性（tp_id == s5_ref）100%"

---

## §4 决策记录

| 维度 | 决策 |
|------|------|
| **采用方案** | C（双标识并存 + 显式约束） |
| **优先级别** | P2（不阻塞 v3.01 业务；Round 15+ 可演进到方案 B） |
| **SSOT owner** | 架构师（修订 STAGE_S5_TEST_POINTS.mdc 注释 + L1S5Validator 一致性行） |
| **数据迁移** | 0 迁移（87 TP × 双字段天然一致） |
| **验证证据** | Read v3.01 S5 test_points.json：87/87 TP 同时含 `tp_id` 与 `s5_ref`，100% 同值 |
| **Round 3 Act 落地** | 仅落档本档，**不实际改 SSOT**（遵循"只落档，不改规则"约束） |
| **Round 15+ 演进路径** | 如需收敛：实施 §2 方案 B（删除 s5_ref，统一为 tp_ref），需 SSOT + s6_generate + qa_fixer_v301 + case_id_and_field_normalizer 4 文件协调改动 |

---

## §5 落档协议执行记录

- **DNA §9.5**：✅ Write 占位后再展开 content（本档为独立决策档）
- **DNA §9.4 先验后答**：✅ 已 Read STAGE_S5_TEST_POINTS.mdc §1.9.7 + §481 + S5 test_points.json + s6_generate.py / qa_fixer_v301.py 关键引用点
- **改动文件清单**：本档新增 1 个决策档；SSOT / 代码 0 改动