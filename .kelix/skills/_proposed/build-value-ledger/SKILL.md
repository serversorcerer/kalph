---
name: build-value-ledger
description: >-
  Create or refresh docs/value-ledger.md with evidence-first SHARPEN/KEEP/SCRAP
  verdicts per module so downstream KV tasks read binding receipts instead of
  re-litigating scope. Use for REQ-VL2 ledger tasks or milestone cut planning.
---

# Build an evidence-first value ledger

Goal: one table row per Kelix module with a **receipt** (proof of value) and a **verdict** that downstream SCRAP/KEEP tasks treat as binding.

## 1. List modules and measure LOC

Enumerate every top-level package under `src/kelix/` plus removed-but-named surfaces (sync, pr) if still in scope.

For each module, record line count:

```bash
wc -l src/kelix/<module>.py   # or directory total for packages
```

## 2. Attach a receipt per row

A receipt must cite **verified** evidence — not intent:

| Source | Example |
|--------|---------|
| Test file | `tests/test_verify.py` |
| Proof run | dogfood 12/12 verified (final-report § D1) |
| Decision log | DECISIONS.md D13 |
| Live run gap | **no live learning receipt** — note explicitly |

No receipt → verdict is **SCRAP** (delete in a named backlog task).

## 3. Assign verdicts (REQ-VL2)

| Verdict | Rule |
|---------|------|
| **SHARPEN** | Receipt exists **and** module is on the critical path of the value sentence |
| **KEEP** | Receipt exists but module is off the critical path — freeze |
| **SCRAP** | No receipt — schedule deletion |

Critical path (Kelix): init → plan (interview) → lint/spec-gate → run → verify → verified commits on run branch.

State the value sentence at the top of the doc so verdict reasoning is auditable.

## 4. Document owner veto

Add an **Owner veto** section stating:

- Edits to the ledger before execution phases are binding.
- Downstream tasks read updated rows — they do not re-litigate.
- Predetermined SCRAPs name the backlog task that will remove each surface.

## 5. Verify and ship

```bash
pytest -q
ruff check src tests
```

Commit the ledger; mark the backlog task `done`. Downstream KV2–KV5-style tasks should cite ledger rows, not reopen verdict debates.
