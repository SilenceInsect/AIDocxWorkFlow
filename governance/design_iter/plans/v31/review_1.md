# Round 1 — Review（S5/S6 方法论重写）

> **Goal**: S5 / S6 方法论、逻辑规则重写
> **Round**: 1
> **Date**: 2026-07-21
> **Draft**: `governance/design_iter/plans/v31/v31_方法论_草案.md`

---

## 缺陷汇总

| # | 缺陷 | 严重度 | 根因 | 修复 Round |
|---|------|--------|------|----------|
| **D1** | TP 库（`test_point_library/<MODULE>/`）8 模块全部为空（⏳ 待补） | MEDIUM | 历史遗留（v1.0 仅建索引未填 TP）；S5 LLM 实际只能"按 STAGE 规则生成"，无成品 TP 模板作锚点 | Round 2 act 决策 → Round 5 act 实施 |
| **D2** | 草案 §4.2 仅完整罗列 CONFIG/UI/BIZ 3 模块子类枚举；AUX/LINK/SPECIAL/LOG/HINT 5 模块以"见 SSOT"形式引用 | LOW | DNA §11 "不重复 SSOT"原则；如一次性展开 70+ 子类会违反分层 | Round 2 act 评估是否补全 |
| **D3** | S2 OBJ/FP 数量未在本响应再次 Read 验证（轻度 §9.4 警告） | LOW | Round 1 焦点是方法论设计而非样本计算；前次会话已 Read S2 backlog/requirement_objects | Round 4 act 计算覆盖率时重新 Read |
| **D4** | 草案未引入 `module_templates` 子模板（`CONFIG/A_field_legality.md` 等具体子模板文件）的内容做引用 | LOW | 草案目标是方法论骨架，不展开每个子模板的 TP 模板；S5 LLM 实际执行时需按需加载 | Round 2 act 补"按需加载清单" |
| **D5** | 既有 v31 目录残留旧 S1.5 目标的 `audit_1.md` + `review_1.md` + `PLAN.md` + `GOAL.md` + `CONVERGENCE_VERDICT.md` | LOW | 前序目标（s1-clarification-redesign-001）已 CONVERGED，残留文件未清理 | Round 2 act 决定是否归档/删除 |

### 详细根因

#### D1：TP 库全空

**根因链**：
1. `knowledge/public/test_point_library/README.md` §"维护流程"明确"本库目前为空，内容随项目积累逐渐填充"
2. 8 模块子模板（`A_*.md`、`B_*.md`...）的 v1.0 版本仅含种子 TP（`seed_tp_*`），未提炼为可复用 TP-TPL 条目
3. S5 LLM 实际生成时只能"按 STAGE 规则 + module_templates 关键词命中"，没有"成品 TP 模板"作为锚点 → **重复劳动 + 风格漂移风险**

**影响**：
- 用户诉求"越使用越成长"无法在 TP 库层积累（仅在 `module_templates` 的关键词命中上间接体现）
- S8 自迭代阶段的"高频 TP 入库"工作流空转（库是空的，无内容可对比）

**修复方案**：
- Round 2 act 决策 D4：采纳"A 策略"——Round 5 act 之前**不主动填充 TP 库**，仅在 Round 4 act 跑通 v3.01 样本时识别高频 TP（如被 ≥ 3 个 Story 复用的 TP），记入 Round 5 落档的"待入库清单"
- 长期修复（项目级，Round 1 不解决）：S8 自迭代阶段从 S5/S6 产出中提炼高频 TP 入库，按 README §"入库流程"执行

#### D2：§4.2 模块子类映射表 5 模块未展开

**根因链**：
1. 草案 §4.2 CONFIG/UI/BIZ 三模块用表格完整罗列子类（9 / 11 / 9 = 29 个枚举）
2. AUX/LINK/SPECIAL/LOG/HINT 五模块以"见 SSOT"形式引用
3. 一致性角度，五模块应当同样展开

**影响**：
- LLM 执行 S5 时，五模块的子类判定仍依赖 `module_templates/<MODULE>.md`（SSOT）——技术上不构成缺陷
- 但读者从草案 §4.2 看不出五模块的全子类清单（需要二次跳转到 SSOT）

**修复方案**：
- **方案 A（推荐）**：Round 2 act 在草案 §4.2 追加五模块子类表（引用而非展开——每行"子类枚举 | 子模板路径"）
- **方案 B（不推荐）**：展开全部 70+ 子类，违反 DNA §11 不重复 SSOT 原则

#### D3：S2 OBJ/FP 数字未验证

**根因链**：
1. Round 1 焦点是方法论设计（草案 §2/§3/§4）
2. 草案 §2.5/§3.5 字段溯源规则中"上游来源 = S2 OBJ/FP"，但**未在本响应 Read S2 验证具体 OBJ 数 / FP 数**
3. 前次会话的 Read 结果未在 Round 1 重新验证

