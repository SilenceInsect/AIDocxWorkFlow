# 测试点库（按 8 模块 + 4 类型 + 子类三级索引）

> **本目录用途**：S5 阶段生成测试点时的**种子库**——把"已验证过的优质 TP"沉淀下来供后续需求复用。
> **数据契约**：与 `workflow_assets/<req_name>/「S5 测试点生成」/<version>/test_points.json` 100% 对齐。
> **来源**：从历史 `test_points.json` 中提炼出"通用部分"——剥离需求特定信息（玩家名/数值等），保留"测试思路"。
>
> ⚠️ **与 `module_templates/` 的区别**：
> - **`module_templates/`** = S5 推理的"判定参考"（什么模块测什么 + 边界陷阱 + 场景 + TP 种子）
> - **`test_point_library/`** = S5 推理的"成品参考"（可直接复用的完整 TP 模板）
>
> 二者**正交**：`module_templates/` 决定"该怎么拆"，`test_point_library/` 提供"该长什么样"。

---

## 目录结构

```
test_point_library/
├── README.md                    ← 本文件
├── _index.md                    ← 总索引（按模块 × 类型 × 子类）
├── CONFIG/                      ← 配置模块 TP 库
│   ├── README.md
│   ├── _index.md
│   ├── A_field_legality.md
│   ├── B_consistency.md
│   ├── C_cross_dep.md
│   ├── D_hot_reload.md
│   ├── E_parse_load.md
│   ├── F_version_compat.md
│   ├── G_value_logic.md
│   ├── H_export_publish.md
│   └── I_server_specific.md
├── UI/                          ← 界面模块 TP 库
│   ├── README.md
│   ├── _index.md
│   ├── A_control_basic.md
│   ├── B_pure_interaction.md
│   ├── C_layout_adapt.md
│   ├── D_static_display.md
│   ├── E_animation.md
│   ├── F_guide_hint.md
│   ├── G_accessibility.md
│   └── H_edge_ui.md
├── BIZ/                         ← 业务模块 TP 库
│   ├── README.md
│   ├── _index.md
│   ├── A_biz_logic.md
│   ├── B_data_flow.md
│   ├── C_protocol.md
│   ├── D_state_machine.md
│   ├── E_db_persist.md
│   ├── F_concurrency.md
│   ├── G_scheduled_task.md
│   ├── H_payment.md
│   └── I_audit_log.md
├── AUX/                         ← 辅助模块 TP 库
│   ├── README.md
│   ├── _index.md
│   ├── A_common_util.md
│   ├── B_network_layer.md
│   ├── C_cache_layer.md
│   ├── D_resource_mgmt.md
│   ├── E_currency_exchange.md
│   ├── F_offline_update.md
│   ├── G_gm_tool.md
│   ├── H_test_script.md
│   ├── I_acceptance_checklist.md
│   ├── J_storage.md
│   ├── K_perf_tool.md
│   ├── L_ops_tool.md
│   ├── M_security.md
│   └── N_error_recovery.md
├── LINK/                        ← 关联模块 TP 库
│   ├── README.md
│   ├── _index.md
│   ├── A_internal_biz_linkage.md
│   ├── B_cross_server_sync.md
│   ├── C_multi_client_sync.md
│   ├── D_external_third_party.md
│   ├── E_cross_module_resource.md
│   └── F_outbound_data.md
├── SPECIAL/                     ← 特殊情境模块 TP 库
│   ├── README.md
│   ├── _index.md
│   ├── A_boundary_extreme.md
│   ├── B_anti_cheat.md
│   ├── C_weak_net_rate_limit.md
│   ├── D_bg_fg_switch.md
│   ├── E_server_ha_risk.md
│   ├── F_version_compat_biz.md
│   ├── G_channel_gray_biz.md
│   ├── H_compliance_risk.md
│   └── I_resource_exhaust.md
├── LOG/                         ← 日志模块 TP 库
│   ├── README.md
│   ├── _index.md
│   ├── A_event_track.md
│   ├── B_asset_audit.md
│   ├── C_operation.md
│   ├── D_monitor.md
│   ├── E_crash_report.md
│   ├── F_level_storage.md
│   ├── G_integrity.md
│   ├── H_field_compliance.md
│   ├── I_trace.md
│   ├── J_security.md
│   ├── K_third_party.md
│   ├── L_isolation.md
│   └── M_report_fault_tolerant.md
└── HINT/                        ← 提示模块 TP 库
    ├── README.md
    ├── _index.md
    ├── A_red_dot_badge.md
    ├── B_item_float.md
    ├── C_currency_float.md
    ├── D_modal_dialog.md
    ├── E_toast.md
    ├── F_float_notify.md
    ├── G_timed_reminder.md
    ├── H_guide_highlight.md
    ├── I_social_prompt.md
    ├── J_ops_push_prompt.md
    ├── K_state_change_dialog.md
    ├── L_compliance_prompt.md
    └── M_offline_compensation.md
```

---

## 命名规范

每个 TP 库文件命名：**`{字母}_{子类名}.md`**，与 `module_templates/{MODULE}/` **1:1 对齐**（同样的文件名、同样的子类划分）。

---

## TP 库条目格式

每个 `.md` 文件包含 N 个 TP 模板，**统一格式**：

```markdown
# {MODULE}/{字母}. {子类名} — TP 库

> **来源**：`workflow_assets/module_templates/{MODULE}/{字母}_{子类名}.md`（种子 TP 来源）
> **数据契约**：与 `test_points.json` 100% 对齐
> **使用方式**：S5 LLM 生成 TP 时，可直接复用本文件条目，**替换需求特定信息**（Story ID / 玩家名 / 数值）

---

## TP-TPL-001：{测试点名称}

| 字段 | 值 |
|------|---|
| `id` | `{StoryID}-TP-NNN`（实际生成时替换） |
| `module` | `{MODULE}` |
| `test_point_type` | POSITIVE / BOUNDARY / NEGATIVE / EXCEPTION |
| `title` | {测试点名称} |
| `precondition` | {前置条件} |
| `test_input` | {测试输入} |
| `expected_result` | {预期结果} |
| `priority` | P0 / P1 / P2 |
| `regression` | true / false |
| `s4_reference` | {S4 风险点 ID 或 `s4_self_inferred`} |

**适用业务**：
- {适用业务 1}
- {适用业务 2}

**复用次数**（被多少需求使用）：N

**最近使用**：{需求名 v{version}}

---

## TP-TPL-002：...
```

---

## 维护流程

1. **新增 TP 模板**：从历史 `test_points.json` 中提炼"通用部分"，按子类归类
2. **TP 入库标准**：被 ≥ 2 个需求复用 + 经 S7 审查 PASS
3. **TP 废弃**：改名 `_deprecated_<原名>.md` 保留 90 天，在 `_index.md` 登记
4. **commit 前缀**：`[TP-LIB]`

---

## 与 S5 prompt 的集成

S5 prompt（`ai_workflow/prompts/test_point_gen.md`）的加载规则：

1. **必读** `workflow_assets/module_templates/<MODULE>.md`（模块概览）
2. **按需读** `workflow_assets/module_templates/<MODULE>/<X>_*.md`（按 story 涉及的子类）
3. **按需读** `workflow_assets/test_point_library/<MODULE>/<X>_*.md`（TP 库复用参考）
4. **优先复用** TP 库已有条目，**禁止复制粘贴**——必须按真实 story 改写
