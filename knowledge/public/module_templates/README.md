# 模块测试点模板（Module Test Point Templates）

> 本目录是**项目级公共**的「模块测试点模板」仓库。
> 定义见 `.cursor/MODULES.md`（项目级唯一真相源）。
> **治理边界 / Git 策略 / 公共库 vs 项目级库格式差异 / 入库审核流** 统一见 `knowledge/README.md`。
> 若本文件与 `knowledge/README.md` 冲突，以 `knowledge/README.md` 为准。
>
> **作用**：作为 S5（测试点生成）阶段的**准入物料**，S5 prompt 在检测到 `epic.module == XXX` 时，
> **自动加载**对应模块的测试点模板，作为推理生成的"种子"和"标准"。

---

## 目录结构

```
module_templates/
  README.md                  ← 本文件
  _common_structure.md       ← 通用模板结构（5 段）
  UI.md                      ← UI 模块概览（聚合 A-J）
  UI/                        ← UI 子类（10 个）
    A_control_basic.md
    B_pure_interaction.md
    C_layout_adapt.md
    D_static_display.md
    E_animation.md
    F_guide_hint.md
    G_accessibility.md
    H_edge_ui.md
    I_boundary.md            ← UI 与 HINT/BIZ/UTIL 边界区分
    J_game_specific.md       ← 游戏专项
  BIZ.md + BIZ/              ← 业务（待补全）
  CONFIG.md + CONFIG/        ← 配置（待补全）
  UTIL.md + UTIL/              ← 辅助（v1.6.1 裁剪完成）
  LINK.md + LINK/            ← 关联（待补全）
  SPECIAL.md + SPECIAL/      ← 特殊情境（待补全）
  LOG.md + LOG/              ← 日志（待补全）
  HINT.md + HINT/            ← 提示（v1.7+ 完整）
```

---

## 模板通用结构（5 段）

每个子类模板都遵循 [`_common_structure.md`](./_common_structure.md) 的 5 段结构：

1. **子类定义**（1 段话讲清这个子类测什么）
2. **典型场景**（3-10 个常见业务场景清单）
3. **种子测试点**（TP 模板——按你给的细化明细**全覆盖**，每子类 1-N 个）
4. **边界陷阱**（与相邻模块的边界 / 常见误判）
5. **验证证据**（UI 截图 / log 关键词 / DB 查询 / 协议字段）

> 完整结构详见 [`_common_structure.md`](./_common_structure.md)

---

## 与 S5 的集成机制

### 触发：自动加载

S5 prompt 内置规则：

> 当 `backlog.json` 的 `epic.module == XXX` 时，**必须**调用：
> `Read .cursor/rules/../knowledge/public/module_templates/XXX.md`
> 作为该 epic 下所有 story 测试点生成的**推理种子**。

### 加载顺序

1. 先读 `_common_structure.md` 了解通用结构
2. 再读 `<MODULE>.md` 模块概览
3. 按 story 实际涉及的子类，**按需**读 `<MODULE>/<子模板>.md`

### 准入物料检查（S5 启动时）

S5 prompt 在生成前**先检查**：

| 物料 | 缺失时 |
|------|--------|
| `module_templates/<epic.module>.md` | **warning 但不阻断**（AI 退化为无模板推理）|
| `module_templates/<epic.module>/<subclass>.md` | **不阻断**（按需加载）|
| 模块名不在 8 模块总表 | **阻断** + 生成 `fail_report_S5.md` |

---

## 维护流程

### 触发来源

| 触发 | 动作 |
|------|------|
| **S8 自迭代**发现 `S5_MODULE` 根因缺陷 | 先写入 `knowledge/project_local/.review_queue/` 待人工审核，禁止直接补正式公共模板 |
| 新需求涉及未覆盖子类 | 参照 `_common_structure.md` 新建子类文件 |
| 业务边界变化导致现有子类不适用 | 在 `O_boundary.md` 中补充边界误判案例 |

### 新增/修改子类模板

1. 沿用 `_common_structure.md` 的 5 段结构
2. 文件名遵循 **字母顺序 + 下划线命名**（如 `C_layout_adapt.md`）
3. S8 经验补充：先产出待审候选，人工审核后再决定是否回写正式模板
4. 修改后**无需改 S5 prompt**（prompt 是按路径加载，与内容解耦）
5. commit 标 `[MODULES-TEMPLATE]` 前缀

### 经验补充格式（S8 候选专用）

在四段（子类定义 / 典型场景 / 种子 TP / 边界陷阱）中追加：

```markdown
> 经验补充（S8 <version>，缺陷 ID #<N>）
> 根因：<S5_MODULE>/<缺陷类型>
> 补充：<具体补充内容>
```

### 模板废弃

- 不主动删除；改名为 `_deprecated_<原名>.md` 保留 30 天
- 在 `_common_structure.md` 的废弃记录区登记

### 版本记录规范

在每个子类文件的底部追加（不在 README 中集中登记）：

```markdown
---
## 版本历史
- v<version> (<date>)：<变更说明>（来自 S8 自迭代 / 人工补全）
```

模块 README 进度表只记录"大版本里程碑"（模块从 0→1 补全），日常经验补充不更新 README。

---

## 进度

| 模块     | 概览 | 子类数 | 状态   | 备注                         |
| -------- | ---- | ------ | ------ | ---------------------------- |
| UI       | ✅    | 10     | v1.0   | 首发：10 子模板 + 1 概览 + 1 通用结构 |
| UTIL      | ✅    | 16（v1.6.1 裁剪后）| v1.6.1 | v1.6.1 裁剪：J/L 子类已迁出至 LOG/BIZ |
| HINT     | ✅    | 15（A-M + O + P）| v1.7+  | 13 大类细化 + 与 UI 边界隔离；2026-06-15 重构 |
| BIZ      | ⏳    | -      | 待补全 | 需提供 BIZ 细化明细         |
| CONFIG   | ⏳    | -      | 待补全 | 需提供 CONFIG 细化明细      |
| LINK     | ⏳    | -      | 待补全 | 需提供 LINK 细化明细        |
| SPECIAL  | ⏳    | -      | 待补全 | 需提供 SPECIAL 细化明细     |
| LOG      | ⏳    | -      | 待补全 | 需提供 LOG 细化明细         |

---

## 版本

- v1.0 (2026-06-15)：UI 模块首发（10 子模板 + 1 概览 + 1 通用结构）
- v1.6.1 (2026-06-15)：UTIL 模块 v1.6.1 裁剪（J/L 子类迁出，J_log_moved_to_LOG.md / L_ops_moved_to_BIZ.md 占位文件已删除）
- v1.7+ (2026-06-15)：HINT 模块完整（13 大类细化 + 边界隔离 + 历史数据迁移；见 CHANGELOG.md）
- 后续：每个模块补全后版本号 +0.1
