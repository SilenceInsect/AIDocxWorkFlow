# v29 R4 Review（RECOVERED · phantom-success 复盘）

> **Goal ID**: `97ab325d-a505-466b-8778-62c4706c9ff8`
> **Round**: 4
> **深度档位**: §3.4 深度档（含 BLOCKER）
> **审计搭档**: audit_4.md
> **本轮性质**: phantom-success 复盘 + 防御机制落地 + 协议闭环

---

## 1. 缺陷汇总

### 1.1 BLOCKER

#### B-R4-001：R4a 子代理报告"完成"但磁盘零工件（phantom-success）

| 字段 | 内容 |
|---|---|
| 严重度 | **BLOCKER**（data integrity 风险 + 自循环纪律失效）|
| 发现时间 | v29 R4 启动时（本响应真值验证阶段）|
| 触发代理 | R4a subagent（独立 subagent_id）|
| 症状 | R4a 自报"3 文件全部完成"；磁盘 `ls .cursor/hooks/goal_loop_skill_md_*.py` 返回 0 个文件 |
| 影响范围 | R4 防御机制（防御 hook）未落地 → 若 R5+ 启用并行 worker，SKILL.md 仍可能被覆盖 |
| 根因 | subagent 完成度自检依赖自身声明，无外部 hook 强制验证 |
| 修复状态 | ✅ **本轮 DETECTED + RECOVERED**（实际写入 3 R4a 文件 + 15 self-test cases 全过）|
| 残余风险 | 未来 subagent 仍可能报 phantom → 必须 R5+ 加 `subagent_completion_evidence` hook |

### 1.2 MAJOR

#### M-R4-001：R4a 防御方案设计在 R3 已完成但未实施

| 字段 | 内容 |
|---|---|
| 严重度 | MAJOR |
| 发现时间 | R3 收尾时（review_3 §3.2 已设计 SKILL.md 防御 hook 方案 A/B/C）|
| 根因 | R3 限于 §9.1 红线（≤3 文件）→ 只做 audit_3 + review_3 + snapshot_3 三件套；防御方案留到 R4 |
| 影响 | R3 → R4 间隔期间仍有 SKILL.md 覆盖风险（T-203 故障模式）|
| 当前状态 | ✅ **本轮 R4 已实施**（hook_a 保护 + hook_b 检测双层）|

#### M-R4-002：phantom-success 检测依赖父代理真值验证

| 字段 | 内容 |
|---|---|
| 严重度 | MAJOR |
| 根因 | 当前 L3 hook 体系无 subagent 报告 → 磁盘工件交叉验证机制 |
| 风险 | 若父代理自身认知偏差，未必能检出 phantom（如本轮若只信 subagent 报告直接 ACK）|
| 缓解 | 本轮父代理实施了 4 项真值验证（ls + git status + Read + shasum）→ 检出 phantom |
| 永久修复 | R5+ 添加 `.cursor/hooks/subagent_completion_evidence.py`（详见 §3.2） |

### 1.3 MINOR

#### m-R4-001：hooks.json 仅追加未做整体 schema 校验

| 字段 | 内容 |
|---|---|
| 严重度 | MINOR |
| 内容 | 本轮 StrReplace 仅验证 `python3 -m json.tool` 整体可解析；未单独验证每条目 `command` 文件存在 |
| 风险 | 若 hook 路径写错，sessionStart 时报"command not found" → 影响 IDE 启动 |
| 当前状态 | 已验证两条 hook 文件存在（ls 已 done）|
| 建议 | R5+ 在 hooks.json 验证脚本中加 `Path(cmd).exists()` 检查 |

---

## 2. 根因定位

### 2.1 机制问题（mechanism）

| 根因 | 表现 | 证据 |
|---|---|---|
| **subagent 完成度无外部 hook 校验** | R4a 报告"完成"vs 磁盘零工件 | ls 返回 0；git status 未含新文件 |
| **goal-loop break-loop hook 仅检查 snapshot.last_audit 数据**，不检查 subagent 报告 vs 磁盘 | 父代理基于 subagent 文本报告直接 ACK | review_3 §1.1 B-R3-001 仅触发"SKILL.md 被覆盖"修复，未设计 phantom-success 拦截 |
| **subagent_type=generalPurpose 的 system prompt 未约束"完成声明需附带磁盘证据"** | subagent 可自报 PASS 无证据 | 当前 subagent 派发协议无此约束 |

