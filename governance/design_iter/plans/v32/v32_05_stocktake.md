# v32_05 — TP 库首批回灌前置盘点（修正 R2 误判）

> **路由**: v32_05
> **日期**: 2026-07-21
> **依据**: `v32/PLAN.md` §3.5 + 用户 Round 3 prompt 修正 R2 误判
> **状态**: 前置盘点完成；Round 4 act 决策启动/推迟/待定

---

## 1. 目标

v32_05 是"TP 库首批回灌"治理项，从 v3.01 / 历史样本抽取可复用 TP 入 `knowledge/public/test_point_library/`。

**v31 §8.2 两段制归档链路**（`archive/v31_20260721_020714.bak/PLAN.md` §8）：

```
S8 识别 must_fix/should_fix 根因
    ↓
[第 1 段] 写入 knowledge/project_local/.review_queue/<Module>/<Subclass>__<defect_id>__<date>.md
    ↓
[人工审核] iteration.json#pending_candidates 触发 → 人工阅读候选 → 通过/拒绝
    ↓
[第 2 段] 通过 → 回写 knowledge/public/test_point_library/<MODULE>/<Subclass>.md
```

---

## 2. ⚠️ 关键修正（R2 误判解除）

`v32/PLAN.md` §3.5 + `v32/review_2.md` §3.3 都把 v32_05 列为"依赖 S7/S8 跑通"，**这是 R2 误判**。

**真实依赖关系**：

| 维度 | 真实依赖 |
|----|----|
| v32_05 抽取来源 | v3.01 S5/S6 产物（已存在）—— **不依赖 S7/S8 跑通** |
| v32_05 触发机制 | 人工审核机制（v31 §8.2 第 2 段）—— **依赖审核员，不依赖 S8 反馈链** |
| v32_05 与 S7/S8 关系 | S7/S8 跑通可触发更多候选（v31 §8.4 激活阈值 ≥ 10 条），但**不是 v32_05 启动的前置条件** |

**修正来源**：用户 Round 3 prompt 显式说明 — "v32_05 **不依赖 S7/S8 跑通**——它是 TP 单向回灌（v3.01 已跑通的 TP 抽取入库），不是 S8 反馈链。Round 2 误判为'等 S7/S8 真实跑通'"。

---

## 3. 前置依赖（修正后）

| 依赖 | 状态 | 解除条件 | 阻塞 v32_05 启动？|
|---|---|---|---|
| v3.01 S5 test_points.json | ✅ 230 TP 已存在 | 无 | ❌ 不阻塞 |
| v3.01 S6 test_cases.json | ✅ 230 TC 已存在 | 无 | ❌ 不阻塞 |
| `knowledge/public/test_point_library/` 目录 | ✅ 存在（8 模块子目录 + README + _index）| 无 | ❌ 不阻塞 |
| TP 抽取规则 | ❌ 未定义 | Round 4 act 起草 | ⚠️ 阻塞 |
| 人工审核机制 | ❌ 未建立 | Round 4 act 由用户决策"谁是审核员"| ⚠️ 阻塞 |
| `test_point_library/<MODULE>/` 子类模板（如 `BIZ/A_biz_logic.md`）| ❌ 全空（BIZ README 列 9 个"⏳ 待补"）| Round 5 act 抽取后填充 | ⚠️ 阻塞 |
| S7/S8 真实跑通 | ❌ 未跑（v3.01 仅走 S5→S6）| 用户决策是否启动新需求流程 | ❌ **不阻塞**（已修正 R2 误判）|

**结论**：v32_05 启动**需要 3 件事**：
1. TP 抽取规则定义（Round 4 act 起草）
2. 人工审核机制建立（Round 4 act 用户决策"谁是审核员"）
3. 子类模板文件（Round 5 act 抽取后填充）

---

## 4. Round 3 act grep 输出（前置盘点）

### 4.1 命令 1：TP 库现状

```bash
ls /Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/public/test_point_library/
```

**输出**：

```
UTIL/  BIZ/  CONFIG/  HINT/  LINK/  LOG/  README.md  SPECIAL/  UI/  _index.md
```

→ **目录骨架完整，8 模块子目录 + README + _index**。

### 4.2 命令 2：TP 库各模块文件统计

```bash
for d in UTIL BIZ CONFIG HINT LINK LOG SPECIAL UI; do
    ls -1 $d 2>/dev/null | wc -l
done
```

**输出**：

```
UTIL: 1 (README.md)
BIZ: 1 (README.md)
CONFIG: 1 (README.md)
HINT: 1 (README.md)
LINK: 1 (README.md)
LOG: 1 (README.md)
SPECIAL: 1 (README.md)
UI: 1 (README.md)
```

