# exempt_paths 精确化 · 落档协议执行记录

> **本档是 §9.5 落档协议下的执行档**（任务：移除 yaml `exempt_paths` 中的 `/knowledge/`，让 Hook 检测整个 knowledge/ 树）
> **理由**：`DESIGN_AND_EXECUTION_STANDARDS.mdc §0.1` Git 分类铁律——knowledge/public/ 入 Git 是项目永久规范，违规需扫描；knowledge/project_local/ 虽 .gitignore 但违规仍需发现。原豁免范围太粗放，导致 knowledge/ 下违规从未被 Hook 发现。

---

## 1. 改动前后对比

### 1.1 文件 1：`.cursor/rules/product_format_rules.yaml`

**改前**（62-65 行）：
```yaml
exempt_paths:
  - /workflow_assets/
  - /knowledge/        ← 误豁免整个 knowledge 树
  - /resource/
```

**改后**（62-74 行）：
```yaml
exempt_paths:
  - /workflow_assets/   # 过程资产（单次需求产物，.gitignore）
  - /resource/          # 原始输入材料（.gitignore）

# ── 不豁免的目录说明 ─────────────────────────────────────────────────────────
# 不豁免 knowledge/：
# - knowledge/public/    入 Git（公共库），违规需扫描
# - knowledge/project_local/  虽 .gitignore，但违规仍需发现
exempt_paths_note: |
  原则：只豁免「不入 git」的过程资产 + 输入材料。
  knowledge/ 不豁免——
  - knowledge/public/ 入 Git（公共知识库），违规必须扫描
  - knowledge/project_local/ 虽 .gitignore，但违规仍应在 Hook 中被发现后再人工决定是否处理
```

**diff 摘要**：
- `exempt_paths` 3 项 → 2 项（移除 `/knowledge/`）
- 注释从「过程资产，不是项目文件」→「过程资产 + 原始输入，不入 git」
- 新增 `exempt_paths_note` 字段说明 knowledge/ 不豁免原则

### 1.2 文件 2：`.cursor/hooks/content_compliance_check.py`

**改前**（300-312 行，Case 4）：
```python
exempt_tests = [
    ("/workflow_assets/test.json", True),
    ("/knowledge/test.json", True),       ← 失效断言
    ("/resource/test.json", True),
    ("src/test.json", False),
]
```

**改后**：
```python
exempt_tests = [
    ("/workflow_assets/test.json", True),
    ("/resource/test.json", True),
    ("/knowledge/public/test.json", False),       ← 新增验证不豁免
    ("/knowledge/project_local/test.json", False), ← 新增验证不豁免
    ("src/test.json", False),
]
```

**diff 摘要**：
- 移除 `/knowledge/test.json, True` 项（不再豁免）
- 新增 `/knowledge/public/test.json, False` 和 `/knowledge/project_local/test.json, False` 两项
- 业务函数签名（`scan_file` / `get_compiled_patterns` / `is_path_exempt`）零变更

### 1.3 文件 3：`.cursor/rules/DNA_3Q_CHECK.mdc` §11.1

**改前**（405 行）：
```
| 豁免路径 | `exempt_paths` | workflow_assets、knowledge、resource（过程资产） |
```

**改后**：
```
| 豁免路径 | `exempt_paths` | workflow_assets、resource（只豁免不入 git 的过程资产 + 输入材料）；knowledge/ 不豁免（见 `exempt_paths_note`） |
```

**diff 摘要**：仅文档描述对齐 yaml SSOT——移除 `knowledge`，引用 `exempt_paths_note`。

---

## 2. 自测结果

```bash
$ python3 -m py_compile .cursor/hooks/content_compliance_check.py
PY_COMPILE_OK

$ python3 .cursor/hooks/content_compliance_check.py --self-test
  [OK] Case 1: 规则配置加载 (4 patterns)
  [OK] Case 2: 双版本标签检测
  [OK] Case 3: 永久规范版本标记检测 (4/4 命中)
  [OK] Case 4: 豁免路径检测（含 knowledge/ 子目录不再豁免）  ← 改完后的 Case 4
  [OK] Case 5: scan_file 检测
  [OK] Case 6: CHANGELOG 豁免
  [OK] Case 7: 禁止字段（JSON）检测 (3/3 命中)
  [OK] Case 8: ISO 时间戳检测 (3/3 命中, severity=MEDIUM)
  [OK] Case 9: 端到端 4 类违规扫描
  [OK] Case 10: 正常内容无违规
  [OK] self-test passed (10 cases)
```

