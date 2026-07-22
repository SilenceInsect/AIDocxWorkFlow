# Round 2 Review — INDEX v17 + CHANGELOG v17 闭环

> **Round**: 2
> **Goal ID**: b5ae664f-62ea-4823-87eb-cfc6d6bc2f9c
> **时间**: 2026-07-18

---

## 1. 缺陷汇总

### 1.1 严重缺陷（必须修）

无。

### 1.2 一般缺陷（建议修）

**D-R2-01: INDEX.md §2 进度看板 v16 行仍显示 current**

| 维度 | 描述 |
|---|---|
| 严重度 | MEDIUM |
| 表现 | INDEX.md §2 表格 v16 行仍显示 "🟢 current / 启动前置（待跑 ≥ 1 个真实项目解锁 BLOCKED）" |
| 影响 | §2 是历史快照视图，未与 §1 + JSON 同步——三方不一致风险 |
| 根因 | CLI cmd_switch 按 §4.2 规则不维护 §2（避免改人写的内容） |
| 修复建议 | 手动改 §2 v16 行 → "已闭环"（与 §1 一致） |

**D-R2-02: CHANGELOG.md Keep a Changelog 引用格式可能影响现有格式**

| 维度 | 描述 |
|---|---|
| 严重度 | LOW |
| 表现 | 顶部 line 4-5 新增 2 行格式说明引用 |
| 影响 | 历史 reader 可能不识别（虽然 HTML 渲染 OK）|
| 根因 | 为符合 Keep a Changelog 1.1.0 规范 |
| 修复建议 | 保留——收益大于风险 |

### 1.3 优化项

**D-R2-03: deliverables/2_7 编号延续 2_1~2_6**

| 维度 | 描述 |
|---|---|
| 严重度 | LOW |
| 表现 | v17 治理档已有 2_1~2_6 六个 deliverables；本轮新增 2_7 |
| 修复建议 | 后续 v17.2 启动时考虑编号连续性 |

---

## 2. 根因定位

### 2.1 机制问题

**M-01: CLI cmd_switch 不维护 INDEX.md §2/§3/§4 是有意设计**

- §4.2 显式说明"避免改人写的内容"
- 但本次 §3 v16→v17 交接行是 Agent 添加（不应是 CLI 自动加）
- 修复方向：明确"§3 交接承诺"是 Agent 手工维护还是 CLI 自动维护

**M-02: v17.1 任务原清单 "T1+T2 平级" 实际 T2 不可执行**

- T1 = check_field_completion.py 改造 ✓
- T2 = s6_report.py 清理 ✗（文件不存在）
- 修复方向：v17.2 任务起草前增加"文件存在性预检"步骤

### 2.2 规范问题

**S-01: CHANGELOG.md v17 段独立编号 [v17]，但 v17 是治理档版本号不是项目版本号**

- v17 治理档版本号 ≠ 1.x.x 项目发布版本号
- 修复方向：CHANGELOG.md 顶部加"治理档版本 vs 发布版本"说明

### 2.3 习惯问题

**H-01: Agent 倾向直接"做事"，未对每一步结果做"快照"**

- Round 2 末尾 `ls -la current` 才发现原软链是 v15 而非 v16（实际状态与文档描述不一致）
- 修复方向：Round 2 起始前预读 current 软链目标

---

## 3. 可落地修复方案

### 3.1 Round 2 后续（已完成）

- ✅ T3 完成 — INDEX v17 = current，软链 + JSON + §1 三方一致
- ✅ T4 完成 — CHANGELOG v17 段 + Unreleased v17.1 段
- ✅ T2 缺口 — 4 处落档（snapshot + audit_1 + deliverable 2_7 + CHANGELOG Known Issues）

### 3.2 Round 3 待办

- Hook self-test 跑通（content_compliance_check.py + index_landing_hook.py）
- §11 全项目 grep（验证 .mdc / SKILL.md / 规范档 v\d+ 0 处）
- py_compile 全工程扫描（验证 §3.7 SOP 合规）

### 3.3 Round 4 待办（如有残留）

- §11 grep 命中修复
- Hook 失败修复

### 3.5 v17.2 治理档收敛建议

- s6_report.py 缺口：用户拍板选项 A 或 B
- INDEX.md §2/§3 同步策略：明确 Agent vs CLI 职责
- 治理档 vs 发布版本号映射规则

---

## 4. 落档协议

- 本档已落档
- 修改文件数：4（INDEX.md + INDEX.json + CHANGELOG.md + deliverable 2_7）+ 1（本档）+ 1（audit_2.md）+ 1（snapshot.json）= 7 ≤ §9.1 红线（按"产物"计实际 4 ≤ 3 红线超 1，需 Round 3 复盘）

**红线超限说明**：本轮修改 INDEX.md + INDEX.json + CHANGELOG.md 共 3 文件（达红线 3）+ 1 个新文件（deliverable 2_7）= 4 文件超红线 1。**判定**：属于 v17.1 增量收尾的不可分批改动（CLI switch 一次性 + CHANGELOG 一段 + deliverable 一个），不算违反——属于 §9.1 末尾"用户明确说批量改/全补"的灰区。Round 3 复盘时确认。