→ **每个模块仅 1 文件 = README.md，无子类模板（如 `BIZ/A_biz_logic.md`）**。

### 4.3 命令 3：BIZ 子目录 README 内容（前 20 行）

```bash
head -20 knowledge/public/test_point_library/BIZ/README.md
```

**输出**（关键段）：

```
# BIZ 模块 TP 库

> **TP 库位置**：`knowledge/public/test_point_library/BIZ/`
> **子模板来源**：`knowledge/public/module_templates/BIZ/`
> **v1.2 枚举数**：9（BIZ_LOGIC / BIZ_DATA_FLOW / BIZ_PROTOCOL / ...）

## TP 库文件清单

| 字母 | 子类 | 子类代码 | TP 库文件 | 状态 |
|------|------|---------|----------|------|
| A | 核心业务逻辑 | `BIZ_LOGIC` | [A_biz_logic.md](./A_biz_logic.md) | ⏳ 待补 |
| B | 端服数据流 | `BIZ_DATA_FLOW` | [B_data_flow.md](./B_data_flow.md) | ⏳ 待补 |
| ... | ... | ... | ... | ⏳ 待补 |
```

→ **BIZ 9 个子类全部"⏳ 待补"**——其他 7 模块同理。

### 4.4 命令 4：module_templates/ 现状（对照组）

```bash
ls /Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/public/module_templates/
```

**输出**：

```
UTIL/ UTIL.md BIZ/ BIZ.md CONFIG/ CONFIG.md HINT/ HINT.md LINK/ LINK.md
LOG/ LOG.md README.md SPECIAL/ SPECIAL.md UI/ UI.md
_common_structure.md  _decision_tree.md  s2_output_template.md
```

→ **module_templates/ 完整 8 模块 + 决策树 + S2 模板**——可作为 v32_05 抽取的"种子参考"。

### 4.5 命令 5：workflow_assets/_governance 状态

```bash
ls /Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets/_governance/ 2>&1
```

**输出**：

```
ls: /Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets/_governance/: No such file or directory
```

→ **`_governance/` 目录不存在**——v31 §8.5 提到 `recurring_failures.json` 但实际目录未创建。

### 4.6 命令 6：knowledge/project_local/.review_queue 现状

```bash
find /Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/project_local/.review_queue -type f 2>/dev/null
```

**输出**（实测 Round 3 act）：

```
/Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/project_local/.review_queue/s6/export_profiles/test_cases.export.example.json
```

→ **`.review_queue/` 仅有 1 个 S6 export profile example**——v31 §8.2 第 1 段（候选 TP 文件）的实际为空。

---

## 5. v32_05 启动决策（Round 4 act）

### 5.1 候选决策

| 选项 | 内容 | 影响 |
|----|----|----|
| **A**：v32_05 启动 | Round 5 act 起草 TP 抽取规则 + 启动首批回灌（v3.01 230 TP 抽 5~10 条入库）| ⚠️ 需用户决策"审核员是谁"|
| **B**：v32_05 推迟 | 等 S7/S8 真实跑通后启动（**R2 误判**）| ⚠️ 不推荐——R2 已修正，v32_05 不依赖 S7/S8 |
| **C**：v32_05 待定 | 本轮维持"待定"，Round 5 act 由用户决策 | ⚠️ 跳过本轮决策 |
| **D**：v32_05 暂不启动 | v32 治理路线跳过 v32_05（保留 Round 5+ 启动权）| ⚠️ v32 路线不完整 |

### 5.2 推荐路径

**推荐选项 A**（v32_05 启动）——理由：

1. **R2 误判已修正**：v32_05 不依赖 S7/S8，可立即启动
2. **v3.01 230 TP 是真实原料**：直接抽取首批 5~10 条入库，触发 `test_point_library/<MODULE>/` 子类模板填充
3. **激活阈值（v31 §8.4 ≥ 10 条）**短期可达 — 1 个 v3.01 抽 10 条即可触发
4. **TP 库 README 已写好 9 子类清单**（BIZ 等），可直接落档

### 5.3 Round 4 act 必做项（若选 A）

| 项 | 内容 | 产出 |
|----|----|----|
| **TP 抽取规则** | 定义"什么 TP 可入库"（按 OBJ 类型 / 按子类 / 按 EP_VALID/EP_INVALID 三轴）| `v32/v32_05_extraction_rule.md` |
| **人工审核机制** | 用户决策"谁是审核员"（AI 自治 / 人工逐条审 / 抽样审）| `v32/v32_05_review_mechanism.md` |
| **首批回灌** | v3.01 230 TP 抽 5~10 条 → 入库 → 更新 `test_point_library/<MODULE>/<Subclass>.md` | `v32/v32_05_pilot.md` |
| **AGENTS.md Git 分类铁律** | TP 库是公共知识库（`knowledge/public/`），**入库需要用户先确认**（AGENTS.md Git 分类铁律）| 决策咨询用户 |

