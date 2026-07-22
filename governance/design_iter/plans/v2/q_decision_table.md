# 待答问题决策表（v7 启动期评估）

> **本文件来源**：open_questions.md（v2 遗留）+ CHANGELOG [v6.1] 末尾遗留段。
> **修正说明**：v6.1 之前部分讨论错把"拖到 v3 启动期"当默认——v3 已于 v3.1（2026-06-19）结束；当前最新已发布版本 = v6.1（2026-07-05），所以"next version"在当前语境下指 v7。
> **本文件状态**：决策建议集合（未实施），待 v7 启动期用户点头。

---

## 一、问题来源

| 来源 | 数量 | 跟踪号 |
|---|---|---|
| open_questions.md（v2 遗留，v3-v6 跨期欠账） | 6 | Q-101 / Q-102 / Q-103 / Q-104 / Q-201 / Q-301 |
| CHANGELOG [v6.1] §遗留（v7 评估，明示） | 4 | Q-316 / Q-317 / Q-318 / Q-319 |
| **合计** | **10** | — |

---

## 二、决策表（10 条）

> **优先级排序**：约束类优先（Q-201 / Q-301）；评估型其次（Q-101~Q-104）；元问题最后（Q-316~Q-319）。

---

### [决策 1] Q-201 — Agent "先执行"误读为"先给方案"

- **现状**：v1 默认 C（DNA 已有"先动手再补"反模式 + Q-201 跟踪）；v2 PLAN.md §推进原则 #1 部分缓解
- **候选 A**：DNA Q3 加"先 = 优先级，非流程词"（L2 改 .mdc）
- **候选 B**：beforeSubmitPrompt hook 检测"先"字 + 强提示（L3 加 hook）
- **候选 C**：A + B
- **推荐**：C（v1 默认仍合理；A 改 .mdc + B 加 hook 强化）
- **代价**：1 个 .mdc 段 + 1 个 hook 测试
- **影响范围**：DNA 自检协议 / Agent 行为约束

---

### [决策 2] Q-301 — S6 xlsx 漏产出门禁（v2.08 实战发现）

- **现状**：v2.08 已即时修复 S6（STAGE_S6 + SKILL 改完），8 阶段统一门禁**没做**
- **候选 A**：仅 S6 加 xlsx 强门禁（v2.08 已做）
- **候选 B**：所有 8 阶段都加"强产出门禁"（每阶段列必产清单，缺一 = 失败）
- **候选 C**：B + S7 审查员 A 加 cross-stage 产物完整性校验
- **推荐**：B（一致性 > 局部；v2.08 案例证明"描述 ≠ 门禁"是普遍问题）
- **代价**：8 个 STAGE_S*.mdc × N 产物 = 大改
- **影响范围**：9 阶段门禁体系（除 S1.5 跨 8 个）

---

### [决策 3] Q-101 — design_iter 存什么

- **现状**：v1 默认 C（已落地——PLAN.md + INDEX.md 双视图）
- **候选 A**：只存方案文本
- **候选 B**：存"完整 diff 状态"
- **候选 C**：A + B（独立方案 + 自动 diff 视图）
- **推荐**：确认 C（v7 启动时观察 INDEX.md 是否满足需求；不满足再扩展）
- **代价**：0（确认现状）
- **影响范围**：design_iter 目录结构

---

### [决策 4] Q-102 — design_iter 回滚粒度

- **现状**：v1 默认 A（仅整份回滚；B 待 v3）
- **候选 A**：整份方案回滚
- **候选 B**：字段级回滚
- **候选 C**：A + B
- **推荐**：留 A（v3-v6 期间未观察到"字段级回滚"必要场景）
- **代价**：0（确认现状）
- **影响范围**：design_iter.py 脚本能力

---

### [决策 5] Q-103 — design_iter 与现有备份关系

- **现状**：v1 已选 A（完全独立）
- **候选 A**：完全独立
- **候选 B**：包含 v1（迁入备份）
- **候选 C**：替代（删旧备份）
- **推荐**：确认 A（v3-v6 期间未发现冲突）
- **代价**：0（确认现状）
- **影响范围**：备份目录结构

---

### [决策 6] Q-104 — design_iter 回滚方式

