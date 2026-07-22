# HINT 模块 TP 库

> **TP 库位置**：`knowledge/public/test_point_library/HINT/`
> **子模板来源**：`knowledge/public/module_templates/HINT/`
> **v1.7 枚举数**：13（RED_DOT_BADGE / ITEM_FLOAT / CURRENCY_FLOAT / MODAL_DIALOG / TOAST / FLOAT_NOTIFY / TIMED_REMINDER / GUIDE_HIGHLIGHT / SOCIAL_PROMPT / OPS_PUSH_PROMPT / STATE_CHANGE_DIALOG / COMPLIANCE_PROMPT / OFFLINE_COMPENSATION）

---

## TP 库文件清单

| 字母 | 子类 | 子类代码 | TP 库文件 | 状态 |
|------|------|---------|----------|------|
| A | 红点/角标/数字 | `RED_DOT_BADGE` | [A_red_dot_badge.md](./A_red_dot_badge.md) | ⏳ 待补 |
| B | 资源飘字 | `ITEM_FLOAT` | [B_item_float.md](./B_item_float.md) | ⏳ 待补 |
| C | 战斗飘字 | `CURRENCY_FLOAT` | [C_currency_float.md](./C_currency_float.md) | ⏳ 待补 |
| D | 模态系统弹窗 | `MODAL_DIALOG` | [D_modal_dialog.md](./D_modal_dialog.md) | ⏳ 待补 |
| E | 轻量 Toast | `TOAST` | [E_toast.md](./E_toast.md) | ⏳ 待补 |
| F | 浮动通知/悬浮浮窗 | `FLOAT_NOTIFY` | [F_float_notify.md](./F_float_notify.md) | ⏳ 待补 |
| G | 限时提醒+错误文案 | `TIMED_REMINDER` | [G_timed_reminder.md](./G_timed_reminder.md) | ⏳ 待补 |
| H | 新手引导高亮 | `GUIDE_HIGHLIGHT` | [H_guide_highlight.md](./H_guide_highlight.md) | ⏳ 待补 |
| I | 聊天&社交提示 | `SOCIAL_PROMPT` | [I_social_prompt.md](./I_social_prompt.md) | ⏳ 待补 |
| J | 运营推送 | `OPS_PUSH_PROMPT` | [J_ops_push_prompt.md](./J_ops_push_prompt.md) | ⏳ 待补 |
| K | 状态变更 | `STATE_CHANGE_DIALOG` | [K_state_change_dialog.md](./K_state_change_dialog.md) | ⏳ 待补 |
| L | 风控合规 | `COMPLIANCE_PROMPT` | [L_compliance_prompt.md](./L_compliance_prompt.md) | ⏳ 待补 |
| M | 离线补偿 | `OFFLINE_COMPENSATION` | [M_offline_compensation.md](./M_offline_compensation.md) | ⏳ 待补 |

---

## HINT vs UI 关键边界隔离规则（**S5 误标高发区**）

> 核心判断原则：**临时弹出 = HINT；常驻 = UI**。

| 归 HINT（不归 UI）| 归 UI（不归 HINT）|
|-------------------|-------------------|
| 临时弹出、一次性反馈、全局浮动、操作后自动消失的提示组件 | 页面常驻控件、固定布局、页面内置按钮/输入框/分页 |
| 红点、飘字、Toast、弹窗、浮窗、引导气泡 | 静态展示、页面内置文字标签、页面内常驻数值显示 |
| 邮件未读数角标（**触发弹性的**）| 邮件页面固定列表/分页器/搜索框 |
| 战斗中暴击伤害飘字（**一次性浮现后消失**）| 战斗血条/角色模型/技能图标（**常驻渲染**）|
| 限时活动倒计时浮窗（**事件触发弹出**）| 活动页面常驻倒计时数字（**页面常驻**）|
| 升级弹窗、突破升星弹窗（**事件触发**）| 升级页面常驻控件（**页面常驻**）|

**HINT vs UI F.GUIDE_HINT 关键区分**：

| 维度 | HINT（内容）| UI F.GUIDE_HINT（样式）|
|------|------------|---------------------|
| 测什么 | 显示什么文字/数字/逻辑/触发 | 位置/大小/动画/时长/颜色/层级 |
| 例子 | Toast"购买成功"、飘字"+100" | Toast 顶部居中 2s、飘字淡入 0.5s |
| 归类依据 | 内容/触发/文案/业务规则 | UI 容器/样式/动画 |

> 完整判定流程图 + 8 个误判案例见 [`module_templates/HINT/O_boundary.md`](../../module_templates/HINT/O_boundary.md)。

---

## HINT 内部子类口诀（按事件驱动类型分类）

- **事件触发临时反馈**（D 弹窗 / E Toast / F 浮窗 / G 限时提醒 / H 引导 / I 社交 / J 运营 / K 状态 / L 合规 / M 补偿）：测"内容/触发/文案"
- **常驻浮动显示**（A 红点 / B 资源飘字 / C 战斗飘字）：测"显示/清除/数值"
- **强制 vs 非强制**：D / L 强制；E / F / H 非强制

---

## v1.6.1 旧枚举迁移

| v1.6.1 旧枚举 | v1.7 新枚举 | 兼容规则 |
|--------------|------------|----------|
| `RED_DOT` | `RED_DOT_BADGE` | 1:1 映射（语义升级"角标+数字"）|
| `ITEM_FLOAT` | `ITEM_FLOAT` | 1:1 映射（资源飘字）|
| `CURRENCY_FLOAT` | `CURRENCY_FLOAT` | 1:1 映射（战斗飘字）|
| `MODAL_DIALOG` | `MODAL_DIALOG` | 1:1 映射（弹窗）|
| `TOAST` | `TOAST` | 1:1 映射（轻量提示）|
| `FLOAT_NOTIFY` | `FLOAT_NOTIFY` | 1:1 映射（浮窗）|
| `SYS_MSG` | `MODAL_DIALOG` 或 `TOAST` | 按场景归类 |
| —（新增）| `GUIDE_HIGHLIGHT` | v1.7 新增 |
| —（新增）| `SOCIAL_PROMPT` | v1.7 新增 |
| —（新增）| `OPS_PUSH_PROMPT` | v1.7 新增 |
| —（新增）| `STATE_CHANGE_DIALOG` | v1.7 新增 |
| —（新增）| `COMPLIANCE_PROMPT` | v1.7 新增 |
| —（新增）| `OFFLINE_COMPENSATION` | v1.7 新增 |
| —（新增）| `TIMED_REMINDER` | v1.7 合并（限时提醒+错误文案）|

> 批量升级：`python3 ai_workflow/test_case_formatter.py --migrate-modules <test_points.json>`

---

## 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引（待补 TP 模板）|
