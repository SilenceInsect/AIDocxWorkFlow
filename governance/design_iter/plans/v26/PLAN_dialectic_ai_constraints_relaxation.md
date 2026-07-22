# v26 治理整治草案 — AI 自治规则放宽与移除清单

> **本档定位**：讨论稿 / 草案 — **等待用户逐条拍板**，不进入 v{N} 归档序列执行
> **背景**：项目主体结果稳定后（v3.01 87 TC / Ready / 0 例外），早期"人工强监督"阶段立的规则与约束出现"卡 AI 自治"症状
> **整治范围**：仅覆盖「AI 自治约束」（DNA / hooks / 决策密度 / 落档协议 / 三步自问 / 业务门禁）；不动"知识资产"（CHANGELOG / 设计迭代记录）
> **基线证据**：
> - `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json`（11311 行，87 TC Ready）
> - L1∧L2 双门全 PASS / 0 例外触发（v17 闭环）
> - Round 15 scenario 合并：331 单步 TC → 87 多步 TC（1.0 硬门禁 → 0.98+ 三步自问放行）
>
> **重要免责**：
> - 本档内 15+10 条建议**仅来自 2 次 explore 深审 + 4 个核心文件 Read + 1 次治理诊断**——**未逐条 Read 各 hook 文件做精审**
> - 落档路径 `v26/`（避开 v17 占用 current + v18/v19-v25 各会话归档中）
> - 用户拍板后才进入治理实施阶段（届时建议补 Read + 精审）

---

## 1. 一句话目标

把项目稳定期"卡 AI 自治"的过度规则与硬阈值（≤ 3 文件改动 / 1.0 硬门禁 / 三步自问决策树 / 落档协议 / Hook 死代码）按"放宽/移除/合并"三档梳理，**给出每条的证据、替代、风险**，由用户拍板。

---

## 2. 范围（In / Out of Scope）

### In Scope（本次讨论）
- DNA_3Q_CHECK.mdc（486 行，硬约束）
- DESIGN_AND_EXECUTION_STANDARDS.mdc（644 行，跨阶段）
- goal-loop SKILL.md（498 行，自治闭环）
- hooks.json（14 个 .py + 18 个文件，需重核数）
- 业务门禁（10 项 + 三步自问例外条款）
- v17 阶段 5 项"卡 AI 自治"约束（含字段溯源 / L1 校验 / Excel schema）

### Out of Scope（不动）
- 项目级知识库 / 模块定义 / SKILL 入口（aidocx-s1-~s8-）
- workflow_assets 既有产物
- CHANGELOG.md / INDEX.md（等本档闭环后再更新）
- v17/v18/v19 既有归档（避免破坏既有审计链）

---

## 3. 治理整治建议 — 决策表（讨论稿）

### A 组：DNA_3Q_CHECK.mdc 冗余 / 过严条款（4 条）

#### [建议 A1] §1「5 问自检」 + §10「准则 4 展开」重复定义 Q5
- **类型**：合并
- **理由**：Q5 在 §1 + §10.6 都出现，且 §10.6 明确说"§1 Q5 = 用在哪 / §10 = 做得对不对"。两份并列让 Agent 在响应时双触发自检，**重复自检反而拖慢推理**
- **影响**：`DNA_3Q_CHECK.mdc:20`（§1 表）+ `DNA_3Q_CHECK.mdc:373-415`（§10）
- **替代**：保留 §10（执行清单），§1 表中 Q5 改为简引「见 §10.6 入口」
- **风险**：低 —— 自检内容不丢，只是少一个"双触发点"

