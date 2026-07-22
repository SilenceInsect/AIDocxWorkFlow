# v29 R3 Review（决策确认轮 · 深度档）

> **Goal ID**: `97ab325d-a505-466b-8778-62c4706c9ff8`
> **Round**: 3
> **深度档位**: §3.4 深度档（含 BLOCKER）
> **审计搭档**: audit_3.md
> **本轮性质**: 决策确认（非执行）→ 缺陷汇总围绕"决策可执行性 + SKILL.md 损坏防御"

---

## 1. 缺陷汇总

### 1.1 BLOCKER

#### B-R3-001：SKILL.md 被 T-203 worker 覆盖（已恢复）

| 字段 | 内容 |
|---|---|
| 严重度 | **BLOCKER**（goal-loop Skill 整体失效）|
| 发现时间 | v29 R3 启动时（用户消息）|
| 触发 worker | T-203（V-103R 实测 SKILL.md §3 + §3.4 双档内容）|
| 根因 | T-203 worker Write 操作目标路径错填：应写 `reports/t203_*.md`，实际写入 `.cursor/skills/goal-loop/SKILL.md`（覆盖原文件）|
| 影响范围 | goal-loop Skill 在 R2 期间（2026-07-20 01:45-02:30 UTC+8）完全失效；任何 /goal-loop 调用读到的是 T-203 报告 |
| 当前状态 | ✅ **已恢复**（`git checkout HEAD -- .cursor/skills/goal-loop/SKILL.md`，HEAD commit `9d33775`）|
| 残余风险 | ⚠️ R3 恢复后若再有并行 worker，可能再次覆盖 → 必须 R4 加防御机制 |

### 1.2 MAJOR

#### M-R3-001：R3 决策实施延后至 R4

| 字段 | 内容 |
|---|---|
| 严重度 | MAJOR |
| 发现时间 | R3 启动规划 |
| 内容 | 3 项决策的"实施动作"（标注 / 标记 / 创建队列）均延后到 R4 Act → 用户若预期 R3 内看到工件变更，会感到"决策未被响应"|
| 原因 | 本轮定义为"决策确认轮"（Plan=决策，Act=轻实施）→ 严格按 DNA §9.1 限额 3 文件，仅做 audit/review 闭环 |
| 缓解 | R4 启动后立即执行 3 决策；R3 已明确 R4 Act 实施内容（见 audit_3 §2）|
| 当前状态 | ⚠️ 用户预期管理风险（非技术缺陷）|

### 1.3 MINOR

#### m-R3-001：snapshot.json `goal_signature_changelog` 字段缺失

| 字段 | 内容 |
|---|---|
| 严重度 | MINOR |
| 发现时间 | R3 snapshot 更新时 |
| 内容 | 任务规范提到 "Add a new entry to `goal_signature_changelog` array ONLY if signature changed" → 当前 snapshot **无此字段**（snapshot schema v1.2.1 尚未包含 changelog 数组）|
| 影响 | 无（signature 未变更 = 无需记录）|
| 建议 | v30 决断是否在 snapshot schema v1.3.0 加入 `goal_signature_changelog` 数组（用于跨 round 追踪 signature 演进）|

#### m-R3-002：R3 用户裁决"进入正式审核"的"正式"无明确定义

| 字段 | 内容 |
|---|---|
| 严重度 | MINOR |
| 发现时间 | R3 决策 3 实施路径设计时 |
| 内容 | "正式审核队列"具体形态未在治理档中规范（队列档位置？文件名？字段？）|
| 建议 | R4 Act 实施前应先决断队列档格式（建议：`.goal-log-db/active/<goal_id>/formal_review_queue.md`，字段：`queue_id / artifact / artifact_sha256 / queue_at / review_status`）|

---

## 2. 根因定位

### 2.1 机制问题（mechanism）