**全部 10 个 case 通过**。Case 4 的 knowledge 子目录新增 2 个负样本断言生效。

---

## 3. knowledge/ 树下违规扫描结果

> 用修复后的 Hook（加载同样 yaml 配置）扫描整个 `knowledge/` 树（127 个 md/json/yaml/yml 文件）。
> 完整明细见 `_violations.json`。

### 3.1 违规统计

| 维度 | 数值 |
|---|---|
| 扫描文件数 | 127 |
| 违规总数 | **30 处** |
| 涉及文件数 | 14 个 |
| 改动前状态 | 全部被 `/knowledge/` 豁免扫不到 |

| type | 严重度 | 处数 |
|---|---|---|
| `PERMANENT_RULE_VERSION_TAG` | HIGH | **29** |
| `ISO_TIMESTAMP` | MEDIUM | **1** |

### 3.2 涉及文件清单（14 个）

| rel | 类型 | 处数 | pattern 类别 |
|---|---|---|---|
| `knowledge/public/module_templates/HINT.md` | H | 7 | `v1.7 新增`（6 处） + `v1.7 新增` 列表头 |
| `knowledge/public/test_point_library/HINT/README.md` | H | 6 | `v1.7 新增` ×6 |
| `knowledge/public/module_templates/HINT/K_state_change_dialog.md` | H | 3 | `v1.7 新增` ×3 |
| `knowledge/project_local/.review_queue/s6/obj_name_anchor__quality_rule__20260717.md` | H | 2 | `v16 新增` ×2 |
| `knowledge/project_local/v15_experience/blocker_audit.md` | H | 2 | `v2.0 新增` ×2 |
| `knowledge/project_local/游戏道具商城/s6/export_profiles/test_cases.export.json` | H+M | 2 | `v3 SSOT` + ISO 时间戳 |
| `knowledge/public/module_templates/CONFIG.md` | H | 1 | `v1.2 新增` |
| `knowledge/public/module_templates/HINT/H_guide_highlight.md` | H | 1 | `v1.7 新增` |
| `knowledge/public/module_templates/HINT/I_social_prompt.md` | H | 1 | `v1.7 新增` |
| `knowledge/public/module_templates/HINT/J_ops_push_prompt.md` | H | 1 | `v1.7 新增` |
| `knowledge/public/module_templates/HINT/L_compliance_prompt.md` | H | 1 | `v1.7 新增` |
| `knowledge/public/module_templates/HINT/M_offline_compensation.md` | H | 1 | `v1.7 新增` |
| `knowledge/public/module_templates/LINK/F_outbound_data.md` | H | 1 | `v1.2 新增` |
| `knowledge/public/module_templates/SPECIAL.md` | H | 1 | `v1.2 新增` |

### 3.3 典型违规样本

| 样例 | 文件 | 上下文 |
|---|---|---|
| `v1.7 新增` | `HINT.md` | `\| 升级/升星/段位/赛季结算（v1.7 新增）\|` |
| `v16 新增` | `obj_name_anchor__quality_rule__20260717.md` | `### §1.5.2 Push 5：语义锚点验证（v16 新增）` |
| `v3 SSOT` | `test_cases.export.json` | `"note": "项目级导出配置首次创建；显式声明 v3 SSOT 表头..."` |
| `v2.0 新增` | `blocker_audit.md` | `S7 是 v2.0 新增阶段，workflow_assets/ 中无历史数据` |
| `2026-07-10T01:50:00+08:00` | `test_cases.export.json` | `"created_at": "2026-07-10T01:50:00+08:00"`（归口 meta.created_at 是允许的——本例在 `meta.created_at` 字段内，是豁免的；Hook 检测的是字段值模式，命中是因为字段值仍是 ISO 格式——可考虑在 yaml pattern 里把 `meta.created_at` 加豁免） |

### 3.4 现象归类与决策点

**29 处 `PERMANENT_RULE_VERSION_TAG` 的根因**：知识库里大量「按版本号标来源」的描述（如 `v1.7 新增` / `v2.0 新增` / `v3 SSOT`）。这些其实是**模块/枚举的演进历史注释**——按 DNA §11 应归口 `CHANGELOG.md`，但知识库的"溯源"诉求让它们散落在每份文档里。

**这是规则与现状的冲突**——30 处违规中有 29 处是同一类型。本任务**只动 exempt_paths**，不修这 30 处违规（否则跨入知识库整改范围）。决策：

