# Planning interview

Fill in each `answer:` line, then re-run `kelix plan` with the same goal.

Q1: v0.3 ship criterion
The sketch lists four phases (T-METRICS → T-DIAGNOSE → T-PROPOSE → T-SKILLS) but not what proves the audacity milestone landed. What is the minimum receipt to close v0.3?
1. One full self-tuning cycle on this repo: ledger populated from real runs, a diagnosis written, a tuning PR opened and owner-merged (or closed with recorded reason), and the post-merge ledger grades the prediction — skill distillation may ship in the same milestone but is not part of the gate (recommended)
2. Metrics ledger alone: T-METRICS aggregates ≥3 real runs (solo or fleet) with documented schema; diagnosis/propose/skills can follow as v0.3.1
3. Dual gate: the self-tuning cycle in (1) plus at least one runner-distilled skill promoted from `proposed` to committed with efficacy tracked in the ledger
4. Dogfood bar: Kelix runs its own v0.3 backlog to completion unattended (same proof standard as PC13 / REQ-P3)

answer: 1 — one full self-tuning cycle is the gate: ledger from real runs, a diagnosis, a tuning PR merged/closed with recorded reason, post-merge grading; skill distillation may ship in-milestone but is not the gate

Q2: Phase sequencing inside v0.3
T-METRICS is prerequisite for everything else. How should T-SKILLS relate to T-DIAGNOSE and T-PROPOSE?
1. Strict waterfall: T-METRICS → T-DIAGNOSE → T-PROPOSE → T-SKILLS (policy self-tuning proven before skill learning ships) (recommended)
2. Fork after metrics: T-DIAGNOSE/T-PROPOSE track and T-SKILLS track in parallel once T-METRICS lands (both consume the same ledger)
3. Skills first: T-METRICS → T-SKILLS → T-DIAGNOSE → T-PROPOSE (fix the zero-skills evidence before tuning prompts)
4. Single combined phase: one "T-LEARN" phase delivers metrics plumbing, distillation, diagnosis, and propose together

answer: 1 — strict waterfall: T-METRICS -> T-DIAGNOSE -> T-PROPOSE -> T-SKILLS

Q3: loop-metrics.json vs episodes.jsonl
Today `episodes.jsonl` is per-iteration, gitignored, and already feeds the digest. The sketch adds aggregated `.kelix/memory/loop-metrics.json`.
1. Keep both: episodes stay the raw append-only stream; loop-metrics.json is a runner-maintained rollup (per-run + cumulative aggregates) updated at retrospective time — also gitignored like episodes (recommended)
2. Keep both, but commit loop-metrics.json so tuning PRs can cite trend lines in git history; episodes stay gitignored
3. Replace episodes with loop-metrics as the single store (migrate digest injection to read from the rollup)
4. Keep episodes only; skip loop-metrics.json and derive aggregates on demand via a `kelix metrics` command

answer: 1 — keep both: episodes.jsonl stays the raw append-only stream; loop-metrics.json is a runner-maintained rollup written at retrospective time; both gitignored

Q4: Token and cost metrics
The sketch names tokens/duration, but adapters today only record duration and transcript bytes — no token counts from `cursor-agent` or other CLIs.
1. Ship v0.3 metrics without token fields: duration, verified rate, retry/circuit-breaker counts, lint-on-backlog findings; add `tokens: null` in schema with a documented optional adapter hook for later (recommended)
2. Estimate tokens as `len(transcript) / 4` (and same for prompt file size) — labeled `estimated_tokens` in the ledger
3. Block T-METRICS until the active adapter exposes real usage (parse cursor-agent output or require a `{usage_file}` template token)
4. Omit cost entirely from v0.3 scope; duration and verified rate are sufficient for self-tuning evidence

answer: 1 — no token fields in v0.3: duration, verified rate, retry/breaker counts, lint-on-backlog findings; schema carries tokens: null plus a documented optional adapter hook

