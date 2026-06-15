# 更新日志

本文件记录 **AIDocxWorkFlow** 的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，
本项目针对**工作流流水线**（S1 → S1.5 → S2 → S2.5 → S3 → S4 → S5 → S6 → S7 → S8）
遵循 [语义化版本（Semantic Versioning）](https://semver.org/spec/v2.0.0.html) 规范。

`prompt` / `skill` / `rule` 的修订**不**提升主版本号；它们会随累积记录在
*Unreleased（未发布）* 章节中。

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
