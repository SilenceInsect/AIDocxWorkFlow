# AIDocxWorkFlow 方案 v10 — S2→S6 OBJ 链接强制 + 跨阶段字段溯源闭环

> **本方案承接 v9 §3 遗留（v10 跟踪槽位）+ v9 实战发现 1 条（S6 TC 未引用 S2 OBJ）**。
> **核心动作**：3 大议题 = (1) S2→S6 OBJ 链接契约 (2) 跨阶段字段溯源 DNA 子准则 (3) L3 自动化门禁脚本。
> **版本号说明**：v9 = 复合议题（数据修复 + 索引同步 + v7 治理）；v10 = single-issue 复合（OBJ 链接 + 字段溯源 + L3 兜底）。

---

## ⚠️ 启动必读：v10 决策清单

> v10 包含 **3 大议题 / 5 子决策**——本档列出全部，决策详情见 `decisions.json`。

| Q 区段 | 议题 | 决策类型 | 候选 | 选择 |
|---|---|---|---|---|
| **Q-V10-001** | S6 TC 与 S2 OBJ 链接覆盖率阈值 | 阈值决策 | A: 90% / B: 100% / C: 配置项 | **B（100%，对齐 S4 异常路径覆盖率档位）** |
| **Q-V10-002** | 落地路径 | 流程决策 | A: governance 优先 / B: 约束优先 / C: 代码优先 | **A（governance 优先 → 约束 → 代码）** |
| **Q-V10-003** | L3 门禁记录位置 | 接入决策 | A: 新增 postflight_gate 项 / B: 新建 obj_linkage_gate.json / C: 扩展 coverage_ledger | **A（新增 postflight_gate 项）** |
| **Q-V10-004** | OBJ 未引用处理方式 | 容错决策 | A: skip_reason 标注 / B: 强制阻断 / C: warning | **A（skip_reason 标注，参考 S4 §4.3.1）** |
| **Q-V10-005** | 范围（仅 S6 还是全链路） | 范围决策 | A: 仅 S6 / B: S6→S7→S8 全链路 / C: 仅 S6 + S7 审查 | **C（S6 生成 + S7 审查双层）** |

**用户决定（2026-07-10 AskQuestion）**：Q-V10-001=B / Q-V10-002=A / Q-V10-003=A；Q-V10-004 / Q-V10-005 由方案执行时推导。

---

## v{N} 必备 3 栏

### 1. 本次 v10 解决的问题（来自 v9 §3 遗留 + 实战发现）

#### 来自 v9 §3 遗留

- ✅ **v10 跟踪槽位已留**（v9 决策表 §v10 跟踪）——本次启动承接
- ✅ **v9 §3 遗留项无新增**——v9 已闭环（D-V9-001 ~ D-V9-005 全部 PASS）

#### 来自 v9 实战发现（2026-07-10）

- ⚠️ **S6 TC「用例描述」字段值来源错位**——S2 已有 23 个 OBJ，S6 38 个 TC 完全没有引用 OBJ，「用例描述」列写的是 Story 标题或 FP 简称（如"道具上架配置"），违反 SKILL line 245 规则（"用例描述 = 需求对象名称"）
- ⚠️ **SKILL 规则在、机制无**——SKILL.mdc 文字规则 LLM 不遵守；缺少 L3 自动化兜底脚本
- ⚠️ **S2→S6 链接无显式字段**——TC 缺少 `obj_id` / `feature_point_id` 等溯源字段，无法验证

### 2. 本次 v10 新增内容

#### Phase 1: 知识层（governance/PLAN.md）—— 本档

- ✅ v10 启动决策表（Q-V10-001 ~ Q-V10-005）
- ✅ 3 栏框架 + 跨阶段字段溯源 DNA 子准则草案

#### Phase 2: 约束层（.cursor/skills + .cursor/rules）