Q5: Lint findings on agent-written backlog edits
The sketch wants lint findings on backlog edits in the ledger. When should the runner capture them?
1. After each iteration that dirties `.kelix/backlog.md`: run `kelix lint` scoped to kelix-authored `proposed` tasks only; store rule ids + counts on that iteration's ledger row (recommended)
2. Once per run at retrospective: lint the backlog diff vs run start (single summary row per run, not per iteration)
3. Only when the agent adds or edits `status: proposed` lines (skip edits to owner `ready` tasks)
4. Defer backlog lint metrics to a follow-up; core ledger is verify/retry/duration/circuit-breaker only

answer: 1 — after each iteration that dirties .kelix/backlog.md: lint kelix-authored proposed tasks only; store rule ids + counts on that iteration's ledger row

Q6: T-DIAGNOSE trigger
Diagnosis reads the ledger plus failed-iteration transcripts. What invokes it?
1. New owner command `kelix diagnose` (optional `--run-id` / `--last N`); writes `.kelix/runs/<id>/self-review.md` or `.kelix/memory/latest-diagnosis.md` — never auto-runs mid-loop (recommended)
2. Automatic after every completed run whose status is `circuit_breaker` or verified rate below a configurable threshold
3. Scheduled backlog task (`status: ready`, `by: owner`) that the loop picks like any other work — diagnosis is an iteration, not a CLI subcommand
4. Fold into retrospective: every run ends with a runner-only heuristic summary (no agent); agent-written diagnosis only when owner runs `kelix diagnose`

answer: 1 — new owner command kelix diagnose (--run-id / --last N); writes the diagnosis file; never auto-runs mid-loop

Q7: T-DIAGNOSE transcript scope
Which transcripts does the diagnosis agent read?
1. Failed iterations only from the runs named on the command line (default: last 3 runs with any failure or circuit-breaker), capped by a configurable char budget (recommended)
2. All iterations from the last N runs regardless of outcome (success transcripts included for contrast)
3. Only circuit-breaker runs — skip individual verify failures inside otherwise-completed runs
4. Owner-maintained manifest (`.kelix/memory/diagnose-targets.txt` listing run ids) — no automatic selection

answer: 1 — failed iterations only from the named runs (default last 3 runs with any failure), capped by a configurable char budget

Q8: T-PROPOSE change surface
Self-tuning PRs may touch prompt template, denylist, budgets, or selection weights. What files are in bounds for v0.3?
1. Kelix-owned policy surface only: `src/kelix/prompt.py` (DEFAULT_TEMPLATE + planning templates), `src/kelix/security.py`, `src/kelix/config.py` defaults, and documented `[memory]` / `[loop]` keys in `kelix.toml` — never `.kelix/backlog.md`, STATE, or roadmap (recommended)
2. Same as (1) plus `.kelix/kelix.toml` in the Kelix repo (project config as tuning target)
3. Narrow MVP: prompt template + `kelix.toml` `[loop]` budgets only; denylist and context weights wait
4. Broad: any file under `src/kelix/` except `gitutil.py` / adapter spawn mechanics

answer: 1 — Kelix-owned policy surface only: prompt templates, security denylist, config defaults, documented [memory]/[loop] toml keys; never backlog/STATE/roadmap

Q9: T-PROPOSE delivery mechanism
How does Kelix open the reviewable diff?
1. New `kelix propose` command: agent iteration on a dedicated branch, changes restricted to Q8 surface, opens PR via existing `pr.py` with a structured body (evidence, predicted delta, metric baseline) — same gate as code runs (recommended)
2. Reuse `kelix run` with a special owner task in backlog (e.g. `T-PROPOSE-1`) and extended prompt role; no new CLI
3. Extend `kelix plan` with a `--self-tune` mode that drafts a patch file only (no PR) for owner to apply manually
4. Runner-only proposals: deterministic small edits (budget numbers) without an agent; agent-written proposals only above a severity threshold

answer: 1 — new kelix propose command on a dedicated branch, restricted to the Q8 surface, opening a PR via existing pr.py with structured evidence body. NOTE for the Milestone V ledger (KV1): this gives pr.py a live receipt and conflicts with the predetermined SCRAP of pr.py in .kelix/phases/V-CUT/CONTEXT.md — re-judge pr.py row-by-row at ledger time; owner is aware.

