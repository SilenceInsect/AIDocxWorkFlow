# AI 错误行为风险与治理手段 — 总览（决策占位骨架）

> **本档是 q_decision_table 占位骨架**——按 DNA_3Q_CHECK.mdc §9.5 落档协议，决策表内容先 Write 占位文件，再 content 展开。
> **落档路径**：`governance/design_iter/current/`
> **状态**：⏸️ **DRAFT** — 内容按用户提问结构展开（占位 → 实答）
> **关联**：v27 GOAL「AI 自治规则放宽 v1」是项目当前正在推的同类治理；本文档做**外部视角的全景梳理**，补足 v27 当前未覆盖的 3 类风险。

---

## 1. 用户提问锚定（Round 1 · 当前轮）

> **提问原文**："LLM 的目前只能以辅助工作的形式落到实际的生产环境，主要原因是因为 AI 的行为边界难以约束，比如 1. 误解意思，在错误的决策和方向快速推进，2. 改错内容，更严重的是错误覆盖和删除。列举 AI 错误的思考和行为带来的风险和 AI 行为的治理手段。"

**两类问题**：
- Q1：**AI 错误思考和行为的风险有哪些？**（按严重度分级枚举 + 本项目已实证案例）
- Q2：**治理手段有哪些？**（按"事前/事中/事后"分层 + 本项目已落地机制）

---

## 2. Q1 风险枚举（占位骨架 · 待 Round 2 充实）

### 2.1 风险严重度分级

| 级别 | 含义 | 典型表现 |
|---|---|---|
| 🔴 CRITICAL | 不可逆数据损失 / 不可撤回的对外动作 | 错误覆盖未提交代码、删除约束文件、commit 错账号 |
| 🟠 HIGH | 大量返工 / 业务正确性崩坏 | 误解需求快速产出错误 TC 集、S2 拆解错位 |
| 🟡 MEDIUM | 局部失效 / 人工审查成本飙升 | 约束文档与实现失配、Agent 仍按旧规则行动 |
| 🟢 LOW | 表面一致 / 暗字段残留 | JSON 多余字段、文档小漂移 |

### 2.2 三大典型错误模式（本项目已实证）

#### 模式 A：误解意图 + 快速推进（用户原文 #1）
- 现象：用户表达模糊时，Agent 默认"少改文件"/"先做完"，错方向快速铺开
- 本项目实证：`goal_s6_case_status_redefinition.md §6.4.3` 写"l2_s6 l2_mode 已实现"——**实测不符**，本轮 Round 14 才补齐（"自证错误"段）

#### 模式 B：改错内容（用户原文 #2）
- 现象：Agent 读到一半就开始动手，**把"候选规则"当"已发布硬约束"**
- 本项目实证：v6 教训，v17.1 实战中 Agent 把 §9.1 的"豁免条款"误用为"批量改通行证"

#### 模式 C：错误覆盖与删除（用户原文最严重）
- 现象：
  - 错误覆盖：`StrReplace` replace_all=False 但匹配到错误位置
  - 错误删除：`Delete` 工具 + 路径手抖
- 本项目实证：
  - `.gitignore` 内单行被覆盖 → `workflow_assets/` 不再忽略 → 过程资产意外入库
  - DNA §6 硬约束："**严禁覆盖未提交改动**"——正是为此设的

### 2.3 衍生风险

- **R-1 约束漂移**：实现改了，`.mdc` / `SKILL.md` / CHANGELOG 没同步 → 系统进入"双轨状态"
- **R-2 决策密度爆炸**：单 turn 改 10 个文件，每个都"局部最优" → 全局失配（§9.1 红线存在的原因）
- **R-3 自证错误传染**：Agent 在响应里"自证已通过" → 后续 Agent 接力时信以为真 → 错误扩散 3-4 轮才发现
- **R-4 落档协议违反**：决策表/计划只写在 response body → 下轮会话/其他 Agent 完全看不到
- **R-5 先答后验**：未 Read 就答 / 未 Read 就 commit → 凭上下文推断生成内容

---

## 3. Q2 治理手段枚举（占位骨架 · 待 Round 2 充实）

