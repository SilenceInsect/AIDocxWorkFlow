# 子任务 2.4 — 跨文档同步

> **本档**：4 份治理档（AIDocxWorkFlow.mdc / DESIGN_AND_EXECUTION_STANDARDS.mdc / AGENTS.md / CHANGELOG.md）的 v17 同步状态确认
> **治理基线**：v17/PLAN.md §2.4 必改治理档
> **v17 阶段定位**：Phase 2 子任务 2.4

---

## 1. 同步状态总览

| 文件 | 现状 | 是否需要改 | 原因 |
|---|---|---|---|
| `AIDocxWorkFlow.mdc` | 1 处 §11 违规（line 21 "v16 改默认"）| ✅ 已改 | §11 模式 2 永久规范版本标记 |
| `DESIGN_AND_EXECUTION_STANDARDS.mdc` | 0 处 §11 违规 | ❌ 不需要改 | 全部 v\d+ 是版本号示例（v1.0/v2.0/v3.0）和历史变更说明（"v2.0 废除"），不属于模式 1/2 |
| `AGENTS.md` | 0 处 §11 违规 | ❌ 不需要改 | 仅有 line 26 "v{N}" 模板描述，无具体版本号引用 |
| `CHANGELOG.md` | 多处 v\d+（line 11/24/25/28/29/41/45 等）| ❌ 不需要改 | `exempt_files` 已豁免（product_format_rules.yaml §11.1） |

---

## 2. AIDocxWorkFlow.mdc 改写详情

### 2.1 改写位置

line 21：环境变量表 `AIDOCX_S3_MODE` 行的"含义"列。

### 2.2 改写内容

| 改前 | 改后 |
|---|---|
| `S3 模式选择（，v16 改默认）：` | `S3 模式选择（默认 depth）：` |

### 2.3 §11 违规修复

| 违规位置 | 违规类型 | 修复方式 |
|---|---|---|
| line 21 "v16 改默认" | 模式 2（永久规范版本标记）| 改为中性描述"默认 depth"，不带版本号 |

### 2.4 §11 违规扫描验证

```
$ grep -E "\b(v\d+(?:\.\d+)?)\s+(v\d+(?:\.\d+)?)\b" AIDocxWorkFlow.mdc
（无输出）

$ grep -E "\b(v\d+(?:\.\d+)?)\s*(\+?\s*(?:新增|SSOT|强制))(规则)?" AIDocxWorkFlow.mdc
（无输出）
```

---

## 3. 其他 3 文档不改的依据

### 3.1 DESIGN_AND_EXECUTION_STANDARDS.mdc

**全部 v\d+ 出现位置**（grep 结果 14 处）：

| 行号 | 内容 | 性质 | 是否违规 |
|---|---|---|---|
| 76 | `v1.0`、`v1.1`、`v2.0` | 模块版本号示例 | ❌ 不违规（不在模式 1/2/3/4 范围） |
| 116 | `（v2.0 废除）` | 历史变更说明 | ❌ 不违规（"废除" 不在禁用词） |
| 251-253 | `v1.0`/`v1.1`/`v2.0` | 版本号规则示例 | ❌ 不违规 |
| 258 | `v8 主轴变更` | 历史变更 | ❌ 不违规（"主轴变更" 不在禁用词） |
| 264 | `v1.0`/`v2.1`/`v3.0` | 版本号示例 | ❌ 不违规 |
| 352 | `v6.2 §八` | 历史变更 | ❌ 不违规 |
| 376 | `v6.2 实战教训` | 历史变更 | ❌ 不违规 |
| 437-438 | `v1.0`/`v2.0`/`v2.1` | 版本号示例 | ❌ 不违规 |
| 455-460 | `"v1.0"` | JSON 数据示例 | ❌ 不违规（模式 3/4 不匹配） |
| 504 | `（v2.0）` | 历史变更 | ❌ 不违规 |
| 571 | `v8 变更` | 历史变更 | ❌ 不违规 |
| 590 | `v8+` | 历史变更 | ❌ 不违规 |

**§11 pattern 严格匹配结果**：0 处违规（"v\d+ 新增/SSOT/强制" 在全文 0 处出现）。

### 3.2 AGENTS.md

全文仅 line 26 "v{N}" 模板描述，无具体版本号引用。0 处违规。

### 3.3 CHANGELOG.md

`product_format_rules.yaml` §11.1 明确定义：
- `double_version.exempt_files: [CHANGELOG.md]`
- `permanent_rule_version_tag.exempt_files: [CHANGELOG.md]`
- `forbidden_json_fields.exempt_files: [CHANGELOG.md]`
- `iso_timestamp.exempt_files: [CHANGELOG.md]`

CHANGELOG.md 是历史快照档案，§11.4 注："业务事实描述归口 CHANGELOG.md，不属于格式违规（CHANGELOG 本身已在 exempt_files 豁免名单内）"。

**判定**：CHANGELOG.md 不需要改；待 v17 闭环后，由人工追加 v17 条目（CHANGELOG 是历史档案，不在 Agent 自主写入范围）。

---

## 4. §9.1 决策密度合规

| 维度 | 本轮 |
|---|---|
| 文件改动数 | 1（AIDocxWorkFlow.mdc）+ 1（落档）= 2 ≤ 3 ✓ |
| 单次响应 tool call | ≤ 10 ✓ |
| §11 违规数 | 0 ✓ |

---

## 5. 落档协议

- 本档已落档
- 修改文件数：1（AIDocxWorkFlow.mdc）+ 1（落档）= 2 ≤ 3
- 单次响应工具调用：≤ 10
- §11 违规数：0
- 子任务 2.4 状态：✅ 完成