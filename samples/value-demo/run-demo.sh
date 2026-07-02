#!/usr/bin/env bash
# Value demo — cold run from scaffold to verified commits (mock adapter).
#
# Reproduces init → (optional plan) → promote note → kelix run for KV16
# transcript capture. Uses a nested git repo so the demo stays isolated from
# the Kelix monorepo checkout.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

KELIX_ROOT="${KELIX_ROOT:-$(cd "$ROOT/../.." && pwd)}"
KELIX_VENV_BIN="${KELIX_VENV:-$KELIX_ROOT/.venv/bin}"
KELIX_CMD="${KELIX_CMD:-$KELIX_VENV_BIN/kelix}"
export PYTHONPATH="${KELIX_ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export PATH="${KELIX_VENV_BIN}:$PATH"

if [ ! -x "$KELIX_CMD" ]; then
  echo "error: kelix CLI not found at $KELIX_CMD (pip install -e . from Kelix root)" >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init -q -b main
  git config user.email "value-demo@kelix.dev"
  git config user.name "Kelix Value Demo"
  git add -A
  git commit -q -m "value demo scaffold"
fi

"$KELIX_CMD" init --agent mock

if ! grep -q 'Milestone M1' .kelix/roadmap.md 2>/dev/null; then
  "$KELIX_CMD" plan --goal-file GOAL.md
  echo ""
  echo "=== PROMOTE STEP (required before kelix run) ==="
  echo "Review .kelix/backlog.md and change status: proposed to status: ready"
  echo "for each task you want the loop to pick up."
  if [ -t 0 ]; then
    read -r -p "Press Enter after promoting tasks..."
  else
    echo "Non-interactive: promote tasks manually, then re-run kelix run."
    exit 0
  fi
else
  echo "Roadmap present — skipping kelix plan."
  echo ""
  echo "=== PROMOTE STEP ==="
  echo "This scaffold ships with status: ready tasks (mock demo needs no edits)."
  echo "For a live agent run after kelix plan, promote proposed tasks in"
  echo ".kelix/backlog.md from status: proposed to status: ready before run."
fi

"$KELIX_CMD" run --max-iterations 10
