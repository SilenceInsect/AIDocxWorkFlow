# AMRD 项目基本盘

> **本文件是 AMRD 项目级规则库的入口索引**。所有项目级 UI / BIZ / AUX / ... 规则都从本文件出发。

---

## 项目基本信息

| 字段 | 值 | 说明 |
|------|---|------|
| **project_code** | `AMRD` | 项目代号（唯一，跨模块一致）|
| **project_name** | AMRD 手游 | 项目正式名 |
| **business_type** | 手游（移动端原生）| 业务类型 |
| **platform** | [iOS, Android] | 平台清单 |
| **ui_owner** | (TBD) | UI 规则 owner |
| **biz_owner** | (TBD) | 业务规则 owner |
| **status** | `active` | active / archived |
| **created_at** | 2026-07-22 | 立项时间 |

---

## 项目特征（影响 UI 规则）

| 特征 | 影响 | 适用规则 |
|------|------|---------|
| **移动端 touch UI** | 无 hover / Tab 焦点 / Loading-on-button | 按钮 4 态（IDLE/PRESSED/DISABLED/ACTIONABLE）|
| **手游项目** | 强引导 / 高密度 / 强奖励驱动 | F_guide_hint 子类需细化 |
| **多皮肤/多语言** | 主题切换 / 多语言文案 | D_static_display 子类需细化 |
| **离线/弱网** | 网络不稳定常态 | H_edge_ui 子类需细化 |

---

## 模块规则入口（按 8 模块分）

| 模块 | 入口 | 状态 | 说明 |
|------|------|------|------|
| **UI** | [`ui/_rules.md`](./ui/_rules.md) | ✅ active | 按钮 4 态 override |
| BIZ | biz/_rules.md | 📋 TODO | 待立项 |
| AUX | aux/_rules.md | 📋 TODO | 待立项 |
| LINK | link/_rules.md | 📋 TODO | 待立项 |
| SPECIAL | special/_rules.md | 📋 TODO | 待立项 |
| LOG | log/_rules.md | 📋 TODO | 待立项 |
| HINT | hint/_rules.md | 📋 TODO | 待立项 |
| CONFIG | config/_rules.md | 📋 TODO | 待立项 |

---

## 决策记录

> 所有 override 与通用库的冲突判定都记录在 [`_decisions.md`](./_decisions.md)。

---

## 生命周期

| 阶段 | 状态 | 时间 |
|------|------|------|
| 1. 立项 | ✅ 完成 | 2026-07-22 |
| 2. 运行 | 🔄 进行中 | 2026-07-22 |
| 3. 结项 | 📋 待触发 | TBD |
| 4. 回灌 | 📋 待触发 | TBD |

---

**维护者**：ui-expert（首个项目级示例）+ AMRD 项目 owner（TBD）
**关联方案**：[v35 project_local_schema](../../../../../governance/design_iter/plans/v35/project_local_schema.md)