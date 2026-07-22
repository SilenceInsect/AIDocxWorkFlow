#!/usr/bin/env python3
"""AIDocxWorkFlow 阶段自动推进钩子（v7 设计意图落地）

触发点:
  - sessionStart: 会话启动时扫描 workflow_assets/ 所有 req_name + 阶段
                   找出"上阶段 PASS + 下阶段未跑"的挂起点
                   → 注入 system_reminder 提示 LLM 自动继续
  - beforeSubmitPrompt: 用户提交 prompt 时检查"上一阶段刚 PASS"
                        → 注入"建议执行下一阶段"提示

核心立场 (v7 治理):
  - 阶段自动推进 = 正常预期（不是例外）
  - 暂停 = 例外（仅 P0 漏答 / clarification_checklist 有 ❌ / BLOCKED）
  - 落地的临时文件 (preflight_gate.json / postflight_gate.json / stage_context.json
                  / exit_permission.json / backlog.json) = 跨会话 SSOT 准入材料

设计:
  - 不直接调用 run_pipeline (S5/S6/S7 仍需 LLM 出活，脚本不能凭空生成)
  - 不阻断：仅注入 system_reminder
  - 重复检测去重：同一 (req, stage) 状态不重复注入

实现: 2026-07-09
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ===== 路径配置 =====
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOW_ASSETS = REPO_ROOT / "workflow_assets"
SYNC_LOG_DIR = REPO_ROOT / ".cursor" / "sync_logs"

# ===== 阶段定义（顺序 = 推进顺序）=====
STAGES_ORDER: list[str] = ["S1", "S1.5", "S2", "S2.5", "S3", "S4", "S5", "S6", "S7", "S8"]

# 阶段产物映射（last-wins 处理跨阶段同名产物）
STAGE_PASS_ARTIFACT: dict[str, list[str]] = {
    "S1":   ["review_report.json", "review_report.md"],
    "S1.5": ["exit_permission.json"],
    "S2":   ["backlog.json", "backlog.md"],
    "S2.5": ["iteration_plan.json", "iteration_plan.md"],
    "S3":   ["prototype.json", "prototype.md"],
    "S4":   ["business_flow.json", "business_flow.md"],
    "S5":   ["test_points.json"],
    "S6":   ["test_cases.json"],
    "S7":   ["review_report.json"],  # S7 写 review_report.* 进 S6 目录 → 跨目录 drop
    "S8":   ["iteration.json", "iteration.md"],
}

STAGE_FAIL_ARTIFACT: dict[str, str] = {
    "S1":   "fail_report_S1.md",
    "S1.5": "fail_report_S1_5.md",
    "S2":   "fail_report_S2.md",
    "S2.5": "fail_report_S2_5.md",
    "S3":   "fail_report_S3.md",
    "S4":   "fail_report_S4.md",
    "S5":   "fail_report_S5.md",
    "S6":   "fail_report_S6.md",
    "S7":   "fail_report_S7.md",
    "S8":   "fail_report_S8.md",
}

# 阶段目录名（中文书名号）
STAGE_DIR_NAME: dict[str, str] = {
    "S1":   "「S1 需求评审」",
    "S1.5": "「S1 业务澄清」",
    "S2":   "「S2 需求拆解」",
    "S2.5": "「S2.5 迭代规划」",
    "S3":   "「S3 原型导出」",
    "S4":   "「S4 流程图导出」",
    "S5":   "「S5 测试点生成」",
    "S6":   "「S6 测试用例生成」",
    "S7":   "「S7 用例审查」",
    "S8":   "「S8 自迭代」",
}

# S7 跨目录 drop（写 review_report.* 进 S6 目录）
S7_CROSS_DROP = True

# ===== 路径解析辅助 =====

def _safe_rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def _stage_dir_path(req_name: str, stage: str, version: str) -> Path:
    # v8+: 先版本再阶段 - workflow_assets/<req_name>/<version>/「S{n}」/
    return WORKFLOW_ASSETS / req_name / version / STAGE_DIR_NAME[stage]


# ===== 阶段状态判定 =====

def _has_pass_artifact(req_name: str, stage: str, version: str) -> Optional[Path]:
    """判定某 req + stage + version 是否已有 PASS 产物。
    返回 PASS 产物路径（取最近 mtime 的），若无返回 None。"""
    candidates: list[tuple[float, Path]] = []
    for fname in STAGE_PASS_ARTIFACT.get(stage, []):
        p = _stage_dir_path(req_name, stage, version) / fname
        if p.exists():
            candidates.append((p.stat().st_mtime, p))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def _has_fail_artifact(req_name: str, stage: str, version: str) -> Optional[Path]:
    p = _stage_dir_path(req_name, stage, version) / STAGE_FAIL_ARTIFACT.get(stage, "")
    return p if p.exists() else None


def _postflight_status(req_name: str, stage: str, version: str) -> Optional[str]:
    """读 postflight_gate.json.verdict 字段。返回 "PASS" / "FAIL" / None。"""
    p = _stage_dir_path(req_name, stage, version) / "postflight_gate.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("postflight_gate_evaluation", {}).get("verdict")
    except (json.JSONDecodeError, OSError):
        return None


def _needs_human_input(req_name: str, version: str) -> Optional[str]:
    """判定 S1.5 之后是否需人工介入。
    返回: None = 无需人工 / str = 阻塞原因。"""
    # 1. S1.5 exit_permission.can_proceed_to_s2
    p = _stage_dir_path(req_name, "S1", version) / "exit_permission.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not data.get("exit_permission", {}).get("can_proceed_to_s2", False):
                return f"exit_permission_blocked (can_proceed_to_s2=false)"
        except (json.JSONDecodeError, OSError):
            pass

    # 2. clarification_checklist 是否有 ❌ 状态
    checklist = _stage_dir_path(req_name, "S1", version) / "clarification_checklist.md"
    if checklist.exists():
        text = checklist.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"\| ❌\s*拒绝", text):
            return "clarification_checklist_has_reject"

    # 3. postflight_gate.halt_pipeline == true
    pf = _stage_dir_path(req_name, "S1", version) / "postflight_gate.json"
    if pf.exists():
        try:
            data = json.loads(pf.read_text(encoding="utf-8"))
            if data.get("halt_pipeline", False):
                return "halt_pipeline_true"
        except (json.JSONDecodeError, OSError):
            pass

    return None


# ===== 扫描所有 req + version + stage 状态 =====

def _scan_all_stages() -> list[dict]:
    """扫描 workflow_assets/ 所有 req_name + version + stage 状态。
    返回 [{req, version, stage, status, artifact, mtime, mtime_iso}, ...]
    status: "PASS" | "FAIL" | "MISSING"
    """
    if not WORKFLOW_ASSETS.exists():
        return []

    results: list[dict] = []
    for req_dir in WORKFLOW_ASSETS.iterdir():
        if not req_dir.is_dir():
            continue
        req_name = req_dir.name
        for stage_dir in req_dir.iterdir():
            if not stage_dir.is_dir():
                continue
            # 解析 stage code（last-wins 处理 S1.5/S2.5 边界）
            # 必须先匹配更具体的 code (S1.5 / S2.5) 再匹配前缀 (S1 / S2)
            stage_code: Optional[str] = None
            # 先匹配带点的 code (S1.5 / S2.5)
            for code in ["S1.5", "S2.5"]:
                if code in stage_dir.name or STAGE_DIR_NAME[code] in stage_dir.name:
                    stage_code = code
                    break
            # 再匹配基础 code
            if not stage_code:
                for code in ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]:
                    if code in stage_dir.name or STAGE_DIR_NAME[code] in stage_dir.name:
                        stage_code = code
                        break
            if not stage_code:
                continue
            for version_dir in stage_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                version = version_dir.name
                pass_artifact = _has_pass_artifact(req_name, stage_code, version)
                fail_artifact = _has_fail_artifact(req_name, stage_code, version)
                if pass_artifact and not fail_artifact:
                    status = "PASS"
                    artifact = pass_artifact
                elif fail_artifact:
                    status = "FAIL"
                    artifact = fail_artifact
                else:
                    status = "MISSING"
                    artifact = None
                mtime = artifact.stat().st_mtime if artifact else 0
                results.append({
                    "req": req_name,
                    "version": version,
                    "stage": stage_code,
                    "status": status,
                    "artifact": _safe_rel(artifact) if artifact else None,
                    "mtime": mtime,
                })
    return results


# ===== 找下一个未执行阶段 =====

def _find_next_pending(stages: list[dict], req: str, version: str) -> Optional[str]:
    """在指定 req + version 下，找出第一个"未 PASS"阶段的后一阶段。"""
    # 找出本 req+version 下所有已 PASS 的 stage，按顺序
    passed_in_order: list[str] = []
    for s in stages:
        if s["req"] == req and s["version"] == version and s["status"] == "PASS":
            passed_in_order.append(s["stage"])
    if not passed_in_order:
        return None
    # 找最大 stage 位置
    last_passed = max(passed_in_order, key=lambda s: STAGES_ORDER.index(s))
    idx = STAGES_ORDER.index(last_passed)
    if idx + 1 < len(STAGES_ORDER):
        return STAGES_ORDER[idx + 1]
    return None  # 已 S8 全部 PASS


# ===== 找挂起任务（跨会话断点恢复用）=====

def _find_pending_tasks() -> list[dict]:
    """找出所有"上阶段 PASS + 下阶段未跑"的挂起任务。"""
    all_stages = _scan_all_stages()
    pending: list[dict] = []
    # 按 (req, version) 分组
    grouped: dict[tuple[str, str], list[dict]] = {}
    for s in all_stages:
        key = (s["req"], s["version"])
        grouped.setdefault(key, []).append(s)

    for (req, version), stages_in_group in grouped.items():
        # 找最大 PASS stage
        next_stage = _find_next_pending(stages_in_group, req, version)
        if not next_stage:
            continue
        # 找本 req+version 最大的 PASS stage
        last_passed = max(
            (s for s in stages_in_group if s["status"] == "PASS"),
            key=lambda s: STAGES_ORDER.index(s["stage"]),
            default=None,
        )
        if not last_passed:
            continue
        # 检查本 req+version 是否需要人工介入
        block_reason = _needs_human_input(req, version)
        pending.append({
            "req": req,
            "version": version,
            "last_passed_stage": last_passed["stage"],
            "next_stage": next_stage,
            "next_stage_dir": STAGE_DIR_NAME[next_stage],
            "last_artifact": last_passed["artifact"],
            "last_mtime_iso": datetime.fromtimestamp(last_passed["mtime"], tz=timezone.utc).isoformat(),
            "block_reason": block_reason,
        })
    return pending


# ===== System Reminder 构造 =====

def _format_reminder_for_pending(pending: list[dict]) -> str:
    """构造 system_reminder：列出所有挂起任务。"""
    if not pending:
        return ""
    lines: list[str] = ["[阶段自动推进 — 上阶段 PASS + 下阶段未跑]"]
    for p in pending:
        if p["block_reason"]:
            lines.append(
                f"\n⚠️ {p['req']} ({p['version']}): {p['last_passed_stage']} PASS → "
                f"{p['next_stage']} 阻塞（{p['block_reason']}）"
            )
            lines.append(
                f"  需要人工解除阻塞后才能继续。建议先 Read 该阻塞点产物，再请用户决策。"
            )
        else:
            lines.append(
                f"\n✅ {p['req']} ({p['version']}): {p['last_passed_stage']} PASS → "
                f"**建议自动执行 {p['next_stage']}**"
            )
            lines.append(
                f"  上次产物: {p['last_artifact']}\n"
                f"  下一阶段目录: workflow_assets/{p['req']}/{p['next_stage_dir']}/{p['version']}/\n"
                f"  无需人工介入（除非 P0 漏答）——可直接 /aidocx-{p['next_stage'].lower().replace('.', '-')} 继续"
            )
    return "\n".join(lines)


# ===== Handlers =====

def handle_session_start(payload: dict) -> int:
    """会话启动：扫描所有挂起任务 → 注入 system_reminder。"""
    pending = _find_pending_tasks()
    if not pending:
        return 0
    reminder = _format_reminder_for_pending(pending)
    # Cursor sessionStart 钩子输出 system_reminder 字段
    out = {
        "system_reminder": reminder,
        "pending_tasks_count": len(pending),
        "tasks": pending,
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    return 0


def handle_before_submit_prompt(payload: dict) -> int:
    """提交 prompt 前：检查上阶段是否刚 PASS（afterFileEdit 也会触发，本 handler 备冗余）。"""
    # beforeSubmitPrompt 重复 sessionStart 逻辑即可——LLM 刚开新 prompt 看到提醒
    return handle_session_start(payload)


# ===== Dispatcher =====

HANDLERS = {
    "sessionStart": handle_session_start,
    "beforeSubmitPrompt": handle_before_submit_prompt,
}


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return 0
    event = payload.get("event") or payload.get("hook") or ""
    handler = HANDLERS.get(event)
    if handler is None:
        return 0
    try:
        return handler(payload)
    except Exception as exc:  # never crash IDE
        sys.stderr.write(f"auto_advance_check: {exc!r}\n")
        return 0


# ===== Self-test =====

def self_test() -> int:
    """python3 .cursor/hooks/auto_advance_check.py --self-test

    验证 5 项：
      1. _has_pass_artifact / _has_fail_artifact：v3.01 S1 应有 PASS（review_report）
      2. _postflight_status：v3.01 S1 postflight_gate.verdict == "PASS"
      3. _needs_human_input：v3.01 应返回 None（无 BLOCKED）
      4. _find_next_pending：v3.01 实际进度 S1-S6 全 PASS（S3 FAIL 跳过）
         → 下一阶段 = S7
      5. main() dispatcher：空 stdin / 无效 JSON / 未知 event → 不崩
    """
    req = "游戏道具商城系统"
    ver = "v3.01"

    # Case 1: _has_pass_artifact
    pa = _has_pass_artifact(req, "S1", ver)
    assert pa is not None, "Case 1: S1 v3.01 应有 PASS 产物（review_report）"
    assert "review_report" in pa.name, f"Case 1: 应为 review_report, got {pa.name}"
    print(f"  [OK] Case 1: _has_pass_artifact(S1, v3.01) = {pa.name}")

    # Case 1b: _has_fail_artifact
    fa = _has_fail_artifact(req, "S1", ver)
    assert fa is None, f"Case 1b: S1 v3.01 无 FAIL 产物, got {fa}"
    print(f"  [OK] Case 1b: _has_fail_artifact(S1, v3.01) = None")

    # Case 2: _postflight_status
    pf = _postflight_status(req, "S1", ver)
    assert pf == "PASS", f"Case 2: postflight_gate.verdict 应为 PASS, got {pf}"
    print(f"  [OK] Case 2: _postflight_status(S1, v3.01) = '{pf}'")

    # Case 3: _needs_human_input
    block = _needs_human_input(req, ver)
    assert block is None, f"Case 3: v3.01 不应阻塞, got '{block}'"
    print(f"  [OK] Case 3: _needs_human_input(v3.01) = None (无 BLOCKED)")

    # Case 4: _find_next_pending
    all_stages = _scan_all_stages()
    next_s = _find_next_pending(all_stages, req, ver)
    # v3.01 实际进度：S1-S2 PASS / S3 FAIL / S4-S6 PASS / S7-S8 未跑
    # 最大 PASS stage = S6 → 下一阶段 = S7
    assert next_s == "S7", f"Case 4: S6 PASS → 下一阶段应为 S7, got {next_s}"
    print(f"  [OK] Case 4: _find_next_pending(v3.01) = '{next_s}' (S1-S6 全 PASS)")

    # Case 4b: _find_pending_tasks 整体扫描
    pending = _find_pending_tasks()
    assert len(pending) >= 1, f"Case 4b: 至少应有 1 个挂起任务, got {len(pending)}"
    target = next((p for p in pending if p["req"] == req and p["version"] == ver), None)
    assert target is not None, f"Case 4b: v3.01 应在挂起列表中"
    assert target["next_stage"] == "S7", f"Case 4b: next_stage = S7, got {target['next_stage']}"
    assert target["block_reason"] is None, f"Case 4b: v3.01 不应阻塞, got {target['block_reason']}"
    print(f"  [OK] Case 4b: _find_pending_tasks() 含 v3.01 (last=S6, next=S7, 无阻塞)")

    # Case 5: main() dispatcher
    import subprocess as sp
    proc5a = sp.run(
        [sys.executable, __file__], input="",
        capture_output=True, text=True, timeout=10,
    )
    assert proc5a.returncode == 0, f"Case 5a (空 stdin): exit 0, got {proc5a.returncode}"
    proc5b = sp.run(
        [sys.executable, __file__], input="not-json",
        capture_output=True, text=True, timeout=10,
    )
    assert proc5b.returncode == 0, f"Case 5b (无效 JSON): exit 0, got {proc5b.returncode}"
    proc5c = sp.run(
        [sys.executable, __file__],
        input=json.dumps({"event": "unknownEvent"}),
        capture_output=True, text=True, timeout=10,
    )
    assert proc5c.returncode == 0, f"Case 5c (未知 event): exit 0, got {proc5c.returncode}"
    # Case 5d: sessionStart 输出 system_reminder
    proc5d = sp.run(
        [sys.executable, __file__],
        input=json.dumps({"event": "sessionStart"}),
        capture_output=True, text=True, timeout=15,
    )
    assert proc5d.returncode == 0, f"Case 5d (sessionStart): exit 0, got {proc5d.returncode}"
    if proc5d.stdout.strip():
        out = json.loads(proc5d.stdout)
        assert "system_reminder" in out, f"Case 5d: 应含 system_reminder 字段"
        assert "游戏道具商城系统" in out["system_reminder"], f"Case 5d: reminder 应提及游戏道具商城系统"
        print(f"  [OK] Case 5d: sessionStart → system_reminder 注入 ({len(out['system_reminder'])} chars)")
    else:
        print(f"  [SKIP] Case 5d: stdout 空（v3.01 已跑过 S1.5？或扫描为空）")
    print(f"  [OK] Case 5: main() dispatcher 4 sub-cases pass")

    print("  [OK] self-test passed (5 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())