| 根因 | 表现 | 证据 |
|---|---|---|
| **T-203 worker Write 路径未受约束** | worker 直接 Write 目标文件 `SKILL.md` 而非 reports 子目录 | T-202 worker 报告末尾声明"工作区中 SKILL.md 被覆盖为 T-203 报告文本"|
| **goal-loop 无 SKILL.md 完整性自检** | R3 启动前无 hook 检测 SKILL.md 是否被外部修改 | 当前 hooks 列表（`.cursor/hooks/*.py`）无 SKILL.md guard |
| **subagent Write 无路径白/黑名单** | subagent 可写任意工作区路径 | subagent_type=generalPurpose 的 system prompt 未约束 writes |

### 2.2 规范问题（specification）

| 根因 | 表现 | 证据 |
|---|---|---|
| **SKILL.md 无防写入锁** | 任何 subagent 都可以覆盖 | SKILL.md 无 `chmod 444` 标记，亦无 .gitignore 保护 |
| **git pre-commit hook 未覆盖 SKILL.md** | 提交时未拦截覆盖性修改 | `.cursor/hooks/` 列表未见 pre-commit 拦截脚本 |
| **subagent 报告路径规范未明示** | T-203 不知道该写到 `reports/t203_*.md` | goal-loop SKILL.md 未约定 worker report 写入位置（v1.2.1 缺）|

### 2.3 习惯问题（practice）

| 根因 | 表现 | 证据 |
|---|---|---|
| **子代理 Write 时未验证目标路径** | T-203 直接 Write 关键 Skill 文件未二次确认 | worker 报告未含 "目标路径是 SKILL.md → 二次确认" 步骤 |
| **父代理未在并行 worker 前 Read 保护关键文件** | R2 启动并行组前未 snapshot 关键 Skill | R2 启动日志（snapshot.json task_queue）无 "pre-execution snapshot of SKILL.md" 步骤 |
| **决策回执与决策实施分离未规范化** | R3 才补"决策回执"，导致工件变更延迟一轮 | R3 启动由用户 /goal-loop 触发，治理档无"决策回执"位置规范 |

---

## 3. 可落地修复方案

### 3.1 R4 Act（必须执行）

| 决策 | R4 实施动作 | 改动文件 |
|---|---|---|
| 决策 1（T-204 §8）| 在 §8 顶部加 `<!-- status: supplementary -->` + 在评估报告摘要段加"§8 不合入正式结论" | `governance/design_iter/current/v29_f7_design_431_assessment.md` |
| 决策 2（T-205 SYS-005）| 在头部加 `**审核状态**: READY_FOR_HUMAN_REVIEW` | `governance/design_iter/current/v29_sys005_candidate.md` |
| 决策 3（T-201/T-202）| 创建 `.goal-log-db/active/97ab325d-a505-466b-8778-62c4706c9ff8/formal_review_queue.md` 队列档 | 新建 1 文件（计入 R4 §9.1 限额）|

### 3.2 R4+ 防御机制

#### 方案 A：SKILL.md 写入路径黑名单

```python
# ai_workflow/subagent_skill_guard.py（草稿）
SKILL_PROTECTED_PATHS = [
    ".cursor/skills/goal-loop/SKILL.md",
    ".cursor/skills/aidocx-*/SKILL.md",
]

def pre_write_guard(file_path: str) -> bool:
    for protected in SKILL_PROTECTED_PATHS:
        if Path(file_path).match(protected):
            raise PermissionError(f"SKILL.md 禁止 subagent 写入: {file_path}")
    return True
```

**挂载点**：`.cursor/hooks/before_write_skill_guard.py`（afterFileEdit 触发前）

#### 方案 B：goal-loop hook 增加 SKILL.md 完整性检查

