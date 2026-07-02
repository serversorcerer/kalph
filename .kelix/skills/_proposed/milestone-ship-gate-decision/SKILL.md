---
name: milestone-ship-gate-decision
description: >-
  Close a Kelix milestone by adding a DECISIONS.md entry that bundles proof
  receipt, ledger counts, and release-gate command results. Use when the last
  backlog task in a phase gate is done or when declaring KELIX COMPLETE.
---

# Milestone ship gate decision

Goal: the milestone closes with auditable evidence in `DECISIONS.md`, not just a green backlog count.

## 1. Confirm gate preconditions

Before writing the decision:

- [ ] All milestone backlog tasks are `status: done` (no `ready` tasks left — leaving one inflates `retry_count` on the next run).
- [ ] Phase requirements covered (grep backlog/STATE for the milestone REQ ids).
- [ ] Proof receipt exists in `docs/proof/` with reproduction commands (see `cold-proof-run-capture` skill if missing).

If backlog is complete but a prior iteration already verified the closing task, emit a clean-close rationale and `KELIX COMPLETE` — do not re-implement work.

## 2. Run the release gate

All must exit 0; capture outputs for the decision entry:

```bash
kelix lint
pytest -q
ruff check src tests
```

Optional: re-run the proof receipt's reproduce block to confirm cold reproducibility.

## 3. Tally ledger verdicts

From `docs/value-ledger.md`, count rows by verdict:

```
N SHARPEN / N KEEP / N SCRAP
```

Note which SCRAP rows were executed (with task ids) and any KEEP rows that survived row-by-row judgment.

## 4. Add D* entry to `DECISIONS.md`

Append a bullet following the D24 pattern:

```markdown
- D<N> (<Milestone name> — <phase> ship gate, <REQ-id>): <task-range> complete.
  **Value demo:** run `<run_id>` on `samples/<name>/` (<adapter>, N/N verified,
  <wall>s wall clock); full receipt in `docs/proof/<name>.md` (transcript,
  verify exit 0, commit SHAs on branch `kelix/run-<run_id>`).
  **Ledger final verdicts** (N rows in `docs/value-ledger.md`): N SHARPEN,
  N KEEP, N SCRAP — SCRAP rows executed (<task ids>); <notable KEEP decisions>.
  **Release gate:** <surface checks, e.g. README value sentence + demo link>;
  `kelix lint`, `pytest -q`, and `ruff check src tests` exit 0 post-cut.
  Milestone <name> closes; no further <prefix>-* backlog tasks remain.
```

Use the next available D number; cite real run ids and SHAs from the receipt — do not placeholder.

## 5. Update tracking files

- Mark the closing backlog task `done` in `.kelix/backlog.md`.
- Advance `.kelix/STATE.md`: `last_task`, `done`/`total` counts, phase if applicable.
- Commit task work and STATE record as separate commits (match existing Kelix iteration convention).

## 6. Verify and exit

```bash
pytest -q && ruff check src tests && kelix lint
```

Emit:

```
RATIONALE: <task-id> — <one sentence summarizing the gate closure>.
```

If no ready tasks remain and gate is satisfied, append `KELIX COMPLETE`.
