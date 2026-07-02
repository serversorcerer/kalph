"""KV15 scaffold checks for samples/value-demo/."""

import os
import stat
import subprocess
import sys
from pathlib import Path

SAMPLE = Path(__file__).resolve().parents[1] / "samples" / "value-demo"


def test_value_demo_directory_exists():
    assert SAMPLE.is_dir()
    assert (SAMPLE / "GOAL.md").is_file()
    assert (SAMPLE / ".kelix" / "kelix.toml").is_file()
    assert (SAMPLE / ".kelix" / "backlog.md").is_file()


def test_value_demo_pytest_passes():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=SAMPLE,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_run_demo_script_executable_and_documents_promote():
    script = SAMPLE / "run-demo.sh"
    assert script.is_file()
    assert os.access(script, os.X_OK) or bool(script.stat().st_mode & stat.S_IEXEC)
    body = script.read_text(encoding="utf-8")
    assert "PROMOTE STEP" in body
    assert "status: ready" in body
    assert "kelix run" in body
