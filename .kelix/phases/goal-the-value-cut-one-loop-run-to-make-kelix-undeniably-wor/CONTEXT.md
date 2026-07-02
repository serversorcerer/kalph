## Decisions from planning interview

- **Q1: Roadmap supersession** — Finish all open tasks first: complete v0.2 (PC7-PC23) before starting any V-* phase. Then verify what is working incredibly, cut the fluff, and simplify to the best working version possible. V-* is the final milestone, sequenced after the existing backlog.
- **Q2: D16 freeze vs no-receipt scrap** — 1 — the ledger decides row-by-row with owner veto in docs/value-ledger.md before execution; D16 is input, not an override
- **Q3: sync/ and pr.py disposition** — 1 — SCRAP both: delete sync/, pr.py, kelix sync, and --pr; the value demo stops at verified commits on a run branch
- **Q4: Fleet mode** — 3 — SHARPEN fleet: keep it and improve its user-facing receipts (run-complete messaging, docs) within V-SHARPEN; it has real proof (zero claim collisions) and is part of Kelix's value story
- **Q5: CLI commands beyond init/plan/run** — 1 — happy path is init/plan/run only; lint, status, stop stay as documented secondary ops, out of quickstart
- **Q6: Milestones v0.3 and v0.4 after the value cut** — Run through both v0.3 and v0.4 milestones first, then move into the value cut: inspect what is working best, enhance and focus on those, remove the fluff and dead weight. Quality over quantity. Sequencing: v0.2 -> v0.3 -> v0.4 -> V-* (value cut ships the release).
- **Q7: Value demo repository** — Planner's judgment with the evidence provided: use a new minimal fresh sample repo (stdlib toy project, 3-5 tasks, no fleet/pr/sync side quests) — clean evidence beats reused evidence, and tasklite receipts already exist for v0.1; the value demo should prove the current version cold.
