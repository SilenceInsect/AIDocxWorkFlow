# DT-V32-003 — v32_04 多项目样本策略决策草案

> **决策 ID**: DT-V32-003
> **触发**: v32_04 grep 实测（`v32/v32_04_candidate_samples.md` §1.1~§1.4）显示 workflow_assets 仅有 v3.01 单样本
> **依据**: `v32/v32_04_candidate_samples.md` §3.2 替代方案 + 本轮 grep 进一步实测
> **日期**: 2026-07-21
> **状态**: ⚠️ **[用户未决策，Agent 起草]** — Round 3 起草草案，Round 4 用户拍板

---

## 触发

v32_04 Round 2 实测（`v32/v32_04_candidate_samples.md`）表明：

- **workflow_assets 仅有 v3.01 1 个真实样本**（BIZ / UI / LOG / LINK 4 模块覆盖）
- **`find ... -not -path "*v3.01*"` 输出空**
- **`example_test_cases/` 目录不存在**
- **`test_point_library/` 是模板库非样本库**

Round 3 act 进一步实测 `knowledge/project_local/` 候选样本（详见本档 §3），仍**无完整 S5/S6 样本**。v32_04 启动条件结构性瓶颈。

---

## 用户状态

> **⚠️ [用户未决策，Agent 起草]**

- Round 3 prompt 显式声明"用户跳过 AskQuestion"
- 本档非用户拍板结果，是 Agent 草拟的**待用户决策候选**
- Round 4 act 用户需在以下 4 替代方案中选一确认

---

## 4 替代方案（继承 `v32_04_candidate_samples.md` §3.2 + §4.3）

| 选项 | 路径 | 成本 | 价值 |
|---|---|---|---|
| A | 推迟到第二个真实需求 | 0 | ⚠️ 高（真实样本可信）但时机不可控 |
| **B（推荐）** | LLM 模拟样本 dry-run | 中（手工构造）| ⚠️ 低（LLM 生成 vs 真实样本有差异）|
| C | `module_templates/` 子样本 | 低 | ⚠️ 中（子样本 ≠ 完整需求）|
| **D（推荐）** | `knowledge/project_local/` 历史样本 | 中 | ⚠️ 高（真实历史）但需兼容性验证 |

---

## 推荐组合：B + D 并行

### B + D 并行的设计逻辑

| 路径 | 角色 |
|----|----|
| **B**：LLM 模拟样本 | 短期可控（不依赖新需求触发）+ 验证"v31 方法论可跑通" |
| **D**：`knowledge/project_local/` 历史样本 | 真实历史样本（即使不完整）+ 验证"v31 方法论兼容性" |

**并行不冲突**：B 不依赖 D 的产出，D 不依赖 B 的产出，可全并行。

### Round 3 act grep 进一步实测（修正 R2-C 候选）

```bash
find /Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/project_local -name "*.json" 2>/dev/null
```

**输出**：

```
/Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/project_local/AMRD/s6/export_profiles/test_cases.export.json
/Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/project_local/.review_queue/s6/export_profiles/test_cases.export.example.json
/Users/gleon/Documents/TestDev/AIDocxWorkFlow/knowledge/project_local/游戏道具商城/s6/export_profiles/test_cases.export.json
```

### 候选样本剖析

| 路径 | 内容 | 是否 S5/S6 样本 |
|----|----|----|
| `AMRD/s6/export_profiles/test_cases.export.json` | **S6 export profile**（输出配置：sheet_name + headers + field_mapping），**非测试用例** | ❌ 否（仅 S6 导出配置）|
| `.review_queue/s6/export_profiles/test_cases.export.example.json` | **example 模板**（注: "复制到 ... 后生效"）| ❌ 否（example 模板）|
| `游戏道具商城/s6/export_profiles/test_cases.export.json` | **同上 S6 export profile** | ❌ 否 |

**关键事实**：**`knowledge/project_local/` 仅有 S6 导出配置，无任何 S5 test_points.json 或 S6 test_cases.json 完整样本**。

→ **D 候选真实状态**：**实际样本为空**——`knowledge/project_local/` 仅有"导出配置"，不是 v32_04 所需的"测试用例样本"。

### B + D 重新评估（基于本轮实测）

| 选项 | 实测后评估 |
|----|----|
| A | ✅ 推迟（仍推荐作为最终路径）|
| **B** | ⚠️ LLM 模拟仍是短期可控路径（**推荐保留**）|
| C | ❌ 弱推荐（`module_templates/` 模板 ≠ 完整需求样本）|
| **D** | ❌ **实测后不推荐** —— `knowledge/project_local/` 无 S5/S6 样本，仅有导出配置；用户 prompt 误判 |

### 修订后的推荐组合：**A + B 并行**

| 路径 | 角色 |
|----|----|
| **A**：推迟到第二个真实需求 | 长期价值路径（真实样本可信）|
| **B**：LLM 模拟样本 dry-run | 短期可控路径（不依赖新需求）|

### 反向挑战

| 反例 | 是否推翻 |
|----|----|
| 组合 A+B 是否过宽？| ❌ 不存在——A 被动等待 + B 主动构造，两者并行不冲突 |
| B 模拟样本与 v31 SSOT 不对齐？| ⚠️ 部分成立——但 B 仅验证"v31 方法论可跑通"，不要求"v31 SSOT 通用性"（那是 A 的目标）|
| D 方案实测后发现不可行，是否要 Round 4 重新决策？| ❌ 不存在——本档已显式说明 D 不推荐（实测依据），A+B 是修订后的推荐 |

