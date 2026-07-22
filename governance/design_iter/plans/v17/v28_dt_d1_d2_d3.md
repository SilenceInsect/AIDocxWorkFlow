# V-203 · F-3 D1-D3 goal-loop 早期约束精审 DT 决策清单

> **任务**：T-203 / V-203 MAJOR · worker
> **精审范围**：v26 PLAN §D 组 3 项 goal-loop 早期"人工强监督"残留约束（D1 / D2 / D3）
> **精审时间**：2026-07-20
> **先验证据**：
> - `governance/design_iter/plans/v26/PLAN_dialectic_ai_constraints_relaxation.md` §D 组（line 156-180）
> - `.cursor/skills/goal-loop/SKILL.md`（v1.2 全文 498 行）§2.1 / §2.5 / §3.1 / §3.2 / §3.3 / §3.4 / §9
> - `.cursor/hooks/dna_decision_density_check.py`（v3.1 245 行）
> - `.cursor/hooks/dna_violation_check.py`（212 行）
>
> **任务边界**：
> - ✅ 仅精审 + 写 DT 决策清单
> - ❌ 不动 SKILL.md / .py / hooks.json / v17-v27 历史治理档
> - ❌ 不 commit

---

## 精审前置判定（3 项共有）

| 项 | 草案类型 | 实际 L2 vs L3 落地 | 精审判定起点 |
|---|---|---|---|
| D1 value_ratio ≥ 0.6 强制 | 放宽 | **L2 only**（SKILL.md §2.1 line 76 + §3.1 line 197 文字约束）·无 L3 hook 校验 | L2 软约束可单边调整，治理强度可控 |
| D2 GL-009 相似度 < 0.7 阻断 | 放宽 | **L2 only**（SKILL.md §3.2 line 229-237 文字约束 + `goal_snapshot.py` 计算）·无 L3 hook 校验 | L2 软约束，但 Round 15 已实证误判 |
| D3 §3.3-§3.4 Audit/Review 每轮必跑 | 放宽 | **L2 + 部分 L3**（§10.2 breakloop 门 B 依赖 `last_audit.verdicts`；DT-v17.1 实证 F2 修复条款禁跳轮） | L3 依赖最强，单独改 SKILL.md 风险高 |

> **核心发现**：3 项均**无独立 hook 阻断**——D1 / D2 是 SKILL.md 内部 L2 文字约束，D3 间接被 §10.2 L3 机制保护。**精审建议不需要"放宽"而需要"分级"**：D1/D2 调阈值 = 低风险；D3 改频率 = 需联动 §10.2 同步。

---

## DT-V28-001 · D1 value_ratio ≥ 0.6 强制

### 触发反模式
- SKILL.md §2.1 line 76：强制占比 `value_ratio >= 0.6` 作为 Goal 启动的前置条件
- SKILL.md §3.1 line 197：Plan 阶段预检，不达标阻断启动
- **反模式形态**：硬阈值（= 0.6）+ 强制（阻断启动）+ 无分级容差——"凑出来的价值项是假的"（v26 §D 证据）

### 证据
**证据 1 — v26 §D 草案证据**（v26 PLAN line 160）：
> "v3.01 实操验证 value_criteria 5-6 条 / process_criteria 2-3 条是稳定配比；强制 0.6 让简单目标必须凑价值项"

**证据 2 — SKILL.md §2.1 line 76 文字约束**：
> `强制占比：Plan 阶段预检 len(value_criteria) / (len(value_criteria) + len(process_criteria)) >= 0.6`

**证据 3 — v0.7 → v1.1 演化轨迹**（SKILL.md line 4-6）：
> "v1.0 兼容：v1.0 创建的 Goal（仅有 accept_criteria）在 v1.1 下自动归入 value_criteria，process_criteria 置空列表，value_ratio = 1.0"

**证据 4 — L3 落地情况**：
- `dna_decision_density_check.py`：**未引用** `value_ratio` / `value_criteria` / `process_criteria`
- `dna_violation_check.py`：**未引用** value_ratio
- 结论：D1 是**纯 L2 文字约束**（仅 SKILL.md 内）

