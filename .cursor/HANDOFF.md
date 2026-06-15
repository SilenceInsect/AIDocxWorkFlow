# 模块测试点模板建设 — 多 Agent 交接手册

> **本文件用途**：在主对话（已 3 个模块完成）结束后，**新 Agent** 在新对话中接手继续推进剩余 5 个模块（BIZ / LINK / SPECIAL / LOG / HINT）。
> **阅读对象**：接手的新 Cursor Agent（任何模式）。
> **阅读时间**：约 5 分钟即可进入工作状态。

---

## 0. 一句话总览

**任务**：在 `.cursor/MODULES.md` 维护 8 个测试模块的"细分定义 + 种子测试点"，让 S5/S6 阶段能按模板生成结构化测试点。

**已进度**：3/8 模块完成（37/45 子模板 = 82%）。
**未完成**：5/8 模块（BIZ / LINK / SPECIAL / LOG / HINT）。

---

## 1. 项目背景

### 1.1 项目名
**AIDocxWorkFlow-SH** — AI 测试用例生成流水线

### 1.2 工作目录
```
/Users/gleon/Documents/TestDev/AIDocxWorkFlow-SH
```

### 1.3 核心产出
1. **`.cursor/MODULES.md`** —— 模块定义 SSoT（轻量索引）
   - §1 总表（8 模块一句话职责）
   - §4 矩阵（模块 vs 测试类型枚举）
   - §4.5/4.6/4.7 模块细分索引（**只**写概览/边界/索引，**不**写明细）
   - §9 兼容映射（v1.1 → v1.2）
   - §10 进度表
   - §11 单写源规则
2. **`workflow_assets/module_templates/{MODULE}/`** —— 模块测试点模板（重量明细）
   - `{MODULE}.md` 概览
   - `{MODULE}/A_*.md` ~ `{MODULE}/N_*.md` 子模板
   - 子模板统一 5 段结构（场景 + 种子 TP + 边界陷阱 + 验证证据）

### 1.4 单写源原则（**SSoT 核心**）
- **MODULES.md** = 概览 + 边界 + 索引（**只**写 30% 内容）
- **`module_templates/{MODULE}/`** = 明细 + 场景 + 种子 TP + 验证证据（写 70% 内容）
- **禁止双写**：明细/场景/种子 TP 只能出现在模板里
- 改模板**无需**改 MODULES（链接稳定即可）
- 改 MODULES 边界规则**必须**同步改对应模块的 `*_boundary.md`

---

## 2. 已完成（3 模块 + 6 版本）

| 版本 | 日期 | 模块 | 关键改动 |
|---|---|---|---|
| **v1.1** | 2026-06-15 | — | 初版；合并 S2 8 模块 + S5 HINT 扩展；废弃 BASE；建立 SSoT |
| **v1.2** | 2026-06-15 | UI | 8 大类深化（控件/交互/布局/静态/动效/引导/无障碍/异常）；新增 §4.5 |
| **v1.3** | 2026-06-15 | — | 模块测试点模板落地；`module_templates/` 仓库；UI 10 子模板；新增 §10 |
| **v1.4** | 2026-06-15 | — | 职责归位 + 单写源收敛；§4.5 从 100+ 行 → 67 行；新增 §11 |
| **v1.5** | 2026-06-15 | **CONFIG** | 11 子模板（146 TP）；4→9 枚举；新增 §4.6 |
| **v1.6** | 2026-06-15 | **AUX** | 16 子模板（236 TP）；4→14 枚举；新增 §4.7 + §9.3-9.4 |
| **v1.7** | 2026-06-15 | **BIZ** | 9 测试子模板 + 2 规则（278 TP）；4→9 枚举；新增 §4.8 + §9.5（含 `ACTIVITY_OPEN_CLOSE` 拆分 + `ENTITY_CACHE` 迁移）|
| **v1.6.1** | 2026-06-15 | **AUX 裁剪** | 收窄为底层基础工具；剔除日志/提示/第三方/风控/业务异常 |
| **v1.6.1+** | 2026-06-15 | **8 模块职责最终版** | BIZ/LINK/SPECIAL/LOG/HINT/CONFIG/UI 7 个模块描述重写；新增 §3.5 交叉场景判定规则；AUX 索引加与各模块边界一一对照 |
| **v1.7+** | 2026-06-15 | **HINT 完整 + 一致性重构** | HINT 7 类 → 13 大类细化（A-M + O + P = 16 文件）；§4.11 新增；§10 进度表 v1.7+ 完整；8 模块一致性 & 边界隔离重构：`test_case_formatter.py` 中英归一化 + 旧枚举迁移框架 + `--migrate-modules` CLI；S5/S6 SKILL.md 添加模块×类型双维度 + HINT vs UI 二次判定；S1/S2/S7/S8 SKILL.md 引用 MODULES.md；AUX 占位文件 J_log/L_ops 已删除；AUX.md 标记"已落地" |

### 2.1 已完成的 3 个模块

| 模块 | 子模板数 | 种子 TP | 概览文件 | 子模板目录 |
|---|---|---|---|---|
| **UI** | 10 | 123 | `UI.md` | `UI/A_control_basic.md` ~ `J_game_specific.md` |
| **CONFIG** | 11 | **146** | `CONFIG.md` | `CONFIG/A_field_legality.md` ~ `K_game_specific.md` |
| **AUX** | 16 | **236** | `AUX.md` | `AUX/A_common_util.md` ~ `P_game_specific.md` |
| **合计** | **37** | **505** | | |