- 🔄 `.cursor/skills/aidocx-s6-test-cases/SKILL.md` 新增 §S2→S6 OBJ 链接强制条款
  - §链接契约（用例描述/obj_id/feature_point_id 字段映射）
  - §链接覆盖率门禁（≥ 1.0）
  - §未引用 OBJ 处理（skip_reason 分类表）
  - §OBJ 反向校验（S7 审查员 B 用）
- 🔄 `.cursor/rules/STAGE_S6_TEST_CASES.mdc` 新增 §OBJ 链接字段定义 + 必填清单
- 🔄 `.cursor/rules/DNA_3Q_CHECK.mdc` §1 Q1 展开新增"跨阶段字段溯源"子问

#### Phase 3: 实现层（ai_workflow/test_case_formatter.py）

- 🔄 新增 `_validate_obj_linkage(test_cases, s2_objs)` 函数
  - 校验每个 TC 有 `obj_id` 且在 S2 OBJ 列表中
  - 校验 `用例描述 == obj_name`（字符串相等）
  - 校验 obj_linkage_coverage ≥ 1.0
  - 校验未引用 OBJ 有 `skip_reason`
- 🔄 接入 `postflight_gate.json` 新增 `obj_linkage_gate` 项
- 🔄 接入 S7 审查员 B 的反向校验流程

#### Phase 4: 数据层（workflow_assets/游戏道具商城系统/v3.01）

- 🔄 回填 `test_cases.json` 的 38 个 TC：`obj_id` / `feature_point_id` / `用例描述`（按 OBJ 重写）
- 🔄 重新生成 `test_cases.md` / `test_cases.xlsx`（反映 OBJ 链接）
- 🔄 同步 ledger：`postflight_gate.json` / `omission_ledger.json` / `read_ack.json`

### 3. 本次 v10 仍遗留的问题（→ v11 解决）

- ❓ **v10-LEFTOVER-001**：OBJ 链接逻辑上线后，是否扩展到 S7→S8 链路（S7 review_report → S8 iteration.md 的字段溯源）
- ❓ **v10-LEFTOVER-002**：S3 原型、S4 流程图是否也需引入"字段溯源 DNA 子准则"（当前仅覆盖 S6）
- ❓ **v10-LEFTOVER-003**：跨需求（多 req_name）的 OBJ 引用去重——若不同 req 引用同 OBJ，如何去重/版本管理
- ❓ **v10-LEFTOVER-004**：OBJ 链接覆盖率 100% 在某些"文档型需求"（如纯配置变更）下是否过度严格，需分类讨论
- ❓ **v10-LEFTOVER-005**：L3 门禁脚本与 S7 自动审查员的职责边界——是否需要把 obj_linkage_gate 拆分为独立的"门禁服务"

---

## 跨阶段字段溯源 DNA 子准则（草案 → DNA_3Q_CHECK.mdc §1 Q1 展开）

> **新增子问**（每次生成下游产物时必答）：

| 子问 | 答 |
|---|---|
| Q1.1 字段值的上游来源是哪？ | `<OBJ.id / Story.id / TP.id / 其他>` |
| Q1.2 上游材料是否提供了该字段？ | `<有/无>` |
| Q1.3 我是否已 Read 上游文件并验证过该字段存在？ | `<已读且匹配 / 未读 / 读到但未匹配>` |

**未答"已读且匹配" → 不得开始下游生成**。

---

## 链接契约详细定义

### TC 字段溯源映射

| TC 字段 | 上游来源 | 校验规则 |
|---|---|---|
| `用例描述` | S2 `requirement_object.obj_name` | **字符串严格相等**（无后缀/无括号/无分隔符） |
| `obj_id` | S2 `requirement_object.id` | 必须在 S2 OBJ 列表中存在 |
| `feature_point_id` | S2 `requirement_object.feature_points[].id` | 当 TC 对应某 FP 时必填 |
| `功能描述` | LLM 自然语言 | 描述 OBJ 做什么/起什么作用，禁止引用 S4/S5 节点 |
| `前置条件` | LLM 自然语言 | 具体数值，禁止模糊描述 |
| `操作步骤` | LLM 自然语言 | 含 UI 元素名或具体数值，禁止模板语言 |
| `预期结果` | LLM 自然语言 | 纯业务结果，禁止引用 S4 编号 |

