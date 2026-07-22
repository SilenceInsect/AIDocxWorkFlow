# q_decision_table — 固定决策：阶段开始前询问是否删除旧产物

> **触发**：用户 2026-07-10 /aidocx-workflow-conversation 指令
> 「@resource/游戏道具商城系统/v3.01_raw.docx 增加固定决策：开始之前请问我是否删除旧产物」
>
> **目标**：把"阶段开始前询问是否删除旧产物"固化为 run_stage / run_pipeline 的固定行为，不再每次口头约定。
>
> **SSOT 范围**：本表只列决策点 + 落档位置；具体改动在用户点头后落到对应规则文件。

---

## 0. 现状事实（先验）

| 项 | 事实 |
|---|---|
| 资源文件 | `resource/游戏道具商城系统/v3.01_raw.docx`（42880 B, Jul 9 22:53） |
| 现有产物 | `workflow_assets/游戏道具商城系统/v3.01/「S1 需求评审」/raw/` 仅 2 个文件（`extracted_text.md` + `image_index.json`，Jul 10 00:50） |
| 其他阶段 | S2~S8 目录**均不存在**（v3.01 是新版本，未跑全流程） |
| 编排入口 | `ai_workflow.conversation_skills.run_stage()` / `run_pipeline()`（v4 唯一推荐入口） |
| 当前行为 | 不询问，直接覆盖；旧产物与新产物并存时无提示 |
| DNA §9.4 | 已先 Read 关键文件（conversation_skills.py / v8 PLAN.md / open_questions.md / stage_gatekeeper.py） |

---

## 1. 决策点（待用户点头）

### 决策 1：固定决策的**作用范围**

| 候选 | 描述 | 影响 |
|---|---|---|
| **A（推荐）** | 只在 `run_stage()` 单阶段入口插入询问 | 改动 1 个函数，最小侵入 |
| B | `run_stage()` + `run_pipeline()` 都插入 | 改动 2 个函数；run_pipeline 调用 run_stage，A 已覆盖大部分场景 |
| C | 同步加在 S1 `stage_s1_input/pipeline.py` 入口 + `run_stage()` | 改动 3 处，但 S1 子模块已被 run_stage 包裹，本质重复 |

**推荐 A 理由**：run_pipeline 内部循环调用 run_stage，A 已覆盖 100% 实际路径；B/C 是过度收敛。

### 决策 2：询问的**时机**

| 候选 | 描述 |
|---|---|
| **A（推荐）** | preflight **之前**（run_stage 第 1 步前），扫到阶段目录存在 → 询问 |
| B | preflight **之后**、stage_callable 之前 |
| C | stage_callable 执行完、postflight 之前 |

**推荐 A 理由**：
- B/C 已经进入 gate 检查，删除旧产物会触发"preflight 失败"无意义开销
- A 是真正"开始之前"——符合用户原话"开始之前请问我"

### 决策 3：询问的**触发条件**

| 候选 | 描述 |
|---|---|
| **A（推荐）** | 阶段目录**存在且非空**（`stage_dir.exists() and any(stage_dir.iterdir())`） |
| B | 阶段目录存在即触发（即使空目录） |
| C | 永远触发（每次都问） |

**推荐 A 理由**：
- C 太啰嗦（v3.0 全新跑每次都问，用户疲劳）
- B 对空目录问"是否删除空目录"语义弱
- A 命中"有旧产物 → 真要删吗？"的语义

### 决策 4：询问的**内容粒度**

| 候选 | 描述 |
|---|---|
| **A（推荐）** | 按用户原话：1 个二元选项（删除旧产物 / 保留旧产物，跳过该阶段） |
| B | 三元选项（删除 / 保留 / mv 到 backup 子目录） |
| C | 四元选项（删除 / 保留 / mv / abort 整个 pipeline） |

