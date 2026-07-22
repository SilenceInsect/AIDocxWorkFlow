# AIDocxWorkFlow 方案 v11 — FP 全覆盖门禁（S5 TP + S6 TC 双层 FP 引用 + 1:N 拓宽规则）

> ⚠️ **本方案已被 v12 替代（obsoleted by v12, 2026-07-10 02:02）**。
> **替代原因**：v11 的 FP 全覆盖是静态拆解（FP 来自 S2 OBJ.feature_points），不能保证 UI TC 覆盖 S3 prototype.md 的 UI 节点、不能保证 BIZ TC 覆盖 S4 business_flow.md 的 4 层引用。
> **替代方案**：见 `governance/design_iter/plans/v12/PLAN.md`——v12 以 S3/S4 为 TC 来源，FP 全覆盖仅对 CONFIG/LINK/LOG/SPECIAL 模块保留。
> **数据状态**：v11 期间修改的 S5/S6 数据（test_points.json + test_cases.json）**暂不重生成**——v12 规则调整到位后再处理（用户 2026-07-10 02:02 明确"不保留，但不需要立刻重新生成，等规则调整到位再处理"）。
> **保留价值**：本档 `_validate_obj_fp_linkage()` 函数保留作为 v12 辅助验证工具（CONFIG/LINK/LOG/SPECIAL 模块仍适用）。

---

# 原 v11 内容（保留作为历史记录）

> **本方案承接 v10 §3 遗留（v10 实战 1 条：FP 全覆盖未落地）+ 用户 2026-07-10 01:54 明确指令「S2需求拆解的对象全覆盖。需求对象的功能点全覆盖。写入S5和S6的产出门禁」**。
> **核心动作**：4 大议题 = (1) S5 TP 必须引用 feature_point_id (2) S6 TC 必须追踪到 1:N 拓宽 (3) OBJ + FP 双层 100% 覆盖率门禁 (4) L3 自动化兜底脚本。
> **版本号说明**：v10 = OBJ 单层覆盖；v11 = OBJ + FP 双层覆盖（v10 派生，更严格档位）。

---

## ⚠️ 启动必读：v11 决策清单

> v11 包含 **4 大议题 / 5 子决策**——本档列出全部，决策详情见 `decisions.json`。

| Q 区段 | 议题 | 决策类型 | 候选 | 选择 |
|---|---|---|---|---|
| **Q-V11-001** | S5 TP 是否必须带 feature_point_id | 输出契约 | A: 必填 / B: 选填 / C: 无要求 | **A（必填，硬约束）** |
| **Q-V11-002** | S6 TC 是否必须能追溯到 S5 TP | 链路契约 | A: 必填 s5_ref / B: 选填 / C: 仅 OBJ 引用 | **A（必填 s5_ref 字段，TC → TP 追溯）** |
| **Q-V11-003** | FP 覆盖率门禁阈值 | 阈值决策 | A: 100% / B: 90% / C: 配置项 | **A（100%，与 OBJ 覆盖率同档）** |
| **Q-V11-004** | 未覆盖 FP 处理方式 | 容错决策 | A: skip_reason / B: 强制阻断 / C: warning | **A（5 类 skip_reason 复用 OBJ 表）** |
| **Q-V11-005** | 现有 38 个 TC 映射策略 | 数据回填 | A: 沿用现有 / B: 全部重审 / C: 沿用现有+补缺 | **B（全部重审——用户明确"现有的不一定对"）** |

**用户决定（2026-07-10 AskQuestion）**：Q-V11-001=A / Q-V11-002=A / Q-V11-003=A / Q-V11-004=A / Q-V11-005=B。

---

## v{N} 必备 3 栏

### 1. 本次 v11 解决的问题（来自 v10 §3 遗留 + 用户指令）

#### 来自 v10 §3 遗留