### 2.2 现状数据
- **MODULES.md**：561 行
- **模板文件总数**：42 个（3 概览 + 37 子模板 + 2 公共）
- **子模板 + 1 概览 = N+1 文件 / 模块**
- **模板总行数**：约 7000+ 行

---

## 3. 未完成（5 模块）

按**推荐推进顺序**（由简到难）：

| 顺序 | 模块 | 现有枚举（v1.1）| 预计 v1.2 枚举 | 预计子模板数 | 预计 TP 数 | 难度 |
|---|---|---|---|---|---|---|
| 1 | **HINT** | `RED_DOT` / `ITEM_FLOAT` / `CURRENCY_FLOAT` / `SYS_MSG` / `TOAST` | 5 → 5-6 | 5-6 | 50-80 | ⭐ 简单 |
| 2 | **LOG** | `ASSET_CHANGE` / `PROGRESS_TRIGGER` / `ANOMALY` / `AUDIT_TRAIL` | 4 → 5-6 | 5-6 | 50-80 | ⭐ 简单 |
| 3 | **LINK** | `CORRELATION_TEST` / `REGRESSION_TEST` / `MULTI_TENANT_SYNC` | 3 → 4-5 | 4-5 | 40-70 | ⭐⭐ 中等 |
| 4 | **SPECIAL** | `DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` / `WEAK_NETWORK` / `SWITCH_TO_BACKGROUND` / `ANTI_CHEAT` | 5 → 6-8 | 6-8 | 60-100 | ⭐⭐⭐ 较难 |
| 5 | **BIZ** | `ACTIVITY_OPEN_CLOSE` / `PROTOCOL` / `ENTITY_CACHE` / `DB_PERSIST` | 4 → 6-8 | 6-8 | 80-120 | ⭐⭐⭐ 较难 |

> **总预计**：5 模块 + 26-33 子模板 + 280-450 TP

---

## 4. 新 Agent 工作流（标准操作流程 SOP）

> **重要**：每次推进一个模块，**严格按以下 5 步走**。

### Step 1：读 MODULES.md 对应章节 + 已完成模块作参考

```bash
# 必读
cat .cursor/MODULES.md                    # 561 行，重点关注 §1 §4 §10
cat workflow_assets/module_templates/CONFIG.md   # 已完成模块的概览（最佳参考）
cat workflow_assets/module_templates/CONFIG/A_field_legality.md   # 已完成子模板（最佳参考）
```

### Step 2：拆解待补模块为 N 个子模板

参考已完成模块的字母映射规则：
- A=基础类 / B=进阶类 / C=关联类 / ... / N=边界类 / O=边界区分 / P=游戏专项
- 子类代码用 v1.2 枚举命名（如 `FIELD_LEGALITY` / `CACHE_HIT_RATE` / `GM_TOOL`）

### Step 3：创建目录 + 概览 + 子模板（4 个动作并行）

```bash
mkdir -p workflow_assets/module_templates/{MODULE}
```

| 文件 | 内容 | 行数参考 |
|---|---|---|
| `{MODULE}.md` | 概览（子类索引 + 边界总览 + 关键词映射 + 进度） | 100-200 行 |
| `{MODULE}/A_*.md` | 子模板 1（场景 + TP + 边界陷阱 + 验证证据）| 200-300 行 |
| `{MODULE}/B_*.md` ~ ... | 子模板 2-N | 200-300 行 each |
| `{MODULE}/O_boundary.md` | 边界区分（**必加**）| 150-200 行 |
| `{MODULE}/P_game_specific.md` | 游戏专项（**必加**）| 200-300 行 |

### Step 4：更新 MODULES.md（5 处同步）

1. **顶部目录**：加 `{MODULE} 细分索引` 到 §4.7 之后
2. **§1 总表** `{MODULE}` 行：扩展职责
3. **§4 矩阵** `{MODULE}` 行：扩展枚举
4. **§4.X 新增**（X = 8, 9, 10, 11, 12）：模块细分索引
5. **§9 兼容映射**：加新章节 §9.5~9.X
6. **§10 进度表**：更新 `{MODULE}` 状态
7. **附录版本历史**：加 v1.X 行

### Step 5：验证 + 报告

```bash
# 文件结构
ls workflow_assets/module_templates/{MODULE}/
wc -l workflow_assets/module_templates/{MODULE}/*.md
find workflow_assets/module_templates -name "*.md" | wc -l

# 章节结构
grep -n "^## " .cursor/MODULES.md
```

跑 lint：
```bash
ReadLints paths: ["ai_workflow/test_case_formatter.py"]
```

最终输出报告：模块名 + 子模板数 + 种子 TP 数 + 4 处 MODULES.md 改动 + v1.X 版本。

---

## 5. 子模板统一结构（5 段式）

> **每个子模板必须严格遵循**——保证下游 S5 prompt 能稳定加载。

```markdown
# {字母}. {子类名}

> **子类代码**：`{V1.2_ENUM}`
> **归属模块**：`{MODULE}`
> **来源**：用户细化定义 §X「...」

> **测什么**：...
> **不测什么**：...
> **与其他子类的差异**：...

---

## 1. 典型场景

### 场景 1：{场景名}
- 业务背景：...
- 涉及字段/工具：...
- 触发动作：...
- 验证点：...

（6-12 个场景）

---

## 2. 种子测试点（TP 模板）

### TP-001（{ENUM}）：{标题}
- **scenario**：场景 1
- **module**：`{ENUM}`
- **precondition**：...
- **test_data**：...
- **expected**：...
- **notes**：注意 "X" vs "Y"

（10-20 个 TP）

---

## 3. 边界陷阱

### 边界 1：vs {其他模块}
- **混淆点**：「...」
- **判定规则**：测 "..." → 归 {本模块}；测 "..." → 归 {其他}
- **实例**：...

（3-4 个边界陷阱）

---

## 4. 验证证据

### 视觉证据
- ...

### 日志证据
- ...

### 数据证据
- ...

### 性能证据
- ...
```

