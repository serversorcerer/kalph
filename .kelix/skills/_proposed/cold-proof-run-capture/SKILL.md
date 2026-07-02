---
name: cold-proof-run-capture
description: >-
  Scaffold a minimal sample repo, run Kelix cold in an isolated worktree, and
  publish a reproducible receipt in docs/proof/. Use for REQ-VP2 value demos,
  milestone proof tasks, or ship-gate evidence capture.
---

# Cold proof run capture

Goal: a third party can rerun the demo from documented commands and get the same verify gate + verified commits.

## 1. Scaffold the sample (`samples/<name>/`)

Minimum layout:

| Path | Purpose |
|------|---------|
| `GOAL.md` | Well-specified outcome with acceptance command |
| `calc.py` + `tests/` | Tiny domain the loop can finish in N one-iteration tasks |
| `.kelix/kelix.toml` | Proof-run keys only (`[agent]`, `[loop]`, `[verify]`, `[git]`) |
| `.kelix/backlog.md` | N tasks with `status: ready` for mock runs |
| `.kelix/roadmap.md` | Pre-written milestone so plan can be skipped |
| `mockdir/001.sh` … | One mock script per backlog task |
| `run-demo.sh` | End-to-end driver (see step 2) |

Add `tests/test_<name>.py` in the monorepo: scaffold exists, sample pytest passes, `run-demo.sh` documents the promote step.

## 2. Write `run-demo.sh`

Pattern from `samples/value-demo/run-demo.sh`:

1. Resolve `KELIX_ROOT` / `KELIX_VENV` from env or parent checkout.
2. **Nested git init** if not already a repo — keeps demo isolated from monorepo root.
3. `kelix init --agent mock`
4. **Skip plan** when roadmap contains the milestone marker; else `kelix plan --goal-file GOAL.md` and document promote.
5. Echo **PROMOTE STEP**: `status: proposed` → `status: ready` before `kelix run`.
6. `kelix run --max-iterations <N+5>`

Smoke-test the script once before capturing the receipt.

## 3. Run cold for the receipt

Prefer a clean temp directory (not the monorepo root):

```bash
export KELIX_ROOT="$(pwd)"
export KELIX_VENV="$KELIX_ROOT/.venv/bin"
DEMO_TMP="$(mktemp -d /tmp/value-demo-XXXXXX)"
cp -r samples/<name>/. "$DEMO_TMP/"
cd "$DEMO_TMP"
/usr/bin/time -p bash run-demo.sh 2>&1 | tee transcript.txt
```

Record: run id, branch (`kelix/run-<run_id>`), wall clock, verify command + exit code, iteration count, commit SHAs.

## 4. Publish `docs/proof/<name>.md`

Structure (reproduction commands **first**):

1. **Reproduce** — copy-pasteable bash block for temp-dir and in-scaffold paths.
2. **Goal** — quote from `GOAL.md`.
3. **Planning interview** — when plan runs vs skipped.
4. **Promote step** — when manual promotion is required.
5. **Captured run** — metrics table (run id, adapter, iterations, wall clock, verify gate).
6. **Iteration summary** — one line per task with commit SHA.
7. **Verify receipt** — full pytest/lint output snippet.
8. **Artifact paths** — `.kelix/runs/<run_id>/`, worktree branch, `loop-metrics.json`.

## 5. Wire proof into entry points

- README first screen: value sentence + link to the receipt (before install wall).
- Add test asserting first ~30 README lines contain value sentence and receipt link.

## 6. Verify

```bash
pytest -q tests/test_<name>.py
pytest -q
ruff check src tests
```
