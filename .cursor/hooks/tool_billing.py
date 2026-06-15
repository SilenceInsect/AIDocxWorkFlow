#!/usr/bin/env python3
"""Cursor hook: track per-tool output for billing.

Trigger: postToolUse
Behavior:
  - Estimate tokens from tool response text (when large enough to matter)
  - Write to session_log.jsonl
  - Update cumulative.json
  - Print summary to stderr

Read-only tools (Read/Glob/Grep/etc.) are tracked only when output > 50 KB
to avoid noise from trivial calls.
"""

from __future__ import annotations

import json, sys
from datetime import datetime, timezone
from pathlib import Path

_hook_dir = Path(__file__).parent.resolve()
_sys_path = list(sys.path)
sys.path.insert(0, str(_hook_dir))
try:
    import token_engine as te
finally:
    sys.path[:] = _sys_path

# ── tracked tools ──────────────────────────────────────────────────────────

# Always track these (they produce significant output)
_TRACKED_WRITE = {
    "Write", "StrReplace", "EditNotebook", "Delete",
    "Shell",
}

# Track only when output > 50 KB (avoid noise from trivially small reads)
_TRACKED_READ_LARGE = {
    "Read", "ReadLints", "Glob", "Grep",
    "FetchMcpResource", "ListMcpResources",
}

# Always skip
_SKIPPED = {
    "CallMcpTool", "Task", "AwaitShell",
    "WebSearch", "WebFetch", "SwitchMode",
}

# ── main ────────────────────────────────────────────────────────────────────

def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return

        inp = json.loads(raw)
        tool_use     = inp.get("toolUse", {})
        tool_name    = tool_use.get("name", "")
        tool_args    = tool_use.get("arguments", {})
        result       = inp.get("result", {})
        duration_ms  = inp.get("durationMs", 0)
        tool_index   = inp.get("toolIndex", 0)
        is_error     = result.get("isError", False)
        result_text  = result.get("text", "")

        # Decide if we should track this tool
        if tool_name in _SKIPPED:
            return
        if tool_name in _TRACKED_READ_LARGE and len(result_text) < 50_000:
            return
        if tool_name not in _TRACKED_WRITE and tool_name not in _TRACKED_READ_LARGE:
            return

        # Estimate tokens
        est   = te.from_response_text(result_text)
        model = te.detect_model()
        cost  = te.estimate_cost(model, est["input_tokens"], est["output_tokens"])

        # Source file path
        file_path = tool_args.get("path", "")
        if not file_path:
            file_path = tool_args.get("working_directory", "")

        record = {
            "timestamp":           datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id":         te.get_session_id(),
            "source":             "tool",
            "record_type":        "tool",
            "tool_name":          tool_name,
            "tool_index":          tool_index,
            "model":              model,
            "input_tokens":         est["input_tokens"],
            "output_tokens":        est["output_tokens"],
            "total_tokens":         est["total_tokens"],
            "estimated_cost_usd":   round(cost, 6),
            "latency_ms":         duration_ms,
            "success":            not is_error,
            "file_path":          file_path,
            "result_chars":        est["chars"],
        }

        te.log_session(record)
        running = te.update_cumulative(est["total_tokens"], cost)
        fp_short = (file_path[-35:] if len(file_path) > 35 else file_path) or "-"
        print(
            f"[Billing:tool] {tool_name} | {fp_short} | "
            f"+{est['total_tokens']:,}t | cume {int(running['total_tokens']):,}t | "
            f"${cost:.4f}",
            file=sys.stderr,
        )

    except json.JSONDecodeError:
        pass
    except Exception as exc:
        print(f"[ToolBilling Error] {type(exc).__name__}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