**影响**：
- Round 1 范围内不影响（不计算覆盖率）
- Round 4 act 计算覆盖率时必须 Read S2 全文 + 验证

**修复方案**：
- Round 4 act 第一步：Read `requirement_objects.json` 全文 → 提取 OBJ 数量 + FP 数量 → 计算 §6 覆盖率

#### D4：未引用具体子模板文件

**根因链**：
1. 草案 §2.1 "按需读"清单已包含 `knowledge/public/module_templates/<MODULE>/<letter>_<subclass>.md`（如 `CONFIG/A_field_legality.md`）
2. 但 §4 映射表只到子类枚举粒度，未给每个枚举对应的"具体子模板文件路径 + 关键词命中规则"
3. LLM 执行时仍需要二次跳转 SSOT 加载子模板

**影响**：
- LLM 加载路径正确（§2.1 / §3.1 已声明）
- 但**"关键词命中规则"分散在每个子模板文件内**（如 `CONFIG/A_field_legality.md` 的"种子 TP 列表"）

**修复方案**：
- Round 2 act 在 §4 增加"关键词快速映射表"——把每个子模板的命中关键词集中到草案（不是展开子模板内容，只是搬运"快速映射表"作为 LLM 提示用）

#### D5：v31 目录残留旧 S1.5 目标文件

**根因链**：
1. 前序目标 `s1-clarification-redesign-001`（2026-07-20 启动）已 CONVERGED
2. 残留 `v31/PLAN.md` / `GOAL.md` / `audit_1.md` / `review_1.md` / `CONVERGENCE_VERDICT.md`
3. Round 1 act 覆盖了 `audit_1.md` + `review_1.md` 两个文件（旧内容丢失）；其余 3 个文件未触碰

**影响**：
- 旧 `v31/PLAN.md` 内容是 S1.5 重设计（如"v31 §解决 1：旧 S1.5 10 份前置物料 → 精简为 3 份"），与本目标（S5/S6 方法论）**主题不冲突但混淆**
- 旧 `v31/GOAL.md` 内容是 S1 阶段工作流+规则重新生成，与本目标主题完全不同
- 旧 `v31/CONVERGENCE_VERDICT.md` 标记为 CONVERGED，是历史归档

**修复方案**：
- Round 2 act 第一步：与用户确认 v31 目录处理方式
  - **方案 A**：保留旧文件 + 在文件名前加 `s1_5_` 前缀（归档）+ 新文件用 `s5_s6_` 前缀（如 `v31_s5_s6_PLAN.md`）
  - **方案 B**：直接删除旧文件（本目标独占 v31 目录）
  - **方案 C**：保留旧文件 + Round 5 act 落档新 PLAN 时，**重写** v31/PLAN.md（覆盖旧内容）
- 草案推荐**方案 C**（覆盖式 + 备份旧内容到 `v31/archive/` 子目录）

---

## 决策表（DNA §9.2 模板）

### Round 2 决策点（待用户确认）

| # | 决策 | 文件 | 影响范围 | 替代方案 | 草案推荐 |
|---|------|------|---------|---------|---------|
| **DT-1** | D1：TP 库填充策略 | 不直接落档；草案 §10 D4 已说明 | S8 自迭代阶段 | A: Round 5 之前不主动填 / B: Round 2 立即填充 | **A** |
| **DT-2** | D2：§4.2 五模块子类表是否展开 | `v31_方法论_草案.md` §4.2 | 草案篇幅 / SSOT 引用 | A: 引用"见 SSOT" / B: 追加"路径映射" | **A**（保留 SSOT 引用） |
| **DT-3** | D4：是否在 §4 增加"关键词快速映射表" | 同上 | 草案篇幅 vs LLM 提示完整性 | A: 增加 / B: 不增加（依赖 SSOT） | **A**（仅罗列路径，不展开内容） |
| **DT-4** | D5：v31 目录旧文件处理方式 | `v31/` 整目录 | 目录结构 / 历史归档 | A: 加前缀归档 / B: 删除 / C: Round 5 覆盖 | **C** + Round 2 act 立即备份到 `v31/archive/s1_5_*` |
| **DT-5** | §10 D1-D4 决策点 | 草案 §10 | TP/TC JSON 字段集 | 详见草案 §10 | A × 4 |

---

## 收敛判定

- Round 1 所有 T 完成（材料通读 + 方法论草案 + audit/review）
- 5 个缺陷已记录 + 修复方案已列
- 5 个决策点（DT-1 ~ DT-5）待用户表态
- 整体状态：✅ **PASS WITH PENDING DECISIONS**

> Round 2 act 启动条件：用户对 DT-1 ~ DT-5（合并 §10 D1-D4）表态后进入。
