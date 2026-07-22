#!/bin/bash
# Quick start script for AIDocxWorkFlow
cd "$(dirname "$0")"

# Check if CURSOR_API_KEY is set
if [ -z "$CURSOR_API_KEY" ]; then
    echo "[ERROR] CURSOR_API_KEY is not set."
    echo "Please set it first: export CURSOR_API_KEY='cursor_...'"
    exit 1
fi

# Activate virtual environment and run
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv .venv
fi

.venv/bin/pip install -q -r requirements.txt
.venv/bin/python run_workflow.py --full --input sample_requirements.md --version v1.2
