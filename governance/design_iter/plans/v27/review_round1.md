# review_round1.md — v27 Round 1 复盘

**Goal ID**: 9b1ca386-de47-4d0a-bd60-0206781429be
**复盘日期**: 2026-07-20
**Round**: 1
**status**: converged_with_followup

---

## §1 缺陷汇总（去重 · 按严重度排序）

### BLOCKER（0）
全部 BLOCKER PASS，无遗留。

### MAJOR（0）
全部 MAJOR PASS，无遗留。

### MINOR（1）

| # | 描述 | 建议修复 | 来源 |
|---|---|---|---|
| M-1 | DESIGN §2.4.2（206/208/211/220/235 行）+ §5.1（618-619 行）含示例性阈值字面值（7.0 / 90% / 20% / 0.20） | v28+ 阶段将示例数字改为「如 §4.3 配置所示」索引格式；纯文档清理不影响 v27 设计意图 | V-101 grep 冲突 → DT-V27-001 决策方案 B |

---

## §2 根因定位（机制 / 规范 / 习惯）

### 根因 R1：v27 GOAL.md 内在矛盾
**类型**：机制问题（goal-loop 契约 + 反模式防御的双向锁）
**现象**：
- v27 §1 第 1 行 = "§2.3 不列阈值"
- v27 out_of_scope §1 = "不动 §4.3 之外其他无关章节"

→ 严格 grep「字面值只在 §4.3」会把 §2.4.2 / §5.1 的"示例性数字"也视作违规
**根因**：v27 任务契约未明确"§2.4.2 / §5.1 的示例数字是知识性内容不在 SSOT 范畴"
**影响**：T-101 worker 报 V-101 FAIL（严格按字面），但实质 PASS（按设计意图）
**处置**：DT-V27-001 决策选方案 B（核心修复 PASS + MINOR follow_up）+ 写 v27 §2 决策表 + 写本 review §3

### 根因 R2：C2/C4 治理档"已完成"vs 缺独立 verification
**类型**：习惯问题（用户决策与执行落档不对称）
**现象**：v27 §1 第 3/4 行写"已实现/已完成"但本轮才补守卫/验证
**根因**：用户拍板时已确认状态，但治理档缺少 verifier anchor
**影响**：T-103/T-104 worker 跑验证（不是新 patch），但产物有效
**处置**：v27_c2_guard.md + t106_v301_regression_20260720.md + T-104 自验证报告 — 治理档闭环

### 根因 R3：任务描述路径错误
**类型**：习惯问题（父会话规划时未实地 Read）
**现象**：T-106 任务描述写 `ai_workflow/l1_s6.py` 但实际在 `ai_workflow/validators/l1_s6.py`
**根因**：v27 GOAL §1 第 4 行未指定路径
**影响**：T-106 worker 自行纠正，无技术阻塞
**处置**：写入 t106 报告 + AI 工作流 README 待补（v28+ follow_up）

### 根因 R4：T-102 决策调整 2 反父任务字面计划
**类型**：机制问题（worker 自治 vs 父会话契约）
**现象**：父任务要求"全局阈值覆盖段"，worker 改成"per-hook 详解节"
**根因**：worker 守 README 一致性原则（per-hook 模式），但与父任务字面冲突
**影响**：V-103 PASS 但语义偏离
**处置**：T-102 落档决策表 + 本 review §3 标注 — 父会话接受 per-hook 模式

---

## §3 可落地修复方案（明确下一步动作 + 影响范围）

### v28+ follow_up_items（已写入 snapshot）

| # | 描述 | 严重度 | 建议修复 | 影响范围 |
|---|---|---|---|---|
| F-1 | DESIGN §2.4.2 / §5.1 示例性数字清理 | MINOR | v28+ 阶段改为索引格式 | 仅文档清理，不影响 v27 设计意图 |

### v28+ carry（来自 v27 GOAL §2）

| # | 描述 | 来源 |
|---|---|---|
| F-2 | v17 5 项约束放宽（fp_name / steps[] / test_method[] / tp_reference / preconditions[]） | v27 §2 Out of Scope |
| F-3 | D1-D3 goal-loop 早期约束放宽 | v27 §2 Out of Scope |
| F-4 | B2/B4 业务门禁放宽（A 组中优 / E 组） | v27 §2 Out of Scope |
| F-5 | A1/A3/A4/B3 内部冗余合并 | v27 §2 Out of Scope |

