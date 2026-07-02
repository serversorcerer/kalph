"""``kelix propose`` path guard — restrict self-tuning edits to policy surface.

Owner decisions (T-PROPOSE CONTEXT): proposals may touch prompt templates,
security denylist defaults, config defaults, and documented kelix.toml template
keys for ``[memory]`` / ``[loop]`` only. Never backlog, STATE, or roadmap.
"""

from __future__ import annotations

# Whole-path allowlist. Partial-file restrictions are documented per entry;
# ST12 may add diff-level checks against these notes.
PROPOSE_ALLOWED_PREFIXES: tuple[str, ...] = (
    ".kelix/prompts/",
    "src/kelix/security.py",
    "src/kelix/config.py",
    ".kelix/kelix.toml",
    "kelix.toml",
)

# Explicit blocked paths (also checked before prefix allowlist).
PROPOSE_BLOCKED_PATHS: tuple[str, ...] = (
    ".kelix/backlog.md",
    ".kelix/STATE.md",
    ".kelix/roadmap.md",
)

# Partial-file edit surfaces (documentation for ST12 diff validation).
# security.py: only the DEFAULT_DENY constant list (currently lines 52–64).
PROPOSE_SECURITY_EDITABLE = "DEFAULT_DENY denylist patterns only"
# config.py: dataclass field defaults (LoopConfig, MemoryConfig, etc.).
PROPOSE_CONFIG_EDITABLE = "dataclass field defaults in config.py only"
# kelix.toml template: [memory] and [loop] documented keys only (see cli.CONFIG_TEMPLATE).
PROPOSE_KELIX_TOML_EDITABLE = "[memory] and [loop] template keys only"


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    while normalized.startswith("../"):
        normalized = normalized[3:]
    return normalized


def _is_allowed(path: str) -> bool:
    for prefix in PROPOSE_ALLOWED_PREFIXES:
        if prefix.endswith("/"):
            if path.startswith(prefix) or path == prefix.rstrip("/"):
                return True
        elif path == prefix:
            return True
    return False


def validate_propose_diff(changed_paths: list[str]) -> list[str]:
    """Return violation messages for paths outside the propose allowlist.

    Each changed path is checked against ``PROPOSE_BLOCKED_PATHS`` first, then
    ``PROPOSE_ALLOWED_PREFIXES``. An empty input list returns an empty list.
    """
    violations: list[str] = []
    for raw in changed_paths:
        path = _normalize_path(raw)
        if not path:
            continue
        if path in PROPOSE_BLOCKED_PATHS:
            violations.append(f"{path}: blocked (backlog, STATE, and roadmap are never editable)")
            continue
        if not _is_allowed(path):
            violations.append(f"{path}: not in propose allowlist")
    return violations
