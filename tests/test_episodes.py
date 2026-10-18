import json
from pathlib import Path

from aura_learn.cli import main
from aura_learn.episodes import correction_row, iter_episodes, stats


def _ep(**kw):
    base = {
        "id": "e1", "timestamp": 1, "task": "fix auth bug", "projectRoot": "/r",
        "archimedesAttempted": True, "archimedesSucceeded": False,
        "archimedesOutput": "wrong patch", "largeModelUsed": "big",
        "largeModelOutput": "right patch", "reviewerApproved": True,
        "tokensUsed": {}, "durationMs": 10, "taskCategory": "implementation",
    }
    base.update(kw)
    return base


def _write(root: Path, project: str, eps: list[dict]) -> None:
    d = root / project
    d.mkdir(parents=True)
    for e in eps:
        (d / f"{e['id']}.json").write_text(json.dumps(e))


def test_escalation_becomes_row(tmp_path):
    _write(tmp_path, "proj0001", [_ep()])
    [ep] = list(iter_episodes(tmp_path))
    row = correction_row(ep)
    assert row["instruction"] == "fix auth bug"
    assert row["input"] == "wrong patch"
    assert row["output"] == "right patch"
    assert row["metadata"]["provenance"] == "correction"
    assert row["metadata"]["project_hash"] == "proj0001"


def test_filters_unusable(tmp_path):
    _write(tmp_path, "p", [
        _ep(id="ok"),
        _ep(id="success", archimedesSucceeded=True),
        _ep(id="skipped", archimedesAttempted=False),
        _ep(id="unapproved", reviewerApproved=False),
        _ep(id="empty", largeModelOutput="  "),
    ])
    (tmp_path / "p" / "corrupt.json").write_text("{not json")
    eps = list(iter_episodes(tmp_path))
    assert len(eps) == 5
    assert [e.id for e in eps if correction_row(e)] == ["ok"]
    assert correction_row(next(e for e in eps if e.id == "unapproved"), require_approval=False)


def test_oldest_first_and_stats(tmp_path):
    _write(tmp_path, "a", [_ep(id="new", timestamp=5), _ep(id="old", timestamp=2, archimedesSucceeded=True)])
    eps = list(iter_episodes(tmp_path))
    assert [e.id for e in eps] == ["old", "new"]
    s = stats(eps)
    assert s["usable_corrections"] == 1
    assert s["by_category"]["implementation"]["escalation_rate"] == 0.5


def test_cli_export_and_exclude(tmp_path):
    _write(tmp_path / "eps", "keep", [_ep(id="k")])
    _write(tmp_path / "eps", "drop", [_ep(id="d")])
    out = tmp_path / "out.jsonl"
    assert main(["export", "--episodes-dir", str(tmp_path / "eps"), "--out", str(out), "--exclude-project", "drop"]) == 0
    rows = [json.loads(l) for l in out.read_text().splitlines()]
    assert [r["metadata"]["episode_id"] for r in rows] == ["k"]


def test_missing_dir_is_empty(tmp_path):
    assert list(iter_episodes(tmp_path / "nope")) == []


def test_enrichment_fields_flow_into_row(tmp_path):
    rich = _ep(
        id="rich",
        filesTouched=["src/a.py", "src/b.py"],
        diff="diff --git a/src/a.py …",
        testResult="pass",
        reviewerReason=None,
    )
    rejected = _ep(id="rejected", reviewerApproved=False, reviewerReason="claim unsupported")
    _write(tmp_path, "p", [rich, rejected])
    eps = list(iter_episodes(tmp_path))
    rich_ep = next(e for e in eps if e.id == "rich")
    row = correction_row(rich_ep)
    assert rich_ep.files_touched == ["src/a.py", "src/b.py"]
    assert rich_ep.diff == "diff --git a/src/a.py …"
    assert rich_ep.test_result == "pass"
    assert row["metadata"]["files_touched"] == ["src/a.py", "src/b.py"]
    assert row["metadata"]["test_result"] == "pass"
    rej = next(e for e in eps if e.id == "rejected")
    assert rej.reviewer_reason == "claim unsupported"