- **现状**：v1 已选 C（已实施——`design_iter.py rollback v0`）
- **候选 A**：人工手工
- **候选 B**：脚本一键
- **候选 C**：自动备份 + 脚本回滚
- **推荐**：确认 C
- **代价**：0（确认现状）
- **影响范围**：design_iter.py 脚本能力

---

### [决策 7] Q-316 — AGENTS.md 行数 ≤ 65 红线

- **现状**：v6.1 缩到 40 行（≤ 65 红线）
- **候选 A**：下调红线（如 ≤ 50）
- **候选 B**：不动（保留 65）
- **候选 C**：v7 复审（看实际维护压力再决定）
- **推荐**：B（再下调 = 限制未来扩展空间）
- **代价**：0（确认现状）
- **影响范围**：AGENTS.md 维护约束

---

### [决策 8] Q-317 — CHANGELOG [v3.1] 历史描述与实际 .mdc 不符

- **现状**：[v3.1] 章节历史描述保留为 snapshot；[v3.1 后续] 漂移注已显式说明
- **候选 A**：修订 [v3.1] 章节
- **候选 B**：留历史（[v3.1 后续] 漂移注已足）
- **推荐**：B（不动 snapshot；Q-301 实例已示范"vN 不动 vN-1 历史"原则——破坏版本可追溯性）
- **代价**：0（确认现状）
- **影响范围**：CHANGELOG 维护约束

---

### [决策 9] Q-318 — 合并分支前必须验证约束冲突

- **现状**：v6 新增问题——合并前是否检查 .mdc / SKILL.md 冲突未约定
- **候选 A**：加 L3 hook（commit 前扫描 .mdc / SKILL.md 冲突）
- **候选 B**：加 L2 mdc 规则（人工遵守）
- **候选 C**：A + B
- **推荐**：C（hook 兜底 + mdc 文档明确协议）
- **代价**：1 个 hook + 1 个 .mdc 段
- **影响范围**：git 工作流 / 合并协议

---

### [决策 10] Q-319 — AGENTS.md / DNA_3Q_CHECK.mdc 拆分原则

- **现状**：v6.1 完成拆分（AGENTS.md = 原则陈述 / DNA_3Q_CHECK.mdc = 执行版）；未来修改是否破坏分工未约定
- **候选 A**：加 alwaysApply 约束（强制拆分）
- **候选 B**：仅 .mdc 文档说明（无强制）
- **候选 C**：A + B（v6.1 已完成；Q-319 跟踪"未来是否破坏"）
- **推荐**：B（文档说明足够；强制约束易过度设计）
- **代价**：1 个 .mdc 段
- **影响范围**：AGENTS.md / DNA_3Q_CHECK.mdc 维护约束

---

## 三、汇总

| 决策 | 推荐 | 类别 | 工作量 |
|---|---|---|---|
| 1 (Q-201) | C | 约束类 | 1 .mdc + 1 hook 测试 |
| 2 (Q-301) | B | 约束类（最大） | 8 STAGE_S* × N 产物 |
| 3 (Q-101) | 确认 C | 评估类 | 0 |
| 4 (Q-102) | 留 A | 评估类 | 0 |
| 5 (Q-103) | 确认 A | 评估类 | 0 |
| 6 (Q-104) | 确认 C | 评估类 | 0 |
| 7 (Q-316) | B | 元问题 | 0 |
| 8 (Q-317) | B | 元问题 | 0 |
| 9 (Q-318) | C | 元问题 | 1 hook + 1 .mdc |
| 10 (Q-319) | B | 元问题 | 1 .mdc |

**核心工作量**：决策 2（Q-301）占大头；其他 9 条多数是"确认现状 / 小改"。

---

## 四、与历史决策表（v3 启动期版）的差异

| 项 | 原版（响应内文） | 本版（v7 启动期） |
|---|---|---|
| 评估期 | "拖到 v3 启动期"（错） | v7 启动期（CHANGELOG 明示） |
| 文件位置 | 未落档 | `governance/design_iter/current/q_decision_table.md` |
| 当前版本判断 | v3（错） | v6.1（CHANGELOG 顶部） |
| 错因承认 | — | 见本文件顶部"修正说明" |

---

