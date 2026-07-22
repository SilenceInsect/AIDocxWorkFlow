# out_of_scope.md — v3.02 跟进清单 Goal 禁区

## 功能禁区
- 不改 v3.01 `test_cases.json` 内容（SSOT 守住，P-001 约束）
- 不删 Round 17 历史 xlsx 备份（P-002 字节不变）
- 不改 v3.01 S5/S6 阶段产出（PROTECT 输入不动）
- 不删 v18 治理档（已闭环保留为审计锚点，P-005）
- 不动 v27 当前治理档（v27 闭环刚完成，§9.1 红线保护）
- 不修无 v3.01 Round 18 审查报告佐证的新问题（避免范围蔓延）
- 不动 S6 校验脚本（`validators/l1_s6.py` / `l2_s6.py`）— 校验器是 S7 审查工具，本 Goal 是数据修复

## 技术栈禁区
- 不引入新依赖（pandas / openpyxl / pytest 不在新增列表）
- 不修改 `case_id_and_field_normalizer.py` 业务函数签名（P-003 约束）
- 不修改 `test_case_formatter.py` 业务函数签名（P-003 约束）
- 不在 normalizer 内调用 LLM / 网络 / eval（避免副作用）
- 不改 xlsx 写入逻辑（仅触发重导，写入路径走原 `_save_xlsx`）

## 职责边界禁区
- 不处理 v17 5 项卡 AI 自治约束（v28+ carry，本 Goal 是 v3.01 数据修复）
- 不处理 v22+ 阶段产物
- 不动 goal-loop SKILL.md 自身（本 Goal 是数据实例修复，非 SKILL 迭代）
- 不动 hooks.json（v27 刚改完，不要在同会话叠加修改）
- 不重做 v3.01 S1-S5 阶段产物（仅 S6 数据修复 + xlsx 重导出）

## 历史坑点禁区
- 不要把 ID 重排当作"业务变更"（v3.01 87 TC ID 是 baseline，重排是修复）
- 不要因为 "test_cases.json 已经有 ID" 就跳过连续性校验（V-001 BLOCKER）
- 不要合并不同 OBJ 的 P0 用例（V-002 要求每 OBJ 至少 1 P0）
- 不要把"重复"当"无意义"删掉（保序去重 ≠ 任意去重，V-003）
- 不要为追求覆盖率把 MAJOR 改 BLOCKER 凑数（V-002 是"补" 不是"提级"）

## 本 Goal 完成后禁止
- 不得回退 v3.01 已有 BLOCKER 字段（仅允许"修"，禁止"破坏")
- 不得为追求 PASS 而删除 BLOCKER 验收项（违反 F2 反模式）
- 不得在 xlsx 主表追加未在 test_cases.json 出现的行（数据不一致 = BLOCKER 失败）
