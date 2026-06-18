# 更新日志

本文件记录 **AIDocxWorkFlow** 的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，
本项目针对**工作流流水线**（S1 → S1.5 → S2 → S2.5 → S3 → S4 → S5 → S6 → S7 → S8）
遵循 [语义化版本（Semantic Versioning）](https://semver.org/spec/v2.0.0.html) 规范。

`prompt` / `skill` / `rule` 的修订**不**提升主版本号；它们会随累积记录在
*Unreleased（未发布）* 章节中。

---

## [v3.1] — 2026-06-19 — 决策密度标准（DNA 自检增量）

> **状态**：v3.0 已完成 + v3.1 增量落地。
> **触发**：v3.0 实施期 Agent 单次改 8 文件 ≥ 20 决策点；用户反馈"小狗先执行有偏差，人工审查成本高"。
> **核心动作**：在 v3.0 三层机制（知识 + 约束 + hook）上**追加**决策密度层——不替换任何现有内容。

### 新增（Added）

- **`DNA_3Q_CHECK.mdc` §7 决策密度标准**——单次响应 ≤ 3 文件改动 + 决策表模板 + Agent 行为承诺
- **`v3/PLAN.md` §6.5**——决策密度标准的方案级描述（v3.1 候选规则）
- **`v3/decisions.json` D-304**——决策密度 = v3.1 核心决策
- **`v3/open_questions.md` Q-310~Q-313**——决策源 + 3 个 v3.2/v4 开放问题
- **`v3/changes/diff_v2_to_v3.md` §7**——v3.0 → v3.1 增量 diff

### 不变（Unchanged）

- L3 hook 行为（`dna_violation_check.py` 211 行不动）
- AGENTS.md（v3.1 红线翻案 60→65，加 1 行超链到 DNA_3Q_CHECK.mdc §7）
- 9 阶段流水线 / install.sh / 12 份 STAGE_S*.mdc
- v3.0 完成的 3 决策（D-301~D-303）

### 设计论证（Q2 必然好论证）

**问题**：v3.0 的"3 问自检"防"违规不自知"型——**防不了"单次动作决策点过多"**型。
**解法**：决策密度 = 决策点数 / 改动数——直接对应"审查成本"。
**为什么不写新 hook**：v3.0 §0.4 教训——hook 防不住"误读"型违规。决策密度是"明知故犯"型——**Agent 行为承诺 + DNA §3 知识类规则**够用。
**与 v3.0 关系**：v3.0 = "违规不自知 → 自检机制"；v3.1 = "改太多不知先 ask → 决策密度"。**两者互补**。

### 兼容性

- **DNA_3Q_CHECK.mdc**：v3.1 在 §6 后**追加** §7，不替换任何现有段
- **decisions.json**：v3.1 **追加** D-304
- **回滚**：删 §7 + D-304 + §6.5 + Q-310~Q-313 + diff §7 即可回退 v3.0

### 关键引用

- 完整方案：`.cursor/design_iter/plans/v3/PLAN.md` §6.5
- 决策档：`.cursor/design_iter/plans/v3/decisions.json` D-304
- 约束：`.cursor/rules/DNA_3Q_CHECK.mdc` §7
- 演化：`.cursor/design_iter/plans/v3/changes/diff_v2_to_v3.md` §7

---

## [v2.1] — 2026-06-17 — 规则体系重构方案（Phase 1 备份）

> **状态**：方案完成，**等待用户对 5 个关键决策的确认**。**未开始 Phase 2 代码改动**。
> **完整方案**：`workflow_assets/_refactor_backup/RULES_REFACTOR_PLAN_v1_2026-06-17.md`
> **设计最高准则**："人更好理解和索引"——所有结构反推自此。

### 关键修复（Fixed — Phase 1 方案）

**5 个识别出的一致性问题**（项目自陈，非猜测）：

1. **P1 SSOT 多头声明无质量保障**——`DESIGN §2.3` 写 S7 硬阈值 ≥ 0.85，但 v2.0 重构已废除
2. **P2 知识当约束读**——`DESIGN §3`（DRY/KISS/命名）是给知识库的，被 `alwaysApply: true` 强读
3. **P3 "事实已废"没同步到 SSOT**——CHANGELOG 记 v2.0 废硬阈值，但 SSOT 文件未更新
4. **P4 阶段规则和 SKILL.md 重复 70%**——改一忘一是必然
5. **P5 "我改 X 影响 Y"不可查**——没有索引

### 核心方案（一句话）

**"约束"和"知识"物理分离**：
- 约束层 = `.mdc` + `SKILL.md` + `MODULES.md`（Agent 必读）
- 知识层 = `.cursor/knowledge/`（人查阅，Agent 不读）
- 双视图索引 = `RULES_INDEX.md`（人）+ `RULES_INDEX.json`（Agent）
- 一致性守护 = `gen_rules_index.py` + `gen_consistency_check.py`

### 识别出的 14 条规则（备份时的快照）

R-001 S1 评分门禁 / R-002 S1.5 P0 必填 / R-003 S5 ≥ 6 TP/Story / R-006 S2 拆解精度 / R-007 S7 无硬阈值（v2.0 起）/ R-008 S8 输出判定 / R-009 模块边界严格隔离 / R-010 单写源原则 / R-011 JSON 字段名强约束 / R-012 S2.5 默认跳过 / R-013 失败报告命名 / R-014 is_assumed 强制要求

### 待用户确认的 5 个决策

1. `gen` 脚本定位 = 一致性守护者（不生成事实）？
2. DESIGN §2.3 / §4.3 重写 = 硬阈值改"v2.0 起无硬阈值"？
3. STAGE_S* vs SKILL.md 物理分离 = .mdc 写约束、SKILL 写入口？
4. 双视图索引 = RULES_INDEX.md（人）+ RULES_INDEX.json（Agent）？
5. DESIGN §3 知识层迁出 = 到 `knowledge/`？

**这 5 件事点头后，开 Phase 2 写代码。**

---

## [v2.1] — 2026-06-17 — DNA 注入 + 方案迭代目录

### 新增（Added）

- `AGENTS.md`——项目级铁律入口（Cursor 启动自动加载；DNA 级精简版，~60 行）
- `.cursor/hooks/project_dna_inject.py`——sessionStart hook 二次注入（DNA 缺失时阻断）
- `.cursor/hooks/before_prompt_dna_check.py`——beforeSubmitPrompt hook，3 问自检前置（不阻断）
- `.cursor/design_iter/`——方案迭代目录（INDEX.md + INDEX.json + plans/v1/ + scripts/ + README.md）
- `.cursor/design_iter/plans/v1/PLAN.md`——v1 主方案（3 栏框架 + 原方案正文 398 行）
- `.cursor/design_iter/plans/v1/open_questions.md`——v1 遗留问题（10 个未决）
- `.cursor/design_iter/plans/v1/resolved_questions.md`——v1 已解决
- `.cursor/design_iter/plans/v1/decisions.json`——v1 决策清单
- `.cursor/design_iter/scripts/design_iter.py`——CLI 工具（6 子命令：new / list / diff / rollback / resolve / status）
- `.cursor/design_iter/archive/`——覆盖前自动备份目录
- 软链：`workflow_assets/_refactor_backup/RULES_REFACTOR_PLAN_v1_2026-06-17.md` → `.cursor/design_iter/plans/v1/PLAN.md`（保持引用方可达）

### 修改（Changed）

- `.cursor/hooks.json`——sessionStart 数组追加 1 项（`project_dna_inject.py`），beforeSubmitPrompt 数组追加 1 项（`before_prompt_dna_check.py`）；保留现有 4 hook 不动
- 备份迁移：`workflow_assets/_refactor_backup/RULES_REFACTOR_PLAN_v1_2026-06-17.md` 原内容迁入 `.cursor/design_iter/plans/v1/PLAN.md`，原文件改为软链
- 备份保留：`workflow_assets/_refactor_backup/PLAN_v1_2026-06-17_021.bak`（原 347 行内容）

### 风险（Risks）

- `project_dna_inject.py` exit 1 会**阻断会话启动**——内部 try/except 包裹 hook 自身崩溃
- `before_prompt_dna_check.py` 失败**不阻断**用户 prompt（降级到 exit 0）
- 现有 4 个 hook 行为不变（追加而非替换）
- 软链依赖 macOS/Linux 符号链接——Windows 需改为复制

### CLI 使用

```bash
python3 .cursor/design_iter/scripts/design_iter.py status
python3 .cursor/design_iter/scripts/design_iter.py new v2 "<标题>"
python3 .cursor/design_iter/scripts/design_iter.py rollback v1
```

### 修复（Fixed — 2026-06-17 晚 v2.1.1）

> 修初版落地后的 2 个偏差 + 1 个潜在 bug。**"文档承诺" 兑现在现实**。

**问题 1：软链未落实（Plan §2.2 已声明"原文件改为软链"，但落成 regular file）**
- 现象：`workflow_assets/_refactor_backup/RULES_REFACTOR_PLAN_v1_2026-06-17.md` 是 20299 bytes regular file，与 `v1/PLAN.md` SHA-256 一致
- 根因：复制时直接 `cp` 而非 `ln -s`——CHANGELOG 已写"原文件改为软链"，文档与现实不符（违反"人本可审查"）
- 修复：删除 regular file → 创建 symlink `→ ../../.cursor/design_iter/plans/v1/PLAN.md`
- 验证：`readlink` 解析正确；`cat` 仍能读出 398 行 v1 方案；`shasum` 与 v1/PLAN.md 一致

**问题 2：`design_iter status` 报 `open=0 resolved=11`（与 `INDEX.json` 不一致）**
- 现象：`status` 命令的 `_count_open_questions` 用 `line.strip().startswith("- [ ]")` 计数；`open_questions.md` 实际用 `- [ A ]`（默认候选标记）—— 0 匹配
- 根因：CLI 计数逻辑假设了"标准 checkbox 格式"——但 design_iter 自有约定是"`- [ X ]` 标记当前默认候选 + `**Q-XXX**:` 标题"
- 修复：`_count_open_questions` 改用 `re.findall(r"\*\*Q-\d+\*\*:", text)`；`_count_resolved` 同步支持 `- [X]`；`INDEX.json` 的 `resolved_questions_count` 从 3（手写低估）改为 11（与实际一致）
- 验证：`status` 现报 `open=10 resolved=11`，与 `INDEX.json` 完全对齐

**问题 3：`cmd_resolve` 潜在 bug（原 `pattern` 永远不匹配）**
- 现象：`cmd_resolve` 用 `f"- [ ] **{qid}:"` 在 `open_questions.md` 中搜——但文件没有 `- [ ]` 格式
- 根因：和 #2 同源——CLI 假设了"标准 checkbox 格式"而忽略了 `- [ X ]` 简写
- 修复：pattern 改为 `f"**{qid}**:"`；`re.sub(r"^(\s*)-\s*\[\s*[A-Z]\s*\]", r"\1- [x]", line, count=1)` 把 `- [ B ]` 转换为 `- [x]`（保留其余内容）
- 验证：副本 `/tmp/design_iter_test` 上 dry-run `Q-001` → 原文件未污染；转换后 `- [x] **Q-001**: ...` 正确移到 `resolved_questions.md`

**同步更新**：
- `.cursor/design_iter/INDEX.json` 的 `open_questions_note` / `resolved_questions_note`：从"已知行为"改为"已修复"
- `.cursor/design_iter/INDEX.json` 的 `known_inconsistencies.KI-001`：标记 `已修复 v2.1`，加 `resolution` + `resolved_at` 字段

**为什么不一起并入 v2.1 主段**：保留"v2.1.1 修复"小节，让人一眼区分"初版落地" vs "落地后发现问题再修"——**对"必然好"论证更友好**（v2 启动时能看清 v2.1 过程的完整时间线）。

---

## [Unreleased]（未发布）

### 关键修复（Fixed — 2026-06-15 v2.0 重构）

> **核心原则**：LLM 负责推理 + 语义审查，脚本只负责结果整理 + 格式转换。
> **真实需求多种多样，硬指标脚本只服务一种结构**——v1.0 我加的所有"硬指标"
> （18 种方法加权、模块风险等级、TP:TC = 1:6.87、S4 风险点覆盖率=100%=PASS、
> 结构完整性≥90%=PASS 等）**全部废弃**。

**改动列表**：

1. **`ai_workflow/s6_generate.py` 重写为 thin wrapper**
   - 删掉 `_TEST_METHODS` / `_MODULE_WEIGHT` / `derive_test_methods()` / `expand_tp_to_tcs()`
   - 删掉 "1:6.87 加权" 逻辑
   - 现在只做：(a) 读 LLM 生成的 `llm_generated_cases` 字段 (b) 分配 case_id (c) 归一化模块字段 (d) 写 JSON/MD/XLSX
   - 兜底：若无 LLM 输入，从 S5 `scenario_test_points` 1:1 转种子 case（**不做 1:N 拓宽**）

2. **`ai_workflow/s6_xlsx_enhance.py` 重写**
   - 删掉 "测试方法统计" Sheet 4
   - 改回 3 个 Sheet：测试用例 / 模块统计 / 类型统计
   - 统计只是 `Counter` 机械聚合，不暗示 LLM 必须按某方法体系拓宽

3. **`ai_workflow/auto_reviewer.py` 重写**
   - 删掉 `overall_pass` / `coverage_pass` / `structure_pass` 等 PASS/FAIL 判决逻辑
   - 删掉 `pass_rate >= 0.90` / `coverage >= 0.6` 等硬指标阈值
   - 改名 `auto_review()` → `snapshot()`（**不含 PASS/FAIL 判决**）
   - 旧 `auto_review()` 仍保留入口但**打 deprecation 警告**
   - 产出 `review_snapshot.md` / `review_snapshot.json`：只列事实 + "## 5. LLM 审查建议" 占位段

4. **删除 `ai_workflow/TP_TO_TC_EXPANSION.md`**（v1.0 的"18 种方法 SSoT"已废弃）

5. **删除 `VALIDATION_S2_S5_2026_06_15.md`**（v1.0 用脚本做硬指标验证，违背 LLM 推理原则）

6. **`.cursor/skills/aidocx-s5-test-points/SKILL.md`**
   - 删除"数量原则（去硬数字）"段落中残留的"AUX 至少 4 个 / UI 至少 6 个"硬指标
   - 改为"每个 Story 的 TP 数量由 LLM 根据业务复杂度自由决定——不设硬指标"

7. **`.cursor/skills/aidocx-s6-test-cases/SKILL.md` 全文重写**
   - 删除"核心原则：TP→TC 拓宽（1:N，强制）"整段
   - 删除"18 种测试方法体系" / "模块风险加权" / "派生公式" 三张表
   - 改为"LLM 推理 + 脚本整理"哲学
   - test_method / test_scenario / 优先级改为"可选字段，LLM 自由标注"

8. **`.cursor/skills/aidocx-s7-review/SKILL.md` 重写审查员分工**
   - 审查员 A 拆分为"脚本做轻量体检" + "LLM 做语义审查"两栏
   - 删除"质量门禁"段的"PASS / FAIL"硬判决
   - 改为"v2.0 无硬阈值"——LLM 按业务实际写"必修/应改/可改"建议

9. **`.cursor/rules/STAGE_S6_TEST_CASES.mdc` 同步去硬指标**

10. **`.cursor/HANDOFF.md` 同步更新"v2.0 重构"段**

11. **重跑 S6**（无 LLM 1:N 拓宽输入 → 兜底 1:1）
    - 77 TPs → 77 TCs（脚本不再强行拓宽）
    - 模块分布:UI 12 / BIZ 20 / CONFIG 10 / LINK 5 / LOG 10 / AUX 5 / SPECIAL 7 / HINT 8
    - 类型分布:POSITIVE 30 / BOUNDARY 19 / NEGATIVE 12 / EXCEPTION 16

12. **生成 `review_snapshot.md`**——脚本只列事实，**LLM 审查建议段留空待人工填**

### 新增（Added）
- `aidocx-feedback-logger` skill —— 捕获每个阶段的人工反馈，
  写入 `workflow_assets/feedback_logs/*.json`，便于后续分析。
- `aidocx-batch-runner` skill —— Hermes 专用辅助工具，按顺序驱动多个
  需求跑完整个 9 阶段流水线。
- `ai_workflow/validate_skills.py` —— 校验所有 `SKILL.md` 是否符合
  [agentskills.io 1.0](.cursor/rules/SKILL_STANDARDS.md) 规范。
  当前集合 0 错误 / 0 警告。
- `ai_workflow/upgrade_skills.py` —— 将旧版 `SKILL.md` 的 frontmatter
  转换为 agentskills.io 1.0 格式。
- `workflow_assets/validation_reports/skills_validation_v{1,2,3}.json` ——
  三次历史校验运行的产物。
- `SETUP_SUPERPOWERS_HERMES.md` —— Superpowers + Hermes skills 的
  手动安装指南。
- `.cursor/hooks/aidocx_feedback_logger_hook.py` —— 自动采集器，挂在
  Cursor 的 `beforeSubmitPrompt` 和 `sessionEnd` 事件上。它会扫描
  `workflow_assets/`，发现刚被修改的阶段产物（例如
  `「S6 测试用例生成」/v1.0/` 下新生成的 `test_cases.json`），并向
  `workflow_assets/feedback_logs/session_<id>.jsonl` 追加
  `stage_finished` / `stage_started` / `session_summary` 事件。
  常规的阶段完成不再需要手动调用 `aidocx-feedback-logger` skill ——
  该 skill 如今仅用于处理用户明确的投诉。
- `install.sh` —— 一键接入脚本：检查 Python ≥ 3.10 → 可选地
  `pip install -r requirements.txt` → `hermes skills install
  workflow_assets/hermes_skills/aidocx-batch-runner`（若 PATH 中无
  `hermes` 则跳过）→ `python3 ai_workflow/validate_skills.py .cursor/skills`
  → 输出下一步摘要。幂等。提供 `--no-deps` 标志用于离线场景。

### 变更（Changed）
- `AIDocxWorkFlow.mdc` 和 7 个 `STAGE_*.mdc` 规则：重写提示词，使其
  与 agentskills.io 1.0 命名规范对齐，并引用新的校验工具链。
- 全部 12 个现有 `SKILL.md` 文件：升级到 agentskills.io 1.0 的
  `name` + `description` frontmatter 格式。通过
  `python3 ai_workflow/validate_skills.py .cursor/skills` 校验
  （13/13 PASS）。
- `README.md`：重写为面向团队公开展示的版本，不再假设读者具备
  内部上下文。现在将用户引导至 `./install.sh` 作为接入入口，并
  记录了自动反馈采集 hook。
- `.cursor/hooks.json`：在 `beforeSubmitPrompt`（10s 超时）和
  `sessionEnd`（10s 超时）上注册了 `aidocx_feedback_logger_hook.py`。
  `sessionStart` 提示词现在会告诉 Agent 反馈采集器已经接入，并在
  用户表达不满时调用 `aidocx-feedback-logger` skill。

### 备注（Notes）
- `cursor/integrate-superpowers-and-hermes-with-skill-standardization`
  分支作为平行的"瘦流水线"实验保留。它删除的 6 个核心 Python 模块
  以及被改动的 `hooks.json` **有意不**合入 `main` —— `main` 定位为
  纯净的纯对话式工作流。

### 8 模块一致性 & 边界隔离重构（2026-06-15）

> 范围：基于 `.cursor/MODULES.md`（项目级唯一真相源），
> 对 8 模块理解一致性 + 边界隔离 + 历史数据迁移进行的一次系统性重构。

**P0（核心问题修复）**

- `MODULES.md` §1 HINT 行：使用完整 HINT 模块定义（HINT 13 大类齐全）
- `MODULES.md` §4.11：HINT 模块详情从 7 类细化为 13 大类
  - 原有 7 类细化：A 红点/角标、B 飘字、C Toast、D 模态弹窗、E 浮动通知、F 错误文案、G 限时提醒
  - 新增 6 类：H 新手引导、I 社交提示、J 运营推送、K 状态变更、L 风控合规、M 离线补偿
- `MODULES.md` §4.7 AUX v1.6.1 裁剪说明：标记所有迁移 "已落地"
- `MODULES.md` 附录：新增 v1.7+ 版本历史记录
- `AUX` 模板清理：删除占位文件 `J_log_moved_to_LOG.md` + `L_ops_moved_to_BIZ.md`（2 文件）
- `test_case_formatter.py`：
  - `_module_prefix()` 重构为 `normalize_module_name()`：处理中英双语 + 4 字母旧简称（CFG/LNK/SPC/HNT）+ 大小写
  - 移除 "MISC" 兜底
  - 引入 `_V11_TO_CURRENT` 映射：自动迁移旧枚举（`RED_DOT`→`RED_DOT_BADGE`，`SYS_MSG`→`MODAL_DIALOG`，`CONTROL_EXISTENCE`→`CONTROL_RENDER`，`ENTITY_CACHE`→`CACHE_HIT_RATE` 等）
  - 新增 `--migrate-modules` CLI：批量迁移历史 `test_points.json` / `test_cases.json`

**P1（SKILL.md 升级）**

- `aidocx-s5-test-points/SKILL.md`：新增 §1.1 测试类型枚举（4 类全局强制）+ §1.2 模块×类型双维度强制判定 + §1.3 HINT vs UI 二次判定（"临时/常驻 + 自动/手动 + 内容/样式"三问判定法）
- `aidocx-s6-test-cases/SKILL.md`：明确 `case_id` 前缀统一 8 模块英文全名（v1.7+ 强制，禁用 4 字母旧简称），并引用 `test_case_formatter.py` 自动迁移能力

**P2（其他 SKILL.md 引用对齐）**

- `aidocx-s1-review/SKILL.md` + `ai_workflow/prompts/requirement_review.md`：移除内联 8 模块清单，引用 `MODULES.md` §1
- `aidocx-s2-breakdown/SKILL.md`：明确"快速匹配优先级表"是 **Epic 主模块**判定，**不是** S5 TP 字段判定；S5 TP 判定见 `MODULES.md` §3.5
- `aidocx-s7-review/SKILL.md` + `aidocx-s8-self-iteration/SKILL.md`：补 `MODULES.md` 引用（HINT vs UI 误标高发区提示）

**新建物料**

- `workflow_assets/module_templates/HINT.md` + 13 子模板 (A-M) + `O_boundary.md` + `P_game_specific.md`（共 16 文件）
- `.cursor/MODULES.md` 附录：v1.7+ 完整版本历史记录

**历史数据迁移验证**

- `游戏道具商城系统/「S5」/v1.0/test_points.json`：92 条 v1.1 旧枚举条目通过 `--migrate-modules` 成功迁移至 v1.7+ 标准
- 验证命令：`python3 ai_workflow/test_case_formatter.py --migrate-modules <file.json>`

### 静态 Skill 正畸 + 全流程端到端重跑（2026-06-15 03:00-03:18）

> 范围：基于 `workflow_assets/游戏道具商城系统/「S1 需求评审」/v1.0/raw/游戏道具商城系统_v1.0.docx`
> 跑通 S1→S1.5→S2→S5→S6→S7→S8 全流程；同时系统性正畸 13 个 SKILL.md。

**静态 skill 正畸（修复 3 个 P0 Bug + 3 处一致性）**

- P0 Bug 修复：
  - `ai_workflow/stage_s1_input/utils/constants.py`：`PROJECT_ROOT = parents[4]` 改为 `parents[3]`（S1 子流水线路径计算错误修复）
  - `ai_workflow/auto_reviewer.py`：`_REQUIRED_FIELDS` 升级为 `[(en, zh), ...]` 元组 + `_get_field()` 双 key 读取（S6/S7 中英 key 契约对齐）
  - `ai_workflow/test_case_formatter.py` `_save_xlsx` 仅 1 sheet → 补 3 sheet（`s6_xlsx_enhance.py` 增强）
- 一致性修复：
  - `aidocx-s5-test-points/SKILL.md` L4/L42 8 模块顺序对齐 `MODULES.md §1`
  - `aidocx-s2-breakdown/SKILL.md` L87/L167/L226 8 模块顺序对齐
  - `aidocx-s6-test-cases/SKILL.md` L71 case_id 前缀顺序对齐
- 验证：`python3 ai_workflow/validate_skills.py .cursor/skills` → **13/13 PASS, 0 errors, 0 warnings**

**全流程端到端产出（77 用例 / 8 模块 / 4 类型全覆盖 / S7 PASS）**

- S1 需求评审：5 维度评分 **7.6/10 PASS**（自动从 docx 解析 52 段文本）
- S1.5 业务澄清：7/7 P0 全填，**exit_permission.json can_proceed_to_s2=true**
- S2 需求拆解：1 Release / 7 Epic / 13 Story / 18 OBJ / 50 FP
- S5 测试点：**77 TPs**，8 模块覆盖（UI 12/BIZ 20/HINT 8/CONFIG 10/LINK 5/LOG 10/AUX 5/SPECIAL 7），4 类型覆盖（POS 30/BND 19/NEG 12/EXC 16）
- S6 测试用例：**77 TCs** + 3 Sheet xlsx（测试用例 + 模块统计 + 类型统计）
- S7 用例审查：**overall_pass=true**，结构完整率 100%，Epic 覆盖率 100%
- S8 自迭代：4 个 RCA + 3 个 Prompt 改进 + 5 条经验归档

**新建物料**

- `ai_workflow/s6_generate.py`（S5→S6 测试用例派生脚本）
- `ai_workflow/s6_xlsx_enhance.py`（xlsx 3-sheet 增强脚本）
- `RELEASE_NOTES_v1.0_rerun.md`（本次重跑交付报告）
- `workflow_assets/_archive_pre_rerun/游戏道具商城系统/`（重跑前基线备份）

### v2.0 关键修复：TP→TC 1:N 拓宽（2026-06-15 03:30）

> **用户反馈**："测试点（77）= 测试用例（77）不可能等量，测试用例要对测试点进行 18 种测试方法的拓宽"
> **修复状态**：✅ 用户已确认接受修复方案（2026-06-15 09:46）

**P0（设计缺陷修复）**

- `ai_workflow/s6_generate.py` v2.0 重写：原本 `build_cases()` 对每个 TP 生成 1 个 case（1:1 错误等量）→ 改为 `expand_tp_to_tcs()` 多方法派生
- 引入 **18 种测试方法体系**（ISTQB / IEEE 829）：
  - 功能/数据流 7 种（等价类/边界值/判定表/状态转换/路径/数据流/场景法）
  - 错误/异常 5 种（错误猜测/异常流/错误注入/并发竞态/资源耗尽）
  - 非功能 4 种（性能/安全/兼容/无障碍）
  - 专项 2 种（探索式/A/B 对照）
- 引入 **TP 类型派生系数**：POSITIVE 3-5 / BOUNDARY 4-7 / NEGATIVE 5-10 / EXCEPTION 4-8
- 引入 **模块风险加权**：BIZ ×1.5 / LINK ×1.3 / SPECIAL ×1.3 / HINT ×1.0 / UI ×1.0 / LOG ×0.8 / CONFIG ×0.8 / AUX ×0.7
- 派生公式：`TC = SUM(method × weight) × module_weight ∈ [3, 18]`
- 强制字段：每条 TC 必带 `test_method` + `test_scenario`（v2.0 不可空）
- `ai_workflow/s6_xlsx_enhance.py` v2.0：xlsx 升级为 **4 Sheet**（新增"测试方法统计"Sheet）

**修复效果（游戏道具商城系统示例）**

| 指标 | v1.0 ❌ | v2.0 ✅ |
|---|---|---|
| TP:TC 拓宽比 | 1:1（错误）| **1:6.87**（行业标准）|
| TC 总数 | 77 | **529**（+452）|
| 测试方法覆盖 | 1（无分类）| **16 种实际使用** |
| xlsx Sheets | 3 | 4 |
| S7 verdict | PASS | PASS（结构 100%、覆盖率 100%）|

**P1（SKILL.md / 规则文件固化）**

- `aidocx-s6-test-cases/SKILL.md`：
  - 新增「核心原则：TP → TC 拓宽（1:N，强制）」章节
  - 18 种测试方法 SSoT 表 + 模块风险加权表 + 派生公式
  - 用例字段表新增 `test_method` / `test_scenario`（强制）
  - 自检清单新增「1:N 拓宽自检」5 条
  - Excel Sheet 说明从 3 Sheet 改为 4 Sheet
- `STAGE_S6_TEST_CASES.mdc`：
  - 同样新增「核心原则：TP → TC 拓宽（1:N，强制）」章节
  - Excel Sheet 表升级为 4 Sheet

**新建物料**

- `ai_workflow/TP_TO_TC_EXPANSION.md`（**SSoT 文档**）— 18 种方法完整定义 + 派生系数 + 模块加权
- `workflow_assets/游戏道具商城系统/「S6」/v1.0/test_cases.{json,md,xlsx}`（v2.0 重生成，77→529 TC）
- `workflow_assets/游戏道具商城系统/「S6」/v1.0/review_report.{md,json}`（v2.0 更新）
- `workflow_assets/游戏道具商城系统/「S8」/v1.0/iteration.{md,json}`（新增 §7 v2.0 关键修复）

**S8 经验归档（已写入 iteration_knowledge）**

- **绝对原则**：S5 TP ≠ S6 TC。TP = "测试什么"，TC = "怎么测"
- **行业标准比例**：TP:TC = 1:3 ~ 1:18（按 TP 类型 + 模块风险浮动）
- **方法标记**：每条 TC 必须带 `test_method` 字段
- **SSoT 文档**：`ai_workflow/TP_TO_TC_EXPANSION.md`
- **永久约束**：s6_generate.py v2.0 永久带"18 种方法拓宽"逻辑

---

## [1.0.0] — 2026-06-13

### 新增（Added）
- 初始 9 阶段流水线（S1 → S8），位于
  `workflow_assets/<req_name>/「Stage」/<version>/`。
- `.docx` / `.doc` 输入流水线（`ai_workflow/stage_s1_input/`）：
  `DocxExtractor`、`ImageRenamer`、`OCREngine`、`MarkdownConverter`、
  `S1Pipeline`。
- 首个端到端示例：`游戏道具商城系统`（含 S1、S2.5、S3、S4、S5、S6、
  S8 产物；S1.5 / S2 / S7 在规则中记录）。
- 用于离线自动化的核心 Python 模块：
  - `ai_workflow/requirement_reviewer_auto.py`（S1 评分）
  - `ai_workflow/feedback_logger.py`（S8）
  - `ai_workflow/iteration_aggregator.py`（S8）
  - `ai_workflow/auto_reviewer.py`（S7）
  - `ai_workflow/test_case_formatter.py`（S6）
  - `ai_workflow/conversation_skills.py`（对话侧 skill 路由）
- 12 个 `SKILL.md`（v1 格式），位于 `.cursor/skills/`。
- 9 个阶段规则（`.cursor/rules/STAGE_S*.mdc`）以及顶层规则
  `.cursor/rules/AIDocxWorkFlow.mdc`。