> **本文件状态**：v7 启动期决策建议集合，未实施。
> **下一步**：
> - 用户从 10 条里挑要答的
> - Agent 列"改前 vs 改后 diff 摘要"再动
> - 实施后回 decisions.json 加 D-3xx 条目（沿用 v2 约定）

---

## 五、落档协议执行记录（§9.5）

> **来源**：本决策表本身就是 §9.5 落档协议触发场景——上轮响应内文给了 10 条，本轮落档补做。
> **本轮实际改动文件**：
> 1. `.cursor/rules/DNA_3Q_CHECK.mdc` —— §9.5 落档协议段新增
> 2. `.cursor/hooks/dna_decision_persistence_check.py` —— 新文件：sessionEnd 检测决策关键词 + 无 Write → block
> 3. `.cursor/hooks.json` —— sessionEnd 段注册新 hook
> 4. `governance/design_iter/current/q_decision_table.md` —— 本文件（落档协议执行记录段）

**DNA 自检标记**：本轮改动超 §9.4 红线 1 个（4 文件 vs 3 红线），E 方案用户点头全做，下轮起回归 3 文件/轮。

## 六、4 项验证报告（2026-07-05 性能/正确性验证）

> **触发**：用户提"做性能/正确性验证"——验证 5 个 sessionEnd hook 行为 + 性能。

### 6.1 验证项

| # | 验证 | 命令 | 结果 |
|---|---|---|---|
| 1 | `hooks.json` JSON 合法 | `python3 -m json.tool .cursor/hooks.json` | ✅ 通过 |
| 2 | `dna_read_before_answer_check.py` self-test | `--self-test` | ✅ 3 case 过 |
| 3 | `dna_decision_density_check.py` self-test | `--self-test` | ✅ 3 case 过 |
| 4 | `dna_violation_check.py` self-test | `--self-test` | ✅ 3 case 过 |
| 5 | `dna_decision_persistence_check.py` self-test（新增） | `--self-test` | ✅ 4 case + main() 集成过 |
| 6 | 5 hook 并发耗时 | `& wait` shell pattern | ✅ 总 0.02s |

### 6.2 性能数据

| 项 | 耗时 |
|---|---|
| 单 hook 平均 | 0.014s |
| 单 hook 最大 | 0.02s |
| 串行 5 hook 总和 | 0.07s |
| 并发 5 hook 总和 | **0.02s**（≈ 单个最长） |
| 加速比 | 3.5x |

**结论**：sessionEnd 5 hook 并发几乎无感（< 0.02s）——**性能不是问题**。

### 6.3 自检发现 + 修复

- **问题**：`dna_decision_persistence_check.py` self-test Case 1 初版用 `extract_last_assistant_turn` 提取 Case 1 数据——但该函数**永远返回最后一条**，实际取到 Case 4（Case 4 含 Write 调用），导致 Case 1 "expected no Write mentions" 断言失败
- **根因**：self-test 4 case 不能复用 main() 的 helper（main() 只处理单 turn）
- **修复**：4 case 各自单独解析对应行 JSON；main() 集成验证独立构造单 turn transcript
- **修复后**：self-test 全过

### 6.4 文件改动清单

| # | 文件 | 改动 |
|---|---|---|
| 1 | `.cursor/hooks/dna_decision_persistence_check.py` | 加 self-test 段（4 case + main() 集成）+ `__main__` 分支 |
| 2 | `governance/design_iter/current/q_decision_table.md` | 加 §六 4 项验证报告（本段） |

**§9.4 红线**：本轮 2 文件改动，**在红线下**。

### 6.5 后续建议

- sessionEnd 5 hook 并发跑——已验证不慢，无需调整顺序
- 5 hook 都加 self-test——新增的 persistence_check 已加，旧 3 个已存在
- 本轮未验证：`aidocx_feedback_logger_hook.py` 是否也有 self-test（下轮可选）

## 七、剩余验证报告（2026-07-05）

> **触发**：用户提"做剩余验证"——验证 `aidocx_feedback_logger_hook.py` self-test + beforeSubmitPrompt/afterFileEdit/sessionStart 性能 + main() 边界。

### 7.1 验证项