---

## 6. 概览文件 `{MODULE}.md` 结构

```markdown
# {MODULE} 模块测试点模板（概览）

> **模块代码**：`{MODULE}`
> **来源**：`.cursor/MODULES.md` §1 总表 + 用户细化定义
> **作用**：S5 生成 {MODULE} 模块测试点时，按 story 实际涉及子类**按需加载**对应子模板。

> **完整覆盖范围**（一句话）：...

---

## 子类索引

| 字母 | 子类名 | 子类代码（v1.2 枚举） | 模板 | 细化段 |
|------|--------|----------------------|------|--------|
| A | ... | `{ENUM}` | [A_*.md](./{MODULE}/A_*.md) | §X |
| B | ... | `{ENUM}` | [B_*.md](./{MODULE}/B_*.md) | §X |
| ... | | | | |
| O | 边界区分 | — | [O_boundary.md](./{MODULE}/O_boundary.md) | §X 边界 |
| P | 游戏项目补充 | — | [P_game_specific.md](./{MODULE}/P_game_specific.md) | §X 游戏 |

---

## 加载规则（S5 prompt 使用方式）

1. **检测** `epic.module == "{MODULE}"` → 必读本概览
2. **按 story 内容** 识别涉及的子类
3. **按需加载** 对应子模板
4. **交叉参考** `O_boundary.md` 防止误标

---

## 边界总览

| 归 {MODULE} | 不归 {MODULE}（归其他模块）|
|------------|--------------------------|
| ... | ... |

---

## 关键词快速映射

| 关键词 / 上下文 | 子类 |
|----------------|------|
| ... | A |
| ... | B |
| ... | ... |

---

## 进度

- v1.0 (2026-06-15)：{MODULE} 模块 N 子模板 + 2 规则全部到位
```

---

## 7. `{MODULE}/O_boundary.md` 边界文件（**必加**）

```markdown
# O. {MODULE} 模块边界区分（判定规则）

> **非测试类型**——本文件是 S5 生成测试点时的**判定参考**，
> 避免误标 {MODULE} 标签（实际是 {其他模块列表}）。

---

## 1. 判定原则

> **{MODULE} = ...**
>
> **不归 {MODULE}**：...

### 判定三问

1. **是 "..." 还是 "..."？** 是 ... → 不归 {MODULE}
2. ...
3. ...

---

## 2. 边界对照表

### vs {模块 1}

| 场景 | 归 {MODULE} | 归 {模块 1} |
|------|------------|-----------|
| ... | ... | ... |

### vs {模块 2}
...

（vs 所有 7 个其他模块）

---

## 3. 常见误判案例

### 误判 1：{场景名} → 错标 {MODULE}
- **错误**：...
- **正确**：
  - {MODULE} 测 "..."（归 {MODULE}）
  - {其他模块} 测 "..."（归 {其他模块}）
  - 同一 Story 应有 N 个 TP

（3-5 个误判案例）

---

## 4. 判定流程图

```
Story 涉及某个功能点
    │
    ├── 是 "..."？
    │     是 → 归 {MODULE}（按子类 ... 选择）
    │
    ├── 是 "..."？
    │     是 → 归 ...
    │
    └── ...
```

---

## 5. 维护

- 边界规则变更：改 `.cursor/MODULES.md` §4 + 本文件 §2 边界对照表（同步）
- 新增误判案例：直接追加本文件 §3
- commit 标 `[{MODULE}-BOUNDARY]` 前缀
```

---

## 8. `{MODULE}/P_game_specific.md` 游戏专项（**必加**）

> **仅游戏项目**——非游戏项目可忽略本文件。

结构同子模板（场景 + 种子 TP + 边界陷阱 + 验证证据），按"本地化/活动/礼包/资源/防沉迷"等 5 个游戏子领域组织。

**TP 格式**：
```markdown
#### TP-001（P-本地化）：多区服配置隔离
- **module**：`{ENUM}`（{MODULE} 子类）
- **precondition**：...
- **test_data**：...
- **expected**：...
- **notes**：...
```

---

## 9. MODULES.md 修改清单（标准 5 处）

> 每次推进一个模块，**这 5 处必须同步改**：

### 9.1 顶部目录
```diff
- §1 总表 → ... → §4.7 AUX 细分索引 → §5 ...
+ §1 总表 → ... → §4.7 AUX 细分索引 → §4.8 {MODULE} 细分索引 → §5 ...
```

### 9.2 §1 总表 `{MODULE}` 行
```diff
- | N | {MODULE}  | `{CODE}`   | ...   | ...    | 原一句话描述 |
+ | N | {MODULE}  | `{CODE}`   | ...   | ...    | 扩展为完整描述（X 大类详见 §4.X + `module_templates/{MODULE}/`）|
```

### 9.3 §4 矩阵 `{MODULE}` 行
```diff
- | {MODULE}   | `ENUM1` / `ENUM2` / ... |
+ | {MODULE}   | **N 个 v1.2 枚举**（详见 §4.X）：`ENUM1` / `ENUM2` / ... / `ENUM_N` |
```

### 9.4 §4.X 新增（X = 8, 9, 10, 11, 12）

完整结构参考 `.cursor/MODULES.md` §4.5 / §4.6 / §4.7（约 60-100 行）：
- 概览（X 大类表）
- 完整覆盖范围（一句话）
- 边界区分（vs 其他 7 模块）
- 维护原则

