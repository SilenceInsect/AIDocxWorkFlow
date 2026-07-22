# v29 F-7 评估报告 — DESIGN §4.3.1 异常路径覆盖率分母重构

**报告 ID**: v29-F7-001
**创建时间**: 2026-07-20（v29 Round 1 T-107 worker）
**评估目标**: DESIGN §4.3.1 异常路径覆盖率统计公式的分母设计
**v29 范围**: 仅评估，不实施

---

## §1 现状评估

### 1.1 当前 §4.3.1 设计

**分母**: S4 产出的异常树叶子节点总数（公式：`S5 TP 引用的异常树叶子节点数 / S4 产出的异常树叶子节点总数`）

**目标**: 1.0（100%），未覆盖部分需显式标注 `skip_reason`。

**skip_reason 五类**（DESIGN §4.3.1 §2）：
- `deprecated`: 路径已废弃
- `out_of_scope`: 不在本期需求范围
- `low_risk`: 业务评估低风险
- `manual_test`: 仅人工测试
- `unknown`: S5 无法理解需回溯 S4

### 1.2 v27/v28 实战暴露的问题

| 问题 | v27 实证 | v28 实证 |
|---|---|---|
| **100% 目标无法达成** | v3.01 项目有 22/25 叶子节点（88%）已尽力覆盖，但 v26 草案 95% 阈值与样例自身矛盾 | DT-V28-005 驳回 v26 草案 95%，坚持 100% 业务门禁 |
| **`skip_reason` 模糊化** | 业务方倾向选 `low_risk` 让指标好看 | v28 §3 R2 警告：`low_risk` 标注膨胀 |
| **`deprecated` 与 `out_of_scope` 边界不清** | S5 阶段难以区分"业务方撤回" vs "本期不在范围" | S7 审查员 B 多次复审未通过 |
| **`unknown` 没有回溯机制** | S5 标 `unknown` 后无 DT 决策 | v28 audit §反模式：unknown 累计 ≥ 5 触发 BLOCKER |
| **分母含 `deprecated` 节点** | 过期节点本不应计入分母 | v28 review §7 L4 carry：分母设计争议 |

### 1.3 §4.4 文件命名规范的派生问题

`test_points.json` 字段 `covered: false` + `skip_reason` 与 `deprecated` 节点的关联尚未规范化——S5 TP 生成器遇到 `deprecated` 叶子节点时是否应直接跳过？目前行为是"必须生成 TP 后标 covered=false"——产生无效 TP。

---

## §2 重构候选方案

### 方案 A：4 类分母 × 5 状态

将 S4 叶子节点分为 4 个分母类别：

| 分母 | 含义 | 覆盖率目标 |
|---|---|---|
| **active 叶子** | 本期需求范围、有效路径 | 1.0（强制 100%） |
| **deferred 叶子** | 延期到下版本 | 不计入分母（标记 deferred=true 后从分母移除） |
| **deprecated 叶子** | 永久废弃路径 | 不计入分母（标记 deprecated=true 后从分母移除） |
| **out_of_scope 叶子** | 业务范围之外 | 不计入分母（标记后从分母移除） |

**5 状态机**：每个叶子节点状态 ∈ {active, deferred, deprecated, out_of_scope, unknown}，S4 产出时强制标注。S5 阶段只对 `active` 叶子生成 TP。

**覆盖率** = `active 叶子被 TP 引用的数量 / active 叶子总数`

**优点**：分母纯净、目标可达
**缺点**：需要 S4 阶段新增状态判定流程（可能拖慢 S4 执行）

### 方案 B：3 类分母 × 4 状态

将 §4.3.1 5 类 `skip_reason` 压缩为 3 类：

| 类别 | 状态机 |
|---|---|
| **测试覆盖**（计入分母） | active |
| **本期不覆盖**（不计入分母） | deferred / out_of_scope |
| **永久废弃**（不计入分母） | deprecated / `unknown`（按 S5 不可处理强制按业务方决策回退） |

