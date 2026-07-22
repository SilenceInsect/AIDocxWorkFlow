# AIDocxWorkFlow 方案 v8 — 目录主轴变更（先版本再阶段）

> **本方案承接 v7 §3 仍遗留问题 + 用户实战反馈（2026-07-09）**。
> **核心动作**：目录主轴 `workflow_assets/<req_name>/「S{n} 阶段」/<version>` → `workflow_assets/<req_name>/<version>/「S{n} 阶段」`，覆盖 SSOT + 9 阶段规则 + 10 SKILL + 4 份代码 + 1 hook + README + 公共知识库 + 现有数据 mv。
> **版本号说明**：v7 = 9 阶段规则层修复（69 条 Q）；v8 = 单一议题（目录主轴）= 简洁版方案档。

---

## ⚠️ 启动必读：v8 决策清单

> **v8 是单议题方案**——不像 v7 有 69 条 Q，v8 只解决 1 个根问题（目录主轴）。
> **所有 Q 已通过 AskQuestion 在启动时一次性收集**，本档只列最终决策 + 残留。

| Q 区段 | 数量 | 来源 | 摘要 |
|---|---|---|---|
| **Q-V8-001** | 1 | 用户反馈 + 实战 | 目录主轴从"先阶段再版本"改为"先版本再阶段" |
| **Q-V8-002** | 1 | 用户决策 | 约束同步范围 = 全部 10 份 STAGE_S*.mdc + 全部 10 份 SKILL.md（彻底） |
| **Q-V8-003** | 1 | 用户决策 | 现有数据 v3.0/raw 处理 = mv 到新结构（目录唯一，不双轨） |
| **Q-V8-004** | 1 | 用户决策 | resource/ 目录保持现状（`keep_resource_old`——避免不必要的改动） |
| **Q-V8-005** | 1 | 用户决策 | 历史版本回填 = 全部迁移（实际只有 v3.0） |
| **Q-V8-006** | 1 | 用户决策 | 替换工具 = Python 脚本（可逆/可追溯/dry-run 预览） |
| **Q-V8-007** | 1 | 用户决策 | DESIGN_AND_EXECUTION_STANDARDS.mdc §4.5 同步更新（保持代码 SSOT 不脱销） |

**所有决策已闭环**——参见 `decisions.json` (D-V8-001 ~ D-V8-007)。

---

## v{N} 必备 3 栏（AGENTS.md 强制）

### 1. 本次 v8 解决的问题（来自 v7 系列）

- ✅ **目录主轴方向问题**——v7 PLAN.md §2.6 描述的 `workflow_assets/<req_name>/「S{n} 阶段」/<version>` 路径**与 `resource/<req_name>/<version>_raw.docx` 模式不对齐**（一个先版本一个先阶段）。实战中 v3.0 S1 Pipeline 产物路径 `「S1 需求评审」/v3.0/raw/` 让用户感觉别扭（2026-07-09 反馈）
- ✅ **v7 闭环后 single-issue 修复通路**——v7 是大工程（69 条 Q + 4 件套），v8 是 single-issue 快速响应范本（1 个 Q + 1 个改动面）
- ✅ **落档协议实战闭环**——DNA §9.5（落档协议）+ §9.4（先验后答）在本轮响应中全程执行：决策表先 Write 后展开（governance/design_iter/current/q_decision_table.md）

### 2. 本次 v8 新增内容

#### 2.1 主轴变更（核心）

**旧路径**：

```
workflow_assets/<req_name>/「S{n} 阶段」/<version>/...
```

**新路径**：

```
workflow_assets/<req_name>/<version>/「S{n} 阶段」/...
```

**优点**：
- 与 `resource/<req_name>/<version>_raw.docx` 路径模式对齐（都先版本）
- 同一版本的所有阶段产物一目了然（"看 v3.0 全长啥样"）

#### 2.2 执行改动清单（42 个文件，217 处路径替换）

