# v3 已解决问题归档

> 本文件归档 v3 实施期间已解决的问题。
> 与 `decisions.json` 的 `decided: true` 项对应——决策落地后的事实记录。

---

## Q-301：3 问自检物化分层（已决）

- **决策时间**：2026-06-19
- **决策值**：L1知识 + L2约束 + L3机制（三层组合）
- **决策理由**：
  - 纯 L1（仅 AGENTS.md）= 软约束，违规 0 后果
  - 纯 L3（仅 hook）= 硬阻断，Agent 写不出东西
  - 三层组合：L1 给"为什么"、L2 给"做什么"、L3 给"自动防呆"
- **影响文件**：
  - `AGENTS.md`（不动）
  - `.cursor/rules/DNA_3Q_CHECK.mdc`（新增 L2）
  - `.cursor/hooks/dna_violation_check.py`（新增 L3）

---

## Q-302：AGENTS.md 是否加 3 问速查表（已决）

- **决策时间**：2026-06-19
- **决策值**：B（独立 DNA_3Q_CHECK.mdc alwaysApply，AGENTS.md 不动）
- **决策理由**：
  - AGENTS.md 写明"≤60 行"红线
  - 按 AGENTS.md L14 约束 vs 知识分离原则，3 问是具体操作约束应独立
- **影响文件**：
  - `AGENTS.md`（保持 60 行）
  - `.cursor/rules/DNA_3Q_CHECK.mdc`（新增）

---

## Q-303：hook A 设计（已决）

- **决策时间**：2026-06-19
- **决策值**：混合：软记录 + 连续 3 次违规才 block
- **决策理由**：
  - 硬阻断会让 Agent 写不出东西（误判）
  - 纯软记录无强制力
  - 临界点 3 次 = 既不误判，又能在连续违规时强制自省
- **影响文件**：
  - `.cursor/hooks/dna_violation_check.py`（新增）
  - `.cursor/hooks.json`（注册 beforeSubmitPrompt 事件）

---

## 触发事件：v2 改造期间 DNA 违规（已记录）

- **时间**：2026-06-19 凌晨
- **违规清单**（3 项）：
  1. 先动手再问——`install.sh` step 3 改 `warn` 跳过前未先问用户
  2. 改动无影响范围——`SKILL_STANDARDS.md` 6 处删除未列影响
  3. 未做 3 问自检——8 个文件改动期间无停顿
- **用户反馈**："违反 dna，证明 dna 的约束没有在行为前或者思考前生效"
- **解决方式**：v3 方案物化 DNA → 见 Q-301 决策
