"""Tests for kelix propose path guard and command (ST11, ST12)."""

import json
import subprocess
from pathlib import Path

from conftest import write_mock_script

from kelix.config import load_config
from kelix.metrics import IterationLedgerRow, LoopMetrics, save_metrics
from kelix.prompt import PROPOSE_TEMPLATE, assemble_propose_prompt
from kelix.propose import (
    PROPOSE_ALLOWED_PREFIXES,
    PROPOSE_BLOCKED_PATHS,
    ProposeRunner,
    extract_predicted_improvement,
    validate_propose_diff,
)


def _write_metrics(kelix: Path, rows: list[IterationLedgerRow]) -> None:
    save_metrics(kelix / "memory" / "loop-metrics.json", LoopMetrics(iterations=rows))


def _config(repo: Path, mock_dir: str = "mockdir") -> object:
    (repo / "kelix.toml").write_text(
        f"""
[agent]
adapter = "mock"
mock_dir = "{mock_dir}"

[git]
isolation = "none"
"""
    )
    subprocess.run(["git", "add", "kelix.toml"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "add kelix config"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    return load_config(repo)


ALLOWED_PROPOSE_SCRIPT = """\
mkdir -p .kelix/prompts
echo '# tuned prompt' > .kelix/prompts/iteration.md
git add .kelix/prompts/iteration.md
git commit -q -m 'propose: tune iteration prompt'
echo 'PREDICTED_IMPROVEMENT: raise verified rate on retry-heavy tasks'
"""

FORBIDDEN_PROPOSE_SCRIPT = """\
echo 'slop' >> .kelix/backlog.md
git add .kelix/backlog.md
git commit -q -m 'propose: edit backlog'
echo 'PREDICTED_IMPROVEMENT: should not land'
"""


def test_allowed_prompt_template_path():
    violations = validate_propose_diff([".kelix/prompts/iteration.md"])
    assert violations == []


def test_allowed_security_and_config_paths():
    violations = validate_propose_diff(
        [
            "src/kelix/security.py",
            "src/kelix/config.py",
        ]
    )
    assert violations == []


def test_allowed_kelix_toml_paths():
    violations = validate_propose_diff([".kelix/kelix.toml", "kelix.toml"])
    assert violations == []


def test_forbidden_backlog_state_roadmap():
    violations = validate_propose_diff(
        [
            ".kelix/backlog.md",
            ".kelix/STATE.md",
            ".kelix/roadmap.md",
        ]
    )
    assert len(violations) == 3
    assert all("blocked" in v for v in violations)


def test_forbidden_arbitrary_paths():
    violations = validate_propose_diff(
        [
            "src/kelix/loop.py",
            "README.md",
            ".kelix/memory/project.md",
        ]
    )
    assert len(violations) == 3
    assert all("not in propose allowlist" in v for v in violations)


def test_normalize_leading_dot_slash():
    violations = validate_propose_diff(["./.kelix/prompts/custom.md"])
    assert violations == []


def test_mixed_allowed_and_forbidden():
    violations = validate_propose_diff(
        [
            ".kelix/prompts/iteration.md",
            ".kelix/backlog.md",
            "src/kelix/cli.py",
        ]
    )
    assert len(violations) == 2
    assert any("backlog.md" in v and "blocked" in v for v in violations)
    assert any("cli.py" in v and "allowlist" in v for v in violations)


def test_allowlist_and_blocklist_constants_non_empty():
    assert PROPOSE_ALLOWED_PREFIXES
    assert PROPOSE_BLOCKED_PATHS


def test_extract_predicted_improvement():
    out = "done\nPREDICTED_IMPROVEMENT: fewer breaker trips on no-diff\n"
    assert extract_predicted_improvement(out) == "fewer breaker trips on no-diff"
    assert extract_predicted_improvement("no metadata") == ""


def test_assemble_propose_prompt_substitutes_slots(tmp_path: Path):
    cfg = load_config(tmp_path)
    out = assemble_propose_prompt(
        cfg,
        metrics_excerpt='{"iterations": []}',
        diagnosis_excerpt="## Findings\nretry heavy",
    )
    assert '{"iterations": []}' in out
    assert "retry heavy" in out
    assert "PREDICTED_IMPROVEMENT" in out
    assert "{{" not in out


def test_propose_template_is_static():
    assert "{{METRICS_EXCERPT}}" in PROPOSE_TEMPLATE
    assert "{{DIAGNOSIS_EXCERPT}}" in PROPOSE_TEMPLATE


def test_propose_runner_allowed_edit(repo):
    kelix = repo / ".kelix"
    _write_metrics(
        kelix,
        [
            IterationLedgerRow(
                run_id="20260702-040000",
                iteration=1,
                task_id="T2",
                verified=False,
                failure="fail",
            ),
        ],
    )
    write_mock_script(repo / "mockdir", "001.sh", ALLOWED_PROPOSE_SCRIPT)
    cfg = _config(repo)

    result = ProposeRunner(cfg).run(log=lambda *_: None)
    assert result.status == "completed"
    assert result.iteration is not None
    assert result.iteration.validated
    assert ".kelix/prompts/iteration.md" in result.touched_files
    assert result.sidecar_path.is_file()
    sidecar = json.loads(result.sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["prediction"] == "raise verified rate on retry-heavy tasks"
    assert sidecar["touched_files"] == [".kelix/prompts/iteration.md"]


def test_propose_runner_rejects_backlog_edit(repo):
    kelix = repo / ".kelix"
    _write_metrics(kelix, [])
    write_mock_script(repo / "mockdir", "001.sh", FORBIDDEN_PROPOSE_SCRIPT)
    cfg = _config(repo)

    result = ProposeRunner(cfg).run(log=lambda *_: None)
    assert result.status == "validation_failed"
    assert result.findings
    assert any("backlog.md" in f for f in result.findings)


def test_cmd_propose_allowed_edit(repo, capsys):
    from kelix.cli import cmd_propose

    kelix = repo / ".kelix"
    _write_metrics(kelix, [])
    write_mock_script(repo / "mockdir", "001.sh", ALLOWED_PROPOSE_SCRIPT)
    _config(repo)

    class Args:
        path = str(repo)
        diagnosis_file = ""
        no_pr = True

    assert cmd_propose(Args()) == 0
    out = capsys.readouterr().out
    assert "proposal ready" in out
    assert "sidecar written" in out


def test_cmd_propose_rejects_backlog_edit(repo, capsys):
    from kelix.cli import cmd_propose

    kelix = repo / ".kelix"
    _write_metrics(kelix, [])
    write_mock_script(repo / "mockdir", "001.sh", FORBIDDEN_PROPOSE_SCRIPT)
    _config(repo)

    class Args:
        path = str(repo)
        diagnosis_file = ""
        no_pr = True

    assert cmd_propose(Args()) == 1
    err = capsys.readouterr().err
    assert "backlog.md" in err


def test_cmd_propose_with_diagnosis_file(repo, capsys):
    from kelix.cli import cmd_propose

    kelix = repo / ".kelix"
    _write_metrics(kelix, [])
    diagnosis = kelix / "memory" / "diagnosis-fixture.md"
    diagnosis.write_text("## Findings\ncontext_share too low\n", encoding="utf-8")
    write_mock_script(repo / "mockdir", "001.sh", ALLOWED_PROPOSE_SCRIPT)
    _config(repo)

    class Args:
        path = str(repo)
        diagnosis_file = ".kelix/memory/diagnosis-fixture.md"
        no_pr = True

    assert cmd_propose(Args()) == 0
    sidecars = list((kelix / "memory").glob("proposal-*.json"))
    assert sidecars
    sidecar = json.loads(sidecars[0].read_text(encoding="utf-8"))
    assert sidecar["diagnosis_file"] == ".kelix/memory/diagnosis-fixture.md"


def test_cmd_propose_opens_pr_with_metric_evidence(repo, capsys, monkeypatch):
    from kelix.cli import cmd_propose

    kelix = repo / ".kelix"
    _write_metrics(
        kelix,
        [
            IterationLedgerRow(
                run_id="20260702-040000",
                iteration=1,
                task_id="T2",
                verified=False,
                failure="fail",
            ),
        ],
    )
    write_mock_script(repo / "mockdir", "001.sh", ALLOWED_PROPOSE_SCRIPT)
    _config(repo)

    calls: list[dict] = []

    def fake_open_propose_pr(cfg, result, *, metrics_excerpt, diagnosis_file=""):
        calls.append(
            {
                "metrics_excerpt": metrics_excerpt,
                "diagnosis_file": diagnosis_file,
                "branch": result.branch,
            }
        )
        return "https://github.com/org/repo/pull/99"

    monkeypatch.setattr("kelix.pr.open_propose_pr", fake_open_propose_pr)

    class Args:
        path = str(repo)
        diagnosis_file = ""
        no_pr = False

    assert cmd_propose(Args()) == 0
    assert len(calls) == 1
    assert "20260702-040000" in calls[0]["metrics_excerpt"]
    out = capsys.readouterr().out
    assert "PR opened" in out

    from kelix.pr import build_propose_pr_body
    from kelix.propose import ProposeIteration, ProposeResult

    body = build_propose_pr_body(
        load_config(repo),
        ProposeResult(
            proposal_id="test",
            touched_files=[".kelix/prompts/iteration.md"],
            iteration=ProposeIteration(
                started_at="",
                predicted_improvement="raise verified rate",
            ),
        ),
        metrics_excerpt=calls[0]["metrics_excerpt"],
    )
    assert "## Metric evidence" in body
    assert "## Diagnosis" in body
    assert "## Predicted improvement" in body
    assert "## Changed policy surface" in body
    assert "raise verified rate" in body


def test_cmd_propose_no_pr_skips_open(repo, capsys, monkeypatch):
    from kelix.cli import cmd_propose

    kelix = repo / ".kelix"
    _write_metrics(kelix, [])
    write_mock_script(repo / "mockdir", "001.sh", ALLOWED_PROPOSE_SCRIPT)
    _config(repo)

    called = {"value": False}

    def fake_open_propose_pr(*args, **kwargs):
        called["value"] = True
        return None

    monkeypatch.setattr("kelix.pr.open_propose_pr", fake_open_propose_pr)

    class Args:
        path = str(repo)
        diagnosis_file = ""
        no_pr = True

    assert cmd_propose(Args()) == 0
    assert called["value"] is False


def test_loop_does_not_import_propose():
    import ast

    loop_src = Path(__file__).resolve().parents[1] / "src" / "kelix" / "loop.py"
    tree = ast.parse(loop_src.read_text(encoding="utf-8"))
    imports = {
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module and "propose" in node.module
    }
    assert not imports