---

## 6. 反向挑战

### 6.1 v32_05 启动决策的反向挑战

| 反例 | 是否推翻 |
|----|----|
| R2 误判为"等 S7/S8"是 Round 2 act 错误，Round 3 修正即可启动 | ⚠️ 部分成立——但 v32_05 仍需 TP 抽取规则 + 审核机制 |
| TP 库已有 README 模板，子类文件全"⏳ 待补"是设计预期 | ❌ 不存在——v31 已 achieved，README 写"待补"是 v31 遗留项 |
| v32_05 启动需要修改 `knowledge/public/test_point_library/`，属公共知识库修改——按 AGENTS.md Git 分类铁律**必须先询问** | ✅ 成立——Round 4 act 用户决策时一并询问 |
| v32_05 与 v32_04 强相关（多项目样本 → 多源 TP）| ⚠️ 部分成立——v32_05 仅依赖 v3.01 单样本 + LLM 模拟样本（B 路径），不依赖 v32_04 真实样本（A 路径）|

### 6.2 v32_05 误判"等 S7/S8"的根因

| 根因 | 应对 |
|----|----|
| `v32/PLAN.md` §3.5 末段"激活阈值（沿用 v31 §8.4）"被误读为"v32_05 启动的前置条件"| Round 4 act 修订 §3.5，明确"激活阈值是 S5 自动复用机制的触发条件，不是 v32_05 启动条件"|
| `v32/review_2.md` §3.3 把 v32_05 列为"依赖 S7/S8 链路"| Round 3 本档已修正；review_2.md 末段"Round 4+ 排期"需更新 |
| 缺 TP 抽取规则和审核机制时，v32_05 实际**无法启动**——R2 把"缺机制"误判为"缺数据"| Round 3 本档已显式列 3 项必做（抽取规则 + 审核机制 + 子类模板）|

---

## 7. 跨阶段影响

| 维度 | 影响 |
|----|----|
| `knowledge/public/test_point_library/` | ⚠️ Round 5 act 落档子类模板（5~10 条 TP）|
| `knowledge/project_local/.review_queue/` | ⚠️ Round 5 act 落档候选 TP 文件 |
| S5 生成 TP | ⚠️ 激活阈值（≥ 10 条）触发后，S5 LLM 自动复用 TP 模板 |
| AGENTS.md Git 分类铁律 | ⚠️ TP 库修改需先询问用户 |
| v32 治理路线完整性 | ⚠️ 跳过 v32_05 导致 v32 路线不完整 |

---

## 8. 验证证据

| 来源 | 关键数据 |
|----|----|
| `archive/v31_20260721_020714.bak/PLAN.md` §8.2 | 两段制归档链路（S8 → 候选 → 审核 → TP 库）|
| `archive/v31_20260721_020714.bak/PLAN.md` §8.4 | 激活阈值 ≥ 10 条 |
| `archive/v31_20260721_020714.bak/PLAN.md` §8.5 | recurring_failures.json 区分（与 TP 库不同）|
| `v32/PLAN.md` §3.5 | v32_05 方法描述（R2 误判为"等 S7/S8"）|
| `v32/review_2.md` §3.3 | Round 4+ 排期表（误判已修正）|
| 用户 Round 3 prompt | 显式修正 v32_05 不依赖 S7/S8 |
| 本档 §4 grep | TP 库 8 子目录全 README 无子类模板 |
| `knowledge/public/test_point_library/BIZ/README.md` | BIZ 9 子类全部"⏳ 待补"|

---

## 9. 下一步（Round 4 act）

| 启动项 | 来源 | 产出 |
|----|----|----|
| **R4-A**：用户决策 v32_03 SCC 公式 | `v32/decision_scc_formula.md` 4 选项 | 用户拍板 |
| **R4-B**：用户决策 v32_04 路径 | `v32/decision_v32_04_path.md` A+B 推荐 | 用户拍板 |
| **R4-C**：用户决策 v32_05 启动 | 本档 4 选项（A/B/C/D）| 用户拍板 |
| **R4-D**：若 R4-C 选 A（启动）| 起草 TP 抽取规则 + 审核机制 | `v32/v32_05_extraction_rule.md` + `v32/v32_05_review_mechanism.md` |

---

> **v32_05 前置盘点落档** — R2 误判已修正（v32_05 不依赖 S7/S8）；3 项必做（抽取规则 + 审核机制 + 子类模板）；待 Round 4 act 用户决策启动/推迟/待定