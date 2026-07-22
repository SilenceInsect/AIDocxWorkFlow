# Round 2 — Audit（S5/S6 方法论重写）

> **Goal**: S5 / S6 方法论、逻辑规则重写
> **Round**: 2
> **Date**: 2026-07-21
> **Draft**: `governance/design_iter/plans/v31/v31_方法论_草案.md`（Round 2 演进版）
> **New Files**: `s8_knowledge_backflow_diagnosis.md` + `v31_SCC.md`

---

## 验收标准审计（对照 6 条 accept_criteria）

| # | 验收标准 | 证据 | Round 2 判定 |
|---|---------|------|-------------|
| **C1** | 方法论沉淀：S5/S6 完整链路 + LLM Prompt + 字段溯源 + 覆盖率公式 | `v31_方法论_草案.md` §2（S5）/ §3（S6）/ §2.5（SCC 新增）/ §3.4（TC 语义收紧新增）/ §6（覆盖率公式）| ✅ **PASS** |
| **C2** | 通用性验证：v3.01 样本跑通 | Round 2 仅完成方法论补充；跑通在 Round 3 act | ⏳ **PENDING**（Round 3 验证） |
| **C3** | 知识库贯通：8 模块 × 子类 × TP 模板映射 | 草案 §4（Round 1）+ §8（Round 2 S8 契约补充了 TP 库入库链路）| ✅ **PASS** |
| **C4** | 覆盖率口径：基于 S4 业务流，TP 引用所有叶子 + OBJ/FP ≥ §4.3 常量 | 草案 §6 口径不变；SCC 新增不影响覆盖率计算 | ✅ **PASS**（口径不变） |
| **C5** | 格式干净：JSON + MD + XLSX 三格式，0 违规 | 草案 §7 不变；TC 语义收紧（§3.4）进一步约束字段来源 | ✅ **PASS** |
| **C6** | 落档完整：方法论文档到 v31/PLAN.md + 产物归位 | Round 2 完成方法论补充；正式 PLAN.md 在 Round 5 act | ⏳ **PENDING**（Round 5 验证） |

### Round 2 判定汇总

- **C1 / C3 / C4 / C5**：✅ **PASS**（Round 1 已 PASS；Round 2 新增内容进一步强化）
- **C2 / C6**：⏳ **PENDING**（属 Round 3 / Round 5 act 范围）

---

## Round 2 新增内容证据

### C1 新增证据

| 新增段 | 内容摘要 | 证据文件 |
|--------|---------|---------|
| §2.5 故事复杂度系数（SCC）| SCC 公式（5 维度乘积）+ TP_TYPE_FACTOR 加权 + 软下限 0.8 + 商城样本计算 | `v31_SCC.md`（完整文件） + 草案 §2.5 |
| §3.4 TC 字段语义收紧规则 | 三条铁律（A: scenario == Epic.title / B: description ⊆ OBJ∪FP / C: obj_id 直接取值）+ 自检方法 + is_exploratory 字段 | 草案 §3.4.1-§3.4.5 |
| §8 S8 回灌 TP 库契约 | 两段归档链路（第1段本地队列 + 第2段人工审核）+ 候选格式 + 入库标准 + recurring_failures 区别 | `s8_knowledge_backflow_diagnosis.md` + 草案 §8 |

### C3 新增证据（TP 库入库链路）

Round 2 新增 §8 补充了"TP 库为空"的根因诊断 + 入库契约：
- 根因：不是 S8 Bug，是 v3.01 未走完 S5→S6→S7→S8 链路 + 人工审核机制缺失
- 契约：两段制归档（S8 → 本地候选 → 人工审核 → 公共库）
- 关联：`recurring_failures.json` ≠ `test_point_library/`（本地防止再犯 vs 公共知识积累）

---

## 反向挑战（DNA §10.5 不产出无根据结论）

### 反向挑战 1：§2.5 SCC 公式是否有实际样本支撑？

**验证**：SCC 公式在 §3 给出了商城道具购买 Story 的样本计算：
```
actors=2 × states=5 × timings=3 × boundaries=4 × exceptions=5 = SCC=600
理论 TP 数（POSITIVE）= 600 × 1.5 = 900
软下限 = 900 × 0.8 = 720
```
✅ 有样本计算，有维度来源说明（S2 requirement_objects.json + S4 business_flow.json）

### 反向挑战 2：§3.4 三条铁律能否防止"模型自由发挥"？

**验证**：
- 铁律 A：`scenario == Epic.title`（严格相等）→ 强制绑死，不允许包含/相似匹配
- 铁律 B：`description ⊆ OBJ∪FP`（集合校验）→ 差集必须 is_exploratory
- 铁律 C：`obj_id` 直接从 TP 继承 → 不允许自补

✅ 三条铁律覆盖"场景描述/功能描述/OBJ 引用"三个最易自由发挥的字段

### 反向挑战 3：§8 S8 契约是否与现有 S8 SKILL/STAGE 矛盾？

**验证**：
- S8 SKILL.md §归档机制明确："只读，不自动写入公共库" ✅ 契约保持此约束
- STAGE_S8 §1.5.2："禁止 S8 直接改公共库" ✅ 契约保持此约束
- S8 的双段制归档（本地队列→人工审核→公共库）与 S8 现有设计一致 ✅

### 反向挑战 4：Round 2 新增内容是否影响 C4/C5 判定？

- C4（覆盖率口径）：§2.5 SCC 仅影响 TP 数量估算，不影响覆盖率公式 ✅ 无影响
- C5（格式干净）：§3.4 TC 语义收紧进一步约束字段来源，有助于减少违规 ✅ 无影响

---

## Round 2 audit 结论

> **✅ PASS for Round 2 scope**
>
> Round 2 完成全部用户反馈（反馈 1/2/3 + DT-4/5）落地：
> - 反馈 1：S8 诊断文档 + §8 契约 ✅
> - 反馈 2：§3.4 TC 语义收紧 ✅
> - 反馈 3：§2.5 SCC + v31_SCC.md ✅
> - DT-4：推迟到 Round 3（已在 §9 标注）✅
> - DT-5：§2.2 is_assumed + §8 tpl_id 链路 ✅