**推荐 A 理由**：
- 用户原话就是"请问我是否删除旧产物"——二元即"是否"
- B/C 属于过度设计（"backup 子目录"违反 `workflow_assets/` 默认不入 git 原则——本来就不需要 backup）
- A 选项保留"跳过该阶段"语义合理（旧产物在，不覆盖，继续执行）

### 决策 5：用户回答"删除"后的**删除范围**

| 候选 | 描述 | 风险 |
|---|---|---|
| **A（推荐）** | `shutil.rmtree(stage_dir)` 整个目录（含 raw/ + 历史产物 + ledger） | 一次性清理 |
| B | 只删 `*.json / *.md` 等产物文件，保留目录结构 | 旧 ledger 残留干扰 S7 审查 |
| C | 只删最新一轮产物，保留 raw（来源材料不可重建） | raw 是 S1 输入，删除会让 S1 失效 |

**推荐 A 理由**：
- raw 也在工作流产物目录下（非 resource/）；删除会强制 S1 重抽 raw——这是设计意图（旧 raw 可能来自旧版 v3.01 raw 文档）
- B 留 ledger 残留，会被 preflight gate 误判
- C 与 A 效果接近，但 A 更简单
- **⚠️ 重要**：resource/<req_name>/<version>_raw.docx（gitignore 区）**绝不删除**——只是产物目录

### 决策 6：用户回答"保留"后的**行为**

| 候选 | 描述 |
|---|---|
| **A（推荐）** | 跳过该阶段（返回 status=SKIPPED，halt_reason="user_chose_keep_existing"） |
| B | 继续执行（覆盖旧产物，违背用户意愿） |
| C | 报错退出（用户没说要 exit） |

**推荐 A 理由**：
- 用户主动说"保留"= "这次不重跑这个阶段"
- B 违背意愿；C 过度反应
- 与 run_pipeline 的 SKIPPED 语义对齐（§5 状态枚举已有）

### 决策 7：约束文档**落档位置**

| 候选 | 位置 |
|---|---|
| **A（推荐）** | `ai_workflow/conversation_skills.py`（实现层 SSOT，run_stage 函数本身） |
| B | `.cursor/skills/aidocx-workflow-conversation/SKILL.md`（skill 文档） |
| C | A + B（实现 + skill 文档同步） |

**推荐 C 理由**：
- A 是真实生效点
- B 是 Agent / 人阅读入口，必须同步说明
- DNA §3 约束 vs 实现 vs 知识：A 是实现（可动）；B 是 skill 约束（必先 ask）

### 决策 8：是否需要**环境变量**全局开关

| 候选 | 描述 |
|---|---|
| **A（推荐）** | 默认开启询问；环境变量 `AIDOCX_PURGE_PROMPT=never` 时跳过询问（直接覆盖） |
| B | 默认关闭；环境变量 `AIDOCX_PURGE_PROMPT=always` 时开启询问 |
| C | 无环境变量，纯交互 |

**推荐 A 理由**：
- 默认开启询问 = 安全默认（DNA 准则 4：人本可审查）
- 自动化场景（CI / 批处理）可显式设 `never` 跳过
- 与 AIDOCX_INCLUDE_S2_5 风格一致（v4 已有先例）

### 决策 9：删除前的**确认信息展示**

| 候选 | 描述 |
|---|---|
| **A（推荐）** | 列出 `stage_dir` 下所有文件 + 总大小 + 最后修改时间 + 阶段名 |
| B | 只显示"目录存在" |
| C | 不显示任何信息，直接问 |

**推荐 A 理由**：DNA 准则 4（人本可审查）——删除前必须让用户看见具体是什么；防止误删。

### 决策 10：**是否同步改 v8 方案档**

| 候选 | 描述 |
|---|---|
| A | 改 v8 PLAN.md 加 §3.4 "新增固定决策"段 |
| B | 写入 v9 启动议题（不动 v8） |
| **C（推荐）** | v8 PLAN.md 加 §3.4 短段（v8 实战发现即写） |

**推荐 C 理由**：v8 PLAN.md §3 已预留"v8 实战发现 → v9 决策"模式；本次也是 v8 实战发现；但本决策属于"代码层固定决策"非"目录主轴"，应在 v8 范围。

