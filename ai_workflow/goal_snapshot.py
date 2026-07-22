#!/usr/bin/env python3
"""Goal Loop 快照持久化（v3.1，对标 v1.2 Schema 扩展）

Schema 字段（20）：
  - goal_id:           UUIDv4，唯一任务 ID
  - raw_user_goal:     用户原始目标文本
  - value_criteria:    外部价值类验收（list[str]，v1.1）
  - process_criteria:   内部过程类验收（list[str]，v1.1）
  - value_ratio:       value_criteria 占比（float，v1.1）
  - severity_label:    BLOCKER/MAJOR/MINOR（str，v1.1）
  - follow_up_items:   遗留项列表（list[dict]，v1.1）
  - goal_signature:    目标语义哈希（str，v1.1）
  - goal_signature_changelog: 签名变更历史（list[dict]，v1.2.1，DT-V28-002）
  - out_of_scope_md:   禁区清单路径（str，v1.1）
  - audit_stability:   增量审计追踪（dict，v1.1）
  - efficiency_stats:  效能统计（dict，v1.1）
  - task_queue:        子任务队列（list[dict]，v1.2 新增 parallelizable/depends_on 字段）
  - parallel_executor_hints: 并行化建议（dict，v1.2 新增）
  - loop_round:        当前迭代轮次（int，从 1 起）
  - last_audit:        上一轮审计论证记录（dict | None）
  - last_review:       上一轮复盘根因与修复方案（dict | None）
  - latest_artifact:   最新交付物路径（str | None）
  - status:            active | achieved | converged_with_followup | paused | budget-limited
  - token_budget:      {used: int, limit: int, updated_at: ISO8601}

持久化路径：<REPO>/.goal-log-db/active/<goal_id>/snapshot.json
防并发：    <REPO>/.goal-log-db/active/<goal_id>/.lock  (fcntl.flock)
Atomic:    写 <file>.tmp 后 os.replace()。

索引维护：
  - session-index.jsonl: 每次 create/update 时 append 一条记录
  - thread_goals.json:   全局状态库，每次 create/update 时同步更新

设计约束（v3）：
  - 仅此模块可写 snapshot.json
  - 普通对话无法篡改：snapshot 目录不进 git，仅 goal_loop_runner.py 可调用
  - 路径遵守 Git 分类铁律（.goal-log-db/ 默认不入 git）
  - v1.1 向后兼容：v1.0 accept_criteria 自动归入 value_criteria
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

# ===== 路径配置 =====

REPO_ROOT = Path(__file__).resolve().parent.parent
GOALS_DIR = REPO_ROOT / ".goal-log-db" / "active"
INDEX_DIR = REPO_ROOT / ".goal-log-db" / "index"
SNAPSHOT_FILENAME = "snapshot.json"
LOCK_FILENAME = ".lock"
SESSION_INDEX_FILE = INDEX_DIR / "session-index.jsonl"
THREAD_GOALS_FILE = INDEX_DIR / "thread_goals.json"

# ===== 字段 Schema 定义（v1.2.1 — 20 字段） =====

SNAPSHOT_FIELDS: tuple[str, ...] = (
    "goal_id",
    "raw_user_goal",
    "value_criteria",           # v1.1 新增
    "process_criteria",         # v1.1 新增
    "value_ratio",              # v1.1 新增
    "severity_label",           # v1.1 新增
    "follow_up_items",           # v1.1 新增
    "goal_signature",            # v1.1 新增（GL-009）
    "goal_signature_changelog",  # v1.2.1 新增（DT-V28-002，默认 []）
    "out_of_scope_md",          # v1.1 新增（GL-003，禁区清单路径）
    "audit_stability",          # v1.1 新增（GL-006，增量审计追踪）
    "efficiency_stats",        # v1.1 新增（GL-008，效能统计）
    "task_queue",
    "parallel_executor_hints",  # v1.2 新增（并行化建议，Act 阶段由 LLM 填充）
    "loop_round",
    "last_audit",
    "last_review",
    "latest_artifact",
    "status",
    "token_budget",
)

# v1.0 遗留字段（v1.1 向前兼容时自动映射）
LEGACY_FIELD: str = "accept_criteria"

# v1.1 新增 status 枚举（v2 修订：REPAIRING 加入）
# v2 修订：REPAIRING 加入（goal-loop 轮次迭代完成时的中间状态，表示有待修复的 audit verdicts）
VALID_STATUS: frozenset[str] = frozenset({
    "active",
    "achieved",
    "converged_with_followup",  # v1.1 新增
    "paused",
    "budget-limited",
    "REPAIRING",  # v2 新增（轮次迭代中间状态，对应 serverchan notify_states）
})

# v1.0 遗留 status 别名（向后兼容）
LEGACY_STATUS_MAP: dict[str, str] = {
    "converged": "achieved",  # v1.0 旧值 → v1.1 等价值
}

# v1.1 严重度枚举
VALID_SEVERITY: frozenset[str] = frozenset({"BLOCKER", "MAJOR", "MINOR"})
DEFAULT_SEVERITY: str = "MAJOR"

DEFAULT_TOKEN_LIMIT: int | None = None  # 默认无上限（None）；显式声明才限制
UNLIMITED_TOKEN: int | None = None    # 别名，同 DEFAULT_TOKEN_LIMIT
MAX_ROUNDS_DEFAULT: int = 5
MIN_VALUE_RATIO_SOFT: float = 0.5   # v30 D1 修订：启动软指导值（不达标仅 WARN，不阻断）
MIN_VALUE_RATIO_HARD: float = 0.6  # v30 D1 修订：收敛判定硬约束（仅在 create_snapshot 时强制）
MIN_SIGNATURE_SOFT: float = 0.5     # v30 D2 修订：签名漂移软指导值（0.5~0.7 仅记录 changelog）


# ===== 异常类型 =====


class SnapshotError(Exception):
    """快照通用错误。"""


class SnapshotSchemaError(SnapshotError):
    """字段缺失或类型错误。"""


class SnapshotLockError(SnapshotError):
    """并发锁失败。"""


class ValueRatioError(SnapshotError):
    """value_ratio 低于阈值（GL-001）"""


# ===== 路径工具 =====


def goal_dir(goal_id: str) -> Path:
    """解析 goal 目录路径。"""
    if not goal_id or "/" in goal_id or ".." in goal_id:
        raise SnapshotError(f"非法 goal_id: {goal_id!r}")
    return GOALS_DIR / goal_id


def snapshot_path(goal_id: str) -> Path:
    return goal_dir(goal_id) / SNAPSHOT_FILENAME


def lock_path(goal_id: str) -> Path:
    return goal_dir(goal_id) / LOCK_FILENAME


# ===== 并发锁 =====


@contextmanager
def _file_lock(goal_id: str) -> Iterator[None]:
    """flock 互斥，防止并发读写导致半写。"""
    lp = lock_path(goal_id)
    lp.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lp), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


# ===== 索引维护 =====


def _append_session_index(goal_id: str, action: str, status: str, round_n: int = 0) -> None:
    """追加一条记录到 session-index.jsonl（append-only）。"""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "goal_id": goal_id,
        "action": action,
        "timestamp": _now_iso(),
        "round": round_n,
        "status": status,
    }
    with open(SESSION_INDEX_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _update_thread_goals(goal_id: str, title: str, status: str, round_n: int = 0, create: bool = False) -> None:
    """同步更新 thread_goals.json 全局状态库。"""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if THREAD_GOALS_FILE.exists():
        try:
            data = json.loads(THREAD_GOALS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {"description": "全局 Goal 状态库", "create_time": _now_iso(), "update_time": _now_iso(), "task_list": []}
    else:
        data = {"description": "全局 Goal 状态库", "create_time": _now_iso(), "update_time": _now_iso(), "task_list": []}

    # 查找或创建任务
    found = False
    for task in data.get("task_list", []):
        if task.get("goal_id") == goal_id:
            task["status"] = status
            task["round"] = round_n
            task["updated_at"] = _now_iso()
            found = True
            break
    if not found and create:
        data["task_list"].append({
            "goal_id": goal_id,
            "title": title,
            "status": status,
            "round": round_n,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        })

    data["update_time"] = _now_iso()

    # Atomic write
    tmp = THREAD_GOALS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, THREAD_GOALS_FILE)


# ===== 向前兼容工具 =====


def _migrate_legacy_snapshot(data: dict[str, Any]) -> dict[str, Any]:
    """将 v1.0 accept_criteria 快照迁移到 v1.1 Schema。

    v1.0 → v1.1 字段映射：
      - accept_criteria → value_criteria（全部归入外部价值类）
      - process_criteria → []（默认空）
      - value_ratio → 1.0（v1.0 无拆分，全归为外部价值）
      - severity_label → DEFAULT_SEVERITY
      - follow_up_items → []
      - last_audit（字符串→null，v1.0 旧格式为 audit 文件路径）
      - ac_results / converged_reason → 忽略（v1.1 不存储中间状态）
    """
    if "value_criteria" in data:
        # 已是 v1.1 Schema；v1.2.1 新字段仍需按默认值补齐
        data["goal_signature_changelog"] = data.get("goal_signature_changelog", [])
        return data

    # v1.0 迁移
    legacy = data.get(LEGACY_FIELD, [])
    data["value_criteria"] = list(legacy) if legacy else []
    data["process_criteria"] = []
    data["value_ratio"] = 1.0  # v1.0 全归外部价值
    data["severity_label"] = data.get("severity_label", DEFAULT_SEVERITY)
    data["follow_up_items"] = data.get("follow_up_items", [])
    data["goal_signature"] = data.get("goal_signature", "")  # v1.0 无签名，v1.1 向前兼容填充空字符串
    data["goal_signature_changelog"] = data.get("goal_signature_changelog", [])  # v1.2.1 新增，旧快照默认空数组
    data["out_of_scope_md"] = data.get("out_of_scope_md", "")
    data["audit_stability"] = data.get("audit_stability", {})
    data["efficiency_stats"] = data.get("efficiency_stats", {})
    data["parallel_executor_hints"] = data.get("parallel_executor_hints", {})  # v1.2 新增，v1.0/v1.1 向前兼容
    data["task_queue"] = data.get("task_queue", [])  # v1.2 扩展字段，v1.0/v1.1 向前兼容
    # v1.0 last_audit 是 audit 文件路径字符串，v1.1 要求 dict | None
    if isinstance(data.get("last_audit"), str):
        data["last_audit"] = None
    # v1.0 last_review 同理
    if isinstance(data.get("last_review"), str):
        data["last_review"] = None
    # v1.0 status='converged' → v1.1 'achieved'
    legacy_status = data.get("status", "")
    if legacy_status in LEGACY_STATUS_MAP:
        data["status"] = LEGACY_STATUS_MAP[legacy_status]
    # 移除 v1.0 额外字段（v1.1 不存储）
    data.pop("ac_results", None)
    data.pop("converged_reason", None)

    # 移除 legacy 字段（已在 snapshot 中则保留，只是不再作为主字段）
    return data


def _compute_value_ratio(value: list, process: list) -> float:
    """计算 value_ratio（GL-001）。"""
    total = len(value) + len(process)
    if total == 0:
        return 0.0
    return round(len(value) / total, 4)


def generate_goal_signature(text: str) -> str:
    """生成目标语义哈希（GL-009）。

    使用 SHA-256 对目标文本生成哈希签名，用于后续轮次漂移检测。

    Args:
        text: raw_user_goal 原始文本

    Returns:
        十六进制哈希签名（前 16 字符 + "..." 截断显示）
    """
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def compute_similarity(text1: str, text2: str) -> float:
    """计算两段文本的语义相似度（GL-009）。

    使用 Jaccard 相似度（基于词汇集合）作为近似度量。
    适用于检测目标描述的词汇级漂移。

    Args:
        text1: 原始目标文本
        text2: 当前目标文本

    Returns:
        0.0~1.0 之间的相似度分数
    """
    def _tokens(s: str) -> set[str]:
        import re
        return set(re.sub(r"[^\w\s]", " ", s).lower().split())

    if not text1 or not text2:
        return 0.0
    t1, t2 = _tokens(text1), _tokens(text2)
    intersection = t1 & t2
    union = t1 | t2
    if not union:
        return 1.0  # 两个空字符串视为完全相同
    return round(len(intersection) / len(union), 4)


def update_efficiency_stats(
    goal_id: str,
    *,
    rounds_to_convergence: int | None = None,
    first_pass_rate: float | None = None,
    blocker_residual_rate: float | None = None,
    avg_round_duration_seconds: float | None = None,
) -> dict[str, Any]:
    """更新效能统计字段（GL-008）。

    Goal 收敛后调用，记录本次执行的关键效能指标。

    Args:
        goal_id: 目标 ID
        rounds_to_convergence: 收敛轮次
        first_pass_rate: 首轮通过率（0.0~1.0）
        blocker_residual_rate: BLOCKER 遗留率（0.0~1.0）
        avg_round_duration_seconds: 平均单轮耗时（秒）

    Returns:
        更新后的完整 snapshot dict。
    """
    snap = load_snapshot(goal_id)
    stats = dict(snap.get("efficiency_stats", {}))
    now = _now_iso()
    stats.update({
        "rounds_to_convergence": rounds_to_convergence if rounds_to_convergence is not None else stats.get("rounds_to_convergence"),
        "first_pass_rate": first_pass_rate if first_pass_rate is not None else stats.get("first_pass_rate"),
        "blocker_residual_rate": blocker_residual_rate if blocker_residual_rate is not None else stats.get("blocker_residual_rate"),
        "avg_round_duration_seconds": avg_round_duration_seconds if avg_round_duration_seconds is not None else stats.get("avg_round_duration_seconds"),
        "last_updated": now,
    })
    return update_snapshot(goal_id, efficiency_stats=stats)


# ===== 字段校验 =====


def _validate_snapshot(data: dict[str, Any]) -> None:
    """校验快照必填字段、类型与 status 枚举（v1.1）。"""
    # 先做向前兼容迁移
    data = _migrate_legacy_snapshot(data)

    missing = [f for f in SNAPSHOT_FIELDS if f not in data]
    if missing:
        raise SnapshotSchemaError(f"快照缺字段: {missing}")

    if not isinstance(data["goal_id"], str) or not data["goal_id"]:
        raise SnapshotSchemaError("goal_id 必须为非空字符串")
    if not isinstance(data["raw_user_goal"], str):
        raise SnapshotSchemaError("raw_user_goal 必须为字符串")
    # value_criteria / process_criteria
    if not isinstance(data["value_criteria"], list):
        raise SnapshotSchemaError("value_criteria 必须为列表")
    if not all(isinstance(x, str) for x in data["value_criteria"]):
        raise SnapshotSchemaError("value_criteria 每项必须为字符串")
    if not isinstance(data["process_criteria"], list):
        raise SnapshotSchemaError("process_criteria 必须为列表")
    if not all(isinstance(x, str) for x in data["process_criteria"]):
        raise SnapshotSchemaError("process_criteria 每项必须为字符串")
    # value_ratio
    if not isinstance(data["value_ratio"], (int, float)) or not (0.0 <= data["value_ratio"] <= 1.0):
        raise SnapshotSchemaError("value_ratio 必须为 0~1 之间的数字")
    # severity_label
    if data["severity_label"] not in VALID_SEVERITY:
        raise SnapshotSchemaError(f"severity_label 非法: {data['severity_label']!r}（应为 {sorted(VALID_SEVERITY)}）")
    # follow_up_items（v1.1 标准格式 + task-like 兼容格式）
    if not isinstance(data["follow_up_items"], list):
        raise SnapshotSchemaError("follow_up_items 必须为列表")
    for i, item in enumerate(data["follow_up_items"]):
        if not isinstance(item, dict):
            raise SnapshotSchemaError("follow_up_items 每项必须为 dict")
        # 两种格式均可：
        # 1. 标准格式（add_follow_up_item 产生）：description + severity
        # 2. task-like 格式（task_queue 迁移产生）：id + title
        has_standard = "description" in item or "id" in item
        if not has_standard:
            raise SnapshotSchemaError(
                f"follow_up_items[{i}] 缺 identity 字段：需有 description 或 id，当前 keys={list(item.keys())}"
            )
    # goal_signature（v1.1 GL-009，允许空字符串）
    if not isinstance(data.get("goal_signature", ""), str):
        raise SnapshotSchemaError("goal_signature 必须为字符串")
    # goal_signature_changelog（v1.2.1 DT-V28-002，允许空数组）
    changelog = data.get("goal_signature_changelog", [])
    if not isinstance(changelog, list):
        raise SnapshotSchemaError("goal_signature_changelog 必须为列表")
    if not all(isinstance(item, dict) for item in changelog):
        raise SnapshotSchemaError("goal_signature_changelog 每项必须为 dict")
    # out_of_scope_md（v1.1 GL-003，允许空字符串）
    if not isinstance(data.get("out_of_scope_md", ""), str):
        raise SnapshotSchemaError("out_of_scope_md 必须为字符串")
    # audit_stability（v1.1 GL-006）
    stability = data.get("audit_stability", {})
    if not isinstance(stability, dict):
        raise SnapshotSchemaError("audit_stability 必须为 dict")
    for k, v in stability.items():
        if not isinstance(k, str):
            raise SnapshotSchemaError(f"audit_stability 键必须为字符串")
        if not isinstance(v, dict):
            raise SnapshotSchemaError(f"audit_stability[{k!r}] 必须为 dict")
    # efficiency_stats（v1.1 GL-008）
    eff_stats = data.get("efficiency_stats", {})
    if not isinstance(eff_stats, dict):
        raise SnapshotSchemaError("efficiency_stats 必须为 dict")
    # task_queue
    if not isinstance(data["task_queue"], list):
        raise SnapshotSchemaError("task_queue 必须为列表")
    # parallel_executor_hints（v1.2 新增，向前兼容允许 None）
    hints = data.get("parallel_executor_hints")
    if hints is not None and not isinstance(hints, dict):
        raise SnapshotSchemaError("parallel_executor_hints 必须为 dict 或 None")
    if not isinstance(data["loop_round"], int) or data["loop_round"] < 0:
        raise SnapshotSchemaError("loop_round 必须为非负整数")
    if data["last_audit"] is not None and not isinstance(data["last_audit"], dict):
        raise SnapshotSchemaError("last_audit 必须为 dict 或 None")
    if data["last_review"] is not None and not isinstance(data["last_review"], dict):
        raise SnapshotSchemaError("last_review 必须为 dict 或 None")
    if data["latest_artifact"] is not None and not isinstance(data["latest_artifact"], str):
        raise SnapshotSchemaError("latest_artifact 必须为 str 或 None")
    if data["status"] not in VALID_STATUS:
        raise SnapshotSchemaError(f"status 非法: {data['status']!r}（应为 {sorted(VALID_STATUS)}）")

    tb = data["token_budget"]
    if not isinstance(tb, dict):
        raise SnapshotSchemaError("token_budget 必须为 dict")
    for k in ("used", "limit", "updated_at"):
        if k not in tb:
            raise SnapshotSchemaError(f"token_budget 缺字段: {k}")
    if not isinstance(tb["used"], int) or tb["used"] < 0:
        raise SnapshotSchemaError("token_budget.used 必须为非负整数")
    if tb["limit"] is not None and (not isinstance(tb["limit"], int) or tb["limit"] <= 0):
        raise SnapshotSchemaError("token_budget.limit 必须为正整数或 None（无上限）")
    if not isinstance(tb["updated_at"], str):
        raise SnapshotSchemaError("token_budget.updated_at 必须为 ISO 字符串")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ===== 公共 API =====


def create_snapshot(
    raw_user_goal: str,
    value_criteria: list[str],
    *,
    process_criteria: list[str] | None = None,
    token_limit: int | None = DEFAULT_TOKEN_LIMIT,
    severity_label: str = DEFAULT_SEVERITY,
) -> dict[str, Any]:
    """创建新快照并落盘（atomic write，v1.1 Schema）。

    Args:
        raw_user_goal: 用户原始目标文本
        value_criteria: 外部价值类验收清单（GL-001）
        process_criteria: 内部过程类验收清单（可选，GL-001）
        token_limit: Token 预算上限（默认 None = 无上限；显式声明才限制）
        severity_label: 目标严重度（默认 MAJOR，GL-002）

    Returns:
        完整 snapshot dict。
    """
    if not raw_user_goal or not isinstance(raw_user_goal, str):
        raise SnapshotError("raw_user_goal 必须为非空字符串")
    if not value_criteria:
        raise SnapshotError("value_criteria 必须非空")

    # severity_label 显式校验（非法值直接拒绝，不静默替换）
    if severity_label not in VALID_SEVERITY:
        raise SnapshotSchemaError(
            f"severity_label 非法: {severity_label!r}（应为 {sorted(VALID_SEVERITY)}）"
        )

    proc = list(process_criteria) if process_criteria else []
    ratio = _compute_value_ratio(value_criteria, proc)

    # GL-001 强制校验：value_ratio >= MIN_VALUE_RATIO_HARD（收敛判定硬约束）
    if ratio < MIN_VALUE_RATIO_HARD:
        raise ValueRatioError(
            f"value_ratio={ratio:.2f} < {MIN_VALUE_RATIO_HARD}（GL-001 收敛硬约束）。"
            f"请确保外部价值类验收（value_criteria）占比 ≥ {int(MIN_VALUE_RATIO_HARD*100)}%。"
            f"（注：启动软指导值为 {MIN_VALUE_RATIO_SOFT}，低于 {MIN_VALUE_RATIO_SOFT} 时仅 WARN，不阻断）"
        )

    snapshot: dict[str, Any] = {
        "goal_id": str(uuid.uuid4()),
        "raw_user_goal": raw_user_goal,
        "value_criteria": list(value_criteria),
        "process_criteria": proc,
        "value_ratio": ratio,
        "severity_label": severity_label,
        "follow_up_items": [],
        "goal_signature": "",  # v1.1 GL-009，签名由 Plan 阶段生成
        "goal_signature_changelog": [],  # v1.2.1 DT-V28-002，签名变更历史
        "out_of_scope_md": "",  # v1.1 GL-003，禁区清单路径由 Plan 阶段写入
        "audit_stability": {},  # v1.1 GL-006，增量审计追踪
        "efficiency_stats": {},  # v1.1 GL-008，效能统计
        "task_queue": [],
        "parallel_executor_hints": {},  # v1.2 并行化建议，Act 阶段由 LLM 填充
        "loop_round": 0,
        "last_audit": None,
        "last_review": None,
        "latest_artifact": None,
        "status": "active",
        "token_budget": {
            "used": 0,
            "limit": int(token_limit) if token_limit is not None else None,
            "updated_at": _now_iso(),
        },
    }
    _validate_snapshot(snapshot)
    _write_snapshot(snapshot)

    # 索引维护
    _append_session_index(snapshot["goal_id"], "create", "active", 0)
    _update_thread_goals(snapshot["goal_id"], raw_user_goal[:50], "active", 0, create=True)

    return snapshot


def load_snapshot(goal_id: str) -> dict[str, Any]:
    """读取快照（自动迁移 v1.0 → v1.1，不带锁因为读不修改）。"""
    sp = snapshot_path(goal_id)
    if not sp.exists():
        raise SnapshotError(f"快照不存在: goal_id={goal_id!r}")
    try:
        data = json.loads(sp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SnapshotError(f"快照 JSON 解析失败: {e}") from e
    # 向前兼容迁移
    data = _migrate_legacy_snapshot(data)
    _validate_snapshot(data)
    return data


def update_snapshot(goal_id: str, **fields: Any) -> dict[str, Any]:
    """更新快照字段（带并发锁 + atomic write）。

    Args:
        goal_id: 目标 ID
        **fields: 待更新字段，必须是 SNAPSHOT_FIELDS 中的合法字段

    Returns:
        更新后的完整 snapshot dict。
    """
    invalid = [k for k in fields if k not in SNAPSHOT_FIELDS]
    if invalid:
        raise SnapshotSchemaError(f"非法字段: {invalid}（允许: {list(SNAPSHOT_FIELDS)}）")

    # 特殊处理：update_snapshot 不做 value_ratio 自动重算（由调用方保证一致性）

    with _file_lock(goal_id):
        snapshot = load_snapshot(goal_id)
        snapshot.update(fields)
        # 若更新了 token_budget 但没传 updated_at，自动补
        if "token_budget" in fields and "updated_at" not in fields["token_budget"]:
            snapshot["token_budget"]["updated_at"] = _now_iso()
        _validate_snapshot(snapshot)
        _write_snapshot(snapshot)

    # 索引维护
    status = fields.get("status", snapshot.get("status", "active"))
    round_n = fields.get("loop_round", snapshot.get("loop_round", 0))
    _append_session_index(goal_id, "update", status, round_n)
    _update_thread_goals(goal_id, snapshot.get("raw_user_goal", "")[:50], status, round_n)

    return snapshot


def add_follow_up_item(
    goal_id: str,
    description: str,
    severity: str,
    suggested_fix: str = "",
    source_round: int = 0,
    source_criterion: str = "",
) -> dict[str, Any]:
    """追加一条遗留项到 follow_up_items（GL-002）。"""
    if severity not in VALID_SEVERITY:
        raise SnapshotSchemaError(f"severity 非法: {severity!r}")

    snap = load_snapshot(goal_id)
    follow_up = list(snap.get("follow_up_items", []))
    follow_up.append({
        "description": description,
        "severity": severity,
        "suggested_fix": suggested_fix,
        "source_round": source_round,
        "source_criterion": source_criterion,
    })
    return update_snapshot(goal_id, follow_up_items=follow_up)


def list_active_goals() -> list[dict[str, Any]]:
    """扫描所有 active 状态的 goal 快照（用于 sessionStart 恢复）。"""
    if not GOALS_DIR.exists():
        return []
    active: list[dict[str, Any]] = []
    for goal_d in GOALS_DIR.iterdir():
        if not goal_d.is_dir():
            continue
        sp = goal_d / SNAPSHOT_FILENAME
        if not sp.exists():
            continue
        try:
            data = load_snapshot(goal_d.name)
        except SnapshotError:
            continue
        if data["status"] == "active":
            active.append(data)
    return active


def list_live_goals() -> list[dict[str, Any]]:
    """扫描所有"还活着"的 goal 快照（不过滤 status）。

    与 list_active_goals() 的区别：
      - list_active_goals()：只返回 status=="active" 的 goal
      - list_live_goals()：返回所有 snapshot.json 可读、status 未终止的 goal
                         （含 achieved/blocked/converged_with_followup/paused/budget-limited/active）

    用途：
      - afterAgentResponse bridge 通知（achieved 等终态也要通知）
      - 任何"会话级观察全部还活着的 goal"的场景

    终止态（未来扩展用）：若未来加 status="archived"/"cleaned"，应在这里排除。
    """
    if not GOALS_DIR.exists():
        return []
    live: list[dict[str, Any]] = []
    for goal_d in GOALS_DIR.iterdir():
        if not goal_d.is_dir():
            continue
        sp = goal_d / SNAPSHOT_FILENAME
        if not sp.exists():
            continue
        try:
            data = load_snapshot(goal_d.name)
        except SnapshotError:
            continue
        # 不过滤 status；快照存在 + 可读 + goal_id 非空即视为"活着"
        if data.get("goal_id"):
            live.append(data)
    return live


def load_all_active_snapshots(filter_active_only: bool = True) -> list[dict[str, Any]]:
    """读取所有 active 状态的 goal 快照（v1.2 跨 Round 并行支持）。

    Args:
        filter_active_only: True（默认）只返回 status=="active"；False 返回所有 snapshot

    与 list_active_goals() 的区别：
      - list_active_goals()：返回轻量摘要（goal_id + status + raw_user_goal）
      - load_all_active_snapshots()：返回完整 snapshot dict（含 task_queue + parallel_executor_hints 等）

    Returns:
        完整 snapshot dict 列表（按 loop_round 降序排列）。
    """
    if not GOALS_DIR.exists():
        return []
    active: list[dict[str, Any]] = []
    for goal_d in GOALS_DIR.iterdir():
        if not goal_d.is_dir():
            continue
        sp = goal_d / SNAPSHOT_FILENAME
        if not sp.exists():
            continue
        try:
            data = load_snapshot(goal_d.name)
        except SnapshotError:
            continue
        if filter_active_only:
            if data["status"] == "active":
                active.append(data)
        else:
            active.append(data)
    # 按 loop_round 降序（轮次高的优先续跑）
    active.sort(key=lambda s: s.get("loop_round", 0), reverse=True)
    return active


def delete_snapshot(goal_id: str) -> bool:
    """删除快照（仅 /clear-goal 调用）。"""
    gd = goal_dir(goal_id)
    if not gd.exists():
        return False
    import shutil
    shutil.rmtree(gd)
    return True


# ===== Internal write =====


def _write_snapshot(snapshot: dict[str, Any]) -> None:
    """Atomic write：写 .tmp 后 os.replace()，并验证写入结果。

    Read-back 验证：写入后读取并比对 goal_id，防止半写导致后续循环读取损坏数据。
    """
    sp = snapshot_path(snapshot["goal_id"])
    sp.parent.mkdir(parents=True, exist_ok=True)
    tmp = sp.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(tmp, sp)
    # Read-back 验证：确保写入的数据可被读取且 goal_id 一致
    try:
        with open(sp, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["goal_id"] == snapshot["goal_id"], (
            f"Snapshot read-back validation failed: "
            f"expected goal_id={snapshot['goal_id']!r}, got {data.get('goal_id')!r}"
        )
    except (json.JSONDecodeError, OSError, AssertionError) as e:
        raise SnapshotError(
            f"写入后 Read-back 验证失败: {e}"
        ) from e


# ===== CLI =====


def _cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Goal Loop 快照管理 (v1.1)")
    sub = parser.add_subparsers(dest="cmd")

    p_new = sub.add_parser("new", help="创建新快照")
    p_new.add_argument("--goal", required=True, help="原始目标文本")
    p_new.add_argument("--value-criteria", required=True, help="逗号分隔的外部价值类验收")
    p_new.add_argument("--process-criteria", default="", help="逗号分隔的内部过程类验收（可选）")
    p_new.add_argument("--token-limit", type=int, default=None, nargs="?", const=100000)
    p_new.add_argument("--severity", default=DEFAULT_SEVERITY, choices=list(VALID_SEVERITY))

    p_load = sub.add_parser("load", help="加载快照")
    p_load.add_argument("--goal-id", required=True)

    p_list = sub.add_parser("list-active", help="列出所有 active 快照")

    p_del = sub.add_parser("delete", help="删除快照")
    p_del.add_argument("--goal-id", required=True)

    args = parser.parse_args(argv)
    if args.cmd == "new":
        snap = create_snapshot(
            args.goal,
            [c.strip() for c in args.value_criteria.split(",") if c.strip()],
            process_criteria=[c.strip() for c in args.process_criteria.split(",") if c.strip()] or None,
            token_limit=args.token_limit,
            severity_label=args.severity,
        )
        print(json.dumps(snap, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "load":
        print(json.dumps(load_snapshot(args.goal_id), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "list-active":
        for s in list_active_goals():
            print(f"{s['goal_id']}\t{s['status']}\t{s['raw_user_goal'][:60]}")
        return 0
    if args.cmd == "delete":
        ok = delete_snapshot(args.goal_id)
        print("deleted" if ok else "not found")
        return 0
    parser.print_help()
    return 1


# ===== Self-test =====


def self_test() -> int:
    """python3 ai_workflow/goal_snapshot.py --self-test

    验证 13 项（v3 新增 v1.1 字段验证）：
      1. create_snapshot 落盘并返回 15 字段（v1.1）
      2. load_snapshot 读到完整字段
      3. update_snapshot 修改 loop_round/status 后落盘
      4. Schema 校验：缺字段 / status 非法 / token_budget 非法 都拒绝
      5. Atomic write：确认 .tmp 不残留
      6. list_active_goals 找到刚创建的快照
      7. session-index.jsonl 追加记录验证
      8. thread_goals.json 同步更新验证
      9. 新路径 .goal-log-db/active/ 验证
     10. v1.1 字段验证：value_criteria / process_criteria / value_ratio / goal_signature / out_of_scope_md / audit_stability / efficiency_stats
     11. value_ratio < 0.6 触发 ValueRatioError（GL-001）
     12. severity_label 非法值触发 SnapshotSchemaError
     13. follow_up_items 追加验证（add_follow_up_item）
     14. audit_stability 结构验证
     15. out_of_scope_md 字段验证
     16. generate_goal_signature 生成一致性（GL-009）
     17. compute_similarity 相似度正确（GL-009）
     18. update_efficiency_stats 写入正确（GL-008）
     19. efficiency_stats 字段存在
     20. CLI list-active exit 0
    """
    import subprocess as sp
    import tempfile

    # 使用临时目录隔离测试
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        global GOALS_DIR, INDEX_DIR, SESSION_INDEX_FILE, THREAD_GOALS_FILE
        original_goals = GOALS_DIR
        original_index = INDEX_DIR
        GOALS_DIR = tmp_path / ".goal-log-db" / "active"
        INDEX_DIR = tmp_path / ".goal-log-db" / "index"
        SESSION_INDEX_FILE = INDEX_DIR / "session-index.jsonl"
        THREAD_GOALS_FILE = INDEX_DIR / "thread_goals.json"

        # Case 1: create_snapshot 落盘并返回 20 字段
        s = create_snapshot(
            "测试目标",
            ["标准1", "标准2"],
            process_criteria=["过程标准1"],
            token_limit=100,
        )
        assert s["status"] == "active"
        assert s["loop_round"] == 0
        assert len(s["value_criteria"]) == 2
        assert len(s["process_criteria"]) == 1
        assert s["value_ratio"] == round(2 / 3, 4)
        assert s["severity_label"] == "MAJOR"
        assert s["follow_up_items"] == []
        assert s["goal_signature_changelog"] == []
        assert s["token_budget"]["limit"] == 100
        assert len(SNAPSHOT_FIELDS) == 20, f"应有 20 字段, got {len(SNAPSHOT_FIELDS)}"
        print(f"  [OK] Case 1: create_snapshot -> goal_id={s['goal_id'][:8]}... (20 字段)")

        # Case 2: load_snapshot 读到完整字段
        loaded = load_snapshot(s["goal_id"])
        assert loaded["goal_id"] == s["goal_id"]
        assert loaded["value_ratio"] == s["value_ratio"]
        assert loaded["severity_label"] == "MAJOR"
        print(f"  [OK] Case 2: load_snapshot 字段完整 (v1.1)")

        # Case 3: update_snapshot 修改 loop_round/status 后落盘
        updated = update_snapshot(s["goal_id"], loop_round=3, latest_artifact="/tmp/x")
        assert updated["loop_round"] == 3
        assert updated["latest_artifact"] == "/tmp/x"
        # 持久化校验
        reloaded = load_snapshot(s["goal_id"])
        assert reloaded["loop_round"] == 3
        print(f"  [OK] Case 3: update_snapshot + 持久化")

        # Case 4a: 缺字段
        try:
            _validate_snapshot({"goal_id": "x"})
            assert False, "应抛 SnapshotSchemaError"
        except SnapshotSchemaError:
            print(f"  [OK] Case 4a: 缺字段拒绝")

        # Case 4b: status 非法
        bad = dict(s)
        bad["status"] = "invalid"
        try:
            _validate_snapshot(bad)
            assert False, "应抛 SnapshotSchemaError"
        except SnapshotSchemaError:
            print(f"  [OK] Case 4b: 非法 status 拒绝")

        # Case 4c: token_budget 非法
        bad2 = dict(s)
        bad2["token_budget"] = {"used": -1, "limit": 100, "updated_at": "x"}
        try:
            _validate_snapshot(bad2)
            assert False, "应抛 SnapshotSchemaError"
        except SnapshotSchemaError:
            print(f"  [OK] Case 4c: 非法 token_budget 拒绝")

        # Case 5: atomic write — 确认 .tmp 不残留
        gd = goal_dir(s["goal_id"])
        tmp_files = list(gd.glob("*.tmp"))
        assert not tmp_files, f"应无 .tmp 残留, got {tmp_files}"
        print(f"  [OK] Case 5: 无 .tmp 残留（atomic write）")

        # Case 6: list_active_goals
        active = list_active_goals()
        assert any(a["goal_id"] == s["goal_id"] for a in active)
        print(f"  [OK] Case 6: list_active_goals 命中新建快照")

        # Case 7: session-index.jsonl 追加记录
        assert SESSION_INDEX_FILE.exists(), "session-index.jsonl 应存在"
        lines = SESSION_INDEX_FILE.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) >= 2, f"应至少 2 条记录（create + update），got {len(lines)}"
        last_record = json.loads(lines[-1])
        assert last_record["goal_id"] == s["goal_id"]
        assert last_record["action"] == "update"
        print(f"  [OK] Case 7: session-index.jsonl 追加 {len(lines)} 条记录")

        # Case 8: thread_goals.json 同步更新
        assert THREAD_GOALS_FILE.exists(), "thread_goals.json 应存在"
        tg = json.loads(THREAD_GOALS_FILE.read_text(encoding="utf-8"))
        task = next((t for t in tg["task_list"] if t["goal_id"] == s["goal_id"]), None)
        assert task is not None, "thread_goals.json 应包含新建任务"
        assert task["status"] == "active"
        print(f"  [OK] Case 8: thread_goals.json 同步更新")

        # Case 9: 新路径验证
        new_snap_path = goal_dir(s["goal_id"]) / SNAPSHOT_FILENAME
        assert new_snap_path.exists(), f"新路径 {new_snap_path} 应存在"
        assert ".goal-log-db" in str(new_snap_path), "路径应包含 .goal-log-db"
        print(f"  [OK] Case 9: 新路径验证通过 -> {new_snap_path.parent.name}/")

        # Case 10: v1.2.1 字段验证（20字段）
        for f in ("value_criteria", "process_criteria", "value_ratio", "severity_label",
                  "follow_up_items", "goal_signature", "goal_signature_changelog",
                  "out_of_scope_md", "audit_stability"):
            assert f in s, f"缺少字段: {f}"
        assert "converged_with_followup" in VALID_STATUS
        assert s["out_of_scope_md"] == ""
        assert s["audit_stability"] == {}
        print(f"  [OK] Case 10: v1.2.1 新增字段验证通过 (20 字段)")

        # Case 11: value_ratio < MIN_VALUE_RATIO_HARD 触发 ValueRatioError（GL-001 收敛硬约束）
        try:
            create_snapshot("目标", ["V1"], process_criteria=["P1", "P2", "P3", "P4"], token_limit=100)
            assert False, "应抛 ValueRatioError"
        except ValueRatioError:
            print(f"  [OK] Case 11: value_ratio < {MIN_VALUE_RATIO_HARD} 触发 ValueRatioError（GL-001 收敛硬约束）")

        # Case 12: severity_label 非法值触发 SnapshotSchemaError
        try:
            create_snapshot("目标", ["V1"], severity_label="INVALID")
            assert False, "应抛 SnapshotSchemaError"
        except SnapshotSchemaError:
            print(f"  [OK] Case 12: severity_label 非法值拒绝")

        # Case 13: add_follow_up_item
        updated = add_follow_up_item(
            s["goal_id"],
            description="遗留问题描述",
            severity="MAJOR",
            suggested_fix="建议修复方向",
            source_round=3,
            source_criterion="V1",
        )
        assert len(updated["follow_up_items"]) == 1
        assert updated["follow_up_items"][0]["severity"] == "MAJOR"
        assert updated["follow_up_items"][0]["description"] == "遗留问题描述"
        print(f"  [OK] Case 13: add_follow_up_item 追加成功")

        # Case 14: audit_stability 结构验证
        updated2 = update_snapshot(
            s["goal_id"],
            audit_stability={"FMT-01": {"consecutive_pass": 2, "stable": True, "skipped": True}},
        )
        assert updated2["audit_stability"]["FMT-01"]["stable"] is True
        assert updated2["audit_stability"]["FMT-01"]["skipped"] is True
        print(f"  [OK] Case 14: audit_stability 结构验证通过")

        # Case 15: out_of_scope_md 字段验证
        updated3 = update_snapshot(s["goal_id"], out_of_scope_md="/path/to/out_of_scope.md")
        assert updated3["out_of_scope_md"] == "/path/to/out_of_scope.md"
        print(f"  [OK] Case 15: out_of_scope_md 字段验证通过")

        # Case 16: generate_goal_signature（GL-009）
        sig1 = generate_goal_signature("创建 Goal Loop Skill")
        sig2 = generate_goal_signature("创建 Goal Loop Skill")
        sig3 = generate_goal_signature("修改 XX 模块")
        assert sig1 == sig2, "相同文本应生成相同签名"
        assert sig1 != sig3, "不同文本应生成不同签名"
        assert len(sig1) == 16, f"签名应为 16 字符, got {len(sig1)}"
        print(f"  [OK] Case 16: generate_goal_signature 生成一致（GL-009）")

        # Case 17: compute_similarity（GL-009）
        sim1 = compute_similarity("创建 Goal Loop Skill", "创建 Goal Loop Skill")
        sim2 = compute_similarity("创建 Goal Loop Skill", "修改 XX 模块")
        assert sim1 == 1.0, f"完全相同文本相似度应为 1.0, got {sim1}"
        assert 0.0 <= sim2 < 1.0, f"不同文本相似度应在 0~1 之间, got {sim2}"
        assert compute_similarity("", "test") == 0.0
        print(f"  [OK] Case 17: compute_similarity 相似度正确（GL-009）")

        # Case 18: update_efficiency_stats（GL-008）
        updated4 = update_efficiency_stats(
            s["goal_id"],
            rounds_to_convergence=3,
            first_pass_rate=0.67,
            blocker_residual_rate=0.0,
        )
        assert updated4["efficiency_stats"]["rounds_to_convergence"] == 3
        assert updated4["efficiency_stats"]["first_pass_rate"] == 0.67
        assert "last_updated" in updated4["efficiency_stats"]
        print(f"  [OK] Case 18: update_efficiency_stats 写入正确（GL-008）")

        # Case 19: efficiency_stats 字段验证
        assert "efficiency_stats" in updated4
        assert isinstance(updated4["efficiency_stats"], dict)
        print(f"  [OK] Case 19: efficiency_stats 字段存在")

        # Case 21: parallel_executor_hints 字段验证（v1.2 新增）
        assert "parallel_executor_hints" in s
        assert isinstance(s["parallel_executor_hints"], dict)
        assert s["parallel_executor_hints"] == {}
        print(f"  [OK] Case 21: parallel_executor_hints 字段存在且为空 dict")

        # Case 22: load_all_active_snapshots 返回完整快照（需 patch 全局路径）
        from unittest.mock import patch as _patch
        import goal_snapshot as _gs_mod
        with _patch.object(_gs_mod, "GOALS_DIR", tmp_path / ".goal-log-db" / "active"):
            with _patch.object(_gs_mod, "INDEX_DIR", tmp_path / ".goal-log-db" / "index"):
                from goal_snapshot import load_all_active_snapshots
                all_active = load_all_active_snapshots()
                assert any(a["goal_id"] == s["goal_id"] for a in all_active)
                assert "task_queue" in all_active[0]
                assert "parallel_executor_hints" in all_active[0]
        print(f"  [OK] Case 22: load_all_active_snapshots 返回完整快照（含 task_queue + parallel_executor_hints）")

        GOALS_DIR = original_goals
        INDEX_DIR = original_index

    # CLI smoke（使用真实路径）
    proc = sp.run(
        [sys.executable, __file__, "list-active"],
        capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 0, f"CLI list-active exit={proc.returncode}"
    print(f"  [OK] Case 20: CLI list-active exit 0")
    print(f"  [OK] self_test passed (22 cases, v1.2)")
    return 0


def test_list_live_goals() -> int:
    """python3 ai_workflow/goal_snapshot.py --test-list-live

    验证 list_live_goals() 不过滤 status 的行为（2 cases）：
      Case 23: status=achieved 的 snapshot → list_live_goals() 包含它；list_active_goals() 不包含
      Case 24: status=active 的 snapshot → list_live_goals() 和 list_active_goals() 都包含
    """
    import tempfile as _tmp
    from unittest.mock import patch as _patch
    import goal_snapshot as _gs_mod

    with _tmp.TemporaryDirectory() as _td:
        _tdp = Path(_td)
        _fake_goals = _tdp / ".goal-log-db" / "active"
        _fake_index = _tdp / ".goal-log-db" / "index"

        with _patch.object(_gs_mod, "GOALS_DIR", _fake_goals):
            with _patch.object(_gs_mod, "INDEX_DIR", _fake_index):
                # Case 23: status=achieved → list_live_goals 包含，list_active_goals 不包含
                achieved_snap = create_snapshot(
                    "已完成的目标",
                    ["标准A"],
                    token_limit=100,
                )
                achieved_id = achieved_snap["goal_id"]
                update_snapshot(achieved_id, status="achieved", loop_round=5)

                live_ids = [g["goal_id"] for g in list_live_goals()]
                active_ids = [g["goal_id"] for g in list_active_goals()]
                assert achieved_id in live_ids, f"achieved goal 应在 list_live_goals, got {live_ids}"
                assert achieved_id not in active_ids, f"achieved goal 不应在 list_active_goals, got {active_ids}"
                print(f"  [OK] Case 23: status=achieved → list_live_goals✓ list_active_goals✗")

                # Case 24: status=active → 两者都包含
                active_snap = create_snapshot(
                    "进行中的目标",
                    ["标准B"],
                    token_limit=100,
                )
                active_id = active_snap["goal_id"]
                live_ids2 = [g["goal_id"] for g in list_live_goals()]
                active_ids2 = [g["goal_id"] for g in list_active_goals()]
                assert active_id in live_ids2, f"active goal 应在 list_live_goals, got {live_ids2}"
                assert active_id in active_ids2, f"active goal 应在 list_active_goals, got {active_ids2}"
                print(f"  [OK] Case 24: status=active → list_live_goals✓ list_active_goals✓")

    print(f"  [OK] test_list_live_goals passed (2 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    elif len(sys.argv) > 1 and sys.argv[1] == "--test-list-live":
        sys.exit(test_list_live_goals())
    sys.exit(_cli(sys.argv[1:]))
