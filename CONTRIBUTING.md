# 贡献指南（Contributing to AIDocxWorkFlow）

感谢你愿意让这套工作流变得更好。本文件介绍**日常**贡献流程。
如果你只是想**使用**这条流水线，请直接看 `README.md`。

---

## TL;DR（一分钟速览）

```bash
git checkout -b feat/<short-topic>
# ……做出你的修改……
python3 ai_workflow/validate_skills.py .cursor/skills   # 必须输出 "13/13 PASS"
git add -A
git commit -m "feat: <what & why>"
git push origin feat/<short-topic>
# 向 main 发起 PR，并 @SilenceInsect
```

---

## 这个仓库是什么 / 不是什么

| 层次 | 存在位置 | 在 `main` 上可变？ |
|---|---|---|
| **Prompts**（`.cursor/rules/*.mdc`） | 是 | 是 |
| **Skills**（`.cursor/skills/*/SKILL.md`） | 是 | 是 |
| **校验工具链**（`ai_workflow/validate_skills.py`、`ai_workflow/upgrade_skills.py`） | 是 | 是 |
| **阶段示例产出**（`workflow_assets/<req_name>/「Stage」/<version>/`） | 是 | 是（仅可新增） |
| **S1–S8 核心 Python 模块**（`ai_workflow/{auto_reviewer,feedback_logger,…}.py`） | 是 | **极少改动** —— 见下方"核心模块"一节 |
| **`.gitignore`**、**`.cursor/hooks.json`** | 是 | **极少改动** —— 见下方"钩子（Hooks）"一节 |

如果你的改动落在标着"极少改动"的行上，请同步更新 `CHANGELOG.md`，并预期会有维护者 review。

---

## 分支策略

- **`main`** —— 干净、纯对话式工作流。必须始终满足：
  - 构建通过：`python3 ai_workflow/validate_skills.py .cursor/skills` 返回 13/13 PASS。
  - 自包含：没有强依赖的外部服务，没有失效链接。
- **`<type>/<short-topic>`** —— 基于 `main` 拉出的功能 / 缺陷修复分支。
- **遗留 / 实验性** —— 例如
  `cursor/integrate-superpowers-and-hermes-with-skill-standardization`：
  实验性的"瘦流水线"改写分支。可能被强推或 rebase。
  **不要**基于它做生产级改动。

分支类型：`feat` `fix` `docs` `refactor` `chore` `test`。

---

## 编辑 Prompts 与 Skills

### `SKILL.md` 规范

每个 `SKILL.md` 都必须遵循
[agentskills.io 1.0](.cursor/rules/SKILL_STANDARDS.md) 规范。文件顶部两
个**必填**字段：

```yaml
---
name: <kebab-case-skill-name>
description: <one-sentence; < 1024 chars; no "I"/"you"/"we">
---
```

如果某个 skill **只**应由用户手动触发（例如 `aidocx-batch-runner`），
请使用 `disable-model-invocation: true` 字段。

`validate_skills.py` 会检查缺字段、frontmatter 错误以及旧版 v1 的
`name:` / `summary:` 格式。**在脚本输出 `0 errors, 0 warnings` 之前，不要合并。**

### 新增一个 skill

1. 选择目录：通用 skill 放在 `.cursor/skills/<name>/SKILL.md`，
   Hermes 专用 skill 放在 `workflow_assets/hermes_skills/<name>/SKILL.md`。
2. 编写 `SKILL.md`（参见规范）。
3. 如果该 skill 应当能在对话中被发现，需要在 `ai_workflow/__init__.py` 注册。
4. 跑一次 `python3 ai_workflow/validate_skills.py .cursor/skills`。
5. 在 `CHANGELOG.md` 的 `[Unreleased] / Added` 段落下补一行。

### 编辑 `STAGE_*.mdc` 规则

1. **通读**现有规则全文 —— 阶段规则之间会互相引用
   （例如 S7 引用 S4 风险点；S6 引用 S5 设计方法）。
2. 编辑规则的 **Markdown 正文**（门禁、检查清单、输出 schema）。
3. 如果是结构性变更，请尽量同步更新对应 `workflow_assets/<req_name>/` 下的示例产物。
4. 重跑校验工具链与任何依赖该规则的阶段示例。

---

## 核心 Python 模块（极少改动）

`ai_workflow/` 下的 6 个模块（`auto_reviewer.py`、`feedback_logger.py`、
`iteration_aggregator.py`、`requirement_reviewer_auto.py`、
`test_case_formatter.py`、`conversation_skills.py`）实现了流水线的
**离线**部分（S1 评分、S7 审查、S8 反馈、S6 格式化）。它们在日常
对话驱动的流水线运行中**不是**必需的。

> 如果你正打算删除或重写其中某个模块，请先停下来想一想：
> 这个改动是不是"切到 agentskills.io 版本"（如果是，正确的做法
> 应该是另开一条实验性分支，**而不是**直接动 `main`）。提交
> `45f658d` 中曾尝试过类似改动，**有意没**有合入 `main`。

如果实在要改动其中之一：

1. 先开一个 issue 说明使用场景。
2. 保持对外的函数签名稳定。
3. 如果 JSON 形态变了，请同步更新 `workflow_assets/<req_name>/` 中
   对应的示例。
4. 在 `CHANGELOG.md` 补一条记录。

---

## 钩子（Hooks）

`.cursor/hooks.json` 控制 `sessionStart`、`beforeSubmitPrompt`、
`afterFileEdit`、`sessionEnd` 等事件上跑什么。这里的改动会影响到项目上的
**每一位**开发者。只有在以下情况才去动它：

- 你要加的钩子对所有人都能帮上忙（例如实验性分支中提出的 SKILL 校验器）。
- 你能在本地无错报地连续跑上一周。
- 该钩子的输出是**幂等**的（跑两次必须安全）。

如果没把握，可以先开一个 draft PR，把钩子设为 disabled
（`"type": "prompt"`），让 reviewer 看到意图而不会自动执行。

---

## Commit 规范

```
<type>(<scope>): <one-line summary, imperative mood, < 72 chars>

<body — why, not what; wrap at 72 chars>

<footer — closes #123, breaks-change notes>
```

常用 type：`feat` `fix` `docs` `refactor` `chore` `test` `perf`。

多 commit 的工作，**请用 rebase** 而非把 `main` merge 进功能分支
（保持日志线性、PR diff 干净）。

---

## Pull Request 自检清单

- [ ] 分支基于 `main`，并已 rebase。
- [ ] `python3 ai_workflow/validate_skills.py .cursor/skills` 通过。
- [ ] 如果改了 `STAGE_*.mdc` 规则，请重跑对应阶段示例并按需更新其产物。
- [ ] 已更新 `CHANGELOG.md`（写在 `[Unreleased]`，breaking change 写在 `[X.Y.Z]`）。
- [ ] 没有把 `.DS_Store` / `__pycache__` / `*.pyc` 误 add 进来。
- [ ] PR 描述包含：是什么 / 为什么 / 如何验证 / UI 改动附截图。

---

## 行为准则（Code of Conduct）

友善。耐心。这条流水线是为所有人服务的，不只是为你一个人。
Review 不是设卡，而是相互兜底。如果 reviewer 表述不清，直接问。

---

## 许可证

向本仓库贡献即表示你同意你的贡献将以
[MIT 许可证](LICENSE) 授权。