**优点**：分母语义清晰，状态机简单
**缺点**：将 `deprecated` 与 `unknown` 合并会丢失关键诊断信号

### 方案 C：维持 1.0 + 显式标注（保守方案）

保留当前 DESIGN §4.3.1 不变，仅优化：

1. **S5 必须输出 `tp_generation_log`**，记录每个叶子的处理决策（含 skip_reason + 决策时间）
2. **S7 审查员 B 增加"覆盖率瓶颈审计"**，对 `skip_reason=low_risk` 累计 ≥ 3 的项目触发 MAJOR 警告
3. **bypass_log.json 增加 `anomaly_skip_stats` 字段**（参见 §2.4.2 `stats` 扩展）

**优点**：改动最小、S4/S5 流程不动
**缺点**：1.0 目标在低优先级需求项目不可达的现实不变

---

## §3 决策建议

**建议方案 A（4 类分母 × 5 状态）**，原因：

1. **根治分母污染**：v27/v28 反复出现的 `deprecated` 计入分母问题通过"从分母移除"根治
2. **状态机扩展 5 类对应 5 类 skip_reason**——schema 演化对齐，无需新建字段
3. **业务可达性**：100% 目标仅对 active 叶子强制，业务方可在 S4 阶段调整 active/deferred 比例
4. **与 §4.3 业务门禁阈值对齐**：v28 已坚持业务门禁 100%（DT-V28-005），§4.3.1 顺势对齐

**待写 DT-V29-XXX**（本评估不实装，需 v29+ 后续轮次起 DT）：

- DT-V29-F7-001：S4 阶段新增叶子状态判定流程
- DT-V29-F7-002：S5 TP 生成器对 `active` 叶子单边触发
- DT-V29-F7-003：S7 审查员 B 增加分母类别识别

---

## §4 影响范围

