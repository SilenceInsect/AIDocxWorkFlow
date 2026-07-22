# INDEX.md 重锚定决策表（2026-07-15）

## 触发

用户问：版本落地进度和版本的交接文档就应该写在迭代文档里面，INDEX.md 的存在目的、设计目的、具体功能职能需要重新锚定。

## 现状问题（已 Read INDEX.md + README.md）

1. INDEX.md 9-20 行"当前生效"方案表 → 应归 `plans/v*/` 每个方案自己记
2. INDEX.md 22-28 行 v14/v13 状态描述 → 应归 `plans/v14/PLAN.md` §本次新增
3. INDEX.md 32-52 行操作命令 → 应归 `README.md`（已存在）
4. INDEX.md 56-98 行目录结构 + current 软链 → 应归 `README.md` 关键设计
5. INDEX.md 132-159 行"详细引用"清单 → 应归 `plans/v*/PLAN.md` 头部
6. INDEX.md 没有"版本进度 + 交接"职能 → 应在 `plans/v*/PLAN.md` 3 栏里承载

**根因**：INDEX.md 当年 v1 时只有 5 个方案 + 1 个 current，功能简单；现在 10+ 个方案 + 软链模式变了 + 出现 cp 模式，INDEX.md 没跟上拆分。

## 新定位候选（请拍 1）

### 候选 A（最小改动）— INDEX.md 只剩 1 行入口

```markdown
# AIDocxWorkFlow 方案迭代

- **当前生效**：[v{N}](plans/v{N}/PLAN.md)（上次切 current：YYYY-MM-DD）
- **操作入口**：`python3 governance/design_iter/scripts/design_iter.py status`
- **详细**：见 `README.md` + `plans/` 各方案
```

- 影响：1 文件（INDEX.md 全文替换）
- 优点：人扫一眼即懂"看哪版、看 README"
- 缺点：跨方案进度看不到（要走 `plans/v*/PLAN.md` 才知每个进度）

### 候选 B（推荐）— INDEX.md = 跨方案速查表，详情下沉到 plans/

```markdown
# AIDocxWorkFlow 方案迭代

> 所有方案详情在 `plans/v{N}/PLAN.md`（每个方案自己写进度 + 交接）。
> 本文件只做"哪版生效 / 哪个有遗留问题"两张速查表。

## 当前生效

- **current**：[v{N}](plans/v{N}/PLAN.md)（上次切 current：YYYY-MM-DD）

## 有遗留问题的方案（→ 下一版启动时必读）

| 版本 | 遗留 Q 数 | open_questions |
|---|---|---|
| v{N-1} | X | `plans/v{N-1}/open_questions.md` |
| ... | | |
```

- 影响：1 文件（INDEX.md）+ 模板（plans/v*/PLAN.md §本次新增 必带"进度"小节）
- 优点：INDEX 极简，方案进度/交接下放到自己家
- 缺点：要回头给每个 plans/v*/PLAN.md 加"进度"小节（最多 10+ 文件，§9.1 红线触发）

### 候选 C（彻底重构）— INDEX.md 删除，新入 `INDEX.json`（机器）

- `INDEX.json` 唯一（机器用）
- 删除 `INDEX.md`
- 人读 `plans/v*/PLAN.md` 自己家
- 进度 + 交接 100% 落在各方案 PLAN.md §本次新增

- 影响：1 文件删除（INDEX.md）+ 各 plans/v*/PLAN.md 必带"进度 + 交接"
- 优点：彻底消除"双源"风险（人 INDEX.md + 机器 INDEX.json 同源不同步）
- 缺点：彻底删除需要 Git 历史保护 + 用户可能仍想看"跨方案一览"

## 推荐

**候选 B** —— 兼顾"人扫一眼"和"进度下放"，改动量小（1 文件 + 模板）。

## 替代方案讨论

| 替代方案 | 否决理由 |
|---|---|
| 候选 A（极简） | 跨方案进度看不到，违反用户"版本落地进度写在迭代文档里"诉求 |
| 候选 C（删除） | 改动过大 + 用户没说"删 INDEX.md" |

## 影响范围

- INDEX.md（1 文件）
- plans/v*/PLAN.md（最多 10+ 文件，加"进度"小节模板）—— **可分批**（§9.1 红线）
- CLI status 输出（如需）

## 落档协议执行记录

（本批未落档——等用户拍板候选 B 后执行）