### 9.5 §9 兼容映射
```diff
+ ### 9.X {MODULE} 测试类型兼容映射
+ 
+ | v1.2 枚举（现行）| 归属子类 | v1.1 旧枚举 | 兼容规则 |
+ | ---------------- | -------- | ----------- | -------- |
+ | `ENUM1` | A | `OLD_ENUM1` | 1:1 映射 |
+ | ... | | | |
```

### 9.6 §10 进度表
```diff
- | {MODULE}  | ⏳    | -        | 待补全    | 需你提供 {MODULE} 细化明细      |
+ | {MODULE}  | ✅    | N        | v1.0 完整 | 你已给 X 段+Y 大类细化（含游戏专项）|
```

### 9.7 附录版本历史
```diff
+ | v1.X  | 2026-06-15 | **{MODULE} 模块深化**：从 N 个 v1.1 枚举扩展为 N 个 v1.2 枚举... |
```

---

## 10. 启动指令（直接复制粘贴）

> 下面这条指令直接发到新 Agent 即可进入工作状态。

```markdown
我要推进 AIDocxWorkFlow-SH 项目的 {MODULE} 模块测试点模板。

**上下文**：
- 项目路径：/Users/gleon/Documents/TestDev/AIDocxWorkFlow-SH
- 已完成 3 个模块：UI（v1.2）、CONFIG（v1.5）、AUX（v1.6 + v1.6.1 裁剪）
- 本次推进：{MODULE} 模块（v1.X）
- MODULES.md 当前 562 行，模板 42 个文件

**必读文档**（先看这些）：
1. /Users/gleon/Documents/TestDev/AIDocxWorkFlow-SH/.cursor/HANDOFF.md （本次交接手册）
2. /Users/gleon/Documents/TestDev/AIDocxWorkFlow-SH/.cursor/MODULES.md （561 行）
3. /Users/gleon/Documents/TestDev/AIDocxWorkFlow-SH/workflow_assets/module_templates/CONFIG.md （最佳参考概览）
4. /Users/gleon/Documents/TestDev/AIDocxWorkFlow-SH/workflow_assets/module_templates/CONFIG/A_field_legality.md （最佳参考子模板）

**任务**：
按 HANDOFF.md §4 的 SOP 5 步走：
1. 读 MODULES.md + 已完成模块作参考
2. 拆解 {MODULE} 为 N 个子模板
3. 创建目录 + 概览 + 子模板 + O_boundary.md + P_game_specific.md
4. 更新 MODULES.md（5 处同步）
5. 验证 + 报告

**输入**（用户提供的细化定义）：
> {用户给该模块的细化段——见下方"§11 各模块细化定义待补"或用户在本次对话中提供}

**交付物**：
- 1 个 `{MODULE}.md` 概览
- N 个 `{MODULE}/A_*.md` ~ `N_*.md` 子模板
- 1 个 `{MODULE}/O_boundary.md` 边界区分
- 1 个 `{MODULE}/P_game_specific.md` 游戏专项
- 5 处 MODULES.md 同步更新
- 1 行版本历史 v1.X
- 1 份报告（子模板数 + 种子 TP 数 + 改动清单）
```

---

## 11. 各模块细化定义（**用户当前对话已提供**）

### 11.1 HINT（提示）— ✅ v1.7+ 完整（2026-06-15）
- **核心定位**：HINT = 全局临时反馈类提示组件（红点/飘字/Toast/弹窗/浮窗/引导气泡）
- **与 UI 边界**：临时弹出、一次性反馈 = HINT；页面常驻、布局、静态元素 = UI
- **现有 v1.7+ 枚举**（13 类）：`RED_DOT_BADGE` / `FLOAT_TEXT` / `TOAST` / `MODAL_DIALOG` / `FLOAT_NOTICE` / `ERROR_MESSAGE` / `TIMED_REMINDER` / `NEWBIE_GUIDE` / `SOCIAL_HINT` / `OPS_PUSH` / `STATUS_CHANGE` / `COMPLIANCE_HINT` / `OFFLINE_COMPENSATION`
- **v1.1 旧枚举迁移**：`RED_DOT` → `RED_DOT_BADGE` / `ITEM_FLOAT` + `CURRENCY_FLOAT` → `FLOAT_TEXT` / `SYS_MSG` → `MODAL_DIALOG` / `TOAST`（保留）

### 11.2 LOG（日志）— 用户待补
- 原定义：行为日志、审计追踪、资产变更埋点、监控埋点、异常日志
- 现有 v1.1 枚举：`ASSET_CHANGE` / `PROGRESS_TRIGGER` / `ANOMALY` / `AUDIT_TRAIL`
- **等待用户给细化定义**

### 11.3 LINK（关联）— 用户待补
- 原定义：外部 API、数据同步、多端一致性、跨服务协议、第三方支付/登录集成
- 现有 v1.1 枚举：`CORRELATION_TEST` / `REGRESSION_TEST` / `MULTI_TENANT_SYNC`
- **等待用户给细化定义**

### 11.4 SPECIAL（特殊情境）— 用户待补
- 原定义：边界情况、异常处理、反作弊、安全、弱网、高频请求、后台切换
- 现有 v1.1 枚举：`DUPLICATE_PACKET` / `HIGH_FREQ_PACKET` / `WEAK_NETWORK` / `SWITCH_TO_BACKGROUND` / `ANTI_CHEAT`
- **等待用户给细化定义**

