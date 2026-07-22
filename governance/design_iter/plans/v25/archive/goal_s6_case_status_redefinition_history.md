# Goal S6 用例状态字段语义重定义 · Round 1-8 历史归档

> **本档是 `governance/design_iter/current/goal_s6_case_status_redefinition.md` Round 1-8 过程历史的归档副本。**
> - **归档时间**：2026-07-19
> - **归档触发**：用户要求"整理完整 goal 目标，审核以后再启动 goal-loop 推进" → 历史过程性记录已沉淀，无需每轮都摆在 current/ 里
> - **保留价值**：Round 1-8 的用户原始语义迭代 + 阻断发现 + 决策依据；Round 9（Act）落地后将以追加方式续档
> - **后续保留**：current/ 保留 §2 现状证据 + §3 用户最终语义 + §4 决策表 + §5 改动面清单 + §6 落档协议（仅 Round 8+）+ §7 风险登记（含 §8.5）
> - **本档不维护**：归档后只读；任何修改请改 current/ 的对应章节，不要在归档档中追加

---

## 1. 用户问题归集（Round 1-7 · 原貌搬运）

### Round 1 问题（2026-07-19 早期）
> "S7 阶段 才会给 S6 的用例，"用例状态": "Draft" 改成 ready。但是 S6 就会产出 excel 版本的测试用例，拿未 ready 的 case 生成较重的 excel 用例明显不合理，这里面是怎样的设计和流程呢"

**Round 1 关键观察**：用户首次发现 S6 直接产 xlsx 不合理——Draft 不应该是 xlsx 输入状态。

### Round 2 修正
> 都不对，因为用例如果有状态，那么启用状态的用例是怎么出现的，如果 L1 和 L2 的校验会把所有的用例都改成 ready，那么，有 ready 才转 xlsx 就是多余的指标要求，有 ready = L1 和 L2 的校验通过

**Round 2 关键语义纠正**：用户否定"分两步走"，要求 Ready = L1/L2 校验通过（语义绑定）。

### Round 3 语义锁定（当前轮基线）
> 选项 c：新增 Rejected 状态（语义最完整，但要扩枚举）。通过 S7 审查不通过状态就会变更，所以 Ready 指"通过 L1/L2"，S7 如果通过状态就还是 Ready 具有传递性和一致性。

**Round 3 关键决策**：
- 状态枚举：`Draft / Ready / Rejected / Deprecated`（4 态而非 2 态）
- 传递性：Ready 一旦赋予在 S7 不介入驳回时保持 Ready
- 双 Sheet：Q3 = two-sheets

### Round 4-6 worker 阶段
- Round 4：执行落地（Round 5 启动前置验证 · BLOCKED 发现 2 项）
- Round 5：发现 2 项阻断 → A. L2 校验器不存在 / B. S7 review_report.overall 字段与现行 SSOT 冲突
- Round 6：未启动（等待用户解决阻断 B 后继续）

### Round 7 用户元层指令（关键增量 · 推翻 Round 5 路径）
- **Q1 = build-L2-first**：拒绝 Round 5 worker 做的 L1-only 降级，要求先实现 L2 校验器作为本次目标的一部分
- **Q2 = 落实 Rejected 概念并移除废弃噪音**：要求 S7 review_report.overall 类字段如有则移除
- **Q3 = two-sheets**（Round 3 已定，无需重决策）
- **Q4 = A-full**（Round 7 暂存疑）

---

## 6. 落档协议执行记录（Round 1-8 · 原貌搬运）

> 本节按 §9.5 规则 5 记录 Round 1-8 各轮实际改动。

### Round 1（探索 + 现状确认）
- 文件改动：0
- Write 调用：本占位文件 `goal_s6_case_status_redefinition.md`
- Read 调用：4 个规则/技能文件 + 2 个脚本文件
- 决策依据：用户 Round 1 问题 "S6 出 excel 不合理"

