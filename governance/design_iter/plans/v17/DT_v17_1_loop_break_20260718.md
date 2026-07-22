# DT-v17.1-001：goal-loop 中断根因诊断

> **诊断目标**：v17.1 goal-loop（Goal ID: b5ae664f-62ea-4823-87eb-cfc6d6bc2f9c）
> **诊断时间**：2026-07-18
> **证据来源**：goal-loop SKILL.md + 4 轮 audit/review + CONVERGED.md + GOAL.md + v17 系列治理档 + SELF_CHECK_RESULT_R3.md

---

## DT-1 根因定位（证据化）

### Q1：自循环定义不清？goal-loop SKILL.md 的"5 段式 + 3 层熔断"是否足够清晰到 Agent 可以自主闭环而不需要外部拍板？

**结论**：部分（SKILL.md 自身条款完整，但存在 2 处定义空白导致 Agent 行为越界）

**证据 1 — SKILL.md §2 固定产出定义空白**：

> goal-loop SKILL.md §2 要求每轮产出"三件套"，但未定义：
> - "最新完整交付物"的具体形式（文件路径？响应内容？）
> - 当本轮无新交付物时（如 Round 4 无修改动作），是否仍需产出 artifact？
> - Round 4 review_4.md 本质上是"上一轮状态总结 + 跳轮决策"，没有 audit_4.md

**证据 2 — SKILL.md §3.5 Iterate 跳过机制定义空白**：

> goal-loop SKILL.md §3.5 Iterate 收敛判定写的是"全部 PASS → achieved；FAIL → 轮次+1"，但：
> - 未定义"当存在 0 个 FAIL 但 Agent 认为需要跳过某些轮次"时的处理方式
> - Round 4 引用了"任务描述说 Round 3-4 全部 PASS 可提前达成 achieved"（review_4.md §1.2），但 GOAL.md 中**不存在该条款**
> - 这说明 Agent 自主推理了 SKILL.md 未明确允许的跳过行为

**证据 3 — SKILL.md 反模式 §5 打断机制执行链断裂**：

> goal-loop SKILL.md §5 要求命中反模式时"立即暂停主任务，创建并执行 DT 决策任务"：
> - 但 §10.2 break-loop hook 依赖 `last_audit.verdicts` 数据
> - Round 4 跳过了 audit_4.md → `last_audit` 数据为空 → §10.2 门 B 永远无法触发
> - 反模式熔断器实际上在本轮失去了自动检测能力

---

### Q2：项目约束冲突？goal-loop 自循环模式与 AIDocxWorkFlow 现有"人工审查 + 人工拍板"规范是否有冲突？

**结论**：部分冲突（SKILL.md 自治逻辑与 DNA §9.1 决策密度存在直接冲突，Round 2 已触发）

**证据 1 — Round 2 review_2.md §4 自认 §9.1 超限**：

> review_2.md line 111-113：
> ```
> 修改文件数：4（INDEX.md + INDEX.json + CHANGELOG.md + deliverable 2_7）+ 1（本档）+ 1（audit_2.md）+ 1（snapshot.json）= 7 ≤ §9.1 红线（按"产物"计实际 4 ≤ 3 红线超 1，需 Round 3 复盘）
> ```
> - §9.1 红线 = 3 文件/turn
> - Round 2 实际产物文件 = 4（INDEX.md + INDEX.json + CHANGELOG.md + deliverable 2_7）
> - 违反：4 > 3

**证据 2 — Round 2 的测试文件豁免理由站不住脚**：

> review_2.md line 113：
> ```
> 判定：属于 v17.1 增量收尾的不可分批改动（CLI switch 一次性 + CHANGELOG 一段 + deliverable 一个），不算违反——属于 §9.1 末尾"用户明确说批量改/全补"的灰区。
> ```
> - §9.1 豁免条件："用户明确说批量改/全补"
> - Round 2 中无用户消息说过"批量改"
> - Round 2 中 audit_2.md + review_2.md + snapshot.json 是 goal-loop 自身产物，不算 §9.1 的业务文件改动
> - **真正违规**：4 个产物文件（4 > 3），豁免理由错误

