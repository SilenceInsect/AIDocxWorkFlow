# AIDocxWorkFlow × Superpowers × Hermes — 手动操作清单

> 本文件列出**需要你手动执行**的步骤（已自动完成的部分在底部汇总）。
> 每步旁边标注了预估时间和风险等级。

---

## 步骤 1 · 安装 Superpowers（5 分钟 · 低风险）

Superpowers 是 Cursor 官方市场插件，一行命令装上。装上后**只在 Cursor Agent 内**生效，不影响系统其他部分。

**操作**：

1. 打开 Cursor Agent（`Cmd+L` / `Ctrl+L`）
2. 在聊天框输入：
   ```
   /add-plugin superpowers
   ```
3. 等待 Cursor 下载并激活插件
4. **新开一个 Agent 会话**（重要：必须新开会话，旧会话不会激活）
5. 在新会话问：
   ```
   Do you have superpowers?
   ```
6. Agent 应该会确认安装并列出可用 skill

**预期看到**：`brainstorming`, `test-driven-development`, `systematic-debugging`, `writing-plans`, `writing-skills` 等 10+ 个 skill。

**遇到问题**：
- "Plugin command not found" → 更新 Cursor 到最新版（Help → Check for Updates）
- 安装后无反应 → 关闭 Cursor 重新打开

**更新命令**（未来用）：
```
/plugin-update superpowers
```

**卸载命令**（如果想回退）：
```
/plugin-remove superpowers
```

---

## 步骤 2 · 安装 Hermes Agent（15-30 分钟 · 中风险 · 涉及系统安装）

Hermes 会装到 `~/.hermes/`，需要 Python 3.11+ 和 Node.js v22。安装器会自动处理，但**会修改 PATH 和创建系统服务**（macOS launchd）。

**前置条件**：
- macOS / Linux / WSL2（Windows 原生不支持）
- 至少 1GB 磁盘空间
- 1 个 LLM provider 的 API key（推荐 OpenRouter，便宜且通用）

**操作**：

1. **获取 OpenRouter API key**（推荐，也可用其他 provider）：
   - 去 https://openrouter.ai 注册
   - 创建 API key（充值 $5 够用几个月）
   - 复制 key 备用

