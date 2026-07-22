#!/usr/bin/env python3
"""Goal Loop 并行执行器（v1.2 新增）

v1.2 并行化扩展核心模块。

功能：
  1. DAG 依赖解析：根据 task_queue 的 depends_on 构建有向无环图，
     计算拓扑序，返回可并行执行的分组列表
  2. 并行执行：检测 parallelizable=true 且入度=0 的任务，
     分批调用 subagent（Task 工具）执行（≤ MAX_CONCURRENT_SUBAGENTS）
  3. 结果汇总：将各 subagent 的产物（artifact 路径）合并，
     更新 task_queue，返回统一 artifact

Schema（task_queue 子任务 v1.2）：
  {
    "id": "T-001",
    "title": "...",
    "status": "pending | running | done | skipped",
    "artifact": "path/to/artifact.md",
    "parallelizable": true,
    "depends_on": ["T-002"],
    "parallel_group": 1,
    "subagent_budget_used": 0
  }

用法（Act 阶段）：
  from goal_parallel_executor import GoalParallelExecutor, MAX_CONCURRENT_SUBAGENTS
  executor = GoalParallelExecutor(max_concurrent=MAX_CONCURRENT_SUBAGENTS)
  groups = executor.detect_parallelizable(task_queue)
  results = executor.execute_parallel(task_queue, goal_id)
  updated_queue, merged_artifact = executor.summarize_results(task_queue, results)
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "ai_workflow"))

try:
    from goal_snapshot import update_snapshot, load_snapshot  # noqa: E402
except Exception:  # pragma: no cover
    update_snapshot = None  # type: ignore
    load_snapshot = None  # type: ignore


# ===== 常量 =====

MAX_CONCURRENT_SUBAGENTS: int = 5
"""subagent 并行执行上限（v1.2 并行约束 §11.4）"""

DEFAULT_SUBAGENT_BUDGET: int = 50_000
"""每个 subagent 默认 token 预算"""


# ===== 数据结构 =====

@dataclass
class TaskNode:
    """DAG 节点（对应 task_queue 中单个任务）。"""
    task_id: str
    title: str
    parallelizable: bool = False
    depends_on: list[str] = field(default_factory=list)
    parallel_group: int = 0
    status: str = "pending"
    artifact: str | None = None
    subagent_budget_used: int = 0

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TaskNode":
        return cls(
            task_id=str(d.get("id", "")),
            title=str(d.get("title", "")),
            parallelizable=bool(d.get("parallelizable", False)),
            depends_on=list(d.get("depends_on") or []),
            parallel_group=int(d.get("parallel_group") or 0),
            status=str(d.get("status", "pending")),
            artifact=d.get("artifact"),
            subagent_budget_used=int(d.get("subagent_budget_used") or 0),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.task_id,
            "title": self.title,
            "parallelizable": self.parallelizable,
            "depends_on": self.depends_on,
            "parallel_group": self.parallel_group,
            "status": self.status,
            "artifact": self.artifact,
            "subagent_budget_used": self.subagent_budget_used,
        }


@dataclass
class ParallelGroup:
    """一个可并行执行的批次。"""
    group_id: int
    tasks: list[TaskNode]
    can_parallel: bool  # True=真正并行，False=降级串行

    @property
    def task_ids(self) -> list[str]:
        return [t.task_id for t in self.tasks]


@dataclass
class SubagentResult:
    """单个 subagent 的执行结果。"""
    task_id: str
    status: str  # "done" | "failed" | "skipped"
    artifact: str | None = None
    error: str | None = None
    token_used: int = 0


# ===== 异常 =====


class ParallelExecutorError(Exception):
    """并行执行器通用错误。"""


class CyclicDependencyError(ParallelExecutorError):
    """检测到循环依赖（DAG 无法拓扑排序）。"""


# ===== DAG 依赖解析 =====

def _build_dag(tasks: list[dict[str, Any]]) -> tuple[dict[str, TaskNode], dict[str, list[str]]]:
    """构建 DAG。

    Returns:
        (nodes, adj) — nodes: task_id → TaskNode；adj: task_id → [依赖者列表]
    """
    nodes: dict[str, TaskNode] = {}
    adj: dict[str, list[str]] = defaultdict(list)  # task_id → dependent tasks

    # Step 1: 创建所有节点
    for t in tasks:
        node = TaskNode.from_dict(t)
        nodes[node.task_id] = node
        adj[node.task_id] = []

    # Step 2: 构建边（依赖关系）
    for task_id, node in nodes.items():
        for dep_id in node.depends_on:
            if dep_id not in nodes:
                # 依赖的 task 不存在，忽略（防止脏数据导致全量失败）
                continue
            # dep_id → task_id（有向边：dep 是 task 的前置）
            adj[dep_id].append(task_id)

    return nodes, adj


def _compute_in_degree(
    nodes: dict[str, TaskNode], adj: dict[str, list[str]]
) -> dict[str, int]:
    """计算每个节点的入度（in-degree）。

    入度 = 前置依赖未完成的数量（初始 = depends_on 长度）。
    """
    in_degree: dict[str, int] = {}
    for task_id, node in nodes.items():
        # 只计入实际存在的依赖
        valid_deps = [d for d in node.depends_on if d in nodes]
        in_degree[task_id] = len(valid_deps)
    return in_degree


def _detect_cycle(
    nodes: dict[str, TaskNode], adj: dict[str, list[str]]
) -> list[str] | None:
    """DFS 检测环。

    Returns:
        环中节点列表（首个节点即入口），无环则返回 None。
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {tid: WHITE for tid in nodes}
    parent: dict[str, str | None] = {tid: None for tid in nodes}

    def dfs(tid: str) -> str | None:
        color[tid] = GRAY
        for dep_id in nodes[tid].depends_on:
            if dep_id not in nodes:
                continue
            if color[dep_id] == GRAY:
                # 发现环：回溯 parent 构建环路径
                cycle = [dep_id, tid]
                cur = tid
                while parent.get(cur) and parent[cur] != dep_id:
                    cur = parent[cur]
                    cycle.append(cur)
                cycle.reverse()
                return cycle[0] if cycle else dep_id
            if color[dep_id] == WHITE and dfs(dep_id) is not None:
                return dep_id
        color[tid] = BLACK
        return None

    for tid in nodes:
        if color[tid] == WHITE:
            parent[tid] = None
            result = dfs(tid)
            if result is not None:
                return list(nodes.keys())
    return None