---

## 2. 改动清单（用户点头后落地）

| # | 文件 | 改动 | 类型 |
|---|---|---|---|
| 1 | `ai_workflow/conversation_skills.py` | `run_stage()` 函数顶部插入 `_prompt_purge_existing()` 调用 | 实现（可动） |
| 2 | `ai_workflow/conversation_skills.py` | 新增 `_prompt_purge_existing(stage, req_name, version, project_name) -> str` 函数（扫描 + 询问 + rmtree/skip） | 实现 |
| 3 | `.cursor/skills/aidocx-workflow-conversation/SKILL.md` | §2 单阶段入口段后插入"purge 询问行为"说明 | skill 约束（必先 ask） |
| 4 | `governance/design_iter/plans/v8/PLAN.md` | §3.4 新增"v8 实战发现 — 固定 purge 决策" | 知识（直接动） |
| 5 | `CHANGELOG.md` | 顶部 [v8] 段追加"固定 purge 决策"条目 | 知识（直接动） |
| 6 | `governance/design_iter/current/open_questions.md` | 不新增（本决策闭环，无遗留） | 知识 |

**触发 §9.1.1 self-test 豁免**？——不适用，因为改动含业务函数 `_prompt_purge_existing` 签名新增。

**是否触发 §9.1 红线**？——文件改动数 = 6 > 3 ⚠️ → 本表即为决策表，用户点头后按"先答后动"逐项推进。

---

## 3. 落档协议执行记录

**用户决策收集**（AskQuestion 一次性 5 项）：

| 决策 | 采纳 |
|---|---|
| 作用范围 | C — run_stage + run_pipeline + S1 子模块入口（run_pipeline 通过 run_stage 内部 SKIPPED 传递） |
| 触发条件 | A — 阶段目录存在且非空 |
| 删除范围 | A — rmtree 整个阶段目录 |
| 环境变量 | C — 无环境变量，纯交互（非 TTY 自动走 auto_keep） |
| 落地范围 | A — 代码 + SKILL 同步 |

**实际改动文件清单**（6 个）：

| # | 文件 | 改动 |
|---|---|---|
| 1 | `ai_workflow/conversation_skills.py` | 新增 `_resolve_stage_path()` / `_list_stage_artifacts()` / `_format_size()` / `_prompt_purge_existing()` / `_purge_decision_to_skip_result()` 共 5 个函数（~180 行）；`run_stage()` 入口插入 purge 询问（preflight 之前） |
| 2 | `ai_workflow/stage_s1_input/pipeline.py` | `run_s1_pipeline()` 入口插入 purge 询问 |
| 3 | `.cursor/skills/aidocx-workflow-conversation/SKILL.md §2` | 新增"阶段开始前：旧产物清理询问"段，含 banner 示意 + 4 行决策表 + 4 行理由 |
| 4 | `governance/design_iter/plans/v8/PLAN.md §3.4` | 新增"v8 实战发现 — 固定 purge 决策"段（30 行） |
| 5 | `CHANGELOG.md [v8]` | 追加"v8 实战补丁 — 固定 purge 决策"段（含 banner + 兼容性说明） |
| 6 | `governance/design_iter/current/q_decision_table.md` | **本档**（决策表已落档） |

**验证记录**：

- ✅ `python3 -m py_compile` 2 个改动 Python 文件全部通过
- ✅ 8 项 self-test 通过（auto_keep / keep / purge / abort / empty input / list / skip result / non-TTY fallback）
- ✅ `_prompt_purge_existing()` 在 v3.01 S1 真实目录上跑过：list 出 `raw/extracted_text.md` + `raw/image_index.json` 共 2 个文件 / 5.3 KB
- ✅ purge 后 `auto_keep` 行为：目录不存在时自动 skip

**修复记录**（v6.3 SOP 实战）：