#### [建议 A2] §9.1「单次响应 ≤ 3 文件改动」与 §9.1.1/§9.1.2 豁免条款自相矛盾
- **类型**：放宽
- **理由**：阈值 3 是 v6.1 时代 LLM 习惯未变时的保守值；项目稳定后已**批量改文件（Round 18 5 文件 / 治理方案动辄 8-10 文件）成常态**，豁免条款反被滥用
- **影响**：`DNA_3Q_CHECK.mdc:172-180`（§9.1 阈值表）+ `:182-252`（§9.1.1/§9.1.2 豁免）
- **替代**：阈值放宽到 **5**（与 §9.1.1 self-test 豁免上限对齐）；豁免条款**保留但不主动触发**——改成"事后审计"（每会话记入 feedback_log）
- **风险**：中 —— 阈值放宽后单 turn 改 4 文件不再 block，但 hook 仍记录；治理强度下降一档

#### [建议 A3] §9.4「先验后答」+ §9.5「落档协议」双触发让响应变长
- **类型**：合并
- **理由**：两项都是"防 Agent 自欺"，但 §9.4（必须先 Read）+ §9.5（必须先 Write 占位）**强制每次响应都带额外 2 次 tool call**，把 30 行响应挤成 80 行；项目稳定后这反而**降低响应质量**（决策密度被流程密度稀释）
- **影响**：`DNA_3Q_CHECK.mdc:271-318`（§9.4）+ `:320-369`（§9.5）
- **替代**：
  - §9.4 保留，但 Read 调用**不必前置**（Agent 内部已 Read 时不重复）
  - §9.5 改成"决策表 / 计划 / 候选方案 ≥ 10 行"才强制落档（小型响应不触发）
- **风险**：中 —— 落档强度下降一档；Agent 自欺成本降低

#### [建议 A4] §9.6「落档协议与 L3 hook 关系」+ §11「产出无版本标记规则」是同一类约束分两处定义
- **类型**：合并
- **理由**：§9.6（落档 hook 触发）+ §11（产品格式 yaml SSOT）都是"产出物合规"约束，但分两套引用链路（L2 + L3）—— Agent 阅读时容易只读一边
- **影响**：`DNA_3Q_CHECK.mdc:362-369`（§9.6）+ `:419-486`（§11）
- **替代**：合并到单一节「§11 产出合规（含落档 + 版本标记）」，§9.6 删；product_format_rules.yaml SSOT 不变
- **风险**：低 —— 内容不变，只改结构

---

### B 组：DESIGN_AND_EXECUTION_STANDARDS.mdc SSOT 重复 / 阈值过严（4 条）

#### [建议 B1] §2.3 质量门禁速查表 + §4.3 配置常量 + §11.3 永久 SSOT 清单三处重复定义阈值
- **类型**：合并
- **理由**：三处都列阈值（S5_MIN_TP_PER_STORY / S6_OBJ_COVERAGE 等），但 SSOT 声明又在 §2.3 顶部说"先改本节再同步引用方"——**实际违反了自己立的 SSOT**（§11.3 又说"SSOT = 设计执行标准 §4.3"）
- **影响**：`DESIGN_AND_EXECUTION_STANDARDS.mdc:107-116`（§2.3）+ `:481-507`（§4.3）+ §11.3（v17 +）
- **替代**：阈值常量**仅在 §4.3**；§2.3 改成"读 §4.3"索引；§11.3 改成"读 §4.3"索引
- **风险**：低 —— 单一来源，杜绝三处漂移

#### [建议 B2] §2.4.2「例外率监控」分母固定 10 + 🟡 20% / 🔴 40% 在 v3.01 稳定后持续自噪扰
- **类型**：放宽
- **理由**：固定 10 项分母（基于走完全流程 S1-S8 的"理想分母"）—— 实际多数项目不走 S3（v3.01 即如此），分母变 8，但阈值仍按 10 算 → **1 项例外就触发 12.5% 黄色预警**，2 项触发 25% 红警
- **影响**：`DESIGN_AND_EXECUTION_STANDARDS.mdc:194-242`（§2.4.2）
- **替代**：
  - 分母改"**实际触发门禁数**"（v3.01 实测 = 7-8）
  - 阈值放宽到 30% / 50%（v3.01 单项目 1-2 项例外属常态）
- **风险**：中 —— 黄色预警门槛提高后，过度门禁问题不易被及时发现

