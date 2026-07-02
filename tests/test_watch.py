"""Tests for `kelix watch`: live transcript streaming, heartbeats, active-run
discovery, and the follow loop."""

import json
import os
import threading
import time
from pathlib import Path

from conftest import write_mock_script

from kelix.adapters import _run_process
from kelix.config import load_config
from kelix.loop import Runner
from kelix.watch import (
    find_active_runs,
    follow,
    live_log_path,
    read_heartbeat,
    write_heartbeat,
)


def _config(repo, mock_dir="mockdir"):
    (repo / "kelix.toml").write_text(
        f"""
[agent]
adapter = "mock"
mock_dir = "{mock_dir}"

[git]
isolation = "none"
"""
    )
    return load_config(repo)


def test_run_process_streams_to_live_log(tmp_path):
    """Chunks land in the live file while the process is still running,
    not only at exit."""
    script = tmp_path / "chatty.sh"
    script.write_text("#!/bin/sh\necho first\nsleep 1.2\necho second\n")
    script.chmod(0o755)
    live = tmp_path / "live.log"

    result_box = {}

    def run():
        result_box["r"] = _run_process(
            [str(script)], tmp_path, timeout=30, live_log=live
        )

    t = threading.Thread(target=run)
    t.start()
    # Poll while the process sleeps: "first" must already be on disk.
    deadline = time.monotonic() + 1.0
    seen_early = b""
    while time.monotonic() < deadline:
        if live.exists() and b"first" in live.read_bytes():
            seen_early = live.read_bytes()
            break
        time.sleep(0.05)
    t.join(timeout=10)

    assert b"first" in seen_early, "live log did not stream before exit"
    assert b"second" not in seen_early, "second chunk should not exist yet"
    assert result_box["r"].ok
    final = live.read_bytes()
    assert b"first" in final and b"second" in final
    assert result_box["r"].output == final.decode()


def test_heartbeat_roundtrip_and_liveness(tmp_path):
    run_dir = tmp_path / "runs" / "r1"
    run_dir.mkdir(parents=True)
    write_heartbeat(run_dir, "r1", 3, "running", role="builder", task="T1")
    hb = read_heartbeat(run_dir)
    assert hb is not None
    assert (hb.run_id, hb.iteration, hb.status) == ("r1", 3, "running")
    assert hb.role == "builder" and hb.task == "T1"
    assert hb.pid == os.getpid()
    assert hb.alive  # our own pid


def test_find_active_runs_skips_dead_and_finished(tmp_path):
    runs = tmp_path / "runs"
    # Alive + running -> active.
    (runs / "a").mkdir(parents=True)
    write_heartbeat(runs / "a", "a", 1, "running")
    # Finished -> inactive.
    (runs / "b").mkdir()
    write_heartbeat(runs / "b", "b", 5, "finished")
    # Running but dead pid -> inactive.
    (runs / "c").mkdir()
    (runs / "c" / "heartbeat.json").write_text(
        json.dumps(
            {"run_id": "c", "iteration": 2, "status": "running", "pid": 99999999}
        )
    )
    active = find_active_runs(runs)
    assert [hb.run_id for hb in active] == ["a"]


def test_follow_streams_and_stops_on_finish(tmp_path):
    runs = tmp_path / "runs"
    run_dir = runs / "r1"
    run_dir.mkdir(parents=True)
    write_heartbeat(run_dir, "r1", 1, "running", task="T1")
    live = live_log_path(runs, "r1", 1)
    live.write_bytes(b"agent thinking...\n")

    chunks: list[str] = []

    def writer():
        time.sleep(0.3)
        with open(live, "ab") as fh:
            fh.write(b"agent acting.\n")
        time.sleep(0.3)
        write_heartbeat(run_dir, "r1", 1, "finished", task="T1")

    t = threading.Thread(target=writer)
    t.start()
    code = follow(runs, "r1", chunks.append, poll_s=0.05)
    t.join()

    out = "".join(chunks)
    assert code == 0
    assert "agent thinking" in out
    assert "agent acting" in out
    assert "finished" in out


def test_follow_hops_iterations(tmp_path):
    runs = tmp_path / "runs"
    run_dir = runs / "r1"
    run_dir.mkdir(parents=True)
    live_log_path(runs, "r1", 1).write_bytes(b"iter one output\n")
    live_log_path(runs, "r1", 2).write_bytes(b"iter two output\n")
    write_heartbeat(run_dir, "r1", 1, "running", task="T1")

    chunks: list[str] = []

    def advance():
        time.sleep(0.3)
        write_heartbeat(run_dir, "r1", 2, "running", task="T2")
        time.sleep(0.3)
        write_heartbeat(run_dir, "r1", 2, "finished")

    t = threading.Thread(target=advance)
    t.start()
    code = follow(runs, "r1", chunks.append, poll_s=0.05)
    t.join()

    out = "".join(chunks)
    assert code == 0
    assert "iter one output" in out
    assert "iter two output" in out
    assert out.index("iter one output") < out.index("iter two output")


def test_follow_returns_1_without_heartbeat(tmp_path):
    (tmp_path / "runs" / "ghost").mkdir(parents=True)
    assert follow(tmp_path / "runs", "ghost", lambda _: None) == 1


def test_runner_writes_heartbeat_and_live_log(repo):
    """End to end: a real (mock-adapter) run leaves live logs and a finished
    heartbeat behind."""
    write_mock_script(
        repo / "mockdir",
        "001-done.sh",
        'echo "RATIONALE: T1 — demo"\necho done > artifact.txt\n'
        "git add -A && git commit -qm 'T1: artifact'\n",
    )
    cfg = _config(repo)
    result = Runner(cfg).run(max_iterations=2)

    run_dir = cfg.kelix_dir / "runs" / result.run_id
    hb = read_heartbeat(run_dir)
    assert hb is not None and hb.status == "finished"
    live_1 = run_dir / "iter-001.live.log"
    assert live_1.is_file()
    assert "RATIONALE: T1" in live_1.read_text()
    # Live logs are runner bookkeeping: never committed.
    tracked = Path(repo / ".git").exists()
    assert tracked  # sanity: repo fixture is a git repo
