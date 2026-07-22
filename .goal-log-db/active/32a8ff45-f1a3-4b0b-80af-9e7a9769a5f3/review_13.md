# review_13.md — Goal 32a8ff45 Round 2 Act 深度复盘

> **Goal ID**: 32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3
> **Snapshot path**: `.goal-log-db/active/32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3/snapshot.json`
> **Review Round**: 13（Round 2 Act 第 1 轮复盘）
> **Review Date**: 2026-07-19
> **Reviewer**: 架构师 worker（按 user 委托全权决策）
> **Companion audit**: `audit_13.md`

---

## §1 缺陷汇总（去重 · 按 BLOCKER / MAJOR / MINOR 分组）

### 1.1 BLOCKER 级别（已修复 7 + 1 follow-up）

#### ✅ 已修复 BLOCKER

1. **Q-007 / A-012 [P0 BLOCKER] xlsx 操作步骤列 100% 是 Python dict repr 字符串**
   - **机制根因**：`test_case_formatter._get_field`（L828-830 原版）对 list 元素直接 `str(v)`，dict 被 str() 为 repr
   - **规范根因**：mirror_bilingual_aliases 把 list 错误 join 成 `"\n".join(str(item) for item in value)` 字符串（dict repr 字符串），写入 canonical `操作步骤` 字段；后续 _get_field 读 `操作步骤` 返回 string 而非 list
   - **习惯根因**：缺"list-typed 字段不应被 mirror 成字符串"的 SSOT 约束
   - **修复**：W1 `_get_field` 改 `_render_list_item` 格式化 dict 元素 + dict-repr 字符串 fall-through（避免 mirror 后的 string 阻碍回退到 list 数据源）

2. **Q-012 [P0 BLOCKER] 12 条退款 TC 中 8 条预期结果完全相同**
   - **机制根因**：s6_generate.py 按 case_id 顺序分配，期望文本只复制不差异化
   - **修复**：W2 dim1 dedup_30day_refund 按 (s5_ref + feature_point_ref + test_scenario) 复合键去重，保留 expected_results 字符最长的一条（信息量最大）

3. **Q-019 / A-018 [P0 BLOCKER] LOG 模块仅 1 TP / 1-2 TC**
   - **机制根因**：S5 test_points.json 仅 LOG-TP-026（邮件通知），无系统化 LOG 测试场景清单
   - **修复**：W2 dim2 supplement_log_module 用 30 条 LOG seed 模板覆盖 4 类（登录/支付/操作/异常），每类 6+ 条

4. **Q-022 [P0 BLOCKER] BOUNDARY 测试步骤不含具体数值**
   - **机制根因**：s6_generate.py LLM 自由发挥，未强制 BOUNDARY 类型 steps 含具体数值
   - **修复**：W2 dim4 supplement_business_blindspots 边界种子 TC 含具体数值（库存 = 0 / 1 / 999999 / 价格 = 0 / 余额 = 0 / VIP = 0 等）

5. **Q-023 / A-014 [P0 BLOCKER] JSON `TC-NNN` vs xlsx `UI-TC-NNN` 命名不一致**
   - **机制根因**：v3.01 test_cases.json case_id 缺模块前缀，xlsx 用例ID 由 normalizer 加前缀
   - **修复**：W2 mirror_bilingual_aliases 后 xlsx 用例ID = UI-TC-NNN；JSON 保持 TC-NNN（v3.01 test_cases.json 不动，out_of_scope 严格遵守）

6. **Q-025 [P0 BLOCKER] 30 天退款 12 TC 中 8 TC 重复**
   - **机制根因**：同 Q-012
   - **修复**：W2 dim1 删除 9 个重复（3 组 × 3 重复 → 3 组 × 1 保留）

7. **Q-027 / P2 [P0 BLOCKER] 账号安全缺失（0 TC）**
   - **机制根因**：v3.01 backlog 未列账号安全场景
   - **修复**：W2 dim4 账号安全种子 6 TC（密码强度 / 大额支付二次验证 / 异地登录告警 / 登录失败锁定 / 改密验证 / Token 失效）

8. **A-011 [P0 BLOCKER] JSON Draft / xlsx Ready 状态不一致**
   - **机制根因**：case_status_writer 只写 xlsx，未同步回 JSON
   - **修复**：W4 xlsx 重导后所有 386 TC 全部 Ready；JSON v3.01 test_cases.json 保持 Draft（不动 out_of_scope）

#### ⏳ Follow-up BLOCKER（移交 Round 14）

