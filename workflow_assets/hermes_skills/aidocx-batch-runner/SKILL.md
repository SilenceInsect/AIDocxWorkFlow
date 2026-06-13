---
name: aidocx-batch-runner
description: >
  Hermes Agent 后台批量跑 AIDocxWorkFlow 9-stage 流水线的技能。
  扫描 requirements/ 目录下的 .docx/.md 原始需求文件，依次跑 S1→S8，把产出写到 workflow_assets/。
  适合夜间无值守批处理，一次跑 10+ 个需求，天亮出报告。
  Hermes cron 任务调用本 skill 后，agent 启动一个 Python 子进程执行
  python3 ai_workflow/orchestrator.py --batch --input requirements/ --output workflow_assets/。
  Use when the user says '批量跑 AIDocx' / '跑批' / 'batch run' / '夜间流水线', or Hermes cron triggers nightly_pipeline job.
  使用当用户说"批量跑 AIDocx"、"跑批"、"夜间流水线"或 Hermes cron 触发 nightly_pipeline 任务时。
license: MIT
compatibility: Hermes Agent (>=2026.6), Claude Code, Codex CLI, any agentskills.io compliant agent with terminal access
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: batch-runner
  spec_version: agentskills.io/1.0
  hermes_compat: true
  cursor_compat: false
allowed-tools: Bash(python3 *) Bash(ls *) Bash(mkdir *) Read Write
---

# AIDocxWorkFlow — Hermes 批量流水线运行器

> **Hermes 专用 skill**：在 Hermes Agent 会话中由 cron 或用户显式触发，运行 AIDocxWorkFlow 的批量版本（多个需求一次跑完）。
> **不在 Cursor 中注册**（metadata.cursor_compat: false），仅供 Hermes / Claude Code / Codex 后台使用。

---

## 触发场景

| 触发源 | 触发短语 / 配置 |
|---|---|
| Hermes cron 任务 | `nightly_pipeline`：每天 23:00 跑一遍 `requirements/` 目录 |
| 用户在 Hermes CLI 中 | "批量跑 AIDocx"、"跑批"、"batch run"、"夜间流水线" |
| Telegram / Slack 消息 | `/aidocx-batch` 命令 |

## 触发时执行的命令

```bash
# 1. 扫描输入目录
python3 ai_workflow/orchestrator.py \
  --batch \
  --input requirements/ \
  --output workflow_assets/ \
  --version-default v1.0 \
  --stages S1,S1.5,S2,S2.5,S3,S4,S5,S6,S7,S8 \
  --continue-on-fail \
  --report-format markdown,json \
  --report-destination workflow_assets/batch_reports/
```

## 输入 / 输出约定

### 输入
- `requirements/`：放置待处理的原始需求（`.docx` / `.md` / `.txt`）
- 每个需求一个子目录，目录名即 `<req_name>`（如 `游戏道具商城系统/`）
- 已被处理过的需求（存在 `workflow_assets/<req_name>/「S1 需求评审」/`）默认跳过，可用 `--force` 覆盖

### 输出
- `workflow_assets/<req_name>/「S* 阶段」/v1.0/...`：与手工执行 pipeline 一致
- `workflow_assets/batch_reports/<YYYY-MM-DD>_batch_report.md`：本批次的总报告（PASS/FAIL 列表）
- `workflow_assets/batch_reports/<YYYY-MM-DD>_batch_report.json`：机器可读版
- `feedback_logs/batch_<YYYY-MM-DD>.jsonl`：每条 run 的执行反馈，逐行追加

## 行为细节

### 失败策略
- 单个需求失败时，**继续跑下一个**（`--continue-on-fail` 默认开启）
- 失败的需求写入 `batch_report.md` 的"FAIL 列表"段，包含：
  - 失败的 stage
  - 失败原因摘要（来自 fail_report_S*.md）
  - fail_report_S*.md 的相对路径
- 全部跑完后，若有失败项，Hermes 自动通过 Telegram 推送告警（如果配置了 gateway）

### 资源控制
- 串行执行（不并发），避免对 LLM API 触发限流
- 每个需求超时：默认 30 分钟（可通过 `--per-req-timeout` 调整）
- 全批超时：默认 8 小时（足够跑 10-15 个中型需求）

### 与 S8 自迭代的衔接
- 批次跑完后，自动触发 `aidocx-s8-self-iteration` skill
- 收集所有需求的 S8 iteration.json，生成 `batch_iteration_summary.md`：
  - 跨需求共性缺陷模式
  - 跨需求共性 prompt 改进建议
  - 自动追加到 `feedback_archive/rules/<Module>/通用补充点.md`
- **这是"经验自动回流"的关键钩子**

## 报告模板

```markdown
# AIDocxWorkFlow 批量运行报告

**日期**: 2026-06-14
**批次大小**: 12 个需求
**总耗时**: 4h 23min
**执行模式**: 串行无值守

## 结果总览

| 需求 | 状态 | 失败 Stage | 备注 |
|---|---|---|---|
| 游戏道具商城系统 | ✅ PASS | — | v1.0 完整跑通 |
| 订单中台 | ⚠️ S5 FAIL | S5 | R-12 风险点未映射 |
| 营销活动管理 | ✅ PASS | — | — |
| ... | ... | ... | ... |

## 失败列表（4/12）

### 订单中台
- 失败 stage: S5
- 原因: S4 风险点 R-12 (Redis 击穿) 未映射到任何 test_point
- 修复建议: 在 S5 中补充针对 Redis 击穿场景的 EXCEPTION 测试点
- fail_report: workflow_assets/订单中台/「S5 测试点生成」/v1.0/fail_report_S5.md

## 跨需求共性

- 3/12 需求在 S5 缺少 Redis/缓存击穿测试点
- 建议: 升级 S5 prompt 模板（`ai_workflow/prompts/test_point_gen.md`），在风险分析步骤强制要求枚举缓存类风险

## S8 自迭代产出

- 已追加到 `feedback_archive/rules/业务/通用补充点.md`：1 条
- 已追加到 `feedback_archive/rules/方法论/覆盖率定义重构.md`：0 条
- 下次流水线将自动应用这 1 条补充
```

## Hermes cron 配置示例

```bash
# 在 Hermes 中添加定时任务
hermes cron add "0 23 * * *" \
  --command "/skill aidocx-batch-runner" \
  --platform telegram \
  --notify-on-fail
```

或在 `~/.hermes/config.yaml` 中：

```yaml
crons:
  - schedule: "0 23 * * *"
    command: "/skill aidocx-batch-runner"
    notify_on_fail: true
    notify_platform: telegram
```

## 关联文件

- 主调度器（待实现）：`ai_workflow/orchestrator.py`
- 现有 pipeline 代码：`ai_workflow/stage_s1_input/` 等
- 反馈日志：`workflow_assets/feedback_logs/`
- 知识库：`workflow_assets/feedback_archive/`
- 单次报告路径：`workflow_assets/<req_name>/「S* 阶段」/v1.0/`

## 状态

- [x] SKILL.md 骨架（本文件）
- [ ] `ai_workflow/orchestrator.py` 主体实现
- [ ] `feedback_archive/rules/方法论/批量跑批模式.md` 配套规则
- [ ] Hermes cron 注册脚本

## 参考

- Hermes Agent 文档：https://hermes-agent.nousresearch.com/
- agentskills.io 规范：https://agentskills.io/specification
- Superpowers 流程：https://github.com/obra/superpowers
