# AIDocxWorkFlow v3.01 全流程执行决策表

> **落档时间**：2026-07-10
> **触发命令**：`/aidocx-workflow-conversation @resource/游戏道具商城系统/v3.01_raw.docx`
> **AIDOCX_INCLUDE_S2_5**：未设置 → 默认跳过 S2.5

## 一、决策表

[决策 1] **历史版本处理**：v3.01 在 workflow_assets 下仅有空 S1 目录，无 v2/v3 历史产物可复用。
 影响范围：v3.01 是全量重生成（按 §4.2.2 vN.0 语义）
 替代方案：(A) 全量跑 S1→S7；(B) 中止并询问用户
 等待确认：[ ]

[决策 2] **S1 输入材料**：`resource/游戏道具商城系统/v3.01_raw.docx`（42.8KB，已存在）
 影响范围：S1 子模块将解析 docx + OCR 图片
 替代方案：(A) 跑 S1 子模块；(B) 用户已有人工填写材料，跳 S1
 等待确认：[ ]

[决策 3] **编排路径**：`run_pipeline(["S1", "S1.5", "S2", "S3", "S4", "S5", "S6", "S7"], ...)`
 影响范围：S2.5 默认跳过
 替代方案：(A) 标准全流程；(B) 用户指定子集
 等待确认：[ ]

[决策 4] **LLM 产物路径**：S5/S6 的 LLM 推理产物由对话层生成（test_points / test_cases 列表）
 影响范围：需要 LLM 在对话中提供完整 payload
 替代方案：(A) LLM 直接生成；(B) 调用脚本兜底（仅种子 case）
 等待确认：[ ]

## 二、5 问自检

| 问 | 检查点 | 答 |
|---|---|---|
| Q1 一致性 | 全流程执行不改 .mdc/SKILL.md/CHANGELOG | ✓ |
| Q2 设计 | 标准执行而非结构变更 | ✓ |
| Q3 全局 | 串行编排，stop_on_failure 阻断 | ✓ |
| Q4 约束 vs 知识 | 纯执行，无约束变更 | ✓ |
| Q5 人本可审查 | 各阶段产物可独立审查 | ✓ |

## 落档协议执行记录

> 决策时间：2026-07-10
> 用户确认：(1) 全流程 S1→S7 一次性跑；(2) project_name=游戏道具商城
> AIDOCX_INCLUDE_S2_5：未设置 → 跳过 S2.5
> 阶段编排：`run_pipeline(["S1","S1.5","S2","S3","S4","S5","S6","S7"], req_name="游戏道具商城系统", project_name="游戏道具商城", version="v3.01")`
> 停止策略：stop_on_failure=True（任一阶段非 PASS 则后续 SKIPPED）

## 执行结果汇总

| 阶段 | 产物数 | 关键产物 | 状态 |
|------|--------|----------|------|
| S1 需求评审 | 7 | review_report (8.80/10 PASS), 5 份物料 | ✅ |
| S1.5 业务澄清 | 1 | exit_permission (can_proceed_to_s2=true, LOW) | ✅ |
| S2 需求拆解 | 3 | backlog.json (9 Epic/18 Story), requirement_objects.json (27 OBJ/78 FP) | ✅ |
| S3 原型导出 | 2 | prototype.md (13 页面 + Mermaid 流图) | ✅ |
| S4 流程图导出 | 2 | business_flow.md (6 图：购买/时序/异常树/风控/VIP/退款) | ✅ |
| S5 测试点生成 | 6 | test_points.json (84 TP, 100% Story 覆盖) | ✅ |
| S6 测试用例生成 | 8 | test_cases.json (38 TC, 13 种方法学, v3.3 强门禁 PASS) | ✅ |
| S7 用例审查 | 8 | review_report (双审查员 PASS), 风险点覆盖 100% | ✅ |
| S8 自迭代 | 0 | S7 PASS 后无需自迭代 | (跳过) |

**总计：37 个产物文件**