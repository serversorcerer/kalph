---
name: fleet-drift-fix-closure
description: >-
  Close a DRIFT-FIX (or doc-only) fleet phase after copy alignment and
  test_doc_drift pass. Use for DR12-style closure — full verify gate, backlog
  completion, STATE update, and a DECISIONS evidence paragraph.
---

# Fleet drift-fix closure gate

Run this only after all copy tasks (DR1–DR10) and the regression gate (DR11)
are green. Do not mark the phase complete while `tests/test_doc_drift.py` fails.

## 1. Run the full verify gate

All three must exit 0:

```bash
env PYTHONPATH=src pytest -q
ruff check src tests
kelix lint --path .
```

Confirm the doc-drift suite explicitly:

```bash
pytest tests/test_doc_drift.py -q
```

## 2. Mark backlog tasks done

In `.kelix/backlog.md`, set every phase task (`DR*`) to `done` only if DR11
tests passed. The done count must equal the phase total (e.g. 118/118).

## 3. Update STATE.md

Set:

- `phase` → phase name + ` complete` (e.g. `DRIFT-FIX complete`)
- `last_task` → final closure task id (e.g. `DR12`)
- `done` → completed count matching backlog total
- `last_verified_commit` → hash of the closure work commit (verifier records this)

## 4. Add a DECISIONS evidence paragraph

Append one decision entry (e.g. D25) summarizing:

- Fleet run id (from branch name or STATE)
- Count of user-facing files touched across the fleet
- Confirmation that `test_doc_drift` regression gate is green

Keep it one paragraph — receipt for auditors, not a file-by-file changelog.

## 5. Commit pattern

Typical two-commit flow on the run branch:

1. **Work commit** — backlog marks, DECISIONS entry, any remaining closure edits
2. **Verified commit** — STATE.md records `last_verified_commit` after gate passes

Emit iteration rationale:

```
RATIONALE: <task-id> — <one sentence why closure is complete>
```

## 6. Exit criteria

Phase is closed when:

- All three verify commands pass
- `test_doc_drift.py` is green
- Backlog done count equals total
- STATE reflects complete phase and verified commit
- DECISIONS contains the fleet evidence paragraph
