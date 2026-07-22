#!/usr/bin/env python3
"""Goal Loop 五段式自治 runner（v1，对标 Codex /goal 状态机）

五段式：Plan → Act → Audit → Review → Iterate
三层熔断：max_rounds / token_budget / user_input_pending

设计约束：
  - 不实际调用 LLM；提供状态机 + 进度推进 + 熔断判定
  - 真实「Act 执行」由 Agent 调用工具完成；本 runner 只负责「轮次 + 状态推进 + 熔断判定」
  - 与 goal_snapshot.py 强耦合：所有状态变更都通过 update_snapshot 落盘
  - 审计/复盘文件模板写入 .goal-log-db/active/<goal_id>/audit_<round>.md + review_<round>.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Reuse snapshot module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from goal_snapshot import (  # noqa: E402
    DEFAULT_TOKEN_LIMIT,
    MAX_ROUNDS_DEFAULT,
    SnapshotError,
    SnapshotSchemaError,
    create_snapshot,
    delete_snapshot,
    goal_dir,
    load_snapshot,
    update_snapshot,
)

# ===== 阶段枚举 =====


class Stage(str, Enum):
    PLAN = "Plan"
    ACT = "Act"
    AUDIT = "Audit"
    REVIEW = "Review"
    ITERATE = "Iterate"
    CONVERGED = "Converged"  # 终态


# ===== 配置常量 =====

# 阈值可由环境变量覆盖
import os

MAX_ROUNDS: int = int(os.environ.get("GOAL_LOOP_MAX_ROUNDS", str(MAX_ROUNDS_DEFAULT)))
# 默认无上限（None），除非 GOAL_LOOP_TOKEN_LIMIT 显式声明
if (tok_str := os.environ.get("GOAL_LOOP_TOKEN_LIMIT")):
    TOKEN_LIMIT: int | None = int(tok_str)
else:
    TOKEN_LIMIT: int | None = None

# ===== 异常 =====


class LoopError(Exception):
    """循环通用错误。"""


class CircuitBreakerError(LoopError):
    """熔断触发（max rounds / token / user input）。"""


# ===== 数据结构 =====


@dataclass
class AuditVerdict:
    """一条审计结论。"""

    standard: str
    evidence: str
    judgement: str  # PASS / FAIL / UNKNOWN
    reverse_challenge: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "standard": self.standard,
            "evidence": self.evidence,
            "judgement": self.judgement,
            "reverse_challenge": self.reverse_challenge,
        }


@dataclass
class ReviewReport:
    """一份复盘报告（三段式）。"""

    defects: list[str] = field(default_factory=list)
    root_causes: list[str] = field(default_factory=list)
    fix_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "defects": list(self.defects),
            "root_causes": list(self.root_causes),
            "fix_actions": list(self.fix_actions),
        }


# ===== 状态机 =====


class GoalLoop:
    """五段式 runner，管理单 goal 快照的循环推进与熔断。"""

    def __init__(self, goal_id: str) -> None:
        self.goal_id: str = goal_id
        self.snapshot: dict[str, Any] = load_snapshot(goal_id)

    # ---- 五段式入口 ----

    def plan(self, task_queue: list[dict[str, Any]]) -> dict[str, Any]:
        """首轮或目标变更时执行：写入 task_queue。"""
        if self.snapshot["status"] != "active":
            raise LoopError(f"plan() 仅 active 状态可执行，当前={self.snapshot['status']}")
        return update_snapshot(
            self.goal_id,
            task_queue=task_queue,
            loop_round=self.snapshot["loop_round"],  # Plan 不递增轮次
        )

    def act(self, artifact_path: Optional[str] = None) -> dict[str, Any]:
        """执行产出（Agent 在外部完成实际工作，本方法只推进状态 + 落 artifact）。

        Returns:
            更新后的 snapshot。
        """
        self._check_user_input_pending()
        self.snapshot = load_snapshot(self.goal_id)
        updates: dict[str, Any] = {}
        if artifact_path is not None:
            updates["latest_artifact"] = artifact_path
        # 标记任务队列首个未完项为 in_progress（如果有）
        for t in self.snapshot.get("task_queue", []):
            if t.get("status") == "pending":
                t["status"] = "in_progress"
                break
        updates["task_queue"] = self.snapshot.get("task_queue", [])
        if updates:
            self.snapshot = update_snapshot(self.goal_id, **updates)
        return self.snapshot

    def audit(
        self,
        verdicts: list[AuditVerdict],
        token_used_delta: int = 0,
    ) -> tuple[dict[str, Any], list[AuditVerdict]]:
        """逐条证据化自检。

        Args:
            verdicts: 每条验收标准的判定
            token_used_delta: 本轮消耗的 token（累加到 budget.used）

        Returns:
            (更新后的 snapshot, 原始 verdicts)

        Raises:
            SnapshotSchemaError: verdicts 非法
        """
        self.snapshot = load_snapshot(self.goal_id)
        self._check_user_input_pending()

        # Token 累计
        tb = self.snapshot["token_budget"]
        tb["used"] += int(token_used_delta)
        tb["updated_at"] = datetime.now(timezone.utc).isoformat()

        # 写 audit_<round>.md
        round_n = self.snapshot["loop_round"] + 1  # 本轮将进入的轮次
        audit_record = {
            "round": round_n,
            "verdicts": [v.to_dict() for v in verdicts],
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        self._write_template(f"audit_{round_n}.md", _render_audit(audit_record))

        # 落盘
        self.snapshot = update_snapshot(
            self.goal_id,
            token_budget=tb,
            last_audit=audit_record,
            loop_round=round_n,
        )
        return self.snapshot, verdicts

    def review(self, report: ReviewReport) -> dict[str, Any]:
        """深度复盘（三段式）。"""
        self.snapshot = load_snapshot(self.goal_id)
        self._check_user_input_pending()
        review_record = {
            **report.to_dict(),
            "round": self.snapshot["loop_round"],
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        self._write_template(
            f"review_{self.snapshot['loop_round']}.md",
            _render_review(review_record),
        )
        self.snapshot = update_snapshot(self.goal_id, last_review=review_record)
        return self.snapshot

    def iterate(self) -> dict[str, Any]:
        """收敛判定。

        v18 修复: PARTIAL 与 UNKNOWN 等价（均不能算通过）。
        v18 修复: status 已为 achieved 时不再重复判定（防止越界 iterate）。
        v18 增强: 触发 PARTIAL 时记录 last_partial_round 便于人工追溯。

        Returns:
            更新后的 snapshot

        Raises:
            CircuitBreakerError: 触发熔断（max rounds / token / user input）
        """
        self.snapshot = load_snapshot(self.goal_id)

        # v18 防越界: 已 achieved/budget-limited 不再重复 iterate
        if self.snapshot["status"] in ("achieved", "budget-limited"):
            raise LoopError(
                f"iterate() 越界：当前 status={self.snapshot['status']}，不允许继续"
            )

        audit = self.snapshot.get("last_audit") or {}
        verdicts: list[dict[str, Any]] = audit.get("verdicts", [])
        has_fail = any(v.get("judgement") == "FAIL" for v in verdicts)
        has_unknown = any(v.get("judgement") == "UNKNOWN" for v in verdicts)
        # v18 修复: PARTIAL 与 UNKNOWN 等价处理
        has_partial = any(v.get("judgement") == "PARTIAL" for v in verdicts)

        # 用户输入阻断
        self._check_user_input_pending()

        # Token 熔断（仅在 limit 不为 None 时检查）
        tb = self.snapshot["token_budget"]
        if tb["limit"] is not None and tb["used"] >= tb["limit"]:
            self.snapshot = update_snapshot(self.goal_id, status="budget-limited")
            raise CircuitBreakerError(
                f"token 熔断: used={tb['used']} >= limit={tb['limit']}"
            )

        # 轮次熔断
        if self.snapshot["loop_round"] >= MAX_ROUNDS:
            self.snapshot = update_snapshot(self.goal_id, status="budget-limited")
            raise CircuitBreakerError(
                f"轮次熔断: loop_round={self.snapshot['loop_round']} >= {MAX_ROUNDS}"
            )

        # 全部 PASS → achieved（v20 修复：显式回写 last_audit / last_review）
        # v20 修复：achieved 时必须将审计数据写回 snapshot，
        # 否则 CONVERGED 快照的 last_audit/last_review 为 null，破坏可追溯性。
        # last_review 可能仍为 null（若本轮尚未调用 review()），仅在有值时回写。
        if verdicts and not has_fail and not has_unknown and not has_partial:
            kwargs: dict[str, Any] = {"status": "achieved"}
            audit_data = self.snapshot.get("last_audit")
            if audit_data is not None:
                kwargs["last_audit"] = audit_data
            review_data = self.snapshot.get("last_review")
            if review_data is not None:
                kwargs["last_review"] = review_data
            self.snapshot = update_snapshot(self.goal_id, **kwargs)
            return self.snapshot

        # 存在 FAIL/PARTIAL/UNKNOWN → 继续（不增 round，audit 已 +1）
        # v18 增强: 在 last_review 写入 PARTIAL 标记（不引入新字段，避免 SNAPSHOT_FIELDS 扩展）
        last_review = self.snapshot.get("last_review") or {}
        if has_partial:
            last_review["had_partial"] = True
            last_review["partial_round"] = self.snapshot["loop_round"]
            self.snapshot = update_snapshot(
                self.goal_id,
                status="active",
                last_review=last_review,
            )
        else:
            self.snapshot = update_snapshot(self.goal_id, status="active")
        return self.snapshot

    # ---- 管控指令 ----

    def pause(self) -> dict[str, Any]:
        return update_snapshot(self.goal_id, status="paused")

    def resume(self) -> dict[str, Any]:
        return update_snapshot(self.goal_id, status="active")

    def clear(self) -> bool:
        return delete_snapshot(self.goal_id)

    # ---- 内部 ----

    def _check_user_input_pending(self) -> None:
        """检测用户未读消息（占位实现）。"""
        marker = goal_dir(self.goal_id) / ".user_input_pending"
        if marker.exists():
            update_snapshot(self.goal_id, status="paused")
            raise CircuitBreakerError("用户输入阻断：检测到 .user_input_pending 标志")

    def _write_template(self, name: str, body: str) -> None:
        gd = goal_dir(self.goal_id)
        gd.mkdir(parents=True, exist_ok=True)
        (gd / name).write_text(body, encoding="utf-8")


# ===== 模板渲染 =====


def _render_audit(record: dict[str, Any]) -> str:
    lines = [
        f"# Audit Round {record['round']}",
        "",
        f"_时间_: {record['ts']}",
        "",
        "## 审计结论",
        "",
    ]
    for v in record.get("verdicts", []):
        lines.append(f"### 标准：{v['standard']}")
        lines.append(f"- **证据**：{v['evidence']}")
        lines.append(f"- **判定**：{v['judgement']}")
        if v.get("reverse_challenge"):
            lines.append(f"- **反向挑战**：{v['reverse_challenge']}")
        lines.append("")
    return "\n".join(lines)


def _render_review(record: dict[str, Any]) -> str:
    lines = [
        f"# Review Round {record['round']}",
        "",
        f"_时间_: {record['ts']}",
        "",
        "## 缺陷汇总",
        "",
    ]
    for d in record.get("defects", []):
        lines.append(f"- {d}")
    lines.extend(["", "## 根因定位", ""])
    for r in record.get("root_causes", []):
        lines.append(f"- {r}")
    lines.extend(["", "## 修复方案", ""])
    for f in record.get("fix_actions", []):
        lines.append(f"- {f}")
    return "\n".join(lines)


# ===== CLI =====


def _cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Goal Loop 五段 runner")
    sub = parser.add_subparsers(dest="cmd")

    p_new = sub.add_parser("new", help="创建 goal 快照")
    p_new.add_argument("--goal", required=True)
    p_new.add_argument("--criteria", required=True)

    p_pause = sub.add_parser("pause", help="暂停循环")
    p_pause.add_argument("--goal-id", required=True)

    p_resume = sub.add_parser("resume", help="恢复循环")
    p_resume.add_argument("--goal-id", required=True)

    p_clear = sub.add_parser("clear", help="清空快照")
    p_clear.add_argument("--goal-id", required=True)

    p_status = sub.add_parser("status", help="查看快照状态")
    p_status.add_argument("--goal-id", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "new":
        snap = create_snapshot(args.goal, [c.strip() for c in args.criteria.split(",")])
        print(snap["goal_id"])
        return 0
    if args.cmd == "pause":
        snap = GoalLoop(args.goal_id).pause()
        print(f"paused: {snap['status']}")
        return 0
    if args.cmd == "resume":
        snap = GoalLoop(args.goal_id).resume()
        print(f"resumed: {snap['status']}")
        return 0
    if args.cmd == "clear":
        ok = GoalLoop(args.goal_id).clear()
        print("cleared" if ok else "not found")
        return 0
    if args.cmd == "status":
        snap = load_snapshot(args.goal_id)
        print(json.dumps(
            {
                "goal_id": snap["goal_id"],
                "status": snap["status"],
                "loop_round": snap["loop_round"],
                "token_used": snap["token_budget"]["used"],
                "token_limit": snap["token_budget"]["limit"],
            },
            ensure_ascii=False,
        ))
        return 0
    parser.print_help()
    return 1


# ===== Self-test =====


def self_test() -> int:
    """python3 ai_workflow/goal_loop_runner.py --self-test

    验证 7 项：
      1. Plan：创建快照 + 写入 task_queue
      2. Act：写 latest_artifact + 首个任务置 in_progress
      3. Audit PASS：写入 audit_<round>.md + loop_round += 1
      4. Iterate PASS：status 变 achieved
      5. 重新创建走第二遍 + Audit FAIL → 继续 + 轮次熔断
      6. Token 熔断：构造超限 token_budget，触发 CircuitBreakerError
      7. 用户输入熔断：写入 .user_input_pending 标志 → 触发
    """
    import tempfile
    import goal_snapshot as gs

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        original_goals = gs.GOALS_DIR
        gs.GOALS_DIR = tmp_path / "goals"

        # Case 1
        snap = create_snapshot("测试目标", ["标准A", "标准B"])
        gid = snap["goal_id"]
        loop = GoalLoop(gid)
        snap2 = loop.plan([
            {"id": "t1", "title": "任务1", "status": "pending"},
            {"id": "t2", "title": "任务2", "status": "pending"},
        ])
        assert len(snap2["task_queue"]) == 2
        assert snap2["loop_round"] == 0
        print(f"  [OK] Case 1: plan() 写入 task_queue")

        # Case 2
        snap3 = loop.act(artifact_path="/tmp/artifact.md")
        assert snap3["latest_artifact"] == "/tmp/artifact.md"
        assert snap3["task_queue"][0]["status"] == "in_progress"
        print(f"  [OK] Case 2: act() 写入 artifact + in_progress")

        # Case 3
        verdicts_pass = [
            AuditVerdict("标准A", "证据A", "PASS", "反向挑战：能否有更弱断言？不能"),
            AuditVerdict("标准B", "证据B", "PASS", "反向挑战：缺样本能漏过？样本已覆盖"),
        ]
        snap4, _ = loop.audit(verdicts_pass, token_used_delta=100)
        assert snap4["loop_round"] == 1
        assert (gs.goal_dir(gid) / "audit_1.md").exists()
        print(f"  [OK] Case 3: audit() 落 audit_1.md + loop_round=1")

        # Case 4: iterate() → achieved
        snap5 = loop.iterate()
        assert snap5["status"] == "achieved", f"应 achieved, got {snap5['status']}"
        print(f"  [OK] Case 4: iterate() PASS → achieved")

        # Case 5: 新建 goal，FAIL 路径
        snap_b = create_snapshot("B", ["S1"])
        loop_b = GoalLoop(snap_b["goal_id"])
        loop_b.plan([{"id": "t1", "title": "T", "status": "pending"}])
        loop_b.act(artifact_path="/tmp/x")
        loop_b.audit(
            [AuditVerdict("S1", "证据", "FAIL", "反向")],
            token_used_delta=10,
        )
        # 此时 loop_round=1，再 iterate 应继续（active）
        snap_b2 = loop_b.iterate()
        assert snap_b2["status"] == "active", f"FAIL 应继续, got {snap_b2['status']}"
        # 再 audit 到 round=5 → 触发熔断
        for r in range(2, 6):
            loop_b.act(artifact_path=f"/tmp/{r}")
            loop_b.audit([AuditVerdict("S1", "证据", "FAIL", "反向")], token_used_delta=10)
            try:
                loop_b.iterate()
            except CircuitBreakerError as e:
                # 第 5 轮后应熔断
                if r == 5:
                    print(f"  [OK] Case 5: 第 {r} 轮熔断 ({e})")
                    break
                raise
        else:
            assert False, "应触发轮次熔断"

        # Case 6: Token 熔断
        snap_c = create_snapshot("C", ["S"], token_limit=50)
        loop_c = GoalLoop(snap_c["goal_id"])
        loop_c.plan([{"id": "t", "title": "T", "status": "pending"}])
        loop_c.act(artifact_path="/tmp/c")
        loop_c.audit([AuditVerdict("S", "ev", "FAIL", "rev")], token_used_delta=200)
        try:
            loop_c.iterate()
            assert False, "应抛 CircuitBreakerError"
        except CircuitBreakerError as e:
            assert "token" in str(e).lower()
            print(f"  [OK] Case 6: token 熔断 ({e})")

        # Case 7: 用户输入熔断
        snap_d = create_snapshot("D", ["S"])
        loop_d = GoalLoop(snap_d["goal_id"])
        loop_d.plan([{"id": "t", "title": "T", "status": "pending"}])
        # 写 .user_input_pending 标志
        marker = gs.goal_dir(snap_d["goal_id"]) / ".user_input_pending"
        marker.write_text("1")
        try:
            loop_d.act()
            assert False, "应抛 CircuitBreakerError"
        except CircuitBreakerError as e:
            assert "用户" in str(e)
            print(f"  [OK] Case 7: 用户输入熔断 ({e})")

        # Case 8 (v18 增补): PARTIAL 触发继续而非 achieved
        snap_e = create_snapshot("E", ["S"])
        loop_e = GoalLoop(snap_e["goal_id"])
        loop_e.plan([{"id": "t", "title": "T", "status": "pending"}])
        loop_e.act(artifact_path="/tmp/e")
        loop_e.audit([AuditVerdict("S", "证据", "PARTIAL", "反向")], token_used_delta=10)
        snap_e2 = loop_e.iterate()
        assert snap_e2["status"] == "active", (
            f"PARTIAL 应继续 active, got {snap_e2['status']}"
        )
        # last_review 应标记 had_partial
        assert snap_e2["last_review"].get("had_partial") is True
        assert snap_e2["last_review"].get("partial_round") == 1
        print(f"  [OK] Case 8: PARTIAL → 继续 + last_review.had_partial=True")

        # Case 9 (v18 增补): achieved 后再次 iterate 应抛 LoopError（防越界）
        snap_f = create_snapshot("F", ["S"])
        loop_f = GoalLoop(snap_f["goal_id"])
        loop_f.plan([{"id": "t", "title": "T", "status": "pending"}])
        loop_f.act(artifact_path="/tmp/f")
        loop_f.audit([AuditVerdict("S", "证据", "PASS", "反向")], token_used_delta=10)
        loop_f.iterate()  # → achieved
        try:
            loop_f.iterate()
            assert False, "应抛 LoopError 防越界"
        except LoopError as e:
            assert "越界" in str(e), f"应为越界错误, got {e}"
            print(f"  [OK] Case 9: achieved 后 iterate 越界保护")

        # Case 10 (v20 增补): achieved 后 snapshot 的 last_audit 非 null
        # 验证 Fix-1 成果：iterate() achieved 时显式回写审计数据
        # 注意：last_review 在标准流程中本轮可能未调用 review()，不强制要求非 null
        reloaded = gs.load_snapshot(snap_f["goal_id"])
        assert reloaded["last_audit"] is not None, "achieved 后 last_audit 不应为 null"
        assert reloaded["last_audit"]["verdicts"][0]["judgement"] == "PASS"
        print(f"  [OK] Case 10: achieved 后 last_audit 已回写快照（last_review 按需回写）")

        gs.GOALS_DIR = original_goals

    print(f"  [OK] self_test passed (10 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(_cli(sys.argv[1:]))