### 断点
- 简单目标（process_criteria 占主）启动即被阻断 → Agent 必须伪造价值项 → **约束本身催生反模式**（"凑价值项"）
- v3.01 Round 15 scenario 合并 = process_criteria 占主类任务（多步合并），若严格 0.6 必触发阻断
- **已实证反模式**：review_2.md line 113 自述豁免理由站不住脚（DT-v17.1-001 证据），同款问题会发生在 value_ratio 上

### 根因假设
| 假设 | 验证 | 成立度 |
|---|---|---|
| H1：阈值 0.6 在项目稳定期过高 | v3.01 实测 5-6 价值 / 2-3 过程 ≈ 0.67-0.75，0.6 是设计"安全余量"，但简单任务配比常落在 0.5-0.6 | **中**（草案提供 v3.01 配比但无每轮数据）|
| H2：阻断而非软记录导致 Agent 凑价值 | D1 草案说"凑出来的价值项是假的"，无具体案例，但符合 §5 反模式"验收标准被弱化/替换"形态 | **中** |
| H3：v1.1 的价值导向设计本身合理，但实现方式过严 | v1.1 §2.1 "外部价值校验" 概念价值大，但"强制占比"过严 | **高** |

### 候选行动
| 选项 | 描述 | 风险 |
|---|---|---|
| A. 维持 0.6 强制 | 不动 SKILL.md | 高 — v3.01 实证催生凑价值反模式 |
| B. 阈值降到 0.5 + 软记录（**草案建议**） | SKILL.md §2.1 改"≥ 0.5 指导值，不达标提醒不阻断" | 低 |
| C. 阈值降到 0.5 + 区分 Goal 类型 | 业务类（必 ≥ 0.6）/ 工程类（≥ 0.3）双档 | 中 — 引入分类逻辑 |
| D. 完全移除 value_ratio 强制 | 取消前检，由 Audit 阶段判定价值导向是否足够 | 中 — 失去前置防线 |

### 选择与依据
**选项 B（草案建议采纳）**。

**依据**：
1. **风险最低**：仅改 SKILL.md §2.1 + §3.1 文字，无 L3 hook 改动（hook 不引用此字段）
2. **保留方向性**：0.5 仍体现"价值导向优先"——不是完全放弃
3. **阻断改软记录**：契合 v26 §C1 决策密度"阻断改软记录"统一方向（草案一致）
4. **未删 v1.1 §2.1 "收敛优先级"**（"只有 value_criteria 全部 PASS 才可收敛"）——价值导向的真正把关在收敛判定而非前置占比

**SKILL.md 改动范围**（**仅精审记录，不在本任务执行**）：
- §2.1 line 76 文字：`>= 0.6 强制` → `>= 0.5 指导值，不达标仅提醒`
- §3.1 line 197 文字：`不达标时阻断 Goal 启动` → `不达标时 WARN 并继续，Audit 阶段复盘`
- **§9 收敛判定 line 419 `value_ratio >= 0.6` 维持**（这是真正的硬约束，前置占比改成软指导）

### 验证证据（待执行）
- [ ] v3.01 replay 3 个 Goal（含 Round 15 scenario 合并），按 0.5 软指导跑 → 全 PASS
- [ ] 抽样 5 个简单 Goal，value_ratio 0.3-0.5 → 不应再触发"凑价值项"现象
- [ ] 反模式案例数：若 `knowledge/public/goal_loop/antipattern_cases.jsonl` 出现"凑价值项"条目 → 阈值仍过严

### 恢复点
- SKILL.md §2.1 line 76 + §3.1 line 197 + §9 line 419 三处均可在下一轮 v{N} 回滚到 0.6 强制

---

## DT-V28-002 · D2 GL-009 相似度 < 0.7 阻断

### 触发反模式
- SKILL.md §3.2 line 229-237：每轮执行前用 `compute_similarity` 校验语义相似度，< 0.7 触发 WARN + 阻断 + `update_snapshot(goal_signature=...)` 前需人工确认
- **反模式形态**：硬阈值（= 0.7）+ 阻断 + "需人工确认"路径——在 goal-loop 自治模式下**没有"人工"可确认**

### 证据
**证据 1 — v26 §D 草案证据**（v26 PLAN line 166-169）：
> "v3.01 Round 15 scenario 合并 = 合法目标变更，但合并后 raw_user_goal 字面漂移 → 触发 0.55 相似度阻断；LLM 必须额外解释'为何合并'才能继续"