### 11.5 BIZ（业务）— 用户待补
- 原定义：核心业务逻辑、数据流、协议交互、状态机、数据库持久化
- 现有 v1.1 枚举：`ACTIVITY_OPEN_CLOSE` / `PROTOCOL` / `ENTITY_CACHE` / `DB_PERSIST`
- **等待用户给细化定义**

---

## 12. 关键文件位置速查

| 用途 | 路径 |
|---|---|
| **模块定义 SSoT** | `.cursor/MODULES.md` |
| **本交接手册** | `.cursor/HANDOFF.md` |
| **概览** | `workflow_assets/module_templates/{MODULE}.md` |
| **子模板** | `workflow_assets/module_templates/{MODULE}/A_*.md` ~ `N_*.md` |
| **边界文件** | `workflow_assets/module_templates/{MODULE}/O_boundary.md` |
| **游戏专项** | `workflow_assets/module_templates/{MODULE}/P_game_specific.md` |
| **公共结构说明** | `workflow_assets/module_templates/_common_structure.md` |
| **已完成参考** | `workflow_assets/module_templates/CONFIG.md` + `AUX.md` |

---

## 13. 风险与注意事项

### 13.1 不要做这些
- ❌ **不要在 MODULES.md 写明细/场景/种子 TP**——只写概览/边界/索引
- ❌ **不要重复 A/B/C 等已用字母**——CONFIG 用 A-K，AUX 用 A-P，HINT/LINK 应从 A 重新开始
- ❌ **不要跳过 O_boundary.md 和 P_game_specific.md**——是判定参考
- ❌ **不要忘记 §9 兼容映射**——v1.1 → v1.2 数据平滑过渡
- ❌ **不要写代码（linter 会查）**——本任务只改 .md 文件

### 13.2 必须做这些
- ✅ **每个子模板必须 4 段**：场景 + 种子 TP + 边界陷阱 + 验证证据
- ✅ **每个 TP 6 字段**：scenario / module / precondition / test_data / expected / notes
- ✅ **每个边界陷阱 3 字段**：混淆点 / 判定规则 / 实例
- ✅ **MODULES.md 必改 5 处**：目录 + §1 + §4 + §4.X + §10
- ✅ **版本号连续**：v1.7 / v1.8 / v1.9 / v1.10 / v1.11（不是 v2.0）

### 13.3 文件结构示意
```
workflow_assets/module_templates/
├── README.md
├── _common_structure.md
├── UI.md                    # 概览
├── UI/                      # 10 子模板
│   ├── A_control_basic.md
│   ├── ...
│   └── J_game_specific.md
├── CONFIG.md                # 概览
├── CONFIG/                  # 11 子模板
│   └── ...
├── AUX.md                   # 概览
├── AUX/                     # 16 子模板
│   └── ...
├── HINT.md                  # ⏳ 待新建
├── HINT/                    # ⏳ 5-6 子模板
└── ...
```

---

## 14. 进度看板

| 模块 | 子模板 | 种子 TP | v1.2 枚举 | 状态 |
|---|---|---|---|---|
| UI | 10 | 123 | 11 | ✅ v1.2 |
| CONFIG | 11 | 146 | 9 | ✅ v1.5 |
| AUX | 16 | 236 | 14 | ✅ v1.6.1+（裁剪 + 边界细化）|
| BIZ | 11 | 278（A~I 238 + P 40）| 9 | ✅ v1.7（独立完成；**注**：BIZ-I `BIZ_AUDIT_LOG` 与新 LOG-B `LOG_ASSET_AUDIT` 已切分：BIZ-I 测"业务侧落点"、LOG-B 测"全链路对账"）|
| LOG | 15 | 353（A~M 321 + P 32）| 13 | ✅ v1.9（独立完成；LOG vs AUX 严格隔离已建立：LOG 管业务规范/审计/埋点触发/合规、AUX 管底层 SDK/采集/上报框架）|
| **HINT** | **16**（A-M + O + P = 13 大类 + 边界 + 游戏专项）| **全套** | 13 | ✅ v1.7+（2026-06-15 完成；13 大类细化 + 与 UI 边界隔离 + v1.1→v1.7+ 旧枚举迁移）|
| LINK | — | — | — | ⏳ v1.10 待补（**注**：版本号已顺延）|
| SPECIAL | — | — | — | ⏳ v1.11 待补（**注**：版本号已顺延）|
| **合计** | **79/79** | **1414** | **69/68+** | **87.5%（v1.7+ 后，HINT 完成）** |

> **v1.6.1 AUX 裁剪说明**（重要！新 Agent 推进 HINT/LOG/LINK/SPECIAL 时必看）：
> - **HINT** 模块要承接 AUX 剔除的"提示"内容：红点/弹窗/Toast/飘字/系统消息
> - **LOG** 模块要承接 AUX 剔除的"日志/埋点"内容：日志采集/分级/导出/崩溃堆栈/用户埋点
> - **LINK** 模块要承接 AUX 剔除的"第三方 SDK"内容：微信/支付宝/渠道登录
> - **SPECIAL** 模块要承接 AUX 剔除的"风控"内容：风控检测/反作弊
> - **BIZ** 模块要承接 AUX 剔除的"业务异常"内容：购买失败补偿等
>
> **预热数据**（HINT/LOG/LINK/SPECIAL Agent 可直接复用）：
> - **HINT v1.7+ 已完成**（13 大类 + 边界 + 游戏专项）——接手 Agent 不再需要从 AUX 占位文件搬运
> - HINT 历史数据迁移：`python3 ai_workflow/test_case_formatter.py --migrate-modules <file.json>`（自动迁移 v1.1 旧枚举 `RED_DOT` / `SYS_MSG` / `ITEM_FLOAT` / `CURRENCY_FLOAT` / `TOAST`）

