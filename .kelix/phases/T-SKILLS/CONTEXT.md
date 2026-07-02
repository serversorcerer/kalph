# Phase T-SKILLS — owner decisions

Captured during v0.3 planning interview (20260702). Do not re-litigate.

## Not the v0.3 ship gate

Skill distillation ships in this milestone but is not required to close v0.3.
The gate is one full self-tuning cycle (ledger → diagnose → propose → grade).

## Distillation pass

After write_retrospective, the runner invokes the configured adapter with a
fixed distillation prompt over the run's transcripts and episode outcomes.
Emit 1–3 candidate skills per run. Fix the mechanism (runner-owned pass), not
the prompt acquisition wording — D17 evidence: ~20 v0.1 iterations produced
zero skills via agent self-acquisition.

## Proposed artifact location

`.kelix/skills/_proposed/<name>/SKILL.md` — excluded from the injection digest
until the owner promotes by moving into `.kelix/skills/<name>/`. Same
agentskills.io format; plumbing frozen.

## Efficacy in the ledger

Per iteration: skills_injected[] from the context manifest skills slot plus
outcome. Per skill in the rollup: rolling verified_rate_with vs
verified_rate_without over matched tasks.
