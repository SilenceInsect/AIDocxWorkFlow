#!/usr/bin/env python3
"""Cursor hook: track token usage per conversation turn and per session.

Triggers:
  - afterAgentResponse : fires after every AI response (text available in payload)
  - sessionEnd         : fires when the conversation ends (final summary)

Input via stdin (JSON).  Schema varies by event — see handlers below.
"""

from __future__ import annotations

import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

_hook_dir = Path(__file__).parent.resolve()
_sys_path = list(sys.path)
sys.path.insert(0, str(_hook_dir))
try:
    import token_engine as te
finally:
    sys.path[:] = _sys_path

# ── session-level state (written between hook invocations) ───────────────────

_SESSION_STATE_FILE = _hook_dir / ".billing_session_state.json"

def _load_state() -> dict:
    if _SESSION_STATE_FILE.exists():
        try:
            with _SESSION_STATE_FILE.open(encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "session_id": te.get_session_id(),
        "turn_count": 0,
        "total_input_chars": 0,
        "total_output_chars": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cost": 0.0,
    }

def _save_state(state: dict) -> None:
    with _SESSION_STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)

# ── afterAgentResponse handler ─────────────────────────────────────────────
#
# Schema (approximate — verify against actual Cursor payload):
# {
#   "message": {
#     "content": [...],
#     "role": "assistant"
#   },
#   "prompt": "...",
#   "model": "...",
#   "usage": {          ← present only when Cursor exposes it
#     "inputTokens": N,
#     "outputTokens": N
#   },
#   "durationMs": N,
#   "turnNumber": N,
#   "messageIndex": N
# }

def handle_agent_response(inp: dict) -> None:
    msg   = inp.get("message", {})
    usage = inp.get("usage", {})
    prompt_text = inp.get("prompt", "")
    turn_number = inp.get("turnNumber", inp.get("turn_number", 0))
    duration_ms = inp.get("durationMs", 0)
    model = inp.get("model") or te.detect_model()

    # Build text from message content blocks
    response_text = _extract_message_text(msg)

    # Use actual token counts if available, otherwise estimate
    raw_in  = usage.get("inputTokens", 0)
    raw_out = usage.get("outputTokens", 0)
    if raw_in and raw_out:
        est = te.from_actual_counts(raw_in, raw_out, model)
    else:
        est = te.from_response_text(response_text, model)
        if prompt_text:
            p_est = te.from_prompt_text(prompt_text, model)
            est["input_tokens"] = p_est["input_tokens"]

    cost = te.estimate_cost(model, est["input_tokens"], est["output_tokens"])

    record = {
        "timestamp":         datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id":       te.get_session_id(),
        "source":           "conv",
        "record_type":      "turn",
        "turn_number":      turn_number,
        "model":            model,
        "input_tokens":      est["input_tokens"],
        "output_tokens":     est["output_tokens"],
        "total_tokens":      est["total_tokens"],
        "estimated_cost_usd": round(cost, 6),
        "latency_ms":       duration_ms,
        "response_chars":    est["chars"],
        "prompt_chars":      len(prompt_text) if prompt_text else None,
    }

    te.log_session(record)
    running = te.update_cumulative(est["total_tokens"], cost)
    print(te.fmt_turn(record, running), file=sys.stderr)

    # Update running state
    state = _load_state()
    state["turn_count"]          = turn_number
    state["total_input_tokens"]  += est["input_tokens"]
    state["total_output_tokens"] += est["output_tokens"]
    state["total_cost"]          += cost
    _save_state(state)


# ── sessionEnd handler ─────────────────────────────────────────────────────
#
# Schema:
# {
#   "sessionId": "...",
#   "durationMs": N,
#   "reason": "completed" | "aborted" | "error" | "window_close" | "user_close",
#   "finalStatus": {...},
#   "usage": {           ← present only on cloud/local when exposed
#     "inputTokens": N,
#     "outputTokens": N
#   },
#   "turnCount": N,
#   "loopCount": N
# }