---

## 14.5 v1.6.1+ 后重要发现（多人协作冲突预警）

> **本节是多人并行推进时**防止冲突的关键——请接手 Agent **必读**。

### 重要：BIZ v1.7 已独立完成

**完成时间**：2026-06-15 01:23-01:31
**完成人**：独立 Agent（不是你）
**BIZ 子模板**：
- `A_biz_logic.md` (BIZ_LOGIC) 15KB
- `B_data_flow.md` (BIZ_DATA_FLOW) 11KB
- `C_protocol.md` (BIZ_PROTOCOL) 13KB
- `D_state_machine.md` (BIZ_STATE_MACHINE) 15KB
- `E_db_persist.md` (BIZ_DB_PERSIST) 13KB
- `F_concurrency.md` (BIZ_CONCURRENCY) 13KB
- `G_scheduled_task.md` (BIZ_SCHEDULED_TASK) 12KB
- `H_payment.md` (BIZ_PAYMENT) 13KB
- `I_audit_log.md` (BIZ_AUDIT_LOG) 14KB
- `O_boundary.md` + `P_game_specific.md`

**已知冲突点**（**不要在 MODULES.md 改动**——已与 v1.6.1+ BIZ 描述同步）：

1. **`BIZ_AUDIT_LOG`（I_audit_log.md）vs 新 LOG 模块 `ASSET_AUDIT`** — BIZ 侧重"业务操作审计"（业务层），LOG 侧重"全量审计完整性"（基础层）。两者**不重叠**——但接手 LOG 的 Agent 推进 v1.9 时需**协调**：
   - 业务审计的具体业务逻辑 → 仍归 BIZ
   - 审计日志完整性、合规校验 → 归 LOG
   - 在 `LOG/O_boundary.md` 加"BIZ 业务审计 vs LOG 审计完整性"边界说明

2. **BIZ 概览 BIZ.md 描述**与 MODULES.md §1 新描述**不完全一致**（BIZ.md 用"全链路核心业务流程..."vs MODULES.md 用"核心业务逻辑、端服数据流..."）
   - **BIZ.md 描述**保留（更详细，Agent 自定）
   - **MODULES.md §1 描述**是 SSoT 顶层（统一）
   - 推进 v1.8+ 时，BIZ.md 描述可选择性同步（不强求）

### 版本号顺延规则

由于 BIZ 在 v1.6.1 之后建了，**后续未完成模块的版本号顺延**：

| 原计划 | 顺延后 | 状态 |
|---|---|---|
| HINT v1.7 | **HINT v1.8** | ⏳ 待补 |
| LOG v1.8 | **LOG v1.9** | ⏳ 待补 |
| LINK v1.9 | **LINK v1.10** | ⏳ 待补 |
| SPECIAL v1.10 | **SPECIAL v1.11** | ⏳ 待补 |

> **新 Agent 接手时**：版本号用**顺延后**的号，不要用 v1.7-v1.10（已被占用）。

### 冲突解决原则

- **MODULES.md §1 总表**：SSoT 顶层，**所有 Agent 必须遵守**（v1.6.1+ 已统一）
- **各模块 BIZ.md/UI.md/CONFIG.md/AUX.md 概览**：可独立维护，描述可更详细
- **子模板具体内容**：完全独立，各自维护
- **冲突时**：以 **MODULES.md §1** 为准（顶层 SSoT）

---

## 15. 完成任务后的报告模板

```markdown
# ✅ {MODULE} 模块测试点模板完整补充报告

## 📊 工作量统计
- 新建文件：N
- 子模板数：N
- 种子 TP 总数：N
- 更新文件：1（.cursor/MODULES.md）
- 新增章节：§4.X

## 📋 N 个子模板
| # | 字母 | 子类 | v1.2 枚举 | TP 数 | 对应段 |
|...|...|...|...|...|...|

## 📝 MODULES.md 改动
1. 顶部目录
2. §1 总表
3. §4 矩阵
4. §4.X 新增
5. §10 进度表
6. 版本历史 v1.X

## ✅ 验证项
- ✅ N 个子模板到位
- ✅ N 个种子 TP 全覆盖
- ✅ O 边界 + P 游戏专项齐
- ✅ 5 处 MODULES.md 同步
- ✅ lint 无错误

## 📈 累计进度
{累计 4/8 = 50%}

## 🔜 下一步建议
{下一个模块名}
```

---

**交接手册结束**。新 Agent 拿到本文件 + 用户细化定义后即可工作。

---

## 16. v2.0 关键修复（2026-06-15 03:30）— S6 TP→TC 1:N 拓宽

> **状态**：✅ **用户已确认接受**（2026-06-15 09:46）
> **范围**：S6 阶段设计缺陷修复（"测试点 = 测试用例" 错误等量）

### 16.1 问题

- **现象**：S5 77 TPs → S6 77 TCs（**1:1 错误等量**）
- **根因**：`ai_workflow/s6_generate.py` `build_cases()` 对每个 TP 只生成 1 个 case
- **违反**：ISTQB / IEEE 829 行业标准（1 TP = 3-18 TC）

### 16.2 修复