| 类别 | 文件数 | 替换数 |
|---|---|---|
| SSOT（DESIGN_AND_EXECUTION_STANDARDS.mdc） | 1 | 1（§2.6）+ 手工 §4.5 |
| 根规则（AIDocxWorkFlow.mdc） | 1 | 10（表格）+ 8（树状结构）+ 1（138 行格式说明）|
| STAGE 规则（10 份） | 10 | 89 |
| SKILL（10 份） | 10 | 79 |
| Hooks | 1 | 4（路径函数）+ 1（_stage_dir_path 函数级） |
| 代码（ai_workflow/） | 7 | 21（含 7 处 Python 裸路径拼接） |
| prompts | 3 | 8 |
| README.md | 1 | 2 |
| 公共知识库 | 1 | 1 |
| v7 治理档（同步） | 3 | 8 |
| **总计** | **~42** | **~217** |

详见 `governance/design_iter/current/q_decision_table.md §7`（执行记录）。

#### 2.3 工厂函数（SSOT 同步）

`DESIGN_AND_EXECUTION_STANDARDS.mdc §4.5` 新增 `stage_dir()` 工厂函数：

```python
ROOT_DIR = Path("workflow_assets")
STAGE_PATTERNS = {
    "S1": "「S1 需求评审」",
    "S1.5": "「S1.5 业务澄清」",
    "S2": "「S2 需求拆解」",
    "S2.5": "「S2.5 迭代规划」",
    "S3": "「S3 原型导出」",
    "S4": "「S4 流程图导出」",
    "S5": "「S5 测试点生成」",
    "S6": "「S6 测试用例生成」",
    "S7": "「S7 用例审查」",
    "S8": "「S8 自迭代」",
}

def stage_dir(req_name: str, version: str, stage: str) -> Path:
    """v8+ 标准路径拼接：workflow_assets/<req_name>/<version>/「S{n} 阶段名」"""
    return ROOT_DIR / req_name / version / STAGE_PATTERNS[stage]
```

#### 2.4 Python 裸路径拼接修复

修复了之前散落在代码里的"裸路径拼接"（脚本正则匹配不到）：

| 文件 | 位置 | 旧模式 | 新模式 |
|---|---|---|---|
| `conversation_skills.py:199` | S7 默认 output_dir | `WF / req_name / "「S7 用例审查」" / version` | `WF / req_name / version / "「S7 用例审查」"` |
| `conversation_skills.py:206-210` | 5 处路径参数 | 同上模式（S6/S2/S5 各变体） | 同上 |
| `test_case_formatter.py:126` | S6 默认 output_dir | `WF / req_name / "「S6 测试用例生成」" / version` | `WF / req_name / version / "「S6 测试用例生成」"` |

#### 2.5 现有数据 mv

```
# 旧
workflow_assets/游戏道具商城系统/「S1 需求评审」/v3.0/raw/

# 新
workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」/raw/
```

**mv 步骤**：
1. `mkdir -p "workflow_assets/游戏道具商城系统/v3.0"`
2. `mv "workflow_assets/游戏道具商城系统/「S1 需求评审」" "workflow_assets/游戏道具商城系统/v3.0/「S1 需求评审」"`
3. 把中间层 `v3.0/「S1 需求评审」/v3.0/raw` 提升为 `v3.0/「S1 需求评审」/raw`（扁平化）

### 3. 本次 v8 仍遗留的问题（→ v9 解决）

- 🚧 **CHANGELOG [v8]** 已写入（见 CHANGELOG.md 顶部新章节）
- 🚧 **resource/ 现状确认**：见下方 §3.1
- 🚧 **v3.0 vs v3.01 版本一致性核查**：见下方 §3.2 ⚠️ **重要**
- 🚧 **INDEX.md 未更新**（v8 启动版章节未加）——保留给后续治理
- 🚧 **v3.0 / v3.01 / v3.3 多版本按新结构组织**：见下方 §3.3

#### 3.1 resource/ 现状确认（2026-07-10）

