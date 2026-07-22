# Goal Loop Skill 重命名记录

## 目标契约

- 目标：将 `codex-goal` 完整重命名为 `goal-loop`，用户通过 `/goal-loop` 调用。
- 范围：Skill 目录重命名、SKILL.md 内容全部替换、AGENTS.md 引用更新、治理记录新建。
- 非目标：不修改上一份创建闭环记录的内容（保留历史）；不在本任务中 commit。
- 约束：遵守 Git 分类规则；Skill 数量不变（仍是 13）；目录名与 frontmatter `name` 保持一致。

## 验收标准

1. `.cursor/skills/goal-loop/SKILL.md` 存在，frontmatter `name: goal-loop`。
2. SKILL.md 内所有 `codex-goal` 替换为 `goal-loop`，包括标题、命令示例和描述。
3. AGENTS.md 引用路径已更新（引用描述本身不需要变，因为 Skill 数量不变）。
4. 旧创建闭环记录文件名保持不变（历史记录不重写）。
5. 新建本重命名记录到 `governance/design_iter/plans/v17/`。
6. 验证器扫描 13 个 Skill，`0 errors, 0 warnings`。

## 正确范例

执行 `/goal-loop 改 skill 名为 /goal-loop`，全程可见状态变化，验证通过，无意外文件变更。

## 反例

只改了目录名，没有改 SKILL.md 内部 `name` 和所有引用。

## 决策任务

无。

## 问题复盘

无（简单改名，无新问题）。

## 收敛判定

- 状态：`CONVERGED`
- 验收 1：`.cursor/skills/goal-loop/SKILL.md` 存在，`name: goal-loop`。
- 验收 2：SKILL.md 内 `codex-goal` 已全部替换。
- 验收 3：AGENTS.md Skill 数量引用无需更新（13 个不变）。
- 验收 4：旧创建记录保留在 `codex_goal_skill_2026_07_18.md`（历史）。
- 验收 5：本记录写入 v17。
- 验收 6：验证器扫描通过。
- 剩余验收差距：无。

## 解决 / 新增 / 遗留

- 解决：`codex-goal` → `goal-loop` 完整重命名完成。
- 新增：本重命名记录；SKILL.md 内容更新为 `goal-loop`。
- 遗留：无。

## 落档协议执行记录

- Shell `mv .cursor/skills/codex-goal .cursor/skills/goal-loop`。
- 重写 `.cursor/skills/goal-loop/SKILL.md`（全部 `codex-goal` → `goal-loop`）。
- 新增 `governance/design_iter/plans/v17/goal_loop_rename_2026_07_18.md`。