| # | 验证 | 结果 |
|---|---|---|
| 1 | `aidocx_feedback_logger_hook.py` self-test（新增） | ✅ 4 case + cleanup |
| 2 | main() 空 stdin / 空 JSON / 未知 event | ✅ 全 exit 0 退化放行 |
| 3 | sessionStart 2 hook 并发 | ✅ 0.13s（scan_module_definitions 是瓶颈） |
| 4 | beforeSubmitPrompt 3 hook 并发 | ✅ 0.02s |
| 5 | afterFileEdit 2 hook 并发 | ✅ 0.02s |
| 6 | sessionEnd 5 hook 并发 | ✅ 0.02s |

### 7.2 self-test 4 case

| Case | 验证目标 | 结果 |
|---|---|---|
| 1 | `_detect_started_stage` 关键词匹配（5 子 case） | ✅ |
| 2 | `handle_before_submit_prompt` 写 stage_started 事件 | ✅ |
| 3 | `handle_session_end` 聚合 + 写 session_summary | ✅ |
| 4 | `main()` dispatcher stdin JSON → handler | ✅ |

### 7.3 性能数据（按触发器）

| 触发器 | hook 数 | 并发耗时 |
|---|---|---|
| sessionStart | 2 | 0.13s（scan_module_definitions 单跑 0.21s，是瓶颈） |
| beforeSubmitPrompt | 3 | 0.02s |
| afterFileEdit | 2 | 0.02s |
| sessionEnd | 5 | 0.02s |

**结论**：所有触发器 hook 总耗时 < 0.15s——**sessionStart 是唯一慢点，但不每次 prompt 触发**，可接受。

### 7.4 自检发现 + 修复

- **问题 1**：Case 4 初版 payload3 用了 `test_sid`（不是 `main_sid`）——subprocess 写入的是 Case 2/3 同一个文件
- **根因**：测试独立性违反——Case 4 必须用独立 session_id
- **修复**：Case 4 构造独立 `payload4 = {"session_id": main_sid, ...}`
- **修复后**：self-test 4 case 全过

- **问题 2**（参考 §6.3）：`dna_decision_persistence_check.py` self-test 也曾用 `extract_last_assistant_turn` 提取 Case 1——已修

### 7.5 文件改动清单

| # | 文件 | 改动 |
|---|---|---|
| 1 | `.cursor/hooks/aidocx_feedback_logger_hook.py` | 加 self-test 段（4 case + cleanup）+ `__main__` 分支 |
| 2 | `governance/design_iter/current/q_decision_table.md` | 加 §七 剩余验证报告（本段） |

**§9.4 红线**：本轮 2 文件改动，**在红线下**（≤ 3）。

### 7.6 完整 self-test 覆盖率现状

| Hook | self-test | 状态 |
|---|---|---|
| dna_read_before_answer_check.py | ✅ | v6.1 已有 |
| dna_decision_density_check.py | ✅ | v6.1 已有 |
| dna_violation_check.py | ✅ | v6.1 已有 |
| dna_decision_persistence_check.py | ✅ | v6.1 新增（§六） |
| aidocx_feedback_logger_hook.py | ✅ | v6.1 新增（§七） |
| before_prompt_dna_check.py | ❌ | 未加（轻量、纯字符串注入） |
| scan_module_definitions.py | ❌ | 未加（sessionStart 0.21s 慢点，是否值得加？） |
| docx_hook.py | ❌ | 未加（beforeSubmitPrompt） |
| sync_modules_table.py | ❌ | 未加（afterFileEdit） |
| codegraph_sync.py | ❌ | 未加（afterFileEdit） |

**未覆盖 5 个**——下轮评估是否值得补。

## 八、剩余 hook self-test 全补（2026-07-05）

> **触发**：用户提"全补——5 个都加 self-test"，并指出"单测文件又不改动业务"。
> **理由**：用户豁免——self-test 文件改动不引入业务变更风险。

### 8.1 验证项

| # | hook | self-test case | 结果 |
|---|---|---|---|
| 1 | scan_module_definitions.py | 4 case | ✅ |
| 2 | before_prompt_dna_check.py | 4 case | ✅ |
| 3 | docx_hook.py | 4 case | ✅（**+ 发现真实 bug**） |
| 4 | sync_modules_table.py | 5 case | ✅ |
| 5 | codegraph_sync.py | 4 case | ✅ |

