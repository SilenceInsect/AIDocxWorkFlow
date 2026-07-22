# AIDocxWorkFlow 方案 v4：需求转用例主线强化 + 运行时硬约束闭环

> **本方案 = 针对内网训练阶段暴露的 3 类严重问题的系统性整改草案**。
> v4 不再只修"规则文本"，而是同时改 **目标函数 / 运行时装配 / 阶段门禁 / 反馈记忆**。
> **核心动作**：把"需求转测试用例并提升全流程质量"从背景知识提升为运行时第一目标，并用脚本硬性执行。

---

## 0. 触发：为什么必须做 v4

### 0.1 训练期暴露的 3 个问题

| 问题 | 表现 | 实际伤害 |
|---|---|---|
| 1. 编码思维压缩测试设计 | 模型按"实现最小闭环"收缩测试点和测试用例 | 需求覆盖不足，遗漏异常/边界/易用性/完整性 |
| 2. skill 规范经常被脚本调用链绕过 | 规则存在，但运行时没有被强制注入和校验 | 行为漂移、结果不稳、重复犯错 |
| 3. 只盯当前阶段，不看全链路目标 | 自查时会把"去看其他阶段定义"当补救，而不是启动时就汇总 | 输出局部正确、全局失真，无法真正提升流程质量 |

### 0.2 本次诊断落点（仓库现状）

| 位置 | 当前现状 | 暴露的问题 |
|---|---|---|
| `AGENTS.md` | 已声明 DNA / 3 问自检 / 约束 vs 知识分离 | 有总纲，但没有阶段运行时装配 |
| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | 已定义全局门禁和跨阶段规则 | 有全局规则，但没有生成"阶段启动包" |
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` | 强调模块判定和 S4 引用 | 关注点偏模块正确性，未把"需求覆盖最大化"提升为第一目标 |
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | 明写"不设硬指标""LLM 自由创作" | 容易被模型理解成"自由裁量缩写" |
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | 仍以自由推理为中心，门禁多为文本约束 | 缺少强制 coverage ledger 和 omission ledger |
| `ai_workflow/conversation_skills.py` | `execute_simple_flow()` 只返回下一阶段 skill；`execute_full_flow()` 只看目录状态 | 没有真正的编排器，也没有阶段预装配 |
| `ai_workflow/consistency_check.py` | 只做声明式一致性检查 | 有检查，无阻断，无运行时强制 |
| `ai_workflow/validate_skills.py` | 只校验 frontmatter 合规 | 校验 skill 文件格式，不校验 skill 是否被执行 |
| `.cursor/skills/aidocx-workflow-conversation/SKILL.md` | 要求 AI 自己读很多材料 | 依赖模型自觉汇总，容易在脚本驱动下失效 |

### 0.3 根因归纳

**不是单个 prompt 写得不够狠，而是 4 层同时失效：**

1. **目标函数错位**：S5/S6 当前更像"高自由度内容生成"，不是"覆盖需求、暴露风险、服务下游审查"。
2. **规则只存在于文件，不存在于运行时上下文**：Agent 需要自行跨文件汇总，脚本没有代劳。
3. **skill 规范是建议，不是门禁**：即使 `consistency_check` 发现问题，也不会阻断执行。
4. **错误没有反哺到下一次阶段启动**：重复问题没有变成强制 read/强制 gate/强制 lint。

---

## 1. v4 目标

### 1.1 总目标

把 AIDocxWorkFlow 从"阶段性 prompt + 若干规则文件"升级为：

> **以需求覆盖为主线、以阶段上下文装配为入口、以脚本门禁为强制、以反馈记忆为纠偏的测试设计流水线。**

### 1.2 v4 必达结果

1. **模型不再默认用编码思维收缩测试设计**：
   S5/S6 首要目标从"生成内容"改成"覆盖需求对象 + 暴露缺口 + 保留未覆盖理由"。
2. **脚本调用下 skill 不再靠自觉遵守**：
   每个阶段执行前必须生成并消费 `stage_context.*`，未生成 = 不允许开始阶段。
3. **阶段启动即具备全局视角**：
   当前阶段规则、全局规则、上游输入契约、下游消费契约、历史缺陷模式，在启动时一次性汇总。
4. **重复犯错可被拦截**：
   同类错误从"聊天经验"沉淀为 validator / lint / read-ack / bypass 规则。

---

## 2. v4 设计总览

### 2.1 总体结构

```
全局规则 + 阶段规则 + skill + 上下游契约 + 历史缺陷
                  ↓
         stage_context_builder.py
                  ↓
      stage_context.md / stage_context.json
                  ↓
         stage_gatekeeper.py 预检
                  ↓
           LLM 阶段执行（S1~S8）
                  ↓
    schema / coverage / downstream / lint 校验
                  ↓
      pass / iterate / fail_report / bypass_log
                  ↓
         recurring_failures.json 回灌下轮
