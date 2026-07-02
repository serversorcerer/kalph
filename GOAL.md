# Goal: The value cut — one loop run to make Kelix undeniably worth it

You are shipping Kelix. Before the doors open, one honest pass: keep what
demonstrably creates value, sharpen it, and scrap what doesn't. The measure
of every decision is the same question the user will ask: "what did the
agent give me that I couldn't get without it?" Features are cost. Verified
outcomes are value. Simplicity is a feature.

The one-sentence value proposition to protect: **you write a well-specified
goal, walk away, and come back to verified commits.** Everything in the
codebase either serves that sentence or leaves.

## Phase V-LEDGER — The value ledger (evidence before opinions)

- Produce docs/value-ledger.md: one row per feature/module (loop, verify,
  plan+interview, lint, state/roadmap/backlog, memory, skills, fleet,
  claims, mcp_server, sync/, pr, kiro, security, adapters, art). Columns:
  lines of code, receipt (proof artifact / test / real run that shows it
  earning value — cite the path), and verdict: SHARPEN, KEEP, or SCRAP.
- The decision rule, applied without sentiment:
  - SHARPEN: has a receipt AND sits on the critical path of the value
    sentence. (Known receipts: verify gate caught real bugs; plan interview
    caught its own draft's REQ collisions, D19; lint rejected slop; circuit
    breaker stopped no-diff burn; worktree isolation survived a killed
    agent, D13.)
  - KEEP: has a receipt but is off the critical path. Freeze it — no new
    code, no new docs beyond what exists.
  - SCRAP: no receipt. Known candidates to evaluate honestly: sync/ (304
    lines, only ever ran against a mocked transport — final-report line
    130), mcp_server (180 lines, appears in zero proof artifacts), skills
    plumbing (shipped, never demonstrated learning — D17), pr.py (built,
    used how many times?). Scrapped code is deleted, not attic'd — git
    history is the attic. Update docs, config, CLI, and tests in the same
    task so nothing dangles.
- Acceptance: ledger exists, every row cites a receipt path or says "none";
  every SCRAP verdict lists the deletion task it spawned; the owner can
  veto any row by editing the file before execution phases run.

## Phase V-SHARPEN — Double down on what's working

- The verification gate is the product. Make its output the best thing the
  user sees: the run-complete message names each verify command, its exit
  status, and the commits it blessed — receipts, not "done."
- The plan interview is the moat. Tighten it: questions must be decisions
  (2-4 options + recommendation), never open-ended essays; cap at the 7
  highest-leverage questions per plan; every answer lands in the phase
  CONTEXT.md so no decision is ever asked twice.
- The circuit breaker and lint gate are trust. When either fires, the
  message must say exactly what to change and where — a user who gets
  stopped should know their next move in one read.
- Acceptance: a run transcript shows the receipt-style completion message;
  a plan run on a sample goal asks <= 7 questions, all multiple-choice;
  breaker/lint messages name file + line/task-id + fix. Tests cover each.

## Phase V-SIMPLE — Cut the surface, not the power

- CLI: audit all subcommands against the ledger. A command whose feature
  was scrapped goes with it. Target: a new user needs exactly three
  commands (init, plan, run) to reach their first verified commit; the
  rest must justify themselves in the ledger.
- Config: every kelix.toml key nobody sets in any proof run, doc, or test
  fixture defaults correctly and disappears from the template. The shipped
  template fits on one screen with comments.
- Docs: index.md routes by user intent ("I want to ship X unattended")
  in five links or fewer. Merge or delete any page whose feature was
  scrapped. Quickstart is measured: a stranger reaches a verified commit
  in the documented step count, no side quests.
- Acceptance: `kelix init && kelix plan && kelix run` is the complete
  documented happy path; the config template is <= 25 lines; every
  remaining doc page maps to a SHARPEN or KEEP row.

## Phase V-PROOF — The value demo is the release gate

- One fresh scripted run on a clean sample repo: goal in, interview,
  promote, run, verified commits out. Capture the transcript as
  docs/proof/value-demo.md with wall-clock time and iteration count.
- README leads with this demo — the real transcript, not a synthetic
  example. The value sentence, then the receipt, in the first screen.
- Acceptance: the demo transcript is reproducible from its own commands;
  README's first screen contains the value sentence + a link to the
  transcript; all tests pass; kelix lint clean; plan validation clean.

## Non-goals

- No new features. This run only sharpens, keeps, or deletes.
- Do not touch the verification gate's strictness, security rails, or
  worktree isolation — the trust core is not up for simplification.
- No rewrites for elegance. SHARPEN means the user-facing edge improves;
  internals change only where a scrap or a message improvement requires it.
- Scrapping is reversible by git revert, but do not build compat shims,
  deprecation warnings, or feature flags. Alpha means clean cuts.