# ===== 并行分组检测 =====

def detect_parallelizable(tasks: list[dict[str, Any]]) -> list[ParallelGroup]:
    """检测可并行执行的分组（基于 DAG 拓扑排序）。

    算法：
      1. 构建 DAG（nodes + adj）
      2. 检测循环依赖（_detect_cycle）→ 有环则抛出异常
      3. 计算入度（_compute_in_degree）
      4. BFS 拓扑序：
         - 入度 = 0 且 parallelizable=true → 真正并行分组（can_parallel=True）
         - 入度 = 0 但 parallelizable=false → 降级串行（can_parallel=False）
         - 入度 > 0 → 等待前置完成
      5. 每轮输出一个批次，批次内可并行的任务并行执行
      6. 批次执行完后更新入度，继续下一轮

    Returns:
        ParallelGroup 列表（按执行顺序排列）。

    Raises:
        CyclicDependencyError: 检测到循环依赖。
    """
    if not tasks:
        return []

    nodes, adj = _build_dag(tasks)

    # 检测环
    if _detect_cycle(nodes, adj) is not None:
        raise CyclicDependencyError(
            f"检测到循环依赖，涉及任务：{list(nodes.keys())}"
        )

    in_degree = _compute_in_degree(nodes, adj)
    completed: set[str] = set()
    groups: list[ParallelGroup] = []
    group_counter = 1

    while len(completed) < len(nodes):
        # 找出本轮可执行的任务（入度 = 0 且未完成）
        ready_parallel: list[TaskNode] = []
        ready_serial: list[TaskNode] = []

        for tid, node in nodes.items():
            if tid in completed:
                continue
            # 入度归零意味着所有前置依赖已完成
            if in_degree.get(tid, 0) == 0:
                if node.parallelizable:
                    ready_parallel.append(node)
                else:
                    ready_serial.append(node)

        if not ready_parallel and not ready_serial:
            # 理论上不应该发生（有 DAG + 无环保障）
            remaining = [tid for tid in nodes if tid not in completed]
            raise ParallelExecutorError(f"无法继续调度，剩余任务：{remaining}")

        # 先输出可并行批次（优先并行）
        if ready_parallel:
            groups.append(ParallelGroup(
                group_id=group_counter,
                tasks=ready_parallel,
                can_parallel=True,
            ))
            group_counter += 1

        # 再输出降级串行批次
        if ready_serial:
            groups.append(ParallelGroup(
                group_id=group_counter,
                tasks=ready_serial,
                can_parallel=False,
            ))
            group_counter += 1

        # 标记本轮任务为完成，更新入度
        for node in ready_parallel + ready_serial:
            completed.add(node.task_id)
            for dependent in adj.get(node.task_id, []):
                if dependent in in_degree:
                    in_degree[dependent] -= 1

    return groups


