# T-102 C1/A2 docstring + README 补强（V-103 · MAJOR · worker）

> **本档是落档协议（DNA §9.5）执行记录**——先 Write 占位，再 content 展开。
> 来源：父任务 T-102（governance/design_iter/plans/v27/GOAL.md §C1/A2）

---

## 0. 任务原文摘要

1. `.cursor/hooks/dna_decision_density_check.py` docstring 显式标注默认值 = 5（含 v27 来源 + env 覆盖说明）
2. `.cursor/hooks/README.md`（如存在）新增「阈值覆盖」段，说明 `DNA_DECISION_DENSITY_THRESHOLD=5` 环境变量；如 README 不存在则新建

---

## 1. 先验证据（DNA §9.4）

### 1.1 `dna_decision_density_check.py` 已读全文（245 行）

| 行号 | 内容摘要 | 现状 |
|---|---|---|
| line 6 | `单次响应 > 5 文件改动 = 决策密度违规（v27 C1 更新：3 → 5；与 DNA_3Q_CHECK.mdc §9.1 self-test 上限对齐）` | ✅ **已写 v27 C1 + 默认 5** |
| line 11 | `默认值 5（v27 修订，匹配"self-test 豁免上限"）` | ✅ **已写 默认 5 来源** |
| line 12 | `覆盖方式：环境变量 DNA_DECISION_DENSITY_THRESHOLD=<N>` | ✅ **已写 env 覆盖** |
| line 13 | `上限设定理由：本项目稳定后批量改文件（治理方案动辄 4-6 文件）成常态，3 太严` | ✅ **已写 v6→v27 历史理由** |
| line 24 | `v27 C1 更新：默认阈值 3 → 5（项目稳定期，无需 6 文件以上单 turn）` | ✅ **已写 v6.0 → v27 历史** |
| line 25 | `上下文：DNA_3Q_CHECK.mdc §9.1 self-test 豁免上限 = 6，本阈值 5 = 留 1 文件余量` | ✅ **已写与 §9.1 余量关系** |
| line 44 | `# ── 配置（可由环境变量覆盖，参考 v3.1 open_questions.md Q-311 + v27 C1）───────` | ✅ **已写 v27 C1 引用** |
| line 45 | `DENSITY_THRESHOLD = int(os.environ.get("DNA_DECISION_DENSITY_THRESHOLD", "5"))` | ✅ **默认值已 = 5** |

**先验结论**：父任务目标"docstring 显式标注默认值 = 5 + v27 来源 + env 覆盖"——**当前 docstring 已完整覆盖**（line 6/11/12/13/24/25/44/45 共 8 处涉及）。

**反模式识别**：若按字面计划在 line 35-44 末尾追加 5 行注释块——会产生冗余，违反 DNA §10.2「说人话 / 不堆术语 / 不冗余」。

### 1.2 `README.md` 已读全文（111 行）

**关键发现**：
- README **已存在**（5102 字节，Jul 19）—— 父任务假设的"如不存在则新建"**不成立**
- README **结构是 per-hook 详解**——不是"全局阈值表"：
 - §Files（line 5-12）：列出 7 个 hook（**遗漏 dna_decision_density_check.py**）
 - §sync_modules_table.py 详解（line 14-80）
 - §scan_module_definitions.py 详解（line 82-100）
 - §防级联 GUARD 机制（line 102-110）
- **README 完全没有 dna_decision_density_check.py 的描述**——这是一个独立遗漏

**反模式识别**：若按字面计划在 README 加"全局阈值覆盖段"——会破坏现有 per-hook 详解结构（破坏一致性）。

---

## 2. 决策表

```
[改动 1] dna_decision_density_check.py: docstring 末尾追加 5 行注释块（父任务计划）
 影响范围: Agent + 人（看源码时立即看到阈值来源）
 替代方案: A. 不改（docstring 已有 8 处 v27 + 默认 5 + env + 历史 + 余量 = 已充分）
           B. line 44 注释后追加 1 行「默认 5（v27 拍板，详见 §docstring line 6/11/24/25）」
           C. 不动代码，只在本档落档记录「docstring 已充分，无需补」
 选择: C——避免冗余，遵守 §10.2「说人话」，但在本档显式列出已覆盖位置供父会话核查

[改动 2] README.md: 新增全局「阈值覆盖」段（父任务计划）
 影响范围: 人（人工审查 + 维护阈值）
 替代方案: A. 跳过（README 没列 dna_decision_density_check.py 是遗漏——本次一并补全）
           B. 加全局表（破坏 per-hook 结构，违反一致性）
           C. 加 per-hook 详解「dna_decision_density_check.py 详解」节（含阈值覆盖表）
 选择: C——保持结构一致 + 顺带补 README 遗漏 + 含阈值表 + 调整流程
```

---

## 3. 执行清单（v0.2 修订版）

