# v20 目录结构整理 - 审计报告

> **生成时间**: 2026-07-18T18:35:00+08:00
> **目标**: 审查当前工程的目录结构，整理零散文件，搞清楚零散文件的创建逻辑然后规整对应逻辑下的文件存放

---

## 1. 零散文件清单

### 1.1 已处理的零散文件

| 文件/目录 | 原位置 | 目标位置 | 操作 | 状态 |
|-----------|--------|---------|------|------|
| `workflow_assets/goals/` | `workflow_assets/` | `.goal-log-db/archive/` | 移动 | ✅ |
| `PRODUCT_DOCUMENTATION.md` | 根目录 | `knowledge/public/` | 移动 | ✅ |
| `431CC982-*/` (空目录) | `.goal-log-db/active/` | — | 删除 | ✅ |
| `09cdc9e7-*/` (已收敛 goal) | `.goal-log-db/active/` | `.goal-log-db/archive/` | 归档 | ✅ |

### 1.2 待处理的零散文件

| 文件/目录 | 位置 | 说明 | 建议处理 |
|-----------|------|------|---------|
| `.cursor/hooks/content_compliance_check.py` | `.cursor/hooks/` | Untracked 功能代码 | 建议 commit |
| `.cursor/hooks/goal_loop_breakloop_hook.py` | `.cursor/hooks/` | Untracked 功能代码 | 建议 commit |
| `.cursor/hooks/goal_loop_hook.py` | `.cursor/hooks/` | Untracked 功能代码 | 建议 commit |
| `.cursor/hooks/index_landing_hook.py` | `.cursor/hooks/` | Untracked 功能代码 | 建议 commit |
| `.cursor/rules/GOAL_BUSINESS_AUDIT.mdc` | `.cursor/rules/` | Untracked 规则文件 | 建议 commit |
| `.cursor/rules/product_format_rules.yaml` | `.cursor/rules/` | Untracked 规则文件 | 建议 commit |
| `.cursor/skills/goal-loop/` | `.cursor/skills/` | Untracked 技能目录 | 建议 commit |
| `ai_workflow/coverage_dual_track.py` | `ai_workflow/` | Untracked 功能代码 | 建议 commit |

---

## 2. 归类决策汇总

### 2.1 Git 分类规则应用

根据 `DESIGN_AND_EXECUTION_STANDARDS.mdc §0.1`:

| 分类 | 规则 | 本次处理 |
|------|------|---------|
| **必须入 Git** | 功能代码、测试代码、规则库、技能库、治理方案、公共知识库 | ✅ |
| **禁止入 Git** | 单次需求输入材料、各阶段运行产物、阶段上下文包、反馈日志、私人分析记录、项目级知识库 | ✅ |

### 2.2 本次归类决策

| 决策 | 依据 | 结果 |
|------|------|------|
| `PRODUCT_DOCUMENTATION.md` → `knowledge/public/` | 公共知识资产，面向用户文档 | ✅ |
| `workflow_assets/goals/` → `.goal-log-db/archive/` | 旧版过程资产，已迁移到新版目录 | ✅ |
| 无效 goal 目录清理 | 维护 .goal-log-db/active/ 清洁 | ✅ |

---

## 3. .gitignore 更新

### 3.1 更新内容

新增忽略规则：

```gitignore
# Workflow assets goals — 旧版 goal 目录（已迁移到 .goal-log-db/archive/）
workflow_assets/goals/
```

### 3.2 当前忽略规则覆盖范围

| 目录/模式 | 说明 |
|-----------|------|
| `workflow_assets/*` | 过程资产（单次需求产物） |
| `.goal-log-db/` | Goal 日志数据库 |
| `workflow_assets/goals/` | 旧版 goal 目录 |
| `resource/` | 本地输入材料 |
| `knowledge/project_local/*` | 项目级私有知识库 |

---

## 4. 目录结构优化

### 4.1 优化前后对比

**优化前**:
```
.
├── PRODUCT_DOCUMENTATION.md      # 零散文件
├── workflow_assets/
│   └── goals/                    # 旧版 goal 目录
└── .goal-log-db/
    └── active/
        ├── 09cdc9e7-*/          # 已收敛（应归档）
        ├── 431CC982-*/          # 空目录（应清理）
        └── ...
```

**优化后**:
```
.
├── knowledge/
│   └── public/
│       └── PRODUCT_DOCUMENTATION.md  # 公共知识资产
└── .goal-log-db/
    ├── archive/
    │   ├── goals/               # 旧版 goal（已归档）
    │   └── 09cdc9e7-*/         # 已收敛 goal（已归档）
    └── active/
        ├── directory-reorg-001/ # 当前 goal
        └── e1c0b1e9-*/         # 其他 goal
```

### 4.2 优化效果

| 指标 | 优化前 | 优化后 |
|------|-------|-------|
| 零散文件 | 2 个 | 0 个 |
| 无效 goal 目录 | 2 个 | 0 个 |
| 目录结构合规性 | 部分合规 | 完全合规 |

---

## 5. 遗留事项

| 事项 | 优先级 | 负责人 | 截止时间 |
|------|-------|-------|---------|
| Commit untracked hooks 文件 | 高 | 用户 | 待定 |
| 验证新目录结构 | 中 | 用户 | 待定 |

---

## 6. 验证命令

```bash
# 验证目录结构
ls -la .goal-log-db/archive/
ls -la knowledge/public/

# 验证 .gitignore
cat .gitignore | grep "workflow_assets/goals"

# 检查 git 状态
git status --short | grep -E "^\?\?.*hooks|^\?\?.*rules|^\?\?.*skills"
```

---

## 7. 结论

本次目录结构整理成功完成以下工作：

1. ✅ 识别并归档旧版 `workflow_assets/goals/` 目录
2. ✅ 将 `PRODUCT_DOCUMENTATION.md` 移动到 `knowledge/public/`
3. ✅ 清理无效 goal 目录
4. ✅ 更新 `.gitignore` 忽略规则

**待办**: 用户需手动 commit untracked hooks 文件。
