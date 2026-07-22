# v8 启动议题（待 v8 期间答完）

> **本文件是 v9 启动输入**——v8 期间答完移到 `resolved_questions.md`。
> **v8 是 single-issue 方案**——目录主轴变更。议题仅从 v7 PLAN.md §3 遗留 + v8 实战发现两个来源。

---

## v7 PLAN §3 遗留（v8 未答完）

> v7 §3 列了 6 个遗留：
> 1. 9 阶段 .mdc 同步更新工作量 → 由 v7.1/v7.2/v7.3 推进（v8 不接）
> 2. S7 审查脚本适配 → v7.1 接（v8 不接）
> 3. S8 读取 S7 review_report.json 适配 → v7.1 接（v8 不接）
> 4. 跨阶段引用一致性回归测试 → v8 实战已部分完成（42 文件改完 + py_compile 通过）
> 5. `before_prompt_dna_check.py` 适配 v7 决策表落档协议 → 不接（v8 不动 hook）
> 6. CHANGELOG [v7] 写入 + design_iter/INDEX.md 更新 → 已部分完成（v7 章节存在，v8 章节新加）

**v8 已答完**：项 4 + 6（部分）

**v8 未答完**：项 1+2+3+5 → 留给 v7.x / v9

---

## v8 实战发现（→ v9 决策）

- [ ] **Q-V9-001**: v3.0/raw 与 v3.01 内容重复
  - **触发**：2026-07-10 检查发现 `resource/游戏道具商城系统/v3.01_raw.docx` 是唯一原档，但 `workflow_assets/游戏道具商城系统/v3.0/raw/extracted_text.md` 内容相同（124 段 / 0 图片）
  - **候选 A（推荐）**：把 `v3.0/raw` 重命名为 `v3.01/raw` → 路径与资源对应
  - **候选 B**：保留 v3.0 目录作为"早期版本快照"，文档化原因
  - **候选 C**：删除 v3.0/raw，从 v3.01 重新跑 S1 Pipeline → 内容覆盖
  - **影响范围**：1 个目录重命名 或 1 次 S1 Pipeline 重跑
  - **v8 不答**——超出目录主轴变更范围

- [ ] **Q-V9-002**: INDEX.md v8 章节未加
  - **触发**：v8 启动但 INDEX.md 还停在 v7 状态（"v7 运行中 / current 已切"）
  - **候选 A**：INDEX.md 加 v8 段（"v8 single-issue 修复 / current 已切 v8"）
  - **候选 B**：保留 v8 章节给 v9 写（避免重复）
  - **影响范围**：INDEX.md 一处表格 + 几行描述

---

## v8 期间无新增议题

> v8 是 single-issue 方案——v8 期间没有"v8 自身"产生的新未决问题。
> v8 决策清单（D-V8-001 ~ D-V8-007）已 100% 闭环，详见 `decisions.json`。