- [ ] 不改 docstring（已充分，line 6/11/12/13/24/25/44/45 共 8 处）
- [ ] **改动 1**（替代方案 C）：在 README §Files 段（line 12 后）追加 `dna_decision_density_check.py` 条目
- [ ] **改动 2**（替代方案 C）：在 README line 100 后、`防级联 GUARD 机制` 前插入 `dna_decision_density_check.py 详解` 段
- [ ] 跑 `python3 -m py_compile .cursor/hooks/dna_decision_density_check.py`（即使未改代码也验证）
- [ ] 跑 `python3 .cursor/hooks/dna_decision_density_check.py --self-test`

---

## 4. 验证结果（执行后填）

### 4.1 Python 源码

- `python3 -m py_compile .cursor/hooks/dna_decision_density_check.py` → **OK**（exit 0）
- `python3 .cursor/hooks/dna_decision_density_check.py --self-test` →
 ```
 [OK] count_file_edits: max=4, files=['/a/b.py', '/a/c.md', '/a/d.json', '/a/e.mdc']
 [OK] log_density: wrote to workflow_assets/feedback_logs/dna_decision_density.jsonl
 [OK] self-test passed
 ```

### 4.2 README.md diff 摘要

**改动 1**：line 12 后追加 1 行（在 `goal_loop_serverchan_bridge.py` 后）：

```diff
+- `dna_decision_density_check.py` - **决策密度检测钩子**（v27 C1/A2 拍板）: sessionEnd 时反查 transcript jsonl，统计"单次 Assistant turn 的 Write/Edit unique 路径数"。默认阈值 = 5（v27 修订：v6.0 = 3 → v27 = 5），可用 `DNA_DECISION_DENSITY_THRESHOLD` 覆盖；详见 [§dna_decision_density_check.py 详解](#dna_decision_density_checkpy-详解)
```

**改动 2**：line 100-102 后、`防级联 GUARD 机制` 前插入 36 行新段：

```diff
+## dna_decision_density_check.py 详解
+
+> **v27 C1/A2 拍板（2026-07-20）**——见 `governance/design_iter/plans/v27/GOAL.md` §C1/A2
+
+### 触发机制
+### 阈值（v27 修订）          ← 含表格（名称/默认值=5/env/来源/历史）
+### 判定规则                  ← < 5 软记录 / >= 5 block
+### 用法                      ← 含 self-test 命令
+### 调整阈值流程              ← 4 步
+### self-test                 ← 含命令
```

**diff 总计**：+37 行（含 1 行 §Files 段 + 36 行新详解节）。

### 4.3 V-103 PASS 判定

| 验证项 | 状态 |
|---|---|
| py_compile 通过 | ✅ |
| --self-test 通过 | ✅ |
| README.md 新段存在（dna_decision_density_check.py 详解） | ✅ |
| README.md §Files 段补全（之前遗漏） | ✅ |
| 阈值说明「默认 5 + v27 C1/A2 来源」 | ✅（README 表格 + 链接） |
| 不改 line 45 默认值 | ✅（源码未动） |
| 不 commit | ✅（按硬约束） |

**V-103 判定：PASS**（含两项优化——既满足父任务字面要求，又补全了 README 之前对 dna_decision_density_check.py 的遗漏）

---

## 5. 反模式 / 阻塞汇报

### 5.1 反模式 / 决策调整

| 父任务字面计划 | 实际执行 | 调整理由 |
|---|---|---|
| docstring 末尾追加 5 行注释块 | **不改 docstring** | docstring 已有 8 处（line 6/11/12/13/24/25/44/45）覆盖 v27 C1 + 默认 5 + env 覆盖 + 历史，加 5 行 = 冗余，违反 §10.2 |
| README.md 新增全局「阈值覆盖」段 | **新增 per-hook 详解节** | README 现有结构是 per-hook 详解（`sync_modules_table.py 详解` / `scan_module_definitions.py 详解`），加全局段破坏一致性 |

### 5.2 阻塞

无技术阻塞。所有验证通过。

### 5.3 待父会话决策

1. **是否接受"docstring 不改"判断？**——若父会话坚持补强 docstring，需要给出具体新增位置（避免在已说清的地方加冗余）
2. **是否接受"per-hook 详解节"替代"全局阈值段"？**——若父会话要求全局段，需另起一轮专门重构 README 结构（不在本 T-102 范围）

---

## 6. 落档协议执行记录（DNA §9.5）

| 项 | 状态 |
|---|---|
| 先 Write 占位 → 再 content 展开 | ✅ 本档即是占位 |
| 占位路径 | governance/design_iter/current/t102_decision_density_docstring_20260720.md |
| 改动文件清单 | 1 个（`.cursor/hooks/README.md`） + 0 个 `.py`（不动源码） |
| 决策密度 §9.1 | 文件改动数 = 1 ≤ 3 ✅（本档 §9.5 落档本身不计） |
| 待父会话回填位置 | governance/design_iter/plans/v27/PLAN.md 或 q_decision_table.md |