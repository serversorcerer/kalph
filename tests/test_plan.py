"""Tests for ``kalph plan`` — one-iteration planning with validation."""

import json
import subprocess

from conftest import write_mock_script

from kalph.cli import cmd_plan
from kalph.config import load_config
from kalph.plan import PlanRunner
from kalph.prompt import PLAN_COMPLETE_SENTINEL, PLANNING_TEMPLATE, assemble_planning_prompt


def _config(repo, mock_dir="mockdir", isolation="none"):
    (repo / "kalph.toml").write_text(
        f"""
[agent]
adapter = "mock"
mock_dir = "{mock_dir}"

[git]
isolation = "{isolation}"
"""
    )
    subprocess.run(["git", "add", "kalph.toml"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "add kalph config"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    return load_config(repo)


def _git_out(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True
    ).stdout


PLAN_SCRIPT = """\
cat > .kalph/roadmap.md << 'EOF'
# Roadmap

## Milestone M1 — Demo milestone

### Phase P-DEMO — demo phase
Outcome: demo works.

- REQ-D1: first requirement
EOF

cat >> .kalph/backlog.md << 'EOF'
- [ ] T10: demo task | priority: 50 | status: proposed | by: kalph | phase: P-DEMO | req: REQ-D1
  details: assert True in tests/test_demo.py
EOF
git add .kalph/roadmap.md .kalph/backlog.md && git commit -q -m "plan: draft demo"
echo "PLAN COMPLETE"
"""


def test_planning_prompt_includes_goal(tmp_path):
    cfg = load_config(tmp_path)
    out = assemble_planning_prompt(cfg, goal="build a widget tracker")
    assert "build a widget tracker" in out
    assert PLAN_COMPLETE_SENTINEL in out
    assert "{{" not in out


def test_planning_template_is_static():
    assert "{{GOAL}}" in PLANNING_TEMPLATE
    assert "status: proposed" in PLANNING_TEMPLATE


def test_plan_happy_path_writes_draft(repo):
    write_mock_script(repo / "mockdir", "001.sh", PLAN_SCRIPT)
    cfg = _config(repo)
    result = PlanRunner(cfg).run(goal="build a demo", log=lambda *_: None)
    assert result.status == "completed"
    assert result.iteration is not None
    assert result.iteration.plan_complete
    assert result.iteration.validated

    roadmap = (repo / ".kalph" / "roadmap.md").read_text()
    assert "## Milestone M1" in roadmap
    assert "REQ-D1" in roadmap

    from kalph.backlog import parse_backlog

    tasks = parse_backlog((repo / ".kalph" / "backlog.md").read_text())
    new_tasks = [t for t in tasks if t.id == "T10"]
    assert len(new_tasks) == 1
    assert new_tasks[0].status == "proposed"
    assert new_tasks[0].by == "kalph"

    run_dir = cfg.kalph_dir / "runs" / f"plan-{result.run_id}"
    assert (run_dir / "iter-001.log").exists()
    assert json.loads((run_dir / "plan.json").read_text())["status"] == "completed"


def test_plan_rejects_non_planning_changes(repo):
    bad = PLAN_SCRIPT.replace(
        "git add .kalph/roadmap.md .kalph/backlog.md",
        "echo oops > src.txt && git add .kalph/roadmap.md .kalph/backlog.md src.txt",
    )
    write_mock_script(repo / "mockdir", "001.sh", bad)
    cfg = _config(repo)
    result = PlanRunner(cfg).run(goal="build a demo", log=lambda *_: None)
    assert result.status == "validation_failed"
    assert any("non_planning_change" in f for f in result.findings)


def test_plan_worktree_leaves_main_untouched(repo):
    write_mock_script(repo / "mockdir", "001.sh", PLAN_SCRIPT)
    cfg = _config(repo, isolation="worktree")
    main_sha = _git_out(repo, "rev-parse", "main").strip()
    result = PlanRunner(cfg).run(goal="build a demo", log=lambda *_: None)
    assert result.status == "completed"
    assert _git_out(repo, "rev-parse", "main").strip() == main_sha
    assert not (repo / ".kalph" / "roadmap.md").exists()


def test_cmd_plan_goal_file(repo):
    write_mock_script(repo / "mockdir", "001.sh", PLAN_SCRIPT)
    _config(repo)
    goal_path = repo / "GOAL.md"
    goal_path.write_text("build from file\n")

    class Args:
        path = str(repo)
        goal = ""
        goal_file = str(goal_path)

    assert cmd_plan(Args()) == 0


def test_cmd_plan_goal_string(repo):
    write_mock_script(repo / "mockdir", "001.sh", PLAN_SCRIPT)
    _config(repo)

    class Args:
        path = str(repo)
        goal = "inline goal"
        goal_file = ""

    assert cmd_plan(Args()) == 0
