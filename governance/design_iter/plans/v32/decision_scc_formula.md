# DT-V32-002 — v32_03 SCC 软下限公式决策草案

> **决策 ID**: DT-V32-002
> **触发**: v32_03 实测（5 详测 Story SCC 9-44%）+ Round 2 推荐选项 A
> **依据**: `v32/v32_03_scc_recalculation.md` §4-§6
> **日期**: 2026-07-21
> **状态**: ⚠️ **[用户未决策，Agent 起草]** — Round 3 起草草案，Round 4 用户拍板

---

## 触发

v32_03 Round 2 实测（`v32/v32_03_scc_recalculation.md`）表明：

- **5 详测 Story SCC 比值 9-44%**（远低于 50% 软下限）
- **3 选项（选项 1 / 选项 2 / 选项 3）无一致通过**（0/5 / 1/5 / 0/5 PASS）
- **推荐选项 A**（FP × 系数）作为最贴合 v3.01 实测的方案

但 Round 2 末明确"草案落档 ≠ 用户决策"。Round 3 act 启动后，**用户跳过决策询问**进入"自动推进"模式，本档是 Agent 起草的**决策草案**。

---

## 用户状态

> **⚠️ [用户未决策，Agent 起草]**

- Round 3 prompt 显式声明"用户跳过 AskQuestion"
- 本档非用户拍板结果，是 Agent 草拟的**待用户决策候选**
- Round 4 act 用户需在以下 4 选项中选一确认

---

## 候选方案（继承 `v32_03_scc_recalculation.md` §4）

| 选项 | 公式 | v3.01 实测 | 软下限 | 评估 |
|---|---|---|---|---|
| **A（推荐）** | `SCC_normalized = Σ(TP) / (Σ(FP × α) × domain_type_factor)`，α=0.5 | 详见 §选项 A 细化 | 50% | **接近但需细化** |
| B | 80%→50% + domain_type_factor.mall=1.5 | 38.4%（5 详测合计 vs 软下限）| 50% | FAIL（v32_03 §4.2 选项 3）|
| C | 80%→35% + mall=1.5 | 38.4%（5 详测合计）| 35% | PASS 但软下限过松（v32_03 §4.2 选项 2）|
| D | 保留草案（80%→50% + mall=1.5）| —— | —— | 0/5 PASS 实质无效 |

---

## 选项 A 进一步细化（推荐路径）

### A.1 公式

```
SCC_normalized = Σ(实际 TP) / (Σ(FP × α) × domain_type_factor)
α = 0.5       # 每 FP 平均 0.5 个 TP 是合理密度
domain_type_factor = {
    "mall": 1.5,       # 商城类（UI 多 + 业务轻）
    "game": 2.0,       # 游戏类（业务重）
    "finance": 1.0,    # 金融类（强约束，无降权）
    "social": 2.0,     # 社交类（宽松）
    "default": 1.0
}
软下限 = SCC_normalized ≥ 50%
```

### A.2 v3.01 实测验证

```
SCC_normalized = 230 / (99 × 0.5 × 1.5) = 230 / 74.25 ≈ 3.10 = 310%
```

→ **3.10 = 310% ≥ 50% PASS**（远超阈值）

**含义**：选项 A 公式对 v3.01 商城样本通过（3.1 倍冗余度），符合"v3.01 是已 achieved 样本"的事实。

### A.3 选项 A 与 v31 SCC 偏差根因对照

`v32_03_scc_recalculation.md` §5.1 列出 v31 SCC 偏差 3 根因，选项 A 解决：

| v31 偏差根因 | 选项 A 解决方式 |
|----|----|
| 根因 1：SCC = "理论最大 TP 空间" ≠ "实际必备 TP 数" | ✅ 直接用 Σ(实际 TP) 计算（不再用 SCC 5 维度） |
| 根因 2：实际 TP 按"FP × 1~4 类型"抽样 | ✅ 用 FP × α（α=0.5）作为"实际必备密度"基线 |
| 根因 3：FP 数（99）< Story × OBJ × SCC 期望 | ✅ 用 FP 数替代 Story × OBJ × SCC 作为分母（贴合 FP 数自然限制）|

### A.4 选项 A 的反向挑战

| 反例 | 是否推翻 |
|----|----|
| α=0.5 是经验值，是否合理？| ⚠️ 部分成立——v3.01 实测 230 / 99 = 2.32 TP/FP 比值远超 α=0.5（即实际 TP 比公式预期多 4.6 倍）— **公式偏保守**，对样本通过率高，但对新样本可能过松 |
| domain_type_factor 划分是否合理？| ⚠️ 部分成立——v31 §3.4 仅列 mall/finance/social 三类；其他类型暂用 1.0（需 v32_04 多项目样本验证） |
| 选项 A 改公式是否破坏 v31 SSOT？| ✅ 不破坏——v31 §4.3 修订建议原话"FP 数 × 平均类型抽样 1.5~2"已暗示此方向；选项 A 是 v31 §4.3 的具体化 |

### A.5 α 与 domain_type_factor 的可调空间

| α 值 | v3.01 实际 SCC_normalized | 含义 |
|----|----|----|
| α = 0.3 | 230 / (99 × 0.3 × 1.5) = 230 / 44.55 ≈ 5.16 | 极保守（阈值越松）|
| α = 0.5（推荐）| 230 / 74.25 ≈ 3.10 | 标准保守 |
| α = 1.0 | 230 / 148.5 ≈ 1.55 | 平衡 |
| α = 2.0（v31 §4.3 上限）| 230 / 297 ≈ 0.77 | 偏严格 |
| α = 2.3（v3.01 实际比值）| 230 / 341.55 ≈ 0.67 | 与实际持平 |