---

## 决策（草案级）

**修订后推荐组合**：**A + B 并行**（**不是用户 prompt 的 B+D**——D 实测后不推荐）

### 决策依据

1. **D 候选实测后无 S5/S6 样本**——`knowledge/project_local/` 仅有 S6 导出配置 + example 模板
2. **A 路径（推迟到第二个真实需求）**长期价值最高（真实样本可信），但**时机不可控**
3. **B 路径（LLM 模拟样本 dry-run）**短期可控（不依赖新需求触发）
4. **A+B 并行**：B 填补短期缺口 + A 等待真实样本触发

### 用户 Round 4 决策路径

| 选项 | Round 4 用户表态 |
|----|----|
| A+B（推荐）| "采纳 A+B 并行 — 短期 B 模拟 + 长期 A 等真实样本" |
| A 单独 | "仅采纳 A — v32_04 完全推迟" |
| B 单独 | "仅采纳 B — v32_04 仅做 LLM 模拟" |
| D 单选 | "采纳 D —— 但需先扩充 knowledge/project_local/ 真实样本" |

**默认行为**（用户不响应）：Round 4 提示用户决策；若用户 5 轮未响应，v32_04 维持"搁置"状态。

---

## 实施路径（A+B 并行版）

| 步骤 | 内容 | 时间 |
|----|----|----|
| Round 4 act 用户决策 A+B | 拍板采用 A+B 并行 | Round 4 |
| Round 5 act 启动 B | LLM 手工构造 2~3 个 mini 样本（mall + finance 各 1）| Round 5 |
| Round 5 act 启动 A 等待 | 在 workflow_assets/ 下建新需求目录，等待真实样本触发 | Round 5 |
| Round 6 act 回写 v32_04 报告 | B 路径落档 `v32/v32_04_report.md` 含 LLM 模拟样本对照 | Round 6 |
| Round 7+ 真实样本触发 | A 路径落档新需求 v32_04_report，含真实样本对照 | 真实需求触发时 |

### B 路径：LLM 模拟样本设计（草案）

| 维度 | 设计 |
|----|----|
| 样本规模 | 2 个 mini 需求（mall 1 + finance 1），每个 4~6 Story + 8~12 OBJ + 20~30 FP + 60~90 TP |
| 上游材料 | LLM 手工生成 S2 backlog + S4 business_flow（不含 S3 prototype）|
| S5 生成 | 用 v31 §3.1.4 Prompt 跑（与 v3.01 一致）|
| S6 生成 | 用 v31 §3.2.4 Prompt 跑（与 v3.01 一致）|
| 对照指标 | 模块分布 / 字段语义一致性 / 4 项覆盖率 / density-OBJ（v32_02 同期产出）|
| 局限声明 | B 路径仅验证"v31 方法论可跑通"，**不证 v31 SSOT 跨需求通用性**（那是 A 路径的目标）|

### A 路径：真实样本触发条件

| 触发条件 | 启动 A 路径 |
|----|----|
| 新需求走完整 S5→S6→S7→S8 | workflow_assets/<req_name>/<version>/「S5」+「S6」存在 |
| S7 review 通过 | v32_04_report 包含新需求实测对照 |

---

## 影响范围

| 资产 | 影响 |
|----|----|
| `v32/v32_04_report.md` | ⏳ Round 6 act 落档（B 路径实测对照）|
| `workflow_assets/` 多样化 | ⏳ 用户决策是否启动新需求流程（A 路径触发条件）|
| `knowledge/project_local/` 真实样本扩充 | ⏳ D 路径需要先扩充（已实测无可用样本）|

---

## 验证证据

| 来源 | 关键数据 |
|----|----|
| `v32/v32_04_candidate_samples.md` §1.1-§1.4 | workflow_assets 仅 v3.01 单样本 |
| `v32/v32_04_candidate_samples.md` §3.2 | 4 替代方案（A/B/C/D）|
| 本档 §3 进一步 grep | `knowledge/project_local/` 仅 S6 export profile + example，无 S5/S6 样本 |

---

## 跨阶段影响

| 维度 | 影响 |
|----|----|
| v32_01（UI 交叉）| ❌ 不依赖 v32_04 |
| v32_02（density-OBJ）| ⚠️ 依赖 v32_04（B 路径实测产出 density 数据）|
| v32_03（SCC 公式）| ⚠️ α=0.5 / domain_type_factor 需 v32_04 多样本验证 |
| v32_05（TP 库回灌）| ❌ 不依赖 v32_04 |

---

## 落档协议（DNA §9.5）

- 本档是 `v32/v32_04_candidate_samples.md` 的**决策转译**——把瓶颈诊断 + 4 替代方案 + B+D 推荐固化为 DT-{seq} 决策任务格式
- 本档**修订了用户 prompt 的 B+D 推荐**——D 路径实测后无 S5/S6 样本（仅有 S6 导出配置），推荐改为 A+B
- Round 4 用户拍板后，本档作为决策链 SSOT 长期保留

---

> **DT-V32-003 决策草案落档** — 修订后推荐 **A+B 并行**（D 实测后不推荐）；[用户未决策，Agent 起草]；Round 4 act 用户拍板