#!/usr/bin/env python3
"""Create v303 snapshot."""
import json, os, uuid
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'ai_workflow')

# 生成新 goal_id
gid = str(uuid.uuid4())
dir_path = f'.goal-log-db/active/{gid}'
os.makedirs(dir_path, exist_ok=True)

# 复制 out_of_scope.md
import shutil
shutil.copy('governance/design_iter/plans/v303/out_of_scope.md', f'{dir_path}/out_of_scope.md')

data = {
  "goal_id": gid,
  "raw_user_goal": "/goal-loop 继续推进 v3.03 — 修复 v3.02 CONVERGED 报告 §5.1 BLOCKER follow_up（V-302-002 OBJ P0 覆盖率 1.0）",
  "created_at": "2026-07-20T01:10:00+08:00",
  "goal_signature": "v303_v002_obj_p0_coverage_fix",
  "value_criteria": [
    "[BLOCKER] V-001 xlsx 16/16 OBJ 每 OBJ >= 1 P0（覆盖率 = 1.0）",
    "[BLOCKER] V-002 xlsx 重导后 P0 case >= 16",
    "[MAJOR] V-003 xlsx sheet 主体 + 附录都存在"
  ],
  "process_criteria": [
    "[BLOCKER] P-001 v3.01 test_cases.json hash 不变",
    "[BLOCKER] P-002 round17.bak.xlsx 字节不变",
    "[BLOCKER] P-003 normalizer 业务函数签名不变",
    "[MAJOR] P-004 driver 业务函数签名不变",
    "[BLOCKER] P-005 py_compile + self-test 全过",
    "[MAJOR] P-006 不引入新依赖",
    "[MAJOR] P-007 v3.02 CONVERGED 不删"
  ],
  "value_ratio": 0.3,
  "value_ratio_note": "3 V + 7 P，本 Goal 单一主题 V-302-002",
  "severity_label": "BLOCKER",
  "follow_up_items": [],
  "task_queue": [
    {"id": "T-001", "title": "run_normalize_and_export.py 加 enforce_obj_p0_coverage(cases) 调用", "status": "pending", "artifact": "ai_workflow/run_normalize_and_export.py", "parallelizable": False, "depends_on": [], "parallel_group": 1, "subagent_budget_used": 0},
    {"id": "T-002", "title": "py_compile + normalizer self-test + driver self-test", "status": "pending", "artifact": "runtime", "parallelizable": False, "depends_on": ["T-001"], "parallel_group": 2, "subagent_budget_used": 0},
    {"id": "T-003", "title": "跑 driver 重导 v3.01 xlsx", "status": "pending", "artifact": "test_cases_public.xlsx", "parallelizable": False, "depends_on": ["T-002"], "parallel_group": 3, "subagent_budget_used": 0},
    {"id": "T-004", "title": "openpyxl 物理读 xlsx：16/16 OBJ P0 + P0 >= 16 + sheet 完整", "status": "pending", "artifact": "audit_1.md evidence", "parallelizable": False, "depends_on": ["T-003"], "parallel_group": 4, "subagent_budget_used": 0}
  ],
  "parallel_executor_hints": {"estimated_total_tasks": 4, "parallelizable_count": 0, "groups": [{"group_id": 1, "tasks": ["T-001"], "can_parallel": False, "rationale": "单文件修改"}, {"group_id": 2, "tasks": ["T-002"], "can_parallel": False, "rationale": "依赖 T-001"}, {"group_id": 3, "tasks": ["T-003"], "can_parallel": False, "rationale": "依赖 T-002"}, {"group_id": 4, "tasks": ["T-004"], "can_parallel": False, "rationale": "依赖 T-003"}], "estimated_rounds": 1, "token_budget_per_subagent": 30000},
  "loop_round": 0,
  "last_audit": None,
  "last_review": None,
  "latest_artifact": None,
  "status": "active",
  "token_budget": {"used": 0, "limit": 200000, "updated_at": "2026-07-20T01:10:00+08:00"},
  "out_of_scope_md": f"{dir_path}/out_of_scope.md",
  "audit_stability": {"passed_items": {}, "skipped_stable": {}},
  "efficiency_stats": {}
}
snap_path = f"{dir_path}/snapshot.json"
tmp = snap_path + ".tmp"
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
os.replace(tmp, snap_path)
print(f"Snapshot OK: gid={gid}")
print(f"  path: {snap_path}")
print(f"  status: {data['status']}, task_queue: {len(data['task_queue'])}")

# 把 gid 写到固定路径
with open('.goal-log-db/active/_v303_gid.txt', 'w') as f:
    f.write(gid)
