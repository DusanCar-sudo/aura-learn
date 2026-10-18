# Architecture

## Components

| Component | Lives in | Role |
|---|---|---|
| Episode capture | aura-code `src/archimedes/alternator.ts`, `episode-capture.ts` | Writes one JSON per task to `~/.aura/episodes/` |
| Correction mining (Path B) | aura-code `src/mining/corrections.ts` | Existing manual `:mine` export of escalation triplets |
| Exporter | aura-learn `episodes.py` | Reads episodes, filters accepted escalations, writes JSONL rows with provenance |
| Replay buffer | aura-learn (Phase 4) | Mixes new, old and anchor rows per night |
| Consolidator | aura-learn (Phase 4) | Incremental QLoRA update from yesterday's adapter |
| Eval harness | aura-learn (Phase 2) | Personal-repo benchmark + forgetting benchmark |
| Guard | aura-learn (Phase 4) | Promote or reject an adapter by eval thresholds |
| Adapter registry | aura-learn (Phase 4) | Versioned adapters + scores, rollback |
| Fast weights | aura-learn (Phase 5) | In-Place TTT inside a session, reset at end |
| Serving | aura-code Archimedes + llama.cpp / vLLM (Phase 6) | Base model + current adapter |

## Memory model

- **Context** (seconds–minutes): the prompt.
- **Fast weights** (one session): In-Place TTT updates to MLP projection matrices. Discarded at session end.
- **Adapter** (days–months): per-user LoRA, consolidated nightly from the replay buffer.
- **Base model** (frozen): never modified. Always recoverable.

## Invariants

1. The base model is never modified in place.
2. No adapter reaches Archimedes without passing the guard.
3. Test tasks are strictly later in time than any training data.
4. aura-learn never writes to `~/.aura/episodes/`.
5. A project flagged as excluded produces zero training rows.

## Training row format (JSONL)

```json
{
  "instruction": "task text",
  "input": "small model's rejected attempt",
  "output": "accepted large-model answer",
  "metadata": {
    "episode_id": "...",
    "project_hash": "...",
    "timestamp": 1760000000000,
    "task_category": "implementation",
    "large_model": "claude-sonnet-4-5",
    "provenance": "correction"
  }
}
```

Same shape and `provenance` tag as aura-code's `TrainingExample`, so rows from both tools can be mixed and ablated.