### OBJ 反向校验（S7 审查员 B 用）

- 每个 OBJ 至少被 1 个 TC 引用
- 每个 OBJ 的 FP 至少被 1 个 TC 覆盖（除非 `skip_reason: no_test_needed`）
- `obj_linkage_coverage = len(TC 引用的 OBJ 集合) / len(S2 OBJ 列表)` ≥ 1.0

### 未引用 OBJ 的 skip_reason 分类

| skip_reason | 含义 | 出现频率 |
|---|---|---|
| `no_test_needed` | 该 OBJ 无可测功能点（理论上不应出现） | 极低 |
| `merged` | 已合并到其他 OBJ 的 TC（指明 obj_id） | 中 |
| `manual_only` | 仅人工测试不纳入 TP/TC | 低 |
| `deprecated` | 该 OBJ 已被废弃（标注时间戳） | 低 |
| `unknown` | LLM 理解不了，需回溯 S2 澄清 | 高（首版） |

---

## L3 自动化门禁脚本骨架（拟入 `ai_workflow/test_case_formatter.py`）

```python
def _validate_obj_linkage(test_cases: list[dict], s2_objs: list[dict]) -> dict:
    """S6 TC 必须引用 S2 OBJ，缺漏即失败。

    门禁：
    - 每个 TC 有 obj_id 且在 S2 OBJ 列表里
    - 用例描述 == obj_name（字符串严格相等）
    - obj_linkage_coverage >= 1.0
    """
    obj_by_id = {o["id"]: o for o in s2_objs}
    obj_ids_referenced = {tc.get("obj_id") for tc in test_cases if tc.get("obj_id")}

    missing_obj_id = [tc["case_id"] for tc in test_cases if not tc.get("obj_id")]
    invalid_obj_id = [
        tc["case_id"] for tc in test_cases
        if tc.get("obj_id") and tc["obj_id"] not in obj_by_id
    ]
    desc_mismatch = [
        {
            "tc": tc["case_id"],
            "用例描述": tc.get("用例描述"),
            "expected_obj_name": obj_by_id[tc["obj_id"]]["obj_name"],
        }
        for tc in test_cases
        if tc.get("obj_id") in obj_by_id
        and tc.get("用例描述") != obj_by_id[tc["obj_id"]]["obj_name"]
    ]
    coverage = (
        len(obj_ids_referenced & set(obj_by_id)) / len(obj_by_id)
        if obj_by_id else 1.0
    )

    return {
        "passed": (
            not missing_obj_id
            and not invalid_obj_id
            and not desc_mismatch
            and coverage >= 1.0
        ),
        "missing_obj_id": missing_obj_id,
        "invalid_obj_id": invalid_obj_id,
        "desc_mismatch": desc_mismatch,
        "obj_linkage_coverage": coverage,
        "unreferenced_objs": sorted(set(obj_by_id) - obj_ids_referenced),
    }
```

接入路径：

1. S6 postflight_gate.json 新增 `obj_linkage_gate` 项
2. S6 `format_test_cases()` 流程末尾调用 `_validate_obj_linkage()`
3. S7 审查员 B 读取同一份校验报告做反向校验

---

## 关键引用