**决定**：保持现状（`keep_resource_old`）——resource 目录不调整。

**实际内容**（`ls -la resource/游戏道具商城系统/`）：

```
sample_requirements.md    2184 字节  2026-06-21 23:05
v3.01_raw.docx           42880 字节  2026-07-09 22:53
```

**结构**：`<req_name>/<version>_raw.<ext>` 已经是"先版本"——与新 workflow_assets 主轴一致。

**结论**：
- ✅ resource 已对齐新主轴（无需改动）
- ✅ `sample_requirements.md` 是 demo 文件，无需版本号
- ⚠️ **v3.0 在 resource/ 缺失**——见 §3.2

#### 3.2 ⚠️ 重要问题：v3.0 vs v3.01 内容一致性

**问题**：resource/ 没有 `v3.0_raw.docx`——只有 `v3.01_raw.docx`。但 workflow_assets 里有 `v3.0/raw/extracted_text.md`（Jul 9 23:54 创建，**晚于** v3.01 上传时间 Jul 9 22:53）。

**数据事实**：

| 文件 | 段落数 | 内联图片数 | 创建时间 |
|---|---|---|---|
| `resource/游戏道具商城系统/v3.01_raw.docx` | 124 | 0 | Jul 9 22:53 |
| `workflow_assets/游戏道具商城系统/v3.0/.../extracted_text.md` | 124 | 0 | Jul 9 23:54 |

**结论**：v3.0/raw 与 v3.01 内容**完全一致**——S1 Pipeline 在 v3.01 上传后跑过一遍，但**目录命名错误**用了 v3.0。

**风险**：v3.0/raw 与 v3.01/raw 内容重复 → 双倍存储 + 索引混乱。

**修复建议**（→ v9）：
1. **方案 A（推荐）**：把 v3.0/raw 重命名为 v3.01/raw → 路径一致
2. **方案 B**：保留 v3.0 目录，删除 v3.0/raw 内容，重新用 v3.01 raw 重跑 S1 Pipeline → 内容覆盖
3. **方案 C**：不动——v3.0 作为"早期版本快照"保留（但需要文档化原因）

**本轮不解决**——超出目录主轴变更范围，留 v9 决策。

#### 3.3 v3.0 / v3.01 / v3.3 多版本按新结构组织

**新结构模板**（v8+ 通用）：

```
workflow_assets/
└── <req_name>/
    ├── v3.0/                    ← 版本独立目录
    │   ├── 「S1 需求评审」/
    │   │   └── raw/
    │   ├── 「S2 需求拆解」/
    │   ├── ...
    │   └── 「S8 自迭代」/
    ├── v3.01/                   ← 版本独立目录
    │   ├── 「S1 需求评审」/
    │   └── ...
    └── v3.3/                    ← 版本独立目录
        └── ...
```

**现状**（2026-07-10）：

```
workflow_assets/游戏道具商城系统/
└── v3.0/
    └── 「S1 需求评审」/
        └── raw/
```

**注意**：v3.01 和 v3.3 实际**还没有 S1 产物**——它们只在 v7 治理档 `governance/design_iter/plans/v7/changes/s7_review_reports_2026_07_09.md` 里**被规划**（"v3.3（192 TC）" / "v3.01"），但**实际产物目录不存在**。

**未来新版本按新结构创建**：
- 新跑 v3.01 → 落在 `workflow_assets/游戏道具商城系统/v3.01/「S{n} 阶段」/`
- 新跑 v3.3 → 落在 `workflow_assets/游戏道具商城系统/v3.3/「S{n} 阶段」/`
- 跨版本比较 → 走 S8 自迭代（§3.2 v3.0/v3.01 内容核查就属于此类）

**资源 → 产物映射**（未来规则）：

| resource/<req_name>/ | workflow_assets/<req_name>/ | 备注 |
|---|---|---|
| `v3.0_raw.docx` | `v3.0/「S1 需求评审」/raw/` | 一对一 |
| `v3.01_raw.docx` | `v3.01/「S1 需求评审」/raw/` | 一对一 |
| `v3.3_raw.docx` | `v3.3/「S1 需求评审」/raw/` | 一对一 |

