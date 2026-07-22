# AIDocxWorkFlow 各阶段产出标准

> **角色定义**：资深游戏测试工程师视角下的阶段审查标准
>
> **适用场景**：规范 AIDocxWorkFlow S1~S8 各阶段必须产出的文件、内容要求、验收方式
>
> **Git 分类铁律**：workflow_assets 目录下所有产物为**过程资产**，默认不入 Git；knowledge/public/ 为**公共知识库**，可入 Git

---

## 角色定义

### 资深游戏测试工程师视角

作为资深游戏测试工程师，审查各阶段产出时关注：

| 维度 | 关注点 |
|------|---------|
| **可测试性** | 需求是否有明确通过/失败条件 |
| **覆盖完整性** | 是否覆盖正常/异常/边界/并发场景 |
| **场景边界** | 是否有清晰的边界值定义 |
| **优先级合理性** | P0/P1/P2 分级是否符合业务风险 |
| **可追溯性** | 从 Epic→Story→OBJ→FP→TP→TC 链路是否完整 |

---

## S1 需求评审

### 任务目标

对需求文档进行 **5维度评审**，识别需求问题、评估可测试性、输出澄清清单。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `review_report.md` | `workflow_assets/<req_name>/<version>/「S1 需求评审」/` | 5维度评分报告 |
| `review_report.json` | 同上 | 结构化评分数据 |
| `role_definitions.md` | 同上 | 角色定义（主/次/边界三类） |
| `requirement_objects.md` | 同上 | 需求对象拆解（评审视角 Markdown） |
| `终版需求.md` | 同上 | AI整理后的需求草稿 |
| `clarification_checklist.md` | 同上 | 待确认问题清单（P0/P1/P2三级） |
| `review_issues.md` | 同上 | 需求评审问题记录表 |
| `edge_cases.md` | 同上 | 需求边界异常场景清单 |
| `testability_assessment.md` | 同上 | 需求可测性评估报告 |

### 产出标准

| 文件 | 验收要点 |
|------|----------|
| `review_report.md` | 包含5维度评分表（完整性25%/清晰度25%/一致性20%/可测试性20%/可行性10%），总分≥7.0 PASS |
| `role_definitions.md` | 角色按"主/次/边界"分类，每类有典型场景 |
| `requirement_objects.md` | 功能×业务故事 1:1配对，100%覆盖率 |
| `clarification_checklist.md` | 含"问题需求"节，P0/P1/P2分级，SPECIAL_FLAG列标注强付费项 |
| `review_issues.md` | 含角色同步问题、需求对象问题、功能/数据流问题三节 |
| `edge_cases.md` | 含边界条件、异常流程、并发/竞态、数据边界四类场景 |
| `testability_assessment.md` | 含可观测性、可控制性、可自动化程度、测试盲区四维评估 |

### 验收方式

| 总分区间 | 判决 | 后续动作 |
|----------|------|----------|
| ≥ 7.0 | **PASS** | 生成终版需求.md → 触发S1.5业务澄清 |
| 4.0 - 6.9 | **NEEDS_REVISION** | 输出修改建议，等待修订后重审 |
| < 4.0 | **REJECT** | 触发三步自问论证放行 |

---

## S1.5 业务澄清与准出

### 任务目标

**策划/需求方对S1 AI评审结论的复核与定调**——S1找出的问题必须由人工给出处理方案。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `终版需求.md`（更新版） | `workflow_assets/<req_name>/<version>/「S1 需求评审」/` | 基于人工反馈完善的终版需求 |
| `exit_permission.json` | 同上 | 准出许可（can_proceed_to_s2=true/false） |
| `clarification_checklist.md`（更新） | 同上 | 状态更新为"已处理" |

### 产出标准

| 文件 | 验收要点 |
|------|----------|
| `exit_permission.json` | 含can_proceed_to_s2、quality_level(HIGH/MEDIUM/LOW)、items_filled统计、strong_purchase_p0_resolved |
| `终版需求.md` | 补充缺失业务规则、修正歧义、更新待确认项状态 |

