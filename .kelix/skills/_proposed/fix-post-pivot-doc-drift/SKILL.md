---
name: fix-post-pivot-doc-drift
description: >-
  Align user-facing docs and prompt strings after a Kelix workflow pivot (e.g.
  KV3 removed PR automation). Use when a DRIFT-FIX fleet, milestone retire/replace
  table, or grep finds stale claims in README, docs/, src/kelix prompts, or
  integration steering files.
---

# Fix post-pivot doc drift

When a shipped workflow changes, stale copy often survives in docs and embedded
prompt strings. Fix copy **before** adding regression tests — tests encode the
target state.

## 1. Apply the binding retire/replace table

Read `.kelix/phases/<phase>/CONTEXT.md` (or the milestone decision) for the
canonical mapping. Typical KV3-style replacements:

| Retire | Replace with |
|--------|----------------|
| "open PRs" / "opens PRs" / "land as PRs" | **verified commits on a `kelix/run-*` branch**; **owner merges** when satisfied |
| "`kelix run --pr`" | remove — flag deleted |
| "`kelix sync`" | remove — module deleted |
| `test_pr.py` as live evidence | historical footnote only — file deleted |

Frame run branches as the **auditable happy path** (receipts the owner reviews),
not as "we removed a feature."

## 2. Respect scope boundaries

**In scope:** README, `docs/**`, `integrations/**/steering/*`, `DECISIONS.md`,
`CHANGELOG.md`, iteration prompt template (`src/kelix/prompt.py`), protection
errors (`src/kelix/gitutil.py`), fleet role strings (`src/kelix/fleet.py`).

**Out of scope:** `.kelix/backlog.md` archive lines, `.kelix/phases/*` interview
artifacts, `PLAN.md` archive checkboxes, `docs/value-ledger.md` SCRAP rows.
Do not rewrite historical backlog entries.

## 3. Touch surfaces by role (parallel-friendly)

| Bucket | Typical files |
|--------|---------------|
| Entry + safety | `README.md` Safety / Will / Will-not; `docs/SECURITY.md`, `docs/quickstart.md` |
| Operator docs | `docs/memory-and-skills.md`, `docs/fleet.md`, `docs/kiro.md` |
| Integration steering | `integrations/kiro/steering/kelix.md` |
| Runtime strings | `src/kelix/prompt.py` security rules, `gitutil.py` errors, `fleet.py` verifier role |
| Honesty labels | `docs/proof/value-demo.md` (**Mock adapter** + live proof link), `CHANGELOG.md` footnotes |
| Historical decisions | `DECISIONS.md` — keep narrative, add pivot footnote (e.g. "SCRAP'd KV3") |

## 4. Distinguish guardrails from drift

Not every PR mention is stale. **Will-not** guardrails that tell agents "never
merge its own PRs" may stay when framed as agent-behavior limits, not product
promises. Retire copy that **promises** Kelix opens PRs or lands work as PRs.

## 5. Verify copy before regression tests

Per file or task, grep for banned phrases:

```bash
rg -i 'open pr|land as pr|opens pr|--pr|kelix sync|from kelix\.pr|test_pr\.py' \
  README.md docs/ src/kelix/prompt.py src/kelix/gitutil.py src/kelix/fleet.py
```

If a doc is already clean (no false edits), skip prose changes and proceed to
the regression gate — see **doc-drift-regression-gate** skill.

Doc-only tasks still run the full suite:

```bash
env PYTHONPATH=src pytest -q
ruff check src tests
```

## 6. Hand off to gate skills

After DR1–DR10 copy tasks pass grep: add `tests/test_doc_drift.py` (DR11), then
run the fleet closure gate (DR12) per **fleet-drift-fix-closure** skill.