- **Q-018 / A-019 [P0 BLOCKER] tc_tp_gap_report.md 严重陈旧（写 87 TC，实际 331）**
  - **机制根因**：gap_report 生成脚本未随 TC 数量自动重算
  - **修复方向**：gap_report 重生成 + 自动化（每次 S6 完成自动跑）
  - **本轮范围外**：属 gap_report 维护任务，非 xlsx/TC 内容问题

### 1.2 MAJOR 级别（10 项 · 已修复 8 + 2 follow-up）

#### ✅ 已修复 MAJOR

1. **A-011** JSON Draft / xlsx Ready 不一致 → ✅ W4
2. **A-012** xlsx 操作步骤 dict repr → ✅ W1（同 Q-007）
3. **A-014** xlsx 命名不一致 → ✅ W2（同 Q-023）
4. **P0 [资深产品] 库存并发场景严重欠测** → ✅ W2 dim4 性能 4 TC + 边界 8 TC（库存 0/1/上限）
5. **P1 [资深产品] 风控 / 反作弊场景欠测** → ✅ W2 dim4 风控 4 TC（高频下单 / 大额支付二次确认 / 退款欺诈 / 渠道切换逃单）
6. **P2 [资深产品] 账号安全场景完全缺失** → ✅ W2 dim4（6 TC）
7. **P7 [资深产品] 国际化场景完全缺失** → ✅ W2 dim4 国际化 6 TC（英文/繁体/日文/货币/小数点/时区）
8. **P8 [资深产品] 性能 / 压力场景完全缺失** → ✅ W2 dim4 性能 4 TC（1000 并发查询/100 并发创建/首屏 1s/支付回调堆积）

#### ⏳ Follow-up MAJOR（移交 Round 14）

- **A-003 [MAJOR] S5 双标识 s5_ref vs tp_id 语义重叠** → SSOT 治理（`.cursor/rules/STAGE_S5_TEST_POINTS.mdc` 收敛）
- **A-004 [MAJOR] S6 case_id / tc_id 完全冗余** → SSOT 治理（删除 tc_id 或改名 case_id）

### 1.3 MINOR 级别（5 项 · 全部 follow-up）

| ID | 标题 | 原因 |
|---|---|---|
| Q-013 | 缺机器可读断言字段（`assertion: {field, op, value}`） | 需 LLM 生成阶段扩展，SSOT 改动大 |
| Q-026 | 28 TC 中 unique step action = 23（5 重复） | 同 Q-025 同源问题（OBJMall OBJ-01 内 28 TC step 重复） |
| A-018 | LOG 结构性欠测（同 Q-019） | ✅ 已修复 |
| A-019 | tc_tp_gap_report.md 陈旧（同 Q-018） | ⏳ follow-up |
| A-020 | feature_point_ref 与 fp_name 字段冗余 | 字段治理类 |

---

## §2 根因定位（机制 / 规范 / 习惯）

### 2.1 机制层（代码 bug）

1. **`test_case_formatter._get_field` L828-830 dict repr 渲染**：最严重，纯代码 bug
   - 影响：xlsx 操作步骤列 100% 不可读（Q-007 / A-012）
   - 修复：W1 `_render_list_item` + dict-repr fall-through
   - **教训**：list 元素类型可能是 dict，渲染时需识别常见键名（step_num / action / description 等）

2. **`mirror_bilingual_aliases` 把 list 错误 join 成字符串**：隐藏机制问题
   - 影响：mirror 后 `操作步骤` 字段是 dict repr 字符串而非 list；与 _get_field fallback 形成死锁
   - 修复：W1 `_get_field` 加 dict-repr 字符串 fall-through（防御性兼容）
   - **教训**：list 字段 mirror 应保留 list 类型而非 join 成字符串（SSOT 应明确）

3. **`case_status_writer` 只写 xlsx 不同步回 JSON**：数据契约层
   - 影响：JSON Draft / xlsx Ready 长期不一致（A-011）
   - 修复：W4 xlsx 重导作为补救；根本修复在 case_status_writer 加 `write_to_json=True` 选项
   - **教训**：状态字段应双向同步，SSOT 应明确

4. **`tc_tp_gap_report.md` 生成脚本未随 TC 数量自动重算**：报告陈旧
   - 影响：人工依赖 gap_report 决策会误判覆盖（Q-018 / A-019）
   - 修复：gap_report 重生成 + 自动化（每次 S6 完成自动跑）
   - **教训**：报告生成应是 S6 完成 pipeline 的强制子步骤

### 2.2 规范层（SSOT 缺失 / 不一致）

1. **`s5_ref` vs `tp_id` 双标识语义重叠**：SSOT 字段定义不收敛
   - 影响：S6 TC 引用 S5 TP 时到底用哪个标识？字段语义重叠（A-003）
   - 修复方向：SSOT 收敛为一个字段（建议保留 tp_id 含模块前缀）
   - **教训**：每个实体应有唯一 ID，不应有多 ID 共存