### 验收方式

| 场景 | 验收结果 |
|------|----------|
| P0 100%填写 | can_proceed_to_s2=true |
| P0 未填完 | can_proceed_to_s2=false，生成fail_report_S1_5.md |
| 强付费项P0未答完 | 与P0缺失同等处理 |

> 注：S1.5 阶段允许 LLM 补齐 P0 答案（is_assumed 字段），由人工审核确认。

---

## S2 需求拆解

### 任务目标

**对内加工**：将S1.5澄清后的定稿需求，拆解为可测试、可排期、可落地的测试基线文档。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `backlog.md` | `workflow_assets/<req_name>/<version>/「S2 需求拆解」/` | Epic/Story总览 |
| `backlog.json` | 同上 | 结构化数据（供S5/S6消费） |
| `requirement_objects.md` | 同上 | 需求对象详细分解（Markdown） |
| `requirement_objects.json` | 同上 | 需求对象JSON（含Epic/Story/OBJ/FP四层） |

### 产出标准

| 文件 | 验收要点 |
|------|----------|
| `backlog.json` | 含五层结构：Release→Epic→Story→Object→FP，每层ID格式正确 |
| `requirement_objects.json` | OBJ含9字段（obj_name/belong_module/scene/input/normal_flow/exception_flow/data_change/output_display/verify_method） |
| `requirement_objects.json` | FP含4字段（fp_id/fp_name/fp_desc/check_type），禁止fp_count |
| `backlog.json` | summary.feature_point_count == Σ各Object.feature_points.length（物量守恒） |

### 验收方式

| 检查项 | 要求 | 缺失时 |
|--------|------|--------|
| exit_permission.json | 存在且can_proceed_to_s2=true | fail_report_S2.md |
| Epic数量 | ≥1 | fail_report_S2.md |
| Story acceptance_criteria | 每Story≥2条，区分三类验收 | 补充提示 |
| OBJ 9字段 | 完整无缺 | 标注缺失项 |
| 物量守恒 | feature_point_count==ΣFPs | 触发三步自问 |

---

## S2.5 迭代规划

> ⚠️ **可选阶段**：全流程模式默认跳过（opt-in），对S5/S6产出数量/质量无强关系

### 任务目标

解决**开发节奏/资源/排期**问题，生成团队可执行的迭代计划。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `project_config.json` | `workflow_assets/<req_name>/<version>/「S2.5 迭代规划」/` | 项目配置参数 |
| `iteration_plan.md` | 同上 | 迭代规划报告（Markdown） |
| `iteration_plan.json` | 同上 | 迭代规划数据 |

### 产出标准

| 文件 | 验收要点 |
|------|----------|
| `project_config.json` | 10项必填字段全齐（req_name/version/schedule_start/schedule_end/team等） |
| `iteration_plan.md` | 含7步：负载平衡/任务确认/启动会/任务录入/资源锁定/并行工作/执行跟进 |

### 验收方式

| 检查项 | 要求 |
|--------|------|
| project_config.json | 全部字段填写 |
| 有Epic优先级 | 必须 |
| 有Task拆解 | 建议有（缺失自动生成简化版） |

---

## S3 原型导出

### 任务目标

为S5/S6生成测试用例提供**UI节点锚点**——每个Story对应页面原型和导航关系。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `prototype.md` | `workflow_assets/<req_name>/<version>/「S3 原型导出」/` | 页面原型+Mermaid页面流图 |

### 产出标准

| 文件 | 验收要点 |
|------|----------|
| `prototype.md` | 每Story有页面名称、关键UI元素、布局描述、状态变化 |
| `prototype.md` | 每个Epic至少1个完整Mermaid页面流图 |
| 页面节点ID | 格式`PAGE-{EpicID}-{NN}`（如PAGE-EPIC-1-01） |

### 验收方式

| 检查项 | 要求 |
|--------|------|
| backlog.md | 存在且含Epic/Story |
| Epic数量 | ≥1 |
| Story有acceptance_criteria | 允许为空但标注 |

