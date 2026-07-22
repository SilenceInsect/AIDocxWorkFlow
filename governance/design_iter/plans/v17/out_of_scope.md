# out_of_scope.md — Round 16 集中归档（v3.01 守卫规则）

> **本档**：Round 16 FU-3 产物——把"v3.01 byte-lock + v3.01 xlsx 字节不变 + v3.01 dict repr=0 不得回潮"3 条规则集中归档。
> **继承**：继承 `.goal-log-db/active/32a8ff45-.../out_of_scope.md` 3 类禁区（功能 / 技术栈 / 职责边界）。
> **作用域**：v3.01 守卫规则集（FU-3 出处）；未来 Round 引用本档作为 SSOT。

---

## 1. v3.01 byte-lock 守卫规则（Round 16 集中）

### 1.1 守卫清单（3 条核心规则）

| 编号 | 规则 | 来源轮次 | 触发条件 | 违反处理 |
|---|---|---|---|---|
| **G-001** | **v3.01 test_cases.json 字节级不变**（338192 bytes） | Round 12 → Round 15 多次重申 | 任何文件改动、归一化、删字段、加字段 | 立即停手；改 v3.02 目录 |
| **G-002** | **v3.01 test_cases_public.xlsx 字节级不变**（41572 bytes） | Round 13 → Round 15 多次重申 | 任何导出、重新生成、状态写回 | 立即停手；改 v3.02 目录 |
| **G-003** | **v3.01 xlsx dict repr=0 不得回潮** | Round 13 e2e_audit | 任何 dict Python 对象 repr 残留（应为 0） | 立即停手；查 fixer dict→JSON 转换逻辑 |

### 1.2 历史出处（Round 11~15 散落决策档）

| Round | 出处档 | 关键约束 |
|---|---|---|
| Round 11 | `.goal-log-db/active/bad7a7fa-.../snapshot.json` §out_of_scope_md | 3 类禁区（含功能禁区第 1 条：v3.01 JSON 不动） |
| Round 11 | `.goal-log-db/active/bad7a7fa-.../out_of_scope.md` §功能禁区 | v3.01 test_cases.json / xlsx 不动 |
| Round 12 | `governance/design_iter/current/goal_s6_case_status_redefinition.md §6.4.9` | v3.01 legacy 数据 L1 整批报错 → normalizer 内存幂等归一化（不动 v3.01 JSON） |
| Round 13 | `audit_13.md` §2.1 + `review_13.md` §5 | xlsx 主表行数 / Ready 计数 / dict repr=0 验证 |
| Round 14 | `round14_q_decision_table.md` §5.5 + `audit_14.md` §2.1 | test_cases.json 字节不变 + xlsx 字节不变 |
| Round 15 | `round15_q_decision_table.md` §5.2 + `audit_15.md` §2.1 | 同上（Round 14 复检 SKIPPED_STABLE） |

### 1.3 守卫检查脚本（标准化引用）

```bash
# 标准守卫检查命令（每轮 audit 必跑）
stat -f '%N: %z bytes' \
  "workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json" \
  "workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx"
# 期望：338192 / 41572

# dict repr 检查（xlsx 独立验证）
PYTHONPATH=. python3 -c "
from openpyxl import load_workbook
wb = load_workbook('workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases_public.xlsx')
main = wb['测试用例']
hdrs = [c.value for c in main[1]]
sc = hdrs.index('用例状态')
ready = sum(1 for r in main.iter_rows(min_row=2, values_only=True) if r[sc] == 'Ready')
print(f'Ready: {ready}/386')
assert ready == 386, ready
# dict repr 检查
import re
text = str([list(r) for r in main.iter_rows(values_only=True)])
dict_count = len(re.findall(r'\\{.*?:.*?\\}', text))
assert dict_count == 0, f'dict repr = {dict_count}'
print('dict repr = 0 ✅')
"
```

---

## 2. v3.02 数据迁移守卫（FU-1 预留 · Round 17 落地）

### 2.1 守卫规则

| 编号 | 规则 | 说明 |
|---|---|---|
| **G-004** | **v3.02 数据迁移走新建目录，不动 v3.01** | `workflow_assets/.../v3.02/「S6 测试用例生成」/` 为 v3.02 数据目录；v3.01 数据保留只读 |
| **G-005** | **v3.02 应用 Round 15 新 schema**（含 assertion 字段 + 删 fp_name） | LLM 推理 386 TC 的 assertion（基于 expected_results 翻译）；删除 fp_name |
| **G-006** | **v3.02 byte-lock 与 v3.01 独立** | v3.02 验收后才有 byte-lock 守卫（G-007）；迁移期间 v3.02 可变 |

