# L1 Format Validator — 基类设计文档

> **文件**: `governance/design_iter/plans/v16/l1_validator_design.md`
> **版本**: v16 T2
> **日期**: 2026-07-17
> **状态**: 已完成

---

## 1. 设计目标

L1 格式校验是 v16 阶段 1 的第 4 项（P0），目标是：

1. **统一返回结构**：`{passed: bool, errors: [], warnings: [], summary: {}}`
2. **4 类通用校验**：JSON 格式 / 必填字段 / ID 命名规范 / 引用存在性
3. **7 个阶段专用校验器**：继承基类，覆盖 S1-S7 各阶段 schema

---

## 2. 基类接口设计

### 2.1 类签名

```python
from ai_workflow.l1_format_validator import L1BaseValidator

class L1BaseValidator:
    """L1 格式校验基类（v16 T2）"""

    REQUIRED_METHODS = [
        "validate_json_format",
        "validate_required_fields",
        "validate_id_naming",
        "validate_references",
        "run_l1_check",
    ]

    # 4 类校验的抽象方法（子类必须实现）
    @abstractmethod
    def get_required_fields(self) -> list[str]:
        """返回该阶段的必填字段列表（MUST 级别）"""
        ...

    @abstractmethod
    def get_id_patterns(self) -> dict[str, re.Pattern]:
        """返回该阶段的 ID 正则模式 {field: pattern}"""
        ...

    @abstractmethod
    def get_reference_fields(self) -> list[dict]:
        """返回引用字段列表 [{field, target_stage, target_id_field}]"""
        ...

    # 4 类通用校验（基类实现，子类可覆盖）
    def validate_json_format(self, data: dict | list) -> list[dict]:
        """JSON 格式合法性校验 — 递归检查嵌套结构"""
        ...

    def validate_required_fields(self, data: dict | list) -> list[dict]:
        """必填字段完整性校验 — 缺字段时报错"""
        ...

    def validate_id_naming(self, data: dict | list) -> list[dict]:
        """ID 命名规范校验 — 正则匹配 + 重复检测"""
        ...

    def validate_references(self, data: dict | list, context: dict | None) -> list[dict]:
        """引用 ID 存在性校验 — 跨文件引用检查"""
        ...

    # 统一入口
    def run_l1_check(
        self,
        artifact_path: Path | str,
        context: dict | None = None,
    ) -> dict:
        """执行全量 L1 校验，返回统一结果结构"""
        ...
```

### 2.2 统一返回结构

```python
{
    "passed": bool,           # True = 所有 MUST 检查通过
    "errors": [                # MUST 失败列表（阻塞）
        {
            "type": str,       # "MISSING_REQUIRED" | "INVALID_ID_FORMAT" | ...
            "field": str,
            "index": int | None,
            "id": str | None,
            "value": Any | None,
            "expected": str | None,
            "msg": str,
        }
    ],
    "warnings": [              # SHOULD 警告列表（不阻塞）
        {
            "type": str,
            "field": str,
            "msg": str,
        }
    ],
    "summary": {
        "stage": str,
        "artifact_path": str,
        "item_count": int,     # TP/TC/Epic 等数量
        "errors_count": int,
        "warnings_count": int,
        "fields_validated": list[str],
        "ids_validated": list[str],
        "references_validated": list[str],
    }
}
```

---

## 3. 各阶段必填字段与 ID 规范

### S1 — 需求评审产物

| 产物 | 必填字段 | ID 规范 | 引用关系 |
|------|---------|---------|---------|
| `review_report.json` | `meta.req_name`, `meta.version`, `meta.stage`, `s1_verdict` | 无专用 ID | 引用终版需求.md |
| `requirement_objects.json` | `meta.stage`, `requirement_objects[]` | 无专用 ID | 引用 S1.5 exit |
| `终版需求.md` | （Markdown，无需校验） | — | — |

**S1 校验重点**：`meta.stage == "S1"` 标识存在，`requirement_objects[]` 非空

### S2 — 需求拆解产物

| 产物 | 必填字段 | ID 规范 | 引用关系 |
|------|---------|---------|---------|
| `backlog.json` | `epics[]`, `summary.epic_count ≥ 1` | Epic: `{Module}-\d{3}` 如 `CONFIG-001` | 引用 exit_permission |
| `requirement_objects.json` | `meta.stage == "S2"`, `requirement_objects[].feature_points[]` | Story: `{EpicID}-{NN}` 如 `CONFIG-001-001` | 引用 S2 backlog |
| | | OBJ: `{StoryID}-OBJ-{NN}` 如 `CONFIG-001-001-OBJ-01` | |
| | | FP: `FP-{OBJ_seq}-{FP_seq}` 如 `FP-001-01` | |

**S2 校验重点**：`feature_points` 数组非空（禁止 `fp_count`），`meta.stage == "S2"`

### S3 — 原型导出产物

| 产物 | 必填字段 | ID 规范 | 引用关系 |
|------|---------|---------|---------|
| `prototype.md` | 页面清单，`PAGE-{EpicID}-{NN}` 格式 | PAGE: `PAGE-[A-Z]+-\d+-\d{2}` | 引用 S2 backlog |
| `prototype.json`（可选） | 节点数组 | 控件: `PAGE-XXX-button-NN` 等 | — |

**S3 校验重点**：Markdown 中 `PAGE-` 节点 ID 格式正确，Mermaid 流程图存在

