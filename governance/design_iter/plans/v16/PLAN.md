# AIDocxWorkFlow v16 — v1.1 迭代方案落地治理

> **本版本定位**：将 v1.1 迭代方案 10 项改动 + 审核档 10 项冲突点统一纳入 v16 治理周期
> **审核档**：`governance/design_iter/current/v15_v1_1_iteration_audit.md`（2026-07-17 落档）
> **用户拍板（2026-07-17）**：全部推进 10 项 + 开新独立迭代版本 v16
> **基线版本**：v15（阶段 1/2/3 全部完成；阶段 1 任务④ BLOCKED）
> **对应产品版本**：v1.1（落地后升 AIDocxWorkFlow 到 v1.1）

---

## §0 拍板依据

| 拍板项 | 用户决策 | 含义 |
|---|---|---|
| Q1 P0 取舍 | **全部推进**（含 #5 三级覆盖率） | 5 项 P0 + 4 项 P1 + 2 项 P2 + C5 红警收紧全部纳入 v16 |
| Q2 最小落地集 | **全部推进** | #2 / #4 / C5 三项无遗漏；其他项按拍板节奏推进 |
| Q3 v16 治理 | **开新的迭代版本 v16** | 不作为 v15 实施补遗；独立治理周期；按 v15/v14 格式走 `plans/v16/PLAN.md` |

---

## §1 v16 范围（10 项改动 + 10 项冲突）

### 1.1 P0 改动（6 项，本周-2 周）

