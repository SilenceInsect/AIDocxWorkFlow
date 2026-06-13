#!/usr/bin/env python3
"""Shared token/cost estimation engine for AIDocxWorkFlow billing.

Used by:
  - afterAgentResponse / sessionEnd / subagentStop → session_billing.py
  - postToolUse                                   → tool_billing.py
  - afterMCPExecution                             → mcp_billing.py
"""

from __future__ import annotations

import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── paths ──────────────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
BILLING_DIR   = _PROJECT_ROOT / "workflow_assets" / "billing_logs"
SESSION_LOG   = BILLING_DIR / "session_log.jsonl"
CUMULATIVE   = BILLING_DIR / "cumulative.json"

# ── pricing ────────────────────────────────────────────────────────────────

_CHARS_IN  = 0.25   # chars → input-tokens
_CHARS_OUT = 0.30   # chars → output-tokens

_TOKEN_PRICE = {          # (input_$/M, output_$/M) — 2026年6月官方定价
    # Composer 2.5
    "composer-2.5-fast":     (3.00,  15.00),   # 默认快速档 (Interactive)
    "composer-2.5":           (3.00,  15.00),   # Fast (default); fallback key
    "composer-2.5-standard": (0.50,   2.50),   # 标准档（后台/长任务）
    # Claude 4.x (2026)
    "claude-opus-4.8":      (5.00,  25.00),
    "claude-opus-4.7":      (5.00,  25.00),
    "claude-opus-4.6":      (5.00,  25.00),
    "claude-opus-4.5":      (5.00,  25.00),
    "claude-opus-4":        (15.00, 75.00),   # deprecated legacy
    "claude-sonnet-4.6":    (3.00,  15.00),
    "claude-sonnet-4.5":    (3.00,  15.00),
    "claude-sonnet-4":      (3.00,  15.00),
    "claude-haiku-4.5":     (1.00,   5.00),
    "claude-haiku-3.5":     (0.80,   4.00),
    # OpenAI
    "gpt-4o":               (2.50,  10.00),
    "gpt-4o-mini":          (0.15,   0.60),
    # fallback
    "default":               (3.00,  15.00),
}

# ── model detection ───────────────────────────────────────────────────────

def detect_model() -> str:
    """Detect model from environment. Returns the most specific matching key."""
    for var in ("CURSOR_MODEL", "ANTHROPIC_MODEL", "CURSOR_AGENT_MODEL", "MODEL"):
        val = os.environ.get(var, "")
        if not val:
            continue
        val_lower = val.lower()
        # Try exact/partial matches from most to least specific
        for known in (
            "composer-2.5-standard", "composer-2.5-fast", "composer-2.5",
            "claude-opus-4.8", "claude-opus-4.7", "claude-opus-4.6", "claude-opus-4.5", "claude-opus-4",
            "claude-sonnet-4.6", "claude-sonnet-4.5", "claude-sonnet-4",
            "claude-haiku-4.5", "claude-haiku-3.5",
            "gpt-4o-mini", "gpt-4o",
        ):
            if known in val_lower:
                return known
    return "composer-2.5"  # Fast is the default


# ── token / cost estimation ────────────────────────────────────────────────

def estimate_tokens(chars: int, direction: str = "input") -> int:
    ratio = _CHARS_IN if direction == "input" else _CHARS_OUT
    return max(1, int(chars * ratio))


def estimate_cost(model: str, in_toks: int, out_toks: int) -> float:
    in_r, out_r = _TOKEN_PRICE.get(model, _TOKEN_PRICE["default"])
    return (in_toks * in_r + out_toks * out_r) / 1_000_000


def from_response_text(text: str, model: Optional[str] = None) -> dict:
    """Estimate tokens/cost from raw response text (char count only)."""
    model  = model or detect_model()
    chars   = len(text) if isinstance(text, str) else len(str(text))
    in_toks  = estimate_tokens(chars, "input")
    out_toks = estimate_tokens(chars, "output")
    return {
        "input_tokens":       in_toks,
        "output_tokens":       out_toks,
        "total_tokens":        in_toks + out_toks,
        "estimated_cost_usd":  round(estimate_cost(model, in_toks, out_toks), 6),
        "chars":              chars,
    }


def from_prompt_text(text: str, model: Optional[str] = None) -> dict:
    """Estimate input tokens from a prompt string."""
    model  = model or detect_model()
    chars   = len(text) if isinstance(text, str) else len(str(text))
    in_toks = estimate_tokens(chars, "input")
    return {"input_tokens": in_toks, "prompt_chars": chars}


def from_actual_counts(input_toks: int, output_toks: int,
                        model: Optional[str] = None) -> dict:
    """Use actual token counts when available (e.g. from sessionEnd)."""
    model = model or detect_model()
    return {
        "input_tokens":       input_toks,
        "output_tokens":       output_toks,
        "total_tokens":        input_toks + output_toks,
        "estimated_cost_usd":  round(estimate_cost(model, input_toks, output_toks), 6),
        "chars":              None,
    }


# ── cumulative ───────────────────────────────────────────────────────────────

def _load_cumulative() -> dict:
    if CUMULATIVE.exists():
        try:
            with CUMULATIVE.open(encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_tokens": 0.0, "total_cost": 0.0, "records": 0, "session_id": ""}


def _save_cumulative(data: dict) -> None:
    BILLING_DIR.mkdir(parents=True, exist_ok=True)
    with CUMULATIVE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_cumulative(add_tokens: int, add_cost: float) -> dict:
    data = _load_cumulative()
    data["total_tokens"] += float(add_tokens)
    data["total_cost"]   += float(add_cost)
    data["records"]      += 1
    _save_cumulative(data)
    return {
        "total_tokens": data["total_tokens"],
        "total_cost":   data["total_cost"],
        "records":      data["records"],
    }


# ── session log ────────────────────────────────────────────────────────────

def log_session(record: dict) -> None:
    BILLING_DIR.mkdir(parents=True, exist_ok=True)
    with SESSION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_session_id() -> str:
    for var in ("CURSOR_SESSION_ID", "CURSOR_CHAT_ID"):
        sid = os.environ.get(var, "")
        if sid:
            return sid
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return hashlib.sha1(str(os.getpid()).encode()).hexdigest()[:8] + "-" + ts


# ── formatter helpers ─────────────────────────────────────────────────────

def fmt_turn(record: dict, running: dict) -> str:
    src  = record.get("source", "conv")
    turn  = record.get("turn_number", "?")
    toks  = record.get("total_tokens", 0)
    cost  = record.get("estimated_cost_usd", 0.0)
    rt    = running.get("total_tokens", 0)
    rc    = running.get("total_cost", 0.0)
    return (f"[Billing:{src}] turn-{turn} | +{toks:,}t | "
            f"cume {int(rt):,}t / ${rc:.4f} | est ${cost:.4f}")


def fmt_session_end(record: dict, running: dict) -> str:
    sid   = record.get("session_id", "?")[:12]
    toks  = record.get("total_tokens", 0)
    cost  = record.get("estimated_cost_usd", 0.0)
    turns = record.get("turn_count", 0)
    dur   = record.get("duration_ms", 0)
    return (f"[Billing:session] {sid} | {turns} turns | "
            f"{toks:,}t | ${cost:.4f} | {dur/1000:.1f}s")