Q10: Grading merged proposals ("homework")
After the owner merges a tuning PR, the ledger records whether the prediction held.
1. Compare the same metric windows before merge (last 5 runs) vs after (next 5 runs); write `proposal_outcomes[]` into loop-metrics.json with predicted vs actual — inconclusive if fewer than 3 post-merge runs (recommended)
2. Single next run only: binary pass/fail on verified rate vs prediction
3. Manual owner verdict recorded in DECISIONS.md; runner stores a pointer only
4. No automatic grading in v0.3 — prediction text in PR is informational; grading ships in v0.5 autonomous roadmapping

answer: 1 — grade by comparing the last-5-runs window before merge vs next-5 after; proposal_outcomes[] in loop-metrics.json; inconclusive under 3 post-merge runs

Q11: T-SKILLS proposed artifact location
D17 requires runner-driven distillation writing `proposed` skill artifacts the owner keeps or deletes; skills plumbing (agentskills.io format, `.kelix/skills/<name>/SKILL.md`) stays frozen.
1. Write to `.kelix/skills/_proposed/<name>/SKILL.md` (underscore prefix excluded from injection digest until promoted); promotion = move to `.kelix/skills/<name>/` on owner action (recommended)
2. Same path as committed skills but YAML frontmatter `status: proposed`; compiler skips non-active statuses
3. Separate tree `.kelix/skill-proposals/<name>/SKILL.md` (not under `skills/` at all)
4. Append proposal stubs to backlog as `status: proposed` tasks with `details:` containing the skill body — no new files until owner promotes

answer: 1 — .kelix/skills/_proposed/<name>/SKILL.md, excluded from the injection digest until the owner promotes by moving into .kelix/skills/<name>/

Q12: T-SKILLS distillation pass
The acquisition rule in the prompt never fired (~20 v0.1 iterations). The fix is a retrospective-time distillation pass over verified episodes.
1. Runner invokes the same configured adapter after `write_retrospective`, with a fixed distillation prompt over the run's transcripts + episode outcomes; writes `_proposed/` skills — bounded to 1–3 candidates per run (recommended)
2. Runner-only extraction: no agent — template-fill from rationales and verify-failure messages into SKILL.md skeletons
3. Distillation only when the run had retries or circuit-breaker (skip clean runs)
4. Owner-triggered `kelix distill --run-id` only — never automatic

answer: 1 — runner invokes the configured adapter after write_retrospective with a fixed distillation prompt over the run's transcripts + episode outcomes; 1-3 candidates per run

Q13: Skill efficacy in the ledger
The sketch ties skill injections (via context manifest) to task outcomes.
1. Per iteration: ledger records `skills_injected[]` from the context manifest plus outcome; per-skill rolling `verified_rate_with` vs `verified_rate_without` over matched tasks (lexical overlap with skill description) (recommended)
2. Binary only: log whether any skill was injected and whether the iteration verified — no per-skill breakdown in v0.3
3. Fleet-only efficacy (solo runs omitted) to reduce noise
4. Defer efficacy metrics; ship distillation + `_proposed/` workflow first, measure later

answer: 1 — per iteration: skills_injected[] from the context manifest plus outcome; per-skill rolling verified_rate_with vs verified_rate_without over matched tasks

Q14: Fleet runs in the outcome ledger
Fleet mode produces per-agent runs and a combined fleet retrospective.
1. Aggregate each agent run into the same loop-metrics ledger with an `agent_id` / `fleet_id` field; fleet-level summary row at fleet completion (recommended)
2. Solo runs only in v0.3 metrics; fleet is out of scope until v0.6 self-reviewing fleet chains
3. Separate files: `loop-metrics-solo.json` and `loop-metrics-fleet.json`
4. Fleet metrics only (dogfood is fleet-heavy) — solo runs are secondary

answer: 1 — fleet runs aggregate into the same ledger with agent_id/fleet_id fields plus a fleet-level summary row at fleet completion