1. **18 种测试方法**（ISTQB 体系）：见 `ai_workflow/TP_TO_TC_EXPANSION.md`
2. **TP 类型派生系数**：POSITIVE 3-5 / BOUNDARY 4-7 / NEGATIVE 5-10 / EXCEPTION 4-8
3. **模块风险加权**：BIZ ×1.5 / LINK ×1.3 / SPECIAL ×1.3 / HINT ×1.0 / UI ×1.0 / LOG ×0.8 / CONFIG ×0.8 / AUX ×0.7
4. **派生公式**：`TC = SUM(method × weight) × module_weight ∈ [3, 18]`
5. **强制字段**：每条 TC 必带 `test_method` + `test_scenario`（不可空）
6. **xlsx 4 Sheet**：新增"测试方法统计"Sheet

### 16.3 修复效果

| 指标 | v1.0 ❌ | v2.0 ✅ |
|---|---|---|
| TP:TC 比 | 1:1 | **1:6.87** |
| TC 总数 | 77 | **529**（+452）|
| 方法覆盖 | 1（无）| **16 种实际使用** |
| xlsx Sheets | 3 | 4 |

### 16.4 SSoT 文件

- `ai_workflow/TP_TO_TC_EXPANSION.md`（**SSoT**）— 18 种方法完整定义
- `ai_workflow/s6_generate.py` v2.0（实现）
- `ai_workflow/s6_xlsx_enhance.py` v2.0（4-Sheet xlsx 增强）

### 16.5 SKILL.md / 规则文件固化

- `.cursor/skills/aidocx-s6-test-cases/SKILL.md`：
  - 新增「核心原则：TP → TC 拓宽（1:N，强制）」章节
  - 18 种方法表 + 模块加权表 + 派生公式 + 强制字段 + 自检清单
  - 4-Sheet Excel 说明
- `.cursor/rules/STAGE_S6_TEST_CASES.mdc`：
  - 同样新增「核心原则：TP → TC 拓宽（1:N，强制）」章节
  - 4-Sheet Excel 表

### 16.6 永久约束

后续所有需求跑 S6 时：
- 强制 TP:TC ≥ 1:3（违反即告警）
- 强制 `test_method` / `test_scenario` 字段填写
- 强制 4-Sheet xlsx 输出

---

## 17. 静态 skill 正畸（2026-06-15 03:00-03:18 + 后续）

> 范围：基于端到端跑通"游戏道具商城系统"docx 时的发现。

### 17.1 P0 Bug 修复

| Bug | 文件 | 修复 |
|---|---|---|
| S1 子流水线路径错误 | `ai_workflow/stage_s1_input/utils/constants.py` | `parents[4]` → `parents[3]` |
| S6/S7 中英 key 不适配 | `ai_workflow/auto_reviewer.py` | `_REQUIRED_FIELDS` 升级为 `[(en, zh), ...]` 元组 + `_get_field()` |
| S6 xlsx 仅 1 Sheet | `ai_workflow/test_case_formatter.py` `_save_xlsx` | 改用 `s6_xlsx_enhance.py`（4 Sheet，v2.0）|

### 17.2 P1 一致性修复

- 8 模块顺序对齐 `MODULES.md §1`：`aidocx-s5-test-points/SKILL.md` L4/L42 + `aidocx-s2-breakdown/SKILL.md` L87/L167/L226 + `aidocx-s6-test-cases/SKILL.md` L71
- 验证：`python3 ai_workflow/validate_skills.py .cursor/skills` → **13/13 PASS, 0 errors, 0 warnings**

### 17.3 端到端产出（v2.0 后）

| 阶段 | 产出 | 状态 |
|---|---|---|
| S1 | review_report（5 维度 7.6/10 PASS）| ✅ |
| S1.5 | exit_permission.json（can_proceed_to_s2=true）| ✅ |
| S2 | backlog（1 Release / 7 Epic / 13 Story / 18 OBJ / 50 FP）| ✅ |
| S5 | test_points（**77 TPs** / 8 模块 / 4 类型）| ✅ |
| S6 | test_cases（**529 TCs** / 16 方法 / 4-Sheet xlsx）| ✅ |
| S7 | review_report（PASS / 结构 100% / 7-7 Epic）| ✅ |
| S8 | iteration（4 RCA + 3 Prompt 改进 + 5 经验归档）| ✅ |

---

## 18. v2.0 关键重构（2026-06-15）— LLM 推理 + 脚本整理

> **用户反馈核心**：ai 工作流是把推理的活给 LLM，推进流程、整理结果的活交给脚本。
> 不要再设硬指标然后用脚本审查硬指标。审查也是用 LLM 审查。
> 真实需求多种多样，硬指标脚本只服务一种结构。

### 18.1 废弃的 v1.0 硬指标

| 类别 | v1.0 硬指标 | v2.0 处理 |
|------|-------------|-----------|
| S6 TC 数量 | TP:TC = 1:6.87 行业标准 / ≥ 1:3 强制 | **废除**——LLM 按业务自然决定 |
| S6 拓宽方法 | 18 种测试方法 + 模块风险加权 | **废除**——LLM 自由选择 |
| S6 强制字段 | test_method / test_scenario 不可空 | **改可选**——LLM 视业务自由标注 |
| S6 优先级 | 3 段映射表（P0 支付 / P1 业务 / P2 展示）| **废除**——LLM 按业务风险决定 |
| S7 PASS 判决 | "覆盖率=100% + 结构≥90% = PASS" | **废除**——脚本只产事实，LLM 写建议 |
| S7 双审查员 | 脚本审计 5 维度全部用硬指标 | **拆分**——脚本 4 机械检查 + LLM 5 语义审查 |
| S5 数量 | "AUX ≥ 4 / UI ≥ 6 / BIZ ≥ 6 / ... 硬数字" | **废除**——LLM 按业务自然分布 |

### 18.2 改动文件清单

