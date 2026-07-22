# out_of_scope.md（v28+ carry — v27 遗留 + 反模式防御）

> **依据**：goal-loop SKILL v1.2 §3.1 强制产出
> **Goal ID**：`a6068831-566a-42b9-ac61-0937ec0980d9`
> **承接**：v27 CONVERGED §遗留项 + v27 review §7 v28 启动条件
> **创建日期**：2026-07-20

---

## 功能禁区

- ❌ **不动 v17 已 CONVERGED 产物**（fp_name 已 Round 15 F-F 删除；v17 §2 已闭环）—— v17 5 项约束的"放宽"是规则放宽，不是 v17 重做
- ❌ **不动 v18-v19 / v22-v26 已归档 / 已闭环方案** —— 保留审计锚点
- ❌ **不动 v3.01 test_cases.json 字节**（SSOT，out_of_scope 不动）
- ❌ **不动 v27 已闭环产物**（B1/C1-A2/C2/C4 + 6 个治理档）—— 仅可追加 v28 段
- ❌ **不动 v3.02 Goal**（`4c1eedec`）—— v28 不接 v3.02 T-005 中断，单独重启
- ❌ **不动 .gitignore / git config / git history**
- ❌ **不动 knowledge/public/**（Agent 不得直接入库；systemic_issues.md 待补写入候选区）
- ❌ **不动 .pytest_cache/**

## 技术栈禁区

- ❌ **不引入新依赖**（DNA §9.1 红线）
- ❌ **不修改 .mdc / SKILL.md / .py 已闭环产物**（v17 / v18 / v27），仅追加 v28 段
- ❌ **不修改 .mdc 列表外文件**（如 hooks/、skill/、rule/ 等层）
- ❌ **不动 validator 源码**（l1_s6.py / l2_s6.py / check_field_completion.py 已闭环）

## 职责边界禁区

- ❌ **不 commit**（用户硬约束）
- ❌ **不动 git config / git history**
- ❌ **不跨 goal 引用快照**（v3.01 Goal `3f9c31b8` blocked / v3.02 Goal `4c1eedec` active 与 v28 独立）

## 反向边界（特别标注）

> 这些边界**必须守住**，否则触发反模式熔断：

1. **v28 不 reopen v17 CONVERGED**——v17 已闭环 100% 字段溯源方案；v28 是 v17 5 项约束的"放宽"，不是 v17 重做
2. **fp_name 字段**已 Round 15 F-F 删除（SKILL.md §3）——v28 处置 ① = 字段已不存在，约束变成"空对象"
3. **preconditions[]**（⑤）按 v26 §判定 = ✅ 维持——v28 不动
4. **D1-D3 / B2-B4 / A1-A3-A4-B3** 是 v26 草案清单——v28 必须先精审（每个独立写 DT 决策）才能进 Round 1 Act
5. **SYS-001/SYS-002** 反模式防御建议——v28 可采纳，但需先精审是否值得写为 SKILL.md 补充段

## 触发熔断条件

| 条件 | 触发动作 |
|---|---|
| 修改 test_cases.json 字节 | BLOCKER：撤销 + 写 DT |
| 修改 v17 / v18 / v19 / v27 已闭环产物 | BLOCKER：撤销 + 写 DT |
| 引入新依赖 | BLOCKER：回退 + 写 DT |
| commit | BLOCKER：撤销 commit + 写 DT |
| v28 改动触动 v3.01 / v3.02 Goal 快照 | MAJOR：人工确认 |
| D1-D3 / B2-B4 / A1-A3-A4-B3 任一项未精审就执行 | BLOCKER：写 DT 决策（v26 §精审漏）|