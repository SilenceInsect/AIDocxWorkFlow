# CONFIG 模块 TP 库

> **TP 库位置**：`knowledge/public/test_point_library/CONFIG/`
> **子模板来源**：`knowledge/public/module_templates/CONFIG/`
> **v1.2 枚举数**：9（FIELD_LEGALITY / FIELD_INTRA_DEP / FIELD_CROSS_DEP / RELOAD_4_MODE / PARSE_LOAD / VERSION_COMPAT / VALUE_LOGIC / EXPORT_PUBLISH / SERVER_CONFIG）

---

## TP 库文件清单

| 字母 | 子类 | 子类代码 | TP 库文件 | 状态 |
|------|------|---------|----------|------|
| A | 字段合法性 | `FIELD_LEGALITY` | [A_field_legality.md](./A_field_legality.md) | ⏳ 待补 |
| B | 同表一致性 | `FIELD_INTRA_DEP` | [B_consistency.md](./B_consistency.md) | ⏳ 待补 |
| C | 跨表依赖 | `FIELD_CROSS_DEP` | [C_cross_dep.md](./C_cross_dep.md) | ⏳ 待补 |
| D | 热更新 | `RELOAD_4_MODE` | [D_hot_reload.md](./D_hot_reload.md) | ⏳ 待补 |
| E | 解析加载 | `PARSE_LOAD` | [E_parse_load.md](./E_parse_load.md) | ⏳ 待补 |
| F | 版本兼容 | `VERSION_COMPAT` | [F_version_compat.md](./F_version_compat.md) | ⏳ 待补 |
| G | 数值逻辑 | `VALUE_LOGIC` | [G_value_logic.md](./G_value_logic.md) | ⏳ 待补 |
| H | 导出发布 | `EXPORT_PUBLISH` | [H_export_publish.md](./H_export_publish.md) | ⏳ 待补 |
| I | 服务端专属 | `SERVER_CONFIG` | [I_server_specific.md](./I_server_specific.md) | ⏳ 待补 |

---

## 数据契约

每条 TP 模板格式与 `test_points.json` **100% 对齐**：

```json
{
  "id": "{StoryID}-TP-NNN",
  "module": "CONFIG",
  "test_point_type": "POSITIVE | BOUNDARY | NEGATIVE | EXCEPTION",
  "title": "...",
  "precondition": "...",
  "test_input": "...",
  "expected_result": "...",
  "priority": "P0 | P1 | P2",
  "regression": true,
  "s4_reference": "R-{EpicID}-NN | s4_self_inferred"
}
```

---

## 入库流程

1. 从历史 `test_points.json` 中筛选 **CONFIG 模块** + **被 ≥ 2 个需求复用** 的 TP
2. 剥离需求特定信息（玩家名/数值等），保留"测试思路"
3. 按子类归类（FIELD_LEGALITY / FIELD_INTRA_DEP / ...）
4. 写入对应 `{字母}_{子类名}.md`
5. 在 S7 审查 PASS 后正式入库
6. commit 标 `[TP-LIB-CONFIG]` 前缀

---

## 维护记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-15 | 初版索引（待补 TP 模板）|