- ✅ **v10-LEFTOVER-006（v10 实战发现）**：HINT OBJ ID 命名规则 `HINT-001-OBJ-NN`（v11 §v11-LEFTOVER-001 跟踪）
- ⚠️ **v10 实战发现（2026-07-10 01:54）**：S6 TC 的 `feature_point_id` 仅 33/87 = 38% 覆盖率——54 个 FP 未被任何 TC 引用
- ⚠️ **S5 TP 链断**：`test_points.json`（S5）产出的 `scenario_test_points[].feature_point_ref` 字段（若已存在）与 S2 OBJ.feature_points[].id 是否对得上？**未自动化校验**
- ⚠️ **S6 TC → S5 TP 链路未硬约束**：现有 TC 没有 `s5_ref` / `tp_id` 字段，无法验证"每个 TC 都源自某个 TP"

#### 来自用户 2026-07-10 01:54 指令

> 「S2需求拆解的对象全覆盖。需求对象的功能点全覆盖。写入S5和S6的产出门禁」

**解读**：
- "对象全覆盖" = OBJ 覆盖率 100%（v10 已达成）
- "功能点全覆盖" = FP 覆盖率 100%（v11 新建）
- "写入 S5 和 S6 的产出门禁" = S5 TP 必填 `feature_point_id` + S6 TC 必填 `s5_ref` + postflight_gate 双层校验

### 2. 本次 v11 新增内容

#### Phase 1: 知识层（governance/PLAN.md）—— 本档

- ✅ v11 启动决策表（Q-V11-001 ~ Q-V11-005）
- ✅ 3 栏框架
- ✅ 双层覆盖门禁契约定义

#### Phase 2: 约束层（.cursor/skills + .cursor/rules）

- 🔄 `.cursor/skills/aidocx-s5-test-points/SKILL.md` 加 §TP 必须引用 feature_point_id 条款
- 🔄 `.cursor/skills/aidocx-s6-test-cases/SKILL.md` 加 §TC 必须引用 s5_ref 条款（v10 OBJ 链接条款基础上叠加）
- 🔄 `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` 加 §FP 必填 + OBJ 覆盖率继承
- 🔄 `.cursor/rules/STAGE_S6_TEST_CASES.mdc` 追加 §FP 追溯条款（v10 OBJ 链接条款基础上叠加）

#### Phase 3: 实现层（ai_workflow/）

- 🔄 `ai_workflow/test_case_formatter.py` 升级 `_validate_obj_linkage` → `_validate_obj_fp_linkage`：
  - **OBJ 覆盖率门禁**（沿用 v10）：`obj_linkage_coverage ≥ 1.0`
  - **FP 覆盖率门禁**（v11 新增）：`fp_linkage_coverage ≥ 1.0`
  - **TC → TP 链路门禁**（v11 新增）：每个 TC 有 `s5_ref` 字段
- 🔄 新增 S5 端 `_validate_tp_fp_linkage()`（TC 之前的 TP 阶段校验）
- 🔄 接入 `postflight_gate.json` 新增 `obj_fp_linkage_gate` 项（合并两个覆盖率）

#### Phase 4: 数据层（workflow_assets/游戏道具商城系统/v3.01）

- 🔄 **重审现有 38 个 TC**：逐条对照 FP，检查 `feature_point_id` 是否**真**匹配 TC 验证的业务意图
- 🔄 标注错配的 TC（`feature_point_id` 与 TC 内容不匹配）：
  - 改 `feature_point_id` 到正确 FP（如果 FP 已被另一 TC 引用 → 加新 TC）
  - 加 `skip_reason=wrong_fp_assignment` 并迁移 TC 到正确 FP
  - 删除孤 TC（如果该 FP 不应有 TC）
- 🔄 补齐缺失 FP：54 个未覆盖 FP 中，至少 1 个 TC 引用（按业务复杂度 1:1 或 1:N）
- 🔄 新增 `s5_ref` 字段：每个 TC 至少引用 1 个 S5 TP.id（`scenario_test_points[].tp_id`）
- 🔄 重生成 md / xlsx + 同步 ledger

