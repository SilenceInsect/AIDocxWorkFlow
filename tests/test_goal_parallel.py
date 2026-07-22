#!/usr/bin/env python3
"""tests/test_goal_parallel.py — goal-loop 并行化集成测试（v1.2）

测试范围：
  1. 并行依赖解析（depends_on 正确串行，非依赖并行）
  2. subagent 总数限制（>5 时排队）
  3. 跨 goal 快照隔离
  4. 异步 hook 触发（mock subagent）
  5. DAG 边界场景（空图 / 单节点 / 环检测）

运行：
  python3 tests/test_goal_parallel.py
  python3 -m unittest tests.test_goal_parallel -v
"""

import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch as _patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "ai_workflow"))
sys.path.insert(0, str(REPO_ROOT / ".cursor" / "hooks"))


# ===== Shared fixtures =====

class _TempGoalDir:
    """临时 goal 目录 fixture（替代 pytest fixture）。"""

    def __init__(self):
        self.tmp: Path | None = None
        self.original_paths: dict[str, Path] = {}

    def setup(self) -> "Path":
        import goal_snapshot as gs_mod
        import goal_parallel_executor as gpe_mod

        self.tmp = Path(tempfile.mkdtemp())
        # Patch GOALS_DIR / INDEX_DIR / REPO_ROOT
        self.original_paths = {
            "gs_GOALS_DIR": gs_mod.GOALS_DIR,
            "gs_INDEX_DIR": gs_mod.INDEX_DIR,
            "gpe_REPO_ROOT": gpe_mod.REPO_ROOT,
        }
        gs_mod.GOALS_DIR = self.tmp / ".goal-log-db" / "active"
        gs_mod.INDEX_DIR = self.tmp / ".goal-log-db" / "index"
        gpe_mod.REPO_ROOT = self.tmp
        return self.tmp

    def teardown(self) -> None:
        import goal_snapshot as gs_mod
        import goal_parallel_executor as gpe_mod

        gs_mod.GOALS_DIR = self.original_paths["gs_GOALS_DIR"]
        gs_mod.INDEX_DIR = self.original_paths["gs_INDEX_DIR"]
        gpe_mod.REPO_ROOT = self.original_paths["gpe_REPO_ROOT"]


# ===== Import modules =====

from goal_parallel_executor import (
    CyclicDependencyError,
    GoalParallelExecutor,
    MAX_CONCURRENT_SUBAGENTS,
    ParallelGroup,
    SubagentResult,
    TaskNode,
    detect_parallelizable,
)
from goal_snapshot import create_snapshot, load_snapshot


# ===== Test 1: 并行依赖解析 =====

class TestParallelDependencyResolution(unittest.TestCase):
    """T1: depends_on 正确串行，非依赖并行。"""

    def test_empty_tasks(self):
        """T1-1: 空任务列表 → 空分组。"""
        groups = detect_parallelizable([])
        self.assertEqual(groups, [])

    def test_single_task_serial(self):
        """T1-2: 单任务（无 parallelizable）→ 串行分组。"""
        groups = detect_parallelizable([{"id": "T-001", "title": "单任务"}])
        self.assertEqual(len(groups), 1)
        self.assertFalse(groups[0].can_parallel)
        self.assertEqual(groups[0].task_ids, ["T-001"])

    def test_two_independent_parallel(self):
        """T1-3: 两独立并行任务 → 单并行分组。"""
        groups = detect_parallelizable([
            {"id": "T-001", "title": "任务1", "parallelizable": True},
            {"id": "T-002", "title": "任务2", "parallelizable": True},
        ])
        self.assertEqual(len(groups), 1)
        self.assertTrue(groups[0].can_parallel)
        self.assertEqual(set(groups[0].task_ids), {"T-001", "T-002"})

    def test_serial_chain(self):
        """T1-4: 串行依赖链 A→B→C → 3 个串行分组。"""
        groups = detect_parallelizable([
            {"id": "T-001", "title": "A", "depends_on": []},
            {"id": "T-002", "title": "B", "depends_on": ["T-001"]},
            {"id": "T-003", "title": "C", "depends_on": ["T-002"]},
        ])
        self.assertEqual(len(groups), 3)
        self.assertFalse(all(g.can_parallel for g in groups))
        self.assertEqual([g.task_ids for g in groups], [["T-001"], ["T-002"], ["T-003"]])

    def test_mixed_parallel_serial(self):
        """T1-5: 并行+串行混合 → 正确分组。"""
        groups = detect_parallelizable([
            {"id": "T-001", "title": "独立A", "parallelizable": True},
            {"id": "T-002", "title": "依赖A", "depends_on": ["T-001"], "parallelizable": True},
            {"id": "T-003", "title": "串行B", "depends_on": ["T-002"]},
        ])
        self.assertEqual(len(groups), 3)
        self.assertTrue(groups[0].can_parallel)
        self.assertEqual(groups[0].task_ids, ["T-001"])
        self.assertTrue(groups[1].can_parallel)
        self.assertEqual(groups[1].task_ids, ["T-002"])
        self.assertFalse(groups[2].can_parallel)
        self.assertEqual(groups[2].task_ids, ["T-003"])

    def test_cyclic_dependency_raises(self):
        """T1-6: 循环依赖 A→B→A → CyclicDependencyError。"""
        with self.assertRaises(CyclicDependencyError):
            detect_parallelizable([
                {"id": "T-001", "title": "A", "depends_on": ["T-002"]},
                {"id": "T-002", "title": "B", "depends_on": ["T-001"]},
            ])


