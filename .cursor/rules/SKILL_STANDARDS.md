# AIDocxWorkFlow — Skill 编写与维护规范

> 本规范保证本项目所有 `SKILL.md` 文件同时兼容：
> - **Cursor Agent**（私有字段 `disable-model-invocation`）
> - **Hermes Agent**（agentskills.io 标准）
> - **Claude Code / Codex CLI / OpenCode**（agentskills.io 标准）
>
> 验证脚本：`ai_workflow/validate_skills.py`

---

## 1. 文件结构

```
my-skill/
├── SKILL.md              ← 唯一必填
├── scripts/              ← 可选：可执行代码
├── references/           ← 可选：参考文档
└── assets/               ← 可选：模板/资源
```

- 目录名 = `name` 字段值（**严格一致**）
- 目录名只允许 `[a-z0-9-]`，kebab-case
- `SKILL.md` 必须存在且非空

## 2. SKILL.md frontmatter 规范

### 必填字段

#### `name`
- 1-64 字符
- 仅小写字母/数字/单连字符
- 不以 `-` 开头或结尾
- 无连续 `--`
- **必须等于父目录名**

```yaml
name: aidocx-s1-review
```

#### `description`
- 1-1024 字符
- **必须包含至少 1 个触发短语**（建议 3-5 个）
- 推荐触发短语（中英任选其一或混用）：
  - 英文：`Use when ...` / `Use this skill when ...` / `Use for ...` / `Triggered when ...`
  - 中文：`使用当 ...` / `用于 ...` / `触发当 ...`
- 推荐使用多行 `>` 块结构，便于阅读：

```yaml
description: >
  AIDocxWorkFlow Stage 1 — 需求评审。执行需求文档的5维度评审，输出评分与判决。
  Use when the user runs /aidocx-s1-review, pastes raw requirements, or starts a Stage 1 review task.
  使用当用户执行 /aidocx-s1-review、粘贴原始需求文档、或进行 S1 需求评审任务时。
```

### 推荐填写的可选字段

#### `license`
- 字符串，许可证名称
- 本项目统一使用 `MIT`

#### `compatibility`
- ≤ 500 字符
- 描述支持的环境
- 推荐模板：

```yaml
compatibility: Cursor Agent (>=1.0), Claude Code, Codex CLI, Hermes Agent (>=2026.6), any agentskills.io compliant agent
```

#### `metadata`
- 任意 key-value 映射
- 本项目统一使用：

```yaml
metadata:
  framework: AIDocxWorkFlow
  pipeline_stage: <stage-name>
  spec_version: agentskills.io/1.0
  cursor_compat: true|false
  hermes_compat: true|false
```

#### `allowed-tools`
- 空格分隔的预批准工具列表（实验性）
- 仅当 skill 需要特定工具时声明

### Cursor 兼容字段（保留，不删除）

```yaml
disable-model-invocation: true   # 防止 Cursor 在不该触发时自动调用
```

- agentskills.io 不识别此字段，但验证脚本会标记为"Cursor 兼容字段"，**不视为违规**
- 本项目所有 9 个 stage skill 都保留此字段，避免 Cursor 在用户闲聊时误触发

## 3. body 内容规范

### 标题结构
- 至少 1 个 H1 (`# 标题`)
- 推荐 H2 分章节（`## 触发场景`、`## 输入材料`、`## 输出规范` 等）

### 推荐章节（按需）
- **阶段入口**：触发方式 + 前置材料清单
- **核心任务**：本 skill 做什么
- **输入审查**：材料检查清单
- **输出规范**：成功 / 失败两种产出
- **与其他阶段的衔接**：上下游依赖
- **代码入口**：Python 函数签名
- **关联文件**：相关 prompt 模板 / 引擎 / 输出目录

### 写作风格
- 中文为主，命令和路径用英文
- 命令块用 `bash` `python` `json` 等代码围栏标注语言
- 表格优先于长段落（agent 阅读友好）

## 4. 命名约定

| 用途 | 前缀 | 示例 |
|---|---|---|
| 9-stage 流水线 skill | `aidocx-s{N}-*` | `aidocx-s1-review` |
| 辅助工具 skill | `aidocx-*` | `aidocx-feedback-logger` |
| Hermes 后台 skill | `aidocx-*` | `aidocx-batch-runner` |
| 顶层入口 skill | `aidocx-workflow` | `aidocx-workflow` |

## 5. 维护流程

### 新增 skill
1. 在 `.cursor/skills/` 或 `workflow_assets/hermes_skills/` 创建目录
2. 写 `SKILL.md`，遵循本规范
3. 跑 `python3 ai_workflow/validate_skills.py <dir>` 验证
4. 修复所有 errors（warnings 可接受但建议修）
5. commit

### 修改现有 skill
1. 修改 SKILL.md
2. 跑验证脚本
3. 若 `name` 字段变更，**同时重命名目录**
4. commit

### 批量升级
- 用 `python3 ai_workflow/upgrade_skills.py <dir>` 自动追加 license/compatibility/metadata
- 不会修改 `name` 和 `description` 核心内容

## 6. 验证脚本使用

```bash
# 验证 Cursor skills
python3 ai_workflow/validate_skills.py .cursor/skills

# 验证 Hermes skills
python3 ai_workflow/validate_skills.py workflow_assets/hermes_skills

# 同时验证两个 + 输出 JSON
python3 ai_workflow/validate_skills.py .cursor/skills reports/cursor_v1.json
python3 ai_workflow/validate_skills.py workflow_assets/hermes_skills reports/hermes_v1.json

# 退出码
# 0 = 合规
# 1 = 有 errors（阻断）
# 2 = 参数错误
```

### CI 集成
```yaml
# .github/workflows/skill-validation.yml（示例，未启用）
- name: Validate skills
  run: |
    python3 ai_workflow/validate_skills.py .cursor/skills
    python3 ai_workflow/validate_skills.py workflow_assets/hermes_skills
```

## 7. 与 Superpowers / Hermes 的关系

### Superpowers
- 通过 Cursor 插件市场安装（`/add-plugin superpowers`）
- 它的 skill 是 Cursor 全局的，不在我们的仓库内
- 我们**借用**它的方法论（brainstorming → writing-plans → TDD）但**不复制**它的 skill 文件

### Hermes
- 通过 `curl ... | bash` 安装
- 它的 skill 库在 `~/.hermes/skills/`，是 markdown 文件
- 我们项目自有的 Hermes skill 放在 `workflow_assets/hermes_skills/`
- 部署到 Hermes 时执行：
  ```bash
  cp -r workflow_assets/hermes_skills/* ~/.hermes/skills/
  ```

## 8. 版本管理

- 本规范版本：`v1.0`（2026-06-14）
- 后续变更需在 `metadata.spec_version` 同步

## 9. 参考

- agentskills.io 规范：https://agentskills.io/specification
- Superpowers 仓库：https://github.com/obra/superpowers
- Hermes Agent 文档：https://hermes-agent.nousresearch.com/
- 本项目 AIDocxWorkFlow 规则：`.cursor/rules/AIDocxWorkFlow.mdc`