#### [建议 B3] §3.7「大文件改动 SOP」与 §9「决策密度」重复定义大文件处理
- **类型**：合并
- **理由**：§3.7 写 SOP（Read 全文 + Write 完整重写 + py_compile + self-test），§9.1 写阈值（≤ 3 文件）。**SOP 是阈值触发的具体执行清单**，但两份独立定义 → Agent 看阈值时不知道有 SOP，看 SOP 时不知道有阈值
- **影响**：`DESIGN_AND_EXECUTION_STANDARDS.mdc:350-381`（§3.7）+ `DNA_3Q_CHECK.mdc:172-180`（§9.1）
- **替代**：合并到 DNA §9.1「决策密度」项下"**触发后执行清单**"列；§3.7 整段删
- **风险**：低 —— 内容不丢，只是结构内聚

#### [建议 B4] §4.3.1「异常路径覆盖率 = 1.0（100%）必须」在 v3.01 已被实测打脸
- **类型**：放宽
- **理由**：v3.01 S4 = 25 条异常路径，其中 3 条标 `deprecated` 后跳过（22/22 = 100% 可控）；但**绝对 1.0 阈值的本意是"零遗漏"，与 deprecated 跳过逻辑冲突**——实际值 22/25 = 0.88，但 S7 已通过三步自问放行
- **影响**：`DESIGN_AND_EXECUTION_STANDARDS.mdc:509-554`（§4.3.1）
- **替代**：阈值 ≥ 95%；5% 容许 `skip_reason = low_risk / deprecated / manual_test`；S7 omission_ledger 跟踪
- **风险**：中 —— 5% 漏测窗口由"业务方季度回顾"补位，治理强度下降一档

---

### C 组：Hook 体系过度检查 / 已死代码（4 条，需精审后确认）

#### [建议 C1] `dna_decision_density_check.py` 阈值 3 与 §9.1 同源过严
- **类型**：放宽
- **理由**：见 [建议 A2]。hook 是 §9.1 的 L3 落地，阈值应同步放宽到 5
- **影响**：`.cursor/hooks/dna_decision_density_check.py:38`（`DENSITY_THRESHOLD = 3`）
- **替代**：`DENSITY_THRESHOLD = 5`；保留软记录（≤ 5）不 block，仅记录到 `workflow_assets/feedback_logs/dna_decision_density.jsonl`
- **风险**：中 —— hook 阻断频率降低

#### [建议 C2] `session_resume_multi_goal.py` 已死代码
- **类型**：移除
- **理由**：子任务已 grep 确认**未注册到 hooks.json**（无事件触发）；self-test 5/5 通过但实际无消费者
- **影响**：`.cursor/hooks/session_resume_multi_goal.py`（未 Read 全文）
- **替代**：若仍想保留多 goal 续跑能力，**先注册到 hooks.json#sessionStart**（与 `goal_loop_hook.py` sessionStart handler 不冲突？需精审）
- **风险**：低 —— 已死代码，移除无副作用；**但需精审是否与 `goal_loop_breakloop_hook.py` sessionEnd 功能冲突**

#### [建议 C3] `dna_violation_check.py` 触发器不写 marker
- **类型**：~~精审后决定保留或移除~~ → **撤回**
- **理由（修订）**：**精审后发现 hook 是好的** —— `MARKER_PREFIX = "⚠️ DNA 自检未通过"` 识别正常（line 91） + `dna_violations.jsonl` 写入正常（line 139） + 阈值 3 临界点触发正常（line 141-147）。**草案 C3 错误**——子任务误判"marker 触发器实际不写"
- **影响**：撤回。`.cursor/hooks/dna_violation_check.py:91`（`count_violations` 工作正确） + `:140-147`（阈值触发正常）
- **替代**：撤回后无需替代
- **风险**：撤回 = 维持现状 = 零风险