def handle_session_end(inp: dict) -> None:
    session_id  = inp.get("sessionId", te.get_session_id())
    duration_ms = inp.get("durationMs", 0)
    reason      = inp.get("reason", "unknown")
    turn_count  = inp.get("turnCount", 0)
    loop_count  = inp.get("loopCount", 0)
    usage       = inp.get("usage", {})
    model       = te.detect_model()

    raw_in  = usage.get("inputTokens", 0)
    raw_out = usage.get("outputTokens", 0)

    # Fall back to tracked state
    state = _load_state()

    if raw_in and raw_out:
        est = te.from_actual_counts(raw_in, raw_out, model)
    else:
        # Use accumulated state values
        est = {
            "input_tokens":  state["total_input_tokens"],
            "output_tokens": state["total_output_tokens"],
            "total_tokens":  state["total_input_tokens"] + state["total_output_tokens"],
            "estimated_cost_usd": round(te.estimate_cost(
                model, state["total_input_tokens"], state["total_output_tokens"]), 6),
            "chars": None,
        }

    record = {
        "timestamp":          datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id":        session_id,
        "source":            "session",
        "record_type":       "session_end",
        "model":             model,
        "input_tokens":       est["input_tokens"],
        "output_tokens":      est["output_tokens"],
        "total_tokens":       est["total_tokens"],
        "estimated_cost_usd": round(est["estimated_cost_usd"], 6),
        "duration_ms":        duration_ms,
        "reason":            reason,
        "turn_count":        state["turn_count"] or turn_count,
        "loop_count":        loop_count,
    }

    te.log_session(record)

    print(te.fmt_session_end(record, {}), file=sys.stderr)

    # Clean up session state
    if _SESSION_STATE_FILE.exists():
        _SESSION_STATE_FILE.unlink()


# ── message text extraction ────────────────────────────────────────────────

def _extract_message_text(msg: dict) -> str:
    """Flatten all content blocks in an agent message to plain text."""
    parts = []
    content = msg.get("content", [])
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                for field in ("text", "content", "assistant_content", "value"):
                    val = block.get(field, "")
                    if val:
                        parts.append(str(val))
            elif block:
                parts.append(str(block))
    return "\n".join(parts)


# ── subagentStop handler ────────────────────────────────────────────────────
#
# Schema:
# {
#   "subagentId": "...",
#   "durationMs": N,
#   "status": "completed" | "error" | "aborted",
#   "messageCount": N,
#   "toolCallCount": N,
#   "modifiedFiles": [...],
#   "usage": { "inputTokens": N, "outputTokens": N }
# }

def handle_subagent_stop(inp: dict) -> None:
    duration_ms   = inp.get("durationMs", 0)
    status        = inp.get("status", "completed")
    msg_count     = inp.get("messageCount", 0)
    tool_count    = inp.get("toolCallCount", 0)
    modified      = inp.get("modifiedFiles", [])
    usage         = inp.get("usage", {})
    model         = te.detect_model()

    raw_in  = usage.get("inputTokens", 0)
    raw_out = usage.get("outputTokens", 0)
    if raw_in and raw_out:
        est = te.from_actual_counts(raw_in, raw_out, model)
    else:
        # Rough estimate: ~200 chars/message, ~300 chars/tool
        chars_est = msg_count * 200 + tool_count * 300
        est = te.from_response_text("x" * chars_est, model)

    cost = te.estimate_cost(model, est["input_tokens"], est["output_tokens"])

    record = {
        "timestamp":          datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id":        te.get_session_id(),
        "source":            "subagent",
        "record_type":       "subagent_stop",
        "subagent_id":       inp.get("subagentId", "?"),
        "model":             model,
        "input_tokens":       est["input_tokens"],
        "output_tokens":      est["output_tokens"],
        "total_tokens":       est["total_tokens"],
        "estimated_cost_usd": round(cost, 6),
        "duration_ms":        duration_ms,
        "status":            status,
        "message_count":     msg_count,
        "tool_call_count":   tool_count,
        "modified_files":     modified,
    }

    te.log_session(record)
    running = te.update_cumulative(est["total_tokens"], cost)
    sub_id  = inp.get("subagentId", "?")[:12]
    print(
        f"[Billing:subagent] {sub_id} | {status} | "
        f"+{est['total_tokens']:,}t | ${cost:.4f} | {duration_ms}ms",
        file=sys.stderr,
    )


# ── main router ────────────────────────────────────────────────────────────

def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        inp = json.loads(raw)

        # Determine event type from keys
        # afterAgentResponse has "message" key
        # sessionEnd has "sessionId" key
        # subagentStop has "subagentId" key
        if "message" in inp and "sessionId" not in inp:
            handle_agent_response(inp)
        elif "sessionId" in inp:
            handle_session_end(inp)
        elif "subagentId" in inp:
            handle_subagent_stop(inp)

    except json.JSONDecodeError:
        pass
    except Exception as exc:
        print(f"[SessionBilling Error] {type(exc).__name__}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
