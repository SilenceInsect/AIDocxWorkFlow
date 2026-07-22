# governance/ — 项目治理目录

AIDocxWorkFlow 的**规则/流程设计变更**在这里走"方案 → 评审 → 闭环"三段。
不属于 Cursor 私有配置，随仓库版本化（入 git）。

---

## 目录构成

| 子目录/文件 | 角色 |
|---|---|
| `design_iter/` | **主目录**——所有规则的方案迭代、归档、CLI 工具 |
| `design_iter/archive/v17_20260719_220000.bak/open_questions.md` | v17 治理已解条目归档（Q-V17-001~007 只读副本） |

---

## `design_iter/` 三段结构

```
design_iter/
├── INDEX.md / INDEX.json   # 总览（SSOT：当前版本、进度、交接）
├── README.md               # 详细版（CLI 用法、3 栏框架、软链 vs cp 模式）
├── plans/v{N}/             # 每版方案：PLAN.md（解决/新增/遗留）+ decisions.json + open_questions.md
├── archive/                # 已闭环版本的备份（含时间戳 .bak）
├── current/                # 当前草案档（候选/占位，未入 plans/）
└── scripts/                # CLI 工具（design_iter.py，6 子命令：status/new/complete/switch/stop/rollback/diff/resolve）
```

**核心原则**：每份方案 v{N} 必有 **解决 / 新增 / 遗留** 三栏，遗留问题直接喂入 v{N+1}，`open_questions.md` 不可缺。

---

## 一句话关系

- `governance/design_iter/` = 规则的"**git log**"（为什么改、改过什么）
- `.cursor/rules/*.mdc` + `.cursor/skills/*/SKILL.md` = 规则的"**当前 HEAD**"（最终生效）
- `.cursor/hooks/` = 规则的"**CI**"（防脱钩、自动同步）

**改 HEAD 前，先在 design_iter 走方案。**

---

## 快速入口

```bash
# 1. 看当前活跃版本 + 进度
python3 governance/design_iter/scripts/design_iter.py status

# 2. 读某版方案（含遗留问题）
cat governance/design_iter/plans/v31/PLAN.md

# 3. 启动新版本（自动建 3 栏骨架）
python3 governance/design_iter/scripts/design_iter.py new v34 "<v34 标题>"
```

详细 CLI 用法见 [`design_iter/README.md`](design_iter/README.md)；版本总览见 [`design_iter/INDEX.md`](design_iter/INDEX.md)。