#### Phase 5: 跟踪槽位

- 🔄 v10-LEFTOVER-006（HINT 命名规则）→ v11-LEFTOVER-001 跟踪
- 新增 v11-LEFTOVER-002~005（4 大新遗留）

### 3. 本次 v11 仍遗留的问题（→ v12 解决）

- ❓ **v11-LEFTOVER-001**：HINT OBJ ID 命名规则 `HINT-001-OBJ-NN` 正式化（v10 遗留）
- ❓ **v11-LEFTOVER-002**：FP 1:N 拓宽规则的"合理 N 上限"——目前按"每 FP 至少 1 TC"做下界，但 1 FP 是否允许多 TC？上限未约束
- ❓ **v11-LEFTOVER-003**：跨需求 FP 复用——同 OBJ 同 FP 是否能在多 req_name 下各自引用？版本如何管理
- ❓ **v11-LEFTOVER-004**：S6 TC 的 `s5_ref` 字段必填后，是否扩展为"`s5_ref` + 方法学组合"（methodology_tag 既在 TP 也在 TC 上）
- ❓ **v11-LEFTOVER-005**：L3 兜底脚本与 S5/S7 自动审查员的职责边界——`fp_linkage_coverage` 是 L3 兜底还是要进 S5/S7 主流程

---

## 双层覆盖门禁契约详细定义

### 链路结构（S2 → S5 → S6）

```
S2.requirement_objects[].feature_points[].id (87 个 FP)
 ↓
S5.test_points.scenario_test_points[].feature_point_ref (每个 TP 引用 1 个 FP)
 ↓
S6.test_cases[].s5_ref (每个 TC 引用至少 1 个 TP)
     ↓
     test_cases[].obj_id (v10) + feature_point_id (v11 = 可选，与 s5_ref 唯一源对齐)
```

### 字段溯源（每个字段必答 Q1.1/Q1.2/Q1.3）

| 字段 | 上游来源 | 校验 |
|---|---|---|
| **S5 TP.feature_point_ref** | S2 OBJ.feature_points[].id | 必填；必在 S2 OBJ.feature_points 列表中存在 |
| **S5 TP.tp_id** | LLM 自生成 | 必填；模块内唯一 |
| **S6 TC.s5_ref** | S5 TP.tp_id | 必填；必在 S5 TP.tp_id 列表中存在 |
| **S6 TC.obj_id** | S2 OBJ.id | 必填（v10）；与 `s5_ref.feature_point_ref` 推导出的 OBJ 一致 |
| **S6 TC.feature_point_id** | S2 OBJ.feature_points[].id | 由 `s5_ref` 推导（不必另存），如存则必须等于 `s5_ref.feature_point_ref` |

### 双层覆盖率门禁

```
obj_linkage_coverage = len(TC 引用的 OBJ 集合) / len(S2 OBJ 列表)     ≥ 1.0  (v10)
fp_linkage_coverage  = len(TC 引用的 FP 集合) / len(S2 feature_points 总数)  ≥ 1.0  (v11)
```

**任一不达 1.0 → S6 不合格**。

### S5 → S6 链路门禁

- 每个 TC 有 `s5_ref`（指向 S5 TP.tp_id）
- TC.obj_id == s5_ref.feature_point_ref 对应的 OBJ.id（**冗余校验**——防止 TC.obj_id 与 s5_ref 来源 FP 不一致）

### 未覆盖 FP 的 skip_reason 复用 OBJ 5 类表

| skip_reason | FP 场景示例 |
|---|---|
| `no_test_needed` | 该 FP 是配置表字段定义（仅校验声明合规，测一次即可） |
| `merged` | 该 FP 测试点已合并到其他 FP 的 TC（如 FP-1+FP-2 同时验证） |
| `manual_only` | 仅人工可测（如服务端压测场景） |
| `deprecated` | 该 FP 已被废弃 |
| `unknown` | LLM 理解不了，需回溯 S2 澄清 |

