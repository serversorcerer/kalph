---
name: ship-agent-guide
description: >-
  Add or extend a docs/agents/*.md loop-wiring guide with banner, heading parity,
  preset-aligned invocation, and load_config-verified TOML tests. Use when closing
  REQ-A2 agent-guide backlog tasks or documenting a new named adapter preset.
---

# Ship an agent integration guide

Each guide lives at `docs/agents/<preset>.md` and must match the loop-wiring shape used by `docs/kiro.md` and sibling guides.

## 1. Choose the verification banner

| Provenance | Banner text | When |
|------------|-------------|------|
| Kelix dogfood / CI proof | `**Kelix-verified invocation.**` | Command exercised in Kelix self-host or proof report |
| Upstream docs only | `**Not Kelix CI-tested.**` | Sourced from vendor headless docs; community corrections welcome |

The documented headless command **must** exactly match `ADAPTER_PRESET_COMMANDS["<preset>"]` in `src/kelix/config.py`.

## 2. Write the guide sections

Use these `##` headings in order (parity enforced by `tests/test_agent_guides.py`):

1. The headless adapter
2. Configure kelix.toml
3. Install
4. Auth
5. Worked example: init → plan → run
6. Quirks
7. Troubleshooting

In **Configure kelix.toml**, show `adapter = "<preset>"` first; optionally show the expanded `adapter = "cmd"` + `command = "..."` block the preset resolves to.

## 3. Extend acceptance tests

In `tests/test_agent_guides.py`:

1. Add `ROOT / "docs" / "agents" / "<preset>.md"` constant.
2. Add banner test asserting the correct banner string and preset command substring.
3. Reuse `AGENT_GUIDE_LOOP_HEADINGS` for heading parity.
4. Parametrize over fenced ` ```toml ` blocks — write each to `tmp_path/.kelix/kelix.toml` and call `load_config(tmp_path)` without error.

Copy the Claude/Codex/Gemini test trio as a template; Cursor is the Kelix-verified reference.

## 4. Verify

```bash
pytest -q tests/test_agent_guides.py
pytest -q
ruff check src tests
```

Do not change guide TOML blocks solely to satisfy tests — fix the guide or preset if `load_config` fails.
