# INDEX.md / INDEX.json 维护机制决策表（2026-07-15）

## 触发

用户指出：INDEX.md / INDEX.json 当前**没有维护钩子 / 没有维护规则**——靠人工同步注定脱钩。

## 现状（已 Read hooks.json + scripts/）

1. **没有任何钩子**维护 INDEX.md / INDEX.json
2. `scripts/design_iter.py` 有 6 子命令（status / list / new / diff / rollback / resolve）——但**只搬文件，不读 json 自动同步**
3. `afterFileEdit` 钩子列表只有 `sync_modules_table.py`（MODULES.md 维护）+ `codegraph_sync.py`（代码图维护）
4. 上次手工对齐发现 4 字段脱钩（`current: v2`、`updated_at: 2026-07-09`、`plans[]` 缺 9 项、`INDEX.md` 描述与实际不符）—— 都是**完全靠人工读 + 改**

## 候选方案（请拍 1）

### 候选 A（最小）— `afterFileEdit` 加 1 个 INDEX 同步钩子

- 新增 `.cursor/hooks/design_iter_index_sync.py`
- 触发时机：afterFileEdit（governance/design_iter/** 改动时）
- 行为：
 1. 重扫 `plans/` 目录列表
 2. 对比 `INDEX.json#plans[]` 差异
 3. 自动补缺失项 / 移除不存在的项
 4. 更新 `INDEX.json#updated_at`
- **不维护 `current` 字段**（避免改 current 时被脚本覆盖人为决策）
- **不维护 INDEX.md**（INDEX.md 是人写的表，脚本只生成 json）
- 影响：1 新文件 + hooks.json +1 项
- 风险：钩子被反复触发可能拖慢 IDE

### 候选 B（推荐）— A + `current` 同步 + INDEX.md 重生成

- A 基础上：扫描 `INDEX.json#current` 字符串在 INDEX.md 中是否一致
- 若不一致 → 改 INDEX.md §1 那一行（**精确替换**，不重写全文）
- 影响：1 新文件 + hooks.json +1 项 + INDEX.md 锁住 §1 行结构
- 风险：INDEX.md §1 行结构变更需同步改钩子

### 候选 C（彻底）— 独立 `scripts/sync_index.py` + CI 化

- 不挂 hooks，挂 cron / pre-commit / GitHub Action
- 每周扫一次 vs plans/ 目录
- 触发 commit 提示："plans/ 目录变动，INDEX 已脱钩，需 `python3 governance/design_iter/scripts/sync_index.py` 同步"
- 影响：1 新脚本 + pre-commit hook 或 GitHub Action YAML
- 优点：不影响 IDE 性能
- 缺点：必须装 git hook 或配 CI（环境依赖）

### 候选 D（最简）— 不加任何自动机制，规则文档化

- 在 `AGENTS.md` / `governance/design_iter/README.md` 写"任何 plans/v{N} 目录变动后，必须人工执行 `python3 scripts/design_iter.py list` + 同步 INDEX.json + INDEX.md"
- 不加任何 hook / 脚本
- 影响：0 新文件（只改 README/AGENTS）
- 优点：0 维护成本
- 缺点：**用户明确否定**——"没有维护的钩子，没有维护的规则，写再多都没用"

## 推荐

**候选 B** —— 自动同步最关键的脱钩点（current + plans 列表 + updated_at），INDEX.md 同步 §1 那一行精确替换。不扫正文（人写正文，钩子不动）。

## 替代方案讨论

| 替代方案 | 否决理由 |
|---|---|
| 候选 A（不同步 current） | 上次实际脱钩的就是 current——只补 plans 不修 current，等于没解决用户痛点 |
| 候选 C（CI 化） | 项目无 .github/ 目录、无 CI 配置；CI 化改动面过大（首次建 CI） |
| 候选 D（文档化） | 用户已明确否定 |

## 影响范围

- 新文件：`.cursor/hooks/design_iter_index_sync.py`（约 80 行）
- 改文件：`.cursor/hooks.json` +1 行（afterFileEdit 加 1 条）
- 锁结构：`governance/design_iter/INDEX.md` §1 行结构（"current: v{N}"）不能改形式
- 落档：本文件 + INDEX.md（已落档在本次响应）

## 落档协议执行记录

（本文件即落档占位——§9.5 合规）

## 等待用户拍板

—— 候选 B 提交拍板后执行 hook 编写 + hooks.json 改 + self-test。