### TC → TP 1:N 拓宽规则

- **下界**：每个 FP 至少 1 个 TC 引用（强制）
- **上界**：单 FP 可以 1:N 拓宽（同 FP 不同方法学 / 不同场景）
- **规则**：`fp_linkage_coverage = 1.0` 是下界；不存在强制上限

---

## L3 自动化门禁脚本骨架

`_validate_obj_linkage` 升级为 `_validate_obj_fp_linkage`：

```python
def _validate_obj_fp_linkage(
    test_cases: list[dict],
    s5_test_points: list[dict],
    s2_objs: list[dict],
) -> dict[str, Any]:
    """S6 TC 与 S5 TP + S2 OBJ/FP 双层链接校验（v11）。"""
    obj_by_id = {o["id"]: o for o in s2_objs}
    all_fp_ids = {fp["id"] for o in s2_objs for fp in o.get("feature_points", [])}
    tp_by_id = {tp["tp_id"]: tp for tp in s5_test_points}

    # 维度 1: OBJ 覆盖率（沿用 v10）
    obj_ids_referenced = set()
    for tc in test_cases:
        if tc.get("obj_id") and tc.get("obj_id") in obj_by_id:
            obj_ids_referenced.add(tc["obj_id"])

    # 维度 2: FP 覆盖率（v11 新增）
    fp_ids_referenced = set()
    for tc in test_cases:
        s5_ref = tc.get("s5_ref")
        if s5_ref and s5_ref in tp_by_id:
            fp_ref = tp_by_id[s5_ref].get("feature_point_ref")
            if fp_ref in all_fp_ids:
                fp_ids_referenced.add(fp_ref)

    obj_coverage = len(obj_ids_referenced) / len(obj_by_id) if obj_by_id else 1.0
    fp_coverage = len(fp_ids_referenced) / len(all_fp_ids) if all_fp_ids else 1.0

    # 维度 3: TC → s5_ref 链路门禁（v11 新增）
    tc_missing_s5_ref = [tc["case_id"] for tc in test_cases if not tc.get("s5_ref")]

    return {
        "passed": (
            obj_coverage >= 1.0
            and fp_coverage >= 1.0
            and not tc_missing_s5_ref
        ),
        "obj_linkage_coverage": round(obj_coverage, 4),
        "fp_linkage_coverage": round(fp_coverage, 4),
        "missing_s5_ref": tc_missing_s5_ref,
        "uncovered_s2_objs": sorted(set(obj_by_id) - obj_ids_referenced),
        "uncovered_s2_fps": sorted(all_fp_ids - fp_ids_referenced),
    }
```

---

## 关键引用

| 内容 | 路径 |
|---|---|
| v10 决策表（OBJ 链接强制条款）| `governance/design_iter/plans/v10/PLAN.md` |
| v11 决策清单 | `governance/design_iter/plans/v11/decisions.json` |
| v11 启动决策表 | `governance/design_iter/plans/v11/q_decision_table.md` |
| v11 遗留问题 | `governance/design_iter/plans/v11/open_questions.md` |
| S5 SKILL（拟入） | `.cursor/skills/aidocx-s5-test-points/SKILL.md` |
| S6 SKILL（拟入） | `.cursor/skills/aidocx-s6-test-cases/SKILL.md` |
| S5 规则字段定义（拟入） | `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` |
| S6 规则字段定义（拟入） | `.cursor/rules/STAGE_S6_TEST_CASES.mdc` |
| L3 兜底脚本（拟入） | `ai_workflow/test_case_formatter.py` |
| 当前数据现状 | `workflow_assets/游戏道具商城系统/v3.01/「S2 需求拆解」/requirement_objects.json`（25 OBJ / 87 FP）|
| 当前 S5 产物 | `workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」/test_points.json` |
| 当前 S6 产物 | `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`（38 TC，FP 覆盖率 38%）|

---

## 执行记录（待补充）

> 本节在 v11 执行过程中追加，记录每阶段实际改动文件清单。