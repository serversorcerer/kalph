---
name: verify-receipt-output
description: >-
  Wire REQ-VS1 receipt-grade run-end output showing per-verify-command exits,
  verified commit SHAs, and claim outcomes for solo kelix run and fleet agents.
  Use when implementing or extending run-complete messaging (KV6/KV10 style).
---

# Verify receipt output (REQ-VS1)

Users must see **what** the verify gate ran, **whether** each command passed, and **which commits** were verified-done — not a opaque summary string.

## 1. Track receipt data on RunResult

In `src/kelix/loop.py`, extend `RunResult` with:

- `verified_commits: list[str]` — append each verified-done iteration SHA (dedupe consecutive duplicates)
- `last_verify_report: VerifyReport | None` — set when the verify gate runs

On verified-done, append the iteration commit SHA only when it differs from the last entry.

## 2. Solo run — themed receipt via art

Replace semicolon-separated verify summaries with `art.run_complete_receipt()`:

```python
verify_results = [
    (r.command, r.exit_code) for r in result.last_verify_report.results
] if result.last_verify_report else None

run_complete_receipt(
    run_id=result.run_id,
    status=result.status,
    iteration_count=len(result.iterations),
    verified_count=verified_count,
    verify_results=verify_results,
    verified_commits=list(result.verified_commits),
    diagnosis=result.diagnosis,
)
```

Expected lines per command:

```text
verify: python3 -c "import greet" exit 0
verified commits: abc1234, def5678
```

When nothing ran, emit `verify: none configured` and `verified commits: none`.

## 3. Fleet — per-agent receipts

In `src/kelix/fleet.py`:

1. **`_print_fleet_run_receipt`** at fleet run end — one `run_complete_receipt` block per agent, prefixed with agent id/role via `art.say`.
2. **Retrospective `### Receipt` section** per agent — markdown bullets:
   - `- verify: \`command\` exit N` for each command
   - `- verified commits: \`sha\`, ...` or `none`
   - `- claims:` with task id and done/open status

Reuse helpers that extract `[(command, exit_code)]` from `result.last_verify_report` — do not duplicate verify parsing.

## 4. Test coverage

Solo (`tests/test_loop.py` or run-complete tests):

- Assert receipt text includes per-command lines and SHAs when verify runs.

Fleet (`tests/test_fleet.py`):

- Configure `[verify] commands = ["true"]` in test config.
- Assert stdout/retrospective contains `verify:` lines and exit codes per agent.

## 5. Verify

```bash
pytest -q tests/test_fleet.py tests/test_loop.py
pytest -q
ruff check src tests
```

Document an example receipt in `docs/fleet.md` when fleet output changes.
