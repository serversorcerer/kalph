## Decisions from planning interview

- **Q1: v0.3 ship criterion** — 1 — one full self-tuning cycle is the gate: ledger from real runs, a diagnosis, a tuning PR merged/closed with recorded reason, post-merge grading; skill distillation may ship in-milestone but is not the gate
- **Q2: Phase sequencing inside v0.3** — 1 — strict waterfall: T-METRICS -> T-DIAGNOSE -> T-PROPOSE -> T-SKILLS
- **Q3: loop-metrics.json vs episodes.jsonl** — 1 — keep both: episodes.jsonl stays the raw append-only stream; loop-metrics.json is a runner-maintained rollup written at retrospective time; both gitignored
- **Q4: Token and cost metrics** — 1 — no token fields in v0.3: duration, verified rate, retry/breaker counts, lint-on-backlog findings; schema carries tokens: null plus a documented optional adapter hook
- **Q5: Lint findings on agent-written backlog edits** — 1 — after each iteration that dirties .kelix/backlog.md: lint kelix-authored proposed tasks only; store rule ids + counts on that iteration's ledger row
- **Q6: T-DIAGNOSE trigger** — 1 — new owner command kelix diagnose (--run-id / --last N); writes the diagnosis file; never auto-runs mid-loop
- **Q7: T-DIAGNOSE transcript scope** — 1 — failed iterations only from the named runs (default last 3 runs with any failure), capped by a configurable char budget
- **Q8: T-PROPOSE change surface** — 1 — Kelix-owned policy surface only: prompt templates, security denylist, config defaults, documented [memory]/[loop] toml keys; never backlog/STATE/roadmap
- **Q9: T-PROPOSE delivery mechanism** — 1 — new kelix propose command on a dedicated branch, restricted to the Q8 surface, opening a PR via existing pr.py with structured evidence body. NOTE for the Milestone V ledger (KV1): this gives pr.py a live receipt and conflicts with the predetermined SCRAP of pr.py in .kelix/phases/V-CUT/CONTEXT.md — re-judge pr.py row-by-row at ledger time; owner is aware.
- **Q10: Grading merged proposals ("homework")** — 1 — grade by comparing the last-5-runs window before merge vs next-5 after; proposal_outcomes[] in loop-metrics.json; inconclusive under 3 post-merge runs
- **Q11: T-SKILLS proposed artifact location** — 1 — .kelix/skills/_proposed/<name>/SKILL.md, excluded from the injection digest until the owner promotes by moving into .kelix/skills/<name>/
- **Q12: T-SKILLS distillation pass** — 1 — runner invokes the configured adapter after write_retrospective with a fixed distillation prompt over the run's transcripts + episode outcomes; 1-3 candidates per run
- **Q13: Skill efficacy in the ledger** — 1 — per iteration: skills_injected[] from the context manifest plus outcome; per-skill rolling verified_rate_with vs verified_rate_without over matched tasks
- **Q14: Fleet runs in the outcome ledger** — 1 — fleet runs aggregate into the same ledger with agent_id/fleet_id fields plus a fleet-level summary row at fleet completion