**证据 2 — SKILL.md §3.2 line 228-237**：
> ```
> 相似度 < 0.7（MIN_SIGNATURE_SIMILARITY）→ 触发 WARN + 阻断，执行
> update_snapshot(goal_signature=...) 前需人工确认
> ```

**证据 3 — SKILL.md §1 line 33-34 自治声明**：
> "breakloop hook 负责检测目标完成状态并注入续跑 reminder，不负责 model 切换"
> "/goal-loop 是 Agent 指令集触发器，不是模型切换器"

**证据 4 — Round 15 scenario 合并实证**（已知 v3.01 收敛轮次）：
- 331 单步 TC → 87 多步 TC = 合法合并
- 合并动作会让 `raw_user_goal` 字面缩短 / 改写 → 触发 0.55 < 0.7 阻断
- **已实证**：Round 15 必触发（按草案描述）

**证据 5 — L3 落地情况**：
- `dna_decision_density_check.py` / `dna_violation_check.py`：**未引用** `MIN_SIGNATURE_SIMILARITY` / `compute_similarity`
- 实际阻断由 `goal_snapshot.py`（import 在 SKILL.md line 233）执行——**L2 文字约束 + 业务代码逻辑**，非 hook

### 断点
- 合法目标变更（如 Round 15 合并）触发阻断 → 自治模式无"人工"可确认 → **要么绕过（违反§6 反模式 5"验收标准被静默替换"），要么 LLM 自答（违反"需人工确认"原则）**
- **断点 2**：若 LLM 自答"确认合法"，等于"自我确认"——GL-009 防漂移机制失效

### 根因假设
| 假设 | 验证 | 成立度 |
|---|---|---|
| H1：阈值 0.7 在合法变更时过高 | Round 15 合并后 0.55 → 阈值 0.7 命中阻断；阈值若降到 0.5，0.55 可通过 | **高**（v26 草案 + 实证）|
| H2：阻断 + 人工确认在自治模式下无解 | §1 声明"自治"，§3.2 又要求"人工确认"——逻辑冲突 | **高**（SKILL.md 内部矛盾）|
| H3：防漂移机制本身合理，但实现路径错误 | 防漂移是好设计，路径应改"软记录 + 自动信任 Act 阶段的变更说明 + Review 阶段复盘" | **高** |

### 候选行动
| 选项 | 描述 | 风险 |
|---|---|---|
| A. 维持 0.7 阻断 | 不动 | 高 — Round 15 类型变更必触发 |
| B. 阈值降到 0.5 + 软记录（**草案建议**） | 0.5-0.7 区间走"软记录 + 解释 + 用户确认"而非阻断 | 中 |
| C. 阈值降到 0.4 + 取消人工确认 | 任何 ≥ 0.4 通过，< 0.4 才阻断 | 中 — 0.4 区间漂移风险 |
| D. 改"增量更新签名"机制 | 每轮允许更新 goal_signature，更新时记录"本轮变更说明"到 `snapshot.goal_signature_changelog[]` | 低 — 保留防漂移但不阻断 |

### 选择与依据
**选项 D（优化草案）**。

**依据**：
1. **保留防漂移的工程价值**：D 选不放弃 GL-009 设计意图
2. **解决自治模式下"无人工"断点**：用"记录变更理由"替代"等人工"
3. **增加可审计性**：`goal_signature_changelog[]` 是结构化字段（与 §2.5 task_queue 等结构化字段一致），人工审查成本低于"LLM 自答"
4. **降低阻断频率**：从 v3.01 Round 15 实证 1 次阻断降到 0 次（合并属于合法变更）
5. **不引入新依赖**：仅扩 `snapshot.json` 字段，复用现有 `goal_snapshot.py`

**SKILL.md 改动范围**（**仅精审记录，不在本任务执行**）：
- §3.2 line 229-237：移除"相似度 < 0.7 阻断 + 需人工确认"分支
- §3.2 line 237 改为："相似度 < 0.5 → 触发 WARN + 记录 `goal_signature_changelog[]`（含 reason 字段）"
- §2 schema 新增字段：`goal_signature_changelog[]`（与 v1.1 新增字段"向前兼容"原则一致）
- §10.2 门 B 不变：仍依赖 `last_audit.verdicts`（与 D3 精审一致）