### 8.2 self-test 内容速览

| Hook | Case |
|---|---|
| scan_module_definitions | is_already_synced / has_definition_table 8 子 case / scan() 桶分类 / main() exit code |
| before_prompt_dna_check | is_design_question 15 子 case / main() 设计类 prompt / 非设计类 / 退化放行 |
| docx_hook | extract_refs（**含 bug**）/ build_result_prompt / main() 回显 / 退化放行 |
| sync_modules_table | find_all_marker_blocks 三协议 / find_marker_block 过滤 / build_synced_block / inject_block_into_content 两条路径 / main() 边界 |
| codegraph_sync | is_trigger_file / run_sync 缺失二进制 / main() 退化 / 非 trigger 扩展 |

### 8.3 自检发现：docx_hook.py 真实 bug

**Bug**：`extract_refs` 函数对 `@"...md"` 模式的输入，会同时被 `@"([^"]+\.md)"` 和 `@([^\s]+\.md)` 两个 regex 命中，导致 refs 列表出现重复条目（如 `"docs/req.md"` 和 `"docs/req.md` 同时出现）。

**复现**：
```python
extract_refs('看一下 @"docs/req.md" 和 @\'notes.md\' 还有 @something.md')
# 实际返回：['docs/req.md', 'notes.md', '"docs/req.md', "'notes.md", 'something.md']  ← 含 2 个重复
# 期望返回：['docs/req.md', 'notes.md', 'something.md']
```

**影响**：
- `auto_flow` 调 `read_req(refs)` 时，第一个 ref 命中后直接 return——重复 ref 不影响正确性
- 但仍可能影响引用计数、日志等下游场景

**修法建议**（**下轮评估，不在本轮**）：
1. **方案 A（regex 互斥）**：把 3 个 regex 合并为单个，用 alternation，避免重叠
2. **方案 B（去重逻辑）**：在 regex 后对 token 做"是否已被引号包过"的去重
3. **方案 C（现状接受）**：给 `read_req` 加 dedup set 兜底

**已记录到 docx_hook Case 1** —— self-test 标注"含 bug"避免误导后续维护。

### 8.4 §9.4 红线情况

| 维度 | 值 | 说明 |
|---|---|---|
| **用户判断** | "单测文件又不改动业务" → 不超红线 | 豁免 |
| **§9.4 字面** | 5 文件改动 > 3 | 超 2 |
| **本轮决策** | 尊重用户豁免 | 5 文件全改 |

**隐含问题**：§9.4 红线定义**没区分**业务 / 单测改动——是否需要新增"self-test 豁免条款"留归档？

### 8.5 文件改动清单

| # | 文件 | 改动 |
|---|---|---|
| 1 | `.cursor/hooks/scan_module_definitions.py` | Write 完整重写（先 try Edit 留残余，后 Write 修复）+ self-test 段（4 case）+ `__main__` 分支 |
| 2 | `.cursor/hooks/before_prompt_dna_check.py` | Edit 插 self-test 段（4 case）+ `__main__` 分支 |
| 3 | `.cursor/hooks/docx_hook.py` | Edit 插 self-test 段（4 case）+ `__main__` 分支 |
| 4 | `.cursor/hooks/sync_modules_table.py` | Write 完整重写 + self-test 段（5 case）+ `__main__` 分支 |
| 5 | `.cursor/hooks/codegraph_sync.py` | Edit 插 self-test 段（4 case）+ `__main__` 分支 |
| 6 | `governance/design_iter/current/q_decision_table.md` | 加 §八（本段） |

**§9.4 红线**：本轮 6 文件改动（5 hook + 1 文档），**按用户豁免算不超；按字面算超 3**——新 DNA 议题。

### 8.6 完整 self-test 覆盖率现状（10/10 = 100%）

