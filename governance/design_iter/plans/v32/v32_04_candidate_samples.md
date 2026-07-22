# v32_04 — 多项目样本候选清单（grep 结果 + 瓶颈诊断）

> **路由**: v32_04
> **日期**: 2026-07-21
> **依据**: `v32/PLAN.md` §3.4 启动前检查
> **状态**: ⚠️ **结构性瓶颈** — 仅有 v3.01 1 个真实样本

---

## 1. grep 命令实测结果

### 1.1 命令 1：找所有 `「S5 测试点生成」` 目录

```bash
find /Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets \
  -type d -name "「S5 测试点生成」" 2>/dev/null
```

**输出**：

```
/Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets/游戏道具商城系统/v3.01/「S5 测试点生成」
```

→ **只命中 1 个样本（v3.01 商城）**。

### 1.2 命令 2：排除 v3.01

```bash
find /Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets \
  -type d -name "「S5 测试点生成」" -not -path "*v3.01*" 2>/dev/null
```

**输出**：空（无任何结果）

→ **v3.01 之外没有第二个真实 S5 完成的需求**。

### 1.3 命令 3：workflow_assets 顶层需求目录

```bash
find /Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets \
  -mindepth 1 -maxdepth 1 -type d
```

**输出**：

```
/Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets/游戏道具商城系统
```

→ **整个 workflow_assets 仅有 1 个需求目录（游戏道具商城系统）**。

### 1.4 命令 4：所有需求×版本组合

```bash
find /Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets \
  -mindepth 2 -maxdepth 2 -type d
```

**输出**：

```
/Users/gleon/Documents/TestDev/AIDocxWorkFlow/workflow_assets/游戏道具商城系统/v3.01
```

→ **仅有 v3.01 一个版本**。

### 1.5 命令 5：备用 `knowledge/public/example_test_cases/`

```bash
ls /Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/public/example_test_cases/
```

**输出**：（目录不存在）

→ **备用历史样本库为空**。

### 1.6 命令 6：TP 库现状

```bash
ls /Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/public/test_point_library/
```

**输出**：

```
UTIL/  BIZ/  CONFIG/  HINT/  LINK/  LOG/  README.md  SPECIAL/  UI/  _index.md
```

→ **TP 库有 8 模块子目录 + README，但每个子目录是否含 TP 模板未查**——不是样本库，是**模板库**。

---

## 2. 候选清单（grep 综合）

| 候选 | 需求 | 版本 | S5 test_points.json | S6 test_cases.json | 状态 |
|----|----|----|----|----|----|
| 唯一 | 游戏道具商城系统 | v3.01 | 230 TP ✅ | 230 TC ✅ | 已 achieved（v31 样本）|
| 候选 1 | 游戏道具商城系统 | 其他版本 | — | — | ❌ 不存在 |
| 候选 2 | 其他需求 | 任意 | — | — | ❌ 不存在 |
| 候选 3 | `knowledge/public/example_test_cases/` | — | — | — | ❌ 目录不存在 |
| 候选 4 | `test_point_library/` 各模块 | — | TP 模板（非样本） | — | ⚠️ 模板库 ≠ 需求样本 |

---

## 3. 候选评估

### 3.1 v32_04 启动条件

`v32/PLAN.md` §3.4 启动前检查：

> v3.01 之外至少有 2 个 S5/S6 完成的样本（需用户确认 `workflow_assets/` 范围）
> 若样本不足 → v32_04 暂缓，启动 v32_05 替代

**实测结果**：

- ❌ v3.01 之外 S5 完成样本：**0 个**
- ❌ 其他需求的 S5/S6 完成样本：**0 个**
- ❌ `example_test_cases/` 备用库：**目录不存在**

**结论**：**v32_04 在当前 workflow_assets 状态下无法启动**。

### 3.2 替代方案

| 替代 | 内容 | 评估 |
|----|----|----|
| **A**：v32_04 推迟 | 等真实新需求跑完 S5/S6 后再启动 | ⚠️ 时间不可控 — 需新需求触发 |
| **B**：LLM 生成"模拟需求样本"做 dry-run | 手工构造 2~3 个小需求（S2 + S3 + S4 + S5），跑 v31 方法论 | ⚠️ 模拟 ≠ 真实；用于"方法论可跑通"验证，不证通用性 |
| **C**：从 `test_point_library/` 抽子样本 | 各模块子目录（如 BIZ/A_biz_logic.md）抽 1 个完整 TP 模板 | ⚠️ 单 TP 模板 ≠ 完整需求样本；无下游 TC / OBJ / FP 对照 |
| **D**：用 v3.01 内部"子样本" | 把 v3.01 16 Story 按 module 拆（UI 4 Story / BIZ 6 Story / ...），每个 module 子集当独立样本 | ⚠️ 子集分析 ≠ 多项目；仅能验证模块分布 |

---

## 4. 反向挑战

### 4.1 v32_04 结构性瓶颈的影响

