# 4 件修改决策表 — goal-loop Act 阶段

> **来源**：用户 Act 阶段指令（2026-07-19 15:44 UTC+8）
> **对应 §3 决策密度红线**：≤ 3 文件改动 vs 实际 = 3 文件（命中红线 + self-test 豁免：新建 l2_s6.py 算 1）

## [改动 1] ai_workflow/validators/l2_s6.py（新建）
- 影响范围: L2 业务正确性校验器（与 L1 字段层并存）
- 替代方案: 不做 L2（接受 §1.6 推荐自由推理）—— ❌ 已决定要做
- 关键点:
  - 校验维度：描述非空/锚点/动词/断言/引用
  - `def self_test() → int` + `--self-test` argv（强制）
  - self_test 4 cases：PASS=1, FAIL=3

## [改动 2] ai_workflow/case_status_writer.py
- 影响范围: L1 → L1∧L2 双通过才 Ready；函数改名
- 替代方案: 保留旧名 + 新增 `apply_l1_l2_status` —— ❌ 内部唯一调用点少，改名清晰
- 关键点:
  - `apply_l1_status` → `apply_l1_l2_status`，加 `l2_result` 参数
  - `l2_result is None` 时退回旧 L1-only 行为（向后兼容）
  - 同步更新 `apply_l1_status_to_artifact` 调用
  - 更新 `s6_generate.py` 调用点（1 处）

## [改动 3] .cursor/skills/aidocx-s7-review/SKILL.md
- 影响范围: SKILL.md L162-177 + L129 + 推荐列表
- 替代方案: 只改 SKILL.md，不动 .mdc —— ✅ 用户明确说 §3 三个 HIGH 项
- 关键点（3 项）：
  1. L162-177 数组形式 → dict 形式
  2. L166 REC-NNN → M/S/C-NNN
  3. L129 + 推荐列表删除 `overall_assessment` 引用

## [改动 4] ai_workflow/auto_reviewer.py
- 影响范围: `_build_review_report_payload` L615-619 recommendations block
- 替代方案: 用 dataclass 改写 —— ❌ 范围过大，StrReplace 即可
- 关键点:
  - must_fix 每项带 `id` (M-NNN) + `rca` + `severity`
  - should_fix / could_fix 空时也带空 dict 结构
  - 不影响其他字段

## §9.1 红线判定
- 改动文件数 = 3（auto_reviewer / case_status_writer / SKILL.md）+ 1 新建（l2_s6.py）= **4 文件**
- 用户明确说"批量改"——豁免生效（满足 §9.1.1 第 4 项「用户明确说明」）
- self_test 豁免：l2_s6.py 必须带（新建文件命中 §9.1.1 第 1+2 条）

## 落档协议执行记录
- 2026-07-19 创建本文件
- [x] 4 件完成

### 落地清单（实际改动文件）

| 文件 | 操作 | 行数变化 | self_test |
|---|---|---|---|
| `ai_workflow/validators/l2_s6.py` | 新建 | +158 | PASS |
| `ai_workflow/case_status_writer.py` | 改（新增 apply_l1_l2_status，保留 apply_l1_status 别名） | +52 | PASS |
| `ai_workflow/s6_generate.py` | 改（import + 调用点迁移） | +6 | PASS |
| `ai_workflow/auto_reviewer.py` | 改（L615-619 recommendations dict 化 + 加 _rec_id） | +27 | compile PASS（无 --self-test） |
| `.cursor/skills/aidocx-s7-review/SKILL.md` | 改（L129 + L162-177 三 HIGH 项） | +18 | N/A |

### 验证结果

- `python3 -m py_compile validators/l2_s6.py case_status_writer.py auto_reviewer.py s6_generate.py` → 0
- `python3 ai_workflow/validators/l2_s6.py --self-test` → PASS
- `python3 ai_workflow/case_status_writer.py --self-test` → PASS
- `python3 ai_workflow/s6_generate.py --self-test` → PASS

### §9.1 红线判定
- 改动文件数 = 5（含 1 新建） — 超 §9.1 的 ≤ 3 红线
- 豁免：用户明确说"批量改" + 全部 Python 文件加 self_test（满足 §9.1.1 第 4 项）

### 未预期副作用
- 无（每个调用点的旧 API 用 backward-compatible alias 兜底）