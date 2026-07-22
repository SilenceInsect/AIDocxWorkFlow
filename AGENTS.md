# AIDocxWorkFlow 项目铁律

> **本文件是项目根级入口——Cursor 启动会话自动加载，每次回答前必读。**
> **范围**：只写项目级原则；阶段细则放 `.mdc` / `SKILL.md` / `MODULES.md`。

## 最高准则（决策顺序 = 优先级）

1. **一致性优先** — 改之前先看是否让设计 / 约束 / 实现 / 测试 / 文档失配
2. **设计优先** — 先判断结构对不对，再判断能不能快做完
3. **全局考虑优先** — 不按"分锅"优化，按项目整体工程化质量；指标：可执行 / 可审查 / 可理解 / 可维护 / 可追溯
4. **人本可审查** — 输出给具体名词看、不堆术语、有执行清单、不凭空、不无根据

5. **辩证求真** — 遇到分歧不停留于"堆选项"，分四步走：

   a. **论题**：显式写出当前方案的"核心主张是什么"（≤1 句话）

   b. **反题**：追问"对立面成立的条件是什么"——不是反驳，而是找它的合理性边界

   c. **合题**：在反题边界内修正论题，形成新命题；明确保留什么、废除什么

   d. **验证**：用具体场景检验合题是否自洽；若仍存分歧，写入 `open_questions.md` 入下一轮，不强行收敛

   **反模式**：跳步（直接给 3 个选项却不写论题）、反题空转（反驳但找不到成立条件）、无验证合题

   **示例**：
   > 论题：identity card 应该装方法论知识
   > 反题：知识无法溯源时怎么办？
   > 合题：框架层放方法论（本身即来源），示例层显式标注 `示例：`，来源可疑的具体断言迁入 module_templates/
   > 验证：LINK 特色节是否还有未经标注的具体断言？

## 结构性反模式（违反任一 = 方案失败）

- ❌ 只补局部闭环，不审全局一致性
- ❌ 代码改了，`.mdc` / `SKILL.md` / 文档 / 测试不对齐
- ❌ 先动手再补设计——先修实现，后补论证
- ❌ 不告诉人影响范围——改 X 影响 Y/Z 却不显式说明

## Git 分类铁律（新增任何文件 / 目录前必判）

**判定优先级：过程录制 > 公共知识库**——所有 `*.jsonl`（目标反模式案例 / 反馈日志 / 阶段录制 / 录制类产物）**一律不入 git**，即使放在 `knowledge/public/` 下也不行；公共知识库仅收录 `.md` / `.json` / `.db` 等**可复用非录制类**资产。

四类边界：

| 资产类别 | 入 git | 落点 |
|---------|--------|------|
| **功能 / 测试 / 规则 / 公共知识**（`.py` / `.mdc` / `.md` / `.json` / `.db`）| ✅ | 默认 |
| **过程录制**（`*.jsonl` / `*.log` / 反馈日志 / 阶段上下文包 / 反模式录制）| ❌ | `.gitignore` 已覆盖（`*.jsonl` / `feedback_logs/` / `workflow_assets/**/stage_context.*`）|
| **项目级私有**（`knowledge/project_local/` / `resource/` / `workflow_assets/` / `governance/` / `CHANGELOG.md` / `.goal-log-db/`）| ❌ | `.gitignore` 已覆盖 |
| **本地构建 / 缓存产物**（`__pycache__/` / `.pytest_cache/` / `dist/` 等）| ❌ | `.gitignore` 已覆盖 |

> **重要**：`knowledge/public/module_templates/` 属公共知识库，新增 / 修改**不得由通用 Agent 直接入库**——先产候选，人工审核。
>
> **模块专家 Agent 已落地（v34 B1）**：8 业务模块（CONFIG / UI / BIZ / AUX / LINK / SPECIAL / LOG / HINT）各自的模块专家 skill 位于 `.cursor/skills/<module>-expert/SKILL.md`，对**自己模块**（`module_templates/<MY_MODULE>/` + `<MY_MODULE>.md`）可直接写正式库（仍需 PR 留痕 + commit 标注 `[<MODULE>-专家直写]`）；跨模块 / 公共文件（`_common_structure.md` / `_decision_tree.md` / `s2_output_template.md`）任何 Agent 都不得直写。
>
> 索引：`.cursor/skills/_module-experts/README.md`
> 详见 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §0.1.3（主体权限对照表 + 边界自检流程）。

## 方案迭代管理

> **`governance/` 是本地工作区（不入 Git），用于存放个人/临时方案草稿与归档。
> `.gitignore` 中 `governance/` 模式锚点是项目显式策略，**不要修改**让 governance 入库——它与 `workflow_assets/`、`feedback_logs/` 同属"过程资产"。
> 若需跨人协作：把已收敛的方案结论**提炼到 `.cursor/rules/*.mdc` 或 `MODULES.md`**，再随代码提交。

> **行号锚点铁律**：`AGENTS.md` / `*.mdc` 中引用 `.gitignore` 规则**只用模式文本**（如 `governance/`），**不用行号**——
> 行号会随 `.gitignore` 任意编辑漂移；模式文本是 `.gitignore` 文件本身的语义内容，肉眼可见可 grep。详见 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §0.1.1。

变更走 `governance/design_iter/plans/v{N}/`：每份方案必有 **解决 / 新增 / 遗留** 三栏；遗留问题直接喂入 v{N+1}，`open_questions.md` 不可缺。索引：`cat governance/design_iter/INDEX.json`。

## 关键引用

| 内容 | 路径 | 谁读 | 入库 |
|---|---|---|---|
| 8 模块 SSOT | `.cursor/MODULES.md` | Agent + 人 | ✅ |
| 跨阶段契约 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | Agent | ✅ |
| 9 阶段规则 | `.cursor/rules/STAGE_S*.mdc` | Agent | ✅ |
| 13 个 SKILL 入口 | `.cursor/skills/*/SKILL.md` | Agent | ✅ |
| 方案迭代（本地工作区） | `governance/design_iter/plans/` | 人 | ❌ `.gitignore` |
| 版本日志 | `CHANGELOG.md` | 人 | ✅ |

## 三阶段核心边界（SSOT）

> **唯一真相源（SSOT）**：三阶段边界在各阶段的 rule/SKILL 文件中具体定义，本节为索引引用。
> - S1 边界定义：`.cursor/rules/STAGE_S1_REVIEW.mdc` §阶段入口
> - S1.5 边界定义：`.cursor/rules/STAGE_S1.5 Clarification.mdc` §阶段定位
> - S2 边界定义：`.cursor/rules/STAGE_S2_BREAKDOWN.mdc` §阶段入口

> **本文件保持短小，只定义优先级和反模式，不展开实现细节。**