```

### 2.2 4 条核心改造线

| 线 | 目标 | 解决的问题 |
|---|---|---|
| A. 目标函数改造 | 把"需求覆盖最大化"写进 S5/S6 第一原则 | 问题 1 |
| B. 运行时上下文装配 | 阶段启动时自动汇总全局 + 跨阶段定义 | 问题 3 |
| C. 强制门禁编排 | skill 不再是建议，变成脚本硬前置 | 问题 2 |
| D. 反馈记忆闭环 | 重复错误沉淀为规则和 lint | 问题 1/2/3 |

---

## 3. A 线：把"需求覆盖最大化"变成 S5/S6 第一原则

### 3.1 纠正当前偏差

当前 S6 明写：

- "`LLM 负责推理`"
- "`不设硬指标`"
- "`LLM 自由创作`"

这些表述在"反模板化"上是对的，但在训练场景下会被模型误读成：

- 可以省略低概率场景
- 可以按经验把多个需求对象压成少量样例
- 可以只写最有把握的用例，不必显式报告遗漏

### 3.2 v4 的新主原则

S5/S6 的系统提示和规则文件顶部统一改成：

> **你当前不是在做代码实现，也不是在写最短答案。你在做需求覆盖设计。默认目标不是少写，而是找全；不是压缩，而是显式列出覆盖和未覆盖。**

### 3.3 新增两个强制产物

#### 1. `coverage_ledger.json`

按以下维度记录覆盖状态：

| 维度 | 说明 |
|---|---|
| `story_id` | 每个 Story 必须出现 |
| `requirement_object` | 每个需求对象必须出现 |
| `function_point` | 每个功能点必须映射 |
| `module` | 8 模块命中情况 |
| `scenario_family` | 正向/异常/边界/负向/配置/权限/状态切换/并发时序/恢复回滚/提示日志 |
| `covered_by` | TP/TC ID 列表 |
| `status` | covered / partial / uncovered |
| `reason` | partial/uncovered 的原因 |

#### 2. `omission_ledger.json`

任何未设计成 TP/TC 的点，不允许"静默消失"，必须记录：

- 为什么没写
- 是需求未定义、上游缺料、还是被风险评估后降级
- 是否阻断下游
- 是否需要人工补充

### 3.4 S5 新标准

S5 不再只要求"Story 生成若干测试点"，而改为：

1. 先出 **覆盖矩阵**，再出 TP。
2. 每个 Story 至少经过一次 **场景族扫描**：
   - 正向
   - 边界
   - 负向
   - 异常
   - 配置切换
   - 权限/角色
   - 状态切换
   - 并发/时序
   - 恢复/回滚
   - 提示/日志/可观测性
3. 如果某类场景判定"不适用"，必须进 omission ledger，而不是直接不写。

### 3.5 S6 新标准

S6 不再只强调"操作步骤写得像人写的"，还必须满足：

1. **每个 TC 必须能回溯到 coverage ledger 的一个或多个未闭合点**。
2. **每个 Story 至少有一条主路径 + 一条风险路径**，除非 omission ledger 给出豁免。
3. **每个高风险 requirement object 必须显式覆盖状态切换和失败恢复**。
4. **如果为减少冗余而合并用例，必须在备注里声明合并了哪些 coverage 点**。

### 3.6 反编码思维约束语

S5/S6 顶部新增硬禁令：

- ❌ 不得以"实现可能共用逻辑"为由合并不同需求对象的测试意图
- ❌ 不得以"代码层已经覆盖"推断产品层无须设计
- ❌ 不得把"用户能看到的功能点"只映射成 API/函数级验证
- ❌ 不得因为不确定就省略，必须写入 omission ledger

---

## 4. B 线：阶段启动时自动汇总全局定义，而不是让模型自己回忆

### 4.1 新增 `stage_context_builder.py`

**建议新增文件**：`ai_workflow/stage_context_builder.py`

职责：

1. 收集全局 DNA：
   - `AGENTS.md`
   - `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc`
   - `.cursor/rules/DNA_3Q_CHECK.mdc`
2. 收集当前阶段定义：
   - `STAGE_S*.mdc`
   - 对应 `SKILL.md`
3. 收集跨阶段契约：
   - 上游输入物料、关键字段、质量门禁
   - 下游消费要求、失败模式
4. 收集历史缺陷：
   - recurring failures
   - bypass 记录
   - 最近一次 review 发现

### 4.2 输出两个文件

| 文件 | 用途 |
|---|---|
| `stage_context.md` | 给人审阅，5 分钟看懂 |
| `stage_context.json` | 给脚本和模型消费 |

### 4.3 `stage_context.json` 建议结构

```json
{
  "meta": {
    "stage": "S6",
    "req_name": "xxx",
    "version": "v1.0"
  },
  "global_mission": {
    "primary_goal": "需求覆盖最大化，显式报告未覆盖点",
    "anti_patterns": [
      "coding_mindset_shrink",
      "stage_local_optimization",
      "silent_omission"
    ]
  },
  "must_read": [],
  "upstream_contract": {},
  "current_stage_contract": {},
  "downstream_contract": {},
  "historical_failures": [],
  "required_outputs": [],
  "gates": []
}
```

### 4.4 阶段启动不再直接喂 SKILL.md

新的运行顺序：

1. 先 `build_stage_context(stage, req_name, version)`
2. 再把 `stage_context.md/json` 喂给阶段执行器
3. 再由阶段执行器调用模型

**结论**：
模型不需要自己去"想起还有全局定义和别的阶段定义"，因为脚本已经先聚合好了。

---

## 5. C 线：让 skill 从建议变成脚本门禁

### 5.1 新增 `stage_gatekeeper.py`

**建议新增文件**：`ai_workflow/stage_gatekeeper.py`

职责分三段：

#### Preflight

- 校验输入物料存在
- 运行 `build_stage_context()`
- 检查 must-read 清单是否完整
- 检查 skill/rule checksum 是否匹配
- 生成 `read_ack.json`

#### Run

- 只把编译后的 `stage_context` 和阶段输入喂给模型
- 禁止脚本绕过 gate 直接进入阶段主逻辑

#### Postflight

- schema 校验
- coverage 校验
- downstream 契约校验
- lint 校验
- 失败则迭代或输出 fail report

### 5.2 `read_ack.json` 强制机制

模型/执行器在生成正式产物前，必须先落一个轻量确认文件：

```json
{
  "stage": "S6",
  "read_materials": [
    "AGENTS.md",
    "DESIGN_AND_EXECUTION_STANDARDS.mdc",
    "STAGE_S6_TEST_CASES.mdc",
    "aidocx-s6-test-cases/SKILL.md",
    "S5 test_points.json",
    "S4 business_flow.md"
  ],
  "global_goal_ack": "本阶段目标是需求覆盖最大化，不是最少用例",
  "downstream_ack": "S7 将审查 coverage_ledger 和 omission_ledger"
}
```

**没有 `read_ack.json` = 阶段未开始。**

### 5.3 强化一致性检查的角色

当前 `consistency_check.py` 是"发现问题但不阻断"。

v4 改为两级：

1. **Build-time check**：保留现有声明式一致性检查。
2. **Run-time check**：发现以下问题直接阻断阶段：
   - must-read 缺失
   - 输出路径与契约不一致
   - 关键字段缺失
   - stage_context 未生成
   - downstream contract 无法满足

### 5.4 修改 `aidocx-workflow-conversation`

这个 skill 需要从"人工说明书"改成"实际编排入口"。

必须删掉或收紧以下模式：

- "AI 自己去读这些文件"
- "当前代码无 save_stage5_output 自动化函数" 这种和代码不一致的说法
- 只列步骤，不做 gate

改成：

1. `build_stage_context()`
2. `run_preflight_gate()`
3. `invoke_stage()`
4. `run_postflight_gate()`
5. `save outputs + ledgers`

---

## 6. D 线：把重复错误沉淀成可执行记忆

### 6.1 新增 `recurring_failures.json`

建议路径：

`workflow_assets/_governance/recurring_failures.json`

记录结构：

```json
[
  {
    "id": "RF-001",
    "stage": "S6",
    "pattern": "coding_mindset_shrink",
    "symptom": "只覆盖主路径，异常和恢复路径消失",
    "prevent_by": [
      "coverage_ledger",
      "omission_ledger",
      "postflight_coverage_check"
    ]
  }
]
```

### 6.2 阶段启动时注入 Top N 历史失败

每次启动某阶段时，默认把与本阶段最相关的 3~5 条历史失败放进 `stage_context`。

目标：

- 不再靠人工反复提醒
- 把"你上次犯过这个错"变成脚本注入事实

### 6.3 审查结果回灌规则

S7/S8 不再只写自然语言评语，还要输出：

- 本次新增失败模式
- 本次验证通过的纠偏规则
- 哪条规则失效了

然后自动更新 `recurring_failures.json`。

### 6.4 新增 Git 分层原则

**工程化边界必须明确区分 3 类资产：**

1. **功能资产**：代码、测试、脚本、自动化能力，必须提交 Git
2. **规则 / 治理 / 知识资产**：`.cursor/rules/`、`.cursor/skills/`、`governance/`、可复用模板库，必须提交 Git
3. **过程资产**：单次需求输入、各阶段中间产物、反馈日志、阶段上下文包、私人分析记录，默认不得提交 Git

**当前仓库的结构要求：**

- `resource/` = 本地输入材料区，不入 Git
- `workflow_assets/<req_name>/...` = 单次需求过程资产区，不入 Git
- `workflow_assets/feedback_logs/`、`workflow_assets/_governance/` = 运行期记录区，不入 Git
- `knowledge/public/module_templates/`、`knowledge/public/test_point_library/`、`knowledge/public/test_case_library/`、`knowledge/public/example_test_cases/` = 公共知识库，入 Git
- `knowledge/project_local/` = 项目级知识库，不入 Git，允许与公共知识库格式不同

**设计要求：**

- 不能再用"整个 `workflow_assets/` 都忽略"这种粗粒度策略，否则会把知识库也排除出版本控制
- 也不能把单次需求的阶段产物直接放进知识库目录，否则会把私人文档和运行过程误传到远端
- 因此必须采用**目录分层 + `.gitignore` 显式放行知识子库**的方案，而不是靠人工记忆区分

---

## 7. 文件级改造建议

### 7.1 新增代码文件

| 文件 | 作用 | 优先级 |
|---|---|---|
| `ai_workflow/stage_context_builder.py` | 构建阶段上下文包 | P0 |
| `ai_workflow/stage_gatekeeper.py` | preflight/run/postflight 三段门禁 | P0 |
| `ai_workflow/coverage_validator.py` | 校验 coverage ledger / omission ledger | P0 |
| `ai_workflow/runtime_contracts.py` | 维护 S1~S8 上下游契约 | P1 |
| `ai_workflow/recurring_failures.py` | 历史失败加载与写回 | P1 |

### 7.2 需要重写的规则 / skill

| 文件 | 改造点 | 优先级 |
|---|---|---|
| `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` | 顶部目标函数改为 coverage-first；新增 coverage ledger / omission ledger | P0 |
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | 删除会被误解的"自由裁量"表述；加入 anti-coding-mindset 硬约束 | P0 |
| `.cursor/skills/aidocx-s5-test-points/SKILL.md` | 从"读很多文件后自由生成"改为"先出矩阵，再出 TP，再过 gate" | P0 |
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | 从"自然语言生成"改为"coverage ledger 驱动生成" | P0 |
| `.cursor/skills/aidocx-workflow-conversation/SKILL.md` | 改为编排入口说明，不再依赖模型手工汇总 | P0 |
| `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` | 增加 `stage_context` / `read_ack` / `coverage_ledger` 的全局定义 | P1 |

### 7.3 需要改造的现有 Python

| 文件 | 改造点 |
|---|---|
| `ai_workflow/conversation_skills.py` | 提供统一 `build_stage_context` / `run_stage_gate` 入口，不再只返回 prompt |
| `ai_workflow/consistency_check.py` | 增加 runtime severity，支持阻断级问题 |
| `ai_workflow/auto_reviewer.py` | 扩展 coverage/omission 审查，而不只看填充率 |
| `ai_workflow/test_case_formatter.py` | 接入 coverage ledger 信息，避免只做格式化 |

---

## 8. 分阶段实施路线

### Phase 1：先修最致命的目标函数和编排入口

1. 新增 `stage_context_builder.py`
2. 新增 `stage_gatekeeper.py`
3. 重写 S5/S6 rule + skill 顶部原则
4. workflow-conversation 改成必须先 build context

**完成标志**：
脚本已经能在 S5/S6 阶段开始前自动生成 `stage_context.*` 和 `read_ack.json`。

### Phase 2：补 coverage 账本和 omission 账本

1. 新增 `coverage_validator.py`
2. S5 输出 `coverage_ledger.json`
3. S6 输出 `coverage_ledger.json` 更新版 + `omission_ledger.json`
4. S7 基于 ledger 审查，而不是只做自然语言评价

**完成标志**：
任何未覆盖点都有记录，不能再静默消失。

### Phase 3：建立失败记忆和重复错误拦截

1. 新增 `recurring_failures.json`
2. S7/S8 写回失败模式
3. 阶段启动时自动注入相关失败模式
4. 将高频问题升级为 lint / gate

**完成标志**：
重复犯错从"靠人提醒"升级为"脚本自动预警/阻断"。

---

## 9. v4 完成判定

- [ ] S5/S6 规则顶部已切换为 coverage-first 目标函数
- [ ] `stage_context_builder.py` 可生成 `stage_context.md/json`
- [ ] `stage_gatekeeper.py` 能执行 preflight / postflight
- [ ] 没有 `read_ack.json` 时不允许进入阶段正式执行
- [ ] S5 产出 `coverage_ledger.json`
- [ ] S6 产出 `coverage_ledger.json` + `omission_ledger.json`
- [ ] S7 审查 coverage/omission，而不只看格式和填写率
- [ ] workflow-conversation 不再要求模型手工汇总全局/跨阶段规则
- [ ] recurring failures 能回灌下一轮阶段启动

---

## 10. 解决 / 新增 / 遗留

### 10.1 本次 v4 解决

- 解释并锁定了"为什么模型会用代码思维收缩测试设计"
- 解释并锁定了"为什么 skill 规范会在脚本调度下失效"
- 解释并锁定了"为什么阶段启动时没有全局上下文汇总"
- 给出从规则、脚本、门禁、反馈四层同时改的方案

### 10.2 本次 v4 新增

- `stage_context` 运行时概念
- `read_ack.json` 强制前置确认
- `coverage_ledger.json` / `omission_ledger.json`
- `recurring_failures.json`
- S5/S6 的 anti-coding-mindset 目标函数

### 10.3 本次 v4 仍遗留（进入 v4 实施决策）

- S5/S6 的最小场景族是否要按业务类型配置化
- `coverage_ledger` 是否要按 Story/Object 双视图分别落盘
- runtime gate 是默认阻断还是允许 `--allow-bypass`
- 历史失败回灌是按阶段 Top N 还是按错误严重度排序

---

## 11. 结论

你提的 3 个问题，本质上不是"模型不够聪明"，而是：

> **系统把测试设计当成了高自由度文本生成，没有把"需求覆盖"做成第一目标，也没有把全局规则在运行时装配并强制执行。**

v4 的方向不是继续堆 prompt，而是把以下 3 件事做成机制：

1. **先定义覆盖，再生成内容**
2. **先装配上下文，再启动阶段**
3. **先过门禁，再允许产出进入下游**

只有这样，模型才会从"会写"转成"会按你的流程稳定写对"。
