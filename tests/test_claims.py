"""Fleet claim file tests."""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from kalph.claims import (
    claim_task,
    heartbeat,
    is_claimed,
    list_claims,
    release_claim,
)


def _kalph_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".kalph"
    d.mkdir()
    return d


def test_single_winner_among_concurrent_claimers(tmp_path):
    kalph = _kalph_dir(tmp_path)
    task_id = "KB7"
    n = 8

    def attempt(agent_id: str) -> bool:
        return claim_task(kalph, task_id, agent_id, f"branch-{agent_id}")

    with ThreadPoolExecutor(max_workers=n) as pool:
        futures = [pool.submit(attempt, f"agent-{i}") for i in range(n)]
        results = [f.result() for f in as_completed(futures)]

    assert sum(results) == 1
    claims = list_claims(kalph)
    assert len(claims) == 1
    assert claims[0]["task"] == task_id
    assert is_claimed(kalph, task_id)


def test_stale_claim_reclaim(tmp_path):
    kalph = _kalph_dir(tmp_path)
    task_id = "KB7"
    claims_dir = kalph / "fleet" / "claims"
    claims_dir.mkdir(parents=True)

    stale_ts = time.time() - 2000
    claim_path = claims_dir / f"{task_id}.json"
    claim_path.write_text(
        json.dumps(
            {
                "task": task_id,
                "agent": "agent-old",
                "branch": "old-branch",
                "ts": stale_ts,
                "heartbeat": stale_ts,
            }
        ),
        encoding="utf-8",
    )

    assert not is_claimed(kalph, task_id, stale_after_s=900)
    assert claim_task(kalph, task_id, "agent-new", "new-branch", stale_after_s=900)

    claims = list_claims(kalph)
    assert len(claims) == 1
    assert claims[0]["agent"] == "agent-new"
    assert claims[0]["branch"] == "new-branch"
    assert is_claimed(kalph, task_id)


def test_release_allows_reclaim(tmp_path):
    kalph = _kalph_dir(tmp_path)
    task_id = "KB7"

    assert claim_task(kalph, task_id, "agent-a", "branch-a")
    assert is_claimed(kalph, task_id)
    assert release_claim(kalph, task_id, "agent-a")
    assert not is_claimed(kalph, task_id)

    assert claim_task(kalph, task_id, "agent-b", "branch-b")
    assert is_claimed(kalph, task_id)
    claims = list_claims(kalph)
    assert claims[0]["agent"] == "agent-b"


def test_wrong_agent_cannot_release_or_heartbeat(tmp_path):
    kalph = _kalph_dir(tmp_path)
    task_id = "KB7"

    assert claim_task(kalph, task_id, "owner", "owner-branch")
    assert not release_claim(kalph, task_id, "intruder")
    assert not heartbeat(kalph, task_id, "intruder")
    assert is_claimed(kalph, task_id)

    claims = list_claims(kalph)
    assert claims[0]["agent"] == "owner"
    before = claims[0]["heartbeat"]
    time.sleep(0.01)
    assert heartbeat(kalph, task_id, "owner")
    after = list_claims(kalph)[0]["heartbeat"]
    assert after >= before