---

## S4 流程图导出

### 任务目标

为S5测试点生成提供**异常路径来源**——每个Epic产出4类产出：Flowchart+Sequence+异常决策树+风险点清单。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `business_flow.md` | `workflow_assets/<req_name>/<version>/「S4 流程图导出」/` | 业务流程图+时序图+异常决策树+风险点清单 |

### 产出标准

| 文件 | 验收要点 |
|------|----------|
| `business_flow.md` | 每个Epic有4类产出：Flowchart+Sequence+异常决策树+风险点清单 |
| 风险点ID | 格式`R-NNN`（全局唯一）或`R-{EpicID}-NN` |
| 异常树叶节点ID | 格式`S4-{EpicID}-{seq}.{N}`（唯一） |
| 风险点→异常树叶 | 每条风险点至少指向1个异常树叶 |

### 验收方式

| 检查项 | 阈值 |
|--------|------|
| 每Epic有4类产出 | 100% |
| 风险点ID全局唯一 | 100% |
| 异常树叶节点ID唯一 | 100% |
| Mermaid语法合法 | 100% |

---

## S5 测试点生成

### 任务目标

为每个Story生成**高质量测试点**，覆盖需求对象、功能点和关键场景族。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `test_points.json` | `workflow_assets/<req_name>/<version>/「S5 测试点生成」/` | 测试点JSON |
| `coverage_ledger.json` | 同上 | 覆盖账本（按Story记录覆盖状态） |
| `omission_ledger.json` | 同上 | 遗漏账本（未覆盖点及原因） |

### 产出标准

| 字段 | 验收要点 |
|------|----------|
| tp_id | 格式`{StoryID}-TP-{3位序号}` |
| module | 8模块之一（CONFIG/UI/BIZ/AUX/LINK/SPECIAL/LOG/HINT） |
| test_point_type | 4类型之一（POSITIVE/BOUNDARY/NEGATIVE/EXCEPTION等） |
| s4_reference | 必须填写，引用S4风险点或异常树叶 |
| feature_point_ref | 强制必填，引用S2 OBJ.feature_points[].id |
| applies_rule | 说明4步判定+反例对照结果 |

### 验收方式

| 指标 | 要求 |
|------|------|
| 每Story TP数 | ≥6（指导值，按业务风险灵活调整） |
| OBJ覆盖率 | 100% |
| FP覆盖率 | 100% |
| 10类场景族覆盖 | 每个Story至少扫描positive/boundary/negative/exception/config_change/permission_role/state_transition/concurrency_timing/recovery_rollback/observability_hint_log |
| feature_point_ref | 100%填写 |

---

## S6 测试用例生成

### 任务目标