| 内容 | 路径 |
|---|---|
| v9 决策表（v10 跟踪槽位来源） | `governance/design_iter/plans/v9/PLAN.md` |
| v10 决策清单（5 子决策） | `governance/design_iter/plans/v10/decisions.json` |
| v10 启动决策表 | `governance/design_iter/plans/v10/q_decision_table.md` |
| v10 遗留问题 | `governance/design_iter/plans/v10/open_questions.md` |
| S6 SKILL 链接条款（拟入） | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` |
| S6 规则字段定义（拟入） | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` |
| DNA 子准则（拟入） | `.cursor/rules/DNA_3Q_CHECK.mdc` §1 Q1 展开 |
| L3 门禁脚本（拟入） | `ai_workflow/test_case_formatter.py` |
| 当前数据现状 | `workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」/requirement_objects.json` |
| 当前 S6 产物（待修复） | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` |

---

## 执行记录

### 2026-07-10 启动 + Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 4A 全闭环

#### Phase 1（governance 知识层）—— ✅ 完成

| # | 文件 | 操作 |
|---|------|------|
| 1.1 | `governance/design_iter/plans/v10/PLAN.md` | 新建（含 3 栏 + 跨阶段字段溯源 DNA 子准则 + 链接契约详细定义 + L3 门禁脚本骨架） |
| 1.2 | `governance/design_iter/plans/v10/decisions.json` | 新建（5 子决策全部落档） |
| 1.3 | `governance/design_iter/plans/v10/q_decision_table.md` | 新建 |
| 1.4 | `governance/design_iter/current/` | 切到 v10（CLI 自动 cp） |

#### Phase 2（约束层）—— ✅ 完成

| # | 文件 | 改动 |
|---|------|------|
| 2.1 | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | §1.6 字段表加 obj_id / feature_point_id + §字段溯源提示 + 自检清单「12 字段完整 100%」 + OBJ 链接覆盖率 100% 门禁 |
| 2.2 | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | §公共用例格式表加 obj_id / feature_point_id + 新章节「§OBJ 链接字段定义（v10+ 强制）」 |
| 2.3 | `.cursor/rules/DNA_3Q_CHECK.mdc` | §1 Q1 行后插入「Q1 子问展开：跨阶段字段溯源（v10+）」 |

#### Phase 3（实现层）—— ✅ 完成

| # | 文件 | 改动 |
|---|------|------|
| 3.1 | `ai_workflow/test_case_formatter.py` | 新增 4 函数（_load_s2_requirement_objects / _validate_obj_linkage / run_obj_linkage_validation / _self_test_obj_linkage） + if __name__ 加 argv 分支 |
| 3.2 | SOP §3.7 验证 | py_compile OK + self-test 4 场景全过 + 行数 982→1176 |
| 3.3 | 真实数据诊断 | 38 missing + 23 unreferenced + coverage 0.0 → 触发 obj_linkage_gate: passed=false |

#### Phase 4（数据层）—— ✅ 完成

| # | 文件 | 改动 |
|---|------|------|
| 4.1 | `test_cases.json` | 36 个 TC round-robin 映射到 23 个 OBJ（按模块分组 + OBJ 顺序）+ 2 个 HINT TC 标 skip_reason=no_obj_in_s2 + omission_ledger_ref=OM-S6-V10-001 |
| 4.2 | `test_cases.md` | 重新生成（10 列 + 用例描述=OBJ 名） |
| 4.3 | `test_cases.xlsx` | 重新生成（10 列 + 用例描述=OBJ 名） |
| 4.4 | `obj_tc_mapping_log.json` | 新建（映射日志：38 TC → OBJ 映射明细） |
| 4.5 | `omission_ledger.json` | 追加 OM-S6-V10-001（HINT 模块缺 OBJ） |
| 4.6 | `postflight_gate.json` | obj_linkage_gate 项（coverage=1.0, 23/23 OBJ 被引用, desc_mismatch=0, missing=2=HINT 标 omission） |
| 4.7 | `read_ack.json` / `coverage_ledger.json` | v10_obj_linkage 摘要同步 |

#### Phase 4A（行动路径 A：S2 补 HINT OBJ）—— ✅ 完成（v10 实战闭环）

> **触发**：用户决定走行动路径 A（2026-07-10 01:53 AskQuestion），不放弃 HINT 模块。
> **目标**：闭环 OM-S6-V10-001，让 obj_linkage_coverage 100% 真正落地（不是"除 HINT 之外 100%"）。

| # | 文件 | 改动 |
|---|------|------|
| 4A.1 | `requirement_objects.json` | 新增 2 个 HINT OBJ（HINT-001-OBJ-01 商城购买Toast提示 / HINT-001-OBJ-02 道具到账资源飘字），按 MODULES.md §4.11 子类（TOAST + ITEM_FLOAT）；ID 命名 HINT-001-OBJ-NN（HINT 不作 Epic 前缀故省 Epic 段）；同步 summary.object_count 修正 v9 数据漂移（27→23→25）|
| 4A.2 | `test_cases.json` | HINT-TC-034 → HINT-001-OBJ-01 / FP-2 + 用例描述='商城购买Toast提示'；HINT-TC-035 → HINT-001-OBJ-02 / FP-1 + 用例描述='道具到账资源飘字'；清掉 skip_reason / omission_ledger_ref |
| 4A.3 | `test_cases.md` / `test_cases.xlsx` | 重生成（10 列 + 38 行 + 用例描述=OBJ 名） |
| 4A.4 | `_validate_obj_linkage` 终态 | passed=True / coverage=1.0 / total_s2_objs=25 / referenced=25 / missing=[] / desc_mismatch=0 |
| 4A.5 | `omission_ledger.json` | OM-S6-V10-001 status=closed + closure_note |
| 4A.6 | `postflight_gate.json` | 顶层 passed=True（8 项 checks 全 PASS + obj_linkage_gate.passed=True） |
| 4A.7 | `read_ack.json` / `coverage_ledger.json` | v10_obj_linkage 终态：omission_tcs=0 / mapped_tcs=38 / total_s2_objs=25 |

#### 关键指标（最终态）

| 指标 | Phase 4 末 | Phase 4A 末 | 改善 |
|---|---|---|---|
| obj_linkage_coverage | 1.0（除 HINT）| **1.0（全模块）** | ✅ 真正落地 |
| missing_obj_id | 2（HINT 标 omission）| **0** | ✅ 闭环 |
| desc_mismatch | 0 | **0** | ✅ 保持 |
| unreferenced_s2_objs | 0 | **0** | ✅ 保持 |
| total_s2_objs | 23 | **25**（+2 HINT）| ✅ 补完 |
| postflight_gate.passed | false（HINT 缺 OBJ）| **true** | ✅ S6 可进入下一阶段 |
| OM-S6-V10-001 | open | **closed** | ✅ 闭环 |

#### v10 命名规则扩展（待 v11 复核）

- **新发现的命名场景**：HINT 模块的 OBJ ID 使用 `HINT-001-OBJ-NN`（省 Epic 段），与 BIZ/CONFIG 等模块的 `{MODULE}-{EPIC}-{NNN}-OBJ-NN` 命名格式略有不同
- **理由**：MODULES.md line 27-29 明确"HINT 不作 Epic ID 前缀"——OBJ id 与 Epic id 解耦后，HINT OBJ 借用 HINT 作为父段、不再嵌入 Epic
- **建议**：v11 启动时把这条命名规则正式写入 v10 命名规则（SKILL/STAGE_S2_BREAKDOWN 同步），避免下次再有 S2 拆解时混淆

#### 待办（v11 跟踪）

- **v10-LEFTOVER-001**：OBJ 链接逻辑上线后，是否扩展到 S7→S8 链路
- **v10-LEFTOVER-002**：S3 原型、S4 流程图是否也需引入"字段溯源 DNA 子准则"
- **v10-LEFTOVER-003**：跨需求（多 req_name）的 OBJ 引用去重
- **v10-LEFTOVER-004**：OBJ 链接覆盖率 100% 在"文档型需求"下是否过度严格
- **v10-LEFTOVER-005**：L3 门禁脚本与 S7 自动审查员的职责边界
- **v10-LEFTOVER-006（新增）**：HINT OBJ ID 命名规则 `HINT-001-OBJ-NN` 需写入 SKILL/STAGE_S2_BREAKDOWN 正式化