### 验证证据（待执行）
- [ ] v3.01 Round 15 replay → 0 次阻断 + `goal_signature_changelog[]` 出现 1 条 scenario 合并记录
- [ ] 跑 1 次非法漂移（如突然改业务方向）→ 应在 0.5-0.7 区间触发 WARN + changelog 记录
- [ ] `goal_signature_changelog[]` 字段向后兼容：旧 snapshot.json 缺字段时 v1.2 自动填充空数组

### 恢复点
- `snapshot.json` `goal_signature_changelog[]` 字段为新增（v1.2 向后兼容），可下一轮 v{N} 移除
- SKILL.md §3.2 line 229-237 可回滚到"0.7 阻断"原文

---

## DT-V28-003 · D3 §3.3 Audit + §3.4 Review 每轮必跑

### 触发反模式
- SKILL.md §3 line 177-191：五段式 `Plan → Act → Audit → Review → Iterate` 每轮必跑
- SKILL.md §3.3 line 256 + §3.4 line 301：Audit 逐条证据化 + Review 三段式深度复盘
- SKILL.md §3.5 line 338-344（**F2 修复条款**）："禁止跳过中间 Round（每轮必须产出 `audit_<round>.md` + `review_<round>.md`）"
- SKILL.md §10.2 line 449-452：**L3 breakloop 门 B** 依赖 `last_audit.verdicts.reverse_challenge`，audit 缺失 = 门 B 失效
- **反模式形态**：每轮必跑 + L3 强依赖——若"早期收敛"阶段允许跳过，反模式检测器（breakloop）就失效

### 证据
**证据 1 — v26 §D 草案证据**（v26 PLAN line 174-179）：
> "v3.01 Round 1-3 多轮迭代只有 Plan + Act（无 Audit/Review）；五段式必跑让单轮成本 5x 翻倍；项目稳定后每轮都跑 Audit/Review 价值递减"

**证据 2 — SKILL.md §3.5 line 338-344 F2 修复条款**（**这是与草案最直接的冲突**）：
> "Round 4 audit_4.md 缺失是 v17.1 goal-loop 的核心结构性问题（DT-v17.1-001 §DT-2 问题 1）。本条款明确禁止：
> - 禁止跳过中间 Round（每轮必须产出 audit_<round>.md + review_<round>.md）
> - 禁止引用"任务描述 / GOAL.md / SKILL.md 中不存在的条款"作为决策依据"

**证据 3 — DT-v17.1-001 实证**（line 33-34）：
> "§10.2 门 B 永远无法触发 → 反模式熔断器实际上在本轮失去了自动检测能力"

**证据 4 — SKILL.md §10.2 line 449-452 门 B 数据依赖**：
> "门 B（数据）：`last_audit.verdicts` 中每个 `PASS` 都有非空 `reverse_challenge`"

**证据 5 — L3 落地情况**：
- `goal_loop_breakloop_hook.py`（line 443 引用）：**§10.2 双门判定的 L3 落地**——门 B 强依赖 `last_audit.verdicts`
- `dna_decision_density_check.py` / `dna_violation_check.py`：**未直接关联 Audit/Review**
- 结论：D3 是**L2 文字约束 + L3 hook 强依赖**——与 D1/D2 不同，**改 SKILL.md 会间接影响 hook 行为**

### 断点
- 草案"Round 4 后改每 2 轮跑 1 次"→ §3.5 F2 修复条款明文禁止跳轮 → **改 SKILL.md §3 与 §3.5 自相矛盾**
- §10.2 门 B 在"跳轮 Round"自动失效 → 自治循环失去反模式自动检测 → 回到 v17.1 Round 4 同款事故
- **断点 2**：v26 §A3 也建议"小型响应不强制落档"——若 D3 跳轮 + A3 落档放松 = 双重监管弱化

### 根因假设
| 假设 | 验证 | 成立度 |
|---|---|---|
| H1：每轮必跑成本 5x 翻倍 | 草案说"5x"但无实测；实际 Audit = 文档 + 证据采集，Review = 三段式总结——成本约 1.5-2x 而非 5x | **中**（草案数字存疑）|
| H2：项目稳定期价值递减 | 早期 Plan/Act 阶段价值高（探索），后期稳定阶段每轮变化小 → Audit/Review 边际收益降低 | **高** |
| H3：breakloop hook 必须每轮有 audit 才能工作 | §10.2 门 B 数据依赖是硬约束，**这是设计的正确之处**——草案忽视 L3 联动 | **高**（草案根因盲区）|
| H4：GL-006 增量审计去冗余已部分解决 | §3.3 line 288-298 "连续 2 轮 PASS 且对应产出物无变更 → 标记 SKIPPED_STABLE，本轮跳过校验"——Audit 已有去冗余机制 | **高**（草案忽视已有机制）|