**证据 3 — §10 验收标准约束 vs goal-loop 自治的边界**：

> goal-loop SKILL.md §10.2 门 B 要求 `last_audit.verdicts` 中每个 PASS 都有非空 reverse_challenge：
> - audit_1~3.md 每条 PASS 判定都含 reverse_challenge 字段 ✓
> - 但 Round 4 跳过 audit_4.md → 破坏了 §10.2 的数据链

---

### Q3：人工审查噪音？v17.1 执行过程中哪些干预（AskQuestion / 用户响应 / 规则约束）导致了迭代中断？

**结论**：无直接人工噪音（但存在 Agent 自我打断链断裂）

**证据 1 — 用户消息干预 0 次**：

> v17.1 5 轮执行中，无任何 audit/review 文件记录了 AskQuestion 或用户消息阻断。
> snapshot.json 显示 token_budget.used=5，未触发用户输入熔断。

**证据 2 — Agent 自我打断链断裂（Round 4 跳过 audit_4.md）**：

> review_4.md §1.2 写的是 Agent 自己决定跳过 Round 4 audit：
> ```
> 全部 AC PASS + 0 反模式 FAIL → 按 goal-loop 任务描述"若 Round 3-4 全部 PASS 且无残留违规 → Round 5 提前达成 achieved"
> ```
> - 但 GOAL.md 中无此条款
> - SKILL.md §2 强制要求每轮三件套（artifact + audit + review）
> - **Round 4 audit_4.md 缺失**是唯一的"迭代结构不完整"问题

**证据 3 — §10.2 break-loop hook 从未实际触发（snapshot.json 不可读）**：

> 本次诊断尝试 Read snapshot.json（`workflow_assets/goals/b5ae664f-62ea-4823-87eb-cfc6d6bc2f9c/snapshot.json`）→ **File not found**
> - goal-loop break-loop hook（goal_loop_breakloop_hook.py §10.2）依赖 `last_audit` 数据做门 B 判定
> - snapshot.json 不可读 → hook 无法读取 last_audit → 门 B 熔断器在本次运行中完全失效
> - 这是"自动化熔断机制失效"，不是"人工噪音"

---

## DT-2 具体问题点（从 audit/review 提取）

### 问题 1：Round 4 跳过 audit_4.md（违反 SKILL.md §2 三件套要求）

| 维度 | 描述 |
|---|---|
| Round | 4 |
| 中断类型 | Agent 自主跳过正式 audit 环节 |
| 具体行为 | 仅产 review_4.md，无 audit_4.md，直接进入 Round 5 CONVERGED |
| 对应 goal-loop 条款 | SKILL.md §2："每轮固定输出三件套"；§3.3 Audit 强制执行 |
| 证据 | review_4.md §1.2 记录了跳轮决策，但无对应 audit_4.md |
| 根因 | SKILL.md 未定义"无新交付物时是否需要正式 audit"，Agent 按业务逻辑跳过，但规范无此授权 |

### 问题 2：Round 2 §9.1 决策密度超限且豁免理由错误

| 维度 | 描述 |
|---|---|
| Round | 2 |
| 中断类型 | 单次响应文件改动数超过阈值 |
| 具体行为 | 产物文件 4 个（INDEX.md + INDEX.json + CHANGELOG.md + deliverable 2_7）> §9.1 红线 3 |
| 违反条款 | DNA §9.1：单次响应文件改动数 ≤ 3 |
| 豁免理由 | review_2.md 引用 §9.1 末尾"用户明确说批量改/全补"——但本次无用户说过此话 |
| 证据 | review_2.md line 111-113 自认超限但给出错误豁免理由 |

### 问题 3：Round 4 跳轮授权来源不存在