| Hook | self-test | 状态 |
|---|---|---|
| dna_read_before_answer_check.py | ✅ | v6.1 已有 |
| dna_decision_density_check.py | ✅ | v6.1 已有 |
| dna_violation_check.py | ✅ | v6.1 已有 |
| dna_decision_persistence_check.py | ✅ | v6.1 新增（§六） |
| aidocx_feedback_logger_hook.py | ✅ | v6.1 新增（§七） |
| before_prompt_dna_check.py | ✅ | **本轮新增**（§八.1-2） |
| scan_module_definitions.py | ✅ | **本轮新增**（修复了 Edit 残段 + 加 self-test） |
| docx_hook.py | ✅ | **本轮新增**（**+ 发现真实 bug**） |
| sync_modules_table.py | ✅ | **本轮新增** |
| codegraph_sync.py | ✅ | **本轮新增** |

**10/10 = 100%** —— 所有 hooks 都有 self-test。

### 8.7 下轮开放问题

1. **docx_hook.py extract_refs bug**——是修（regex 改写）还是接受现状（dedup 兜底）？
2. **§9.4 红线是否需豁免条款**——self-test 文件改动豁免？待 v6.2 评估。

## 九、v6.2 闭环（2026-07-05）

> **触发**：用户提"做下轮修"——§八.7 两个开放问题收尾。

### 9.1 改动

| # | 文件 | 改动 |
|---|---|---|
| 1 | `.cursor/hooks/docx_hook.py` | `extract_refs` 加 normalize + dedup（方案 B） |
| 2 | `.cursor/rules/DNA_3Q_CHECK.mdc` | §9.1.1 加 self-test 豁免条款（严格边界） |

**§9.4 红线**：本轮 2 文件改动，**在红线下**。

### 9.2 extract_refs bug 修复

**修法**：方案 B —— 保留 3 个 regex 意图清晰，加 normalize + dedup：
- 模式 1：`@"foo.md"` → 提取 `"foo.md"`
- 模式 2：`@'foo.md'` → 提取 `"foo.md"`
- 模式 3：`@foo.md` → 提取 `"foo.md"`
- **dedup key**：`p.lstrip("\"'")` 去前导引号后判重

**修前**：`@"docs/req.md"` + `@docs/req.md` → refs = 2 条（重复）
**修后**：refs = 1 条（去重）

**self-test Case 1f 新增**：验证 `@"foo.md" 和 @foo.md` → 1 条（dedup 命中）

### 9.3 self-test 豁免条款（DNA_3Q_CHECK.mdc §9.1.1）

**豁免边界**（**同时满足全部**）：

| # | 条件 |
|---|---|
| 1 | 文件含 `def self_test() → int` |
| 2 | 含 `--self-test` argv 分支 |
| 3 | 改动**不修改任何业务函数签名或参数** |
| 4 | 改动文件 ≤ 6 个（绝对硬上限） |

**豁免失效**（任一）：改业务函数 / 文件 > 6 / 加依赖 / 用户未明示批量

**示例判定**：
- §八 加 5 个 hook self-test → **豁免有效**（5 ≤ 6，业务函数未改）
- 本轮 docx_hook.py bug 修复 → **豁免无效**（改了 `extract_refs` 业务函数）

### 9.4 自检汇报

| 检查 | 状态 |
|---|---|
| Q1 人本可审查 | ✅ §9.2 / §9.3 表格化 |
| Q2 必然好论证 | ✅ 豁免边界 4 条 + 失效 4 条——**严防滥用** |
| Q3 约束 vs 知识 | ✅ DNA_3Q_CHECK.mdc（约束） vs docx_hook.py（代码）分别落档 |
| §9.4 红线 | ✅ 2 文件改动 < 3 |

### 9.5 10/10 self-test 覆盖率不变 + 修复

| Hook | self-test | 状态 |
|---|---|---|
| 10 个 hook | ✅ 10/10 | v6.2 全覆盖 |
| docx_hook.py Case 1 | ✅ 6 子 case | v6.2 修复 + 加 dedup 验证 |

### 9.6 v6.2 收尾

- ✅ §六 ~ §九 已闭环
- ✅ 11 个 hooks 全 self-test + docx_hook.py bug 修复
- ✅ §9.1.1 豁免条款正式写入 DNA
- ⏭️ 下轮议题（v6.3）：AGENTS.md 引用 DNA_3Q_CHECK §9.1.1（让 Agent 必读）

## 十、v6.3 闭环（2026-07-05）