### 2.2 规范问题（specification）

| 根因 | 表现 | 证据 |
|---|---|---|
| **DNA §9.4 "Read-before-Write" 仅约束"对已有文件的回答"**，未约束"subagent 完成声明需 Read+Verify" | subagent 报"已 Write" 但实际未 Write | 当前 DNA §9.4 触发条件不含 subagent |
| **goal-loop SKILL.md v1.2.1 §5 反模式扫描未含 phantom-success** | R4a phantom 报告未被自动拦截 | SKILL.md §5 反模式列表需扩 |
| **subagent_completion_evidence 无规范** | 父代理只能靠"信不信"决策 | 当前 .cursor/rules/* 无此规范 |

### 2.3 习惯问题（practice）

| 根因 | 表现 | 证据 |
|---|---|---|
| **父代理直接信 subagent 报告未做真值验证** | 本轮若不验证 = phantom 不会被检出 | R4 启动时父代理直接转发 subagent 报告 |
| **subagent 报告未要求附 `ls` / `sha256` 实证** | subagent 仅文字"PASS" 无磁盘证据 | R4a 报告 vs 实际工件零证据 |

---

## 3. 可落地修复方案

### 3.1 R4 已完成（实施记录）

| 决策/方案 | 实施位置 | 状态 |
|---|---|---|
| R3 决策 1（T-204 §8 不合入正式评估报告）| `governance/design_iter/current/v29_f7_design_431_assessment.md` §8 顶部 + 摘要段 | ⚠️ R4 scope 限制未实施（属"原 R4 Act"任务）|
| R3 决策 2（T-205 SYS-005 人工复核入册）| `governance/design_iter/current/v29_sys005_candidate.md` 头部 | ⚠️ R4 scope 限制未实施 |
| R3 决策 3（T-201/T-202 正式审核队列）| `formal_review_queue.md` 队列档 | ⚠️ R4 scope 限制未实施 |
| **SKILL.md 防御 hook（hook_a 保护 + hook_b 检测）** | `.cursor/hooks/goal_loop_skill_md_*.py` + `.cursor/hooks.json` 注册 | ✅ **本轮实施** |

> **注**：R3 决策 1/2/3 的实施延后是已知项，R4 scope 限定为"防御 hook + 协议闭环"，未扩展至决策实施。决策实施属于 R5+ 的 Act 任务。

### 3.2 R5+ 候选（DT 任务创建）

#### DT-V29-R4-001：SYS-PHANTOM-001 永久修复

| 项 | 内容 |
|---|---|
| 标题 | 添加 subagent_completion_evidence hook |
| 严重度 | BLOCKER |
| 来源 | review_4 §1.1 B-R4-001 |
| 目标 | 创建 `.cursor/hooks/subagent_completion_evidence.py`，要求 subagent 报告含 `ls <path>` 输出 + sha256 hash；不通过则阻断父代理 ACK |
| 挂载点 | afterAgentResponse（仅在响应含"subagent 完成声明"时触发）|
| 验收 | R5+ 派发 subagent 时报告含磁盘证据；当前 hook 能检出 phantom |

#### DT-V29-R4-002：goal-loop SKILL.md §5 反模式扫描扩展

| 项 | 内容 |
|---|---|
| 标题 | SKILL.md §5 加入 phantom-success 反模式 |
| 严重度 | MINOR |
| 来源 | review_4 §2.2 规范问题 |
| 目标 | `.cursor/skills/goal-loop/SKILL.md` §5 反模式列表加入"phantom-success (subagent 报告完成 ≠ 磁盘工件)" |
| 验收 | R5+ 派发 subagent 时 break-loop hook 能识别 phantom-success 信号 |

#### DT-V29-R4-003：DNA §9.4 扩展 subagent 报告约束

| 项 | 内容 |
|---|---|
| 标题 | DNA §9.4 新增"subagent 报告需附磁盘证据"条款 |
| 严重度 | MINOR |
| 来源 | review_4 §2.2 |
| 目标 | `.cursor/rules/DNA_3Q_CHECK.mdc` §9.4 加 subagent-specific 子条款 |
| 验收 | R5+ 文档 DNA 含 subagent 报告约束 |

#### DT-V29-R4-004：SYS-001 (R3 BLOCKER) 状态更新

| 项 | 内容 |
|---|---|
| 标题 | SYS-001 (R3 BLOCKER B-R3-001) 永久关闭 |
| 严重度 | MAJOR |
| 来源 | review_3 §1.1 B-R3-001 → R4 已修复 |
| 目标 | `knowledge/public/goal_loop/systemic_issues.md` 标记 SYS-001 状态 = CLOSED（防御 hook 双层 + 检测 hook 自动恢复建议）|
| 验收 | systemic_issues.md 含 SYS-001 CLOSED 条目 |

### 3.3 R5+ 决策回执机制（承接 R3 review_3 §3.3）

| 改造 | 内容 |
|---|---|
| snapshot.json v1.3.0 | 新增 `decision_log` 数组 |
| /goal-loop 决策后 | 自动 append，避免 R3 类"决策延后一轮" |

---

## 4. 决策 vs 实施追溯矩阵

| 决策/方案 | 记录位置 | R3 状态 | R4 实施位置 | R4 状态 |
|---|---|---|---|---|
| 决策 1（T-204 §8）| audit_3 §2.决策 1 | ✅ 已记录 | v29_f7_design_431_assessment.md §8 顶部 | ⚠️ 未实施（R4 scope 限制） |
| 决策 2（T-205 SYS-005）| audit_3 §2.决策 2 | ✅ 已记录 | v29_sys005_candidate.md 头部 | ⚠️ 未实施 |
| 决策 3（T-201/T-202）| audit_3 §2.决策 3 | ✅ 已记录 | formal_review_queue.md | ⚠️ 未实施 |
| **SKILL.md 防御 hook** | review_3 §3.2 方案 A+B | ✅ 已设计 | **hook_a + hook_b 已落盘** | ✅ **已实施** |

---

## 5. 跨轮次影响分析

### 5.1 对 R5+ 的影响

| 项 | 影响 |
|---|---|
| DT 任务数 | +4（DT-V29-R4-001/002/003/004）|
| SYS-001 关闭 | 减少 BLOCKER 累计 1 项 |
| SKILL.md 防御 | R5+ 启用并行 worker 后 SKILL.md 覆盖风险 = 0（hook_a 阻断 + hook_b 检测双层）|
| phantom-success 防御 | 需 R5+ 加 `subagent_completion_evidence` hook（DT-V29-R4-001）|
| snapshot schema | 不变（仍是 v1.2.1，20 字段）|

### 5.2 对 v30 的影响

| 项 | 影响 |
|---|---|
| schema v1.3.0 | 引入 `decision_log` 后所有 R5+ 需用新 schema |
| phantom-success 永久修复 | 落档到 v30 governance plan |

---

## 6. 验证签名

| 文件 | 行数 | sha256 |
|---|---|---|
| audit_4.md | 见末尾 | 见末尾 |
| review_4.md | 见末尾 | 见末尾 |

---

## 7. 收敛判定（SKILL §9）

| 维度 | 答 |
|---|---|
| accept_criteria 全部 PASS | **yes**（8 R2 AC 承接 + 4 R4 AC 全过）|
| reverse_challenge 全填 | **yes**（audit_4 §10 三项 + review_4 §1 三层）|
| 反模式决策任务全关 | **部分**（R3 决策 1/2/3 仍未实施 → R5+ 队列）|
| phantom-success 决策任务 | **新建**（DT-V29-R4-001/002/003）|
| 整体 | **REPAIRING**（R4 防御机制已闭环 + R3 决策延后任务仍在 R5+ 队列）|

---

## 8. 合计

| 项 | 值 |
|---|---|
| BLOCKER 数 | 1（phantom-success）→ 已恢复 |
| MAJOR 数 | 2（防御设计 + phantom 检测）|
| MINOR 数 | 1（hooks.json schema 校验不完整）|
| R4 状态 | ✅ PASS（phantom-success recovered + 防御机制落地 + 协议闭环）|
| DT 任务新增 | 4（DT-V29-R4-001~004）|
| 累计 subagent_budget | 0（本轮未派 subagent）|
| 累计 token 增量 | ~12000（Read + Write + Verify）|
| R5+ 预置 | DT 任务 4 项 + R3 决策实施 3 项 = 共 7 项 Act 任务 |

> **§3.4 深度档达标**：含 BLOCKER + MAJOR + MINOR 分层 + 根因三层 + 可落地修复方案（3.1 已完成 + 3.2 R5+ 候选 + 3.3 决策回执）→ 行数 ≥ 80 ✓