# ===== 并行执行（stub：实际由 Task 工具调用 subagent） =====

class GoalParallelExecutor:
    """并行执行器主类。"""

    def __init__(self, max_concurrent: int = MAX_CONCURRENT_SUBAGENTS) -> None:
        self.max_concurrent = max_concurrent
        self._subagent_count = 0

    @property
    def subagent_count(self) -> int:
        return self._subagent_count

    def execute_parallel(
        self,
        task_queue: list[dict[str, Any]],
        goal_id: str,
    ) -> list[SubagentResult]:
        """并行执行 task_queue 中的 parallelizable 任务。

        实际 subagent 调用由上层（Act 阶段）通过 Task 工具执行，
        本函数只返回执行计划（哪些任务在哪个批次并行）。

        Returns:
            SubagentResult 列表（与 task_queue 一一对应）。

        实现说明（v1.2）：
          - 本函数是 stub，实际并行由 Act 阶段使用 Task 工具实现
          - 产出的结果通过 summarize_results() 合并
          - subagent 调用示例（Act 阶段）：
              executor = GoalParallelExecutor()
              groups = executor.detect_parallelizable(task_queue)
              for group in groups:
                  if group.can_parallel:
                      # Task(subagent_type="generalPurpose", run_in_background=True, ...)
                      pass
        """
        groups = detect_parallelizable(task_queue)
        results: list[SubagentResult] = []

        for group in groups:
            for task in group.tasks:
                # stub：实际执行由 Task 工具完成
                results.append(SubagentResult(
                    task_id=task.task_id,
                    status="pending",  # 待 Act 阶段填充
                    artifact=None,
                    error=None,
                    token_used=0,
                ))
                if group.can_parallel:
                    self._subagent_count += 1

        return results

    def summarize_results(
        self,
        task_queue: list[dict[str, Any]],
        subagent_results: list[SubagentResult],
        goal_id: str = "unknown",
    ) -> tuple[list[dict[str, Any]], str | None]:
        """汇总 subagent 结果，合并产物，更新 task_queue。

        Args:
            task_queue: 原始 task_queue
            subagent_results: 各 subagent 执行结果

        Returns:
            (updated_task_queue, merged_artifact_path) — 更新后的队列 + 合并产物路径

        合并规则：
          - status = "done" 且有 artifact → 更新 task_queue 对应项
          - 合并 artifact：生成 `_parallel_merge/{goal_id}/` 目录，
            将所有产物路径写入 manifest.json
        """
        # 构建 task_id → result 映射
        result_map: dict[str, SubagentResult] = {
            r.task_id: r for r in subagent_results
        }

        updated_queue: list[dict[str, Any]] = []
        merged_artifacts: list[str] = []

        for task in task_queue:
            task_id = task.get("id", "")
            result = result_map.get(task_id)

            updated = dict(task)
            if result:
                updated["status"] = result.status
                updated["artifact"] = result.artifact
                updated["subagent_budget_used"] = result.token_used
                if result.status == "done" and result.artifact:
                    merged_artifacts.append(result.artifact)
            updated_queue.append(updated)

        # 生成合并 manifest
        merged_artifact: str | None = None
        if merged_artifacts:
            merge_dir = REPO_ROOT / ".goal-log-db" / "parallel-merge" / goal_id
            merge_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = merge_dir / "manifest.json"
            manifest_path.write_text(
                json.dumps({
                    "goal_id": goal_id,
                    "artifacts": merged_artifacts,
                    "merged_at": _now_iso(),
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            merged_artifact = str(manifest_path)

        return updated_queue, merged_artifact

    def can_launch_more(self) -> bool:
        """检查是否可继续启动 subagent（不超过上限）。"""
        return self._subagent_count < self.max_concurrent


# ===== 工具函数 =====

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# ===== CLI =====

def _cli(argv: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Goal Parallel Executor CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_detect = sub.add_parser("detect", help="检测 task_queue 的并行分组")
    p_detect.add_argument("--tasks", required=True, help="JSON 字符串的 task_queue")
    p_detect.add_argument("--json-output", action="store_true", help="输出 JSON")

    args = parser.parse_args(argv)

    if args.cmd == "detect":
        tasks = json.loads(args.tasks)
        groups = detect_parallelizable(tasks)
        if args.json_output:
            output = [
                {
                    "group_id": g.group_id,
                    "task_ids": g.task_ids,
                    "can_parallel": g.can_parallel,
                }
                for g in groups
            ]
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            for g in groups:
                mode = "PARALLEL" if g.can_parallel else "SERIAL"
                print(f"Group {g.group_id} [{mode}]: {g.task_ids}")
        return 0

    parser.print_help()
    return 1


# ===== Self-test =====

def self_test() -> int:
    """python3 ai_workflow/goal_parallel_executor.py --self-test

    验证 8 项：
      1. 无任务 → 空分组列表
      2. 单任务 → 单分组（降级串行，因为 parallelizable=false）
      3. 两独立并行任务（parallelizable=true，互不依赖）→ 单并行分组
      4. 串行依赖链 A→B→C → 3 个串行分组
      5. 并行+串行混合
      6. 循环依赖检测（CyclicDependencyError）
      7. summarize_results 正确更新 task_queue
      8. can_launch_more 正确判断
    """
    from pathlib import Path
    import tempfile

    # Case 1: 空任务列表
    groups = detect_parallelizable([])
    assert groups == [], f"Case 1: 应返回空列表, got {groups}"
    print("  [OK] Case 1: 空任务 → 空分组列表")

    # Case 2: 单任务（无 parallelizable）
    groups = detect_parallelizable([{"id": "T-001", "title": "单任务"}])
    assert len(groups) == 1, f"Case 2: 应 1 分组, got {len(groups)}"
    assert groups[0].can_parallel is False, "Case 2: 应降级串行"
    print("  [OK] Case 2: 单任务 → 串行分组")

    # Case 3: 两独立并行任务
    groups = detect_parallelizable([
        {"id": "T-001", "title": "任务1", "parallelizable": True},
        {"id": "T-002", "title": "任务2", "parallelizable": True},
    ])
    assert len(groups) == 1, f"Case 3: 应 1 分组, got {len(groups)}"
    assert groups[0].can_parallel is True, "Case 3: 应真正并行"
    assert set(groups[0].task_ids) == {"T-001", "T-002"}, f"Case 3: 任务ID不匹配, got {groups[0].task_ids}"
    print("  [OK] Case 3: 两独立并行任务 → 单并行分组")

    # Case 4: 串行依赖链 A→B→C
    groups = detect_parallelizable([
        {"id": "T-001", "title": "A", "depends_on": []},
        {"id": "T-002", "title": "B", "depends_on": ["T-001"]},
        {"id": "T-003", "title": "C", "depends_on": ["T-002"]},
    ])
    assert len(groups) == 3, f"Case 4: 应 3 分组, got {len(groups)}"
    assert all(not g.can_parallel for g in groups), "Case 4: 全部串行"
    print("  [OK] Case 4: 串行依赖链 A→B→C → 3 个串行分组")

    # Case 5: 并行+串行混合
    groups = detect_parallelizable([
        {"id": "T-001", "title": "独立并行", "parallelizable": True},
        {"id": "T-002", "title": "依赖A", "depends_on": ["T-001"], "parallelizable": True},
        {"id": "T-003", "title": "串行B", "depends_on": ["T-002"]},
    ])
    assert len(groups) == 3, f"Case 5: 应 3 分组, got {len(groups)}"
    assert groups[0].can_parallel is True, "Case 5: 第一组应并行"
    assert groups[0].task_ids == ["T-001"], f"Case 5: 第一组应为 T-001, got {groups[0].task_ids}"
    assert groups[1].can_parallel is True, "Case 5: 第二组应并行"
    assert groups[1].task_ids == ["T-002"], f"Case 5: 第二组应为 T-002, got {groups[1].task_ids}"
    assert groups[2].can_parallel is False, "Case 5: 第三组应串行"
    print("  [OK] Case 5: 并行+串行混合 → 3 个分组")

    # Case 6: 循环依赖检测
    try:
        detect_parallelizable([
            {"id": "T-001", "title": "A", "depends_on": ["T-002"]},
            {"id": "T-002", "title": "B", "depends_on": ["T-001"]},
        ])
        assert False, "Case 6: 应抛出 CyclicDependencyError"
    except CyclicDependencyError:
        print("  [OK] Case 6: 循环依赖 A→B→A → CyclicDependencyError")

    # Case 7: summarize_results 逻辑验证（不依赖 REPO_ROOT 写入）
    executor = GoalParallelExecutor(max_concurrent=5)
    task_queue = [
        {"id": "T-001", "title": "任务1", "status": "pending", "parallelizable": True},
        {"id": "T-002", "title": "任务2", "status": "pending", "parallelizable": True},
    ]
    results = [
        SubagentResult(task_id="T-001", status="done", artifact="/path/to/t1.md", token_used=10000),
        SubagentResult(task_id="T-002", status="done", artifact="/path/to/t2.md", token_used=8000),
    ]
    updated, merged = executor.summarize_results(task_queue, results, goal_id="test-goal-001")
    assert updated[0]["status"] == "done", "Case 7: T-001 status 应为 done"
    assert updated[0]["artifact"] == "/path/to/t1.md", "Case 7: T-001 artifact 应更新"
    assert updated[0]["subagent_budget_used"] == 10000, "Case 7: T-001 budget 应更新"
    assert updated[1]["status"] == "done", "Case 7: T-002 status 应为 done"
    assert updated[1]["artifact"] == "/path/to/t2.md", "Case 7: T-002 artifact 应更新"
    assert merged is not None, "Case 7: 应生成 merged artifact"
    assert "manifest.json" in merged, "Case 7: merged path 应含 manifest.json"
    print("  [OK] Case 7: summarize_results 正确更新 task_queue + 生成 manifest")

    # Case 8: can_launch_more 正确判断
    executor2 = GoalParallelExecutor(max_concurrent=5)
    for i in range(5):
        assert executor2.can_launch_more() is True, f"Case 8: 第{i}次应可启动"
        executor2._subagent_count += 1
    assert executor2.can_launch_more() is False, "Case 8: 超出上限应不可启动"
    print("  [OK] Case 8: can_launch_more 正确判断上限")

    print("  [OK] self_test passed (8 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(_cli(sys.argv[1:]))