> **触发**：open_questions.md Q-401 / Q-402 收尾 + 用户"做轮 2"。

### 10.1 改动

| # | 文件 | 改动 | 性质 |
|---|---|---|---|
| 1 | `AGENTS.md` | 关键引用表更新：DNA_3Q_CHECK §9 加注"含 §9.1.1 self-test 豁免条款" | 约束 |
| 2 | `DESIGN_AND_EXECUTION_STANDARDS.mdc` | §3.7 加"大文件改动 SOP"（Q-402 模式化预防） | 约束 |
| 3 | `q_decision_table.md` | §十（本段） | 知识 |

**§9.4 红线**：3 文件改动 ≤ 3 ✅ **卡在红线上**——两约束改动均先 ask（用户在"做轮 2"指令中点头）。

### 10.2 Q-401 闭环：AGENTS.md 引用 §9.1.1

**前**：

```markdown
| 5 问自检 + 准则 4 展开 | `.cursor/rules/DNA_3Q_CHECK.mdc` §1 + §9 + §10 | Agent |
```

**后**：

```markdown
| 5 问自检 + 准则 4 展开 + 决策密度 | `.cursor/rules/DNA_3Q_CHECK.mdc` §1 + §9（含 §9.1.1 self-test 豁免条款）+ §10 | Agent |
```

**为什么这样改**：§9 已包含 §9.1.1，不单独加行——避免引用表膨胀。

### 10.3 Q-402 闭环：Edit 残段风险 SOP

**完整根因分析**：

| 阶段 | 发生了什么 |
|---|---|
| v6.2 §八 | 给 scan_module_definitions.py 加 self_test 函数 |
| 第一次 Edit | StrReplace 用 `if __name__ == "__main__"` 块作 anchor——把 self_test 函数体**留在 `__main__` 之后** |
| Python 加载 | `__main__` 块不执行，**`self_test()` 在 module-level 不存在** → NameError |
| 修复 | Write 完整重写整个文件 |

**SOP 落地位置**：DESIGN_AND_EXECUTION_STANDARDS.mdc §3.7

**SOP 4 步**：

1. **Read 全文** + 确认 ≤ 400 行（经验值）
2. **判断路径**：≤ 400 行 Write 重写；> 400 行 StrReplace
3. **StrReplace 验证**：
   - `def xxx(` 必须出现在引用 `xxx()` 之前
   - `python3 -m py_compile <file>` 强制验证
   - `python3 <file> --self-test` 强制验证
4. **Write 后**：`py_compile` + 重读 + self-test

**3 违规**：
- 跳过 py_compile
- 跳过 self-test
- "Edit 成功 = 文件正确"（**v6.2 教训**）

### 10.4 自检汇报

| 检查 | 状态 |
|---|---|
| Q1 人本可审查 | ✅ §10.2 / §10.3 表格化 |
| Q2 必然好论证 | ✅ 根因 4 阶段 + SOP 4 步 + 3 违规——**严防再发生** |
| Q3 约束 vs 知识 | ✅ AGENTS.md / DESIGN_AND_EXECUTION_STANDARDS.mdc（约束）+ q_decision_table.md（知识）分别落档 |
| §9.4 红线 | ✅ 3 文件改动 = 3，**卡红线**——两约束已先 ask |

### 10.5 收尾汇总（v6.2 → v6.3）

| 版本 | 阶段 | 关键改动 |
|---|---|---|
| v6.2 §六 | dna_decision_persistence self-test | 落档 |
| v6.2 §七 | feedback_logger self-test + cleanup | 落档 |
| v6.2 §八 | 5 hook self-test（10/10 = 100%）| 含 docx_hook bug 发现 |
| v6.2 §九 | bug 修复 + §9.1.1 豁免条款 | DNA 升级 |
| v6.2 收尾 | open_questions.md Q-401/Q-402 + CHANGELOG Unreleased | 落档 |
| v6.3（本轮）| AGENTS.md 引用 + §3.7 SOP + §十 | DNA 升级 |

**v6.3 闭环**——§十以后**没有遗留**（除 §8.7 / §9 原本议题）。

### 10.6 真·下轮议题（v6.4 待 user 决）

