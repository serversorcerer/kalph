# Value demo sample — stdlib calculator for Kelix proof runs (REQ-VP1).

Minimal toy project with five one-iteration backlog tasks, mock adapter scripts,
and `run-demo.sh` for cold reproduction.

## Quick check

```bash
cd samples/value-demo
python3 -m pytest -q
```

## Full demo

```bash
cd samples/value-demo
./run-demo.sh
```

The script initializes a nested git repo (if needed), runs `kelix init`, skips
`kelix plan` when `.kelix/roadmap.md` already exists, documents the promote
step, then runs `kelix run --max-iterations 10` with the mock adapter.