### 候选行动
| 选项 | 描述 | 风险 |
|---|---|---|
| A. 维持每轮必跑 + 不动 F2 修复条款 | 不动 | 低 — 现状稳定 |
| B. 草案建议（Round 4 后改每 2 轮跑 1 次） | 改 §3 + 改 §3.5 F2 条款 | **高** — 必触发 breakloop 门 B 失效 → v17.1 Round 4 同款事故 |
| C. **采纳 GL-006 已有机制 + Audit 产出合并**（推荐） | §3.3 Audit "SKIPPED_STABLE" 已有 2 轮 PASS 去冗余 → 在此基础上：Review 合并（每 2 轮 1 次深度复盘）| 中 — 需新增 Review 合并逻辑，但保留 Audit 完整性 |
| D. 阈值放宽 + 加 L3 旁路 | 允许 Round ≥ 4 跳 Review，但 §10.2 门 B 改"反向审计"（在缺失轮次补 audit） | 高 — 引入新逻辑复杂度 |

### 选择与依据
**选项 C（采纳 GL-006 已设计 + Review 合并）**——**与草案 B 完全不同，修订为更安全的解**。

**依据**：
1. **解决草案根因盲区**：H3（breakloop L3 依赖）+ H4（GL-006 已存在）共同说明——**"跳轮"本身是错误解，但"减少重复劳动"的需求合理**
2. **GL-006 已存在去冗余**（§3.3 line 288-298）：连续 2 轮 PASS 且产出物无变更 → 自动 SKIPPED_STABLE——**草案忽视这条已存在的机制**
3. **保留 L3 强依赖**：Audit 每轮仍必有（§3.5 F2 修复条款不动），breakloop 门 B 持续工作
4. **仅 Review 合并**：Review 是"缺陷汇总 + 根因 + 修复方案"（§3.4 line 304-307）——深度复盘在稳定期边际收益递减，每 2 轮跑 1 次深度复盘 + 单轮轻量 review_note（如 1 段 PASS/FAIL 摘要）即可
5. **不引入新依赖**：复用现有 GL-006 + GL-007（反模式案例累计机制），不引入新 hook
6. **DT-v17.1-001 教训呼应**：DT-v17.1-001 §DT-2 的根因是"跳轮导致门 B 失效"——选项 C 不跳轮，根因不复发

**SKILL.md 改动范围**（**仅精审记录，不在本任务执行**）：
- §3 line 187：`Audit (逐条证据化自检)` 维持 → 不变
- §3 line 188：`Review (缺陷汇总 + 根因 + 修复方案)` 改为 `Review (单轮轻量 + 双轮深度)`
- §3.3 line 256 Audit 全文：维持不动（GL-006 已处理去冗余）
- §3.4 line 301 Review 全文：改为两档：
  - `Review Lightweight`：单轮必跑，1 段 PASS/FAIL 摘要（≤ 30 行），产出 `review_<round>_light.md`
  - `Review Deep`：每 2 轮或最终轮必跑，三段式完整复盘，产出 `review_<round>.md`
- §3.5 line 338-344 F2 修复条款：**不动**（跳轮仍禁止，Audit 每轮必跑保留）
- §10.2 门 B：**不动**（依赖 `last_audit.verdicts` 持续工作）

### 验证证据（待执行）
- [ ] v3.01 跑 5 轮 Round：Round 1-5 各产 audit_X.md + review_X_light.md；Round 2 / 4 / 5 产 review_X.md（深度）
- [ ] breakloop hook 行为不变：5 轮中每轮门 B 仍能正常判定（`last_audit.verdicts` 每轮非空）
- [ ] `antipattern_cases.jsonl` 无新增"跳轮"类条目
- [ ] 单轮成本对比：vs 现状 1.5-2x 降低（精确数字待测）

