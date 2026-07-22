# UI 模块测试点模板（概览）

> **模块代码**：`UI`
> **来源**：`.cursor/MODULES.md` §4.5
> **作用**：S5 生成 UI 模块测试点时，按 story 实际涉及子类**按需加载**对应子模板。
>
> **完整覆盖范围**：UI 控件渲染与多状态校验、纯前端无接口交互、键盘/鼠标多操作、弹窗浮层联动、
> 页面布局/窗口/分辨率多端适配、页面静态资源与文案展示、动效转场动画、引导红点提示、
> 前端本地筛选排序、输入实时格式校验、空态/异常/加载占位页面、权限锁定控件样式、
> 多主题皮肤展示、控件焦点与无障碍适配。

---

## 子类索引

| 字母 | 子类名             | 子类代码                                  | 模板                                                                | 测试类型数 |
| ---- | ------------------ | ----------------------------------------- | ------------------------------------------------------------------- | ---------- |
| A    | 控件基础校验       | `CONTROL_RENDER` / `CONTROL_STATE` / `CONTROL_BASE_FUNC` / `CONTROL_BOUNDARY` | [A_control_basic.md](./UI/A_control_basic.md)                     | 4          |
| B    | 纯前端交互         | `PURE_INTERACTION`                        | [B_pure_interaction.md](./UI/B_pure_interaction.md)                  | 1（聚合 5 子项）|
| C    | 布局适配           | `LAYOUT_ADAPT`                            | [C_layout_adapt.md](./UI/C_layout_adapt.md)                          | 1（聚合 5 子项）|
| D    | 页面级静态展示     | `STATIC_DISPLAY`                          | [D_static_display.md](./UI/D_static_display.md)                      | 1（聚合 5 子项）|
| E    | 动效与动画         | `ANIMATION`                               | [E_animation.md](./UI/E_animation.md)                                | 1          |
| F    | 引导、浮窗、提示   | `GUIDE_HINT`                              | [F_guide_hint.md](./UI/F_guide_hint.md)                              | 1          |
| G    | 无障碍 / 基础体验  | `ACCESSIBILITY`                           | [G_accessibility.md](./UI/G_accessibility.md)                        | 1          |
| H    | 边界异常 UI 场景   | `EDGE_UI`                                 | [H_edge_ui.md](./UI/H_edge_ui.md)                                    | 1（聚合 3 子项）|
| I    | UI 模块边界区分    | —（非测试类型，是判定规则）              | [I_boundary.md](./UI/I_boundary.md)                                  | —          |
| J    | 游戏项目额外专属   | —（非测试类型，是游戏项目专项）          | [J_game_specific.md](./UI/J_game_specific.md)                        | —          |

> **结构说明**：
> - A 子类**已展开为 4 个独立枚举**（`CONTROL_RENDER/STATE/BASE_FUNC/BOUNDARY`），其他子类
>   多数为聚合（一个枚举值代表 1 个子模板）
> - I/J 是判定规则和专项补充，**不是测试类型**——S5 不直接生成 I/J 类型的 TP，
>   但用 I/J 作为"边界判定参考"避免误打标签

---

## 加载规则（S5 prompt 使用方式）

1. **检测** `epic.module == "UI"` → 必读本概览
2. **按 story 内容** 识别涉及的子类（如"按钮点击"→ 涉及 A 控件基础 + B 纯前端交互）
3. **按需加载** 对应子模板（`UI/A_*.md` `UI/B_*.md`）
4. **交叉参考** `UI/I_boundary.md` 防止误标 UI 标签（实际是 BIZ/HINT/UTIL）

---

## 边界总览（与 `.cursor/MODULES.md` §4.5 I 节一致）

| 归 UI                          | 不归 UI（归其他模块）              |
| ------------------------------ | ---------------------------------- |
| 只改页面视觉、前端本地逻辑     | 调接口、提交表单落库 → BIZ          |
| 不请求后端接口的本地状态变更   | 后端数据返回渲染 → BIZ / UTIL        |
| 纯前端本地筛选、排序、分页     | 付费弹窗拉起支付 → LINK            |
| 静态资源展示                   | 资源下载逻辑、缓存命中率 → UTIL     |
| 动效展示                       | 动效触发的数据变化、日志埋点 → LOG  |
| 提示的承载样式（红点图标等）   | 提示内容本身 → HINT                |

> 完整边界规则见 [`UI/I_boundary.md`](./UI/I_boundary.md)

---

## UI 触发 SOP

S5 prompt 在生成 UI 模块测试点时执行：

1. 读取本概览
2. 对每个 story，扫描其 `description` / `acceptance_criteria` 关键词
3. 关键词 → 子类映射（见下表）→ 加载对应子模板
4. 子模板的种子 TP + 真实 story 信息 → 推理生成

### 关键词快速映射

| 关键词                              | 子类       |
| ----------------------------------- | ---------- |
| 控件、按钮、输入框、列表、弹窗      | A 控件基础 |
| 单击、双击、拖拽、键盘、Tab、焦点   | B 纯前端交互 |
| 分辨率、窗口缩放、横竖版、DPI       | C 布局适配 |
| 图标、文案、多语言、皮肤、空页面    | D 静态展示 |
| 动画、转场、闪烁、加载动画          | E 动效     |
| 引导、红点、Toast、浮窗、新手       | F 引导     |
| 焦点指示器、色盲、对比度            | G 无障碍  |
| 超长、空列表、断网、权限锁定        | H 异常场景 |

---

## 进度

- v1.0 (2026-06-15)：UI 模块 10 子模板全部到位