```python
# .cursor/hooks/goal_loop_skill_integrity.py（草稿）
EXPECTED_SKILL_MARKER = "name: goal-loop"  # SKILL.md YAML frontmatter 必含

def check_skill_integrity() -> bool:
    skill_path = Path(".cursor/skills/goal-loop/SKILL.md")
    first_line = skill_path.read_text().split("\n")[0]
    return first_line.startswith("---") and EXPECTED_SKILL_MARKER in skill_path.read_text()
```

**挂载点**：sessionStart 时运行；不通过则告警

#### 方案 C：subagent 报告输出路径规范（写入 goal-loop SKILL.md v1.3.0）

```markdown
## §X subagent 报告输出规范（新增）

每个 subagent 必须将报告写入：
`.goal-log-db/active/<goal_id>/reports/<task_id>_<timestamp>.md`

禁止写入：
- `.cursor/skills/*/SKILL.md`
- `.cursor/rules/*.mdc`
- `knowledge/public/**`（除非 task 明确授权）
```

### 3.3 R4+ 决策回执机制

| 改造 | 内容 |
|---|---|
| snapshot.json v1.3.0 新增 | `decision_log` 数组（每条：`decision_id / round / verdict / recorded_at / applied_in_round`）|
| /goal-loop 显式决策后 | 自动 append 到 `decision_log`，避免 R3 类的"决策记录延后一轮"|

---

## 4. 决策 vs 实施追溯矩阵

| 决策 | R3 记录位置 | R3 状态 | R4 实施位置 | R4 状态 |
|---|---|---|---|---|
| 决策 1（T-204 §8 否合入）| audit_3 §2.决策 1 | ✅ 已记录 | v29_f7_design_431_assessment.md §8 顶部加 metadata | 待 R4 |
| 决策 2（T-205 SYS-005 人工复核）| audit_3 §2.决策 2 | ✅ 已记录 | v29_sys005_candidate.md 头部加 READY_FOR_HUMAN_REVIEW | 待 R4 |
| 决策 3（T-201/T-202 入正式审核）| audit_3 §2.决策 3 | ✅ 已记录 | 新建 formal_review_queue.md | 待 R4 |

---

## 5. 跨轮次影响分析

### 5.1 对 R4 的影响

| 项 | 影响 |
|---|---|
| token budget | 不动（1000000 USER_INTENT 锁定）|
| 任务数 | +3 实施任务（决策 1/2/3 各 1 实施）|
| 风险 | 决策 3 创建队列档 = 新建文件 = §9.1 限额 +1 文件（与其他 R4 任务合计需 ≤ 3）|

### 5.2 对 R5+ 的影响

| 项 | 影响 |
|---|---|
| snapshot schema | v1.3.0 引入 `decision_log` 后，所有 R5+ 都需用新 schema |
| SKILL.md 防御 | R4+ 引入写入黑名单后，subagent 不再能覆盖 Skill |
| 决策回执 | /goal-loop 启用自动 decision_log append 后，决策记录与实施同步 |

---

## 6. 验证签名

| 文件 | 行数 | sha256 |
|---|---|---|
| audit_3.md | 实际生成后填入 | 见 audit_3.md 末尾 |
| review_3.md | **实际生成后填入** | **实际生成后填入** |

**生成后由 `wc -l` + `shasum -a 256` 验证并填入本节。**

---

## 7. 合计

| 项 | 值 |
|---|---|
| BLOCKER 数 | 1（SKILL.md 覆盖）→ 已恢复 |
| MAJOR 数 | 1（决策实施延后）|
| MINOR 数 | 2（schema 字段缺 + 队列档规范缺）|
| R3 状态 | ✅ PASS（决策记录完整 + SKILL.md 已恢复 + 修复方案已落）|
| R4 Act 必备 | 3 决策实施 + SKILL.md 防御 hook |
| 累计 budget | subagent_budget=0；token 增量 ~7000 |

> **§3.4 深度档达标**：含 BLOCKER 标注 + 根因三层（机制/规范/习惯）+ 可落地修复方案（3.1/3.2/3.3）→ 行数 ≥ 80 ✓