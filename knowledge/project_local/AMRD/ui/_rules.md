# AMRD · UI 模块规则入口

> **本文件是 AMRD 项目级 UI 规则的入口索引**。S5 生成 TP 时**先读本文件**，再按需读 override 文档。

---

## 1. 通用基线（fallback）

若本文件未列出某子类的 override，则 fallback 到通用库：
- `knowledge/public/module_templates/UI/A_control_basic.md` ~ `J_game_specific.md`

## 2. 本项目 override 清单（**override 优先于通用**）

| 子类 | Override 文件 | 状态 | 说明 |
|------|-------------|------|------|
| **A_control_basic** | [`A_button_mobile_4state.md`](./A_button_mobile_4state.md) | ✅ active | 按钮从通用 8 态砍到 4 态（手游）|
| _excluded_states | [`_excluded_states.md`](./_excluded_states.md) | ✅ active | 显式排除的通用状态 + 理由 |

## 3. 未来待立项（与项目 owner 沟通）

| 子类 | 优先级 | 待补充 |
|------|-------|-------|
| C_layout_adapt（横竖屏 / 折叠屏）| P1 | AMRD 是否支持横屏？折叠屏适配？|
| D_static_display（多语言 / 多皮肤）| P1 | AMRD 支持哪些语言？皮肤切换如何实现？|
| E_animation（动效）| P2 | AMRD 动效节奏感（手游快 / 慢）|
| F_guide_hint（强引导）| P0 | 强奖励驱动下的引导设计 |
| G_accessibility（无障碍）| P2 | 是否需要无障碍适配？ |
| H_edge_ui（弱网 / 离线）| P0 | 手游弱网常态 |

## 4. override 冲突处理

若本项目 override 与通用库冲突：

1. **override 优先**（项目有最终解释权）
2. **记录冲突**到 [`../_decisions.md`](../_decisions.md)
3. **复盘时提议回灌**：若 override 被引用 ≥ 3 次，主动问"是不是该升格到通用库？"

## 5. 决策历史

| 日期 | 决策 | 理由 | 记录位置 |
|------|------|------|---------|
| 2026-07-22 | 按钮 4 态 override 通用 8 态 | 移动端无 hover / Tab 焦点 / 选中由 Radio 承载 / loading 用 skeleton | [`../_decisions.md`](../_decisions.md) #1 |

---

**维护者**：ui-expert（首个项目级示例）+ AMRD 项目 UI owner（TBD）
**基线引用**：[`module_templates/UI/`](../../../../public/module_templates/UI/)
**关联方案**：[v35 project_local_schema](../../../../../governance/design_iter/plans/v35/project_local_schema.md) §3