"""Read aura-code episodes and build correction triplets.

Data contract: aura-code ``src/archimedes/types.ts`` -> ``Episode``.
Episodes live at ``~/.aura/episodes/{projectHash}/{id}.json`` (override with
``AURA_EPISODES_DIR``, same as aura-code). This module is strictly read-only.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

MAX_INPUT_CHARS = 4000
MAX_OUTPUT_CHARS = 8000


def default_episodes_dir() -> Path:
    env = os.environ.get("AURA_EPISODES_DIR")
    if env:
        return Path(env)
    return Path(os.environ.get("HOME", "/tmp")) / ".aura" / "episodes"


@dataclass
class Episode:
    id: str
    timestamp: int
    task: str
    project_root: str
    project_hash: str
    archimedes_attempted: bool
    archimedes_succeeded: bool
    reviewer_approved: bool
    task_category: str
    archimedes_output: str | None = None
    large_model_used: str | None = None
    large_model_output: str | None = None
    files_touched: list[str] = field(default_factory=list)
    diff: str | None = None
    test_result: str | None = None
    reviewer_reason: str | None = None
    tokens_used: dict[str, int] = field(default_factory=dict)
    duration_ms: int = 0

    @classmethod
    def from_json(cls, data: dict[str, Any], project_hash: str) -> "Episode | None":
        if not isinstance(data.get("id"), str) or not isinstance(data.get("timestamp"), (int, float)):
            return None
        return cls(
            id=data["id"],
            timestamp=int(data["timestamp"]),
            task=str(data.get("task", "")),
            project_root=str(data.get("projectRoot", "")),
            project_hash=project_hash,
            archimedes_attempted=bool(data.get("archimedesAttempted", False)),
            archimedes_succeeded=bool(data.get("archimedesSucceeded", False)),
            reviewer_approved=bool(data.get("reviewerApproved", False)),
            task_category=str(data.get("taskCategory", "other")),
            archimedes_output=data.get("archimedesOutput"),
            large_model_used=data.get("largeModelUsed"),
            large_model_output=data.get("largeModelOutput"),
            files_touched=list(data.get("filesTouched") or []),
            diff=data.get("diff"),
            test_result=data.get("testResult"),
            reviewer_reason=data.get("reviewerReason"),
            tokens_used=dict(data.get("tokensUsed") or {}),
            duration_ms=int(data.get("durationMs", 0) or 0),
        )

    @property
    def is_escalation(self) -> bool:
        return self.archimedes_attempted and not self.archimedes_succeeded and bool(self.large_model_used)


def iter_episodes(root: Path | None = None) -> Iterator[Episode]:
    """Yield every parseable episode under ``root``, oldest first. Never raises on bad files."""
    root = root or default_episodes_dir()
    if not root.is_dir():
        return
    found: list[Episode] = []
    for project_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for f in sorted(project_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if not isinstance(data, dict):
                continue
            ep = Episode.from_json(data, project_dir.name)
            if ep is not None:
                found.append(ep)
    found.sort(key=lambda e: e.timestamp)
    yield from found


def correction_row(ep: Episode, require_approval: bool = True) -> dict[str, Any] | None:
    """Build one instruction-tuning row from an escalation episode, or None if unusable.

    Usable = Archimedes tried and failed, a large model produced output, and
    (by default) the reviewer approved that output.
    """
    if not ep.is_escalation:
        return None
    if not ep.large_model_output or not ep.large_model_output.strip():
        return None
    if require_approval and not ep.reviewer_approved:
        return None
    return {
        "instruction": ep.task,
        "input": (ep.archimedes_output or "")[:MAX_INPUT_CHARS],
        "output": ep.large_model_output[:MAX_OUTPUT_CHARS],
        "metadata": {
            "episode_id": ep.id,
            "project_hash": ep.project_hash,
            "timestamp": ep.timestamp,
            "task_category": ep.task_category,
            "large_model": ep.large_model_used,
            "files_touched": ep.files_touched,
            "test_result": ep.test_result,
            "reviewer_reason": ep.reviewer_reason,
            "provenance": "correction",
        },
    }


def stats(episodes: list[Episode]) -> dict[str, Any]:
    """Descriptive statistics: totals and escalation rate per task category."""
    by_cat: dict[str, dict[str, int]] = {}
    for ep in episodes:
        c = by_cat.setdefault(ep.task_category, {"total": 0, "attempted": 0, "escalated": 0, "usable": 0})
        c["total"] += 1
        if ep.archimedes_attempted:
            c["attempted"] += 1
        if ep.is_escalation:
            c["escalated"] += 1
        if correction_row(ep) is not None:
            c["usable"] += 1
    for c in by_cat.values():
        c["escalation_rate"] = round(c["escalated"] / c["attempted"], 3) if c["attempted"] else None
    return {
        "episodes": len(episodes),
        "projects": len({e.project_hash for e in episodes}),
        "usable_corrections": sum(c["usable"] for c in by_cat.values()),
        "by_category": by_cat,
    }
