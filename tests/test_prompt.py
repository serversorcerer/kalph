from kalph.config import load_config
from kalph.prompt import (
    DEFAULT_TEMPLATE,
    assemble_prompt,
    load_template,
)


def test_default_template_used_when_no_repo_prompt(tmp_path):
    cfg = load_config(tmp_path)
    assert load_template(cfg) == DEFAULT_TEMPLATE


def test_repo_prompt_file_overrides_default(tmp_path):
    cfg = load_config(tmp_path)
    prompt_path = tmp_path / cfg.loop.prompt_file
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("custom {{MEMORY_DIGEST}}")
    assert load_template(cfg) == "custom {{MEMORY_DIGEST}}"


def test_slots_filled_with_placeholders_when_empty(tmp_path):
    cfg = load_config(tmp_path)
    out = assemble_prompt(DEFAULT_TEMPLATE, cfg)
    assert "{{" not in out
    assert "(no state file — flat-backlog mode)" in out
    assert "(no episodes yet)" in out
    assert "(no skills yet)" in out
    assert "solo builder" in out


def test_slots_filled_with_data(tmp_path):
    cfg = load_config(tmp_path)
    out = assemble_prompt(
        DEFAULT_TEMPLATE, cfg, memory_digest="ep1 ok", skills="skill-a", role="Role: verifier."
    )
    assert "ep1 ok" in out
    assert "skill-a" in out
    assert "Role: verifier." in out


def test_digest_budget_enforced(tmp_path):
    (tmp_path / "kalph.toml").write_text("[memory]\ndigest_max_chars = 50\n")
    cfg = load_config(tmp_path)
    out = assemble_prompt(DEFAULT_TEMPLATE, cfg, memory_digest="x" * 500)
    assert "truncated to 50 chars" in out
    # The raw 500-char blob must not appear.
    assert "x" * 51 not in out


def test_contract_and_security_present_in_default():
    assert "KALPH COMPLETE" in DEFAULT_TEMPLATE
    assert "exactly ONE task" in DEFAULT_TEMPLATE
    assert "Read `.kalph/STATE.md` first" in DEFAULT_TEMPLATE
    assert "DATA" in DEFAULT_TEMPLATE
    assert "Never push directly to main" in DEFAULT_TEMPLATE


def test_state_slot_before_episode_digest():
    state_pos = DEFAULT_TEMPLATE.index("{{STATE}}")
    digest_pos = DEFAULT_TEMPLATE.index("{{MEMORY_DIGEST}}")
    assert state_pos < digest_pos


def test_state_slot_filled_from_file(tmp_path):
    cfg = load_config(tmp_path)
    kalph = tmp_path / ".kalph"
    kalph.mkdir()
    (kalph / "STATE.md").write_text(
        "# Kalph state\n\n- milestone: v0.2\n- phase: P-SPINE\n",
        encoding="utf-8",
    )
    out = assemble_prompt(DEFAULT_TEMPLATE, cfg, state=(kalph / "STATE.md").read_text())
    assert "milestone: v0.2" in out
    assert "P-SPINE" in out
    assert "(no state file" not in out


def test_state_budget_enforced(tmp_path):
    (tmp_path / "kalph.toml").write_text("[memory]\nstate_max_chars = 40\n")
    cfg = load_config(tmp_path)
    out = assemble_prompt(DEFAULT_TEMPLATE, cfg, state="s" * 500)
    assert "truncated to 40 chars" in out
    assert "s" * 41 not in out