### Round 2（语义纠正）
- 文件改动：0
- 决策依据：用户 Round 2 修正"Ready = L1/L2 校验通过"

### Round 3（语义锁定 + 决策表）
- 文件改动：0（仅占位文件）
- 决策依据：用户 Round 3 选项 c + 传递性规则
- AskQuestion 4 个决策点：Q1=L1+L2 / Q2=S7-FAIL-or-MAJOR / Q3=two-sheets / Q4=A-full（用户全量授权）

### Round 4（执行落地 · Round 5 启动前置验证 · BLOCKED 发现 2 项）
- 落档文件已写：`governance/design_iter/current/goal_s6_case_status_redefinition.md`
- 待执行 9 文件改动清单见 current/ §5
- **Round 5 前置验证发现 2 项阻断**：

#### 6.1 阻断项 A：L2 校验器不存在（Q1 必须降级为 L1-only） · Round 7 已被用户否决降级

- **Round 5 验证方式**：
  - Glob `ai_workflow/validators/l2_*.py` → 0 文件
  - Glob `ai_workflow/validators/*.py` → 仅 `l1_s1/s2/s3/s4/s5/s6/s7.py`，**无 L2 任何实现**
  - 全仓库 grep `L2S6Validator|l2_s6` → 0 命中（仅在 v17 决策档出现）
- **Round 5 降级方案（已被 Round 7 用户否决）**：
  - Q1 降级为 **L1-only**：`Ready = L1 PASS`
  - L2 校验器留空（本次不实现）
- **Round 7 用户决策（当前基线）**：Q1 = build-L2-first——**拒绝降级**，要求本次目标必须实现 L2 校验器
- **Act 阶段落地动作**：新增 `ai_workflow/validators/l2_s6.py`（80-120 行）

#### 6.2 阻断项 B：S7 `review_report.overall` 字段与现行 SSOT 冲突 · Round 7 元层指令已落档为 §4.2-Q2-decision

- **Round 5 验证方式**：
  - Read `.cursor/skills/aidocx-s7-review/SKILL.md` L160 → `❌ 旧格式 overall_pass: true/false 禁止出现——已废弃`
  - Read `.cursor/rules/STAGE_S7_REVIEW.mdc` L305-308 → `❌ overall_pass: true/false 字段 / ❌ 整体判决：PASS / FAIL 行`
  - Read `.cursor/rules/STAGE_S7_REVIEW.mdc` 执行卡 L455 → `overall_assessment 不能含 PASS/FAIL 字样`
- **Round 7 元层指令落档**（§4.2-Q2-decision）：
  - Rejected 触发条件改为依赖 `recommendations.must_fix[].id` 任一非空——与现行 S7 SSOT 完全一致
  - **落实"移除废弃噪音"**：移除 `reviewer_a.overall_assessment` 字段引用（auto_reviewer.py 实际不写入此字段，但 SKILL.md L129 仍允许 LLM 填——**SSOT 与代码不一致的废弃残留**）
  - `overall_pass` 字段已完全废弃（无需操作，auto_reviewer.py 不输出）

### 6.3 Round 5 进度

- 前置验证：已完成（2 项阻断均已识别）
- 代码改动：未启动（等待用户决策解决阻断 B 后继续）

### 6.4 Round 7 用户决策明确化（2026-07-19 · 当前基线）

- Q1 = build-L2-first（拒绝 Round 5 worker 的 L1-only 降级；要求先实现 L2 校验器）
- Q2 = 落实 Rejected 概念并移除废弃噪音（元层指令）
- Q3 = two-sheets（Round 3 已定）
- Q4 = A-full（暂存疑——用户后续可改 B/C/D）

### 6.5 Round 8 Plan 阶段执行（本轮 · 2026-07-19）

