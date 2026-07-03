# PyPI publish + doc refresh — owner decisions (PUB run)

Owner PyPI account is registered. Kelix lands everything that can be committed;
the owner still does one-time UI steps (trusted publisher, GitHub `pypi`
environment, `git tag v0.1.0 && git push origin v0.1.0`).

## Audience (binding tone)

Primary readers: **vibe-coders, power users, and software developers** already
using headless coding CLIs (Cursor, Claude Code, Codex, Gemini). They know git,
tests, and overnight agent runs. Write for competence, not beginners.

- **Do:** precise terms (verify gate, worktree, adapter, backlog, Ralph loop),
  short receipts, copy-paste commands, honest alpha caveats.
- **Don't:** patronizing "plain English" sections, "you do not need to know
  jargon" framing, emoji, or tutorial voice that hides how the loop works.
- **Balance:** one sentence of context for unfamiliar terms, then move on.

## PyPI deliverables (code)

- `pyproject.toml`: PEP 621 metadata, `license = "Apache-2.0"`, `license-files`,
  `project.urls` (Homepage, Documentation, Repository, Issues).
- `.github/workflows/publish.yml`: on tag `v*`, build, `twine check`, upload via
  `pypa/gh-action-pypi-publish`, `environment: pypi`.
- `.github/workflows/ci.yml`: `package` job builds wheel and runs `kelix --help`.
- `docs/publishing.md`: maintainer runbook (trusted publishing, TestPyPI optional,
  tag release, verify `pipx install kelix`).

## Doc files in scope

README.md, docs/index.md, docs/quickstart.md, CONTRIBUTING.md, docs/_config.yml,
docs/agents/cursor.md (install section only if stale), docs/agents/claude.md,
docs/agents/codex.md, docs/agents/gemini.md.

## Out of scope

- Owner clicks on pypi.org / GitHub environment UI (document only).
- Pushing git tags from this run.
- Changing loop behavior or adding features.

## Verify gate

`env PYTHONPATH=src pytest -q`, `ruff check src tests`, `kelix lint --path .`,
`python -m build && twine check dist/*`.
