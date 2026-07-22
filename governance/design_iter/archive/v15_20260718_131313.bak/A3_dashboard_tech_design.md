# A3：L4 缺陷率趋势看板技术方案稿

> **文档类型**：v15 §5 阶段 3（v16 规划 + 经验归档）
> **状态**：草案 / 论证并行 / 留 v16 拍板
> **生效日期**：2026-07-16
> **依赖**：v15 §5 阶段 1 `defect_cluster.py` 数据积累（≥ 3 项目 bypass_log + review_report.json）

---

## 1. 背景与动机

### 1.1 问题陈述

v15 阶段 1 的 `defect_cluster.py` 输出 `defect_mode_latest.json`（单项目） + `defect_mode_trend.json`（跨项目，但需 ≥ 3 项目数据）。但**没有可视化层**——QA 和研发只能看原始 JSON 文件，无法快速识别：

- 哪种缺陷模式占比最高？
- 哪个模块的 RCA 触发率最高？
- 跨项目趋势是否恶化？

### 1.2 期望目标

可视化看板包含 3 类图：
1. **缺陷模式堆叠柱图**（cluster 分组 + 计数）
2. **模块 RCA 热力图**（module × RCA type 交叉）
3. **跨项目趋势折线**（按时间轴）

---

## 2. 三种实现方案对比

### 方案 A：CLI 命令行输出（MCP 工具集成）

**技术栈**：纯 Python + rich/textual（终端表格）+ Cursor MCP 适配

**优点**：
- 零前端依赖，部署简单
- 与现有 `defect_cluster.py` 集成零成本
- 在 Cursor IDE 内即可消费

**缺点**：
- 终端表格有限，复杂图难展现
- 跨项目趋势难交互

**工作量**：1 周（POC） + 1 周（完善）

### 方案 B：Web Dashboard（独立 HTTP 服务）

**技术栈**：Python FastAPI + Plotly + Bootstrap（本地）

**优点**：
- 完整可视化，可交互（鼠标 hover 看明细）
- 可嵌入项目 README.md 链接
- 后续易扩展

**缺点**：
- 需端口 + 浏览器
- 与 Cursor IDE 集成弱

**工作量**：2-3 周

### 方案 C：MCP 图表服务（推荐）

**技术栈**：MCP Server + Plotly.js + 浏览器渲染

**优点**：
- 与 Cursor IDE 深度集成
- 同一对话内可调用 + 看图
- 与 v14 末尾 + v15 §5 阶段 1 脚本天然兼容

**缺点**：
- MCP 服务开发工作量
- 需 Cursor 测试环境验证

**工作量**：2-4 周（首次）+ 持续迭代

---

## 3. 推荐方案（待 v16 拍板）

### 3.1 推荐 A → C 路径

1. **v15 末（当前）**：方案 A POC ——`defect_cluster.py` 增加 `--ascii-chart` 参数
2. **v16 阶段 1**：升级到方案 C（MCP 图表服务）

### 3.2 选型理由

- **MCP 路径**与 Cursor IDE 原生集成——v14/15 大量产出都在 Cursor 内消费
- **CLI POC**先行——验证数据契约，避免早期投入过高

---

## 4. 数据契约（已沿用 defect_cluster.py）

### 4.1 输入

- `workflow_assets/<req>/defect_mode_latest.json`（v15 阶段 1 输出）
- `workflow_assets/<req>/defect_mode_trend.json`（v15 阶段 1 输出，≥ 3 项目触发）

### 4.2 输出 schema（图表层扩展）

```json
{
  "meta": { ... },
  "charts": {
    "bar_chart": {
      "title": "Defect Mode Top 10",
      "x_axis": "module × type",
      "y_axis": "count"
    },
    "heatmap": {
      "title": "Module × RCA Type",
      "x_axis": "rca.type",
      "y_axis": "module",
      "values": [[count_matrix]]
    },
    "trend_line": {
      "title": "Cross-Project Trend",
      "x_axis": "time",
      "y_axis": "defect_count_by_mode"
    }
  }
}
```

---

## 5. POC 范围（v15 末 1 周）

### 5.1 可交付物

| 项 | 内容 |
|---|---|
| `defect_cluster.py --ascii-chart` | 命令行 ASCII 柱图（按 top 10 缺陷模式）|
| 1 个集成测试 | 真实需求数据跑通 |
| README | 用法 + 截图（终端 ASCII 图）+ 局限说明 |

### 5.2 POC 不做

- ❌ 交互式图（hover/zoom）
- ❌ 跨项目趋势图（v16 阶段 1）
- ❌ Web UI

### 5.3 POC 评估标准

- 1 个真实需求跑通 → 输出 ASCII 柱图
- 看图能否在 30 秒内识别 Top 3 缺陷模式

---

## 6. v16 阶段 1 规划

### 6.1 范围

- 升级到方案 C（MCP 图表服务）
- 跨项目趋势图（≥ 3 项目数据触发）
- 模块 RCA 热力图

### 6.2 工作量估算

- MCP 服务搭建：2 周
- 图表实现：1 周
- 集成测试：1 周
- 总计：4 周

### 6.3 依赖

- ✓ v15 阶段 1 `defect_cluster.py`（已完成）
- ✓ v15 阶段 2 A2 用例价值评分（试点数据）
- ⏳ ≥ 3 个真实需求的 bypass_log + review_report.json（**当前 0 个**——必须先跑真实需求）

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 数据不足（< 3 项目）| trend 图空白 | POC 只展示 latest；v16 强制要求 ≥ 3 |
| 图表误导（聚类结果片面）| QA 错误决策 | 图表旁显示"样本量 + 时间范围"元数据 |
| MCP 服务开发慢 | v16 延迟 | POC 先用 ASCII 验证数据流 |

---

## 8. 决策位（v15 待 P-V15-X，v16 阶段 1 拍板）

v15 末段只需拍板 **POC 范围**（§5）：
- [ ] **P-V15-4**：方案 A POC 在 v15 内完成（1 周）
- [ ] **P-V15-5**：方案 C 推迟 v16 阶段 1（**否**——v15 内只做 POC，不上 MCP）

v16 阶段 1 决策位（v16 PLAN.md 拍板）：
- [ ] **D-V16-001**：选型方案 C（MCP 图表服务）
- [ ] **D-V16-002**：图表范围（3 类图全做 / 只做 Top 1）
- [ ] **D-V16-003**：数据契约拍板（沿用 A3 + defect_cluster.py 输出）

---

## 附录：参考

- v15 PLAN.md §附录 C（L3 缺陷模式聚类技术方案）
- v15 A1_enhanced_path_feasibility.md（数据流基础）
- v15 A2_case_value_scoring.md（试点数据来源）
- Plotly.js 文档（图表库候选）
- MCP 协议规范（Cursor 集成）