| 反例 | 是否推翻 |
|----|----|
| v32_04 是 v32 整条治理路线"验证 v31 SSOT 是否通用"的关键实验 — **若无样本 → v32_04 实质空转** | ⚠️ 部分成立 — v32_04 不可启动，但 v32 整条路线仍可继续（v32_01/02/03/05 不依赖多项目）|
| "v32 整条治理路线失效"过于激烈 | ❌ 不成立 — v32_01（UI 交叉）/ v32_02（density）/ v32_03（SCC）/ v32_05（TP 库）均不依赖多项目样本 |
| 推动用户提交新需求是治理问题的"绕路解决" | ❌ 不成立 — v32 推进的目标是 v31 SSOT 验证，并非"强制创建新需求"|

### 4.2 workflow_assets 状态的根因

| 维度 | 当前 | 推断原因 |
|----|----|----|
| 需求目录数 | 1 | 项目长期以商城样本为唯一工件 |
| 版本数 | 1（v3.01）| 需求范围未发生重大调整（v8 增量版本语义下不需要新版本）|
| 历史归档 | 0 | v32 之前未走样本多样化策略 |

**根因**：项目自 v31 以来聚焦 S5/S6 方法论重写，未启动多个新需求 → workflow_assets 单一化。**非项目问题，是治理路线阶段性特征**。

### 4.3 替代方案优劣对比

| 维度 | A 推迟 | B LLM 模拟 | C TP 模板 | D module 子集 |
|----|----|----|----|----|
| 时间可控 | ⚠️ 不可控 | ✅ 可控 | ✅ 可控 | ✅ 可控 |
| 真实需求验证 | ✅ 高 | ❌ 模拟 | ❌ 模板 | ⚠️ 子集 |
| 工程成本 | 0 | 中（手工构造）| 低 | 低 |
| v32_04 通用性证据强度 | 高（待真实样本）| 低（不证通用）| 极低 | 中（仅证模块层）|

---

## 5. 决策（草案落档，待 Round 3 用户决策）

**推荐方案**：**B + D 并行**（短期可控 + 真实样本）

| 步骤 | 内容 | 时间 |
|----|----|----|
| **Step 1**：Round 3 用户决策 v32_04 路径 | 从 A/B/C/D 选一（或 B+D）| Round 3 act |
| **Step 2**：若选 B | 手工构造 2 个 mini 样本（mall + finance 各 1），跑 v31 方法论 | Round 4 act |
| **Step 3**：若选 D | 把 v3.01 16 Story 拆 module 子集，每模块跑 v31 SSOT 4 项覆盖率 | Round 4 act |
| **Step 4**：回写 v32_04 报告 | 落档 `v32/v32_04_report.md` 含真实对照数据 | Round 4 act |

**关键事实**：

- ✅ B 方案可以填补 R2-C 工作（不依赖新需求触发）
- ⚠️ B 方案"模拟样本"质量取决于 LLM 生成的 S2/S4 上游材料真实性
- ⚠️ D 方案"模块子集"是 v3.01 内部分析，不证 v31 SSOT 跨需求通用性（仅证模块层）
- ⚠️ A 方案等真实样本是最终路径，但触发时机不可控

**草案 ≠ 决策**：

- 本档是 R2-C 候选清单与瓶颈诊断
- Round 3 act 由用户在 A/B/C/D 选项中选最终路径
- 选定后启动 v32_04 实测

---

## 6. 验证证据

| 来源 | 关键数据 |
|----|----|
| `find workflow_assets ...` 输出 | 唯一命中 `v3.01/「S5 测试点生成」` |
| `find ... -not -path "*v3.01*"` 输出 | 空 |
| `find workflow_assets -mindepth 2 -maxdepth 2` 输出 | 唯一 `游戏道具商城系统/v3.01` |
| `ls knowledge/public/example_test_cases/` | 目录不存在 |
| `ls knowledge/public/test_point_library/` | 8 模块目录 + README（模板库）|

---

## 7. 跨阶段影响

| 资产 | 影响 |
|----|----|
| `v32_04_candidate_samples.md`（本档）| ✅ 落档（瓶颈诊断 + 4 替代方案）|
| `v32/PLAN.md` §3.4 | ⚠️ Round 3 用户决策后更新"替代方案"段 |
| `v32/v32_04_report.md` | ⏳ 待 Round 4 act 落档（路径选定后）|
| `workflow_assets/` 多样化 | ⏳ 用户决策是否启动新需求流程 |

---

## 8. 后续轮次触发条件

| 触发条件 | 启动项 |
|----|----|
| Round 3 用户决策 B / C / D 任一 | Round 4 act 启动 v32_04 实测 |
| Round 3 用户决策 A | 等真实新需求跑完 S5/S6 后再启动（时机不可控）|
| Round 3 用户决策"不启动 v32_04" | v32 治理路线绕过 v32_04，仅走 v32_01/02/03/05 → CONVERGED |

---

> **v32_04 候选清单落档** — workflow_assets 仅有 v3.01 单样本（结构性瓶颈）；4 替代方案对照；待 Round 3 act 用户决策路径
