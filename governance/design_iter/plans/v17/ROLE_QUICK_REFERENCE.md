# AI需求全流程治理工程师 — 快捷调用指南

## 身份
- **角色名**: AI需求全流程治理工程师
- **身份**: 资深测试工程师 + 高级 Prompt 设计师
- **职责**: S1-S9 全阶段规则治理与项目设计理念持续迭代优化

## 调用命令

### 1. 启动治理任务
```
/goal-loop <治理目标>
```
示例：
```
/goal-loop 检查S6测试用例生成是否违反TC结构化映射规范（每个TC至少3个步骤）
```

### 2. 暂停/继续
```
/pause-goal    # 暂停当前治理循环
/resume-goal   # 继续治理循环（如果支持）
```

### 3. 重置
```
/clear-goal    # 清空当前角色状态，重新开始
```

## 治理范围

| 阶段 | 可治理问题 |
|------|-----------|
| S1 | 需求评审质量、clarification_checklist 填写规范 |
| S2 | Epic/Story 拆解精度、模块分类准确性 |
| S5 | 测试点覆盖率、8模块分类、TP 数量 |
| S6 | TC 结构化映射、多步骤 TC、Excel 渲染质量 |
| S7 | 用例审查覆盖率、缺陷分析准确性 |
| S8 | 自迭代建议落地、经验归档完整性 |

## 常用治理任务示例

### 任务1：检查 Excel 渲染质量
```
检查 test_cases.xlsx 的预期结果列是否正确显示 [步骤N] 格式
```

### 任务2：验证模块分类
```
验证 backlog.json 中 epic.module 字段是否符合 MODULES.md 8模块规范
```

### 任务3：优化 SKILL 约束
```
分析 S6 SKILL.md §12 规范落地情况，识别 LLM 执行偏差
```

## 角色状态

当前 goal-loop 快照：
- **goal_id**: tc-structural-mapping-v1
- **status**: achieved
- **latest_artifact**: test_cases_structured.xlsx
- **定义文件**: `governance/design_iter/current/ROLE_AI_REQUIREMENTS_GOVERNANCE_ENGINEER.md`

## 必读规则（角色启动时自动加载）

1. `AGENTS.md` — 项目 DNA
2. `.cursor/rules/DNA_3Q_CHECK.mdc` — 5问自检
3. `.cursor/MODULES.md` — 8模块定义
4. `.cursor/rules/DESIGN_AND_EXECUTION_STANDARDS.mdc` — 跨阶段契约
