#!/usr/bin/env python3
"""Cursor hook: track MCP tool execution for billing.

Trigger: afterMCPExecution
Behavior:
  - Parse MCP tool call result
  - Estimate tokens from tool response
  - Write to session_log.jsonl
  - Update cumulative.json
  - Print summary to stderr

Input via stdin:
  {
    "toolCall": { "name": "...", "arguments": {...} },
    "result":  { "text": "...", "isError": false },
    "durationMs": N
  }
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

_STEP_NAMES = {
    "wf_review_requirement":     ("S1-Review",     1),
    "wf_break_down_requirement": ("S2-Breakdown",   2),
    "wf_export_prototype":      ("S3-Prototype",   3),
    "wf_export_flowchart":      ("S4-Flowchart",   4),
    "wf_generate_test_points":  ("S5-TestPoints",  5),
    "wf_generate_test_cases":   ("S6-TestCases",   6),
    "wf_review_test_cases":     ("S7-Review",      7),
    "wf_self_iterate":          ("S8-Iterate",     8),
    "wf_full_flow":             ("FullPipeline",    0),
    "wf_simple_flow":           ("SimplePipeline",  0),
}


def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return

        inp    = json.loads(raw)
        tcall  = inp.get("toolCall", {})
        tname  = tcall.get("name", "")
        targs  = tcall.get("arguments", {})
        result = inp.get("result", {})
        dur    = inp.get("durationMs", 0)
        is_err = result.get("isError", False)

        # Only track workflow tools (wf_*)
        if not tname.startswith("wf_"):
            return

        step_label, step_number = _STEP_NAMES.get(tname, (tname, 99))
        version = targs.get("version", "v1.0")

        # Estimate input from args
        args_text = targs.get("requirement_text", "") or \
            " ".join(str(v) for v in targs.values())
        in_est = te.from_prompt_text(args_text)

        # Estimate output from response
        resp_text = result.get("text", "")
        out_est   = te.from_response_text(resp_text)

        model = te.detect_model()
        cost  = te.estimate_cost(model, in_est["input_tokens"], out_est["output_tokens"])

        record = {
            "timestamp":           datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id":         te.get_session_id(),
            "source":            "mcp",
            "record_type":       "mcp",
            "record_id":         f"{step_label}-{version}",
            "tool_name":         tname,
            "step_label":        step_label,
            "step_number":        step_number,
            "version":           version,
            "model":             model,
            "input_tokens":        in_est["input_tokens"],
            "output_tokens":       out_est["output_tokens"],
            "total_tokens":        in_est["input_tokens"] + out_est["output_tokens"],
            "estimated_cost_usd":  round(cost, 6),
            "latency_ms":        dur,
            "success":           not is_err,
            "pipeline_type":     "full" if "full" in tname else "simple",
            "prompt_chars":       in_est["prompt_chars"],
            "response_chars":      out_est["chars"],
        }

        te.log_session(record)
        running = te.update_cumulative(
            in_est["input_tokens"] + out_est["output_tokens"], cost)

        status = "OK" if record["success"] else "ERR"
        print(
            f"[Billing:mcp] {step_label} | {version} | "
            f"+{record['total_tokens']:,}t | "
            f"cume {int(running['total_tokens']):,}t / ${running['total_cost']:.4f} | "
            f"${cost:.4f} | {dur}ms | {status}",
            file=sys.stderr,
        )

    except json.JSONDecodeError:
        pass
    except Exception as exc:
        print(f"[MCPBilling Error] {type(exc).__name__}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