⚠️ **当前 v3.0 与 v3.01 内容相同**（见 §3.2）——resource 里没有 v3.0，目录里却有 v3.0。这是 v3.0/raw **事实上**派生自 v3.01，但目录命名反映的是"早期版本"——需要 v9 决策。

#### 3.4 v8 实战发现 — 固定 purge 决策（2026-07-10 用户反馈）

**触发**：用户跑 `run_pipeline(["S5","S6","S7"], version="v3.01")` 前，每次都要口头"先问一下是否要删 v3.01 的旧产物"——重复劳动，需要固化。

**决策**：

- `ai_workflow/conversation_skills.py` 新增 `_prompt_purge_existing()` 函数
- `run_stage()` 入口插入 purge 询问（在 `preflight` **之前**）
- `run_s1_pipeline()` 入口也插入（覆盖直接调用 S1 子模块场景）
- `run_pipeline()` 不直接插（依赖 `run_stage` 内部 SKIPPED 决策向下传递）
- 触发条件：阶段目录存在 **且** 非空
- 三选项：Y 删除 / N 保留（skip）/ A 中止
- 非交互环境（CI / 无 TTY）默认 auto_keep，不阻塞
- 删除范围：`shutil.rmtree(stage_dir)` 整个目录（含 raw + ledger）
- **不删** `resource/<req_name>/<version>_raw.docx`（gitignore 区）
- 详细决策表：`governance/design_iter/current/q_decision_table.md`
- SKILL 同步：`.cursor/skills/aidocx-workflow-conversation/SKILL.md §2`

**影响范围**：

| 类别 | 文件 |
|---|---|
| 实现 | `ai_workflow/conversation_skills.py`（新增 ~150 行 + 改 run_stage） |
| 实现 | `ai_workflow/stage_s1_input/pipeline.py`（run_s1_pipeline 加 8 行） |
| Skill | `.cursor/skills/aidocx-workflow-conversation/SKILL.md §2` |
| 知识 | `governance/design_iter/plans/v8/PLAN.md §3.4` |
| 知识 | `CHANGELOG.md [v8]` 追加条目 |

**与 v8 主轴变更的关系**：本次决策属于"代码层固定行为"，非"目录主轴"——但与 v8 同期发现并落地，归 v8 范畴。

---

## 关键引用

| 内容 | 路径 |
|---|---|
| v8 输入（决策表）| `governance/design_iter/current/q_decision_table.md`（原 v7 决策表 v8 复用为决策记录）|
| v8 决策清单 | `governance/design_iter/plans/v8/decisions.json`（D-V8-001 ~ D-V8-007）|
| v8 启动脚本（可重用）| `governance/design_iter/current/scripts/rewrite_path_axis.py` |
| 修复后的 SSOT | `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc §2.6 + §4.5` |
| 修复后的根规则 | `.cursor/rules/AIDocxWorkFlow.mdc` |
| 修复后的 10 份 STAGE 规则 | `.cursor/rules/STAGE_S*.mdc` |
| 修复后的 10 份 SKILL | `.cursor/skills/aidocx-*/SKILL.md` |
| 修复后的 Hook | `.cursor/hooks/auto_advance_check.py` |
| 修复后的核心代码 | `ai_workflow/conversation_skills.py` / `test_case_formatter.py` / `runtime_contracts.py` / `stage_s1_input/utils/constants.py` |
| 项目根铁律 | `AGENTS.md` |
| DNA §9 落档协议 | `.cursor/rules/DNA_3Q_CHECK.mdc §9.4 + §9.5` |

---

> **维护者**：v8 是 single-issue 快速响应范本——1 个核心改动 + 4 件套最小骨架 + 不重写整个治理层。v9 启动议题已识别 2 个（§3.2 v3.0/v3.01 内容核查 + INDEX.md 同步）。