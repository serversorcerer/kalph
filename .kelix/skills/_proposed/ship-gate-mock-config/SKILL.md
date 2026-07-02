---
name: ship-gate-mock-config
description: >-
  Configure mock adapters and kelix.toml overrides for ship-gate proof steps
  (run, diagnose, propose) inside a worktree. Use when executing ST19-style
  subtasks without calling a real agent CLI.
---

# Ship-gate mock adapter configuration

Proof mocks live under gitignored `.kelix/<step>-mock/` (e.g. `.kelix/st19b-mock/`). Temporarily edit root `.kelix/kelix.toml`; **restore** after each subcommand so mock config is never committed.

## Shared rules

- Never run `pip install -e .` in a worktree; use `PYTHONPATH=src`.
- Mock dirs are gitignored — safe for iteration scripts that echo fixed agent output.
- Pre-iteration checkpoints capture config; avoid committing `[agent] adapter=mock` overrides.

## Per subcommand

### `kelix run` (metrics seed)

```toml
[agent]
adapter = "mock"
mock_dir = ".kelix/<gate>a-mock"

[memory]
distill_skills = false
```

- Use default `[git] isolation=worktree`.
- Block the seed backlog task during the run so another ready task is selected (see execute-self-tuning-ship-gate).

### `kelix diagnose`

```toml
[agent]
adapter = "mock"
mock_dir = ".kelix/<gate>b-mock"

[git]
isolation = "none"
```

- **`isolation=none` is required** so diagnose reads/writes `.kelix/memory/` in the current worktree root.
- Mock script should emit a diagnosis with `## Findings` and cite the target `--run-id`.
- Output path `.kelix/memory/diagnosis-*.md` is gitignored; record the path in `DECISIONS.md`.

### `kelix propose`

```toml
[agent]
adapter = "mock"
mock_dir = ".kelix/<gate>c-mock"
```

- **Keep default `[git] isolation=worktree`** — do not set `isolation=none`.
- Policy edits land on branch `kelix/propose-<id>` inside `.kelix/worktrees/<id>/`.
- Only override `[agent]` locally; restoring tom prevents mock config from entering the pre-propose checkpoint commit.
- Mock script must print `PREDICTED_IMPROVEMENT:` and touch only allowlisted paths (typically `.kelix/prompts/iteration.md`).

### Post-merge `kelix run` (grade step)

```toml
[agent]
adapter = "mock"
mock_dir = ".kelix/<gate>e-mock"

[memory]
distill_skills = false
```

- Apply merged prompt/policy to the tree **before** the run.
- Use a **new** mock dir and run id so grading windows distinguish pre- vs post-merge metrics.

## Restore checklist

After each proof subcommand:

1. Revert `.kelix/kelix.toml` to pre-proof values (or remove mock overrides).
2. Confirm `git diff .kelix/kelix.toml` is clean before committing task work.
3. Run project verification (`pytest -q`, `ruff check src tests`).
