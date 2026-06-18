# Git Hooks — codegraph 自动同步

## 启用

```bash
git config core.hooksPath .githooks
```

设置后，以下 git 操作会**自动跑** `codegraph sync -q`：

| Hook | 触发时机 |
|---|---|
| `post-checkout` | `git checkout` / `git switch` 切分支时 |
| `post-merge` | `git pull` / `git merge` 完成后 |
| `post-rewrite` | `git commit --amend` / `git rebase` 改写历史后 |

## 不启用会怎样

代码仍然能跑，但**外部编辑器 / CLI 场景下 codegraph 索引不会自动更新**。
Cursor IDE 内的 `afterFileEdit` hook（`.cursor/hooks/codegraph_sync.py`）会兜底 IDE 写代码场景。

## 覆盖 codegraph 路径

```bash
export CODEGRAPH_BIN=/custom/path/to/codegraph
```

## 失败处理

Hook 内部用 `|| true` 包裹 `codegraph sync`，**失败不阻塞 git 操作**。
失败原因会留在 stderr（git 静默丢弃），需要排查时手动跑：

```bash
codegraph sync .
```