- 文件改动：1（本落档文件全文重写）+ 1（`.goal-log-db/active/bad7a7fa-4135-42c2-9a9e-b5233cb454d5/snapshot.json`）+ 1（`.goal-log-db/active/bad7a7fa-4135-42c2-9a9e-b5233cb454d5/out_of_scope.md`）
- 决策依据：用户 Round 7 元层指令 + 用户最新决策"整理完整 goal 目标，我审核以后再启动 goal-loop 推进"
- **核心动作**：
  1. Read `aidocx-s7-review/SKILL.md` 全文 → 列出 S7 review_report JSON Schema 字段
  2. Read `STAGE_S7_REVIEW.mdc` 全文 → 同上 + 执行卡
  3. Grep `ai_workflow/auto_reviewer.py` → 实测产出字段（dict 形式 recommendations，非数组形式）
  4. Grep `ai_workflow/validators/l1_s7.py` → 实测消费字段（must_fix[].id 校验逻辑）
  5. **Step 2 排查结论** 落档到 §4.2-Q2-decision
- **value_ratio 校验结果**：
  - V 数 = 7（V-001..V-007）
  - P 数 = 5（P-001..P-005）
  - ratio = 7/12 ≈ 0.583 < 0.6 ——**未达硬约束**
  - **未达原因**：V-007「用户审核本 Plan 通过」是元价值（必须算 V 位），无法转 P
  - **处理方案**：本轮按 §9.5 落档协议在 §3.1 标注 `[推理补全]` 标记 + 在本节（§6.5）说明放宽理由；待用户审核 Plan 时同步决定是否接受 ratio 放宽
- **关键风险**：用户 Round 7 说"我审核以后再启动 goal-loop 推进"——意味着本 Plan 阶段产出后用户要审核，**不直接进入 Act**
- **goal_signature 计算**（GL-009）：
  - 算法：`hashlib.sha256(raw_user_goal.encode("utf-8")).hexdigest()`
  - 输入：`raw_user_goal` 字段（Round 1-7 用户原文汇总，含语义锁定 + L2-first + 移除废弃噪音元指令）
  - 结果：`a1a81723703c0217de53384f0a82525d82f9df288d1d9cf33ed1a39298c71454`（sha256 hex64）
- **下一步等待**：用户审核本 Plan 通过 → 启动 Act 阶段（按 task_queue T-001 起始）

### 6.6 隔离版本测试计划（基于 build-L2-first 基线）

- 测试 mini 需求将通过 `resource/test_s6_status/` 路径（**待创建**——目前该目录不存在）
- mini 需求：5 OBJ + 10 TP + 20 TC（覆盖 L1 PASS / L1 FAIL / L2 PASS / L2 FAIL 四象限）
- 端到端测试流程：
  1. 落档 mini 需求到 `resource/test_s6_status/v1.0_raw.md`
  2. S6 生成 → L1 + L2 校验 → case_status_writer → 检查用例状态
  3. 验证：L1 PASS ∧ L2 PASS → Ready；任一 FAIL → Draft
  4. 跑 S7 评审（注入 mock must_fix）→ s7_status_writer → 验证 Rejected 转换

---

## 7. 执行前置验证（Act 启动前完成）

| 验证项 | 验证方式 | 失败处理 |
|---|---|---|
| L2 校验器是否存在 | glob `l2_s6.py` / `L2S6Validator` | 不存在则本次方案阻断——L2 校验器是 Q1 的必交付物 |
| l1_s6.py self-test 可跑 | `python3 -m py_compile` + `--self-test` | 编译失败 → 不动代码 |
| xlsx 模板是否含"用例状态"列 | Read `knowledge/project_local/.review_queue/s6/export_profiles/test_cases.export.example.json` | 已确认含（第 13 行） |
| review_report.json 推荐形式 | `auto_reviewer.py` 实测产出 `recommendations` 是 dict 形式 | 与 SSOT SKILL.md L162 数组形式不一致——**SSOT 文档需同步修正为 dict 形式（Act 阶段落地）** |

