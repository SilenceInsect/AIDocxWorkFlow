# 根目录治理 + v7 启动版第二轮落地决策

> **触发**：用户 2026-07-09 00:10 "先去做其他治理项"
> **范围**：补完根目录治理 + v7 治理体系完整化 + git 状态同步
> **DNA 引用**：DESIGN_AND_EXECUTION_STANDARDS.mdc §0.1 + AGENTS.md "方案迭代管理"

---

## 1. 全量扫描结果（§9.4 先验后答）

| 序号 | 空缺项 | 现状 | 风险等级 |
|---|---|---|---|
| 1 | `current` 软链仍指向 v2 | `lrwxr-xr-x current -> plans/v2` | 中（治理层断裂）|
| 2 | `plans/v7/` 缺 4 件套 | `open_questions.md` / `resolved_questions.md` / `decisions.json` / `changes/` 全无 | 高（v7 体系不完整）|
| 3 | `ai_workflow/tools/__init__.py` 缺失 | `tools/` 是新子目录但不是 Python 包 | 低（功能未启用时无影响）|
| 4 | `INDEX.md` / `INDEX.json` 无 v7 记录 | governance 顶层索引未同步 | 中 |
| 5 | `git status` 有 5 个 `D` + 4 个 `??` | working tree 与 index 不一致 | 低（git 操作问题）|

---

## 2. 决策表（按 DNA §9.1 + §3 约束类必先 ask）

### 决策 A：current 软链切换

- **当前**：`current -> plans/v2`
- **选项**：
 - A1（推荐）：**不切 current**，等 v7/PLAN.md §"3 栏 + 治理 4 件套"全部就位再切（v2.1.1 实战教训：切 current 必须 4 件套齐全，否则 Agent 看 current/ 路径迷惑）
 - A2：立即切 current → v7（v7 体系未完整，**人/A 会迷惑**）
- **风险**：A2 会破坏治理层一致性——open_questions.md 还在 v2，但 v7/PLAN.md 已在 current/

### 决策 B：plans/v7/ 4 件套补全

- **缺失**：`open_questions.md` / `resolved_questions.md` / `decisions.json` / `changes/diff_v6_to_v7.md`
- **选项**：
 - B1（推荐）：**本轮先补 `open_questions.md` + `resolved_questions.md` + `decisions.json` 骨架**，**`changes/` 留 v7.1 启动时再建**（v7 主体答 Q-501~Q-569 时自然产出 changes/diff）
 - B2：4 件套全补 + 写完整内容（**超 §9.1 红线**——5 文件改动）
- **影响**：B1 = 3 文件，B2 = 5 文件（超出 3 文件红线 2）

### 决策 C：INDEX.md / INDEX.json 加 v7 记录

- **缺失**：governance 顶层 INDEX 未同步 v7
- **选项**：
 - C1（推荐）：本轮**先 Read INDEX.md + INDEX.json 现有结构**，按 v7/Q-501~Q-569 添加 v7 段
 - C2：留 v7.1 启动时再做（**延后，治理索引持续失同步**）

### 决策 D：ai_workflow/tools/__init__.py

- **缺失**：Python 包声明
- **选项**：
 - D1（推荐）：**写空 `__init__.py`**（最小声明）+ 文件顶部注释 `"""一次性工具脚本归档目录。当前包含：convert_md_to_docx.py（md → docx 转换，已被 stage_s1_input/MarkdownConverter 覆盖，保留为历史工具）。"""`
 - D2：写完整 __init__.py 含 `__all__` + `import convert_md_to_docx` 重导出（**过度工程**）

### 决策 E：git 状态同步

- **现状**：5 个 `D`（CHANGELOG_v2.0.bak / RELEASE_NOTES_v1.0_rerun.md / RULE_SKILL_CONSISTENCY_REVIEW.md / SCRIPT_SKILL_CLOSURE_REVIEW.md / SKILL_LOGIC_REVIEW.md / convert_md_to_docx.py / sample_requirements.md — 共 7 个）+ 4 个 `??`
- **选项**：
 - E1（推荐）：**git add -u**（自动同步 working tree 与 index）+ **git add 新文件**（4 个 untracked）
 - E2：手动 `git rm` 每个（**碎片化**）

---

## 3. 本轮动作清单（按 §9.1 红线 ≤ 3 文件改动）

> **本轮先做低风险实现类**：D + E + C（INDEX 同步）+ B1 子集
> **下轮做治理层强约束类**：A（切 current）+ B1 完整 4 件套

### 本轮 3 文件改动：

| N | 操作 | 文件 |
|---|---|---|
| 1 | Write `ai_workflow/tools/__init__.py` | 1 文件 |
| 2 | StrReplace INDEX.md + INDEX.json 加 v7 段（**2 个文件但同主题**——governance 索引同步）| 2 文件（INDEX.md + INDEX.json）|

**共 3 文件改动**——紧贴 §9.1 红线。

### 本轮不做的（待下轮拍板）：

- ❌ 切 current → v7（A，等 B 4 件套齐全再做）
- ❌ v7/PLAN.md 不补 4 件套（B，等下轮 ask）
- ❌ git add -u（E，留到所有改动落定后统一 commit）

### 下轮待拍板（实施前必 ask）：

- A 切 current → v7 的具体时点
- B 4 件套是否在本轮一起做
- E git add -u 是否本轮执行

---

## 4. 落档协议执行记录

- 2026-07-09 00:10：本决策表落档
- 后续：本表 v1 决策表（q_decision_table_q_audit_001.md）已删