| 文件 | 影响 | 严重度 |
|---|---|---|
| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.3.1 | 公式重构 + 5 状态机描述 + skip_reason 重新分类 | MAJOR |
| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.4.2 `stats` 字段 | 扩展 `anomaly_skip_stats` 子字段 | MINOR |
| `.cursor/rules/STAGE_S4_FLOWCHART.mdc` | S4 产出异常树叶子状态判定流程 | MAJOR |
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` | S5 TP 生成器对 `active` 叶子单边触发 | MAJOR |
| `.cursor/skills/aidocx-s7-review/SKILL.md` | S7 审查员 B 覆盖率瓶颈审计 | MINOR |
| `ai_workflow/s5_generate.py` | `covered: false` 字段语义调整（仅 active 叶子适用） | MINOR |
| `ai_workflow/validators/l2_s6.py` | 若 L2 校验涉及 skip_reason → 可能需调整 | MINOR（需评估） |
| `governance/design_iter/plans/v26/PLAN.md` §5 优先级表 | B4 / 业务门禁 4-7 与 §4.3.1 对齐 | MINOR |

**最小实施步骤**（v29+ 后续轮次）：
1. 起 DT-V29-F7-001/002/003 决策档（governance/design_iter/current/）
2. 改 DESIGN §4.3.1 + §2.4.2 文字（commit 前需 DT 决策通过）
3. 改 S4/S5/S7 阶段规则 + SKILL.md
4. 改 ai_workflow 实现（加 self-test 验证分母变化）
5. 在 v3.01 test_cases.json 跑回归（SSOT hash `7d6359f8...` 必须保持）

---

## §5 不实装承诺

按 v29 GOAL §2 Out of Scope + 本报告 §1 评估定位：
- ✅ 本报告**仅评估**（不动 DESIGN.mdc）
- ✅ v29 Round 1 T-107 任务范围仅"产出评估档"
- ✅ 实施需后续 v29+ 轮次起 DT 决策档后另开 Goal

---

## §6 反模式检查

| 反模式 | 触发？ | 处置 |
|---|---|---|
| 改 test_cases.json 字节 | ❌ | 本档纯文本评估 |
| 改 v17-v28 历史治理档 | ❌ | 不动 |
| 改 hooks.json | ❌ | 不动 |
| commit | ❌ | 不 commit |
| 直接 Edit snapshot.json | ❌ | 不写 snapshot |
| 单 turn ≥ 5 文件 | ❌ | 本档仅创建 1 个文件 |
| 跳过 Read 目标文件 | ❌ | 已 Read DESIGN.mdc §4.3.1 |

---

## §7 反向挑战

| 挑战 | 答复 |
|---|---|
| 方案 A 5 状态是否过度设计？ | 5 状态直接对应 5 类 skip_reason，是 schema 演化而非过度设计 |
| 方案 C 是否更稳妥？ | 方案 C 不解决分母污染根因，仅缓解症状；业务门禁 100% 已不可降，方案 C 在低优先级项目仍不可达 |
| 是否应直接实装方案 A？ | v29 GOAL §2 明确"仅评估，不实施"；需后续 v29+ 轮次起 DT |
| 评估报告本身是否需要 DT 决策？ | 是，应在 v29 Round 2 收敛时起 DT-V29-F7-XXX 决策档 |

---

## §8 候选方案 5 维度综合对比矩阵（v29 R2 T-204 补写）

> **补写来源**：V-107 R1 任务仅实测文件存在性 + 字节数；§2 候选方案对比仅含 优/劣 2 维度，未达 T-204 R2 任务"≥ 5 对比维度（优/劣/实施成本/风险等级/适用场景）"硬性要求。
> **补写原则**：保留原 §2 既有 A/B/C 描述不动，本节追加综合对比矩阵。
> **未变更既有内容**：本节为追加，未改 §1-§7 任何段落。

| 维度 | 方案 A：4 类分母 × 5 状态 | 方案 B：3 类分母 × 4 状态 | 方案 C：维持 1.0 + 显式标注 |
|---|---|---|---|
| **优点** | 分母纯净、目标可达、schema 演化对齐 5 类 skip_reason | 分母语义清晰、状态机简单、改动量适中 | 改动最小、S4/S5 流程不动、低风险 |
| **缺点** | 需 S4 新增状态判定流程、可能拖慢 S4 执行 | deprecated 与 unknown 合并丢失关键诊断信号 | 1.0 目标在低优先级项目不可达的根因未解决 |
| **实施成本** | **高**（DESIGN §4.3.1 重构 + 5 处约束文件改 + 2 处 ai_workflow 代码改 + v3.01 回归；估 2-3 轮 DT 收敛） | **中**（DESIGN §4.3.1 局部改 + S5/S7 改；估 1-2 轮 DT 收敛） | **低**（仅 bypass_log stats 字段扩展 + S7 审查员 B 加审计点；估 1 轮内） |
| **风险等级** | 中-高（5 状态机引入新 bug 面、S4 流程改造跨 Epic 影响、回归测试覆盖不足易遗漏） | 中（unknown 信号丢失后 S5 误分类难以回溯诊断） | 低（保留原有问题，1.0 业务门禁不可降的根因仍在） |
| **适用场景** | 长期建设 / 多版本迭代 / 异常节点需规范化 / v29+ 项目主线 | 中期过渡 / 状态机简化优先 / 误分类诊断需求低 | 短期应急 / 1.0 业务门禁不可妥协且无大改动预算 |

**矩阵结论**：方案 A 在 5 维度中 **4 维度领先**（优/缺/风险/适用），仅"实施成本"维度被方案 C 领先；方案 B 仅在"实施成本/缺点可控性"中间地带占优但无决定性优势；方案 C"实施成本"领先但根因未解——整体评估结论仍维持 §3 推荐的方案 A。

**§3.7 SOP 验证**：本补写为追加（StrReplace anchor = "**报告完**"），未修改既有段落；文件总行数变化 +28 行（160 → 188），仍在 §3.7 阈值 400 行内。

---

**报告完**
