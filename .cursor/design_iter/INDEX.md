# AIDocxWorkFlow 方案迭代索引

> 本目录记录 AIDocxWorkFlow **所有规则 / 结构 / 流程**的设计方案迭代。
> 每一份方案 v{N} 必有 **"解决 / 新增 / 遗留" 3 栏**——遗留问题直接喂入 v{N+1}。
> **目录级别**：`.cursor/` 下，与 `rules/` / `skills/` / `hooks/` 并列。

---

## 当前生效

| 版本 | 标题 | 状态 | 创建时间 | 未解决问题 |
|---|---|---|---|---|
| **v1** | 规则体系重构（备份迁入 + 3 栏框架） | 已被 v2 取代 | 2026-06-17 | 10（v2 启动后冻结） |
| **v2** | 5 决策回答 + 4 步迁移实施 | **待 5 决策** | 2026-06-17 | 5（Q-001~Q-005 必答） + 5（v3 跟踪） |

> **v2 是当前生效方案**——基于 `plans/v1/PLAN.md`（v1 是 v2 起点）。
> v2 启动前**必读** `plans/v2/PLAN.md §⚠️ 启动必读`（5 决策清单）。

---

## 操作命令

```bash
# 状态总览
python3 .cursor/design_iter/scripts/design_iter.py status

# 启动 v2（从 v1 复制 + 自动建 3 栏骨架）
python3 .cursor/design_iter/scripts/design_iter.py new v2 "<v2 标题>"

# 整份回滚到 v1
python3 .cursor/design_iter/scripts/design_iter.py rollback v1

# 看 v1 vs v2 差异
python3 .cursor/design_iter/scripts/design_iter.py diff v1 v2

# 把 v2 的某个遗留问题标记为已解决
python3 .cursor/design_iter/scripts/design_iter.py resolve v2 Q-001

# 列出所有方案
python3 .cursor/design_iter/scripts/design_iter.py list
```

---

## 目录结构

```
.cursor/design_iter/
├── INDEX.md                    ← 本文件（人类索引）
├── INDEX.json                  ← 机器可读（元数据）
├── current → plans/v2          ← 软链：当前生效方案
├── README.md                   ← 目录使用说明
├── plans/
│   ├── v1/
│   │   ├── PLAN.md             ← v1 主方案（398 行：3 栏框架 + 原方案正文）
│   │   ├── open_questions.md   ← v1 遗留问题（10 个未决 + 优先级排序）
│   │   ├── resolved_questions.md ← v1 已解决
│   │   ├── decisions.json      ← v1 决策清单（D-001 ~ D-003）
│   │   └── changes/            ← diff 产物目录
│   └── v2/                     ← v2（v2.1 启动后创建）
│       ├── PLAN.md             ← v2 主方案（5 决策必答清单 + 3 栏）
│       ├── open_questions.md   ← v2 启动版（Q-101~Q-104 + Q-201）
│       ├── resolved_questions.md ← v2 启动决策（D-201~D-203）
│       └── decisions.json      ← v2 决策占位（D-101~D-105 待点头）
├── archive/                    ← 覆盖前的自动备份
└── scripts/
    └── design_iter.py          ← CLI 工具（6 子命令）
```

---

## 关键概念

### 3 栏框架

每份方案 PLAN.md **顶部必有**：

1. **本次 v{N} 解决的问题**（来自 v{N-1} 的 open_questions）
2. **本次 v{N} 新增内容**
3. **本次 v{N} 仍遗留的问题**（→ v{N+1} 解决）

### current 软链

- `current` 是**软链** → `plans/v1/`
- 回滚 = **改软链**（不复制文件）
- 备份 = 覆盖前自动存到 `archive/`

### 问题编号

- `Q-XXX` 编号 3 位（如 `Q-001`）
- `[ ]` 未决 / `[x]` 已决
- v1 自身的决策用 `D-XXX`（区别于 v1 收到的待决问题）

---

## 详细引用

| 内容 | 路径 |
|---|---|
| 完整 v1 方案 | `.cursor/design_iter/plans/v1/PLAN.md` |
| v1 遗留问题 | `.cursor/design_iter/plans/v1/open_questions.md` |
| v1 已解决 | `.cursor/design_iter/plans/v1/resolved_questions.md` |
| v1 决策清单 | `.cursor/design_iter/plans/v1/decisions.json` |
| 完整 v2 方案 | `.cursor/design_iter/plans/v2/PLAN.md` |
| v2 5 决策必答清单 | `.cursor/design_iter/plans/v2/PLAN.md#⚠️-启动必读5-个核心决策必答清单` |
| v2 决策占位 | `.cursor/design_iter/plans/v2/decisions.json` |
| 备份原文件 | `workflow_assets/_refactor_backup/PLAN_v1_2026-06-17_021.bak` |
| 项目根铁律 | `AGENTS.md` |

---

> **维护者**：每次新方案都先 `new` → 填 3 栏 → 答遗留问题 → 切 current。
