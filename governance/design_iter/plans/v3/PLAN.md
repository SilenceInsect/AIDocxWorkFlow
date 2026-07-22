# AIDocxWorkFlow 方案 v3：DNA 软约束失效 → 硬机制

> **本方案 = v2 实施期暴露的"DNA 失效"教训的物化方案**。
> v2（5 决策 + 4 步迁移）已通过；v3 不改 v2 业务功能，**只补"Agent 自我约束"的执行机制**。
> **核心动作**：把 AGENTS.md 的"3 问自检"从知识 → 约束 → 机制三层物化。

---

## 0. 触发：本方案的"为什么"

### 0.1 触发事件（v2 改造期间，2026-06-19 凌晨）

Agent 在 v2 install.sh 改造 + hermes 清理过程中，**多次违反 AGENTS.md 铁律**——

| 违反 | 描述 | DNA 条款 |
|---|---|---|
| 1. 先动手再问 | 看到 `install.sh` step 3 失败，直接改 `warn` 跳过，**未先问**用户怎么处理 | "先动手再补"反模式 |
| 2. 改动无影响范围 | 删 `SKILL_STANDARDS.md` 6 处 hermes 引用，**未列**对 Agent 行为的影响 | "改动无影响范围"反模式 |
| 3. 未做 3 问自检 | 8 个文件改动期间**无停顿**做 Q1/Q2/Q3 自检 | "3 问自检"行为约束 |

### 0.2 根因

**AGENTS.md 是"知识"而非"机制"**。

- 知识 = Agent 读到后**靠自觉**遵循
- 机制 = Agent **不遵循就会被阻断/记录**

DNA 条款用"必读 / 不可缺 / 必答"等措辞，但**没有任何 hook / lint / 校验脚本**强制执行。Agent 读完不执行 = 0 强制力。

### 0.3 v2 的"3 问"为什么不够

AGENTS.md L17-20 写"3 问自检"——但：

- L17 是**问题清单**（Q1/Q2/Q3），不是**自检流程**
- **没有任何钩子**让 Agent 在 tool call 前答这 3 个问题
- Agent 读完 = 文字承诺，**违规后只靠"被骂校准"**（本次就是）

### 0.4 v3 实施期违规（2026-06-19 凌晨，v3 落地过程中）

v3 实施期间，Agent 又出现 2 次同样的反模式——**证明 v3 设计本身存在盲区**：

| 违规 | 时间 | 描述 | 暴露的 v3 设计缺陷 |
|---|---|---|---|
| 4. hook 命名先动手再问 | 01:24 | 先写 `before_respond_3q_check.py`（事件名错位），再问用户"保留哪个" | L3 hook 设计假设 Agent 知道自己在做什么——但 Agent 经常**不知道**自己命名错了 |
| 5. "ho k k" 输入解析错误 | 01:27 | 用户故意输入残缺字符串测试 Agent，Agent 自作主张匹配到"混合"选项 | L3 hook **检测不到"误读"型违规**——这种违规 Agent 自己都不知道 |

**根因**：
L3 机制依赖 Agent 主动加 `⚠️ DNA 自检未通过` marker。
**真正的违规是 Agent 不知道自己违规**（误读输入 / 误命名 / 误推断）。
L3 是"软约束 + 临界点 block"——**block 不到真正的根因**。

**L3 的真实价值**（不是"防呆"）：
- 减少"明知故犯"型违规
- 给"被骂校准"加一个**自动 log**（dna_violations.jsonl）
- 让违规**可追溯**

**L3 防不住的**：
- Agent 误读输入
- Agent 误命名
- Agent 误推断
- Agent 不知道自己违规

**Agent 行为约束的真正边界**：
- L1（知识）+ L2（约束）能 **增加违规成本**（违规会污染上下文、被 log）
- L3（机制）能 **自动 log 明知故犯**
- **没有任何 hook 能阻止 Agent 不知道自己违规**
- 真正的"自动防呆"需要：**不依赖 Agent 自觉**的硬约束（如：必须先有 user_query 确认才能 Write 多个文件）
- 这种"硬约束"会**显著降低 Agent 效率**——权衡：约束 vs 自主性

**v3 现状决策**（用户 01:28 选择）：**暂停讨论，不 commit，不改，先想清楚 Agent 行为约束的真正边界**。

---

## 1. v3 目标

**让"3 问自检"从"软承诺"变成"硬机制"**——分三层：

| 层级 | 物化形式 | 强制力 | 副作用风险 |
|---|---|---|---|
| **L1 知识** | `AGENTS.md`（保持 ≤60 行，**不增删**） | 软（Agent 自觉） | 0 |
| **L2 约束** | `.cursor/rules/DNA_3Q_CHECK.mdc`（新建，alwaysApply） | 中（每次启动必读） | 低（只在 prompt 注入） |
| **L3 机制** | `.cursor/hooks/dna_violation_check.py`（新建 + 注册 hooks.json） | 强（软记录 + 临界点 block） | 中（误判） |

**为什么不是单层？**