基于S5测试点，推理生成**可执行的测试用例**。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `test_cases.json` | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/` | 公共默认测试用例JSON |
| `test_cases.xlsx` | 同上 | 公共默认测试用例Excel |
| `coverage_ledger.json` | 同上 | 覆盖账本 |
| `omission_ledger.json` | 同上 | 遗漏账本 |

### 产出标准

| 字段 | 验收要点 |
|------|----------|
| case_id | 格式`{Module}-TC-{NNN}` |
| 用例描述 | 来自S2 backlog.epics[].title，100%原样 |
| 功能描述 | 来自S2 backlog.stories[].title，100%原样 |
| 前置条件 | 含具体数值，禁止模糊描述 |
| 操作步骤 | 每步含具体UI元素名或数值，禁止模板语言 |
| 预期结果 | 纯业务结果，禁止S4节点引用 |
| obj_id | 来自S2 requirement_object.id |
| feature_point_id | 来自S2 OBJ.feature_points[].id |
| s5_ref | 引用S5 tp_id |

### 验收方式

| 指标 | 要求 |
|------|------|
| JSON+Excel同时生成 | 缺一则不合格 |
| case_id格式 | 100%符合`{Module}-TC-{NNN}` |
| 字段填写率 | ≥90% |
| OBJ覆盖率 | 100% |
| FP覆盖率 | 100% |
| L1∧L2双门禁 | 通过后写Ready，否则Draft |

---

## S7 用例审查

### 任务目标

双审查员审计S6产出的测试用例：**结构完整性+覆盖率**，脚本输出数字，LLM按业务实际写建议。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `review_report.md` | `workflow_assets/<req_name>/<version>/「S6 测试用例生成」/` | 审查报告（Markdown） |
| `review_report.json` | 同上 | 审查报告（JSON） |

### 产出标准

| 审查员 | 检查项 |
|--------|--------|
| 审查员A | ID规范化率、字段填写率、模块归一化率、字段名合规、跨模块边界、步骤质量、预期可验证性 |
| 审查员B | S4风险点引用率、S4异常树叶引用率、is_assumed填充率、s4_reference填充率、applies_rule填充率 |

### 验收方式

| 三类建议 | 定义 |
|----------|------|
| **必修** | 不补充会引发线上bug或严重漏测 |
| **应改** | 不修改会导致测试盲区 |
| **可改** | 完善用例但优先级低 |

> ⚠️ **无硬阈值**：S7不设PASS/FAIL硬判决，脚本输出数字，LLM按业务实际判断

---

## S8 自迭代

### 任务目标

从S4→S5→S6→S7链路推理**根因**，产出缺陷模式分析和Prompt改进建议，**强制归档经验**。

### 产出清单（必须产出）

| 文件 | 路径 | 说明 |
|------|------|------|
| `iteration.md` | `workflow_assets/<req_name>/<version>/「S8 自迭代」/` | 自迭代报告（Markdown） |
| `iteration.json` | 同上 | 自迭代数据（含根因链路图） |

### 产出标准

| 产出 | 验收要点 |
|------|----------|
| 根因追溯 | 每缺陷回答4问：根因来源/断裂环节/受影响阶段/修复动作 |
| 根因来源 | 8类之一（S4_PROVIDE/S4_NAME/S5_RULE/S5_EXEC/S5_MODULE/S2_OBJ/S2_RULE/S6_EXEC） |
| 缺陷模式统计 | 按模块×类型统计出现频次 |
| 归档 | 写入knowledge/project_local/.review_queue/（不直接改公共库） |

### 验收方式

| 检查项 | 要求 |
|--------|------|
| 4问追溯 | 每缺陷必须回答4问，空答则禁止输出 |
| 归档 | S5_MODULE/S5_EXEC/S6_EXEC根因必须归档到待审候选区 |
| rca字段 | stage/type/clause必须来自标准化映射表 |

---

## 附录：阶段间追溯链路

```
S1 评审报告 ──────────────────────→ S1.5 澄清 ──────────────────────→ S2 拆解
     ↓ 角色/问题/边界                    ↓ P0答案/处理方案                    ↓ Epic/Story/OBJ/FP
     ↓                                                                               ↓
S3 原型 ───────────────────────────────────────────────────────────────────→ S5 TP
  ↓ PAGE节点ID                                                                      ↓ feature_point_ref
  ↓                                                                                 ↓
S4 流程图 ──────────────────────────────────────────────────────────────────→ S5 TP
  ↓ R-NNN/异常树叶ID                                                               ↓ s4_reference
  ↓                                                                                 ↓
S6 TC ──────────────────────────────────────────────────────────────────────→ S7 审查
  ↓ s5_ref/obj_id/feature_point_id                                                ↓ 根因追溯
  ↓                                                                                 ↓
S8 自迭代（经验归档）
```

---

## 核心验收原则

| 原则 | 说明 |
|------|------|
| **覆盖优先** | S5/S6默认目标不是少写，而是找全 |
| **账本驱动** | coverage_ledger + omission_ledger 是必须产出 |
| **无硬阈值** | S7/S8不设PASS/FAIL，由LLM按业务实际判断 |
| **归档经验** | S8经验先写入待审候选区，不直接改公共库 |
| **跨阶段追溯** | tp_id→s5_ref→obj_id→feature_point_id链路必须完整 |
