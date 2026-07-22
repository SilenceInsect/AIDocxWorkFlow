# governance/design_iter/ — 方案迭代目录

> AIDocxWorkFlow 所有规则 / 结构 / 流程的设计方案都在这里管理。
> **核心原则**：每份方案 v{N} 必有"解决 / 新增 / 遗留" 3 栏，遗留问题直接喂入 v{N+1}。
> **定位**：这是项目治理目录，不属于 Cursor 私有配置。

---

## 3 分钟上手

### 1. 看当前生效方案

```bash
python3 governance/design_iter/scripts/design_iter.py status
```

### 2. 看 v1 的遗留问题（v2 启动时必读）

```bash
cat governance/design_iter/plans/v1/open_questions.md
```

### 3. 启动 v2

```bash
# 自动从 v1 复制 + 建 3 栏骨架
python3 governance/design_iter/scripts/design_iter.py new v2 "<v2 标题>"

# 然后编辑 governance/design_iter/plans/v2/PLAN.md
# 在顶部 3 栏填：解决（v1 留下的）/ 新增 / 遗留
```

### 4. 整份回滚

```bash
python3 governance/design_iter/scripts/design_iter.py rollback v1
```

---

## CLI 6 子命令

| 子命令 | 用途 |
|---|---|
| `status` | 输出 current + 所有方案 + open/resolved 计数 |
| `list` | 同 status |
| `new <ver> <title>` | 从 current 复制 → plans/{ver}/ + 强制建 3 栏 |
| `diff <v1> <v2>` | 生成 plans/{v2}/changes/diff_{v1}_to_{v2}.md |
| `rollback <ver>` | 覆盖前自动备份到 archive/ → 改 current 软链 |
| `resolve <ver> <Q-XXX>` | 把 open 的 Q-XXX 移到 resolved |

---

## 关键设计

### 1. 软链回滚（核心）

`current` 是软链 → `plans/v{N}/`。回滚 = **改软链**（不复制文件）。

```bash
$ ls -la governance/design_iter/current
lrwxr-xr-x  current -> plans/v1
```

### 2. 覆盖前自动备份

`new` / `rollback` 触发时，**当前方案自动复制**到 `archive/{name}_{ts}.bak`。

### 3. 3 栏强制

每份 `PLAN.md` **顶部必有**：

```markdown
## v{N} 必备 3 栏

### 1. 解决的问题（来自 v{N-1}）
### 2. 本次新增
### 3. 仍遗留（→ v{N+1}）
```

`new` 子命令**只建骨架**——填内容是人 / AI 后续动作。

### 4. 不生成事实

CLI **不扫代码 / 不读 .mdc**——只操作"已经写过的方案"。事实由 LLM 推理，CLI 只搬文件。

---

## 与项目其它部分的关系

| 角色 | 路径 |
|---|---|
| **8 模块 SSOT** | `.cursor/MODULES.md`（不动） |
| **跨阶段决策** | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`（**v2 决策后**改写） |
| **9 阶段规范** | `.cursor/rules/STAGE_S*.mdc`（**v2 决策后**改写） |
| **12 SKILL 入口** | `.cursor/skills/*/SKILL.md`（**v2 决策后**改写） |
| **本目录** | `governance/design_iter/`（治理层，**v1 已建立**） |
| **项目根铁律** | `AGENTS.md`（v2.1 新建） |
| **v1 起点** | `governance/design_iter/plans/v1/PLAN.md` |
| **v1 备份** | `workflow_assets/_refactor_backup/PLAN_v1_2026-06-17_021.bak` |

---

## 不做什么

- ❌ 不扫代码生成方案（CLI 只搬文件）
- ❌ 不改 `MODULES.md`（8 模块 SSOT 不在本目录管）
- ❌ 不替用户做决策（Q-001 ~ Q-005 等 v2 用户答）
- ❌ 不强制字段级回滚（v1 只做整份回滚；字段级是 v2 候选）

---

> **详细索引**：`cat governance/design_iter/INDEX.md`