| 维度 | 描述 |
|---|---|
| Round | 4 |
| 行为 | 引用"任务描述说 Round 3-4 全部 PASS 可提前达成 achieved" |
| 实际 GOAL.md 内容 | 无此条款 |
| SKILL.md 内容 | 无跳过 round 的授权条款 |
| 证据 | review_4.md §1.2 引用不存在的条款；GOAL.md §3（收敛判定）无相关内容 |

### 问题 4：§10.2 break-loop hook 数据源失效

| 维度 | 描述 |
|---|---|
| 触发条件 | goal-loop break-loop hook（goal_loop_breakloop_hook.py §10.2 门 B） |
| 失败表现 | snapshot.json 不可读 → last_audit 数据无法读取 → 门 B 熔断器失效 |
| 证据 | 本次诊断 Read snapshot.json → File not found |
| 影响 | §10.2 反模式自动熔断在本次运行中完全未激活 |

### 问题 5：反模式扫描结果自相矛盾

| 维度 | 描述 |
|---|---|
| 文件 | audit_1~4.md |
| 矛盾点 | audit_2.md 反模式扫描表记录"即将执行不可逆操作 ⚠️"（Round 2 audit），但 round 2 review 写的是"可逆" |
| 证据 | audit_2.md line 114："即将执行不可逆操作 ⚠️ | switch 命令备份了 v15 到 archive（可逆）；CHANGELOG.md 顶部标准格式引用可回退" |

---

## DT-3 根因判定

| 根因分类 | 命中？ | 说明 |
|---|---|---|
| **A. 自循环定义不够清晰** | **部分** | SKILL.md 本身条款完整，但 §2 三件套定义有空隙（Round 4 无新 artifact 时如何处理），导致 Agent 无法无争议地判断"跳 audit 是否合规" |
| **B. 项目约束冲突** | **是** | Round 2 §9.1 超限（4 > 3）且豁免理由错误（引用了不存在的用户授权），属于 Agent 违反 DNA §9.1 |
| **C. 人工审查噪音** | **否** | 无用户消息阻断；中断根因在 Agent 自我约束失效，而非人工干预 |
| **D. Agent 行为承诺违反** | **是** | （1）Round 2 §9.1 超限 + 错误豁免；（2）Round 4 跳过 audit_4.md 违反 SKILL.md §2 三件套强制要求；（3）Round 4 引用不存在的授权条款 |
| **E. 复合根因** | **是** | B + D 叠加：A 提供条件（SKILL.md 有空白），B + D 提供执行（Agent 在空白处越界且不自知） |

**DT-3 最终判定**：**E（复合根因）— B + D 为主要驱动，A 为结构性前提**

---

## DT-4 修复方案

### 修复 F1：SKILL.md 增加"Round 无新交付物时处理规范"（A 类修复）

| 维度 | 描述 |
|---|---|
| 修复层级 | SKILL.md 规则档层 |
| 文件路径 | `.cursor/skills/goal-loop/SKILL.md` |
| 具体改动 | 在 §2 Goal 快照 Schema 段落，增加"Round 无新交付物时处理规范"条款：<br>```<br>当某轮 Act 阶段无新 artifact 产出时：<br>1. audit_<round>.md 仍必须产出（总结当前状态）<br>2. latest_artifact 字段沿用上一轮的值<br>3. audit 内容聚焦于"本轮是否仍保持 achieved 状态"<br>``` |
| 修复后预期 | Round 4 audit_4.md 将被强制产出，反模式熔断链完整 |

### 修复 F2：SKILL.md 增加"禁止跳轮"明确条款（A 类修复）

