---
name: execute-value-ledger-verdict
description: >-
  Execute a backlog task that implements a value-ledger row verdict (SCRAP or
  KEEP) without re-litigating scope. Use for KV2–KV5-style tasks when
  docs/value-ledger.md already binds the module verdict and receipt.
---

# Execute a value-ledger verdict

The ledger in `docs/value-ledger.md` is binding for downstream execution tasks.
Read the target module row **first**; do not re-debate SHARPEN/KEEP/SCRAP.

## 1. Read the binding row

Locate the module in the ledger table. Note:

- **Verdict** — SCRAP or KEEP (SHARPEN tasks are separate)
- **Receipt** column — tests, proof docs, or DECISIONS citations
- **Owner veto** section — predetermined SCRAPs are already documented

If the row was edited since the task was written, the committed ledger wins.

## 2. Branch on verdict

### KEEP — no deletion (KV4/KV5 pattern)

When the row is **KEEP** with a cited receipt:

1. Do **not** delete code, tests, or docs for that module.
2. Run standard verification (`pytest -q`, `ruff check src tests`).
3. Mark the backlog task `done` and update STATE.
4. Commit a no-op record that **quotes the ledger row** (module name, verdict, receipt path).
5. Emit `RATIONALE: <task-id> — <ledger row is KEEP with receipt; no deletion required>.`

A KEEP task is complete when verification passes and the commit cites the ledger — not when files are removed.

### SCRAP — remove unverified surface (KV2/KV3 pattern)

When the row is **SCRAP** (no live receipt):

1. **Delete** the module directory, CLI subcommands, and config types tied to it.
2. **Migrate retained behavior** before deleting — e.g. move `sanitize_inbound` from a scrapped sync package into `security.py` when security tests still need it.
3. **Retarget tests** — delete module-specific tests; add coverage for migrated code in the owning module's test file.
4. **Sweep references** — README, CONTRIBUTING, SECURITY, integrations, phase CONTEXT, and the ledger row itself.
5. **Acceptance grep** — confirm zero matches for the removed surface in `src`, `tests`, and `docs` (use precise patterns like `\b--pr\b` for flags, not broad strings).
6. Run `pytest -q` and `ruff check src tests`.
7. Update the ledger row to `SCRAP (done **KVn**)` and mark backlog `done`.

## 3. Verify and close

```bash
pytest -q
ruff check src tests
# SCRAP only: acceptance grep must return zero matches
```

Mark the backlog task `done` **before exiting** — leaving a verified task at `ready` inflates `retry_count`.

Commit all work and emit `RATIONALE: <task-id> — <one sentence>`.