#### [建议 C4] `before_prompt_dna_check.py` 与 `project_dna_inject.py` 功能重叠
- **类型**：~~合并~~ → **修 bug 而非合并**
- **理由（修订）**：精审后发现两者**功能不同**：
  - `before_prompt_dna_check.py`（beforeSubmitPrompt）：**仅在设计类 prompt 触发时**注入 3 问自检提示
  - `project_dna_inject.py`（sessionStart）：**会话启动时**注入 AGENTS.md 全量 DNA
  - **真正的 bug**：`before_prompt_dna_check.py` 注入文本是**3 问版本**（Q1-Q3），与 `DNA_3Q_CHECK.mdc §1` 的 **5 问**（Q1-Q5）**不一致**
- **影响**：`.cursor/hooks/before_prompt_dna_check.py:24-36`（注入文本过时）+ `.cursor/hooks/project_dna_inject.py:48-93`（AGENTS.md 全量，正常）
- **替代**：**更新** `before_prompt_dna_check.py` 注入文本到 5 问版本（与 DNA §1 对齐）；保留双 hook（功能互补：1 个 DNA 全量 / 1 个自检提示）
- **风险**：中 —— 注入文本不对齐时 Agent 误以为"3 问够用"，但 `DNA_3Q_CHECK.mdc` 仍在自动加载时覆盖

#### [精审结论 · 2026-07-19 Read 全文]

| Hook | 草案判断 | 实测真相 | 修订决策 |
|---|---|---|---|
| C1 决策密度阈值 | 放宽到 5 | 源码默认 3，但**已支持环境变量覆盖**（`DNA_DECISION_DENSITY_THRESHOLD` line 38）| 改 doc 注释阈值 5；源码不变；补充 README 说明覆盖方式 |
| C2 session_resume_multi_goal 未注册 | 移除 | 代码完整 + 5/5 self-test（line 147-244）+ HANDLERS={sessionStart:...}（line 123-125）；只是 hooks.json 缺一行注册 | **修：补注册**（非删）|
| C3 dna_violation_check marker 不写 | 修复/移除 | **hook 是好的** —— marker + 计数 + log 全正常 | **撤回 C3**（子任务误判）|
| C4 before_prompt_dna + project_dna 重叠 | 合并 | **不重叠** —— 功能不同（DNA 全量 vs 自检提示），但注入文本过时 | **修 bug 而非合并**：注入文本对齐到 5 问 |

---

### D 组：Goal-Loop 早期"人工强监督"残留（3 条）

#### [建议 D1] GL-001「value_criteria vs process_criteria 拆分 + value_ratio ≥ 0.6 强制」
- **类型**：放宽
- **理由**：v3.01 实操验证 value_criteria 5-6 条 / process_criteria 2-3 条是稳定配比；强制 0.6 让简单目标必须凑价值项 → **凑出来的价值项是假的**
- **影响**：`.cursor/skills/goal-loop/SKILL.md:38-42`（§2.1）+ `:78-83`（§3.1 GL-001）
- **替代**：value_ratio 改**指导值 ≥ 0.5**；不达标时仅提醒，不阻断
- **风险**：低 —— 阻断放宽到软记录；v3.01 实证配比仍能 PASS

#### [建议 D2] GL-009「Goal Signature 防漂移」相似度 < 0.7 触发 WARN + 阻断
- **类型**：放宽
- **理由**：v3.01 Round 15 scenario 合并 = 合法目标变更，但合并后 raw_user_goal 字面漂移 → 触发 0.55 相似度阻断；LLM 必须额外解释"为何合并"才能继续
- **影响**：`.cursor/skills/goal-loop/SKILL.md` §2.5 + §3.2 GL-009
- **替代**：阈值放宽到 0.5；相似度 0.5-0.7 走"软记录 + 解释 + 用户确认"而非直接阻断
- **风险**：中 —— 误判目标漂移的成本降低

#### [建议 D3] §3.3「Audit 客观论证」+ §3.4「Review 深度复盘」每轮必跑不可跳过
- **类型**：放宽
- **理由**：v3.01 Round 1-3 多轮迭代只有 Plan + Act（无 Audit/Review）；五段式必跑让单轮成本 5x 翻倍；**项目稳定后每轮都跑 Audit/Review 价值递减**
- **影响**：`.cursor/skills/goal-loop/SKILL.md:88-156`（§3.3-§3.4）
- **替代**：
  - 第 1-3 轮必跑 Audit/Review（早期收敛阶段）
  - 第 4 轮后改为"每 2 轮跑 1 次 Audit/Review"
  - 最终轮必跑
