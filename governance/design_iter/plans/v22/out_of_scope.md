# out_of_scope.md — S6 用例状态字段重定义（沿用 v22 plan_id）

> 本 Goal 禁区清单（GL-003）。执行中如发现新越界项，须同步更新本文件。

## 功能禁区
- S1 / S1.5 / S2 / S3 / S4 / S5 阶段的产物 schema 变更
- 16 种测试方法学体系调整
- S8 iteration.md / CHANGELOG.md 中已记录的旧版本条目改动

## 技术栈禁区
- 不引入新外部依赖（openpyxl / pyyaml 已存在）
- 不复活被 S7 v14 废除的 `review_report.overall` 字段（违反 SSOT）
- 不复活 v1.1 旧 4 字母缩写（CFG/LNK/SPC/HNT）
- 不改 `_XLSX_HEADERS_V3` 10 列硬约束（用户已确认"表头已有规定"）
- 不改 `_DEFAULT_XLSX_PROFILE` field_mapping
- L2 校验器**本次不实现**（§4.x.1 阻断项 A 已确认 L2 不存在，Q1 降级为 L1-only）

## 职责边界禁区
- 不直接修改 `knowledge/public/module_templates/`（按 S8 §1.5.2 需人工审核）
- 不动项目级 xlsx 导出配置（`knowledge/project_local/<project>/s6/export_profiles/test_cases.export.json`）
- 公共 xlsx 导出 = 走 `_DEFAULT_XLSX_PROFILE`，与项目级 export profile **互斥**
- S7 审查脚本**不改用例状态字段**（只读；状态写回由 `s7_status_writer.py` 单独负责）

## 兼容性边界
- **用例状态枚举** = `Draft / Ready / Rejected / Deprecated`（4 值，**用户 Round 3 锁定**）
  - **禁用我之前错误引入的 `discarded` 枚举**
- **Rejected 触发条件** = `S7 review_report.recommendations.must_fix[]` 任一 severity=MUST_FIX（与现行 S7 SSOT 一致；**不依赖废除的 overall 字段**——§4.x.2 阻断项 B 降级方案）
- **Ready 触发条件** = `L1S6Validator.run_l1_check().passed == True`（L1-only，§4.x.1 降级方案）
- **Draft 触发条件** = 初值 / L1 FAIL
- **Deprecated 触发条件** = S8 阶段（需求变更 / OBJ 废弃）
- v3.01 历史 `Draft` 用例**不主动重写**（§8.5 风险 LOW）
