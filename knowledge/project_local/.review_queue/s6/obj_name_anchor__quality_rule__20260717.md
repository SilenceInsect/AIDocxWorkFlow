# 经验候选 — S5→S6 跨阶段语义链路断裂

> 经验补充（S8 ITER-001，2026-07-17）
> 根因：S5_RULE，S5 规则缺少「文本语义质量门禁」，只覆盖结构链路
> 来源：`workflow_assets/游戏道具商城系统/v3.01/「S8 自迭代」/iteration.md` §4

---

## 经验摘要

| 维度 | 数据 |
|------|------|
| S6 TC obj_id 字段链路 | 100%（104/104 TCs 引用有效 S2 OBJ ID） |
| S6 TC 文本中正式 OBJ 名称覆盖率 | **6.25%**（1/16 OBJ 出现"满减活动"） |
| S5 TP 文本中正式 OBJ 名称覆盖率 | 18.75%（3/16 OBJ） |
| 受影响模块 | 全部 8 模块 |
| 根因阶段 | S5 规则（STAGE_S5_TEST_POINTS.mdc §1.4） |

## 根因分析

跨阶段链路（S5→S6）需要**双向验证**：
1. **结构验证**（ID 引用）→ 当前已达标（100%）
2. **语义验证**（正式命名文本）→ 当前断裂（6.25%）

仅结构验证通过 ≠ 实际可追溯性好。若 `obj_id` 字段因解析错误缺失，TC 即失去与需求的关联锚点。

## 建议回写目标

### 目标 1：`.cursor/rules/STAGE_S5_TEST_POINTS.mdc`

**§1.4 必读材料表 — 新增第 6 行**：

```
| 6 | S2 requirement_objects（必须读取） | OBJ obj_name 是 TP 描述的语义锚点；每个 TP 的 title/description 必须包含其引用的正式 OBJ obj_name |
```

**§1.5.2 Push 5 — 新增语义锚点验证**：

```markdown
### §1.5.2 Push 5：语义锚点验证（v16 新增）

**验证每条 TP 的 title 和 description 是否包含其引用的正式 OBJ obj_name**。

**操作步骤**:
1. 从 TP 的 `s5_ref` 或 `feature_point_ref` 解析出对应的 OBJ ID
2. 在 S2 `requirement_objects.json` 中查找该 OBJ，获取 `obj_name`
3. 验证 TP 的 `title` 或 `description` 文本中是否包含该 `obj_name`
4. 若不包含：补充 `obj_name` 或在 `applies_rule` 中记录同义词替代

**未通过处理**：TP 返回 LLM 迭代。
```

### 目标 2：`.cursor/rules/STAGE_S6_TEST_CASES.mdc`

**§字段语义规范表 — 修改 test_scenario 行**：

```
| test_scenario | 场景名 | **必须包含** `obj_id` 对应的正式 OBJ `obj_name`；禁止仅用口语化词替代正式名称 |
```

**§1.5.3 — 新增 OBJ 名称锚点传递规则**：

```markdown
### §1.5.3 OBJ 名称锚点传递（v16 新增）

每条 TC 的 `test_scenario` 必须包含其 `obj_id` 对应的正式 OBJ `obj_name`。

**自检**：
- [ ] `test_scenario` 包含正式 OBJ obj_name
- [ ] 不全用口语化词替代（如"道具"→"游戏道具"）
- [ ] 若用同义词，记录到 `applies_rule`
```

### 目标 3：同步更新技能文件

- `aidocx-s5-test-points/SKILL.md` — 同步 Push 5 语义锚点验证
- `aidocx-s6-test-cases/SKILL.md` — 同步 §1.5.3 OBJ 名称锚点传递规则

---

## 遗留问题（待下一轮验证）

| 问题 | 状态 |
|------|------|
| S5 Push 5 增加后，历史 TP 需回填正式 OBJ 名称 | 待下一需求批次验证 |
| 知识库对照表（正式名称 ↔ 常用口语词） | 建议在 `knowledge/public/module_templates/<MODULE>/` 增加 `naming_map.md` |