---

## 8. 风险登记

| 风险 | 等级 | 缓解 |
|---|---|---|
| L2 校验器当前不存在，Q1=L1∧L2 双通过 → Ready 链路断 | HIGH（Round 7 升级） | Q1=build-L2-first（用户拒绝降级）；Act 阶段必须新增 l2_s6.py |
| 修改 10 个文件超 §9.1 红线 7 个——若中途用户改主意 | MEDIUM | 单文件可逆，逐文件推进，每文件改动后 `git diff` 验证 |
| 现有 v3.01 test_cases.json 全是 Draft → 全量跑一遍后变 Ready，会动到下游产物 | MEDIUM | 必须先在隔离需求版本上验证（如 `resource/test_s6_status`），不直接动 v3.01 |
| `Rejected` 是新枚举，遗留 v3.01 数据的语义是 `Draft` 而非 `Rejected`，迁移脚本要不要写？ | LOW | 决策点 Q5：保留枚举兼容性 → 旧 Draft 保留 + 不主动重写 |
| SSOT SKILL.md L162 写 `recommendations[]` 数组形式 vs auto_reviewer.py 实测 dict 形式不一致 | MEDIUM | Act 阶段需同步修正 SKILL.md L162-177 文档为 dict 形式 |
| 移除 `reviewer_a.overall_assessment` 残留字段 → 是否影响 LLM 审查输出？ | LOW | auto_reviewer.py L592-611 已不输出此字段，移除 SSOT 引用是纯文档清理 |
| value_ratio = 0.583 < 0.6 硬约束 | MEDIUM | §6.5 已说明元价值（用户审核）必须占 1 个 V 位；待用户审核 Plan 时同步决定是否接受 ratio 放宽 |

### 8.5 Round 7 发现的额外风险（已落档为 current/ §4.2-Q2-decision）

| 风险 | 等级 | 缓解 |
|---|---|---|
| **S7 `reviewer_a.overall_assessment` 字段 SSOT 残留**：SKILL.md L129 允许 LLM 填、STAGE_S7_REVIEW.mdc 执行卡列 MUST，但 auto_reviewer.py L592-611 不写入此字段——**SSOT 文档与代码不一致** | LOW | §4.2-Q2-decision 落实：Act 阶段删除 SKILL.md L129 / STAGE_S7_REVIEW.mdc 执行卡 MUST 列表中 `overall_assessment` 字段引用 |
| **落档决策表执行前未完成用户复审**：Round 5 直接在落档文件中改了 §4.1 + §4.3，未先与用户确认 → Round 7 用户已否决降级路径 | HIGH | Round 8 Plan 阶段产出 snapshot + out_of_scope + task_queue 后即停，**不进入 Act**——用户审核通过后再启动 |

---

## 附：本档与 current/ 的对应关系

| 本档章节 | 对应 current/ 章节 | 处置 |
|---|---|---|
| §1 用户问题归集 | （current/ 已删除此节） | 历史归档 |
| §6.1-6.6 落档执行记录 | current/ §6 仅保留 Round 8+ | 历史归档 |
| §7 执行前置验证 | （current/ 已删除） | 历史归档 |
| §8 + §8.5 风险登记 | current/ 保留 §8 + §8.5 | current/ 与本档同步（current/ 为现行活跃版） |
| §4 决策表 | current/ §4 | **不归档**——Round 7 基线活跃版 |
| §5 改动面清单 | current/ §5 | **不归档**——Act 阶段执行依据 |
| §2 现状证据 | current/ §2 | **不归档**——SSOT 引用基础 |
| §3 用户最终语义定义 | current/ §3 | **不归档**——Round 3 语义锁定 |

---

*归档执行：2026-07-19 · 由只读扫描 worker 完成*
*触发：用户要求"整理完整 goal 目标，审核以后再启动 goal-loop 推进" → 历史沉淀不再每轮摆在 current/*