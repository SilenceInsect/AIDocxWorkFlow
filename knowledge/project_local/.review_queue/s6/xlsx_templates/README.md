# S6 XLSX Template Candidate

本目录用于放置 **项目级 S6 Excel 模板候选**。

目标正式路径：

```text
knowledge/project_local/<project_name>/s6/xlsx_templates/test_cases.template.xlsx
```

职责边界：
- 这里的 `.xlsx` 只负责样式、额外 Sheet、列宽、冻结窗格、批注、人工协作布局
- 字段映射、表头顺序、目标 Sheet 名称，放在 `../export_profiles/test_cases.export.json`
- 运行时先读 JSON 导出配置，再按需加载这里的 `.xlsx` 模板

约束：
- 未确认项目名时，不应创建正式项目目录
- 模板若包含项目私有信息，默认只留在 `knowledge/project_local/<project_name>/...`
- 若要提交可审查样例，必须先放在 `.review_queue/`
