---
name: decompose-multi-run-ship-gate
description: >-
  Decompose an owner ship-gate task that needs multiple kelix runs plus owner
  merge/grade steps into one-iteration backlog subtasks. Use when the loop
  contract says the task is too large for one iteration but must still close
  as a single gate (e.g. ledger → diagnose → propose → grade).
---

# Decompose a multi-run ship gate

When a ship-gate task spans several kelix runs **and** owner-only steps (merge, record outcome, grade), do **not** implement it in one iteration. Decompose, commit, and stop.

## When to apply

- Acceptance requires `kelix run`, `kelix diagnose`, `kelix propose`, and/or owner merge/grade commands — each is its own run or manual step.
- A single iteration cannot both seed metrics and diagnose/propose without violating one-task scope.

## Steps

1. **Keep the parent task** for final consolidation only (evidence rollup, DECISIONS.md entry, REQ citation). Add `deps:` on the last subtask.

2. **Add lettered subtasks** (e.g. `ST19a`–`ST19e`), each:
   - One iteration-sized deliverable with concrete acceptance (command, file path, or row count).
   - Chained `deps:` in execution order.
   - Descending priority so the earliest step sorts first among ready tasks.

3. **Standard five-step chain** (adjust names/ids to your gate):

   | Step | Purpose | Typical acceptance |
   |------|---------|-------------------|
   | a | Seed metrics | `kelix run --max-iterations 3` → ≥3 rows in `loop-metrics.json` |
   | b | Diagnose | `kelix diagnose --run-id <seed>` → `.kelix/memory/diagnosis-*.md` with `## Findings` |
   | c | Propose | `kelix propose --no-pr --diagnosis-file …` → sidecar + allowlisted diff |
   | d | Record outcome | `kelix propose --record-merge <sha> --proposal-id <id>` |
   | e | Post-merge grade | Apply merged policy, post-merge run, `kelix metrics grade-proposal` |
   | parent | Consolidate | Merge execution evidence into `DECISIONS.md` |

4. **Update STATE.md** `current_task` to the first ready subtask and bump `total`.

5. **Verify** backlog lint (`kelix lint`), tests, and ruff; commit with the parent task id in the message; **do not** start subtask work in the decomposition iteration.

## Do not

- Fold two runs or merge+grade into one subtask — each subcommand boundary is a natural iteration cut.
- Remove the parent task; it holds the gate-closure rollup once all subtasks are done.
