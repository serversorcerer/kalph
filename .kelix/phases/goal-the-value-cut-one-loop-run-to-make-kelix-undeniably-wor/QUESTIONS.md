# Planning interview

Fill in each `answer:` line, then re-run `kelix plan` with the same goal.

Q1: Roadmap supersession
v0.2 is 10/24 tasks done (STATE.md: phase P-GATE, next PC7). This goal introduces V-LEDGER / V-SHARPEN / V-SIMPLE / V-PROOF. What happens to the pending v0.2 backlog (PC7–PC23) and the proposed v0.4 KE1–KE32 backlog?
1. Replace now: V-* phases become the active roadmap; cancel or archive all pending PC7+ and KE* tasks (recommended)
2. Finish v0.2 first (PC7 through PC13 at minimum), then run the value cut as a follow-on milestone
3. Hybrid: finish P-GATE + P-HARDEN only (trust/path items), drop P-CONTEXT / P-WAVES / P-PROOF remainder, then pivot to V-*

answer: Finish all open tasks first: complete v0.2 (PC7-PC23) before starting any V-* phase. Then verify what is working incredibly, cut the fluff, and simplify to the best working version possible. V-* is the final milestone, sequenced after the existing backlog.

Q2: D16 freeze vs no-receipt scrap
D16 froze MCP/skills plumbing (keep working, zero new investment). The value-cut goal lists mcp_server and skills plumbing as SCRAP candidates (no proof receipt). Which rule wins when the ledger is drafted?
1. Ledger decides row-by-row with owner veto in docs/value-ledger.md before execution — D16 is input, not an override (recommended)
2. Honor D16: MCP and skills plumbing are KEEP (frozen); they cannot receive SCRAP in this milestone
3. Value-cut wins: scrap anything without a receipt, including mcp_server and skills selection plumbing

answer: 1 — the ledger decides row-by-row with owner veto in docs/value-ledger.md before execution; D16 is input, not an override

Q3: sync/ and pr.py disposition
sync/ ran only against mocked transport (docs/proof/final-report.md line 130); pr.py / --pr ran only against stubbed gh (dogfood used local merge branches per D12). For the value sentence "verified commits," what is the verdict?
1. SCRAP both: delete sync/, pr.py, kelix sync, and --pr; the value demo stops at verified commits on a run branch (recommended)
2. SCRAP sync/ only; KEEP --pr as an optional advanced command off the quickstart
3. KEEP both frozen (tests stay, no quickstart mention) until a live receipt exists

answer: 1 — SCRAP both: delete sync/, pr.py, kelix sync, and --pr; the value demo stops at verified commits on a run branch

Q4: Fleet mode
Fleet has real proof (docs/proof/fleet-session*.md, zero claim collisions) but sits off the init → plan → run critical path. Verdict?
1. KEEP frozen: code and tests stay; fleet drops out of quickstart and README hero path (recommended)
2. SCRAP: delete kelix fleet, fleet.py, claims coordination, and fleet docs in this milestone
3. SHARPEN: keep fleet and improve its user-facing receipts (run-complete messaging, docs) within V-SHARPEN

answer: 3 — SHARPEN fleet: keep it and improve its user-facing receipts (run-complete messaging, docs) within V-SHARPEN; it has real proof (zero claim collisions) and is part of Kelix's value story

Q5: CLI commands beyond init/plan/run
The goal targets three commands for a stranger's first verified commit. What about lint, status, stop, and any aux commands that survive the ledger?
1. Happy path is init / plan / run only; keep lint, status, and stop as documented secondary ops (CI, phase gate, kill switch), not in quickstart (recommended)
2. Strict surface: delete every CLI subcommand outside {init, plan, run} unless a KEEP ledger row explicitly requires it
3. Keep the current full CLI; simplify docs only (index routes by intent, commands unchanged)

answer: 1 — happy path is init/plan/run only; lint, status, stop stay as documented secondary ops, out of quickstart

Q6: Milestones v0.3 and v0.4 after the value cut
The roadmap still sketches v0.3 self-tuning loop (metrics, skill learning per D17) and v0.4 agent-agnostic reposition (KE backlog from the prior plan interview). After V-PROOF ships, what happens to them?
1. Remove both from the active roadmap until post-release; re-plan v0.3+ with kelix plan after the value demo lands (recommended)
2. Keep v0.4 KE backlog proposed but blocked until V-PROOF completes; drop v0.3 self-tuning entirely
3. Keep both milestones visible as frozen sketches; execute only V-* tasks now

answer: Run through both v0.3 and v0.4 milestones first, then move into the value cut: inspect what is working best, enhance and focus on those, remove the fluff and dead weight. Quality over quantity. Sequencing: v0.2 -> v0.3 -> v0.4 -> V-* (value cut ships the release).

Q7: Value demo repository
V-PROOF requires one fresh scripted run on a clean sample repo with a captured transcript (docs/proof/value-demo.md). Which repo?
1. New minimal fresh sample (stdlib toy project, ~3–5 tasks, no fleet / pr / sync side quests) (recommended)
2. Reuse tasklite from dogfood (known 12/12 proof, faster setup but reuses prior evidence)
3. Self-host on the Kelix repo itself (meta demo, highest noise)

answer: Planner's judgment with the evidence provided: use a new minimal fresh sample repo (stdlib toy project, 3-5 tasks, no fleet/pr/sync side quests) — clean evidence beats reused evidence, and tasklite receipts already exist for v0.1; the value demo should prove the current version cold.
