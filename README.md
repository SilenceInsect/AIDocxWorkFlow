# AIDocxWorkFlow

> AI 驱动的端到端需求 → 测试用例自动化工作流。
> 9 阶段模块化流水线，每阶段可独立调用、可重入、可在失败时输出失败报告并暂停。
> 跨 Cursor / Hermes / Claude Code / Codex CLI 兼容（[agentskills.io](https://agentskills.io) 1.0 标准）。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](#)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%2FWSL-lightgrey?logo=apple&logoColor=white)](#)
[![Skills Spec](https://img.shields.io/badge/Skills-agentskills.io%201.0-7c3aed)](#)
[![License](https://img.shields.io/badge/License-Internal--Use-orange)](#)

---

## 目录

- [项目定位](#项目定位)
- [核心特性](#核心特性)
- [快速开始](#快速开始)
- [9 阶段流水线](#9-阶段流水线)
- [目录结构](#目录结构)
- [质量门禁与失败报告](#质量门禁与失败报告)
- [AI 经验沉淀（自迭代）](#ai-经验沉淀自迭代)
- [团队协作约定](#团队协作约定)
- [常见问题](#常见问题)

---

## 项目定位

| 项 | 说明 |
|---|---|
| **目的** | 把"原始需求 → 测试用例"的链路交给 AI 串起来，让 QA 团队把精力放在**用例质量**而不是**用例搬运**上 |
| **适用场景** | 游戏 / 工具类产品的功能测试用例自动生成；任何有结构化需求文档的 QA 流程 |
| **输入** | `.docx` / `.md` / 粘贴的需求文本 |
| **产出** | `backlog.md`（Epic/Story）+ `test_points.json`（测试点）+ `test_cases.md` / `.json` / `.xlsx`（测试用例）+ `review_report.md`（审查报告） |
| **运行依赖** | Python 3.10+，Cursor IDE / Hermes Agent / Claude Code / Codex CLI 任一 |
| **网络要求** | S1–S7 的 AI 阶段需要网络；S8 反馈聚合、报告生成、Excel 导出均离线 |

---

## 核心特性

- 🧩 **模块化**：9 个阶段可独立触发，任意阶段可"丢材料 → 审查 → 产出"
- 🔁 **可重入**：每个阶段都有 `fail_report_S*.md` 失败报告，**不会**在原料不合格时硬产出
- 🧠 **可自迭代**：S8 把每轮反馈写进 `feedback_archive/`，下一轮 AI 产出自动吸收
- 🌐 **跨平台**：所有 SKILL.md 符合 [agentskills.io](https://agentskills.io) 1.0 规范，Cursor / Hermes / Claude Code 都能加载
- 📦 **零破坏**：所有中间产物按 `<需求名>/「阶段名」/v<版本>/` 落盘，团队可随时回溯

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/SilenceInsect/AIDocxWorkFlow.git
cd AIDocxWorkFlow
```

### 2. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> macOS 用户首次运行 OCR 还需要 `brew install tesseract`（仅当 S1 解析扫描件 PDF/图片时使用）。

### 3. 打开 IDE

| IDE | 说明 |
|---|---|
| **Cursor**（推荐） | 直接打开本目录；13 个 SKILL.md 自动加载，钩子自动注册 |
| **Hermes Agent** | `hermes skills install ./aidocx-s1-review` 等 |
| **Claude Code** | 把 `.cursor/skills/` 软链到 `~/.claude/skills/` |
| **Codex CLI** | 软链 `.cursor/skills/` 到 `~/.codex/skills/` |

### 4. 跑通一个示例需求

仓库自带 `workflow_assets/游戏道具商城系统/`，它**已经跑完 S1 → S6 → S7 → S8**，可直接对照学习：

```bash
# 看一下产出物
ls workflow_assets/游戏道具商城系统/「S6 测试用例生成」/v1.0/
#  -> test_cases.md / test_cases.json / test_cases.xlsx / review_report.md
```

### 5. 触发一条新需求

打开 IDE，对话框里描述需求（或粘贴 `.docx` 路径），AI 会按 9 阶段引导推进。也可以在输入框打 `/` 查看所有可用命令（如 `/aidocx-s1-review`、`/aidocx-s5-test-points` 等）。

---

## 9 阶段流水线

```
原始需求
  │
  ▼
S1 需求评审        ──→  review_report.md + clarification_checklist.md + 终版需求.md（草稿）
  │
  ▼ 人工填写 clarification_checklist
S1.5 业务澄清     ──→  终版需求.md（终版） + exit_permission.json
  │
  ▼ 读取 exit_permission
S2 需求拆解        ──→  backlog.md / backlog.json / requirement_objects.md / requirement_objects.json
  │
  ▼
S2.5 迭代规划     ──→  project_config.json + iteration_plan.md / iteration_plan.json
  │
  ▼
S3 原型导出        ──→  prototype.md（含 Mermaid 页面流图）
  │
  ▼
S4 流程图导出     ──→  business_flow.md（业务流图 + 时序图 + 异常决策树）
  │
  ▼
S5 测试点生成     ──→  test_points.json（18 种测试设计方法 + S4 风险点全量映射）
  │
  ▼
S6 测试用例生成  ──→  test_cases.md / .json / .xlsx（3 Sheet：测试用例 / 评审 / 覆盖率）
  │
  ▼
S7 用例审查        ──→  review_report.md / .json（双审查员 + S4 风险点 100% 覆盖判定）
  │
  ▼
S8 自迭代          ──→  iteration.md / iteration.json（反馈归因 → Prompt 改进 → 经验归档）
```

| Stage | 触发命令 | 失败报告 |
|---|---|---|
| **S1** 需求评审 | `/aidocx-s1-review` | `fail_report_S1.md` |
| **S1.5** 业务澄清 | 人工清单 → 自动准出 | `fail_report_S1_5.md` |
| **S2** 需求拆解 | `/aidocx-s2-breakdown` | `fail_report_S2.md` |
| **S2.5** 迭代规划 | `/aidocx-s2-5-iteration` | `fail_report_S2_5.md` |
| **S3** 原型导出 | `/aidocx-s3-prototype` | `fail_report_S3.md` |
| **S4** 流程图导出 | `/aidocx-s4-flowchart` | `fail_report_S4.md` |
| **S5** 测试点生成 | `/aidocx-s5-test-points` | `fail_report_S5.md` |
| **S6** 测试用例生成 | `/aidocx-s6-test-cases` | `fail_report_S6.md` |
| **S7** 用例审查 | `/aidocx-s7-review` | `fail_report_S7.md` |
| **S8** 自迭代 | `/aidocx-s8-self-iteration` | `fail_report_S8.md` |

> **每阶段都是独立的**——你可以直接喂 S5 的 `test_points.json` 跳到 S6，也可以从 S1 重新跑。失败报告不会污染产出目录。

---

## 目录结构

```
AIDocxWorkFlow/
├── README.md                        # 本文件
├── requirements.txt                 # Python 依赖
├── sample_requirements.md           # 示例需求
├── quickstart.sh                    # 一键环境引导
├── convert_md_to_docx.py            # Markdown ↔ .docx 转换
├── AIDocxWorkFlow.code-workspace    # Cursor 工作区配置
│
├── .cursor/                         # Cursor 规则、skills、hooks
│   ├── rules/                       # 阶段规则文件 (STAGE_S*.mdc)
│   ├── skills/                      # 13 个 AI 技能 (SKILL.md)
│   └── hooks/                       # 钩子（SKILL 验证、计费等）
│
├── ai_workflow/                     # Python 自动化模块（离线可跑）
│   ├── requirement_reviewer_auto.py # S1 自动评分
│   ├── feedback_logger.py           # 反馈日志读写
│   ├── auto_reviewer.py             # S7 自动审查
│   ├── iteration_aggregator.py      # S8 反馈聚合
│   ├── conversation_skills.py       # 对话式 skill 触发
│   ├── test_case_formatter.py       # 用例格式化 + ID 分配
│   └── ...
│
└── workflow_assets/                 # 全部中间产物 + 知识库
    ├── 游戏道具商城系统/            # 示例需求（已跑完 S1–S8）
    │   ├── 「S1 需求评审」/v1.0/
    │   ├── 「S2 需求拆解」/v1.0/
    │   ├── 「S2.5 迭代规划」/v1.0/
    │   ├── 「S3 原型导出」/v1.0/
    │   ├── 「S4 流程图导出」/v1.0/
    │   ├── 「S5 测试点生成」/v1.0/
    │   ├── 「S6 测试用例生成」/v1.0/
    │   └── 「S8 自迭代」/v1.0/
    ├── feedback_logs/               # 每轮反馈日志
    ├── feedback_archive/            # AI 经验知识库（按"业务/方法论/界面/配置"分类）
    └── billing_logs/                # 计费日志（如果开了 token 计费）
```

---

## 质量门禁与失败报告

每阶段都有**结构门禁 + 质量门禁 + 完整性门禁 + 边界门禁**四层校验。**原料不合格时不会硬产出**，而是生成 `fail_report_S*.md` 并暂停：

| Stage | 通过条件 |
|---|---|
| S1 | 评分仅作参考；P0 问题已澄清即放行 |
| S1.5 | P0 项 100% 填写 → `can_proceed_to_s2 = true` |
| S2 | Epic/Story/需求对象/功能点字段齐全，无循环依赖 |
| S2.5 | 关键里程碑（开发完成、转测、回归、上线）均有明确日期 |
| S3 | 每个 UI 类 Story 有对应页面原型 |
| S4 | 所有识别出的异常路径均已覆盖 |
| S5 | 18 种测试设计方法 + S4 风险点全量映射（非固定数量） |
| S6 | 100% 必填字段（前置条件、操作步骤、预期结果） |
| S7 | S4 风险点覆盖率 = 100% 且异常树覆盖率 = 100% |
| S8 | 每个根因有可执行改进建议 |

---

## AI 经验沉淀（自迭代）

S8 不是"产出物阶段"，而是**学习阶段**：

1. **收集反馈** — `workflow_assets/feedback_logs/*.json` 记录每轮 S7 审查发现的问题
2. **归因分析** — `iteration_aggregator.py` 把同类问题聚合，找根因
3. **Prompt 改进** — 自动给各阶段 SKILL.md 提改进建议
4. **经验归档** — 把可复用的教训写进 `workflow_assets/feedback_archive/`，分四类：
   - `业务/` — 某类业务的常见漏测点
   - `方法论/` — 测试方法论层面的改进
   - `界面/` — UI 测试补充点
   - `配置/` — 配置类需求补充点

下一轮 S1–S7 执行时，AI 会**自动**读取 `feedback_archive/`，避免重复犯同样错误。

---

## 团队协作约定

### 分支策略

| 分支 | 用途 |
|---|---|
| `main` | 稳定版，每个阶段都"跑通过"才能合 |
| `cursor/<特性>` | 通过 Cursor AI 协作开发的特性分支（例：`cursor/integrate-superpowers-and-hermes-with-skill-standardization`） |
| `hermes/<特性>` | Hermes Agent 协作分支（未来） |
| `feat/<特性>` | 人类手动 PR 分支 |

### Commit 风格

```
<type>(<scope>): <subject>

<body explaining "why">

<footer with refs>
```

常用 `type`：`feat` / `fix` / `chore` / `docs` / `refactor` / `test` / `iter`。

### 提 PR 之前

1. `git status` 干净（`.DS_Store` / `__pycache__/` / `.pyc` 已被 `.gitignore` 挡掉）
2. 示例需求 `workflow_assets/游戏道具商城系统/` 至少重跑 S5–S7 通过
3. 新增 / 改动的 SKILL.md 跑过 `ai_workflow/validate_skills.py`（hooks 会自动跑）
4. PR 描述里附上 `fail_report_S*.md`（如有）和 `review_report.md` 关键结论

---

## 常见问题

<details>
<summary><b>Q: 跑某个阶段时原料不合格，会污染产出吗？</b></summary>

不会。失败报告会落到对应阶段的 `fail_report_S*.md`，并明确指出缺什么、补全后重跑即可。

</details>

<details>
<summary><b>Q: 我可以只跑 S5/S6 吗？</b></summary>

可以。每阶段独立可触发——只要 `test_points.json` 准备好（或更上游任一阶段的产物准备好），就能直接跑对应阶段。
</details>

<details>
<summary><b>Q: SKILL.md 改坏了怎么办？</b></summary>

`ai_workflow/validate_skills.py` 会按 agentskills.io 1.0 规范校验；`.cursor/hooks/skill_validation_hook.py` 会在每次写入时自动跑一次。CI 里也可以加一行 `python3 ai_workflow/validate_skills.py` 作为门禁。
</details>

<details>
<summary><b>Q: 示例需求 <code>游戏道具商城系统</code> 跑过 S8 吗？</b></summary>

跑过。`workflow_assets/游戏道具商城系统/「S8 自迭代」/v1.0/iteration.md` 有完整记录，可作为新需求 S8 产出格式的参考。
</details>

---

## 维护

| | |
|---|---|
| **Owner** | QA 平台组 |
| **AI 工具链** | Cursor + Claude Opus 4 + Hermes Agent（可选） |
| **更新机制** | S8 自迭代 + 人工评审 |
| **License** | 内部使用，暂不开源 |

> 任何阶段出问题，第一时间看 `fail_report_S*.md`——这是流水线里"自检不出错"的关键设计。