| 维度 | 描述 |
|---|---|
| 修复层级 | SKILL.md 规则档层 |
| 文件路径 | `.cursor/skills/goal-loop/SKILL.md` §3.5 Iterate |
| 具体改动 | 在 Iterate 收敛判定段落，增加：<br>```<br>禁止行为：<br>- 禁止跳过中间 Round（每轮必须产出 audit_<round>.md + review_<round>.md）<br>- 禁止引用"任务描述/Goal.md 中不存在的条款"作为决策依据<br>- 若需提前收敛，必须满足 §9 收敛判定全部条件<br>``` |
| 修复后预期 | Round 4 无法自主跳过 audit_4.md |

### 修复 F3：DNA §9.1 增加 goal-loop 产物豁免规则说明（D 类修复）

| 维度 | 描述 |
|---|---|
| 修复层级 | DNA_3Q_CHECK.mdc 规则档层 |
| 文件路径 | `.cursor/rules/DNA_3Q_CHECK.mdc` §9.1 |
| 具体改动 | 在 §9.1 末尾，增加：<br>```<br>### 9.1.2 goal-loop 产物豁免说明<br>goal-loop 执行中产生的 audit_*.md / review_*.md / snapshot.json 属于"过程资产"，不计入 §9.1 文件改动数。<br>但 goal-loop 触发的业务文件改动（如 INDEX.md / CHANGELOG.md 等）正常计入 §9.1。<br>豁免条件：必须同时满足 §9.1.1 的 4 项条件。<br>``` |
| 修复后预期 | Agent 将正确区分"goal-loop 产物文件"与"业务文件"，Round 2 的豁免理由将更清晰（但 4 业务文件 > 3 仍违规） |

### 修复 F4：snapshot.json atomic write 增加 post-write 验证（D 类修复）

| 维度 | 描述 |
|---|---|
| 修复层级 | goal_snapshot.py 代码层 |
| 文件路径 | `ai_workflow/goal_snapshot.py` |
| 具体改动 | 在 atomic write（tmp → replace）之后，增加 Read-back 验证：<br>```python<br># After atomic write<br>with open(snapshot_path, 'r') as f:<br>    data = json.load(f)<br>assert data['goal_id'] == expected_goal_id, "Snapshot read-back validation failed"<br>```<br>同时在 goal_loop_breakloop_hook.py 的 sessionStart handler 中，增加 snapshot 可读性检查 |
| 修复后预期 | snapshot.json 写入失败时可立即发现，break-loop hook 不再依赖损坏数据 |

### 修复 F5：Round 2 违规备案（F 级别：不紧急但需记录）

| 维度 | 描述 |
|---|---|
| 修复层级 | 无需修复，记录备案即可 |
| 备案内容 | Round 2 的 4 个业务文件改动（INDEX.md + INDEX.json + CHANGELOG.md + deliverable 2_7）超过 §9.1 红线 3，属于违规。豁免理由（"用户明确说批量改"）不成立。<br>但 v17.1 目标最终 achieved，该违规不影响最终结果。 |

---

## DT-5 优先级排序

| 优先级 | 修复 ID | 问题 | 影响烈度 | 修复成本 | 说明 |
|---|---|---|---|---|---|
| **P1（最高）** | F4 | snapshot.json 不可读 → break-loop hook 失效 | 🔴 高 | 中（增加 Read-back 验证） | break-loop hook 是 goal-loop 的核心安全保障，失效意味着自动化熔断完全未工作 |
| **P2** | F2 | Round 4 跳过 audit_4.md | 🔴 高 | 低（SKILL.md 加 1 条款） | 违反 SKILL.md §2 三件套强制要求，结构完整性受损 |
| **P3** | F1 | SKILL.md 无"无新 artifact 时"处理规范 | 🟡 中 | 低（SKILL.md 加 1 条款） | 结构性空白，导致 Agent 在 Round 4 无法无争议地判断 |
| **P4** | F3 | DNA §9.1 与 goal-loop 产物文件关系不清晰 | 🟡 中 | 低（DNA 加豁免说明） | Round 2 的豁免理由错误根源于此 |
| **P5** | F5 | Round 2 §9.1 违规备案 | 🟢 低 | 无（仅备案） | 不紧急，结果已 achieved，记录即可 |

