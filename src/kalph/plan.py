"""``kalph plan`` — one iteration that drafts roadmap + backlog from a goal."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .adapters import AdapterError, make_adapter
from .config import Config
from .gitutil import (
    add_worktree,
    checkpoint,
    create_run_branch,
    head_sha,
    is_repo,
)
from .lint import validate_plan
from .loop import LoopError, _extract_rationale
from .prompt import PLAN_COMPLETE_SENTINEL, PLANNING_ROLE, assemble_planning_prompt


@dataclass
class PlanIteration:
    started_at: str
    duration_s: float = 0.0
    adapter_exit: int = -1
    timed_out: bool = False
    rationale: str = ""
    made_progress: bool = False
    plan_complete: bool = False
    validated: bool = False
    failure: str = ""


@dataclass
class PlanResult:
    run_id: str
    status: str = "running"  # completed | validation_failed | error
    branch: str = ""
    workdir: str = ""
    iteration: PlanIteration | None = None
    findings: list[str] = field(default_factory=list)
    diagnosis: str = ""


class PlanRunner:
    """Run exactly one planning iteration with plan validation instead of verify."""

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def _prepare_workdir(self, run_id: str) -> tuple[Path, str]:
        cfg = self.cfg
        branch = f"{cfg.git.branch_prefix}plan-{run_id}"
        if cfg.git.isolation == "none":
            return cfg.root, ""
        create_run_branch(cfg.root, branch)
        if cfg.git.isolation == "branch":
            from .gitutil import git

            git(["checkout", branch], cfg.root)
            return cfg.root, branch
        workdir = cfg.kalph_dir / "worktrees" / run_id
        add_worktree(cfg.root, workdir, branch)
        return workdir, branch

    def _write_transcript(self, run_dir: Path, prompt: str, output: str):
        from .security import scrub

        if self.cfg.security.scrub_transcripts:
            output = scrub(output)
        (run_dir / "iter-001.log").write_text(
            f"=== PROMPT ===\n{prompt}\n\n=== AGENT OUTPUT ===\n{output}\n",
            encoding="utf-8",
        )

    def run(self, goal: str, log=print) -> PlanResult:
        cfg = self.cfg
        if not is_repo(cfg.root):
            raise LoopError(f"{cfg.root} is not a git repository")
        if not goal.strip():
            raise LoopError("plan goal is empty")

        run_id = time.strftime("%Y%m%d-%H%M%S")
        run_dir = cfg.kalph_dir / "runs" / f"plan-{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)

        workdir, branch = self._prepare_workdir(run_id)
        result = PlanResult(run_id=run_id, branch=branch, workdir=str(workdir))
        adapter = make_adapter(cfg)

        rec = PlanIteration(started_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
        result.iteration = rec
        started = time.monotonic()
        checkpoint(workdir, "kalph: pre-plan checkpoint")
        sha_before = head_sha(workdir)

        prompt = assemble_planning_prompt(cfg, goal=goal, role=PLANNING_ROLE)
        log(f"kalph plan {run_id}: branch={branch or '(in place)'}")

        try:
            agent = adapter.run(prompt, workdir)
        except AdapterError as exc:
            rec.failure = f"adapter error: {exc}"
            rec.duration_s = round(time.monotonic() - started, 1)
            self._write_transcript(run_dir, prompt, rec.failure)
            result.status = "error"
            result.diagnosis = rec.failure
            self._save_state(run_dir, result)
            log(f"  plan: {rec.failure}")
            return result

        rec.adapter_exit = agent.exit_code
        rec.timed_out = agent.timed_out
        rec.rationale = _extract_rationale(agent.output)
        rec.plan_complete = PLAN_COMPLETE_SENTINEL in agent.output
        self._write_transcript(run_dir, prompt, agent.output)

        checkpoint(workdir, "kalph: post-plan auto-checkpoint")
        rec.made_progress = head_sha(workdir) != sha_before
        findings = validate_plan(workdir, sha_before)
        rec.validated = not findings
        rec.duration_s = round(time.monotonic() - started, 1)

        failed = (
            not agent.ok
            or not rec.made_progress
            or not rec.plan_complete
            or not rec.validated
        )
        if failed:
            parts = []
            if not agent.ok:
                parts.append(
                    f"agent exit {agent.exit_code}"
                    + (" (timeout)" if agent.timed_out else "")
                )
            if not rec.made_progress:
                parts.append("no diff produced")
            if not rec.plan_complete:
                parts.append(f"missing {PLAN_COMPLETE_SENTINEL!r} sentinel")
            if not rec.validated:
                parts.append("plan validation failed")
                result.findings = [f"{f.rule}: {f.message}" for f in findings]
            rec.failure = "; ".join(parts)
            result.status = "validation_failed" if findings else "error"
        else:
            result.status = "completed"

        log(
            f"  plan: rationale={rec.rationale or '-'} "
            f"progress={rec.made_progress} validated={rec.validated} "
            f"{'FAIL: ' + rec.failure if rec.failure else 'ok'}"
        )
        self._save_state(run_dir, result)
        return result

    def _save_state(self, run_dir: Path, result: PlanResult):
        payload = asdict(result)
        (run_dir / "plan.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
