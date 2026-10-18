# aura-learn

Continual learning for [aura-code](https://github.com/DusanCar-sudo/aura-code): a small local model that learns from its own mistakes every day — no classical retraining cycle.

## How it works

```
aura-code session
  └─ Archimedes (small model) tries the task
       ├─ succeeds → episode logged
       └─ fails → large model fixes it → escalation triplet logged
                                          (task, small-model attempt, accepted fix)

Night ("sleep")
  episodes → export → replay buffer (new + old + anchor data)
          → incremental LoRA update → guard (personal + forgetting benchmarks)
          → pass: promote adapter   |   fail: keep yesterday's adapter

Day
  Archimedes loads the latest guard-passed adapter
  (Phase 5) fast weights adapt inside the session, reset at session end
```

## Status

Scaffold. Working today: `aura-learn export` (episodes → training JSONL) with tests. Everything else is planned in [docs/PLAN.md](docs/PLAN.md).

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
aura-learn export --out data/corrections.jsonl          # reads ~/.aura/episodes
aura-learn export --episodes-dir path/to/episodes --stats
```

## Layout

```
docs/          PLAN, ARCHITECTURE, RESEARCH notes, DECISIONS log
src/aura_learn/
  episodes.py  read aura-code episodes, build correction triplets
  cli.py       aura-learn command
configs/       base experiment config
experiments/   run logs and results table
tests/         unit tests with fixture episodes
```

## Data contract

aura-learn reads aura-code's `Episode` JSON (`src/archimedes/types.ts`) from `~/.aura/episodes/{projectHash}/*.json`, **read-only**. Override with `AURA_EPISODES_DIR`, same as aura-code.

## License

MIT (pending decision D5 in the plan).