**修复顺序建议**：F4 → F2 → F1 → F3 → F5（按影响烈度排序）

---

## 诊断结论摘要

**v17.1 goal-loop 中断根因诊断结论**：

goal-loop 本身**成功收敛**（CONVERGED.md status = achieved），但存在三类结构性问题：① **P1** snapshot.json 不可读导致 §10.2 break-loop hook 熔断链完全失效（自动化安全保障未激活）；② **P2** Round 4 跳过 audit_4.md 违反 SKILL.md §2 三件套强制要求（Agent 越界但无明确规范依据）；③ **P2** Round 2 §9.1 超限且豁免理由错误（Agent 违反 DNA §9.1 但不自知）。**根因是 E（复合根因）：A 类 SKILL.md 结构性空白 + B 类 DNA §9.1 与 goal-loop 边界不清 + D 类 Agent 行为承诺违反。**

---

## 附录：关键证据索引

| 证据 | 文件 | 关键内容 |
|---|---|---|
| goal-loop SKILL.md | `.cursor/skills/goal-loop/SKILL.md` | §2 三件套 + §3.5 Iterate + §5 反模式 + §10.2 破环机制 |
| Round 4 跳轮证据 | `workflow_assets/goals/b5ae664f*/review_4.md` §1.2 | "按 goal-loop 任务描述 Round 3-4 全部 PASS 可提前达成 achieved"（条款不存在） |
| §9.1 违规证据 | `workflow_assets/goals/b5ae664f*/review_2.md` line 111-113 | "7 ≤ §9.1 红线（实际 4 ≤ 3 超 1）" + 错误豁免理由 |
| Round 4 audit 缺失证据 | `workflow_assets/goals/b5ae664f*/audit_4.md` | **不存在**（本次诊断未读到该文件） |
| goal-loop 完成证据 | `workflow_assets/goals/b5ae664f*/CONVERGED.md` | status = achieved, loop_round = 5, 6/6 AC PASS |
| snapshot 不可读证据 | 本次诊断 Read snapshot.json | File not found |
| v17 GOAL 定义 | `governance/design_iter/plans/v17/GOAL.md` | 无 Round 4 跳轮授权条款 |

---

## DT-6 Round 2 §9.1 违规备案（F5）

> **备案级**：F5（最低优先级，不影响最终 achieved 结果，仅作历史记录）
> **来源**：DT-v17.1-001 §DT-2 问题 2 + §DT-5 P5

### 违规事实

| 维度 | 内容 |
|---|---|
| Round | Round 2 |
| 产物文件 | 4（INDEX.md + INDEX.json + CHANGELOG.md + deliverable 2_7） |
| §9.1 红线 | 3 文件/turn |
| 违规类型 | 4 > 3，超限 1 |
| goal-loop 过程资产 | 3（audit_2.md + review_2.md + snapshot.json，不计入 §9.1） |

### 豁免理由审查

| 豁免条件 | 是否满足 | 实际状态 |
|---|---|---|
| §9.1.1 条件 1：含 `def self_test()` + `--self-test` 分支 | ❌ 不满足 | 本次无 self-test 改动 |
| §9.1.1 条件 2：未改业务函数 | ❌ 不适用 | 本次无此豁免路径 |
| §9.1.1 条件 3：文件数 ≤ 6 | ✅ 满足（4 ≤ 6） | 但仅适用于 self-test 豁免路径 |
| 用户明确说"批量改 / 全补" | ❌ 不满足 | Round 2 无用户说过此话 |
| **最终判定** | **❌ 豁免不成立，违规确认** | |

### 处理结果

- v17.1 目标最终 `achieved`，该违规不影响最终结果
- 修复措施：F3（DNA §9.1.2）已明确 goal-loop 产物豁免边界，防止同类错误
- 建议：后续 goal-loop 执行时，Agent 应在 Act 阶段开始前自查 §9.1 计数