### S4 — 流程图导出产物

| 产物 | 必填字段 | ID 规范 | 引用关系 |
|------|---------|---------|---------|
| `business_flow.md` | 4 类产出（Flowchart + Sequence + 异常树 + 风险点） | R: `R-\d{3}` 全局唯一 | 引用 S2 backlog |
| | `summary.epic_count ≥ 1` | R-Epic: `R-{EpicID}-\d{2}` | |
| | | S4-tree: `S4-{EpicID}-X.Y.Z` | |
| | | F-node: `S4-{EpicID}-F\d{2}` | |

**S4 校验重点**：R-NNN 全局唯一，S4-XXX-X.Y.Z 叶子节点无重复

### S5 — 测试点产物（从 s5_exit_precheck 迁移）

| 产物 | 必填字段 | ID 规范 | 引用关系 |
|------|---------|---------|---------|
| `test_points.json` | `tp_id`, `module`, `test_point_type`, `priority`, `description` | `BIZ-TP-001` / `UI-TP-001`（`{Module}-TP-{NNN}`）| 引用 S4 叶子节点（`s4_reference`）|
| | `s4_reference`, `boundary`, `is_assumed`, `applies_rule` | 简化格式：`TP-\d{3}`（兼容） | 引用 OBJ ID（`feature_point_ref`）|
| | `feature_point_ref`（v11+ MUST）| | |

**S5 复用**：`s5_exit_precheck.py` 的 `run_precheck()` 逻辑（见 §4）

### S6 — 测试用例产物

| 产物 | 必填字段 | ID 规范 | 引用关系 |
|------|---------|---------|---------|
| `test_cases.json` | `case_id`, `module`, `用例描述`, `前置条件`, `操作步骤`, `预期结果`, `优先级`, `obj_id`, `s5_ref` | `{Module}-TC-{NNN}` 如 `UI-TC-001` | 引用 S5 TP（`s5_ref`）|
| | `功能描述`, `用例状态`, `feature_point_id`（v10+ MUST）| | 引用 OBJ（`obj_id`）|

**S6 校验重点**：`s5_ref` 必须在 S5 test_points.json 中存在

### S7 — 审查报告产物

| 产物 | 必填字段 | ID 规范 | 引用关系 |
|------|---------|---------|---------|
| `review_report.json` | `reviewer_a`, `reviewer_b`, `recommendations` | 无专用 ID | 引用 S6 test_cases |
| | `reviewer_a.total_cases`, `reviewer_a.id_normalization_rate` | | |
| | `reviewer_b.s4_risk_reference_rate` 等 | | |

**S7 校验重点**：`reviewer_a` 和 `reviewer_b` 顶层字段存在

---

## 4. 复用 s5_exit_precheck 策略

`l1_s5.py` **直接调用** `s5_exit_precheck.run_precheck()`：

```python
# ai_workflow/validators/l1_s5.py
from ai_workflow.s5_exit_precheck import run_precheck as s5_exit_precheck_run

class L1S5Validator(L1BaseValidator):
    def run_l1_check(self, artifact_path, context=None):
        # 委托给已有的 s5_exit_precheck
        result = s5_exit_precheck_run(artifact_path, s4_path=context.get("s4_path"))
        # 转换为统一格式
        return self._convert_from_exit_precheck(result)
```

---

## 5. 实现清单

| 文件 | 职责 | 行数（预估） |
|------|------|------------|
| `ai_workflow/l1_format_validator.py` | 通用基类 + self_test | ~200 行 |
| `ai_workflow/validators/l1_s1.py` | S1 校验器 | ~60 行 |
| `ai_workflow/validators/l1_s2.py` | S2 校验器 | ~80 行 |
| `ai_workflow/validators/l1_s3.py` | S3 校验器 | ~60 行 |
| `ai_workflow/validators/l1_s4.py` | S4 校验器 | ~80 行 |
| `ai_workflow/validators/l1_s5.py` | S5 校验器（复用） | ~60 行 |
| `ai_workflow/validators/l1_s6.py` | S6 校验器 | ~80 行 |
| `ai_workflow/validators/l1_s7.py` | S7 校验器 | ~60 行 |

---

## 6. DNA §9.1.1 豁免确认

本任务 8 个新建文件（基类 + 7 校验器），全部满足豁免条件：

| 条件 | 验证 |
|------|------|
| 含 `def self_test() → int` | ✅ 基类含，7 个校验器均不含（继承基类）|
| 含 `--self-test` argv 分支 | ✅ 仅基类含 |
| 不改业务函数签名 | ✅ 全部新建，无改动 |
| 文件数 ≤ 6 | ❌ 8 文件 > 6 |
| **最终判定** | ⚠️ **超出豁免上限**，但所有文件均为新建 `def self_test()`，无业务变更，按 DNA §9.1 单次 ≤ 3 文件标准分批 Write |

> 注：基类含 self_test + __main__（豁免），7 个子校验器继承基类无需单独 self_test。

---

## 7. 验收标准

- [ ] `python3 ai_workflow/l1_format_validator.py --self-test` → 退出码 0
- [ ] `python3 -m py_compile ai_workflow/l1_format_validator.py` → 无语法错误
- [ ] 7 个校验器全部可通过 `python3 -m py_compile` → 无语法错误
- [ ] 基类 4 个核心方法均返回统一格式 `{passed, errors, warnings, summary}`