- **风险**：中 —— 收敛后段的反馈延迟一档

---

## 4. 业务门禁放宽清单（10 条，已 Read v3.01 实测数据）

| # | 门禁项 | 当前阈值 | 放宽建议 | 替代机制 | 证据（v3.01）|
|---|---|---|---|---|---|
| 1 | S1 评分 | ≥ 7.0（5 维加权）| ≥ 6.5；权重前置完整性（完 30 / 清 25 / 一 20 / 测 15 / 可行 10）| S1.5 P0 100% 拦截兜底 | 实测 6.8-7.2 区间徘徊 |
| 2 | S2 拆解精度 | ≥ 90% | ≥ 85%；"核心必拆 + 边缘可合并"双轨 | S5 ≥ 6 TP/Story + S6 OBJ 1.0 兜底 | 边缘 Epic 合并后 ~88% |
| 3 | S4 异常路径 | = 1.0 | ≥ 95%；5% 容许 `skip_reason` | S7 omission_ledger 跟踪 | 25 路径 → 3 deprecated → 22/22 = 100% |
| 4 | S5 TP/Story | ≥ 6（指导）| 分级：低 ≥ 4 / 中 ≥ 6 / 高 ≥ 8 | S2 backlog risk_level 字段 | 87 Story 平均 = 1（合并前）|
| 5 | S5 FP 覆盖率 | = 1.0 | ≥ 98%；2% 容许 FP = "辅助/性能基线"不测 | `fp_coverage_exempt[]` 显式枚举 | 87 FP → 85/87 = 97.7% |
| 6 | S5 OBJ 覆盖率 | = 1.0 | **维持 = 1.0**（硬约束）| 无替代 | 100% 实证 |
| 7 | S5 S3/S4 引用 | = 1.0 | 维持 100%；允许 scenario_group 引用 | S4 `scenario_group_id` 字段 | 331 单步 → 87 多步合并 |
| 8 | S6 字段填写率 | ≥ 90% | 维持 ≥ 90%；分档：结构 100% / 业务 ≥ 85% | required vs business 分层 | Round 12 normalizer 后结构 100% |
| 9 | S6 OBJ/FP 双层 | = 1.0 | **维持 = 1.0**（硬约束）| 无替代 | 87/87 OBJ + 87/87 FP |
| 10 | BYPASS 例外率 | 10 项固定 / 20% / 40% | 动态分母（实际触发数）；阈值 30% / 50% | S7 omission_ledger 自动汇总 | 实际触发 6-7 项 |

### 三步自问例外条款放宽

| 项 | 当前 | 建议 |
|---|---|---|
| Q1/Q2 任一"有/存在"→ 阻断 | 100% 阻断 | 加 Q4 = "业务方已显式接受"作放行条件 |
| bypass_log 备案 | 必填 | 维持必填；**取消 §2.4.2 红黄预警的强制告警** |

### v17 卡 AI 自治 5 项约束（已 Read v17 GOAL.md）

| # | 约束 | 判定 |
|---|---|---|
| ① | `fp_name` 必须 100% 等于 S2 `fp_desc` | ❌ 过度 → 改"差异度 > 30% 报警" |
| ② | `steps[]` 结构化数组强制 | ⚠️ 半必 → 允许字符串数组 |
| ③ | `test_method[]` 字符串数组强制 | ❌ 过度 → 允许单字符串 |
| ④ | `tp_reference` 必填（单值）| ⚠️ 半必 → 改 `tp_references[]` 数组 |
| ⑤ | `preconditions[]` 字符串数组强制 | ✅ 必须 → 维持 |

---

## 5. 整治优先级

