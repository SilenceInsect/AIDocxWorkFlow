#!/bin/bash
# post-commit hook: 提交了 module_templates 变更时自动触发增量索引
#
# 安装方式（选一）：
#   方式 1（推荐）：复制到 .git/hooks/post-commit 并赋予执行权限
#     cp .cursor/hooks/git_post_commit_module_indexer.sh .git/hooks/post-commit
#     chmod +x .git/hooks/post-commit
#
#   方式 2：创建符号链接
#     ln -sf ../../.cursor/hooks/git_post_commit_module_indexer.sh .git/hooks/post-commit
#
# 注意：.git/hooks/ 目录通常不纳入版本控制，无需 git add。
#       符号链接方式可随项目迁移，方式 1 需要在新机器上重新安装。

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
VENV_PYTHON="$REPO_ROOT/.venv/bin/python3"
INDEXER="$REPO_ROOT/ai_workflow/knowledge_indexer.py"

# 需要索引的模块目录前缀
MODULE_TEMPLATES_PREFIX="knowledge/public/module_templates/"

# 从 git diff-tree 获取本次提交变更的文件列表
changed_files=$(git diff-tree --no-commit-id --name-only -r HEAD)

# 检查是否包含 module_templates 变更
has_module_change=false
changed_modules=""

while IFS= read -r file; do
    if [[ "$file" == "$MODULE_TEMPLATES_PREFIX"* ]] && [[ "$file" != *"_candidates/"* ]]; then
        # 从路径提取模块 ID（如 knowledge/public/module_templates/UI/xxx.md → UI）
        module=$(echo "$file" | cut -d'/' -f4)
        if [[ -n "$module" ]]; then
            if [[ ",$changed_modules," != *",$module,"* ]]; then
                changed_modules="${changed_modules}${module},"
            fi
        fi
    fi
done <<< "$changed_files"

# 如果有变更，触发增量索引
if [[ -n "$changed_modules" ]]; then
    echo "[post-commit hook] Detected module_templates changes: ${changed_modules%,}"
    IFS=',' read -ra MODULES <<< "${changed_modules%,}"
    for module in "${MODULES[@]}"; do
        if [[ -n "$module" ]]; then
            echo "  → Indexing: $module"
            "$VENV_PYTHON" -m ai_workflow.knowledge_indexer \
                --module "$module" \
                --incremental \
                --quiet \
                2>&1 || echo "  ! Indexer failed for $module (non-blocking)"
        fi
    done
fi