- 初版 `_resolve_stage_path()` 调用本地 `_stage_dir()` → 走了 v7 旧主轴（先阶段再版本）
- 修复：直接按 v8 规范拼路径 `WF / req_name / version / stage_dir_name`
- 根因：本地 `_stage_dir()` 函数（行 24-36）仍按 v7 模式拼——它是给 `make_stageX_skill` 用的，不应被 `_prompt_purge_existing` 复用

**触发 §9.1.1 self-test 豁免**？——否，因为 `_prompt_purge_existing` 是新增业务函数（非单纯 self-test 包装）。

**触发 §9.1 红线**？——文件改动数 = 6 > 3 ⚠️ → 本表即为决策表，用户点头后按"先答后动"逐项推进。

**没改的（避免过度收敛）**：

- `run_pipeline()` 不直接插 purge 询问（依赖 `run_stage` 内部 SKIPPED 自然传递；run_pipeline 本质是循环 run_stage）
- `_stage_dir()` 旧主轴函数（保留给 `make_stageX_skill` 使用，不与新主轴混用）
- `stage_gatekeeper.run_preflight_gate()` 不插入（purge 必须在 preflight **之前**，否则会先扫到错误状态）

---

## v13 — 工作流产品说明书 + SSOT 修复（2026-07-10）

**触发**：`整理并且审查整个流程，落地成一份工作流产品说明书`

### v13 执行决策表

| # | 决策点 | 选择 |
|---|--------|------|
| v13-01 | 产品说明书落档路径 | `governance/design_iter/current/PRODUCT_MANUAL.md` |
| v13-02 | 说明书覆盖范围 | 9 阶段（S1~S8+S1.5）+ 8 模块 + 全局约束 + 7 项不一致修复 |
| v13-03 | SSOT 修复范围 | 批量全部 7 项 |
| v13-04 | SSOT 修复路径 | §2.3 补 S3/S4 + §4.3 删 S7 旧值补 FP 覆盖率 + MODULES §4.5 去重 |

### v13 产出文件

| # | 文件 | 性质 |
|---|------|------|
| 1 | `governance/design_iter/current/PRODUCT_MANUAL.md` | 新建（产品说明书 SSOT，~500 行）|
| 2 | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | 修改（§2.3 + §4.3 修复 4 项不一致）|
| 3 | `.cursor/MODULES.md` | 修改（§4.5 去重）|
| 4 | `governance/design_iter/current/open_questions.md` | 修改（追加 v13 闭环记录）|
| 5 | `governance/design_iter/current/q_decision_table.md` | 修改（追加 v13 决策记录）|

### v13 SSOT 修复明细

**修复 1**：DESIGN_AND_EXECUTION_STANDARDS.mdc §2.3 补 S3/S4 门禁 + S7 标注废除
**修复 2**：同上，§2.3 补 S4_ANOMALY_COVERAGE 映射
**修复 3**：同上，§4.3 补 S5_OBJ/S5_FP/S5_S3_REF/S5_S4_REF_COVERAGE = 1.0
**修复 4**：同上，§4.3 删 S7_COVERAGE_THRESHOLD/S7_STRUCTURE_THRESHOLD + 加废除标注
**修复 5**：MODULES.md §4.5 删除"枚举值与子类映射"表，枚举信息并入"概览表"标题
**修复 6**：SKILL 路径无需修复（.cursor/引用正确，.agents/不存在，无冲突）
**修复 7**：PRODUCT_MANUAL.md §5.1 补全 `fail_report_S7.md` 路径

### v13 说明书结构

```
PRODUCT_MANUAL.md
 §1 项目定位（与 README 关系）
 §2 9 阶段流水线（S1~S8+S1.5 含入口/物料/产出/门禁）
 §3 8 模块系统（边界+子类统计）
 §4 全局约束与质量门禁（SSOT §2.3+§4.3）
 §5 输入输出规范（含目录结构 v8+）
 §6 版本与目录规范
 §7 附录（模板/示例/FAQ + 7 项不一致修复记录）
```