1. **Q-402 SOP 实际效果**：v6.3 后下一次大文件改动是否触发 SOP？如果未触发说明 SOP 不够醒目——可能要在 L3 hook 加 dna_sop_check.py
2. **§9.1.1 豁免条款实际效果**：下次"批量加 self-test" 是否走豁免？还是又走字面红线？

## 十一、v6.4 闭环（2026-07-05）

> **触发**：用户"做下一轮"——回顾 §10.6 真·下轮议题 + 本轮遗留档收敛。

### 11.1 决策路径

**初判**：议题 3 "加 L3 hook dna_sop_check.py"——用 AskQuestion 收集：

| 子决策 | 初选项 | 用户决 |
|---|---|---|
| 时机 | afterFileEdit / beforeSubmitPrompt / stop | **beforeSubmitPrompt** |
| 规则 | A 柔 / B 启发式 / C 严 | **选项 C 严（py_compile log）** |
| 重检（不可执行）| — | 用户反馈"不可执行"——**撤 C，重议** |

**第二轮 AskQuestion**：

| 选项 | 含义 |
|---|---|
| B 启发式 + 仅警告 | 检测"prompt 含 Edit 改 .py 且改后没 self-test"——仅 stderr 不阻断 |
| C 撤换 log 计数 | 加 hook_count_py_compile + 检查 log（**复杂**——Q-402 真因非缺 py_compile）|
| D 撤 hook | 不加 hook，靠 §3.7 SOP 自运转 |

**用户决**：**选项 D（撤 hook）**——按治本走。

### 11.2 决策理由

**为什么撤 hook（流程 > 机制）**：

1. **真因是认知问题**——Q-402 是"Agent 不理解 def 顺序"，不是"漏跑命令"
2. **py_compile 不报 def 顺序错**——加 hook 拦不住
3. **强制 = 误报**——启发式检查"是否跑 self-test"会误报小文件改动
4. **现状双保险够**——§9.1.1（self-test 批量）+ §3.7 SOP（大文件改动）——互不冲突
5. **撤 hook ≠ 不防御**——SOP 写在 .mdc + AGENTS.md 引用 + self-test 主动覆盖——多层防御

### 11.3 改动

| # | 文件 | 改动 | 性质 |
|---|---|---|---|
| 1 | `open_questions.md` | Q-401 / Q-402 标记 `[x]` 已决 | 知识 |
| 2 | `CHANGELOG.md` | Unreleased 段加 v6.3 累积 + 撤 hook 决策记录 | 知识 |
| 3 | `q_decision_table.md` | §十一（本段）| 知识 |

**§9.4 红线**：3 文件改动 = 3，**卡红线**——3 个都是知识落档，**无需先 ask**。

### 11.4 决策表 vs §9.4 红线

| 项 | 是否需先 ask |
|---|---|
| open_questions.md close Q-401/Q-402 | ❌ 知识落档 |
| CHANGELOG Unreleased 累积 | ❌ 知识落档 |
| q_decision_table.md §十一 | ❌ 知识落档 |
| **L3 hook dna_sop_check.py** | ⏸️ **本轮撤——不下手** |

### 11.5 自检汇报

| 检查 | 状态 |
|---|---|
| Q1 人本可审查 | ✅ §11.2 决策理由 5 条——清晰可追溯 |
| Q2 必然好论证 | ✅ "真因是认知问题" + "py_compile 不报 def 顺序错"——破除"sensor 防 bug"误区 |
| Q3 约束 vs 知识 | ✅ 3 文件改动全是知识（撤 hook 是知识决策，不动约束） |
| §9.4 红线 | ✅ 3 = 3 卡红线——3 文件都是知识落档 |

### 11.6 真·下轮议题（v6.5+ 待观测触发）

| # | 议题 | 类型 |
|---|---|---|
| 1 | §3.7 SOP 实际效果——下次大文件改动是否触发？ | 观测 |
| 2 | §9.1.1 豁免条款实际效果——下次"批量加 self-test"走豁免还是字面红线？ | 观测 |
| 3 | 撤 hook 决策是否需回头补救（万一 SOP 不够用） | 观测 |

**v6.4 收敛**——§11.6 留 3 观测类议题，**下轮议题不再"造动"**，等实际场景触发。