### 2.2 Round 17 任务清单（待启动）

- [ ] 新建 `workflow_assets/游戏道具商城系统/v3.02/「S6 测试用例生成」/` 目录
- [ ] Read v3.01 test_cases.json（338192 bytes）
- [ ] LLM 推理 386 TC 的 assertion 字段
- [ ] 删除 fp_name 字段
- [ ] 用 `ai_workflow/test_case_formatter.py` 重导出 .md + .xlsx
- [ ] 验证 v3.02 行数 / 字段覆盖 / dict repr=0
- [ ] 验证 v3.01 字节级不变（G-001 / G-002）

---

## 3. Pipeline 集成守卫（FU-2 / FU-4 预留 · Round 17 落地）

### 3.1 守卫规则

| 编号 | 规则 | 说明 |
|---|---|---|
| **G-008** | **`stage_gatekeeper` S6 gate 段自动调 `check_assertion_completeness`** | production 模式（非 `--self-test`）自动跑 assertion 完整性校验 |
| **G-009** | **`coverage_validator` S6 gate 段自动跑 assertion 缺失统计** | gap_report 输出段加 assertion 缺失统计 |
| **G-010** | **`l1_format_validator` helpers 加 `--auto` argv 分支** | production 模式（`--auto`）自动跑全部 helpers |

### 3.2 Round 17 任务清单（待启动）

- [ ] Read `ai_workflow/stage_gatekeeper.py`（必先 Read §9.4）
- [ ] Read `ai_workflow/coverage_validator.py`（必先 Read §9.4）
- [ ] S6 gate 段加 `check_assertion_completeness` 自动调用
- [ ] `gap_report` 输出段加 assertion 缺失统计
- [ ] helpers 加 `--auto` argv 分支
- [ ] L1 self-test 加 C23（stage_gatekeeper 集成）+ C24（auto 模式接入）

---

## 4. Open Questions 守卫（FU-5 预留 · Round 17 落地）

### 4.1 当前 Open Questions 状态

`governance/design_iter/current/open_questions.md` 历史条目：

- **Q-V17-001~007**：v17 字段溯源方案 7 项（全部 Agent 默认值，用户未拍板）
- 待新增：Round 14 + Round 15 治理产生的 Q（按归档需求）

### 4.2 守卫规则

| 编号 | 规则 |
|---|---|
| **G-011** | Q-V17-001~007 由 Agent 默认填入；如需调整需用户重新拍板（沿用旧规） |
| **G-012** | Round 14 + Round 15 治理新 Q（如有）按"已解 / 未解 / 无主"分类归档 |

### 4.3 Round 17 任务清单（待启动）

- [ ] Read `governance/open_questions.md`（如有迁移到 current/）
- [ ] 按"已解 / 未解 / 无主"分类
- [ ] 已解的归档到 `governance/design_iter/archive/open_questions_resolved/`
- [ ] 未解的留 active
- [ ] 无主的标注需人工认领

---

## 5. out_of_scope 守卫检查清单（标准化）

每轮 audit 必跑（Round 14 / 15 / 16 / 17 均已遵守）：

```
□ G-001: v3.01 test_cases.json 字节级不变（338192）
□ G-002: v3.01 test_cases_public.xlsx 字节级不变（41572）
□ G-003: v3.01 xlsx dict repr=0
□ G-004: v3.02 数据迁移走新建目录（FU-1 / Round 17）
□ G-005: v3.02 应用 Round 15 新 schema
□ G-006: v3.02 byte-lock 与 v3.01 独立
□ G-008: stage_gatekeeper 自动调 assertion 校验（FU-2 / Round 17）
□ G-009: coverage_validator 自动跑 assertion 缺失统计（FU-2 / Round 17）
□ G-010: l1_format_validator helpers 加 --auto argv（FU-4 / Round 17）
□ G-011: Q-V17-001~007 默认值（FU-5 / Round 17）
□ G-012: Round 14+15 Q 按状态分类（FU-5 / Round 17）
```

---

## 6. 引用方式

| 引用方 | 引用方式 |
|---|---|
| `round16_q_decision_table.md` | §3 §3.1 引用本档 G-001 / G-002 / G-003 |
| `audit_16.md` | §2 范围合规性 引用本档守卫检查清单 |
| `review_16.md` | §1 / §3 修复方案 引用本档 G-001~G-012 |
| `CONVERGED.md`（Round 16 收敛） | §3 验收证据 引用本档守卫检查 |

---

> 本档创建时间：2026-07-19（Round 16 FU-3）
> 配套档：`governance/design_iter/current/round16_q_decision_table.md`
> 配套档：`governance/design_iter/current/CONVERGED.md`（Round 16 收敛版）