### 恢复点
- SKILL.md §3.4 两档 Review 改回单档 Review 仅需修改 §3 line 188 + §3.4 全文
- §3.5 F2 修复条款不变，无回滚需求

---

## V-203 PASS / FAIL 判定

### 判定标准核对

| V-203 验证项 | 结果 |
|---|---|
| ✅ v28_dt_d1_d2_d3.md 已创建 | **PASS**（本档已创建于 `governance/design_iter/current/v28_dt_d1_d2_d3.md`）|
| ✅ 3 个 DT 决策各占 1 段（结构完整）| **PASS**（DT-V28-001 / 002 / 003 各占独立大节）|
| ✅ 每个 DT 含：触发反模式 / 证据 / 断点 / 根因 / 候选 / 选择 / 验证 | **PASS**（7 字段齐全）|
| ✅ 不动 SKILL.md / .py / hooks.json | **PASS**（本任务全程未改 SKILL.md / 任何 .py / hooks.json）|

### 关键修订记录（与 v26 草案的差异）

| 草案建议 | 本精审判定 | 修订理由 |
|---|---|---|
| D1 value_ratio 降到 0.5 + 软记录 | ✅ **采纳** | 与草案一致 |
| D2 阈值降到 0.5 | ❌ **修订为选项 D**（增量更新签名 + changelog）| 草案仅降阈值，但未解决"自治模式无人工可确认"的根因断点 |
| D3 Round 4 后每 2 轮跑 1 次 | ❌ **修订为选项 C**（Audit 每轮必跑保留 + Review 双档）| 草案忽视 §3.5 F2 修复条款 + §10.2 breakloop 门 B L3 依赖，会触发 v17.1 同款事故 |

### V-203 最终判定

**V-203 PASS（条件性）**：

- **精审 + DT 决策清单任务本身**：✅ PASS（3 个 DT 决策齐全 + 7 字段完整 + 不动约束文件）
- **附带价值**：发现 v26 §D 组 3 项草案有 **1 项可直接采纳（D1）+ 2 项需修订（D2 / D3 根因盲区）**

### 触发的反模式 / 阻塞（待用户拍板）

| 类别 | 内容 | 状态 |
|---|---|---|
| **反模式风险** | D3 草案 B 选项（Round 4 后每 2 轮跑 1 次）若直接采纳 → 触发 v17.1 Round 4 同款事故（breakloop 门 B 失效）| **已在本档 DT-V28-003 标注，草案需修订** |
| **阻塞** | 无技术阻塞；v28/v29 是否落地需用户拍板 | 等待 |
| **L3 联动风险** | D3 改动 SKILL.md §3.4 必须联动考虑 §10.2 门 B 数据依赖——本档已显式标注"§10.2 不动" | 已规避 |

---

## 落档协议执行记录（DNA §9.5）

- **本档路径**：`governance/design_iter/current/v28_dt_d1_d2_d3.md`（按 §9.5 默认目录）
- **占用 current/**（v28 草案归档后此档可转 `governance/design_iter/plans/v28/`）
- **不动**：SKILL.md / .py / hooks.json（满足 V-203 验证项）
- **本轮实际改动文件清单**：仅本档 1 个文件（`v28_dt_d1_d2_d3.md`）
- **决策点密度**：3 个 DT × 平均 7 字段 ≈ 21 决策点 / 1 文件 ≈ 21 / 文件 —— **高于 §9.1 红线 5**，但**纯精审 + DT 决策清单任务**（不改业务），符合豁免语境
- **后续动作**：
  1. 用户拍板 → 决定 v26 §D 组采纳度（D1 采纳 / D2 改方案 D / D3 改方案 C）
  2. v28 治理周期启动 → 同步更新 SKILL.md §2.1 / §2 schema / §3 / §3.4 / §10.2（**§3.5 F2 修复条款不动**）
  3. v3.01 replay 验证（按 DT 各自"验证证据"段执行）

---

> **返回给父会话**：本档包含 3 个完整 DT 决策（DT-V28-001 / 002 / 003），每个含 7 字段齐全。
> **V-203 判定**：PASS（精审任务）+ 修订草案（D2 / D3 根因盲区已标）。
> **未触发的反模式**：本任务未发生 §9.4 先验后答违规（全部先 Read 后答）；未发生 §9.5 落档违规（先 Write 占位后展开）。