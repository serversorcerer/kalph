# Project goal

**Gold in, diamonds out.** Build a tiny stdlib-only calculator module that Kelix
can complete in five one-iteration tasks.

## Outcome

A `calc.py` module with `add`, `sub`, `mul`, `div` (zero-safe), and a small CLI
entrypoint. Every function has a pytest assertion in `tests/test_calc.py`.

## Non-goals

- No third-party dependencies, web UI, or packaging.
- No fleet, PR automation, or sync tooling.

## Acceptance

- `python3 -m pytest -q` exits 0 after all backlog tasks are verified done.
- Each operation has at least one test asserting correct behavior.
- `div(a, 0)` raises `ValueError` with a clear message.