# ===== Test 2: subagent 总数限制 =====

class TestSubagentBudgetLimit(unittest.TestCase):
    """T2: subagent 总数 ≤ MAX_CONCURRENT_SUBAGENTS。"""

    def test_can_launch_more_under_limit(self):
        """T2-1: < 5 个 subagent 时可继续启动。"""
        executor = GoalParallelExecutor(max_concurrent=5)
        for i in range(4):
            self.assertTrue(executor.can_launch_more())
            executor._subagent_count += 1

    def test_can_launch_more_at_limit(self):
        """T2-2: = 5 个 subagent 时不可再启动。"""
        executor = GoalParallelExecutor(max_concurrent=5)
        for i in range(5):
            executor._subagent_count += 1
        self.assertFalse(executor.can_launch_more())

    def test_max_concurrent_constant(self):
        """T2-3: MAX_CONCURRENT_SUBAGENTS = 5。"""
        self.assertEqual(MAX_CONCURRENT_SUBAGENTS, 5)


# ===== Test 3: 跨 goal 快照隔离 =====

class TestGoalSnapshotIsolation(unittest.TestCase):
    """T3: 多 goal 快照独立，无状态竞争。"""

    def setUp(self):
        self.fixture = _TempGoalDir()
        self.fixture.setup()

    def tearDown(self):
        self.fixture.teardown()

    def test_two_goals_independent(self):
        """T3-1: 两个 goal 快照独立，互不影响。"""
        snap1 = create_snapshot("Goal1 目标", ["标准1"], token_limit=1000)
        snap2 = create_snapshot("Goal2 目标", ["标准1"], token_limit=1000)
        loaded1 = load_snapshot(snap1["goal_id"])
        loaded2 = load_snapshot(snap2["goal_id"])
        self.assertEqual(loaded1["goal_id"], snap1["goal_id"])
        self.assertEqual(loaded2["goal_id"], snap2["goal_id"])
        self.assertNotEqual(loaded1["goal_id"], loaded2["goal_id"])
        self.assertNotEqual(loaded1["raw_user_goal"], loaded2["raw_user_goal"])

    def test_parallel_executor_hints_initialized(self):
        """T3-2: 新建 goal 的 parallel_executor_hints = {}。"""
        snap = create_snapshot("并行测试", ["标准1"], token_limit=1000)
        self.assertIn("parallel_executor_hints", snap)
        self.assertEqual(snap["parallel_executor_hints"], {})

    def test_task_queue_exists(self):
        """T3-3: task_queue 字段存在且为空列表。"""
        snap = create_snapshot("并行任务", ["标准1"], token_limit=1000)
        self.assertIn("task_queue", snap)
        self.assertIsInstance(snap["task_queue"], list)


# ===== Test 4: 异步 hook 触发（mock） =====

