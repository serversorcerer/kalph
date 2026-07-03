"""Packaging smoke tests (REQ-PB4): PyPI metadata and build artifacts."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
PUBLISH_YML = ROOT / ".github" / "workflows" / "publish.yml"


def _load_pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def test_publish_workflow_exists():
    assert PUBLISH_YML.is_file()
    text = PUBLISH_YML.read_text(encoding="utf-8")
    assert "pypa/gh-action-pypi-publish" in text
    assert "v*" in text


def test_pyproject_license_and_script_entry():
    project = _load_pyproject()["project"]
    assert project["license"] == "Apache-2.0"
    assert project["scripts"]["kelix"] == "kelix.cli:main"


def test_pyproject_version_matches_package():
    from kelix import __version__

    assert _load_pyproject()["project"]["version"] == __version__


def test_python_build_produces_wheel_and_sdist(tmp_path):
    pytest.importorskip("build")
    for name in ("pyproject.toml", "README.md", "LICENSE"):
        shutil.copy2(ROOT / name, tmp_path / name)
    shutil.copytree(ROOT / "src", tmp_path / "src")

    result = subprocess.run(
        [sys.executable, "-m", "build"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout

    dist = tmp_path / "dist"
    wheels = list(dist.glob("*.whl"))
    sdists = list(dist.glob("*.tar.gz"))
    assert len(wheels) == 1
    assert len(sdists) == 1
    assert wheels[0].name.startswith("kelix-")