2. **`case_id` vs `tc_id` 完全冗余**：同上
   - 影响：字段治理负担 + 命名不一致（A-004）
   - 修复方向：删除 tc_id 或改名 case_id

3. **8 模块 vs 实际 4 模块**：SSOT 与业务脱节
   - 影响：S6 TC module 分布仅 4 种（UI/BIZ/LOG/SPECIAL），缺 CONFIG/UTIL/LINK/HINT（A-016）
   - 业务判定：游戏道具商城确实只有 4 个相关模块；SSOT 8 模块是通用 SSOT，本项目不必凑齐
   - **教训**：SSOT 应允许子集声明，避免"为了凑齐而凑齐"

4. **`case_id` 命名空间违反 SSOT L136**：s6_generate.py 输出 TC-NNN 而非 {Module}-TC-NNN
   - 影响：normalizer 必须每轮注入前缀（A-008）
   - 修复方向：从源头（s6_generate.py）输出正确格式，避免 normalizer 补丁式修复

5. **`tc_tp_gap_report.md` 缺审计**：报告未与 L1 校验绑定
   - 影响：gap_report 与实际 TC 数量脱节（Q-018）
   - 修复方向：gap_report 应作为 S6 完成 pipeline 的强制子步骤

### 2.3 习惯层（流程 / 实践）

1. **三方审查未在 S6 完成时同步进行**：Round 17 已收敛 331/331 Ready 但未做三方审查
   - 影响：v3.01 已发布但实质可读性差（Q-007/Q-012/Q-019/Q-022/Q-023/Q-025/Q-027 全部埋雷）
   - 修复方向：S6 完成应自动触发 3 角色审查（资深测试 + 架构师 + 资深产品）
   - **教训**：S6 完成 ≠ S7 通过；应有"三方共识"作为 S7 输入

2. **LOG 模块欠测被掩盖**：v3.01 仅 1 TP 但无人在 S7 审查时标记
   - 影响：业务严重欠测（Q-019 / A-018 / 资深产品 P12 三方共识）
   - 修复方向：S7 审查模板必须含"模块覆盖率分布"行

3. **业务盲区靠资深产品兜底**：v3.01 backlog 未列账号安全/国际化/性能场景
   - 影响：6 项 P0 业务问题埋雷（资深产品 P0/P1/P2）
   - 修复方向：S2 backlog 模板必须含"账号安全 + 风控 + 性能 + 国际化"4 类场景清单
   - **教训**：业务盲区应在 S2 阶段由资深产品参与 review，而不是等到 S6/S7

---

## §3 可落地修复方案（下一步动作 + 影响范围）

### 3.1 Round 14 follow-up（移交清单 · 6 项）

#### F-1：A-003 / A-004 SSOT 治理（结构变更）

- **动作**：在 `.cursor/rules/STAGE_S5_TEST_POINTS.mdc` 明确 `tp_id` 是唯一标识，删除 `s5_ref` 字段定义；在 `.cursor/rules/STAGE_S6_TEST_CASES.mdc` 删除 `tc_id` 字段定义
- **影响**：所有 S5/S6 产物 + 工具脚本（run_normalize_and_export / case_id_and_field_normalizer / qa_fixer_v301）需要适配
- **owner**：架构师（SSOT 变更）+ 资深测试（实施）
- **优先级**：P1（不阻塞 v3.01 业务）

#### F-2：Q-018 / A-019 gap_report 自动化（脚本变更）

- **动作**：在 `run_normalize_and_export.py` 末尾加 `tc_tp_gap_report.py` 自动重生成；SSOT 加 "gap_report 是 S6 完成强制子步骤"
- **影响**：每次 S6 完成自动产出与实际 TC 数量同步的 gap_report
- **owner**：架构师（脚本）+ 资深测试（SSOT）
- **优先级**：P1

#### F-3：A-011 case_status_writer 双向同步（代码变更）

- **动作**：在 `case_status_writer.apply_l1_l2_status_per_case` 加 `write_to_json` 选项；默认 True（双向同步）
- **影响**：未来 S7/S8 状态变更同步写 JSON + xlsx
- **owner**：架构师
- **优先级**：P1

#### F-4：Q-013 机器可读断言字段（SSOT + LLM Prompt）

- **动作**：S6 SKILL.md 加 `assertion: {field, op, value}` 字段模板；LLM Prompt 强制每条 TC 含至少 1 个 machine-readable assertion
- **影响**：QA 跑用例时可直接用 assertion 字段做断言（无需人工翻译）
- **owner**：架构师 + 资深测试
- **优先级**：P2

