# 示例测试点参考（按 8 模块分类的真实产出）

> **本目录用途**：S5 阶段生成测试点时的**完整产出样例**——从历史需求中提炼的"标准答案"。
> **与 `test_point_library/` 的区别**：
> - **`test_point_library/`** = TP 模板库（剥离需求特定信息，保留"测试思路"）——可复用模板
> - **`example_test_points/`** = 完整 TP 样例（保留完整需求上下文）——学习样例
>
> 二者**正交**：
> - 想看"TP 该长什么样" → `test_point_library/`
> - 想看"完整需求怎么拆 TP" → `example_test_points/`

---

## 目录结构

```
example_test_points/
├── README.md                    ← 本文件
├── _index.md                    ← 总索引
├── game_item_shop/              ← 游戏道具商城系统（v1.0 端到端跑通）
│   ├── README.md
│   ├── test_points.json
│   ├── test_points.md
│   └── analysis.md              ← 拆解思路分析
├── recharge_system/             ← 充值系统（待补）
├── activity_limited/            ← 限时活动（待补）
├── guild_war/                   ← 公会战（待补）
└── social_system/               ← 社交系统（待补）
```

---

## 命名规范

按**业务域**组织（不是按模块）——每个示例是一个完整需求（多 Epic / 多 Story / 多模块混合）的完整 TP 产出。

---

## 当前示例清单

| # | 业务域 | 需求名 | Epic 数 | Story 数 | TP 数 | 8 模块分布 | 状态 |
|---|--------|--------|---------|---------|-------|-----------|------|
| 1 | 商城 | 游戏道具商城系统 | 7 | 13 | 77 | UI 6 / BIZ 25 / HINT 10 / CONFIG 8 / SPECIAL 12 / LOG 8 / LINK 4 / AUX 4 | ✅ v1.0 |

---

## 使用方法

S5 LLM 在生成新需求的 TP 时：

1. **第 1 步**：先读 `game_item_shop/test_points.json` 理解完整产出格式
2. **第 2 步**：再读 `game_item_shop/analysis.md` 理解"为什么这么拆"
3. **第 3 步**：按相同格式 + 思路，生成新需求的 TP

**严禁照搬**——必须按真实需求改写，避免"洗稿"。

---

## 维护流程

1. **新增示例**：从有完整 `test_points.json` 的需求中筛选
2. **示例标准**：
   - 端到端跑通 S1→S5 全流程
   - S7 审查 PASS
   - 8 模块均覆盖
   - 包含 EXCEPTION 类型 + s4_reference 字段
3. **敏感信息脱敏**：玩家名/ID/具体数值 → 替换为 `*` 通配符
4. **commit 标 `[EXAMPLE-TP]` 前缀**

---

## 关联文件

- S5 完整规则：`.cursor/rules/STAGE_S5_TEST_POINTS.mdc`
- S5 SKILL：`.cursor/skills/aidocx-s5-test-points/SKILL.md`
- S5 Prompt：`ai_workflow/prompts/test_point_gen.md`
- TP 模板库：`workflow_assets/test_point_library/`
- 模块子模板：`workflow_assets/module_templates/`
