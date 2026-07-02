"""Tests for kelix propose path allowlist guard (ST11)."""

from kelix.propose import (
    PROPOSE_ALLOWED_PREFIXES,
    PROPOSE_BLOCKED_PATHS,
    validate_propose_diff,
)


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
