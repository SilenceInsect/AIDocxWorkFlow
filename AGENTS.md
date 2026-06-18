# AIDocxWorkFlow 项目铁律（项目 DNA）

> **本文件是项目根级入口——Cursor 启动会话自动加载，每次回答前必读。**
> **范围**：仅写"DNA 级"——具体规则在 `.mdc` / `SKILL.md` / `MODULES.md`。

---

## 最高准则

1. **人本可审查**（最高原则）
   - 任何方案 / 产出 / 回答，人能在 5 分钟内直接看懂
   - 反模式：术语堆砌 / 多层嵌套 / "技术正确但人难懂"
2. **约束 vs 知识 物理分离**
   - **约束**（Agent 必读）：`.mdc` / `SKILL.md` / `MODULES.md`
   - **知识**（人查阅）：`MODULES.md` 业务定义 + `.cursor/knowledge/` + `.cursor/design_iter/plans/`
   - 反模式：`alwaysApply: true` 滥用 → 把知识强读给 Agent
3. **每次回答前 3 问自检**（Agent 行为约束）
   - **Q1（人本可审查）**：人能不能直接看懂？
   - **Q2（必然好论证）**：方案有"为什么这个结构能避免再发生"的论证吗？
   - **Q3（约束 vs 知识）**：内容是"约束"还是"知识"？混在一起 = ❌

---

## 结构性反模式（违反任一 = 方案失败）

- ❌ **只给方案不论证**——"必然好"必须有"为什么"
- ❌ **不区分"给 Agent 读的"和"给人看的"**——alwaysApply 滥用
- ❌ **"先动手再补"**——先设计方案再讨论 → 漂移 → 重做
- ❌ **改动无影响范围**——不告诉人"改 X 影响 Y"

---

## 方案迭代管理

所有规则 / 结构 / 流程的方案变更走 `.cursor/design_iter/` 目录：

- 每份方案 v{N} 必有 **"解决 / 新增 / 遗留" 3 栏**
- 遗留问题直接喂入 v{N+1}——`open_questions.md` 不可缺
- 整份回滚：`python3 .cursor/design_iter/scripts/design_iter.py rollback v{N-1}`
- 详细：`cat .cursor/design_iter/INDEX.md`

---

## 关键引用

| 内容 | 路径 | 谁读 |
|---|---|---|
| 8 模块 SSOT | `.cursor/MODULES.md` | Agent（必读）+ 人（参考） |
| 跨阶段决策 + 行为约束 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | Agent |
| 9 阶段规范 | `.cursor/rules/STAGE_S*.mdc` | Agent |
| 12 个 SKILL 入口 | `.cursor/skills/*/SKILL.md` | Agent |
| **决策密度标准**（v3.1 新增） | `.cursor/rules/DNA_3Q_CHECK.mdc` §7 | Agent（必读） |
| **方案 v1（备份）** | `.cursor/design_iter/plans/v1/PLAN.md` | **人读**（v1 起点） |
| 方案遗留问题 | `.cursor/design_iter/plans/v1/open_questions.md` | **人读**（v2 输入） |
| 项目根铁律 | **`AGENTS.md`**（本文件） | **Agent 必读** |
| 版本日志 | `CHANGELOG.md` | 人读 |

---

> **本文件 ≤ 65 行**（v3.1 红线翻案 60→65；详见 [CHANGELOG.md](CHANGELOG.md) `[v3.1]`）——只写 DNA，不重复规则。规则细节看引用表。
