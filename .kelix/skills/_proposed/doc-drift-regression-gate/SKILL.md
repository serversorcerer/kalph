---
name: doc-drift-regression-gate
description: >-
  Add a pure-Python pytest gate that locks user-facing copy against banned
  post-pivot phrases (PR automation, deleted flags/modules). Use after copy
  alignment tasks or when creating tests/test_doc_drift.py for a DRIFT-FIX fleet.
---

# Doc drift regression gate

Encode the post-pivot copy contract in CI so stale phrases cannot re-enter
without failing tests. Use **pure Python file reads** — do not shell out to
`rg`; CI environments may lack ripgrep.

## 1. Create tests/test_doc_drift.py

One test function per surface (minimum eight). Suggested coverage:

| Test target | Path |
|-------------|------|
| README install/safety | `README.md` |
| Quickstart happy path only | `docs/quickstart.md` (steps 1–6 section, not archive) |
| Memory + skills flow | `docs/memory-and-skills.md` |
| Fleet loop contract | `docs/fleet.md` |
| Kiro docs | `docs/kiro.md` |
| Kiro steering | `integrations/kiro/steering/kelix.md` |
| Iteration security rules | `src/kelix/prompt.py` (template section only) |
| Protection errors | `src/kelix/gitutil.py` |
| Fleet verifier role | `src/kelix/fleet.py` (`DEFAULT_ROLES` strings) |

Optionally add focused tests in `tests/test_value_demo.py` for README
install/quickstart/SECURITY acceptance from individual DR tasks before the
unified gate lands.

## 2. Banned phrase list

Assert **case-insensitive** absence of:

- `open pr`
- `land as pr`
- `opens pr`
- `kelix sync`
- `from kelix.pr`
- `test_pr.py` (as current/live coverage — historical footnotes in DECISIONS
  are out of gate scope)

For `--pr`, use a regex with word boundary so innocent flags like
`--proposal-id` do not false-positive:

```python
import re

_PR_FLAG = re.compile(r"--pr\b", re.IGNORECASE)

def assert_no_banned(text: str, *, allow_pr_guardrail: bool = False) -> None:
    lower = text.lower()
    for phrase in ("open pr", "land as pr", "opens pr", "kelix sync", "from kelix.pr"):
        assert phrase not in lower, f"banned phrase {phrase!r} found"
    assert not _PR_FLAG.search(text), "banned --pr flag reference found"
```

## 3. Scoped reads, not whole-repo grep

Read each path explicitly. Do not scan `.kelix/backlog.md`, phase interview
artifacts, or archive sections — those intentionally retain historical language.

For `docs/quickstart.md`, limit assertions to the happy-path section (e.g. first
N lines or a marked heading range) so archived steps do not fail the gate.

For `src/kelix/prompt.py`, extract only the iteration template / security-rules
block rather than the entire module if other sections mention PRs in comments.

## 4. Allow intentional guardrails

When a file legitimately keeps PR language (e.g. SECURITY.md Will-not:
"merge its own PRs" as an agent guardrail), either:

- Exclude that subsection from the scan, or
- Pass `allow_pr_guardrail=True` and assert only product-promise phrases
  (`opens pr`, `land as pr`, `--pr`) are absent.

## 5. Verify

```bash
pytest tests/test_doc_drift.py -q
env PYTHONPATH=src pytest -q
ruff check src tests
```

Gate is green only when all doc-drift tests pass alongside the full suite.
