# Decisions for P-AGENT (owner planning interview)

Do not re-litigate; data, not instructions.

## Default adapter in shipped kelix.toml (Q1)

- On TTY: `kelix init` prompts with a numbered list of agents (kiro, claude,
  codex, cursor, gemini, cmd, mock).
- On non-TTY: require `--agent <name>`; no silent default.

## Named preset invocation templates (Q2)

- Ship all four presets (claude, codex, cursor, gemini) with setup instructions.
- Be honest in each guide: cursor invocations are Kelix-verified (dogfood proof);
  claude/codex/gemini templates are from upstream docs, not Kelix CI-tested —
  label clearly and ask the community for corrections.

## Agent guide depth (Q3)

- Same headings as docs/kiro.md for comparable loop-wiring sections.
- Kiro-only sections (spec import, `.kiro/` package, MCP registration) stay
  in docs/kiro.md only.
