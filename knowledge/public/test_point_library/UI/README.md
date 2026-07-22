# UI 模块 TP 库

> **TP 库位置**：`knowledge/public/test_point_library/UI/`
> **子模板来源**：`knowledge/public/module_templates/UI/`
> **v1.2 枚举数**：11（CONTROL_RENDER / CONTROL_STATE / CONTROL_BASE_FUNC / CONTROL_BOUNDARY / PURE_INTERACTION / LAYOUT_ADAPT / STATIC_DISPLAY / ANIMATION / GUIDE_HINT / ACCESSIBILITY / EDGE_UI）

---

## TP 库文件清单

| 字母 | 子类 | 子类代码 | TP 库文件 | 状态 |
|------|------|---------|----------|------|
| A | 控件基础 | `CONTROL_RENDER` / `CONTROL_STATE` / `CONTROL_BASE_FUNC` / `CONTROL_BOUNDARY` | [A_control_basic.md](./A_control_basic.md) | ⏳ 待补 |
| B | 纯前端交互 | `PURE_INTERACTION` | [B_pure_interaction.md](./B_pure_interaction.md) | ⏳ 待补 |
| C | 布局适配 | `LAYOUT_ADAPT` | [C_layout_adapt.md](./C_layout_adapt.md) | ⏳ 待补 |
| D | 静态展示 | `STATIC_DISPLAY` | [D_static_display.md](./D_static_display.md) | ⏳ 待补 |
| E | 动效动画 | `ANIMATION` | [E_animation.md](./E_animation.md) | ⏳ 待补 |
| F | 引导浮窗 | `GUIDE_HINT` | [F_guide_hint.md](./F_guide_hint.md) | ⏳ 待补 |
| G | 无障碍 | `ACCESSIBILITY` | [G_accessibility.md](./G_accessibility.md) | ⏳ 待补 |
| H | 异常场景 | `EDGE_UI` | [H_edge_ui.md](./H_edge_ui.md) | ⏳ 待补 |

---

## 数据契约

```json
{
  "id": "{StoryID}-TP-NNN",
  "module": "UI",
  "test_point_type": "POSITIVE | BOUNDARY | NEGATIVE | EXCEPTION",
  "title": "...",
  "precondition": "...",
  "test_input": "...",
  "expected_result": "...",
  "priority": "P0 | P1 | P2",
  "regression": true,
  "s4_reference": "R-{EpicID}-NN | s4_self_inferred"
}
```

> **UI vs HINT 边界**（误标高发区）：
> - UI 测"**样式/位置/动画/布局**"（**常驻** UI 元素）
> - HINT 测"**内容/触发/文案**"（**临时** 弹出元素）
> - 完整判定见 [`module_templates/HINT/O_boundary.md`](../../module_templates/HINT/O_boundary.md)

---

## 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引（待补 TP 模板）|
