#!/usr/bin/env python3
"""Cursor hook: post-process MCP tool execution for token billing.

Trigger: Runs after any MCP tool call completes.
Behavior:
  1. Parse the hook input (tool name, args, result, duration)
  2. If the tool is a workflow stage (wf_*), emit a billing note to stderr
  3. Write a lightweight JSON line to workflow_assets/billing_logs/hook_billing.jsonl
     so external dashboards can tail it
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
BILLING_LOGS_DIR = _PROJECT_ROOT / "workflow_assets" / "billing_logs"

_CHARS_TO_INPUT_TOKENS = 0.25
_CHARS_TO_OUTPUT_TOKENS = 0.30

_TOKEN_PRICING = {
    "composer-2.5": (15.0, 75.0),
    "claude-opus-4": (15.0, 75.0),
    "claude-sonnet-4": (3.0, 15.0),
    "gpt-4o": (2.5, 10.0),
    "default": (10.0, 30.0),
}

_STEP_NAMES = {
    "wf_review_requirement": ("S1-Review", 1),
    "wf_break_down_requirement": ("S2-Breakdown", 2),
    "wf_export_prototype": ("S3-Prototype", 3),
    "wf_export_flowchart": ("S4-Flowchart", 4),
    "wf_generate_test_points": ("S5-TestPoints", 5),
    "wf_generate_test_cases": ("S6-TestCases", 6),
    "wf_review_test_cases": ("S7-Review", 7),
    "wf_self_iterate": ("S8-Iterate", 8),
    "wf_full_flow": ("FullPipeline", 0),
    "wf_simple_flow": ("SimplePipeline", 0),
}


def _estimate_tokens(chars: int, mode: str = "input") -> int:
    ratio = _CHARS_TO_INPUT_TOKENS if mode == "input" else _CHARS_TO_OUTPUT_TOKENS
    return max(1, int(chars * ratio))


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    in_rate, out_rate = _TOKEN_PRICING.get(model, _TOKEN_PRICING["default"])
    return (input_tokens * in_rate + output_tokens * out_rate) / 1_000_000


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            return

        hook_input = json.loads(raw_input)
        tool_call = hook_input.get("toolCall", {})
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("arguments", {})
        result = hook_input.get("result", {})
        duration_ms = hook_input.get("durationMs", 0)

        if not tool_name.startswith("wf_"):
            return

        step_info = _STEP_NAMES.get(tool_name, (tool_name, 99))
        step_label, step_number = step_info

        version = tool_args.get("version", "v1.0")

        req_text = tool_args.get("requirement_text", "")
        prompt_chars = len(req_text) or sum(len(str(v)) for v in tool_args.values())
        response_text = result.get("text", "")
        response_chars = len(response_text) if isinstance(response_text, str) else len(str(response_text))

        model = "composer-2.5"
        input_tokens = _estimate_tokens(prompt_chars, "input")
        output_tokens = _estimate_tokens(response_chars, "output")
        total_tokens = input_tokens + output_tokens
        cost = _estimate_cost(model, input_tokens, output_tokens)

        is_error = result.get("isError", False)

        billing = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "record_id": f"{step_label}-{version}",
            "tool_name": tool_name,
            "step_label": step_label,
            "step_number": step_number,
            "version": version,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "latency_ms": duration_ms,
            "estimated_cost_usd": round(cost, 6),
            "prompt_chars": prompt_chars,
            "response_chars": response_chars,
            "success": not is_error,
            "pipeline_type": "full" if "full" in tool_name else "simple",
        }

        BILLING_LOGS_DIR.mkdir(parents=True, exist_ok=True)
        hook_log = BILLING_LOGS_DIR / "hook_billing.jsonl"
        with hook_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(billing, ensure_ascii=False) + "\n")

        status = "OK" if billing["success"] else "ERR"
        print(
            f"[Billing] {step_label} | {version} | "
            f"tokens: {total_tokens:,} | est: ${cost:.4f} | {duration_ms}ms | {status}",
            file=sys.stderr,
        )

    except json.JSONDecodeError:
        pass
    except Exception as exc:
        print(f"[BillingHook Error] {type(exc).__name__}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