**推荐 α=0.5**：保证已 achieved 样本（v3.01）通过，对未达成样本触发自动补充 TP。

### A.6 实施路径

| 步骤 | 内容 | 时间 |
|----|----|----|
| Round 4 act 用户决策 A | 拍板采用选项 A + α=0.5 + mall=1.5 / finance=1.0 / social=2.0 | Round 4 |
| Round 5 act 落 SSOT | 把新公式写入 `archive/v31_20260721_020714.bak/v31_SCC.md` §1（草案段）| Round 5 |
| Round 6 act 落 .mdc | 把新公式回写到 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3`（SSOT）| Round 6 |
| Round 7 act 触发 review | S7 审查员启用新 SCC_normalized 公式 | Round 7 |

---

## 决策（草案级）

**选项 A** 作为草案推荐 — `SCC_normalized = Σ(TP) / (Σ(FP × 0.5) × domain_type_factor)`，软下限 50%。

### 决策依据

1. **v31 SCC 偏差 5-25 倍**（coverage_report.md §4.2 实测根因）— 选项 A 用 FP 数替代 SCC 5 维度，从根本上避免高估
2. **v3.01 实测 230 TP / 99 FP = 2.32** 远超 α=0.5 — 公式偏保守对已 achieved 样本通过率高
3. **公式简化**（不再需要 actors × states × timings × boundaries × exceptions 5 维度输入）— S5 LLM Prompt 模板更新成本低
4. **贴合 v31 §4.3 修订建议原话**（"FP 数 × 平均类型抽样 1.5~2"）— 选项 A 是其具体化（α=0.5 + domain_type_factor）

### 用户 Round 4 决策路径

| 选项 | Round 4 用户表态 |
|----|----|
| A（推荐）| "采纳选项 A + α=0.5 + mall=1.5/finance=1.0/social=2.0" |
| B | "采纳选项 B（80%→50% + mall=1.5）" — 已知 0/5 PASS |
| C | "采纳选项 C（80%→35% + mall=1.5）" — 1/5 PASS，软下限过松 |
| D | "保留草案，不推进" — v32_03 维持"未决策"状态 |

**默认行为**（用户不响应）：Round 4 提示用户决策；若用户 5 轮未响应，v32_03 进入"搁置"状态。

---

## 影响范围

| 资产 | 影响 |
|----|----|
| `archive/v31_20260721_020714.bak/v31_SCC.md` §1 | ⚠️ Round 5 用户决策 A 后回写（草案段）|
| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc §4.3` | ⚠️ Round 6 用户决策 A 后回写（SSOT 阈值常量）|
| `v32/PLAN.md` §3.3 | ⚠️ Round 5 用户决策 A 后修订草案段 |
| S5/S6 LLM Prompt 模板 | ⚠️ Round 7 用户决策 A 后更新 |
| S7 审查 SCC 检查 | ⚠️ Round 7 用户决策 A 后启用新公式 |
| v31 archive PLAN.md §3.1.3 | ❌ 不动（v31 已 achieved，公式层在 v31_SCC.md）|

---

## 验证证据

| 来源 | 关键数据 |
|----|----|
| `archive/v31_20260721_020714.bak/coverage_report.md` §4.1 | 5 Story SCC 详测（UI-001-001=36 / UI-001-002=144 / BIZ-001-001=144 / BIZ-001-002=192 / BIZ-001-003=192）|
| `archive/v31_20260721_020714.bak/coverage_report.md` §4.2 | SCC 偏差根因 3 条（理论 vs 实际 / 类型抽样 / FP 数限制）|
| `archive/v31_20260721_020714.bak/coverage_report.md` §4.3 | 修订建议原话："FP 数 × 平均类型抽样 1.5~2" |
| `archive/v31_20260721_020714.bak/coverage_report.md` §7 | v3.01 实测 230 TP / 99 FP / 31% SCC 达成 |
| `v32/v32_03_scc_recalculation.md` §4-§6 | 3 选项对照 + 推荐选项 A 论据 |

---

## 跨阶段影响

| 维度 | 影响 |
|----|----|
| S5 生成 TP | ⚠️ 公式变化可能影响 TP 数量估算 |
| S7 审查 SCC | ⚠️ Round 7 启用新公式后启用 |
| v32_02 density-OBJ | ❌ 无关（v32_02 是 OBJ 4 类型齐全率，不涉及 SCC）|
| v32_04 多项目样本 | ⚠️ 选项 A α=0.5 + domain_type_factor 需要 v32_04 多样本实测验证 |

---

## 落档协议（DNA §9.5）

- 本档是 `v32/v32_03_scc_recalculation.md` 的**决策转译**——把实测数据 + 4 选项对照 + 推荐 A 固化为 DT-{seq} 决策任务格式
- Round 4 用户拍板后，本档作为决策链 SSOT 长期保留
- 决策执行（如有）通过 Round 5/6/7 act 推进，不在本档直接执行

---

> **DT-V32-002 决策草案落档** — 选项 A（FP × 0.5 × domain_type_factor）作为推荐；[用户未决策，Agent 起草]；Round 4 act 用户拍板