### v28+ 反模式防御建议（GL-004）

| # | 建议 | 写入 |
|---|---|---|
| SYS-001 | v28 GOAL.md 必须避免与 out_of_scope.md 产生内在矛盾；如有冲突在 GOAL §1 显式标注边界（"本规则仅适用于 §2.3 表，不约束 §2.4.2 / §5.1 示例"） | knowledge/public/goal_loop/systemic_issues.md |
| SYS-002 | 父任务描述路径必须先 Read 验证再写入 subagent prompt；建议父会话加 Read → 实地确认步骤 | 同上 |

### v28+ 反模式识别（同类 ≥ 2 条）

| 反模式 | 累计 | 触发时间 | 相关 Skill |
|---|---|---|---|
| "目标契约内在矛盾"（v17.1 GL-007 + v27） | 2 次 | 2026-07-18 + 2026-07-20 | goal-loop |
| "C*/B* 决策标已完成但缺独立 verification" | 1 次（v27） | 2026-07-20 | goal-loop |

未达 SYS-001 类 ≥ 3 次阈值（v28+ 累计）。

---

## §4 本轮决策表（影响范围 + 替代方案）

### 决策 D-1（DT-V27-001 落档）：V-101 grep 冲突选方案 B
- **改动**：§2.3 顶部加索引引用块 + §2.3 表删除「阈值 SSOT」列；§4.3 顶部加 v27 B1 修订说明
- **影响范围**：仅 DESIGN_AND_EXECUTION_STANDARDS.mdc（v27 目标章节）
- **替代方案**：
  - 方案 A（撤销 §2.4.2 / §5.1 含数字）→ 触动非目标章节，违反 out_of_scope
  - 方案 C（撤销 T-101 改动宣告 FAIL）→ 反模式 GL-007

### 决策 D-2（T-102 落档）：README per-hook 模式 vs 全局段
- **改动**：README.md 新增 dna_decision_density_check.py 详解节（含阈值表 + env 覆盖）
- **影响范围**：仅 `.cursor/hooks/README.md`
- **替代方案**：
  - 方案 A（全局"阈值覆盖"段）→ 破坏 README per-hook 模式一致性

### 决策 D-3（T-103 守卫）：C2 决策保留不注册
- **改动**：仅写守卫审计记录（不碰 hooks.json）
- **影响范围**：仅新增 `v27_c2_guard.md`
- **替代方案**：
  - 方案 A（私自注册 session_resume_multi_goal.py）→ BLOCKER 双注入风险

### 决策 D-4（T-105）：原位补全 v27 段
- **改动**：检测到 CHANGELOG.md 已有 v27 段，原位补全（不重复追加 v27 标题）
- **影响范围**：仅 CHANGELOG.md v27 段
- **替代方案**：
  - 方案 A（追加第二个 v27 标题）→ 历史档重复

---

## §5 总结

v27 Round 1 完成 4 个高优动作 + 1 个 DT 决策 + 6 个治理档产物：
- B1 SSOT 合并 ✅
- C1/A2 README 详解 ✅
- C2 守卫 ✅
- C4 5 问对齐 ✅

全部 BLOCKER PASS + 全部 MAJOR PASS → converged_with_followup。

MINOR 遗留 1 项（§2.4.2 / §5.1 残留示例数字）→ v28+ 处理。

不 commit / 不动 git config / 不动 v17-v26 历史治理档 / 不动 test_cases.json / 不动 hooks.json / 不动 knowledge/public/。

---

## §6 触发的反模式 / 阻塞

- 反模式：0（§4 反模式防御全过）
- 阻塞：0（DT-V27-001 已闭环）

---

## §7 v28 启动条件

| 项 | 条件 |
|---|---|
| 1 | 读完 v27 audit_round1.md + review_round1.md + CONVERGED.md |
| 2 | F-1（§2.4.2 / §5.1 清理）+ F-2（v17 5 项约束）首批处理 |
| 3 | SYS-001/SYS-002 反模式防御建议采纳（如同意） |
| 4 | value_ratio ≥ 0.6（GL-001 强制线） |
| 5 | goal-loop v1.2 schema 18 字段保持 |