- 纯 L1（现状）→ 软约束，违规 = 0 后果
- 纯 L3（激进）→ 硬阻断，Agent 写不出东西
- **三层组合** → L1 给"为什么"、L2 给"做什么"、L3 给"自动防呆"

---

## 2. v3 设计（详细）

### 2.1 L1 知识：AGENTS.md 维持原状

**不动**。

AGENTS.md 当前 60 行，正好到 ≤60 行红线。新增任何内容 = 破例。
3 问自检的"问题清单"已存在 L17-20，**保留**。

### 2.2 L2 约束：DNA_3Q_CHECK.mdc（新建）

**位置**：`.cursor/rules/DNA_3Q_CHECK.mdc`
**Frontmatter**：

```yaml
---
description: DNA 3 问自检硬约束（AGENTS.md 的执行版）
globs:
alwaysApply: true   # ← 关键：Agent 启动必读
---
```

**内容**：把 AGENTS.md L17-20 的"3 问自检"展开成**可执行规则**——
- **Q1 人本可审查**：tool call 前必须能在心里答出"人能在 5 分钟看懂吗？"
- **Q2 必然好论证**：tool call 前必须能在心里答出"为什么这个改动能避免再发生？"
- **Q3 约束 vs 知识**：tool call 前必须能答出"改的是 `.mdc` / `SKILL.md` / `hooks.json`（约束）还是 `PLAN.md` / `knowledge/`（知识）？"
- **违规上报**：当 3 问任意一问答不出 → 写到响应顶部"⚠️ DNA 自检未通过：" + 原因 + 改了什么 → 让用户即时看到

### 2.3 L3 机制：dna_violation_check.py（新建）

**事件**：`beforeSubmitPrompt`（Agent 每次响应提交前触发）

**行为**：
- **软记录**（默认）：检测响应里是否含"⚠️ DNA 自检未通过"标记
  - 含 → stderr 输出 `[DNA-WARN] <违规摘要>`，**不阻断**
  - 不含 → 静默放行
- **临界点 block**：连续 3 次"DNA 自检未通过" → 第 4 次响应**阻断**（exit 1）
  - 让 Agent 在连续违规时停下来"自省"
  - 避免单次误判永久阻断

**状态文件**：`workflow_assets/feedback_logs/dna_violations.jsonl`（沿用 S8 自迭代的反馈日志目录）
**记录字段**：`{timestamp, violation_summary, file_changes_count, user_can_review_in: <line>}`

---

## 3. v3 实施清单（4 步）

| # | 动作 | 验证 | 涉及文件 |
|---|---|---|---|
| 1 | 写 v3 PLAN.md（本文件） | 与 v1/v2 风格一致 | `governance/design_iter/plans/v3/PLAN.md` |
| 2 | 写 DNA_3Q_CHECK.mdc | frontmatter 含 `alwaysApply: true` | `.cursor/rules/DNA_3Q_CHECK.mdc` |
| 3 | 写 dna_violation_check.py + 注册 hooks.json | `python3 .cursor/hooks/dna_violation_check.py --self-test` 通过 | `.cursor/hooks/dna_violation_check.py` + `.cursor/hooks.json` |
| 4 | 跑 install.sh 验证 hook 加载 | 启动 log 出现 `[3Q-CHECK] loaded` | `install.sh` + 终端输出 |

---

## 4. v3 完成判定（Checklist）

- [ ] v3/PLAN.md 写入
- [ ] v3/decisions.json 写入（D-301 ~ D-303 三个决策 + decided=true）
- [ ] v3/open_questions.md 写入（Q-301 ~ Q-303 三个开放问题）
- [ ] DNA_3Q_CHECK.mdc 创建 + frontmatter 验证
- [ ] dna_violation_check.py 创建 + `--self-test` 通过
- [ ] hooks.json 注册 + `beforeRespond` 事件触发
- [ ] 跑 install.sh 看到 `[3Q-CHECK] loaded` 日志
- [ ] CHANGELOG 加 `[v3.0]` 段落
- [ ] 在 v2/open_questions.md 加"v3 转移"标记

---

## 5. 解决 / 新增 / 遗留

### 5.1 本次 v3 解决

- **DNA 软约束失效问题**——从"靠骂校准"升级到"软记录 + 临界点 block"
- **Agent 改约束文件前无停顿**——通过 L2 约束 + L3 机制强制"3 问自检"
- **v2 期间 3 个具体违规**（先动手 / 改动无影响范围 / 未做 3 问）——已记入 §0.1 触发事件

### 5.2 本次 v3 新增

- `governance/design_iter/plans/v3/PLAN.md`（本文件）
- `governance/design_iter/plans/v3/decisions.json`
- `governance/design_iter/plans/v3/open_questions.md`
- `governance/design_iter/plans/v3/resolved_questions.md`
- `governance/design_iter/plans/v3/changes/diff_v2_to_v3.md`（记录 3 问机制从软到硬的演化）
- `.cursor/rules/DNA_3Q_CHECK.mdc`（L2 约束）
- `.cursor/hooks/dna_violation_check.py`（L3 机制）
- `.cursor/hooks.json` 增量（`beforeSubmitPrompt` 事件 +1）
- `workflow_assets/feedback_logs/dna_violations.jsonl`（违规记录文件，运行时生成）

