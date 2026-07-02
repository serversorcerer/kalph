---
name: value-ledger-surface-audit
description: >-
  Align CLI help, docs index, and quickstart with docs/value-ledger.md verdicts
  (SHARPEN happy path, KEEP secondary, SCRAP absent). Use for V-SIMPLE audits,
  value-cut tasks, or when user-facing surfaces drift from the ledger.
---

# Value ledger surface audit

Goal: every user-facing entry point reflects the ledger — init/plan/run first, secondary ops labeled, SCRAP surfaces gone.

## 1. Read the ledger

Open `docs/value-ledger.md` and classify each row:

| Verdict | Surface treatment |
|---------|-------------------|
| **SHARPEN** | Happy path — lead with it, no caveats |
| **KEEP** | Document below the fold or in an Operations section; mark `(secondary)` in CLI help |
| **SCRAP** | Must not appear in happy-path docs or `--help` |

Note executed SCRAP tasks (e.g. KV2 sync/, KV3 pr) so grep targets are explicit.

## 2. Audit CLI (`src/kelix/cli.py`)

- Order subcommands: `init`, `plan`, `run` before secondary ops.
- Append `(secondary)` to help text for `lint`, `status`, `stop`.
- Confirm SCRAP subcommands and flags are removed (no `sync`, no `--pr`).

Add or extend `tests/test_cli_audit.py`:

```python
HAPPY_PATH_SUBCOMMANDS = ("init", "plan", "run")
SECONDARY_SUBCOMMANDS = ("lint", "status", "stop")
SCRAPPED_SUBCOMMANDS = ("sync",)

# Capture --help via kelix.cli.main(["--help"])
# Assert happy path present, scrapped absent, (secondary) in help,
# init < plan < run in help text order
# rg src/kelix/cli.py for scrapped symbols — expect no matches
```

## 3. Audit docs index (`docs/index.md`)

- **Above the fold:** five intent routes tied to "ship unattended" (quickstart, writing contract, concept, security, proof receipt).
- **Below the fold:** agents, more guides, reference — deduplicate anything already in Start here.
- **Footer:** state that every linked page maps to SHARPEN or KEEP in `docs/value-ledger.md`; note SCRAP surfaces removed.

## 4. Audit quickstart (`docs/quickstart.md`)

- Header: numbered happy path only (e.g. "6 steps to first verified commit").
- Steps: init → goal → plan → promote → run → read verified commits.
- **Operations section:** secondary commands (`lint`, `status`, `stop`, `watch`) — never mixed into numbered steps.
- Grep happy-path section for SCRAP references (`--pr`, `sync`, fleet if deferred) — expect zero hits.

## 5. Verify

```bash
pytest -q tests/test_cli_audit.py
pytest -q
ruff check src tests
rg -i 'sync|--pr' docs/quickstart.md docs/index.md   # expect no SCRAP refs in happy path
```