### 🟢 高优先级（先做 · C 组已精审修订）
1. **B1 阈值 SSOT 三处合并** — 影响所有门禁，单一来源杜绝漂移
2. **C1 / A2 决策密度阈值 3 → 5** — **修订**：源码已支持 `DNA_DECISION_DENSITY_THRESHOLD` 环境变量，**改 doc 注释 + 补 README**，源码不变
3. **C2 session_resume_multi_goal 补注册** — **修订**：补注册到 `hooks.json#sessionStart`（不删）；self-test 5/5 已 PASS
4. **C4 before_prompt_dna_check 注入文本** — **修订**：3 问 → 5 问对齐 DNA §1

### 🟡 中优先级（第二批）
5. A1 / A3 / A4 / B3 — DNA 与 DESIGN 内部冗余合并（**已 v28 DT 精审 REJECT，维持现状** — DT-V28-006/007/008/009，参考 v28 review_round1.md §3 R1）
6. B2 例外率动态分母 / 30% 50% 阈值
7. B4 / 业务门禁 4-7 — 硬阈值 → 软阈值（保留兜底）（**B4 已 v28 DT 精审维持 100% 业务门槛** — DT-V28-005，驳回 v26 草案 95% 因为草案样例 22/25=88% < 95% 自身矛盾）

### ⚪ 低优先级（按需 / 已撤回）
8. **C3 dna_violation_check 已撤回** — hook 是好的，不动作
9. D1-D3 goal-loop 早期约束放宽（**D3 已 v28 DT 精审选 C：Audit 每轮必跑 + Review 双档** — DT-V28-003）
10. v17 5 项约束分类处置（v27 carry）

---

## 6. 风险与回退

| 风险 | 触发条件 | 回退方案 |
|---|---|---|
| 决策密度阈值放宽后改文件过度 | 5+ 文件改动出现错改 | 重设阈值 4 / 重新启用 §9.1.1 豁免条款 |
| 落档协议放宽后决策丢失 | 计划 / 决策表未落档 | §9.5 触发条件重设为"≥ 10 行"或"含决策关键词" |
| 业务门禁放宽后漏测 | OBJ/FP 100% 仍维持；S5 FP 98% 引入漏测风险 | S7 omission_ledger 兜底；季度回顾 |
| 三步自问放宽后业务确认弱化 | 业务方未及时签 bypass | 加 stakeholder_signoff 强制字段 |

---

## 7. 落档协议执行记录

- **本档路径**：`governance/design_iter/plans/v26/PLAN_dialectic_ai_constraints_relaxation.md`
- **不抢占 current/**（其他会话占用）
- **不开 v{N} 索引**（草案非闭环，等用户拍板）
- **已完成精审**（2026-07-19 Read 全文）：
  - `dna_violation_check.py`（212 行）：hook 是好的，C3 撤回
  - `session_resume_multi_goal.py`（251 行）：代码完整 + 5/5 self-test，C2 改"补注册"
  - `before_prompt_dna_check.py`（144 行）：注入文本是 3 问过时版，C4 改"更新文本"
  - `project_dna_inject.py`（104 行）：注入 AGENTS.md 全量，正常
  - `dna_decision_density_check.py`：已支持环境变量覆盖，C1 改"改 doc 不改源码"
- **后续动作**：
  1. 用户拍板 → 启动 v27 治理周期（v27 carry v17 5 项约束 + 4 条高优先）
  2. v27 落地后同步更新 INDEX.md / CHANGELOG.md
  3. 跑一轮 v3.01 验证（确认治理改动不影响既有产出）

---

## 附录：待补充材料（需用户决策后展开）

1. **25 条 → 实际改文件清单** —— 等用户拍板后细化到文件级改动（C 组已精审，落到 v27）
2. **v27 治理任务分解** —— 4 条高优动作对应 4 个子任务
3. **v17 5 项约束影响面** —— v17 已 CONVERGED，需用户判断是否 reopen v17
4. **业务门禁数据面板** —— 抽取 v3.01 实际触发门禁数 → 例外率面板
