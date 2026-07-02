# Phase T-METRICS — owner decisions

Captured during v0.3 planning interview (20260702). Do not re-litigate.

## Dual memory streams

Keep both episodes.jsonl and loop-metrics.json. episodes.jsonl stays the raw
append-only per-iteration stream. loop-metrics.json is a runner-maintained
rollup written at retrospective time. Both are gitignored under
`.kelix/memory/*` (only project.md is committed).

## Metrics in scope for v0.3

No token fields. Record duration_s, verified outcome, retry_count,
circuit-breaker causes, and backlog lint findings. Schema carries `tokens: null`
on every row plus a documented optional adapter hook for a future milestone.

## Backlog lint on agent edits

After each iteration that dirties `.kelix/backlog.md`, lint kelix-authored
`status: proposed` tasks only (`by: kelix`). Store rule ids and counts on that
iteration's ledger row as backlog_lint.

## Fleet aggregation

Fleet runs use the same ledger. Per-iteration rows include agent_id and
fleet_id. At fleet completion, append one fleet-level summary row to
fleet_summaries[].
