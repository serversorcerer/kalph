# Phase T-DIAGNOSE — owner decisions

Captured during v0.3 planning interview (20260702). Do not re-litigate.

## Trigger

New owner command `kelix diagnose` (--run-id / --last N). Writes the diagnosis
file. Never auto-runs mid-loop — the runner must not invoke diagnose from
kelix run or fleet completion hooks.

## Transcript scope

Failed iterations only from the named runs. Default: last 3 runs with any
failure in the ledger. Total transcript chars capped by a configurable budget
(`[loop] diagnose_transcript_chars` in kelix.toml).

## Deliverable

One adapter iteration produces a markdown diagnosis under `.kelix/memory/`
correlating prompt sections, policies, and config budgets with failure modes,
citing run_id and iteration indices from the ledger.
