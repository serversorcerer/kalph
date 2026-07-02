"""Pull request flow for overnight runs.

Opens a reviewable PR after a completed run — never pushes to main/master
directly.
"""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from .config import Config
from .gitutil import PROTECTED_BRANCHES
from .loop import RunResult

if TYPE_CHECKING:
    from .propose import ProposeResult

log = logging.getLogger(__name__)

TASK_ID_RE = re.compile(r"\b([A-Z]+\d+)\b")


def _extract_task_ids(rationales: list[str]) -> list[str]:
    seen: set[str] = set()
    ids: list[str] = []
    for rationale in rationales:
        for match in TASK_ID_RE.finditer(rationale):
            task_id = match.group(1)
            if task_id not in seen:
                seen.add(task_id)
                ids.append(task_id)
    return ids


def build_pr_title(result: RunResult) -> str:
    for rec in result.iterations:
        if rec.rationale:
            return f"kelix: {rec.rationale}"
    return f"kelix: {result.run_id}"


def build_pr_body(cfg: Config, result: RunResult) -> str:
    rationales = [rec.rationale for rec in result.iterations if rec.rationale]
    lines = ["## Summary", ""]
    if rationales:
        lines.extend(f"- {rationale}" for rationale in rationales)
    else:
        lines.append("- (no rationales recorded)")

    lines.extend(["", "## Verification evidence", ""])
    if cfg.verify.commands:
        lines.append("Verify commands:")
        lines.extend(f"- `{command}`" for command in cfg.verify.commands)
        lines.append("")
    for rec in result.iterations:
        if rec.verified is True:
            status = "verified"
        elif rec.verified is False:
            status = "failed"
        else:
            status = "not configured"
        lines.append(f"- iteration {rec.index}: {status}")

    lines.extend(["", "## Backlog", ""])
    task_ids = _extract_task_ids(rationales)
    if task_ids:
        lines.extend(f"- {task_id}" for task_id in task_ids)
    else:
        lines.append("- (none detected)")

    lines.extend(
        [
            "",
            f"Opened by Kelix run {result.run_id}; review before merging.",
        ]
    )
    return "\n".join(lines)


def _push_and_create_pr(workdir: Path, branch: str, title: str, body: str) -> str | None:
    """Push *branch* and open a GitHub PR. Returns the PR URL or None."""
    try:
        push = subprocess.run(
            ["git", "push", "-u", "origin", branch],
            cwd=str(workdir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if push.returncode != 0:
            log.warning("git push failed: %s", push.stdout)
            return None

        create = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--title",
                title,
                "--body",
                body,
                "--base",
                "main",
                "--head",
                branch,
            ],
            cwd=str(workdir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if create.returncode != 0:
            log.warning("gh pr create failed: %s", create.stdout)
            return None
        return create.stdout.strip()
    except Exception as exc:  # log-and-skip; never raise out
        log.warning("open_pr failed: %s", exc)
        return None


def build_propose_pr_title(result: ProposeResult) -> str:
    """Return a PR title for a tuning proposal."""
    prediction = ""
    if result.iteration and result.iteration.predicted_improvement:
        prediction = result.iteration.predicted_improvement
    if prediction:
        short = prediction if len(prediction) <= 72 else prediction[:69] + "..."
        return f"kelix propose: {short}"
    return f"kelix propose: {result.proposal_id}"


def build_propose_pr_body(
    cfg: Config,
    result: ProposeResult,
    *,
    metrics_excerpt: str,
    diagnosis_file: str = "",
) -> str:
    """Build a PR body for a policy-surface tuning proposal."""
    prediction = ""
    if result.iteration and result.iteration.predicted_improvement:
        prediction = result.iteration.predicted_improvement

    lines = ["## Metric evidence", ""]
    if metrics_excerpt.strip():
        lines.extend(["```json", metrics_excerpt.strip(), "```"])
    else:
        lines.append("(no loop-metrics.json data)")

    lines.extend(["", "## Diagnosis", ""])
    if diagnosis_file:
        lines.append(f"- `{diagnosis_file}`")
    else:
        lines.append("- (none supplied)")

    lines.extend(["", "## Predicted improvement", ""])
    lines.append(prediction or "(not recorded)")

    lines.extend(["", "## Changed policy surface", ""])
    if result.touched_files:
        lines.extend(f"- `{path}`" for path in result.touched_files)
    else:
        lines.append("- (none)")

    lines.extend(
        [
            "",
            f"Opened by Kelix propose {result.proposal_id}; review before merging.",
        ]
    )
    return "\n".join(lines)


def open_propose_pr(
    cfg: Config,
    result: ProposeResult,
    *,
    metrics_excerpt: str,
    diagnosis_file: str = "",
) -> str | None:
    """Push the propose branch and open a GitHub PR. Returns the PR URL or None."""
    branch = result.branch
    if not branch or branch in PROTECTED_BRANCHES:
        log.info("refusing to open propose PR: branch=%r", branch)
        return None

    workdir = result.workdir if result.workdir else cfg.root
    title = build_propose_pr_title(result)
    body = build_propose_pr_body(
        cfg,
        result,
        metrics_excerpt=metrics_excerpt,
        diagnosis_file=diagnosis_file,
    )
    return _push_and_create_pr(workdir, branch, title, body)


def open_pr(cfg: Config, result: RunResult, run_dir: Path) -> str | None:
    """Push the run branch and open a GitHub PR. Returns the PR URL or None."""
    del run_dir  # reserved for future run-artifact references
    branch = result.branch
    if not branch or branch in PROTECTED_BRANCHES:
        log.info("refusing to open PR: branch=%r", branch)
        return None

    workdir = Path(result.workdir) if result.workdir else cfg.root
    title = build_pr_title(result)
    body = build_pr_body(cfg, result)
    return _push_and_create_pr(workdir, branch, title, body)
