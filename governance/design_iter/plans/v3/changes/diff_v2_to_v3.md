# v2 → v3 diff

> 本文件记录 v2 → v3 的关键差异——v3 主要是 DNA 物化机制，不改 v2 业务功能。

## 1. 设计哲学变化

| 维度 | v2 | v3 |
|---|---|---|
| 核心问题 | "5 决策 + 4 步迁移" | "DNA 软约束失效 → 硬机制" |
| 触发 | v1 暴露的 14 项规则不一致 | v2 实施期 Agent 违反 AGENTS.md 铁律 |
| 方案性质 | 业务功能改造 | Agent 自我约束机制 |
| 决策数 | 5 决策（D-101~D-105） | 3 决策（D-301~D-303） |

## 2. 文件变化（v2 → v3）

| 文件 | v2 状态 | v3 状态 | 变化 |
|---|---|---|---|
| `AGENTS.md` | 60 行（DNA 总纲） | 60 行（**不动**） | 无 |
| `.cursor/rules/*.mdc` | 12 份（STAGE_S* + DESIGN + SKILL） | 13 份（+1 DNA_3Q_CHECK.mdc） | +1 |
| `.cursor/hooks/*.py` | 6 份（含 codegraph_sync） | 7 份（+1 dna_violation_check.py） | +1 |
| `.cursor/hooks.json` | beforeFileEdit + afterFileEdit + sessionStart + beforeSubmitPrompt + sessionEnd | 同上 + beforeSubmitPrompt 加 1 处理器 | +1 entry |
| `install.sh` | 5 步（+ git hooks step） | 5 步（**不动**） | 无 |
| `.githooks/` | 3 个 git hook + README | 不动 | 无 |

## 3. 关键设计对比

### 3.1 DNA 约束强度

| 层级 | v2 强度 | v3 强度 |
|---|---|---|
| L1 知识（AGENTS.md） | Agent 读不读 = 0 强制 | 同 v2 |
| L2 约束（`.cursor/rules/*.mdc`） | onlyApply 不一定 | alwaysApply 必读（DNA_3Q_CHECK.mdc） |
| L3 机制（hooks） | 无 | 软记录 + 临界点 block |

### 3.2 违规处理

| 违规类型 | v2 处理 | v3 处理 |
|---|---|---|
| 先动手再问 | 用户骂 + Agent 道歉 | hook stderr 警告 + 连续 3 次 block |
| 改动无影响范围 | 用户问 + Agent 补述 | hook stderr 警告 |
| 未做 3 问自检 | 用户提示 + Agent 重做 | hook 主动检测响应里"⚠️ DNA 自检未通过" |

## 4. 不变项（v2 → v3 不改）

- 9 阶段流水线（S1 ~ S8）
- install.sh 5 步流程
- codegraph 同步机制（v2 新增 +1 step）
- git hooks 启用（v2 新增）
- 12 份 STAGE_S*.mdc
- 12 个 SKILL.md
- 8 模块 SSOT（.cursor/MODULES.md）
- v2 完成的 5 决策（D-101~D-105）

## 5. v3 新增文件清单

```
governance/design_iter/plans/v3/
├── PLAN.md                              # 3 问自检物化方案
├── decisions.json                       # D-301 ~ D-303
├── open_questions.md                    # Q-304 ~ Q-309（v3.1 评估）
├── resolved_questions.md                # 3 决策落地记录
└── changes/diff_v2_to_v3.md             # 本文件

.cursor/rules/
└── DNA_3Q_CHECK.mdc                     # L2 约束（alwaysApply）

.cursor/hooks/
└── dna_violation_check.py           # L3 机制（软记录 + 临界点 block）
```

## 6. 兼容性

- **AGENTS.md 兼容性**：v3 不改 AGENTS.md，所有依赖 DNA 总纲的代码/规则继续工作
- **hooks 兼容性**：v3 在 `beforeSubmitPrompt` 事件上**追加** 1 个处理器，不替换任何现有处理器
- **install.sh 兼容性**：v3 不改 install.sh，5 步流程继续
- **回滚路径**：`python3 governance/design_iter/scripts/design_iter.py rollback v2` 一键回退

---

## 7. v3.0 → v3.1 增量（决策密度标准）

> v3.0 → v3.1 是**非破坏性增量**——不替换 v3.0 任何内容，只补"决策密度"层。

### 7.1 触发

v3.0 实施期（2026-06-19 凌晨），Agent 单次响应改 8 文件 = ≥ 20 决策点。
用户反馈："小狗先执行有偏差，人工审查成本高"。
v3.0 的"3 问自检"防的是"违规不自知"型——**防不了"单次动作决策点过多"**型。

### 7.2 设计

| 维度 | v3.0 | v3.1 |
|---|---|---|
| 核心问题 | "Agent 不知道自己违规" | "Agent 改太多不知先 ask" |
| 解决方案 | L1 知识 + L2 约束 + L3 机制 | + **决策密度阈值** + **决策表模板** + **A2 行为承诺** |
| 阈值 | 无 | **单次响应 ≤ 3 文件改动** |
| Agent 行为 | 自觉做 3 问 | **先 ask 决策点 → 列决策表 → 动手** |
| L3 hook | 软记录 + 临界点 block | **不动**（v3.0 §0.4 教训） |

### 7.3 文件变化（v3.0 → v3.1）

| 文件 | v3.0 | v3.1 |
|---|---|---|
| `AGENTS.md` | 60 行（DNA 总纲） | 60 行（**不动**） |
| `DNA_3Q_CHECK.mdc` | 6 段（§1-§6） | 7 段（+§7 决策密度标准，§8 重命名原"关键引用"） |
| `dna_violation_check.py` | 211 行 | 211 行（**不动**） |
| `v3/PLAN.md` | §1-§7 | §1-§7 + **§6.5 决策密度标准**（v3.1 候选规则） |
| `v3/decisions.json` | D-301~D-303 | + **D-304**（决策密度 = v3.1 新决策） |
| `v3/open_questions.md` | Q-304~Q-309 | + **Q-310~Q-313**（v3.1 决策源 + 3 开放） |

### 7.4 不变项（v3.0 → v3.1 不改）

- L3 hook 行为（软记录 + 临界点 block 不变）
- AGENTS.md（≤ 60 行不动）
- 9 阶段流水线
- install.sh
- v3.0 完成的 3 决策（D-301~D-303）

### 7.5 兼容性

- **DNA_3Q_CHECK.mdc 兼容性**：v3.1 在 §6 后**追加** §7，不替换任何现有段
- **decisions.json 兼容性**：v3.1 **追加** D-304，保留 D-301~D-303
- **回滚路径**：删除 §7 + D-304 + §6.5 + Q-310~Q-313 即可回退到 v3.0