class TestAsyncHookTrigger(unittest.TestCase):
    """T4: hook 异步触发（mock subagent，不真实启动进程）。"""

    def setUp(self):
        self.fixture = _TempGoalDir()
        self.fixture.setup()

    def tearDown(self):
        self.fixture.teardown()

    def test_hook_queue_file_written(self):
        """T4-1: _spawn_async_subagent 写 queue 文件。"""
        import goal_loop_breakloop_hook as glbh_mod

        snap = create_snapshot("Hook 测试", ["标准1"], token_limit=1000)
        with _patch("subprocess.Popen"):
            glbh_mod._spawn_async_subagent(
                "afterFileEdit",
                {"goal_id": snap["goal_id"], "file_path": "/tmp/test.md"},
            )
        queue_files = list(glbh_mod.HOOK_QUEUE_DIR.glob("*.json"))
        self.assertGreaterEqual(len(queue_files), 1)
        content = json.loads(queue_files[0].read_text())
        self.assertEqual(content["event"], "afterFileEdit")
        self.assertEqual(content["status"], "pending")

    def test_session_start_injects_reminder(self):
        """T4-2: sessionStart 注入 reminder（使用 session_resume_multi_goal）。"""
        import session_resume_multi_goal as srmg_mod

        snap = create_snapshot("续跑测试", ["标准1"], token_limit=1000)
        buf = io.StringIO()
        with _patch("sys.stdout", buf):
            rc = srmg_mod.handle_session_start_multi_goal({})
        self.assertEqual(rc, 0)
        captured = buf.getvalue().strip()
        self.assertTrue(captured, "应注入 reminder")
        out = json.loads(captured)
        self.assertIn("续跑", out["system_reminder"])


# ===== Test 5: DAG 边界场景 =====

class TestDAGEdgeCases(unittest.TestCase):
    """T5: DAG 边界场景。"""

    def test_missing_dependency_ignored(self):
        """T5-1: 依赖不存在的 task_id → 该依赖被忽略（入度=0），两任务为1个串行组。"""
        groups = detect_parallelizable([
            {"id": "T-001", "title": "A", "depends_on": []},
            {"id": "T-002", "title": "B", "depends_on": ["NONEXISTENT"]},
        ])
        # NONEXISTENT 不在 nodes 中被忽略 → T-002 入度=0
        # T-001 和 T-002 均无 parallelizable=true → 同为串行，按 ID 顺序 → 1 个串行组
        self.assertEqual(len(groups), 1)
        self.assertFalse(groups[0].can_parallel)
        self.assertEqual(set(groups[0].task_ids), {"T-001", "T-002"})

    def test_all_parallel_no_depends(self):
        """T5-2: 全parallelizable无依赖 → 单并行分组。"""
        groups = detect_parallelizable([
            {"id": "T-001", "title": "A", "parallelizable": True},
            {"id": "T-002", "title": "B", "parallelizable": True},
            {"id": "T-003", "title": "C", "parallelizable": True},
        ])
        self.assertEqual(len(groups), 1)
        self.assertTrue(groups[0].can_parallel)
        self.assertEqual(set(groups[0].task_ids), {"T-001", "T-002", "T-003"})

    def test_execute_parallel_returns_all_tasks(self):
        """T5-3: execute_parallel 返回所有任务（stub）。"""
        executor = GoalParallelExecutor(max_concurrent=5)
        tasks = [
            {"id": "T-001", "title": "A", "parallelizable": True},
            {"id": "T-002", "title": "B", "parallelizable": True},
        ]
        results = executor.execute_parallel(tasks, "test-goal")
        self.assertEqual(len(results), 2)
        self.assertTrue(all(isinstance(r, SubagentResult) for r in results))

    def test_summarize_results_updates_queue(self):
        """T5-4: summarize_results 正确更新 task_queue。"""
        executor = GoalParallelExecutor(max_concurrent=5)
        task_queue = [
            {"id": "T-001", "title": "任务1", "status": "pending"},
            {"id": "T-002", "title": "任务2", "status": "pending"},
        ]
        results = [
            SubagentResult(task_id="T-001", status="done", artifact="/path/t1.md", token_used=5000),
            SubagentResult(task_id="T-002", status="done", artifact="/path/t2.md", token_used=6000),
        ]
        updated, merged = executor.summarize_results(task_queue, results, goal_id="g001")
        self.assertEqual(updated[0]["status"], "done")
        self.assertEqual(updated[0]["artifact"], "/path/t1.md")
        self.assertEqual(updated[0]["subagent_budget_used"], 5000)
        self.assertEqual(updated[1]["status"], "done")
        self.assertIsNotNone(merged)
        self.assertIn("manifest.json", merged)


# ===== Test 6: goal_parallel_executor CLI =====

class TestCLI(unittest.TestCase):
    """T6: goal_parallel_executor detect CLI。"""

    def test_detect_cli_json_output(self):
        """T6-1: detect 子命令 --json-output。"""
        tasks = json.dumps([
            {"id": "T-001", "title": "A", "parallelizable": True},
            {"id": "T-002", "title": "B", "parallelizable": True},
        ])
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "ai_workflow" / "goal_parallel_executor.py"),
                "detect", "--tasks", tasks, "--json-output",
            ],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output = json.loads(proc.stdout)
        self.assertEqual(len(output), 1)
        self.assertTrue(output[0]["can_parallel"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
