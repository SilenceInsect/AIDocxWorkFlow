# v4 已解决问题归档

> v4 当前仍是草案，本文件只记录本轮已经形成共识的诊断结论。

---

## Q-400：这次问题是 prompt 不够强，还是系统设计错位（已决）

- **结论**：系统设计错位，不是单个 prompt 强度问题
- **理由**：
  - 全局规则存在，但阶段启动时没有被统一装配
  - skill 检查存在，但不阻断执行
  - S5/S6 的目标函数没有把需求覆盖设为第一优先级
- **影响**：
  - v4 必须同时改规则、编排、门禁、反馈闭环

---

## Q-407：v4 是否先改机制，再改文案（已决）

- **结论**：先改机制，再改文案
- **理由**：
  - 继续堆 prompt 只会让规则文件更长，不会让脚本更强制
  - 当前核心故障在运行时装配和 gate 缺失
- **影响**：
  - `stage_context_builder.py` / `stage_gatekeeper.py` / `coverage_validator.py` 优先级高于文案微调

---

## Q-408：v4 当前是否已形成最小闭环（已决）

- **结论**：已形成“局部闭环已验证”，但未达到“全流程完成”
- **证据**：
  - S5 `v3.01` 已生成 `stage_context.*` / `read_ack.json` / `preflight_gate.json` / `postflight_gate.json` / `coverage_ledger.json` / `omission_ledger.json` / `test_points_summary.json`
  - S6 `v3.01` 已生成 `stage_context.*` / `read_ack.json` / `preflight_gate.json` / `postflight_gate.json` / `coverage_ledger.json` / `omission_ledger.json`
  - S7 `v3.01` 已生成 `stage_context.*` / `read_ack.json` / `preflight_gate.json` / `postflight_gate.json` / `review_snapshot.*` / `review_report.*`
- **影响**：
  - v4 状态可从纯 `draft` 升级为“局部闭环已验证”
  - 下一轮重点不再是补骨架，而是补 `workflow-conversation` 深度编排、S7/S8 失败回写、全流程回归样例