### 3.1 治理分层框架（事前 / 事中 / 事后）

#### A. 事前（Prevent）— 防患于未然

| 手段 | 本项目落地位置 |
|---|---|
| **A1. 决策密度红线**（单 turn 改 ≤ 3 文件） | `DNA_3Q_CHECK.mdc §9.1` + hook `dna_decision_density_check.py`（L3） |
| **A2. self-test 豁免条款**（避免红线误伤合法 self-test） | §9.1.1 |
| **A3. 5 问自检**（Q1 一致性 / Q2 设计 / Q3 全局 / Q4 约束 vs 知识 / Q5 人本可审查） | §1 |
| **A4. 先验后答约束**（写操作前必先 Read） | §9.4 |
| **A5. 落档协议**（决策表必先 Write 占位文件） | §9.5 |
| **A6. 分层 Read 优先级**（SSOT > 当前文件 > 历史快照） | §10.4 |
| **A7. 错误兜底白名单**（process_assets / resource / .gitignore 路径） | `.gitignore` + 治理档 |

#### B. 事中（Detect）— 实时阻断

| 手段 | 本项目落地位置 |
|---|---|
| **B1. L3 Hook 实时检测**（beforeFileEdit / sessionEnd / afterFileEdit） | `.cursor/hooks/*.py` |
| **B2. 内容合规检测**（版本号标签 / 禁止 JSON 字段 / ISO 时间戳） | `product_format_rules.yaml` SSOT + hook `content_compliance_check.py` |
| **B3. 决策落档检测**（sessionEnd 检查决策关键词 + 无 Write → block） | hook `dna_decision_persistence_check.py` |
| **B4. 并行 goal 隔离**（避免多 goal 撞车） | `goal_loop_serverchan_bridge.py` + `goal_parallel_executor.py` |

#### C. 事后（Recover / Learn）— 出错能挽回

| 手段 | 本项目落地位置 |
|---|---|
| **C1. Git 安全协议**（不 update config / 不 --force push / 不 --no-verify） | 通用约束（不存本项目规则档） |
| **C2. 强制备份**（关键写操作前 snapshot） | Round 12 §6.4.4"normalizer 不写回 JSON" + Round 14 P-001 保护 v3.01 JSON |
| **C3. 失败报告 + 阻断链路**（每个阶段 fail_report_S*.md） | `DESIGN_AND_EXECUTION_STANDARDS.mdc §2.4` |
| **C4. Goal-Loop 自迭代**（S7 审查 → S8 自迭代 → 知识库归档） | `STAGE_S8_SELF_ITERATION.mdc` + 治理档 v18 |
| **C5. CHANGELOG 强制**（每次变更必落版本条目） | `CHANGELOG.md` + §9.5 + `product_format_rules.yaml` exempt_files |
| **C6. 三步自问旁路**（bypass 必备案） | `DESIGN_AND_EXECUTION_STANDARDS.mdc §2.4.1` + `bypass_log.json` |
| **C7. 例外率监控**（bypass > 20% 黄 / > 40% 红） | §2.4.2 |

### 3.2 治理手段的"反模式"——同样要约束治理本身

- ❌ 把"加 hook"当银弹（hook 多了 = 性能瓶颈 + 维护负担）
- ❌ 阈值常量化但阈值数字硬编码（§4.3 SSOT 教训）
- ❌ 决策表落档但占位文件 0 字节（§9.5 违规但难发现）
- ❌ 自证"已通过"但没跑 self-test（Round 14 "自证错误"教训）

---

## 4. 决策表（Round 2 · 待充实）

（按 DNA §9.2 模板：改动 N 文件 → 影响范围 + 替代方案）
（本档是文档/治理梳理，不动代码，所以 §9.1 红线不触发；决策表仅做"是否扩档"判定）

---

## 5. 落档协议执行记录

### 5.1 Round 1（本轮）
- 触发：用户在父会话问"AI 错误风险 + 治理手段"
- 文件改动：1（`governance/design_iter/current/ai_error_risks_and_governance.md` 占位骨架）
- 下一步：Round 2 content 充实（§2 风险实证 + §3 治理手段映射 + §4 决策表）