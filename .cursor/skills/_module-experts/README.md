# 8 模块专家 Skill 索引

> **本目录是项目内 8 个模块专家 skill 的统一索引。**
> 每个专家 = 1 个独立 skill，**绑定到 `knowledge/public/module_templates/<MODULE>/` 作为权威资产库**。
> 权威定义详见 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §0.1.3「主体权限对照表」。

---

## 8 个模块专家（一览）

| # | Skill 名 | 模块 | 中文 | 资产根 | 触发命令 |
|---|---------|------|------|--------|---------|
| 1 | `config-expert` | `CONFIG` | 配置 | `knowledge/public/module_templates/CONFIG/` | `/config-expert` |
| 2 | `ui-expert` | `UI` | 界面 | `knowledge/public/module_templates/UI/` | `/ui-expert` |
| 3 | `biz-expert` | `BIZ` | 业务 | `knowledge/public/module_templates/BIZ/` | `/biz-expert` |
| 4 | `UTIL-expert` | `UTIL` | 辅助 | `knowledge/public/module_templates/UTIL/` | `/UTIL-expert` |
| 5 | `link-expert` | `LINK` | 关联 | `knowledge/public/module_templates/LINK/` | `/link-expert` |
| 6 | `special-expert` | `SPECIAL` | 特殊情境 | `knowledge/public/module_templates/SPECIAL/` | `/special-expert` |
| 7 | `log-expert` | `LOG` | 日志 | `knowledge/public/module_templates/LOG/` | `/log-expert` |
| 8 | `hint-expert` | `HINT` | 提示 | `knowledge/public/module_templates/HINT/` | `/hint-expert` |

---

## 权限对照（精炼版）

> **完整对照表**见 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §0.1.3。

| 主体 | 我的模块 | 别人的模块 | 跨模块 | 公共文件 |
|------|---------|----------|--------|---------|
| **通用 Agent**（默认） | ❌ 仅候选 | ❌ 仅候选 | ❌ 仅候选 | ❌ 仅候选 |
| **`<X>-expert`** | ✅ **可直接写正式库** | ⚠️ 降级为通用 Agent | ⚠️ 降级为通用 Agent | ❌ 仅候选 |
| **人工** | ✅ 直写 | ✅ 直写 | ✅ 直写 | ✅ 直写 |

> **`<X>-expert`** = 8 个模块专家中**任意一个**（包括 X 不是当前模块的情形）。

---

## 资产库结构（每个专家都一样）

```
knowledge/public/module_templates/
├── _common_structure.md          ← 跨模块公共文件（任何 Agent 都不得直写）
├── _decision_tree.md             ← 跨模块公共文件（任何 Agent 都不得直写）
├── s2_output_template.md         ← 跨模块公共文件（任何 Agent 都不得直写）
├── CONFIG.md  UI.md  BIZ.md ...  ← 模块概览（**写权限归对应模块专家**）
├── CONFIG/                       ← config-expert 的资产根
├── UI/                           ← ui-expert 的资产根
├── BIZ/                          ← biz-expert 的资产根
├── UTIL/                          ← UTIL-expert 的资产根
├── LINK/                         ← link-expert 的资产根
├── SPECIAL/                      ← special-expert 的资产根
├── LOG/                          ← log-expert 的资产根
└── HINT/                         ← hint-expert 的资产根
```

---

## 标准工作流（每个专家 5 步一致）

> **详见各专家 SKILL.md 的"标准工作流"章节。**

1. **身份自检**：我写的是不是 `knowledge/public/module_templates/<MY_MODULE>/` 或 `<MY_MODULE>.md`？
2. **读现状**：模块概览 + 要改的子模板 + MODULES.md 对应章节 + 边界文件
3. **判定改动范围**：新增子类 / 修订种子 TP / 边界规则 → 直接写；跨模块 → 降级
4. **写入**：正式库 commit message 标注 `[<MODULE>-专家直写]`；候选写入 `_candidates/`
5. **自检**：MODULES.md SSOT 同步 + 子类索引表同步 + 跨模块边界通知

---

## 协作 / 边界争议

| 场景 | 处理 |
|------|------|
| **两个专家对边界有争议** | 走候选 + 人工裁决，**不**互相改对方模板 |
| **新模块增加**（超出 8 模块） | 走 `.cursor/MODULES.md` §1 总表更新流程（**不是专家 skill 权限**） |
| **需要删一个专家 skill** | 走 §0.1.1 表 + AGENTS.md 反模式审查 — **不得私自删** |
| **专家 skill 升级/拆分** | 在本索引 `更新历史` 追加记录；走 commit message 标注 `[模块专家治理]` |

---

## 设计动机（v34 B1）

- **§0.1.3 早期**：「模块专家 Agent 当前未在 Cursor 工程层显式建模」——**这句话现在作废**
- **本目录落地**：8 个模块专家以 skill 形式存在，**每个 skill 文件即一个专家 agent 的"出生证 + 操作手册"**
- **Cursor 工程层建模**：通过 `disable-model-invocation: true` + `description` + `metadata` 字段，Cursor 主 agent 收到用户输入 `/<module>-expert` 时可加载本 skill（与 `aidocx-s6-test-cases/` 等平级）
- **未来工程升级路径**（待人工决定）：
  - ① 升级为独立 subagent_type（需要 Cursor 后续支持）
  - ② 增加 `permissions.json` 写入白名单（让 Cursor 工程层强制约束路径）
  - ③ 与 hooks 联动——`session_resume_multi_goal.py` 等 hook 可触发模块专家 skill 自动加载

---

## 更新历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v34 B1 | 2026-07-22 | 初版 — 8 个模块专家 skill 全部创建，与 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §0.1.3 + `.cursor/MODULES.md` §1 总表 1:1 对齐 |