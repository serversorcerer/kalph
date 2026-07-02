# Phase T-PROPOSE — owner decisions

Captured during v0.3 planning interview (20260702). Do not re-litigate.

## Change surface (Kelix-owned policy only)

`kelix propose` may edit: prompt templates (`.kelix/prompts/`), security
denylist defaults and `[security].deny_extra`, config default values and
documented `[memory]` / `[loop]` keys in the shipped kelix.toml template.
Never backlog.md, STATE.md, or roadmap.md.

## Delivery

Dedicated branch (`kelix/propose-<id>`), one adapter iteration, PR opened via
existing pr.py with structured evidence body (metrics, optional diagnosis ref,
predicted improvement). Owner merges or closes — same gate as any code change.

## pr.py vs Milestone V SCRAP

This phase gives pr.py a live receipt for tuning PRs. At Milestone V ledger
time (KV1), re-judge the pr.py row row-by-row — it conflicts with the
predetermined SCRAP in `.kelix/phases/V-CUT/CONTEXT.md`. Owner is aware.

## Grading merged proposals ("homework")

Record each outcome in proposal_outcomes[] in loop-metrics.json. Grade by
comparing verified rate and retry/breaker counts in the last-5-runs window
before merge vs the next-5 after. Mark inconclusive when fewer than 3
post-merge runs exist.
