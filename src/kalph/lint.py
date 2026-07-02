"""Plan and backlog lint — machine-check draft plans before promotion."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .backlog import parse_backlog
from .roadmap import load_roadmap, parse_roadmap

PLAN_ARTIFACTS = (
    ".kalph/roadmap.md",
    ".kalph/backlog.md",
)


@dataclass
class Finding:
    task_id: str
    rule: str
    message: str


def _planning_only_changes(workdir: Path, base_sha: str) -> list[Finding]:
    """Ensure the iteration only touched planning artifacts."""
    from .gitutil import git

    if not base_sha:
        return []
    names = git(
        ["diff", "--name-only", base_sha, "HEAD"],
        workdir,
        check=False,
    ).splitlines()
    findings: list[Finding] = []
    for name in names:
        if not name:
            continue
        if name in PLAN_ARTIFACTS:
            continue
        if name.startswith(".kalph/phases/"):
            continue
        findings.append(
            Finding(
                "",
                "non_planning_change",
                f"plan iteration changed {name!r}; only roadmap/backlog/phase files allowed",
            )
        )
    return findings


def validate_plan(workdir: Path, base_sha: str = "") -> list[Finding]:
    """Validate a draft plan produced by ``kalph plan``.

    Checks roadmap parse, proposed-only kalph tasks, REQ coverage, and that
    only planning files changed. Expanded lint rules live in ``lint_backlog``.
    """
    findings: list[Finding] = []
    kalph = workdir / ".kalph"
    roadmap_path = kalph / "roadmap.md"
    backlog_path = kalph / "backlog.md"

    if not roadmap_path.is_file():
        findings.append(Finding("", "roadmap_missing", "missing .kalph/roadmap.md"))
    else:
        roadmap = parse_roadmap(roadmap_path.read_text(encoding="utf-8"))
        if not roadmap.milestones:
            findings.append(
                Finding("", "roadmap_empty", "roadmap has no milestones")
            )
        if not roadmap.phases:
            findings.append(Finding("", "roadmap_empty", "roadmap has no phases"))
        if not roadmap.reqs:
            findings.append(Finding("", "roadmap_empty", "roadmap has no REQs"))

    if not backlog_path.is_file():
        findings.append(Finding("", "backlog_missing", "missing .kalph/backlog.md"))
        return findings + _planning_only_changes(workdir, base_sha)

    tasks = parse_backlog(backlog_path.read_text(encoding="utf-8"))
    for task in tasks:
        if task.by == "kalph" and task.status != "proposed":
            findings.append(
                Finding(
                    task.id,
                    "not_proposed",
                    f"kalph-authored task {task.id!r} must have status: proposed",
                )
            )

    roadmap = load_roadmap(kalph)
    if roadmap is not None:
        covered = {task.req for task in tasks if task.req}
        for req in roadmap.reqs:
            if req.id not in covered:
                findings.append(
                    Finding(
                        "",
                        "uncovered_req",
                        f"{req.id} is not referenced by any backlog task",
                    )
                )

    findings.extend(_planning_only_changes(workdir, base_sha))
    return findings
