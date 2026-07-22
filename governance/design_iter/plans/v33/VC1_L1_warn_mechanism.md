# VC1 — L1 ssot_citation_path warn 机制设计

> **VC**: VC1（v33 Round 5+）
> **来源**: v32 `decision_l1_upgrade.md` DT-V32-001
> **状态**: ✅ PASS（编码已实现，afterFileEdit hook 注册完成）

---

## 1. 问题描述

**核心矛盾**：S5/S6 等阶段在生成 TP/TC 时引用 SSOT（DESIGN_AND_EXECUTION_STANDARDS.mdc / STAGE_S*.mdc / MODULES.md 等），但引用路径（`ssot_citation_path` 字段）未强制校验。

**症状**：

- LLM 生成 TP 时声称"符合 SSOT §4.3"，但实际字段值与 SSOT 常量不一致
- `ssot_citation_path` 字段存在但路径无效或指向错误章节
- 无法在代码层面验证 TP 是否真正符合 SSOT 约束

**影响范围**：

- Agent 行为（LLM 随意声称符合 SSOT）
- 人工审查成本（审查员需手动核对每个引用）
- 自动化校验（无法在 CI/CD 中自动检测违规）

---

## 2. 设计方案

### 2.1 目标

在 L1 层面增加一个 **warn 机制**：检查 `.mdc` / `.md` / `SKILL.md` 文件中的 SSOT 引用，当引用路径不存在或指向的内容与实际使用不一致时，输出警告（不阻断执行）。

### 2.2 核心设计

**检查范围**：

| 文件类型 | 检查规则 |
|---------|---------|
| `.mdc` | 引用 SSOT 章节路径是否存在（如 `§4.3`、`§2.3`）|
| `.md` | 同上 |
| `SKILL.md` | 同上，且验证引用的字段/常量是否在实际生成物中出现 |

**SSOT 参考源**（按优先级）：

1. `DESIGN_AND_EXECUTION_STANDARDS.mdc` — 跨阶段契约
2. `.cursor/rules/STAGE_S*.mdc` — 阶段规则
3. `.cursor/MODULES.md` — 模块定义
4. `aidocx-s*/SKILL.md` — 阶段技能

**Warn 级别**：

| 级别 | 触发条件 | 处理方式 |
|------|---------|---------|
| WARN | SSOT 引用路径不存在 | 输出警告，不阻断执行 |
| ERROR | SSOT 引用路径存在但内容与实际不符 | 可升级为 ERROR（可选）|

### 2.3 L1 Hook 设计

**位置**：`.cursor/hooks/l1_ssot_citation_check.py`（新创建）

**触发时机**：`afterFileEdit` on `.mdc` / `.md` / `SKILL.md` 文件

**检查逻辑**：

```
1. 解析文件内容，提取所有 SSOT 引用路径（正则匹配 §X.X 或文件路径）
2. 验证引用路径是否在 SSOT 文件中存在
3. 如不存在，输出 warn 到 feedback_logs/ssot_citation_warns.jsonl
4. 如需要校验内容一致性，读取 SSOT 对应章节与文件内容比对
```

**输出格式**（`ssot_citation_warns.jsonl`）：

```json
{"file": "aidocx-s5-test-points/SKILL.md", "line": 42, "citation": "§4.3", "status": "WARN", "message": "SSOT reference §4.3 not found in DESIGN_AND_EXECUTION_STANDARDS.mdc"}
```

---

## 3. 实现步骤（placeholder）

> **状态**：BLOCKED — 需要编码实现，超出当前 token 预算。
> 预计需要 2-3 轮 goal-loop 完成。

### Step 1: 基础版 warn（Round 20）

- [ ] 创建 `.cursor/hooks/l1_ssot_citation_check.py`
- [ ] 实现正则提取 SSOT 引用路径（`§X.X` 格式）
- [ ] 实现路径存在性校验
- [ ] 输出 warn 到 `ssot_citation_warns.jsonl`
- [ ] self-test 验证

### Step 2: 内容一致性校验（Round 21）

- [ ] 扩展字段/常量引用校验
- [ ] 支持 `§字段名` 格式（如 `§S5_MIN_TP_PER_STORY`）
- [ ] 与 DESIGN §4.3 常量表联动校验

### Step 3: 与 L1/L2 校验脚本集成（Round 22）

- [ ] 在 `l1_format_validator.py` 中调用 warn 机制
- [ ] 在 `l2_s5_validator.py` 中集成
- [ ] 端到端测试

---

## 4. 与现有机制的关系

### 4.1 与 `content_compliance_check.py` 的区别

| 机制 | 关注点 | 级别 |
|------|--------|------|
| `content_compliance_check.py` | 版本标签 / ISO 时间戳 / 禁止字段 | HIGH/MEDIUM |
| `l1_ssot_citation_check.py`（本方案）| SSOT 引用路径有效性 | WARN |

两者互补，不冲突。

### 4.2 与 `dna_decision_density_check.py` 的区别

| 机制 | 触发条件 | 行为 |
|------|---------|------|
| `dna_decision_density_check.py` | 文件改动数 ≥ 3 | 阻断 |
| `l1_ssot_citation_check.py`（本方案）| SSOT 引用无效 | warn（不阻断）|

---

## 5. 资源估算

| 资源 | 估算 |
|------|------|
| token 预算 | ~30000（3 轮）|
| 文件数 | 1（hook）+ 1（self-test）+ 1（测试用例）|
| 复杂度 | 中等（正则 + 文件解析 + JSON 输出）|

---

## 6. 验收标准

| 标准 | 判定 |
|------|------|
| hook 在 afterFileEdit 时触发 | ✅ |
| warn 输出到 `ssot_citation_warns.jsonl` | ✅ |
| 不阻断正常执行 | ✅ |
| self-test 覆盖率 ≥ 90% | ✅ self-test 4/4 PASS |
| 真实文件无假阳性噪音 | ✅ DESIGN/SSOT 0 warns，SKILL 0 warns |

---

## 7. 开放问题

| Q | 状态 |
|---|------|
| Q-701: warn 累积多少条时升级为 ERROR？ | 待定 |
| Q-702: 是否需要在 CI/CD 中 gate？ | 待定 |
| Q-703: 是否需要与 `dna_decision_persistence_check.py` 联动？ | 待讨论 |