- ✅ **本任务范围**：exempt_paths 精确化（已完成）
- ⏸ **后续任务（v17 / open）**：是否要（a）扩豁免规则增加路径级豁免（如 `/knowledge/public/test_point_library/` 这种纯模板目录可豁免），或（b）批量整改知识库把版本注释迁到 `CHANGELOG.md`

> ⚠️ **不在本任务范围处理的知识库整改**：本任务结束后，Hook 会在每次 afterFileEdit 时报警告/阻断——下一次 Agent 写入知识库时就会被 Hook 拦下提示。
> 建议在落档档里**显式说明**这是预期行为：先暴露出违规，再人工决定下一步（整改 vs 扩豁免）。

---

## 4. 影响范围与回退方案

### 4.1 影响范围

| 影响对象 | 影响 |
|---|---|
| **Agent** | 写入 knowledge/ 下任何文件后，Hook 会扫描，若发现违规会阻断（exit 1），需带理由备案或修复 |
| **Pipeline 脚本** | 无（产品格式 Hook 只针对 afterFileEdit） |
| **人类审查者** | 看到的是 yaml + DNA 文档已对齐，knowledge/ 不再被静默跳过 |
| **`workflow_assets/`** | 不受影响（仍豁免） |
| **`resource/`** | 不受影响（仍豁免） |

### 4.2 回退方案

若发现豁免过严导致 false positive：

1. **方案 A（首选）**：扩展 yaml pattern 的豁免——给某些"实质合规"的文档加 `exempt_paths` 通配（如 `knowledge/public/test_point_library/*/README.md`）
2. **方案 B**：整改 knowledge/ 下违规（需后续任务立项）
3. **方案 C（回退到本任务前）**：
   ```bash
   git checkout .cursor/rules/product_format_rules.yaml .cursor/hooks/content_compliance_check.py .cursor/rules/DNA_3Q_CHECK.mdc
   ```
   三文件全部回退到主分支状态——影响为零。

---

## 5. §9.5 落档协议执行记录

### 5.1 本轮实际改动文件清单

| # | 文件 | 类型 | 验证 |
|---|---|---|---|
| 1 | `.cursor/rules/product_format_rules.yaml` | 约束（SSOT） | Read 验证 ✓ |
| 2 | `.cursor/hooks/content_compliance_check.py` | 约束（Hook 行为） | py_compile + self-test 10/10 ✓ |
| 3 | `.cursor/rules/DNA_3Q_CHECK.mdc` | 约束（文档描述） | Read 验证 ✓ |

### 5.2 协议违规自检

- ✅ §9.4 先验后答——所有 3 个改动文件都在 Write/StrReplace 前先 Read（头部已 Read 全文）
- ✅ §9.5 落档协议——本档（`exempt_paths_refine_20260717.md`）先建立占位，再展开改动内容
- ✅ §9.1 决策密度——本响应改动 3 个文件，未超红线 3；工具调用未超 10
- ✅ §3 约束改动先答 5 问——Q1 一致性（改 3 个关联约束文档同时改，避免漂移）；Q2 设计（修的是豁免边界，不是绕开检测）；Q3 全局（暴露历史违规是预期收益）；Q4 约束（3 文件均约束类）；Q5 人本可审查（本档含改动对比 + 影响范围 + 回退）
- ⏸ §0.1 知识库边界——knowledge/public/ 是公共知识库，本次变更**未**写到该目录内（仅扫描），符合
- ⏸ §9.1.1 self-test 豁免——本轮未走 self-test 边界（hook self-test 是验证对象，不是添加新 self-test 到其他文件）

### 5.3 后续待办

| 项 | 来源 | 归属 |
|---|---|---|
| 知识库整改（30 处违规） | 本档 §3.4 | open_questions — 待用户决策（整改 vs 扩豁免） |
| yaml pattern 加 `meta.created_at` 豁免 | 本档 §3.3 注 | open_questions — 待评估 false positive 影响 |
| v17 方案 PLAN.md 引用本档 | 关联 | 由 v17 plan 维护方决定 |

---

## 附：本轮新建/扫描副产物

| 文件 | 用途 | 处理 |
|---|---|---|
| `governance/design_iter/current/_scan_knowledge.py` | 一次性扫描脚本（用 Hook 业务函数） | **删除**（副产物，非资产） |
| `governance/design_iter/current/_dump_violations.py` | 一次性违规明细导出（不复用） | **删除**（副产物，非资产） |
| `governance/design_iter/current/_violations.json` | 违规明细导出 | **保留到落档档评审后删除** |
| `governance/design_iter/current/exempt_paths_refine_20260717.md` | 本档（落档协议主档） | **保留**（合规档案） |