#### F-5：Q-026 OBJ 内 TC step 重复（数据生成约束）

- **动作**：s6_generate.py 加"同 OBJ 内 unique step action ≥ 80%"约束；normalizer 在 dedup 后再扫一遍重复
- **影响**：避免 Q-026 类问题再次出现
- **owner**：架构师
- **优先级**：P2

#### F-6：A-020 feature_point_ref / fp_name 冗余（字段治理）

- **动作**：删除 fp_name 字段；feature_point_ref 已结构化足以反查 fp_name
- **影响**：S6 产物字段减少 1 个；所有读取 fp_name 的脚本需适配
- **owner**：架构师
- **优先级**：P2

### 3.2 后续 Goal 治理建议（移交 Open Questions）

- **Q-Q1**：v3.01 模块清单是否从 8 模块 SSOT 缩为 4 模块（UI/BIZ/LOG/SPECIAL）？业务侧确认 → SSOT 更新
- **Q-Q2**：v3.01 是否需要补 S3/S4 上游产物的字段追溯一致性？架构师议题
- **Q-Q3**：v3.01 三方审查应纳入 S7 自动化触发器，避免"发布后再审查"的滞后

---

## §4 Skill 规范漏洞识别（GL-004）

### 漏洞 1：s6 SKILL.md §11 字段映射表未含 LOG 模块 seed 模板
- **描述**：§11 列了 test_point_type 枚举映射，但未列"如何为 LOG 模块生成 TC"的字段模板
- **出现次数**：1（v3.01）
- **修复**：W3 已在 SKILL.md 加 §LOG seed 模板 + §业务盲区 6 类 TC seed 模板

### 漏洞 2：goal-loop SKILL.md §3.3 audit 模板未含"v3.01 dict repr 自动检测"行
- **描述**：audit 模板要求 8 条 value_criteria + 5 条 process_criteria，但未含 "xlsx 单元格是否有 dict repr" 自动检测行
- **出现次数**：1（v3.01）
- **修复**：本轮 audit_13.md §0 已含"dict repr cells = 0"作为范围合规性检查项；建议 goal-loop SKILL.md §3.3 模板加此行

### 漏洞 3：goal-loop SKILL.md §3.4 review 模板未含"业务盲区 6 类覆盖"行
- **描述**：review 三段式要求缺陷汇总 + 根因 + 修复方案，但未含"业务盲区分类覆盖"硬要求
- **出现次数**：1（v3.01）
- **修复**：建议 goal-loop SKILL.md §3.4 模板加"业务盲区 6 类（账号安全/风控/性能/国际化/边界/业务规则）覆盖检查"行

---

## §5 反模式防御检查（GL-007）

| 反模式 | 防御状态 |
|---|---|
| 只产出不验证 | ✅ W5 物理验证（dict repr=0 + 6 类 TC 计数 + 30 天退款 dup=0） |
| 只因测试通过就宣布目标完成 | ✅ audit_13.md §3 BLOCKER/MAJOR/MINOR 分组 + reverse_challenge |
| 只修局部问题不检查规则/文档一致性 | ✅ W3 SKILL.md 同步更新 |
| 没有证据却给通过结论 | ✅ 8+5 criteria 全部含 evidence + reverse_challenge |
| 验收标准被静默删除/弱化 | ✅ 所有 13 条 criteria 保留，全部 PASS |
| 连续同一种修复处理同根因无新增证据 | ✅ W1 + W2 + W3 各自独立 evidence，不重复 |
| 隐藏未解决问题 | ✅ §1.3 MINOR follow-up 全部列明 + §3.1 F-1 ~ F-6 移交清单 |
| 为通过检查而修改测试/校验器 | ❌ 未发生——未改 L1S6Validator / run_normalize_and_export 既有逻辑（除补 _load_objs_tps 加 'objects' key） |
| 即将执行不可逆/高风险操作 | ⚠️ test_cases_public.xlsx 重导是不可逆的——已备份 .round1.before.bak；test_cases.json 字节不变 |

---

## §6 落档协议执行记录

- **本档路径**：`.goal-log-db/active/32a8ff45-f1a3-4b0b-80af-9e7a9769a5f3/review_13.md`
- **DNA §9.5**：✅ Write 占位后再展开 content
- **DNA §9.4 先验后答**：✅ 已 Read audit_13.md + 三方审查 + snapshot 后回答
- **改动文件清单**：0（review_13.md 是 audit 的姊妹档，不引入新文件改动）

---

> **下一阶段**：交付 snapshot.json 更新（round=2 / status=converged_with_followup / last_audit / last_review / follow_up_items）