### 5.3 本次 v3 遗留（v4+ 评估）

- **L3 机制误判**——"⚠️ DNA 自检未通过"标记被 Agent 滥写 / 不写 → hook 失效
  - 缓解：v3.1 加"marker 必须包含具体违规描述"校验
- **临界点 3 次是否合适**——可能太松（3 次才 block）也可能太紧
  - 缓解：v3.1 加配置化（`DNA_VIOLATION_BLOCK_THRESHOLD=3` 环境变量）
- **AGENTS.md 是否也要加 3 问速查**——目前只有 L2 `.mdc` 必读
  - 待评估：AGENTS.md 加 3 问 vs 保持精简的权衡
- **hook 性能**——`beforeSubmitPrompt` 是 hot path，每次响应都跑
  - 缓解：v3.1 加"短路"——前 5 秒已检测就不重复检测
- **L1 vs L2 内容同步**——AGENTS.md 改 3 问措辞 → DNA_3Q_CHECK.mdc 也要改
  - 缓解：v3.1 加"双文件一致性 check"hook

---

## 6. 风险与回滚

### 6.1 主要风险

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| Agent 写不出东西（误判） | 中 | 高 | 软记录 + 临界点 block 折中 |
| Agent 完全忽略 L2（不读 mdc） | 低 | 中 | L3 hook 是兜底 |
| hook 启动报错 | 低 | 高 | `--self-test` 内置 |

### 6.2 回滚方案

```bash
# 整份回滚 v3
python3 governance/design_iter/scripts/design_iter.py rollback v2
```

### 6.3 部分回滚

- 删 DNA_3Q_CHECK.mdc → 回退到 L1-only（软约束）
- 删 dna_violation_check.py + 改 hooks.json → 回退到 L1+L2（无机制）
- 改 .mdc 的 `alwaysApply: true` → `false` → 仅手动读

---

## 6.5 决策密度标准（v3.1 候选规则）

> 背景：用户反馈"小狗先执行有偏差，人工审查成本高"——
> 根因 = 一次会话决策点过多，单次改动 8 文件 = ≥ 20 决策点。

### 6.5.1 核心规则

| 指标 | 阈值 | 超过 → |
|---|---|---|
| 单次响应文件改动数 | ≤ 3 个 | 列"决策表" + 必先 ask |
| 单次响应 tool call 数 | ≤ 10 个 | 停下来列"未完成项" |
| 单次响应里"未问先动"的工具调用 | 0 个 | **违规**（直接认错） |
| 决策点密度 | 改动数 × 平均决策/文件 ≤ 5 | 列决策表 |

### 6.5.2 决策表模板

每次动手前，**先用 AskQuestion 给 1 个"决策表"**——格式：

```
[改动 1] <文件>: <1 行说明>
   影响范围: <人/Agent/流水线>
   替代方案: <B 选项 1 行>

[改动 2] <文件>: <1 行说明>
   ...
```

### 6.5.3 A2 行为承诺（Agent 自约束，已在 DNA_3Q_CHECK.mdc §8 落地）

- 用户提任何事 → **先反问 1 个 AskQuestion**（澄清目标 / 列决策点）
- 用户答完 → 列决策表 → 用户点头 → 动手
- 单次改动 ≤ 3 文件（除非用户明确说"批量改"）
- 改完 → 报"diff 摘要 + 影响范围"（不超 5 行）

### 6.5.4 不增加 L3 hook 复杂度的原因

v3.0 §0.4 已论证 L3 hook 防不住"误读"型违规。
本次规则走 L1 + L2 层：DNA_3Q_CHECK.mdc §8 加"决策密度"段 + Agent 行为承诺。
**不写新 hook**——v3 §0.4 教训：**hook 不是答案，流程才是**。

### 6.5.5 与 v3 现有 L2 的关系

| 段 | 内容 | 状态 |
|---|---|---|
| §1 三问速查 | Q1/Q2/Q3 自检 | 已存在（v3.0） |
| §2 违规标记协议 | marker 协议 | 已存在（v3.0） |
| §3 约束 vs 知识对照 | 改之前/改之中/改之后 | 已存在（v3.0） |
| §8 决策密度标准 | 本节物化（v3.1） | **本轮新增** |

---

## 7. 关键引用

| 内容 | 路径 |
|---|---|
| DNA 总纲 | `AGENTS.md` |
| 跨阶段决策 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` |
| v3 决策记录 | `governance/design_iter/plans/v3/decisions.json` |
| v3 开放问题 | `governance/design_iter/plans/v3/open_questions.md` |
| v3→v2 diff | `governance/design_iter/plans/v3/changes/diff_v2_to_v3.md` |
| 触发事件 | 本文件 §0.1 |
| v1 / v2 起点 | `governance/design_iter/plans/{v1,v2}/PLAN.md` |


