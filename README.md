# AIDocxWorkFlow

> AI 驱动的端到端"需求 → 测试用例"自动化工作流。
> 10 阶段模块化流水线（S1 ~ S8 + S1.5），每阶段可独立调用、可重入，原料不合格时输出失败报告并暂停。
> 兼容 Cursor / Claude Code / Codex CLI（[agentskills.io](https://agentskills.io) 1.0 标准）。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](#)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%2FWSL-lightgrey?logo=apple&logoColor=white)](#)
[![Skills Spec](https://img.shields.io/badge/Skills-agentskills.io%201.0-7c3aed)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 目录

- [项目定位](#项目定位)
- [核心特性](#核心特性)
- [快速开始](#快速开始)
- [10 阶段流水线](#10-阶段流水线)
- [8 模块系统](#8-模块系统)
- [目录结构](#目录结构)
- [质量门禁与失败报告](#质量门禁与失败报告)
- [AI 经验沉淀（自迭代）](#ai-经验沉淀自迭代)
- [设计演进管理](#设计演进管理)
- [团队协作约定](#团队协作约定)
- [常见问题](#常见问题)
- [维护](#维护)

---

## 项目定位

| 项 | 说明 |
|---|---|
| **目的** | 把"原始需求 → 测试用例"的链路交给 AI 串起来，让 QA 团队把精力放在**用例质量**而不是**用例搬运**上 |
| **适用场景** | 游戏 / 工具类产品的功能测试用例自动生成；任何有结构化需求文档的 QA 流程 |
| **输入** | `.docx` / `.md` / 粘贴的需求文本 |
| **产出** | `backlog.md`（Epic/Story）+ `test_points.json`（测试点）+ `test_cases.json`（公共默认测试用例）+ `review_report.md`（审查报告）；项目级场景可额外导出 `test_cases.md/.xlsx` |
| **运行依赖** | Python 3.10+，Cursor IDE / Claude Code / Codex CLI 任一 |
| **网络要求** | S1–S7 的 AI 阶段需要网络；S8 反馈聚合、报告生成、Excel 导出均离线 |

---

## 核心特性

- **模块化**：10 个阶段可独立触发，任意阶段可"丢材料 → 审查 → 产出"
- **可重入**：每个阶段都有 `fail_report_S*.md` 失败报告，**不会**在原料不合格时硬产出
- **可自迭代**：S8 把每轮反馈整理成知识候选写入 `knowledge/project_local/.review_queue/`，人工审核后再决定是否回写公共知识库
- **8 模块体系**：覆盖游戏/工具类产品的全部测试场景（CONFIG / UI / BIZ / UTIL / LINK / SPECIAL / LOG / HINT）
- **跨平台**：所有 `SKILL.md` 符合 [agentskills.io](https://agentskills.io) 1.0 规范，Cursor / Claude Code 都能加载
- **零破坏**：所有中间产物按 `<需求名>/「阶段名」/v<版本>/` 落盘，团队可随时回溯

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/SilenceInsect/AIDocxWorkFlow.git
cd AIDocxWorkFlow
```

### 2. 运行 install.sh（推荐 · 一键接入）

```bash
./install.sh            # 标准安装
./install.sh --no-deps  # 离线机器（跳过 pip）
```

`install.sh` 会自动：
- 校验 Python ≥ 3.10
- 跑 `validate_skills.py` 确认 13/13 SKILL 合规
- 打印下一步清单

### 2b. 手动安装依赖（如果跳过 install.sh）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> macOS 用户首次运行 OCR 还需要 `brew install tesseract`（仅当 S1 解析扫描件 PDF/图片时使用）。

### 3. 打开 IDE

| IDE | 说明 |
|---|---|
| **Cursor**（推荐） | 直接打开本目录；13 个 SKILL.md 自动加载，hooks 自动注册 |
| **Claude Code** | 把 `.cursor/skills/` 软链到 `~/.claude/skills/` |
| **Codex CLI** | 软链 `.cursor/skills/` 到 `~/.codex/skills/` |

### 4. 触发一条新需求

打开 IDE，在对话框中描述需求（或粘贴 `.docx` 路径），AI 会按 10 阶段引导推进。也可以在输入框打 `/` 查看所有可用命令（如 `/aidocx-s1-review`、`/aidocx-s5-test-points` 等）。

---

## 10 阶段流水线

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
S2.5 迭代规划     ──→  iteration_plan.md / iteration_plan.json（默认跳过，见编排开关）
  │
  ▼
S3 原型导出        ──→  prototype.md（含 Mermaid 页面流图）
  │
  ▼
S4 流程图导出     ──→  business_flow.md（业务流图 + 时序图 + 异常决策树）
  │
  ▼
S5 测试点生成     ──→  test_points.json（8 模块 × 场景全覆盖）
  │
  ▼
S6 测试用例生成  ──→  test_cases.json（公共默认） + test_cases.md / .xlsx（仅项目级导出）
  │
  ▼
S7 用例审查        ──→  review_report.md / .json（双审查员 + 覆盖率判定）
  │
  ▼
S8 自迭代          ──→  iteration.md / iteration.json（反馈归因 → Prompt 改进 → 经验归档）
```

| 阶段 | 触发命令 | 失败报告 |
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

> **S2.5 默认跳过**：S2.5 迭代规划对测试点/用例产出无强关系，全流程默认不执行。需要在全流程中包含 S2.5 时，显式设置 `AIDOCX_INCLUDE_S2_5=true`。

---

## 8 模块系统

每个测试点必须归属以下 8 个模块之一（Epic ID 前缀）：

| 模块 | ID 前缀 | 职责边界 |
|---|---|---|
| **CONFIG** 配置 | `CONFIG-` | 配置表字段合法性、同表/跨表一致性、热更新、版本兼容、数值逻辑、导出发布、服务端配置 |
| **UI** 界面 | `UI-` | 控件渲染与多状态、纯前端交互、布局适配、静态展示、动效动画、引导浮窗、无障碍 |
| **BIZ** 业务 | `BIZ-` | 核心业务流程、端服数据流、协议交互、状态机、DB 持久化、并发事务、付费/定时任务 |
| **UTIL** 辅助 | `UTIL-` | 底层工具框架、网络层、缓存层、资源管理、离线更新、GM 工具、性能监控、加密安全 |
| **LINK** 关联 | `LINK-` | 内部业务联动、跨服数据同步、多端一致性、第三方接口、跨模块资源、对外数据透出 |
| **SPECIAL** 特殊 | `SPECIAL-` | 边界极端场景、反作弊、数据安全、弱网容错、前后台切换、宕机高危、版本兼容、渠道灰度、合规风控、资源耗尽 |
| **LOG** 日志 | `LOG-` | 玩家行为埋点、资产审计流水、全量操作日志、监控埋点、崩溃日志、分级存储、Trace 溯源、合规字段 |
| **HINT** 提示 | — | 红点/飘字/Toast/弹窗/浮窗/引导气泡/合规预警/离线补偿（临时弹出；常驻归 UI）|

完整定义见 [`.cursor/MODULES.md`](.cursor/MODULES.md)。

---

## 目录结构

```
AIDocxWorkFlow/
├── README.md
├── requirements.txt
├── sample_requirements.md
├── install.sh
├── quickstart.sh
├── AIDocxWorkFlow.code-workspace
│
├── governance/                     # 项目治理资产（人可读 / 跨工具共享）
│   └── design_iter/                # 设计方案迭代管理
│       ├── INDEX.md / INDEX.json   # 方案索引
│       ├── plans/v1/v2/v3/        # 各版本方案 + 决策 + 遗留问题
│       └── scripts/design_iter.py  # 方案管理 CLI
│
├── .cursor/                        # Cursor 接入层（规则 / skills / hooks）
│   ├── MODULES.md                  # 8 模块系统 SSOT
│   ├── hooks/                      # Cursor 钩子
│   │   ├── codegraph_sync.py               # CodeGraph 索引同步
│   │   ├── sync_modules_table.py           # MODULES.md 副本同步
│   │   ├── scan_module_definitions.py      # 8 模块定义体检
│   │   └── docx_hook.py                    # DOCX 自动收集
│   ├── rules/                       # 阶段规则（STAGE_S*.mdc）
│   │   ├── AIDocxWorkFlow.mdc
│   │   ├── DESIGN_AND_EXECUTION_STANDARDS.mdc
│   │   ├── SKILL_STANDARDS.md
│   │   └── STAGE_S*.mdc            # 10 阶段规则
│   └── skills/                      # 13 个 AI Skill（SKILL.md）
│       ├── aidocx-workflow-conversation/    # 全局对话编排
│       ├── aidocx-feedback-logger/          # 阶段反馈收集
│       ├── aidocx-s1-review/
│       ├── aidocx-s1-5-clarification/
│       ├── aidocx-s2-breakdown/
│       ├── aidocx-s2-5-iteration/
│       ├── aidocx-s3-prototype/
│       ├── aidocx-s4-flowchart/
│       ├── aidocx-s5-test-points/
│       ├── aidocx-s6-test-cases/
│       ├── aidocx-s7-review/
│       └── aidocx-s8-self-iteration/
│
├── ai_workflow/                     # Python 自动化模块（离线可跑）
│   ├── __init__.py
│   ├── requirement_reviewer_auto.py # S1 自动评分
│   ├── feedback_logger.py           # 反馈日志读写
│   ├── auto_reviewer.py             # S7 自动审查（snapshot）
│   ├── iteration_aggregator.py       # S8 反馈聚合
│   ├── conversation_skills.py      # 对话式 skill 触发
│   ├── test_case_formatter.py       # 用例格式化 + ID 分配 + 模块迁移
│   ├── consistency_check.py         # SKILL/规则一致性检查
│   ├── s4_validator.py              # S4 流程图验证
│   ├── s6_generate.py               # S5→S6 测试用例派生
│   ├── s6_xlsx_enhance.py          # S6 xlsx 3 Sheet 增强
│   ├── self_iteration.py            # S8 根因分析 + 经验归档
│   ├── upgrade_skills.py            # SKILL.md 格式升级
│   ├── validate_skills.py          # agentskills.io 1.0 校验
│   ├── prompts/                     # 各阶段 prompt 模板
│   │   ├── requirement_review.md
│   │   ├── test_point_gen.md
│   │   └── flowchart_export.md
│   └── stage_s1_input/              # S1 DOCX→Markdown OCR 子模块
│       ├── pipeline.py
│       ├── docx_extractor.py
│       ├── image_renamer.py
│       ├── ocr_engine.py
│       └── md_converter.py
│
├── workflow_assets/                 # 工作流资产根目录（过程资产默认不纳入版本控制）
│   ├── feedback_logs/               # 每轮会话反馈日志（不纳入版本控制）
│   ├── module_templates/             # 8 模块测试点模板（公共知识库，纳入版本控制）
│   │   ├── UI/                      # UI 模块 10 子类模板
│   │   ├── BIZ/                     # BIZ 模块 11 子类模板
│   │   ├── CONFIG/                  # CONFIG 模块 11 子类模板
│   │   ├── UTIL/                     # UTIL 模块 16 子类模板
│   │   ├── LINK/                    # LINK 模块 8 子类模板
│   │   ├── SPECIAL/                 # SPECIAL 模块 11 子类模板
│   │   ├── LOG/                     # LOG 模块 15 子类模板
│   │   ├── HINT/                    # HINT 模块 16 子类模板
│   │   └── _common_structure.md     # 通用 5 段模板结构
│   ├── test_point_library/          # 公共测试点知识库（纳入版本控制）
│   ├── test_case_library/           # 公共测试用例知识库（纳入版本控制）
│   ├── example_test_cases/          # 公共示例用例知识库（纳入版本控制）
│   └── <需求名>/                    # 每个需求独立工作目录（不纳入版本控制）
│
├── knowledge/
│   ├── public/                      # 公共知识库（纳入版本控制）
│   │   ├── module_templates/
│   │   ├── test_point_library/
│   │   ├── test_case_library/
│   │   └── example_test_cases/
│   └── project_local/               # 项目级知识库（默认不纳入版本控制）
│       └── .review_queue/           # Agent 产出的待人工审核知识候选
│       ├── v<ver>/「S1 需求评审」/
│       ├── v<ver>/「S2 需求拆解」/
│       └── ...（按阶段产出）
│
└── .githooks/                       # Git 钩子（可复用）
    ├── post-checkout
    ├── post-merge
    └── post-rewrite
```

---

## 版本控制边界

- `resource/`：原始需求、变更说明、私人输入材料，不纳入版本控制
- `workflow_assets/<req_name>/...`：单次需求的各阶段产物，不纳入版本控制
- `workflow_assets/feedback_logs/`：运行反馈日志，不纳入版本控制
- `knowledge/public/module_templates/`、`knowledge/public/test_point_library/`、`knowledge/public/test_case_library/`、`knowledge/public/example_test_cases/`：公共知识库，纳入版本控制
- `knowledge/project_local/`：项目级知识库，默认不纳入版本控制，允许与公共知识库格式不同
- 知识库分层、格式差异、入库审核流的唯一说明见 `knowledge/README.md`
- 规则库与治理库（`.cursor/rules/`、`.cursor/skills/`、`governance/`）属于项目知识，不因“过程性”被忽略

---

## 质量门禁与失败报告

每阶段都有**结构门禁 + 质量门禁 + 完整性门禁 + 边界门禁**四层校验。**原料不合格时不会硬产出**，而是生成 `fail_report_S*.md` 并暂停。

> **强制阅读指令（MANDATORY）**：本节是**简介**，**非规则定义**。
> - **规则定义唯一真相源（SSOT）**：`.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.3 质量门禁 + §4.3 配置常量
> - **详细判定逻辑**见各 `STAGE_S*.mdc` 的"质量门禁"节。
> - **本节表格不可独立编辑**，任何阈值变更**必须**先修改 SSOT，再回写本表同步。

---

## AI 经验沉淀（自迭代）

`aidocx-feedback-logger` 由 Cursor 钩子驱动——无需手动调用：

| 钩子事件 | 写入事件 | 触发条件 |
|---|---|---|
| `beforeSubmitPrompt` | `stage_finished` | 检测到上一轮产生了 S 阶段产物（`review_report.md` / `test_cases.json` / `fail_report_S*.md` 等）|
| `beforeSubmitPrompt` | `stage_started` | 用户输入包含阶段关键词（如 `S7`、`/aidocx-s6-test-cases`、`再跑一次 S6`）|
| `sessionEnd` | `session_summary` | 会话结束，汇总本次 started/finished/failed 计数 |

事件落到 `workflow_assets/feedback_logs/session_<id>.jsonl`，S8 自迭代可直接消费。手动调用 skill 仍可——用户对 AI 表达不满时，Agent 会主动追加一条结构化反馈。

S8 不是"产出物阶段"，而是**学习阶段**：

1. **收集反馈** — `feedback_logs/*.json` 记录每轮 S7 审查发现的问题
2. **归因分析** — `iteration_aggregator.py` 把同类问题聚合，找根因
3. **Prompt 改进** — 自动给各阶段 SKILL.md 提改进建议
4. **经验归档** — 根因先写入待审核候选区：
   - `S5_MODULE` / `S5_EXEC` / `S6_EXEC` → 写入 `knowledge/project_local/.review_queue/`
   - Prompt 规则不明确 → 写入 `.cursor/rules/prompt_fixes/<Stage>_<日期>.md`
   - `module_templates/` 这类核心公共知识库必须人工审核后才能回写

下一轮 S1–S7 执行时，AI 会**自动读取** `knowledge/public/` 下的公共知识库；项目级候选和私有知识默认不直接注入公共运行时。

---

## 设计演进管理

> ⚠️ **`governance/` 是本地工作区（不入 Git）**——见 `.gitignore` 第 69 行。
> 方案草稿、归档、INDEX.json 都是个人 / 临时工作区，**新克隆的仓库看不到这个目录**。
> 协作约定：**已收敛的方案结论必须提炼到 `.cursor/rules/*.mdc` 或 `MODULES.md`**，随代码提交。

`governance/design_iter/` 仅供本机归档与回溯，使用规范：

- 每份方案 v{N} 必有 **"解决 / 新增 / 遗留" 3 栏**
- 遗留问题直接喂入 v{N+1}——`open_questions.md` 不可缺
- 整份回滚：`python3 governance/design_iter/scripts/design_iter.py rollback v{N-1}`

| 工具 | 用途 |
|---|---|
| `design_iter.py new` | 创建新版本方案 |
| `design_iter.py list` | 列出所有方案 |
| `design_iter.py diff` | 对比两版本差异 |
| `design_iter.py rollback` | 回滚到指定版本 |
| `design_iter.py resolve` | 关闭某个遗留问题 |

---

## 团队协作约定

### 分支策略

| 分支 | 用途 |
|---|---|
| `main` | 稳定版，每个阶段都"跑通过"才能合 |
| `cursor/<特性>` | 通过 Cursor AI 协作开发的特性分支 |
| `feat/<特性>` | 人类手动 PR 分支 |

### Commit 风格

```
<type>(<scope>): <subject>

<body explaining "why">

<footer with refs>
```

常用 `type`：`feat` / `fix` / `chore` / `docs` / `refactor` / `test` / `iter`。

### 提 PR 之前

1. `git status` 干净（过程资产未误入版本控制，`.DS_Store` / `__pycache__/` / `.pyc` 已被 `.gitignore` 挡掉）
2. `python3 ai_workflow/validate_skills.py .cursor/skills` 通过（13/13 PASS）
3. PR 描述里附上 `fail_report_S*.md`（如有）和 `review_report.md` 关键结论

---

## 常见问题

<details>
<summary><b>Q：跑某个阶段时原料不合格，会污染产出吗？</b></summary>

不会。失败报告会落到对应阶段的 `fail_report_S*.md`，并明确指出缺什么，补全后重跑即可。

</details>

<details>
<summary><b>Q：我可以只跑 S5/S6 吗？</b></summary>

可以。每阶段独立可触发——只要 `test_points.json` 准备好，就能直接跑对应阶段。
</details>

<details>
<summary><b>Q：SKILL.md 改坏了怎么办？</b></summary>

`ai_workflow/validate_skills.py` 会按 agentskills.io 1.0 规范校验；`.cursor/hooks/scan_module_definitions.py` 会在 sessionStart 时自动跑体检。CI 里也可以加一行 `python3 ai_workflow/validate_skills.py` 作为门禁。
</details>

<details>
<summary><b>Q：8 模块有哪些？</b></summary>

CONFIG（配置）/ UI（界面）/ BIZ（业务）/ UTIL（辅助）/ LINK（关联）/ SPECIAL（特殊情境）/ LOG（日志）/ HINT（提示）。详见 [`.cursor/MODULES.md`](.cursor/MODULES.md)。
</details>

---

## 维护

| | |
|---|---|
| **Owner** | QA 平台组 |
| **AI 工具链** | Cursor + Claude Opus 4 / Claude Code |
| **更新机制** | S8 自迭代 + 人工评审 |
| **License** | [MIT](LICENSE) |

> 任何阶段出问题，第一时间看 `fail_report_S*.md`——这是流水线里"自检不出错"的关键设计。