2. **运行安装器**：
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```
   安装器会自动：
   - 装 `uv`（Python 包管理器）
   - 装 Python 3.11（用 uv，不需 sudo）
   - 装 Node.js v22
   - 装 ripgrep、ffmpeg
   - clone hermes-agent 仓库
   - 创建虚拟环境
   - 设置全局 `hermes` 命令

3. **重新加载 shell**：
   ```bash
   source ~/.zshrc
   ```

4. **配置 LLM provider**：
   ```bash
   hermes setup
   ```
   按提示选择 OpenRouter，粘贴 API key。

5. **验证安装**：
   ```bash
   hermes doctor
   hermes --version
   ```

6. **第一次对话**（可选）：
   ```bash
   hermes
   ```
   看到 `❯` 提示符即可开始对话。

**沙箱配置**（强烈建议）：
```bash
hermes config set terminal.backend docker
```
这会让 Hermes 的所有命令在 Docker 容器里跑，不会污染你的系统。

**部署我们的 skill 到 Hermes**：
```bash
# 复制本项目自有的 Hermes skill 到 Hermes 全局目录
mkdir -p ~/.hermes/skills
cp -r ~/Documents/TestDev/AIDocxWorkFlow/workflow_assets/hermes_skills/* ~/.hermes/skills/

# 验证
hermes skills list | grep aidocx
```

**设置夜间 cron**（可选）：
```bash
# 每天 23:00 跑批量流水线，结果发到 Telegram
hermes cron add "0 23 * * *" \
  --command "/skill aidocx-batch-runner" \
  --notify-on-fail
```

**遇到问题**：
- Python 3.11 装不上 → 手动 `brew install python@3.11`
- API key 验证失败 → 检查 key 格式（OpenRouter 应该是 `sk-or-v1-...`）
- 想卸载：`rm -rf ~/.hermes ~/.local/bin/hermes`（不会影响系统 Python）

---

## 步骤 3 · 部署本项目的 Hermes skill（2 分钟 · 零风险）

如果步骤 2 跳过了 cron 配置，可以只部署 skill：

```bash
mkdir -p ~/.hermes/skills
cp -r ~/Documents/TestDev/AIDocxWorkFlow/workflow_assets/hermes_skills/* ~/.hermes/skills/
hermes skills list | grep aidocx
```

应该看到 `aidocx-batch-runner`。

---

## 步骤 4 · 验证 Superpowers 工作流（10 分钟 · 零风险）

Superpowers 装上后，**下次改任何 AIDocxWorkFlow 的 SKILL.md 或 STAGE_S*.mdc 之前**，先主动调用 brainstorming skill：

1. 打开 Cursor Agent
2. 输入：
   ```
   use the brainstorming skill — I'm thinking about adding a new S9 deployment stage
   ```
3. Agent 会进入 Socratic 提问模式，先问你 5-10 个澄清问题，再开始写代码

**这是 Superpowers 的核心价值**：防止 AI 跳进代码就开干。

---

## 步骤 5 · 验证 Hermes skill 加载（5 分钟 · 零风险）

```bash
# 进入 Hermes
hermes

# 在 prompt 里输入
❯ /skill aidocx-batch-runner

# Hermes 会展示这个 skill 的说明
# 然后你可以：
❯ 跑一下当前 requirements/ 目录里的所有需求
```

如果 `requirements/` 是空的，Hermes 会扫描并跳过（无操作）。

---

## 已自动完成的部分（无需你操作）

| # | 任务 | 状态 | 文件 |
|---|---|---|---|
| 1 | 写 agentskills.io 合规验证脚本 | ✅ | `ai_workflow/validate_skills.py` |
| 2 | 写批量升级脚本 | ✅ | `ai_workflow/upgrade_skills.py` |
| 3 | 升级 13 个 Cursor skills 到全合规 | ✅ | `.cursor/skills/*/SKILL.md` |
| 4 | 验证：13 个 skill 全部 0 errors 0 warnings | ✅ | `workflow_assets/validation_reports/skills_validation_v3.json` |
| 5 | 新增 Hermes 专用 skill `aidocx-batch-runner` | ✅ | `workflow_assets/hermes_skills/aidocx-batch-runner/SKILL.md` |
| 6 | 写 skill 编写规范文档 | ✅ | `.cursor/rules/SKILL_STANDARDS.md` |

---

## 时间线建议

| 阶段 | 时长 | 时机 |
|---|---|---|
| 步骤 1（Superpowers） | 5 分钟 | 现在就做，立刻受益 |
| 步骤 2（Hermes 安装） | 30 分钟 | 周末有空再做 |
| 步骤 3-4（部署+验证） | 15 分钟 | 步骤 2 完成后接着做 |
| 步骤 5（首次跑批） | 5 分钟 | 完成所有步骤后跑一次试试 |

---

## 升级路径

| 阶段 | 当前 | 未来 |
|---|---|---|
| 短期（1-2 周） | Superpowers 给 Cursor 加纪律，Hermes 闲置 | 熟悉两个工具 |
| 中期（1-2 月） | Hermes 跑夜间批处理 | 写 `ai_workflow/orchestrator.py` 主体 |
| 长期（3+ 月） | Hermes 自动写新 skill、归档经验 | 流水线自生长 |

---

## 卸载/回退

- Superpowers：`/plugin-remove superpowers`（在 Cursor Agent 里）
- Hermes：`rm -rf ~/.hermes ~/.local/bin/hermes`（不破坏项目文件）
- 本项目的 skill 文件：删除 `.cursor/skills/*/SKILL.md` 不会破坏 pipeline，删除了相应的 stage 命令会失效
