"""`kelix watch` — live view into a running loop.

The runner leaves two kinds of breadcrumbs under `.kelix/runs/<run_id>/`
(runner bookkeeping: gitignored, never checkpointed):

- `heartbeat.json`: written at iteration start and run end — run id, role,
  iteration, task, pid, status. A run is *active* when its recorded pid is
  still alive.
- `iter-NNN.live.log`: the agent's stdout/stderr streamed chunk-by-chunk as
  it happens (the adapter flushes per chunk). The final `iter-NNN.log`
  transcript still lands at iteration end, unchanged.

`kelix watch` tails the live log of the active run's current iteration and
hops to the next iteration's file when the heartbeat advances. Stdlib only:
the follow loop is plain seek-and-poll, the same thing `tail -f` does.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Heartbeat:
    run_id: str
    iteration: int
    status: str  # running | finished
    pid: int
    role: str = ""
    task: str = ""
    updated_at: str = ""

    @property
    def alive(self) -> bool:
        if self.pid <= 0:
            return False
        try:
            os.kill(self.pid, 0)
        except (ProcessLookupError, PermissionError):
            return False
        except OSError:
            return False
        return True


def write_heartbeat(
    run_dir: Path,
    run_id: str,
    iteration: int,
    status: str,
    role: str = "",
    task: str = "",
) -> None:
    """Runner-side: record where the run is right now. Best-effort — a
    heartbeat failure must never take down an iteration."""
    try:
        payload = {
            "run_id": run_id,
            "iteration": iteration,
            "status": status,
            "pid": os.getpid(),
            "role": role,
            "task": task,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        tmp = run_dir / "heartbeat.json.tmp"
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(run_dir / "heartbeat.json")
    except OSError:
        pass


def read_heartbeat(run_dir: Path) -> Heartbeat | None:
    path = run_dir / "heartbeat.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return Heartbeat(
            run_id=str(data.get("run_id", run_dir.name)),
            iteration=int(data.get("iteration", 0)),
            status=str(data.get("status", "")),
            pid=int(data.get("pid", 0)),
            role=str(data.get("role", "")),
            task=str(data.get("task", "")),
            updated_at=str(data.get("updated_at", "")),
        )
    except (ValueError, OSError):
        return None


def find_active_runs(runs_dir: Path) -> list[Heartbeat]:
    """All runs whose heartbeat says running AND whose pid is alive,
    newest first."""
    if not runs_dir.is_dir():
        return []
    beats = []
    for run_dir in sorted(runs_dir.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        hb = read_heartbeat(run_dir)
        if hb is not None and hb.status == "running" and hb.alive:
            beats.append(hb)
    return beats


def live_log_path(runs_dir: Path, run_id: str, iteration: int) -> Path:
    return runs_dir / run_id / f"iter-{iteration:03d}.live.log"


def follow(
    runs_dir: Path,
    run_id: str,
    emit,
    poll_s: float = 0.2,
    max_idle_s: float = 0.0,
) -> int:
    """Stream a run's live output to *emit(text)* until it finishes.

    Follows the heartbeat across iterations. Returns 0 when the run ended,
    1 if it never produced a heartbeat. `max_idle_s` (tests) bails out after
    that much time with no new bytes and no heartbeat change.
    """
    from .art import say

    current_iter = 0
    fh = None
    idle_since = time.monotonic()

    def open_iter(iteration: int):
        nonlocal fh, current_iter
        if fh is not None:
            # Drain what the finished iteration wrote after our last poll —
            # otherwise its closing lines are silently dropped.
            tail = fh.read()
            if tail:
                emit(tail.decode(errors="replace"))
            fh.close()
            fh = None
        current_iter = iteration
        path = live_log_path(runs_dir, run_id, iteration)
        # The file may not exist yet the instant the heartbeat lands.
        if path.exists():
            fh = open(path, "rb")

    try:
        while True:
            hb = read_heartbeat(runs_dir / run_id)
            if hb is None:
                return 1

            if hb.iteration != current_iter and hb.iteration > 0:
                open_iter(hb.iteration)
                task = f" task={hb.task}" if hb.task else ""
                emit(say(f"iteration {hb.iteration}{task}", "climb") + "\n")
                idle_since = time.monotonic()

            if fh is None and current_iter > 0:
                path = live_log_path(runs_dir, run_id, current_iter)
                if path.exists():
                    fh = open(path, "rb")

            got_bytes = False
            if fh is not None:
                chunk = fh.read()
                if chunk:
                    emit(chunk.decode(errors="replace"))
                    got_bytes = True
                    idle_since = time.monotonic()

            if hb.status == "finished" and not got_bytes:
                emit(say(f"run {run_id} finished", "ok") + "\n")
                return 0
            if not hb.alive and not got_bytes:
                emit(say(f"run {run_id} ended (process gone)", "warn") + "\n")
                return 0
            if max_idle_s > 0 and time.monotonic() - idle_since > max_idle_s:
                return 0

            time.sleep(poll_s)
    finally:
        if fh is not None:
            fh.close()
