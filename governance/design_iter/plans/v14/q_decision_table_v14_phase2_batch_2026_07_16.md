# v14 §5 第二阶段批量完成决策表（2026-07-16）

## 用户拍板

用户原话：
> 继续 → 选择 `phase2-all`：一次性补齐第二阶段剩余 2 项

## §9.1 红线冲突说明

**违反**：
- §9.1 "单次响应文件改动数 ≤ 3 个"——本轮 ≥ 5 文件
- §9.1.1 self-test 豁免**不适用**（不是 self-test，是业务功能）

**允许条件**：用户明示"批量改 / 全补"（§9.1 倒数第 2 行）——**你说了"phase2-all"= 全补，符合白名单触发**。

## 第二阶段 2 项范围（外部方案 §5）

| # | 优化项 | 具体改动 | 涉及文件 | 预期收益 |
|---|---|---|---|---|
| ② | 覆盖率分级机制 | S2 FP 优先级 + S6/S7 分级覆盖率 | S2 字段规范 + S6/S7 门禁 | 用例价值密度提升 |
| ③ | 例外率监控 | bypass_log 增加统计维度 + 预警 | S7 审查脚本 + 报告模板 | 防止例外滥用 |

## 候选方案（已拍板 phase2-all）

按 §9.5 落档 + §3.7 SOP 强制验证：
1. **新建 `ai_workflow/s6_coverage_gate.py`**（覆盖率分级门禁——P0 ≥95% / P1 ≥80% / P2 ≥50%）
2. **新建 `scripts/bypass_log_aggregator.py`**（bypass_log 聚合 + 例外率趋势 + 预警）
3. **新建 `workflow_assets/_example/bypass_log_example.json`**（bypass_log 文件示例——SSOT）
4. **S6 SKILL.md 追加 §S6 覆盖率门禁 + 引用新脚本**
5. **S7 SKILL.md 追加 §S7 例外率聚合 + 引用新脚本 + bypass_log 写入路径**
6. **STAGE_S6/S7 .mdc 加执行卡 P0/P1/P2 行**（引用 SSOT）
7. **INDEX.md §1 v14 进度更新**（第二阶段 33% → 100%）

**总文件数 = 7**——**严重超红线**，**但用户明示"全补"**。

## 影响范围

| 文件 | 改动 | 风险 |
|---|---|---|
| `ai_workflow/s6_coverage_gate.py` | 新建 ~200 行 | 中（新增脚本需 self-test）|
| `scripts/bypass_log_aggregator.py` | 新建 ~250 行 | 中（新增脚本需 self-test）|
| `workflow_assets/_example/bypass_log_example.json` | 新建示例 | 低（SSOT 参考）|
| `.cursor/skills/aidocx-s6-test-cases/SKILL.md` | 追加 §S6 覆盖率门禁 | 低（追加，不改现有）|
| `.cursor/skills/aidocx-s7-review/SKILL.md` | 追加 §S7 例外率聚合 | 低（追加）|
| `.cursor/rules/STAGE_S6_TEST_CASES.mdc` | 执行卡加 P0/P1/P2 | 低（追加一行）|
| `.cursor/rules/STAGE_S7_REVIEW.mdc` | 执行卡加 bypass_log | 低（追加一行）|
| `governance/design_iter/INDEX.md` | §1 v14 进度 33% → 100% | 低（同步）|

**8 文件总**——比初估 7 多 1（两个 .mdc 加 1 行）。

## 执行顺序（按 §3.7 SOP）

1. **Read 全部 8 个目标文件**（先验 §9.4）
2. **写 2 个新脚本**（含 `def self_test()`）
3. **追加 S6/S7 SKILL.md**（追加，不删现有）
4. **追加 .mdc**（追加 1 行）
5. **建 bypass_log 示例**
6. **更新 INDEX.md**
7. **§3.7 全量验证**（py_compile × 2 + self-test × 2 + JSON 合法性 + grep 引用）

## 自检豁免判断

§9.1.1 self-test 豁免条件 4：
- 1. ✅ 含 `def self_test()`（按 §9.1.1 要求）
- 2. ✅ 含 `--self-test` argv 分支
- 3. ✅ 本次改动**不修改任何业务函数签名或参数**（只新增脚本 + 追加 SKILL.md 段）
- 4. ⚠️ 改动文件 = 8 > 6 → **豁免失效**（按 §9.1.1 失效条件）

**结论**：本轮**不享受豁免**——但**用户明示"全补"覆盖**了红线。

## 等待确认

无（用户已拍板）。直接执行。

## 落档协议执行记录

（本文件即落档——§9.5 合规）