# v3.01 docx 触发决策表（aidocx-workflow-conversation skill）

## 触发

用户于 2026-07-09 22:50 触发：
```
/aidocx-workflow-conversation @/Users/gleon/Documents/游戏道具商城系统_v3.01.docx
```

## 先验（§9.4）

### 1. 文件存在性
- docx 文件存在：✅ 42880 字节，Jun 20

### 2. v4 编排 API 实际签名
- `run_stage(stage, req_name, version, project_name, *, stage_callable)` — conversation_skills.py 行 72-120
- `run_pipeline(stages, req_name, version, project_name, *, stage_callables, stop_on_failure)` — 行 123
- `run_stage_preflight` 调用 `stage_gatekeeper.run_preflight_gate` — 行 50-58
- preflight 默认 req_name="游戏道具商城系统" + version="v1.0" — 与 v3.01 不匹配

### 3. resource/ 现状
- `resource/游戏道具商城系统/sample_requirements.md` 存在（2184 字节，Jun 21）
- **无 v3.01_raw.docx**（docx 还未复制到项目目录）

### 4. workflow_assets/ 现状
- `workflow_assets/游戏道具商城系统/` 已存在 S1~S5 阶段目录（v1.0）
- **无 v3.01 目录**

## §9.5 落档：决策表

### D-1：v3.01 文档首次处理 vs 复用 v1.0 产物

| 候选 | 描述 | 风险 |
|---|---|---|
| **A** | v3.01 视为全新版本，从 S1 开始跑全流程（推荐）| 中（耗时）|
| B | v3.01 在 v1.0 基础上做 diff，仅跑变更阶段 | 高（v3.01 与 v1.0 内容差异未知）|

**默认决策**：A（v3.01 是 v1.0 的下一个大版本，按 `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` §4.2.1 版本语义，v3.0 触发全量重生成）

### D-2：docx 文件如何落到 resource/

| 候选 | 描述 | 风险 |
|---|---|---|
| **A** | 复制到 `resource/游戏道具商城系统/v3.01_raw.docx`（推荐）| 低 |
| B | 直接在代码中传 docx 路径，跳过 resource/ 规范 | 高（违反 §0.1 输入材料规范）|

**默认决策**：A（SSOT 规范要求原始需求文档在 resource/）

### D-3：本轮跑哪几个阶段？

| 候选 | 描述 | 风险 |
|---|---|---|
| **A** | S1 单独跑（输入评审 → 5 维度评分 → 产出终版需求草稿）| 低（最小闭环）|
| B | S1+S1.5+S2 串跑 | 中（需先完成 S1 输出）|
| C | 9 阶段全流程 | 极高（破坏 §9.1 红线 — 单次 ≤ 3 文件改动）|

**默认决策**：A（本轮仅 S1 输入评审）

### D-4：是否需要 docx→markdown 预处理？

| 候选 | 描述 | 风险 |
|---|---|---|
| **A** | 调用 `ai_workflow.stage_s1_input.run_s1_pipeline` 做 docx→md+OCR+图片重命名（推荐）| 低 |
| B | 跳过预处理，让 S1 直接读 .docx | 高（.mdc §S1 要求 Markdown 化）|

**默认决策**：A（SSOT S1 规范）

## 候选决策表（须用户点头才能动手）

```markdown
[D-1] A vs B：v3.01 全新执行 vs diff v1.0
 影响范围: S1 输入 + 全流程下游
 替代方案: B = v3.01 diff v1.0（高风险，未验证 diff 机制）

[D-2] A vs B：复制到 resource/ vs 直接传路径
 影响范围: 资源目录规范
 替代方案: B = 跳规范（违反 SSOT）

[D-3] A vs B vs C：本轮跑 1 / 3 / 9 阶段
 影响范围: 本会话工作时长 + 改动文件数
 替代方案: B = S1+S1.5+S2 / C = 9 阶段全流程

[D-4] A vs B：docx 预处理 vs 直接读 .docx
 影响范围: S1 输入规范
 替代方案: B = 跳 .mdc 规范
```

## 落档协议执行记录

本轮改动（待用户点头后执行）：
1. ⏳ Read conversation_skills.py + resource/ + workflow_assets/ 现状 ✅
2. ⏳ Write 本占位文件 ✅
3. ⏳ 列决策表请用户点头（A 选项）
4. ⏳ 复制 docx → resource/游戏道具商城系统/v3.01_raw.docx
5. ⏳ 调 stage_s1_input.run_s1_pipeline 做 docx→md
6. ⏳ 触发 S1 5 维度评分
7. ⏳ commit