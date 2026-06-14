# 更新日志

本文件记录 **AIDocxWorkFlow** 的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，
本项目针对**工作流流水线**（S1 → S1.5 → S2 → S2.5 → S3 → S4 → S5 → S6 → S7 → S8）
遵循 [语义化版本（Semantic Versioning）](https://semver.org/spec/v2.0.0.html) 规范。

`prompt` / `skill` / `rule` 的修订**不**提升主版本号；它们会随累积记录在
*Unreleased（未发布）* 章节中。

---

## [Unreleased]（未发布）

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
