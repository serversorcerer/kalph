---
name: execute-self-tuning-ship-gate
description: >-
  Run the verified self-tuning ship gate (metrics seed → diagnose → propose →
  record merge → post-merge grade → evidence consolidation). Use when executing
  ST19-style subtasks or proving REQ-TP2/REQ-TP3 end-to-end.
---

# Execute the self-tuning ship gate

Procedures verified in ST19a–ST19e. Invoke kelix with `PYTHONPATH=src` and `$KELIX_VENV/kelix` or `python -m kelix.cli` — not `python -m kelix`.

## Step 1 — Seed metrics (a)

1. Create a proof mock adapter under gitignored `.kelix/<gate>-mock/` (see ship-gate-mock-config skill if needed).
2. Set `[memory] distill_skills=false` for the seed run so distillation does not consume the iteration budget.
3. **Block the seed subtask** in the backlog before running `kelix run --max-iterations 3`. Otherwise `select_next` keeps picking the seed task and the run never advances other work.
4. Run the seed; confirm ≥3 verified `IterationLedgerRow` entries in `.kelix/memory/loop-metrics.json`.
5. Record the run id, row count, and metrics summary in `DECISIONS.md` (pending section) and optional `docs/proof/<gate>-seed.txt`.
6. Unblock/mark the seed subtask done after verification.

## Step 2 — Diagnose (b)

1. Run `kelix diagnose --run-id <seed-run-id>` with mock adapter (diagnose mock config: `isolation=none`).
2. Confirm output at `.kelix/memory/diagnosis-<task>.md` contains `## Findings` citing the seed run.
3. Append diagnosis path to `DECISIONS.md` pending evidence.

## Step 3 — Propose (c)

1. Run `kelix propose --no-pr --diagnosis-file .kelix/memory/diagnosis-<task>.md` with mock adapter.
2. Keep default `[git] isolation=worktree` — do not set `isolation=none` for propose.
3. Confirm: proposal id, branch `kelix/propose-<id>`, sidecar `.kelix/memory/proposal-<id>.json`, and `validate_propose_diff` clean (typically only `.kelix/prompts/iteration.md`).
4. Capture `PREDICTED_IMPROVEMENT:` text for later grading; record proposal id and merge SHA in `DECISIONS.md`.

## Step 4 — Record merge (d)

1. Run `kelix propose --record-merge <merge-sha> --proposal-id <proposal-id>`.
2. Verify `loop-metrics.json` has a `proposal_outcomes[]` entry (grade may be `inconclusive` until post-merge runs exist).
3. Document in `DECISIONS.md`; note that `loop-metrics.json` is gitignored — tracked evidence lives in DECISIONS and proof files.

## Step 5 — Post-merge grade (e)

1. Apply merged policy to the working tree (e.g. checkout `.kelix/prompts/iteration.md` from merge SHA).
2. Run a **new** `kelix run --max-iterations 3` with a distinct mock dir; capture a new run id (must differ from seed run).
3. Run `kelix metrics grade-proposal --proposal-id <id>`. Grading needs ≥3 distinct post-merge run ids for `improved`/`regressed`; fewer yields `inconclusive` — that is acceptable for gate proof if documented.
4. Record post-merge run id, grade, and proof lines in `DECISIONS.md` / `docs/proof/<gate>-postmerge.txt`.

## Step 6 — Consolidate (parent)

1. Merge the `## D22 execution evidence (pending)` (or equivalent) section into the permanent decision entry in `DECISIONS.md`.
2. Cite the full trail: seed run id → diagnosis path → proposal id / merge SHA → post-merge run id → grade.
3. Mark parent task done after `kelix lint`, `pytest -q`, and `ruff check src tests` pass.

## Evidence rule

Because `loop-metrics.json`, diagnosis files, and proposal sidecars are gitignored, every step must leave **git-tracked** pointers (DECISIONS.md, `docs/proof/*.txt`) so a fresh iteration can continue the chain without the local metrics file.