| 编号 | 项 | 优先级 | 难度 | 依赖 | 落地文件 |
|---|---|---|---|---|---|
| #2 | 模块优先级矩阵补充 | P0 | 低 | 无 | `MODULES.md` §3.5 + STAGE_S5/S4 |
| #4 | L1 格式硬校验门禁 | P0 | 低 | 复用 `s5_exit_precheck.py` | `ai_workflow/l1_format_validator.py`（新）+ 7 个阶段校验规则 |
| C5 | 红警阈值 40% → 20% | P0 | 0 改动 | 无 | `DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.4.2（已为 0.20，确认无变化）|
| #1 | S1 结构化评审包 + S2 消费 | P0 | 中 | C1 边界设计 | `STAGE_S1_REVIEW.mdc` §1.5.4 + S1 SKILL + S2 SKILL |
| #3 | related_tags + 双轨覆盖率 | P0 | 中 | C3 字段命名 + C5 双轨优先级 | `STAGE_S5_TEST_POINTS.mdc` §1.6 + TP JSON schema |
| #5 | 三级覆盖率深度定义 | P0 | 中-高 | 缺 L2 属性级机检方法 + 与 S5 §FP 门禁冲突 | `STAGE_S5_TEST_POINTS.mdc` + `STAGE_S7_REVIEW.mdc` |

### 1.2 P1 改动（3 项，2-3 周）

| 编号 | 项 | 优先级 | 难度 | 依赖 | 落地文件 |
|---|---|---|---|---|---|
| #6 | L2/L3 门禁 + 黄金用例基准 | P1 | 中 | 黄金库录入（v15 阶段 1 任务④ BLOCKED 部分解锁） | `ai_workflow/golden_case_compare.py`（新）+ S7 SKILL.md |
| #7 | S7 三层审查架构重构 | P1 | 中 | 复用 #4 L1 + #6 L3 | `STAGE_S7_REVIEW.mdc` + `aidocx-s7-review/SKILL.md` §131-156 重写 |
| C8 | S8 RCA 新根因类型命名 | P1 | 中 | 走 v16 治理拍板（不可在 #9 一并改）| `STAGE_S8_SELF_ITERATION.mdc` §142-148 |

### 1.3 P2 改动（2 项，3-4 周）

| 编号 | 项 | 优先级 | 难度 | 依赖 | 落地文件 |
|---|---|---|---|---|---|
| #8 | SPECIAL 变体用例机制 | P2 | 高 | v15 §A.1 变体化能力框架 + 真实 TC 数据 | TC JSON schema + 变体解析器 |
| #9 + #10 | S8 根因自动分流 + 全局经验库 | P2 | 高 | C8 RCA 命名 + v15 §A.3 dashboard 合并 | `STAGE_S8_SELF_ITERATION.mdc` + `knowledge/public/experience/` 候选区 |

### 1.4 冲突点解决（C1-C10，v16 治理拍板）

| 冲突 | 解决方式 | 责任人 |
|---|---|---|
| C1 S1 vs S1.5 职责重叠 | **拆分**：S1 评审产出结构化洞察（review_structured.json）；S1.5 准出许可（exit_permission.json）独立——S1.5 引用 S1 结构化包作为输入 | v16 PLAN §2 #1 |
| C2 S1.5 越权标功能优先级 | **不改 S1.5**：S2 自行在 `requirement_objects.json` 中按 epic 标 risk_level | 写明 SKILL |
| C3 TP 字段重复 | **保留 module、新增 related_tags**（不要 primary_module） | v16 PLAN §2 #3 |
| C4 L1 与 s5_exit_precheck.py 重叠 | **复用 + 扩展**：抽 `l1_format_validator.py` 通用基类 | v16 PLAN §2 #4 |
| C5 三步自问删 Q3 | **不改 Q3**：仅保留"红警阈值收紧至 20%"——已在 SSOT | v16 PLAN §2 C5 |
| C6 三级覆盖率与 S5 §FP 冲突 | **推迟到 v16 阶段 2**（#5 落地时统一指标口径） | v16 PLAN §2 #5 |
| C7 L3 黄金用例与 v15 §A.2 重叠 | **合并**：v16 用例质量评分体系 = A2 3 维评分 + v1.1 L3 黄金库 | v16 PLAN §3 #6 |
| C8 S8 RCA 新类型与 v14 冲突 | **走 v16 治理拍板**：不直接覆盖 v14，需重新拍板 | v16 PLAN §3 C8 |
| C9 经验库入库规则 | **遵守**：`knowledge/public/experience/` 入库须人工审核；先入候选区 | v16 PLAN §3 #10 |
| C10 SPECIAL 变体与 v15 §A.1 框架重叠 | **合并**：v16 阶段 2 统一"变体化能力"框架（S3 + SPECIAL TC） | v16 PLAN §4 #8 |

---

## §2 v16 阶段 1（本周-2 周，P0 6 项）

### 2.1 任务清单

| ID | 任务 | 工作量 | 责任人 | 依赖 |
|---|---|---|---|---|
| T1 | #2 模块优先级矩阵落地 | 1-2 天 | LLM 主改 + 人工确认 | 无 |
| T2 | #4 L1 格式校验通用基类 + 7 阶段规则 | 3-5 天 | LLM 主改 + 人工抽检 | 复用 s5_exit_precheck.py |
| T3 | C5 红警阈值 20% 确认 | 0.5 天 | LLM 验证 SSOT | 无 |
| T4 | #1 S1 结构化评审包 + S2 消费 | 5-7 天 | LLM 主改 + 人工拍板 | C1 边界设计 |
| T5 | #3 related_tags + 双轨覆盖率 | 5-7 天 | LLM 主改 + 人工拍板 | C3 字段命名 + C5 双轨优先级 |
| T6 | #5 三级覆盖率深度定义（修订版：避开 S5 §FP 冲突） | 7-10 天 | LLM 主改 + 人工拍板 | 缺 L2 属性级机检方法定义 |

### 2.2 T1 — #2 模块优先级矩阵

**目标**：1-2 天内落地，解决归类优先级未定义问题

**输入**：
- `MODULES.md` §3.5（交叉场景判定决策树）
- v1.1 方案提议的 5 行冲突场景
- 测试架构师审核建议追加 3 行冲突（BIZ vs CONFIG / LOG vs BIZ-AUDIT_LOG / UI vs HINT）

**输出**：
- `MODULES.md` §3.5 末尾追加"冲突优先级矩阵"段（5+3 = 8 行场景）
- `STAGE_S5_TEST_POINTS.mdc` §1.5.2 "4 步判定 push" 末尾加"Step 2.5：命中冲突查优先级矩阵"
- `STAGE_S4_FLOWCHART.mdc` §1.5.2 "异常树叶子归属判定" 末尾加同样出口

**验收**：
- 8 行场景规则全部机检（每行 = 1 个 if-then 规则）
- 与现有 §3.5 决策树无矛盾
- 至少 2 个真实 Story 跨多模块时走优先级矩阵命中

**风险**：
- 模块冲突场景枚举不全——需结合 `test_points.json` 历史数据补查
- 优先级规则可能与现有交叉判定决策树重复——§1 风险已识别

### 2.3 T2 — #4 L1 格式校验通用基类

**目标**：3-5 天内抽出通用基类 + 7 个阶段规则

**输入**：
- `ai_workflow/s5_exit_precheck.py`（v14 §5 第二阶段第一项，2026-07-14 落地）
- `scripts/check_field_completion.py`（多阶段字段填写率）
- 各阶段 STAGE_*.mdc "输入审查" 节

**输出**：
- `ai_workflow/l1_format_validator.py`（通用基类，含 `run_l1_check(artifact_path, stage) -> dict`）
- 7 个阶段校验规则（每阶段 1 个校验器，引用基类）：
  - `validators/l1_s1.py`
  - `validators/l1_s2.py`
  - `validators/l1_s3.py`
  - `validators/l1_s4.py`
  - `validators/l1_s5.py`（从 s5_exit_precheck.py 抽出）
  - `validators/l1_s6.py`
  - `validators/l1_s7.py`

**L1 校验项**（4 类）：
1. **JSON 格式合法性**（try-except json.loads）
2. **必填字段完整性**（各阶段 schema 列出必填字段，缺失率 0%）
3. **ID 命名规范**（正则匹配，如 `TP-\d{3,}` / `TC-\d{3,}` / `OBJ-\d{3,}` / `FP-\d{3,}`）
4. **引用 ID 存在性**（TP 引用 s4_reference 必须存在 S4 叶子节点）

**验收**：
- `l1_format_validator.py` 通用基类可通过 `--self-test` 验证
- 7 个阶段校验规则全部跑通（用一个历史产物作为 fixture）
- L1 校验输出格式统一（dict: `{passed: bool, errors: [], warnings: [], summary: {}}`）

**风险**：
- 各阶段 schema 差异大，通用基类抽象成本高——若基类过于通用，可退化为"每阶段独立函数 + 共享工具函数"折中方案
- 历史产物作 fixture 需手动收集

### 2.4 T3 — C5 红警阈值 20% 确认

**目标**：0.5 天验证 SSOT

**输入**：
- `DESIGN_AND_EXECUTION_STANDARDS.mdc` §2.4.2

**输出**：
- 无文件改动（已为 0.20）
- 在 v16 PLAN.md §3 记录"已确认"

**验收**：
- `grep BYPASS_EXCEPTION_RATE_WARNING DESIGN_AND_EXECUTION_STANDARDS.mdc` 输出 `0.20`

**风险**：无

### 2.5 T4 — #1 S1 结构化评审包 + S2 消费

**目标**：5-7 天落地 S1 结构化产出 + S2 消费

**输入**：
- v1.1 方案 §3.1（review_structured.json 6 字段）
- 现有 S1 SKILL.md / STAGE_S1_REVIEW.mdc
- 现有 S1.5 exit_permission.json（5 个字段：can_proceed_to_s2 / quality_level / fallback_rules / s2_guidance / must_clarify_topics）

**输出**：
- `STAGE_S1_REVIEW.mdc` §1.5.4 新增"结构化评审包 Schema"段，列出 6 字段
- `aidocx-s1-review/SKILL.md` 输出契约增加 review_structured.json
- S2 SKILL 输入契约增加 review_structured.json 消费逻辑
- 新增 `review_structured.json` 示例文件（v16/example/ 目录）

**S1.5 边界设计（C1 解决）**：
- S1 评审产出 → review_structured.json（6 字段：requirement_quality / confirmed_boundaries / explicit_assumptions / risk_points_preview / missing_scenarios / final_requirement_text）
- S1.5 完善终版需求 → exit_permission.json（5 字段）
- **职责拆分**：S1 关注"识别问题"；S1.5 关注"问题回答 + 准出"
- S1.5 读取 S1 结构化包作为输入，特别是 must_clarify_topics 与 missing_scenarios

**验收**：
- 6 字段全部填写率 ≥ 90%（除非合理标注 is_assumed）
- S2 消费 review_structured.json 后 OBJ 边界定义与 S1 confirmed_boundaries 字符串相等率 ≥ 90%

**风险**：
- S1 vs S1.5 职责边界理解不一——需明确"评审"vs"澄清"的语义边界
- LLM 在 S1 阶段可能不产完整结构化字段——需 fallback 机制（v1.1 §3.2 提议 "S1 LLM 未填全 → 降级为字符串"）

### 2.6 T5 — #3 related_tags + 双轨覆盖率

**目标**：5-7 天落地 related_tags 字段 + 双轨统计

**输入**：
- v1.1 方案 §3.2（primary_module + related_tags + verification_points）
- 现有 TP JSON schema（含 module 字段）
- v15 §A.3 dashboard 维度（按 module 统计）

**字段命名方案（C3 解决）**：
- **保留 module**（不引入 primary_module，避免字段重复）
- **新增 related_tags**：数组，元素为模块名（CONFIG / UI / BIZ / AUX / LINK / LOG / SPECIAL / HINT）
- **新增 verification_points**：数组，元素为 fp_id 或 s4_leaf_id

**双轨不一致时优先级（C5 解决）**：
- 主模块（module）覆盖率 = TP 数 / 模块需求对象数
- 维度覆盖率 = 至少有一个 TP 的 related_tags 含该模块的需求对象数 / 该模块需求对象总数
- **不一致时以"维度覆盖率"为准**（更宽松，反映实际覆盖深度）

**双轨统计脚本**：
- 新增 `ai_workflow/coverage_dual_track.py`
- 输入：TP JSON + OBJ JSON
- 输出：双轨覆盖率 dict（`{"module_coverage": {...}, "dimension_coverage": {...}}`）

**验收**：
- TP JSON schema 增加 related_tags + verification_points 字段后，旧 TP 可平滑升级（默认 related_tags=[]）
- 双轨覆盖率数字差异 ≥ 10% 时打印 WEAK_OVERLAP 警告

**风险**：
- 双轨不一致业务解释困难——可能引出"覆盖率到底以哪个为准"的反复质疑
- 与 v15 defect_cluster.py 数据契约不一致——需在 v16 §3.2 §3.3 明确两者维度不同

### 2.7 T6 — #5 三级覆盖率深度定义（修订版）

**目标**：7-10 天落地三级覆盖率深度分级，避开 S5 §FP 覆盖率冲突

**输入**：
- v1.1 方案 §4（覆盖率三级深度定义）
- STAGE_S5_TEST_POINTS.mdc §FP 覆盖率门禁 `≥ 1.0`（100%）
- v15 §A.3 ASCII 柱图

**修订版三级覆盖率（C6 解决）**：

| 等级 | 含义 | 机检方法 | 阈值 |
|---|---|---|---|
| **L1 引用级** | OBJ/FP 被至少 1 个 TP 引用 | grep s4_reference / fp_linkage | ≥ 90% |
| **L2 属性级** | OBJ.feature_points 数组中的每个属性都有 ≥ 1 个 TP（按 OA 标签归类） | TP.test_point_type == OA_* + TP.factors 对齐 FP 属性 | ≥ 80%（P0）/ ≥ 60%（P1） |
| **L3 全面级** | OBJ 所有 EP/BOUNDARY/OA 子类都有 TP（≥ 18 种 test_point_type 覆盖率） | 按 test_point_type 分类统计 TP 数 | ≥ 70%（P0）/ ≥ 50%（P1） |

**与 S5 §FP 门禁冲突解决（C6）**：
- S5 §FP 门禁 `≥ 1.0`（100%）保留 = **L1 引用级硬门禁**
- L2/L3 软门禁 = **L2 报告值，不作硬门禁**
- L3 数字 = L3 报告值（含 18 种 test_point_type 覆盖率明细）

**输出**：
- `STAGE_S5_TEST_POINTS.mdc` §新增"三级覆盖率定义"段
- `STAGE_S7_REVIEW.mdc` §覆盖率报告增加 L1/L2/L3 三层明细
- 新增 `ai_workflow/coverage_l3.py`（L3 18 种类型统计脚本）

**验收**：
- P0 OBJ L2 ≥ 80%、L3 ≥ 70%（业务实际可达）
- 与 v15 §A.3 ASCII 柱图集成（L3 数字附加到柱图底部）

**风险**：
- L2 属性级机检方法依赖 FP.feature_points 字段——v15 阶段 1 任务④ BLOCKED，FP 数据不全，机检覆盖率可能偏低
- 阈值校准需真实数据——v16 §3 拍板 L2/L3 阈值时用 ≥ 1 个真实项目校准

---

## §3 v16 阶段 2（2-3 周，P1 3 项）

### 3.1 任务清单

| ID | 任务 | 工作量 | 依赖 |
|---|---|---|---|
| T7 | #6 L2/L3 门禁 + 黄金用例基准 | 5-7 天 | v15 阶段 1 任务④部分解锁（需 ≥ 1 个真实 S6 TC） |
| T8 | #7 S7 三层审查架构重构（L1 + L2 + L3） | 5-7 天 | T2 完成 + T7 部分完成 |
| T9 | C8 S8 RCA 新根因类型命名 | 3-5 天 | v16 治理拍板（不可在 #9 一并改） |

### 3.2 T7 — #6 L2/L3 门禁 + 黄金用例基准

**目标**：5-7 天落地黄金库 + 相似度比对

**输入**：
- v1.1 方案 §6（L2 覆盖率交叉校验 + L3 黄金用例相似度比对）
- v15 §A.2 用例价值 3 维评分（effectiveness × 0.5 + executability × 0.3 + independence × 0.2）

**输出**：
- `ai_workflow/golden_case_compare.py`（新）：embedding 余弦相似度比对脚本
- `knowledge/public/golden_cases/` 目录（候选区）：录入 20-30 条标杆用例（来源：游戏道具商城 v3.01 S6 TC）
- S7 SKILL.md §L3 审查部分用黄金库相似度评分
- `STAGE_S7_REVIEW.mdc` §覆盖率报告新增 L3 黄金相似度评分

**C7 解决（合并 v15 §A.2）**：
- v16 用例质量评分体系 = A2 3 维评分 × 0.6 + v1.1 L3 黄金相似度 × 0.4
- 验收：综合分 ≥ 0.7 为高质量 TC

**风险**：
- 黄金用例库来源不明——建议从 `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` 中人工精选 20-30 条
- embedding 集成需要外部依赖（sentence-transformers 等）——v16 阶段 2 决定是否引入

### 3.3 T8 — #7 S7 三层审查架构重构

**目标**：5-7 天重写 S7 审查架构

**输入**：
- v1.1 方案 §7（三层审查 L1/L2/L3）
- 现有 S7 SKILL.md §131-156 审查员 A/B

**输出**：
- `aidocx-s7-review/SKILL.md` §131-156 重写：
  - L1 脚本硬校验（用 T2 通用基类）
  - L2 脚本统计（覆盖率、双轨、不一致警告）
  - L3 LLM 审查（覆盖率深度 + 黄金库相似度 + 业务合理性）
- `STAGE_S7_REVIEW.mdc` §新增"三层审查"段

**验收**：
- L1 校验 0 错误才能进 L2
- L2 覆盖率明细全部填齐
- L3 LLM 审查报告含建议条数 ≥ 3

**风险**：
- 与 #6 黄金库依赖——T7 未完成时 L3 用 fallback 机制（仅 LLM 审查）
- L3 黄金相似度可能引入新依赖——见 T7 风险

### 3.4 T9 — C8 S8 RCA 新根因类型命名

**目标**：3-5 天重新拍板 S8 RCA 命名

**v14 现状**：
- v14 §A.2 已拍板 RCA type 7 类枚举（OMISSION / BOUNDARY_ERR / QUALITY_LOW / FIELD_MISSING / LINKAGE_BROKEN / RULE_VIOLATION / ID_NONCOMPLIANT）
- STAGE_S8_SELF_ITERATION.mdc §142-148 落地

**v1.1 提议新增 5 类**：
- RULE_MISSING / MODULE_MISCLASSIFY / EXEC_OMISSION / NAMING_MISLEAD / COVERAGE_GAP

**v16 治理拍板方案**：
- 在 v16 §3.4 决策表拍板：
  - RULE_MISSING → 并入 RULE_VIOLATION 子类（不独立枚举）
  - MODULE_MISCLASSIFY → 并入 QUALITY_LOW 子类
  - EXEC_OMISSION → 并入 OMISSION 子类
  - NAMING_MISLEAD → 并入 RULE_VIOLATION 子类
  - COVERAGE_GAP → **新增**（v14 未覆盖，需独立枚举）
- v16 后 RCA 8 类：OMISSION / BOUNDARY_ERR / QUALITY_LOW / FIELD_MISSING / LINKAGE_BROKEN / RULE_VIOLATION / ID_NONCOMPLIANT / COVERAGE_GAP

**风险**：
- v14 §A.2 是治理拍板的——v16 §3.4 拍板需走治理流程（不可在 #9 直接覆盖）
- 历史 S7 review_report.json 中 RCA.type 字段需重新归类——脚本改造

---

## §4 v16 阶段 3（3-4 周，P2 2 项）

### 4.1 任务清单

| ID | 任务 | 工作量 | 依赖 |
|---|---|---|---|
| T10 | #8 SPECIAL 变体用例机制（合并 v15 §A.1 变体化能力） | 10-14 天 | 真实 TC 数据 + 自动化框架 baseline |
| T11 | #9 + #10 S8 根因自动分流 + 全局经验库（合并 v15 §A.3 dashboard） | 10-14 天 | T9 RCA 命名 + v15 §A.3 ASCII 柱图 POC |

### 4.2 T10 — #8 SPECIAL 变体用例机制

**目标**：10-14 天落地变体用例

**C10 解决（合并 v15 §A.1 变体化能力）**：
- v16 阶段 3 统一规划"变体化能力框架"：
  - S3 侧：S3-lightweight（v15 §A.1 已实现 s3_mode_selector.py）
  - SPECIAL TC 侧：基例引用 + 差异点（v1.1 #8 提议）
  - 自动化框架侧：解析 step_deltas 操作语义（insert_after / replace / append）

**输出**：
- TC JSON schema 增加：`base_case_ref` / `variant_type` / `variant_conditions` / `step_deltas` / `expected_deltas` 字段
- `ai_workflow/variant_resolver.py`（新）：变体解析器
- `STAGE_S6_TEST_CASES.mdc` §新增"变体用例"段
- `v15/A1_enhanced_path_feasibility.md` §5 升级为"v16 变体化能力框架"

**验收**：
- 10 个 SPECIAL 场景（弱网购买 / 并发购买 / 支付超时）走变体机制后 TC 行数减少 ≥ 50%
- 自动化框架能解析 step_deltas 操作语义（人工测试 5 个样本）

**风险**：
- 变体用例的 QA 认知成本——人工跑测时需要先理解基例
- 与现有 TC JSON 不兼容——v16 阶段 3 给出迁移方案

### 4.3 T11 — #9 + #10 S8 根因自动分流 + 全局经验库

**目标**：10-14 天落地根因自动分流 + 全局经验库

**C8 解决（依赖 T9 完成）**：RCA 命名 8 类已拍板
**v15 §A.3 合并**：dashboard POC + ASCII 柱图 + 跨项目聚合

**输出**：
- `ai_workflow/rca_router.py`（新）：根因自动分流脚本（5 种 type → 5 种动作）
- `knowledge/public/experience/` 候选区（候选反例 / 命名库 / 执行经验）
- `STAGE_S8_SELF_ITERATION.mdc` §150-168 重写："自动闭环"段（替代原"待审候选区"）
- `ai_workflow/defect_cluster.py` 升级：与 dashboard ASCII 柱图集成

**自动分流 5 种动作**：
| RCA type | 动作 | 输出 |
|---|---|---|
| RULE_VIOLATION | 生成规则提案 | 写入 `knowledge/public/experience/candidates/rule_proposals/` |
| RULE_VIOLATION 子类 RULE_MISSING | 新增规则条目 | 写入 `MODULES.md` 或 STAGE_*.mdc 候选段 |
| MODULE_MISCLASSIFY | 写反例库 | 写入 `knowledge/public/experience/anti_patterns/module/` |
| NAMING_MISLEAD | 写反例库 | 写入 `knowledge/public/experience/anti_patterns/naming/` |
| COVERAGE_GAP | 触发 S5 补全建议 | 写入 S8 报告 `iteration.json` 补全建议段 |

**C9 解决（遵守入库规则）**：
- 经验库必须经人工审核后入正式区（MODULES §11.1 + DESIGN §0.1）
- v16 §3 阶段流程：脚本写入候选区 → 人工审核 → 移入正式区

**验收**：
- 经验库候选区每周 ≥ 1 条新候选
- dashboard ASCII 柱图能输出月度缺陷聚合图
- 根因自动分流准确率 ≥ 80%（人工抽检 10 个样本）

**风险**：
- LLM prompt 注入机制复杂——v16 §3 可能需要专门的"经验注入器"工具
- 入库审核可能拖慢进度——v16 §3 给出审核 SLA（候选区 → 正式区 ≤ 3 天）

---

## §5 v16 资源与依赖

### 5.1 依赖关系图

```
T1 (#2 模块优先级矩阵) ─┐
T3 (C5 红警确认) ──────┤
                       ├─→ T2 (#4 L1 基类) ─→ T4 (#1 S1 结构化) ─→ T5 (#3 related_tags) ─→ T6 (#5 三级覆盖率)
                       │                  ↓
                       │                  └─→ T8 (#7 S7 三层重构 L1/L2)
                       │
                       └─→ T7 (#6 黄金库 + L3 相似度) ─→ T8 (续, L3 部分)
                                          ↓
                                          └─→ T9 (C8 RCA 命名) ─→ T11 (#9 + #10 自动分流 + 经验库)
                                                               ↑
T10 (#8 SPECIAL 变体) ────────────────────────────────────────────┘ (共享依赖 v15 §A.1 变体化框架)
```

### 5.2 解锁 BLOCKED 项

v15 阶段 1 任务④ BLOCKED（无 S7 真实数据）→ 阻塞 T6 #5 / T7 #6 / T10 #8 / T11 #9
- v16 §3 阶段 1 任务：跑 ≥ 1 个真实项目完整 S1-S7 流程，解锁 BLOCKED

### 5.3 资源估算

| 阶段 | LLM 改动文件数 | 人工评审工作量 | 总工作量 |
|---|---|---|---|
| v16 阶段 1（T1-T6） | 约 15-20 个文件 | 8-10 次小拍板 | 2-3 周 |
| v16 阶段 2（T7-T9） | 约 8-10 个文件 | 5-7 次拍板 | 2-3 周 |
| v16 阶段 3（T10-T11） | 约 6-8 个文件 | 3-5 次拍板 | 3-4 周 |
| **v16 合计** | **约 30-38 个文件** | **16-22 次拍板** | **7-10 周** |

---

## §6 v16 拍板位（用户决策）

### Q4：v16 §3 阶段 1 任务的"BLOCKED 解锁"策略

v15 阶段 1 任务④ BLOCKED 阻塞 v16 阶段 1 中的 T6 #5。如何解锁？

| 选项 | 含义 | 建议 | **用户最终选择** |
|---|---|---|---|
| A | **用历史数据解锁**：从 `workflow_assets/游戏道具商城系统/v3.01/「S6 测试用例生成」/test_cases.json` 反推 S7 审查报告（不真实但可用） | 快但不真实 | — |
| B | **跑真实项目**：用 v16.1 跑一个新需求完整 S1-S7 流程，生成真实 S7 报告 | 慢但真实 | ✅ **B（2026-07-17 拍板）** |
| C | **混合**：A + B 并行——A 解锁 v16 阶段 1 推进，B 解锁 v16 阶段 2 | 推荐 | — |

**拍板后含义**：v16 阶段 1 不能立即启动——必须先跑 ≥ 1 个新需求完整 S1-S7 流程，生成真实 S7 review_report.json 后，才能解锁 T6 / T7 / T10 / T11。

### Q5：v16 §3 阶段 1 中 #5 三级覆盖率 L2/L3 阈值校准

L2 属性级 / L3 全面级阈值（P0 ≥ 80% / 70%）基于 v1.1 方案，无真实数据校准。

| 选项 | 含义 | 建议 | **用户最终选择** |
|---|---|---|---|
| A | **按 v1.1 原阈值**（P0 L2 ≥ 80% / L3 ≥ 70%） | 风险高——可能太高 | ✅ **A（2026-07-17 拍板）** |
| B | **先拍低阈值**（P0 L2 ≥ 60% / L3 ≥ 50%）后续校准 | 推荐 | — |
| C | **暂不设阈值**——v16 §3 阶段 1 仅产出"覆盖率明细报告"，v16 §3 阶段 2 用真实数据校准 | 最稳但慢 | — |

**拍板后含义**：L2 ≥ 80% / L3 ≥ 70% 阈值直接落地——若真实数据校准显示阈值过高（达成率 < 50%），触发 v16 §3 阶段 1 风险登记第 2 条（阈值校准），需走 v16 治理拍板调整。

### Q6：v16 §3.4 C8 RCA 新根因类型合并方案

v1.1 提议新增 5 类 RCA type，与 v14 已拍板冲突。建议合并方案：

| 选项 | 含义 | 建议 | **用户最终选择** |
|---|---|---|---|
| A | **5 类全并入现有 7 类**（仅 COVERAGE_GAP 新增）——v16 §3.4 已列 | 推荐（保守） | — |
| B | **5 类全新增**（不并入） | 激进——破坏 v14 治理拍板 | ✅ **B（2026-07-17 拍板）** |
| C | **3 类并入 + 2 类新增** | 中间方案 | — |

**拍板后含义**：
- RCA type 从 v14 拍板 7 类 → v16 拍板 12 类（7 + 5）
- 历史 S7 review_report.json 中 RCA.type 字段需重新归类（脚本改造）
- v14 §A.2 拍板结论**被推翻**——属于"用户拍板推翻历史拍板"，需在 v16 治理层走拍板决议记录（v16 §7.1 治理流程的"重大变更登记"步骤）

---

## §7 治理层与版本日志

### 7.1 治理流程

| 阶段 | 治理动作 |
|---|---|
| v16 启动 | 本 PLAN.md 落档 + 用户拍板 Q4/Q5/Q6 |
| v16 §3 阶段 1 推进 | 每完成 1 个 T 任务，登记到 `governance/design_iter/plans/v16/iteration_log.md` |
| v16 §3 阶段 2 推进 | 同上 |
| v16 §3 阶段 3 推进 | 同上 |
| v16 收尾 | 写 SELF_CHECK.md（含本版本已解决/新增/遗留三栏）+ INDEX.md 更新 |

### 7.2 风险登记

| 风险 | 影响范围 | 缓解 | 严重性 |
|---|---|---|---|
| **BLOCKED 未解锁（用户选 B = 跑真实项目）** → 阻塞 T6/T7/T10/T11 | v16 阶段 1-3 进度 | 先跑 ≥ 1 个新需求完整 S1-S7 解锁；预估 2-4 周前置 | 🔴 高 |
| **L2/L3 阈值采用 v1.1 原值（用户选 A）** | v16 §3 T6 落地 | 若真实数据校准达成率 < 50%，触发 v16 治理拍板调整 | 🟡 中 |
| **RCA 5 类全新增（用户选 B）推翻 v14 §A.2 拍板** | v16 §3.4 T9 + 历史数据迁移 | v16 §7.1 "重大变更登记"步骤；历史 RCA.type 重归类脚本 | 🟡 中 |
| 黄金用例库来源不明 | v16 §3 T7 | 人工精选 20-30 条（来源：游戏道具商城 v3.01 S6 TC）| 🟢 低 |
| v15 §A.3 dashboard 与 v1.1 经验库重叠 | v16 §3 T11 | 合并实现 | 🟢 低 |

### 7.3 版本日志

| 日期 | 事件 |
|---|---|
| 2026-07-17 | v1.1 迭代方案审核档落档（`current/v15_v1_1_iteration_audit.md`）|
| 2026-07-17 | 用户拍板：全部推进 + 开新独立迭代版本 v16 |
| 2026-07-17 | v16 PLAN.md 首版落档（本文件）|
| 2026-07-17 | 用户 Q4-Q6 拍板：B / A / B（与默认推荐 C/B/A 不同）|
| 2026-07-17 | v16 §3 阶段 1 启动条件：先跑 ≥ 1 个真实项目解锁 BLOCKED，再推 T1-T6 |

---

## §8 自我引用（避免重复审核）

| 节 | 引用的 v1.1 / v15 / STAGE 文件 | 已 Read 验证 |
|---|---|---|
| §0 | 用户对话拍板 | ✅ |
| §1.1 P0 | `current/v15_v1_1_iteration_audit.md` §2 逐条审核 | ✅ |
| §1.2 P1 | `current/v15_v1_1_iteration_audit.md` §2 #6/#7/C8 | ✅ |
| §1.3 P2 | `current/v15_v1_1_iteration_audit.md` §2 #8/#9/#10 | ✅ |
| §1.4 冲突 | `current/v15_v1_1_iteration_audit.md` §3 C1-C10 | ✅ |
| §2.2 T1 | `MODULES.md` §3.5 + STAGE_S5_TEST_POINTS.mdc §1.5.2 | ✅ |
| §2.3 T2 | `ai_workflow/s5_exit_precheck.py` + `scripts/check_field_completion.py` | ✅ |
| §2.5 T4 | v1.1 方案 §3.1 + S1 SKILL.md + S1.5 exit_permission.json | ✅ |
| §2.6 T5 | v1.1 方案 §3.2 + v15 §A.3 dashboard | ✅ |
| §2.7 T6 | v1.1 方案 §4 + STAGE_S5 §FP 门禁 | ✅ |
| §3.2 T7 | v1.1 方案 §6 + v15 §A.2 用例价值 | ✅ |
| §3.3 T8 | v1.1 方案 §7 + S7 SKILL.md §131-156 | ✅ |
| §3.4 T9 | v14 §A.2 RCA 7 类 + STAGE_S8 §142-148 | ✅ |
| §4.2 T10 | v1.1 方案 §8 + v15 §A.1 S3 增强路径 | ✅ |
| §4.3 T11 | v1.1 方案 §9 + v15 §A.3 + MODULES §11.1 | ✅ |

---

*由 AIDocxWorkFlow 测试架构师治理模式生成*
*本 PLAN.md 为决策辅助，最终推进方案由用户拍板*