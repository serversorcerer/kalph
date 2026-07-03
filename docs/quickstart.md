# Quickstart

**6 steps to first verified commit** — from an empty repo to verified commits on a
`kelix/run-*` branch using only init, plan, and run.

Install Kelix once, then follow the numbered path. Core loop is stdlib-only Python;
`kelix init` wires a headless agent adapter (Kiro, Claude Code, Codex, Cursor,
Gemini, custom CLI, or `mock` for tests).

```bash
pipx install kelix
# until the first PyPI release lands:
# pipx install git+https://github.com/serversorcerer/kelix.git
```

## 1. Initialize

Inside a git repository:

```bash
kelix init
```

This creates `GOAL.md`, `.kelix/backlog.md`, `.kelix/memory/project.md`,
`.kelix/kelix.toml`, and empty `.kelix/skills/` and `.kelix/prompts/` directories.
Edit `.kelix/kelix.toml` now if you need to change the default agent or set
verification commands — every command under `[verify]` must exit 0 before a task
counts as done:

```toml
[verify]
commands = ["pytest -q", "ruff check ."]
```

No verify commands means no gate — fine for experimenting, not for unattended runs.

## 2. Write your goal

Edit `GOAL.md` with your outcome, non-goals, and testable acceptance bullets
(the PRD skeleton from [writing-for-the-loop.md](writing-for-the-loop.md)):

```bash
$EDITOR GOAL.md
```

Or point planning at an existing goal file with `--goal-file` in the next step.

## 3. Plan

One planning iteration drafts `.kelix/roadmap.md` and proposed backlog tasks:

```bash
kelix plan --goal-file GOAL.md
```

Review the draft roadmap and backlog. Every new task starts as `status: proposed`.
Already have a hand-written backlog? Skip this step and edit `.kelix/backlog.md`
directly — the flat-backlog path still works.

## 4. Promote tasks

Change `status: proposed` to `status: ready` for work you want the loop to pick up.
Only `ready` tasks with satisfied dependencies are candidates. Task format and
the full rubric are in [prioritization.md](prioritization.md) and
[writing-for-the-loop.md](writing-for-the-loop.md).

Example:

```text
- [ ] T1: add rate limiting to the API client | priority: 80 | status: ready | by: owner
  rationale: we are getting 429s from the upstream service in CI
  details: exponential backoff with jitter, max 5 retries, covered by a unit test
```

## 5. Run

```bash
kelix run --max-iterations 25
```

Each iteration: a fresh agent reads backlog + git log, picks the highest-priority
ready task, implements it in an isolated **worktree** on `kelix/run-<id>`, and the
runner re-runs your **verify commands**. Green: commit, record memory, next task.
Red: task stays on top. The run stops on the completion sentinel, the iteration
cap, the circuit breaker (3 consecutive failures by default), or the kill switch.

Useful flags for this step:

- `--max-iterations N` — override the config cap for this run
- `--role "text"` — extra role text injected into the prompt
- `--path DIR` — run against a repo other than the current directory
- `--force` — skip the run-time spec gate only (ready-task backlog lint);
  git safety rails (worktree isolation, command denylist) are unchanged

Kelix never pushes to `main`/`master`.

## 6. Read verified commits

Review the run branch diff and merge when ready. Every run also writes an audit
trail under `.kelix/runs/<run-id>/`:

| File | Contents |
|---|---|
| `run.json` | Machine-readable record: status, branch, and per-iteration data |
| `retrospective.md` | Human summary and a "for the owner" section |
| `iter-001.log`, … | Full transcript per iteration (secrets scrubbed) |
| `diagnosis.md` | Present only if the circuit breaker tripped |

Start with `retrospective.md`, then the diff on `kelix/run-<id>`, then individual
`iter-*.log` files for anything surprising. Each verified iteration leaves a
commit on the run branch gated by your `[verify]` commands.

## Operations

These commands stay available but are not on the init → plan → run happy path.
Use them when you need to inspect or steer an active run.

| Command | Purpose |
|---------|---------|
| `kelix lint` | Check backlog tasks against the input contract before promoting |
| `kelix status` | Show active runs, claims, and kill-switch state |
| `kelix stop` | Write `.kelix/STOP` — active runs halt before the next iteration |
| `kelix watch` | Stream a running agent's output live (`ctrl-c` detaches without stopping the run) |

## Where next

- [Concept](concept.md) — the invariants behind the design
- [Writing for the loop](writing-for-the-loop.md) — the input contract in depth
- [Planning](planning.md) — roadmap, phase gate, and waves
- [Security model](SECURITY.md) — read this before an unattended run
- [Kiro guide](kiro.md) — deepest integration: specs, steering, and hooks