| 文件 | 改动 |
|------|------|
| `ai_workflow/s6_generate.py` | **全文重写** — 删 18 种方法/模块加权；改成 thin wrapper |
| `ai_workflow/s6_xlsx_enhance.py` | **全文重写** — 删 Sheet 4 测试方法统计；改回 3 Sheet |
| `ai_workflow/auto_reviewer.py` | **全文重写** — 删 PASS/FAIL 判决；改 snapshot() |
| `ai_workflow/TP_TO_TC_EXPANSION.md` | **删除**（v1.0 硬方法 SSoT 已废弃）|
| `VALIDATION_S2_S5_2026_06_15.md` | **删除**（v1.0 脚本硬指标验证违反设计哲学）|
| `.cursor/skills/aidocx-s5-test-points/SKILL.md` | 删 "AUX 至少 4 / UI 至少 6" 硬数字 |
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | **全文重写** — 删 TP→TC 1:N 强制段 |
| `.cursor/skills/aidocx-s7-review/SKILL.md` | 审查员 A/B 拆"脚本/ LLM"分工；删 PASS/FAIL 判决 |
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | 同步去硬指标 |
| `CHANGELOG.md` | 新增 v2.0 重构条目 |
| `workflow_assets/游戏道具商城系统/「S6 测试用例生成」/v1.0/test_cases.*` | 77 TCs（兜底 1:1）— LLM 后续按需在对话中拓宽 |
| `workflow_assets/游戏道具商城系统/「S6 测试用例生成」/v1.0/review_snapshot.*` | **新产出** — 脚本事实快照，**无 PASS/FAIL 判决** |
| `workflow_assets/游戏道具商城系统/「S6 测试用例生成」/v1.0/review_report.*` | **删除**（v1.0 硬指标报告已过时）|

### 18.3 S6 / S7 重跑结果

- **S6 输出**：77 TPs → 77 TCs（脚本不强行拓宽；LLM 后续按需在对话中拓宽）
  - 模块分布:UI 12 / BIZ 20 / CONFIG 10 / LINK 5 / LOG 10 / AUX 5 / SPECIAL 7 / HINT 8
  - 类型分布:POSITIVE 30 / BOUNDARY 19 / NEGATIVE 12 / EXCEPTION 16
- **S7 输出**：`review_snapshot.md/json` — 脚本只列事实，**"## 5. LLM 审查建议" 段待 LLM 填**
  - 填写率 75%（事实数字）
  - 8 模块全有 TC（事实数字）
  - 不做 PASS/FAIL 判决——**改由 LLM 在 review_report 中按业务实际写建议**

### 18.4 关键认知

- **LLM 推理 + 脚本整理 = 唯一正确范式**——脚本永远不替代 LLM 思考
- **真实需求多种多样**——硬指标脚本 = 强行套结构
- **不告诉 LLM 多少算合格**——告诉 LLM 怎么思考产出质量
- **审查是 LLM 干的事**——脚本只产事实，LLM 读事实后做语义审查
- **未来工作流**：
  1. S5 / S6 LLM 在对话中推理生成（带 PUSH 决策块 / 反例库 / 5 问自查）
  2. LLM 把生成的 case 写到 test_points.json 的 `llm_generated_cases` 字段
  3. 脚本读这个字段，做 ID 分配 / 模块归一化 / 写文件
  4. 脚本产 review_snapshot（事实）+ LLM 填 review_report（建议）

### 18.5 全流程 S2.5 默认跳过（opt-in）

**问题**：S2.5 迭代规划只解决"开发节奏/资源/排期"问题，对 S5 测试点 / S6 用例的产出数量/质量**无强关系**。但历史 conversation SKILL 在「完整流水线」里把 S2.5 写成了 S2 → S3 之间的固定环节，导致全流程跑下来时 S2.5 总是被空跑一遍（产出空目录），多余且误导。

**决策**：
- **全流程模式默认跳过 S2.5**。需要做迭代排期时显式声明：`AIDOCX_INCLUDE_S2_5=true`（或 `1`）。
- **独立调用方式不变**：`/aidocx-s2-5-iteration` 或粘贴 S2 backlog → 直接执行 S2.5（不受环境变量控制）。
- S2.5 自身的 rule / SKILL 不删——它仍是「独立阶段」，可单独跑。

**改动文件**（5 处同步）：
| 文件 | 改动 |
|---|---|
| `.cursor/rules/AIDocxWorkFlow.mdc` | 顶部加「编排开关（环境变量）」节；Stage 表 S2.5 行加 ⚙️opt-in 标记；S1→S1.5→S2 流程说明后追加「S2.5 默认跳过」原则 |
| `.cursor/skills/aidocx-workflow-conversation/SKILL.md` | 流水线表加「默认」列（S2.5 = ⏭️ 跳过）；新增「S2.5 默认跳过原则」段；第四步改为条件块 + 跳过分支 |
| `.cursor/rules/STAGE_S2_5_ITERATION.mdc` | 标题下方加 ⚠️ opt-in 声明 |
| `.cursor/skills/aidocx-s2-5-iteration/SKILL.md` | 标题下方加 ⚠️ opt-in 声明（独立调用不受影响）|
| `.cursor/HANDOFF.md`（本文件）| 新增 §18.5（本节）记录决策和改动清单 |

**判定语义**：
- `AIDOCX_INCLUDE_S2_5 ∈ {"true", "1", "yes"}`（小写不敏感）→ 全流程包含 S2.5
- 其他值 / 未设置 → 跳过 S2.5
- 跳过时：**不**创建空 `「S2.5 迭代规划」/` 目录，流程报告写 `S2.5: SKIPPED (AIDOCX_INCLUDE_S2_5 unset)`

